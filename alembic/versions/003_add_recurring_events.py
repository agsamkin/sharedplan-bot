"""add recurring events fields

Revision ID: 003
Revises: 002
Create Date: 2026-03-29
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("events", sa.Column("recurrence_rule", sa.String(20), nullable=True))
    op.add_column(
        "events",
        sa.Column(
            "parent_event_id",
            UUID(as_uuid=True),
            sa.ForeignKey("events.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    op.create_index("idx_events_parent", "events", ["parent_event_id"])


def downgrade() -> None:
    op.drop_index("idx_events_parent", table_name="events")
    op.drop_column("events", "parent_event_id")
    op.drop_column("events", "recurrence_rule")
