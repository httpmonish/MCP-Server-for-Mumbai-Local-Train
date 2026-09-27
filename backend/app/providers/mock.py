from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..models.transit import (
    DataConfidence,
    DataFreshness,
    OperationalStatus,
    TransitDataSourceType,
)
from .base import BaseTransitProvider


class MockTransitProvider(BaseTransitProvider):
    """
    Simulated Transit Provider for automated tests and offline environments.
    Strictly tags all outputs as SIMULATED_TEST to ensure complete data transparency.
    """

    def __init__(self):
        self.provider_name = "MOCK_TRANSIT_SIMULATOR"

    async def get_live_train(self, train_number: str) -> Optional[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        return {
            "train_number": train_number,
            "line": "CR" if train_number.startswith("9") else "WR",
            "status": OperationalStatus.RUNNING.value,
            "latitude": 19.1860,
            "longitude": 72.9759,
            "speed_kmh": 65.4,
            "bearing": 182.0,
            "current_station_code": "THN",
            "next_station_code": "MLND",
            "delay_minutes": 3,
            "source": self.provider_name,
            "source_type": TransitDataSourceType.SIMULATED_TEST.value,
            "data_label": "SIMULATED_TEST",
            "observed_at": now.isoformat(),
            "received_at": now.isoformat(),
            "age_seconds": 5,
            "freshness": DataFreshness.FRESH.value,
            "confidence": DataConfidence.HIGH.value,
        }

    async def get_station_board(self, station_code: str) -> Optional[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        return {
            "station_code": station_code.upper(),
            "station_name": station_code.upper(),
            "line": "CR",
            "queried_at": now.strftime("%H:%M:%S"),
            "source": self.provider_name,
            "source_type": TransitDataSourceType.SIMULATED_TEST.value,
            "data_label": "SIMULATED_TEST",
            "observed_at": now.isoformat(),
            "trains": [
                {
                    "train_number": "97001",
                    "line": "CR",
                    "destination": "CSMT",
                    "train_type": "SLOW",
                    "scheduled_time": "08:30",
                    "expected_time": "08:33",
                    "delay_minutes": 3,
                    "platform": "PF 2",
                    "status": "RUNNING",
                },
                {
                    "train_number": "97003",
                    "line": "CR",
                    "destination": "CSMT",
                    "train_type": "FAST",
                    "scheduled_time": "08:38",
                    "expected_time": "08:38",
                    "delay_minutes": 0,
                    "platform": "PF 4",
                    "status": "ON_TIME",
                },
            ],
        }

    async def get_trains_between(
        self,
        from_station: str,
        to_station: str,
        live: bool = True,
    ) -> Optional[List[Dict[str, Any]]]:
        return [
            {
                "train_number": "97011",
                "line": "CR",
                "line_name": "Central Line",
                "train_type": "FAST",
                "departure_from_source": "08:45:00",
                "arrival_at_destination": "09:25:00",
                "expected_departure": "08:48:00",
                "delay_minutes": 3,
                "travel_time_minutes": 40,
                "platform": "PF 4",
                "crowd_level": "High",
                "source_terminal": "Kalyan",
                "dest_terminal": "CSMT",
                "data_label": "SIMULATED_TEST",
            }
        ]

    async def health_check(self) -> bool:
        return True
