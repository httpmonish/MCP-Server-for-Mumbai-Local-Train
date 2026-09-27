from typing import Optional

from ...core.config import settings
from .base import BaseEmailProvider, EmailDeliveryResult
from .mock import MockEmailProvider
from .sendgrid import SendGridEmailProvider

_mock_instance: Optional[MockEmailProvider] = None


def get_mock_email_provider() -> MockEmailProvider:
    global _mock_instance
    if _mock_instance is None:
        _mock_instance = MockEmailProvider()
    return _mock_instance


def get_email_provider() -> BaseEmailProvider:
    """Factory selecting email provider based on configuration."""
    provider_name = (settings.NOTIFICATION_EMAIL_PROVIDER or "mock").lower().strip()
    if provider_name == "sendgrid" and settings.NOTIFICATION_SENDGRID_API_KEY:
        return SendGridEmailProvider()
    return get_mock_email_provider()


__all__ = [
    "BaseEmailProvider",
    "EmailDeliveryResult",
    "MockEmailProvider",
    "SendGridEmailProvider",
    "get_email_provider",
    "get_mock_email_provider",
]
