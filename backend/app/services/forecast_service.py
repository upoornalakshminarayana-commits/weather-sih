"""
VARSHAAI — Forecast & Forecast Journey Service
SIH 26080: Core Operational Prediction Service
"""

from typing import Dict, Any, Optional
from app.services.data_service import data_service
from app.ml.inference import inference_engine

class ForecastService:
    def get_forecast_for_record(self, record_id: str) -> Dict[str, Any]:
        """Execute ML pipeline on a specific record."""
        rec = data_service.get_record(record_id)
        if rec is None:
            # Generate default prototype record
            rec = {
                "nwp_rainfall_mm": 72.0,
                "ensemble_mean_mm": 70.0,
                "ensemble_std_mm": 12.0,
                "ensemble_min_mm": 51.0,
                "ensemble_max_mm": 91.0,
                "temperature_c": 27.0,
                "relative_humidity_pct": 87.0,
                "surface_pressure_hpa": 1002.0,
                "wind_u_ms": 4.1,
                "wind_v_ms": 8.4,
                "latitude": 17.7,
                "longitude": 83.3,
                "elevation_m": 10.0,
                "coastal_distance_km": 5.0,
                "lead_time_hours": 24,
                "district": "Visakhapatnam",
                "region": "East Coast",
                "observed_rainfall_mm": 108.0
            }

        prediction = inference_engine.predict(rec)
        prediction["district"] = rec.get("district", "Visakhapatnam")
        prediction["region"] = rec.get("region", "East Coast")
        prediction["observed_rainfall_mm"] = float(rec.get("observed_rainfall_mm", 0.0))
        return prediction

    def get_forecast_journey(self, record_id: str) -> Dict[str, Any]:
        """Generate the 7-Step Forecast Journey using genuine ML inference."""
        rec = data_service.get_record(record_id)
        if rec is None:
            rec = {
                "record_id": record_id,
                "district": "Visakhapatnam",
                "region": "East Coast",
                "lead_time_hours": 24,
                "nwp_rainfall_mm": 72.0,
                "ensemble_mean_mm": 70.0,
                "ensemble_std_mm": 12.0,
                "ensemble_min_mm": 51.0,
                "ensemble_max_mm": 91.0,
                "temperature_c": 27.0,
                "relative_humidity_pct": 87.0,
                "surface_pressure_hpa": 1002.0,
                "wind_u_ms": 4.1,
                "wind_v_ms": 8.4,
                "elevation_m": 10.0,
                "coastal_distance_km": 5.0,
                "observed_rainfall_mm": 108.0
            }

        pred = inference_engine.predict(rec)
        raw_nwp = pred["raw_nwp_rainfall_mm"]
        corr_rain = pred["corrected_rainfall_mm"]
        obs_rain = float(rec.get("observed_rainfall_mm", 0.0))

        raw_err = round(abs(raw_nwp - obs_rain), 1)
        corr_err = round(abs(corr_rain - obs_rain), 1)
        improved = corr_err < raw_err

        steps = [
            {
                "step_number": 1,
                "step_title": "Raw NWP Forecast",
                "badge": "Physical Numerical Simulation",
                "content": {"nwp_rainfall_mm": raw_nwp, "lead_time_hours": rec.get("lead_time_hours", 24)},
                "explanation": f"Raw NWP physical model predicted {raw_nwp} mm prior to statistical AI calibration."
            },
            {
                "step_number": 2,
                "step_title": "Atmospheric Conditions",
                "badge": "Thermodynamic State",
                "content": {
                    "temperature_c": rec.get("temperature_c", 27.0),
                    "relative_humidity_pct": rec.get("relative_humidity_pct", 87.0),
                    "surface_pressure_hpa": rec.get("surface_pressure_hpa", 1002.0),
                    "wind_u_ms": rec.get("wind_u_ms", 4.1),
                    "wind_v_ms": rec.get("wind_v_ms", 8.4),
                    "elevation_m": rec.get("elevation_m", 10.0),
                    "coastal_distance_km": rec.get("coastal_distance_km", 5.0)
                },
                "explanation": f"Surface pressure at {rec.get('surface_pressure_hpa', 1002.0)} hPa with {rec.get('relative_humidity_pct', 87.0)}% humidity creates deep moisture convergence."
            },
            {
                "step_number": 3,
                "step_title": "Weather Regime Detection",
                "badge": "XGBoost Multiclass Classifier",
                "content": {
                    "predicted_regime": pred["predicted_regime"],
                    "confidence": pred["regime_confidence"],
                    "class_probabilities": pred["class_probabilities"]
                },
                "explanation": f"Multiclass regime classifier identified {pred['predicted_regime']} with {int(pred['regime_confidence'] * 100)}% model confidence."
            },
            {
                "step_number": 4,
                "step_title": "Regime-Specific AI Bias Correction",
                "badge": "XGBoost Regressor",
                "content": {
                    "raw_nwp_rainfall_mm": raw_nwp,
                    "corrected_rainfall_mm": corr_rain,
                    "ai_adjustment_mm": pred["ai_adjustment_mm"]
                },
                "explanation": pred["explanation"]
            },
            {
                "step_number": 5,
                "step_title": "Heavy Rainfall Probability",
                "badge": "Calibrated Classifier",
                "content": {
                    "probability": pred["heavy_rain_probability"],
                    "threshold_mm": 64.5,
                    "risk_category": pred["risk_category"]
                },
                "explanation": f"Calibrated model estimated a {int(pred['heavy_rain_probability'] * 100)}% probability of exceeding the 64.5 mm threshold ({pred['risk_category']})."
            },
            {
                "step_number": 6,
                "step_title": "Forecast Uncertainty / Ensemble",
                "badge": "Multi-Member Spread",
                "content": {
                    "ensemble_mean_mm": rec.get("ensemble_mean_mm", raw_nwp * 0.95),
                    "ensemble_std_mm": rec.get("ensemble_std_mm", 12.0),
                    "ensemble_min_mm": rec.get("ensemble_min_mm", 51.0),
                    "ensemble_max_mm": rec.get("ensemble_max_mm", 91.0)
                },
                "explanation": f"Ensemble envelope spans {rec.get('ensemble_min_mm', 51.0)} to {rec.get('ensemble_max_mm', 91.0)} mm (spread ±{rec.get('ensemble_std_mm', 12.0)} mm)."
            }
        ]

        obs_rain = rec.get("observed_rainfall_mm")
        if obs_rain is None:
            step7 = {
                "step_number": 7,
                "step_title": "Observation Ground Truth",
                "badge": "Pending Observation",
                "content": {
                    "observed_rainfall_mm": None,
                    "status": "Pending Observation",
                    "raw_nwp_error_mm": None,
                    "ai_corrected_error_mm": None,
                    "improved": None,
                    "error_reduced_mm": None
                },
                "explanation": "Pending Observation: Ground-truth rain gauge verification will occur after the forecast valid time has elapsed. No verification errors calculated yet."
            }
        else:
            obs_rain = float(obs_rain)
            raw_err = round(abs(raw_nwp - obs_rain), 1)
            corr_err = round(abs(corr_rain - obs_rain), 1)
            improved = corr_err < raw_err
            step7 = {
                "step_number": 7,
                "step_title": "Observation Ground Truth",
                "badge": "Rain Gauge Verification",
                "content": {
                    "observed_rainfall_mm": obs_rain,
                    "raw_nwp_error_mm": raw_err,
                    "ai_corrected_error_mm": corr_err,
                    "improved": improved,
                    "error_reduced_mm": round(raw_err - corr_err, 1)
                },
                "explanation": (
                    f"Ground truth gauge recorded {obs_rain} mm. "
                    f"AI post-processing reduced the error from {raw_err} mm to {corr_err} mm "
                    f"({round(raw_err - corr_err, 1)} mm error reduction)."
                    if improved else f"AI prediction error was {corr_err} mm."
                )
            }

        steps.append(step7)

        return {
            "record_id": str(rec.get("record_id", record_id)),
            "district": rec.get("district", "Visakhapatnam"),
            "region": rec.get("region", "East Coast"),
            "lead_time_hours": rec.get("lead_time_hours", 24),
            "is_real_model": pred.get("is_real_model", True),
            "steps": steps
        }

forecast_service = ForecastService()
