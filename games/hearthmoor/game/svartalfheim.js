// [SVARTALFHEIM] Svartalfheim (realm-svartalfheim branch), built from the Hearthmoor Story script (staging story/svartalfheim.md)
// with Cozy Builder's decisions (section 14). Chunk 1 = the first area only: Anvildeep, Copper Row (`svartalfheim`).
// The realm's game module (quests, TALK, shops, gate at Bifrost, alliance lock, Dagna / Tick) comes in later chunks and merges into the
// shared tables from here, like alfheim.js, so shared files only carry a few marked hook lines.
export const AREAS_SV = { svartalfheim: 'areas/svartalfheim/', forge_hall: 'areas/forge_hall/', glowmines: 'areas/glowmines/', clockdeep: 'areas/clockdeep/' };
export const AREA_NAMES_SV = { svartalfheim: 'Anvildeep: Copper Row', forge_hall: 'The Great Forge', glowmines: 'The Amethyst Mines', clockdeep: 'The Clockwork Deep' };

// Ground light pools and glow lights placed from an area spec's `game.svfx` ([{ name, pos: [x, y, z], light? }]): svart_fx decals (pool_red /
// pool_blue / pool_violet / water_glow) with a matching point light at night, like forge.js does for the Forge Quarter. Data only; a later chunk
// adds the realm's quests / TALK / shops / gate on this class.
const SV_AREAS = Object.keys(AREAS_SV);
const SV_LIGHT = { pool_red: ['#ff5a4a', 7, 5.0], pool_blue: ['#2ab4ff', 5, 3.6], pool_violet: ['#a45cf0', 5, 4.0], water_glow: ['#3ac8b0', 4, 3.2] };
export class Svartalfheim {
  constructor(G) { this.G = G; this.ctx = null; this.area = null; this.fx = []; this.lights = []; }
  attach(ctx, area) {
    this.detach(); this.ctx = ctx; this.area = area;
    if (!SV_AREAS.includes(area)) return;
    const still = !!this.G.qaStill;
    for (const f of (ctx.scene.game || {}).svfx || []) {
      const [x, , z] = f.pos, y = ctx.heightAt(x, z);
      if (ctx.gamefx && ctx.gamefx.meta.effects[f.name]) this.fx.push(ctx.gamefx.spawn(f.name, x, y, z, { duration: Infinity, fadeIn: still ? 0 : 0.6 }));
      const L = SV_LIGHT[f.name];
      if (ctx.addGlow && L && f.light !== false) this.lights.push(ctx.addGlow(x, y, z, { color: L[0], intensity: L[1], range: L[2], lift: 0.6, fadeIn: still ? 0.01 : 0.8 }));
    }
  }
  detach() { for (const f of this.fx) if (f) f.dur = f.t + 0.2; for (const l of this.lights) if (l) l.kill = true; this.fx = []; this.lights = []; this.ctx = null; this.area = null; }
  update() {}
}
