"""
VARSHAAI — Heavy Rain Hazard & Risk Endpoints
"""

from fastapi import APIRouter
from app.services.forecast_service import forecast_service

router = APIRouter(prefix="/api", tags=["Risk"])

@router.get("/risk/{record_id}")
def get_risk_for_record(record_id: str):
    """Retrieve calibrated heavy rain exceedance probability and risk categorization."""
    pred = forecast_service.get_forecast_for_record(record_id)
    return {
        "record_id": record_id,
        "heavy_rain_probability": pred["heavy_rain_probability"],
        "threshold_mm": pred["heavy_rain_threshold_mm"],
        "risk_category": pred["risk_category"],
        "raw_nwp_rainfall_mm": pred["raw_nwp_rainfall_mm"],
        "corrected_rainfall_mm": pred["corrected_rainfall_mm"]
    }
