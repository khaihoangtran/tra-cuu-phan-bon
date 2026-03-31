# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Tra cứu Phân Bón** — A fertilizer product lookup system with 1M+ records. Vietnamese-language product, deployed on Render.com (free tier).

## Tech Stack

- **Backend**: Python + FastAPI + SQLite with FTS5 (full-text search)
- **Frontend**: HTML + Vanilla JavaScript
- **Deploy**: Render.com

## Development Commands

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Import CSV data into SQLite
python load_data.py

# Run development server
uvicorn main:app --reload
```

## Architecture

The system is split into two parts:

- **`backend/`** — FastAPI app serving a REST search API over a SQLite database. `load_data.py` imports source CSV data into SQLite using FTS5 for fast full-text search across 1M+ records. `main.py` is the FastAPI entry point.
- **Frontend** — Static HTML + JS files that query the backend API and render results.

The SQLite FTS5 extension is critical for performance at this data scale — queries go through the FTS5 virtual table, not plain `LIKE` searches.
