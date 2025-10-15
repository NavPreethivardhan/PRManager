"""
Health check endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.database import get_db
import redis

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "service": "pr-copilot"}


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness check with database connectivity"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        
        # Test Redis connection
        r = redis.Redis.from_url("redis://localhost:6379/0")
        r.ping()
        
        return {
            "status": "ready",
            "database": "connected",
            "redis": "connected"
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "error": str(e)
        }
