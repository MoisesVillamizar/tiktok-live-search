"""
TikTok Live Scraper Service using TikAPI
"""
import json
import logging
from datetime import datetime
from typing import List, Dict
from tikapi import TikAPI, ValidationException, ResponseException
from sqlalchemy.orm import Session
from app.models.database import Streamer, ScanHistory

logger = logging.getLogger(__name__)


class TikAPIService:
    """Service for fetching TikTok Live streams using TikAPI"""

    def __init__(self, api_key: str, account_key: str):
        """
        Initialize TikAPI service

        Args:
            api_key: TikAPI API key
            account_key: TikAPI account key
        """
        self.api_key = api_key
        self.account_key = account_key
        self.api = TikAPI(api_key)
        self.user = self.api.user(accountKey=account_key)
        logger.info("TikAPI service initialized")

    def _extract_room_ids(self, json_texto: str) -> List[str]:
        """
        Extract room IDs from search response

        Args:
            json_texto: JSON response text from TikAPI

        Returns:
            List of room IDs
        """
        try:
            datos = json.loads(json_texto)
            room_ids = []

            for item in datos.get("data", []):
                room_info = item.get("live_info", {}).get("owner", {}).get("own_room", {})
                ids = room_info.get("room_ids", [])
                room_ids.extend(ids)

            return room_ids

        except json.JSONDecodeError:
            logger.error("Error: El texto proporcionado no es un JSON válido.")
            return []

    def _extract_display_ids(self, json_str: str) -> List[str]:
        """
        Extract display IDs from search response

        Args:
            json_str: JSON response text from TikAPI

        Returns:
            List of display IDs (usernames)
        """
        display_ids = []
        try:
            datos = json.loads(json_str)

            for item in datos.get("data", []):
                display_id = item.get("live_info", {}).get("owner", {}).get("display_id")
                if display_id:
                    display_ids.append(str(display_id))

        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Error procesando el JSON: {e}")

        return display_ids

    def _extract_display_ids_recommended(self, json_str: str) -> List[str]:
        """
        Extract display IDs from recommended response

        Args:
            json_str: JSON response text from TikAPI

        Returns:
            List of display IDs (usernames)
        """
        display_ids = []
        try:
            datos = json.loads(json_str)

            for item in datos.get("data", []):
                display_id = item.get("owner", {}).get("display_id")
                if display_id:
                    display_ids.append(str(display_id))

        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Error procesando el JSON: {e}")

        return display_ids

    def search_live_streamers(self, query: str) -> List[str]:
        """
        Search for live streamers by query and get recommended streamers

        Args:
            query: Search query

        Returns:
            List of unique display IDs (usernames)

        Raises:
            Exception: If rate limit is reached or other API errors occur
        """
        all_display_ids = []

        try:
            # Search for live streams
            logger.info(f"Searching for live streams with query: {query}")
            response = self.user.live.search(query=query)

            # Extract display IDs from search results
            search_display_ids = self._extract_display_ids(response.text)
            all_display_ids.extend(search_display_ids)
            logger.info(f"Found {len(search_display_ids)} streamers from search")

            # Extract room IDs for recommendations (limit to first 5 for speed)
            room_ids = self._extract_room_ids(response.text)
            logger.info(f"Found {len(room_ids)} room IDs, using first 5 for recommendations")

            # Get recommended streamers for each room (limited to 5 for faster results)
            for room_id in room_ids[:5]:
                try:
                    response1 = self.user.live.recommend(room_id=str(room_id))
                    recommended_ids = self._extract_display_ids_recommended(response1.text)
                    all_display_ids.extend(recommended_ids)
                    logger.info(f"Found {len(recommended_ids)} recommended streamers for room {room_id}")

                except ValidationException as e:
                    logger.error(f"Validation error for room {room_id}: {e}, field: {e.field}")

                except ResponseException as e:
                    logger.error(f"Response error for room {room_id}: {e}, status: {e.response.status_code}")

        except ValidationException as e:
            logger.error(f"Validation error searching for '{query}': {e}, field: {e.field}")
            raise Exception(f"Validation error: {e}")

        except ResponseException as e:
            logger.error(f"Response error searching for '{query}': {e}, status: {e.response.status_code}")
            if e.response.status_code == 429:
                raise Exception("Rate limit alcanzado. Por favor espera unos minutos antes de hacer otra búsqueda.")
            elif e.response.status_code == 401:
                raise Exception("Credenciales de TikAPI inválidas. Verifica tu API key y account key.")
            else:
                raise Exception(f"Error de API: {e} (status: {e.response.status_code})")

        # Remove duplicates while preserving order
        unique_display_ids = list(dict.fromkeys(all_display_ids))
        logger.info(f"Total unique streamers found for '{query}': {len(unique_display_ids)}")

        return unique_display_ids

    def scrape_multiple_queries(self, queries: List[str], db: Session) -> Dict:
        """
        Scrape multiple queries and store results in database

        Args:
            queries: List of search queries
            db: Database session

        Returns:
            Dictionary with scraping statistics
        """
        total_found = 0
        total_new = 0
        total_updated = 0
        errors = []

        for query in queries:
            try:
                logger.info(f"Scraping query: {query}")
                usernames = self.search_live_streamers(query)

                # Update database
                for username in usernames:
                    existing = db.query(Streamer).filter(
                        Streamer.username == username
                    ).first()

                    if existing:
                        # Update existing streamer
                        existing.last_seen = datetime.utcnow()
                        existing.times_seen += 1
                        existing.is_live = True
                        existing.query = query  # Update with latest query
                        total_updated += 1
                        logger.info(f"Updated streamer: {username}")
                    else:
                        # Create new streamer
                        new_streamer = Streamer(
                            username=username,
                            query=query,
                            viewers=0,  # TikAPI doesn't provide viewer count in this endpoint
                            first_seen=datetime.utcnow(),
                            last_seen=datetime.utcnow(),
                            times_seen=1,
                            is_live=True
                        )
                        db.add(new_streamer)
                        total_new += 1
                        logger.info(f"Added new streamer: {username}")

                total_found += len(usernames)

                # Record scan history
                scan = ScanHistory(
                    timestamp=datetime.utcnow(),
                    query=query,
                    streamers_found=len(usernames),
                    success=True
                )
                db.add(scan)
                db.commit()

            except Exception as e:
                error_msg = f"Error scraping query '{query}': {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)

                # Record failed scan
                scan = ScanHistory(
                    timestamp=datetime.utcnow(),
                    query=query,
                    streamers_found=0,
                    success=False,
                    error_message=str(e)
                )
                db.add(scan)
                db.commit()

        return {
            "total_found": total_found,
            "total_new": total_new,
            "total_updated": total_updated,
            "queries_processed": len(queries),
            "errors": errors
        }


def run_scraper_job(queries: List[str], db: Session, api_key: str, account_key: str):
    """
    Convenience function to run scraper job using TikAPI

    Args:
        queries: List of search queries
        db: Database session
        api_key: TikAPI API key
        account_key: TikAPI account key

    Returns:
        Dictionary with scraping statistics
    """
    service = TikAPIService(api_key=api_key, account_key=account_key)
    results = service.scrape_multiple_queries(queries, db)
    logger.info(f"Scraping completed: {results}")
    return results
