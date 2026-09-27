import uuid
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_location_and_class_schedule_lifecycle(client: AsyncClient):
    # 1. Register College Organization
    admin_email = f"dean_{uuid.uuid4().hex[:6]}@vjti.ac.in"
    reg_res = await client.post(
        "/auth/register",
        json={
            "org_name": "VJTI Mumbai Engineering",
            "org_type": "COLLEGE",
            "org_domain": "vjti.ac.in",
            "email": admin_email,
            "password": "SecurePassword123!",
        },
    )
    assert reg_res.status_code == 201
    admin_token = reg_res.json()["tokens"]["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Create Campus Location with nearest transit station
    loc_res = await client.post(
        "/api/v1/locations",
        headers=admin_headers,
        json={
            "name": "Matunga Engineering Campus",
            "address": "HR Mahajani Rd, Matunga, Mumbai",
            "latitude": 19.0222,
            "longitude": 72.8561,
            "nearest_station_code": "MTN",
        },
    )
    assert loc_res.status_code == 201
    loc_id = loc_res.json()["id"]
    assert loc_res.json()["nearest_station_code"] == "MTN"

    # 3. Create Class Schedule with Weekly Slots
    sched_res = await client.post(
        "/api/v1/schedules",
        headers=admin_headers,
        json={
            "title": "CSE Semester 5 Timetable",
            "type": "CLASS",
            "timezone": "Asia/Kolkata",
            "description": "Third year Computer Science weekly timetable",
            "slots": [
                {
                    "day_of_week": 0,  # Monday
                    "start_time": "09:00:00",
                    "end_time": "10:00:00",
                    "title": "Computer Networks",
                    "location_id": loc_id,
                    "location_name": "Lab 301",
                    "instructor_or_supervisor": "Prof. Sharma",
                },
                {
                    "day_of_week": 0,  # Monday
                    "start_time": "10:15:00",
                    "end_time": "11:15:00",
                    "title": "Database Management Systems",
                    "location_id": loc_id,
                    "location_name": "Room 402",
                    "instructor_or_supervisor": "Dr. Kulkarni",
                },
                {
                    "day_of_week": 2,  # Wednesday
                    "start_time": "11:30:00",
                    "end_time": "12:30:00",
                    "title": "Algorithms",
                    "location_id": loc_id,
                    "location_name": "Room 402",
                },
            ],
        },
    )
    assert sched_res.status_code == 201
    sched_data = sched_res.json()
    assert sched_data["title"] == "CSE Semester 5 Timetable"
    assert len(sched_data["slots"]) == 3
    sched_id = sched_data["id"]

    # 4. Add Student Member
    stud_email = f"student_{uuid.uuid4().hex[:6]}@vjti.ac.in"
    member_res = await client.post(
        "/organizations/members",
        headers=admin_headers,
        json={
            "email": stud_email,
            "role": "STUDENT",
            "full_name": "Aarav Mehta",
            "password": "StudentPassword123!",
        },
    )
    assert member_res.status_code == 201
    student_id = member_res.json()["id"]

    # 5. Assign Schedule to Student
    today = datetime.now(ZoneInfo("Asia/Kolkata")).date()
    assign_res = await client.post(
        f"/api/v1/schedules/{sched_id}/assign",
        headers=admin_headers,
        json={
            "user_ids": [student_id],
            "valid_from": (today - timedelta(days=7)).isoformat(),
            "valid_until": (today + timedelta(days=90)).isoformat(),
        },
    )
    assert assign_res.status_code == 201
    assert len(assign_res.json()) == 1

    # 6. Login as Student and Query Today's Schedule
    stud_login = await client.post(
        "/auth/login",
        json={"email": stud_email, "password": "StudentPassword123!"},
    )
    stud_token = stud_login.json()["tokens"]["access_token"]
    stud_headers = {"Authorization": f"Bearer {stud_token}"}

    today_res = await client.get("/api/v1/schedules/me/today", headers=stud_headers)
    assert today_res.status_code == 200
    today_data = today_res.json()
    assert today_data["timezone"] == "Asia/Kolkata"

    # If today is Monday (day 0), should have 2 classes
    if today.weekday() == 0:
        assert today_data["count"] == 2
        assert today_data["items"][0]["title"] == "Computer Networks"
        assert today_data["items"][0]["nearest_station_code"] == "MTN"

    # 7. Query Weekly Schedule
    week_res = await client.get("/api/v1/schedules/me/week", headers=stud_headers)
    assert week_res.status_code == 200
    week_data = week_res.json()
    assert len(week_data["days"]) == 7
    # Total occurrences across week: Monday (2) + Wednesday (1) = 3
    assert week_data["total_occurrences"] == 3


@pytest.mark.asyncio
async def test_employee_overnight_shift_lifecycle(client: AsyncClient):
    # 1. Register Company
    admin_email = f"hr_{uuid.uuid4().hex[:6]}@techcorp.in"
    reg_res = await client.post(
        "/auth/register",
        json={
            "org_name": "TechCorp Logistics BKC",
            "org_type": "COMPANY",
            "org_domain": "techcorp.in",
            "email": admin_email,
            "password": "SecurePassword123!",
        },
    )
    admin_token = reg_res.json()["tokens"]["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Create Night Shift Schedule (Crossing midnight 22:00 -> 06:00)
    shift_res = await client.post(
        "/api/v1/schedules",
        headers=admin_headers,
        json={
            "title": "Night Operations Shift",
            "type": "SHIFT",
            "timezone": "Asia/Kolkata",
            "slots": [
                {
                    "day_of_week": i,
                    "start_time": "22:00:00",
                    "end_time": "06:00:00",
                    "title": "Night Operations Shift",
                    "location_name": "BKC Control Center",
                }
                for i in range(5)  # Mon-Fri
            ],
        },
    )
    assert shift_res.status_code == 201
    shift_data = shift_res.json()
    assert all(s["is_overnight"] is True for s in shift_data["slots"])


@pytest.mark.asyncio
async def test_schedule_multi_tenant_security(client: AsyncClient):
    # 1. Tenant A (College)
    reg_a = await client.post(
        "/auth/register",
        json={
            "org_name": "College A",
            "org_type": "COLLEGE",
            "org_domain": "college-a.edu",
            "email": f"admin_{uuid.uuid4().hex[:6]}@college-a.edu",
            "password": "SecurePassword123!",
        },
    )
    token_a = reg_a.json()["tokens"]["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Create Schedule in Org A
    sched_a = await client.post(
        "/api/v1/schedules",
        headers=headers_a,
        json={"title": "Org A Timetable", "type": "CLASS"},
    )
    sched_a_id = sched_a.json()["id"]

    # 2. Tenant B (Company)
    reg_b = await client.post(
        "/auth/register",
        json={
            "org_name": "Company B",
            "org_type": "COMPANY",
            "org_domain": "company-b.com",
            "email": f"admin_{uuid.uuid4().hex[:6]}@company-b.com",
            "password": "SecurePassword123!",
        },
    )
    token_b = reg_b.json()["tokens"]["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 3. IDOR Attack: Admin B tries to GET Org A's schedule -> 404
    attack_get = await client.get(f"/api/v1/schedules/{sched_a_id}", headers=headers_b)
    assert attack_get.status_code == 404

    # 4. IDOR Attack: Admin B tries to DELETE Org A's schedule -> 404
    attack_del = await client.delete(f"/api/v1/schedules/{sched_a_id}", headers=headers_b)
    assert attack_del.status_code == 404

    # 5. IDOR Attack: Admin B tries to assign Org A's schedule to Org B user -> 404
    attack_assign = await client.post(
        f"/api/v1/schedules/{sched_a_id}/assign",
        headers=headers_b,
        json={"user_ids": [str(uuid.uuid4())], "valid_from": "2026-09-01"},
    )
    assert attack_assign.status_code == 404
