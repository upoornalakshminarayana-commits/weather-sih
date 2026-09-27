"""
VARSHAAI — Backend Configuration Settings
SIH 26080: Environment, Paths & Live Weather API Keys
"""

import os
from typing import List

class Settings:
    PROJECT_NAME: str = "VARSHAAI — Regime-Aware AI Rainfall Forecast Post-Processing"
    VERSION: str = "0.1.0-prototype"
    API_V1_STR: str = "/api"

    # Base directory of the backend (e.g. .../backend)
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Read .env file directly if present in backend/ or root
    _env_paths = [
        os.path.join(BASE_DIR, ".env"),
        os.path.join(os.path.dirname(BASE_DIR), ".env")
    ]
    for _env_file in _env_paths:
        if os.path.exists(_env_file):
            try:
                with open(_env_file, "r", encoding="utf-8") as _f:
                    for _line in _f:
                        _line = _line.strip()
                        if _line and not _line.startswith("#") and "=" in _line:
                            _k, _v = _line.split("=", 1)
                            _k = _k.strip()
                            _v = _v.strip().strip("'\"")
                            os.environ.setdefault(_k, _v)
            except Exception:
                pass

    # Deployment Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")

    # Server Network Configuration (Render/Railway/Fly.io inject PORT)
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")

    # Public URLs for deployed instances
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "").rstrip("/")

    # Model and Dataset Paths (fully configurable via environment)
    MODELS_DIR: str = os.getenv("MODEL_PATH", os.getenv("MODELS_DIR", os.path.join(BASE_DIR, "models")))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    DATASET_PATH: str = os.getenv(
        "DATASET_PATH",
        os.path.join(DATA_DIR, "SIH26080_10000_training_dataset.csv")
    )

    # Live Weather APIs (configured via environment variables)
    OPEN_METEO_BASE_URL: str = os.getenv("OPEN_METEO_BASE_URL", "https://api.open-meteo.com/v1").rstrip("/")
    
    # Accepts either OPENWEATHER_API_KEY or OPENWEATHERMAP_API_KEY
    OPENWEATHER_API_KEY: str = (
        os.getenv("OPENWEATHER_API_KEY") or
        os.getenv("OPENWEATHERMAP_API_KEY") or
        ""
    )
    OPENWEATHERMAP_API_KEY: str = OPENWEATHER_API_KEY

    # Accepts either TOMORROW_API_KEY or TOMORROW_IO_API_KEY
    TOMORROW_API_KEY: str = (
        os.getenv("TOMORROW_API_KEY") or
        os.getenv("TOMORROW_IO_API_KEY") or
        ""
    )
    TOMORROW_IO_API_KEY: str = TOMORROW_API_KEY
    TOMORROW_API_BASE_URL: str = os.getenv("TOMORROW_API_BASE_URL", "https://api.tomorrow.io/v4").rstrip("/")

    # CORS configuration
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        origins = [
            "http://localhost",
            "http://localhost:8000",
            "http://localhost:3000",
            "http://localhost:5500",
            "http://127.0.0.1:8000",
            "http://127.0.0.1:5500",
            "http://127.0.0.1:3000",
            "*"
        ]
        if self.FRONTEND_URL and self.FRONTEND_URL not in origins:
            origins.append(self.FRONTEND_URL)
        
        # Support both CORS_ORIGINS and ALLOWED_ORIGINS env variables
        raw_custom = os.getenv("CORS_ORIGINS", "") or os.getenv("ALLOWED_ORIGINS", "")
        if raw_custom:
            for o in raw_custom.split(","):
                o = o.strip()
                if o and o not in origins:
                    origins.append(o)
        return origins

settings = Settings()
