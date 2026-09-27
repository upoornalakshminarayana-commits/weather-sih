"""
VARSHAAI — Anti-Leakage Feature Registry
SIH 26080: Regime-Aware AI Post-Processing of Monsoon Rainfall Forecasts

This registry strictly defines feature sets for each model stage to guarantee:
1. No predictive target leakage (e.g. observed_rainfall_mm never used in prediction).
2. Regime-specific models do not contain weather_regime as a feature (the model IS the regime).
3. The heavy rain classifier properly ingests predicted_corrected_rainfall and predicted_regime.
"""

from typing import List, Dict

# Standard regime keys and their display labels
REGIME_MAPPING: Dict[str, int] = {
    "active_monsoon": 0,
    "break_monsoon": 1,
    "monsoon_low_depression": 2,
    "coastal_rainfall": 3,
    "orographic_rainfall": 4,
    "western_disturbance": 5
}

REVERSE_REGIME_MAPPING: Dict[int, str] = {v: k for k, v in REGIME_MAPPING.items()}

# Human readable display names
REGIME_DISPLAY_NAMES: Dict[str, str] = {
    "active_monsoon": "Active Monsoon",
    "break_monsoon": "Break Monsoon",
    "monsoon_low_depression": "Monsoon Low / Depression",
    "coastal_rainfall": "Coastal Rainfall",
    "orographic_rainfall": "Orographic Rainfall",
    "western_disturbance": "Western Disturbance"
}

def normalize_regime_name(name: str) -> str:
    """Normalize arbitrary regime strings from dataset into standard keys."""
    clean = str(name).strip().lower().replace("/", " ").replace("-", " ")
    if "active" in clean:
        return "active_monsoon"
    if "break" in clean:
        return "break_monsoon"
    if "low" in clean or "depression" in clean:
        return "monsoon_low_depression"
    if "coast" in clean:
        return "coastal_rainfall"
    if "orog" in clean:
        return "orographic_rainfall"
    if "western" in clean or "wd" in clean:
        return "western_disturbance"
    return "active_monsoon"

# 1. MODEL 1: REGIME CLASSIFIER INPUT FEATURES (15 features)
# Target: weather_regime (multiclass 0..5)
# STRICTLY NO: observed_rainfall_mm, regime_aware_corrected_rainfall_mm, heavy_rain_event
REGIME_CLASSIFIER_FEATURES: List[str] = [
    "temperature_c",
    "relative_humidity_pct",
    "surface_pressure_hpa",
    "wind_u_ms",
    "wind_v_ms",
    "nwp_rainfall_mm",
    "ensemble_mean_mm",
    "ensemble_std_mm",
    "ensemble_min_mm",
    "ensemble_max_mm",
    "latitude",
    "longitude",
    "elevation_m",
    "coastal_distance_km",
    "lead_time_hours"
]

# 2. MODEL 2: REGIME-AWARE RAINFALL CORRECTION FEATURES (15 features)
# Target: observed_rainfall_mm (continuous regression)
# Applied independently per regime. No weather_regime input, no observed_rainfall_mm input.
CORRECTION_MODEL_FEATURES: List[str] = [
    "nwp_rainfall_mm",
    "ensemble_mean_mm",
    "ensemble_std_mm",
    "ensemble_min_mm",
    "ensemble_max_mm",
    "temperature_c",
    "relative_humidity_pct",
    "surface_pressure_hpa",
    "wind_u_ms",
    "wind_v_ms",
    "latitude",
    "longitude",
    "elevation_m",
    "coastal_distance_km",
    "lead_time_hours"
]

# 3. MODEL 3: HEAVY RAINFALL PROBABILITY FEATURES
# Target: heavy_rain_event (binary 0 or 1)
# Base features + predicted_corrected_rainfall + one-hot encoded regime
HEAVY_RAIN_BASE_FEATURES: List[str] = [
    "nwp_rainfall_mm",
    "ensemble_mean_mm",
    "ensemble_std_mm",
    "ensemble_min_mm",
    "ensemble_max_mm",
    "temperature_c",
    "relative_humidity_pct",
    "surface_pressure_hpa",
    "wind_u_ms",
    "wind_v_ms",
    "latitude",
    "longitude",
    "elevation_m",
    "coastal_distance_km",
    "lead_time_hours"
]

# When training Model 3, we append:
# 'predicted_corrected_rainfall'
# 'regime_idx' (or one-hot encoded regimes)
HEAVY_RAIN_MODEL_FEATURES: List[str] = HEAVY_RAIN_BASE_FEATURES + [
    "predicted_corrected_rainfall",
    "regime_idx"
]
