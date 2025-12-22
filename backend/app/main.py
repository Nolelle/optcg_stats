from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.api import api_router
from app.database import engine, Base, get_db
from app.config import get_settings
from app.scheduler import start_scheduler, stop_scheduler, scrape_matchmaking_data, scrape_tcgplayer_prices, scrape_cardmarket_prices

settings = get_settings()

# Create tables
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if not settings.debug:
        start_scheduler()
    yield
    # Shutdown
    if not settings.debug:
        stop_scheduler()


app = FastAPI(
    title=settings.app_name,
    description="API for OPTCG deck statistics, matchups, and card prices",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "Welcome to OPTCG Stats API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/api/scrape/matchmaking")
async def trigger_matchmaking_scrape(background_tasks: BackgroundTasks):
    """Manually trigger TCG Matchmaking scrape"""
    background_tasks.add_task(scrape_matchmaking_data)
    return {"message": "Matchmaking scrape started"}


@app.post("/api/scrape/tcgplayer")
async def trigger_tcgplayer_scrape(background_tasks: BackgroundTasks):
    """Manually trigger TCGPlayer price scrape"""
    background_tasks.add_task(scrape_tcgplayer_prices)
    return {"message": "TCGPlayer scrape started"}


@app.post("/api/scrape/cardmarket")
async def trigger_cardmarket_scrape(background_tasks: BackgroundTasks):
    """Manually trigger Cardmarket price scrape"""
    background_tasks.add_task(scrape_cardmarket_prices)
    return {"message": "Cardmarket scrape started"}

