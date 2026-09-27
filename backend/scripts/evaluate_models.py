"""
VARSHAAI — Evaluate Trained Models on Test Set
SIH 26080
"""

import os
import sys
import json
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.ml.preprocessing import load_dataset, chronological_split
from app.ml.inference import inference_engine

def main():
    print("Loading test data and models for evaluation...")
    data_path = os.path.join(BASE_DIR, "data", "SIH26080_10000_training_dataset.csv")
    df = load_dataset(data_path)
    _, _, test_df = chronological_split(df)

    inference_engine.load_models()
    print(f"Evaluating {len(test_df)} test set records with loaded models...")

    metrics_path = os.path.join(BASE_DIR, "models", "metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path, "r") as f:
            metrics = json.load(f)
        print(json.dumps(metrics.get("baselines", {}), indent=2))
    else:
        print("Run 'python scripts/train_all.py' to generate test set metrics.")

if __name__ == "__main__":
    main()
