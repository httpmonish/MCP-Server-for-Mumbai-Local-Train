from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.rate_limiter import limiter
from ..dependencies.auth import (
    get_auth_service,
    get_current_user,
    get_db_session,
    require_org_admin,
)
from ..models.auth import User
from ..schemas.auth import (
    AuthResponse,
    LogoutRequest,
    OrganizationResponse,
    TokenRefreshRequest,
    TokenResponse,
    UserLoginRequest,
    UserMeResponse,
    UserRegisterRequest,
    UserResponse,
)
from ..services.auth_service import (
    AuthService,
    DuplicateEmailError,
    InactiveUserError,
    InvalidCredentialsError,
)

router = APIRouter(prefix="/auth", tags=["Identity & Authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new organization and founding ORG_ADMIN",
)
async def register(
    req: UserRegisterRequest,
    db: AsyncSession = Depends(get_db_session),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Atomically creates a new Organization and its initial ORG_ADMIN user.
    Returns the newly created user, organization, and authentication tokens.
    """
    try:
        return await auth_service.register_organization_and_admin(db=db, req=req)
    except DuplicateEmailError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and issue token pair",
)
@limiter.limit(settings.RATE_LIMIT_LOGIN)
async def login(
    request: Request,
    req: UserLoginRequest,
    db: AsyncSession = Depends(get_db_session),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Authenticates a user via email and password with rate limiting (5 attempts/min).
    Issues a short-lived 15-minute JWT access token and a long-lived 7-day Redis refresh session.
    """
    try:
        return await auth_service.authenticate_user(db=db, email=req.email, password=req.password)
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InactiveUserError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Rotate refresh token and issue new access token",
)
async def refresh_token(
    req: TokenRefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Validates an existing refresh token, invalidates it immediately to prevent replay,
    and returns a newly rotated refresh token and a fresh access token.
    """
    try:
        return await auth_service.refresh_tokens(refresh_token=req.refresh_token)
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Revoke refresh token and terminate session",
)
async def logout(
    req: LogoutRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Revokes the refresh token from Redis. Any subsequent refresh attempts with this token will fail.
    """
    await auth_service.logout(refresh_token=req.refresh_token)
    return {"detail": "Successfully logged out. Refresh session revoked."}


@router.get(
    "/me",
    response_model=UserMeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user identity and tenant context",
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """
    Protected endpoint verifying access token validity.
    Returns authenticated user profile and associated organization.
    """
    return UserMeResponse(
        user=UserResponse.model_validate(current_user),
        organization=OrganizationResponse.model_validate(current_user.organization),
    )


@router.get(
    "/admin/verify",
    status_code=status.HTTP_200_OK,
    summary="Protected endpoint requiring ORG_ADMIN or PLATFORM_ADMIN role",
)
async def verify_org_admin(
    current_user: User = Depends(require_org_admin),
):
    """
    Protected RBAC demonstration endpoint.
    Only accessible by users with ORG_ADMIN or PLATFORM_ADMIN role.
    """
    return {
        "status": "authorized",
        "message": f"Welcome Admin {current_user.email}",
        "org_id": str(current_user.org_id),
        "role": current_user.role.value,
    }
