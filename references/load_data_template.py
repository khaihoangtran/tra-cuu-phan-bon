"""
load_data.py — Tra cứu Phân Bón
Imports the fertilizer CSV into SQLite with FTS5 and filter indexes.
Run once: python load_data.py
"""
import pandas as pd
import sqlite3
import os
import re

CSV_FILE = os.path.join(os.path.dirname(__file__), "../data/phan_bon.csv")
DB_FILE  = os.path.join(os.path.dirname(__file__), "database.db")

# ── 1. Load CSV ───────────────────────────────────────────────────────────────
print("📂 Loading CSV...")
df = pd.read_csv(CSV_FILE, encoding="utf-8-sig", low_memory=False, dtype=str)
print(f"   Raw rows: {len(df):,}  |  Columns: {len(df.columns)}")

# ── 2. Parse compound field "Lưu hành" → 5 clean columns ─────────────────────
# Raw format: "TÊN SẢN PHẨM\nMSPB\nSỐ QĐ\nDD/MM/YYYY -> DD/MM/YYYY"
def parse_luu_hanh(val):
    if pd.isna(val) or not str(val).strip():
        return pd.Series({
            "ten_san_pham": None, "ma_so_phan_bon": None,
            "so_quyet_dinh": None, "ngay_cap": None, "ngay_het_han": None
        })
    parts = str(val).split("\n")
    ten   = parts[0].strip() if len(parts) > 0 else None
    mspb  = parts[1].strip() if len(parts) > 1 else None
    so_qd = parts[2].strip() if len(parts) > 2 else None
    hl    = parts[3].strip() if len(parts) > 3 else None
    ngay_cap = ngay_het = None
    if hl and "->" in hl:
        d = hl.split("->")
        ngay_cap = d[0].strip()
        ngay_het = d[1].strip()
    return pd.Series({
        "ten_san_pham": ten,
        "ma_so_phan_bon": mspb,
        "so_quyet_dinh": so_qd,
        "ngay_cap": ngay_cap,
        "ngay_het_han": ngay_het,
    })

print("🔧 Parsing 'Lưu hành' field...")
parsed = df["Lưu hành"].apply(parse_luu_hanh)
df = pd.concat([df.drop(columns=["Lưu hành"]), parsed], axis=1)

# ── 3. Rename all columns to clean snake_case ─────────────────────────────────
COLUMN_MAP = {
    "MSPB":                                  "mspb",
    "Ghi chú thêm":                          "ghi_chu",
    "Loại phân":                             "loai_phan",
    "Thành phần":                            "thanh_phan",
    # Macro nutrients
    "Đạm tổng số (Nts)":                     "dam_tong_so_pct",
    "Lân hữu hiệu (P2O5hh)":                "lan_huu_hieu_pct",
    "Kali hữu hiệu (K2Ohh)":                "kali_huu_hieu_pct",
    # Secondary nutrients
    "Canxi (Ca)":                            "canxi_pct",
    "Magie (Mg)":                            "magie_pct",
    "Lưu huỳnh (S)":                         "luu_huynh_pct",
    "Silic hữu hiệu (SiO2hh)":              "silic_huu_hieu_pct",
    # Micro nutrients
    "Đồng (Cu)":                             "dong_ppm",
    "Sắt (Fe)":                              "sat_ppm",
    "Kẽm (Zn)":                              "kem_ppm",
    "Bo (B)":                                "bo_ppm",
    "Mangan (Mn)":                           "mangan_ppm",
    "GA3":                                   "ga3",
    "NAA ":                                  "naa",
    # Organic & biological
    "Chất hữu cơ":                           "chat_huu_co_pct",
    "Axit humic (axit humic)":               "axit_humic_pct",
    "Axit fulvic (axit fulvic)":             "axit_fulvic_pct",
    "Tổng axit humic và axit fulvic (C)":    "tong_axit_humic_fulvic_pct",
    "Axit amin":                             "axit_amin",
    "Chitosan":                              "chitosan",
    # Microbes
    "Vi Sinh vật cố định đạm":              "vsv_co_dinh_dam",
    "Vi Sinh vật phân giải lân":            "vsv_phan_giai_lan",
    "Vi Sinh vật phân giải xenlulo":        "vsv_phan_giai_xenlulo",
    "Trichoderma":                           "trichoderma",
    # Physical properties
    "pHH2O":                                 "ph_h2o",
    "Tỷ lệ C/N":                             "ty_le_cn",
    "Độ ẩm":                                 "do_am_pct",
    "Tỷ trọng":                              "ty_trong",
    # Parsed from Lưu hành
    "ten_san_pham":                          "ten_san_pham",
    "ma_so_phan_bon":                        "ma_so_phan_bon",
    "so_quyet_dinh":                         "so_quyet_dinh",
    "ngay_cap":                              "ngay_cap",
    "ngay_het_han":                          "ngay_het_han",
}
df.rename(columns=COLUMN_MAP, inplace=True)

# Preferred column order for display
COL_ORDER = [
    "mspb", "ten_san_pham", "loai_phan", "ma_so_phan_bon",
    "so_quyet_dinh", "ngay_cap", "ngay_het_han",
    "thanh_phan", "ghi_chu",
    "dam_tong_so_pct", "lan_huu_hieu_pct", "kali_huu_hieu_pct",
    "canxi_pct", "magie_pct", "luu_huynh_pct", "silic_huu_hieu_pct",
    "dong_ppm", "sat_ppm", "kem_ppm", "bo_ppm", "mangan_ppm",
    "ga3", "naa",
    "chat_huu_co_pct", "axit_humic_pct", "axit_fulvic_pct",
    "tong_axit_humic_fulvic_pct", "axit_amin", "chitosan",
    "vsv_co_dinh_dam", "vsv_phan_giai_lan", "vsv_phan_giai_xenlulo",
    "trichoderma", "ph_h2o", "ty_le_cn", "do_am_pct", "ty_trong",
]
# Only keep columns that exist
COL_ORDER = [c for c in COL_ORDER if c in df.columns]
df = df[COL_ORDER]

print(f"   Final columns ({len(df.columns)}): {list(df.columns)}")

# ── 4. Write to SQLite ────────────────────────────────────────────────────────
print("💾 Writing to SQLite...")
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
con = sqlite3.connect(DB_FILE)
df.to_sql("records", con, if_exists="replace", index=False)
print(f"   Rows written: {len(df):,}")

# ── 5. Indexes for filter columns ─────────────────────────────────────────────
print("🔍 Creating indexes...")
INDEX_COLS = ["loai_phan", "ghi_chu", "ngay_het_han"]
for col in INDEX_COLS:
    if col in df.columns:
        con.execute(f"CREATE INDEX IF NOT EXISTS idx_{col} ON records({col})")
        print(f"   ✅ idx_{col}")

# ── 6. FTS5 virtual table (unicode61 for Vietnamese) ─────────────────────────
# Search across: product name, fertilizer type, composition, registration
print("🔎 Building FTS5 index...")
con.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS records_fts
    USING fts5(
        ten_san_pham,
        loai_phan,
        thanh_phan,
        ma_so_phan_bon,
        so_quyet_dinh,
        tokenize='unicode61',
        content='records',
        content_rowid='rowid'
    )
""")
con.execute("INSERT INTO records_fts(records_fts) VALUES('rebuild')")
print("   ✅ FTS5 index built")

# ── 7. Done ───────────────────────────────────────────────────────────────────
con.commit()
con.close()
print(f"\n✅ Done! database.db ready → {DB_FILE}")
print(f"   Total records: {len(df):,}")