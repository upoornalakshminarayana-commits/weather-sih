"""
VARSHAAI — Model Metrics & Feature Importance Endpoints
"""

from fastapi import APIRouter
from app.services.verification_service import verification_service

router = APIRouter(prefix="/api/model", tags=["Model"])

@router.get("/metrics")
def get_model_metrics():
    """Retrieve full test-set evaluation metrics for all trained models."""
    return verification_service.get_metrics()

@router.get("/feature-importance")
def get_feature_importance():
    """Retrieve genuine model feature importance weights."""
    return verification_service.get_feature_importance()
