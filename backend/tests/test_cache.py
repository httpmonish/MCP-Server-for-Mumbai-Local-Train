import asyncio
import json
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio
from fakeredis.aioredis import FakeRedis

from backend.app.cache import RedisCache


@pytest_asyncio.fixture
async def cache():
    # Use fakeredis for testing
    cache_instance = RedisCache("redis://localhost")
    # Override the client with FakeRedis
    cache_instance.client = FakeRedis(decode_responses=True)
    yield cache_instance
    await cache_instance.close()

@pytest.mark.asyncio
async def test_cache_lifecycle(cache):
    key = "test_key"
    value = {"foo": "bar"}
    ttl = 10

    # Set and Get
    assert await cache.set(key, value, ttl) is True
    result = await cache.get(key)
    assert result == value

    # Delete
    assert await cache.delete(key) is True
    assert await cache.get(key) is None

@pytest.mark.asyncio
async def test_cache_expiration(cache):
    key = "expire_key"
    value = {"foo": "bar"}
    ttl = 1

    await cache.set(key, value, ttl)
    assert await cache.get(key) == value

    # Sleep until expired
    await asyncio.sleep(1.1)
    assert await cache.get(key) is None

@pytest.mark.asyncio
async def test_redis_unreachable_fail_open():
    # Mock redis.from_url to return a client that raises ConnectionError
    with patch("redis.asyncio.from_url") as mock_from_url:
        mock_client = MagicMock()
        mock_client.get.side_effect = Exception("Connection Error")
        mock_client.set.side_effect = Exception("Connection Error")
        mock_from_url.return_value = mock_client

        cache = RedisCache("redis://broken")

        # Assert get returns None without crashing
        assert await cache.get("any_key") is None

        # Assert set returns False without crashing
        assert await cache.set("any_key", {"data": 1}, 10) is False
