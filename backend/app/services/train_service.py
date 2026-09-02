from datetime import datetime, time
from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from ..cache import RedisCache
from ..models.train import TrainSchedule


async def bulk_import_schedules(db_session, train_records: List[Dict[str, Any]]) -> int:
    if not train_records:
        return 0

    # Using on_conflict_do_nothing as specified
    stmt = insert(TrainSchedule).values(train_records)
    stmt = stmt.on_conflict_do_nothing(constraint="uq_line_train_departure")

    result = await db_session.execute(stmt)
    await db_session.commit()
    return result.rowcount

async def get_next_trains(db_session, cache: RedisCache, source: str, destination: str, query_time: time, limit: int = 5) -> Dict[str, Any]:
    # 1. Cache Key Construction
    # Round query_time to 10-minute intervals
    slot_index = query_time.minute // 10
    cache_key = f"trains:{source.upper()}:{destination.upper()}:{query_time.hour}:{slot_index}"

    cached_result = await cache.get(cache_key)
    if cached_result:
        return {"data": cached_result, "source": "cache"}

    # 2. Database Query
    # We search for trains that depart from source AFTER query_time
    # and contain both source and destination stations.

    # Base query
    stmt = select(TrainSchedule).where(
        TrainSchedule.departure_time >= query_time
    ).order_by(TrainSchedule.departure_time.asc())

    result = await db_session.execute(stmt)
    all_trains = result.scalars().all()

    matching_trains = []
    for train in all_trains:
        # Safety check: Ensure departure time is still valid
        if train.departure_time < query_time:
            continue

        # Filter by stops_data
        source_stop = next((s for s in train.stops_data if s["station_name"].lower() == source.lower() or s["station_code"].upper() == source.upper()), None)
        dest_stop = next((s for s in train.stops_data if s["station_name"].lower() == destination.lower() or s["station_code"].upper() == destination.upper()), None)

        if source_stop and dest_stop:
            # Ensure source comes before destination (Directional Validation)
            if source_stop["seq"] < dest_stop["seq"]:

                # Calculate travel time
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
                    "travel_time_minutes": int(duration)
                })

        if len(matching_trains) >= limit:
            break

    # 3. Cache Populate
    await cache.set(cache_key, matching_trains, 43200) # 12 Hours

    return {"data": matching_trains, "source": "database"}


class TrainService:
    get_next_trains = staticmethod(get_next_trains)
    bulk_import_schedules = staticmethod(bulk_import_schedules)

