// Pixel billboard actors. Two parts per actor:
//  1. SHARP pass quad (drawn after the world post): screen-space, pixel-snapped, integer scale k, texelFetch
//     from the atlas (nearest, no mips), depth from the cylindrical billboard so roofs/walls still occlude.
//  2. Shadow caster in the WORLD scene: an upright cylindrical-billboard plane turned toward the sun, invisible
//     in colour, with an alpha-tested customDepthMaterial so the real silhouette lands in the shadow map.
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
out vec4 outColor;
void main() {
  vec2 origin = vec2(uAnchor.x - uPivot.x * uK, uAnchor.y - (uFrameSize.y - uPivot.y) * uK);
  ivec2 t = ivec2(floor((gl_FragCoord.xy - origin) / uK));
  t = clamp(t, ivec2(0), ivec2(uFrameSize) - 1);
  ivec2 at = ivec2(int(uFrame.x) + t.x, int(uFrame.y) + int(uFrameSize.y) - 1 - t.y);
  vec4 c = texelFetch(uAtlas, at, 0);
  if (c.a < 0.5) discard;           // hard alpha only
  outColor = vec4(min(c.rgb * uTint, vec3(1.0)), 1.0);
}`;

const FACINGS = ['down', 'up', 'left', 'right'];
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
      },
    });
    const quad = new THREE.Mesh(QUAD, mat);
    quad.frustumCulled = false;
    this.scene.add(quad);
    // shadow caster (world scene)
    const ctex = this.tex.clone();
    ctex.flipY = true; ctex.needsUpdate = true;
    ctex.repeat.set(this.fw / this.aw, this.fh / this.ah);
    const isCreature = role.kind !== 'human';
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
    };
    const h0 = this.collide ? this.collide.height(a.x, a.z) : 0;
    a.y = h0 ?? 0;
    this.list.push(a);
    return a;
  }

  remove(a) {
    const i = this.list.indexOf(a); if (i >= 0) this.list.splice(i, 1);
    this.scene.remove(a.quad); this.world.remove(a.caster);
    a.mat.dispose(); a.ctex.dispose(); a.caster.geometry.dispose(); a.caster.material.dispose(); a.caster.customDepthMaterial.dispose();
  }

  frameOrigin(a) {
    const fi = FACINGS.indexOf(a.facing);
    const anims = this.meta.anims;
    const col = (anims[a.anim] || anims.idle).start + a.frame;
    return [col * this.fw, (a.roleRow + fi) * this.fh];
  }

  setFacingFromVec(a, dx, dz) {
    if (Math.abs(dx) < 1e-4 && Math.abs(dz) < 1e-4) return;
    if (Math.abs(dx) > Math.abs(dz) * 1.05) a.facing = dx > 0 ? 'right' : 'left';
    else a.facing = dz > 0 ? 'down' : 'up';
  }

  animate(a, dt, moving) {
    const anims = this.meta.anims;
    const prev = a.anim;
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
      toCam.copy(camera.position).sub(this._v.set(a.x, a.y, a.z)).normalize().multiplyScalar(0.45);
      const feet = this._v.set(a.x, a.y, a.z).add(toCam).project(camera);
      const sx = Math.round((feet.x * 0.5 + 0.5) * bufW);
      const sy = Math.round((feet.y * 0.5 + 0.5) * bufH);
      u.uAnchor.value.set(sx, sy);
      u.uZBottom.value = feet.z;
      const head = this._w.set(a.x, a.y + this.heightM * (a.kind === 'human' ? 1 : 0.55), a.z).add(toCam).project(camera);
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
      // shadow caster: upright, turned to face the sun, same frame as the visible sprite
      a.caster.position.set(a.x, a.y, a.z);
      a.caster.rotation.set(0, az, 0);
      a.ctex.offset.set(fx / this.aw, 1 - (fy + this.fh) / this.ah);
      if (a.kind !== 'human') a.caster.scale.set(1, 1, 1);
      // CSS-free debug rect (drawing-buffer px, top-left origin) for check-scene
      const x0 = sx - this.meta.pivot[0] * k, yTop = bufH - (sy + this.fh * k);
      a.rect = { x: x0, y: yTop, w: this.fw * k, h: this.fh * k, frame: [fx, fy], k };
    }
  }
}
