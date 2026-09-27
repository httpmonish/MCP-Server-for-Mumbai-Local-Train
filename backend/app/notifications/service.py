import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.logger import get_logger
from ..models.notification import (
    Notification,
    NotificationPreference,
    NotificationType,
)
from ..schemas.notification import (
    NotificationListResponse,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
    NotificationResponse,
)
from .outbox import OutboxService
from .worker import NotificationDeliveryWorker

logger = get_logger("notifications.service")


class NotificationEngineService:
    @staticmethod
    async def trigger_attendance_below_threshold_event(
        db: AsyncSession,
        org_id: UUID,
        user_id: UUID,
        percentage: float,
        min_required: float,
        shortage_count: int,
        policy_name: Optional[str] = None,
    ) -> None:
        """
        Record attendance below threshold domain event into the transactional outbox.
        """
        payload = {
            "user_id": str(user_id),
            "org_id": str(org_id),
            "percentage": percentage,
            "min_required": min_required,
            "shortage_count": shortage_count,
            "policy_name": policy_name or "Statutory Attendance Policy",
            "occurred_at": datetime.now(timezone.utc).isoformat(),
        }
        await OutboxService.record_event(
            db=db,
            org_id=org_id,
            event_type=NotificationType.ATTENDANCE_BELOW_THRESHOLD.value,
            aggregate_type="ATTENDANCE",
            aggregate_id=user_id,
            payload=payload,
        )

    @staticmethod
    async def trigger_commute_delay_risk_event(
        db: AsyncSession,
        org_id: UUID,
        user_id: UUID,
        slot_id: UUID,
        slot_title: str,
        origin_station: str,
        destination_station: str,
        scheduled_start: str,
        estimated_arrival: str,
        arrival_margin_minutes: int,
        risk_status: str,
        train_number: Optional[str] = None,
        reason_codes: Optional[List[str]] = None,
    ) -> None:
        """
        Record commute delay risk domain event into the transactional outbox.
        """
        payload = {
            "user_id": str(user_id),
            "org_id": str(org_id),
            "slot_id": str(slot_id),
            "slot_title": slot_title,
            "origin_station": origin_station,
            "destination_station": destination_station,
            "scheduled_start": scheduled_start,
            "estimated_arrival": estimated_arrival,
            "arrival_margin_minutes": arrival_margin_minutes,
            "risk_status": risk_status,
            "train_number": train_number,
            "reason_codes": reason_codes or [],
            "occurred_at": datetime.now(timezone.utc).isoformat(),
        }
        await OutboxService.record_event(
            db=db,
            org_id=org_id,
            event_type=NotificationType.COMMUTE_DELAY_RISK.value,
            aggregate_type="COMMUTE",
            aggregate_id=slot_id,
            payload=payload,
        )

    @staticmethod
    async def get_user_notifications(
        db: AsyncSession,
        org_id: UUID,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> NotificationListResponse:
        """
        Retrieve paginated notification history for the authenticated user.
        Strictly tenant-scoped.
        """
        base_filters = [Notification.org_id == org_id, Notification.user_id == user_id]

        count_stmt = select(func.count(Notification.id)).where(*base_filters)
        total_res = await db.execute(count_stmt)
        total = total_res.scalar_one() or 0

        unread_stmt = select(func.count(Notification.id)).where(
            *base_filters,
            Notification.read_at.is_(None),
        )
        unread_res = await db.execute(unread_stmt)
        unread_count = unread_res.scalar_one() or 0

        stmt = (
            select(Notification)
            .where(*base_filters)
            .order_by(desc(Notification.created_at))
            .limit(limit)
            .offset(offset)
        )
        res = await db.execute(stmt)
        items = list(res.scalars().all())

        return NotificationListResponse(
            items=[NotificationResponse.model_validate(n) for n in items],
            total=total,
            unread_count=unread_count,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    async def get_user_preferences(
        db: AsyncSession,
        org_id: UUID,
        user_id: UUID,
    ) -> List[NotificationPreferenceResponse]:
        """
        Retrieve user's notification preferences.
        """
        stmt = (
            select(NotificationPreference)
            .where(NotificationPreference.org_id == org_id, NotificationPreference.user_id == user_id)
            .order_by(NotificationPreference.notification_type.asc())
        )
        res = await db.execute(stmt)
        prefs = list(res.scalars().all())
        return [NotificationPreferenceResponse.model_validate(p) for p in prefs]

    @staticmethod
    async def update_user_preference(
        db: AsyncSession,
        org_id: UUID,
        user_id: UUID,
        update_in: NotificationPreferenceUpdate,
    ) -> NotificationPreferenceResponse:
        """
        Update or create user's notification preference.
        """
        stmt = select(NotificationPreference).where(
            NotificationPreference.org_id == org_id,
            NotificationPreference.user_id == user_id,
            NotificationPreference.notification_type == update_in.notification_type,
            NotificationPreference.channel == update_in.channel,
        )
        res = await db.execute(stmt)
        pref = res.scalars().first()

        if not pref:
            pref = NotificationPreference(
                id=uuid.uuid4(),
                org_id=org_id,
                user_id=user_id,
                notification_type=update_in.notification_type,
                channel=update_in.channel,
                enabled=update_in.enabled,
                quiet_hours_start=update_in.quiet_hours_start,
                quiet_hours_end=update_in.quiet_hours_end,
                timezone=update_in.timezone or "Asia/Kolkata",
            )
            db.add(pref)
        else:
            pref.enabled = update_in.enabled
            pref.quiet_hours_start = update_in.quiet_hours_start
            pref.quiet_hours_end = update_in.quiet_hours_end
            if update_in.timezone:
                pref.timezone = update_in.timezone

        await db.commit()
        await db.refresh(pref)
        return NotificationPreferenceResponse.model_validate(pref)

    @staticmethod
    async def process_outbox_and_deliver(
        db: AsyncSession,
        limit: int = 50,
    ) -> Tuple[int, int]:
        """
        Run a full pipeline cycle: dispatch outbox events -> deliver notifications.
        Returns (dispatched_events_count, delivered_notifications_count).
        """
        dispatched = await OutboxService.dispatch_pending_events(db, limit=limit)
        delivered = await NotificationDeliveryWorker.process_pending_notifications(db, limit=limit)
        return dispatched, delivered
