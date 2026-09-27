import time
import uuid
from typing import Any, Dict, List, Optional

from .base import BaseEmailProvider, EmailDeliveryResult


class MockEmailProvider(BaseEmailProvider):
    """
    Mock Email Provider for automated tests and offline development.
    Records delivered messages and supports failure simulation.
    """
    def __init__(self):
        self.sent_messages: List[Dict[str, Any]] = []
        self.simulated_failure_type: Optional[str] = None  # None | "timeout" | "429" | "500" | "invalid_email"

    async def send_email(
        self,
        to_email: str,
        subject: str,
        text_content: str,
        html_content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EmailDeliveryResult:
        start_time = time.perf_counter()

        # Handle failure simulations
        if self.simulated_failure_type == "timeout":
            latency = (time.perf_counter() - start_time) * 1000 + 100
            return EmailDeliveryResult(
                success=False,
                provider="mock",
                latency_ms=latency,
                error_code="PROVIDER_TIMEOUT",
                error_message="Simulated mock socket timeout connecting to mail exchange.",
                is_permanent_failure=False,
            )
        elif self.simulated_failure_type == "429":
            latency = (time.perf_counter() - start_time) * 1000 + 10
            return EmailDeliveryResult(
                success=False,
                provider="mock",
                latency_ms=latency,
                error_code="RATE_LIMITED",
                error_message="Simulated provider 429 Too Many Requests rate limit exceeded.",
                is_permanent_failure=False,
            )
        elif self.simulated_failure_type == "500":
            latency = (time.perf_counter() - start_time) * 1000 + 10
            return EmailDeliveryResult(
                success=False,
                provider="mock",
                latency_ms=latency,
                error_code="PROVIDER_5XX",
                error_message="Simulated provider 500 Internal Server Error.",
                is_permanent_failure=False,
            )
        elif self.simulated_failure_type == "invalid_email" or "invalid" in to_email.lower():
            latency = (time.perf_counter() - start_time) * 1000 + 5
            return EmailDeliveryResult(
                success=False,
                provider="mock",
                latency_ms=latency,
                error_code="INVALID_RECIPIENT",
                error_message="Recipient address was rejected as permanently undeliverable.",
                is_permanent_failure=True,
            )

        # Successful mock delivery
        latency = (time.perf_counter() - start_time) * 1000 + 2
        msg_id = f"mock-msg-{uuid.uuid4().hex[:12]}"
        record = {
            "id": msg_id,
            "to_email": to_email,
            "subject": subject,
            "text_content": text_content,
            "html_content": html_content,
            "metadata": metadata or {},
            "timestamp": time.time(),
        }
        self.sent_messages.append(record)

        return EmailDeliveryResult(
            success=True,
            provider="mock",
            provider_message_id=msg_id,
            latency_ms=latency,
        )

    def clear(self):
        self.sent_messages.clear()
        self.simulated_failure_type = None
