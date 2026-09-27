from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseTransitProvider(ABC):
    """Abstract interface for transit data providers (RailRadar, Official, Crowd, Mock)."""

    @abstractmethod
    async def get_live_train(self, train_number: str) -> Optional[Dict[str, Any]]:
        """Fetch real-time location, speed, delay, and status for a specific train."""
        pass

    @abstractmethod
    async def get_station_board(self, station_code: str) -> Optional[Dict[str, Any]]:
        """Fetch live arrival/departure board for a station."""
        pass

    @abstractmethod
    async def get_trains_between(
        self,
        from_station: str,
        to_station: str,
        live: bool = True,
    ) -> Optional[List[Dict[str, Any]]]:
        """Fetch live-enriched trains running between two stations."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check provider connectivity and status."""
        pass
