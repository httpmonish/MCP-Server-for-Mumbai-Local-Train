import uuid
from datetime import date, datetime, time, timedelta, timezone

import pytest
from app.models.attendance import AttendancePolicy, AttendanceRecord, AttendanceStatus, PolicyAppliesTo
from app.models.auth import Organization, OrgType, User, UserRole
from app.models.schedule import Schedule, ScheduleSlot, ScheduleType
from app.services.attendance_calculator import calculate_attendance_summary
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_pure_attendance_calculator():
    u_id = uuid.uuid4()
    o_id = uuid.uuid4()

    # 20 sessions: 17 present, 3 absent
    records = [
        AttendanceRecord(id=uuid.uuid4(), org_id=o_id, user_id=u_id, date=date(2026, 9, 1), status=AttendanceStatus.PRESENT)
        for _ in range(17)
    ] + [
        AttendanceRecord(id=uuid.uuid4(), org_id=o_id, user_id=u_id, date=date(2026, 9, 2), status=AttendanceStatus.ABSENT)
        for _ in range(3)
    ]
    # Add 2 cancelled classes and 1 holiday
    records.append(AttendanceRecord(id=uuid.uuid4(), org_id=o_id, user_id=u_id, date=date(2026, 9, 3), status=AttendanceStatus.CANCELLED))
    records.append(AttendanceRecord(id=uuid.uuid4(), org_id=o_id, user_id=u_id, date=date(2026, 9, 4), status=AttendanceStatus.HOLIDAY))

    summary = calculate_attendance_summary(records, min_percentage=75.0, user_id=u_id, org_id=o_id)
    assert summary.total_sessions == 22
    assert summary.counted_sessions == 20
    assert summary.present_count == 17
    assert summary.absent_count == 3
    assert summary.cancelled_count == 2
    assert summary.percentage == 85.0
    assert summary.status.value == "ABOVE_THRESHOLD"
    assert summary.shortage_percentage == 0.0
    assert summary.sessions_needed_to_recover == 0


@pytest.mark.asyncio
async def test_shortage_and_recovery_calculation():
    u_id = uuid.uuid4()
    o_id = uuid.uuid4()

    # Construct scenario with 26 present, 9 absent (26/35 = 74.2857 -> 74.29%)
    records = [
        AttendanceRecord(id=uuid.uuid4(), org_id=o_id, user_id=u_id, date=date(2026, 9, 1), status=AttendanceStatus.PRESENT)
        for _ in range(26)
    ] + [
        AttendanceRecord(id=uuid.uuid4(), org_id=o_id, user_id=u_id, date=date(2026, 9, 2), status=AttendanceStatus.ABSENT)
        for _ in range(9)
    ]

    summary = calculate_attendance_summary(records, min_percentage=75.0, user_id=u_id, org_id=o_id)
    assert summary.percentage < 75.0
    assert summary.status.value == "BELOW_THRESHOLD"
    assert summary.shortage_percentage > 0.0
    assert summary.sessions_needed_to_recover == 1  # 27 / 36 = 75.0% exactly!


@pytest.mark.asyncio
async def test_create_policy_and_get_summary_api(client: AsyncClient):
    # Register admin & college org
    admin_res = await client.post(
        "/auth/register",
        json={
            "email": f"dean_{uuid.uuid4().hex[:6]}@vjti.ac.in",
            "password": "SecurePassword123!",
            "org_name": "VJTI Mumbai",
            "org_type": "COLLEGE",
            "full_name": "Dean Academics",
        },
    )
    assert admin_res.status_code == 201
    admin_token = admin_res.json()["tokens"]["access_token"]
    admin_auth = {"Authorization": f"Bearer {admin_token}"}

    # Create policy
    policy_res = await client.post(
        "/api/v1/attendance/policies",
        headers=admin_auth,
        json={
            "name": "VJTI 75% Statutory Attendance Policy",
            "applies_to": "STUDENT",
            "min_percentage": 75.0,
            "late_penalty_multiplier": 1.0,
            "count_excused_in_denominator": False,
        },
    )
    assert policy_res.status_code == 201
    policy_data = policy_res.json()
    assert policy_data["name"] == "VJTI 75% Statutory Attendance Policy"
    assert policy_data["min_percentage"] == 75.0

    # Add a student member
    student_email = f"aditya_{uuid.uuid4().hex[:6]}@vjti.ac.in"
    member_res = await client.post(
        "/organizations/members",
        headers=admin_auth,
        json={
            "email": student_email,
            "password": "StudentPassword123!",
            "full_name": "Aditya Sharma",
            "role": "STUDENT",
        },
    )
    assert member_res.status_code == 201
    student_id = member_res.json()["id"]

    # Student logs in
    student_login = await client.post(
        "/auth/login",
        json={"email": student_email, "password": "StudentPassword123!"},
    )
    assert student_login.status_code == 200
    student_token = student_login.json()["tokens"]["access_token"]
    student_auth = {"Authorization": f"Bearer {student_token}"}

    # Admin marks 3 attendance records for student (2 present, 1 absent)
    rec1 = await client.post(
        "/api/v1/attendance",
        headers=admin_auth,
        json={
            "user_id": student_id,
            "date": "2026-09-01",
            "status": "PRESENT",
            "remarks": "On-time arrival",
        },
    )
    assert rec1.status_code == 201
    assert "id" in rec1.json()

    rec2 = await client.post(
        "/api/v1/attendance",
        headers=admin_auth,
        json={
            "user_id": student_id,
            "date": "2026-09-02",
            "status": "PRESENT",
        },
    )
    assert rec2.status_code == 201

    rec3 = await client.post(
        "/api/v1/attendance",
        headers=admin_auth,
        json={
            "user_id": student_id,
            "date": "2026-09-03",
            "status": "ABSENT",
        },
    )
    assert rec3.status_code == 201

    # Student fetches own summary: 2 present out of 3 = 66.67% (BELOW_THRESHOLD)
    sum_res = await client.get("/api/v1/attendance/me/summary", headers=student_auth)
    assert sum_res.status_code == 200
    sum_data = sum_res.json()
    assert sum_data["total_sessions"] == 3
    assert sum_data["counted_sessions"] == 3
    assert sum_data["present_count"] == 2
    assert sum_data["absent_count"] == 1
    assert sum_data["percentage"] == 66.67
    assert sum_data["status"] == "BELOW_THRESHOLD"
    assert sum_data["shortage_percentage"] == 8.33
    assert sum_data["sessions_needed_to_recover"] == 1  # (3/4 = 75.0%)

    # Student fetches own attendance records
    records_res = await client.get("/api/v1/attendance/me", headers=student_auth)
    assert records_res.status_code == 200
    assert records_res.json()["total"] == 3

    # Admin corrects rec3 (ABSENT -> PRESENT) with mandatory reason
    patch_res = await client.patch(
        f"/api/v1/attendance/{rec3.json()['id']}",
        headers=admin_auth,
        json={
            "status": "PRESENT",
            "reason": "Official Central Railway delay certificate submitted for Thane-Dadar corridor delay.",
        },
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "PRESENT"

    # View audit trail
    audit_res = await client.get(
        f"/api/v1/attendance/{rec3.json()['id']}/audit",
        headers=admin_auth,
    )
    assert audit_res.status_code == 200
    audits = audit_res.json()
    assert len(audits) == 1
    assert audits[0]["old_status"] == "ABSENT"
    assert audits[0]["new_status"] == "PRESENT"
    assert "Railway delay certificate" in audits[0]["reason"]

    # Student summary now reflects 3/3 = 100% (ABOVE_THRESHOLD)
    sum_res_after = await client.get("/api/v1/attendance/me/summary", headers=student_auth)
    assert sum_res_after.status_code == 200
    assert sum_res_after.json()["percentage"] == 100.0
    assert sum_res_after.json()["status"] == "ABOVE_THRESHOLD"


@pytest.mark.asyncio
async def test_bulk_attendance_and_duplicate_prevention(client: AsyncClient):
    # Register org & teacher
    admin_res = await client.post(
        "/auth/register",
        json={
            "email": f"hod_cs_{uuid.uuid4().hex[:6]}@somaiya.edu",
            "password": "Password123!",
            "org_name": "Somaiya College",
            "org_type": "COLLEGE",
            "full_name": "Prof. Sharma",
        },
    )
    assert admin_res.status_code == 201
    admin_token = admin_res.json()["tokens"]["access_token"]
    admin_auth = {"Authorization": f"Bearer {admin_token}"}

    # Add 2 students
    s1_res = await client.post(
        "/organizations/members",
        headers=admin_auth,
        json={"email": f"s1_{uuid.uuid4().hex[:6]}@somaiya.edu", "password": "Pass123!", "full_name": "Student 1", "role": "STUDENT"},
    )
    s2_res = await client.post(
        "/organizations/members",
        headers=admin_auth,
        json={"email": f"s2_{uuid.uuid4().hex[:6]}@somaiya.edu", "password": "Pass123!", "full_name": "Student 2", "role": "STUDENT"},
    )
    s1_id = s1_res.json()["id"]
    s2_id = s2_res.json()["id"]

    # Create a schedule and slot
    sched_res = await client.post(
        "/api/v1/schedules",
        headers=admin_auth,
        json={
            "title": "Computer Networks Lecture",
            "type": "CLASS",
            "slots": [
                {
                    "day_of_week": 0,
                    "start_time": "09:00:00",
                    "end_time": "10:00:00",
                    "title": "CN Lab Room 101",
                }
            ],
        },
    )
    assert sched_res.status_code == 201
    slot_id = sched_res.json()["slots"][0]["id"]

    # Bulk mark attendance for the class
    bulk_res = await client.post(
        "/api/v1/attendance/bulk",
        headers=admin_auth,
        json={
            "schedule_slot_id": slot_id,
            "date": "2026-09-28",
            "records": [
                {"user_id": s1_id, "status": "PRESENT", "remarks": "Present in lab"},
                {"user_id": s2_id, "status": "LATE", "remarks": "Arrived 10m late"},
            ],
        },
    )
    assert bulk_res.status_code == 200
    assert len(bulk_res.json()) == 2

    # Attempting duplicate single POST on same slot and date returns 409
    dup_res = await client.post(
        "/api/v1/attendance",
        headers=admin_auth,
        json={
            "user_id": s1_id,
            "schedule_slot_id": slot_id,
            "date": "2026-09-28",
            "status": "PRESENT",
        },
    )
    assert dup_res.status_code == 409


@pytest.mark.asyncio
async def test_attendance_tenant_isolation_and_idor(client: AsyncClient):
    # Org A: Company Alpha
    res_a = await client.post(
        "/auth/register",
        json={
            "email": f"hr_{uuid.uuid4().hex[:6]}@alpha.com",
            "password": "Password123!",
            "org_name": "Alpha Corp",
            "org_type": "COMPANY",
            "full_name": "HR Alpha",
        },
    )
    token_a = res_a.json()["tokens"]["access_token"]
    auth_a = {"Authorization": f"Bearer {token_a}"}

    # Add employee in Org A
    emp_a = await client.post(
        "/organizations/members",
        headers=auth_a,
        json={"email": f"emp_{uuid.uuid4().hex[:6]}@alpha.com", "password": "Pass123!", "full_name": "Emp Alpha", "role": "EMPLOYEE"},
    )
    emp_a_id = emp_a.json()["id"]

    # Mark attendance for employee in Org A
    rec_a = await client.post(
        "/api/v1/attendance",
        headers=auth_a,
        json={"user_id": emp_a_id, "date": "2026-09-28", "status": "PRESENT"},
    )
    assert rec_a.status_code == 201
    rec_a_id = rec_a.json()["id"]

    # Org B: Company Beta
    res_b = await client.post(
        "/auth/register",
        json={
            "email": f"hr_{uuid.uuid4().hex[:6]}@beta.com",
            "password": "Password123!",
            "org_name": "Beta Corp",
            "org_type": "COMPANY",
            "full_name": "HR Beta",
        },
    )
    token_b = res_b.json()["tokens"]["access_token"]
    auth_b = {"Authorization": f"Bearer {token_b}"}

    # Org B admin tries to correct Org A's attendance record (IDOR) -> 404
    idor_res = await client.patch(
        f"/api/v1/attendance/{rec_a_id}",
        headers=auth_b,
        json={"status": "ABSENT", "reason": "Malicious modification attempt"},
    )
    assert idor_res.status_code == 404

    # Org B admin tries to mark attendance for Org A employee (Cross-tenant user) -> 404
    cross_mark = await client.post(
        "/api/v1/attendance",
        headers=auth_b,
        json={"user_id": emp_a_id, "date": "2026-09-29", "status": "PRESENT"},
    )
    assert cross_mark.status_code == 404
