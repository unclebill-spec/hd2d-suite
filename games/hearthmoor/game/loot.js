// Hearthmoor loot (stage 2): five rarities, pixel loot beams, gold, a bag + three equipment slots.
// Drops are crisp DOM pixel canvases pinned to the world (like the damage numbers): a beam column in the
// rarity colour, Epic adds a faint stepped glow, Legendary an animated neon aura. No blur, no bloom.
export const RARITY = [
  { id: 'common', name: 'Common', col: '#fff8e6', lo: '#c4a984', w: 52, mul: 1, scrap: 2 },
  { id: 'uncommon', name: 'Uncommon', col: '#b2c464', lo: '#4a7234', w: 27, mul: 1.4, scrap: 4 },
  { id: 'rare', name: 'Rare', col: '#6c8cd4', lo: '#3e5a8c', w: 13, mul: 1.9, scrap: 8 },
  { id: 'epic', name: 'Epic', col: '#b07ce0', lo: '#6a3e9a', w: 6, mul: 2.6, scrap: 16 },
  { id: 'legendary', name: 'Legendary', col: '#f2a63a', lo: '#c4502c', w: 2, mul: 3.5, scrap: 32 },
];
export const SLOTS = ['weapon', 'armor', 'trinket'];
export const BAG_MAX = 30;
const INK = '#2a1e1c';
const BASES = {
  weapon: ['Oak Wand', 'Iron Sword', 'Hearth Staff', 'Ember Blade', 'Willow Bow', 'Rune Hammer'],
  armor: ['Wool Tunic', 'Leather Jerkin', 'Moss Mail', 'Rune Coat', 'Bakers Apron', 'Lantern Cloak'],
  trinket: ['Acorn Charm', 'Moon Locket', 'Glow Ring', 'Toadstool Brooch', 'Firefly Jar', 'Hearth Ember'],
};
const PREFIX = [['Plain', 'Worn', 'Sturdy'], ['Fine', 'Mossy', 'Bright'], ['Gleaming', 'Runed', 'Moonlit'], ['Starlit', 'Spellwoven', 'Twilight'], ['Sunfire', 'Elderglow', 'Rainbow']];
// 8x8 icons: weapon / armor / trinket / gold (1 = rarity colour, 2 = light, 3 = dark)
const ICONS = {
  weapon: ['......2.', '.....21.', '....21..', '...21...', '.321....', '..33....', '.3..3...', '........'],
  armor: ['.11..11.', '.111111.', '..1221..', '..1111..', '..1111..', '..1331..', '..1..1..', '........'],
  trinket: ['...33...', '..3..3..', '...11...', '..1221..', '.112211.', '..1111..', '...11...', '........'],
  gold: ['........', '..1111..', '.112211.', '.121111.', '.111111.', '.111131.', '..1111..', '........'],
};

let uidN = 0;
const pickW = (rnd, ws) => { let t = ws.reduce((a, b) => a + b, 0) * rnd(); for (let i = 0; i < ws.length; i++) { t -= ws[i]; if (t <= 0) return i; } return 0; };
export function ensure(S) {
  if (!Array.isArray(S.bag)) S.bag = [];
  if (!S.gear || typeof S.gear !== 'object') S.gear = { weapon: null, armor: null, trinket: null };
  if (typeof S.gold !== 'number') S.gold = (S.inv && S.inv.coin) || 0;
  return S;
}
export function makeItem(lv = 1, rar = null, slot = null, rnd = Math.random, luck = 0) {
  const r = rar ?? pickW(rnd, RARITY.map((x, i) => x.w * (luck && i >= 2 ? 1.6 : 1)));
  const sl = slot || SLOTS[Math.floor(rnd() * 3)];
  const R = RARITY[r], k = R.mul * (1 + (lv - 1) * 0.06);
  const base = BASES[sl][Math.floor(rnd() * BASES[sl].length)], pre = PREFIX[r][Math.floor(rnd() * 3)];
  const mods = {};
  if (sl === 'weapon') { mods.meleeMul = +(0.04 * k).toFixed(3); mods.spellMul = +(0.04 * k).toFixed(3); }
  else if (sl === 'armor') { mods.hpAdd = Math.round(8 * k); mods.guardMul = -+(0.015 * k).toFixed(3); }
  else { mods.crit = +(0.01 * k).toFixed(3); mods.stAdd = Math.round(4 * k); if (r >= 3) mods.summonMul = +(0.05 * k).toFixed(3); }
  return { uid: `${Date.now().toString(36)}${(uidN++).toString(36)}`, slot: sl, name: `${pre} ${base}`, rar: r, lv, mods };
}
export function describe(it) {
  const m = it.mods, out = [];
  if (m.meleeMul) out.push(`+${Math.round(m.meleeMul * 100)}% melee`);
  if (m.spellMul) out.push(`+${Math.round(m.spellMul * 100)}% spells`);
  if (m.hpAdd) out.push(`+${m.hpAdd} HP`);
  if (m.guardMul) out.push(`guard ${Math.round(m.guardMul * 100)}% dmg`);
  if (m.crit) out.push(`+${(m.crit * 100).toFixed(1)}% crit`);
  if (m.stAdd) out.push(`+${m.stAdd} stamina`);
  if (m.summonMul) out.push(`+${Math.round(m.summonMul * 100)}% summons`);
  return out.join(' · ');
}
export function gearMods(S, m) {   // fold equipped gear into progress.mods()
  for (const it of Object.values((S && S.gear) || {})) {
    if (!it) continue;
    for (const [k, v] of Object.entries(it.mods)) {
      if (k === 'guardMul') m.guardMul = Math.max(0.4, m.guardMul + v);
      else m[k] = (m[k] || 0) + v;
    }
  }
  return m;
}
// pixel art: icon canvas (8x8 at scale, 1 px ink outline) and beam canvas
export function iconCanvas(kind, rar, scale = 3) {
  const R = RARITY[rar] || RARITY[0], rows = ICONS[kind] || ICONS.trinket;
  const cv = document.createElement('canvas'); cv.width = 10 * scale; cv.height = 10 * scale;
  const g = cv.getContext('2d'); g.imageSmoothingEnabled = false;
  const col = { 1: kind === 'gold' ? '#f2c24a' : R.col, 2: '#fff8e6', 3: kind === 'gold' ? '#c4502c' : R.lo };
  const on = (x, y) => y >= 0 && y < 8 && x >= 0 && x < 8 && rows[y][x] !== '.';
  const px = (x, y, c) => { g.fillStyle = c; g.fillRect(x * scale, y * scale, scale, scale); };
  for (let y = -1; y < 9; y++) for (let x = -1; x < 9; x++) if (!on(x, y) && (on(x + 1, y) || on(x - 1, y) || on(x, y + 1) || on(x, y - 1))) px(x + 1, y + 1, INK);
  for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) if (on(x, y)) px(x + 1, y + 1, col[rows[y][x]] || R.col);
  return cv;
}
function beamCanvas(rar, scale = 3, frame = 0) {
  const R = RARITY[rar], H = rar >= 3 ? 34 : 26 + rar * 2;
  const cv = document.createElement('canvas'); cv.width = 7 * scale; cv.height = H * scale;
  drawBeam(cv, rar, scale, frame);
  return cv;
}
function drawBeam(cv, rar, scale, frame) {
  const R = RARITY[rar], g = cv.getContext('2d'), H = cv.height / scale;
  g.clearRect(0, 0, cv.width, cv.height);
  const px = (x, y, c) => { g.fillStyle = c; g.fillRect(x * scale, y * scale, scale, scale); };
  for (let y = 0; y < H; y++) {
    const t = y / H;                                   // 0 top .. 1 bottom: dither thins out towards the top
    const keep = (x) => ((x + y + frame) % 4 === 0) || t > 0.75 || (t > 0.4 && (x + y) % 2 === 0);
    if (keep(3) || t > 0.2) px(3, y, t > 0.55 ? '#fff8e6' : R.col);
    if (keep(2)) px(2, y, R.col); if (keep(4)) px(4, y, R.col);
    if (t > 0.6 && (y + frame) % 2 === 0) { px(1, y, R.lo); px(5, y, R.lo); }
  }
  if (rar >= 1) for (let k = 0; k < rar; k++) { const y = (Math.floor(frame * 1.5) + k * 7) % H; px(k % 2 ? 6 : 0, H - 1 - y, '#fff8e6'); }   // rising motes
}
// Legendary aura: a ring of neon pixels marching round the drop (4 frames, colours cycle)
function drawAura(cv, scale, frame, epic, worn = false) {
  const g = cv.getContext('2d'), W = cv.width / scale, Hh = cv.height / scale;
  g.clearRect(0, 0, cv.width, cv.height);
  const cols = epic ? ['#b07ce0', '#e0c8f4', '#6a3e9a'] : ['#f2a63a', '#f2c24a', '#fff8e6', '#e47c8c'];
  // worn (under the hero): the DOM layer sits over the sprite, so the back arc behind the legs is left out
  const px = (x, y, c) => { if (worn && y < Hh / 2 - 0.5 && Math.abs(x - W / 2) < 6) return; g.fillStyle = c; g.fillRect(Math.round(x) * scale, Math.round(y) * scale, scale, scale); };
  const ring = (rx, ry, n, skip, off) => {
    for (let i = 0; i < n; i++) {
      if ((i + frame + off) % skip) continue;
      const a = i / n * Math.PI * 2;
      px(W / 2 + Math.cos(a) * rx, Hh / 2 + Math.sin(a) * ry, cols[(i + frame) % cols.length]);
    }
  };
  ring(W / 2 - 1, Hh / 2 - 1, epic ? 30 : 44, 2, 0);                 // outer marching ring
  if (!epic) ring(W / 2 - 4, Hh / 2 - 2.5, 30, 3, 1);                 // legendary: a second, counter-phased ring
  // four sparks orbiting (plus shapes, white core)
  const k = epic ? 2 : 4;
  for (let j = 0; j < k; j++) {
    const a = (frame / 8 + j / k) * Math.PI * 2, x = W / 2 + Math.cos(a) * (W / 2 - 2), y = Hh / 2 + Math.sin(a) * (Hh / 2 - 1.5);
    px(x, y, '#fff8e6'); px(x + 1, y, cols[0]); px(x - 1, y, cols[0]); px(x, y - 1, cols[1]); px(x, y + 1, cols[1]);
  }
}

export class Loot {
  constructor(G) { this.G = G; this.layer = document.getElementById('fxlayer'); this.drops = []; this.t = 0; }
  attach(ctx) { this.clear(); this.ctx = ctx; }
  detach() { this.clear(); this.ctx = null; }
  clear() {
    for (const d of this.drops) { d.el.remove(); if (d.light) d.light.kill = true; }
    this.drops = [];
    if (this.pa) { this.pa.el.remove(); if (this.pa.light) this.pa.light.kill = true; this.pa = null; }
  }
  // a Legendary equipped: the same marching neon ring under the hero's feet, plus a warm rune light that follows
  playerAura(fr) {
    const ctx = this.ctx, S = this.G.S, p = ctx.player;
    const on = !!Object.values(S.gear || {}).some((it) => it && it.rar === 4) && !this.G.title;
    if (!on) { if (this.pa) { this.pa.el.remove(); if (this.pa.light) this.pa.light.kill = true; this.pa = null; } return; }
    if (!this.pa) {
      const el = document.createElement('div'); el.className = 'loot paura';
      const cv = document.createElement('canvas'); cv.width = 26 * 3; cv.height = 13 * 3; cv.className = 'aura'; el.appendChild(cv);
      this.layer.appendChild(el);
      const light = ctx.addGlow ? ctx.addGlow(p.x, p.y, p.z, { color: RARITY[4].col, intensity: 2.6, range: 2.6, lift: 0.5, fadeIn: 0.4 }) : null;
      this.pa = { el, cv, light, frame: -1 };
    }
    const s = ctx.project(p.x, p.y + 0.03, p.z);
    this.pa.el.style.transform = `translate(${Math.round(s.x)}px, ${Math.round(s.y)}px)`;
    this.pa.el.style.visibility = p.quad && !p.quad.visible ? 'hidden' : '';
    if (this.pa.light) this.pa.light.pos.set(p.x, p.y, p.z);
    if (fr !== this.pa.frame) { this.pa.frame = fr; drawAura(this.pa.cv, 3, fr % 8, false, true); }
  }
  // an enemy went down: gold always, and sometimes an item (rarity weights, level-scaled)
  onKill(a, lv, o = {}) {
    const gold = 2 + Math.floor(Math.random() * 5) + (o.gold || 0);
    this.drop(a.x + 0.35, a.z + 0.2, { gold });
    const luck = this.G.S.mode === 'hero' ? 1 : 0;
    if (o.legendary) { this.drop(a.x - 0.3, a.z + 0.35, { item: makeItem(lv + 1, 4, null, Math.random, luck) }); return; }   // a boss: always a Legendary
    if (Math.random() < 0.6 + luck * 0.1) this.drop(a.x - 0.3, a.z + 0.35, { item: makeItem(lv, null, null, Math.random, luck) });
  }
  drop(x, z, what) {
    const ctx = this.ctx; if (!ctx || !this.layer) return null;
    const y = ctx.heightAt(x, z), it = what.item || null, rar = it ? it.rar : -1;
    const el = document.createElement('div'); el.className = 'loot' + (it ? ' r' + rar : ' gold') + (what.purse ? ' purse' : '');
    const sc = 3;
    let beam = null, aura = null;
    if (it) { beam = beamCanvas(rar, sc); beam.className = 'beam'; el.appendChild(beam); }
    if (rar >= 3) { aura = document.createElement('canvas'); aura.width = 26 * sc; aura.height = 13 * sc; aura.className = 'aura'; el.appendChild(aura); }
    const icon = iconCanvas(it ? it.slot : 'gold', Math.max(0, rar), sc); icon.className = 'icon'; el.appendChild(icon);
    this.layer.appendChild(el);
    // Epic / Legendary drops also light the ground around them (a pooled point light, no bloom)
    const light = rar >= 3 && ctx.addGlow ? ctx.addGlow(x, y, z, { color: RARITY[rar].col, intensity: rar === 4 ? 6 : 3.5, range: 2.8, lift: 0.45, fadeIn: 0.3 }) : null;
    const d = { x, y, z, it, gold: what.gold || 0, purse: !!what.purse, el, beam, aura, sc, frame: -1, t: 0, light };
    this.drops.push(d);
    return d;
  }
  update(dt) {
    const ctx = this.ctx; if (!ctx) return;
    this.t += dt;
    const p = ctx.player, fr = Math.floor(this.t * 6);
    this.playerAura(fr);
    for (const d of [...this.drops]) {
      d.t += dt;
      if (!this.G.downed && Math.hypot(p.x - d.x, p.z - d.z) < 0.75 && d.t > 0.4) { this.pick(d); continue; }
      const s = ctx.project(d.x, d.y + 0.05, d.z);
      d.el.style.transform = `translate(${Math.round(s.x)}px, ${Math.round(s.y)}px)`;
      if (fr !== d.frame) {
        d.frame = fr;
        if (d.beam) drawBeam(d.beam, d.it.rar, d.sc, fr);
        if (d.aura) drawAura(d.aura, d.sc, fr % 8, d.it.rar === 3);
      }
    }
  }
  pick(d) {
    const G = this.G, S = ensure(G.S);
    if (d.it && S.bag.length >= BAG_MAX) { if (!d.full) { d.full = true; G.toast && G.toast('Bag full: scrap something on the gear page (G)', 2.4); } return; }
    d.el.remove(); this.drops.splice(this.drops.indexOf(d), 1);
    if (d.purse) { S.purse = null; G.toast && G.toast(`Found your purse: +${d.gold} gold`, 2.4); }
    if (d.gold) { S.gold += d.gold; G.popText && G.popText(`+${d.gold}`, d, '#f2c24a'); }
    if (d.it) { S.bag.push(d.it); G.toast && G.toast(`<span style="color:${RARITY[d.it.rar].lo}">${RARITY[d.it.rar].name}</span> ${d.it.name}`, 2.4, true); }
    G.audio && G.audio.sfx('pickup');
    if (d.light) d.light.kill = true;
    G.drawBag && G.drawBag();
    G.onLoot && G.onLoot(d);
  }
  removePurse() { for (const d of this.drops.filter((x) => x.purse)) { d.el.remove(); if (d.light) d.light.kill = true; this.drops.splice(this.drops.indexOf(d), 1); } }
  restorePurse(area) { const P = this.G.S.purse; if (P && P.area === area && P.gold > 0) this.drop(P.x, P.z, { gold: P.gold, purse: true }); }
  auraOn() { return !!this.pa; }
  qa() { return this.drops.map((d) => ({ x: +d.x.toFixed(2), z: +d.z.toFixed(2), gold: d.gold, rar: d.it ? d.it.rar : null, slot: d.it ? d.it.slot : null })); }
}
// bag / gear actions (the hero screen's Gear tab calls these)
export function equip(S, i) {
  ensure(S); const it = S.bag[i]; if (!it) return false;
  const cur = S.gear[it.slot]; S.gear[it.slot] = it; S.bag.splice(i, 1); if (cur) S.bag.splice(i, 0, cur);
  return true;
}
export function unequip(S, slot) {
  ensure(S); const it = S.gear[slot]; if (!it || S.bag.length >= BAG_MAX) return false;
  S.gear[slot] = null; S.bag.unshift(it); return true;
}
export function scrap(S, i) {
  ensure(S); const it = S.bag[i]; if (!it) return 0;
  S.bag.splice(i, 1); const g = RARITY[it.rar].scrap; S.gold += g; return g;
}
