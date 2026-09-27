import uuid
from typing import Any, Callable, Dict, Optional

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..cache import RedisCache
from ..core.security import decode_access_token
from ..models.auth import User, UserRole
from ..services.auth_service import AuthService
from ..services.session_service import SessionService

# HTTP Bearer scheme
http_bearer = HTTPBearer(auto_error=False)


async def get_db_session(request: Request):
    """Dependency yielding an AsyncSession from the application session factory."""
    async_session_factory = request.app.state.async_session_factory
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def get_cache(request: Request) -> RedisCache:
    """Dependency returning the global Redis cache instance."""
    return request.app.state.cache


async def get_session_service(cache: RedisCache = Depends(get_cache)) -> SessionService:
    return SessionService(cache=cache)


async def get_auth_service(
    session_service: SessionService = Depends(get_session_service),
) -> AuthService:
    return AuthService(session_service=session_service)


async def get_current_token_payload(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
) -> Dict[str, Any]:
    """
    Extract and validate the JWT Bearer token from the Authorization header.
    Returns decoded JWT claims payload.
    """
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Missing or malformed Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(credentials.credentials)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has expired. Please refresh your session.",
            headers={"WWW-Authenticate": 'Bearer error="invalid_token", error_description="The access token expired"'},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or malformed access token.",
            headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
        )


async def get_current_user(
    token_payload: Dict[str, Any] = Depends(get_current_token_payload),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """
    Look up the active user associated with the verified access token claims.
    Preloads the organization to ensure tenant isolation.
    """
    user_id_str = token_payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing subject identifier.",
        )

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid subject UUID in token payload.",
        )

    stmt = select(User).options(selectinload(User.organization)).where(User.id == user_uuid)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with this token no longer exists.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account has been deactivated.",
        )

    return user


def require_role(*allowed_roles: UserRole) -> Callable:
    """
    Role-based Access Control (RBAC) dependency factory.
    Verifies that the authenticated user possesses one of the allowed roles.
    """

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles and current_user.role != UserRole.PLATFORM_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires one of roles: {[r.value for r in allowed_roles]}",
            )
        return current_user

    return role_checker


# Convenient role dependencies
require_org_admin = require_role(UserRole.ORG_ADMIN)
require_teacher_or_admin = require_role(UserRole.ORG_ADMIN, UserRole.TEACHER)
require_hr_or_admin = require_role(UserRole.ORG_ADMIN, UserRole.HR_ADMIN)
