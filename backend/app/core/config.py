from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379/0"
    TTL_ATTENDANCE: int = 3600  # 1 Hour TTL for student attendance
    TTL_EXAMS: int = 86400     # 24 Hours TTL for exam timetables
    RATE_LIMIT_DEFAULT: str = "10/minute"
    SCRAPER_MAX_CONCURRENCY: int = 2  # Maximum parallel Playwright browser contexts

    model_config = ConfigDict(env_file=".env", extra="ignore")

settings = Settings()
