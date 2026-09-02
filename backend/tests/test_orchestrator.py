from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.core.config import settings
from backend.app.main import app
from backend.app.scrapers.exceptions import PortalTimeoutError
from backend.app.services.academic_orchestrator import AcademicOrchestrator


@pytest.fixture
def mock_deps():
    return {
        "scraper": AsyncMock(),
        "cache": AsyncMock(),
        "db_session_factory": MagicMock()
    }

@pytest.mark.asyncio
async def test_cache_hit_skips_scraper(mock_deps):
    # Arrange
    student_id = "TEST123"
    creds = {"username": "u", "password": "p"}
    mock_data = [{"subject": "Math", "percentage": 80.0}]

    mock_deps["cache"].get.return_value = mock_data

    orchestrator = AcademicOrchestrator(
        mock_deps["scraper"],
        mock_deps["cache"],
        mock_deps["db_session_factory"]
    )

    # Act
    result = await orchestrator.get_attendance(student_id, creds)

    # Assert
    assert result["source"] == "cache"
    assert result["data"] == mock_data
    mock_deps["scraper"].login.assert_not_called()
    mock_deps["scraper"].scrape_attendance.assert_not_called()

@pytest.mark.asyncio
async def test_scraper_failure_triggers_stale_db_fallback(mock_deps):
    # Arrange
    student_id = "TEST123"
    creds = {"username": "u", "password": "p"}

    mock_deps["cache"].get.return_value = None
    mock_deps["scraper"].login.side_effect = PortalTimeoutError("Timeout")

    # Mock DB result
    mock_record = MagicMock()
    mock_record.student_id = student_id
    mock_record.subject_name = "Math"
    mock_record.total_conducted = 10
    mock_record.total_attended = 8
    mock_record.percentage = 80.0
    mock_record.last_synced_at.isoformat.return_value = "2026-01-01T00:00:00"

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_record]
    mock_session.execute.return_value = mock_result
    mock_deps["db_session_factory"].return_value.__aenter__.return_value = mock_session

    orchestrator = AcademicOrchestrator(
        mock_deps["scraper"],
        mock_deps["cache"],
        mock_deps["db_session_factory"]
    )

    # Act
    result = await orchestrator.get_attendance(student_id, creds)

    # Assert
    assert result["source"] == "database"
    assert result["stale"] is True
    assert len(result["data"]) == 1
    assert result["data"][0]["subject_name"] == "Math"

def test_rate_limiter_triggers_429():
    client = TestClient(app)
    payload = {"username": "test", "password": "test"}

    # Send requests rapidly.
    # Note: The default is "10/minute". 11th should fail.
    for _ in range(10):
        client.post("/api/v1/academic/attendance/S123", json=payload)

    response = client.post("/api/v1/academic/attendance/S123", json=payload)

    assert response.status_code == 429
    assert response.json()["error"] == "Too Many Requests"
