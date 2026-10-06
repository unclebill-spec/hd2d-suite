// Hearthmoor random rifts (Stage 5 part 2). Small tears open now and then in Mossglen, the Hollows and Vanaheim (a
// toast + rumble warns you). Three tiers: I minor (a small cold-fire tear, one wave), II major (the violet-red tear,
// one bigger wave, a good chance of a rare), III abyssal (a wide crimson tear over a rune ring, two waves and always a
// two-trait rare). Walk up to it and it spits out its wave; clear everything and it seals with a reward (gold, XP, an
// item by tier, rift shards). Ignored rifts close by themselves. Harder at night (one more foe per wave).
import { RARE_AREAS, rngOf, hashStr } from './rares.js';
import { STORM, STORM_OPEN, stormHere } from './storms.js';

export const TIERS = [
  { id: 'minor', name: 'Minor rift', roman: 'I', fx: 'rift_tear_minor', y: 0.35, light: '#6c8cd4', wave: 3, waves: 1, rare: 0.15, gold: 15, xp: 40, minRar: 1, shard: 0.25 },
  { id: 'major', name: 'Major rift', roman: 'II', fx: 'rift_tear', y: 0.45, light: '#c03cc8', wave: 4, waves: 1, rare: 0.5, gold: 35, xp: 90, minRar: 2, shard: 0.6 },
  { id: 'abyssal', name: 'Abyssal rift', roman: 'III', fx: 'rift_tear_abyss', ring: 'rift_ring_abyss', y: 0.5, light: '#e0302a', wave: 4, waves: 2, rare: 1, rareTraits: 2,
    gold: 80, xp: 200, minRar: 3, shard: 1 },
];
export const RIFT_AREAS = {
  mossglen: { foes: ['skeleton', 'wraith', 'golem', 'skelmage'], spots: [[1.6, 1.0], [-1.2, 5.6], [5.0, 2.6], [-2.6, 2.6]] },
  hollows: { foes: ['wraith', 'skeleton'], spots: [[2.2, 5.4], [7.6, -0.8], [-6.4, -6.0]] },
  vanaheim: { foes: ['sporeling', 'mossgolem', 'sporeling'], spots: [[6.2, 0.4], [3.6, 2.8], [8.6, -2.2]] },
  // Bifrost Crossing (Stage 6 part 2): scripted only (the Stray Den's little rift behind the woodpile); never opens by itself
  // 6.5: + storm-only spots (they open by themselves only while a rift storm is over Bifrost), clear of the nine arches,
  // the Den yard (around -5.6, 3.9), the skiff landing (south) and the stair / bridge head
  bifrost: { foes: ['wraith', 'wraith', 'skeleton'], spots: [[-5.6, 3.9]], scripted: true,
             storm: { foes: ['wraith', 'skeleton', 'skelmage', 'wraith'], spots: [[-2.4, 4.4], [2.8, 4.8], [7.4, 2.6], [-1.6, -2.6], [2.4, -2.8]] } },
  // the Rift Shrine (6.5): storm only, at the dais edge
  rift: { foes: ['wraith', 'skelmage', 'wraith'], spots: [], stormOnly: true, storm: { foes: ['wraith', 'skelmage', 'wraith'], spots: [[-2.8, 2.2], [4.2, 1.6], [-0.4, 3.6]] } },
  // the Old Temple (6.3): scripted only (the tear above the court when the Rift-gate wakes; 'Keeper of the Gate')
  temple: { foes: ['wraith', 'skeleton', 'skelmage', 'wraith'], spots: [[0.0, -8.0]], scripted: true },
};
export const FIRST = [45, 80], EVERY = [120, 200], LIFE = 90, NEAR = 3.4;

export class Rifts {
  constructor(G) { this.G = G; this.cur = null; this.timer = 0; }
  get S() { return this.G.S; }
  attach(ctx, area) {
    this.ctx = ctx; this.area = area; this.cur = null; this.nextPos = null; this.warned = false;
    const r = rngOf(hashStr(`rift:${area}:${this.S.day || 0}:${Math.floor(Date.now() / 60000)}`));
    this.timer = FIRST[0] + r() * (FIRST[1] - FIRST[0]);
    if (this.storm()) this.timer = STORM.first[0] + r() * (STORM.first[1] - STORM.first[0]);
    const q = this.G.qs, t = q && q.get('riftnow');
    if (t && RIFT_AREAS[area] && !RIFT_AREAS[area].scripted && this.pool().spots.length) setTimeout(() => this.ctx === ctx && this.open(Math.max(0, Math.min(2, (+t || 1) - 1))), 600);
  }
  detach() { this.close(false, true); this.ctx = null; }
  // 6.5 rift storms: is one raging here, and this area's pool (storm spots / foes while it does)
  storm() { return stormHere(this.S, this.area); }
  pool() { const A = RIFT_AREAS[this.area]; return A && this.storm() && A.storm ? A.storm : A; }
  canAuto() { const A = RIFT_AREAS[this.area]; if (!A) return false; return this.storm() ? !!(A.storm || (!A.scripted && !A.stormOnly)) : !A.scripted && !A.stormOnly; }
  stormKick() { if (!this.cur) this.timer = Math.min(this.timer, STORM.first[0] + Math.random() * (STORM.first[1] - STORM.first[0])); }
  auto() { const G = this.G; return !(G.qa || G.peace || G.qaStill) || (G.qs && G.qs.has('rifts')); }   // QA / smoke: only on request
  // open a tier (0-2) rift at a spot (or near the player for tests)
  // opts.tag: a scripted rift (the Stray Den's 'den': no rare, never closes by itself, sets S.flags.den_rift when sealed)
  open(tier = 0, at = null, opts = {}) {
    const ctx = this.ctx, A = opts.tag ? RIFT_AREAS[this.area] : this.pool(); if (!ctx || !A) return null;
    if (this.cur) this.close(false, true);
    const T = TIERS[tier], G = this.G;
    let pos = at || this.nextPos || A.spots[Math.floor(Math.random() * A.spots.length)];
    this.nextPos = null; this.warned = false;
    pos = this.walk(pos);
    const y = ctx.heightAt(pos[0], pos[1]);
    const R = { tier, T, pos, y, t: 0, state: 'open', wave: 0, foes: [], rare: null, fx: [], light: null, tag: opts.tag || null, storm: !opts.tag && this.storm(), foePool: A.foes };
    if (R.tag || !RARE_AREAS[this.area]) R.forceRare = false;   // scripted tears and rare-less areas spit out no rare
    if (ctx.effects) {
      R.fx.push(ctx.effects.spawn(T.fx, pos[0], y + T.y, pos[1], { duration: 1e9, fadeIn: 0.5 }));
      if (T.ring) R.fx.push(ctx.effects.spawn(T.ring, pos[0], y + 0.02, pos[1], { duration: 1e9, fadeIn: 0.5 }));
      ctx.effects.spawn('glyph_burst', pos[0], y, pos[1] + 0.05);
    }
    R.light = ctx.addGlow ? ctx.addGlow(pos[0], y + 0.8, pos[1] + 0.3, { color: T.light, intensity: 4 + tier * 1.5, range: 4 + tier, fadeIn: 0.6, lift: 0 }) : null;
    this.cur = R;
    G.audio && G.audio.sfx('portal');
    if (R.storm) G.toast && G.toast(T.id === 'abyssal' ? 'The storm rips an abyssal rift open. The ground hums under your boots.' : STORM_OPEN[Math.floor(Math.random() * STORM_OPEN.length)], 2.6);
    else G.toast && G.toast(`${T.id === 'abyssal' ? 'An' : 'A'} ${T.name.toLowerCase()} (tier ${T.roman}) tears open nearby…`, 2.6);
    return R;
  }
  walk(p) {
    const nav = this.ctx.nav; if (!nav) return p.slice();
    const [i, j] = nav.cellOf(p[0], p[1]), c = nav.nearest(i, j, 12);
    return c ? nav.center(c[0], c[1]) : p.slice();
  }
  night() { const ct = this.ctx.clock.t; return ct > 0.8 || ct < 0.25; }
  // the hero came close: the rift spits out its next wave (and maybe a rare)
  engage() {
    const R = this.cur, G = this.G, ctx = this.ctx; if (!R || (R.state === 'fight' && this.alive().length) || R.wave >= R.T.waves) return false;   // one wave at a time
    const A = { foes: R.foePool || RIFT_AREAS[this.area].foes }, T = R.T, n = T.wave + (this.night() ? 1 : 0);
    R.state = 'fight'; R.wave += 1;
    for (let k = 0; k < n; k++) {
      const ang = (k / n) * Math.PI * 2 + R.wave, at = this.walk([R.pos[0] + Math.cos(ang) * 1.6, R.pos[1] + Math.sin(ang) * 1.2 + 0.6]);
      const e = G.combat.spawnEnemy({ id: `rift_${R.wave}_${k}_${Math.floor(R.t * 100)}`, role: A.foes[k % A.foes.length], pos: at, once: true }, true);
      if (!G.peace) e.state = 'chase';
      R.foes.push(e);
    }
    const rr = R.wave === 1 && G.rares && (R.forceRare ?? Math.random() < T.rare);
    if (rr) {
      const RA = RARE_AREAS[this.area];
      R.rare = G.rares.spawn({ base: RA.bases[Math.floor(Math.random() * RA.bases.length)], nTraits: T.rareTraits || 1, pos: [R.pos[0], R.pos[1] + 1.4], rift: T.id, seed: hashStr(`riftrare:${Date.now()}`) });
      if (R.rare && !G.peace) R.rare.e.state = 'chase';
    }
    ctx.effects && ctx.effects.spawn('glyph_burst', R.pos[0], R.y, R.pos[1] + 0.05);
    G.toast && G.toast(R.wave === 1 ? `The ${T.name.toLowerCase()} spits out ${n} foes${R.rare ? ' and something bigger' : ''}!` : `Wave ${R.wave} pours out of the rift!`, 2.2);
    return true;
  }
  alive() { const R = this.cur; return R ? R.foes.concat(R.rare ? [R.rare.e] : []).filter((e) => e.state !== 'dead' && e.state !== 'gone') : []; }
  update(dt) {
    const R = this.cur, ctx = this.ctx, G = this.G; if (!ctx) return;
    const paused = G.title || G.busy || G.dlg || G.log || G.downed || G.picking || (G.intro && G.intro.active);
    if (!R) {
      if (!this.canAuto() || paused || !this.auto()) return;
      this.timer -= dt;
      // the lantern-fox's Rift-sense: its tail flares riftWarn seconds early, pointing at where the tear will open
      const warn = G.pets ? G.pets.riftWarn() : 0;
      if (warn && !this.warned && this.timer <= warn) {
        const A = this.pool(); this.nextPos = A.spots[Math.floor(Math.random() * A.spots.length)]; this.warned = true;
        G.pets.senseRift(this.nextPos);
      }
      if (this.timer <= 0) {
        const night = this.night(), w = this.storm() ? STORM.weights : night ? [45, 38, 17] : [60, 30, 10], x = Math.random() * 100;
        this.open(x < w[0] ? 0 : x < w[0] + w[1] ? 1 : 2);
      }
      return;
    }
    if (paused) return;
    R.t += dt;
    if (R.light) R.light.scale = 0.85 + Math.sin(R.t * 9) * 0.1 + (Math.random() < 0.05 ? -0.3 : 0);   // a cold flicker
    const p = ctx.player, d = Math.hypot(p.x - R.pos[0], p.z - R.pos[1]);
    if (R.state === 'open') {
      if (d < NEAR) this.engage();
      else if (R.t > LIFE && !R.tag) { G.toast && G.toast('The rift flickers and closes on its own.', 2); this.close(false); }
    } else if (R.state === 'fight' && !this.alive().length) {
      if (R.wave < R.T.waves) this.engage();
      else this.close(true);
    }
  }
  // seal the rift (won = the reward); quiet = no toast / effects (area change)
  close(won, quiet = false) {
    const R = this.cur, ctx = this.ctx, G = this.G; if (!R) return;
    this.cur = null;
    for (const f of R.fx) if (f) f.dur = f.t + 0.3;
    if (R.light) R.light.kill = true;
    if (quiet || !ctx) return;
    ctx.effects && ctx.effects.spawn('glyph_burst', R.pos[0], R.y, R.pos[1] + 0.05);
    ctx.effects && ctx.effects.spawn('light_pool', R.pos[0], R.y + 0.02, R.pos[1]);
    this.timer = this.storm() ? STORM.every[0] + Math.random() * (STORM.every[1] - STORM.every[0]) : EVERY[0] + Math.random() * (EVERY[1] - EVERY[0]);
    if (!won) return;
    const T = R.T, S = this.S;
    S.rifts = S.rifts || { minor: 0, major: 0, abyssal: 0 };
    S.rifts[T.id] = (S.rifts[T.id] || 0) + 1;
    if (G.loot) {
      G.loot.drop(R.pos[0] + 0.4, R.pos[1] + 0.3, { gold: Math.round((T.gold + Math.floor(Math.random() * 10)) * (G.factions ? G.factions.riftGoldMul() : 1)) });   // Guild Friend: +25%
      G.loot.dropItem && G.loot.dropItem(R.pos[0] - 0.4, R.pos[1] + 0.35, S.lv || 1, T.minRar);
      if (Math.random() < T.shard) G.loot.drop(R.pos[0], R.pos[1] - 0.4, { gem: 'rift_shard' });
    }
    G.gainXP && G.gainXP(T.xp, { x: R.pos[0], y: R.y, z: R.pos[1] });
    G.audio && G.audio.sfx('quest');
    if (R.storm && G.storms) G.storms.onSeal(T);   // the storm count, its toasts, Storm Watch 1 -> 2
    else G.toast && G.toast(`${T.name} sealed! +${T.xp} XP and the rift's spoils.`, 2.8);
    G.drawHunt && G.drawHunt();
    G.factions && G.factions.onRift(R.tier, R.storm);   // Rift Marks + the realm's faction
    if (R.tag === 'temple' && G.temple) G.temple.afterRift();   // tm_rift + the toast + Veyra's cameo
    if (R.tag === 'den') {   // 'Strays of the Rift': the little rift behind the woodpile is sealed
      S.flags = S.flags || {}; S.flags.den_rift = 1;
      G.toast && G.toast('The little rift seals. A fox kit peeks out, then thinks better of it.', 3);
      G.refreshMarkers && G.refreshMarkers(); G.drawLog && G.drawLog(); G.save && G.save();
    }
  }
  // QA / smoke: jump the random timer (the fox warning fires on the next frame when t <= riftWarn)
  setTimer(t) { this.timer = t; this.warned = false; this.nextPos = null; }
  state() {
    const R = this.cur;
    return { area: this.area, storm: this.storm(), timer: +this.timer.toFixed(1), nextPos: this.nextPos, warned: this.warned, rift: R ? { tag: R.tag, tier: R.tier, id: R.T.id, state: R.state, wave: R.wave, waves: R.T.waves, foes: R.foes.length,
             alive: this.alive().length, rare: R.rare ? R.rare.name : null, inStorm: !!R.storm, pos: R.pos.map((v) => +v.toFixed(2)), fx: R.fx.map((f) => f && f.name) } : null,
             closed: this.S.rifts || { minor: 0, major: 0, abyssal: 0 } };
  }
}
