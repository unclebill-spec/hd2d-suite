# Adding a realm (template: Alfheim, built by Master Builder, merged 2026-10-15)

Read `ALFHEIM_PROGRESS.md` (history, pitfalls) and `docs/ALFHEIM.md` (what shipped). Alfheim = 4 areas (`alfheim` Glimmer Steps,
`lumen_court`, `wispwood`, `prismvault`), 1 companion (Lumi), 5 bosses, a beam puzzle. A smaller realm needs only the parts you use.

## Files
| Piece | File(s) |
|---|---|
| Story / script (source of truth) | `/workspace/hearthmoor-staging/story/<realm>.md`; art pack in `/workspace/hearthmoor-staging/art/<realm>/` (README + READY.txt) |
| Area specs | `games/hearthmoor/areas/src/<area>.json` (built output `areas/<area>/`, committed) |
| Game module | `games/hearthmoor/game/<realm>.js` (+ `_bosses`, `_beams`, `_lumi`-style helpers): enemies / XP / spawns, quests, TALK, MARKER_HOOKS, ITEMS, SHOPS, WAYS, rift / rare tables, alliance lock |
| Kit pieces | `tools/kit/kit_<realm>.py` (+ one import line in `tools/kit/kit.py`) |
| Gamefx / portal / spells | `tools/portal/portal_<realm>.py`, `tools/spells/spells_<realm>.py` (+ hook in `portal.py` / `spells.py`) |
| NPC + enemy sprites | `tools/sprite/roles_<realm>.py` (+ hook in `sprite.py`); bosses `tools/sprite/boss_<realm>.py` (+ `boss_sheet.py`; the assembler writes one boss sheet per frame size) |
| Art re-run after a staging change | `tools/hearthmoor/alf_art.py` (additive and idempotent: adds sheets, places staging props, never deletes). Copy it for the next realm |
| Tests | `games/hearthmoor/tests/smoke_<realm>.py` (called from `tests/smoke.py`, own browser context); QA presets in the module (`?alfq=...`) |

## Shared-file hooks (all tagged `[ALFHEIM]`; grep it for the exact lines)
`game/game.js`: import, `AREAS` path map, `new <Realm>(G)`, `detach` / `attach` / `update` in the area lifecycle, `AREA_NAME`,
`drawPortrait` (own portrait sheets). `game/data.js`: `MARKER_HOOKS`. `game/glow.js`: `GLOW_TABLES`, a `zones()` wrap.
`build.py`: `AREAS`. `tools/assemble/assemble.py`: boss sheets per frame size. `tools/check-scene/check_scene.py` and
`tools/check-sprite/check_sprite.py`: scoped allowances (extra-sheet actors, sparse gamefx, neon allow-list for the realm's companion only).

## Steps
1. Re-pull the story doc and the art README first; the art seat updates them. Copy art into `games/hearthmoor/art/<realm>/`.
2. Write the area specs; build **one area at a time into a private dir**: `HM_BUILD_TMP=/tmp/<realm>_build python3 build.py --areas <a> --no-zip`, then run the realm's `*_art.py`, then `python3 -c "import build; build.write_pwa()"`.
3. Add the kit / portal / spells / roles / boss modules and their one-line hooks; add the areas to `AREAS` in `build.py` and `game.js`.
4. Write `game/<realm>.js` (tables merge into the shared ones at import); wire the realm's gate at Bifrost (`bifrost.js` GATES) and the alliance flag.
5. Quick-load every area (phone size, `?qa&nosw`, 0 page / console / HTTP errors), then `smoke_<realm>.py`, then `check_scene --quick` per area, one at a time under `flock /workspace/.hm-logs/browser.lock`.
6. Fix check-scene failures in the **area spec** (spawn out of arches / occlusion, terrace height >= 1 m for the height check, enough warm lamps for the night grade, sparse gamefx dropped), not by loosening checks.
7. Merge main into the realm branch (not the reverse), re-run the art script (it re-adds shared sheets such as Lumi's), regenerate `sw.js`, then full sharded smoke (`--jobs 2`) and `check_all --lowres` on every area.
8. Merge to main fast-forward, update CHANGELOG + AGENTS current state, rebuild PWA + zip, secret scan (rg + gitleaks tree and history), push, confirm the live `sw.js` cache id.

## Pitfalls
- **Never `build.py --skip-assemble`** when `/tmp/hearthmoor_build` is gone: `copy_areas()` wipes `areas/*/public`. Restore with `git checkout -- games/hearthmoor/areas`. To refresh only the zip / PWA: `python3 -c "import build; build.draw_icons(); build.draw_button_icons(); build.write_pwa(); build.make_zip()"`.
- Only one agent drives a browser at a time: `flock /workspace/.hm-logs/browser.lock` (Master Builder used `browser-mb.lock` with its own Chromium profile).
- Keep new neon hexes on glow pixels only; the biome palette check (`tests/check_palette.py`) and check-sprite will fail anything else.
- Smoke steps wait for conditions; do not widen thresholds. Keep steps' info kwargs from colliding with `step(name=...)`.
