from enum import Enum
from typing import Any, Dict, Optional


class MCPErrorCode(str, Enum):
    MCP_UNAUTHORIZED = "MCP_UNAUTHORIZED"
    MCP_FORBIDDEN = "MCP_FORBIDDEN"
    INVALID_STATION = "INVALID_STATION"
    NO_UPCOMING_SCHEDULE = "NO_UPCOMING_SCHEDULE"
    NO_TRANSIT_OPTION = "NO_TRANSIT_OPTION"
    ATTENDANCE_UNAVAILABLE = "ATTENDANCE_UNAVAILABLE"
    DEPENDENCY_TIMEOUT = "DEPENDENCY_TIMEOUT"
    RATE_LIMITED = "RATE_LIMITED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class MCPToolException(Exception):
    """Safe, structured exception for MCP tool invocations without leaking internal stack traces."""

    def __init__(
        self,
        code: MCPErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": True,
            "error_code": self.code.value,
            "message": self.message,
            "details": self.details,
        }


def format_mcp_error(
    code: MCPErrorCode,
    message: str,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "error": True,
        "error_code": code.value,
        "message": message,
        "details": details or {},
    }
