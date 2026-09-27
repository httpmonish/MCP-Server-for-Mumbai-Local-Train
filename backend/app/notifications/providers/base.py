from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class EmailDeliveryResult:
    success: bool
    provider: str
    provider_message_id: Optional[str] = None
    latency_ms: float = 0.0
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    is_permanent_failure: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseEmailProvider(ABC):
    @abstractmethod
    async def send_email(
        self,
        to_email: str,
        subject: str,
        text_content: str,
        html_content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EmailDeliveryResult:
        """Deliver an email message to a recipient."""
        pass
