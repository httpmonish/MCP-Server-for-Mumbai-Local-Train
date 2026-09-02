import uuid

from sqlalchemy import Boolean, Column, String, Time, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID

from .academic import Base


class TrainSchedule(Base):
    __tablename__ = "train_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    line = Column(String(10), nullable=False, index=True)  # "CR" or "WR"
    train_number = Column(String(20), nullable=False, index=True)
    train_type = Column(String(10), nullable=False)  # "SLOW" or "FAST"
    source_station = Column(String(50), nullable=False, index=True)
    destination_station = Column(String(50), nullable=False, index=True)
    departure_time = Column(Time, nullable=False, index=True)
    arrival_time = Column(Time, nullable=False)
    is_sunday_run = Column(Boolean, default=True)
    stops_data = Column(JSONB, nullable=False)

    __table_args__ = (
        UniqueConstraint("line", "train_number", "departure_time", name="uq_line_train_departure"),
    )
