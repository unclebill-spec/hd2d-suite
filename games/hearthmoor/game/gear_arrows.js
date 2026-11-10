// Gear compare arrows: neon up / red down / blue equal over world drops, bag rows, and the gear tooltip.
// Colours are the check_palette ramps only: ORB_NEON green #3cf08a / #b8ffd4 / #14a85a, NEON red #ff5a4a / #e0302a / #a81c22,
// NEON blue (portal / temple) #2ab4ff / #a6ecff / #1c62d8.
import { compareToEquipped, describe, RARITY } from './loot.js';

export const ARROW_PAL = {
  up: { hi: '#b8ffd4', mid: '#3cf08a', lo: '#14a85a' },
  down: { hi: '#ff5a4a', mid: '#e0302a', lo: '#a81c22' },
  equal: { hi: '#a6ecff', mid: '#2ab4ff', lo: '#1c62d8' },
};

const UP = [
  '...........',
  '.....2.....',
  '....211....',
  '...21112...',
  '..2111112..',
  '.211111112.',
  '.....1.....',
  '.....1.....',
  '.....1.....',
  '.....1.....',
  '.....1.....',
  '.....3.....',
  '...........',
];
const DOWN = [
  '...........',
  '.....1.....',
  '.....1.....',
  '.....1.....',
  '.....1.....',
  '.....1.....',
  '.211111112.',
  '..2111112..',
  '...21112...',
  '....211....',
  '.....2.....',
  '.....3.....',
  '...........',
];
// Same 11×13 grid as the arrows. Two bars, hi on the top edge of each, mid underneath.
const EQUAL = [
  '...........',
  '...........',
  '...........',
  '.222222222.',
  '.111111111.',
  '...........',
  '...........',
  '...........',
  '.222222222.',
  '.111111111.',
  '...........',
  '...........',
  '...........',
];

export function arrowDir(item, gear) { return compareToEquipped(item, gear); }
export function arrowKind(item, gear) {
  const d = arrowDir(item, gear);
  if (d > 0) return 'up';
  if (d < 0) return 'down';
  return item && item.slot ? 'equal' : 'none';
}

function arrowCanvas(dir, scale) {
  const kind = dir > 0 ? 'up' : dir < 0 ? 'down' : 'equal';
  const rows = kind === 'up' ? UP : kind === 'down' ? DOWN : EQUAL, h = rows.length, w = rows[0].length;
  const cv = document.createElement('canvas');
  cv.width = w * scale; cv.height = h * scale;
  const g = cv.getContext('2d'); g.imageSmoothingEnabled = false;
  const ramp = ARROW_PAL[kind];
  const on = (x, y) => x >= 0 && y >= 0 && y < h && x < w && rows[y][x] !== '.';
  const px = (x, y, c) => { g.fillStyle = c; g.fillRect(x * scale, y * scale, scale, scale); };
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    if (on(x, y)) continue;
    if (on(x - 1, y) || on(x + 1, y) || on(x, y - 1) || on(x, y + 1)) px(x, y, ramp.lo);
  }
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const ch = rows[y][x];
    if (ch === '2') px(x, y, ramp.hi);
    else if (ch === '1') px(x, y, ramp.mid);
    else if (ch === '3') px(x, y, ramp.lo);
  }
  cv.className = 'garrow';
  cv.dataset.dir = kind;
  // `.card canvas` in game.css is 60×96 and matches every canvas in the hero card, so a bag-row
  // arrow (scale 2 → 22×26) was stretched and clipped the name. Pin each arrow to its bitmap.
  cv.style.width = cv.width + 'px';
  cv.style.height = cv.height + 'px';
  cv.style.flex = 'none';
  return cv;
}

// beam canvas sits on bottom: 6px inside a 0-tall .loot pin, so its top is -(6 + pixel height)
function placeWorld(cv, rar) {
  const r = rar | 0;
  const H = r >= 4 ? 38 : r >= 3 ? 34 : 26 + Math.max(0, r) * 3;
  const beamTop = -(6 + H * 3);
  cv.style.left = (-cv.width / 2) + 'px';
  cv.style.top = (beamTop - cv.height - 2) + 'px';
  cv.style.zIndex = '5';
}

function syncDrop(d, gear) {
  if (!d.it || !d.el) return;
  const dir = compareToEquipped(d.it, gear);
  if (d.arrowDir === dir && d.arrowEl && d.arrowEl.isConnected) return;
  d.arrowDir = dir;
  if (d.arrowEl) { d.arrowEl.remove(); d.arrowEl = null; }
  if (arrowKind(d.it, gear) === 'none') return;
  const cv = arrowCanvas(dir, 3);
  placeWorld(cv, d.it.rar);
  d.el.appendChild(cv);
  d.arrowEl = cv;
}

const ARMOR = new Set(['helm', 'chest', 'legs', 'feet', 'arms', 'gloves', 'belt', 'cloak']);
function piece(slot, name, mods, extra = {}) {
  return {
    uid: extra.uid || ('arr-' + name), slot, name, rar: extra.rar ?? 1, lv: extra.lv ?? 8, rv: 3, up: extra.up || 0,
    mods, gems: extra.gems || [], procs: extra.procs || [],
    at: extra.at !== undefined ? extra.at : (ARMOR.has(slot) ? 'leather' : undefined),
  };
}

let tipEl = null, marking = false;

function ensureUi() {
  if (document.getElementById('gearArrowCss')) return;
  const s = document.createElement('style');
  s.id = 'gearArrowCss';
  s.textContent = '#gearArrowTip{position:fixed;z-index:80;display:flex;gap:8px;align-items:flex-start;width:min(340px,88vw);padding:8px 10px;pointer-events:none;background:#f6ead0;color:#3a2a1c;border:3px solid #5a3e26;border-radius:4px;box-shadow:inset 0 0 0 2px #d9c193;font:700 13px/1.35 system-ui,sans-serif}'
    + '#gearArrowTip[hidden]{display:none}#gearArrowTip .gat-name{font:800 14px/1.2 Georgia,serif;margin:0 0 3px}'
    + '#gearArrowTip .gat-tag{font:800 11px/1.2 system-ui;letter-spacing:.04em;margin:0 0 4px}'
    + '#gearArrowTip .gat-lines{display:flex;flex-direction:column;gap:1px}#gearArrowTip canvas.garrow{flex:none;width:44px;height:52px;image-rendering:pixelated;image-rendering:crisp-edges}'
    + '#heroBody .row.gear .iname canvas.garrow{flex:none;width:22px;height:26px;max-width:22px;max-height:26px;image-rendering:pixelated;image-rendering:crisp-edges}'
    + '.loot canvas.garrow{flex:none;width:33px;height:39px;image-rendering:pixelated;image-rendering:crisp-edges}';
  document.head.appendChild(s);
  tipEl = document.createElement('div');
  tipEl.id = 'gearArrowTip';
  tipEl.hidden = true;
  document.body.appendChild(tipEl);
}

function openTip(it, gear, rect) {
  if (!tipEl || !it) return;
  const dir = compareToEquipped(it, gear);
  const kind = arrowKind(it, gear);
  const col = dir > 0 ? ARROW_PAL.up.mid : dir < 0 ? ARROW_PAL.down.mid : ARROW_PAL.equal.mid;
  const lines = describe(it).split(' · ');
  tipEl.innerHTML = '';
  if (kind !== 'none') tipEl.appendChild(arrowCanvas(dir, 4));
  const body = document.createElement('div');
  const name = document.createElement('div');
  name.className = 'gat-name';
  name.textContent = it.name;
  name.style.color = (RARITY[it.rar] || RARITY[0]).lo;
  body.appendChild(name);
  if (kind !== 'none') {
    const tag = document.createElement('div');
    tag.className = 'gat-tag';
    tag.style.color = col;
    tag.textContent = dir > 0 ? 'UPGRADE' : dir < 0 ? 'WORSE' : 'SAME';
    body.appendChild(tag);
  }
  const box = document.createElement('div');
  box.className = 'gat-lines';
  for (const line of lines) { const p = document.createElement('div'); p.textContent = line; box.appendChild(p); }
  body.appendChild(box);
  tipEl.appendChild(body);
  tipEl.hidden = false;
  tipEl.dataset.kind = kind;
  let left = rect ? Math.max(8, rect.right + 10) : 16;
  let top = rect ? Math.max(8, rect.top) : 16;
  tipEl.style.left = left + 'px';
  tipEl.style.top = top + 'px';
  const th = tipEl.offsetHeight, tw = tipEl.offsetWidth;
  if (top + th > window.innerHeight - 8) top = Math.max(8, window.innerHeight - th - 8);
  if (left + tw > window.innerWidth - 8) left = Math.max(8, window.innerWidth - tw - 8);
  tipEl.style.left = left + 'px';
  tipEl.style.top = top + 'px';
}

function hideTip() { if (tipEl) tipEl.hidden = true; }

function bagRows(body) {
  return [...body.children].filter((el) => el.classList && el.classList.contains('row') && el.classList.contains('gear'));
}

function markBag(G) {
  const body = document.getElementById('heroBody');
  if (!body || marking) return;
  marking = true;
  try {
    const gear = (G.S && G.S.gear) || {};
    const bag = (G.S && G.S.bag) || [];
    bagRows(body).forEach((row, i) => {
      const it = bag[i];
      const dir = it ? compareToEquipped(it, gear) : 0;
      const kind = it ? arrowKind(it, gear) : 'none';
      row.querySelectorAll('canvas.garrow').forEach((n) => n.remove());
      const name = row.querySelector('.iname');
      if (name && kind !== 'none') { name.style.minWidth = '0'; name.style.overflow = 'hidden'; name.prepend(arrowCanvas(dir, 2)); }
      if (!row.dataset.arrListen) {
        row.dataset.arrListen = '1';
        row.addEventListener('mouseenter', () => {
          const rows = bagRows(body), k = rows.indexOf(row), item = (G.S.bag || [])[k];
          if (item) openTip(item, G.S.gear || {}, row.getBoundingClientRect());
        });
        row.addEventListener('mouseleave', hideTip);
      }
    });
  } finally { marking = false; }
}

function watchBag(G) {
  const body = document.getElementById('heroBody');
  if (!body || body.dataset.arrWatch) return;
  body.dataset.arrWatch = '1';
  const mo = new MutationObserver(() => markBag(G));
  mo.observe(body, { childList: true });
}

// window.__hm.arrows. spawn / spawnTest drop a world pickup; qa() lists arrows on the drops still lying there.
export function attachArrows(G) {
  ensureUi();
  const loot = G.loot;
  const drop = loot.drop.bind(loot);
  loot.drop = (x, z, what) => {
    const d = drop(x, z, what);
    if (d && d.it) syncDrop(d, (G.S && G.S.gear) || {});
    return d;
  };
  const update = loot.update.bind(loot);
  loot.update = (dt) => {
    update(dt);
    const gear = (G.S && G.S.gear) || {};
    for (const d of loot.drops) if (d.it) syncDrop(d, gear);
  };
  watchBag(G);
  const api = {
    qa() {
      return loot.drops.filter((d) => d.it && d.el && d.el.isConnected).map((d) => {
        const gear = (G.S && G.S.gear) || {};
        const dir = compareToEquipped(d.it, gear);
        const kind = arrowKind(d.it, gear);
        const el = d.arrowEl;
        const r = el && el.isConnected ? el.getBoundingClientRect() : null;
        const onScreen = !!(r && r.width > 2 && r.bottom > 0 && r.right > 0 && r.top < window.innerHeight && r.left < window.innerWidth);
        return {
          name: d.it.name, slot: d.it.slot, dir,
          arrow: kind,
          color: kind === 'up' ? ARROW_PAL.up.mid : kind === 'down' ? ARROW_PAL.down.mid : kind === 'equal' ? ARROW_PAL.equal.mid : null,
          shown: kind !== 'none' && !!el,
          onScreen,
          rect: r ? { x: r.x, y: r.y, w: r.width, h: r.height } : null,
        };
      });
    },
    spawn(item, x, z) {
      const p = G.ctx && G.ctx.player;
      const px = p ? p.x : 0, pz = p ? p.z : 0;
      return loot.drop(x == null ? px + 1.05 : x, z == null ? pz - 0.7 : z, { item });
    },
    spawnTest(which, slot = 'chest', dx = 1.05, dz = -0.7) {
      const S = G.S;
      const weak = piece(slot, 'Dim ' + slot, { hpAdd: 2 }, { rar: 0, uid: 'arr-weak-' + slot });
      const strong = piece(slot, 'Bright ' + slot, { meleeMul: 0.28, runePct: 0.04, avoid: 0.02 }, { rar: 2, uid: 'arr-strong-' + slot });
      if (!S.gear) S.gear = {};
      if (which === 'down') S.gear[slot] = piece(slot, 'Kept ' + slot, { meleeMul: 0.4, runePct: 0.05 }, { rar: 3, uid: 'arr-kept-' + slot });
      else if (which === 'up') S.gear[slot] = weak;
      const it = which === 'down' ? weak : strong;
      const p = G.ctx && G.ctx.player;
      return loot.drop((p ? p.x : 0) + dx, (p ? p.z : 0) + dz, { item: it });
    },
    clearDrops() {
      for (const d of [...loot.drops]) { if (d.el) d.el.remove(); if (d.light) d.light.kill = true; }
      loot.drops.length = 0;
    },
    markBag() { markBag(G); },
    showTip(i = 0) {
      markBag(G);
      const body = document.getElementById('heroBody');
      const row = body ? bagRows(body)[i] : null;
      const it = (G.S.bag || [])[i];
      if (!it) return false;
      openTip(it, G.S.gear || {}, row ? row.getBoundingClientRect() : { right: 24, top: 80 });
      return true;
    },
    hideTip,
    putBag(it) {
      if (!Array.isArray(G.S.bag)) G.S.bag = [];
      G.S.bag.push(it);
      return G.S.bag.length - 1;
    },
  };
  G.arrows = api;
  return api;
}
