"""
Limitless TCG Scraper - Scrapes tournament and meta data from onepiece.limitlesstcg.com

This scraper extracts:
- Meta share percentages (deck popularity)
- Tournament points/rankings
- Core cards for each deck
- Tournament results
"""
import httpx
import asyncio
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from app.models import Leader, Deck
from app.database import SessionLocal
from app.scrapers.base import BaseScraper
import logging
import json

logger = logging.getLogger(__name__)

BASE_URL = "https://onepiece.limitlesstcg.com"
DECKS_URL = f"{BASE_URL}/decks"
CARD_IMAGES_CDN = "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/one-piece"


class LimitlessTCGScraper(BaseScraper):
    """Scraper for Limitless TCG OPTCG tournament data"""
    
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
    
    async def scrape(self) -> Dict[str, int]:
        """Main scraping entry point"""
        results = {
            "decks": 0,
            "leaders_updated": 0
        }
        
        # Scrape meta data (deck rankings)
        meta_data = await self.scrape_meta()
        results["decks"] = len(meta_data)
        
        # Update leaders with meta info
        for deck_info in meta_data:
            try:
                self._update_deck_meta(deck_info)
                results["leaders_updated"] += 1
            except Exception as e:
                logger.error(f"Error updating deck {deck_info.get('name')}: {e}")
        
        self.db.commit()
        return results
    
    async def scrape_meta(self) -> List[Dict]:
        """Scrape the meta/deck rankings page"""
        html = await self.fetch(DECKS_URL)
        if not html:
            logger.error("Failed to fetch meta page")
            return []
        
        decks = []
        soup = BeautifulSoup(html, "lxml")
        
        # Find the main table with deck rankings
        table = soup.select_one("table")
        if not table:
            logger.error("Could not find deck rankings table")
            return []
        
        rows = table.select("tbody tr, tr")
        
        for row in rows:
            cells = row.select("td")
            if len(cells) < 4:
                continue
            
            try:
                # Parse row data
                # Format: Rank | Image | Deck Name (link) | Points | Share %
                rank_cell = cells[0].text.strip()
                if not rank_cell.isdigit():
                    continue
                
                rank = int(rank_cell)
                
                # Get deck link and name
                deck_link = cells[2].select_one("a")
                if not deck_link:
                    continue
                
                deck_name = deck_link.text.strip()
                deck_url = deck_link.get("href", "")
                deck_id = deck_url.split("/")[-1] if deck_url else None
                
                # Parse color from deck name element
                color_elem = cells[2].select_one("span, div")
                color = color_elem.text.strip() if color_elem else self._extract_color(deck_name)
                
                # Points
                points = 0
                if len(cells) > 3:
                    points_text = cells[3].text.strip().replace(",", "")
                    if points_text.isdigit():
                        points = int(points_text)
                
                # Share percentage
                share = 0.0
                if len(cells) > 4:
                    share_text = cells[4].text.strip().replace("%", "")
                    try:
                        share = float(share_text)
                    except ValueError:
                        pass
                
                # Extract leader ID from deck page URL if possible
                leader_id = await self._get_leader_id_from_deck(deck_id) if deck_id else None
                
                decks.append({
                    "rank": rank,
                    "name": deck_name,
                    "color": color,
                    "limitless_deck_id": deck_id,
                    "points": points,
                    "meta_share": share,
                    "leader_id": leader_id,
                    "source_url": f"{BASE_URL}{deck_url}" if deck_url else None
                })
                
            except Exception as e:
                logger.error(f"Error parsing deck row: {e}")
                continue
        
        logger.info(f"Scraped {len(decks)} decks from meta page")
        return decks
    
    async def _get_leader_id_from_deck(self, deck_id: str) -> Optional[str]:
        """Fetch deck detail page to get the leader ID"""
        url = f"{DECKS_URL}/{deck_id}"
        html = await self.fetch(url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, "lxml")
        
        # Look for leader ID in the page (usually in a subtitle like "OP13-079")
        # The leader ID pattern is like OP##-### or ST##-###
        text = soup.get_text()
        match = re.search(r'(OP\d{2}-\d{3}|ST\d{2}-\d{3})', text)
        
        if match:
            return match.group(1)
        
        return None
    
    async def scrape_deck_details(self, deck_id: str) -> Optional[Dict]:
        """Scrape detailed info for a specific deck"""
        url = f"{DECKS_URL}/{deck_id}"
        html = await self.fetch(url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, "lxml")
        
        details = {
            "id": deck_id,
            "name": "",
            "leader_id": None,
            "placings": 0,
            "wins": 0,
            "points": 0,
            "core_cards": []
        }
        
        # Get deck name from h1
        h1 = soup.select_one("h1")
        if h1:
            details["name"] = h1.text.strip()
        
        # Parse stats from subtitle (e.g., "128 placings, including 10 wins • 1662 points")
        subtitle = soup.select_one("h1 + div, .subtitle")
        if subtitle:
            text = subtitle.get_text()
            
            # Extract leader ID
            leader_match = re.search(r'(OP\d{2}-\d{3}|ST\d{2}-\d{3})', text)
            if leader_match:
                details["leader_id"] = leader_match.group(1)
            
            # Extract placings
            placings_match = re.search(r'(\d+)\s*placings?', text, re.I)
            if placings_match:
                details["placings"] = int(placings_match.group(1))
            
            # Extract wins
            wins_match = re.search(r'(\d+)\s*wins?', text, re.I)
            if wins_match:
                details["wins"] = int(wins_match.group(1))
            
            # Extract points
            points_match = re.search(r'(\d+)\s*points?', text, re.I)
            if points_match:
                details["points"] = int(points_match.group(1))
        
        # Get core cards
        core_cards_section = soup.select_one("h2:-soup-contains('Core Cards')")
        if core_cards_section:
            parent = core_cards_section.parent
            if parent:
                card_links = parent.select("a[href*='/cards/']")
                for link in card_links:
                    card_id = link.get("href", "").split("/")[-1]
                    # Try to get inclusion rate
                    rate_elem = link.find_next_sibling()
                    rate = 100.0
                    if rate_elem:
                        rate_match = re.search(r'(\d+(?:\.\d+)?)\s*%', rate_elem.get_text())
                        if rate_match:
                            rate = float(rate_match.group(1))
                    
                    details["core_cards"].append({
                        "card_id": card_id,
                        "inclusion_rate": rate
                    })
        
        return details
    
    def _update_deck_meta(self, deck_info: Dict):
        """Update or create deck record with meta data"""
        leader_id = deck_info.get("leader_id")
        
        if not leader_id:
            # Try to find leader by name match
            name = deck_info.get("name", "")
            leader = self.db.query(Leader).filter(
                Leader.name.ilike(f"%{name.split()[-1]}%")
            ).first()
            if leader:
                leader_id = leader.id
        
        if not leader_id:
            logger.warning(f"Could not find leader for deck: {deck_info.get('name')}")
            return
        
        # Check if leader exists
        leader = self.db.query(Leader).filter(Leader.id == leader_id).first()
        if not leader:
            # Create leader if it doesn't exist
            color = deck_info.get("color", "Unknown")
            name = deck_info.get("name", leader_id)
            leader = Leader(
                id=leader_id,
                name=name,
                color=color
            )
            self.db.add(leader)
        
        # Find or create deck
        deck = self.db.query(Deck).filter(
            Deck.leader_id == leader_id,
            Deck.source_url == deck_info.get("source_url")
        ).first()
        
        if not deck:
            # Create aggregate deck entry
            deck = Deck(leader_id=leader_id)
            self.db.add(deck)
        
        # Update with meta data
        points = deck_info.get("points", 0)
        meta_share = deck_info.get("meta_share", 0)
        
        # Calculate approximate games from points (rough estimate)
        # In tournament scoring, points roughly correlate with wins
        deck.games_played = max(points // 3, 1) if points > 0 else 0
        
        # Estimate win rate from meta share (higher share = generally better performance)
        # This is an approximation since we don't have exact win rates
        deck.win_rate = min(50 + (meta_share * 0.5), 70) if meta_share > 0 else 50.0
        
        # Assign tier based on meta share
        deck.tier = self._calculate_tier_from_meta(meta_share)
        deck.source_url = deck_info.get("source_url")
        
        # Store additional data in deck_list_json
        extra_data = {
            "limitless_deck_id": deck_info.get("limitless_deck_id"),
            "meta_share": meta_share,
            "tournament_points": points,
            "rank": deck_info.get("rank")
        }
        deck.deck_list_json = json.dumps(extra_data)
    
    def _extract_color(self, deck_name: str) -> str:
        """Extract color from deck name"""
        colors = ["Red", "Blue", "Green", "Purple", "Black", "Yellow"]
        name_lower = deck_name.lower()
        
        found_colors = []
        for color in colors:
            if color.lower() in name_lower:
                found_colors.append(color)
        
        if found_colors:
            return "/".join(found_colors)
        return "Unknown"
    
    def _calculate_tier_from_meta(self, meta_share: float) -> str:
        """Calculate tier based on meta share percentage"""
        if meta_share >= 30:
            return "S"
        elif meta_share >= 15:
            return "A"
        elif meta_share >= 5:
            return "B"
        elif meta_share >= 1:
            return "C"
        else:
            return "D"


async def run_limitless_scrape():
    """Standalone function to run the scrape"""
    db = SessionLocal()
    try:
        scraper = LimitlessTCGScraper(db)
        results = await scraper.scrape()
        logger.info(f"Limitless TCG scrape complete: {results}")
        return results
    except Exception as e:
        logger.error(f"Error in Limitless TCG scrape: {e}")
        raise
    finally:
        db.close()

