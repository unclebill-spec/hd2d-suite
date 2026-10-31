// game/minigames/bloomtide.js: the Bloomtide harvest + dance minigames (Vanaheim Stage C, Systems).
// Entry: startBloomGame(G, 'harvest' | 'dance') -> Promise<{ won, score }>. The only save write: on a win,
// G.S.flags.vh_bloom_games[kind] = true (then G.save()). Quitting (Esc / pad B / the x button) resolves
// { won: false, score } and writes nothing. Story's Liss runtime does the turn-in; gating is the caller's.
// Dialogue hook: an option { act: 'bloom_game', kind, label } run through bloomAction(G, opt), or bloomOption(kind, label)
// which already carries a live-shape pick(G). Input: one tap on Space / E / Enter, pad A, touch or click.
// Rules + numbers live in bloom_rules.js; juice in bloom_fun.js via HOOKS (no rule changes there).
import { GAMES, chart, tapAt, expire, score as scoreOf } from './bloom_rules.js';
import('./bloom_fun.js').catch((e) => console.warn('bloom fun', e));   // juice layer (fun pass)

// cozy-village biome + the approved NEON / ORB_NEON effect set (tests/check_palette.py), Game Director 2026-10-31.
// Key names kept from the first pass; only the values moved. Browns of the biome are not used (ink is the shared outline).
export const PAL = { ink: '#2a1e1c', indigo: '#3e5a8c', slate: '#2a6cb0', slate_hi: '#6c8cd4', slate_lo: '#1c62d8', moss: '#72a046', moss_hi: '#b2c464', moss_lo: '#4a7234',
  rim: '#6a34b8', mist: '#94c0dc', pale: '#d8f4ff', white: '#fff8e6', cyan: '#2ab4ff', cyan_hi: '#a6ecff', vio: '#a45cf0', vio_hi: '#d4a8ff',
  frost: '#5ab4f0', frost_hi: '#d8f4ff', mag: '#ff4fc8', mag_hi: '#ffb4ea', lime: '#5aec3c' };   // = art/minigames/bloomtide.json
export const W = 192, H = 144;   // logical pixels, drawn at an integer scale
export const HOOKS = [];         // juice layers: { start(st), judge(st, r), draw(g, st), result(st, res), stop(st) }
const call = (st, k, ...a) => { for (const h of HOOKS) try { h[k] && h[k](st, ...a); } catch (e) { console.warn('bloom hook', e); } };

export function reducedMotion(G) {
  try { if (localStorage.getItem('hearthmoor-reduced-motion') === '1') return true; } catch (_) {}
  try { if (matchMedia('(prefers-reduced-motion: reduce)').matches) return true; } catch (_) {}
  return !!(G && G.shakeOK && !G.shakeOK());
}
const CSS = `
#bloomgame{position:fixed;inset:0;z-index:60;display:flex;align-items:center;justify-content:center;background:rgba(42,30,28,.72);touch-action:none;user-select:none;-webkit-user-select:none;font-family:"Pixelify Sans",monospace;color:${PAL.pale}}
#bloomgame .bpanel{position:relative;width:min(94vw,640px);border:16px solid transparent;border-image:var(--f-night,none) 16 fill stretch;background:${PAL.ink};image-rendering:pixelated;padding:4px}
#bloomgame h2{margin:2px 0 4px;font:400 clamp(20px,4.6vw,30px) "Jacquarda Bastarda 9",serif;color:${PAL.cyan_hi};text-align:center;letter-spacing:1px}
#bloomgame canvas{display:block;width:100%;image-rendering:pixelated;background:${PAL.indigo}}
#bloomgame .bhud{display:flex;justify-content:space-between;font-size:clamp(13px,3.4vw,17px);margin:4px 2px 0;color:${PAL.mist}}
#bloomgame .bhint{text-align:center;font-size:clamp(12px,3.2vw,15px);color:${PAL.mist};margin-top:4px}
#bloomgame .bquit{position:absolute;top:-12px;right:-12px;width:34px;height:34px;border:2px solid ${PAL.rim};background:${PAL.slate};color:${PAL.pale};font:700 18px "Pixelify Sans",monospace;cursor:pointer}
#bloomgame .bres{position:absolute;inset:0;display:none;flex-direction:column;align-items:center;justify-content:center;gap:6px;background:rgba(42,30,28,.86);text-align:center;padding:10px}
#bloomgame .bres.on{display:flex}
#bloomgame .bres b{font:400 clamp(26px,6vw,40px) "Jacquarda Bastarda 9",serif;color:${PAL.cyan_hi}}
#bloomgame .bres .lose{color:${PAL.vio_hi}}
#bloomgame .bres p{margin:0;font-size:clamp(14px,3.6vw,18px)}
#bloomgame .bres button{margin-top:6px;padding:6px 18px;border:2px solid ${PAL.moss_hi};background:${PAL.moss_lo};color:${PAL.white};font:600 16px "Pixelify Sans",monospace;cursor:pointer}
`;
function el(tag, cls, html) { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }

// World freeze (Game Director call 3): enemies already hold while G.busy (combat.paused() reads busy); the day clock does
// not, so pause ctx.clock here and put back exactly what was there on close (win, lose or quit). No combat/area edits.
export function freezeWorld(G) {
  const busy0 = G.busy, clk = G.ctx && G.ctx.clock, clk0 = clk ? clk.paused : null;
  G.busy = true; if (clk) clk.paused = true;
  return () => { G.busy = busy0; if (clk) clk.paused = clk0; };
}

// Hearthmoor Art sprites (art/minigames/bloomtide/, 16x16 caps + fx, 24x24 basket; cells = col*w, row*h, pivot bottom-centre)
const ART_DIR = new URL('../../art/minigames/bloomtide/', import.meta.url);
export const SHEETS = { caps: [16, 16], basket: [24, 24], glow_fx: [16, 16], sparkle_fx: [16, 16] };
export const CAP_ROWS = ['cap_blue', 'cap_violet', 'cap_frost'];
export const ANIM = { pop: [90], perfect: [80, 80, 80, 120], glow: [70, 70, 70, 140], sparkle: 120, catch: 100 };   // ms, from the sheet JSONs
const IMG = {};
export function loadArt() {
  if (typeof Image === 'undefined') return;
  for (const k of Object.keys(SHEETS)) if (!IMG[k]) { const im = new Image(); im.src = new URL(`bt_${k}.png`, ART_DIR).href; IMG[k] = im; }
}
export function cell(g, sheet, row, col, cx, by, s = 1) {   // draw one cell with its bottom-centre pivot at (cx, by)
  const im = IMG[sheet], [w, h] = SHEETS[sheet]; if (!im || !im.complete || !im.naturalWidth) return false;
  g.drawImage(im, col * w, row * h, w, h, Math.round(cx - (w * s) / 2), Math.round(by - h * s), w * s, h * s); return true;
}
export function frameAt(ms, el) { let a = 0; for (let i = 0; i < ms.length; i++) { a += ms[i]; if (el < a) return i; } return -1; }   // -1 = finished

let active = null;
export const isActive = () => !!active;

export function startBloomGame(G, kind, opts = {}) {
  if (!GAMES[kind]) return Promise.reject(new Error(`bloom: unknown game ${kind}`));
  if (active) return active.promise;
  loadArt();
  if (!document.getElementById('bloomcss')) { const s = el('style'); s.id = 'bloomcss'; s.textContent = CSS; document.head.appendChild(s); }
  const g = GAMES[kind], times = chart(kind);
  const st = { G, kind, g, times, judged: [], t: -1, t0: 0, done: false, rm: reducedMotion(G), pops: [], fx: {}, now: () => performance.now() };
  const root = el('div'); root.id = 'bloomgame'; root.dataset.kind = kind;
  const panel = el('div', 'bpanel');
  const quit = el('button', 'bquit', '&#x2715;'); quit.setAttribute('aria-label', 'Quit');
  const cv = el('canvas'); cv.width = W; cv.height = H;
  const hud = el('div', 'bhud'), hint = el('div', 'bhint', kind === 'harvest' ? 'Tap when the ring closes on the glow-cap' : 'Tap as each bloom lands on the spring');
  const res = el('div', 'bres');
  panel.append(quit, el('h2', '', g.title), cv, hud, hint, res); root.append(panel); document.body.appendChild(root);
  Object.assign(st, { root, cv, hud, hint, res, gx: cv.getContext('2d') }); st.gx.imageSmoothingEnabled = false;

  const thaw = freezeWorld(G); G.bloom = st;
  let resolve; const promise = new Promise((r) => { resolve = r; });
  const finish = (won, quitted) => {
    if (st.done) return; st.done = true;
    const r = scoreOf(kind, times.map((_, i) => st.judged[i] || 'miss'));
    st.result = { ...r, won: !quitted && r.won, quit: !!quitted };
    if (st.result.won) {
      const f = G.S.flags || (G.S.flags = {}); f.vh_bloom_games = f.vh_bloom_games || {}; f.vh_bloom_games[kind] = true;
      G.save && G.save();
    }
    if (quitted) return close();
    call(st, 'result', st.result); showResult();
  };
  const close = () => {
    cancelAnimationFrame(st.raf); removeEventListener('keydown', onKey, true); call(st, 'stop');
    root.remove(); thaw(); if (G.bloom === st) G.bloom = null; active = null;
    resolve({ won: !!st.result.won, score: st.result.quit ? 0 : st.result.score });
  };
  function showResult() {
    const r = st.result;
    res.innerHTML = `<b class="${r.won ? '' : 'lose'}">${r.won ? (kind === 'harvest' ? 'A fine basket!' : 'The springs sing!') : 'Not this time'}</b>
      <p>${kind === 'harvest' ? 'Caps picked' : 'Steps danced'}: ${r.hits} / ${r.of} (need ${r.need})</p><p>Perfect: ${r.perfect} · Score: ${r.score}</p>
      <p>${r.won ? 'Liss claps with her whole body.' : 'Liss says try again. Any time. Tonight.'}</p><button class="bok">OK</button>`;
    res.classList.add('on'); st.resultAt = st.now();
    res.querySelector('.bok').onclick = (e) => { e.stopPropagation(); close(); };
  }
  function tap() {
    if (st.done) { if (st.result && !st.result.quit && st.now() - st.resultAt > 350) close(); return; }
    if (st.t < 0) return;
    const r = tapAt(times, st.judged, st.t);
    if (!r) { call(st, 'judge', { i: -1, grade: 'stray' }); return; }
    st.judged[r.i] = r.grade; st.last = { ...r, at: st.t };
    call(st, 'judge', r);
  }
  function onKey(e) {
    const k = e.key.toLowerCase();
    e.stopImmediatePropagation();
    if (e.repeat) { e.preventDefault(); return; }
    if (k === ' ' || k === 'e' || k === 'enter') { e.preventDefault(); tap(); } else if (k === 'escape') { e.preventDefault(); st.done ? close() : finish(false, true); }
  }
  addEventListener('keydown', onKey, true);
  root.addEventListener('pointerdown', (e) => { e.preventDefault(); e.stopPropagation(); if (e.target === quit) return finish(false, true); if (e.target.closest && e.target.closest('.bok')) return; tap(); });
  let padA = true, padB = true;   // held at open (the A that picked the option) must be released first
  const pad = () => { try { const p = [...(navigator.getGamepads ? navigator.getGamepads() : [])].find((x) => x && x.connected); if (!p) return;
    const a = !!(p.buttons[0] && p.buttons[0].pressed), b = !!(p.buttons[1] && p.buttons[1].pressed);
    if (a && !padA) tap(); if (b && !padB) { st.done ? close() : finish(false, true); } padA = a; padB = b; } catch (_) {} };

  st.t0 = st.now() + (opts.delay ?? 600);
  const frame = () => {
    st.raf = requestAnimationFrame(frame); pad();
    const now = st.now(); st.t = now < st.t0 ? -1 : now - st.t0;
    if (!st.done && st.t >= 0) {
      for (const i of expire(times, st.judged, st.t)) call(st, 'judge', { i, grade: 'miss', off: null, late: true });
      if (st.judged.filter(Boolean).length === times.length && st.t > times[times.length - 1] + 400) finish(true, false);
    }
    draw(st);
  };
  call(st, 'start'); frame();
  active = { promise, st };
  return promise;
}

// ---------------------------------------------------------------- drawing (base look; bloom_fun.js layers juice on top)
function px(g, c, x, y, w = 1, h = 1) { g.fillStyle = c; g.fillRect(Math.round(x), Math.round(y), w, h); }
function disc(g, c, cx, cy, r) { g.fillStyle = c; for (let y = -r; y <= r; y++) { const w = Math.floor(Math.sqrt(r * r - y * y)); g.fillRect(Math.round(cx - w), Math.round(cy + y), w * 2 + 1, 1); } }
function ring(g, c, cx, cy, r) { g.fillStyle = c; const n = Math.max(12, Math.round(r * 6)); for (let i = 0; i < n; i++) { const a = (i / n) * Math.PI * 2; g.fillRect(Math.round(cx + Math.cos(a) * r), Math.round(cy + Math.sin(a) * r), 1, 1); } }
// cap sprite: idle, pop (on a good hit) or the perfect pulse + glow ring, from the time since the cue was judged
export function capSprite(g, cx, by, s, row, hit) {
  let col = 0;
  if (hit && hit.grade === 'perfect') { const f = frameAt(ANIM.perfect, hit.el); col = f < 0 ? 0 : 2 + f; }
  else if (hit && hit.grade === 'good') col = frameAt(ANIM.pop, hit.el) < 0 ? 0 : 1;
  cell(g, 'caps', row, col, cx, by, s);
  if (hit && hit.grade === 'perfect') { const f = frameAt(ANIM.glow, hit.el); if (f >= 0) cell(g, 'glow_fx', 0, f, cx, by, s); }
}
// PLACEHOLDER (Liss, on hold for Art's violet nymph_vh recolour): swap drawLiss() for bt_liss_dance row 0 cols 4-7
// (20x32, pivot 10,32, 180 ms/frame, retimed to the beat). Until then a plain violet stand-in from PAL.
export function drawLiss(g, cx, by, beat) {
  const sway = beat % 2 ? 1 : -1;
  g.fillStyle = PAL.rim; g.fillRect(cx - 4 + sway, by - 20, 8, 14); g.fillStyle = PAL.vio; g.fillRect(cx - 3 + sway, by - 26, 6, 6);
  g.fillStyle = PAL.vio_hi; g.fillRect(cx - 6 + sway * 2, by - 22 - (beat % 2) * 3, 2, 6); g.fillRect(cx + 4 + sway * 2, by - 22 - ((beat + 1) % 2) * 3, 2, 6);
  g.fillStyle = PAL.rim; g.fillRect(cx - 3, by - 6, 2, 6); g.fillRect(cx + 1, by - 6, 2, 6);
}
const GROUND = 112, CX = W / 2, CY = 82, LANE_X = W / 2, HIT_Y = 116;
export const GEOM = { GROUND, CX, CY, LANE_X, HIT_Y };
function backdrop(g, st) {
  px(g, PAL.indigo, 0, 0, W, H);
  for (let i = 0; i < 26; i++) px(g, i % 3 ? PAL.slate_hi : PAL.pale, (i * 53) % W, (i * 29) % 70, 1, 1);   // stars
  if (st.kind === 'harvest') {
    px(g, PAL.moss_lo, 0, GROUND, W, H - GROUND); px(g, PAL.moss, 0, GROUND, W, 2);
    for (let x = 4; x < W; x += 11) px(g, PAL.moss_hi, x, GROUND - 2, 1, 2);
  } else {
    for (let i = 0; i < 4; i++) px(g, i % 2 ? PAL.slate : PAL.slate_lo, LANE_X - 26 + i * 2, 18 + i * 22, 52 - i * 4, 3);   // the Fizzing Steps
    px(g, PAL.slate, LANE_X - 1, 10, 2, HIT_Y - 10);
    for (let y = HIT_Y - 6; y <= HIT_Y + 6; y++) { const w = Math.round(30 * Math.sqrt(1 - ((y - HIT_Y) / 7) ** 2)); px(g, y < HIT_Y ? PAL.rim : PAL.vio, LANE_X - w, y, w * 2, 1); }   // the violet spring
  }
}
function draw(st) {
  const g = st.gx, t = st.t, { times, judged } = st;
  backdrop(g, st);
  if (st.kind === 'harvest') {
    const lead = st.g.lead;
    let cur = times.findIndex((_, i) => !judged[i]);
    if (cur < 0) cur = times.length - 1;
    for (let i = 0; i < times.length; i++) {   // the row of caps still to ripen, small, on the right
      if (judged[i] || i === cur) continue; const k = i - cur; if (k < 1 || k > 3) continue;
      capSprite(g, CX + 30 + k * 18, GROUND, 1, i % 3, null);
    }
    const tt = times[cur], L = st.last, lh = L && t - L.at < 400 ? { grade: L.grade, el: t - L.at } : null;
    if (lh && judged[L.i]) capSprite(g, CX, CY + 30, 2, L.i % 3, lh);   // the cap just picked: pop / perfect pulse + glow
    else if (!judged[cur] && t >= 0) {
      capSprite(g, CX, CY + 30, 2, cur % 3, null);
      const k = Math.max(0, Math.min(1, (tt - t) / lead));
      if (t > tt - lead) { ring(g, PAL.vio_hi, CX, CY + 16, 14); ring(g, PAL.cyan, CX, CY + 16, 14 + k * 40); }
    }
    st.fx.target = [CX, CY + 16];
  } else {
    const lead = st.g.lead;
    for (let i = 0; i < times.length; i++) {
      if (judged[i]) continue; const k = (times[i] - t) / lead; if (k > 1 || k < -0.3) continue;
      cell(g, 'sparkle_fx', 0, Math.floor(Math.max(0, t) / ANIM.sparkle) % 4, LANE_X, HIT_Y + 8 - k * (HIT_Y - 12), 1);   // falling bloom note
    }
    ring(g, PAL.cyan_hi, LANE_X, HIT_Y, 8);
    st.fx.target = [LANE_X, HIT_Y];
    { const L = st.last; if (L && L.grade === 'perfect' && t - L.at < 350) { const f = frameAt(ANIM.glow, t - L.at); if (f >= 0) cell(g, 'glow_fx', 0, f, LANE_X, HIT_Y + 8, 2); } }
    drawLiss(g, LANE_X + 52, HIT_Y + 4, Math.max(0, Math.floor(t / (60000 / st.g.bpm))));
    if (t < 0 || t < times[0] - 1000) { /* count-in drawn by the fun layer; base shows nothing */ }
  }
  for (const h of HOOKS) try { h.draw && h.draw(g, st); } catch (e) { /* juice never breaks play */ }
  const hits = judged.filter((x) => x === 'perfect' || x === 'good').length, done = judged.filter(Boolean).length;
  const txt = `${st.kind === 'harvest' ? 'Caps' : 'Steps'} ${hits}/${st.g.cues} · need ${st.g.need}`, sc = `Score ${scoreOf(st.kind, judged.filter(Boolean)).score}`;
  if (st.hudTxt !== txt + sc + done) { st.hudTxt = txt + sc + done; st.hud.innerHTML = `<span>${txt}</span><span>${sc}</span>`; }
}

// ---------------------------------------------------------------- dialogue entry (contract: { act: 'bloom_game', kind })
export function bloomAction(G, o) {
  if (!o || o.act !== 'bloom_game') return null;
  return startBloomGame(G, o.kind).then((r) => { if (G.toast) G.toast(r.won ? `Bloomtide: ${GAMES[o.kind].title} won!` : 'Bloomtide: try again any time tonight.', 2.2); G.refreshMarkers && G.refreshMarkers(); return r; });
}
export function bloomOption(kind, label = `Play the ${GAMES[kind].title}`) {
  const o = { act: 'bloom_game', kind, label };
  o.pick = (G) => { bloomAction(G, o); return null; };   // live choice shape: pick returns the next entry (null closes the dialogue)
  return o;
}
export const BLOOM_ACTIONS = { bloom_game: bloomAction };
