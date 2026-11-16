"""create notes, tags and note_tags tables

Revision ID: 0001
Revises:
Create Date: 2026-11-16
"""
import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(50), nullable=False),
    )
    op.create_index("ix_tags_name", "tags", ["name"], unique=True)
    op.create_table(
        "note_tags",
        sa.Column("note_id", sa.Integer(), sa.ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tag_id", sa.Integer(), sa.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table("note_tags")
    op.drop_index("ix_tags_name", table_name="tags")
    op.drop_table("tags")
    op.drop_table("notes")
