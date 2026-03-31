---
name: tra-cuu-phan-bon
description: >
  Full-stack development skill for "Tra cứu Phân Bón" (Fertilizer Lookup) —
  a Vietnamese fertilizer registry search system with ~100k records from the real
  Ministry of Agriculture CSV. Use this skill for ANY task on this project:
  modifying load_data.py or the column map, updating FastAPI endpoints (main.py),
  changing the card-based search UI (index.html), adjusting filters (loai_phan, nutrient ranges), fixing Vietnamese FTS search, or deploying to
  Render.com. Trigger on: phân bón, tra cứu, fertilizer lookup, load_data.py,
  main.py search endpoint, index.html card UI, loai_phan filter, dam/lan/kali range,
  Render deploy, or the repo name "tra-cuu-phan-bon".
---

# Tra cứu Phân Bón — Development Skill

Vietnamese fertilizer product registry lookup. ~100k records from the Ministry of Agriculture. FastAPI + SQLite FTS5 backend, single-file card-based HTML frontend, deployed free on Render.com.

## Project Overview

| Layer | Technology | Notes |
|---|---|---|
| Data import | Python + pandas | CSV → SQLite, run once |
| Database | SQLite with FTS5 | `unicode61` tokenizer for Vietnamese |
| Backend | FastAPI + uvicorn | `/search`, `/columns`, `/filters`, `/health` |
| Frontend | Single HTML file | Card UI, vanilla JS, no build step |
| Deploy | Render.com free tier | Backend = Web Service, Frontend = Static Site |

## Repo Structure

```
tra-cuu-phan-bon/
├── backend/
│   ├── main.py              # FastAPI app — all endpoints
│   ├── load_data.py         # CSV → SQLite importer (run once at deploy)
│   ├── requirements.txt
│   └── database.db          # ⚠️ gitignored — generated at build time
├── frontend/
│   └── index.html           # Card-based search UI (single self-contained file)
├── data/
│   └── phan_bon.csv         # Source CSV — ⚠️ gitignored (commit or fetch at build)
├── .gitignore
├── render.yaml
└── README.md
```

## Core Architecture Rules

1. **Never query Google Sheets directly** — always use the local SQLite DB
2. **Always paginate** — PAGE_SIZE = 20, never return all rows
3. **FTS5 with `unicode61`** for Vietnamese text search across 4 columns
4. **Indexed columns only** for filter dropdowns — never enumerate high-cardinality fields
5. **CORS open** (`allow_origins=["*"]`) — static frontend lives on a different domain
6. **`/columns` returns labels** — frontend uses Vietnamese display names from the API, never hardcoded

---

## Actual Database Schema (37 columns)

The CSV's `Lưu hành` compound field is **parsed into 5 separate columns** at import time.
Columns with 0% fill rate (NAA, Tổng axit humic & fulvic, Chitosan, VSV phân giải lân/xenlulo) are kept in DB but excluded from filters and FTS.

### Identity & Registration

| DB column | Vietnamese label | Fill % | Notes |
|---|---|---|---|
| `mspb` | MSPB | 100% | Ministry registration number (int) |
| `ten_san_pham` | Tên sản phẩm | ~29% | Parsed from `Lưu hành` line 1 |
| `ma_so_phan_bon` | Mã số phân bón | ~29% | Parsed from `Lưu hành` line 2 |
| `so_quyet_dinh` | Số quyết định | ~29% | Parsed from `Lưu hành` line 3 |
| `ngay_cap` | Ngày cấp | ~29% | Parsed from `Lưu hành` line 4 (before `->`) |
| `ngay_het_han` | Ngày hết hạn | ~29% | Parsed from `Lưu hành` line 4 (after `->`) |
| `loai_phan` | Loại phân | ~29% | Categorical — 954 unique types → **dropdown filter** |
| `thanh_phan` | Thành phần | ~28% | Raw composition text → **FTS indexed** |

### Macro Nutrients (% by weight)

| DB column | Label | Fill % |
|---|---|---|
| `dam_tong_so_pct` | Đạm tổng số | 6.6% |
| `lan_huu_hieu_pct` | Lân hữu hiệu | 6.0% |
| `kali_huu_hieu_pct` | Kali hữu hiệu | 6.2% |
| `canxi_pct` | Canxi | 0.8% |
| `magie_pct` | Magie | 0.9% |
| `luu_huynh_pct` | Lưu huỳnh | 1.5% |
| `silic_huu_hieu_pct` | Silic hữu hiệu | 0.3% |

### Micro Nutrients (ppm unless noted)

| DB column | Label | Fill % |
|---|---|---|
| `dong_ppm` | Đồng (Cu) | 1.8% |
| `sat_ppm` | Sắt (Fe) | 1.9% |
| `kem_ppm` | Kẽm (Zn) | 3.0% |
| `bo_ppm` | Bo (B) | 3.1% |
| `mangan_ppm` | Mangan (Mn) | 1.5% |
| `ga3` | GA3 | 0.1% |

### Organic & Biological

| DB column | Label | Fill % |
|---|---|---|
| `chat_huu_co_pct` | Chất hữu cơ | 0.9% |
| `axit_humic_pct` | Axit humic | 0.2% |
| `axit_fulvic_pct` | Axit fulvic | ~0% |
| `axit_amin` | Axit amin | 0.1% |
| `vsv_co_dinh_dam` | VSV cố định đạm | 0.1% |
| `trichoderma` | Trichoderma | 0.1% |

### Physical Properties

| DB column | Label | Fill % |
|---|---|---|
| `ph_h2o` | pH H₂O | 2.0% |
| `ty_le_cn` | Tỷ lệ C/N | 0.2% |
| `do_am_pct` | Độ ẩm | 1.7% |
| `ty_trong` | Tỷ trọng | 0.3% |

---

## Filter Strategy (Best Practice)

| Filter | UI control | Backend param | Rationale |
|---|---|---|---|
| Loại phân | `<select>` dropdown | `loai_phan` (exact match) | 954 uniques, categorical, indexed |
| Còn/Hết lưu hành | `<select>` dropdown | Only 1 value |
| Đạm tổng số | min/max number inputs | `dam_min`, `dam_max` | Most-searched nutrient |
| Lân hữu hiệu | min/max number inputs | `lan_min`, `lan_max` | Core NPK |
| Kali hữu hiệu | min/max number inputs | `kali_min`, `kali_max` | Core NPK |
| Full text | search input (debounced 320ms) | `q` via FTS5 MATCH | Covers name, type, composition, mã số |

**Never add** dropdowns for `loai_phan` subtypes or numeric columns — too high cardinality or too sparse.

## FTS5 Indexed Columns (4 columns, unicode61)

```sql
CREATE VIRTUAL TABLE records_fts USING fts5(
  ten_san_pham, loai_phan, thanh_phan, ma_so_phan_bon,
  tokenize='unicode61', content='records', content_rowid='rowid'
)
```

## Card UI Layout

Each search result renders as a card (not a table row). Card sections:
1. **Header** — MSPB badge · product name · status badge (YES=green/NO=red) · loại phân tag
2. **Registration row** — mã số phân bón · số quyết định
3. **Nutrient chips** — only non-null values: N, P₂O₅, K₂O, Ca, Mg, S, Cu, Fe, Zn, B, Mn, Hữu cơ, Humic, pH
4. **Composition** — collapsible `thanh_phan` text (max-height 80px, expand toggle)
5. **Validity dates** — ngày cấp → ngày hết hạn

CSS design tokens: green theme (`--green: #2d7a3a`), `Be Vietnam Pro` font, `JetBrains Mono` for codes/numbers.

---

## Step-by-Step Workflows

### A. Data Setup (first time or re-import)

Read → `references/data-setup.md` for the complete `load_data.py` with the real COLUMN_MAP.

```bash
cp new_export.csv data/phan_bon.csv
rm backend/database.db        # force full rebuild
cd backend && python load_data.py
sqlite3 database.db "SELECT COUNT(*) FROM records;"   # verify
```

### B. Backend Changes

Read → `references/backend.md` for full `main.py`, endpoint patterns, and how to add filters.

### C. Frontend Changes

Read → `references/frontend.md` for CSS tokens, card builder function, filter wiring, and API contract.

### D. Deploy

Read → `references/deployment.md` for `render.yaml`, CSV strategy, and cold-start workaround.

---

## Common Tasks Quick Reference

| Task | Reference |
|---|---|
| Re-import updated CSV | `data-setup.md` → Re-import |
| Add a new filter param | `backend.md` → Adding a Filter |
| Change which nutrients show as chips | `frontend.md` → NUTRIENTS array |
| Change card layout | `frontend.md` → buildCard() |
| Fix slow Vietnamese search | `backend.md` → Performance / FTS |
| Update deploy config | `deployment.md` |
| Add a new API endpoint | `backend.md` → Endpoint Patterns |

## Critical Files — Never Delete

- `backend/main.py` — entire API
- `backend/load_data.py` — entire COLUMN_MAP and DB build logic
- `frontend/index.html` — entire UI
- `render.yaml` — deploy config