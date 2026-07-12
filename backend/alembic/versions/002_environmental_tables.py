"""Environmental module tables and seed departments."""

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op

revision = "002_environmental_tables"
down_revision = "001_initial_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    goal_status = sa.Enum(
        "NOT_STARTED",
        "IN_PROGRESS",
        "COMPLETED",
        "OVERDUE",
        name="goal_status",
    )
    carbon_transaction_status = sa.Enum(
        "ACTIVE",
        "ARCHIVED",
        "CANCELLED",
        name="carbon_transaction_status",
    )
    emission_factor_status = sa.Enum(
        "ACTIVE",
        "INACTIVE",
        "ARCHIVED",
        name="emission_factor_status",
    )
    product_esg_status = sa.Enum(
        "ACTIVE",
        "INACTIVE",
        "ARCHIVED",
        name="product_esg_status",
    )

    op.create_table(
        "emission_factors",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("source_type", sa.String(length=100), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=False),
        sa.Column("co2_factor", sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", emission_factor_status, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_emission_factors_name", "emission_factors", ["name"], unique=False)
    op.create_index("ix_emission_factors_source_type", "emission_factors", ["source_type"], unique=False)

    op.create_table(
        "carbon_transactions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("department_id", sa.UUID(), nullable=False),
        sa.Column("emission_factor_id", sa.UUID(), nullable=False),
        sa.Column("activity_name", sa.String(length=255), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=14, scale=4), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=False),
        sa.Column("calculated_emission", sa.Numeric(precision=14, scale=4), nullable=False),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("status", carbon_transaction_status, nullable=False),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["emission_factor_id"], ["emission_factors.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_carbon_transactions_department_id", "carbon_transactions", ["department_id"], unique=False)
    op.create_index("ix_carbon_transactions_emission_factor_id", "carbon_transactions", ["emission_factor_id"], unique=False)
    op.create_index("ix_carbon_transactions_transaction_date", "carbon_transactions", ["transaction_date"], unique=False)
    op.create_index("ix_carbon_transactions_status", "carbon_transactions", ["status"], unique=False)

    op.create_table(
        "environmental_goals",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("department_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("target_value", sa.Numeric(precision=14, scale=4), nullable=False),
        sa.Column("current_value", sa.Numeric(precision=14, scale=4), nullable=False),
        sa.Column("deadline", sa.Date(), nullable=False),
        sa.Column("status", goal_status, nullable=False),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_environmental_goals_department_id", "environmental_goals", ["department_id"], unique=False)
    op.create_index("ix_environmental_goals_deadline", "environmental_goals", ["deadline"], unique=False)
    op.create_index("ix_environmental_goals_status", "environmental_goals", ["status"], unique=False)

    op.create_table(
        "product_esg_profiles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("product_name", sa.String(length=255), nullable=False),
        sa.Column("carbon_score", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("recyclability", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("supplier_score", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", product_esg_status, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_product_esg_profiles_product_name", "product_esg_profiles", ["product_name"], unique=False)

    connection = op.get_bind()
    org_row = connection.execute(sa.text("SELECT id FROM organizations LIMIT 1")).fetchone()
    if org_row is not None:
        now = datetime.now(timezone.utc)
        organization_id = org_row[0]
        department_rows = [
            {
                "id": uuid.uuid4(),
                "organization_id": organization_id,
                "slug": "operations",
                "name": "Operations",
                "code": "OPS",
                "status": "ACTIVE",
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": uuid.uuid4(),
                "organization_id": organization_id,
                "slug": "manufacturing",
                "name": "Manufacturing",
                "code": "MFG",
                "status": "ACTIVE",
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": uuid.uuid4(),
                "organization_id": organization_id,
                "slug": "logistics",
                "name": "Logistics",
                "code": "LOG",
                "status": "ACTIVE",
                "created_at": now,
                "updated_at": now,
            },
        ]
        op.bulk_insert(
            sa.table(
                "departments",
                sa.column("id", sa.UUID()),
                sa.column("organization_id", sa.UUID()),
                sa.column("slug", sa.String()),
                sa.column("name", sa.String()),
                sa.column("code", sa.String()),
                sa.column(
                    "status",
                    sa.Enum("ACTIVE", "INACTIVE", "ARCHIVED", name="department_status"),
                ),
                sa.column("created_at", sa.DateTime(timezone=True)),
                sa.column("updated_at", sa.DateTime(timezone=True)),
            ),
            department_rows,
        )


def downgrade() -> None:
    op.drop_index("ix_product_esg_profiles_product_name", table_name="product_esg_profiles")
    op.drop_table("product_esg_profiles")
    op.drop_index("ix_environmental_goals_status", table_name="environmental_goals")
    op.drop_index("ix_environmental_goals_deadline", table_name="environmental_goals")
    op.drop_index("ix_environmental_goals_department_id", table_name="environmental_goals")
    op.drop_table("environmental_goals")
    op.drop_index("ix_carbon_transactions_status", table_name="carbon_transactions")
    op.drop_index("ix_carbon_transactions_transaction_date", table_name="carbon_transactions")
    op.drop_index("ix_carbon_transactions_emission_factor_id", table_name="carbon_transactions")
    op.drop_index("ix_carbon_transactions_department_id", table_name="carbon_transactions")
    op.drop_table("carbon_transactions")
    op.drop_index("ix_emission_factors_source_type", table_name="emission_factors")
    op.drop_index("ix_emission_factors_name", table_name="emission_factors")
    op.drop_table("emission_factors")

    sa.Enum(name="product_esg_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="emission_factor_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="carbon_transaction_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="goal_status").drop(op.get_bind(), checkfirst=True)
