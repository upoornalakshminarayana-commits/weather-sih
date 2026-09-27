# VARSHAAI (SIH 26080) — Complete Production Deployment Guide
**Regime-Aware AI Post-Processing of Monsoon Rainfall Forecasts**

This document provides step-by-step instructions for deploying both the FastAPI machine learning backend and the client dashboard to public cloud infrastructure.

---

## 1. System Architecture Overview

```text
┌────────────────────────────────────────────────────────┐
│                   FRONTEND HOST                        │
│   (Vercel / GitHub Pages / Netlify)                    │
│   • index.html, css/, js/                              │
│   • Direct Open-Meteo fallback (CORS enabled)          │
│   • window.VARSHA_CONFIG.BACKEND_URL                   │
└──────────────────────────┬─────────────────────────────┘
                           │ HTTPS (CORS)
                           ▼
┌────────────────────────────────────────────────────────┐
│                   BACKEND HOST                         │
│   (Render Web Service / Railway / Docker)              │
│   • FastAPI (uvicorn app.main:app --port $PORT)        │
│   • GET /health & GET /api/health                      │
│   • Server-Side OpenWeatherMap & Tomorrow.io Keys      │
│   • Server-Side Open-Meteo Feed (No Key Required)      │
└──────────────────────────┬─────────────────────────────┘
                           │ Internal Pipeline
                           ▼
┌────────────────────────────────────────────────────────┐
│                   MACHINE LEARNING                     │
│   • Weather Regime Classifier (XGBoost Multiclass)     │
│   • 6 Regime-Specific Bias Regressors + Global Model   │
│   • Calibrated Heavy Rain Exceedance (P >= 64.5 mm)    │
│   • Feature Registry with Anti-Leakage Guards          │
└────────────────────────────────────────────────────────┘
```

---

## 2. Backend Deployment

### Option A: Render (Recommended & Free Tier Friendly)
Render natively runs Python/FastAPI web services and supports automatic deploys from GitHub.

1. **Sign in to Render**: Navigate to [render.com](https://render.com) and log in with your GitHub account.
2. **Create New Web Service**: Click **New +** → **Web Service**.
3. **Connect Repository**: Select `upoornalakshminarayana-commits/weather-sih`.
4. **Configure Service Settings**:
   - **Name**: `varshaai-backend`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
5. **Add Environment Variables**:
   Under **Environment Variables**, add:
   - `PYTHON_VERSION`: `3.11.9`
   - `OPEN_METEO_BASE_URL`: `https://api.open-meteo.com/v1`
   - `TOMORROW_API_KEY`: *(Optional: your Tomorrow.io key)*
   - `TOMORROW_API_BASE_URL`: `https://api.tomorrow.io/v4`
   - `OPENWEATHER_API_KEY`: *(Optional: your OpenWeather key)*
   - `CORS_ORIGINS`: `https://your-frontend-domain.vercel.app`
   - `ENVIRONMENT`: `production`
6. **Click Deploy**: Render will install dependencies, load the ML models from `backend/models/*.joblib`, and launch the service.
7. **Copy Your Backend URL**: Once deployed, note down your live URL (e.g. `https://varshaai-backend.onrender.com`).

---

### Option B: Railway / Docker (Containerized Deployment)
The repository includes a ready-to-run `backend/Dockerfile`.

1. Go to [railway.app](https://railway.app) and create a project from GitHub repository.
2. Set Root Directory to `/backend`.
3. Railway automatically detects `backend/Dockerfile` and runs:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
4. Set required environment variables in the Railway dashboard.

---

## 3. Backend Verification & Health Checks

Once the backend is live, verify it using these endpoints:

| Endpoint | Method | Expected Output | Purpose |
| :--- | :--- | :--- | :--- |
| `/health` | `GET` | `{"status":"healthy","is_models_loaded":true,...}` | Container health probe |
| `/api/health` | `GET` | `{"status":"healthy","is_models_loaded":true,...}` | Aliased health check |
| `/docs` | `GET` | Swagger Interactive UI | API Documentation |
| `/api/live-weather?lat=17.68&lon=83.21` | `GET` | Live weather + real AI prediction | Open-Meteo ML feed |
| `/api/model/metrics` | `GET` | Test-set RMSE & Skill Scores | Model Verification |

---

## 4. Frontend Deployment

### Option A: Vercel (Recommended Static CDN)
1. Navigate to [vercel.com](https://vercel.com) and log in with GitHub.
2. Click **Add New...** → **Project**.
3. Import `upoornalakshminarayana-commits/weather-sih`.
4. Leave settings as default:
   - **Framework Preset**: `Other`
   - **Root Directory**: `./`
5. Click **Deploy**. Vercel will deploy `index.html`, `css/`, and `js/` in under 30 seconds.
6. Note down your live URL (e.g. `https://weather-sih.vercel.app`).

### Option B: GitHub Pages
1. Go to your repository on GitHub: `upoornalakshminarayana-commits/weather-sih`.
2. Click **Settings** → **Pages** (left sidebar).
3. Under **Branch**, select `main` and folder `/ (root)`.
4. Click **Save**. GitHub Pages will be live at:
   `https://upoornalakshminarayana-commits.github.io/weather-sih/`

---

## 5. Connecting Frontend to Backend

You have 3 easy ways to link the frontend to the deployed backend:

### Method 1: URL Parameter (Zero-Deploy Testing)
You can open your live frontend in any browser and pass the backend URL directly:
```text
https://weather-sih.vercel.app/?backend=https://varshaai-backend.onrender.com
```
The frontend immediately locks onto the backend, confirms `/health`, and displays `🟢 ML MODEL ACTIVE`.

### Method 2: Configure `js/config.js`
For local or dedicated static deploys, create `js/config.js`:
```javascript
window.VARSHA_CONFIG = {
  BACKEND_URL: "https://varshaai-backend.onrender.com"
};
```

### Method 3: In `index.html` Default Header
Set the default production URL in `index.html` (lines 1258-1264):
```html
<script>
  window.VARSHA_CONFIG = window.VARSHA_CONFIG || {
    BACKEND_URL: "https://varshaai-backend.onrender.com",
    CARTO_API_KEY: "",
    OPENWEATHERMAP_API_KEY: "",
    TOMORROW_IO_API_KEY: ""
  };
</script>
```

---

## 6. Security & API Key Management

1. **Never commit `.env` or `js/config.js` to GitHub**:
   Both files are strictly guarded by `.gitignore`.
2. **Zero-Secret Client Operation**:
   The frontend calls your FastAPI backend `/api/live-weather` endpoint. The backend handles Tomorrow.io and OpenWeatherMap credentials securely on the server. The browser network inspector never sees private API keys.
3. **Open-Meteo Integration**:
   Open-Meteo requires **no API key**. Even if you have zero commercial keys, the live weather tab works flawlessly for all Indian coordinates.

---

## 7. Troubleshooting Guide

### Issue 1: Status badge shows `🟡 DEMO MODE (ML Backend Disconnected)`
- **Cause:** Backend is either warming up (Render free tier sleeps after 15 min of inactivity) or the URL in the frontend is pointing to `localhost`.
- **Solution:** Wait 40-50 seconds for Render to wake up, or open the frontend with `?backend=https://your-backend.onrender.com`.

### Issue 2: CORS Error in Browser Console
- **Cause:** The frontend origin is not in the backend's allowed origins list.
- **Solution:** In the Render dashboard, add `CORS_ORIGINS=https://your-frontend-app.vercel.app` (or leave as `*` which is permitted when `allow_credentials=False`).

### Issue 3: Backend logs `Warning: Some or all model files not found`
- **Cause:** `.joblib` files were not pushed to GitHub.
- **Solution:** Ensure `.gitignore` does not contain `backend/models/*.joblib`, and push the model files (`git add backend/models/*.joblib && git push`).

---

## 8. Local Smoke Test Command

Run the included verification suite anytime before pushing changes:

```powershell
py -3 backend/test_deployment.py
```
Expected output:
```text
============================================================
ALL TESTS PASSED — DEPLOYMENT READY!
============================================================
```
