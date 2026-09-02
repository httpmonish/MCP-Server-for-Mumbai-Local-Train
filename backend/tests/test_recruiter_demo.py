from unittest.mock import AsyncMock, MagicMock

import pytest
from app.mcp_server.formatters import format_attendance_report, format_train_schedule
from app.scrapers.exceptions import PortalTimeoutError
from app.services.academic_orchestrator import AcademicOrchestrator


@pytest.mark.asyncio
async def test_full_degradation_pipeline_and_formatting():
    # 1. Setup mocks
    mock_scraper = MagicMock()
    mock_scraper.login = AsyncMock(side_effect=PortalTimeoutError("Portal offline"))
    mock_cache = MagicMock()
    mock_cache.get = AsyncMock(return_value=None)  # Cache miss

    # Mock historical database data
    mock_db = MagicMock()
    mock_record = MagicMock()
    mock_record.subject_name = "Advanced Computer Networks"
    mock_record.total_conducted = 40
    mock_record.total_attended = 28
    mock_record.percentage = 70.0
    mock_record.last_synced_at.isoformat.return_value = "2026-10-01T08:00:00Z"

    # 2. Test orchestrator fallback to DB
    orchestrator = AcademicOrchestrator(
        scraper=mock_scraper,
        cache=mock_cache,
        db_session_factory=lambda: mock_db,
    )
    orchestrator._query_db_attendance = AsyncMock(
        return_value=[
            {
                "subject_name": mock_record.subject_name,
                "total_conducted": mock_record.total_conducted,
                "total_attended": mock_record.total_attended,
                "percentage": mock_record.percentage,
                "last_synced_at": "2026-10-01T08:00:00Z",
            }
        ]
    )

    result = await orchestrator.get_attendance("241635", {"username": "u", "password": "p"})

    assert result["source"] == "database"
    assert result["stale"] is True

    # 3. Test MCP text output formatting with critical warning badge
    formatted_report = format_attendance_report("241635", result)
    assert "[WARNING: UPSTREAM PORTAL UNREACHABLE" in formatted_report
    assert "CRITICAL WARNING (<75%)" in formatted_report
    assert "Advanced Computer Networks" in formatted_report


def test_train_mcp_formatting():
    mock_trains = [
        {
            "train_number": "95701",
            "line": "CR",
            "train_type": "FAST",
            "departure_from_source": "08:22",
            "arrival_at_destination": "08:58",
            "travel_time_minutes": 36,
        }
    ]
    output = format_train_schedule("Thane", "Byculla", mock_trains)
    assert "| 95701 | CR | FAST | 08:22 | 08:58 | 36 mins |" in output
