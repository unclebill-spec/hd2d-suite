// [ALFHEIM] Lumi, the talking wisp companion (script alfheim.md 5.5 / 9.3, Bill's correction 2026-10-06), realm-alfheim.
// NOT the wisp-kit pet: about 2x its size, a neon-blue core (#5ac8ff) with a pulsing violet halo (#a45cf0), white dot
// eyes, a curling tail and a real light pool; she floats at head height (lift 1.1, above any pet) and she TALKS.
// Recruited at The Dimming's end (S.flags.companions.lumi = 1, befriend only). Her kit (support, never melee):
//   * Wisp Call: every 18 s in a fight her halo flares and 2 mini-wisps orbit you for 12 s, zapping foes within 3.2 m
//   * light zone: r 2.2 round you (a glow.js light zone: the Lantern-glow buff, Sylvaine can't lunge into it)
//   * mark: every 8 s the nearest foe gets a violet ring (+5% crit on it)
// Barks (script 5.5 table) show in the talk strip with her name. Body / pool / sparks are spell effects (lumi_wisp,
// coldfire_pool, lumi_spark, lumi_zap, lumi_mark); areas built before this branch fall back to light_orb / glitter.
export const COMPANIONS = {
  lumi: { name: 'Lumi', kind: 'wisp', talks: true, role: 'companion_lumi', realm: 'alfheim', scale: 2.0,
          hover: { lift: 1.1, bob: 0.08, hz: 0.7 },
          glow: '#5ac8ff', halo: '#a45cf0',
          light: { color: '#5ac8ff', intensity: 5.5, range: 4.2, lift: 1.1, pulse: [0.85, 1.15, 0.8], r: 2.6 },
          fx: { aura: 'lumi_wisp', pool: 'coldfire_pool', parts: 'lumi_spark' },
          kit: { call: { wisps: 2, life: 12, cd: 18, dmg: 6, reach: 3.2, ranged: true }, light: { r: 2.2 }, mark: { crit: 0.05, every: 8 } },
          about: 'A talking wisp, twice a wisp kit\'s size. Once the light of Sylvaine\'s nursery. Free now, and staying with you.' },
};
export const LUMI_BARKS = {
  follow: ['Ting! Left, left, no, your other left.', 'I like your boots. They\'re very... stompy.'],
  night: 'Night! Finally. Days are too bright. I can\'t see myself.',
  aurora: 'The sky\'s dancing. The old queen used to dance like that, before.',
  prismrain: 'Ooh, tickly rain. Everything\'s sparkling. Me most of all.',
  pond: 'Hello, frogs! (The frogs sing back. Lumi glows a little brighter.)',
  combat: 'Bright and sharp! I\'ll light them up for you!',
  call: 'Out you come, little ones! Bite!',
  lowhp: 'You\'re flickering! Drink something! The red one!',
  spring: 'Ting? Something fizzy behind those vines. I can hear it.',
  pet: 'Hello, small one. (The wisp kit hums. It doesn\'t talk. Most wisps don\'t. I\'m special.)',
  bifrost: 'So many gates. Most of them are frowning. Alfheim\'s isn\'t, now. Because of you.',
  plaza: 'Your village is so warm. Everything smells like bread. Is it always like this? Can I stay?',
  lane: 'Your village is so warm. Everything smells like bread. Is it always like this? Can I stay?',
  vanaheim: 'Mushroom people! They used to be cross with us. Not anymore. You did that.',
  storm: 'The storm\'s loud. I\'m not scared. I\'m just floating very close to you. On purpose.',
  prismvault: 'I\'ve been here before. I hung over her cradle. She was smaller. So was I.',
};
const L = COMPANIONS.lumi;
const NIGHT = (t) => t > 0.8 || t < 0.25;

export class Lumi {
  constructor(G) { this.G = G; this.ctx = null; this.on = false; this.t = 0; this.minis = []; this.said = {}; this.barkCd = 0; }
  joined() { const F = this.G.S.flags || {}; return !!((F.companions || {}).lumi) && (F.alliance || {}).alfheim !== 'conquer'; }
  fx(name, alt, x, y, z, o) {
    const E = this.ctx && this.ctx.effects; if (!E) return null;
    const n = E.meta.effects[name] ? name : alt && E.meta.effects[alt] ? alt : null;
    return n ? E.spawn(n, x, y, z, o || {}) : null;
  }
  attach(ctx, area) {
    this.ctx = ctx; this.area = area; this.on = false; this.minis = []; this.said = {}; this.t = 0; this.callT = 6; this.markT = 3; this.idleT = 40 + Math.random() * 40;
    if (!this.joined()) return;
    this.spawnBody();
    this.later(1.4, () => { const b = LUMI_BARKS[area]; if (b) this.bark(b, area); else if (NIGHT(ctx.clock.t)) this.bark(LUMI_BARKS.night, 'night'); });
  }
  spawnBody(at) {
    const c = this.ctx, p = c.player, x = at ? at[0] : p.x + 0.7, z = at ? at[1] : p.z + 0.3, y = c.heightAt(x, z);
    this.x = x; this.z = z; this.y = y;
    this.body = this.fx('lumi_wisp', 'light_orb', x, y + L.hover.lift, z + 0.04, { duration: 1e9 });
    this.pool = this.fx('coldfire_pool', 'light_pool', x, y + 0.02, z + 0.03, { duration: 1e9 });
    this.light = c.addGlow ? c.addGlow(x, y, z, { color: L.light.color, intensity: L.light.intensity, range: L.light.range, lift: L.light.lift, fadeIn: 0.4 }) : null;
    this.on = true;
  }
  detach() {
    const E = this.ctx && this.ctx.effects;
    if (E) { for (const f of [this.body, this.pool, ...this.minis.map((m) => m.f), this.markFx]) if (f) E.remove(f); }
    if (this.light) this.light.kill = true;
    this.body = this.pool = this.light = this.markFx = null; this.minis = []; this.on = false; this.ctx = null;
  }
  later(s, fn) { const c = this.ctx; setTimeout(() => { if (this.ctx === c) fn(); }, s * 1000); }
  bark(line, key) {
    if (key && this.said[key]) return; if (key) this.said[key] = 1;
    const el = document.getElementById('say'); if (!el) return;
    el.innerHTML = `<b>Lumi</b> — ${line}`; el.hidden = false;
    const tok = (this.barkTok = (this.barkTok || 0) + 1);
    setTimeout(() => { if (this.barkTok === tok) el.hidden = true; }, 4600);
    this.lastBark = line;
  }
  zones() { return this.on && this.ctx ? [{ x: this.ctx.player.x, z: this.ctx.player.z, r: L.kit.light.r, src: 'lumi' }] : []; }
  update(dt) {
    const c = this.ctx; if (!c || !this.on) return;
    this.t += dt;
    const p = c.player, G = this.G, C = G.combat;
    // follow: hover beside your shoulder at head height, catch up fast, hop over when left far behind
    const fv = { up: [0, 1], down: [0, -1], left: [1, 0], right: [-1, 0] }[p.facing] || [0, -1];
    const tx = p.x + fv[0] * 0.55 + 0.55, tz = p.z + fv[1] * 0.35 + 0.15;
    const d = Math.hypot(tx - this.x, tz - this.z);
    if (d > 7) { this.x = tx; this.z = tz; }
    else { const k = Math.min(1, dt * (d > 2.5 ? 6 : 3)); this.x += (tx - this.x) * k; this.z += (tz - this.z) * k; }
    this.y = c.heightAt(this.x, this.z);
    const bob = Math.sin(this.t * Math.PI * 2 * L.hover.hz) * L.hover.bob, pulse = 1 + Math.sin(this.t * Math.PI * 2 / 1.2) * 0.15;
    if (this.body) { this.body.x = this.x; this.body.y = this.y + L.hover.lift + bob + (p.lift || 0) * 0.5; this.body.z = this.z + 0.04; }
    if (this.pool) { this.pool.x = this.x; this.pool.y = this.y + 0.02; this.pool.z = this.z + 0.03; }
    if (this.light) { this.light.pos.set(this.x, this.y, this.z); this.light.base = L.light.intensity * pulse; }
    if (d > 2.5 && Math.floor(this.t * 8) !== Math.floor((this.t - dt) * 8)) this.fx('lumi_spark', 'glitter', this.x - fv[0] * 0.3, this.y + L.hover.lift, this.z + 0.05, { duration: 0.5 });
    if (!C || !C.ctx || G.downed) return;
    // fight: Wisp Call, the mark, combat barks
    const foes = C.alive().filter((e) => Math.hypot(e.a.x - p.x, e.a.z - p.z) < 8 && (e.state === 'chase' || e.state === 'attack'));
    const fighting = foes.length > 0;
    if (fighting && !this.fighting && this.barkCd <= 0) { this.bark(LUMI_BARKS.combat); this.barkCd = 25; }
    this.fighting = fighting; this.barkCd -= dt;
    this.callT -= dt; this.markT -= dt;
    if (fighting && this.callT <= 0) this.wispCall();
    if (fighting && this.markT <= 0) this.mark(foes);
    if (this.marked && (this.marked.state === 'dead' || this.marked.state === 'gone' || this.t > this.markEnd)) this.unmark();
    if (this.markFx && this.marked) { this.markFx.x = this.marked.a.x; this.markFx.z = this.marked.a.z + 0.02; this.markFx.y = this.marked.a.y + 0.03; }
    this.updateMinis(dt, foes);
    if (G.S.hp != null && C.maxHp && G.S.hp < C.maxHp() * 0.3 && (this.lowT || 0) < this.t) { this.lowT = this.t + 30; this.bark(LUMI_BARKS.lowhp); }
    if (!fighting && (this.idleT -= dt) <= 0) { this.idleT = 60 + Math.random() * 50; const f = LUMI_BARKS.follow; this.bark(f[Math.floor(Math.random() * f.length)]); }
  }
  wispCall() {
    const c = this.ctx, k = L.kit.call; this.callT = k.cd;
    this.bark(LUMI_BARKS.call);
    this.fx('beam_hit', 'sparkle_burst', this.x, this.y + L.hover.lift - 0.2, this.z + 0.05);
    for (const m of this.minis) if (m.f && c.effects) c.effects.remove(m.f);
    this.minis = [];
    for (let i = 0; i < k.wisps; i++) this.minis.push({ a: i * Math.PI, life: k.life, zapT: 0.6 + i * 0.5, f: this.fx('lumi_spark', 'glitter', this.x, this.y + 1, this.z, { duration: 1e9 }) });
  }
  updateMinis(dt, foes) {
    const c = this.ctx, C = this.G.combat, p = c.player, k = L.kit.call;
    for (const m of this.minis) {
      m.life -= dt; m.a += dt * 2.4; m.zapT -= dt;
      const x = p.x + Math.cos(m.a) * 1.0, z = p.z + Math.sin(m.a) * 0.7, y = c.heightAt(x, z) + 1.0 + Math.sin(m.a * 2) * 0.15;
      if (m.f) { m.f.x = x; m.f.y = y; m.f.z = z + 0.05; }
      if (m.zapT <= 0) {
        const tgt = foes.filter((e) => Math.hypot(e.a.x - x, e.a.z - z) < k.reach).sort((a, b) => Math.hypot(a.a.x - x, a.a.z - z) - Math.hypot(b.a.x - x, b.a.z - z))[0];
        if (tgt) {
          m.zapT = 1.2;
          this.fx('lumi_zap', 'sparkle_burst', x, y, z + 0.05, { to: [tgt.a.x, tgt.a.y + 0.6, tgt.a.z + 0.05] });
          C.damageEnemy(tgt, C.out('summon', k.dmg), { x, z }, 0.05, '#5ac8ff');
        } else m.zapT = 0.3;
      }
    }
    const gone = this.minis.filter((m) => m.life <= 0);
    for (const m of gone) if (m.f && c.effects) c.effects.remove(m.f);
    this.minis = this.minis.filter((m) => m.life > 0);
  }
  mark(foes) {
    const c = this.ctx, p = c.player; this.markT = L.kit.mark.every;
    const e = foes.slice().sort((a, b) => Math.hypot(a.a.x - p.x, a.a.z - p.z) - Math.hypot(b.a.x - p.x, b.a.z - p.z))[0]; if (!e) return;
    this.unmark();
    this.marked = e; this.markEnd = this.t + L.kit.mark.every;
    this.markFx = this.fx('lumi_mark', 'rune_circle', e.a.x, e.a.y + 0.03, e.a.z + 0.02, { duration: 1e9 });
    if (!e.lumiHook) {   // +5% crit on the marked foe: a 1.5x blow 5% of the time
      e.lumiHook = true; const prev = e.mods && e.mods.hurt, self = this;
      e.mods = { ...(e.mods || {}), hurt(en, dmg) { let d = prev ? prev(en, dmg) : dmg; if (self.marked === en && Math.random() < L.kit.mark.crit) d = Math.round(d * 1.5); return d; } };
    }
  }
  unmark() { if (this.markFx && this.ctx && this.ctx.effects) this.ctx.effects.remove(this.markFx); this.markFx = null; this.marked = null; }
  qa() { return { on: this.on, joined: this.joined(), x: this.x, z: this.z, minis: this.minis.length, marked: this.marked ? this.marked.id : null, body: this.body ? this.body.name : null, lastBark: this.lastBark || null }; }
}
