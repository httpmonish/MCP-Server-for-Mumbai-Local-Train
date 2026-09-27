import uuid
from datetime import date, datetime, time
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..models.schedule import ExceptionType, ScheduleType


class LocationCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Location name (e.g. Vidyavihar Campus)")
    address: Optional[str] = Field(None, max_length=255, description="Street address or building details")
    latitude: Optional[float] = Field(None, description="GPS Latitude")
    longitude: Optional[float] = Field(None, description="GPS Longitude")
    nearest_station_code: Optional[str] = Field(None, max_length=10, description="Nearest Mumbai transit station code")

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Location name cannot be blank.")
        return cleaned


class LocationResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    name: str
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    nearest_station_code: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ScheduleSlotInput(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 1=Tuesday, ..., 6=Sunday")
    start_time: str = Field(..., description="Start time in HH:MM or HH:MM:SS format")
    end_time: str = Field(..., description="End time in HH:MM or HH:MM:SS format")
    title: str = Field(..., min_length=1, max_length=255, description="Class subject or shift title")
    location_id: Optional[uuid.UUID] = Field(None, description="Linked organization location ID")
    location_name: Optional[str] = Field(None, max_length=255, description="Free-text location or room name")
    instructor_or_supervisor: Optional[str] = Field(None, max_length=255, description="Faculty or lead name")


class ScheduleSlotResponse(BaseModel):
    id: uuid.UUID
    schedule_id: uuid.UUID
    day_of_week: int
    start_time: time
    end_time: time
    title: str
    location_id: Optional[uuid.UUID] = None
    location_name: Optional[str] = None
    instructor_or_supervisor: Optional[str] = None
    is_overnight: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ScheduleCreateRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=255, description="Schedule title (e.g. CSE Sem 5 Timetable)")
    type: ScheduleType = Field(default=ScheduleType.CLASS, description="CLASS, SHIFT, etc.")
    timezone: str = Field(default="Asia/Kolkata", description="IANA timezone name")
    description: Optional[str] = Field(None, max_length=500, description="Schedule description")
    slots: List[ScheduleSlotInput] = Field(default=[], description="Initial schedule slots")

    @field_validator("title")
    @classmethod
    def clean_title(cls, v: str) -> str:
        cleaned = v.strip()
        if len(cleaned) < 2:
            raise ValueError("Schedule title must be at least 2 characters long.")
        return cleaned


class ScheduleUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    timezone: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    slots: Optional[List[ScheduleSlotInput]] = None


class ScheduleResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    title: str
    type: ScheduleType
    timezone: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ScheduleDetailResponse(ScheduleResponse):
    slots: List[ScheduleSlotResponse] = []


class ScheduleAssignRequest(BaseModel):
    user_ids: List[uuid.UUID] = Field(..., min_length=1, description="List of user UUIDs to assign")
    valid_from: date = Field(..., description="Assignment start date (YYYY-MM-DD)")
    valid_until: Optional[date] = Field(None, description="Optional assignment end date (YYYY-MM-DD)")

    @field_validator("valid_until")
    @classmethod
    def validate_dates(cls, v: Optional[date], info) -> Optional[date]:
        valid_from = info.data.get("valid_from")
        if v is not None and valid_from is not None and v < valid_from:
            raise ValueError("valid_until date cannot precede valid_from date.")
        return v


class UserAssignmentResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    user_id: uuid.UUID
    schedule_id: uuid.UUID
    valid_from: date
    valid_until: Optional[date] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ScheduleOccurrence(BaseModel):
    slot_id: uuid.UUID
    schedule_id: uuid.UUID
    schedule_title: str
    schedule_type: ScheduleType
    title: str
    start_time: str
    end_time: str
    is_overnight: bool
    location_id: Optional[uuid.UUID] = None
    location_name: Optional[str] = None
    nearest_station_code: Optional[str] = None
    instructor_or_supervisor: Optional[str] = None
    is_exception: bool = False
    exception_reason: Optional[str] = None


class TodayScheduleResponse(BaseModel):
    user_id: uuid.UUID
    date: date
    day_name: str
    timezone: str
    count: int
    items: List[ScheduleOccurrence]


class DaySchedule(BaseModel):
    date: date
    day_of_week: int
    day_name: str
    items: List[ScheduleOccurrence]


class WeekScheduleResponse(BaseModel):
    user_id: uuid.UUID
    week_start: date
    week_end: date
    timezone: str
    total_occurrences: int
    days: List[DaySchedule]
