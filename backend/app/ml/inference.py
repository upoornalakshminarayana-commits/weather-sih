"""
VARSHAAI — End-to-End ML Inference Engine
SIH 26080: Runtime Prediction Service
"""

import os
import json
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
import joblib

from app.ml.features import (
    REGIME_CLASSIFIER_FEATURES,
    CORRECTION_MODEL_FEATURES,
    HEAVY_RAIN_MODEL_FEATURES,
    REGIME_MAPPING,
    REGIME_DISPLAY_NAMES
)
from app.ml.regime_classifier import predict_regime
from app.ml.rainfall_corrector import predict_corrected_rainfall
from app.ml.heavy_rain_model import predict_heavy_rain_probability

class InferenceEngine:
    def __init__(self, models_dir: Optional[str] = None):
        if models_dir is None:
            models_dir = os.path.join(os.path.dirname(__file__), "..", "..", "models")
        self.models_dir = os.path.abspath(models_dir)
        self.regime_model = None
        self.regime_correctors = {}
        self.heavy_rain_model = None
        self.global_corrector = None
        self.metrics = {}
        self.feature_importance = {}
        self.model_version = {}
        self.is_loaded = False

    def load_models(self, models_dir: Optional[str] = None) -> bool:
        """Load all serialized .joblib models and metadata."""
        if models_dir:
            self.models_dir = os.path.abspath(models_dir)
        try:
            regime_path = os.path.join(self.models_dir, "regime_classifier.joblib")
            if os.path.exists(regime_path):
                self.regime_model = joblib.load(regime_path)

            for key in REGIME_MAPPING.keys():
                corr_path = os.path.join(self.models_dir, f"{key}_corrector.joblib")
                if os.path.exists(corr_path):
                    self.regime_correctors[key] = joblib.load(corr_path)

            global_path = os.path.join(self.models_dir, "global_corrector.joblib")
            if os.path.exists(global_path):
                self.global_corrector = joblib.load(global_path)

            heavy_path = os.path.join(self.models_dir, "heavy_rain_classifier.joblib")
            if os.path.exists(heavy_path):
                self.heavy_rain_model = joblib.load(heavy_path)

            # Metadata files
            metrics_path = os.path.join(self.models_dir, "metrics.json")
            if os.path.exists(metrics_path):
                with open(metrics_path, "r", encoding="utf-8") as f:
                    self.metrics = json.load(f)

            feat_path = os.path.join(self.models_dir, "feature_importance.json")
            if os.path.exists(feat_path):
                with open(feat_path, "r", encoding="utf-8") as f:
                    self.feature_importance = json.load(f)

            version_path = os.path.join(self.models_dir, "model_version.json")
            if os.path.exists(version_path):
                with open(version_path, "r", encoding="utf-8") as f:
                    self.model_version = json.load(f)

            self.is_loaded = (
                self.regime_model is not None and
                len(self.regime_correctors) > 0 and
                self.heavy_rain_model is not None
            )
            return self.is_loaded
        except Exception as e:
            print(f"Error loading models from {self.models_dir}: {e}")
            self.is_loaded = False
            return False

    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute full inference pipeline:
        NWP Input -> Regime Classifier -> Regime Corrector -> Heavy Rain Probability.
        """
        df = pd.DataFrame([input_data])

        # Ensure all features exist with defaults
        all_needed = list(set(REGIME_CLASSIFIER_FEATURES + CORRECTION_MODEL_FEATURES))
        for col in all_needed:
            if col not in df.columns:
                df[col] = 0.0
            else:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        raw_nwp = float(df["nwp_rainfall_mm"].iloc[0])

        if not self.is_loaded:
            # Fallback heuristic if models not loaded yet
            regime_key = "active_monsoon"
            corrected = max(0.0, round(raw_nwp * 1.05, 1))
            prob = 0.75 if corrected >= 64.5 else 0.15
            return {
                "predicted_regime": REGIME_DISPLAY_NAMES[regime_key],
                "regime_key": regime_key,
                "regime_confidence": 0.85,
                "class_probabilities": {},
                "raw_nwp_rainfall_mm": raw_nwp,
                "corrected_rainfall_mm": corrected,
                "ai_adjustment_mm": round(corrected - raw_nwp, 1),
                "heavy_rain_probability": prob,
                "heavy_rain_threshold_mm": 64.5,
                "risk_category": "Red Alert (Very High Risk)" if prob >= 0.75 else "Green (Low Risk)",
                "model_version": "0.1.0-prototype",
                "is_real_model": False,
                "explanation": "Models not loaded; fallback demo calculation."
            }

        # 1. Weather Regime Classification
        regime_res = predict_regime(self.regime_model, df)
        regime_key = regime_res["regime_key"]
        regime_display = regime_res["regime_display"]
        regime_conf = regime_res["confidence"]

        # 2. Select Regime Model & Predict Corrected Rainfall
        corrected_rain = predict_corrected_rainfall(self.regime_correctors, regime_key, df)
        ai_adj = round(corrected_rain - raw_nwp, 1)

        # 3. Augment with predicted rainfall and regime index for Heavy Rain Classifier
        df["predicted_corrected_rainfall"] = corrected_rain
        df["regime_idx"] = REGIME_MAPPING.get(regime_key, 0)

        # 4. Heavy Rain Probability Prediction
        heavy_res = predict_heavy_rain_probability(self.heavy_rain_model, df)

        # 5. Scientific physical explanation
        if ai_adj > 0:
            exp = (
                f"Under the {regime_display} regime, physical NWP models systematically underestimate "
                f"intense boundary-layer moisture convergence. The regime-specific regressor adjusted "
                f"the prediction from {raw_nwp} mm to {corrected_rain} mm (+{ai_adj} mm)."
            )
        elif ai_adj < 0:
            exp = (
                f"Under the {regime_display} regime, raw NWP simulations often overestimate light drizzle. "
                f"The regime-specific model attenuated the forecast by {abs(ai_adj)} mm."
            )
        else:
            exp = f"Raw NWP physics aligns with empirical regime distributions; minimal bias adjustment applied."

        return {
            "predicted_regime": regime_display,
            "regime_key": regime_key,
            "regime_confidence": regime_conf,
            "class_probabilities": regime_res["class_probabilities"],
            "raw_nwp_rainfall_mm": raw_nwp,
            "corrected_rainfall_mm": corrected_rain,
            "ai_adjustment_mm": ai_adj,
            "heavy_rain_probability": heavy_res["heavy_rain_probability"],
            "heavy_rain_threshold_mm": 64.5,
            "risk_category": heavy_res["risk_category"],
            "model_version": self.model_version.get("version", "0.1.0-prototype"),
            "is_real_model": True,
            "explanation": exp
        }

# Global singleton
inference_engine = InferenceEngine()
