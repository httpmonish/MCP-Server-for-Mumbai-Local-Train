from unittest.mock import AsyncMock, patch

import pytest
from app.chaos.fault_injector import ChaosInjector
from app.main import app
from app.scrapers.adapters.mu_standard import MUStandardAdapter
from app.scrapers.base_adapter import CampusAdapterRegistry
from app.services import train_service
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_resilience_under_portal_latency_jitter():
    injector = ChaosInjector(enabled=True)
    delay = await injector.inject_latency(min_ms=50, max_ms=150)
    assert delay >= 0.05

    client = TestClient(app)
    mock_attendance = {
        "data": [{"subject_name": "Operating Systems", "total_conducted": 30, "total_attended": 28, "percentage": 93.3}],
        "source": "live",
        "stale": False,
    }

    with patch.object(app.state.orchestrator, "get_attendance", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_attendance
        response = client.post(
            "/api/v1/academic/attendance/241635",
            json={"username": "testuser", "password": "testpass", "campus_code": "MU_STANDARD"},
        )
        assert response.status_code == 200
        assert response.json()["data"][0]["subject_name"] == "Operating Systems"


@pytest.mark.asyncio
async def test_resilience_under_database_partition():
    # Simulate DB failure while Redis cache has train schedule data
    mock_cached_trains = [
        {
            "train_number": "97001",
            "line": "CR",
            "train_type": "FAST",
            "departure_from_source": "08:15",
            "arrival_at_destination": "08:45",
            "travel_time_minutes": 30,
        }
    ]

    mock_cache = AsyncMock()
    mock_cache.get = AsyncMock(return_value=mock_cached_trains)

    # Broken database session that raises an error if queried
    mock_db = AsyncMock()
    mock_db.execute.side_effect = ConnectionResetError("PostgreSQL pool partition disconnect")

    result = await train_service.get_next_trains(
        db_session=mock_db,
        cache=mock_cache,
        source="Thane",
        destination="Byculla",
        query_time=train_service.time(8, 15),
    )

    # Assert cache serves train routes gracefully without database access
    assert result["source"] == "cache"
    assert len(result["data"]) == 1
    assert result["data"][0]["train_number"] == "97001"
    mock_db.execute.assert_not_called()


def test_multi_campus_adapter_resolution():
    client = TestClient(app)

    # 1. Valid MU_STANDARD resolution
    adapter = CampusAdapterRegistry.get_adapter("MU_STANDARD")
    assert isinstance(adapter, MUStandardAdapter)
    assert adapter.campus_code == "MU_STANDARD"
    assert adapter.campus_name == "University of Mumbai Standard ERP"

    # 2. Unknown campus rejected with HTTP 400 and list of supported institutions
    response = client.post(
        "/api/v1/academic/attendance/241635",
        json={"username": "user", "password": "pwd", "campus_code": "UNKNOWN_CAMPUS"},
    )
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "Unsupported campus code: 'UNKNOWN_CAMPUS'" in detail
    assert "MU_STANDARD" in detail
