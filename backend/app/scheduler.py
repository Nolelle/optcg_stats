from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.scrapers import TCGMatchmakingScraper, TCGPlayerScraper, CardmarketScraper
from app.scrapers import OPTCGAPIImporter, LimitlessTCGScraper
from app.config import get_settings
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


# ============ NEW DATA SOURCES (WORKING) ============

async def import_optcg_api_data():
    """Import cards and prices from OPTCG API (optcgapi.com)"""
    logger.info("Starting OPTCG API import...")
    db = SessionLocal()
    try:
        importer = OPTCGAPIImporter(db)
        results = await importer.import_all()
        logger.info(f"OPTCG API import complete: {results}")
        return results
    except Exception as e:
        logger.error(f"Error in OPTCG API import: {e}")
        return {"error": str(e)}
    finally:
        db.close()


async def scrape_limitless_data():
    """Scrape tournament/meta data from Limitless TCG"""
    logger.info("Starting Limitless TCG scrape...")
    db = SessionLocal()
    try:
        scraper = LimitlessTCGScraper(db)
        results = await scraper.scrape()
        logger.info(f"Limitless TCG scrape complete: {results}")
        return results
    except Exception as e:
        logger.error(f"Error in Limitless TCG scrape: {e}")
        return {"error": str(e)}
    finally:
        db.close()


# ============ LEGACY SCRAPERS (TEMPLATE CODE) ============

async def scrape_matchmaking_data():
    """Scheduled job to scrape TCG Matchmaking data (legacy - template only)"""
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
    """Scheduled job to scrape TCGPlayer prices (legacy - template only)"""
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
    """Scheduled job to scrape Cardmarket prices (legacy - template only)"""
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
    # Schedule OPTCG API import every 24 hours (card data updates daily)
    scheduler.add_job(
        import_optcg_api_data,
        trigger=IntervalTrigger(hours=24),
        id="import_optcg_api",
        name="Import OPTCG API Data (Cards & Prices)",
        replace_existing=True,
    )
    
    # Schedule Limitless TCG scrape every 6 hours (tournament data)
    scheduler.add_job(
        scrape_limitless_data,
        trigger=IntervalTrigger(hours=settings.scrape_interval_hours),
        id="scrape_limitless",
        name="Scrape Limitless TCG Meta Data",
        replace_existing=True,
    )
    
    # Legacy scrapers (kept for reference but not scheduled by default)
    # Uncomment if you want to enable these template scrapers
    # scheduler.add_job(
    #     scrape_matchmaking_data,
    #     trigger=IntervalTrigger(hours=settings.scrape_interval_hours),
    #     id="scrape_matchmaking",
    #     name="Scrape TCG Matchmaking Data",
    #     replace_existing=True,
    # )
    
    scheduler.start()
    logger.info("Background scheduler started")


def stop_scheduler():
    """Stop the background scheduler"""
    scheduler.shutdown()
    logger.info("Background scheduler stopped")

