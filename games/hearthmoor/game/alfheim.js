// [ALFHEIM] Alfheim (realm-alfheim branch), built from the Hearthmoor Story script (staging story/alfheim.md, batch 2,
// 2026-10-06) with Cozy Builder's decisions. Everything Alfheim lives here (+ alfheim_beams.js, alfheim_lumi.js,
// alfheim_bosses.js) and is merged into the shared tables at import, so shared files only carry a few marked hook lines.
//   * The Frozen Gate (Bifrost): Halvard cuts the Keybearer's key (Guild rank 3); strike Alfheim's frozen seal, beat the
//     frost sentinel, tell Halvard -> the arch opens (S.flags.alf_gate_open; ?alfheim for QA)
//   * Lumenvale, 3 areas: alfheim (the Glimmer Steps hub), lumen_court (the Moonlit Court: Regent Aerin's choice, the
//     Prism Library lens table, the Prism Spire door), wispwood (nests, glowfrog ponds, the frost scar, rifts + rares)
//   * befriend: A Name in Frost -> The Dimming (Lumi joins) -> The Prism Vault (Sylvaine resealed, asleep)
//     conquer: The Prism Claim (ranger posts, Faelan yields) -> The Prism Vault (the Heart taken) -> dark Lumenvale
//   * the Prism Vault: 9 rooms, 3 beam puzzles (alfheim_beams.js), the Lens Warden (2.8x), Lady Sylvaine (6x, 3 phases)
//   * the prism sky: aurora at night (spells come back 10% faster), prism-rain showers at late dusk
//   * lavender day = per-area day dimming (each area spec's grades: sun 0.9, exposure 0.9, sun #c8b8f0); dark Lumenvale =
//     a runtime re-grade of the clock's grades + lamp tints (cold violet, 1 in 6 red) + neon-blue watch-lamps
// Not built yet (documented in docs/ALFHEIM.md): Wisp Night's festival runtime + the wisp catalog, The Dancing Blade /
// Prism Edge, the Prism light school, the P6 hero palette-swap (the generic Mirror Duelist stands in, as approved).
import { ENEMIES, SPAWNS } from './heroes.js';
import { TALK, QUESTS, ITEMS, MARKER_HOOKS } from './data.js';
import { REALM, MERIT } from './factions.js';
import { XP } from './progress.js';
import { GLOW_TABLES } from './glow.js';
import { RIFT_AREAS } from './rifts.js';
import { BASES, RARE_AREAS } from './rares.js';
import { GEMS, GEM_IDS } from './loot.js';
import { SHOPS } from './shop.js';
import { WAYS } from './ravenhold.js';
import { Beams } from './alfheim_beams.js';
import { Lumi } from './alfheim_lumi.js';
import { AlfFoes } from './alfheim_bosses.js';

const V = '#a45cf0', COLD = '#5ab4f0', RED = '#ff4a3a';
export const AREAS_ALF = { alfheim: 'areas/alfheim/', lumen_court: 'areas/lumen_court/', wispwood: 'areas/wispwood/', prismvault: 'areas/prismvault/' };
export const AREA_NAMES_ALF = { alfheim: 'Lumenvale: the Glimmer Steps', lumen_court: 'The Moonlit Court', wispwood: 'The Wispwood', prismvault: 'The Prism Vault' };
const LUMENVALE = ['alfheim', 'lumen_court', 'wispwood'];
const BF_ARCH = { pos: [-5.0, -11.9], rect: [-5.75, -12.3, -4.25, -11.45], spawn: [-5.0, -10.1, 'down'] };   // Bifrost's Alfheim arch
let GREF = null;
const flags = (S) => (S.flags = S.flags || {});
const ally = (S) => (flags(S).alliance = flags(S).alliance || {});
const A = (S) => ((S.flags || {}).alliance || {}).alfheim;
const F_ = (S) => S.flags || {};
const found = (S, ids) => ids.filter((id) => (S.found || {})[id]).length;
const DW = ['dw_1', 'dw_2', 'dw_3', 'dw_4', 'dw_5'];
const gold = (G, n) => { G.S.gold = (G.S.gold || 0) + n; G.toast(`+${n} gold`, 1.8); G.drawBag && G.drawBag(); };
export const lockRival = (S, realm) => { const f = flags(S); f.rivals = { ...(f.rivals || {}), [realm]: 'locked' }; };
export const moodUp = (S, realm) => { const f = flags(S); f.realm_mood = { ...(f.realm_mood || {}), [realm]: ((f.realm_mood || {})[realm] || 0) + 1 }; };
const NIGHT = (t) => t > 0.8 || t < 0.25;
const hash = (n) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
export function prismWeather(day, t) {
  if (NIGHT(t)) return hash(day * 7 + 31) < 0.6 ? 'aurora' : 'clear';
  if (t >= 0.62 && t < 0.8) return hash(day * 5 + 77) < 0.3 ? 'prismrain' : 'clear';
  return 'clear';
}

// ------------------------------------------------------------------ foes (script 8.1-8.4; scale = hero heights)
Object.assign(ENEMIES, {
  prismshard: { name: 'Prism shard', hp: 40, dmg: 9, speed: 1.4, reach: 6.0, keep: 3.4, windup: 0.6, cd: 2.4, aggro: 6.5, r: 0.24, push: 0.6, ranged: true, float: true, bolt: 'prism_bolt' },
  willwisp: { name: 'Will-o\'-wisp', hp: 30, dmg: 7, speed: 2.2, reach: 5.0, keep: 3.0, windup: 0.5, cd: 2.2, aggro: 7, r: 0.22, push: 0.7, ranged: true, float: true, blink: 6, lure: true, bolt: 'prism_bolt' },
  crystalgolem: { name: 'Crystal golem', hp: 150, dmg: 17, speed: 0.95, reach: 1.7, windup: 0.7, cd: 2.0, aggro: 5.5, r: 0.38, push: 0.2, heavy: true, slam: true, prismShield: 0.6, beamWeak: true },
  mirrorduelist: { name: 'Mirror Duelist', hp: 95, dmg: 13, speed: 2.1, reach: 1.4, windup: 0.4, cd: 1.3, aggro: 7, r: 0.3, push: 0.5, elite: true, mimic: true, invisRain: true },
  mirroryou: { name: 'Your Reflection', hp: 110, dmg: 13, speed: 2.1, reach: 1.4, windup: 0.4, cd: 1.3, aggro: 8, r: 0.3, push: 0.5, elite: true, mimic: true },
  lightranger: { name: 'Light-elf ranger', hp: 70, dmg: 10, speed: 1.9, reach: 7.0, keep: 4.0, windup: 0.5, cd: 1.8, aggro: 8, r: 0.28, push: 0.5, ranged: true, bolt: 'bolt' },
  faelan: { name: 'Captain Faelan Thorne', hp: 260, dmg: 12, speed: 2.2, reach: 7.0, keep: 4.0, windup: 0.45, cd: 1.4, aggro: 10, r: 0.32, push: 0.5, ranged: true, bolt: 'bolt', elite: true, yieldAt: 0.25, respawn: 1e9 },
  frostsentinel: { name: 'Frost sentinel', scale: 2.0, hp: 300, dmg: 16, speed: 1.0, reach: 2.0, windup: 0.6, cd: 1.8, aggro: 9, r: 0.6, push: 0.2, heavy: true, slam: true, chill: 20, combo: 3, glow: COLD, respawn: 1e9 },
  lenswarden: { name: 'The Lens Warden', scale: 2.8, hp: 520, dmg: 22, speed: 0.95, reach: 3.0, windup: 0.75, cd: 2.0, aggro: 8, r: 0.85, push: 0.15, heavy: true, slam: true, boss: true,
                wave: { every: 3, r: 4.4, dmg: 16 }, prismShield: 0.9, beamWeak: true, glow: V, legendary: true, respawn: 1e9 },
  sylvaine: { name: 'Lady Sylvaine, the Light-Drinker', scale: 6, hp: 1700, dmg: 24, speed: 1.4, reach: 7.0, keep: 4.5, windup: 0.8, cd: 2.0, aggro: 12, r: 1.4, push: 0.2, ranged: true, float: true,
              boss: true, minion: 'prismshard', phases: [0.65, 0.3], drain: { dps: 8, heal: 2, range: 8 }, shield: 0.8, clones: 2, dark: { every: 10, lunge: 34 }, beamWeak: true,
              glow: V, legendary: true, respawn: 1e9, bolt: 'prism_bolt', minRar: 3 },
  sylvaine_reflection: { name: 'A reflection of Sylvaine', scale: 6, hp: 60, dmg: 8, speed: 1.2, reach: 6.0, keep: 4.5, windup: 0.9, cd: 2.6, aggro: 12, r: 1.2, push: 0.2, ranged: true, float: true, bolt: 'prism_bolt' },
});
Object.assign(XP, { mirroryou: 72, prismshard: 32, willwisp: 26, crystalgolem: 58, mirrorduelist: 72, lightranger: 40, frostsentinel: 180, faelan: 200, lenswarden: 320, sylvaine: 800, sylvaine_reflection: 0 });
Object.assign(BASES, {
  shardmother: { name: 'Shardmother', scale: 2.4, hp: 290, dmg: 12, speed: 1.2, reach: 6.5, keep: 3.8, windup: 0.55, cd: 2.0, aggro: 8, r: 0.66, push: 0.4, ranged: true, float: true, bolt: 'prism_bolt', minion: 'prismshard', xp: 180 },
  glassstalker: { name: 'Glass Stalker', scale: 2.6, hp: 300, dmg: 18, speed: 1.6, reach: 2.4, windup: 0.5, cd: 1.6, aggro: 8.5, r: 0.6, push: 0.3, blink: 4, invisRain: true, xp: 190 },
});
RARE_AREAS.wispwood = { bases: ['shardmother', 'glassstalker'], spots: [[5.4, -3.6], [-6.0, 0.4]] };
RARE_AREAS.prismvault = { bases: ['shardmother', 'glassstalker'], spots: [[11.2, 2.2], [0.0, -30.0]] };   // P3 grotto / P7 stair head
RIFT_AREAS.wispwood = { foes: ['prismshard', 'willwisp', 'crystalgolem'], spots: [[3.6, 1.6], [-4.4, -4.6], [-2.4, 7.4]] };
SPAWNS.wispwood = [
  { id: 'ww_wisp0', role: 'willwisp', pos: [3.8, -1.2] }, { id: 'ww_wisp1', role: 'willwisp', pos: [-3.6, 3.0] },
  { id: 'ww_golem0', role: 'crystalgolem', pos: [-4.2, -4.6] },
  { id: 'ww_shard_n0', role: 'prismshard', pos: [6.4, -3.4], night: true }, { id: 'ww_shard_n1', role: 'prismshard', pos: [-6.6, 0.4], night: true },
  { id: 'ww_wisp_n', role: 'willwisp', pos: [1.2, -3.6], night: true },
];
// the Vault's pools depend on the save (bosses stay down, conquer adds rangers): a getter, read by combat.attach
const VAULT = [
  ['pv_s1', 'prismshard', [-3.0, 30.4]], ['pv_s2', 'prismshard', [3.0, 27.8]], ['pv_s3', 'prismshard', [0.0, 24.6]], ['pv_w1', 'willwisp', [-3.4, 26.0]],
  ['pv_g2', 'crystalgolem', [0.6, 15.6]], ['pv_s4', 'prismshard', [-4.0, 11.6]], ['pv_s5', 'prismshard', [4.2, 16.4]],
  ['pv_w3a', 'willwisp', [10.2, 2.6]], ['pv_w3b', 'willwisp', [12.4, -1.4]],
  ['lenswarden', 'lenswarden', [2.4, 0.6]], ['pv_s6', 'prismshard', [-4.2, 5.0]], ['pv_s7', 'prismshard', [3.6, 5.4]],
  ['pv_d6a', 'mirrorduelist', [-3.6, -18.0]], ['pv_d6b', 'mirrorduelist', [3.8, -24.2]],
  ['pv_s8', 'prismshard', [-0.6, -37.6]], ['pv_s9', 'prismshard', [0.6, -37.6]],
];
Object.defineProperty(SPAWNS, 'prismvault', { enumerable: true, configurable: true, get() {
  const S = GREF ? GREF.S : { flags: {} }, F = S.flags || {}, out = [];
  for (const [id, role, pos] of VAULT) if (!(id === 'lenswarden' && F.pv_warden)) out.push({ id, role, pos, once: id === 'lenswarden' });
  if (A(S) === 'conquer') out.push({ id: 'pv_r1a', role: 'lightranger', pos: [-2.4, 28.6] }, { id: 'pv_r1b', role: 'lightranger', pos: [2.4, 28.6] });
  return out;
} });
Object.assign(REALM, { alfheim: 'embassy', lumen_court: 'embassy', wispwood: 'embassy', prismvault: 'embassy' });
Object.assign(MERIT, { thaw: 60, claim: 60, alf_name: 60, apology: 20, alf_dim: 80, vault: 120, vault_c: 120, wispnight: 40 });
GEMS.prism_core = { name: 'Prism core', col: '#6af0f0', lo: '#a45cf0', mods: { spellMul: 0.04, summonMul: 0.04, crit: 0.01 }, price: 130, about: '+4% spells · +4% summons · +1% crit' };
if (!GEM_IDS.includes('prism_core')) GEM_IDS.push('prism_core');
SHOPS.lumen = { name: 'Saelis\'s Lanterns', keeper: 'Saelis, lantern seller', goods: ['tonic', 'glowseed'], gems: ['moon_opal'], gear: { n: 3, rar: [1, 1, 2] }, sellMul: 1 };
WAYS.alfheim = ['Lumenvale, the Glimmer Steps', 'alfheim', 'from_waystone'];
Object.assign(ITEMS, {
  thawkey: { name: 'Keybearer\'s key', px: 'thawkey', about: 'Cut by the Guild for Alfheim\'s frozen seal. It hums near ice.' },
  frost_stencil: { name: 'Rune stencil', px: 'frost_stencil', about: 'Frost-iron, with Alfheim runes cut clean through. Never warm. Evidence.' },
  moss_letter: { name: 'Mossbrook\'s apology', px: 'moss_letter', about: 'In Burrowmoss\'s hand, four drafts deep. Tobble drew a mushroom on it.' },
  spirekey: { name: 'Spire key', px: 'spirekey', about: 'A key of violet glass. It opens the Prism Spire, and nothing else, ever.' },
  speaklens: { name: 'Speaking lens', px: 'speaklens', about: 'Mirelle\'s voice comes out of it. Sometimes she forgets it\'s on.' },
  wisp_net: { name: 'Wisp net', px: 'wisp_net', about: 'Nim\'s spare net. Catch wisps with E / A. Be gentle. Let them go after.' },
  prism_glass: { name: 'Prism glass', px: 'prism_glass', about: 'A shard of living prism. It splits light into three when you breathe on it.' },
  prism_heart: { name: 'Prism Heart', px: 'prism_heart', about: 'The core of Alfheim\'s Heart Prism. Warm. Every lamp in Lumenvale went dark for it.' },
  queen_lantern: { name: 'The Queen\'s Lantern', px: 'queen_lantern', about: 'Aerin\'s gift. A violet lantern from Sylvaine\'s nursery. Lumi used to sit in it.' },
  sylvaine_crown: { name: 'Sylvaine\'s Crown', px: 'sylvaine_crown', about: 'Violet prism spikes, cold to the touch. A trophy. No one in Alfheim will look at it.' },
});

// ------------------------------------------------------------------ glow: always-on gloom-and-glow pools
if (GLOW_TABLES) {
  Object.assign(GLOW_TABLES.ALWAYS, { alfheim: true, lumen_court: true, wispwood: true, prismvault: true });
  GLOW_TABLES.POOLS.alfheim = [[6.4, 4.6, 'cold', COLD], [-6.0, 5.4, 'violet', V], [0.0, -2.0, 'light', V], [-3.6, 9.0, 'violet', V], [8.8, 1.2, 'bloom', 'coldfire'],
    [10.4, -6.6, 'cold', COLD], [-8.4, 3.6, 'red', RED], [3.6, -2.4, 'bloom', 'violet']];
  GLOW_TABLES.POOLS.lumen_court = [[0.0, -6.0, 'violet', V], [-2.0, 4.0, 'cold', COLD], [-8.2, 1.6, 'light', V], [9.4, -6.2, 'violet', V], [5.0, 3.0, 'bloom', 'violet'], [-4.4, -2.0, 'red', RED]];
  GLOW_TABLES.POOLS.wispwood = [[4.4, 7.6, 'red', RED], [-5.6, 3.6, 'cold', COLD], [-9.0, -6.4, 'violet', V], [-1.0, 0.8, 'light', V], [6.0, 4.0, 'bloom', 'coldfire'],
    [2.4, -5.2, 'bloom', 'violet'], [-8.4, 6.8, 'cold', COLD], [8.2, 3.0, 'bloom', 'violet']];
  GLOW_TABLES.POOLS.prismvault = [[0.0, 38.0, 'violet', V], [-4.2, 30.0, 'cold', COLD], [4.0, 25.0, 'violet', V], [11.0, 1.4, 'cold', COLD], [-4.6, -9.4, 'violet', V],
    [0.0, -21.0, 'violet', V], [0.0, -33.0, 'light', V], [0.0, -47.0, 'violet', V], [-6.0, -47.0, 'red', RED], [6.0, -47.0, 'red', RED]];
}

// ------------------------------------------------------------------ quests (script section 3)
Object.assign(QUESTS, {
  alf_gate: { title: 'The Frozen Gate', giver: 'Gatewright Halvard Ness', story: true, steps: {
    1: (S) => { const f = F_(S);
      if (!f.ag_struck) return 'Strike Alfheim\'s frozen seal with the Keybearer\'s key (E / A at the violet gate, Bifrost Crossing).';
      if (!f.ag_sentinel) return 'Defeat the frost sentinel that tore free of the seal!';
      return 'Tell Gatewright Halvard the seal is broken.'; },
    2: 'Tell Gatewright Halvard the seal is broken.',
    3: 'Alfheim\'s gate is open. Violet light spills across the Crossing.' } },
  alf_name: { title: 'A Name in Frost', giver: 'Regent Aerin Vael', story: true, steps: {
    1: (S) => { const f = F_(S), inv = S.inv || {};
      if (!f.an_lens) return inv.blight_spike ? 'Show the frost-iron spike to Mirelle at the Prism Library\'s lens table.' : 'Ask Mirelle in the Prism Library how to prove Alfheim innocent.';
      if (!f.an_stencil) return 'Search the frost scar in the Wispwood, where the vines died of cold.';
      return 'Bring the rune stencil to Mirelle\'s lens table.'; },
    2: 'Tell Regent Aerin what the lens shows.',
    3: 'Alfheim\'s name is clear. The runes were cut by frost, and the frost came from somewhere cold.' } },
  alf_dim: { title: 'The Dimming', giver: 'Mirelle Glasswing', story: true, steps: {
    1: (S) => { const f = F_(S), n = found(S, DW);
      if (!f.dm_lumi) return 'Find the grey old wisp in the Wispwood\'s central nest.';
      if (n < 5) return `Carry dimmed wisps to a glowfrog pond to relight them (E / A at a nest, then a pond). ${n}/5`;
      if (!f.dm_trail) return 'Follow the thread of drained light to the Moonlit Court. Lumi can see it.';
      return 'Tell Mirelle where the light is going.'; },
    2: 'Tell Regent Aerin the light drains into the Prism Spire.',
    3: 'The wisps burn again, for now. The light was draining into the Prism Vault, and Lumi is with you.' } },
  alf_take: { title: 'The Prism Claim', giver: 'Regent Aerin Vael', story: true, steps: {
    1: (S) => { const f = F_(S), n = found(S, ['pc_r1', 'pc_r2', 'pc_r3']);
      if (n < 3) return `Break the ranger posts guarding the Spire bridge. ${n}/3`;
      if (!f.pc_faelan) return 'Captain Faelan Thorne holds the Spire key. Take it from her.';
      return 'Open the Prism Spire door with Faelan\'s key.'; },
    2: 'Open the Prism Spire door with Faelan\'s key.',
    3: 'The Spire is yours. Below it lies the Prism Heart, and whatever the elves locked up with it.' } },
  prismvault: { title: 'The Prism Vault', giver: 'Regent Aerin Vael', story: true, steps: {
    1: (S) => { const f = F_(S), n = found(S, ['pv_lens1', 'pv_lens2', 'pv_lens3']);
      if (n < 3) return `Realign the Vault's three great lenses (light-beam puzzles). ${n}/3`;
      if (!f.pv_boss) return 'Descend to the Heart Prism. Something is awake down there.';
      return A(S) === 'conquer' ? 'Take the Prism Heart and leave the Vault.' : 'Reseal the Heart Prism (E / A at the Heart).'; },
    2: (S) => (A(S) === 'conquer' ? 'Leave Alfheim with the Prism Heart.' : 'Return to Regent Aerin in the Moonlit Court.'),
    3: (S) => (A(S) === 'conquer' ? 'The Prism Heart is yours. Lumenvale\'s lights are going out, one by one.'
                                   : 'Sylvaine is resealed, asleep in the Heart Prism, fed and at peace. Alfheim calls you friend.') } },
});

// ------------------------------------------------------------------ talk (script sections 4-6)
const say1 = (line) => ({ pages: [line] });
const met = (k) => (G) => { G.S.met = { ...(G.S.met || {}), [k]: 1 }; };
const night = () => !!(GREF && GREF.ctx && NIGHT(GREF.ctx.clock.t));
const notC = (S, line) => (A(S) === 'conquer' ? '(The elf looks away and pulls her lantern closer.)' : line);
const gatewright0 = TALK.gatewright, warden0 = TALK.warden;
Object.assign(TALK, {
  // Halvard: the Frozen Gate hook (Keybearer, Guild rank 3) + its turn-in, then his own talk
  gatewright(S) {
    const q = (S.quests || {}).alf_gate || 0, f = F_(S);
    if ((q === 1 && f.ag_sentinel) || q === 2) return {
      pages: ['The seal\'s broken? Good. Good. The ledger will say so.',
              'Odd thing. That frost took my key like it knew the shape. I\'ll check the stock. Keys go missing, you know.',
              'Alfheim\'s open. Mind the elves. They\'ve been shouting through a frozen door for months. They\'ll be cross.'],
      then: (G) => { G.setQuest('alf_gate', 3); G.factions.add('gate', MERIT.thaw, 'thaw'); gold(G, 50); flags(G.S).alf_gate_open = 1; G.alfheim && G.alfheim.reopenGate(); },
    };
    const base = gatewright0 ? gatewright0(S) : { pages: ['Gatewright Halvard Ness, Gatekeepers\' Guild.'] };
    if (((S.ranks || {}).gate || 0) >= 3 && !q && base.choice && !base.then) {
      const opt = { label: 'About the frozen gates...', pick: () => ({
        pages: ['Keybearer. Has a ring to it. And a key, now. This one took some cutting. Longer than it should have.',
                'Alfheim\'s seal is frozen from the far side. Veyra\'s work, they say. Strike it with this and step back. Quickly.'],
        then: (G2) => { G2.give('thawkey', 1); G2.setQuest('alf_gate', 1); } }) };
      return { ...base, choice: { ...base.choice, options: [opt, ...base.choice.options] } };
    }
    return base;
  },
  warden(S) {
    const f = F_(S);
    if (((S.quests || {}).alf_gate || 0) === 3 && (f.alliance || {}).vanaheim === 'befriend' && !f.moss_letter) return {
      pages: ['Alfheim\'s gate is open? Then take this. Mossbrook\'s apology, in my own hand. Took me four drafts.',
              'Tell the elves we were wrong. Tell them nicely. Tobble wanted to add a drawing. I let him.'],
      then: (G) => { G.give('moss_letter', 1); flags(G.S).moss_letter = 1; },
    };
    return warden0 ? warden0(S) : say1('...');
  },
  regent(S) {
    const a = A(S), q = S.quests || {}, f = F_(S), inv = S.inv || {};
    if (!a) {
      const pages = ['A Midgard face. The first through our gate in months. I am Aerin Vael, Regent of Lumenvale.',
                     'Mossbrook calls us poisoners. Midgard sends you. And our own wisps are going dark. It has not been a good season.'];
      if (inv.blight_spike) pages.push('You carry frost-iron. I can feel it from here. Is that Vanaheim\'s \'proof\'?');
      pages.push('So tell me plainly, hearth-walker. Are you Alfheim\'s friend, or one more accuser at the door?');
      const befriend = (extra) => (G) => { ally(G.S).alfheim = 'befriend'; G.toast('Alfheim: befriended', 2.2); G.setQuest('alf_name', 1); lockRival(G.S, 'svartalfheim');
        return { pages: [...(extra ? [extra] : []), 'Then you are welcome under our boughs. Mirelle keeps the Prism Library. If proof exists, she will see it.',
                         '(Alfheim is your friend now. Its rival, Svartalfheim, will not stand with you as well.)'] }; };
      const opts = [];
      if (S.cls === 'seer') opts.push({ label: 'Your runes on Mossbrook\'s moss were forged. I\'ve seen the hand.', pick: befriend('...You\'ve seen it too? Then perhaps we are not mad after all.') });
      opts.push({ label: 'A friend. Let me prove you innocent.', pick: befriend() },
        { label: 'Alfheim will answer to Hearthmoor.', pick: (G) => { ally(G.S).alfheim = 'conquer'; G.toast('Alfheim: conquered', 2.2); G.setQuest('alf_take', 1); moodUp(G.S, 'svartalfheim');
            G.alfheim && G.alfheim.onConquer();
            return { pages: ['...I see. Then you will find the Spire barred, and Captain Thorne between you and it.', 'Faelan: "So that\'s what you are. Rangers! To the Spire bridge. Nobody passes."',
                             '(Alfheim stands against you now. The light elves will remember.)'] }; } },
        { label: 'I\'m only passing through.', cancel: true, pick: () => ({ pages: ['Then pass gently. Our light is thin enough already.'] }) });
      return { pages, choice: { id: 'alliance_alfheim', options: opts } };
    }
    if (a === 'befriend' && q.alf_name === 2) {
      const pages = ['Carved cold. A stencil. The same hand. So we were framed, and framed by someone patient.'];
      if (inv.moss_letter) pages.push('And a letter from Mossbrook. With a drawing of a... mushroom? Tell them we accept.');
      pages.push('Alfheim thanks you, and Alfheim does not say that often. Ask my advisers. They keep a list.', 'But proof will not light our wisps. Mirelle has been watching them die. Go to her. Please.');
      return { pages, then: (G) => { G.setQuest('alf_name', 3); G.factions.add('embassy', MERIT.alf_name, 'alf_name'); gold(G, 40);
        flags(G.S).alf_cleared = 1; G.S.evidence = { ...(G.S.evidence || {}), alfheim: 'frost_stencil' };
        if ((G.S.inv || {}).moss_letter) G.factions.add('embassy', MERIT.apology, 'apology'); } };
    }
    if (a === 'befriend' && q.alf_dim === 2) return {
      pages: ['Into the Spire. Into the Vault. Of course it is. Of course it is her.', 'My great-great-grandmother, Sylvaine. Our first queen. She feared the dark so much she began to drink the light.',
              'We sealed her in the Vault, in endless light, so she would sleep fed. If the prisms are cracked, she is waking.',
              'Here is the Spire key. Mirelle will guide you. Put her back to sleep. Please. She was someone\'s grandmother once.',
              'Lumi: "I\'m coming with you. Don\'t argue. I\'m older than your whole village. Ting."'],
      then: (G) => { G.setQuest('alf_dim', 3); G.factions.add('embassy', MERIT.alf_dim, 'alf_dim'); gold(G, 60); G.give('spirekey', 1); G.give('speaklens', 1);
        const ff = flags(G.S); ff.companions = { ...(ff.companions || {}), lumi: 1 }; G.toast('Lumi joins you: a talking wisp companion', 2.8);
        G.setQuest('prismvault', 1); G.alfheim && G.alfheim.lumiJoin(); },
    };
    if (a === 'befriend' && q.prismvault === 2) return {
      pages: ['She\'s asleep? Truly? And the wisps... listen. Listen to them. They\'re singing again.',
              'She said the throne is mine? ...Then perhaps, one day. Not today. Today I am going to cry in a corridor.',
              'Alfheim stands with you, hearth-walker. Our gate, our light, our rangers. Even Thorne, if you ask nicely.',
              'Mirelle has something to teach you. And Nim says there will be a festival. There is always a festival.'],
      then: (G) => { G.setQuest('prismvault', 3); G.factions.add('embassy', MERIT.vault, 'vault'); gold(G, 150); G.give('queen_lantern', 1);
        flags(G.S).alf_resolved = 'befriend'; G.toast('Alfheim is your ally.', 3.0); },
    };
    if (a === 'conquer') return say1(f.alf_dark ? 'You took the Heart. Look at the trees. Every light you see is a light going out.' : 'Say what you came to say, Midgarder. Then go, and take your cold with you.');
    if (q.prismvault === 3) return say1('She sleeps. I went down and sat with her. I told her about the frogs. She\'d have liked the frogs.');
    return say1(night() ? 'The aurora\'s out. When I was small, I thought it was the queen dancing. Now I know better.' : 'The throne stays empty. A regent is a promise to keep the chair warm, not to sit in it.');
  },
  librarian(S) {
    const a = A(S), q = S.quests || {}, f = F_(S), inv = S.inv || {};
    if (a === 'conquer') return { pages: [(inv.blight_spike || inv.frost_stencil) && !f.mirelle_c ? 'You carry proof we\'re innocent. And you came with a sword anyway.' : '(Mirelle keeps her eyes on her lenses.)'], then: (G) => { flags(G.S).mirelle_c = 1; } };
    if (a === 'befriend' && q.alf_name === 1) return GREF.alfheim.lensScene();
    if (a === 'befriend' && q.alf_name === 3 && !q.alf_dim) return {
      pages: ['Our wisps are dimming. One a night, then two. They don\'t die. They go grey, and they stop singing.',
              'There\'s an old wisp in the Wispwood. Lumi. She talks. Rudely, to regents. If anyone knows where light goes, she does.',
              'Relight the dimmed ones in the glowfrog ponds. The frogs sing light back into them. Don\'t ask how. They just croak.'],
      then: (G) => { met('mirelle')(G); G.setQuest('alf_dim', 1); },
    };
    if (q.alf_dim === 1 && f.dm_trail) return { pages: ['The Spire? Lumi\'s sure? Then it\'s the Vault. Then it\'s her. Tell the Regent. I\'ll pack lenses. Lots of lenses.'], then: (G) => G.setQuest('alf_dim', 2) };
    if (q.alf_dim === 1) return say1('The glowfrog ponds. Carry the grey wisps to the frogs, and the frogs will do the rest.');
    if (!(S.met || {}).mirelle) return { pages: ['Oh! Hello. Mind the shelves, the books are glass. Mirelle Glasswing, Prism Library. Do you like lenses?'], then: met('mirelle') };
    if (q.prismvault === 3) return say1('I measured the Heart Prism this morning. It\'s humming. Content. I think that\'s her snoring.');
    if (GREF && GREF.alfheim.wx === 'prismrain') return say1('Prism rain! Everything\'s in three colours. I\'ve been sneezing rainbows all morning.');
    return say1(night() ? 'The library glows at night. I sleep under the desk. Don\'t tell the Regent. She knows.' : 'Light bends, you know. So do people. The trick is finding the right angle.');
  },
  ranger(S) {
    const a = A(S), q = S.quests || {};
    if (!a) return say1('Faelan Thorne, ranger captain. I don\'t like Midgard. Nothing personal. I don\'t like anyone.');
    if (a === 'conquer') return say1('(Faelan turns her back on you. The rangers do the same, one after another.)');
    if (q.prismvault === 3) return say1('You went down there and came back. I\'ve known rangers who wouldn\'t. I\'ve known rangers who didn\'t.');
    return say1(night() ? 'The rangers walk the canopy at night. The aurora makes good light for arrows. And for thinking.' : 'You cleared our name. I\'ll grudgingly admit that\'s useful. Don\'t make me say it twice.');
  },
  ranger_a(S) { return say1(A(S) === 'conquer' ? '(The ranger looks straight through you.)' : 'The Captain says Midgarders are loud. You seem... medium.'); },
  ranger_b(S) { return say1(A(S) === 'conquer' ? '(The ranger\'s hand stays on her bow.)' : 'Night watch is the best watch. The aurora does half the work.'); },
  wispcatcher(S) {
    const a = A(S), q = S.quests || {};
    if (a === 'conquer') return say1('(Nim hides her net behind her back and won\'t look at you.)');
    if (q.alf_dim === 1) return say1('My wisps went grey. All of them. I put them in a jar and sang to them. It didn\'t work. I\'m a bad singer.');
    if (!(S.met || {}).nim) return { pages: ['Shh! There\'s a wisp right... it\'s gone. I\'m Nim. I catch wisps. Well. I chase wisps. Catching\'s harder.'], then: met('nim') };
    return say1('There are nine rare wisps. I\'ve seen four. I\'ve caught none. One day.');
  },
  poolkeeper(S) {
    const a = A(S), q = S.quests || {};
    if (a === 'conquer') return say1('The frogs went quiet when you came in. They know. Frogs always know.');
    if (!(S.met || {}).ferrin) return { pages: ['Mind the frogs. That\'s Duchess, the blue one. She bites. Affectionately. I\'m Ferrin. I tend the pools.'], then: met('ferrin') };
    if (q.alf_dim === 1) return say1('The frogs know how to sing light back. They\'ve been singing all night. Hoarse, poor things.');
    return say1(night() ? 'Night chorus. Best music in the Nine Realms. Don\'t let the bards hear me say that.' : 'Bryony in Ravenhold has one of my frogs, you know. Bloop. Named him herself. Terrible name. Lovely frog.');
  },
  lanternseller(S) {
    const a = A(S), first = !(S.met || {}).saelis;
    return { pages: [a === 'conquer' ? 'Prices went up. For you. Don\'t look at me like that. Look at the trees.'
                     : first ? 'Lanterns! Neon ones, prism ones, and those funny Midgard fish ones. Everyone loves the fish ones.'
                     : 'Every lantern here holds a little wisp-light. Freely given. We ask nicely. That\'s the elf way.'],
             then: (G) => { met('saelis')(G); GREF.alfheim.shopTone(); G.shopUI.show('lumen'); } };
  },
  dwarftrader(S) {
    const a = A(S), f = F_(S);
    if (a === 'befriend') return { pages: ['So you\'ve thrown in with the light-ears. Fine. Anvildeep keeps a ledger too, Midgarder. Don\'t forget it.'], then: (G) => { flags(G.S).brokk_said = 1; } };
    if (a === 'conquer') return say1(f.brokk_cheer ? 'Come see us under the mountain someday. The forges are warm and the welcome\'s warmer. For you.' : 'Ha! Somebody finally put the elves in their place. Anvildeep will drink to you. Loudly.');
    if (!(S.met || {}).brokk) return { pages: ['Brokk Emberlode, Anvildeep. Yes, a dwarf in Alfheim. The elves glare. I glare back. It\'s tradition.'], then: met('brokk') };
    return say1('The elves blame us for half their troubles. We blame them for the other half. Keeps things tidy.');
  },
  elf1(S) { return say1(notC(S, (S.quests || {}).prismvault === 3 ? 'The wisps are singing again. I\'d forgotten how loud they are. I\'d forgotten I liked it.' : 'Another wisp went grey last night. Three streets over. I keep my lantern lit, just in case.')); },
  elf2(S) { return say1(notC(S, 'Mossbrook called us poisoners. Us! We can\'t even poison a slug. We apologise to the slugs.')); },
  elf3(S) { return say1(notC(S, 'A Midgarder. Through the gate. Somebody fetch the Regent. No? Fine. Hello, then.')); },
  elf4(S) { return say1(notC(S, 'The aurora\'s coming in green tonight. Green means luck. Or rain. It\'s usually rain.')); },
});
MARKER_HOOKS.push((id, S) => {
  const F = S.flags || {}, a = (F.alliance || {}).alfheim, q = S.quests || {};
  if (id === 'gatewright' && ((S.ranks || {}).gate || 0) >= 3 && !q.alf_gate) return 'quest_mark';
  if (id === 'gatewright' && ((q.alf_gate === 1 && F.ag_sentinel) || q.alf_gate === 2)) return 'quest_turnin';
  if (id === 'warden' && q.alf_gate === 3 && (F.alliance || {}).vanaheim === 'befriend' && !F.moss_letter) return 'quest_mark';
  if (id === 'regent' && !a) return 'quest_mark';
  if (id === 'regent' && a === 'befriend' && (q.alf_name === 2 || q.alf_dim === 2 || q.prismvault === 2)) return 'quest_turnin';
  if (id === 'librarian' && a === 'befriend' && q.alf_name === 1 && !F.an_lens) return 'quest_mark';
  if (id === 'librarian' && a === 'befriend' && q.alf_name === 1 && F.an_stencil) return 'quest_turnin';
  if (id === 'librarian' && a === 'befriend' && q.alf_name === 3 && !q.alf_dim) return 'quest_mark';
  if (id === 'librarian' && q.alf_dim === 1 && F.dm_trail) return 'quest_turnin';
  return undefined;
});

// ------------------------------------------------------------------ the module
export class Alfheim {
  constructor(G) {
    GREF = G; this.G = G; this.ctx = null; this.area = null; this.t = 0; this.told = {}; this.extra = []; this.spots = [];
    this.lumi = new Lumi(G); this.foes = new AlfFoes(this); this.beams = null; this.wx = 'clear'; this.glareT = 0;
    this.wrap();
  }
  // seams onto other modules, so game.js only carries its attach / detach / update lines: the E / A prompt, interact and
  // tap try Alfheim's interactables first; Lumi + lit rim braziers count as glow light zones; a cast near a dark beam
  // source or a dark brazier lights it; Bifrost's Alfheim seal can be struck with the Keybearer's key (and Svartalfheim's
  // look notes the rival lock); the Vault's Glare trims outgoing damage by 10% for 2 s
  wrap() {
    const G = this.G, me = this;
    if (G.harbor) {
      const p0 = G.harbor.prompt.bind(G.harbor), i0 = G.harbor.interact.bind(G.harbor), t0 = G.harbor.onTap.bind(G.harbor);
      G.harbor.prompt = (...a) => me.prompt() || p0(...a);
      G.harbor.interact = (...a) => me.interact() || i0(...a);
      G.harbor.onTap = (hit, ...a) => me.onTap(hit) || t0(hit, ...a);
    }
    if (G.glow) { const z0 = G.glow.zones.bind(G.glow); G.glow.zones = (...a) => [...z0(...a), ...me.zones()]; }
    if (G.hollows) { const c0 = G.hollows.onCast.bind(G.hollows); G.hollows.onCast = (...a) => { const r = c0(...a); const p = me.ctx && me.ctx.player; if (p) me.spellAt(p.x, p.z); return r; }; }
    if (G.crossing) {
      const l0 = G.crossing.look.bind(G.crossing);
      G.crossing.look = (g) => {
        if (g && g.arch === 'alfheim' && me.strikeSeal()) return true;
        const r = l0(g);
        if (g && g.arch === 'svartalfheim' && ((F_(G.S).rivals || {}).svartalfheim === 'locked') && G.dlg) G.dlg.pages.push('A dwarven notice is nailed over the copper seal: \'No elf-friends.\' Someone has underlined it twice.');
        return r;
      };
    }
    if (G.combat) { const o0 = G.combat.out.bind(G.combat); G.combat.out = (...a) => { const v = o0(...a); return me.glareT > me.t && typeof v === 'number' ? Math.max(1, Math.round(v * 0.9)) : v; }; }
  }
  qs() { return this.G.qs || new URLSearchParams(location.search); }
  open() { const F = this.G.S.flags || {}; return !!(F.alf_gate_open || this.qs().has('alfheim') || (F.alliance || {}).alfheim); }
  fx(name, x, y, z, o) { const E = this.ctx && this.ctx.effects; return E && E.meta.effects[name] ? E.spawn(name, x, y, z, o || {}) : null; }
  gfx(name, x, y, z, o) { const E = this.ctx && this.ctx.gamefx; return E && E.meta.effects[name] ? E.spawn(name, x, y, z, o || {}) : null; }
  keep(fx) { if (fx) this.extra.push({ fx }); return fx; }
  attach(ctx, id) {
    this.ctx = ctx; this.area = id; this.t = 0; this.spots = []; this.extra = []; this.room = null; this.carry = null; this.glareT = 0;
    this.sylSpawned = false; this.told = {}; this.aurora = null; this.lumiNest = null; this.lumiMark = null; this.nestFx = {};
    const G = this.G, S = G.S; S.found = S.found || {}; S.quests = S.quests || {}; S.inv = S.inv || {};
    this.qaPreset();
    this.foes.reset();
    this.prefetchBifrost();
    const conquer = A(S) === 'conquer';
    for (const a of [...LUMENVALE, 'prismvault']) REALM[a] = conquer ? 'gate' : 'embassy';
    if (id === 'bifrost') this.atBifrost(ctx);
    if (LUMENVALE.includes(id)) { this.weatherInit(); if (F_(S).alf_dark) this.darkGrade(ctx); }
    if (id === 'alfheim') this.atSteps(ctx);
    if (id === 'lumen_court') this.atCourt(ctx);
    if (id === 'wispwood') this.atWood(ctx);
    if (id === 'prismvault') this.atVault(ctx);
    this.lumi.attach(ctx, id);
    const f = F_(S);
    if (f.alf_resolved && !f.alf_veyra_seen) setTimeout(() => this.ctx === ctx && !G.dlg && this.veyraBeat(), 2200);
  }
  detach() {
    if (this.beams) { this.beams.dispose(); this.beams = null; }
    this.lumi.detach(); this.foes.dropTether();
    const E = this.ctx && this.ctx.effects, GF = this.ctx && this.ctx.gamefx;
    for (const x of this.extra) {
      if (x.fx) { try { E && E.remove(x.fx); } catch (e) { /* already gone */ } }
      else if (x.gfx) { try { GF && GF.remove(x.gfx); } catch (e) { /* already gone */ } }
      else if (x.isObject3D) { if (x.parent) x.parent.remove(x); }
      else if ('kill' in x) x.kill = true;
    }
    this.extra = []; this.spots = []; this.rims = null; this.gates = null; this.ctx = null; this.area = null; this.carryFx = null; this.aurora = null;
  }
  // QA presets for screenshots + smoke: ?alfq=befriend|dim|lumi|vault|boss|conquer|dark
  qaPreset() {
    const q = this.qs().get('alfq'), S = this.G.S; if (!q || this.qaDone === q) return;
    this.qaDone = q;
    const f = flags(S); S.found = S.found || {};
    const bef = () => { ally(S).alfheim = 'befriend'; f.alf_gate_open = 1; S.quests.alf_gate = 3; S.quests.alf_name = 3; f.alf_veyra_seen = 1; lockRival(S, 'svartalfheim'); };
    if (q === 'befriend') bef();
    if (q === 'dim') { bef(); S.quests.alf_dim = 1; }
    if (q === 'lumi' || q === 'vault' || q === 'boss') { bef(); S.quests.alf_dim = 3; f.dm_lumi = 1; f.dm_trail = 1; for (const k of DW) S.found[k] = 1; f.companions = { ...(f.companions || {}), lumi: 1 }; S.inv.spirekey = 1; S.inv.speaklens = 1; S.quests.prismvault = 1; }
    if (q === 'boss') { for (const k of ['pv_lens1', 'pv_lens2', 'pv_lens3', 'pv_lens2v', 'pv_lens2b', 'pv_lens2r', 'p2_src', 'p4_src', 'p6_src']) S.found[k] = 1; f.pv_warden = 1; }
    if (q === 'conquer' || q === 'dark') { ally(S).alfheim = 'conquer'; f.alf_gate_open = 1; S.quests.alf_gate = 3; S.quests.alf_take = 1; moodUp(S, 'svartalfheim'); }
    if (q === 'dark') { f.alf_dark = 1; f.pv_taken = 1; S.quests.alf_take = 3; S.quests.prismvault = 3; f.alf_resolved = 'conquer'; f.alf_veyra_seen = 1; }
  }
  // ---------------------------------------------------------------- Bifrost: the Frozen Gate
  prefetchBifrost() {
    const G = this.G, put = (sc) => { const gm = (sc.game = sc.game || {}); gm.spawns = gm.spawns || {}; if (!gm.spawns.from_alfheim) gm.spawns.from_alfheim = BF_ARCH.spawn.slice(); };
    if (G.scenes && G.scenes.bifrost) { put(G.scenes.bifrost); return; }
    if (!AREAS_ALF[this.area] || this.fetching || !G.scenes) return;
    this.fetching = true;
    fetch('areas/bifrost/scene.json').then((r) => r.json()).then((sc) => { if (!G.scenes.bifrost) G.scenes.bifrost = sc; put(G.scenes.bifrost); }).catch(() => {}).finally(() => { this.fetching = false; });
  }
  atBifrost(ctx) {
    const S = this.G.S, f = F_(S);
    this.wireGate(ctx);
    if (f.ag_struck && !f.ag_sentinel) setTimeout(() => this.ctx === ctx && this.spawnSentinel(), 300);
    if (A(S) === 'conquer' && f.pv_taken && (S.quests.prismvault || 0) === 2) setTimeout(() => this.ctx === ctx && this.conquerLeave(), 900);
  }
  reopenGate() { if (this.ctx && this.area === 'bifrost') this.wireGate(this.ctx); }
  wireGate(ctx) {
    const gm = ctx.scene.game; if (!gm || !this.open()) return;
    gm.sealed = (gm.sealed || []).filter((g) => g.arch !== 'alfheim');
    gm.portals = gm.portals || [];
    if (!gm.portals.find((p) => p.to === 'alfheim')) gm.portals.push({ fx: 'gate_alfheim', to: 'alfheim', spawn: 'from_bifrost', rect: BF_ARCH.rect.slice(), label: 'Alfheim\'s gate' });
    (gm.spawns = gm.spawns || {}).from_alfheim = gm.spawns.from_alfheim || BF_ARCH.spawn.slice();
    const f = ctx.fx && ctx.fx.gate_alfheim, meta = ctx.gamefx && ctx.gamefx.meta && ctx.gamefx.meta.effects;
    const want = meta && meta.rift_vortex_violet ? 'rift_vortex_violet' : 'rift_vortex';
    if (f && f.name !== want && ctx.gamefx && meta && meta[want]) { ctx.gamefx.remove(f); ctx.fx.gate_alfheim = ctx.gamefx.spawn(want, f.x, f.y, f.z, { duration: Infinity }); }
  }
  strikeSeal() {
    const G = this.G, S = G.S, f = flags(S), q = (S.quests || {}).alf_gate || 0;
    if (q === 1 && (S.inv || {}).thawkey && !f.ag_struck) {
      G.openDialogue({ id: 'sealed_alfheim', name: 'Alfheim\'s gate (frozen)' }, {
        pages: ['(The key bites into the frost. The ice groans... and something inside it stands up.)'],
        then: () => { f.ag_struck = 1; G.save && G.save(); this.spawnSentinel(true); G.refreshMarkers(); } });
      return true;
    }
    if (q === 1 && f.ag_struck && !f.ag_sentinel) { G.toast('The frost sentinel stands between you and the seal!', 2); return true; }
    return false;
  }
  spawnSentinel(poof) {
    const ctx = this.ctx, C = this.G.combat; if (!ctx || !C || !C.ctx) return null;
    if ((C.enemies || []).some((e) => e.sp.id === 'frostsentinel' && e.state !== 'dead')) return null;
    const roles = (ctx.actors && ctx.actors.meta && ctx.actors.meta.roles) || {};
    const role = roles.frostsentinel ? 'frostsentinel' : roles.icegolem ? 'icegolem' : 'golem';   // the 2x sheet once bifrost's spec lists it
    const e = C.spawnEnemy({ id: 'frostsentinel', role, def: 'frostsentinel', pos: [BF_ARCH.pos[0], BF_ARCH.pos[1] + 2.4], once: true }, !!poof);
    if (poof) { this.fx('frost_puff', e.a.x, e.a.y + 0.6, e.a.z + 0.1); this.G.toast('A frost sentinel tears free of the seal!', 2.4); }
    e.onKill = () => { const S = this.G.S; flags(S).ag_sentinel = 1; if ((S.quests.alf_gate || 0) === 1) this.G.setQuest('alf_gate', 2); this.G.toast('The seal cracks wide. Tell Gatewright Halvard.', 2.6); this.G.refreshMarkers(); };
    return e;
  }
  conquerLeave() {
    this.G.openDialogue({ id: 'narr', name: 'Lumenvale' }, { pages: ['(Lumenvale is dark behind you. Only the frogs still glow, and they\'ve stopped singing.)'],
      then: (G2) => { G2.setQuest('prismvault', 3); G2.factions.add('gate', MERIT.vault_c, 'vault_c'); gold(G2, 200); G2.give('sylvaine_crown', 1);
        const f = flags(G2.S); f.alf_dark = 1; f.alf_resolved = 'conquer'; } });
  }
  veyraBeat() {
    const G = this.G, f = flags(G.S), rev = !!f.veyra_revealed, bef = f.alf_resolved === 'befriend';
    const lines = bef ? (rev ? ['You keep mending what I break. It\'s becoming tiresome.', 'Enjoy the festival. Lanterns burn out.'] : ['You sang a hungry queen to sleep instead of killing her. That\'s rarer than you know.', 'Alfheim\'s light is back. I\'ll... remember that.'])
                      : (rev ? ['Another realm in the dark. Thank you. Truly.', 'You\'d make a fine Rift-Breaker. Think on it.'] : ['A whole city of lights, and you turned it off. You\'re doing my work for me, you know.', 'Keep the Heart. It\'ll keep you warm. No one else.']);
    if (bef && !rev && G.S.cls === 'seer') lines.push('(Your runes prickle again: the same cold as the stencil.)');
    lines.push('(She\'s gone before you can answer.)');
    G.openDialogue({ id: 'veyra', name: f.met_veyra ? 'Veyra' : 'A frost-witch in grey-blue' }, { pages: lines, then: () => { f.alf_veyra_seen = 1; } });
  }
  // ---------------------------------------------------------------- interactables (E / A, tap): {pos, r, label, act, show}
  spot(o) { this.spots.push({ r: 1.4, show: () => true, ...o }); }
  nearSpot() {
    const c = this.ctx; if (!c || this.G.dlg) return null;
    let best = null, bd = 1e9;
    for (const s of this.spots) { if (!s.show()) continue; const d = Math.hypot(c.player.x - s.pos[0], c.player.z - s.pos[1]); if (d < s.r && d < bd) { bd = d; best = s; } }
    const m = this.beams && this.beams.near(c.player.x, c.player.z);
    if (m && Math.hypot(c.player.x - m.pos[0], c.player.z - m.pos[1]) < bd) return { label: 'turn the mirror (E / A)', act: () => this.beams.turn(m) };
    return best;
  }
  prompt() { const s = this.nearSpot(); return s ? (typeof s.label === 'function' ? s.label() : s.label) : ''; }
  interact() { const s = this.nearSpot(); if (!s) return false; s.act(); return true; }
  onTap(hit) {
    const c = this.ctx; if (!c || !hit) return false;
    const cand = [...this.spots.filter((s) => s.show()), ...(this.beams ? this.beams.mirrors.filter((m) => !m.fixed && (!m.boss || this.bossOn)).map((m) => ({ pos: m.pos, r: 1.25, act: () => this.beams.turn(m) })) : [])];
    for (const s of cand) {
      if (Math.hypot(hit.x - s.pos[0], hit.z - s.pos[1]) > 0.9) continue;
      if (Math.hypot(c.player.x - s.pos[0], c.player.z - s.pos[1]) < s.r) s.act(); else c.walkTo(s.pos[0], s.pos[1] + 0.9);
      return true;
    }
    return false;
  }
  zones() {
    const out = [...this.lumi.zones()];
    for (const r of this.rims || []) if (r.lit) out.push({ x: r.pos[0], z: r.pos[1], r: 3.2, src: 'brazier' });
    return out;
  }
  spellAt(x, z) {
    if (this.beams && this.beams.spellAt(x, z)) this.G.toast('The source crystal drinks your spell and blazes white!', 2.2);
    for (const r of this.rims || []) if (!r.lit && Math.hypot(x - r.pos[0], z - r.pos[1]) <= 2.6) { this.rimOn(r); this.G.toast('The brazier blazes back to life!', 1.8); }
  }
  look(id, name, pages, then) { this.G.openDialogue({ id, name }, { pages, then }); }
  // ---------------------------------------------------------------- the Glimmer Steps
  atSteps(ctx) {
    const G = this.G, S = G.S, f = flags(S), al = (ctx.scene.game || {}).alf || {};
    if (!f.alf_seen) {
      f.alf_seen = 1;
      setTimeout(() => {
        if (this.ctx !== ctx || G.qaStill) return;
        G.toast('ALFHEIM · Lumenvale, city of the light elves', 3.2);
        if (!G.dlg) this.look('narr', 'Lumenvale', ['(Silverbark trees taller than towers. Vines of violet light. Glow orbs drifting like slow bubbles.)',
          '(Below the bridges, dark pools shine blue, and somewhere, a thousand frogs are singing.)',
          '(But here and there, a wisp hangs grey and silent in the branches, like a lamp someone forgot to light.)']);
      }, 1500);
    }
    if (A(S) === 'befriend' && f.brokk_said) f.brokk_left = 1;
    if (f.brokk_left) { const b = ctx.npc('dwarftrader'); if (b) ctx.removeNpc(b); }
    if (A(S) === 'conquer' && (S.met || {}).brokk) f.brokk_cheer = 1;
    if (al.pond) this.pondSpot(al.pond.pos, 'Ferrin\'s glow-pool');
  }
  shopTone() {
    const conquer = A(this.G.S) === 'conquer';
    SHOPS.lumen.gear = { n: 3, rar: conquer ? [0, 0, 0] : [1, 1, 2] };
    SHOPS.lumen.gems = conquer ? [] : (this.G.S.quests.prismvault === 3 ? ['moon_opal', 'prism_core'] : ['moon_opal']);
  }
  // ---------------------------------------------------------------- the Moonlit Court
  atCourt(ctx) {
    const G = this.G, S = G.S, gm = ctx.scene.game || {}, al = gm.alf || {};
    const door = (gm.portals || []).find((p) => p.to === 'prismvault');   // the Spire door: sealed until you hold the Spire key
    if (door && !S.inv.spirekey && !this.qs().has('alfvault')) { this.spire = door; gm.portals = gm.portals.filter((p) => p !== door); }
    if (!door && this.spire && S.inv.spirekey) gm.portals.push(this.spire);
    if (al.door) this.spot({ pos: al.door.pos, r: 1.8, label: 'the Prism Spire door is sealed (E / A to look)', show: () => !S.inv.spirekey,
      act: () => this.look('spire', 'The Prism Spire door', ['A tall door of violet glass, sealed by the Regent\'s key. Cold air seeps under it, and a faint sound, like someone humming.']) });
    if (this.spots.length && !this.courtOnce) this.courtOnce = true;
    if (al.lens) this.spot({ pos: al.lens.pos, r: 1.8, label: 'the lens table (E / A)', act: () => this.G.openDialogue({ id: 'librarian', name: 'Mirelle Glasswing' }, this.lensScene()) });
    if (al.throne) this.spot({ pos: al.throne, r: 1.6, label: 'the Empty Throne (E / A to look)', act: () => this.look('throne', 'The Empty Throne', ['Violet glass under a dust sheet. Four hundred years, and nobody has sat in it.']) });
    if (al.pool) this.spot({ pos: al.pool.pos, r: 1.6, label: 'the moon-pool (E / A to look)', act: () => this.look('moonpool', 'The moon-pool', ['Still water, black as a mirror. The aurora moves in it even when the sky is clear.']) });
    if (A(S) === 'conquer' && (S.quests.alf_take || 0) === 1) setTimeout(() => this.ctx === ctx && this.rangerPosts(ctx, al), 200);
  }
  lensScene() {
    const S = this.G.S, f = F_(S), inv = S.inv || {};
    if (A(S) !== 'befriend' || (S.quests.alf_name || 0) !== 1) return { pages: ['(The great lens bends the library\'s light into a slow violet ring on the table.)'] };
    const done = (G) => { flags(G.S).an_lens = 1; G.refreshMarkers(); G.setQuest('alf_name', 1); };
    if (!f.an_lens) return inv.blight_spike ? {
      pages: ['A frost-iron spike? From Vanaheim? Lay it on the lens. Gently. Iron makes the glass grumpy.', '(Violet light pours through the lens. The runes on the spike glow, but their edges stay dark and rimed.)',
              'See that? Our runes are burned with light. These were carved. Cold. By someone who\'s never lit a rune in their life.', 'That\'s half a proof. Somebody made these. If they practised, they practised near here. Look for dead vines.'],
      then: done } : {
      pages: ['Vanaheim says our runes are on their moss. Fine. Runes can be copied. But copying takes practice.', 'Whoever did it would need a quiet place, a cold one. Vines die near frost-iron. Look for a ring of dead vines.'],
      then: done };
    if (f.an_stencil) return {
      pages: ['(The stencil and the spike lie side by side. Under the lens, the cut marks line up perfectly.)', 'Same tool. Same cold hand. This isn\'t Alfheim\'s work. It isn\'t even Midgard\'s.',
              'Take it to the Regent. And... thank you. We\'ve been shouting \'it wasn\'t us\' at a frozen gate for months.'],
      then: (G) => G.setQuest('alf_name', 2) };
    return { pages: ['A ring of dead vines. Somewhere cold, somewhere quiet. The Wispwood, I\'d wager. Over the glass bridge.'] };
  }
  onConquer() {
    const ctx = this.ctx; if (!ctx || this.area !== 'lumen_court') return;
    setTimeout(() => { if (this.ctx === ctx) this.rangerPosts(ctx, (ctx.scene.game || {}).alf || {}); }, 400);
  }
  rangerPosts(ctx, al) {
    const G = this.G, S = G.S, C = G.combat; if (!C || !C.ctx || this.postsUp) return;
    this.postsUp = ctx;
    for (const id of ['ranger', 'ranger_a', 'ranger_b']) { const a = ctx.npc(id); if (a) ctx.removeNpc(a); }
    const posts = al.posts || [[5.0, -1.4], [7.2, -2.6], [8.6, -4.2]];
    const roles = ctx.actors.meta.roles || {}, role = roles.lightranger ? 'lightranger' : roles.ranger ? 'ranger' : 'skeleton';
    const n3 = () => found(S, ['pc_r1', 'pc_r2', 'pc_r3']);
    posts.forEach(([x, z], i) => {
      const id = `pc_r${i + 1}`; if (S.found[id]) return;
      let left = 2;
      for (const ox of [-0.6, 0.6]) {
        const e = C.spawnEnemy({ id: `${id}_${ox > 0 ? 1 : 0}`, role, def: 'lightranger', pos: [x + ox, z], once: true }, false);
        e.onKill = () => { if (--left <= 0) { S.found[id] = 1; G.toast(`Ranger post broken. ${n3()}/3`, 2); G.setQuest('alf_take', 1); if (n3() === 3) this.faelanDuel(); } };
      }
    });
    if (!this.told.posts) { this.told.posts = 1; G.toast('Faelan: "Rangers, hold the bridge!"', 2.4); }
    if (n3() === 3 && !F_(S).pc_faelan) this.faelanDuel();
  }
  faelanDuel() {
    const C = this.G.combat, ctx = this.ctx; if (!C || !ctx || this.faelanUp) return;
    this.faelanUp = true;
    const roles = ctx.actors.meta.roles || {}, role = roles.lightranger ? 'lightranger' : 'skeleton';
    C.spawnEnemy({ id: 'faelan', role, def: 'faelan', pos: [7.6, -3.6], once: true, noLoot: true }, true);
    this.G.toast('Faelan: "You want the key? Earn it. I\'ll make you sweat for every step."', 2.8);
  }
  onYield(e) {
    const G = this.G, C = G.combat;
    if (C && e.state !== 'dead') C.kill(e, true);
    G.openDialogue({ id: 'ranger', name: 'Captain Faelan Thorne' }, { pages: ['Enough. Take it. Take the key. Whatever you find down there, you woke it, not us.'],
      then: (G2) => { flags(G2.S).pc_faelan = 1; G2.give('spirekey', 1); G2.setQuest('alf_take', 2); const gm = this.ctx && this.ctx.scene.game; if (gm && this.spire && !gm.portals.includes(this.spire)) gm.portals.push(this.spire); } });
  }
  // ---------------------------------------------------------------- the Wispwood (+ Ferrin's pool on the Steps)
  pondSpot(pos, name) {
    this.spot({ pos, r: 2.4, label: () => (this.carry ? `${name}: let the frogs sing the grey wisp bright (E / A)` : `${name} (E / A to look)`),
      act: () => {
        if (this.carry) return this.relight(pos);
        this.look('pond', name, ['Glowfrogs in blue, violet and red sit on the lily pads, throats glowing as they sing. "Prrrp."']);
        if (this.lumi.on) setTimeout(() => this.lumi.bark('Hello, frogs! (The frogs sing back. Lumi glows a little brighter.)', 'pond'), 400);
      } });
  }
  atWood(ctx) {
    const G = this.G, S = G.S, f = flags(S), al = (ctx.scene.game || {}).alf || {};
    const dim = (S.quests.alf_dim || 0) === 1;
    for (const [, x, z] of al.ponds || []) this.pondSpot([x, z], 'A glowfrog pond');
    for (const [id, x, z] of al.nests || []) {
      if (!S.found[id] && dim) this.nestFx[id] = this.keep(this.fx('lumi_dim', x, ctx.heightAt(x, z) + 0.9, z + 0.05, { duration: 1e9 }));
      this.spot({ pos: [x, z], r: 1.5, show: () => (S.quests.alf_dim || 0) === 1 && !!f.dm_lumi && !S.found[id] && !this.carry,
        label: 'a dimmed wisp, grey in its nest (E / A to carry it)', act: () => this.carryWisp(id, x, z) });
    }
    if (al.scar) {
      this.spot({ pos: al.scar, r: 1.8, label: 'the frost scar (E / A to search)', show: () => !f.an_stencil, act: () => {
        const pages = ['A ring of dead vines, white with frost, around a flat stone. The frost hasn\'t melted in weeks.', 'Under the stone: a thin frost-iron plate with Alfheim runes cut clean through it. A stencil.'];
        if (S.cls === 'seer') pages.push('(Your runes recognise the hand. The same cold patience as the spike, the tongs, the snuffer.)');
        if (S.cls === 'grovekeeper') pages.push('(The dead vines whisper to you: cold hands, a grey-blue cloak, a long time kneeling here.)');
        this.look('clue', 'The frost scar', pages, (G2) => { G2.give('frost_stencil', 1); flags(G2.S).an_stencil = 1; G2.S.evidence = { ...(G2.S.evidence || {}), alfheim: 'frost_stencil' };
          G2.toast('Found: a frost-iron rune stencil. Evidence.', 2.6); if ((G2.S.quests.alf_name || 0) === 1) G2.setQuest('alf_name', 1); G2.refreshMarkers(); });
      } });
      if (!f.an_stencil && (S.quests.alf_name || 0) === 1) this.extra.push({ gfx: this.gfx('quest_mark', al.scar[0], ctx.heightAt(...al.scar) + 1.4, al.scar[1] + 0.05, { duration: 1e9 }) });
    }
    // Lumi in her nest (befriend, before she joins), or one big grey wisp that flees (conquer)
    const lp = al.lumi || [-0.4, 1.6], joined = !!(f.companions || {}).lumi;
    if (!joined && A(S) !== 'conquer' && (S.quests.alf_dim || 0) >= 1) {
      this.nestLumi(ctx, lp);
      if (!f.dm_lumi) this.lumiMark = this.gfx('quest_mark', lp[0], ctx.heightAt(lp[0], lp[1]) + 2.0, lp[1] + 0.05, { duration: 1e9 });
      this.spot({ pos: lp, r: 1.6, label: 'the grey old wisp (E / A to talk)', show: () => !f.dm_lumi && (S.quests.alf_dim || 0) === 1, act: () => this.findLumi() });
      this.spot({ pos: lp, r: 1.6, label: 'Lumi (E / A to talk)', show: () => !!f.dm_lumi && !(f.companions || {}).lumi, act: () => this.G.openDialogue({ id: 'lumi', name: 'Lumi' }, {
        pages: [found(S, DW) >= 5 ? 'Lumi: "Ting-ting! Bright again! See the thread? The light\'s going up. To the Spire."' : 'Lumi: "The frogs. Carry them to the frogs. One at a time, they\'re shy."'] }) });
    }
    if (A(S) === 'conquer' && !joined) this.spot({ pos: lp, r: 2.6, label: 'a big grey wisp (E / A)', show: () => !this.told.flee,
      act: () => { this.told.flee = 1; this.look('narr', 'The Wispwood', ['(A big grey wisp with two dim eyes sees you, and darts away into the dark.)']); } });
  }
  nestLumi(ctx, lp) {
    const bright = found(this.G.S, DW) >= 5, y = ctx.heightAt(lp[0], lp[1]);
    if (this.lumiNest) { try { ctx.effects.remove(this.lumiNest); } catch (e) { /* gone */ } }
    this.lumiNest = this.keep(this.fx(bright ? 'lumi_wisp' : 'lumi_dim', lp[0], y + 1.1, lp[1] + 0.05, { duration: 1e9 }));
    if (this.lumiLight) this.lumiLight.kill = true;
    this.lumiLight = ctx.addGlow ? ctx.addGlow(lp[0], y, lp[1], { color: bright ? '#5ac8ff' : '#9c8e7a', intensity: bright ? 5.5 : 1.6, range: bright ? 4.2 : 2, lift: 1.1 }) : null;
    if (this.lumiLight) this.extra.push(this.lumiLight);
    if (bright) this.trail(ctx, lp);
  }
  findLumi() {
    this.G.openDialogue({ id: 'lumi', name: 'Lumi' }, {
      pages: ['(A grey wisp, bigger than most, curls in the bottom of the nest. It flickers. Two dim eyes open.)',
              'Lumi: "Ting. Oh. A warm one. You smell like hearth and spring water. Nice. I\'m... very tired."',
              'Lumi: "Something\'s drinking us. From under the city. I know that thirst. It drank me first, long ago."',
              'Lumi: "Help the others first. Frogs can sing us bright. Then I\'ll show you where the light goes."'],
      then: (G) => { flags(G.S).dm_lumi = 1; if (this.lumiMark && this.ctx) { this.ctx.gamefx.remove(this.lumiMark); this.lumiMark = null; } G.setQuest('alf_dim', 1); } });
  }
  carryWisp(id, x, z) {
    const ctx = this.ctx; this.carry = id;
    const nf = this.nestFx[id]; if (nf) { try { ctx.effects.remove(nf); } catch (e) { /* gone */ } this.nestFx[id] = null; }
    this.carryFx = this.fx('lumi_dim', x, ctx.heightAt(x, z) + 1.0, z + 0.05, { duration: 1e9 });
    this.G.toast('The grey wisp drifts after you. Find a glowfrog pond.', 2.2);
  }
  relight(pos) {
    const G = this.G, S = G.S, ctx = this.ctx, id = this.carry; this.carry = null;
    if (this.carryFx) { try { ctx.effects.remove(this.carryFx); } catch (e) { /* gone */ } this.carryFx = null; }
    S.found[id] = 1;
    const y = ctx.heightAt(pos[0], pos[1]);
    this.fx('beam_hit', pos[0], y + 0.8, pos[1] + 0.05); this.fx('sparkle_burst', pos[0], y + 0.2, pos[1] + 0.05);
    if (ctx.addGlow) ctx.addGlow(pos[0], y, pos[1], { color: '#5ac8ff', intensity: 8, range: 4, life: 2.4, lift: 0.8 });
    const n = found(S, DW);
    G.toast(`The frogs sing, and the wisp flares blue-violet and flies home. ${n}/5`, 2.4);
    G.setQuest('alf_dim', 1);
    if (n >= 5) setTimeout(() => {
      if (this.ctx !== ctx) return;
      G.openDialogue({ id: 'lumi', name: 'Lumi' }, { pages: ['Lumi: "Ting-ting! Bright again! See the thread? The light\'s going up. To the Spire."'] });
      if (this.area === 'wispwood') this.nestLumi(ctx, (ctx.scene.game.alf || {}).lumi || [-0.4, 1.6]);
    }, 1200);
  }
  // the thread of drained light: dotted violet marks from the central nest toward the root stair (on to the Spire door)
  trail(ctx, from) {
    if (this.trailOn === ctx) return; this.trailOn = ctx;
    const sp = (ctx.scene.game.spawns || {}).from_steps || [12.2, -1.9], to = [sp[0], sp[1]], n = 14;
    for (let i = 1; i < n; i++) {
      const u = i / n, x = from[0] + (to[0] - from[0]) * u, z = from[1] + (to[1] - from[1]) * u + Math.sin(u * 6) * 0.4;
      this.keep(this.fx('lumi_mark', x, ctx.heightAt(x, z) + 0.03, z, { duration: 1e9 }) || this.fx('violet_pool', x, ctx.heightAt(x, z) + 0.03, z, { duration: 1e9 }));
    }
  }
  lumiJoin() { if (this.ctx && !this.lumi.on && this.lumi.joined()) this.lumi.attach(this.ctx, this.area); }
  // ---------------------------------------------------------------- the Prism Vault
  atVault(ctx) {
    const G = this.G, S = G.S, f = flags(S), gm = ctx.scene.game || {}, al = gm.alf || {};
    if ((S.quests.alf_take || 0) === 2) {
      G.setQuest('alf_take', 3); G.factions.add('gate', MERIT.claim, 'claim'); gold(G, 80); G.setQuest('prismvault', 1);
      setTimeout(() => this.ctx === ctx && this.look('narr', 'The Prism Spire', ['(The glass door swings inward. Cold air rises from below, and a faint sound, like someone humming.)']), 600);
    }
    if (!S.quests.prismvault) G.setQuest('prismvault', 1);
    const me = this;
    this.beams = gm.beams ? new Beams(G, ctx, gm.beams, {
      found: (id) => !!S.found[id], setFound: (id) => { S.found[id] = 1; },
      onLit: (rc) => me.onLens(rc),
      onBeamHit: (e, col) => me.foes.onBeamHit(e, col),
      targets: () => (G.combat && G.combat.ctx ? G.combat.alive().map((e) => ({ x: e.a.x, z: e.a.z, r: Math.max(0.45, e.D.r || 0.3), ref: e })) : []),
      wall: (x, z) => { const h = ctx.collide ? ctx.collide.height(x, z) : 0; return h === null || h > 0.9; },
    }) : null;
    if (this.qs().get('beams') === 'solve' && this.beams) setTimeout(() => this.beams && this.beams.solve(), 300);
    // sealed doors (violet glass grilles) + the light bridge over P7's chasm
    this.gates = {};
    for (const [id, r] of Object.entries(al.gates || {})) this.gates[id] = { id, rect: r, open: false, blocked: false };
    this.syncGates();
    if (al.illusory) this.carve(al.illusory);
    if (al.frost) this.spot({ pos: al.frost, r: 1.6, label: 'frost on a cracked prism (E / A to look)', act: () => this.look('frost', 'A cracked prism', ['Frost on glass, deep inside the Vault. Nobody up there could have done this.']) });
    const ML = [['A young queen laughing in a nursery under one bright wisp. It sits on her shoulder like a pet.', '...That\'s me. I was smaller. She was too. I thought she hung the moon.'],
                ['The queen alone in a dark room, eyes wide, holding a wisp to her lips. The wisp is going grey.', 'That\'s me too. Going grey. She was so scared of the dark. She never meant to be hungry.'],
                ['Elves carry great prisms down a stair. The queen sleeps in a crystal, smiling, in a rain of light.', 'They put her to bed with all the lights on. That\'s kind. I think that\'s kind.']];
    (al.murals || []).forEach(([id, x, z], i) => this.spot({ pos: [x, z], r: 1.6, label: 'a mural (E / A to look)', act: () => {
      const pages = [ML[i % 3][0]];
      if (i === 2 && S.cls === 'seer') pages.push('(The crystal in the mural has no cracks. The cracks you passed are new, and rimed.)');
      if (this.lumi.on) pages.push(`Lumi: "${ML[i % 3][1]}"`);
      this.look('mural', 'A mural', pages, (G2) => { G2.S.found[id] = 1; });
    } }));
    if (al.reliquary) this.spot({ pos: al.reliquary, r: 1.5, label: 'the reliquary (E / A to open)', show: () => !S.found.pv_reliquary,
      act: () => { S.found.pv_reliquary = 1; gold(G, 60); G.give('prism_glass', 1); this.fx('sparkle_burst', al.reliquary[0], ctx.heightAt(...al.reliquary) + 0.4, al.reliquary[1] + 0.05); } });
    if (al.heart) {
      this.spot({ pos: al.heart, r: 2.8, label: () => (A(S) === 'conquer' ? 'the Heart Prism: take its core (E / A)' : 'the Heart Prism: reseal it (E / A)'), show: () => !!f.pv_boss && !f.pv_sealed && !f.pv_taken, act: () => this.heartOutro() });
      this.spot({ pos: al.heart, r: 2.8, label: 'the Heart Prism (E / A to look)', show: () => !!f.sylvaine_sleeps, act: () => this.look('heart', 'The Heart Prism', ['(The Heart Prism hums. Under the light, someone turns over in her sleep.)']) });
    }
    // P8's rim braziers: lit until Sylvaine drinks them (spells relight them)
    this.rims = (al.rims || []).map((pos) => ({ pos, lit: false, fx: [], light: null }));
    for (const r of this.rims) this.rimOn(r, true);
    this.bossOn = false;
  }
  bossBeams(on) { this.bossOn = on; if (this.beams) { this.beams.bossOn = on; this.beams.dirty = true; } }
  rimOn(r, quiet) {
    const ctx = this.ctx; if (!ctx || r.lit) return;
    const [x, z] = r.pos, y = ctx.heightAt(x, z);
    r.fx = [this.fx('coldfire_flame', x, y + 0.86, z + 0.04, { duration: 1e9 }), this.fx('violet_pool', x, y + 0.02, z + 0.04, { duration: 1e9 })].filter(Boolean);
    r.light = ctx.addGlow ? ctx.addGlow(x, y, z, { color: V, intensity: 8, range: 4.6, lift: 1.1, fadeIn: quiet ? 0.01 : 0.3 }) : null;
    r.lit = true;
  }
  rimOff(r, drunk) {
    const E = this.ctx && this.ctx.effects;
    for (const f of r.fx) { try { E && E.remove(f); } catch (e) { /* gone */ } }
    if (r.light) r.light.kill = true;
    r.fx = []; r.light = null; r.lit = false;
    if (drunk && this.ctx) { this.fx('drain_nova', r.pos[0], this.ctx.heightAt(...r.pos) + 0.04, r.pos[1]); this.G.toast('Sylvaine drinks a brazier\'s light. The dark creeps closer.', 2.2); }
  }
  onLens() {
    const G = this.G, S = G.S, n = found(S, ['pv_lens1', 'pv_lens2', 'pv_lens3']);
    G.toast(`The great lens flares! ${n}/3`, 2.4); G.audio && G.audio.sfx && G.audio.sfx('quest');
    this.syncGates();
    if (n === 3) G.toast('All three lenses aligned: a bridge of light forms over the chasm.', 3);
    G.setQuest('prismvault', S.quests.prismvault || 1); G.save && G.save();
  }
  gateOpen(id) {
    const S = this.G.S;
    if (id === 'p2_door') return !!S.found.pv_lens1;
    if (id === 'p4_door') return !!S.found.pv_lens2;
    if (id === 'p6_door') return !!S.found.pv_lens3;
    if (id === 'p7_bridge') return found(S, ['pv_lens1', 'pv_lens2', 'pv_lens3']) === 3;
    return true;
  }
  syncGates() {
    for (const g of Object.values(this.gates || {})) {
      const want = this.gateOpen(g.id);
      if (want && !g.open) this.openRect(g); else if (!want && !g.blocked) this.closeRect(g);
    }
  }
  cells(rect, pad = 0) {
    const c = this.ctx.collide, out = []; if (!c) return out;
    const i0 = Math.floor((rect[0] - pad - c.ox) / c.cell), i1 = Math.floor((rect[2] + pad - c.ox) / c.cell);
    const j0 = Math.floor((rect[1] - pad - c.oz) / c.cell), j1 = Math.floor((rect[3] + pad - c.oz) / c.cell);
    for (let j = Math.max(0, j0); j <= Math.min(c.h - 1, j1); j++) for (let i = Math.max(0, i0); i <= Math.min(c.w - 1, i1); i++) out.push([i, j, j * c.w + i]);
    return out;
  }
  // re-derive the nav grid around a changed rect with the Nav constructor's own rule (engine/nav.js)
  renav(rect) {
    const ctx = this.ctx, c = ctx.collide, nav = ctx.nav; if (!c || !nav) return;
    const rc = Math.ceil(nav.r / c.cell);
    for (const [i, j, k] of this.cells(rect, nav.r + c.cell * 2)) {
      const v = c.d[k]; if (v === -32768) { nav.ok[k] = 0; continue; }
      let good = true;
      for (let dj = -rc; dj <= rc && good; dj++) for (let di = -rc; di <= rc; di++) {
        if (di * di + dj * dj > (rc + 0.5) * (rc + 0.5)) continue;
        const ii = i + di, jj = j + dj;
        if (ii < 0 || jj < 0 || ii >= c.w || jj >= c.h) { good = false; break; }
        const u = c.d[jj * c.w + ii]; if (u === -32768 || Math.abs(u - v) > c.maxStep * 160) { good = false; break; }
      }
      nav.ok[k] = good ? 1 : 0;
    }
    if (this.G.combat) this.G.combat.navBig = null;
  }
  closeRect(g) {
    const c = this.ctx.collide; if (!c) return;
    g.save = this.cells(g.rect).map(([, , k]) => [k, c.d[k]]);
    for (const [k] of g.save) c.d[k] = -32768;
    this.renav(g.rect); g.blocked = true; g.open = false;
    if (g.id !== 'p7_bridge') this.grille(g); else this.bridgeFx(g, false);
  }
  openRect(g) {
    const c = this.ctx.collide; if (!c) return;
    const was = g.blocked;
    if (g.save) for (const [k, v] of g.save) c.d[k] = v;
    this.renav(g.rect); g.blocked = false; g.open = true;
    for (const m of g.meshes || []) if (m.parent) m.parent.remove(m);
    g.meshes = [];
    if (g.id === 'p7_bridge') this.bridgeFx(g, true);
    else if (was) { const [x0, z0, x1, z1] = g.rect; this.fx('prism_pop', (x0 + x1) / 2, this.ctx.heightAt((x0 + x1) / 2, (z0 + z1) / 2) + 0.8, (z0 + z1) / 2 + 0.1); }
  }
  carve(rect) {   // the illusory mirror-wall (P4 -> P3): its glass doesn't stop you
    const c = this.ctx.collide; if (!c) return;
    const base = c.height(rect[0] - 0.6, (rect[1] + rect[3]) / 2) ?? c.height(rect[2] + 0.6, (rect[1] + rect[3]) / 2) ?? 0;
    for (const [, , k] of this.cells(rect)) c.d[k] = Math.round(base * 100);
    this.renav(rect);
    this.spot({ pos: [rect[0] - 0.7, (rect[1] + rect[3]) / 2], r: 1.4, label: 'a mirror that doesn\'t show your reflection (E / A)', show: () => !this.told.illusory,
      act: () => { this.told.illusory = 1; this.look('mirror', 'A tall mirror', ['It shows the hall behind you, the lamps, the floor... but not you.', '(Your hand goes straight through the glass.)']); } });
  }
  grille(g) {
    const sharp = this.ctx.effects && this.ctx.effects.sharp; if (!sharp) return;
    const ctx = this.ctx;
    import('three').then((THREE) => {
      if (this.ctx !== ctx || g.open) return;
      const [x0, z0, x1, z1] = g.rect, y = ctx.heightAt((x0 + x1) / 2, (z0 + z1) / 2 + 1.2);
      const mat = new THREE.MeshBasicMaterial({ color: new THREE.Color(V) }), hi = new THREE.MeshBasicMaterial({ color: new THREE.Color('#d4a8ff') });
      g.meshes = [];
      const n = 7, zc = (z0 + z1) / 2;
      for (let i = 0; i <= n; i++) { const bar = new THREE.Mesh(new THREE.BoxGeometry(0.07, 1.9, 0.07), mat); bar.position.set(x0 + (x1 - x0) * i / n, y + 0.95, zc); sharp.add(bar); g.meshes.push(bar); this.extra.push(bar); }
      const top = new THREE.Mesh(new THREE.BoxGeometry(x1 - x0, 0.09, 0.09), hi); top.position.set((x0 + x1) / 2, y + 1.9, zc); sharp.add(top); g.meshes.push(top); this.extra.push(top);
    });
  }
  bridgeFx(g, on) {
    const ctx = this.ctx; for (const f of g.fx || []) { try { ctx.effects.remove(f); } catch (e) { /* gone */ } }
    g.fx = [];
    if (!on) return;
    const [x0, z0, x1, z1] = g.rect, xc = (x0 + x1) / 2;
    for (let z = z0 + 0.4; z < z1; z += 1.1) { const f = this.fx('violet_pool', xc, ctx.heightAt(xc, z) + 0.03, z, { duration: 1e9 }); if (f) g.fx.push(f); }
    if (ctx.addGlow && !g.glow) { g.glow = ctx.addGlow(xc, ctx.heightAt(xc, (z0 + z1) / 2), (z0 + z1) / 2, { color: V, intensity: 6, range: 5, lift: 0.6 }); this.extra.push(g.glow); }
  }
  // Mirelle's speaking lens + Lumi, room by room (script 6.3)
  roomLine(room) {
    const S = this.G.S, bef = A(S) === 'befriend' && S.inv.speaklens;
    const M = { P0: 'Can you hear me? Good. Light the stair brazier. The Vault likes visitors who bring their own light.', P1: 'Those are prism shards. Loose bits of the Vault. They fire whatever light they\'ve swallowed. Duck.',
      P2: 'The first lens! Turn the mirrors (E / A) and send the sunbeam into the lens. Think like light. Lazy and straight.', P3: 'A glowfrog grotto, down here? Oh, the frogs have been singing to her. For four hundred years. Bless them.',
      P4: 'The splitter breaks white light into three. Violet, blue and red. Match each colour to its lens.', P5: 'The murals. I\'ve only seen sketches. Look at them for me? Slowly. I\'m taking notes.',
      P6: 'The Hall of Reflections. Trust the floor, not the walls. Mirrors lie. Floors are honest.', P7: 'All three lenses aligned! The bridge should hold now. Should. Walk lightly. Lighter than that.',
      P8: 'I\'m right here. Well, I\'m up here. But I\'m right here. Put her back to sleep.' };
    const Lm = { P0: 'Ting. It smells like old dust and older light. I remember it.', P1: 'The cracks are frosty. Who freezes glass? Rude.', P2: 'Try the mirror by the pillar. No, the other pillar.',
      P3: 'Ting? That mirror doesn\'t show me. I always show up in mirrors. I\'m very bright. Walk through it.', P4: 'That big crystal fellow is not happy to see us.',
      P6: 'That one\'s wearing your face. Badly. Your nose is better.', P7: 'She\'s close. That humming. It\'s the song she hummed under me in the nursery.' };
    const el = document.getElementById('say');
    if (bef && M[room] && el) { el.innerHTML = `<b>Mirelle (speaking lens)</b> — ${M[room]}`; el.hidden = false; const tok = (this.lensTok = (this.lensTok || 0) + 1); setTimeout(() => { if (this.lensTok === tok) el.hidden = true; }, 4600); }
    if (this.lumi.on && Lm[room]) setTimeout(() => this.ctx && this.lumi.bark(Lm[room], 'room_' + room), bef && M[room] ? 4800 : 600);
    if (room === 'P7' && !this.told.hum) { this.told.hum = 1; setTimeout(() => this.ctx && this.G.toast('(Something below is humming. The light bends toward it like grass in wind.)', 3), 1200); }
  }
  vaultTick() {
    const ctx = this.ctx, G = this.G, S = G.S, f = flags(S), p = ctx.player, al = (ctx.scene.game || {}).alf || {}, C = G.combat;
    const room = Object.entries(al.rooms || {}).find(([, r]) => p.x >= r[0] && p.x <= r[2] && p.z >= r[1] && p.z <= r[3]);
    const rid = room ? room[0] : this.room;
    if (rid !== this.room) { this.room = rid; if (rid && !this.told['room_' + rid]) { this.told['room_' + rid] = 1; this.roomLine(rid); } }
    // P1 Glare: light leaking from a frost-cracked prism (-10% damage for 2 s)
    for (const [x, z] of al.leaks || []) if (Math.hypot(p.x - x, p.z - z) < 1.0) { if (this.glareT < this.t) G.toast('Glare! The leaking light dazzles you (-10% damage).', 1.4); this.glareT = this.t + 2; }
    if (!C || !C.ctx) return;
    // P5 -> P6: an ambush on the way out of the mural hall
    if (!this.told.ambush && p.z < -13.4 && p.z > -15.5 && Math.abs(p.x) < 6) {
      this.told.ambush = 1;
      for (const [i, ox] of [[0, -3.0], [1, 3.0]]) C.spawnEnemy({ id: `pv_amb${i}`, role: 'mirrorduelist', pos: [ox, -11.4], once: true }, true);
      if (A(S) === 'conquer') for (const [i, ox] of [[0, -4.4], [1, 4.4]]) C.spawnEnemy({ id: `pv_ambr${i}`, role: 'lightranger', pos: [ox, -7.0], once: true }, true);
      G.toast('Mirror Duelists step out of the murals!', 2);
    }
    // P6: your reflection steps out of the glass (the generic duelist stands in for the hero palette-swap)
    if (!this.told.reflection && p.z < -20.4 && p.z > -27) {
      this.told.reflection = 1;
      C.spawnEnemy({ id: 'pv_you', role: 'mirrorduelist', def: 'mirroryou', pos: [p.x > 0 ? -2.0 : 2.0, -22.4], once: true }, true);
      G.toast('Your reflection steps out of the glass!', 2.2);
    }
    if (al.veyra && !f.alf_veyra && !G.dlg && Math.hypot(p.x - al.veyra[0], p.z - al.veyra[1]) < 2.4) {
      f.alf_veyra = 1;
      const rev = !!f.veyra_revealed;
      const pages = rev ? ['I only cracked the lid. Hunger did the rest. Put her back, if you think you\'re clever enough.', 'Or don\'t. A dark Alfheim suits me very well.', '(The mirror frosts over and cracks. Her laugh hangs in the cold air a moment longer.)']
                        : ['The prisms are cracking all across the Nine. I can\'t hold them all. I\'m so glad someone came.', 'Mind the queen. Hunger never sleeps as deep as it pretends.', '(The mirror frosts over, white edge to white edge, and cracks. She\'s gone.)'];
      if (!rev && S.cls === 'seer') pages.splice(2, 0, '(Your runes flinch. The frost on this glass is the frost on the stencil. The same cold hand.)');
      this.look('veyra', f.met_veyra ? 'Veyra' : 'A frost-witch in grey-blue', ['(One mirror shows a woman in grey-blue standing behind you. When you turn, she\'s only in the glass.)', ...pages]);
    }
    // P7: the light bridge flickers off 1 s every 8 s (a 1 s violet tell first); caught on it, you drop back to the stair head
    const bg = this.gates && this.gates.p7_bridge;
    if (bg && bg.open && !G.qaStill) {
      const ph = this.t % 8, onB = p.x >= bg.rect[0] - 0.3 && p.x <= bg.rect[2] + 0.3 && p.z >= bg.rect[1] && p.z <= bg.rect[3];
      if (ph > 6 && ph < 7 && !bg.tell) { bg.tell = true; this.fx('drain_nova', 0, ctx.heightAt(0, -33) + 0.04, -33); }
      if (ph >= 7 && !bg.off) {
        bg.off = true; this.bridgeFx(bg, false);
        if (onB && !G.downed) { C.hurtPlayer(8, null, 0); const sp = (ctx.scene.game.spawns || {}).p7 || [0, -28.6]; p.x = sp[0]; p.z = sp[1]; p.y = ctx.heightAt(sp[0], sp[1]); G.toast('The bridge flickers out! You scramble back to the stair head.', 2); }
      }
      if (ph < 6 && bg.off) { bg.off = false; bg.tell = false; this.bridgeFx(bg, true); }
    }
    if (rid === 'P8' && !f.pv_boss && !this.sylSpawned && !G.dlg) this.sylvaineIntro();
  }
  sylvaineIntro() {
    const G = this.G, S = G.S, bef = A(S) !== 'conquer'; this.sylSpawned = true;
    const pages = bef ? ['(Inside the cracked Heart Prism, a tall figure opens violet eyes. Frost-cracks race across the crystal.)', 'Light. Warm light, walking in my house. I have been so hungry. And so very cold.']
                      : ['(You pry at the Heart Prism. It cracks wide open. A tall figure unfolds from the light, violet eyes awake.)', 'A thief in my vault, prying at my heart. Do you know what you\'ve let out, little warm thing?', 'No matter. You\'re full of light. I\'ll start with you.'];
    if (bef && this.lumi.on) pages.push('Little Lumi? My nursery light? You came back to me. You were always my favourite light.', 'Lumi: "You drank from me first, my lady. I hid in a frog pond till the frogs sang me bright."');
    if (bef) pages.push('Then come closer, and I\'ll finish. The dark is coming back. I can\'t be in the dark again. I can\'t.');
    const spawn = () => {
      const C = G.combat, h = ((this.ctx.scene.game || {}).alf || {}).heart || [0, -47];
      const e = C.spawnEnemy({ id: 'sylvaine', role: 'sylvaine', pos: [h[0], h[1] + 2.4], once: true }, true);
      e.state = 'chase';
      G.toast('Lady Sylvaine, the Light-Drinker', 2.6);
      return e;
    };
    if (G.qaStill || this.qs().get('alfq') === 'boss' && this.qs().has('qa')) { spawn(); return; }
    G.openDialogue({ id: 'sylvaine', name: 'Lady Sylvaine' }, { pages, then: () => this.ctx && spawn() });
  }
  onSylvaine() {
    const G = this.G, f = flags(G.S);
    f.pv_boss = 1; this.bossBeams(false);
    if (this.ctx && this.ctx.framePull) this.ctx.framePull(1);
    const h = ((this.ctx && this.ctx.scene.game || {}).alf || {}).heart || [0, -47];
    if (!f.pv_core) { f.pv_core = 1; G.loot && G.loot.drop && G.loot.drop(h[0] + 1.6, h[1] + 2.6, { gem: 'prism_core' }); }
    G.toast(A(G.S) === 'conquer' ? 'Sylvaine falls. The Heart Prism splinters. Take its core.' : 'Sylvaine sinks to her knees. Reseal the Heart Prism (E / A at the Heart).', 3.2);
    G.setQuest('prismvault', G.S.quests.prismvault || 1); G.refreshMarkers();
  }
  onWarden() {
    const G = this.G; flags(G.S).pv_warden = 1;
    G.give('prism_glass', 2);
    if (Math.random() < 0.25 && G.loot && G.loot.drop && this.ctx) { const p = this.ctx.player; G.loot.drop(p.x + 0.8, p.z - 0.6, { gem: 'prism_core' }); }
  }
  heartOutro() {
    const G = this.G, bef = A(G.S) !== 'conquer';
    if (bef) G.openDialogue({ id: 'sylvaine', name: 'Lady Sylvaine' }, { pages: ['(Sylvaine sinks to her knees. Her violet light gutters like a candle in a draught.)', 'It\'s so dark... Lumi? Lumi, are you there? I\'m frightened.',
        'Lumi: "I\'m here, my lady. I\'ll glow till you sleep. Like I used to, over your cradle."', '(Lumi drifts into the Heart Prism. Gentle light fills it, endless and warm. The cracks close.)',
        'Enough light... at last. Thank you, warm thing. Tell my granddaughter the throne is hers. It always was.', '(Sylvaine sleeps, sealed in the Heart Prism, smiling. Lumi slips out, a little dimmer, and settles by your shoulder.)',
        'Lumi: "She\'s asleep. Resealed, and fed. I left some light with her. I\'ve got plenty. Ting."'],
      then: (G2) => { const f = flags(G2.S); f.pv_sealed = 1; f.sylvaine_sleeps = 1; G2.setQuest('prismvault', 2); } });
    else G.openDialogue({ id: 'sylvaine', name: 'Lady Sylvaine' }, { pages: ['(Sylvaine falls. The Heart Prism splinters, and its core drops into your hand, still warm.)', 'You\'ve taken the last light in my house. So I\'ll take the dark with me.',
        'Every lamp in Lumenvale will remember this. Every frog. Every wisp.', '(Far above, through the shaft in the roof, the city\'s lights begin to go out, one by one.)'],
      then: (G2) => { flags(G2.S).pv_taken = 1; G2.give('prism_heart', 1); G2.setQuest('prismvault', 2); } });
  }
  // ---------------------------------------------------------------- the prism sky + dark Lumenvale
  weatherInit() {
    this.wx = this.qs().get('alfwx') || prismWeather(this.G.S.day || 0, this.ctx.clock.t); this.wxT = 5;
    const ctx = this.ctx;
    if (this.wx !== 'clear') setTimeout(() => this.ctx === ctx && this.wxToast(), 1800);
  }
  wxToast() {
    const G = this.G;
    if (this.wx === 'aurora') { G.toast('The aurora is out. Your spells feel lighter.', 2.6); if (this.lumi.on) setTimeout(() => this.lumi.on && this.lumi.bark('The sky\'s dancing. The old queen used to dance like that, before.', 'aurora'), 3000); this.auroraOn(); }
    if (this.wx === 'prismrain') { G.toast('Prism rain. Light bends strangely, and something in the trees just vanished.', 2.8); if (this.lumi.on) setTimeout(() => this.lumi.on && this.lumi.bark('Ooh, tickly rain. Everything\'s sparkling. Me most of all.', 'prismrain'), 3000); }
  }
  // the aurora: a slow curtain of violet / blue / green pixel bands high over the canopy (a nearest-filtered canvas texture
  // on a big plane far behind the scene; dark Lumenvale turns it red and violet)
  auroraOn() {
    const ctx = this.ctx, sharp = ctx && ctx.effects && ctx.effects.sharp; if (!sharp || this.aurora) return;
    this.aurora = { pending: true };
    import('three').then((THREE) => {
      if (this.ctx !== ctx) return;
      const cv = document.createElement('canvas'); cv.width = 96; cv.height = 24; const g = cv.getContext('2d');
      const dark = F_(this.G.S).alf_dark, cols = dark ? ['#a42a4a', '#6a34b8'] : ['#a45cf0', '#5ac8ff', '#3cf08a', '#d4a8ff'];
      for (let x = 0; x < 96; x++) {
        const h = 6 + Math.round(6 * Math.sin(x * 0.21) + 4 * Math.sin(x * 0.07 + 1.3)), top = 4 + Math.round(3 * Math.sin(x * 0.13));
        for (let y = top; y < top + h; y++) { if ((x + y) % 2 && y > top + 1) continue; g.fillStyle = cols[(Math.floor(x / 9) + (y > top + h / 2 ? 1 : 0)) % cols.length]; g.fillRect(x, y, 1, 1); }
      }
      const tex = new THREE.CanvasTexture(cv); tex.magFilter = THREE.NearestFilter; tex.minFilter = THREE.NearestFilter; tex.wrapS = THREE.RepeatWrapping;
      const m = new THREE.Mesh(new THREE.PlaneGeometry(64, 16), new THREE.MeshBasicMaterial({ map: tex, transparent: true, alphaTest: 0.5, depthWrite: false }));
      const p = ctx.player; m.position.set(p.x, 14, p.z - 22); m.rotation.x = -0.15;
      sharp.add(m); this.aurora = { m, tex }; this.extra.push(m);
    });
  }
  darkGrade(ctx) {
    import('three').then((THREE) => {
      if (this.ctx !== ctx) return;
      const ind = new THREE.Color('#1a1430'), cold = new THREE.Color('#7a68b8');
      for (const g of Object.values(ctx.clock.cache || {})) {
        if (!g || typeof g !== 'object') continue;
        if (typeof g.sun_intensity === 'number') g.sun_intensity *= 0.45;
        if (typeof g.hemi_intensity === 'number') g.hemi_intensity *= 0.6;
        for (const [k, to, u] of [['sun_color', cold, 0.7], ['hemi_sky', ind, 0.6], ['hemi_ground', ind, 0.5], ['fog_color', ind, 0.7], ['sky_top', ind, 0.7], ['sky_bottom', cold, 0.4]])
          if (g[k] && g[k].isColor) g[k].lerp(to, u);
      }
      (ctx.lamps || []).forEach((L, i) => { L.tint = new THREE.Color(i % 6 === 5 ? RED : '#6a4ab8'); });
      // neon-blue watch-lamps at the stairs and doorways: the readability floor in the dark
      for (const sp of Object.values((ctx.scene.game || {}).spawns || {}).slice(0, 6)) {
        if (ctx.addGlow) this.extra.push(ctx.addGlow(sp[0], ctx.heightAt(sp[0], sp[1]), sp[1], { color: COLD, intensity: 4.5, range: 4.2, lift: 1.6 }));
        this.keep(this.fx('coldfire_flame', sp[0] + 0.6, ctx.heightAt(sp[0], sp[1]) + 1.2, sp[1] + 0.05, { duration: 1e9 }));
      }
    });
  }
  // ---------------------------------------------------------------- per frame
  update(dt) {
    const ctx = this.ctx, C = this.G.combat; if (!ctx) return;
    this.t += dt; this.foes.t = this.t;
    if (C && C.ctx) for (const e of C.enemies || []) if (!e.alf && (AREAS_ALF[this.area] || e.sp.id === 'frostsentinel')) this.hookFoe(e);
    this.lumi.update(dt);
    if (this.beams) this.beams.update(dt);
    if (this.area === 'prismvault') this.vaultTick(dt);
    if (this.carryFx) { const p = ctx.player; this.carryFx.x = p.x - 0.5; this.carryFx.z = p.z + 0.3; this.carryFx.y = ctx.heightAt(p.x, p.z) + 1.3 + Math.sin(this.t * 3) * 0.08; }
    if (this.area === 'lumen_court') this.courtTick();
    if (LUMENVALE.includes(this.area)) this.weatherTick(dt);
    if (this.aurora && this.aurora.tex) this.aurora.tex.offset.x = (this.t * 0.004) % 1;
  }
  hookFoe(e) {
    this.foes.hook(e); e.alf = true;
    if (!e.tick) e.tick = (en, dt, frozen) => this.foes.tickBase(en, dt, frozen);
    const role = e.D === ENEMIES.crystalgolem ? 'crystalgolem' : e.D === ENEMIES.prismshard ? 'prismshard' : null, prev = e.onKill;
    if (role) e.onKill = (en) => { if (prev) prev(en); if (!en.sp.noLoot && Math.random() < (role === 'crystalgolem' ? 0.2 : 0.08)) this.G.give('prism_glass', 1); };
    if (e.D && e.D.name === 'Shardmother' && !F_(this.G.S).sm_core) { const p0 = e.onKill; e.onKill = (en) => { if (p0) p0(en); flags(this.G.S).sm_core = 1; this.G.loot && this.G.loot.drop(en.a.x, en.a.z - 0.4, { gem: 'prism_core' }); this.G.give('prism_glass', 1); }; }
  }
  courtTick() {
    const S = this.G.S, f = flags(S), p = this.ctx.player, al = (this.ctx.scene.game || {}).alf || {};
    if ((S.quests.alf_dim || 0) === 1 && f.dm_lumi && !f.dm_trail && found(S, DW) >= 5 && al.door && Math.hypot(p.x - al.door.pos[0], p.z - al.door.pos[1]) < 2.4) {
      f.dm_trail = 1; this.G.toast('The thread of drained light runs under the Prism Spire door. Tell Mirelle.', 3); this.G.setQuest('alf_dim', 1); this.G.refreshMarkers();
    }
  }
  weatherTick(dt) {
    const C = this.G.combat, ctx = this.ctx;
    if ((this.wxT -= dt) <= 0) { this.wxT = 5; const w = this.qs().get('alfwx') || prismWeather(this.G.S.day || 0, ctx.clock.t); if (w !== this.wx) { this.wx = w; this.wxToast(); } }
    if (this.wx === 'aurora' && C && C.cd) { C.cd.spell = Math.max(0, (C.cd.spell || 0) - dt * 0.1); C.cd.charm = Math.max(0, (C.cd.charm || 0) - dt * 0.1); }
    if (this.wx === 'prismrain' && Math.floor(this.t * 6) !== Math.floor((this.t - dt) * 6)) {
      const p = ctx.player, x = p.x + (Math.random() - 0.5) * 12, z = p.z + (Math.random() - 0.5) * 9;
      this.fx('glitter', x, ctx.heightAt(x, z) + 0.05, z, { duration: 0.6 });
    }
  }
  qa() {
    const c = this.ctx, C = this.G.combat, S = this.G.S, gm = c ? c.scene.game || {} : {};
    const syl = C && C.enemies ? C.enemies.find((e) => e.D === ENEMIES.sylvaine && e.state !== 'dead') : null;
    return { area: this.area, open: this.open(), portals: (gm.portals || []).map((p) => p.to), sealed: (gm.sealed || []).map((g) => g.arch || g.realm),
             gateFx: c && c.fx && c.fx.gate_alfheim ? c.fx.gate_alfheim.name : null, wx: this.wx, room: this.room || null,
             quests: Object.fromEntries(['alf_gate', 'alf_name', 'alf_dim', 'alf_take', 'prismvault'].map((k) => [k, (S.quests || {})[k] || 0])),
             alliance: A(S) || null, rivals: F_(S).rivals || null, spots: this.spots.filter((s) => s.show()).length, prompt: this.prompt(),
             gates: this.gates ? Object.fromEntries(Object.values(this.gates).map((g) => [g.id, !!g.open])) : null,
             beams: this.beams ? this.beams.qa() : null, lumi: this.lumi.qa(), rims: (this.rims || []).map((r) => r.lit),
             foes: C && C.enemies ? C.enemies.filter((e) => e.state !== 'dead').map((e) => e.a.role) : [],
             sylvaine: syl ? { hp: Math.round(syl.hp), max: syl.D.hp, scale: syl.D.scale, r: syl.D.r, state: syl.state, phase: syl.phase || 1, shield: !!syl.shieldOn, role: syl.a.role } : null };
  }
}
