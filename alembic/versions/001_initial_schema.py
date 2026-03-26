"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-26
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("first_name", sa.String(length=255), nullable=False),
        sa.Column(
            "reminder_settings",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text(
                "'{\"1d\": true, \"2h\": true, \"1h\": false, \"30m\": false, \"15m\": true, \"0m\": false}'::jsonb"
            ),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "spaces",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("invite_code", sa.String(length=32), nullable=False),
        sa.Column("created_by", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("invite_code"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
    )

    op.create_table(
        "user_spaces",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "space_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("user_id", "space_id"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["space_id"], ["spaces.id"], ondelete="CASCADE"
        ),
        sa.CheckConstraint(
            "role IN ('admin', 'member')", name="ck_user_spaces_role"
        ),
    )

    op.create_table(
        "events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "space_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("event_time", sa.Time(), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=False),
        sa.Column("raw_input", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["space_id"], ["spaces.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
    )
    op.create_index(
        "idx_events_space_date", "events", ["space_id", "event_date"]
    )

    op.create_table(
        "scheduled_reminders",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "event_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "remind_at", sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column("reminder_type", sa.String(length=10), nullable=False),
        sa.Column(
            "sent", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["event_id"], ["events.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
    )
    op.create_index(
        "idx_reminders_remind_at_sent",
        "scheduled_reminders",
        ["remind_at", "sent"],
    )


def downgrade() -> None:
    op.drop_table("scheduled_reminders")
    op.drop_table("events")
    op.drop_table("user_spaces")
    op.drop_table("spaces")
    op.drop_table("users")
