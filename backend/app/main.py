from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .cache import RedisCache
from .core.config import settings
from .core.rate_limiter import limiter, rate_limit_handler
from .routes import academic, delays, health, metrics, trains
from .scrapers.college_portal import CollegePortalScraper
from .services.academic_orchestrator import AcademicOrchestrator

app = FastAPI(title="Academic MCP Data Server")

# Setup CORS
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

# Database Setup
# Using a mock URL for this implementation, would be in settings in production
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/dbname"
engine = create_async_engine(DATABASE_URL)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)

# Global Dependencies
cache = RedisCache(settings.REDIS_URL)
scraper = CollegePortalScraper(base_url="https://college.portal")
orchestrator = AcademicOrchestrator(
    scraper=scraper,
    cache=cache,
    db_session_factory=async_session_factory
)

# Attach to state for dependency injection
app.state.orchestrator = orchestrator

# Register Routers
app.include_router(health.router)
app.include_router(academic.router)
app.include_router(trains.router)
app.include_router(metrics.router)
app.include_router(delays.router)

@app.on_event("shutdown")
async def shutdown_event():
    await cache.close()
