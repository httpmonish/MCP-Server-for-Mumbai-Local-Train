from datetime import datetime

from sqlalchemy.dialects.postgresql import insert

from ..models.academic import AttendanceRecord, ExamTimetable


async def upsert_attendance(db_session, student_id: str, records: list[dict]) -> None:
    for record in records:
        stmt = insert(AttendanceRecord).values(
            student_id=student_id,
            **record,
            last_synced_at=datetime.utcnow()
        )

        # Define columns to update on conflict
        update_cols = {
            col.name: stmt.excluded[col.name]
            for col in AttendanceRecord.__table__.columns
            if col.name not in ['id', 'student_id']
        }

        stmt = stmt.on_conflict_do_update(
            constraint='uq_attendance_student_subject',
            set_=update_cols
        )
        await db_session.execute(stmt)
    await db_session.commit()

async def upsert_exams(db_session, student_id: str, exams: list[dict]) -> None:
    for exam in exams:
        stmt = insert(ExamTimetable).values(
            student_id=student_id,
            **exam,
            last_synced_at=datetime.utcnow()
        )

        # Define columns to update on conflict
        update_cols = {
            col.name: stmt.excluded[col.name]
            for col in ExamTimetable.__table__.columns
            if col.name not in ['id', 'student_id']
        }

        stmt = stmt.on_conflict_do_update(
            constraint='uq_exam_student_subject_date',
            set_=update_cols
        )
        await db_session.execute(stmt)
    await db_session.commit()
