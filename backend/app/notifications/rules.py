import hashlib
from datetime import datetime, time, timezone
from typing import Any, Dict, Optional, Tuple
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.logger import get_logger
from ..models.notification import (
    NotificationChannel,
    NotificationPreference,
    NotificationPriority,
    NotificationType,
)

logger = get_logger("notifications.rules")


def is_in_quiet_hours(
    check_time: time,
    quiet_start: Optional[time],
    quiet_end: Optional[time],
) -> bool:
    """
    Check if a given local time falls within quiet hours.
    Handles overnight quiet hour windows (e.g. 22:00 -> 06:00).
    """
    if not quiet_start or not quiet_end:
        return False

    if quiet_start <= quiet_end:
        return quiet_start <= check_time <= quiet_end
    else:
        # Crosses midnight (e.g., 22:00 to 06:00)
        return check_time >= quiet_start or check_time <= quiet_end


def compute_deduplication_key(
    notification_type: NotificationType,
    user_id: UUID,
    payload: Dict[str, Any],
) -> str:
    """
    Generate a deterministic deduplication key for atomic database idempotency.
    """
    if notification_type == NotificationType.ATTENDANCE_BELOW_THRESHOLD:
        percentage = payload.get("percentage", 0.0)
        # Group percentage to integer buckets to debounce minor floating point wobbles
        pct_bucket = int(round(percentage))
        now_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return f"notif:att_below:{user_id}:{now_date}:{pct_bucket}"

    elif notification_type == NotificationType.COMMUTE_DELAY_RISK:
        slot_id = payload.get("slot_id", "none")
        risk_status = payload.get("risk_status", "AT_RISK")
        now_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return f"notif:commute_risk:{user_id}:{slot_id}:{now_date}:{risk_status}"

    elif notification_type == NotificationType.CLASS_STARTING_REMINDER:
        slot_id = payload.get("slot_id", "none")
        target_date = payload.get("target_date") or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return f"notif:class_remind:{user_id}:{slot_id}:{target_date}:30m"

    else:
        raw_hash = hashlib.sha256(str(payload).encode("utf-8")).hexdigest()[:16]
        return f"notif:gen:{user_id}:{notification_type.value}:{raw_hash}"


async def check_user_notification_eligibility(
    db: AsyncSession,
    org_id: UUID,
    user_id: UUID,
    notification_type: NotificationType,
    channel: NotificationChannel,
    priority: NotificationPriority,
) -> Tuple[bool, Optional[str]]:
    """
    Check if user is eligible to receive this notification based on preferences and quiet hours.
    Returns (eligible: bool, suppression_reason: Optional[str]).
    """
    # 1. Critical priority notifications bypass quiet hours and opt-outs
    if priority == NotificationPriority.CRITICAL:
        return True, None

    # 2. Query user preferences
    stmt = select(NotificationPreference).where(
        NotificationPreference.org_id == org_id,
        NotificationPreference.user_id == user_id,
        NotificationPreference.notification_type == notification_type,
        NotificationPreference.channel == channel,
    )
    res = await db.execute(stmt)
    pref = res.scalars().first()

    if pref and not pref.enabled:
        return False, f"User disabled {notification_type.value} on {channel.value}"

    # 3. Check quiet hours (unless priority is HIGH or CRITICAL)
    if priority != NotificationPriority.HIGH and pref and pref.quiet_hours_start and pref.quiet_hours_end:
        try:
            user_tz = ZoneInfo(pref.timezone or "Asia/Kolkata")
        except Exception:
            user_tz = timezone.utc
        now_local = datetime.now(user_tz).time()

        if is_in_quiet_hours(now_local, pref.quiet_hours_start, pref.quiet_hours_end):
            return False, f"Suppressed during user quiet hours ({pref.quiet_hours_start} - {pref.quiet_hours_end})"

    return True, None
