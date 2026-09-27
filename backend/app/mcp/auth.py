import uuid
from typing import Any, Dict, List, Optional
from uuid import UUID

import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.logger import get_logger
from ..models.auth import Organization, User
from .context import MCPUserContext
from .errors import MCPErrorCode, MCPToolException

logger = get_logger(__name__)

# Standardized MCP read-only scopes
SCOPE_SCHEDULE_READ = "transitpulse:schedule:read"
SCOPE_ATTENDANCE_READ = "transitpulse:attendance:read"
SCOPE_TRANSIT_READ = "transitpulse:transit:read"
SCOPE_INTELLIGENCE_READ = "transitpulse:intelligence:read"


def decode_and_validate_mcp_jwt(
    token: str,
    required_scope: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Decode and validate a JWT token specifically for MCP server access.
    Validates signature, expiration, token type, issuer, and audience.
    """
    if not token or not token.strip():
        raise MCPToolException(
            MCPErrorCode.MCP_UNAUTHORIZED,
            "Authentication token is required for MCP tool access.",
        )

    clean_token = token.strip()
    if clean_token.lower().startswith("bearer "):
        clean_token = clean_token[7:].strip()

    try:
        payload = jwt.decode(
            clean_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_aud": False,
                "require": ["sub", "org_id", "role", "exp", "type"],
            },
        )
    except jwt.ExpiredSignatureError:
        raise MCPToolException(
            MCPErrorCode.MCP_UNAUTHORIZED,
            "MCP authentication token has expired. Please refresh your credentials.",
        )
    except jwt.PyJWTError as e:
        logger.warning(f"MCP token validation error: {e}")
        raise MCPToolException(
            MCPErrorCode.MCP_UNAUTHORIZED,
            f"Invalid authentication token: {str(e)}",
        )

    # Validate token type
    if payload.get("type") != "access":
        raise MCPToolException(
            MCPErrorCode.MCP_UNAUTHORIZED,
            "Invalid token type. Only 'access' tokens are accepted.",
        )

    # Validate token issuer if present
    token_iss = payload.get("iss")
    if token_iss and token_iss not in (settings.MCP_AUTH_ISSUER, "transitpulse-auth"):
        raise MCPToolException(
            MCPErrorCode.MCP_UNAUTHORIZED,
            f"Untrusted token issuer: {token_iss}",
        )

    # Validate token audience if present
    token_aud = payload.get("aud")
    if token_aud:
        valid_audiences = [settings.MCP_AUTH_AUDIENCE, "transitpulse-mcp", "transitpulse-api"]
        if isinstance(token_aud, str) and token_aud not in valid_audiences:
            raise MCPToolException(
                MCPErrorCode.MCP_UNAUTHORIZED,
                f"Invalid token audience: {token_aud}",
            )
        elif isinstance(token_aud, list) and not any(aud in valid_audiences for aud in token_aud):
            raise MCPToolException(
                MCPErrorCode.MCP_UNAUTHORIZED,
                f"Invalid token audience: {token_aud}",
            )

    # Validate scope if specified
    if required_scope:
        token_scopes: List[str] = []
        raw_scopes = payload.get("scopes") or payload.get("scope")
        if isinstance(raw_scopes, list):
            token_scopes = raw_scopes
        elif isinstance(raw_scopes, str):
            token_scopes = raw_scopes.split()

        role = payload.get("role", "")
        # Superadmins, Admins, or tokens without explicit scope restriction grant read access
        if token_scopes and required_scope not in token_scopes and role not in ("SUPERADMIN", "ADMIN"):
            raise MCPToolException(
                MCPErrorCode.MCP_FORBIDDEN,
                f"Insufficient privileges. Required scope: {required_scope}",
                {"required_scope": required_scope, "granted_scopes": token_scopes},
            )

    return payload


async def resolve_mcp_user_context(
    token: str,
    db: Optional[AsyncSession] = None,
    required_scope: Optional[str] = None,
    request_id: Optional[str] = None,
    client_name: Optional[str] = None,
) -> MCPUserContext:
    """
    Resolve and verify full tenant context from the MCP token and database.
    Ensures active user and organization status.
    """
    payload = decode_and_validate_mcp_jwt(token, required_scope=required_scope)

    user_id_str = payload.get("sub")
    org_id_str = payload.get("org_id")
    role = payload.get("role", "STUDENT")
    email = payload.get("email", "")

    try:
        user_id = UUID(user_id_str)
        org_id = UUID(org_id_str)
    except Exception:
        raise MCPToolException(
            MCPErrorCode.MCP_UNAUTHORIZED,
            "Malformed user or organization identifier in token.",
        )

    # If DB session is available, verify active status in database
    if db:
        user_stmt = select(User).where(User.id == user_id, User.org_id == org_id)
        user_res = await db.execute(user_stmt)
        user = user_res.scalars().first()

        if not user:
            raise MCPToolException(
                MCPErrorCode.MCP_UNAUTHORIZED,
                "User account not found or does not belong to the token organization.",
            )
        if not user.is_active:
            raise MCPToolException(
                MCPErrorCode.MCP_FORBIDDEN,
                "User account is inactive or disabled.",
            )

        org_stmt = select(Organization).where(Organization.id == org_id)
        org_res = await db.execute(org_stmt)
        org = org_res.scalars().first()

        if not org or not org.is_active:
            raise MCPToolException(
                MCPErrorCode.MCP_FORBIDDEN,
                "Organization is inactive or suspended.",
            )

    raw_scopes = payload.get("scopes") or payload.get("scope") or []
    scopes = raw_scopes if isinstance(raw_scopes, list) else (raw_scopes.split() if isinstance(raw_scopes, str) else [])

    return MCPUserContext(
        user_id=user_id,
        org_id=org_id,
        role=role,
        email=email,
        scopes=scopes,
        request_id=request_id or str(uuid.uuid4()),
        client_name=client_name or "mcp_client",
    )
