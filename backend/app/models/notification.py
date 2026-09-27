import enum
import uuid
from datetime import datetime, time, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    Time,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base


class OutboxStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class NotificationType(str, enum.Enum):
    ATTENDANCE_BELOW_THRESHOLD = "ATTENDANCE_BELOW_THRESHOLD"
    COMMUTE_DELAY_RISK = "COMMUTE_DELAY_RISK"
    CLASS_STARTING_REMINDER = "CLASS_STARTING_REMINDER"
    SYSTEM_ALERT = "SYSTEM_ALERT"


class NotificationChannel(str, enum.Enum):
    EMAIL = "EMAIL"
    PUSH = "PUSH"
    SMS = "SMS"
    WHATSAPP = "WHATSAPP"
    IN_APP = "IN_APP"


class NotificationPriority(str, enum.Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class NotificationStatus(str, enum.Enum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    SENDING = "SENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    SUPPRESSED = "SUPPRESSED"


class DeliveryAttemptStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    ATTEMPTED = "ATTEMPTED"


class OutboxEvent(Base):
    """
    Transactional Outbox Table ensuring zero lost domain events.
    Events are committed in the same database transaction as domain state mutations.
    """
    __tablename__ = "outbox_events"

    id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    org_id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type = Column(String(100), nullable=False, index=True)
    event_version = Column(String(20), nullable=False, default="1.0")
    aggregate_type = Column(String(100), nullable=False)
    aggregate_id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        nullable=False,
        index=True,
    )
    payload = Column(JSON, nullable=False)
    status = Column(
        Enum(OutboxStatus, native_enum=False, length=50),
        nullable=False,
        default=OutboxStatus.PENDING,
        index=True,
    )
    retry_count = Column(Integer, nullable=False, default=0)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    processed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    organization = relationship("Organization")

    __table_args__ = (
        Index("ix_outbox_status_created", "status", "created_at"),
    )


class Notification(Base):
    """
    Canonical notification record tracking delivery status, deduplication, and scheduling.
    """
    __tablename__ = "notifications"

    id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    org_id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        ForeignKey("outbox_events.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    type = Column(
        Enum(NotificationType, native_enum=False, length=50),
        nullable=False,
        index=True,
    )
    channel = Column(
        Enum(NotificationChannel, native_enum=False, length=50),
        nullable=False,
        default=NotificationChannel.EMAIL,
    )
    priority = Column(
        Enum(NotificationPriority, native_enum=False, length=50),
        nullable=False,
        default=NotificationPriority.NORMAL,
    )
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    html_body = Column(Text, nullable=True)
    deduplication_key = Column(String(255), nullable=False, index=True)
    status = Column(
        Enum(NotificationStatus, native_enum=False, length=50),
        nullable=False,
        default=NotificationStatus.PENDING,
        index=True,
    )
    scheduled_for = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    expires_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    suppressed_reason = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    organization = relationship("Organization", foreign_keys=[org_id])
    deliveries = relationship("NotificationDelivery", back_populates="notification", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("org_id", "deduplication_key", name="uq_notification_org_dedup"),
        Index("ix_notifications_user_created", "user_id", "created_at"),
        Index("ix_notifications_status_scheduled", "status", "scheduled_for"),
    )


class NotificationDelivery(Base):
    """
    Detailed audit and diagnostic record for each individual delivery attempt to a provider.
    """
    __tablename__ = "notification_deliveries"

    id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    notification_id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        ForeignKey("notifications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider = Column(String(50), nullable=False)
    provider_message_id = Column(String(255), nullable=True)
    status = Column(
        Enum(DeliveryAttemptStatus, native_enum=False, length=50),
        nullable=False,
        default=DeliveryAttemptStatus.ATTEMPTED,
    )
    attempt_number = Column(Integer, nullable=False, default=1)
    latency_ms = Column(Float, nullable=False, default=0.0)
    error_code = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    attempted_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    notification = relationship("Notification", back_populates="deliveries")

    __table_args__ = (
        Index("ix_deliveries_notification_attempt", "notification_id", "attempt_number"),
    )


class NotificationPreference(Base):
    """
    Per-user notification channel preferences and quiet-hours configuration.
    """
    __tablename__ = "notification_preferences"

    id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    org_id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    notification_type = Column(
        Enum(NotificationType, native_enum=False, length=50),
        nullable=False,
    )
    channel = Column(
        Enum(NotificationChannel, native_enum=False, length=50),
        nullable=False,
        default=NotificationChannel.EMAIL,
    )
    enabled = Column(Boolean, nullable=False, default=True)
    quiet_hours_start = Column(Time, nullable=True)
    quiet_hours_end = Column(Time, nullable=True)
    timezone = Column(String(50), nullable=False, default="Asia/Kolkata")
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    organization = relationship("Organization", foreign_keys=[org_id])

    __table_args__ = (
        UniqueConstraint("org_id", "user_id", "notification_type", "channel", name="uq_user_notif_pref"),
        Index("ix_preferences_user_type", "user_id", "notification_type"),
    )
