"""
VARSHAAI — Forecast & Inference Endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.schemas import PredictionRequest, PredictionResponse, ForecastJourneyResponse
from app.ml.inference import inference_engine
from app.services.forecast_service import forecast_service

router = APIRouter(prefix="/api", tags=["Forecast"])

@router.post("/predict", response_model=PredictionResponse)
def predict_rainfall(request: PredictionRequest):
    """
    Real-time inference using trained XGBoost ML models:
    1. Multiclass Regime Classifier
    2. Regime-Specific Bias Corrector
    3. Calibrated Heavy Rain Probability Classifier
    """
    input_data = request.model_dump()
    result = inference_engine.predict(input_data)
    return result

@router.get("/forecast/{record_id}", response_model=PredictionResponse)
def get_forecast_record(record_id: str):
    """Get forecast and real ML predictions for a specific dataset record."""
    result = forecast_service.get_forecast_for_record(record_id)
    return result

@router.get("/forecast-journey/{record_id}", response_model=ForecastJourneyResponse)
def get_forecast_journey_endpoint(record_id: str):
    """
    Get the 7-Step Forecast Journey driven by real ML model outputs.
    Powers varshaJourney.js directly.
    """
    return forecast_service.get_forecast_journey(record_id)
