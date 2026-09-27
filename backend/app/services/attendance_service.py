import logging
import uuid
from datetime import date, datetime, timezone
from typing import List, Optional, Tuple

from app.models.attendance import (
    AttendanceAudit,
    AttendancePolicy,
    AttendanceRecord,
    AttendanceStatus,
    PolicyAppliesTo,
)
from app.models.auth import User, UserRole
from app.models.schedule import Schedule, ScheduleSlot
from app.schemas.attendance import (
    AttendanceAuditResponse,
    AttendancePolicyCreate,
    AttendancePolicyResponse,
    AttendanceRecordCreate,
    AttendanceRecordResponse,
    AttendanceRecordUpdate,
    AttendanceSummaryResponse,
    BulkAttendanceCreate,
)
from app.services.attendance_calculator import calculate_attendance_summary
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

logger = logging.getLogger("attendance_service")


class AttendanceService:

    @staticmethod
    async def create_policy(
        db: AsyncSession,
        org_id: uuid.UUID,
        policy_in: AttendancePolicyCreate,
    ) -> AttendancePolicyResponse:
        policy = AttendancePolicy(
            org_id=org_id,
            name=policy_in.name,
            applies_to=policy_in.applies_to,
            min_percentage=policy_in.min_percentage,
            late_penalty_multiplier=policy_in.late_penalty_multiplier,
            count_excused_in_denominator=policy_in.count_excused_in_denominator,
            is_active=policy_in.is_active,
            valid_from=policy_in.valid_from,
            valid_until=policy_in.valid_until,
        )
        db.add(policy)
        await db.commit()
        await db.refresh(policy)
        logger.info(f"Created attendance policy {policy.id} for org {org_id}")
        return AttendancePolicyResponse.model_validate(policy)

    @staticmethod
    async def get_policies(
        db: AsyncSession,
        org_id: uuid.UUID,
    ) -> List[AttendancePolicyResponse]:
        query = (
            select(AttendancePolicy)
            .where(AttendancePolicy.org_id == org_id)
            .order_by(AttendancePolicy.created_at.desc())
        )
        result = await db.execute(query)
        policies = result.scalars().all()
        return [AttendancePolicyResponse.model_validate(p) for p in policies]

    @staticmethod
    async def get_active_policy(
        db: AsyncSession,
        org_id: uuid.UUID,
        applies_to: PolicyAppliesTo = PolicyAppliesTo.ALL,
    ) -> Optional[AttendancePolicy]:
        # Look for specific role policy first, then ALL
        query = (
            select(AttendancePolicy)
            .where(
                AttendancePolicy.org_id == org_id,
                AttendancePolicy.is_active.is_(True),
                AttendancePolicy.applies_to.in_([applies_to, PolicyAppliesTo.ALL]),
            )
            .order_by(
                # Specific role takes precedence over ALL
                func.nullif(AttendancePolicy.applies_to == applies_to, False).desc().nullslast(),
                AttendancePolicy.created_at.desc(),
            )
        )
        result = await db.execute(query)
        return result.scalars().first()

    @staticmethod
    async def mark_attendance(
        db: AsyncSession,
        org_id: uuid.UUID,
        record_in: AttendanceRecordCreate,
        marked_by_user_id: uuid.UUID,
    ) -> AttendanceRecordResponse:
        # 1. Validate target user belongs to org
        user_res = await db.execute(
            select(User).where(User.id == record_in.user_id, User.org_id == org_id, User.is_active.is_(True))
        )
        user = user_res.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target user not found in this organization.",
            )

        # 2. Validate schedule slot if provided
        slot = None
        if record_in.schedule_slot_id:
            slot_res = await db.execute(
                select(ScheduleSlot)
                .join(Schedule)
                .where(ScheduleSlot.id == record_in.schedule_slot_id, Schedule.org_id == org_id)
            )
            slot = slot_res.scalars().first()
            if not slot:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Schedule slot not found in this organization.",
                )

        # 3. Check for duplicate record
        dup_query = select(AttendanceRecord).where(
            AttendanceRecord.org_id == org_id,
            AttendanceRecord.user_id == record_in.user_id,
            AttendanceRecord.schedule_slot_id == record_in.schedule_slot_id,
            AttendanceRecord.date == record_in.date,
        )
        dup_res = await db.execute(dup_query)
        if dup_res.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Attendance record already exists for this slot and date. Use PATCH /api/v1/attendance/{id} to correct it.",
            )

        # 4. Create record
        record = AttendanceRecord(
            org_id=org_id,
            user_id=record_in.user_id,
            schedule_slot_id=record_in.schedule_slot_id,
            date=record_in.date,
            status=record_in.status,
            source=record_in.source,
            check_in_time=record_in.check_in_time,
            check_out_time=record_in.check_out_time,
            marked_by_user_id=marked_by_user_id,
            remarks=record_in.remarks,
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)

        return AttendanceRecordResponse(
            id=record.id,
            org_id=record.org_id,
            user_id=record.user_id,
            user_name=user.full_name or user.email,
            user_email=user.email,
            schedule_slot_id=record.schedule_slot_id,
            slot_title=slot.title if slot else None,
            date=record.date,
            status=record.status,
            source=record.source,
            check_in_time=record.check_in_time,
            check_out_time=record.check_out_time,
            marked_by_user_id=record.marked_by_user_id,
            remarks=record.remarks,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    @staticmethod
    async def bulk_mark_attendance(
        db: AsyncSession,
        org_id: uuid.UUID,
        bulk_in: BulkAttendanceCreate,
        marked_by_user_id: uuid.UUID,
    ) -> List[AttendanceRecordResponse]:
        slot = None
        if bulk_in.schedule_slot_id:
            slot_res = await db.execute(
                select(ScheduleSlot)
                .join(Schedule)
                .where(ScheduleSlot.id == bulk_in.schedule_slot_id, Schedule.org_id == org_id)
            )
            slot = slot_res.scalars().first()
            if not slot:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Schedule slot not found in this organization.",
                )

        results: List[AttendanceRecordResponse] = []

        for item in bulk_in.records:
            user_res = await db.execute(
                select(User).where(User.id == item.user_id, User.org_id == org_id, User.is_active.is_(True))
            )
            user = user_res.scalars().first()
            if not user:
                continue  # skip invalid user safely

            # Check if record exists
            existing_query = select(AttendanceRecord).where(
                AttendanceRecord.org_id == org_id,
                AttendanceRecord.user_id == item.user_id,
                AttendanceRecord.schedule_slot_id == bulk_in.schedule_slot_id,
                AttendanceRecord.date == bulk_in.date,
            )
            existing_res = await db.execute(existing_query)
            existing = existing_res.scalars().first()

            if existing:
                # Update status
                existing.status = item.status
                existing.remarks = item.remarks or existing.remarks
                existing.marked_by_user_id = marked_by_user_id
                rec = existing
            else:
                rec = AttendanceRecord(
                    org_id=org_id,
                    user_id=item.user_id,
                    schedule_slot_id=bulk_in.schedule_slot_id,
                    date=bulk_in.date,
                    status=item.status,
                    source=bulk_in.source,
                    marked_by_user_id=marked_by_user_id,
                    remarks=item.remarks,
                )
                db.add(rec)

            await db.flush()
            results.append(
                AttendanceRecordResponse(
                    id=rec.id,
                    org_id=rec.org_id,
                    user_id=rec.user_id,
                    user_name=user.full_name or user.email,
                    user_email=user.email,
                    schedule_slot_id=rec.schedule_slot_id,
                    slot_title=slot.title if slot else None,
                    date=rec.date,
                    status=rec.status,
                    source=rec.source,
                    check_in_time=rec.check_in_time,
                    check_out_time=rec.check_out_time,
                    marked_by_user_id=rec.marked_by_user_id,
                    remarks=rec.remarks,
                    created_at=rec.created_at or datetime.now(timezone.utc),
                    updated_at=rec.updated_at or datetime.now(timezone.utc),
                )
            )

        await db.commit()
        return results

    @staticmethod
    async def get_user_attendance(
        db: AsyncSession,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status_filter: Optional[AttendanceStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[AttendanceRecordResponse], int]:
        filters = [AttendanceRecord.org_id == org_id, AttendanceRecord.user_id == user_id]
        if start_date:
            filters.append(AttendanceRecord.date >= start_date)
        if end_date:
            filters.append(AttendanceRecord.date <= end_date)
        if status_filter:
            filters.append(AttendanceRecord.status == status_filter)

        count_query = select(func.count(AttendanceRecord.id)).where(*filters)
        total_res = await db.execute(count_query)
        total = total_res.scalar() or 0

        query = (
            select(AttendanceRecord)
            .options(
                selectinload(AttendanceRecord.user),
                selectinload(AttendanceRecord.schedule_slot),
            )
            .where(*filters)
            .order_by(AttendanceRecord.date.desc(), AttendanceRecord.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        res = await db.execute(query)
        records = res.scalars().all()

        items = [
            AttendanceRecordResponse(
                id=r.id,
                org_id=r.org_id,
                user_id=r.user_id,
                user_name=r.user.full_name if r.user else None,
                user_email=r.user.email if r.user else None,
                schedule_slot_id=r.schedule_slot_id,
                slot_title=r.schedule_slot.title if r.schedule_slot else None,
                date=r.date,
                status=r.status,
                source=r.source,
                check_in_time=r.check_in_time,
                check_out_time=r.check_out_time,
                marked_by_user_id=r.marked_by_user_id,
                remarks=r.remarks,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
            for r in records
        ]
        return items, total

    @staticmethod
    async def get_user_summary(
        db: AsyncSession,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> AttendanceSummaryResponse:
        # 1. Fetch user to check role
        user_res = await db.execute(select(User).where(User.id == user_id, User.org_id == org_id))
        user = user_res.scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        applies_to = PolicyAppliesTo.STUDENT if user.role == UserRole.STUDENT else PolicyAppliesTo.EMPLOYEE
        policy = await AttendanceService.get_active_policy(db, org_id, applies_to)

        min_percentage = policy.min_percentage if policy else 75.0
        late_multiplier = policy.late_penalty_multiplier if policy else 1.0
        count_excused_denom = policy.count_excused_in_denominator if policy else False
        policy_name = policy.name if policy else "Default 75% Statutory Policy"

        # 2. Fetch all records in period
        filters = [AttendanceRecord.org_id == org_id, AttendanceRecord.user_id == user_id]
        if start_date:
            filters.append(AttendanceRecord.date >= start_date)
        if end_date:
            filters.append(AttendanceRecord.date <= end_date)

        query = select(AttendanceRecord).where(*filters)
        res = await db.execute(query)
        records = res.scalars().all()

        return calculate_attendance_summary(
            records=records,
            min_percentage=min_percentage,
            late_penalty_multiplier=late_multiplier,
            count_excused_in_denominator=count_excused_denom,
            user_id=user_id,
            org_id=org_id,
            start_date=start_date,
            end_date=end_date,
            policy_name=policy_name,
        )

    @staticmethod
    async def get_org_attendance(
        db: AsyncSession,
        org_id: uuid.UUID,
        role_filter: Optional[UserRole] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status_filter: Optional[AttendanceStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[AttendanceRecordResponse], int]:
        filters = [AttendanceRecord.org_id == org_id]
        if start_date:
            filters.append(AttendanceRecord.date >= start_date)
        if end_date:
            filters.append(AttendanceRecord.date <= end_date)
        if status_filter:
            filters.append(AttendanceRecord.status == status_filter)

        count_query = select(func.count(AttendanceRecord.id)).join(User, AttendanceRecord.user_id == User.id).where(*filters)
        if role_filter:
            count_query = count_query.where(User.role == role_filter)

        total_res = await db.execute(count_query)
        total = total_res.scalar() or 0

        query = (
            select(AttendanceRecord)
            .join(User, AttendanceRecord.user_id == User.id)
            .options(
                selectinload(AttendanceRecord.user),
                selectinload(AttendanceRecord.schedule_slot),
            )
            .where(*filters)
        )
        if role_filter:
            query = query.where(User.role == role_filter)

        query = query.order_by(AttendanceRecord.date.desc(), AttendanceRecord.created_at.desc()).limit(limit).offset(offset)
        res = await db.execute(query)
        records = res.scalars().all()

        items = [
            AttendanceRecordResponse(
                id=r.id,
                org_id=r.org_id,
                user_id=r.user_id,
                user_name=r.user.full_name if r.user else None,
                user_email=r.user.email if r.user else None,
                schedule_slot_id=r.schedule_slot_id,
                slot_title=r.schedule_slot.title if r.schedule_slot else None,
                date=r.date,
                status=r.status,
                source=r.source,
                check_in_time=r.check_in_time,
                check_out_time=r.check_out_time,
                marked_by_user_id=r.marked_by_user_id,
                remarks=r.remarks,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
            for r in records
        ]
        return items, total

    @staticmethod
    async def correct_attendance(
        db: AsyncSession,
        org_id: uuid.UUID,
        record_id: uuid.UUID,
        update_in: AttendanceRecordUpdate,
        changed_by_user_id: uuid.UUID,
        ip_address: Optional[str] = None,
    ) -> AttendanceRecordResponse:
        query = (
            select(AttendanceRecord)
            .options(
                selectinload(AttendanceRecord.user),
                selectinload(AttendanceRecord.schedule_slot),
            )
            .where(AttendanceRecord.id == record_id, AttendanceRecord.org_id == org_id)
        )
        res = await db.execute(query)
        record = res.scalars().first()

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record not found in this organization.",
            )

        old_status = record.status.value
        new_status = update_in.status.value

        if old_status != new_status:
            # Create audit record
            audit = AttendanceAudit(
                org_id=org_id,
                record_id=record.id,
                changed_by_user_id=changed_by_user_id,
                old_status=old_status,
                new_status=new_status,
                reason=update_in.reason,
                ip_address=ip_address,
            )
            db.add(audit)
            record.status = update_in.status
            record.updated_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(record)
            logger.info(f"Attendance {record.id} corrected from {old_status} to {new_status} by {changed_by_user_id}")

        return AttendanceRecordResponse(
            id=record.id,
            org_id=record.org_id,
            user_id=record.user_id,
            user_name=record.user.full_name if record.user else None,
            user_email=record.user.email if record.user else None,
            schedule_slot_id=record.schedule_slot_id,
            slot_title=record.schedule_slot.title if record.schedule_slot else None,
            date=record.date,
            status=record.status,
            source=record.source,
            check_in_time=record.check_in_time,
            check_out_time=record.check_out_time,
            marked_by_user_id=record.marked_by_user_id,
            remarks=record.remarks,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    @staticmethod
    async def get_record_audits(
        db: AsyncSession,
        org_id: uuid.UUID,
        record_id: uuid.UUID,
    ) -> List[AttendanceAuditResponse]:
        query = (
            select(AttendanceAudit)
            .options(selectinload(AttendanceAudit.changed_by))
            .where(AttendanceAudit.record_id == record_id, AttendanceAudit.org_id == org_id)
            .order_by(AttendanceAudit.created_at.desc())
        )
        res = await db.execute(query)
        audits = res.scalars().all()
        return [
            AttendanceAuditResponse(
                id=a.id,
                record_id=a.record_id,
                changed_by_user_id=a.changed_by_user_id,
                changed_by_name=a.changed_by.full_name if a.changed_by else None,
                old_status=a.old_status,
                new_status=a.new_status,
                reason=a.reason,
                ip_address=a.ip_address,
                created_at=a.created_at,
            )
            for a in audits
        ]
