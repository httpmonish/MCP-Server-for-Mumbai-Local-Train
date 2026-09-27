import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Uuid
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class TrainDelayReport(Base):
    __tablename__ = "train_delay_reports"

    id = Column(Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"), primary_key=True, default=uuid.uuid4)
    train_number = Column(String(20), nullable=False, index=True)
    station_code = Column(String(10), nullable=False, index=True)
    reported_delay_minutes = Column(Integer, nullable=False)
    reporter_id_hash = Column(String(64), nullable=False)
    confidence_score = Column(Float, default=1.0)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    is_active = Column(Boolean, default=True)
