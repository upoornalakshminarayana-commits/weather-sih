/**
 * VARSHAAI — Frontend API Client
 * Connects the web application to the FastAPI Python ML backend
 * Includes Live Operational Weather Ingestion (OpenWeatherMap & Tomorrow.io)
 */

class VarshaApi {
  constructor(baseUrl = null) {
    if (baseUrl) {
      this.baseUrl = baseUrl;
    } else if (typeof window !== 'undefined' && window.location && window.location.protocol.startsWith('http')) {
      if (window.location.port === '8000') {
        this.baseUrl = window.location.origin;
      } else {
        this.baseUrl = 'http://localhost:8000';
      }
    } else {
      this.baseUrl = 'http://localhost:8000';
    }
    this.isBackendOnline = false;
    this.modelVersion = null;
    this.healthSubscribers = [];
    this.checkInterval = null;

    this._owmKey = (window.VARSHA_CONFIG && window.VARSHA_CONFIG.OPENWEATHERMAP_API_KEY) || '';
    this._tomorrowKey = (window.VARSHA_CONFIG && window.VARSHA_CONFIG.TOMORROW_IO_API_KEY) || '';
  }

  get owmKey() {
    return (window.VARSHA_CONFIG && window.VARSHA_CONFIG.OPENWEATHERMAP_API_KEY) || this._owmKey || '';
  }

  set owmKey(val) {
    this._owmKey = val;
  }

  get tomorrowKey() {
    return (window.VARSHA_CONFIG && window.VARSHA_CONFIG.TOMORROW_IO_API_KEY) || this._tomorrowKey || '';
  }

  set tomorrowKey(val) {
    this._tomorrowKey = val;
  }

  onStatusChange(callback) {
    this.healthSubscribers.push(callback);
  }

  notifyStatus() {
    this.healthSubscribers.forEach(cb => cb(this.isBackendOnline, this.modelVersion));
  }

  async init() {
    await this.checkHealth();
    if (!this.checkInterval) {
      this.checkInterval = setInterval(() => this.checkHealth(), 8000);
    }
  }

  async checkHealth() {
    try {
      const res = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
        signal: AbortSignal.timeout(2500)
      });
      if (res.ok) {
        const data = await res.json();
        this.isBackendOnline = true;
        this.modelVersion = data.model_version || '0.1.0-prototype';
        this.notifyStatus();
        return true;
      }
    } catch (e) {
      // Backend is unreachable
    }

    if (this.isBackendOnline !== false) {
      this.isBackendOnline = false;
      this.notifyStatus();
    }
    return false;
  }

  /**
   * Fetch Live Real-Time Weather (OpenWeatherMap or Tomorrow.io)
   * Tries FastAPI backend proxy first; falls back to direct browser fetch!
   */
  async fetchLiveWeather(lat, lon, provider = 'openweathermap') {
    if (this.isBackendOnline) {
      try {
        const res = await fetch(`${this.baseUrl}/api/live-weather?lat=${lat}&lon=${lon}&provider=${provider}`, {
          signal: AbortSignal.timeout(5000)
        });
        if (res.ok) {
          return await res.json();
        }
      } catch (e) {
        console.warn('Backend live-weather proxy error, trying direct browser fetch...', e);
      }
    }

    // Direct Browser Client Fallback
    return await this.fetchLiveWeatherDirect(lat, lon, provider);
  }

  async fetchLiveWeatherDirect(lat, lon, provider = 'openweathermap') {
    try {
      if (provider === 'tomorrow') {
        const url = `https://api.tomorrow.io/v4/weather/realtime?location=${lat},${lon}&apikey=${this.tomorrowKey}`;
        const res = await fetch(url);
        if (res.ok) {
          const json = await res.json();
          const vals = json.data?.values || {};
          const speed = vals.windSpeed || 4.0;
          const deg = vals.windDirection || 240;
          const rad = deg * (Math.PI / 180);
          return {
            status: 'success',
            is_live_data: true,
            provider: 'Tomorrow.io (Direct Client)',
            city_name: 'Indian Coordinates',
            coordinates: { lat, lon },
            live_observations: {
              temperature_c: vals.temperature || 28.0,
              relative_humidity_pct: vals.humidity || 75.0,
              surface_pressure_hpa: vals.surfacePressure || 1010.0,
              wind_speed_ms: speed,
              wind_u_ms: parseFloat((-speed * Math.sin(rad)).toFixed(2)),
              wind_v_ms: parseFloat((-speed * Math.cos(rad)).toFixed(2)),
              nwp_rainfall_mm: parseFloat(((vals.precipitationIntensity || 0) * 24).toFixed(1)),
              description: 'Tomorrow.io Live Satellite Stream'
            }
          };
        }
      }

      // Default OpenWeatherMap
      const url = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${this.owmKey}&units=metric`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        const speed = data.wind?.speed || 4.0;
        const deg = data.wind?.deg || 240;
        const rad = deg * (Math.PI / 180);
        const rain1h = data.rain?.['1h'] || 0;
        const nwpRain = rain1h > 0 ? parseFloat((rain1h * 24).toFixed(1)) : parseFloat(((data.clouds?.all || 50) * 0.35).toFixed(1));

        return {
          status: 'success',
          is_live_data: true,
          provider: 'OpenWeatherMap (Direct Client)',
          city_name: data.name || 'Indian Station',
          coordinates: { lat, lon },
          live_observations: {
            temperature_c: data.main?.temp || 28.0,
            relative_humidity_pct: data.main?.humidity || 75.0,
            surface_pressure_hpa: data.main?.pressure || 1010.0,
            wind_speed_ms: speed,
            wind_deg: deg,
            wind_u_ms: parseFloat((-speed * Math.sin(rad)).toFixed(2)),
            wind_v_ms: parseFloat((-speed * Math.cos(rad)).toFixed(2)),
            nwp_rainfall_mm: nwpRain,
            description: data.weather?.[0]?.description || 'Live Atmosphere'
          }
        };
      }
    } catch (err) {
      console.error('Direct live weather fetch failed:', err);
    }
    return null;
  }

  /**
   * POST /api/predict — Real-time inference on arbitrary input features
   */
  async predict(inputData) {
    if (!this.isBackendOnline) return null;
    try {
      const res = await fetch(`${this.baseUrl}/api/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(inputData),
        signal: AbortSignal.timeout(4000)
      });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('API predict call failed:', e);
    }
    return null;
  }

  async getForecast(recordId) {
    if (!this.isBackendOnline) return null;
    try {
      const res = await fetch(`${this.baseUrl}/api/forecast/${encodeURIComponent(recordId)}`, {
        signal: AbortSignal.timeout(3000)
      });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('API getForecast failed:', e);
    }
    return null;
  }

  async getForecastJourney(recordId) {
    if (!this.isBackendOnline) return null;
    try {
      const res = await fetch(`${this.baseUrl}/api/forecast-journey/${encodeURIComponent(recordId)}`, {
        signal: AbortSignal.timeout(3000)
      });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('API getForecastJourney failed:', e);
    }
    return null;
  }

  async getModelMetrics() {
    if (!this.isBackendOnline) return null;
    try {
      const res = await fetch(`${this.baseUrl}/api/model/metrics`, {
        signal: AbortSignal.timeout(3000)
      });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('API getModelMetrics failed:', e);
    }
    return null;
  }

  async getFeatureImportance() {
    if (!this.isBackendOnline) return null;
    try {
      const res = await fetch(`${this.baseUrl}/api/model/feature-importance`, {
        signal: AbortSignal.timeout(3000)
      });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('API getFeatureImportance failed:', e);
    }
    return null;
  }

  async getDataQuality() {
    if (!this.isBackendOnline) return null;
    try {
      const res = await fetch(`${this.baseUrl}/api/data-quality`, {
        signal: AbortSignal.timeout(3000)
      });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('API getDataQuality failed:', e);
    }
    return null;
  }
}

window.varshaApi = new VarshaApi();
