// Cheap pixel particles in the SHARP pass: GL points, integer pixel scale k, snapped centres, texelFetch.
import * as THREE from 'three';

const VERT = /* glsl */`
in vec2 aCell; in float aGlow;
uniform float uK, uCell; uniform vec2 uViewport;
out vec2 vCell; out float vGlow;
void main() {
  vec4 clip = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  vec2 ndc = clip.xy / clip.w;
  vec2 px = floor((ndc * 0.5 + 0.5) * uViewport + 0.5);       // snap the centre to a pixel corner
  clip.xy = ((px / uViewport) * 2.0 - 1.0) * clip.w;
  gl_Position = clip;
  gl_PointSize = uCell * uK;
  vCell = aCell; vGlow = aGlow;
}`;
const FRAG = /* glsl */`
precision highp float;
uniform sampler2D uSheet; uniform float uCell; uniform vec3 uTint;
in vec2 vCell; in float vGlow;
out vec4 outColor;
void main() {
  ivec2 t = ivec2(floor(gl_PointCoord * uCell));
  t = clamp(t, ivec2(0), ivec2(int(uCell) - 1));
  vec4 c = texelFetch(uSheet, ivec2(int(vCell.x * uCell) + t.x, int(vCell.y * uCell) + t.y), 0);
  if (c.a < 0.5) discard;
  vec3 tint = mix(uTint, vec3(1.0), vGlow);
  outColor = vec4(min(c.rgb * tint, vec3(1.0)), 1.0);
}`;

export class Particles {
  constructor(scene, sheetImage, meta, max = 600) {
    this.meta = meta; this.cell = meta.cell; this.max = max;
    const tex = new THREE.Texture(sheetImage);
    tex.flipY = false; tex.generateMipmaps = false; tex.minFilter = tex.magFilter = THREE.NearestFilter;
    tex.colorSpace = THREE.NoColorSpace; tex.needsUpdate = true;
    this.pos = new Float32Array(max * 3); this.cellA = new Float32Array(max * 2); this.glow = new Float32Array(max);
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(this.pos, 3).setUsage(THREE.DynamicDrawUsage));
    g.setAttribute('aCell', new THREE.BufferAttribute(this.cellA, 2).setUsage(THREE.DynamicDrawUsage));
    g.setAttribute('aGlow', new THREE.BufferAttribute(this.glow, 1).setUsage(THREE.DynamicDrawUsage));
    g.setDrawRange(0, 0);
    this.geo = g;
    this.mat = new THREE.ShaderMaterial({
      glslVersion: THREE.GLSL3, vertexShader: VERT, fragmentShader: FRAG, depthTest: true, depthWrite: false,
      uniforms: { uSheet: { value: tex }, uCell: { value: this.cell }, uK: { value: 3 }, uViewport: { value: new THREE.Vector2(1, 1) },
                  uTint: { value: new THREE.Vector3(1, 1, 1) } },
    });
    this.points = new THREE.Points(g, this.mat);
    this.points.frustumCulled = false;
    scene.add(this.points);
    this.emitters = [];
    this.parts = [];
    this.rng = mulberry(meta.seed || 7);
  }
  addEmitter(e) {
    const p = this.meta.presets[e.preset];
    if (!p) { console.warn('no particle preset', e.preset); return; }
    this.emitters.push({ ...e, p, acc: 0, area: e.area || p.area || [1, 1, 1], follow: e.follow ?? !!p.follow,
                         floor: e.floor ?? p.floor, every: e.every || 0, clock: 0 });
  }
  // one-shot puffs (footstep dust, splashes): manual presets are never auto-emitted
  burst(name, x, y, z, n) {
    const p = this.meta.presets[name];
    if (!p) return;
    const R = this.rng;
    for (let i = 0; i < (n ?? p.burst ?? 1); i++) {
      if (this.parts.length >= this.max - 24) return;
      const lv = p.life[0] + R() * (p.life[1] - p.life[0]);
      this.parts.push({ x: x + (R() - 0.5) * 0.25, y, z: z + (R() - 0.5) * 0.15, vx: rr(R, p.vel[0]), vy: rr(R, p.vel[1]), vz: rr(R, p.vel[2]),
                        life: lv, age: 0, p, ph: R() * 6.28, floor: p.floor });
    }
  }
  // static flicker sprites (lamp glow): handled by the caller through flickerFrame()
  flickerFrame(t, phase = 0) {
    const f = this.meta.presets.lamp_flicker;
    const seq = f.sequence;
    const i = seq[Math.floor((t + phase) * f.fps) % seq.length];
    return { frame: i, intensity: f.intensity[i], row: f.row };
  }
  update(dt, grade, statics = []) {
    const R = this.rng;
    const F = this.followPos || { x: 0, z: 0 };
    for (const e of this.emitters) {
      const p = e.p;
      if (p.manual) {   // showcase: re-fire manual presets on a timer
        if (e.every) { e.clock -= dt; if (e.clock <= 0) { e.clock = e.every; this.burst(e.preset, e.pos[0], e.pos[1], e.pos[2]); } }
        continue;
      }
      const gate = e.min_gate != null ? Math.max(e.min_gate, p.grade ? (grade[p.grade] ?? 1) : 1) : (p.grade ? (grade[p.grade] ?? 1) : 1);   // min_gate: glade bugs by day too
      if (gate <= 0.02) continue;
      e.acc += dt * p.rate * gate * (e.rate_scale ?? 1);
      while (e.acc >= 1) {
        e.acc -= 1;
        if (this.parts.length >= this.max - statics.length) break;
        const [ax, ay, az] = e.area;
        const lv = p.life[0] + R() * (p.life[1] - p.life[0]);
        const bx = e.follow ? F.x : e.pos[0], bz = e.follow ? F.z : e.pos[2];
        const by = e.follow ? (e.pos?.[1] ?? p.y0 ?? 6) : e.pos[1];
        this.parts.push({
          x: bx + (R() - 0.5) * ax, y: by + (R() - 0.5) * ay, z: bz + (R() - 0.5) * az,
          vx: rr(R, p.vel[0]), vy: rr(R, p.vel[1]), vz: rr(R, p.vel[2]), life: lv, age: 0, p, ph: R() * 6.28,
          floor: p.weather && e.follow ? undefined : (e.floor ?? (p.floor_rel !== undefined ? e.pos[1] + p.floor_rel : undefined)),
        });
      }
    }
    let n = 0;
    const keep = [];
    for (const q of this.parts) {
      q.age += dt;
      if (q.age >= q.life) continue;
      const p = q.p;
      q.vy += (p.gravity || 0) * dt;
      const sw = p.sway ? Math.sin(q.age * 2.1 + q.ph) * p.sway : 0;
      q.x += (q.vx + sw) * dt; q.y += q.vy * dt; q.z += q.vz * dt;
      const fl = q.floor ?? (this.groundAt && p.weather ? this.groundAt(q.x, q.z) : undefined);
      if (fl !== undefined && q.y < fl) {
        if (p.on_floor) { this.burst(p.on_floor, q.x, fl + 0.02, q.z, 1); continue; }
        if (p.weather || p.gravity < -1) { q.age = q.life; continue; }   // drops vanish where they land
        q.y = fl; q.vx *= 0.2; q.vz *= 0.2; q.vy = 0;
      }
      keep.push(q);
      let fr;
      if (p.mode === 'life') fr = Math.min(p.frames - 1, Math.floor(q.age / q.life * p.frames));
      else fr = Math.floor(q.age * p.fps + q.ph) % p.frames;
      this.pos[n * 3] = q.x; this.pos[n * 3 + 1] = q.y; this.pos[n * 3 + 2] = q.z;
      this.cellA[n * 2] = fr; this.cellA[n * 2 + 1] = p.row; this.glow[n] = typeof p.glow === 'number' ? p.glow : (p.glow ? 1 : 0);   // a number = partly self-lit (rain catching lamp light)
      n++;
    }
    this.parts = keep;
    for (const s of statics) {
      if (n >= this.max) break;
      this.pos[n * 3] = s.x; this.pos[n * 3 + 1] = s.y; this.pos[n * 3 + 2] = s.z;
      this.cellA[n * 2] = s.frame; this.cellA[n * 2 + 1] = s.row; this.glow[n] = 1; n++;
    }
    this.geo.setDrawRange(0, n);
    for (const k of ['position', 'aCell', 'aGlow']) this.geo.attributes[k].needsUpdate = true;
    this.count = n;
  }
  sync(k, w, h, tint) {
    this.mat.uniforms.uK.value = k;
    this.mat.uniforms.uViewport.value.set(w, h);
    this.mat.uniforms.uTint.value.set(tint.r, tint.g, tint.b);
  }
}
function rr(R, [a, b]) { return a + R() * (b - a); }
export function mulberry(a) {
  return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
}
