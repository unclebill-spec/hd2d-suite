// Bifrost Crossing (Stage 6 part 1): the portal capital between the Nine Realms. Nine realm gates stand on the plaza,
// each lit in its realm's colour: Vanaheim's is open (a portal to Mossbrook Springs), the other eight are sealed, and
// looking at one (E / A / a second tap) says why: the alliance or the faction merit its key needs, and where you stand.
// Area data: scene.game.sealed [{realm, hue, pos, arch}]; the gatewright (Gatekeepers' Guild) talks in data.js.
import { FACTIONS, RANKS, NEED } from './factions.js';

// arch id -> [why it is shut, the key it needs: [faction, rank] or null (story-locked)]
export const GATES = {
  asgard: ['Gold light hums behind the seal, warm as a hall fire. Asgard opens only to allies, and the Aesir have not named you one yet.', ['embassy', 3]],
  alfheim: ['Violet light pulses behind the seal. Frost rimes it from the far side: Veyra froze Alfheim\'s gate shut, and only a Guild Keybearer may cut through a frozen seal.', ['gate', 3]],
  jotunheim: ['Ice-white light glitters behind the seal. The giants bar their gate to strangers; a friend of the Realm Embassies can ask their envoy to lift the bar.', ['embassy', 1]],
  helheim: ['Spirit-rose light drifts behind the seal like breath on glass. The dead pass Helheim\'s gate freely; the living need Hel\'s leave, asked through the Embassies.', ['embassy', 2]],
  muspelheim: ['A red glow beats behind the seal like embers under ash. Muspelheim is no friend to mortals: the Guild sends only proven Gate Runners through, and they go armed.', ['gate', 2]],
  svartalfheim: ['Copper light glows behind the seal like a forge through a keyhole. The dwarves forge this key under the mountain, and only for those the Gnome Council vouches for.', ['gnome', 2]],
  niflheim: ['Cold-fire flickers blue under a skin of ice. Niflheim is Veyra\'s home, and she has frozen this gate from the inside. No key opens it yet.', null],
  // 6.3: the relight alone opens it (Decision 1, option A); temple.js moves it into the portals once S.flags.temple_lit
  midgard: ['Rainbow light runs round the seal. Its far side is the Old Temple\'s Rift-gate in Ravenhold, dark and cold. Until the Temple is relit, mortals cross by Corsair skiff.', 'temple'],
};

export class Crossing {
  constructor(G) { this.G = G; this.ctx = null; }
  attach(ctx, id) {
    this.ctx = ctx; if (id !== 'bifrost') return;
    const S = this.G.S, F = (S.flags = S.flags || {});
    if (!F.bf_seen) { F.bf_seen = 1; this.G.save && this.G.save(); }   // the vine gate in Vanaheim now offers the Crossing too
  }
  detach() { this.ctx = null; }
  // a sealed realm gate's look: why it is shut, what key it needs, where you stand (merit is real, keys come later)
  pages(g) {
    const G = this.G, row = GATES[g.arch]; if (!row) return ['The gate is sealed.'];
    const [why, need] = row, out = [why];
    if (need === 'temple') { out.push('Key: relight the Old Temple\'s flame (Order of the Hearth). Ask Warden Hilde in Hearthmoor.'); return out; }
    if (!need) { out.push('The Guild has no key for this one. Coming soon.'); return out; }
    const [fid, r] = need, Fc = FACTIONS[fid], have = G.factions.rank(fid), m = (G.S.merit || {})[fid] || 0;
    out.push(`Key: ${Fc.name} at ${RANKS[r]} ("${Fc.titles[r]}", ${NEED[r]} ${Fc.cur}). You: ${RANKS[have]}, ${m} ${Fc.cur}.`);
    out.push(have >= r ? 'You have the standing. The Guild is still cutting this key: coming soon.' : 'Not yet. Gatewright Halvard can tell you how merit is earned.');
    return out;
  }
  look(g) {
    this.G.openDialogue({ id: 'sealed_' + g.arch, name: `${g.realm}'s gate (sealed)` }, { pages: this.pages(g) });
    const F = (this.G.S.flags = this.G.S.flags || {}); F.bf_looked = { ...(F.bf_looked || {}), [g.arch]: 1 };
    return true;
  }
  qa() {
    const c = this.ctx; if (!c) return null;
    return { sealed: (c.scene.game?.sealed || []).map((g) => g.arch), open: (c.scene.game?.portals || []).map((p) => p.to) };
  }
}
