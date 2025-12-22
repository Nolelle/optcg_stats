from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CardPriceBase(BaseModel):
    card_id: str
    source: str
    price_usd: Optional[float] = None
    price_eur: Optional[float] = None
    market_price: Optional[float] = None
    low_price: Optional[float] = None
    high_price: Optional[float] = None


class CardPriceCreate(CardPriceBase):
    pass


class CardPriceResponse(CardPriceBase):
    id: int
    fetched_at: datetime
    
    class Config:
        from_attributes = True

