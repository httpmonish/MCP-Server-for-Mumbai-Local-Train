import enum
import uuid
from datetime import datetime, timezone

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
    Time,
    Uuid,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base


class ScheduleType(str, enum.Enum):
    CLASS = "CLASS"
    SHIFT = "SHIFT"
    EXAM = "EXAM"
    MEETING = "MEETING"
    OTHER = "OTHER"


class ExceptionType(str, enum.Enum):
    CANCELLED = "CANCELLED"
    RESCHEDULED = "RESCHEDULED"
    HOLIDAY = "HOLIDAY"


class Location(Base):
    __tablename__ = "locations"

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
    address = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    nearest_station_code = Column(String(10), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
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
        Index("ix_locations_org_active", "org_id", "is_active"),
    )


class Schedule(Base):
    __tablename__ = "schedules"

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
    title = Column(String(255), nullable=False)
    type = Column(
        Enum(ScheduleType, native_enum=False, length=50),
        nullable=False,
        default=ScheduleType.CLASS,
    )
    timezone = Column(String(50), nullable=False, default="Asia/Kolkata")
    description = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
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
    slots = relationship("ScheduleSlot", back_populates="schedule", cascade="all, delete-orphan")
    assignments = relationship("UserScheduleAssignment", back_populates="schedule", cascade="all, delete-orphan")
    exceptions = relationship("ScheduleException", back_populates="schedule", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_schedules_org_type", "org_id", "type"),
        Index("ix_schedules_org_active", "org_id", "is_active"),
    )


class ScheduleSlot(Base):
    __tablename__ = "schedule_slots"

    id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    schedule_id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        ForeignKey("schedules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    day_of_week = Column(Integer, nullable=False, index=True)  # 0=Monday, 6=Sunday
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    title = Column(String(255), nullable=False)
    location_id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        ForeignKey("locations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    location_name = Column(String(255), nullable=True)
    instructor_or_supervisor = Column(String(255), nullable=True)
    is_overnight = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    schedule = relationship("Schedule", back_populates="slots")
    location = relationship("Location")

    __table_args__ = (
        Index("ix_slots_schedule_day", "schedule_id", "day_of_week"),
    )


class UserScheduleAssignment(Base):
    __tablename__ = "user_schedule_assignments"

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
    schedule_id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        ForeignKey("schedules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    valid_from = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    schedule = relationship("Schedule", back_populates="assignments")
    user = relationship("User")

    __table_args__ = (
        Index("ix_assignments_user_dates", "user_id", "valid_from", "valid_until", "is_active"),
        Index("ix_assignments_org_user", "org_id", "user_id"),
    )


class ScheduleException(Base):
    __tablename__ = "schedule_exceptions"

    id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    schedule_id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        ForeignKey("schedules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    exception_date = Column(Date, nullable=False, index=True)
    exception_type = Column(
        Enum(ExceptionType, native_enum=False, length=50),
        nullable=False,
        default=ExceptionType.CANCELLED,
    )
    replacement_start_time = Column(Time, nullable=True)
    replacement_end_time = Column(Time, nullable=True)
    replacement_location_name = Column(String(255), nullable=True)
    reason = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    schedule = relationship("Schedule", back_populates="exceptions")

    __table_args__ = (
        Index("ix_exceptions_schedule_date", "schedule_id", "exception_date"),
    )
