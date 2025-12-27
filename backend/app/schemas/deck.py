from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, List


class CardInDeck(BaseModel):
    """Card details for display in deck viewer"""
    id: str
    name: str
    card_type: Optional[str] = None  # Leader, Character, Event, Stage
    cost: Optional[int] = None
    power: Optional[int] = None
    color: Optional[str] = None
    rarity: Optional[str] = None
    image_url: Optional[str] = None
    count: int = 1
    price_usd: Optional[float] = None
    price_eur: Optional[float] = None


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


class DeckDetailedResponse(DeckResponse):
    """Detailed deck with full card information for deck viewer"""
    total_cost_usd: Optional[float] = None
    total_cost_eur: Optional[float] = None
    leader_name: Optional[str] = None
    leader_color: Optional[str] = None
    leader_image_url: Optional[str] = None
    cards: List[CardInDeck] = []
    cost_curve: Dict[str, int] = {}  # cost -> count of cards at that cost

