import math
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies.auth import get_current_user, get_db_session, require_org_admin
from ..models.auth import User, UserRole
from ..schemas.organizations import (
    BulkImportResponse,
    MemberCreateRequest,
    MemberResponse,
    OrganizationDetailResponse,
    OrganizationUpdateRequest,
    PaginatedMembersResponse,
)
from ..services.csv_import_service import CsvImportService
from ..services.member_service import MemberService
from ..services.organization_service import OrganizationService

router = APIRouter(prefix="/organizations", tags=["Organizations & Members"])


@router.get(
    "/me",
    response_model=OrganizationDetailResponse,
    summary="Get current organization",
    description="Retrieve the organization profile associated with the authenticated user's organization context.",
)
async def get_my_organization(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> OrganizationDetailResponse:
    org = await OrganizationService.get_organization_by_id(db=db, org_id=current_user.org_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )
    return OrganizationDetailResponse.model_validate(org)


@router.patch(
    "/me",
    response_model=OrganizationDetailResponse,
    summary="Update current organization",
    description="Partially update organization settings. Only ORG_ADMIN can modify organization details.",
)
async def update_my_organization(
    update_data: OrganizationUpdateRequest,
    current_admin: User = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db_session),
) -> OrganizationDetailResponse:
    org = await OrganizationService.update_organization(
        db=db,
        org_id=current_admin.org_id,
        update_data=update_data,
    )
    return OrganizationDetailResponse.model_validate(org)


@router.post(
    "/members",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add organization member",
    description="Add a new member to the organization. Only ORG_ADMIN is authorized.",
)
async def add_member(
    member_in: MemberCreateRequest,
    current_admin: User = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db_session),
) -> MemberResponse:
    new_member = await MemberService.create_member(
        db=db,
        org_id=current_admin.org_id,
        member_in=member_in,
    )
    return MemberResponse.model_validate(new_member)


@router.get(
    "/members",
    response_model=PaginatedMembersResponse,
    summary="List organization members",
    description="Retrieve paginated list of members belonging strictly to the authenticated user's organization.",
)
async def list_members(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    role: Optional[UserRole] = Query(None, description="Filter by member role"),
    search: Optional[str] = Query(None, description="Search by email or name"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_admin: User = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db_session),
) -> PaginatedMembersResponse:
    members, total = await MemberService.list_members(
        db=db,
        org_id=current_admin.org_id,
        page=page,
        limit=limit,
        role=role,
        search=search,
        is_active=is_active,
    )
    pages = math.ceil(total / limit) if total > 0 else 1
    items = [MemberResponse.model_validate(m) for m in members]

    return PaginatedMembersResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.delete(
    "/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove organization member",
    description="Remove a member from the organization. Guards against IDOR, self-deletion, and removing the last admin.",
)
async def remove_member(
    user_id: uuid.UUID,
    current_admin: User = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db_session),
) -> None:
    await MemberService.remove_member(
        db=db,
        org_id=current_admin.org_id,
        target_user_id=user_id,
        current_admin_id=current_admin.id,
    )


@router.post(
    "/members/bulk",
    response_model=BulkImportResponse,
    summary="Bulk import members from CSV",
    description="Upload a CSV file to bulk onboard members. Validates rows, sanitizes inputs, and returns an itemized audit error report.",
)
async def bulk_import_members(
    file: UploadFile = File(..., description="CSV file with email, role, and optional name headers"),
    current_admin: User = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db_session),
) -> BulkImportResponse:
    return await CsvImportService.process_csv_upload(
        db=db,
        org_id=current_admin.org_id,
        file=file,
    )
