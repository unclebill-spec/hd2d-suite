// World-only post: tilt-shift focus band + distance/valley haze + palette grade + soft shoulder (no bloom).
// The composite writes the world depth back (gl_FragDepth) so the SHARP sprite pass that follows can be
// depth-tested against the world without ever passing through this blur.
import * as THREE from 'three';

const VERT = /* glsl */`
out vec2 vUv;
void main() { vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }`;

const FRAG = /* glsl */`
precision highp float;
in vec2 vUv;
out vec4 outColor;
uniform sampler2D tColor;
uniform sampler2D tDepth;
uniform vec2 uRes;            // world RT size (px)
uniform float uOutScale;      // RT px per output px
uniform mat4 uInvProj;
uniform mat4 uInvView;
uniform float uFocusY, uBand, uFalloff, uMaxBlur, uFarBlur;
uniform vec3 uFog; uniform float uFogNear, uFogFar, uHaze, uValley, uDistOff;
uniform vec3 uSkyTop, uSkyBottom;
uniform float uExposure, uSat, uWarmth, uVignette;
uniform vec3 uShadowTint;

vec3 viewPos(vec2 uv, float d) {
  vec4 p = uInvProj * vec4(uv * 2.0 - 1.0, d * 2.0 - 1.0, 1.0);
  return p.xyz / p.w;
}
vec3 shoulder(vec3 c) {               // keeps highlights under 1.0: no blown whites, no glow
  vec3 k = 0.78 + 0.22 * (1.0 - exp(-(c - 0.78) / 0.22));
  return mix(c, k, step(0.78, c));
}
vec3 toSRGB(vec3 c) {
  c = clamp(c, 0.0, 1.0);
  return mix(c * 12.92, 1.055 * pow(c, vec3(1.0 / 2.4)) - 0.055, step(0.0031308, c));
}
void main() {
  float d = texture(tDepth, vUv).x;
  vec3 col;
  if (d >= 0.999999) {
    float t = smoothstep(0.25, 1.0, vUv.y);
    col = mix(uSkyBottom, uSkyTop, t);
  } else {
    vec3 vp = viewPos(vUv, d);
    float dist = max(0.0, length(vp) - uDistOff);   // haze relative to the authored camera distance
    vec3 wp = (uInvView * vec4(vp, 1.0)).xyz;
    // tilt-shift: only the walk band stays sharp; far rows and the foreground go soft
    float off = abs(vUv.y - uFocusY);
    float r = uMaxBlur * smoothstep(uBand, uBand + uFalloff, off);
    r = max(r, uFarBlur * smoothstep(uFogNear, uFogFar, dist));
    r *= uOutScale;
    vec3 acc = texture(tColor, vUv).rgb;
    float wsum = 1.0;
    if (r > 0.35) {
      const float GA = 2.39996323;
      for (int i = 1; i < 14; i++) {
        float fi = float(i);
        float rr = r * sqrt(fi / 13.0);
        vec2 o = vec2(cos(fi * GA), sin(fi * GA)) * rr / uRes;
        float sd = texture(tDepth, vUv + o).x;
        // do not drag a sharp near object's colour into a far blurred pixel too strongly
        float w = sd < 0.999999 ? 1.0 : 0.6;
        acc += texture(tColor, vUv + o).rgb * w;
        wsum += w;
      }
    }
    col = acc / wsum;
    // distance haze + valley haze (low ground far away fills with soft air)
    float f = uHaze * smoothstep(uFogNear, uFogFar, dist);
    float v = uValley * (1.0 - smoothstep(-1.5, 2.5, wp.y)) * smoothstep(10.0, 34.0, dist);
    col = mix(col, uFog, clamp(f + v, 0.0, 0.8));
  }
  // grade
  col *= uExposure;
  float l = dot(col, vec3(0.2126, 0.7152, 0.0722));
  col = mix(vec3(l), col, uSat);
  col += uShadowTint * 0.06 * (1.0 - smoothstep(0.0, 0.35, l));
  col.r *= 1.0 + uWarmth; col.b *= 1.0 - uWarmth;
  col = shoulder(col);
  vec2 q = vUv - 0.5;
  col *= 1.0 - uVignette * smoothstep(0.35, 0.85, length(q * vec2(1.1, 1.0)));
  outColor = vec4(toSRGB(col), 1.0);
  gl_FragDepth = d;
}`;

export class Post {
  constructor(renderer, ss = 1.0) {
    this.renderer = renderer;
    this.ss = ss;
    const caps = renderer.capabilities;
    const type = caps.isWebGL2 ? THREE.HalfFloatType : THREE.UnsignedByteType;
    this.rt = new THREE.WebGLRenderTarget(4, 4, { type, depthBuffer: true, samples: 0 });
    this.rt.texture.minFilter = THREE.LinearFilter;
    this.rt.texture.magFilter = THREE.LinearFilter;
    this.rt.texture.generateMipmaps = false;
    this.rt.depthTexture = new THREE.DepthTexture(4, 4);
    this.rt.depthTexture.type = THREE.UnsignedIntType;
    this.rt.depthTexture.minFilter = THREE.NearestFilter;
    this.rt.depthTexture.magFilter = THREE.NearestFilter;
    this.mat = new THREE.ShaderMaterial({
      glslVersion: THREE.GLSL3, vertexShader: VERT, fragmentShader: FRAG,
      depthTest: true, depthWrite: true, depthFunc: THREE.AlwaysDepth,
      uniforms: {
        tColor: { value: this.rt.texture }, tDepth: { value: this.rt.depthTexture },
        uRes: { value: new THREE.Vector2() }, uOutScale: { value: ss },
        uInvProj: { value: new THREE.Matrix4() }, uInvView: { value: new THREE.Matrix4() },
        uFocusY: { value: 0.46 }, uBand: { value: 0.13 }, uFalloff: { value: 0.32 }, uMaxBlur: { value: 2.6 }, uFarBlur: { value: 2.0 },
        uFog: { value: new THREE.Color() }, uFogNear: { value: 30 }, uFogFar: { value: 80 }, uHaze: { value: 0.3 }, uValley: { value: 0.1 }, uDistOff: { value: 0 },
        uSkyTop: { value: new THREE.Color() }, uSkyBottom: { value: new THREE.Color() },
        uExposure: { value: 1 }, uSat: { value: 1 }, uWarmth: { value: 0 }, uVignette: { value: 0.16 },
        uShadowTint: { value: new THREE.Color() },
      },
    });
    this.quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), this.mat);
    this.quad.frustumCulled = false;
    this.scene = new THREE.Scene();
    this.scene.add(this.quad);
    this.cam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    this.enabled = true;
  }
  setSize(w, h) {
    const W = Math.round(w * this.ss), H = Math.round(h * this.ss);
    this.rt.setSize(W, H);
    this.mat.uniforms.uRes.value.set(W, H);
    this.outW = w; this.outH = h;
  }
  setGrade(g, focusY) {
    const u = this.mat.uniforms;
    u.uFog.value.copy(g.fog_color); u.uFogNear.value = g.fog_near; u.uFogFar.value = g.fog_far;
    u.uHaze.value = g.haze; u.uValley.value = g.valley_haze;
    u.uSkyTop.value.copy(g.sky_top); u.uSkyBottom.value.copy(g.sky_bottom);
    u.uExposure.value = g.exposure; u.uSat.value = g.saturation; u.uWarmth.value = g.warmth;
    u.uShadowTint.value.copy(g.shadow_tint);
    if (focusY !== undefined) u.uFocusY.value = focusY;
  }
  dispose() { this.rt.depthTexture.dispose(); this.rt.dispose(); this.mat.dispose(); this.quad.geometry.dispose(); }
  render(worldScene, camera) {
    const r = this.renderer;
    const u = this.mat.uniforms;
    u.uInvProj.value.copy(camera.projectionMatrixInverse);
    u.uInvView.value.copy(camera.matrixWorld);
    u.uDistOff.value = camera.userData.hazeOff || 0;
    r.setRenderTarget(this.rt);
    r.setClearColor(0x000000, 1);
    r.clear(true, true, true);
    r.render(worldScene, camera);
    r.setRenderTarget(null);
    r.clear(true, true, true);
    r.render(this.scene, this.cam);   // blurred, hazed, graded world + its depth
  }
}
