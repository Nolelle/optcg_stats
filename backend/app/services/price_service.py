from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from app.models import Card, CardPrice
from app.schemas.card_price import CardPriceCreate


class PriceService:
    def __init__(self, db: Session):
        self.db = db
    
    def add_price(self, price: CardPriceCreate) -> CardPrice:
        db_price = CardPrice(**price.model_dump())
        self.db.add(db_price)
        self.db.commit()
        self.db.refresh(db_price)
        return db_price
    
    def get_latest_price(self, card_id: str, source: Optional[str] = None) -> Optional[CardPrice]:
        query = self.db.query(CardPrice).filter(CardPrice.card_id == card_id)
        if source:
            query = query.filter(CardPrice.source == source)
        return query.order_by(desc(CardPrice.fetched_at)).first()
    
    def get_price_history(self, card_id: str, days: int = 30) -> List[CardPrice]:
        cutoff = datetime.utcnow() - timedelta(days=days)
        return self.db.query(CardPrice).filter(
            CardPrice.card_id == card_id,
            CardPrice.fetched_at >= cutoff
        ).order_by(CardPrice.fetched_at).all()
    
    def get_top_movers(self, days: int = 7, limit: int = 20) -> Dict[str, List[Dict]]:
        """Get cards with biggest price changes"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # Get cards with price changes
        cards = self.db.query(Card).all()
        movers = []
        
        for card in cards:
            # Get oldest and newest prices in the period
            old_price = self.db.query(CardPrice).filter(
                CardPrice.card_id == card.id,
                CardPrice.fetched_at >= cutoff
            ).order_by(CardPrice.fetched_at).first()
            
            new_price = self.db.query(CardPrice).filter(
                CardPrice.card_id == card.id
            ).order_by(desc(CardPrice.fetched_at)).first()
            
            if old_price and new_price and old_price.id != new_price.id:
                old_val = old_price.price_usd or old_price.market_price or 0
                new_val = new_price.price_usd or new_price.market_price or 0
                
                if old_val > 0:
                    change_pct = ((new_val - old_val) / old_val) * 100
                    movers.append({
                        "card_id": card.id,
                        "card_name": card.name,
                        "old_price": old_val,
                        "new_price": new_val,
                        "change_pct": round(change_pct, 2)
                    })
        
        # Sort by absolute change
        movers.sort(key=lambda x: abs(x["change_pct"]), reverse=True)
        
        gainers = [m for m in movers if m["change_pct"] > 0][:limit]
        losers = [m for m in movers if m["change_pct"] < 0][:limit]
        
        return {
            "gainers": gainers,
            "losers": losers
        }
    
    def compare_prices(self, card_id: str) -> Dict[str, Optional[float]]:
        """Compare prices between sources"""
        tcgplayer = self.get_latest_price(card_id, "tcgplayer")
        cardmarket = self.get_latest_price(card_id, "cardmarket")
        
        return {
            "tcgplayer_usd": tcgplayer.price_usd if tcgplayer else None,
            "cardmarket_eur": cardmarket.price_eur if cardmarket else None,
            "tcgplayer_market": tcgplayer.market_price if tcgplayer else None,
            "cardmarket_market": cardmarket.market_price if cardmarket else None,
        }

