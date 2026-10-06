// [ALFHEIM] Alfheim foe behaviours (script alfheim.md 8.1-8.4), realm-alfheim branch. Hooked onto combat.js enemies by
// role via e.tick / e.mods.hurt / e.onKill (the same seams rares.js uses), so combat.js stays untouched.
//   prismShield (crystal golem 0.6, Lens Warden 0.9): soaks that share of every hit until a light beam crosses it
//     (alfheim_beams.js onBeamHit): the shield drops for 5 s and the foe staggers 2 s
//   mirrorduelist: a hit may make it step out of its reflection behind you; willwisp: blinks aside every 6 s (a lure)
//   faelan (conquer duel): yields at 25% HP (no kill), drops the Spire key
//   frostsentinel: a 3-hit frost combo (every 3rd swing chills twice as hard)
//   glassstalker: blinks to your side every 4 s
//   Lady Sylvaine, 6x, 3 phases: 1 The Long Light (lances, drain tether, glide, shard summons); 2 The Hall of Mirrors
//     (80% light shield, 2 reflections that shatter into shards, the roof sunbeam + mirror pylons break the shield and
//     stagger her 4 s); 3 Hunger (every 10 s she drinks a rim brazier; in the dark she lunges, in a light zone she can't
//     and her drain halves; relight braziers with spells)
import * as THREE from 'three';

const V = '#a45cf0';
export class AlfFoes {
  constructor(alf) { this.alf = alf; this.G = alf.G; this.told = {}; this.t = 0; }
  get ctx() { return this.alf.ctx; }
  get C() { return this.G.combat; }
  fx(n, x, y, z, o) { return this.alf.fx(n, x, y, z, o); }
  tell(key, msg, s = 2.4) { if (this.told[key]) return; this.told[key] = 1; this.G.toast(msg, s); }
  reset() { this.told = {}; this.syl = null; this.dropTether(); }
  hook(e) {
    e.alf = true;
    const r = e.a.role, D = e.D;
    if (D.prismShield) this.shield(e);
    if (r === 'mirrorduelist' || D.mimic) this.duelist(e);
    if (D.blink) this.blinker(e);
    if (D.yieldAt) this.yielder(e);
    if (D.combo) this.combo(e);
    if (r === 'sylvaine' && !e.sp.clone) this.sylvaine(e);
    if (e.sp.clone) this.clone(e);
    if (r === 'lenswarden') e.onKill = () => this.alf.onWarden(e);
  }
  // ------------------------------------------------------------ shields + beams
  shield(e) {
    const prev = e.mods && e.mods.hurt, self = this;
    e.mods = { ...(e.mods || {}), hurt(en, dmg) {
      let d = prev ? prev(en, dmg) : dmg;
      if ((en.shieldT || 0) <= self.t) {
        d = Math.max(1, Math.round(d * (1 - en.D.prismShield)));
        if (en.a.role === 'lenswarden') self.tell('lw_shield', 'The Lens Warden\'s prism shield soaks the blow! Cross a light beam through its chest-lens.', 3);
        else self.tell('cg_shield', 'The crystal golem\'s prism shell soaks the blow. A light beam would crack it.', 2.6);
      }
      return d;
    } };
  }
  onBeamHit(e, col) {
    const a = e.a;
    if (e.a.role === 'sylvaine' && !e.sp.clone) { this.sylBeam(e); return; }
    if (e.D.prismShield) {
      const was = (e.shieldT || 0) > this.t;
      e.shieldT = this.t + 5; this.stagger(e, 2);
      if (!was) { this.fx('beam_hit', a.x, a.y + 1.0 * (e.D.scale || 1), a.z + 0.1); this.G.toast(`${e.D.name}: the beam cracks its prism shield!`, 2); }
    }
    if (e.D.mimic && e.invis) { e.invis = false; a.quad.visible = true; }
  }
  stagger(e, s) {
    const a = e.a; e.cd = Math.max(e.cd, s); a.act = null; if (e.state === 'attack') e.state = 'chase';
    a.speed0 = a.speed0 || a.speed; a.speed = 0.01; e.stagEnd = this.t + s;
  }
  tickBase(e) { if (e.stagEnd && this.t >= e.stagEnd) { e.a.speed = e.a.speed0 || e.D.speed; e.stagEnd = 0; } }
  // ------------------------------------------------------------ small foes
  duelist(e) {
    const prev = e.mods && e.mods.hurt, self = this;
    e.mods = { ...(e.mods || {}), hurt(en, dmg) {
      const d0 = prev ? prev(en, dmg) : dmg;
      const ctx = self.ctx, C = self.C; if (!ctx || en.hp - d0 <= 0 || self.t < (en.blinkT || 0) || Math.random() > 0.35) return d0;
      en.blinkT = self.t + 4;
      const p = ctx.player, a = en.a, FV = { up: [0, -1], down: [0, 1], left: [-1, 0], right: [1, 0] }, fv = FV[p.facing] || [0, 1];
      self.fx('mirror_flash', a.x, a.y + 0.6, a.z + 0.05) || self.fx('prism_pop', a.x, a.y + 0.6, a.z + 0.05);
      const bx = p.x - fv[0] * 1.3, bz = p.z - fv[1] * 1.3;
      C.shove(a, bx - a.x, bz - a.z, Math.hypot(bx - a.x, bz - a.z));
      self.fx('prism_pop', a.x, a.y + 0.6, a.z + 0.05);
      self.tell('blink', 'The Mirror Duelist steps out of its reflection behind you!', 2);
      return Math.round(d0 * 0.5);
    } };
  }
  blinker(e) {
    const prev = e.tick, self = this;
    e.tick = (en, dt, frozen) => {
      if (prev) prev(en, dt, frozen);
      self.tickBase(en);
      if (frozen || en.state !== 'chase') return;
      en.blinkClock = (en.blinkClock ?? en.D.blink) - dt;
      if (en.blinkClock > 0) return;
      en.blinkClock = en.D.blink;
      const p = self.ctx.player, a = en.a, side = Math.random() < 0.5 ? -1 : 1;
      const dx = a.x - p.x, dz = a.z - p.z, L = Math.hypot(dx, dz) || 1;
      const tx = (en.a.role === 'glassstalker' ? p.x : a.x) + (-dz / L) * 1.8 * side, tz = (en.a.role === 'glassstalker' ? p.z : a.z) + (dx / L) * 1.8 * side;
      self.fx('prism_pop', a.x, a.y + 0.5, a.z + 0.05);
      self.C.shove(a, tx - a.x, tz - a.z, Math.hypot(tx - a.x, tz - a.z));
      self.fx('prism_pop', a.x, a.y + 0.5, a.z + 0.05);
    };
  }
  yielder(e) {
    const prev = e.mods && e.mods.hurt, self = this;
    e.mods = { ...(e.mods || {}), hurt(en, dmg) {
      const d = prev ? prev(en, dmg) : dmg;
      if (!en.yielded && en.hp - d <= en.D.hp * en.D.yieldAt) {
        en.yielded = true; en.hp = Math.round(en.D.hp * en.D.yieldAt) + d;   // the blow lands, she stays standing
        setTimeout(() => self.alf.onYield(en), 50);
      }
      return d;
    } };
  }
  combo(e) {
    const prev = e.tick, self = this;
    e.tick = (en, dt, frozen) => {
      if (prev) prev(en, dt, frozen);
      self.tickBase(en);
      if (en.state === 'attack' && en.fired && !en.comboDone) {
        en.comboDone = true;
        en.comboN = ((en.comboN || 0) + 1) % (en.D.combo || 3);
        if (en.comboN === 0) { const C = self.C; C.st = Math.max(0, C.st - en.D.chill); self.fx('frost_puff', self.ctx.player.x, self.ctx.player.y + 0.4, self.ctx.player.z + 0.05); }
      }
      if (en.state !== 'attack') en.comboDone = false;
    };
  }
  // ------------------------------------------------------------ Lady Sylvaine
  sylvaine(e) {
    const self = this, D = e.D;
    this.syl = e; e.phase = 1; e.lanceT = 4; e.tetherT = 9; e.glideT = 7; e.summonT = 20; e.drinkT = 10; e.lungeT = 5; e.shieldOn = false;
    e.mods = { ...(e.mods || {}), hurt(en, dmg) {
      if (en.phase === 2 && en.shieldOn && !(en.stagEnd > self.t)) { self.tell('syl_shield', 'Her light shield drinks the blow. Turn the mirror pylons and bounce the sunbeam into her!', 3.2); return Math.max(1, Math.round(dmg * (1 - D.shield))); }
      return dmg;
    } };
    e.tick = (en, dt, frozen) => self.sylTick(en, dt, frozen);
    e.onKill = () => { self.dropTether(); self.alf.onSylvaine(e); };
  }
  sylTick(e, dt, frozen) {
    const ctx = this.ctx, C = this.C; if (!ctx) return;
    this.tickBase(e);
    const a = e.a, p = ctx.player, D = e.D, d = Math.hypot(p.x - a.x, p.z - a.z), k = D.scale || 6;
    if (ctx.framePull) ctx.framePull(d < 16 ? 2.0 : 1);   // 5-6x boss camera pull (clamped by the engine: 1.6 on old main, 2.0 with Cozy's batch 1)
    if (frozen || C.peace || e.state === 'idle' || e.state === 'home') { this.dropTether(); return; }
    const f = e.hp / D.hp;
    if (e.phase === 1 && f <= D.phases[0]) this.sylPhase(e, 2);
    if (e.phase === 2 && f <= D.phases[1]) this.sylPhase(e, 3);
    // lances: a fan of 3 violet bolts, a 0.8 s tell (her raised hand flashes)
    e.lanceT -= dt;
    if (e.lanceT <= 0.8 && !e.lanceTold) { e.lanceTold = true; this.fx('beam_hit', a.x + 0.9, a.y + 0.62 * k * 1.8 * 0.55, a.z + 0.1); }
    if (e.lanceT <= 0) {
      e.lanceT = e.phase === 3 ? 5 : 6.5; e.lanceTold = false;
      const base = Math.atan2(p.z - a.z, p.x - a.x);
      for (const off of [-0.32, 0, 0.32]) {
        const ang = base + off, R = 12, tx = a.x + Math.cos(ang) * R, tz = a.z + Math.sin(ang) * R;
        const f = this.fx('prism_bolt', a.x, a.y + 2.2, a.z + 0.05, { to: [tx, ctx.heightAt(tx, tz), tz] });
        if (f) C.projs.push({ f, owner: 'enemy', dmg: 12, r: 0.6, src: a });
      }
    }
    // drain tether: a violet beam to you; 8 HP/s, heals her; a dodge roll or a mirror pylon between you breaks it
    e.tetherT -= dt;
    if (!this.tether && e.tetherT <= 0 && d < D.drain.range) this.startTether(e);
    if (this.tether) this.tetherTick(e, dt);
    // glide: across the arena when you keep away
    e.glideT -= dt;
    if (e.glideT <= 0 && d > 5.5) { e.glideT = 9; e.glide = 0.6; this.fx('drain_nova', a.x, a.y + 0.04, a.z); }
    if (e.glide > 0) { e.glide -= dt; a.lift = 1.0; C.shove(a, p.x - a.x, p.z - a.z, Math.min(d - 2.5, 7 * dt)); if (e.glide <= 0) a.lift = 0; }
    // shards every 20 s
    e.summonT -= dt;
    if (e.summonT <= 0) {
      e.summonT = 20;
      for (const ox of [-2.6, 2.6]) C.spawnEnemy({ id: `syl_shard_${Math.floor(this.t * 10)}_${ox > 0 ? 1 : 0}`, role: 'prismshard', pos: [a.x + ox, a.z + 1.6], once: true, noLoot: true }, true);
    }
    if (e.phase === 3) this.hunger(e, dt, d);
  }
  sylPhase(e, n) {
    e.phase = n; const a = e.a;
    this.fx('drain_nova', a.x, a.y + 0.04, a.z); this.fx('beam_hit', a.x, a.y + 3, a.z + 0.1);
    if (n === 2) {
      e.shieldOn = true; this.alf.bossBeams(true);
      this.G.toast('The Hall of Mirrors: Sylvaine splits into reflections behind a light shield. Only the real one casts a shadow.', 3.4);
      for (const [i, ox] of [[0, -4.2], [1, 4.2]]) {
        const ce = this.C.spawnEnemy({ id: `syl_mirror_${i}`, role: 'sylvaine', def: 'sylvaine_reflection', pos: [a.x + ox, a.z + 0.8], once: true, noLoot: true, noXp: true, clone: true }, true);
        if (ce) ce.clone = true;
      }
    }
    if (n === 3) {
      e.shieldOn = false;
      this.G.toast('Hunger: she drinks the arena\'s light. Stay in a light zone and relight the braziers with spells!', 3.4);
    }
  }
  sylBeam(e) {
    if (e.phase !== 2 || !e.shieldOn) return;
    const a = e.a;
    this.stagger(e, 4); e.shieldOn = false; e.shieldBackT = this.t + 9;
    this.fx('beam_hit', a.x, a.y + 3, a.z + 0.1); this.fx('prism_pop', a.x, a.y + 2, a.z + 0.1);
    this.G.toast('The sunbeam shatters her light shield! She staggers.', 2.4);
    setTimeout(() => { if (this.syl === e && e.phase === 2 && e.state !== 'dead') e.shieldOn = true; }, 9000);
  }
  clone(e) {
    e.tick = (en, dt) => { en.flick = (en.flick || 0) + dt; if (en.a.quad) en.a.quad.visible = Math.floor(en.flick * 2.2) % 5 !== 0; };   // reflections shimmer; the real one never does
    e.onKill = (en) => {
      const C = this.C, a = en.a;
      for (const ox of [-0.8, 0.8]) C.spawnEnemy({ id: `${en.id}_shard_${ox > 0 ? 1 : 0}_${Math.floor(this.t)}`, role: 'prismshard', pos: [a.x + ox, a.z + 0.6], once: true, noLoot: true }, true);
      this.tell('clone', 'A reflection! It shatters into prism shards.', 2);
    };
  }
  startTether(e) {
    const ctx = this.ctx; if (!ctx || !ctx.effects || !ctx.effects.sharp) return;
    const m = new THREE.Mesh(new THREE.BoxGeometry(1, 0.09, 0.09), new THREE.MeshBasicMaterial({ color: new THREE.Color(V) }));
    ctx.effects.sharp.add(m);
    this.tether = { m, life: 3.2, e };
    this.fx('drain_hit', e.a.x, e.a.y + 2, e.a.z) || this.fx('rune_circle', e.a.x, e.a.y + 0.03, e.a.z);
    this.tell('tether', 'A drain tether! Dodge-roll through it, or put a mirror pylon between you.', 2.8);
  }
  dropTether() { const T = this.tether; if (!T) return; if (T.m.parent) T.m.parent.remove(T.m); T.m.geometry.dispose(); T.m.material.dispose(); this.tether = null; if (this.syl) this.syl.tetherT = 11; }
  tetherTick(e, dt) {
    const T = this.tether, ctx = this.ctx, p = ctx.player, a = e.a, C = this.C, G = this.G;
    T.life -= dt;
    const hx = a.x, hz = a.z, hy = a.y + 2.4, px = p.x, pz = p.z, py = p.y + 1.0;
    const L = Math.hypot(px - hx, pz - hz) || 0.01;
    T.m.scale.x = Math.hypot(L, py - hy); T.m.position.set((hx + px) / 2, (hy + py) / 2, (hz + pz) / 2);
    T.m.rotation.set(0, -Math.atan2(pz - hz, px - hx), Math.atan2(py - hy, L));
    const pylon = (this.alf.beams ? this.alf.beams.mirrors : []).some((m) => {
      const vx = px - hx, vz = pz - hz, u = Math.max(0, Math.min(1, ((m.pos[0] - hx) * vx + (m.pos[1] - hz) * vz) / (L * L)));
      return u > 0.05 && u < 0.95 && Math.hypot(m.pos[0] - (hx + vx * u), m.pos[1] - (hz + vz * u)) < 0.55;
    });
    if (T.life <= 0 || p.roll || pylon || L > e.D.drain.range + 1 || G.downed) {
      if (p.roll || pylon) G.toast(pylon ? 'The pylon\'s mirror cuts the tether.' : 'You roll through the tether and it snaps!', 1.6);
      this.dropTether(); return;
    }
    const lit = G.glow && G.glow.litAt(p.x, p.z), dps = e.D.drain.dps * (lit && e.phase === 3 ? 0.5 : 1);
    T.acc = (T.acc || 0) + dps * dt;
    if (T.acc >= 4) { const n = Math.floor(T.acc); T.acc -= n; if (C.hurtPlayer(n, a, 0)) e.hp = Math.min(e.D.hp, e.hp + Math.round(e.D.drain.heal * n / 4)); }
  }
  hunger(e, dt, d) {
    const ctx = this.ctx, p = ctx.player, a = e.a, C = this.C, G = this.G, rims = this.alf.rims || [];
    e.drinkT -= dt;
    const lit = rims.filter((r) => r.lit);
    if (e.drinkT <= 1.2 && !e.drinkTold && lit.length) { e.drinkTold = lit[Math.floor(this.t * 7) % lit.length]; e.drinkTold.flick = 1.2; }
    if (e.drinkT <= 0) { e.drinkT = 10; const r = e.drinkTold; e.drinkTold = null; if (r && r.lit) this.alf.rimOff(r, true); }
    // in the dark she lunges (two violet eyes open 1 s before); in a light zone she can't
    e.lungeT -= dt;
    const safe = G.glow && G.glow.litAt(p.x, p.z);
    if (e.lungeT <= 1 && !e.lungeTold && !safe) { e.lungeTold = true; this.fx('beam_hit', a.x - 0.3, a.y + 4.8, a.z + 0.1); this.fx('beam_hit', a.x + 0.3, a.y + 4.8, a.z + 0.1); }
    if (e.lungeT <= 0) {
      e.lungeT = 5; e.lungeTold = false;
      if (safe) { this.tell('lunge_safe', 'She hisses at the light and can\'t reach you there.', 2); return; }
      if (d < 9) { C.shove(a, p.x - a.x, p.z - a.z, Math.max(0, d - 1.6)); this.fx('drain_nova', p.x, p.y + 0.04, p.z); C.hurtPlayer(e.D.dark.lunge, a, 0.6); }
    }
  }
}
