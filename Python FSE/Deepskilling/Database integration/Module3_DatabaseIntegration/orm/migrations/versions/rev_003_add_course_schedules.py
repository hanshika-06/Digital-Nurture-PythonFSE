"""add course_schedules

Revision ID: rev_003_add_course_schedules
Revises: rev_002_add_is_active
Create Date: 2026-07-02 01:17:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'rev_003_add_course_schedules'
down_revision: Union[str, None] = 'rev_002_add_is_active'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create course_schedules table
    op.create_table(
        'course_schedules',
        sa.Column('schedule_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('day_of_week', sa.String(length=20), nullable=False),
        sa.Column('start_time', sa.String(length=10), nullable=False),
        sa.Column('end_time', sa.String(length=10), nullable=False),
        sa.ForeignKeyConstraint(['course_id'], ['courses.course_id'], ),
        sa.PrimaryKeyConstraint('schedule_id')
    )
    op.create_index(op.f('ix_course_schedules_schedule_id'), 'course_schedules', ['schedule_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_course_schedules_schedule_id'), table_name='course_schedules')
    op.drop_table('course_schedules')
