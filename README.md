# RentalHubTW 🏠

台北、新北、桃園租屋地圖搜尋平台。整合 Facebook 前 20 大租屋社團的房源資訊，提供地圖式搜尋介面與直覺的篩選功能。

---

## 功能特色

- **地圖為主的搜尋介面** — 房源以價格標記顯示於地圖，可縮放瀏覽
- **完整篩選條件** — 類型、租金、行政區、坪數、捷運距離、電梯、水電計費方式、租補、寵物、停車等
- **資料清洗管線** — 規則式解析 + 地址標準化 + 多因子去重（解決同一物件被不同房仲重複刊登的問題）
- **涵蓋範圍** — 台北市、新北市、桃園市

---

## Tech Stack

| 層級 | 技術 |
|------|------|
| 前端 | React + Mapbox GL JS |
| 後端 | Python 3.12 / FastAPI |
| 資料庫 | PostgreSQL 16 + PostGIS 3.4 |
| 爬蟲 | Playwright |
| ORM | SQLAlchemy 2.0 (async) + GeoAlchemy2 |
| Migration | Alembic |
| 部署 | Docker Compose + VPS |

---

## 快速開始

### 1. Clone 專案

```bash
git clone git@github.com:wayneho219/RentalHubTW.git
cd RentalHubTW
```

### 2. 安裝 PostgreSQL + PostGIS（Ubuntu / WSL）

```bash
sudo apt-get install -y postgresql postgresql-contrib postgresql-16-postgis-3
sudo service postgresql start

# 建立使用者與資料庫
sudo -u postgres psql -c "CREATE USER rentalhub WITH PASSWORD 'rentalhub';"
sudo -u postgres psql -c "CREATE DATABASE rentalhub OWNER rentalhub;"
sudo -u postgres psql -c "CREATE DATABASE rentalhub_test OWNER rentalhub;"

# 啟用 PostGIS
sudo -u postgres psql -d rentalhub -c "CREATE EXTENSION IF NOT EXISTS postgis;"
sudo -u postgres psql -d rentalhub_test -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

### 3. 建立 Python 虛擬環境

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. 設定環境變數

```bash
cp .env.example .env
# 根據需要修改 .env 內容
```

### 5. 執行 Migration

```bash
cd backend
source .venv/bin/activate
alembic upgrade head
```

### 6. 啟動後端

```bash
uvicorn api.main:app --reload --port 8000
```

API 文件：http://localhost:8000/docs

---

## 專案結構

```
RentalHubTW/
├── backend/
│   ├── models/          # SQLAlchemy ORM 模型
│   ├── repository/      # 資料庫存取層
│   ├── scraper/         # FB 社團爬蟲
│   ├── parser/          # 房源資料解析
│   ├── geocoder/        # 地址轉座標
│   ├── deduplication/   # 去重邏輯
│   ├── pipeline/        # 資料整合管線
│   ├── api/             # FastAPI 路由
│   ├── tests/           # 測試
│   └── alembic/         # 資料庫 migration
├── frontend/            # React 前端（開發中）
└── docs/
    └── superpowers/
        ├── specs/       # 設計文件
        └── plans/       # 實作計畫
```

---

## 開發

### 執行測試

```bash
cd backend
source .venv/bin/activate
pytest tests/ -v
```

### 分支規範

- `main` — 穩定版本，只透過 PR 合併
- `Wayne_OuOb`、`Wayne_<機器名>` — 開發分支，完成後開 PR

---

## 設計文件

- [平台設計規格](docs/superpowers/specs/2026-05-24-rental-platform-design.md)
- [Plan 1：Foundation 實作計畫](docs/superpowers/plans/2026-05-24-plan-1-foundation.md)

---

## 免責聲明

- 本專案為非商業用途開源專案
- 資料來源為公開 Facebook 租屋社團
- 爬蟲設有 rate limiting，避免過度請求
- 使用本專案須自行承擔相關法律風險（Facebook ToS）

---

## License

MIT
