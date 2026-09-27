from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID


@dataclass
class MCPUserContext:
    """Authenticated user context propagated through MCP tool invocations."""
    user_id: UUID
    org_id: UUID
    role: str
    email: str
    scopes: List[str] = field(default_factory=list)
    request_id: Optional[str] = None
    client_name: Optional[str] = None


# Task-local ContextVar for the current MCP invocation context
_current_mcp_ctx: ContextVar[Optional[MCPUserContext]] = ContextVar("current_mcp_ctx", default=None)


def get_current_mcp_context() -> Optional[MCPUserContext]:
    return _current_mcp_ctx.get()


def set_mcp_context(ctx: Optional[MCPUserContext]):
    return _current_mcp_ctx.set(ctx)
