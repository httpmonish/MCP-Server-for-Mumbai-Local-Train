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
    async with async_session_factory() as session:
        yield session

@router.get("/next")
async def get_next_trains(
    from_station: str = Query(..., min_length=2, max_length=50),
    to_station: str = Query(..., min_length=2, max_length=50),
    time_str: Optional[str] = Query(None, alias="time"),
    limit: int = Query(5, ge=1, le=20),
    cache: RedisCache = Depends(get_cache),
    db_session = Depends(get_db_session)
):
    if from_station.lower() == to_station.lower():
        raise HTTPException(status_code=400, detail="Source and destination stations must be different")

    # Parse time
    if time_str:
        try:
            # Handle HH:MM or HH:MM:SS
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
        limit=limit
    )

    return {
        "source": from_station,
        "destination": to_station,
        "queried_at": query_time.strftime("%H:%M:%S"),
        "count": len(result["data"]),
        "trains": result["data"]
    }

# Adding missing import for Depends
