# backend/alembic/env.py
import sys
import os
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# 讓 alembic 可以找到 backend/ 下的 models
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

config = context.config

# Allow DATABASE_URL env var to override alembic.ini setting
_db_url = os.getenv("DATABASE_URL")
if _db_url:
    config.set_main_option("sqlalchemy.url", _db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 載入所有模型讓 Alembic 偵測到
from models.base import Base
from models.listing import Listing
from models.raw_post import RawPost
from models.geocode_cache import GeocodeCache

target_metadata = Base.metadata

# Only manage tables defined in our models (exclude PostGIS system tables)
_our_tables = {t.name for t in target_metadata.sorted_tables}


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table":
        return name in _our_tables
    return True


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
