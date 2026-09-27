import secrets
import uuid
from typing import List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.logger import get_logger
from ..core.security import hash_password
from ..models.auth import User, UserRole
from ..schemas.organizations import MemberCreateRequest

logger = get_logger(__name__)


class MemberService:
    @staticmethod
    async def create_member(
        db: AsyncSession,
        org_id: uuid.UUID,
        member_in: MemberCreateRequest,
    ) -> User:
        """
        Create a new member within the specified organization tenant.
        Enforces unique email across the platform and role restrictions.
        """
        # 1. Duplicate check across the database
        stmt_check = select(User).where(User.email == member_in.email)
        res_check = await db.execute(stmt_check)
        existing = res_check.scalars().first()
        if existing:
            if existing.org_id == org_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A member with this email already exists in your organization.",
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A user with this email address is already registered.",
                )

        # 2. Prevent privilege escalation
        if member_in.role == UserRole.PLATFORM_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigning PLATFORM_ADMIN role is forbidden.",
            )

        # 3. Password handling
        raw_password = member_in.password or secrets.token_urlsafe(16)
        password_hash = hash_password(raw_password)

        new_member = User(
            id=uuid.uuid4(),
            org_id=org_id,
            email=member_in.email,
            full_name=member_in.full_name,
            password_hash=password_hash,
            role=member_in.role,
            is_active=member_in.is_active,
            is_verified=False,
        )

        db.add(new_member)
        await db.commit()
        await db.refresh(new_member)

        logger.info(
            "Member created successfully.",
            extra={
                "org_id": str(org_id),
                "member_id": str(new_member.id),
                "role": str(new_member.role.value),
            },
        )
        return new_member

    @staticmethod
    async def list_members(
        db: AsyncSession,
        org_id: uuid.UUID,
        page: int = 1,
        limit: int = 50,
        role: Optional[UserRole] = None,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[User], int]:
        """
        Query members strictly bounded by organization tenant.
        Supports pagination, filtering by role/status, and search.
        """
        base_filters = [User.org_id == org_id]

        if role is not None:
            base_filters.append(User.role == role)

        if is_active is not None:
            base_filters.append(User.is_active == is_active)

        if search:
            search_pattern = f"%{search.strip()}%"
            base_filters.append(
                or_(
                    User.email.ilike(search_pattern),
                    User.full_name.ilike(search_pattern),
                )
            )

        # Count total matching
        count_stmt = select(func.count(User.id)).where(*base_filters)
        total_res = await db.execute(count_stmt)
        total = total_res.scalar() or 0

        # Query paginated rows
        offset = (page - 1) * limit
        query_stmt = (
            select(User)
            .where(*base_filters)
            .order_by(User.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        members_res = await db.execute(query_stmt)
        members = list(members_res.scalars().all())

        return members, total

    @staticmethod
    async def remove_member(
        db: AsyncSession,
        org_id: uuid.UUID,
        target_user_id: uuid.UUID,
        current_admin_id: uuid.UUID,
    ) -> None:
        """
        Remove a member from the organization.
        Guards:
        - Prevents IDOR by querying strictly by (target_user_id, org_id).
        - Prevents admin self-deletion.
        - Prevents removing the last active ORG_ADMIN.
        """
        # 1. Look up target user inside THIS organization
        stmt = select(User).where(User.id == target_user_id, User.org_id == org_id)
        result = await db.execute(stmt)
        target_user = result.scalars().first()

        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found in your organization.",
            )

        # 2. Self-deletion guard
        if target_user.id == current_admin_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization administrators cannot delete their own account. Transfer ownership first.",
            )

        # 3. Last admin guard
        if target_user.role == UserRole.ORG_ADMIN:
            count_stmt = (
                select(func.count(User.id))
                .where(
                    User.org_id == org_id,
                    User.role == UserRole.ORG_ADMIN,
                    User.id != target_user.id,
                    User.is_active.is_(True),
                )
            )
            count_res = await db.execute(count_stmt)
            active_admins = count_res.scalar() or 0
            if active_admins == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot remove the last active administrator of the organization.",
                )

        await db.delete(target_user)
        await db.commit()

        logger.info(
            "Member removed successfully.",
            extra={
                "org_id": str(org_id),
                "target_user_id": str(target_user_id),
                "admin_id": str(current_admin_id),
            },
        )
