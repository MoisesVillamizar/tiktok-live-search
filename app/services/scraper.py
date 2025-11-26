"""
TikTok Live Scraper Service using TikAPI
This module wraps the TikAPI service to maintain backward compatibility
"""
import logging
from typing import List
from sqlalchemy.orm import Session
from app.services.tikapi_service import run_scraper_job as tikapi_run_scraper_job

logger = logging.getLogger(__name__)


async def run_scraper_job(queries: List[str], db: Session, api_key: str = None, account_key: str = None, **kwargs):
    """
    Convenience function to run scraper job using TikAPI

    Args:
        queries: List of search queries
        db: Database session
        api_key: TikAPI API key (required)
        account_key: TikAPI account key (required)
        **kwargs: Additional arguments (for backward compatibility, will be ignored)

    Returns:
        Dictionary with scraping statistics
    """
    if not api_key or not account_key:
        error_msg = "TikAPI credentials (api_key and account_key) are required"
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.info(f"Running scraper job with TikAPI for queries: {queries}")
    return tikapi_run_scraper_job(queries, db, api_key, account_key)
