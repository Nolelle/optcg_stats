from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict


class MatchupBase(BaseModel):
    leader_a_id: str
    leader_b_id: str
    win_rate_a: float = 0.5
    sample_size: int = 0
    first_win_rate: Optional[float] = None
    second_win_rate: Optional[float] = None


class MatchupCreate(MatchupBase):
    pass


class MatchupResponse(MatchupBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MatchupCell(BaseModel):
    leader_a_id: str
    leader_b_id: str
    win_rate: float
    sample_size: int
    first_win_rate: Optional[float] = None
    second_win_rate: Optional[float] = None


class MatchupMatrix(BaseModel):
    leaders: List[str]  # List of leader IDs
    leader_names: Dict[str, str]  # Leader ID -> Name mapping
    matrix: Dict[str, Dict[str, MatchupCell]]  # leader_a -> leader_b -> matchup data

