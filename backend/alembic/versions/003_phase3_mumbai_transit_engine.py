"""phase 3 mumbai transit engine

Revision ID: 003_phase3_transit_engine
Revises: 002_phase2_orgs_members
Create Date: 2026-09-27 22:50:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003_phase3_transit_engine"
down_revision: Union[str, None] = "002_phase2_orgs_members"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create transit_lines table
    op.create_table(
        "transit_lines",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("code", sa.String(length=10), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("color", sa.String(length=20), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_transit_lines_code"), "transit_lines", ["code"], unique=True)

    # 2. Create stations table
    op.create_table(
        "stations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("code", sa.String(length=10), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("canonical_name", sa.String(length=100), nullable=False),
        sa.Column("line", sa.String(length=10), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("sequence_order", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_fast_stop", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_interchange", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_stations_code"),
    )
    op.create_index(op.f("ix_stations_code"), "stations", ["code"], unique=True)
    op.create_index(op.f("ix_stations_canonical_name"), "stations", ["canonical_name"], unique=False)
    op.create_index(op.f("ix_stations_line"), "stations", ["line"], unique=False)
    op.create_index("ix_stations_line_seq", "stations", ["line", "sequence_order"], unique=False)

    # 3. Create railway_segments table
    op.create_table(
        "railway_segments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("line_code", sa.String(length=10), nullable=False),
        sa.Column("from_station_code", sa.String(length=10), nullable=False),
        sa.Column("to_station_code", sa.String(length=10), nullable=False),
        sa.Column("sequence_order", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("distance_km", sa.Float(), nullable=True),
        sa.Column("avg_travel_seconds", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_railway_segments_line_code"), "railway_segments", ["line_code"], unique=False)
    op.create_index(op.f("ix_railway_segments_from_station"), "railway_segments", ["from_station_code"], unique=False)
    op.create_index(op.f("ix_railway_segments_to_station"), "railway_segments", ["to_station_code"], unique=False)

    # 4. Create transit_data_sources table
    op.create_table(
        "transit_data_sources",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("provider_type", sa.String(length=50), nullable=False),
        sa.Column("base_url", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="ACTIVE"),
        sa.Column("license_type", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_transit_data_sources_name"),
    )

    # 5. Create live_train_states table
    op.create_table(
        "live_train_states",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("train_number", sa.String(length=20), nullable=False),
        sa.Column("line", sa.String(length=10), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("speed_kmh", sa.Float(), nullable=True),
        sa.Column("bearing", sa.Float(), nullable=True),
        sa.Column("current_station_code", sa.String(length=10), nullable=True),
        sa.Column("next_station_code", sa.String(length=10), nullable=True),
        sa.Column("delay_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("freshness", sa.String(length=50), nullable=False),
        sa.Column("confidence", sa.String(length=50), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_live_train_states_train_number"), "live_train_states", ["train_number"], unique=False)
    op.create_index(op.f("ix_live_train_states_line"), "live_train_states", ["line"], unique=False)
    op.create_index("ix_live_train_lookup", "live_train_states", ["train_number", "observed_at"], unique=False)


def downgrade() -> None:
    op.drop_table("live_train_states")
    op.drop_table("transit_data_sources")
    op.drop_table("railway_segments")
    op.drop_table("stations")
    op.drop_table("transit_lines")
