"""Initial foundation schema with RBAC seed data."""

import uuid
from datetime import datetime, timezone

import bcrypt
import sqlalchemy as sa
from alembic import op

revision = "001_initial_foundation"
down_revision = None
branch_labels = None
depends_on = None

ADMIN_PASSWORD_HASH = bcrypt.hashpw(b"ChangeMe123!", bcrypt.gensalt()).decode()

PERMISSIONS = [
    ("dashboard:read", "View Dashboard", "dashboard", "Access dashboard metrics"),
    ("departments:read", "View Departments", "administration", "View department records"),
    ("departments:write", "Manage Departments", "administration", "Create and update departments"),
    ("carbon:read", "View Carbon Data", "environmental", "View carbon transactions and factors"),
    ("carbon:write", "Manage Carbon Data", "environmental", "Manage carbon transactions and factors"),
    ("csr:read", "View CSR Activities", "social", "View CSR activities"),
    ("csr:write", "Manage CSR Activities", "social", "Manage CSR activities"),
    ("csr:participate", "Participate in CSR", "social", "Participate in CSR activities"),
    ("policies:read", "View Policies", "governance", "View governance policies"),
    ("policies:write", "Manage Policies", "governance", "Manage governance policies"),
    ("policies:acknowledge", "Acknowledge Policies", "governance", "Acknowledge policy documents"),
    ("audits:read", "View Audits", "governance", "View audit records"),
    ("audits:write", "Manage Audits", "governance", "Manage audit records"),
    ("challenges:read", "View Challenges", "gamification", "View gamification challenges"),
    ("challenges:write", "Manage Challenges", "gamification", "Manage gamification challenges"),
    ("challenges:participate", "Participate in Challenges", "gamification", "Join and submit challenges"),
    ("reports:read", "View Reports", "reports", "View ESG reports"),
    ("reports:export", "Export Reports", "reports", "Export ESG reports"),
    ("settings:read", "View Settings", "administration", "View platform settings"),
    ("settings:write", "Manage Settings", "administration", "Manage platform settings"),
    ("users:read", "View Users", "auth", "View user accounts"),
    ("users:write", "Manage Users", "auth", "Manage user accounts"),
]

ROLE_PERMISSIONS = {
    "ADMIN": [code for code, _, _, _ in PERMISSIONS],
    "ESG_MANAGER": [
        "dashboard:read",
        "carbon:read",
        "carbon:write",
        "csr:read",
        "csr:write",
        "policies:read",
        "policies:write",
        "audits:read",
        "audits:write",
        "challenges:read",
        "challenges:write",
        "reports:read",
        "reports:export",
        "settings:read",
    ],
    "HR_MANAGER": [
        "dashboard:read",
        "csr:read",
        "csr:write",
        "challenges:read",
        "challenges:write",
        "reports:read",
        "settings:read",
    ],
    "AUDITOR": [
        "dashboard:read",
        "policies:read",
        "audits:read",
        "reports:read",
        "reports:export",
    ],
    "EMPLOYEE": [
        "dashboard:read",
        "carbon:read",
        "csr:participate",
        "policies:read",
        "policies:acknowledge",
        "audits:read",
        "challenges:participate",
        "reports:read",
    ],
}


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.Enum("ACTIVE", "INACTIVE", "ARCHIVED", name="entity_status"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_organizations_slug", "organizations", ["slug"], unique=True)

    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("status", sa.Enum("ACTIVE", "INACTIVE", "LOCKED", name="user_status"), nullable=False),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "roles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_roles_slug", "roles", ["slug"], unique=True)

    op.create_table(
        "permissions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("module", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_permissions_code", "permissions", ["code"], unique=True)
    op.create_index("ix_permissions_module", "permissions", ["module"], unique=False)

    op.create_table(
        "departments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("head_id", sa.UUID(), nullable=True),
        sa.Column("parent_department_id", sa.UUID(), nullable=True),
        sa.Column("status", sa.Enum("ACTIVE", "INACTIVE", "ARCHIVED", name="department_status"), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_department_id"], ["departments.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_departments_code", "departments", ["code"], unique=False)
    op.create_index("ix_departments_organization_id", "departments", ["organization_id"], unique=False)
    op.create_index("ix_departments_slug", "departments", ["slug"], unique=True)

    op.create_table(
        "employees",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("department_id", sa.UUID(), nullable=True),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("designation", sa.String(length=150), nullable=True),
        sa.Column("status", sa.Enum("ACTIVE", "INACTIVE", "ARCHIVED", name="employee_status"), nullable=False),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_employees_department_id", "employees", ["department_id"], unique=False)
    op.create_index("ix_employees_email", "employees", ["email"], unique=True)
    op.create_index("ix_employees_organization_id", "employees", ["organization_id"], unique=False)

    op.create_foreign_key(
        "fk_departments_head_id_employees",
        "departments",
        "employees",
        ["head_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "user_roles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("role_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "role_id", name="uq_user_role"),
    )
    op.create_index("ix_user_roles_role_id", "user_roles", ["role_id"], unique=False)
    op.create_index("ix_user_roles_user_id", "user_roles", ["user_id"], unique=False)

    op.create_table(
        "role_permissions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("role_id", sa.UUID(), nullable=False),
        sa.Column("permission_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )
    op.create_index("ix_role_permissions_permission_id", "role_permissions", ["permission_id"], unique=False)
    op.create_index("ix_role_permissions_role_id", "role_permissions", ["role_id"], unique=False)

    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"], unique=False)

    op.create_table(
        "activity_logs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("employee_id", sa.UUID(), nullable=True),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity", sa.String(length=100), nullable=False),
        sa.Column("entity_id", sa.UUID(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_activity_logs_action", "activity_logs", ["action"], unique=False)
    op.create_index("ix_activity_logs_employee_id", "activity_logs", ["employee_id"], unique=False)
    op.create_index("ix_activity_logs_entity", "activity_logs", ["entity"], unique=False)
    op.create_index("ix_activity_logs_user_id", "activity_logs", ["user_id"], unique=False)

    now = datetime.now(timezone.utc)
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()
    employee_id = uuid.uuid4()

    op.bulk_insert(
        sa.table(
            "organizations",
            sa.column("id", sa.UUID()),
            sa.column("slug", sa.String()),
            sa.column("name", sa.String()),
            sa.column(
                "status",
                sa.Enum("ACTIVE", "INACTIVE", "ARCHIVED", name="entity_status"),
            ),
            sa.column("created_at", sa.DateTime(timezone=True)),
            sa.column("updated_at", sa.DateTime(timezone=True)),
        ),
        [
            {
                "id": organization_id,
                "slug": "ecosphere-default",
                "name": "EcoSphere Default Organization",
                "status": "ACTIVE",
                "created_at": now,
                "updated_at": now,
            }
        ],
    )

    permission_rows = []
    permission_ids: dict[str, uuid.UUID] = {}
    for code, name, module, description in PERMISSIONS:
        permission_id = uuid.uuid4()
        permission_ids[code] = permission_id
        permission_rows.append(
            {
                "id": permission_id,
                "code": code,
                "name": name,
                "module": module,
                "description": description,
                "created_at": now,
                "updated_at": now,
            }
        )

    op.bulk_insert(
        sa.table(
            "permissions",
            sa.column("id", sa.UUID()),
            sa.column("code", sa.String()),
            sa.column("name", sa.String()),
            sa.column("module", sa.String()),
            sa.column("description", sa.Text()),
            sa.column("created_at", sa.DateTime(timezone=True)),
            sa.column("updated_at", sa.DateTime(timezone=True)),
        ),
        permission_rows,
    )

    role_rows = []
    role_ids: dict[str, uuid.UUID] = {}
    for role_name in ROLE_PERMISSIONS:
        role_id = uuid.uuid4()
        role_ids[role_name] = role_id
        role_rows.append(
            {
                "id": role_id,
                "slug": role_name.lower().replace("_", "-"),
                "name": role_name,
                "description": f"{role_name.replace('_', ' ').title()} role",
                "created_at": now,
                "updated_at": now,
            }
        )

    op.bulk_insert(
        sa.table(
            "roles",
            sa.column("id", sa.UUID()),
            sa.column("slug", sa.String()),
            sa.column("name", sa.String()),
            sa.column("description", sa.Text()),
            sa.column("created_at", sa.DateTime(timezone=True)),
            sa.column("updated_at", sa.DateTime(timezone=True)),
        ),
        role_rows,
    )

    role_permission_rows = []
    for role_name, permission_codes in ROLE_PERMISSIONS.items():
        for permission_code in permission_codes:
            role_permission_rows.append(
                {
                    "id": uuid.uuid4(),
                    "role_id": role_ids[role_name],
                    "permission_id": permission_ids[permission_code],
                    "created_at": now,
                    "updated_at": now,
                }
            )

    op.bulk_insert(
        sa.table(
            "role_permissions",
            sa.column("id", sa.UUID()),
            sa.column("role_id", sa.UUID()),
            sa.column("permission_id", sa.UUID()),
            sa.column("created_at", sa.DateTime(timezone=True)),
            sa.column("updated_at", sa.DateTime(timezone=True)),
        ),
        role_permission_rows,
    )

    op.bulk_insert(
        sa.table(
            "users",
            sa.column("id", sa.UUID()),
            sa.column("email", sa.String()),
            sa.column("password_hash", sa.String()),
            sa.column(
                "status",
                sa.Enum("ACTIVE", "INACTIVE", "LOCKED", name="user_status"),
            ),
            sa.column("created_at", sa.DateTime(timezone=True)),
            sa.column("updated_at", sa.DateTime(timezone=True)),
        ),
        [
            {
                "id": user_id,
                "email": "admin@ecosphere.local",
                "password_hash": ADMIN_PASSWORD_HASH,
                "status": "ACTIVE",
                "created_at": now,
                "updated_at": now,
            }
        ],
    )

    op.bulk_insert(
        sa.table(
            "employees",
            sa.column("id", sa.UUID()),
            sa.column("organization_id", sa.UUID()),
            sa.column("user_id", sa.UUID()),
            sa.column("first_name", sa.String()),
            sa.column("last_name", sa.String()),
            sa.column("email", sa.String()),
            sa.column("designation", sa.String()),
            sa.column(
                "status",
                sa.Enum("ACTIVE", "INACTIVE", "ARCHIVED", name="employee_status"),
            ),
            sa.column("created_at", sa.DateTime(timezone=True)),
            sa.column("updated_at", sa.DateTime(timezone=True)),
        ),
        [
            {
                "id": employee_id,
                "organization_id": organization_id,
                "user_id": user_id,
                "first_name": "System",
                "last_name": "Administrator",
                "email": "admin@ecosphere.local",
                "designation": "Platform Administrator",
                "status": "ACTIVE",
                "created_at": now,
                "updated_at": now,
            }
        ],
    )

    op.bulk_insert(
        sa.table(
            "user_roles",
            sa.column("id", sa.UUID()),
            sa.column("user_id", sa.UUID()),
            sa.column("role_id", sa.UUID()),
            sa.column("created_at", sa.DateTime(timezone=True)),
            sa.column("updated_at", sa.DateTime(timezone=True)),
        ),
        [
            {
                "id": uuid.uuid4(),
                "user_id": user_id,
                "role_id": role_ids["ADMIN"],
                "created_at": now,
                "updated_at": now,
            }
        ],
    )


def downgrade() -> None:
    op.drop_table("activity_logs")
    op.drop_table("refresh_tokens")
    op.drop_table("role_permissions")
    op.drop_table("user_roles")
    op.drop_table("employees")
    op.drop_constraint("fk_departments_head_id_employees", "departments", type_="foreignkey")
    op.drop_table("departments")
    op.drop_table("permissions")
    op.drop_table("roles")
    op.drop_table("users")
    op.drop_table("organizations")
    op.execute("DROP TYPE IF EXISTS employee_status")
    op.execute("DROP TYPE IF EXISTS department_status")
    op.execute("DROP TYPE IF EXISTS user_status")
    op.execute("DROP TYPE IF EXISTS entity_status")
