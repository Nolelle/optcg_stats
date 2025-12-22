from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Deck(Base):
    __tablename__ = "decks"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    leader_id = Column(String, ForeignKey("leaders.id"), nullable=False, index=True)
    deck_list_json = Column(Text, nullable=True)  # JSON string of card IDs and counts
    win_rate = Column(Float, default=0.0)
    games_played = Column(Integer, default=0)
    first_win_rate = Column(Float, default=0.0)  # Win rate when going first
    second_win_rate = Column(Float, default=0.0)  # Win rate when going second
    tier = Column(String, nullable=True)  # S, A, B, C, D
    source_url = Column(String, nullable=True)  # Where this deck was scraped from
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    leader = relationship("Leader", back_populates="decks")

