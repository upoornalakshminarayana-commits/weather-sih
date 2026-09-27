"""
VARSHAAI — Live Operational Weather Ingestion Service
Integrates OpenWeatherMap & Tomorrow.io APIs with trained Machine Learning models
"""

import math
import urllib.request
import urllib.parse
import json
from typing import Dict, Any, Optional

from app.config import settings
from app.ml.inference import inference_engine

# Known Indian reference stations with accurate geography
INDIAN_CITIES: Dict[str, Dict[str, Any]] = {
    "visakhapatnam": {"name": "Visakhapatnam", "state": "Andhra Pradesh", "lat": 17.68, "lon": 83.21, "elev": 45, "coast": 5, "region": "East Coast"},
    "mumbai": {"name": "Mumbai", "state": "Maharashtra", "lat": 19.07, "lon": 72.87, "elev": 14, "coast": 2, "region": "West Coast"},
    "cherrapunji": {"name": "Cherrapunji", "state": "Meghalaya", "lat": 25.29, "lon": 91.73, "elev": 1430, "coast": 340, "region": "North East"},
    "delhi": {"name": "Delhi", "state": "Delhi", "lat": 28.61, "lon": 77.20, "elev": 216, "coast": 880, "region": "North West"},
    "kochi": {"name": "Kochi", "state": "Kerala", "lat": 9.93, "lon": 76.26, "elev": 5, "coast": 3, "region": "South Peninsular"},
    "kolkata": {"name": "Kolkata", "state": "West Bengal", "lat": 22.57, "lon": 88.36, "elev": 9, "coast": 85, "region": "East Coast"},
    "chennai": {"name": "Chennai", "state": "Tamil Nadu", "lat": 13.08, "lon": 80.27, "elev": 7, "coast": 4, "region": "South Peninsular"},
    "bhubaneswar": {"name": "Bhubaneswar", "state": "Odisha", "lat": 20.29, "lon": 85.82, "elev": 45, "coast": 55, "region": "East Coast"},
    "pune": {"name": "Pune", "state": "Maharashtra", "lat": 18.52, "lon": 73.85, "elev": 560, "coast": 120, "region": "Central India"},
    "shimla": {"name": "Shimla", "state": "Himachal Pradesh", "lat": 31.10, "lon": 77.17, "elev": 2200, "coast": 1100, "region": "North West"}
}

class LiveWeatherService:
    def __init__(self):
        self.owm_key = settings.OPENWEATHERMAP_API_KEY
        self.tomorrow_key = settings.TOMORROW_IO_API_KEY

    def fetch_from_openweathermap(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch current weather from OpenWeatherMap API."""
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.owm_key}&units=metric"
        req = urllib.request.Request(url, headers={"User-Agent": "VARSHAAI-Scientific/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        temp = float(data.get("main", {}).get("temp", 28.0))
        rh = float(data.get("main", {}).get("humidity", 75.0))
        pressure = float(data.get("main", {}).get("pressure", 1010.0))
        wind_speed = float(data.get("wind", {}).get("speed", 4.0))
        wind_deg = float(data.get("wind", {}).get("deg", 240.0))

        # Raw precipitation estimate from rain field or cloud cover
        rain_1h = float(data.get("rain", {}).get("1h", 0.0))
        raw_nwp_rain = round(rain_1h * 24.0, 1) if rain_1h > 0 else round(float(data.get("clouds", {}).get("all", 50)) * 0.35, 1)

        # Convert wind speed & direction to meteorological U, V components
        rad = math.radians(wind_deg)
        wind_u = round(-wind_speed * math.sin(rad), 2)
        wind_v = round(-wind_speed * math.cos(rad), 2)

        return {
            "provider": "OpenWeatherMap",
            "city_name": data.get("name", "Indian Station"),
            "temperature_c": temp,
            "relative_humidity_pct": rh,
            "surface_pressure_hpa": pressure,
            "wind_speed_ms": wind_speed,
            "wind_deg": wind_deg,
            "wind_u_ms": wind_u,
            "wind_v_ms": wind_v,
            "nwp_rainfall_mm": raw_nwp_rain,
            "description": data.get("weather", [{}])[0].get("description", "Clear sky"),
            "clouds_pct": data.get("clouds", {}).get("all", 0)
        }

    def fetch_from_tomorrow(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch current realtime weather from Tomorrow.io API."""
        url = f"https://api.tomorrow.io/v4/weather/realtime?location={lat},{lon}&apikey={self.tomorrow_key}"
        req = urllib.request.Request(url, headers={"User-Agent": "VARSHAAI-Scientific/1.0", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        values = data.get("data", {}).get("values", {})
        temp = float(values.get("temperature", 28.0))
        rh = float(values.get("humidity", 75.0))
        pressure = float(values.get("surfacePressure", 1010.0))
        wind_speed = float(values.get("windSpeed", 4.0))
        wind_deg = float(values.get("windDirection", 240.0))
        precip_intensity = float(values.get("precipitationIntensity", 0.0))
        raw_nwp_rain = round(precip_intensity * 24.0, 1)

        rad = math.radians(wind_deg)
        wind_u = round(-wind_speed * math.sin(rad), 2)
        wind_v = round(-wind_speed * math.cos(rad), 2)

        return {
            "provider": "Tomorrow.io",
            "city_name": "Indian Coordinates",
            "temperature_c": temp,
            "relative_humidity_pct": rh,
            "surface_pressure_hpa": pressure,
            "wind_speed_ms": wind_speed,
            "wind_deg": wind_deg,
            "wind_u_ms": wind_u,
            "wind_v_ms": wind_v,
            "nwp_rainfall_mm": raw_nwp_rain,
            "description": "Live Tomorrow.io Feed",
            "clouds_pct": int(values.get("cloudCover", 50))
        }

    def get_live_weather_and_ai_prediction(self, lat: float, lon: float, provider: str = "openweathermap") -> Dict[str, Any]:
        """
        1. Fetch live real-time conditions from API.
        2. Feed live parameters into trained XGBoost models.
        3. Return live regime detection and post-processed rainfall intelligence.
        """
        # Fetch live data
        live_data = None
        if provider.lower() == "tomorrow":
            try:
                live_data = self.fetch_from_tomorrow(lat, lon)
            except Exception as e:
                print(f"Tomorrow.io error: {e}, falling back to OpenWeatherMap...")
                live_data = self.fetch_from_openweathermap(lat, lon)
        else:
            try:
                live_data = self.fetch_from_openweathermap(lat, lon)
            except Exception as e:
                print(f"OpenWeatherMap error: {e}, trying Tomorrow.io...")
                live_data = self.fetch_from_tomorrow(lat, lon)

        # Estimate local elevation and coastal distance
        elev = 15.0
        coast = 30.0
        # Check closest city for accurate terrain calibration
        for c in INDIAN_CITIES.values():
            if math.hypot(lat - c["lat"], lon - c["lon"]) < 0.8:
                elev = c["elev"]
                coast = c["coast"]
                break

        raw_nwp = float(live_data["nwp_rainfall_mm"])
        ens_spread = round(max(2.0, raw_nwp * 0.2 + 3.0), 1)
        ens_mean = round(raw_nwp * 0.96, 1)

        input_payload = {
            "nwp_rainfall_mm": raw_nwp,
            "ensemble_mean_mm": ens_mean,
            "ensemble_std_mm": ens_spread,
            "ensemble_min_mm": max(0.0, round(ens_mean - 1.8 * ens_spread, 1)),
            "ensemble_max_mm": round(ens_mean + 2.1 * ens_spread, 1),
            "temperature_c": live_data["temperature_c"],
            "relative_humidity_pct": live_data["relative_humidity_pct"],
            "surface_pressure_hpa": live_data["surface_pressure_hpa"],
            "wind_u_ms": live_data["wind_u_ms"],
            "wind_v_ms": live_data["wind_v_ms"],
            "latitude": lat,
            "longitude": lon,
            "elevation_m": elev,
            "coastal_distance_km": coast,
            "lead_time_hours": 24
        }

        # Run through trained ML models!
        ai_prediction = inference_engine.predict(input_payload)

        return {
            "status": "success",
            "is_live_data": True,
            "provider": live_data["provider"],
            "city_name": live_data["city_name"],
            "coordinates": {"lat": lat, "lon": lon},
            "live_observations": live_data,
            "ai_post_processing": ai_prediction
        }

    def get_live_city(self, city_key: str, provider: str = "openweathermap") -> Dict[str, Any]:
        """Fetch live weather and run AI for a major Indian city."""
        city_key = city_key.lower().strip()
        info = INDIAN_CITIES.get(city_key, INDIAN_CITIES["visakhapatnam"])
        res = self.get_live_weather_and_ai_prediction(info["lat"], info["lon"], provider)
        res["city_info"] = info
        return res

live_weather_service = LiveWeatherService()
