// Hearthmoor combat core (stage 1): real-time hits, guard, dodge i-frames, stamina, hero spells + summons,
// three enemies with simple AI, crisp pixel damage numbers, cozy defeat (wake up, nothing lost).
// Visuals come from the engine (sprites, spells atlas); this file only decides who gets hit and how hard.
import { mods as progMods, XP, addXP, MODES, summonTier } from './progress.js';
import { HERO, SPELLS, CHARM_DMG, CHARM_CD, SUMMONS, SUMMON_LIFE, SUMMON_CD, ENEMIES, RESPAWN, LEASH, SPAWNS, PLAYER } from './heroes.js';
import { CAPS, PROCS, SCHOOL_OF } from './loot.js';   // gearfx: caps, proc table, element -> school

// summon tiers (Part 4): I base, II glows (a following light + sparkles), III radiant form (lit rim, crown of light,
// sparkles; '<role>_r' sprite) + a rune circle on arrival, IV (capstone) brighter and wider light + a sparkle burst.
// Stats grow through the summon-branch skills (summonMul / summonLife). Gloom-and-glow: palette pixels, no bloom.
// [JOTUNHEIM] Stonefrost II / III (Solvi's lessons; flags sf_ii / sf_iii). The art is the gamefx atlas rows jot_art.py appends (48 px cells).
const STONE = {
  2: { cast: 'stonefrost_cast_ii', bolt: 'stonefrost_bolt_ii', hit: 'stonefrost_impact_ii', rune: 'stonefrost_rune_ii', burst: 'stonefrost_burst_ii', mul: 1.3, rad: 1.15 },
  3: { cast: 'stonefrost_cast_iii', bolt: 'stonefrost_bolt_iii', hit: 'stonefrost_impact_iii', rune: 'stonefrost_rune_iii', burst: 'stonefrost_burst_iii', mul: 1.6, rad: 1.3 },
};
const COLD_BLUE = '#7fd4ff', COLD_R = 2.2, GOLEM = { name: 'Stone golem', hp: 90, dmg: 14, reach: 1.4, speed: 1.9 };
const GOLEM_ROLES = ['golem', 'eldergolem', 'icegolem', 'mushgolem'];   // first one this area's actor atlas has
// [MUSPELHEIM-2] the Caldera school (Torka's lessons; flags cs_i / cs_ii / cs_iii). Art: the gamefx rows musp_art.school appends (48 px cells; the
// Muspelheim areas carry the pack's five from mp_fx), fire_wave_l / _u / _d and ember_mote are derived there. Neon-orange fire against the dark.
const LAVA = '#ff7a1a', HOT = '#ffd27a';
const HOUND = { name: 'Magma hound', hp: 110, dmg: 13, reach: 1.4, speed: 2.6 };
const HOUND_ROLES = ['magma_hound'];
const SCHOOL_KIND = { root: 'nature', golem: 'nature', skin: 'nature', hound: 'nature', nova: 'light', chain: 'light', ward: 'light', spirits: 'dark', veil: 'dark', swarm: 'dark' };
const spellSfx = (S) => { const sc = S.school || SCHOOL_KIND[S.kind]; return sc ? 'spell_' + sc : 'spell'; };
// [HMFX48] cast flourishes from the shared hm_fx48 atlas, GD order: blue -> violet -> flame_blue (names matched to the Frostweave / Cold Fire spells)
const HMFX_CAST = { lance: 'spell_cast_blue', fnova: 'impact_blue', igolem: 'portal_blue',   // blue
  veil: 'buff_aura_violet', spirits: 'wisps_violet',                                          // violet
  coldfire: 'flame_blue' };                                                                    // flame_blue (the cold fire)
// [HMFX48] school casts the first pass left alone: fire/Caldera, nature, dark/gloam
const HMFX_CAST2 = { firewave: 'spell_cast_fire', magma: 'spell_cast_fire', swarm: 'spell_cast_fire', hound: 'spell_cast_fire', pierce: 'spell_cast_fire', // [HMFX48]
  'nature:hound': 'spell_cast_green', 'nature:root': 'spell_cast_green', golem: 'spell_cast_green', projectile: 'spell_cast_green', // [HMFX48]
  veil: 'spell_cast_violet', spirits: 'spell_cast_violet' }; // [HMFX48]
const HMFX_IMPACT = { fire: 'impact_fire', nature: 'impact_green', dark: 'impact_violet' }; // [HMFX48] impacts by element
const HMFX_FLASH = { fire: 'hit_flash_fire', frost: 'hit_flash_blue', light: 'hit_flash_blue', dark: 'hit_flash_violet' }; // [HMFX48] hit flashes: fire, frost/light, dark
const HMFX_BOLT = { lance: 'magic_bolt_blue', pierce: 'magic_bolt_fire', spirits: 'magic_bolt_violet' }; // [HMFX48] frost / fire / dark bolts
const HMFX_ZAP = { chain: 'lightning_blue' }; // [HMFX48] chain lightning
const HMFX_HEAL = { heal: 'heal_aura_green' }; // [HMFX48] bloom
const HMFX_BUFF = { skin: 'buff_aura_gold', ward: 'buff_aura_gold' }; // [HMFX48] stone skin and flame ward
const HOUND_LOOK = { magma_hound: { name: 'Magma hound', color: null, toast: 'A Magma Hound shakes itself out of the lava!' },
  moss_golem: { name: 'Moss Golem', color: 0x7cff9a, toast: 'A Moss Golem heaves itself up out of the loam!' } };   // the realm's own hound sheet (every Muspelheim area carries it); elsewhere no hound answers
const WAVE_FX = { right: 'fire_wave', left: 'fire_wave_l', up: 'fire_wave_u', down: 'fire_wave_d' };
// [NIFLHEIM-2] the Frostweave school (Gudrun's lessons; flags fw_i / fw_ii / fw_iii). Art: the Niflheim pack's own nf_fx rows (ice_lance, frost_nova, mist_veil,
// spirit_swarm, snow_puff) where an area's game-fx atlas carries them (the six Niflheim areas), else the stock spells atlas (coldfire_bolt, frost_puff, coldfire_motes, summon_poof).
const FROST = '#a6ecff';
const ICEGOLEM = { name: 'Ice golem', hp: 100, dmg: 15, reach: 1.4, speed: 1.8 };
const ICEGOLEM_ROLES = ['ice_golem', 'icegolem', 'golem', 'eldergolem'];   // the realm's own ice golem first (Niflheim areas), else the stock frost golem / stone golem looks

const SUMMON_GLOW = { mushgolem: '#f2c24a', runesentinel: '#ffb24a', runewisp: '#94c0dc', stormsprite: '#94c0dc', sapling: '#b2c464', emberimp: '#ffb24a' };
// 6.4: camera framing for big foes: 2.5x Glenheart pulls ~1.18 (unchanged); 5-6x bosses pull ~1.7-1.9;
// 7x / 8x (Hrimgard, Aurelion, Vharzul) need past the old 2.0 cap or the head sits on the canvas lip
export const framePullFor = (k) => (k >= 4 ? Math.min(2.4, 1 + (k - 1) * 0.18) : 1 + (k - 1) * 0.12);
// Mordrath opts in with frameFit. The numeric frameLift is the floor (clears the pin). Past ~5.6 m north of
// the ossuary aim (hero.z - 2.4, clamped to the scene), the crown needs +0.7 m of lift per extra metre.
// Hard max 9. Pull is unchanged. Foes without frameFit never reach this.
const FRAME_LIFT_MAX = 9;
export function frameLiftFor(def, hero, boss) {
  const base = def && def.frameLift > 0 ? def.frameLift : 0;
  if (!def || !def.frameFit || !hero || !boss) return base;
  const az = Math.min(12, Math.max(-48, hero.z - 2.4));
  const north = az - boss.z;
  const need = 0.7 * north - 1.87;
  return Math.min(FRAME_LIFT_MAX, Math.max(base, need));
}
// Nameplate opt-in. Mordrath's crown sits in the top band, so his bar docks low. Every other boss and rare stays up top.
export const bossBarLow = (def) => !!(def && def.barLow);
// 6.4 trial mode: ENEMIES[x].trial = true or (S) => bool (Hjortur yields on the befriend path); a spawn can set sp.trial
export const isTrial = (e, S) => { const t = (e.sp && e.sp.trial) ?? e.D.trial; return typeof t === 'function' ? !!t(S) : !!t; };
const ROMAN = ['', 'I', 'II', 'III', 'IV'];
const PAL = { ink: '#2a1e1c', white: '#fff8e6', gold: '#f2c24a', rose: '#e47c8c', green: '#b2c464', sky: '#94c0dc' };
const GREY = '#b7b1a6';   // gearfx: Dodged (no grey in PAL)
const PROC_WORD = { lifeSteal: 'Leech', fireBolt: 'Bolt', freeze: 'Freeze', root: 'Root', heal: 'Heal', damageShield: 'Thorns', runeShield: 'Rune' };
const PROC_COL = { lifeSteal: PAL.rose, fireBolt: PAL.gold, freeze: PAL.sky, root: PAL.green, heal: PAL.green, damageShield: PAL.gold, runeShield: PAL.sky };
// 3x5 pixel font: digits, + and - (drawn at an integer scale with a 1 px ink outline, never smoothed)
const GLYPH = {
  0: ['111', '101', '101', '101', '111'], 1: ['010', '110', '010', '010', '111'], 2: ['111', '001', '111', '100', '111'],
  3: ['111', '001', '011', '001', '111'], 4: ['101', '101', '111', '001', '001'], 5: ['111', '100', '111', '001', '111'],
  6: ['111', '100', '111', '101', '111'], 7: ['111', '001', '010', '010', '010'], 8: ['111', '101', '111', '101', '111'],
  9: ['111', '101', '111', '001', '111'], '+': ['000', '010', '111', '010', '000'], '-': ['000', '000', '111', '000', '000'],
  A: ['010', '101', '111', '101', '101'], B: ['110', '101', '110', '101', '110'], C: ['111', '100', '100', '100', '111'],
  D: ['110', '101', '101', '101', '110'], E: ['111', '100', '110', '100', '111'], F: ['111', '100', '110', '100', '100'],
  G: ['111', '100', '101', '101', '011'], H: ['101', '101', '111', '101', '101'], I: ['111', '010', '010', '010', '111'],
  J: ['001', '001', '001', '101', '010'], K: ['101', '101', '110', '101', '101'], L: ['100', '100', '100', '100', '111'],
  M: ['101', '111', '101', '101', '101'], N: ['101', '111', '111', '101', '101'], O: ['111', '101', '101', '101', '111'],
  P: ['110', '101', '110', '100', '100'], Q: ['111', '101', '101', '111', '001'], R: ['110', '101', '110', '101', '101'],
  S: ['111', '100', '111', '001', '111'], T: ['111', '010', '010', '010', '010'], U: ['101', '101', '101', '101', '111'],
  V: ['101', '101', '101', '101', '010'], W: ['101', '101', '101', '111', '101'], X: ['101', '101', '010', '101', '101'],
  Y: ['101', '101', '010', '010', '010'], Z: ['111', '001', '010', '100', '111'],
};
export function pixelText(str, color, scale = 3) {
  const w = str.length * 4 + 1, h = 7;                 // 3 px glyph + 1 px gap, 1 px outline all round
  const cv = document.createElement('canvas');
  cv.width = w * scale; cv.height = h * scale;
  const g = cv.getContext('2d');
  g.imageSmoothingEnabled = false;
  const on = new Set();
  [...str].forEach((ch, i) => (GLYPH[ch] || GLYPH[ch.toUpperCase()] || []).forEach((row, y) => [...row].forEach((b, x) => { if (b === '1') on.add(`${1 + i * 4 + x},${1 + y}`); })));
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
    this.cd = { spell: 0, charm: 0, summon: 0, skin: 0, cold: 0, golem: 0, swarm: 0, ward: 0, hound: 0, veil: 0, spirits: 0, igolem: 0, root: 0 };   // skin / cold / golem: the long Stonefrost II / III cooldowns, swarm / ward / hound: the Caldera school's (spell = the shared 1 s gap)
    this.skin = null; this.patches = []; this.magma = []; this.motes = []; this.ward = null; this.veil = null; this.spirits = [];
    this.godT = 0;
    this.defeated = {};              // area:id -> game seconds left until it wanders back
    this.time = 0;
    this.procCd = {}; this.dmgShieldT = 0; this.runeAbs = 0; this.runeAbsT = 0; this._procHit = false; this._inProc = false;   // gearfx
    this.gfx = { lastProc: null, procs: 0 };   // gearfx: lastProc + procs fired count
  }
  get hero() { return HERO[this.G.S.cls] || HERO.wildcaller; }
  maxHp() { return this.hero.hp + this.M.hpAdd; }
  maxSt() { return PLAYER.stamina + this.M.stAdd; }
  get M() { return progMods(this.G.S); }
  // outgoing damage: stat / skill multiplier + a crit roll (crits pop bigger, in gold)
  out(kind, base) {
    const M = this.M, mul = kind === 'melee' ? M.meleeMul : kind === 'summon' ? M.summonMul : M.spellMul;
    const crit = kind !== 'summon' && Math.random() < M.crit + ((this.foreUntil || 0) > performance.now() ? 0.05 : 0);   // [VANAHEIM] Foresight Charm
    this.lastCrit = crit;
    const lit = kind !== 'summon' && this.G.glow ? this.G.glow.dmgMul() : 1;   // glowlit: +10%
    const mode = (MODES[this.G.S.mode] || MODES.adventurer).deal;
    const sv = this.G.svart && this.G.svart.tempMul ? this.G.svart.tempMul(kind) : 1;   // [SVARTALFHEIM] Dagna's temper, the Tinker's Heart
    return Math.max(1, Math.round(base * mul * lit * mode * sv * (crit ? 1.5 + (M.critDmg || 0) : 1)));
  }

  // ---------------------------------------------------------------- area lifecycle
  attach(ctx, area) {
    this.ctx = ctx; this.area = area;
    if (ctx && ctx.player) this.bindSpeed(ctx.player);   // gearfx: move bonus on the raw speed, before the first step
    this.enemies = []; this.navBig = null; this.summon = null; this.projs = []; this.traps = []; this.later = []; this.skin = null; this.patches = []; this.magma = []; this.motes = []; this.endWard(); this.endVeil(); this.spirits = [];
    this.clearDom();
    if (this.G.S.hp == null || this.G.S.hp <= 0) this.G.S.hp = this.maxHp();
    this.G.S.hp = Math.min(this.G.S.hp, this.maxHp());
    for (const sp of SPAWNS[area] || []) if (!sp.night && !(this.defeated[area + ':' + sp.id] > 0)) this.spawnEnemy(sp);
  }
  detach() { this.endWard(); this.endVeil(); this.spirits = []; this.clearDom(); this.ctx = null; this.enemies = []; this.navBig = null; this.summon = null; this.magma = []; this.motes = []; }
  clearDom() {
    for (const e of this.enemies || []) if (e.light) e.light.kill = true;
    if (this.bossEl) { this.bossEl.remove(); this.bossEl = null; }
    for (const n of this.nums) n.el.remove();
    for (const b of this.bars.values()) b.remove();
    this.nums = []; this.bars.clear();
  }
  spawnEnemy(sp, poof = false) {
    const ctx = this.ctx, D = sp.D || ENEMIES[sp.def || sp.role];   // sp.def: a stat variant drawn with the role's sprite (Lantern Eve's wraith); sp.D: a built def (rares.js)
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
  flashOK() { return this.G.flashOK ? this.G.flashOK() : true; }   // Settings: flashes toggle (fun pass)
  get peace() { return !!this.G.peace; }
  paused() { const G = this.G; return !!(G.title || G.busy || G.dlg || G.log || G.downed || G.picking || G.pause); }

  // ---------------------------------------------------------------- per frame (dt already slowed by the spell wheel)
  update(dt, ctx) {
    if (!this.ctx || ctx !== this.ctx) return;
    this.time += dt;
    const p = ctx.player, G = this.G;
    if (p) this.bindSpeed(p);   // gearfx
    // cooldowns + stamina
    for (const k in this.cd) this.cd[k] = Math.max(0, this.cd[k] - dt);
    for (const id in this.procCd) this.procCd[id] = Math.max(0, this.procCd[id] - dt);   // gearfx: each proc id keeps its own ICD
    if (this.dmgShieldT > 0) this.dmgShieldT = Math.max(0, this.dmgShieldT - dt);
    if (this.runeAbsT > 0 && (this.runeAbsT = Math.max(0, this.runeAbsT - dt)) <= 0) this.runeAbs = 0;
    if (this.godT > 0) { this.godT -= dt; p.quad.visible = this.godT <= 0 || Math.floor(this.godT * 12) % 2 === 0; if (this.godT <= 0) p.quad.visible = true; }
    const guarding = p.act && p.act.name === 'defend';
    if (this.stT > 0) this.stT -= dt;
    else if (!guarding && !p.roll) this.st = Math.min(this.maxSt(), this.st + PLAYER.regen * (1 + (this.M.stRegen || 0)) * (this.G.glow ? this.G.glow.regenMul() : 1) * dt);
    const regen = this.M.regen;   // Warm Light: slow regen while nothing is chasing you
    if (regen && !this.G.downed && this.G.S.hp < this.maxHp() && !this.enemies.some((e) => e.state === 'chase' || e.state === 'attack')) this.G.S.hp = Math.min(this.maxHp(), this.G.S.hp + regen * dt);
    // the player's swing lands on its impact frame
    if (p.act && p.act.name === 'attack' && !p.act.hitDone && p.act.t >= PLAYER.impact / (p.act.gfxH || 1)) { p.act.hitDone = true; this.meleeHit(); }   // gearfx: impact stays at the same point in the (shorter) swing
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
    this.updateStone(dt, frozen);
    this.updateCaldera(dt, frozen);
    this.updateFrost(dt, frozen);
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
    if (e.tick) e.tick(e, dt, frozen);   // rares: traits (ward regrowth, rage, blinks, summons) + their aura
    let moving = false;
    const dx = p.x - a.x, dz = p.z - a.z, d = Math.hypot(dx, dz);
    const fromHome = Math.hypot(a.x - e.home[0], a.z - e.home[1]);
    const veiled = this.veilHides(e, d);   // Mist Veil: you are hard to target (stalkers cannot see you at all)
    const sees = !frozen && !this.peace && this.godT <= 0 && !veiled && d < D.aggro && Math.abs(p.y - a.y) < 1.3;
    e.cd -= dt;
    if (frozen && e.state !== 'attack') { ctx.actors.animate(a, dt, false); this.floatBob(e); return; }
    if (e.frozenT > 0) { a.act = null; if (e.state === 'attack') { e.state = 'chase'; e.fired = false; } ctx.actors.animate(a, dt, false); this.floatBob(e); return; }   // gearfx: a freeze holds the foe and stops the swing
    const gl = D.shy ? this.G.glow : null;   // cold-fire wraiths: never drift into light
    const step = (tx, tz, scale = 1) => {
      if (gl) { const n = Math.hypot(tx, tz) || 1; if (gl.litAt(a.x + tx / n * 0.45, a.z + tz / n * 0.45)) return false; }
      return ctx.moveActor(a, tx, tz, dt * scale * (this.coldAt(a.x, a.z) ? this.coldSlow : 1) * (e.chillT > 0 ? 1 - (e.chillPct > 0 ? e.chillPct : 0.5) : 1) * (e.rootT > 0 || e.frozenT > 0 ? 0 : 1));   // [VANAHEIM] Vine Grasp / gearfx freeze: rooted foes do not move   // Cold Fire patch / Frostweave chill: half speed (a boss freeze is a 40% slow via chillPct)
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
        if (this.peace || fromHome > LEASH || d > D.aggro * 1.9 || this.godT > 0 || veiled) { e.state = 'home'; break; }
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
  ping(e) { const a = e.a; if (this.ctx.gamefx && this.ctx.gamefx.meta.effects.quest_bang) { /* reuse nothing: a quick flash says "noticed" */ } a.flashT = this.flashOK() ? 0.08 : 0; }
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
  damageEnemy(e, dmg, src, push = 0.35, color = PAL.white, noProc = false) {
    if (e.state === 'dead' || e.state === 'gone') return false;
    const ctx = this.ctx, a = e.a;
    if (e.mods && e.mods.hurt) dmg = e.mods.hurt(e, dmg);   // a Shielded rare's ward soaks part of the hit
    e.hp -= dmg;
    a.flashT = this.flashOK() ? 0.12 : 0;
    this.number(dmg, a.x, a.y + (e.D.float ? 2.1 : 1.9), a.z, color);
    if (ctx.effects) ctx.effects.spawn('hit_spark', a.x, a.y + (e.a.lift || 0), a.z + 0.1);
    this.G.audio.sfx('hit');
    if (push && src) this.shove(a, a.x - src.x, a.z - src.z, push * (e.a.role === 'golem' || e.D.heavy ? (e.D.boss ? 0.15 : 0.35) : 1));
    if (!this.peace && (e.state === 'idle' || e.state === 'home')) e.state = 'chase';
    if (e.hp <= 0) { if (isTrial(e, this.G.S)) this.yieldTo(e); else this.kill(e); }
    if (!noProc && this._procHit && !this._inProc) this.rollProc(e, dmg);   // gearfx: player melee / spell / bolt only; proc damage passes noProc
    return true;
  }
  // 6.4 trial mode (Hjortur's guardian trial): at 0 HP the foe yields instead of dying: no XP, no loot, no onBoss merit,
  // no 'defeated' respawn timer; S.trials[id] counts it and e.onYield (the outro / rewards) fires
  yieldTo(e) {
    const a = e.a; e.hp = 0; e.yielded = true; e.state = 'dead'; e.t = 0; a.act = null;
    this.G.S.trials = { ...(this.G.S.trials || {}), [e.id]: (this.G.S.trials?.[e.id] || 0) + 1 };
    this.G.audio.sfx('quest');
    this.G.toast && this.G.toast(`${e.D.name} yields. The trial is passed.`, 3.0);
    if (e.onYield) e.onYield(e);
  }
  kill(e, quiet = false) {
    const ctx = this.ctx, a = e.a;
    e.state = 'dead'; e.t = 0; a.act = null;
    if (!quiet) {
      this.G.audio.sfx('defeat');
      if (ctx.effects) ctx.effects.spawn(a.role === 'wraith' ? 'glyph_burst' : 'impact', a.x, a.y, a.z + 0.05);
      if (!e.sp.once) this.defeated[this.area + ':' + e.id] = e.D.respawn || RESPAWN;   // rift waves and rares don't wander back
      if (e.D.boss) { this.G.toast && this.G.toast(`${e.D.name} falls! Its heart-light spills out as a Legendary.`, 3.2); this.G.S.bosses = { ...(this.G.S.bosses || {}), [e.id]: (this.G.S.bosses?.[e.id] || 0) + 1 }; }
      this.G.stats = this.G.stats || { defeated: 0 };
      this.G.stats.defeated++;
      if (!e.sp.noXp && this.G.gainXP) {
        const seen = (this.G.S.bestiary = this.G.S.bestiary || {});
        const first = !seen[a.role]; seen[a.role] = (seen[a.role] || 0) + 1;
        this.G.gainXP(Math.round((e.D.xp || XP[a.role] || 25) * (first ? 1 + XP.firstKill : 1)), a);
      }
      if (this.G.loot && !e.sp.noLoot) this.G.loot.onKill(a, this.G.S.lv || 1, { legendary: !!e.D.legendary, gold: e.D.boss ? 30 : e.D.rare ? 20 : 0, minRar: e.D.minRar });
      if (e.onKill) e.onKill(e);   // rares: hunt log, aura off
      if (e.D.boss && !e.D.rare && this.G.factions) this.G.factions.onBoss(e);   // mini-bosses: the realm's merit
    } else e.t = 1.5;
  }
  shove(a, dx, dz, m) {
    const ctx = this.ctx, L = Math.hypot(dx, dz) || 1;
    if (!ctx.collide) { a.x += dx / L * m; a.z += dz / L * m; return; }
    const [nx, nz, nh] = ctx.collide.move(a.x, a.z, a.y, dx / L * m, dz / L * m, a.r);
    a.x = nx; a.z = nz; a.y = nh;
  }

  // ---------------------------------------------------------------- gearfx: haste, move, resists, procs
  hasteMul() { return 1 + Math.min(this.M.haste || 0, CAPS.haste); }   // gearfx: swing interval. onAct divides p.act.dur by this; PLAYER.atkCost stays. Base clip is engine/sprites.js ACT.attack (engine/main.js actorAct). Do not divide that again.
  moveMul() { return 1 + Math.min(this.M.move || 0, CAPS.move); }   // gearfx: composed in the p.speed getter so Stone Skin / blizzard keep writing the raw value
  bindSpeed(p) {   // gearfx: effective speed = raw * moveMul. Writers (blizzard, gaze, Stone Skin) store the raw number.
    if (!p || p._gfxSp) return;
    let raw = p.speed; const C = this;
    Object.defineProperty(p, 'speed', { configurable: true, enumerable: true, get() { return raw * C.moveMul(); }, set(v) { raw = v; } });
    Object.defineProperty(p, '_spRaw', { configurable: true, enumerable: false, get() { return raw; } });
    Object.defineProperty(p, '_gfxSp', { value: 1, enumerable: false });
  }
  spRaw(p) { return p && p._spRaw != null ? p._spRaw : (p ? p.speed : 0); }
  foeOf(src) { return src && this.enemies ? this.enemies.find((x) => x.a === src || (src.a && x.a === src.a)) || null : null; }
  hitSchool(foe, src) {   // gearfx: foe element via SCHOOL_OF; a loose src.fire / ice / lightning maps the same way when the foe is physical or missing
    let school = foe && foe.D ? SCHOOL_OF(foe.D.element) : 'physical';
    if (school === 'physical' && src) {
      if (src.fire) school = 'fire';
      else if (src.ice || src.cold) school = SCHOOL_OF('ice');
      else if (src.lightning) school = SCHOOL_OF('lightning');
      else if (src.light) school = 'light';
      else if (src.dark) school = 'dark';
      else if (src.water) school = 'water';
      else if (src.element) school = SCHOOL_OF(src.element);
    }
    return school;
  }
  shieldHeld() { const it = this.G.S.gear && this.G.S.gear.secondary; return !!(it && /Buckler|Shield/.test(it.name || '')); }   // gearfx: same bases that roll block
  foeLv(foe) { return foe ? (foe.lv != null ? foe.lv : (foe.D && foe.D.lv != null ? foe.D.lv : (foe.sp && foe.sp.lv != null ? foe.sp.lv : null))) : null; }
  resKey(school) { return 'res' + school.charAt(0).toUpperCase() + school.slice(1); }
  resistPct(R, foe) { if (!(R > 0)) return 0; const K = CAPS.resK(this.foeLv(foe), this.G.S.lv || 1); return Math.min(CAPS.res, R / (R + K)); }
  foeRes(e, school) {   // gearfx: a foe's own rating, if it has one (D.resFire / resAll / D.res[school] / mods)
    if (!e) return 0; const D = e.D || {}, X = e.mods || {}, k = this.resKey(school);
    const R = (D[k] || 0) + (D.resAll || 0) + (X[k] || 0) + (X.resAll || 0) + (D.res && D.res[school] || 0);
    return this.resistPct(R, e);
  }
  hitFoe(e, dmg, src, push = 0.35, color = PAL.white) {   // gearfx: a landed player melee / spell / bolt. Summons stay on damageEnemy and never proc.
    this._procHit = true;
    try { return this.damageEnemy(e, dmg, src, push, color, false); }
    finally { this._procHit = false; }
  }
  procReady(e, p) {
    const def = PROCS[p.id]; if (!def) return false;
    if (p.id === 'root' && e.D && e.D.boss) return false;   // gearfx: bosses are immune, so the roll can land on another proc
    if (def.per === 'target') return !(e.procT && e.procT[p.id] > 0);
    return !((this.procCd[p.id] || 0) > 0);
  }
  rollProc(e, dmg) {   // gearfx: at most one proc. chance = min(ch + crit*0.25, ch*2, 0.35). crit is M.crit. A killing blow still procs.
    if (!e || e.state === 'gone' || this._inProc) return;
    const list = (this.M.procs || []).filter((p) => p && this.procReady(e, p)); if (!list.length) return;
    const crit = this.M.crit || 0, bag = list.slice();
    for (let i = bag.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); const t = bag[i]; bag[i] = bag[j]; bag[j] = t; }
    this._inProc = true;
    try {
      for (const p of bag) {
        const ch = p.ch ?? PROCS[p.id].ch, chance = Math.min(ch + crit * 0.25, ch * 2, 0.35);
        if (Math.random() < chance) { this.fireProc(p, e, dmg); return; }
      }
    } finally { this._inProc = false; }
  }
  fireProc(p, e, dmg) {
    const id = p.id, def = PROCS[id]; if (!def) return;
    const icd = p.icd ?? def.icd;
    if (def.per === 'target') { e.procT = e.procT || {}; e.procT[id] = icd; } else this.procCd[id] = icd;
    this.gfx.lastProc = id; this.gfx.procs = (this.gfx.procs || 0) + 1;
    if (e.a) this.number(PROC_WORD[id] || id, e.a.x, e.a.y + 2.35, e.a.z, PROC_COL[id] || PAL.white);
    if (id === 'lifeSteal') this.heal(dmg * def.healPct, true);
    else if (id === 'fireBolt') this.procBolt(p, e);
    else if (id === 'freeze') this.procFreeze(e);
    else if (id === 'root') { if (!(e.D && e.D.boss)) e.rootT = Math.max(e.rootT || 0, def.dur); }
    else if (id === 'heal') this.heal(this.maxHp() * def.healPct, true);
    else if (id === 'damageShield') this.dmgShieldT = def.dur;
    else if (id === 'runeShield') { this.runeAbs = this.maxHp() * def.absorb; this.runeAbsT = def.dur; }
  }
  procBolt(p, e) {   // gearfx: (8 + 3*lv) * spellMul, then the foe's own fire resist. Reuses ember / coldfire_bolt / ember_pop. noProc so it cannot chain.
    const ctx = this.ctx; if (!ctx || !e || e.state === 'dead' || e.state === 'gone') return;
    const def = PROCS.fireBolt, lv = p.lv || this.G.S.lv || 1, pl = ctx.player;
    const n = Math.max(CAPS.minHit, Math.round((def.base + def.perLv * lv) * (this.M.spellMul || 1) * (1 - this.foeRes(e, 'fire'))));
    const fx = ctx.effects, nm = fx && (fx.meta.effects.ember ? 'ember' : fx.meta.effects.coldfire_bolt ? 'coldfire_bolt' : (fx.meta.effects.ember_pop ? 'ember_pop' : null));
    if (nm) fx.spawn(nm, pl.x, pl.y + 0.3, pl.z + 0.05, nm === 'coldfire_bolt' ? { to: [e.a.x, e.a.y + 0.4, e.a.z] } : { duration: 0.35, fadeIn: 0 });
    this.damageEnemy(e, n, pl, 0.15, LAVA, true);
  }
  procFreeze(e) {   // gearfx: freeze = rootT (no move) + frozenT (no swing). Elite/rare 0.5 s. Bosses are only slowed.
    const def = PROCS.freeze;
    if (e.D && e.D.boss) { e.chillT = Math.max(e.chillT || 0, def.bossDur); e.chillPct = def.bossSlow; return; }
    const dur = (e.D && (e.D.elite || e.D.rare)) || e.rare ? def.eliteDur : def.dur;
    e.rootT = Math.max(e.rootT || 0, dur); e.frozenT = Math.max(e.frozenT || 0, dur);
  }

  // ---------------------------------------------------------------- the player
  hurtPlayer(dmg, src, push = 0.3) {
    const ctx = this.ctx, p = ctx.player, G = this.G;
    if (p.iframes > 0 && p.roll && !G.downed && this.hasForesight()) this.foreUntil = performance.now() + 60000;   // [VANAHEIM] Foresight Charm: a dodged hit -> +5% crit 60 s
    if (G.downed || this.godT > 0 || p.iframes > 0) return false;
    dmg *= (MODES[G.S.mode] || MODES.adventurer).hurt;   // Story / Adventurer / Hero
    if (this.skin) dmg = Math.max(1, Math.round(dmg * this.skin.take));   // Stone Skin: -40 % damage taken
    const foe = this.foeOf(src), raw = dmg;
    if (this.ward && src && (src.fire || (foe && foe.D.element === 'fire'))) dmg = Math.max(1, Math.round(dmg * this.ward.take));   // Flame Ward: -30 % fire damage taken
    // gearfx: after mode / skin / ward. (a) avoid (b) rune or resist+shield (c) block (d) rune absorb (e) min 1. Guard below is unchanged.
    const M = this.M, school = this.hitSchool(foe, src);
    const half = !!(src && (src.proj || src.bolt)) || !!(foe && foe.D && foe.D.ranged) || school !== 'physical';
    const avoid = Math.min(M.avoid || 0, CAPS.avoid) * (half ? CAPS.avoidSpell : 1);
    if (avoid > 0 && Math.random() < avoid) { this.number('Dodged', p.x, p.y + 2.0, p.z, GREY); return true; }   // gearfx: 0 damage, the swing still "lands" for the caller
    if (school === 'physical') dmg *= 1 - Math.min(M.runePct || 0, CAPS.runePct);
    else {
      const red = this.resistPct((M[this.resKey(school)] || 0) + (M.resAll || 0), foe);
      if (red >= 0.25) this.number('Resisted', p.x, p.y + 2.15, p.z, PAL.sky);
      dmg *= (1 - red) * (1 - Math.min(M.shieldPct || 0, CAPS.shieldPct));
    }
    const fv = FV[p.facing] || [0, 1];
    const dx = src && src.x != null ? src.x - p.x : 0, dz = src && src.z != null ? src.z - p.z : 0, dlen = Math.hypot(dx, dz) || 1;
    const front = !!(src && src.x != null && (fv[0] * dx + fv[1] * dz) / dlen > 0.15);
    if (dmg > 0 && front && this.shieldHeld() && Math.random() < Math.min(M.block || 0, CAPS.block)) { dmg *= 1 - CAPS.blockSoak; this.number('Blocked', p.x, p.y + 2.15, p.z, PAL.sky); }
    if (this.runeAbsT > 0 && this.runeAbs > 0 && dmg > 0) {
      const soak = Math.min(this.runeAbs, dmg); this.runeAbs -= soak; dmg -= soak;
      if (dmg <= 0.0001) { this.number('Absorbed', p.x, p.y + 2.0, p.z, PAL.white); return true; }   // gearfx: the pool ate the whole hit, so it never connects
    }
    let guarded = false;
    if (p.act && p.act.name === 'defend' && front) {
      guarded = true;
      dmg = Math.max(1, Math.round(dmg * (this.hero.guard ?? PLAYER.guardMul) * M.guardMul));
      this.st -= (6 + dmg * 1.5) * M.guardSt; this.stT = PLAYER.regenDelay;
      if (ctx.effects) ctx.effects.spawn('hit_spark', p.x + fv[0] * 0.3, p.y, p.z + fv[1] * 0.3 + 0.1);
      G.audio.sfx('guard');
      if (this.st <= 0) { this.st = 0; ctx.release('defend'); G.toast('Guard broken!', 1.2); }
    } else { G.audio.sfx('hurt'); dmg = Math.max(CAPS.minHit, Math.round(dmg)); }   // gearfx: a hit that connects deals at least 1
    G.S.hp = Math.max(0, G.S.hp - dmg);
    if (this.ward && foe && foe.state !== 'dead' && foe.state !== 'gone') this.ignite(foe, Math.max(1, Math.round(raw * this.ward.refl)));   // ... and 10 % of the blow comes back as a burn on whoever struck
    if (this.dmgShieldT > 0 && foe && foe.state !== 'dead' && foe.state !== 'gone' && dmg > 0) this.damageEnemy(foe, Math.max(CAPS.minHit, Math.round(dmg * PROCS.damageShield.reflect)), null, 0, LAVA, true);   // gearfx: 20% of the dealt hit back as fire, and it does not proc
    p.flashT = this.flashOK() ? 0.15 : 0; p.iframes = PLAYER.hitIframes;
    this.number(dmg, p.x, p.y + 2.0, p.z, guarded ? PAL.sky : PAL.rose);
    if (src && src.x != null) this.shove(p, -dx, -dz, guarded ? push * 0.4 : push);
    if (G.S.hp <= 0) this.down();
    return true;
  }
  heal(n, raw = false) {
    if (n >= 3) this.G.audio && this.G.audio.sfx('heal');   // [SFX 2026-11-03] heal.ogg (throttled 400 ms in audio.js)
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
      if (this.hitFoe(e, dmg, p, 0.45, this.lastCrit ? PAL.gold : PAL.white)) { hit++; if (this.M.drain) this.heal(dmg * this.M.drain, true); }   // gearfx: melee procs
    }
    if (this.summon) hit += 0;   // never hits your own summon
    if (!hit) this.G.audio.sfx('swing');
    return hit;
  }
  onAct(name) {
    if (name === 'attack') { this.st = Math.max(0, this.st - PLAYER.atkCost); this.stT = 0.35; const a = this.ctx && this.ctx.player && this.ctx.player.act; if (a && a.name === 'attack' && !a.gfxH) { const h = this.hasteMul(); a.dur /= h; a.gfxH = h; } }   // gearfx: interval / dur / hasteMul. Stamina stays PLAYER.atkCost. Base clip is engine ACT.attack; step 3 must not divide dur again.
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
        for (const e of this.alive()) if (Math.hypot(e.a.x - cx, e.a.z - cz) < 1.5) this.hitFoe(e, this.out('spell', dmg), p, 0.25, PAL.gold);   // gearfx: charm
      } });
      return true;
    }
    if (this.cd.spell > 0 || (S.own && this.cd[S.own] > 0)) { this.tired(); return false; }
    if (S.own) { this.cd[S.own] = S.cd * (1 - Math.min(0.5, this.M.spellCd || 0)); this.cd.spell = 1.0; }
    else this.cd.spell = S.cd * (1 - Math.min(0.5, this.M.spellCd || 0));   // tier II / III skills shorten spell cooldowns
    // auto-face the nearest foe (4-way facing) so a quick tap aims where you mean
    const tgt = this.nearestEnemy(p, 7);
    if (tgt && !p.act) ctx.actors.setFacingFromVec(p, tgt.a.x - p.x, tgt.a.z - p.z);
    if (!p.act) p.castT = p.castDur;
    G.audio.sfx(spellSfx(S));
    { const hx = ctx.hmfx, hn = HMFX_CAST[S.kind], hm = hx && hn && hx.meta.effects[hn];
      if (hm) hx.spawn(hn, p.x, p.y, p.z + 0.06, hm.loop ? { duration: 1.2 } : {}); }   // [SOUND] school -> spell_light / spell_dark / spell_nature (audio falls back to 'spell')
    { const hx = ctx.hmfx, hn = HMFX_CAST2[(S.school === 'nature' ? 'nature:' : '') + S.kind], hm = hx && hn && hx.meta.effects[hn]; if (hm) hx.spawn(hn, p.x, p.y, p.z + 0.06, hm.loop ? { duration: 1.2 } : {}); } // [HMFX48] school cast
    const fv = FV[p.facing] || [0, 1], fx = ctx.effects;
    if (!fx) return false;
    const T = S.stone ? this.stoneFx() : null;   // Boulder Toss / Frost Rune: tier II / III art + damage from the game-fx atlas
    if (T && T.cast) T.g.spawn(T.cast, p.x + fv[0] * 0.4, p.y, p.z + fv[1] * 0.4 + 0.06);
    if (S.kind === 'skin') this.doSkin(S);
    else if (S.kind === 'coldfire') this.doColdFire(S);
    else if (S.kind === 'golem') this.doGolem(S);
    else if (S.kind === 'firewave') this.doFireWave(S);
    else if (S.kind === 'magma') this.doMagma(S);
    else if (S.kind === 'swarm') this.doSwarm(S);
    else if (S.kind === 'ward') this.doWard(S);
    else if (S.kind === 'hound') this.doHound(S);
    else if (S.kind === 'root') this.doRoot(S);
    else if (S.kind === 'lance') this.doLance(S);
    else if (S.kind === 'fnova') this.doFrostNova(S);
    else if (S.kind === 'veil') this.doVeil(S);
    else if (S.kind === 'spirits') this.doSpirits(S);
    else if (S.kind === 'igolem') this.doGolem(S);
    else if (S.kind === 'projectile' || S.kind === 'pierce') {
      const fxo = T && T.bolt ? T.g : fx, fxn = T && T.bolt ? T.bolt : S.fx;
      const travel = fxo.meta.effects[fxn].travel || 4.5;
      const tx = p.x + fv[0] * travel, tz = p.z + fv[1] * travel;
      const proj = { owner: 'player', spell: name, S, hitSet: new Set(), fxo, mul: T ? T.mul : 1, T };
      proj.f = fxo.spawn(fxn, p.x + fv[0] * 0.4, p.y, p.z + fv[1] * 0.4 + 0.05,
                        { to: [tx, ctx.heightAt(tx, tz), tz], onDone: (f) => { if (S.kind === 'projectile' && !proj.done) this.burst(proj, f.x, f.z, true); proj.done = true; if (S.kind === 'pierce' && this.G.glow) this.G.glow.pool(f.x, f.z, this.G.glow.colorOf(S.fx)); } });
      this.projs.push(proj);
      if (S.kind === 'pierce') { const hx = ctx.hmfx, hn = HMFX_BOLT.pierce, hm = hx && hn && hx.meta.effects[hn]; if (hm) hx.spawn(hn, p.x, p.y, p.z + 0.06, hm.loop ? { duration: 1.2 } : {}); } // [HMFX48] fire bolt
    } else if (S.kind === 'nova') {
      fx.spawn('rune_slam', p.x, p.y, p.z + 0.05); fx.spawn('impact', p.x, p.y, p.z + 0.06);
      { const hx = ctx.hmfx, hn = HMFX_FLASH.light, hm = hx && hn && hx.meta.effects[hn]; if (hm) hx.spawn(hn, p.x, p.y, p.z + 0.06, hm.loop ? { duration: 1.2 } : {}); } // [HMFX48] light hit
      if (this.G.glow) this.G.glow.pool(p.x, p.z, this.G.glow.colorOf('rune_slam'), 1.2);
      for (const e of this.alive()) if (dist(e.a, p) < S.radius + e.D.r) this.hitFoe(e, this.out('spell', S.dmg), p, S.push, PAL.gold);   // gearfx: nova
    } else if (S.kind === 'trap') {
      const x = p.x + fv[0] * 1.7, z = p.z + fv[1] * 1.7, y = ctx.heightAt(x, z);
      (T && T.rune ? T.g : fx).spawn(T && T.rune ? T.rune : 'rune_trap', x, y, z + 0.02);
      this.traps.push({ x, y, z, t: 0, S, armed: null, T });
      if (this.G.glow) this.G.glow.pool(x, z, T ? COLD_BLUE : this.G.glow.colorOf('rune_trap'));
    } else if (S.kind === 'chain') {
      let from = p, hitList = [], t = 0;
      for (let i = 0; i <= S.jumps + this.M.chainJumps; i++) {
        const e = this.nearestEnemy(from, i === 0 ? S.range : S.hop, hitList);
        if (!e) break;
        hitList.push(e);
        const dmg = this.out('spell', S.dmg * Math.pow(0.75, i));
        if (i === 0 && this.G.glow) this.G.glow.pool(e.a.x, e.a.z, this.G.glow.colorOf('sky_strike'));   // first jump: same as nova / bloom, not deferred through later()

        this.later.push({ t, fn: () => { if (this.ctx !== ctx) return; if (e.state !== 'dead' && e.state !== 'gone') { fx.spawn('sky_strike', e.a.x, e.a.y, e.a.z + 0.06); { const hx = ctx.hmfx, hn = HMFX_ZAP.chain, hm = hx && hn && hx.meta.effects[hn]; if (hm) hx.spawn(hn, e.a.x, e.a.y, e.a.z + 0.06, hm.loop ? { duration: 1.2 } : {}); } this.hitFoe(e, dmg, p, 0.2, PAL.gold); } } }); // [HMFX48] chain lightning
        from = e.a; t += 0.16;
      }
      if (!hitList.length) { fx.spawn('sky_strike', p.x + fv[0] * 2, ctx.heightAt(p.x + fv[0] * 2, p.z + fv[1] * 2), p.z + fv[1] * 2 + 0.06); { const hx = ctx.hmfx, hn = HMFX_ZAP.chain, hm = hx && hn && hx.meta.effects[hn]; if (hm) hx.spawn(hn, p.x + fv[0] * 2, ctx.heightAt(p.x + fv[0] * 2, p.z + fv[1] * 2), p.z + fv[1] * 2 + 0.06, hm.loop ? { duration: 1.2 } : {}); } } // [HMFX48] chain lightning
    } else if (S.kind === 'heal') {
      fx.spawn('bloom_ring', p.x, p.y, p.z + 0.05); fx.spawn('healing_petals', p.x, p.y, p.z + 0.06);
      { const hx = ctx.hmfx, hn = HMFX_HEAL.heal, hm = hx && hn && hx.meta.effects[hn]; if (hm) hx.spawn(hn, p.x, p.y, p.z + 0.06, hm.loop ? { duration: 1.2 } : {}); } // [HMFX48] heal spell
      if (this.G.glow) this.G.glow.pool(p.x, p.z, this.G.glow.colorOf('bloom_ring'));
      this.heal(S.heal);
      if (this.summon) this.summon.hp = Math.min(this.summon.D.hp, this.summon.hp + S.heal);
      for (const e of this.alive()) if (dist(e.a, p) < S.radius + e.D.r) this.hitFoe(e, this.out('spell', S.dmg), p, 0.5, PAL.gold);   // gearfx: bloom
    }
    return false;
  }
  burst(proj, x, z, hitFxAuto = false) {   // hitFxAuto: the bolt ran its full travel, so the atlas already queues its own impact (`then`)
    const ctx = this.ctx, S = proj.S, T = proj.T;
    if (!proj.small && this.G.glow) this.G.glow.pool(x, z, this.G.glow.colorOf(S.fx === 'seed_bomb' ? 'earth_burst' : S.fx));
    if (!proj.small && S.fx === 'seed_bomb' && this.M.seedSplit) {
      for (let k = 0; k < this.M.seedSplit; k++) {
        const a = k * Math.PI + 0.7, sx = x + Math.cos(a) * 1.1, sz = z + Math.sin(a) * 0.8;
        this.later.push({ t: 0.15 + 0.1 * k, fn: () => this.burst({ S, small: true }, sx, sz) });
      }
    }
    if (T && T.hit) { if (!hitFxAuto) T.g.spawn(T.hit, x, ctx.heightAt(x, z), z + 0.05); }
    else if (S.burst && ctx.effects) ctx.effects.spawn(S.burst, x, ctx.heightAt(x, z), z + 0.05);
    if ((T && T.hit) || S.burst) { const hx = ctx.hmfx, hn = HMFX_IMPACT.nature, hm = hx && hn && hx.meta.effects[hn]; if (hm) hx.spawn(hn, x, ctx.heightAt(x, z), z + 0.06, hm.loop ? { duration: 1.2 } : {}); } // [HMFX48] nature impact
    const rad = S.radius * (T ? T.rad : 1);
    for (const e of this.alive()) if (Math.hypot(e.a.x - x, e.a.z - z) < rad + e.D.r) this.hitFoe(e, this.out('spell', S.dmg * (proj.mul || 1) * (proj.small ? 0.5 : 1)), { x, z }, 0.4, PAL.gold);   // gearfx: bolt burst
  }
  updateProjs() {
    const ctx = this.ctx, p = ctx.player;
    for (const pr of this.projs) {
      const f = pr.f;
      const fxo = pr.fxo || ctx.effects;
      if (!f || pr.done || !fxo.list.includes(f)) { pr.done = true; continue; }
      if (pr.owner === 'enemy') {
        if (Math.hypot(f.x - p.x, f.z - p.z) < pr.r && !this.G.downed) {
          if (this.hurtPlayer(pr.dmg, { x: f.x, z: f.z, a: pr.src, proj: true }, 0.35) || p.act?.name === 'defend') { ctx.effects.remove(f); ctx.effects.spawn('frost_puff', f.x, f.y - 0.6, f.z); pr.done = true; }   // gearfx: a bolt is a projectile (half avoid)
        }
        // a summon in the way takes the bolt
        const s = this.summon;
        if (!pr.done && s && Math.hypot(f.x - s.a.x, f.z - s.a.z) < 0.5) { ctx.effects.remove(f); ctx.effects.spawn('frost_puff', f.x, f.y - 0.6, f.z); pr.done = true; this.hurtSummon(pr.dmg); }
        continue;
      }
      for (const e of this.alive()) {
        if (pr.hitSet.has(e) || Math.hypot(e.a.x - f.x, e.a.z - f.z) > 0.6 + e.D.r) continue;
        if (pr.S.kind === 'pierce') { pr.hitSet.add(e); this.hitFoe(e, this.out('spell', pr.S.dmg), f, 0.5, PAL.gold); }   // gearfx: pierce
        else { fxo.remove(f); this.burst(pr, f.x, f.z); pr.done = true; break; }
      }
    }
    this.projs = this.projs.filter((pr) => !pr.done);
  }
  updateTraps(dt) {
    const ctx = this.ctx;
    for (const tr of this.traps) {
      tr.t += dt;
      const T = tr.T, fxo = T && T.rune ? T.g : ctx.effects;
      if (!tr.armed && tr.t >= tr.S.arm) tr.armed = fxo.spawn(T && T.rune ? T.rune : 'rune_trap', tr.x, tr.y, tr.z + 0.02, { frame: 5 });
      if (!tr.armed) continue;
      const near = this.alive().some((e) => Math.hypot(e.a.x - tr.x, e.a.z - tr.z) < 1.1 + e.D.r);
      if (near || tr.t > tr.S.life) {
        fxo.remove(tr.armed);
        (T && T.burst ? T.g : ctx.effects).spawn(T && T.burst ? T.burst : 'glyph_burst', tr.x, tr.y, tr.z + 0.04);
        if (near) for (const e of this.alive()) if (Math.hypot(e.a.x - tr.x, e.a.z - tr.z) < tr.S.radius * (T ? T.rad : 1) * this.M.trapRadius + e.D.r) { this.hitFoe(e, this.out('spell', tr.S.dmg * (T ? T.mul : 1)), tr, 0.3, PAL.gold); e.cd = Math.max(e.cd, 1.6); }   // gearfx: trap
        tr.done = true;
      }
    }
    this.traps = this.traps.filter((t) => !t.done);
  }

  // ---------------------------------------------------------------- [JOTUNHEIM] Stonefrost II / III
  stoneTier() { const f = this.G.S.flags || {}; return f.sf_iii ? 3 : f.sf_ii ? 2 : 1; }
  // tier II / III art for Boulder Toss / Frost Rune (null = tier I, or an area with no game-fx atlas: the old spells-atlas art plays)
  stoneFx() {
    const g = this.ctx && this.ctx.gamefx, T = STONE[this.stoneTier()];
    if (!g || !T) return null;
    const has = (n) => !!g.meta.effects[n];
    return { g, mul: T.mul, rad: T.rad, cast: has(T.cast) ? T.cast : null, bolt: has(T.bolt) ? T.bolt : null, hit: has(T.hit) ? T.hit : null, rune: has(T.rune) ? T.rune : null, burst: has(T.burst) ? T.burst : null };
  }
  get coldSlow() { return 0.5; }
  coldAt(x, z) { for (const c of this.patches || []) if (Math.hypot(x - c.x, z - c.z) < c.r) return true; return false; }
  // Stone Skin: 6 s, -40 % damage taken, -20 % speed (raw p.speed is shared with the blizzard's frost slow: re-base whenever someone else writes it)
  doSkin(S) {
    const ctx = this.ctx, p = ctx.player, g = ctx.gamefx;
    if (this.skin) this.endSkin();
    this.bindSpeed(p); const sp0 = this.spRaw(p);   // gearfx: the slow is on the raw value; the getter puts moveMul on top
    this.skin = { t: S.t, take: S.take, sp0, sp: sp0 * S.speed, k: S.speed };
    p.speed = this.skin.sp;
    const T = STONE[2];
    if (g && g.meta.effects[T.cast]) g.spawn(T.cast, p.x, p.y, p.z + 0.06);
    else if (ctx.effects && ctx.effects.meta.effects.impact) ctx.effects.spawn('impact', p.x, p.y, p.z + 0.06);   // no game-fx atlas (hollows, lane)
    { const hx = ctx.hmfx, hn = HMFX_BUFF.skin, hm = hx && hn && hx.meta.effects[hn]; if (hm) hx.spawn(hn, p.x, p.y, p.z + 0.06, hm.loop ? { duration: 1.2 } : {}); } // [HMFX48] stone skin
    if (g && g.meta.effects[T.rune]) this.skin.ring = g.spawn(T.rune, p.x, p.y, p.z + 0.03, { duration: S.t, frame: 5 });
    if (this.G.glow) this.G.glow.pool(p.x, p.z, '#b9c7d6', 0.5);
    this.G.toast('Stone Skin: the stone holds', 1.4);
  }
  endSkin() {
    const k = this.skin, p = this.ctx && this.ctx.player; if (!k) return;
    if (p && this.spRaw(p) === k.sp) p.speed = k.sp0;   // gearfx: restore the raw speed, not the move-scaled one
    if (k.ring && this.ctx.gamefx) this.ctx.gamefx.remove(k.ring);
    this.skin = null;
  }
  // Cold Fire: a neon-blue fire patch for 8 s: foes in it move at half speed, it lights dark rooms (a glow zone + a cold-blue light), it never burns
  doColdFire(S) {
    const ctx = this.ctx, p = ctx.player, g = ctx.gamefx, fv = FV[p.facing] || [0, 1];
    const x = p.x + fv[0] * 2.0, z = p.z + fv[1] * 2.0, y = ctx.heightAt(x, z);
    const c = { x, z, r: S.radius, t: S.life, fx: [] };
    const T = STONE[2], gl = this.G.glow;
    if (g && g.meta.effects[T.rune]) c.fx.push([g, g.spawn(T.rune, x, y, z + 0.03, { duration: S.life, frame: 5 })]);
    else if (ctx.effects) c.fx.push([ctx.effects, ctx.effects.spawn('coldfire_pool', x, y, z + 0.03, { duration: S.life })]);
    if (ctx.effects) c.fx.push([ctx.effects, ctx.effects.spawn('coldfire_motes', x + 0.1, y + 0.1, z + 0.1, { duration: S.life })]);
    if (ctx.addGlow) ctx.addGlow(x, y, z, { color: COLD_BLUE, intensity: 8, range: 4.6, life: S.life, fadeIn: 0.2, lift: 0.5 });
    if (gl) { gl.pools.push({ x, z, r: S.radius, t: S.life, cold: 1 }); if (this.G.hollows) this.G.hollows.spellAt(x, z); }   // a lit zone: braziers catch it, shy wraiths keep out
    this.patches.push(c);
    this.G.toast('Cold Fire', 1.0);
  }
  // Stone Golem: a stone golem fights for you for 20 s (it takes the place of any other summon)
  doGolem(S) {
    const ctx = this.ctx, p = ctx.player, G = this.G, roles = ctx.actors.meta.roles;
    const ice = S.kind === 'igolem', GD = ice ? ICEGOLEM : GOLEM, role = (ice ? ICEGOLEM_ROLES : GOLEM_ROLES).find((r) => roles[r]);   // [NIFLHEIM-2] the Frostweave Ice Golem shares this path
    if (!role) { this.cd[S.own || 'golem'] = 0; this.cd.spell = 0; if (ice) G.toast('No frost golem answers here.', 2.2); return; }
    if (this.summon) this.unsummon();
    const fv = FV[p.facing] || [0, 1], hp = Math.round(GD.hp * this.M.summonMul);
    const a = ctx.addNpc({ id: 'summon', role, name: GD.name, pos: [p.x + fv[0] * 1.0 + 0.3, p.z + fv[1] * 1.0], behavior: 'idle', turn: false, speed: GD.speed });
    a.ai = true; a.noTalk = true; a.facing = p.facing;
    this.summon = { a, tier: 3, golem: true, ice, D: { ...GD, hp }, hp, life: S.life + this.M.summonLife, cd: 0.4, target: null, sparkT: 0.3 };
    if (ice) { if (ctx.addGlow) this.summon.light = ctx.addGlow(a.x, a.y, a.z, { color: FROST, intensity: 3.5, range: 2.8, lift: 0.8, fadeIn: 0.4 });
      this.frostFx('frost_nova', 'frost_puff', a.x, a.y, a.z + 0.05, {}); G.audio.sfx('summon'); G.toast('An Ice Golem rises out of the frost!', 1.6); return; }
    if (ctx.addGlow) this.summon.light = ctx.addGlow(a.x, a.y, a.z, { color: COLD_BLUE, intensity: 3.5, range: 2.8, lift: 0.8, fadeIn: 0.4 });
    const g = ctx.gamefx, T = STONE[3];
    if (g && g.meta.effects[T.burst]) g.spawn(T.burst, a.x, a.y, a.z + 0.05); else if (ctx.effects) ctx.effects.spawn('summon_poof', a.x, a.y, a.z + 0.05);
    G.audio.sfx('summon');
    G.toast('The Stone Golem rises!', 1.6);
  }
  updateStone(dt, frozen) {
    const ctx = this.ctx, p = ctx.player, k = this.skin;
    if (k && !frozen) {
      k.t -= dt;
      if (this.spRaw(p) !== k.sp) { k.sp0 = this.spRaw(p); k.sp = k.sp0 * k.k; p.speed = k.sp; }   // gearfx: blizzard / gaze write the raw speed; re-base from that so the slow does not compound
      if (k.t <= 0 || this.G.downed) this.endSkin();
    }
    for (const c of this.patches) {
      if (!frozen) c.t -= dt;
      if (c.t <= 0) { c.done = true; for (const [o, f] of c.fx) o.remove(f); }   // forced-frame decals never expire by themselves
    }
    if (this.patches.some((c) => c.done)) this.patches = this.patches.filter((c) => !c.done);
  }

  // ---------------------------------------------------------------- [MUSPELHEIM-2] the Caldera school
  calFx(name) { const g = this.ctx && this.ctx.gamefx; return g && g.meta.effects[name] ? g : null; }
  calSpawn(name, x, y, z, o) { const g = this.calFx(name); return g ? [g, g.spawn(name, x, y, z, o)] : null; }
  // a burn on a foe: `n` damage, dealt over ~2 s in 0.5 s ticks (burns stack)
  ignite(e, n) { if (!e || n <= 0) return; e.burn = e.burn || { left: 0, t: 0.5 }; e.burn.left += n; }
  // Fire Wave (I): a rolling wave of fire in a 100 deg cone in front of you, 4.2 m deep; it reaches each foe as the wave rolls past it
  doFireWave(S) {
    const ctx = this.ctx, p = ctx.player, fv = FV[p.facing] || [0, 1], nm = WAVE_FX[p.facing] || 'fire_wave', G = this.G;
    for (let i = 0; i < 3; i++) {
      const d = 1.1 + i * 1.05, x = p.x + fv[0] * d, z = p.z + fv[1] * d;
      this.later.push({ t: i * 0.11, fn: () => { if (this.ctx !== ctx) return; if (!this.calSpawn(this.calFx(nm) ? nm : 'fire_wave', x, ctx.heightAt(x, z), z + 0.06, {}) && ctx.effects && ctx.effects.meta.effects.ember_pop) ctx.effects.spawn('ember_pop', x, ctx.heightAt(x, z), z + 0.06); } });   // no game-fx atlas (hollows, lane): the spells atlas' ember pop
      this.later.push({ t: i * 0.11, fn: () => { if (this.ctx !== ctx) return; { const hx = ctx.hmfx, hn = HMFX_IMPACT.fire, hm = hx && hn && hx.meta.effects[hn]; if (hm) hx.spawn(hn, x, ctx.heightAt(x, z), z + 0.06, hm.loop ? { duration: 1.2 } : {}); } } }); // [HMFX48] fire impact
    }
    if (ctx.addGlow) ctx.addGlow(p.x + fv[0] * 2.2, p.y, p.z + fv[1] * 2.2, { color: LAVA, intensity: 9, range: 4.8, life: 0.7, fadeIn: 0.05, lift: 0.5 });
    if (G.hollows) G.hollows.spellAt(p.x + fv[0] * 2, p.z + fv[1] * 2);   // braziers in its path catch
    const hit = [];
    for (const e of this.alive()) {
      const dx = e.a.x - p.x, dz = e.a.z - p.z, d = Math.hypot(dx, dz);
      if (d > S.range + e.D.r || Math.abs(e.a.y - p.y) > 1.2) continue;
      if (d > 0.5 && (fv[0] * dx + fv[1] * dz) / d < S.arc) continue;
      hit.push(e);
      this.later.push({ t: Math.max(0, d - 0.6) / S.roll, fn: () => { if (this.ctx === ctx && e.state !== 'dead' && e.state !== 'gone') { this.hitFoe(e, this.out('spell', S.dmg), p, S.push, PAL.gold); this.ignite(e, S.burn); } } });
      this.later.push({ t: Math.max(0, d - 0.6) / S.roll, fn: () => { if (this.ctx === ctx && e.state !== 'dead' && e.state !== 'gone') { const hx = ctx.hmfx, hn = HMFX_FLASH.fire, hm = hx && hn && hx.meta.effects[hn]; if (hm) hx.spawn(hn, e.a.x, e.a.y, e.a.z + 0.06, hm.loop ? { duration: 1.2 } : {}); } } }); // [HMFX48] fire hit
    }
    this.lastWave = { n: hit.length, ids: hit.map((e) => e.id) };
  }
  // Magma Pool (I): a lava patch 2 m ahead for 6 s; foes standing in it burn (5 every 0.5 s); two at most (the oldest cools first)
  doMagma(S) {
    const ctx = this.ctx, p = ctx.player, fv = FV[p.facing] || [0, 1];
    const x = p.x + fv[0] * 2.0, z = p.z + fv[1] * 2.0, y = ctx.heightAt(x, z);
    while (this.magma.length >= 2) this.coolMagma(this.magma.shift());
    const m = { x, z, r: S.radius, t: S.life, tick: 0.5, dmg: S.dmg, fx: [] };
    const f = this.calSpawn('magma_pool', x, y, z + 0.03, { duration: S.life }); if (f) m.fx.push(f);
    else if (ctx.effects) m.fx.push([ctx.effects, ctx.effects.spawn('red_pool', x, y, z + 0.03, { duration: S.life })]);
    const e2 = this.calSpawn('ember_mote', x, y + 0.1, z + 0.1, { duration: S.life }); if (e2) m.fx.push(e2);
    if (ctx.addGlow) m.light = ctx.addGlow(x, y, z, { color: LAVA, intensity: 7, range: 4.0, life: S.life, fadeIn: 0.2, lift: 0.4 });
    if (this.G.glow) { this.G.glow.pools.push({ x, z, r: S.radius, t: S.life }); if (this.G.hollows) this.G.hollows.spellAt(x, z); }   // lava is light: a lit zone
    this.magma.push(m);
  }
  coolMagma(m) { m.done = true; for (const [o, f] of m.fx) o.remove(f); if (m.light) m.light.kill = true; }
  magmaAt(x, z) { return this.magma.some((m) => Math.hypot(x - m.x, z - m.z) < m.r); }
  // Ember Swarm (II): six motes circle you for 1 s, then each flies at a foe (the nearest six, shared round), 9 damage + a small burn each
  doSwarm(S) {
    const ctx = this.ctx, p = ctx.player;
    for (const m of this.motes) if (m.f) m.f[0].remove(m.f[1]);
    this.motes = [];
    const fb = (n, x, y, z, o) => ctx.effects && ctx.effects.meta.effects[n] ? [ctx.effects, ctx.effects.spawn(n, x, y, z, o)] : null;   // no game-fx atlas (hollows, lane): the spells atlas
    const cloud = this.calSpawn('ember_swarm', p.x, p.y, p.z + 0.05, { duration: S.orbit + 0.2 }) || fb('summon_poof', p.x, p.y, p.z + 0.05, { duration: S.orbit + 0.2 });
    for (let i = 0; i < S.n; i++) {
      const a0 = i / S.n * Math.PI * 2;
      this.motes.push({ i, a0, t: 0, state: 'orbit', x: p.x, z: p.z, y: p.y, target: null, f: this.calSpawn('ember_mote', p.x, p.y, p.z, { duration: S.orbit + 3.5 }) || fb('ember_pop', p.x, p.y, p.z, { duration: S.orbit + 3.5 }), S });
    }
    this.swarm = { cloud, t: S.orbit, hits: 0 };
    if (ctx.addGlow) this.swarm.light = ctx.addGlow(p.x, p.y, p.z, { color: LAVA, intensity: 5, range: 3.2, life: S.orbit + 1.0, fadeIn: 0.1, lift: 0.8 });
    this.G.toast('Ember Swarm', 1.0);
  }
  // Flame Ward (II): a ring of small flames for 8 s: -30 % fire damage taken (fire foes, fire pillars, lava stones), the ember storm cannot burn you,
  // and 10 % of every blow that lands comes back on the striker as a burn
  doWard(S) {
    const ctx = this.ctx, p = ctx.player;
    this.endWard();
    this.ward = { t: S.t, take: S.take, refl: S.refl, f: this.calSpawn('flame_ward', p.x, p.y, p.z + 0.08, { duration: S.t }) || (ctx.effects && ctx.effects.meta.effects.rune_circle ? [ctx.effects, ctx.effects.spawn('rune_circle', p.x, p.y, p.z + 0.08, { duration: S.t })] : null) };
    { const hx = ctx.hmfx, hn = HMFX_BUFF.ward, hm = hx && hn && hx.meta.effects[hn]; if (hm) hx.spawn(hn, p.x, p.y, p.z + 0.06, hm.loop ? { duration: 1.2 } : {}); } // [HMFX48] flame ward
    if (ctx.addGlow) this.ward.light = ctx.addGlow(p.x, p.y, p.z, { color: LAVA, intensity: 4, range: 3.0, life: S.t, fadeIn: 0.2, lift: 0.7 });
    this.G.toast('Flame Ward: the fire forgets you', 1.4);
  }
  endWard() {
    const w = this.ward; if (!w) return;
    if (w.f) w.f[0].remove(w.f[1]);
    if (w.light) w.light.kill = true;
    this.ward = null;
  }
  // Magma Hound (III): a magma hound runs at your side for 20 s (it takes the place of any other summon); only where the hound sheet is (Muspelheim)
  doHound(S) {
    const ctx = this.ctx, p = ctx.player, G = this.G, roles = ctx.actors.meta.roles;
    const moss = S.look === 'mossgolem';   // [VANAHEIM] Growth III: SPELLS.moss_golem reuses the hound minion with the moss_golem glow sheet
    const role = moss ? (roles.moss_golem ? 'moss_golem' : null) : HOUND_ROLES.find((r) => roles[r]);
    if (!role && moss) { this.cd.hound = 0; this.cd.spell = 0; G.toast('No moss answers here: the Moss Golem needs Vanaheim\'s loam.', 2.2); return; }
    if (!role) { this.cd.hound = 0; this.cd.spell = 0; G.toast('No hound answers here: the Magma Hound needs Muspelheim\'s heat.', 2.2); return; }
    const LK = HOUND_LOOK[role] || HOUND_LOOK.magma_hound, GLOW = LK.color || LAVA;
    if (this.summon) this.unsummon();
    const fv = FV[p.facing] || [0, 1], hp = Math.round(HOUND.hp * this.M.summonMul);
    const x = p.x + fv[0] * 1.0 + 0.3, z = p.z + fv[1] * 1.0;
    this.calSpawn('hound_summon', x, ctx.heightAt(x, z), z + 0.05, {}) || (ctx.effects && ctx.effects.spawn('summon_poof', x, ctx.heightAt(x, z), z + 0.05));
    const a = ctx.addNpc({ id: 'summon', role, name: LK.name, pos: [x, z], behavior: 'idle', turn: false, speed: HOUND.speed });
    a.ai = true; a.noTalk = true; a.facing = p.facing;
    this.summon = { a, tier: 3, hound: true, D: { ...HOUND, name: LK.name, hp }, hp, life: S.life + this.M.summonLife, cd: 0.4, target: null, sparkT: 0.3 };
    if (ctx.addGlow) this.summon.light = ctx.addGlow(a.x, a.y, a.z, { color: GLOW, intensity: 4, range: 3.0, lift: 0.6, fadeIn: 0.4 });
    if (G.glow) G.glow.pool(x, z, GLOW, 0.6);
    G.audio.sfx('summon');
    G.toast(LK.toast, 1.6);
  }
  // [VANAHEIM] Vine Grasp ('root' kind): roots snare the nearest foe in place for S.life s (it can still swing); vine_grasp loops, then vine_grasp_end
  hasForesight() { const eq = (this.G.S && this.G.S.gear) || {}; return Object.values(eq).some((it) => it && (it.unique === 'foresight_charm' || it.id === 'foresight_charm')); }
  doRoot(S) {
    const ctx = this.ctx, p = ctx.player, G = this.G, dur = S.root || S.life || 2.0;
    const t = this.nearestEnemy(p, S.range || 6);
    if (!t) { this.cd.spell = 0; this.cd.root = 0; G.toast('Nothing in reach for the vines.', 1.4); return; }
    t.rootT = Math.max(t.rootT || 0, dur);
    if (S.dmg) this.hitFoe(t, this.out('spell', S.dmg), p, 0, PAL.gold);   // gearfx: vine grasp
    const a = t.a, gx = ctx.gamefx;
    if (!(gx && gx.spawn && gx.meta && gx.meta.effects && gx.meta.effects.vine_grasp && gx.spawn('vine_grasp', a.x, a.y, a.z + 0.05, { duration: dur })))
      ctx.effects && ctx.effects.spawn('summon_poof', a.x, a.y, a.z + 0.05);
    G.toast('Vine Grasp: roots hold it fast.', 1.2);
  }
  updateCaldera(dt, frozen) {
    const ctx = this.ctx, p = ctx.player;
    if (frozen) return;
    // burns on foes (Fire Wave, Magma Pool, motes, Flame Ward's reflect)
    for (const e of this.alive()) {
      const b = e.burn; if (!b) continue;
      if ((b.t -= dt) > 0) continue;
      b.t = 0.5; const n = Math.min(b.left, Math.max(1, Math.ceil(b.left / 4))); b.left -= n;
      this.damageEnemy(e, n, null, 0, LAVA);
      if (b.left <= 0) e.burn = null;
    }
    // magma pools
    for (const m of this.magma) {
      m.t -= dt;
      if ((m.tick -= dt) <= 0) {
        m.tick = 0.5;
        for (const e of this.alive()) if (Math.hypot(e.a.x - m.x, e.a.z - m.z) < m.r + e.D.r * 0.5 && Math.abs(e.a.y - ctx.heightAt(m.x, m.z)) < 1.0) this.damageEnemy(e, this.out('spell', m.dmg), null, 0, LAVA);
      }
      if (m.t <= 0) this.coolMagma(m);
    }
    if (this.magma.some((m) => m.done)) this.magma = this.magma.filter((m) => !m.done);
    // the ward follows you
    const w = this.ward;
    if (w) {
      w.t -= dt;
      if (w.f) { w.f[1].x = p.x; w.f[1].y = p.y; w.f[1].z = p.z + 0.08; }
      if (w.light) w.light.pos.set(p.x, p.y, p.z);
      if (w.t <= 0 || this.G.downed) this.endWard();
    }
    // the swarm: orbit, then fly
    const sw = this.swarm;
    if (sw) {
      sw.t -= dt;
      if (sw.cloud) { sw.cloud[1].x = p.x; sw.cloud[1].y = p.y; sw.cloud[1].z = p.z + 0.05; }
      if (sw.light) sw.light.pos.set(p.x, p.y, p.z);
      if (sw.t <= 0 && !sw.launched) {
        sw.launched = true;
        const foes = this.alive().filter((e) => dist(e.a, p) < 7 && Math.abs(e.a.y - p.y) < 1.5).sort((a, b) => dist(a.a, p) - dist(b.a, p)).slice(0, 6);
        this.motes.forEach((m, i) => { m.state = 'fly'; m.target = foes.length ? foes[i % foes.length] : null; m.t = 0; });
      }
    }
    for (const m of this.motes) {
      m.t += dt;
      if (m.state === 'orbit') {
        const a = m.a0 + m.t * Math.PI * 2.2, r = 0.95;
        m.x = p.x + Math.cos(a) * r; m.z = p.z + Math.sin(a) * r * 0.75; m.y = p.y + 0.35 + Math.sin(a * 2) * 0.12;
      } else if (m.state === 'fly') {
        const e = m.target;
        let tx, tz, ty;
        if (e && e.state !== 'dead' && e.state !== 'gone') { tx = e.a.x; tz = e.a.z; ty = e.a.y + 0.4; }
        else { const a = m.a0; tx = m.x + Math.cos(a) * 3; tz = m.z + Math.sin(a) * 3; ty = m.y; if (m.t > 0.6) m.state = 'gone'; }
        const dx = tx - m.x, dz = tz - m.z, d = Math.hypot(dx, dz), st = Math.min(d, 9 * dt);
        if (d > 0.01) { m.x += dx / d * st; m.z += dz / d * st; m.y += (ty - m.y) * Math.min(1, dt * 6); }
        if (e && e.state !== 'dead' && e.state !== 'gone' && d < 0.35 + e.D.r * 0.6) {
          this.hitFoe(e, this.out('spell', m.S.dmg), m, 0.15, PAL.gold); this.ignite(e, m.S.burn);   // gearfx: swarm mote (a bolt). Burns and magma ticks stay on damageEnemy and do not proc.
          if (sw) sw.hits++; this.swarmHits = (this.swarmHits || 0) + 1;
          if (ctx.effects && ctx.effects.meta.effects.ember_pop) ctx.effects.spawn('ember_pop', e.a.x, e.a.y, e.a.z + 0.1);
          m.state = 'gone';
        }
        if (m.t > 3) m.state = 'gone';
      }
      if (m.f) { m.f[1].x = m.x; m.f[1].y = m.y; m.f[1].z = m.z + 0.1; }
      if (m.state === 'gone' && m.f) { m.f[0].remove(m.f[1]); m.f = null; }
    }
    if (this.motes.length && this.motes.every((m) => m.state === 'gone')) { this.motes = []; if (sw && sw.launched) this.swarm = null; }
  }
  // ---------------------------------------------------------------- [NIFLHEIM-2] the Frostweave school
  // the pack effect where this area's game-fx atlas has it (Niflheim), else the stock spells-atlas stand-in; returns [atlas, fx] or null
  frostFx(name, stock, x, y, z, o) {
    const g = this.calFx(name); if (g) return [g, g.spawn(name, x, y, z, o)];
    const e = this.ctx && this.ctx.effects; return e && stock && e.meta.effects[stock] ? [e, e.spawn(stock, x, y, z, o)] : null;
  }
  chill(e, t) { if (e) e.chillT = Math.max(e.chillT || 0, t); }   // half speed (the step() in updateEnemy)
  // Ice Lance (I): a piercing bolt of ice 6.5 m straight ahead; every foe on the line takes the hit (as the lance passes it) and is chilled 2 s
  doLance(S) {
    const ctx = this.ctx, p = ctx.player, fv = FV[p.facing] || [0, 1];
    for (let i = 0; i < 4; i++) {
      const d = 1.0 + i * 1.6, x = p.x + fv[0] * d, z = p.z + fv[1] * d;
      this.later.push({ t: i * 0.07, fn: () => { if (this.ctx === ctx) this.frostFx('ice_lance', 'coldfire_bolt', x, ctx.heightAt(x, z) + 0.9, z + 0.06, { duration: 0.25, fadeIn: 0 }); } });
      if (i === 0) this.later.push({ t: 0, fn: () => { if (this.ctx !== ctx) return; { const hx = ctx.hmfx, hn = HMFX_BOLT.lance, hm = hx && hn && hx.meta.effects[hn]; if (hm) hx.spawn(hn, x, ctx.heightAt(x, z), z + 0.06, hm.loop ? { duration: 1.2 } : {}); } } }); // [HMFX48] frost bolt
    }
    if (ctx.addGlow) ctx.addGlow(p.x + fv[0] * 3, p.y, p.z + fv[1] * 3, { color: FROST, intensity: 6, range: 4.0, life: 0.5, fadeIn: 0.05, lift: 0.8 });
    const hit = [];
    for (const e of this.alive()) {
      const dx = e.a.x - p.x, dz = e.a.z - p.z, along = dx * fv[0] + dz * fv[1], side = Math.abs(dx * fv[1] - dz * fv[0]);
      if (along < 0 || along > S.range + e.D.r || side > 0.6 + e.D.r * 0.5 || Math.abs(e.a.y - p.y) > 1.2) continue;
      hit.push(e);
      this.later.push({ t: along / S.speed, fn: () => { if (this.ctx === ctx && e.state !== 'dead' && e.state !== 'gone') { this.hitFoe(e, this.out('spell', S.dmg), p, S.push, PAL.sky); this.chill(e, S.chill); } } });
      this.later.push({ t: along / S.speed, fn: () => { if (this.ctx === ctx && e.state !== 'dead' && e.state !== 'gone') { const hx = ctx.hmfx, hn = HMFX_FLASH.frost, hm = hx && hn && hx.meta.effects[hn]; if (hm) hx.spawn(hn, e.a.x, e.a.y, e.a.z + 0.06, hm.loop ? { duration: 1.2 } : {}); } } }); // [HMFX48] frost hit
    }
    this.lastLance = { n: hit.length, ids: hit.map((e) => e.id) };
  }
  // Frost Nova (I): a ring of ice around you, 2.8 m: damage and a 3 s chill on every foe inside
  doFrostNova(S) {
    const ctx = this.ctx, p = ctx.player;
    this.frostFx('frost_nova', 'frost_puff', p.x, p.y, p.z + 0.05, { duration: 0.9, fadeIn: 0 });
    if (ctx.addGlow) ctx.addGlow(p.x, p.y, p.z, { color: FROST, intensity: 8, range: 4.6, life: 0.7, fadeIn: 0.05, lift: 0.4 });
    const hit = [];
    for (const e of this.alive()) {
      if (dist(e.a, p) > S.radius + e.D.r * 0.5 || Math.abs(e.a.y - p.y) > 1.2) continue;
      hit.push(e); this.hitFoe(e, this.out('spell', S.dmg), p, S.push, PAL.sky); this.chill(e, S.chill);   // gearfx: frost nova
    }
    this.lastNova = { n: hit.length, ids: hit.map((e) => e.id) };
  }
  // Mist Veil (II): a cloud of violet mist for 4 s: foes beyond arm's reach lose you (they go home), mist stalkers cannot see you at all
  doVeil(S) {
    const ctx = this.ctx, p = ctx.player;
    this.endVeil();
    this.veil = { t: S.t, near: S.near, f: this.frostFx('mist_veil', 'frost_puff', p.x, p.y, p.z + 0.08, { duration: S.t }) };
    this.G.toast('Mist Veil: they cannot find you', 1.4);
  }
  endVeil() { const v = this.veil; if (!v) return; if (v.f) v.f[0].remove(v.f[1]); this.veil = null; }
  veilHides(e, d) { const v = this.veil; return !!v && (/stalker/.test(e.a.role || '') || /stalker/.test(e.D.name || '') || d > v.near) && !e.D.boss; }
  // Frost Spirits (II): two frost spirits circle you for 15 s; each throws an ice shard at the nearest foe in 6 m every 1.2 s (works in any area: no sprite, pack / stock fx)
  doSpirits(S) {
    const ctx = this.ctx, p = ctx.player;
    for (const s2 of this.spirits) if (s2.f) s2.f[0].remove(s2.f[1]);
    this.spirits = [0, 1].map((i) => ({ i, a0: i * Math.PI, t: 0, life: S.life + this.M.summonLife, cd: 0.6 + i * 0.6, x: p.x, y: p.y, z: p.z, S,
      f: this.frostFx('spirit_swarm', 'coldfire_motes', p.x, p.y, p.z, { duration: S.life + this.M.summonLife + 0.5 }) }));
    this.spiritHits = 0;
    if (ctx.effects && ctx.effects.meta.effects.summon_poof) ctx.effects.spawn('summon_poof', p.x, p.y, p.z + 0.05);
    this.G.audio.sfx('summon'); this.G.toast('Two frost spirits answer!', 1.6);
  }
  updateFrost(dt, frozen) {
    const ctx = this.ctx, p = ctx.player;
    if (frozen) return;
    for (const e of this.enemies) { if (e.chillT > 0) { e.chillT = Math.max(0, e.chillT - dt); if (!(e.chillT > 0) && e.chillPct) e.chillPct = 0; } if (e.rootT > 0) e.rootT = Math.max(0, e.rootT - dt); if (e.frozenT > 0) e.frozenT = Math.max(0, e.frozenT - dt); if (e.procT) for (const id in e.procT) e.procT[id] = Math.max(0, e.procT[id] - dt); }   // gearfx: freeze timer, boss chill clears, per-target proc ICD
    const v = this.veil;
    if (v) { v.t -= dt; if (v.f) { v.f[1].x = p.x; v.f[1].y = p.y; v.f[1].z = p.z + 0.08; } if (v.t <= 0 || this.G.downed) this.endVeil(); }
    for (const s2 of this.spirits) {
      s2.t += dt; s2.life -= dt;
      const a = s2.a0 + s2.t * 1.8; s2.x = p.x + Math.cos(a) * 1.1; s2.z = p.z + Math.sin(a) * 0.8; s2.y = p.y + 1.0 + Math.sin(a * 2) * 0.15;
      if (s2.f) { s2.f[1].x = s2.x; s2.f[1].y = s2.y; s2.f[1].z = s2.z + 0.1; }
      if ((s2.cd -= dt) <= 0) {
        const e = this.nearestEnemy(s2, s2.S.reach);
        s2.cd = s2.S.every;
        if (e) { this.frostFx('ice_lance', 'coldfire_bolt', e.a.x, e.a.y + 0.6, e.a.z + 0.1, { duration: 0.3, fadeIn: 0 }); this.damageEnemy(e, this.out('summon', s2.S.dmg), s2, 0.1, PAL.sky); this.chill(e, 1.0); this.spiritHits++; // [HMFX48] dark spirit bolt
          { const hx = ctx.hmfx, hn = HMFX_BOLT.spirits, hm = hx && hn && hx.meta.effects[hn]; if (hm) hx.spawn(hn, e.a.x, e.a.y, e.a.z + 0.06, hm.loop ? { duration: 1.2 } : {}); } // [HMFX48] dark bolt
          { const hx = ctx.hmfx, hn = HMFX_IMPACT.dark, hm = hx && hn && hx.meta.effects[hn]; if (hm) hx.spawn(hn, e.a.x, e.a.y, e.a.z + 0.06, hm.loop ? { duration: 1.2 } : {}); } // [HMFX48] dark impact
          { const hx = ctx.hmfx, hn = HMFX_FLASH.dark, hm = hx && hn && hx.meta.effects[hn]; if (hm) hx.spawn(hn, e.a.x, e.a.y, e.a.z + 0.06, hm.loop ? { duration: 1.2 } : {}); } } // [HMFX48] dark hit
      }
      if (s2.life <= 0 || this.G.downed) { if (s2.f) s2.f[0].remove(s2.f[1]); s2.f = null; s2.done = true; }
    }
    if (this.spirits.some((s2) => s2.done)) this.spirits = this.spirits.filter((s2) => !s2.done);
  }
  qaFrost() {
    const v = this.veil;
    return { veil: v ? { t: +v.t.toFixed(2), fx: !!v.f } : null, spirits: this.spirits.map((s2) => ({ life: +s2.life.toFixed(1), fx: !!s2.f })), spiritHits: this.spiritHits || 0,
             lance: this.lastLance || null, nova: this.lastNova || null, chilled: this.enemies.filter((e) => e.chillT > 0).map((e) => e.id),
             golem: this.summon && this.summon.ice ? { role: this.summon.a.role, life: +this.summon.life.toFixed(1) } : null, cd: { veil: this.cd.veil, spirits: this.cd.spirits, igolem: this.cd.igolem } };
  }
  qaCaldera() {
    const w = this.ward, sw = this.swarm;
    return { magma: this.magma.map((m) => ({ x: +m.x.toFixed(2), z: +m.z.toFixed(2), r: m.r, t: +m.t.toFixed(2), fx: m.fx.map(([, f]) => f.name) })), motes: this.motes.map((m) => m.state),
             swarm: sw ? { t: +sw.t.toFixed(2), hits: sw.hits, launched: !!sw.launched } : null, ward: w ? { t: +w.t.toFixed(2), take: w.take, refl: w.refl, fx: !!w.f } : null,
             wave: this.lastWave || null, burns: this.enemies.filter((e) => e.burn).map((e) => e.id), cd: { swarm: this.cd.swarm, ward: this.cd.ward, hound: this.cd.hound } };
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
    s.hp -= dmg; s.a.flashT = this.flashOK() ? 0.12 : 0;
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
    // camera framing scales with big foes: breathe the camera out while one is engaged and near (eased in the engine).
    // framePull on a def replaces the scale curve for that foe only. frameLift raises the look target (Mordrath's crown).
    let pullF = 1, liftF = 0;
    for (const e of this.enemies) {
      const k = e.D.scale || 1;
      if (k > 1 && (e.state === 'chase' || e.state === 'attack' || e.D.framed) && dist(e.a, ctx.player) < (e.D.aggro || 6) + 3) {
        pullF = Math.max(pullF, e.D.framePull > 0 ? e.D.framePull : framePullFor(k));
        const lift = e.D.frameFit ? frameLiftFor(e.D, ctx.player, e.a) : (e.D.frameLift > 0 ? e.D.frameLift : 0);
        if (lift > 0) liftF = Math.max(liftF, lift);
      }
    }
    if (ctx.frameLook) ctx.frameLook(liftF);
    if (ctx.framePull) ctx.framePull(pullF);
    for (const e of this.enemies) {
      let b = this.bars.get(e.id);
      const show = (e.hp < e.D.hp || e.state === 'chase' || e.state === 'attack' || (e.engaged && (e.D.boss || e.D.rare))) && e.state !== 'dead' && e.state !== 'gone';   // [NIFLHEIM-2] an engaged boss keeps its bar wherever it stands (Veyra at the top edge of the portrait view)
      if (e.light) e.light.pos.set(e.a.x, e.a.y, e.a.z);
      if (!show) { if (b) b.hidden = true; if ((e.D.boss || e.D.rare) && this.bossEl && this.bossEl.dataset.id === e.id) this.bossEl.hidden = true; continue; }
      if (!b) { b = document.createElement('div'); b.className = 'ebar'; b.innerHTML = '<i></i>'; this.layer.appendChild(b); this.bars.set(e.id, b); }
      b.hidden = false;
      if (e.light) e.light.pos.set(e.a.x, e.a.y, e.a.z);
      if (e.D.boss || e.D.rare) { this.bossBar(e); b.hidden = true; continue; }   // bosses and rares: a named bar (low only when the def sets barLow)
      const s = ctx.project(e.a.x, e.a.y + (e.a.lift || 0) + (e.a.role === 'golem' || e.D.slam ? 1.75 : 1.85) * (e.D.scale || 1), e.a.z);
      b.style.transform = `translate(${Math.round(s.x - 15)}px, ${Math.round(s.y)}px)`;
      b.firstChild.style.width = Math.max(0, Math.round(26 * e.hp / e.D.hp)) + 'px';
    }
  }
  // a named parchment bar instead of a little world bar. Top of the screen, unless the def sets barLow.
  bossBar(e) {
    if (!this.bossEl) {
      const el = document.createElement('div'); el.id = 'bossbar'; el.innerHTML = '<b></b><span><i></i></span>';
      (document.getElementById('hud') || document.body).appendChild(el); this.bossEl = el;
    }
    const el = this.bossEl; el.hidden = false;
    el.classList.toggle('low', bossBarLow(e.D));
    el.firstChild.textContent = e.D.name; el.dataset.id = e.id;
    el.firstChild.style.color = e.D.rare ? e.D.glow : '';   // a rare's name in its element colour
    el.querySelector('i').style.width = Math.max(0, Math.round(100 * e.hp / e.D.hp)) + '%';
  }
  // QA helpers
  qa() {
    return { hp: this.G.S.hp, max: this.maxHp(), st: Math.round(this.st), cd: { ...this.cd }, god: this.godT, gfx: this.gfx,   // gearfx: lastProc + procs fired count
             enemies: this.enemies.map((e) => ({ id: e.id, role: e.a.role, hp: e.hp, state: e.state, rare: !!e.rare, name: e.D.name, x: +e.a.x.toFixed(2), z: +e.a.z.toFixed(2) })),
             summon: this.summon ? { role: this.summon.a.role, hp: this.summon.hp, life: +this.summon.life.toFixed(1), tier: this.summon.tier, light: !!this.summon.light, name: this.summon.a.name } : null };
  }
}
function walkStop(ctx) { ctx.stopWalk && ctx.stopWalk(); }
