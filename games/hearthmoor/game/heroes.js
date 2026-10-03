// Hearthmoor heroes (the six starters), their first spell + first summon, enemy stats and where enemies live.
// All original. Numbers are stage-1 tuning: forgiving, cozy, readable.
export const HEROES = [
  { id: 'wildcaller', cls: 'Wildcaller', origin: 'Midgard farmhand', kind: 'mortal', style: 'caster',
    blurb: 'Grew up behind a plough. Hearth-and-earth magic comes easily: seed bombs, roots and warm light. Learns any charm faster.',
    hp: 90, melee: { dmg: 11, reach: 1.45 }, spell: 'seed_bomb', summon: 'mushgolem' },
  { id: 'runeguard', cls: 'Runeguard', origin: 'Shield-warden', kind: 'mortal', style: 'brawler',
    blurb: 'Hearthmoor\'s own guard. Light runes burn on her round shield: block, charge and slam. The steadiest fighter.',
    hp: 125, melee: { dmg: 15, reach: 1.35 }, spell: 'rune_slam', summon: 'runesentinel', guard: 0.15 },
  { id: 'seer', cls: 'Seer', origin: 'Rune-reader', kind: 'mortal', style: 'caster',
    blurb: 'The village seer. Reads the runes, lays glowing traps and sees a heartbeat ahead. Spots hidden clues.',
    hp: 85, melee: { dmg: 10, reach: 1.5 }, spell: 'rune_trap', summon: 'runewisp' },
  { id: 'stormborn', cls: 'Stormborn', origin: 'Child of thunder', kind: 'demigod', style: 'brawler',
    blurb: 'Half sky. Swings a stone war-hammer and calls lightning that leaps from foe to foe.',
    hp: 120, melee: { dmg: 17, reach: 1.4 }, spell: 'chain_lightning', summon: 'stormsprite' },
  { id: 'grovekeeper', cls: 'Grovekeeper', origin: 'Child of the Vanir', kind: 'demigod', style: 'caster',
    blurb: 'Moss in the hair, flowers in the footsteps. Heals with blooms and spores; mushroom folk are friends.',
    hp: 95, melee: { dmg: 10, reach: 1.4 }, spell: 'bloom', summon: 'sapling' },
  { id: 'cinderknight', cls: 'Cinderknight', origin: 'Ember-born', kind: 'demigod', style: 'brawler',
    blurb: 'Heavy dark plate with an ember seam. A greatsword that flings fire. Fire spirits answer the call.',
    hp: 130, melee: { dmg: 18, reach: 1.65 }, spell: 'ember_slash', summon: 'emberimp' },
];
export const HERO = Object.fromEntries(HEROES.map((h) => [h.id, h]));

// first spells: cooldown (s), damage, shape. The visuals live in the spells atlas (tools/spells/spells.py).
export const SPELLS = {
  seed_bomb: { name: 'Seed Bomb', cd: 1.6, dmg: 22, radius: 1.5, kind: 'projectile', fx: 'seed_bomb', burst: 'earth_burst' },
  rune_slam: { name: 'Rune Slam', cd: 4.0, dmg: 20, radius: 2.5, kind: 'nova', push: 1.4 },
  rune_trap: { name: 'Rune Trap', cd: 3.0, dmg: 28, radius: 1.7, kind: 'trap', arm: 0.5, life: 6 },
  chain_lightning: { name: 'Chain Lightning', cd: 3.5, dmg: 20, range: 6.5, jumps: 2, hop: 3.6, kind: 'chain' },
  bloom: { name: 'Bloom', cd: 6.0, heal: 35, dmg: 10, radius: 2.2, kind: 'heal' },
  ember_slash: { name: 'Ember Slash', cd: 2.0, dmg: 18, kind: 'pierce', fx: 'ember_slash' },
};
// charms (the errand rewards) still cast: small, friendly damage so they matter in a pinch
export const CHARM_DMG = { sparkle_burst: 8, frost_puff: 10, hearth_flame: 9, leaf_gust: 8, light_orb: 0, healing_petals: 0, bolt: 12 };
export const CHARM_CD = 1.2;

export const SUMMONS = {
  mushgolem: { name: 'Mushroom golem', hp: 40, dmg: 8, reach: 1.1, speed: 2.2 },
  runesentinel: { name: 'Rune sentinel', hp: 60, dmg: 7, reach: 1.2, speed: 2.0 },
  runewisp: { name: 'Rune-wisp', hp: 30, dmg: 7, reach: 3.2, speed: 2.8, ranged: true },
  stormsprite: { name: 'Storm sprite', hp: 35, dmg: 9, reach: 3.0, speed: 2.8, ranged: true },
  sapling: { name: 'Treant sapling', hp: 50, dmg: 8, reach: 1.4, speed: 2.0 },
  emberimp: { name: 'Ember imp', hp: 35, dmg: 9, reach: 2.8, speed: 2.6, ranged: true },
};
export const SUMMON_LIFE = 15, SUMMON_CD = 30;

export const ENEMIES = {
  golem: { name: 'Stone golem', hp: 120, dmg: 18, speed: 1.05, reach: 1.6, windup: 0.62, cd: 1.9, aggro: 5.5, r: 0.36, push: 0.2 },
  skeleton: { name: 'Skeleton swordsman', hp: 60, dmg: 10, speed: 2.0, reach: 1.2, windup: 0.36, cd: 1.15, aggro: 6.0, r: 0.28, push: 0.5 },
  wraith: { name: 'Cold-fire wraith', hp: 45, dmg: 9, speed: 1.6, reach: 6.0, keep: 3.2, windup: 0.5, cd: 2.3, aggro: 6.5, r: 0.26, push: 0.6, ranged: true, float: true, shy: true },
  // stage 3: a frost golem (its slam chills: drains stamina), a skeleton mage (arcane bolts from range), and
  // Mossheart, the Mossglen mini-boss (every third slam is a rune shockwave; always drops a Legendary)
  icegolem: { name: 'Frost golem', hp: 140, dmg: 15, speed: 1.0, reach: 1.6, windup: 0.66, cd: 2.0, aggro: 5.5, r: 0.36, push: 0.2, heavy: true, slam: true, chill: 18 },
  skelmage: { name: 'Skeleton mage', hp: 52, dmg: 11, speed: 1.7, reach: 6.5, keep: 3.8, windup: 0.6, cd: 2.5, aggro: 7.0, r: 0.28, push: 0.5, ranged: true, bolt: 'bolt' },
  // scale: figure height in hero heights (style lock: mini-boss / rare ~2.5x, boss 5x+). The art is drawn natively on its
  // own boss sheet (tools/sprite/boss_sheet.py, area spec boss_roles); hitbox r, reach, wave ring, light and nav
  // clearance below are authored for that size, and combat.js scales the slam dust / telegraph / light by `scale`
  eldergolem: { name: 'Mossheart, the Elder Golem', scale: 2.5, hp: 460, dmg: 22, speed: 1.0, reach: 3.0, windup: 0.78, cd: 2.0, aggro: 7.5, r: 0.8, push: 0.15, heavy: true, slam: true,
                boss: true, wave: { every: 3, r: 4.2, dmg: 16 }, respawn: 600, legendary: true, glow: '#f2a63a' },
};
export const RESPAWN = 60;      // seconds before a defeated enemy wanders back
export const LEASH = 12;        // metres from home before an enemy gives up and goes home

// enemy homes per area (walkable, reachable, clear of the errand paths' first steps)
export const SPAWNS = {
  mossglen: [
    { id: 'golem_0', role: 'golem', pos: [1.6, 1.0] },
    { id: 'skeleton_0', role: 'skeleton', pos: [5.0, 2.6] },
    { id: 'wraith_0', role: 'wraith', pos: [-6.0, -4.4] },
    { id: 'wraith_night', role: 'wraith', pos: [-2.6, 2.6], night: true },
    { id: 'icegolem_0', role: 'icegolem', pos: [9.0, 4.6] },
    { id: 'skelmage_0', role: 'skelmage', pos: [-1.2, 5.6] },
    { id: 'mossheart', role: 'eldergolem', pos: [10.2, -0.6] },
  ],
  hollows: [
    { id: 'wraith_h0', role: 'wraith', pos: [7.6, -0.8] },
    { id: 'wraith_hnight', role: 'wraith', pos: [-6.4, -6.0], night: true },
    { id: 'skeleton_h0', role: 'skeleton', pos: [2.2, 5.4] },
  ],
};

export const PLAYER = { stamina: 100, regen: 30, regenDelay: 0.6, atkCost: 6, dodgeCost: 25, guardMul: 0.25, hitIframes: 0.5,
                        respawnIframes: 2.0, impact: 0.17, arc: 0.5 /* cos(60°) */ };
