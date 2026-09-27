import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from ..cache import RedisCache
from ..core.config import settings
from ..core.logger import get_logger
from ..core.security import generate_refresh_token, hash_token

logger = get_logger(__name__)


class SessionService:
    """
    Manages stateful refresh token sessions in Redis with SHA-256 token hashing,
    automatic token rotation, replay detection, and revocation.
    """

    def __init__(self, cache: RedisCache):
        self.cache = cache
        self.ttl_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400

    def _session_key(self, token_hash: str) -> str:
        return f"auth:session:{token_hash}"

    def _user_sessions_key(self, user_id: str) -> str:
        return f"auth:user_sessions:{user_id}"

    def _revoked_token_key(self, token_hash: str) -> str:
        return f"auth:revoked:{token_hash}"

    async def create_session(
        self,
        user_id: str,
        org_id: str,
        role: str,
        email: str,
        device_info: Optional[str] = None,
    ) -> str:
        """
        Generate a new refresh token, store its hash and session metadata in Redis.
        Returns the plaintext refresh token.
        """
        raw_refresh_token = generate_refresh_token()
        token_hash = hash_token(raw_refresh_token)
        session_id = str(uuid.uuid4())

        session_data: Dict[str, Any] = {
            "session_id": session_id,
            "user_id": str(user_id),
            "org_id": str(org_id),
            "role": role,
            "email": email,
            "device_info": device_info or "unknown",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        # Store session in Redis
        key = self._session_key(token_hash)
        await self.cache.set(key, session_data, ttl=self.ttl_seconds)

        logger.info(f"Created refresh session {session_id} for user {user_id}")
        return raw_refresh_token

    async def rotate_refresh_token(self, old_refresh_token: str) -> Optional[Tuple[str, str, str, str, str]]:
        """
        Validate the old refresh token, invalidate it, issue a new rotated refresh token.

        Returns:
            Tuple of (user_id, org_id, role, email, new_refresh_token) if successful,
            or None if the token is invalid/revoked.
        """
        old_token_hash = hash_token(old_refresh_token)
        old_key = self._session_key(old_token_hash)

        session_data = await self.cache.get(old_key)
        if not session_data:
            # Check if this token was recently revoked (possible replay attack)
            is_revoked = await self.cache.get(self._revoked_token_key(old_token_hash))
            if is_revoked:
                logger.warning(f"SECURITY ALERT: Replay detected for previously rotated token hash {old_token_hash}!")
            else:
                logger.debug(f"Refresh session not found or expired for token hash {old_token_hash}")
            return None

        # Extract user context
        user_id = session_data.get("user_id")
        org_id = session_data.get("org_id")
        role = session_data.get("role")
        email = session_data.get("email")

        # Invalidate old token immediately and mark in revocation registry for 24h to catch replays
        await self.cache.delete(old_key)
        await self.cache.set(
            self._revoked_token_key(old_token_hash), {"revoked_at": datetime.now(timezone.utc).isoformat()}, ttl=86400
        )

        # Issue new rotated refresh token
        new_raw_refresh_token = generate_refresh_token()
        new_token_hash = hash_token(new_raw_refresh_token)
        new_session_id = session_data.get("session_id", str(uuid.uuid4()))

        new_session_data: Dict[str, Any] = {
            "session_id": new_session_id,
            "user_id": user_id,
            "org_id": org_id,
            "role": role,
            "email": email,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        new_key = self._session_key(new_token_hash)
        await self.cache.set(new_key, new_session_data, ttl=self.ttl_seconds)

        logger.info(f"Rotated refresh session {new_session_id} for user {user_id}")
        return user_id, org_id, role, email, new_raw_refresh_token

    async def revoke_session(self, refresh_token: str) -> bool:
        """Revoke a refresh session on logout."""
        token_hash = hash_token(refresh_token)
        key = self._session_key(token_hash)
        deleted = await self.cache.delete(key)
        # Store in revoked marker
        await self.cache.set(
            self._revoked_token_key(token_hash), {"revoked_at": datetime.now(timezone.utc).isoformat()}, ttl=86400
        )
        logger.info(f"Revoked refresh session for token hash {token_hash}")
        return deleted
