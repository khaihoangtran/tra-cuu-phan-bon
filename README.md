# 🌿 Tra cứu Phân Bón

Hệ thống tra cứu thông tin phân bón nhanh chóng với hơn 1 triệu bản ghi.

**Fertilizer Lookup** — A fast search system for fertilizer product data with 1M+ records.

## Tech Stack
- Backend: Python + FastAPI + SQLite (FTS5)
- Frontend: HTML + Vanilla JS
- Deploy: Render.com (free tier)

## Setup
```bash
cd backend
pip install -r requirements.txt
python load_data.py   # import your CSV first
uvicorn main:app --reload
```