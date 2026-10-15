// [SVARTALFHEIM] The Foreman (story 7 C4 mini-boss, 8.x): a 2.8x brass overseer construct that guards the Assembly Line (clockdeep2 C4).
// Whistles up 2 forgeconstructs every 20 s (his furnace belly is the weak point while he whistles: x2 damage for 2 s), a steam-blast
// cone (60 deg, 4 m, 14 dmg) with a telegraph, and the stamping charge is his normal heavy swing. Always drops 1 clock spring (The
// Masterwork) + 2 deep brass; once dead he stays dead (flags.cd_foreman). Deviation: the stamping charge is the plain heavy attack.
import { ENEMIES } from './heroes.js';
import { XP } from './progress.js';

const flags = (S) => (S.flags = S.flags || {});
export const FOREMAN_AT = [0.0, 31.0];
Object.assign(ENEMIES, { foreman: { name: 'The Foreman', scale: 2.8, hp: 540, dmg: 21, speed: 1.0, reach: 3.0, windup: 0.75, cd: 2.0, aggro: 8, r: 0.85, push: 0.15, heavy: true, boss: true, minion: 'forgeconstruct', whistle: { every: 20, n: 2 }, steam: { cone: 60, len: 4, dmg: 14 }, weakWhistle: 2, glow: '#f2a63a', noRespawn: true } });
Object.assign(XP, { foreman: 330 });

export class Foreman {
  constructor(sv) { this.sv = sv; this.G = sv.G; this.e = null; this.n = 0; }
  get ctx() { return this.sv.ctx; }
  attach(area) {
    this.e = null; this.n = 0;
    if (area !== 'clockdeep2' || flags(this.G.S).cd_foreman) return;
    const ctx = this.ctx;
    setTimeout(() => { if (this.sv.ctx === ctx && !this.e) this.spawn(); }, 500);
  }
  spawn() {
    const G = this.G, C = G.combat, ctx = this.ctx; if (!C || !C.ctx || !ctx) return null;
    const e = C.spawnEnemy({ id: 'cd_foreman', role: 'foreman', def: 'foreman', pos: FOREMAN_AT.slice(), once: true, noLoot: true }, false);
    this.e = e; this.hook(e); return e;
  }
  hook(e) {
    const self = this, G = this.G, C = G.combat, D = e.D; let whistleT = 8, steamT = 5; e.whistling = 0; e.steamAt = 0;
    const prev = e.mods && e.mods.hurt;
    e.mods = { ...(e.mods || {}), hurt(en, dmg) { const d = prev ? prev(en, dmg) : dmg; return en.whistling > 0 ? d * D.weakWhistle : d; } };   // the furnace belly shows while he whistles
    e.tick = (en, dt, frozen) => {
      const ctx = self.ctx; if (!ctx || frozen || C.peace || en.state === 'idle' || en.state === 'dead') return;
      const a = en.a, p = ctx.player, d = Math.hypot(p.x - a.x, p.z - a.z);
      en.whistling = Math.max(0, en.whistling - dt); whistleT -= dt; steamT -= dt;
      if (whistleT <= 0) { whistleT = D.whistle.every; self.whistle(); }
      if (en.steamAt > 0) { en.steamAt -= dt; if (en.steamAt <= 0) self.steam(); }
      else if (steamT <= 0 && d < D.steam.len + 0.5) { steamT = 7; en.steamAt = 0.7; en.steamDir = Math.atan2(p.z - a.z, p.x - a.x); if (ctx.effects && ctx.effects.meta.effects.frost_puff) ctx.effects.spawn('frost_puff', a.x + Math.cos(en.steamDir) * 1.6, a.y + 0.6, a.z + Math.sin(en.steamDir) * 1.6); }   // the telegraph: a puff in front
    };
    e.onKill = () => { const S = G.S; flags(S).cd_foreman = 1; G.give('clock_spring', 1); G.give('deep_brass', 2); G.toast('The Foreman winds down. Found: a clock spring, 2 deep brass.', 3); G.save && G.save(); G.refreshMarkers && G.refreshMarkers(); };
  }
  whistle() {
    const e = this.e, C = this.G.combat, ctx = this.ctx; if (!e || !ctx) return 0;
    e.whistling = 2.0; let made = 0;
    const alive = (C.enemies || []).filter((x) => /^fm_w/.test(x.sp.id) && x.state !== 'dead').length;
    if (ctx.effects && ctx.effects.meta.effects.frost_puff) ctx.effects.spawn('frost_puff', e.a.x, e.a.y + 1.8, e.a.z + 0.05);
    this.G.toast('The Foreman blows his whistle! (his furnace belly is open)', 2);
    for (const dx of [-1.6, 1.6]) { if (alive + made >= 4) break; C.spawnEnemy({ id: `fm_w${this.n++}`, role: 'forgeconstruct', pos: [e.a.x + dx, e.a.z + 1.8], once: true }, true); made++; }
    return made;
  }
  steam() {
    const e = this.e, ctx = this.ctx, C = this.G.combat; if (!e || !ctx || e.state === 'dead') return false;
    const a = e.a, p = ctx.player, D = e.D.steam, ang = Math.atan2(p.z - a.z, p.x - a.x), da = Math.abs(((ang - e.steamDir + Math.PI * 3) % (Math.PI * 2)) - Math.PI);
    for (let k = 0; k < 3; k++) if (ctx.effects && ctx.effects.meta.effects.frost_puff) ctx.effects.spawn('frost_puff', a.x + Math.cos(e.steamDir) * (1.4 + k * 1.1), a.y + 0.6, a.z + Math.sin(e.steamDir) * (1.4 + k * 1.1));
    const hit = Math.hypot(p.x - a.x, p.z - a.z) <= D.len && da <= (D.cone / 2) * Math.PI / 180;
    if (hit && C.hurtPlayer) C.hurtPlayer(D.dmg, a, 0.6);
    return hit;
  }
  qa() { const e = this.e; return { up: !!e && e.state !== 'dead', scale: e ? e.D.scale : 0, hp: e ? Math.round(e.hp) : 0, whistling: e ? e.whistling > 0 : false, minions: ((this.G.combat && this.G.combat.enemies) || []).filter((x) => /^fm_w/.test(x.sp.id) && x.state !== 'dead').length, dead: !!flags(this.G.S).cd_foreman }; }
  qaWeak() { const e = this.e; if (!e) return null; e.whistling = 0; const a = e.mods.hurt(e, 10); e.whistling = 2; return [a, e.mods.hurt(e, 10)]; }
}
