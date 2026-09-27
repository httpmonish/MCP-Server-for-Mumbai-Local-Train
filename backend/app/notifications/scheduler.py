from datetime import date, datetime, time, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.logger import get_logger
from ..models.notification import NotificationType
from ..models.schedule import (
    ExceptionType,
    Schedule,
    ScheduleSlot,
    UserScheduleAssignment,
)
from .outbox import OutboxService

logger = get_logger("notifications.scheduler")


class ReminderSchedulerService:
    @staticmethod
    async def scan_and_generate_class_reminders(
        db: AsyncSession,
        lookahead_minutes: int = 35,
        target_date: Optional[date] = None,
        target_time: Optional[time] = None,
    ) -> int:
        """
        Scan active schedule assignments for today, identify classes starting within
        ~30 minutes, verify they are not canceled, and emit Outbox events.
        """
        tz_str = "Asia/Kolkata"
        try:
            user_tz = ZoneInfo(tz_str)
        except Exception:
            user_tz = timezone.utc

        now_in_tz = datetime.now(user_tz)
        today_date = target_date or now_in_tz.date()
        current_time = target_time or now_in_tz.time()
        today_weekday = today_date.weekday()

        # Calculate reminder window: current_time + 20 mins to current_time + lookahead_minutes
        now_dt = datetime.combine(today_date, current_time)
        window_start_dt = now_dt + timedelta(minutes=20)
        window_end_dt = now_dt + timedelta(minutes=lookahead_minutes)

        window_start_time = window_start_dt.time()
        window_end_time = window_end_dt.time()

        # 1. Fetch active assignments with schedules, slots, and exceptions
        stmt = (
            select(UserScheduleAssignment)
            .options(
                selectinload(UserScheduleAssignment.schedule)
                .selectinload(Schedule.slots)
                .selectinload(ScheduleSlot.location),
                selectinload(UserScheduleAssignment.schedule).selectinload(Schedule.exceptions),
            )
            .where(
                UserScheduleAssignment.is_active.is_(True),
                UserScheduleAssignment.valid_from <= today_date,
                or_(
                    UserScheduleAssignment.valid_until.is_(None),
                    UserScheduleAssignment.valid_until >= today_date,
                ),
            )
        )
        res = await db.execute(stmt)
        assignments = list(res.scalars().all())

        reminders_emitted = 0

        for assign in assignments:
            schedule = assign.schedule
            if not schedule or not schedule.is_active:
                continue

            # Check if there is an exception for today
            exception = next(
                (
                    e
                    for e in schedule.exceptions
                    if e.exception_date == today_date and e.exception_type == ExceptionType.CANCELLED
                ),
                None,
            )
            if exception:
                continue  # Class canceled for today, suppress reminder

            for slot in schedule.slots:
                if slot.day_of_week != today_weekday:
                    continue

                # Check if slot start_time falls in upcoming reminder window
                if window_start_time <= slot.start_time <= window_end_time:
                    loc = slot.location
                    payload = {
                        "user_id": str(assign.user_id),
                        "org_id": str(assign.org_id),
                        "slot_id": str(slot.id),
                        "slot_title": slot.title,
                        "schedule_title": schedule.title,
                        "start_time": slot.start_time.strftime("%H:%M:%S"),
                        "location_name": loc.name if loc else "Main Campus",
                        "station_code": loc.nearest_station_code if loc else None,
                        "target_date": str(today_date),
                        "minutes_before": 30,
                    }

                    await OutboxService.record_event(
                        db=db,
                        org_id=assign.org_id,
                        event_type=NotificationType.CLASS_STARTING_REMINDER.value,
                        aggregate_type="SCHEDULE_SLOT",
                        aggregate_id=slot.id,
                        payload=payload,
                    )
                    reminders_emitted += 1

        if reminders_emitted > 0:
            await db.commit()

        return reminders_emitted
