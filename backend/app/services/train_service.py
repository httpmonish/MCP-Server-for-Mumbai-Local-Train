from datetime import datetime, time
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from ..cache import RedisCache
from ..core.logger import get_logger
from ..models.train import TrainSchedule
from .mumbai_local_data import (
    MASTER_SCHEDULES,
    detect_line_for_stations,
    get_all_lines,
    get_network_health,
    get_stations_for_line,
    match_station,
)

logger = get_logger(__name__)


async def bulk_import_schedules(db_session, train_records: List[Dict[str, Any]]) -> int:
    if not train_records:
        return 0

    stmt = insert(TrainSchedule).values(train_records)
    stmt = stmt.on_conflict_do_nothing(constraint="uq_line_train_departure")

    result = await db_session.execute(stmt)
    await db_session.commit()
    return result.rowcount


async def get_next_trains(
    db_session,
    cache: RedisCache,
    source: str,
    destination: str,
    query_time: time,
    limit: int = 5,
    line: Optional[str] = None,
    train_type: Optional[str] = None,
) -> Dict[str, Any]:
    # 1. Detect corridor line if not explicitly supplied
    detected_line = detect_line_for_stations(source, destination, line)

    # 2. Cache Key Construction
    slot_index = query_time.minute // 10
    cache_key = f"trains:{line or detected_line}:{source.upper()}:{destination.upper()}:{query_time.hour}:{slot_index}"

    if cache:
        try:
            cached_result = await cache.get(cache_key)
            if cached_result:
                return {"data": cached_result, "source": "cache", "line": detected_line}
        except Exception as e:
            logger.debug(f"Cache lookup failed: {e}")

    # 3. Try Database Query if session is healthy
    all_trains = []
    if db_session:
        try:
            stmt = select(TrainSchedule).where(
                TrainSchedule.departure_time >= query_time
            ).order_by(TrainSchedule.departure_time.asc())
            result = await db_session.execute(stmt)
            all_trains = result.scalars().all()
        except Exception as e:
            logger.info(f"Database query skipped or failed ({e}); falling back to local multi-line engine")
            all_trains = []

    matching_trains = []

    # If DB returned records, parse them
    if all_trains:
        for train in all_trains:
            if train.departure_time < query_time:
                continue

            # Check line if filtered
            if line and line.upper() != "ALL" and getattr(train, "line", "") != line.upper():
                continue

            stops = getattr(train, "stops_data", [])
            source_stop = next(
                (s for s in stops if match_station(s, source) or s.get("station_name", "").lower() == source.lower() or s.get("station_code", "").upper() == source.upper()),
                None
            )
            dest_stop = next(
                (s for s in stops if match_station(s, destination) or s.get("station_name", "").lower() == destination.lower() or s.get("station_code", "").upper() == destination.upper()),
                None
            )

            if source_stop and dest_stop and source_stop["seq"] < dest_stop["seq"]:
                fmt = "%H:%M:%S"
                t1 = datetime.strptime(source_stop["time"], fmt)
                t2 = datetime.strptime(dest_stop["time"], fmt)
                duration = (t2 - t1).total_seconds() / 60

                matching_trains.append({
                    "train_number": train.train_number,
                    "line": train.line,
                    "train_type": train.train_type,
                    "departure_from_source": source_stop["time"],
                    "arrival_at_destination": dest_stop["time"],
                    "travel_time_minutes": int(duration),
                    "platform": getattr(train, "platform", "PF 1"),
                    "crowd_level": getattr(train, "crowd_level", "Moderate"),
                })

            if len(matching_trains) >= limit:
                break

    # 4. If DB had no records at all (offline or local dev), query MASTER_SCHEDULES
    if not all_trains:
        q_str = query_time.strftime("%H:%M:%S")

        target_line = line.upper() if (line and line.upper() != "ALL") else (detected_line or "CR")

        for sched in MASTER_SCHEDULES:
            if target_line and sched["line"] != target_line and target_line != "ALL":
                continue

            if train_type and train_type.upper() != "ALL":
                if train_type.upper() not in sched["train_type"]:
                    continue

            stops = sched["stops_data"]
            source_stop = next((s for s in stops if match_station(s, source)), None)
            dest_stop = next((s for s in stops if match_station(s, destination)), None)

            if source_stop and dest_stop and source_stop["seq"] < dest_stop["seq"]:
                # Ensure departure from source is >= query_time
                if source_stop["time"] < q_str:
                    continue

                fmt = "%H:%M:%S"
                t1 = datetime.strptime(source_stop["time"], fmt)
                t2 = datetime.strptime(dest_stop["time"], fmt)
                duration = max(1, int((t2 - t1).total_seconds() / 60))

                matching_trains.append({
                    "train_number": sched["train_number"],
                    "line": sched["line"],
                    "line_name": sched.get("line_name", f"{sched['line']} Line"),
                    "train_type": sched["train_type"],
                    "departure_from_source": source_stop["time"],
                    "arrival_at_destination": dest_stop["time"],
                    "travel_time_minutes": duration,
                    "platform": sched.get("platform", "PF 2"),
                    "crowd_level": sched.get("crowd_level", "Moderate"),
                    "source_terminal": sched["source_station"],
                    "dest_terminal": sched["destination_station"],
                })

            if len(matching_trains) >= limit:
                break

    # 5. Populate cache if available
    if cache and matching_trains:
        try:
            await cache.set(cache_key, matching_trains, 43200)
        except Exception:
            pass

    return {
        "data": matching_trains,
        "source": "database" if (all_trains and matching_trains) else "live_network_schedule",
        "line": detected_line,
    }


def get_lines_info() -> List[Dict[str, Any]]:
    return get_all_lines()


def get_stations_info(line: Optional[str] = None) -> List[Dict[str, Any]]:
    return get_stations_for_line(line)


def get_network_status_info() -> Dict[str, Any]:
    return get_network_health()


class TrainService:
    get_next_trains = staticmethod(get_next_trains)
    bulk_import_schedules = staticmethod(bulk_import_schedules)
    get_lines_info = staticmethod(get_lines_info)
    get_stations_info = staticmethod(get_stations_info)
    get_network_status_info = staticmethod(get_network_status_info)

