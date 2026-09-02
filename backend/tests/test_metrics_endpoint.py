import httpx
import pytest
from app.main import app
from httpx import ASGITransport


@pytest.mark.asyncio
async def test_metrics_endpoint():
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/metrics")

        assert response.status_code == 200
        content = response.text

        assert "scraper_duration_seconds" in content
        assert "cache_operations_total" in content
        assert "alerts_dispatched_total" in content
