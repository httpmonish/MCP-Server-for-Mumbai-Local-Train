from typing import Any, Dict, List


def format_attendance_report(student_id: str, data: Dict[str, Any]) -> str:
    records = data.get("data", [])
    is_stale = data.get("stale", False)
    source = data.get("source", "live")
    timestamp = data.get("last_synced_at", "Unknown")

    output = []
    if is_stale:
        output.append(f"[WARNING: UPSTREAM PORTAL UNREACHABLE. DISPLAYING CACHED RECORDS FROM {timestamp}]")

    output.append(f"## Attendance Report for Student: {student_id}")
    output.append(f"Source: {source}")
    output.append("")
    output.append("| Subject | Conducted | Attended | Percentage | Status |")
    output.append("| :--- | :---: | :---: | :---: | :--- |")

    total_cond = 0
    total_att = 0

    for rec in records:
        subj = rec.get("subject_name", "Unknown")
        cond = rec.get("total_conducted", 0)
        att = rec.get("total_attended", 0)
        perc = rec.get("percentage", 0.0)

        status = "GOOD" if perc >= 75.0 else "CRITICAL WARNING (<75%)"
        output.append(f"| {subj} | {cond} | {att} | {perc}% | {status} |")

        total_cond += cond
        total_att += att

    overall_perc = (total_att / total_cond * 100) if total_cond > 0 else 0.0
    output.append("")
    output.append(f"**Aggregate Overall Attendance: {overall_perc:.2f}%**")

    return "\n".join(output)

def format_exam_schedule(student_id: str, data: Dict[str, Any]) -> str:
    exams = data.get("data", [])
    if not exams:
        return f"No upcoming exams found for student {student_id}."

    output = [f"## Upcoming Exam Schedule for Student: {student_id}", ""]

    # Sort exams by date (assuming date format allows string sort or handle properly)
    # For the spec, we'll just list them.
    for exam in exams:
        output.append(f"### {exam.get('subject_name', 'Unknown Subject')}")
        output.append(f"- Date: {exam.get('exam_date', 'TBD')}")
        output.append(f"- Time Slot: {exam.get('time_slot', 'TBD')}")
        output.append(f"- Location: {exam.get('classroom') or 'TBD'}")
        output.append("")

    return "\n".join(output)

def format_train_schedule(
    source: str, destination: str, trains: List[Dict[str, Any]], query_time: str | None = None
) -> str:
    if not trains:
        time_suffix = f" after {query_time}" if query_time else ""
        return f"No upcoming suburban trains found between {source} and {destination}{time_suffix}."

    output = [f"## Upcoming Trains: {source} $\\to$ {destination}", ""]
    if query_time:
        output.append(f"Queried at: {query_time}")
        output.append("")
    output.append(f"| Train No. | Line | Type | Departs {source} | Arrives {destination} | Travel Time |")
    output.append("| :--- | :---: | :---: | :---: | :---: | :---: |")

    for t in trains:
        output.append(
            f"| {t['train_number']} | {t['line']} | {t['train_type']} | {t['departure_from_source']} | {t['arrival_at_destination']} | {t['travel_time_minutes']} mins |"
        )

    return "\n".join(output)

