"""Social module tables for CSR activities and employee participation."""

import sqlalchemy as sa
from alembic import op

revision = "003_social_tables"
down_revision = "002_environmental_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    csr_activity_status = sa.Enum(
        "ACTIVE",
        "COMPLETED",
        "CANCELLED",
        "ARCHIVED",
        name="csr_activity_status",
    )
    participation_approval_status = sa.Enum(
        "PENDING",
        "APPROVED",
        "REJECTED",
        name="participation_approval_status",
    )

    op.create_table(
        "csr_activities",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("department_id", sa.UUID(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("evidence_required", sa.Boolean(), nullable=False),
        sa.Column("status", csr_activity_status, nullable=False),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_csr_activities_title", "csr_activities", ["title"], unique=False)
    op.create_index("ix_csr_activities_category", "csr_activities", ["category"], unique=False)
    op.create_index("ix_csr_activities_department_id", "csr_activities", ["department_id"], unique=False)
    op.create_index("ix_csr_activities_start_date", "csr_activities", ["start_date"], unique=False)
    op.create_index("ix_csr_activities_end_date", "csr_activities", ["end_date"], unique=False)
    op.create_index("ix_csr_activities_status", "csr_activities", ["status"], unique=False)

    op.create_table(
        "employee_participation",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("employee_id", sa.UUID(), nullable=False),
        sa.Column("csr_activity_id", sa.UUID(), nullable=False),
        sa.Column("proof_file", sa.String(length=500), nullable=True),
        sa.Column("approval_status", participation_approval_status, nullable=False),
        sa.Column("points_earned", sa.Integer(), nullable=False),
        sa.Column("completion_date", sa.Date(), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["csr_activity_id"], ["csr_activities.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("employee_id", "csr_activity_id", name="uq_employee_csr_activity"),
    )
    op.create_index(
        "ix_employee_participation_employee_id", "employee_participation", ["employee_id"], unique=False
    )
    op.create_index(
        "ix_employee_participation_csr_activity_id",
        "employee_participation",
        ["csr_activity_id"],
        unique=False,
    )
    op.create_index(
        "ix_employee_participation_approval_status",
        "employee_participation",
        ["approval_status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_employee_participation_approval_status", table_name="employee_participation")
    op.drop_index("ix_employee_participation_csr_activity_id", table_name="employee_participation")
    op.drop_index("ix_employee_participation_employee_id", table_name="employee_participation")
    op.drop_table("employee_participation")
    op.drop_index("ix_csr_activities_status", table_name="csr_activities")
    op.drop_index("ix_csr_activities_end_date", table_name="csr_activities")
    op.drop_index("ix_csr_activities_start_date", table_name="csr_activities")
    op.drop_index("ix_csr_activities_department_id", table_name="csr_activities")
    op.drop_index("ix_csr_activities_category", table_name="csr_activities")
    op.drop_index("ix_csr_activities_title", table_name="csr_activities")
    op.drop_table("csr_activities")
    sa.Enum(name="participation_approval_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="csr_activity_status").drop(op.get_bind(), checkfirst=True)
