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
export const XP = { golem: 45, skeleton: 28, wraith: 34, icegolem: 55, skelmage: 36, sporeling: 30, mossgolem: 60, eldergolem: 260, errand: 120, firstKill: 0.5 };

// Skill trees: three branches per class, three tiers per branch (Part 4). Tier I: 1 point, any level. Tier II: 1 point,
// level 5, needs that branch's tier I. Tier III (the branch capstone): 2 points, level 10, needs tier II. Rows are
// listed tier I first (the hero screen shows them by tier, so tier-I rows keep their old positions).
export const TIER = { 1: { cost: 1, lv: 1 }, 2: { cost: 1, lv: 5 }, 3: { cost: 2, lv: 10 } };
export const TREES = {
  wildcaller: [
    { tier: 1, id: 'wc_hearth', branch: 'Hearth', name: 'Warm Light', desc: 'Healing +30%, and 1 HP/s regen out of combat.', mods: { healMul: 0.3, regen: 1 } },
    { tier: 1, id: 'wc_root', branch: 'Root', name: 'Seed Split', desc: 'Seed Bomb bursts into 3 smaller blasts.', mods: { seedSplit: 2 } },
    { tier: 1, id: 'wc_gnome', branch: 'Gnomecraft', name: 'Mushroom Golem II', desc: 'Summon +40% HP and damage, +5 s.', mods: { summonMul: 0.4, summonLife: 5 } },
    { tier: 2, id: 'wc_hearth2', branch: 'Hearth', req: 'wc_hearth', name: 'Hearthside', desc: 'Healing +25% more, regen 2 HP/s, stamina refills 25% faster.', mods: { healMul: 0.25, regen: 1, stRegen: 0.25 } },
    { tier: 2, id: 'wc_root2', branch: 'Root', req: 'wc_root', name: 'Deep Roots', desc: 'Seed Bomb +30% damage and spell cooldowns 15% shorter.', mods: { spellMul: 0.3, spellCd: 0.15 } },
    { tier: 2, id: 'wc_gnome2', branch: 'Gnomecraft', req: 'wc_gnome', name: 'Mushroom Golem III', desc: 'Summon tier III: +40% HP and damage, +5 s, a radiant glow-cap form.', mods: { summonMul: 0.4, summonLife: 5, summonTier: 1 } },
    { tier: 3, id: 'wc_hearth3', branch: 'Hearth', req: 'wc_hearth2', name: 'Hearthfire Heart (capstone)', desc: '+40 HP, healing +40%, and you mend 4 HP/s out of combat.', mods: { hpAdd: 40, healMul: 0.4, regen: 2 } },
    { tier: 3, id: 'wc_root3', branch: 'Root', req: 'wc_root2', name: 'Worldroot (capstone)', desc: 'Seed Bomb splits into 2 more blasts, +25% spell damage, +30% crit damage.', mods: { seedSplit: 2, spellMul: 0.25, critDmg: 0.3 } },
    { tier: 3, id: 'wc_gnome3', branch: 'Gnomecraft', req: 'wc_gnome2', name: 'Elder Mushroom Golem (capstone)', desc: 'Summon tier IV: +60% HP and damage, +8 s, summons 25% sooner.', mods: { summonMul: 0.6, summonLife: 8, summonTier: 1, summonCd: 0.25 } },
  ],
  runeguard: [
    { tier: 1, id: 'rg_bulwark', branch: 'Bulwark', name: 'Steady Guard', desc: 'Guarding costs 35% less stamina.', mods: { guardSt: -0.35 } },
    { tier: 1, id: 'rg_axe', branch: 'Axe of Dawn', name: 'Cleave', desc: 'Melee +15% damage and a wider arc.', mods: { meleeMul: 0.15, arc: 0.25 } },
    { tier: 1, id: 'rg_host', branch: 'Shield-host', name: 'Rune Sentinel II', desc: 'Summon +40% HP and damage, +5 s.', mods: { summonMul: 0.4, summonLife: 5 } },
    { tier: 2, id: 'rg_bulwark2', branch: 'Bulwark', req: 'rg_bulwark', name: 'Stone Skin', desc: 'Guarded hits do 10% less, +25 HP.', mods: { guardMul: -0.1, hpAdd: 25 } },
    { tier: 2, id: 'rg_axe2', branch: 'Axe of Dawn', req: 'rg_axe', name: 'Dawn Edge', desc: 'Melee +20% damage, +5% crit.', mods: { meleeMul: 0.2, crit: 0.05 } },
    { tier: 2, id: 'rg_host2', branch: 'Shield-host', req: 'rg_host', name: 'Rune Sentinel III', desc: 'Summon tier III: +40% HP and damage, +5 s, a radiant rune-lit form.', mods: { summonMul: 0.4, summonLife: 5, summonTier: 1 } },
    { tier: 3, id: 'rg_bulwark3', branch: 'Bulwark', req: 'rg_bulwark2', name: 'Unbroken Wall (capstone)', desc: 'Guarding costs 30% less, guarded hits 10% less, +40 HP.', mods: { guardSt: -0.3, guardMul: -0.1, hpAdd: 40 } },
    { tier: 3, id: 'rg_axe3', branch: 'Axe of Dawn', req: 'rg_axe2', name: 'Sunrise Cleave (capstone)', desc: 'Melee +25%, an even wider arc, and crits hit 40% harder.', mods: { meleeMul: 0.25, arc: 0.2, critDmg: 0.4 } },
    { tier: 3, id: 'rg_host3', branch: 'Shield-host', req: 'rg_host2', name: 'Rune Colossus (capstone)', desc: 'Summon tier IV: +60% HP and damage, +8 s, summons 25% sooner.', mods: { summonMul: 0.6, summonLife: 8, summonTier: 1, summonCd: 0.25 } },
  ],
  seer: [
    { tier: 1, id: 'se_runes', branch: 'Runes', name: 'Wider Circle', desc: 'Rune Trap radius +35%, +20% damage.', mods: { trapRadius: 0.35, spellMul: 0.2 } },
    { tier: 1, id: 'se_sigil', branch: 'Sigil-walking', name: 'Long Step', desc: 'Dodge roll goes 25% farther, +0.1 s i-frames.', mods: { rollSpeed: 0.25, rollIframes: 0.1 } },
    { tier: 1, id: 'se_sight', branch: 'Foresight', name: 'Keen Eye', desc: '+8% critical hit chance.', mods: { crit: 0.08 } },
    { tier: 2, id: 'se_runes2', branch: 'Runes', req: 'se_runes', name: 'Deep Glyphs', desc: 'Rune Trap +25% damage, spell cooldowns 15% shorter.', mods: { spellMul: 0.25, spellCd: 0.15 } },
    { tier: 2, id: 'se_sigil2', branch: 'Sigil-walking', req: 'se_sigil', name: 'Quickstep', desc: 'Dodge 15% farther, stamina refills 30% faster.', mods: { rollSpeed: 0.15, stRegen: 0.3 } },
    { tier: 2, id: 'se_sight2', branch: 'Foresight', req: 'se_sight', name: 'Rune-wisp II', desc: 'Summon tier II: +40% HP and damage, +5 s, a starry glow; +4% crit.', mods: { summonMul: 0.4, summonLife: 5, summonTier: 1, crit: 0.04 } },
    { tier: 3, id: 'se_runes3', branch: 'Runes', req: 'se_runes2', name: 'Great Sigil (capstone)', desc: 'Rune Trap radius +40%, +30% spell damage.', mods: { trapRadius: 0.4, spellMul: 0.3 } },
    { tier: 3, id: 'se_sigil3', branch: 'Sigil-walking', req: 'se_sigil2', name: 'Between Steps (capstone)', desc: 'Dodge +0.15 s i-frames, +25 stamina, refills 30% faster.', mods: { rollIframes: 0.15, stAdd: 25, stRegen: 0.3 } },
    { tier: 3, id: 'se_sight3', branch: 'Foresight', req: 'se_sight2', name: 'Fate-reader (capstone)', desc: 'Summon tier III (+50% HP and damage, +6 s, radiant star-lit form), +6% crit, crits hit 40% harder.', mods: { summonMul: 0.5, summonLife: 6, summonTier: 1, crit: 0.06, critDmg: 0.4 } },
  ],
  stormborn: [
    { tier: 1, id: 'sb_hand', branch: 'Thunderhand', name: 'Charged Hammer', desc: 'Melee +20% damage.', mods: { meleeMul: 0.2 } },
    { tier: 1, id: 'sb_tempest', branch: 'Tempest', name: 'Forked Bolt', desc: 'Chain Lightning leaps to 1 more foe.', mods: { chainJumps: 1 } },
    { tier: 1, id: 'sb_herd', branch: 'Skyherd', name: 'Storm Sprite II', desc: 'Summon +40% HP and damage, +5 s.', mods: { summonMul: 0.4, summonLife: 5 } },
    { tier: 2, id: 'sb_hand2', branch: 'Thunderhand', req: 'sb_hand', name: 'Thunderclap', desc: 'Melee +20% damage, +20 stamina.', mods: { meleeMul: 0.2, stAdd: 20 } },
    { tier: 2, id: 'sb_tempest2', branch: 'Tempest', req: 'sb_tempest', name: 'Gale Bolt', desc: 'Chain Lightning +30% damage, spell cooldowns 15% shorter.', mods: { spellMul: 0.3, spellCd: 0.15 } },
    { tier: 2, id: 'sb_herd2', branch: 'Skyherd', req: 'sb_herd', name: 'Storm Sprite III', desc: 'Summon tier III: +40% HP and damage, +5 s, a radiant storm-lit form.', mods: { summonMul: 0.4, summonLife: 5, summonTier: 1 } },
    { tier: 3, id: 'sb_hand3', branch: 'Thunderhand', req: 'sb_hand2', name: 'Hammer of Skies (capstone)', desc: 'Melee +30%, a wider arc, crits hit 40% harder.', mods: { meleeMul: 0.3, arc: 0.2, critDmg: 0.4 } },
    { tier: 3, id: 'sb_tempest3', branch: 'Tempest', req: 'sb_tempest2', name: 'Eye of the Storm (capstone)', desc: 'Chain Lightning leaps to 2 more foes, +25% spell damage.', mods: { chainJumps: 2, spellMul: 0.25 } },
    { tier: 3, id: 'sb_herd3', branch: 'Skyherd', req: 'sb_herd2', name: 'Thunderhead (capstone)', desc: 'Summon tier IV: +60% HP and damage, +8 s, summons 25% sooner.', mods: { summonMul: 0.6, summonLife: 8, summonTier: 1, summonCd: 0.25 } },
  ],
  grovekeeper: [
    { tier: 1, id: 'gk_bloom', branch: 'Bloom', name: 'Lush Bloom', desc: 'Healing +35%.', mods: { healMul: 0.35 } },
    { tier: 1, id: 'gk_thorn', branch: 'Thorn and Spore', name: 'Thorn Ring', desc: 'Bloom hits twice as hard.', mods: { spellMul: 1.0 } },
    { tier: 1, id: 'gk_kin', branch: 'Grove Kin', name: 'Sapling II', desc: 'Summon +40% HP and damage, +5 s.', mods: { summonMul: 0.4, summonLife: 5 } },
    { tier: 2, id: 'gk_bloom2', branch: 'Bloom', req: 'gk_bloom', name: 'Sap Mending', desc: 'Healing +25% more, 1 HP/s regen out of combat.', mods: { healMul: 0.25, regen: 1 } },
    { tier: 2, id: 'gk_thorn2', branch: 'Thorn and Spore', req: 'gk_thorn', name: 'Bramble Burst', desc: 'Bloom +30% damage, spell cooldowns 15% shorter.', mods: { spellMul: 0.3, spellCd: 0.15 } },
    { tier: 2, id: 'gk_kin2', branch: 'Grove Kin', req: 'gk_kin', name: 'Sapling III', desc: 'Summon tier III: +40% HP and damage, +5 s, a radiant blossom form.', mods: { summonMul: 0.4, summonLife: 5, summonTier: 1 } },
    { tier: 3, id: 'gk_bloom3', branch: 'Bloom', req: 'gk_bloom2', name: 'Evergreen (capstone)', desc: '+40 HP, healing +40%, regen 2 HP/s out of combat.', mods: { hpAdd: 40, healMul: 0.4, regen: 2 } },
    { tier: 3, id: 'gk_thorn3', branch: 'Thorn and Spore', req: 'gk_thorn2', name: 'Thornheart (capstone)', desc: 'Spells +40% damage, crits hit 30% harder.', mods: { spellMul: 0.4, critDmg: 0.3 } },
    { tier: 3, id: 'gk_kin3', branch: 'Grove Kin', req: 'gk_kin2', name: 'Elder Treant (capstone)', desc: 'Summon tier IV: +60% HP and damage, +8 s, summons 25% sooner.', mods: { summonMul: 0.6, summonLife: 8, summonTier: 1, summonCd: 0.25 } },
  ],
  cinderknight: [
    { tier: 1, id: 'ck_blade', branch: 'Ember Blade', name: 'Hot Edge', desc: 'Ember Slash +30% damage.', mods: { spellMul: 0.3 } },
    { tier: 1, id: 'ck_ash', branch: 'Ashen Shadow', name: 'Life Drain', desc: 'Melee hits heal you for 10% of the damage.', mods: { drain: 0.1 } },
    { tier: 1, id: 'ck_legion', branch: 'Ash Legion', name: 'Ember Imp II', desc: 'Summon +40% HP and damage, +5 s.', mods: { summonMul: 0.4, summonLife: 5 } },
    { tier: 2, id: 'ck_blade2', branch: 'Ember Blade', req: 'ck_blade', name: 'White-hot Edge', desc: 'Ember Slash +30% damage, melee +10%.', mods: { spellMul: 0.3, meleeMul: 0.1 } },
    { tier: 2, id: 'ck_ash2', branch: 'Ashen Shadow', req: 'ck_ash', name: 'Ash Veil', desc: 'Life drain 15% total, dodge +0.08 s i-frames.', mods: { drain: 0.05, rollIframes: 0.08 } },
    { tier: 2, id: 'ck_legion2', branch: 'Ash Legion', req: 'ck_legion', name: 'Ember Imp III', desc: 'Summon tier III: +40% HP and damage, +5 s, a radiant cinder form.', mods: { summonMul: 0.4, summonLife: 5, summonTier: 1 } },
    { tier: 3, id: 'ck_blade3', branch: 'Ember Blade', req: 'ck_blade2', name: 'Sunforged (capstone)', desc: 'Spells +30%, spell cooldowns 20% shorter, crits hit 30% harder.', mods: { spellMul: 0.3, spellCd: 0.2, critDmg: 0.3 } },
    { tier: 3, id: 'ck_ash3', branch: 'Ashen Shadow', req: 'ck_ash2', name: 'Cinder Wraithblade (capstone)', desc: 'Life drain 25% total, melee +20%.', mods: { drain: 0.1, meleeMul: 0.2 } },
    { tier: 3, id: 'ck_legion3', branch: 'Ash Legion', req: 'ck_legion2', name: 'Ash Legion Lord (capstone)', desc: 'Summon tier IV: +60% HP and damage, +8 s, summons 25% sooner.', mods: { summonMul: 0.6, summonLife: 8, summonTier: 1, summonCd: 0.25 } },
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
// why a node can't be learned right now ('' = it can): learned / needs the tier below / level gate / points
export function lockOf(S, node) {
  if (!node) return 'unknown';
  if (S.skills[node.id]) return 'learned';
  const T = TIER[node.tier || 1];
  if (node.req && !S.skills[node.req]) return `needs ${(TREES[S.cls] || []).find((n) => n.id === node.req)?.name || 'the tier below'}`;
  if ((S.lv || 1) < T.lv) return `Lv ${T.lv}`;
  if ((S.sp || 0) < T.cost) return `${T.cost} point${T.cost > 1 ? 's' : ''}`;
  return '';
}
export function learn(S, nodeId) {
  const node = (TREES[S.cls] || []).find((n) => n.id === nodeId);
  if (!node || lockOf(S, node)) return false;
  S.skills[nodeId] = 1; S.sp -= TIER[node.tier || 1].cost; return true;
}
// summon tier from the summon branch: I (base) .. IV (capstone); each tier-I/II/III summon node adds one
export function summonTier(S) {
  let t = 1;
  for (const n of TREES[S.cls] || []) if (S.skills[n.id] && n.mods.summonMul) t++;
  return Math.min(4, t);
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
    spellCd: 0, critDmg: 0, stRegen: 0, summonCd: 0, summonTier: 0,
  };
  for (const node of TREES[S.cls] || []) {
    if (!S.skills[node.id]) continue;
    for (const [k, v] of Object.entries(node.mods)) {
      if (k === 'guardSt') m.guardSt = Math.max(0.3, m.guardSt + v);
      else if (k === 'guardMul') m.guardMul = Math.max(0.45, m.guardMul + v);
      else if (k === 'trapRadius' || k === 'rollSpeed') m[k] += v;
      else if (k.endsWith('Mul')) m[k] += v;
      else m[k] = (m[k] || 0) + v;
    }
  }
  return gearMods(S, m);
}
