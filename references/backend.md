# Backend Reference — FastAPI (main.py)

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/columns` | Column list + Vietnamese labels dict |
| GET | `/filters` | Unique values for dropdown filters |
| GET | `/search` | Paginated FTS + filter search |
| GET | `/health` | Record count health check |

## `/columns` response shape

```json
{
  "columns": ["mspb", "ten_san_pham", "loai_phan", ...],
  "labels": {
    "mspb": "MSPB",
    "ten_san_pham": "Tên sản phẩm",
    "loai_phan": "Loại phân",
    ...
  }
}
```

Full labels dict lives in `main.py` — update there if adding/renaming columns.

## `/filters` response shape

```json
{
  "loai_phan": ["Phân bón hỗn hợp NPK", "Phân bón hữu cơ", ...]
}
```

Only `loai_phan` is enumerated here. Do NOT add high-cardinality or numeric columns.

## `/search` query params

| Param | Type | Default | Notes |
|---|---|---|---|
| `q` | string | `""` | FTS5 MATCH query, prefix search auto-appended |
| `page` | int ≥ 1 | `1` | Pagination |
| `loai_phan` | string | None | Exact match on `loai_phan` |
| `dam_min` | float | None | Đạm tổng số ≥ |
| `dam_max` | float | None | Đạm tổng số ≤ |
| `lan_min` | float | None | Lân hữu hiệu ≥ |
| `lan_max` | float | None | Lân hữu hiệu ≤ |
| `kali_min` | float | None | Kali hữu hiệu ≥ |
| `kali_max` | float | None | Kali hữu hiệu ≤ |

## `/search` response shape

```json
{
  "total": 4821,
  "pages": 242,
  "page": 1,
  "data": [{ "mspb": "26324", "ten_san_pham": "ĐÁP MỸ 911", ... }]
}
```

## Adding a New Filter

1. **Add index** in `load_data.py` INDEX_COLS list and re-run
2. **Add to `/filters`** FILTER_COLS if it's categorical and low-cardinality
3. **Add Query param** to `/search` with `Optional[str] = Query(default=None)`
4. **Add WHERE clause**: `base += " AND col = ?"; params.append(val)`
5. **Add `<select>`** in `frontend/index.html` filter bar, wire to `applyFilters()`

## Performance Notes

- Numeric range filters use `CAST(col AS REAL)` — columns stored as TEXT due to mixed types in source CSV
- FTS5 prefix search: always append `"*"` to query → `q.strip() + "*"`
- EXPLAIN QUERY PLAN to debug: `sqlite3 database.db "EXPLAIN QUERY PLAN SELECT ..."`
- PAGE_SIZE = 20 — keep low for card UI (cards are taller than table rows)

## Endpoint Pattern (adding a new one)

```python
@app.get("/stats")
def stats():
    """Example: aggregate stats endpoint."""
    con = get_db()
    result = con.execute("""
        SELECT loai_phan, COUNT(*) as count
        FROM records WHERE loai_phan IS NOT NULL
        GROUP BY loai_phan ORDER BY count DESC LIMIT 20
    """).fetchall()
    con.close()
    return {"data": [dict(r) for r in result]}
```