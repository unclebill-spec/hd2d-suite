# Svartalfheim pack: Anvildeep, Amethyst Mines, Clockwork Deep (Gorrak Ironmaw)

Art seat staging, 2026-10-14. Brief: `story/svartalfheim.md` + handoff 11.6 (Tick). Rebuild: `cd src && python3 gen_svartalfheim.py`
(Pillow + numpy; reads the repo's tools read-only; also imports `../../pets/pets_gen.py` for Tick, unchanged). This finishes the
aborted attempt's `sv_common / sv_actors / sv_big / sv_boss` generators (reused as is) and adds the orchestrator, Tick, the kit, fx and the scene.

![contact sheet](contact_sheet.png)  Scene: `renders/scene_clockwork_deep_night.png`

## Contents and scales
| sheet | roles | frame / scale |
|---|---|---|
| `sprite/svart_npcs` | thane, runewarden, hushed, dwarftrader, tinker, minerunner, poolkeeper_sv, dw1, dw2, sv1, sv2 | 20x32, idle+walk. Dwarves/kid are natively short (kind `creature` + `body` note so they fit check-sprite's size bounds) |
| `sprite/dagna` (+ `dagna_neon.png`) | dagna (companion) | 20x32, idle/walk/cast/attack |
| `sprite/deep_enemies` | forgeconstruct, sparkgolem, sootling, shadowsmith (elite), hushblade | 20x32 |
| `sprite/runaway_construct` | runaway | 40x64, **2.0x** |
| `sprite/rare_basilisk` | basilisk (Amethyst Basilisk) | 96x80, **2.5x** |
| `sprite/rare_sootcolossus` | sootcolossus | 64x90, **2.8x** |
| `sprite/miniboss_foreman` | foreman (C4 mini-boss) | 56x90, **2.8x** |
| `sprite/boss_gorrak` | gorrak (phase 1, chained), gorrak_unbuckled (phases 2-3) | 144x192, **6x**, the only plate armour |
| `tick/` | pet_tick: `tick_neon.png` (primary), `tick.png` (palette-safe), `tick.json`, `tick_fx` (aura, pool, safe pool) | pets/ layout: 20x32, pivot [10,32], rows down/up/left/right, idle 0-3, walk 4-7, follow 8-11; petfx light/aura/pool in json (particles: none) |
| `kit/*.glb` + `kit.json` | deep_floor, deep_wall, rail_straight, mine_cart, gear_wall, crystal_cluster, rune_lamp, forge_brazier, glow_pool, anvil_pillar (boss_stand marker) | `src/kit_svart.py`, renders in `renders/*_night.png` |
| `gamefx/svart_fx` | pool_blue/violet/red, water_glow, neon_fireflies_blue/violet, forge_embers, glow_orb_blue/violet/red | 48 px |

All townsfolk wear real clothes: separate top and bottom with a visible belt or apron tie. There are no onesies or armour bodies. Palette: forge reds and copper, cold-blue runes, violet crystal.

## Check-sprite
Every sheet passes; see `check_sprite_report.json`. That covers 8 sheets plus `tick.png`. `tick_neon.png` and `dagna_neon.png` are the neon twins. They fail the palette check by design until the lead adds scoped allow-list entries for `pet_tick` and `dagna`.

## Neon flag
- **Neon pixels:** `tick/tick_neon.png` (neon-blue eyes and chest core), `sprite/dagna_neon.png` (ember hammer and cast sparks in neon red), every `gamefx/svart_fx` effect, and the kit `glow` material (rune seams, crystal tips, flames, water).
- **No neon:** all other character sprites, including the bosses, rares and enemies. They use the palette only, and their glow comes from fx and lights.
- New staging tones `sv_*` (story 2.2) are used on fx only.

## Notes
- Hammer outline issue: Dagna's back hammer and attack, the Thane's hammer sceptre and the Shadowsmith's hot hammer all **pass** check-sprite here, so I kept them and didn't swap them for chisels, tongs or picks.
- Scene ground light pools are fx decals, so the engine needs to place them as the recipe in kit.json `fx` describes.

## Questions
1. Should the dwarves' hammers still be swapped for picks, tongs or chisels, even though they pass check-sprite?
2. Tick's light pulse shape is `"tick"`, a stepped pulse. Can pets.js take it, or should it use `sine`?
3. Should Dagna ship with neon-red ember glow (`dagna_neon.png`) or palette only?
4. The Gorrak scene uses a red pool scaled x3 under him. Is that OK, or should he get a dedicated `gorrak_aura`?
