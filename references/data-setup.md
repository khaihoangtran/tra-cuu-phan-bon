# Data Setup Reference

## load_data.py — Production Version (real CSV columns)

The source CSV (`data/phan_bon.csv`) has 33 raw columns. `load_data.py` does three things:
1. Parses the compound `Lưu hành` field into 5 clean columns
2. Renames all columns via an explicit `COLUMN_MAP`
3. Builds SQLite indexes + FTS5 virtual table

### Lưu hành field structure
Raw value: `"ĐÁP MỸ 911\n26324\n363/QĐ-BVTV-PB\n15/03/2024 -> 14/03/2029"`
Parsed into: `ten_san_pham` / `ma_so_phan_bon` / `so_quyet_dinh` / `ngay_cap` / `ngay_het_han`

### Complete COLUMN_MAP (raw CSV → DB snake_case)

```python
COLUMN_MAP = {
    "MSPB":                                  "mspb",
    "Loại phân":                             "loai_phan",
    "Thành phần":                            "thanh_phan",
    "Đạm tổng số (Nts)":                     "dam_tong_so_pct",
    "Lân hữu hiệu (P2O5hh)":                "lan_huu_hieu_pct",
    "Kali hữu hiệu (K2Ohh)":                "kali_huu_hieu_pct",
    "Canxi (Ca)":                            "canxi_pct",
    "Magie (Mg)":                            "magie_pct",
    "Lưu huỳnh (S)":                         "luu_huynh_pct",
    "Silic hữu hiệu (SiO2hh)":              "silic_huu_hieu_pct",
    "Đồng (Cu)":                             "dong_ppm",
    "Sắt (Fe)":                              "sat_ppm",
    "Kẽm (Zn)":                              "kem_ppm",
    "Bo (B)":                                "bo_ppm",
    "Mangan (Mn)":                           "mangan_ppm",
    "GA3":                                   "ga3",
    "NAA ":                                  "naa",           # 0% fill — kept, not filtered
    "Chất hữu cơ":                           "chat_huu_co_pct",
    "Axit humic (axit humic)":               "axit_humic_pct",
    "Axit fulvic (axit fulvic)":             "axit_fulvic_pct",
    "Tổng axit humic và axit fulvic (C)":    "tong_axit_humic_fulvic_pct",  # 0% fill
    "Axit amin":                             "axit_amin",
    "Chitosan":                              "chitosan",      # 0% fill
    "Vi Sinh vật cố định đạm":              "vsv_co_dinh_dam",
    "Vi Sinh vật phân giải lân":            "vsv_phan_giai_lan",   # 0% fill
    "Vi Sinh vật phân giải xenlulo":        "vsv_phan_giai_xenlulo",  # 0% fill
    "Trichoderma":                           "trichoderma",
    "pHH2O":                                 "ph_h2o",
    "Tỷ lệ C/N":                             "ty_le_cn",
    "Độ ẩm":                                 "do_am_pct",
    "Tỷ trọng":                              "ty_trong",
    # Parsed from Lưu hành:
    "ten_san_pham":    "ten_san_pham",
    "ma_so_phan_bon":  "ma_so_phan_bon",
    "so_quyet_dinh":   "so_quyet_dinh",
    "ngay_cap":        "ngay_cap",
    "ngay_het_han":    "ngay_het_han",
}
```

### Indexes created

```python
INDEX_COLS = ["loai_phan", "ngay_het_han"]
```

### FTS5 table (4 columns, unicode61)

```python
con.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS records_fts
    USING fts5(
        ten_san_pham, loai_phan, thanh_phan, ma_so_phan_bon,
        tokenize='unicode61',
        content='records', content_rowid='rowid'
    )
""")
con.execute("INSERT INTO records_fts(records_fts) VALUES('rebuild')")
```

## Re-import Updated CSV

```bash
cp new_export.csv data/phan_bon.csv
rm backend/database.db          # FTS rebuild requires clean DB
cd backend && python load_data.py
sqlite3 database.db "SELECT COUNT(*) FROM records;"
sqlite3 database.db "SELECT ten_san_pham FROM records_fts WHERE records_fts MATCH 'ure*' LIMIT 3;"
```

## Encoding Notes

Always use `encoding="utf-8-sig"` — the Ministry CSV uses UTF-8 with BOM (Excel export).
Also use `low_memory=False, dtype=str` to avoid mixed-type warnings across 100k rows.

## DB Verification Queries

```sql
SELECT COUNT(*) FROM records;
SELECT loai_phan, COUNT(*) FROM records GROUP BY loai_phan ORDER BY 2 DESC LIMIT 10;
SELECT ten_san_pham, loai_phan FROM records_fts WHERE records_fts MATCH 'NPK*' LIMIT 5;
```