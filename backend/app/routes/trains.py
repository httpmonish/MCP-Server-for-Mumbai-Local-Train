from datetime import datetime, time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..cache import RedisCache
from ..dependencies.auth import get_cache, get_db_session
from ..schemas.transit import (
    LiveTrainStateResponse,
    NextTrainsResponse,
    ScheduleResponse,
    StationBoardResponse,
    StationListResponse,
)
from ..services.transit_service import TransitEngineService

router = APIRouter(prefix="/api/v1/trains", tags=["Mumbai Transit Engine"])


@router.get(
    "/lines",
    summary="Get Mumbai suburban railway lines",
    description="Retrieve all suburban railway corridors (Central Line, Western Line, Harbour Line).",
)
async def get_lines():
    return {"lines": TransitEngineService.get_lines_info()}


@router.get(
    "/stations",
    response_model=StationListResponse,
    summary="Get Mumbai railway stations",
    description="Retrieve canonical station master list with line filtering and search capabilities.",
)
async def get_stations(
    line: Optional[str] = Query(None, description="Corridor line filter: CR, WR, or HR"),
    search: Optional[str] = Query(None, description="Search by station name or code (e.g. 'Thane', 'CSMT')"),
    db: AsyncSession = Depends(get_db_session),
) -> StationListResponse:
    stations = await TransitEngineService.get_stations_info(line=line, search=search, db=db)
    return StationListResponse(
        line=line.upper() if line else "ALL",
        count=len(stations),
        stations=stations,
    )


@router.get(
    "/next",
    response_model=NextTrainsResponse,
    summary="Get next upcoming trains",
    description="Calculate the next upcoming suburban trains between two stations with live delay enrichment.",
)
async def get_next_trains(
    from_station: str = Query(..., alias="from", min_length=2, max_length=50, description="Origin station name or code"),
    to_station: str = Query(..., alias="to", min_length=2, max_length=50, description="Destination station name or code"),
    line: Optional[str] = Query(None, description="Line corridor: CR, WR, HR, or ALL"),
    train_type: Optional[str] = Query(None, description="Filter: FAST, SLOW, or ALL"),
    time_str: Optional[str] = Query(None, alias="time", description="Query time (HH:MM or HH:MM:SS) in IST"),
    limit: int = Query(6, ge=1, le=20, description="Max trains to return"),
    include_live: bool = Query(True, description="Enrich results with live telemetry"),
    cache: RedisCache = Depends(get_cache),
) -> NextTrainsResponse:
    if time_str:
        try:
            parts = time_str.split(":")
            if len(parts) == 2:
                h, m = map(int, parts)
                query_time = time(h, m)
            else:
                h, m, s = map(int, parts)
                query_time = time(h, m, s)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM or HH:MM:SS")
    else:
        query_time = datetime.now().time()

    return await TransitEngineService.get_next_trains(
        from_stn=from_station,
        to_stn=to_station,
        query_time=query_time,
        line=line,
        train_type=train_type,
        limit=limit,
        include_live=include_live,
        cache=cache,
    )


@router.get(
    "/schedule",
    response_model=ScheduleResponse,
    summary="Get static timetable schedule",
    description="Retrieve full scheduled timetable between two stations.",
)
async def get_schedule(
    from_station: str = Query(..., alias="from", min_length=2, max_length=50, description="Origin station"),
    to_station: str = Query(..., alias="to", min_length=2, max_length=50, description="Destination station"),
    line: Optional[str] = Query(None, description="Corridor line code"),
) -> ScheduleResponse:
    return await TransitEngineService.get_schedule(
        from_stn=from_station,
        to_stn=to_station,
        line=line,
    )


@router.get(
    "/between",
    response_model=NextTrainsResponse,
    summary="Get trains running between stations",
    description="Query trains connecting two stations with live telemetry metadata.",
)
async def get_trains_between(
    from_station: str = Query(..., alias="from", min_length=2, max_length=50),
    to_station: str = Query(..., alias="to", min_length=2, max_length=50),
    include_live: bool = Query(True),
    cache: RedisCache = Depends(get_cache),
) -> NextTrainsResponse:
    now_time = datetime.now().time()
    return await TransitEngineService.get_next_trains(
        from_stn=from_station,
        to_stn=to_station,
        query_time=now_time,
        include_live=include_live,
        cache=cache,
    )


@router.get(
    "/{train_id}/live",
    response_model=LiveTrainStateResponse,
    summary="Get real-time train status",
    description="Retrieve live GPS position, current station, speed, and delay for a running train.",
)
async def get_live_train(
    train_id: str,
    cache: RedisCache = Depends(get_cache),
) -> LiveTrainStateResponse:
    return await TransitEngineService.get_live_train(train_number=train_id, cache=cache)


@router.get(
    "/stations/{station_code}/live",
    response_model=StationBoardResponse,
    summary="Get live station arrival/departure board",
    description="Retrieve real-time electronic indicator board for a station.",
)
async def get_station_live_board(
    station_code: str,
    cache: RedisCache = Depends(get_cache),
) -> StationBoardResponse:
    return await TransitEngineService.get_station_board(station_code=station_code, cache=cache)
