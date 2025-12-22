from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.scrapers import TCGMatchmakingScraper, TCGPlayerScraper, CardmarketScraper
from app.config import get_settings
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def scrape_matchmaking_data():
    """Scheduled job to scrape TCG Matchmaking data"""
    logger.info("Starting TCG Matchmaking scrape job...")
    db = SessionLocal()
    try:
        scraper = TCGMatchmakingScraper(db)
        results = await scraper.scrape()
        logger.info(f"TCG Matchmaking scrape complete: {results}")
    except Exception as e:
        logger.error(f"Error in TCG Matchmaking scrape: {e}")
    finally:
        db.close()


async def scrape_tcgplayer_prices():
    """Scheduled job to scrape TCGPlayer prices"""
    logger.info("Starting TCGPlayer price scrape job...")
    db = SessionLocal()
    try:
        scraper = TCGPlayerScraper(db)
        count = await scraper.scrape()
        logger.info(f"TCGPlayer scrape complete: {count} prices updated")
    except Exception as e:
        logger.error(f"Error in TCGPlayer scrape: {e}")
    finally:
        db.close()


async def scrape_cardmarket_prices():
    """Scheduled job to scrape Cardmarket prices"""
    logger.info("Starting Cardmarket price scrape job...")
    db = SessionLocal()
    try:
        scraper = CardmarketScraper(db)
        count = await scraper.scrape()
        logger.info(f"Cardmarket scrape complete: {count} prices updated")
    except Exception as e:
        logger.error(f"Error in Cardmarket scrape: {e}")
    finally:
        db.close()


def start_scheduler():
    """Start the background scheduler"""
    # Schedule TCG Matchmaking scrape every N hours
    scheduler.add_job(
        scrape_matchmaking_data,
        trigger=IntervalTrigger(hours=settings.scrape_interval_hours),
        id="scrape_matchmaking",
        name="Scrape TCG Matchmaking Data",
        replace_existing=True,
    )
    
    # Schedule TCGPlayer price scrape every N hours
    scheduler.add_job(
        scrape_tcgplayer_prices,
        trigger=IntervalTrigger(hours=settings.price_cache_ttl_hours),
        id="scrape_tcgplayer",
        name="Scrape TCGPlayer Prices",
        replace_existing=True,
    )
    
    # Schedule Cardmarket price scrape every N hours
    scheduler.add_job(
        scrape_cardmarket_prices,
        trigger=IntervalTrigger(hours=settings.price_cache_ttl_hours),
        id="scrape_cardmarket",
        name="Scrape Cardmarket Prices",
        replace_existing=True,
    )
    
    scheduler.start()
    logger.info("Background scheduler started")


def stop_scheduler():
    """Stop the background scheduler"""
    scheduler.shutdown()
    logger.info("Background scheduler stopped")

