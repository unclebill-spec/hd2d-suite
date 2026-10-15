// [SVARTALFHEIM] The Copper Gate (story 3.1, "A Word from the Council"): Bix's vouch -> Halvard posts it -> the dwarves' key
// capsule -> wind the key at Bifrost's amber arch -> a runaway construct stumbles out -> Halvard opens the gate (the arch moves
// from `sealed` to `portals`). Built the way Alfheim's Frozen Gate was (runtime wiring + a prefetched Bifrost scene), so no
// area rebuild: the Copper Gate back to Bifrost in Copper Row is a runtime portal too.
// Deviations: the runaway uses Bifrost's 'golem' sheet (a stand-in until Art lists a forge-construct sheet for Bifrost); the
// rift-seal shortcut for the Council's answer (sg_riftAfter) is not hooked, the answer simply arrives the next day.
import { QUESTS, ITEMS, TALK, MARKER_HOOKS } from './data.js';
import { ENEMIES } from './heroes.js';
import { XP } from './progress.js';
import { MERIT } from './factions.js';

const flags = (S) => (S.flags = S.flags || {});
const F = (S) => S.flags || {};
const q = (S, k) => (S.quests || {})[k] || 0;
const gold = (G, n) => { G.S.gold = (G.S.gold || 0) + n; G.toast(`+${n} gold`, 1.8); G.drawBag && G.drawBag(); };
export const SV_ARCH = { rect: [-7.35, -5.4, -5.85, -4.55], pos: [-6.6, -5.0], spawn: [-6.6, -3.6, 'down'] };
const HUB_GATE = { to: 'bifrost', spawn: 'from_svartalfheim', rect: [-0.9, 10.1, 0.9, 11.1], label: 'the Copper Gate back to Bifrost Crossing' };

Object.assign(ITEMS, {
  council_vouch: { name: 'Council vouch', px: 'glowseed', about: 'The Gnome Council\'s word on you, sealed in wax. For the dwarves, via Halvard.' },
  copper_key: { name: 'Copper key', px: 'glowseed', about: 'A copper key with a wind-up bow. The dwarves forge them under the mountain.' },
});
Object.assign(MERIT, { vouch: 40, copper: 60 });
Object.assign(ENEMIES, { runaway: { name: 'Runaway construct', scale: 2.0, hp: 300, dmg: 16, speed: 1.0, reach: 2.0, windup: 0.6, cd: 1.8, aggro: 9, r: 0.6, push: 0.2, heavy: true, weakBelly: 1.5 } });
Object.assign(XP, { runaway: 180 });
Object.assign(QUESTS, {
  sv_gate: { title: 'A Word from the Council', giver: 'Bix Coppertuft', story: true, steps: {
    1: (S) => { const f = F(S);
      if (!f.sg_vouch) return 'Ask Bix Coppertuft at the Nine Keys Bank for the Gnome Council\'s word.';
      if (!f.sg_sent) return 'Take the Council\'s vouch to Gatewright Halvard at Bifrost Crossing.';
      if (!f.sg_key) return 'Wait for the dwarves\' answer. (Sleep, then see Halvard.)';
      return 'Wind the copper key in Svartalfheim\'s gate (E / A at the copper gate).'; },
    2: 'Deal with whatever came out of the gate, then tell Halvard.',
    3: 'Svartalfheim\'s gate is open. Copper light and forge-heat spill across the Crossing.',
  } },
});

export const gateOpen = (S, qs) => !!(F(S).sv_gate_open || (F(S).alliance || {}).svartalfheim || (qs && qs.has('svq')));
const openBank = (G) => { G.S.met = { ...(G.S.met || {}), banker: 1 }; G.shopUI.show('bank'); };
const banker0 = TALK.banker, gatewright0 = TALK.gatewright;
Object.assign(TALK, {
  banker(S) {
    const base = banker0(S), f = F(S);
    if (q(S, 'sv_gate') || f.sg_vouch || ((S.ranks || {}).gnome || 0) < 2) return base;
    return { pages: ['Trusted of the Council, now. Quite the climb. The Council has been asked a question by the dwarves, and I\'ve been asked to ask you one.'],
      choice: { id: 'sv_gate', options: [
        { label: 'About the copper gate...', pick: () => ({
          pages: ['The dwarves forge the gate key under the mountain, and only for those the Council vouches for. So. Here is the Council\'s word, in wax.',
                  'Take it to Gatewright Halvard at Bifrost. He posts it through the slot. Dwarves answer slowly, and loudly.'],
          then: (G) => { flags(G.S).sg_vouch = 1; G.give('council_vouch', 1); G.setQuest('sv_gate', 1); G.factions.add('gnome', MERIT.vouch, 'vouch'); G.refreshMarkers && G.refreshMarkers(); } }) },
        { label: 'Just the vault, please.', cancel: true, pick: () => ({ pages: ['Keys, ledger, lantern.'], then: openBank }) },
      ] } };
  },
  gatewright(S) {
    const f = F(S), qq = q(S, 'sv_gate');
    if (qq === 1 && f.sg_vouch && !f.sg_sent && (S.inv || {}).council_vouch) return { pages: ['A Council vouch! Wax and everything. I\'ll post it through the gate\'s message slot. Come back tomorrow.'],
      then: (G) => { G.take && G.take('council_vouch', 1); const f2 = flags(G.S); f2.sg_sent = 1; f2.sg_sentDay = G.S.day || 0; G.refreshMarkers && G.refreshMarkers(); } };
    if (qq === 1 && f.sg_sent && !f.sg_key) {
      if ((S.day || 0) > (f.sg_sentDay || 0)) return { pages: ['The slot rattled in the night. A key capsule. Copper, with a bow to wind.', 'Wind it at the amber gate. Stand back. They say the Cooling sends something out first.'],
        then: (G) => { flags(G.S).sg_key = 1; G.give('copper_key', 1); G.refreshMarkers && G.refreshMarkers(); } };
      return { pages: ['No answer yet. Dwarves answer slowly. Sleep, and ask again.'] };
    }
    if (qq === 1 && f.sg_key) return { pages: ['Wind the key at the amber arch, the one with the copper light behind it. I\'ll hold the ledger.'] };
    if (qq === 2 || (qq === 1 && f.sg_runaway)) return { pages: ['It\'s down? Good. Good. I\'ll note a runaway in the ledger. Someone will want to sign for it.', 'Svartalfheim\'s open. The Crossing smells of forge-smoke. I like it.'],
      then: (G) => { G.setQuest('sv_gate', 3); G.factions.add('gate', MERIT.copper, 'copper'); gold(G, 50); flags(G.S).sv_gate_open = 1; G.svart && G.svart.gate.reopen(); G.refreshMarkers && G.refreshMarkers(); } };
    return gatewright0(S);
  },
});
MARKER_HOOKS.push((id, S) => {
  const f = F(S), qq = q(S, 'sv_gate');
  if (id === 'banker' && !qq && !f.sg_vouch && ((S.ranks || {}).gnome || 0) >= 2) return 'quest_mark';
  if (id === 'gatewright' && qq === 1 && ((f.sg_vouch && !f.sg_sent) || (f.sg_sent && !f.sg_key && (S.day || 0) > (f.sg_sentDay || 0)))) return 'quest_mark';
  if (id === 'gatewright' && (qq === 2 || (qq === 1 && f.sg_runaway))) return 'quest_turnin';
});

export class SvGate {
  constructor(sv) { this.sv = sv; this.G = sv.G; this.wrapped = false; this.fetching = false; }
  get ctx() { return this.sv.ctx; }
  qs() { return this.G.qs || new URLSearchParams(location.search); }
  put(sc) { const gm = (sc.game = sc.game || {}); gm.spawns = gm.spawns || {}; if (!gm.spawns.from_svartalfheim) gm.spawns.from_svartalfheim = SV_ARCH.spawn.slice(); }
  // Copper Row: the Copper Gate back to Bifrost (runtime portal) + the Bifrost scene prefetched with its return spawn
  atHub(ctx) {
    const G = this.G, gm = ctx.scene.game || (ctx.scene.game = {});
    gm.portals = gm.portals || [];
    if (!gm.portals.find((p) => p.to === 'bifrost')) gm.portals.push({ ...HUB_GATE, rect: HUB_GATE.rect.slice() });
    if (G.scenes && G.scenes.bifrost) { this.put(G.scenes.bifrost); return; }
    if (this.fetching || !G.scenes) return;
    this.fetching = true;
    fetch('areas/bifrost/scene.json').then((r) => r.json()).then((sc) => { if (!G.scenes.bifrost) G.scenes.bifrost = sc; this.put(G.scenes.bifrost); }).catch(() => {}).finally(() => { this.fetching = false; });
  }
  atBifrost(ctx) {
    const S = this.G.S, f = F(S);
    this.put(ctx.scene);
    this.wrapLook();
    this.wire(ctx);
    if (f.sg_wound && !f.sg_runaway) setTimeout(() => this.ctx === ctx && this.spawnRunaway(), 300);
  }
  reopen() { if (this.ctx && this.sv.area === 'bifrost') this.wire(this.ctx); }
  wire(ctx) {
    const gm = ctx.scene.game; if (!gm || !gateOpen(this.G.S, this.qs())) return;
    gm.sealed = (gm.sealed || []).filter((g) => g.arch !== 'svartalfheim');
    gm.portals = gm.portals || [];
    if (!gm.portals.find((p) => p.to === 'svartalfheim')) gm.portals.push({ fx: 'gate_svartalfheim', to: 'svartalfheim', spawn: 'from_bifrost', rect: SV_ARCH.rect.slice(), label: 'Svartalfheim\'s gate' });
    (gm.spawns = gm.spawns || {}).from_svartalfheim = gm.spawns.from_svartalfheim || SV_ARCH.spawn.slice();
  }
  // winding the key: E / A (or tap) at the sealed amber arch. Wraps crossing.look once; everything else is passed through.
  wrapLook() {
    const G = this.G, me = this; if (this.wrapped || !G.crossing) return; this.wrapped = true;
    const l0 = G.crossing.look.bind(G.crossing);
    G.crossing.look = (g) => (g && g.arch === 'svartalfheim' && me.wind()) || l0(g);
  }
  wind() {
    const G = this.G, S = G.S, f = flags(S);
    if (q(S, 'sv_gate') === 1 && f.sg_key && (S.inv || {}).copper_key && !f.sg_wound) {
      G.openDialogue({ id: 'sealed_svartalfheim', name: 'Svartalfheim\'s gate (sealed)' }, {
        pages: ['(You wind the copper key. Gears turn behind the stone. The door rolls open a hand\'s width... and something forges its way out.)'],
        then: () => { f.sg_wound = 1; G.take && G.take('copper_key', 1); G.save && G.save(); this.spawnRunaway(true); } });
      return true;
    }
    if (q(S, 'sv_gate') === 1 && f.sg_wound && !f.sg_runaway) { G.toast('The runaway construct stands between you and the gate!', 2); return true; }
    return false;
  }
  spawnRunaway(poof) {
    const ctx = this.ctx, C = this.G.combat; if (!ctx || !C || !C.ctx) return null;
    if ((C.enemies || []).some((e) => e.sp.id === 'runaway' && e.state !== 'dead')) return null;
    const roles = (ctx.actors && ctx.actors.meta && ctx.actors.meta.roles) || {};
    const role = roles.forgeconstruct ? 'forgeconstruct' : roles.golem ? 'golem' : 'eldergolem';
    const e = C.spawnEnemy({ id: 'runaway', role, def: 'runaway', pos: [SV_ARCH.pos[0], SV_ARCH.pos[1] + 2.6], once: true }, !!poof);
    if (poof) this.G.toast('A runaway construct staggers out of the gate!', 2.4);
    e.onKill = () => { const S = this.G.S; flags(S).sg_runaway = 1; if (q(S, 'sv_gate') === 1) this.G.setQuest('sv_gate', 2); this.G.toast('The gate stills. Tell Gatewright Halvard.', 2.6); this.G.refreshMarkers && this.G.refreshMarkers(); };
    return e;
  }
  qa() { const c = this.ctx, gm = c ? (c.scene.game || {}) : {}; return { portals: (gm.portals || []).map((p) => p.to), sealed: (gm.sealed || []).map((g) => g.arch), spawns: Object.keys(gm.spawns || {}), open: gateOpen(this.G.S, this.qs()) }; }
}
