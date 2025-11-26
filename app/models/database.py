"""
Database models for TikTok Live Monitor
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Streamer(Base):
    """Model for storing streamer information"""
    __tablename__ = "streamers"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    query = Column(String, index=True, nullable=False)  # Search query used to find them
    viewers = Column(Integer, default=0)
    first_seen = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen = Column(DateTime, default=datetime.utcnow, nullable=False)
    times_seen = Column(Integer, default=1)
    is_live = Column(Boolean, default=True)

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "username": self.username,
            "query": self.query,
            "viewers": self.viewers,
            "first_seen": self.first_seen.isoformat() if self.first_seen else None,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "times_seen": self.times_seen,
            "is_live": self.is_live
        }


class ScanHistory(Base):
    """Model for storing scan history"""
    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    query = Column(String, nullable=False)
    streamers_found = Column(Integer, default=0)
    success = Column(Boolean, default=True)
    error_message = Column(String, nullable=True)

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "query": self.query,
            "streamers_found": self.streamers_found,
            "success": self.success,
            "error_message": self.error_message
        }


class Database:
    """Database manager class"""

    def __init__(self, database_url: str = "sqlite:///./tiktok_monitor.db"):
        self.engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(bind=self.engine)

    def get_session(self):
        """Get a new database session"""
        db = self.SessionLocal()
        try:
            return db
        except Exception:
            db.close()
            raise

    def close_session(self, db):
        """Close a database session"""
        db.close()
