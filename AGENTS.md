# AGENTS.md: handoff guide for hd2d-suite

Bill (GitHub `unclebill-spec`) hands this project between his bots and Cursor through GitHub. Read this file first, then `CHANGELOG.md`.

**Building Hearthmoor? Start with [`docs/HEARTHMOOR_BUILDER_HANDOFF.md`](docs/HEARTHMOOR_BUILDER_HANDOFF.md)**: the one consolidated game design document (pitch, style, platform, story, world, heroes, bestiary, dungeons and rifts, economy, build status, open decisions, milestones).

**New design (2026-10-03, Bill approved):** [`docs/story/DESIGN_EXPANSION_2026-10-03.md`](docs/story/DESIGN_EXPANSION_2026-10-03.md) (also appended to `STORY_SEEDS.md`): opening hour, main quest beats, leveling and skill trees, death / difficulty / New Game+, day-night and weather, Ravenhold's Forge Quarter / Old Temple / Market Terraces, music and sound. Not yet merged into the handoff; read it alongside it.

## Before you start / before you stop
1. **`git pull` first**, every time you resume.
2. Keep `CHANGELOG.md` (dated America/New_York entries) and this file current.
3. Write descriptive commit messages (`area: what changed and why`).
4. **Secret scan before every push**:
   - rg regexes for gh/ghp_/gho_/github_pat_ tokens, AWS/Google keys, private keys, password/token assignments and `.env` / credential files;
   - **gitleaks** on the tree and on the git history.
   - If anything real turns up, don't push; report it.
5. Run the checks and the smoke test (below) before pushing code changes. They must pass.

## Current state (2026-10-02)
- **Story direction:** Hearthmoor is becoming a **Norse Nine Realms** story (original art and characters, public-domain myth). Read [`docs/story/STORY_SEEDS.md`](docs/story/STORY_SEEDS.md) before touching story, quests or characters. It covers realms, cities, the villain Veyra, alliances, heroes and magic, pets, and the look-and-feel priority.
- **Hero classes:** `hd2d sprite` has 6 playable classes (`roles_heroes.py`: wildcaller, runeguard, seer, stormborn, grovekeeper, cinderknight).
  - Each has idle, walk and four 4-frame action anims in all 4 facings (right = mirrored left): **cast** (cols 8–11), **attack** (12–15), **defend** (16–19, hold frames 2/3) and **jump** (20–23: crouch, launch, airborne, land). Hero strips are 24 columns; villagers stay 12.
  - Lineups: `docs/screenshots/hero_origins_4x.png` (looks), `hero_anims_4x.png` / `hero_anims_side_4x.png` / `hero_anims_up_4x.png` (actions). In-scene: `docs/screenshots/hero_origins_plaza.png`. Review scene: `scenes/hero-classes-plaza.json` (player = stormborn).
  - **Runtime action states:** `Actors.act(a, name, {hold, dur})` / `release(a, name)` in `engine/sprites.js`. Keys **R** attack, **C** hold guard, **Z** jump, **X** dodge roll; controller **X / RS** attack, **LS** jump, **LT** held guard, **B** roll. The jump lifts the visible sprite only (`a.lift`); the shadow caster and depth stay on the ground. API: `__hd2d.act / release / actorState / actAdvance / dodge`.
  - **Stage 2 part 1 (2026-10-03):** leveling in `game/progress.js` (XP, cap 50, six stats, 2 free points + 1 skill point per level, auto-level Yes / No ask + options toggle, tier I of each skill tree) and the hero screen (I / vitals chip / Y-LB-RB in the log).
  - **Stage 2 glow pass (2026-10-03):** `game/glow.js`: spell light pools (light_pool decal + glitter + `ctx.addGlow` point light), night toadstools per area (`TOADS`), light zones (lamps / toadstools / pools) → glowlit buff (+10% dmg, 1.5x stamina) and wraiths (`shy`) avoid light. Engine `ctx.addGlow` = 3 pooled PointLights + sprite warmth.
  - **Stage 2 spellbook (2026-10-03):** hero screen tab 3 "Spells" (B) assigns the 4 slots (`G.S.slots`, `slotSpell`, `knownSpells` in game.js); controller hold Y (0.35 s) opens the slow-time wheel (`PADW` / `padWheel`, `hooks.onPadRelease` casts on release).
  - **Stage 2 loot + modes (2026-10-03):** `game/loot.js` (RARITY x5, makeItem, DOM pixel beams / Epic glow / Legendary aura pinned via ctx.project, bag 30 + gear slots, equip / scrap, gold, faint purse); hero screen tab 4 Gear (G); `progress.js` MODES (story / adventurer / hero) + gear folded into `mods()`; day = 1440 s. Stage 2 is complete.
  - **Stage 3 part 1 (2026-10-03):** picker mode button (`pickMode`, `PICK.mode`), bag chip gear / gold counts, brighter Epic / Legendary drop auras + drop point lights (`ctx.addGlow`), enemy pathfinding (`Combat.seek`, nav A*).
  - **Stage 3 part 2 (2026-10-03):** new foes in `heroes.js` `ENEMIES` + `SPAWNS.mossglen`: `icegolem` (slam `chill` drains stamina), `skelmage` (ranged, `bolt: 'bolt'`), mini-boss `eldergolem` "Mossheart" (`boss`, `wave` shockwave every 3rd slam, `legendary` guaranteed drop via `loot.onKill(a, lv, {legendary})`, `respawn` 600 s, own `ctx.addGlow` light, `#bossbar`). Sprites are palette-remap variants (`_Remap`) in `roles_enemies.py`. Legendary equipped -> `Loot.playerAura` (worn ring + following light). Next: shops + gem sockets, skill tiers II-III + summon tiers, Toadstool Hollows.
  - **Stage 3 part 3 (2026-10-03):** `game/shop.js`: `Shop` panel (`#shopui`, `G.shop` blocks input, `G.shopUI.show(id)` / `.key` / `.pad`), `SHOPS`, `GOODS` (tonic, glowseed), `MERCHANT` NPCs spawned per area (`attach`), buy / sell prices by rarity (`buyPrice`, `sellPrice`), `drinkTonic` (U / RS click / tap). Plaza + Lane `sprite_roles` list summons explicitly (no enemy sprites). Night merchant: `NIGHT_MERCHANT` (spawned / removed in `Shop.update` by the night window, own `ctx.addGlow` lantern, `glow.zones()` src `lantern`), shop `night` sells gems. Sockets: `loot.js` `GEMS`, `rollSockets`, `socketGem`, `it.gems` (null = empty), gem mods folded in `gearMods`, `iconCanvas(kind, rar, scale, gems)`; Gear tab `heroSocket` (R / Y / button) + `gemCycle` (T / RT).
  - **Boss scale (2026-10-03, style lock BOSS SCALE OVERRIDE):** mini-bosses / rares are ~2.5x the hero, bosses 5x+, and are drawn **natively** at that size (more pixels, same texel density; never upscale a small sprite). Draw them in `tools/sprite/boss_sheet.py` (`BOSS[role]`: frame size, `scale`, anims; same column layout as the actor atlas), list them in the area spec's `boss_roles` (assemble writes `boss.png` / `boss.json` and a stub `{sheet: 'boss'}` role in `actors.json`; `build.py` ships the sheet). The engine picks texture / frame size / pivot per role (`Actors.sheetOf`). Give the foe a `scale` in `ENEMIES` and author its `r`, `reach`, `wave.r` for that size; combat scales light, slam dust, bar height and nav clearance from `scale`, and calls `ctx.framePull` to pull the camera back while it fights. Mossheart (`eldergolem`, 50x80) is the first.
  - **Lantern / glow cap (2026-10-03):** Sefa's lantern = `coldfire_pool` decals x3 + `coldfire_motes` x2 + a power-11 blue `ctx.addGlow` (kept in `shopUI.nm.fx`, dithered out by `dropLantern`). Options `#btnGlow` sets `glowLights` for `boot` (`glowCap()`: `?glow=`, else localStorage `hearthmoor-glowlights`, else 2 on coarse pointers / 3); `ctx.glowN` reports it.
  - **Part 4 skill + summon tiers (2026-10-03):** `progress.js` `TREES[cls]` = 9 nodes (`tier` 1-3, `req`, ordered tier I, II, III so tier-I rows keep their indices), `TIER` costs / level gates, `lockOf(S, node)` (why not learnable), `learn` charges the tier cost, `summonTier(S)` = 1 + learned summon-branch nodes (max IV). New mods: `spellCd`, `critDmg`, `stRegen`, `summonCd` (applied in combat.js). Summons: tier II+ get a following `ctx.addGlow` + glitter, tier III+ use the radiant `<role>_r` sprite (`roles_enemies.py` `_radiant`, in every area's `sprite_roles`), tier IV adds a sparkle burst. `G.PR` exposes progress.js for tests.
  - **Part 5 Toadstool Hollows (2026-10-03):** area `hollows` (`areas/src/hollows.json`, in `build.py` `AREAS` + game.js `AREAS`). Mossglen `game.exits` east rect -> `from_mossglen`, Hollows west exit -> Mossglen `from_hollows`. `glow.js` `ALWAYS[area]` keeps the toadstools lit at every hour, and `POOLS[area]` holds standing light / cold-fire pools (light zones, `src: 'pool'`). `game/hollows.js` `Hollows` handles bounce toadstools from `game.bounces` (jump inside 0.85 m -> a scripted arc to `to`; `busy()` blocks input; first landing with `secret` toasts and sets `S.found[id]`). Kit pieces live in `tools/kit/kit_hollows.py`. Violet comes from lights and grades only, never the palette. Next steps: gnome doors + gnome NPC, the hidden bubbly spring (on the ledge), and dark-hour cold-fire braziers.
  - **In the game (Stage 1, 2026-10-03):** the title opens a hero picker for the 6 starters and the chosen class is the player (saved in `hearthmoor-slot-1-v2`). Real-time combat lives in `game/combat.js`: 3 enemies in Mossglen (stone golem, skeleton swordsman, cold-fire wraith, plus a night wraith), HP / stamina, guard, dodge-roll i-frames, pixel damage numbers, a class spell + summon per hero, cozy defeat. Enemy + summon sprites: `tools/sprite/roles_enemies.py` (`hd2d sprite --roles combat`); combat VFX: new `tools/spells` effects.
- **Toolset:** a Python CLI `bin/hd2d` with 13 tools, which generates original pixel art and assembles lit three.js r160 dioramas (static ES modules, no build step).
- **Demos:** `demos/hearthmoor-plaza`, `demos/bakery-lane` (+ zips).
- **Game:** `games/hearthmoor/`:
  - title → hero picker (6 starters); 3 areas (Plaza, Bakery Lane, Mossglen through a portal), 3 errands, dialogue, quest log, bag;
  - real-time action combat in Mossglen (attack / guard / jump / dodge roll, 4 spell slots, summon, slow-time spell wheel on the phone);
  - real-time day / dusk / night, charms, save / load (`hearthmoor-slot-1-v2`, migrates v1), PWA with an in-game Install button (iPhone: Add to Home Screen tip);
  - options card: display presets (Auto / Phone landscape / 720p / 1080p TV / Retro 320x240), fullscreen, sound, pad, hand; rotate-to-landscape prompt; see-through player silhouette behind buildings;
  - touch with a floating stick + action buttons, Bluetooth / USB controller (no button double-mapped: zoom is on the right stick), keyboard + mouse.
  - Zip: `games/hearthmoor.zip`. Restore kit and do-not-regress list: `games/hearthmoor/RESTORE.md`.
- **Live on GitHub Pages:**
  - index: https://unclebill-spec.github.io/hd2d-suite/
  - Hearthmoor: https://unclebill-spec.github.io/hd2d-suite/games/hearthmoor/
  - Plaza demo: https://unclebill-spec.github.io/hd2d-suite/demos/hearthmoor-plaza/
  - Bakery Lane demo: https://unclebill-spec.github.io/hd2d-suite/demos/bakery-lane/
  - Pages serves `main` at the repo root, so pushing to `main` redeploys. All game paths are relative: keep it that way, because the site lives under `/hd2d-suite/`.

## Repo layout
| Path | What |
|---|---|
| `bin/hd2d` | CLI entry: `hd2d <tool> ...` |
| `tools/<name>/` | One tool per folder, each with its own README: palette, sprite, check-sprite, runtime, texel, kit, trees, particles, spells, portal, assemble, check-scene (+ `serve` in the CLI) |
| `tools/runtime/web/` | **The shared engine** (`engine/*.js`, `hud.css`, `index.html`, `vendor/` three r160). Change it here, then copy into `demos/*/engine` and `games/hearthmoor/engine` (`build.py` does the game) |
| `hd2d_common/` | Shared Python helpers (`load_tool`) |
| `scenes/*.json` | Demo scene specs (+ `hero-classes-plaza.json` review scene) |
| `demos/<name>/` | Assembled demos (static) |
| `games/hearthmoor/` | The game: `index.html`, `game/` (game.js, data.js, heroes.js, combat.js, audio.js, game.css), `areas/<id>/` (built), `areas/src/*.json` (area specs), `build.py`, `tests/smoke.py`, `startup.sh`, `RESTORE.md` |
| `docs/HD2D_COZY_STYLE_LOCK.md` | Bill's style law (binding) |
| `docs/HEARTHMOOR_BUILDER_HANDOFF.md` | Consolidated builder handoff / game design document (start here to build the game) |
| `docs/story/STORY_SEEDS.md` | Story bible: Norse Nine Realms direction, villain, alliances, cities, heroes and magic, pets, plus the 2026-10-03 design expansion |
| `docs/story/DESIGN_EXPANSION_2026-10-03.md` | Design expansion E1–E7 (opening hour, main quest, skill trees, difficulty / NG+, day-night and weather, Ravenhold districts, music) |
| `docs/screenshots/` | Curated screenshots. The full `shots/` QA folders are gitignored (they are regenerated) |
| `index.html` | Pages landing page linking the game + demos |

## Run things
Requirements: Python 3.13 + Pillow + numpy; Node 20 (for `trees`); Playwright + Chromium for the checks (`pip install playwright && playwright install chromium`).

```
# the game (static server, 0.0.0.0:8080; PORT=... to change)
games/hearthmoor/startup.sh                                   # http://localhost:8080/
# the demos
bin/hd2d serve demos/hearthmoor-plaza                         # http://127.0.0.1:8077/
python3 -m http.server 8078 --directory demos/bakery-lane     # http://localhost:8078/

# tools (P = a project folder)
bin/hd2d palette --biome all --out P/public/art/palette
bin/hd2d sprite --biome cozy-village --roles all --out P/public/art/sprite
bin/hd2d sprite --roles heroes --out /tmp/h --lineup docs/screenshots/hero_origins_4x.png   # 6 hero classes + 4x lineup
bin/hd2d sprite --roles heroes --out /tmp/h --anim-lineup docs/screenshots/hero_anims_4x.png  # action sheet (--anim-facing left|up)
bin/hd2d assemble scenes/hero-classes-plaza.json --out /tmp/heroplaza --no-zip           # heroes on the plaza at golden hour
bin/hd2d check-sprite P/public/art/sprite/actors.png --biome cozy-village
bin/hd2d texel --biome cozy-village --sizes 32,64 --out P/public/art/texel
bin/hd2d kit --biome cozy-village --out P/public/art/kit --texel P/public/art/texel
bin/hd2d trees --biome cozy-village --out P/public/art/trees
bin/hd2d particles --biome cozy-village --out P/public/art/particles
bin/hd2d spells --biome cozy-village --out P/public/art/spells
bin/hd2d portal --biome cozy-village --out P/public/art/gamefx
bin/hd2d runtime --out P
bin/hd2d assemble scenes/hearthmoor-plaza.json --out demos/hearthmoor-plaza [--no-zip] [--shots]
python3 games/hearthmoor/build.py [--skip-assemble] [--no-zip]   # rebuild areas, icons, manifest, sw.js, zip
```

Useful URL params: `?pad=1`, `?hand=left`, `?t=day|dusk|night`, `?freeze`. For the game: `?qa&area=plaza|lane|mossglen` (fresh state, no title, no saving), `?reset`, `?nosw`, `?day=SECONDS`, `?simscale=N`.

## Checks and smoke test (must pass)
```
bin/hd2d check-sprite games/hearthmoor/areas/<id>/public/art/sprite/actors.png --json .../actors.json --biome cozy-village
bin/hd2d check-scene demos/hearthmoor-plaza
bin/hd2d check-scene demos/bakery-lane
bin/hd2d check-scene games/hearthmoor --scene-dir areas/plaza    --params "area=plaza&qa&spawn=start"    --out games/hearthmoor/shots/plaza
bin/hd2d check-scene games/hearthmoor --scene-dir areas/lane     --params "area=lane&qa&spawn=qa"        --out games/hearthmoor/shots/lane
bin/hd2d check-scene games/hearthmoor --scene-dir areas/mossglen --params "area=mossglen&qa&spawn=start" --out games/hearthmoor/shots/mossglen
python3 games/hearthmoor/tests/smoke.py        # ~10 min headless, writes games/hearthmoor/tests/shots/ (+ smoke.json)
```
- **check-scene** (~5–7 min each) checks:
  - sprite sharpness, camera lock and no bloom;
  - height and colours, and the day / dusk / night grades;
  - effects and game-effects sharpness;
  - the phone check: layout, tap-walk, floating stick, no page zoom, loading gate, controller, pinch.
  - actions: a jump (held sim, fixed steps) lifts the sprite while the shadow stays at the feet; hero players also attack and hold a guard.
- **Smoke test:** the hero picker, a full playthrough of all 3 errands, both exits and the portal both ways, Mossglen combat (hit, guard, roll i-frames, spell, summon, defeat / respawn), save / reload ×2, v1 → v2 save migration, a stubbed controller (new map), phone touch (stick, action buttons, spell wheel) and the loading gate. It runs with `?peace` so enemies don't interrupt the errands, then turns them on for the combat steps.
- **Headless tips:**
  - Use SwiftShader args: `--use-angle=swiftshader --enable-unsafe-swiftshader --ignore-gpu-blocklist`.
  - Run **one browser job at a time**; a second busy page makes touch timing flaky.
  - Run long jobs detached and poll their logs.

## Bill's standing preferences
- **Style:** follow [`docs/HD2D_COZY_STYLE_LOCK.md`](docs/HD2D_COZY_STYLE_LOCK.md):
  - pixel billboard actors in a lit 3D miniature with a locked 3/4 camera and mild tilt-shift;
  - one key sun plus lamps and sprite shadows; warm day, blue dusk, orange-window night;
  - a parchment / carved-wood HUD;
  - no bloom, no blur, no free camera.
- **Original IP only.** No Octopath / Square Enix assets, characters, UI or maps, and no copied pixels from anywhere.
- **Sprites are always nearest-neighbour and never blurred** (integer pixel scale, 1 px outline). They never go through the world's blur pass.
- **Gloom-and-glow:** dark scenes full of glowing objects, plus neon (wisps, fireflies, glowing mushrooms, runes, portals, orb lanterns). The glow comes from emissive pixels and point lights, **never bloom**.
- **Phone first:**
  - a floating joystick;
  - no page scroll or zoom (pinch is camera zoom only);
  - input blocked while loading;
  - HUD inside the viewport, touch targets ≥ 30 px, safe-area aware;
  - a left-handed flip.
- **All three input schemes work at once:** touch, Bluetooth controller (standard mapping) and WASD + mouse (click-to-walk, wheel zoom).
- **Portals:** draw them fresh in the game's palette. Gravewake's `style/rift_refs` (swirling vortexes, stone-arch gates, flame ring, wall vortex) are a **style reference only**. Never copy their pixels, and never modify Gravewake or other projects.
- **Replies:** keep them brief.
- **Repo hygiene:**
  - secret scan before every push;
  - keep `CHANGELOG.md` and `AGENTS.md` current;
  - descriptive commits;
  - pull before resuming.

## Known issues
- No real-device or real-GPU test yet (headless Chromium + SwiftShader and emulated phones only).
- The controller is tested only through a simulated `navigator.getGamepads()`. There's no button remap, and non-standard pads are read as standard.
- Dialogue is linear (no choices); there's one save slot; errands have a single path.
- Pathfinding ignores moving NPCs (they're avoided only by collision sliding).
- Hero actions: wards are hidden from behind (`up` shows glow at the hands only). The demos' atlases weren't regenerated (only the game's were), so demo villagers have no attack / defend / jump frames.
- Combat (Stage 1): no loot, XP or levels yet; one summon per hero; spell slots 2–4 are simply the newest charms (no spellbook UI); the controller has no hold-for-wheel (LB / RB step slots instead); enemies don't path-find (they chase straight and slide on walls); the golem's side view reads a little bird-like.
- Smaller notes:
  - Plaza and Lane reuse the demo layouts.
  - Backdrop hills are simple domes.
  - The first visit precaches about 12 MB.
  - The procedural audio has never been listened to.

## Next steps
Hearthmoor is being built in stages (milestones in `docs/HEARTHMOOR_BUILDER_HANDOFF.md` section 12); each stage pushes a playable build to Pages. Stage 1 (M0 platform polish + M1 heroes + start of M2 combat) is done. Proposed **Stage 2**:
1. Leveling (XP from foes and errands, 2 free stat points per level) and the first tier of each hero's skill tree (`docs/story/DESIGN_EXPANSION_2026-10-03.md` E3). Bill's call: a new game asks "Auto level? Yes / No" (Yes = class-based auto-assign of the 2 points, No = manual), toggleable anytime in the options card.
2. Loot with rarity colours, an inventory / equipment page and a spellbook UI to assign the 4 slots.
3. Day-night effects on gameplay (night spawns, lamp-lit safe zones) and light weather.
4. More enemy types, a mini-boss in Mossglen, difficulty settings, a controller hold-for-wheel and button remap.
5. Then: first realm areas and the Rainbow Rift portal hub, dialogue choices, more save slots, mushroom villages / gnomes / bubbly springs.
