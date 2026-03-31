"""
main.py — Tra cứu Phân Bón API
FastAPI backend: /search, /columns, /filters, /health
"""
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3, math, os
from typing import Optional

app = FastAPI(title="Tra cứu Phân Bón", version="1.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

DB        = os.path.join(os.path.dirname(__file__), "database.db")
PAGE_SIZE = 20

def get_db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

# ── /columns ──────────────────────────────────────────────────────────────────
@app.get("/columns")
def columns():
    """Column names + Vietnamese display labels for the frontend."""
    LABELS = {
        "mspb":                       "MSPB",
        "ten_san_pham":               "Tên sản phẩm",
        "loai_phan":                  "Loại phân",
        "ma_so_phan_bon":             "Mã số phân bón",
        "so_quyet_dinh":              "Số quyết định",
        "ngay_cap":                   "Ngày cấp",
        "ngay_het_han":               "Ngày hết hạn",
        "thanh_phan":                 "Thành phần",
        "ghi_chu":                    "Ghi chú",
        "dam_tong_so_pct":            "Đạm tổng số (%)",
        "lan_huu_hieu_pct":           "Lân hữu hiệu (%)",
        "kali_huu_hieu_pct":          "Kali hữu hiệu (%)",
        "canxi_pct":                  "Canxi (%)",
        "magie_pct":                  "Magie (%)",
        "luu_huynh_pct":              "Lưu huỳnh (%)",
        "silic_huu_hieu_pct":         "Silic hữu hiệu (%)",
        "dong_ppm":                   "Đồng (ppm)",
        "sat_ppm":                    "Sắt (ppm)",
        "kem_ppm":                    "Kẽm (ppm)",
        "bo_ppm":                     "Bo (ppm)",
        "mangan_ppm":                 "Mangan (ppm)",
        "ga3":                        "GA3",
        "naa":                        "NAA",
        "chat_huu_co_pct":            "Chất hữu cơ (%)",
        "axit_humic_pct":             "Axit humic (%)",
        "axit_fulvic_pct":            "Axit fulvic (%)",
        "tong_axit_humic_fulvic_pct": "Tổng axit humic & fulvic (%)",
        "axit_amin":                  "Axit amin",
        "chitosan":                   "Chitosan",
        "vsv_co_dinh_dam":            "VSV cố định đạm",
        "vsv_phan_giai_lan":          "VSV phân giải lân",
        "vsv_phan_giai_xenlulo":      "VSV phân giải xenlulo",
        "trichoderma":                "Trichoderma",
        "ph_h2o":                     "pH H₂O",
        "ty_le_cn":                   "Tỷ lệ C/N",
        "do_am_pct":                  "Độ ẩm (%)",
        "ty_trong":                   "Tỷ trọng",
    }
    con = get_db()
    cur = con.execute("SELECT * FROM records LIMIT 1")
    cols = [d[0] for d in cur.description]
    con.close()
    return {
        "columns": cols,
        "labels": {c: LABELS.get(c, c) for c in cols}
    }

# ── /filters ──────────────────────────────────────────────────────────────────
@app.get("/filters")
def filters():
    """
    Returns unique values for all categorical filter dropdowns.
    Best practice: only enumerate low-cardinality columns here.
    """
    con = get_db()

    def unique_vals(col, limit=200):
        rows = con.execute(
            f"SELECT DISTINCT {col} FROM records WHERE {col} IS NOT NULL ORDER BY {col} LIMIT {limit}"
        ).fetchall()
        return [r[0] for r in rows]

    result = {
        "loai_phan": unique_vals("loai_phan"),
        "ghi_chu":   unique_vals("ghi_chu"),       # YES / NO
    }
    con.close()
    return result

# ── /search ───────────────────────────────────────────────────────────────────
@app.get("/search")
def search(
    q:           str            = Query(default="",   description="Full-text search (tên, loại, thành phần, mã số)"),
    page:        int            = Query(default=1, ge=1),
    loai_phan:   Optional[str]  = Query(default=None, description="Lọc theo loại phân"),
    ghi_chu:     Optional[str]  = Query(default=None, description="YES = còn lưu hành, NO = hết lưu hành"),
    # Numeric range filters for key nutrients
    dam_min:     Optional[float] = Query(default=None, description="Đạm tổng số tối thiểu (%)"),
    dam_max:     Optional[float] = Query(default=None, description="Đạm tổng số tối đa (%)"),
    lan_min:     Optional[float] = Query(default=None, description="Lân hữu hiệu tối thiểu (%)"),
    lan_max:     Optional[float] = Query(default=None, description="Lân hữu hiệu tối đa (%)"),
    kali_min:    Optional[float] = Query(default=None, description="Kali hữu hiệu tối thiểu (%)"),
    kali_max:    Optional[float] = Query(default=None, description="Kali hữu hiệu tối đa (%)"),
):
    con = get_db()
    offset = (page - 1) * PAGE_SIZE
    params = []

    # Start with FTS or full table
    if q.strip():
        base = "FROM records WHERE rowid IN (SELECT rowid FROM records_fts WHERE records_fts MATCH ?)"
        params.append(q.strip() + "*")
    else:
        base = "FROM records WHERE 1=1"

    # Categorical filters
    if loai_phan:
        base += " AND loai_phan = ?"
        params.append(loai_phan)

    if ghi_chu:
        base += " AND ghi_chu = ?"
        params.append(ghi_chu)

    # Numeric range filters
    if dam_min is not None:
        base += " AND CAST(dam_tong_so_pct AS REAL) >= ?"
        params.append(dam_min)
    if dam_max is not None:
        base += " AND CAST(dam_tong_so_pct AS REAL) <= ?"
        params.append(dam_max)

    if lan_min is not None:
        base += " AND CAST(lan_huu_hieu_pct AS REAL) >= ?"
        params.append(lan_min)
    if lan_max is not None:
        base += " AND CAST(lan_huu_hieu_pct AS REAL) <= ?"
        params.append(lan_max)

    if kali_min is not None:
        base += " AND CAST(kali_huu_hieu_pct AS REAL) >= ?"
        params.append(kali_min)
    if kali_max is not None:
        base += " AND CAST(kali_huu_hieu_pct AS REAL) <= ?"
        params.append(kali_max)

    total = con.execute(f"SELECT COUNT(*) {base}", params).fetchone()[0]
    rows  = con.execute(
        f"SELECT * {base} LIMIT {PAGE_SIZE} OFFSET {offset}", params
    ).fetchall()
    con.close()

    return {
        "total": total,
        "pages": math.ceil(total / PAGE_SIZE) if total > 0 else 1,
        "page":  page,
        "data":  [dict(r) for r in rows],
    }

# ── /health ───────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    con = get_db()
    count = con.execute("SELECT COUNT(*) FROM records").fetchone()[0]
    con.close()
    return {"status": "ok", "total_records": count}