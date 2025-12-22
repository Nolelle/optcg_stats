from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class LeaderBase(BaseModel):
    id: str
    name: str
    color: str
    image_url: Optional[str] = None


class LeaderCreate(LeaderBase):
    pass


class LeaderResponse(LeaderBase):
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LeaderWithStats(LeaderResponse):
    win_rate: float = 0.0
    games_played: int = 0
    first_win_rate: float = 0.0
    second_win_rate: float = 0.0
    tier: Optional[str] = None
    deck_count: int = 0

