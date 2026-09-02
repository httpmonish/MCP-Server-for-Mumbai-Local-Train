import asyncio
import json
from typing import Dict, Optional, Set

import redis.asyncio as aioredis
from fastapi import WebSocket

from ..core.logger import get_logger

logger = get_logger(__name__)


class TransitConnectionManager:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.redis = aioredis.from_url(redis_url, decode_responses=True)
        self.listener_task: Optional[asyncio.Task] = None
        self._is_running = False

    async def connect(self, corridor: str, websocket: WebSocket) -> None:
        await websocket.accept()
        if corridor not in self.active_connections:
            self.active_connections[corridor] = set()
        self.active_connections[corridor].add(websocket)
        logger.info(f"WebSocket client connected to corridor: {corridor}")

    async def disconnect(self, corridor: str, websocket: WebSocket) -> None:
        if corridor in self.active_connections:
            self.active_connections[corridor].discard(websocket)
            if not self.active_connections[corridor]:
                del self.active_connections[corridor]
        logger.info(f"WebSocket client disconnected from corridor: {corridor}")

    async def broadcast_local(self, corridor: str, payload: dict) -> None:
        if corridor not in self.active_connections:
            return

        dead_sockets = set()
        message_text = json.dumps(payload)

        for ws in list(self.active_connections[corridor]):
            try:
                await ws.send_text(message_text)
            except Exception as exc:
                logger.debug(f"Failed to send to WebSocket, marking for removal: {exc}")
                dead_sockets.add(ws)

        for dead_ws in dead_sockets:
            await self.disconnect(corridor, dead_ws)

    async def publish_delay_event(self, corridor: str, delay_event: dict) -> None:
        # 1. Immediately notify local subscribers on this node
        await self.broadcast_local(corridor, delay_event)

        # 2. Publish to Redis Pub/Sub for horizontal distribution
        try:
            channel = f"transit:events:{corridor}"
            await self.redis.publish(channel, json.dumps(delay_event))
        except Exception as exc:
            logger.warning(f"Failed to publish delay event to Redis channel: {exc}")

    async def start_pubsub_listener(self) -> None:
        if self._is_running:
            return
        self._is_running = True
        self.listener_task = asyncio.create_task(self._listen_pubsub())

    async def _listen_pubsub(self) -> None:
        try:
            pubsub = self.redis.pubsub()
            await pubsub.psubscribe("transit:events:*")
            logger.info("Subscribed to Redis PubSub pattern transit:events:*")

            async for message in pubsub.listen():
                if message and message.get("type") == "pmessage":
                    channel = message.get("channel", "")
                    # Extract corridor from transit:events:{corridor}
                    corridor = channel.split(":")[-1]
                    raw_data = message.get("data", "{}")
                    try:
                        payload = json.loads(raw_data)
                        await self.broadcast_local(corridor, payload)
                    except json.JSONDecodeError:
                        continue
        except asyncio.CancelledError:
            logger.info("PubSub listener task cancelled.")
        except Exception as exc:
            logger.error(f"Error in Redis PubSub listener: {exc}")
        finally:
            self._is_running = False

    async def aclose(self) -> None:
        self._is_running = False
        if self.listener_task and not self.listener_task.done():
            self.listener_task.cancel()
        await self.redis.close()
