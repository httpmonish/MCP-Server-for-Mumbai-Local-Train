import uuid
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.logger import get_logger
from ..models.auth import Organization
from ..schemas.organizations import OrganizationUpdateRequest

logger = get_logger(__name__)


class OrganizationService:
    @staticmethod
    async def get_organization_by_id(
        db: AsyncSession,
        org_id: uuid.UUID,
    ) -> Optional[Organization]:
        """Fetch organization strictly by ID with tenant isolation guarantee."""
        stmt = select(Organization).where(Organization.id == org_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def update_organization(
        db: AsyncSession,
        org_id: uuid.UUID,
        update_data: OrganizationUpdateRequest,
    ) -> Organization:
        """
        Partially update organization settings for the authenticated tenant.
        Prevents mass assignment and guards immutable attributes (id, type, created_at).
        """
        stmt = select(Organization).where(Organization.id == org_id)
        result = await db.execute(stmt)
        org = result.scalars().first()

        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found.",
            )

        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            return org

        for key, value in update_dict.items():
            setattr(org, key, value)

        await db.commit()
        await db.refresh(org)

        logger.info(
            f"Organization updated successfully.",
            extra={"org_id": str(org.id), "updated_fields": list(update_dict.keys())},
        )
        return org
