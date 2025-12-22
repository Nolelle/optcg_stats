from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Leader(Base):
    __tablename__ = "leaders"
    
    id = Column(String, primary_key=True, index=True)  # e.g., "OP01-001"
    name = Column(String, nullable=False)
    color = Column(String, nullable=False)  # e.g., "Red", "Blue", "Green", etc.
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    decks = relationship("Deck", back_populates="leader")

