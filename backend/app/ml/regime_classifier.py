"""
VARSHAAI — Weather Regime Multiclass Classifier
SIH 26080: Model 1
Target: weather_regime (active_monsoon, break_monsoon, monsoon_low_depression,
coastal_rainfall, orographic_rainfall, western_disturbance)
"""

import os
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
import joblib

from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from app.ml.features import (
    REGIME_CLASSIFIER_FEATURES,
    REGIME_MAPPING,
    REVERSE_REGIME_MAPPING,
    REGIME_DISPLAY_NAMES
)

def create_regime_classifier():
    """Create XGBoost classifier with RandomForest/HistGradient fallback."""
    try:
        import xgboost as xgb
        return xgb.XGBClassifier(
            n_estimators=120,
            max_depth=5,
            learning_rate=0.08,
            objective="multi:softprob",
            num_class=6,
            random_state=42,
            eval_metric="mlogloss"
        )
    except (ImportError, Exception):
        from sklearn.ensemble import HistGradientBoostingClassifier
        return HistGradientBoostingClassifier(
            max_iter=120,
            max_depth=6,
            learning_rate=0.08,
            random_state=42
        )

def train_regime_classifier(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame
) -> Tuple[Any, Dict[str, Any]]:
    """
    Train weather regime classifier on anti-leakage atmospheric features.
    """
    X_train = train_df[REGIME_CLASSIFIER_FEATURES]
    y_train = train_df["regime_idx"]

    X_val = val_df[REGIME_CLASSIFIER_FEATURES]
    y_val = val_df["regime_idx"]

    model = create_regime_classifier()
    model.fit(X_train, y_train)

    # Evaluate on validation set
    y_pred = model.predict(X_val)
    acc = float(accuracy_score(y_val, y_pred))
    prec, rec, f1, _ = precision_recall_fscore_support(y_val, y_pred, average="weighted", zero_division=0)
    cm = confusion_matrix(y_val, y_pred).tolist()

    # Feature importances
    feature_importance = {}
    if hasattr(model, "feature_importances_"):
        for feat, imp in zip(REGIME_CLASSIFIER_FEATURES, model.feature_importances_):
            feature_importance[feat] = float(imp)
    elif hasattr(model, "coef_"):
        for feat, imp in zip(REGIME_CLASSIFIER_FEATURES, np.abs(model.coef_).mean(axis=0)):
            feature_importance[feat] = float(imp)
    else:
        # Default uniform
        for feat in REGIME_CLASSIFIER_FEATURES:
            feature_importance[feat] = 1.0 / len(REGIME_CLASSIFIER_FEATURES)

    metrics = {
        "accuracy": round(acc, 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1": round(float(f1), 4),
        "confusion_matrix": cm,
        "feature_importance": feature_importance
    }

    return model, metrics

def predict_regime(model: Any, input_features: pd.DataFrame) -> Dict[str, Any]:
    """
    Predict regime, confidence, and class probability distribution.
    """
    X = input_features[REGIME_CLASSIFIER_FEATURES]
    probs = model.predict_proba(X)[0]
    best_idx = int(np.argmax(probs))
    confidence = float(probs[best_idx])

    regime_key = REVERSE_REGIME_MAPPING.get(best_idx, "active_monsoon")
    display_name = REGIME_DISPLAY_NAMES.get(regime_key, regime_key)

    class_probabilities = {
        REGIME_DISPLAY_NAMES.get(REVERSE_REGIME_MAPPING[i], str(i)): round(float(probs[i]), 4)
        for i in range(len(probs))
    }

    return {
        "regime_key": regime_key,
        "regime_display": display_name,
        "confidence": round(confidence, 4),
        "class_probabilities": class_probabilities
    }
