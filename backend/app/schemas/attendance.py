import uuid
from datetime import date, datetime, time
from typing import List, Optional

from app.models.attendance import (
    AttendanceRiskStatus,
    AttendanceSource,
    AttendanceStatus,
    PolicyAppliesTo,
)
from pydantic import BaseModel, ConfigDict, Field


class AttendancePolicyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    applies_to: PolicyAppliesTo = PolicyAppliesTo.ALL
    min_percentage: float = Field(75.0, ge=0.0, le=100.0)
    late_penalty_multiplier: float = Field(1.0, ge=0.0, le=1.0)
    count_excused_in_denominator: bool = False
    is_active: bool = True
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None


class AttendancePolicyCreate(AttendancePolicyBase):
    pass


class AttendancePolicyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    applies_to: Optional[PolicyAppliesTo] = None
    min_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    late_penalty_multiplier: Optional[float] = Field(None, ge=0.0, le=100.0)
    count_excused_in_denominator: Optional[bool] = None
    is_active: Optional[bool] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None


class AttendancePolicyResponse(AttendancePolicyBase):
    id: uuid.UUID
    org_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AttendanceRecordCreate(BaseModel):
    user_id: uuid.UUID
    schedule_slot_id: Optional[uuid.UUID] = None
    date: date
    status: AttendanceStatus = AttendanceStatus.PRESENT
    source: AttendanceSource = AttendanceSource.MANUAL
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    remarks: Optional[str] = Field(None, max_length=255)


class BulkAttendanceItem(BaseModel):
    user_id: uuid.UUID
    status: AttendanceStatus = AttendanceStatus.PRESENT
    remarks: Optional[str] = Field(None, max_length=255)


class BulkAttendanceCreate(BaseModel):
    schedule_slot_id: Optional[uuid.UUID] = None
    date: date
    records: List[BulkAttendanceItem] = Field(..., min_length=1)
    source: AttendanceSource = AttendanceSource.MANUAL


class AttendanceRecordUpdate(BaseModel):
    status: AttendanceStatus
    reason: str = Field(..., min_length=3, max_length=500, description="Mandatory reason for correcting attendance")


class AttendanceRecordResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    user_id: uuid.UUID
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    schedule_slot_id: Optional[uuid.UUID] = None
    slot_title: Optional[str] = None
    date: date
    status: AttendanceStatus
    source: AttendanceSource
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    marked_by_user_id: Optional[uuid.UUID] = None
    remarks: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AttendanceAuditResponse(BaseModel):
    id: uuid.UUID
    record_id: uuid.UUID
    changed_by_user_id: Optional[uuid.UUID] = None
    changed_by_name: Optional[str] = None
    old_status: str
    new_status: str
    reason: str
    ip_address: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AttendanceSummaryResponse(BaseModel):
    user_id: uuid.UUID
    org_id: uuid.UUID
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    total_sessions: int
    counted_sessions: int
    present_count: int
    late_count: int
    absent_count: int
    excused_count: int
    cancelled_count: int
    percentage: float
    min_percentage_required: float
    status: AttendanceRiskStatus
    shortage_percentage: float
    sessions_needed_to_recover: int
    policy_name: Optional[str] = None


class AttendanceListResponse(BaseModel):
    items: List[AttendanceRecordResponse]
    total: int
    limit: int
    offset: int
