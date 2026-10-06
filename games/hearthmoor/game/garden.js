// Hearthmoor glow-gardening (Stage 4 part 3). Garden plots (area game.gardens: [{id, pos: [x, z], kinds: [...]}])
// hold three glow seeds each (Odo sells them). A planted seed sprouts after one in-game day and blooms after two
// (S.day counts whole days as the clock wraps). Blooms glow by palette pixels only; at night each one casts a light
// pool (decal + a point light in its colour) and is a light zone. E / A / tap beside a bloom harvests it.
export const PLANTS = {
  coldfire: { name: 'cold-fire bloom', fx: 'glowplant_coldfire', pool: 'coldfire_pool', color: '#5ab4f0', gives: { gem: 'frost_core' } },
  violet:   { name: 'violet glowbell', fx: 'glowplant_violet', pool: 'violet_pool', color: '#a45cf0', gives: { gem: 'moon_opal' } },
  toadcap:  { name: 'red glow toadstool', fx: 'glowplant_toadcap', pool: 'red_pool', color: '#ff4a3a', gives: { item: 'tonic', n: 2 } },
};
export const GROW = { sprout: 1, bloom: 2 };           // in-game days after planting
const NIGHT = (t) => t > 0.8 || t < 0.25;
const SPACING = 0.85, REACH = 1.3, ZONE_R = 2.2;
export class Garden {
  constructor(G) { this.G = G; this.ctx = null; this.plots = []; }
  attach(ctx) {
    this.detach();
    const gm = ctx.scene.game || {}, S = this.G.S; S.garden = S.garden || {}; S.day = S.day || 0;
    this.ctx = ctx;
    this.plots = (gm.gardens || []).flatMap((g) => (g.kinds || ['coldfire', 'violet', 'toadcap']).map((kind, k, all) => ({
      id: `${g.id}_${k}`, kind, x: g.pos[0] + (k - (all.length - 1) / 2) * SPACING, z: g.pos[1], fx: null, pool: null, light: null, shown: -1, lit: false })));
    for (const g of gm.gardens || []) if (ctx.effects) ctx.effects.spawn('garden_plot', g.pos[0], ctx.heightAt(g.pos[0], g.pos[1]), g.pos[1] - 0.05, { duration: 1e9 });
    this.lastT = ctx.clock.t;
    for (const p of this.plots) this.show(p);
  }
  detach() { for (const p of this.plots) this.clear(p, true); this.plots = []; this.ctx = null; }
  stage(p) {
    const s = this.G.S.garden[p.id]; if (!s) return 0;
    const age = (this.G.S.day || 0) - s.day + ((this.ctx ? this.ctx.clock.t : 0) < s.t ? -1 : 0);   // whole days since planting
    return age >= GROW.bloom ? 3 : age >= GROW.sprout ? 2 : 1;            // 1 seed mound, 2 sprout, 3 bloom
  }
  clear(p, all) {
    if (p.fx) p.fx.dur = p.fx.t + 0.3; p.fx = null;
    if (all || p.pool) { if (p.pool) p.pool.dur = p.pool.t + 0.4; p.pool = null; if (p.light) p.light.kill = true; p.light = null; p.lit = false; }
    p.shown = -1;
  }
  show(p) {
    const ctx = this.ctx; if (!ctx || !ctx.effects) return;
    const st = this.stage(p), still = !!this.G.qaStill;
    if (st !== p.shown) {
      if (p.fx) p.fx.dur = p.fx.t + 0.3; p.fx = null;
      const y = ctx.heightAt(p.x, p.z);
      const name = st === 1 ? 'glowplant_seed' : st === 2 ? 'glowplant_sprout' : st === 3 ? PLANTS[p.kind].fx : null;
      if (name) p.fx = ctx.effects.spawn(name, p.x, y, p.z + 0.02, { duration: 1e9, fadeIn: still ? 0 : 0.5 });
      p.shown = st;
    }
    const want = st === 3 && NIGHT(ctx.clock.t);
    if (want && !p.lit) {
      const P = PLANTS[p.kind], y = ctx.heightAt(p.x, p.z);
      p.pool = ctx.effects.spawn(P.pool, p.x, y, p.z + 0.04, { duration: 1e9, fadeIn: still ? 0 : 1.0 });
      p.light = ctx.addGlow ? ctx.addGlow(p.x, y, p.z, { color: P.color, intensity: 5, range: 3.4, lift: 0.5, fadeIn: still ? 0.01 : 1.0 }) : null;
      p.lit = true;
    } else if (!want && p.lit) {
      if (p.pool) p.pool.dur = p.pool.t + 0.6; p.pool = null; if (p.light) p.light.kill = true; p.light = null; p.lit = false;
    }
  }
  // the day counter: the clock wraps from ~1 back to ~0 at midnight
  update() {
    const ctx = this.ctx; if (!ctx) return;
    const t = ctx.clock.t, S = this.G.S;
    if (t + 0.5 < this.lastT) S.day = (S.day || 0) + 1;
    this.lastT = t;
    for (const p of this.plots) this.show(p);
  }
  near(ctx = this.ctx) {
    if (!ctx) return null; const pl = ctx.player; let best = null, bd = REACH;
    for (const p of this.plots) { const d = Math.hypot(pl.x - p.x, pl.z - p.z); if (d < bd) { bd = d; best = p; } }
    return best;
  }
  nearThing(ctx) { return !!this.near(ctx); }
  interact() {
    const G = this.G, S = G.S, p = this.near(); if (!p) return false;
    const st = this.stage(p), P = PLANTS[p.kind];
    if (st === 0) {
      if (!(S.inv.glowseed > 0)) { G.toast && G.toast('An empty garden plot. Odo sells glow seeds.', 2.2); return true; }
      G.take('glowseed', 1); S.garden[p.id] = { day: S.day || 0, t: this.ctx.clock.t };
      G.toast && G.toast(`Planted a glow seed. It will grow into a ${P.name} in ${GROW.bloom} days.`, 2.6); G.audio && G.audio.sfx('pickup');
    } else if (st < 3) {
      G.toast && G.toast(st === 1 ? 'A seed mound, humming faintly. Give it a day.' : `A glowing sprout. It blooms in about a day.`, 2.0);
      return true;
    } else {
      delete S.garden[p.id];
      if (P.gives.gem) { S.gems = S.gems || {}; S.gems[P.gives.gem] = (S.gems[P.gives.gem] || 0) + 1; G.toast && G.toast(`Harvested the ${P.name}: +1 ${P.gives.gem.replace('_', ' ')}`, 2.4); }
      else { G.give(P.gives.item, P.gives.n + (G.forage ? G.forage() : 0)); }
      if (this.ctx.effects) this.ctx.effects.spawn('sparkle_burst', p.x, this.ctx.heightAt(p.x, p.z), p.z + 0.1);
      G.audio && G.audio.sfx('quest');
      this.clear(p, true);
    }
    this.show(p); G.save && G.save();
    return true;
  }
  zones() { return this.plots.filter((p) => p.lit).map((p) => ({ x: p.x, z: p.z, r: ZONE_R, src: 'garden' })); }
  qa() { return this.plots.map((p) => ({ id: p.id, kind: p.kind, stage: this.stage(p), lit: p.lit, x: p.x, z: p.z })); }
}
