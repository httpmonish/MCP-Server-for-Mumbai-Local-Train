from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .cache import RedisCache
from .core.config import settings
from .core.logger import get_logger
from .core.rate_limiter import limiter, rate_limit_handler
from .models.base import Base
from .routes import (
    academic,
    attendance,
    auth,
    delays,
    health,
    intelligence,
    metrics,
    organizations,
    schedules,
    trains,
)
from .scrapers.college_portal import CollegePortalScraper
from .services.academic_orchestrator import AcademicOrchestrator

logger = get_logger(__name__)

# Database Setup
DATABASE_URL = settings.DATABASE_URL
engine = create_async_engine(DATABASE_URL)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)

# Global Cache & Services
cache = RedisCache(settings.REDIS_URL)
scraper = CollegePortalScraper(base_url="https://college.portal")
orchestrator = AcademicOrchestrator(
    scraper=scraper,
    cache=cache,
    db_session_factory=async_session_factory,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Try to verify and create tables
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.warning(f"Database connection skipped during startup ({e}). Operating in degraded/fallback mode.")

    yield

    # Shutdown: Clean up connections
    try:
        await cache.close()
    except Exception as e:
        logger.warning(f"Cache close error during shutdown: {e}")
    try:
        await engine.dispose()
    except Exception as e:
        logger.warning(f"Engine dispose error during shutdown: {e}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Identity, Authentication, Multi-tenant Organization Management, and Commuter Telemetry Platform",
    lifespan=lifespan,
)

# Setup CORS with explicit security policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# Attach dependencies to state
app.state.async_session_factory = async_session_factory
app.state.cache = cache
app.state.orchestrator = orchestrator

# Register Routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(organizations.router)
app.include_router(schedules.router)
app.include_router(attendance.router)
app.include_router(intelligence.router)
app.include_router(academic.router)
app.include_router(trains.router)
app.include_router(metrics.router)
app.include_router(delays.router)

# Mount MCP (Model Context Protocol) Server endpoint
if settings.MCP_ENABLED:
    from .mcp import create_mcp_app

    app.mount("/mcp", create_mcp_app())

