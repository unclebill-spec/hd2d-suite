// Hearthmoor weather (Stage 4): per-area skies that follow the day cycle, soft pixel particles, wet-cobble glints.
//   Plaza + Bakery Lane share the town sky: each 6-hour block of each day is clear, drizzle or rain (seeded by the day).
//   Mossglen: mist in the mornings. Toadstool Hollows: drifting self-lit glow mist through the night.
//   Snow is ready (the engine's `snowfall` preset) for a winter area or `?wx=snow`, but no area schedules it yet.
// Rain wets the ground over ~20 s and dries over ~60 s; while wet, lamps, glow pools, braziers, garden blooms and
// lanterns throw short 1-3 px vertical reflection glints (palette pixels, self-lit, no bloom) on the ground around
// them, so every light pool shimmers in the wet. Options: weather on / light (phones by default) / off.
const STORE = 'hearthmoor-weather';
const MODES = ['on', 'light', 'off'];
const SKY = { plaza: 'town', lane: 'town', mossglen: 'glen', hollows: 'hollow' };
const NIGHT = (t) => t > 0.8 || t < 0.25;
// kind -> particle emitters ({preset, rate}); rate scales the preset's own rate
const KINDS = {
  clear: [],
  drizzle: [{ preset: 'rain', rate: 0.6 }],
  rain: [{ preset: 'rain', rate: 1.6 }],
  mist: [{ preset: 'mist', rate: 1 }],
  glowmist: [{ preset: 'glow_mist', rate: 1 }],
  snow: [{ preset: 'snowfall', rate: 0.6 }],
};
const WET = { drizzle: 0.6, rain: 1 };            // how wet each kind gets the ground
const GLINT_RATE = 90;                            // glints / s at full wet near the lights in view
const COOL = { brazier: 1, lantern: 1, spring: 1 };
const hash = (n) => { let x = (n | 0) * 374761393 + 668265263; x = (x ^ (x >>> 13)) * 1274126177; return ((x ^ (x >>> 16)) >>> 0) / 4294967296; };

// the scheduled weather for an area at (day, clock t); pure, so smoke can check the calendar
export function weatherAt(area, day, t) {
  const sky = SKY[area];
  if (sky === 'town') {
    if (!day) return 'clear';   // day 0 is Lantern Eve: the festival opening stays clear (rain starts the next day)
    const r = hash(day * 4 + Math.floor(t * 4) + 9001);
    return r < 0.5 ? 'clear' : r < 0.8 ? 'drizzle' : 'rain';
  }
  if (sky === 'glen') return t >= 0.22 && t < 0.42 ? 'mist' : 'clear';
  if (sky === 'hollow') return NIGHT(t) ? 'glowmist' : 'clear';
  return 'clear';
}

export class Weather {
  constructor(G) { this.G = G; this.ctx = null; this.kind = 'clear'; this.ems = []; this.wet = 0; this.acc = 0; this.forced = null; this.glints = 0; }
  get mode() {
    const s = localStorage.getItem(STORE); if (MODES.includes(s)) return s;
    return matchMedia('(pointer: coarse)').matches ? 'light' : 'on';
  }
  setMode(m) { localStorage.setItem(STORE, m); this.apply(true); }
  cycle() { const m = MODES[(MODES.indexOf(this.mode) + 1) % MODES.length]; this.setMode(m); return m; }
  attach(ctx, area) {
    this.ctx = ctx; this.area = area; this.ems = []; this.kind = null; this.acc = 0;
    const Q = new URLSearchParams(location.search), wx = Q.get('wx');
    // QA captures (check-scene) stay clear unless a ?wx= kind is asked for
    this.forced = wx && KINDS[wx] ? wx : (Q.has('qa') ? 'clear' : this.forced);
    this.apply(true);
    this.prewarm();
    this.wet = WET[this.kind] || 0;   // arriving in the rain: the cobbles are already wet
  }
  // arriving in weather: run just the weather emitters ~6 s so the rain / mist is already in the air
  prewarm() {
    const P = this.ctx && this.ctx.particles; if (!P || !this.ems.length) return;
    const all = P.emitters; P.emitters = this.ems;
    try { for (let i = 0; i < 60; i++) P.update(0.1, { motes: 1, bugs: 1 }, []); } finally { P.emitters = all; }
  }
  detach() { this.ctx = null; this.ems = []; }
  force(kind) { this.forced = kind && KINDS[kind] ? kind : null; this.apply(true); return this.kind; }
  scheduled() { const c = this.ctx; return c ? weatherAt(this.area, this.G.S.day || 0, c.clock.t) : 'clear'; }
  apply(rebuild) {
    const c = this.ctx; if (!c || !c.particles) return;
    const kind = this.mode === 'off' ? 'clear' : (this.forced || this.scheduled());
    if (kind === this.kind && !rebuild) return;
    const P = c.particles;
    for (const e of this.ems) { const i = P.emitters.indexOf(e); if (i >= 0) P.emitters.splice(i, 1); }
    this.ems = [];
    const light = this.mode === 'light' ? 0.5 : 1;
    for (const d of KINDS[kind]) {
      if (!P.meta.presets[d.preset]) continue;
      const n = P.emitters.length;
      P.addEmitter({ preset: d.preset, rate_scale: d.rate * light });
      if (P.emitters.length > n) this.ems.push(P.emitters[P.emitters.length - 1]);
    }
    this.kind = kind;
    const el = document.getElementById('btnWeather'); if (el) el.textContent = `weather: ${this.mode}${this.mode === 'light' ? ' (phone)' : ''}`;
  }
  // light sources that shimmer on wet ground: {x, z, r, cool}
  lights() {
    const G = this.G, out = [];
    for (const Z of (G.glow ? G.glow.zones() : [])) {
      let cool = !!COOL[Z.src];
      if (Z.src === 'pool') { const f = G.glow.fixed.find((p) => p.x === Z.x && p.z === Z.z); cool = !!(f && f.kind === 'cold'); if (f && f.kind === 'under') continue; }
      if (Z.src === 'garden' && G.garden) { const p = G.garden.plots.find((q) => q.x === Z.x && q.z === Z.z); cool = !!(p && p.kind === 'coldfire'); }
      out.push({ x: Z.x, z: Z.z, r: Math.min(Z.r, 2.2), cool });
    }
    return out;
  }
  update(dt) {
    const c = this.ctx; if (!c || !c.particles) return;
    this.apply(false);
    const target = WET[this.kind] || 0;
    this.wet = target > this.wet ? Math.min(target, this.wet + dt / 20) : Math.max(target, this.wet - dt / 60);   // soak ~20 s, dry ~60 s
    if (this.wet < 0.03 || this.mode === 'off') return;
    const P = c.particles, F = P.followPos || { x: c.player.x, z: c.player.z };
    const L = this.lights().filter((l) => Math.abs(l.x - F.x) < 14 && Math.abs(l.z - F.z) < 10);
    const R = Math.random;
    this.acc += dt * GLINT_RATE * this.wet * (this.mode === 'light' ? 0.5 : 1) * (L.length ? 1 : 0.25);
    while (this.acc >= 1) {
      this.acc -= 1;
      let x, z, cool;
      if (L.length && R() < 0.9) {   // around a light: denser near its middle
        const l = L[(R() * L.length) | 0], a = R() * 6.283, d = l.r * Math.sqrt(R()) * 0.85;
        x = l.x + Math.cos(a) * d; z = l.z + Math.sin(a) * d * 0.8; cool = l.cool;
      } else {                       // a faint sky glint anywhere on the open ground in view
        x = F.x + (R() - 0.5) * 18; z = F.z + (R() - 0.5) * 12; cool = true;
      }
      const h = c.collide ? c.collide.height(x, z) : 0; if (h === null) continue;
      P.burst(cool ? 'wet_glint_cool' : 'wet_glint', x, h + 0.03, z, 1);
      this.glints++;
    }
  }
  qa() {
    const c = this.ctx, P = c && c.particles, by = {};
    if (P) for (const q of P.parts) { const n = Object.keys(P.meta.presets).find((k) => P.meta.presets[k] === q.p); by[n] = (by[n] || 0) + 1; }
    return { mode: this.mode, kind: this.kind, forced: this.forced, wet: +this.wet.toFixed(3), glints: this.glints,
             emitters: this.ems.map((e) => ({ preset: e.preset, rate: +(e.rate_scale ?? 1).toFixed(3) })), parts: by };
  }
}
