
"""add assistant inquiry contexts

Revision ID: fe3ead3f9931
Revises: b0130b4aa235
Create Date: 2026-10-10
"""

from alembic import op
import sqlalchemy as sa


revision = "fe3ead3f9931"
down_revision = "b0130b4aa235"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "assistant_inquiry_contexts",
        sa.Column("context_id", sa.String(length=36), nullable=False),
        sa.Column("owner_user_id", sa.String(length=36), nullable=True),
        sa.Column("guest_session_hash", sa.String(length=64), nullable=True),
        sa.Column("question_id", sa.String(length=100), nullable=True),
        sa.Column("context_data", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "absolute_expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.CheckConstraint(
            "(owner_user_id IS NOT NULL AND guest_session_hash IS NULL) "
            "OR (owner_user_id IS NULL AND guest_session_hash IS NOT NULL)",
            name="ck_assistant_context_exactly_one_owner",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'completed', 'expired', 'reset')",
            name="ck_assistant_context_status",
        ),
        sa.CheckConstraint(
            "expires_at <= absolute_expires_at",
            name="ck_assistant_context_expiry_order",
        ),
        sa.ForeignKeyConstraint(
            ["owner_user_id"],
            ["users.user_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("context_id"),
    )

    op.create_index(
        "ix_assistant_inquiry_contexts_owner_user_id",
        "assistant_inquiry_contexts",
        ["owner_user_id"],
    )
    op.create_index(
        "ix_assistant_inquiry_contexts_guest_session_hash",
        "assistant_inquiry_contexts",
        ["guest_session_hash"],
    )
    op.create_index(
        "ix_assistant_inquiry_contexts_last_activity_at",
        "assistant_inquiry_contexts",
        ["last_activity_at"],
    )
    op.create_index(
        "ix_assistant_inquiry_contexts_expires_at",
        "assistant_inquiry_contexts",
        ["expires_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_assistant_inquiry_contexts_expires_at",
        table_name="assistant_inquiry_contexts",
    )
    op.drop_index(
        "ix_assistant_inquiry_contexts_last_activity_at",
        table_name="assistant_inquiry_contexts",
    )
    op.drop_index(
        "ix_assistant_inquiry_contexts_guest_session_hash",
        table_name="assistant_inquiry_contexts",
    )
    op.drop_index(
        "ix_assistant_inquiry_contexts_owner_user_id",
        table_name="assistant_inquiry_contexts",
    )
    op.drop_table("assistant_inquiry_contexts")
