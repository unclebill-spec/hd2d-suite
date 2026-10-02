// hd2d runtime: locked 3/4 diorama camera, lit kit world (+tilt-shift/haze post), sharp pixel actors on top.
import * as THREE from 'three';
import { Clock, NAMED_TIMES } from './clock.js';
import { Collide } from './collide.js';
import { Post } from './post.js';
import { Actors } from './sprites.js';
import { Particles, mulberry } from './particles.js';
import { loadGLB, loadImage, litify, buildTrees, swayTrees } from './world.js';
import { Pad } from './pad.js';
import { Effects } from './effects.js';
import { Nav } from './nav.js';
import { GamepadInput } from './gamepad.js';

const Q = new URLSearchParams(location.search);
const $ = (id) => document.getElementById(id);
const API = (window.__hd2d = window.__hd2d || { ready: false, frames: 0, errors: [] });

// ---------------------------------------------------------------- page-level input guards (installed once)
// 1) loading gate: from the start of boot() until the first frames of the area are on screen, every pointer,
//    touch, mouse, key and wheel event is swallowed (capture phase on window, before any game listener), so an
//    early tap can't queue a walk or skip the title. body.loading + the #boot overlay show the state.
// 2) no page scroll / zoom: iOS gesture* events, double-tap zoom, pull-to-refresh / overscroll, ctrl+wheel
//    page zoom and long-press menus are blocked; pinch stays an in-game camera zoom (pointer events).
// 3) input scheme: any touch brings the on-screen pad back (drops body.ctrl, set while a controller is used).
const GATE = (window.__hd2dGate = window.__hd2dGate || { loading: true, swallowed: 0 });
if (!window.__hd2dGuards) {
  window.__hd2dGuards = true;
  document.body && document.body.classList.add('loading');
  const swallow = (e) => {
    if (!GATE.loading) return;
    GATE.swallowed++;
    if (e.cancelable) e.preventDefault();
    e.stopImmediatePropagation();
  };
  for (const t of ['pointerdown', 'pointerup', 'pointermove', 'pointercancel', 'touchstart', 'touchmove', 'touchend', 'mousedown', 'mouseup',
                   'click', 'dblclick', 'keydown', 'keyup', 'wheel', 'contextmenu']) {
    addEventListener(t, swallow, { capture: true, passive: false });
  }
  addEventListener('pointerdown', (e) => { if (e.pointerType === 'touch' && document.body.classList.contains('ctrl')) setCtrl(false); }, { capture: true });
  const stop = (e) => { if (e.cancelable) e.preventDefault(); };
  for (const t of ['gesturestart', 'gesturechange', 'gestureend']) document.addEventListener(t, stop, { passive: false });
  document.addEventListener('dblclick', stop, { passive: false });
  const scrollable = (t) => t && t.closest && t.closest('[data-scroll]');
  document.addEventListener('touchmove', (e) => { if (e.touches.length > 1 || !scrollable(e.target)) stop(e); }, { passive: false });
  let lastEnd = -1e9;
  document.addEventListener('touchend', (e) => {
    // a second tap within 320 ms would be a double-tap zoom on older iOS; buttons keep their click
    if (e.timeStamp - lastEnd < 320 && !(e.target.closest && e.target.closest('button,a,input,select,textarea,[data-scroll]'))) stop(e);
    lastEnd = e.timeStamp;
  }, { passive: false });
  addEventListener('wheel', (e) => { if (e.ctrlKey) stop(e); }, { passive: false });
  document.addEventListener('contextmenu', (e) => { if (!(e.target.closest && e.target.closest('input,textarea'))) stop(e); });
}
function setGate(loading) {
  GATE.loading = loading;
  document.body.classList.toggle('loading', loading);
  const b = document.getElementById('boot');
  if (b && !loading) b.classList.add('gone');
}
// controller mode: hide the on-screen pad while a gamepad drives the game; the hint shows the controller keys
function setCtrl(on) {
  const body = document.body;
  if (body.classList.contains('ctrl') === on) return;
  body.classList.toggle('ctrl', on);
  const h = document.getElementById('hint');
  if (h) {
    if (on) { h.dataset.keys = h.dataset.keys || h.textContent; h.textContent = h.dataset.pad || '🎮 stick walk · A talk · B close · X cast · Y / LB / RB charm · LT / RT zoom · Start menu · Select pad'; }
    else if (h.dataset.keys) h.textContent = h.dataset.keys;
  }
}
// a small parchment toast for engine messages (a game can pass opts.toast to use its own)
function engineToast(msg, s = 2.4) {
  let el = document.getElementById('etoast');
  if (!el) { el = document.createElement('div'); el.id = 'etoast'; el.className = 'chip etoast'; (document.getElementById('hud') || document.body).appendChild(el); }
  el.textContent = msg; el.hidden = false;
  clearTimeout(engineToast.t); engineToast.t = setTimeout(() => { el.hidden = true; }, s * 1000);
}

// boot(opts): one area. Demos autoboot with defaults; a game calls boot() per area and dispose()s the handle.
//   opts.base        URL prefix for scene.json and every asset path inside it ('' = page folder)
//   opts.canvas      canvas element (default #view)
//   opts.spawn       {x, z, facing} player start override;  opts.player: player spec overrides (role, ...)
//   opts.startT      clock time 0..1;  opts.clockSpeed: cycles per second
//   opts.spellCycle  spells the player can cast (default: scene.spell_cycle or the spells atlas cycle)
//   opts.hooks       { onInteract(ctx), onTalk(npc, ctx), onTap(hit, ctx), onFrame(dt, ctx), blockInput() }
export async function boot(opts = {}) {
  const base = opts.base ?? '';
  const R = (u) => (u && !/^(https?:|data:|blob:|\/)/.test(u) ? base + u : u);
  const hooks = opts.hooks || {};
  const ac = new AbortController(), sig = { signal: ac.signal };
  let alive = true;
  setGate(true);
  const toast = opts.toast || engineToast;
  const scene = await (await fetch(R(Q.get('scene') || 'scene.json'))).json();
  const biome = await (await fetch(R(scene.palette))).json();
  const atlasMeta = await (await fetch(R(scene.atlas.json))).json();
  const atlasImg = await loadImage(R(scene.atlas.image));
  const pMeta = scene.particles ? await (await fetch(R(scene.particles.json))).json() : null;
  const pImg = pMeta ? await loadImage(R(scene.particles.image)) : null;
  const treesMeta = scene.trees_meta ? await (await fetch(R(scene.trees_meta))).json() : { trees: {} };
  const sMeta = scene.spells ? await (await fetch(R(scene.spells.json))).json() : null;
  const sImg = sMeta ? await loadImage(R(scene.spells.image)) : null;
  const gMeta = scene.gamefx ? await (await fetch(R(scene.gamefx.json))).json() : null;
  const gImg = gMeta ? await loadImage(R(scene.gamefx.image)) : null;
  if (!opts.keepTitle) document.title = scene.name;
  if ($('title')) $('title').textContent = scene.name;
  const canvas = opts.canvas || $('view');

  // ---------------------------------------------------------------- renderer
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, powerPreference: 'high-performance', preserveDrawingBuffer: Q.has('shot') });
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  renderer.setPixelRatio(dpr);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.NoToneMapping;
  renderer.autoClear = false;
  const ss = Number(Q.get('ss') || (Math.min(innerWidth, innerHeight) < 600 ? 1.0 : 1.5));
  const post = new Post(renderer, ss);

  const world = new THREE.Scene();
  const sharp = new THREE.Scene();   // sprites + particles: never blurred

  // ---------------------------------------------------------------- camera (locked 3/4)
  const C = scene.camera;
  const camera = new THREE.PerspectiveCamera(C.fov, 1, 1, 260);
  const pitch = THREE.MathUtils.degToRad(C.pitch);
  const camDir = new THREE.Vector3(0, Math.sin(pitch), Math.cos(pitch));   // from target toward camera
  let dist = C.distance;
  const zoomRange = C.zoom;
  const target = new THREE.Vector3(...(C.target || [0, 0, 0]));
  const bounds = C.bounds; // [x0, z0, x1, z1] for the target
  const look = new THREE.Vector3(...(C.look || [0, 0, -3]));   // frame ahead of the player (the terrace)
  function aspectScale() { const a = innerWidth / innerHeight; return a < 1.25 ? Math.min(1.9, 1.25 / a) : 1; }
  function placeCamera() {
    const d = dist * aspectScale();
    camera.position.copy(target).addScaledVector(camDir, d);
    camera.userData.hazeOff = d - C.distance;   // portrait / zoom pull-back does not add fog
    camera.quaternion.setFromEuler(new THREE.Euler(-pitch, 0, 0, 'YXZ'));   // fixed: no orbit, no yaw
    camera.updateMatrixWorld();
  }

  // ---------------------------------------------------------------- lights
  const hemi = new THREE.HemisphereLight(0xffffff, 0x444444, 1);
  world.add(hemi);
  const sun = new THREE.DirectionalLight(0xffffff, 2);
  sun.castShadow = true;
  const sb = scene.shadow_box || 24;
  Object.assign(sun.shadow.camera, { left: -sb, right: sb, top: sb, bottom: -sb, near: 1, far: 120 });
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.bias = -0.0004;
  sun.shadow.normalBias = 0.035;
  sun.shadow.radius = 3;
  world.add(sun, sun.target);

  // per-scene grade tweaks on top of the biome palette (e.g. a lamp-dense lane wants a slightly darker night)
  for (const [gname, over] of Object.entries(scene.grades || {})) Object.assign(biome.grades[gname] || {}, over);
  const clock = new Clock(biome, opts.startT ?? startTime(scene), opts.clockSpeed ?? scene.time?.speed ?? 1 / 480);
  if (Q.has('freeze') || scene.time?.freeze) clock.paused = true;

  // ---------------------------------------------------------------- world objects
  const slots = { windows: [], lamps: [] };
  const occluders = [];
  await Promise.all(scene.objects.map(async (ob) => {
    const g = litify(await loadGLB(R(ob.glb)), slots);
    g.position.set(...ob.pos);
    g.rotation.y = THREE.MathUtils.degToRad(ob.rot || 0);
    if (ob.scale) g.scale.setScalar(ob.scale);
    g.traverse((o) => { if (o.isMesh) { o.castShadow = ob.cast !== false; o.receiveShadow = ob.receive !== false; } });
    if (ob.walkable) g.userData.walkable = true;
    if (ob.occluder) occluders.push(g);
    world.add(g);
  }));
  const rnd = mulberry(scene.seed || 1);
  const trees = await buildTrees(world, R(scene.trees_base || ''), treesMeta, scene.trees || [], rnd);
  for (const t of trees) occluders.push(t);
  world.updateMatrixWorld(true);

  // lamps: point lights (capped) + 4-frame flicker glow sprites
  const lampDefs = scene.lamps || [];
  const lamps = lampDefs.map((L, i) => {
    const light = L.light !== false && i < (sMeta ? 7 : 8) ? new THREE.PointLight(new THREE.Color(L.color || biome.colors.lamp), 0, L.range || 7, 2.0) : null;
    if (light) { light.position.set(...L.pos); world.add(light); }
    const c = new THREE.Color(L.color || biome.colors.lamp);
    return { kind: L.kind, pos: new THREE.Vector3(...L.pos), range: L.range || 9, light, power: 0, phase: i * 0.37, srgb: c.clone().convertLinearToSRGB(), glow: L.glow !== false, tint: L.color ? c : null, fixed: L.fixed ?? null };
  });

  // ---------------------------------------------------------------- collision + actors
  const collide = scene.collision ? new Collide(scene.collision) : null;
  const actors = new Actors(world, sharp, atlasImg, atlasMeta, collide);
  const nav = collide ? new Nav(collide, 0.3) : null;
  const npcs = (scene.actors || []).filter((s) => !(hooks.skipActor && hooks.skipActor(s))).map((s) => actors.add(s));
  const pspec = { ...scene.player, ...(opts.player || {}) };
  if (opts.spawn) { pspec.pos = [opts.spawn.x, opts.spawn.z]; if (opts.spawn.facing) pspec.facing = opts.spawn.facing; }
  const player = actors.add({ ...pspec, id: 'player', behavior: 'player', turn: false });
  player.speed = 2.6;

  // particles
  let particles = null;
  const showcase = Q.get('showcase');
  if (pMeta) {
    particles = new Particles(sharp, pImg, pMeta, 900);
    if (showcase !== 'particles') for (const e of scene.emitters || []) particles.addEmitter(e);
    const weather = Q.get('weather') ?? scene.weather;
    if (weather && weather !== 'none' && showcase !== 'particles') particles.addEmitter({ preset: weather === 'snow' ? 'snowfall' : weather });
    particles.followPos = { x: 0, z: 0 };
    particles.groundAt = (x, z) => (collide ? (collide.height(x, z) ?? 0) : 0);
  }
  // spell effects (sharp pass) + the player's spell cycle
  const effects = sMeta ? new Effects(world, sharp, sImg, sMeta) : null;
  // game art (portal vortex, ground rings, pickups): persistent looping billboards/decals, no extra lights
  const gamefx = gMeta ? new Effects(world, sharp, gImg, gMeta, 0) : null;
  const fxPlaced = {};
  if (gamefx) for (const f of scene.fx || []) fxPlaced[f.id || f.name] = gamefx.spawn(f.name, f.pos[0], f.pos[1], f.pos[2], { duration: Infinity });
  let spellCycle = sMeta ? (opts.spellCycle || scene.spell_cycle || sMeta.cycle).filter((n) => sMeta.cast_sets[n] || sMeta.effects[n]) : [];
  let spellIdx = 0;
  function facingVec(a) { return { down: [0, 1], up: [0, -1], left: [-1, 0], right: [1, 0] }[a.facing] || [0, 1]; }
  function castSpell(a, name) {
    if (!effects) return;
    const set = sMeta.cast_sets[name] || [[name, 'front']];
    if (!a.act) a.castT = a.castDur;   // mid-jump / mid-swing casts still fire, without restarting the pose
    const [fx, fz] = facingVec(a);
    for (const [fxName, where] of set) {
      if (where === 'feet') effects.spawn(fxName, a.x, a.y, a.z + 0.05);
      else if (where === 'hands') {
        const tx = a.x + fx * 4.5, tz = a.z + fz * 4.5;
        const ty = collide ? (collide.height(tx, tz) ?? a.y) : a.y;
        effects.spawn(fxName, a.x + fx * 0.4, a.y, a.z + fz * 0.4 + 0.05, { to: [tx, ty, tz] });
      } else effects.spawn(fxName, a.x + fx * 0.95, a.y, a.z + fz * 0.95 + 0.05);
    }
  }
  function playerCast(advance = true) {
    if (!spellCycle.length) return;
    castSpell(player, spellCycle[spellIdx]);
    if (advance) spellIdx = (spellIdx + 1) % spellCycle.length;
    showSpell();
  }
  function cycleSpell(dir = 1) { if (spellCycle.length) { spellIdx = (spellIdx + dir + spellCycle.length) % spellCycle.length; showSpell(); } }
  function showSpell() { const b = $('btnSpell'); if (b) b.textContent = '✦ ' + (spellCycle[spellIdx] || '').replace(/_/g, ' '); }

  // hero action states (R attack, C hold to guard, Z jump; controller RS attack, LS jump, LT short guard)
  function actorAct(name, a = player, opts = {}) {
    if (a === player && blocked()) return false;
    const ok = actors.act(a, name, opts);
    if (ok && a === player && name !== 'jump') walkTo = null;
    return ok;
  }

  // ---------------------------------------------------------------- input
  const keys = new Set();
  let walkTo = null;   // { pts: [[x, z], ...], i, talk?, arrive? }
  const blocked = () => !!(hooks.blockInput && hooks.blockInput());
  // walk along an A* path (falls back to a straight line when there is no heightfield)
  function walkPath(x, z, extra = {}) {
    const pts = nav ? nav.path(player.x, player.z, x, z) : [[x, z]];
    if (!pts || !pts.length) { walkTo = null; return false; }
    walkTo = { pts, i: 0, ...extra };
    return true;
  }
  addEventListener('keydown', (e) => {
    if (e.target && /INPUT|TEXTAREA/.test(e.target.tagName)) return;
    const k = e.key.toLowerCase();
    keys.add(k);
    if (['e', ' ', 'enter'].includes(k)) { e.preventDefault(); if (!e.repeat) interact(); }
    if (blocked()) return;
    if (k === 't' && !opts.noTimeKeys) stepTime();
    if (k === 'f' && !e.repeat) playerCast(true);
    if (k === 'q' && !e.repeat) cycleSpell();
    if (k === 'r' && !e.repeat) actorAct('attack');
    if (k === 'c' && !e.repeat) actorAct('defend', player, { hold: true });
    if (k === 'z' && !e.repeat) actorAct('jump');
    if (k === 'p' && !opts.noTimeKeys) togglePause();
    if (k === 'g') togglePad();
    if (k === 'h') toggleHand();
    if (e.key === '+' || e.key === '=') zoomBy(0.92);
    if (e.key === '-') zoomBy(1.08);
  }, sig);
  addEventListener('keyup', (e) => { const k = e.key.toLowerCase(); keys.delete(k); if (k === 'c') actors.release(player, 'defend'); }, sig);
  addEventListener('blur', () => { keys.clear(); actors.release(player, 'defend'); }, sig);
  // taps on the canvas (event time, not handler time: a janky frame must not turn a tap into a hold)
  const pointers = new Map();
  canvas.addEventListener('pointerdown', (e) => {
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY, x0: e.clientX, y0: e.clientY, t0: e.timeStamp });
  }, sig);
  canvas.addEventListener('pointermove', (e) => {
    const p = pointers.get(e.pointerId); if (!p) return;
    p.x = e.clientX; p.y = e.clientY;
    // a one-finger drag does nothing on purpose: the camera is locked
  }, sig);
  const endPointer = (e) => {
    const p = pointers.get(e.pointerId); if (!p) return;
    pointers.delete(e.pointerId);
    const moved = Math.hypot(p.x - p.x0, p.y - p.y0);
    if (moved < 12 && e.timeStamp - p.t0 < 600 && pointers.size === 0 && !pinchUsed) tapAt(p.x, p.y);
    if (pointers.size === 0 && touches.size === 0) pinchUsed = false;
  };
  canvas.addEventListener('pointerup', endPointer, sig);
  canvas.addEventListener('pointercancel', (e) => { pointers.delete(e.pointerId); }, sig);
  // pinch = camera zoom: two touches anywhere on the canvas or the stick zone (window capture phase, so a finger
  // that lands in the floating-stick zone still counts). A stick the thumb has only just put down (not dragged,
  // < 300 ms) gives way to the pinch; a thumb already steering keeps the stick.
  const touches = new Map();
  let pinch0 = null, pinchUsed = false;
  const onPlayfield = (t) => t === canvas || !!(t && t.closest && t.closest('#stickZone'));
  addEventListener('pointerdown', (e) => {
    if (e.pointerType === 'mouse' || !onPlayfield(e.target)) return;
    touches.set(e.pointerId, { x: e.clientX, y: e.clientY, zone: e.target !== canvas });
    if (touches.size === 2 && [...touches.values()].every((p) => !p.zone || pad.fresh(e.timeStamp))) {
      const [a, b] = [...touches.values()];
      pinch0 = { d: Math.hypot(a.x - b.x, a.y - b.y), dist }; pinchUsed = true;
      pad.release();
    }
  }, { capture: true, signal: ac.signal });
  addEventListener('pointermove', (e) => {
    const p = touches.get(e.pointerId); if (!p) return;
    p.x = e.clientX; p.y = e.clientY;
    if (pinch0 && touches.size === 2) {
      const [a, b] = [...touches.values()];
      dist = THREE.MathUtils.clamp(pinch0.dist * pinch0.d / Math.max(Math.hypot(a.x - b.x, a.y - b.y), 1), zoomRange[0], zoomRange[1]);
    }
  }, { capture: true, signal: ac.signal });
  const endTouch = (e) => { if (touches.delete(e.pointerId) && touches.size < 2) pinch0 = null; if (touches.size === 0 && pointers.size === 0) setTimeout(() => { if (!touches.size) pinchUsed = false; }, 0); };
  addEventListener('pointerup', endTouch, { capture: true, signal: ac.signal });
  addEventListener('pointercancel', endTouch, { capture: true, signal: ac.signal });
  canvas.addEventListener('wheel', (e) => { e.preventDefault(); zoomBy(e.deltaY > 0 ? 1.06 : 0.94); }, { passive: false, signal: ac.signal });
  function zoomBy(f) { dist = THREE.MathUtils.clamp(dist * f, zoomRange[0], zoomRange[1]); }

  const ray = new THREE.Raycaster();
  const walkables = [];
  world.traverse((o) => { if (o.isMesh) { let p = o; while (p) { if (p.userData.walkable) { walkables.push(o); break; } p = p.parent; } } });
  function tapAt(cx, cy) {
    if (blocked()) { if (hooks.onInteract) hooks.onInteract(ctx, 'tap'); return; }
    // talk if the tap lands on an NPC sprite (buffer px; the rects are in drawing-buffer pixels)
    const bx = cx * bufW / innerWidth, by = cy * bufH / innerHeight;
    for (const a of npcs) {
      const r = a.rect;
      if (a.quad.visible && r && bx >= r.x && bx < r.x + r.w && by >= r.y && by < r.y + r.h) {
        if (Math.hypot(a.x - player.x, a.z - player.z) < 2.4) { talk(a); return; }
        const dx = player.x - a.x, dz = player.z - a.z, L = Math.hypot(dx, dz) || 1;
        walkPath(a.x + dx / L * 1.1, a.z + dz / L * 1.1, { talk: a });
        return;
      }
    }
    ray.setFromCamera(new THREE.Vector2(cx / innerWidth * 2 - 1, -(cy / innerHeight) * 2 + 1), camera);
    const hit = ray.intersectObjects(walkables, false)[0];
    if (!hit) return;
    if (hooks.onTap && hooks.onTap({ x: hit.point.x, y: hit.point.y, z: hit.point.z }, ctx)) return;
    walkPath(hit.point.x, hit.point.z);
  }

  // ---------------------------------------------------------------- talk (parchment bubble)
  let sayTimer = 0;
  function talk(a) {
    actors.setFacingFromVec(player, a.x - player.x, a.z - player.z);
    if (hooks.onTalk && hooks.onTalk(a, ctx)) { actors.setFacingFromVec(a, player.x - a.x, player.z - a.z); a.wait = 4; a.target = null; return; }
    if (!a.say) return;
    const lines = Array.isArray(a.say) ? a.say : [a.say];
    a.sayIdx = ((a.sayIdx ?? -1) + 1) % lines.length;
    $('say').innerHTML = `<b>${a.name || a.role}</b> — ${lines[a.sayIdx]}`;
    $('say').hidden = false;
    sayTimer = 4.5;
    actors.setFacingFromVec(a, player.x - a.x, player.z - a.z);
    a.wait = 3; a.target = null;
    actors.setFacingFromVec(player, a.x - player.x, a.z - player.z);
  }
  function nearestNpc(maxd = 2.2) {
    let best = null, bd = maxd;
    for (const a of npcs) { const d = Math.hypot(a.x - player.x, a.z - player.z); if (d < bd && (a.say || a.talkable) && a.quad.visible) { bd = d; best = a; } }
    return best;
  }
  function interact() {
    if (hooks.onInteract && hooks.onInteract(ctx, 'key')) return;
    if (blocked()) return;
    const n = nearestNpc(); if (n) talk(n);
  }

  // ---------------------------------------------------------------- HUD
  const pad = new Pad({ onMain: interact, near: () => !!nearestNpc(), onSpell: sMeta ? () => playerCast(true) : null,
                       onSpellHold: sMeta ? () => cycleSpell(1) : null, onTap: (x, y) => tapAt(x, y), blockStart: () => !!pinch0, signal: ac.signal });
  if (sMeta && !$('btnSpell') && document.querySelector('#hud .btns')) {
    const b = document.createElement('button');
    b.className = 'chip btn'; b.id = 'btnSpell'; b.title = 'Cast the spell (F), next spell (Q)';
    document.querySelector('#hud .btns').appendChild(b);
    if ($('hint') && !$('hint').textContent.includes('F cast')) $('hint').textContent += ' · F cast · Q next spell';
  }
  if ($('hint') && player.anims.includes('attack') && !$('hint').textContent.includes('R attack')) $('hint').textContent += ' · R attack · C guard · Z jump';
  if ($('btnSpell')) { $('btnSpell').onclick = () => playerCast(true); $('btnSpell').hidden = !spellCycle.length; }
  showSpell();
  // left-handed pad: ?hand=left, the 'hand' HUD chip or H; remembered per device
  function setHand(left) {
    document.body.classList.toggle('lefthand', left);
    try { localStorage.setItem('hd2d-hand', left ? 'left' : 'right'); } catch (e) { /* private mode */ }
    if ($('btnHand')) { $('btnHand').textContent = left ? 'hand: L' : 'hand: R'; $('btnHand').classList.toggle('on', left); }
  }
  function toggleHand() { setHand(!document.body.classList.contains('lefthand')); }
  function togglePad() { pad.toggle(); if ($('btnPad')) $('btnPad').classList.toggle('on', pad.on); }
  let handPref = null;
  try { handPref = localStorage.getItem('hd2d-hand'); } catch (e) { /* private mode */ }
  setHand((Q.get('hand') || handPref) === 'left');
  function stepTime() {
    const order = [NAMED_TIMES.golden, NAMED_TIMES.dusk, NAMED_TIMES.night, NAMED_TIMES.dawn, NAMED_TIMES.day];
    const next = order.find((t) => t > clock.t + 0.01) ?? order[0];
    clock.set(next < clock.t ? next : next);
  }
  function togglePause() { clock.paused = !clock.paused; if ($('btnPause')) $('btnPause').classList.toggle('on', clock.paused); }
  if ($('btnTime')) $('btnTime').onclick = stepTime;
  if ($('btnPause')) $('btnPause').onclick = togglePause;
  if ($('btnPad')) $('btnPad').onclick = togglePad;
  if ($('btnHand')) $('btnHand').onclick = toggleHand;
  if (Q.has('pad') && !pad.on && !opts.padHandled) togglePad();
  if ($('btnPad')) $('btnPad').classList.toggle('on', pad.on);
  if (Q.get('hud') === '0' && $('hud')) $('hud').style.display = 'none';

  // ---------------------------------------------------------------- controller (Gamepad API, standard mapping)
  function cancel() { if ($('say')) $('say').hidden = true; sayTimer = 0; walkTo = null; }
  function padButton(name) {
    API.padPresses = (API.padPresses || 0) + 1; API.lastPad = name;   // QA: presses seen by the engine
    if (hooks.onPad && hooks.onPad(name, ctx)) return;
    switch (name) {
      case 'a': interact(); break;
      case 'b': cancel(); break;
      case 'x': if (!blocked()) playerCast(true); break;
      case 'y': case 'rb': if (!blocked()) cycleSpell(1); break;
      case 'lb': if (!blocked()) cycleSpell(-1); break;
      case 'rs': actorAct('attack'); break;
      case 'ls': actorAct('jump'); break;
      case 'lt': actorAct('defend', player, { hold: false, dur: 0.8 }); break;
      case 'start': if (!opts.noTimeKeys) togglePause(); break;
      case 'select': togglePad(); document.body.classList.toggle('padpin', pad.on); break;
      default: break;
    }
  }
  const gamepads = new GamepadInput({
    onButton: (name) => padButton(name),
    onConnect: (on, gp) => { toast(on ? '🎮 controller connected' : 'controller disconnected', 2.4); if (!on) setCtrl(false); },
    signal: ac.signal,
  });
  let gp = { x: 0, y: 0, mag: 0, zoom: 0, used: false };
  if ($('btnPause')) $('btnPause').classList.toggle('on', clock.paused);

  // ---------------------------------------------------------------- sizing
  let bufW = 1, bufH = 1;
  function resize() {
    renderer.setSize(innerWidth, innerHeight, false);
    canvas.style.width = innerWidth + 'px'; canvas.style.height = innerHeight + 'px';
    bufW = renderer.domElement.width; bufH = renderer.domElement.height;
    camera.aspect = bufW / bufH; camera.updateProjectionMatrix();
    post.setSize(bufW, bufH);
  }
  addEventListener('resize', resize, sig);
  resize();

  // ---------------------------------------------------------------- simulation
  const sunDir = new THREE.Vector3();
  const tmpV = new THREE.Vector3();
  const shadeRay = new THREE.Raycaster();
  let shadeClock = 0;
  if (Q.get('t')) clock.set(NAMED_TIMES[Q.get('t')] ?? Number(Q.get('t')));
  target.set(player.x, player.y, player.z).add(look);
  if (bounds) clampTarget();
  function clampTarget() { target.x = THREE.MathUtils.clamp(target.x, bounds[0], bounds[2]); target.z = THREE.MathUtils.clamp(target.z, bounds[1], bounds[3]); }

  function moveActor(a, dx, dz, dt) {
    const len = Math.hypot(dx, dz);
    if (len < 1e-5) return false;
    const sp = a.speed * (a.running ? 1.6 : 1) * (a.speedScale ?? 1) * dt;
    const mx = dx / len * sp, mz = dz / len * sp;
    actors.setFacingFromVec(a, dx, dz);
    if (!collide) { a.x += mx; a.z += mz; return true; }
    const [nx, nz, nh, ok] = collide.move(a.x, a.z, a.y, mx, mz, a.r);
    const movedAny = Math.hypot(nx - a.x, nz - a.z) > sp * 0.2;
    a.x = nx; a.z = nz; a.y = nh;
    return movedAny ? true : false;
  }

  function updatePlayer(dt) {
    let dx = 0, dz = 0;
    if (keys.has('w') || keys.has('arrowup')) dz -= 1;
    if (keys.has('s') || keys.has('arrowdown')) dz += 1;
    if (keys.has('a') || keys.has('arrowleft')) dx -= 1;
    if (keys.has('d') || keys.has('arrowright')) dx += 1;
    player.running = keys.has('shift');
    player.speedScale = 1;
    // analog walk: walk speed ramps with the tilt, the outer rim runs (touch stick and controller alike)
    const analog = (mag, run) => { player.running = run; player.speedScale = run ? 1 : Math.max(0.35, Math.min(1, mag / 0.8)); };
    if (gp.mag > 0) { dx = gp.x; dz = gp.y; analog(gp.mag, gp.mag > 0.92); }
    const st = pad.stick();
    if (st.active) { dx = st.x; dz = st.y; analog(st.mag || 0, st.run); }
    if (blocked()) { dx = 0; dz = 0; walkTo = null; }
    // planted actions: no walking during attack / guard / cast-by-act; a jump keeps its momentum
    if (player.act && player.act.name !== 'jump') { dx = 0; dz = 0; walkTo = null; }
    if (dx || dz) walkTo = null;
    let moving = false;
    if (walkTo) {
      const [wx, wz] = walkTo.pts[walkTo.i];
      const ex = wx - player.x, ez = wz - player.z;
      const d = Math.hypot(ex, ez);
      const last = walkTo.i === walkTo.pts.length - 1;
      if (d < (last ? 0.12 : 0.22)) {
        if (!last) walkTo.i++;
        else { const w = walkTo; walkTo = null; if (w.talk) talk(w.talk); if (w.arrive) w.arrive(ctx); }
      } else {
        moving = moveActor(player, ex, ez, dt);
        if (!moving) { walkTo.stuck = (walkTo.stuck || 0) + dt; if (walkTo.stuck > 0.5) walkTo = null; } else walkTo.stuck = 0;
      }
    } else if (dx || dz) moving = moveActor(player, dx, dz, dt);
    if (player.castT > 0) moving = false;
    actors.animate(player, dt, moving);
    if (player.act && player.act.justLanded) {   // landing: one dust kick per foot, on the ground
      player.act.justLanded = false;
      if (particles) { particles.burst('footstep_dust', player.x - 0.18, player.y + 0.05, player.z + 0.05); particles.burst('footstep_dust', player.x + 0.18, player.y + 0.05, player.z + 0.05); }
    }
    // footstep dust: a small kick on each planted foot (walk frames 0 and 2)
    if (particles && player.anim === 'walk' && player.frame !== player._lastStep && (player.frame === 0 || player.frame === 2)) {
      particles.burst('footstep_dust', player.x, player.y + 0.05, player.z + 0.05);
    }
    player._lastStep = player.anim === 'walk' ? player.frame : -1;
  }

  function updateNpc(a, dt) {
    let moving = false;
    if (a.behavior === 'wander' || a.behavior === 'stroll') {
      if (a.target) {
        const ex = a.target[0] - a.x, ez = a.target[1] - a.z;
        if (Math.hypot(ex, ez) < 0.15) { a.target = null; a.wait = 1.5 + rnd() * 3; }
        else { moving = moveActor(a, ex, ez, dt); if (!moving) { a.target = null; a.wait = 0.8; } }
      } else {
        a.wait -= dt;
        if (a.wait <= 0) {
          const ang = rnd() * Math.PI * 2, r = a.radius * (0.3 + rnd() * 0.7);
          a.target = [a.home[0] + Math.cos(ang) * r, a.home[1] + Math.sin(ang) * r];
        }
      }
    } else if (a.behavior === 'follow') {
      // a pet or friend tagging along: keep ~1.3 m behind the player, hop over when left far behind
      const ex = player.x - a.x, ez = player.z - a.z, d = Math.hypot(ex, ez);
      if (d > 7) { a.x = player.x - 0.8; a.z = player.z + 0.4; a.y = player.y; }
      else if (d > 1.3) moving = moveActor(a, ex, ez, dt * (d > 3 ? 1.5 : 1));
    } else if (a.behavior === 'caster' && a.spell) {
      a.castClock -= dt;
      if (a.castClock <= 0) { a.castClock = a.every; a.facing = a.castFacing || 'down'; castSpell(a, a.spell); }
    } else if (a.idleTurn) {
      a.wait -= dt;
      if (a.wait <= 0) { a.wait = 3 + rnd() * 4; const f = ['down', 'left', 'right', 'down']; a.facing = f[Math.floor(rnd() * f.length)]; }
    }
    actors.animate(a, dt, moving);
  }

  function updateShade() {
    // cheap: one ray per actor toward the sun against buildings/trees (sprites dim in a cottage's shadow)
    for (const a of actors.list) {
      shadeRay.set(tmpV.set(a.x, a.y + 1.0, a.z), sunDir);
      shadeRay.far = 40;
      a.shadeTarget = shadeRay.intersectObjects(occluders, true).length ? 1 : 0;
    }
  }

  // ---------------------------------------------------------------- grade -> world
  function applyGrade(g, time) {
    const el = THREE.MathUtils.degToRad(g.sun_elevation), az = THREE.MathUtils.degToRad(g.sun_azimuth);
    sunDir.set(Math.sin(az) * Math.cos(el), Math.sin(el), Math.cos(az) * Math.cos(el)).normalize();
    sun.color.copy(g.sun_color); sun.intensity = g.sun_intensity;
    sun.position.copy(target).addScaledVector(sunDir, 50);
    sun.target.position.copy(target); sun.target.updateMatrixWorld();
    hemi.color.copy(g.hemi_sky); hemi.groundColor.copy(g.hemi_ground); hemi.intensity = g.hemi_intensity;
    for (const m of slots.windows) {
      m.emissive.copy(g.window_emissive).multiplyScalar(g.window_intensity);
      m.color.setRGB(0.22, 0.26, 0.34).lerp(g.sky_top, 0.25);
    }
    const lampOn = g.lamp_intensity;
    for (const L of lamps) {
      const fl = particles ? particles.flickerFrame(time, L.phase) : { intensity: 1 };
      L.power = lampOn * fl.intensity;
      L.frame = fl.frame;
      if (L.light) { L.light.intensity = (L.fixed != null ? Math.max(L.fixed, L.power) : L.power) * (L.kind === 'lamp_post' ? 26 : 12); L.light.color.copy(L.tint || g.lamp_color); }
    }
    for (const m of slots.lamps) m.emissive.copy(g.lamp_color).multiplyScalar(0.25 + lampOn * 1.6);
    post.setGrade(g);
  }

  // ---------------------------------------------------------------- particles showcase (?showcase=particles)
  const showLabels = [];
  function setupShowcase() {
    for (const a of actors.list) { a.quad.visible = false; a.caster.visible = false; }
    // three rows, tall risers at the back so their plumes don't cover the rows in front
    const rows = [['chimney_wisp', 'oven_steam', 'embers', 'fountain_spray', 'lamp_bugs'],
                  ['fireflies', 'petals', 'pollen', 'butterflies', 'leaf_bits'],
                  ['dust_motes', 'snowfall', 'rain', 'rain_splash', 'footstep_dust']];
    const known = new Set(rows.flat());
    const extra = Object.keys(pMeta.presets).filter((n) => n !== 'lamp_flicker' && !known.has(n));
    if (extra.length) rows.push(extra);
    const cells = [];
    rows.forEach((r, ri) => r.forEach((n, ci) => { if (pMeta.presets[n]) cells.push([n, ci - (r.length - 1) / 2, ri]); }));
    cells.forEach(([n, cx, ri]) => {
      const p = pMeta.presets[n];
      const x = player.x + cx * 3.4;
      const z = player.z - 0.5 - (2 - ri) * 2.8;
      const y = collide ? (collide.height(x, z) ?? 0) : 0;
      const e = { preset: n, pos: [x, y + (p.weather ? 1.8 : n === 'fountain_spray' ? 0.2 : n.includes('steam') || n.includes('ember') || n.includes('wisp') ? 0.3 : 0.9), z],
                  area: p.weather ? [1.8, 0.3, 1.0] : n === 'rain_splash' || n === 'footstep_dust' ? [0.4, 0, 0.3] : [1.6, 0.7, 0.9],
                  follow: false, every: p.manual ? 0.3 : 0, floor: p.weather ? y + 0.02 : (n === 'fountain_spray' ? y + 0.1 : undefined),
                  rate_scale: p.weather ? (n === 'rain' ? 0.3 : 0.15) : (p.rate < 1 ? 6 : 1) };
      particles.addEmitter(e);
      const el = document.createElement('div');
      el.className = 'fxlabel'; el.textContent = n.replace(/_/g, ' ');
      el.style.cssText = 'position:fixed;font:600 12px/1 system-ui;color:#3a2a1e;background:#f3e6c6;border:1px solid #6a4a30;padding:2px 5px;border-radius:3px;transform:translate(-50%,0);pointer-events:none;z-index:5';
      document.body.appendChild(el);
      showLabels.push({ el, pos: new THREE.Vector3(x, y, z + 0.7) });
    });
  }
  function updateShowcase() {
    for (const L of showLabels) {
      const p = tmpV.copy(L.pos).project(camera);
      L.el.style.left = ((p.x * 0.5 + 0.5) * innerWidth) + 'px';
      L.el.style.top = ((-p.y * 0.5 + 0.5) * innerHeight + 4) + 'px';
    }
  }
  if (showcase === 'particles' && particles) {
    setupShowcase();
    for (const a of npcs) if (a.behavior === 'caster') a.behavior = 'idle';   // keep the showcase about particles
  }
  // pre-warm emitters (~6 s of simulation) so fireflies, steam and weather are already in the air on frame one
  if (particles) {
    const g0 = clock.grade(), gate = showcase === 'particles' ? { motes: 1, bugs: 1 } : { motes: g0.motes, bugs: g0.bugs };
    for (let i = 0; i < 60; i++) particles.update(0.1, gate, []);
  }

  // ---------------------------------------------------------------- loop
  let last = performance.now(), time = 0;
  const fixedDt = Q.has('shot') ? 1 / 30 : null;
  const simScale = Math.max(1, Math.min(12, Number(Q.get('simscale')) || 1));   // QA: extra sim sub-steps per frame
  function simulate(dt) {
    time += dt;
    clock.tick(dt);
    updatePlayer(dt);
    for (const a of npcs) updateNpc(a, dt);
    if (effects) effects.update(dt);
    if (gamefx) gamefx.update(dt);
    if (hooks.onFrame) hooks.onFrame(dt, ctx);
  }
  function frame() {
    if (!alive) return;
    const now = performance.now();
    let dt = Math.min(0.05, (now - last) / 1000); last = now;
    if (fixedDt) dt = fixedDt;
    if (API.held) dt = 0; // QA: freeze simulation, keep rendering
    gp = gamepads.poll(!GATE.loading);
    API.padPolls = (API.padPolls || 0) + 1;
    if (gp.used && !GATE.loading) setCtrl(true);
    if (gp.zoom) zoomBy(1 - gp.zoom * Math.min(0.05, (now - (frame.lastNow || now)) / 1000) * 0.6);
    frame.lastNow = now;
    for (let s = 0; s < simScale; s++) simulate(dt);
    if (particles && simScale > 1) for (let s = 1; s < simScale; s++) particles.update(dt, { motes: 0, bugs: 0 }, []);
    // camera follows (translation only; orientation is locked)
    tmpV.set(player.x, player.y, player.z).add(look);
    target.lerp(tmpV, 1 - Math.exp(-dt * 4));
    if (bounds) clampTarget();
    placeCamera();
    const g = clock.grade();
    applyGrade(g, time);
    shadeClock -= dt;
    if (shadeClock <= 0) { updateShade(); shadeClock = 0.25; }
    for (const a of actors.list) a.shade += (a.shadeTarget * Math.min(1, g.sun_intensity / 2) - a.shade) * Math.min(1, dt * 5);
    swayTrees(trees, time);
    const k = Number(Q.get('k')) || actors.pixelScale(camera, target, bufH);
    actors.sync(camera, bufW, bufH, k, g, lamps, sunDir);
    if (particles) {
      const statics = lamps.filter((L) => L.glow && L.power > 0.15).map((L) => ({ x: L.pos.x, y: L.pos.y, z: L.pos.z + 0.02, frame: L.frame, row: pMeta.presets.lamp_flicker.row }));
      particles.followPos.x = target.x; particles.followPos.z = target.z + 2;
      if (showcase === 'particles') updateShowcase(dt);
      particles.update(dt, showcase === 'particles' ? { motes: 1, bugs: 1 } : { motes: g.motes, bugs: g.bugs }, statics);
      particles.sync(k, bufW, bufH, g.sprite_tint.clone().convertLinearToSRGB());
    }
    if (effects) effects.sync(camera, bufW, bufH, k, g.sprite_tint.clone().convertLinearToSRGB());
    if (gamefx) gamefx.sync(camera, bufW, bufH, k, g.sprite_tint.clone().convertLinearToSRGB());
    // focus band follows the player's screen row (the walk band)
    const pf = tmpV.set(player.x, player.y + 0.8, player.z).project(camera);
    post.mat.uniforms.uFocusY.value = THREE.MathUtils.clamp(pf.y * 0.5 + 0.5, 0.3, 0.7);
    post.render(world, camera);          // world: lit, shadowed, tilt-shift + haze + grade
    renderer.render(sharp, camera);      // sprites + particles: sharp, depth-tested against the world
    if (sayTimer > 0) { sayTimer -= dt; if (sayTimer <= 0 && $('say')) $('say').hidden = true; }
    if ($('clocktxt')) $('clocktxt').textContent = clock.label();
    if ($('dial')) $('dial').style.background = '#' + g.sky_top.clone().lerp(g.sun_color, 0.5).getHexString();
    pad.update(!!nearestNpc() || !!(hooks.nearThing && hooks.nearThing(ctx)));
    API.frames++;
    requestAnimationFrame(frame);
  }

  // ---------------------------------------------------------------- game context (hooks get this)
  const project = (x, y, z) => { const p = tmpV.set(x, y, z).project(camera); return { x: (p.x * 0.5 + 0.5) * innerWidth, y: (-p.y * 0.5 + 0.5) * innerHeight, z: p.z }; };
  const ctx = {
    scene, clock, camera, actors, player, npcs, collide, nav, effects, gamefx, fx: fxPlaced, particles, keys, project,
    walkTo: (x, z, extra) => walkPath(x, z, extra), stopWalk: () => { walkTo = null; }, walking: () => !!walkTo,
    castSpell, setSpellCycle: (c) => { spellCycle = (c || []).filter((n) => sMeta && (sMeta.cast_sets[n] || sMeta.effects[n])); spellIdx = Math.min(spellIdx, Math.max(0, spellCycle.length - 1)); if ($('btnSpell')) $('btnSpell').hidden = !spellCycle.length; showSpell(); },
    spellCycle: () => spellCycle.slice(),
    addNpc: (spec) => { const a = actors.add(spec); npcs.push(a); return a; },
    removeNpc: (a) => { const i = npcs.indexOf(a); if (i >= 0) npcs.splice(i, 1); actors.remove(a); },
    npc: (id) => npcs.find((a) => a.id === id) || null,
    burst: (name, x, y, z, n) => particles && particles.burst(name, x, y, z, n),
    heightAt: (x, z) => (collide ? (collide.height(x, z) ?? 0) : 0),
    zoom: () => dist,
  };

  // ---------------------------------------------------------------- debug / QA API
  Object.assign(API, {
    scene, clock, camera, actors, player, ctx, nav,
    setTime: (t) => clock.set(NAMED_TIMES[t] ?? t),
    pause: (p = true) => { clock.paused = p; },
    camState: () => ({ quat: camera.quaternion.toArray().map((v) => +v.toFixed(6)), fov: camera.fov,
      offset: camera.position.clone().sub(target).normalize().toArray().map((v) => +v.toFixed(5)), dist,
      pitch: C.pitch, pos: camera.position.toArray() }),
    actorRects: () => actors.list.map((a) => ({ id: a.id, role: a.role, facing: a.facing, anim: a.anim, frame: a.frame, ...a.rect, buf: [bufW, bufH], dpr })),
    stats: () => {
      const box = new THREE.Box3();
      world.traverse((o) => { if (o.isMesh && o.geometry && !o.userData.noBounds && o.material.colorWrite !== false) { o.geometry.computeBoundingBox(); const b = o.geometry.boundingBox.clone().applyMatrix4(o.matrixWorld); if (b.max.y < 30) box.union(b); } });
      return { heightRange: collide ? collide.range : null, worldMinY: box.min.y, worldMaxY: box.max.y,
        calls: renderer.info.render.calls, tris: renderer.info.render.triangles, lamps: lamps.length, k: actors.k,
        particles: particles ? particles.count : 0, phase: clock.grade()._names, t: clock.t };
    },
    walk: (x, z) => walkPath(x, z), walking: () => !!walkTo, path: (x, z) => (nav ? nav.path(player.x, player.z, x, z) : null),
    tap: (cx, cy) => tapAt(cx, cy), pad, setHand, toggleHand, gamefxRects: () => (gamefx ? gamefx.rects().map((r) => ({ ...r, buf: [bufW, bufH] })) : []),
    effects, castSpell: (id, name) => castSpell(actors.list.find((a) => a.id === id) || player, name), playerCast, cycleSpell,
    spellName: () => spellCycle[spellIdx],
    // action states: act('jump' | 'attack' | 'defend' | 'cast', id?, {hold, dur}); release('defend', id?)
    act: (name, id, opts) => actorAct(name, (id && actors.list.find((a) => a.id === id)) || player, opts || {}),
    release: (name, id) => actors.release((id && actors.list.find((a) => a.id === id)) || player, name),
    // QA: advance an actor's running action by `sec` of game time in fixed 1/60 s steps (use with hold(true))
    actAdvance: (sec, id) => {
      const a = (id && actors.list.find((b) => b.id === id)) || player;
      for (let t = 0; t < sec - 1e-9 && a.act; t += 1 / 60) actors.animate(a, 1 / 60, false);
      return a.act ? a.act.t : null;
    },
    actorState: (id) => {
      const a = (id && actors.list.find((b) => b.id === id)) || player;
      return { id: a.id, role: a.role, anims: a.anims, anim: a.anim, frame: a.frame, act: a.act ? a.act.name : null,
               t: a.act ? a.act.t : 0, lift: a.lift || 0, y: a.y, casterY: a.caster.position.y, rect: a.rect };
    },
    effectRects: () => (effects ? effects.rects().map((r) => ({ ...r, buf: [bufW, bufH] })) : []),
    showEffects: (v = true) => { if (effects) for (const f of effects.list) f.mesh.visible = v; },
    // QA: hide spell effects + particles so actor crops can be compared 1:1 with the atlas
    showOverlays: (v = true) => { API.showEffects(v); if (particles) particles.points.visible = v; },
    hideActors: (h = true) => { for (const a of actors.list) { a.quad.visible = !h; a.caster.visible = !h; } },
    // QA lineup: every effect frozen on a chosen frame in a grid on open ground in front of the camera
    effectLineup: (frameFrac = 0.5) => {
      if (!effects) return [];
      effects.clear();
      const names = effects.names();
      const cols = 5;
      names.forEach((n, i) => {
        const e = sMeta.effects[n];
        const x = target.x + ((i % cols) - (cols - 1) / 2) * 2.4;
        const z = target.z - look.z + 0.6 - Math.floor(i / cols) * 3.2;
        const y = collide ? (collide.height(x, z) ?? 0) : 0;
        effects.spawn(n, x, y, z, { frame: Math.min(e.frames - 1, Math.floor(e.frames * frameFrac)), onTop: true });
      });
      return names;
    },
    // QA lineup for game effects (portal vortex, ring, pickups, quest tags): same layout, own atlas
    gamefxLineup: (frameFrac = 0.5) => {
      if (!gamefx) return [];
      for (const f of gamefx.list) f.mesh.visible = false;
      API._gfxLine = (API._gfxLine || []).filter((f) => { gamefx.remove(f); return false; });
      const names = gamefx.names();
      names.forEach((n, i) => {
        const e = gMeta.effects[n];
        const x = target.x + (i - (names.length - 1) / 2) * 2.6;
        const z = target.z - look.z + 0.6;
        const y = collide ? (collide.height(x, z) ?? 0) : 0;
        API._gfxLine.push(gamefx.spawn(n, x, y, z, { frame: Math.min(e.frames - 1, Math.floor(e.frames * frameFrac)), onTop: true, duration: Infinity }));
      });
      return names;
    },
    gamefxLineupRects: () => (API._gfxLine || []).map((f) => ({ ...f.rect, buf: [bufW, bufH] })),
    clearGamefxLineup: () => { for (const f of API._gfxLine || []) gamefx.remove(f); API._gfxLine = []; if (gamefx) for (const f of gamefx.list) f.mesh.visible = true; },
    hold: (h = true) => { API.held = h; },
    // input QA: gate state, controller state, floating-stick state
    loading: () => GATE.loading, swallowed: () => GATE.swallowed, gamepad: () => ({ ...gp, ctrl: document.body.classList.contains('ctrl') }),
    stickState: () => ({ ...pad.st, base: pad.base, rest: !pad.base }), padButton,
  });

  API.ready = false; API.frames = 0;
  requestAnimationFrame(frame);
  // ready after a few frames have rendered: only then does the loading gate open and the #boot overlay go
  const waitFrames = () => (!alive ? null : API.frames > 6 ? ((API.ready = true), setGate(false)) : requestAnimationFrame(waitFrames));
  waitFrames();

  // ---------------------------------------------------------------- teardown (area change)
  function dispose() {
    alive = false; API.ready = false;
    ac.abort();
    pad.dispose();
    const seen = new Set();
    const free = (o) => {
      if (o.geometry && !seen.has(o.geometry)) { seen.add(o.geometry); o.geometry.dispose(); }
      for (const m of [].concat(o.material || [])) {
        if (seen.has(m)) continue; seen.add(m);
        for (const v of Object.values(m)) if (v && v.isTexture) v.dispose();
        if (m.uniforms) for (const u of Object.values(m.uniforms)) if (u.value && u.value.isTexture) u.value.dispose();
        m.dispose();
      }
    };
    world.traverse(free); sharp.traverse(free);
    post.dispose && post.dispose();
    renderer.dispose();
    renderer.forceContextLoss();
  }
  return { ctx, dispose, scene, get clockT() { return clock.t; }, player };
}

function startTime(scene) {
  const s = scene.time?.start ?? 'golden';
  return typeof s === 'number' ? s : (NAMED_TIMES[s] ?? 0.64);
}

if (!window.__hd2dErrHook) { window.__hd2dErrHook = true; window.addEventListener('error', (e) => API.errors.push(String(e.message))); }
if (!window.HD2D_MANUAL) boot().catch((e) => { console.error(e); API.errors.push(String(e && e.stack || e)); document.getElementById('boot').textContent = 'failed: ' + e; });
