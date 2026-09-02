import re
from typing import Optional

import httpx

from ..core.config import settings
from ..core.logger import get_logger
from ..core.telemetry import ALERTS_DISPATCHED_TOTAL

logger = get_logger(__name__)


def escape_markdown_v2(text: str) -> str:
    """Escape special characters reserved in Telegram MarkdownV2."""
    return re.sub(r"([_*\[\]()~>#+\-=|{}.!])", r"\\\1", text)


class AlertDispatcher:
    def __init__(
        self,
        telegram_bot_token: Optional[str] = None,
        telegram_chat_id: Optional[str] = None,
    ):
        self.telegram_bot_token = telegram_bot_token or settings.TELEGRAM_BOT_TOKEN
        self.telegram_chat_id = telegram_chat_id or settings.TELEGRAM_CHAT_ID
        self.client = httpx.AsyncClient(timeout=10.0)

    def escape_markdown_v2(self, text: str) -> str:
        return escape_markdown_v2(text)

    async def send_telegram_alert(
        self, message_markdown: str, chat_id: Optional[str] = None
    ) -> bool:
        target_chat_id = chat_id or self.telegram_chat_id
        token = self.telegram_bot_token
        if not token or not target_chat_id:
            logger.warning("Telegram bot token or chat ID missing; cannot send alert.")
            ALERTS_DISPATCHED_TOTAL.labels(channel="telegram", status="failure").inc()
            return False

        escaped_text = self.escape_markdown_v2(message_markdown)
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": target_chat_id,
            "text": escaped_text,
            "parse_mode": "MarkdownV2",
            "disable_web_page_preview": True,
        }

        try:
            response = await self.client.post(url, json=payload)
            if response.status_code == 200:
                ALERTS_DISPATCHED_TOTAL.labels(channel="telegram", status="success").inc()
                return True
            else:
                logger.error(
                    f"Telegram alert failed with HTTP {response.status_code}: {response.text}"
                )
                ALERTS_DISPATCHED_TOTAL.labels(channel="telegram", status="failure").inc()
                return False
        except Exception as exc:
            logger.error(f"Error dispatching Telegram alert: {exc}")
            ALERTS_DISPATCHED_TOTAL.labels(channel="telegram", status="failure").inc()
            return False

    async def send_webhook_alert(self, webhook_url: str, payload: dict) -> bool:
        try:
            response = await self.client.post(webhook_url, json=payload)
            if 200 <= response.status_code < 300:
                ALERTS_DISPATCHED_TOTAL.labels(channel="webhook", status="success").inc()
                return True
            else:
                logger.error(
                    f"Webhook alert failed with HTTP {response.status_code}: {response.text}"
                )
                ALERTS_DISPATCHED_TOTAL.labels(channel="webhook", status="failure").inc()
                return False
        except Exception as exc:
            logger.error(f"Error dispatching webhook alert to {webhook_url}: {exc}")
            ALERTS_DISPATCHED_TOTAL.labels(channel="webhook", status="failure").inc()
            return False

    async def aclose(self) -> None:
        await self.client.aclose()
