/**
 * VARSHAAI — Environment Configuration Template
 * 
 * Instructions:
 * 1. Copy this file to `js/config.js`
 * 2. Add your CARTO Basemaps API key and weather telemetry credentials
 * 3. Never commit `js/config.js` to Git (it is protected via .gitignore)
 */

window.VARSHA_CONFIG = {
  // CARTO Basemaps Raster API Key
  // Obtain from https://app.carto.com/ -> Developers -> API Keys
  CARTO_API_KEY: "YOUR_CARTO_API_KEY_HERE",

  // Live Weather Telemetry Providers
  OPENWEATHERMAP_API_KEY: "YOUR_OPENWEATHERMAP_API_KEY_HERE",
  TOMORROW_IO_API_KEY: "YOUR_TOMORROW_IO_API_KEY_HERE"
};
