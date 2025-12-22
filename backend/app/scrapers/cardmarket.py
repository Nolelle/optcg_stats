from typing import List, Optional

from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.models import CardPrice
from app.schemas.card_price import CardPriceCreate
from app.scrapers.base import BaseScraper
from app.services import CardService, PriceService


class CardmarketScraper(BaseScraper):
    """Scraper for Cardmarket OPTCG card prices"""

    BASE_URL = "https://www.cardmarket.com"
    SEARCH_URL = f"{BASE_URL}/en/OnePiece/Products/Search"

    # EUR to USD conversion rate (should be fetched dynamically in production)
    EUR_TO_USD = 1.10

    def __init__(self, db: Session):
        super().__init__()
        self.db = db
        self.card_service = CardService(db)
        self.price_service = PriceService(db)

    async def scrape(self) -> int:
        """Scrape all OPTCG card prices"""
        # Get all cards from database
        cards = self.card_service.get_all(limit=10000)
        count = 0

        for card in cards:
            price = await self.scrape_card_price(card.id, card.name)
            if price:
                count += 1

        return count

    async def scrape_card_price(
        self, card_id: str, card_name: str
    ) -> Optional[CardPrice]:
        """Scrape price for a specific card"""
        search_url = f"{self.SEARCH_URL}?searchString={card_name.replace(' ', '+')}"
        html = await self.fetch(search_url)

        if not html:
            return None

        soup = BeautifulSoup(html, "lxml")

        try:
            # This is a template - adjust selectors based on actual site structure
            product_row = soup.select_one(".table-body .row")
            if not product_row:
                return None

            # Extract price info (Cardmarket uses EUR)
            price_from_el = product_row.select_one(".price-container .price-from")
            price_eur = self._parse_price(price_from_el.text if price_from_el else None)

            trend_el = product_row.select_one(".price-container .price-trend")
            trend_eur = self._parse_price(trend_el.text if trend_el else None)

            # Create price entry
            price_data = CardPriceCreate(
                card_id=card_id,
                source="cardmarket",
                price_eur=price_eur,
                price_usd=round(price_eur * self.EUR_TO_USD, 2) if price_eur else None,
                market_price=trend_eur,
                low_price=price_eur,
            )

            return self.price_service.add_price(price_data)

        except (AttributeError, ValueError) as e:
            print(f"Error scraping price for {card_name}: {e}")
            return None

    def _parse_price(self, price_str: Optional[str]) -> Optional[float]:
        """Parse price string to float (EUR format)"""
        if not price_str:
            return None
        try:
            # Remove € and handle European number format
            clean = price_str.replace("€", "").replace(",", ".").strip()
            return float(clean)
        except ValueError:
            return None

    async def scrape_set(self, set_code: str) -> List[CardPrice]:
        """Scrape all cards from a specific set"""
        # Cardmarket uses different set naming
        set_url = f"{self.BASE_URL}/en/OnePiece/Products/Singles/{set_code}"
        html = await self.fetch(set_url)

        if not html:
            return []

        prices = []
        soup = BeautifulSoup(html, "lxml")

        # Parse all products on the page
        products = soup.select(".table-body .row")

        for product in products:
            try:
                name_el = product.select_one(".product-name")
                if not name_el:
                    continue

                card_name = name_el.text.strip()
                card_id_el = product.select_one(".product-id")
                card_id = (
                    card_id_el.text.strip()
                    if card_id_el
                    else f"{set_code}-{len(prices) + 1:03d}"
                )

                price_el = product.select_one(".price-container .price-from")
                price_eur = self._parse_price(price_el.text if price_el else None)

                if price_eur:
                    price_data = CardPriceCreate(
                        card_id=card_id,
                        source="cardmarket",
                        price_eur=price_eur,
                        price_usd=round(price_eur * self.EUR_TO_USD, 2),
                        market_price=price_eur,
                    )
                    price = self.price_service.add_price(price_data)
                    prices.append(price)

            except (AttributeError, ValueError) as e:
                print(f"Error parsing product: {e}")
                continue

        return prices
