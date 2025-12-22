from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from app.models import Matchup, Leader
from app.schemas.matchup import MatchupCreate, MatchupCell, MatchupMatrix


class MatchupService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[Matchup]:
        return self.db.query(Matchup).all()
    
    def get_matchup(self, leader_a: str, leader_b: str) -> Optional[Matchup]:
        return self.db.query(Matchup).filter(
            Matchup.leader_a_id == leader_a,
            Matchup.leader_b_id == leader_b
        ).first()
    
    def create(self, matchup: MatchupCreate) -> Matchup:
        db_matchup = Matchup(**matchup.model_dump())
        self.db.add(db_matchup)
        self.db.commit()
        self.db.refresh(db_matchup)
        return db_matchup
    
    def upsert(self, matchup: MatchupCreate) -> Matchup:
        existing = self.get_matchup(matchup.leader_a_id, matchup.leader_b_id)
        if existing:
            for key, value in matchup.model_dump().items():
                setattr(existing, key, value)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        return self.create(matchup)
    
    def get_matchups_for_leader(self, leader_id: str) -> List[Matchup]:
        return self.db.query(Matchup).filter(
            (Matchup.leader_a_id == leader_id) | (Matchup.leader_b_id == leader_id)
        ).all()
    
    def get_matrix(self) -> MatchupMatrix:
        """Build a complete matchup matrix for all leaders"""
        leaders = self.db.query(Leader).all()
        leader_ids = [l.id for l in leaders]
        leader_names = {l.id: l.name for l in leaders}
        
        matchups = self.db.query(Matchup).all()
        
        # Build the matrix
        matrix: Dict[str, Dict[str, MatchupCell]] = {}
        
        for leader_a in leader_ids:
            matrix[leader_a] = {}
            for leader_b in leader_ids:
                if leader_a == leader_b:
                    # Mirror matchup - 50% by definition
                    matrix[leader_a][leader_b] = MatchupCell(
                        leader_a_id=leader_a,
                        leader_b_id=leader_b,
                        win_rate=50.0,
                        sample_size=0,
                        first_win_rate=50.0,
                        second_win_rate=50.0
                    )
                else:
                    # Find the matchup data
                    matchup = next(
                        (m for m in matchups if m.leader_a_id == leader_a and m.leader_b_id == leader_b),
                        None
                    )
                    if matchup:
                        matrix[leader_a][leader_b] = MatchupCell(
                            leader_a_id=leader_a,
                            leader_b_id=leader_b,
                            win_rate=matchup.win_rate_a,
                            sample_size=matchup.sample_size,
                            first_win_rate=matchup.first_win_rate,
                            second_win_rate=matchup.second_win_rate
                        )
                    else:
                        # Check reverse matchup
                        reverse = next(
                            (m for m in matchups if m.leader_a_id == leader_b and m.leader_b_id == leader_a),
                            None
                        )
                        if reverse:
                            matrix[leader_a][leader_b] = MatchupCell(
                                leader_a_id=leader_a,
                                leader_b_id=leader_b,
                                win_rate=100 - reverse.win_rate_a,
                                sample_size=reverse.sample_size,
                                first_win_rate=100 - reverse.second_win_rate if reverse.second_win_rate else None,
                                second_win_rate=100 - reverse.first_win_rate if reverse.first_win_rate else None
                            )
                        else:
                            # No data
                            matrix[leader_a][leader_b] = MatchupCell(
                                leader_a_id=leader_a,
                                leader_b_id=leader_b,
                                win_rate=50.0,
                                sample_size=0,
                                first_win_rate=None,
                                second_win_rate=None
                            )
        
        return MatchupMatrix(
            leaders=leader_ids,
            leader_names=leader_names,
            matrix=matrix
        )

