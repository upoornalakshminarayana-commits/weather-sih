"""
VARSHAAI — Verification Lab Endpoints
"""

from fastapi import APIRouter
from app.services.verification_service import verification_service

router = APIRouter(prefix="/api/verification", tags=["Verification"])

@router.get("")
def get_overall_verification():
    """Retrieve test-set verification metrics comparing NWP, Global Baseline, and Regime-Aware AI."""
    metrics = verification_service.get_metrics()
    return metrics.get("baselines", {})

@router.get("/by-regime")
def get_verification_by_regime():
    """Retrieve regime-wise error and skill statistics."""
    metrics = verification_service.get_metrics()
    return metrics.get("regime_wise", {})

@router.get("/by-lead-time")
def get_verification_by_lead_time():
    """Retrieve skill degradation metrics across lead times."""
    metrics = verification_service.get_metrics()
    return metrics.get("lead_time_wise", {})
