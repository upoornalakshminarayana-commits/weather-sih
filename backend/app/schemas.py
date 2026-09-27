"""
VARSHAAI — Pydantic Schemas for API Requests & Responses
SIH 26080: Data Transfer Objects
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class PredictionRequest(BaseModel):
    nwp_rainfall_mm: float = Field(..., description="Raw NWP model rainfall forecast (mm)")
    ensemble_mean_mm: float = Field(..., description="Ensemble mean rainfall (mm)")
    ensemble_std_mm: float = Field(..., description="Ensemble spread/standard deviation (mm)")
    ensemble_min_mm: float = Field(..., description="Ensemble minimum member rainfall (mm)")
    ensemble_max_mm: float = Field(..., description="Ensemble maximum member rainfall (mm)")
    temperature_c: float = Field(..., description="Surface temperature (°C)")
    relative_humidity_pct: float = Field(..., description="Relative humidity (%)")
    surface_pressure_hpa: float = Field(..., description="Surface barometric pressure (hPa)")
    wind_u_ms: float = Field(..., description="Zonal wind velocity U (m/s)")
    wind_v_ms: float = Field(..., description="Meridional wind velocity V (m/s)")
    latitude: float = Field(..., description="Latitude (°N)")
    longitude: float = Field(..., description="Longitude (°E)")
    elevation_m: float = Field(..., description="Surface elevation above sea level (m)")
    coastal_distance_km: float = Field(..., description="Distance from coastline (km)")
    lead_time_hours: int = Field(24, description="Forecast lead time (hours)")

class PredictionResponse(BaseModel):
    predicted_regime: str
    regime_key: str
    regime_confidence: float
    class_probabilities: Dict[str, float]
    raw_nwp_rainfall_mm: float
    corrected_rainfall_mm: float
    ai_adjustment_mm: float
    heavy_rain_probability: float
    heavy_rain_threshold_mm: float
    risk_category: str
    model_version: str
    is_real_model: bool
    explanation: str

class JourneyStep(BaseModel):
    step_number: int
    step_title: str
    badge: str
    content: Dict[str, Any]
    explanation: str

class ForecastJourneyResponse(BaseModel):
    record_id: str
    district: str
    region: str
    lead_time_hours: int
    is_real_model: bool
    steps: List[JourneyStep]

class HealthResponse(BaseModel):
    status: str
    is_models_loaded: bool
    model_version: str
    dataset_status: str
    device: str

class DataQualityResponse(BaseModel):
    total_records: int
    missing_values: int
    duplicate_records: int
    invalid_coordinates: int
    negative_rainfall_count: int
    valid_percentage: float
    provenance_status: str
