// Hearthmoor ambient audio: tiny procedural WebAudio (no files). A soft two-voice pad, music-box plucks on a
// pentatonic scale, birds by day, crickets at night, a wind shimmer in Mossglen, and small event chimes.
// Starts on the first user gesture; M toggles mute (saved).
const SCALE = [0, 2, 4, 7, 9, 12, 14, 16, 19, 21];     // major pentatonic, two octaves
const CHORDS = [[0, 4, 7], [5, 9, 12], [-3, 0, 4], [7, 11, 14]];   // I IV vi V
const ROOT = 349.23;   // F4
const hz = (semi) => ROOT * Math.pow(2, semi / 12);

export class Ambient {
  constructor() { this.ctx = null; this.muted = localStorage.getItem('hearthmoor-mute') === '1'; this.area = 'plaza'; this.night = 0; this.timers = []; }
  start() {
    if (this.ctx) { if (this.ctx.state === 'suspended') this.ctx.resume(); return; }
    const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return;
    const c = this.ctx = new AC();
    this.master = c.createGain(); this.master.gain.value = this.muted ? 0 : 0.5; this.master.connect(c.destination);
    // echo for the plucks
    this.echo = c.createDelay(1.0); this.echo.delayTime.value = 0.38;
    const fb = c.createGain(); fb.gain.value = 0.32; const ef = c.createBiquadFilter(); ef.type = 'lowpass'; ef.frequency.value = 2200;
    this.echo.connect(ef); ef.connect(fb); fb.connect(this.echo); ef.connect(this.master);
    // pad: two detuned triangles per chord tone through a gentle lowpass
    this.padBus = c.createGain(); this.padBus.gain.value = 0.05;
    const lp = c.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 900; this.padBus.connect(lp); lp.connect(this.master);
    this.voices = [0, 1, 2].map(() => { const o1 = c.createOscillator(), o2 = c.createOscillator(); o1.type = o2.type = 'triangle'; o2.detune.value = 7;
      const g = c.createGain(); g.gain.value = 0.33; o1.connect(g); o2.connect(g); g.connect(this.padBus); o1.start(); o2.start(); return [o1, o2]; });
    this.chord = 0; this.setChord();
    this.loop(() => { this.chord = (this.chord + 1) % CHORDS.length; this.setChord(); }, 7000);
    this.tick();
  }
  setChord() {
    const t = this.ctx.currentTime;
    CHORDS[this.chord].forEach((s, i) => { for (const o of this.voices[i]) o.frequency.setTargetAtTime(hz(s - 12), t, 0.8); });
  }
  loop(fn, ms) { this.timers.push(setInterval(fn, ms)); }
  tick() {
    // plucks, birds or crickets: schedule the next one at a random gap
    const gap = 700 + Math.random() * 1900;
    this.timers.push(setTimeout(() => {
      if (!this.muted && document.visibilityState !== 'hidden') {
        const glade = this.area === 'mossglen';
        if (Math.random() < (glade ? 0.75 : 0.55)) this.pluck(SCALE[Math.floor(Math.random() * SCALE.length)] + (glade ? 12 : 0), glade ? 0.07 : 0.06);
        if (this.night < 0.5 && Math.random() < 0.18) this.bird();
        if (this.night > 0.5 && Math.random() < 0.35) this.cricket();
        if (glade && Math.random() < 0.2) this.shimmer();
      }
      this.tick();
    }, gap));
  }
  env(g, t, a, peak, d) { g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(peak, t + a); g.gain.exponentialRampToValueAtTime(0.0001, t + a + d); }
  pluck(semi, vol = 0.06, when = 0) {
    if (!this.ctx) return;
    const c = this.ctx, t = c.currentTime + when, o = c.createOscillator(), g = c.createGain();
    o.type = 'sine'; o.frequency.value = hz(semi); this.env(g, t, 0.006, vol, 0.9);
    o.connect(g); g.connect(this.master); g.connect(this.echo); o.start(t); o.stop(t + 1.0);
  }
  bird() {
    const c = this.ctx, t = c.currentTime, o = c.createOscillator(), g = c.createGain();
    o.type = 'sine'; const f = 2400 + Math.random() * 1400;
    o.frequency.setValueAtTime(f, t); o.frequency.exponentialRampToValueAtTime(f * 1.5, t + 0.07); o.frequency.exponentialRampToValueAtTime(f * 1.1, t + 0.14);
    this.env(g, t, 0.01, 0.018, 0.14); o.connect(g); g.connect(this.master); o.start(t); o.stop(t + 0.2);
  }
  cricket() {
    const c = this.ctx, t0 = c.currentTime;
    for (let i = 0; i < 3; i++) {
      const t = t0 + i * 0.09, o = c.createOscillator(), g = c.createGain();
      o.type = 'square'; o.frequency.value = 4300; this.env(g, t, 0.004, 0.006, 0.04);
      const bp = c.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = 4300; bp.Q.value = 8;
      o.connect(bp); bp.connect(g); g.connect(this.master); o.start(t); o.stop(t + 0.06);
    }
  }
  shimmer() { [19, 23, 26].forEach((s, i) => this.pluck(s + 12, 0.025, i * 0.11)); }
  sfx(kind) {
    if (!this.ctx || this.muted) return;
    if (kind === 'pickup') { this.pluck(14, 0.08); this.pluck(19, 0.08, 0.09); }
    if (kind === 'quest') [0, 4, 7, 12].forEach((s, i) => this.pluck(s + 12, 0.08, i * 0.1));
    if (kind === 'blip') this.pluck(24, 0.02);
    if (kind === 'save') this.pluck(12, 0.05);
    if (kind === 'portal') {
      const c = this.ctx, t = c.currentTime, n = c.createBufferSource(), b = c.createBuffer(1, c.sampleRate * 0.9, c.sampleRate), d = b.getChannelData(0);
      for (let i = 0; i < d.length; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / d.length);
      n.buffer = b; const f = c.createBiquadFilter(); f.type = 'bandpass'; f.Q.value = 3;
      f.frequency.setValueAtTime(300, t); f.frequency.exponentialRampToValueAtTime(2600, t + 0.8);
      const g = c.createGain(); g.gain.value = 0.12; n.connect(f); f.connect(g); g.connect(this.master); n.start(t);
      [7, 12, 16, 19].forEach((s, i) => this.pluck(s + 12, 0.04, 0.1 + i * 0.08));
    }
  }
  setArea(a) { this.area = a; }
  setNight(n) { this.night = n; }
  toggle() {
    this.muted = !this.muted; localStorage.setItem('hearthmoor-mute', this.muted ? '1' : '0');
    if (this.master) this.master.gain.setTargetAtTime(this.muted ? 0 : 0.5, this.ctx.currentTime, 0.1);
    return this.muted;
  }
}
