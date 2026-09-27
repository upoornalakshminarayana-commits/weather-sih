"""
VARSHAAI — Backend Configuration Settings
SIH 26080: Environment, Paths & Live Weather API Keys
"""

import os
from pydantic import BaseModel

class Settings:
    PROJECT_NAME: str = "VARSHAAI — Regime-Aware AI Rainfall Forecast Post-Processing"
    VERSION: str = "0.1.0-prototype"
    API_V1_STR: str = "/api"

    # Base directory of the backend
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODELS_DIR: str = os.path.join(BASE_DIR, "models")
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    DATASET_PATH: str = os.path.join(DATA_DIR, "SIH26080_10000_training_dataset.csv")

    # Read .env file directly if present
    _env_file = os.path.join(BASE_DIR, ".env")
    if os.path.exists(_env_file):
        try:
            with open(_env_file, "r", encoding="utf-8") as _f:
                for _line in _f:
                    _line = _line.strip()
                    if _line and not _line.startswith("#") and "=" in _line:
                        _k, _v = _line.split("=", 1)
                        os.environ.setdefault(_k.strip(), _v.strip())
        except Exception:
            pass

    # Live Weather APIs (configured via environment variables)
    OPENWEATHERMAP_API_KEY: str = os.getenv("OPENWEATHERMAP_API_KEY", "")
    TOMORROW_IO_API_KEY: str = os.getenv("TOMORROW_IO_API_KEY", "")

    # CORS origins
    ALLOWED_ORIGINS: list = [
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:5500",
        "*"
    ]

settings = Settings()
