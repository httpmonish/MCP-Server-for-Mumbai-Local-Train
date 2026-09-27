import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

from ..core.config import settings
from ..core.logger import get_logger
from ..models.transit import (
    DataConfidence,
    DataFreshness,
    OperationalStatus,
    TransitDataSourceType,
)
from .base import BaseTransitProvider

logger = get_logger(__name__)


class RailRadarProvider(BaseTransitProvider):
    """
    RailRadar Live Transit Provider Adapter.
    Communicates with RailRadar external APIs with resilient error handling,
    exponential backoff retries, and strict schema normalization.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        self.base_url = (base_url or settings.RAILRADAR_BASE_URL).rstrip("/")
        self.api_key = api_key or settings.RAILRADAR_API_KEY
        self.timeout = timeout or settings.TRANSIT_LIVE_TIMEOUT_SECONDS
        self.provider_name = "RAILRADAR"
        self._consecutive_failures = 0

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": "TransitPulse-Mobility-Engine/1.0",
        }
        if self.api_key:
            headers["X-API-Key"] = self.api_key
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Execute HTTP request with 2-attempt exponential backoff retry."""
        if not self.api_key and settings.ENVIRONMENT == "production":
            logger.warning("RailRadar API key not configured in production.")
            return None

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        max_retries = 2
        backoff = 0.2

        for attempt in range(1, max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.get(url, headers=self._get_headers(), params=params)

                    if resp.status_code == 200:
                        self._consecutive_failures = 0
                        return resp.json()

                    if resp.status_code in (401, 403):
                        logger.error(f"RailRadar auth error: HTTP {resp.status_code}")
                        return None

                    if resp.status_code == 404:
                        return None

                    if resp.status_code in (429, 500, 502, 503, 504):
                        logger.warning(
                            f"RailRadar transient error HTTP {resp.status_code} (attempt {attempt}/{max_retries})"
                        )
                        if attempt < max_retries:
                            await asyncio.sleep(backoff)
                            backoff *= 2
                        continue

            except httpx.TimeoutException:
                logger.warning(f"RailRadar request timed out for {url} (attempt {attempt}/{max_retries})")
                if attempt < max_retries:
                    await asyncio.sleep(backoff)
                    backoff *= 2
            except Exception as e:
                logger.warning(f"RailRadar connection error for {url}: {e} (attempt {attempt}/{max_retries})")
                if attempt < max_retries:
                    await asyncio.sleep(backoff)
                    backoff *= 2

        self._consecutive_failures += 1
        return None

    async def get_live_train(self, train_number: str) -> Optional[Dict[str, Any]]:
        """Query RailRadar /v1/trains/{number}/live."""
        endpoint = f"v1/trains/{train_number}/live"
        data = await self._make_request(endpoint)
        if not data:
            return None

        now = datetime.now(timezone.utc)
        observed_at_str = data.get("observed_at") or now.isoformat()

        # Parse status
        raw_status = data.get("status", "RUNNING").upper()
        try:
            status_enum = OperationalStatus(raw_status).value
        except ValueError:
            status_enum = OperationalStatus.RUNNING.value

        return {
            "train_number": train_number,
            "line": data.get("line", "CR"),
            "status": status_enum,
            "latitude": data.get("latitude") or data.get("lat"),
            "longitude": data.get("longitude") or data.get("lng"),
            "speed_kmh": data.get("speed_kmh") or data.get("speed", 0.0),
            "bearing": data.get("bearing", 0.0),
            "current_station_code": data.get("current_station_code") or data.get("current_station"),
            "next_station_code": data.get("next_station_code") or data.get("next_station"),
            "delay_minutes": int(data.get("delay_minutes", data.get("delay", 0))),
            "source": self.provider_name,
            "source_type": TransitDataSourceType.LICENSED_THIRD_PARTY.value,
            "data_label": "REALTIME",
            "observed_at": observed_at_str,
            "received_at": now.isoformat(),
            "confidence": DataConfidence.HIGH.value,
        }

    async def get_station_board(self, station_code: str) -> Optional[Dict[str, Any]]:
        """Query RailRadar /v1/stations/{code}/live."""
        endpoint = f"v1/stations/{station_code}/live"
        data = await self._make_request(endpoint)
        if not data:
            return None

        now = datetime.now(timezone.utc)
        raw_trains = data.get("trains", data.get("departures", []))

        normalized_trains = []
        for t in raw_trains:
            normalized_trains.append(
                {
                    "train_number": str(t.get("train_number", t.get("number", ""))),
                    "line": t.get("line", "CR"),
                    "destination": t.get("destination", "CSMT"),
                    "train_type": t.get("train_type", t.get("type", "SLOW")),
                    "scheduled_time": t.get("scheduled_time", t.get("scheduled", "--:--")),
                    "expected_time": t.get("expected_time", t.get("expected", "--:--")),
                    "delay_minutes": int(t.get("delay_minutes", t.get("delay", 0))),
                    "platform": t.get("platform", "PF 1"),
                    "status": t.get("status", "ON_TIME"),
                }
            )

        return {
            "station_code": station_code.upper(),
            "station_name": data.get("station_name", station_code.upper()),
            "line": data.get("line", "CR"),
            "queried_at": now.strftime("%H:%M:%S"),
            "source": self.provider_name,
            "source_type": TransitDataSourceType.LICENSED_THIRD_PARTY.value,
            "data_label": "REALTIME",
            "observed_at": data.get("observed_at", now.isoformat()),
            "trains": normalized_trains,
        }

    async def get_trains_between(
        self,
        from_station: str,
        to_station: str,
        live: bool = True,
    ) -> Optional[List[Dict[str, Any]]]:
        """Query RailRadar /v1/trains/between/{from}/{to}?live=true."""
        endpoint = f"v1/trains/between/{from_station}/{to_station}"
        data = await self._make_request(endpoint, params={"live": "true" if live else "false"})
        if not data:
            return None

        trains_list = data.get("trains", data.get("data", []))
        normalized = []
        for item in trains_list:
            normalized.append(
                {
                    "train_number": str(item.get("train_number", item.get("number", ""))),
                    "line": item.get("line", "CR"),
                    "line_name": item.get("line_name", f"{item.get('line', 'CR')} Line"),
                    "train_type": item.get("train_type", "SLOW"),
                    "departure_from_source": item.get("departure_from_source", item.get("departure", "")),
                    "arrival_at_destination": item.get("arrival_at_destination", item.get("arrival", "")),
                    "expected_departure": item.get("expected_departure", item.get("departure", "")),
                    "delay_minutes": int(item.get("delay_minutes", 0)),
                    "travel_time_minutes": int(item.get("travel_time_minutes", 30)),
                    "platform": item.get("platform", "PF 1"),
                    "crowd_level": item.get("crowd_level", "Moderate"),
                    "source_terminal": item.get("source_terminal", from_station),
                    "dest_terminal": item.get("dest_terminal", to_station),
                    "data_label": "REALTIME",
                }
            )
        return normalized

    async def health_check(self) -> bool:
        if not self.api_key:
            return False
        return self._consecutive_failures < 3
