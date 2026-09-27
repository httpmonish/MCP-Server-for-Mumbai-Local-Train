import pytest
from app.core.config import settings
from app.models.transit import DataFreshness, OperationalStatus
from app.providers.mock import MockTransitProvider
from app.providers.railradar import RailRadarProvider
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_mock_provider_lifecycle():
    provider = MockTransitProvider()
    assert await provider.health_check() is True

    # 1. Live train
    live_train = await provider.get_live_train("97001")
    assert live_train is not None
    assert live_train["train_number"] == "97001"
    assert live_train["data_label"] == "SIMULATED_TEST"
    assert live_train["speed_kmh"] > 0

    # 2. Station board
    board = await provider.get_station_board("THN")
    assert board is not None
    assert board["station_code"] == "THN"
    assert len(board["trains"]) >= 2
    assert board["data_label"] == "SIMULATED_TEST"


@pytest.mark.asyncio
async def test_railradar_provider_resilience_and_graceful_handling():
    # Test with dummy key to verify non-throwing graceful fallback
    provider = RailRadarProvider(
        base_url="https://api.railradar.io",
        api_key="test_dummy_key",
        timeout=0.1,
    )
    # When external service is unreachable or returns 401, provider returns None gracefully
    result = await provider.get_live_train("97001")
    assert result is None  # Fails open/graceful


@pytest.mark.asyncio
async def test_live_train_endpoint(client: AsyncClient):
    res = await client.get("/api/v1/trains/97001/live")
    assert res.status_code == 200
    data = res.json()
    assert data["train_number"] == "97001"
    assert data["status"] in [s.value for s in OperationalStatus]
    assert "meta" in data
    assert data["meta"]["data_label"] in ("SIMULATED_TEST", "REALTIME", "STATIC_TIMETABLE")
    assert data["meta"]["freshness"] in [f.value for f in DataFreshness]


@pytest.mark.asyncio
async def test_live_station_board_endpoint(client: AsyncClient):
    res = await client.get("/api/v1/trains/stations/THN/live")
    assert res.status_code == 200
    data = res.json()
    assert data["station_code"] == "THN"
    assert data["count"] >= 0
    assert "meta" in data
    assert data["meta"]["freshness"] in [f.value for f in DataFreshness]


@pytest.mark.asyncio
async def test_trains_between_endpoint(client: AsyncClient):
    res = await client.get("/api/v1/trains/between?from=Thane&to=CSMT&include_live=true")
    assert res.status_code == 200
    data = res.json()
    assert data["source"] == "Thane"
    assert data["destination"] == "CSMT"
    assert "trains" in data
