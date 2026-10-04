// Hearthmoor procedural rares (Stage 5 part 2). A rare = a base body (drawn natively at 2-3x the hero on the area's
// boss sheet: tools/sprite/boss_sheet.py) + an element affix (Frostfire blue / Gloam violet / Bloodmoon red: the
// name prefix, a ground aura decal and its own light) + a trait (Shielded, Enraged, Blinking, Summoner). Rares roam
// Mossglen, the Hollows and Vanaheim now and then, and come out of random rifts. Every kill goes into the hunt log
// (S.hunt) and always drops a Rare-or-better item. Seeded (day + area), so a day's rare is the same on a reload.
import { ENEMIES } from './heroes.js';

export const BASES = {
  elderwraith: { name: 'Elder Wraith', scale: 2.4, hp: 240, dmg: 12, speed: 1.45, reach: 6.5, keep: 3.6, windup: 0.55, cd: 1.9, aggro: 8.5, r: 0.62, push: 0.4,
                 ranged: true, float: true, bolt: 'coldfire_bolt', minion: 'wraith', xp: 160 },
  deathlord: { name: 'Death Lord', scale: 2.4, hp: 320, dmg: 19, speed: 1.3, reach: 2.6, windup: 0.62, cd: 1.7, aggro: 7.5, r: 0.7, push: 0.2, heavy: true,
               minion: 'skeleton', xp: 180 },
  sporemother: { name: 'Sporemother', scale: 2.2, hp: 280, dmg: 11, speed: 1.2, reach: 6.5, keep: 3.8, windup: 0.6, cd: 2.1, aggro: 8, r: 0.66, push: 0.4,
                 ranged: true, float: true, bolt: 'seed_bomb', minion: 'sporeling', xp: 170 },
};
export const ELEMENTS = {
  frost: { prefix: 'Frostfire', col: '#94c0dc', aura: 'rare_aura_blue', hex: 'sky' },
  gloam: { prefix: 'Gloam', col: '#a45cf0', aura: 'rare_aura_violet', hex: 'neon_violet' },
  blood: { prefix: 'Bloodmoon', col: '#e0302a', aura: 'rare_aura_red', hex: 'neon_red' },
};
export const TRAITS = {
  shielded: { name: 'Shielded', about: 'a rune ward soaks most of each hit until it breaks, then grows back' },
  enraged: { name: 'Enraged', about: 'below half health it gets faster and hits harder' },
  blinking: { name: 'Blinking', about: 'blinks to your side every few seconds' },
  summoner: { name: 'Summoner', about: 'calls lesser kin to fight beside it' },
};
// which bodies roam where (the area sheet must list them in spec boss_roles) and where they may appear
export const RARE_AREAS = {
  mossglen: { bases: ['elderwraith', 'deathlord'], spots: [[-6.0, -4.4], [5.0, 2.6], [-1.2, 5.6]] },
  hollows: { bases: ['elderwraith', 'deathlord'], spots: [[7.6, -0.8], [2.2, 5.4]] },
  vanaheim: { bases: ['sporemother'], spots: [[6.2, 0.4], [8.6, -2.2]] },
};
export const ROAM_CHANCE = 0.3;   // per area per day (0.45 at night)

// tiny seeded RNG (mulberry32) so a day's rare is stable
export function rngOf(seed) {
  let a = seed >>> 0;
  return () => { a = (a + 0x6d2b79f5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
export const hashStr = (s) => { let h = 2166136261; for (const c of String(s)) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619); } return h >>> 0; };
const pick = (r, arr) => arr[Math.floor(r() * arr.length) % arr.length];

// build a rare: { key, name, base, el, traits, D } (D is an ENEMIES-shaped def for combat.spawnEnemy)
export function makeRare(o = {}) {
  const r = rngOf(o.seed ?? hashStr(`${o.base || ''}:${Date.now()}`));
  const base = o.base || pick(r, Object.keys(BASES)), el = o.el || pick(r, Object.keys(ELEMENTS));
  const nT = o.nTraits || 1, keys = Object.keys(TRAITS), traits = o.traits ? o.traits.slice() : [];
  while (traits.length < nT) { const t = pick(r, keys); if (!traits.includes(t)) traits.push(t); }
  const B = BASES[base], E = ELEMENTS[el], lvK = 1 + Math.max(0, (o.lv || 1) - 1) * 0.06;
  const name = `${traits.map((t) => TRAITS[t].name).join(' ')} ${E.prefix} ${B.name}`;
  const D = { ...B, name, hp: Math.round(B.hp * lvK * (nT > 1 ? 1.3 : 1)), dmg: Math.round(B.dmg * lvK), rare: true, glow: E.col, el, traits, minRar: nT > 1 ? 3 : 2 };
  return { key: `${base}:${el}:${traits.join('+')}`, name, base, el, traits, D };
}

export class Rares {
  constructor(G) { this.G = G; this.list = []; this.t = 0; }
  get S() { return this.G.S; }
  attach(ctx, area) {
    this.ctx = ctx; this.area = area; this.list = [];
    const A = RARE_AREAS[area], G = this.G, S = this.S;
    if (!A || !this.sheetHas(A.bases[0])) return;
    const forced = G.qs && G.qs.has('rare');
    if (!forced && (G.qa || G.peace || G.qaStill)) return;   // QA / smoke: only when asked for
    const day = S.day || 0, key = `${day}:${area}`;
    S.rareDays = S.rareDays || {};
    if (!forced && S.rareDays[key]) return;                   // today's rare here is already hunted
    const r = rngOf(hashStr(`rare:${key}:${S.cls || ''}`)), ct = ctx.clock.t, night = ct > 0.8 || ct < 0.25;
    if (!forced && r() > (night ? 0.45 : ROAM_CHANCE)) return;
    const spot = pick(r, A.spots);
    this.spawn({ base: pick(r, A.bases), seed: hashStr(`rare:${key}:b`), pos: spot, roam: key });
  }
  detach() { for (const R of this.list) this.dropFx(R); this.list = []; this.ctx = null; }
  sheetHas(role) { try { return !!(this.ctx && this.ctx.actors && this.ctx.actors.sheetOf(role)); } catch (err) { return false; } }
  // spawn a rare near pos (snapped to a walkable cell); o: base, el, traits, nTraits, seed, pos, roam, rift
  spawn(o = {}) {
    const ctx = this.ctx, G = this.G; if (!ctx || !G.combat) return null;
    const A = RARE_AREAS[this.area];
    const base = o.base || (A ? A.bases[0] : 'elderwraith');
    const R = makeRare({ ...o, base, lv: this.S.lv || 1 });
    const pos = this.walk(o.pos || [ctx.player.x + 3, ctx.player.z]);
    const id = `rare_${(this.n = (this.n || 0) + 1)}`;
    const e = G.combat.spawnEnemy({ id, role: base, D: R.D, pos, once: true }, true);
    e.rare = R; R.e = e; R.roam = o.roam || null; R.rift = o.rift || null; R.minions = []; R.t = 0; R.blinkT = 4 + Math.random() * 2; R.callT = 6;
    R.ward = R.traits.includes('shielded') ? Math.round(R.D.hp * 0.25) : 0; R.wardMax = R.ward; R.wardT = 0;
    e.mods = { hurt: (en, dmg) => this.hurt(en, dmg) };
    e.tick = (en, dt, frozen) => this.tick(en, dt, frozen);
    e.onKill = (en) => this.onKill(en);
    if (ctx.effects) R.fx = ctx.effects.spawn(ELEMENTS[R.el].aura, e.a.x, e.a.y + 0.02, e.a.z, { duration: 1e9, fadeIn: 0.4 });
    if (ctx.effects) ctx.effects.spawn('glyph_burst', e.a.x, e.a.y, e.a.z + 0.05);
    this.list.push(R);
    G.audio && G.audio.sfx('portal');
    G.toast && G.toast(`<span style="color:${ELEMENTS[R.el].col}">✦ ${R.name}</span> appears!`, 2.6, true);
    return R;
  }
  walk(p) {
    const nav = this.ctx.nav; if (!nav) return p.slice();
    const [i, j] = nav.cellOf(p[0], p[1]), c = nav.nearest(i, j, 12);
    return c ? nav.center(c[0], c[1]) : p.slice();
  }
  hurt(e, dmg) {
    const R = e.rare; if (!R || !R.ward) return dmg;
    const soak = Math.min(R.ward, Math.round(dmg * 0.7));   // Shielded: the ward takes 70% of each hit until it breaks
    R.ward -= soak;
    if (R.ward <= 0) { R.wardT = 8; this.G.toast && this.G.toast(`${R.name}'s ward breaks!`, 1.6); this.ctx.effects && this.ctx.effects.spawn('impact', e.a.x, e.a.y + 1, e.a.z + 0.1); }
    return Math.max(1, dmg - soak);
  }
  tick(e, dt, frozen) {
    const R = e.rare, ctx = this.ctx, G = this.G; if (!R || frozen) return;
    R.t += dt;
    if (R.fx) { R.fx.x = e.a.x; R.fx.y = e.a.y + 0.02; R.fx.z = e.a.z; }
    if (R.traits.includes('shielded') && R.ward <= 0 && (R.wardT -= dt) <= 0) { R.ward = R.wardMax; ctx.effects && ctx.effects.spawn('rune_circle', e.a.x, e.a.y + 0.03, e.a.z); }
    if (R.traits.includes('enraged') && !R.enraged && e.hp < e.D.hp * 0.5) {
      R.enraged = true; e.D = { ...e.D, speed: e.D.speed * 1.35, cd: e.D.cd * 0.7, dmg: Math.round(e.D.dmg * 1.25), windup: e.D.windup * 0.85 };
      if (e.light) e.light.intensity = (e.light.intensity || 4) * 1.4;
      G.toast && G.toast(`${R.name} is enraged!`, 1.8); ctx.effects && ctx.effects.spawn('earth_burst', e.a.x, e.a.y, e.a.z + 0.05);
    }
    const busy = e.state === 'chase' || e.state === 'attack';
    if (!busy || G.peace) return;
    const p = ctx.player;
    if (R.traits.includes('blinking') && e.state === 'chase' && (R.blinkT -= dt) <= 0) {
      R.blinkT = 5 + Math.random() * 2;
      const ang = Math.atan2(e.a.z - p.z, e.a.x - p.x) + (Math.random() < 0.5 ? 1.3 : -1.3), d = e.D.ranged ? e.D.keep : 1.8;
      const to = this.walk([p.x + Math.cos(ang) * d, p.z + Math.sin(ang) * d]);
      ctx.effects && ctx.effects.spawn('glyph_burst', e.a.x, e.a.y, e.a.z + 0.05);
      e.a.x = to[0]; e.a.z = to[1]; e.a.y = ctx.heightAt(to[0], to[1]); e.path = null;
      ctx.effects && ctx.effects.spawn('glyph_burst', e.a.x, e.a.y, e.a.z + 0.05);
      R.blinks = (R.blinks || 0) + 1;
    }
    if (R.traits.includes('summoner') && (R.callT -= dt) <= 0) {
      R.callT = 10;
      R.minions = R.minions.filter((m) => m.state !== 'dead' && m.state !== 'gone');
      if (R.minions.length < 2 && ENEMIES[e.D.minion]) {
        const at = this.walk([e.a.x + (Math.random() - 0.5) * 3, e.a.z + 1.2]);
        const m = G.combat.spawnEnemy({ id: `${e.id}_kin${(R.called = (R.called || 0) + 1)}`, role: e.D.minion, pos: at, once: true, noLoot: true }, true);
        m.state = 'chase'; R.minions.push(m);
      }
    }
  }
  onKill(e) {
    const R = e.rare, S = this.S, G = this.G; if (!R) return;
    this.dropFx(R);
    S.hunt = S.hunt || {};
    const h = S.hunt[R.key] || (S.hunt[R.key] = { name: R.name, base: R.base, el: R.el, traits: R.traits, kills: 0, first: S.day || 0 });
    h.kills += 1; h.last = S.day || 0;
    if (R.roam) { S.rareDays = S.rareDays || {}; S.rareDays[R.roam] = true; }
    for (const m of R.minions || []) if (m.state !== 'dead' && m.state !== 'gone') G.combat.kill(m, true);
    G.toast && G.toast(`<span style="color:${ELEMENTS[R.el].col}">✦ ${R.name}</span> falls! Hunt log updated.`, 2.8, true);
    G.drawHunt && G.drawHunt();
    G.onRareKill && G.onRareKill(R);
  }
  dropFx(R) { if (R.fx) { R.fx.dur = R.fx.t + 0.3; R.fx = null; } }   // dither out over 0.3 s
  update() {
    for (const R of [...this.list]) if (R.e.state === 'gone' || R.e.state === 'dead') { this.dropFx(R); if (R.e.state === 'gone') this.list.splice(this.list.indexOf(R), 1); }
  }
  state() {
    return { area: this.area, rares: this.list.map((R) => ({ name: R.name, base: R.base, el: R.el, traits: R.traits, hp: R.e.hp, max: R.D.hp, state: R.e.state, ward: R.ward,
                                                           scale: R.D.scale, aura: !!R.fx, x: +R.e.a.x.toFixed(2), z: +R.e.a.z.toFixed(2), id: R.e.id, blinks: R.blinks || 0 })),
             hunt: this.S.hunt || {} };
  }
}
