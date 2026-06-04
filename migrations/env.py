from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.config import DATABASE_URL
from app.infrastructure.db.base import Base

# Import models so Alembic can see their metadata for autogenerate.
from app.infrastructure.persistence.accounts import models as accounts_models  # noqa: F401
from app.infrastructure.persistence.accounting import models as accounting_models  # noqa: F401
from app.infrastructure.persistence.assets import models as assets_models  # noqa: F401
from app.infrastructure.persistence.audit import models as audit_models  # noqa: F401
from app.infrastructure.persistence.auth import models as auth_models  # noqa: F401
from app.infrastructure.persistence.banking import models as banking_models  # noqa: F401
from app.infrastructure.persistence.budgets import models as budgets_models  # noqa: F401
from app.infrastructure.persistence.core import models as core_models  # noqa: F401
from app.infrastructure.persistence.documents import models as documents_models  # noqa: F401
from app.infrastructure.persistence.finance import models as finance_models  # noqa: F401
from app.infrastructure.persistence.fiscal import models as fiscal_models  # noqa: F401
from app.infrastructure.persistence.hr import models as hr_models  # noqa: F401
from app.infrastructure.persistence.inventory import models as inventory_models  # noqa: F401
from app.infrastructure.persistence.partners import models as partners_models  # noqa: F401
from app.infrastructure.persistence.purchases import models as purchases_models  # noqa: F401
from app.infrastructure.persistence.sales import models as sales_models  # noqa: F401
from app.infrastructure.persistence.settings import models as settings_models  # noqa: F401
from app.infrastructure.persistence.treasury import models as treasury_models  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
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
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
