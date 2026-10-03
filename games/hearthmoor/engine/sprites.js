// Pixel billboard actors. Two parts per actor:
//  1. SHARP pass quad (drawn after the world post): screen-space, pixel-snapped, integer scale k, texelFetch
//     from the atlas (nearest, no mips), depth from the cylindrical billboard so roofs/walls still occlude.
//  2. Shadow caster in the WORLD scene: an upright cylindrical-billboard plane turned toward the sun, invisible
//     in colour, with an alpha-tested customDepthMaterial so the real silhouette lands in the shadow map.
// Action states (hero roles): act(a, 'attack' | 'defend' | 'jump' | 'cast'); defend holds until release().
// A jump lifts only the visible quad (a.lift, metres); the shadow caster stays planted at the feet (a.y).
import * as THREE from 'three';

const VERT = /* glsl */`
uniform vec2 uAnchor;      // feet, in drawing-buffer pixels (origin bottom-left), integers
uniform vec2 uFrameSize;   // 20, 32
uniform vec2 uPivot;       // 10, 32 (from the frame's top-left)
uniform float uK;          // integer pixel scale
uniform vec2 uViewport;
uniform float uZBottom, uZTop;
void main() {
  float px = uAnchor.x + (position.x * uFrameSize.x - uPivot.x) * uK;
  float py = uAnchor.y + (position.y * uFrameSize.y - (uFrameSize.y - uPivot.y)) * uK;
  gl_Position = vec4(px / uViewport.x * 2.0 - 1.0, py / uViewport.y * 2.0 - 1.0, mix(uZBottom, uZTop, position.y), 1.0);
}`;

const FRAG = /* glsl */`
precision highp float;
precision highp usampler2D;
uniform sampler2D uAtlas;
uniform vec2 uFrame;       // frame top-left in atlas px
uniform vec2 uFrameSize, uPivot, uAnchor;
uniform float uK;
uniform vec3 uTint;        // sRGB-space multiplier from the clock grade + lamps
uniform int uRot;          // 0..3 quarter turns of the frame about (10, 10) from the feet (dodge-roll tumble, pixel exact)
uniform float uFlash;      // 0..1 hurt flash toward the palette's lightest step (no bloom: a flat colour mix)
uniform int uMode;         // 0 = sprite, 1 = see-through silhouette (only drawn where the world hides the sprite)
uniform vec3 uSil;         // silhouette colour (sRGB, a palette colour)
out vec4 outColor;
void main() {
  vec2 origin = vec2(uAnchor.x - uPivot.x * uK, uAnchor.y - (uFrameSize.y - uPivot.y) * uK);
  ivec2 t = ivec2(floor((gl_FragCoord.xy - origin) / uK));
  if (uRot != 0) {
    ivec2 q = t - ivec2(10, 10);
    if (uRot == 1) q = ivec2(-q.y - 1, q.x);
    else if (uRot == 2) q = ivec2(-q.x - 1, -q.y - 1);
    else q = ivec2(q.y, -q.x - 1);
    t = q + ivec2(10, 10);
    if (t.x < 0 || t.y < 0 || t.x >= int(uFrameSize.x) || t.y >= int(uFrameSize.y)) discard;
  }
  t = clamp(t, ivec2(0), ivec2(uFrameSize) - 1);
  ivec2 at = ivec2(int(uFrame.x) + t.x, int(uFrame.y) + int(uFrameSize.y) - 1 - t.y);
  vec4 c = texelFetch(uAtlas, at, 0);
  if (c.a < 0.5) discard;           // hard alpha only
  if (uMode == 1) {                 // checker dither on the texel grid: crisp, never a soft ghost
    ivec2 g = ivec2(floor((gl_FragCoord.xy - origin) / uK));
    if (((g.x + g.y) & 1) == 1) discard;
    outColor = vec4(uSil, 1.0);
    return;
  }
  vec3 col = min(c.rgb * uTint, vec3(1.0));
  outColor = vec4(mix(col, vec3(1.0, 0.97, 0.9), uFlash), 1.0);
}`;

const FACINGS = ['down', 'up', 'left', 'right'];
// action timings (seconds). jump: crouch -> airborne arc (lift = JUMP_H * sin(pi * p)) -> landing pose
export const ACT = { attack: 0.42, defend: 0.35, cast: 0.9, crouch: 0.1, air: 0.46, land: 0.12, JUMP_H: 0.55 };
const QUAD = (() => {
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute([0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0], 3));
  return g;
})();

export class Actors {
  constructor(world, spriteScene, atlasImage, meta, collide) {
    this.world = world; this.scene = spriteScene; this.meta = meta; this.collide = collide;
    this.list = [];
    const tex = new THREE.Texture(atlasImage);
    tex.flipY = false; tex.generateMipmaps = false;
    tex.minFilter = THREE.NearestFilter; tex.magFilter = THREE.NearestFilter;
    tex.colorSpace = THREE.NoColorSpace; tex.needsUpdate = true;
    this.tex = tex;
    this.aw = atlasImage.width; this.ah = atlasImage.height;
    this.fw = meta.frame[0]; this.fh = meta.frame[1];
    this.heightM = 1.8;
    this.k = 3;
    this._v = new THREE.Vector3(); this._w = new THREE.Vector3();
  }

  add(spec) {
    const role = this.meta.roles[spec.role];
    if (!role) throw new Error('no role ' + spec.role);
    const mat = new THREE.ShaderMaterial({
      vertexShader: VERT, fragmentShader: FRAG, glslVersion: THREE.GLSL3, depthTest: true, depthWrite: true,
      uniforms: {
        uAtlas: { value: this.tex }, uFrame: { value: new THREE.Vector2() },
        uFrameSize: { value: new THREE.Vector2(this.fw, this.fh) },
        uPivot: { value: new THREE.Vector2(this.meta.pivot[0], this.meta.pivot[1]) },
        uAnchor: { value: new THREE.Vector2() }, uK: { value: 3 }, uViewport: { value: new THREE.Vector2(1, 1) },
        uZBottom: { value: 0 }, uZTop: { value: 0 }, uTint: { value: new THREE.Vector3(1, 1, 1) },
        uRot: { value: 0 }, uFlash: { value: 0 }, uMode: { value: 0 }, uSil: { value: new THREE.Vector3(0.97, 0.93, 0.82) },
      },
    });
    const quad = new THREE.Mesh(QUAD, mat);
    quad.frustumCulled = false;
    this.scene.add(quad);
    // see-through silhouette (spec.xray, the player): the same quad drawn only where the world is in front of it
    // (GreaterDepth, no depth write) as a dithered palette-colour figure, so a hero behind a cottage stays readable
    let xray = null;
    if (spec.xray) {
      const xm = mat.clone();
      xm.uniforms = THREE.UniformsUtils.clone(mat.uniforms);
      xm.uniforms.uAtlas.value = this.tex; xm.uniforms.uMode.value = 1;
      if (spec.xrayColor) xm.uniforms.uSil.value.copy(spec.xrayColor);
      xm.depthFunc = THREE.GreaterDepth; xm.depthWrite = false;
      xray = new THREE.Mesh(QUAD, xm);
      xray.frustumCulled = false; xray.renderOrder = 5;
      this.scene.add(xray);
    }
    // shadow caster (world scene)
    const ctex = this.tex.clone();
    ctex.flipY = true; ctex.needsUpdate = true;
    ctex.repeat.set(this.fw / this.aw, this.fh / this.ah);
    const isCreature = role.kind !== 'human' && role.kind !== 'enemy';
    const h = this.heightM;
    const w = h * this.fw / this.fh;
    const cg = new THREE.PlaneGeometry(w, h); cg.translate(0, h / 2, 0);
    const caster = new THREE.Mesh(cg, new THREE.MeshBasicMaterial({ colorWrite: false, depthWrite: false, side: THREE.DoubleSide }));
    caster.customDepthMaterial = new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking, map: ctex, alphaTest: 0.5, side: THREE.DoubleSide });
    caster.castShadow = true; caster.receiveShadow = false;
    caster.renderOrder = -1;
    this.world.add(caster);
    const a = {
      id: spec.id || spec.role, role: spec.role, roleRow: role.row, kind: role.kind,
      x: spec.pos[0], z: spec.pos[1], y: 0, facing: spec.facing || 'down', anim: 'idle', t: Math.random() * 3,
      frame: 0, mat, quad, caster, ctex, speed: spec.speed || (isCreature ? 1.7 : 2.2), say: spec.say || null,
      behavior: spec.behavior || 'idle', home: [spec.pos[0], spec.pos[1]], radius: spec.radius || 2.5,
      target: null, wait: 1 + Math.random() * 2, shade: 0, shadeTarget: 0, tint: new THREE.Color(1, 1, 1),
      blinkAt: 2 + Math.random() * 4, idleTurn: spec.turn !== false, r: isCreature ? 0.22 : 0.28, rect: null,
      canCast: (role.anims || []).includes('cast'), castT: 0, castDur: 0.9, spell: spec.spell || null,
      every: spec.every || 4, castClock: spec.castDelay ?? 0.5, name: spec.name,
      anims: role.anims || ['idle', 'walk'], act: null, lift: 0, xray, rot: 0, flashT: 0,
    };
    const h0 = this.collide ? this.collide.height(a.x, a.z) : 0;
    a.y = h0 ?? 0;
    this.list.push(a);
    return a;
  }

  // swap an actor's role in place (a game's hero picker): same position, new atlas row + anims
  setRole(a, roleName) {
    const role = this.meta.roles[roleName];
    if (!role) return false;
    a.role = roleName; a.roleRow = role.row; a.kind = role.kind;
    a.anims = role.anims || ['idle', 'walk']; a.canCast = a.anims.includes('cast');
    a.act = null; a.castT = 0; a.lift = 0;
    return true;
  }

  remove(a) {
    const i = this.list.indexOf(a); if (i >= 0) this.list.splice(i, 1);
    this.scene.remove(a.quad); this.world.remove(a.caster);
    if (a.xray) { this.scene.remove(a.xray); a.xray.material.dispose(); }
    a.mat.dispose(); a.ctex.dispose(); a.caster.geometry.dispose(); a.caster.material.dispose(); a.caster.customDepthMaterial.dispose();
  }

  frameOrigin(a) {
    const fi = FACINGS.indexOf(a.facing);
    const anims = this.meta.anims;
    const has = a.anims ? a.anims.includes(a.anim) : true;   // roles without the anim fall back to idle columns
    const col = ((has && anims[a.anim]) || anims.idle).start + (has ? a.frame : Math.min(a.frame, 3));
    return [col * this.fw, (a.roleRow + fi) * this.fh];
  }

  setFacingFromVec(a, dx, dz) {
    if (Math.abs(dx) < 1e-4 && Math.abs(dz) < 1e-4) return;
    if (Math.abs(dx) > Math.abs(dz) * 1.05) a.facing = dx > 0 ? 'right' : 'left';
    else a.facing = dz > 0 ? 'down' : 'up';
  }

  // Start an action. jump works for every role (non-heroes just hop with idle frames); attack / defend / cast need
  // the anim in the role's atlas. Returns false if the action is unavailable or another one is still running.
  act(a, name, opts = {}) {
    const has = a.anims.includes(name) && this.meta.anims[name];
    if (name !== 'jump' && !has) return false;
    if (a.act && !(a.act.name === name && name === 'defend')) {
      if (a.act.name === 'jump' || a.act.t < a.act.dur) return false;
    }
    const dur = opts.dur || (name === 'jump' ? ACT.crouch + ACT.air + ACT.land : name === 'defend' ? ACT.defend : name === 'cast' ? ACT.cast : ACT.attack);
    a.act = { name, t: 0, dur, held: name === 'defend' && opts.hold !== false, has: !!has, landed: false };
    a.castT = 0;
    return true;
  }

  release(a, name) {
    if (a.act && (!name || a.act.name === name)) a.act.held = false;
  }

  // advance the running action; returns true while it owns the frame
  _actStep(a, dt) {
    const s = a.act, anims = this.meta.anims;
    s.t += dt;
    const p = Math.min(1, s.t / s.dur);
    const n = s.name;
    a.lift = 0;
    if (n === 'jump') {
      const tc = ACT.crouch, ta = ACT.air;
      let f;
      if (s.t < tc) f = 0;
      else if (s.t < tc + ta) {
        const q = (s.t - tc) / ta;
        a.lift = ACT.JUMP_H * Math.sin(Math.PI * q);
        f = q < 0.5 ? 1 : 2;
      } else { f = 3; if (!s.landed) { s.landed = true; s.justLanded = true; } }
      if (s.t >= s.dur) { a.act = null; a.lift = 0; return false; }
      a.anim = s.has ? 'jump' : 'idle'; a.frame = s.has ? f : 0;
      return true;
    }
    if (n === 'defend') {
      if (s.t >= s.dur && !s.held) { a.act = null; return false; }
      const tf = s.t / (ACT.defend / 2);   // raise, set, then pulse the hold frames while the guard is up
      a.anim = 'defend';
      a.frame = tf < 1 ? 0 : tf < 2 ? 1 : (anims.defend.hold || [2, 3])[Math.floor((s.t - ACT.defend) * (anims.defend.fps || 6)) % 2];
      return true;
    }
    if (s.t >= s.dur) { a.act = null; return false; }
    const loop = anims[n].loop || [0, 1, 2, 3];
    a.anim = n; a.frame = loop[Math.min(loop.length - 1, Math.floor(p * loop.length))];
    return true;
  }

  animate(a, dt, moving) {
    const anims = this.meta.anims;
    const prev = a.anim;
    if (a.act && this._actStep(a, dt)) return;
    if (a.castT > 0) {
      a.castT -= dt;
      if (a.canCast && anims.cast) {
        a.anim = 'cast';
        const loop = anims.cast.loop || [0, 1, 2, 3];
        const u = 1 - Math.max(0, a.castT) / a.castDur;
        a.frame = loop[Math.min(loop.length - 1, Math.floor(u * loop.length))];
        return;
      }
    }
    a.anim = moving ? 'walk' : 'idle';
    if (prev !== a.anim) a.t = 0;
    a.t += dt;
    if (a.anim === 'walk') {
      a.frame = Math.floor(a.t * anims.walk.fps * (a.running ? 1.4 : 1)) % 4;
    } else {
      const loop = anims.idle.loop || [0, 1, 2, 1];
      a.frame = loop[Math.floor(a.t * anims.idle.fps) % loop.length];
      a.blinkAt -= dt;
      if (a.blinkAt < 0) { a.frame = anims.idle.blink ?? 3; if (a.blinkAt < -0.16) a.blinkAt = 2.5 + Math.random() * 4; }
    }
  }

  // Integer pixel scale: the walk band's sprite height ≈ the projected 1.8 m figure.
  pixelScale(camera, target, bufH) {
    const p0 = this._v.set(target.x, target.y, target.z).project(camera);
    const p1 = this._w.set(target.x, target.y + this.heightM, target.z).project(camera);
    const px = Math.abs(p1.y - p0.y) * 0.5 * bufH;
    return Math.max(1, Math.round(px / (this.fh - 1)));
  }

  // per-frame: place quads + casters, pixel-snap, light tint
  sync(camera, bufW, bufH, k, grade, lamps, sunDir) {
    this.k = k;
    const tintBase = grade.sprite_tint.clone().convertLinearToSRGB();
    const az = Math.atan2(sunDir.x, sunDir.z);
    const toCam = this._tc || (this._tc = new THREE.Vector3());
    for (const a of this.list) {
      const [fx, fy] = this.frameOrigin(a);
      const u = a.mat.uniforms;
      u.uFrame.value.set(fx, fy);
      u.uK.value = k;
      u.uViewport.value.set(bufW, bufH);
      // feet → pixels, snapped to whole pixels
      // the visible quad rides a.lift (jump arc); depth + shadow stay anchored to the ground under the feet
      const ly = a.y + (a.lift || 0);
      toCam.copy(camera.position).sub(this._v.set(a.x, a.y, a.z)).normalize().multiplyScalar(0.45);
      const feet = this._v.set(a.x, ly, a.z).add(toCam).project(camera);
      const sx = Math.round((feet.x * 0.5 + 0.5) * bufW);
      const sy = Math.round((feet.y * 0.5 + 0.5) * bufH);
      u.uAnchor.value.set(sx, sy);
      u.uZBottom.value = feet.z;
      const head = this._w.set(a.x, ly + this.heightM * (a.kind === 'human' || a.kind === 'enemy' ? 1 : 0.55), a.z).add(toCam).project(camera);
      u.uZTop.value = head.z;
      // light: clock tint, building shade, nearby lamps (warm pools at night)
      const t = a.tint.setRGB(tintBase.r, tintBase.g, tintBase.b);
      t.multiplyScalar(1 - a.shade * 0.32);
      for (const L of lamps) {
        if (L.power <= 0.01) continue;
        const dx = L.pos.x - a.x, dz = L.pos.z - a.z, dy = L.pos.y - (a.y + 1);
        const d = Math.sqrt(dx * dx + dz * dz + dy * dy);
        const f = Math.max(0, 1 - d / L.range);
        if (f <= 0) continue;
        const s = f * f * L.power * 0.55;
        t.r += L.srgb.r * s; t.g += L.srgb.g * s; t.b += L.srgb.b * s;
      }
      u.uTint.value.set(Math.min(t.r, 1.25), Math.min(t.g, 1.25), Math.min(t.b, 1.25));
      u.uRot.value = a.rot || 0;
      u.uFlash.value = a.flashT > 0 ? 0.5 : 0;
      if (a.xray) {   // mirror the live uniforms (values copied, so the silhouette keeps its own mode / colour)
        const xu = a.xray.material.uniforms;
        for (const k2 of ['uFrame', 'uAnchor', 'uViewport']) xu[k2].value.copy(u[k2].value);
        for (const k2 of ['uK', 'uZBottom', 'uZTop', 'uRot']) xu[k2].value = u[k2].value;
        a.xray.visible = a.quad.visible;
      }
      // shadow caster: upright, turned to face the sun, same frame as the visible sprite
      a.caster.position.set(a.x, a.y, a.z);
      a.caster.rotation.set(0, az, 0);
      a.ctex.offset.set(fx / this.aw, 1 - (fy + this.fh) / this.ah);
      if (a.kind !== 'human') a.caster.scale.set(1, 1, 1);
      // CSS-free debug rect (drawing-buffer px, top-left origin) for check-scene
      const x0 = sx - this.meta.pivot[0] * k, yTop = bufH - (sy + this.fh * k);
      a.rect = { x: x0, y: yTop, w: this.fw * k, h: this.fh * k, frame: [fx, fy], k, lift: a.lift || 0 };
    }
  }
}
