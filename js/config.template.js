/**
 * VARSHAAI — Frontend Runtime Configuration Template
 * 
 * Instructions:
 * 1. Copy this file to `js/config.js` for local development or static hosting
 * 2. Set BACKEND_URL to your deployed FastAPI backend URL (e.g. https://varshaai-api.onrender.com)
 * 3. Never commit `js/config.js` containing real secrets to Git (it is protected via .gitignore)
 */

window.VARSHA_CONFIG = {
  // Public HTTPS URL of the deployed FastAPI Python backend
  // In development: "http://localhost:8000"
  // In production: "https://your-backend-app.onrender.com"
  BACKEND_URL: "http://localhost:8000",

  // CARTO Basemaps Raster API Key (optional - works without key)
  CARTO_API_KEY: "",

  // Live Weather Telemetry Providers (Optional - backend proxies with server-side env vars)
  // Open-Meteo works with zero keys and zero configuration.
  OPENWEATHERMAP_API_KEY: "",
  TOMORROW_IO_API_KEY: ""
};
