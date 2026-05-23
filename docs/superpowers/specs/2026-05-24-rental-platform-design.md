# RentalHubTW — 設計文件

**日期：** 2026-05-24
**狀態：** 已確認，待實作

---

## 專案概述

台北租屋搜尋平台，資料來源為 Facebook 前 20 大租屋社團。
核心目標：改善現有參考平台（附近找房小幫手）的資料穩定性與篩選體驗。

**參考平台：** https://maps.nearyou.com.tw/

---

## 目標與範圍

**解決的問題：**
1. FB 社團爬蟲資料品質不穩（地址誤判、重複房源）
2. 現有平台篩選功能不直覺、難用
3. 資料來源單一且不穩定

**地理範圍：** 台北市、新北市、桃園市

**第一版範圍（MVP）：**
- FB 社團爬蟲（前 20 大台北/新北/桃園租屋社團）
- 規則式資料清洗管線（地址標準化、去重）
- 地圖為主的搜尋介面（Airbnb 風格）
- 左側可收合篩選面板
- 公開部署，開源

**不在範圍：**
- 591 或其他平台資料來源
- LLM 解析（後續版本可升級）
- 使用者帳號/收藏功能（後續版本）

---

## 技術選型

| 層級 | 技術 |
|------|------|
| 前端 | React + Mapbox GL JS |
| 後端 | Python / FastAPI |
| 資料庫 | PostgreSQL + PostGIS |
| 爬蟲 | Playwright |
| 排程 | Cron（Docker 內） |
| 部署 | Docker Compose + VPS（Hetzner/DigitalOcean）|
| CI | GitHub Actions |
| 反向代理 | Caddy（自動 HTTPS）|

---

## 整體架構

```
┌─────────────────────────────────────────────────────┐
│                     排程爬蟲層                        │
│  Playwright → FB 社團貼文 → 規則式解析器              │
│  (每日凌晨定時執行，random delay 避免被擋)            │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│                   資料清洗管線                         │
│  1. 規則式欄位解析（價格、地址、坪數、格局）           │
│  2. 地址標準化 → Geocoding API 轉座標                 │
│     (失敗打 geocode_failed flag，不顯示給用戶)        │
│  3. 去重：標題 + 電話 hash，Levenshtein 距離輔助      │
│  4. 欄位合理性驗證（價格/坪數範圍）                   │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│          PostgreSQL + PostGIS                         │
│  listings / raw_posts / geocode_cache                │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│          FastAPI 後端                                 │
│  GET /listings（地理範圍 + 篩選條件查詢）             │
│  GET /listings/:id                                    │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│          React 前端                                   │
│  Mapbox GL JS 地圖 + 左側可收合篩選面板               │
└─────────────────────────────────────────────────────┘
```

---

## 資料模型

### `listings`（對外展示的乾淨資料）
```sql
id              SERIAL PRIMARY KEY,
title           TEXT,
price           INTEGER,
price_type      VARCHAR(10),        -- 月租 / 季租
size_ping       NUMERIC(5,1),
room_type       VARCHAR(10),        -- 套房 / 雅房 / 整層
address         TEXT,
district        VARCHAR(20),
lat             NUMERIC(10,7),
lng             NUMERIC(10,7),
location        GEOGRAPHY(POINT),   -- PostGIS 地理欄位
pet_allowed     BOOLEAN,
parking         BOOLEAN,
balcony         BOOLEAN,
internet        BOOLEAN,
rental_subsidy  VARCHAR(10),        -- yes / no / unknown
water_billing   VARCHAR(20),        -- fixed / taiwan_water / unknown
electric_billing VARCHAR(20),       -- fixed / taiwan_power / unknown
has_elevator    BOOLEAN,
floor           SMALLINT,
total_floors    SMALLINT,
contact_name    TEXT,
contact_phone   TEXT,
contact_method  TEXT,
source_url      TEXT,
source_group    TEXT,
posted_at       TIMESTAMPTZ,
scraped_at      TIMESTAMPTZ,
updated_at      TIMESTAMPTZ,
status          VARCHAR(10) DEFAULT 'active'
```

### `raw_posts`（爬蟲原始資料，永久保留供除錯）
```sql
id                SERIAL PRIMARY KEY,
group_id          TEXT,
post_id           TEXT UNIQUE,
raw_text          TEXT,
scraped_at        TIMESTAMPTZ,
parsed_listing_id INTEGER REFERENCES listings(id),
parse_status      VARCHAR(20)   -- success / geocode_failed / duplicate / rejected
```

### `geocode_cache`（避免重複呼叫 API）
```sql
address_text  TEXT PRIMARY KEY,
lat           NUMERIC(10,7),
lng           NUMERIC(10,7),
confidence    NUMERIC(3,2),
source        VARCHAR(20),    -- google / ntpc_open_data
cached_at     TIMESTAMPTZ
```

**查詢設計：**
- `listings.location` 使用 PostGIS `ST_DWithin` 做地理範圍查詢
- 地址 Geocoding 優先使用國土測繪中心開放 API（免費），備用 Google Maps API

---

## 後端 OOP 結構

```
backend/
├── scraper/
│   ├── base_scraper.py          # BaseScraper (ABC)
│   ├── fb_group_scraper.py      # FBGroupScraper
│   └── scraper_config.py        # ScraperConfig（社團清單、delay 設定、FB cookie 管理）
│
├── parser/
│   ├── listing_parser.py        # ListingParser（協調子解析器）
│   ├── price_parser.py          # PriceParser
│   ├── address_parser.py        # AddressParser
│   └── field_validator.py       # FieldValidator
│
├── geocoder/
│   ├── geocoder_service.py      # GeocoderService
│   └── geocode_cache.py         # GeocodeCache
│
├── deduplication/
│   └── dedup_service.py         # DedupService（hash + Levenshtein）
│
├── repository/
│   ├── listing_repo.py          # ListingRepository
│   └── raw_post_repo.py         # RawPostRepository
│
├── pipeline/
│   └── ingestion_pipeline.py    # IngestionPipeline（串接所有步驟）
│
└── api/
    ├── routers/listings.py      # FastAPI router
    └── services/listing_svc.py  # ListingService
```

**去重策略（多因子評分）：**

| 比對維度 | 權重 |
|---------|------|
| 標準化地址（geocoding 後座標相近） | 高 |
| 樓層相同 | 中 |
| 坪數相近（±1坪） | 中 |
| 價格相近（±10%） | 中 |
| 聯絡電話相同 | 高（非必要條件） |

加總超過門檻值 → 標記 duplicate，保留資料較完整的那筆。
電話只是訊號之一，不同房仲接同一物件（電話不同但地址/樓層/坪數相同）亦可偵測。

**Pipeline 流程：**
```
IngestionPipeline.run()
  → FBGroupScraper.scrape_all()
  → ListingParser.parse(raw_text)
  → FieldValidator.validate(listing)
  → AddressParser → GeocoderService（失敗 → geocode_failed）
  → DedupService.check(listing)（多因子評分去重 → duplicate）
  → ListingRepository.upsert(listing)
```

---

## 前端 UI 設計

**整體佈局：**
- 頂部：導覽列（Logo + 搜尋欄）
- 左側：可收合篩選面板
- 右側：Mapbox GL JS 地圖（房源價格標記）

**篩選面板（左側，預設展開）：**
- 類型：套房 / 雅房 / 整層（Chip 多選）
- 租金範圍：快速標籤 + 自訂輸入
- 行政區：Chip 多選 + 展開更多
- 坪數：快速標籤
- 捷運距離：步行 5 / 10 分 / 不限
- 額外條件：可養寵物、含網路、有停車位、有陽台、有電梯（checkbox）
- 租補：有 / 無 / 不限（radio）
- 水電計費：台水台電計費 / 包水電 / 不限
- 樓層：自訂範圍輸入（如 3F–10F）
- 套用按鈕（顯示符合筆數）

**收合行為：**
- 收合後左側只留窄條 + 展開箭頭
- 若有篩選條件生效，地圖左上角顯示「篩選中 ×N」徽章
- 手機版：篩選面板改為底部 Sheet（responsive）

**地圖互動：**
- 房源以價格標記（price pin）顯示
- 縮小時自動 cluster
- 點擊標記開啟房源預覽卡片

---

## 錯誤處理

| 狀況 | 處理方式 |
|------|---------|
| Geocoding 失敗 | `parse_status = geocode_failed`，不顯示，可批次重試 |
| 解析失敗 | `parse_status = rejected`，保留 raw_post |
| FB 爬蟲被擋 | 記錄錯誤、跳過該社團、下次排程重試 |
| 重複房源 | `parse_status = duplicate`，指向已存在的 listing |
| 每次 pipeline 執行 | 寫入 run log（成功/失敗/跳過筆數） |

---

## 測試策略

- `PriceParser`、`AddressParser`、`FieldValidator`：pytest unit tests
- `GeocoderService`：mock 外部 API
- `DedupService`：樣本資料驗證
- `IngestionPipeline`：integration test 用本地 test DB

---

## 部署

```
GitHub Actions
  └─ pytest → build Docker image → push registry

生產環境
  ├─ VPS（Hetzner/DigitalOcean，~$5-10/月）
  │   └─ Docker Compose：FastAPI + PostgreSQL + Playwright
  ├─ Cron job：每日凌晨執行 IngestionPipeline
  └─ Caddy：反向代理 + 自動 HTTPS
```

---

## 法律聲明（README 需包含）

- 非商業用途，資料來源為公開 FB 社團
- 爬蟲加入 rate limiting，避免過度請求
- 標準開源免責聲明（MIT License）
- FB ToS 風險由使用者自行承擔
