from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.auth.models import (  # noqa: F401
    ActivityLog,
    Department,
    Employee,
    Organization,
    Permission,
    RefreshToken,
    Role,
    RolePermission,
    User,
    UserRole,
)
from app.modules.environmental.models import (  # noqa: F401
    CarbonTransaction,
    EmissionFactor,
    EnvironmentalGoal,
    ProductEsgProfile,
)
from app.modules.governance.models import (  # noqa: F401
    Audit,
    ComplianceIssue,
    Policy,
    PolicyAcknowledgement,
)
from app.modules.gamification.models import (  # noqa: F401
    Badge,
    Challenge,
    ChallengeParticipation,
    EmployeeBadge,
    Reward,
    RewardRedemption,
)
from app.modules.social.models import (  # noqa: F401
    CsrActivity,
    EmployeeParticipation,
)
from app.core.config import get_settings
from app.shared.models.base import Base

config = context.config
settings = get_settings()
config.set_main_option("sqlalchemy.url", str(settings.database_url))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
