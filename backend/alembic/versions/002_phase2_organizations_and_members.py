"""phase 2 organizations and members

Revision ID: 002_phase2_orgs_members
Revises: 001_phase1_auth
Create Date: 2026-09-27 22:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002_phase2_orgs_members"
down_revision: Union[str, None] = "001_phase1_auth"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_active to organizations table
    op.add_column(
        "organizations",
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
    )

    # Add full_name to users table
    op.add_column(
        "users",
        sa.Column("full_name", sa.String(length=255), nullable=True),
    )

    # Add compound index for active org users
    op.create_index(
        "ix_users_org_active",
        "users",
        ["org_id", "is_active"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_users_org_active", table_name="users")
    op.drop_column("users", "full_name")
    op.drop_column("organizations", "is_active")
