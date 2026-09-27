import enum
import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class CommuteStatus(str, enum.Enum):
    ON_TIME = "ON_TIME"
    AT_RISK = "AT_RISK"
    LIKELY_LATE = "LIKELY_LATE"
    NO_DATA = "NO_DATA"


class CombinedRiskStatus(str, enum.Enum):
    NORMAL = "NORMAL"
    ATTENDANCE_NEAR_THRESHOLD = "ATTENDANCE_NEAR_THRESHOLD"
    ATTENDANCE_RISK = "ATTENDANCE_RISK"
    COMMUTE_RISK = "COMMUTE_RISK"
    COMBINED_RISK = "COMBINED_RISK"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    NO_UPCOMING_SCHEDULE = "NO_UPCOMING_SCHEDULE"


class IntelligenceConfidence(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class ReasonCode(str, enum.Enum):
    ON_TIME_COMFORTABLE_MARGIN = "ON_TIME_COMFORTABLE_MARGIN"
    ARRIVAL_AFTER_REQUIRED_TIME = "ARRIVAL_AFTER_REQUIRED_TIME"
    LOW_ARRIVAL_MARGIN = "LOW_ARRIVAL_MARGIN"
    ATTENDANCE_BELOW_THRESHOLD = "ATTENDANCE_BELOW_THRESHOLD"
    ATTENDANCE_NEAR_THRESHOLD = "ATTENDANCE_NEAR_THRESHOLD"
    ATTENDANCE_HEALTHY = "ATTENDANCE_HEALTHY"
    STATIC_TIMETABLE_FALLBACK = "STATIC_TIMETABLE_FALLBACK"
    LIVE_DATA_FRESH = "LIVE_DATA_FRESH"
    LIVE_DATA_STALE = "LIVE_DATA_STALE"
    NO_SCHEDULE_FOUND = "NO_SCHEDULE_FOUND"
    NO_TRANSIT_OPTIONS_AVAILABLE = "NO_TRANSIT_OPTIONS_AVAILABLE"
    LAST_MILE_BUFFER_APPLIED = "LAST_MILE_BUFFER_APPLIED"


class ScheduleIntelligenceFact(BaseModel):
    slot_id: Optional[uuid.UUID] = None
    title: str
    schedule_type: str
    start_time: str
    end_time: str
    location_name: Optional[str] = None
    destination_station: str
    required_arrival_time: str
    is_overnight: bool = False
    instructor_or_supervisor: Optional[str] = None


class CommuteIntelligenceFact(BaseModel):
    origin_station: str
    destination_station: str
    train_number: Optional[str] = None
    train_type: Optional[str] = None
    line: Optional[str] = None
    scheduled_departure: Optional[str] = None
    scheduled_arrival: Optional[str] = None
    delay_minutes: int = 0
    estimated_station_arrival: Optional[str] = None
    estimated_final_arrival: Optional[str] = None
    arrival_margin_minutes: Optional[int] = None
    travel_time_minutes: Optional[int] = None
    platform: Optional[str] = None
    status: CommuteStatus


class AttendanceIntelligenceFact(BaseModel):
    percentage: Optional[float] = None
    min_percentage_required: Optional[float] = None
    status: str
    shortage_percentage: float = 0.0
    sessions_needed_to_recover: int = 0
    total_sessions: int = 0
    counted_sessions: int = 0
    policy_name: Optional[str] = None


class DataProvenanceFact(BaseModel):
    transit_source: str
    data_label: str
    freshness: str
    confidence: IntelligenceConfidence
    last_updated: Optional[datetime] = None


class CommuteCheckResponse(BaseModel):
    rules_version: str = "1.0.0"
    user_id: uuid.UUID
    evaluated_at: datetime
    schedule: Optional[ScheduleIntelligenceFact] = None
    commute: Optional[CommuteIntelligenceFact] = None
    attendance: Optional[AttendanceIntelligenceFact] = None
    combined_status: CombinedRiskStatus
    reason_codes: List[str]
    decision_summary: str
    data_provenance: DataProvenanceFact

    model_config = ConfigDict(from_attributes=True)
