"""phase 4 schedules and timetables

Revision ID: 004_phase4_schedules
Revises: 003_phase3_transit_engine
Create Date: 2026-09-27 23:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004_phase4_schedules"
down_revision: Union[str, None] = "003_phase3_transit_engine"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create locations table
    op.create_table(
        "locations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("org_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("nearest_station_code", sa.String(length=10), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_locations_id"), "locations", ["id"], unique=False)
    op.create_index(op.f("ix_locations_org_id"), "locations", ["org_id"], unique=False)
    op.create_index(op.f("ix_locations_nearest_station_code"), "locations", ["nearest_station_code"], unique=False)
    op.create_index("ix_locations_org_active", "locations", ["org_id", "is_active"], unique=False)

    # 2. Create schedules table
    op.create_table(
        "schedules",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("org_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("timezone", sa.String(length=50), nullable=False, server_default="Asia/Kolkata"),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_schedules_id"), "schedules", ["id"], unique=False)
    op.create_index(op.f("ix_schedules_org_id"), "schedules", ["org_id"], unique=False)
    op.create_index("ix_schedules_org_type", "schedules", ["org_id", "type"], unique=False)
    op.create_index("ix_schedules_org_active", "schedules", ["org_id", "is_active"], unique=False)

    # 3. Create schedule_slots table
    op.create_table(
        "schedule_slots",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("schedule_id", sa.UUID(), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("location_id", sa.UUID(), nullable=True),
        sa.Column("location_name", sa.String(length=255), nullable=True),
        sa.Column("instructor_or_supervisor", sa.String(length=255), nullable=True),
        sa.Column("is_overnight", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["schedule_id"], ["schedules.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["location_id"], ["locations.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_schedule_slots_id"), "schedule_slots", ["id"], unique=False)
    op.create_index(op.f("ix_schedule_slots_schedule_id"), "schedule_slots", ["schedule_id"], unique=False)
    op.create_index(op.f("ix_schedule_slots_day_of_week"), "schedule_slots", ["day_of_week"], unique=False)
    op.create_index("ix_slots_schedule_day", "schedule_slots", ["schedule_id", "day_of_week"], unique=False)

    # 4. Create user_schedule_assignments table
    op.create_table(
        "user_schedule_assignments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("org_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("schedule_id", sa.UUID(), nullable=False),
        sa.Column("valid_from", sa.Date(), nullable=False),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["schedule_id"], ["schedules.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_schedule_assignments_id"), "user_schedule_assignments", ["id"], unique=False)
    op.create_index(op.f("ix_user_schedule_assignments_org_id"), "user_schedule_assignments", ["org_id"], unique=False)
    op.create_index(op.f("ix_user_schedule_assignments_user_id"), "user_schedule_assignments", ["user_id"], unique=False)
    op.create_index("ix_assignments_user_dates", "user_schedule_assignments", ["user_id", "valid_from", "valid_until", "is_active"], unique=False)
    op.create_index("ix_assignments_org_user", "user_schedule_assignments", ["org_id", "user_id"], unique=False)

    # 5. Create schedule_exceptions table
    op.create_table(
        "schedule_exceptions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("schedule_id", sa.UUID(), nullable=False),
        sa.Column("exception_date", sa.Date(), nullable=False),
        sa.Column("exception_type", sa.String(length=50), nullable=False),
        sa.Column("replacement_start_time", sa.Time(), nullable=True),
        sa.Column("replacement_end_time", sa.Time(), nullable=True),
        sa.Column("replacement_location_name", sa.String(length=255), nullable=True),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["schedule_id"], ["schedules.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_schedule_exceptions_id"), "schedule_exceptions", ["id"], unique=False)
    op.create_index(op.f("ix_schedule_exceptions_schedule_id"), "schedule_exceptions", ["schedule_id"], unique=False)
    op.create_index(op.f("ix_schedule_exceptions_exception_date"), "schedule_exceptions", ["exception_date"], unique=False)
    op.create_index("ix_exceptions_schedule_date", "schedule_exceptions", ["schedule_id", "exception_date"], unique=False)


def downgrade() -> None:
    op.drop_table("schedule_exceptions")
    op.drop_table("user_schedule_assignments")
    op.drop_table("schedule_slots")
    op.drop_table("schedules")
    op.drop_table("locations")
