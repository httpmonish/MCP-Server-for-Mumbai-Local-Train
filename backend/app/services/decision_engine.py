from datetime import datetime, time
from typing import Any, Dict, List


class CommuteDecisionEngine:
    @staticmethod
    def _parse_time(t: Any) -> time:
        if isinstance(t, time):
            return t
        parts = str(t).strip().split(":")
        hour = int(parts[0])
        minute = int(parts[1])
        second = int(parts[2]) if len(parts) > 2 else 0
        return time(hour, minute, second)

    @classmethod
    def _calculate_buffer_minutes(cls, target: time, arrival: time) -> float:
        today = datetime.today().date()
        target_dt = datetime.combine(today, target)
        arrival_dt = datetime.combine(today, arrival)
        return (target_dt - arrival_dt).total_seconds() / 60.0

    def evaluate_commute_urgency(
        self,
        attendance_records: List[Dict[str, Any]],
        exam_records: List[Dict[str, Any]],
        available_trains: List[Dict[str, Any]],
        target_arrival_time: time,
    ) -> Dict[str, Any]:
        # 1. Analyze Academic Risk
        warning_subjects = [
            r["subject_name"]
            for r in attendance_records
            if float(r.get("percentage", 100.0)) < 75.0
        ]
        sub_70_subjects = [
            r["subject_name"]
            for r in attendance_records
            if float(r.get("percentage", 100.0)) < 70.0
        ]

        today_str = datetime.now().date().isoformat()
        has_exam_today = any(
            str(e.get("exam_date", "")).strip().lower() in (today_str, "today")
            or str(e.get("exam_date", "")).strip().startswith(today_str)
            for e in exam_records
        )

        if has_exam_today or len(sub_70_subjects) >= 2:
            risk_level = "HIGH"
            if has_exam_today:
                urgency_reason = "Final examination scheduled for today."
            else:
                urgency_reason = (
                    f"Multiple courses severely below 70%: {', '.join(sub_70_subjects)}"
                )
        elif len(warning_subjects) >= 1:
            risk_level = "MEDIUM"
            urgency_reason = (
                f"Attendance shortfall (<75%) in: {', '.join(warning_subjects)}"
            )
        else:
            risk_level = "LOW"
            urgency_reason = "Attendance in good standing (>75%) and no exams today."

        # 2. Transit Buffer Matching
        if risk_level == "HIGH":
            min_buffer = 25.0
        elif risk_level == "MEDIUM":
            min_buffer = 15.0
        else:
            min_buffer = 5.0

        evaluated_trains: List[tuple[Dict[str, Any], float]] = []
        for train in available_trains:
            raw_arrival = train.get("arrival_at_destination") or train.get("arrival_time")
            if not raw_arrival:
                continue
            arr_time = self._parse_time(raw_arrival)
            buf = self._calculate_buffer_minutes(target_arrival_time, arr_time)
            evaluated_trains.append((train, buf))

        # Eligible trains must meet min_buffer
        eligible = [t for t in evaluated_trains if t[1] >= min_buffer]

        if eligible:
            # Maximizes sleep: choose the train closest to target arrival (smallest buffer >= min_buffer)
            eligible.sort(key=lambda x: x[1])
            recommended_train = eligible[0][0]
            # Backup train is an earlier train if available, else next candidate
            backup_train = eligible[1][0] if len(eligible) > 1 else None
        elif evaluated_trains:
            # If none meet min_buffer, pick earliest arriving train (highest buffer)
            evaluated_trains.sort(key=lambda x: x[1], reverse=True)
            recommended_train = evaluated_trains[0][0]
            backup_train = evaluated_trains[1][0] if len(evaluated_trains) > 1 else None
        else:
            recommended_train = None
            backup_train = None

        return {
            "risk_level": risk_level,
            "recommended_train": recommended_train,
            "backup_train": backup_train,
            "urgency_reason": urgency_reason,
            "warning_subjects": warning_subjects,
        }
