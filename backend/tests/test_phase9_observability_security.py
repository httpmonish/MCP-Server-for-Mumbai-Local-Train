import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

import pytest
import pytest_asyncio
from app.core.config import settings
from app.core.logger import (
    SecretRedactionFilter,
    StructuredJSONFormatter,
    clear_request_context,
    get_logger,
    get_request_context,
    redact_dict,
    redact_sensitive_text,
    set_request_context,
)
from app.core.security import create_access_token, hash_password
from app.core.telemetry import (
    HTTP_REQUESTS_TOTAL,
    MCP_TOOL_CALLS_TOTAL,
    NOTIFICATION_DELIVERIES_TOTAL,
    SECURITY_EVENTS_TOTAL,
    TRANSIT_PROVIDER_REQUESTS_TOTAL,
    get_metrics_payload,
    record_cache_hit,
    record_cache_miss,
    record_security_event,
)
from app.main import app
from app.models.auth import Organization, OrgType, User, UserRole
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest_asyncio.fixture
async def phase9_test_setup(test_session_factory):
    """Seed test organizations and users for Phase 9 testing."""
    async with test_session_factory() as db:
        # Organization A (College)
        org_a = Organization(
            id=uuid.uuid4(),
            name="Vidyalankar Institute",
            type=OrgType.COLLEGE,
            domain="vjti.ac.in",
            is_active=True,
        )
        db.add(org_a)

        # Admin A
        admin_a = User(
            id=uuid.uuid4(),
            org_id=org_a.id,
            email="admin_a@vjti.ac.in",
            password_hash=hash_password("AdminPass123!"),
            full_name="Admin A",
            role=UserRole.ORG_ADMIN,
            is_active=True,
        )
        db.add(admin_a)

        # Student A
        student_a = User(
            id=uuid.uuid4(),
            org_id=org_a.id,
            email="student_a@vjti.ac.in",
            password_hash=hash_password("StudentPass123!"),
            full_name="Student A",
            role=UserRole.STUDENT,
            is_active=True,
        )
        db.add(student_a)

        # Organization B (Company)
        org_b = Organization(
            id=uuid.uuid4(),
            name="Reliance Tech",
            type=OrgType.COMPANY,
            domain="reliance.com",
            is_active=True,
        )
        db.add(org_b)

        # Admin B
        admin_b = User(
            id=uuid.uuid4(),
            org_id=org_b.id,
            email="admin_b@reliance.com",
            password_hash=hash_password("AdminBPass123!"),
            full_name="Admin B",
            role=UserRole.ORG_ADMIN,
            is_active=True,
        )
        db.add(admin_b)

        await db.commit()
        await db.refresh(org_a)
        await db.refresh(admin_a)
        await db.refresh(student_a)
        await db.refresh(org_b)
        await db.refresh(admin_b)

        return {
            "org_a": org_a,
            "admin_a": admin_a,
            "student_a": student_a,
            "org_b": org_b,
            "admin_b": admin_b,
        }


# ==============================================================================
# 1. STRUCTURED JSON LOGGING & PII REDACTION TESTS
# ==============================================================================

def test_structured_json_logging_and_redaction():
    """Verify structured JSON formatter and automated secret redaction."""
    formatter = StructuredJSONFormatter(service_name="test-service", environment="test")
    record = logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=42,
        msg="User login attempt with password 'SuperSecret123!' and token 'eyJh.eyJ.sig' for user test@example.com",
        args=(),
        exc_info=None,
    )

    set_request_context(request_id="req_test_123", trace_id="trc_test_456", user_id="usr_789")
    formatted_str = formatter.format(record)
    clear_request_context()

    parsed = json.loads(formatted_str)
    assert parsed["service"] == "test-service"
    assert parsed["environment"] == "test"
    assert parsed["request_id"] == "req_test_123"
    assert parsed["trace_id"] == "trc_test_456"
    assert parsed["user_id"] == "usr_789"
    assert parsed["level"] == "INFO"

    # Redaction checks
    assert "SuperSecret123!" not in parsed["message"]
    assert "[REDACTED]" in parsed["message"]


def test_dict_and_text_redaction_utilities():
    """Test dictionary and raw string secret redaction filters."""
    sensitive_dict = {
        "user_email": "commuter@mumbai.in",
        "password": "ClearTextPassword123",
        "api_key": "sk-live-1234567890",
        "nested": {
            "jwt_token": "Bearer eyJhbGciOi...",
            "safe_metric": 42.5,
        },
    }
    redacted = redact_dict(sensitive_dict)
    assert redacted["password"] == "[REDACTED]"
    assert redacted["api_key"] == "[REDACTED]"
    assert redacted["nested"]["jwt_token"] == "[REDACTED]"
    assert redacted["nested"]["safe_metric"] == 42.5
    assert redacted["user_email"] == "commuter@mumbai.in"

    raw_text = "Sending Authorization: Bearer abc.def.ghi to external endpoint"
    assert redact_sensitive_text(raw_text) == "Sending Authorization: Bearer [REDACTED] to external endpoint"


# ==============================================================================
# 2. OBSERVABILITY MIDDLEWARE & HEADERS TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_observability_middleware_headers_and_correlation(client: AsyncClient, phase9_test_setup):
    """Verify middleware injects X-Request-ID, X-Trace-ID, and Security Headers."""
    # 1. Custom incoming request ID propagation
    headers = {"X-Request-ID": "custom-client-req-999"}
    res = await client.get("/health", headers=headers)
    assert res.status_code == 200
    assert res.headers["X-Request-ID"] == "custom-client-req-999"
    assert "X-Trace-ID" in res.headers
    assert res.headers["X-Content-Type-Options"] == "nosniff"
    assert res.headers["X-Frame-Options"] == "DENY"

    # 2. Auto-generated request ID when omitted
    res_auto = await client.get("/health")
    assert res_auto.status_code == 200
    assert res_auto.headers["X-Request-ID"].startswith("req_")
    assert res_auto.headers["X-Trace-ID"].startswith("trc_")


# ==============================================================================
# 3. PROMETHEUS METRICS (/metrics) TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_prometheus_metrics_endpoint_telemetry(client: AsyncClient):
    """Verify /metrics exposes HTTP, transit, notification, and security metrics."""
    # Trigger metric recordings
    record_cache_hit("timetable")
    record_cache_miss("timetable")
    record_security_event(event_type="auth_unauthorized", severity="warning")
    TRANSIT_PROVIDER_REQUESTS_TOTAL.labels(provider="mock", status="success").inc()
    NOTIFICATION_DELIVERIES_TOTAL.labels(channel="email", provider="mock", status="success").inc()
    MCP_TOOL_CALLS_TOTAL.labels(tool_name="get_my_schedule", status="success").inc()

    res = await client.get("/metrics")
    assert res.status_code == 200
    content = res.text
    assert "http_requests_total" in content
    assert "http_request_duration_seconds" in content
    assert "cache_operations_total" in content
    assert "transit_provider_requests_total" in content
    assert "notification_deliveries_total" in content
    assert "mcp_tool_calls_total" in content
    assert "security_events_total" in content


# ==============================================================================
# 4. STANDARDIZED ERROR CONTRACT TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_standardized_error_response_format(client: AsyncClient):
    """Verify 401, 404, and 422 return standardized error payloads."""
    # 1. 401 Unauthorized
    res_401 = await client.get("/api/v1/notifications/me")
    assert res_401.status_code == 401
    data_401 = res_401.json()
    assert "error" in data_401
    assert data_401["error"]["code"] == "AUTHENTICATION_REQUIRED"
    assert "request_id" in data_401["error"]
    assert "timestamp" in data_401["error"]

    # 2. 404 Not Found
    res_404 = await client.get("/api/v1/non-existent-route-endpoint")
    assert res_404.status_code == 404
    data_404 = res_404.json()
    assert "error" in data_404
    assert data_404["error"]["code"] == "RESOURCE_NOT_FOUND"

    # 3. 422 Validation Error
    res_422 = await client.post("/auth/register", json={"email": "invalid_email"})
    assert res_422.status_code == 422
    data_422 = res_422.json()
    assert "error" in data_422
    assert data_422["error"]["code"] == "SCHEMA_VALIDATION_FAILED"
    assert "details" in data_422["error"]


# ==============================================================================
# 5. SECURITY HARDENING: IDOR & CROSS-TENANT ISOLATION
# ==============================================================================

@pytest.mark.asyncio
async def test_cross_tenant_idor_security(client: AsyncClient, phase9_test_setup):
    """Verify Org A Admin cannot access or mutate Org B data."""
    admin_a = phase9_test_setup["admin_a"]
    org_a = phase9_test_setup["org_a"]
    org_b = phase9_test_setup["org_b"]
    admin_b = phase9_test_setup["admin_b"]

    token_admin_a = create_access_token(
        user_id=str(admin_a.id),
        email=admin_a.email,
        org_id=str(org_a.id),
        role=admin_a.role.value,
    )
    headers_a = {"Authorization": f"Bearer {token_admin_a}"}

    # Org A Admin tries to get members of Org B
    res = await client.get(f"/organizations/members?org_id={org_b.id}", headers=headers_a)
    # Should only return Org A members or refuse cross-tenant access
    assert res.status_code in [200, 403]
    if res.status_code == 200:
        members = res.json().get("members", [])
        for m in members:
            assert str(m["org_id"]) == str(org_a.id)
            assert str(m["org_id"]) != str(org_b.id)

    # Org A Admin tries to delete Org B admin
    res_del = await client.delete(f"/organizations/members/{admin_b.id}", headers=headers_a)
    assert res_del.status_code in [403, 404]


# ==============================================================================
# 6. SECURITY HARDENING: ROLE ESCALATION PREVENTION
# ==============================================================================

@pytest.mark.asyncio
async def test_role_escalation_prevention(client: AsyncClient, phase9_test_setup):
    """Verify STUDENT cannot access admin management routes."""
    student_a = phase9_test_setup["student_a"]
    org_a = phase9_test_setup["org_a"]

    token_student = create_access_token(
        user_id=str(student_a.id),
        email=student_a.email,
        org_id=str(org_a.id),
        role=student_a.role.value,
    )
    headers = {"Authorization": f"Bearer {token_student}"}

    # Student attempts to add a new admin member
    res = await client.post(
        "/organizations/members",
        json={
            "email": "hacker@vjti.ac.in",
            "full_name": "Hacker Admin",
            "role": "ORG_ADMIN",
        },
        headers=headers,
    )
    assert res.status_code == 403


# ==============================================================================
# 7. RELIABILITY: HEALTH & READINESS PROBES
# ==============================================================================

@pytest.mark.asyncio
async def test_health_liveness_and_readiness(client: AsyncClient):
    """Verify /health (liveness) and /ready (readiness) probe endpoints."""
    # Liveness
    res_health = await client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "alive"

    # Readiness
    res_ready = await client.get("/ready")
    assert res_ready.status_code in [200, 503]
    if res_ready.status_code == 200:
        data = res_ready.json()
        assert data["status"] == "ready"
        assert "database" in data["services"]
