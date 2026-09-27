import logging
import uuid
from datetime import date, datetime, time, timedelta, timezone
from typing import List, Optional
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import RedisCache
from app.models.auth import User
from app.schemas.attendance import AttendanceSummaryResponse
from app.schemas.intelligence import (
    AttendanceIntelligenceFact,
    CombinedRiskStatus,
    CommuteCheckResponse,
    CommuteIntelligenceFact,
    CommuteStatus,
    DataProvenanceFact,
    IntelligenceConfidence,
    ReasonCode,
    ScheduleIntelligenceFact,
)
from app.services.attendance_service import AttendanceService
from app.services.intelligence_calculator import (
    build_decision_summary,
    calculate_arrival_margin_minutes,
    calculate_final_arrival_time,
    calculate_required_arrival_time,
    classify_attendance_status,
    classify_commute_status,
    evaluate_combined_risk,
    evaluate_confidence,
)
from app.services.schedule_service import ScheduleEngineService
from app.services.transit_service import TransitEngineService

logger = logging.getLogger("intelligence_service")


class IntelligenceService:
    @staticmethod
    async def evaluate_commute_check(
        db: AsyncSession,
        user: User,
        from_station: str,
        at_time: Optional[str] = None,
        arrival_buffer_minutes: int = 10,
        last_mile_minutes: int = 5,
        cache: Optional[RedisCache] = None,
    ) -> CommuteCheckResponse:
        """
        Orchestrates Transit, Schedule, and Attendance data into a single explainable intelligence fact.
        Pure deterministic evaluation with data provenance.
        """
        tz_str = "Asia/Kolkata"
        try:
            user_tz = ZoneInfo(tz_str)
        except Exception:
            user_tz = timezone.utc

        now_dt = datetime.now(user_tz)
        if at_time:
            parts = [int(p) for p in at_time.strip().split(":")]
            query_time = time(parts[0], parts[1], parts[2] if len(parts) > 2 else 0)
        else:
            query_time = now_dt.time()

        q_time_str = query_time.strftime("%H:%M:%S")
        reason_codes: List[str] = []

        # 1. Query user's schedule occurrences for today (Phase 4)
        today_sched = await ScheduleEngineService.get_user_today_schedule(
            db=db,
            user=user,
            target_date=now_dt.date(),
        )

        upcoming_occurrence = None
        for item in today_sched.items:
            # Find next upcoming occurrence or currently active session
            if item.end_time >= q_time_str:
                upcoming_occurrence = item
                break

        # 2. Query user's attendance standing (Phase 5)
        attendance_summary: Optional[AttendanceSummaryResponse] = None
        try:
            attendance_summary = await AttendanceService.get_user_summary(
                db=db,
                org_id=user.org_id,
                user_id=user.id,
            )
        except Exception as e:
            logger.warning(f"Could not retrieve attendance summary for user {user.id}: {e}")

        # Classify Attendance Fact
        att_status, att_reasons = classify_attendance_status(attendance_summary)
        reason_codes.extend(att_reasons)

        attendance_fact = None
        if attendance_summary:
            attendance_fact = AttendanceIntelligenceFact(
                percentage=attendance_summary.percentage,
                min_percentage_required=attendance_summary.min_percentage_required,
                status=att_status,
                shortage_percentage=attendance_summary.shortage_percentage,
                sessions_needed_to_recover=attendance_summary.sessions_needed_to_recover,
                total_sessions=attendance_summary.total_sessions,
                counted_sessions=attendance_summary.counted_sessions,
                policy_name=attendance_summary.policy_name,
            )

        # If no upcoming schedule today
        if not upcoming_occurrence:
            reason_codes.append(ReasonCode.NO_SCHEDULE_FOUND.value)
            combined_status = CombinedRiskStatus.NO_UPCOMING_SCHEDULE
            provenance = DataProvenanceFact(
                transit_source="NONE",
                data_label="UNAVAILABLE",
                freshness="UNAVAILABLE",
                confidence=IntelligenceConfidence.HIGH,
                last_updated=now_dt,
            )
            summary_text = build_decision_summary(
                schedule_title=None,
                start_time=None,
                final_arrival=None,
                margin_minutes=None,
                commute_status=CommuteStatus.NO_DATA,
                attendance_status=att_status,
                attendance_percentage=attendance_summary.percentage if attendance_summary else None,
                combined_status=combined_status,
            )
            return CommuteCheckResponse(
                rules_version="1.0.0",
                user_id=user.id,
                evaluated_at=now_dt,
                schedule=None,
                commute=None,
                attendance=attendance_fact,
                combined_status=combined_status,
                reason_codes=reason_codes,
                decision_summary=summary_text,
                data_provenance=provenance,
            )

        # 3. Resolve Destination Transit Access Point
        dest_station = (
            upcoming_occurrence.nearest_station_code
            or (upcoming_occurrence.location_name.split()[0] if upcoming_occurrence.location_name else "DR")
        ).upper()

        req_arrival_str = calculate_required_arrival_time(
            upcoming_occurrence.start_time,
            arrival_buffer_minutes=arrival_buffer_minutes,
        )

        schedule_fact = ScheduleIntelligenceFact(
            slot_id=upcoming_occurrence.slot_id,
            title=upcoming_occurrence.title,
            schedule_type=upcoming_occurrence.schedule_type.value,
            start_time=upcoming_occurrence.start_time,
            end_time=upcoming_occurrence.end_time,
            location_name=upcoming_occurrence.location_name,
            destination_station=dest_station,
            required_arrival_time=req_arrival_str,
            is_overnight=upcoming_occurrence.is_overnight,
            instructor_or_supervisor=upcoming_occurrence.instructor_or_supervisor,
        )

        # 4. Query Transit Engine for Candidate Trains (Phase 3)
        candidate_trains = []
        transit_meta = None
        try:
            trains_resp = await TransitEngineService.get_next_trains(
                from_stn=from_station,
                to_stn=dest_station,
                query_time=query_time,
                limit=4,
                include_live=True,
                cache=cache,
            )
            candidate_trains = trains_resp.trains
            transit_meta = trains_resp.meta
        except Exception as e:
            logger.warning(f"Transit lookup failed between {from_station} and {dest_station}: {e}")

        # 5. Evaluate Commute Timing and Margin
        commute_fact: Optional[CommuteIntelligenceFact] = None
        if candidate_trains:
            best_train = candidate_trains[0]
            delay = best_train.delay_minutes or 0
            station_arr = best_train.arrival_at_destination
            final_arr = calculate_final_arrival_time(
                station_arr,
                delay_minutes=delay,
                last_mile_minutes=last_mile_minutes,
            )
            margin = calculate_arrival_margin_minutes(req_arrival_str, final_arr)

            comm_status, comm_reasons = classify_commute_status(margin, has_transit=True)
            reason_codes.extend(comm_reasons)
            reason_codes.append(ReasonCode.LAST_MILE_BUFFER_APPLIED.value)

            if best_train.data_label == "STATIC_TIMETABLE":
                reason_codes.append(ReasonCode.STATIC_TIMETABLE_FALLBACK.value)
            elif best_train.data_label == "REALTIME":
                reason_codes.append(ReasonCode.LIVE_DATA_FRESH.value)

            commute_fact = CommuteIntelligenceFact(
                origin_station=from_station.upper(),
                destination_station=dest_station,
                train_number=best_train.train_number,
                train_type=best_train.train_type,
                line=best_train.line,
                scheduled_departure=best_train.departure_from_source,
                scheduled_arrival=best_train.arrival_at_destination,
                delay_minutes=delay,
                estimated_station_arrival=station_arr,
                estimated_final_arrival=final_arr,
                arrival_margin_minutes=margin,
                travel_time_minutes=best_train.travel_time_minutes,
                platform=best_train.platform,
                status=comm_status,
            )
        else:
            comm_status, comm_reasons = classify_commute_status(None, has_transit=False)
            reason_codes.extend(comm_reasons)
            commute_fact = CommuteIntelligenceFact(
                origin_station=from_station.upper(),
                destination_station=dest_station,
                delay_minutes=0,
                status=comm_status,
            )

        # 6. Evaluate Combined Risk State & Data Quality
        combined_status = evaluate_combined_risk(
            commute_status=commute_fact.status,
            attendance_status=att_status,
            has_schedule=True,
        )

        transit_label = transit_meta.data_label if transit_meta else "UNAVAILABLE"
        transit_freshness = transit_meta.freshness.value if transit_meta else "UNAVAILABLE"
        transit_src = transit_meta.source if transit_meta else "NONE"

        confidence = evaluate_confidence(
            transit_data_label=transit_label,
            transit_freshness=transit_freshness,
            has_schedule=True,
            has_transit=bool(candidate_trains),
        )

        provenance = DataProvenanceFact(
            transit_source=transit_src,
            data_label=transit_label,
            freshness=transit_freshness,
            confidence=confidence,
            last_updated=now_dt,
        )

        summary_text = build_decision_summary(
            schedule_title=schedule_fact.title,
            start_time=schedule_fact.start_time,
            final_arrival=commute_fact.estimated_final_arrival,
            margin_minutes=commute_fact.arrival_margin_minutes,
            commute_status=commute_fact.status,
            attendance_status=att_status,
            attendance_percentage=attendance_summary.percentage if attendance_summary else None,
            combined_status=combined_status,
        )

        return CommuteCheckResponse(
            rules_version="1.0.0",
            user_id=user.id,
            evaluated_at=now_dt,
            schedule=schedule_fact,
            commute=commute_fact,
            attendance=attendance_fact,
            combined_status=combined_status,
            reason_codes=list(dict.fromkeys(reason_codes)),  # Deduplicate preserving order
            decision_summary=summary_text,
            data_provenance=provenance,
        )
