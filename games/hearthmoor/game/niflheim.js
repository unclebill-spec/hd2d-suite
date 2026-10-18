// [NIFLHEIM] Niflheim (realm-niflheim branch), built from the Hearthmoor Story script (staging story/niflheim.md; plan + status in NIFLHEIM_PROGRESS.md).
// CHUNK 1 = SKELETON: realm tables, the Bifrost ice-arch wiring (The Frost Invitation), quest data, NPC talk, Hrefna's companion data, the three bosses
// (Glacier Colossus 6x, Kael Frostfang 5.5x, Veyra 5x with 4 phases; all framed:true), rares, weather, items, Tove's stall, the Muspelheim-lock flag, the Mistmere
// spots. Nothing here changes any existing area or behaviour while NIFL_BUILT is empty: no Niflheim area is built into areas/ yet (the art pack
// /workspace/hearthmoor-staging/art/niflheim/READY.txt is not there), so the Bifrost ice arch stays sealed and AREAS_NIFL stays empty. To take an area live:
// build its spec (areas/src/<id>.json), run tools/hearthmoor/nifl_art.py, add the id to NIFL_BUILT. Quests / TALK / shops / the Bifrost look merge into the
// shared tables from here (like muspelheim.js), so shared files only carry a few marked hook lines.
// Decisions (Cozy Builder, Oct 18 2026): (1) the Muspelheim lock stays (befriending Muspelheim = Niflheim is conquer-only) but behind ONE constant, NIFL_MUSP_LOCK,
// so it is an easy change once Bill answers; (2) the mirror sigil and the frost wedges are enough: no corrupted Cinderhold shrine; (3) the rest follows the story doc.
import { TALK, ITEMS, QUESTS, MARKER_HOOKS } from './data.js';
import { REALM, MERIT, Factions } from './factions.js';
import { ENEMIES, SPAWNS } from './heroes.js';
import { XP } from './progress.js';
import { SHOPS, GOODS } from './shop.js';
import { lockRival, moodUp } from './alfheim.js';
import { allyCount } from './muspelheim.js';
import { BASES, RARE_AREAS, Rares } from './rares.js';
import { RARITY, makeItem } from './loot.js';
import { KINDS as WX_KINDS, WX_HOOK } from './weather.js';
import { COMP, unlock as compUnlock, swap as compSwap, active as compActive } from './svartalfheim_companions.js';
import { WAYS } from './ravenhold.js';
import { KIT as FOLLOW_KIT } from './svartalfheim_follow.js';
import { Crossing } from './bifrost.js';

// ---- THE ONE FLAG (Cozy Builder, Oct 18 2026; Bill has not answered). true = the story doc's lock: a Muspelheim friend (muspelheim.js calls lockRival(S, 'niflheim'))
// gets Niflheim conquer-only (no befriend, no Hrefna, no redemption path, defeat ending only). false = the lock is ignored everywhere in this module: lockedBy() is always false,
// so the befriend chain, Hrefna and Ending A open for everybody (only the 4-ally cap still greys the option). Nothing else needs to change.
export // STAND-INS: until the art pack lands (READY.txt) the Niflheim foe / boss roles have no sheet; every foe wears the stock `wraith` role (its ENEMIES entry, hp, attacks stay its own).
// Flip to true when nifl_art.py installs the sheets (the roles then exist in every built area).
const NIFL_ROLES_READY = false;
const NIFL_MUSP_LOCK = true;

// story 2.1. The Frozen Spire is 10 rooms: two areas like clockdeep / caldera (decision in NIFLHEIM_PROGRESS.md): frozenspire F1-F5, frozenspire2 F6-F10; the Crown of Ice is the finale arena.
export const NIFL_PLANNED = {
  niflheim: 'Mistmere', nf_home: 'The Quiet Shore', iceglow: 'The Glowpool Caverns', frozenspire: 'The Frozen Spire', frozenspire2: 'The Frozen Spire: the Aerie', frozen_rift: 'The Crown of Ice',
};
export const NIFL_BUILT = [];   // ids of areas whose built output is in areas/<id>/ (the live list; empty until the art pack is READY and an area is built)
export const AREAS_NIFL = Object.fromEntries(NIFL_BUILT.map((a) => [a, `areas/${a}/`]));        // id -> 'areas/<id>/' (merged into game.js's area path map)
export const AREA_NAMES_NIFL = Object.fromEntries(NIFL_BUILT.map((a) => [a, NIFL_PLANNED[a]]));   // id -> display name (merged into game.js's AREA_NAME)
export const NIFL_AREAS = Object.keys(NIFL_PLANNED);

const flags = (S) => (S.flags = S.flags || {});
const F = (S) => S.flags || {};
const q = (S, k) => (S.quests || {})[k] || 0;
const ally = (S) => (flags(S).alliance = flags(S).alliance || {});
const gold = (G, n) => { G.S.gold = (G.S.gold || 0) + n; G.toast(`+${n} gold`, 1.8); G.drawBag && G.drawBag(); };
const met = (k) => (G) => { G.S.met = { ...(G.S.met || {}), [k]: 1 }; };
const found = (S, ...ks) => ks.filter((k) => (S.found || {})[k]).length;
const mark = (G) => { G.refreshMarkers && G.refreshMarkers(); G.save && G.save(); };

// story 1.1 / 12: helpers. lockedBy = befriended Muspelheim (rivals.niflheim === 'locked', set by muspelheim.js) behind NIFL_MUSP_LOCK; mood = conquered Muspelheim.
export { allyCount };
export const lockedBy = (S) => NIFL_MUSP_LOCK && (F(S).rivals || {}).niflheim === 'locked';
export const mood = (S) => ((F(S).realm_mood || {}).niflheim || 0) >= 1;
const emberBorn = (S) => S.hero === 'cinderknight';
const runeReader = (S) => S.hero === 'runeguard';
export const RESOLVED = ['vh_resolved', 'alf_resolved', 'sv_resolved', 'jt_resolved', 'mp_resolved'];   // vanaheim, alfheim, svartalfheim, jotunheim, muspelheim
export const resolvedCount = (S) => RESOLVED.filter((k) => F(S)[k]).length;
export const evidenceCount = (S) => Object.values(S.evidence || {}).filter(Boolean).length;
export const redeemable = (S) => {   // story 8.2: the Ask-first ending needs befriend (so Muspelheim was NOT befriended), Eira's Lanterns done, 3 pieces of evidence, no Breaker detour
  const f = F(S);
  return (f.alliance || {}).niflheim === 'befriend' && !lockedBy(S) && (f.nf_vigil || 0) === 3 && evidenceCount(S) >= 3 && !f.rift_breaker && !f.switched_to_saver;
};
const conquer = (S) => (F(S).alliance || {}).niflheim === 'conquer';
const befriend = (S) => (F(S).alliance || {}).niflheim === 'befriend';

Object.assign(REALM, { niflheim: 'embassy', nf_home: 'embassy', iceglow: 'embassy', frozenspire: 'embassy', frozenspire2: 'embassy', frozen_rift: 'embassy' });   // befriend = Realm Favor; conquer pays 'gate' (Factions.realm wrap below)
Object.assign(MERIT, { nf_gate: 60, rimetoll: 60, spire_c: 120, nf_lanterns: 40, nf_cold: 60, nf_rival: 20, nf_hrefna: 80, nf_eira: 80, frozenspire: 120, frostvigil: 40 });   // story 3.12
{   // story 12: factions.realm() returns `gate` in the realm's areas when alliance.niflheim === "conquer"
  const realm0 = Factions.prototype.realm;
  Factions.prototype.realm = function realm() {
    if (NIFL_AREAS.includes(this.G.area) && conquer(this.G.S)) return 'gate';
    return realm0.call(this);
  };
}

// ------------------------------------------------------------------ the Bifrost ice arch (story 0, 3.1): sealed pos [6.6, -5] on Bifrost's east side
export const NF_ARCH = { rect: [5.85, -5.4, 7.35, -4.55], pos: [6.6, -5.0], spawn: [6.6, -3.6, 'down'] };
export const NF_KEY = ['flag', 'nf_open'];   // the new key kind (story 0): the arch opens when The Frost Invitation sets flags.nf_open (stage 2 -> 3 sets nf_gate_open too)
const HUB_GATE = { to: 'bifrost', spawn: 'from_niflheim', rect: [-0.9, 10.1, 0.9, 11.1], label: 'the ice arch back to Bifrost Crossing' };   // Mistmere's own arch [0, 10.6]
// open when the reveal has run, or ?nfq= (QA; ?nfq=gate keeps it shut for the quest itself). Never opens while no area is built.
export const gateOpen = (S, qs) => !!(F(S).nf_gate_open || F(S).nf_open || (qs && qs.has('nfq') && qs.get('nfq') !== 'gate'));
export const live = () => NIFL_BUILT.includes('niflheim');
export const FROST_LETTER = ['(The sealed Niflheim arch is writing in frost. Slowly, a line of blue-black rime crosses the glass.)', '"You followed the footprints. Come home with me. -V"'];

// ------------------------------------------------------------------ foes (story 8.1-8.5)
Object.assign(ENEMIES, {
  frost_spirit: { name: 'Frost spirit', scale: 1.2, hp: 70, dmg: 10, speed: 1.3, reach: 5.0, windup: 0.7, cd: 2.4, aggro: 8, r: 0.4, push: 0.3, float: true, bolt: 'bolt', element: 'ice' },   // gate foe: no melee, an ice bolt
  mist_stalker: { name: 'Mist stalker', scale: 1.5, hp: 95, dmg: 13, speed: 2.3, reach: 1.5, windup: 0.4, cd: 1.5, aggro: 7, r: 0.45, push: 0.4, element: 'ice', mistHidden: true },   // invisible in mist beyond 3 m
  ice_golem: { name: 'Ice golem', scale: 1.8, hp: 230, dmg: 19, speed: 0.8, reach: 2.1, windup: 1.0, cd: 2.4, aggro: 6, r: 0.65, push: 0.15, heavy: true, element: 'ice' },
  frost_wraith: { name: 'Frost wraith', scale: 1.4, hp: 100, dmg: 13, speed: 1.5, reach: 1.6, windup: 0.6, cd: 1.9, aggro: 7, r: 0.5, push: 0.3, float: true, element: 'ice' },
  ice_warden: { name: 'Ice Warden', hp: 90, dmg: 13, speed: 1.9, reach: 1.5, windup: 0.4, cd: 1.5, aggro: 7.5, r: 0.4, push: 0.5, elite: true, element: 'ice' },   // elite, 1x: grey-blue hooded tunic, jerkin, no plate
  brisa: { name: 'Warden-Captain Brisa Rimeheart', scale: 3, hp: 400, dmg: 17, speed: 1.3, reach: 2.6, windup: 0.6, cd: 1.8, aggro: 9, r: 0.8, push: 0.2, heavy: true, boss: true, trial: true, element: 'ice', respawn: 1e9 },   // conquer: yields at 25%; no plate
  // F5. 6x ice golem (golems are not plate): P1 slam + ice-block throw, P2 (60%) core exposed + 2 ice golems, P3 (25%) runes dim, frost spirits swarm. framed:true pulls the camera back.
  colossus: { name: 'Glacier Colossus', scale: 6, framed: true, golem: true, element: 'ice', hp: 1900, dmg: 26, speed: 0.7, reach: 5.0, windup: 1.0, cd: 2.6, aggro: 12, r: 1.9, push: 0.05, heavy: true, slam: true, boss: true,
              wave: { every: 3, r: 6.0, dmg: 20 }, minion: 'ice_golem', phases: [0.6, 0.25], glow: '#3fb8ff', respawn: 1e9 },
  // F9. 5.5x, black-iron plate (bosses only wear plate): P1 lunges + blade arcs + cold bite, P2 (60%) splits into 3 violet mist bats, P3 (25%) plate frosts white, calls 2 Ice Wardens.
  kael: { name: 'Kael Frostfang', scale: 5.5, framed: true, plate: true, element: 'ice', hp: 2000, dmg: 28, speed: 1.1, reach: 4.6, windup: 0.8, cd: 2.2, aggro: 12, r: 1.7, push: 0.05, heavy: true, boss: true,
          minion: 'ice_warden', phases: [0.6, 0.25], glow: '#e8321e', respawn: 1e9 },
  // the finale (frozen_rift). 5x (P3 grows to 6x), rime-plate, FOUR phases: P1 Mist (100-70 %) clones + lances, P2 Freeze (70-40 %) four portals, P3 Warden (40-15 %) beam + red cracks, P4 Ask (15-0 %) the choice.
  veyra: { name: 'Veyra Ashmantle, the Rift-Warden', scale: 5, framed: true, plate: true, element: 'ice', hp: 2800, dmg: 30, speed: 1.0, reach: 5.2, windup: 0.9, cd: 2.2, aggro: 14, r: 1.8, push: 0.05, heavy: true, boss: true,
           wave: { every: 3, r: 6.4, dmg: 22 }, minion: 'mist_stalker', phases: [0.7, 0.4, 0.15], glow: '#3fb8ff', legendary: true, respawn: 1e9 },
});
Object.assign(XP, { frost_spirit: 25, mist_stalker: 55, ice_golem: 85, frost_wraith: 55, ice_warden: 75, brisa: 0, colossus: 900, kael: 1000, veyra: 1400 });
// rares (story 8.4): bodies `mistalpha` (2x) and `spiritprime` (3x) must be in iceglow's boss_roles when the art lands.
Object.assign(BASES, {
  mistalpha: { name: 'Mist Stalker Alpha', scale: 2, hp: 290, dmg: 16, speed: 2.2, reach: 2.0, windup: 0.5, cd: 1.7, aggro: 8.5, r: 0.7, push: 0.2, heavy: true, minion: 'mist_stalker', xp: 175 },
  spiritprime: { name: 'Frost Spirit Prime', scale: 3, hp: 360, dmg: 18, speed: 1.2, reach: 2.8, windup: 0.8, cd: 2.2, aggro: 8, r: 0.8, push: 0.2, float: true, xp: 210 },
});
RARE_AREAS.iceglow = { bases: ['mistalpha', 'spiritprime'], spots: [[6.0, -3.0], [-2.4, 3.4]] };   // provisional: the far pool; chosen with the area build (clear of pools, actors, the start view)
const spawnRare0 = Rares.prototype.spawn;
Rares.prototype.spawn = function spawn(o = {}) {   // Mist Alpha = ghosting + quick (blinking + summoner: calls 2 stalkers), Spirit Prime = rime aura + split (shielded + summoner)
  if (!o.traits && o.base === 'mistalpha') o = { ...o, traits: ['blinking', 'summoner'] };
  if (!o.traits && o.base === 'spiritprime') o = { ...o, traits: ['shielded', 'summoner'] };
  return spawnRare0.call(this, o);
};
SPAWNS.iceglow = [   // provisional (authored with the area build): 1.4x / 1.5x foes read fully on screen, far from the start view
  { id: 'ig_stalker0', role: 'mist_stalker', pos: [5.0, -4.0] }, { id: 'ig_spirit0', role: 'frost_spirit', pos: [-3.0, 1.0], night: true },
];
// the three warm springs (story 2.6): nf_spring (Mistmere), ig_spring (the caverns), fs_spring (Spire F3); +2 s frost-slow immunity per drink, stacking to 3
export const SPRINGS = { nf_spring: 'niflheim', ig_spring: 'iceglow', fs_spring: 'frozenspire' };
WAYS.frozenspire2 = ['the Frozen Spire, the Aurora Archive', 'frozenspire2', 'from_waystone'];   // F7's waystone (the area comes with the Spire build)

// ------------------------------------------------------------------ weather (story 2.7): freezing mist 40 %, still frost 40 %, clear glow 20 %
// (named frost_mist / still_frost: the shared `mist` kind is Mossglen's morning mist and stays as it is)
WX_KINDS.frost_mist = [{ preset: 'mist', rate: 1.4 }, { preset: 'snowfall', rate: 0.2 }];   // stalkers hidden beyond 3 m; frost spells +10 %
WX_KINDS.still_frost = [{ preset: 'dust_motes', rate: 0.4 }];                                // no wind, no snow, stars; the lake freezes into walkable ice (S.found.nf_ice)
const wxHash = (n) => { let x = (Math.imul(n | 0, 0x9E3779B1) + 0x7F4A7C15) | 0; x = Math.imul(x ^ (x >>> 16), 0x85EBCA6B); x = Math.imul(x ^ (x >>> 13), 0xC2B2AE35); return ((x ^ (x >>> 16)) >>> 0) / 4294967296; };
const niflWx = (day, t) => { const r = wxHash(day * 4 + Math.floor(t * 4) + 7373); return r < 0.4 ? 'frost_mist' : r < 0.8 ? 'still_frost' : 'clear'; };
WX_HOOK.niflheim = niflWx; WX_HOOK.iceglow = niflWx; WX_HOOK.nf_home = niflWx;   // the Spire and the Crown of Ice are indoors / above the sky (no weather)

// ------------------------------------------------------------------ items + Tove's stall (story 5.5, 11; prices are first guesses)
Object.assign(ITEMS, {
  frost_letter: { name: 'Frost-letter', px: 'glowseed', about: '"You followed the footprints. Come home with me. -V" The ink is rime, and it will not melt in your hand.' },
  spire_key: { name: 'Spire Key', px: 'tonic', about: "Warden-Captain Brisa's key, forced from the Wardens. It forces the three rune-locks of the Spire mouth, no questions asked." },
  eira_lantern: { name: "Eira's lantern", px: 'glowseed', about: "Eira Ashmantle's cold-fire lantern, cold and cracked. Hrefna says it can burn again." },
  heart_ice: { name: 'Heart-ice', px: 'glowseed', about: "A lump of ice from the Spire's deep pools that is warm to the touch. Hrefna wants three for the Coldflame Lantern." },
  frostmoss_cake: { name: 'Frost-moss cake', px: 'denbiscuit', about: "Ketil's frost-moss cake, elk-sized. One a day, from the same hand, and a young elk starts to trust it." },
  warm_tea: { name: 'Warm tea', px: 'tonic', about: "Tove's tea. Clears frost slow, and stops a shiver halfway." },
  cold_lamp: { name: 'Cold-fire lamp', px: 'glowseed', about: 'A lamp with a pinch of cold fire in it. Light radius +2. It burns without heat.' },
  fur_mantle: { name: 'Fur mantle', px: 'glowseed', about: 'A grey fur mantle. Cosmetic, and very warm.' },
  kael_fang: { name: "Kael's fang", px: 'glowseed', about: 'A fang of black iron, frost-white at the root. A socket item.' },
  colossus_core: { name: 'Golem core', px: 'glowseed', about: "The Glacier Colossus's cold-fire core, dimmed. A socket item for Frostweave." },
  hoarfrost_crown: { name: 'Hoarfrost Crown', px: 'glowseed', about: "Veyra's crown of rime, cold now. A trophy. Mistmere will not forget who took it." },
});
Object.assign(GOODS, {
  warm_tea: { name: 'Warm tea', about: 'Clears frost slow. Smoky-sweet, nothing like moonpetal.', price: 14 },
  cold_lamp: { name: 'Cold-fire lamp', about: 'Burns without heat. Light radius +2.', price: 60 },
  fur_mantle: { name: 'Fur mantle', about: 'Cosmetic, and warm.', price: 90 },
});
SHOPS.nf_trader = { name: "Tove's Fish-Stall", keeper: 'Tove Lanternwright', goods: ['warm_tea', 'cold_lamp', 'fur_mantle', 'tonic'], gear: { n: 3, rar: [0, 1, 1] }, sellMul: 1 };   // +25 % in Hushed Mistmere (flags.nf_hushed, with the build)
// the Coldflame Lantern (story 9.1): Eira's lantern relit, a legendary staff (ice-bolt slow + freeze 1.5 s, charged frost nova, reveals clones / stalkers). Granted when nf_staff completes.
export function COLDFLAME(S) {
  const it = makeItem(Math.max(10, S.lv || 1), 4, 'weapon'), k = RARITY[4].mul * (1 + (it.lv - 1) * 0.06);
  it.name = 'Coldflame Lantern'; it.fixed = true; it.unique = 'coldflame_lantern'; it.crafted = true;
  it.mods = { meleeMul: +(0.02 * k).toFixed(3), spellMul: +(0.08 * k).toFixed(3), crit: +(0.005 * k).toFixed(3) };
  it.gems = [null, null];
  it.about = "Eira's cold-fire lantern relit on a pale-wood pole: a neon-blue flame in rime-glass, runes up the shaft. Bolts slow and freeze (no burn). It reveals illusion clones and mist stalkers.";
  return it;
}
export const HI = [['hi_1', 'frozenspire', [0, 0]], ['hi_2', 'frozenspire', [0, 0]], ['hi_3', 'frozenspire2', [0, 0]]];   // heart-ice spots (F4, F6, F8): positions come with the Spire build

// ------------------------------------------------------------------ quests (story 3.1-3.10; 3 = done)
export const COLD = ['cm_table', 'cm_runes', 'cm_lantern'];
export function cold(S) {   // 4.3: three clues; a Rune-reader's runes read themselves (free)
  const f = F(S), read = COLD.filter((k) => f[k]).length, free = runeReader(S) && !f.cm_runes ? 1 : 0, n = Math.min(3, read + free);
  return { read, free, n, done: n >= 3 };
}
Object.assign(QUESTS, {
  nf_gate: { title: 'The Frost Invitation', giver: 'Gatewright Halvard', story: true, steps: {
    1: (S) => { const f = F(S); return !f.ng_read ? 'The Niflheim arch is writing in frost. Read it.' : !f.ng_halvard ? 'Show Halvard the frost-letter.' : 'Step through the ice, if you dare.'; },
    2: 'Walk to the Quiet Shore. Someone is waiting.',
    3: 'You have met Veyra Ashmantle. Niflheim is open.',
  } },
  nf_lanterns: { title: 'The Lanterns of Mistmere', giver: 'Frost-Speaker Gudrun Hoarwick', story: true, steps: {
    1: (S) => { const n = found(S, 'nl_p0', 'nl_p1', 'nl_p2'); return n < 3 ? `Relight the lantern posts with cold fire. ${n}/3` : 'Tell the Frost-Speaker.'; },
    2: "Sit by the Frost-Speaker's hearth.",
    3: 'Mistmere has lit its lanterns for you.',
  } },
  nf_cold: { title: 'The Cold Mark', giver: 'Frost-Speaker Gudrun Hoarwick', story: true, steps: {
    1: (S) => `Lay out the evidence from every realm you cleared. ${cold(S).n}/3`,
    2: 'Tell the Frost-Speaker what it shows.',
    3: "The Cold Mark is Veyra's. Mistmere knew, and was ashamed.",
  } },
  nf_hrefna: { title: "Hrefna's Thaw", giver: 'Hrefna Frostveil', story: true, steps: {
    1: (S) => `Win back Hrefna's trust. ${found(S, 'ht_tea', 'ht_glove', 'ht_rune')}/3`,
    2: 'Walk Hrefna to the Spire mouth.',
    3: 'Hrefna walks with you now.',
  } },
  nf_eira: { title: "Eira's Lanterns", giver: 'Hrefna Frostveil', story: true, steps: {
    1: (S) => `Gather what Eira left behind. ${found(S, 'el_lantern', 'el_song', 'el_word')}/3`,
    2: "Hang Eira's lantern at her grave on Vigil Night.",
    3: "Eira's lantern burns again. Veyra will hear of it.",
  } },
  nf_take: { title: 'The Rime Toll', giver: 'Gatewright Halvard', story: true, steps: {
    1: (S) => { const n = found(S, 'rt_l1', 'rt_l2', 'rt_l3'); return n < 3 ? `Put out the warding lanterns. ${n}/3` : (F(S).rt_captain ? 'Take the Spire Key.' : 'Beat Warden-Captain Brisa Rimeheart.'); },
    2: 'Open the Spire.',
    3: "The Spire Key is yours. Mistmere's lights are dark.",
  } },
  frozenspire: { title: 'The Frozen Spire', giver: 'Frost-Speaker Gudrun Hoarwick', story: true, steps: {
    1: (S) => { const n = found(S, 'fs_c1', 'fs_c2', 'fs_c3'); return n < 3 ? `Break the three freeze-cores that hold the portals shut. ${n}/3` : 'Face Kael Frostfang at the Aerie.'; },
    2: (S) => (conquer(S) ? 'Climb to the Crown of Ice.' : 'Tell Gudrun the Spire is open.'),
    3: 'The way to the Rift is open.',
  } },
  nf_staff: { title: 'The Coldflame Lantern', giver: 'Hrefna Frostveil', ripple: true, steps: {
    1: (S) => `Bring 3 heart-ice from the Spire's deep pools. ${found(S, 'hi_1', 'hi_2', 'hi_3')}/3`,
    2: "Watch Hrefna rekindle Eira's lantern.", 3: 'The Coldflame Lantern is yours.' } },
  nf_elk: { title: 'The Elk of the Fen', giver: 'Ketil Icehook', ripple: true, steps: {
    1: (S) => `Win a young frost elk's trust: a frost-moss cake a day, three days. ${Math.min(3, F(S).ne_cakes || 0)}/3`,
    2: 'Ride one lap of the lake. (Ketil is still fitting the saddle: the elk mount arrives with the mounts.)', 3: 'Your elk. Her name is Hoarlight.' } },
  frostvigil: { title: 'The Frost Vigil', giver: 'Frost-Speaker Gudrun Hoarwick', bounty: true, steps: {
    1: (S) => { const g = S.vigil || {}; return `Light ${g.light || 0}/1, walk ${g.walk ? 1 : 0}/1, sing ${g.sing ? 1 : 0}/1.`; },
    2: 'Float your lantern on the lake.', 3: 'The lake is quiet. So are you.' } },
});

// ------------------------------------------------------------------ companion: Hrefna Frostveil (story 5.4). COMP table + the follower kit. One active companion at a time (the shared swap).
// ice_lance = a bolt at the nearest foe (cd 8 s); mist_veil = allies are hard to target for 4 s (cd 20 s): the combat-side targeting hook comes with the Spire build, today it sets `veilT` + a violet fx.
export const HREFNA = { name: 'Hrefna Frostveil', scale: 1.0, follow: 1.8, hp: 180, skills: ['ice_lance', 'mist_veil'], aura: { mistSight: true, frostSlowImmune: true }, lines: 'hrefna',
  say: { first: 'I know this fight. I learned it from her.', stalker: "Careful. That one's breathing.", veyra: "She wasn't always cold. I'd like you to see that.", faint: '(Hrefna sits on the ice. She will be back at the waystone.)' } };
Object.assign(COMP, { hrefna: 'Hrefna Frostveil' });
Object.assign(FOLLOW_KIT, { hrefna: { role: 'hrefna', dist: 1.8, speed: 2.8, scale: HREFNA.scale, brawl: { dmg: 12, reach: 1.5, cd: 1.8, knock: 0.4 }, mend: { below: 0.3, heal: 35 }, light: '#3fb8ff',
  follow: [HREFNA.say.first, HREFNA.say.stalker, HREFNA.say.veyra] } });

// ------------------------------------------------------------------ talk (TALK is keyed by the actor id in the area spec)
const GUDRUN = 'Frost-Speaker Gudrun Hoarwick';
const closeCold = (G) => {   // The Cold Mark done (4.3): the mark is Veyra's. +20 more for a Muspelheim conqueror
  const S = G.S, f = flags(S);
  G.setQuest('nf_cold', 3); G.factions.add('embassy', MERIT.nf_cold + (mood(S) ? MERIT.nf_rival : 0), 'nf_cold'); f.nf_cleared = 1; mark(G);
};
const FROST_OPTIONS = (S) => {   // Gudrun's choice (story 5.2): the befriend option is greyed behind the lock flag or the 4-ally cap; no contract option exists here
  const lk = lockedBy(S), cap = allyCount(S) >= 4, md = mood(S), opts = [];
  if (lk || cap) opts.push({ label: lk ? '(Locked. You stand with Muspelheim.)' : '(Four realms already stand with you.)', locked: true, pick: () => ({ pages: [lk ? 'You warmed the fire-throne\'s hearth. Say what you want, and say it from the doorstep.' : 'Your friends are many. Ours are few. Another time.'] }) });
  else opts.push({ label: 'Stand with Mistmere. Let me bring her home.', pick: () => ({ pages: ['Then relight us. We have forgotten how.'],
    then: (G) => { ally(G.S).niflheim = 'befriend'; lockRival(G.S, 'muspelheim');
      if (md) { flags(G.S).nl_skip = 1; G.setQuest('nf_lanterns', 3); G.S.found = { ...(G.S.found || {}), nl_p0: 1, nl_p1: 1, nl_p2: 1 }; flags(G.S).nf_trusted = 1; G.factions.add('embassy', MERIT.nf_lanterns, 'nf_lanterns'); G.setQuest('nf_cold', 1); }
      else G.setQuest('nf_lanterns', 1);
      G.toast('Niflheim: befriended', 2.2); mark(G); } }) });
  opts.push({ label: "Midgard's. Hand over the Spire Key.", pick: () => ({ pages: ['So Midgard is cold, too. Take it. We are used to it.'],
    then: (G) => { ally(G.S).niflheim = 'conquer'; moodUp(G.S, 'muspelheim'); G.setQuest('nf_take', 1); G.toast('Niflheim: conquered', 2.2); mark(G); } }) });
  return opts;
};
Object.assign(TALK, {
  frostspeaker(S) {   // Gudrun Hoarwick: the choice (after the reveal), the Cold Mark / Lanterns / Spire turn-ins, the Vigil bounty (story 5.2, 5.3, 3.2-3.10)
    const f = F(S), al = (f.alliance || {}).niflheim, st = (k) => q(S, k);
    if (!f.veyra_revealed) return { pages: ["Don't be loud. The lake listens.", 'Someone is waiting for you on the Quiet Shore. Go and hear her.'] };
    if (!al) return { pages: [lockedBy(S) ? 'You warmed the fire-throne\'s hearth. Say what you want, and say it from the doorstep.' : mood(S) ? 'You broke the fire-throne. Then you have earned a seat.' : 'Veyra is ours, and she is not. What will you do with her, and with us?'],
                      choice: { id: 'nf_speaker', options: FROST_OPTIONS(S) } };
    if (al === 'conquer') return { pages: [st('nf_take') === 3 ? 'Take it. We are used to the cold.' : 'So Midgard is cold, too. Take it. We are used to it.'] };
    if (st('nf_lanterns') === 2) return { pages: ['Three posts, three lights. We had forgotten how a street looks lit.', 'Sit. The hearth is yours.'], then: (G) => { G.setQuest('nf_lanterns', 3); flags(G.S).nf_trusted = 1; G.factions.add('embassy', MERIT.nf_lanterns, 'nf_lanterns'); gold(G, 20); G.setQuest('nf_cold', 1); mark(G); } };
    if (st('nf_cold') === 1) return { pages: [`Gudrun's table is a map of the nine realms, with a hollow for each mark. The table, the runes, the lantern: ${cold(S).n}/3.`] };
    if (st('nf_cold') === 2) return { pages: ['Blue-black rime, grown from the inside out. One hand, in every realm.', 'We knew the mark. We said nothing. We were ashamed.', mood(S) ? 'You broke the fire-throne, and you read this. Sit.' : 'Hrefna will want to speak with you.'], then: closeCold };
    if (st('frozenspire') === 2) return { pages: ['The Spire is open. Kael is gone, and the Rift is showing through.', 'Frost is not cruelty. It is patience. Be patient with her.'], then: (G) => { G.setQuest('frozenspire', 3); G.factions.add('embassy', MERIT.frozenspire, 'frozenspire'); gold(G, 150); mark(G); } };
    if (!st('frozenspire') && st('nf_cold') >= 3 && st('nf_hrefna') >= 3) return { pages: ['Three cores hold the Rift\'s portals shut, high in the Spire. The mouth is in the Glowpool Caverns. Hrefna knows the way.'], then: (G) => { G.setQuest('frozenspire', 1); mark(G); } };
    if (!st('frostvigil') && st('nf_eira') >= 3) return { pages: ['The Frost Vigil is every seventh night. Light a lantern for someone. There is no wrong one.'], then: (G) => { G.setQuest('frostvigil', 1); mark(G); } };
    return { pages: ['Frost isn\'t cruelty. It\'s patience.'] };   // the Frostweave school (9.2) comes with its combat.js kinds, after frozenspire = 3
  },
  hrefna(S) {   // Hrefna Frostveil: the Thaw, Eira's Lanterns, the Coldflame Lantern, the locked line (story 3.4, 3.5, 3.8, 9.9)
    const f = F(S), al = (f.alliance || {}).niflheim, st = (k) => q(S, k);
    if (lockedBy(S)) return { pages: ["You warmed their hearth. I can't light yours."] };
    if (emberBorn(S) && st('nf_lanterns') === 1 && !f.nl_vouch) return { pages: ['(Hrefna looks at your hands. Then at the ember-light under your coat.)', "It's warm. It's not cruel. Fine."], then: (G) => { flags(G.S).nl_vouch = 1; mark(G); } };
    if (al === 'befriend' && st('nf_cold') >= 3 && !st('nf_hrefna')) return { pages: ['I carved a rune for her once. I never finished it.', 'Bring me tea that is warm, my mitten from the lake, and a blue rune on the sill. Then maybe I will talk.'], then: (G) => { G.setQuest('nf_hrefna', 1); mark(G); } };
    if (st('nf_hrefna') === 1 && (S.inv || {}).warm_tea && !(S.found || {}).ht_tea) return { pages: ['(She will not drink it. She holds it until it stops steaming. Then she drinks it.)'], then: (G) => { G.S.inv.warm_tea = Math.max(0, (G.S.inv.warm_tea || 0) - 1); G.S.found = { ...(G.S.found || {}), ht_tea: 1 }; G.toast('Warm tea 1/3', 2.2); hthCheck(G); } };
    if (st('nf_hrefna') === 1) return { pages: [`Tea from Tove, the mitten on the lake, the rune on the sill. ${found(S, 'ht_tea', 'ht_glove', 'ht_rune')}/3.`] };
    if (st('nf_hrefna') === 2) return { pages: ['Walk me to the Spire mouth. I will not go in first. But I will go in.'] };
    if (al === 'befriend' && st('nf_hrefna') >= 3 && !st('nf_eira')) return { pages: ['Eira left three things. Her lantern, her song, her last word. The door to her room is shut. I have the key now.'], then: (G) => { G.setQuest('nf_eira', 1); mark(G); } };
    if (st('nf_eira') === 1) return { pages: [`Her lantern, her music box, the shard-window. ${found(S, 'el_lantern', 'el_song', 'el_word')}/3.`] };
    if (al === 'befriend' && st('frozenspire') >= 2 && st('nf_eira') >= 3 && !st('nf_staff')) return { pages: ["Eira's lantern wants a heart. Three pieces of heart-ice from the Spire's deep pools."], then: (G) => { G.setQuest('nf_staff', 1); mark(G); } };
    if (st('nf_staff') === 2) return { pages: ['(Hrefna sets the three lumps of ice around the lantern, breathes once, and the flame turns from grey to blue.)', 'The Coldflame Lantern. She would have wanted you to have it.'],
      then: (G) => { G.S.inv.heart_ice = Math.max(0, (G.S.inv.heart_ice || 0) - 3); (G.S.bag = G.S.bag || []).push(COLDFLAME(G.S)); G.setQuest('nf_staff', 3); G.toast('You are given the Coldflame Lantern (check your bag)', 3.0); mark(G); } };
    return { pages: ['I know this fight. I learned it from her.'] };
  },
  veyra() { return { pages: ['(A tall, tired figure in a violet-black coat. She does not turn.)'] }; },
  eira() { return { pages: ['(A girl in a pale tunic, a lantern at her belt, only an outline of light.)'] }; },
  brisa(S) { return { pages: [conquer(S) ? 'Brisa Rimeheart. Midgard wants the Spire Key? Put out my lanterns first.' : 'Brisa Rimeheart. The lake is mine to watch.'] }; },
  nf_trader(S) {
    const first = !(S.met || {}).nf_trader, hushed = !!F(S).nf_hushed;
    const base = { pages: [first ? 'Eat. Mistmere hasn\'t had a guest in years.' : hushed ? 'Prices are what they are. The lanterns are dark, and so is my mood.' : 'Tea, a lamp, a mantle? The tea clears frost slow.'], then: (G) => { met('nf_trader')(G); G.shopUI.show('nf_trader'); } };
    if (q(S, 'nf_hrefna') === 1 && !(S.inv || {}).warm_tea && !(S.found || {}).ht_tea) return { pages: ['Hrefna? Warm tea, for Hrefna. On the house, and do not tell her it was me.'], then: (G) => { G.give('warm_tea', 1); met('nf_trader')(G); } };
    return base;
  },
  elkman(S) {   // Ketil Icehook: the frost elk (story 3.9, 5.5)
    const f = F(S), al = (f.alliance || {}).niflheim, st = q(S, 'nf_elk'), day = S.day || 0;
    if (!st && al === 'befriend' && q(S, 'nf_hrefna') >= 3) return { pages: ['She bit you? Good. Elk say hello with their teeth.', 'A frost-moss cake a day, from the same hand, three days running. Not two in one day.'], then: (G) => { G.setQuest('nf_elk', 1); G.give('frostmoss_cake', 1); flags(G.S).ne_lastDay = day; mark(G); } };
    if (st === 1 && (f.ne_lastDay ?? -1) < day && (f.ne_cakes || 0) < 3) return { pages: ['Another day, another cake. Hold it flat.'], then: (G) => { G.give('frostmoss_cake', 1); flags(G.S).ne_lastDay = day; } };
    return { pages: ['She bit you? Good. Elk say hello with their teeth.'] };
  },
  archivist() { return { pages: ['Vigdis Stillwater. The frost-witches kept their tablets in this room. Mind the ink; it is older than you.'] }; },
  nf_a() { return { pages: ['The aurora hums, if you stand still.'] }; },
  nf_b() { return { pages: [['We lit the lanterns for her anyway.', "The lake sings at night. Don't answer."][(S.day || 0) % 2]] }; },
  nf_shore() { return { pages: ['We never stopped missing her. We never said so.'] }; },
});
function hthCheck(G) {   // Hrefna's Thaw: three things in -> stage 2 (walk her to the Spire mouth)
  if (found(G.S, 'ht_tea', 'ht_glove', 'ht_rune') >= 3 && q(G.S, 'nf_hrefna') === 1) { G.setQuest('nf_hrefna', 2); G.toast('Hrefna is speaking again. Walk her to the Spire mouth.', 3.0); }
  mark(G);
}

MARKER_HOOKS.push((id, S) => {
  const f = F(S), al = f.alliance && f.alliance.niflheim;
  if (id === 'frostspeaker') {
    if (f.veyra_revealed && !al) return 'quest_mark';
    if (al === 'befriend' && (q(S, 'nf_lanterns') === 2 || q(S, 'nf_cold') === 2 || q(S, 'frozenspire') === 2 || (!q(S, 'frozenspire') && q(S, 'nf_cold') >= 3 && q(S, 'nf_hrefna') >= 3))) return 'quest_mark';
  }
  if (id === 'hrefna' && !lockedBy(S) && al === 'befriend' && ((q(S, 'nf_cold') >= 3 && !q(S, 'nf_hrefna')) || (q(S, 'nf_hrefna') >= 3 && !q(S, 'nf_eira')) || q(S, 'nf_staff') === 2 || (q(S, 'frozenspire') >= 2 && q(S, 'nf_eira') >= 3 && !q(S, 'nf_staff')))) return 'quest_mark';
  if (id === 'elkman' && al === 'befriend' && ((!q(S, 'nf_elk') && q(S, 'nf_hrefna') >= 3) || (q(S, 'nf_elk') === 1 && (f.ne_lastDay ?? -1) < (S.day || 0) && (f.ne_cakes || 0) < 3))) return 'quest_mark';
  if (id === 'brisa' && al === 'conquer' && q(S, 'nf_take') === 1) return 'quest_mark';
});

// ------------------------------------------------------------------ the module
const LANTERNS = [[-7.0, 4.0], [0.0, 5.0], [7.0, 4.0]];   // story 2.3: the three lantern posts (The Lanterns of Mistmere / the Rime Toll's warding lanterns)
const COLD_SPOTS = { cm_table: [-3.2, -7.6], cm_runes: [3.2, -7.6], cm_lantern: [0.0, -9.0] };   // Gudrun's hall terrace (hub): the Cold Mark table, the runes, Veyra's copy of Eira's lantern
const COLD_TEXT = {
  cm_table: ['(Gudrun\'s table: a map of the nine realms, a carved hollow for each. One by one, a blue-black mark lights where you have cleared a frame-up.)', '(Every mark is rime grown from the inside out, never white frost.)'],
  cm_runes: ['(The runes on the table read the marks together. They spell one hand, over and over.)'],
  cm_lantern: ["(A cold-fire lantern, a copy of the one Eira carried. It is Veyra's own. The soot on the glass is hers.)"],
};
const EH = { eh_lantern: [5.0, -2.0], eh_song: [7.0, -2.0], eh_glass: [6.0, -4.4] };   // Ashmantle House look-points (nf_home): the lantern, the music box, the shard-window
const SHORE = { reveal: [0.0, -1.0], grave: [0.0, -4.0] };
// the finale's four frozen portals (frozen_rift) and the three mist clones: positions come with the area
export const PORTALS = [[-7.0, -3.0], [7.0, -3.0], [-4.0, -8.0], [4.0, -8.0]];

export class Niflheim {
  constructor(G) { this.G = G; G.markLifts = { ...(G.markLifts || {}) };
    this.ctx = null; this.area = null; this.planned = NIFL_PLANNED; this.fx = []; this.lights = []; this.spots = []; this.cb = {}; this.pend = []; this.boss = null; this.qaDone = null; this.gate = new NfGate(this); this.wrap(); }
  qs() { return this.G.qs || new URLSearchParams(location.search); }
  wrap() {   // E / A and tap try the realm's interactables first (same chained hook as Muspelheim's)
    const G = this.G, me = this; if (!G.harbor) return;
    const p0 = G.harbor.prompt.bind(G.harbor), i0 = G.harbor.interact.bind(G.harbor), t0 = G.harbor.onTap.bind(G.harbor);
    G.harbor.prompt = (...a) => me.prompt() || p0(...a);
    G.harbor.interact = (...a) => me.interact() || i0(...a);
    G.harbor.onTap = (hit, ...a) => me.onTap(hit) || t0(hit, ...a);
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
    const e = C.spawnEnemy({ once: true, noRespawn: true, ...sp, ...(NIFL_ROLES_READY ? {} : { role: 'wraith' }) }, true); e.state = 'chase';
    const done = () => { delete this.cb[sp.id]; (yielded && sp.trial ? yielded : then)(e); };
    e.onKill = done; if (yielded) e.onYield = done; this.cb[sp.id] = done;
    return e;
  }
  moveTo(x, z) { const c = this.ctx; if (!c) return; c.player.x = x; c.player.z = z; c.player.y = c.heightAt(x, z); }
  find(k) { const S = this.G.S; S.found = { ...(S.found || {}), [k]: 1 }; this.G.save && this.G.save(); }
  fxAt(ctx, name, x, y, z, o = {}) {   // the pack's effects (nf_fx rows) once they are in an area's gamefx atlas; a missing effect is a no-op
    if (!ctx || !ctx.gamefx || !ctx.gamefx.meta.effects[name]) return null;
    const f = ctx.gamefx.spawn(name, x, y, z, { duration: Infinity, fadeIn: this.G.qaStill ? 0 : 0.6, ...o }); this.fx.push(f); return f;
  }
  dropFx(f) { if (f) f.dur = f.t + 0.2; }

  // QA preset (smoke / screenshots): ?nfq=open (gate only) | revealed | befriend | conquer | lanterns | cold | thaw | eira | done
  qaPreset() {
    const v = this.qs().get('nfq'), S = this.G.S; if (!v || this.qaDone === v) return;
    this.qaDone = v;
    const open = () => { flags(S).nf_gate_open = 1; flags(S).veyra_revealed = 1; S.quests.nf_gate = 3; };
    if (v === 'open') flags(S).nf_gate_open = 1;
    if (v === 'revealed') open();
    if (v === 'befriend' || v === 'lanterns') { open(); ally(S).niflheim = 'befriend'; S.quests.nf_lanterns = 1; }
    if (v === 'cold') { open(); ally(S).niflheim = 'befriend'; S.quests.nf_lanterns = 3; flags(S).nf_trusted = 1; S.quests.nf_cold = 1; }
    if (v === 'thaw') { open(); ally(S).niflheim = 'befriend'; S.quests.nf_lanterns = 3; S.quests.nf_cold = 3; flags(S).nf_cleared = 1; S.quests.nf_hrefna = 1; }
    if (v === 'eira') { open(); ally(S).niflheim = 'befriend'; S.quests.nf_lanterns = 3; S.quests.nf_cold = 3; flags(S).nf_cleared = 1; S.quests.nf_hrefna = 3; S.quests.nf_eira = 1; }
    if (v === 'conquer') { open(); ally(S).niflheim = 'conquer'; S.quests.nf_take = 1; }
    if (v === 'done') { open(); ally(S).niflheim = 'befriend'; S.quests.nf_lanterns = 3; S.quests.nf_cold = 3; S.quests.nf_hrefna = 3; flags(S).nf_cleared = 1; flags(S).nf_trusted = 1; }
  }
  attach(ctx, area) {
    this.detach(); this.ctx = ctx; this.area = area;
    if (area === 'bifrost') { this.qaPreset(); this.gate.atBifrost(ctx); this.bifrost(ctx); return; }
    if (!AREAS_NIFL[area]) return;
    this.qaPreset();
    if (area === 'niflheim') this.hub(ctx);
    if (area === 'nf_home') this.home(ctx);
    if (area === 'iceglow') this.cave(ctx);
  }
  detach() {
    for (const f of this.fx) if (f) f.dur = f.t + 0.2;
    for (const l of this.lights) if (l) l.kill = true;
    this.fx = []; this.lights = []; this.spots = []; this.cb = {}; this.pend = []; this.boss = null; this.revealed = false; this.hrefT = 0; this.ctx = null; this.area = null;
  }
  // ---- Mistmere: the lantern posts (befriend: relight; conquer: put out), the Cold Mark table, the paddock's elk
  hub(ctx) {
    const G = this.G, S = G.S, f = F(S), got = (k) => !!(S.found || {})[k];
    this.gate.atHub(ctx);
    LANTERNS.forEach(([x, z], i) => {
      const k = 'nl_p' + i, kc = 'rt_l' + (i + 1);
      if (got(k) && befriend(S)) this.fxAt(ctx, 'cold_flame', x, ctx.heightAt(x, z) + 1.9, z);
      this.spot({ id: 'lantern' + i, pos: [x, z], r: 1.8, label: 'a lantern post (E / A: relight)', show: () => q(S, 'nf_lanterns') === 1 && !got(k) && (!emberBorn(S) || F(S).nl_vouch), act: () => {
        this.look(k, 'The lantern post', ['(An iron lantern with a skin of ice over the cold fire. You breathe on the rune; it answers, and a ring of blue closes round the wick.)', '(The flame stands up, quiet and blue, and throws no heat.)'], () => {
          this.find(k); this.fxAt(ctx, 'cold_flame', x, ctx.heightAt(x, z) + 1.9, z); const n = found(S, 'nl_p0', 'nl_p1', 'nl_p2'); flags(S).nl_lit = n;
          if (n >= 3 && q(S, 'nf_lanterns') === 1) { G.setQuest('nf_lanterns', 2); G.toast('All three posts are lit. Sit by the Frost-Speaker\'s hearth.', 3.0); } else G.toast(`Lantern ${n}/3`, 2.0);
          mark(G);
        });
      } });
      // the Rime Toll (conquer, story 3.6): each warding lantern has 2 Ice Wardens and a frost spirit
      this.spot({ id: 'ward' + i, pos: [x, z], r: 1.8, label: 'a warding lantern (E / A: put it out)', show: () => q(S, 'nf_take') === 1 && !got(kc), act: () => {
        if (this.cb[kc + 'a'] || this.cb[kc + 'b'] || this.cb[kc + 's']) return this.look(kc + '_busy', 'The warding lantern', ['The Wardens are already on you.']);
        this.look(kc, 'The warding lantern', ['A warding lantern, banked and blue. Two Ice Wardens stand beside it, and a frost spirit drifts overhead. They look up.'], () => {
          let left = 3;
          const dead = () => { if (--left > 0) return; this.find(kc); ['a', 'b', 's'].forEach((t) => delete this.cb[kc + t]); G.toast(`Warding lantern ${i + 1} out.`, 2.4); mark(G); };
          this.foe({ id: kc + 'a', role: 'ice_warden', pos: [x - 1.6, z - 1.4] }, dead); this.foe({ id: kc + 'b', role: 'ice_warden', pos: [x + 1.6, z - 1.4] }, dead); this.foe({ id: kc + 's', role: 'frost_spirit', pos: [x, z - 2.6] }, dead);
        });
      } });
    });
    this.spot({ id: 'brisa_post', pos: [0.0, -3.4], r: 2.0, label: "Warden-Captain Brisa's post (E / A)", show: () => q(S, 'nf_take') === 1 && LANTERNS.every((_, i) => got('rt_l' + (i + 1))) && !f.rt_captain && !this.cb.brisa, act: () => this.captain() });
    for (const [k, pos] of Object.entries(COLD_SPOTS)) {
      this.spot({ id: k, pos, r: 1.7, label: { cm_table: "Gudrun's map table (E / A)", cm_runes: 'the frost runes (E / A)', cm_lantern: "Veyra's copy of Eira's lantern (E / A)" }[k], show: () => q(S, 'nf_cold') === 1 && !F(S)[k], act: () => {
        this.look(k, k === 'cm_table' ? 'The map table' : k === 'cm_runes' ? 'The frost runes' : "Eira's lantern, copied", COLD_TEXT[k].concat(k === 'cm_table' ? [`(${evidenceCount(S)} marks glow: one for each frame-up you undid.)`] : []), () => {
          flags(S)[k] = 1; if (q(S, 'nf_cold') === 1 && cold(S).done) { G.setQuest('nf_cold', 2); G.toast('The Cold Mark is plain. Tell the Frost-Speaker.', 3.0); } mark(G);
        });
      } });
    }
    this.spot({ id: 'ne_elk', pos: [9.4, -1.6], r: 1.8, label: () => (q(S, 'nf_elk') === 2 ? 'the young frost elk: name her (E / A)' : 'the young frost elk (E / A)'), show: () => q(S, 'nf_elk') >= 1 && q(S, 'nf_elk') < 3, act: () => this.elk() });
  }
  captain() {   // the Rime Toll: Brisa yields at 25 % and hands over the Spire Key
    const G = this.G, S = G.S; if (this.cb.brisa) return;
    this.look('rt_captain', 'Warden-Captain Brisa Rimeheart', ['"Three lanterns out. A small one, and a ledger of rime at my feet. Hm."', '"Show me. If you can put me on the ice, the Key is yours."'], () => {
      this.foe({ id: 'brisa', role: 'brisa', def: 'brisa', pos: [0.0, -6.0], trial: true }, () => {}, () => {
        delete this.cb.brisa; const f = flags(S); f.rt_captain = 1; G.give('spire_key', 1); G.setQuest('nf_take', 2);
        this.look('rt_key', 'Warden-Captain Brisa Rimeheart', ['(Brisa lowers her ice blades, breathing hard.) "Enough. You have the arm for it."', '"The Spire Key. It forces the rune-locks. It does not make the Spire agree."']); mark(G);
      });
    });
  }
  elk() {   // one frost-moss cake a day, three days; then she is yours (the saddle / the mount ride waits for mounts, like the lizard and the goat)
    const G = this.G, S = G.S, f = flags(S), day = S.day || 0, st = q(S, 'nf_elk');
    if (st === 2) return this.look('ne_name', 'The young frost elk', ['(She butts your hand, then your knee, then leans her whole warm weight on you.)', '"Her name is Hoarlight," Ketil says, not looking up. "I did not name her. She named herself."'], () => {
      G.setQuest('nf_elk', 3); S.mounts = { ...(S.mounts || {}), elk: 1 }; G.toast('Hoarlight is yours. (The saddle comes with the mounts.)', 3.0); mark(G);
    });
    if (!(S.inv || {}).frostmoss_cake) return this.look('ne_none', 'The young frost elk', ['(She sniffs your empty hand and looks at Ketil. Ketil shrugs. "One a day, from the same hand. Ask me for the day\'s cake.")']);
    if ((f.ne_fed ?? -1) >= day) return this.look('ne_fed', 'The young frost elk', ['(She is full of cake and suspicion. One a day, not two.)']);
    this.look('ne_feed', 'The young frost elk', ['(You hold the cake flat. She takes it with great delicacy, and then takes your sleeve as well.)'], () => {
      S.inv.frostmoss_cake = Math.max(0, (S.inv.frostmoss_cake || 0) - 1); f.ne_fed = day; f.ne_cakes = (f.ne_cakes || 0) + 1;
      if (f.ne_cakes >= 3) { G.setQuest('nf_elk', 2); G.toast('She trusts you. Visit her again.', 2.8); } else G.toast(`Frost-moss cake ${f.ne_cakes}/3`, 2.0);
      mark(G);
    });
  }
  // ---- the Quiet Shore: the reveal (6.4, stage 2 of The Frost Invitation), Eira's grave, Ashmantle House (Eira's Lanterns)
  home(ctx) {
    const G = this.G, S = G.S, got = (k) => !!(S.found || {})[k], sealed = () => lockedBy(S);
    const eira = () => q(S, 'nf_eira') === 1 && !sealed(), mine = (k) => eira() && !got(k);
    const chk = () => { if (found(S, 'el_lantern', 'el_song', 'el_word') >= 3 && q(S, 'nf_eira') === 1) { G.setQuest('nf_eira', 2); G.toast("Hang Eira's lantern at her grave.", 3.0); } mark(G); };
    this.spot({ id: 'eh_lantern', pos: EH.eh_lantern, r: 1.7, label: () => (sealed() ? 'the sealed door (E / A)' : "Eira's room: the lantern (E / A)"), show: () => sealed() || mine('el_lantern'), act: () => (sealed() ? this.sealedLook() : this.look('el_lantern', "Eira's room", ["(Hrefna opens the shut door with a small key. Eira's cold-fire lantern sits on the sill, cold and cracked.)"], () => { this.find('el_lantern'); G.give('eira_lantern', 1); G.toast("Eira's lantern 1/3", 2.2); chk(); })) });
    this.spot({ id: 'eh_song', pos: EH.eh_song, r: 1.7, label: 'the music box (E / A)', show: () => mine('el_song'), act: () => this.look('el_song', 'The music box', ['(A music box with a broken comb. Three teeth are bent. You press them straight, one, two, three, and the little tune plays: slow, bright, and a note short of finished.)', '(You hum the missing note. It fits.)'], () => { this.find('el_song'); G.toast("Eira's song 2/3", 2.2); chk(); }) });
    this.spot({ id: 'eh_glass', pos: EH.eh_glass, r: 1.7, label: 'the shard-window (E / A)', show: () => mine('el_word'), act: () => this.look('el_word', 'The shard-window', ['(You hold the shard-window up to the aurora. A silhouette of a girl in a pale tunic, a lantern at her belt, steps into the light.)', '"Veyra. Ask first."', '(Hrefna, quietly:) "She said it to the whole realm. Only Veyra heard it and decided it was an order."'], () => { this.find('el_word'); G.toast("Eira's last word 3/3", 2.2); chk(); }) });
    this.spot({ id: 'grave', pos: [SHORE.grave[0], SHORE.grave[1] + 1.4], r: 2.0, label: () => (q(S, 'nf_eira') === 2 ? "Eira's grave: hang the lantern (E / A)" : "Eira's grave (E / A)"), show: () => true, act: () => this.grave() });
  }
  sealedLook() { this.look('nf_sealed', 'Sealed in ice', ["(Ice has grown over the door, the music box and the shard-window, blue-black from the inside. Nothing here can be touched.)", 'Hrefna, at the door: "You warmed their hearth. I can\'t light yours."']); }
  grave() {
    const G = this.G, S = G.S, f = flags(S);
    if (lockedBy(S)) return this.sealedLook();
    if (q(S, 'nf_eira') === 2) return this.look('nf_vigil', "Eira's grave", ['(Hrefna and Gudrun hang Eira\'s lantern. The cold fire lights blue. Far off on the ice cliffs, a silhouette is watching.)', '"We never stopped missing her," Gudrun says. "We never said so to you."'], () => {
      G.setQuest('nf_eira', 3); f.nf_vigil = 3; S.unlocks = { ...(S.unlocks || {}), mistwalker: 1 }; G.factions.add('embassy', MERIT.nf_eira, 'nf_eira'); mark(G);
    });
    this.look('nf_grave', "Eira's grave", ['(A standing stone of glowing runes, violet shrine-lamps, a bare patch where a lantern should hang.)']);
  }
  // the reveal (story 6.4): a tick in nf_home once nf_gate is at stage 2 and you walk onto the shore
  revealTick() {
    const G = this.G, c = this.ctx, S = G.S, f = flags(S);
    if (this.area !== 'nf_home' || G.dlg || G.busy || this.revealed || q(S, 'nf_gate') !== 2 || f.veyra_revealed || c.player.z > SHORE.reveal[1] + 2.0) return;
    this.revealed = true; this.reveal();
  }
  reveal() {
    const G = this.G, S = G.S, f = flags(S), eb = emberBorn(S), rr = runeReader(S);
    const pages = ['(Veyra stands at the grave, her back turned. Kael waits in the dark, red-eyed.)', '"You walked all the way here. Most people stop at the first lie."', '"The Rift cracked. Fire blamed ice. Asgard took fire\'s side. We were cut off."', '"My sister held the crack closed with her hands. They called it an accident."',
      ...(eb ? ['"Ember-blood. You smell like the ones who left us."'] : []), ...(rr ? ['(The grave\'s runes spell, plainly: ASK FIRST.)'] : []), '"Every frame was mine. I wanted to see who would look."', '"Join me. The Rift can be remade. Or stay with them, and watch them forget you."'];
    this.G.openDialogue({ id: 'veyra', name: 'Veyra Ashmantle' }, { pages, choice: { id: 'nf_reveal', options: [
      { label: '(Join Veyra. That road is not open yet.)', locked: true, pick: () => ({ pages: ['"Not yet," she says, and almost smiles. "Ask me again when I am ready to be asked."'] }) },   // Rift-Breaker: story 13 (a later stub)
      { label: 'Refuse. The Rift is not yours to remake.', pick: () => ({ pages: ['"Then run," Veyra says, gently. Kael steps out of the dark.', '(You run. The ice arch is behind you, and the cold laughs at your heels.)'], then: (G) => this.revealDone(G) }) },
    ] } });
  }
  revealDone(G) {   // sets nf_gate_open + veyra_revealed (stage 2 -> 3); +60 Rift Marks, 50 gold
    const f = flags(G.S); f.veyra_revealed = 1; f.nf_gate_open = 1; f.nf_open = 1; G.setQuest('nf_gate', 3); G.factions.add('gate', MERIT.nf_gate, 'nf_gate'); gold(G, 50); this.gate.reopen(); mark(G);
    G.save && G.save(); G.loadArea('niflheim', 'from_shore');
  }
  // ---- the Glowpool Caverns: Hrefna's mitten (the mist-stalker's nest), the Spire mouth (rune-locks; the Spire areas come with their builds)
  cave(ctx) {
    const G = this.G, S = G.S, got = (k) => !!(S.found || {})[k];
    this.spot({ id: 'ht_glove', pos: [6.0, -3.6], r: 1.8, label: 'a stalker\'s nest (E / A)', show: () => q(S, 'nf_hrefna') === 1 && !got('ht_glove'), act: () => this.look('ht_glove', "The stalker's nest", ["(A nest of pale fur and torn mitten wool. Hrefna's blue mitten is at the bottom, stiff with frost.)"], () => { this.find('ht_glove'); G.toast("Hrefna's mitten 2/3", 2.2); hthCheck(G); }) });
    this.spot({ id: 'spire_mouth', pos: [0, -6.0], r: 2.0, label: 'the Spire mouth (E / A)', show: () => true, act: () => this.mouth() });
  }
  mouth() {   // three rune-locks: befriend: Hrefna's runes open them (also ends Hrefna's Thaw); conquer: the Spire Key forces them. The Frozen Spire areas come with the Spire build.
    const G = this.G, S = G.S, f = F(S);
    if (q(S, 'nf_hrefna') === 2) return this.look('ht_walk', 'The Spire mouth', ['(Hrefna lays her palm on the first rune-lock and the cold light climbs her arm. "I will not go in first," she says. "But I will go in."', '(She falls in beside you.)'], () => {
      G.setQuest('nf_hrefna', 3); G.factions.add('embassy', MERIT.nf_hrefna, 'nf_hrefna'); compUnlock(G, 'hrefna'); compSwap(G, 'hrefna'); mark(G);
    });
    const how = befriend(S) && q(S, 'nf_hrefna') >= 3 ? 'runes' : conquer(S) && (S.inv || {}).spire_key ? 'key' : null;
    if (!how) return this.look('sm_shut', 'The Spire mouth', ['(A six-metre door of ice with three rune-locks across it, blue and slow.)', "None of them will give for you yet. Hrefna's runes or the Spire Key: one of them has to be yours."]);
    this.look('sm_open', 'The Spire mouth', [how === 'runes' ? "(Hrefna's runes thaw the first lock, then the second, then the third. The door breathes out mist.)" : '(The Key forces the locks, one, two, three. The ice groans and gives.)'], () => {
      if (how === 'key' && q(S, 'nf_take') === 2) { G.setQuest('nf_take', 3); G.factions.add('gate', MERIT.rimetoll, 'rimetoll'); gold(G, 120); f.nf_hushed = 1; }
      if (!q(S, 'frozenspire') && how === 'key') G.setQuest('frozenspire', 1);
      G.save && G.save();
      if (AREAS_NIFL.frozenspire) G.loadArea('frozenspire', how === 'key' ? 'from_mouth_key' : 'from_mouth'); else G.toast('(The Frozen Spire is not built yet.)', 2.4);
    });
  }
  // ---- Hrefna (story 5.4): ice_lance (a bolt at the nearest foe, cd 8 s) and mist_veil (4 s, cd 20 s, when you are below 60 %)
  hrefnaTick(dt) {
    const G = this.G, S = G.S, F2 = G.svart && G.svart.follow, c = this.ctx;
    if (!c || !F2 || !F2.on || F2.id !== 'hrefna' || !F2.sprite) return;
    const C = G.combat, sp = F2.sprite, p = c.player; this.hlance = Math.max(0, (this.hlance || 0) - dt); this.hveil = Math.max(0, (this.hveil || 0) - dt); this.veilT = Math.max(0, (this.veilT || 0) - dt);
    if (C && this.hveil <= 0 && (S.hp || 0) < C.maxHp() * 0.6 && (S.hp || 0) > 0) { this.hveil = 20; this.veilT = 4; this.fxAt(c, 'mist_veil', p.x, p.y, p.z, { duration: 4, fadeIn: 0.2 }); F2.bark && F2.bark('Stay behind me. They cannot see you.'); }
    if (C && this.hlance <= 0 && C.enemies) {
      let best = null, bd = 6.5;
      for (const e of C.enemies) { if (!e.a || e.state === 'dead' || e.state === 'gone') continue; const d = Math.hypot(e.a.x - sp.x, e.a.z - sp.z); if (d < bd) { bd = d; best = e; } }
      if (best) { this.hlance = 8; C.damageEnemy(best, 16, { x: sp.x, z: sp.z }, 0.4); this.fxAt(c, 'ice_lance', best.a.x, c.heightAt(best.a.x, best.a.z) + 0.6, best.a.z, { duration: 0.8, fadeIn: 0 }); }
    }
  }
  // ---- telegraphed strikes (the bosses): a ring marks the spot, then the ice lands
  strike(kind, x, z, dmg, delay, r) {
    const c = this.ctx; if (!c) return;
    this.fxAt(c, kind === 'beam' ? 'beam_ring_red' : 'frost_ring', x, c.heightAt(x, z), z, { duration: delay, fadeIn: 0 });
    this.pend.push({ t: delay, x, z, dmg, r, kind });
  }
  tickStrikes(dt) {
    const c = this.ctx, p = c && c.player; if (!c || !this.pend.length) return;
    this.pend = this.pend.filter((s) => {
      s.t -= dt; if (s.t > 0) return true;
      this.fxAt(c, s.kind === 'beam' ? 'cold_beam' : 'ice_burst', s.x, c.heightAt(s.x, s.z), s.z, { duration: 0.7, fadeIn: 0 });
      if (Math.hypot(p.x - s.x, p.z - s.z) < s.r && this.G.combat && this.G.combat.hurtPlayer) this.G.combat.hurtPlayer(s.dmg, { x: s.x, z: s.z, ice: true }, 0.5);
      return false;
    });
  }
  // ---- the three bosses (story 8.1, 8.1a, 8.5). Scripted in tick functions like Muspelheim's Vharzul. Positions are authored with the Spire / Crown builds (BOSS_AT); the phase logic is live and
  // smoke-tested through qaBoss() in any area. Phase numbers live on the enemy (`phaseN`), one-shot flags are `p2` / `p3` / `p4`.
  phaseOf(e) { const fr = e.hp / e.D.hp, th = e.D.phases || []; return 1 + th.filter((t) => fr < t).length; }
  bossStart(which, pos, role) {   // role = the sprite role (the boss sheet's, once the art lands); smoke passes a stock role (the boss's ENEMIES entry is `def`)
    const G = this.G, def = which, at = pos || BOSS_AT[which]; if (this.cb[which] || !at) return null;
    const OPEN = { colossus: 'The ice shudders. "WHO WAKES THE GLACIER HEART?"', kael: '"Little hearth-rat. She said you\'d come."', veyra: '"Which is me? You\'ve lost count."' };
    G.toast(OPEN[which], 3.0);
    this.boss = this.foe({ id: which, role: role || which, def, pos: at.slice() }, () => this.bossDown(which)); this.boss.which = which; this.bt = 3; this.bt2 = 0; this.p4open = false;
    return this.boss;
  }
  tickBoss(dt) {
    const e = this.boss, c = this.ctx, G = this.G; if (!e || e.state === 'dead' || e.state === 'gone') return;
    const p = c.player, ph = this.phaseOf(e); e.phaseN = ph;
    if (e.which === 'veyra') return this.tickVeyra(e, ph, dt);
    this.bt -= dt; if (this.bt <= 0 && Math.hypot(e.a.x - p.x, e.a.z - p.z) < 14) { this.bt = ph === 1 ? 5.2 : 4.0; this.strike('ring', p.x, p.z, e.which === 'kael' ? 22 : 20, 1.0, 1.6); }
    if (ph >= 2 && !e.p2) {
      e.p2 = 1;
      if (e.which === 'colossus') { G.toast('The core cracks open! Two ice golems climb out of the walls.', 3.0); [[-4.6, -4.0], [4.6, -4.0]].forEach(([x, z], i) => this.foe({ id: 'co_g' + i, role: 'ice_golem', pos: [e.a.x + x, e.a.z + z] }, () => {})); }
      else { G.toast('Kael splits into three bat-shaped mist forms! Hit them, or he mends.', 3.0); e.bats = 3; }
    }
    if (ph >= 3 && !e.p3) {
      e.p3 = 1;
      if (e.which === 'colossus') { G.toast('The runes dim. Frost spirits swarm out of the ice.', 3.0); [[-3.0, 3.0], [3.0, 3.0], [0, 5.0]].forEach(([x, z], i) => this.foe({ id: 'co_s' + i, role: 'frost_spirit', pos: [e.a.x + x, e.a.z + z] }, () => {})); }
      else { G.toast("Kael's plate frosts white. Two Ice Wardens answer his call.", 3.0); [[-4.0, 3.0], [4.0, 3.0]].forEach(([x, z], i) => this.foe({ id: 'ka_w' + i, role: 'ice_warden', pos: [e.a.x + x, e.a.z + z] }, () => {})); }
    }
    if (e.which === 'kael' && ph === 2 && e.bats > 0) { e.healT = (e.healT || 0) + dt; if (e.healT > 2) { e.healT = 0; e.hp = Math.min(e.hp + e.D.hp * 0.012 * e.bats, e.D.hp * 0.6); } }   // ignoring the bats mends him (they die to any hit: qaBat)
  }
  tickVeyra(e, ph, dt) {   // P1 Mist (clones + lances), P2 Freeze (four portals), P3 Warden (red-ring beam, red cracks; grows to 6x), P4 Ask (the choice)
    const G = this.G, p = this.ctx.player;
    this.bt -= dt;
    if (ph <= 3 && this.bt <= 0 && Math.hypot(e.a.x - p.x, e.a.z - p.z) < 16) { this.bt = ph === 1 ? 5.0 : ph === 2 ? 4.2 : 3.6; this.strike(ph === 3 ? 'beam' : 'ring', p.x, p.z, ph === 3 ? 26 : 22, ph === 3 ? 1.5 : 1.0, ph === 3 ? 1.4 : 1.6); }
    if (ph >= 1 && !e.p1) { e.p1 = 1; e.clones = 3; }
    if (ph >= 2 && !e.p2) { e.p2 = 1; e.portals = [1, 1, 1, 1]; e.thaw = [0, 0, 0, 0]; G.toast('Veyra freezes the four portals, one by one. Stand on a thaw rune for 3 s to open each.', 3.2); }
    if (e.p2 && !e.p4) PORTALS.forEach(([x, z], i) => {   // standing on a portal's thaw rune for 3 s thaws it
      if (!e.portals[i]) return;
      if (Math.hypot(p.x - x, p.z - z) < 1.3) { e.thaw[i] += dt; if (e.thaw[i] >= 3) { e.portals[i] = 0; G.toast(`A portal thaws (${e.portals.filter((v) => !v).length}/4).`, 2.0); } } else e.thaw[i] = Math.max(0, e.thaw[i] - dt * 0.5);
    });
    if (ph >= 3 && !e.p3) { e.p3 = 1; e.grown = 6; this.bt = 0; G.toast('Rime-plate spikes outward. Red cracks open in her armour: hit them. A red ring warns of each beam.', 3.2); }   // the 6x swap is the boss sheet's p3 frame (art); the number is on the enemy
    if (ph >= 4 && !e.p4) { e.p4 = 1; this.p4(e); }
    if (e.p4 && !this.p4done) e.hp = Math.max(e.hp, e.D.hp * 0.1);   // she stops attacking and cannot die until the choice is made
  }
  p4(e) {   // P4: Ask (story 8.2). redeemable: Ask first (spare) or End it; otherwise only End it
    const G = this.G, S = G.S, rd = redeemable(S), opts = [];
    this.pend = [];
    if (rd) opts.push({ label: 'Ask first.', pick: () => ({ pages: ['(You lower your weapon. Hrefna lifts Eira\'s lantern; the cold fire turns violet, then white.)', '"You asked. At every realm. I counted."', '"Eira said \'ask first.\' I thought she meant \'don\'t ask\'."', '"Hold the Rift with me. Not alone."'], then: () => this.ending('redeemed') }) });
    opts.push({ label: 'End it.', pick: () => ({ pages: ['(Her rime-plate cracks into white dust. The platform shakes.)', '"Then ask them first. Next time."', ...(lockedBy(S) ? ['"You stood with the fire. No one asked me. Not one of you."'] : [])], then: () => this.ending('defeated') }) });
    this.G.openDialogue({ id: 'veyra', name: 'Veyra Ashmantle' }, { pages: ['(She has stopped. The aurora dims. Her lantern flickers.)', '"Ask me why. You never did."'], choice: { id: 'nf_p4', options: opts } });
  }
  ending(kind) {
    const G = this.G, S = G.S, f = flags(S), e = this.boss; this.p4done = true;
    if (kind === 'redeemed') f.veyra_redeemed = 1; else f.veyra_defeated = 1;
    f.nf_resolved = 1; if (e) { e.hp = 1; G.combat && G.combat.damageEnemy && G.combat.damageEnemy(e, 9999, { x: e.a.x, z: e.a.z }, 0); }
    mark(G);
  }
  bossDown(which) {
    const G = this.G, S = G.S, f = flags(S); this.boss = null;
    if (which === 'colossus') { this.find('fs_colossus'); f.fs_colossus = 1; G.give('colossus_core', 1); G.factions.add(conquer(S) ? 'gate' : 'embassy', 80, 'colossus'); }
    if (which === 'kael') { this.find('fs_boss'); f.fs_boss = 1; G.give('kael_fang', 1); G.setQuest('frozenspire', 2); G.factions.add(conquer(S) ? 'gate' : 'embassy', 80, 'kael');
      this.look('nf_kael_out', 'Kael Frostfang', ['(Kael falls to one knee, his plate frosting white.) "She never... looked at me."', '(His plate cracks and he is gone in a drift of snow. The Aerie door opens.)']); }
    mark(G);
  }
  // ---- Bifrost: The Frost Invitation (story 3.1). Hidden while no Niflheim area is built. The arch writes in frost once 3 realms are resolved.
  bifrost() {
    const G = this.G, S = G.S, open = () => gateOpen(S, this.qs()), invited = () => live() && resolvedCount(S) >= 3;
    this.spot({ id: 'frost_arch', pos: [6.6, -4.2], r: 1.6, label: () => (F(S).ng_read ? 'the ice arch: step through (E / A)' : 'the Niflheim arch: it is writing (E / A)'), show: () => invited() && !open() && (!F(S).ng_read || !!F(S).ng_halvard), act: () => this.frostArch() });
    this.spot({ id: 'halvard_frost', pos: [-3.4, 0.9], r: 1.5, label: 'Gatewright Halvard: the frost-letter (E / A)', show: () => invited() && !open() && !!F(S).ng_read && !F(S).ng_halvard, act: () => this.halvard() });
  }
  frostArch() {
    const G = this.G, S = G.S, f = flags(S);
    if (!f.ng_read) return this.look('ng_read', 'The Niflheim arch', FROST_LETTER, () => { f.ng_read = 1; G.give('frost_letter', 1); G.setQuest('nf_gate', 1); mark(G); });
    this.look('ng_open', 'The ice arch', ['(The ice parts into a bridge of runes. On the far side something small and blue is waiting.)'], () => { f.ng_opened = 1; G.save && G.save(); G.loadArea('niflheim', 'from_bifrost'); });
  }
  halvard() { const G = this.G, f = flags(G.S); this.look('ng_halvard', 'Gatewright Halvard', ['(He reads the frost-letter, and for a moment the cold is on his face. Then it is not.)', '"Never seen the ice do that. Hm. Go on."'], () => { f.ng_halvard = 1; mark(G); }); }
  gateSpirit() {   // the far side's guard (1.2x frost spirit): its death moves The Frost Invitation 1 -> 2
    const G = this.G, f = flags(G.S);
    this.foe({ id: 'ng_spirit', role: 'frost_spirit', pos: [0, 5.4] }, () => { f.ng_spirit = 1; G.setQuest('nf_gate', 2); G.toast('The spirit gutters out. Someone is waiting on the Quiet Shore.', 3.0); mark(G); });
  }
  update(dt) {
    if (!this.ctx) return;
    const S = this.G.S;
    if (this.area === 'niflheim' && !this.G.dlg && !this.G.busy && this.G.combat && F(S).ng_opened && !F(S).ng_spirit && !this.cb.ng_spirit) this.gateSpirit();
    this.revealTick(); this.hrefnaTick(dt); this.tickStrikes(dt); this.tickBoss(dt);
  }
  // QA helpers for the smoke test
  qaBoss(which, pos, role = 'wraith') { return !!this.bossStart(which, pos || [0, -6], role); }
  qaHp(id, frac) { const e = this.G.combat.enemies.find((x) => x.id === id); if (!e) return false; e.hp = e.D.hp * frac; return true; }
  qaTick(dt = 0.1, n = 1) { for (let i = 0; i < n; i++) { this.tickBoss(dt); this.tickStrikes(dt); } return this.qaBossState(); }
  qaBossState() { const e = this.boss; return { which: e ? e.which : null, phase: e ? e.phaseN : 0, p2: !!(e && e.p2), p3: !!(e && e.p3), p4: !!(e && e.p4), portals: e && e.portals ? [...e.portals] : null, clones: e ? e.clones || 0 : 0, bats: e ? e.bats || 0 : 0, pend: this.pend.length, hp: e ? e.hp : null, scale: e ? (e.grown || e.D.scale) : null, framed: e ? !!e.D.framed : null,
    dlg: this.G.dlg ? this.G.dlg.npc.id : null, ids: this.G.combat ? this.G.combat.enemies.filter((x) => x.state !== 'dead' && x.state !== 'gone').map((x) => x.id) : [] }; }
  qaThaw(i) { const e = this.boss; if (e && e.portals) e.portals[i] = 0; return this.qaBossState(); }
  qaEnding(kind) { this.p4done = true; const f = flags(this.G.S); if (kind === 'redeemed') f.veyra_redeemed = 1; else f.veyra_defeated = 1; return { redeemed: !!f.veyra_redeemed, defeated: !!f.veyra_defeated }; }
  qaP4Options() { const S = this.G.S; return { redeemable: redeemable(S), locked: lockedBy(S) }; }
  qaLine(id) { const e = TALK[id](this.G.S); return e && e.pages ? e.pages[0] : null; }
  qaTalk(id) { const e = TALK[id](this.G.S); if (e && e.then) e.then(this.G); return { pages: e ? e.pages.length : 0, choice: e && e.choice ? e.choice.options.map((o) => o.label) : null, locked: e && e.choice ? e.choice.options.filter((o) => o.locked).map((o) => o.label) : null }; }
  qaPick(label, id = 'frostspeaker') { const e = TALK[id](this.G.S), o = e.choice.options.find((x) => x.label === label), nx = o.pick(this.G); if (nx && nx.then) nx.then(this.G); return nx ? nx.pages.length : 0; }
  qaSpot(id) { const sp = this.spots.find((x) => x.id === id); if (!sp) return false; sp.act(); return true; }
  qaKill(id) { const f = this.cb[id]; if (!f) return false; f(); return true; }
  qaCold() { return cold(this.G.S); }
  qaWx() { return { kinds: ['frost_mist', 'still_frost'].filter((k) => WX_KINDS[k]), hook: !!WX_HOOK.niflheim }; }
  qaDefs() {   // the realm's shared-table registrations, for the smoke
    return { quests: Object.keys(QUESTS).filter((k) => ['nf_gate', 'nf_lanterns', 'nf_cold', 'nf_hrefna', 'nf_eira', 'nf_take', 'frozenspire', 'nf_staff', 'nf_elk', 'frostvigil'].includes(k)).length,
             merit: Object.fromEntries(Object.keys(MERIT).filter((k) => ['nf_gate', 'rimetoll', 'spire_c', 'nf_lanterns', 'nf_cold', 'nf_rival', 'nf_hrefna', 'nf_eira', 'frozenspire', 'frostvigil'].includes(k)).map((k) => [k, MERIT[k]])),
             bosses: Object.fromEntries(['colossus', 'kael', 'veyra'].map((k) => [k, { scale: ENEMIES[k].scale, framed: ENEMIES[k].framed, plate: !!ENEMIES[k].plate, golem: !!ENEMIES[k].golem, boss: ENEMIES[k].boss, phases: ENEMIES[k].phases, element: ENEMIES[k].element }])),
             foes: ['frost_spirit', 'mist_stalker', 'ice_golem', 'frost_wraith', 'ice_warden', 'brisa', 'colossus', 'kael', 'veyra'].filter((k) => ENEMIES[k]), bases: ['mistalpha', 'spiritprime'].filter((k) => BASES[k]),
             wx: { frost_mist: !!WX_KINDS.frost_mist, still_frost: !!WX_KINDS.still_frost }, comp: COMP.hrefna || null, kit: !!FOLLOW_KIT.hrefna, shop: !!SHOPS.nf_trader, lock: NIFL_MUSP_LOCK,
             items: ['frost_letter', 'spire_key', 'eira_lantern', 'heart_ice', 'frostmoss_cake', 'warm_tea', 'cold_lamp', 'fur_mantle', 'kael_fang', 'colossus_core', 'hoarfrost_crown'].filter((k) => ITEMS[k]).length,
             talk: ['frostspeaker', 'hrefna', 'veyra', 'eira', 'brisa', 'nf_trader', 'elkman', 'archivist'].filter((k) => TALK[k]).length };
  }
  qa() {
    const c = this.ctx, S = this.G.S, f = F(S), gm = c ? (c.scene.game || {}) : {};
    return { realm: 'niflheim', built: Object.keys(AREAS_NIFL), planned: NIFL_AREAS, area: this.area, exits: (gm.exits || []).map((e) => e.to), portals: (gm.portals || []).map((p) => p.to),
             spots: this.spots.filter((x) => x.show()).length, gate: this.gate.qa(), alliance: (f.alliance || {}).niflheim || null, rival: (f.rivals || {}).niflheim || null, rivals: { ...(f.rivals || {}) }, moods: { ...(f.realm_mood || {}), }, dlg: this.G.dlg ? this.G.dlg.npc.id : null,
             mood: (f.realm_mood || {}).niflheim || 0, lockedBy: lockedBy(S), allies: allyCount(S), resolved: resolvedCount(S), evidence: evidenceCount(S), redeemable: redeemable(S), companions: Object.keys(f.companions || {}),
             quests: Object.fromEntries(['nf_gate', 'nf_lanterns', 'nf_cold', 'nf_hrefna', 'nf_eira', 'nf_take', 'frozenspire', 'nf_staff', 'nf_elk', 'frostvigil'].map((k) => [k, q(S, k)])),
             flags: { read: !!f.ng_read, halvard: !!f.ng_halvard, opened: !!f.ng_opened, spirit: !!f.ng_spirit, open: !!f.nf_gate_open, revealed: !!f.veyra_revealed, trusted: !!f.nf_trusted, cleared: !!f.nf_cleared, vigil: f.nf_vigil || 0 },
             actors: c ? c.actors.list.map((a) => a.id || a.role) : [], fx: this.fx.length, lights: this.lights.length, gold: S.gold || 0 };
  }
}
export const BOSS_AT = { colossus: [0, -8], kael: [0, -8], veyra: [0, -8] };   // provisional: the Spire / Crown builds set the real spots (fully on or fully off screen)

// ------------------------------------------------------------------ the gate (story 3.1): runtime wiring on both ends, like muspelheim.js's MpGate (no Bifrost rebuild)
class NfGate {
  constructor(nf) { this.nf = nf; this.G = nf.G; this.fetching = false; }
  get ctx() { return this.nf.ctx; }
  qs() { return this.nf.qs(); }
  put(sc) { const gm = (sc.game = sc.game || {}); gm.spawns = gm.spawns || {}; if (!gm.spawns.from_niflheim) gm.spawns.from_niflheim = NF_ARCH.spawn.slice(); }
  atHub(ctx) {   // Mistmere: the ice arch back to Bifrost (runtime portal) + the Bifrost scene prefetched with its return spawn
    const G = this.G, gm = ctx.scene.game || (ctx.scene.game = {});
    gm.portals = gm.portals || [];
    if (!gm.portals.find((p) => p.to === 'bifrost')) gm.portals.push({ ...HUB_GATE, rect: HUB_GATE.rect.slice() });
    if (G.scenes && G.scenes.bifrost) { this.put(G.scenes.bifrost); return; }
    if (this.fetching || !G.scenes) return;
    this.fetching = true;
    fetch('areas/bifrost/scene.json').then((r) => r.json()).then((sc) => { if (!G.scenes.bifrost) G.scenes.bifrost = sc; this.put(G.scenes.bifrost); }).catch(() => {}).finally(() => { this.fetching = false; });
  }
  atBifrost(ctx) { this.put(ctx.scene); this.wire(ctx); }
  reopen() { if (this.ctx && this.nf.area === 'bifrost') this.wire(this.ctx); }
  wire(ctx) {   // the sealed ice arch becomes a portal once the gate is open AND Mistmere is built (dormant otherwise: the arch just stays sealed)
    const gm = ctx.scene.game; if (!gm || !live() || !gateOpen(this.G.S, this.qs())) return;
    gm.sealed = (gm.sealed || []).filter((g) => g.arch !== 'niflheim');
    gm.portals = gm.portals || [];
    if (!gm.portals.find((p) => p.to === 'niflheim')) gm.portals.push({ fx: 'gate_niflheim', to: 'niflheim', spawn: 'from_bifrost', rect: NF_ARCH.rect.slice(), label: "Niflheim's gate" });
    (gm.spawns = gm.spawns || {}).from_niflheim = gm.spawns.from_niflheim || NF_ARCH.spawn.slice();
  }
  qa() { const c = this.ctx, gm = c ? (c.scene.game || {}) : {}; return { portals: (gm.portals || []).map((p) => p.to), sealed: (gm.sealed || []).map((g) => g.arch), spawns: Object.keys(gm.spawns || {}), open: gateOpen(this.G.S, this.qs()), live: live() }; }
}
// the sealed arch's look (Bifrost's Crossing.pages): once 3 realms are resolved and the realm is built, the frost writes; before that the stock "no key opens it yet" text stands
{
  const pages0 = Crossing.prototype.pages;
  Crossing.prototype.pages = function pages(g) {
    if (g && g.arch === 'niflheim' && live() && resolvedCount(this.G.S) >= 3) return [...FROST_LETTER, 'Key: the frost-letter (flag nf_open). Read the arch, show Gatewright Halvard, and step through.'];
    return pages0.call(this, g);
  };
}
