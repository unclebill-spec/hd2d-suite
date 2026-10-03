// Hearthmoor shops (stage 3): Odo's stall in the Plaza (tonics, glow seeds, plain gear; buys your loot back) and
// Sefa's Lantern Pack, the travelling night merchant (night hours only: socket gems + rarer, socketed gear).
// The shop is a parchment / wood panel like the hero screen: keys, controller and touch all drive the same rows.
import * as LO from './loot.js';

export const GOODS = {
  tonic: { name: 'Hearth tonic', about: 'Drink (U, right-stick click, or tap it in the bag): heals 60 HP.', price: 12 },
  glowseed: { name: 'Glow seed', about: 'A seed that hums in the dark. Keep a few: glow-gardens are coming.', price: 8 },
};
// buy price of a piece of gear by rarity (sell-back is a quarter of it, always more than scrapping)
const GEAR_PRICE = [20, 45, 110, 260, 600];
export const buyPrice = (it) => Math.round(GEAR_PRICE[it.rar] * (1 + 0.05 * ((it.lv || 1) - 1)));
export const sellPrice = (it, mul = 1) => Math.max(LO.RARITY[it.rar].scrap + 1, Math.round(buyPrice(it) * 0.25 * mul));

export const SHOPS = {
  hearthmoor: { name: "Odo's Wares", keeper: 'Odo the merchant', goods: ['tonic', 'glowseed'], gear: { n: 3, rar: [0, 0, 1] }, sellMul: 1 },
  night: { name: 'The Lantern Pack', keeper: 'Sefa, the night merchant', goods: ['tonic'], gems: ['rift_shard', 'golem_core', 'frost_core', 'moon_opal'],
           gear: { n: 2, rar: [2, 3], sockets: 1 }, sellMul: 1.2 },
};
// the travelling night merchant: sets up by the well after dark, packs up at dawn (a neon-blue cold-fire lantern)
export const NIGHT_MERCHANT = { plaza: { id: 'nightmerchant', role: 'nightmerchant', name: 'Sefa, the night merchant', pos: [-9.7, 1.7], facing: 'down',
  say: ['Lantern Pack, open till dawn.'] } };
export const NIGHT = (t) => t > 0.8 || t < 0.25;
const LANTERN = '#5ab4f0';
export const MERCHANT = { plaza: { id: 'merchant', role: 'shopkeeper', name: 'Odo the merchant', pos: [5.0, 0.3], facing: 'down',
  say: ['Tonics, seeds, sturdy kit. And I buy whatever you drag out of the glade.'] } };

const pick = (a) => a[Math.floor(Math.random() * a.length)];
export class Shop {
  constructor(G) { this.G = G; this.open = null; this.tab = 0; this.i = 0; this.stock = {}; this.confirm = -1; }
  attach(ctx, area) {
    this.ctx = ctx; this.area = area;
    const M = MERCHANT[area];
    if (M && !ctx.npc(M.id)) { const a = ctx.addNpc({ ...M, pos: M.pos.slice(), behavior: 'idle', talkable: true }); a.facing = M.facing; }
  }
  detach() { this.close(); if (this.nm && this.nm.light) this.nm.light.kill = true; this.nm = null; this.ctx = null; }
  // per frame: the night merchant comes and goes with the dark (not while you are mid-purchase with him)
  update(dt) {
    const ctx = this.ctx, M = ctx && NIGHT_MERCHANT[this.area]; if (!M) return;
    const night = NIGHT(ctx.clock.t), a = ctx.npc(M.id);
    if (night && !a) {
      const n = ctx.addNpc({ ...M, pos: M.pos.slice(), behavior: 'idle', talkable: true }); n.facing = M.facing;
      if (ctx.effects && !this.G.qaStill) ctx.effects.spawn('summon_poof', n.x, n.y, n.z + 0.05);
      this.nm = { a: n, light: ctx.addGlow ? ctx.addGlow(n.x + 0.35, n.y, n.z + 0.1, { color: LANTERN, intensity: 5, range: 3.8, lift: 0.7, fadeIn: 0.8 }) : null };
      delete this.stock.night;   // fresh stock every night
    } else if (!night && a && this.open !== 'night') {
      if (ctx.effects) ctx.effects.spawn('summon_poof', a.x, a.y, a.z + 0.05);
      ctx.removeNpc(a); if (this.nm && this.nm.light) this.nm.light.kill = true; this.nm = null;
    }
  }
  nightHere() { return !!(this.ctx && NIGHT_MERCHANT[this.area] && this.ctx.npc(NIGHT_MERCHANT[this.area].id)); }
  // the day's gear on the stall: rolled when you first open the shop after arriving in the area
  stockOf(id) {
    const D = SHOPS[id], lv = this.G.S.lv || 1;
    if (!this.stock[id]) this.stock[id] = D.gear.rar.map((r, k) => {
      const it = LO.makeItem(lv + (D.gear.sockets ? 1 : 0), r, LO.SLOTS[(k + (D.gear.sockets ? 1 : 0)) % 3]);
      if (D.gear.sockets && it.gems.length < D.gear.sockets) it.gems = Array(D.gear.sockets).fill(null);   // the night stock always has a socket
      return it;
    });
    return this.stock[id];
  }
  rows() {
    const S = this.G.S, D = SHOPS[this.open];
    if (this.tab === 0) {
      return [...D.goods.map((g) => ({ kind: 'good', id: g, name: GOODS[g].name, about: GOODS[g].about, price: GOODS[g].price, have: (S.inv[g] || 0) })),
              ...(D.gems || []).map((g) => ({ kind: 'gem', id: g, name: LO.GEMS[g].name, about: `socket gem · ${LO.GEMS[g].about}`, price: LO.GEMS[g].price, have: (S.gems[g] || 0) })),
              ...this.stockOf(this.open).map((it, k) => ({ kind: 'gear', it, k, name: it.name, about: `${LO.RARITY[it.rar].name} ${it.slot} · ${LO.describe(it)}`, price: buyPrice(it) }))];
    }
    return (S.bag || []).map((it, k) => ({ kind: 'sell', it, k, name: it.name, about: `${LO.RARITY[it.rar].name} ${it.slot} · ${LO.describe(it)}`, price: sellPrice(it, D.sellMul) }));
  }
  show(id) {
    const G = this.G;
    if (G.title || G.busy || G.picking || G.heroUI) return false;
    LO.ensure(G.S);
    this.open = id; this.tab = 0; this.i = 0; this.confirm = -1; G.shop = true;
    document.getElementById('shopui').hidden = false;
    this.draw();
    return true;
  }
  close() {
    if (!this.open) return;
    this.open = null; this.G.shop = false;
    const el = document.getElementById('shopui'); if (el) el.hidden = true;
    this.G.save && this.G.save();
  }
  draw() {
    const G = this.G, S = G.S, D = SHOPS[this.open]; if (!D) return;
    const $ = (id) => document.getElementById(id);
    $('shopHead').innerHTML = `<b>${D.name}</b> <span class="tag">${D.keeper}</span><span class="tag gold">gold ${S.gold || 0}</span><span class="tag">bag ${S.bag.length} / ${LO.BAG_MAX}</span>`;
    document.querySelectorAll('#shopTabs button').forEach((b, k) => b.classList.toggle('on', k === this.tab));
    const rows = this.rows(); this.n = rows.length; this.i = Math.min(this.i, Math.max(0, rows.length - 1));
    const body = $('shopBody');
    const hint = this.tab === 0 ? 'Enter / A / tap buy · ← → or LB / RB: sell tab' : 'Enter / A / tap sell (Epic and Legendary ask twice) · ← → or LB / RB: buy tab';
    body.innerHTML = `<p class="pts">${hint}</p>` + (rows.length ? '' : '<p class="pts">nothing in the bag to sell yet</p>')
      + rows.map((r, k) => {
        const rar = r.it ? r.it.rar : -1, cant = r.kind !== 'sell' && ((S.gold || 0) < r.price || (r.kind === 'gear' && S.bag.length >= LO.BAG_MAX));
        const label = r.kind === 'sell' ? (this.confirm === k ? `sure? ${r.price}g` : `sell ${r.price}g`) : `buy ${r.price}g`;
        return `<div class="row gear${rar >= 0 ? ' r' + rar : ' good'}${k === this.i ? ' sel' : ''}" data-k="${k}">`
          + `<em class="iname">${r.it ? `<i class="ic" data-ic="${k}"></i>` : r.kind === 'gem' ? `<i class="gm" data-gm="${r.id}"></i>` : `<i class="gd" data-gd="${r.id}"></i>`}${r.name}${r.kind === 'good' || r.kind === 'gem' ? ` <small>(have ${r.have})</small>` : ''}</em>`
          + `<span>${r.about}</span><span class="bb"><button class="wbtn sm plus" data-buy="${k}" ${cant ? 'disabled' : ''}>${label}</button></span></div>`;
      }).join('');
    body.querySelectorAll('[data-ic]').forEach((el) => { const it = rows[+el.dataset.ic].it; const cv = LO.iconCanvas(it.slot, it.rar, 2, it.gems); cv.className = 'gicon'; el.replaceWith(cv); });
    body.querySelectorAll('[data-gm]').forEach((el) => { const cv = LO.iconCanvas('gem', 0, 2, [el.dataset.gm]); cv.className = 'gicon'; el.replaceWith(cv); });
    body.querySelectorAll('[data-gd]').forEach((el) => { const cv = goodIcon(el.dataset.gd, 2); cv.className = 'gicon gd'; el.replaceWith(cv); });
    body.querySelectorAll('[data-buy]').forEach((b) => { b.onclick = (e) => { e.stopPropagation(); this.i = +b.dataset.buy; this.act(); }; });
    body.querySelectorAll('.row').forEach((r) => { r.onclick = () => { this.i = +r.dataset.k; this.confirm = -1; this.draw(); }; });
    const sel = body.querySelector('.row.sel'); if (sel && sel.scrollIntoView) sel.scrollIntoView({ block: 'nearest' });
  }
  act() {
    const G = this.G, S = G.S, r = this.rows()[this.i]; if (!r) return false;
    if (r.kind === 'sell') {
      if (r.it.rar >= 3 && this.confirm !== this.i) { this.confirm = this.i; this.draw(); return false; }
      S.bag.splice(r.k, 1); S.gold = (S.gold || 0) + r.price; this.confirm = -1;
      G.toast && G.toast(`Sold ${r.name} for ${r.price} gold`, 1.6); G.audio && G.audio.sfx('pickup');
    } else {
      if ((S.gold || 0) < r.price) { G.toast && G.toast('Not enough gold', 1.2); return false; }
      if (r.kind === 'gear') {
        if (S.bag.length >= LO.BAG_MAX) { G.toast && G.toast('Bag full', 1.2); return false; }
        S.gold -= r.price; S.bag.push(r.it); this.stock[this.open].splice(r.k, 1);
      } else if (r.kind === 'gem') { S.gold -= r.price; S.gems[r.id] = (S.gems[r.id] || 0) + 1; }
      else { S.gold -= r.price; S.inv[r.id] = (S.inv[r.id] || 0) + 1; }
      G.toast && G.toast(`Bought ${r.name}`, 1.4); G.audio && G.audio.sfx('pickup');
    }
    G.drawBag && G.drawBag(); this.draw();
    return true;
  }
  setTab(t) { this.tab = (t + 2) % 2; this.i = 0; this.confirm = -1; this.draw(); }
  move(d) { this.i = Math.max(0, Math.min((this.n || 1) - 1, this.i + d)); this.confirm = -1; this.draw(); }
  key(k, e) {
    if (k === 'escape' || k === 'b' || k === 'i' || k === 'g') this.close();
    else if (k === 'arrowleft' || k === 'a' || k === 'q') this.setTab(this.tab - 1); else if (k === 'arrowright' || k === 'd' || k === 'e') this.setTab(this.tab + 1);
    else if (k === 'arrowup' || k === 'w') this.move(-1); else if (k === 'arrowdown' || k === 's') this.move(1);
    else if (k === 'enter' || k === ' ' || k === 'f') { e && e.preventDefault(); this.act(); }
  }
  pad(name) {
    if (name === 'b' || name === 'start') this.close();
    else if (name === 'lb' || name === 'left') this.setTab(this.tab - 1); else if (name === 'rb' || name === 'right') this.setTab(this.tab + 1);
    else if (name === 'up') this.move(-1); else if (name === 'down') this.move(1);
    else if (name === 'a' || name === 'x') this.act();
  }
  wire() {
    const el = document.getElementById('shopui'); if (!el) return;
    document.getElementById('shopClose').onclick = () => this.close();
    document.querySelectorAll('#shopTabs button').forEach((b, k) => { b.onclick = () => this.setTab(k); });
    el.addEventListener('pointerdown', (e) => { if (e.target === el) this.close(); });
  }
  qa() { return { open: this.open, tab: this.tab, i: this.i, rows: this.open ? this.rows().map((r) => ({ kind: r.kind, name: r.name, price: r.price })) : [] }; }
}
// drink a Hearth tonic (U, right-stick click, tap the tonic in the bag)
export function drinkTonic(G) {
  const S = G.S, C = G.combat;
  if (!(S.inv.tonic > 0) || G.downed || !C || !C.ctx) return false;
  if (S.hp >= C.maxHp()) { G.toast && G.toast('Already at full health', 1.2); return false; }
  S.inv.tonic -= 1; if (!S.inv.tonic) delete S.inv.tonic;
  C.heal(60, true); G.audio && G.audio.sfx('pickup');
  if (C.ctx.effects) C.ctx.effects.spawn('healing_petals', C.ctx.player.x, C.ctx.player.y, C.ctx.player.z + 0.05);
  G.drawBag && G.drawBag();
  return true;
}
// 16x16 pixel icons for the shop goods (drawn at an integer scale, 1 px ink outline, never smoothed)
const GOOD_PX = {
  tonic: ['................', '......3333......', '......2222......', '.......11.......', '.......11.......', '.....111111.....', '....11444411....', '...1144444411...',
          '...1444444441...', '...1445444441...', '...1454444441...', '...1444444441...', '....14444441....', '.....111111.....', '................', '................'],
  glowseed: ['................', '.......5........', '......66.5......', '.....6..6.......', '.......66.......', '.......6........', '......777.......', '.....77887......',
             '....7788887.....', '....7888887.....', '....7888877..5..', '.....78877......', '......777.......', '..5.............', '................', '................'],
};
const GOOD_COL = { 1: '#c4d8e4', 2: '#fff8e6', 3: '#9a6a3c', 4: '#e47c8c', 5: '#f2c24a', 6: '#b2c464', 7: '#6a4428', 8: '#a8743e' };
export function goodIcon(id, scale = 2) {
  const rows = GOOD_PX[id] || GOOD_PX.tonic;
  const cv = document.createElement('canvas'); cv.width = 16 * scale; cv.height = 16 * scale;
  const g = cv.getContext('2d'); g.imageSmoothingEnabled = false;
  const on = (x, y) => y >= 0 && y < 16 && x >= 0 && x < 16 && rows[y][x] !== '.' && rows[y][x] !== '5';
  const px = (x, y, c) => { g.fillStyle = c; g.fillRect(x * scale, y * scale, scale, scale); };
  for (let y = 0; y < 16; y++) for (let x = 0; x < 16; x++) if (!on(x, y) && (on(x + 1, y) || on(x - 1, y) || on(x, y + 1) || on(x, y - 1))) px(x, y, '#2a1e1c');
  for (let y = 0; y < 16; y++) for (let x = 0; x < 16; x++) if (rows[y][x] !== '.') px(x, y, GOOD_COL[rows[y][x]]);
  return cv;
}
export function goodIconURL(id) { try { return goodIcon(id, 2).toDataURL(); } catch (e) { return ''; } }
