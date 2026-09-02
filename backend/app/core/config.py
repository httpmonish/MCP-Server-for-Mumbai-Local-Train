from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379/0"
    TTL_ATTENDANCE: int = 3600  # 1 Hour TTL for student attendance
    TTL_EXAMS: int = 86400     # 24 Hours TTL for exam timetables
    RATE_LIMIT_DEFAULT: str = "10/minute"
    SCRAPER_MAX_CONCURRENCY: int = 2  # Maximum parallel Playwright browser contexts
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/mcp_production"
    ENCRYPTION_MASTER_KEY: str = "MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5MDE="

    model_config = ConfigDict(env_file=".env", extra="ignore")

settings = Settings()
