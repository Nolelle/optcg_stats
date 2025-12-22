from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.services.deck_service import DeckService
from app.schemas.deck import DeckResponse, DeckWithCost

router = APIRouter()


@router.get("/", response_model=List[DeckResponse])
def get_decks(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all decks with pagination"""
    service = DeckService(db)
    return service.get_all(limit=limit, offset=offset)


@router.get("/most-played", response_model=List[DeckResponse])
def get_most_played(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get most played decks"""
    service = DeckService(db)
    return service.get_most_played(limit=limit)


@router.get("/most-successful", response_model=List[DeckResponse])
def get_most_successful(
    min_games: int = Query(50, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get most successful decks (highest win rate with minimum games)"""
    service = DeckService(db)
    return service.get_most_successful(min_games=min_games, limit=limit)


@router.get("/leader/{leader_id}", response_model=List[DeckResponse])
def get_decks_by_leader(leader_id: str, db: Session = Depends(get_db)):
    """Get all decks for a specific leader"""
    service = DeckService(db)
    return service.get_by_leader(leader_id)


@router.get("/{deck_id}", response_model=DeckResponse)
def get_deck(deck_id: int, db: Session = Depends(get_db)):
    """Get a specific deck by ID"""
    service = DeckService(db)
    deck = service.get_by_id(deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    return deck


@router.get("/{deck_id}/with-cost", response_model=DeckWithCost)
def get_deck_with_cost(deck_id: int, db: Session = Depends(get_db)):
    """Get a deck with calculated costs"""
    service = DeckService(db)
    deck = service.get_with_cost(deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    return deck

