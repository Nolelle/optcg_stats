from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.models import Leader, Deck
from app.schemas.leader import LeaderCreate, LeaderWithStats


class LeaderService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[Leader]:
        return self.db.query(Leader).all()
    
    def get_by_id(self, leader_id: str) -> Optional[Leader]:
        return self.db.query(Leader).filter(Leader.id == leader_id).first()
    
    def create(self, leader: LeaderCreate) -> Leader:
        db_leader = Leader(**leader.model_dump())
        self.db.add(db_leader)
        self.db.commit()
        self.db.refresh(db_leader)
        return db_leader
    
    def upsert(self, leader: LeaderCreate) -> Leader:
        existing = self.get_by_id(leader.id)
        if existing:
            for key, value in leader.model_dump().items():
                setattr(existing, key, value)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        return self.create(leader)
    
    def get_tier_list(self) -> List[LeaderWithStats]:
        """Get all leaders with aggregated stats, ordered by win rate"""
        leaders = self.db.query(Leader).all()
        result = []
        
        for leader in leaders:
            # Aggregate stats from all decks for this leader
            stats = self.db.query(
                func.avg(Deck.win_rate).label("avg_win_rate"),
                func.sum(Deck.games_played).label("total_games"),
                func.avg(Deck.first_win_rate).label("avg_first_wr"),
                func.avg(Deck.second_win_rate).label("avg_second_wr"),
                func.count(Deck.id).label("deck_count")
            ).filter(Deck.leader_id == leader.id).first()
            
            tier = self._calculate_tier(stats.avg_win_rate or 0)
            
            result.append(LeaderWithStats(
                id=leader.id,
                name=leader.name,
                color=leader.color,
                image_url=leader.image_url,
                created_at=leader.created_at,
                updated_at=leader.updated_at,
                win_rate=round(stats.avg_win_rate or 0, 2),
                games_played=stats.total_games or 0,
                first_win_rate=round(stats.avg_first_wr or 0, 2),
                second_win_rate=round(stats.avg_second_wr or 0, 2),
                tier=tier,
                deck_count=stats.deck_count or 0
            ))
        
        # Sort by win rate descending
        result.sort(key=lambda x: x.win_rate, reverse=True)
        return result
    
    def _calculate_tier(self, win_rate: float) -> str:
        if win_rate >= 55:
            return "S"
        elif win_rate >= 52:
            return "A"
        elif win_rate >= 49:
            return "B"
        elif win_rate >= 46:
            return "C"
        else:
            return "D"

