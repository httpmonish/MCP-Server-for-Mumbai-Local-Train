from datetime import datetime, time
from typing import Optional

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from ..app.cache import RedisCache
from ..app.scrapers.college_portal import CollegePortalScraper
from ..app.services import train_service
from ..app.services.academic_orchestrator import AcademicOrchestrator
from ..mcp_server.config import mcp_settings
from ..mcp_server.formatters import format_attendance_report, format_exam_schedule, format_train_schedule

# Shared Resources (initialized lazily or as singletons)
_resources = {}

async def get_orchestrator():
    if "orchestrator" not in _resources:
        engine = create_async_engine(mcp_settings.DATABASE_URL)
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        cache = RedisCache(mcp_settings.REDIS_URL)
        scraper = CollegePortalScraper(base_url="https://college.portal")
        _resources["orchestrator"] = AcademicOrchestrator(scraper, cache, session_factory)
    return _resources["orchestrator"]

async def get_cache():
    if "cache" not in _resources:
        _resources["cache"] = RedisCache(mcp_settings.REDIS_URL)
    return _resources["cache"]

async def get_db_session():
    if "session_factory" not in _resources:
        engine = create_async_engine(mcp_settings.DATABASE_URL)
        _resources["session_factory"] = async_sessionmaker(engine, expire_on_commit=False)

    async with _resources["session_factory"]() as session:
        yield session

async def handle_get_attendance(student_id: str, username: Optional[str] = None, password: Optional[str] = None) -> str:
    # Resolve credentials
    user = username or mcp_settings.PORTAL_DEFAULT_USERNAME
    pwd = password or mcp_settings.PORTAL_DEFAULT_PASSWORD

    if not user or not pwd:
        return "Missing portal credentials. Provide username and password."

    orchestrator = await get_orchestrator()
    try:
        result = await orchestrator.get_attendance(student_id, {"username": user, "password": pwd})
        return format_attendance_report(student_id, result)
    except Exception as e:
        return f"Tool Execution Error: {str(e)}"

async def handle_get_upcoming_exams(student_id: str, username: Optional[str] = None, password: Optional[str] = None) -> str:
    # Resolve credentials
    user = username or mcp_settings.PORTAL_DEFAULT_USERNAME
    pwd = password or mcp_settings.PORTAL_DEFAULT_PASSWORD

    if not user or not pwd:
        return "Missing portal credentials. Provide username and password."

    orchestrator = await get_orchestrator()
    try:
        result = await orchestrator.get_exams(student_id, {"username": user, "password": pwd})
        return format_exam_schedule(student_id, result)
    except Exception as e:
        return f"Tool Execution Error: {str(e)}"

async def handle_get_next_train(source: str, destination: str, query_time: Optional[str] = None, limit: int = 5) -> str:
    # Parse query_time
    if query_time:
        try:
            if len(query_time.split(':')) == 2:
                h, m = map(int, query_time.split(':'))
                parsed_time = time(h, m)
            else:
                h, m, s = map(int, query_time.split(':'))
                parsed_time = time(h, m, s)
        except ValueError:
            return "Invalid time format. Use HH:MM or HH:MM:SS."
    else:
        parsed_time = datetime.now().time()

    try:
        # We need a db session and cache for train_service
        cache = await get_cache()

        # Manually handle session for the service call
        engine = create_async_engine(mcp_settings.DATABASE_URL)
        async with async_sessionmaker(engine, expire_on_commit=False)() as session:
            result = await train_service.get_next_trains(
                db_session=session,
                cache=cache,
                source=source,
                destination=destination,
                query_time=parsed_time,
                limit=limit
            )

        return format_train_schedule(source, destination, result["data"], parsed_time.strftime("%H:%M:%S"))
    except Exception as e:
        return f"Tool Execution Error: {str(e)}"
