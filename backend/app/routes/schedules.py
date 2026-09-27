import uuid
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies.auth import get_current_user, get_db_session, require_org_admin
from ..models.auth import User
from ..models.schedule import ScheduleType
from ..schemas.schedules import (
    LocationCreateRequest,
    LocationResponse,
    ScheduleAssignRequest,
    ScheduleCreateRequest,
    ScheduleDetailResponse,
    ScheduleResponse,
    ScheduleUpdateRequest,
    TodayScheduleResponse,
    UserAssignmentResponse,
    WeekScheduleResponse,
)
from ..services.schedule_service import ScheduleEngineService

router = APIRouter(prefix="/api/v1", tags=["Schedules & Timetables"])


# -------------------------------------------------------------
# Location Endpoints
# -------------------------------------------------------------
@router.post(
    "/locations",
    response_model=LocationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create organization location",
    description="Create a campus, office, or room location linked to the organization.",
)
async def create_location(
    req: LocationCreateRequest,
    current_admin: User = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db_session),
) -> LocationResponse:
    loc = await ScheduleEngineService.create_location(
        db=db,
        org_id=current_admin.org_id,
        req=req,
    )
    return LocationResponse.model_validate(loc)


@router.get(
    "/locations",
    response_model=List[LocationResponse],
    summary="List organization locations",
    description="Retrieve all active campus, office, and classroom locations for the organization.",
)
async def list_locations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> List[LocationResponse]:
    locations = await ScheduleEngineService.list_locations(
        db=db,
        org_id=current_user.org_id,
    )
    return [LocationResponse.model_validate(loc) for loc in locations]


# -------------------------------------------------------------
# Schedule CRUD Endpoints
# -------------------------------------------------------------
@router.post(
    "/schedules",
    response_model=ScheduleDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create schedule definition",
    description="Create a reusable class timetable or work shift schedule with recurring weekly slots.",
)
async def create_schedule(
    req: ScheduleCreateRequest,
    current_admin: User = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db_session),
) -> ScheduleDetailResponse:
    sched = await ScheduleEngineService.create_schedule(
        db=db,
        org_id=current_admin.org_id,
        req=req,
    )
    return ScheduleDetailResponse.model_validate(sched)


@router.get(
    "/schedules",
    response_model=List[ScheduleResponse],
    summary="List organization schedules",
    description="Retrieve all active timetables and shift schedules belonging to the organization.",
)
async def list_schedules(
    type: Optional[ScheduleType] = Query(None, description="Filter by schedule type (CLASS, SHIFT)"),
    current_admin: User = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db_session),
) -> List[ScheduleResponse]:
    schedules = await ScheduleEngineService.list_schedules(
        db=db,
        org_id=current_admin.org_id,
        type=type,
    )
    return [ScheduleResponse.model_validate(s) for s in schedules]


@router.get(
    "/schedules/{schedule_id}",
    response_model=ScheduleDetailResponse,
    summary="Get schedule details",
    description="Retrieve schedule definition along with all its recurring day slots and location links.",
)
async def get_schedule(
    schedule_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ScheduleDetailResponse:
    sched = await ScheduleEngineService.get_schedule_by_id(
        db=db,
        org_id=current_user.org_id,
        schedule_id=schedule_id,
    )
    return ScheduleDetailResponse.model_validate(sched)


@router.patch(
    "/schedules/{schedule_id}",
    response_model=ScheduleDetailResponse,
    summary="Update schedule",
    description="Update schedule title, description, active status, or replace recurring slots.",
)
async def update_schedule(
    schedule_id: uuid.UUID,
    req: ScheduleUpdateRequest,
    current_admin: User = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db_session),
) -> ScheduleDetailResponse:
    sched = await ScheduleEngineService.update_schedule(
        db=db,
        org_id=current_admin.org_id,
        schedule_id=schedule_id,
        req=req,
    )
    return ScheduleDetailResponse.model_validate(sched)


@router.delete(
    "/schedules/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete schedule",
    description="Delete a schedule and all associated slots and assignments.",
)
async def delete_schedule(
    schedule_id: uuid.UUID,
    current_admin: User = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db_session),
) -> None:
    await ScheduleEngineService.delete_schedule(
        db=db,
        org_id=current_admin.org_id,
        schedule_id=schedule_id,
    )


@router.post(
    "/schedules/{schedule_id}/assign",
    response_model=List[UserAssignmentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Assign schedule to members",
    description="Assign a timetable or shift schedule to organization students or employees.",
)
async def assign_schedule(
    schedule_id: uuid.UUID,
    req: ScheduleAssignRequest,
    current_admin: User = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db_session),
) -> List[UserAssignmentResponse]:
    assignments = await ScheduleEngineService.assign_schedule(
        db=db,
        org_id=current_admin.org_id,
        schedule_id=schedule_id,
        req=req,
    )
    return [UserAssignmentResponse.model_validate(a) for a in assignments]


# -------------------------------------------------------------
# Member Today & Week Endpoints
# -------------------------------------------------------------
@router.get(
    "/schedules/me/today",
    response_model=TodayScheduleResponse,
    summary="Get my schedule for today",
    description="Retrieve the authenticated student or employee's scheduled classes/shifts for today.",
)
async def get_my_today_schedule(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> TodayScheduleResponse:
    return await ScheduleEngineService.get_user_today_schedule(
        db=db,
        user=current_user,
    )


@router.get(
    "/schedules/me/week",
    response_model=WeekScheduleResponse,
    summary="Get my schedule for the week",
    description="Retrieve the authenticated student or employee's 7-day weekly schedule.",
)
async def get_my_week_schedule(
    date: Optional[date] = Query(None, description="Target date in YYYY-MM-DD format (defaults to current date)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> WeekScheduleResponse:
    return await ScheduleEngineService.get_user_week_schedule(
        db=db,
        user=current_user,
        query_date=date,
    )
