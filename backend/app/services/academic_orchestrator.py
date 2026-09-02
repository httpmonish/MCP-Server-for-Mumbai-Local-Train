import asyncio
from typing import Any, Dict

from fastapi import HTTPException
from sqlalchemy import select

from ..cache import RedisCache
from ..core.config import settings
from ..core.logger import get_logger
from ..models.academic import AttendanceRecord, ExamTimetable
from ..scrapers.college_portal import CollegePortalScraper
from ..scrapers.exceptions import PortalSelectorError, PortalTimeoutError
from . import academic_service

logger = get_logger(__name__)

class AcademicOrchestrator:
    def __init__(self, scraper: CollegePortalScraper, cache: RedisCache, db_session_factory):
        self.scraper = scraper
        self.cache = cache
        self.db_session_factory = db_session_factory
        self.semaphore = asyncio.Semaphore(settings.SCRAPER_MAX_CONCURRENCY)

    async def get_attendance(self, student_id: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        # 1. Cache-Aside Check
        cache_key = f"attendance:{student_id}"
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            return {"data": cached_data, "source": "cache", "stale": False}

        # 2. Scraping with Concurrency Throttling
        async with self.semaphore:
            try:
                # Note: In a real app, the 'page' object would be managed by a browser context
                # For this implementation, we assume the scraper handles the session or we provide it
                # Since the spec says "Initialize Playwright context", we'll mock the process
                # of using a context for this orchestrator.

                from playwright.async_api import async_playwright
                async with async_playwright() as p:
                    browser = await p.chromium.launch()
                    page = await browser.new_page()
                    try:
                        await self.scraper.login(page, credentials["username"], credentials["password"])
                        scraped_data = await self.scraper.scrape_attendance(page)

                        # Persistence
                        async with self.db_session_factory() as db_session:
                            await academic_service.upsert_attendance(db_session, student_id, scraped_data)

                        # Caching
                        await self.cache.set(cache_key, scraped_data, settings.TTL_ATTENDANCE)

                        return {"data": scraped_data, "source": "live", "stale": False}
                    finally:
                        await browser.close()

            except (PortalTimeoutError, PortalSelectorError, Exception) as e:
                logger.warning(f"Live scraper failed for student {student_id}, attempting DB fallback. Error: {e}")

                # DB Fallback
                records = await self._query_db_attendance(student_id)
                if records:
                    first = records[0]
                    last_synced = (
                        first.get("last_synced_at", "Unknown")
                        if isinstance(first, dict)
                        else (
                            first.last_synced_at.isoformat()
                            if hasattr(first.last_synced_at, "isoformat")
                            else str(first.last_synced_at)
                        )
                    )
                    return {
                        "data": records,
                        "source": "database",
                        "stale": True,
                        "last_synced_at": last_synced,
                    }

                raise HTTPException(
                    status_code=503,
                    detail="Portal unreachable and no cached records available"
                )

    async def _query_db_attendance(self, student_id: str):
        async with self.db_session_factory() as db_session:
            result = await db_session.execute(
                select(AttendanceRecord).where(AttendanceRecord.student_id == student_id)
            )
            records = result.scalars().all()
            if records:
                return [
                    {
                        "subject_name": r.subject_name,
                        "total_conducted": r.total_conducted,
                        "total_attended": r.total_attended,
                        "percentage": r.percentage,
                        "last_synced_at": (
                            r.last_synced_at.isoformat()
                            if hasattr(r.last_synced_at, "isoformat")
                            else str(r.last_synced_at)
                        ),
                    }
                    for r in records
                ]
            return []

    async def get_exams(self, student_id: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        cache_key = f"exams:{student_id}"
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            return {"data": cached_data, "source": "cache", "stale": False}

        async with self.semaphore:
            try:
                from playwright.async_api import async_playwright
                async with async_playwright() as p:
                    browser = await p.chromium.launch()
                    page = await browser.new_page()
                    try:
                        await self.scraper.login(page, credentials["username"], credentials["password"])
                        scraped_data = await self.scraper.scrape_exam_timetable(page)

                        async with self.db_session_factory() as db_session:
                            await academic_service.upsert_exams(db_session, student_id, scraped_data)

                        await self.cache.set(cache_key, scraped_data, settings.TTL_EXAMS)

                        return {"data": scraped_data, "source": "live", "stale": False}
                    finally:
                        await browser.close()

            except (PortalTimeoutError, PortalSelectorError, Exception) as e:
                logger.warning(f"Live scraper failed for student {student_id}, attempting DB fallback. Error: {e}")

                # DB Fallback
                records = await self._query_db_exams(student_id)
                if records:
                    first = records[0]
                    last_synced = (
                        first.get("last_synced_at", "Unknown")
                        if isinstance(first, dict)
                        else (
                            first.last_synced_at.isoformat()
                            if hasattr(first.last_synced_at, "isoformat")
                            else str(first.last_synced_at)
                        )
                    )
                    return {
                        "data": records,
                        "source": "database",
                        "stale": True,
                        "last_synced_at": last_synced,
                    }

                raise HTTPException(
                    status_code=503,
                    detail="Portal unreachable and no cached records available"
                )

    async def _query_db_exams(self, student_id: str):
        async with self.db_session_factory() as db_session:
            result = await db_session.execute(
                select(ExamTimetable).where(ExamTimetable.student_id == student_id)
            )
            records = result.scalars().all()
            if records:
                return [
                    {
                        "subject_name": r.subject_name,
                        "exam_date": r.exam_date,
                        "time_slot": r.time_slot,
                        "classroom": r.classroom,
                        "last_synced_at": (
                            r.last_synced_at.isoformat()
                            if hasattr(r.last_synced_at, "isoformat")
                            else str(r.last_synced_at)
                        ),
                    }
                    for r in records
                ]
            return []

