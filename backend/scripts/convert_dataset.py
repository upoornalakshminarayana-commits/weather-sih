"""
VARSHAAI — Convert Prototype Excel Dataset to CSV
SIH 26080
"""

import os
import pandas as pd

def convert():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    root_dir = os.path.dirname(base_dir)

    xlsx_path = os.path.join(root_dir, "SIH26080_10000_training_dataset (1).xlsx")
    csv_out_root = os.path.join(root_dir, "SIH26080_10000_training_dataset.csv")
    csv_out_data = os.path.join(base_dir, "data", "SIH26080_10000_training_dataset.csv")

    if os.path.exists(xlsx_path):
        print(f"Reading {xlsx_path}...")
        df = pd.read_excel(xlsx_path)
        os.makedirs(os.path.dirname(csv_out_data), exist_ok=True)
        df.to_csv(csv_out_root, index=False)
        df.to_csv(csv_out_data, index=False)
        print(f"Successfully converted:\n  - {csv_out_root}\n  - {csv_out_data}")
        print("-" * 50)
        print(f"Row count: {len(df)}")
        print(f"Column count: {len(df.columns)}")
        print(f"Duplicate count: {df.duplicated().sum()}")
        print(f"Missing-value count: {df.isna().sum().sum()}")
        print("-" * 50)
    else:
        print(f"Excel file not found at {xlsx_path}")

if __name__ == "__main__":
    convert()
