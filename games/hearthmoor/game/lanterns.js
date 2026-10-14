// Hearthmoor 6.6: glow-fish orb lanterns. Buy glow-fish (Odo, Ida) or catch them at night where they swim (the Hollows
// spring, Ravenhold's pier ends; one catch per spot per in-game day). An orb lantern = an empty orb (`orblamp`) + a
// glow-fish, set on a fixed spot at home (the Plaza cottage, by Pudding's corner) or in the Lane garden. Each spot has
// its fish colour (blue / violet / red, from the art pack). At night a placed orb casts a pool of radiance: pool decal +
// a point light in its colour, and a light zone (glowlit, wraiths keep out). The orb billboard shows at every hour.
// Art: art/orb_lanterns (orb_fx_32: orb_large_* / orb_grand_mix appended to the area spells atlas by build.py).
export const ORB = {
  blue:   { fx: 'orb_large_blue', pool: 'coldfire_pool', color: '#2ab4ff' },
  violet: { fx: 'orb_large_violet', pool: 'violet_pool', color: '#a45cf0' },
  red:    { fx: 'orb_large_red', pool: 'red_pool', color: '#e0302a' },
  grand:  { fx: 'orb_grand_mix', pool: 'violet_pool', color: '#7a8cff' },
};
// placement spots per area: [id, x, z, colour, where]
export const SPOTS = {
// (the kit stands orb_post_* sit at the same spots in areas/src; lift = the kit orb centre, so the billboard covers it)
  plaza: [['home_blue', 3.9, 2.8, 'blue', 'home', 1.53], ['home_violet', 5.7, 2.8, 'violet', 'home', 1.53]],
  lane: [['garden_red', 2.0, 4.0, 'red', 'garden', 1.34], ['garden_grand', 5.2, 4.0, 'grand', 'garden', 1.37]],
};
// where glow-fish can be caught at night: [id, x, z]
export const FISH = { hollows: [['fish_spring', 10.0, -6.2]], ravenhold: [['fish_pier_w', -6.0, 7.9], ['fish_pier_e', 6.0, 7.9]] };
const NIGHT = (t) => t > 0.8 || t < 0.25;
const REACH = 1.6, ZONE_R = 2.6;
export class Lanterns {
  constructor(G) { this.G = G; this.ctx = null; this.spots = []; this.fish = []; }
  attach(ctx, area) {
    this.detach(); this.ctx = ctx; const S = this.G.S; S.orbs = S.orbs || {}; S.fishDay = S.fishDay || {};
    this.spots = (SPOTS[area] || []).map(([id, x, z, col, where, lift]) => ({ id, x, z, col, where, lift, orb: null, pool: null, light: null, lit: false }));
    this.fish = (FISH[area] || []).map(([id, x, z]) => ({ id, x, z }));
    for (const p of this.spots) this.show(p);
  }
  detach() { for (const p of this.spots) this.clear(p); this.spots = []; this.fish = []; this.ctx = null; }
  clear(p) {
    if (p.orb) p.orb.dur = p.orb.t + 0.3; if (p.pool) p.pool.dur = p.pool.t + 0.5; if (p.light) p.light.kill = true;
    p.orb = p.pool = p.light = null; p.lit = false;
  }
  show(p) {
    const ctx = this.ctx; if (!ctx || !ctx.effects) return;
    const on = !!this.orbs()[p.id], still = !!this.G.qaStill, O = ORB[p.col], y = ctx.heightAt(p.x, p.z);
    if (!on) { if (p.orb || p.lit) this.clear(p); return; }
    if (!p.orb) p.orb = ctx.effects.spawn(O.fx, p.x, y + p.lift, p.z + 0.12, { duration: 1e9, fadeIn: still ? 0 : 0.6 });
    const want = NIGHT(ctx.clock.t);
    if (want && !p.lit) {
      p.pool = ctx.effects.spawn(O.pool, p.x, y, p.z + 0.04, { duration: 1e9, fadeIn: still ? 0 : 1.0 });
      p.light = ctx.addGlow ? ctx.addGlow(p.x, y, p.z, { color: O.color, intensity: 6, range: 4.5, lift: p.lift, fadeIn: still ? 0.01 : 1.0 }) : null;
      p.lit = true;
    } else if (!want && p.lit) {
      if (p.pool) p.pool.dur = p.pool.t + 0.6; if (p.light) p.light.kill = true; p.pool = p.light = null; p.lit = false;
    }
  }
  orbs() { const S = this.G.S; return S.orbs || (S.orbs = {}); }   // the save object can be swapped (slots, Continue)
  update() { for (const p of this.spots) this.show(p); }
  near(list, ctx = this.ctx) {
    if (!ctx) return null; const pl = ctx.player; let best = null, bd = REACH;
    for (const p of list) { const d = Math.hypot(pl.x - p.x, pl.z - p.z); if (d < bd) { bd = d; best = p; } }
    return best;
  }
  nearThing(ctx) { return !!(this.near(this.spots, ctx) || this.near(this.fish, ctx)); }
  interact() {
    const G = this.G, S = G.S, ctx = this.ctx, inv = S.inv; S.orbs = this.orbs(); S.fishDay = S.fishDay || {};
    const f = this.near(this.fish);
    if (f) {
      if (!NIGHT(ctx.clock.t)) { G.toast && G.toast('Dark water. The glow-fish only rise after dusk.', 2.2); return true; }
      if (S.fishDay[f.id] === (S.day || 0)) { G.toast && G.toast('The glow-fish here have scattered. Try again tomorrow night.', 2.2); return true; }
      S.fishDay[f.id] = S.day || 0; G.give('glowfish', 1); G.audio && G.audio.sfx('pickup');
      ctx.effects && ctx.effects.spawn('sparkle_burst', f.x, ctx.heightAt(f.x, f.z), f.z + 0.1);
      G.save && G.save(); return true;
    }
    const p = this.near(this.spots); if (!p) return false;
    if (S.orbs[p.id]) {
      delete S.orbs[p.id]; G.give('orblamp', 1); G.give('glowfish', 1); this.clear(p);
    } else if (!(inv.orblamp > 0) || !(inv.glowfish > 0)) {
      G.toast && G.toast(`A spot for an orb lantern (${p.where}). You need an empty orb and a glow-fish: Odo sells both.`, 2.6); return true;
    } else {
      G.take('orblamp', 1); G.take('glowfish', 1); S.orbs[p.id] = { day: S.day || 0 };
      G.toast && G.toast(`The glow-fish settles into the orb. It will light a ${p.col === 'grand' ? 'rainbow' : p.col} pool at night.`, 2.6);
      G.audio && G.audio.sfx('quest');
    }
    this.show(p); G.save && G.save(); return true;
  }
  zones() { return this.spots.filter((p) => p.lit).map((p) => ({ x: p.x, z: p.z, r: ZONE_R, src: 'orb' })); }
  qa() { return { spots: this.spots.map((p) => ({ id: p.id, col: p.col, on: !!this.orbs()[p.id], lit: p.lit, orb: !!p.orb, x: p.x, z: p.z })), fish: this.fish.map((f) => ({ id: f.id, x: f.x, z: f.z })) }; }
}
