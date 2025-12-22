from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict


class DeckBase(BaseModel):
    leader_id: str
    deck_list_json: Optional[str] = None
    win_rate: float = 0.0
    games_played: int = 0
    first_win_rate: float = 0.0
    second_win_rate: float = 0.0
    tier: Optional[str] = None


class DeckCreate(DeckBase):
    source_url: Optional[str] = None


class DeckResponse(DeckBase):
    id: int
    source_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DeckWithCost(DeckResponse):
    total_cost_usd: Optional[float] = None
    total_cost_eur: Optional[float] = None
    leader_name: Optional[str] = None
    leader_color: Optional[str] = None
    card_breakdown: Optional[Dict[str, float]] = None  # Card ID -> price

