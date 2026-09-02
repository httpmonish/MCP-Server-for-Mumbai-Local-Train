from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..cache import RedisCache

router = APIRouter()

# Dependency to get a DB session (simplified for health check)
# In a real app, this would use the app's session factory
async def get_db_session():
    from ..main import async_session_factory
    async with async_session_factory() as session:
        yield session

async def get_cache():
    from ..main import cache
    return cache

@router.get("/health")
@router.get("/health/live")
async def health_check():
    """Basic liveness probe."""
    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/ready")
@router.get("/health/ready")
async def readiness_check(
    db_session: AsyncSession = Depends(get_db_session),
    cache: RedisCache = Depends(get_cache)
):
    """Readiness probe checking downstream dependencies."""
    services = {}
    is_ready = True

    # Check PostgreSQL
    try:
        await db_session.execute(text("SELECT 1"))
        services["database"] = "connected"
    except Exception as e:
        services["database"] = f"error: {str(e)}"
        is_ready = False

    # Check Redis
    try:
        if await cache.ping():
            services["redis"] = "connected"
        else:
            services["redis"] = "disconnected"
            is_ready = False
    except Exception as e:
        services["redis"] = f"error: {str(e)}"
        is_ready = False

    if is_ready:
        return {
            "status": "ready",
            "services": services
        }
    else:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "degraded",
                "services": services
            }
        )
