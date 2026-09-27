"""
VARSHAAI — Data Ingestion & Quality Audit Service
SIH 26080: Prototype Dataset Indexer
"""

import os
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List

from app.config import settings
from app.ml.preprocessing import load_dataset

class DataService:
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.records_dict: Dict[str, Dict[str, Any]] = {}
        self.is_loaded = False
        self._load()

    def _load(self):
        try:
            self.df = load_dataset(settings.DATASET_PATH)
            # Index by record_id
            for _, row in self.df.iterrows():
                rec_id = str(row.get("record_id", f"REC_{len(self.records_dict)}"))
                self.records_dict[rec_id] = row.to_dict()
            self.is_loaded = True
        except Exception as e:
            print(f"DataService: Warning, could not load dataset from {settings.DATASET_PATH}: {e}")
            self.is_loaded = False

    def get_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        return self.records_dict.get(record_id)

    def get_data_quality_report(self) -> Dict[str, Any]:
        if self.df is None or len(self.df) == 0:
            return {
                "total_records": 0,
                "missing_values": 0,
                "duplicate_records": 0,
                "invalid_coordinates": 0,
                "negative_rainfall_count": 0,
                "valid_percentage": 0.0,
                "provenance_status": "Prototype Dataset (Disconnected)"
            }

        df = self.df
        total = len(df)
        missing = int(df.isna().sum().sum())
        duplicates = int(df.duplicated(subset=["latitude", "longitude", "valid_time"]).sum()) if "valid_time" in df.columns else 0
        invalid_coords = int(((df["latitude"] < 6.0) | (df["latitude"] > 38.0) | (df["longitude"] < 68.0) | (df["longitude"] > 98.0)).sum())
        negative_rain = int((df["nwp_rainfall_mm"] < 0).sum() + (df.get("observed_rainfall_mm", 0) < 0).sum())

        clean_pct = round(float(((total - (duplicates + invalid_coords + negative_rain)) / total) * 100), 2)

        return {
            "total_records": total,
            "missing_values": missing,
            "duplicate_records": duplicates,
            "invalid_coordinates": invalid_coords,
            "negative_rainfall_count": negative_rain,
            "valid_percentage": max(0.0, clean_pct),
            "provenance_status": "Prototype Dataset — Ready for NCMRWF NEPS-G & IMD Integration"
        }

data_service = DataService()
