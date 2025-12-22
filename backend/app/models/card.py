from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Card(Base):
    __tablename__ = "cards"
    
    id = Column(String, primary_key=True, index=True)  # e.g., "OP01-001"
    name = Column(String, nullable=False, index=True)
    set_code = Column(String, nullable=True)  # e.g., "OP01"
    rarity = Column(String, nullable=True)  # Common, Uncommon, Rare, Super Rare, etc.
    card_type = Column(String, nullable=True)  # Leader, Character, Event, Stage
    color = Column(String, nullable=True)
    cost = Column(String, nullable=True)
    power = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    prices = relationship("CardPrice", back_populates="card")

