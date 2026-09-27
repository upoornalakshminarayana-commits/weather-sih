# VARSHAAI — Machine Learning Backend (SIH 26080)
### Regime-Aware AI Post-Processing of Monsoon Rainfall Forecasts

> **“We are not replacing NWP. We are intelligently post-processing NWP rainfall forecasts according to the prevailing weather regime to reduce systematic rainfall errors.”**

---

## 1. Overview & Architecture

Raw Numerical Weather Prediction (NWP) models (such as NCMRWF NEPS-G) have systematic bias structures that depend on the active synoptic weather regime. A single universal bias correction degrades forecasts in opposing regimes.

The VARSHAAI machine learning backend implements a two-stage regime-aware intelligence pipeline:

```text
NWP Forecast + Atmospheric Variables (15 anti-leakage features)
                         ↓
    [Stage 1: Multiclass Weather Regime Classifier]
          (XGBoost Multiclass: 6 Regimes)
                         ↓
                 Predicted Regime
                         ↓
    [Stage 2: Regime-Specific Bias Correction]
      (6 dedicated XGBoost Regressors:
       Active, Break, Low, Coastal, Orographic, WD)
                         ↓
             Corrected Rainfall (mm)
                         ↓
    [Stage 3: Calibrated Heavy Rain Classifier]
    (P(Rain ≥ 64.5 mm) with Sigmoid Probability Calibration)
                         ↓
               Uncertainty Envelope
                         ↓
            Verification Against Observations
```

---

## 2. Directory Structure

```text
backend/
├── app/
│   ├── main.py                  # FastAPI application entrypoint (CORS, lifespan)
│   ├── schemas.py               # Pydantic request/response models
│   ├── config.py                # Environment paths and configuration
│   ├── api/
│   │   ├── health.py            # GET /health
│   │   ├── forecast.py          # POST /api/predict, GET /api/forecast-journey/{id}
│   │   ├── regime.py            # GET /api/regime/{id}
│   │   ├── risk.py              # GET /api/risk/{id}
│   │   ├── verification.py      # GET /api/verification (baselines, regime-wise)
│   │   ├── model.py             # GET /api/model/metrics, /feature-importance
│   │   └── data_quality.py      # GET /api/data-quality (audit metrics)
│   ├── ml/
│   │   ├── features.py          # Anti-leakage Feature Registry
│   │   ├── preprocessing.py     # Chronological 70/15/15 train/val/test splitting
│   │   ├── regime_classifier.py # Multiclass XGBoost Regime Classifier
│   │   ├── rainfall_corrector.py# 6 Regime-specific XGBoost Regressors + Global Baseline
│   │   ├── heavy_rain_model.py  # Calibrated probability classifier (≥ 64.5 mm)
│   │   ├── calibration.py       # Reliability curves & CSI/POD/FAR/ETS scores
│   │   └── inference.py         # Runtime inference engine
│   └── services/
│       ├── data_service.py      # Ingestion & quality checks
│       ├── forecast_service.py  # Forecast Journey generator
│       └── verification_service.py # Evaluation analytics
├── data/
│   └── SIH26080_10000_training_dataset.csv # 10,000 prototype records
├── models/
│   ├── regime_classifier.joblib
│   ├── global_corrector.joblib
│   ├── active_monsoon_corrector.joblib
│   ├── break_monsoon_corrector.joblib
│   ├── monsoon_low_depression_corrector.joblib
│   ├── coastal_rainfall_corrector.joblib
│   ├── orographic_rainfall_corrector.joblib
│   ├── western_disturbance_corrector.joblib
│   ├── heavy_rain_classifier.joblib
│   ├── metrics.json             # Genuine holdout test-set evaluation results
│   ├── feature_importance.json  # Empirical tree feature importance weights
│   └── model_version.json       # Version tracking metadata
├── scripts/
│   ├── train_all.py             # End-to-end master training & evaluation script
│   ├── train_regime_model.py    # Train regime classifier only
│   ├── train_correction_models.py # Train 6 regressors only
│   ├── train_heavy_rain_model.py# Train heavy rain classifier only
│   ├── evaluate_models.py       # Benchmark evaluation script
│   └── convert_dataset.py       # Convert XLSX to CSV
├── requirements.txt
└── README.md
```

---

## 3. Quickstart & Installation

### Step 1: Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run Full Model Training & Evaluation
```bash
python scripts/train_all.py
```
This executes:
1. Chronological splitting (Train 70% | Val 15% | Test 15%).
2. Training of Model 1 (Weather Regime Classifier).
3. Training of Model 2 (6 Regime-Specific Bias Regressors + Global Baseline).
4. Training and probability calibration of Model 3 (Heavy Rain Exceedance).
5. Evaluation on the **unseen 1,500-record test set**.
6. Serialization into `models/*.joblib`, `metrics.json`, and `feature_importance.json`.

### Step 4: Start the FastAPI Microservice
```bash
uvicorn app.main:app --reload --port 8000
```
Interactive Swagger API documentation will be available at:
`http://localhost:8000/docs`

### Step 5: Open the Frontend
Open `index.html` in your web browser.  
The topbar badge will immediately transition from `🟡 DEMO MODE` to:
`🟢 ML MODEL ACTIVE (FastAPI v0.1.0)`
and live model predictions will power the GIS map, Forecast Journey, and Model Lab.

---

## 4. API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Heartbeat, model loading status, and version |
| `POST` | `/api/predict` | Real-time prediction (Regime, Corrected Rain, Probability, Risk) |
| `GET` | `/api/forecast/{record_id}` | Real ML inference for a specific dataset record |
| `GET` | `/api/forecast-journey/{record_id}` | Complete 7-step Forecast Journey payload |
| `GET` | `/api/regime/{record_id}` | Regime classification & probability distribution |
| `GET` | `/api/risk/{record_id}` | Calibrated probability ($P \ge 64.5\text{ mm}$) & risk level |
| `GET` | `/api/verification` | Benchmark comparison (Raw NWP vs Global Baseline vs Regime AI) |
| `GET` | `/api/verification/by-regime` | Regime-wise error metrics (RMSE, CSI, POD, FAR) |
| `GET` | `/api/model/metrics` | Full evaluation metrics from unseen test set |
| `GET` | `/api/model/feature-importance` | Tree feature importance weights (empirical) |
| `GET` | `/api/data-quality` | Data cleanliness audit (nulls, duplicates, coordinates) |

### Sample Real-Time Prediction Request (`POST /api/predict`):
```json
{
  "nwp_rainfall_mm": 72.0,
  "ensemble_mean_mm": 70.0,
  "ensemble_std_mm": 12.0,
  "ensemble_min_mm": 51.0,
  "ensemble_max_mm": 91.0,
  "temperature_c": 27.0,
  "relative_humidity_pct": 87.0,
  "surface_pressure_hpa": 1002.0,
  "wind_u_ms": 4.1,
  "wind_v_ms": 8.4,
  "latitude": 17.7,
  "longitude": 83.3,
  "elevation_m": 10.0,
  "coastal_distance_km": 5.0,
  "lead_time_hours": 24
}
```

### Response:
```json
{
  "predicted_regime": "Monsoon Low / Depression",
  "regime_key": "monsoon_low_depression",
  "regime_confidence": 0.885,
  "raw_nwp_rainfall_mm": 72.0,
  "corrected_rainfall_mm": 91.0,
  "ai_adjustment_mm": 19.0,
  "heavy_rain_probability": 0.78,
  "heavy_rain_threshold_mm": 64.5,
  "risk_category": "Red Alert (Very High Risk)",
  "model_version": "0.1.0-prototype",
  "is_real_model": true,
  "explanation": "Under the Monsoon Low / Depression regime, physical NWP models systematically underestimate intense boundary-layer moisture convergence. The regime-specific regressor adjusted the prediction from 72.0 mm to 91.0 mm (+19.0 mm)."
}
```

---

## 5. Anti-Leakage Protection & Verification Rigor

1. **Anti-Leakage Feature Registry (`app/ml/features.py`)**:
   - `observed_rainfall_mm`, `heavy_rain_event`, and `regime_aware_corrected_rainfall_mm` are strictly locked out of training feature sets.
   - The regime models do not accept `weather_regime` as a feature (routing to the regime model eliminates self-referential bias).
2. **Chronological Splitting**:
   - Data is sorted by `valid_time` and split chronologically (First 70% Train, Next 15% Val, Final 15% Unseen Test) to ensure future weather events never leak into historical training.
3. **No Fabricated Spatial Metrics**:
   - Fraction Skill Score (FSS) is explicitly documented as: *"FSS unavailable for current prototype dataset; requires verified spatial grid data."*

---

## 6. Dataset Limitations & Operational Roadmap

> [!WARNING]
> **Prototype Dataset Notice**:
> The 10,000-row prototype dataset is a development dataset. It must not be cited as operational NCMRWF / IMD observational feeds.
> 
> **Operational Integration Roadmap**:
> The architecture is engineered with standard abstract data services (`DataService`, `ForecastService`). To deploy operationally:
> 1. Ingest NCMRWF NEPS-G 12km ensemble GRIB2/NetCDF files via `xarray`.
> 2. Align spatially with IMD 0.25° gridded daily rainfall observations.
> 3. Retrain the exact same XGBoost pipelines without modifying any frontend code.
