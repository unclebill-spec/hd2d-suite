// Hearthmoor combat core (stage 1): real-time hits, guard, dodge i-frames, stamina, hero spells + summons,
// three enemies with simple AI, crisp pixel damage numbers, cozy defeat (wake up, nothing lost).
// Visuals come from the engine (sprites, spells atlas); this file only decides who gets hit and how hard.
import { mods as progMods, XP, addXP, MODES, summonTier } from './progress.js';
import { HERO, SPELLS, CHARM_DMG, CHARM_CD, SUMMONS, SUMMON_LIFE, SUMMON_CD, ENEMIES, RESPAWN, LEASH, SPAWNS, PLAYER } from './heroes.js';

// summon tiers (Part 4): I base, II glows (a following light + sparkles), III radiant form (lit rim, crown of light,
// sparkles; '<role>_r' sprite) + a rune circle on arrival, IV (capstone) brighter and wider light + a sparkle burst.
// Stats grow through the summon-branch skills (summonMul / summonLife). Gloom-and-glow: palette pixels, no bloom.
const SUMMON_GLOW = { mushgolem: '#f2c24a', runesentinel: '#ffb24a', runewisp: '#94c0dc', stormsprite: '#94c0dc', sapling: '#b2c464', emberimp: '#ffb24a' };
const ROMAN = ['', 'I', 'II', 'III', 'IV'];
const PAL = { ink: '#2a1e1c', white: '#fff8e6', gold: '#f2c24a', rose: '#e47c8c', green: '#b2c464', sky: '#94c0dc' };
// 3x5 pixel font: digits, + and - (drawn at an integer scale with a 1 px ink outline, never smoothed)
const GLYPH = {
  0: ['111', '101', '101', '101', '111'], 1: ['010', '110', '010', '010', '111'], 2: ['111', '001', '111', '100', '111'],
  3: ['111', '001', '011', '001', '111'], 4: ['101', '101', '111', '001', '001'], 5: ['111', '100', '111', '001', '111'],
  6: ['111', '100', '111', '101', '111'], 7: ['111', '001', '010', '010', '010'], 8: ['111', '101', '111', '101', '111'],
  9: ['111', '101', '111', '001', '111'], '+': ['000', '010', '111', '010', '000'], '-': ['000', '000', '111', '000', '000'],
};
export function pixelText(str, color, scale = 3) {
  const w = str.length * 4 + 1, h = 7;                 // 3 px glyph + 1 px gap, 1 px outline all round
  const cv = document.createElement('canvas');
  cv.width = w * scale; cv.height = h * scale;
  const g = cv.getContext('2d');
  g.imageSmoothingEnabled = false;
  const on = new Set();
  [...str].forEach((ch, i) => (GLYPH[ch] || []).forEach((row, y) => [...row].forEach((b, x) => { if (b === '1') on.add(`${1 + i * 4 + x},${1 + y}`); })));
  const px = (x, y, c) => { g.fillStyle = c; g.fillRect(x * scale, y * scale, scale, scale); };
  for (const k of on) {
    const [x, y] = k.split(',').map(Number);
    for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, -1], [1, -1], [-1, 1]]) if (!on.has(`${x + dx},${y + dy}`)) px(x + dx, y + dy, PAL.ink);
  }
  for (const k of on) { const [x, y] = k.split(',').map(Number); px(x, y, color); }
  return cv;
}

const FV = { down: [0, 1], up: [0, -1], left: [-1, 0], right: [1, 0] };
const dist = (a, b) => Math.hypot(a.x - b.x, a.z - b.z);

export class Combat {
  constructor(G) {
    this.G = G;
    this.layer = document.getElementById('fxlayer');
    this.nums = [];
    this.bars = new Map();
    this.st = PLAYER.stamina; this.stT = 0;
    this.cd = { spell: 0, charm: 0, summon: 0 };
    this.godT = 0;
    this.defeated = {};              // area:id -> game seconds left until it wanders back
    this.time = 0;
  }
  get hero() { return HERO[this.G.S.cls] || HERO.wildcaller; }
  maxHp() { return this.hero.hp + this.M.hpAdd; }
  maxSt() { return PLAYER.stamina + this.M.stAdd; }
  get M() { return progMods(this.G.S); }
  // outgoing damage: stat / skill multiplier + a crit roll (crits pop bigger, in gold)
  out(kind, base) {
    const M = this.M, mul = kind === 'melee' ? M.meleeMul : kind === 'summon' ? M.summonMul : M.spellMul;
    const crit = kind !== 'summon' && Math.random() < M.crit;
    this.lastCrit = crit;
    const lit = kind !== 'summon' && this.G.glow ? this.G.glow.dmgMul() : 1;   // glowlit: +10%
    const mode = (MODES[this.G.S.mode] || MODES.adventurer).deal;
    return Math.max(1, Math.round(base * mul * lit * mode * (crit ? 1.5 + (M.critDmg || 0) : 1)));
  }

  // ---------------------------------------------------------------- area lifecycle
  attach(ctx, area) {
    this.ctx = ctx; this.area = area;
    this.enemies = []; this.navBig = null; this.summon = null; this.projs = []; this.traps = []; this.later = [];
    this.clearDom();
    if (this.G.S.hp == null || this.G.S.hp <= 0) this.G.S.hp = this.maxHp();
    this.G.S.hp = Math.min(this.G.S.hp, this.maxHp());
    for (const sp of SPAWNS[area] || []) if (!sp.night && !(this.defeated[area + ':' + sp.id] > 0)) this.spawnEnemy(sp);
  }
  detach() { this.clearDom(); this.ctx = null; this.enemies = []; this.navBig = null; this.summon = null; }
  clearDom() {
    for (const e of this.enemies || []) if (e.light) e.light.kill = true;
    if (this.bossEl) { this.bossEl.remove(); this.bossEl = null; }
    for (const n of this.nums) n.el.remove();
    for (const b of this.bars.values()) b.remove();
    this.nums = []; this.bars.clear();
  }
  spawnEnemy(sp, poof = false) {
    const ctx = this.ctx, D = ENEMIES[sp.role];
    const a = ctx.addNpc({ id: sp.id, role: sp.role, name: D.name, pos: sp.pos.slice(), behavior: 'idle', turn: false, speed: D.speed });
    a.ai = true; a.noTalk = true; a.r = D.r; a.facing = 'down';
    const e = { a, D, sp, id: sp.id, home: sp.pos.slice(), hp: D.hp, state: 'idle', t: 0, cd: 1, wt: 1 + Math.random() * 2, target: null,
                phase: Math.random() * 6, night: !!sp.night };
    const k = D.scale || 1;   // big foes: light reach / height grow with the figure
    if (D.glow && ctx.addGlow) e.light = ctx.addGlow(a.x, a.y, a.z, { color: D.glow, intensity: 3.2 + k * 0.6, range: 3.2 * Math.sqrt(k) * 1.15, lift: 1.1 * k, fadeIn: 0.6 });   // the boss carries its own rune light
    this.enemies.push(e);
    if (poof && ctx.effects) ctx.effects.spawn('summon_poof', a.x, a.y, a.z + 0.05);
    return e;
  }
  alive() { return this.enemies.filter((e) => e.state !== 'dead' && e.state !== 'gone'); }
  get peace() { return !!this.G.peace; }
  paused() { const G = this.G; return !!(G.title || G.busy || G.dlg || G.log || G.downed || G.picking); }

  // ---------------------------------------------------------------- per frame (dt already slowed by the spell wheel)
  update(dt, ctx) {
    if (!this.ctx || ctx !== this.ctx) return;
    this.time += dt;
    const p = ctx.player, G = this.G;
    // cooldowns + stamina
    for (const k in this.cd) this.cd[k] = Math.max(0, this.cd[k] - dt);
    if (this.godT > 0) { this.godT -= dt; p.quad.visible = this.godT <= 0 || Math.floor(this.godT * 12) % 2 === 0; if (this.godT <= 0) p.quad.visible = true; }
    const guarding = p.act && p.act.name === 'defend';
    if (this.stT > 0) this.stT -= dt;
    else if (!guarding && !p.roll) this.st = Math.min(this.maxSt(), this.st + PLAYER.regen * (1 + (this.M.stRegen || 0)) * (this.G.glow ? this.G.glow.regenMul() : 1) * dt);
    const regen = this.M.regen;   // Warm Light: slow regen while nothing is chasing you
    if (regen && !this.G.downed && this.G.S.hp < this.maxHp() && !this.enemies.some((e) => e.state === 'chase' || e.state === 'attack')) this.G.S.hp = Math.min(this.maxHp(), this.G.S.hp + regen * dt);
    // the player's swing lands on its impact frame
    if (p.act && p.act.name === 'attack' && !p.act.hitDone && p.act.t >= PLAYER.impact) { p.act.hitDone = true; this.meleeHit(); }
    // defeated enemies wander back after a while
    for (const k of Object.keys(this.defeated)) {
      this.defeated[k] -= dt;
      if (this.defeated[k] <= 0) {
        delete this.defeated[k];
        const [ar, id] = k.split(':');
        const sp = (SPAWNS[ar] || []).find((s) => s.id === id);
        if (ar === this.area && sp && !sp.night && !this.enemies.find((e) => e.id === id && e.state !== 'gone')) {
          this.enemies = this.enemies.filter((e) => e.id !== id);
          this.spawnEnemy(sp, true);
        }
      }
    }
    // night: one more wraith drifts into the glade after dark, and fades at dawn
    const ct = ctx.clock.t, night = ct > 0.8 || ct < 0.25;   // 19:12 to 06:00 (Mossglen has fireflies by day, so not the bug grade)
    for (const sp of this.G.qaStill ? [] : SPAWNS[this.area] || []) {   // QA stills: no night spawn mid-capture
      if (!sp.night) continue;
      const e = this.enemies.find((x) => x.id === sp.id && x.state !== 'gone');
      if (night && !e && !(this.defeated[this.area + ':' + sp.id] > 0)) { this.enemies = this.enemies.filter((x) => x.id !== sp.id); this.spawnEnemy(sp, true); }
      else if (!night && e && e.state === 'idle') { this.kill(e, true); }
    }
    const frozen = this.paused() || !!this.G.qaStill;   // QA screenshots: enemies hold still (deterministic sprite checks)
    for (const e of this.enemies) this.updateEnemy(e, dt, frozen);
    this.enemies = this.enemies.filter((e) => e.state !== 'gone' || e.keep);
    this.updateSummon(dt, frozen);
    this.updateProjs(dt);
    this.updateTraps(dt);
    for (const l of this.later) l.t -= dt;
    const due = this.later.filter((l) => l.t <= 0); this.later = this.later.filter((l) => l.t > 0);
    for (const l of due) l.fn();
    this.updateDom(dt);
  }

  // ---------------------------------------------------------------- enemies
  updateEnemy(e, dt, frozen) {
    const ctx = this.ctx, a = e.a, D = e.D, p = ctx.player;
    if (e.state === 'gone') return;
    if (e.state === 'dead') {
      e.t += dt;
      a.act = null; a.anim = 'die'; a.frame = Math.min(3, Math.floor(e.t * 6));
      if (D.float) a.lift = Math.max(0, (a.lift || 0) - dt * 0.4);
      if (e.t > 1.5) a.quad.visible = Math.floor(e.t * 10) % 2 === 0;
      if (e.light) { e.light.kill = true; e.light = null; }
      if (e.t > 2.3) { ctx.removeNpc(a); e.state = 'gone'; const b = this.bars.get(e.id); if (b) { b.remove(); this.bars.delete(e.id); } }
      return;
    }
    let moving = false;
    const dx = p.x - a.x, dz = p.z - a.z, d = Math.hypot(dx, dz);
    const fromHome = Math.hypot(a.x - e.home[0], a.z - e.home[1]);
    const sees = !frozen && !this.peace && this.godT <= 0 && d < D.aggro && Math.abs(p.y - a.y) < 1.3;
    e.cd -= dt;
    if (frozen && e.state !== 'attack') { ctx.actors.animate(a, dt, false); this.floatBob(e); return; }
    const gl = D.shy ? this.G.glow : null;   // cold-fire wraiths: never drift into light
    const step = (tx, tz, scale = 1) => {
      if (gl) { const n = Math.hypot(tx, tz) || 1; if (gl.litAt(a.x + tx / n * 0.45, a.z + tz / n * 0.45)) return false; }
      return ctx.moveActor(a, tx, tz, dt * scale);
    };
    if (gl && e.state !== 'attack') {
      const Z = gl.zoneAt(a.x, a.z);   // caught in light (a pool bloomed under it, a lamp came on): slip out
      if (Z) { const mv = ctx.moveActor(a, a.x - Z.x || 0.01, a.z - Z.z, dt * 1.2); ctx.actors.animate(a, dt, mv); this.floatBob(e); return; }
    }
    const pLit = gl ? gl.lit : false;
    switch (e.state) {
      case 'idle': {
        if (sees) { e.state = 'chase'; e.cd = Math.max(e.cd, 0.5); this.ping(e); break; }
        if (e.target) {
          const ex = e.target[0] - a.x, ez = e.target[1] - a.z;
          if (Math.hypot(ex, ez) < 0.2) { e.target = null; e.wt = 1.5 + Math.random() * 3; } else { moving = step(ex, ez, 0.45); if (!moving) e.target = null; }
        } else if ((e.wt -= dt) <= 0) {
          const ang = Math.random() * Math.PI * 2, r = 0.6 + Math.random() * 1.4;
          e.target = [e.home[0] + Math.cos(ang) * r, e.home[1] + Math.sin(ang) * r];
        }
        break;
      }
      case 'chase': {
        if (this.peace || fromHome > LEASH || d > D.aggro * 1.9 || this.godT > 0) { e.state = 'home'; break; }
        if (D.ranged) {
          if (d < D.keep - 0.6) moving = step(-dx, -dz);
          else if (d > D.keep + 1.4) moving = this.seek(e, p.x, p.z, dt, step);
          else if (e.cd <= 0 && !pLit) { this.beginAttack(e); break; }   // a lit hero is out of reach
          else ctx.actors.setFacingFromVec(a, dx, dz);
        } else if (d > D.reach * 0.8) moving = this.seek(e, p.x, p.z, dt, step);
        else if (e.cd <= 0) { this.beginAttack(e); break; }
        else ctx.actors.setFacingFromVec(a, dx, dz);
        break;
      }
      case 'attack': {
        e.t += dt;
        if (!e.fired && e.t >= D.windup) { e.fired = true; this.enemyStrike(e); }
        if (!a.act) { e.state = 'chase'; e.cd = D.cd; }
        break;
      }
      case 'home': {
        const ex = e.home[0] - a.x, ez = e.home[1] - a.z;
        if (Math.hypot(ex, ez) < 0.3 || (e.homeT = (e.homeT || 0) + dt) > 8) { e.state = 'idle'; e.homeT = 0; e.hp = D.hp; e.wt = 2; }
        else moving = this.seek(e, e.home[0], e.home[1], dt, step);
        if (sees && fromHome < LEASH * 0.6) e.state = 'chase';
        break;
      }
      default: break;
    }
    ctx.actors.animate(a, dt, moving && !a.act);
    this.floatBob(e);
  }
  // walk around walls, fences and trees: A* over the area's nav grid (string-pulled), re-planned twice a second;
  // close up (or with no nav grid) it is a straight step as before
  seek(e, tx, tz, dt, step, scale = 1) {
    const a = e.a, big = (e.D.scale || 1) > 1;
    // big foes plan on their own nav grid with clearance for their hitbox (built once per area, on first need)
    if (big && this.ctx.nav && this.ctx.collide && !this.navBig) this.navBig = new this.ctx.nav.constructor(this.ctx.collide, e.D.r);
    const nav = big ? this.navBig : this.ctx.nav;
    if (!nav || Math.hypot(tx - a.x, tz - a.z) < 1.0) { e.path = null; return step(tx - a.x, tz - a.z, scale); }
    e.pathT = (e.pathT || 0) - dt;
    if (!e.path || e.pathT <= 0 || Math.hypot(e.pathGoal[0] - tx, e.pathGoal[1] - tz) > 1.2) {
      e.path = nav.path(a.x, a.z, tx, tz, 20000); e.pathGoal = [tx, tz]; e.pathT = 0.5; e.pathI = 0;
    }
    if (!e.path || !e.path.length) return step(tx - a.x, tz - a.z, scale);
    let wp = e.path[e.pathI];
    while (wp && e.pathI < e.path.length - 1 && Math.hypot(wp[0] - a.x, wp[1] - a.z) < 0.3) wp = e.path[++e.pathI];
    const mv = step(wp[0] - a.x, wp[1] - a.z, scale);
    if (!mv) e.pathT = 0;   // blocked (light, another actor): re-plan next frame
    return mv;
  }
  floatBob(e) { if (e.D.float && e.state !== 'dead') e.a.lift = 0.16 + Math.sin(this.time * 2.6 + e.phase) * 0.07; }
  ping(e) { const a = e.a; if (this.ctx.gamefx && this.ctx.gamefx.meta.effects.quest_bang) { /* reuse nothing: a quick flash says "noticed" */ } a.flashT = 0.08; }
  beginAttack(e) {
    const a = e.a, p = this.ctx.player;
    this.ctx.actors.setFacingFromVec(a, p.x - a.x, p.z - a.z);
    a.act = null;
    this.ctx.actors.act(a, 'attack', { dur: e.D.windup / 0.42 });
    e.state = 'attack'; e.t = 0; e.fired = false;
    const W = e.D.wave;   // the boss: every Nth slam is a rune shockwave, telegraphed by a rune circle under it
    e.waveNow = !!W && ((e.swings = (e.swings || 0) + 1) % W.every === 0);
    if (e.waveNow && this.ctx.effects) {
      this.ctx.effects.spawn('rune_circle', a.x, a.y + 0.02, a.z);
      const W = e.D.wave, n = (e.D.scale || 1) > 1 ? 6 : 0;   // a big boss rings its whole shockwave reach with runes
      for (let i = 0; i < n; i++) { const t = i / n * Math.PI * 2; this.ctx.effects.spawn('rune_circle', a.x + Math.cos(t) * W.r * 0.72, a.y + 0.02, a.z + Math.sin(t) * W.r * 0.72); }
    }
  }
  enemyStrike(e) {
    const ctx = this.ctx, a = e.a, D = e.D, p = ctx.player;
    if (D.ranged) {
      const from = [a.x, a.y + 0.2, a.z + 0.05], to = [p.x, p.y, p.z];
      // aim a little ahead of a walking player, then fly past the aim point so a dodge is a real dodge
      const ddx = to[0] - from[0], ddz = to[2] - from[2], L = Math.hypot(ddx, ddz) || 1, reach = Math.min(D.reach, L + 2.5);
      const tx = from[0] + ddx / L * reach, tz = from[2] + ddz / L * reach;
      const f = ctx.effects && ctx.effects.spawn(D.bolt || 'coldfire_bolt', from[0], from[1], from[2], { to: [tx, ctx.heightAt(tx, tz), tz] });
      if (f) this.projs.push({ f, owner: 'enemy', dmg: D.dmg, r: 0.55, src: a });
      return;
    }
    const fv = FV[a.facing] || [0, 1];
    const dx = p.x - a.x, dz = p.z - a.z, d = Math.hypot(dx, dz) || 1;
    if ((e.a.role === 'golem' || D.slam) && ctx.particles) {   // the slam kicks up dust where the fists land
      const k = D.scale || 1, sx = a.x + fv[0] * 0.9 * k, sz = a.z + fv[1] * 0.9 * k;
      for (let i = 0; i < 3 * k; i++) ctx.burst('footstep_dust', sx + (i - 1) * 0.3 * k / 1.5, a.y + 0.05, sz + 0.05);
    }
    if (e.waveNow) {   // rune shockwave: a ring all round the boss (dodge-roll through it, or be out of range)
      const W = D.wave;
      if (ctx.effects) { ctx.effects.spawn('rune_slam', a.x, a.y + 0.03, a.z); ctx.effects.spawn('earth_burst', a.x, a.y, a.z + 0.05); }
      if (this.G.glow) this.G.glow.pool(a.x, a.z, D.glow || '#f2a63a', 1.4);
      if (d <= W.r && Math.abs(p.y - a.y) < 1.0) this.hurtPlayer(W.dmg, a, 0.6);
      return;
    }
    if (d <= D.reach + 0.3 && (fv[0] * dx + fv[1] * dz) / d > 0.25 && this.hurtPlayer(D.dmg, a, D.push) && D.chill) {
      this.st = Math.max(0, this.st - D.chill); this.stT = PLAYER.regenDelay;   // frost golem: the cold saps your stamina
      if (ctx.effects) ctx.effects.spawn('frost_puff', p.x, p.y + 0.4, p.z + 0.05);
      this.G.toast && !this.chillTold && (this.chillTold = true, this.G.toast(D.chillMsg || 'Chilled! The frost golem saps your stamina.', 2));
    }
  }
  damageEnemy(e, dmg, src, push = 0.35, color = PAL.white) {
    if (e.state === 'dead' || e.state === 'gone') return false;
    const ctx = this.ctx, a = e.a;
    e.hp -= dmg;
    a.flashT = 0.12;
    this.number(dmg, a.x, a.y + (e.D.float ? 2.1 : 1.9), a.z, color);
    if (ctx.effects) ctx.effects.spawn('hit_spark', a.x, a.y + (e.a.lift || 0), a.z + 0.1);
    this.G.audio.sfx('hit');
    if (push && src) this.shove(a, a.x - src.x, a.z - src.z, push * (e.a.role === 'golem' || e.D.heavy ? (e.D.boss ? 0.15 : 0.35) : 1));
    if (!this.peace && (e.state === 'idle' || e.state === 'home')) e.state = 'chase';
    if (e.hp <= 0) this.kill(e);
    return true;
  }
  kill(e, quiet = false) {
    const ctx = this.ctx, a = e.a;
    e.state = 'dead'; e.t = 0; a.act = null;
    if (!quiet) {
      this.G.audio.sfx('defeat');
      if (ctx.effects) ctx.effects.spawn(a.role === 'wraith' ? 'glyph_burst' : 'impact', a.x, a.y, a.z + 0.05);
      this.defeated[this.area + ':' + e.id] = e.D.respawn || RESPAWN;
      if (e.D.boss) { this.G.toast && this.G.toast(`${e.D.name} falls! Its heart-light spills out as a Legendary.`, 3.2); this.G.S.bosses = { ...(this.G.S.bosses || {}), [e.id]: (this.G.S.bosses?.[e.id] || 0) + 1 }; }
      this.G.stats = this.G.stats || { defeated: 0 };
      this.G.stats.defeated++;
      if (!e.sp.noXp && this.G.gainXP) {
        const seen = (this.G.S.bestiary = this.G.S.bestiary || {});
        const first = !seen[a.role]; seen[a.role] = (seen[a.role] || 0) + 1;
        this.G.gainXP(Math.round((XP[a.role] || 25) * (first ? 1 + XP.firstKill : 1)), a);
      }
      if (this.G.loot && !e.sp.noLoot) this.G.loot.onKill(a, this.G.S.lv || 1, { legendary: !!e.D.legendary, gold: e.D.boss ? 30 : 0 });
    } else e.t = 1.5;
  }
  shove(a, dx, dz, m) {
    const ctx = this.ctx, L = Math.hypot(dx, dz) || 1;
    if (!ctx.collide) { a.x += dx / L * m; a.z += dz / L * m; return; }
    const [nx, nz, nh] = ctx.collide.move(a.x, a.z, a.y, dx / L * m, dz / L * m, a.r);
    a.x = nx; a.z = nz; a.y = nh;
  }

  // ---------------------------------------------------------------- the player
  hurtPlayer(dmg, src, push = 0.3) {
    const ctx = this.ctx, p = ctx.player, G = this.G;
    if (G.downed || this.godT > 0 || p.iframes > 0) return false;
    dmg *= (MODES[G.S.mode] || MODES.adventurer).hurt;   // Story / Adventurer / Hero
    const fv = FV[p.facing] || [0, 1];
    const dx = src.x - p.x, dz = src.z - p.z, d = Math.hypot(dx, dz) || 1;
    let guarded = false;
    if (p.act && p.act.name === 'defend' && (fv[0] * dx + fv[1] * dz) / d > 0.15) {
      guarded = true;
      dmg = Math.max(1, Math.round(dmg * (this.hero.guard ?? PLAYER.guardMul) * this.M.guardMul));
      this.st -= (6 + dmg * 1.5) * this.M.guardSt; this.stT = PLAYER.regenDelay;
      if (ctx.effects) ctx.effects.spawn('hit_spark', p.x + fv[0] * 0.3, p.y, p.z + fv[1] * 0.3 + 0.1);
      G.audio.sfx('guard');
      if (this.st <= 0) { this.st = 0; ctx.release('defend'); G.toast('Guard broken!', 1.2); }
    } else G.audio.sfx('hurt');
    G.S.hp = Math.max(0, G.S.hp - dmg);
    p.flashT = 0.15; p.iframes = PLAYER.hitIframes;
    this.number(dmg, p.x, p.y + 2.0, p.z, guarded ? PAL.sky : PAL.rose);
    this.shove(p, -dx, -dz, guarded ? push * 0.4 : push);
    if (G.S.hp <= 0) this.down();
    return true;
  }
  heal(n, raw = false) {
    const p = this.ctx.player;
    const was = this.G.S.hp;
    this.G.S.hp = Math.min(this.maxHp(), this.G.S.hp + n * (raw ? 1 : this.M.healMul));
    if (this.G.S.hp > was) this.number('+' + Math.round(this.G.S.hp - was), p.x, p.y + 2.0, p.z, PAL.green);
  }
  // cozy defeat: you slump, the screen warms to dark, you wake at the area's start with everything you had
  down() {
    const ctx = this.ctx, p = ctx.player, G = this.G;
    G.downed = true; p.act = null; p.roll = null; p.rot = 1; walkStop(ctx);
    G.audio.sfx('down');
    // faint penalty (not in Story): 10% of carried gold drops where you fell, as a purse you can walk back to
    const md = MODES[G.S.mode] || MODES.adventurer;
    let lost = 0;
    if (md.penalty && (G.S.gold || 0) > 0) {
      lost = Math.max(1, Math.ceil(G.S.gold * md.penalty));
      G.S.gold -= lost;
      const prev = G.S.purse && G.S.purse.area === this.area ? G.S.purse.gold : 0;   // one purse per area: they stack
      if (prev && G.loot) G.loot.removePurse();
      G.S.purse = { area: this.area, x: +p.x.toFixed(2), z: +p.z.toFixed(2), gold: lost + prev };
      if (G.loot) G.loot.drop(p.x, p.z, { gold: lost + prev, purse: true });
      if (G.drawBag) G.drawBag();
    }
    const f = document.getElementById('fade');
    setTimeout(() => { f.className = 'on'; }, 900);
    setTimeout(() => {
      if (this.ctx !== ctx) return;
      const s = (ctx.scene.game?.spawns || {}).start;
      if (s) { p.x = s[0]; p.z = s[1]; p.y = ctx.heightAt(s[0], s[1]); p.facing = s[2] || 'down'; }
      p.rot = 0; G.S.hp = this.maxHp(); this.st = this.maxSt();
      for (const e of this.alive()) { e.state = 'idle'; e.hp = e.D.hp; e.a.act = null; e.a.x = e.home[0]; e.a.z = e.home[1]; e.a.y = ctx.heightAt(e.home[0], e.home[1]); }
      this.godT = PLAYER.respawnIframes; G.downed = false;
      f.className = '';
      G.toast(lost ? `You wake by the gate. You dropped ${lost} gold where you fell: go get it back.` : 'You wake by the gate, warm and whole. Nothing lost.', 3.4);
    }, 1700);
  }
  meleeHit() {
    const ctx = this.ctx, p = ctx.player, m = this.hero.melee, fv = FV[p.facing] || [0, 1];
    let hit = 0;
    for (const e of this.alive()) {
      const a = e.a, dx = a.x - p.x, dz = a.z - p.z, d = Math.hypot(dx, dz);
      if (d > m.reach + e.D.r || Math.abs(a.y - p.y) > 1.0) continue;
      if (d > 0.45 && (fv[0] * dx + fv[1] * dz) / d < PLAYER.arc - this.M.arc) continue;
      const dmg = this.out('melee', m.dmg);
      if (this.damageEnemy(e, dmg, p, 0.45, this.lastCrit ? PAL.gold : PAL.white)) { hit++; if (this.M.drain) this.heal(dmg * this.M.drain, true); }
    }
    if (this.summon) hit += 0;   // never hits your own summon
    if (!hit) this.G.audio.sfx('swing');
    return hit;
  }
  onAct(name) {
    if (name === 'attack') { this.st = Math.max(0, this.st - PLAYER.atkCost); this.stT = 0.35; }
  }
  onDodge() {
    if (this.G.downed) return false;
    if (this.st < PLAYER.dodgeCost) { this.tired(); return false; }
    this.st -= PLAYER.dodgeCost; this.stT = PLAYER.regenDelay;
    this.G.audio.sfx('dodge');
    return true;
  }
  tired() { const v = document.getElementById('vitals'); if (v) { v.classList.remove('tired'); void v.offsetWidth; v.classList.add('tired'); } }
  nearestEnemy(from, maxd, skip = []) {
    let best = null, bd = maxd;
    for (const e of this.alive()) { if (skip.includes(e)) continue; const d = dist(e.a, from); if (d < bd) { bd = d; best = e; } }
    return best;
  }

  // ---------------------------------------------------------------- spells (hooks.onCast: false = the engine draws nothing)
  cast(name) {
    const ctx = this.ctx, p = ctx.player, G = this.G;
    if (!ctx || G.downed) return false;
    const S = SPELLS[name];
    if (!S) {                                            // a charm: the engine draws it, it nips whatever is in front
      if (this.cd.charm > 0) return false;
      this.cd.charm = CHARM_CD;
      { const fv = FV[p.facing] || [0, 1], gl = this.G.glow; if (gl) gl.pool(p.x + fv[0] * 0.95, p.z + fv[1] * 0.95, gl.colorOf(name), 0.8); }
      const dmg = CHARM_DMG[name] ?? 6;
      if (name === 'healing_petals') this.later.push({ t: 0.3, fn: () => this.heal(12) });
      if (dmg) this.later.push({ t: 0.18, fn: () => {
        const fv = FV[p.facing] || [0, 1], cx = p.x + fv[0] * 1.2, cz = p.z + fv[1] * 1.2;
        for (const e of this.alive()) if (Math.hypot(e.a.x - cx, e.a.z - cz) < 1.5) this.damageEnemy(e, this.out('spell', dmg), p, 0.25, PAL.gold);
      } });
      return true;
    }
    if (this.cd.spell > 0) { this.tired(); return false; }
    this.cd.spell = S.cd * (1 - Math.min(0.5, this.M.spellCd || 0));   // tier II / III skills shorten spell cooldowns
    // auto-face the nearest foe (4-way facing) so a quick tap aims where you mean
    const tgt = this.nearestEnemy(p, 7);
    if (tgt && !p.act) ctx.actors.setFacingFromVec(p, tgt.a.x - p.x, tgt.a.z - p.z);
    if (!p.act) p.castT = p.castDur;
    G.audio.sfx('spell');
    const fv = FV[p.facing] || [0, 1], fx = ctx.effects;
    if (!fx) return false;
    if (S.kind === 'projectile' || S.kind === 'pierce') {
      const travel = fx.meta.effects[S.fx].travel || 4.5;
      const tx = p.x + fv[0] * travel, tz = p.z + fv[1] * travel;
      const proj = { owner: 'player', spell: name, S, hitSet: new Set() };
      proj.f = fx.spawn(S.fx, p.x + fv[0] * 0.4, p.y, p.z + fv[1] * 0.4 + 0.05,
                        { to: [tx, ctx.heightAt(tx, tz), tz], onDone: (f) => { if (S.kind === 'projectile' && !proj.done) this.burst(proj, f.x, f.z); proj.done = true; if (S.kind === 'pierce' && this.G.glow) this.G.glow.pool(f.x, f.z, this.G.glow.colorOf(S.fx)); } });
      this.projs.push(proj);
    } else if (S.kind === 'nova') {
      fx.spawn('rune_slam', p.x, p.y, p.z + 0.05); fx.spawn('impact', p.x, p.y, p.z + 0.06);
      if (this.G.glow) this.G.glow.pool(p.x, p.z, this.G.glow.colorOf('rune_slam'), 1.2);
      for (const e of this.alive()) if (dist(e.a, p) < S.radius + e.D.r) this.damageEnemy(e, this.out('spell', S.dmg), p, S.push, PAL.gold);
    } else if (S.kind === 'trap') {
      const x = p.x + fv[0] * 1.7, z = p.z + fv[1] * 1.7, y = ctx.heightAt(x, z);
      fx.spawn('rune_trap', x, y, z + 0.02);
      this.traps.push({ x, y, z, t: 0, S, armed: null });
      if (this.G.glow) this.G.glow.pool(x, z, this.G.glow.colorOf('rune_trap'));
    } else if (S.kind === 'chain') {
      let from = p, hitList = [], t = 0;
      for (let i = 0; i <= S.jumps + this.M.chainJumps; i++) {
        const e = this.nearestEnemy(from, i === 0 ? S.range : S.hop, hitList);
        if (!e) break;
        hitList.push(e);
        const dmg = this.out('spell', S.dmg * Math.pow(0.75, i));
        this.later.push({ t, fn: () => { if (e.state !== 'dead' && e.state !== 'gone') { fx.spawn('sky_strike', e.a.x, e.a.y, e.a.z + 0.06); this.damageEnemy(e, dmg, p, 0.2, PAL.gold); if (i === 0 && this.G.glow) this.G.glow.pool(e.a.x, e.a.z, this.G.glow.colorOf('sky_strike')); } } });
        from = e.a; t += 0.16;
      }
      if (!hitList.length) fx.spawn('sky_strike', p.x + fv[0] * 2, ctx.heightAt(p.x + fv[0] * 2, p.z + fv[1] * 2), p.z + fv[1] * 2 + 0.06);
    } else if (S.kind === 'heal') {
      fx.spawn('bloom_ring', p.x, p.y, p.z + 0.05); fx.spawn('healing_petals', p.x, p.y, p.z + 0.06);
      if (this.G.glow) this.G.glow.pool(p.x, p.z, this.G.glow.colorOf('bloom_ring'));
      this.heal(S.heal);
      if (this.summon) this.summon.hp = Math.min(this.summon.D.hp, this.summon.hp + S.heal);
      for (const e of this.alive()) if (dist(e.a, p) < S.radius + e.D.r) this.damageEnemy(e, this.out('spell', S.dmg), p, 0.5, PAL.gold);
    }
    return false;
  }
  burst(proj, x, z) {
    const ctx = this.ctx, S = proj.S;
    if (!proj.small && this.G.glow) this.G.glow.pool(x, z, this.G.glow.colorOf(S.fx === 'seed_bomb' ? 'earth_burst' : S.fx));
    if (!proj.small && S.fx === 'seed_bomb' && this.M.seedSplit) {
      for (let k = 0; k < this.M.seedSplit; k++) {
        const a = k * Math.PI + 0.7, sx = x + Math.cos(a) * 1.1, sz = z + Math.sin(a) * 0.8;
        this.later.push({ t: 0.15 + 0.1 * k, fn: () => this.burst({ S, small: true }, sx, sz) });
      }
    }
    if (S.burst && ctx.effects) ctx.effects.spawn(S.burst, x, ctx.heightAt(x, z), z + 0.05);
    for (const e of this.alive()) if (Math.hypot(e.a.x - x, e.a.z - z) < S.radius + e.D.r) this.damageEnemy(e, this.out('spell', S.dmg * (proj.small ? 0.5 : 1)), { x, z }, 0.4, PAL.gold);
  }
  updateProjs() {
    const ctx = this.ctx, p = ctx.player;
    for (const pr of this.projs) {
      const f = pr.f;
      if (!f || pr.done || !ctx.effects.list.includes(f)) { pr.done = true; continue; }
      if (pr.owner === 'enemy') {
        if (Math.hypot(f.x - p.x, f.z - p.z) < pr.r && !this.G.downed) {
          if (this.hurtPlayer(pr.dmg, { x: f.x, z: f.z }, 0.35) || p.act?.name === 'defend') { ctx.effects.remove(f); ctx.effects.spawn('frost_puff', f.x, f.y - 0.6, f.z); pr.done = true; }
        }
        // a summon in the way takes the bolt
        const s = this.summon;
        if (!pr.done && s && Math.hypot(f.x - s.a.x, f.z - s.a.z) < 0.5) { ctx.effects.remove(f); ctx.effects.spawn('frost_puff', f.x, f.y - 0.6, f.z); pr.done = true; this.hurtSummon(pr.dmg); }
        continue;
      }
      for (const e of this.alive()) {
        if (pr.hitSet.has(e) || Math.hypot(e.a.x - f.x, e.a.z - f.z) > 0.6 + e.D.r) continue;
        if (pr.S.kind === 'pierce') { pr.hitSet.add(e); this.damageEnemy(e, this.out('spell', pr.S.dmg), f, 0.5, PAL.gold); }
        else { ctx.effects.remove(f); this.burst(pr, f.x, f.z); pr.done = true; break; }
      }
    }
    this.projs = this.projs.filter((pr) => !pr.done);
  }
  updateTraps(dt) {
    const ctx = this.ctx;
    for (const tr of this.traps) {
      tr.t += dt;
      if (!tr.armed && tr.t >= tr.S.arm) tr.armed = ctx.effects.spawn('rune_trap', tr.x, tr.y, tr.z + 0.02, { frame: 5 });
      if (!tr.armed) continue;
      const near = this.alive().some((e) => Math.hypot(e.a.x - tr.x, e.a.z - tr.z) < 1.1 + e.D.r);
      if (near || tr.t > tr.S.life) {
        ctx.effects.remove(tr.armed);
        ctx.effects.spawn('glyph_burst', tr.x, tr.y, tr.z + 0.04);
        if (near) for (const e of this.alive()) if (Math.hypot(e.a.x - tr.x, e.a.z - tr.z) < tr.S.radius * this.M.trapRadius + e.D.r) { this.damageEnemy(e, this.out('spell', tr.S.dmg), tr, 0.3, PAL.gold); e.cd = Math.max(e.cd, 1.6); }
        tr.done = true;
      }
    }
    this.traps = this.traps.filter((t) => !t.done);
  }

  // ---------------------------------------------------------------- summons (a tiny friend from the hero's background)
  doSummon() {
    const ctx = this.ctx, p = ctx.player, G = this.G;
    if (!ctx || G.downed) return false;
    if (this.cd.summon > 0) { this.tired(); return false; }
    const base = this.hero.summon, D = SUMMONS[base];
    if (!ctx.actors.meta.roles[base]) return false;
    if (this.summon) this.unsummon();
    const tier = summonTier(G.S), roles = ctx.actors.meta.roles;
    const role = tier >= 3 && roles[base + '_r'] ? base + '_r' : base;
    const fv = FV[p.facing] || [0, 1];
    const name = tier > 1 ? `${D.name} ${ROMAN[tier]}` : D.name;
    const a = ctx.addNpc({ id: 'summon', role, name, pos: [p.x + fv[0] * 0.9 + 0.3, p.z + fv[1] * 0.9], behavior: 'idle', turn: false, speed: D.speed });
    a.ai = true; a.noTalk = true; a.facing = p.facing;
    this.summon = { a, tier, D: { ...D, hp: Math.round(D.hp * this.M.summonMul) }, hp: Math.round(D.hp * this.M.summonMul), life: SUMMON_LIFE + this.M.summonLife, cd: 0.4, target: null, sparkT: 0.3 };
    if (tier >= 2 && ctx.addGlow) this.summon.light = ctx.addGlow(a.x, a.y, a.z, { color: SUMMON_GLOW[base] || '#f2c24a', intensity: tier >= 4 ? 6 : tier >= 3 ? 4.5 : 3, range: tier >= 4 ? 3.6 : tier >= 3 ? 3.0 : 2.4, lift: 0.8, fadeIn: 0.4 });
    if (tier >= 3 && ctx.effects) ctx.effects.spawn('rune_circle', a.x, a.y + 0.02, a.z);
    if (tier >= 4 && ctx.effects) ctx.effects.spawn('sparkle_burst', a.x, a.y, a.z + 0.06);
    this.cd.summon = SUMMON_CD * (1 - Math.min(0.5, this.M.summonCd || 0));
    if (ctx.effects) ctx.effects.spawn('summon_poof', a.x, a.y, a.z + 0.05);
    G.audio.sfx('summon');
    G.toast(`${name} answers your call!`, 1.6);
    return true;
  }
  hurtSummon(dmg) {
    const s = this.summon; if (!s) return;
    s.hp -= dmg; s.a.flashT = 0.12;
    this.number(dmg, s.a.x, s.a.y + 1.3, s.a.z, PAL.rose);
    if (s.hp <= 0) this.unsummon();
  }
  unsummon() {
    const s = this.summon; if (!s) return;
    if (this.ctx.effects) this.ctx.effects.spawn('summon_poof', s.a.x, s.a.y, s.a.z + 0.05);
    if (s.light) s.light.kill = true;
    this.ctx.removeNpc(s.a);
    this.summon = null;
  }
  updateSummon(dt, frozen) {
    const s = this.summon, ctx = this.ctx; if (!s) return;
    const a = s.a, p = ctx.player, D = s.D;
    s.life -= frozen ? 0 : dt;
    if (s.life <= 0) { this.unsummon(); return; }
    let moving = false;
    if (!frozen) {
      s.cd -= dt;
      if (!s.target || s.target.state === 'dead' || s.target.state === 'gone' || dist(s.target.a, a) > 7) s.target = this.nearestEnemy(a, 5);
      const e = s.target;
      if (e) {
        const dx = e.a.x - a.x, dz = e.a.z - a.z, d = Math.hypot(dx, dz);
        if (d > D.reach * 0.85) moving = ctx.moveActor(a, dx, dz, dt);
        else {
          ctx.actors.setFacingFromVec(a, dx, dz);
          if (s.cd <= 0 && !a.act) {
            ctx.actors.act(a, 'attack', { dur: 0.5 }); s.cd = 1.0;
            this.later.push({ t: 0.22, fn: () => { if (this.summon === s && e.state !== 'dead' && e.state !== 'gone') {
              if (D.ranged && ctx.effects) ctx.effects.spawn('hit_spark', e.a.x, e.a.y + 0.4, e.a.z + 0.1);
              this.damageEnemy(e, this.out('summon', D.dmg), a, 0.25, PAL.green);
            } } });
          }
        }
      } else {
        const dx = p.x - a.x, dz = p.z - a.z, d = Math.hypot(dx, dz);
        if (d > 6) { a.x = p.x + 0.6; a.z = p.z + 0.4; a.y = p.y; }
        else if (d > 1.2) moving = ctx.moveActor(a, dx, dz, dt * (d > 3 ? 1.4 : 1));
      }
    }
    ctx.actors.animate(a, dt, moving && !a.act);
    if (s.life < 2) a.quad.visible = Math.floor(s.life * 10) % 2 === 0;
    if (s.light) { s.light.pos.set(a.x, a.y, a.z); s.light.scale = a.quad.visible ? 1 : 0.4; }
    if (s.tier >= 2 && ctx.effects && !frozen && (s.sparkT -= dt) <= 0) {   // glowing tiers shed little sparkles as they go
      s.sparkT = s.tier >= 4 ? 0.7 : s.tier >= 3 ? 1.0 : 1.5;
      ctx.effects.spawn('glitter', a.x + (Math.random() - 0.5) * 0.5, a.y, a.z + 0.08, { duration: 1.2 });
    }
  }

  // ---------------------------------------------------------------- crisp DOM numbers + little health bars
  number(n, x, y, z, color) {
    if (!this.layer) return;
    const scale = Math.max(2, Math.min(4, Math.round((this.ctx.pixelK ? this.ctx.pixelK() : 3) / (window.devicePixelRatio || 1) * 1.5) || 3));
    const el = pixelText(String(typeof n === 'number' ? Math.round(n) : n), color, scale);
    el.className = 'dmgnum';
    this.layer.appendChild(el);
    this.nums.push({ el, x, y, z, t: 0, dx: (Math.random() - 0.5) * 0.4 });
  }
  updateDom(dt) {
    const ctx = this.ctx;
    for (const n of this.nums) {
      n.t += dt;
      const s = ctx.project(n.x + n.dx * n.t, n.y + n.t * 0.9, n.z);
      n.el.style.transform = `translate(${Math.round(s.x - n.el.width / 2)}px, ${Math.round(s.y - n.el.height)}px)`;
      if (n.t > 0.6) n.el.style.visibility = Math.floor(n.t * 14) % 2 ? 'hidden' : 'visible';
      if (n.t > 0.9) { n.el.remove(); n.done = true; }
    }
    this.nums = this.nums.filter((n) => !n.done);
    // camera framing scales with big foes: breathe the camera out while one is engaged and near (eased in the engine)
    let pullF = 1;
    for (const e of this.enemies) {
      const k = e.D.scale || 1;
      if (k > 1 && (e.state === 'chase' || e.state === 'attack') && dist(e.a, ctx.player) < (e.D.aggro || 6) + 3) pullF = Math.max(pullF, 1 + (k - 1) * 0.12);
    }
    if (ctx.framePull) ctx.framePull(pullF);
    for (const e of this.enemies) {
      let b = this.bars.get(e.id);
      const show = (e.hp < e.D.hp || e.state === 'chase' || e.state === 'attack') && e.state !== 'dead' && e.state !== 'gone';
      if (e.light) e.light.pos.set(e.a.x, e.a.y, e.a.z);
      if (!show) { if (b) b.hidden = true; if (e.D.boss && this.bossEl) this.bossEl.hidden = true; continue; }
      if (!b) { b = document.createElement('div'); b.className = 'ebar'; b.innerHTML = '<i></i>'; this.layer.appendChild(b); this.bars.set(e.id, b); }
      b.hidden = false;
      if (e.light) e.light.pos.set(e.a.x, e.a.y, e.a.z);
      if (e.D.boss) { this.bossBar(e); b.hidden = true; continue; }
      const s = ctx.project(e.a.x, e.a.y + (e.a.lift || 0) + (e.a.role === 'golem' || e.D.slam ? 1.75 : 1.85) * (e.D.scale || 1), e.a.z);
      b.style.transform = `translate(${Math.round(s.x - 15)}px, ${Math.round(s.y)}px)`;
      b.firstChild.style.width = Math.max(0, Math.round(26 * e.hp / e.D.hp)) + 'px';
    }
  }
  // the mini-boss gets a named parchment bar at the top of the screen instead of a little world bar
  bossBar(e) {
    if (!this.bossEl) {
      const el = document.createElement('div'); el.id = 'bossbar'; el.innerHTML = '<b></b><span><i></i></span>';
      (document.getElementById('hud') || document.body).appendChild(el); this.bossEl = el;
    }
    const el = this.bossEl; el.hidden = false;
    el.firstChild.textContent = e.D.name;
    el.querySelector('i').style.width = Math.max(0, Math.round(100 * e.hp / e.D.hp)) + '%';
  }
  // QA helpers
  qa() {
    return { hp: this.G.S.hp, max: this.maxHp(), st: Math.round(this.st), cd: { ...this.cd }, god: this.godT,
             enemies: this.enemies.map((e) => ({ id: e.id, role: e.a.role, hp: e.hp, state: e.state, x: +e.a.x.toFixed(2), z: +e.a.z.toFixed(2) })),
             summon: this.summon ? { role: this.summon.a.role, hp: this.summon.hp, life: +this.summon.life.toFixed(1), tier: this.summon.tier, light: !!this.summon.light, name: this.summon.a.name } : null };
  }
}
function walkStop(ctx) { ctx.stopWalk && ctx.stopWalk(); }
