from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from app.database import Base


class Matchup(Base):
    __tablename__ = "matchups"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    leader_a_id = Column(String, ForeignKey("leaders.id"), nullable=False, index=True)
    leader_b_id = Column(String, ForeignKey("leaders.id"), nullable=False, index=True)
    win_rate_a = Column(Float, default=0.5)  # Win rate of leader A vs leader B
    sample_size = Column(Integer, default=0)  # Number of games in the sample
    first_win_rate = Column(Float, nullable=True)  # Win rate when A goes first
    second_win_rate = Column(Float, nullable=True)  # Win rate when A goes second
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

