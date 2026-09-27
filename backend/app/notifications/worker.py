import random
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.config import settings
from ..core.logger import get_logger
from ..models.auth import User
from ..models.notification import (
    DeliveryAttemptStatus,
    Notification,
    NotificationDelivery,
    NotificationStatus,
)
from .providers import get_email_provider

logger = get_logger("notifications.worker")


class NotificationDeliveryWorker:
    @staticmethod
    async def process_pending_notifications(
        db: AsyncSession,
        limit: int = 50,
    ) -> int:
        """
        Claim and deliver pending/retrying notifications using the configured provider.
        """
        now = datetime.now(timezone.utc)
        stmt = (
            select(Notification)
            .options(selectinload(Notification.user), selectinload(Notification.deliveries))
            .where(
                Notification.status.in_([NotificationStatus.PENDING, NotificationStatus.RETRYING]),
                Notification.scheduled_for <= now,
            )
            .order_by(Notification.scheduled_for.asc())
            .limit(limit)
        )
        res = await db.execute(stmt)
        notifications = list(res.scalars().all())

        delivered_count = 0
        provider = get_email_provider()

        for notif in notifications:
            # 1. Check expiration
            if notif.expires_at and notif.expires_at < now:
                notif.status = NotificationStatus.EXPIRED
                notif.suppressed_reason = "Notification expired before delivery."
                continue

            user = notif.user
            if not user or not user.is_active or not user.email:
                notif.status = NotificationStatus.FAILED
                notif.suppressed_reason = "Recipient user invalid or missing email."
                continue

            notif.status = NotificationStatus.SENDING
            await db.flush()

            attempt_number = len(notif.deliveries) + 1

            # 2. Execute delivery attempt
            result = await provider.send_email(
                to_email=user.email,
                subject=notif.title,
                text_content=notif.body,
                html_content=notif.html_body,
                metadata={"notification_id": str(notif.id), "attempt": attempt_number},
            )

            # 3. Record Delivery attempt record
            delivery_record = NotificationDelivery(
                id=uuid.uuid4(),
                notification_id=notif.id,
                provider=result.provider,
                provider_message_id=result.provider_message_id,
                status=DeliveryAttemptStatus.SUCCESS if result.success else DeliveryAttemptStatus.FAILURE,
                attempt_number=attempt_number,
                latency_ms=result.latency_ms,
                error_code=result.error_code,
                error_message=result.error_message,
                attempted_at=datetime.now(timezone.utc),
            )
            db.add(delivery_record)

            # 4. Handle result status
            if result.success:
                notif.status = NotificationStatus.SENT
                notif.sent_at = datetime.now(timezone.utc)
                delivered_count += 1
            else:
                max_retries = settings.NOTIFICATION_MAX_RETRIES
                if result.is_permanent_failure or attempt_number >= max_retries:
                    notif.status = NotificationStatus.FAILED
                    notif.suppressed_reason = result.error_message
                else:
                    notif.status = NotificationStatus.RETRYING
                    # Exponential backoff with jitter
                    base_delay = settings.NOTIFICATION_INITIAL_RETRY_DELAY_SEC
                    delay_seconds = base_delay * (2 ** (attempt_number - 1)) + random.uniform(0.5, 2.0)
                    notif.scheduled_for = datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)

        await db.commit()
        return delivered_count
