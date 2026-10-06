// Hearthmoor Stage 6.3: the Old Temple (Ravenhold, Midgard). Story: the Story bot's old_temple.md (Mother Ilse, Brother
// Tamsin, Novice Edda, Warden Aldis's lantern charm; quests 'altar' (The Cold Altar) + 'gate' (Keeper of the Gate)).
// This module owns the world side: the Harbor's Old Temple gate opening for the Hearth writ, the temple area's clue
// spots / altar / Rift-gate interactions, the rite's chain-lighting, the scripted major rift + Veyra's cameo, and
// Bifrost's Midgard arch opening once the Temple is relit (Decision 1, option A: the relight alone is the key).
// ART: the Old Temple pack (art/old_temple/, Art bot 2026-10-05): riftgate arch + dormant glow, temple braziers, faceless
// statues, stained windows, Ilse / Tamsin sprites and the riftgate / cold-fire gamefx (areas/src/temple.json game.art).
// Still placeholder: VEYRA_FX (no Veyra art yet) and Edda's role; Bifrost's Midgard arch keeps the portal-kit rift_vortex.
import { MERIT } from './factions.js';

export const TEMPLE = { veyra: true };   // Veyra's cameo after the relight rift (toggle: false, or ?noveyra)
export const templeOpen = (S) => ((S.quests || {}).altar || 0) >= 1;
export const midgardOpen = (S) => !!(S.flags || {}).temple_lit;
export const CLUES = ['clue_tongs', 'clue_prints', 'clue_snuffer'];
export const clues = (S) => CLUES.filter((k) => (S.found || {})[k]).length;
export const tmBraziers = (S) => ['tm_b1', 'tm_b2', 'tm_b3'].filter((k) => (S.found || {})[k]).length;
export const isDark = (t) => t > 0.75 || t < 0.25;
const flags = (S) => (S.flags = S.flags || {});
const GATE_LIT_FX = ['riftgate_vortex_lit', 'rift_vortex'];   // the Temple's own lit gate (old_temple gamefx); Bifrost's atlas only has rift_vortex
const VEYRA_FX = ['glitter', 'sparkle_burst'];   // swap point: Veyra's sprite / frost-flower fx (no Veyra art yet)
const HARBOR_EXIT = { rect: [-9.8, -12.4, -7.4, -10.7], to: 'temple', spawn: 'from_harbor', label: 'the Old Temple stair' };
const EDDA = { id: 'novice', role: 'lamplighter', name: 'Novice Edda, the Old Temple gate', pos: [-7.0, -10.2], facing: 'down' };   // swap point: role novice
const MIDGARD_PORTAL = { fx: 'gate_midgard', to: 'temple', spawn: 'from_bifrost', rect: [10.25, -5.45, 11.75, -4.6], label: "Midgard's gate (the Old Temple)" };

export const CLUE_SAY = {
  clue_tongs: 'Dwarven forge tongs. Good iron, rimed with frost. Forge tools live by the fire. These have never been warm.',
  clue_prints: 'Frost-flowers in the shape of footprints, leading from the altar to the inner court. Not toward the forges.',
  clue_snuffer: 'A brazier snuffer behind a statue. Frost-iron, no maker\'s mark. Made so nobody could say whose it was.',
};
export const TAMSIN_CLUE = {
  clue_tongs: 'Frost on forge tongs. Writing it down. Underlining it.',
  clue_prints: 'Footprints that freeze the floor. That\'s not a smith. That\'s not anyone I want to meet.',
  clue_snuffer: 'A snuffer with no name. Someone wanted no one blamed. Except whoever they did want blamed.',
};

export class Temple {
  constructor(G) { this.G = G; this.ctx = null; this.area = null; this.lit = []; this.chain = []; this.cameo = 0; }
  get S() { return this.G.S; }
  get gm() { return (this.ctx && this.ctx.scene.game) || {}; }
  veyraOn() { const q = this.G.qs; return TEMPLE.veyra && !(q && q.has('noveyra')); }
  attach(ctx, area) {
    this.ctx = ctx; this.area = area; this.lit = []; this.chain = []; this.cameo = 0;
    const gm = ctx.scene.game || (ctx.scene.game = {}), S = this.S;
    if (area === 'ravenhold') {
      if (!ctx.npc('novice') && ctx.actors.sheetOf(EDDA.role)) { const a = ctx.addNpc({ ...EDDA, behavior: 'idle' }); a.y = ctx.heightAt(a.x, a.z); }
      if (templeOpen(S)) {   // the Hearth writ opens the Old Temple's district gate: an exit up the stair
        gm.sealed = (gm.sealed || []).filter((g) => g.id !== 'temple');
        gm.exits = (gm.exits || []).filter((e) => e.to !== 'temple').concat([{ ...HARBOR_EXIT }]);
      }
    } else if (area === 'bifrost') {
      if (midgardOpen(S)) {   // Midgard's arch: sealed until the Temple is relit, then a portal to its Rift-gate
        gm.sealed = (gm.sealed || []).filter((g) => g.arch !== 'midgard');
        gm.portals = (gm.portals || []).filter((p) => p.to !== 'temple').concat([{ ...MIDGARD_PORTAL }]);
        this.swapFx('gate_midgard', GATE_LIT_FX);
      }
    } else if (area === 'temple') {
      const F = flags(S);
      if (F.tm_altar || F.temple_lit) this.altarOn(true);
      if (F.tm_gate || F.temple_lit) this.gateLit(true);
      this.night = [];   // the faceless statues' night gaze + the stained windows' dusk glass-light pools
      const art = gm.art || {};
      if (ctx.gamefx && ctx.gamefx.meta.effects.faceless_gaze) for (const [x, z] of art.statues || []) this.night.push({ f: ctx.gamefx.spawn('faceless_gaze', x, ctx.heightAt(x, z), z + 0.05, { duration: Infinity }), dusk: false });
      for (const id of ['tm_glass_0', 'tm_glass_1']) if (ctx.fx[id]) this.night.push({ f: ctx.fx[id], dusk: true });
      this.nightFx();
      if (F.temple_lit && gm.midgard_portal) gm.portals = (gm.portals || []).filter((p) => p.to !== 'bifrost').concat([{ ...gm.midgard_portal }]);
      // the rift tore open and the area changed before it sealed: it is waiting again above the court
      if (F.tm_gate && !F.tm_rift) setTimeout(() => { if (this.ctx === ctx && !this.G.rifts.cur) this.G.rifts.open(1, gm.riftAt, { tag: 'temple' }); }, 400);
    }
  }
  detach() { this.ctx = null; this.lit = []; this.chain = []; this.night = []; }
  // swap a placed gamefx for the first name this area's atlas has (a list = preference order)
  swapFx(id, names) {
    const ctx = this.ctx, f = ctx && ctx.fx[id]; if (!f || !ctx.gamefx) return false;
    const name = [].concat(names).find((n) => ctx.gamefx.meta.effects[n]); if (!name || f.name === name) return false;
    ctx.gamefx.remove(f); ctx.fx[id] = ctx.gamefx.spawn(name, f.x, f.y, f.z, { duration: Infinity });
    return true;
  }
  // the Temple's Rift-gate wakes: riftgate_awaken (once) -> riftgate_vortex_lit, and the rune ring on the plinth
  gateLit(still = false) {
    const ctx = this.ctx, f = ctx && ctx.fx.gate_midgard; if (!f) return;
    const at = [f.x, f.y, f.z], gx = ctx.gamefx, has = (n) => gx && gx.meta.effects[n];
    if (!still && has('riftgate_awaken')) gx.spawn('riftgate_awaken', at[0], at[1], at[2] + 0.05);
    this.swapFx('gate_midgard', GATE_LIT_FX);
    if (has('riftgate_ring_lit') && !ctx.fx.gate_ring) ctx.fx.gate_ring = gx.spawn('riftgate_ring_lit', at[0], at[1], at[2] + 0.5, { duration: Infinity, ...(still ? {} : { fadeIn: 0.6 }) });
  }
  nightFx() {
    const ctx = this.ctx; if (!ctx || !this.night) return;
    const t = ctx.clock.t, dark = isDark(t), dusk = dark || t > 0.62;
    for (const n of this.night) if (n.f && n.f.mesh) n.f.mesh.visible = n.dusk ? dusk : dark;
  }
  // the sacred brazier on the altar: cold-fire flame, a wide pool, a blue light (a light zone)
  altarOn(still = false) {
    const ctx = this.ctx, A = this.gm.altar; if (!ctx || !A || this.lit.some((l) => l.id === 'altar')) return;
    const [x, z] = A.pos, y = ctx.heightAt(x, z + 0.6), fx = [];
    const gx = ctx.gamefx && ctx.gamefx.meta.effects.temple_coldfire ? ctx.gamefx : null;   // the pack's temple cold fire + wide pool
    if (gx) {
      fx.push({ gx: gx.spawn('temple_coldfire', x, y - 0.1, z + 0.05, { duration: Infinity, ...(still ? {} : { fadeIn: 0.4 }) }) });
      fx.push({ gx: gx.spawn('coldfire_pool_wide', x, y, z + 0.6, { duration: Infinity, ...(still ? {} : { fadeIn: 0.6 }) }) });
      if (ctx.effects) fx.push(ctx.effects.spawn('coldfire_motes', x, y + 1.2, z + 0.12, { duration: 1e9 }));
    } else if (ctx.effects) {
      fx.push(ctx.effects.spawn('coldfire_flame', x, y + 1.0, z + 0.1, { duration: 1e9, fadeIn: still ? 0 : 0.4 }));
      fx.push(ctx.effects.spawn('coldfire_motes', x, y + 1.2, z + 0.12, { duration: 1e9 }));
      for (const [ox, oz] of [[0, 0.9], [-0.9, 0.7], [0.9, 0.7]]) fx.push(ctx.effects.spawn('coldfire_pool', x + ox, ctx.heightAt(x + ox, z + oz), z + oz + 0.03, { duration: 1e9, fadeIn: still ? 0 : 0.6 }));
    }
    const light = ctx.addGlow ? ctx.addGlow(x, y, z + 0.4, { color: '#2ab4ff', intensity: 10, range: 6.0, lift: 1.1, fadeIn: still ? 0.01 : 0.5 }) : null;
    this.lit.push({ id: 'altar', x, z, r: 2.8, fx, light });
  }
  zones() { return this.lit.map((l) => ({ x: l.x, z: l.z, r: l.r, src: 'temple' })); }
  // ---------------------------------------------------------------- E / A points: clues (altar 2), the altar, the Rift-gate
  near() {
    const ctx = this.ctx; if (!ctx || this.area !== 'temple') return null;
    const p = ctx.player, S = this.S, F = S.flags || {}, q = S.quests || {}, gm = this.gm;
    const d = (pos) => Math.hypot(p.x - pos[0], p.z - pos[1]);
    if (q.altar === 2) for (const c of gm.clues || []) if (!(S.found || {})[c.id] && d(c.pos) < 1.3) return { kind: 'clue', c };
    if (q.gate === 2 && !F.tm_altar && gm.altar && d(gm.altar.use) < 1.4) return { kind: 'altar' };
    if (q.gate === 2 && F.tm_altar && !F.tm_gate && gm.riftgate && d(gm.riftgate.use) < 1.5) return { kind: 'gate' };
    return null;
  }
  nearThing() { return !!this.near(); }
  prompt() {
    const n = this.near(); if (!n) return '';
    return n.kind === 'clue' ? 'something here (E / A to look)' : n.kind === 'altar' ? 'the cold altar (E / A: set the lantern charm)' : 'the dark Rift-gate (E / A: raise the charm)';
  }
  interact() {
    const n = this.near(); if (!n) return false;
    const G = this.G, S = this.S;
    if (n.kind === 'clue') {
      const pages = [CLUE_SAY[n.c.id]];
      if (S.cls === 'seer') pages.push('(Your runes prickle. This was put here to be found. A frame, and a careful one.)');
      if (S.cls === 'runeguard' && n.c.id === 'clue_prints') pages.push('(Long strides, light weight. Whoever walked here wasn\'t hurrying. They weren\'t afraid.)');
      G.openDialogue({ id: 'clue', name: 'The nave' }, { pages, then: (G) => {
        S.found[n.c.id] = 1; flags(S).tm_lastclue = n.c.id;
        G.toast(`Clue noted (${clues(S)}/3).`, 2); G.refreshMarkers(); G.drawLog && G.drawLog(); G.save();
      } });
      return true;
    }
    if (n.kind === 'altar') {
      if (!isDark(this.ctx.clock.t)) { G.openDialogue({ id: 'altar', name: 'The cold altar' }, { pages: ['The cold altar waits. Ilse said dusk or after. Cold fire burns truest in the dark.'] }); return true; }
      G.openDialogue({ id: 'altar', name: 'The cold altar' }, { pages: [
        'You set the charm on the cold altar. For a breath, nothing. Then blue fire pours out of it like water running uphill.',
        'The sacred brazier roars awake. Blue light runs down the stair, brazier to brazier, and the stained glass blooms violet.',
        'Ilse: "There. There it is. Now the gate. It\'s been dark so long it may not remember what it\'s for."'],
        then: (G) => { flags(S).tm_altar = 1; this.rite(); G.drawLog && G.drawLog(); G.save(); } });
      return true;
    }
    G.openDialogue({ id: 'riftgate', name: 'The Rift-gate' }, { pages: [
      'You raise the charm to the dark arch. Runes wake around the stone one by one, cold blue, then every colour at once.',
      'The arch fills with a slow rainbow swirl. Far off, you hear the bells of Bifrost Crossing.',
      'Then the sky above the court cracks open. The Rift has noticed its old door.'],
      then: (G) => { flags(S).tm_gate = 1; this.gateLit(); G.rifts.open(1, this.gm.riftAt, { tag: 'temple' }); G.drawLog && G.drawLog(); G.save(); } });
    return true;
  }
  // the rite: the altar first, then every temple brazier 0.25 s apart (they burn at every hour from now on)
  rite() {
    const G = this.G; this.altarOn();
    G.audio && G.audio.sfx('quest');
    const bz = (G.hollows.braziers || []).filter((b) => b.temple);
    this.chain = bz.map((b, k) => ({ b, t: 0.25 * (k + 1) }));
  }
  // the scripted rift sealed (rifts.js tag 'temple'): the toast, then Veyra's cameo (or the crack simply fades)
  afterRift() {
    const G = this.G, F = flags(this.S);
    F.tm_rift = 1;
    G.toast(`The tear seals. A second crack is already spreading above the arch...${this.veyraOn() ? '' : ' ...and fades. The Rift settles.'}`, 3.2);
    G.refreshMarkers(); G.drawLog && G.drawLog(); G.save();
    if (this.veyraOn()) this.cameo = 2.2;
  }
  veyra() {
    const G = this.G, S = this.S, ctx = this.ctx; if (!ctx) return;
    const gm = this.gm, at = gm.riftAt || [0, -8];
    if (ctx.effects) for (const n of VEYRA_FX) ctx.effects.spawn(n, at[0] + 0.8, ctx.heightAt(at[0], at[1]) + 0.2, at[1] + 0.4, { duration: 2.4 });
    const tail = ['Veyra Ashmantle. Once the Rift had a hundred wardens. Now it has me, and I am very tired.',
                  'You relit the gate. That was kind. Kindness is rare up here.',
                  'Someone is poisoning Ravenhold\'s water, down under the grates. If you find who, I would like to know.',
                  'Keep that charm lit, hearth-walker. Cold fire remembers who carries it.'];
    if (S.cls === 'seer') tail.push('(For a heartbeat your runes hear the frost on the tongs answer her, like an echo. Then it\'s gone.)');
    if (S.cls === 'cinderknight') tail.push('(She glances at your ember seam, and something cold passes over her face. Then the kind smile is back.)');
    G.openDialogue({ id: 'veyra', name: 'A frost-witch in grey-blue' }, {
      pages: ['Easy. It\'s only the Rift breathing out. It does that when someone lights a door it has forgotten.',
              '(She lifts two fingers. The crack above the arch stitches shut in a ribbon of frost.)'],
      then: (G) => G.openDialogue({ id: 'veyra', name: 'Veyra' }, { pages: tail, then: (G) => {
        flags(S).met_veyra = 1;
        G.toast('She walks into the arch\'s swirl and is gone. Frost-flowers fade where she stood.', 3);
        G.save();
      } }),
    });
  }
  update(dt) {
    const G = this.G; if (!this.ctx) return;
    if (this.chain.length) {
      for (const c of this.chain) { c.t -= dt; if (c.t <= 0 && !c.done) { c.done = true; c.b.flare = 9999; G.audio && G.audio.sfx('spell'); } }
      if (this.chain.every((c) => c.done)) this.chain = [];
    }
    if (this.cameo > 0 && !G.dlg && !G.busy) { this.cameo -= dt; if (this.cameo <= 0) this.veyra(); }
    for (const l of this.lit) if (l.light) l.light.scale = 0.92 + Math.sin(performance.now() / 300) * 0.06;
    this.nightFx();
  }
  qa() {
    const c = this.ctx; if (!c) return null;
    return { area: this.area, lit: this.lit.map((l) => l.id), gate: c.fx.gate_midgard ? c.fx.gate_midgard.name : null, ring: c.fx.gate_ring ? c.fx.gate_ring.name : null,
             gaze: (this.night || []).filter((n) => !n.dusk).length, glass: (this.night || []).filter((n) => n.dusk).length, near: this.near(), cameo: this.cameo,
             sealed: (c.scene.game?.sealed || []).map((g) => g.id || g.arch), exits: (c.scene.game?.exits || []).map((e) => e.to), portals: (c.scene.game?.portals || []).map((p) => p.to) };
  }
}
export { MERIT };
