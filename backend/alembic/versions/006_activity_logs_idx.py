"""Add index on activity_logs.created_at for recent activity queries."""

from alembic import op

revision = "006_activity_logs_idx"
down_revision = "005_gamification_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_activity_logs_created_at",
        "activity_logs",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_activity_logs_created_at", table_name="activity_logs")
