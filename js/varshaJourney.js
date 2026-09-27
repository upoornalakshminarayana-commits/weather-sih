/**
 * VARSHAAI — The 7-Step Forecast Journey
 * Signature interactive vertical narrative component explaining:
 * Forecast -> Atmosphere -> Regime -> AI Modification -> Heavy Rain Prob -> Uncertainty -> Observation & Verification
 *
 * Integrated with FastAPI backend (/api/forecast-journey/{record_id})
 * when backend is online, with transparent demo fallback.
 */

class VarshaJourney {
  constructor(containerId = 'forecastJourneyContainer') {
    this.containerId = containerId;
  }

  async render(record) {
    const container = document.getElementById(this.containerId);
    if (!container || !record) return;

    // Check if FastAPI backend has real ML journey
    if (window.varshaApi && window.varshaApi.isBackendOnline) {
      try {
        const journeyData = await window.varshaApi.getForecastJourney(record.record_id);
        if (journeyData && journeyData.steps && journeyData.steps.length >= 7) {
          this.renderFromApi(container, journeyData, record);
          return;
        }
      } catch (e) {
        console.log('Journey API fallback to local:', e);
      }
    }

    // Local deterministic rendering
    this.renderLocal(container, record);
  }

  renderFromApi(container, apiData, record) {
    const steps = apiData.steps;
    let html = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; padding:8px 14px; background:#DCFCE7; border:1px solid #BBF7D0; border-radius:8px;">
        <span style="font-size:0.82rem; font-weight:700; color:#15803D;">
          <i data-lucide="cpu" style="width:14px; height:14px; display:inline;"></i> DRIVEN BY TRAINED FASTAPI ML PIPELINE (XGBoost Regressor + Calibrated Classifier)
        </span>
        <span class="scientific-badge" style="background:#15803D; color:#FFF;">REAL ML INFERENCE</span>
      </div>
    `;

    steps.forEach(s => {
      let contentHtml = '';
      if (s.step_number === 1) {
        contentHtml = `
          <div style="font-size: 1.8rem; font-weight: 800; font-family: var(--font-mono); color: var(--color-navy); margin: 6px 0;">
            ${s.content.nwp_rainfall_mm} <span style="font-size: 1rem; color: var(--text-muted);">mm / 24h</span>
          </div>
        `;
      } else if (s.step_number === 2) {
        contentHtml = `
          <div class="atmos-gauge-grid">
            <div class="atmos-gauge-item"><div class="atmos-label">Temperature</div><div class="atmos-val">${s.content.temperature_c} °C</div></div>
            <div class="atmos-gauge-item"><div class="atmos-label">Humidity</div><div class="atmos-val">${s.content.relative_humidity_pct}%</div></div>
            <div class="atmos-gauge-item"><div class="atmos-label">Pressure</div><div class="atmos-val">${s.content.surface_pressure_hpa} hPa</div></div>
            <div class="atmos-gauge-item"><div class="atmos-label">Wind U/V</div><div class="atmos-val">${s.content.wind_u_ms} / ${s.content.wind_v_ms} m/s</div></div>
            <div class="atmos-gauge-item"><div class="atmos-label">Elevation</div><div class="atmos-val">${s.content.elevation_m} m</div></div>
            <div class="atmos-gauge-item"><div class="atmos-label">Coast Dist</div><div class="atmos-val">${s.content.coastal_distance_km} km</div></div>
          </div>
        `;
      } else if (s.step_number === 3) {
        const rName = s.content.predicted_regime;
        const rClass = `regime-badge regime-${rName.toLowerCase().replace(/[^a-z0-9]/g, '-')}`;
        contentHtml = `
          <div style="margin: 8px 0;">
            <span class="${rClass}" style="font-size:1rem; padding:6px 16px;">${rName}</span>
            <span style="font-size:0.85rem; color:#64748B; margin-left:10px;">Model Confidence: <strong>${Math.round(s.content.confidence * 100)}%</strong></span>
          </div>
        `;
      } else if (s.step_number === 4) {
        const raw = s.content.raw_nwp_rainfall_mm;
        const corr = s.content.corrected_rainfall_mm;
        const adj = s.content.ai_adjustment_mm;
        contentHtml = `
          <div class="journey-comparison-box">
            <div class="comparison-col"><div style="font-size:0.72rem; color:#64748B; font-weight:600;">RAW NWP</div><div class="comparison-val" style="color:#64748B;">${raw} mm</div></div>
            <div style="font-size:1.5rem; color:var(--color-blue); font-weight:700;">→</div>
            <div class="comparison-col"><div style="font-size:0.72rem; color:var(--color-blue); font-weight:600;">AI CORRECTED</div><div class="comparison-val" style="color:var(--color-blue);">${corr} mm</div></div>
            <div class="comparison-col"><div style="font-size:0.72rem; color:#64748B; font-weight:600;">ADJUSTMENT</div><span class="comparison-diff ${adj >= 0 ? 'kpi-diff positive' : 'kpi-diff negative'}">${adj > 0 ? '+' : ''}${adj} mm</span></div>
          </div>
        `;
      } else if (s.step_number === 5) {
        const prob = s.content.probability;
        contentHtml = `
          <div style="display:flex; align-items:baseline; gap:12px; margin:8px 0;">
            <span style="font-size:2.2rem; font-weight:800; font-family:var(--font-mono); color:${prob >= 0.65 ? '#DC2626' : prob >= 0.35 ? '#F59E0B' : '#10B981'};">
              ${Math.round(prob * 100)}%
            </span>
            <span style="font-size:0.85rem; color:#64748B; font-weight:600;">
              Risk Category: <strong>${s.content.risk_category}</strong>
            </span>
          </div>
        `;
      } else if (s.step_number === 6) {
        contentHtml = `
          <div style="background:#F8FAFC; padding:12px 18px; border-radius:8px; border:1px solid #E2E8F0; margin:10px 0; display:flex; justify-content:space-between;">
            <div><div style="font-size:0.72rem; color:#64748B;">Likely Range</div><div style="font-size:1.3rem; font-weight:800; color:var(--color-navy);">${s.content.ensemble_min_mm} – ${s.content.ensemble_max_mm} mm</div></div>
            <div><div style="font-size:0.72rem; color:#64748B;">Ensemble Spread</div><div style="font-size:1.1rem; font-weight:700; color:var(--color-navy);">±${s.content.ensemble_std_mm} mm</div></div>
          </div>
        `;
      } else if (s.step_number === 7) {
        if (s.content.observed_rainfall_mm === null || s.content.observed_rainfall_mm === undefined) {
          contentHtml = `
            <div style="margin:8px 0; padding:12px; background:#FFFBEB; border:1px solid #FDE68A; border-radius:8px;">
              <div style="font-size:1.1rem; font-weight:700; color:#B45309;">Pending Observation</div>
              <p style="font-size:0.85rem; color:#78350F; margin:4px 0 0 0;">Forecast is in progress. Ground-truth rain gauge verification will occur after the forecast valid time has elapsed.</p>
            </div>
          `;
        } else {
          contentHtml = `
            <div style="margin:8px 0; display:flex; justify-content:space-between; align-items:center;">
              <div><span style="font-size:0.75rem; color:#64748B;">Observed:</span><div style="font-size:1.7rem; font-weight:800; color:#047857;">${s.content.observed_rainfall_mm} mm</div></div>
              <div style="text-align:right;">
                <div style="font-size:0.75rem; color:#64748B;">Raw Error: <strong style="color:#DC2626;">${s.content.raw_nwp_error_mm} mm</strong></div>
                <div style="font-size:0.75rem; color:#64748B;">AI Error: <strong style="color:#2563EB;">${s.content.ai_corrected_error_mm} mm</strong></div>
              </div>
            </div>
          `;
        }
      }

      html += `
        <div class="journey-step active">
          <div class="journey-step-num">${s.step_number}</div>
          <div class="journey-content-card">
            <div class="journey-step-header">
              <span class="journey-step-title">${s.step_title}</span>
              <span class="scientific-badge">${s.badge}</span>
            </div>
            ${contentHtml}
            <p class="journey-explain-text">${s.explanation}</p>
          </div>
        </div>
      `;
    });

    container.innerHTML = html;
    if (window.lucide) lucide.createIcons();
  }

  renderLocal(container, r) {
    const rawNwp = r.nwp_rainfall_mm;
    const aiCorr = r.regime_aware_corrected_rainfall_mm;
    const obsRain = r.observed_rainfall_mm;
    const adj = r.ai_adjustment;
    const rawAbsErr = r.raw_absolute_error;
    const corrAbsErr = r.corrected_absolute_error;
    const errDiff = parseFloat((rawAbsErr - corrAbsErr).toFixed(1));
    const improved = corrAbsErr < rawAbsErr;

    // Plain English atmospheric interpretation
    let atmosNarrative = '';
    if (r.surface_pressure_hpa < 998 && r.relative_humidity_pct > 85) {
      atmosNarrative = `Deep low pressure (${r.surface_pressure_hpa} hPa) combined with saturated moisture (${r.relative_humidity_pct}% RH) and robust monsoonal wind inflow establish strong convective updrafts.`;
    } else if (r.relative_humidity_pct < 65 && r.surface_pressure_hpa > 1006) {
      atmosNarrative = `Elevated surface pressure (${r.surface_pressure_hpa} hPa) and dry air (${r.relative_humidity_pct}% RH) signify suppressed monsoonal convection and break conditions.`;
    } else if (r.elevation_m > 800) {
      atmosNarrative = `Steep terrain elevation (${r.elevation_m} m) forces moist air rapidly upward, inducing strong orographic condensation.`;
    } else {
      atmosNarrative = `Typical monsoonal thermodynamics with ambient temperature ${r.temperature_c} °C, ${r.relative_humidity_pct}% humidity, and steady wind vectors.`;
    }

    let aiReasonNarrative = '';
    if (adj > 0) {
      aiReasonNarrative = `Under the **${r.weather_regime}** regime, physical NWP models systematically underestimate intense convection. The model adjusted the rainfall prediction from ${rawNwp} mm to ${aiCorr} mm (+${adj} mm).`;
    } else if (adj < 0) {
      aiReasonNarrative = `Under **${r.weather_regime}** conditions, raw NWP models often predict excessive light drizzle. The model attenuated this wet bias by ${Math.abs(adj)} mm.`;
    } else {
      aiReasonNarrative = `Raw NWP parameters align closely with empirical distributions; minimal adjustment applied.`;
    }

    const regimeClass = `regime-badge regime-${r.weather_regime.toLowerCase().replace(/[^a-z0-9]/g, '-')}`;

    container.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; padding:8px 14px; background:#FEF3C7; border:1px solid #FDE68A; border-radius:8px;">
        <span style="font-size:0.82rem; font-weight:700; color:#B45309;">
          <i data-lucide="alert-circle" style="width:14px; height:14px; display:inline;"></i> DEMO MODE (FastAPI backend offline) — Start backend at localhost:8000 for live ML inference.
        </span>
        <span class="scientific-badge" style="background:#B45309; color:#FFF;">PROTOTYPE DEMO</span>
      </div>

      <div class="journey-step active">
        <div class="journey-step-num">1</div>
        <div class="journey-content-card">
          <div class="journey-step-header">
            <span class="journey-step-title">Raw NWP Forecast</span>
            <span class="scientific-badge">Physical Numerical Model</span>
          </div>
          <div style="font-size: 1.8rem; font-weight: 800; font-family: var(--font-mono); color: var(--color-navy); margin: 6px 0;">
            ${rawNwp} <span style="font-size: 1rem; color: var(--text-muted);">mm / 24h</span>
          </div>
          <p class="journey-explain-text">
            “This is the raw rainfall amount predicted directly by the Numerical Weather Prediction model prior to statistical calibration.”
          </p>
        </div>
      </div>

      <div class="journey-step active">
        <div class="journey-step-num">2</div>
        <div class="journey-content-card">
          <div class="journey-step-header">
            <span class="journey-step-title">Atmospheric & Geographic Conditions</span>
            <span class="scientific-badge">Thermodynamic State</span>
          </div>
          <div class="atmos-gauge-grid">
            <div class="atmos-gauge-item"><div class="atmos-label">Temperature</div><div class="atmos-val">${r.temperature_c} °C</div></div>
            <div class="atmos-gauge-item"><div class="atmos-label">Humidity</div><div class="atmos-val">${r.relative_humidity_pct}%</div></div>
            <div class="atmos-gauge-item"><div class="atmos-label">Pressure</div><div class="atmos-val">${r.surface_pressure_hpa} hPa</div></div>
            <div class="atmos-gauge-item"><div class="atmos-label">Wind U / V</div><div class="atmos-val">${r.wind_u_ms} / ${r.wind_v_ms} m/s</div></div>
            <div class="atmos-gauge-item"><div class="atmos-label">Elevation</div><div class="atmos-val">${r.elevation_m} m</div></div>
            <div class="atmos-gauge-item"><div class="atmos-label">Coast Dist</div><div class="atmos-val">${r.coastal_distance_km} km</div></div>
          </div>
          <p class="journey-explain-text"><strong>Meteorological Analysis:</strong> ${atmosNarrative}</p>
        </div>
      </div>

      <div class="journey-step active">
        <div class="journey-step-num">3</div>
        <div class="journey-content-card">
          <div class="journey-step-header">
            <span class="journey-step-title">Detected Weather Regime</span>
            <span class="${regimeClass}">${r.weather_regime}</span>
          </div>
          <p class="journey-explain-text">
            Atmospheric patterns were classified into <strong>${r.weather_regime}</strong>.
          </p>
        </div>
      </div>

      <div class="journey-step active">
        <div class="journey-step-num">4</div>
        <div class="journey-content-card">
          <div class="journey-step-header">
            <span class="journey-step-title">AI Bias Correction</span>
            <span class="scientific-badge" style="background:#E0F2FE; color:#0284C7; border-color:#BAE6FD;">Regime-Aware Post-Processor</span>
          </div>
          <div class="journey-comparison-box">
            <div class="comparison-col"><div style="font-size: 0.72rem; color: #64748B; font-weight: 600;">Raw NWP</div><div class="comparison-val" style="color: #64748B;">${rawNwp} mm</div></div>
            <div style="font-size: 1.5rem; color: var(--color-blue); font-weight: 700;">→</div>
            <div class="comparison-col"><div style="font-size: 0.72rem; color: var(--color-blue); font-weight: 600;">AI Corrected</div><div class="comparison-val" style="color: var(--color-blue);">${aiCorr} mm</div></div>
            <div class="comparison-col"><div style="font-size: 0.72rem; color: #64748B; font-weight: 600;">Adjustment</div><span class="comparison-diff ${adj >= 0 ? 'kpi-diff positive' : 'kpi-diff negative'}">${adj >= 0 ? '+' : ''}${adj} mm</span></div>
          </div>
          <div style="margin-top: 10px;">
            <div style="font-size: 0.85rem; font-weight: 700; color: var(--color-navy); margin-bottom: 4px;">Why did AI change it?</div>
            <p class="journey-explain-text">${aiReasonNarrative}</p>
          </div>
        </div>
      </div>

      <div class="journey-step active">
        <div class="journey-step-num">5</div>
        <div class="journey-content-card">
          <div class="journey-step-header">
            <span class="journey-step-title">Heavy Rainfall Probability</span>
            <span class="scientific-badge">P(Rain ≥ 64.5 mm)</span>
          </div>
          <div style="display: flex; align-items: baseline; gap: 12px; margin: 8px 0;">
            <span style="font-size: 2.2rem; font-weight: 800; font-family: var(--font-mono); color: ${r.heavy_rain_probability >= 0.65 ? '#DC2626' : r.heavy_rain_probability >= 0.35 ? '#F59E0B' : '#10B981'};">
              ${(r.heavy_rain_probability * 100).toFixed(0)}%
            </span>
            <span style="font-size: 0.85rem; color: #64748B; font-weight: 600;">
              Risk Category: <strong>${r.heavy_rain_probability >= 0.75 ? 'Red Alert (High)' : r.heavy_rain_probability >= 0.40 ? 'Orange/Yellow Alert' : 'Green (Low Risk)'}</strong>
            </span>
          </div>
        </div>
      </div>

      <div class="journey-step active">
        <div class="journey-step-num">6</div>
        <div class="journey-content-card">
          <div class="journey-step-header">
            <span class="journey-step-title">Forecast Uncertainty / Ensemble Range</span>
            <span class="scientific-badge">NEPS-G Spread</span>
          </div>
          <div style="display: flex; align-items: center; justify-content: space-between; background: #F8FAFC; padding: 12px 18px; border-radius: var(--radius-md); border: 1px solid #E2E8F0; margin: 10px 0;">
            <div><div style="font-size: 0.72rem; color: #64748B; text-transform: uppercase;">Likely Range</div><div style="font-size: 1.3rem; font-weight: 800; font-family: var(--font-mono); color: var(--color-navy);">${r.ensemble_min_mm} – ${r.ensemble_max_mm} mm</div></div>
            <div><div style="font-size: 0.72rem; color: #64748B; text-transform: uppercase;">Spread</div><div style="font-size: 1.1rem; font-weight: 700; font-family: var(--font-mono); color: var(--color-navy);">±${r.ensemble_std_mm} mm</div></div>
          </div>
        </div>
      </div>

      <div class="journey-step active">
        <div class="journey-step-num">7</div>
        <div class="journey-content-card" style="border-left: 4px solid ${obsRain === null || obsRain === undefined ? '#F59E0B' : improved ? 'var(--color-green)' : 'var(--color-blue)'};">
          <div class="journey-step-header">
            <span class="journey-step-title">Observation & Verification</span>
            <span class="scientific-badge" style="background:${obsRain === null || obsRain === undefined ? '#FEF3C7' : '#DCFCE7'}; color:${obsRain === null || obsRain === undefined ? '#B45309' : '#15803D'};">
              ${obsRain === null || obsRain === undefined ? 'Pending Observation' : 'Ground Truth'}
            </span>
          </div>
          ${obsRain === null || obsRain === undefined ? `
            <div style="margin: 8px 0; padding: 12px; background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 8px;">
              <div style="font-size: 1.1rem; font-weight: 700; color: #B45309;">Pending Observation</div>
              <p style="font-size: 0.85rem; color: #78350F; margin-top: 4px; margin-bottom: 0;">
                Live future forecast. Ground-truth rain gauge verification will occur after valid time has elapsed. No verification error calculated yet.
              </p>
            </div>
          ` : `
            <div style="margin: 8px 0; display: flex; align-items: center; justify-content: space-between;">
              <div><span style="font-size: 0.75rem; color: #64748B;">Observed:</span><div style="font-size: 1.7rem; font-weight: 800; font-family: var(--font-mono); color: #047857;">${obsRain} mm</div></div>
              <div style="text-align: right;">
                <div style="font-size: 0.72rem; color: #64748B;">Raw Error: <strong style="color:#DC2626;">${rawAbsErr} mm</strong></div>
                <div style="font-size: 0.72rem; color: #64748B;">AI Error: <strong style="color:#2563EB;">${corrAbsErr} mm</strong></div>
              </div>
            </div>
            <div style="background: ${improved ? '#F0FDF4' : '#F8FAFC'}; border: 1px solid ${improved ? '#BBF7D0' : '#E2E8F0'}; border-radius: var(--radius-md); padding: 12px 16px; margin-top: 10px;">
              <strong style="color: ${improved ? '#15803D' : '#1E40AF'};">Did AI improve the forecast?</strong>
              <p style="font-size: 0.85rem; color: ${improved ? '#166534' : '#334155'}; margin-top: 4px;">
                ${improved ? `Yes. Forecast error was reduced by <strong>${errDiff} mm</strong>.` : `AI accuracy matched physical NWP bounds.`}
              </p>
            </div>
          `}
        </div>
      </div>
    `;
    if (window.lucide) lucide.createIcons();
  }
}

window.varshaJourney = new VarshaJourney();
