"""initial schema

Revision ID: 20260812_0001
Revises:
Create Date: 2026-08-12
"""
from alembic import op
import sqlalchemy as sa


revision = "20260812_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    _create_users()
    _create_courses()
    _create_quiz_history()
    _create_content_items()


def downgrade():
    op.drop_table("content_items")
    op.drop_table("quiz_history")
    op.drop_table("courses")
    op.drop_table("users")


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


def _create_users():
    if not _has_table("users"):
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("hashed_password", sa.String(length=255), nullable=False),
            sa.Column("role", sa.String(length=32), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
    _create_index_if_missing("ix_users_id", "users", ["id"])
    _create_index_if_missing("ix_users_email", "users", ["email"], unique=True)
    _create_index_if_missing("ix_users_role", "users", ["role"])


def _create_courses():
    if not _has_table("courses"):
        op.create_table(
            "courses",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("slug", sa.String(length=80), nullable=True),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("author", sa.String(length=120), nullable=False),
            sa.Column("category", sa.String(length=80), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("image_url", sa.String(length=255), nullable=True),
            sa.Column("level", sa.String(length=40), nullable=True),
            sa.Column("lessons", sa.Integer(), nullable=True),
            sa.Column("duration", sa.String(length=80), nullable=True),
            sa.Column("rating", sa.Float(), nullable=True),
            sa.Column("students", sa.Integer(), nullable=True),
            sa.Column("progress", sa.Integer(), nullable=True),
            sa.Column("tag", sa.String(length=80), nullable=True),
            sa.Column("outcomes", sa.JSON(), nullable=True),
            sa.Column("syllabus", sa.JSON(), nullable=True),
            sa.Column("resources", sa.JSON(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
    else:
        _add_column_if_missing("courses", sa.Column("slug", sa.String(length=80), nullable=True))
        _add_column_if_missing("courses", sa.Column("level", sa.String(length=40), nullable=True))
        _add_column_if_missing("courses", sa.Column("lessons", sa.Integer(), nullable=True))
        _add_column_if_missing("courses", sa.Column("duration", sa.String(length=80), nullable=True))
        _add_column_if_missing("courses", sa.Column("rating", sa.Float(), nullable=True))
        _add_column_if_missing("courses", sa.Column("students", sa.Integer(), nullable=True))
        _add_column_if_missing("courses", sa.Column("progress", sa.Integer(), nullable=True))
        _add_column_if_missing("courses", sa.Column("tag", sa.String(length=80), nullable=True))
        _add_column_if_missing("courses", sa.Column("outcomes", sa.JSON(), nullable=True))
        _add_column_if_missing("courses", sa.Column("syllabus", sa.JSON(), nullable=True))
        _add_column_if_missing("courses", sa.Column("resources", sa.JSON(), nullable=True))
    _create_index_if_missing("ix_courses_id", "courses", ["id"])
    _create_index_if_missing("ix_courses_slug", "courses", ["slug"], unique=True)
    _create_index_if_missing("ix_courses_title", "courses", ["title"])
    _create_index_if_missing("ix_courses_category", "courses", ["category"])


def _create_quiz_history():
    if not _has_table("quiz_history"):
        op.create_table(
            "quiz_history",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.String(), nullable=True),
            sa.Column("course_id", sa.String(), nullable=True),
            sa.Column("score", sa.Integer(), nullable=True),
            sa.Column("total", sa.Integer(), nullable=True),
            sa.Column("topic", sa.String(), nullable=True),
            sa.Column("max_streak", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
    _create_index_if_missing("ix_quiz_history_id", "quiz_history", ["id"])
    _create_index_if_missing("ix_quiz_history_user_id", "quiz_history", ["user_id"])
    _create_index_if_missing("ix_quiz_history_course_id", "quiz_history", ["course_id"])


def _create_content_items():
    if not _has_table("content_items"):
        op.create_table(
            "content_items",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("kind", sa.String(length=40), nullable=False),
            sa.Column("slug", sa.String(length=120), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("payload", sa.JSON(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
    _create_index_if_missing("ix_content_items_id", "content_items", ["id"])
    _create_index_if_missing("ix_content_items_kind", "content_items", ["kind"])
    _create_index_if_missing("ix_content_items_slug", "content_items", ["slug"], unique=True)
    _create_index_if_missing("ix_content_items_title", "content_items", ["title"])
