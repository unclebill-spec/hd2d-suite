// [SVARTALFHEIM] The minimal companion roster + swap (lead's section 15 decision: recruited companions stay unlocked, you bring ONE
// at a time, and you swap at Bifrost's Gatekeepers' Guild desk (Halvard) or any inn (the Bakery Lane innkeeper)).
// What exists: Lumi (alfheim_lumi.js) is the only companion with a body. Dagna and Tobble are recruitable names + the swap (the
// choice is stored in flags.companion_active); their in-world followers come later. Lumi's `joined()` now also checks the choice.
// Tick is a pet, not a companion: he swaps at the Stray Den like the others.
import { TALK } from './data.js';
import { Lumi } from './alfheim_lumi.js';

export const COMP = { lumi: 'Lumi', dagna: 'Dagna Coalbeard', tobble: 'Tobble Capwhistle' };
const flags = (S) => (S.flags = S.flags || {});
export const owned = (S) => Object.keys(COMP).filter((k) => ((S.flags || {}).companions || {})[k]);
export const active = (S) => { const o = owned(S), a = (S.flags || {}).companion_active; return o.includes(a) ? a : o[0] || null; };
export function unlock(G, id) {
  const f = flags(G.S); if ((f.companions || {})[id]) return false;
  f.companions = { ...(f.companions || {}), [id]: 1 };
  if (!f.companion_active) f.companion_active = id;
  G.toast && G.toast(`${COMP[id]} is now one of your companions. (Bring one at a time: swap at the Guild desk or any inn.)`, 3.2);
  return true;
}
export function swap(G, id) {
  const f = flags(G.S); if (!owned(G.S).includes(id)) return false;
  f.companion_active = id; G.toast && G.toast(`${COMP[id]} walks with you now.`, 2.4);
  const L = G.alfheim && G.alfheim.lumi; if (L && L.ctx) { try { L.attach(L.ctx, L.area); } catch (e) { /* re-attach only toggles her body */ } }
  return true;
}
const swapEntry = (S) => ({
  pages: [`${COMP[active(S)]} is with you. Who else is coming?`],
  choice: { id: 'comp_swap', options: [
    ...owned(S).filter((k) => k !== active(S)).map((k) => ({ label: `${COMP[k]}.`, pick: (G) => { swap(G, k); return { pages: [`${COMP[k]} falls in beside you. One at a time, mind. They bicker.`] }; } })),
    { label: 'Never mind.', cancel: true, pick: () => null },
  ] },
});
const withSwap = (id) => {
  const base = TALK[id];
  TALK[id] = (S) => {
    const e = base(S);
    if (owned(S).length < 2 || !e) return e;
    const opt = { label: 'Swap my companion.', pick: () => swapEntry(S) };
    if (e.choice) return { ...e, choice: { ...e.choice, options: [opt, ...e.choice.options] } };
    if (e.then) return e;
    return { ...e, choice: { id: 'comp_swap_gate', options: [opt, { label: 'Never mind.', cancel: true, pick: () => null }] } };
  };
};
withSwap('gatewright'); withSwap('innkeeper');

// Lumi only walks with you while she is the active companion
const j0 = Lumi.prototype.joined;
Lumi.prototype.joined = function () { return j0.call(this) && active(this.G.S) === 'lumi'; };
