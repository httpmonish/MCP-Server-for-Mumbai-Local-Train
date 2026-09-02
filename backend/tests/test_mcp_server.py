import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.app.core.config import settings
from backend.mcp_server.server import call_tool_handler, list_tools_handler
from backend.mcp_server.tools import handle_get_attendance, handle_get_next_train, handle_get_upcoming_exams


class MockRequest:
    def __init__(self, params):
        self.params = params

@pytest.mark.asyncio
async def test_list_tools_schema():
    # call the handler directly
    tools = await list_tools_handler(None)
    assert len(tools) == 3
    tool_names = [t.name for t in tools]
    assert "get_student_attendance" in tool_names
    assert "get_upcoming_exams" in tool_names
    assert "get_next_train" in tool_names

    # Validate schema for one
    attendance_tool = next(t for t in tools if t.name == "get_student_attendance")
    assert "student_id" in attendance_tool.input_schema["properties"]
    assert "student_id" in attendance_tool.input_schema["required"]

@pytest.mark.asyncio
async def test_call_tool_attendance_formatting():
    # Mock the orchestrator result
    mock_result = {
        "data": [
            {"subject_name": "Math", "total_conducted": 10, "total_attended": 7, "percentage": 70.0},
            {"subject_name": "Physics", "total_conducted": 10, "total_attended": 9, "percentage": 90.0},
        ],
        "source": "live",
        "stale": False
    }

    with patch("backend.mcp_server.tools.get_orchestrator", new_callable=AsyncMock) as mock_get_orch:
        mock_orch = AsyncMock()
        mock_orch.get_attendance.return_value = mock_result
        mock_get_orch.return_value = mock_orch

        # Simulate a request
        req = MockRequest({"name": "get_student_attendance", "arguments": {"student_id": "241635", "username": "u", "password": "p"}})
        result = await call_tool_handler(req)
        text = result[0].text
        assert "CRITICAL WARNING (<75%)" in text
        assert "GOOD" in text
        assert "Math" in text

@pytest.mark.asyncio
async def test_call_tool_trains_empty():
    with patch("backend.app.services.train_service.get_next_trains", new_callable=AsyncMock) as mock_get_trains:
        mock_get_trains.return_value = {"data": [], "source": "database"}

        # Simulate a request
        req = MockRequest({"name": "get_next_train", "arguments": {"source": "Thane", "destination": "Byculla"}})
        result = await call_tool_handler(req)
        text = result[0].text
        assert "No upcoming suburban trains found" in text

@pytest.mark.asyncio
async def test_call_tool_unknown_name_error():
    # Simulate a request with unknown tool name
    req = MockRequest({"name": "non_existent_tool", "arguments": {}})
    result = await call_tool_handler(req)
    text = result[0].text
    assert "Tool Execution Error" in text
    assert "Unknown tool" in text
