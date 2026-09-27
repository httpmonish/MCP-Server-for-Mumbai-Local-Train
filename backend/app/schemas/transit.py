import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from ..models.transit import (
    DataConfidence,
    DataFreshness,
    LineCode,
    OperationalStatus,
    TransitDataSourceType,
)


class DataMeta(BaseModel):
    source: str = Field(..., description="Data provider or source name (e.g. RAILRADAR, STATIC_TIMETABLE)")
    source_type: TransitDataSourceType = Field(..., description="Classification of the data source")
    data_label: str = Field(..., description="Public label: REALTIME, STATIC_TIMETABLE, STALE, SIMULATED_TEST")
    observed_at: Optional[datetime] = Field(None, description="Timestamp when telemetry was originally observed")
    received_at: Optional[datetime] = Field(None, description="Timestamp when data was ingested by TransitPulse")
    age_seconds: Optional[int] = Field(None, description="Elapsed seconds since observation")
    freshness: DataFreshness = Field(default=DataFreshness.FRESH, description="FRESH, STALE, or EXPIRED")
    confidence: DataConfidence = Field(default=DataConfidence.HIGH, description="Data confidence score")


class StationResponse(BaseModel):
    id: Optional[uuid.UUID] = None
    code: str
    name: str
    canonical_name: Optional[str] = None
    line: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    sequence_order: int
    is_fast_stop: bool
    is_interchange: bool
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class StationListResponse(BaseModel):
    line: str
    count: int
    stations: List[StationResponse]


class RailwayLineResponse(BaseModel):
    code: str
    name: str
    color: str
    description: Optional[str] = None
    status: str
    punctuality: str
    avg_headway_mins: int


class LiveTrainStateResponse(BaseModel):
    train_number: str
    line: str
    status: OperationalStatus
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    speed_kmh: Optional[float] = None
    bearing: Optional[float] = None
    current_station_code: Optional[str] = None
    next_station_code: Optional[str] = None
    delay_minutes: int = 0
    meta: DataMeta


class StationBoardItem(BaseModel):
    train_number: str
    line: str
    destination: str
    train_type: str
    scheduled_time: str
    expected_time: str
    delay_minutes: int
    platform: str
    status: str


class StationBoardResponse(BaseModel):
    station_code: str
    station_name: str
    line: str
    queried_at: str
    count: int
    trains: List[StationBoardItem]
    meta: DataMeta


class NextTrainItem(BaseModel):
    train_number: str
    line: str
    line_name: str
    train_type: str
    departure_from_source: str
    arrival_at_destination: str
    expected_departure: str
    delay_minutes: int
    travel_time_minutes: int
    platform: str
    crowd_level: str
    source_terminal: str
    dest_terminal: str
    data_label: str


class NextTrainsResponse(BaseModel):
    source: str
    destination: str
    line: Optional[str] = None
    queried_at: str
    count: int
    trains: List[NextTrainItem]
    meta: DataMeta


class ScheduleItem(BaseModel):
    train_number: str
    line: str
    train_type: str
    source: str
    destination: str
    departure_time: str
    arrival_time: str
    duration_mins: int
    stops_count: int


class ScheduleResponse(BaseModel):
    from_station: str
    to_station: str
    line: str
    count: int
    schedules: List[ScheduleItem]
    meta: DataMeta
