// Hearthmoor leveling (stage 2): XP, levels (cap 50), six stats, 2 free points per level (auto by class or manual),
// 1 skill point per level and the first tier of each starter's skill tree (docs/story/DESIGN_EXPANSION_2026-10-03.md E3).
// Pure data + maths; game.js owns the UI, combat.js reads mods().
import { ensure as lootEnsure, gearMods } from './loot.js';
// difficulty: Story (gentle, no faint penalty), Adventurer (default), Hero (hits harder, better loot)
export const MODES = {
  story: { name: 'Story', hurt: 0.6, deal: 1.15, penalty: 0, luck: 0 },
  adventurer: { name: 'Adventurer', hurt: 1, deal: 1, penalty: 0.1, luck: 0 },
  hero: { name: 'Hero', hurt: 1.35, deal: 0.9, penalty: 0.1, luck: 1 },
};
export const MODE_IDS = ['story', 'adventurer', 'hero'];
export const LEVEL_CAP = 50;
export const STATS = [
  { id: 'might', name: 'Might', does: 'melee damage, guard break' },
  { id: 'arcana', name: 'Arcana', does: 'spell damage' },
  { id: 'spirit', name: 'Spirit', does: 'summon power + duration, healing' },
  { id: 'vigor', name: 'Vigor', does: 'max HP' },
  { id: 'grit', name: 'Grit', does: 'block strength, guard stamina' },
  { id: 'swift', name: 'Swiftness', does: 'stamina, dodge, crit chance' },
];
export const STAT_IDS = STATS.map((s) => s.id);
// starting stats and the class lean (auto-level spends the 2 free points in this order, round robin by weight)
export const CLASS_STATS = {
  wildcaller:   { base: { might: 4, arcana: 6, spirit: 6, vigor: 5, grit: 4, swift: 5 }, lean: ['arcana', 'spirit', 'vigor'] },
  runeguard:    { base: { might: 6, arcana: 3, spirit: 4, vigor: 7, grit: 7, swift: 3 }, lean: ['grit', 'vigor', 'might'] },
  seer:         { base: { might: 3, arcana: 7, spirit: 5, vigor: 4, grit: 4, swift: 7 }, lean: ['arcana', 'swift', 'spirit'] },
  stormborn:    { base: { might: 7, arcana: 5, spirit: 4, vigor: 6, grit: 5, swift: 3 }, lean: ['might', 'arcana', 'vigor'] },
  grovekeeper:  { base: { might: 3, arcana: 5, spirit: 8, vigor: 5, grit: 4, swift: 5 }, lean: ['spirit', 'arcana', 'vigor'] },
  cinderknight: { base: { might: 8, arcana: 4, spirit: 3, vigor: 6, grit: 6, swift: 3 }, lean: ['might', 'vigor', 'grit'] },
};
// XP to go from level L to L+1: gentle early, ~1.6 power curve
export const xpNeed = (L) => Math.round(60 * Math.pow(L, 1.6));
export const XP = { golem: 45, skeleton: 28, wraith: 34, icegolem: 55, skelmage: 36, eldergolem: 260, errand: 120, firstKill: 0.5 };

// First tier of each tree: one node per branch (3 per class), 1 skill point each.
export const TREES = {
  wildcaller: [
    { id: 'wc_hearth', branch: 'Hearth', name: 'Warm Light', desc: 'Healing +30%, and 1 HP/s regen out of combat.', mods: { healMul: 0.3, regen: 1 } },
    { id: 'wc_root', branch: 'Root', name: 'Seed Split', desc: 'Seed Bomb bursts into 3 smaller blasts.', mods: { seedSplit: 2 } },
    { id: 'wc_gnome', branch: 'Gnomecraft', name: 'Mushroom Golem II', desc: 'Summon +40% HP and damage, +5 s.', mods: { summonMul: 0.4, summonLife: 5 } },
  ],
  runeguard: [
    { id: 'rg_bulwark', branch: 'Bulwark', name: 'Steady Guard', desc: 'Guarding costs 35% less stamina.', mods: { guardSt: -0.35 } },
    { id: 'rg_axe', branch: 'Axe of Dawn', name: 'Cleave', desc: 'Melee +15% damage and a wider arc.', mods: { meleeMul: 0.15, arc: 0.25 } },
    { id: 'rg_host', branch: 'Shield-host', name: 'Rune Sentinel II', desc: 'Summon +40% HP and damage, +5 s.', mods: { summonMul: 0.4, summonLife: 5 } },
  ],
  seer: [
    { id: 'se_runes', branch: 'Runes', name: 'Wider Circle', desc: 'Rune Trap radius +35%, +20% damage.', mods: { trapRadius: 0.35, spellMul: 0.2 } },
    { id: 'se_sigil', branch: 'Sigil-walking', name: 'Long Step', desc: 'Dodge roll goes 25% farther, +0.1 s i-frames.', mods: { rollSpeed: 0.25, rollIframes: 0.1 } },
    { id: 'se_sight', branch: 'Foresight', name: 'Keen Eye', desc: '+8% critical hit chance.', mods: { crit: 0.08 } },
  ],
  stormborn: [
    { id: 'sb_hand', branch: 'Thunderhand', name: 'Charged Hammer', desc: 'Melee +20% damage.', mods: { meleeMul: 0.2 } },
    { id: 'sb_tempest', branch: 'Tempest', name: 'Forked Bolt', desc: 'Chain Lightning leaps to 1 more foe.', mods: { chainJumps: 1 } },
    { id: 'sb_herd', branch: 'Skyherd', name: 'Storm Sprite II', desc: 'Summon +40% HP and damage, +5 s.', mods: { summonMul: 0.4, summonLife: 5 } },
  ],
  grovekeeper: [
    { id: 'gk_bloom', branch: 'Bloom', name: 'Lush Bloom', desc: 'Healing +35%.', mods: { healMul: 0.35 } },
    { id: 'gk_thorn', branch: 'Thorn and Spore', name: 'Thorn Ring', desc: 'Bloom hits twice as hard.', mods: { spellMul: 1.0 } },
    { id: 'gk_kin', branch: 'Grove Kin', name: 'Sapling II', desc: 'Summon +40% HP and damage, +5 s.', mods: { summonMul: 0.4, summonLife: 5 } },
  ],
  cinderknight: [
    { id: 'ck_blade', branch: 'Ember Blade', name: 'Hot Edge', desc: 'Ember Slash +30% damage.', mods: { spellMul: 0.3 } },
    { id: 'ck_ash', branch: 'Ashen Shadow', name: 'Life Drain', desc: 'Melee hits heal you for 10% of the damage.', mods: { drain: 0.1 } },
    { id: 'ck_legion', branch: 'Ash Legion', name: 'Ember Imp II', desc: 'Summon +40% HP and damage, +5 s.', mods: { summonMul: 0.4, summonLife: 5 } },
  ],
};

// ------------------------------------------------------------------ state helpers (S is the save)
export function ensure(S) {
  lootEnsure(S);
  if (!MODES[S.mode]) S.mode = 'adventurer';
  const cs = CLASS_STATS[S.cls] || CLASS_STATS.wildcaller;
  if (!S.lv) S.lv = 1;
  if (S.xp == null) S.xp = 0;
  if (!S.stats) S.stats = { ...cs.base };
  for (const k of STAT_IDS) if (S.stats[k] == null) S.stats[k] = cs.base[k];
  if (S.free == null) S.free = 0;
  if (S.sp == null) S.sp = 0;
  if (!S.skills) S.skills = {};
  if (!('autoLevel' in S)) S.autoLevel = null;   // null = not asked yet
  return S;
}
// class-based auto assignment of free points: lean stats in turn (2 per level -> the first two of the lean, rotating)
export function autoSpend(S) {
  const lean = (CLASS_STATS[S.cls] || CLASS_STATS.wildcaller).lean;
  let i = (S.lv * 2) % lean.length;
  while (S.free > 0) { S.stats[lean[i % lean.length]]++; S.free--; i++; }
}
// returns the number of levels gained
export function addXP(S, n) {
  ensure(S);
  if (S.lv >= LEVEL_CAP) return 0;
  S.xp += Math.round(n);
  let up = 0;
  while (S.lv < LEVEL_CAP && S.xp >= xpNeed(S.lv)) {
    S.xp -= xpNeed(S.lv); S.lv++; up++;
    S.free += 2; S.sp += 1;
    if (S.autoLevel) autoSpend(S);
  }
  if (S.lv >= LEVEL_CAP) S.xp = 0;
  return up;
}
export function spendStat(S, id) {
  if (!S.free || !STAT_IDS.includes(id)) return false;
  S.stats[id]++; S.free--; return true;
}
export function learn(S, nodeId) {
  const node = (TREES[S.cls] || []).find((n) => n.id === nodeId);
  if (!node || S.skills[nodeId] || S.sp < 1) return false;
  S.skills[nodeId] = 1; S.sp--; return true;
}
// combat modifiers from stats (relative to the class's starting stats, so level 1 plays like stage 1) + learned nodes
export function mods(S) {
  ensure(S);
  const base = (CLASS_STATS[S.cls] || CLASS_STATS.wildcaller).base, st = S.stats;
  const d = (k) => st[k] - base[k];
  const m = {
    meleeMul: 1 + 0.04 * d('might'), spellMul: 1 + 0.04 * d('arcana'), summonMul: 1 + 0.04 * d('spirit'), healMul: 1 + 0.04 * d('spirit'),
    hpAdd: 6 * d('vigor'), guardMul: Math.max(0.6, 1 - 0.025 * d('grit')), guardSt: Math.max(0.5, 1 - 0.03 * d('grit')),
    stAdd: 3 * d('swift'), crit: 0.03 + 0.01 * d('swift'), rollSpeed: 1 + 0.02 * d('swift'), rollIframes: 0,
    summonLife: 0, seedSplit: 0, chainJumps: 0, trapRadius: 1, drain: 0, regen: 0, arc: 0,
  };
  for (const node of TREES[S.cls] || []) {
    if (!S.skills[node.id]) continue;
    for (const [k, v] of Object.entries(node.mods)) {
      if (k === 'guardSt') m.guardSt = Math.max(0.3, m.guardSt + v);
      else if (k === 'trapRadius' || k === 'rollSpeed') m[k] += v;
      else if (k.endsWith('Mul')) m[k] += v;
      else m[k] = (m[k] || 0) + v;
    }
  }
  return gearMods(S, m);
}
