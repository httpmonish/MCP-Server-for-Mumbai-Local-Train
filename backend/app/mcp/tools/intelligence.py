from typing import Any, Dict, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.models.auth import User
from app.services.intelligence_service import IntelligenceService
from ..context import MCPUserContext
from ..errors import MCPErrorCode, MCPToolException

logger = get_logger(__name__)


async def handle_check_commute_risk(
    ctx: MCPUserContext,
    db: AsyncSession,
    from_station: str,
    at_time: Optional[str] = None,
    arrival_buffer_minutes: int = 10,
    last_mile_minutes: int = 5,
) -> Dict[str, Any]:
    """
    Execute check_commute_risk tool by delegating to Phase 6 IntelligenceService.
    Preserves deterministic rules, reason codes, confidence, and data freshness.
    """
    if not from_station or not from_station.strip():
        raise MCPToolException(
            MCPErrorCode.INVALID_STATION,
            "Parameter 'from_station' is required.",
        )

    clean_from = from_station.strip().replace("\n", " ").replace("\r", " ")[:64]

    try:
        user_res = await db.execute(
            select(User).where(User.id == ctx.user_id, User.org_id == ctx.org_id)
        )
        user = user_res.scalars().first()
        if not user:
            raise MCPToolException(
                MCPErrorCode.MCP_UNAUTHORIZED,
                "User not found in the organization.",
            )

        response_model = await IntelligenceService.evaluate_commute_check(
            db=db,
            user=user,
            from_station=clean_from,
            at_time=at_time,
            arrival_buffer_minutes=max(0, min(arrival_buffer_minutes, 60)),
            last_mile_minutes=max(0, min(last_mile_minutes, 60)),
        )
    except MCPToolException:
        raise
    except Exception as e:
        logger.error(f"Intelligence service error in MCP tool: {e}", exc_info=True)
        raise MCPToolException(
            MCPErrorCode.INTERNAL_ERROR,
            f"Intelligence service error: {str(e)}",
        )

    # Convert Pydantic response model to clean dictionary
    return response_model.model_dump(mode="json")
