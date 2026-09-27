"""
VARSHAAI — Data Preprocessing & Chronological Splitting
SIH 26080: Regime-Aware AI Post-Processing of Monsoon Rainfall Forecasts
"""

import os
from typing import Tuple, Dict, Any
import pandas as pd
import numpy as np

from app.ml.features import (
    REGIME_CLASSIFIER_FEATURES,
    CORRECTION_MODEL_FEATURES,
    HEAVY_RAIN_BASE_FEATURES,
    REGIME_MAPPING,
    normalize_regime_name
)

def load_dataset(file_path: str) -> pd.DataFrame:
    """
    Load dataset from CSV or XLSX with schema validation.
    """
    if not os.path.exists(file_path):
        # Check alternative locations
        alt_paths = [
            file_path,
            os.path.join(os.path.dirname(__file__), "..", "..", "data", "SIH26080_10000_training_dataset.csv"),
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "SIH26080_10000_training_dataset.csv"),
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "SIH26080_10000_training_dataset (1).xlsx")
        ]
        for p in alt_paths:
            if os.path.exists(p):
                file_path = p
                break

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset not found at {file_path}")

    if file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path)

    # Standardize column names
    df.columns = [c.strip().lower() for c in df.columns]

    # Normalize weather regime column
    if "weather_regime" in df.columns:
        df["weather_regime_norm"] = df["weather_regime"].apply(normalize_regime_name)
        df["regime_idx"] = df["weather_regime_norm"].map(REGIME_MAPPING)

    # Cast numeric columns
    numeric_cols = list(set(REGIME_CLASSIFIER_FEATURES + CORRECTION_MODEL_FEATURES + [
        "observed_rainfall_mm", "heavy_rain_event"
    ]))
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # Ensure heavy rain event binary
    if "heavy_rain_event" not in df.columns or df["heavy_rain_event"].isna().all():
        df["heavy_rain_event"] = (df["observed_rainfall_mm"] >= 64.5).astype(int)
    else:
        df["heavy_rain_event"] = df["heavy_rain_event"].astype(int)

    # Parse and sort chronologically by valid_time
    if "valid_time" in df.columns:
        df["valid_time_dt"] = pd.to_datetime(df["valid_time"], errors="coerce")
        df = df.sort_values(by="valid_time_dt").reset_index(drop=True)

    return df

def chronological_split(
    df: pd.DataFrame,
    train_pct: float = 0.70,
    val_pct: float = 0.15,
    test_pct: float = 0.15
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Chronological Train / Validation / Test split.
    Prevents future data leakage into historical evaluation.
    """
    n = len(df)
    train_end = int(n * train_pct)
    val_end = int(n * (train_pct + val_pct))

    train_df = df.iloc[:train_end].copy().reset_index(drop=True)
    val_df = df.iloc[train_end:val_end].copy().reset_index(drop=True)
    test_df = df.iloc[val_end:].copy().reset_index(drop=True)

    return train_df, val_df, test_df
