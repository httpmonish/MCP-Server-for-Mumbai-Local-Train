import uuid
from datetime import date, datetime, time, timedelta, timezone
from typing import List, Optional
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.logger import get_logger
from ..models.auth import User
from ..models.schedule import (
    ExceptionType,
    Location,
    Schedule,
    ScheduleSlot,
    ScheduleType,
    UserScheduleAssignment,
)
from ..schemas.schedules import (
    DaySchedule,
    LocationCreateRequest,
    ScheduleAssignRequest,
    ScheduleCreateRequest,
    ScheduleOccurrence,
    ScheduleUpdateRequest,
    TodayScheduleResponse,
    WeekScheduleResponse,
)

logger = get_logger(__name__)


def parse_time_str(t_str: str) -> time:
    """Parse time string in HH:MM or HH:MM:SS format."""
    parts = t_str.strip().split(":")
    if len(parts) == 2:
        return time(int(parts[0]), int(parts[1]))
    elif len(parts) == 3:
        return time(int(parts[0]), int(parts[1]), int(parts[2]))
    raise ValueError(f"Invalid time format: '{t_str}'. Expected HH:MM or HH:MM:SS.")


class ScheduleEngineService:
    # -------------------------------------------------------------
    # Location Management
    # -------------------------------------------------------------
    @staticmethod
    async def create_location(
        db: AsyncSession,
        org_id: uuid.UUID,
        req: LocationCreateRequest,
    ) -> Location:
        loc = Location(
            id=uuid.uuid4(),
            org_id=org_id,
            name=req.name,
            address=req.address,
            latitude=req.latitude,
            longitude=req.longitude,
            nearest_station_code=req.nearest_station_code.upper() if req.nearest_station_code else None,
            is_active=True,
        )
        db.add(loc)
        await db.commit()
        await db.refresh(loc)
        return loc

    @staticmethod
    async def list_locations(
        db: AsyncSession,
        org_id: uuid.UUID,
    ) -> List[Location]:
        stmt = (
            select(Location)
            .where(Location.org_id == org_id, Location.is_active.is_(True))
            .order_by(Location.name.asc())
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

    # -------------------------------------------------------------
    # Schedule CRUD
    # -------------------------------------------------------------
    @staticmethod
    async def create_schedule(
        db: AsyncSession,
        org_id: uuid.UUID,
        req: ScheduleCreateRequest,
    ) -> Schedule:
        """Create a new schedule with initial recurring slots."""
        # 1. Create schedule definition
        schedule = Schedule(
            id=uuid.uuid4(),
            org_id=org_id,
            title=req.title,
            type=req.type,
            timezone=req.timezone,
            description=req.description,
            is_active=True,
        )
        db.add(schedule)

        # 2. Add slots if provided
        for s in req.slots:
            t_start = parse_time_str(s.start_time)
            t_end = parse_time_str(s.end_time)
            is_overnight = t_end < t_start

            # Validate location ownership if location_id supplied
            if s.location_id:
                stmt_loc = select(Location).where(Location.id == s.location_id, Location.org_id == org_id)
                res_loc = await db.execute(stmt_loc)
                if not res_loc.scalars().first():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Location {s.location_id} does not belong to your organization.",
                    )

            slot = ScheduleSlot(
                id=uuid.uuid4(),
                schedule_id=schedule.id,
                day_of_week=s.day_of_week,
                start_time=t_start,
                end_time=t_end,
                title=s.title,
                location_id=s.location_id,
                location_name=s.location_name,
                instructor_or_supervisor=s.instructor_or_supervisor,
                is_overnight=is_overnight,
            )
            db.add(slot)

        await db.commit()
        await db.refresh(schedule)

        # Reload with slots and location relationship
        stmt_reload = (
            select(Schedule)
            .options(selectinload(Schedule.slots).selectinload(ScheduleSlot.location))
            .where(Schedule.id == schedule.id)
        )
        res_reload = await db.execute(stmt_reload)
        return res_reload.scalars().first()

    @staticmethod
    async def get_schedule_by_id(
        db: AsyncSession,
        org_id: uuid.UUID,
        schedule_id: uuid.UUID,
    ) -> Schedule:
        """Fetch schedule strictly scoped to tenant."""
        stmt = (
            select(Schedule)
            .options(selectinload(Schedule.slots).selectinload(ScheduleSlot.location))
            .where(Schedule.id == schedule_id, Schedule.org_id == org_id)
        )
        res = await db.execute(stmt)
        schedule = res.scalars().first()
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found in your organization.",
            )
        return schedule

    @staticmethod
    async def list_schedules(
        db: AsyncSession,
        org_id: uuid.UUID,
        type: Optional[ScheduleType] = None,
    ) -> List[Schedule]:
        stmt = (
            select(Schedule)
            .options(selectinload(Schedule.slots))
            .where(Schedule.org_id == org_id, Schedule.is_active.is_(True))
        )
        if type:
            stmt = stmt.where(Schedule.type == type)
        stmt = stmt.order_by(Schedule.created_at.desc())
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def update_schedule(
        db: AsyncSession,
        org_id: uuid.UUID,
        schedule_id: uuid.UUID,
        req: ScheduleUpdateRequest,
    ) -> Schedule:
        schedule = await ScheduleEngineService.get_schedule_by_id(db=db, org_id=org_id, schedule_id=schedule_id)

        if req.title is not None:
            schedule.title = req.title
        if req.description is not None:
            schedule.description = req.description
        if req.timezone is not None:
            schedule.timezone = req.timezone
        if req.is_active is not None:
            schedule.is_active = req.is_active

        # Replace slots if provided
        if req.slots is not None:
            # Remove existing slots
            for existing_slot in schedule.slots:
                await db.delete(existing_slot)

            for s in req.slots:
                t_start = parse_time_str(s.start_time)
                t_end = parse_time_str(s.end_time)
                is_overnight = t_end < t_start

                slot = ScheduleSlot(
                    id=uuid.uuid4(),
                    schedule_id=schedule.id,
                    day_of_week=s.day_of_week,
                    start_time=t_start,
                    end_time=t_end,
                    title=s.title,
                    location_id=s.location_id,
                    location_name=s.location_name,
                    instructor_or_supervisor=s.instructor_or_supervisor,
                    is_overnight=is_overnight,
                )
                db.add(slot)

        await db.commit()
        return await ScheduleEngineService.get_schedule_by_id(db=db, org_id=org_id, schedule_id=schedule_id)

    @staticmethod
    async def delete_schedule(
        db: AsyncSession,
        org_id: uuid.UUID,
        schedule_id: uuid.UUID,
    ) -> None:
        schedule = await ScheduleEngineService.get_schedule_by_id(db=db, org_id=org_id, schedule_id=schedule_id)
        await db.delete(schedule)
        await db.commit()

    # -------------------------------------------------------------
    # Schedule Assignment
    # -------------------------------------------------------------
    @staticmethod
    async def assign_schedule(
        db: AsyncSession,
        org_id: uuid.UUID,
        schedule_id: uuid.UUID,
        req: ScheduleAssignRequest,
    ) -> List[UserScheduleAssignment]:
        # 1. Verify schedule belongs to org
        schedule = await ScheduleEngineService.get_schedule_by_id(db=db, org_id=org_id, schedule_id=schedule_id)

        # 2. Verify all users belong to org
        stmt_users = select(User.id).where(User.id.in_(req.user_ids), User.org_id == org_id)
        res_users = await db.execute(stmt_users)
        valid_user_ids = set(res_users.scalars().all())

        if len(valid_user_ids) != len(req.user_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more target users do not belong to your organization.",
            )

        assignments: List[UserScheduleAssignment] = []
        for uid in req.user_ids:
            assignment = UserScheduleAssignment(
                id=uuid.uuid4(),
                org_id=org_id,
                user_id=uid,
                schedule_id=schedule.id,
                valid_from=req.valid_from,
                valid_until=req.valid_until,
                is_active=True,
            )
            db.add(assignment)
            assignments.append(assignment)

        await db.commit()
        for a in assignments:
            await db.refresh(a)

        return assignments

    # -------------------------------------------------------------
    # User Today & Week Occurrence Queries
    # -------------------------------------------------------------
    @staticmethod
    async def get_user_today_schedule(
        db: AsyncSession,
        user: User,
        target_date: Optional[date] = None,
    ) -> TodayScheduleResponse:
        """
        Calculate today's schedule occurrences for the authenticated user.
        Determines current date in organization timezone, evaluates active assignments,
        matches day_of_week slots, and applies exceptions.
        """
        tz_str = "Asia/Kolkata"
        try:
            user_tz = ZoneInfo(tz_str)
        except Exception:
            user_tz = timezone.utc

        now_in_tz = datetime.now(user_tz)
        today_date = target_date or now_in_tz.date()
        today_weekday = today_date.weekday()  # 0=Monday, 6=Sunday
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        # 1. Query active assignments for today
        stmt = (
            select(UserScheduleAssignment)
            .options(
                selectinload(UserScheduleAssignment.schedule)
                .selectinload(Schedule.slots)
                .selectinload(ScheduleSlot.location),
                selectinload(UserScheduleAssignment.schedule).selectinload(Schedule.exceptions),
            )
            .where(
                UserScheduleAssignment.user_id == user.id,
                UserScheduleAssignment.org_id == user.org_id,
                UserScheduleAssignment.is_active.is_(True),
                UserScheduleAssignment.valid_from <= today_date,
                or_(
                    UserScheduleAssignment.valid_until.is_(None),
                    UserScheduleAssignment.valid_until >= today_date,
                ),
            )
        )
        res = await db.execute(stmt)
        assignments = res.scalars().all()

        occurrences: List[ScheduleOccurrence] = []

        for assignment in assignments:
            sched = assignment.schedule
            if not sched or not sched.is_active:
                continue

            # Check if today has a schedule exception (e.g. Holiday or Cancelled)
            exception = next((e for e in sched.exceptions if e.exception_date == today_date), None)
            if exception and exception.exception_type == ExceptionType.HOLIDAY:
                continue  # Entire day holiday

            for slot in sched.slots:
                if slot.day_of_week == today_weekday:
                    # Check slot exception
                    is_exc = bool(exception)
                    exc_reason = exception.reason if exception else None

                    nearest_station = slot.location.nearest_station_code if slot.location else None
                    loc_name = slot.location.name if slot.location else slot.location_name

                    occurrences.append(
                        ScheduleOccurrence(
                            slot_id=slot.id,
                            schedule_id=sched.id,
                            schedule_title=sched.title,
                            schedule_type=sched.type,
                            title=slot.title,
                            start_time=slot.start_time.strftime("%H:%M:%S"),
                            end_time=slot.end_time.strftime("%H:%M:%S"),
                            is_overnight=slot.is_overnight,
                            location_id=slot.location_id,
                            location_name=loc_name,
                            nearest_station_code=nearest_station,
                            instructor_or_supervisor=slot.instructor_or_supervisor,
                            is_exception=is_exc,
                            exception_reason=exc_reason,
                        )
                    )

        # Sort occurrences chronologically
        occurrences.sort(key=lambda o: o.start_time)

        return TodayScheduleResponse(
            user_id=user.id,
            date=today_date,
            day_name=day_names[today_weekday],
            timezone=tz_str,
            count=len(occurrences),
            items=occurrences,
        )

    @staticmethod
    async def get_user_week_schedule(
        db: AsyncSession,
        user: User,
        query_date: Optional[date] = None,
    ) -> WeekScheduleResponse:
        """
        Calculate full 7-day week schedule for the user without N+1 queries.
        """
        tz_str = "Asia/Kolkata"
        try:
            user_tz = ZoneInfo(tz_str)
        except Exception:
            user_tz = timezone.utc

        target_date = query_date or datetime.now(user_tz).date()
        # Monday of target week
        week_start = target_date - timedelta(days=target_date.weekday())
        week_end = week_start + timedelta(days=6)
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        # Single eager-loaded query across the week bounds
        stmt = (
            select(UserScheduleAssignment)
            .options(
                selectinload(UserScheduleAssignment.schedule)
                .selectinload(Schedule.slots)
                .selectinload(ScheduleSlot.location),
                selectinload(UserScheduleAssignment.schedule).selectinload(Schedule.exceptions),
            )
            .where(
                UserScheduleAssignment.user_id == user.id,
                UserScheduleAssignment.org_id == user.org_id,
                UserScheduleAssignment.is_active.is_(True),
                UserScheduleAssignment.valid_from <= week_end,
                or_(
                    UserScheduleAssignment.valid_until.is_(None),
                    UserScheduleAssignment.valid_until >= week_start,
                ),
            )
        )
        res = await db.execute(stmt)
        assignments = res.scalars().all()

        days_list: List[DaySchedule] = []
        total_count = 0

        for day_offset in range(7):
            curr_date = week_start + timedelta(days=day_offset)
            curr_weekday = curr_date.weekday()
            day_occurrences: List[ScheduleOccurrence] = []

            for assignment in assignments:
                sched = assignment.schedule
                if not sched or not sched.is_active:
                    continue

                # Check assignment valid on this specific day
                if assignment.valid_from > curr_date:
                    continue
                if assignment.valid_until and assignment.valid_until < curr_date:
                    continue

                # Exception check
                exception = next((e for e in sched.exceptions if e.exception_date == curr_date), None)
                if exception and exception.exception_type == ExceptionType.HOLIDAY:
                    continue

                for slot in sched.slots:
                    if slot.day_of_week == curr_weekday:
                        nearest_station = slot.location.nearest_station_code if slot.location else None
                        loc_name = slot.location.name if slot.location else slot.location_name

                        day_occurrences.append(
                            ScheduleOccurrence(
                                slot_id=slot.id,
                                schedule_id=sched.id,
                                schedule_title=sched.title,
                                schedule_type=sched.type,
                                title=slot.title,
                                start_time=slot.start_time.strftime("%H:%M:%S"),
                                end_time=slot.end_time.strftime("%H:%M:%S"),
                                is_overnight=slot.is_overnight,
                                location_id=slot.location_id,
                                location_name=loc_name,
                                nearest_station_code=nearest_station,
                                instructor_or_supervisor=slot.instructor_or_supervisor,
                                is_exception=bool(exception),
                                exception_reason=exception.reason if exception else None,
                            )
                        )

            day_occurrences.sort(key=lambda o: o.start_time)
            total_count += len(day_occurrences)

            days_list.append(
                DaySchedule(
                    date=curr_date,
                    day_of_week=curr_weekday,
                    day_name=day_names[curr_weekday],
                    items=day_occurrences,
                )
            )

        return WeekScheduleResponse(
            user_id=user.id,
            week_start=week_start,
            week_end=week_end,
            timezone=tz_str,
            total_occurrences=total_count,
            days=days_list,
        )
