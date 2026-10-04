// Toadstool Hollows (Part 5): bounce toadstools. Jump (Z / LS / A with nobody near) while standing on a bounce cap
// and you spring along a high arc to its landing spot (a hidden ledge, or back down). Data lives in the area's
// game.bounces: [{pos: [x, z], to: [x, z], h: arc height (m), dur: s, secret?: 'toast on first landing'}].
// Also: gnome doors (game.doors, E / A opens: a peeking gnome or a little chest), the hidden bubbly spring on the
// ledge (game.spring: heals fully + a timed "spring-fizz" buff), and dark-hour cold-fire braziers (game.braziers:
// a spell landing near one lights it; lit braziers burn through the dark hours as light zones wraiths avoid).
const DARK = (t) => t > 0.75 || t < 0.25;              // dusk-into-night to dawn
export const SPRING = { buff: 60, dmg: 1.15, regen: 1.5, cd: 8 };
export const BRAZIER = { reach: 2.6, r: 3.2, flare: 25, color: '#5ac8ff' };
export class Hollows {
  constructor(G) { this.G = G; this.ctx = null; this.b = null; this.list = []; this.count = 0; this.buffT = 0; this.doors = []; this.braziers = []; this.spring = null; }
  attach(ctx) {
    const gm = ctx.scene.game || {}, S = this.G.S; S.found = S.found || {};
    this.ctx = ctx; this.b = null; this.list = gm.bounces || []; this.doors = gm.doors || []; this.springCd = 0;
    this.braziers = (gm.braziers || []).map((q) => ({ ...q, lit: !!S.found[q.id], flare: 0, burning: false, fx: [], light: null }));
    this.spring = gm.spring ? { ...gm.spring, fx: [], light: null } : null;
    if (this.spring) this.springOn();
  }
  detach() { this.ctx = null; this.b = null; this.list = []; this.doors = []; this.braziers = []; this.spring = null; }
  // ---------------------------------------------------------------- the bubbly spring
  springOn() {
    const ctx = this.ctx, q = this.spring, still = !!this.G.qaStill, [x, z] = q.pos, y = ctx.heightAt(x, z);
    if (ctx.effects) {
      for (const [ox, oz, f] of [[0, 0.1, 0], [-0.6, -0.2, 3], [0.55, 0.3, 6], [0.1, -0.55, 8]]) {
        q.fx.push(ctx.effects.spawn('spring_bubbles', x + ox, y + 0.1, z + oz + 0.1, { duration: 1e9, fadeIn: still ? 0 : 1, ...(still ? { frame: f } : {}) }));
      }
      q.fx.push(ctx.effects.spawn('glitter', x, y + 0.1, z + 0.3, { duration: 1e9, ...(still ? { frame: 1 } : {}) }));
    }
    q.light = ctx.addGlow ? ctx.addGlow(x, y, z, { color: '#94c0dc', intensity: 7, range: 4.2, fadeIn: still ? 0.01 : 1.2, lift: 0.6 }) : null;
  }
  drink() {
    const G = this.G, C = G.combat, S = G.S, ctx = this.ctx;
    S.hp = C.maxHp(); C.st = C.maxSt(); this.buffT = SPRING.buff; this.springCd = SPRING.cd;
    S.found.spring = 1;
    if (ctx.effects) ctx.effects.spawn('healing_petals', ctx.player.x, ctx.player.y, ctx.player.z + 0.05);
    G.toast && G.toast(`The spring fizzes through you: healed, and spring-fizz for ${SPRING.buff} s (+15% damage, faster stamina)`, 3.2);
    G.audio && G.audio.sfx('quest');
  }
  buffOn() { return this.buffT > 0; }
  dmgMul() { return this.buffT > 0 ? SPRING.dmg : 1; }
  regenMul() { return this.buffT > 0 ? SPRING.regen : 1; }
  // ---------------------------------------------------------------- gnome doors
  doorNear(x, z, r = 1.15) { return this.doors.find((d) => Math.hypot(x - d.pos[0], z - d.pos[1]) < r) || null; }
  interact() {
    const ctx = this.ctx; if (!ctx || this.b) return false;
    const d = this.doorNear(ctx.player.x, ctx.player.z); if (!d) return false;
    const G = this.G, S = G.S, key = d.id;
    if (d.kind === 'chest') {
      if (S.found[key]) { G.toast && G.toast('The little chest is empty (thank you kindly, says a tiny note).', 2.2); return true; }
      S.found[key] = 1; S.gold = (S.gold || 0) + (d.gold || 0);
      if (d.item) G.give(d.item, 1);
      if (ctx.effects) ctx.effects.spawn('glitter', d.pos[0], ctx.heightAt(d.pos[0], d.pos[1]) + 0.1, d.pos[1] + 0.1, { duration: 1.2 });
      G.toast && G.toast(`The gnome door creaks open: a little chest! +${d.gold || 0} gold${d.item ? ' and a ' + (G.itemName ? G.itemName(d.item) : d.item) : ''}`, 2.8);
      G.audio && G.audio.sfx('pickup');
      return true;
    }
    S.found[key] = (S.found[key] || 0) + 1;
    const g = ctx.npc && ctx.npc('gnome');
    const pages = d.say || ['(The door opens a crack. A gnome peeks out.)'];
    if (G.say && g) G.say({ ...g, name: d.name || 'A gnome behind the door' }, pages[(S.found[key] - 1) % pages.length]);
    return true;
  }
  // ---------------------------------------------------------------- dark-hour braziers
  spellAt(x, z) {
    const ctx = this.ctx; if (!ctx) return;
    for (const q of this.braziers) {
      if (Math.hypot(x - q.pos[0], z - q.pos[1]) > BRAZIER.reach) continue;
      q.flare = BRAZIER.flare;
      if (!q.lit) {
        q.lit = true; this.G.S.found[q.id] = 1;
        this.G.toast && this.G.toast('The cold-fire brazier catches! It will burn through the dark hours.', 2.6);
        this.G.audio && this.G.audio.sfx('spell');
      }
    }
  }
  onCast() { const p = this.ctx && this.ctx.player; if (p) this.spellAt(p.x, p.z); }   // casting beside a brazier lights it too
  burnOn(q) {
    const ctx = this.ctx, still = !!this.G.qaStill, [x, z] = q.pos, y = ctx.heightAt(x, z);
    if (ctx.effects) {
      q.fx.push(ctx.effects.spawn('coldfire_flame', x, y + 0.86, z + 0.04, { duration: 1e9, fadeIn: still ? 0 : 0.3, ...(still ? { frame: 1 } : {}) }));
      q.fx.push(ctx.effects.spawn('coldfire_motes', x + 0.05, y + 1.1, z + 0.06, { duration: 1e9, ...(still ? { frame: 3 } : {}) }));
      for (const [ox, oz] of [[0, 0.35], [-0.75, 0.15], [0.75, 0.2], [0, -0.45]]) {   // a wide neon-blue pool on the ground
        q.fx.push(ctx.effects.spawn('coldfire_pool', x + ox, ctx.heightAt(x + ox, z + oz), z + oz + 0.03, { duration: 1e9, fadeIn: still ? 0 : 0.6, ...(still ? { frame: 0 } : {}) }));
      }
    }
    q.light = ctx.addGlow ? ctx.addGlow(x, y, z, { color: BRAZIER.color, intensity: 10, range: 5.0, fadeIn: still ? 0.01 : 0.4, lift: 1.1 }) : null;
    q.burning = true;
  }
  burnOff(q) {
    const fx = this.ctx.effects;
    for (const f of q.fx) if (f && fx) fx.remove(f);
    if (q.light) q.light.kill = true;
    q.fx = []; q.light = null; q.burning = false;
  }
  zones() {
    const out = [];
    for (const q of this.braziers) if (q.burning) out.push({ x: q.pos[0], z: q.pos[1], r: BRAZIER.r, src: 'brazier' });
    if (this.spring) out.push({ x: this.spring.pos[0], z: this.spring.pos[1], r: this.spring.r || 1.8, src: 'spring' });
    return out;
  }
  nearThing(ctx) { return !!this.doorNear(ctx.player.x, ctx.player.z); }
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
    if (this.buffT > 0) this.buffT -= dt;
    const ctx = this.ctx; if (!ctx) return;
    if (this.springCd > 0) this.springCd -= dt;
    const p = ctx.player, sp = this.spring;
    if (sp && !this.b && this.springCd <= 0 && Math.hypot(p.x - sp.pos[0], p.z - sp.pos[1]) < (sp.r || 1.8) * 0.8) this.drink();
    const dark = DARK(ctx.clock.t);
    for (const q of this.braziers) {
      if (q.flare > 0) q.flare -= dt;
      const want = q.lit && (dark || q.flare > 0);
      if (want && !q.burning) this.burnOn(q); else if (!want && q.burning) this.burnOff(q);
    }
    this.bounceStep(dt);
  }
  bounceStep(dt) {
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
