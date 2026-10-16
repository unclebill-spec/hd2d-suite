// [JOTUNHEIM] Jotunheim (realm-jotunheim branch), built from the Hearthmoor Story script (staging story/jotunheim.md) with Cozy Builder's
// rulings (Hrimgard 7x, Ulfar combat_scale 2.4 with no second sheet, Flurry's neon twin as the main look). Chunk 1 = the first area: Stonehollow
// (`jotunheim`). Quests / TALK / shops / the Bifrost gate merge into the shared tables from here, like svartalfheim.js, so shared files only
// carry a few marked hook lines. Planned and not built yet: see JOT_PLANNED + JOTUNHEIM_PROGRESS.md (RESUME HERE).
import { TALK, ITEMS, QUESTS, MARKER_HOOKS, SPELL_NAMES } from './data.js';
import { REALM, MERIT } from './factions.js';
import { ENEMIES, SPAWNS, SPELLS } from './heroes.js';
import { XP } from './progress.js';
import { SHOPS, GOODS } from './shop.js';
import { WAYS, WAY_SAY } from './ravenhold.js';
import { lockRival, moodUp } from './alfheim.js';
import { BASES, RARE_AREAS, Rares } from './rares.js';
import { RARITY, makeItem } from './loot.js';
import { KINDS as WX_KINDS, WX_HOOK } from './weather.js';
import { unlock as compUnlock, swap as compSwap, active as compActive } from './svartalfheim_companions.js';

export const JOT_PLANNED = {   // id -> display name (story 2.1); `barrow` (B1-B4) + `barrow2` (B5-B9) are the dungeon, two areas like clockdeep
  jotunheim: 'Stonehollow', jt_hall: 'Hall of Hearthstones', rimecaves: 'The Rime Caves', barrow: "The Titan's Barrow", barrow2: "The Titan's Barrow: the Throne",
};
export const AREAS_JOT = { jotunheim: 'areas/jotunheim/', jt_hall: 'areas/jt_hall/', rimecaves: 'areas/rimecaves/', barrow: 'areas/barrow/', barrow2: 'areas/barrow2/' };   // id -> 'areas/<id>/' (merged into game.js's area path map)
export const AREA_NAMES_JOT = { jotunheim: 'Stonehollow', jt_hall: 'Hall of Hearthstones', rimecaves: 'The Rime Caves', barrow: "The Titan's Barrow", barrow2: "The Titan's Barrow: the Throne" };   // id -> display name (merged into game.js's AREA_NAME)
export const JOT_AREAS = Object.keys(JOT_PLANNED);

const flags = (S) => (S.flags = S.flags || {});
const F = (S) => S.flags || {};
const q = (S, k) => (S.quests || {})[k] || 0;
const ally = (S) => (flags(S).alliance = flags(S).alliance || {});
const gold = (G, n) => { G.S.gold = (G.S.gold || 0) + n; G.toast(`+${n} gold`, 1.8); G.drawBag && G.drawBag(); };
const met = (k) => (G) => { G.S.met = { ...(G.S.met || {}), [k]: 1 }; };
Object.assign(REALM, { jotunheim: 'embassy', jt_hall: 'embassy', rimecaves: 'embassy', barrow: 'embassy', barrow2: 'embassy' });   // conquer / contract pay 'gate' with the alliance lock (later)
Object.assign(MERIT, { tollstones: 60, barrow: 120, jt_gate: 60, jt_welcome: 40, jt_heart: 60, jt_rival: 20, jt_ulfar: 80 });   // story 3.12 (the rest arrive with their quests)
WAYS.jotunheim = ['Stonehollow', 'jotunheim', 'from_waystone'];
WAYS.barrow2 = ["the Titan's Barrow, the Waystone Crypt", 'barrow2', 'from_waystone'];
Object.assign(WAY_SAY, { jotunheim: 'Cold-fire runes glow along the waystone, and the snow around it is trodden flat by giant boots.', barrow2: "A waystone older than the Barrow. The first Jarl's people set it here so the dead would never be far from home." });

export const JT_ARCH = { rect: [4.25, -12.3, 5.75, -11.45], pos: [5.0, -11.9], spawn: [5.0, -10.1, 'down'] };   // the ice arch on Bifrost's north wall
const HUB_GATE = { to: 'bifrost', spawn: 'from_jotunheim', rect: [-0.9, 10.1, 0.9, 11.1], label: 'the ice arch back to Bifrost Crossing' };
export const gateOpen = (S, qs) => !!(F(S).jt_gate_open || (F(S).alliance || {}).jotunheim || (qs && qs.has('jtq') && qs.get('jtq') !== 'gate'));   // QA: ?jtq=... opens it, except ?jtq=gate (Kolbrun's quest)   // QA: ?jtq=... (Kolbrun's jt_gate quest comes next chunk)


// ------------------------------------------------------------------ foes (story 8.4) + the Rime Caves' pools (story 2.5; rares frostmother / avalanche come with the BASES hook)
Object.assign(ENEMIES, {
  frost_troll: { name: 'Frost troll', hp: 130, dmg: 15, speed: 1.0, reach: 1.8, windup: 0.7, cd: 2.0, aggro: 6.5, r: 0.5, push: 0.25, heavy: true },
  ice_golem: { name: 'Ice golem', hp: 160, dmg: 16, speed: 0.9, reach: 1.7, windup: 0.8, cd: 2.2, aggro: 6, r: 0.5, push: 0.2, heavy: true, weakBelly: 1.4 },
  avalanche_golem: { name: 'Avalanche golem', hp: 190, dmg: 20, speed: 0.9, reach: 2.0, windup: 1.0, cd: 2.4, aggro: 6, r: 0.6, push: 0.15, heavy: true },
  rime_berserker: { name: 'Rime Berserker', hp: 90, dmg: 13, speed: 2.0, reach: 1.5, windup: 0.4, cd: 1.4, aggro: 7.5, r: 0.4, push: 0.5, elite: true },
  // story 8: the Barrow's three named foes (own sheets via jot_art EXTRA: boss_hrimgard / jtelite). Hrimgard 7x, Ormgar and Hjordis 3x.
  hrimgard: { name: 'Hrimgard the Unthawed', scale: 7, framed: true, hp: 1900, dmg: 28, speed: 0.8, reach: 5.5, windup: 0.9, cd: 2.4, aggro: 12, r: 2.0, push: 0.05, heavy: true, slam: true, boss: true,
              wave: { every: 3, r: 6.5, dmg: 22 }, minion: 'ice_golem', phases: [0.6, 0.25], glow: '#7fd4ff', legendary: true, respawn: 1e9 },
  ormgar: { name: 'Rime Berserker Chief Ormgar', scale: 3, hp: 420, dmg: 19, speed: 1.7, reach: 2.6, windup: 0.5, cd: 1.6, aggro: 9, r: 0.8, push: 0.2, heavy: true, boss: true, respawn: 1e9 },
  hjordis: { name: 'Rime-Captain Hjordis Icejaw', scale: 3, hp: 380, dmg: 17, speed: 1.2, reach: 2.4, windup: 0.6, cd: 1.8, aggro: 9, r: 0.8, push: 0.2, heavy: true, boss: true, trial: true, respawn: 1e9 },
});
Object.assign(XP, { frost_troll: 50, ice_golem: 60, avalanche_golem: 85, rime_berserker: 80, hrimgard: 900, ormgar: 220, hjordis: 0 });
// the Rime Caves' two rares (story 8.3), on the procedural-rare system (rares.js): own sheets `frostmother` (2.5x) and `avalanche` (3x) from jot_art EXTRA.
// Traits map onto the engine's: frostmother = frozen (a chill that saps stamina) + thick-hide (extra HP) + Summoner (calls frost trolls as whelps);
// avalanche = stone-skin (always Shielded) + quake (a rune shockwave every 4th slam).
Object.assign(BASES, {
  frostmother: { name: 'Frostmother', scale: 2.5, hp: 340, dmg: 15, speed: 1.1, reach: 2.6, windup: 0.7, cd: 2.0, aggro: 8, r: 0.75, push: 0.2, heavy: true, chill: 14, minion: 'frost_troll', xp: 190 },
  avalanche: { name: 'Avalanche', scale: 3, hp: 380, dmg: 18, speed: 0.95, reach: 2.8, windup: 0.85, cd: 2.2, aggro: 8, r: 0.85, push: 0.15, heavy: true, slam: true, wave: { every: 4, r: 3.4, dmg: 12 }, xp: 200 },
});
RARE_AREAS.rimecaves = { bases: ['frostmother', 'avalanche'], spots: [[5.2, -3.2], [-4.6, 2.6]] };   // clear of the braziers (+-3.6, -8.4), pools, pillars, Solvi (-8.2, -2.2) and the start view
const spawnRare0 = Rares.prototype.spawn;
Rares.prototype.spawn = function spawn(o = {}) {
  if (!o.traits && o.base === 'frostmother') o = { ...o, traits: ['summoner'] };
  if (!o.traits && o.base === 'avalanche') o = { ...o, traits: ['shielded'] };
  return spawnRare0.call(this, o);
};
SPAWNS.rimecaves = [   // giants are tall: day foes stand clear of the braziers / ice walls (phone portrait shows them at the top), night foes anywhere north of the camera's first view (off screen) and >= 3.5 m apart (phone portrait shows them at the top; overlapping giants fail sprites_sharp)
  { id: 'rc_troll0', role: 'frost_troll', pos: [-10.5, -11.3] }, { id: 'rc_golem1', role: 'ice_golem', pos: [-7.0, -11.3] },
  { id: 'rc_golem0', role: 'ice_golem', pos: [-3.5, -11.3], night: true }, { id: 'rc_avl0', role: 'avalanche_golem', pos: [0.0, -9.6] },
  { id: 'rc_zerk0', role: 'rime_berserker', pos: [3.5, -11.3], night: true }, { id: 'rc_zerk1', role: 'rime_berserker', pos: [7.0, -11.3], night: true },
  { id: 'rc_troll1', role: 'frost_troll', pos: [11.4, -11.3] },
];

SPAWNS.barrow2 = [   // B5-B9: the Frozen Echo is quiet; berserkers in the Berserker Hall, golems on the Rune Bridge, trolls in the crypt; Ormgar / Hrimgard are scripted (tbBoss)
  { id: 'b2_zerk0', role: 'rime_berserker', pos: [-5.6, -9.4] }, { id: 'b2_zerk1', role: 'rime_berserker', pos: [5.6, -9.4] },
  { id: 'b2_golem0', role: 'ice_golem', pos: [0.0, -21.0] }, { id: 'b2_golem1', role: 'ice_golem', pos: [0.0, -25.0], night: true },
  { id: 'b2_troll0', role: 'frost_troll', pos: [6.4, -34.6] }, { id: 'b2_troll1', role: 'frost_troll', pos: [-8.0, -32.6], night: true },
];
SPAWNS.barrow = [   // B1-B4: two frost trolls at the door hall, ice golems wake in the Hall of Shields / pools, avalanche golems at the top of the Run; none near the start view
  { id: 'bw_troll0', role: 'frost_troll', pos: [-5.6, -9.4] }, { id: 'bw_troll1', role: 'frost_troll', pos: [5.6, -9.4] },
  { id: 'bw_golem0', role: 'ice_golem', pos: [-3.6, -10.6] }, { id: 'bw_golem1', role: 'ice_golem', pos: [3.6, -10.6] }, { id: 'bw_golem2', role: 'ice_golem', pos: [0.0, -26.0] },   // the golems stand on the bank / the Run's foot, off the slide puzzle's ice
  { id: 'bw_avl0', role: 'avalanche_golem', pos: [-4.4, -28.0] }, { id: 'bw_avl1', role: 'avalanche_golem', pos: [4.4, -28.0] },
  { id: 'bw_zerk0', role: 'rime_berserker', pos: [-8.0, -12.0], night: true }, { id: 'bw_zerk1', role: 'rime_berserker', pos: [8.0, -12.0], night: true },
];

// ------------------------------------------------------------------ items + Grimsa's stall (story 5.5; prices are first guesses)
Object.assign(ITEMS, {
  fur_mantle: { name: 'Fur cloak', px: 'tonic', about: "Grimsa's fur cloak, cut down for a small one. Frost resist +20%, and a cosmetic mantle over your tunic." },
  oat_cake: { name: 'Oat-cake', px: 'denbiscuit', about: "Brynja's oat-cake, goat-sized. One a day, from the same hand, and a goat starts to trust it." },
  heart_ice: { name: 'Heart-ice', px: 'glowseed', about: 'A shard of ice that never melts and hums when you hold it. Solvi wants three for the Rimebreaker.' },
  barrow_key: { name: 'Barrow Key', px: 'tonic', about: "Three rune-iron keys wired into one. Hjordis Icejaw's. It opens the Titan's Barrow door, no questions asked." },
  coldfire_lantern: { name: 'Cold-fire lamp', px: 'glowseed', about: 'A lamp that burns the giants\' blue cold fire. It lights, it never burns. Light radius +2.' },
});
Object.assign(GOODS, {
  tea: GOODS.tea || { name: 'Moonpetal tea', about: "A tin of moonpetal tea. Calms storms and clears a frost slow.", price: 14 },
  fur_mantle: { name: 'Fur cloak', about: 'Frost resist +20%. A mantle of goat-fur and bear-fur, sized for someone small.', price: 90 },
  coldfire_lantern: { name: 'Cold-fire lamp', about: 'Burns blue and never burns you. Light radius +2.', price: 55 },
});
SHOPS.jt_trader = { name: "Grimsa's Stall", keeper: 'Grimsa, giant trader', goods: ['tea', 'fur_mantle', 'coldfire_lantern', 'tonic'], gear: { n: 3, rar: [0, 1, 1] }, sellMul: 1 };

// ------------------------------------------------------------------ quests (story 3.2)
Object.assign(QUESTS, {
  jt_welcome: { title: 'The Stone Welcome', giver: 'Jarl Thyra Stonebrow', story: true, steps: {
    1: (S) => { const n = Math.min(F(S).jw_lifts || 0, need(S)); return n < need(S) ? `Lift the Welcome stones (E / A on the glow). ${n}/${need(S)}` : 'Let the town cheer.'; },
    2: "Sit at the Jarl's fire.",
    3: 'Stonehollow has welcomed you. The goats are still suspicious.',
  } },
  jt_ulfar: { title: "Ulfar's Walk", giver: 'Ulfar Mossback', story: true, steps: {
    1: (S) => { const f = S.found || {}, n = ['uw_goat', 'uw_song', 'uw_mitten'].filter((k) => f[k]).length; return `Spend the day with Ulfar. ${n}/3`; },
    2: 'Walk Ulfar to the Barrow door.',
    3: 'Ulfar walks with you now.',
  } },
  jt_goat: { title: 'The Goat Who Chose You', giver: 'Brynja Hornwise', ripple: true, steps: {
    1: (S) => `Win Brynja's young goat's trust: an oat-cake a day, three days. ${Math.min(3, F(S).gt_cakes || 0)}/3`,
    2: "Ride one lap of the lake. (Brynja is still stitching the saddle: the goat mount arrives with the mounts.)",
    3: 'Your goat. Her name is Clatter.',
  } },
  jt_heart: { title: 'The Hollow Heart', giver: 'Jarl Thyra Stonebrow', story: true, steps: {
    1: (S) => { const f = F(S), n = ['jh_heart', 'jh_rime', 'jh_trail'].filter((k) => f[k]).length;
      return f.sv_decoy ? 'Show the Jarl the boot mould from Anvildeep.' : `Study the Heart in the ice cellar. ${n}/3`; },
    2: 'Tell the Jarl what you found.',
    3: 'The Heart is a fake. Stonehollow was framed.',
  } },
  jt_hire: { title: 'Rime Wages', giver: 'Gatewright Halvard', story: true, steps: { 1: 'Hear the Jarl\'s terms, and meet Skuli at the goat pens.', 2: 'Lay Hrimgard back to sleep.', 3: 'Paid in full.' } },
  barrow: { title: "The Titan's Barrow", giver: 'Rimewife Solvi', story: true, steps: {
    1: (S) => { const n = ['tb_b1', 'tb_b2', 'tb_b3'].filter((k) => (S.found || {})[k]).length; return n < 3 ? `Snuff Veyra's cold-fire braziers. ${n}/3` : 'Face Hrimgard in the Throne Barrow.'; },
    2: (S) => (F(S).alliance || {}).jotunheim === 'conquer' ? 'Leave with the crown.' : 'Tell the Jarl the king sleeps.',
    3: 'Hrimgard is quiet again.' } },
  jt_gate: { title: 'The Barred Gate', giver: 'Envoy Kolbrun Hailstride', story: true, steps: {
    1: (S) => { const f = F(S); return !f.jg_asked ? "Ask the giants' envoy at Bifrost to lift the bar." : !f.jg_horn ? "Fetch Kolbrun's horn from Gatewright Halvard." : 'Sound the horn at the ice arch, and face what answers.'; },
    2: 'Tell Kolbrun the bar is lifted.', 3: "The giants' gate is open. Mind your head." } },
  jt_axe: { title: 'The Rimebreaker', giver: 'Rimewife Solvi', ripple: true, steps: {
    1: (S) => `Bring 3 heart-ice from the Barrow. ${['hi_1', 'hi_2', 'hi_3'].filter((k) => (S.found || {})[k]).length}/3`,
    2: 'Take the heart-ice to Solvi in the Hall and watch her wake the axe.', 3: 'The Rimebreaker is yours.' } },
  jt_take: { title: 'The Toll of Stones', giver: 'Envoy Kolbrun Hailstride', story: true, steps: { 1: (S) => { const n = ['tt_c1', 'tt_c2', 'tt_c3'].filter((k) => (S.found || {})[k]).length; return n < 3 ? `Topple the watch-cairns in the Rime Caves. ${n}/3` : 'Beat the Rime-Captain in the caves.'; }, 2: 'Open the Barrow.', 3: 'The Barrow Key is yours. Stonehollow will not forget.' } },
});
// Solvi's Stonefrost school (story 4.2): tier I lessons are real casts built on the existing spell kinds (a thrown boulder = a projectile with the earth burst, a frost rune = a trap).
// Tiers II / III (Stone Skin, Cold Fire, Stone Golem) are recorded as unlocks and learned from her later; their casts arrive with the spell atlas additions.
SPELLS.boulder_toss = { name: 'Boulder Toss', cd: 2.2, dmg: 26, radius: 1.6, kind: 'projectile', fx: 'seed_bomb', burst: 'earth_burst' };
SPELLS.frost_rune = { name: 'Frost Rune', cd: 3.2, dmg: 24, radius: 1.8, kind: 'trap', arm: 0.5, life: 6 };
Object.assign(SPELL_NAMES, { boulder_toss: 'Boulder Toss', frost_rune: 'Frost Rune' });
// ---- the Rimebreaker (story 3.8 / 9.1): a legendary weapon from Solvi after three heart-ice. Every 3rd melee hit with it freezes the foe for 1.5 s and rings a small ice wave.
// Deviation: the engine has no charged attack yet, so the "charged hit throws an ice wave" half rides on the 3rd hit instead.
export function RIMEBREAKER(S) {
  const it = makeItem(Math.max(10, S.lv || 1), 4, 'weapon'), k = RARITY[4].mul * (1 + (it.lv - 1) * 0.06);
  it.name = 'The Rimebreaker'; it.fixed = true; it.unique = 'rimebreaker'; it.crafted = true;
  it.mods = { meleeMul: +(0.07 * k).toFixed(3), spellMul: +(0.03 * k).toFixed(3), crit: +(0.006 * k).toFixed(3) };
  it.gems = [null, null];
  it.about = 'A giant frost axe, cut down to your size by Solvi\'s runes. Cold blue fire runs along the edge. Every third hit freezes what it bites.';
  return it;
}
export const HI = [['hi_1', 'barrow', [7.2, -22.0]], ['hi_2', 'barrow2', [6.0, -14.8]], ['hi_3', 'barrow2', [-9.2, -40.2]]];
// ---- Jotunheim weather (story 2.6): Stonehollow's day is 70% snow / 15% blizzard / 15% clear per 6-hour block; clear nights show the aurora. Interiors stay clear.
// Blizzard: frost slow of -1% speed per 5 s outdoors (max -30%); standing by cold fire thaws it quickly. (Flurry / Moonpetal tea thaw it too once those exist.)
WX_KINDS.blizzard = [{ preset: 'snowfall', rate: 2.4 }, { preset: 'mist', rate: 0.9 }];
WX_KINDS.aurora = [];
const wxHash = (n) => { let x = (n | 0) * 374761393 + 668265263; x = (x ^ (x >>> 13)) * 1274126177; return ((x ^ (x >>> 16)) >>> 0) / 4294967296; };
WX_HOOK.jotunheim = (day, t) => { const r = wxHash(day * 4 + Math.floor(t * 4) + 4242), night = t > 0.8 || t < 0.25; return r < 0.7 ? 'snow' : r < 0.85 ? 'blizzard' : night ? 'aurora' : 'clear'; };
const BASE_SPEED = 2.6, FROST_MAX = 0.3;
const need = (S) => (S.hero === 'runeguard' ? 2 : 3);

// ------------------------------------------------------------------ shared quest steps (module level so TALK can use them)
export const cellarOK = (S) => !!((F(S).alliance || {}).jotunheim || F(S).jt_contract || (typeof location !== 'undefined' && new URLSearchParams(location.search).has('jtq')));
const clueN = (S) => ['jh_heart', 'jh_rime', 'jh_trail'].filter((k) => F(S)[k]).length;
function finishWelcome(G) {
  const f = flags(G.S); G.setQuest('jt_welcome', 3); f.jt_trusted = 1; G.factions.add('embassy', MERIT.jt_welcome, 'jt_welcome'); gold(G, 20);
  f.realm_mood = { ...(f.realm_mood || {}), jotunheim: Math.max(3, (f.realm_mood || {}).jotunheim || 0) }; G.refreshMarkers && G.refreshMarkers();
}
function closeHeart(G) {   // The Hollow Heart done (story 3.3 / 4.3): the Heart is a fake, the war band turns back
  const S = G.S, f = flags(S), mood = moodJot(S);
  G.setQuest('jt_heart', 3); G.factions.add('embassy', MERIT.jt_heart + (mood ? MERIT.jt_rival : 0), 'jt_heart'); gold(G, 40);
  f.jt_cleared = 1; f.jt_peace = 1; S.evidence = { ...(S.evidence || {}), jotunheim: 'false_heart' }; G.refreshMarkers && G.refreshMarkers();
}

// ------------------------------------------------------------------ talk (TALK is keyed by the actor id in the area spec)
const moodJot = (S) => ((F(S).realm_mood || {}).jotunheim || 0) >= 1;
Object.assign(TALK, {
  jt_trader(S) {
    const first = !(S.met || {}).jt_trader;
    return { pages: [first ? 'Grimsa. Stall. Cloaks for small ones, tea for cold ones. Everything here is cut to your size, which is, hm, more work than you know.'
                           : 'Cloak, tea or lamp? The lamp burns blue. It will not burn you. We tested on a goat.'],
             then: (G) => { met('jt_trader')(G); G.shopUI.show('jt_trader'); } };
  },
  goatherd(S) {
    const f = F(S);
    if (f.jt_contract && f.jw_terms && !f.jw_skuli) return { pages: ['The Guild man! Skuli. I know a goat-path. Goats know everything. I will take you to the Barrow when it is time.', '(He whispers.) The Heart in the cellar rings hollow, you know. Look, if you like. Not my business.'], then: (G) => { flags(G.S).jw_skuli = 1; G.setQuest('jt_hire', 2); G.refreshMarkers && G.refreshMarkers(); } };
    if (f.jt_contract && !f.jw_terms) return { pages: ['The Jarl wants to hear your terms first. She is in the Hall. Goats wait. Goats are good at it.'] };
    return { pages: [f.jt_peace ? 'The war band turned back? Goats knew. Goats know everything.' : 'I know a goat-path. Goats know everything. Ask me when you have a reason to go sneaking.'] };
  },
  goatwife(S) {
    const f = F(S), st = q(S, 'jt_goat'), al = (f.alliance || {}).jotunheim, day = S.day || 0, cakes = f.gt_cakes || 0, has = ((S.inv || {}).oat_cake || 0) > 0;
    if (!st && al === 'befriend' && q(S, 'jt_welcome') >= 3)
      return { pages: ['You are the small one the stones liked. Good. I have a young goat, Clatter, who likes nobody. She will like you or she will not, and I will not lie about which.', 'An oat-cake a day, from the same hand, three days running. Not two in one day: she is a goat, not a fool. Come back tomorrow for the next.'],
               then: (G) => { G.setQuest('jt_goat', 1); G.toast('The Goat Who Chose You: an oat-cake a day, three days.', 3); G.give('oat_cake', 1); f.gt_given = day; } };
    if (st === 1) {
      if (has) return { pages: ['You have the cake. She is at the fence, the brown one with the bell. Hold it flat. Flat! She is not a cow.'] };
      if ((f.gt_given ?? -1) < day && (f.gt_lastDay ?? -1) < day && cakes < 3) return { pages: ['Another day, another oat-cake. Hold it flat.'], then: (G) => { G.give('oat_cake', 1); flags(G.S).gt_given = day; } };
      return { pages: [cakes < 3 ? 'One a day. She would get fat and then she would get opinions. Come back tomorrow.' : 'She is yours, near enough.'] };
    }
    if (st === 2) return { pages: ['She follows you around the pen like a cat with horns. When the saddle is stitched you can ride one lap of the lake. Goats are patient. I am less so.'] };
    return { pages: [q(S, 'jt_welcome') >= 3 ? 'She bit you? Good. That means she likes you.' : 'Mind the horns. Mind the whole goat, really. She has opinions.'] };
  },
  ulfar(S) {
    const f = F(S), first = !(S.met || {}).ulfar, st = q(S, 'jt_ulfar'), n = ['uw_goat', 'uw_song', 'uw_mitten'].filter((k) => (S.found || {})[k]).length;
    if (!st && (f.alliance || {}).jotunheim === 'befriend' && q(S, 'jt_welcome') >= 3)
      return { pages: ['Small one. You lifted our stones. Will you spend a day with me? It is a long day. I have three small things to do and I am bad at remembering.', '(He holds up three huge fingers.) My goat Turnip is on the lake ice. I want to finish my song. I lost my mitten. That is all.'],
               then: (G) => { met('ulfar')(G); G.setQuest('jt_ulfar', 1); G.toast("Ulfar's Walk: Turnip, the song, the mitten.", 3); } };
    if (st === 1 && n < 3) return { pages: [`Turnip, the song, the mitten. ${n} of three. I counted on my fingers. Then I ran out of fingers.`] };
    if (st === 1) return { pages: ['All three! The goat is back and the song has a next line. And my mitten is a bed for a small hare. It is a better mitten now.', 'Walk with me to the Barrow door. I want to see the big door. Then I will come with you. I am the big one. I go first.'],
                           then: (G) => { G.setQuest('jt_ulfar', 2); flags(G.S).uw_walk = 1; G.jot.afterWalk(); } };
    return { pages: [first ? 'Oh. Hello. You are very small. I am Ulfar. I look at the lake. It does not look back.'
                            : 'Snow tastes like nothing. I eat it anyway.', 'Kolbrun says stay off the lake. Unless you are a goat.'], then: met('ulfar') };
  },
  jt_a(S) { return { pages: ['Mind the stools. They are for sitting, not climbing.'] }; },
  jt_b(S) { return { pages: [['The aurora sings if you are quiet.', 'Dwarves think we steal. We cannot even fit in their doors.'][(S.day || 0) % 2]] }; },
  // the Jarl (story 5.2, 3.2 stage 2, 3.3, 3.6, 4.3): the choice, the fire, the Hollow Heart, the contract terms
  jarl(S) {
    const f = F(S), mood = moodJot(S), locked = (f.rivals || {}).jotunheim === 'locked', al = (f.alliance || {}).jotunheim;
    if (q(S, 'barrow') === 2 && (S.found || {}).tb_slept && (al === 'befriend' || f.jt_contract)) return { pages: ['You went down, and the king sleeps. I felt the stones settle from here.', '"Tell Thyra... the stones still stand." (You say it as he did.) Her eyes are wet, and she looks very hard at the fire.', f.jt_contract ? 'Paid in full. The Guild gets its word, and you get your coin.' : 'Stonehollow owes you more than I can say. Take this, and a seat at my fire.'],
      then: (G) => { G.setQuest('barrow', 3); G.factions.add(f.jt_contract ? 'gate' : 'embassy', MERIT.barrow, 'barrow'); gold(G, 150); if (f.jt_contract) { G.setQuest('jt_hire', 3); f.jt_resolved = 1; } else f.jt_resolved = 1; G.refreshMarkers && G.refreshMarkers(); G.save && G.save(); } };
    if (f.jt_contract && !f.jw_terms) return { pages: ['An offer from the Guild? Hm. Terms, then: the Titan sleeps in the Barrow and his sleep is thinning.', 'Lay him back down, and the Guild may have its coin. Skuli at the goat pens will guide you. He is young. He is also right, mostly.'], then: (G) => { flags(G.S).jw_terms = 1; G.setQuest('jt_hire', 1); } };
    if (al === 'befriend') {
      if (q(S, 'jt_welcome') === 2) return { pages: ["(You sit at the Jarl's fire. The hall hums. Someone passes you a bone, politely.)", 'Arms that work, and a fire shared. Welcome, small one.', 'One more thing. The dwarves say we stole their Heart. There is a Heart in my cellar, and I am not proud of it. Go and look at it. Tell me what you see.'],
        then: (G) => { finishWelcome(G); G.setQuest('jt_heart', 1); } };
      if (q(S, 'jt_heart') === 1 && f.sv_decoy) return { pages: ['You carry a boot mould from Anvildeep? Show me.', '(The mould fits the frost-iron prints in the cellar, small straps and all.)', 'The dwarves sent a friend? Then the world is not all spears.', 'I will send a horn-message to their Thane. The war band turns back.'], then: (G) => closeHeart(G) };
      if (q(S, 'jt_heart') === 2) return { pages: ['A shell. Blue-black rime, and big boots that went in and never came out. Someone small and cruel wanted two realms at each other\'s throats.', 'You have done Stonehollow a great kindness. I will send a horn-message to Anvildeep: the war band turns back.'], then: (G) => closeHeart(G) };
      if (q(S, 'jt_heart') === 1) { const n = ['jh_heart', 'jh_rime', 'jh_trail'].filter((k) => f[k]).length; return { pages: [`The cellar trapdoor is by the north-east table. Tap the Heart, look at the rime, follow the prints. ${n}/3.`] }; }
      if (q(S, 'jt_welcome') === 3 && !q(S, 'jt_heart')) return { pages: ['The town trusts you. So I will ask the hard thing: look at the Heart in my cellar.'], then: (G) => G.setQuest('jt_heart', 1) };
      if (q(S, 'jt_welcome') === 1) return { pages: ['Then lift our stones. We trust arms that work.'] };
      return { pages: ['The fire is for everyone. Sit.'] };
    }
    if (al === 'conquer') return { pages: ['So. Midgard is a thief too. Take it, and go.'] };
    const opts = [];
    if (!locked) opts.push({ label: 'A friend. Let me prove you innocent.', pick: () => ({ pages: ['Then lift our stones. We trust arms that work.'],
      then: (G) => { ally(G.S).jotunheim = 'befriend'; lockRival(G.S, 'asgard'); moodUp(G.S, 'vanaheim'); G.setQuest(mood ? 'jt_heart' : 'jt_welcome', 1); G.toast('Jotunheim: befriended', 2.2); G.refreshMarkers && G.refreshMarkers(); } }) });
    opts.push({ label: "Midgard's. Hand over the Barrow Key.", pick: () => ({ pages: ['So. Midgard is a thief too. Take it, and go.'],
      then: (G) => { ally(G.S).jotunheim = 'conquer'; moodUp(G.S, 'asgard'); G.setQuest('jt_take', 1); G.toast('Jotunheim: conquered', 2.2); } }) });
    if (locked) opts.push({ label: 'The Guild sent me with an offer.', pick: () => ({ pages: ['An offer. Hm. Hear my terms.'], then: (G) => { flags(G.S).jt_contract = 1; G.setQuest('jt_hire', 1); } }) });
    return { pages: [mood ? 'You humbled the thunder-folk? Sit by the fire, small one.' : locked ? "Asgard's friend, in my hall. Say it quick."
                           : 'Midgard comes to Stonehollow. Dwarves call us thieves. Asgard calls us raiders. What are you?'], choice: { id: 'jt_jarl', options: opts } };
  },
  envoy_jt(S) {
    const al = (F(S).alliance || {}).jotunheim;
    return { pages: [al === 'conquer' ? 'So you took the Barrow Key by asking. Or by not asking. I keep the ledger either way.' : al === 'befriend' ? 'Stay off the lake. Unless you are a goat. The Jarl likes you; do not make her regret it.' : 'Stay off the lake. Unless you are a goat.'] };
  },
  rimewife(S) {
    const f = F(S), al = (f.alliance || {}).jotunheim;
    if (al === 'conquer') return { pages: ["You know it's hollow. Everyone can hear it.", 'Cold fire is a gift. It lights. It never burns. Someone made it burn in a tomb.'] };
    if (al === 'befriend' && q(S, 'jt_axe') === 2) return { pages: ['Three heart-ice. Good. They are the Titan\'s own cold, and the cold remembers what it was for.', '(Solvi sets the shards in an axe-head of black rune-iron. Ulfar hums a long low note. Blue fire runs along the edge.)', 'The Rimebreaker. It was a giant\'s axe once. It will fit your hand now.'],
      then: (G) => { const i = G.S.inv; i.heart_ice = Math.max(0, (i.heart_ice || 0) - 3); (G.S.bag = G.S.bag || []).push(RIMEBREAKER(G.S)); G.setQuest('jt_axe', 3); G.toast('You are given The Rimebreaker (check your bag)', 3.0); G.refreshMarkers && G.refreshMarkers(); G.save && G.save(); } };
    if (al === 'befriend' && q(S, 'jt_axe') === 1) return { pages: [`Heart-ice, small one: ${['hi_1', 'hi_2', 'hi_3'].filter((k) => (S.found || {})[k]).length} of 3. One in the Glow Pools, one behind the Berserker chief's seat, one in the crypt crystals.`] };
    if (al === 'befriend' && f.sf_i && q(S, 'barrow') === 3 && !q(S, 'jt_axe')) return { pages: ['There is an axe I have wanted to wake for a hundred winters. It needs three shards of heart-ice from the Barrow.', 'Bring them, and I will cut it down to your size.'], then: (G) => { G.setQuest('jt_axe', 1); G.refreshMarkers && G.refreshMarkers(); } };
    if (al === 'befriend' && q(S, 'barrow') === 3 && !f.sf_i) return { pages: ['You laid the king down. Sit by my hearth, small one, and I will teach you what the stone teaches.', '(Solvi draws a rune in the soot. The stone in the hearth hums back.)', 'Stonefrost. Throw the boulder, then ask it to stay: two lessons for the first circle. Come back when you are older for the rest.'],
      then: (G) => { flags(G.S).sf_i = 1; G.S.unlocks = { ...(G.S.unlocks || {}), stonefrost: 1 }; G.learn('boulder_toss'); G.learn('frost_rune'); G.toast('Stonefrost school: first circle', 2.6); G.refreshMarkers && G.refreshMarkers(); } };
    if (al === 'befriend' && f.sf_i) return { pages: ['The first circle is yours: Boulder Toss, Frost Rune. Stone Skin, Cold Fire and the Stone Golem come later. The stone is patient, and so am I.'] };
    if (al === 'befriend' && q(S, 'jt_heart') === 1 && !f.jh_solvi) return { pages: ['The cellar Heart? Rime tells the truth if you give it good light. Take my rune-light.', '(Solvi lends you her rune-light. It hums, and shows rime for what it is.)'], then: (G) => { flags(G.S).jh_solvi = 1; } };
    return { pages: ['Cold fire is a gift. It lights. It never burns. Someone made it burn in a tomb.'] };
  },
  solvi(S) {   // the rune-keeper in her own hall (story 5.3); the Stonefrost school comes after the Barrow (barrow = 3)
    const f = F(S), al = (f.alliance || {}).jotunheim;
    if (al === 'conquer') return { pages: ["You know it's hollow. Everyone can hear it.", 'The Barrow Key? It opens the door. It does not make the dead agree.'] };
    if (al === 'befriend' && q(S, 'barrow') === 3) return { pages: ['The king sleeps. Good. I teach in the Hall, at my hearth; the caves are for listening.'] };
    if (al === 'befriend') return { pages: ['Cold fire is a gift. It lights. It never burns. Someone made it burn in a tomb.', 'The Barrow door has three rune locks. I can open them when the Jarl trusts you with the Titan. Soon.'] };
    return { pages: ['Cold fire is a gift. It lights. It never burns. Someone made it burn in a tomb.'] };
  },
  rc_skuli(S) { return { pages: [F(S).jt_contract ? 'The goat-path goes round the side of the door. Goats do not need rune locks.' : 'Goats know the way round the side.'] }; },
  jt_guard1(S) { return { pages: [cellarOK(S) ? 'The Jarl says you may go down. Mind the plinth.' : "The cellar is the Jarl's."] }; },
  jt_guard2(S) { return { pages: [cellarOK(S) ? 'Down the trapdoor. Do not lick the Heart.' : 'Nobody goes down without the Jarl\'s word.'] }; },
  jt_diner1(S) { return { pages: ['The aurora sings if you are quiet.'] }; },
  jt_diner2(S) { return { pages: ['Mind the stools. They are for sitting, not climbing.'] }; },
});

MARKER_HOOKS.push((id, S) => {
  const f = F(S), al = f.alliance && f.alliance.jotunheim;
  if (id === 'jarl') {
    if (!al || (al === 'befriend' && (q(S, 'jt_welcome') === 2 || q(S, 'jt_heart') === 2 || (q(S, 'jt_heart') === 1 && f.sv_decoy) || (q(S, 'jt_welcome') === 3 && !q(S, 'jt_heart'))))) return 'quest_mark';
    if (f.jt_contract && !f.jw_terms) return 'quest_mark';
    if (q(S, 'barrow') === 2 && (S.found || {}).tb_slept && (al === 'befriend' || f.jt_contract)) return 'quest_mark';
  }
  if (id === 'goatwife' && al === 'befriend' && ((!q(S, 'jt_goat') && q(S, 'jt_welcome') >= 3) || (q(S, 'jt_goat') === 1 && !((S.inv || {}).oat_cake) && (f.gt_given ?? -1) < (S.day || 0) && (f.gt_cakes || 0) < 3))) return 'quest_mark';
  if (id === 'ulfar' && al === 'befriend' && ((!q(S, 'jt_ulfar') && q(S, 'jt_welcome') >= 3) || (q(S, 'jt_ulfar') === 1 && ['uw_goat', 'uw_song', 'uw_mitten'].every((k) => (S.found || {})[k])))) return 'quest_mark';
  if (id === 'rimewife' && al === 'befriend' && (q(S, 'jt_axe') === 2 || (f.sf_i && q(S, 'barrow') === 3 && !q(S, 'jt_axe')))) return 'quest_mark';
  if (id === 'rimewife' && al === 'befriend' && q(S, 'barrow') === 3 && !f.sf_i) return 'quest_mark';
  if (id === 'rimewife' && al === 'befriend' && q(S, 'jt_heart') === 1 && !f.jh_solvi) return 'quest_mark';
});

// ------------------------------------------------------------------ Dark Stonehollow (story 9.7, flags.jt_dark = 1: you took Hrimgard's crown)
// The cold fires are out, only glow orbs remain; the giants are curt, no song, no Games, and the trader charges +25% (factions.js priceMul).
export const isDark = (S) => !!F(S).jt_dark;
const DARK_TALK = {
  jt_trader: () => ({ pages: ['Prices are up a quarter. Cold fire kept the stall warm. Orbs do not.'], then: (G) => { met('jt_trader')(G); G.shopUI.show('jt_trader'); } }),
  goatherd: () => ({ pages: ['Goats are quiet now. Goats know why.'] }),
  goatwife: () => ({ pages: ['The goats do not like the dark. Neither do I. Move along.'] }),
  ulfar: () => ({ pages: ['(Ulfar looks at the lake. He does not wave.)', 'The fires went out. I am not sure who to be angry at.'] }),
  jt_a: () => ({ pages: ['Quiet. Please.'] }),
  jt_b: () => ({ pages: ['No song tonight. No Games this year either. Nobody has the heart.'] }),
  jarl: () => ({ pages: ['The fires are out. You have the crown. Take what you came for, and go.'] }),
  envoy_jt: () => ({ pages: ['A dark town keeps the ledger too. You are in it.'] }),
};
for (const id of Object.keys(DARK_TALK)) { const base = TALK[id]; TALK[id] = (S) => (isDark(S) && ((F(S).alliance || {}).jotunheim === 'conquer') ? DARK_TALK[id](S) : base(S)); }
// ------------------------------------------------------------------ the area's own look: cold fire on the braziers, rune pulses, the lake, a gloom light
const COLD = ['#7fd4ff', 4.2, 4.2];
const DARK_GLOW = [1.1, 3.4];   // Dark Stonehollow: the glow orbs' point light (intensity, range)   // colour, intensity, range
// Stonehollow's pen goats + Clatter (runtime actors on the jt_goats sheet): north of the fence line (z 3.4) so the fence never hides them, in the far-left column (x -11.2) so they sit outside Brynja's sprite box and the fur stall / trader (they hide anything at x > -8.5)
const GOATS = [['pen_goat1', [-11.2, -1.1], 0.25, 'goat', 'pen goat'], ['clatter', [-11.2, 1.1], 0.25, 'clatter', 'Clatter']];
const JT_FX = {
  jotunheim: [['cold_flame', [-2.4, -5.0], 1.0, 1], ['cold_flame', [2.4, -5.0], 1.0, 1],
              ['rune_pulse', [0, -5.4], 0.8, 1], ['rune_pulse', [-5.4, 0.2], 0.8, 0], ['rune_pulse', [5.2, -0.4], 0.8, 0],
              ['rune_pulse', [10.6, -1.4], 0.8, 1], ['ice_sparkles', [8.0, -3.2], 0.5, 0]],
};
JT_FX.jt_hall = [['cold_flame', [-1.5, -2.0], 1.0, 1], ['cold_flame', [1.5, -2.0], 1.0, 1], ['cold_flame', [0, -3.6], 1.0, 1], ['cold_flame', [0, -0.4], 1.0, 1],
  ['rune_pulse', [-7.0, -10.4], 0.8, 1], ['rune_pulse', [7.0, -10.4], 0.8, 1], ['cold_flame', [12.4, -3.0], 1.0, 1], ['cold_flame', [16.0, -3.0], 1.0, 1], ['ice_sparkles', [14.2, -5.4], 0.5, 0]];
JT_FX.rimecaves = [['cold_flame', [-3.6, -8.4], 1.0, 1], ['cold_flame', [3.6, -8.4], 1.0, 1], ['pool_teal', [-6.0, 5.2], 0, 0], ['pool_aurora', [6.0, 5.2], 0, 0],
  ['pool_teal', [-7.4, -0.4], 0, 0], ['ice_sparkles', [0, 0.2], 0.5, 0], ['rune_pulse', [-9.8, -7.0], 0.8, 0]];
JT_FX.barrow = [['cold_flame', [-3.6, 7.0], 1.0, 1], ['cold_flame', [3.6, 7.0], 1.0, 1], ['cold_flame', [0, -8.6], 1.0, 1], ['cold_flame', [0, -29.0], 1.0, 1],
  ['pool_teal', [-5.0, -17.0], 0, 0], ['pool_aurora', [5.0, -17.0], 0, 0], ['pool_teal', [0, -19.4], 0, 0], ['ice_sparkles', [0, -16.0], 0.5, 0]];
JT_FX.barrow2 = [['cold_flame', [-3.6, 7.0], 1.0, 1], ['cold_flame', [3.6, 7.0], 1.0, 1], ['cold_flame', [0, -32.0], 1.0, 1], ['pool_teal', [-6.4, -21.0], 0, 0], ['pool_aurora', [6.4, -21.0], 0, 0],
  ['cold_flame', [-6.0, -47.0], 1.0, 1], ['cold_flame', [6.0, -47.0], 1.0, 1], ['cold_flame', [0, -52.4], 1.0, 1], ['ice_sparkles', [0, -2.0], 0.5, 0], ['rune_pulse', [0, -30.8], 0.8, 0]];
// ---- B3 The Glow Pools slide puzzle (story 7): the pool floor is ice. You slide in one direction until a frost-rune pillar or the wall stops you;
// the far door is the stair at the north end of column 3. Stateless (so it cannot soft-lock: the layout is checked by BFS in the smoke: every stop cell
// reaches both the door and the bank), the bank is the way back, the ice runes under your feet slide you back to the bank on E / A, and once solved the
// pools are ordinary (walkable) floor for good (found.tb_slide).
export const PZ = { cols: 7, rows: 4, cell: 2.4, x0: -7.2, z0: -13.4, door: 3, zS: -12.2, zN: -22.9, speed: 7.0, pillars: [[1, 1], [2, 3], [3, 1], [4, 0], [5, 0], [5, 3], [6, 0]] };
export const pzXZ = (c, r) => [PZ.x0 + c * PZ.cell, PZ.z0 - r * PZ.cell];
// where a slide from cell (c, r) in direction d ends: [c, r] (a cell; r = -1 is the bank), 'goal' (up the far door's stair) or null (blocked)
export function pzSlide(c, r, d) {
  const [dx, dr] = { N: [0, 1], S: [0, -1], E: [1, 0], W: [-1, 0] }[d];
  const P = (cc, rr) => PZ.pillars.some(([a, b]) => a === cc && b === rr);
  let k = 0;
  for (;;) {
    const nc = c + dx, nr = r + dr;
    if (nr >= PZ.rows) return c === PZ.door ? 'goal' : (k ? [c, r] : null);
    if (nr < 0) return r === -1 ? null : [c, -1];
    if (nc < 0 || nc >= PZ.cols || P(nc, nr)) return k ? [c, r] : null;
    c = nc; r = nr; k++;
  }
}
const CAIRNS = [[-10.2, 6.4], [10.2, 6.4], [3.0, -1.6]];   // the Toll of Stones cairns (invisible spots; the ambush spawns at runtime)
// the Rune Bridge (story 7, B7): step on lit frost runes only; unlit tiles crack and drop you back at the bridge head. 3 columns x 6 rows; LIT[row] = lit columns.
// The lit tiles form one orthogonally connected path from the head to the far end (the smoke checks that); a fall costs a little health, never position.
const BRIDGE = { x0: -2.6, w: 5.2 / 3, z0: -17.2, h: 2.2, rows: 6, endZ: -30.4, head: [0, -16.8], LIT: [[1], [1, 2], [2], [2, 1], [1, 0], [0, 1]] };
const bridgeTile = (x, z) => { const r = Math.floor((BRIDGE.z0 - z) / BRIDGE.h), c = Math.min(2, Math.max(0, Math.floor((x - BRIDGE.x0) / BRIDGE.w))); return r < 0 || r >= BRIDGE.rows ? null : [c, r]; };
const bridgeCentre = (c, r) => [BRIDGE.x0 + BRIDGE.w * (c + 0.5), BRIDGE.z0 - BRIDGE.h * (r + 0.5)];
const THRONE_BRAZ = [[-6.0, -47.0], [6.0, -47.0], [0.0, -52.4]];   // Hrimgard's three braziers: they relight in phase 3
const SPOTS = {   // look-spots / interactables (Svartalfheim pattern): hall door, cave path, frost prints, Welcome Ring stones
  lifts: [[-1.4, 2.6], [0.0, 3.3], [1.4, 2.6]],
  hall: [0, -9.4], caves: [10.0, -0.2], prints: [-3.4, -1.6],
};

export class Jotunheim {
  constructor(G) { this.G = G; this.ctx = null; this.area = null; this.planned = JOT_PLANNED; this.fx = []; this.lights = []; this.spots = []; this.qaDone = null; this.gate = new JtGate(this); this.ring = null; this.lastLift = null; this.wrap(); }
  qs() { return this.G.qs || new URLSearchParams(location.search); }
  wrap() {   // E / A and tap try the realm's interactables first (same chained hook as Alfheim's / Svartalfheim's)
    const G = this.G, me = this; if (!G.harbor) return;
    const p0 = G.harbor.prompt.bind(G.harbor), i0 = G.harbor.interact.bind(G.harbor), t0 = G.harbor.onTap.bind(G.harbor);
    G.harbor.prompt = (...a) => me.prompt() || p0(...a);
    G.harbor.interact = (...a) => me.interact() || i0(...a);
    G.harbor.onTap = (hit, ...a) => me.onTap(hit) || t0(hit, ...a);
    if (G.combat && !G.combat.__rime) {   // the Rimebreaker: every 3rd melee hit freezes the foe 1.5 s and rings a small ice wave
      G.combat.__rime = 1; const d0 = G.combat.damageEnemy.bind(G.combat);
      G.combat.damageEnemy = (e, dmg, src, push, color) => {
        const r = d0(e, dmg, src, push, color), C = G.combat, wp = ((G.S.gear || {}).weapon) || {};
        if (r && push === 0.45 && wp.unique === 'rimebreaker' && C.ctx && src === C.ctx.player) {
          C.rimeN = (C.rimeN || 0) + 1;
          if (C.rimeN % 3 === 0) me.rimeFreeze(e);
        }
        return r;
      };
    }
    if (G.hollows) { const c0 = G.hollows.onCast.bind(G.hollows); G.hollows.onCast = (...a) => { const r = c0(...a); me.onCast(); return r; }; }
  }
  // ---- the goat pens (story 2.3, 3.9): a pen goat and Clatter inside the fence line at z 3.4 (Brynja stands north of the goats, the goats' stand-in sheet is jt_goats). The mount stays deferred.
  penGoats(ctx) {
    const G = this.G, S = G.S, roles = ctx.actors.meta.roles;
    for (const [id, pos, radius, role, name] of GOATS) {
      if (!roles[role]) continue;
      const a = ctx.actors.add({ role, id, name, pos: pos.slice(), behavior: 'wander', radius, talkable: false, turn: false }); a.home = pos.slice();
    }
    this.spot({ id: 'clatter', pos: [-10.8, 1.2], r: 1.8, label: () => (q(S, 'jt_goat') ? 'Clatter, the young brown goat (E / A)' : 'a young brown goat with a bell (E / A)'), act: () => this.clatter() });
  }
  clatter() {
    const G = this.G, S = G.S, f = flags(S), st = q(S, 'jt_goat'), day = S.day || 0, i = S.inv || {};
    const say = (pages, then) => this.look('clatter', 'Clatter', pages, then);
    if (!st) return say(['A young brown goat with a gold bell. She looks at you like a creditor, and the bell goes clatter.']);
    if (st >= 2) return say(['Clatter leans her whole weight on your knee. The bell goes clatter. The saddle is still Brynja\'s problem for later.']);
    if ((f.gt_lastDay ?? -1) >= day) return say(['She has had her cake today. She looks at the empty hand with a very particular disappointment. Tomorrow.']);
    if (!(i.oat_cake > 0)) return say(['She sniffs your pockets and finds nothing. Brynja keeps the oat-cakes.']);
    return say(['(You hold the oat-cake flat. Clatter takes it with great dignity and no thanks.)'], () => {
      i.oat_cake -= 1; f.gt_cakes = (f.gt_cakes || 0) + 1; f.gt_lastDay = day;
      if (f.gt_cakes >= 3) { G.setQuest('jt_goat', 2); G.toast('Clatter trusts you. Ride one lap of the lake: once the saddle is stitched.', 3.6); }
      else G.toast(`Clatter ate the oat-cake. ${f.gt_cakes}/3`, 2.4);
      G.refreshMarkers && G.refreshMarkers(); G.save && G.save();
    });
  }
  // ---- Ulfar's Walk (story 3.4): Turnip on the lake ice, the song at the cold fire, the mitten that is a hare's bed; then the Barrow door, and he joins
  ulfarWalk(ctx) {
    const G = this.G, S = G.S, mine = () => q(S, 'jt_ulfar') === 1, got = (k) => !!(S.found || {})[k];
    const find = (k) => { S.found = { ...(S.found || {}), [k]: 1 }; G.save && G.save(); };
    this.spot({ id: 'uw_goat', pos: [8.8, 3.6], r: 1.7, label: 'Turnip, stuck on the lake ice (E / A)', show: () => mine() && !got('uw_goat'), act: () =>
      this.look('uw_goat', 'Turnip', ['A small goat stands very still in the middle of the thin ice, offended by the ice.', '(You coax Turnip back with a pinch of snow-moss. He leaves a hoofprint on your boot as a thank-you.)'], () => { find('uw_goat'); G.toast("Turnip is off the ice. Ulfar's Walk 1/3", 2.4); }) });
    this.spot({ id: 'uw_song', pos: [2.4, -3.8], r: 1.7, label: "the cold fire: Ulfar's song (E / A)", show: () => mine() && !got('uw_song'), act: () =>
      G.openDialogue({ id: 'uw_song', name: "Ulfar's song" }, { pages: ['(Ulfar hums by the cold fire. He is stuck on the next line.) "The snow came down on the goat, and the goat..."'], choice: { id: 'uw_song', options: [
        { label: '"...said hello."', pick: (G2) => { find('uw_song'); flags(G2.S).uw_tune = 'hello'; return { pages: ['He sings it twice. It is a slow, kind song now.'] }; } },
        { label: '"...ate the snow."', pick: (G2) => { find('uw_song'); flags(G2.S).uw_tune = 'snow'; return { pages: ['He laughs so hard the cold fire flickers. The song is faster now.'] }; } },
        { label: '"...climbed the giant."', pick: (G2) => { find('uw_song'); flags(G2.S).uw_tune = 'giant'; return { pages: ['"Ha! The goat is the hero now." The song is a march.'] }; } },
      ] } }) });
    this.spot({ id: 'uw_mitten', pos: [-8.6, 5.0], r: 1.7, label: 'a huge mitten in the snow (E / A)', show: () => mine() && !got('uw_mitten'), act: () =>
      this.look('uw_mitten', 'The mitten', ['A mitten the size of a sleeping bag. Something small and white is asleep in the thumb. It opens one pink eye, sneezes, and goes back to sleep.', '(A snow hare. Flurry, you will call her. She does not mind.)'], () => { find('uw_mitten'); G.toast("The mitten is a bed now. Ulfar's Walk 2/3", 2.4); }) });
    this.hideUlfar();
  }
  hideUlfar() {   // while Ulfar walks with you (or is your companion) the town's Ulfar is not standing at the lake
    const c = this.ctx, S = this.G.S; if (!c || !c.actors || this.area !== 'jotunheim') return;
    if (!((F(S).uw_walk) || compActive(S) === 'ulfar')) return;
    const a = c.actors.list.find((x) => x.id === 'ulfar'); if (a) c.actors.remove(a);
  }
  afterWalk() {   // Ulfar steps in beside you: the follower sprite appears (svartalfheim_follow.js reads flags.uw_walk)
    this.hideUlfar();
    const F2 = this.G.svart && this.G.svart.follow; if (F2 && F2.ctx) { try { F2.attach(F2.ctx, F2.area); } catch (e) { /* body only */ } }
  }
  ulfarFinish() {   // at the Barrow door: Ulfar joins for good (companions.ulfar), Flurry's mitten bed, the Frostbrute unlock
    const G = this.G, S = G.S, f = flags(S);
    this.look('uw_door', 'The Barrow door', ['A stone door six metres tall, sunk in the cliff. Ulfar puts one huge hand flat on it, the way you pat a horse.', '"Big door." He nods slowly. "Good door. I will come with you now. I go first. I am the big one."'], () => {
      G.setQuest('jt_ulfar', 3); f.uw_walk = 0; G.factions.add('embassy', MERIT.jt_ulfar, 'jt_ulfar');
      compUnlock(G, 'ulfar'); compSwap(G, 'ulfar');
      S.pets = S.pets || {}; S.pets.flurry = S.pets.flurry || { name: 'Flurry', bond: 1, fed: 0, lastFed: null };
      S.unlocks = { ...(S.unlocks || {}), frostbrute: 1 };
      G.refreshMarkers && G.refreshMarkers(); G.save && G.save();
    });
  }
  // ---- weather: frost slow in a blizzard, the aurora on a clear night
  weatherTick(dt) {
    const c = this.ctx, G = this.G, p = c.player, kind = G.weather ? G.weather.kind : 'clear', out = this.area === 'jotunheim';
    if (out && kind === 'aurora') this.auroraOn(); else if (this.aurora) this.dropAurora();
    if (this.aurora && this.aurora.tex) this.aurora.tex.offset.x = (this.aurora.tex.offset.x + dt / 40) % 1;   // a 40 s loop
    let t = this.frostT || 0;
    if (out && kind === 'blizzard') {
      t += dt;
      const warm = JT_FX.jotunheim.some(([n, [x, z]]) => n === 'cold_flame' && Math.hypot(p.x - x, p.z - z) < 3.2);
      if (warm) t = Math.max(0, t - dt * 12);
    } else t = Math.max(0, t - dt * 2);
    this.frostT = t;
    const slow = Math.min(FROST_MAX, t / 5 * 0.01) * (compActive(this.G.S) === 'ulfar' ? 0.5 : 1);   // Ulfar's aura: frostResist 0.5
    if (slow >= 0.01 && !this.frostSaid) { this.frostSaid = true; G.toast('The blizzard bites. Cold fire thaws you.', 2.4); }
    if (slow !== this.frostSlow) { this.frostSlow = slow; p.speed = BASE_SPEED * (1 - slow); }
  }
  auroraOn() {
    const ctx = this.ctx, sharp = ctx && ctx.effects && ctx.effects.sharp; if (!sharp || this.aurora) return;
    this.aurora = { pending: true };
    import('three').then((THREE) => {
      if (this.ctx !== ctx || !this.aurora || !this.aurora.pending) return;
      const cv = document.createElement('canvas'); cv.width = 96; cv.height = 24; const g = cv.getContext('2d'), cols = ['#3fe0a0', '#5ac8ff', '#a45cf0', '#d4a8ff'];
      for (let x = 0; x < 96; x++) {
        const h = 6 + Math.round(6 * Math.sin(x * 0.21) + 4 * Math.sin(x * 0.07 + 1.3)), top = 4 + Math.round(3 * Math.sin(x * 0.13));
        for (let y = top; y < top + h; y++) { if ((x + y) % 2 && y > top + 1) continue; g.fillStyle = cols[(Math.floor(x / 9) + (y > top + h / 2 ? 1 : 0)) % cols.length]; g.fillRect(x, y, 1, 1); }
      }
      const tex = new THREE.CanvasTexture(cv); tex.magFilter = THREE.NearestFilter; tex.minFilter = THREE.NearestFilter; tex.wrapS = THREE.RepeatWrapping;
      const m = new THREE.Mesh(new THREE.PlaneGeometry(64, 16), new THREE.MeshBasicMaterial({ map: tex, transparent: true, alphaTest: 0.5, depthWrite: false }));
      const p = ctx.player; m.position.set(p.x, 14, p.z - 22); m.rotation.x = -0.15;
      sharp.add(m); this.aurora = { m, tex };
    });
  }
  dropAurora() {
    const a = this.aurora; this.aurora = null; if (!a) return;
    if (a.m) { if (a.m.parent) a.m.parent.remove(a.m); a.m.geometry.dispose(); a.m.material.dispose(); if (a.tex) a.tex.dispose(); } else a.pending = false;
  }
  rimeFreeze(e) {
    const C = this.G.combat, ctx = C.ctx; if (!ctx) return;
    const freeze = (en) => { if (en.state === 'dead' || en.state === 'gone' || en.rimeT > 0) return; const sp = en.D.speed, D0 = en.D; en.rimeT = 1.5; en.D = { ...en.D, speed: 0 }; en.a.speed = 0; en.cd = Math.max(en.cd || 0, 1.5);
      if (ctx.effects) ctx.effects.spawn('frost_puff', en.a.x, en.a.y + 0.8, en.a.z + 0.05);
      C.later.push({ t: 1.5, fn: () => { en.rimeT = 0; if (en.D !== D0) en.D = { ...en.D, speed: sp }; else en.D = D0; en.D.speed = sp; en.a.speed = sp; } }); };
    freeze(e);
    for (const o of C.alive()) if (o !== e && Math.hypot(o.a.x - e.a.x, o.a.z - e.a.z) < 1.8) { C.damageEnemy(o, Math.round(e.D.hp * 0.02) + 4, null, 0, '#bfe8ff'); freeze(o); }   // the small ice wave
    this.rimes = (this.rimes || 0) + 1;
  }
  spot(o) { this.spots.push({ r: 1.6, show: () => true, ...o }); }
  nearSpot() {
    const c = this.ctx; if (!c || this.G.dlg) return null;
    let best = null, bd = 1e9;
    for (const s of this.spots) { if (!s.show()) continue; const d = Math.hypot(c.player.x - s.pos[0], c.player.z - s.pos[1]); if (d < s.r && d < bd) { bd = d; best = s; } }
    return best;
  }
  prompt() { const s = this.nearSpot(); return s ? s.label : ''; }
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

  // QA preset (smoke / screenshots): ?jtq=open (gate only) | befriend (Jarl's choice made, Welcome quest at 1) | done
  qaPreset() {
    const v = this.qs().get('jtq'), S = this.G.S; if (!v || this.qaDone === v) return;
    this.qaDone = v;
    if (v === 'befriend' || v === 'done') { ally(S).jotunheim = 'befriend'; flags(S).jt_gate_open = 1; if (!q(S, 'jt_welcome')) S.quests.jt_welcome = 1; }
    if (v === 'barrow') { ally(S).jotunheim = 'befriend'; flags(S).jt_gate_open = 1; S.quests.jt_welcome = 3; flags(S).jt_trusted = 1; }
    if (v === 'heart' || v === 'decoy') { ally(S).jotunheim = 'befriend'; flags(S).jt_gate_open = 1; S.quests.jt_welcome = 3; flags(S).jt_trusted = 1; S.quests.jt_heart = 1; }
    if (v === 'decoy') { flags(S).sv_decoy = 1; flags(S).sv_cleared = 1; S.evidence = { ...(S.evidence || {}), svartalfheim: 'boot_mould' }; }
    if (v === 'fire') { ally(S).jotunheim = 'befriend'; flags(S).jt_gate_open = 1; S.quests.jt_welcome = 2; flags(S).jw_lifts = 3; }
    if (v === 'deep') { ally(S).jotunheim = 'befriend'; flags(S).jt_gate_open = 1; S.quests.jt_welcome = 3; flags(S).jt_trusted = 1; S.quests.barrow = 1; S.found = { ...(S.found || {}), tb_b1: 1, tb_b2: 1 }; }
    if (v === 'deepc') { ally(S).jotunheim = 'conquer'; flags(S).jt_gate_open = 1; S.quests.barrow = 1; S.quests.jt_take = 2; flags(S).barrow_key = 1; }
    if (v === 'lessons') { ally(S).jotunheim = 'befriend'; flags(S).jt_gate_open = 1; S.quests.jt_welcome = 3; flags(S).jt_trusted = 1; S.quests.barrow = 3; }
    if (v === 'conquer') { ally(S).jotunheim = 'conquer'; flags(S).jt_gate_open = 1; S.quests.jt_take = 1; }
    if (v === 'dark') { ally(S).jotunheim = 'conquer'; flags(S).jt_gate_open = 1; S.quests.jt_take = 2; S.quests.barrow = 3; flags(S).barrow_key = 1; flags(S).jt_dark = 1; S.found = { ...(S.found || {}), tb_crown: 1 }; }   // Dark Stonehollow (crown taken)
    if (v === 'contract') { flags(S).rivals = { ...(flags(S).rivals || {}), jotunheim: 'locked' }; flags(S).jt_contract = 1; flags(S).jt_gate_open = 1; S.quests.jt_hire = 1; }
    if (v === 'done') { S.quests.jt_welcome = 3; flags(S).jw_lifts = 3; flags(S).jt_trusted = 1; }
  }
  attach(ctx, area) {
    this.detach(); this.ctx = ctx; this.area = area;
    if (area === 'bifrost') { this.qaPreset(); this.gate.atBifrost(ctx); this.bifrost(ctx); return; }
    if (!AREAS_JOT[area]) return;
    this.qaPreset();
    if (area === 'jotunheim') this.stonehollow(ctx);
    if (area === 'jt_hall') this.hall(ctx);
    if (area === 'rimecaves') this.caves(ctx);
    if (area === 'barrow') this.barrowRooms(ctx);
    if (area === 'barrow2') this.deepRooms(ctx);
  }
  detach() {
    for (const f of this.fx) if (f) f.dur = f.t + 0.2;
    for (const l of this.lights) if (l) l.kill = true;
    this.fx = []; this.lights = []; this.spots = []; this.dropAurora(); this.boss = null; this.orm = null; this.frostT = 0; this.frostSlow = 0; this.frostSaid = false; this.relit = null; this.relitFx = []; this.slideV = null; this.falls = 0; this.cb = {}; this.clearRing(); this.ctx = null; this.area = null;
  }
  stonehollow(ctx) {
    const G = this.G, S = G.S, gm = ctx.scene.game || (ctx.scene.game = {}), still = !!G.qaStill;
    this.gate.atHub(ctx);
    const dark = isDark(S);
    if (dark) this.darken(ctx);
    for (const [name0, [x, z], dy, glow0] of JT_FX.jotunheim) {   // gamefx decals / flames + a cold point light where the fx glows
      if (dark && name0 === 'rune_pulse') continue;   // the runes are dead
      const orb = dark && name0 === 'cold_flame', name = orb ? 'glow_orb_blue' : name0, glow = glow0;   // Dark Stonehollow: a pale glow orb where each cold fire was
      const y = ctx.heightAt(x, z);
      if (orb) { if (ctx.gamefx && ctx.gamefx.meta.effects[name]) this.fx.push(ctx.gamefx.spawn(name, x, y + dy, z, { duration: Infinity, fadeIn: still ? 0 : 0.6 })); if (ctx.addGlow) this.lights.push(ctx.addGlow(x, y, z, { color: '#86a4c8', intensity: DARK_GLOW[0], range: DARK_GLOW[1], lift: dy, fadeIn: still ? 0.01 : 0.8 })); continue; }
      if (ctx.gamefx && ctx.gamefx.meta.effects[name]) this.fx.push(ctx.gamefx.spawn(name, x, y + dy, z, { duration: Infinity, fadeIn: still ? 0 : 0.6 }));
      if (glow && ctx.addGlow) this.lights.push(ctx.addGlow(x, y, z, { color: COLD[0], intensity: COLD[1], range: COLD[2], lift: dy, fadeIn: still ? 0.01 : 0.8 }));
    }
    // Welcome Ring: three lift stones (story 3.2). E / A starts the ring, E / A again in the blue band lifts it.
    SPOTS.lifts.forEach((pos, i) => this.spot({ pos, r: 1.3, label: () => this.liftLabel(i), show: () => this.liftLive(i), act: () => this.tryLift(i) }));
    this.spot({ pos: [0, 4.0], r: 0.1, show: () => false, act: () => {}, label: '' });   // the ring's centre (story 2.3), for the QA / markers
    // look-spots (story 2.3 / 4.2): the Hall door, the cave path and the frost prints (entry points for the Giant Footprints clues)
    this.spot({ pos: SPOTS.hall, r: 1.8, label: 'the Hall of Hearthstones (E / A)', show: () => !AREAS_JOT.jt_hall, act: () => this.look('jt_hall_door', 'The Hall door', ["The great doors of the Hall of Hearthstones, barred by a beam as thick as a tree. The Jarl's fire glows under them.", '(The Hall opens in the next chapter of the build.)']) });
    this.spot({ pos: SPOTS.caves, r: 1.8, label: 'the path to the Rime Caves (E / A)', show: () => !AREAS_JOT.rimecaves, act: () => this.look('jt_caves_stair', 'The cave path', ['A stair of piled stone climbs toward a crack in the cliff. Cold blue light breathes out of it.', '(The Rime Caves open in a later chapter of the build.)']) });
    this.penGoats(ctx);
    this.ulfarWalk(ctx);
    this.spot({ pos: SPOTS.prints, r: 1.8, label: 'giant frost prints (E / A)', act: () => this.prints() });
    if (dark && !flags(S).jt_dark_seen && !still) { flags(S).jt_dark_seen = 1; G.toast('The cold fires are out. Only the glow orbs are left. Stonehollow is quiet.', 3.6); }
    if (!dark && !flags(S).jt_arrived && !still) { flags(S).jt_arrived = 1; G.toast('Snow drifts down; the cold fires gutter blue. A giant child stares, then waves.', 3.6); }
  }
  // ---- the Glow Pools slide (see PZ above)
  pzOn() { return this.area === 'barrow' && !((this.G.S.found || {}).tb_slide); }
  pzCell() {   // the free cell nearest the player (r = -1: on the bank)
    const p = this.ctx.player; if (p.z >= PZ.zS) return [Math.max(0, Math.min(PZ.cols - 1, Math.round((p.x - PZ.x0) / PZ.cell))), -1];
    const c0 = Math.max(0, Math.min(PZ.cols - 1, Math.round((p.x - PZ.x0) / PZ.cell))), r0 = Math.max(0, Math.min(PZ.rows - 1, Math.round((PZ.z0 - p.z) / PZ.cell)));
    let best = null, bd = 1e9;
    for (let c = 0; c < PZ.cols; c++) for (let r = 0; r < PZ.rows; r++) {
      if (PZ.pillars.some(([a, b]) => a === c && b === r)) continue;
      const d = Math.hypot(c - c0, r - r0); if (d < bd) { bd = d; best = [c, r]; }
    }
    return best;
  }
  pzStart(d, fromBank) {   // begin a slide from where you stand (fromBank: you just stepped off the bank); false when the way is blocked
    const c = this.ctx, p = c.player, st = this.pz; if (!c || st.st !== 'idle' || !this.pzOn()) return false;
    const [cc, rr] = fromBank ? [Math.max(0, Math.min(PZ.cols - 1, Math.round((p.x - PZ.x0) / PZ.cell))), -1] : this.pzCell(), end = pzSlide(cc, rr, d); if (!end) return false;
    const a = pzXZ(cc, rr), b = end === 'goal' ? [0, -24.4] : pzXZ(end[0], end[1]);
    c.stopWalk && c.stopWalk();
    Object.assign(st, { st: 'slide', d, t: 0, lock: 0.1, from: [p.x, p.z], a, b, end, len: Math.hypot(b[0] - a[0], b[1] - a[1]), cell: [cc, rr] });
    st.moves++; return true;
  }
  pzTick(dt) {
    const c = this.ctx, p = c.player, st = this.pz, G = this.G;
    if (!this.pzOn()) { st.st = 'idle'; return; }
    if (st.st === 'slide') {
      let x, z;
      if (st.lock > 0) { st.lock = Math.max(0, st.lock - dt); const k = 1 - st.lock / 0.1; x = st.from[0] + (st.a[0] - st.from[0]) * k; z = st.from[1] + (st.a[1] - st.from[1]) * k; }
      else { st.t = Math.min(1, st.t + dt * PZ.speed / Math.max(0.1, st.len)); x = st.a[0] + (st.b[0] - st.a[0]) * st.t; z = st.a[1] + (st.b[1] - st.a[1]) * st.t; }
      p.x = x; p.z = z; p.y = c.heightAt(x, z);
      if (st.lock <= 0 && st.t >= 1) {
        st.st = 'idle'; st.pos = null; this.pzPrev = null; st.at = st.end === 'goal' ? 'goal' : st.end;
        if (st.end === 'goal') this.pzSolved();
        else if (st.end[1] === -1) st.at = 'bank';
      }
      return;
    }
    // idle: standing on the ice, a push of the stick starts a slide
    const prev = this.pzPrev; this.pzPrev = [p.x, p.z];
    const onIce = p.z < PZ.zS && p.z > PZ.zN - 1.0 && Math.abs(p.x) < 11.9;
    if (!prev || dt <= 0 || G.dlg || G.busy || G.title) return;
    const dx = p.x - prev[0], dz = p.z - prev[1], sp = Math.hypot(dx, dz) / dt;
    if (!onIce || sp < 1.2) return;
    const d = Math.abs(dx) > Math.abs(dz) ? (dx > 0 ? 'E' : 'W') : (dz < 0 ? 'N' : 'S');
    const wasBank = prev[1] >= PZ.zS;
    if (wasBank && d !== 'N') return;   // from the bank the only slide is north onto the ice
    if (!this.pzStart(d, wasBank)) { const [cc, rr] = this.pzCell(); if (!wasBank && rr >= 0) { const q2 = pzXZ(cc, rr); p.x = q2[0]; p.z = q2[1]; } }
  }
  pzSolved() {
    const S = this.G.S; S.found = { ...(S.found || {}), tb_slide: 1 }; gold(this.G, 40);
    this.G.toast('The far door grinds open. The pools go quiet, plain ice underfoot now.', 3.2); this.G.save && this.G.save();
  }
  pzReset() {   // the ice runes pull you back to the bank, from anywhere on the pools
    const c = this.ctx, p = c.player, st = this.pz; if (!this.pzOn() || st.st !== 'idle') return;
    const [cc] = this.pzCell(), b = pzXZ(Math.max(0, Math.min(PZ.cols - 1, cc)), -1);
    c.stopWalk && c.stopWalk(); p.x = 0; p.z = b[1]; p.y = c.heightAt(p.x, p.z); st.at = 'bank'; st.resets++; this.pzPrev = null;
    this.G.toast('The ice runes pull you back to the bank.', 1.8);
  }
  // Dark Stonehollow: switch off the scene's cold-fire lamps (the blue / teal ones; the warm giant lanterns stay) so only the glow orbs and lanterns light the town
  darken(ctx) {
    this.coldLamps = 0; this.coldMeshes = 0;
    const cold = (ctx.lamps || []).filter((L) => L.tint && L.tint.r <= L.tint.b);
    const w0 = (ctx.lamps || []).find((L) => L.light && L.light.parent); const world = w0 && w0.light.parent;
    if (world) { world.updateMatrixWorld(true); const v = ctx.camera.position.clone();
      world.traverse((o) => {   // the braziers' / rune stones' / lake's blue 'glow' meshes (vertex-coloured) sit under a cold lamp: they go dark; warm lantern and window glows stay
        if (!o.isMesh) return;
        const ms = Array.isArray(o.material) ? o.material : [o.material];
        if (!ms.some((m) => m && m.name === 'glow')) return;
        o.getWorldPosition(v);
        if (!cold.some((L) => Math.hypot(L.pos.x - v.x, L.pos.z - v.z) < 1.0)) return;
        for (const m of ms) if (m && m.name === 'glow') { m.visible = false; this.coldMeshes++; }
      }); }
    for (const L of ctx.lamps || []) {
      // warm lanterns are #ffc866 (red-heavy), cold fire is blue / teal
      if (!L.tint || L.tint.r > L.tint.b) continue;
      if (L.light) { if (L.light.parent) L.light.parent.remove(L.light); L.light = null; }
      L.glow = false; L.fixed = null; this.coldLamps++;
    }
  }
  // ---- the Hall of Hearthstones (story 2.4, 4): the Jarl, the ice cellar trapdoor and the false Heart's three clues. The cellar is the walled pocket
  // east of the hall (spawn `cellar`); the trapdoor and the cellar stair move the player between the two (no loading, one scene).
  hall(ctx) {
    const G = this.G, still = !!G.qaStill; this.inCellar = false;
    for (const [name, [x, z], dy, glow] of JT_FX.jt_hall) {
      const y = ctx.heightAt(x, z);
      if (ctx.gamefx && ctx.gamefx.meta.effects[name]) this.fx.push(ctx.gamefx.spawn(name, x, y + dy, z, { duration: Infinity, fadeIn: still ? 0 : 0.6 }));
      if (glow && ctx.addGlow) this.lights.push(ctx.addGlow(x, y, z, { color: COLD[0], intensity: COLD[1], range: COLD[2], lift: dy, fadeIn: still ? 0.01 : 0.8 }));
    }
    this.spot({ id: 'trapdoor', pos: [5.0, -7.4], r: 1.7, label: 'the ice cellar trapdoor (E / A)', show: () => !this.inCellar, act: () => this.trapdoor() });
    this.spot({ id: 'plinth', pos: [14.2, -8.6], r: 2.0, label: 'the false Heart (E / A)', act: () => this.plinth() });
    this.spot({ id: 'rime', pos: [16.2, -9.0], r: 1.5, label: 'the rime on the plinth (E / A)', act: () => this.rime() });
    this.spot({ id: 'stair', pos: [14.2, -1.8], r: 1.6, label: 'the cellar stair (E / A)', act: () => this.cellarStair() });
  }
  // ---- the Rime Caves (story 2.5): Solvi's rune-hall, the Barrow mouth with its three rune locks, the frozen waterfall's hidden spring
  caves(ctx) {
    const G = this.G, still = !!G.qaStill;
    for (const [name, [x, z], dy, glow] of JT_FX.rimecaves) {
      const y = ctx.heightAt(x, z);
      if (ctx.gamefx && ctx.gamefx.meta.effects[name]) this.fx.push(ctx.gamefx.spawn(name, x, y + dy, z, { duration: Infinity, fadeIn: still ? 0 : 0.6 }));
      if (glow && ctx.addGlow) this.lights.push(ctx.addGlow(x, y, z, { color: COLD[0], intensity: COLD[1], range: COLD[2], lift: dy, fadeIn: still ? 0.01 : 0.8 }));
    }
    this.spot({ id: 'door', pos: [0, -7.6], r: 2.2, label: 'the Barrow door (E / A)', act: () => this.barrowDoor() });
    this.spot({ id: 'spring', pos: [9.0, -7.4], r: 2.0, label: 'the frozen waterfall (E / A)', act: () => this.springLook() });
    // the Toll of Stones (conquer, story 3.5): three watch-cairns with two Rime Berserkers each, then the Rime-Captain
    CAIRNS.forEach(([x, z], i) => this.spot({ id: 'tt' + (i + 1), pos: [x, z], r: 1.8, label: 'a watch-cairn (E / A: topple it)', show: () => q(this.G.S, 'jt_take') === 1 && !(this.G.S.found || {})['tt_c' + (i + 1)], act: () => this.cairn(i + 1) }));
    this.spot({ id: 'captain', pos: [0, -3.6], r: 1.6, label: 'the Rime-Captain\'s post (E / A)', show: () => q(this.G.S, 'jt_take') === 1 && CAIRNS.every((_, i) => (this.G.S.found || {})['tt_c' + (i + 1)]) && !F(this.G.S).barrow_key, act: () => this.captain() });
  }
  cairn(n) {
    const S = this.G.S, c = this.ctx, [x, z] = CAIRNS[n - 1];
    if (this.cb['tt' + n + 'a'] || this.cb['tt' + n + 'b']) return this.look('tt_busy' + n, 'The watch-cairn', ['The cairn-wardens are already on you.']);
    this.look('tt_c' + n, 'The watch-cairn', ['A watch-cairn of stacked rime-stone, a horn on top. Two Rime Berserkers sleep against it. Not for long.'], () => {
      let left = 2;
      const dead = () => { if (--left > 0) return; S.found = { ...(S.found || {}), ['tt_c' + n]: 1 }; delete this.cb['tt' + n + 'a']; delete this.cb['tt' + n + 'b']; this.G.toast(`Cairn ${n} toppled.`, 2.4); this.G.save && this.G.save(); this.G.refreshMarkers && this.G.refreshMarkers(); };
      ['a', 'b'].forEach((k, j) => this.foe({ id: 'tt' + n + k, role: 'rime_berserker', pos: [x + (j ? 1.4 : -1.4), z - 1.4] }, dead));
    });
  }
  captain() {
    const G = this.G, S = G.S;
    if (this.cb.hjordis) return;
    this.look('tt_captain', 'Rime-Captain Hjordis Icejaw', ['"Cairns toppled by a small one. Hm. My shield wall says no, my pride says yes."', '"Show me. If you can lay me on my back, the Key is yours."'], () => {
      this.foe({ id: 'hjordis', role: 'rime_berserker', def: 'hjordis', pos: [0, -9.6], trial: true }, () => {}, (e) => {
        delete this.cb.hjordis; const f = flags(S); f.tt_captain = 1; f.barrow_key = 1; G.give('barrow_key', 1); G.setQuest('jt_take', 2);
        this.look('tt_key', 'Rime-Captain Hjordis Icejaw', ['(Hjordis lowers her shield, breathing hard.) "Enough. You have the arm for it."', '"The Barrow Key. Do not make me regret it."']);
        G.save && G.save(); G.refreshMarkers && G.refreshMarkers();
      });
    });
  }
  barrowOpen() { const f = F(this.G.S), al = (f.alliance || {}).jotunheim; return !!((al === 'befriend' && f.jt_trusted) || f.jt_contract || f.barrow_key || f.jt_barrow_open); }
  // ---- the Titan's Barrow B1-B4 (story 7): the door hall, the Hall of Shields (brazier 1), the Glow Pools, the Avalanche Run (brazier 2; 2.4 m up)
  barrowRooms(ctx) {
    const still = !!this.G.qaStill;
    for (const [name, [x, z], dy, glow] of JT_FX.barrow) {
      const y = ctx.heightAt(x, z);
      if (ctx.gamefx && ctx.gamefx.meta.effects[name]) this.fx.push(ctx.gamefx.spawn(name, x, y + dy, z, { duration: Infinity, fadeIn: still ? 0 : 0.6 }));
      if (glow && ctx.addGlow) this.lights.push(ctx.addGlow(x, y, z, { color: COLD[0], intensity: COLD[1], range: COLD[2], lift: dy, fadeIn: still ? 0.01 : 0.8 }));
    }
    this.pz = { st: 'idle', moves: 0, resets: 0, at: 'bank' }; this.pzPrev = null;
    const follow = [0, 0];   // the reset spot follows you over the ice (and gives way to the heart-ice shard)
    this.spot({ id: 'pzreset', pos: follow, r: 0.6, label: 'the ice runes hum (E / A: they slide you back to the bank)', show: () => {
      const c = this.ctx; if (!c || !this.pzOn() || this.pz.st !== 'idle') return false;
      const p = c.player; if (p.z >= PZ.zS || p.z < PZ.zN) return false;
      follow[0] = p.x; follow[1] = p.z;
      return !HI.some(([k, a, pos]) => a === 'barrow' && q(this.G.S, 'jt_axe') === 1 && !(this.G.S.found || {})[k] && Math.hypot(p.x - pos[0], p.z - pos[1]) < 1.6);
    }, act: () => this.pzReset() });
    this.hiSpots(ctx);
    this.spot({ id: 'tb1', pos: [0, -7.4], r: 1.8, label: () => ((this.G.S.found || {}).tb_b1 ? 'the snuffed brazier' : "Veyra's cold-fire brazier (E / A: snuff it)"), act: () => this.snuff('tb_b1', 'one') });
    this.spot({ id: 'tb2', pos: [0, -27.6], r: 1.8, label: () => ((this.G.S.found || {}).tb_b2 ? 'the snuffed brazier' : "Veyra's cold-fire brazier (E / A: snuff it)"), act: () => this.snuff('tb_b2', 'two') });
  }
  hiSpots(ctx) {   // heart-ice for the Rimebreaker (jt_axe): hi_1 in the Glow Pools, hi_2 behind Ormgar's seat, hi_3 in the crypt crystals
    const S = this.G.S;
    HI.filter(([, a]) => a === this.area).forEach(([k, , pos]) => {
      const live = () => q(S, 'jt_axe') === 1 && !(S.found || {})[k];
      if (live() && ctx.gamefx && ctx.gamefx.meta.effects.ice_sparkles) this.fx.push(ctx.gamefx.spawn('ice_sparkles', pos[0], ctx.heightAt(pos[0], pos[1]) + 0.5, pos[1], { duration: Infinity, fadeIn: this.G.qaStill ? 0 : 0.6 }));
      this.spot({ id: k, pos, r: 1.6, label: 'a shard of heart-ice (E / A)', show: live, act: () => this.look(k, 'Heart-ice', ['A shard of heart-ice, humming in the cold. It is not melting.'], () => {
        S.found = { ...(S.found || {}), [k]: 1 }; this.G.give('heart_ice', 1);
        if (HI.every(([kk]) => S.found[kk])) { this.G.setQuest('jt_axe', 2); this.G.toast('Three heart-ice. Take them to Solvi in the Hall.', 2.8); }
        this.G.refreshMarkers && this.G.refreshMarkers(); this.G.save && this.G.save();
      }) });
    });
  }
  snuff(key, n) {
    const S = this.G.S;
    if ((S.found || {})[key]) return this.look('tb_done_' + key, 'The brazier', ['Only grey ash. The Titan is a little quieter.']);
    this.look('tb_' + key, "Veyra's brazier", ['A cold-fire brazier, lit by someone who knew the Barrow. The flame leans toward you. You smother it, and the hall goes a little less blue.'], () => {
      S.found = { ...(S.found || {}), [key]: 1 }; this.G.toast(`Brazier ${n} snuffed.`, 2.4); this.G.save && this.G.save();
    });
  }
  barrowDoor() {
    const S = this.G.S, f = F(S), al = (f.alliance || {}).jotunheim;
    if (q(S, 'jt_ulfar') === 2 && f.uw_walk) return this.ulfarFinish();
    if (this.barrowOpen()) {
      const how = f.jt_contract ? "Skuli's goat-path leads round the side of the door and in." : f.barrow_key ? 'The Barrow Key turns all three locks at once.' : 'Solvi stands at the door and hums. The three rune locks slide open, one above the other.';
      return this.look('jt_barrow_door', 'The Barrow door', ['A stone door six metres tall, sunk in the cliff.', how, 'Cold light and the smell of old iron breathe out of the dark.'], () => {
        if (!(S.quests || {}).barrow) S.quests = { ...(S.quests || {}), barrow: 1 };
        if (f.jt_contract && q(S, 'jt_hire') === 1) this.G.setQuest('jt_hire', 2);
        if (f.barrow_key && q(S, 'jt_take') === 2) { this.G.setQuest('jt_take', 3); this.G.factions.add('gate', MERIT.tollstones, 'tollstones'); gold(this.G, 120); }
        this.G.save && this.G.save(); this.G.loadArea('barrow', 'from_caves');
      });
    }
    const how = al === 'conquer' ? 'The Barrow Key would open them all at once.' : al === 'befriend' ? 'Solvi can open them, when the Jarl trusts you with the Titan.' : "Without the Jarl's word or a key, they stay locked.";
    this.look('jt_barrow_door', 'The Barrow door', ['A stone door six metres tall, sunk in the cliff. Three rune locks glow dull blue across it, one above the other.', how]);
  }
  springLook() {
    const S = this.G.S;
    if (!(S.found || {}).rc_spring) this.look('rc_waterfall', 'The frozen waterfall', ['A waterfall frozen mid-fall, thick as a tree. Something blue glints behind it.', '(Any fire spell cast close by would melt it.)']);
    else this.look('rc_spring', 'The hidden spring', ['The thaw has uncovered a hidden spring behind the waterfall. The water is cold and very clear.']);
  }
  onCast() {   // a spell cast within 2.6 m of the frozen waterfall (rimecaves) or the Throne Barrow's ice wall melts it (the Hollows brazier / flue rule)
    const c = this.ctx, S = this.G.S, T = { rimecaves: [9.0, -7.4, 'rc_spring'], barrow2: [8.0, -38.6, 'tb_spring'] }[this.area]; if (!c || !T || (S.found || {})[T[2]]) return;
    if (Math.hypot(c.player.x - T[0], c.player.z - T[1]) > 2.6) return;
    S.found = { ...(S.found || {}), [T[2]]: 1 }; this.G.toast('The ice sweats and cracks: a hidden spring.', 2.6);
    if (c.gamefx && c.gamefx.meta.effects.snow_puff) this.fx.push(c.gamefx.spawn('snow_puff', T[0], c.heightAt(T[0], T[1]) + 0.6, T[1], { duration: 1.6 }));
    this.G.save && this.G.save();
  }
  // a runtime foe: spawnEnemy + onKill (and onYield for trial foes); cb[id] lets the QA kill it without a fight
  foe(sp, then, yielded) {
    const C = this.G.combat; if (!C || !this.ctx) return null;
    const e = C.spawnEnemy({ once: true, noRespawn: true, ...sp }, true); e.state = 'chase';
    const done = () => { delete this.cb[sp.id]; (yielded && sp.trial ? yielded : then)(e); };
    e.onKill = done; if (yielded) e.onYield = done; this.cb[sp.id] = done;
    return e;
  }
  // ---- the Throne Barrow B5-B9
  deepRooms(ctx) {
    const still = !!this.G.qaStill, S = this.G.S;
    for (const [name, [x, z], dy, glow] of JT_FX.barrow2) {
      const y = ctx.heightAt(x, z);
      if (ctx.gamefx && ctx.gamefx.meta.effects[name]) this.fx.push(ctx.gamefx.spawn(name, x, y + dy, z, { duration: Infinity, fadeIn: still ? 0 : 0.6 }));
      if (glow && ctx.addGlow) this.lights.push(ctx.addGlow(x, y, z, { color: COLD[0], intensity: COLD[1], range: COLD[2], lift: dy, fadeIn: still ? 0.01 : 0.8 }));
    }
    this.hiSpots(ctx);
    const lab = (k) => () => ((this.G.S.found || {})[k] ? 'the snuffed brazier' : "Veyra's cold-fire brazier (E / A: snuff it)");
    this.spot({ id: 'tb3', pos: [0, -32.0], r: 1.8, label: lab('tb_b3'), act: () => this.snuff('tb_b3', 'three') });
    BRIDGE.LIT.forEach((cols, r) => cols.forEach((c) => { const [x, z] = bridgeCentre(c, r), y = ctx.heightAt(x, z);
      if (ctx.gamefx && ctx.gamefx.meta.effects.rune_pulse) this.fx.push(ctx.gamefx.spawn('rune_pulse', x, y + 0.25, z, { duration: Infinity, fadeIn: still ? 0 : 0.6 })); }));
    this.spot({ id: 'bridgehint', pos: [3.6, -15.2], r: 1.6, label: 'a frost-rune tablet (E / A)', act: () => this.look('tb_bridge_hint', 'Rune tablet', ['"ONLY THE LIT RUNES WILL BEAR YOU. THE DARK ONES REMEMBER THE COLD."', '(Pale runes pulse in the ice ahead. The dark tiles between them look thin.)']) });
    THRONE_BRAZ.forEach(([x, z], i) => this.spot({ id: 'tbt' + (i + 1), pos: [x, z], r: 1.8, label: 'the relit cold-fire brazier (E / A: snuff it)', show: () => !!(this.relit && this.relit[i]), act: () => this.snuffThrone(i) }));
    this.spot({ id: 'echo', pos: [0, 0.8], r: 2.0, label: 'a wall of black ice (E / A)', act: () => this.echo() });
    this.spot({ id: 'tablet1', pos: [-6.6, -38.0], r: 1.6, label: 'a rune tablet (E / A)', act: () => this.look('tb_t1', 'Rune tablet', ['"HRIMGARD STONEBROW, FIRST JARL. HE BUILT THE HALL WITH HIS HANDS AND HELD THE PASS WITH HIS BACK."', '"LET HIM SLEEP. A KING WHO WAKES IS HUNGRY."']) });
    this.spot({ id: 'tablet2', pos: [6.6, -38.0], r: 1.6, label: 'a rune tablet (E / A)', act: () => this.look('tb_t2', 'Rune tablet', ['"THREE FIRES LIT BY STRANGERS. THREE FIRES TO PUT OUT. THEN THE HALL IS QUIET AGAIN."', '(Someone has scratched a small bird beneath it. Veyra\'s mark.)']) });
    this.spot({ id: 'tbspring', pos: [8.0, -38.6], r: 2.0, label: 'the ice wall (E / A)', act: () => ((S.found || {}).tb_spring ? this.look('tb_spring', 'The hidden spring', ['A spring of clear, cold water behind the thawed wall.']) : this.look('tb_wall', 'The ice wall', ['A wall of old ice, a dark hollow behind it.', '(Any fire spell cast close by would melt it.)'])) });
  }
  echo() {
    const f = flags(this.G.S);
    const pages = ['(The black ice shows you, then someone behind you. Small, hooded, smiling.)', '"You walked all the way here following my footprints. Good dog."', '"Two realms at war over a hollow shell. You can\'t fix them all."'];
    if (f.veyra_revealed) pages.push('"No masks now. Freeze with them or walk away."');
    this.look('tb_echo', 'The Frozen Echo', pages, () => { if (f.veyra_revealed) { f.jt_veyra = 1; this.G.save && this.G.save(); } });
  }
  tbBoss(which) {   // Ormgar in the Berserker Hall, Hrimgard on the dais; each once, scripted from the player's position
    const G = this.G, S = G.S, f = F(S);
    if (which === 'ormgar') {
      if (this.cb.ormgar || (S.found || {}).tb_ormgar) return;
      this.orm = this.foe({ id: 'ormgar', role: 'ormgar', def: 'ormgar', pos: [0, -12.4] }, () => { S.found = { ...(S.found || {}), tb_ormgar: 1 }; G.toast('Ormgar falls. The hall goes quiet.', 2.4); G.save && G.save(); });
    } else {
      if (this.cb.hrimgard || (S.found || {}).tb_boss) return;
      G.toast('"Who wakes the first Jarl?"', 3.0);
      this.boss = this.foe({ id: 'hrimgard', role: 'hrimgard', def: 'hrimgard', pos: [0, -50.0] }, () => this.tbDown());
    }
  }
  deepTick(dt) {
    const c = this.ctx, p = c.player, G = this.G, S = G.S, f = S.found || (S.found = {});
    // the Rune Bridge: an unlit tile cracks and drops you back at the head
    if (p.y > 2.0 && p.x > BRIDGE.x0 && p.x < -BRIDGE.x0 && p.z < BRIDGE.z0 && p.z > -30.2 && !f.tb_bridge) {
      const t = bridgeTile(p.x, p.z);
      if (t && !BRIDGE.LIT[t[1]].includes(t[0])) this.crack(t);
    }
    if (!f.tb_bridge && p.y > 2.0 && p.z < BRIDGE.endZ + 0.1 && Math.abs(p.x) < 2.8) { f.tb_bridge = 1; G.toast('The runes hold. The far side is yours.', 2.6); G.save && G.save(); }
    this.tickOrmgar();
    this.tickHrimgard(dt);
  }
  crack(t) {
    const c = this.ctx, p = c.player, G = this.G, [x, z] = bridgeCentre(t[0], t[1]);
    this.falls = (this.falls || 0) + 1;
    if (c.gamefx && c.gamefx.meta.effects.snow_puff) this.fx.push(c.gamefx.spawn('snow_puff', x, c.heightAt(x, z) + 0.4, z, { duration: 1.4 }));
    G.toast('The dark ice cracks under you! Back to the bridge head. Only the lit runes hold.', 2.4);
    p.x = BRIDGE.head[0]; p.z = BRIDGE.head[1]; p.y = c.heightAt(p.x, p.z);
    if (G.combat && G.combat.hurtPlayer) G.combat.hurtPlayer(5, { x, z }, 0);
  }
  tickOrmgar() {   // frenzy at 50% HP: faster, quicker swings, harder hits
    const e = this.orm; if (!e || e.state === 'dead' || e.state === 'gone' || e.frenzy || e.hp / e.D.hp >= 0.5) return;
    e.frenzy = 1; e.D = { ...e.D, speed: e.D.speed * 1.35, cd: e.D.cd * 0.7, dmg: Math.round(e.D.dmg * 1.2) }; e.a.speed = e.D.speed;
    this.G.toast('Ormgar howls: FRENZY!', 2.2);
    if (this.ctx.effects) this.ctx.effects.spawn('frost_puff', e.a.x, e.a.y + 1.2, e.a.z + 0.05);
  }
  tickHrimgard(dt) {
    const e = this.boss, c = this.ctx, p = c.player, G = this.G; if (!e || e.state === 'dead' || e.state === 'gone') { this.slideV = null; return; }
    const fr = e.hp / e.D.hp, ph = fr < e.D.phases[1] ? 3 : fr < e.D.phases[0] ? 2 : 1; e.phaseN = ph;
    if (ph >= 2 && !e.p2) {   // P2: the throne-room floor freezes (slide) and two ice golems rise
      e.p2 = 1; this.slideV = [0, 0]; G.toast('The throne-room floor freezes over. Ice golems rise from the dais.', 3.0);
      [[-5.5, -48.0], [5.5, -48.0]].forEach(([x, z], i) => this.foe({ id: 'hr_m' + (i + 1), role: 'ice_golem', pos: [x, z] }, () => {}));
    }
    if (ph >= 3 && !e.p3) { e.p3 = 1; e.p3t = 0; e.healT = 0; this.relit = [0, 0, 0]; this.snuffed = [0, 0, 0]; G.toast('The braziers you snuffed gutter back to life. Snuff them again!', 3.0); }
    if (e.p3) {   // P3: the braziers relight one by one; each lit one mends him until you snuff it
      e.p3t += dt;
      THRONE_BRAZ.forEach(([x, z], i) => {
        if (!this.relit[i] && !this.snuffed[i] && e.p3t > 3 + 4 * i) {
          this.relit[i] = 1; const y = c.heightAt(x, z);
          if (c.gamefx && c.gamefx.meta.effects.rune_pulse) this.relitFx[i] = c.gamefx.spawn('rune_pulse', x, y + 1.6, z, { duration: Infinity, fadeIn: 0.4 });
          G.toast(`A brazier relights (${this.relit.filter(Boolean).length}/3). Snuff it, or he mends.`, 2.0);
        }
      });
      e.healT += dt; const n = this.relit.filter(Boolean).length;
      if (e.healT > 2) { e.healT = 0; if (n) e.hp = Math.min(e.hp + e.D.hp * 0.012 * n, e.D.hp * 0.3); }
    }
    // the frozen floor: you keep sliding for a moment after you stop (on the dais only)
    if (this.slideV && p.y > 3.3 && p.z < -42.4) {
      const prev = this.slidePrev, k = Math.min(1, 1.5 * dt);
      if (prev && dt > 0) { const vx = (p.x - prev[0]) / dt, vz = (p.z - prev[1]) / dt; this.slideV[0] += (vx - this.slideV[0]) * k; this.slideV[1] += (vz - this.slideV[1]) * k; }
      if (c.collide) { const [nx, nz, nh, ok] = c.collide.move(p.x, p.z, p.y, this.slideV[0] * dt * 0.9, this.slideV[1] * dt * 0.9, p.r); if (ok !== false) { p.x = nx; p.z = nz; p.y = nh; } }
      this.slidePrev = [p.x, p.z];
    } else { this.slidePrev = null; if (this.slideV) { this.slideV[0] *= 0.5; this.slideV[1] *= 0.5; } }
  }
  snuffThrone(i) {
    const G = this.G; if (!this.relit || !this.relit[i]) return;
    this.relit[i] = 0; this.snuffed[i] = 1; const f = this.relitFx[i]; if (f) f.dur = f.t + 0.2; this.relitFx[i] = null;
    G.toast(`Brazier snuffed (${this.relit.filter(Boolean).length}/3 still burning).`, 2.0);
  }
  tbDown() {
    const G = this.G, S = G.S, f = flags(S), conq = (f.alliance || {}).jotunheim === 'conquer';
    S.found = { ...(S.found || {}), tb_boss: 1 };
    if (conq) {
      S.found.tb_crown = 1; f.jt_dark = 1; G.setQuest('barrow', 3); G.factions.add('gate', MERIT.barrow, 'barrow_c'); gold(G, 150);
      this.look('tb_crown', 'Hrimgard the Unthawed', ['(The ice throne cracks. You lift the rune-iron crown from the dust.)', '(Far away, the cold fires over Stonehollow gutter out.)']);
    } else {
      S.found.tb_slept = 1; G.setQuest('barrow', 2);
      this.look('tb_slept', 'Hrimgard the Unthawed', ['(The braziers die one by one. The king sinks into the ice, slow as a sigh.)', '"Tell Thyra... the stones still stand."']);
    }
    G.save && G.save(); G.refreshMarkers && G.refreshMarkers();
  }
  // ---- The Barred Gate (story 3.1) at Bifrost: Kolbrun at the arch, Halvard's drawer, the horn
  bifrost() {
    const G = this.G, S = G.S, open = () => gateOpen(S, this.qs());
    this.spot({ id: 'kolbrun', pos: [5.0, -9.8], r: 2.2, label: 'Envoy Kolbrun Hailstride (E / A)', show: () => !open() || q(S, 'jt_gate') === 2, act: () => this.kolbrun() });
    this.spot({ id: 'halvard', pos: [-4.4, 1.2], r: 1.8, label: 'Gatewright Halvard: the horn (E / A)', show: () => !!F(S).jg_asked && !F(S).jg_horn, act: () => this.horn() });
    this.spot({ id: 'arch', pos: [5.0, -11.0], r: 1.8, label: 'the barred ice arch: sound the horn (E / A)', show: () => !!F(S).jg_horn && !F(S).jg_troll && !open(), act: () => this.sound() });
  }
  kolbrun() {
    const G = this.G, S = G.S, f = flags(S), K = 'Envoy Kolbrun Hailstride';
    if (q(S, 'jt_gate') === 2) return this.look('jg_done', K, ['(The bar beam lies cracked across the snow.)', '"A troll for a doorbell. Fine. The gate is open. Mind your head."'], () => {
      f.jt_gate_open = 1; G.setQuest('jt_gate', 3); G.factions.add('gate', MERIT.jt_gate, 'jt_gate'); gold(G, 50); this.gate.reopen(); G.refreshMarkers && G.refreshMarkers(); G.save && G.save();
    });
    if (!G.factions.has('embassy', 1)) return this.look('jg_no', K, ["You want our gate open? Then be someone the Embassies vouch for. Bring that, and I'll talk."]);
    if (!f.jg_asked) return this.look('jg_ask', K, ['The Embassies like you. Fine. Halvard has my horn. Ask him nicely, he loses things.'], () => { f.jg_asked = 1; G.setQuest('jt_gate', 1); G.save && G.save(); });
    this.look('jg_wait', K, [!f.jg_horn ? 'Halvard has my horn. Nicely, I said.' : 'Sound it at the arch. Stand back. Then do not stand back.']);
  }
  horn() {
    const f = flags(this.G.S);
    this.look('jg_horn', 'Gatewright Halvard', ["Kolbrun's horn? In safe keeping! (He opens the wrong drawer, then the right one.) Ah. There. It is rather large."], () => { f.jg_horn = 1; this.G.toast("You carry Kolbrun's horn.", 2.4); this.G.save && this.G.save(); });
  }
  sound() {   // Bifrost has no Jotunheim foe sheets, so the troll comes through on the Stonehollow side of the arch (spawned by update() on arrival)
    const G = this.G, f = flags(G.S);
    this.look('jg_sound', 'The barred ice arch', ['(You sound the horn. The bar beam lifts with a groan, the ice arch flares blue, and you are pulled through.)'], () => {
      f.jg_sounded = 1; G.save && G.save(); G.loadArea('jotunheim', 'from_bifrost');
    });
  }
  gateTroll() {
    const G = this.G, f = flags(G.S);
    this.foe({ id: 'jg_troll', role: 'frost_troll', pos: [0, 6.2] }, () => { f.jg_troll = 1; G.setQuest('jt_gate', 2); G.toast('The troll falls. Tell Kolbrun at the Bifrost arch.', 2.8); G.save && G.save(); G.refreshMarkers && G.refreshMarkers(); });
  }
  moveTo(x, z) { const c = this.ctx; if (!c) return; c.player.x = x; c.player.z = z; c.player.y = c.heightAt(x, z); }
  trapdoor() {
    const S = this.G.S;
    if (!cellarOK(S)) { this.look('jt_trapdoor', 'The cellar trapdoor', ['A trapdoor of black oak, barred. A guard shifts to stand on it.', '"Nobody goes down without the Jarl\'s word."']); return; }
    this.look('jt_trapdoor', 'The cellar trapdoor', ['(You heave the trapdoor up. Cold breathes out, and a blue light below.)'], () => { this.inCellar = true; this.moveTo(14.2, -3.4); });
  }
  clue(k, name) {
    const G = this.G, S = G.S, f = flags(S); if (f[k]) return; f[k] = 1;
    G.toast(`Clue: ${name} (${clueN(S)}/3)`, 2.2);
    if (q(S, 'jt_heart') === 1 && !f.sv_decoy && clueN(S) >= 3) { G.setQuest('jt_heart', 2); G.refreshMarkers && G.refreshMarkers(); }
    G.save && G.save();
  }
  plinth() {
    const G = this.G, S = G.S, con = ((F(S).alliance || {}).jotunheim) === 'conquer';
    S.evidence = { ...(S.evidence || {}), jotunheim: 'false_heart' };   // the evidence counts on every path, if you look (story 4.4)
    const pages = ['(The false Heart sits on its plinth, a shell of frost-iron shaped like a heart. You tap it. It rings hollow, like a bucket.)', 'The real Anvil-Heart beats like a drum. This one is a shell.'];
    if (con) pages.push('(You could say it is the real one. You could use it as your excuse. Everyone in the hall knows what it sounds like.)');
    this.look('jh_heart', 'The false Heart', pages, () => this.clue('jh_heart', 'it rings hollow'));
  }
  rime() {
    const f = F(this.G.S);
    if (!f.jh_solvi) { this.look('jh_rime', 'The rime', ['The rime on the plinth looks grey in this gloom. Solvi\'s rune-light would show its true colour.']); return; }
    this.look('jh_rime', 'The rime', ["(Solvi's rune-light washes the plinth. The rime is blue-black, like the Cold Altar tongs and the boot mould.)", 'Giant frost is white. This is not giant frost.'], () => this.clue('jh_rime', 'the rime is blue-black'));
  }
  cellarStair() {
    this.look('jh_trail', 'The cellar stair', ['(Frost prints, huge ones, climb the stair. They go in. None come out.)', 'Someone small took off big boots right here, and went on in their socks.'], () => { this.clue('jh_trail', 'the prints go in, none come out'); this.inCellar = false; this.moveTo(4.6, -5.8); });
  }
  prints() {   // story 4: the footprints clue's entry point. The cellar clue (jh_trail) is in the Hall; here you learn the prints exist.
    const f = flags(this.G.S), decoy = !!f.sv_decoy;
    this.G.S.found = { ...(this.G.S.found || {}), jt_prints: 1 };
    this.look('jt_prints', 'Frost prints', decoy
      ? ["Giant prints, in frost. The boots match the mould you found in Anvildeep: the same cut, the same heel.", 'Someone wore these up the ice road and left the Hall by the cellar. Ask the Jarl to show you the cellar.']
      : ['Prints in the frost, bigger than a barrel lid, heading up to the Hall. They do not look like anyone in this town walks like that.', "(Jarl Thyra's cellar may know who wore them.)"]);
  }
  // ---- Welcome Ring stones (story 3.2): timing beat, 3 lifts (2 for the Runeguard)
  liftLive(i) { const S = this.G.S; return q(S, 'jt_welcome') === 1 && !((F(S).jw_done || {})[i]) && (F(S).jw_lifts || 0) < need(S); }
  liftLabel(i) { return this.ring && this.ring.i === i ? 'now! (E / A in the blue)' : 'lift the Welcome stone (E / A on the glow)'; }
  clearRing() { if (this.ring && this.ring.el) this.ring.el.remove(); this.ring = null; }
  tryLift(i) {
    const G = this.G;
    if (this.qs().get('lift') === 'auto') return this.lifted(i, true);
    if (!this.ring) {   // start: the ring fills over 1.6 s, the blue band is 0.55..0.8 of it
      const el = document.createElement('div'); el.id = 'jt-ring';
      el.style.cssText = 'position:fixed;left:50%;bottom:22%;width:180px;height:16px;margin-left:-90px;border:2px solid #cfeaff;border-radius:9px;background:#0a1830;z-index:50;pointer-events:none';
      el.innerHTML = '<div style="position:absolute;left:55%;width:25%;height:100%;background:#2ab4ff;opacity:.85"></div><div id="jt-ring-fill" style="position:absolute;left:0;height:100%;width:0;background:#e9f6ff;opacity:.9"></div>';
      document.body.appendChild(el); this.ring = { i, t: 0, el };
      return;
    }
    const t = this.ring.t / 1.6, hit = t >= 0.55 && t <= 0.8; this.clearRing();
    if (hit) this.lifted(i); else G.toast('The stone thuds. A giant laughs, kindly. Try again.', 2.2);
  }
  lifted(i, auto) {
    const G = this.G, S = G.S, f = flags(S); f.jw_done = { ...(f.jw_done || {}), [i]: 1 }; f.jw_lifts = (f.jw_lifts || 0) + 1; this.lastLift = i;
    const c = this.ctx, [x, z] = SPOTS.lifts[i];
    if (c && c.gamefx && c.gamefx.meta.effects.snow_puff) this.fx.push(c.gamefx.spawn('snow_puff', x, c.heightAt(x, z) + 0.2, z, { duration: 1.6 }));
    G.toast(`The stone lifts! ${Math.min(f.jw_lifts, need(S))}/${need(S)}`, 2);
    if (f.jw_lifts >= need(S)) this.cheer();
    G.drawLog && G.drawLog(); G.save && G.save();
  }
  cheer() {
    const G = this.G, hall = !!AREAS_JOT.jt_hall;
    this.look('jt_cheer', 'Stonehollow', ['(The last stone rolls upright with a boom. Giants lean out of their longhouses and cheer. A goat headbutts a fence in solidarity.)', hall ? "Jarl Thyra waits by her fire." : 'Welcome to Stonehollow, small one.'], (G2) => {
      if (hall) { G2.setQuest('jt_welcome', 2); return; }   // the Jarl's fire is in the Hall (next chunk): until it opens the welcome ends here
      this.finishWelcome(G2);
    });
  }
  finishWelcome(G) { finishWelcome(G); }
  update(dt) {
    if (!this.ctx) return;
    if (this.area === 'jotunheim' && !this.G.dlg && !this.G.busy && this.G.combat && F(this.G.S).jg_sounded && !F(this.G.S).jg_troll && !this.cb.jg_troll) this.gateTroll();
    this.weatherTick(dt);
    if (this.area === 'barrow2') this.deepTick(dt);
    if (this.area === 'barrow') this.pzTick(dt);
    if (this.area === 'barrow2' && !this.G.dlg && this.G.combat) { const z = this.ctx.player.z; if (z < -7.2) this.tbBoss('ormgar'); if (z < -45.0) this.tbBoss('hrimgard'); }
    if (this.ring) {
      this.ring.t += dt; const el = this.ring.el, fill = el && el.querySelector('#jt-ring-fill');
      if (fill) fill.style.width = Math.min(100, (this.ring.t / 1.6) * 100) + '%';
      if (this.ring.t > 1.6) { this.clearRing(); this.G.toast('The stone thuds. A giant laughs, kindly. Try again.', 2.2); }
    }
  }
  // QA helpers for the smoke test
  qaPzGo(d) { return this.pzStart(d); }
  qaPzSolve() { this.pzSolved(); }
  qaLine(id) { const e = TALK[id](this.G.S); return e && e.pages ? e.pages[0] : null; }
  qaTalk(id) { const e = TALK[id](this.G.S); if (e && e.then) e.then(this.G); return { pages: e ? e.pages.length : 0, choice: e && e.choice ? e.choice.options.map((o) => o.label) : null }; }
  qaPick(label, id = 'jarl') { const e = TALK[id](this.G.S), o = e.choice.options.find((x) => x.label === label), nx = o.pick(this.G); if (nx && nx.then) nx.then(this.G); return nx ? nx.pages.length : 0; }
  qaHp(id, frac) { const e = this.G.combat.enemies.find((x) => x.id === id); if (!e) return false; e.hp = e.D.hp * frac; return true; }
  qaSlideKick(vx, vz) { this.slideV = this.slideV || [0, 0]; this.slideV = [vx, vz]; this.slidePrev = null; return true; }
  qaRares() { const c = this.ctx, sp = (RARE_AREAS[this.area] || { spots: [] }).spots, ac = c ? c.actors.list.filter((a) => !a.rare).map((a) => [a.x, a.z]) : []; return { spots: sp, clear: sp.map(([x, z]) => Math.min(...ac.map(([ax, az]) => Math.hypot(ax - x, az - z)))) }; }
  qaFoe(id) { const e = this.G.combat.enemies.find((x) => x.id === id); return e ? { speed: e.D.speed, hp: e.hp, frozen: e.rimeT > 0 } : null; }
  qaFrost(t) { this.frostT = t; this.frostSaid = false; return true; }
  qaKill(id) { const f = this.cb[id]; if (!f) return false; f(); return true; }
  qaBoss(w) { this.tbBoss(w); return !!this.cb[w]; }
  qaSpot(id) { const sp = this.spots.find((x) => x.id === id); if (!sp) return false; sp.act(); return true; }
  qaLift(i) { this.lifted(i, true); return this.qa(); }
  qa() {
    const c = this.ctx, S = this.G.S, f = F(S), gm = c ? (c.scene.game || {}) : {};
    return { realm: 'jotunheim', built: Object.keys(AREAS_JOT), planned: JOT_AREAS, area: this.area, exits: (gm.exits || []).map((e) => e.to), portals: (gm.portals || []).map((p) => p.to),
             spots: this.spots.filter((x) => x.show()).length, lifts: f.jw_lifts || 0, need: need(S), quest: q(S, 'jt_welcome'), gate: this.gate.qa(), alliance: (f.alliance || {}).jotunheim || null,
             actors: c ? c.actors.list.map((a) => a.id || a.role) : [], fx: this.fx.length, lights: this.lights.length, ring: !!this.ring, inCellar: !!this.inCellar, heart: q(S, 'jt_heart'), clues: ['jh_heart', 'jh_rime', 'jh_trail'].filter((k) => f[k]), peace: !!f.jt_peace, evidence: (S.evidence || {}).jotunheim || null, hire: q(S, 'jt_hire'), terms: !!f.jw_terms, skuli: !!f.jw_skuli, pos: c ? [c.player.x, c.player.z] : null, spring: !!(S.found || {}).rc_spring, quest_barrow: q(S, 'barrow'), foes: c ? c.actors.list.filter((a) => ['frost_troll', 'ice_golem', 'avalanche_golem', 'rime_berserker', 'hrimgard', 'ormgar'].includes(a.role)).map((a) => a.role) : [], shop: !!SHOPS.jt_trader, found: S.found || {}, gate_q: q(S, 'jt_gate'), take_q: q(S, 'jt_take'), hire_q: q(S, 'jt_hire'), key: !!f.barrow_key, spells: S.spells || [], unlocks: S.unlocks || {}, cb: Object.keys(this.cb), bridge: { falls: this.falls || 0, solved: !!(S.found || {}).tb_bridge, lit: BRIDGE.LIT, head: BRIDGE.head }, boss: { phase: this.boss ? this.boss.phaseN || 1 : 0, p2: !!(this.boss && this.boss.p2), p3: !!(this.boss && this.boss.p3), relit: this.relit ? this.relit.slice() : null, hp: this.boss ? this.boss.hp : null, max: this.boss ? this.boss.D.hp : null, slide: this.slideV ? this.slideV.slice() : null }, orm: { frenzy: !!(this.orm && this.orm.frenzy), speed: this.orm ? this.orm.D.speed : null, base: ENEMIES.ormgar.speed }, goats: c ? c.actors.list.filter((x) => /^(pen_goat|clatter)/.test(x.id)).map((x) => [x.id, x.role, +x.x.toFixed(2), +x.z.toFixed(2)]) : [],
             goat: { q: q(S, 'jt_goat'), cakes: f.gt_cakes || 0, last: f.gt_lastDay ?? null, cake: (S.inv || {}).oat_cake || 0, mount: !!(S.mounts || {}).goat },
             ulfar: { q: q(S, 'jt_ulfar'), walk: !!F(S).uw_walk, comp: compActive(S), found: ['uw_goat', 'uw_song', 'uw_mitten'].map((k) => (S.found || {})[k] ? 1 : 0), flurry: !!(S.pets || {}).flurry, brute: !!(S.unlocks || {}).frostbrute, town: c ? c.actors.list.some((x) => x.id === 'ulfar') : null },
             pz: { on: this.pzOn ? this.pzOn() : false, st: this.pz ? this.pz.st : null, at: this.pz ? this.pz.at : null, moves: this.pz ? this.pz.moves : 0, resets: this.pz ? this.pz.resets : 0, solved: !!(S.found || {}).tb_slide, layout: { ...PZ } },
             dark: { on: isDark(S), cold: this.coldLamps || 0, meshes: this.coldMeshes || 0, litCold: c ? c.lamps.filter((L) => L.tint && L.tint.r <= L.tint.b && (L.light || L.glow)).length : null, litWarm: c ? c.lamps.filter((L) => L.tint && L.tint.r > L.tint.b && L.light).length : null, orbs: this.fx.filter((f) => f && f.name === 'glow_orb_blue').length, flames: this.fx.filter((f) => f && f.name === 'cold_flame').length, pulses: this.fx.filter((f) => f && f.name === 'rune_pulse').length, glows: this.lights.filter(Boolean).length },
             wx: { kind: this.G.weather ? this.G.weather.kind : null, frost: +(this.frostT || 0).toFixed(1), slow: this.frostSlow || 0, speed: c ? c.player.speed : null, aurora: !!(this.aurora && this.aurora.m) }, rimes: this.rimes || 0, axe: q(S, 'jt_axe'), bag: (S.bag || []).map((i) => i.unique || i.name), hice: (S.inv || {}).heart_ice || 0, gold: S.gold || 0, jg: [f.jg_asked, f.jg_horn, f.jg_troll].map((x) => !!x) };
  }
}

// ------------------------------------------------------------------ the gate (story 3.1 comes next chunk): runtime wiring on both ends, like svartalfheim_gate.js
class JtGate {
  constructor(jt) { this.jt = jt; this.G = jt.G; this.fetching = false; }
  get ctx() { return this.jt.ctx; }
  qs() { return this.jt.qs(); }
  put(sc) { const gm = (sc.game = sc.game || {}); gm.spawns = gm.spawns || {}; if (!gm.spawns.from_jotunheim) gm.spawns.from_jotunheim = JT_ARCH.spawn.slice(); }
  atHub(ctx) {   // Stonehollow: the ice arch back to Bifrost (runtime portal) + the Bifrost scene prefetched with its return spawn
    const G = this.G, gm = ctx.scene.game || (ctx.scene.game = {});
    gm.portals = gm.portals || [];
    if (!gm.portals.find((p) => p.to === 'bifrost')) gm.portals.push({ ...HUB_GATE, rect: HUB_GATE.rect.slice() });
    if (G.scenes && G.scenes.bifrost) { this.put(G.scenes.bifrost); return; }
    if (this.fetching || !G.scenes) return;
    this.fetching = true;
    fetch('areas/bifrost/scene.json').then((r) => r.json()).then((sc) => { if (!G.scenes.bifrost) G.scenes.bifrost = sc; this.put(G.scenes.bifrost); }).catch(() => {}).finally(() => { this.fetching = false; });
  }
  atBifrost(ctx) { this.put(ctx.scene); this.wire(ctx); }
  reopen() { if (this.ctx && this.jt.area === 'bifrost') this.wire(this.ctx); }
  wire(ctx) {   // the sealed ice arch becomes a portal once the gate is open
    const gm = ctx.scene.game; if (!gm || !gateOpen(this.G.S, this.qs())) return;
    gm.sealed = (gm.sealed || []).filter((g) => g.arch !== 'jotunheim');
    gm.portals = gm.portals || [];
    if (!gm.portals.find((p) => p.to === 'jotunheim')) gm.portals.push({ fx: 'gate_jotunheim', to: 'jotunheim', spawn: 'from_bifrost', rect: JT_ARCH.rect.slice(), label: "Jotunheim's gate" });
    (gm.spawns = gm.spawns || {}).from_jotunheim = gm.spawns.from_jotunheim || JT_ARCH.spawn.slice();
  }
  qa() { const c = this.ctx, gm = c ? (c.scene.game || {}) : {}; return { portals: (gm.portals || []).map((p) => p.to), sealed: (gm.sealed || []).map((g) => g.arch), spawns: Object.keys(gm.spawns || {}), open: gateOpen(this.G.S, this.qs()) }; }
}
