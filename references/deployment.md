# Deployment Reference — Render.com Free Tier

## render.yaml (commit this to repo root)

```yaml
services:
  - type: web
    name: tra-cuu-phan-bon-api
    env: python
    rootDir: backend
    buildCommand: pip install -r requirements.txt && python load_data.py
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    plan: free
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0

  - type: web
    name: tra-cuu-phan-bon-frontend
    env: static
    rootDir: frontend
    staticPublishPath: .
    plan: free
```

## .gitignore (repo root)

```
# Generated files — never commit these
backend/database.db
data/*.csv

# Python
__pycache__/
*.pyc
*.pyo
.env
.venv/
venv/

# OS
.DS_Store
Thumbs.db
```

## Step-by-Step Deploy

### 1. Prepare the CSV for Render

Render's free tier has no persistent disk — the DB must be **built at deploy time** from a file bundled in the repo, or fetched from an external source.

**Option A — Small CSV (<100MB): commit to repo**
```bash
# Remove CSV from .gitignore temporarily, commit, then restore
git add data/phan_bon.csv
git commit -m "data: add fertilizer CSV for build"
```
This is fine for a 1M row CSV (~50-150MB depending on columns).

**Option B — Large CSV: host on Google Drive / S3**
Modify `load_data.py` to download the CSV at build time:
```python
import urllib.request
CSV_URL = "https://drive.google.com/uc?export=download&id=YOUR_FILE_ID"
urllib.request.urlretrieve(CSV_URL, CSV_FILE)
```

### 2. Create the Backend Service on Render

1. Go to https://render.com → **New → Web Service**
2. Connect your GitHub repo `tra-cuu-phan-bon`
3. Settings:
   - **Name:** `tra-cuu-phan-bon-api`
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt && python load_data.py`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free
4. Click **Create Web Service**
5. Copy the URL, e.g. `https://tra-cuu-phan-bon-api.onrender.com`

### 3. Create the Frontend Static Site on Render

1. **New → Static Site**
2. Same repo, settings:
   - **Root Directory:** `frontend`
   - **Publish Directory:** `.`
   - **Plan:** Free
3. Click **Create Static Site**
4. Open the site → enter the backend URL from step 2 in the ⚙ panel

### 4. Custom Domain (optional, free)

In Render dashboard → your Static Site → **Custom Domains** → add your domain → follow DNS instructions.

## Free Tier Limitations

| Limit | Value | Impact |
|---|---|---|
| Spin-down | 15 min inactivity | First request after idle takes ~30s |
| Build time | 30 min max | 1M row DB build usually takes 3-5 min |
| RAM | 512MB | Pandas load of 1M rows fits fine |
| Bandwidth | 100GB/month | ~100M search requests |
| Storage | Ephemeral | DB rebuilt on every deploy |

## Preventing Cold Starts (free tier workaround)

Add a health-check ping every 10 minutes using a free service like UptimeRobot:
- URL: `https://tra-cuu-phan-bon-api.onrender.com/health`
- Interval: 5 minutes
- This keeps the service warm.

## Logs & Debugging

```bash
# View live logs from Render CLI (optional)
render logs --service tra-cuu-phan-bon-api --tail

# Or check the Render dashboard → your service → Logs tab
```

Common errors:
- `ModuleNotFoundError: No module named 'fastapi'` → build command didn't run pip install
- `database.db not found` → load_data.py failed, check CSV path
- `CORS error in browser` → check `allow_origins=["*"]` is in main.py