import json
from typing import Any, Dict, List

import ollama

from ..core.logger import get_logger
from ..mcp_server.tools import (
    handle_get_attendance,
    handle_get_next_train,
    handle_get_upcoming_exams,
)

logger = get_logger(__name__)

LOCAL_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_student_attendance",
            "description": "Fetch real-time lecture attendance records and threshold warnings for a student.",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_id": {"type": "string", "description": "Student roll or enrollment ID"},
                    "username": {"type": "string", "description": "Portal username (optional)"},
                    "password": {"type": "string", "description": "Portal password (optional)"},
                },
                "required": ["student_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_upcoming_exams",
            "description": "Retrieve the scheduled examination timetable, dates, slots, and exam classrooms.",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_id": {"type": "string", "description": "Student roll or enrollment ID"},
                    "username": {"type": "string", "description": "Portal username (optional)"},
                    "password": {"type": "string", "description": "Portal password (optional)"},
                },
                "required": ["student_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_next_train",
            "description": "Query next upcoming Mumbai suburban trains between two stations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "from_station": {"type": "string", "description": "Departure station (e.g. Thane, CSMT)"},
                    "to_station": {"type": "string", "description": "Destination station (e.g. Byculla, Dadar)"},
                    "time": {"type": "string", "description": "Query time in HH:MM format (optional)"},
                },
                "required": ["from_station", "to_station"],
            },
        },
    },
]


class LocalEdgeAIGateway:
    def __init__(self, model_name: str = "llama3.2:3b", host: str = "http://localhost:11434"):
        self.model_name = model_name
        self.host = host
        self.client = ollama.AsyncClient(host=host)

    async def execute_tool(self, tool_name: str, args: Dict[str, Any], context_credentials: Dict[str, str]) -> str:
        """Execute local MCP tools based on function name."""
        merged_args = {**args}
        if "username" not in merged_args and "username" in context_credentials:
            merged_args["username"] = context_credentials["username"]
        if "password" not in merged_args and "password" in context_credentials:
            merged_args["password"] = context_credentials["password"]

        if tool_name == "get_student_attendance":
            return await handle_get_attendance(merged_args)
        elif tool_name == "get_upcoming_exams":
            return await handle_get_upcoming_exams(merged_args)
        elif tool_name == "get_next_train":
            return await handle_get_next_train(merged_args)
        else:
            return f"Error: Unknown tool function '{tool_name}'"

    async def chat_with_tools(self, prompt: str, student_id: str, context_credentials: Dict[str, str]) -> str:
        messages: List[Dict[str, Any]] = [
            {
                "role": "system",
                "content": (
                    "You are the Campus & Commute AI Assistant running at the local edge. "
                    "Use available tool calls to answer academic and suburban transit queries."
                ),
            },
            {"role": "user", "content": prompt},
        ]

        try:
            # 1. First invocation to detect tool calls
            response = await self.client.chat(
                model=self.model_name,
                messages=messages,
                tools=LOCAL_TOOLS_SCHEMA,
            )

            message = response.get("message", {})
            tool_calls = message.get("tool_calls", [])

            if not tool_calls:
                return message.get("content", "No response generated.")

            messages.append(message)

            # 2. Execute tool calls locally
            for call in tool_calls:
                function_info = call.get("function", {})
                func_name = function_info.get("name", "")
                raw_args = function_info.get("arguments", {})

                if isinstance(raw_args, str):
                    try:
                        parsed_args = json.loads(raw_args)
                    except json.JSONDecodeError:
                        parsed_args = {}
                else:
                    parsed_args = raw_args

                if "student_id" not in parsed_args and student_id:
                    parsed_args["student_id"] = student_id

                tool_result = await self.execute_tool(func_name, parsed_args, context_credentials)

                messages.append({
                    "role": "tool",
                    "content": tool_result,
                })

            # 3. Final synthesis
            final_response = await self.client.chat(
                model=self.model_name,
                messages=messages,
            )
            return final_response.get("message", {}).get("content", "Failed synthesizing tool results.")

        except Exception as exc:
            logger.warning(f"Local Ollama inference daemon unavailable at {self.host}: {exc}")
            return (
                f"⚠️ *Local SLM Gateway Offline*\n\n"
                f"Could not connect to Ollama daemon on `{self.host}` (`{self.model_name}`). "
                f"Falling back to direct Model Context Protocol or REST API."
            )
