"""phase 5 attendance engine

Revision ID: 005_phase5_attendance
Revises: 004_phase4_schedules
Create Date: 2026-09-27 23:15:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "005_phase5_attendance"
down_revision: Union[str, None] = "004_phase4_schedules"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create attendance_policies table
    op.create_table(
        "attendance_policies",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("org_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("applies_to", sa.String(length=50), nullable=False),
        sa.Column("min_percentage", sa.Float(), nullable=False, server_default="75.0"),
        sa.Column("late_penalty_multiplier", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("count_excused_in_denominator", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("valid_from", sa.Date(), nullable=True),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_attendance_policies_id"), "attendance_policies", ["id"], unique=False)
    op.create_index(op.f("ix_attendance_policies_org_id"), "attendance_policies", ["org_id"], unique=False)
    op.create_index("ix_attendance_policies_org_applies", "attendance_policies", ["org_id", "applies_to", "is_active"], unique=False)

    # 2. Create attendance_records table
    op.create_table(
        "attendance_records",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("org_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("schedule_slot_id", sa.UUID(), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False, server_default="MANUAL"),
        sa.Column("check_in_time", sa.Time(), nullable=True),
        sa.Column("check_out_time", sa.Time(), nullable=True),
        sa.Column("marked_by_user_id", sa.UUID(), nullable=True),
        sa.Column("remarks", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["schedule_slot_id"], ["schedule_slots.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["marked_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("org_id", "user_id", "schedule_slot_id", "date", name="uq_attendance_user_slot_date"),
    )
    op.create_index(op.f("ix_attendance_records_id"), "attendance_records", ["id"], unique=False)
    op.create_index(op.f("ix_attendance_records_org_id"), "attendance_records", ["org_id"], unique=False)
    op.create_index(op.f("ix_attendance_records_user_id"), "attendance_records", ["user_id"], unique=False)
    op.create_index(op.f("ix_attendance_records_date"), "attendance_records", ["date"], unique=False)
    op.create_index("ix_attendance_org_user_date", "attendance_records", ["org_id", "user_id", "date"], unique=False)
    op.create_index("ix_attendance_slot_date", "attendance_records", ["schedule_slot_id", "date"], unique=False)
    op.create_index("ix_attendance_org_date", "attendance_records", ["org_id", "date"], unique=False)

    # 3. Create attendance_audit table
    op.create_table(
        "attendance_audit",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("org_id", sa.UUID(), nullable=False),
        sa.Column("record_id", sa.UUID(), nullable=False),
        sa.Column("changed_by_user_id", sa.UUID(), nullable=True),
        sa.Column("old_status", sa.String(length=50), nullable=False),
        sa.Column("new_status", sa.String(length=50), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["record_id"], ["attendance_records.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["changed_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_attendance_audit_id"), "attendance_audit", ["id"], unique=False)
    op.create_index("ix_attendance_audit_record", "attendance_audit", ["record_id"], unique=False)
    op.create_index("ix_attendance_audit_org", "attendance_audit", ["org_id"], unique=False)


def downgrade() -> None:
    op.drop_table("attendance_audit")
    op.drop_table("attendance_records")
    op.drop_table("attendance_policies")
