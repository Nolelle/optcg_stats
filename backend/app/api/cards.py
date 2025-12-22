from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.services.card_service import CardService
from app.schemas.card import CardResponse, CardWithPrice

router = APIRouter()


@router.get("/", response_model=List[CardResponse])
def get_cards(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all cards with pagination"""
    service = CardService(db)
    return service.get_all(limit=limit, offset=offset)


@router.get("/search", response_model=List[CardResponse])
def search_cards(
    q: str = Query(..., min_length=2),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search cards by name"""
    service = CardService(db)
    return service.search(q, limit=limit)


@router.get("/set/{set_code}", response_model=List[CardResponse])
def get_cards_by_set(set_code: str, db: Session = Depends(get_db)):
    """Get all cards from a specific set"""
    service = CardService(db)
    return service.get_by_set(set_code)


@router.get("/rarity/{rarity}", response_model=List[CardResponse])
def get_cards_by_rarity(rarity: str, db: Session = Depends(get_db)):
    """Get all cards of a specific rarity"""
    service = CardService(db)
    return service.get_by_rarity(rarity)


@router.get("/{card_id}", response_model=CardResponse)
def get_card(card_id: str, db: Session = Depends(get_db)):
    """Get a specific card by ID"""
    service = CardService(db)
    card = service.get_by_id(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card


@router.get("/{card_id}/with-prices", response_model=CardWithPrice)
def get_card_with_prices(card_id: str, db: Session = Depends(get_db)):
    """Get a card with its price information"""
    service = CardService(db)
    card = service.get_with_prices(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card

