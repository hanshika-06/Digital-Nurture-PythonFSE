"""add is_active to students

Revision ID: rev_002_add_is_active
Revises: rev_001_initial_schema
Create Date: 2026-07-02 01:16:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'rev_002_add_is_active'
down_revision: Union[str, None] = 'rev_001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_active column with default value True
    op.add_column(
        'students',
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('1'), nullable=False)
    )


def downgrade() -> None:
    op.drop_column('students', 'is_active')
