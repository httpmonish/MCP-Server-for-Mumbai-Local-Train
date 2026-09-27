import math
import uuid
from datetime import date
from typing import List, Optional

from app.models.attendance import AttendanceRecord, AttendanceRiskStatus, AttendanceStatus
from app.schemas.attendance import AttendanceSummaryResponse


def calculate_attendance_summary(
    records: List[AttendanceRecord],
    min_percentage: float = 75.0,
    late_penalty_multiplier: float = 1.0,
    count_excused_in_denominator: bool = False,
    user_id: Optional[uuid.UUID] = None,
    org_id: Optional[uuid.UUID] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    policy_name: Optional[str] = None,
) -> AttendanceSummaryResponse:
    """
    Pure deterministic calculator for attendance aggregations, thresholds, and shortages.
    No DB or network dependencies.
    """
    total_sessions = len(records)
    present_count = 0
    late_count = 0
    absent_count = 0
    excused_count = 0
    cancelled_count = 0

    for r in records:
        if r.status == AttendanceStatus.PRESENT:
            present_count += 1
        elif r.status == AttendanceStatus.LATE:
            late_count += 1
        elif r.status == AttendanceStatus.ABSENT:
            absent_count += 1
        elif r.status == AttendanceStatus.EXCUSED:
            excused_count += 1
        elif r.status in (AttendanceStatus.CANCELLED, AttendanceStatus.HOLIDAY, AttendanceStatus.NOT_REQUIRED):
            cancelled_count += 1

    # Denominator calculation:
    # CANCELLED, HOLIDAY, and NOT_REQUIRED never count towards denominator.
    # EXCUSED is excluded unless count_excused_in_denominator is True.
    counted_sessions = present_count + late_count + absent_count
    if count_excused_in_denominator:
        counted_sessions += excused_count

    # Numerator calculation (points):
    attended_points = (present_count * 1.0) + (late_count * late_penalty_multiplier)
    # If excused is counted in denominator, check if any credit is given; standard is 0 unless present.

    if counted_sessions == 0:
        percentage = 100.0
    else:
        percentage = round((attended_points / counted_sessions) * 100.0, 2)

    # Threshold & Shortage calculation
    if percentage < min_percentage:
        status = AttendanceRiskStatus.BELOW_THRESHOLD
        shortage_percentage = round(min_percentage - percentage, 2)
        if min_percentage >= 100.0:
            sessions_needed_to_recover = -1 if percentage < 100.0 else 0
        else:
            diff = (min_percentage * counted_sessions) - (100.0 * attended_points)
            if diff > 0:
                sessions_needed_to_recover = math.ceil(diff / (100.0 - min_percentage))
            else:
                sessions_needed_to_recover = 0
    elif percentage - min_percentage <= 2.0:
        status = AttendanceRiskStatus.NEAR_THRESHOLD
        shortage_percentage = 0.0
        sessions_needed_to_recover = 0
    else:
        status = AttendanceRiskStatus.ABOVE_THRESHOLD
        shortage_percentage = 0.0
        sessions_needed_to_recover = 0

    return AttendanceSummaryResponse(
        user_id=user_id or (records[0].user_id if records else uuid.uuid4()),
        org_id=org_id or (records[0].org_id if records else uuid.uuid4()),
        start_date=start_date,
        end_date=end_date,
        total_sessions=total_sessions,
        counted_sessions=counted_sessions,
        present_count=present_count,
        late_count=late_count,
        absent_count=absent_count,
        excused_count=excused_count,
        cancelled_count=cancelled_count,
        percentage=percentage,
        min_percentage_required=min_percentage,
        status=status,
        shortage_percentage=shortage_percentage,
        sessions_needed_to_recover=sessions_needed_to_recover,
        policy_name=policy_name,
    )
