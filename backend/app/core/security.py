import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import bcrypt
import jwt

from .config import settings
from .logger import get_logger

logger = get_logger(__name__)


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt with automatic salt generation.
    Enforces maximum 72 bytes boundary safely.
    """
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash in constant time.
    """
    try:
        pwd_bytes = plain_password.encode("utf-8")[:72]
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception as e:
        logger.warning(f"Password verification error: {e}")
        return False


def hash_token(token: str) -> str:
    """
    Hash an opaque token using SHA-256 before storing it in Redis.
    This prevents tokens from being exposed if the Redis store is ever inspected.
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_refresh_token() -> str:
    """Generate a cryptographically secure, high-entropy opaque refresh token."""
    return secrets.token_urlsafe(48)


def create_access_token(
    user_id: str,
    email: str,
    org_id: str,
    role: str,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a signed JWT access token with standardized claims.

    Claims include:
    - sub: User ID
    - email: User email
    - org_id: Tenant Organization ID
    - role: User Role
    - type: 'access'
    - jti: Unique JWT ID for tracking
    - iat: Issued At timestamp
    - exp: Expiration timestamp
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: Dict[str, Any] = {
        "sub": str(user_id),
        "email": email.lower().strip(),
        "org_id": str(org_id),
        "role": role,
        "type": "access",
        "jti": str(uuid.uuid4()),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    if extra_claims:
        payload.update(extra_claims)

    encoded_jwt = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and strictly validate a JWT access token.
    Fails if the token is expired, invalid, uses the wrong algorithm, or has wrong token type.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "require": ["sub", "org_id", "role", "exp", "type"],
            },
        )
        if payload.get("type") != "access":
            raise jwt.InvalidTokenError("Token type must be 'access'")
        return payload
    except jwt.ExpiredSignatureError as e:
        logger.debug(f"JWT expired: {e}")
        raise
    except jwt.PyJWTError as e:
        logger.debug(f"JWT decode error: {e}")
        raise
