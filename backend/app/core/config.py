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

    # MCP (Model Context Protocol) Server Configuration
    MCP_ENABLED: bool = True
    MCP_SERVER_NAME: str = "TransitPulse-MCP"
    MCP_SERVER_VERSION: str = "1.0.0"
    MCP_TRANSPORT: str = "streamable_http"  # streamable_http | stdio
    MCP_AUTH_ISSUER: str = "transitpulse-auth"
    MCP_AUTH_AUDIENCE: str = "transitpulse-mcp"
    MCP_RATE_LIMIT: str = "30/minute"

    # Notification & Alerting Configuration (Phase 8)
    NOTIFICATION_EMAIL_PROVIDER: str = "mock"  # mock | sendgrid
    NOTIFICATION_SENDGRID_API_KEY: str = ""
    NOTIFICATION_FROM_EMAIL: str = "alerts@transitpulse.io"
    NOTIFICATION_FROM_NAME: str = "TransitPulse Alerts"
    NOTIFICATION_DEFAULT_QUIET_HOURS_START: str = "22:00"
    NOTIFICATION_DEFAULT_QUIET_HOURS_END: str = "06:00"
    NOTIFICATION_MAX_RETRIES: int = 3
    NOTIFICATION_INITIAL_RETRY_DELAY_SEC: int = 5
    NOTIFICATION_RATE_LIMIT: str = "60/minute"

    # Observability, Reliability & Security Hardening (Phase 9)
    APP_VERSION: str = "1.0.0"
    GIT_COMMIT: str = "main"
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json | console
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    SECURITY_HEADERS_ENABLED: bool = True
    ALLOWED_CORS_ORIGINS: list[str] = ["*"]
    REQUEST_TIMEOUT_SECONDS: float = 15.0

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if not v or len(v.strip()) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long for secure HS256 signing.")
        return v.strip()

    model_config = ConfigDict(env_file=".env", extra="ignore")


settings = Settings()
