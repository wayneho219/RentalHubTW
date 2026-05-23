# RentalHubTW — Plan 1: Foundation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立專案基礎架構——目錄結構、Docker PostgreSQL/PostGIS、SQLAlchemy 模型、Alembic migration、FastAPI 骨架。

**Architecture:** 使用 async SQLAlchemy 2.x 搭配 asyncpg 驅動；GeoAlchemy2 處理 PostGIS Geography 欄位；Alembic 管理 migration；FastAPI 提供 HTTP API。

**Tech Stack:** Python 3.12、FastAPI 0.115、SQLAlchemy 2.0 (async)、asyncpg、GeoAlchemy2、Alembic、PostgreSQL 16 + PostGIS 3.4、pytest、pytest-asyncio、Docker Compose

---

## 檔案結構

```
RentalHubTW/
├── backend/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py            # engine, SessionLocal, Base
│   │   ├── listing.py         # Listing ORM model
│   │   ├── raw_post.py        # RawPost ORM model
│   │   └── geocode_cache.py   # GeocodeCache ORM model
│   ├── repository/
│   │   ├── __init__.py
│   │   └── listing_repo.py    # ListingRepository
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py            # FastAPI app + health check
│   ├── tests/
│   │   ├── conftest.py        # test DB session fixture
│   │   ├── test_models.py     # model creation smoke tests
│   │   └── test_listing_repo.py
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   │       └── 001_initial_schema.py
│   ├── alembic.ini
│   ├── requirements.txt
│   └── .env.example
├── docker-compose.yml
└── .gitignore
```

---

## Task 1：專案骨架與 Python 環境

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/.env.example`
- Create: `docker-compose.yml`
- Create: `.gitignore`

- [ ] **Step 1：建立目錄結構**

```bash
cd /home/wayne/RentalHubTW
mkdir -p backend/{models,repository,api,tests,alembic/versions}
touch backend/{models,repository,api,tests}/__init__.py
```

- [ ] **Step 2：建立 requirements.txt**

```
# backend/requirements.txt
fastapi==0.115.5
uvicorn[standard]==0.32.1
sqlalchemy[asyncio]==2.0.36
asyncpg==0.30.0
geoalchemy2==0.15.2
alembic==1.14.0
python-dotenv==1.0.1
pytest==8.3.4
pytest-asyncio==0.24.0
httpx==0.28.1
aiosqlite==0.20.0
```

- [ ] **Step 3：建立 .env.example**

```
# backend/.env.example
DATABASE_URL=postgresql+asyncpg://rentalhub:rentalhub@localhost:5432/rentalhub
TEST_DATABASE_URL=postgresql+asyncpg://rentalhub:rentalhub@localhost:5432/rentalhub_test
```

- [ ] **Step 4：建立 docker-compose.yml**

```yaml
# docker-compose.yml
services:
  db:
    image: postgis/postgis:16-3.4
    environment:
      POSTGRES_DB: rentalhub
      POSTGRES_USER: rentalhub
      POSTGRES_PASSWORD: rentalhub
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U rentalhub"]
      interval: 5s
      timeout: 5s
      retries: 5

  db_test:
    image: postgis/postgis:16-3.4
    environment:
      POSTGRES_DB: rentalhub_test
      POSTGRES_USER: rentalhub
      POSTGRES_PASSWORD: rentalhub
    ports:
      - "5433:5432"
    volumes:
      - postgres_test_data:/var/lib/postgresql/data

volumes:
  postgres_data:
  postgres_test_data:
```

- [ ] **Step 5：建立 .gitignore**

```
# .gitignore
__pycache__/
*.pyc
.env
.venv/
venv/
*.egg-info/
.pytest_cache/
node_modules/
dist/
.DS_Store
```

- [ ] **Step 6：建立虛擬環境並安裝依賴**

```bash
cd /home/wayne/RentalHubTW/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Expected: 所有套件安裝成功，無 error。

- [ ] **Step 7：啟動 Docker 資料庫**

```bash
cd /home/wayne/RentalHubTW
docker compose up -d db db_test
docker compose ps
```

Expected: db 和 db_test 狀態為 `running (healthy)`。

- [ ] **Step 8：Commit**

```bash
cd /home/wayne/RentalHubTW
git add .gitignore docker-compose.yml backend/requirements.txt backend/.env.example
git commit -m "chore: project scaffolding and docker compose setup"
```

---

## Task 2：SQLAlchemy Base 設定

**Files:**
- Create: `backend/models/base.py`

- [ ] **Step 1：建立 base.py**

```python
# backend/models/base.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://rentalhub:rentalhub@localhost:5432/rentalhub"
)

engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
```

- [ ] **Step 2：寫 smoke test 確認 engine 可建立**

```python
# backend/tests/test_models.py
import pytest
from sqlalchemy.ext.asyncio import AsyncEngine
from models.base import engine

def test_engine_is_created():
    assert isinstance(engine, AsyncEngine)
```

- [ ] **Step 3：設定 pytest（pytest.ini）**

```ini
# backend/pytest.ini
[pytest]
asyncio_mode = auto
testpaths = tests
pythonpath = .
```

- [ ] **Step 4：執行測試確認通過**

```bash
cd /home/wayne/RentalHubTW/backend
source .venv/bin/activate
pytest tests/test_models.py::test_engine_is_created -v
```

Expected: `PASSED`

- [ ] **Step 5：Commit**

```bash
git add backend/models/base.py backend/pytest.ini
git commit -m "feat: sqlalchemy async engine and session factory"
```

---

## Task 3：Listing 模型

**Files:**
- Create: `backend/models/listing.py`
- Modify: `backend/models/__init__.py`

- [ ] **Step 1：建立 Listing 模型**

```python
# backend/models/listing.py
from datetime import datetime
from sqlalchemy import String, Integer, Numeric, Boolean, DateTime, SmallInteger, Text
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geography
from .base import Base


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str | None] = mapped_column(Text)
    price: Mapped[int | None] = mapped_column(Integer)
    price_type: Mapped[str | None] = mapped_column(String(10))       # 月租 / 季租
    size_ping: Mapped[float | None] = mapped_column(Numeric(5, 1))
    room_type: Mapped[str | None] = mapped_column(String(10))        # 套房 / 雅房 / 整層
    address: Mapped[str | None] = mapped_column(Text)
    district: Mapped[str | None] = mapped_column(String(20))
    lat: Mapped[float | None] = mapped_column(Numeric(10, 7))
    lng: Mapped[float | None] = mapped_column(Numeric(10, 7))
    location: Mapped[object | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326), nullable=True
    )
    pet_allowed: Mapped[bool | None] = mapped_column(Boolean)
    parking: Mapped[bool | None] = mapped_column(Boolean)
    balcony: Mapped[bool | None] = mapped_column(Boolean)
    internet: Mapped[bool | None] = mapped_column(Boolean)
    has_elevator: Mapped[bool | None] = mapped_column(Boolean)
    floor: Mapped[int | None] = mapped_column(SmallInteger)
    total_floors: Mapped[int | None] = mapped_column(SmallInteger)
    rental_subsidy: Mapped[str | None] = mapped_column(String(10))   # yes / no / unknown
    water_billing: Mapped[str | None] = mapped_column(String(20))    # fixed / taiwan_water / unknown
    electric_billing: Mapped[str | None] = mapped_column(String(20)) # fixed / taiwan_power / unknown
    contact_name: Mapped[str | None] = mapped_column(Text)
    contact_phone: Mapped[str | None] = mapped_column(Text)
    contact_method: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(Text)
    source_group: Mapped[str | None] = mapped_column(Text)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    scraped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(10), default="active")
```

- [ ] **Step 2：更新 models/__init__.py（只先 export Listing）**

```python
# backend/models/__init__.py
from .base import Base, engine, SessionLocal
from .listing import Listing

__all__ = ["Base", "engine", "SessionLocal", "Listing"]
```

- [ ] **Step 3：新增 Listing 模型 smoke test**

```python
# 在 backend/tests/test_models.py 補充：
from models.listing import Listing

def test_listing_tablename():
    assert Listing.__tablename__ == "listings"

def test_listing_has_location_column():
    assert hasattr(Listing, "location")

def test_listing_has_required_billing_columns():
    assert hasattr(Listing, "water_billing")
    assert hasattr(Listing, "electric_billing")
    assert hasattr(Listing, "rental_subsidy")
```

- [ ] **Step 4：執行測試確認通過**

```bash
cd /home/wayne/RentalHubTW/backend
source .venv/bin/activate
pytest tests/test_models.py -v
```

Expected: `test_engine_is_created`、`test_listing_tablename`、`test_listing_has_location_column`、`test_listing_has_required_billing_columns` 全部 `PASSED`

- [ ] **Step 5：Commit**

```bash
git add backend/models/listing.py backend/models/__init__.py backend/tests/test_models.py
git commit -m "feat: Listing ORM model with all rental fields"
```

---

## Task 4：RawPost 與 GeocodeCache 模型

**Files:**
- Create: `backend/models/raw_post.py`
- Create: `backend/models/geocode_cache.py`

- [ ] **Step 1：建立 RawPost 模型**

```python
# backend/models/raw_post.py
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class RawPost(Base):
    __tablename__ = "raw_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[str | None] = mapped_column(Text)
    post_id: Mapped[str | None] = mapped_column(Text, unique=True)
    raw_text: Mapped[str | None] = mapped_column(Text)
    scraped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    parsed_listing_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("listings.id"), nullable=True
    )
    parse_status: Mapped[str | None] = mapped_column(String(20))
    # parse_status 可能的值:
    # success / geocode_failed / duplicate / rejected
```

- [ ] **Step 2：建立 GeocodeCache 模型**

```python
# backend/models/geocode_cache.py
from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class GeocodeCache(Base):
    __tablename__ = "geocode_cache"

    address_text: Mapped[str] = mapped_column(Text, primary_key=True)
    lat: Mapped[float | None] = mapped_column(Numeric(10, 7))
    lng: Mapped[float | None] = mapped_column(Numeric(10, 7))
    confidence: Mapped[float | None] = mapped_column(Numeric(3, 2))
    source: Mapped[str | None] = mapped_column(String(20))  # google / ntpc_open_data
    cached_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
```

- [ ] **Step 3：更新 models/__init__.py 加入 RawPost 和 GeocodeCache**

```python
# backend/models/__init__.py
from .base import Base, engine, SessionLocal
from .listing import Listing
from .raw_post import RawPost
from .geocode_cache import GeocodeCache

__all__ = ["Base", "engine", "SessionLocal", "Listing", "RawPost", "GeocodeCache"]
```

- [ ] **Step 4：補充 models smoke tests**

```python
# 在 backend/tests/test_models.py 補充：
from models.raw_post import RawPost
from models.geocode_cache import GeocodeCache

def test_raw_post_tablename():
    assert RawPost.__tablename__ == "raw_posts"

def test_raw_post_has_parse_status():
    assert hasattr(RawPost, "parse_status")

def test_geocode_cache_tablename():
    assert GeocodeCache.__tablename__ == "geocode_cache"
```

- [ ] **Step 5：執行所有 model tests**

```bash
cd /home/wayne/RentalHubTW/backend
source .venv/bin/activate
pytest tests/test_models.py -v
```

Expected: 所有 `PASSED`

- [ ] **Step 6：Commit**

```bash
git add backend/models/raw_post.py backend/models/geocode_cache.py backend/models/__init__.py backend/tests/test_models.py
git commit -m "feat: RawPost and GeocodeCache ORM models"
```

---

## Task 5：Alembic Migration

**Files:**
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/versions/001_initial_schema.py`

- [ ] **Step 1：初始化 Alembic**

```bash
cd /home/wayne/RentalHubTW/backend
source .venv/bin/activate
alembic init alembic
```

Expected: `alembic/` 目錄建立，`alembic.ini` 出現。

- [ ] **Step 2：修改 alembic.ini 設定 sqlalchemy.url**

在 `backend/alembic.ini` 找到這行：
```
sqlalchemy.url = driver://user:pass@localhost/dbname
```
改為：
```
sqlalchemy.url = postgresql+asyncpg://rentalhub:rentalhub@localhost:5432/rentalhub
```

- [ ] **Step 3：修改 alembic/env.py 載入模型**

```python
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
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 載入所有模型讓 Alembic 偵測到
from models.base import Base
from models.listing import Listing
from models.raw_post import RawPost
from models.geocode_cache import GeocodeCache

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


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
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
```

- [ ] **Step 4：自動生成 initial migration**

```bash
cd /home/wayne/RentalHubTW/backend
source .venv/bin/activate
alembic revision --autogenerate -m "initial schema"
```

Expected: `alembic/versions/xxxx_initial_schema.py` 生成，內含 listings / raw_posts / geocode_cache 三張表的 `op.create_table()`。

確認生成的 migration 檔案中有 PostGIS `GEOGRAPHY` 欄位（location 欄位）。

- [ ] **Step 5：執行 migration**

```bash
alembic upgrade head
```

Expected:
```
INFO  [alembic.runtime.migration] Running upgrade  -> xxxx, initial schema
```

- [ ] **Step 6：驗證資料表已建立**

```bash
docker compose exec db psql -U rentalhub -d rentalhub -c "\dt"
```

Expected: 看到 `listings`、`raw_posts`、`geocode_cache` 三張表。

- [ ] **Step 7：Commit**

```bash
git add backend/alembic.ini backend/alembic/
git commit -m "feat: alembic migrations for initial schema"
```

---

## Task 6：測試用 DB Fixture

**Files:**
- Create: `backend/tests/conftest.py`

- [ ] **Step 1：建立 conftest.py**

```python
# backend/tests/conftest.py
import os
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from models.base import Base
from models.listing import Listing
from models.raw_post import RawPost
from models.geocode_cache import GeocodeCache

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://rentalhub:rentalhub@localhost:5433/rentalhub_test"
)

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


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


@pytest_asyncio.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()
```

- [ ] **Step 2：確認 test DB 也有 PostGIS extension**

```bash
docker compose exec db_test psql -U rentalhub -d rentalhub_test -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

Expected: `CREATE EXTENSION` 或 `NOTICE: extension already exists`

- [ ] **Step 3：執行測試確認 fixture 可正常連線**

```bash
cd /home/wayne/RentalHubTW/backend
source .venv/bin/activate
pytest tests/test_models.py -v
```

Expected: 所有 `PASSED`

- [ ] **Step 4：Commit**

```bash
git add backend/tests/conftest.py
git commit -m "test: async test DB fixture with PostGIS"
```

---

## Task 7：ListingRepository

**Files:**
- Create: `backend/repository/listing_repo.py`
- Create: `backend/tests/test_listing_repo.py`

- [ ] **Step 1：寫失敗測試**

```python
# backend/tests/test_listing_repo.py
import pytest
from datetime import datetime, timezone
from repository.listing_repo import ListingRepository
from models.listing import Listing


@pytest.mark.asyncio
async def test_create_listing(db_session):
    repo = ListingRepository(db_session)
    listing = await repo.create(
        title="大安區套房近捷運",
        price=18000,
        price_type="月租",
        room_type="套房",
        address="台北市大安區復興南路一段",
        district="大安區",
        status="active",
    )
    assert listing.id is not None
    assert listing.title == "大安區套房近捷運"
    assert listing.price == 18000


@pytest.mark.asyncio
async def test_get_listing_by_id(db_session):
    repo = ListingRepository(db_session)
    created = await repo.create(title="測試房源", price=15000, status="active")
    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id


@pytest.mark.asyncio
async def test_get_listing_by_id_not_found(db_session):
    repo = ListingRepository(db_session)
    result = await repo.get_by_id(99999)
    assert result is None
```

- [ ] **Step 2：執行確認測試失敗**

```bash
pytest tests/test_listing_repo.py -v
```

Expected: `ImportError` 或 `ModuleNotFoundError`（ListingRepository 尚未建立）

- [ ] **Step 3：實作 ListingRepository**

```python
# backend/repository/listing_repo.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.listing import Listing


class ListingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs) -> Listing:
        listing = Listing(**kwargs)
        self.session.add(listing)
        await self.session.commit()
        await self.session.refresh(listing)
        return listing

    async def get_by_id(self, listing_id: int) -> Listing | None:
        result = await self.session.execute(
            select(Listing).where(Listing.id == listing_id)
        )
        return result.scalar_one_or_none()

    async def upsert_by_source(self, post_id: str, **kwargs) -> tuple[Listing, bool]:
        """依 source_url 找已有房源，有則更新，無則新增。回傳 (listing, created)。"""
        result = await self.session.execute(
            select(Listing).where(Listing.source_url == kwargs.get("source_url"))
        )
        existing = result.scalar_one_or_none()
        if existing:
            for key, value in kwargs.items():
                setattr(existing, key, value)
            await self.session.commit()
            await self.session.refresh(existing)
            return existing, False
        return await self.create(**kwargs), True
```

- [ ] **Step 4：執行確認測試通過**

```bash
pytest tests/test_listing_repo.py -v
```

Expected: 3 個 `PASSED`

- [ ] **Step 5：Commit**

```bash
git add backend/repository/listing_repo.py backend/tests/test_listing_repo.py
git commit -m "feat: ListingRepository with create, get_by_id, upsert_by_source"
```

---

## Task 8：FastAPI 骨架 + Health Check

**Files:**
- Create: `backend/api/main.py`
- Create: `backend/tests/test_api.py`

- [ ] **Step 1：寫失敗測試**

```python
# backend/tests/test_api.py
import pytest
from httpx import AsyncClient, ASGITransport
from api.main import app


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 2：執行確認失敗**

```bash
pytest tests/test_api.py -v
```

Expected: `ImportError`（api/main.py 尚未建立）

- [ ] **Step 3：實作 FastAPI app**

```python
# backend/api/main.py
from fastapi import FastAPI

app = FastAPI(title="RentalHubTW API", version="0.1.0")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

- [ ] **Step 4：執行確認通過**

```bash
pytest tests/test_api.py -v
```

Expected: `PASSED`

- [ ] **Step 5：手動啟動確認**

```bash
cd /home/wayne/RentalHubTW/backend
source .venv/bin/activate
uvicorn api.main:app --reload --port 8000
```

開啟瀏覽器確認 `http://localhost:8000/health` 回傳 `{"status":"ok"}`，  
並確認 `http://localhost:8000/docs` 顯示 Swagger UI。

- [ ] **Step 6：Commit**

```bash
git add backend/api/main.py backend/tests/test_api.py
git commit -m "feat: FastAPI app skeleton with health check endpoint"
```

---

## Task 9：全套測試 + Push

- [ ] **Step 1：執行所有測試**

```bash
cd /home/wayne/RentalHubTW/backend
source .venv/bin/activate
pytest tests/ -v
```

Expected: 全部 `PASSED`，沒有 warning 需要修正。

- [ ] **Step 2：Push 到 GitHub**

```bash
cd /home/wayne/RentalHubTW
git push origin main
```

---

## 完成標準

- [ ] `docker compose up -d` 可正常啟動 PostgreSQL + PostGIS
- [ ] `alembic upgrade head` 建出三張表
- [ ] `pytest tests/ -v` 全部通過
- [ ] `GET /health` 回傳 `{"status": "ok"}`
- [ ] `GET /docs` 顯示 Swagger UI
