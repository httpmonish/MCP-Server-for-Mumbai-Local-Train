import uuid
from datetime import date, datetime, time, timedelta, timezone

import pytest
from app.schemas.intelligence import (
    CombinedRiskStatus,
    CommuteStatus,
    IntelligenceConfidence,
    ReasonCode,
)
from app.services.intelligence_calculator import (
    calculate_arrival_margin_minutes,
    calculate_final_arrival_time,
    calculate_required_arrival_time,
    classify_attendance_status,
    classify_commute_status,
    evaluate_combined_risk,
    evaluate_confidence,
)
from httpx import AsyncClient


def test_pure_intelligence_time_and_margin_calculations():
    # 09:00 start with 10m buffer = 08:50 required arrival
    req = calculate_required_arrival_time("09:00:00", arrival_buffer_minutes=10)
    assert req == "08:50:00"

    # Train arrival 08:35 + 0m delay + 5m walk = 08:40 final arrival
    final_arr = calculate_final_arrival_time("08:35:00", delay_minutes=0, last_mile_minutes=5)
    assert final_arr == "08:40:00"

    # Margin: 08:50 - 08:40 = +10 minutes (comfortable)
    margin = calculate_arrival_margin_minutes(req, final_arr)
    assert margin == 10

    status, reasons = classify_commute_status(margin, has_transit=True)
    assert status == CommuteStatus.ON_TIME
    assert ReasonCode.ON_TIME_COMFORTABLE_MARGIN.value in reasons

    # Late scenario: Train arrives 08:52 + 5m walk = 08:57
    late_final = calculate_final_arrival_time("08:52:00", delay_minutes=0, last_mile_minutes=5)
    late_margin = calculate_arrival_margin_minutes(req, late_final)
    assert late_margin == -7  # 7 minutes late

    late_status, late_reasons = classify_commute_status(late_margin, has_transit=True)
    assert late_status == CommuteStatus.LIKELY_LATE
    assert ReasonCode.ARRIVAL_AFTER_REQUIRED_TIME.value in late_reasons

    # Low margin / tight buffer scenario: 08:48 final arrival -> margin = +2 minutes
    tight_final = calculate_final_arrival_time("08:43:00", delay_minutes=0, last_mile_minutes=5)
    tight_margin = calculate_arrival_margin_minutes(req, tight_final)
    assert tight_margin == 2

    tight_status, tight_reasons = classify_commute_status(tight_margin, has_transit=True)
    assert tight_status == CommuteStatus.AT_RISK
    assert ReasonCode.LOW_ARRIVAL_MARGIN.value in tight_reasons


def test_pure_intelligence_combined_risk_matrix():
    # 1. On time + Above threshold -> NORMAL
    assert evaluate_combined_risk(CommuteStatus.ON_TIME, "ABOVE_THRESHOLD", has_schedule=True) == CombinedRiskStatus.NORMAL

    # 2. On time + Below threshold -> ATTENDANCE_RISK
    assert evaluate_combined_risk(CommuteStatus.ON_TIME, "BELOW_THRESHOLD", has_schedule=True) == CombinedRiskStatus.ATTENDANCE_RISK

    # 3. Late + Above threshold -> COMMUTE_RISK
    assert evaluate_combined_risk(CommuteStatus.LIKELY_LATE, "ABOVE_THRESHOLD", has_schedule=True) == CombinedRiskStatus.COMMUTE_RISK

    # 4. Late + Below threshold -> COMBINED_RISK
    assert evaluate_combined_risk(CommuteStatus.LIKELY_LATE, "BELOW_THRESHOLD", has_schedule=True) == CombinedRiskStatus.COMBINED_RISK

    # 5. At risk + Near threshold -> COMBINED_RISK
    assert evaluate_combined_risk(CommuteStatus.AT_RISK, "NEAR_THRESHOLD", has_schedule=True) == CombinedRiskStatus.COMBINED_RISK

    # 6. No upcoming schedule -> NO_UPCOMING_SCHEDULE
    assert evaluate_combined_risk(CommuteStatus.ON_TIME, "ABOVE_THRESHOLD", has_schedule=False) == CombinedRiskStatus.NO_UPCOMING_SCHEDULE


def test_pure_intelligence_confidence_and_provenance():
    # Fresh live data -> HIGH confidence
    conf_high = evaluate_confidence("REALTIME", "FRESH", has_schedule=True, has_transit=True)
    assert conf_high == IntelligenceConfidence.HIGH

    # Static timetable fallback -> MEDIUM confidence
    conf_med = evaluate_confidence("STATIC_TIMETABLE", "FRESH", has_schedule=True, has_transit=True)
    assert conf_med == IntelligenceConfidence.MEDIUM

    # No transit -> LOW confidence
    conf_low = evaluate_confidence("UNAVAILABLE", "UNAVAILABLE", has_schedule=True, has_transit=False)
    assert conf_low == IntelligenceConfidence.LOW


@pytest.mark.asyncio
async def test_commute_check_e2e_integration_flow(client: AsyncClient):
    # 1. Register College Organization & Admin
    admin_email = f"dean_{uuid.uuid4().hex[:6]}@vjti.ac.in"
    reg_res = await client.post(
        "/auth/register",
        json={
            "org_name": "VJTI Mumbai Engineering",
            "org_type": "COLLEGE",
            "email": admin_email,
            "password": "SecurePassword123!",
        },
    )
    assert reg_res.status_code == 201
    admin_token = reg_res.json()["tokens"]["access_token"]
    admin_auth = {"Authorization": f"Bearer {admin_token}"}

    # 2. Create Campus Location (Nearest Station: Dadar / DR)
    loc_res = await client.post(
        "/api/v1/locations",
        headers=admin_auth,
        json={
            "name": "VJTI Matunga Campus",
            "nearest_station_code": "DR",
        },
    )
    assert loc_res.status_code == 201
    loc_id = loc_res.json()["id"]

    # 3. Create Class Schedule with a morning lecture on Mondays (day 0) and Tuesdays (day 1), etc.
    sched_res = await client.post(
        "/api/v1/schedules",
        headers=admin_auth,
        json={
            "title": "Computer Engineering Sem VI",
            "type": "CLASS",
            "slots": [
                {
                    "day_of_week": d,
                    "start_time": "09:30:00",
                    "end_time": "10:30:00",
                    "title": "CS-602 Database Systems",
                    "location_id": loc_id,
                    "location_name": "VJTI Matunga Campus",
                }
                for d in range(7)  # All days to guarantee match
            ],
        },
    )
    assert sched_res.status_code == 201
    sched_id = sched_res.json()["id"]

    # 4. Add Student Member
    stud_email = f"aditya_{uuid.uuid4().hex[:6]}@vjti.ac.in"
    mem_res = await client.post(
        "/organizations/members",
        headers=admin_auth,
        json={
            "email": stud_email,
            "password": "StudentPassword123!",
            "full_name": "Aditya Sharma",
            "role": "STUDENT",
        },
    )
    assert mem_res.status_code == 201
    student_id = mem_res.json()["id"]

    # 5. Assign Schedule to Student
    today = datetime.now(timezone.utc).date()
    assign_res = await client.post(
        f"/api/v1/schedules/{sched_id}/assign",
        headers=admin_auth,
        json={
            "user_ids": [student_id],
            "valid_from": (today - timedelta(days=1)).isoformat(),
            "valid_until": (today + timedelta(days=30)).isoformat(),
        },
    )
    assert assign_res.status_code == 201

    # 6. Create Policy & Mark Attendance (e.g. 2 present, 1 absent = 66.7% vs 75% -> BELOW_THRESHOLD)
    await client.post(
        "/api/v1/attendance/policies",
        headers=admin_auth,
        json={
            "name": "Statutory 75% Rule",
            "applies_to": "STUDENT",
            "min_percentage": 75.0,
        },
    )
    await client.post(
        "/api/v1/attendance",
        headers=admin_auth,
        json={"user_id": student_id, "date": "2026-09-01", "status": "PRESENT"},
    )
    await client.post(
        "/api/v1/attendance",
        headers=admin_auth,
        json={"user_id": student_id, "date": "2026-09-02", "status": "PRESENT"},
    )
    await client.post(
        "/api/v1/attendance",
        headers=admin_auth,
        json={"user_id": student_id, "date": "2026-09-03", "status": "ABSENT"},
    )

    # 7. Student logs in
    stud_login = await client.post(
        "/auth/login",
        json={"email": stud_email, "password": "StudentPassword123!"},
    )
    assert stud_login.status_code == 200
    student_token = stud_login.json()["tokens"]["access_token"]
    student_auth = {"Authorization": f"Bearer {student_token}"}

    # 8. Call GET /api/v1/intelligence/commute-check at 08:30:00 (Thane -> Dadar)
    # Lecture is at 09:30. Required arrival is 09:20 (with 10m buffer).
    # Morning trains from Thane arrive Dadar around 08:40 - 09:15.
    intel_res = await client.get(
        "/api/v1/intelligence/commute-check?from_station=THANE&at_time=08:30:00",
        headers=student_auth,
    )
    assert intel_res.status_code == 200
    intel_data = intel_res.json()

    assert intel_data["schedule"]["title"] == "CS-602 Database Systems"
    assert intel_data["schedule"]["destination_station"] == "DR"
    assert intel_data["schedule"]["required_arrival_time"] == "09:20:00"

    assert intel_data["commute"]["origin_station"] == "THANE"
    assert intel_data["commute"]["destination_station"] == "DR"
    assert intel_data["commute"]["status"] in ("ON_TIME", "AT_RISK", "LIKELY_LATE")

    assert intel_data["attendance"]["percentage"] == 66.67
    assert intel_data["attendance"]["status"] == "BELOW_THRESHOLD"

    # Because attendance is below threshold:
    assert intel_data["combined_status"] in (
        CombinedRiskStatus.ATTENDANCE_RISK.value,
        CombinedRiskStatus.COMBINED_RISK.value,
    )
    assert ReasonCode.ATTENDANCE_BELOW_THRESHOLD.value in intel_data["reason_codes"]
    assert "CS-602 Database Systems" in intel_data["decision_summary"]
    assert intel_data["data_provenance"]["confidence"] in ("HIGH", "MEDIUM")


@pytest.mark.asyncio
async def test_commute_check_no_schedule_case(client: AsyncClient):
    # Register user with no assigned schedule
    user_email = f"emp_{uuid.uuid4().hex[:6]}@company.com"
    reg_res = await client.post(
        "/auth/register",
        json={
            "org_name": "Beta Corp",
            "org_type": "COMPANY",
            "email": user_email,
            "password": "Password123!",
        },
    )
    token = reg_res.json()["tokens"]["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    res = await client.get(
        "/api/v1/intelligence/commute-check?from_station=THANE&at_time=10:00:00",
        headers=auth_headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["combined_status"] == CombinedRiskStatus.NO_UPCOMING_SCHEDULE.value
    assert ReasonCode.NO_SCHEDULE_FOUND.value in data["reason_codes"]
    assert "No upcoming classes or shifts" in data["decision_summary"]
