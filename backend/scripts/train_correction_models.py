"""
VARSHAAI — Train Model 2: Six Regime-Aware Rainfall Correctors
SIH 26080
"""

import os
import sys
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.ml.preprocessing import load_dataset, chronological_split
from app.ml.rainfall_corrector import train_regime_specific_correctors

def main():
    data_path = os.path.join(BASE_DIR, "data", "SIH26080_10000_training_dataset.csv")
    models_dir = os.path.join(BASE_DIR, "models")
    os.makedirs(models_dir, exist_ok=True)

    print("Loading data...")
    df = load_dataset(data_path)
    train_df, val_df, _ = chronological_split(df)

    print("Training 6 regime-specific regressors + global baseline...")
    models, metrics, global_m, _ = train_regime_specific_correctors(train_df, val_df)

    for k, m in models.items():
        out_path = os.path.join(models_dir, f"{k}_corrector.joblib")
        joblib.dump(m, out_path)
        print(f"Saved {k}_corrector.joblib (RMSE: {metrics[k]['rmse']} mm)")

    joblib.dump(global_m, os.path.join(models_dir, "global_corrector.joblib"))
    print("Saved global_corrector.joblib")

if __name__ == "__main__":
    main()
