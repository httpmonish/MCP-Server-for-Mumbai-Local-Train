from datetime import datetime, time, timedelta
from typing import List, Optional, Tuple

from app.schemas.attendance import AttendanceSummaryResponse
from app.schemas.intelligence import (
    CombinedRiskStatus,
    CommuteStatus,
    IntelligenceConfidence,
    ReasonCode,
)


def parse_time_to_minutes(time_str: str) -> int:
    """Convert 'HH:MM' or 'HH:MM:SS' string to total minutes since midnight."""
    parts = [int(p) for p in time_str.strip().split(":")]
    return parts[0] * 60 + parts[1]


def minutes_to_time_str(total_minutes: int) -> str:
    """Convert total minutes back to 'HH:MM:SS' string (wrapping around 24 hours if needed)."""
    norm = total_minutes % (24 * 60)
    hours = norm // 60
    mins = norm % 60
    return f"{hours:02d}:{mins:02d}:00"


def calculate_required_arrival_time(start_time_str: str, arrival_buffer_minutes: int = 10) -> str:
    """Subtracts the required buffer before lecture/shift start time."""
    start_mins = parse_time_to_minutes(start_time_str)
    req_mins = start_mins - arrival_buffer_minutes
    return minutes_to_time_str(req_mins)


def calculate_final_arrival_time(
    train_arrival_str: str,
    delay_minutes: int = 0,
    last_mile_minutes: int = 5,
) -> str:
    """Adds train delay and last-mile walking time to train arrival time."""
    arrival_mins = parse_time_to_minutes(train_arrival_str)
    total_mins = arrival_mins + delay_minutes + last_mile_minutes
    return minutes_to_time_str(total_mins)


def calculate_arrival_margin_minutes(required_arrival_str: str, final_arrival_str: str) -> int:
    """
    Computes arrival margin = required_arrival - final_arrival.
    Positive value means arriving before required time (comfortable buffer).
    Negative value means arriving late.
    """
    req_mins = parse_time_to_minutes(required_arrival_str)
    final_mins = parse_time_to_minutes(final_arrival_str)
    diff = req_mins - final_mins

    # Handle crossing midnight: if diff is huge, normalize
    if diff < -720:
        diff += 1440
    elif diff > 720:
        diff -= 1440
    return diff


def classify_commute_status(
    arrival_margin_minutes: Optional[int],
    has_transit: bool,
) -> Tuple[CommuteStatus, List[str]]:
    """
    Classifies commute status based on arrival margin:
    - margin > 5 min -> ON_TIME
    - 0 <= margin <= 5 min -> AT_RISK (low buffer)
    - margin < 0 -> LIKELY_LATE
    """
    if not has_transit or arrival_margin_minutes is None:
        return CommuteStatus.NO_DATA, [ReasonCode.NO_TRANSIT_OPTIONS_AVAILABLE.value]

    if arrival_margin_minutes < 0:
        return CommuteStatus.LIKELY_LATE, [ReasonCode.ARRIVAL_AFTER_REQUIRED_TIME.value]
    elif 0 <= arrival_margin_minutes <= 5:
        return CommuteStatus.AT_RISK, [ReasonCode.LOW_ARRIVAL_MARGIN.value]
    else:
        return CommuteStatus.ON_TIME, [ReasonCode.ON_TIME_COMFORTABLE_MARGIN.value]


def classify_attendance_status(
    summary: Optional[AttendanceSummaryResponse],
) -> Tuple[str, List[str]]:
    """
    Classifies attendance standing from Phase 5 summary.
    """
    if not summary or summary.counted_sessions == 0:
        return "NO_DATA", []

    if summary.percentage < summary.min_percentage_required:
        return "BELOW_THRESHOLD", [ReasonCode.ATTENDANCE_BELOW_THRESHOLD.value]
    elif summary.percentage - summary.min_percentage_required <= 2.0:
        return "NEAR_THRESHOLD", [ReasonCode.ATTENDANCE_NEAR_THRESHOLD.value]
    else:
        return "ABOVE_THRESHOLD", [ReasonCode.ATTENDANCE_HEALTHY.value]


def evaluate_combined_risk(
    commute_status: CommuteStatus,
    attendance_status: str,
    has_schedule: bool,
) -> CombinedRiskStatus:
    """
    Deterministic combined risk evaluation matrix.
    """
    if not has_schedule:
        return CombinedRiskStatus.NO_UPCOMING_SCHEDULE

    if commute_status == CommuteStatus.NO_DATA:
        if attendance_status == "BELOW_THRESHOLD":
            return CombinedRiskStatus.ATTENDANCE_RISK
        return CombinedRiskStatus.INSUFFICIENT_DATA

    if commute_status == CommuteStatus.ON_TIME:
        if attendance_status == "BELOW_THRESHOLD":
            return CombinedRiskStatus.ATTENDANCE_RISK
        elif attendance_status == "NEAR_THRESHOLD":
            return CombinedRiskStatus.ATTENDANCE_NEAR_THRESHOLD
        else:
            return CombinedRiskStatus.NORMAL

    elif commute_status == CommuteStatus.AT_RISK:
        if attendance_status in ("BELOW_THRESHOLD", "NEAR_THRESHOLD"):
            return CombinedRiskStatus.COMBINED_RISK
        else:
            return CombinedRiskStatus.COMMUTE_RISK

    elif commute_status == CommuteStatus.LIKELY_LATE:
        if attendance_status in ("BELOW_THRESHOLD", "NEAR_THRESHOLD"):
            return CombinedRiskStatus.COMBINED_RISK
        else:
            return CombinedRiskStatus.COMMUTE_RISK

    return CombinedRiskStatus.INSUFFICIENT_DATA


def evaluate_confidence(
    transit_data_label: str,
    transit_freshness: str,
    has_schedule: bool,
    has_transit: bool,
) -> IntelligenceConfidence:
    """
    Evaluates confidence score based on data provenance.
    """
    if not has_schedule or not has_transit:
        return IntelligenceConfidence.LOW

    if transit_data_label == "REALTIME" and transit_freshness == "FRESH":
        return IntelligenceConfidence.HIGH
    elif transit_data_label in ("STATIC_TIMETABLE", "REALTIME") and transit_freshness in ("FRESH", "STALE"):
        return IntelligenceConfidence.MEDIUM
    elif transit_freshness == "EXPIRED" or transit_data_label == "UNAVAILABLE":
        return IntelligenceConfidence.LOW

    return IntelligenceConfidence.MEDIUM


def build_decision_summary(
    schedule_title: Optional[str],
    start_time: Optional[str],
    final_arrival: Optional[str],
    margin_minutes: Optional[int],
    commute_status: CommuteStatus,
    attendance_status: str,
    attendance_percentage: Optional[float],
    combined_status: CombinedRiskStatus,
) -> str:
    """
    Builds a factual, objective, non-judgmental decision summary.
    """
    if combined_status == CombinedRiskStatus.NO_UPCOMING_SCHEDULE:
        return "No upcoming classes or shifts scheduled for today."

    parts = []
    if schedule_title and start_time:
        parts.append(f"Next session: {schedule_title} starts at {start_time}.")

    if final_arrival and margin_minutes is not None:
        if margin_minutes >= 0:
            parts.append(f"Estimated campus arrival: {final_arrival} (+{margin_minutes}m margin).")
        else:
            parts.append(f"Estimated campus arrival: {final_arrival} ({margin_minutes}m late).")

    if attendance_percentage is not None:
        parts.append(f"Current attendance: {attendance_percentage:.1f}% ({attendance_status.replace('_', ' ').lower()}).")

    if combined_status == CombinedRiskStatus.COMBINED_RISK:
        parts.append("Status: COMBINED RISK — Both transit delay and attendance shortage present.")
    elif combined_status == CombinedRiskStatus.COMMUTE_RISK:
        parts.append("Status: COMMUTE RISK — Transit arrival is after required arrival buffer.")
    elif combined_status == CombinedRiskStatus.ATTENDANCE_RISK:
        parts.append("Status: ATTENDANCE RISK — Attendance is currently below statutory threshold.")
    elif combined_status == CombinedRiskStatus.ATTENDANCE_NEAR_THRESHOLD:
        parts.append("Status: ATTENDANCE CAUTION — Attendance is within 2% of threshold.")
    elif combined_status == CombinedRiskStatus.NORMAL:
        parts.append("Status: ON TIME — Transit timing is comfortable and attendance is healthy.")
    else:
        parts.append(f"Status: {combined_status.value.replace('_', ' ')}.")

    return " ".join(parts)
