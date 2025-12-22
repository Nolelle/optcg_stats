from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.services.matchup_service import MatchupService
from app.schemas.matchup import MatchupResponse, MatchupMatrix

router = APIRouter()


@router.get("/", response_model=List[MatchupResponse])
def get_matchups(db: Session = Depends(get_db)):
    """Get all matchups"""
    service = MatchupService(db)
    return service.get_all()


@router.get("/matrix", response_model=MatchupMatrix)
def get_matchup_matrix(db: Session = Depends(get_db)):
    """Get the full matchup matrix for all leaders"""
    service = MatchupService(db)
    return service.get_matrix()


@router.get("/leader/{leader_id}", response_model=List[MatchupResponse])
def get_matchups_for_leader(leader_id: str, db: Session = Depends(get_db)):
    """Get all matchups involving a specific leader"""
    service = MatchupService(db)
    return service.get_matchups_for_leader(leader_id)


@router.get("/{leader_a}/{leader_b}", response_model=MatchupResponse)
def get_matchup(leader_a: str, leader_b: str, db: Session = Depends(get_db)):
    """Get matchup data between two leaders"""
    service = MatchupService(db)
    matchup = service.get_matchup(leader_a, leader_b)
    if not matchup:
        # Try reverse
        matchup = service.get_matchup(leader_b, leader_a)
        if not matchup:
            raise HTTPException(status_code=404, detail="Matchup not found")
    return matchup

