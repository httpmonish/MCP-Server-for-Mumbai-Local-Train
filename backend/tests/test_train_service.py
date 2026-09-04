import asyncio
from datetime import datetime, time
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.app.cache import RedisCache
from backend.app.scrapers.timetable_parser import TrainTimetableParser
from backend.app.services import train_service
from backend.tests.fixtures.timetable_data import SAMPLE_PARSED_TRAINS


@pytest.mark.parametrize("raw, expected", [
    ("8.15", time(8, 15)),
    ("08:15", time(8, 15)),
    ("0815", time(8, 15)),
    ("-", None),
    ("--", None),
])
def test_time_normalizer(raw, expected):
    parser = TrainTimetableParser("mock.pdf", "CR")
    assert parser._parse_time(raw) == expected

@pytest.mark.asyncio
async def test_query_chronological_filtering():
    # Mock DB Session
    mock_db = AsyncMock()
    mock_cache = AsyncMock()
    mock_cache.get.return_value = None

    # Create mock model instances from SAMPLE_PARSED_TRAINS
    from backend.app.models.train import TrainSchedule
    mock_trains = []
    for t in SAMPLE_PARSED_TRAINS:
        train = MagicMock(spec=TrainSchedule)
        train.line = t["line"]
        train.train_number = t["train_number"]
        train.train_type = t["train_type"]
        train.stops_data = t["stops_data"]
        train.departure_time = t["departure_time"] # Simplified as string for mock, but service expects Time
        # In a real test we'd convert these to actual time objects
        mock_trains.append(train)

    # Patch the DB query result
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_trains
    mock_db.execute.return_value = mock_result

    # Query from "Byculla" to "Thane" at 08:10
    # Train 95701: Byculla 08:08 (Exclude)
    # Train 95703: Byculla 08:22 (Include)

    # We must handle the time objects properly in the mock
    # For the sake of the test, we'll override the filter logic inside the service
    # or ensure the mock objects return correctly.

    # Let's just call the service and check the filtered results
    # Note: we need to pass real time objects for the comparison in the service
    from datetime import datetime
    query_time = time(8, 10)

    # Overriding the mock to return specific objects that pass the service's checks
    for mt in mock_trains:
        # a. departure_time comparison (train.departure_time >= query_time)
        # In SAMPLE_PARSED_TRAINS, they are strings. We need Time objects.
        dep_t = datetime.strptime(mt.departure_time, "%H:%M:%S").time()
        mt.departure_time = dep_t

    result = await train_service.get_next_trains(mock_db, mock_cache, "Byculla", "Thane", query_time)

    assert result["data"][0]["train_number"] == "95703"
    assert len(result["data"]) == 1

@pytest.mark.asyncio
async def test_reverse_direction_rejection():
    mock_db = AsyncMock()
    mock_cache = AsyncMock()
    mock_cache.get.return_value = None

    from backend.app.models.train import TrainSchedule
    mock_trains = []
    for t in SAMPLE_PARSED_TRAINS:
        train = MagicMock(spec=TrainSchedule)
        train.line = t["line"]
        train.train_number = t["train_number"]
        train.train_type = t["train_type"]
        train.stops_data = t["stops_data"]
        train.departure_time = datetime.strptime(t["departure_time"], "%H:%M:%S").time()
        mock_trains.append(train)

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_trains
    mock_db.execute.return_value = mock_result

    # Query from "Thane" to "Byculla" (Wrong way)
    result = await train_service.get_next_trains(mock_db, mock_cache, "Thane", "Byculla", time(0, 0))

    assert len(result["data"]) == 0

@pytest.mark.asyncio
async def test_train_caching_hit():
    mock_db = AsyncMock()
    mock_cache = AsyncMock()

    # Mock cached data
    cached_data = [{"train_number": "95703", "line": "CR", "train_type": "FAST"}]
    mock_cache.get.return_value = cached_data

    result = await train_service.get_next_trains(mock_db, mock_cache, "Byculla", "Thane", time(8, 0))

    assert result["source"] == "cache"
    assert result["data"] == cached_data
    mock_db.execute.assert_not_called()


@pytest.mark.asyncio
async def test_kasara_mindicator_timetable_retrieval():
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    mock_cache = AsyncMock()
    mock_cache.get.return_value = None

    # Query from Kasara to CSMT in the morning (e.g. 06:00:00)
    query_time = time(6, 0)
    result = await train_service.get_next_trains(mock_db, mock_cache, "Kasara", "Mumbai CSMT", query_time, limit=5)

    assert result["line"] == "CR"
    assert len(result["data"]) > 0
    # First train after 06:00 is 95404 departing at 06:10:00
    first_train = result["data"][0]
    assert first_train["train_number"] in ["95404", "95406", "95408"]
    assert first_train["departure_from_source"] >= "06:00:00"


@pytest.mark.asyncio
async def test_kasara_stations_topology_extended():
    stations = train_service.get_stations_info("CR")
    station_names = [s["name"] for s in stations]
    assert "Kasara" in station_names
    assert "Titwala" in station_names
    assert "Asangaon" in station_names
    assert len(stations) == 37

