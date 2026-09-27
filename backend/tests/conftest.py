import fakeredis.aioredis
import pytest
import pytest_asyncio
from app.cache import RedisCache
from app.main import app
from app.models.base import Base
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


@pytest_asyncio.fixture(scope="function")
async def async_test_engine():
    """Create in-memory SQLite async engine for isolated test runs."""
    test_db_url = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(test_db_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session_factory(async_test_engine):
    return async_sessionmaker(async_test_engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def fake_redis_cache():
    cache = RedisCache("redis://localhost:6379/0")
    cache.client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield cache
    await cache.client.flushall()
    await cache.close()


@pytest_asyncio.fixture(scope="function")
async def client(test_session_factory, fake_redis_cache):
    # Override app state for tests
    app.state.async_session_factory = test_session_factory
    app.state.cache = fake_redis_cache

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
