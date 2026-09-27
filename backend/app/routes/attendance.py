import uuid
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies.auth import (
    get_current_user,
    get_db_session,
    require_hr_or_admin,
    require_org_admin,
    require_role,
    require_teacher_or_admin,
)
from ..models.attendance import AttendanceStatus, PolicyAppliesTo
from ..models.auth import User, UserRole
from ..schemas.attendance import (
    AttendanceAuditResponse,
    AttendanceListResponse,
    AttendancePolicyCreate,
    AttendancePolicyResponse,
    AttendanceRecordCreate,
    AttendanceRecordResponse,
    AttendanceRecordUpdate,
    AttendanceSummaryResponse,
    BulkAttendanceCreate,
)
from ..services.attendance_service import AttendanceService

router = APIRouter(prefix="/api/v1/attendance", tags=["Attendance Engine"])


# -------------------------------------------------------------
# Policy Management
# -------------------------------------------------------------
@router.post(
    "/policies",
    response_model=AttendancePolicyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create organization attendance policy",
    description="Define statutory thresholds, late penalty multipliers, and calculation rules.",
)
async def create_policy(
    policy_in: AttendancePolicyCreate,
    current_admin: User = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db_session),
) -> AttendancePolicyResponse:
    return await AttendanceService.create_policy(
        db=db,
        org_id=current_admin.org_id,
        policy_in=policy_in,
    )


@router.get(
    "/policies",
    response_model=List[AttendancePolicyResponse],
    summary="List organization attendance policies",
)
async def list_policies(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> List[AttendancePolicyResponse]:
    return await AttendanceService.get_policies(
        db=db,
        org_id=current_user.org_id,
    )


# -------------------------------------------------------------
# Mark Attendance
# -------------------------------------------------------------
@router.post(
    "",
    response_model=AttendanceRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Mark attendance record",
    description="Record attendance for a student/employee for a schedule slot or occurrence.",
)
async def mark_attendance(
    record_in: AttendanceRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> AttendanceRecordResponse:
    # Role checks: If student/employee is marking, they can only mark themselves
    if current_user.role in (UserRole.STUDENT, UserRole.EMPLOYEE):
        if record_in.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students and employees can only mark their own attendance.",
            )

    return await AttendanceService.mark_attendance(
        db=db,
        org_id=current_user.org_id,
        record_in=record_in,
        marked_by_user_id=current_user.id,
    )


@router.post(
    "/bulk",
    response_model=List[AttendanceRecordResponse],
    status_code=status.HTTP_200_OK,
    summary="Bulk mark class/shift attendance",
    description="Teachers and HR Admins can mark an entire class or shift in a single transaction.",
)
async def bulk_mark_attendance(
    bulk_in: BulkAttendanceCreate,
    current_user: User = Depends(
        require_role(UserRole.ORG_ADMIN, UserRole.TEACHER, UserRole.HR_ADMIN)
    ),
    db: AsyncSession = Depends(get_db_session),
) -> List[AttendanceRecordResponse]:
    return await AttendanceService.bulk_mark_attendance(
        db=db,
        org_id=current_user.org_id,
        bulk_in=bulk_in,
        marked_by_user_id=current_user.id,
    )


# -------------------------------------------------------------
# Self Attendance & Summary
# -------------------------------------------------------------
@router.get(
    "/me",
    response_model=AttendanceListResponse,
    summary="Get current user's attendance records",
    description="Retrieve chronologically sorted attendance history for the authenticated user.",
)
async def get_my_attendance(
    start_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    status: Optional[AttendanceStatus] = Query(None, description="Filter by attendance status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> AttendanceListResponse:
    items, total = await AttendanceService.get_user_attendance(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        status_filter=status,
        limit=limit,
        offset=offset,
    )
    return AttendanceListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get(
    "/me/summary",
    response_model=AttendanceSummaryResponse,
    summary="Get current user's attendance summary & shortage radar",
    description="Deterministic percentage, shortage analysis, and recoverability sessions.",
)
async def get_my_summary(
    start_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> AttendanceSummaryResponse:
    return await AttendanceService.get_user_summary(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
    )


# -------------------------------------------------------------
# Organization-wide Attendance
# -------------------------------------------------------------
@router.get(
    "/org",
    response_model=AttendanceListResponse,
    summary="Get organization attendance roster",
    description="Authorized administrators and supervisors can view multi-tenant scoped roster.",
)
async def get_org_attendance(
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    status: Optional[AttendanceStatus] = Query(None, description="Filter by attendance status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(
        require_role(UserRole.ORG_ADMIN, UserRole.HR_ADMIN, UserRole.TEACHER)
    ),
    db: AsyncSession = Depends(get_db_session),
) -> AttendanceListResponse:
    items, total = await AttendanceService.get_org_attendance(
        db=db,
        org_id=current_user.org_id,
        role_filter=role,
        start_date=start_date,
        end_date=end_date,
        status_filter=status,
        limit=limit,
        offset=offset,
    )
    return AttendanceListResponse(items=items, total=total, limit=limit, offset=offset)


# -------------------------------------------------------------
# Attendance Correction with Mandatory Audit Trail
# -------------------------------------------------------------
@router.patch(
    "/{id}",
    response_model=AttendanceRecordResponse,
    summary="Correct attendance record with audit trail",
    description="Supervisors or administrators can adjust attendance with mandatory reason logging.",
)
async def correct_attendance(
    id: uuid.UUID,
    update_in: AttendanceRecordUpdate,
    request: Request,
    current_user: User = Depends(
        require_role(UserRole.ORG_ADMIN, UserRole.TEACHER, UserRole.HR_ADMIN)
    ),
    db: AsyncSession = Depends(get_db_session),
) -> AttendanceRecordResponse:
    client_ip = request.client.host if request.client else None
    return await AttendanceService.correct_attendance(
        db=db,
        org_id=current_user.org_id,
        record_id=id,
        update_in=update_in,
        changed_by_user_id=current_user.id,
        ip_address=client_ip,
    )


@router.get(
    "/{id}/audit",
    response_model=List[AttendanceAuditResponse],
    summary="Get audit trail for attendance record",
    description="Retrieve immutable chronological correction logs for compliance.",
)
async def get_attendance_audits(
    id: uuid.UUID,
    current_user: User = Depends(
        require_role(UserRole.ORG_ADMIN, UserRole.TEACHER, UserRole.HR_ADMIN)
    ),
    db: AsyncSession = Depends(get_db_session),
) -> List[AttendanceAuditResponse]:
    return await AttendanceService.get_record_audits(
        db=db,
        org_id=current_user.org_id,
        record_id=id,
    )
