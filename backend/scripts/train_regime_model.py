"""
VARSHAAI — Train Model 1: Weather Regime Multiclass Classifier
SIH 26080
"""

import os
import sys
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.ml.preprocessing import load_dataset, chronological_split
from app.ml.regime_classifier import train_regime_classifier

def main():
    data_path = os.path.join(BASE_DIR, "data", "SIH26080_10000_training_dataset.csv")
    models_dir = os.path.join(BASE_DIR, "models")
    os.makedirs(models_dir, exist_ok=True)

    print("Loading data...")
    df = load_dataset(data_path)
    train_df, val_df, _ = chronological_split(df)

    print("Training regime classifier...")
    model, metrics = train_regime_classifier(train_df, val_df)
    print(f"Accuracy: {metrics['accuracy']:.4f} | F1: {metrics['f1']:.4f}")

    joblib.dump(model, os.path.join(models_dir, "regime_classifier.joblib"))
    print("Saved regime_classifier.joblib")

if __name__ == "__main__":
    main()
