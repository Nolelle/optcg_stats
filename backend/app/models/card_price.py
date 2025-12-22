from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class CardPrice(Base):
    __tablename__ = "card_prices"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    card_id = Column(String, ForeignKey("cards.id"), nullable=False, index=True)
    source = Column(String, nullable=False)  # "tcgplayer" or "cardmarket"
    price_usd = Column(Float, nullable=True)
    price_eur = Column(Float, nullable=True)
    market_price = Column(Float, nullable=True)  # Market/average price
    low_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    card = relationship("Card", back_populates="prices")

