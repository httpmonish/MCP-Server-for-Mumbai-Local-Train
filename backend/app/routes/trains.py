from datetime import datetime, time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from ..cache import RedisCache
from ..services import train_service

router = APIRouter(prefix="/api/v1/trains", tags=["Trains"])


async def get_cache():
    from ..main import cache
    return cache


async def get_db_session():
    from ..main import async_session_factory
    try:
        async with async_session_factory() as session:
            yield session
    except Exception:
        yield None


@router.get("/lines")
async def get_lines():
    """Return all Mumbai Suburban Railway lines (Central, Western, Harbour)."""
    return {
        "lines": train_service.get_lines_info()
    }


@router.get("/stations")
async def get_stations(line: Optional[str] = Query(None, description="Line code: CR, WR, or HR")):
    """Return stations, optionally filtered by line corridor."""
    stations = train_service.get_stations_info(line)
    return {
        "line": line.upper() if line else "ALL",
        "count": len(stations),
        "stations": stations
    }


@router.get("/status")
async def get_network_status():
    """Return live status across Central, Western, and Harbour lines."""
    return train_service.get_network_status_info()


@router.get("/next")
async def get_next_trains(
    from_station: str = Query(..., min_length=2, max_length=50),
    to_station: str = Query(..., min_length=2, max_length=50),
    line: Optional[str] = Query(None, description="Corridor line: CR (Central), WR (Western), HR (Harbour), or ALL"),
    train_type: Optional[str] = Query(None, description="Filter: FAST, SLOW, AC, or ALL"),
    time_str: Optional[str] = Query(None, alias="time"),
    limit: int = Query(6, ge=1, le=20),
    cache: RedisCache = Depends(get_cache),
    db_session = Depends(get_db_session)
):
    if from_station.strip().lower() == to_station.strip().lower():
        raise HTTPException(status_code=400, detail="Source and destination stations must be different")

    # Parse time
    if time_str:
        try:
            if len(time_str.split(':')) == 2:
                h, m = map(int, time_str.split(':'))
                query_time = time(h, m)
            else:
                h, m, s = map(int, time_str.split(':'))
                query_time = time(h, m, s)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM or HH:MM:SS")
    else:
        query_time = datetime.now().time()

    result = await train_service.get_next_trains(
        db_session=db_session,
        cache=cache,
        source=from_station,
        destination=to_station,
        query_time=query_time,
        limit=limit,
        line=line,
        train_type=train_type
    )

    return {
        "source": from_station,
        "destination": to_station,
        "line": result.get("line"),
        "queried_at": query_time.strftime("%H:%M:%S"),
        "count": len(result["data"]),
        "trains": result["data"]
    }

