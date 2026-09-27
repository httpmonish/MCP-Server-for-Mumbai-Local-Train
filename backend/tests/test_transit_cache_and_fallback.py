from datetime import datetime, timedelta, timezone

import pytest
from app.models.transit import DataConfidence, DataFreshness, OperationalStatus, TransitDataSourceType
from app.normalization.transit_normalizer import TransitNormalizer
from app.services.transit_cache import TransitCacheManager
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_transit_normalizer_freshness_rules():
    now = datetime.now(timezone.utc)

    # 1. Fresh data (< 120s)
    fresh_time = now - timedelta(seconds=30)
    f_status, age = TransitNormalizer.calculate_freshness(fresh_time)
    assert f_status == DataFreshness.FRESH
    assert age == 30

    # 2. Stale data (120s - 600s)
    stale_time = now - timedelta(seconds=300)
    s_status, s_age = TransitNormalizer.calculate_freshness(stale_time)
    assert s_status == DataFreshness.STALE
    assert s_age == 300

    # 3. Expired data (> 600s)
    expired_time = now - timedelta(seconds=1200)
    e_status, e_age = TransitNormalizer.calculate_freshness(expired_time)
    assert e_status == DataFreshness.EXPIRED
    assert e_age == 1200


@pytest.mark.asyncio
async def test_transit_cache_manager_lifecycle(fake_redis_cache):
    cache_mgr = TransitCacheManager(fake_redis_cache)

    # Set live train in cache
    train_data = {
        "train_number": "97005",
        "line": "CR",
        "status": "RUNNING",
        "latitude": 19.186,
        "longitude": 72.975,
        "delay_minutes": 2,
    }
    await cache_mgr.set_live_train("97005", train_data, ttl=60)

    # Retrieve from cache
    cached = await cache_mgr.get_live_train("97005")
    assert cached is not None
    assert cached["train_number"] == "97005"
    assert cached["delay_minutes"] == 2


@pytest.mark.asyncio
async def test_static_fallback_labeling(client: AsyncClient):
    # Verify schedule endpoint always labels as STATIC_TIMETABLE
    res = await client.get("/api/v1/trains/schedule?from=Thane&to=CSMT")
    assert res.status_code == 200
    data = res.json()
    assert data["meta"]["data_label"] == "STATIC_TIMETABLE"
    assert data["meta"]["source"] == "STATIC_TIMETABLE"
