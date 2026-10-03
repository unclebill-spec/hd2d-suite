// Toadstool Hollows (Part 5): bounce toadstools. Jump (Z / LS / A with nobody near) while standing on a bounce cap
// and you spring along a high arc to its landing spot (a hidden ledge, or back down). Data lives in the area's
// game.bounces: [{pos: [x, z], to: [x, z], h: arc height (m), dur: s, secret?: 'toast on first landing'}].
export class Hollows {
  constructor(G) { this.G = G; this.ctx = null; this.b = null; this.list = []; this.count = 0; }
  attach(ctx) { this.ctx = ctx; this.b = null; this.list = (ctx.scene.game && ctx.scene.game.bounces) || []; }
  detach() { this.ctx = null; this.b = null; this.list = []; }
  near(x, z, r = 0.85) { return this.list.find((q) => Math.hypot(x - q.pos[0], z - q.pos[1]) < r) || null; }
  busy() { return !!this.b; }
  onJump() {
    const ctx = this.ctx; if (!ctx || this.b) return false;
    const p = ctx.player, q = this.near(p.x, p.z); if (!q) return false;
    ctx.stopWalk();
    this.b = { q, t: 0, dur: q.dur || 1.1, x0: p.x, z0: p.z, y0: p.y, y1: ctx.heightAt(q.to[0], q.to[1]) };
    if (Math.abs(q.to[0] - p.x) > Math.abs(q.to[1] - p.z)) p.facing = q.to[0] > p.x ? 'right' : 'left';
    else p.facing = q.to[1] > p.z ? 'down' : 'up';
    if (ctx.effects) ctx.effects.spawn('glitter', q.pos[0], ctx.heightAt(q.pos[0], q.pos[1]) + 0.3, q.pos[1] + 0.05, { duration: 0.9 });
    if (ctx.addGlow) ctx.addGlow(q.pos[0], ctx.heightAt(q.pos[0], q.pos[1]), q.pos[1], { color: '#e47c8c', intensity: 8, range: 3.2, life: 0.6, fadeIn: 0.05, lift: 0.4 });
    this.G.audio && this.G.audio.sfx('dodge');
    this.count++;
    return true;
  }
  update(dt) {
    const b = this.b, ctx = this.ctx; if (!b || !ctx) return;
    b.t += dt;
    const k = Math.min(1, b.t / b.dur), p = ctx.player, q = b.q;
    p.x = b.x0 + (q.to[0] - b.x0) * k; p.z = b.z0 + (q.to[1] - b.z0) * k;
    p.y = b.y0 + (b.y1 - b.y0) * Math.min(1, k * 1.6);          // the shadow climbs the bank early, the hero arcs over it
    p.lift = Math.max(0, (q.h || 3) * 4 * k * (1 - k) + (b.y0 + (b.y1 - b.y0) * k) - p.y);
    if (k >= 1) {
      p.x = q.to[0]; p.z = q.to[1]; p.y = b.y1; p.lift = 0; this.b = null;
      if (ctx.effects) ctx.effects.spawn('glitter', p.x, p.y + 0.1, p.z + 0.05, { duration: 0.7 });
      const S = this.G.S; S.found = S.found || {};
      if (q.secret && !S.found[q.id || 'bounce']) { S.found[q.id || 'bounce'] = 1; this.G.toast && this.G.toast(q.secret, 2.6); this.G.audio && this.G.audio.sfx('quest'); }
    }
  }
}
