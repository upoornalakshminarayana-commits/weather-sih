/**
 * VARSHAAI — Interactive India Rainfall & Regime Map
 * Leaflet.js based scientific meteorological GIS visualizer
 */

class VarshaMap {
  constructor(containerId = 'varshaIndiaMap') {
    this.containerId = containerId;
    this.map = null;
    this.markersLayer = null;
    this.activeLayer = 'ai_corrected'; // Default
    this.records = [];
    this.selectedMarker = null;
  }

  init() {
    if (!document.getElementById(this.containerId)) return;
    if (this.map) return; // already initialized

    // Center coordinates over India
    this.map = L.map(this.containerId, {
      center: [22.5, 80.0],
      zoom: 5,
      minZoom: 4,
      maxZoom: 10,
      zoomControl: false
    });

    // Retrieve CARTO API key from safe environment/config object (window.VARSHA_CONFIG)
    const apiKey = (window.VARSHA_CONFIG && window.VARSHA_CONFIG.CARTO_API_KEY)
      ? String(window.VARSHA_CONFIG.CARTO_API_KEY).trim()
      : '';

    // Authenticated CARTO Voyager Basemap URL
    const tileUrl = apiKey
      ? `https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png?key=${encodeURIComponent(apiKey)}`
      : 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png';

    this.tileLayer = L.tileLayer(tileUrl, {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions" target="_blank" rel="noopener noreferrer">CARTO</a>',
      subdomains: ['a', 'b', 'c', 'd'],
      maxZoom: 19
    }).addTo(this.map);

    let authErrorReported = false;
    this.tileLayer.on('tileerror', () => {
      if (!authErrorReported) {
        authErrorReported = true;
        // Seamless fallback to OpenStreetMap tiles
        this.tileLayer.setUrl('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png');
        this.hideMapNotice();
      }
    });

    // Zoom control in top right
    L.control.zoom({ position: 'topright' }).addTo(this.map);

    this.markersLayer = L.layerGroup().addTo(this.map);

    // Setup map click listener
    this.map.on('click', () => {
      // close drawer if open
      const drawer = document.getElementById('mapInspectorDrawer');
      if (drawer && !drawer.classList.contains('pinned')) {
        drawer.classList.remove('open');
      }
    });

    this.updateData(window.varshaEngine.records);
  }

  showMapNotice(message, type = 'warning') {
    const container = document.getElementById(this.containerId);
    if (!container) return;
    let notice = document.getElementById('cartoMapStatusNotice');
    if (!notice) {
      notice = document.createElement('div');
      notice.id = 'cartoMapStatusNotice';
      container.appendChild(notice);
    }
    notice.className = `carto-map-notice ${type}`;
    notice.innerHTML = `<span style="font-size: 1rem;">${type === 'error' ? '🚫' : '⚠️'}</span> <span>${message}</span>`;
    notice.classList.remove('hidden');
  }

  hideMapNotice() {
    const notice = document.getElementById('cartoMapStatusNotice');
    if (notice) {
      notice.classList.add('hidden');
    }
  }

  setLayer(layerKey) {
    this.activeLayer = layerKey;
    this.renderMarkers();
    this.updateLegendUI();
  }

  updateData(records) {
    this.records = records || [];
    this.renderMarkers();
    this.updateLegendUI();
  }

  getColorForRecord(r) {
    switch (this.activeLayer) {
      case 'ai_corrected':
        return this.getRainfallColor(r.regime_aware_corrected_rainfall_mm);
      case 'raw_nwp':
        return this.getRainfallColor(r.nwp_rainfall_mm);
      case 'observed':
        return this.getRainfallColor(r.observed_rainfall_mm);
      case 'forecast_error':
        return this.getErrorColor(r.raw_error);
      case 'weather_regime':
        return this.getRegimeColor(r.weather_regime);
      case 'heavy_rain_prob':
        return this.getProbColor(r.heavy_rain_probability);
      case 'ensemble_mean':
        return this.getRainfallColor(r.ensemble_mean_mm);
      case 'uncertainty_spread':
        return this.getSpreadColor(r.ensemble_std_mm);
      default:
        return '#1677FF';
    }
  }

  getRainfallColor(val) {
    // IMD Standard isohyetal rainfall colors
    if (val >= 204.5) return '#7E22CE'; // Extremely Heavy (Purple)
    if (val >= 115.5) return '#DC2626'; // Very Heavy (Red)
    if (val >= 64.5)  return '#EA580C'; // Heavy (Orange)
    if (val >= 35.5)  return '#FBBF24'; // Rather Heavy (Yellow-amber)
    if (val >= 15.6)  return '#22C55E'; // Moderate (Green)
    if (val >= 2.5)   return '#38BDF8'; // Light (Sky Blue)
    return '#CBD5E1';                   // Very Light / Trace
  }

  getErrorColor(err) {
    // Negative error = underforecast (NWP < Obs), Positive = overforecast (NWP > Obs)
    if (err > 25) return '#B91C1C';
    if (err > 10) return '#F97316';
    if (err > -10) return '#22C55E'; // Low error
    if (err > -25) return '#3B82F6';
    return '#1D4ED8'; // Severe underforecast
  }

  getRegimeColor(regime) {
    const colors = {
      'Active Monsoon': '#2563EB',
      'Break Monsoon': '#D97706',
      'Monsoon Low / Depression': '#DC2626',
      'Coastal Rainfall': '#0891B2',
      'Orographic Rainfall': '#059669',
      'Western Disturbance': '#7C3AED'
    };
    return colors[regime] || '#64748B';
  }

  getProbColor(prob) {
    if (prob >= 0.75) return '#DC2626'; // High Risk
    if (prob >= 0.50) return '#F97316'; // Moderate Risk
    if (prob >= 0.25) return '#FBBF24'; // Low-Moderate
    return '#22C55E';                   // Low Risk
  }

  getSpreadColor(spread) {
    if (spread >= 15) return '#9333EA'; // High uncertainty
    if (spread >= 8)  return '#3B82F6';
    return '#10B981';                   // Low uncertainty (Confident)
  }

  renderMarkers() {
    if (!this.markersLayer) return;
    this.markersLayer.clearLayers();

    // Sample points across India to maintain smooth 60fps rendering
    // Pick unique spatial points for visual clarity
    const displayPoints = this.records.slice(0, 800);

    displayPoints.forEach(r => {
      const color = this.getColorForRecord(r);
      const isSelected = window.varshaEngine.selectedRecord && window.varshaEngine.selectedRecord.record_id === r.record_id;
      
      const marker = L.circleMarker([r.latitude, r.longitude], {
        radius: isSelected ? 9 : 6,
        fillColor: color,
        color: isSelected ? '#071A33' : '#FFFFFF',
        weight: isSelected ? 3 : 1.5,
        opacity: 1,
        fillOpacity: 0.85
      });

      // Hover Tooltip
      const tooltipContent = `
        <div style="font-family: var(--font-sans); padding: 4px;">
          <div style="font-weight: 700; color: #071A33; font-size: 0.85rem;">${r.district} (${r.region})</div>
          <div style="font-size: 0.75rem; color: #64748B; margin: 2px 0;">Regime: <strong>${r.weather_regime}</strong></div>
          <div style="display: flex; gap: 8px; font-family: var(--font-mono); font-size: 0.78rem; margin-top: 4px;">
            <span>NWP: <strong>${r.nwp_rainfall_mm} mm</strong></span>
            <span>AI: <strong style="color:#1677FF;">${r.regime_aware_corrected_rainfall_mm} mm</strong></span>
          </div>
          <div style="font-size: 0.72rem; color: #94A3B8; margin-top: 3px;">Lead: ${r.lead_time_hours}h | Heavy Rain Prob: ${(r.heavy_rain_probability * 100).toFixed(0)}%</div>
        </div>
      `;
      marker.bindTooltip(tooltipContent, { className: 'varsha-map-tooltip', offset: [0, -6] });

      // Click to inspect record
      marker.on('click', (e) => {
        L.DomEvent.stopPropagation(e);
        window.varshaEngine.setSelectedRecord(r);
        this.openInspectorDrawer(r);
        this.renderMarkers(); // re-render to show selection halo
      });

      marker.addTo(this.markersLayer);
    });
  }

  openInspectorDrawer(r) {
    const drawer = document.getElementById('mapInspectorDrawer');
    if (!drawer) return;

    document.getElementById('drawerDistrict').textContent = `${r.district} (${r.region})`;
    document.getElementById('drawerCoords').textContent = `${r.latitude.toFixed(2)}°N, ${r.longitude.toFixed(2)}°E | Lead: ${r.lead_time_hours}h`;
    document.getElementById('drawerRegime').textContent = r.weather_regime;
    document.getElementById('drawerRegime').className = `regime-badge regime-${r.weather_regime.toLowerCase().replace(/[^a-z0-9]/g, '-')}`;

    document.getElementById('drawerRawNwp').textContent = `${r.nwp_rainfall_mm} mm`;
    document.getElementById('drawerCorrected').textContent = `${r.regime_aware_corrected_rainfall_mm} mm`;
    document.getElementById('drawerObserved').textContent = `${r.observed_rainfall_mm} mm`;

    const adj = r.ai_adjustment;
    const adjEl = document.getElementById('drawerAdjustment');
    adjEl.textContent = `${adj > 0 ? '+' : ''}${adj} mm`;
    adjEl.className = `kpi-diff ${adj >= 0 ? 'positive' : 'negative'}`;

    document.getElementById('drawerProb').textContent = `${(r.heavy_rain_probability * 100).toFixed(0)}%`;
    document.getElementById('drawerEnsRange').textContent = `${r.ensemble_min_mm} – ${r.ensemble_max_mm} mm (±${r.ensemble_std_mm})`;

    document.getElementById('drawerTemp').textContent = `${r.temperature_c} °C`;
    document.getElementById('drawerRh').textContent = `${r.relative_humidity_pct}%`;
    document.getElementById('drawerPress').textContent = `${r.surface_pressure_hpa} hPa`;
    document.getElementById('drawerWind').textContent = `U: ${r.wind_u_ms} m/s, V: ${r.wind_v_ms} m/s`;
    document.getElementById('drawerCoast').textContent = `${r.coastal_distance_km} km (Elev: ${r.elevation_m}m)`;

    const rawErr = Math.abs(r.raw_error);
    const corrErr = Math.abs(r.corrected_error);
    const improved = corrErr < rawErr;
    const verifyBadge = document.getElementById('drawerVerifyBadge');
    verifyBadge.textContent = improved ? `AI Error Reduced by ${(rawErr - corrErr).toFixed(1)} mm` : 'Comparable Forecast Skill';
    verifyBadge.className = `kpi-diff ${improved ? 'positive' : 'negative'}`;

    drawer.classList.add('open');
  }

  updateLegendUI() {
    const legendTitle = document.getElementById('legendTitle');
    const legendScale = document.getElementById('legendScale');
    const legendMin = document.getElementById('legendMin');
    const legendMid = document.getElementById('legendMid');
    const legendMax = document.getElementById('legendMax');

    if (!legendTitle || !legendScale) return;

    if (this.activeLayer === 'ai_corrected' || this.activeLayer === 'raw_nwp' || this.activeLayer === 'observed' || this.activeLayer === 'ensemble_mean') {
      legendTitle.textContent = 'Rainfall Intensity (mm/24h)';
      legendScale.innerHTML = `
        <div class="legend-segment" style="background:#CBD5E1;" title="< 2.5 mm (Very Light)"></div>
        <div class="legend-segment" style="background:#38BDF8;" title="2.5 - 15.5 mm (Light)"></div>
        <div class="legend-segment" style="background:#22C55E;" title="15.6 - 64.4 mm (Moderate)"></div>
        <div class="legend-segment" style="background:#FBBF24;" title="35.5 - 64.4 mm"></div>
        <div class="legend-segment" style="background:#EA580C;" title="64.5 - 115.5 mm (Heavy)"></div>
        <div class="legend-segment" style="background:#DC2626;" title="115.6 - 204.4 mm (Very Heavy)"></div>
        <div class="legend-segment" style="background:#7E22CE;" title="≥ 204.5 mm (Extremely Heavy)"></div>
      `;
      legendMin.textContent = '0 mm';
      legendMid.textContent = '64.5 mm (Heavy)';
      legendMax.textContent = '≥ 204 mm';
    } else if (this.activeLayer === 'heavy_rain_prob') {
      legendTitle.textContent = 'Heavy Rain Exceedance Prob (P ≥ 64.5 mm)';
      legendScale.innerHTML = `
        <div class="legend-segment" style="background:#22C55E;" title="< 25% (Low Risk)"></div>
        <div class="legend-segment" style="background:#FBBF24;" title="25% - 50% (Moderate Risk)"></div>
        <div class="legend-segment" style="background:#F97316;" title="50% - 75% (High Risk)"></div>
        <div class="legend-segment" style="background:#DC2626;" title="≥ 75% (Very High Alert)"></div>
      `;
      legendMin.textContent = '0%';
      legendMid.textContent = '50%';
      legendMax.textContent = '100%';
    } else if (this.activeLayer === 'weather_regime') {
      legendTitle.textContent = 'Detected Weather Regime';
      legendScale.innerHTML = `
        <div class="legend-segment" style="background:#2563EB;" title="Active Monsoon"></div>
        <div class="legend-segment" style="background:#D97706;" title="Break Monsoon"></div>
        <div class="legend-segment" style="background:#DC2626;" title="Monsoon Low"></div>
        <div class="legend-segment" style="background:#0891B2;" title="Coastal"></div>
        <div class="legend-segment" style="background:#059669;" title="Orographic"></div>
        <div class="legend-segment" style="background:#7E22CE;" title="Western Disturbance"></div>
      `;
      legendMin.textContent = 'Active';
      legendMid.textContent = 'Low/Coastal';
      legendMax.textContent = 'WD';
    } else if (this.activeLayer === 'forecast_error') {
      legendTitle.textContent = 'Raw NWP Forecast Error (NWP - Obs, mm)';
      legendScale.innerHTML = `
        <div class="legend-segment" style="background:#1D4ED8;" title="Underforecast (< -25mm)"></div>
        <div class="legend-segment" style="background:#3B82F6;" title="Moderate Underforecast"></div>
        <div class="legend-segment" style="background:#22C55E;" title="Accurate (±10mm)"></div>
        <div class="legend-segment" style="background:#F97316;" title="Moderate Overforecast"></div>
        <div class="legend-segment" style="background:#B91C1C;" title="Overforecast (> +25mm)"></div>
      `;
      legendMin.textContent = '-50 mm';
      legendMid.textContent = '0 mm';
      legendMax.textContent = '+50 mm';
    } else if (this.activeLayer === 'uncertainty_spread') {
      legendTitle.textContent = 'Ensemble Spread / Standard Deviation (mm)';
      legendScale.innerHTML = `
        <div class="legend-segment" style="background:#10B981;" title="Low spread (High confidence)"></div>
        <div class="legend-segment" style="background:#3B82F6;" title="Moderate spread"></div>
        <div class="legend-segment" style="background:#9333EA;" title="High spread (High uncertainty)"></div>
      `;
      legendMin.textContent = '2 mm';
      legendMid.textContent = '8 mm';
      legendMax.textContent = '≥ 25 mm';
    }
  }
}

window.varshaMap = new VarshaMap();
