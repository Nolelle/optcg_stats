"""
OPTCG API Importer - Fetches real card data from optcgapi.com
API Documentation: https://optcgapi.com/documentation

This is a free, public API with no authentication required.
Data is updated daily.
"""

import logging
from typing import Dict, List, Optional

import httpx
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Card, CardPrice, Leader

logger = logging.getLogger(__name__)

# API Endpoints
BASE_URL = "https://optcgapi.com/api"
ALL_CARDS_URL = f"{BASE_URL}/allSetCards/"  # Returns all cards with prices
ALL_SETS_URL = f"{BASE_URL}/allSets/"
SINGLE_CARD_URL = f"{BASE_URL}/sets/card/"  # Append card_id/

# Note: The allSetCards endpoint returns both regular cards AND leaders
# Leaders have card_type == "Leader"


class OPTCGAPIImporter:
    """Imports card data from the OPTCG API (optcgapi.com)"""

    def __init__(self, db: Session):
        self.db = db
        self.headers = {"User-Agent": "OPTCG-Stats-App/1.0"}

    async def fetch_json(self, url: str) -> Optional[Dict | List]:
        """Fetch JSON data from URL"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Error fetching {url}: {e}")
                return None

    async def import_all_cards(self) -> int:
        """Import all cards from the API"""
        logger.info("Fetching all cards from OPTCG API...")
        data = await self.fetch_json(ALL_CARDS_URL)

        if not data:
            logger.error("Failed to fetch cards from API")
            return 0

        # Deduplicate cards - API returns same card_set_id for alternate arts
        # Keep only the first (main) version of each card
        seen_ids = set()
        unique_cards = []
        for card_data in data:
            card_id = card_data.get("card_set_id")
            if card_id and card_id not in seen_ids:
                seen_ids.add(card_id)
                unique_cards.append(card_data)

        logger.info(
            f"Processing {len(unique_cards)} unique cards (filtered from {len(data)} total)"
        )

        count = 0
        for card_data in unique_cards:
            try:
                card = self._upsert_card(card_data)
                if card:
                    # Also create/update price if available
                    self._upsert_price(card_data)
                    count += 1
            except Exception as e:
                logger.error(
                    f"Error processing card {card_data.get('card_set_id', 'unknown')}: {e}"
                )
                continue

        self.db.commit()
        logger.info(f"Imported {count} cards")
        return count

    async def import_all_leaders(self) -> int:
        """Import all leaders from the all cards API (filtered by card_type=Leader)"""
        logger.info("Fetching all leaders from OPTCG API...")
        # Leaders are included in the allSetCards endpoint
        data = await self.fetch_json(ALL_CARDS_URL)

        if not data:
            logger.error("Failed to fetch data from API")
            return 0

        # Filter for leaders only and deduplicate
        leaders_data = [c for c in data if c.get("card_type") == "Leader"]

        seen_ids = set()
        unique_leaders = []
        for leader_data in leaders_data:
            leader_id = leader_data.get("card_set_id")
            if leader_id and leader_id not in seen_ids:
                seen_ids.add(leader_id)
                unique_leaders.append(leader_data)

        logger.info(
            f"Processing {len(unique_leaders)} unique leaders (filtered from {len(leaders_data)} total)"
        )

        count = 0
        for leader_data in unique_leaders:
            try:
                leader = self._upsert_leader(leader_data)
                if leader:
                    count += 1
            except Exception as e:
                logger.error(
                    f"Error processing leader {leader_data.get('card_set_id', 'unknown')}: {e}"
                )
                continue

        self.db.commit()
        logger.info(f"Imported {count} leaders")
        return count

    def _upsert_card(self, data: Dict) -> Optional[Card]:
        """Create or update a card from API data

        API fields:
        - card_set_id: "OP13-079"
        - card_name: "Imu"
        - set_id: "OP-13"
        - rarity: "L", "SR", "R", "UC", "C", "SEC", "TR"
        - card_type: "Leader", "Character", "Event", "Stage"
        - card_color: "Black", "Red", "Blue", "Green", "Purple", "Yellow", "Red Black", etc.
        - card_cost: "4" or null
        - card_power: "5000" or null
        - card_image: "https://optcgapi.com/media/static/Card_Images/..."
        - market_price: 0.12
        - inventory_price: 0.08
        """
        card_id = data.get("card_set_id")
        if not card_id:
            return None

        # Extract set code from card ID (e.g., "OP13" from "OP13-079")
        set_code = card_id.split("-")[0] if "-" in card_id else None

        # Map API fields to our model
        card = self.db.query(Card).filter(Card.id == card_id).first()

        if not card:
            card = Card(id=card_id)
            self.db.add(card)

        # Update fields - API uses slightly different field names
        card.name = data.get("card_name", "Unknown")
        card.set_code = set_code
        card.rarity = data.get("rarity")
        card.card_type = data.get("card_type")
        card.color = data.get("card_color")
        card.cost = (
            str(data.get("card_cost")) if data.get("card_cost") is not None else None
        )
        card.power = (
            str(data.get("card_power")) if data.get("card_power") is not None else None
        )
        card.image_url = data.get("card_image")  # API uses card_image, not card_img_url

        return card

    def _upsert_leader(self, data: Dict) -> Optional[Leader]:
        """Create or update a leader from API data"""
        leader_id = data.get("card_set_id")
        if not leader_id:
            return None

        leader = self.db.query(Leader).filter(Leader.id == leader_id).first()

        if not leader:
            leader = Leader(id=leader_id)
            self.db.add(leader)

        # Update fields - API uses card_image for image URL
        leader.name = data.get("card_name", "Unknown")
        leader.color = data.get("card_color", "Unknown")
        leader.image_url = data.get("card_image")

        return leader

    def _upsert_price(self, data: Dict) -> Optional[CardPrice]:
        """Create or update price data from API

        API provides:
        - market_price: float (e.g., 0.12)
        - inventory_price: float (e.g., 0.08) - this is like "low price"
        """
        card_id = data.get("card_set_id")
        if not card_id:
            return None

        # Extract price info from API
        market_price = data.get("market_price")
        inventory_price = data.get(
            "inventory_price"
        )  # API uses inventory_price for low price

        if market_price is None and inventory_price is None:
            return None

        # Find or create price record
        price = (
            self.db.query(CardPrice)
            .filter(CardPrice.card_id == card_id, CardPrice.source == "optcgapi")
            .first()
        )

        if not price:
            price = CardPrice(card_id=card_id, source="optcgapi")
            self.db.add(price)

        # Update price fields
        if market_price is not None:
            try:
                price.market_price = float(market_price)
            except (ValueError, TypeError):
                pass

        if inventory_price is not None:
            try:
                price.low_price = float(inventory_price)
            except (ValueError, TypeError):
                pass

        return price

    async def import_all(self) -> Dict[str, int]:
        """Import all data from the API"""
        results = {"cards": 0, "leaders": 0}

        # Import leaders first (they're also cards, but we want them in the leaders table)
        results["leaders"] = await self.import_all_leaders()
        # Then import all cards
        results["cards"] = await self.import_all_cards()

        return results


async def run_optcg_import():
    """Standalone function to run the import"""
    db = SessionLocal()
    try:
        importer = OPTCGAPIImporter(db)
        results = await importer.import_all()
        logger.info(f"OPTCG API import complete: {results}")
        return results
    except Exception as e:
        logger.error(f"Error in OPTCG API import: {e}")
        raise
    finally:
        db.close()
