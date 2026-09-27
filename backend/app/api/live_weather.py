"""
VARSHAAI — Live Operational Weather API Endpoints
Serves real-time OpenWeatherMap & Tomorrow.io atmospheric feeds + live AI predictions.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict, Any

from app.services.live_weather_service import live_weather_service, INDIAN_CITIES

router = APIRouter(prefix="/api/live-weather", tags=["Live Weather"])

@router.get("")
def get_live_weather(
    lat: float = Query(17.68, description="Latitude (°N)"),
    lon: float = Query(83.21, description="Longitude (°E)"),
    provider: str = Query("openmeteo", description="API provider: 'openmeteo' (default, free), 'openweathermap', or 'tomorrow'")
):
    """
    Fetch real-time atmospheric conditions from Open-Meteo, OpenWeatherMap, or Tomorrow.io
    and immediately execute the trained XGBoost ML pipeline for live regime detection
    and regime-aware post-processing!
    """
    try:
        return live_weather_service.get_live_weather_and_ai_prediction(lat, lon, provider)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Live weather fetch failed: {str(e)}")

@router.get("/city/{city_name}")
def get_live_city_weather(
    city_name: str,
    provider: str = Query("openmeteo", description="API provider: 'openmeteo', 'openweathermap', or 'tomorrow'")
):
    """Fetch live weather & AI regime classification for a specific Indian city."""
    try:
        return live_weather_service.get_live_city(city_name, provider)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch live weather for {city_name}: {str(e)}")

@router.get("/cities-list")
def list_supported_cities():
    """List supported reference cities across India."""
    return list(INDIAN_CITIES.values())
