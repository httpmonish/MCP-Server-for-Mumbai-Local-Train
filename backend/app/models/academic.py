import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, UniqueConstraint, Uuid
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class LegacyAcademicAttendance(Base):
    __tablename__ = "legacy_academic_attendance"

    id = Column(Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"), primary_key=True, default=uuid.uuid4)
    student_id = Column(String(50), nullable=False, index=True)
    subject_name = Column(String(120), nullable=False)
    total_conducted = Column(Integer, default=0)
    total_attended = Column(Integer, default=0)
    percentage = Column(Float, default=0.0)
    last_synced_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (UniqueConstraint("student_id", "subject_name", name="uq_legacy_attendance_student_subject"),)


class ExamTimetable(Base):
    __tablename__ = "exam_timetables"

    id = Column(Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"), primary_key=True, default=uuid.uuid4)
    student_id = Column(String(50), nullable=False, index=True)
    subject_name = Column(String(120), nullable=False)
    exam_date = Column(String(50), nullable=False)
    time_slot = Column(String(50), nullable=False)
    classroom = Column(String(50), nullable=True)
    last_synced_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (UniqueConstraint("student_id", "subject_name", "exam_date", name="uq_exam_student_subject_date"),)
