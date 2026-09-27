"""
VARSHAAI — Weather Regime Intelligence Endpoints
"""

from fastapi import APIRouter
from app.services.forecast_service import forecast_service

router = APIRouter(prefix="/api", tags=["Regime"])

@router.get("/regime/{record_id}")
def get_regime_for_record(record_id: str):
    """Retrieve weather regime prediction and probability breakdown for a record."""
    pred = forecast_service.get_forecast_for_record(record_id)
    return {
        "record_id": record_id,
        "regime": pred["predicted_regime"],
        "regime_key": pred["regime_key"],
        "confidence": pred["regime_confidence"],
        "class_probabilities": pred["class_probabilities"]
    }
