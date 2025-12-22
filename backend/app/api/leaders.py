from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.services.leader_service import LeaderService
from app.schemas.leader import LeaderResponse, LeaderWithStats

router = APIRouter()


@router.get("/", response_model=List[LeaderResponse])
def get_leaders(db: Session = Depends(get_db)):
    """Get all leaders"""
    service = LeaderService(db)
    return service.get_all()


@router.get("/tier-list", response_model=List[LeaderWithStats])
def get_tier_list(db: Session = Depends(get_db)):
    """Get leaders ranked by win rate with tier assignments"""
    service = LeaderService(db)
    return service.get_tier_list()


@router.get("/{leader_id}", response_model=LeaderResponse)
def get_leader(leader_id: str, db: Session = Depends(get_db)):
    """Get a specific leader by ID"""
    service = LeaderService(db)
    leader = service.get_by_id(leader_id)
    if not leader:
        raise HTTPException(status_code=404, detail="Leader not found")
    return leader

