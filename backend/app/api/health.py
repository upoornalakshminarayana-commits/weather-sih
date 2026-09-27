"""
VARSHAAI — Health Check & Model Status API
"""

from fastapi import APIRouter
from app.schemas import HealthResponse
from app.ml.inference import inference_engine

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health_check():
    return {
        "status": "healthy",
        "is_models_loaded": inference_engine.is_loaded,
        "model_version": inference_engine.model_version.get("version", "0.1.0-prototype"),
        "dataset_status": "Prototype Dataset (SIH 26080) — Ready for NCMRWF / IMD Live Ingestion",
        "device": "cpu"
    }
