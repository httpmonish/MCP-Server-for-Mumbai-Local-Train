from unittest.mock import AsyncMock, patch

import httpx
import pytest
from app.core.telemetry import ALERTS_DISPATCHED_TOTAL
from app.services.alert_service import AlertDispatcher


@pytest.mark.asyncio
async def test_telegram_alert_success():
    mock_response = httpx.Response(
        status_code=200,
        json={"ok": True},
        request=httpx.Request("POST", "https://api.telegram.org"),
    )
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        initial_val = ALERTS_DISPATCHED_TOTAL.labels(channel="telegram", status="success")._value.get()

        dispatcher = AlertDispatcher(telegram_bot_token="fake_bot_token", telegram_chat_id="999999")
        result = await dispatcher.send_telegram_alert("Test Alert")
        await dispatcher.aclose()

        assert result is True
        mock_post.assert_called_once()
        new_val = ALERTS_DISPATCHED_TOTAL.labels(channel="telegram", status="success")._value.get()
        assert new_val == initial_val + 1


@pytest.mark.asyncio
async def test_telegram_markdown_escaping():
    raw_message = "Subject: CS-101 [74.5%] (Attended: 15/20)"
    mock_response = httpx.Response(
        status_code=200,
        json={"ok": True},
        request=httpx.Request("POST", "https://api.telegram.org"),
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        dispatcher = AlertDispatcher(telegram_bot_token="fake_bot_token", telegram_chat_id="999999")
        await dispatcher.send_telegram_alert(raw_message)
        await dispatcher.aclose()

        mock_post.assert_called_once()
        sent_json = mock_post.call_args.kwargs["json"]
        outbound_text = sent_json["text"]

        # Verify dashes, brackets, period, and parentheses are escaped for Telegram MarkdownV2
        assert r"\-" in outbound_text
        assert r"\[" in outbound_text
        assert r"\]" in outbound_text
        assert r"\(" in outbound_text
        assert r"\)" in outbound_text
        assert r"\." in outbound_text
