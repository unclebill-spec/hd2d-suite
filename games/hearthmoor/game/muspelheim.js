// [MUSPELHEIM] Muspelheim (realm-muspelheim branch), built from the Hearthmoor Story script (staging story/muspelheim.md; plan + status in
// MUSPELHEIM_PROGRESS.md). CHUNK 1 = SKELETON: realm tables, the Bifrost red-arch wiring, quest data, NPC talk, Kindle's companion data,
// Vharzul's boss data, the Armed Crossing look-spots. Nothing here changes any existing area or behaviour while MUSP_BUILT is empty:
// no Muspelheim area is built yet (the art pack /workspace/hearthmoor-staging/art/muspelheim/READY.txt is not there), so the Bifrost red
// arch stays sealed, the gate-quest spots stay hidden and AREAS_MUSP stays empty. To take an area live: build its spec (areas/src/<id>.json),
// run tools/hearthmoor/musp_art.py, add the id to MUSP_BUILT. Quests / TALK / shops / the Bifrost gate merge into the shared tables from here,
// like jotunheim.js, so shared files only carry a few marked hook lines.
// Decisions (Cozy Builder, Oct 17 2026): (1) lockRival("niflheim") on befriend stays as written; (2) the Ember-born skip is the whole Ember-born
// perk (no second option in Aska's choice); (3) Vharzul stays a boss only.
import { TALK, ITEMS, QUESTS, MARKER_HOOKS, SPELL_NAMES } from './data.js';
import { REALM, MERIT, Factions } from './factions.js';
import { ENEMIES, SPAWNS, SPELLS } from './heroes.js';
import { XP, TIER } from './progress.js';
import { SHOPS, GOODS } from './shop.js';
import { lockRival, moodUp } from './alfheim.js';
import { BASES, RARE_AREAS, Rares } from './rares.js';
import { RARITY, makeItem } from './loot.js';
import { KINDS as WX_KINDS, WX_HOOK } from './weather.js';
import { COMP, unlock as compUnlock, swap as compSwap, active as compActive } from './svartalfheim_companions.js';
import { WAYS } from './ravenhold.js';
import { KIT as FOLLOW_KIT } from './svartalfheim_follow.js';

// story 2.1. The dungeon is 9 rooms: two areas like clockdeep / barrow (decision recorded in MUSPELHEIM_PROGRESS.md): `caldera` C1-C4, `caldera2` C5-C9.
export const MUSP_PLANNED = {
  muspelheim: 'Cinderhold', mp_hall: 'The Sigil Forge', lavafalls: 'The Lavafalls', caldera: 'The Ember Caldera', caldera2: 'The Ember Caldera: the Throne',
};
export const MUSP_BUILT = ['muspelheim', 'mp_hall', 'lavafalls', 'caldera', 'caldera2'];   // ids of areas whose built output is in areas/<id>/ (the live list)
export const AREAS_MUSP = Object.fromEntries(MUSP_BUILT.map((a) => [a, `areas/${a}/`]));        // id -> 'areas/<id>/' (merged into game.js's area path map)
export const AREA_NAMES_MUSP = Object.fromEntries(MUSP_BUILT.map((a) => [a, MUSP_PLANNED[a]]));   // id -> display name (merged into game.js's AREA_NAME)
export const MUSP_AREAS = Object.keys(MUSP_PLANNED);

const flags = (S) => (S.flags = S.flags || {});
const F = (S) => S.flags || {};
const q = (S, k) => (S.quests || {})[k] || 0;
const ally = (S) => (flags(S).alliance = flags(S).alliance || {});
const gold = (G, n) => { G.S.gold = (G.S.gold || 0) + n; G.toast(`+${n} gold`, 1.8); G.drawBag && G.drawBag(); };
const met = (k) => (G) => { G.S.met = { ...(G.S.met || {}), [k]: 1 }; };
const found = (S, ...ks) => ks.filter((k) => (S.found || {})[k]).length;
const mark = (G) => { G.refreshMarkers && G.refreshMarkers(); G.save && G.save(); };

// story 1.1 / 12: helpers (allyCount = the 4-ally safety net, lockedBy = befriended Niflheim, mood = conquered Niflheim)
export const allyCount = (S) => Object.values(F(S).alliance || {}).filter((v) => v === 'befriend').length;
export const lockedBy = (S) => (F(S).rivals || {}).muspelheim === 'locked';
export const mood = (S) => ((F(S).realm_mood || {}).muspelheim || 0) >= 1;
const emberBorn = (S) => S.hero === 'cinderknight';
const runeReader = (S) => S.hero === 'runeguard';
const gateRank = (S) => ((S.ranks || {}).gate || 0);   // the Guild rank (Rift Marks); `G.factions.rank('gate')` reads the same field
const armed = (S) => !!((S.gear || {}).weapon);

Object.assign(REALM, { muspelheim: 'embassy', mp_hall: 'embassy', lavafalls: 'embassy', caldera: 'embassy', caldera2: 'embassy' });   // befriend = Realm Favor; conquer / contract pay 'gate' (Factions.realm wrap below)
Object.assign(MERIT, { mp_gate: 60, ashtoll: 60, mp_contract: 60, caldera_c: 120, mp_walk: 40, mp_sigil: 60, mp_rival: 20, mp_kindle: 80, caldera: 120, emberfall: 40 });   // story 3.12
{   // story 12: factions.realm() returns `gate` in the realm's areas when alliance.muspelheim === "conquer" or flags.mp_contract
  const realm0 = Factions.prototype.realm;
  Factions.prototype.realm = function realm() {
    const f = F(this.G.S);
    if (MUSP_AREAS.includes(this.G.area) && ((f.alliance || {}).muspelheim === 'conquer' || f.mp_contract)) return 'gate';
    return realm0.call(this);
  };
}

// ------------------------------------------------------------------ the Bifrost red arch (story 0, 3.1): sealed pos [-11, -5] on Bifrost's west wall
export const MP_ARCH = { rect: [-11.75, -5.4, -10.25, -4.55], pos: [-11.0, -5.0], spawn: [-11.0, -3.6, 'down'] };
const HUB_GATE = { to: 'bifrost', spawn: 'from_muspelheim', rect: [-0.9, 10.1, 0.9, 11.1], label: 'the red arch back to Bifrost Crossing' };   // Cinderhold's own arch [0, 10.6]
// open when the quest is done, the realm is allied, or ?muq= (QA; ?muq=gate keeps it shut for the quest itself). Never opens while no area is built.
export const gateOpen = (S, qs) => !!(F(S).mp_gate_open || (F(S).alliance || {}).muspelheim || F(S).mp_contract || (qs && qs.has('muq') && qs.get('muq') !== 'gate'));
export const live = () => MUSP_BUILT.includes('muspelheim');

// ------------------------------------------------------------------ foes (story 8.1-8.4)
Object.assign(ENEMIES, {
  magma_hound: { name: 'Magma hound', scale: 1.4, hp: 90, dmg: 12, speed: 2.2, reach: 1.4, windup: 0.45, cd: 1.6, aggro: 7.5, r: 0.45, push: 0.4, element: 'fire' },
  magma_hound_gate: { name: 'Magma hound', scale: 2, hp: 190, dmg: 16, speed: 2.0, reach: 1.9, windup: 0.5, cd: 1.7, aggro: 8, r: 0.6, push: 0.3, heavy: true, element: 'fire' },   // the Armed Crossing's gate foe (2x, pounces)
  flame_elemental: { name: 'Flame elemental', scale: 1.5, hp: 110, dmg: 14, speed: 1.4, reach: 1.7, windup: 0.6, cd: 1.9, aggro: 7, r: 0.5, push: 0.3, float: true, element: 'fire' },
  fire_golem: { name: 'Fire golem', scale: 2, hp: 240, dmg: 20, speed: 0.8, reach: 2.2, windup: 1.0, cd: 2.4, aggro: 6, r: 0.7, push: 0.15, heavy: true, element: 'fire' },
  ashen_cultist: { name: 'Ashen Cultist', hp: 90, dmg: 13, speed: 1.9, reach: 1.5, windup: 0.4, cd: 1.5, aggro: 7.5, r: 0.4, push: 0.5, elite: true, element: 'fire' },   // elite, 1x: ash-grey hooded tunic, no plate
  kilnmother: { name: 'Kilnmother', scale: 3, hp: 460, dmg: 22, speed: 0.9, reach: 3.0, windup: 1.0, cd: 2.4, aggro: 9, r: 0.9, push: 0.1, heavy: true, boss: true, minion: 'flame_elemental', respawn: 1e9, element: 'fire' },   // C6 mini-boss: molten fist telegraph, calls 2 elementals at 50%
  dagny: { name: 'Cinder-Captain Dagny Flameguard', scale: 2.5, hp: 380, dmg: 17, speed: 1.2, reach: 2.4, windup: 0.6, cd: 1.8, aggro: 9, r: 0.8, push: 0.2, heavy: true, boss: true, trial: true, respawn: 1e9 },   // conquer path: yields at 25%
  // C9. 8x: framed:true pulls the camera back from the first frame (combat.js reads D.framed); the sheet is a boss sheet (boss_roles) with black-iron plate (the arc's only plate).
  // P1 blade arcs + telegraphed fire pillars, P2 (60%) two flame elementals + lava edge, P3 (25%) the three Warden's lamps relight (snuff / break them to stop his heal).
  vharzul: { name: 'Vharzul the Ember Throne', scale: 8, framed: true, plate: true, element: 'fire', hp: 2300, dmg: 30, speed: 0.8, reach: 6.2, windup: 0.95, cd: 2.4, aggro: 13, r: 2.3, push: 0.05, heavy: true, slam: true, boss: true,
             wave: { every: 3, r: 7.2, dmg: 24 }, minion: 'flame_elemental', phases: [0.6, 0.25], glow: '#ff7a1a', legendary: true, respawn: 1e9 },
});
// ------------------------------------------------------------------ the Caldera school (story 9.2, Muspelheim-2): realm magic from Torka, drawn by combat.js from the game-fx atlas
// Circle I after The Ember Caldera (caldera = 3, befriend; flag cs_i), II at Lv 5 (cs_ii), III at Lv 10 (cs_iii): the skill tiers' gates (TIER in progress.js), like Solvi's Stonefrost.
export const CS_LV = { 2: TIER[2].lv, 3: TIER[3].lv };
export const SCHOOL = ['fire_wave', 'magma_pool', 'ember_swarm', 'flame_ward', 'magma_hound'];
SPELLS.fire_wave = { name: 'Fire Wave', cd: 2.4, dmg: 24, range: 4.2, arc: 0.64, roll: 10, push: 0.6, burn: 4, kind: 'firewave' };   // I: a rolling cone of fire (100 deg, 4.2 m), a little burn after
SPELLS.magma_pool = { name: 'Magma Pool', cd: 3.6, dmg: 5, radius: 1.6, life: 6, kind: 'magma' };   // I: a lava patch 2 m ahead for 6 s, 5 every 0.5 s to foes standing in it
SPELLS.ember_swarm = { name: 'Ember Swarm', cd: 10, dmg: 9, burn: 2, n: 6, orbit: 1.0, kind: 'swarm', own: 'swarm' };   // II: 6 motes orbit you for 1 s, then fly at the nearest foes
SPELLS.flame_ward = { name: 'Flame Ward', cd: 16, t: 8, take: 0.7, refl: 0.1, kind: 'ward', own: 'ward' };   // II: 8 s, -30 % fire damage taken, 10 % of each blow back as a burn
SPELLS.magma_hound = { name: 'Magma Hound', cd: 40, life: 20, kind: 'hound', own: 'hound' };   // III: a magma hound fights for 20 s (replaces any other summon)
Object.assign(SPELL_NAMES, { fire_wave: 'Fire Wave', magma_pool: 'Magma Pool', ember_swarm: 'Ember Swarm', flame_ward: 'Flame Ward', magma_hound: 'Magma Hound' });
const csTeach = (G, flag, spells, toast) => { flags(G.S)[flag] = 1; for (const n of spells) G.learn(n); G.toast(toast, 2.8); mark(G); G.save && G.save(); };
function school(S) {   // Torka's lessons, or null: they win over the Emberfang / Emberfall lines as soon as the level allows (Solvi's order)
  const f = F(S), al = (f.alliance || {}).muspelheim, lv = S.lv || 1;
  if (al !== 'befriend') return null;
  if (f.cs_i && !f.cs_ii && lv >= CS_LV[2]) return { pages: ['Back at my anvil. You have grown into your boots.', '(Torka opens his fist. Six embers lift off his palm and circle him like moths. Then he closes the fist, and a ring of small flames stands up around him.)',
    'Ember Swarm: six motes circle you, then go and bite whatever is rude. Flame Ward: a ring of fire for eight breaths. Fire forgets to burn you, and whatever strikes you feels its own heat.'],
    then: (G) => csTeach(G, 'cs_ii', ['ember_swarm', 'flame_ward'], 'Caldera school II: Ember Swarm, Flame Ward') };
  if (f.cs_ii && !f.cs_iii && lv >= CS_LV[3]) return { pages: ['The third circle. Stand back from the anvil.', '(Torka strikes the anvil once. Lava runs off its horn, curls up on the floor, and shakes itself into a hound.)',
    'The Magma Hound. It runs at your side for twenty breaths, then it is warm stone again. Do not try to pet it.', 'That is the whole of the Caldera school. Hot iron says what a smith won\'t. Let it.'],
    then: (G) => csTeach(G, 'cs_iii', ['magma_hound'], 'Caldera school III: Magma Hound') };
  if (q(S, 'caldera') === 3 && !f.cs_i) return { pages: ['The Throne sleeps, and the Caldera breathes easy. Sit at my anvil, small one. Hot iron teaches; so do I.', '(Torka draws two shapes in the forge-scale: a wave that curls over, and a round pool that glows when he breathes on it.)',
    'Fire Wave: push the heat out in front of you and let it roll. Magma Pool: pour it on the ground and let them stand in it. Two lessons for the first circle. Come back older for the rest.'],
    then: (G) => { G.S.unlocks = { ...(G.S.unlocks || {}), caldera_school: 1 }; csTeach(G, 'cs_i', ['fire_wave', 'magma_pool'], 'Caldera school: first circle (Fire Wave, Magma Pool)'); } };
  return null;
}
function schoolWait(S) {   // what you are waiting for, below the level (after the errand lines)
  const f = F(S);
  if ((F(S).alliance || {}).muspelheim !== 'befriend') return null;
  if (f.cs_iii) return { pages: ['All three circles are yours: Fire Wave, Magma Pool, Ember Swarm, Flame Ward, the Magma Hound. Hot iron says what a smith won\'t. Let it.'] };
  if (f.cs_ii) return { pages: [`The second circle is yours: Ember Swarm, Flame Ward. The Magma Hound waits for Lv ${CS_LV[3]}. Hot iron does not hurry.`] };
  if (f.cs_i) return { pages: [`The first circle is yours: Fire Wave, Magma Pool. Ember Swarm and Flame Ward wait for Lv ${CS_LV[2]}, the Magma Hound for Lv ${CS_LV[3]}. Hot iron does not hurry.`] };
  return null;
}
Object.assign(XP, { magma_hound: 45, magma_hound_gate: 120, flame_elemental: 60, fire_golem: 90, ashen_cultist: 80, kilnmother: 240, dagny: 0, vharzul: 1000 });
// rares (story 8.3) on the procedural-rare system: bodies `ashalpha` (2x) and `pyreling` (3x) must be in lavafalls' boss_roles when the art lands.
Object.assign(BASES, {
  ashalpha: { name: 'Ash Alpha', scale: 2, hp: 300, dmg: 16, speed: 2.1, reach: 2.0, windup: 0.5, cd: 1.7, aggro: 8.5, r: 0.7, push: 0.2, heavy: true, minion: 'magma_hound', xp: 180 },
  pyreling: { name: 'Pyreling', scale: 3, hp: 360, dmg: 18, speed: 1.3, reach: 2.6, windup: 0.7, cd: 2.0, aggro: 8, r: 0.8, push: 0.2, float: true, xp: 210 },
});
RARE_AREAS.lavafalls = { bases: ['ashalpha', 'pyreling'], spots: [[5.6, 1.6], [2.4, -2.4]] };   // spots are chosen with the area (fall-pool; clear of braziers, glass walks, actors and the start view)
const spawnRare0 = Rares.prototype.spawn;
Rares.prototype.spawn = function spawn(o = {}) {   // Ash Alpha = blazing + quick (enraged + summoner: calls 2 hounds), Pyreling = flicker-step (blinking)
  if (!o.traits && o.base === 'ashalpha') o = { ...o, traits: ['enraged', 'summoner'] };
  if (!o.traits && o.base === 'pyreling') o = { ...o, traits: ['blinking'] };
  return spawnRare0.call(this, o);
};
SPAWNS.lavafalls = [   // 1.4x / 1.5x foes read fully on screen; clear of the braziers (+-1.6, -5.4), cold braziers (+-3.6, 1), lava pools (+-6.4, -4.4), the channel at z 3 and Torka (-4.8, -2.4)
  { id: 'lf_hound0', role: 'magma_hound', pos: [5.0, -5.0] }, { id: 'lf_hound1', role: 'magma_hound', pos: [8.0, -1.4] },
  { id: 'lf_elem0', role: 'flame_elemental', pos: [-1.0, -1.4], night: true }, { id: 'lf_hound2', role: 'magma_hound', pos: [-1.6, 6.4], night: true },
];
const MP_FX = {   // [effect, [x, z], dy]: the pack's animated pools / flames / motes (art metadata layout; the Caldera rooms from the placed pieces)
  muspelheim: [['pool_lava', [-8, 3.0], 0], ['pool_lava', [-4, 3.0], 0], ['pool_lava', [0, 3.0], 0], ['pool_lava', [4, 3.0], 0], ['pool_lava', [8, 3.0], 0], ['pool_lava', [9.6, 7.0], 0], ['pool_forge', [-7.2, -3.4], 0], ['pool_forge', [6.6, -4.9], 0], ['pool_forge', [-7.0, 7.4], 0], ['pool_forge', [-9.0, -0.4], 0], ['pool_forge', [-3.4, -1.8], 0], ['pool_forge', [3.4, -1.8], 0], ['pool_forge', [-3.6, 7.0], 0], ['pool_forge', [3.6, 7.0], 0], ['pool_forge', [0, -9.0], 0], ['pool_forge', [8.0, -2.0], 0], ['pool_cold', [-1.6, 5.8], 0], ['pool_cold', [1.6, 5.8], 0], ['pool_cold', [-5.2, 0.6], 0], ['pool_cold', [5.4, 0.4], 0], ['pool_violet', [-1.3, -9.2], 0], ['pool_violet', [1.3, -9.2], 0], ['pool_violet', [-9.4, -9.0], 0], ['pool_teal', [-11.0, -9.2], 0], ['frost_vein', [-5.2, 2.2], 0], ['frost_vein', [5.4, 1.6], 0], ['forge_flame', [-3.4, -1.8], 1.9], ['forge_flame', [3.4, -1.8], 1.9], ['forge_flame', [-3.6, 7.0], 1.9], ['forge_flame', [3.6, 7.0], 1.9], ['cold_flame', [-1.6, 5.8], 1.9], ['cold_flame', [1.6, 5.8], 1.9], ['violet_flame', [-1.3, -9.2], 3.4], ['violet_flame', [1.3, -9.2], 3.4], ['ember_motes', [-7.2, -6.2], 5.0], ['ember_motes', [-4.0, 3.4], 0.2], ['ember_motes', [4.0, 3.4], 0.2], ['neon_embers', [0, 3.4], 0.4], ['neon_embers', [8.4, 7.0], 0.2], ['glow_orb_blue', [-4.4, 5.0], 2.2], ['glow_orb_violet', [-9.6, -8.0], 1.9], ['glow_orb_red', [6.0, 4.6], 1.9], ['neon_fireflies_blue', [-5.4, 1.6], 0.6], ['neon_fireflies_violet', [-10.0, -8.0], 0.6], ['neon_fireflies_red', [7.6, 0.6], 0.6], ['glow_frog_blue', [-4.6, 4.4], 0.0], ['glow_frog_violet', [-10.2, -6.0], 0.0], ['spring_bubbles', [-11.0, -9.2], 0.3], ['lava_fall', [9.6, 6.8], 0.0]],
  mp_hall: [['pool_violet', [-2.0, -5.2], 0], ['pool_violet', [2.0, -5.2], 0], ['pool_forge', [-4.6, -3.0], 0], ['pool_forge', [-4.8, -5.6], 0], ['pool_forge', [-2.6, 3.4], 0], ['pool_forge', [2.6, 3.4], 0], ['pool_forge', [0, -6.4], 0], ['pool_forge', [-4.6, -0.4], 0], ['pool_cold', [4.6, -6.6], 0], ['pool_forge', [0, 9.0], 0], ['pool_forge', [-5.4, 7.4], 0], ['pool_forge', [5.4, 7.4], 0], ['frost_vein', [-1.6, 2.6], 0], ['violet_flame', [-2.0, -5.2], 2.1], ['violet_flame', [2.0, -5.2], 2.1], ['cold_flame', [4.6, -6.6], 3.2], ['forge_flame', [-2.6, 3.4], 1.9], ['forge_flame', [2.6, 3.4], 1.9], ['ember_motes', [-4.6, -3.0], 0.4], ['neon_embers', [-4.6, -3.0], 0.6], ['neon_fireflies_violet', [0, -2.0], 0.6], ['glow_orb_violet', [-5.6, 2.0], 2.0], ['glow_orb_red', [5.4, 3.6], 2.2], ['glow_crystals_violet', [-3.2, -7.6], 3.0]],
  lavafalls: [['pool_lava', [-6.4, -4.4], 0], ['pool_lava', [6.4, -4.4], 0], ['pool_lava', [4, 3.0], 0], ['pool_lava', [8, 3.0], 0], ['pool_lava', [0, -7.0], 0], ['pool_forge', [-1.6, -5.4], 0], ['pool_forge', [1.6, -5.4], 0], ['pool_cold', [-3.6, 1.0], 0], ['pool_cold', [3.6, 1.0], 0], ['pool_teal', [-7.4, 6.0], 0], ['pool_violet', [-5.4, 6.4], 0], ['pool_violet', [-9.2, 4.2], 0], ['pool_lava', [7.6, 6.4], 0], ['pool_forge', [0, -4.0], 0], ['burn_patch', [2.6, -0.2], 0], ['burn_patch', [-4.0, 0.0], 0], ['pool_lava', [-6.0, -4.0], 0], ['lava_fall', [-6.4, -6.9], 0.0], ['lava_fall', [-5.6, -6.9], 0.0], ['lava_fall', [6.4, -6.9], 0.0], ['lava_fall', [5.6, -6.9], 0.0], ['forge_flame', [-1.6, -5.4], 1.9], ['forge_flame', [1.6, -5.4], 1.9], ['cold_flame', [-3.6, 1.0], 1.9], ['cold_flame', [3.6, 1.0], 1.9], ['violet_flame', [-5.4, 6.4], 2.1], ['violet_flame', [-9.2, 4.2], 2.1], ['spring_bubbles', [-7.4, 6.0], 0.3], ['steam_puff', [-8.6, 7.0], 0.2], ['ember_motes', [0, -3.0], 0.2], ['ember_motes', [-6.4, -4.4], 0.2], ['neon_embers', [6.4, -4.4], 0.3], ['neon_fireflies_blue', [-3.0, 3.0], 0.6], ['neon_fireflies_violet', [-8.0, 5.0], 0.6], ['glow_orb_blue', [-1.0, 3.0], 2.4], ['glow_orb_violet', [-6.4, 2.0], 2.0], ['glow_frog_blue', [-6.0, 7.4], 0.0], ['glow_crystals_blue', [-4.4, -5.8], 3.0]],
  caldera: [['forge_flame', [-3.4, 7.0], 1.9], ['forge_flame', [3.4, 7.0], 1.9], ['pool_lava', [-9.0, 6.0], 0], ['pool_lava', [-9.0, 2.0], 0], ['pool_lava', [9.0, 6.0], 0], ['pool_lava', [9.0, 2.0], 0], ['forge_flame', [-4.6, -6.6], 1.9], ['forge_flame', [4.6, -6.6], 1.9], ['pool_lava', [-9.4, -7.0], 0], ['pool_lava', [9.4, -7.0], 0], ['pool_lava', [-3.7, -18.4], 0], ['pool_lava', [-3.7, -22.4], 0], ['pool_lava', [-3.7, -26.4], 0], ['pool_lava', [3.7, -18.4], 0], ['pool_lava', [3.7, -22.4], 0], ['pool_lava', [3.7, -26.4], 0], ['pool_lava', [-7.6, -22.4], 0], ['pool_lava', [7.6, -22.4], 0], ['cold_flame', [-2.4, -29.6], 1.9], ['forge_flame', [-6.4, -37.4], 2.2], ['forge_flame', [5.6, -33.6], 1.9], ['forge_flame', [-8.6, -32.4], 1.9]],
  caldera2: [['cold_flame', [-2.8, 3.0], 1.9], ['cold_flame', [2.8, 3.0], 1.9], ['forge_flame', [-5.6, -6.6], 1.9], ['forge_flame', [5.6, -6.6], 1.9], ['spring_bubbles', [-6.0, -24.0], 0.3], ['cold_flame', [6.0, -24.6], 1.9], ['forge_flame', [-7.2, -32.4], 1.9], ['forge_flame', [7.2, -32.4], 1.9], ['pool_lava', [-9.4, -54.0], 0], ['pool_lava', [-9.4, -50.0], 0], ['pool_lava', [-9.4, -46.0], 0], ['pool_lava', [9.4, -54.0], 0], ['pool_lava', [9.4, -50.0], 0], ['pool_lava', [9.4, -46.0], 0], ['cold_flame', [-5.4, -43.4], 1.9], ['cold_flame', [5.4, -43.4], 1.9], ['cold_flame', [-5.4, -43.4], 1.9], ['cold_flame', [5.4, -43.4], 1.9], ['ember_motes', [-4.0, -53.0], 0.2], ['neon_embers', [4.0, -53.0], 0.2], ['glow_crystals_blue', [-6.0, -52.0], 3.0], ['glow_crystals_violet', [6.0, -52.0], 3.0], ['pool_cold', [-5.4, -43.4], 0], ['pool_cold', [5.4, -43.4], 0], ['pool_violet', [0.0, -45.2], 0], ['pool_violet', [-4.5, -53.0], 0], ['pool_violet', [4.5, -53.0], 0], ['steam_puff', [-6.0, -24.6], 0.2]],
};

WAYS.caldera2 = ['the Ember Caldera, the Waystone Landing', 'caldera2', 'from_waystone'];
SPAWNS.caldera = [   // C1 (two hounds) is an ambush on the way in (calderaRooms); C2 cultists step out when you pass z -3 (caldera2c; a phone-portrait view reaches z -10, under the HUD), C3's far bank + C4 golems. Nothing in the start view (z > -9).
  { id: 'cd_golem0', role: 'fire_golem', pos: [4.4, -34.4] }, { id: 'cd_golem1', role: 'fire_golem', pos: [-1.0, -41.0], night: true }, { id: 'cd_cult2', role: 'ashen_cultist', pos: [-3.0, -32.4], night: true },
];
SPAWNS.caldera2 = [   // C5 is quiet (Veyra's seam); C6 Kilnmother is scripted; C7 elementals + a golem; C9 is Vharzul
  { id: 'c2_elem0', role: 'flame_elemental', pos: [4.6, -21.6] }, { id: 'c2_elem1', role: 'flame_elemental', pos: [-1.6, -27.4] },
  { id: 'c2_golem0', role: 'fire_golem', pos: [3.6, -34.0] }, { id: 'c2_hound0', role: 'magma_hound', pos: [-5.4, -30.4], night: true },
];
// the three frost wedges (Veyra, story 6): area, x, z. Melted by any spell cast within 3 m (the Hollows brazier / flue rule, as in the Barrow's ice wall)
export const WEDGE = { cd_w1: ['caldera', -4.6, -31.8], cd_w2: ['caldera2', 3.0, -3.4], cd_w3: ['caldera2', -3.6, -40.0] };
// C3's glass bridge (z -16.4 .. -30.2, 2.4 m up): a 3 x 6 tile grid; the lit path holds, any dark pane cracks and drops you back at the head
const GLASS = { x0: -2.6, w: 5.2 / 3, z0: -16.4, h: 2.3, rows: 6, endZ: -30.0, head: [0, -15.0], LIT: [[1], [1, 2], [2], [2, 1], [1, 0], [0, 1]] };
const glassTile = (x, z) => { const r = Math.floor((GLASS.z0 - z) / GLASS.h), c = Math.min(2, Math.max(0, Math.floor((x - GLASS.x0) / GLASS.w))); return r < 0 || r >= GLASS.rows ? null : [c, r]; };
const glassCentre = (c, r) => [GLASS.x0 + GLASS.w * (c + 0.5), GLASS.z0 - GLASS.h * (r + 0.5)];
// Vharzul's three Warden's lamps (the pack's throne scene): they relight in phase 3; each lit lamp mends him until you snuff it
const LAMPS = [[0.0, -45.2], [-4.5, -53.0], [4.5, -53.0]];
const THRONE = { z: -44.4, boss: [0, -51.8], elems: [[-4.6, -48.4], [4.6, -48.4]] };
// SPAWNS.<area> are authored with each area (phone portrait shows the north strip: giants / 8x actors fully on or fully off screen; see JOTUNHEIM_PROGRESS placement lessons)

// ------------------------------------------------------------------ weather (story 2.7): ash fall 60 %, clear glow 25 %, ember storm 15 %
WX_KINDS.ash_fall = [{ preset: 'embers', rate: 0.6 }, { preset: 'dust_motes', rate: 1.2 }, { preset: 'mist', rate: 0.3 }];   // visibility slightly down, cosmetic
WX_KINDS.ember_storm = [{ preset: 'embers', rate: 1.8 }, { preset: 'mist', rate: 0.5 }];   // + burn patches (2 dmg / s) on open ground: fire resist (Kindle, springs, fire-ward, cinder-tea) negates them (with the area build)
const wxHash = (n) => { let x = (Math.imul(n | 0, 0x9E3779B1) + 0x7F4A7C15) | 0; x = Math.imul(x ^ (x >>> 16), 0x85EBCA6B); x = Math.imul(x ^ (x >>> 13), 0xC2B2AE35); return ((x ^ (x >>> 16)) >>> 0) / 4294967296; };   // murmur-style int32 finalizer (a plain * loses precision and skews the split)
const muspWx = (day, t) => { const r = wxHash(day * 4 + Math.floor(t * 4) + 6161); return r < 0.6 ? 'ash_fall' : r < 0.85 ? 'clear' : 'ember_storm'; };
WX_HOOK.muspelheim = muspWx; WX_HOOK.lavafalls = muspWx; WX_HOOK.caldera = muspWx;   // mp_hall and the deep Caldera room set are indoors (no sky)

// ------------------------------------------------------------------ items + Svala's stall (story 5.5, 11; prices are first guesses)
Object.assign(ITEMS, {
  heat_key: { name: 'Heat-sealed key', px: 'glowseed', about: "A copper rod that went into the wrong kiln and came out hot. Carry it with the tongs. Halvard's, for the red arch." },
  ember_sigil_copy: { name: 'Ember-sigil (a copy)', px: 'glowseed', about: 'The false sigil from Lantern Eve. Look, do not wear: the flame curls the wrong way, and the core is cold blue.' },
  caldera_key: { name: 'Caldera Key', px: 'tonic', about: "Cinder-Captain Dagny's key-fire, forced from the Warden. It opens the Ember Caldera, no questions asked." },
  heart_coal: { name: 'Heart-coal', px: 'glowseed', about: "A coal from the Caldera's deep vents that never goes out. Torka wants three for Emberfang." },
  cinder_berry: { name: 'Cinder-berry', px: 'denbiscuit', about: "Orm's cinder-berry, lizard-sized. One a day, from the same hand, and a young lizard starts to trust it." },
  cinder_tea: { name: 'Cinder-tea', px: 'tonic', about: 'Svala\'s smoky tea. Clears an ember storm for 60 s.' },
  fire_ward: { name: 'Fire-ward charm', px: 'glowseed', about: 'A charm of copper wire and ash. Fire resist +20%.' },
  brazier_lamp: { name: 'Brazier-lamp', px: 'glowseed', about: 'A lamp that burns like a little brazier. Light radius +2.' },
  ember_crown: { name: 'Ember Crown', px: 'glowseed', about: "Vharzul's crown, cold now. A trophy. Cinderhold will not forget who took it." },
});
Object.assign(GOODS, {
  cinder_tea: { name: 'Cinder-tea', about: 'Clears an ember storm for 60 s. Smoky, and nothing like moonpetal.', price: 16 },
  fire_ward: { name: 'Fire-ward charm', about: 'Fire resist +20%.', price: 85 },
  brazier_lamp: { name: 'Brazier-lamp', about: 'Burns like a little brazier. Light radius +2.', price: 55 },
});
SHOPS.mp_trader = { name: "Svala's Spice Braziers", keeper: 'Svala, spice trader', goods: ['cinder_tea', 'fire_ward', 'brazier_lamp', 'tonic'], gear: { n: 3, rar: [0, 1, 1] }, sellMul: 1 };
// Emberfang (story 9.1): the legendary red-flame greatsword. Heavy hits ignite (burn 3 s), a charged slash throws a flame wave: the ignite rides on the combat hook that comes with
// the Caldera build (like the Rimebreaker's 3rd-hit freeze); the engine has no charged attack yet.
export function EMBERFANG(S) {
  const it = makeItem(Math.max(10, S.lv || 1), 4, 'weapon'), k = RARITY[4].mul * (1 + (it.lv - 1) * 0.06);
  it.name = 'Emberfang'; it.fixed = true; it.unique = 'emberfang'; it.crafted = true;
  it.mods = { meleeMul: +(0.07 * k).toFixed(3), spellMul: +(0.03 * k).toFixed(3), crit: +(0.006 * k).toFixed(3) };
  it.gems = [null, null];
  it.about = "A red-flame greatsword forged from the Caldera's heart-coals, cut down to your size. A cold-blue line runs down the fuller: a reminder. Heavy hits ignite what they bite.";
  return it;
}
export const HC = [['hc_1', 'caldera', [-4.4, -40.6]], ['hc_2', 'caldera2', [3.0, -15.6]], ['hc_3', 'caldera2', [6.6, -30.4]]];   // heart-coal spots: C4 behind the furnace, C6 behind Kilnmother's altar, C7 by the springs

// ------------------------------------------------------------------ quests (story 3.1-3.10; 3 = done)
export const SIGIL = ['sf_cast', 'sf_ledger', 'sf_mirror'];
// 4.3: each cleared realm (S.evidence.jotunheim / svartalfheim) is one free clue (max 2), a Rune-reader's mirror clue is free, and at least one is read here
export function sigil(S) {
  const f = F(S), read = SIGIL.filter((k) => f[k]).length, ev = S.evidence || {};
  const free = Math.min(2, ['jotunheim', 'svartalfheim'].filter((k) => ev[k]).length) + (runeReader(S) && !f.sf_mirror ? 1 : 0);
  const n = Math.min(3, read + free);
  return { read, free, n, done: n >= 3 && read >= 1 };
}
Object.assign(QUESTS, {
  mp_gate: { title: 'The Armed Crossing', giver: 'Guildmaster Aud Rainholt', story: true, steps: {
    1: (S) => { const f = F(S);
      return !f.mg_aud ? "Show Guildmaster Aud you're a proven Gate Runner, and armed." : !f.mg_key ? 'Collect the heat-sealed key from Gatewright Halvard.' : 'Open the red arch, and face what comes through.'; },
    2: 'Tell Aud the crossing is open.',
    3: "Muspelheim's gate is open. Dress for heat.",
  } },
  mp_walk: { title: 'The Cinder Walk', giver: 'Ember-Warden Aska Cindervane', story: true, steps: {
    1: (S) => { const n = F(S).mw_stones || 0; return n < 5 ? `Cross the Warden's Walk, stone by stone. ${n}/5` : 'Reach the Warden.'; },
    2: "Stand before the Warden's seat.",
    3: "Cinderhold has seen your steps. The Warden says they were 'steady'.",
  } },
  mp_sigil: { title: 'The Mirror Sigil', giver: 'Ember-Warden Aska Cindervane', story: true, steps: {
    1: (S) => `Find out how the Lantern Eve sigil was made. ${sigil(S).n}/3`,
    2: 'Tell the Warden what you found.',
    3: 'The sigil is a fake. Cinderhold was framed.',
  } },
  mp_kindle: { title: 'A Spark for Kindle', giver: 'Yrsa Brightwell', story: true, steps: {
    1: (S) => `Warm Kindle back to her flame. ${found(S, 'ks_hot', 'ks_song', 'ks_glass')}/3`,
    2: 'Take Kindle to the Caldera mouth.',
    3: 'Kindle burns bright again, and follows you.',
  } },
  mp_take: { title: 'The Ashen Toll', giver: 'Envoy Sunndis Embervane', story: true, steps: {
    1: (S) => { const n = found(S, 'at_b1', 'at_b2', 'at_b3'); return n < 3 ? `Douse the fire-bowls. ${n}/3` : (F(S).at_captain ? 'Take the Caldera Key.' : 'Beat Cinder-Captain Dagny Flameguard.'); },
    2: 'Open the Caldera.',
    3: 'The Caldera Key is yours. Cinderhold will not forget.',
  } },
  mp_hire: { title: 'Ash Wages', giver: 'Gatewright Halvard', story: true, steps: { 1: "Hear the Warden's terms, and meet Grettir at the lizard stables.", 2: 'Rebuild the seals: rebind Vharzul.', 3: 'Paid in full.' } },
  caldera: { title: 'The Ember Caldera', giver: 'Torka Ashgrip', story: true, steps: {
    1: (S) => { const n = found(S, 'cd_w1', 'cd_w2', 'cd_w3'); return n < 3 ? `Melt Veyra's frost wedges with fire. ${n}/3` : 'Face Vharzul on the Ember Throne.'; },
    2: (S) => ((F(S).alliance || {}).muspelheim === 'conquer' ? 'Leave with the crown.' : 'Tell the Warden the Throne is sealed.'),
    3: 'Vharzul is quiet again.',
  } },
  mp_sword: { title: 'Emberfang', giver: 'Torka Ashgrip', ripple: true, steps: {
    1: (S) => `Bring 3 heart-coals from the Caldera's deep vents. ${found(S, 'hc_1', 'hc_2', 'hc_3')}/3`,
    2: 'Watch Torka quench the blade.', 3: 'Emberfang is yours.' } },
  mp_lizard: { title: 'The Lizard That Chose You', giver: 'Orm Kettlebrand', ripple: true, steps: {
    1: (S) => `Win a young ember lizard's trust: a cinder-berry a day, three days. ${Math.min(3, F(S).ml_berries || 0)}/3`,
    2: 'Ride one lap of the terraces. (Orm is still fitting the saddle: the lizard mount arrives with the mounts.)',
    3: 'Your lizard. Her name is Smoulder.' } },
  emberfall: { title: 'Emberfall', giver: 'Torka Ashgrip', bounty: true, steps: {
    1: (S) => { const g = S.emberfall || {}; return `Forge ${g.forge || 0}/3, dance ${g.dance ? 1 : 0}/1, coal run ${g.run ? 1 : 0}/1.`; },
    2: 'Collect your prize from Torka.', 3: 'Champion of Emberfall, until next week.' } },
});

// ------------------------------------------------------------------ companion: Kindle (story 5.4). COMP table + the follower kit (jotunheim: ulfar). Her sheet comes with the art pack (role `kindle`);
// until a sheet has the role the follower is just "with you" (flag, swap, toast). ember_dash = a fast bite-rush that leaves a burn patch; warm_ring = heals 10 HP/s in 3 m for 4 s (cd 20 s).
export const KINDLE = { name: 'Kindle', scale: 1.0, follow: 1.4, hp: 150, skills: ['ember_dash', 'warm_ring'],
  aura: { fireResist: 1.0, frostSlowImmune: true, lightsTorches: true }, lines: 'kindle',
  say: { first: "I'll go first. I'm warm. You're squishy.", rude: "That one's rude. Burn it.", bead: 'Cold bead. Keep it. It\'s nice.', emberBorn: 'You smell like home.', faint: '(Kindle curls into a coal. She will be back at the waystone.)' } };
Object.assign(COMP, { kindle: 'Kindle' });   // one active companion at a time (swap at the Guild desk or any inn)
Object.assign(FOLLOW_KIT, { kindle: { role: 'pet_kindle', dist: 1.3, speed: 3.2, scale: KINDLE.scale, brawl: { dmg: 14, reach: 1.4, cd: 1.8, knock: 0.5 }, light: '#ff7a1a',
  follow: [KINDLE.say.first, KINDLE.say.rude, KINDLE.say.bead] } });   // warm_ring (heal ring) + ember_dash burn patch arrive with the Caldera build

// ------------------------------------------------------------------ shared quest steps (module level so TALK can use them)
export const SIGIL_TEXT = {   // story 4.2: the three Sigil Forge clues (areas: mp_hall; spot positions come with the area)
  sf_cast: ['(The cooling bed. A scrap of the Lantern Eve sigil sits on the iron beside a real seal.)', 'The real seals cool orange from the edge in. The fake cooled blue from the middle out: a frost core.'],
  sf_ledger: ["(The seal ledger. Every seal is accounted for. One entry is smudged where a pale-furred visitor 'asked to see the casting'.)", 'Someone small and pale was shown the foundry, and the ledger blushed.'],
  sf_mirror: ["(The sigil mould wall. You hold Hearthmoor's sigil up to the real flame.)", 'The real flame curls right. The fake curls left. Someone cast from a reflection.'],
};
function finishWalk(G) {
  const f = flags(G.S); G.setQuest('mp_walk', 3); f.mp_trusted = 1; G.factions.add('embassy', MERIT.mp_walk, 'mp_walk'); gold(G, 20);
  f.realm_mood = { ...(f.realm_mood || {}), muspelheim: Math.max(3, (f.realm_mood || {}).muspelheim || 0) };
  if (!q(G.S, 'mp_sigil')) G.setQuest('mp_sigil', 1);
  mark(G);
}
function closeSigil(G) {   // The Mirror Sigil done (story 3.3 / 4.3): the sigil is a fake, a rider carries the real seal to Hearthmoor
  const S = G.S, f = flags(S);
  G.setQuest('mp_sigil', 3); G.factions.add('embassy', MERIT.mp_sigil + (f.mp_prior ? MERIT.mp_rival : 0), 'mp_sigil'); gold(G, 40);   // the +20 is for a Niflheim conqueror (mood set before the Walk; the Walk itself raises the mood to 3)
  f.mp_cleared = 1; f.mp_peace = 1; S.evidence = { ...(S.evidence || {}), muspelheim: 'mirror_sigil' }; mark(G);
}
const WARDEN_OPTIONS = (S) => {   // Aska's choice (story 5.2 / muspelheim.md 1.1, Bill 2026-10-25): only the 4-ally cap greys befriend; a Niflheim friend (frost friend mark) may still befriend
  const lk = lockedBy(S), cap = allyCount(S) >= 4, opts = [];
  if (cap) opts.push({ label: '(Four realms already stand with you.)', locked: true, pick: () => ({ pages: ['Your friends are many. Mine are few. Another time.'] }) });
  else opts.push({ label: 'A friend. Let me clear your name.', pick: () => ({ pages: ['Then walk my stones. Fire trusts feet.'],
    then: (G) => { const ff = lockedBy(G.S); flags(G.S).mp_prior = mood(G.S) ? 1 : 0; if (ff) flags(G.S).mp_frostfriend = 1; ally(G.S).muspelheim = 'befriend'; lockRival(G.S, 'niflheim');
      G.setQuest(!ff && (mood(G.S) || emberBorn(G.S)) ? 'mp_sigil' : 'mp_walk', 1); G.toast('Muspelheim: befriended', 2.2); mark(G); } }) });
  opts.push({ label: "Midgard's. Hand over the Ember Crown.", pick: () => ({ pages: ['So Midgard is a thief. Take the Crown. Choke on it.'],
    then: (G) => { ally(G.S).muspelheim = 'conquer'; moodUp(G.S, 'niflheim'); G.setQuest('mp_take', 1); G.toast('Muspelheim: conquered', 2.2); mark(G); } }) });
  if (lk) opts.push({ label: '(Frost friend) The Guild sent me with an offer.', pick: () => ({ pages: ['An offer. Hm. Hear my terms: the seals are failing, and I will not turn down hands.'],
    then: (G) => { flags(G.S).mp_contract = 1; flags(G.S).mh_terms = 1; G.setQuest('mp_hire', 1); mark(G); } }) });
  return opts;
};

// ------------------------------------------------------------------ talk (TALK is keyed by the actor id in the area spec)
Object.assign(TALK, {
  envoy_mp(S) {   // Sunndis, at the Bifrost arch (look-spot) and then the hall door (actor); lines story 5.1
    const al = (F(S).alliance || {}).muspelheim;
    return { pages: [al === 'conquer' ? 'So you took the Crown by asking. Or by not asking. I keep the ledger either way.' : al === 'befriend' ? 'Mind the edge. It does not mind you. The Warden likes you; do not make her regret it.'
      : gateRank(S) < 2 ? "Muspelheim doesn't welcome tourists. Be a Gate Runner. Be armed." : "A runner, then. Aud will see your blade. Halvard has the key. Don't touch the hot end."] };
  },
  warden_mp(S) {
    const f = F(S), al = (f.alliance || {}).muspelheim, st = (k) => q(S, k);
    if (al === 'befriend' || f.mp_contract) {
      if (st('mp_walk') === 2 && f.mp_frostfriend && !f.mp_doorstep) {   // story 3.2a Cinder-Tea on the Doorstep (frost friend only); every answer is fine
        const ans = (label, line) => ({ label, pick: () => ({ pages: [line], then: (G) => { flags(G.S).mp_doorstep = 1; finishWalk(G); } }) });
        return { pages: ['You walked my stones with frost on your boots. They hissed the whole way. I enjoyed that.', 'Mistmere called us arsonists for a hundred winters. Now Mistmere sends me its friend. Why should fire trust a frost-friend?'],
                 choice: { id: 'mp_doorstep', options: [
                   ans("Because I'll ask you first. Same as I asked them.", "Ask first. Hm. That's a frost word. ...It's a good one. Drink your tea."),
                   ans("Somebody framed you both. I'd like to find out who.", 'Both? Then the frost-witches got a sigil too? ...Drink. Then tell me everything.'),
                   ans("(Shrug) The tea's good.", "It is. Svala's. Don't tell Mistmere we have nice things.") ] } };
      }
      if (st('mp_walk') === 2) return { pages: ['Five stones, and no more than a hiss. Steady. Fire trusts feet.', 'Now the hard thing: the sigil Midgard blames us for. The Sigil Forge is behind my seat. Look at how it was made.'], then: finishWalk };
      if (st('mp_sigil') === 2 && sigil(S).done) return { pages: ['Blue from the middle out. A ledger that blushes. A flame that curls left.', 'So we were framed, by something that hates warmth. I will send a rider to Hearthmoor with the real seal.', mood(S) ? 'You broke the frost-witches? Then you are warm company. Sit.' : 'Cinderhold remembers who read the cast.'], then: closeSigil };
      if (st('mp_sigil') === 1) return { pages: [`The Sigil Forge is behind my seat. Three clues: the cooling bed, the ledger, the mould wall. ${sigil(S).n}/3.`] };
      if (st('caldera') === 2 && f.cd_bound) return { pages: ['The Flame sank into the Throne, and the chains lit? Then Vharzul sleeps. For now.', 'Cinderhold thanks you. Torka will teach you what the fire teaches.'],
        then: (G) => { G.setQuest('caldera', 3); G.factions.add(f.mp_contract ? 'gate' : 'embassy', f.mp_contract ? MERIT.caldera_c : MERIT.caldera, 'caldera'); gold(G, 150); if (f.mp_contract) G.setQuest('mp_hire', 3); flags(G.S).mp_resolved = 1; mark(G); } };
      if (al === 'befriend') return { pages: [st('mp_walk') === 1 ? 'Then walk my stones. Fire trusts feet.' : 'The fire is for everyone. Sit.'] };
      return { pages: ['Hear my terms: Grettir waits at the stables. He is burned, and he is right, mostly.'] };
    }
    if (al === 'conquer') return { pages: ['So Midgard is a thief. Take the Crown. Choke on it.'] };
    return { pages: [mood(S) ? 'You broke the frost-witches? Then you are warm company. Sit.' : lockedBy(S) ? 'A friend of the frost, in my hall. Say it quick.' : 'Midgard blames us for a sigil. Frost blames us for a war. Who are you?'],
             choice: { id: 'mp_warden', options: WARDEN_OPTIONS(S) } };
  },
  forgejudge(S) {   // Torka Ashgrip: the Caldera offer, the school (9.2), Emberfang, Emberfall (story 5.3, 3.7, 3.8, 3.10)
    const f = F(S), al = (f.alliance || {}).muspelheim;
    if (al === 'conquer') return { pages: ["You know the flame curls wrong. We all do.", 'The Caldera Key opens the door. It does not make the Throne agree.'] };
    if (!q(S, 'caldera') && (q(S, 'mp_sigil') >= 3 || f.mp_contract || al === 'conquer')) return { pages: ['Hot iron says what a smith won\'t. Let it.', "Veyra drove three frost wedges into the Throne's seals. Melt them with fire, then face what wakes."], then: (G) => { G.setQuest('caldera', 1); mark(G); } };
    const sc = school(S); if (sc) return sc;   // the Caldera school (I right after the Caldera, II / III as soon as the level allows)
    if (al === 'befriend' && q(S, 'caldera') === 3 && !q(S, 'mp_sword')) return { pages: ['The Throne sleeps. Good. There is a blade I have wanted to quench for a hundred winters. It needs three heart-coals.'], then: (G) => { G.setQuest('mp_sword', 1); mark(G); } };
    if (al === 'befriend' && q(S, 'mp_sword') === 2) return { pages: ['Three heart-coals. Good. Watch.', '(Torka sets the coals in the blade and quenches it. Blue runs down the fuller, once, and stays.)', 'Emberfang. Mind the cold line: it is a reminder.'],
      then: (G) => { const i = G.S.inv; i.heart_coal = Math.max(0, (i.heart_coal || 0) - 3); (G.S.bag = G.S.bag || []).push(EMBERFANG(G.S)); G.setQuest('mp_sword', 3); G.toast('You are given Emberfang (check your bag)', 3.0); mark(G); } };
    return schoolWait(S) || { pages: ['Hot iron says what a smith won\'t. Let it.'] };
  },
  springkeeper(S) {   // Yrsa Brightwell: A Spark for Kindle (story 3.4, 5.5)
    const f = F(S), al = (f.alliance || {}).muspelheim;
    if (al === 'befriend' && q(S, 'mp_sigil') >= 3 && !q(S, 'mp_kindle')) return { pages: ['Springs are shy. Whistle, and they bubble.', 'Kindle, there, is a young salamander whose flame went cold. A hot coal, a tune at the cool spring, and the blue bead she lost in a lava crack. Will you?'], then: (G) => { G.setQuest('mp_kindle', 1); mark(G); } };
    return { pages: ['Springs are shy. Whistle, and they bubble.'] };
  },
  lizardman(S) {   // Orm Kettlebrand: the lizard ripple (story 3.9, 5.5)
    const f = F(S), al = (f.alliance || {}).muspelheim, st = q(S, 'mp_lizard'), day = S.day || 0;
    if (!st && al === 'befriend' && (q(S, 'mp_walk') >= 3 || emberBorn(S))) return { pages: ['She bit you? Good. Biting is how lizards say hello.', 'A cinder-berry a day, from the same hand, three days running. Not two in one day.'], then: (G) => { G.setQuest('mp_lizard', 1); G.give('cinder_berry', 1); flags(G.S).ml_lastDay = day; mark(G); } };
    if (st === 1 && (f.ml_lastDay ?? -1) < day && (f.ml_berries || 0) < 3) return { pages: ['Another day, another cinder-berry. Hold it flat.'], then: (G) => { G.give('cinder_berry', 1); flags(G.S).ml_lastDay = day; } };
    return { pages: ['She bit you? Good. Biting is how lizards say hello.'] };
  },
  mp_trader(S) {
    const first = !(S.met || {}).mp_trader, ash = !!F(S).mp_ash;
    return { pages: [first ? 'Svala. Braziers, charms, tea. Everything here is spiced and sized for small ones, which is more work than you know.' : ash ? 'Prices are what they are. The lava crusted over. So did I.' : 'Charm, tea or lamp? The tea clears an ember storm. We tested it on a brazier.'],
             then: (G) => { met('mp_trader')(G); G.shopUI.show('mp_trader'); } };
  },
  cindercaptain(S) { return { pages: [(F(S).alliance || {}).muspelheim === 'conquer' ? 'Dagny Flameguard. Midgard wants the Crown? Douse my bowls first, small one.' : 'Dagny Flameguard. The Walk is mine. Mind the stones.'] }; },
  mp_guide(S) {   // Grettir, ex-cultist, the contract guide (story 3.6): no fighting, points out wedges; mentions the sigil (4.4)
    const f = F(S);
    if (f.mp_contract && f.mh_terms && !f.mh_grettir) return { pages: ["Guild? Good. I was Ashen once. I know the cultists' side-tunnel, and it skips the stair and the glass bridge.", '(He whispers.) The sigil in Hearthmoor? Flame curls the wrong way. Look at the mould wall, if you like. Not my business.'], then: (G) => { flags(G.S).mh_grettir = 1; mark(G); } };
    return { pages: [f.mp_contract ? 'I will point at the wedges. I will not fight. I have fought enough.' : 'The cultists burn what they cannot bow to. I stopped bowing.'] };
  },
  mp_a(S) { return { pages: ['Mind the lava. It minds nobody.'] }; },
  mp_b(S) { return { pages: [['The forges sing at dusk. Listen.', 'Frost-witches blame us. We blame the weather.'][(S.day || 0) % 2]] }; },
});

MARKER_HOOKS.push((id, S) => {
  const f = F(S), al = f.alliance && f.alliance.muspelheim;
  if (id === 'warden_mp') {
    if (!al && !f.mp_contract) return 'quest_mark';
    if ((al === 'befriend' || f.mp_contract) && (q(S, 'mp_walk') === 2 || (q(S, 'mp_sigil') === 2 && sigil(S).done) || (q(S, 'caldera') === 2 && f.cd_bound))) return 'quest_mark';
  }
  if (id === 'kindle' && al === 'befriend' && q(S, 'mp_kindle') === 1 && found(S, 'ks_hot', 'ks_song', 'ks_glass') === 3) return 'quest_mark';
  if (id === 'springkeeper' && al === 'befriend' && q(S, 'mp_sigil') >= 3 && !q(S, 'mp_kindle')) return 'quest_mark';
  if (id === 'forgejudge' && ((!q(S, 'caldera') && (q(S, 'mp_sigil') >= 3 || f.mp_contract || al === 'conquer')) || (al === 'befriend' && ((q(S, 'caldera') === 3 && !q(S, 'mp_sword')) || q(S, 'mp_sword') === 2)))) return 'quest_mark';
  if (id === 'forgejudge' && school(S)) return 'quest_mark';   // a Caldera school lesson is ready
  if (id === 'lizardman' && al === 'befriend' && ((!q(S, 'mp_lizard') && q(S, 'mp_walk') >= 3) || (q(S, 'mp_lizard') === 1 && (f.ml_lastDay ?? -1) < (S.day || 0) && (f.ml_berries || 0) < 3))) return 'quest_mark';
  if (id === 'envoy_mp' && al === 'conquer' && q(S, 'mp_take') === 1) return 'quest_mark';
  if (id === 'mp_guide' && f.mp_contract && f.mh_terms && !f.mh_grettir) return 'quest_mark';
});

// ------------------------------------------------------------------ the module
export class Muspelheim {
  constructor(G) { this.G = G; G.markLifts = { ...(G.markLifts || {}), warden_mp: 2.8, forgejudge: 2.8 };   // the 5 m giants carry the quest tag above the head (game.js markLift)
    this.ctx = null; this.area = null; this.planned = MUSP_PLANNED; this.fx = []; this.lights = []; this.spots = []; this.cb = {}; this.pend = []; this.wfx = {}; this.relit = null; this.relitFx = []; this.relitLt = []; this.boss = null; this.kiln = null; this.qaDone = null; this.gate = new MpGate(this); this.wrap(); }
  qs() { return this.G.qs || new URLSearchParams(location.search); }
  wrap() {   // E / A and tap try the realm's interactables first (same chained hook as Alfheim's / Svartalfheim's / Jotunheim's)
    const G = this.G, me = this; if (!G.harbor) return;
    const p0 = G.harbor.prompt.bind(G.harbor), i0 = G.harbor.interact.bind(G.harbor), t0 = G.harbor.onTap.bind(G.harbor);
    G.harbor.prompt = (...a) => me.prompt() || p0(...a);
    G.harbor.interact = (...a) => me.interact() || i0(...a);
    G.harbor.onTap = (hit, ...a) => me.onTap(hit) || t0(hit, ...a);
    if (G.hollows) { const c0 = G.hollows.onCast.bind(G.hollows); G.hollows.onCast = (...a) => { const r = c0(...a); me.onCast(); return r; }; }   // a spell cast beside a frost wedge melts it
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
    const e = C.spawnEnemy({ once: true, noRespawn: true, ...sp }, true); e.state = 'chase';
    const done = () => { delete this.cb[sp.id]; (yielded && sp.trial ? yielded : then)(e); };
    e.onKill = done; if (yielded) e.onYield = done; this.cb[sp.id] = done;
    return e;
  }
  moveTo(x, z) { const c = this.ctx; if (!c) return; c.player.x = x; c.player.z = z; c.player.y = c.heightAt(x, z); }

  // QA preset (smoke / screenshots): ?muq=open (gate only) | befriend | frostfriend (Niflheim friend at the Walk turn-in, 3.2a) | walk | sigil | kindle | conquer | contract | done | school (the Caldera done, befriend: Torka's lessons)
  qaPreset() {
    const v = this.qs().get('muq'), S = this.G.S; if (!v || this.qaDone === v) return;
    this.qaDone = v;
    const open = () => { flags(S).mp_gate_open = 1; S.quests.mp_gate = 3; };
    if (v === 'befriend' || v === 'walk') { ally(S).muspelheim = 'befriend'; open(); S.quests.mp_walk = 1; }
    if (v === 'sigil') { ally(S).muspelheim = 'befriend'; open(); S.quests.mp_walk = 3; flags(S).mp_trusted = 1; S.quests.mp_sigil = 1; }
    if (v === 'kindle') { ally(S).muspelheim = 'befriend'; open(); S.quests.mp_walk = 3; S.quests.mp_sigil = 3; flags(S).mp_cleared = 1; S.quests.mp_kindle = 1; }
    if (v === 'caldera') { ally(S).muspelheim = 'befriend'; open(); S.quests.mp_walk = 3; S.quests.mp_sigil = 3; flags(S).mp_cleared = 1; S.quests.caldera = 1; }
    if (v === 'conquer') { ally(S).muspelheim = 'conquer'; open(); S.quests.mp_take = 1; }
    if (v === 'frostfriend') { flags(S).rivals = { ...(flags(S).rivals || {}), muspelheim: 'locked' }; flags(S).mp_frostfriend = 1; ally(S).muspelheim = 'befriend'; open(); S.quests.mp_walk = 2; flags(S).mw_stones = 1; }
    if (v === 'contract') { flags(S).rivals = { ...(flags(S).rivals || {}), muspelheim: 'locked' }; flags(S).mp_contract = 1; flags(S).mh_terms = 1; open(); S.quests.mp_hire = 1; }
    if (v === 'open') open();
    if (v === 'school') { ally(S).muspelheim = 'befriend'; open(); S.quests.mp_walk = 3; S.quests.mp_sigil = 3; flags(S).mp_cleared = 1; flags(S).mp_trusted = 1; S.quests.caldera = 3; flags(S).cd_bound = 1; }
    if (v === 'done') { ally(S).muspelheim = 'befriend'; open(); S.quests.mp_walk = 3; S.quests.mp_sigil = 3; flags(S).mp_cleared = 1; flags(S).mp_trusted = 1; }
  }
  attach(ctx, area) {
    this.detach(); this.ctx = ctx; this.area = area;
    if (area === 'bifrost') { this.qaPreset(); this.gate.atBifrost(ctx); this.bifrost(ctx); return; }
    if (!AREAS_MUSP[area]) return;
    this.qaPreset();
    if (area === 'muspelheim') this.hub(ctx);
    if (area === 'mp_hall') this.hall(ctx);
    if (area === 'lavafalls') this.falls(ctx);
    if (area === 'caldera') this.calderaRooms(ctx);
    if (area === 'caldera2') this.deepRooms(ctx);
    this.mpfx(ctx, area);
  }
  detach() {
    for (const f of this.fx) if (f) f.dur = f.t + 0.2;
    for (const l of this.lights) if (l) l.kill = true;
    this.fx = []; this.lights = []; this.spots = []; this.cb = {}; this.pend = []; this.wfx = {}; this.relit = null; this.relitFx = []; this.relitLt = []; this.boss = null; this.kiln = null; this.ambushed = false; this.cults = false; this.burnT = 0; this.ctx = null; this.area = null;
  }
  // ---- area hooks. Skeleton: only the hub's gate wiring is real; the rest are filled in with their area builds (see MUSPELHEIM_PROGRESS.md)
  // The Warden's Walk (story 3.2): five stones over the lava channel at z 3 (warden_stones at [0, 3]). Step on all five in order from either end; a wrong stone hisses and you start again.
  // (The 1.5 s cool cycle of each stone is not built: the stones are steady for now, see MUSPELHEIM_PROGRESS.md.)
  hub(ctx) {
    this.gate.atHub(ctx); this.walk = { next: 0, dir: 0, last: -1, t: 0 }; this.hubQuests(ctx);
    this.spot({ id: 'mp_stones', pos: [0, 4.4], r: 1.6, label: "the Warden's Stones (E / A)", show: () => q(this.G.S, 'mp_walk') === 1 && !F(this.G.S).mw_stones,
               act: () => this.look('mw_hint', "The Warden's Stones", ['(Five black stones over the lava channel, hissing. Step on each in turn, end to end. A wrong step and the stone sulks.)']) });
  }
  walkTick(dt = 0) {
    const c = this.ctx, G = this.G, S = G.S, w = this.walk; if (!c || !w || this.area !== 'muspelheim' || G.dlg || q(S, 'mp_walk') !== 1 || F(S).mw_stones) return;
    const XS = [-1.6, -0.8, 0, 0.8, 1.6];
    w.t = (w.t || 0) + dt;
    const i = XS.findIndex((x) => Math.hypot(c.player.x - x, c.player.z - 3.0) < 0.42);
    if (i < 0 || i === w.last) return;
    w.last = i;
    // the 1.5 s cool cycle (story 3.2): each stone is hot for the last 0.5 s of its own 1.5 s beat, staggered by stone; a hot stone sulks (start again) and stings. ?mwalk=steady keeps the stones cool (QA / accessibility)
    if (this.qs().get('mwalk') !== 'steady' && ((w.t + i * 0.37) % 1.5) > 1.0) {
      w.next = 0; w.dir = 0; w.last = -1; G.toast('The stone is hot! It stings. Start again.', 1.6);
      if (G.combat && G.combat.hurtPlayer && (S.hp || 0) > 8) G.combat.hurtPlayer(3, { x: XS[i], z: 3.0, fire: true }, 0);
      return;
    }
    if (w.next === 0 && (i === 0 || i === 4)) { w.dir = i === 0 ? 1 : -1; w.next = 1; return; }
    if (w.next > 0 && i === (w.dir > 0 ? w.next : 4 - w.next)) { w.next++; if (w.next >= 5) { flags(S).mw_stones = 1; G.setQuest('mp_walk', 2); G.toast('The last stone cools under you. Back to Aska.', 3.0); mark(G); } return; }
    w.next = 0; w.dir = 0; G.toast('The stone hisses. Start again.', 1.6);
  }
  // The Sigil Forge clues (story 4.2): cooling bed, ledger, mould wall; the quest moves to stage 2 once enough are in (free clues from the cleared realms count, one must be read here)
  hall(ctx) {
    const G = this.G, S = G.S, f = F(S);
    const read = (k, name) => () => {
      const first = !F(S)[k];
      this.look(k, name, SIGIL_TEXT[k], () => { flags(S)[k] = 1; if (q(S, 'mp_sigil') === 1 && sigil(S).done) { G.setQuest('mp_sigil', 2); G.toast('That is enough. Show Aska.', 3.0); } mark(G); });
      return first;
    };
    this.spot({ id: 'sf_cast', pos: [-3.2, -3.0], r: 1.7, label: 'the cooling bed (E / A)', show: () => q(S, 'mp_sigil') >= 1 && !f.sf_cast, act: read('sf_cast', 'The cooling bed') });
    this.spot({ id: 'sf_ledger', pos: [-3.2, -0.4], r: 1.5, label: 'the seal ledger (E / A)', show: () => q(S, 'mp_sigil') >= 1 && !F(S).sf_ledger, act: read('sf_ledger', 'The seal ledger') });
    this.spot({ id: 'sf_mirror', pos: [-5.8, -1.6], r: 1.7, label: 'the sigil mould wall (E / A)', show: () => q(S, 'mp_sigil') >= 1 && !F(S).sf_mirror, act: read('sf_mirror', 'The sigil mould wall') });
  }
  // The Caldera mouth (story 2.5, 4.4): three seal-doors, one per path. The Caldera areas open with their builds; until then the doors only speak.
  falls(ctx) {
    const G = this.G, S = G.S, mine = () => q(S, 'mp_kindle') === 1;
    this.spot({ id: 'caldera_mouth', pos: [0, -6.0], r: 2.0, label: 'the Caldera mouth (E / A)', show: () => true, act: () => this.mouth() });
    this.spot({ id: 'ks_song', pos: [-6.6, 5.4], r: 2.0, label: 'the cool spring: whistle (E / A)', show: () => mine() && !(S.found || {}).ks_song,
      act: () => this.look('ks_song', 'The cool spring', ['(Kindle sits on the rim of the cool spring and listens. You whistle the first tune that comes to you, badly. The spring bubbles, politely, in key.)', '(Kindle hums along, a single warm note.)'], () => { this.find('ks_song'); G.toast('The tune 2/3', 2.2);
        if (found(S, 'ks_hot', 'ks_song', 'ks_glass') >= 3 && q(S, 'mp_kindle') === 1) { G.setQuest('mp_kindle', 2); G.toast('Kindle is warm again. Take her to the Caldera mouth.', 3.0); } mark(G); }) });
  }
  // ---- the pack's animated pools / flames / motes (MP_FX) + small helpers
  fxAt(ctx, name, x, y, z, o = {}) {
    if (!ctx || !ctx.gamefx || !ctx.gamefx.meta.effects[name]) return null;
    const f = ctx.gamefx.spawn(name, x, y, z, { duration: Infinity, fadeIn: this.G.qaStill ? 0 : 0.6, ...o }); this.fx.push(f); return f;
  }
  dropFx(f) { if (f) f.dur = f.t + 0.2; }
  mpfx(ctx, area) {   // effects that would sit on a standing actor (or the start spot) are left out: a billboard over a sprite breaks its pixel grid (check_scene sprites_sharp).
    // A billboard at height y reads on screen like a ground point 1.9 m * y further north, so its footprint is tested against each actor's sprite column (height in m: giants 5, foes 3.4, folk 2.2)
    if (this.qs().get('mpfx') === '0') return;   // QA: ?mpfx=0 leaves the pack's fx out (isolates what a check_scene failure comes from)
    const H = (role) => (['warden_mp', 'forgejudge', 'cindercaptain', 'fire_golem', 'kilnmother'].includes(role) ? 5.0 : ['magma_hound', 'flame_elemental', 'ashalpha', 'pyreling'].includes(role) ? 3.4 : 2.2);
    const near = [[ctx.player.x, ctx.player.z, 1.6], ...(ctx.actors && ctx.actors.list ? ctx.actors.list.map((a) => [a.x, a.z, H(a.role)]) : []), ...(SPAWNS[area] || []).map((sp) => [sp.pos[0], sp.pos[1], H(sp.role)])];
    for (const [name, [x, z], dy] of MP_FX[area] || []) {
      const e = ctx.gamefx && ctx.gamefx.meta.effects[name], decal = e && e.kind === 'decal', ez = z - 1.9 * dy;
      if (near.some(([ax, az, h]) => (decal ? Math.hypot(ax - x, az - z) < 1.5 : Math.abs(ax - x) < 1.5 && ez > az - 1.9 * h - 0.3 && ez < az + 0.8))) continue;
      this.fxAt(ctx, name, x, ctx.heightAt(x, z) + dy, z);
    }
  }
  find(k) { const S = this.G.S; S.found = { ...(S.found || {}), [k]: 1 }; this.G.save && this.G.save(); }
  strike(kind, x, z, dmg, delay, r) {   // a telegraphed hit: the pack's molten_fist / pillar_telegraph decal marks the spot, then the flame lands (fire_pillar) and hurts what stands in it
    const c = this.ctx; if (!c) return;
    this.fxAt(c, kind === 'fist' ? 'molten_fist' : 'pillar_telegraph', x, c.heightAt(x, z), z, { duration: delay, fadeIn: 0 });
    this.pend.push({ t: delay, x, z, dmg, r, kind });
  }
  tickStrikes(dt) {
    const c = this.ctx, p = c && c.player; if (!c || !this.pend.length) return;
    this.pend = this.pend.filter((s) => {
      s.t -= dt; if (s.t > 0) return true;
      if (s.kind !== 'fist') this.fxAt(c, 'fire_pillar', s.x, c.heightAt(s.x, s.z), s.z, { duration: 0.7, fadeIn: 0 });
      if (Math.hypot(p.x - s.x, p.z - s.z) < s.r && this.G.combat && this.G.combat.hurtPlayer) this.G.combat.hurtPlayer(s.dmg, { x: s.x, z: s.z, fire: true }, 0.5);
      return false;
    });
  }
  // ---- weather: the ember storm burns open ground (2 dmg / s) unless something keeps the fire off you (Kindle, a fire-ward charm, a spring's fizz, cinder-tea)
  fireRes() { const G = this.G, S = G.S; return compActive(S) === 'kindle' || !!((S.inv || {}).fire_ward) || !!(G.combat && G.combat.ward) || !!(G.hollows && G.hollows.buffT > 0) || this.teaT > 0 || (this.qs().get('mwx') === 'safe'); }   // + the Caldera school's Flame Ward
  weatherTick(dt) {
    const c = this.ctx, G = this.G, kind = G.weather ? G.weather.kind : 'clear';
    if (!(this.area === 'muspelheim' || this.area === 'lavafalls') || kind !== 'ember_storm' || G.dlg || this.fireRes()) { this.burnT = 0; return; }
    this.burnT = (this.burnT || 0) + dt;
    if (this.burnT >= 1.0) {
      this.burnT = 0; const p = c.player, C = G.combat;
      if (C && C.hurtPlayer && (G.S.hp || 0) > 12) C.hurtPlayer(2, { x: p.x, z: p.z, fire: true }, 0);
      if (!this.burnSaid) { this.burnSaid = true; G.toast('The ember storm scorches you. Kindle, a fire-ward charm, Flame Ward, a spring or cinder-tea keeps the fire off.', 3.0); }
    }
  }
  // ---- Kindle (story 5.4): warm_ring (10 HP/s in 3 m for 4 s, cd 20 s, when you are below 60%), ember_dash (a bite-rush at the nearest foe + a burn patch, cd 11 s)
  kindleTick(dt) {
    const G = this.G, S = G.S, F2 = G.svart && G.svart.follow, c = this.ctx;
    if (!c || !F2 || !F2.on || F2.id !== 'kindle' || !F2.sprite) return;
    const C = G.combat, sp = F2.sprite, p = c.player; this.kdash = Math.max(0, (this.kdash || 0) - dt); this.kring = Math.max(0, (this.kring || 0) - dt);
    if (this.kringT > 0) { this.kringT -= dt; if (C && Math.hypot(sp.x - p.x, sp.z - p.z) < 3.0) S.hp = Math.min(C.maxHp(), (S.hp || 0) + 10 * dt); }
    if (C && this.kring <= 0 && (S.hp || 0) < C.maxHp() * 0.6 && (S.hp || 0) > 0) {
      this.kring = 20; this.kringT = 4; this.fxAt(c, 'warm_ring_orange', p.x, p.y, p.z, { duration: 4, fadeIn: 0.2 }); F2.bark && F2.bark('Warm. Stay close.');
    }
    if (C && this.kdash <= 0 && C.enemies) {
      let best = null, bd = 6.0;
      for (const e of C.enemies) { if (!e.a || e.state === 'dead' || e.state === 'gone') continue; const d = Math.hypot(e.a.x - sp.x, e.a.z - sp.z); if (d < bd) { bd = d; best = e; } }
      if (best) {
        this.kdash = 11; C.damageEnemy(best, 14, { x: sp.x, z: sp.z }, 0.5);
        this.fxAt(c, 'burn_patch', best.a.x, c.heightAt(best.a.x, best.a.z), best.a.z, { duration: 3, fadeIn: 0.1 });
      }
    }
  }
  // ---- Cinderhold: Kindle's three warmings, the fire-bowls + Dagny (conquer), Orm's lizard
  hubQuests(ctx) {
    const G = this.G, S = G.S, f = F(S), day = () => S.day || 0;
    const mine = () => q(S, 'mp_kindle') === 1, got = (k) => !!(S.found || {})[k], check = () => { if (found(S, 'ks_hot', 'ks_song', 'ks_glass') >= 3 && q(S, 'mp_kindle') === 1) { G.setQuest('mp_kindle', 2); G.toast('Kindle is warm again. Take her to the Caldera mouth.', 3.0); } mark(G); };
    this.spot({ id: 'ks_hot', pos: [3.4, -0.4], r: 1.8, label: 'a hot coal in the forge-trough (E / A)', show: () => mine() && !got('ks_hot'),
      act: () => this.look('ks_hot', 'The forge-trough', ['(A coal as big as a fist, still orange in the middle. You lift it with the tongs. Kindle leans in and does not blink.)'], () => { this.find('ks_hot'); G.toast('Warm coal 1/3', 2.2); check(); }) });
    this.spot({ id: 'ks_glass', pos: [7.4, 0.6], r: 1.8, label: 'a crack in the glass walk (E / A)', show: () => mine() && !got('ks_glass'),
      act: () => this.look('ks_glass', 'The lava crack', ['(Deep in the crack, past the red, something small and blue winks. You fish it out on a hooked wire: a cold, cold bead.)'], () => { this.find('ks_glass'); G.toast('Blue bead 3/3', 2.2); check(); }) });
    // the Ashen Toll (conquer, story 3.5): three fire-bowls with two Ashen Cultists each, then Cinder-Captain Dagny; she yields at 25 % and hands over the Caldera Key
    const BOWLS = [[8.0, -2.0], [3.6, 7.0], [-3.6, 7.0]];
    BOWLS.forEach(([x, z], i) => {
      const n = i + 1, k = 'at_b' + n;
      this.spot({ id: 'tb' + n, pos: [x, z], r: 1.8, label: 'a fire-bowl (E / A: douse it)', show: () => q(S, 'mp_take') === 1 && !got(k), act: () => {
        if (this.cb[k + 'a'] || this.cb[k + 'b']) return this.look('at_busy' + n, 'The fire-bowl', ['The bowl-wardens are already on you.']);
        this.look(k, 'The fire-bowl', ['A fire-bowl of the Warden\'s Walk, banked and bright. Two Ashen Cultists crouch beside it, tending. They look up.'], () => {
          let left = 2;
          const dead = () => { if (--left > 0) return; this.find(k); delete this.cb[k + 'a']; delete this.cb[k + 'b']; G.toast(`Fire-bowl ${n} doused.`, 2.4); mark(G); };
          ['a', 'b'].forEach((t, j) => this.foe({ id: k + t, role: 'ashen_cultist', pos: [x + (j ? 1.6 : -1.6), z - 1.4] }, dead));
        });
      } });
    });
    this.spot({ id: 'captain', pos: [0.0, -5.2], r: 2.0, label: "Dagny Flameguard's post (E / A)", show: () => q(S, 'mp_take') === 1 && BOWLS.every((_, i) => got('at_b' + (i + 1))) && !f.at_captain && !this.cb.dagny, act: () => this.captain() });
    // the young ember lizard at the stables (story 3.9): one cinder-berry a day, three days, then she is yours (the saddle / the mount ride is not in the game yet)
    this.spot({ id: 'ml_lizard', pos: [-9.6, 1.6], r: 1.8, label: () => (q(S, 'mp_lizard') === 2 ? 'the young ember lizard: name her (E / A)' : 'the young ember lizard (E / A)'), show: () => q(S, 'mp_lizard') >= 1 && q(S, 'mp_lizard') < 3, act: () => this.lizard() });
  }
  lizard() {
    const G = this.G, S = G.S, f = flags(S), day = S.day || 0, st = q(S, 'mp_lizard');
    if (st === 2) return this.look('ml_name', 'The young ember lizard', ['(She butts your hand, then your knee, then sits on your foot, warm as a bread oven.)', '"Her name is Smoulder," Orm says, not looking up. "I did not name her. She named herself."'], () => {
      G.setQuest('mp_lizard', 3); S.pets = S.pets || {}; S.pets.smoulder = S.pets.smoulder || { name: 'Smoulder', bond: 1, fed: 0, lastFed: null }; G.toast('Smoulder is yours. (The saddle comes with the mounts.)', 3.0); mark(G);
    });
    if (!(S.inv || {}).cinder_berry) return this.look('ml_none', 'The young ember lizard', ['(She sniffs your empty hand and looks at Orm. Orm shrugs. "One a day, from the same hand. Ask me for the day\'s berry.")']);
    if ((f.ml_fed ?? -1) >= day) return this.look('ml_fed', 'The young ember lizard', ['(She is full of berry and suspicion. One a day, not two.)']);
    this.look('ml_feed', 'The young ember lizard', ['(You hold the berry flat. She takes it with great delicacy, and then takes your sleeve as well.)'], () => {
      S.inv.cinder_berry = Math.max(0, (S.inv.cinder_berry || 0) - 1); f.ml_fed = day; f.ml_berries = (f.ml_berries || 0) + 1;
      if (f.ml_berries >= 3) { G.setQuest('mp_lizard', 2); G.toast('She trusts you. Visit her again.', 2.8); } else G.toast(`Cinder-berry ${f.ml_berries}/3`, 2.0);
      mark(G);
    });
  }
  captain() {
    const G = this.G, S = G.S;
    if (this.cb.dagny) return;
    this.look('at_captain', 'Cinder-Captain Dagny Flameguard', ['"Three bowls out. A small one, and a ledger of cinders at my feet. Hm. My pride says no, the ash says yes."', '"Show me. If you can lay me on my back, the Key is yours."'], () => {
      this.foe({ id: 'dagny', role: 'cindercaptain', def: 'dagny', pos: [0.0, -8.0], trial: true }, () => {}, (e) => {
        delete this.cb.dagny; const f = flags(S); f.at_captain = 1; f.caldera_key = 1; G.give('caldera_key', 1); G.setQuest('mp_take', 2);
        this.look('at_key', 'Cinder-Captain Dagny Flameguard', ['(Dagny lowers her glowing blade, breathing hard.) "Enough. You have the arm for it."', '"The Caldera Key. It opens the door. It does not make the Throne agree."']);
        mark(G);
      });
    });
  }
  // ---- the Ember Caldera C1-C4: the ambush at the gate, Seal tablets, the glass bridge, the furnace hall
  wedges(ctx) {
    const S = this.G.S;
    Object.entries(WEDGE).filter(([, w]) => w[0] === this.area).forEach(([k, [, x, z]]) => {
      if (!(S.found || {})[k]) this.wfx[k] = this.fxAt(ctx, 'frost_vein', x, ctx.heightAt(x, z), z);
      this.spot({ id: k, pos: [x, z], r: 2.0, label: () => ((this.G.S.found || {})[k] ? 'the melted wedge' : "Veyra's frost wedge (E / A)"),
        act: () => ((this.G.S.found || {})[k] ? this.look(k + '_m', 'The melted wedge', ['A black stain in the stone where the frost wedge was. The seal beside it glows.']) : this.look(k + '_w', "Veyra's frost wedge", ['A wedge of blue-white ice, driven into the seal by someone small and careful. It hums, cold, against the heat.', '(Any spell cast close by would melt it.)'])) });
    });
  }
  melt(k) {
    const c = this.ctx, S = this.G.S, w = WEDGE[k]; if (!c || !w || (S.found || {})[k]) return false;
    this.find(k); this.dropFx(this.wfx[k]); this.wfx[k] = null;
    this.fxAt(c, 'steam_puff', w[1], c.heightAt(w[1], w[2]) + 0.4, w[2], { duration: 1.6, fadeIn: 0 });
    const n = found(S, 'cd_w1', 'cd_w2', 'cd_w3'); this.G.toast(n >= 3 ? "The last wedge melts. The Throne's seals glow." : `The wedge sweats and cracks (${n}/3).`, 2.6); mark(this.G); return true;
  }
  onCast() {   // a spell cast within 3 m of a frost wedge melts it
    const c = this.ctx, p = c && c.player; if (!c || !p) return;
    for (const [k, [a, x, z]] of Object.entries(WEDGE)) if (a === this.area && Math.hypot(p.x - x, p.z - z) < 3.0) this.melt(k);
  }
  hcSpots(ctx) {   // heart-coals for Emberfang (mp_sword): C4 furnace, C6 behind Kilnmother's altar, C7 by the springs
    const G = this.G, S = G.S;
    HC.filter(([, a]) => a === this.area).forEach(([k, , pos]) => {
      const live = () => q(S, 'mp_sword') === 1 && !(S.found || {})[k];
      if (live()) this.fxAt(ctx, 'neon_embers', pos[0], ctx.heightAt(pos[0], pos[1]) + 0.4, pos[1]);
      this.spot({ id: k, pos, r: 1.7, label: 'a heart-coal (E / A)', show: live, act: () => this.look(k, 'Heart-coal', ['A coal from the Caldera\'s deep vents. It is hotter than the room, and it does not go out.'], () => {
        this.find(k); G.give('heart_coal', 1);
        if (HC.every(([kk]) => (S.found || {})[kk])) { G.setQuest('mp_sword', 2); G.toast('Three heart-coals. Take them to Torka.', 2.8); }
        mark(G);
      }) });
    });
  }
  calderaRooms(ctx) {
    const G = this.G, S = G.S;
    this.spot({ id: 'cd_tab1', pos: [3.8, -14.4], r: 1.8, label: 'a seal tablet (E / A)', act: () => this.look('cd_t1', 'Seal tablet', ['"THE GLASS REMEMBERS FIRE. ONLY WHERE IT STILL GLOWS WILL IT BEAR YOU."', '(Warm lines of light run through the glass ahead. The dark panes between them look thin.)']) });
    this.spot({ id: 'cd_tab0', pos: [-3.6, 6.0], r: 1.8, label: 'a seal tablet (E / A)', act: () => this.look('cd_t0', 'Seal tablet', ['"THE WARDENS CUT THE THRONE A COLD SPRING, FAR DOWN. DRINK, AND THE FIRE FORGIVES YOU."', '(A scratched bird beneath it. Veyra\'s mark.)']) });
    GLASS.LIT.forEach((cols, r) => cols.forEach((col) => { const [x, z] = glassCentre(col, r); this.fxAt(ctx, 'pool_forge', x, ctx.heightAt(x, z), z); }));
    this.wedges(ctx); this.hcSpots(ctx);
    this.ambushed = !!(S.found || {}).cd_c1 || this.ambushed;
  }
  caldera1() {   // C1: two magma hounds come off the walls as you step onto the stair
    const G = this.G, S = G.S; if (this.ambushed || (S.found || {}).cd_c1) return; this.ambushed = true;
    let left = 2; const dead = () => { if (--left > 0) return; this.find('cd_c1'); delete this.cb.cd_h0; delete this.cb.cd_h1; };
    G.toast('Hounds drop off the wall!', 2.0);
    [[-5.2, -1.8], [5.2, -1.8]].forEach(([x, z], i) => this.foe({ id: 'cd_h' + i, role: 'magma_hound', pos: [x, z] }, dead));
  }
  caldera2c() {   // C2: two ashen cultists step out of the dark beside the seal tablet once you are past the stair
    const G = this.G, S = G.S; if (this.cults || (S.found || {}).cd_c2) return; this.cults = true;
    let left = 2; const dead = () => { if (--left > 0) return; this.find('cd_c2'); delete this.cb.cd_cult0; delete this.cb.cd_cult1; };
    [-4.6, 4.6].forEach((x, i) => this.foe({ id: 'cd_cult' + i, role: 'ashen_cultist', pos: [x, -10.4] }, dead));
  }
  // ---- the Throne rooms C5-C9: Veyra's seam, the Kilnmother, springs + waystone, Vharzul
  deepRooms(ctx) {
    const G = this.G, S = G.S;
    this.wedges(ctx); this.hcSpots(ctx);
    this.spot({ id: 'cd_tab5', pos: [-3.8, 4.4], r: 1.8, label: 'a seal tablet (E / A)', act: () => this.look('cd_t5', 'Seal tablet', ['"THE COLD SEAM. WHERE A FIRE-KING SLEPT, SOMEONE HAS TAUGHT THE ROCK TO BE COLD."']) });
    this.spot({ id: 'cd_tab7', pos: [-6.6, -40.8], r: 1.8, label: 'a seal tablet (E / A)', act: () => this.look('cd_t7', 'Seal tablet', ['"VHARZUL EMBERTHRONE. HE HELD THE FIRE WHEN THE FIRE WAS A CHILD. LET HIM SLEEP, IF HE WILL."', '"THREE LAMPS IN HIS HALL. LET NONE BURN WHEN HE BREAKS."']) });
    this.spot({ id: 'cd_tab8', pos: [-1.0, -38.4], r: 1.8, label: 'a seal tablet (E / A)', act: () => this.look('cd_t8', 'Seal tablet', ['"THE WAYSTONE BURNS WHEN IT KNOWS YOU. COME BACK, WHEN YOU HAVE BEEN WARMED."']) });
    LAMPS.forEach(([x, z], i) => this.spot({ id: 'lamp' + (i + 1), pos: [x, z + 1.6], r: 2.0, label: "the relit Warden's lamp (E / A: snuff it)", show: () => !!(this.relit && this.relit[i]), act: () => this.snuffLamp(i) }));
  }
  caldera2Tick() {
    const G = this.G, c = this.ctx, p = c.player, S = G.S, f = F(S);
    if (G.dlg || G.busy || !G.combat) return;
    if (!(S.found || {}).cd_veyra && p.z < 4.0) {
      this.find('cd_veyra'); flags(S).mp_veyra = 1;
      this.look('cd_veyra', 'A small, hooded figure', ['(Frost-veins crawl along the seam, and a hooded figure no taller than you turns at the very edge of the light. She is smiling.)', '"Warm all the way down. How sweet. The Throne is hungry, little hearth. Feed it, or feed it a lesson."', '(She is gone, and the seam is a little colder where she stood.)']);
      return;
    }
    if (p.z < -5.0 && !(S.found || {}).cd_kiln && !this.cb.kilnmother) this.kilnStart();
    if (p.z < THRONE.z && !(S.found || {}).cd_boss && !this.cb.vharzul) this.bossStart();
  }
  kilnStart() {
    const G = this.G, S = G.S;
    G.toast('The Kilnmother wakes: "Who walks my kiln?"', 2.6);
    this.kiln = this.foe({ id: 'kilnmother', role: 'kilnmother', def: 'kilnmother', pos: [0.0, -13.0] }, () => { this.find('cd_kiln'); G.toast('The Kilnmother cools. The chapel is quiet.', 2.6); this.kiln = null; });
    this.kt = 2;
  }
  bossStart() {
    const G = this.G, S = G.S; if (this.cb.vharzul || (S.found || {}).cd_boss) return;
    G.toast('"WHO WAKES THE EMBER THRONE?"', 3.0);
    this.boss = this.foe({ id: 'vharzul', role: 'vharzul', def: 'vharzul', pos: THRONE.boss.slice() }, () => this.vharzulDown());
    this.bt = 3; this.bt2 = 0;
  }
  tickKiln(dt) {
    const e = this.kiln, p = this.ctx.player; if (!e || e.state === 'dead' || e.state === 'gone') return;
    if (Math.hypot(e.a.x - p.x, e.a.z - p.z) > 9) return;
    this.kt = (this.kt || 0) - dt; if (this.kt <= 0) { this.kt = 4.6; this.strike('fist', p.x, p.z, 22, 0.9, 1.7); }
  }
  tickVharzul(dt) {
    const e = this.boss, c = this.ctx, p = c.player, G = this.G; if (!e || e.state === 'dead' || e.state === 'gone') return;
    const fr = e.hp / e.D.hp, ph = fr < e.D.phases[1] ? 3 : fr < e.D.phases[0] ? 2 : 1; e.phaseN = ph;
    this.bt -= dt; if (this.bt <= 0 && Math.hypot(e.a.x - p.x, e.a.z - p.z) < 13) { this.bt = ph === 1 ? 5.4 : 4.0; this.strike('pillar', p.x, p.z, 24, 1.0, 1.5); if (ph >= 2) this.strike('pillar', p.x + (Math.random() < 0.5 ? -2.4 : 2.4), p.z - 1.2, 24, 1.3, 1.5); }
    if (ph >= 2 && !e.p2) {
      e.p2 = 1; G.toast('Two flame elementals spiral out of the vents. The edges of the hall burn!', 3.0);
      THRONE.elems.forEach(([x, z], i) => this.foe({ id: 'vz_m' + (i + 1), role: 'flame_elemental', pos: [x, z] }, () => {}));
    }
    if (ph >= 2 && Math.abs(p.x) > 8.0 && p.z < -42 && !G.dlg) { this.edgeT = (this.edgeT || 0) + dt; if (this.edgeT > 1) { this.edgeT = 0; if (G.combat && G.combat.hurtPlayer && !this.fireRes()) G.combat.hurtPlayer(3, { x: p.x < 0 ? -9.4 : 9.4, z: p.z, fire: true }, 0.2); } }
    if (ph >= 3 && !e.p3) { e.p3 = 1; e.p3t = 0; e.healT = 0; this.relit = [0, 0, 0]; this.snuffed = [0, 0, 0]; G.toast("The three Warden's lamps gutter back to life. Snuff them, or he mends!", 3.2); }
    if (e.p3) {   // P3: the lamps relight one by one; each lit one mends him until you snuff it
      e.p3t += dt;
      LAMPS.forEach(([x, z], i) => {
        if (!this.relit[i] && !this.snuffed[i] && e.p3t > 3 + 4 * i) {
          this.relit[i] = 1; const y = c.heightAt(x, z);
          this.relitFx[i] = this.fxAt(c, 'warden_lamp', x, y + 3.2, z, { duration: Infinity, fadeIn: 0.3 });
          if (c.addGlow) { this.relitLt[i] = c.addGlow(x, y, z, { color: '#ffb066', intensity: 2.2, range: 3.4, lift: 2.6, fadeIn: 0.4 }); this.lights.push(this.relitLt[i]); }
          G.toast(`A lamp relights (${this.relit.filter(Boolean).length}/3). Snuff it, or he mends.`, 2.0);
        }
      });
      e.healT += dt; const n = this.relit.filter(Boolean).length;
      if (e.healT > 2) { e.healT = 0; if (n) e.hp = Math.min(e.hp + e.D.hp * 0.012 * n, e.D.hp * 0.3); }
    }
  }
  snuffLamp(i) {
    const G = this.G; if (!this.relit || !this.relit[i]) return;
    this.relit[i] = 0; this.snuffed[i] = 1; this.dropFx(this.relitFx[i]); this.relitFx[i] = null; if (this.relitLt[i]) this.relitLt[i].kill = true; this.relitLt[i] = null;
    G.toast(`Lamp snuffed (${this.relit.filter(Boolean).length}/3 still burning).`, 2.0);
  }
  vharzulDown() {
    const G = this.G, S = G.S, f = flags(S), al = (f.alliance || {}).muspelheim, conq = al === 'conquer';
    this.find('cd_boss'); this.boss = null;
    for (let i = 0; i < 3; i++) { this.dropFx(this.relitFx[i]); if (this.relitLt[i]) this.relitLt[i].kill = true; }
    this.relit = null;
    if (!q(S, 'caldera')) G.setQuest('caldera', 1);
    if (conq) {
      this.find('cd_crown'); f.mp_ash = 1; f.cd_crown = 1; G.give('ember_crown', 1); G.setQuest('caldera', 3); G.factions.add('gate', MERIT.caldera_c, 'caldera_c'); gold(G, 150);
      this.look('cd_crown', 'Vharzul the Ember Throne', ['(The Throne cracks along its seams. You lift a cooling crown of black iron out of the embers.)', '(Far away, the braziers of Cinderhold gutter low. Cinderhold will not forget who took it.)']);
    } else {
      f.cd_bound = 1; G.setQuest('caldera', 2);
      this.look('cd_bound', 'Vharzul the Ember Throne', ['(The Flame slides out of you and into the Throne. The chains along the floor light, one by one, and hold.)', '"Sleep," says something in the fire. "Tell the Warden... the seals will keep."']);
    }
    mark(G);
  }
  // ---- the Caldera mouth door: ways in and the Kindle ending
  mouth() {
    const G = this.G, S = G.S, f = F(S), al = (f.alliance || {}).muspelheim;
    if (q(S, 'mp_kindle') === 2) return this.look('ks_finish', 'The Caldera mouth', ['(Kindle slides down your arm, climbs the arch, and sits in the open mouth of the Caldera. A long breath, and she lights: red, then orange, then a proud, small gold.)', '"There," she says, in a voice like a cinder settling. "I am warm. I will go first. You are squishy."'], () => {
      G.setQuest('mp_kindle', 3); G.factions.add('embassy', MERIT.mp_kindle, 'mp_kindle'); compUnlock(G, 'kindle'); compSwap(G, 'kindle');
      S.pets = S.pets || {}; S.pets.kindle = S.pets.kindle || { name: 'Kindle', bond: 1, fed: 0, lastFed: null };
      mark(G);
    });
    const d = al === 'befriend' && q(S, 'mp_sigil') >= 3 ? 'flame' : al === 'conquer' && (S.inv || {}).caldera_key ? 'key' : f.mp_contract ? 'tunnel' : null;
    if (!d) return this.look('cm_shut', 'The Caldera mouth', ['(Three seal-doors under a six-metre arch. The left bears a flame, the middle a lock, the right a crack no wider than a man.)', "None of them will open for you yet. The Warden's Flame, the Caldera Key, or Grettir's tunnel: one of them has to be yours."]);
    const how = d === 'flame' ? "(The Warden's Flame lights the left door. It swings in on heat, and then on darkness.)" : d === 'key' ? '(The key-fire burns the lock open.)' : "(Grettir's crack breathes cold ash. He said it skips the stair and the glass bridge.)";
    this.look('cm_open', 'The Caldera mouth', [how], () => {
      if (!q(S, 'caldera') && d !== 'key') G.setQuest('caldera', 1);
      if (d === 'key' && q(S, 'mp_take') === 2) { G.setQuest('mp_take', 3); G.factions.add('gate', MERIT.ashtoll, 'ashtoll'); gold(G, 120); }
      if (d === 'tunnel' && q(S, 'mp_hire') === 1) G.setQuest('mp_hire', 2);
      G.save && G.save(); G.loadArea('caldera', d === 'tunnel' ? 'tunnel' : 'from_falls');
    });
  }
  // ---- Bifrost: The Armed Crossing look-spots (story 3.1). Hidden while no Muspelheim area is built.
  bifrost() {
    const G = this.G, S = G.S, open = () => gateOpen(S, this.qs());
    this.spot({ id: 'sunndis', pos: [-9.4, -4.6], r: 1.3, label: 'Envoy Sunndis Embervane (E / A)', show: () => live() && !open(), act: () => this.sunndis() });
    this.spot({ id: 'aud', pos: [-8.0, -2.9], r: 1.3, label: 'Guildmaster Aud Rainholt (E / A)', show: () => live() && (!open() || q(S, 'mp_gate') === 2), act: () => this.aud() });
    this.spot({ id: 'halvard_key', pos: [-3.4, 0.9], r: 1.4, label: 'Gatewright Halvard: the heat-sealed key (E / A)', show: () => live() && !!F(S).mg_aud && !F(S).mg_key, act: () => this.key() });
    this.spot({ id: 'arch', pos: [-11.0, -4.2], r: 1.5, label: 'the red arch: open it (E / A)', show: () => live() && !!F(S).mg_key && !F(S).mg_hound && !open(), act: () => this.openArch() });
  }
  sunndis() { const S = this.G.S; this.look('mg_sunndis', 'Envoy Sunndis Embervane', TALK.envoy_mp(S).pages); }
  aud() {
    const G = this.G, S = G.S, f = flags(S), A = 'Guildmaster Aud Rainholt';
    if (q(S, 'mp_gate') === 2) return this.look('mg_done', A, ['The hound at the arch? You walked it down. Then the crossing is open.', "Dress for heat, Runner."], () => {
      f.mp_gate_open = 1; G.setQuest('mp_gate', 3); G.factions.add('gate', MERIT.mp_gate, 'mp_gate'); gold(G, 50); this.gate.reopen(); mark(G);
    });
    if (G.factions.rank('gate') < 2) return this.look('mg_no', A, ["Muspelheim is no friend to mortals. I send only proven Gate Runners through, and they go armed. Come back with more marks."]);
    if (!armed(S)) return this.look('mg_unarmed', A, ["You are a Runner, but where is your blade? Equip a weapon (G, the gear page). I will not send a bare hand into that heat."]);
    if (!f.mg_aud) return this.look('mg_aud', A, ['A Runner, and armed. Good. Halvard has the heat-sealed key. It went into the wrong kiln. Carry it with the tongs.'], () => { f.mg_aud = 1; G.setQuest('mp_gate', 1); mark(G); });
    this.look('mg_wait', A, [f.mg_key ? 'Open the arch. Stand back. Then do not stand back.' : 'Halvard has the key. Do not touch the hot end.']);
  }
  key() {
    const G = this.G, f = flags(G.S);
    this.look('mg_key', 'Gatewright Halvard', ['The key? It came out of the kiln hot, and cooking is a crime in this job. (He passes it with a pair of tongs.)', 'No sprinting for ten seconds, if you value your hands.'], () => {
      f.mg_key = 1; G.give('heat_key', 1); this.noSprint = 10; G.toast('You carry the heat-sealed key with the tongs.', 2.6); mark(G);
    });
  }
  openArch() {   // Bifrost has no Muspelheim foe sheets: the hound comes through on the Cinderhold side (spawned by update() on arrival), like Jotunheim's troll
    const G = this.G, f = flags(G.S);
    this.look('mg_open', 'The red arch', ['(You slot the key. The arch flares red, and you are pulled through.)'], () => { f.mg_opened = 1; G.save && G.save(); G.loadArea('muspelheim', 'from_bifrost'); });
  }
  gateHound() {
    const G = this.G, f = flags(G.S);
    this.foe({ id: 'mg_hound', role: 'magma_hound', def: 'magma_hound_gate', pos: [0, 6.2] }, () => { f.mg_hound = 1; G.setQuest('mp_gate', 2); G.toast('The hound falls. Tell Aud at Bifrost.', 2.8); mark(G); });
  }
  update(dt) {
    if (!this.ctx) return;
    const S = this.G.S;
    if (this.area === 'muspelheim' && !this.G.dlg && !this.G.busy && this.G.combat && F(S).mg_opened && !F(S).mg_hound && !this.cb.mg_hound) this.gateHound();
    this.walkTick(dt); this.weatherTick(dt); this.kindleTick(dt); this.tickStrikes(dt);
    if (this.teaT > 0) this.teaT -= dt;
    if (this.area === 'caldera2') { this.caldera2Tick(); this.tickKiln(dt); this.tickVharzul(dt); }
    if (this.area === 'caldera' && !this.G.dlg && !this.G.busy && this.G.combat && this.ctx.player.z < 3.0) this.caldera1();
    if (this.area === 'caldera' && !this.G.dlg && !this.G.busy && this.G.combat && this.ctx.player.z < -3.0) this.caldera2c();
    if (this.area === 'caldera' && this.ctx.player.y > 1.9 && this.ctx.player.z < GLASS.z0 && this.ctx.player.z > GLASS.endZ && !(S.found || {}).cd_glass) this.glassTick();
    if (this.noSprint > 0) this.noSprint = Math.max(0, this.noSprint - dt);   // the tongs: story 3.1 (the 10 s no-sprint rule is enforced with the hub build)
  }
  glassTick() {   // C3: a dark pane cracks and drops you back at the bridge head; the far end is safe for good
    const c = this.ctx, p = c.player, G = this.G, S = G.S;
    const t = glassTile(p.x, p.z);
    if (t && !GLASS.LIT[t[1]].includes(t[0])) return this.crack(t);
  }
  crack(t) {
    const c = this.ctx, p = c.player, G = this.G, [x, z] = glassCentre(t[0], t[1]);
    this.gfalls = (this.gfalls || 0) + 1;
    this.fxAt(c, 'steam_puff', x, c.heightAt(x, z) + 0.4, z, { duration: 1.4, fadeIn: 0 });
    G.toast('The dark glass cracks under you! Back to the bridge head. Only the glowing panes hold.', 2.4);
    p.x = GLASS.head[0]; p.z = GLASS.head[1]; p.y = c.heightAt(p.x, p.z);
    if (G.combat && G.combat.hurtPlayer) G.combat.hurtPlayer(5, { x, z }, 0);
  }
  // QA helpers for the smoke test
  qaMelt(k) { return this.melt(k); }
  qaBoss(w) { if (w === 'kiln') this.kilnStart(); else this.bossStart(); return !!(this.cb.kilnmother || this.cb.vharzul); }
  qaHp(id, frac) { const e = this.G.combat.enemies.find((x) => x.id === id); if (!e) return false; e.hp = e.D.hp * frac; return true; }
  qaTick(dt = 0.1, n = 1) { for (let i = 0; i < n; i++) { this.tickVharzul(dt); this.tickKiln(dt); this.tickStrikes(dt); } return this.qaBossState(); }
  qaBossState() { const e = this.boss; return { phase: e ? e.phaseN : 0, p2: !!(e && e.p2), p3: !!(e && e.p3), relit: this.relit ? [...this.relit] : null, snuffed: this.snuffed ? [...this.snuffed] : null, pend: this.pend.length, hp: e ? e.hp : null, scale: e ? e.D.scale : null, framed: e ? !!e.D.framed : null, ids: this.G.combat ? this.G.combat.enemies.filter((x) => x.state !== 'dead' && x.state !== 'gone').map((x) => x.id) : [] }; }
  qaSnuff(i) { this.snuffLamp(i); return this.qaBossState(); }
  qaGlass(col, row) { const [x, z] = glassCentre(col, row), c = this.ctx; this.moveTo(x, z); this.glassTick(); return { gfalls: this.gfalls || 0, z: +c.player.z.toFixed(2), lit: GLASS.LIT[row].includes(col) }; }
  qaFire() { return { res: this.fireRes(), kind: this.G.weather ? this.G.weather.kind : null }; }
  qaHeal() { const S = this.G.S; return { hp: S.hp, ring: this.kringT || 0 }; }
  qaLine(id) { const e = TALK[id](this.G.S); return e && e.pages ? e.pages[0] : null; }
  qaTalk(id) { const e = TALK[id](this.G.S); if (e && e.then) e.then(this.G); return { pages: e ? e.pages.length : 0, choice: e && e.choice ? e.choice.options.map((o) => o.label) : null, locked: e && e.choice ? e.choice.options.filter((o) => o.locked).map((o) => o.label) : null }; }
  qaPick(label, id = 'warden_mp') { const e = TALK[id](this.G.S), o = e.choice.options.find((x) => x.label === label), nx = o.pick(this.G); if (nx && nx.then) nx.then(this.G); return nx ? nx.pages.length : 0; }
  qaRares() { const c = this.ctx, sp = (RARE_AREAS[this.area] || { spots: [] }).spots; return { spots: sp }; }
  qaSpot(id) { const sp = this.spots.find((x) => x.id === id); if (!sp) return false; sp.act(); return true; }
  qaDefs() {   // the realm's shared-table registrations, for the smoke
    const E = ENEMIES.vharzul;
    return { quests: Object.keys(QUESTS).filter((k) => ['mp_gate', 'mp_walk', 'mp_sigil', 'mp_kindle', 'mp_take', 'mp_hire', 'caldera', 'mp_sword', 'mp_lizard', 'emberfall'].includes(k)).length,
             merit: Object.fromEntries(Object.keys(MERIT).filter((k) => ['mp_gate', 'ashtoll', 'mp_contract', 'caldera_c', 'mp_walk', 'mp_sigil', 'mp_rival', 'mp_kindle', 'caldera', 'emberfall'].includes(k)).map((k) => [k, MERIT[k]])),
             vharzul: { scale: E.scale, framed: E.framed, plate: E.plate, element: E.element, boss: E.boss, phases: E.phases },
             foes: ['magma_hound', 'magma_hound_gate', 'flame_elemental', 'fire_golem', 'ashen_cultist', 'kilnmother', 'dagny', 'vharzul'].filter((k) => ENEMIES[k]), bases: ['ashalpha', 'pyreling'].filter((k) => BASES[k]),
             wx: { ash_fall: !!WX_KINDS.ash_fall, ember_storm: !!WX_KINDS.ember_storm }, comp: COMP.kindle || null, kit: !!FOLLOW_KIT.kindle, shop: !!SHOPS.mp_trader,
             items: ['heat_key', 'ember_sigil_copy', 'caldera_key', 'heart_coal', 'cinder_berry', 'cinder_tea', 'fire_ward', 'brazier_lamp', 'ember_crown'].filter((k) => ITEMS[k]).length,
             talk: ['envoy_mp', 'warden_mp', 'forgejudge', 'springkeeper', 'lizardman', 'mp_trader', 'cindercaptain', 'mp_guide'].filter((k) => TALK[k]).length };
  }
  qaSchool() { const f = F(this.G.S), C = this.G.combat; return { flags: { i: !!f.cs_i, ii: !!f.cs_ii, iii: !!f.cs_iii }, unlock: !!(this.G.S.unlocks || {}).caldera_school, spells: SCHOOL.filter((n) => (this.G.S.spells || []).includes(n)),
    defs: SCHOOL.filter((n) => SPELLS[n] && SPELL_NAMES[n]).length, mark: (MARKER_HOOKS.map((h) => h('forgejudge', this.G.S)).find((m) => m !== undefined)) || null, lv: CS_LV, cal: C && C.qaCaldera ? C.qaCaldera() : null }; }
  qaFang() { const it = EMBERFANG(this.G.S); return { name: it.name, unique: it.unique, slot: it.slot, rar: it.rar }; }
  qaKill(id) { const f = this.cb[id]; if (!f) return false; f(); return true; }
  qa() {
    const c = this.ctx, S = this.G.S, f = F(S), gm = c ? (c.scene.game || {}) : {};
    return { realm: 'muspelheim', built: Object.keys(AREAS_MUSP), planned: MUSP_AREAS, area: this.area, exits: (gm.exits || []).map((e) => e.to), portals: (gm.portals || []).map((p) => p.to),
             spots: this.spots.filter((x) => x.show()).length, gate: this.gate.qa(), alliance: (f.alliance || {}).muspelheim || null, rival: (f.rivals || {}).muspelheim || null, rivals: { ...(f.rivals || {}) }, moods: { ...(f.realm_mood || {}) }, dlg: this.G.dlg ? this.G.dlg.npc.id : null, mood: (f.realm_mood || {}).muspelheim || 0,
             contract: !!f.mp_contract, allies: allyCount(S), sigil: sigil(S), evidence: (S.evidence || {}).muspelheim || null, companions: Object.keys(f.companions || {}),
             quests: Object.fromEntries(['mp_gate', 'mp_walk', 'mp_sigil', 'mp_kindle', 'mp_take', 'mp_hire', 'caldera', 'mp_sword', 'mp_lizard', 'emberfall'].map((k) => [k, q(S, k)])),
             flags: { aud: !!f.mg_aud, key: !!f.mg_key, hound: !!f.mg_hound, open: !!f.mp_gate_open, trusted: !!f.mp_trusted, cleared: !!f.mp_cleared, peace: !!f.mp_peace, stones: !!f.mw_stones },
             actors: c ? c.actors.list.map((a) => a.id || a.role) : [], fx: this.fx.length, lights: this.lights.length, gold: S.gold || 0 };
  }
}

// ------------------------------------------------------------------ the gate (story 3.1): runtime wiring on both ends, like jotunheim.js's JtGate (no Bifrost rebuild)
class MpGate {
  constructor(mp) { this.mp = mp; this.G = mp.G; this.fetching = false; }
  get ctx() { return this.mp.ctx; }
  qs() { return this.mp.qs(); }
  put(sc) { const gm = (sc.game = sc.game || {}); gm.spawns = gm.spawns || {}; if (!gm.spawns.from_muspelheim) gm.spawns.from_muspelheim = MP_ARCH.spawn.slice(); }
  atHub(ctx) {   // Cinderhold: the red arch back to Bifrost (runtime portal) + the Bifrost scene prefetched with its return spawn
    const G = this.G, gm = ctx.scene.game || (ctx.scene.game = {});
    gm.portals = gm.portals || [];
    if (!gm.portals.find((p) => p.to === 'bifrost')) gm.portals.push({ ...HUB_GATE, rect: HUB_GATE.rect.slice() });
    if (G.scenes && G.scenes.bifrost) { this.put(G.scenes.bifrost); return; }
    if (this.fetching || !G.scenes) return;
    this.fetching = true;
    fetch('areas/bifrost/scene.json').then((r) => r.json()).then((sc) => { if (!G.scenes.bifrost) G.scenes.bifrost = sc; this.put(G.scenes.bifrost); }).catch(() => {}).finally(() => { this.fetching = false; });
  }
  atBifrost(ctx) { this.put(ctx.scene); this.wire(ctx); }
  reopen() { if (this.ctx && this.mp.area === 'bifrost') this.wire(this.ctx); }
  wire(ctx) {   // the sealed red arch becomes a portal once the gate is open AND Cinderhold is built (dormant otherwise: the arch just stays sealed)
    const gm = ctx.scene.game; if (!gm || !live() || !gateOpen(this.G.S, this.qs())) return;
    gm.sealed = (gm.sealed || []).filter((g) => g.arch !== 'muspelheim');
    gm.portals = gm.portals || [];
    if (!gm.portals.find((p) => p.to === 'muspelheim')) gm.portals.push({ fx: 'gate_muspelheim', to: 'muspelheim', spawn: 'from_bifrost', rect: MP_ARCH.rect.slice(), label: "Muspelheim's gate" });
    (gm.spawns = gm.spawns || {}).from_muspelheim = gm.spawns.from_muspelheim || MP_ARCH.spawn.slice();
  }
  qa() { const c = this.ctx, gm = c ? (c.scene.game || {}) : {}; return { portals: (gm.portals || []).map((p) => p.to), sealed: (gm.sealed || []).map((g) => g.arch), spawns: Object.keys(gm.spawns || {}), open: gateOpen(this.G.S, this.qs()), live: live() }; }
}
