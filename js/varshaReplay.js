/**
 * VARSHAAI — Historical Synoptic Event Replay
 * Sequentially steps through forecast cycles and valid dates,
 * synchronizing the map, weather regime, and atmospheric indicators.
 */

class VarshaReplay {
  constructor() {
    this.dates = [];
    this.currentIndex = 0;
    this.isPlaying = false;
    this.timer = null;
    this.speed = 1500; // 1.5 seconds per step
  }

  init() {
    this.dates = window.varshaEngine.timelineDates || [];
    const slider = document.getElementById('replaySlider');
    if (slider) {
      slider.max = Math.max(0, this.dates.length - 1);
      slider.value = 0;
    }
    this.updateUI();
  }

  setIndex(index) {
    if (index >= 0 && index < this.dates.length) {
      this.currentIndex = index;
      const targetDate = this.dates[this.currentIndex];

      // Filter records for this valid date
      const dateRecords = window.varshaEngine.getFilteredRecords({ date: targetDate });
      if (dateRecords.length > 0) {
        // Pick first heavy rain or primary record for the inspector
        const highImpact = dateRecords.find(r => r.observed_rainfall_mm >= 35) || dateRecords[0];
        window.varshaEngine.setSelectedRecord(highImpact);
        window.varshaMap.updateData(dateRecords);
      }

      this.updateUI();
    }
  }

  updateUI() {
    const targetDate = this.dates[this.currentIndex] || '2025-07-01';
    const timestampEl = document.getElementById('replayTimestamp');
    if (timestampEl) {
      timestampEl.textContent = `Valid Date: ${targetDate} 00:00 UTC`;
    }
    const slider = document.getElementById('replaySlider');
    if (slider) {
      slider.value = this.currentIndex;
    }

    // Update synoptic regime summary
    const curRecord = window.varshaEngine.selectedRecord;
    const regimeEl = document.getElementById('replayRegimeBadge');
    if (regimeEl && curRecord) {
      regimeEl.textContent = curRecord.weather_regime;
      regimeEl.className = `regime-badge regime-${curRecord.weather_regime.toLowerCase().replace(/[^a-z0-9]/g, '-')}`;
    }
  }

  play() {
    this.isPlaying = true;
    const playBtn = document.getElementById('replayPlayBtn');
    if (playBtn) playBtn.innerHTML = '<i data-lucide="pause"></i>';
    if (window.lucide) lucide.createIcons();

    this.timer = setInterval(() => {
      if (this.currentIndex < this.dates.length - 1) {
        this.setIndex(this.currentIndex + 1);
      } else {
        this.pause();
      }
    }, this.speed);
  }

  pause() {
    this.isPlaying = false;
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
    const playBtn = document.getElementById('replayPlayBtn');
    if (playBtn) playBtn.innerHTML = '<i data-lucide="play"></i>';
    if (window.lucide) lucide.createIcons();
  }

  togglePlay() {
    if (this.isPlaying) this.pause();
    else this.play();
  }

  next() {
    if (this.currentIndex < this.dates.length - 1) {
      this.setIndex(this.currentIndex + 1);
    }
  }

  prev() {
    if (this.currentIndex > 0) {
      this.setIndex(this.currentIndex - 1);
    }
  }

  setSpeed(ms) {
    this.speed = ms;
    if (this.isPlaying) {
      this.pause();
      this.play();
    }
  }
}

window.varshaReplay = new VarshaReplay();
