"""initial schema

Revision ID: rev_001_initial_schema
Revises: None
Create Date: 2026-07-02 01:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'rev_001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create departments table
    op.create_table(
        'departments',
        sa.Column('department_id', sa.Integer(), nullable=False),
        sa.Column('dept_name', sa.String(length=100), nullable=False),
        sa.Column('head_of_dept', sa.String(length=100), nullable=True),
        sa.Column('budget', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('department_id')
    )
    op.create_index(op.f('ix_departments_department_id'), 'departments', ['department_id'], unique=False)

    # 2. Create students table (without is_active to match Hands-On 07 baseline)
    op.create_table(
        'students',
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=50), nullable=False),
        sa.Column('last_name', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('enrollment_year', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['department_id'], ['departments.department_id'], ),
        sa.PrimaryKeyConstraint('student_id')
    )
    op.create_index(op.f('ix_students_email'), 'students', ['email'], unique=True)
    op.create_index(op.f('ix_students_student_id'), 'students', ['student_id'], unique=False)

    # 3. Create courses table
    op.create_table(
        'courses',
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('course_name', sa.String(length=150), nullable=False),
        sa.Column('course_code', sa.String(length=20), nullable=False),
        sa.Column('credits', sa.Integer(), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['department_id'], ['departments.department_id'], ),
        sa.PrimaryKeyConstraint('course_id')
    )
    op.create_index(op.f('ix_courses_course_code'), 'courses', ['course_code'], unique=True)
    op.create_index(op.f('ix_courses_course_id'), 'courses', ['course_id'], unique=False)

    # 4. Create enrollments table
    op.create_table(
        'enrollments',
        sa.Column('enrollment_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('enrollment_date', sa.Date(), nullable=True),
        sa.Column('grade', sa.String(length=2), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.course_id'], ),
        sa.ForeignKeyConstraint(['student_id'], ['students.student_id'], ),
        sa.PrimaryKeyConstraint('enrollment_id')
    )
    op.create_index(op.f('ix_enrollments_enrollment_id'), 'enrollments', ['enrollment_id'], unique=False)

    # 5. Create professors table
    op.create_table(
        'professors',
        sa.Column('professor_id', sa.Integer(), nullable=False),
        sa.Column('prof_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('salary', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['department_id'], ['departments.department_id'], ),
        sa.PrimaryKeyConstraint('professor_id')
    )
    op.create_index(op.f('ix_professors_email'), 'professors', ['email'], unique=True)
    op.create_index(op.f('ix_professors_professor_id'), 'professors', ['professor_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_professors_professor_id'), table_name='professors')
    op.drop_index(op.f('ix_professors_email'), table_name='professors')
    op.drop_table('professors')
    op.drop_index(op.f('ix_enrollments_enrollment_id'), table_name='enrollments')
    op.drop_table('enrollments')
    op.drop_index(op.f('ix_courses_course_id'), table_name='courses')
    op.drop_index(op.f('ix_courses_course_code'), table_name='courses')
    op.drop_table('courses')
    op.drop_index(op.f('ix_students_student_id'), table_name='students')
    op.drop_index(op.f('ix_students_email'), table_name='students')
    op.drop_table('students')
    op.drop_index(op.f('ix_departments_department_id'), table_name='departments')
    op.drop_table('departments')
