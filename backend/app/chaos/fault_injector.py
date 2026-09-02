import asyncio
import random
import re
from typing import Optional

from ..core.config import settings
from ..core.logger import get_logger

logger = get_logger(__name__)


class ChaosInjector:
    def __init__(self, enabled: Optional[bool] = None):
        if enabled is not None:
            self.enabled = enabled
        else:
            self.enabled = getattr(settings, "CHAOS_MODE_ENABLED", False)

    async def inject_latency(self, min_ms: int = 1000, max_ms: int = 5000) -> float:
        """Inject artificial latency jitter if chaos mode is enabled."""
        if not self.enabled:
            return 0.0
        delay_sec = random.uniform(min_ms / 1000.0, max_ms / 1000.0)
        logger.warning(f"ChaosInjector: Injecting artificial latency of {delay_sec:.2f}s")
        await asyncio.sleep(delay_sec)
        return delay_sec

    async def inject_packet_drop(self, drop_rate: float = 0.3) -> None:
        """Randomly raise network failure exceptions if chaos mode is enabled."""
        if not self.enabled:
            return
        if random.random() < drop_rate:
            if random.random() < 0.5:
                logger.warning("ChaosInjector: Triggering simulated ConnectionResetError")
                raise ConnectionResetError("Chaos: Simulated network socket disconnect / packet drop")
            else:
                logger.warning("ChaosInjector: Triggering simulated TimeoutError")
                raise TimeoutError("Chaos: Simulated network packet drop timeout")

    async def inject_memory_spike(self, allocation_mb: int = 256, duration_sec: int = 3) -> None:
        """Temporarily allocate byte arrays to simulate memory pressure."""
        if not self.enabled:
            return
        logger.warning(f"ChaosInjector: Simulating {allocation_mb}MB memory spike for {duration_sec}s")
        buffer = bytearray(allocation_mb * 1024 * 1024)
        try:
            await asyncio.sleep(duration_sec)
        finally:
            del buffer

    async def inject_corrupted_payload(self, raw_html: str) -> str:
        """Strip random structural tags to simulate university portal DOM mutations."""
        if not self.enabled:
            return raw_html
        logger.warning("ChaosInjector: Injecting DOM mutation corruption into portal HTML")
        # Strip critical table and row tags to simulate breaking changes
        corrupted = re.sub(r"</?(td|tr|table|tbody)[^>]*>", "", raw_html, flags=re.IGNORECASE)
        return corrupted
