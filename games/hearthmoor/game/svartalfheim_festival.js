// [SVARTALFHEIM] Forgefire Week (story 2.7 festival + 3.10 bounty). Every 7th day (S.day % 7 === 3), befriend only, after The Clockwork
// Deep. Dagna offers the bounty: 3 true strikes at the Great Anvil (the 3.2 ring beat) + 3 forge orders from Copper Row townsfolk, then
// show her the work: +40 Realm Favor, 30 gold, 1 deep brass; the quest resets at the next festival. Conquer: the cold banner.
// Deviations: not gated to the day shift; the soot-smudge face decal, Tova's 20% discount and the anvil_ring r 3.0 are not built
// (those systems don't exist yet); the festival look is embers on the Great Forge floor, no bunting.
import { QUESTS, TALK, MARKER_HOOKS } from './data.js';
import { MERIT } from './factions.js';
import { SV, ANVIL } from './svartalfheim_story.js';

const F = (S) => S.flags || {};
const flags = (S) => (S.flags = S.flags || {});
const q = (S, k) => (S.quests || {})[k] || 0;
const gold = (G, n) => { G.S.gold = (G.S.gold || 0) + n; G.toast(`+${n} gold`, 1.8); G.drawBag && G.drawBag(); };
export const festDay = (S) => (S.day || 0) % 7 === 3;
export const forgefireDay = (S) => festDay(S) && SV(S) === 'befriend' && q(S, 'clockdeep') === 3;
const ORDERERS = { dw_a: 'a dwarf on the terrace', sv_a: 'a smith in a leather apron', haldis: 'Haldis the pool-keeper' };
const GIVE = ['ironbit', 'amethyst'];   // common items: any iron bits or amethyst (a Common gear piece also counts in the story; bits and amethyst are the bag items that exist)
MERIT.forgefire = 40;
QUESTS.forgefire = { title: 'Forgefire Week', giver: 'Dagna Coalbeard', side: true, bounty: true, steps: {
  1: (S) => { const w = S.forgefire || { strikes: 0, orders: 0 };
    return w.strikes < 3 || w.orders < 3 ? `Win the anvil contest (3 true strikes) and fill 3 forge orders on Copper Row. strikes ${Math.min(3, w.strikes)}/3 · orders ${Math.min(3, w.orders)}/3` : 'Show Dagna your work at the Great Anvil.'; },
  2: 'Show Dagna your work at the Great Anvil.',
  3: 'Forgefire Week done. Your name\'s chalked on the contest board. Spelled wrong, but chalked.',
} };

// a new festival day resets the bounty (3 -> 0) and the counters
export function sync(S) {
  if (!festDay(S) || SV(S) !== 'befriend') return;
  const w = S.forgefire;
  if (!w || w.fday !== S.day) { S.forgefire = { strikes: 0, orders: 0, fday: S.day, given: {} }; if (q(S, 'forgefire')) S.quests.forgefire = 0; }
}
const done = (S) => { const w = S.forgefire || {}; return (w.strikes || 0) >= 3 && (w.orders || 0) >= 3; };

const dagna0 = TALK.dagna;
TALK.dagna = (S) => {
  if (SV(S) === 'befriend' && q(S, 'clockdeep') === 3) {
    sync(S);
    if (forgefireDay(S) && !q(S, 'forgefire')) return { pages: ['Forgefire! Go and hit something. Not me. Something metal.', 'There\'s a contest at the Great Anvil: three true strikes. And Copper Row wants forge orders filled. Iron bits or amethyst, one each. Do both and show me.'],
      then: (G) => { G.setQuest('forgefire', 1); G.refreshMarkers && G.refreshMarkers(); } };
    if (q(S, 'forgefire') === 1 && done(S)) return { pages: ['Three true strikes and three orders? ...Not bad. I\'ll chalk your name on the board. I might even spell it right.'],
      then: (G) => { G.setQuest('forgefire', 3); G.factions.add('embassy', MERIT.forgefire, 'forgefire'); gold(G, 30); G.give('deep_brass', 1);
        const f = flags(G.S); if (!f.soot_smudge) { f.soot_smudge = 1; G.toast('Soot-smudge face decal unlocked (cosmetic).', 2.4); } G.refreshMarkers && G.refreshMarkers(); } };
    if (q(S, 'forgefire') === 1) return { pages: [`Forgefire! strikes ${Math.min(3, (S.forgefire || {}).strikes || 0)}/3, orders ${Math.min(3, (S.forgefire || {}).orders || 0)}/3. Hit the anvil when the glow is smallest.`] };
  }
  return dagna0(S);
};
for (const [id, who] of Object.entries(ORDERERS)) {
  const base = TALK[id];
  TALK[id] = (S) => {
    const w = S.forgefire;
    if (q(S, 'forgefire') === 1 && w && !(w.given || {})[id]) {
      const have = GIVE.find((k) => ((S.inv || {})[k] || 0) >= 1);
      const pages = [`Forgefire order! Spare me one iron bit or an amethyst, would you? Anything common will do.`];
      if (!have) return { pages: [...pages, '(You have no iron bits or amethyst on you.)'] };
      return { pages, choice: { id: 'ff_order', options: [
        { label: `Hand over ${have === 'ironbit' ? 'an iron bit' : 'an amethyst'}.`, pick: (G) => { G.take(have, 1); const w2 = G.S.forgefire; w2.given = { ...(w2.given || {}), [id]: 1 }; w2.orders += 1; G.refreshMarkers && G.refreshMarkers(); return { pages: ['Ha! Fills the order nicely. Forgefire to you.'] }; } },
        { label: 'Not now.', cancel: true, pick: () => null },
      ] } };
    }
    if (base) return base(S);
    return { pages: [festDay(S) && SV(S) === 'befriend' ? 'Forgefire! Best day of the week. All of it. The whole week. It\'s a day.' : `${who[0].toUpperCase()}${who.slice(1)} nods and goes back to work.`] };
  };
}
MARKER_HOOKS.push((id, S) => {
  if (id === 'dagna' && forgefireDay(S) && !q(S, 'forgefire')) return 'quest_mark';
  if (id === 'dagna' && q(S, 'forgefire') === 1 && done(S)) return 'quest_turnin';
});

export class SvFest {
  constructor(sv) { this.sv = sv; this.G = sv.G; this.fx = []; }
  get ctx() { return this.sv.ctx; }
  attach(area) {
    const sv = this.sv, G = this.G, S = G.S, c = this.ctx;
    const qs = G.qs || new URLSearchParams(location.search);
    if (qs.get('svq') === 'forgefire') { const f = flags(S); f.alliance = { ...(f.alliance || {}), svartalfheim: 'befriend' }; S.quests = S.quests || {}; S.quests.clockdeep = 3; S.day = Math.ceil(((S.day || 0) - 3) / 7) * 7 + 3; }
    sync(S);
    if (area === 'forge_hall') sv.spot({ pos: ANVIL, r: 1.9, label: 'strike the Great Anvil (Forgefire contest, E / A)', show: () => forgefireDay(S) && q(S, 'forgefire') === 1 && ((S.forgefire || {}).strikes || 0) < 3, act: () => this.strike() });
    if (area !== 'svartalfheim' && area !== 'forge_hall') return;
    if (forgefireDay(S)) {
      if (!flags(S).ff_banner || flags(S).ff_banner !== S.day) { flags(S).ff_banner = S.day; G.toast('Forgefire Week! Every forge in Anvildeep is open. (It\'s a day. Don\'t tell the dwarves.)', 4); }
      if (area === 'forge_hall' && c && c.gamefx && c.gamefx.meta.effects.forge_embers) for (const [x, z] of [[-4.5, -1.5], [4.5, -1.5], [0, 2.6]]) this.fx.push(c.gamefx.spawn('forge_embers', x, c.heightAt(x, z), z, { duration: Infinity }));
    } else if (festDay(S) && SV(S) === 'conquer' && flags(S).ff_cold !== S.day) { flags(S).ff_cold = S.day; G.toast('The forges stay cold. Nobody in Anvildeep is celebrating.', 3.6); }
  }
  detach() { for (const f of this.fx) if (f) f.dur = f.t + 0.2; this.fx = []; }
  strike() {
    const G = this.G, S = G.S, st = this.sv.story, ph = (st.t - st.t0) % 2.0, hit = st.auto || (ph >= 1.4 && ph <= 1.95), w = S.forgefire;
    if (hit) { w.strikes += 1; G.toast(['Dagna: "Hm. Not bad."', 'Dagna: "That one sang. Do it again."', 'Dagna: "Three true."'][Math.min(2, w.strikes - 1)] + ` (${w.strikes}/3)`, 2.2); const c = this.ctx; if (c && c.effects) c.effects.spawn('ember_pop', ANVIL[0], c.heightAt(ANVIL[0], ANVIL[1]) + 0.9, ANVIL[1]); G.refreshMarkers && G.refreshMarkers(); }
    else G.toast('Dagna: "Wait for the glow. The anvil talks. Listen."', 2.2);
  }
  update(dt) {
    const c = this.ctx, S = this.G.S, st = this.sv.story;
    if (this.sv.area === 'forge_hall' && c && c.effects && forgefireDay(S) && q(S, 'forgefire') === 1 && ((S.forgefire || {}).strikes || 0) < 3 && Math.hypot(c.player.x - ANVIL[0], c.player.z - ANVIL[1]) < 6 && !(q(S, 'sv_trial') === 1)) {
      if (((st.t - st.t0) % 2.0) < dt) c.effects.spawn('rune_circle', ANVIL[0], c.heightAt(ANVIL[0], ANVIL[1]) + 0.05, ANVIL[1]);
    }
  }
  qa() { const S = this.G.S; return { day: S.day || 0, festDay: festDay(S), forgefireDay: forgefireDay(S), forgefire: S.forgefire || null, quest: q(S, 'forgefire') }; }
}
