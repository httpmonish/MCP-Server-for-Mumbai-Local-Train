import asyncio
import time
from typing import Any, Dict, Optional

from mcp.server.mcpserver import MCPServer
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..core.config import settings
from ..core.logger import get_logger
from .audit import record_mcp_tool_audit
from .auth import (
    SCOPE_ATTENDANCE_READ,
    SCOPE_INTELLIGENCE_READ,
    SCOPE_SCHEDULE_READ,
    SCOPE_TRANSIT_READ,
    resolve_mcp_user_context,
)
from .context import MCPUserContext, get_current_mcp_context, set_mcp_context
from .errors import MCPErrorCode, MCPToolException, format_mcp_error
from .tools.attendance import handle_get_attendance_summary
from .tools.intelligence import handle_check_commute_risk
from .tools.schedule import handle_get_my_schedule
from .tools.transit import handle_get_next_train

logger = get_logger("mcp.server")

# Database session engine for MCP operations
_engine = create_async_engine(settings.DATABASE_URL)
_async_session_factory = async_sessionmaker(_engine, expire_on_commit=False)


def set_mcp_session_factory(factory):
    """Override session factory for testing environments."""
    global _async_session_factory
    _async_session_factory = factory


# Initialize production MCPServer instance
mcp_server = MCPServer(
    name=settings.MCP_SERVER_NAME,
    version=settings.MCP_SERVER_VERSION,
    instructions=(
        "TransitPulse Platform MCP Server. "
        "Provides read-only access to authenticated student/employee schedules, "
        "attendance summaries, Mumbai suburban railway transit telemetry, and "
        "deterministic commute risk intelligence. "
        "All sensitive operations require a valid JWT bearer token."
    ),
)


async def _resolve_execution_context(
    token: Optional[str] = None,
    required_scope: Optional[str] = None,
    db: Optional[AsyncSession] = None,
) -> MCPUserContext:
    """Resolve user context from active ContextVar or provided token."""
    existing_ctx = get_current_mcp_context()
    if existing_ctx:
        return existing_ctx

    if not token:
        raise MCPToolException(
            MCPErrorCode.MCP_UNAUTHORIZED,
            "Authentication required. Provide a valid JWT bearer token.",
        )

    return await resolve_mcp_user_context(
        token=token,
        db=db,
        required_scope=required_scope,
    )


@mcp_server.tool(
    name="get_my_schedule",
    description=(
        "Retrieve the authenticated user's scheduled classes or work shifts for today or a specific date. "
        "Returns start time, end time, location, destination station, and mandatory attendance flags. "
        "This tool is read-only and strictly scoped to the authenticated user's tenant organization."
    ),
)
async def get_my_schedule(
    token: Optional[str] = None,
    target_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get current user's schedule for today or a specified target date (YYYY-MM-DD).
    """
    start_time = time.perf_counter()
    ctx: Optional[MCPUserContext] = None
    try:
        async with _async_session_factory() as db:
            ctx = await _resolve_execution_context(
                token=token,
                required_scope=SCOPE_SCHEDULE_READ,
                db=db,
            )
            result = await handle_get_my_schedule(ctx=ctx, db=db, target_date=target_date)
            latency = (time.perf_counter() - start_time) * 1000
            await record_mcp_tool_audit("get_my_schedule", ctx, "SUCCESS", latency)
            return result
    except MCPToolException as e:
        latency = (time.perf_counter() - start_time) * 1000
        await record_mcp_tool_audit("get_my_schedule", ctx, "ERROR", latency, e.code.value)
        return e.to_dict()
    except Exception as err:
        logger.error(f"Unexpected error in get_my_schedule: {err}", exc_info=True)
        latency = (time.perf_counter() - start_time) * 1000
        await record_mcp_tool_audit("get_my_schedule", ctx, "ERROR", latency, MCPErrorCode.INTERNAL_ERROR.value)
        return format_mcp_error(MCPErrorCode.INTERNAL_ERROR, "An internal error occurred while retrieving schedule.")


@mcp_server.tool(
    name="get_attendance_summary",
    description=(
        "Retrieve the authenticated user's aggregate lecture/shift attendance summary, "
        "including total conducted sessions, attended sessions, current percentage, "
        "applicable minimum policy threshold (e.g., 75%), shortage count, and recovery classes required. "
        "This tool is read-only and strictly scoped to the authenticated user's tenant organization."
    ),
)
async def get_attendance_summary(
    token: Optional[str] = None,
    period: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get current user's attendance metrics and policy status.
    """
    start_time = time.perf_counter()
    ctx: Optional[MCPUserContext] = None
    try:
        async with _async_session_factory() as db:
            ctx = await _resolve_execution_context(
                token=token,
                required_scope=SCOPE_ATTENDANCE_READ,
                db=db,
            )
            result = await handle_get_attendance_summary(ctx=ctx, db=db, period=period)
            latency = (time.perf_counter() - start_time) * 1000
            await record_mcp_tool_audit("get_attendance_summary", ctx, "SUCCESS", latency)
            return result
    except MCPToolException as e:
        latency = (time.perf_counter() - start_time) * 1000
        await record_mcp_tool_audit("get_attendance_summary", ctx, "ERROR", latency, e.code.value)
        return e.to_dict()
    except Exception as err:
        logger.error(f"Unexpected error in get_attendance_summary: {err}", exc_info=True)
        latency = (time.perf_counter() - start_time) * 1000
        await record_mcp_tool_audit("get_attendance_summary", ctx, "ERROR", latency, MCPErrorCode.INTERNAL_ERROR.value)
        return format_mcp_error(MCPErrorCode.INTERNAL_ERROR, "An internal error occurred while retrieving attendance.")


@mcp_server.tool(
    name="get_next_train",
    description=(
        "Look up upcoming Mumbai suburban local trains between two railway stations. "
        "Returns departure time, expected arrival, train numbers, delay minutes, "
        "and data freshness provenance (REALTIME vs STATIC_TIMETABLE). "
        "Public read-only transit lookup."
    ),
)
async def get_next_train(
    from_station: str,
    to_station: str,
    query_time: Optional[str] = None,
    limit: int = 5,
    token: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Look up next available trains between from_station and to_station.
    """
    start_time = time.perf_counter()
    ctx: Optional[MCPUserContext] = None
    try:
        # Optional auth context propagation
        if token or get_current_mcp_context():
            try:
                ctx = await _resolve_execution_context(token=token, required_scope=SCOPE_TRANSIT_READ)
            except Exception:
                pass  # Transit lookup is permitted public/unauthenticated

        result = await handle_get_next_train(
            from_station=from_station,
            to_station=to_station,
            query_time=query_time,
            limit=limit,
        )
        latency = (time.perf_counter() - start_time) * 1000
        await record_mcp_tool_audit("get_next_train", ctx, "SUCCESS", latency)
        return result
    except MCPToolException as e:
        latency = (time.perf_counter() - start_time) * 1000
        await record_mcp_tool_audit("get_next_train", ctx, "ERROR", latency, e.code.value)
        return e.to_dict()
    except Exception as err:
        logger.error(f"Unexpected error in get_next_train: {err}", exc_info=True)
        latency = (time.perf_counter() - start_time) * 1000
        await record_mcp_tool_audit("get_next_train", ctx, "ERROR", latency, MCPErrorCode.INTERNAL_ERROR.value)
        return format_mcp_error(MCPErrorCode.INTERNAL_ERROR, "An internal error occurred while searching trains.")


@mcp_server.tool(
    name="check_commute_risk",
    description=(
        "Evaluate real-time commute feasibility and attendance risk for the authenticated user's "
        "next scheduled class or shift. Combines transit live telemetry, required arrival buffer, "
        "and attendance policy thresholds to compute a deterministic risk status (NORMAL, COMMUTE_RISK, "
        "ATTENDANCE_RISK, COMBINED_RISK) with structured explainability reason codes."
    ),
)
async def check_commute_risk(
    from_station: str,
    token: Optional[str] = None,
    at_time: Optional[str] = None,
    arrival_buffer_minutes: int = 10,
    last_mile_minutes: int = 5,
) -> Dict[str, Any]:
    """
    Evaluate deterministic commute risk from origin station to the next scheduled destination.
    """
    start_time = time.perf_counter()
    ctx: Optional[MCPUserContext] = None
    try:
        async with _async_session_factory() as db:
            ctx = await _resolve_execution_context(
                token=token,
                required_scope=SCOPE_INTELLIGENCE_READ,
                db=db,
            )
            result = await handle_check_commute_risk(
                ctx=ctx,
                db=db,
                from_station=from_station,
                at_time=at_time,
                arrival_buffer_minutes=arrival_buffer_minutes,
                last_mile_minutes=last_mile_minutes,
            )
            latency = (time.perf_counter() - start_time) * 1000
            await record_mcp_tool_audit("check_commute_risk", ctx, "SUCCESS", latency)
            return result
    except MCPToolException as e:
        latency = (time.perf_counter() - start_time) * 1000
        await record_mcp_tool_audit("check_commute_risk", ctx, "ERROR", latency, e.code.value)
        return e.to_dict()
    except Exception as err:
        logger.error(f"Unexpected error in check_commute_risk: {err}", exc_info=True)
        latency = (time.perf_counter() - start_time) * 1000
        await record_mcp_tool_audit("check_commute_risk", ctx, "ERROR", latency, MCPErrorCode.INTERNAL_ERROR.value)
        return format_mcp_error(MCPErrorCode.INTERNAL_ERROR, "An internal error occurred while evaluating commute risk.")


def get_mcp_server() -> MCPServer:
    return mcp_server


def create_mcp_app():
    """Create ASGI application for Streamable HTTP transport mounting."""
    return mcp_server.streamable_http_app()


async def run_mcp_stdio():
    """Run MCP server over stdio for local development and Claude Desktop testing."""
    await mcp_server.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(run_mcp_stdio())
