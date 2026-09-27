from typing import Any, Dict, Optional

from app.core.logger import get_logger
from app.services.attendance_service import AttendanceService
from sqlalchemy.ext.asyncio import AsyncSession

from ..context import MCPUserContext
from ..errors import MCPErrorCode, MCPToolException

logger = get_logger(__name__)


async def handle_get_attendance_summary(
    ctx: MCPUserContext,
    db: AsyncSession,
    period: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute get_attendance_summary tool by delegating to Phase 5 AttendanceService.
    Scoping is enforced through the authenticated user's org_id and user_id.
    """
    try:
        summary_resp = await AttendanceService.get_user_summary(
            db=db,
            org_id=ctx.org_id,
            user_id=ctx.user_id,
        )
    except Exception as e:
        logger.error(f"Attendance service error in MCP tool: {e}", exc_info=True)
        raise MCPToolException(
            MCPErrorCode.ATTENDANCE_UNAVAILABLE,
            "Attendance service is currently unavailable.",
        )

    # Format into a clean, bounded, structured representation
    is_shortage = summary_resp.percentage < summary_resp.min_percentage_required
    return {
        "user_id": str(ctx.user_id),
        "total_sessions": summary_resp.total_sessions,
        "counted_sessions": summary_resp.counted_sessions,
        "present_count": summary_resp.present_count,
        "late_count": summary_resp.late_count,
        "absent_count": summary_resp.absent_count,
        "excused_count": summary_resp.excused_count,
        "percentage": summary_resp.percentage,
        "minimum_required_percentage": summary_resp.min_percentage_required,
        "status": summary_resp.status.value if hasattr(summary_resp.status, "value") else str(summary_resp.status),
        "is_shortage": is_shortage,
        "shortage_percentage": summary_resp.shortage_percentage,
        "sessions_needed_to_recover": summary_resp.sessions_needed_to_recover,
        "policy_name": summary_resp.policy_name,
    }
