// Spell effects in the SHARP pass (never blurred): screen-space quads at the actors' integer pixel scale k,
// snapped anchors, texelFetch from the spells atlas (nearest, no mips), hard alpha. Fades are a per-texel
// dither discard, never alpha. Ground decals (rune circle) are pre-squashed for the locked camera and drawn
// before the actors without writing depth. Each decal fragment takes the depth of the ground plane point under
// it (ray from the camera through the pixel, hit at the decal's height + 3 cm), so props, walls and actors in
// front of the ground always cover it, while the decal still sits on top of the ground it lies on. Optional small point-light
// flashes from a fixed pool of 2 lights (always present, so no shader recompiles). No bloom anywhere.
import * as THREE from 'three';

const VERT = /* glsl */`
uniform vec2 uAnchor, uCell, uPivot, uViewport;
uniform float uK, uZBottom, uZTop;
void main() {
  float px = uAnchor.x + (position.x * uCell.x - uPivot.x) * uK;
  float py = uAnchor.y + (position.y * uCell.y - (uCell.y - uPivot.y)) * uK;
  gl_Position = vec4(px / uViewport.x * 2.0 - 1.0, py / uViewport.y * 2.0 - 1.0, mix(uZBottom, uZTop, position.y), 1.0);
}`;
const FRAG = /* glsl */`
precision highp float;
uniform sampler2D uAtlas;
uniform vec2 uFrame, uCell, uPivot, uAnchor;
uniform float uK, uFade, uDecal, uPlaneY;
uniform vec2 uViewport;
uniform mat4 uInvVP, uVP;
uniform vec3 uTint;
out vec4 outColor;
float hash(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
void main() {
  vec2 origin = vec2(uAnchor.x - uPivot.x * uK, uAnchor.y - (uCell.y - uPivot.y) * uK);
  ivec2 t = clamp(ivec2(floor((gl_FragCoord.xy - origin) / uK)), ivec2(0), ivec2(uCell) - 1);
  vec4 c = texelFetch(uAtlas, ivec2(int(uFrame.x) + t.x, int(uFrame.y) + int(uCell.y) - 1 - t.y), 0);
  if (c.a < 0.5) discard;                         // hard alpha
  if (uFade > 0.0 && hash(vec2(t)) < uFade) discard; // dither-out per whole texel
  if (uDecal > 0.5) {
    vec2 ndc = gl_FragCoord.xy / uViewport * 2.0 - 1.0;
    vec4 a = uInvVP * vec4(ndc, -1.0, 1.0); a /= a.w;
    vec4 b = uInvVP * vec4(ndc, 1.0, 1.0); b /= b.w;
    vec3 d = b.xyz - a.xyz;
    vec3 p = a.xyz + d * ((uPlaneY - a.y) / d.y);
    vec4 cp = uVP * vec4(p, 1.0);
    gl_FragDepth = clamp(cp.z / cp.w * 0.5 + 0.5, 0.0, 1.0);
  } else {
    gl_FragDepth = gl_FragCoord.z;
  }
  outColor = vec4(min(c.rgb * uTint, vec3(1.0)), 1.0);
}`;
const QUAD = (() => {
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute([0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0], 3));
  return g;
})();

export class Effects {
  constructor(world, sharp, img, meta, nLights = 2) {
    this.sharp = sharp; this.meta = meta; this.cell = meta.cell;
    const tex = new THREE.Texture(img);
    tex.flipY = false; tex.generateMipmaps = false; tex.minFilter = tex.magFilter = THREE.NearestFilter;
    tex.colorSpace = THREE.NoColorSpace; tex.needsUpdate = true;
    this.tex = tex;
    this.list = [];
    this.lights = [];
    for (let i = 0; i < nLights; i++) {
      const L = new THREE.PointLight(0xffffff, 0, 4, 2);
      world.add(L); this.lights.push(L);
    }
    this._v = new THREE.Vector3(); this._w = new THREE.Vector3(); this._c = new THREE.Vector3();
    this.k = 3;
  }
  names() { return Object.keys(this.meta.effects); }
  spawn(name, x, y, z, opts = {}) {
    const e = this.meta.effects[name];
    if (!e) { console.warn('no effect', name); return null; }
    const mat = new THREE.ShaderMaterial({
      vertexShader: VERT, fragmentShader: FRAG, glslVersion: THREE.GLSL3,
      depthTest: true, depthWrite: false, transparent: false,
      uniforms: {
        uAtlas: { value: this.tex }, uFrame: { value: new THREE.Vector2() }, uCell: { value: new THREE.Vector2(this.cell, this.cell) },
        uPivot: { value: new THREE.Vector2(e.pivot[0], e.pivot[1]) }, uAnchor: { value: new THREE.Vector2() },
        uK: { value: 3 }, uViewport: { value: new THREE.Vector2(1, 1) }, uZBottom: { value: 0 }, uZTop: { value: 0 },
        uTint: { value: new THREE.Vector3(1, 1, 1) }, uFade: { value: 0 },
        uDecal: { value: e.kind === 'decal' ? 1 : 0 }, uPlaneY: { value: 0 }, uInvVP: { value: new THREE.Matrix4() }, uVP: { value: new THREE.Matrix4() },
      },
    });
    const mesh = new THREE.Mesh(QUAD, mat);
    mesh.frustumCulled = false;
    mesh.renderOrder = e.kind === 'decal' ? -10 : 10;   // decals under the actors, effects over them
    this.sharp.add(mesh);
    const fx = { name, e, mesh, mat, x, y, z, t: 0, frame: 0, fade: 0, done: false,
                 from: [x, y, z], to: opts.to || null, onDone: opts.onDone || null, forceFrame: opts.frame ?? null,
                 onTop: !!opts.onTop, fadeIn: opts.fadeIn || 0, dur: e.kind === 'projectile' ? 9 : (opts.duration ?? e.duration), id: (this._id = (this._id || 0) + 1) };
    if (e.kind === 'projectile' && fx.to) {
      const d = Math.hypot(fx.to[0] - x, fx.to[2] - z);
      fx.dur = Math.max(0.2, d / (e.speed || 6));
    }
    this.list.push(fx);
    return fx;
  }
  clear() { for (const f of this.list) this.sharp.remove(f.mesh); this.list = []; }
  update(dt) {
    const keep = [], queue = [];
    for (const f of this.list) {
      const e = f.e;
      f.t += dt;
      const n = e.frames;
      let fr = Math.floor(f.t * e.fps);
      if (e.loop) {
        const lf = e.loop_from || 0;
        fr = fr < n ? fr : lf + ((fr - lf) % (n - lf));
      } else fr = Math.min(n - 1, fr);
      f.frame = f.forceFrame ?? fr;
      if (e.kind === 'projectile' && f.to) {
        const u = Math.min(1, f.t / f.dur);
        f.x = f.from[0] + (f.to[0] - f.from[0]) * u;
        f.z = f.from[2] + (f.to[2] - f.from[2]) * u;
        f.y = f.from[1] + (f.to[1] - f.from[1]) * u + Math.sin(u * Math.PI) * 0.35;
      }
      // dither fade over the last 0.3 s of looping effects
      f.fade = e.loop && f.forceFrame === null ? THREE.MathUtils.clamp((f.t - (f.dur - 0.3)) / 0.3, 0, 1) : 0;
      if (f.fadeIn && f.forceFrame === null) f.fade = Math.max(f.fade, THREE.MathUtils.clamp(1 - f.t / f.fadeIn, 0, 1));   // dither in
      if (f.forceFrame === null && f.t >= f.dur) {
        this.sharp.remove(f.mesh); f.mat.dispose();
        if (e.then) queue.push([e.then, f.x, f.y, f.z]);
        if (f.onDone) f.onDone(f);
        continue;
      }
      keep.push(f);
    }
    this.list = keep;
    for (const q of queue) this.spawn(...q);
  }
  sync(camera, bufW, bufH, k, tint) {
    this.k = k;
    this._vp = (this._vp || new THREE.Matrix4()).multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse);
    this._ivp = (this._ivp || new THREE.Matrix4()).copy(this._vp).invert();
    const toCam = this._c;
    // lights: the newest lit effects get the pool
    const lit = this.list.filter((f) => f.e.light).slice(-this.lights.length);
    this.lights.forEach((L, i) => {
      const f = lit[i];
      if (!f) { L.intensity = 0; return; }
      const li = f.e.light, cv = li.curve || [1];
      L.color.set(li.color);
      L.intensity = li.intensity * cv[f.frame % cv.length] * (1 - f.fade);
      L.distance = li.range || 4;
      L.position.set(f.x, f.y + (f.e.lift || 0) + 0.6, f.z + 0.2);
    });
    for (const f of this.list) {
      const e = f.e, u = f.mat.uniforms;
      u.uFrame.value.set(f.frame * this.cell, e.row * this.cell);
      u.uK.value = k; u.uViewport.value.set(bufW, bufH); u.uFade.value = f.fade;
      if (e.glow) u.uTint.value.set(1, 1, 1); else u.uTint.value.set(tint.r, tint.g, tint.b);
      const y = f.y + (e.lift || 0);
      toCam.copy(camera.position).sub(this._v.set(f.x, y, f.z)).normalize();
      const p = this._v.set(f.x, y, f.z).project(camera);
      const sx = Math.round((p.x * 0.5 + 0.5) * bufW), sy = Math.round((p.y * 0.5 + 0.5) * bufH);
      u.uAnchor.value.set(sx, sy);
      if (e.kind === 'decal') {
        // per-fragment ground depth in the shader (see FRAG); the quad's own depth only has to be on screen
        const near = this._w.set(f.x, y, f.z).project(camera);
        u.uZBottom.value = near.z; u.uZTop.value = near.z;
        u.uPlaneY.value = f.y + 0.03;
        u.uVP.value.copy(this._vp); u.uInvVP.value.copy(this._ivp);
        u.uDecal.value = f.onTop ? 0 : 1;
      } else {
        const b = this._w.set(f.x, y, f.z).addScaledVector(toCam, 0.9).project(camera);
        u.uZBottom.value = b.z; u.uZTop.value = b.z;
      }
      // QA lineup only: never occluded by the scene, but still ordered among themselves (decals first, then billboards,
      // each far to near). A shared depth let the first-drawn effect win, and depth bands squeezed near the far plane are
      // below depth-buffer precision, so order by renderOrder with the depth test off (a back-row burst cut into lane's orb)
      if (f.onTop) {
        u.uZBottom.value = -0.999; u.uZTop.value = -0.999; f.mat.depthTest = false;
        const far = camera.position.distanceTo(this._c.set(f.x, y, f.z));
        f.mesh.renderOrder = (e.kind === 'decal' ? 100000 : 200000) - Math.round(far * 100);
      }
      const piv = u.uPivot.value;
      f.rect = { id: f.name, name: f.name, kind: e.kind, x: sx - piv.x * k, y: bufH - (sy + piv.y * k), w: this.cell * k, h: this.cell * k,
                 k, frame: [f.frame * this.cell, e.row * this.cell], cell: this.cell };
    }
  }
  remove(f) {
    const i = this.list.indexOf(f); if (i < 0) return;
    this.list.splice(i, 1); this.sharp.remove(f.mesh); f.mat.dispose();
  }
  rects() { return this.list.map((f) => f.rect).filter(Boolean); }
}
