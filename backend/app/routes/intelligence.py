from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..cache import RedisCache
from ..dependencies.auth import get_cache, get_current_user, get_db_session
from ..models.auth import User
from ..schemas.intelligence import CommuteCheckResponse
from ..services.intelligence_service import IntelligenceService

router = APIRouter(prefix="/api/v1/intelligence", tags=["Intelligence & Commute Decision Engine"])


@router.get(
    "/commute-check",
    response_model=CommuteCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate commute, schedule, and attendance risk",
    description="Deterministic cross-domain decision engine combining real-time trains, upcoming class/shift, and attendance standing.",
)
async def get_commute_check(
    from_station: str = Query(..., description="Origin commuter station (e.g., Thane, TNA, Kalyan, CSMT)"),
    at_time: Optional[str] = Query(None, description="Optional time override in HH:MM:SS format"),
    arrival_buffer_minutes: int = Query(10, ge=0, le=60, description="Arrival buffer required before class/shift"),
    last_mile_minutes: int = Query(5, ge=0, le=60, description="Walking/transfer buffer from destination station"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    cache: RedisCache = Depends(get_cache),
) -> CommuteCheckResponse:
    """
    Evaluates current commute feasibility against user's next schedule occurrence and attendance deficit risk.
    """
    return await IntelligenceService.evaluate_commute_check(
        db=db,
        user=current_user,
        from_station=from_station,
        at_time=at_time,
        arrival_buffer_minutes=arrival_buffer_minutes,
        last_mile_minutes=last_mile_minutes,
        cache=cache,
    )
