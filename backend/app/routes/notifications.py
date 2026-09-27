from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies.auth import get_current_user, get_db_session
from ..models.auth import User
from ..notifications.service import NotificationEngineService
from ..schemas.notification import (
    NotificationListResponse,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
)

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications & Alerts"])


@router.get(
    "/me",
    response_model=NotificationListResponse,
    summary="Get Current User Notification Inbox",
    description="Retrieve paginated notification history for the authenticated user, strictly tenant-scoped.",
)
async def get_my_notifications(
    limit: int = Query(20, ge=1, le=100, description="Page size limit"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    return await NotificationEngineService.get_user_notifications(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/preferences",
    response_model=List[NotificationPreferenceResponse],
    summary="Get User Notification Preferences",
    description="List all notification channel preferences and quiet-hours configuration for the authenticated user.",
)
async def get_my_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    return await NotificationEngineService.get_user_preferences(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
    )


@router.patch(
    "/preferences",
    response_model=NotificationPreferenceResponse,
    summary="Update User Notification Preference",
    description="Update or configure a specific notification channel preference or quiet hours for the authenticated user.",
)
async def update_my_preference(
    pref_in: NotificationPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    return await NotificationEngineService.update_user_preference(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        update_in=pref_in,
    )
