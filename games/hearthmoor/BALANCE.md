# Hearthmoor balance sheet (numbers read from the code, 2026-10-26)

Source of truth is the code; update this file when you change a number. Paths are under `games/hearthmoor/game/`.

## Difficulty modes (`progress.js` MODES)
| Mode | damage taken | damage dealt | faint penalty | luck |
|---|---|---|---|---|
| Story | x0.6 | x1.15 | 0 | 0 |
| Adventurer | x1 | x1 | 10 % | 0 |
| Hero | x1.35 | x0.9 | 10 % | +1 |

## Player (`heroes.js` PLAYER, `progress.js`)
- Stamina 100, regen 30/s after 0.6 s; attack costs 6, dodge 25; guard takes x0.25 damage; 0.5 s i-frames on hit, 2 s after respawn; melee arc 60 deg.
- Level cap 50; XP to next level `round(60 * L^1.6)`; 2 stat points + 1 skill point per level. Stats: Might, Arcana, Spirit, Vigor, Grit, Swiftness.
- Skill tiers (`TIER`): tier 1 cost 1 at Lv 1, tier 2 cost 1 at Lv 5, tier 3 cost 2 at Lv 10.
- XP per kill (`XP`): golem 45, skeleton 28, wraith 34, frost golem 55, skeleton mage 36, sporeling 30, moss golem 60, Glenheart 260; errand 120; `firstKill` factor 0.5 (see progress.js).

## Spells, charms, summons (`heroes.js`)
| Spell | cd s | dmg | notes |
|---|---|---|---|
| Seed Bomb | 1.6 | 22 | r 1.5 projectile |
| Rune Slam | 4.0 | 20 | r 2.5 nova, push 1.4 |
| Rune Trap | 3.0 | 28 | r 1.7, arms 0.5 s, lasts 6 s |
| Chain Lightning | 3.5 | 20 | range 6.5, 2 jumps |
| Bloom | 6.0 | 10 | heals 35, r 2.2 |
| Ember Slash | 2.0 | 18 | pierce |
- Charms (errand rewards): sparkle 8, frost puff 10, hearth flame 9, leaf gust 8, bolt 12, light orb / healing petals 0; cd 1.2 s.
- Summons last 15 s, cooldown 30 s: mushroom golem 40 HP / 8 dmg, rune sentinel 60/7, rune-wisp 30/7 (ranged), storm sprite 35/9 (ranged), treant sapling 50/8, ember imp 35/9 (ranged).

## Enemies (`heroes.js` ENEMIES, `combat.js`)
| Enemy | HP | dmg | notes |
|---|---|---|---|
| Rift wraith (Lantern Eve) | 30 | 5 | gentle opener |
| Cold-fire wraith | 45 | 9 | ranged |
| Skeleton swordsman | 60 | 10 | |
| Skeleton mage | 52 | 11 | ranged bolt |
| Spore elemental | 40 | 8 | ranged |
| Stone golem | 120 | 18 | |
| Frost golem | 140 | 15 | slam chills 18 stamina |
| Moss golem | 150 | 16 | slam roots, 14 stamina |
| Rot treant | 120 | 14 | |
| Magma hound (`combat.js`) | 110 | 13 | |
| Ice golem (`combat.js`) | 100 | 15 | |
| Glenheart (mini-boss 2.5x) | 460 | 22 | wave every 3rd slam (16), respawn 600 s, always Legendary |
| The Thornmother (2.4x) | 520 | 20 | rare |
| The Blight Regent (5.5x) | 1400 | 26 | phases at 60 % / 25 %, frost-iron spike weak point, wave 20 |
| Hjortur (6x, trial when befriended) | 1600 | 24 | wave 18; corrupted (conquer) 1700 / 28, wave 22 |
- Enemies respawn after 60 s, leash 12 m.

## Loot (`loot.js`)
| Rarity | drop weight | stat mul | scrap |
|---|---|---|---|
| Common | 52 | x1 | 2 |
| Uncommon | 27 | x1.4 | 4 |
| Rare | 13 | x1.9 | 8 |
| Epic | 6 | x2.6 | 16 |
| Legendary | 2 | x3.5 | 32 |
- Bag 30 slots, bank 40. Slots: weapon, armor, trinket.

## Economy (`shop.js`, `forge.js`, `factions.js`)
- Gear buy price by rarity 20 / 45 / 110 / 260 / 600 gold, +5 % per item level above 1; sell = 25 % of buy (night merchant x1.2), never below scrap + 1.
- Goods: tonic 12 (heals 60), den biscuit 6, glow-dew 5, vial 2, red toadstool 4, iron bits 6, cold-steel ingot 30, rune-stone 40, glow-fish 10, empty orb 18.
- Tempering (Tova, `UP`): +7 % per level; caps by rarity +2 / +4 / +6 / +8 / +10; cost +1 15g 2 iron ... +10 350g 12 iron 5 steel + golem core + rift shard; chance 100 % to +5, then 90 / 80 / 70 / 60 / 50 %; each fail adds heat (+15 % chance), 3 heat = sure.
- Sockets: cap by rarity 0 / 1 / 2 / 3 / 3; punch costs 50g + 2 iron, 120g + 1 steel, 250g + 2 steel + rift shard. Scrap iron by rarity 1 / 2 / 3 / 4 / 6.
- Faction merit (`MERIT`): errand 40, rifts 30 / 60 / 120, rare 50, boss 80, riddle 60, secret 40; ranks Stranger, Friend, Trusted, Honored, Champion, Legend.

## 2026-10-28: Vanaheim Stage B (decider: Game Director; spare reward details from Hearthmoor Story)

- **Mother Nettlecrown** (vh_garden, the Thorngarden): scale 5.5, 1500 HP, 22 dmg, phases at 65 % and 35 %, heartroot grab at 10 % (14 dmg), yields at 5 % (75 HP, never dies), then the `nettle_end` choice. No enrage. 600 XP.
- Adds: 2 thorn-nymphs in P1, 2 more in P3 (32 XP each). The conquer path adds 1 Thornhex (70 XP) that heals her 20 HP every 6 s.
- XP: Blight Regent 560, Hjortur 640.
- Tobble unlocks when `vh_tobble` is done (moved from the Svartalfheim gate).
- **Spring Wages** contract (players already at 4 allies): sets `vh_contract`, starts `vh_spring`, merit goes to the Gate faction, gives `blight_spike` evidence, 150 gold. No Tobble, no Mossheart Staff, no Growth school.
- Hollis is dialogue only. The Nettlecrown sabotage hook is parked. Befriend sets `vh_thorn_pact`; finale code is untouched.
- Mini-boss is Glenheart; the staff keeps the name "Mossheart Staff". "Moss Ward" replaces "bloom shield" (no such string existed in code yet; the Growth school is not built). The moss golem is the tier-3 summon upgrade.
- **Spare reward** (should pay about what conquering does): her garden reopens as a seed and tonic shop (`nettle`: tonic, glowseed), plus `frost_bloom`, plus `nettle_circlet` "Nettlecrown's Bean-Circlet" (trinket: +2 HP/s resting regen; 5 thorn damage to the first enemy that hits you each fight; "Wear it. Things grow back. Even you."), and Embassy merit topped up to the next rank (NEED step), capped at Legend. Placeholder icon: alder_charm.
- Music: Mossbrook theme on vanaheim, vh_village, vh_garden, rotwood and verdant; the boss keeps music_boss.ogg.

- Oct 28, 2026, Game Director: Nettlecrown neon look approved; scoped neon palette exception for this boss only, plus the vanaheim-gloom area palette.

## 2026-10-29: GD fun-pass picks (GD approved Oct 29)

- **Mother Nettlecrown** (GD approved Oct 29, unchanged): 1500 HP, 22 dmg, phases at 65 % and 35 %, yields at 5 %.
- **Nettlecrown "thorns close in"** (Will approved Oct 29, via GD): `THORNS_CLOSE_IN = true` (`game/vanaheim_fun.js`). Phase-3 ring of thorn fx closing in is visual only: no arena shrink, no hitbox, collision or damage change.
- **Mossbrook coin-in-the-spring** (GD approved Oct 29; `vanaheim_fun.js` COIN): at the fizzing spring in vh_village (-1.2, 1.4), toss costs 1 Copper bit, or 1 gold if you have none (no toss when broke). Rare line chance 1 in 8 (12.5 %) per toss, repeatable. The Spring-Wish Penny (keepsake, no stats, existing Copper-bits icon) is given once per save: on the first rare line, or on the 8th toss at the latest. Flags: `vh_wish_tosses`, `vh_wish_rare`, `vh_wish_penny`.
- **Bonus seed** (GD approved Oct 29; `vanaheim_fun.js` BONUS_SEED): Nettlecrown's Seed & Tonic Stall, 10 % chance per common-seed purchase (glow seed only) of +1 free glow seed; cap 1 bonus per in-game day (`S.day`), stored in the save as `flags.vh_bonus_day`. Tonics never roll.

Helheim night warm-light (GD, Oct 30 2026): hh_shore gets one Asgard brazier (plus one warm lantern) and ossuary2 gets two (the second added Oct 30, mirroring ossuary's fix1028 brazier); ossuary2's brazier light range is 3.5 m vs the 3 m cap elsewhere (Oct 30: night_warm_frac 0.0027 before, barely over the 0.002 grade; AFTER_PLACEHOLDER) (OK); hh_archive uses three small warm lanterns at the reading desks instead, blue flames stay dominant.
