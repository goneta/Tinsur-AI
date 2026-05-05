"""
Alembic environment configuration.
"""
import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, BASE_DIR)

from logging.config import fileConfig
from sqlalchemy import create_engine
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import sqlalchemy as sa
from app.core.database import Base
from app.models import *  # Import all models for autogenerate detection


# Alembic Config object
config = context.config

# Set the SQLAlchemy URL from settings
#config.set_main_option('sqlalchemy.url', settings.DATABASE_URL.replace('%', '%%'))

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate
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


def run_migrations_online():
    from app.core.config import Settings

    print("CONFIG FILE:", Settings.__module__)
    print("CONFIG PATH:", Settings.__module__)
    print("HAS DATABASE:", hasattr(Settings(), "DATABASE_URL"))
    print("ACTUAL CLASS:", Settings)
    
    settings = Settings()

    connectable = create_engine(settings.DATABASE_URL)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
