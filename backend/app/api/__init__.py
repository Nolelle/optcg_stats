from fastapi import APIRouter
from app.api import leaders, decks, matchups, cards, prices

api_router = APIRouter()

api_router.include_router(leaders.router, prefix="/leaders", tags=["leaders"])
api_router.include_router(decks.router, prefix="/decks", tags=["decks"])
api_router.include_router(matchups.router, prefix="/matchups", tags=["matchups"])
api_router.include_router(cards.router, prefix="/cards", tags=["cards"])
api_router.include_router(prices.router, prefix="/prices", tags=["prices"])

