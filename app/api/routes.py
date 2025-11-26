"""
FastAPI routes and WebSocket endpoints
"""
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.database import Streamer, ScanHistory, Database
import logging
import json
import os

logger = logging.getLogger(__name__)

router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to websocket: {e}")
                disconnected.append(connection)

        # Remove disconnected clients
        for connection in disconnected:
            if connection in self.active_connections:
                self.active_connections.remove(connection)


manager = ConnectionManager()


# Dependency to get database session
def get_db():
    db_url = os.getenv("DATABASE_URL", "sqlite:///./tiktok_monitor.db")
    db_instance = Database(db_url)
    session = db_instance.get_session()
    try:
        yield session
    finally:
        session.close()


@router.get("/api/streamers")
async def get_streamers(
    query: Optional[str] = Query(None, description="Filter by search query"),
    is_live: Optional[bool] = Query(None, description="Filter by live status"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get list of streamers with optional filters"""
    try:
        # Build query
        db_query = db.query(Streamer)

        if query:
            db_query = db_query.filter(Streamer.query == query)

        if is_live is not None:
            db_query = db_query.filter(Streamer.is_live == is_live)

        # Order by last seen (most recent first)
        db_query = db_query.order_by(desc(Streamer.last_seen))

        # Get total count
        total = db_query.count()

        # Apply pagination
        streamers = db_query.offset(offset).limit(limit).all()

        return {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "data": [streamer.to_dict() for streamer in streamers]
        }
    except Exception as e:
        logger.error(f"Error getting streamers: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/api/streamers/{username}")
async def get_streamer(username: str, db: Session = Depends(get_db)):
    """Get specific streamer by username"""
    try:
        streamer = db.query(Streamer).filter(Streamer.username == username).first()
        if streamer:
            return {
                "success": True,
                "data": streamer.to_dict()
            }
        else:
            return {
                "success": False,
                "error": "Streamer not found"
            }
    except Exception as e:
        logger.error(f"Error getting streamer: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/api/statistics")
async def get_statistics(
    hours: int = Query(24, description="Statistics for last N hours"),
    db: Session = Depends(get_db)
):
    """Get statistics about scraping activity"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        # Total streamers
        total_streamers = db.query(Streamer).count()
        live_streamers = db.query(Streamer).filter(Streamer.is_live == True).count()

        # Recent scans
        recent_scans = db.query(ScanHistory).filter(
            ScanHistory.timestamp >= cutoff_time
        ).count()

        successful_scans = db.query(ScanHistory).filter(
            ScanHistory.timestamp >= cutoff_time,
            ScanHistory.success == True
        ).count()

        failed_scans = db.query(ScanHistory).filter(
            ScanHistory.timestamp >= cutoff_time,
            ScanHistory.success == False
        ).count()

        # Streamers by query
        streamers_by_query = db.query(
            Streamer.query,
            func.count(Streamer.id).label('count')
        ).group_by(Streamer.query).all()

        # Top streamers by times seen
        top_streamers = db.query(Streamer).order_by(
            desc(Streamer.times_seen)
        ).limit(10).all()

        # Recent scan history
        scan_history = db.query(ScanHistory).filter(
            ScanHistory.timestamp >= cutoff_time
        ).order_by(desc(ScanHistory.timestamp)).limit(20).all()

        return {
            "success": True,
            "data": {
                "total_streamers": total_streamers,
                "live_streamers": live_streamers,
                "recent_scans": recent_scans,
                "successful_scans": successful_scans,
                "failed_scans": failed_scans,
                "streamers_by_query": [
                    {"query": q, "count": c} for q, c in streamers_by_query
                ],
                "top_streamers": [s.to_dict() for s in top_streamers],
                "scan_history": [s.to_dict() for s in scan_history]
            }
        }
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/api/queries")
async def get_queries(db: Session = Depends(get_db)):
    """Get all unique search queries"""
    try:
        queries = db.query(Streamer.query).distinct().all()
        return {
            "success": True,
            "data": [q[0] for q in queries]
        }
    except Exception as e:
        logger.error(f"Error getting queries: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/api/scan-history")
async def get_scan_history(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get scan history"""
    try:
        total = db.query(ScanHistory).count()
        scans = db.query(ScanHistory).order_by(
            desc(ScanHistory.timestamp)
        ).offset(offset).limit(limit).all()

        return {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "data": [scan.to_dict() for scan in scans]
        }
    except Exception as e:
        logger.error(f"Error getting scan history: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and receive messages
            data = await websocket.receive_text()
            logger.info(f"Received WebSocket message: {data}")

            # Echo back or handle specific commands
            if data == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.post("/api/search-live")
async def search_live_streamers(
    query: str = Query(..., description="Search query"),
    db: Session = Depends(get_db)
):
    """
    Buscar streamers en vivo en tiempo real usando TikAPI y guardar en BD
    """
    try:
        from app.services.tikapi_service import TikAPIService
        from datetime import datetime

        api_key = os.getenv("TIKAPI_KEY")
        account_key = os.getenv("TIKAPI_ACCOUNT_KEY")

        if not api_key or not account_key:
            return {
                "success": False,
                "error": "TikAPI credentials not configured"
            }

        service = TikAPIService(api_key=api_key, account_key=account_key)
        usernames = service.search_live_streamers(query)

        # Save streamers to database
        streamers_data = []
        for username in usernames:
            existing = db.query(Streamer).filter(
                Streamer.username == username
            ).first()

            if existing:
                # Update existing streamer
                existing.last_seen = datetime.utcnow()
                existing.times_seen += 1
                existing.is_live = True
                existing.query = query
                streamers_data.append(existing.to_dict())
            else:
                # Create new streamer
                new_streamer = Streamer(
                    username=username,
                    query=query,
                    viewers=0,
                    first_seen=datetime.utcnow(),
                    last_seen=datetime.utcnow(),
                    times_seen=1,
                    is_live=True
                )
                db.add(new_streamer)
                db.flush()  # Get the ID
                streamers_data.append(new_streamer.to_dict())

        # Record scan history
        scan = ScanHistory(
            timestamp=datetime.utcnow(),
            query=query,
            streamers_found=len(usernames),
            success=True
        )
        db.add(scan)
        db.commit()

        return {
            "success": True,
            "query": query,
            "total": len(usernames),
            "streamers": usernames,
            "streamers_data": streamers_data
        }
    except Exception as e:
        logger.error(f"Error searching live streamers: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def broadcast_update(message_type: str, data: dict):
    """
    Helper function to broadcast updates to all WebSocket clients

    Args:
        message_type: Type of update (e.g., 'new_streamer', 'scan_complete')
        data: Data to send
    """
    await manager.broadcast({
        "type": message_type,
        "timestamp": datetime.utcnow().isoformat(),
        "data": data
    })
