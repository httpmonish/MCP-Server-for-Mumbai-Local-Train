import asyncio
from typing import Any

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from .config import mcp_settings
from .tools import handle_get_attendance, handle_get_next_train, handle_get_upcoming_exams

app = Server(mcp_settings.MCP_SERVER_NAME)

async def list_tools_handler(request):
    return [
        types.Tool(
            name="get_student_attendance",
            description="Retrieve current subject-wise lecture attendance percentages and low-attendance warnings for a student.",
            input_schema={
                "type": "object",
                "properties": {
                    "student_id": {"type": "string", "description": "Student enrollment / roll number."},
                    "username": {"type": "string", "description": "Portal login username."},
                    "password": {"type": "string", "description": "Portal login password."},
                },
                "required": ["student_id"],
            },
        ),
        types.Tool(
            name="get_upcoming_exams",
            description="Fetch the upcoming examination dates, time slots, and classroom venues for a student.",
            input_schema={
                "type": "object",
                "properties": {
                    "student_id": {"type": "string", "description": "Student enrollment / roll number."},
                    "username": {"type": "string", "description": "Portal login username."},
                    "password": {"type": "string", "description": "Portal login password."},
                },
                "required": ["student_id"],
            },
        ),
        types.Tool(
            name="get_next_train",
            description="Look up upcoming suburban local trains operating between two railway stations with departure times and Fast/Slow service classification.",
            input_schema={
                "type": "object",
                "properties": {
                    "source": {"type": "string", "description": "Departure railway station name or station code (e.g. Thane, TNA)."},
                    "destination": {"type": "string", "description": "Arrival railway station name or station code (e.g. Byculla, BY)."},
                    "query_time": {"type": "string", "description": "Query time in HH:MM:SS format (defaults to current time)."},
                    "limit": {"type": "integer", "description": "Number of upcoming trains to return.", "default": 5},
                },
                "required": ["source", "destination"],
            },
        ),
    ]

async def call_tool_handler(request):
    # In MCP SDK, request.params usually contains the name and arguments
    params = request.params
    name = params.get("name")
    arguments = params.get("arguments", {})

    try:
        if name == "get_student_attendance":
            result_string = await handle_get_attendance(
                student_id=arguments.get("student_id"),
                username=arguments.get("username"),
                password=arguments.get("password"),
            )
        elif name == "get_upcoming_exams":
            result_string = await handle_get_upcoming_exams(
                student_id=arguments.get("student_id"),
                username=arguments.get("username"),
                password=arguments.get("password"),
            )
        elif name == "get_next_train":
            result_string = await handle_get_next_train(
                source=arguments.get("source"),
                destination=arguments.get("destination"),
                query_time=arguments.get("query_time"),
                limit=arguments.get("limit", 5),
            )
        else:
            return [types.TextContent(type="text", text=f"Tool Execution Error: Unknown tool {name}")]

        return [types.TextContent(type="text", text=result_string)]

    except Exception as err:
        return [types.TextContent(type="text", text=f"Tool Execution Error: {str(err)}")]

# Correctly register handlers using the Server.add_request_handler method
# Signature: (self, method, params_type, handler)
app.add_request_handler("list_tools", Any, list_tools_handler)
app.add_request_handler("call_tool", Any, call_tool_handler)

async def _app_list_tools():
    return await list_tools_handler(None)

app.list_tools = _app_list_tools


async def run_mcp():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        init_options = InitializationOptions(
            server_name=mcp_settings.MCP_SERVER_NAME,
            server_version=mcp_settings.MCP_SERVER_VERSION,
            capabilities=app.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={},
            ),
        )
        await app.run(read_stream, write_stream, init_options)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_mcp())
