import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.config import settings
from ..core.logger import get_logger
from ..core.security import create_access_token, hash_password, verify_password
from ..models.auth import Organization, User, UserRole
from ..schemas.auth import (
    AuthResponse,
    OrganizationResponse,
    TokenResponse,
    UserRegisterRequest,
    UserResponse,
)
from .session_service import SessionService

logger = get_logger(__name__)


class DuplicateEmailError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InactiveUserError(Exception):
    pass


class AuthService:
    """
    Handles authentication business logic, atomic registration transactions,
    login validation, token generation, and tenant binding.
    """

    def __init__(self, session_service: SessionService):
        self.session_service = session_service

    async def register_organization_and_admin(self, db: AsyncSession, req: UserRegisterRequest) -> AuthResponse:
        """
        Atomically register an organization and its founding ORG_ADMIN user.
        Ensures email uniqueness across the system and rolls back on error.
        """
        email_clean = req.email.lower().strip()

        # Check for duplicate user email
        stmt = select(User).where(User.email == email_clean)
        result = await db.execute(stmt)
        existing_user = result.scalars().first()
        if existing_user:
            logger.warning(f"Registration failed: duplicate email {email_clean}")
            raise DuplicateEmailError("A user with this email address is already registered.")

        # Create Organization
        org = Organization(
            id=uuid.uuid4(),
            name=req.org_name.strip(),
            type=req.org_type,
            domain=req.org_domain.strip().lower() if req.org_domain else None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(org)
        await db.flush()  # Populate org.id for foreign key

        # Hash password and create first User as ORG_ADMIN
        hashed_pwd = hash_password(req.password)
        user = User(
            id=uuid.uuid4(),
            org_id=org.id,
            email=email_clean,
            password_hash=hashed_pwd,
            role=UserRole.ORG_ADMIN,
            is_active=True,
            is_verified=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        await db.refresh(org)

        logger.info(
            f"Successfully registered organization '{org.name}' ({org.id}) and admin user '{user.email}' ({user.id})"
        )

        # Generate Access JWT and Redis Refresh Token
        access_token = create_access_token(
            user_id=str(user.id),
            email=user.email,
            org_id=str(user.org_id),
            role=user.role.value,
        )
        refresh_token = await self.session_service.create_session(
            user_id=str(user.id),
            org_id=str(user.org_id),
            role=user.role.value,
            email=user.email,
        )

        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

        return AuthResponse(
            user=UserResponse.model_validate(user),
            organization=OrganizationResponse.model_validate(org),
            tokens=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=expires_in,
            ),
        )

    async def authenticate_user(self, db: AsyncSession, email: str, password: str) -> AuthResponse:
        """
        Authenticate a user by email and password, update last_login_at,
        and issue access and refresh tokens.
        """
        email_clean = email.lower().strip()

        stmt = select(User).options(selectinload(User.organization)).where(User.email == email_clean)
        result = await db.execute(stmt)
        user = result.scalars().first()

        # Generic failure message to prevent email enumeration
        if not user or not verify_password(password, user.password_hash):
            logger.warning(f"Login failed for email '{email_clean}'")
            raise InvalidCredentialsError("Invalid email or password.")

        if not user.is_active:
            logger.warning(f"Login rejected: account for user '{user.id}' is inactive")
            raise InactiveUserError("Your account has been deactivated. Please contact support.")

        # Update last login timestamp
        user.last_login_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(user)

        # Generate tokens
        access_token = create_access_token(
            user_id=str(user.id),
            email=user.email,
            org_id=str(user.org_id),
            role=user.role.value,
        )
        refresh_token = await self.session_service.create_session(
            user_id=str(user.id),
            org_id=str(user.org_id),
            role=user.role.value,
            email=user.email,
        )

        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

        return AuthResponse(
            user=UserResponse.model_validate(user),
            organization=OrganizationResponse.model_validate(user.organization),
            tokens=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=expires_in,
            ),
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """
        Rotate refresh token and issue a fresh access token.
        """
        rotated = await self.session_service.rotate_refresh_token(refresh_token)
        if not rotated:
            raise InvalidCredentialsError("Invalid, expired, or revoked refresh token.")

        user_id, org_id, role, email, new_refresh_token = rotated

        access_token = create_access_token(
            user_id=user_id,
            email=email,
            org_id=org_id,
            role=role,
        )
        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=expires_in,
        )

    async def logout(self, refresh_token: Optional[str]) -> bool:
        """
        Revoke the refresh token session from Redis.
        """
        if refresh_token:
            return await self.session_service.revoke_session(refresh_token)
        return True
