// [HELHEIM] Helheim foes and bosses: Lord Vesperin (O5, 3x, bat split) and Mordrath, the Pale Sovereign (O9, 8x, 3 phases via swapRole).
// Split out of helheim.js the way other realms keep boss code apart. Driven by Helheim (helheim.js) through HelBoss.
import { ENEMIES } from './heroes.js';
import { XP } from './progress.js';
import { BASES } from './rares.js';

const F = (S) => S.flags || {};
const flags = (S) => (S.flags = S.flags || {});
const q = (S, k) => (S.quests || {})[k] || 0;
const defiant = (S) => F(S).hel === 'defiant';
const helRealm = (S) => (defiant(S) ? 'gate' : 'embassy');

Object.assign(ENEMIES, {
  shade: { name: 'Shade', hp: 60, dmg: 10, speed: 1.6, reach: 1.4, windup: 0.6, cd: 1.8, aggro: 7, r: 0.4, push: 0.4, float: true, element: 'dark' },
  gate_shade: { name: 'Gate shade', scale: 1.2, hp: 120, dmg: 12, speed: 1.4, reach: 1.6, windup: 0.7, cd: 2.0, aggro: 8, r: 0.5, push: 0.3, float: true, element: 'dark', respawn: 1e9 },
  soul_wraith: { name: 'Soul-wraith', scale: 1.3, hp: 90, dmg: 13, speed: 1.7, reach: 1.6, windup: 0.6, cd: 1.9, aggro: 8, r: 0.5, push: 0.3, float: true, element: 'cold' },
  grave_lantern: { name: 'Grave lantern', hp: 70, dmg: 11, speed: 1.0, reach: 1.4, windup: 0.8, cd: 2.2, aggro: 6, r: 0.4, push: 0.4, bolt: 'bolt', element: 'cold' },
  bone_elemental: { name: 'Bone elemental', scale: 1.6, hp: 180, dmg: 16, speed: 1.0, reach: 2.0, windup: 0.9, cd: 2.3, aggro: 7, r: 0.6, push: 0.2, heavy: true, element: 'dark' },
  garnet_golem: { name: 'Garnet golem', scale: 1.8, hp: 240, dmg: 18, speed: 0.7, reach: 2.1, windup: 1.1, cd: 2.6, aggro: 6, r: 0.7, push: 0.1, heavy: true },
  skeleton_line: { name: 'Skeleton line', hp: 65, dmg: 10, speed: 1.5, reach: 1.5, windup: 0.5, cd: 1.7, aggro: 7, r: 0.4, push: 0.5, element: 'dark' },
  lich: { name: 'Lich', scale: 1.4, hp: 150, dmg: 15, speed: 1.1, reach: 1.6, windup: 0.6, cd: 2.0, aggro: 8, r: 0.5, push: 0.3, bolt: 'bolt', element: 'dark' },
  gloam_knight: { name: 'Gloam Knight', hp: 110, dmg: 14, speed: 1.8, reach: 1.6, windup: 0.5, cd: 1.6, aggro: 8, r: 0.45, push: 0.4, elite: true, element: 'dark' },
  odric: { name: 'Ser Odric Gravemantle', scale: 3, hp: 460, dmg: 18, speed: 1.3, reach: 2.6, windup: 0.6, cd: 1.8, aggro: 9, r: 0.8, push: 0.2, heavy: true, boss: true, trial: true, respawn: 1e9, element: 'dark' },
  vesperin_bat: { name: 'Mist-bat', scale: 1.6, hp: 60, dmg: 9, speed: 2.4, reach: 1.4, windup: 0.4, cd: 1.4, aggro: 10, r: 0.5, push: 0.4, float: true, element: 'dark', respawn: 1e9 },
  vesperin: { name: 'Lord Vesperin', scale: 3, hp: 900, dmg: 20, speed: 1.6, reach: 2.6, windup: 0.6, cd: 1.8, aggro: 10, r: 0.9, push: 0.2, heavy: true, boss: true, miniboss: true, element: 'dark', phases: [0.5], respawn: 1e9 },
  mordrath: { name: 'Mordrath, the Pale Sovereign', scale: 8, framed: true, plate: true, element: 'dark', phases: [0.6, 0.25], hp: 2800, dmg: 30, speed: 0.9, reach: 6.0, windup: 1.0, cd: 2.4, aggro: 14, r: 2.2, push: 0.05, heavy: true, boss: true, minion: 'shade', respawn: 1e9 },
});
Object.assign(XP, { shade: 35, gate_shade: 80, soul_wraith: 55, grave_lantern: 40, bone_elemental: 90, garnet_golem: 110, skeleton_line: 30, lich: 85, gloam_knight: 70, odric: 0, vesperin_bat: 20, vesperin: 500, mordrath: 1400 });
Object.assign(BASES, {
  gravelamp: { name: 'Gravelamp Elder', scale: 2, hp: 300, dmg: 16, speed: 1.0, reach: 2.0, windup: 0.7, cd: 2.0, aggro: 8, r: 0.7, push: 0.2, element: 'cold', xp: 180 },
  hollowchoir: { name: 'The Hollow Choir', scale: 3, hp: 420, dmg: 18, speed: 0.9, reach: 2.4, windup: 0.8, cd: 2.2, aggro: 9, r: 0.9, push: 0.15, element: 'dark', xp: 240 },
});

export const BOSS_AT = { vesperin: [0.0, -58.0], mordrath: [0.0, -43.4] };
export const MORDRATH_ROLES = ['mordrath', 'mordrath_p2', 'mordrath_p3'];
const O9_CHAINS = [[-6.6, -46.0], [-6.6, -42.0], [-3.0, -49.4], [3.0, -49.4]];

export class HelBoss {
  constructor(h) { this.h = h; this.G = h.G; this.reset(); }
  reset() { this.boss = null; this.pend = []; this.bt = 0; this.bt2 = 0; }
  get ctx() { return this.h.ctx; }
  phaseOf(e) { const fr = e.hp / e.D.hp; return 1 + (e.D.phases || []).filter((t) => fr < t).length; }
  start(which, pos) {
    const G = this.G, S = G.S, at = pos || BOSS_AT[which]; if (this.h.cb[which] || !at) return null;
    G.toast(which === 'vesperin' ? '"A guest. Living, too. How rare, how warm."' : '"Another soul walks into my house."', 3.0);
    this.boss = this.h.foe({ id: which, role: which, pos: at.slice() }, () => this.down(which));
    if (!this.boss) return null;
    this.boss.which = which; this.bt = 3; this.bt2 = 6;
    if (defiant(S)) [[-3.0, 2.0], [3.0, 2.0]].forEach(([x, z], i) => this.h.foe({ id: which + '_gk' + i, role: 'gloam_knight', pos: [at[0] + x, at[1] + z] }, () => {}));
    return this.boss;
  }
  swapRole(e, role) {
    const A = this.ctx && this.ctx.actors, fr = A && A.sheetOf && A.sheetOf(role), a = e.a; if (!fr) return false;
    if (fr.S && a.S && fr.S !== a.S) return false;
    a.role = role; a.roleRow = fr.role.row; a.kind = fr.role.kind; a.anims = fr.role.anims || ['idle', 'walk']; a.canCast = a.anims.includes('cast'); a.act = null; a.castT = 0; return true;
  }
  strike(kind, x, z, dmg, delay, r) {
    const c = this.ctx; if (!c) return;
    this.h.fxAt(c, kind === 'chain' ? 'telegraph_line' : 'slam_ring', x, c.heightAt(x, z), z, { duration: delay, fadeIn: 0 });
    this.pend.push({ t: delay, x, z, dmg, r, kind });
  }
  tickStrikes(dt) {
    const c = this.ctx; if (!c || !this.pend.length) return;
    const p = c.player;
    this.pend = this.pend.filter((s) => {
      s.t -= dt; if (s.t > 0) return true;
      if (Math.hypot(p.x - s.x, p.z - s.z) < s.r && this.G.combat && this.G.combat.hurtPlayer) this.G.combat.hurtPlayer(s.dmg, { x: s.x, z: s.z }, 0.5);
      return false;
    });
  }
  tickBoss(dt) {
    const e = this.boss, c = this.ctx, G = this.G; if (!e || !c || e.state === 'dead' || e.state === 'gone') return;
    const p = c.player, ph = this.phaseOf(e); e.phaseN = ph;
    this.bt -= dt; this.bt2 -= dt;
    const near = Math.hypot(e.a.x - p.x, e.a.z - p.z) < 18;
    if (e.which === 'vesperin') {
      if (this.bt <= 0 && near && !e.split) { this.bt = 4.2; this.strike('bat', p.x, p.z, 18, 0.9, 1.5); }
      if (this.bt2 <= 0 && near && !e.split) { this.bt2 = 8; this.strike('ring', p.x, p.z, 10, 1.2, 1.8); }
      if (ph >= 2 && !e.p2) {
        e.p2 = 1; e.split = 1; G.toast('He splits into three mist-bats! Hit the one with a shadow.', 3.0);
        e.bats = [[-3.0, 1.5], [0.0, 3.0], [3.0, 1.5]].map(([x, z], i) => this.h.foe({ id: 'vbat' + i, role: 'vesperin_bat', pos: [e.a.x + x, e.a.z + z] }, () => { if (i === 1) e.split = 0; }));
      }
      if (e.split) e.hp = Math.max(e.hp, e.D.hp * 0.5);
      return;
    }
    if (e.which === 'mordrath') {
      if (e.ph0 !== ph) { e.ph0 = ph; this.swapRole(e, MORDRATH_ROLES[ph - 1]); }
      if (this.bt <= 0 && near) { this.bt = ph === 1 ? 4.6 : 3.8; this.strike('sweep', p.x, p.z, 26, 1.0, 2.0); }
      if (ph === 1 && this.bt2 <= 0 && near) { this.bt2 = 6.5; const [x, z] = O9_CHAINS[Math.floor(Math.random() * O9_CHAINS.length)]; this.strike('chain', (x + p.x) / 2, (z + p.z) / 2, 20, 1.5, 1.6); }
      if (ph >= 2 && !e.p2) { e.p2 = 1; [[-4.0, 3.0, 'shade'], [4.0, 3.0, 'shade'], [0.0, 5.0, 'soul_wraith']].forEach(([x, z, r], i) => this.h.foe({ id: 'md_m' + i, role: r, pos: [e.a.x + x, e.a.z + z] }, () => {})); }
      if (ph === 2 && this.bt2 <= 0 && near) { this.bt2 = 6.0; this.strike('hunt', p.x, p.z, 24, 1.2, 1.8); }
      if (ph >= 3 && !e.p3) e.p3 = 1;
      if (e.p3) {
        if (this.bt2 <= 0 && near) { this.bt2 = 7.0; this.strike('crown', e.a.x + (p.x < e.a.x ? -4 : 4), e.a.z + 3.0, 28, 2.0, 5.0); }
        e.moteT = (e.moteT || 0) + dt;
        if (!e.mote && e.moteT > 5) { e.moteT = 0; const S = G.S; e.mote = { t: 3.0, seen: !!(F(S).inkling || (S.inv || {}).living_lamp) }; }
        if (e.mote) { e.mote.t -= dt; if (e.mote.t <= 0) { e.hp = Math.min(e.D.hp * 0.25, e.hp + e.D.hp * 0.02); e.mote = null; } }
      }
    }
  }
  moteSeen() { const e = this.boss; return !!(e && e.mote && e.mote.seen); }
  strikeMote() { const e = this.boss; if (e && e.mote) { e.mote = null; this.G.toast('The name slips free.', 1.8); } }
  down(which) {
    const G = this.G, S = G.S, f = flags(S), side = helRealm(S); this.boss = null; this.pend = [];
    if (which === 'vesperin') { f.hh_vesperin = 1; G.factions.add(side, 80, 'vesperin'); this.h.look('hh_vesperin', 'Lord Vesperin', ['"Fine! Take the cage. He\'ll only make more."']); }
    if (which === 'mordrath') {
      f.hh_boss = 1; f.hh_mordrath = 1; G.factions.add(side, 80, 'mordrath'); G.give('demon_heart', 1); if (defiant(S)) G.give('pale_crown', 1);
      if (q(S, 'ossuary') === 1) G.setQuest('ossuary', 2);
      this.h.look('hh_mordrath', 'Mordrath, the Pale Sovereign', ['(His plate cracks. The names rise like moths.)', '"Names... are such small things... to die for."'], () => {
        if (defiant(S) && q(S, 'ossuary') === 2) { G.setQuest('ossuary', 3); f.hh_resolved = 1; }
        if (f.rift_breaker && this.h.G.openDialogue) { /* tithe choice lives in helheim.js TALK.tithe */ }
        G.refreshMarkers && G.refreshMarkers(); G.save && G.save();
      });
    }
  }
  update(dt) { this.tickStrikes(dt); this.tickBoss(dt); }
  qaDefs() { return { bosses: Object.fromEntries(['vesperin', 'mordrath', 'odric'].map((k) => [k, { scale: ENEMIES[k].scale, plate: !!ENEMIES[k].plate, phases: ENEMIES[k].phases || null }])) }; }
  qaState() { const e = this.boss; return { which: e ? e.which : null, role: e ? e.a.role : null, phase: e ? e.phaseN : 0, p2: !!(e && e.p2), p3: !!(e && e.p3), split: !!(e && e.split), hp: e ? e.hp : null }; }
  qaHp(id, frac) { const e = this.G.combat.enemies.find((x) => x.id === id); if (!e) return false; e.hp = e.D.hp * frac; return true; }
  qaTick(dt = 0.1, n = 1) { for (let i = 0; i < n; i++) this.update(dt); return this.qaState(); }
}
