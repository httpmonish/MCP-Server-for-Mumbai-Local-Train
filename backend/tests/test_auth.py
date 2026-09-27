import fakeredis.aioredis
import pytest
import pytest_asyncio
from app.cache import RedisCache
from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.auth import Organization, OrgType, User, UserRole
from app.models.base import Base
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


@pytest_asyncio.fixture
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
    # Override app state
    app.state.async_session_factory = test_session_factory
    app.state.cache = fake_redis_cache

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_registration_success(client: AsyncClient):
    """Test successful organization and founding ORG_ADMIN registration."""
    payload = {
        "org_name": "Veermata Jijabai Technological Institute",
        "org_type": "COLLEGE",
        "org_domain": "vjti.ac.in",
        "email": "Admin@vjti.ac.in",
        "password": "SecurePassword123!",
    }
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert "user" in data
    assert "organization" in data
    assert "tokens" in data

    # Verify user details
    assert data["user"]["email"] == "admin@vjti.ac.in"  # Normalized to lowercase
    assert data["user"]["role"] == "ORG_ADMIN"
    assert data["user"]["is_active"] is True
    assert "password" not in data["user"]
    assert "password_hash" not in data["user"]

    # Verify organization details
    assert data["organization"]["name"] == "Veermata Jijabai Technological Institute"
    assert data["organization"]["type"] == "COLLEGE"

    # Verify tokens
    assert data["tokens"]["access_token"] is not None
    assert data["tokens"]["refresh_token"] is not None
    assert data["tokens"]["token_type"] == "bearer"
    assert data["tokens"]["expires_in"] == 900  # 15 minutes


@pytest.mark.asyncio
async def test_registration_duplicate_email_rejected(client: AsyncClient):
    """Duplicate email registration must return 409 Conflict."""
    payload = {
        "org_name": "VJTI",
        "org_type": "COLLEGE",
        "email": "director@vjti.ac.in",
        "password": "Password12345",
    }
    res1 = await client.post("/auth/register", json=payload)
    assert res1.status_code == 201

    # Try duplicate registration with different casing
    payload2 = {
        "org_name": "Another College",
        "org_type": "COLLEGE",
        "email": "DIRECTOR@vjti.ac.in",
        "password": "DifferentPassword123",
    }
    res2 = await client.post("/auth/register", json=payload2)
    assert res2.status_code == 409
    assert "already registered" in res2.json()["detail"]


@pytest.mark.asyncio
async def test_registration_validation_errors(client: AsyncClient):
    """Weak passwords, invalid emails, and blank org names must return 422."""
    # Weak password (< 8 chars)
    res_weak = await client.post(
        "/auth/register",
        json={
            "org_name": "My Org",
            "email": "valid@org.com",
            "password": "short",
        },
    )
    assert res_weak.status_code == 422

    # Invalid email
    res_email = await client.post(
        "/auth/register",
        json={
            "org_name": "My Org",
            "email": "not-an-email",
            "password": "ValidPassword123",
        },
    )
    assert res_email.status_code == 422

    # Blank org name
    res_blank = await client.post(
        "/auth/register",
        json={
            "org_name": "   ",
            "email": "valid@org.com",
            "password": "ValidPassword123",
        },
    )
    assert res_blank.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Test login with valid credentials returns fresh tokens."""
    # Register user first
    await client.post(
        "/auth/register",
        json={
            "org_name": "SPIT",
            "org_type": "COLLEGE",
            "email": "dean@spit.ac.in",
            "password": "StrongPassword99!",
        },
    )

    # Login with case-insensitive email
    login_res = await client.post(
        "/auth/login",
        json={
            "email": "DEAN@SPIT.AC.IN",
            "password": "StrongPassword99!",
        },
    )
    assert login_res.status_code == 200
    data = login_res.json()
    assert data["user"]["email"] == "dean@spit.ac.in"
    assert data["tokens"]["access_token"] is not None
    assert data["tokens"]["refresh_token"] is not None


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Incorrect passwords and nonexistent emails must return generic 401."""
    # Nonexistent user
    res1 = await client.post(
        "/auth/login",
        json={
            "email": "ghost@nowhere.com",
            "password": "SomePassword123",
        },
    )
    assert res1.status_code == 401
    assert res1.json()["detail"] == "Invalid email or password."

    # Register user
    await client.post(
        "/auth/register",
        json={
            "org_name": "DJSCE",
            "email": "prof@djsce.ac.in",
            "password": "CorrectPassword123!",
        },
    )

    # Wrong password
    res2 = await client.post(
        "/auth/login",
        json={
            "email": "prof@djsce.ac.in",
            "password": "WrongPassword!",
        },
    )
    assert res2.status_code == 401
    assert res2.json()["detail"] == "Invalid email or password."


@pytest.mark.asyncio
async def test_protected_route_auth_me(client: AsyncClient):
    """Protected /auth/me route requires valid Bearer access token."""
    # Unauthenticated request rejected
    res_unauth = await client.get("/auth/me")
    assert res_unauth.status_code == 401

    # Register and obtain token
    reg_res = await client.post(
        "/auth/register",
        json={
            "org_name": "KJSCE",
            "email": "admin@somaiya.edu",
            "password": "SuperSecretPassword123!",
        },
    )
    access_token = reg_res.json()["tokens"]["access_token"]

    # Authenticated request succeeds
    res_auth = await client.get("/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert res_auth.status_code == 200
    user_me = res_auth.json()
    assert user_me["user"]["email"] == "admin@somaiya.edu"
    assert user_me["organization"]["name"] == "KJSCE"


@pytest.mark.asyncio
async def test_token_refresh_rotation(client: AsyncClient):
    """
    Refresh token rotation: Old refresh token is invalidated upon refresh,
    and a new rotated pair is returned.
    """
    reg_res = await client.post(
        "/auth/register",
        json={
            "org_name": "TSEC",
            "email": "admin@tsec.edu",
            "password": "Password12345!",
        },
    )
    refresh_token_1 = reg_res.json()["tokens"]["refresh_token"]

    # First refresh: succeeds and returns new rotated token
    ref_res1 = await client.post("/auth/refresh", json={"refresh_token": refresh_token_1})
    assert ref_res1.status_code == 200
    tokens1 = ref_res1.json()
    refresh_token_2 = tokens1["refresh_token"]
    assert refresh_token_2 != refresh_token_1

    # Second refresh with OLD token_1: must fail (rotation / revocation)
    ref_res_replay = await client.post("/auth/refresh", json={"refresh_token": refresh_token_1})
    assert ref_res_replay.status_code == 401

    # Third refresh with new token_2: succeeds
    ref_res2 = await client.post("/auth/refresh", json={"refresh_token": refresh_token_2})
    assert ref_res2.status_code == 200
    assert ref_res2.json()["access_token"] is not None


@pytest.mark.asyncio
async def test_logout_revocation(client: AsyncClient):
    """Logout invalidates the refresh token session immediately."""
    reg_res = await client.post(
        "/auth/register",
        json={
            "org_name": "IIT Bombay",
            "email": "dean@iitb.ac.in",
            "password": "Password12345!",
        },
    )
    refresh_token = reg_res.json()["tokens"]["refresh_token"]

    # Call logout
    logout_res = await client.post("/auth/logout", json={"refresh_token": refresh_token})
    assert logout_res.status_code == 200
    assert "revoked" in logout_res.json()["detail"].lower()

    # Attempting to refresh with the logged-out token must fail
    ref_res = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert ref_res.status_code == 401


@pytest.mark.asyncio
async def test_rbac_admin_verification(client: AsyncClient, test_session_factory):
    """Verify ORG_ADMIN can access admin endpoint while regular STUDENT is denied."""
    # Register ORG_ADMIN
    reg_res = await client.post(
        "/auth/register",
        json={
            "org_name": "MU College",
            "email": "principal@mu.ac.in",
            "password": "Password12345!",
        },
    )
    admin_token = reg_res.json()["tokens"]["access_token"]
    admin_org_id = reg_res.json()["organization"]["id"]

    # Admin access succeeds
    admin_res = await client.get("/auth/admin/verify", headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_res.status_code == 200
    assert admin_res.json()["role"] == "ORG_ADMIN"

    # Create a non-admin STUDENT user in the database
    import uuid

    student_id = uuid.uuid4()
    async with test_session_factory() as session:
        student = User(
            id=student_id,
            org_id=uuid.UUID(admin_org_id),
            email="student@mu.ac.in",
            password_hash=hash_password("StudentPass123!"),
            role=UserRole.STUDENT,
            is_active=True,
        )
        session.add(student)
        await session.commit()

    student_token = create_access_token(
        user_id=str(student_id),
        email="student@mu.ac.in",
        org_id=admin_org_id,
        role="STUDENT",
    )

    # Student trying to access admin endpoint -> 403 Forbidden
    student_res = await client.get("/auth/admin/verify", headers={"Authorization": f"Bearer {student_token}"})
    assert student_res.status_code == 403
    assert "Access denied" in student_res.json()["detail"]
