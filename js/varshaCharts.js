/**
 * VARSHAAI — Scientific Chart Analytics Engine
 * Powered by Chart.js for meteorological verification and model comparisons
 */

class VarshaCharts {
  constructor() {
    this.charts = {};
  }

  destroyChart(id) {
    if (this.charts[id]) {
      this.charts[id].destroy();
      delete this.charts[id];
    }
  }

  // 1. Overview Regime Distribution Doughnut
  renderRegimeDoughnut(canvasId = 'regimeDistChart') {
    const ctx = document.getElementById(canvasId);
    if (!ctx || typeof Chart === 'undefined') return;
    this.destroyChart(canvasId);

    const stats = window.varshaEngine.regimeStats;
    const labels = Object.keys(stats);
    const data = labels.map(k => stats[k].count);
    const colors = [
      '#2563EB', '#D97706', '#DC2626', '#0891B2', '#059669', '#7C3AED'
    ];

    this.charts[canvasId] = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data,
          backgroundColor: colors,
          borderWidth: 2,
          borderColor: '#FFFFFF'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right',
            labels: { boxWidth: 12, font: { size: 11, family: 'Inter' } }
          }
        },
        cutout: '68%'
      }
    });
  }

  // 2. Verification Lab: Lead-time RMSE comparison
  renderLeadTimeChart(canvasId = 'leadTimeChart') {
    const ctx = document.getElementById(canvasId);
    if (!ctx || typeof Chart === 'undefined') return;
    this.destroyChart(canvasId);

    const leadStats = window.varshaEngine.leadTimeStats;
    const leads = Object.keys(leadStats).sort((a,b) => a - b);
    const rawRmses = leads.map(l => leadStats[l].rawRmse);
    const corrRmses = leads.map(l => leadStats[l].corrRmse);

    this.charts[canvasId] = new Chart(ctx, {
      type: 'line',
      data: {
        labels: leads.map(l => `${l}h Forecast`),
        datasets: [
          {
            label: 'Raw NWP RMSE (mm)',
            data: rawRmses,
            borderColor: '#EF4444',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            borderWidth: 2.5,
            tension: 0.3,
            pointRadius: 4
          },
          {
            label: 'VARSHAAI AI Corrected RMSE (mm)',
            data: corrRmses,
            borderColor: '#1677FF',
            backgroundColor: 'rgba(22, 119, 255, 0.1)',
            borderWidth: 2.5,
            tension: 0.3,
            pointRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          tooltip: { mode: 'index', intersect: false },
          legend: { position: 'top', labels: { font: { family: 'Inter', size: 12 } } }
        },
        scales: {
          y: {
            title: { display: true, text: 'RMSE (mm / 24h)' },
            grid: { color: '#F1F5F9' }
          },
          x: { grid: { display: false } }
        }
      }
    });
  }

  // 3. Verification Lab: Regime-wise RMSE comparison bar chart
  renderRegimeBarChart(canvasId = 'regimeBarChart') {
    const ctx = document.getElementById(canvasId);
    if (!ctx || typeof Chart === 'undefined') return;
    this.destroyChart(canvasId);

    const stats = window.varshaEngine.regimeStats;
    const labels = Object.keys(stats);
    const rawErrors = labels.map(k => stats[k].rawRmse);
    const aiErrors = labels.map(k => stats[k].corrRmse);

    this.charts[canvasId] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [
          {
            label: 'Raw NWP RMSE (mm)',
            data: rawErrors,
            backgroundColor: 'rgba(239, 68, 68, 0.75)',
            borderColor: '#DC2626',
            borderWidth: 1,
            borderRadius: 4
          },
          {
            label: 'VARSHAAI Corrected RMSE (mm)',
            data: aiErrors,
            backgroundColor: 'rgba(22, 119, 255, 0.85)',
            borderColor: '#1D4ED8',
            borderWidth: 1,
            borderRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top', labels: { font: { family: 'Inter', size: 12 } } },
          tooltip: {
            callbacks: {
              footer: (items) => {
                const raw = items[0].raw;
                const corr = items[1].raw;
                const red = ((1 - corr / raw) * 100).toFixed(1);
                return `Error Reduction: ${red}%`;
              }
            }
          }
        },
        scales: {
          y: { title: { display: true, text: 'Root Mean Square Error (mm)' } }
        }
      }
    });
  }

  // 4. Verification Lab: Skill Scores Comparison Radar (CSI, POD, FAR, ETS)
  renderSkillScoresChart(canvasId = 'skillScoresChart') {
    const ctx = document.getElementById(canvasId);
    if (!ctx || typeof Chart === 'undefined') return;
    this.destroyChart(canvasId);

    const raw = window.varshaEngine.metrics.rawScores;
    const ai = window.varshaEngine.metrics.aiScores;

    this.charts[canvasId] = new Chart(ctx, {
      type: 'radar',
      data: {
        labels: [
          'Critical Success Index (CSI)',
          'Probability of Detection (POD)',
          'False Alarm Ratio (FAR inverted)',
          'Equitable Threat Score (ETS)'
        ],
        datasets: [
          {
            label: 'Raw NWP',
            data: [
              raw.csi,
              raw.pod,
              Math.max(0, 1 - raw.far), // Invert FAR so larger is better
              Math.max(0, raw.ets)
            ],
            borderColor: '#DC2626',
            backgroundColor: 'rgba(220, 38, 38, 0.15)',
            borderWidth: 2,
            pointBackgroundColor: '#DC2626'
          },
          {
            label: 'VARSHAAI Regime-Aware AI',
            data: [
              ai.csi,
              ai.pod,
              Math.max(0, 1 - ai.far),
              Math.max(0, ai.ets)
            ],
            borderColor: '#1677FF',
            backgroundColor: 'rgba(22, 119, 255, 0.25)',
            borderWidth: 2,
            pointBackgroundColor: '#1677FF'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            min: 0,
            max: 1.0,
            ticks: { stepSize: 0.2, font: { size: 10 } },
            pointLabels: { font: { size: 11, weight: '600', family: 'Inter' } }
          }
        }
      }
    });
  }

  // 5. Heavy Rain Exceedance Probability Curve
  renderExceedanceCurve(canvasId = 'exceedanceCurveChart') {
    const ctx = document.getElementById(canvasId);
    if (!ctx || typeof Chart === 'undefined') return;
    this.destroyChart(canvasId);

    // Thresholds: 15.6, 35.5, 64.5, 115.5, 204.5 mm
    const thresholds = [15.6, 35.5, 64.5, 115.5, 204.5];
    const recs = window.varshaEngine.records;
    const total = recs.length;

    const rawProbs = thresholds.map(t => (recs.filter(r => r.nwp_rainfall_mm >= t).length / total) * 100);
    const corrProbs = thresholds.map(t => (recs.filter(r => r.regime_aware_corrected_rainfall_mm >= t).length / total) * 100);
    const obsProbs = thresholds.map(t => (recs.filter(r => r.observed_rainfall_mm >= t).length / total) * 100);

    this.charts[canvasId] = new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['Moderate (15.6mm)', 'Rather Heavy (35.5mm)', 'Heavy (64.5mm)', 'Very Heavy (115.5mm)', 'Extremely Heavy (204.5mm)'],
        datasets: [
          {
            label: 'Observed Frequency (%)',
            data: obsProbs,
            borderColor: '#15803D',
            backgroundColor: 'transparent',
            borderWidth: 2.5,
            borderDash: [5, 5],
            pointRadius: 4
          },
          {
            label: 'Raw NWP Predicted (%)',
            data: rawProbs,
            borderColor: '#EF4444',
            backgroundColor: 'transparent',
            borderWidth: 2,
            pointRadius: 4
          },
          {
            label: 'VARSHAAI Post-Processed (%)',
            data: corrProbs,
            borderColor: '#1677FF',
            backgroundColor: 'rgba(22, 119, 255, 0.08)',
            borderWidth: 3,
            fill: true,
            pointRadius: 5
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top' },
          tooltip: { mode: 'index', intersect: false }
        },
        scales: {
          y: {
            title: { display: true, text: 'Exceedance Frequency (%)' },
            min: 0
          }
        }
      }
    });
  }

  // Render all active charts
  renderAll() {
    this.renderRegimeDoughnut();
    this.renderLeadTimeChart();
    this.renderRegimeBarChart();
    this.renderSkillScoresChart();
    this.renderExceedanceCurve();
  }
}

window.varshaCharts = new VarshaCharts();
