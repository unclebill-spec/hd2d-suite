// Hearthmoor Stage 6.4: Vanaheim's dungeons. Story: the Story bot's verdant_heart.md (Bill's decisions). Art: the Verdant
// Heart pack (art/verdant_heart/, Art bot 2026-10-06; installed by build.py install_verdant_heart).
// - Mossbrook (vanaheim): The Violet Spring (befriend): 2 braziers (Hollows rule), 3 red caps under the giant toadstools,
//   drop them in the spring. The root-cave under the Old Bough opens to the Rotwood once 'rotwood' starts (befriend: Burrowmoss's
//   word; conquer: you burn through the roots at the cave, E / A).
// - The Rotwood Hollow (rotwood, R0-R7): rune-sealed root door (3 braziers lit in the rune pulse order; a wrong order
//   snuffs them), Gnome Larder cages + the riddle door, the Weeping Root, the Regent's Bower: the Blight Regent (5.5x):
//   phase 2 (<60%) rot-fog Blight outside lit rim braziers, phase 3 (<25%) the frost-iron spike pulses blue: hits in the
//   pulse window strike the spike (double damage + a 3 s stagger). His fall drops the spike and grows the sapling stair.
// - The Verdant Heart (verdant, V0-V5): Bloom Stair's 3 root bowls (glow seed + spell -> a moss bridge), the Moonwell's
//   Thornmother rare (2.4x), and Hjortur (6x): the guardian trial on befriend (combat.js trial mode: he yields), the
//   corrupted stag on conquer.
import { MERIT } from './factions.js';

const flags = (S) => (S.flags = S.flags || {});
export const ally = (S) => ((S.flags || {}).alliance || {}).vanaheim;
export const capsAt = [[-5.6, -5.0], [9.6, 4.0], [-7.0, 6.0]];   // Mossbrook's giant toadstools (vanaheim.json props)
export const ROOT_CAVE = { pos: [8.4, -6.4], rect: [7.6, -7.2, 9.2, -6.0], to: 'rotwood', spawn: 'from_mossbrook', label: 'the root-cave under the Old Bough' };
export const REGENT = { phases: [0.6, 0.25], pulseEvery: 4.0, pulseWin: 1.3, stagger: 3.0, spikeMul: 2.0, blightMax: 3 };
const SPRING_AT = [4.6, -5.0];

export class Verdant {
  constructor(G) { this.G = G; this.ctx = null; this.area = null; this.boss = null; this.pulseT = 0; this.room = -1; this.order = []; this.blight = 0; }
  get S() { return this.G.S; }
  get gm() { return (this.ctx && this.ctx.scene.game) || {}; }
  attach(ctx, area) {
    this.ctx = ctx; this.area = area; this.boss = null; this.pulseT = 0; this.room = -1; this.order = []; this.blight = 0; this.fx = [];
    const S = this.S, F = flags(S), q = S.quests || {}, gm = ctx.scene.game || (ctx.scene.game = {});
    if (area === 'vanaheim' && (q.rotwood >= 1)) gm.exits = (gm.exits || []).filter((e) => e.to !== 'rotwood').concat([{ ...ROOT_CAVE }]);
    if (area === 'rotwood') {
      if (!F.rw_in) { F.rw_in = 1; this.G.drawLog && this.G.drawLog(); }
      if (F.rw_boss && gm.sapling) gm.exits = (gm.exits || []).filter((e) => e.to !== 'verdant').concat([{ rect: gm.sapling.rect, to: 'verdant', spawn: 'from_rotwood', label: gm.sapling.label }]);
      if (F.rw_boss) this.swapFx('rw_bower_blight', 'regent_cleansed');
    }
    if (area === 'verdant' && (q.verdant || 0) === 1 && gm.glade) { /* stage 2 starts at the glade */ }
  }
  detach() { this.ctx = null; this.boss = null; }
  swapFx(id, name) { const ctx = this.ctx, f = (ctx.scene.fx || []).find((x) => x.id === id); if (f && ctx.effects) ctx.effects.spawn(name, f.pos[0], f.pos[1], f.pos[2], { duration: 1e9 }); }
  roomAt(x) { const R = this.gm.rooms || []; let k = -1; for (let i = 0; i < R.length; i++) if (x > R[i].x - 4.5) k = i; return k; }
  // ---------------------------------------------------------------- per frame
  update(dt) {
    const ctx = this.ctx; if (!ctx) return;
    const G = this.G, S = this.S, F = flags(S), p = ctx.player, gm = this.gm;
    if (gm.rooms) {   // room-name toasts as you pass each cavern
      const k = this.roomAt(p.x);
      if (k !== this.room) { this.room = k; if (k >= 0 && G.toast) G.toast(`${gm.rooms[k].id}: ${gm.rooms[k].name}`, 1.6); }
    }
    if (this.area === 'rotwood') this.rotwood(dt, p, F);
    if (this.area === 'verdant') this.verdant(dt, p, F);
  }
  rotwood(dt, p, F) {
    const G = this.G, S = this.S, gm = this.gm, found = S.found || (S.found = {});
    if (!F.rw_lock && gm.rootdoor) {   // the brazier lock: they must be lit in the rune pulse order
      const lit = gm.rootdoor.order.filter((id) => found[id]);
      const fresh = gm.rootdoor.order.filter((id) => found[id] && !this.order.includes(id));
      for (const id of fresh) this.order.push(id);
      if (this.order.length && this.order.some((id, i) => id !== gm.rootdoor.order[i])) {
        for (const id of gm.rootdoor.order) delete found[id];
        for (const b of (G.hollows.braziers || [])) if (gm.rootdoor.order.includes(b.id)) { b.lit = false; }
        this.order = []; G.toast && G.toast('The runes flare violet. All three braziers gutter out. (Watch the pulse order.)', 2.6);
        if (S.cls === 'seer') G.toast && G.toast('(Frost-writing on the roots: middle, left, right.)', 2.6);
      } else if (lit.length === 3) {
        F.rw_lock = 1;
        G.toast && G.toast('The root door groans open. The runes rime over with frost as they die.', 2.6); G.drawLog && G.drawLog(); G.save && G.save();
      }
    }
    if (!F.rw_lock && gm.rootdoor && p.x > gm.rootdoor.x - 0.5) {   // the rune-sealed root door holds (the baked collision can't move, so the door is a soft wall)
      p.x = gm.rootdoor.x - 0.5; this.doorT = (this.doorT || 0) - dt;
      if (this.doorT <= 0) { this.doorT = 4; G.toast && G.toast('A wall of roots, three violet runes pulsing in turn. Three cold braziers stand before it.', 2.4); }
    }
    const bw = gm.bower;   // the Regent's Bower
    if (bw && !F.rw_boss && !this.boss && F.rw_lock && p.x > bw.enter_x) {
      if ((S.quests || {}).rotwood === 1) G.setQuest('rotwood', 2);
      this.boss = G.combat.spawnEnemy({ id: 'blightregent', role: 'blightregent', pos: [bw.pos[0] + 1.5, bw.pos[1] - 0.6], once: true, noRespawn: true }, true);
      const e = this.boss; e.state = 'chase';
      e.mods = { ...(e.mods || {}), hurt: (en, dmg) => this.regentHurt(en, dmg) };
      e.onKill = () => this.regentDown();
      G.toast && G.toast('THE BLIGHT REGENT\n\nThe taproot weeps violet. Something old and rotten rises.', 3.0);
    }
    if (this.boss && this.boss.state !== 'dead' && this.boss.state !== 'gone') {
      const e = this.boss, f = e.hp / e.D.hp;
      e.phaseN = f < REGENT.phases[1] ? 3 : f < REGENT.phases[0] ? 2 : 1;
      if (e.phaseN === 2) {   // rot-fog: Blight stacks outside the lit rim braziers' light
        const rims = (G.hollows.braziers || []).filter((b) => b.id.startsWith('rw_rim_') && found[b.id]);
        const safe = rims.some((b) => Math.hypot(p.x - b.pos[0], p.z - b.pos[1]) < 2.2);
        this.blightT = (this.blightT || 0) + dt;
        if (this.blightT > 3) { this.blightT = 0; this.blight = safe ? Math.max(0, this.blight - 1) : Math.min(REGENT.blightMax, this.blight + 1); }
        if (this.blight && G.combat.st != null) G.combat.st = Math.max(0, G.combat.st - this.blight * 2.0 * dt);
      }
      if (e.phaseN === 3) {   // the frost-iron spike pulses blue: the weak-point window
        this.pulseT += dt;
        const w = this.pulseT % REGENT.pulseEvery;
        e.spikeOpen = w > REGENT.pulseEvery - REGENT.pulseWin;
        if (e.spikeOpen && !e.pulsed && this.ctx.effects) { e.pulsed = 1; this.ctx.effects.spawn('glow_orb_blue', e.a.x, e.a.y + 3.4, e.a.z + 0.3, { duration: REGENT.pulseWin }); }
        if (!e.spikeOpen) e.pulsed = 0;
      }
    }
  }
  regentHurt(e, dmg) {
    if (e.phaseN === 3 && e.spikeOpen) {
      e.spikeHits = (e.spikeHits || 0) + 1; e.cd = Math.max(e.cd || 0, REGENT.stagger); e.state = 'chase';
      this.G.toast && this.G.toast('You strike the frost-iron spike! The Regent staggers.', 1.6);
      return dmg * REGENT.spikeMul;
    }
    return dmg;
  }
  regentDown() {
    const G = this.G, S = this.S, F = flags(S), gm = this.gm;
    F.rw_boss = 1; this.boss = null; this.blight = 0;
    this.swapFx('rw_bower_blight', 'regent_cleansed');
    if (!(S.inv || {}).blight_spike && !F.rw_spike) { F.rw_spike = 1; G.give('blight_spike', 1); }
    if (gm.sapling) gm.exits = (gm.exits || []).concat([{ rect: gm.sapling.rect, to: 'verdant', spawn: 'from_rotwood', label: gm.sapling.label }]);
    if (ally(S) === 'conquer') { G.setQuest('rotwood', 3); this.resolve('conquer'); }
    G.toast && G.toast('The Regent sinks. The spike lies on the root mound, and a fresh sapling breaks the moss.', 3.2);
    G.drawLog && G.drawLog(); G.save && G.save();
  }
  resolve(path) {   // the Rotwood's ending (both paths); the Verdant Heart opens
    const G = this.G, S = this.S, F = flags(S);
    if (F.vh_resolved) return; F.vh_resolved = path;
    if (path === 'befriend') { G.factions.add('embassy', MERIT.rotwood, 'rotwood'); S.pets = S.pets || {}; S.pets.mosspup = { ...(S.pets.mosspup || {}), atDen: true }; }
    else { S.gold = (S.gold || 0) + 150; G.give('heartwood', 1); }
    if (!(S.quests || {}).verdant) G.setQuest('verdant', 1);
  }
  verdant(dt, p, F) {
    const G = this.G, S = this.S, gm = this.gm, A = ally(S);
    const mw = gm.moonwell;
    if (mw && !F.vh_thorn && !this.thorn && Math.abs(p.x - mw.pos[0]) < 4) {   // V4: the Thornmother rises from the well
      this.thorn = G.combat.spawnEnemy({ id: 'thornmother', role: 'thornmother', pos: [mw.pos[0] + 2.2, mw.pos[1] + 1.6], once: true }, true);
      this.thorn.state = 'chase'; this.thorn.onKill = () => { F.vh_thorn = 1; this.thorn = null; G.toast && G.toast('The Thornmother sinks into violet moonpetals. The Moonwell stills.', 2.6); };
    }
    const gl = gm.glade;
    if (gl && !F.vh_hjortur && !this.hj && p.x > gl.enter_x && (S.quests || {}).verdant >= 1) {
      if (S.quests.verdant === 1) G.setQuest('verdant', 2);
      const role = A === 'conquer' ? 'hjortur_corrupted' : 'hjortur';
      this.hj = G.combat.spawnEnemy({ id: 'hjortur', role, pos: [gl.pos[0] + 1.6, gl.pos[1] - 0.6], once: true, trial: A !== 'conquer' }, true);
      this.hj.state = 'chase';
      const done = () => { F.vh_hjortur = 1; this.hj = null;
        if (A === 'conquer') { G.setQuest('verdant', 3); S.gold = (S.gold || 0) + 200; G.toast && G.toast('Hjortur lies down. The corruption lifts from his antlers. The forest is very quiet.', 3.0); }
        else { G.factions.add('embassy', MERIT.trial, 'trial'); G.setQuest('verdant', 3); G.factions.add('embassy', MERIT.verdant, 'verdant'); G.give('greenheart_tine', 1);
          G.toast && G.toast('Hjortur kneels. "Root, bloom and light. The forest knows your step now."', 3.0); }
        G.drawLog && G.drawLog(); G.save && G.save(); };
      this.hj.onYield = done; this.hj.onKill = done;
      G.toast && G.toast(A === 'conquer' ? 'HJORTUR, CORRUPTED\n\nRose eyes. Blight in the antlers.' : 'HJORTUR THE GREENHEART\n\n"Show me root, bloom and light, little hearth-walker."', 3.0);
    }
  }
  // ---------------------------------------------------------------- E / A spots
  near() {
    const ctx = this.ctx; if (!ctx) return null;
    const p = ctx.player, S = this.S, F = S.flags || {}, q = S.quests || {}, gm = this.gm, inv = S.inv || {};
    const d = (pos) => Math.hypot(p.x - pos[0], p.z - pos[1]);
    if (this.area === 'vanaheim') {
      if (q.vh_spring === 1) {
        for (let i = 0; i < capsAt.length; i++) if (!(S.found || {})['redcap_' + i] && d(capsAt[i]) < 1.6) return { kind: 'cap', i };
        if ((inv.redcap || 0) >= 3 && !F.vh_caps && d(SPRING_AT) < 2.0) return { kind: 'spring' };
      }
      if (ally(S) === 'conquer' && !q.rotwood && d(ROOT_CAVE.pos) < 1.8) return { kind: 'roots' };
    }
    if (this.area === 'rotwood') {
      for (const c of gm.cages || []) if (!(S.found || {})[c.id] && d(c.pos) < 1.3) return { kind: 'cage', c };
      if (gm.riddle && !F.rw_riddle && d(gm.riddle.pos) < 1.4) return { kind: 'riddle' };
      if (gm.taproot && d(gm.taproot.pos) < 1.6) return { kind: 'taproot' };
    }
    if (this.area === 'verdant') {
      for (const b of gm.bowls || []) if (!(S.found || {})[b.id] && d(b.pos) < 1.3) return { kind: 'bowl', b };
    }
    return null;
  }
  nearThing() { return !!this.near(); }
  prompt() {
    const n = this.near(); if (!n) return '';
    return { cap: 'a red toadstool cap (E / A to pick)', spring: 'the violet spring (E / A: drop in the red caps)', roots: 'thorny roots (E / A: burn through)',
             cage: 'a thorn cage (E / A: break it)', riddle: 'a carved gnome face (E / A)', taproot: 'the Weeping Root (E / A to look)', bowl: 'a root bowl (E / A: plant a glow seed)' }[n.kind];
  }
  interact() {
    const n = this.near(); if (!n) return false;
    const G = this.G, S = this.S, F = flags(S), found = S.found || (S.found = {});
    if (n.kind === 'cap') { found['redcap_' + n.i] = 1; G.give('redcap', 1); G.drawLog && G.drawLog(); return true; }
    if (n.kind === 'spring') {
      G.take('redcap', 3); F.vh_caps = 1; F.vanaheim_spring = 'cleansed'; G.setQuest('vh_spring', 2);
      G.toast('The red caps fizz and sink. The violet drains from the spring... but a trickle still runs down from the Old Bough.', 3.2);
      G.refreshMarkers && G.refreshMarkers(); G.save && G.save(); return true;
    }
    if (n.kind === 'roots') {
      G.setQuest('rotwood', 1); const gm = this.gm; gm.exits = (gm.exits || []).concat([{ ...ROOT_CAVE }]);
      G.toast('Your spell chews through the thorny roots. The root-cave under the Old Bough gapes open.', 2.8); G.save && G.save(); return true;
    }
    if (n.kind === 'cage') {
      found[n.c.id] = 1;
      const k = (this.gm.cages || []).filter((c) => found[c.id]).length;
      G.toast(ally(S) === 'conquer' ? 'The gnome bolts through a burrow without a word.' : `A gnome tumbles out: "Mulch! They called us MULCH!" (${k}/3)`, 2.2); return true;
    }
    if (n.kind === 'riddle') {
      if (ally(S) === 'conquer') { G.say({ id: 'riddle', name: 'A carved gnome face' }, '(A gnome voice: "Not for YOU.")'); return true; }
      if ((this.gm.cages || []).some((c) => !found[c.id])) { G.say({ id: 'riddle', name: 'A carved gnome face' }, 'The carved face is dark. Somewhere nearby, small voices are crying for help.'); return true; }
      G.openDialogue({ id: 'riddle', name: 'A carved gnome face' }, {
        pages: ['The carved gnome\'s eyes glow. "I follow you all day, but run from every lamp. What am I?"'],
        choice: { id: 'rw_riddle', options: [
          { label: 'A shadow.', pick: (G) => { flags(G.S).rw_riddle = 1; G.factions.onRiddle(); G.S.gems = G.S.gems || {}; G.S.gems.moon_opal = (G.S.gems.moon_opal || 0) + 1; G.S.gold = (G.S.gold || 0) + 40;
              return { pages: ['"Ha! Clever big-folk." The door rolls aside like a sleepy snail. (+1 moon opal, +40 gold)'] }; } },
          { label: 'A cat.', pick: () => ({ pages: ['"Cats run TOWARD lamps. To sit in front of them." The door sulks.'] }) },
          { label: 'My debts.', pick: () => ({ pages: ['"Ha! True, but no." The door stays shut, chuckling.'] }) },
          { label: 'Leave it.', cancel: true, pick: () => ({ pages: ['The carved gnome winks. It\'ll keep.'] }) },
        ] } });
      return true;
    }
    if (n.kind === 'taproot') { G.say({ id: 'taproot', name: 'The Weeping Root' }, ['Violet sap oozes down the great taproot toward Mossbrook.', 'A rune is carved in the bark, rimed with frost. The cold seeps up from below, not down from the rot.']); return true; }
    if (n.kind === 'bowl') {
      const seeds = (S.inv || {}).glowseed || 0, tobble = ally(S) === 'befriend' && !F['vh_tobseed_' + n.b.id];
      if (!seeds && !tobble) { G.toast('An empty root bowl. A glow seed would take here.', 2); return true; }
      if (seeds) G.take('glowseed', 1); else F['vh_tobseed_' + n.b.id] = 1;
      found[n.b.id] = 1;
      if (this.ctx.effects) this.ctx.effects.spawn('glow_orb_green', n.b.pos[0], 0.6, n.b.pos[1], { duration: 1e9 });
      G.toast('The seed blooms into a cold-glowing moss bridge.', 2); return true;
    }
    return false;
  }
  state() { const e = this.boss; return { area: this.area, room: this.room, order: this.order.slice(), blight: this.blight, boss: e ? { hp: e.hp, max: e.D.hp, phase: e.phaseN || 1, spikeOpen: !!e.spikeOpen, spikeHits: e.spikeHits || 0, scale: e.D.scale } : null,
                     thorn: this.thorn ? { hp: this.thorn.hp, scale: this.thorn.D.scale } : null, hj: this.hj ? { role: this.hj.a.role, trial: this.G.isTrial(this.hj, this.S), scale: this.hj.D.scale } : null }; }
}
