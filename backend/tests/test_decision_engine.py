from datetime import datetime, time

from app.services.decision_engine import CommuteDecisionEngine


def test_high_risk_exam_day_selection():
    engine = CommuteDecisionEngine()
    today_str = datetime.now().date().isoformat()

    exam_records = [
        {
            "subject_name": "Distributed Systems",
            "exam_date": today_str,
            "time_slot": "09:00 - 12:00",
            "classroom": "Hall A",
        }
    ]
    attendance_records = [
        {"subject_name": "Distributed Systems", "percentage": 85.0},
        {"subject_name": "Algorithms", "percentage": 90.0},
    ]

    train_a = {
        "train_number": "97001",
        "train_type": "FAST",
        "departure_from_source": "08:00",
        "arrival_at_destination": "08:35",
    }
    train_b = {
        "train_number": "97003",
        "train_type": "SLOW",
        "departure_from_source": "08:20",
        "arrival_at_destination": "08:52",
    }
    available_trains = [train_a, train_b]
    target_arrival = time(9, 0)

    result = engine.evaluate_commute_urgency(
        attendance_records=attendance_records,
        exam_records=exam_records,
        available_trains=available_trains,
        target_arrival_time=target_arrival,
    )

    assert result["risk_level"] == "HIGH"
    assert result["recommended_train"]["train_number"] == "97001"


def test_attendance_deficit_escalation():
    engine = CommuteDecisionEngine()

    attendance_records = [
        {"subject_name": "Database Systems", "percentage": 68.0},
        {"subject_name": "Operating Systems", "percentage": 71.0},
    ]
    exam_records = []
    available_trains = [
        {
            "train_number": "96001",
            "train_type": "FAST",
            "departure_from_source": "08:10",
            "arrival_at_destination": "08:40",
        }
    ]
    target_arrival = time(9, 0)

    result = engine.evaluate_commute_urgency(
        attendance_records=attendance_records,
        exam_records=exam_records,
        available_trains=available_trains,
        target_arrival_time=target_arrival,
    )

    assert result["risk_level"] in ["MEDIUM", "HIGH"]
    assert "Database Systems" in result["warning_subjects"]
    assert "Operating Systems" in result["warning_subjects"]


def test_zero_risk_buffer_optimization():
    engine = CommuteDecisionEngine()

    attendance_records = [
        {"subject_name": "Maths", "percentage": 100.0},
        {"subject_name": "Physics", "percentage": 100.0},
    ]
    exam_records = []

    # Train 1: 08:30 (30 min buffer)
    # Train 2: 08:50 (10 min buffer) -> Maximizes sleep while >= 5 min buffer
    # Train 3: 08:57 (3 min buffer) -> Violates min 5 min safe buffer
    train_1 = {
        "train_number": "95001",
        "departure_from_source": "07:50",
        "arrival_at_destination": "08:30",
    }
    train_2 = {
        "train_number": "95003",
        "departure_from_source": "08:10",
        "arrival_at_destination": "08:50",
    }
    train_3 = {
        "train_number": "95005",
        "departure_from_source": "08:20",
        "arrival_at_destination": "08:57",
    }

    result = engine.evaluate_commute_urgency(
        attendance_records=attendance_records,
        exam_records=exam_records,
        available_trains=[train_1, train_2, train_3],
        target_arrival_time=time(9, 0),
    )

    assert result["risk_level"] == "LOW"
    assert result["recommended_train"]["train_number"] == "95003"
