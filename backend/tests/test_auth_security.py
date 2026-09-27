import time
import uuid

import fakeredis.aioredis
import jwt
import pytest
import pytest_asyncio
from app.cache import RedisCache
from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.auth import Organization, OrgType, User, UserRole
from app.models.base import Base
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


@pytest_asyncio.fixture
async def async_test_engine():
    test_db_url = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(test_db_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def test_session_factory(async_test_engine):
    return async_sessionmaker(async_test_engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def fake_redis_cache():
    cache = RedisCache("redis://localhost:6379/0")
    cache.client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield cache
    await cache.client.flushall()
    await cache.close()


@pytest_asyncio.fixture
async def client(test_session_factory, fake_redis_cache):
    app.state.async_session_factory = test_session_factory
    app.state.cache = fake_redis_cache

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_jwt_algorithm_confusion_attack(client: AsyncClient):
    """Ensure attacker cannot bypass signature verification with 'none' algorithm."""
    malicious_payload = {
        "sub": str(uuid.uuid4()),
        "email": "hacker@evil.com",
        "org_id": str(uuid.uuid4()),
        "role": "PLATFORM_ADMIN",
        "type": "access",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
    }
    # Unsigned token with alg: none
    unsigned_token = jwt.encode(malicious_payload, key="", algorithm="none")

    res = await client.get("/auth/me", headers={"Authorization": f"Bearer {unsigned_token}"})
    assert res.status_code == 401
    assert "Invalid or malformed" in res.json()["detail"]


@pytest.mark.asyncio
async def test_jwt_forged_secret_attack(client: AsyncClient):
    """Ensure tokens signed with wrong secret are rejected."""
    payload = {
        "sub": str(uuid.uuid4()),
        "email": "admin@vjti.ac.in",
        "org_id": str(uuid.uuid4()),
        "role": "ORG_ADMIN",
        "type": "access",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
    }
    forged_token = jwt.encode(payload, "wrong_secret_key_1234567890123456789012", algorithm="HS256")

    res = await client.get("/auth/me", headers={"Authorization": f"Bearer {forged_token}"})
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_jwt_expired_token(client: AsyncClient):
    """Ensure expired access tokens are rejected with appropriate 401 expired message."""
    payload = {
        "sub": str(uuid.uuid4()),
        "email": "user@org.com",
        "org_id": str(uuid.uuid4()),
        "role": "EMPLOYEE",
        "type": "access",
        "iat": int(time.time()) - 3600,
        "exp": int(time.time()) - 1800,  # Expired 30 mins ago
    }
    expired_token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

    res = await client.get("/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert res.status_code == 401
    assert "expired" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_token_type_enforcement(client: AsyncClient):
    """Ensure tokens without type='access' (e.g. type='refresh') cannot be used as Bearer tokens."""
    payload = {
        "sub": str(uuid.uuid4()),
        "email": "user@org.com",
        "org_id": str(uuid.uuid4()),
        "role": "EMPLOYEE",
        "type": "refresh",  # Wrong token type
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
    }
    wrong_type_token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

    res = await client.get("/auth/me", headers={"Authorization": f"Bearer {wrong_type_token}"})
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_inactive_user_token_rejection(client: AsyncClient, test_session_factory):
    """Ensure active token is rejected if user account gets deactivated in database."""
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    async with test_session_factory() as session:
        org = Organization(id=org_id, name="Test Corp", type=OrgType.COMPANY)
        user = User(
            id=user_id,
            org_id=org_id,
            email="banned@corp.com",
            password_hash=hash_password("Password123!"),
            role=UserRole.EMPLOYEE,
            is_active=False,  # Deactivated account
        )
        session.add(org)
        session.add(user)
        await session.commit()

    token = create_access_token(
        user_id=str(user_id),
        email="banned@corp.com",
        org_id=str(org_id),
        role="EMPLOYEE",
    )

    res = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403
    assert "deactivated" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_sql_injection_resilience(client: AsyncClient):
    """Ensure SQL injection payloads in email or password fail safely."""
    injection_payload = {
        "email": "test' OR '1'='1@exploit.com",
        "password": "' OR '1'='1' --",
    }
    res = await client.post("/auth/login", json=injection_payload)
    # Email validator will reject malformed email, or auth fails cleanly
    assert res.status_code in [401, 422]
