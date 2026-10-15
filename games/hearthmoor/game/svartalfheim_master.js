// [SVARTALFHEIM] The Masterwork (story 3.9 + 9.6): Tansy's ripple quest that builds the Tinker's Heart (a Legendary trinket) at the Great
// Anvil on Forgefire Week and unlocks the secret hero Tinkerforge. Parts: 1 clock spring (the Foreman, NOT built yet), 3 amethyst
// (Tansy sells it here until the mine crystals drop it), 2 cold-steel (Tova's forge). The 3-strike beat is the 3.2 anvil ring.
// Deviation: the `wound_up` unique (+30% after 3 s unhit) is stored on the item but has no combat hook yet.
import { QUESTS, TALK, MARKER_HOOKS } from './data.js';
import { MERIT } from './factions.js';
import { GOODS, SHOPS } from './shop.js';
import { RARITY, makeItem } from './loot.js';
import { SV, ANVIL } from './svartalfheim_story.js';
import { forgefireDay } from './svartalfheim_festival.js';

const F = (S) => S.flags || {};
const flags = (S) => (S.flags = S.flags || {});
const q = (S, k) => (S.quests || {})[k] || 0;
const parts = (S) => { const i = S.inv || {}; return (i.clock_spring || 0) >= 1 && (i.amethyst || 0) >= 3 && (i.coldsteel || 0) >= 2; };
GOODS.amethyst = { name: 'Amethyst', about: 'Violet crystal from the mines. It catches rune-light and keeps a little.', price: 18 };
QUESTS.sv_master = { title: 'The Masterwork', giver: 'Tansy Brasswhistle', ripple: true, steps: {
  1: (S) => parts(S) ? 'Take the parts to the Great Anvil during Forgefire Week.' : 'Gather Tansy\'s parts: 1 clock spring (the Foreman), 3 amethyst, 2 cold-steel.',
  2: 'Build the Tinker\'s Heart at the Great Anvil, with Tansy and Dagna watching.',
  3: 'You built a legendary treasure with your own hands. Somewhere, a very small engineer is very proud.',
} };
export function TINKERS_HEART(S) {
  const it = makeItem(Math.max(10, S.lv || 1), 4, 'trinket');
  const k = RARITY[4].mul * (1 + (it.lv - 1) * 0.06);
  it.name = 'Tinker\'s Heart'; it.fixed = true; it.unique = 'wound_up'; it.crafted = true;
  it.mods = { stAdd: Math.round(4 * k), summonMul: +(0.03 * k).toFixed(3), crit: +(0.008 * k).toFixed(3) };
  it.gems = [null, null];
  it.about = 'A clockwork heart in a cage of amethyst. Stand still and it winds up. Your next hit lets it go.';
  return it;
}
export const masterOffer = (S) => SV(S) === 'befriend' && q(S, 'clockdeep') === 3 && !!(S.met || {}).tansy && !!(S.pets || {}).tick && !q(S, 'sv_master');

// called once from the Svartalfheim constructor (TALK.tansy is defined in svartalfheim.js, after this module loads)
export function installMaster() {
  if (SHOPS.tinker && !SHOPS.tinker.goods.includes('amethyst')) SHOPS.tinker.goods.push('amethyst');
  const t0 = TALK.tansy;
  TALK.tansy = (S) => {
    const base = t0(S);
    if (masterOffer(S)) return { pages: ['You want to build something legendary? Of course you do. Everybody does. Here\'s the list.', 'One clock spring (the Foreman keeps one), three amethyst (I sell those), two cold-steel (Tova\'s forge). Then the Great Anvil, on Forgefire Week. Dagna and I will watch.'],
      then: (G) => { G.setQuest('sv_master', 1); G.refreshMarkers && G.refreshMarkers(); } };
    if (q(S, 'sv_master') === 1 || q(S, 'sv_master') === 2) return { ...base, pages: [parts(S) ? 'You have everything! Great Anvil, Forgefire Week. Don\'t drop the spring.' : 'Parts: one clock spring, three amethyst, two cold-steel. The spring is the hard one.', ...(base.pages || [])] };
    return base;
  };
  MARKER_HOOKS.push((id, S) => { if (id === 'tinker' && masterOffer(S)) return 'quest_mark'; });
}

export class SvMaster {
  constructor(sv) { this.sv = sv; this.G = sv.G; }
  get ctx() { return this.sv.ctx; }
  attach(area) {
    const sv = this.sv, S = this.G.S;
    const qs = this.G.qs || new URLSearchParams(location.search);
    if (qs.get('svq') === 'master') { const f = flags(S); f.alliance = { ...(f.alliance || {}), svartalfheim: 'befriend' }; S.quests = S.quests || {}; S.quests.clockdeep = 3; S.quests.sv_master = 1; S.met = { ...(S.met || {}), tansy: 1 }; S.pets = { ...(S.pets || {}), tick: { name: 'Tick', bond: 1, fed: 0 } };
      S.inv = S.inv || {}; S.inv.clock_spring = 1; S.inv.amethyst = 3; S.inv.coldsteel = 2; S.day = Math.ceil(((S.day || 0) - 3) / 7) * 7 + 3; }
    if (area === 'forge_hall') sv.spot({ pos: [ANVIL[0] - 1.3, ANVIL[1] + 1.2], r: 1.7, label: 'build the Tinker\'s Heart at the Great Anvil (E / A)', show: () => (q(S, 'sv_master') === 1 || q(S, 'sv_master') === 2) && parts(S) && forgefireDay(S), act: () => this.build() });
  }
  build() {
    const G = this.G, S = G.S, f = flags(S), st = this.sv.story;
    if (q(S, 'sv_master') === 1) { G.setQuest('sv_master', 2); G.openDialogue({ id: 'tansy', name: 'Tansy Brasswhistle' }, { pages: ['(Tansy and Dagna gather round the Great Anvil. Tansy lays out the spring, the amethyst and the cold-steel.)', 'Tansy: "Three strikes. Slow ones. Clockwork hates a hurry."'] }); return; }
    const ph = (st.t - st.t0) % 2.0, hit = st.auto || (ph >= 1.4 && ph <= 1.95);
    if (!hit) { G.toast('Dagna: "Wait for the glow. The anvil talks. Listen."', 2.2); return; }
    f.sm_hits = (f.sm_hits || 0) + 1; G.toast(`Strike ${f.sm_hits}/3`, 1.6);
    const c = this.ctx; if (c && c.effects) c.effects.spawn('ember_pop', ANVIL[0], c.heightAt(ANVIL[0], ANVIL[1]) + 0.9, ANVIL[1]);
    if (f.sm_hits < 3) return;
    G.openDialogue({ id: 'tansy', name: 'Tansy Brasswhistle' }, { pages: ['(The last strike rings. The clockwork heart ticks once, twice, and starts to beat inside its amethyst cage.)', 'Tansy: "You built that? With those hands? I\'m going to cry into my goggles."'],
      then: (G2) => { const i = G2.S.inv; i.clock_spring -= 1; i.amethyst -= 3; i.coldsteel -= 2; (G2.S.bag = G2.S.bag || []).push(TINKERS_HEART(G2.S)); G2.S.unlocks = { ...(G2.S.unlocks || {}), tinkerforge: 1 };
        G2.setQuest('sv_master', 3); G2.toast('Secret hero unlocked: Tinkerforge', 3); G2.refreshMarkers && G2.refreshMarkers(); } });
  }
  update(dt) {
    const c = this.ctx, S = this.G.S, st = this.sv.story;
    if (this.sv.area === 'forge_hall' && c && c.effects && (q(S, 'sv_master') === 2) && forgefireDay(S) && Math.hypot(c.player.x - ANVIL[0], c.player.z - ANVIL[1]) < 6 && ((st.t - st.t0) % 2.0) < dt) c.effects.spawn('rune_circle', ANVIL[0], c.heightAt(ANVIL[0], ANVIL[1]) + 0.05, ANVIL[1]);
  }
  qa() { const S = this.G.S; return { quest: q(S, 'sv_master'), parts: parts(S), hits: F(S).sm_hits || 0, offer: masterOffer(S), heart: (S.bag || []).some((x) => x.name === 'Tinker\'s Heart'), tinkerforge: !!(S.unlocks || {}).tinkerforge }; }
}
