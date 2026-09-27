from datetime import datetime, timezone
from typing import Any, Dict, Optional

from ..core.logger import get_logger
from .context import MCPUserContext

logger = get_logger("mcp.audit")


async def record_mcp_tool_audit(
    tool_name: str,
    ctx: Optional[MCPUserContext],
    status: str,
    latency_ms: float,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Structured audit logging for every MCP tool invocation.
    Guarantees user context and tenant isolation traceability without leaking sensitive payloads.
    """
    user_id_str = str(ctx.user_id) if ctx else "unauthenticated"
    org_id_str = str(ctx.org_id) if ctx else "none"
    request_id = ctx.request_id if ctx else "none"
    client_name = ctx.client_name if ctx else "unknown"

    safe_details = {k: v for k, v in (details or {}).items() if not any(sens in k.lower() for sens in ("token", "password", "secret", "key"))}

    audit_entry = {
        "event": "MCP_TOOL_CALLED",
        "called_by": "mcp_agent",
        "client_name": client_name,
        "tool_name": tool_name,
        "user_id": user_id_str,
        "organization_id": org_id_str,
        "request_id": request_id,
        "status": status,
        "latency_ms": round(latency_ms, 2),
        "error_code": error_code,
        "details": safe_details,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if status == "SUCCESS":
        logger.info(
            f"MCP Tool Execution: {tool_name} status={status} user={user_id_str} org={org_id_str} latency={latency_ms:.1f}ms",
            extra=audit_entry,
        )
    else:
        logger.warning(
            f"MCP Tool Error: {tool_name} status={status} error={error_code} user={user_id_str} org={org_id_str} latency={latency_ms:.1f}ms",
            extra=audit_entry,
        )
