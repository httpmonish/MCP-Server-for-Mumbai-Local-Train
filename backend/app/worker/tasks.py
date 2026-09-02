from datetime import datetime, time
from typing import List, Optional, Tuple

from arq import Retry
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from ..cache import RedisCache
from ..core.config import settings
from ..core.logger import get_logger
from ..scrapers.college_portal import CollegePortalScraper
from ..services.academic_orchestrator import AcademicOrchestrator
from ..services.alert_service import AlertDispatcher
from ..services.decision_engine import CommuteDecisionEngine
from ..services.train_service import TrainService

logger = get_logger(__name__)


async def _get_orchestrator(ctx: dict) -> AcademicOrchestrator:
    if "orchestrator" in ctx:
        return ctx["orchestrator"]
    engine = create_async_engine(settings.DATABASE_URL)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    cache = ctx.get("cache") or RedisCache(settings.REDIS_URL)
    scraper = CollegePortalScraper(base_url="https://college.portal")
    return AcademicOrchestrator(scraper, cache, session_factory)


async def task_morning_commute_digest(
    ctx: dict,
    student_id: str,
    username: str,
    password: str,
    source_station: str,
    destination_station: str,
    target_lecture_time: str,
    telegram_chat_id: str,
) -> bool:
    """Collect academic and suburban rail data, reason about commute urgency,

    and dispatch a personalized morning briefing.
    """
    try:
        orchestrator = await _get_orchestrator(ctx)
        credentials = {"username": username, "password": password}

        # 1 & 2: Fetch student attendance and exam records
        attendance_res = await orchestrator.get_attendance(student_id, credentials)
        attendance_records = attendance_res.get("data", [])

        exam_res = await orchestrator.get_exams(student_id, credentials)
        exam_records = exam_res.get("data", [])

        # 3: Query upcoming trains departing after 07:00 AM
        cache = ctx.get("cache") or RedisCache(settings.REDIS_URL)
        engine = create_async_engine(settings.DATABASE_URL)
        async with async_sessionmaker(engine, expire_on_commit=False)() as session:
            train_res = await TrainService.get_next_trains(
                db_session=session,
                cache=cache,
                source=source_station,
                destination=destination_station,
                query_time=time(7, 0, 0),
                limit=10,
            )
        available_trains = train_res.get("data", [])

        # 4: Autonomous commute evaluation
        decision_engine = CommuteDecisionEngine()
        target_time = decision_engine._parse_time(target_lecture_time)
        decision = decision_engine.evaluate_commute_urgency(
            attendance_records=attendance_records,
            exam_records=exam_records,
            available_trains=available_trains,
            target_arrival_time=target_time,
        )

        # 5: Format structured markdown notification
        today = datetime.now().strftime("%A, %d %B %Y")
        risk_level = decision["risk_level"]
        rec_train = decision["recommended_train"] or {}

        # Attendance alert section
        critical_lines: List[str] = []
        for r in attendance_records:
            if float(r.get("percentage", 100.0)) < 75.0:
                cond = r.get("total_conducted", 0)
                att = r.get("total_attended", 0)
                critical_lines.append(
                    f"- {r['subject_name']}: {r['percentage']}% ({att}/{cond}) -> *CRITICAL*"
                )

        if not critical_lines:
            attendance_summary = "All courses above 75% requirement."
        else:
            attendance_summary = "\n".join(critical_lines)

        dep_time = rec_train.get("departure_from_source", "N/A")
        arr_time = rec_train.get("arrival_at_destination", "N/A")
        train_num = rec_train.get("train_number", "N/A")
        train_type = rec_train.get("train_type", "SLOW")

        if arr_time != "N/A":
            parsed_arr = decision_engine._parse_time(arr_time)
            buf = int(decision_engine._calculate_buffer_minutes(target_time, parsed_arr))
        else:
            buf = 0

        briefing_message = f"""🚨 *MORNING COMMUTE BRIEFING* 🚨
📅 Date: {today}
⚠️ Risk Level: *{risk_level}*

📚 *Attendance Alert:*
{attendance_summary}

🚆 *Recommended Commute ({source_station} -> {destination_station}):*
- Train: *#{train_num} ({train_type})*
- Departs {source_station}: *{dep_time}*
- Arrives {destination_station}: *{arr_time}* (Buffer: {buf} mins)

💡 *Recommendation:* Take this train to avoid further attendance deficit."""

        # 6: Dispatch via Telegram
        alert_dispatcher = AlertDispatcher(telegram_chat_id=telegram_chat_id)
        try:
            return await alert_dispatcher.send_telegram_alert(
                briefing_message, chat_id=telegram_chat_id
            )
        finally:
            await alert_dispatcher.aclose()

    except Exception as exc:
        logger.error(f"task_morning_commute_digest failed for student {student_id}: {exc}")
        raise Retry(defer=ctx.get("job_try", 1) * 30) from exc


async def task_background_cache_warm(
    ctx: dict, stations_pair: Optional[List[Tuple[str, str]]] = None
) -> int:
    """Pre-fetch next trains for high-traffic commuter routes during peak hours

    and pre-populate Redis cache.
    """
    if stations_pair is None:
        stations_pair = [
            ("Thane", "Byculla"),
            ("Byculla", "Thane"),
            ("CSMT", "Kalyan"),
            ("Kalyan", "CSMT"),
        ]

    cache = ctx.get("cache") or RedisCache(settings.REDIS_URL)
    engine = create_async_engine(settings.DATABASE_URL)
    now_time = datetime.now().time()
    warmed_count = 0

    try:
        async with async_sessionmaker(engine, expire_on_commit=False)() as session:
            for src, dst in stations_pair:
                await TrainService.get_next_trains(
                    db_session=session,
                    cache=cache,
                    source=src,
                    destination=dst,
                    query_time=now_time,
                    limit=5,
                )
                warmed_count += 1
        logger.info(f"Successfully warmed {warmed_count} commuter routes into Redis cache.")
        return warmed_count
    except Exception as exc:
        logger.error(f"task_background_cache_warm encountered error: {exc}")
        return warmed_count
