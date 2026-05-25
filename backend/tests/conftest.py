import os
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from models.base import Base
from models.listing import Listing  # noqa: F401 — registers with Base.metadata
from models.raw_post import RawPost  # noqa: F401 — registers with Base.metadata
from models.geocode_cache import GeocodeCache  # noqa: F401 — registers with Base.metadata

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://rentalhub:rentalhub@localhost:5433/rentalhub_test"
)

# Use NullPool to avoid connection pool issues with asyncpg
test_engine = create_async_engine(
    TEST_DATABASE_URL, echo=False, poolclass=NullPool
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    async with test_engine.begin() as conn:
        # PostGIS extension 必須在建表前啟用
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture
async def db_session():
    SessionLocal = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )
    async with SessionLocal() as session:
        yield session
        await session.rollback()
