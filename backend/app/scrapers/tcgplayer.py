from bs4 import BeautifulSoup
from typing import List, Optional
from sqlalchemy.orm import Session
from app.scrapers.base import BaseScraper
from app.models import Card, CardPrice
from app.schemas.card import CardCreate
from app.schemas.card_price import CardPriceCreate
from app.services import CardService, PriceService


class TCGPlayerScraper(BaseScraper):
    """Scraper for TCGPlayer OPTCG card prices"""
    
    BASE_URL = "https://www.tcgplayer.com"
    SEARCH_URL = f"{BASE_URL}/search/one-piece-card-game/product"
    
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
    
    async def scrape_card_price(self, card_id: str, card_name: str) -> Optional[CardPrice]:
        """Scrape price for a specific card"""
        # Search for the card
        search_url = f"{self.SEARCH_URL}?q={card_name.replace(' ', '%20')}"
        html = await self.fetch(search_url)
        
        if not html:
            return None
        
        soup = BeautifulSoup(html, "lxml")
        
        try:
            # This is a template - adjust selectors based on actual site structure
            product_card = soup.select_one(".search-result__product")
            if not product_card:
                return None
            
            # Extract price info
            market_price_el = product_card.select_one(".product-card__market-price")
            market_price = self._parse_price(market_price_el.text if market_price_el else None)
            
            low_price_el = product_card.select_one(".product-card__low-price")
            low_price = self._parse_price(low_price_el.text if low_price_el else None)
            
            # Create price entry
            price_data = CardPriceCreate(
                card_id=card_id,
                source="tcgplayer",
                price_usd=market_price,
                market_price=market_price,
                low_price=low_price
            )
            
            return self.price_service.add_price(price_data)
            
        except (AttributeError, ValueError) as e:
            print(f"Error scraping price for {card_name}: {e}")
            return None
    
    def _parse_price(self, price_str: Optional[str]) -> Optional[float]:
        """Parse price string to float"""
        if not price_str:
            return None
        try:
            # Remove $ and commas, convert to float
            clean = price_str.replace("$", "").replace(",", "").strip()
            return float(clean)
        except ValueError:
            return None
    
    async def scrape_set(self, set_code: str) -> List[CardPrice]:
        """Scrape all cards from a specific set"""
        set_url = f"{self.BASE_URL}/search/one-piece-card-game/{set_code}/product"
        html = await self.fetch(set_url)
        
        if not html:
            return []
        
        prices = []
        soup = BeautifulSoup(html, "lxml")
        
        # Parse all products on the page
        products = soup.select(".search-result__product")
        
        for product in products:
            try:
                name_el = product.select_one(".product-card__name")
                if not name_el:
                    continue
                
                card_name = name_el.text.strip()
                card_id = f"{set_code}-{len(prices)+1:03d}"  # Generate ID if not available
                
                market_price_el = product.select_one(".product-card__market-price")
                market_price = self._parse_price(market_price_el.text if market_price_el else None)
                
                if market_price:
                    price_data = CardPriceCreate(
                        card_id=card_id,
                        source="tcgplayer",
                        price_usd=market_price,
                        market_price=market_price
                    )
                    price = self.price_service.add_price(price_data)
                    prices.append(price)
                    
            except (AttributeError, ValueError) as e:
                print(f"Error parsing product: {e}")
                continue
        
        return prices

