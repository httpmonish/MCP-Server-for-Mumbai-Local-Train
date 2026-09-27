import enum
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base


class AttendanceStatus(str, enum.Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"
    EXCUSED = "EXCUSED"
    CANCELLED = "CANCELLED"
    HOLIDAY = "HOLIDAY"
    NOT_REQUIRED = "NOT_REQUIRED"


class AttendanceSource(str, enum.Enum):
    MANUAL = "MANUAL"
    SELF_CHECKIN = "SELF_CHECKIN"
    QR = "QR"
    BIOMETRIC = "BIOMETRIC"
    IMPORT = "IMPORT"
    SYSTEM = "SYSTEM"


class PolicyAppliesTo(str, enum.Enum):
    STUDENT = "STUDENT"
    EMPLOYEE = "EMPLOYEE"
    ALL = "ALL"


class AttendanceRiskStatus(str, enum.Enum):
    ABOVE_THRESHOLD = "ABOVE_THRESHOLD"
    NEAR_THRESHOLD = "NEAR_THRESHOLD"
    BELOW_THRESHOLD = "BELOW_THRESHOLD"


class AttendancePolicy(Base):
    __tablename__ = "attendance_policies"

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
    name = Column(String(100), nullable=False)
    applies_to = Column(
        Enum(PolicyAppliesTo, native_enum=False, length=50),
        nullable=False,
        default=PolicyAppliesTo.ALL,
    )
    min_percentage = Column(Float, nullable=False, default=75.0)
    late_penalty_multiplier = Column(Float, nullable=False, default=1.0)  # 1.0 = counts full, 0.5 = half credit
    count_excused_in_denominator = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    valid_from = Column(Date, nullable=True)
    valid_until = Column(Date, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_attendance_policies_org_applies", "org_id", "applies_to", "is_active"),
    )


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

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
    schedule_slot_id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        ForeignKey("schedule_slots.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    date = Column(Date, nullable=False, index=True)
    status = Column(
        Enum(AttendanceStatus, native_enum=False, length=50),
        nullable=False,
        default=AttendanceStatus.PRESENT,
    )
    source = Column(
        Enum(AttendanceSource, native_enum=False, length=50),
        nullable=False,
        default=AttendanceSource.MANUAL,
    )
    check_in_time = Column(Time, nullable=True)
    check_out_time = Column(Time, nullable=True)
    marked_by_user_id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    remarks = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    marked_by = relationship("User", foreign_keys=[marked_by_user_id])
    schedule_slot = relationship("ScheduleSlot")
    audits = relationship("AttendanceAudit", back_populates="record", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("org_id", "user_id", "schedule_slot_id", "date", name="uq_attendance_user_slot_date"),
        Index("ix_attendance_org_user_date", "org_id", "user_id", "date"),
        Index("ix_attendance_slot_date", "schedule_slot_id", "date"),
        Index("ix_attendance_org_date", "org_id", "date"),
    )


class AttendanceAudit(Base):
    __tablename__ = "attendance_audit"

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
    record_id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        ForeignKey("attendance_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    changed_by_user_id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    old_status = Column(String(50), nullable=False)
    new_status = Column(String(50), nullable=False)
    reason = Column(String(500), nullable=False)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    record = relationship("AttendanceRecord", back_populates="audits")
    changed_by = relationship("User", foreign_keys=[changed_by_user_id])

    __table_args__ = (
        Index("ix_attendance_audit_record", "record_id"),
        Index("ix_attendance_audit_org", "org_id"),
    )
