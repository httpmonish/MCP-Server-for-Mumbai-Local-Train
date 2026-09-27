import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from ..models.auth import OrgType, UserRole


class OrganizationRegisterInput(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Organization name")
    type: OrgType = Field(default=OrgType.OTHER, description="Type of organization")
    domain: Optional[str] = Field(None, max_length=255, description="Associated domain e.g. college.edu")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Organization name cannot be blank")
        return cleaned


class UserRegisterRequest(BaseModel):
    org_name: str = Field(..., min_length=2, max_length=255, description="Name of the organization")
    org_type: OrgType = Field(default=OrgType.OTHER, description="Type of organization")
    org_domain: Optional[str] = Field(None, max_length=255, description="Optional organization domain")
    email: EmailStr = Field(..., description="Admin email address")
    password: str = Field(..., min_length=8, max_length=128, description="Password (min 8 chars)")

    @field_validator("org_name")
    @classmethod
    def validate_org_name(cls, v: str) -> str:
        cleaned = v.strip()
        if len(cleaned) < 2:
            raise ValueError("Organization name must be at least 2 characters long")
        return cleaned

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if len(v) > 128:
            raise ValueError("Password must not exceed 128 characters")
        if v.strip() != v:
            raise ValueError("Password cannot start or end with whitespace")
        return v


class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, max_length=128, description="Password")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class TokenRefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=10, description="Opaque refresh token")


class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = Field(None, description="Refresh token to invalidate immediately")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="Short-lived JWT access token")
    refresh_token: str = Field(..., description="Long-lived rotated opaque refresh token")
    token_type: str = Field(default="bearer", description="Token authorization type")
    expires_in: int = Field(..., description="Access token expiration in seconds")


class OrganizationResponse(BaseModel):
    id: uuid.UUID
    name: str
    type: OrgType
    domain: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    email: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AuthResponse(BaseModel):
    user: UserResponse
    organization: OrganizationResponse
    tokens: TokenResponse


class UserMeResponse(BaseModel):
    user: UserResponse
    organization: OrganizationResponse
