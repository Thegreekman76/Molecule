# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys
from core.database.base import Base
from core.metadata.models import TableMetadata, FieldMetadata, RelationshipMetadata, UITemplate
from core.security.auth import UserModel

# Agregar el directorio raíz del proyecto al PATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# override sqlalchemy.url from environment variable if exists
if os.getenv("DATABASE_URL"):
    config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
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
    """Run migrations in 'online' mode."""
    # Configuración de la conexión
    configuration = config.get_section(config.config_ini_section)
    if not configuration:
        configuration = {}
    configuration["sqlalchemy.url"] = os.getenv(
        "DATABASE_URL", 
        "postgresql://admin:secret@localhost:5434/molecule_db"
    )
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            include_schemas=True,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()