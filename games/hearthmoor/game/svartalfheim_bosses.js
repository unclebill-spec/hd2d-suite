// [SVARTALFHEIM] Gorrak Ironmaw, the Bound Forge-Tyrant (story 8.1, clockdeep2 C8). Hooked onto the combat enemy by e.tick /
// e.mods.hurt / e.onKill (the seams alfheim_bosses.js uses), so combat.js stays untouched. The default melee swing stays.
//   1 The Bound Tyrant (100-65%): chained to the pillar (6 m ring); hammer slam (0.8 s rune-circle tell, 3 m), chain whip (lane
//     tell, 9 m), rivet spray (5 bolts); 2 forgeconstruct every 25 s
//   2 Unbuckled (65-30%): chains off, walks; plates open for 4 s every 12 s (x2 damage); a quench valve (E / A) vents cold steam
//     across a lane for 6 s: Gorrak in it = plates lock open 6 s + stagger; molten lanes (8 s pools)
//   3 Forge-Tyrant (<30%): fire rain every 10 s (marked circles), a spark golem every 15 s; strike all 4 rune-anvils (E / A) =
//     he kneels 8 s and takes x1.5 for the rest of the fight
// Stand-ins: the rivets use the 'bolt' spell fx; the rune-anvil strike is an E / A spot (the story: one melee hit or spell).
export const PILLAR = [0, -30];
export const ANVILS = [[-5.6, -29.4], [5.6, -29.4], [-5.6, -23.0], [5.6, -23.0]];
export const VALVES = [[-7.8, -30.0], [7.8, -30.0], [-7.8, -23.6], [7.8, -23.6]];

export class GorrakFight {
  constructor(sv) { this.sv = sv; this.G = sv.G; this.t = 0; this.e = null; this.later = []; this.pools = []; this.struck = {}; this.steam = null; }
  get ctx() { return this.sv.ctx; }
  get C() { return this.G.combat; }
  fx(n, x, y, z, o) { const E = this.ctx && this.ctx.effects; return E && E.meta.effects[n] ? E.spawn(n, x, y, z, o || {}) : null; }
  gfx(n, x, y, z, o) { const E = this.ctx && this.ctx.gamefx; return E && E.meta.effects[n] ? E.spawn(n, x, y, z, o || {}) : null; }
  tell(msg, s = 2.6) { this.G.toast(msg, s); }
  reset() { this.e = null; this.later = []; this.pools = []; this.struck = {}; this.steam = null; }
  after(s, fn) { this.later.push({ at: this.t + s, fn }); }
  spawn() {
    const C = this.C, e = C.spawnEnemy({ id: 'gorrak', role: 'gorrak', pos: [PILLAR[0], PILLAR[1] + 2.0], once: true }, true);
    if (!e) return null;
    e.state = 'chase'; e.home = [PILLAR[0], PILLAR[1] + 2.0]; this.e = e; e.ph = 1;
    Object.assign(e, { slamT: 5, whipT: 9, sprayT: 13, summonT: 25, plateT: 12, plateOpen: 0, moltenT: 7, rainT: 10, golemT: 15, bind: 0, kneelEnd: 0, lockEnd: 0 });
    e.mods = { ...(e.mods || {}), hurt: (en, dmg) => {
      let d = dmg;
      if (en.plateOpen > 0 || en.lockEnd > this.t) d *= en.D.plates.mul;
      if (en.bind) d *= en.D.bindMul;
      return Math.round(d);
    } };
    e.tick = (en, dt, frozen) => this.tick(en, dt, frozen);
    e.onKill = () => this.sv.onGorrak(e);
    this.G.toast('Gorrak Ironmaw, the Bound Forge-Tyrant', 2.6);
    return e;
  }
  stagger(e, s) { const a = e.a; e.cd = Math.max(e.cd, s); a.act = null; if (e.state === 'attack') e.state = 'chase'; a.speed0 = a.speed0 || a.speed; a.speed = 0.01; e.stagEnd = this.t + s; }
  tick(e, dt, frozen) {
    const ctx = this.ctx, C = this.C; if (!ctx) return;
    this.t += dt;
    for (const l of this.later.filter((x) => x.at <= this.t)) l.fn();
    this.later = this.later.filter((x) => x.at > this.t);
    for (const p of this.pools.filter((q) => q.end <= this.t)) { if (p.fx) p.fx.dur = p.fx.t + 0.2; }
    this.pools = this.pools.filter((q) => q.end > this.t);
    if (e.stagEnd && this.t >= e.stagEnd) { e.a.speed = e.a.speed0 || e.D.speed; e.stagEnd = 0; }
    const a = e.a, p = ctx.player, D = e.D, d = Math.hypot(p.x - a.x, p.z - a.z);
    if (ctx.framePull) ctx.framePull(d < 18 ? 2.0 : 1);
    if (frozen || C.peace || e.state === 'idle' || e.state === 'home') return;
    const f = e.hp / D.hp;
    if (e.ph === 1 && f <= D.phases[0]) this.phase(e, 2);
    if (e.ph === 2 && f <= D.phases[1]) this.phase(e, 3);
    if (e.ph === 1) {   // the chains: a 6 m ring round the pillar
      const pd = Math.hypot(a.x - PILLAR[0], a.z - PILLAR[1]);
      if (pd > D.chained.r) C.shove(a, PILLAR[0] - a.x, PILLAR[1] - a.z, pd - D.chained.r);
    }
    const kneel = e.kneelEnd > this.t, still = kneel || e.stagEnd > 0;
    // molten lanes burn the player standing in them
    for (const q of this.pools) if (Math.hypot(p.x - q.x, p.z - q.z) < q.r) { q.acc = (q.acc || 0) + D.molten.dps * dt; if (q.acc >= 4) { const n = Math.floor(q.acc); q.acc -= n; C.hurtPlayer(n, { x: q.x, z: q.z }, 0); } }
    if (still) return;
    e.slamT -= dt; e.sprayT -= dt;
    if (e.ph === 1) e.whipT -= dt;
    if (e.slamT <= 0 && d < 5.5) { e.slamT = 7; this.slam(e); }
    if (e.ph === 1 && e.whipT <= 0 && d < D.whip.len + 1) { e.whipT = 9; this.whip(e); }
    if (e.sprayT <= 0 && d > 3) { e.sprayT = 10; this.spray(e); }
    e.summonT -= dt;
    if (e.ph === 1 && e.summonT <= 0) { e.summonT = 25; for (const ox of [-2.4, 2.4]) C.spawnEnemy({ id: `gk_fc_${Math.floor(this.t * 10)}_${ox > 0 ? 1 : 0}`, role: 'forgeconstruct', pos: [a.x + ox, a.z + 2.4], once: true, noLoot: true }, true); this.tell('Gorrak: "SERVE!" Two forge constructs clank to life.', 2.2); }
    if (e.ph >= 2) this.plates(e, dt);
    if (e.ph === 2) {
      e.moltenT -= dt;
      if (e.moltenT <= 0) { e.moltenT = 9; this.molten(e); }
    }
    if (e.ph === 3) {
      e.rainT -= dt; e.golemT -= dt;
      if (e.rainT <= 0) { e.rainT = 10; this.rain(e); }
      if (e.golemT <= 0) { e.golemT = 15; C.spawnEnemy({ id: `gk_sg_${Math.floor(this.t * 10)}`, role: 'sparkgolem', pos: [a.x + 3, a.z + 2], once: true, noLoot: true }, true); this.tell('A spark golem tumbles out of the flue.', 2); }
    }
  }
  phase(e, n) {
    e.ph = n; const a = e.a;
    this.fx('rune_slam', a.x, a.y + 0.03, a.z); this.fx('ember_pop', a.x, a.y + 3, a.z + 0.1);
    if (n === 2) { this.tell('Unbuckled: the chains snap. His plates overheat: open a quench valve into his path!', 3.4); a.speed0 = a.speed0 || a.speed; e.plateT = 4; }
    if (n === 3) { this.tell('Forge-Tyrant: the flue roars. Strike all four rune-anvils to re-light the binding!', 3.4); this.sv.anvilsOn(true); }
  }
  slam(e) {
    const a = e.a, C = this.C, ctx = this.ctx;
    this.fx('rune_circle', a.x, a.y + 0.03, a.z);
    this.after(0.8, () => {
      if (e.state === 'dead' || !this.ctx) return;
      this.fx('rune_slam', a.x, a.y + 0.03, a.z);
      const p = ctx.player; if (Math.hypot(p.x - a.x, p.z - a.z) <= 3.4) C.hurtPlayer(e.D.dmg, a, 0.7);
    });
  }
  whip(e) {
    const a = e.a, C = this.C, ctx = this.ctx, p = ctx.player, L = e.D.whip.len;
    const ang = Math.atan2(p.z - a.z, p.x - a.x);
    this.tell('The chain rattles taut!', 1.4);
    for (let i = 1; i <= 4; i++) this.fx('rune_circle', a.x + Math.cos(ang) * L * i / 4, a.y + 0.03, a.z + Math.sin(ang) * L * i / 4);
    this.after(0.9, () => {
      if (e.state === 'dead' || !this.ctx) return;
      for (let i = 1; i <= 4; i++) this.fx('ember_pop', a.x + Math.cos(ang) * L * i / 4, a.y + 0.4, a.z + Math.sin(ang) * L * i / 4 + 0.05);
      const px = p.x - a.x, pz = p.z - a.z, along = px * Math.cos(ang) + pz * Math.sin(ang), side = Math.abs(-px * Math.sin(ang) + pz * Math.cos(ang));
      const q = ctx.player; const qx = q.x - a.x, qz = q.z - a.z, al = qx * Math.cos(ang) + qz * Math.sin(ang), sd = Math.abs(-qx * Math.sin(ang) + qz * Math.cos(ang));
      void along; void side;
      if (al > 0.5 && al < L + 0.5 && sd < 1.1) C.hurtPlayer(e.D.whip.dmg, a, 0.6);
    });
  }
  spray(e) {
    const a = e.a, C = this.C, ctx = this.ctx, p = ctx.player, base = Math.atan2(p.z - a.z, p.x - a.x);
    this.tell('His chest-plate vents steam. Rivets!', 1.6);
    this.fx('ember_pop', a.x, a.y + 1.8, a.z + 0.1);
    this.after(0.6, () => {
      if (e.state === 'dead' || !this.ctx) return;
      const n = e.D.spray.n;
      for (let i = 0; i < n; i++) {
        const ang = base + (i - (n - 1) / 2) * 0.22, R = 11, tx = a.x + Math.cos(ang) * R, tz = a.z + Math.sin(ang) * R;
        const f = this.fx('bolt', a.x, a.y + 2.0, a.z + 0.05, { to: [tx, ctx.heightAt(tx, tz), tz] });
        if (f) C.projs.push({ f, owner: 'enemy', dmg: e.D.spray.dmg, r: 0.5, src: a });
      }
    });
  }
  plates(e, dt) {
    e.plateT -= dt;
    if (e.plateOpen > 0) { e.plateOpen -= dt; if (e.plateOpen <= 0) this.tell('His plates close again.', 1.4); }
    else if (e.plateT <= 0) {
      e.plateT = 12; e.plateOpen = 4; this.fx('ember_pop', e.a.x, e.a.y + 2, e.a.z + 0.1);
      this.tell('His plates glow white and open: the fire inside is the weak point (x2)!', 2.6);
    }
  }
  molten(e) {
    const a = e.a, ctx = this.ctx, p = ctx.player, ang = Math.atan2(p.z - a.z, p.x - a.x);
    for (let i = 1; i <= 3; i++) {
      const x = a.x + Math.cos(ang) * 2.0 * i, z = a.z + Math.sin(ang) * 2.0 * i;
      const fx = this.gfx('pool_red', x, ctx.heightAt(x, z), z, { duration: 8, fadeIn: 0.4 });
      this.pools.push({ x, z, r: 1.1, end: this.t + 8, fx });
    }
    this.tell('He drags a molten lane across the floor.', 1.8);
  }
  rain(e) {
    const ctx = this.ctx, C = this.C, p = ctx.player;
    this.tell('Fire rain! Leave the marked circles.', 1.8);
    const pts = [[p.x, p.z]];
    for (let i = 0; i < 4; i++) { const ang = Math.random() * 6.28, r = 2 + Math.random() * 5; pts.push([p.x + Math.cos(ang) * r, p.z + Math.sin(ang) * r]); }
    for (const [x, z] of pts) {
      this.fx('rune_circle', x, ctx.heightAt(x, z) + 0.03, z);
      this.after(1.2, () => {
        if (e.state === 'dead' || !this.ctx) return;
        this.fx('ember_pop', x, ctx.heightAt(x, z) + 0.3, z + 0.05);
        const q = ctx.player; if (Math.hypot(q.x - x, q.z - z) < 1.3) C.hurtPlayer(e.D.rain.dmg, { x, z }, 0.5);
      });
    }
  }
  // a quench valve: cold steam across the lane between the valve and the pillar for 6 s
  valve(i) {
    const e = this.e, ctx = this.ctx; if (!e || e.state === 'dead' || e.ph !== 2) { this.tell('The valve hisses. Nothing to cool right now.', 1.8); return; }
    const v = VALVES[i]; this.fx('frost_puff', v[0], ctx.heightAt(v[0], v[1]) + 0.4, v[1] + 0.05);
    const a = e.a, mx = (v[0] + PILLAR[0]) / 2, mz = (v[1] + PILLAR[1]) / 2;
    this.tell('The valve vents cold steam across the lane.', 1.6);
    const until = this.t + 6;
    const poll = (n) => {
      if (!this.ctx || e.state === 'dead' || n > 12) return;
      if (Math.hypot(a.x - mx, a.z - mz) < 4.2 && e.lockEnd < this.t) {
        e.lockEnd = this.t + 6; e.plateOpen = 6; this.stagger(e, 2.5);
        this.fx('frost_puff', a.x, a.y + 1.5, a.z + 0.1);
        this.tell('He steps into the cold steam: plates lock open, he staggers!', 2.6); return;
      }
      if (this.t < until) this.after(0.5, () => poll(n + 1));
    };
    poll(0);
  }
  anvil(i) {
    const e = this.e, ctx = this.ctx; if (!e || e.state === 'dead' || e.ph !== 3 || this.struck[i]) return false;
    this.struck[i] = 1; const a = ANVILS[i];
    this.fx('rune_slam', a[0], ctx.heightAt(a[0], a[1]) + 0.03, a[1]);
    const n = Object.keys(this.struck).length;
    this.tell(`Rune-anvil struck (${n}/4). The binding runes flare cold blue.`, 1.8);
    if (n >= 4) { e.bind = 1; e.kneelEnd = this.t + 8; this.stagger(e, 8); this.fx('rune_circle', e.a.x, e.a.y + 0.03, e.a.z); this.tell('The binding holds! Gorrak is pulled to his knees. He takes more damage now.', 3.2); }
    return true;
  }
}
