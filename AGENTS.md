# AGENTS.md: handoff guide for hd2d-suite

Bill (GitHub `unclebill-spec`) hands this project between his bots and Cursor through GitHub. Read this file first, then `CHANGELOG.md`.

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
- **Hero classes:** `hd2d sprite` has 6 playable classes (`roles_heroes.py`: wildcaller, runeguard, seer, stormborn, grovekeeper, cinderknight), each with a 4-frame cast or attack.
  - Lineup: `docs/screenshots/hero_origins_4x.png`. In-scene: `docs/screenshots/hero_origins_plaza.png`. Review scene: `scenes/hero-classes-plaza.json`.
  - Not yet wired into the game: the player is still the traveler, and there's no class picker.
- **Toolset:** a Python CLI `bin/hd2d` with 13 tools, which generates original pixel art and assembles lit three.js r160 dioramas (static ES modules, no build step).
- **Demos:** `demos/hearthmoor-plaza`, `demos/bakery-lane` (+ zips).
- **Game:** `games/hearthmoor/`:
  - 3 areas (Plaza, Bakery Lane, Mossglen through a portal), 3 errands, dialogue, quest log, bag;
  - real-time day / dusk / night, charms, save / load (`hearthmoor-slot-1-v1`), PWA;
  - touch with a floating stick, Bluetooth / USB controller, keyboard + mouse.
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
| `games/hearthmoor/` | The game: `index.html`, `game/` (game.js, data.js, audio.js, game.css), `areas/<id>/` (built), `areas/src/*.json` (area specs), `build.py`, `tests/smoke.py`, `startup.sh`, `RESTORE.md` |
| `docs/HD2D_COZY_STYLE_LOCK.md` | Bill's style law (binding) |
| `docs/story/STORY_SEEDS.md` | Story bible: Norse Nine Realms direction, villain, alliances, cities, heroes and magic, pets |
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
python3 games/hearthmoor/tests/smoke.py        # ~8 min headless, 46 steps, writes games/hearthmoor/tests/shots/ (+ smoke.json)
```
- **check-scene** (~5–7 min each) checks:
  - sprite sharpness, camera lock and no bloom;
  - height and colours, and the day / dusk / night grades;
  - effects and game-effects sharpness;
  - the phone check: layout, tap-walk, floating stick, no page zoom, loading gate, controller, pinch.
- **Smoke test:** a full playthrough of all 3 errands, both exits and the portal both ways, save / reload ×2, a stubbed controller, phone touch and the loading gate.
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
- The player can disappear behind buildings (sprites are depth-tested; there's no see-through outline yet).
- Dialogue is linear (no choices); there's one save slot; errands have a single path.
- Pathfinding ignores moving NPCs (they're avoided only by collision sliding).
- Smaller notes:
  - Plaza and Lane reuse the demo layouts.
  - Backdrop hills are simple domes.
  - The first visit precaches about 12 MB.
  - The procedural audio has never been listened to.

## Next steps
1. A see-through outline / silhouette for the player when a building occludes them (sprite-only pass, no blur).
2. Controller button remap (saved per device) and handling for non-standard mappings.
3. Bill's display presets: **Auto, Phone landscape, 720p, 1080p TV, Retro 320x240**, plus aspect options. Keep the integer pixel scale for sprites.
4. A fullscreen button and a "rotate your phone" prompt.
5. More areas and quests (dialogue choices, NPC schedules, more save slots).
6. New content: mushroom villages, gnomes, bubbly springs (new kit pieces, roles, particles; original art under the style lock).
7. **Hero classes in the game:**
   - a class picker on the title screen, with the chosen class as the player sprite;
   - per-class spells and summons (see Heroes and magic in `STORY_SEEDS.md`);
   - action-frame VFX in the spells atlas;
   - first realm areas and the Rainbow Rift portal hub.
