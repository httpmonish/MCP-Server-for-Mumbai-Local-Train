import asyncio
import logging
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from ..app.core.config import settings
from ..app.models.academic import Base as AcademicBase
from ..app.models.train import Base as TrainBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("migration")

async def migrate():
    try:
        logger.info(f"Initializing migration against: {settings.DATABASE_URL}")
        engine = create_async_engine(settings.DATABASE_URL)

        async with engine.begin() as conn:
            # Create all tables
            # Since AcademicBase and TrainBase might share the same Base if implemented correctly,
            # but in our files they are separate Base = declarative_base() calls.
            # We need to run both.
            await conn.run_sync(AcademicBase.metadata.create_all)
            await conn.run_sync(TrainBase.metadata.create_all)

            # Verify tables exist
            tables_to_verify = ['attendance_records', 'exam_timetables', 'train_schedules']
            for table in tables_to_verify:
                res = await conn.execute(text(f"SELECT 1 FROM information_schema.tables WHERE table_name = '{table}'"))
                if not res.scalar():
                    logger.error(f"Table {table} was not created successfully.")
                    sys.exit(1)
                logger.info(f"Verified table: {table}")

        logger.info("Database migration completed successfully.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(migrate())
