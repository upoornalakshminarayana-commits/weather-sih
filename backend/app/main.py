"""
VARSHAAI — FastAPI Application Entrypoint
SIH 26080: Regime-Aware AI Post-Processing of Monsoon Rainfall Forecasts
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.ml.inference import inference_engine
from app.api import health, forecast, regime, risk, verification, model, data_quality, live_weather

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load all trained models upon startup
    print(f"Loading trained models from {settings.MODELS_DIR}...")
    loaded = inference_engine.load_models(settings.MODELS_DIR)
    if loaded:
        print("All models successfully loaded and ready for inference.")
    else:
        print("Warning: Some or all model files not found. Run 'python scripts/train_all.py' to generate.")
    yield
    print("Shutting down VARSHAAI backend.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Scientific Decision-Support Microservice for SIH 26080: Regime-Aware AI Rainfall Forecast Post-Processing.",
    lifespan=lifespan
)

# CORS Configuration for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

PROJECT_ROOT = os.path.dirname(settings.BASE_DIR)

# Include Routers
app.include_router(health.router)
app.include_router(forecast.router)
app.include_router(regime.router)
app.include_router(risk.router)
app.include_router(verification.router)
app.include_router(model.router)
app.include_router(data_quality.router)
app.include_router(live_weather.router)

# Mount static asset directories
css_dir = os.path.join(PROJECT_ROOT, "css")
if os.path.isdir(css_dir):
    app.mount("/css", StaticFiles(directory=css_dir), name="css")

js_dir = os.path.join(PROJECT_ROOT, "js")
if os.path.isdir(js_dir):
    app.mount("/js", StaticFiles(directory=js_dir), name="js")

@app.get("/SIH26080_10000_training_dataset.csv")
def serve_dataset_csv():
    csv_file = os.path.join(PROJECT_ROOT, "SIH26080_10000_training_dataset.csv")
    if os.path.isfile(csv_file):
        return FileResponse(csv_file, media_type="text/csv")
    data_csv = os.path.join(settings.DATA_DIR, "SIH26080_10000_training_dataset.csv")
    if os.path.isfile(data_csv):
        return FileResponse(data_csv, media_type="text/csv")
    return FileResponse(csv_file, media_type="text/csv")

@app.get("/")
def root():
    index_file = os.path.join(PROJECT_ROOT, "index.html")
    if os.path.isfile(index_file):
        return FileResponse(index_file)
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "health_check": "/health",
        "live_weather": "/api/live-weather",
        "status": "online"
    }

@app.get("/api/info")
def api_info():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "health_check": "/health",
        "live_weather": "/api/live-weather",
        "status": "online"
    }

@app.get("/api/health")
def api_health():
    return health.health_check()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=False)
