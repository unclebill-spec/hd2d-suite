# Changelog

Dates are America/New_York. Newest first. Keep this current with every change you push.

## 2026-10-03: Hearthmoor Stage 3, part 3.2 + 3.3: the travelling night merchant, gem sockets
- **Sefa, the travelling night merchant** sets up by the Plaza well only in the night hours (19:12 to 06:00) and packs up at dawn (a little poof each way). Deep hood, night-blue cloak and a **neon-blue cold-fire lantern** that lights the cobbles (a pooled point light) and counts as a light zone (glowlit, wraith-proof). Her **Lantern Pack** shop (same panel and controls as Odo's) sells tonics, the four socket gems and two rarer pieces (Rare + Epic, one level up, always at least one socket), fresh each night, and buys loot back at 1.2x.
- **Gem sockets:** Rare gear rolls 0-2 sockets (mostly 0-1), Epic 0-2 (mostly 1-2), **Legendary always 2**. Gems: **Golem core** (+15 HP, guard -3% dmg), **Rift shard** (+6% spells, +1% crit), Frost core (+12 stamina), Moon opal (+8% summons). Mossheart always drops a golem core; stone golems (10%), frost golems (25% frost core), wraiths and skeleton mages (rift shards) sometimes do. Loose gems lie on the ground as faceted pixel stones and go into a gem pouch (`S.gems`).
- **Socketing in the Gear tab:** a gem line lists what you own (the chosen gem is outlined; "gem ▸", T or RT picks the next one); R (keys), Y (controller) or the row's "socket" button sets it into the chosen piece's first empty socket. Set gems glow in their colour on the item icon (a dithered ring around a 2x2 inlay with a white glint; empty sockets are dark holes) and are listed in the item text (◆ / ◇). Gear-tab icons are now drawn at 3x. Gems stay set (a jeweler to clear them comes later).
- Smoke: shop steps (keys, controller, touch, tonic), night merchant (appears with light + zone at night, gem stock, socketed gear, gone at dawn), Mossheart's golem core, socketing by R and Y, gem stats once equipped.

## 2026-10-03: Hearthmoor Stage 3, part 3.1: Odo's shop in the Plaza
- **Odo the merchant** (Plaza, by the barrels and crates east of the fountain): talk to him to open his shop, a parchment / wood panel like the hero screen. **Buy**: Hearth tonics (12 gold, heal 60 HP), glow seeds (8 gold; kept for the coming glow-gardens) and three pieces of plain gear rolled when you arrive (Common / Uncommon, priced by rarity and level). **Sell**: anything in the gear bag, priced by rarity (always more than scrapping; Epic and Legendary ask "sure?" first).
- Works on all three schemes: keys (← → tabs, ↑ ↓ choose, Enter buy / sell, Esc close), controller (LB / RB tabs, d-pad, A, B) and touch (tap a tab, a row, the buy / sell button, ✕ or outside the card). The field is input-blocked while it is open.
- **Hearth tonics** show in the bag chip with a new pixel icon; drink one with **U**, a **right-stick click**, or by tapping it in the bag.
- Plaza and Bakery Lane sprite sheets no longer carry the enemy sprites (only Mossglen has enemies): Lane 3328 → 2560 px tall, Plaza 2944 → 2432 px.
- Sprites: `nightmerchant` role added (deep hood, night-blue cloak, neon-blue lantern) for part 3.2.

## 2026-10-03: Hearthmoor Stage 3, part 2: new foes, the Mossheart mini-boss, the Legendary aura
- **Frost golem** (Mossglen, east by the hedge): the stone golem re-cut in pale ice with ice spikes and white rune light. Tougher than the stone golem; its slam also **chills** you (drains 18 stamina).
- **Skeleton mage** (Mossglen, south glade): skull under a red hood, long gold-hemmed robe, a crooked staff with a cold-fire orb. Keeps its distance and fires arcane bolts (dodge, guard, or let a summon take them). Not light-shy, unlike the wraiths.
- **Mossheart, the Elder Golem** (Mossglen mini-boss, east clearing): the glowing tier-III golem look (dark ancient stone, amber crystal crown, gold runes all over, glow-flowers in the moss) and it carries its own warm rune light. 460 HP; every third slam is a telegraphed rune shockwave all round it (rune circle on the wind-up; roll through or stay out of range). A named parchment / wood boss bar shows at the top while it fights. It **always drops a Legendary** (plus extra gold) and comes back after 10 minutes. Same sprite scale as every actor (style lock); it reads as a boss through the glow, light and bar.
- **Legendary aura on the hero:** with any Legendary equipped, the same marching neon ring as a Legendary drop circles your feet (the back arc behind your legs is left out) and a warm orange-gold rune light follows you.
- Sprites: `icegolem`, `skelmage`, `eldergolem` in `tools/sprite/roles_enemies.py` (palette-remapped golem / robed skeleton variants; atlases rebuilt). XP: frost golem 55, skeleton mage 36, Mossheart 260.
- Smoke: new steps for the three foes, the chill, the mage bolt, the boss light + bar, the guaranteed Legendary and the hero aura on / off; the part-1 pathfinding step now checks the result (the foe reached the terrace by the stairs) rather than the path length. 88/88 pass. check-scene: plaza 11/11, lane 10/10 (clean re-run), mossglen 11/11 (on 0f8fb68).

## 2026-10-03: Hearthmoor Stage 3, part 1: leftovers + enemy pathfinding
- **Brighter Epic / Legendary drops:** bigger aura (Legendary: two counter-marching rings plus four orbiting sparks; Epic: one ring plus two sparks) and each Epic / Legendary drop now lights the ground around it with a pooled point light in its colour (purple / orange-gold). Still no blur or bloom.
- **Bag chip:** shows "⚔ N" (gear pieces in the bag) and "● gold" next to the errand items, refreshed on pickup, equip, scrap and faint.
- **Mode at New Game:** the hero picker has a "mode:" button (M key, Y / X on a controller, or tap) cycling Story / Adventurer / Hero with a one-line tip; the new save starts in that mode (options can still change it).
- **Enemy pathfinding:** chasing / returning enemies follow an A* path over the area's nav grid (string-pulled, re-planned twice a second) so they walk round walls, fences, terrace edges (via the stairs) and trees instead of sliding along them. Cold-fire wraiths still refuse to path into light.
- Smoke: picker mode step, bag-chip step, a pathfinding step (a skeleton below Mossglen's terrace wall routes by the stairs).

## 2026-10-03: Hearthmoor Stage 2, loot + gear (part 3) and modes, faint penalty, 24-minute day (part 5)
- **Loot:** beaten foes drop a little gold and often an item (weapon, armor or trinket) in one of five rarities: Common (white), Uncommon (green), Rare (blue), Epic (purple), Legendary (orange-gold). Every item drop stands under a crisp pixel beam in its colour with rising motes; Epic adds a faint stepped glow ring, Legendary an animated neon aura (marching pixels cycling orange / gold / white / rose). Walk over a drop to pick it up (the toast names it in its colour; gold pops as a pixel number).
- **Gear page:** a fourth hero-screen tab, Gear (G): weapon / armor / trinket slots plus a 30-item bag. Enter / A / "equip" swaps an item in, "take off" puts it back, X / "scrap" turns it into gold. Rarity-coloured names; Epic rows glow faintly, Legendary rows have the animated neon edge. Gear adds melee / spell %, HP, guard, crit, stamina and (Epic+) summon power through the same stat system as levels. Saved as `bag`, `gear`, `gold` (old saves start empty; old coins become gold).
- **Modes:** options `mode:` Story / Adventurer / Hero (`?mode=`). Story: foes hit 40% softer, you hit 15% harder, no faint penalty. Hero: foes hit 35% harder, you hit 10% softer, better loot odds.
- **Faint penalty** (Adventurer and Hero): fainting drops 10% of carried gold as a purse where you fell. It stays there (also across area changes and saves) until you walk back over it. Story mode: nothing lost.
- **24-minute day:** a whole day / night cycle now takes 24 real minutes (was 12).
- Smoke: dawn check uses midday (the run can already be at night); new loot / gear / faint / Story steps. 78/78 pass.
- Bakery Lane: one toadstool cluster moved off a spot behind the flower shop (it showed over the roof) to the open front-left corner.

## 2026-10-03: Hearthmoor Stage 2, spellbook + controller spell wheel (part 2 of 5)
- **Spellbook:** a third "Spells" tab on the hero screen (B opens it straight away; or I / the vitals chip / Start, Y on a controller, then → / RB). Four slots; Enter / A / "change" cycles a slot through every spell you know (your class spell + each charm; slots 2-4 can be empty). The cast cycle (F, Q, 1-4, LB / RB, the wheels) follows at once; saved as `slots` in the v2 save (old saves keep the default: class spell + newest three charms). A newly learned charm fills an empty slot.
- **Controller hold-for-wheel:** tap Y casts (on release); hold Y for a third of a second opens the same slow-time spell wheel as the touch ✦ button, the left stick or d-pad picks a slot, letting go of Y casts it. The field is input-blocked while the wheel is open.
- Hint line: "B spellbook", "Y cast (hold: spell wheel)".

## 2026-10-03: Hearthmoor Stage 2, glow pass (part 4 of 5)
- **Spell light pools:** every hero spell and charm leaves a short pool of light where it lands (about 1.8 s): a dithered gold ground decal (`light_pool`), twinkling glitter motes rising out of it (`glitter`) and a real point light in the spell's own colour. No bloom: all palette pixels and point lights.
- **Glowing toadstools at night:** red-and-white toadstool clusters come out between 19:12 and 06:00 in Mossglen (6), Market Square (4) and Bakery Lane (4). Their white spots twinkle, spores drift up, and each casts a soft rose pool of light; at dawn they dither away.
- **Light is a place:** standing in a light zone (a lit lamp post, stone lantern, shrine, shop window, toadstool or spell pool) makes you **glowlit**: +10% damage and 1.5x stamina regen, shown as "✦ glowlit" and a gold rim on the vitals chip. Cold-fire wraiths will not drift into light, slip out of it if a pool blooms under them, and hold their fire while you stand lit.
- **Engine:** `ctx.addGlow(x, y, z, {color, intensity, range, life, fadeIn})` gives games a small fixed pool of point lights (3, made at boot so shaders never recompile) for the strongest glows near the camera; every glow also warms nearby sprites like a lamp. Effects take `fadeIn` (dither in). `ctx.lamps` is exposed.
- New spells-atlas effects (`tools/spells/spells.py`): `light_pool`, `glitter`, `toadstools`.

## 2026-10-03: Hearthmoor Stage 2, part 1: leveling (+ review fixes)
- **Review fixes:** the toast is a brief fade below the top HUD row (never over buttons, never takes taps); the inventory shows once (bag chip; the pad rail is empty); the see-through silhouette has a solid 1-texel ink outline around the dither; the golem's side view is a hunched stone block with a brow ridge and a long hanging arm (no more bird); check-scene's effects lineup hides quest tags, so Plaza `effects_sharp` passes.
- **Leveling (`game/progress.js`):** XP from enemies (golem 45, wraith 34, skeleton 28, +50% the first time you beat each kind) and errands (120); level cap 50; six stats (Might, Arcana, Spirit, Vigor, Grit, Swiftness) with class starting values; 2 free stat points + 1 skill point per level.
  - A new game asks **"Auto level? Yes / No"** (Yes = the class spends the points along its lean, No = spend them yourself); toggle in options (`auto level: on/off`). `?autolevel=1|0` skips the ask.
  - **Hero screen** (I, tap the vitals chip, or Y / LB / RB inside the quest log on a controller): Stats tab (+ buttons) and Skills tab with tier I of each hero's three branches (E3), e.g. Stormborn Charged Hammer / Forked Bolt / Storm Sprite II, Cinderknight Life Drain, Seer Long Step.
  - Stats feed combat: melee / spell / summon / heal multipliers, max HP (Vigor), guard strength and stamina (Grit), stamina, roll distance and crits (Swiftness). Crits pop in gold.
  - Level-up: sparkle burst, bloom ring and a light-orb pool at your feet, full heal, a toast, the vitals chip flashes. The vitals chip has a level + XP bar.
  - Saves stay `hearthmoor-slot-1-v2`; the new fields (`lv`, `xp`, `stats`, `free`, `sp`, `skills`, `autoLevel`, `bestiary`) are filled with defaults when an older v2 save loads.

## 2026-10-03: Hearthmoor Stage 1: platform polish, 6 playable heroes, real-time combat core
First build stage from the builder handoff (M0 + M1 + the start of M2). Playable on Pages.
- **Platform (M0):**
  - an options card (O / ⚙ chip, also on the title) with display presets: Auto, Phone landscape (DPR cap 1.5), 720p, 1080p TV (bigger HUD, TV-safe inset), Retro 320x240 (4:3 letterbox, chunky integer pixels). Saved as `hd2d-display`, or `?display=`;
  - fullscreen button, an in-game Install button (`beforeinstallprompt`; iPhone / iPad get an "Add to Home Screen" tip), a rotate-to-landscape banner on upright phones;
  - the LT double-map is gone: LT is a held guard, RT summons, and zoom moved to the right stick;
  - a see-through silhouette: a dithered plaster-colour ghost of the player shows through buildings and trees (second quad with an inverted depth test; no blur).
- **Heroes (M1):**
  - New game opens a hero picker with the 6 starters (name, origin, mortal / demigod, blurb, animated sprite preview from the atlas, first spell and summon). It works with keys, controller and taps. The chosen class is the player;
  - the game atlases were regenerated with the hero anims plus the new enemy and summon roles;
  - phone action buttons: MAIN (attack / talk) plus guard, jump, roll, ✦ spell (tap casts, hold opens a slow-time spell wheel), summon and log, pixel icons from `art/buttons.png`, mirrored for left hands;
  - save is now `hearthmoor-slot-1-v2` (class + HP). Old `hearthmoor-slot-1-v1` saves still load: Continue asks for a hero once, then everything carries over (the v1 key is left alone).
- **Combat core (M2 start), `game/combat.js` + `game/heroes.js`:**
  - HP and stamina (parchment vitals chip), melee hitboxes on the impact frame, crisp 3x5 pixel-font damage numbers, enemy HP bars;
  - guard cuts frontal hits to a quarter; the dodge roll is a pixel-exact tumble with 0.26 s of i-frames; defeat is cozy (wake at the area start, full HP, a moment of grace, nothing lost);
  - three gloom-and-glow enemies in Mossglen: a stone golem, a skeleton swordsman and a blue cold-fire wraith (ranged), plus a second wraith at night. They wander, aggro, telegraph, leash home and respawn;
  - each starter has a first spell (Seed Bomb, Rune Slam, Rune Trap, Chain Lightning, Bloom, Ember Slash) and a first summon (mushroom golem, rune sentinel, rune wisp, storm sprite, sapling, ember imp). The 4 spell slots are the class spell + the newest 3 charms; charms do small damage too;
  - new SFX: swing, hit, hurt, guard, dodge, spell, summon, defeat, down.
- **Tools:**
  - `hd2d sprite`: new `roles_enemies.py` (golem / wraith / skeleton with idle / walk / attack / die, and 6 summons), `--roles combat`, a `die` anim;
  - `hd2d spells`: combat effects (seed bomb, earth burst, rune slam, rune trap, glyph burst, sky strike, bloom ring, ember slash / pop, cold-fire bolt, hit spark, summon poof), glow pixels only;
  - `hd2d assemble`: a `sprite_roles` spec key;
  - engine: `dodge`, `summon`, spell-slot select, `timeScale`, hit flash and roll rotation in the sprite shader, x-ray silhouette quads, display presets, press / release for every pad button, the effects QA lineup wraps to at most 3 rows.
- Small: Marla / Bram / Wren no longer call every hero a hedgewitch; the vitals chip sits under the bag whatever its height; in QA stills (`?qa` without `&combat`) enemies hold still and the night wraith doesn't spawn, so check-scene captures stay deterministic.
- Tests: the smoke test (64 steps, PASS) now covers the hero picker, Mossglen combat (hit, guard, roll i-frames, spell, summon, defeat / respawn), the new controller map, phone action buttons and the spell wheel, and the v1 → v2 save migration. `RESTORE.md` and `AGENTS.md` (game section) are updated.

## 2026-10-03: design expansion (opening hour, main quest, skill trees, difficulty, day/night, Ravenhold, music)
- New `docs/story/DESIGN_EXPANSION_2026-10-03.md` (Bill approved), also appended to `docs/story/STORY_SEEDS.md`. Seven sections:
  - E1 opening hour: Lantern Eve in Hearthmoor, tutorial beats (move, talk, errands, first fight, guard / dodge / jump, first spell and summon), six origin openings, the Rift cracking, leaving home;
  - E2 main quest: prologue, Acts 1–3, the finale, Veyra's appearances and reveal, the Saver/Breaker choice, the betrayal (Gatewright Halvard), the one side-switch window, how each of the 4 endings is reached, where the optional dungeons and superbosses fit;
  - E3 leveling: cap 50 (+10 per NG+ cycle, max 70), six stats, 3-branch skill trees for the six starters, realm school trees, summon tiers, respec;
  - E4 fainting (recoverable 10% carried gold), Story / Adventurer / Hero / Saga modes, boss retry, New Game+ carry-over, the Hall of Heroes;
  - E5 a 24-minute day, night changes, weather per realm, weekly festivals;
  - E6 Ravenhold's Forge Quarter, Old Temple (home of the Rift-gate) and Market Terraces (NPCs, shops, quests), with a consistency check of the Harbor and Undercity;
  - E7 music and sound direction, leitmotifs, per-realm instruments, the layers, day vs night, UI / SFX rules (original only).
- Not yet merged into `docs/HEARTHMOOR_BUILDER_HANDOFF.md` (at Bill's request; that happens at the end of the session). `AGENTS.md` points to the new file.

## 2026-10-03: storyboard decisions
- docs: handoff section 11 now records the storyboard decisions (combat style, Glimmerdeep, Verdant Heart nature dungeon, 10 rift types with signature bosses, factions, names, companions, mechanical pet).

## 2026-10-02: consolidated Hearthmoor builder handoff
- New `docs/HEARTHMOOR_BUILDER_HANDOFF.md`: one game design document for the Master Builder, merged from `STORY_SEEDS.md`, `AGENTS.md`, this changelog, the style lock, the tool READMEs and the code. Sections: pitch and pillars, style lock, platform/input requirements, story, world, heroes (6 + 9 = 15), bestiary, dungeons and rifts, progression and economy, current build status, open decisions, suggested milestones and repo rules, plus an appendix of resolved contradictions (later drafts win).
- No new design. Superseded drafts resolved (e.g. one static dungeon per realm instead of 1–2, Wildcaller casts, flesh/blood golems gross only in the Plaguewell).
- `AGENTS.md` links the handoff and now says the game player is the `hedgewitch` role (the code), not the traveler.

## 2026-10-02: hero action sets (cast / attack / defend / jump) and runtime action states
- `hd2d sprite`: every hero class now has **four 4-frame action anims in all four facings** (down, up, left drawn; right is the mirrored left):
  - **cast** (cols 8–11): a spell with crisp glow pixels for every class (brawlers now cast too: Runeguard light rune, Stormborn lightning, Cinderknight ember flame; Wildcaller lifts a hearth-light orb);
  - **attack** (cols 12–15): melee with the class weapon (hoe chop, axe chop + shield bash, staff sweep / thrust, hammer swing with ground sparks, Grovekeeper vine lash, greatsword ember slash);
  - **defend** (cols 16–19): raise, set, hold a / hold b (Runeguard shield up and centred with the rune lit; Wildcaller / Seer / Grovekeeper a small ward glyph; Stormborn hammer and Cinderknight greatsword held crosswise);
  - **jump** (cols 20–23): crouch, launch, airborne, land (dust pixels on landing). Frames stay feet-anchored; the runtime adds the height.
- Hero strips are now 24 columns (480 px); villager strips stay 12 columns, and an atlas is as wide as its widest role (`meta.cols`).
- Pixel identity: the idle / walk columns of all six heroes and all 24 villager roles (per-role PNGs byte-identical) match the previous build. Palette caps hold (Wildcaller still 20 colours).
- `actors.json`: new `meta.anims` entries `attack`, `defend` (with `hold: [2, 3]`) and `jump` (with `phases`), all `heroes_only`; hero roles list `anims` = idle, walk, cast, attack, defend, jump and carry `cls` / `origin` / `style` (the old `pose` key is gone).
- New CLI: `--anim-lineup PATH [--anim-facing F]` writes a 4x action sheet (rows cast / attack / defend / jump, 4 frames per hero, dark panel; the jump row previews the arc with a ground shadow).
- Screenshots: `docs/screenshots/hero_anims_4x.png` (down), `hero_anims_side_4x.png` (left), `hero_anims_up_4x.png` (up).
- Runtime (`engine/sprites.js`, `engine/main.js`):
  - `Actors.act(a, 'attack' | 'defend' | 'jump' | 'cast', {hold, dur})` and `release()`. Jump works for every role (villagers hop on idle frames); the others need the anim.
  - The jump lifts only the visible quad (`lift = 0.55 m * sin`, crouch 0.1 s, air 0.46 s, land 0.12 s); depth and the shadow caster stay on the ground. Landing kicks footstep dust.
  - Keys: **R** attack, **C** hold to guard, **Z** jump. Controller: **RS** attack, **LS** jump, **LT** short guard. No walking during attack / guard; a jump keeps moving.
  - API: `window.__hd2d.act(name, id?, opts)`, `release(name, id?)`, `actorState(id?)`, `actAdvance(sec, id?)` (QA).
  - Copied into `demos/*/engine` and `games/hearthmoor/engine` (zips rebuilt). Their atlases were not regenerated, so the game player (traveler) only has the jump.
- check-sprite: the frame count now comes from each role's `anims`, and every extra anim must differ from idle in every facing.
- Checks: check-sprite PASS (heroes alone, all 30 roles, the review-scene atlas, both demos and all 3 game areas). check-scene PASS on the review scene (hero player: jump, attack and defend), both demos and all 3 game areas (jump on non-hero players). Smoke test PASS 46/46.
- check-scene: Playwright's default timeout now follows `--timeout` (screenshots on a loaded shared box stalled past 30 s).
- check-scene: new `actions` check: with the sim held, a jump is stepped in fixed game time; the sprite must lift (≥ 0.2 m, its screen rect rises) while the shadow caster stays at the feet, then land and end. Hero players also need ≥ 2 attack frames and a held defend reaching its hold frames, ending on release.

## 2026-10-02: hero classes (Norse Nine Realms) and story seeds
- Story: Hearthmoor is now a Norse Nine Realms story. The seeds live in `docs/story/STORY_SEEDS.md` (committed for the first time). It holds:
  - the three original pitches and the chosen direction (realms linked by the Rainbow Rift);
  - the villain Veyra Ashmantle and the realm alliance map;
  - the hero origins, plus the newer **Cities** section (the Bifrost Crossing hub and one city per realm);
  - world structure, pets, and the look-and-feel priority (gloom-and-glow, neon, still no bloom);
  - **Heroes and magic**.
- `hd2d sprite`: **6 new hero classes** (30 roles total), in the new module `tools/sprite/roles_heroes.py`:
  - **Wildcaller** (Midgard farmhand): blond, rust tunic, rolled sleeves, satchel, long hoe; hearth sparks.
  - **Runeguard** (Shield-warden, paladin brawler): chestnut braids, mail and leather, axe, a round shield whose light rune glows.
  - **Seer** (Rune-reader): grey hood with a stitched back rune, rune-stone pouch, rune staff; rune glyph glow.
  - **Stormborn** (Child of thunder, brawler): bulkier `broad` layout, storm-blue cloak, silver circlet, stone war-hammer; lightning.
  - **Grovekeeper** (Child of the Vanir): moss-green hair, flower crown, leaf mantle, mushroom charms; neon-green heal.
  - **Cinderknight** (Ember-born, dark-knight brawler): bulky dark plate with a glowing ember seam, flame-tuft hair, ash cheek marks and hands, greatsword with an ember edge.
- **Hero frames:** the same 20x32 spec (4 facings × idle 4 + walk 4, hard alpha, 1 px outline, big head), plus a 4-frame action in the cast columns:
  - casters cast;
  - brawlers swing with a solid swoosh arc (dust and sprout for the hoe, an ember flame aura for the greatsword).
  - The glow is crisp emissive pixels only.
- **Hero metadata:** heroes carry `hero`, `origin` and `pose` in `actors.json`.
- **New CLI options:**
  - `--roles heroes` builds just the six;
  - `--lineup PATH` writes a labelled 4x nearest lineup.
- The 24 existing roles are pixel-identical.
- New review scene `scenes/hero-classes-plaza.json` (all six on the plaza at golden hour, frozen clock).
- Screenshots: `docs/screenshots/hero_origins_4x.png` (lineup) and `docs/screenshots/hero_origins_plaza.png` (in-scene).
- Checks: check-sprite PASS (heroes alone and all 30 roles). check-scene PASS on the review scene (all 8 checks, including sprites_sharp on 21 actor crops and the phone check).

## 2026-10-01: docs for builder handoff
- Added `AGENTS.md` (handoff guide for Cursor and Bill's bots), this `CHANGELOG.md`, and `docs/HD2D_COZY_STYLE_LOCK.md` (Bill's style law, copied into the repo).
- `README.md` and `games/hearthmoor/RESTORE.md` link all three.

## 2026-10-01: GitHub and Pages
- Published to https://github.com/unclebill-spec/hd2d-suite (public) after a secret scan (rg regexes + gitleaks on the tree, zips and history: clean).
- GitHub Pages (main, root) with a root `index.html` linking the game and both demos. `.nojekyll` added.
- `.gitignore` keeps out the `shots/` and `iterations/` QA folders (~54 MB, regenerated by the checks) and `__pycache__`. A small curated set lives in `docs/screenshots/`.
- README opens with a play-online / run-locally quick start.

## 2026-10-01: input polish (Hearthmoor and the shared runtime)
- **Controller:** new `engine/gamepad.js` (Gamepad API, standard mapping).
  - Walking: stick and d-pad walk with analog speed.
  - Buttons: A talk, B close, X cast, Y / LB / RB charm, LT / RT zoom, Start menu or quest log, Select pad.
  - Hot-plug toast. The on-screen pad hides while a controller is used and comes back on touch.
  - Games can take buttons first with `hooks.onPad`.
- **Floating stick:** it appears under the thumb in the movement zone, follows the finger and re-centres past its rim. Analog walk, the rim runs, and a left-handed mirror is available.
  - A quick tap in the zone still walks there.
  - Pinch works even when one finger lands in the zone.
- **No page scroll or zoom:**
  - blocked: iOS gesture events, double-tap zoom, pull-to-refresh / overscroll, ctrl+wheel and long-press menus;
  - `touch-action: none` on the canvas.
- **Loading gate:** every input is swallowed until the area's first frames are drawn. The `#boot` overlay sits above the title, so early taps can't queue walks or skip the title.
- **Hearthmoor title:**
  - works with a controller;
  - "press New game twice" replaces the browser `confirm()` dialog.
- Fixes:
  - The item rail no longer overlaps the chip column on mid-height screens.
  - `build.py --skip-assemble` now copies the current runtime, not a stale one.
  - The check-scene effects lineup hides particles, so fireflies can't fail it.
- **Tests:**
  - check-scene phone check: new `floating_stick`, `no_page_zoom`, `loading_gate` and `gamepad` sub-checks.
  - Smoke test: 46 steps, including a stubbed controller (`tests/gamepad_stub.js`), the floating stick, taps during loading, and keyboard + mouse working alongside a controller.

## 2026-10-01: Hearthmoor, the first game (`games/hearthmoor/`)
- Three areas:
  - Hearthmoor Plaza and Bakery Lane, joined by edge / stair exits with a fade;
  - Mossglen, a glade reached through a stone-arch moss gate with a swirling vortex. The portal art is drawn fresh in the cozy palette; the Gravewake rift refs were a style reference only.
- Three errands (Warm Bread, Moonpetal Tea, Where's Pudding?).
- Parchment / carved-wood dialogue with portraits, a quest log, a bag, quest tags, and Pudding the cat following you between areas.
- Real-time day / dusk / night, and charms as rewards (spell keys kept).
- Procedural WebAudio ambience.
- Save / load to localStorage `hearthmoor-slot-1-v1`.
- PWA (manifest, icons, offline service worker).
- Phone play: tap, pinch, Layout One pad.
- `build.py`, playable zip `games/hearthmoor.zip`, `RESTORE.md` with a do-not-regress list, and the Playwright smoke test.
- New tool `hd2d portal`: portal vortex, rune ring, moonpetal and quest-tag effects.
- New kit glade pieces: portal arch, shrine, standing stone, stone lantern, mushroom ring, fern bush.

## 2026-10-01: fixes and phone checks
- Ground decals (rune circle, portal ring) now write per-fragment ground depth, so they sit under props and actors.
- Tap-to-walk uses A* (`engine/nav.js`) over the heightfield, terraces and stairs, going around walls and props.
- Left-handed Layout One pad: `?pad=1&hand=left`, the H key or the `hand` chip, remembered per device.
- check-scene got a `phone` check (portrait 390x844 + landscape 844x390, DPR 2, touch). It found and the runtime now fixes:
  - small chips;
  - the button column running into the pad in short landscape;
  - taps dropped on slow frames.
- Rain splashes and footstep dust are more readable, still cheap, still no bloom.
- Screenshot-review fixes: the quest log ignoring `hidden`, the hint under the dialogue, the toast over the title on phones, the coin icon, faceted hills, the black fern, and occluded spawns.
- Runtime embedding for games: `boot()` / `dispose()` and hooks; NPC `follow` behaviour; lamp `color` / `fixed`; emitter `min_gate`; `?simscale`.

## 2026-09-30 / 2026-10-01: Bakery Lane, new roles, spells, particles
- Demo **Bakery Lane at Dusk** (`demos/bakery-lane`, `scenes/bakery-lane.json`): two terrace levels and stairs, the bakery and the Kettle & Key inn, a flower shop, laundry lines, a fountain, fireflies and 7 NPCs.
- **14 new sprite roles** (24 total), including magic users with 4 cast frames per facing.
- **Spells** (`hd2d spells`): 9 pixel spell effects with frame strips, presets and cast sets. F casts, Q switches, and the pad's ✦ casts on tap and switches on hold.
- **Particles:** 16 presets (fireflies, petals, snow, rain + splashes, embers, oven steam, pollen, fountain spray, butterflies, footstep dust, …) and the `?showcase=particles` grid.

## 2026-09-30: initial toolset and the Hearthmoor Plaza demo
- `bin/hd2d` CLI with the first tools:
  - `palette`: 5 biomes × 27 colours + grades;
  - `sprite`: 20x32 actors with 4 facings, idle 4 + walk 4;
  - `check-sprite`, `runtime` (three.js r160 diorama engine), `texel`, `kit`, `trees`, `particles`, `assemble`, `check-scene`.
- Demo **Hearthmoor Plaza** (`demos/hearthmoor-plaza`, `scenes/hearthmoor-plaza.json`):
  - a terraced village square, locked 3/4 camera, tilt-shift, one sun plus flickering lamps, sprite shadows;
  - day / dusk / night;
  - Layout One pad.
