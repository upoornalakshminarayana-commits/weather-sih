"""
VARSHAAI — Train Model 3: Calibrated Heavy Rain Probability Model
SIH 26080
"""

import os
import sys
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.ml.preprocessing import load_dataset, chronological_split
from app.ml.heavy_rain_model import train_heavy_rain_classifier

def main():
    data_path = os.path.join(BASE_DIR, "data", "SIH26080_10000_training_dataset.csv")
    models_dir = os.path.join(BASE_DIR, "models")
    os.makedirs(models_dir, exist_ok=True)

    print("Loading data...")
    df = load_dataset(data_path)
    train_df, val_df, _ = chronological_split(df)

    # Augment with predicted rainfall estimate
    train_df["predicted_corrected_rainfall"] = train_df["nwp_rainfall_mm"]
    val_df["predicted_corrected_rainfall"] = val_df["nwp_rainfall_mm"]

    print("Training calibrated heavy rain classifier...")
    model, metrics = train_heavy_rain_classifier(train_df, val_df)
    print(f"ROC-AUC: {metrics['roc_auc']:.4f} | Brier: {metrics['brier_score']:.4f}")

    joblib.dump(model, os.path.join(models_dir, "heavy_rain_classifier.joblib"))
    print("Saved heavy_rain_classifier.joblib")

if __name__ == "__main__":
    main()
