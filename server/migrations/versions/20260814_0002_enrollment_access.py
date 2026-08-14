"""add enrollment access model

Revision ID: 20260814_0002
Revises: 20260812_0001
Create Date: 2026-08-14
"""
from alembic import op
import sqlalchemy as sa


revision = "20260814_0002"
down_revision = "20260812_0001"
branch_labels = None
depends_on = None


def upgrade():
    _add_course_access_columns()
    _create_enrollments()


def downgrade():
    if _has_table("enrollments"):
        op.drop_table("enrollments")
    for column_name in ["manual_enrollment_enabled", "currency", "price_cents", "access_type"]:
        if column_name in _columns("courses"):
            op.drop_column("courses", column_name)


def _has_table(table_name):
    return sa.inspect(op.get_bind()).has_table(table_name)


def _columns(table_name):
    if not _has_table(table_name):
        return set()
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def _indexes(table_name):
    if not _has_table(table_name):
        return set()
    inspector = sa.inspect(op.get_bind())
    index_names = {index["name"] for index in inspector.get_indexes(table_name)}
    unique_names = {constraint["name"] for constraint in inspector.get_unique_constraints(table_name)}
    return index_names | unique_names


def _add_column_if_missing(table_name, column):
    if column.name not in _columns(table_name):
        op.add_column(table_name, column)


def _create_index_if_missing(name, table_name, columns, unique=False):
    if name not in _indexes(table_name):
        op.create_index(name, table_name, columns, unique=unique)


def _add_course_access_columns():
    _add_column_if_missing("courses", sa.Column("access_type", sa.String(length=20), nullable=False, server_default="free"))
    _add_column_if_missing("courses", sa.Column("price_cents", sa.Integer(), nullable=False, server_default="0"))
    _add_column_if_missing("courses", sa.Column("currency", sa.String(length=3), nullable=False, server_default="VND"))
    _add_column_if_missing("courses", sa.Column("manual_enrollment_enabled", sa.Boolean(), nullable=False, server_default=sa.true()))


def _create_enrollments():
    if not _has_table("enrollments"):
        op.create_table(
            "enrollments",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("course_id", sa.Integer(), nullable=False),
            sa.Column("status", sa.String(length=32), nullable=False),
            sa.Column("payment_provider", sa.String(length=40), nullable=True),
            sa.Column("payment_reference", sa.String(length=120), nullable=True),
            sa.Column("note", sa.Text(), nullable=True),
            sa.Column("requested_at", sa.DateTime(), nullable=False),
            sa.Column("approved_at", sa.DateTime(), nullable=True),
            sa.Column("expires_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["course_id"], ["courses.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id", "course_id", name="uq_enrollments_user_course"),
        )
    _create_index_if_missing("ix_enrollments_id", "enrollments", ["id"])
    _create_index_if_missing("ix_enrollments_user_id", "enrollments", ["user_id"])
    _create_index_if_missing("ix_enrollments_course_id", "enrollments", ["course_id"])
    _create_index_if_missing("ix_enrollments_status", "enrollments", ["status"])
