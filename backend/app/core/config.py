from pydantic import ConfigDict, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "मुंबईTeleport Platform"
    ENVIRONMENT: str = "development"

    # Database & Cache
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/mcp_production"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Authentication & JWT Configuration
    JWT_SECRET_KEY: str = "mumbai_teleport_super_secure_jwt_secret_key_change_in_prod_12345"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Password Policy
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_MAX_LENGTH: int = 128

    # Rate Limiting & Concurrency
    RATE_LIMIT_DEFAULT: str = "10/minute"
    RATE_LIMIT_LOGIN: str = "5/minute"
    SCRAPER_MAX_CONCURRENCY: int = 2

    # Academic & Timetable Cache TTL (in seconds)
    TTL_ATTENDANCE: int = 3600  # 1 Hour
    TTL_EXAMS: int = 86400  # 24 Hours

    # Telegram Alert Configuration
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""

    # Encryption Master Key
    ENCRYPTION_MASTER_KEY: str = "MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5MDE="
    # Transit Engine & Live Provider Configuration
    TRANSIT_PROVIDER: str = "mock"
    TRANSIT_LIVE_ENABLED: bool = True
    RAILRADAR_BASE_URL: str = "https://api.railradar.io"
    RAILRADAR_API_KEY: str = ""
    TRANSIT_CACHE_TTL_LIVE_TRAIN: int = 30  # 30 seconds
    TRANSIT_CACHE_TTL_STATION_BOARD: int = 60  # 60 seconds
    TRANSIT_CACHE_TTL_SCHEDULE: int = 43200  # 12 hours
    TRANSIT_LIVE_TIMEOUT_SECONDS: float = 3.5

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if not v or len(v.strip()) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long for secure HS256 signing.")
        return v.strip()

    model_config = ConfigDict(env_file=".env", extra="ignore")


settings = Settings()
