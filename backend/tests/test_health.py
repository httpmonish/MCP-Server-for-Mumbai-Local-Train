import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from httpx import ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.cache import RedisCache
from backend.app.main import app


@pytest.mark.asyncio
async def test_liveness_endpoint():
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "alive"

@pytest.mark.asyncio
async def test_readiness_all_healthy():
    with patch("backend.app.main.async_session_factory") as mock_session_factory, \
         patch("backend.app.main.cache") as mock_cache:

        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.execute.return_value = MagicMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        # Correctly mock the async ping method
        mock_cache.ping = AsyncMock(return_value=True)

        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/ready")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ready"
            assert data["services"]["database"] == "connected"
            assert data["services"]["redis"] == "connected"

@pytest.mark.asyncio
async def test_readiness_database_down():
    with patch("backend.app.main.async_session_factory") as mock_session_factory, \
         patch("backend.app.main.cache") as mock_cache:

        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.execute.side_effect = Exception("Connection Timeout")
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        mock_cache.ping = AsyncMock(return_value=True)

        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/ready")
            assert response.status_code == 503
            data = response.json()["detail"]
            assert data["status"] == "degraded"
            assert "database" in data["services"]
            assert "error" in data["services"]["database"]

@pytest.mark.asyncio
async def test_readiness_redis_down():
    with patch("backend.app.main.async_session_factory") as mock_session_factory, \
         patch("backend.app.main.cache") as mock_cache:

        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.execute.return_value = MagicMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        # Correctly mock the async ping method
        mock_cache.ping = AsyncMock(return_value=False)

        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/ready")
            assert response.status_code == 503
            data = response.json()["detail"]
            assert data["status"] == "degraded"
            assert data["services"]["redis"] == "disconnected"
