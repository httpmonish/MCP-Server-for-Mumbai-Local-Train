import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_lines(client: AsyncClient):
    res = await client.get("/api/v1/trains/lines")
    assert res.status_code == 200
    lines = res.json()["lines"]
    assert len(lines) >= 3
    line_codes = [l["code"] for l in lines]
    assert "CR" in line_codes
    assert "WR" in line_codes
    assert "HR" in line_codes


@pytest.mark.asyncio
async def test_get_stations_all_and_filtering(client: AsyncClient):
    # 1. All stations
    res = await client.get("/api/v1/trains/stations")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] >= 50
    station_names = [s["name"] for s in data["stations"]]
    assert "Thane" in station_names or "Mumbai CSMT" in station_names

    # 2. Central Line stations
    res_cr = await client.get("/api/v1/trains/stations?line=CR")
    assert res_cr.status_code == 200
    cr_data = res_cr.json()
    assert cr_data["line"] == "CR"
    assert cr_data["count"] >= 30

    # 3. Western Line stations
    res_wr = await client.get("/api/v1/trains/stations?line=WR")
    assert res_wr.status_code == 200
    assert res_wr.json()["line"] == "WR"
    assert any(s["code"] == "CCG" for s in res_wr.json()["stations"])

    # 4. Search station by name
    res_search = await client.get("/api/v1/trains/stations?search=Dadar")
    assert res_search.status_code == 200
    assert any("Dadar" in s["name"] for s in res_search.json()["stations"])


@pytest.mark.asyncio
async def test_get_schedule_and_direction_validation(client: AsyncClient):
    # 1. Valid journey Thane -> CSMT
    res = await client.get("/api/v1/trains/schedule?from=Thane&to=CSMT&line=CR")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] > 0
    assert data["meta"]["data_label"] == "STATIC_TIMETABLE"
    for item in data["schedules"]:
        assert item["line"] == "CR"
        assert item["duration_mins"] > 0

    # 2. Same station rejection
    res_err = await client.get("/api/v1/trains/schedule?from=Thane&to=Thane")
    assert res_err.status_code == 400
    assert "different" in res_err.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_next_trains_static_fallback(client: AsyncClient):
    # Query next trains at specific morning rush hour
    res = await client.get("/api/v1/trains/next?from=Thane&to=CSMT&time=08:15&limit=4")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] > 0
    trains = data["trains"]
    assert len(trains) <= 4

    # Verify chronological sequence
    for i in range(len(trains) - 1):
        assert trains[i]["departure_from_source"] <= trains[i + 1]["departure_from_source"]

    # Verify data label transparency
    assert data["meta"]["data_label"] in ("STATIC_TIMETABLE", "SIMULATED_TEST", "REALTIME")
