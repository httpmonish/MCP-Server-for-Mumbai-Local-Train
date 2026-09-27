import enum
import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from ..models.auth import OrgType, UserRole


class OrganizationUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255, description="Updated organization name")
    domain: Optional[str] = Field(None, max_length=255, description="Updated organization domain")
    is_active: Optional[bool] = Field(None, description="Organization active status")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip()
            if len(cleaned) < 2:
                raise ValueError("Organization name must be at least 2 characters long")
            return cleaned
        return v

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip().lower()
            return cleaned if cleaned else None
        return v


class OrganizationDetailResponse(BaseModel):
    id: uuid.UUID
    name: str
    type: OrgType
    domain: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MemberCreateRequest(BaseModel):
    email: EmailStr = Field(..., description="Member's unique email address")
    role: UserRole = Field(default=UserRole.EMPLOYEE, description="Assigned organization role")
    full_name: Optional[str] = Field(None, max_length=255, description="Member full name")
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=128,
        description="Optional initial password (if omitted, a secure temporary password is auto-generated)",
    )
    is_active: bool = Field(default=True, description="Account active status")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("full_name")
    @classmethod
    def sanitize_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip()
            return cleaned if cleaned else None
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: UserRole) -> UserRole:
        if v == UserRole.PLATFORM_ADMIN:
            raise ValueError("Organization administrators cannot assign PLATFORM_ADMIN role.")
        return v


class MemberResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    email: str
    full_name: Optional[str] = None
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedMembersResponse(BaseModel):
    items: List[MemberResponse]
    total: int
    page: int
    limit: int
    pages: int


class BulkImportErrorItem(BaseModel):
    row: int
    email: Optional[str] = None
    error: str


class BulkImportResponse(BaseModel):
    total_rows: int
    valid_rows: int
    invalid_rows: int
    created_count: int
    errors: List[BulkImportErrorItem] = []
    created_members: List[MemberResponse] = []
