import uuid
from datetime import datetime, time
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from ..models.notification import (
    DeliveryAttemptStatus,
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
    NotificationType,
    OutboxStatus,
)


class NotificationPreferenceBase(BaseModel):
    notification_type: NotificationType
    channel: NotificationChannel = NotificationChannel.EMAIL
    enabled: bool = True
    quiet_hours_start: Optional[time] = None
    quiet_hours_end: Optional[time] = None
    timezone: str = "Asia/Kolkata"


class NotificationPreferenceUpdate(BaseModel):
    notification_type: NotificationType
    channel: NotificationChannel = NotificationChannel.EMAIL
    enabled: bool
    quiet_hours_start: Optional[time] = None
    quiet_hours_end: Optional[time] = None
    timezone: Optional[str] = "Asia/Kolkata"


class NotificationPreferenceResponse(NotificationPreferenceBase):
    id: uuid.UUID
    org_id: uuid.UUID
    user_id: uuid.UUID
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationDeliveryResponse(BaseModel):
    id: uuid.UUID
    provider: str
    provider_message_id: Optional[str] = None
    status: DeliveryAttemptStatus
    attempt_number: int
    latency_ms: float
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    attempted_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    user_id: uuid.UUID
    type: NotificationType
    channel: NotificationChannel
    priority: NotificationPriority
    title: str
    body: str
    html_body: Optional[str] = None
    status: NotificationStatus
    scheduled_for: datetime
    created_at: datetime
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    suppressed_reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    items: List[NotificationResponse]
    total: int
    unread_count: int
    limit: int
    offset: int


# Domain Event Payloads
class AttendanceBelowThresholdPayload(BaseModel):
    user_id: uuid.UUID
    org_id: uuid.UUID
    percentage: float
    min_required: float
    shortage_count: int
    policy_name: Optional[str] = None
    occurred_at: datetime = Field(default_factory=lambda: datetime.now())


class CommuteDelayRiskPayload(BaseModel):
    user_id: uuid.UUID
    org_id: uuid.UUID
    slot_id: uuid.UUID
    slot_title: str
    origin_station: str
    destination_station: str
    train_number: Optional[str] = None
    scheduled_start: str
    estimated_arrival: str
    arrival_margin_minutes: int
    risk_status: str
    reason_codes: List[str] = []
    occurred_at: datetime = Field(default_factory=lambda: datetime.now())


class ClassReminderPayload(BaseModel):
    user_id: uuid.UUID
    org_id: uuid.UUID
    slot_id: uuid.UUID
    slot_title: str
    schedule_title: str
    start_time: str
    location_name: Optional[str] = None
    station_code: Optional[str] = None
    target_date: str
    minutes_before: int = 30
    occurred_at: datetime = Field(default_factory=lambda: datetime.now())
