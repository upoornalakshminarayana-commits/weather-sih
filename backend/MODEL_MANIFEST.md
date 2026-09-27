# VARSHAAI — Machine Learning Model Manifest
**Smart India Hackathon (SIH 26080)**  
**Problem Statement:** Regime-Aware AI Post-Processing of Monsoon Rainfall Forecasts

This manifest documents every trained machine learning model, serialized artifact, feature registry, and test-set verification metric deployed in the VARSHAAI system.

---

## 1. Summary of Model Artifacts

| Model Filename | Architecture | Framework | Size | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `regime_classifier.joblib` | XGBoost Multiclass Classifier | `xgboost>=1.7.0` | 1.60 MB | Classifies atmospheric synoptic state into 6 monsoon regimes |
| `active_monsoon_corrector.joblib` | XGBoost Regressor | `xgboost>=1.7.0` | 253 KB | Bias correction under Active Monsoon conditions |
| `break_monsoon_corrector.joblib` | XGBoost Regressor | `xgboost>=1.7.0` | 239 KB | Bias correction under Break Monsoon conditions |
| `monsoon_low_depression_corrector.joblib` | XGBoost Regressor | `xgboost>=1.7.0` | 245 KB | Bias correction during Low Pressure / Depression systems |
| `coastal_rainfall_corrector.joblib` | XGBoost Regressor | `xgboost>=1.7.0` | 242 KB | Bias correction along West Coast & East Coast strips |
| `orographic_rainfall_corrector.joblib` | XGBoost Regressor | `xgboost>=1.7.0` | 227 KB | Bias correction across Western Ghats & Northeast topography |
| `western_disturbance_corrector.joblib` | XGBoost Regressor | `xgboost>=1.7.0` | 226 KB | Bias correction for winter/pre-monsoon WD regimes |
| `global_corrector.joblib` | XGBoost Regressor | `xgboost>=1.7.0` | 264 KB | Regime-blind global baseline for scientific ablation comparison |
| `heavy_rain_classifier.joblib` | CalibratedClassifierCV (Sigmoid) | `scikit-learn>=1.3.0` + XGBoost | 365 KB | Calibrated exceedance probability $P(\text{Rain} \ge 64.5\text{ mm})$ |
| `metrics.json` | JSON Metadata | Built-in | 5.23 KB | Official test-set verification benchmarks |
| `feature_importance.json` | JSON Metadata | Built-in | 1.20 KB | Feature attribution split gain weights |
| `model_version.json` | JSON Metadata | Built-in | 628 B | Pipeline version metadata and training timestamps |

**Total Serialized Artifacts Footprint:** ~3.7 MB (well below GitHub's 100 MB limit, natively committable without Git LFS).

---

## 2. Model 1: Weather Regime Multiclass Classifier

- **File:** `backend/models/regime_classifier.joblib`
- **Algorithm:** XGBoost (`XGBClassifier`)
- **Objective:** `multi:softprob` (6 discrete classes)
- **Input Features (15 anti-leakage atmospheric predictors):**
  1. `temperature_c` (2m Surface Temperature)
  2. `relative_humidity_pct` (Relative Humidity)
  3. `surface_pressure_hpa` (Surface Atmospheric Pressure)
  4. `wind_u_ms` (Zonal Wind Component)
  5. `wind_v_ms` (Meridional Wind Component)
  6. `wind_speed_ms` (Scalar Wind Speed)
  7. `dew_point_spread_c` (Temperature minus Dew Point)
  8. `vorticity_proxy` (Dynamical low-level vorticity indicator)
  9. `moisture_flux_convergence_proxy` (Wind convergence $\times$ Humidity)
  10. `lapse_rate_proxy` (Atmospheric stability indicator)
  11. `cape_proxy_jkg` (Convective available potential energy estimate)
  12. `latitude` (°N)
  13. `longitude` (°E)
  14. `elevation_m` (Terrain height above sea level)
  15. `coastal_distance_km` (Distance to nearest maritime coast)
- **Strict Anti-Leakage Guard:** Strictly forbids `observed_rainfall_mm`, `nwp_rainfall_mm`, or any target rain field.
- **Test Metrics (Withheld 15% Chronological Split):**
  - Accuracy: **88.5%**
  - Precision (Macro): **88.7%**
  - Recall (Macro): **88.5%**
  - F1-Score (Macro): **0.886**

---

## 3. Model 2: Six Regime-Specific Bias Correctors

- **Directory:** `backend/models/*_corrector.joblib`
- **Algorithm:** 6 dedicated XGBoost Regressors (`XGBRegressor`) + 1 Global Baseline
- **Input Features (10 NWP predictors):**
  1. `nwp_rainfall_mm` (Raw NWP physical model simulation)
  2. `ensemble_mean_mm` (Ensemble mean precipitation)
  3. `ensemble_std_mm` (Ensemble spread / uncertainty)
  4. `ensemble_min_mm` (Ensemble lower bound)
  5. `ensemble_max_mm` (Ensemble upper bound)
  6. `temperature_c`
  7. `relative_humidity_pct`
  8. `surface_pressure_hpa`
  9. `wind_u_ms`
  10. `wind_v_ms`
- **Target:** `observed_rainfall_mm`
- **Test Set Evaluation vs Raw NWP & Global Baseline:**

| Model | Raw NWP RMSE | Global Baseline RMSE | Regime-Aware AI RMSE | Error Reduction |
| :--- | :--- | :--- | :--- | :--- |
| **Active Monsoon** | 20.8 mm | 17.2 mm | **11.2 mm** | **-46.2%** |
| **Break Monsoon** | 14.5 mm | 10.4 mm | **6.8 mm** | **-53.1%** |
| **Monsoon Low / Depression** | 29.1 mm | 22.8 mm | **16.4 mm** | **-43.6%** |
| **Coastal Rainfall** | 22.4 mm | 17.6 mm | **12.1 mm** | **-46.0%** |
| **Orographic Rainfall** | 26.7 mm | 20.3 mm | **14.9 mm** | **-44.2%** |
| **Western Disturbance** | 18.9 mm | 14.1 mm | **10.3 mm** | **-45.5%** |
| **OVERALL TEST BENCHMARK** | **21.4 mm** | **16.8 mm** | **12.8 mm** | **-40.2%** |

---

## 4. Model 3: Calibrated Heavy Rain Classifier

- **File:** `backend/models/heavy_rain_classifier.joblib`
- **Algorithm:** `CalibratedClassifierCV` wrapping `XGBClassifier` with `method="sigmoid"`
- **Target Threshold:** $P(\text{Observed Rainfall} \ge 64.5\text{ mm})$ (IMD Official Heavy Rain Criteria)
- **Input Features (13 features):**
  - 10 NWP atmospheric features
  - `predicted_corrected_rainfall` (Output of Model 2)
  - `regime_idx` (Integer code from Model 1)
  - `lead_time_hours` (Forecast lead time)
- **Test Metrics:**
  - ROC-AUC: **0.942**
  - Brier Score: **0.082** (Well-calibrated probabilities)
  - Critical Success Index (CSI): **0.68** (vs raw NWP: 0.42)
  - Probability of Detection (POD): **0.81** (vs raw NWP: 0.58)
  - False Alarm Ratio (FAR): **0.19** (vs raw NWP: 0.38)

---

## 5. Model Loading & Verification Code

Models are loaded via `InferenceEngine.load_models(models_dir)` in `backend/app/ml/inference.py`:

```python
from app.ml.inference import inference_engine
is_loaded = inference_engine.load_models("backend/models")
assert is_loaded is True
```

If model files are ever deleted, the engine gracefully falls back to meteorological baseline calculations without crashing the service.
