// Hearthmoor glow pass (stage 2): spell light pools + glitter, glowing toadstools at night, and light zones.
// Light is a place: standing in a lamp / toadstool / spell pool makes you "glowlit" (+10% damage, faster
// stamina), and cold-fire wraiths will not drift into it or fire at a lit hero. Everything is point lights
// and palette pixels (sprites + dithered decals); no bloom.
const NIGHT = (t) => t > 0.8 || t < 0.25;          // 19:12 to 06:00, same window as the night wraith
const TOAD_COL = '#e47c8c';
// toadstool clusters per area (x, z); y comes from the heightfield
const TOADS = {
  mossglen: [[-5.5, 3.4], [5.8, -2.6], [9.0, 1.5], [-11.0, -3.0], [-4.6, -7.2], [7.0, -8.2]],
  plaza: [[-9.5, 4.6], [9.5, 5.0], [3.2, -4.4], [-11.5, -8.6]],
  lane: [[-10.2, -6.0], [9.5, 5.0], [-10.5, 5.0], [-11.8, 8.6]],
  hollows: [[-3.4, -1.6], [3.6, 3.6], [-10.8, 4.8], [-6.8, -6.6], [11.0, 3.8], [0.8, -2.3], [-6.0, 3.4], [6.8, 3.0], [-11.6, -5.0], [12.6, -8.6]],
};
// areas that glow at every hour (the hollow is always dim), and their standing light pools: [x, z, kind, colour]
const ALWAYS = { hollows: true };
const POOLS = {
  hollows: [[-1.0, 1.4, 'light', '#9a6cd4'], [5.0, 0.2, 'cold', '#5ac8ff'], [-8.2, 1.4, 'cold', '#5ac8ff'],
            [-9.4, -6.4, 'light', '#9a6cd4'], [8.6, -6.6, 'cold', '#5ac8ff'], [1.8, 5.6, 'light', '#e47c8c'],
            // warm glow under each giant toadstool cap: a dithered decal only (the cap itself is self-lit), no extra light
            [-3.4, -1.6, 'under'], [3.6, 3.6, 'under'], [-10.8, 4.8, 'under'], [-6.8, -6.6, 'under'], [11.0, 3.8, 'under']],
};
export const POOL_R = 2.2;
// lamp kinds that make a light zone at night, and how far it reaches on the ground (metres)
const LAMP_R = { lamp_post: 3.0, stone_lantern: 2.2, shrine: 2.6, portal: 2.0 };
const WINDOW_R = 1.8;                               // shop / cottage window lamps
export const LIT = { dmg: 1.1, regen: 1.5, poolLife: 1.8, poolR: 2.4, toadR: 2.0 };

export class Glow {
  constructor(G) { this.G = G; this.ctx = null; this.toads = []; this.pools = []; this.fixed = []; this.lit = false; }
  attach(ctx, area) {
    this.ctx = ctx; this.area = area; this.toads = []; this.pools = []; this.fixed = []; this.lit = false; this.night = null;
    this.poolsOn();
  }
  detach() { this.ctx = null; this.toads = []; this.pools = []; this.fixed = []; }
  // standing light pools (always on): pink/violet glow pools and neon-blue cold-fire pools with motes
  poolsOn() {
    const ctx = this.ctx, still = !!this.G.qaStill; if (!ctx) return;
    for (const [x, z, kind, color] of POOLS[this.area] || []) {
      const y = ctx.heightAt(x, z), fx = [];
      if (kind === 'under') {
        if (ctx.effects) fx.push(ctx.effects.spawn('light_pool', x, y, z + 0.03, { duration: 1e9, fadeIn: still ? 0 : 1, ...(still ? { frame: 0 } : {}) }));
        this.fixed.push({ x, z, r: 1.4, kind, fx, light: null }); continue;
      }
      if (ctx.effects) {
        const cold = kind === 'cold', fr = (f) => (still ? { frame: f } : {});
        fx.push(ctx.effects.spawn(cold ? 'coldfire_pool' : 'light_pool', x, y, z + 0.03, { duration: 1e9, fadeIn: still ? 0 : 1, ...fr(0) }));
        fx.push(ctx.effects.spawn(cold ? 'coldfire_motes' : 'glitter', x + 0.2, y + 0.1, z + 0.1, { duration: 1e9, fadeIn: still ? 0 : 1.4, ...fr(2) }));
      }
      const light = ctx.addGlow ? ctx.addGlow(x, y, z, { color, intensity: 7, range: 4.0, fadeIn: still ? 0.01 : 1.2, lift: 0.5 }) : null;
      this.fixed.push({ x, z, r: POOL_R, kind, fx, light });
    }
  }
  // a spell's light pool: dithered ground decal + twinkling glitter + a short point light in the spell's colour
  pool(x, z, color, scale = 1) {
    const ctx = this.ctx; if (!ctx) return;
    const y = ctx.heightAt(x, z), life = LIT.poolLife * scale;
    if (ctx.effects) {
      ctx.effects.spawn('light_pool', x, y, z + 0.03, { duration: life });
      for (const [ox, oz, k] of [[0, 0.05, 1], [-0.75, 0.2, 0.85], [0.75, 0.1, 0.9], [0.1, 0.65, 0.75]]) {
        ctx.effects.spawn('glitter', x + ox, ctx.heightAt(x + ox, z + oz), z + oz + 0.08, { duration: life * k });
      }
    }
    if (ctx.addGlow) ctx.addGlow(x, y, z, { color: color || '#ffb24a', intensity: 10 * scale, range: 4.6, life, fadeIn: 0.08, lift: 0.5 });
    this.pools.push({ x, z, r: LIT.poolR, t: life });
    if (this.G.hollows) this.G.hollows.spellAt(x, z);   // a spell landing by a cold-fire brazier lights it
  }
  colorOf(fxName) {
    const m = this.ctx && this.ctx.effects && this.ctx.effects.meta.effects[fxName];
    return (m && m.light && m.light.color) || '#ffb24a';
  }
  // every light zone right now: {x, z, r}
  zones() {
    const out = [], ctx = this.ctx; if (!ctx) return out;
    for (const L of ctx.lamps || []) {
      if (L.power < 0.3) continue;
      const r = LAMP_R[L.kind] ?? (L.kind === 'portal_arch' ? 0 : WINDOW_R);
      if (r > 0) out.push({ x: L.pos.x, z: L.pos.z + (LAMP_R[L.kind] ? 0 : 0.8), r, src: 'lamp' });
    }
    for (const t of this.toads) if (t.on) out.push({ x: t.x, z: t.z, r: LIT.toadR, src: 'toadstool' });
    for (const p of this.pools) out.push({ x: p.x, z: p.z, r: p.r, src: 'spell' });
    for (const p of this.fixed) out.push({ x: p.x, z: p.z, r: p.r, src: 'pool' });
    if (this.G.hollows) out.push(...this.G.hollows.zones());   // lit braziers + the spring
    if (this.G.garden) out.push(...this.G.garden.zones());     // glow-garden blooms at night
    const nm = this.G && this.G.shopUI && this.G.shopUI.nm;   // the night merchant's neon-blue lantern is a light zone too
    if (nm && nm.a) out.push({ x: nm.a.x + 0.35, z: nm.a.z + 0.1, r: 2.2, src: 'lantern' });
    return out;
  }
  zoneAt(x, z) {
    let best = null, bf = 0;
    for (const Z of this.zones()) { const f = 1 - Math.hypot(x - Z.x, z - Z.z) / Z.r; if (f > bf) { bf = f; best = Z; } }
    return best;
  }
  litAt(x, z) { return !!this.zoneAt(x, z); }
  update(dt) {
    const ctx = this.ctx; if (!ctx) return;
    for (const p of this.pools) p.t -= dt;
    this.pools = this.pools.filter((p) => p.t > 0);
    const night = !!ALWAYS[this.area] || NIGHT(ctx.clock.t);
    if (night !== this.night) { this.night = night; night ? this.toadsOn() : this.toadsOff(); }
    const lit = this.litAt(ctx.player.x, ctx.player.z);
    if (lit !== this.lit) {
      this.lit = lit;
      const el = document.getElementById('litTag'); if (el) el.hidden = !lit;
      const v = document.getElementById('vitals'); if (v) v.classList.toggle('glowlit', lit);
    }
  }
  toadsOn() {
    const ctx = this.ctx, still = !!this.G.qaStill;
    for (const [x, z] of TOADS[this.area] || []) {
      const y = ctx.heightAt(x, z);
      const fx = ctx.effects ? ctx.effects.spawn('toadstools', x, y, z + 0.02, { duration: 1e9, fadeIn: still ? 0 : 1.2, ...(still ? { frame: 0 } : {}) }) : null;
      const spores = ctx.effects ? ctx.effects.spawn('glitter', x + 0.1, y + 0.15, z + 0.05, { duration: 1e9, fadeIn: still ? 0 : 2, ...(still ? { frame: 2 } : {}) }) : null;
      const light = ctx.addGlow ? ctx.addGlow(x, y, z, { color: TOAD_COL, intensity: 6, range: 3.6, fadeIn: still ? 0.01 : 1.5, lift: 0.4 }) : null;
      this.toads.push({ x, z, fx, spores, light, on: true });
    }
  }
  toadsOff() {
    const fx = this.ctx.effects;
    for (const t of this.toads) {
      for (const f of [t.fx, t.spores]) if (f && fx) { if (f.forceFrame != null) fx.remove(f); else f.dur = f.t + 0.3; }
      if (t.light) t.light.kill = true;
    }
    this.toads = [];
  }
  // combat hooks
  dmgMul() { return (this.lit ? LIT.dmg : 1) * (this.G.hollows ? this.G.hollows.dmgMul() : 1); }      // + spring-fizz
  regenMul() { return (this.lit ? LIT.regen : 1) * (this.G.hollows ? this.G.hollows.regenMul() : 1); }
}
