// Day clock + palette grades. cycleT 0 = midnight, 0.5 = noon, 0.75 = dusk (Game Layout One's shared clock).
import * as THREE from 'three';

const COLOR_KEYS = ['sun_color', 'hemi_sky', 'hemi_ground', 'fog_color', 'sky_top', 'sky_bottom', 'window_emissive',
  'sprite_tint', 'shadow_tint', 'lamp_color'];

export class Clock {
  constructor(biome, start = 0.62, speed = 1 / 480) {
    this.biome = biome;
    this.grades = biome.grades;
    this.stops = biome.clock;
    this.t = start;
    this.speed = speed; // cycles per second (a full day = 8 minutes by default)
    this.paused = false;
    this.cache = {};
    for (const [k, g] of Object.entries(this.grades)) {
      const c = {};
      for (const key of Object.keys(g)) {
        c[key] = COLOR_KEYS.includes(key) ? new THREE.Color(g[key]) : g[key];  // THREE.Color = linear
      }
      this.cache[k] = c;
    }
    this.cur = {};
  }
  tick(dt) { if (!this.paused) this.t = (this.t + dt * this.speed) % 1; }
  set(t) { this.t = ((t % 1) + 1) % 1; }
  label() {
    const h = Math.floor(this.t * 24), m = Math.floor((this.t * 24 - h) * 60);
    return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
  }
  phase() {
    const g = this.grade();
    return g._names;
  }
  // blended grade at the current time
  grade() {
    const s = this.stops;
    let i = 0;
    while (i < s.length - 2 && this.t > s[i + 1].t) i++;
    const a = s[i], b = s[i + 1];
    const f = b.t > a.t ? THREE.MathUtils.clamp((this.t - a.t) / (b.t - a.t), 0, 1) : 0;
    const ga = this.cache[a.grade], gb = this.cache[b.grade];
    const out = this.cur;
    for (const key of Object.keys(ga)) {
      const va = ga[key], vb = gb[key];
      if (va && va.isColor) { (out[key] ||= new THREE.Color()).copy(va).lerp(vb, f); }
      else if (typeof va === 'number') {
        if (key === 'sun_azimuth') {
          let d = vb - va; if (d > 180) d -= 360; if (d < -180) d += 360; out[key] = va + d * f;
        } else out[key] = va + (vb - va) * f;
      } else out[key] = f < 0.5 ? va : vb;
    }
    out._names = f < 0.5 ? a.grade : b.grade;
    out._f = f;
    return out;
  }
}

export const NAMED_TIMES = { night: 0.95, dawn: 0.3, day: 0.6, golden: 0.64, dusk: 0.76, evening: 0.82 };
