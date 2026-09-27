from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .cache import RedisCache
from .core.config import settings
from .core.errors import register_error_handlers
from .core.logger import get_logger
from .core.middleware import ObservabilityAndSecurityMiddleware
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
    notifications,
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


# Initialize Sentry if configured
if getattr(settings, "SENTRY_DSN", None):
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration

        def before_send_filter(event, hint):
            # Strip sensitive headers and PII before sending to Sentry
            if "request" in event and "headers" in event["request"]:
                headers = event["request"]["headers"]
                for sensitive in ["authorization", "cookie", "x-api-key"]:
                    if sensitive in headers:
                        headers[sensitive] = "[REDACTED]"
            return event

        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENVIRONMENT,
            release=f"{settings.PROJECT_NAME}@{settings.APP_VERSION}",
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
            before_send=before_send_filter,
            integrations=[FastApiIntegration()],
        )
        logger.info("Sentry monitoring initialized successfully.")
    except Exception as e:
        logger.warning(f"Sentry initialization skipped: {e}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.APP_VERSION,
    description="Identity, Authentication, Multi-tenant Organization Management, and Commuter Telemetry Platform",
    lifespan=lifespan,
)

# Setup Observability & Security Headers Middleware
app.add_middleware(ObservabilityAndSecurityMiddleware)

# Setup CORS with explicit security policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Rate Limiter & Standardized Error Handlers
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
register_error_handlers(app)

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
app.include_router(notifications.router)
app.include_router(academic.router)
app.include_router(trains.router)
app.include_router(metrics.router)
app.include_router(delays.router)

# Mount MCP (Model Context Protocol) Server endpoint
if settings.MCP_ENABLED:
    from .mcp import create_mcp_app

    app.mount("/mcp", create_mcp_app())
