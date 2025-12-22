from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from app.database import get_db
from app.services.price_service import PriceService
from app.schemas.card_price import CardPriceResponse

router = APIRouter()


@router.get("/card/{card_id}", response_model=List[CardPriceResponse])
def get_price_history(
    card_id: str,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get price history for a card"""
    service = PriceService(db)
    return service.get_price_history(card_id, days=days)


@router.get("/card/{card_id}/compare")
def compare_prices(card_id: str, db: Session = Depends(get_db)) -> Dict[str, Optional[float]]:
    """Compare prices between TCGPlayer and Cardmarket"""
    service = PriceService(db)
    return service.compare_prices(card_id)


@router.get("/movers")
def get_top_movers(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
) -> Dict[str, List[Dict]]:
    """Get cards with biggest price changes"""
    service = PriceService(db)
    return service.get_top_movers(days=days, limit=limit)

