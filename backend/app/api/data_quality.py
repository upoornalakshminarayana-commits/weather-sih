"""
VARSHAAI — Data Quality Audit API Endpoint
"""

from fastapi import APIRouter
from app.schemas import DataQualityResponse
from app.services.data_service import data_service

router = APIRouter(prefix="/api", tags=["Data Quality"])

@router.get("/data-quality", response_model=DataQualityResponse)
def get_data_quality_report():
    """Retrieve actual data audit stats (missing values, duplicates, coordinate bounds, clean %)."""
    return data_service.get_data_quality_report()
