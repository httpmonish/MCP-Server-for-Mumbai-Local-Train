import hashlib
from typing import Any, Dict

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from pydantic import BaseModel, Field
from sqlalchemy import select

from ..cache import RedisCache
from ..core.config import settings
from ..core.logger import get_logger
from ..models.transit_delay import TrainDelayReport
from ..services.delay_consensus import DelayConsensusEngine
from ..services.websocket_manager import TransitConnectionManager

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/delays", tags=["Transit Delays"])

ws_manager = TransitConnectionManager(settings.REDIS_URL)
consensus_engine = DelayConsensusEngine()


async def get_cache() -> RedisCache:
    from ..main import cache

    return cache


async def get_db_session():
    from ..main import async_session_factory

    async with async_session_factory() as session:
        yield session


class DelayReportRequest(BaseModel):
    train_number: str
    station_code: str
    reported_delay_minutes: int = Field(ge=-5, le=120)
    student_id: str
    corridor: str = "CR"  # "CR" or "WR"


@router.post("/report")
async def report_delay(
    req: DelayReportRequest,
    cache: RedisCache = Depends(get_cache),
    db_session=Depends(get_db_session),
) -> Dict[str, Any]:
    # 1. Anonymize reporter
    reporter_hash = hashlib.sha256(req.student_id.encode("utf-8")).hexdigest()

    # 2. Anti-spam rate limiting: 10 minutes per reporter per train
    rate_key = f"rate:report:{reporter_hash}:{req.train_number}"
    existing_report = await cache.get(rate_key)
    if existing_report:
        raise HTTPException(
            status_code=429,
            detail="A report for this train was already submitted recently. Please wait 10 minutes.",
        )

    # 3. Persist delay report
    report = TrainDelayReport(
        train_number=req.train_number,
        station_code=req.station_code,
        reported_delay_minutes=req.reported_delay_minutes,
        reporter_id_hash=reporter_hash,
    )
    db_session.add(report)
    await db_session.commit()

    # Set anti-spam lock
    await cache.set(rate_key, {"reported": True}, 600)

    # 4. Recalculate consensus
    stmt = select(TrainDelayReport).where(
        TrainDelayReport.train_number == req.train_number,
        TrainDelayReport.is_active.is_(True),
    )
    result = await db_session.execute(stmt)
    active_reports = result.scalars().all()

    consensus_data = consensus_engine.calculate_weighted_delay(active_reports)

    # 5. Broadcast real-time event
    delay_event = {
        "event_type": "DELAY_UPDATE",
        "train_number": req.train_number,
        "station_code": req.station_code,
        "corridor": req.corridor,
        "consensus": consensus_data,
    }
    await ws_manager.publish_delay_event(req.corridor, delay_event)

    return {
        "status": "recorded",
        "current_consensus": consensus_data,
    }


@router.websocket("/ws/transit/{corridor}")
async def websocket_transit_stream(websocket: WebSocket, corridor: str):
    corridor_key = corridor.upper()
    await ws_manager.connect(corridor_key, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            if data.strip().lower() == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await ws_manager.disconnect(corridor_key, websocket)
    except Exception as exc:
        logger.debug(f"WebSocket connection error on {corridor_key}: {exc}")
        await ws_manager.disconnect(corridor_key, websocket)
