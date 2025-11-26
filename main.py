"""
TikTok Live Monitor - Main Application
"""
import os
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dotenv import load_dotenv

from app.models.database import Database
from app.services.scraper import run_scraper_job
from app.api.routes import router, broadcast_update

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tiktok_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global instances
db_instance = Database(os.getenv("DATABASE_URL", "sqlite:///./tiktok_monitor.db"))
scheduler = AsyncIOScheduler()


# Configuration
SEARCH_QUERIES = os.getenv("SEARCH_QUERIES", "gaming,music,cooking").split(",")
SCRAPE_INTERVAL_MINUTES = int(os.getenv("SCRAPE_INTERVAL_MINUTES", "5"))
TIKAPI_KEY = os.getenv("TIKAPI_KEY")
TIKAPI_ACCOUNT_KEY = os.getenv("TIKAPI_ACCOUNT_KEY")


async def scheduled_scrape_job():
    """Scheduled job to scrape TikTok live streams"""
    logger.info(f"Starting scheduled scrape job for queries: {SEARCH_QUERIES}")

    try:
        # Validate TikAPI credentials
        if not TIKAPI_KEY or not TIKAPI_ACCOUNT_KEY:
            logger.error("TikAPI credentials not configured. Please set TIKAPI_KEY and TIKAPI_ACCOUNT_KEY environment variables.")
            return

        # Get database session
        db = db_instance.get_session()

        # Run scraper with TikAPI credentials
        results = await run_scraper_job(
            SEARCH_QUERIES,
            db,
            api_key=TIKAPI_KEY,
            account_key=TIKAPI_ACCOUNT_KEY
        )

        logger.info(f"Scrape job completed: {results}")

        # Broadcast update to WebSocket clients
        await broadcast_update("scan_complete", {
            "results": results,
            "queries": SEARCH_QUERIES
        })

        db.close()

    except Exception as e:
        logger.error(f"Error in scheduled scrape job: {e}", exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("Starting TikTok Live Monitor...")

    # Initialize database
    db_instance.create_tables()
    logger.info("Database tables created")

    # No automatic scraping - only manual searches
    logger.info("Automatic scraping disabled - use manual search only")

    yield

    # Shutdown
    logger.info("Shutting down TikTok Live Monitor...")


# Create FastAPI app
app = FastAPI(
    title="TikTok Live Monitor",
    description="Monitor TikTok live streams and track streamers",
    version="1.0.0",
    lifespan=lifespan
)

# Include API routes
app.include_router(router)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def search_page():
    """Serve the search HTML page as main page"""
    try:
        with open("app/templates/search.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Error: search.html not found</h1>",
            status_code=500
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "scheduler_running": scheduler.running,
        "queries": SEARCH_QUERIES,
        "scrape_interval": f"{SCRAPE_INTERVAL_MINUTES} minutes",
        "tikapi_configured": bool(TIKAPI_KEY and TIKAPI_ACCOUNT_KEY)
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"Starting server on {host}:{port}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("RELOAD", "false").lower() == "true",
        log_level="info"
    )
