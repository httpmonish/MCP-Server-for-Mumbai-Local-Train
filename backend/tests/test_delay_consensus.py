from datetime import datetime, timedelta, timezone

from app.models.transit_delay import TrainDelayReport
from app.services.delay_consensus import DelayConsensusEngine


def test_single_report_unverified():
    engine = DelayConsensusEngine()
    now = datetime.now(timezone.utc)

    report = TrainDelayReport(
        train_number="97001",
        station_code="TNA",
        reported_delay_minutes=15,
        reporter_id_hash="hash1",
        created_at=now,
    )

    result = engine.calculate_weighted_delay([report])

    assert result["verified"] is False
    assert result["delay_minutes"] == 15
    assert result["report_count"] == 1


def test_multiple_reports_reach_consensus():
    engine = DelayConsensusEngine()
    now = datetime.now(timezone.utc)

    # 3 reports submitted within 2 minutes of each other: 10m, 12m, 10m
    report1 = TrainDelayReport(
        train_number="97002",
        station_code="BY",
        reported_delay_minutes=10,
        reporter_id_hash="hash1",
        created_at=now,
    )
    report2 = TrainDelayReport(
        train_number="97002",
        station_code="BY",
        reported_delay_minutes=12,
        reporter_id_hash="hash2",
        created_at=now - timedelta(minutes=1),
    )
    report3 = TrainDelayReport(
        train_number="97002",
        station_code="BY",
        reported_delay_minutes=10,
        reporter_id_hash="hash3",
        created_at=now - timedelta(minutes=2),
    )

    result = engine.calculate_weighted_delay([report1, report2, report3])

    assert result["verified"] is True
    assert result["delay_minutes"] == 11
    assert result["report_count"] == 3


def test_stale_reports_decayed_out():
    engine = DelayConsensusEngine()
    now = datetime.now(timezone.utc)

    # 3 reports submitted 40 minutes ago
    reports = [
        TrainDelayReport(
            train_number="97003",
            station_code="CLA",
            reported_delay_minutes=20,
            reporter_id_hash=f"hash_{i}",
            created_at=now - timedelta(minutes=40),
        )
        for i in range(3)
    ]

    result = engine.calculate_weighted_delay(reports)

    # Weight of 3 reports at 40 min = 3 * 0.5^(40/15) = ~0.47, well below 2.5 threshold
    assert result["verified"] is False
    assert result["confidence"] < 2.5
