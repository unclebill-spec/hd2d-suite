// Hearthmoor loot (stage 2): five rarities, pixel loot beams, gold, a bag + three equipment slots.
// Drops are crisp DOM pixel canvases pinned to the world (like the damage numbers): a beam column in the
// rarity colour, Epic adds a faint stepped glow, Legendary an animated neon aura. No blur, no bloom.
// gear14 (2026-11-03, Will: "the 14 slots and the 5 rarities, keep Hearthmoor's simpler stats"): the game-shell template's
// 5 tiers (STATS.md 4.2 names / colours / drop table). Stat muls keep the live (6299ce7) values for the 4 shared tiers
// (Common 1, Rare 1.9, Epic 2.6, Legendary 3.5) so, with GEAR_NORM, a full 14-piece kit matches the old 3-piece kit of the same tier;
// Runeforged 4.4 sits one step above Legendary (~ +26%, the same ratio as Epic -> Legendary). w = drop weights [normal, elite (rares, rifts), boss] from the template table.
export const RARITY = [
  { id: 'common', name: 'Common', col: '#fff8e6', lo: '#c4a984', w: [80, 40, 0], mul: 1, scrap: 2 },
  { id: 'rare', name: 'Rare', col: '#2ab4ff', lo: '#1c62d8', w: [17, 45, 38], mul: 1.9, scrap: 8 },
  { id: 'epic', name: 'Epic', col: '#b46cff', lo: '#6a34b8', w: [3, 13, 40], mul: 2.6, scrap: 16 },
  { id: 'legendary', name: 'Legendary', col: '#ffc85a', lo: '#b07a2a', w: [0, 2, 18], mul: 3.5, scrap: 32 },
  { id: 'runeforged', name: 'Runeforged', col: '#ff2bd6', lo: '#b82a8c', hi: '#ffb4ea', w: [0, 0.2, 4], mul: 4.4, scrap: 48 },
];
export const R_RARE = 1, R_EPIC = 2, R_LEG = 3, R_RUNE = 4;
// the template's 14 slots (STATS.md 4.3); W = its slot weight, used only as a multiplier on the item's stat roll
export const SLOTS = ['helm', 'neck', 'chest', 'legs', 'feet', 'arms', 'gloves', 'ringL', 'ringR', 'belt', 'cloak', 'primary', 'secondary', 'ranged'];
export const SLOT_W = { helm: 0.8, neck: 0.6, chest: 1.0, legs: 0.9, feet: 0.6, arms: 0.6, gloves: 0.6, ringL: 0.5, ringR: 0.5, belt: 0.5, cloak: 0.6, primary: 1.0, secondary: 0.8, ranged: 0.6 };
// gear14 power normalisation: the live 3-slot kit (weapon + armor + trinket) rolled each piece at weight 1 (sum 3, ~2 mods each);
// every new slot also rolls ~2 mods, so a full 14-piece kit would carry sum(SLOT_W) = 9.6 "old pieces" of stats (3.2x).
// GEAR_NORM = 3 / sum(SLOT_W) = 3 / 9.6 = 0.3125 scales every roll so a full kit totals ~ the old kit; slot weights keep their relative shape.
// uniques (asgard / vanaheim literals) set their own mods and are not scaled.
export const GEAR_NORM = 3 / SLOTS.reduce((a, sl) => a + SLOT_W[sl], 0);
export const SLOT_LABEL = { helm: 'helm', neck: 'neck', chest: 'chest', legs: 'legs', feet: 'feet', arms: 'arms', gloves: 'gloves', ringL: 'ring (left)', ringR: 'ring (right)', belt: 'belt', cloak: 'cloak', primary: 'main hand', secondary: 'off-hand', ranged: 'ranged / charm' };
const DROP_SLOTS = SLOTS.filter((s) => s !== 'ringR');   // rings roll once (as ringL) and equip into the free / weaker ring slot
export const ringSlot = (sl) => sl === 'ringL' || sl === 'ringR';
// gearfx: armor type only restricts wearing and biases which optional mod is picked. The rolled numbers do not change by type.
// Order is the wear hierarchy: plate wears all, chain wears chain/leather/cloth, leather wears leather/cloth, cloth wears cloth.
export const ARMOR_TYPES = ['plate', 'chain', 'leather', 'cloth'];
export const CLASS_ARMOR = { runeguard: 'plate', cinderknight: 'plate', stormborn: 'chain', grovekeeper: 'chain', wildcaller: 'leather', seer: 'cloth' };
const ARMOR_SLOTS = ['helm', 'chest', 'legs', 'feet', 'arms', 'gloves', 'belt', 'cloak'];
const WEAPON_SLOTS = ['primary', 'secondary', 'ranged'];
const ARMOR_W = { plate: 7, chain: 8, leather: 11, cloth: 16 };   // gearfx: how often each type's name shows up on the armor bases
const BIAS = { plate: ['hpAdd', 'guardMul', 'runePct'], chain: ['hpAdd', 'guardMul', 'runePct'], leather: ['crit', 'avoid', 'haste'], cloth: ['spellMul', 'healMul', 'shieldPct'] };
const BIAS_W = 3;   // gearfx: a favoured optional stat is 3x as likely; its value is the same as any other roll
export function canWear(cls, it) {
  if (!it || !it.at) return true;
  const own = CLASS_ARMOR[cls]; if (!own) return false;
  return ARMOR_TYPES.indexOf(it.at) >= ARMOR_TYPES.indexOf(own);
}
// gearfx: enemy D.element -> school. Missing (and anything unlisted) is physical. Mana does not exist; stamina is the only resource.
const SCHOOL_MAP = { fire: 'fire', ice: 'water', cold: 'water', water: 'water', light: 'light', lightning: 'light', dark: 'dark' };
export const SCHOOL_OF = (element) => SCHOOL_MAP[element] || 'physical';
// gearfx: resist reduction is min(60%, R/(R+K)), K = 50 + 10*foeLevel (enemy level, else the player's). Avoid 25% (spells/bolts use half).
// Move +25% total; feet clamp at +10% and cloaks at +5% when the mod is rolled. Haste +50%. Block chance 50%, a block soaks 50%.
// runePct and shieldPct cap at 20%. A hit that connects always deals at least 1.
export const CAPS = {
  res: 0.6, resK: (foeLv, playerLv) => 50 + 10 * (foeLv == null ? (playerLv || 1) : foeLv),
  avoid: 0.25, avoidSpell: 0.5, move: 0.25, moveFeet: 0.1, moveCloak: 0.05,
  haste: 0.5, block: 0.5, blockSoak: 0.5, runePct: 0.2, shieldPct: 0.2, minHit: 1,
};
// gearfx: on-hit chance = min(ch + crit*0.25, ch*2, 0.35). One proc per landed hit, each id keeps its own ICD, procs never trigger procs.
// Common/Rare: none. Epic: 30% of one. Legendary: one. Runeforged: one + 35% of a second, distinct. Primary, secondary and ranged only.
export const PROCS = {
  lifeSteal: { school: 'dark', ch: .15, icd: 1, healPct: .15 },
  fireBolt: { school: 'fire', ch: .10, icd: 3, base: 8, perLv: 3 },
  freeze: { school: 'water', ch: .06, icd: 8, dur: 1, eliteDur: .5, bossSlow: .4, bossDur: 1.5, per: 'target' },
  root: { school: 'water', ch: .08, icd: 8, dur: 2, boss: 'immune', per: 'target' },
  heal: { school: 'light', ch: .10, icd: 4, healPct: .04 },
  damageShield: { school: 'fire', ch: .08, icd: 12, dur: 5, reflect: .2 },
  runeShield: { school: 'light', ch: .06, icd: 15, absorb: .08, dur: 6 },
};
const PROC_LABEL = { lifeSteal: 'life steal', fireBolt: 'fire bolt', freeze: 'freeze', root: 'root', heal: 'heal proc', damageShield: 'damage shield', runeShield: 'rune shield' };
const procName = (id) => { const w = PROC_LABEL[id] || id; return w.charAt(0).toUpperCase() + w.slice(1); };   // gearfx: "Fire bolt"
// ---- save migration (old 3-slot / 5-rarity gear -> 14 slots / template tiers). Each item gets rv: 2 so it is never mapped twice.
// rarity: common -> common, uncommon -> common, rare -> rare, epic -> epic, legendary -> legendary (never downgrades rare+)
const OLD_RAR = [0, 0, 1, 2, 3], OLD_SLOT = { weapon: 'primary', armor: 'chest', trinket: 'neck' };
// balance (Game Director, 2026-11-03): migrated mods are rescaled to the new per-piece norm so an old piece sits in line with a
// fresh drop of the same slot / rarity / level: x (new rarity mul / old rarity mul) x SLOT_W[new slot] x GEAR_NORM.
// Old pieces rolled at slot weight 1 with the old muls below. Uniques (it.fixed / it.unique) keep their literal values.
// Gems, sockets, temper (it.up), rerolls (it.rr), names untouched; rv: 2 marks the item so it is never rescaled twice.
const OLD_MUL = [1, 1.4, 1.9, 2.6, 3.5];
export function migrateItem(it) {
  if (!it || typeof it !== 'object' || it.rv === 3) return it;
  if (it.rv !== 2) {   // gearfx: rv < 2 keeps the gear14 map + rescale exactly, and still lands on rv 2 before the fx step
    const oldR = typeof it.rar === 'number' ? Math.max(0, Math.min(4, it.rar)) : null;
    if (oldR !== null) it.rar = OLD_RAR[oldR];
    if (OLD_SLOT[it.slot]) it.slot = OLD_SLOT[it.slot];
    if (!it.fixed && !it.unique && oldR !== null && SLOT_W[it.slot] && it.mods && typeof it.mods === 'object') {
      // base factor, then a uniform trim so the piece's score equals a fresh drop's expected score (old weapons lacked the
      // Epic+ crit-dmg roll, old trinkets rolled stamina where necks roll crit dmg / melee / spells)
      const f0 = (RARITY[it.rar].mul / OLD_MUL[oldR]) * SLOT_W[it.slot] * GEAR_NORM, raw = {};
      for (const [key, v] of Object.entries(it.mods)) if (typeof v === 'number') raw[key] = v * f0;
      const have = Object.entries(raw).reduce((a, [key, v]) => a + (SCORE[key] ?? 0.5) * v, 0), want = freshScore(it.slot, it.rar, it.lv || 1);
      const g = have > 0 && want > 0 ? want / have : 1;
      for (const [key, v] of Object.entries(raw)) it.mods[key] = ['hpAdd', 'stAdd'].includes(key) ? (v ? Math.sign(v) * Math.max(1, Math.round(Math.abs(v) * g)) : 0) : +(v * g).toFixed(3);
      // integer HP / stamina rounding (min 1) can swing a tiny low-level piece by 20%+: put the leftover on its largest % mod
      const fl = Object.keys(raw).filter((key) => !['hpAdd', 'stAdd'].includes(key) && SCORE[key]).sort((a, b) => Math.abs(SCORE[b] * raw[b]) - Math.abs(SCORE[a] * raw[a]))[0];
      if (fl && want > 0) { const now = Object.entries(it.mods).reduce((a, [key, v]) => a + (key in raw ? (SCORE[key] ?? 0.5) * v : 0), 0), nv = it.mods[fl] + (want - now) / SCORE[fl];
        if (Math.sign(nv) === Math.sign(it.mods[fl])) it.mods[fl] = +nv.toFixed(4); }
    }
    it.rv = 2;
  }
  return migrateItemFx(it);   // gearfx: rv 2 -> rv 3, no second rescale
}
// gearfx: an rv 2 piece (already on the 14-slot scale) gains it.at from its base name and procs []. No new mods, never rescaled. Idempotent.
const PLATE_BITS = ['Rune Helm', 'Rune Coat', 'Rune Sabatons', 'Rune Gauntlets', 'Rune Armbands', 'Rune Leggings', 'Rune Sash'];
const CHAIN_BITS = ['Moss Mail', 'Moss Greaves', 'Fjord Hauberk', 'Moss', 'Smiths', 'Forge'];
const LEATHER_BITS = ['Leather', 'Bog', 'Fur', 'Herders', 'Pouch', 'Raven'];
const CLOTH_BITS = ['Wool', 'Felt', 'Knit', 'Lantern', 'Hearth', 'Bakers', 'Gardeners', 'Braided', 'Rope'];
function armorTypeOf(name) {
  const n = name || '';
  if (PLATE_BITS.some((p) => n.includes(p))) return 'plate';
  if (CHAIN_BITS.some((p) => n.includes(p))) return 'chain';
  if (LEATHER_BITS.some((p) => n.includes(p))) return 'leather';
  if (CLOTH_BITS.some((p) => n.includes(p))) return 'cloth';
  return 'cloth';
}
export function migrateItemFx(it) {
  if (!it || typeof it !== 'object' || it.rv !== 2) return it;
  if (ARMOR_SLOTS.includes(it.slot) && !it.at) it.at = armorTypeOf(it.name);
  if (!Array.isArray(it.procs)) it.procs = [];
  it.rv = 3; return it;
}
export function migrateGear(S) {   // bag + equipped (the bank's vault maps its items via migrateItem on read); gems, sockets (it.gems), temper (it.up) and rerolls (it.rr) are kept as-is
  if (!S || typeof S !== 'object') return S;
  if (Array.isArray(S.bag)) S.bag.forEach(migrateItem);
  const g = S.gear && typeof S.gear === 'object' ? S.gear : {}, out = Object.fromEntries(SLOTS.map((sl) => [sl, null]));
  for (const [k, it] of Object.entries(g)) {
    if (!it) continue; migrateItem(it);
    let to = OLD_SLOT[k] || k; if (ringSlot(to) && out[to]) to = to === 'ringL' ? 'ringR' : 'ringL';
    if (!SLOTS.includes(to) || out[to]) { (S.bag = S.bag || []).push(it); continue; }
    if (ringSlot(it.slot)) it.slot = to;
    out[to] = it;
  }
  S.gear = out; return S;
}
// socket gems (stage 3): golem cores and rift shards are the high-tier ones; each glows in its colour on the item icon
export const GEMS = {
  golem_core: { name: 'Golem core', col: '#f2a63a', lo: '#c4502c', mods: { hpAdd: 15, guardMul: -0.03 }, price: 150, about: '+15 HP · guard -3% dmg' },
  rift_shard: { name: 'Rift shard', col: '#b07ce0', lo: '#6a3e9a', mods: { spellMul: 0.06, crit: 0.01 }, price: 120, about: '+6% spells · +1% crit' },
  frost_core: { name: 'Frost core', col: '#94c0dc', lo: '#3e5a8c', mods: { stAdd: 12 }, price: 70, about: '+12 stamina' },
  moon_opal: { name: 'Moon opal', col: '#fff8e6', lo: '#c4a984', mods: { summonMul: 0.08 }, price: 90, about: '+8% summons' },
};
export const GEM_IDS = Object.keys(GEMS);
// Rare: 0-2 sockets (mostly 0-1), Epic: 0-2 (mostly 1-2), Legendary: always 2, Runeforged: 2-3 (mostly 3)
export function rollSockets(rar, rnd = Math.random) {
  if (rar >= R_RUNE) return 2 + pickW(rnd, [30, 70]); if (rar === R_LEG) return 2; if (rar === R_EPIC) return pickW(rnd, [25, 45, 30]); if (rar === R_RARE) return pickW(rnd, [55, 35, 10]); return 0;
}
export function socketGem(S, it, gem) {
  if (!it || !GEMS[gem] || !((S.gems || {})[gem] > 0)) return false;
  const k = (it.gems || []).indexOf(null); if (k < 0) return false;
  it.gems[k] = gem; S.gems[gem] -= 1; if (!S.gems[gem]) delete S.gems[gem];
  return true;
}
export const BAG_MAX = 30;
const INK = '#2a1e1c';
const BASES = {
  helm: ['Wool Hood', 'Moss Cap', 'Rune Helm', 'Hearth Coif', 'Raven Helm', 'Birch Circlet'],
  neck: ['Moon Locket', 'Acorn Charm', 'Toadstool Brooch', 'Amber Torc', 'Rune Pendant', 'Hearth Ember'],
  chest: ['Wool Tunic', 'Leather Jerkin', 'Moss Mail', 'Rune Coat', 'Bakers Apron', 'Fjord Hauberk'],
  legs: ['Wool Breeks', 'Leather Trews', 'Moss Greaves', 'Rune Leggings', 'Herders Breeches'],
  feet: ['Felt Boots', 'Bog Walkers', 'Fur Boots', 'Rune Sabatons', 'Hearth Slippers'],
  arms: ['Braided Bracers', 'Leather Vambraces', 'Rune Armbands', 'Moss Wraps', 'Smiths Sleeves'],
  gloves: ['Knit Mittens', 'Leather Gloves', 'Rune Gauntlets', 'Gardeners Gloves', 'Forge Grips'],
  ringL: ['Glow Ring', 'Birch Band', 'Rune Ring', 'Amber Loop', 'Moonstone Ring', 'Oath Ring'],
  belt: ['Rope Belt', 'Leather Girdle', 'Rune Sash', 'Pouch Belt', 'Hearth Cord'],
  cloak: ['Lantern Cloak', 'Wool Mantle', 'Raven Cape', 'Moss Shawl', 'Fjord Cloak'],
  primary: ['Iron Sword', 'Hearth Staff', 'Ember Blade', 'Rune Hammer', 'Oak Wand', 'Bearded Axe'],
  secondary: ['Oak Buckler', 'Linden Shield', 'Rune Tome', 'Glow Orb', 'Seax Knife', 'Ember Lantern'],
  ranged: ['Willow Bow', 'Firefly Jar', 'Yew Longbow', 'Rune Sling', 'Feather Charm', 'Elk Horn Charm'],
};
BASES.ringR = BASES.ringL;
const PREFIX = [['Plain', 'Worn', 'Sturdy'], ['Gleaming', 'Runed', 'Moonlit'], ['Starlit', 'Spellwoven', 'Twilight'], ['Sunfire', 'Elderglow', 'Rainbow'], ['Runeforged', 'Allfather\'s', 'Rift-sung']];
// per-slot stat rolls (Hearthmoor's own mods; picked to fit the template's "can roll" column). fix = always, opt = one of.
// base values are the old weapon / armor / trinket rolls; each is x rarity mul x level x SLOT_W[slot].
const HP = ['hpAdd', 8], ST = ['stAdd', 4], MEL = ['meleeMul', 0.04], SPL = ['spellMul', 0.04], CRIT = ['crit', 0.01], CDMG = ['critDmg', 0.05],
  GRD = ['guardMul', -0.015], HEAL = ['healMul', 0.04], SUM = ['summonMul', 0.05], CD = ['spellCd', 0.015], STR = ['stRegen', 0.04], ROLL = ['rollSpeed', 0.04];
// gearfx: new keys join the opt pools (one optional roll, same affix count). RES picks one school or resAll. Block is shield bases only, added in makeItem.
const RES_OPTS = [['resFire', 6], ['resWater', 6], ['resLight', 6], ['resDark', 6], ['resAll', 3]];
const RES = ['res', 0], AVD = ['avoid', 0.01], MOV = ['move', 0.015], HST = ['haste', 0.015], BLK = ['block', 0.03];
const INT_MOD = new Set(['hpAdd', 'stAdd', 'resFire', 'resWater', 'resLight', 'resDark', 'resAll']);
// gearfx: runePct / shieldPct are absolute percents, not scaled by GEAR_NORM (or by level / slot / rarity).
const ADV = { [R_EPIC]: { p: 0.25, lo: 1, hi: 2, n: 1 }, [R_LEG]: { p: 1, lo: 2, hi: 4, n: 1 }, [R_RUNE]: { p: 1, lo: 3, hi: 6, n: 2 } };
export const ROLLS = {
  helm: { fix: [HP], opt: [SPL, HEAL, RES] },                 // VIT, INT, SPI, max HP, a resist
  neck: { fix: [CRIT], opt: [CDMG, MEL, SPL, RES], epic: SUM },   // any primary, crit, crit dmg, a resist
  chest: { fix: [HP], opt: [GRD, RES] },                      // max HP + guard or a resist (still two mods; the old armor had both fixed)
  legs: { fix: [HP], opt: [ST, MEL, SPL] },                   // VIT, STR, DEX, AGI, INT, max HP
  feet: { fix: [ST], opt: [ROLL, STR, AVD, MOV] },            // AGI, DEX, VIT, avoid or move
  arms: { fix: [MEL], opt: [SPL, CD, HST] },                  // STR, DEX, INT, haste
  gloves: { fix: [CRIT], opt: [MEL, SPL, CD, HST] },          // STR, DEX, INT, crit, haste
  ringL: { fix: [CRIT], opt: [CDMG, ST, MEL, SPL, RES, AVD] }, // any primary, crit, crit dmg, stamina, avoid, a resist
  belt: { fix: [HP, ST], opt: [] },                           // VIT, STR, max HP, max stamina
  cloak: { fix: [STR], opt: [GRD, HEAL, ROLL, RES, AVD, MOV] }, // AGI, SPI, avoid or move, a resist
  primary: { fix: [MEL, SPL], opt: [], epic: CDMG },          // weapon damage, crit dmg (the old weapon roll)
  secondary: { fix: [GRD], opt: [HP, SPL, HEAL] },            // shield VIT / tome-orb INT, SPI; Buckler/Shield also roll block
  ranged: { fix: [CRIT], opt: [CDMG, SUM, ST, RES], epic: SUM },  // bow DEX, crit / charm, a resist
};
ROLLS.ringR = ROLLS.ringL;
// 8x8 icons (1 = rarity colour, 2 = light, 3 = dark); old ids weapon / armor / trinket kept for any stray caller
const ICONS = {
  primary: ['......2.', '.....21.', '....21..', '...21...', '.321....', '..33....', '.3..3...', '........'],
  chest: ['.11..11.', '.111111.', '..1221..', '..1111..', '..1111..', '..1331..', '..1..1..', '........'],
  neck: ['...33...', '..3..3..', '...11...', '..1221..', '.112211.', '..1111..', '...11...', '........'],
  helm: ['........', '..1111..', '.112211.', '.111111.', '.1.33.1.', '.1....1.', '........', '........'],
  legs: ['..1111..', '..1111..', '..1..1..', '..1..1..', '..1..1..', '..2..2..', '.33..33.', '........'],
  feet: ['........', '..11....', '..11....', '..11....', '..1211..', '..11111.', '..33333.', '........'],
  arms: ['........', '.111....', '.1211...', '..1111..', '...1211.', '....111.', '........', '........'],
  gloves: ['..1.1...', '.11111..', '.12111.1', '.111111.', '.11111..', '..333...', '..333...', '........'],
  ringL: ['........', '...22...', '..3113..', '.1....1.', '.1....1.', '..1..1..', '...11...', '........'],
  belt: ['........', '........', '11111111', '1112.111', '11133111', '........', '........', '........'],
  cloak: ['...33...', '..1111..', '.112211.', '.111111.', '1111111.', '11111111', '1.1.1.11', '........'],
  secondary: ['.111111.', '.122221.', '.121121.', '.121121.', '..1221..', '..1111..', '...11...', '........'],
  ranged: ['..1.....', '.1.2....', '.1..2...', '1...2333', '.1..2...', '.1.2....', '..1.....', '........'],
  gold: ['........', '..1111..', '.112211.', '.121111.', '.111111.', '.111131.', '..1111..', '........'],
};
ICONS.ringR = ICONS.ringL; ICONS.weapon = ICONS.primary; ICONS.armor = ICONS.chest; ICONS.trinket = ICONS.neck;

let uidN = 0;
const pickW = (rnd, ws) => { let t = ws.reduce((a, b) => a + b, 0) * rnd(); for (let i = 0; i < ws.length; i++) { t -= ws[i]; if (t <= 0) return i; } return 0; };
export function ensure(S) {
  if (!Array.isArray(S.bag)) S.bag = [];
  if (!S.gear || typeof S.gear !== 'object') S.gear = {};
  if (Object.keys(S.gear).some((k) => !SLOTS.includes(k)) || S.bag.some((it) => it && it.rv !== 3) || Object.values(S.gear).some((it) => it && it.rv !== 3)) migrateGear(S);   // gearfx: rv 2 still needs the fx step
  for (const sl of SLOTS) if (!(sl in S.gear)) S.gear[sl] = null;
  if (typeof S.gold !== 'number') S.gold = (S.inv && S.inv.coin) || 0;
  if (!S.gems || typeof S.gems !== 'object') S.gems = {};
  return S;
}
// col: 0 = normal foes, 1 = elite (rares, rift rewards), 2 = boss (template drop table); luck (Hero mode) = +25% per tier above common
export const rarityWeights = (col = 0, luck = 0, minRar = 0) => RARITY.map((x, i) => (i < minRar ? 0 : x.w[col] * (luck && i >= 1 ? 1.25 : 1)));
export function rollRarity(col = 0, luck = 0, minRar = 0, rnd = Math.random) {
  const ws = rarityWeights(col, luck, minRar);
  return ws.some((w) => w > 0) ? pickW(rnd, ws) : Math.min(R_RUNE, minRar);
}
const biasW = (at, key) => (at && BIAS[at] && BIAS[at].includes(key) ? BIAS_W : 1);
function scaledMod(key, base, k, sl) {   // gearfx: same rounding makeItem and freshScore share. move clamps per slot at roll time.
  if (INT_MOD.has(key)) return Math.max(1, Math.round(base * k));
  if (key === 'move') { const cap = sl === 'feet' ? CAPS.moveFeet : sl === 'cloak' ? CAPS.moveCloak : CAPS.move; return Math.min(cap, +(base * k).toFixed(3)); }
  return +(base * k).toFixed(3);
}
function rollType(cls, rnd) {   // gearfx: 70% the class's own type when cls is passed; otherwise (and the other 30%) weighted by ARMOR_W
  const own = cls && CLASS_ARMOR[cls];
  if (own && rnd() < 0.7) return own;
  const pool = own ? ARMOR_TYPES.filter((t) => t !== own) : ARMOR_TYPES;
  return pool[pickW(rnd, pool.map((t) => ARMOR_W[t]))];
}
function rollAdv(r, at, rnd) {   // gearfx: absolute 1-6%, not multiplied by k / GEAR_NORM. Plate/chain lean runePct, cloth leans shieldPct.
  const A = ADV[r]; if (!A || (A.p < 1 && rnd() >= A.p)) return [];
  const pct = () => Math.min(CAPS.runePct, (A.lo + Math.floor(rnd() * (A.hi - A.lo + 1))) / 100);
  if (A.n === 2) return [['runePct', pct()], ['shieldPct', pct()]];
  const keys = ['runePct', 'shieldPct'];
  return [[keys[pickW(rnd, keys.map((key) => biasW(at, key)))], pct()]];
}
function rollProcs(r, rnd) {
  if (r < R_EPIC) return [];
  const ids = Object.keys(PROCS), pack = (id) => ({ id, ch: PROCS[id].ch, icd: PROCS[id].icd });
  const pick = (ban) => { const pool = ban ? ids.filter((id) => id !== ban) : ids; return pool[Math.floor(rnd() * pool.length)]; };
  if (r === R_EPIC) return rnd() < 0.3 ? [pack(pick())] : [];
  const a = pick(), out = [pack(a)];
  if (r >= R_RUNE && rnd() < 0.35) out.push(pack(pick(a)));
  return out;
}
export function makeItem(lv = 1, rar = null, slot = null, rnd = Math.random, luck = 0, cls = null) {
  const r = rar ?? rollRarity(0, luck, 0, rnd);
  let sl = slot === 'weapon' ? 'primary' : slot === 'armor' ? 'chest' : slot === 'trinket' ? 'neck' : slot || DROP_SLOTS[Math.floor(rnd() * DROP_SLOTS.length)];
  if (!ROLLS[sl]) sl = 'neck';
  const R = RARITY[r], k = R.mul * (1 + (lv - 1) * 0.06) * SLOT_W[sl] * GEAR_NORM;
  const base = BASES[sl][Math.floor(rnd() * BASES[sl].length)], pre = PREFIX[r][Math.floor(rnd() * 3)];
  const at = ARMOR_SLOTS.includes(sl) ? rollType(cls, rnd) : null;
  const mods = {}, Rl = ROLLS[sl];
  const add = (pair) => {
    let [key, baseV] = pair;
    if (key === 'res') { add(RES_OPTS[Math.floor(rnd() * RES_OPTS.length)]); return; }
    if (key in mods) return;
    mods[key] = scaledMod(key, baseV, k, sl);
  };
  Rl.fix.forEach(add);
  let opt = Rl.opt;
  if (sl === 'secondary' && /Buckler|Shield/.test(base)) opt = opt.concat([BLK]);   // gearfx: block is a shield-type secondary only
  if (opt.length) add(opt[pickW(rnd, opt.map((e) => biasW(at, e[0])))]);
  if (Rl.epic && r >= R_EPIC) add(Rl.epic);
  for (const [key, v] of rollAdv(r, at, rnd)) if (!(key in mods)) mods[key] = v;
  const n = rollSockets(r, rnd);
  const it = { uid: `${Date.now().toString(36)}${(uidN++).toString(36)}`, slot: sl, name: `${pre} ${base}`, rar: r, lv, mods, gems: Array(n).fill(null), rv: 3 };
  if (at) it.at = at;
  if (WEAPON_SLOTS.includes(sl)) it.procs = rollProcs(r, rnd);
  return it;
}
// expected score of a fresh classless makeItem(lv, r, sl) (fixed + mean biased opt + epic + mean advanced), no gems / temper / procs
function optScore(opt, at, k, sl, fixKeys) {
  const W = opt.reduce((a, e) => a + biasW(at, e[0]), 0); if (!W) return 0;
  const one = (key, base) => (SCORE[key] ?? 0.5) * scaledMod(key, base, k, sl);
  let t = 0;
  for (const e of opt) {
    const p = biasW(at, e[0]) / W;
    if (e[0] === 'res') t += p * RES_OPTS.reduce((a, x) => a + one(x[0], x[1]), 0) / RES_OPTS.length;
    else if (!fixKeys.has(e[0])) t += p * one(e[0], e[1]);
  }
  return t;
}
function meanOverType(sl, opt, fn) {
  if (!ARMOR_SLOTS.includes(sl)) return fn(null);
  let t = 0, w = 0;
  for (const at of ARMOR_TYPES) { const ww = ARMOR_W[at]; t += ww * fn(at); w += ww; }
  return t / w;
}
function advScore(r) {
  const A = ADV[r]; if (!A) return 0;
  let s = 0, n = 0; for (let p = A.lo; p <= A.hi; p++) { s += p / 100; n++; }
  return A.p * A.n * SCORE.runePct * (s / n);   // gearfx: runePct and shieldPct share a weight, so the bias does not change the expected score
}
function freshScore(sl, r, lv) {
  const Rl = ROLLS[sl]; if (!Rl) return 0; const k = RARITY[r].mul * (1 + (lv - 1) * 0.06) * SLOT_W[sl] * GEAR_NORM;
  const fixKeys = new Set(Rl.fix.map((x) => x[0]));
  let t = Rl.fix.reduce((a, x) => a + (SCORE[x[0]] ?? 0.5) * scaledMod(x[0], x[1], k, sl), 0);
  const lists = sl === 'secondary'
    ? [[BASES.secondary.filter((b) => /Buckler|Shield/.test(b)).length / BASES.secondary.length, Rl.opt.concat([BLK])], [0, Rl.opt]]
    : [[1, Rl.opt]];
  lists[1] && (lists[1][0] = 1 - lists[0][0]);
  let pEpic = 0;
  for (const [p, opt] of lists) {
    if (!p || !opt.length) continue;
    t += p * meanOverType(sl, opt, (at) => optScore(opt, at, k, sl, fixKeys));
    if (Rl.epic) pEpic += p * meanOverType(sl, opt, (at) => { const W = opt.reduce((a, e) => a + biasW(at, e[0]), 0); return opt.reduce((a, e) => a + (e[0] === Rl.epic[0] ? biasW(at, e[0]) : 0), 0) / W; });
  }
  if (Rl.epic && r >= R_EPIC && !fixKeys.has(Rl.epic[0])) t += (1 - pEpic) * (SCORE[Rl.epic[0]] ?? 0.5) * scaledMod(Rl.epic[0], Rl.epic[1], k, sl);
  return t + advScore(r);
}
// a rough "how good is this piece" number (compare + the weaker-ring pick); same weights the tooltips show
// gearfx: each new key's base roll scores ~0.036, in line with melee 0.04 / crit 0.03 / a point of the old budget.
// resAll's 3 rating counts as four schools (4 * 3/6 of a single resist). runePct / shieldPct are the absolute percent, so 3% ~= one base roll.
const SCORE = { hpAdd: 0.005, stAdd: 0.008, meleeMul: 1, spellMul: 1, crit: 3, critDmg: 0.6, guardMul: -2, healMul: 0.8, summonMul: 0.8, spellCd: 2, stRegen: 0.5, rollSpeed: 0.5, drain: 3, regen: 0.1, resFire: 0.006, resWater: 0.006, resLight: 0.006, resDark: 0.006, resAll: 0.024, avoid: 3.6, move: 2.4, haste: 2.4, block: 1.2, runePct: 1.2, shieldPct: 1.2 };
export function score(it) {
  if (!it) return 0; const k = 1 + 0.07 * (it.up || 0);
  let t = 0; for (const [key, v] of Object.entries(it.mods || {})) t += (SCORE[key] ?? 0.5) * v * k;
  for (const g of it.gems || []) if (g && GEMS[g]) for (const [key, v] of Object.entries(GEMS[g].mods)) t += (SCORE[key] ?? 0.5) * v;
  return t;
}
// which gear slot a piece goes into: its own, or for a ring the free ring slot, else the weaker ring
export function targetSlot(S, it) {
  if (!it) return null; if (!ringSlot(it.slot)) return it.slot;
  const g = (S && S.gear) || {};
  if (!g.ringL) return 'ringL'; if (!g.ringR) return 'ringR';
  return score(g.ringR) < score(g.ringL) ? 'ringR' : 'ringL';
}
// tooltip compare: "vs <equipped name>: +12% melee, -4 HP" against the same slot (rings: the weaker ring)
const MOD_NAME = { meleeMul: ['% melee', 100], spellMul: ['% spells', 100], hpAdd: [' HP', 1], stAdd: [' stamina', 1], crit: ['% crit', 100], critDmg: ['% crit dmg', 100], guardMul: ['% guard dmg', 100], healMul: ['% healing', 100], summonMul: ['% summons', 100], spellCd: ['% spell cd', -100], stRegen: ['% st regen', 100], rollSpeed: ['% roll', 100], drain: ['% drain', 100], regen: [' HP/s', 1], resFire: [' fire resist', 1], resWater: [' water resist', 1], resLight: [' light resist', 1], resDark: [' dark resist', 1], resAll: [' all resists', 1], avoid: ['% avoid', 100], move: ['% move', 100], haste: ['% haste', 100], block: ['% block', 100], runePct: [' Rune %', 100], shieldPct: [' Spell Shield %', 100] };
const AT_WORD = { plate: 'Plate', chain: 'Chain', leather: 'Leather', cloth: 'Cloth' };   // gearfx: armor type word, first in describe()
export function compare(S, it) {
  const sl = targetSlot(S, it), cur = sl && (S.gear || {})[sl];
  if (!cur || cur === it) return cur === it ? '' : `new for ${SLOT_LABEL[sl]}`;
  const tot = (x) => { const m = {}; const k = 1 + 0.07 * (x.up || 0); for (const [key, v] of Object.entries(x.mods || {})) m[key] = (m[key] || 0) + v * k; for (const g of x.gems || []) if (g && GEMS[g]) for (const [key, v] of Object.entries(GEMS[g].mods)) m[key] = (m[key] || 0) + v; return m; };
  const a = tot(it), b = tot(cur), keys = [...new Set([...Object.keys(a), ...Object.keys(b)])], out = [];
  for (const [key, name] of [['resFire', ' fire resist'], ['resWater', ' water resist'], ['resLight', ' light resist'], ['resDark', ' dark resist']]) {   // gearfx: per school; resAll adds to each
    const d = ((a[key] || 0) + (a.resAll || 0)) - ((b[key] || 0) + (b.resAll || 0)); if (Math.abs(d) < 0.5) continue;
    out.push(`<b class="${d > 0 ? 'up' : 'dn'}">${d > 0 ? '+' : ''}${Math.round(d)}${name}</b>`);
  }
  for (const key of keys) {
    if (key === 'resFire' || key === 'resWater' || key === 'resLight' || key === 'resDark' || key === 'resAll') continue;
    const N = MOD_NAME[key] || [` ${key}`, 1], d = ((a[key] || 0) - (b[key] || 0)) * N[1]; if (Math.abs(d) < 0.05) continue;
    const better = key === 'guardMul' ? d < 0 : d > 0;
    out.push(`<b class="${better ? 'up' : 'dn'}">${d > 0 ? '+' : ''}${Math.abs(d) >= 10 || N[1] === 1 ? Math.round(d) : d.toFixed(1)}${N[0]}</b>`);
  }
  const ids = (x) => [...new Set((x.procs || []).map((p) => p.id))], pa = ids(it), pb = ids(cur);   // gearfx: proc words gained (up) / lost (dn)
  for (const id of pa) if (!pb.includes(id)) out.push(`<b class="up">+ ${procName(id)}</b>`);
  for (const id of pb) if (!pa.includes(id)) out.push(`<b class="dn">- ${procName(id)}</b>`);
  return `vs ${cur.name}: ${out.length ? out.join(' ') : 'about the same'}`;
}
export function describe(it) {
  const k = 1 + 0.07 * (it.up || 0), m = Object.fromEntries(Object.entries(it.mods).map(([key, v]) => [key, INT_MOD.has(key) ? Math.round(v * k) : v * k])), out = [];
  const ptxt = (v) => { const n = v * 100; return Math.abs(n - Math.round(n)) < 0.05 ? String(Math.round(n)) : n.toFixed(1); };   // gearfx: whole percents stay whole ("+3% move"); avoid keeps a tenth
  if (it.at) out.push(AT_WORD[it.at] || (it.at.charAt(0).toUpperCase() + it.at.slice(1)));   // gearfx: Plate / Chain / Leather / Cloth first
  if (it.up) out.push(`+${it.up} tempered`);
  if (m.meleeMul) out.push(`+${Math.round(m.meleeMul * 100)}% melee`);
  if (m.spellMul) out.push(`+${Math.round(m.spellMul * 100)}% spells`);
  if (m.hpAdd) out.push(`+${m.hpAdd} HP`);
  if (m.guardMul) out.push(`guard ${Math.round(m.guardMul * 100)}% dmg`);
  if (m.crit) out.push(`+${(m.crit * 100).toFixed(1)}% crit`);
  if (m.stAdd) out.push(`+${m.stAdd} stamina`);
  if (m.summonMul) out.push(`+${Math.round(m.summonMul * 100)}% summons`);
  if (m.critDmg) out.push(`+${Math.round(m.critDmg * 100)}% crit damage`);
  if (m.rollSpeed) out.push(`+${Math.round(m.rollSpeed * 100)}% roll distance`);
  if (m.drain) out.push(`${(m.drain * 100).toFixed(1)}% life drain`);
  if (m.regen) out.push(`+${m.regen.toFixed(1)} HP/s resting`);
  if (m.healMul) out.push(`+${Math.round(m.healMul * 100)}% healing`);
  if (m.spellCd) out.push(`-${(m.spellCd * 100).toFixed(1)}% spell cooldown`);
  if (m.stRegen) out.push(`+${Math.round(m.stRegen * 100)}% stamina regen`);
  if (m.resFire) out.push(`+${m.resFire} fire resist`);
  if (m.resWater) out.push(`+${m.resWater} water resist`);
  if (m.resLight) out.push(`+${m.resLight} light resist`);
  if (m.resDark) out.push(`+${m.resDark} dark resist`);
  if (m.resAll) out.push(`+${m.resAll} all resists`);
  if (m.avoid) { const t = (m.avoid * 100).toFixed(1); if (t !== '0.0') out.push(`+${t}% avoid`); }
  if (m.move) { const t = ptxt(m.move); if (t !== '0') out.push(`+${t}% move`); }
  if (m.haste) { const t = ptxt(m.haste); if (t !== '0') out.push(`+${t}% haste`); }
  if (m.block) { const t = ptxt(m.block); if (t !== '0') out.push(`+${t}% block`); }
  if (m.runePct) { const t = ptxt(m.runePct); if (t !== '0') out.push(`Rune % +${t}`); }   // gearfx: label runePct "Rune %"
  if (m.shieldPct) { const t = ptxt(m.shieldPct); if (t !== '0') out.push(`Spell Shield % +${t}`); }   // gearfx: label shieldPct "Spell Shield %"
  for (const p of it.procs || []) { const d = PROCS[p.id] || {}, ch = Math.round(((p.ch ?? d.ch) || 0) * 100), icd = p.icd ?? d.icd ?? 0, cd = Math.abs(icd - Math.round(icd)) < 1e-6 ? Math.round(icd) : +(+icd).toFixed(1); out.push(`✦ ${procName(p.id)} ${ch}% · ${cd} s cd`); }   // gearfx: chance and cooldown
  for (const g of it.gems || []) out.push(g ? `◆ ${GEMS[g].name}` : '◇ empty socket');
  return out.join(' · ');
}
export function gearMods(S, m) {   // fold equipped gear into progress.mods()
  m.procs = [];   // gearfx: {id, ch, icd, lv, uid} from equipped weapons; resAll stays its own key (combat adds it to every school)
  for (const it of Object.values((S && S.gear) || {})) {
    if (!it) continue;
    const k = 1 + 0.07 * (it.up || 0);   // 6.7 forge: +7% per + on the item's own mods (not gems, not proc chances)
    const own = Object.fromEntries(Object.entries(it.mods).map(([key, v]) => [key, INT_MOD.has(key) ? Math.round(v * k) : v * k]));
    const all = [own, ...(it.gems || []).filter(Boolean).map((g) => GEMS[g].mods)];
    for (const mods of all) for (const [key, v] of Object.entries(mods)) {
      if (key === 'guardMul') m.guardMul = Math.max(0.4, m.guardMul + v);
      else m[key] = (m[key] || 0) + v;
    }
    for (const p of it.procs || []) m.procs.push({ id: p.id, ch: p.ch, icd: p.icd, lv: it.lv, uid: it.uid });
  }
  return m;
}
// pixel art: icon canvas (8x8 at scale, 1 px ink outline) and beam canvas
const SOCK_Y = { 1: [1], 2: [1, 6], 3: [0, 3, 6] };   // 6.7: Orri's 3rd socket (Epic / Legendary): top, middle, bottom
export function iconCanvas(kind, rar, scale = 3, gems = null, up = 0) {
  const R = RARITY[rar] || RARITY[0], rows = ICONS[kind] || ICONS.neck;
  const cv = document.createElement('canvas'); cv.width = 10 * scale; cv.height = 10 * scale;
  const g = cv.getContext('2d'); g.imageSmoothingEnabled = false;
  const col = { 1: kind === 'gold' ? '#f2c24a' : R.col, 2: '#fff8e6', 3: kind === 'gold' ? '#c4502c' : R.lo };
  const on = (x, y) => y >= 0 && y < 8 && x >= 0 && x < 8 && rows[y][x] !== '.';
  const px = (x, y, c) => { g.fillStyle = c; g.fillRect(x * scale, y * scale, scale, scale); };
  for (let y = -1; y < 9; y++) for (let x = -1; x < 9; x++) if (!on(x, y) && (on(x + 1, y) || on(x - 1, y) || on(x, y + 1) || on(x, y - 1))) px(x + 1, y + 1, INK);
  for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) if (on(x, y)) px(x + 1, y + 1, col[rows[y][x]] || R.col);
  if (kind === 'gem') return gemPaint(cv, g, px, gems && gems[0]);
  // sockets: 2x2 inlays down the right edge; a set gem glows (a dithered ring of its colour), an empty one is a dark hole
  (gems || []).forEach((gm, k) => {
    const x = 7, y = (SOCK_Y[gems.length] || [1, 6, 6])[k], G = gm && GEMS[gm];
    if (G) for (const [dx, dy] of [[-1, 0], [2, 1], [0, -1], [1, 2], [-1, 1], [2, 0], [1, -1], [0, 2]]) if ((dx + dy + k) % 2 === 0) px(x + dx, y + dy, G.col);
    px(x, y, G ? '#fff8e6' : INK); px(x + 1, y, G ? G.col : INK); px(x, y + 1, G ? G.col : INK); px(x + 1, y + 1, G ? G.lo : '#5a3e26');
  });
  // 6.7 temper marks: +7..+9 a cold-blue glint pixel on the left edge, +10 a cold-blue ember (glint + mote above it)
  if (up >= 7) { px(0, 2, '#a6ecff'); px(0, 3, '#2ab4ff'); }
  if (up >= 10) { px(1, 0, '#a6ecff'); px(0, 1, '#2ab4ff'); }
  return cv;
}
// a loose gem: a faceted 6x6 stone in its colour, white glint, ink outline
function gemPaint(cv, g, px, id) {
  const G = GEMS[id] || GEMS.rift_shard;
  g.clearRect(0, 0, cv.width, cv.height);
  const rows = ['..11..', '.1211.', '122113', '111133', '.1133.', '..33..'];
  const on = (x, y) => y >= 0 && y < 6 && x >= 0 && x < 6 && rows[y][x] !== '.';
  for (let y = -1; y < 7; y++) for (let x = -1; x < 7; x++) if (!on(x, y) && (on(x + 1, y) || on(x - 1, y) || on(x, y + 1) || on(x, y - 1))) px(x + 2, y + 2, INK);
  for (let y = 0; y < 6; y++) for (let x = 0; x < 6; x++) if (on(x, y)) px(x + 2, y + 2, { 1: G.col, 2: '#fff8e6', 3: G.lo }[rows[y][x]]);
  return cv;
}
function beamCanvas(rar, scale = 3, frame = 0) {
  const R = RARITY[rar], H = rar >= R_RUNE ? 38 : rar >= R_LEG ? 34 : 26 + rar * 3;
  const cv = document.createElement('canvas'); cv.width = 7 * scale; cv.height = H * scale;
  drawBeam(cv, rar, scale, frame);
  return cv;
}
function drawBeam(cv, rar, scale, frame) {
  const R = RARITY[rar], g = cv.getContext('2d'), H = cv.height / scale;
  g.clearRect(0, 0, cv.width, cv.height);
  const px = (x, y, c) => { g.fillStyle = c; g.fillRect(x * scale, y * scale, scale, scale); };
  for (let y = 0; y < H; y++) {
    const t = y / H;                                   // 0 top .. 1 bottom: dither thins out towards the top
    const keep = (x) => ((x + y + frame) % 4 === 0) || t > 0.75 || (t > 0.4 && (x + y) % 2 === 0);
    if (keep(3) || t > 0.2) px(3, y, t > 0.55 ? '#fff8e6' : R.col);
    if (keep(2)) px(2, y, R.col); if (keep(4)) px(4, y, R.col);
    if (t > 0.6 && (y + frame) % 2 === 0) { px(1, y, R.lo); px(5, y, R.lo); }
  }
  if (rar >= R_RUNE) {   // Runeforged: a slow magenta pulse (about 2.4 s a breath) washes up the beam's core and edges
    const p = 0.5 + 0.5 * Math.sin(frame * Math.PI * 2 / 24), on = p > 0.66 ? R.hi : p > 0.33 ? R.col : R.lo;
    for (let y = 0; y < H; y++) if ((y + Math.floor(frame / 3)) % 3 === 0) { px(1, y, on); px(5, y, on); }
    for (let y = Math.floor(H * (1 - p) * 0.8); y < H * 0.55; y++) px(3, y, on);
  }
  if (rar >= 1) for (let k = 0; k < rar; k++) { const y = (Math.floor(frame * 1.5) + k * 7) % H; px(k % 2 ? 6 : 0, H - 1 - y, '#fff8e6'); }   // rising motes
}
// Legendary aura: a ring of neon pixels marching round the drop (4 frames, colours cycle)
function drawAura(cv, scale, frame, epic, worn = false, rune = false) {
  const g = cv.getContext('2d'), W = cv.width / scale, Hh = cv.height / scale;
  g.clearRect(0, 0, cv.width, cv.height);
  const cols = rune ? ['#ff2bd6', '#ffb4ea', '#fff8e6', '#b82a8c'] : epic ? ['#b46cff', '#e0c8f4', '#6a34b8'] : ['#ffc85a', '#f2c24a', '#fff8e6', '#b07a2a'];
  // worn (under the hero): the DOM layer sits over the sprite, so the back arc behind the legs is left out
  const px = (x, y, c) => { if (worn && y < Hh / 2 - 0.5 && Math.abs(x - W / 2) < 6) return; g.fillStyle = c; g.fillRect(Math.round(x) * scale, Math.round(y) * scale, scale, scale); };
  const ring = (rx, ry, n, skip, off) => {
    for (let i = 0; i < n; i++) {
      if ((i + frame + off) % skip) continue;
      const a = i / n * Math.PI * 2;
      px(W / 2 + Math.cos(a) * rx, Hh / 2 + Math.sin(a) * ry, cols[(i + frame) % cols.length]);
    }
  };
  ring(W / 2 - 1, Hh / 2 - 1, epic ? 30 : 44, 2, 0);                 // outer marching ring
  if (!epic) ring(W / 2 - 4, Hh / 2 - 2.5, 30, 3, 1);                 // legendary: a second, counter-phased ring
  // four sparks orbiting (plus shapes, white core)
  const k = epic ? 2 : 4;
  for (let j = 0; j < k; j++) {
    const a = (frame / 8 + j / k) * Math.PI * 2, x = W / 2 + Math.cos(a) * (W / 2 - 2), y = Hh / 2 + Math.sin(a) * (Hh / 2 - 1.5);
    px(x, y, '#fff8e6'); px(x + 1, y, cols[0]); px(x - 1, y, cols[0]); px(x, y - 1, cols[1]); px(x, y + 1, cols[1]);
  }
}

export class Loot {
  constructor(G) { this.G = G; this.layer = document.getElementById('fxlayer'); this.drops = []; this.t = 0; }
  attach(ctx) { this.clear(); this.ctx = ctx; }
  detach() { this.clear(); this.ctx = null; }
  clear() {
    for (const d of this.drops) { d.el.remove(); if (d.light) d.light.kill = true; }
    this.drops = [];
    if (this.pa) { this.pa.el.remove(); if (this.pa.light) this.pa.light.kill = true; this.pa = null; }
  }
  // a Legendary equipped: the same marching neon ring under the hero's feet, plus a warm rune light that follows
  playerAura(fr) {
    const ctx = this.ctx, S = this.G.S, p = ctx.player;
    const on = !!Object.values(S.gear || {}).some((it) => it && it.rar >= R_LEG) && !this.G.title;
    if (!on) { if (this.pa) { this.pa.el.remove(); if (this.pa.light) this.pa.light.kill = true; this.pa = null; } return; }
    if (!this.pa) {
      const el = document.createElement('div'); el.className = 'loot paura';
      const cv = document.createElement('canvas'); cv.width = 26 * 3; cv.height = 13 * 3; cv.className = 'aura'; el.appendChild(cv);
      this.layer.appendChild(el);
      const light = ctx.addGlow ? ctx.addGlow(p.x, p.y, p.z, { color: RARITY[R_LEG].col, intensity: 2.6, range: 2.6, lift: 0.5, fadeIn: 0.4 }) : null;
      this.pa = { el, cv, light, frame: -1 };
    }
    const s = ctx.project(p.x, p.y + 0.03, p.z);
    this.pa.el.style.transform = `translate(${Math.round(s.x)}px, ${Math.round(s.y)}px)`;
    this.pa.el.style.visibility = p.quad && !p.quad.visible ? 'hidden' : '';
    if (this.pa.light) this.pa.light.pos.set(p.x, p.y, p.z);
    if (fr !== this.pa.frame) { this.pa.frame = fr; drawAura(this.pa.cv, 3, fr % 8, false, true, Object.values(this.G.S.gear || {}).some((it) => it && it.rar >= R_RUNE)); }
  }
  // an enemy went down: gold always, and sometimes an item (rarity weights, level-scaled)
  onKill(a, lv, o = {}) {
    const gold = 2 + Math.floor(Math.random() * 5) + (o.gold || 0);
    this.drop(a.x + 0.35, a.z + 0.2, { gold });
    const luck = this.G.S.mode === 'hero' ? 1 : 0, cls = this.G.S.cls;   // gearfx: pass class so 70% of armor matches CLASS_ARMOR
    if (o.legendary) {   // a boss: always a Legendary (template boss odds: 4% it comes out Runeforged), and Glenheart's golem core
      this.drop(a.x - 0.3, a.z + 0.35, { item: makeItem(lv + 1, Math.random() < 0.04 * (luck ? 1.25 : 1) ? R_RUNE : R_LEG, null, Math.random, luck, cls) });
      this.drop(a.x + 0.1, a.z - 0.35, { gem: 'golem_core' });
      return;
    }
    if (o.minRar != null) {   // rares (Rare+) and rift rewards: always an item of at least that rarity
      this.dropItem(a.x - 0.3, a.z + 0.35, lv + 1, o.minRar);
      if (Math.random() < 0.5) this.drop(a.x + 0.05, a.z - 0.4, { gem: 'rift_shard' });
      return;
    }
    const gemOdds = { golem: ['golem_core', 0.1], icegolem: ['frost_core', 0.25], wraith: ['rift_shard', 0.08], skelmage: ['rift_shard', 0.1], mossgolem: ['golem_core', 0.15], sporeling: ['rift_shard', 0.08] }[a.role];
    if (gemOdds && Math.random() < gemOdds[1]) this.drop(a.x + 0.05, a.z - 0.4, { gem: gemOdds[0] });
    if (Math.random() < 0.6 + luck * 0.1) this.drop(a.x - 0.3, a.z + 0.35, { item: makeItem(lv, null, null, Math.random, luck, cls) });
  }
  dropItem(x, z, lv, minRar = 0) {
    const luck = this.G.S.mode === 'hero' ? 1 : 0, cls = this.G.S.cls;   // gearfx: rare / rift drops use the same class armor bias
    return this.drop(x, z, { item: makeItem(lv, rollRarity(1, luck, minRar), null, Math.random, luck, cls) });
  }
  drop(x, z, what) {
    const ctx = this.ctx; if (!ctx || !this.layer) return null;
    const y = ctx.heightAt(x, z), it = what.item || null, rar = it ? it.rar : -1;
    const el = document.createElement('div'); el.className = 'loot' + (it ? ' r' + rar : what.gem ? ' gem' : ' gold') + (what.purse ? ' purse' : '');
    const sc = 3;
    let beam = null, aura = null;
    if (it) { beam = beamCanvas(rar, sc); beam.className = 'beam'; el.appendChild(beam); }
    if (rar >= R_EPIC) { aura = document.createElement('canvas'); aura.width = 26 * sc; aura.height = 13 * sc; aura.className = 'aura'; el.appendChild(aura); }
    const icon = what.gem ? iconCanvas('gem', 0, sc, [what.gem]) : iconCanvas(it ? it.slot : 'gold', Math.max(0, rar), sc, it ? it.gems : null, it ? it.up || 0 : 0); icon.className = 'icon'; el.appendChild(icon);
    this.layer.appendChild(el);
    // Epic / Legendary drops also light the ground around them (a pooled point light, no bloom)
    const light = rar >= R_EPIC && ctx.addGlow ? ctx.addGlow(x, y, z, { color: RARITY[rar].col, intensity: rar >= R_LEG ? 6 : 3.5, range: 2.8, lift: 0.45, fadeIn: 0.3 }) : null;
    const d = { x, y, z, it, gem: what.gem || null, gold: what.gold || 0, purse: !!what.purse, el, beam, aura, sc, frame: -1, t: 0, light };
    this.drops.push(d);
    return d;
  }
  update(dt) {
    const ctx = this.ctx; if (!ctx) return;
    this.t += dt;
    const p = ctx.player, fr = Math.floor(this.t * 6);
    this.playerAura(fr);
    for (const d of [...this.drops]) {
      d.t += dt;
      if (!this.G.downed && Math.hypot(p.x - d.x, p.z - d.z) < 0.75 && d.t > 0.4) { this.pick(d); continue; }
      const s = ctx.project(d.x, d.y + 0.05, d.z);
      d.el.style.transform = `translate(${Math.round(s.x)}px, ${Math.round(s.y)}px)`;
      if (fr !== d.frame) {
        d.frame = fr;
        if (d.beam) drawBeam(d.beam, d.it.rar, d.sc, fr);
        if (d.aura) drawAura(d.aura, d.sc, fr % 8, d.it.rar === R_EPIC, false, d.it.rar >= R_RUNE);
      }
    }
  }
  pick(d) {
    const G = this.G, S = ensure(G.S);
    if (d.it && S.bag.length >= BAG_MAX) { if (!d.full) { d.full = true; G.toast && G.toast('Bag full: scrap something on the gear page (G)', 2.4); } return; }
    d.el.remove(); this.drops.splice(this.drops.indexOf(d), 1);
    if (d.purse) { S.purse = null; G.toast && G.toast(`Found your purse: +${d.gold} gold`, 2.4); }
    if (d.gold && !d.purse && G.factions) d.gold = Math.round(d.gold * G.factions.pickupGoldMul());   // Gnome Council Friend: +10%
    if (d.gold && !d.purse) { const gm = (G.combat && G.combat.M && G.combat.M.goldMul) || 0; if (gm) d.gold = Math.floor(d.gold * (1 + gm) + Math.random()); }   // Tick's Clockwork Eye: pickup gold +6% / +8%
    if (d.gold) { S.gold += d.gold; G.popText && G.popText(`+${d.gold}`, d, '#f2c24a'); }
    if (d.gem) { S.gems[d.gem] = (S.gems[d.gem] || 0) + 1; G.toast && G.toast(`<span style="color:${GEMS[d.gem].lo}">${GEMS[d.gem].name}</span>: a socket gem (G: gear page)`, 2.6, true); }
    if (d.it) { S.bag.push(d.it); G.toast && G.toast(`<span style="color:${RARITY[d.it.rar].lo}">${RARITY[d.it.rar].name}</span> ${d.it.name}`, 2.4, true); }
    G.audio && G.audio.sfx(d.it && d.it.rar >= R_RARE ? 'rare_pickup' : d.it || d.gem ? 'pickup' : d.gold ? 'coin' : 'pickup');   // [SFX 2026-11-03] RARITY[1] = rare and up: stinger; gold only: coin
    if (d.light) d.light.kill = true;
    G.drawBag && G.drawBag();
    G.onLoot && G.onLoot(d);
  }
  removePurse() { for (const d of this.drops.filter((x) => x.purse)) { d.el.remove(); if (d.light) d.light.kill = true; this.drops.splice(this.drops.indexOf(d), 1); } }
  restorePurse(area) { const P = this.G.S.purse; if (P && P.area === area && P.gold > 0) this.drop(P.x, P.z, { gold: P.gold, purse: true }); }
  auraOn() { return !!this.pa; }
  qa() { return this.drops.map((d) => ({ x: +d.x.toFixed(2), z: +d.z.toFixed(2), gold: d.gold, gem: d.gem, rar: d.it ? d.it.rar : null, slot: d.it ? d.it.slot : null })); }
}
// bag / gear actions (the hero screen's Gear tab calls these)
export function equip(S, i) {
  ensure(S); const it = S.bag[i]; if (!it) return false;
  const sl = targetSlot(S, it); if (ringSlot(sl)) it.slot = sl;   // rings: the free ring slot, else replace the weaker ring
  const cur = S.gear[sl]; S.gear[sl] = it; S.bag.splice(i, 1); if (cur) S.bag.splice(i, 0, cur);
  return true;
}
export function unequip(S, slot) {
  ensure(S); const it = S.gear[slot]; if (!it || S.bag.length >= BAG_MAX) return false;
  S.gear[slot] = null; S.bag.unshift(it); return true;
}
export function scrap(S, i) {
  ensure(S); const it = S.bag[i]; if (!it) return 0;
  S.bag.splice(i, 1); const g = RARITY[it.rar].scrap; S.gold += g; return g;
}
