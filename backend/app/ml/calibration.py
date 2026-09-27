"""
VARSHAAI — Probability Calibration & Categorical Scores
SIH 26080: Verification Utilities
"""

from typing import Dict, Any, List
import numpy as np
from sklearn.calibration import calibration_curve

def compute_calibration_curve(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 5
) -> Dict[str, List[float]]:
    """
    Compute reliability curve points (fraction of positives vs mean predicted value).
    """
    prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=n_bins, strategy="uniform")
    return {
        "fraction_of_positives": [round(float(x), 4) for x in prob_true],
        "mean_predicted_value": [round(float(x), 4) for x in prob_pred]
    }

def compute_categorical_scores(
    hits: int,
    fa: int,
    miss: int,
    cn: int
) -> Dict[str, float]:
    """
    Compute Critical Success Index (CSI), POD, FAR, and ETS.
    """
    total = hits + fa + miss + cn
    pod = float(hits / (hits + miss)) if (hits + miss) > 0 else 0.0
    far = float(fa / (hits + fa)) if (hits + fa) > 0 else 0.0
    csi = float(hits / (hits + fa + miss)) if (hits + fa + miss) > 0 else 0.0

    ar = ((hits + fa) * (hits + miss)) / total if total > 0 else 0.0
    ets = float((hits - ar) / (hits + fa + miss - ar)) if (hits + fa + miss - ar) > 0 else 0.0

    return {
        "pod": round(pod, 4),
        "far": round(far, 4),
        "csi": round(csi, 4),
        "ets": round(ets, 4)
    }
