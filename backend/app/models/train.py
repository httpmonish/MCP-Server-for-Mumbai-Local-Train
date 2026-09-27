import uuid

from sqlalchemy import JSON, Boolean, Column, String, Time, UniqueConstraint, Uuid
from sqlalchemy.dialects.postgresql import JSONB, UUID

from .base import Base


class TrainSchedule(Base):
    __tablename__ = "train_schedules"

    id = Column(Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"), primary_key=True, default=uuid.uuid4)
    line = Column(String(10), nullable=False, index=True)  # "CR" or "WR"
    train_number = Column(String(20), nullable=False, index=True)
    train_type = Column(String(10), nullable=False)  # "SLOW" or "FAST"
    source_station = Column(String(50), nullable=False, index=True)
    destination_station = Column(String(50), nullable=False, index=True)
    departure_time = Column(Time, nullable=False, index=True)
    arrival_time = Column(Time, nullable=False)
    is_sunday_run = Column(Boolean, default=True)
    stops_data = Column(JSON().with_variant(JSONB, "postgresql"), nullable=False)

    __table_args__ = (UniqueConstraint("line", "train_number", "departure_time", name="uq_line_train_departure"),)
