import json
from typing import Any, Optional

import redis.asyncio as redis

from .core.logger import get_logger

logger = get_logger(__name__)

class RedisCache:
    def __init__(self, redis_url: str):
        self.client = redis.from_url(redis_url, decode_responses=True)

    async def get(self, key: str) -> Optional[dict]:
        try:
            data = await self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.warning(f"Redis get error for key {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int) -> bool:
        try:
            await self.client.set(key, json.dumps(value), ex=ttl)
            return True
        except Exception as e:
            logger.warning(f"Redis set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Redis delete error for key {key}: {e}")
            return False

    async def ping(self) -> bool:
        try:
            return await self.client.ping()
        except Exception as e:
            logger.warning(f"Redis ping error: {e}")
            return False

    async def close(self):
        try:
            await self.client.close()
        except Exception as e:
            logger.warning(f"Redis close error: {e}")
