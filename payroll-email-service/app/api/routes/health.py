from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.email_sender import EmailSender
import redis.asyncio as redis
from app.config import settings

router = APIRouter()


@router.get("/")
async def health_check(db: Session = Depends(get_db)):
    """Check service health"""

    health_status = {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "database": "unknown",
        "redis": "unknown",
        "email_provider": "unknown",
    }

    # Check database
    try:
        db.execute("SELECT 1")
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"

    # Check Redis
    try:
        r = await redis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.close()
        health_status["redis"] = "connected"
    except Exception as e:
        health_status["redis"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    # Check email provider
    try:
        sender = EmailSender()
        provider_ok = await sender.check_provider_health()
        health_status["email_provider"] = "connected" if provider_ok else "failed"
    except Exception as e:
        health_status["email_provider"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    return health_status
