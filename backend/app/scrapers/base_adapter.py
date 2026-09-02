from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Type

from playwright.async_api import Page


class BasePortalAdapter(ABC):
    campus_code: str = "BASE"
    campus_name: str = "Base Campus Portal"
    base_url: str = ""

    def __init__(self, base_url: str = ""):
        if base_url:
            self.base_url = base_url

    @abstractmethod
    async def authenticate(self, page: Page, username: str, password: str) -> None:
        """Perform automated headless login on the student portal."""
        pass

    @abstractmethod
    async def parse_attendance(self, page: Page) -> List[Dict[str, Any]]:
        """Scrape and normalize course attendance figures."""
        pass

    @abstractmethod
    async def parse_exam_schedule(self, page: Page) -> List[Dict[str, Any]]:
        """Scrape and normalize upcoming examination timetables."""
        pass


class CampusAdapterRegistry:
    _registry: Dict[str, Type[BasePortalAdapter]] = {}

    @classmethod
    def register(cls, campus_code: str) -> Callable[[Type[BasePortalAdapter]], Type[BasePortalAdapter]]:
        """Decorator to register a portal adapter strategy class."""
        def decorator(adapter_cls: Type[BasePortalAdapter]) -> Type[BasePortalAdapter]:
            normalized_code = campus_code.upper()
            adapter_cls.campus_code = normalized_code
            cls._registry[normalized_code] = adapter_cls
            return adapter_cls

        return decorator

    @classmethod
    def get_adapter(cls, campus_code: str, **kwargs) -> BasePortalAdapter:
        """Instantiate and return the matching campus adapter or raise ValueError."""
        normalized_code = campus_code.upper()
        if normalized_code not in cls._registry:
            supported = [
                f"{code} ({getattr(c, 'campus_name', code)})"
                for code, c in cls._registry.items()
            ]
            raise ValueError(
                f"Unsupported campus code: '{campus_code}'. Supported institutions: {', '.join(supported)}"
            )
        adapter_cls = cls._registry[normalized_code]
        return adapter_cls(**kwargs)

    @classmethod
    def list_supported_campuses(cls) -> List[Dict[str, str]]:
        """Return registered campus codes and names."""
        return [
            {
                "code": code,
                "name": getattr(adapter_cls, "campus_name", code),
                "base_url": getattr(adapter_cls, "base_url", ""),
            }
            for code, adapter_cls in cls._registry.items()
        ]
