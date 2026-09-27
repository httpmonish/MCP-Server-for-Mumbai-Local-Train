import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base


class OrgType(str, enum.Enum):
    COLLEGE = "COLLEGE"
    COMPANY = "COMPANY"
    HOTEL = "HOTEL"
    OTHER = "OTHER"


class UserRole(str, enum.Enum):
    PLATFORM_ADMIN = "PLATFORM_ADMIN"
    ORG_ADMIN = "ORG_ADMIN"
    TEACHER = "TEACHER"
    HR_ADMIN = "HR_ADMIN"
    STUDENT = "STUDENT"
    EMPLOYEE = "EMPLOYEE"


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    name = Column(String(255), nullable=False)
    type = Column(
        Enum(OrgType, native_enum=False, length=50),
        nullable=False,
        default=OrgType.OTHER,
    )
    domain = Column(String(255), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name='{self.name}', type='{self.type}', is_active={self.is_active})>"


class User(Base):
    __tablename__ = "users"

    id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    org_id = Column(
        Uuid(as_uuid=True).with_variant(UUID(as_uuid=True), "postgresql"),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email = Column(String(255), nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(
        Enum(UserRole, native_enum=False, length=50),
        nullable=False,
        default=UserRole.EMPLOYEE,
    )
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="users")

    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        Index("ix_users_org_role", "org_id", "role"),
        Index("ix_users_org_active", "org_id", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', full_name='{self.full_name}', role='{self.role}', org_id={self.org_id})>"
