// Hearthmoor random rifts (Stage 5 part 2). Small tears open now and then in Mossglen, the Hollows and Vanaheim (a
// toast + rumble warns you). Three tiers: I minor (a small cold-fire tear, one wave), II major (the violet-red tear,
// one bigger wave, a good chance of a rare), III abyssal (a wide crimson tear over a rune ring, two waves and always a
// two-trait rare). Walk up to it and it spits out its wave; clear everything and it seals with a reward (gold, XP, an
// item by tier, rift shards). Ignored rifts close by themselves. Harder at night (one more foe per wave).
import { RARE_AREAS, rngOf, hashStr } from './rares.js';

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
};
export const FIRST = [45, 80], EVERY = [120, 200], LIFE = 90, NEAR = 3.4;

export class Rifts {
  constructor(G) { this.G = G; this.cur = null; this.timer = 0; }
  get S() { return this.G.S; }
  attach(ctx, area) {
    this.ctx = ctx; this.area = area; this.cur = null;
    const r = rngOf(hashStr(`rift:${area}:${this.S.day || 0}:${Math.floor(Date.now() / 60000)}`));
    this.timer = FIRST[0] + r() * (FIRST[1] - FIRST[0]);
    const q = this.G.qs, t = q && q.get('riftnow');
    if (t && RIFT_AREAS[area]) setTimeout(() => this.ctx === ctx && this.open(Math.max(0, Math.min(2, (+t || 1) - 1))), 600);
  }
  detach() { this.close(false, true); this.ctx = null; }
  auto() { const G = this.G; return !(G.qa || G.peace || G.qaStill) || (G.qs && G.qs.has('rifts')); }   // QA / smoke: only on request
  // open a tier (0-2) rift at a spot (or near the player for tests)
  open(tier = 0, at = null) {
    const ctx = this.ctx, A = RIFT_AREAS[this.area]; if (!ctx || !A) return null;
    if (this.cur) this.close(false, true);
    const T = TIERS[tier], G = this.G;
    let pos = at || A.spots[Math.floor(Math.random() * A.spots.length)];
    pos = this.walk(pos);
    const y = ctx.heightAt(pos[0], pos[1]);
    const R = { tier, T, pos, y, t: 0, state: 'open', wave: 0, foes: [], rare: null, fx: [], light: null };
    if (ctx.effects) {
      R.fx.push(ctx.effects.spawn(T.fx, pos[0], y + T.y, pos[1], { duration: 1e9, fadeIn: 0.5 }));
      if (T.ring) R.fx.push(ctx.effects.spawn(T.ring, pos[0], y + 0.02, pos[1], { duration: 1e9, fadeIn: 0.5 }));
      ctx.effects.spawn('glyph_burst', pos[0], y, pos[1] + 0.05);
    }
    R.light = ctx.addGlow ? ctx.addGlow(pos[0], y + 0.8, pos[1] + 0.3, { color: T.light, intensity: 4 + tier * 1.5, range: 4 + tier, fadeIn: 0.6, lift: 0 }) : null;
    this.cur = R;
    G.audio && G.audio.sfx('portal');
    G.toast && G.toast(`${T.id === 'abyssal' ? 'An' : 'A'} ${T.name.toLowerCase()} (tier ${T.roman}) tears open nearby…`, 2.6);
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
    const A = RIFT_AREAS[this.area], T = R.T, n = T.wave + (this.night() ? 1 : 0);
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
      if (!RIFT_AREAS[this.area] || paused || !this.auto()) return;
      if ((this.timer -= dt) <= 0) {
        const night = this.night(), w = night ? [45, 38, 17] : [60, 30, 10], x = Math.random() * 100;
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
      else if (R.t > LIFE) { G.toast && G.toast('The rift flickers and closes on its own.', 2); this.close(false); }
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
    this.timer = EVERY[0] + Math.random() * (EVERY[1] - EVERY[0]);
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
    G.toast && G.toast(`${T.name} sealed! +${T.xp} XP and the rift's spoils.`, 2.8);
    G.drawHunt && G.drawHunt();
    G.factions && G.factions.onRift(R.tier);   // Rift Marks + the realm's faction
  }
  state() {
    const R = this.cur;
    return { area: this.area, timer: +this.timer.toFixed(1), rift: R ? { tier: R.tier, id: R.T.id, state: R.state, wave: R.wave, waves: R.T.waves, foes: R.foes.length,
             alive: this.alive().length, rare: R.rare ? R.rare.name : null, pos: R.pos.map((v) => +v.toFixed(2)), fx: R.fx.map((f) => f && f.name) } : null,
             closed: this.S.rifts || { minor: 0, major: 0, abyssal: 0 } };
  }
}
