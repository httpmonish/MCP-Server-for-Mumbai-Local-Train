import json
import uuid
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Dict

import pytest
import pytest_asyncio
from app.core.config import settings
from app.core.security import create_access_token
from app.main import app
from app.models.auth import Organization, OrgType, User, UserRole
from app.models.notification import (
    DeliveryAttemptStatus,
    Notification,
    NotificationChannel,
    NotificationDelivery,
    NotificationPreference,
    NotificationPriority,
    NotificationStatus,
    NotificationType,
    OutboxEvent,
    OutboxStatus,
)
from app.models.schedule import (
    ExceptionType,
    Location,
    Schedule,
    ScheduleException,
    ScheduleSlot,
    ScheduleType,
    UserScheduleAssignment,
)
from app.notifications.outbox import OutboxService
from app.notifications.providers import get_mock_email_provider
from app.notifications.rules import is_in_quiet_hours
from app.notifications.scheduler import ReminderSchedulerService
from app.notifications.service import NotificationEngineService
from app.notifications.worker import NotificationDeliveryWorker
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def notification_test_setup(test_session_factory, fake_redis_cache):
    """Seed test organizations and users for notification tests."""
    mock_provider = get_mock_email_provider()
    mock_provider.clear()

    async with test_session_factory() as db_session:
        # Org A (College)
        org_a = Organization(
            id=uuid.uuid4(),
            name="Notification Test Institute",
            type=OrgType.COLLEGE,
            is_active=True,
        )
        # Org B
        org_b = Organization(
            id=uuid.uuid4(),
            name="Other Tech Org",
            type=OrgType.COMPANY,
            is_active=True,
        )
        db_session.add_all([org_a, org_b])
        await db_session.flush()

        # User A (Org A)
        user_a = User(
            id=uuid.uuid4(),
            org_id=org_a.id,
            email="student_a_notif@college.edu",
            password_hash="test_password_hash",
            role=UserRole.STUDENT,
            full_name="Pooja Mehta",
            is_active=True,
        )
        # User B (Org B)
        user_b = User(
            id=uuid.uuid4(),
            org_id=org_b.id,
            email="employee_b_notif@tech.com",
            password_hash="test_password_hash",
            role=UserRole.EMPLOYEE,
            full_name="Vikram Singh",
            is_active=True,
        )
        db_session.add_all([user_a, user_b])
        await db_session.flush()

        # Location & Schedule in Org A
        loc_a = Location(
            id=uuid.uuid4(),
            org_id=org_a.id,
            name="Ghatkopar Campus",
            nearest_station_code="GHATKOPAR",
            is_active=True,
        )
        db_session.add(loc_a)
        await db_session.flush()

        sched_a = Schedule(
            id=uuid.uuid4(),
            org_id=org_a.id,
            title="Distributed Systems Timetable",
            type=ScheduleType.CLASS,
            is_active=True,
        )
        db_session.add(sched_a)
        await db_session.flush()

        # Slot at 09:30 on Mondays (day_of_week=0)
        slot_a = ScheduleSlot(
            id=uuid.uuid4(),
            schedule_id=sched_a.id,
            day_of_week=0,
            start_time=time(9, 30, 0),
            end_time=time(11, 0, 0),
            title="Distributed Algorithms Lecture",
            location_id=loc_a.id,
        )
        db_session.add(slot_a)

        # Assignment for User A
        assign_a = UserScheduleAssignment(
            id=uuid.uuid4(),
            org_id=org_a.id,
            user_id=user_a.id,
            schedule_id=sched_a.id,
            valid_from=date(2026, 1, 1),
            is_active=True,
        )
        db_session.add(assign_a)

        await db_session.commit()

        token_a = create_access_token(
            user_id=str(user_a.id),
            email=user_a.email,
            org_id=str(org_a.id),
            role=user_a.role.value,
        )
        token_b = create_access_token(
            user_id=str(user_b.id),
            email=user_b.email,
            org_id=str(org_b.id),
            role=user_b.role.value,
        )

        return {
            "org_a": org_a,
            "org_b": org_b,
            "user_a": user_a,
            "user_b": user_b,
            "token_a": token_a,
            "token_b": token_b,
            "slot_a": slot_a,
            "sched_a": sched_a,
            "loc_a": loc_a,
            "mock_provider": mock_provider,
        }


# ==============================================================================
# 1. OUTBOX & DEDUPLICATION TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_outbox_event_recording_and_dispatch(test_session_factory, notification_test_setup):
    """Test emitting domain event into outbox and dispatching into a Notification."""
    user_a = notification_test_setup["user_a"]
    org_a = notification_test_setup["org_a"]

    async with test_session_factory() as db:
        # 1. Record attendance below threshold event
        await NotificationEngineService.trigger_attendance_below_threshold_event(
            db=db,
            org_id=org_a.id,
            user_id=user_a.id,
            percentage=73.5,
            min_required=75.0,
            shortage_count=3,
            policy_name="Semester 5 Attendance Rule",
        )
        await db.commit()

        # Verify outbox event exists in PENDING state
        stmt = select(OutboxEvent).where(OutboxEvent.org_id == org_a.id)
        res = await db.execute(stmt)
        events = list(res.scalars().all())
        assert len(events) == 1
        assert events[0].status == OutboxStatus.PENDING

        # 2. Dispatch pending outbox events
        dispatched = await OutboxService.dispatch_pending_events(db, limit=10)
        assert dispatched == 1

        # Verify OutboxEvent is marked PROCESSED
        await db.refresh(events[0])
        assert events[0].status == OutboxStatus.PROCESSED
        assert events[0].processed_at is not None

        # Verify Notification record created with PENDING status
        notif_stmt = select(Notification).where(Notification.user_id == user_a.id)
        notif_res = await db.execute(notif_stmt)
        notifs = list(notif_res.scalars().all())
        assert len(notifs) == 1
        assert notifs[0].type == NotificationType.ATTENDANCE_BELOW_THRESHOLD
        assert notifs[0].priority == NotificationPriority.HIGH
        assert notifs[0].status == NotificationStatus.PENDING
        assert "73.5%" in notifs[0].title


@pytest.mark.asyncio
async def test_outbox_idempotency_and_deduplication(test_session_factory, notification_test_setup):
    """Test duplicate outbox events are deduplicated without creating duplicate notifications."""
    user_a = notification_test_setup["user_a"]
    org_a = notification_test_setup["org_a"]

    async with test_session_factory() as db:
        # Emit identical event twice
        await NotificationEngineService.trigger_attendance_below_threshold_event(
            db=db,
            org_id=org_a.id,
            user_id=user_a.id,
            percentage=74.0,
            min_required=75.0,
            shortage_count=2,
        )
        await NotificationEngineService.trigger_attendance_below_threshold_event(
            db=db,
            org_id=org_a.id,
            user_id=user_a.id,
            percentage=74.0,
            min_required=75.0,
            shortage_count=2,
        )
        await db.commit()

        # Dispatch
        await OutboxService.dispatch_pending_events(db, limit=10)

        # Verify only 1 Notification was created
        notif_stmt = select(Notification).where(Notification.user_id == user_a.id)
        notif_res = await db.execute(notif_stmt)
        notifs = list(notif_res.scalars().all())
        assert len(notifs) == 1


# ==============================================================================
# 2. WORKER DELIVERY & RETRY TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_notification_delivery_success(test_session_factory, notification_test_setup):
    """Test NotificationDeliveryWorker delivers email and updates status to SENT."""
    user_a = notification_test_setup["user_a"]
    org_a = notification_test_setup["org_a"]
    mock_provider = notification_test_setup["mock_provider"]

    async with test_session_factory() as db:
        # Create outbox event and dispatch
        await NotificationEngineService.trigger_attendance_below_threshold_event(
            db=db,
            org_id=org_a.id,
            user_id=user_a.id,
            percentage=70.0,
            min_required=75.0,
            shortage_count=5,
        )
        await db.commit()
        await OutboxService.dispatch_pending_events(db)

        # Run delivery worker
        delivered_count = await NotificationDeliveryWorker.process_pending_notifications(db)
        assert delivered_count == 1
        assert len(mock_provider.sent_messages) == 1
        sent_msg = mock_provider.sent_messages[0]
        assert sent_msg["to_email"] == user_a.email
        assert "Attendance Alert" in sent_msg["subject"]

        # Verify Notification status is SENT
        stmt = select(Notification).where(Notification.user_id == user_a.id)
        res = await db.execute(stmt)
        notif = res.scalars().first()
        assert notif.status == NotificationStatus.SENT
        assert notif.sent_at is not None

        # Verify Delivery Attempt record
        del_stmt = select(NotificationDelivery).where(NotificationDelivery.notification_id == notif.id)
        del_res = await db.execute(del_stmt)
        deliveries = list(del_res.scalars().all())
        assert len(deliveries) == 1
        assert deliveries[0].status == DeliveryAttemptStatus.SUCCESS
        assert deliveries[0].provider == "mock"


@pytest.mark.asyncio
async def test_notification_delivery_retry_on_temporary_failure(test_session_factory, notification_test_setup):
    """Test temporary provider outage sets status to RETRYING with exponential backoff."""
    user_a = notification_test_setup["user_a"]
    org_a = notification_test_setup["org_a"]
    mock_provider = notification_test_setup["mock_provider"]
    mock_provider.simulated_failure_type = "500"

    async with test_session_factory() as db:
        await NotificationEngineService.trigger_attendance_below_threshold_event(
            db=db,
            org_id=org_a.id,
            user_id=user_a.id,
            percentage=71.0,
            min_required=75.0,
            shortage_count=4,
        )
        await db.commit()
        await OutboxService.dispatch_pending_events(db)

        # Attempt 1 -> fails with 500
        delivered = await NotificationDeliveryWorker.process_pending_notifications(db)
        assert delivered == 0

        stmt = select(Notification).where(Notification.user_id == user_a.id)
        res = await db.execute(stmt)
        notif = res.scalars().first()
        assert notif.status == NotificationStatus.RETRYING
        # Check that scheduled_for is set
        assert notif.scheduled_for is not None

        # Verify Delivery Attempt logged
        del_stmt = select(NotificationDelivery).where(NotificationDelivery.notification_id == notif.id)
        del_res = await db.execute(del_stmt)
        deliveries = list(del_res.scalars().all())
        assert len(deliveries) == 1
        assert deliveries[0].status == DeliveryAttemptStatus.FAILURE
        assert deliveries[0].error_code == "PROVIDER_5XX"


@pytest.mark.asyncio
async def test_notification_permanent_failure_handling(test_session_factory, notification_test_setup):
    """Test permanent rejection marks status FAILED immediately without retry loop."""
    user_a = notification_test_setup["user_a"]
    org_a = notification_test_setup["org_a"]
    mock_provider = notification_test_setup["mock_provider"]
    mock_provider.simulated_failure_type = "invalid_email"

    async with test_session_factory() as db:
        await NotificationEngineService.trigger_attendance_below_threshold_event(
            db=db,
            org_id=org_a.id,
            user_id=user_a.id,
            percentage=65.0,
            min_required=75.0,
            shortage_count=8,
        )
        await db.commit()
        await OutboxService.dispatch_pending_events(db)

        await NotificationDeliveryWorker.process_pending_notifications(db)

        stmt = select(Notification).where(Notification.user_id == user_a.id)
        res = await db.execute(stmt)
        notif = res.scalars().first()
        assert notif.status == NotificationStatus.FAILED


# ==============================================================================
# 3. SCHEDULE REMINDER & CANCELLATION TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_class_reminder_scheduler_and_cancellation(test_session_factory, notification_test_setup):
    """Test reminder scheduler identifies upcoming classes and suppresses canceled ones."""
    sched_a = notification_test_setup["sched_a"]

    monday_date = date(2026, 9, 28)  # Monday

    async with test_session_factory() as db:
        # Scenario 1: Scan at 09:02 for a class starting at 09:30 (approx 28 min away) -> emits reminder
        emitted = await ReminderSchedulerService.scan_and_generate_class_reminders(
            db=db,
            target_date=monday_date,
            target_time=time(9, 2, 0),
        )
        assert emitted == 1

        # Dispatch and deliver
        dispatched = await OutboxService.dispatch_pending_events(db)
        assert dispatched == 1
        delivered = await NotificationDeliveryWorker.process_pending_notifications(db)
        assert delivered == 1

        # Scenario 2: Add ScheduleException marking class canceled for a specific date
        exc = ScheduleException(
            id=uuid.uuid4(),
            schedule_id=sched_a.id,
            exception_date=date(2026, 10, 5),  # Next Monday
            exception_type=ExceptionType.CANCELLED,
            reason="National Holiday",
        )
        db.add(exc)
        await db.commit()

        # Scan on the canceled Monday date -> must emit 0 reminders
        emitted_canceled = await ReminderSchedulerService.scan_and_generate_class_reminders(
            db=db,
            target_date=date(2026, 10, 5),
            target_time=time(9, 2, 0),
        )
        assert emitted_canceled == 0


# ==============================================================================
# 4. PREFERENCES, QUIET HOURS & COMMUTE RISK TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_quiet_hours_and_user_opt_out_suppression(test_session_factory, notification_test_setup):
    """Test quiet hours calculation and user preference opt-out suppression."""
    # Unit check quiet hours function
    assert is_in_quiet_hours(time(23, 30), time(22, 0), time(6, 0)) is True
    assert is_in_quiet_hours(time(3, 0), time(22, 0), time(6, 0)) is True
    assert is_in_quiet_hours(time(14, 0), time(22, 0), time(6, 0)) is False

    user_a = notification_test_setup["user_a"]
    org_a = notification_test_setup["org_a"]

    async with test_session_factory() as db:
        # User disables COMMUTE_DELAY_RISK
        pref = NotificationPreference(
            id=uuid.uuid4(),
            org_id=org_a.id,
            user_id=user_a.id,
            notification_type=NotificationType.COMMUTE_DELAY_RISK,
            channel=NotificationChannel.EMAIL,
            enabled=False,
        )
        db.add(pref)
        await db.commit()

        # Trigger commute risk event
        await NotificationEngineService.trigger_commute_delay_risk_event(
            db=db,
            org_id=org_a.id,
            user_id=user_a.id,
            slot_id=uuid.uuid4(),
            slot_title="Operating Systems",
            origin_station="Thane",
            destination_station="Vidyavihar",
            scheduled_start="09:00:00",
            estimated_arrival="09:12:00",
            arrival_margin_minutes=-12,
            risk_status="LIKELY_LATE",
        )
        await db.commit()
        await OutboxService.dispatch_pending_events(db)

        # Verify notification was SUPPRESSED because user disabled it
        stmt = select(Notification).where(
            Notification.user_id == user_a.id,
            Notification.type == NotificationType.COMMUTE_DELAY_RISK,
        )
        res = await db.execute(stmt)
        notif = res.scalars().first()
        assert notif.status == NotificationStatus.SUPPRESSED
        assert "disabled" in notif.suppressed_reason


# ==============================================================================
# 5. REST API & TENANT ISOLATION TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_notifications_rest_api_and_tenant_isolation(client: AsyncClient, test_session_factory, notification_test_setup):
    """Test GET /api/v1/notifications/me and PATCH preferences with tenant isolation."""
    token_a = notification_test_setup["token_a"]
    token_b = notification_test_setup["token_b"]
    user_a = notification_test_setup["user_a"]
    org_a = notification_test_setup["org_a"]

    async with test_session_factory() as db:
        # Create a notification for User A
        await NotificationEngineService.trigger_attendance_below_threshold_event(
            db=db,
            org_id=org_a.id,
            user_id=user_a.id,
            percentage=69.0,
            min_required=75.0,
            shortage_count=6,
        )
        await db.commit()
        await OutboxService.dispatch_pending_events(db)

    # 1. User A queries /me -> returns 1 notification
    resp_a = await client.get("/api/v1/notifications/me", headers={"Authorization": f"Bearer {token_a}"})
    assert resp_a.status_code == 200
    data_a = resp_a.json()
    assert data_a["total"] == 1
    assert data_a["items"][0]["user_id"] == str(user_a.id)

    # 2. User B from Org B queries /me -> returns 0 notifications (strict tenant isolation)
    resp_b = await client.get("/api/v1/notifications/me", headers={"Authorization": f"Bearer {token_b}"})
    assert resp_b.status_code == 200
    data_b = resp_b.json()
    assert data_b["total"] == 0

    # 3. User A configures preferences via PATCH /preferences
    pref_payload = {
        "notification_type": "CLASS_STARTING_REMINDER",
        "channel": "EMAIL",
        "enabled": True,
        "quiet_hours_start": "23:00:00",
        "quiet_hours_end": "06:00:00",
        "timezone": "Asia/Kolkata",
    }
    patch_res = await client.patch(
        "/api/v1/notifications/preferences",
        json=pref_payload,
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert patch_res.status_code == 200
    pref_data = patch_res.json()
    assert pref_data["notification_type"] == "CLASS_STARTING_REMINDER"
    assert pref_data["enabled"] is True
    assert pref_data["quiet_hours_start"] == "23:00:00"

    # 4. User A reads back preferences via GET /preferences
    get_pref_res = await client.get(
        "/api/v1/notifications/preferences",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert get_pref_res.status_code == 200
    prefs_list = get_pref_res.json()
    assert len(prefs_list) >= 1
    assert any(p["notification_type"] == "CLASS_STARTING_REMINDER" for p in prefs_list)
