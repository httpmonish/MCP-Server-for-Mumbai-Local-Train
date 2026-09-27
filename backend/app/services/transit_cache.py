from typing import Any, Dict, List, Optional

from ..cache import RedisCache
from ..core.config import settings
from ..core.logger import get_logger

logger = get_logger(__name__)


class TransitCacheManager:
    """Manages Redis caching for real-time transit telemetry, boards, and routes."""

    def __init__(self, cache: RedisCache):
        self.cache = cache

    async def get_live_train(self, train_number: str) -> Optional[Dict[str, Any]]:
        key = f"transit:live:train:{train_number.upper()}"
        try:
            return await self.cache.get(key)
        except Exception as e:
            logger.debug(f"TransitCache get_live_train failed: {e}")
            return None

    async def set_live_train(self, train_number: str, data: Dict[str, Any], ttl: Optional[int] = None) -> None:
        key = f"transit:live:train:{train_number.upper()}"
        ttl_val = ttl or settings.TRANSIT_CACHE_TTL_LIVE_TRAIN
        try:
            await self.cache.set(key, data, ttl_val)
        except Exception as e:
            logger.debug(f"TransitCache set_live_train failed: {e}")

    async def get_station_board(self, station_code: str) -> Optional[Dict[str, Any]]:
        key = f"transit:live:station:{station_code.upper()}"
        try:
            return await self.cache.get(key)
        except Exception as e:
            logger.debug(f"TransitCache get_station_board failed: {e}")
            return None

    async def set_station_board(self, station_code: str, data: Dict[str, Any], ttl: Optional[int] = None) -> None:
        key = f"transit:live:station:{station_code.upper()}"
        ttl_val = ttl or settings.TRANSIT_CACHE_TTL_STATION_BOARD
        try:
            await self.cache.set(key, data, ttl_val)
        except Exception as e:
            logger.debug(f"TransitCache set_station_board failed: {e}")

    async def get_next_trains(self, from_stn: str, to_stn: str, hour: int, slot: int) -> Optional[List[Dict[str, Any]]]:
        key = f"transit:next:{from_stn.upper()}:{to_stn.upper()}:{hour}:{slot}"
        try:
            return await self.cache.get(key)
        except Exception as e:
            logger.debug(f"TransitCache get_next_trains failed: {e}")
            return None

    async def set_next_trains(self, from_stn: str, to_stn: str, hour: int, slot: int, data: List[Dict[str, Any]]) -> None:
        key = f"transit:next:{from_stn.upper()}:{to_stn.upper()}:{hour}:{slot}"
        try:
            await self.cache.set(key, data, 120)
        except Exception as e:
            logger.debug(f"TransitCache set_next_trains failed: {e}")
