"""Gamification module tables for challenges, badges, and rewards."""

import sqlalchemy as sa
from alembic import op

revision = "005_gamification_tables"
down_revision = "004_governance_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    challenge_status = sa.Enum(
        "DRAFT",
        "ACTIVE",
        "UNDER_REVIEW",
        "COMPLETED",
        "ARCHIVED",
        name="challenge_status",
    )
    challenge_difficulty = sa.Enum(
        "EASY",
        "MEDIUM",
        "HARD",
        "EXPERT",
        name="challenge_difficulty",
    )
    participation_approval_status = sa.Enum(
        "PENDING",
        "SUBMITTED",
        "APPROVED",
        "REJECTED",
        name="challenge_participation_approval_status",
    )
    badge_status = sa.Enum("ACTIVE", "INACTIVE", "ARCHIVED", name="badge_status")
    reward_status = sa.Enum(
        "ACTIVE",
        "INACTIVE",
        "OUT_OF_STOCK",
        "ARCHIVED",
        name="reward_status",
    )

    op.create_table(
        "challenges",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("xp", sa.Integer(), nullable=False),
        sa.Column("difficulty", challenge_difficulty, nullable=False),
        sa.Column("evidence_required", sa.Boolean(), nullable=False),
        sa.Column("deadline", sa.Date(), nullable=False),
        sa.Column("status", challenge_status, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_challenges_title", "challenges", ["title"], unique=False)
    op.create_index("ix_challenges_category", "challenges", ["category"], unique=False)
    op.create_index("ix_challenges_deadline", "challenges", ["deadline"], unique=False)
    op.create_index("ix_challenges_status", "challenges", ["status"], unique=False)

    op.create_table(
        "challenge_participation",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("employee_id", sa.UUID(), nullable=False),
        sa.Column("challenge_id", sa.UUID(), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("proof_file", sa.String(length=500), nullable=True),
        sa.Column("approval_status", participation_approval_status, nullable=False),
        sa.Column("xp_awarded", sa.Integer(), nullable=False),
        sa.Column("completion_date", sa.Date(), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["challenge_id"], ["challenges.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("employee_id", "challenge_id", name="uq_employee_challenge"),
    )
    op.create_index(
        "ix_challenge_participation_employee_id",
        "challenge_participation",
        ["employee_id"],
        unique=False,
    )
    op.create_index(
        "ix_challenge_participation_challenge_id",
        "challenge_participation",
        ["challenge_id"],
        unique=False,
    )
    op.create_index(
        "ix_challenge_participation_approval_status",
        "challenge_participation",
        ["approval_status"],
        unique=False,
    )

    op.create_table(
        "badges",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("unlock_rule", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.Column("icon", sa.String(length=255), nullable=True),
        sa.Column("status", badge_status, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_badges_name", "badges", ["name"], unique=False)
    op.create_index("ix_badges_status", "badges", ["status"], unique=False)

    op.create_table(
        "employee_badges",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("badge_id", sa.UUID(), nullable=False),
        sa.Column("employee_id", sa.UUID(), nullable=False),
        sa.Column("earned_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["badge_id"], ["badges.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("employee_id", "badge_id", name="uq_employee_badge"),
    )
    op.create_index(
        "ix_employee_badges_badge_id", "employee_badges", ["badge_id"], unique=False
    )
    op.create_index(
        "ix_employee_badges_employee_id", "employee_badges", ["employee_id"], unique=False
    )

    op.create_table(
        "rewards",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("points_required", sa.Integer(), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False),
        sa.Column("status", reward_status, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_rewards_name", "rewards", ["name"], unique=False)
    op.create_index("ix_rewards_status", "rewards", ["status"], unique=False)

    op.create_table(
        "reward_redemptions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("reward_id", sa.UUID(), nullable=False),
        sa.Column("employee_id", sa.UUID(), nullable=False),
        sa.Column("redeemed_points", sa.Integer(), nullable=False),
        sa.Column("redeemed_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["reward_id"], ["rewards.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_reward_redemptions_reward_id", "reward_redemptions", ["reward_id"], unique=False
    )
    op.create_index(
        "ix_reward_redemptions_employee_id",
        "reward_redemptions",
        ["employee_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_reward_redemptions_employee_id", table_name="reward_redemptions")
    op.drop_index("ix_reward_redemptions_reward_id", table_name="reward_redemptions")
    op.drop_table("reward_redemptions")
    op.drop_index("ix_rewards_status", table_name="rewards")
    op.drop_index("ix_rewards_name", table_name="rewards")
    op.drop_table("rewards")
    op.drop_index("ix_employee_badges_employee_id", table_name="employee_badges")
    op.drop_index("ix_employee_badges_badge_id", table_name="employee_badges")
    op.drop_table("employee_badges")
    op.drop_index("ix_badges_status", table_name="badges")
    op.drop_index("ix_badges_name", table_name="badges")
    op.drop_table("badges")
    op.drop_index(
        "ix_challenge_participation_approval_status", table_name="challenge_participation"
    )
    op.drop_index(
        "ix_challenge_participation_challenge_id", table_name="challenge_participation"
    )
    op.drop_index(
        "ix_challenge_participation_employee_id", table_name="challenge_participation"
    )
    op.drop_table("challenge_participation")
    op.drop_index("ix_challenges_status", table_name="challenges")
    op.drop_index("ix_challenges_deadline", table_name="challenges")
    op.drop_index("ix_challenges_category", table_name="challenges")
    op.drop_index("ix_challenges_title", table_name="challenges")
    op.drop_table("challenges")
    sa.Enum(name="reward_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="badge_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="challenge_participation_approval_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="challenge_difficulty").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="challenge_status").drop(op.get_bind(), checkfirst=True)
