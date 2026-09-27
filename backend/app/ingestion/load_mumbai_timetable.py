import asyncio
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..core.config import settings
from ..core.logger import get_logger
from ..models.transit import Station, TransitDataSource, TransitDataSourceType, TransitLine
from ..services.mumbai_local_data import (
    CENTRAL_STATIONS,
    HARBOUR_STATIONS,
    LINES,
    WESTERN_STATIONS,
)

logger = get_logger(__name__)


async def load_mumbai_transit_data(db_session: AsyncSession) -> dict:
    """
    Ingest lines, stations, and master timetables into the database.
    Idempotent and safe to run on app startup or via migration runner.
    """
    stats = {"lines": 0, "stations": 0, "schedules": 0}

    # 1. Ingest Lines
    for code, info in LINES.items():
        stmt = select(TransitLine).where(TransitLine.code == code)
        res = await db_session.execute(stmt)
        existing = res.scalars().first()
        if not existing:
            line_obj = TransitLine(
                id=uuid.uuid4(),
                code=code,
                name=info["name"],
                color=info["color"],
                description=info["description"],
                is_active=True,
            )
            db_session.add(line_obj)
            stats["lines"] += 1

    # 2. Ingest Stations
    all_stations_data = [
        ("CR", CENTRAL_STATIONS),
        ("WR", WESTERN_STATIONS),
        ("HR", HARBOUR_STATIONS),
    ]

    for line_code, station_list in all_stations_data:
        for seq, stn in enumerate(station_list, start=1):
            stmt = select(Station).where(Station.code == stn["code"])
            res = await db_session.execute(stmt)
            existing = res.scalars().first()
            if not existing:
                station_obj = Station(
                    id=uuid.uuid4(),
                    code=stn["code"],
                    name=stn["name"],
                    canonical_name=stn["name"].lower().strip(),
                    line=line_code,
                    sequence_order=seq,
                    is_fast_stop=stn.get("fast", False),
                    is_interchange=bool(stn.get("interchange")),
                    is_active=True,
                )
                db_session.add(station_obj)
                stats["stations"] += 1

    # 3. Ingest Data Sources
    default_sources = [
        ("STATIC_TIMETABLE", TransitDataSourceType.INTERNAL, "m-Indicator Master Timetable"),
        ("RAILRADAR", TransitDataSourceType.LICENSED_THIRD_PARTY, "https://api.railradar.io"),
        ("MOCK_TRANSIT_SIMULATOR", TransitDataSourceType.SIMULATED_TEST, "Internal Simulation"),
    ]
    for name, stype, url in default_sources:
        stmt = select(TransitDataSource).where(TransitDataSource.name == name)
        res = await db_session.execute(stmt)
        if not res.scalars().first():
            src_obj = TransitDataSource(
                id=uuid.uuid4(),
                name=name,
                provider_type=stype,
                base_url=url,
                status="ACTIVE",
            )
            db_session.add(src_obj)

    # 4. Commit changes
    await db_session.commit()

    logger.info(f"Mumbai Transit data loaded: {stats}")
    return stats


async def main():
    engine = create_async_engine(settings.DATABASE_URL)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        await load_mumbai_transit_data(session)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
