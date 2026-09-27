from datetime import datetime, timezone
from typing import Any, Dict, Optional

from ..models.transit import (
    DataConfidence,
    DataFreshness,
    OperationalStatus,
    TransitDataSourceType,
)
from ..schemas.transit import DataMeta, LiveTrainStateResponse


class TransitNormalizer:
    """
    Normalizes transit telemetry into canonical domain representations.
    Evaluates age, freshness, confidence, and validates spatial boundaries.
    """

    MUMBAI_LAT_MIN = 18.50
    MUMBAI_LAT_MAX = 20.20
    MUMBAI_LON_MIN = 72.50
    MUMBAI_LON_MAX = 73.50

    @classmethod
    def calculate_freshness(cls, observed_at: Optional[datetime]) -> tuple[DataFreshness, int]:
        if not observed_at:
            return DataFreshness.EXPIRED, 999999

        now = datetime.now(timezone.utc)
        if observed_at.tzinfo is None:
            observed_at = observed_at.replace(tzinfo=timezone.utc)

        age_seconds = max(0, int((now - observed_at).total_seconds()))

        if age_seconds <= 120:
            freshness = DataFreshness.FRESH
        elif age_seconds <= 600:
            freshness = DataFreshness.STALE
        else:
            freshness = DataFreshness.EXPIRED

        return freshness, age_seconds

    @classmethod
    def validate_spatial_telemetry(
        cls,
        lat: Optional[float],
        lon: Optional[float],
        speed: Optional[float],
    ) -> tuple[Optional[float], Optional[float], Optional[float]]:
        valid_lat = lat if (lat and cls.MUMBAI_LAT_MIN <= lat <= cls.MUMBAI_LAT_MAX) else None
        valid_lon = lon if (lon and cls.MUMBAI_LON_MIN <= lon <= cls.MUMBAI_LON_MAX) else None
        valid_speed = speed if (speed is not None and 0.0 <= speed <= 140.0) else 0.0
        return valid_lat, valid_lon, valid_speed

    @classmethod
    def normalize_live_train_state(cls, raw: Dict[str, Any]) -> LiveTrainStateResponse:
        observed_at_raw = raw.get("observed_at")
        if isinstance(observed_at_raw, str):
            try:
                observed_at = datetime.fromisoformat(observed_at_raw.replace("Z", "+00:00"))
            except ValueError:
                observed_at = datetime.now(timezone.utc)
        elif isinstance(observed_at_raw, datetime):
            observed_at = observed_at_raw
        else:
            observed_at = datetime.now(timezone.utc)

        freshness, age_seconds = cls.calculate_freshness(observed_at)

        lat, lon, speed = cls.validate_spatial_telemetry(
            lat=raw.get("latitude"),
            lon=raw.get("longitude"),
            speed=raw.get("speed_kmh"),
        )

        status_str = raw.get("status", "RUNNING")
        try:
            status_enum = OperationalStatus(status_str)
        except ValueError:
            status_enum = OperationalStatus.RUNNING

        source_type_str = raw.get("source_type", TransitDataSourceType.INTERNAL.value)
        try:
            source_type_enum = TransitDataSourceType(source_type_str)
        except ValueError:
            source_type_enum = TransitDataSourceType.INTERNAL

        confidence_str = raw.get("confidence", DataConfidence.HIGH.value)
        try:
            confidence_enum = DataConfidence(confidence_str)
        except ValueError:
            confidence_enum = DataConfidence.HIGH

        data_label = raw.get("data_label", "REALTIME")
        if freshness == DataFreshness.EXPIRED or freshness == DataFreshness.STALE:
            data_label = "STALE"

        meta = DataMeta(
            source=raw.get("source", "UNKNOWN"),
            source_type=source_type_enum,
            data_label=data_label,
            observed_at=observed_at,
            received_at=datetime.now(timezone.utc),
            age_seconds=age_seconds,
            freshness=freshness,
            confidence=confidence_enum,
        )

        return LiveTrainStateResponse(
            train_number=str(raw.get("train_number", "")),
            line=raw.get("line", "CR"),
            status=status_enum,
            latitude=lat,
            longitude=lon,
            speed_kmh=speed,
            bearing=raw.get("bearing"),
            current_station_code=raw.get("current_station_code"),
            next_station_code=raw.get("next_station_code"),
            delay_minutes=int(raw.get("delay_minutes", 0)),
            meta=meta,
        )
