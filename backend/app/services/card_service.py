from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from app.models import Card, CardPrice
from app.schemas.card import CardCreate, CardWithPrice, CardPriceInfo


class CardService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[Card]:
        return self.db.query(Card).offset(offset).limit(limit).all()
    
    def get_by_id(self, card_id: str) -> Optional[Card]:
        return self.db.query(Card).filter(Card.id == card_id).first()
    
    def search(self, query: str, limit: int = 50) -> List[Card]:
        return self.db.query(Card).filter(
            Card.name.ilike(f"%{query}%")
        ).limit(limit).all()
    
    def create(self, card: CardCreate) -> Card:
        db_card = Card(**card.model_dump())
        self.db.add(db_card)
        self.db.commit()
        self.db.refresh(db_card)
        return db_card
    
    def upsert(self, card: CardCreate) -> Card:
        existing = self.get_by_id(card.id)
        if existing:
            for key, value in card.model_dump().items():
                setattr(existing, key, value)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        return self.create(card)
    
    def get_with_prices(self, card_id: str) -> Optional[CardWithPrice]:
        card = self.get_by_id(card_id)
        if not card:
            return None
        
        prices = self.db.query(CardPrice).filter(
            CardPrice.card_id == card_id
        ).order_by(desc(CardPrice.fetched_at)).all()
        
        # Get latest price per source
        latest_prices = {}
        for price in prices:
            if price.source not in latest_prices:
                latest_prices[price.source] = price
        
        price_infos = [
            CardPriceInfo(
                source=p.source,
                price_usd=p.price_usd,
                price_eur=p.price_eur,
                market_price=p.market_price,
                low_price=p.low_price,
                high_price=p.high_price,
                fetched_at=p.fetched_at
            )
            for p in latest_prices.values()
        ]
        
        best_usd = min((p.price_usd for p in price_infos if p.price_usd), default=None)
        best_eur = min((p.price_eur for p in price_infos if p.price_eur), default=None)
        
        return CardWithPrice(
            id=card.id,
            name=card.name,
            set_code=card.set_code,
            rarity=card.rarity,
            card_type=card.card_type,
            color=card.color,
            cost=card.cost,
            power=card.power,
            image_url=card.image_url,
            created_at=card.created_at,
            updated_at=card.updated_at,
            prices=price_infos,
            best_price_usd=best_usd,
            best_price_eur=best_eur
        )
    
    def get_by_set(self, set_code: str) -> List[Card]:
        return self.db.query(Card).filter(Card.set_code == set_code).all()
    
    def get_by_rarity(self, rarity: str) -> List[Card]:
        return self.db.query(Card).filter(Card.rarity == rarity).all()

