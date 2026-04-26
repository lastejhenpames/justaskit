from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.core.config import settings
import time
import psutil
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Track application start time
START_TIME = time.time()

@router.get("/health")
async def health_check():
    """
    Basic health check endpoint
    Returns 200 if service is alive
    """
    return {
        "status": "healthy",
        "service": "multi-agent-analytics",
        "version": "0.1.0",
        "uptime_seconds": int(time.time() - START_TIME)
    }

@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness check - verifies dependencies are available
    Checks: Database connection, OpenAI API key
    """
    checks = {
        "database": False,
        "openai_configured": False,
    }
    
    # Check database
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception as e:
        logger.error(f"Database check failed: {e}")
    
    # Check OpenAI configuration
    if settings.OPENAI_API_KEY and settings.OPENAI_BASE_URL:
        checks["openai_configured"] = True
    
    all_ready = all(checks.values())
    
    return {
        "status": "ready" if all_ready else "not_ready",
        "checks": checks,
        "timestamp": time.time()
    }

@router.get("/metrics")
async def metrics():
    """
    Basic metrics endpoint
    Returns system metrics and application stats
    """
    # System metrics
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    
    return {
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_mb": memory.available / (1024 * 1024),
        },
        "application": {
            "uptime_seconds": int(time.time() - START_TIME),
            "environment": settings.ENVIRONMENT,
        }
    }
