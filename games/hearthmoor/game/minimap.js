// Corner map of the current area. 2D canvas, redrawn at most five times a second.
// Quest marks use markerFor (same tags as the overhead ! / star). Off-area goals
// point at the exit, portal or waystone that leads there, when one can be found.

import { markerFor } from './data.js';

const KEY = 'hearthmoor-minimap';
const SCALE = 4;          // canvas px per world metre, player-centred
const SHOP_IDS = { merchant: 1, nightmerchant: 1, banker: 1, chandler: 1, denkeeper: 1, smith: 1, runesmith: 1, alchemist: 1, mp_trader: 1, nf_trader: 1, as_trader: 1, jt_trader: 1, tansy: 1 };
const WAY_NET = { lane: 1, ravenhold: 1, bifrost: 1, temple: 1 };

const faceOf = (f) => ({ down: [0, 1], up: [0, -1], left: [-1, 0], right: [1, 0] }[f] || [0, 1]);

function onPref() {
  try { return localStorage.getItem(KEY) !== '0'; } catch (e) { return true; }
}
function isShop(n) {
  if (!n || n.ai) return false;
  if (SHOP_IDS[n.id]) return true;
  const role = n.role || '';
  return role === 'shopkeeper' || role === 'nightmerchant' || /trader|merchant|smith|alchemist|chandler/.test(role);
}
function center(r) {
  if (!r || r.length < 4) return null;
  return [(r[0] + r[2]) / 2, (r[1] + r[3]) / 2];
}

// A best-effort area id for the first active errand that is not in `here`. Missing data returns null.
function offArea(S, here) {
  const q = (S && S.quests) || {}, F = (S && S.flags) || {}, inv = (S && S.inv) || {};
  const list = [];
  if (q.bread === 1) list.push('lane');
  if (q.tea === 1) list.push('mossglen');
  if (q.tea === 2) list.push('lane');
  if (q.cat === 1) list.push('mossglen');
  if (q.cat === 2) list.push('plaza');
  if (q.harbor === 1) list.push('ravenhold');
  if (q.harbor === 2 && !F.rh_road) list.push('ravenhold');
  if (q.harbor === 2 && F.rh_road && !F.bf_done) list.push('bifrost');
  if (q.altar === 1 || q.altar === 2) list.push('temple');
  if (q.gate === 1 && !inv.alder_charm) list.push('plaza');
  else if (q.gate === 1 && !F.tm_wick) list.push('ravenhold');
  else if (q.gate === 1 || q.gate === 2) list.push('temple');
  if ((q.forge_riot > 0 && q.forge_riot < 3) || (q.temper > 0 && q.temper < 3) || (q.cauldron > 0 && q.cauldron < 3)) list.push('forge');
  if (q.strays === 1 || q.strays === 2) list.push('bifrost');
  if (q.vh_spring === 1 || q.vh_spring === 2) list.push('vh_village');
  return list.find((a) => a && a !== here) || null;
}
function aimAt(gm, target, here) {
  if (!gm || !target) return null;
  const spots = [];
  const take = (x, z) => { if (Number.isFinite(x) && Number.isFinite(z)) spots.push([x, z]); };
  for (const e of gm.exits || []) if (e && e.to === target) { const c = center(e.rect); if (c) take(c[0], c[1]); }
  for (const p of gm.portals || []) {
    if (!p) continue;
    const hit = p.to === target || (p.choose || []).some((ch) => ch && ch.to === target);
    if (hit) { const c = center(p.rect); if (c) take(c[0], c[1]); }
  }
  if (gm.ferry && gm.ferry.to === target && gm.ferry.pos) take(gm.ferry.pos[0], gm.ferry.pos[1]);
  if (!spots.length && WAY_NET[here] && WAY_NET[target] && gm.waystone && gm.waystone.pos) take(gm.waystone.pos[0], gm.waystone.pos[1]);
  return spots[0] || null;
}

function star(g, x, y, r) {
  g.beginPath();
  for (let i = 0; i < 10; i++) {
    const a = -Math.PI / 2 + i * Math.PI / 5;
    const rad = i % 2 ? r * 0.42 : r;
    const px = x + Math.cos(a) * rad, py = y + Math.sin(a) * rad;
    if (i) g.lineTo(px, py); else g.moveTo(px, py);
  }
  g.closePath();
  g.fillStyle = '#f2c24a';
  g.strokeStyle = '#2a1e1c';
  g.lineWidth = 1;
  g.fill();
  g.stroke();
}
function rimArrow(g, w, h, x, y) {
  const cx = w / 2, cy = h / 2;
  let dx = x - cx, dy = y - cy;
  const len = Math.hypot(dx, dy) || 1;
  dx /= len; dy /= len;
  const rad = Math.min(w, h) / 2 - 8;
  const ax = cx + dx * rad, ay = cy + dy * rad;
  const px = -dy, py = dx;
  g.beginPath();
  g.moveTo(ax + dx * 6, ay + dy * 6);
  g.lineTo(ax - dx * 4 + px * 4, ay - dy * 4 + py * 4);
  g.lineTo(ax - dx * 4 - px * 4, ay - dy * 4 - py * 4);
  g.closePath();
  g.fillStyle = '#f2c24a';
  g.strokeStyle = '#2a1e1c';
  g.lineWidth = 1;
  g.fill();
  g.stroke();
}

export function attachMinimap(G) {
  const cv = document.getElementById('minimap');
  const btn = document.getElementById('btnMinimap');
  if (!cv) return;
  let on = onPref();
  let last = 0;
  const g = cv.getContext('2d');

  function syncBtn() {
    if (!btn) return;
    btn.textContent = on ? 'minimap: on' : 'minimap: off';
    btn.classList.toggle('on', on);
  }
  function toggle() {
    on = !on;
    try { localStorage.setItem(KEY, on ? '1' : '0'); } catch (e) { /* private mode */ }
    syncBtn();
    last = 0;
  }
  if (btn) btn.onclick = () => toggle();
  syncBtn();

  function hide(v) { if (cv.hidden !== v) cv.hidden = v; }

  function draw() {
    const ctx = G.ctx, p = ctx && ctx.player;
    if (!ctx || !p || !Number.isFinite(p.x)) return;
    const w = cv.width, h = cv.height;
    const scene = ctx.scene || {}, gm = scene.game || {};
    g.clearRect(0, 0, w, h);
    const to = (x, z) => [w / 2 + (x - p.x) * SCALE, h / 2 + (z - p.z) * SCALE];
    const walk = scene.ground && scene.ground.walk;
    const cam = scene.camera && scene.camera.bounds;
    const bounds = walk || cam;
    if (bounds && bounds.length >= 4) {
      const a = to(bounds[0], bounds[1]), b = to(bounds[2], bounds[3]);
      g.strokeStyle = '#4a2e20';
      g.lineWidth = 1;
      g.strokeRect(Math.min(a[0], b[0]), Math.min(a[1], b[1]), Math.abs(b[0] - a[0]), Math.abs(b[1] - a[1]));
    }
    g.save();
    g.beginPath();
    g.rect(3, 3, w - 6, h - 6);
    g.clip();
    const dot = (x, z, col, r) => {
      const [mx, my] = to(x, z);
      if (mx < -8 || my < -8 || mx > w + 8 || my > h + 8) return;
      g.beginPath();
      g.arc(mx, my, r, 0, Math.PI * 2);
      g.fillStyle = col;
      g.fill();
    };
    for (const e of gm.exits || []) {
      const c = center(e && e.rect); if (!c) continue;
      const [mx, my] = to(c[0], c[1]);
      g.fillStyle = '#7a4e2e';
      g.fillRect(mx - 2, my - 2, 4, 4);
    }
    for (const po of gm.portals || []) {
      const c = center(po && po.rect); if (!c) continue;
      const [mx, my] = to(c[0], c[1]);
      g.fillStyle = '#7a2c22';
      g.fillRect(mx - 2.5, my - 2.5, 5, 5);
    }
    if (gm.waystone && gm.waystone.pos) {
      const [mx, my] = to(gm.waystone.pos[0], gm.waystone.pos[1]);
      g.beginPath();
      g.moveTo(mx, my - 4); g.lineTo(mx + 3, my); g.lineTo(mx, my + 4); g.lineTo(mx - 3, my);
      g.closePath();
      g.fillStyle = '#f2c24a';
      g.fill();
      g.strokeStyle = '#2a1e1c';
      g.stroke();
    }
    if (gm.ferry && gm.ferry.pos) dot(gm.ferry.pos[0], gm.ferry.pos[1], '#7a2c22', 3);
    for (const sg of gm.sealed || []) if (sg && sg.pos) dot(sg.pos[0], sg.pos[1], '#4a2e20', 2);
    const quests = [];
    for (const n of ctx.npcs || []) {
      if (!n || n.ai || !Number.isFinite(n.x) || !Number.isFinite(n.z)) continue;
      let mark = null;
      try { mark = G.S ? markerFor(n.id, G.S) : null; } catch (e) { mark = null; }
      if (mark) quests.push(n);
      else if (isShop(n)) dot(n.x, n.z, '#b07a44', 3);
      else dot(n.x, n.z, '#2a1e1c', 2);
    }
    const [fx, fz] = faceOf(p.facing);
    const cx = w / 2, cy = h / 2;
    const pxp = -fz, pzp = fx;
    g.beginPath();
    g.moveTo(cx + fx * 8, cy + fz * 8);
    g.lineTo(cx - fx * 3 + pxp * 3.2, cy - fz * 3 + pzp * 3.2);
    g.lineTo(cx - fx * 3 - pxp * 3.2, cy - fz * 3 - pzp * 3.2);
    g.closePath();
    g.fillStyle = '#f2c24a';
    g.fill();
    g.strokeStyle = '#2a1e1c';
    g.stroke();
    g.beginPath();
    g.arc(cx, cy, 2.6, 0, Math.PI * 2);
    g.fillStyle = '#fff6dc';
    g.fill();
    g.stroke();
    const margin = 10;
    let arrow = null;
    for (const n of quests) {
      const [mx, my] = to(n.x, n.z);
      if (mx >= margin && my >= margin && mx <= w - margin && my <= h - margin) star(g, mx, my, 5);
      else if (!arrow || Math.hypot(n.x - p.x, n.z - p.z) < Math.hypot(arrow[0] - p.x, arrow[1] - p.z)) arrow = [n.x, n.z];
    }
    g.restore();
    if (!quests.length) {
      try {
        const tgt = offArea(G.S, G.area);
        const spot = aimAt(gm, tgt, G.area);
        if (spot) arrow = spot;
      } catch (e) { /* no arrow */ }
    }
    if (arrow) {
      const [mx, my] = to(arrow[0], arrow[1]);
      const offscreen = mx < margin || my < margin || mx > w - margin || my > h - margin;
      // in another area the arrow sits on the rim even when the exit itself is in view
      if (offscreen || !quests.length) rimArrow(g, w, h, mx, my);
    }
  }

  function tick() {
    try {
      const hideIt = !on || G.title || G.pause || G.dlg || (G.intro && G.intro.active) || !G.ctx || !G.ctx.player;
      hide(!!hideIt);
      if (hideIt) return;
      const now = performance.now();
      if (now - last < 200) return;
      last = now;
      draw();
    } catch (e) { /* the map never breaks the frame */ }
  }

  G.minimapTick = tick;
  G.minimapToggle = toggle;
}
