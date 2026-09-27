from datetime import date, datetime
from typing import Any, Dict, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.models.auth import User
from app.services.schedule_service import ScheduleEngineService
from ..context import MCPUserContext
from ..errors import MCPErrorCode, MCPToolException

logger = get_logger(__name__)


async def handle_get_my_schedule(
    ctx: MCPUserContext,
    db: AsyncSession,
    target_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute get_my_schedule tool by delegating to Phase 4 ScheduleEngineService.
    Scoping is enforced through the authenticated user's org_id and user_id.
    """
    parsed_date: Optional[date] = None
    if target_date and target_date.strip():
        try:
            parsed_date = datetime.strptime(target_date.strip(), "%Y-%m-%d").date()
        except ValueError:
            raise MCPToolException(
                MCPErrorCode.INTERNAL_ERROR,
                f"Invalid date format for target_date '{target_date}'. Expected YYYY-MM-DD.",
            )

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

        schedule_resp = await ScheduleEngineService.get_user_today_schedule(
            db=db,
            user=user,
            target_date=parsed_date,
        )
    except MCPToolException:
        raise
    except Exception as e:
        logger.error(f"Schedule service error in MCP tool: {e}", exc_info=True)
        raise MCPToolException(
            MCPErrorCode.INTERNAL_ERROR,
            "Schedule service encountered an error while resolving schedule.",
        )

    formatted_occurrences = []
    for occ in schedule_resp.items:
        formatted_occurrences.append({
            "slot_id": str(occ.slot_id),
            "title": occ.title,
            "schedule_title": occ.schedule_title,
            "schedule_type": occ.schedule_type.value if hasattr(occ.schedule_type, "value") else str(occ.schedule_type),
            "start_time": str(occ.start_time),
            "end_time": str(occ.end_time),
            "location_name": occ.location_name,
            "nearest_station_code": occ.nearest_station_code,
            "is_overnight": occ.is_overnight,
        })

    return {
        "user_id": str(ctx.user_id),
        "target_date": str(schedule_resp.date),
        "day_name": schedule_resp.day_name,
        "total_occurrences": len(formatted_occurrences),
        "has_schedule": len(formatted_occurrences) > 0,
        "occurrences": formatted_occurrences,
    }
