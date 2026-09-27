"""
VARSHAAI — Regime-Aware Rainfall Bias Correction Models
SIH 26080: Model 2
Target: observed_rainfall_mm

Trains six dedicated regressors for each weather regime,
plus a single global bias correction baseline.
"""

import os
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
import joblib

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from app.ml.features import (
    CORRECTION_MODEL_FEATURES,
    REGIME_MAPPING,
    REVERSE_REGIME_MAPPING
)

def create_regressor():
    """Create XGBoost Regressor with HistGradient/RandomForest fallback."""
    try:
        import xgboost as xgb
        return xgb.XGBRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.07,
            subsample=0.85,
            colsample_bytree=0.85,
            random_state=42
        )
    except (ImportError, Exception):
        from sklearn.ensemble import HistGradientBoostingRegressor
        return HistGradientBoostingRegressor(
            max_iter=100,
            max_depth=6,
            learning_rate=0.07,
            random_state=42
        )

def train_regime_specific_correctors(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame
) -> Tuple[Dict[str, Any], Dict[str, Any], Any, Dict[str, Any]]:
    """
    Train 6 regime-specific regressors + 1 global baseline regressor.
    """
    models = {}
    metrics_per_regime = {}

    # 1. Global Baseline Regressor (All regimes combined)
    global_model = create_regressor()
    global_model.fit(train_df[CORRECTION_MODEL_FEATURES], train_df["observed_rainfall_mm"])
    global_preds = global_model.predict(val_df[CORRECTION_MODEL_FEATURES])
    global_mae = float(mean_absolute_error(val_df["observed_rainfall_mm"], global_preds))
    global_rmse = float(np.sqrt(mean_squared_error(val_df["observed_rainfall_mm"], global_preds)))
    global_bias = float(np.mean(global_preds - val_df["observed_rainfall_mm"]))
    global_r2 = float(r2_score(val_df["observed_rainfall_mm"], global_preds))

    global_metrics = {
        "mae": round(global_mae, 3),
        "rmse": round(global_rmse, 3),
        "bias": round(global_bias, 3),
        "r2": round(global_r2, 4)
    }

    # 2. Six Regime-Specific Regressors
    for regime_key, idx in REGIME_MAPPING.items():
        regime_train = train_df[train_df["regime_idx"] == idx]
        regime_val = val_df[val_df["regime_idx"] == idx]

        if len(regime_train) < 30:
            # Fallback to global if regime partition too small
            regime_train = train_df

        model = create_regressor()
        model.fit(regime_train[CORRECTION_MODEL_FEATURES], regime_train["observed_rainfall_mm"])
        models[regime_key] = model

        if len(regime_val) > 0:
            preds = model.predict(regime_val[CORRECTION_MODEL_FEATURES])
            mae = float(mean_absolute_error(regime_val["observed_rainfall_mm"], preds))
            rmse = float(np.sqrt(mean_squared_error(regime_val["observed_rainfall_mm"], preds)))
            bias = float(np.mean(preds - regime_val["observed_rainfall_mm"]))
            r2 = float(r2_score(regime_val["observed_rainfall_mm"], preds))
        else:
            mae, rmse, bias, r2 = global_mae, global_rmse, global_bias, global_r2

        # Feature importances
        fi = {}
        if hasattr(model, "feature_importances_"):
            for f, imp in zip(CORRECTION_MODEL_FEATURES, model.feature_importances_):
                fi[f] = round(float(imp), 4)

        metrics_per_regime[regime_key] = {
            "mae": round(mae, 3),
            "rmse": round(rmse, 3),
            "bias": round(bias, 3),
            "r2": round(r2, 4),
            "sample_count": len(regime_train),
            "feature_importance": fi
        }

    return models, metrics_per_regime, global_model, global_metrics

def predict_corrected_rainfall(
    models: Dict[str, Any],
    regime_key: str,
    input_features: pd.DataFrame
) -> float:
    """
    Select corresponding regime model and predict corrected rainfall.
    """
    model = models.get(regime_key, list(models.values())[0])
    X = input_features[CORRECTION_MODEL_FEATURES]
    pred = float(model.predict(X)[0])
    return max(0.0, round(pred, 1))
