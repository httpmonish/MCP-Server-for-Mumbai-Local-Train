import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.logger import get_logger
from ..models.auth import User
from ..models.notification import (
    Notification,
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
    NotificationType,
    OutboxEvent,
    OutboxStatus,
)
from .rules import check_user_notification_eligibility, compute_deduplication_key
from .templates import (
    render_attendance_alert,
    render_class_reminder,
    render_commute_risk_alert,
)

logger = get_logger("notifications.outbox")


class OutboxService:
    @staticmethod
    async def record_event(
        db: AsyncSession,
        org_id: UUID,
        event_type: str,
        aggregate_type: str,
        aggregate_id: UUID,
        payload: Dict[str, Any],
    ) -> OutboxEvent:
        """
        Record a domain event into the transactional outbox table.
        Must be invoked inside the same database transaction as the business state change.
        """
        event = OutboxEvent(
            id=uuid.uuid4(),
            org_id=org_id,
            event_type=event_type,
            event_version="1.0",
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            payload=payload,
            status=OutboxStatus.PENDING,
            created_at=datetime.now(timezone.utc),
        )
        db.add(event)
        return event

    @staticmethod
    async def dispatch_pending_events(
        db: AsyncSession,
        limit: int = 50,
    ) -> int:
        """
        Poll and process pending outbox events, creating corresponding Notification records.
        """
        stmt = (
            select(OutboxEvent)
            .where(OutboxEvent.status == OutboxStatus.PENDING)
            .order_by(OutboxEvent.created_at.asc())
            .limit(limit)
        )
        res = await db.execute(stmt)
        events = list(res.scalars().all())

        processed_count = 0
        for ev in events:
            try:
                ev.status = OutboxStatus.PROCESSING
                await db.flush()

                # Dispatch according to event_type
                await OutboxService._process_single_event(db, ev)
                ev.status = OutboxStatus.PROCESSED
                ev.processed_at = datetime.now(timezone.utc)
                processed_count += 1
            except Exception as e:
                logger.error(f"Error processing outbox event {ev.id}: {e}", exc_info=True)
                ev.status = OutboxStatus.FAILED
                ev.retry_count += 1
                ev.error_message = str(e)[:500]

        await db.commit()
        return processed_count

    @staticmethod
    async def _process_single_event(
        db: AsyncSession,
        ev: OutboxEvent,
    ) -> Optional[Notification]:
        payload = ev.payload or {}
        user_id_str = payload.get("user_id")
        if not user_id_str:
            return None

        user_id = UUID(str(user_id_str))
        user_res = await db.execute(select(User).where(User.id == user_id, User.org_id == ev.org_id))
        user = user_res.scalars().first()
        if not user or not user.is_active:
            return None

        # 1. Map event type to notification type & priority
        if ev.event_type == NotificationType.ATTENDANCE_BELOW_THRESHOLD.value:
            notif_type = NotificationType.ATTENDANCE_BELOW_THRESHOLD
            priority = NotificationPriority.HIGH
            title, plain_body, html_body = render_attendance_alert(payload)
        elif ev.event_type == NotificationType.COMMUTE_DELAY_RISK.value:
            notif_type = NotificationType.COMMUTE_DELAY_RISK
            priority = NotificationPriority.HIGH
            title, plain_body, html_body = render_commute_risk_alert(payload)
        elif ev.event_type == NotificationType.CLASS_STARTING_REMINDER.value:
            notif_type = NotificationType.CLASS_STARTING_REMINDER
            priority = NotificationPriority.NORMAL
            title, plain_body, html_body = render_class_reminder(payload)
        else:
            logger.warning(f"Unhandled outbox event_type: {ev.event_type}")
            return None

        channel = NotificationChannel.EMAIL
        dedup_key = compute_deduplication_key(notif_type, user_id, payload)

        # 2. Check if a notification with this deduplication key was already created
        existing_stmt = select(Notification).where(
            Notification.org_id == ev.org_id,
            Notification.deduplication_key == dedup_key,
        )
        existing_res = await db.execute(existing_stmt)
        if existing_res.scalars().first():
            logger.info(f"Duplicate notification suppressed by dedup_key: {dedup_key}")
            return None

        # 3. Check user preferences and quiet-hours eligibility
        eligible, suppression_reason = await check_user_notification_eligibility(
            db=db,
            org_id=ev.org_id,
            user_id=user_id,
            notification_type=notif_type,
            channel=channel,
            priority=priority,
        )

        initial_status = NotificationStatus.PENDING if eligible else NotificationStatus.SUPPRESSED

        # 4. Create Notification entity
        notification = Notification(
            id=uuid.uuid4(),
            org_id=ev.org_id,
            user_id=user_id,
            event_id=ev.id,
            type=notif_type,
            channel=channel,
            priority=priority,
            title=title,
            body=plain_body,
            html_body=html_body,
            deduplication_key=dedup_key,
            status=initial_status,
            suppressed_reason=suppression_reason,
            scheduled_for=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
        )
        db.add(notification)
        await db.flush()
        return notification
