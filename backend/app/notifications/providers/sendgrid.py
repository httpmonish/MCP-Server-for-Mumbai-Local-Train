import time
from typing import Any, Dict, Optional

import httpx

from ...core.config import settings
from ...core.logger import get_logger
from .base import BaseEmailProvider, EmailDeliveryResult

logger = get_logger("notifications.sendgrid")


class SendGridEmailProvider(BaseEmailProvider):
    """
    Production SendGrid v3 Mail Send HTTP client.
    """
    def __init__(self, api_key: Optional[str] = None, from_email: Optional[str] = None, from_name: Optional[str] = None):
        self.api_key = api_key or settings.NOTIFICATION_SENDGRID_API_KEY
        self.from_email = from_email or settings.NOTIFICATION_FROM_EMAIL
        self.from_name = from_name or settings.NOTIFICATION_FROM_NAME
        self.base_url = "https://api.sendgrid.com/v3/mail/send"

    async def send_email(
        self,
        to_email: str,
        subject: str,
        text_content: str,
        html_content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EmailDeliveryResult:
        if not self.api_key:
            return EmailDeliveryResult(
                success=False,
                provider="sendgrid",
                error_code="MISSING_API_KEY",
                error_message="SendGrid API key is not configured.",
                is_permanent_failure=True,
            )

        start_time = time.perf_counter()
        payload = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": self.from_email, "name": self.from_name},
            "subject": subject,
            "content": [{"type": "text/plain", "value": text_content}],
        }
        if html_content:
            payload["content"].append({"type": "text/html", "value": html_content})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.post(self.base_url, json=payload, headers=headers)
                latency = (time.perf_counter() - start_time) * 1000

                if resp.status_code in (200, 202):
                    msg_id = resp.headers.get("X-Message-Id") or "sg-delivered"
                    return EmailDeliveryResult(
                        success=True,
                        provider="sendgrid",
                        provider_message_id=msg_id,
                        latency_ms=latency,
                    )
                elif resp.status_code == 429:
                    return EmailDeliveryResult(
                        success=False,
                        provider="sendgrid",
                        latency_ms=latency,
                        error_code="RATE_LIMITED",
                        error_message="SendGrid rate limit exceeded.",
                        is_permanent_failure=False,
                    )
                elif 400 <= resp.status_code < 500:
                    return EmailDeliveryResult(
                        success=False,
                        provider="sendgrid",
                        latency_ms=latency,
                        error_code=f"SENDGRID_{resp.status_code}",
                        error_message=f"SendGrid request rejected: {resp.text[:200]}",
                        is_permanent_failure=True,
                    )
                else:
                    return EmailDeliveryResult(
                        success=False,
                        provider="sendgrid",
                        latency_ms=latency,
                        error_code=f"SENDGRID_{resp.status_code}",
                        error_message=f"SendGrid server error: {resp.status_code}",
                        is_permanent_failure=False,
                    )
        except httpx.TimeoutException:
            latency = (time.perf_counter() - start_time) * 1000
            return EmailDeliveryResult(
                success=False,
                provider="sendgrid",
                latency_ms=latency,
                error_code="PROVIDER_TIMEOUT",
                error_message="SendGrid HTTP request timed out.",
                is_permanent_failure=False,
            )
        except Exception as e:
            latency = (time.perf_counter() - start_time) * 1000
            logger.error(f"SendGrid delivery exception: {e}", exc_info=True)
            return EmailDeliveryResult(
                success=False,
                provider="sendgrid",
                latency_ms=latency,
                error_code="PROVIDER_EXCEPTION",
                error_message=str(e),
                is_permanent_failure=False,
            )
