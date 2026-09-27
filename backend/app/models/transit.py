import enum
import uuid
from datetime import datetime, timezone
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
    String,
    Time,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class LineCode(str, enum.Enum):
    CR = "CR"  # Central Railway
    WR = "WR"  # Western Railway
    HR = "HR"  # Harbour Railway


class TransitDataSourceType(str, enum.Enum):
    OFFICIAL = "OFFICIAL"
    LICENSED_THIRD_PARTY = "LICENSED_THIRD_PARTY"
    CROWDSOURCED = "CROWDSOURCED"
    INTERNAL = "INTERNAL"
    SIMULATED_TEST = "SIMULATED_TEST"


class DataFreshness(str, enum.Enum):
    FRESH = "FRESH"
    STALE = "STALE"
    EXPIRED = "EXPIRED"


class DataConfidence(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class OperationalStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    AT_STATION = "AT_STATION"
    DEPARTED = "DEPARTED"
    DELAYED = "DELAYED"
    CANCELLED = "CANCELLED"
    TERMINATED = "TERMINATED"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"


class Station(Base):
    __tablename__ = "stations"

    id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    code = Column(String(10), nullable=False, unique=True, index=True)
    name = Column(String(100), nullable=False)
    canonical_name = Column(String(100), nullable=False, index=True)
    line = Column(String(10), nullable=False, index=True)  # CR, WR, HR
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    sequence_order = Column(Integer, nullable=False, default=1, index=True)
    is_fast_stop = Column(Boolean, default=False, nullable=False)
    is_interchange = Column(Boolean, default=False, nullable=False)
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
        Index("ix_stations_line_seq", "line", "sequence_order"),
    )

    def __repr__(self) -> str:
        return f"<Station(code='{self.code}', name='{self.name}', line='{self.line}')>"


class TransitLine(Base):
    __tablename__ = "transit_lines"

    id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        primary_key=True,
        default=uuid.uuid4,
    )
    code = Column(String(10), nullable=False, unique=True, index=True)
    name = Column(String(100), nullable=False)
    color = Column(String(20), nullable=False)
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class RailwaySegment(Base):
    __tablename__ = "railway_segments"

    id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        primary_key=True,
        default=uuid.uuid4,
    )
    line_code = Column(String(10), nullable=False, index=True)
    from_station_code = Column(String(10), nullable=False, index=True)
    to_station_code = Column(String(10), nullable=False, index=True)
    sequence_order = Column(Integer, nullable=False, default=1)
    distance_km = Column(Float, nullable=True)
    avg_travel_seconds = Column(Integer, nullable=True)


class TransitDataSource(Base):
    __tablename__ = "transit_data_sources"

    id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        primary_key=True,
        default=uuid.uuid4,
    )
    name = Column(String(100), nullable=False, unique=True)
    provider_type = Column(
        Enum(TransitDataSourceType, native_enum=False, length=50),
        nullable=False,
        default=TransitDataSourceType.INTERNAL,
    )
    base_url = Column(String(255), nullable=True)
    status = Column(String(50), default="ACTIVE", nullable=False)
    license_type = Column(String(100), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class LiveTrainState(Base):
    __tablename__ = "live_train_states"

    id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    train_number = Column(String(20), nullable=False, index=True)
    line = Column(String(10), nullable=False, index=True)
    status = Column(
        Enum(OperationalStatus, native_enum=False, length=50),
        nullable=False,
        default=OperationalStatus.RUNNING,
    )
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    speed_kmh = Column(Float, nullable=True)
    bearing = Column(Float, nullable=True)
    current_station_code = Column(String(10), nullable=True, index=True)
    next_station_code = Column(String(10), nullable=True, index=True)
    delay_minutes = Column(Integer, default=0, nullable=False)
    source_type = Column(
        Enum(TransitDataSourceType, native_enum=False, length=50),
        nullable=False,
        default=TransitDataSourceType.INTERNAL,
    )
    freshness = Column(
        Enum(DataFreshness, native_enum=False, length=50),
        nullable=False,
        default=DataFreshness.FRESH,
    )
    confidence = Column(
        Enum(DataConfidence, native_enum=False, length=50),
        nullable=False,
        default=DataConfidence.HIGH,
    )
    observed_at = Column(DateTime(timezone=True), nullable=False)
    received_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_live_train_lookup", "train_number", "observed_at"),
    )
