"""Governance module tables for policies, audits, and compliance issues."""

import sqlalchemy as sa
from alembic import op

revision = "004_governance_tables"
down_revision = "003_social_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    policy_status = sa.Enum(
        "ACTIVE",
        "INACTIVE",
        "ARCHIVED",
        name="policy_status",
    )
    acknowledgement_status = sa.Enum(
        "PENDING",
        "ACKNOWLEDGED",
        name="acknowledgement_status",
    )
    audit_status = sa.Enum(
        "PLANNED",
        "IN_PROGRESS",
        "COMPLETED",
        "CANCELLED",
        name="audit_status",
    )
    compliance_severity = sa.Enum(
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
        name="compliance_severity",
    )
    compliance_issue_status = sa.Enum(
        "OPEN",
        "IN_PROGRESS",
        "CLOSED",
        "OVERDUE",
        name="compliance_issue_status",
    )

    op.create_table(
        "policies",
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
        sa.Column("version", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column("status", policy_status, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_policies_title", "policies", ["title"], unique=False)
    op.create_index("ix_policies_effective_date", "policies", ["effective_date"], unique=False)
    op.create_index("ix_policies_status", "policies", ["status"], unique=False)

    op.create_table(
        "policy_acknowledgements",
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
        sa.Column("policy_id", sa.UUID(), nullable=False),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", acknowledgement_status, nullable=False),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["policy_id"], ["policies.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("employee_id", "policy_id", name="uq_employee_policy_ack"),
    )
    op.create_index(
        "ix_policy_acknowledgements_employee_id",
        "policy_acknowledgements",
        ["employee_id"],
        unique=False,
    )
    op.create_index(
        "ix_policy_acknowledgements_policy_id",
        "policy_acknowledgements",
        ["policy_id"],
        unique=False,
    )
    op.create_index(
        "ix_policy_acknowledgements_status",
        "policy_acknowledgements",
        ["status"],
        unique=False,
    )

    op.create_table(
        "audits",
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
        sa.Column("department_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("auditor_id", sa.UUID(), nullable=False),
        sa.Column("audit_date", sa.Date(), nullable=False),
        sa.Column("status", audit_status, nullable=False),
        sa.ForeignKeyConstraint(["auditor_id"], ["employees.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audits_title", "audits", ["title"], unique=False)
    op.create_index("ix_audits_department_id", "audits", ["department_id"], unique=False)
    op.create_index("ix_audits_auditor_id", "audits", ["auditor_id"], unique=False)
    op.create_index("ix_audits_audit_date", "audits", ["audit_date"], unique=False)
    op.create_index("ix_audits_status", "audits", ["status"], unique=False)

    op.create_table(
        "compliance_issues",
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
        sa.Column("audit_id", sa.UUID(), nullable=True),
        sa.Column("owner_id", sa.UUID(), nullable=False),
        sa.Column("severity", compliance_severity, nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("status", compliance_issue_status, nullable=False),
        sa.ForeignKeyConstraint(["audit_id"], ["audits.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["owner_id"], ["employees.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_compliance_issues_audit_id", "compliance_issues", ["audit_id"], unique=False
    )
    op.create_index(
        "ix_compliance_issues_owner_id", "compliance_issues", ["owner_id"], unique=False
    )
    op.create_index(
        "ix_compliance_issues_severity", "compliance_issues", ["severity"], unique=False
    )
    op.create_index(
        "ix_compliance_issues_due_date", "compliance_issues", ["due_date"], unique=False
    )
    op.create_index(
        "ix_compliance_issues_status", "compliance_issues", ["status"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_compliance_issues_status", table_name="compliance_issues")
    op.drop_index("ix_compliance_issues_due_date", table_name="compliance_issues")
    op.drop_index("ix_compliance_issues_severity", table_name="compliance_issues")
    op.drop_index("ix_compliance_issues_owner_id", table_name="compliance_issues")
    op.drop_index("ix_compliance_issues_audit_id", table_name="compliance_issues")
    op.drop_table("compliance_issues")
    op.drop_index("ix_audits_status", table_name="audits")
    op.drop_index("ix_audits_audit_date", table_name="audits")
    op.drop_index("ix_audits_auditor_id", table_name="audits")
    op.drop_index("ix_audits_department_id", table_name="audits")
    op.drop_index("ix_audits_title", table_name="audits")
    op.drop_table("audits")
    op.drop_index("ix_policy_acknowledgements_status", table_name="policy_acknowledgements")
    op.drop_index("ix_policy_acknowledgements_policy_id", table_name="policy_acknowledgements")
    op.drop_index(
        "ix_policy_acknowledgements_employee_id", table_name="policy_acknowledgements"
    )
    op.drop_table("policy_acknowledgements")
    op.drop_index("ix_policies_status", table_name="policies")
    op.drop_index("ix_policies_effective_date", table_name="policies")
    op.drop_index("ix_policies_title", table_name="policies")
    op.drop_table("policies")
    sa.Enum(name="compliance_issue_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="compliance_severity").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="audit_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="acknowledgement_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="policy_status").drop(op.get_bind(), checkfirst=True)
