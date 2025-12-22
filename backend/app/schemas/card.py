from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class CardBase(BaseModel):
    id: str
    name: str
    set_code: Optional[str] = None
    rarity: Optional[str] = None
    card_type: Optional[str] = None
    color: Optional[str] = None
    cost: Optional[str] = None
    power: Optional[str] = None
    image_url: Optional[str] = None


class CardCreate(CardBase):
    pass


class CardResponse(CardBase):
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CardPriceInfo(BaseModel):
    source: str
    price_usd: Optional[float] = None
    price_eur: Optional[float] = None
    market_price: Optional[float] = None
    low_price: Optional[float] = None
    high_price: Optional[float] = None
    fetched_at: datetime


class CardWithPrice(CardResponse):
    prices: List[CardPriceInfo] = []
    best_price_usd: Optional[float] = None
    best_price_eur: Optional[float] = None

