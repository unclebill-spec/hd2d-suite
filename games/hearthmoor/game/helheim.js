// [HELHEIM] Helheim (realm-helheim branch): areas, quests, stance, talk, gate. Bosses live in helheim_boss.js.
// Story: staging story/helheim.md. Plan + status: HELHEIM_PROGRESS.md.
// Decisions (final, Oct 21 2026):
//  - `redeemable` is imported from game/niflheim.js (Veyra's redemption check, niflheim.md 8.2), unchanged; Muspelheim lock stays behind NIFL_MUSP_LOCK (niflheim.js lockedBy).
//  - Helheim is a STANCE only (S.flags.hel = 'kind' | 'defiant'), never marches (HEL_MARCHES = false).
//  - A fallen ally dragged back by force returns 'pale' (S.flags.bh_pale): cosmetic only, no stat changes.
//  - Mordrath's fall removes one finale wave (finaleWaves).
import { TALK, ITEMS, QUESTS, MARKER_HOOKS } from './data.js';
import { REALM, MERIT, Factions } from './factions.js';
import { SPAWNS } from './heroes.js';
import { SHOPS, GOODS } from './shop.js';
import { RARE_AREAS } from './rares.js';
import { KINDS as WX_KINDS, WX_HOOK } from './weather.js';
import { WAYS, WAY_SAY } from './ravenhold.js';
import { Crossing } from './bifrost.js';
import { redeemable, lockedBy as nfLocked, evidenceCount } from './niflheim.js';
import { HH_FX } from './helheim_fx.js';
import { HelBoss, BOSS_AT } from './helheim_boss.js';

export const HEL_PLANNED = { helheim: 'Gloamhaven', hh_shore: 'The Lantern Shore', hh_archive: 'The Quiet Archive', ossuary: 'The Ossuary of Whispers', ossuary2: 'The Ossuary of Whispers: the Pale Throne' };
export const HEL_BUILT = ['helheim', 'hh_shore', 'hh_archive', 'ossuary', 'ossuary2'];
export const AREAS_HEL = Object.fromEntries(HEL_BUILT.map((a) => [a, `areas/${a}/`]));
export const AREA_NAMES_HEL = Object.fromEntries(HEL_BUILT.map((a) => [a, HEL_PLANNED[a]]));
export const HEL_AREAS = Object.keys(HEL_PLANNED);
export const HEL_MARCHES = false;

export const flags = (S) => (S.flags = S.flags || {});
export const F = (S) => S.flags || {};
export const q = (S, k) => (S.quests || {})[k] || 0;
const found = (S, ...ks) => ks.filter((k) => (S.found || {})[k]).length;
export const mark = (G) => { G.refreshMarkers && G.refreshMarkers(); G.save && G.save(); };
const gold = (G, n) => { G.S.gold = (G.S.gold || 0) + n; G.toast(`+${n} gold`, 1.8); G.drawBag && G.drawBag(); };

export const helStance = (S) => F(S).hel || null;
export const kind = (S) => helStance(S) === 'kind';
export const defiant = (S) => helStance(S) === 'defiant';
export const helRealm = (S) => (defiant(S) ? 'gate' : 'embassy');
export const eiraBranch = (S) => {
  if (F(S).rift_breaker) return 'breaker';
  if (redeemable(S)) return 'thread';
  if (nfLocked(S)) return 'locked';
  return 'notyet';
};
export const finaleWaves = (S, base) => base - (F(S).hh_mordrath ? 1 : 0);
export const BRIDGE_REALMS = ['alfheim', 'svartalfheim', 'jotunheim', 'muspelheim', 'niflheim', 'asgard', 'vanaheim'];
export const bridgeLanterns = (S) => { const a = F(S).alliance || {}; return BRIDGE_REALMS.map((r) => ({ realm: r, lit: a[r] === 'befriend', restless: a[r] === 'conquer' })); };
export const HEL_GATE = ['embassy', 2];
export const isPale = (S) => !!F(S).bh_pale;
export const fallenAlly = (S) => F(S).fallen_ally || null;
{
  const realm0 = Factions.prototype.realm;
  Factions.prototype.realm = function realm() { return HEL_AREAS.includes(this.G.area) ? helRealm(this.G.S) : realm0.call(this); };
}
Object.assign(REALM, { helheim: 'embassy', hh_shore: 'embassy', hh_archive: 'embassy', ossuary: 'embassy', ossuary2: 'embassy' });
export const HEL_MERIT = { hh_gate: 60, paletoll: 60, hh_home_d: 80, ossuary_d: 120, hh_bridge: 40, hh_stories: 60, hh_ledger: 60, hh_home: 80, hh_eira: 40, ossuary: 120, lanternboat: 40 };
Object.assign(MERIT, HEL_MERIT);

export const HH_ARCH = { rect: [9.25, -12.3, 10.75, -11.45], pos: [10.0, -11.9], spawn: [10.0, -10.1, 'down'] };
const HUB_GATE = { to: 'bifrost', spawn: 'from_helheim', rect: [-0.9, 10.1, 0.9, 11.1], label: "Hel's arch back to Bifrost Crossing" };
export const gateOpen = (S, qs) => !!(F(S).hh_gate_open || F(S).hg_boat || (qs && qs.has('hhq') && qs.get('hhq') !== 'gate'));
export const live = () => HEL_BUILT.includes('helheim');

Object.assign(SPAWNS, {
  ossuary: [{ id: 'os_shade0', role: 'shade', pos: [-1.6, 0.6] }, { id: 'os_skel0', role: 'skeleton_line', pos: [-1.2, -16.6] }, { id: 'os_lant0', role: 'grave_lantern', pos: [2.6, -28.4] }, { id: 'os_golem0', role: 'garnet_golem', pos: [-2.0, -43.0] }],
  ossuary2: [{ id: 'os2_lich0', role: 'lich', pos: [-2.4, -17.6], night: true }],
});
RARE_AREAS.helheim = { bases: ['gravelamp'], spots: [[9.0, 6.4], [-9.4, -4.6]] };
RARE_AREAS.ossuary2 = { bases: ['hollowchoir', 'gravelamp'], spots: [[-1.0, -2.2]] };
export const SPRINGS = { hh_spring: 'helheim', ls_spring: 'hh_shore', os_spring: 'ossuary' };
WAYS.ossuary2 = ["the Ossuary of Whispers, Mordrath's Vault", 'ossuary2', 'from_waystone'];
WAY_SAY.ossuary2 = 'The waystone hums under the bones. Someone kept it lit, even down here.';

WX_KINDS.gloam_fog = [{ preset: 'mist', rate: 1.2 }];
WX_KINDS.soul_lights = [{ preset: 'glow_mist', rate: 0.6 }];
const wxHash = (n) => { let x = (Math.imul(n | 0, 0x9E3779B1) + 0x7F4A7C15) | 0; x = Math.imul(x ^ (x >>> 16), 0x85EBCA6B); x = Math.imul(x ^ (x >>> 13), 0xC2B2AE35); return ((x ^ (x >>> 16)) >>> 0) / 4294967296; };
export const hhWx = (day, t) => { const r = wxHash(day * 4 + Math.floor(t * 4) + 6161); return r < 0.5 ? 'gloam_fog' : r < 0.85 ? 'soul_lights' : 'clear'; };
WX_HOOK.helheim = hhWx; WX_HOOK.hh_shore = hhWx;

Object.assign(ITEMS, {
  living_lamp: { name: 'Living-lamp', px: 'glowseed', about: 'A lamp that burns only for the living.' },
  ossuary_key: { name: 'Ossuary key', px: 'tonic', about: 'A bone-white key with violet runes.' },
  ledger_page: { name: 'Ledger page', px: 'glowseed', about: 'A torn page of the Ledger of Names, with a red claw-mark and a rime fingerprint.' },
  button: { name: 'Bright button', px: 'glowseed', about: 'Ravens like bright things.' },
  flour: { name: "Hettie's flour", px: 'denbiscuit', about: 'Flour for one last loaf.' },
  soul_glass: { name: 'Soul-glass', px: 'glowseed', about: 'Violet glass with a soft voice in it.' },
  demon_heart: { name: 'Demon-heart', px: 'glowseed', about: "Mordrath's heart. A socket item." },
  pale_crown: { name: 'The Pale Crown', px: 'glowseed', about: 'A trophy.' },
  eira_thread: { name: "Eira's thread", px: 'glowseed', about: 'A violet lantern-thread for her sister.' },
  gloamreaver: { name: 'Gloamreaver', px: 'glowseed', about: 'A violet soul scythe.' },
  violet_shawl: { name: 'Violet shawl', px: 'glowseed', about: 'Cosmetic.' },
  ghost_lantern: { name: 'Ghost-lantern', px: 'glowseed', about: 'Cosmetic.' },
});
Object.assign(GOODS, { violet_shawl: { name: 'Violet shawl', about: 'Cosmetic.', price: 30 }, button: { name: 'Bright button', about: 'Ravens like bright things.', price: 2 } });
SHOPS.innghost = { name: 'The Last Hearth Inn', keeper: 'Hettie Tallow', goods: ['tonic', 'button', 'violet_shawl'], gear: { n: 2, rar: [0, 1] }, sellMul: 1 };

Object.assign(QUESTS, {
  hh_gate: { title: "Hel's Leave", giver: 'Envoy Ingrith Goldrune', story: true, steps: {
    1: (S) => (!F(S).hg_petition ? 'Write a petition to Hel at the Bifrost embassy desk.' : !F(S).hg_boat ? "Wait for the lantern-boat's answer at the arch." : 'Carry the living-lamp through the arch.'),
    2: 'Meet Hel in Gloamhaven.', 3: 'Hel has let you in.' } },
  hh_bridge: { title: 'The Lantern Bridge', giver: 'Hel', story: true, steps: { 1: (S) => `Light the bridge lanterns. ${F(S).lb_lit || 0}/3`, 2: 'Tell Hel the bridge is bright.', 3: 'The dead can find their way again.' } },
  hh_stories: { title: 'Three Ghost Stories', giver: 'Hettie Tallow', story: true, steps: { 1: (S) => `Help three ghosts. ${found(S, 'gs_baker', 'gs_sailor', 'gs_child')}/3`, 2: 'Tell Hettie.', 3: 'Three ghosts rest easy.' } },
  hh_ledger: { title: 'The Ledger of Names', giver: 'Quillon Greymarch', story: true, steps: { 1: (S) => `Find the torn pages. ${found(S, 'lg_p1', 'lg_p2', 'lg_p3')}/3`, 2: 'Read them with Hel.', 3: 'Someone below is binding the dead.' } },
  hh_take: { title: 'The Pale Toll', giver: 'Gatewright Halvard', story: true, steps: {
    1: (S) => { const n = found(S, 'pt_l1', 'pt_l2', 'pt_l3'); return n < 3 ? `Snuff the soul-lamps. ${n}/3` : F(S).pt_odric ? 'Take the Ossuary key.' : 'Beat Ser Odric.'; }, 2: 'Break into the Ossuary.', 3: "You're in." } },
  hh_home: { title: 'Bring Them Home', giver: 'Hel', story: true, steps: { 1: (S) => (!F(S).bh_name ? "Find your friend's name in Mordrath's vault." : 'Find your friend on the Lantern Shore.'), 2: (S) => (defiant(S) ? 'Drag them across the bridge.' : "Walk them home, and don't look back."), 3: "They're home." } },
  hh_eira: { title: "Eira's Word", giver: 'Eira Ashmantle', story: true, steps: { 1: 'Meet the girl with the lantern.', 2: 'Hear her out.', 3: 'Eira has said her piece.' } },
  ossuary: { title: 'The Ossuary of Whispers', giver: 'Hel', story: true, steps: {
    1: (S) => { const n = found(S, 'os_n1', 'os_n2', 'os_n3'); return n < 3 ? `Free the bound names. ${n}/3` : 'Face Mordrath.'; }, 2: (S) => (defiant(S) ? 'Leave before the knights find you.' : "Return the names to Hel's Ledger."), 3: "Mordrath's tithe is broken." } },
  hh_scythe: { title: 'Gloamreaver', giver: 'Quillon Greymarch', ripple: true, steps: { 1: (S) => `Bring 3 soul-glass. ${found(S, 'sgl_1', 'sgl_2', 'sgl_3')}/3`, 2: 'Watch the binding.', 3: 'Gloamreaver is yours.' } },
  hh_raven: { title: 'Inkling', giver: 'Corvin Lanternmere', ripple: true, steps: { 1: (S) => `Leave a button on the jetty. ${F(S).ik_nights || 0}/3`, 2: 'Ask Corvin.', 3: 'Inkling has chosen you.' } },
  lanternboat: { title: 'Lantern-Boat Night', giver: 'Hel', bounty: true, steps: { 1: (S) => { const g = S.lboat || {}; return `Float ${g.float ? 1 : 0}/1, story ${g.story ? 1 : 0}/1, row ${g.row ? 1 : 0}/1.`; }, 2: 'Sit with Hel.', 3: 'The lake holds every light.' } },
});
export const HEL_QUESTS = ['hh_gate', 'hh_bridge', 'hh_stories', 'hh_ledger', 'hh_take', 'hh_home', 'hh_eira', 'ossuary', 'hh_scythe', 'hh_raven', 'lanternboat'];
const festival = (S) => kind(S) && (S.day || 0) % 7 === 4;

const choiceOpts = (S) => [
  { label: 'Ask how I can help.', locked: defiant(S), lockedLabel: '(Locked. You broke her gate.)',
    pick: () => ({ pages: ['"Then light my bridge."'], then: (G) => { flags(G.S).hel = 'kind'; if (!q(G.S, 'hh_bridge')) G.setQuest('hh_bridge', 1); mark(G); } }) },
  { label: "Give me the Ossuary. I'll handle it myself.", locked: q(S, 'hh_ledger') === 3, lockedLabel: '(Locked. You gave her your word.)',
    pick: () => ({ pages: ['"Go on, then. I\'ll write your name in pencil."'], then: (G) => { flags(G.S).hel = 'defiant'; if (!q(G.S, 'hh_take')) G.setQuest('hh_take', 1); mark(G); } }) },
].map((o) => (o.locked ? { label: o.lockedLabel, locked: true, pick: () => ({ pages: ['(Hel only looks at you.)'] }) } : { label: o.label, pick: o.pick }));
function lboatCheck(G) { const g = G.S.lboat || {}; if (g.float && g.story && g.row && q(G.S, 'lanternboat') === 1) G.setQuest('lanternboat', 2); mark(G); }
function notYetWhy(S) {
  const f = F(S), miss = [];
  if ((f.alliance || {}).niflheim !== 'befriend') miss.push('Mistmere has to call you a friend');
  if ((f.nf_vigil || 0) < 3) miss.push('my lanterns in Mistmere need lighting');
  if (evidenceCount(S) < 3) miss.push(`more of her marks (${evidenceCount(S)}/3)`);
  return miss.length ? `(What's missing: ${miss.join('; ')}.)` : '(Nothing you can mend from here.)';
}
Object.assign(TALK, {
  hel(S) {
    const f = F(S), st = (k) => q(S, k);
    if (st('hh_gate') === 2) return { pages: ['"A living lamp, in my town. Sit."'], then: (G) => { G.setQuest('hh_gate', 3); flags(G.S).hh_gate_open = 1; G.factions.add('gate', MERIT.hh_gate, 'hh_gate'); gold(G, 50); mark(G); } };
    if (st('hh_gate') === 3 && !f.hel) {
      const L = bridgeLanterns(S);
      const opener = f.rift_breaker ? 'You walk with the cold one. Walk carefully here.' : f.hg_line === 'help' ? 'You came to help the dead. Few do.' : f.hg_line === 'someone' ? 'You came for someone. Everyone does.' : 'You came because you must. Honest.';
      return { pages: [opener, ...(L.some((x) => x.lit) ? ["Your friends sent lights ahead."] : []), ...(L.some((x) => x.restless) ? ["You've sent me many. I'm counting."] : []), 'Someone below is stealing names from my Ledger. What will you do?'], choice: { id: 'hel_stance', options: choiceOpts(S) } };
    }
    if (st('hh_bridge') === 2) return { pages: ['"There. They can see their way."'], then: (G) => { G.setQuest('hh_bridge', 3); G.factions.add('embassy', MERIT.hh_bridge, 'hh_bridge'); if (!q(G.S, 'hh_stories')) G.setQuest('hh_stories', 1); if (!q(G.S, 'hh_ledger')) G.setQuest('hh_ledger', 1); mark(G); } };
    if (st('hh_ledger') === 2) return { pages: ['(A red claw-mark on each page; a blue-black rime fingerprint in the margins.)', '"He takes their names. She takes the rest."', '"The Ossuary key. Bring my names home."'], then: (G) => { G.setQuest('hh_ledger', 3); flags(G.S).hh_cleared = 1; G.S.evidence = { ...(G.S.evidence || {}), helheim: 'ledger' }; G.give('ossuary_key', 1); G.factions.add('embassy', MERIT.hh_ledger, 'hh_ledger'); if (!q(G.S, 'ossuary')) G.setQuest('ossuary', 1); mark(G); } };
    if (st('ossuary') === 2 && kind(S)) return { pages: ['(Hel writes the names back in.)', '"Ink, this time."'], then: (G) => { G.setQuest('ossuary', 3); flags(G.S).hh_resolved = 1; G.factions.add('embassy', MERIT.ossuary, 'ossuary'); mark(G); } };
    if (fallenAlly(S) && !st('hh_home') && f.hel) return { pages: ['"Your friend is here, without their name. Find it in his vault."'], then: (G) => { G.setQuest('hh_home', 1); mark(G); } };
    if (st('lanternboat') === 2) return { pages: ['"They can hear you. They always could."'], then: (G) => { G.setQuest('lanternboat', 3); G.factions.add('embassy', MERIT.lanternboat, 'lanternboat'); G.give('ghost_lantern', 1); mark(G); } };
    if (festival(S) && st('hh_bridge') >= 3 && (!st('lanternboat') || st('lanternboat') === 3) && (!S.lboat || S.lboat.day !== S.day)) return { pages: ['"Lantern-Boat Night."'], then: (G) => { G.S.lboat = { day: G.S.day }; G.setQuest('lanternboat', 1); mark(G); } };
    return { pages: [defiant(S) ? '"Pencil, still."' : '"Mind your lamp."'] };
  },
  ferryman(S) {
    const st = q(S, 'hh_raven'), f = F(S);
    if (kind(S) && !st && q(S, 'hh_bridge') >= 3) return { pages: ['"Leave a raven a button on the jetty. Three nights."'], then: (G) => { G.setQuest('hh_raven', 1); G.give('button', 1); mark(G); } };
    if (st === 1 && (f.ik_lastDay ?? -1) < (S.day || 0) && !(S.inv || {}).button) return { pages: ['"Another button. Another night."'], then: (G) => G.give('button', 1) };
    if (st === 2) return { pages: ['(A black raven with violet-tipped feathers waits on the willow.)'], then: (G) => { G.setQuest('hh_raven', 3); flags(G.S).inkling = 1; G.S.pets = G.S.pets || {}; G.S.pets.inkling = G.S.pets.inkling || { name: 'Inkling', bond: 1, fed: 0, lastFed: null };
      if (G.pets) G.pets.swap('inkling'); else G.S.pet = { id: 'inkling', name: 'Inkling', bond: 1 }; G.toast && G.toast('✦ Inkling the gloam raven joined you. Aura: Gloam Sight. (Swap at the Stray Den.)', 3); mark(G); } };
    if (st === 3 && S.pet && S.pet.id === 'inkling') return { pages: ['"Living? Lovely. Mind your lamp, love, and mind that bird. It\'s had three of my buttons."'] };   // [HELHEIM] fun pass
    return { pages: ['"Living? Lovely. Mind your lamp, love."'] };
  },
  innghost(S) {
    const st = q(S, 'hh_stories');
    if (defiant(S)) return { pages: ['"No soup for gate-breakers."'] };
    if (st === 2) return { pages: ['"All three? They\'ll sleep like babies."'], then: (G) => { G.setQuest('hh_stories', 3); G.factions.add('embassy', MERIT.hh_stories, 'hh_stories'); mark(G); } };
    if (st === 1 && !(S.inv || {}).flour && !(S.found || {}).gs_baker) return { pages: ['"Take Old Marrow my flour."'], then: (G) => G.give('flour', 1) };
    if (q(S, 'lanternboat') === 1 && !(S.lboat || {}).story) return { pages: ['(Hettie tells the one about the boatman who never got wet.)'], then: (G) => { G.S.lboat = { ...(G.S.lboat || {}), story: 1 }; lboatCheck(G); } };
    return { pages: ['"Sit, sit, love. Smell the soup."'], then: (G) => { G.shopUI && G.shopUI.show('innghost'); } };
  },
  bakerghost(S) {
    if (q(S, 'hh_stories') === 1 && (S.inv || {}).flour && !(S.found || {}).gs_baker) return { pages: ['(He bakes, you eat, and he fades into violet light.)'], then: (G) => { G.S.inv.flour -= 1; G.hel.find('gs_baker'); G.hel.storyCheck(); } };
    return { pages: ['"Best crust in Helheim."'] };
  },
  sailorghost(S) {
    if (q(S, 'hh_stories') === 1 && (S.found || {}).gs_ship && !(S.found || {}).gs_sailor) return { pages: ['"My ship! Off we go."'], then: (G) => { G.hel.find('gs_sailor'); G.hel.storyCheck(); } };
    return { pages: ['"Have you seen my ship? She\'s very small."'] };
  },
  childghost(S) {
    if (q(S, 'hh_stories') === 1 && !(S.found || {}).gs_child) return { pages: ['"Walk me to the shore? We could float a lantern."'], then: (G) => { flags(G.S).gs_walk = 1; mark(G); } };
    return { pages: ['"I collect buttons."'] };
  },
  gloam_folk(S) { return { pages: [["Mind the road. It wails, but it doesn't bite.", "It's always Tuesday.", "The lake's lovely tonight."][(S.day || 0) % 3]] }; },
  archivist_hh(S) {
    const st = (k) => q(S, k);
    if (st('hh_scythe') === 2) return { pages: ['"Gloamreaver. Do not swing it indoors."'], then: (G) => { G.S.inv.soul_glass = Math.max(0, (G.S.inv.soul_glass || 0) - 3); G.give('gloamreaver', 1); G.setQuest('hh_scythe', 3); mark(G); } };
    if (st('hh_scythe') === 1 && found(S, 'sgl_1', 'sgl_2', 'sgl_3') >= 3) return { pages: ['"Three! Now Hel."'], then: (G) => { G.setQuest('hh_scythe', 2); mark(G); } };
    if (kind(S) && st('ossuary') >= 3 && !st('hh_scythe')) return { pages: ['"Bring me three soul-glass."'], then: (G) => { G.setQuest('hh_scythe', 1); mark(G); } };
    return { pages: ['"Three pages are missing. I notice these things."'] };
  },
  eira_spirit(S) {
    const f = F(S), ready = (q(S, 'hh_ledger') === 3 || q(S, 'hh_take') >= 2) && !!f.veyra_revealed;
    if (!ready || q(S, 'hh_eira') === 3) return { pages: [q(S, 'hh_eira') === 3 ? '"Go gently."' : '(A girl with a cold-fire lantern looks out over the lake.)'] };
    const b = eiraBranch(S), hi = "You're the one my sister keeps counting. I'm Eira.";
    const P = { thread: [hi, "I said 'ask first' because I was scared.", 'You asked. Take this to her.'], locked: [hi, 'You stood with the fire. I won\'t hold it against you.', 'Stop her. Gently.'],
      notyet: [hi, "She's not ready, or you aren't.", notYetWhy(S)], breaker: ["You walk with her. I'm Eira.", "Don't let her be cruel through you."] }[b];
    return { pages: P, then: (G) => { flags(G.S)[{ thread: 'eira_thread', locked: 'eira_blessing', notyet: 'eira_blessing', breaker: 'eira_warned' }[b]] = 1; if (b === 'thread') G.give('eira_thread', 1); G.setQuest('hh_eira', 3); G.factions.add('embassy', MERIT.hh_eira, 'hh_eira'); mark(G); } };
  },
  tithe() {
    const opt = (label, k, t) => ({ label, pick: () => ({ pages: [t], then: (G) => { flags(G.S)[k] = 1; mark(G); } }) });
    return { pages: ["Veyra wants the names. They're yours now."], choice: { id: 'hh_tithe', options: [opt('Give them to Veyra.', 'hh_tithe_given', '(The cages go cold.)'), opt('Keep them.', 'hh_tithe_kept', '(The names turn toward you.)'), opt('Let them go.', 'hh_tithe_freed', '(The names rise like moths.)')] } };
  },
});
MARKER_HOOKS.push((id, S) => {
  const f = F(S), st = (k) => q(S, k);
  if (id === 'hel' && (st('hh_gate') === 2 || (st('hh_gate') === 3 && !f.hel) || st('hh_bridge') === 2 || st('hh_ledger') === 2 || (st('ossuary') === 2 && kind(S)) || (fallenAlly(S) && !st('hh_home') && f.hel) || st('lanternboat') === 2)) return 'quest_mark';
  if (id === 'innghost' && st('hh_stories') === 2) return 'quest_mark';
  if (id === 'eira_spirit' && (st('hh_ledger') === 3 || st('hh_take') >= 2) && f.veyra_revealed && st('hh_eira') !== 3) return 'quest_mark';
});

const BRIDGE = [[0.0, 3.0], [0.0, 1.0], [0.0, -1.0]];
const PAGES = { lg_p1: ['helheim', [0.0, 6.5]], lg_p2: ['hh_shore', [-5.2, 0.4]], lg_p3: ['hh_archive', [2.2, 0.2]] };
const SOUL_LAMPS = [[-2.2, 7.3], [2.2, 7.3], [6.0, 3.6]];
const HALL = [0.0, -7.0], OS_DOOR = [0.0, -6.8], LEDGER = [0.0, -3.0], SHIP = [-5.0, -2.0], JETTY = [0.0, 0.8], NAME_CAGE = [0.0, -32.4];
const CAGES = { os_n1: ['ossuary', [-4.4, -29.0]], os_n2: ['ossuary', [4.2, -60.4]], os_n3: ['ossuary2', [4.6, -14.6]] };
const SGL = { sgl_1: ['ossuary', [4.4, -29.0]], sgl_2: ['ossuary', [4.6, -43.6]], sgl_3: ['ossuary2', [0.0, -19.4]] };
const HEARTS = [[-3.0, -46.4], [0.0, -46.4], [3.0, -46.4]];

export class Helheim {
  constructor(G) { this.G = G; this.ctx = null; this.area = null; this.fx = []; this.spots = []; this.cb = {}; this.sp = {}; this.qaDone = null; G.hel = this; this.gate = new HhGate(this); this.bosses = new HelBoss(this); this.wrap(); }
  qs() { return this.G.qs || new URLSearchParams(location.search); }
  wrap() {
    const G = this.G; if (!G.harbor) return;
    const p0 = G.harbor.prompt.bind(G.harbor), i0 = G.harbor.interact.bind(G.harbor), t0 = G.harbor.onTap.bind(G.harbor);
    G.harbor.prompt = (...a) => this.prompt() || p0(...a);
    G.harbor.interact = (...a) => this.interact() || i0(...a);
    G.harbor.onTap = (hit, ...a) => this.onTap(hit) || t0(hit, ...a);
  }
  spot(o) { this.spots.push({ r: 1.6, show: () => true, ...o }); }
  nearSpot() {
    const c = this.ctx; if (!c || this.G.dlg) return null;
    let best = null, bd = 1e9;
    for (const s of this.spots) { if (!s.show()) continue; const d = Math.hypot(c.player.x - s.pos[0], c.player.z - s.pos[1]); if (d < s.r && d < bd) { bd = d; best = s; } }
    return best;
  }
  prompt() { const s = this.nearSpot(); return s ? (typeof s.label === 'function' ? s.label() : s.label) : ''; }
  interact() { const s = this.nearSpot(); if (!s) return false; s.act(); return true; }
  onTap(hit) {
    const c = this.ctx; if (!c || !hit) return false;
    for (const s of this.spots.filter((x) => x.show())) {
      if (Math.hypot(hit.x - s.pos[0], hit.z - s.pos[1]) > 0.9) continue;
      if (Math.hypot(c.player.x - s.pos[0], c.player.z - s.pos[1]) < s.r) s.act(); else c.walkTo(s.pos[0], s.pos[1] + 0.9);
      return true;
    }
    return false;
  }
  look(id, name, pages, then) { this.G.openDialogue({ id, name }, { pages, then }); }
  foe(sp, then, yielded) {
    const C = this.G.combat; if (!C || !this.ctx) return null;
    const A = this.ctx.actors, role = A && A.sheetOf && A.sheetOf(sp.role) ? sp.role : 'wraith';
    const e = C.spawnEnemy({ once: true, noRespawn: true, ...sp, role }, true); e.state = 'chase';
    const done = () => { delete this.cb[sp.id]; (yielded && sp.trial ? yielded : then)(e); };
    e.onKill = done; if (yielded) e.onYield = done; this.cb[sp.id] = done;
    return e;
  }
  moveTo(x, z) { const c = this.ctx; if (!c) return; c.player.x = x; c.player.z = z; c.player.y = c.heightAt(x, z); }
  find(k) { const S = this.G.S; S.found = { ...(S.found || {}), [k]: 1 }; this.G.save && this.G.save(); }
  fxAt(ctx, name, x, y, z, o = {}) {
    if (!ctx || !ctx.gamefx || !ctx.gamefx.meta.effects[name]) return null;
    const f = ctx.gamefx.spawn(name, x, y, z, { duration: Infinity, fadeIn: this.G.qaStill ? 0 : 0.6, ...o }); this.fx.push(f); return f;
  }
  hhfx(ctx, area) {
    if (this.qs().get('hhfx') === '0') return;
    const near = [[ctx.player.x, ctx.player.z], ...(ctx.actors && ctx.actors.list ? ctx.actors.list.map((a) => [a.x, a.z]) : []), ...(SPAWNS[area] || []).map((sp) => sp.pos)];
    const dark = defiant(this.G.S);
    for (const [name, [x, z], dy] of HH_FX[area] || []) {
      if (dark && area === 'helheim' && /pool_window|hel_light/.test(name)) continue;
      if (near.some(([ax, az]) => Math.hypot(ax - x, az - z) < 1.5)) continue;
      this.fxAt(ctx, name, x, ctx.heightAt(x, z) + dy, z);
    }
  }
  qaPreset() {
    const v = this.qs().get('hhq'), S = this.G.S; if (!v || this.qaDone === v) return;
    this.qaDone = v; S.quests = S.quests || {}; const f = flags(S), Q = S.quests;
    Object.assign(f, { hg_petition: 1, hg_line: 'help', hg_boat: 1, hg_shade: 1, hh_gate_open: 1 });
    Q.hh_gate = v === 'open' ? 2 : 3;
    if (v === 'kind') { f.hel = 'kind'; Q.hh_bridge = 1; }
    if (v === 'ledger') { f.hel = 'kind'; Q.hh_bridge = 3; Q.hh_stories = 1; Q.hh_ledger = 1; }
    if (v === 'ossuary' || v === 'fallen') { f.hel = 'kind'; Q.hh_bridge = 3; Q.hh_ledger = 3; f.hh_cleared = 1; Q.ossuary = 1; S.inv = { ...(S.inv || {}), ossuary_key: 1 }; }
    if (v === 'fallen') { f.fallen_ally = 'dagna'; Q.hh_home = 1; }
    if (v === 'defiant') { f.hel = 'defiant'; Q.hh_take = 1; }
    if (v === 'done') { f.hel = 'kind'; Q.hh_ledger = 3; Q.ossuary = 3; Object.assign(f, { hh_vesperin: 1, hh_boss: 1, hh_mordrath: 1, hh_resolved: 1, os_rhythm: 1 }); }
  }
  attach(ctx, area) {
    this.detach(); this.ctx = ctx; this.area = area;
    if (area === 'bifrost') { this.qaPreset(); this.gate.atBifrost(ctx); this.bifrost(); return; }
    if (!AREAS_HEL[area]) { this.betweenRealms(); return; }
    this.qaPreset(); this.hhfx(ctx, area);
    if (area === 'helheim') this.town(ctx);
    if (area === 'hh_shore') this.shore();
    if (area === 'hh_archive') this.archive();
    if (area === 'ossuary' || area === 'ossuary2') this.ossuary(area);
  }
  detach() { for (const f of this.fx) if (f) f.dur = f.t + 0.2; this.fx = []; this.spots = []; this.cb = {}; this.sp = {}; this.bosses.reset(); this.ctx = null; this.area = null; }
  betweenRealms() {
    const G = this.G, f = F(G.S); if (!f.hh_resolved || f.hh_veyra_between) return;
    flags(G.S).hh_veyra_between = 1;
    G.toast && G.toast(f.rift_breaker ? 'A cold voice: "Then we use what\'s left."' : 'A cold voice: "You freed my soldiers. I\'ll climb without them."', 4.0);
  }
  town(ctx) {
    const G = this.G, S = G.S, f = flags(S);
    this.gate.atHub(ctx);
    if (!f.hh_arrived) { f.hh_arrived = 1; G.toast('Corvin: "Living? Lovely. Mind your lamp, love."', 3.2); }
    if (q(S, 'hh_gate') === 1 && f.hg_boat && !f.hg_shade) this.foe({ id: 'gate_shade', role: 'gate_shade', pos: [0.0, 5.6] }, () => { f.hg_shade = 1; G.setQuest('hh_gate', 2); mark(G); });
    BRIDGE.forEach(([x, z], i) => this.spot({ id: 'lb' + i, pos: [x, z], r: 1.4, label: 'a dark bridge lantern (E / A)', show: () => q(S, 'hh_bridge') === 1 && !((f.lb_on || {})[i]), act: () => this.lightLantern(i) }));
    this.spot({ id: 'hel_hall', pos: HALL, r: 1.8, label: "Hel's Hall (E / A)", show: () => q(S, 'hh_gate') >= 2, act: () => G.openDialogue({ id: 'hel', name: 'Hel' }, TALK.hel(S)) });
    this.pageSpot('helheim');
    SOUL_LAMPS.forEach(([x, z], i) => {
      const k = 'pt_l' + (i + 1);
      this.spot({ id: k, pos: [x, z], r: 1.6, label: 'a soul-lamp (E / A: snuff it)', show: () => q(S, 'hh_take') === 1 && !(S.found || {})[k], act: () => {
        if (this.cb[k + 'a'] || this.cb[k + 'b']) return;
        let left = 2; const dead = () => { if (--left > 0) return; this.find(k); mark(G); };
        this.foe({ id: k + 'a', role: 'gloam_knight', pos: [x - 1.4, z - 1.6] }, dead); this.foe({ id: k + 'b', role: 'gloam_knight', pos: [x + 1.4, z - 1.6] }, dead);
      } });
    });
    this.spot({ id: 'pt_odric', pos: [0.0, -3.0], r: 2.0, label: 'Ser Odric Gravemantle (E / A)', show: () => q(S, 'hh_take') === 1 && found(S, 'pt_l1', 'pt_l2', 'pt_l3') >= 3 && !f.pt_odric && !this.cb.odric, act: () => this.odric() });
    this.spot({ id: 'hh_drag', pos: [0.0, 4.6], r: 1.8, label: () => (defiant(S) ? 'drag them back (E / A)' : 'walk them home (E / A)'), show: () => q(S, 'hh_home') === 2, act: () => this.home() });
  }
  pageSpot(area) {
    const G = this.G, S = G.S;
    for (const [k, [a, pos]] of Object.entries(PAGES)) {
      if (a !== area) continue;
      this.spot({ id: k, pos, r: 1.5, label: 'a torn Ledger page (E / A)', show: () => q(S, 'hh_ledger') === 1 && !(S.found || {})[k], act: () => this.look(k, 'A Ledger page', ['(A torn page of names, a red claw-mark across it.)'], () => {
        this.find(k); G.give('ledger_page', 1); if (found(S, 'lg_p1', 'lg_p2', 'lg_p3') >= 3) G.setQuest('hh_ledger', 2); mark(G); }) });
    }
  }
  lightLantern(i) {
    const G = this.G, f = flags(G.S);
    this.look('lb' + i, 'The Lantern Bridge', ['(Cold fire catches, blue and steady.)'], () => {
      f.lb_on = { ...(f.lb_on || {}), [i]: 1 }; f.lb_lit = Object.keys(f.lb_on).length;
      if (f.lb_lit >= 3) G.setQuest('hh_bridge', 2); mark(G);
    });
  }
  storyCheck() { const G = this.G, S = G.S; if (found(S, 'gs_baker', 'gs_sailor', 'gs_child') >= 3 && q(S, 'hh_stories') === 1) G.setQuest('hh_stories', 2); mark(G); }
  odric() {
    const G = this.G, S = G.S;
    this.look('pt_odric', 'Ser Odric Gravemantle', ['"Three lamps out. Draw, then."'], () => {
      this.foe({ id: 'odric', role: 'odric', pos: [0.0, -4.4], trial: true }, () => {}, () => {
        flags(S).pt_odric = 1; G.give('ossuary_key', 1); G.setQuest('hh_take', 2);
        this.look('pt_yield', 'Ser Odric Gravemantle', ['"Hel will remember this. So will I. The stair is under the Archive."']); mark(G);
      });
    });
  }
  home() {
    const G = this.G, S = G.S, f = flags(S), ally = fallenAlly(S) || 'halla', pale = defiant(S);
    this.look('hh_home', 'The Lantern Bridge', pale ? ['(You drag them across. The lanterns stay dark.)'] : ['(You walk ahead, and do not look back.)', '"...Hello. I\'m home."'], () => {
      f.companions = { ...(f.companions || {}), [ally]: 1 }; S.unlocks = { ...(S.unlocks || {}), gravelight: 1 };
      if (pale) f.bh_pale = 1;   // cosmetic only
      G.setQuest('hh_home', 3); G.factions.add(pale ? 'gate' : 'embassy', pale ? MERIT.hh_home_d : MERIT.hh_home, pale ? 'hh_home_d' : 'hh_home'); mark(G);
    });
  }
  shore() {
    const G = this.G, S = G.S, f = flags(S);
    this.pageSpot('hh_shore');
    this.spot({ id: 'gs_child', pos: JETTY, r: 1.8, label: 'float a lantern with Hollin (E / A)', show: () => !!f.gs_walk && !(S.found || {}).gs_child, act: () => { this.find('gs_child'); this.storyCheck(); } });
    this.spot({ id: 'ik_button', pos: [1.2, JETTY[1]], r: 1.6, label: 'leave a button (E / A)', show: () => q(S, 'hh_raven') === 1 && !!(S.inv || {}).button && (f.ik_lastDay ?? -1) < (S.day || 0), act: () => {
      S.inv.button -= 1; f.ik_lastDay = S.day || 0; f.ik_nights = (f.ik_nights || 0) + 1; if (f.ik_nights >= 3) G.setQuest('hh_raven', 2); mark(G); } });
    this.spot({ id: 'bh_shore', pos: [2.4, 0.2], r: 1.8, label: 'your friend (E / A)', show: () => q(S, 'hh_home') === 1 && !!f.bh_name, act: () => { G.setQuest('hh_home', 2); mark(G); } });
    for (const k of ['float', 'row']) this.spot({ id: 'lb_' + k, pos: k === 'float' ? [-1.2, JETTY[1]] : [0, JETTY[1] - 1.4], r: 1.6, label: k === 'float' ? 'float a lantern (E / A)' : 'row the lake (E / A)', show: () => q(S, 'lanternboat') === 1 && !(S.lboat || {})[k], act: () => { S.lboat = { ...(S.lboat || {}), [k]: 1 }; lboatCheck(G); } });
  }
  archive() {
    const G = this.G, S = G.S;
    this.pageSpot('hh_archive');
    this.spot({ id: 'gs_ship', pos: SHIP, r: 1.5, label: 'a model ship (E / A)', show: () => q(S, 'hh_stories') === 1 && !(S.found || {}).gs_ship, act: () => { this.find('gs_ship'); mark(G); } });
    this.spot({ id: 'ledger', pos: LEDGER, r: 1.6, label: 'the Ledger of Names (E / A)', act: () => this.look('ledger', 'The Ledger of Names', ['(Eleven million names.)']) });
    this.spot({ id: 'os_door', pos: OS_DOOR, r: 1.8, label: 'the Ossuary door (E / A)', act: () => this.door() });
  }
  door() {
    const G = this.G, S = G.S, inv = S.inv || {};
    const how = kind(S) && q(S, 'hh_ledger') >= 3 && inv.ossuary_key ? 'key' : defiant(S) && inv.ossuary_key ? 'force' : this.qs().has('hhq') ? 'key' : null;
    if (!how) return this.look('os_shut', 'The Ossuary door', ["Hel's key, or force. Neither is yours yet."]);
    this.look('os_open', 'The Ossuary door', [how === 'key' ? "(Hel's key turns.)" : '(You force the door.)'], () => {
      if (how === 'force' && q(S, 'hh_take') === 2) { G.setQuest('hh_take', 3); G.factions.add('gate', MERIT.paletoll, 'paletoll'); gold(G, 120); }
      if (!q(S, 'ossuary')) G.setQuest('ossuary', 1);
      G.save && G.save(); G.loadArea('ossuary', 'from_archive');
    });
  }
  ossuary(area) {
    const G = this.G, S = G.S, f = flags(S);
    for (const [k, [a, pos]] of Object.entries(CAGES)) if (a === area) this.spot({ id: k, pos, r: 1.6, label: 'a name-cage (E / A)', show: () => !(S.found || {})[k] && (k !== 'os_n2' || !!f.hh_vesperin), act: () => { this.find(k); mark(G); } });
    for (const [k, [a, pos]] of Object.entries(SGL)) if (a === area) this.spot({ id: k, pos, r: 1.5, label: 'soul-glass (E / A)', show: () => !(S.found || {})[k], act: () => { this.find(k); G.give('soul_glass', 1); mark(G); } });
    if (area === 'ossuary') HEARTS.forEach(([x, z], i) => this.spot({ id: 'heart' + i, pos: [x, z], r: 1.3, label: 'roll a glass heart (E / A)', show: () => !((f.os_hearts || {})[i]), act: () => { f.os_hearts = { ...(f.os_hearts || {}), [i]: 1 }; mark(G); } }));
    if (area === 'ossuary2') {
      this.spot({ id: 'bh_name', pos: NAME_CAGE, r: 1.8, label: 'a violet cage (E / A)', show: () => !f.bh_name, act: () => { if (fallenAlly(S)) f.bh_name = 1; mark(G); } });
      this.spot({ id: 'rhythm', pos: [0.0, -5.0], r: 1.8, label: 'the rhythm door (E / A)', show: () => !f.os_rhythm, act: () => { f.os_rhythm = 1; mark(G); } });
      this.spot({ id: 'o9_mote', pos: [0.0, -40.0], r: 6.0, label: 'strike the name-mote (E / A)', show: () => this.bosses.moteSeen(), act: () => this.bosses.strikeMote() });
    }
  }
  osTick() {
    const G = this.G, S = G.S, f = F(S), p = this.ctx.player, sp = this.sp;
    if (G.dlg || G.busy || !G.combat) return;
    if (this.area === 'ossuary') {
      if (!sp.o5 && p.z < -50.0 && !f.hh_vesperin && !this.cb.vesperin) { sp.o5 = 1; this.bosses.start('vesperin'); }
      if (p.z < -62.0 && !f.hh_vesperin) this.moveTo(0, -61.0);
    }
    if (this.area === 'ossuary2') {
      if (p.z < -7.0 && !f.os_rhythm) this.moveTo(0, -5.6);
      if (!sp.o9 && p.z < -36.0 && !f.hh_boss && !this.cb.mordrath) { sp.o9 = 1; this.bosses.start('mordrath'); }
    }
  }
  bifrost() {
    const G = this.G, S = G.S, ARCH = [HH_ARCH.pos[0], HH_ARCH.pos[1] + 1.6];
    const offer = () => live() && ((G.factions ? G.factions.rank('embassy') : 0) >= HEL_GATE[1] || this.qs().has('hhq'));
    this.spot({ id: 'hg_desk', pos: [ARCH[0] - 1.8, ARCH[1]], r: 1.6, label: 'petition Hel (E / A)', show: () => offer() && !q(S, 'hh_gate'), act: () => this.petition() });
    this.spot({ id: 'hg_boat', pos: ARCH, r: 1.6, label: "the lantern-boat's answer (E / A)", show: () => q(S, 'hh_gate') === 1 && !!F(S).hg_petition && !F(S).hg_boat, act: () => this.boat() });
  }
  petition() {
    this.G.openDialogue({ id: 'hg_desk', name: 'A petition to Hel' }, { pages: ['"Write what you\'re coming for. She reads them all."'], choice: { id: 'hg_line', options: [
      ['I come to help', 'help'], ['I come for someone', 'someone'], ['I come because I must', 'must']].map(([label, v]) => ({ label, pick: () => ({ pages: ['(The paper boat drifts through the seal.)'], then: (G2) => { const f = flags(G2.S); f.hg_petition = 1; f.hg_line = v; f.hg_day = G2.S.day || 0; G2.setQuest('hh_gate', 1); mark(G2); } }) })) } });
  }
  boat() {
    const G = this.G, S = G.S, f = flags(S);
    if ((S.day || 0) <= (f.hg_day ?? -1) && !this.qs().has('hhq') && !f.hg_rift) return this.look('hg_wait', 'The arch', ['(No boat yet. Come back tomorrow.)']);
    this.look('hg_boat', 'The arch', ['(A lantern-boat brings a lamp that burns only for the living.)'], () => { f.hg_boat = 1; G.give('living_lamp', 1); this.gate.reopen(); mark(G); });
  }
  update(dt) {
    if (!this.ctx) return;
    this.bosses.update(dt);
    if (this.area === 'ossuary' || this.area === 'ossuary2') this.osTick();
  }
  qaTalk(id) { const e = TALK[id](this.G.S); if (e && e.then) e.then(this.G); return { pages: e ? e.pages.length : 0, choice: e && e.choice ? e.choice.options.map((o) => o.label) : null }; }
  qaPick(label, id = 'hel') { const e = TALK[id](this.G.S), o = e.choice && e.choice.options.find((x) => x.label === label); if (!o) return -1; const nx = o.pick(this.G); if (nx && nx.then) nx.then(this.G); return nx ? nx.pages.length : 0; }
  qaSpot(id) { const sp = this.spots.find((x) => x.id === id); if (!sp) return false; sp.act(); return true; }
  qaKill(id) { const fn = this.cb[id]; if (!fn) return false; fn(); return true; }
  qaFinale(base = 5) { return finaleWaves(this.G.S, base); }
  qaEira() { return eiraBranch(this.G.S); }
  qaDefs() { return { quests: HEL_QUESTS.filter((k) => QUESTS[k]).length, marches: HEL_MARCHES, redeemableFn: typeof redeemable === 'function', shop: !!SHOPS.innghost, fx: Object.keys(HH_FX).length, bossAt: BOSS_AT, ...this.bosses.qaDefs() }; }
  qa() {
    const c = this.ctx, S = this.G.S, f = F(S), gm = c ? (c.scene.game || {}) : {};
    return { area: this.area, exits: (gm.exits || []).map((e) => e.to), portals: (gm.portals || []).map((p) => p.to), spots: this.spots.filter((x) => x.show()).map((x) => x.id), gate: this.gate.qa(), stance: helStance(S),
      realmFor: this.G.factions ? this.G.factions.realm() : null, quests: Object.fromEntries(HEL_QUESTS.map((k) => [k, q(S, k)])), pale: isPale(S),
      flags: Object.fromEntries(['hh_gate_open', 'pt_odric', 'bh_name', 'bh_pale', 'hh_vesperin', 'hh_boss', 'hh_mordrath', 'hh_resolved', 'os_rhythm'].map((k) => [k, !!f[k]])),
      actors: c ? c.actors.list.map((a) => a.id || a.role) : [], fx: this.fx.length };
  }
}

class HhGate {
  constructor(h) { this.h = h; this.G = h.G; this.fetching = false; }
  get ctx() { return this.h.ctx; }
  put(sc) { const gm = (sc.game = sc.game || {}); gm.spawns = gm.spawns || {}; if (!gm.spawns.from_helheim) gm.spawns.from_helheim = HH_ARCH.spawn.slice(); }
  atHub(ctx) {
    const G = this.G, gm = ctx.scene.game || (ctx.scene.game = {});
    gm.portals = gm.portals || [];
    if (!gm.portals.find((p) => p.to === 'bifrost')) gm.portals.push({ ...HUB_GATE, rect: HUB_GATE.rect.slice() });
    if (G.scenes && G.scenes.bifrost) { this.put(G.scenes.bifrost); return; }
    if (this.fetching || !G.scenes) return;
    this.fetching = true;
    fetch('areas/bifrost/scene.json').then((r) => r.json()).then((sc) => { if (!G.scenes.bifrost) G.scenes.bifrost = sc; this.put(G.scenes.bifrost); }).catch(() => {}).finally(() => { this.fetching = false; });
  }
  atBifrost(ctx) { this.put(ctx.scene); this.wire(ctx); }
  reopen() { if (this.ctx && this.h.area === 'bifrost') this.wire(this.ctx); }
  wire(ctx) {
    const gm = ctx.scene.game; if (!gm || !live() || !gateOpen(this.G.S, this.h.qs())) return;
    gm.sealed = (gm.sealed || []).filter((g) => g.arch !== 'helheim');
    gm.portals = gm.portals || [];
    if (!gm.portals.find((p) => p.to === 'helheim')) gm.portals.push({ fx: 'gate_helheim', to: 'helheim', spawn: 'from_bifrost', rect: HH_ARCH.rect.slice(), label: "Hel's arch" });
    (gm.spawns = gm.spawns || {}).from_helheim = gm.spawns.from_helheim || HH_ARCH.spawn.slice();
  }
  qa() { const c = this.ctx, gm = c ? (c.scene.game || {}) : {}; return { portals: (gm.portals || []).map((p) => p.to), sealed: (gm.sealed || []).map((g) => g.arch), open: gateOpen(this.G.S, this.h.qs()), live: live() }; }
}
{
  const pages0 = Crossing.prototype.pages;
  Crossing.prototype.pages = function pages(g) { const out = pages0.call(this, g); if (g && g.arch === 'helheim' && live()) out.push('An embassy desk stands beside the arch. Hel reads every petition.'); return out; };
}
