from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class MCPSettings(BaseSettings):
    PORTAL_DEFAULT_USERNAME: str = ""
    PORTAL_DEFAULT_PASSWORD: str = ""
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/mcp_data"
    REDIS_URL: str = "redis://localhost:6379/0"
    MCP_SERVER_NAME: str = "academic-transit-mcp"
    MCP_SERVER_VERSION: str = "1.0.0"

    model_config = ConfigDict(env_file=".env", extra="ignore")

mcp_settings = MCPSettings()
