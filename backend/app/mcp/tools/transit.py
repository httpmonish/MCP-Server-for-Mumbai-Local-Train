from datetime import datetime, time, timezone
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo

from app.core.logger import get_logger
from app.services.transit_service import TransitEngineService

from ..errors import MCPErrorCode, MCPToolException

logger = get_logger(__name__)


async def handle_get_next_train(
    from_station: str,
    to_station: str,
    query_time: Optional[str] = None,
    limit: int = 5,
) -> Dict[str, Any]:
    """
    Execute get_next_train tool by delegating to Phase 3 TransitEngineService.
    Preserves data freshness, source labels, and bounded result counts.
    """
    if not from_station or not from_station.strip():
        raise MCPToolException(
            MCPErrorCode.INVALID_STATION,
            "Parameter 'from_station' is required and cannot be empty.",
        )
    if not to_station or not to_station.strip():
        raise MCPToolException(
            MCPErrorCode.INVALID_STATION,
            "Parameter 'to_station' is required and cannot be empty.",
        )

    # Sanitize input strings to prevent prompt injection / control character exploitation
    clean_from = from_station.strip().replace("\n", " ").replace("\r", " ")[:64]
    clean_to = to_station.strip().replace("\n", " ").replace("\r", " ")[:64]
    bounded_limit = max(1, min(limit, 10))

    try:
        user_tz = ZoneInfo("Asia/Kolkata")
    except Exception:
        user_tz = timezone.utc

    now_time = datetime.now(user_tz).time()
    parsed_query_time: time = now_time
    if query_time and query_time.strip():
        try:
            parts = [int(p) for p in query_time.strip().split(":")]
            parsed_query_time = time(parts[0], parts[1], parts[2] if len(parts) > 2 else 0)
        except Exception:
            raise MCPToolException(
                MCPErrorCode.INTERNAL_ERROR,
                f"Invalid time format for query_time '{query_time}'. Expected HH:MM:SS or HH:MM.",
            )

    try:
        transit_resp = await TransitEngineService.get_next_trains(
            from_stn=clean_from,
            to_stn=clean_to,
            query_time=parsed_query_time,
            limit=bounded_limit,
        )
    except Exception as e:
        logger.error(f"Transit service error in MCP tool: {e}", exc_info=True)
        raise MCPToolException(
            MCPErrorCode.INTERNAL_ERROR,
            f"Transit service error: {str(e)}",
        )

    formatted_trains = []
    for item in transit_resp.trains:
        formatted_trains.append({
            "train_number": item.train_number,
            "line": item.line,
            "line_name": item.line_name,
            "train_type": item.train_type,
            "scheduled_departure": item.departure_from_source,
            "scheduled_arrival": item.arrival_at_destination,
            "expected_departure": item.expected_departure,
            "delay_minutes": item.delay_minutes,
            "travel_time_minutes": item.travel_time_minutes,
            "platform": item.platform,
            "crowd_level": item.crowd_level,
            "data_label": item.data_label,
        })

    return {
        "from_station": clean_from,
        "to_station": clean_to,
        "total_trains": len(formatted_trains),
        "source": transit_resp.meta.source.value if hasattr(transit_resp.meta.source, "value") else str(transit_resp.meta.source),
        "freshness": transit_resp.meta.freshness.value if hasattr(transit_resp.meta.freshness, "value") else str(transit_resp.meta.freshness),
        "confidence": transit_resp.meta.confidence.value if hasattr(transit_resp.meta.confidence, "value") else str(transit_resp.meta.confidence),
        "trains": formatted_trains,
    }
