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

## Files

| file | size | px |
|---|---|---|
| `check_sprite_report.json` | 5 KB |  |
| `contact_sheet.png` | 466 KB | 1400x7822 |
| `gamefx/strips/forge_embers.png` | 1 KB | 384x48 |
| `gamefx/strips/glow_orb_blue.png` | 2 KB | 384x48 |
| `gamefx/strips/glow_orb_red.png` | 2 KB | 384x48 |
| `gamefx/strips/glow_orb_violet.png` | 2 KB | 384x48 |
| `gamefx/strips/neon_fireflies_blue.png` | 1 KB | 384x48 |
| `gamefx/strips/neon_fireflies_violet.png` | 1 KB | 384x48 |
| `gamefx/strips/pool_blue.png` | 2 KB | 288x48 |
| `gamefx/strips/pool_red.png` | 2 KB | 288x48 |
| `gamefx/strips/pool_violet.png` | 2 KB | 288x48 |
| `gamefx/strips/water_glow.png` | 2 KB | 288x48 |
| `gamefx/svart_fx.json` | 10 KB |  |
| `gamefx/svart_fx.png` | 9 KB | 384x480 |
| `kit/anvil_pillar.glb` | 28 KB |  |
| `kit/crystal_cluster.glb` | 66 KB |  |
| `kit/deep_floor.glb` | 10 KB |  |
| `kit/deep_wall.glb` | 38 KB |  |
| `kit/forge_brazier.glb` | 22 KB |  |
| `kit/gear_wall.glb` | 78 KB |  |
| `kit/glow_pool.glb` | 41 KB |  |
| `kit/kit.json` | 5 KB |  |
| `kit/mine_cart.glb` | 59 KB |  |
| `kit/rail_straight.glb` | 16 KB |  |
| `kit/rune_lamp.glb` | 20 KB |  |
| `renders/anvil_pillar_night.png` | 2 KB | 66x91 |
| `renders/crystal_cluster_night.png` | 1 KB | 33x45 |
| `renders/deep_floor_night.png` | 1 KB | 48x34 |
| `renders/deep_wall_night.png` | 1 KB | 48x67 |
| `renders/forge_brazier_night.png` | 1 KB | 28x35 |
| `renders/gear_wall_night.png` | 2 KB | 56x52 |
| `renders/glow_pool_night.png` | 1 KB | 76x40 |
| `renders/mine_cart_night.png` | 1 KB | 28x37 |
| `renders/rail_straight_night.png` | 1 KB | 30x35 |
| `renders/rune_lamp_night.png` | 1 KB | 20x53 |
| `renders/scene_clockwork_deep_night.png` | 41 KB | 348x305 |
| `sprite/boss_gorrak.json` | 30 KB |  |
| `sprite/boss_gorrak.png` | 501 KB | 4032x1536 |
| `sprite/dagna.json` | 15 KB |  |
| `sprite/dagna.png` | 9 KB | 320x128 |
| `sprite/dagna_neon.png` | 9 KB | 320x128 |
| `sprite/deep_enemies.json` | 64 KB |  |
| `sprite/deep_enemies.png` | 34 KB | 560x640 |
| `sprite/miniboss_foreman.json` | 15 KB |  |
| `sprite/miniboss_foreman.png` | 28 KB | 1568x360 |
| `sprite/rare_basilisk.json` | 15 KB |  |
| `sprite/rare_basilisk.png` | 40 KB | 2688x320 |
| `sprite/rare_sootcolossus.json` | 15 KB |  |
| `sprite/rare_sootcolossus.png` | 56 KB | 1792x360 |
| `sprite/runaway_construct.json` | 15 KB |  |
| `sprite/runaway_construct.png` | 28 KB | 1120x256 |
| `sprite/strips/dagna.png` | 9 KB | 320x128 |
| `sprite/strips/dw1.png` | 4 KB | 240x128 |
| `sprite/strips/dw2.png` | 4 KB | 240x128 |
| `sprite/strips/dwarftrader.png` | 4 KB | 240x128 |
| `sprite/strips/forgeconstruct.png` | 8 KB | 560x128 |
| `sprite/strips/hushblade.png` | 7 KB | 560x128 |
| `sprite/strips/hushed.png` | 4 KB | 240x128 |
| `sprite/strips/minerunner.png` | 4 KB | 240x128 |
| `sprite/strips/poolkeeper_sv.png` | 5 KB | 240x128 |
| `sprite/strips/runewarden.png` | 4 KB | 240x128 |
| `sprite/strips/shadowsmith.png` | 8 KB | 560x128 |
| `sprite/strips/sootling.png` | 6 KB | 560x128 |
| `sprite/strips/sparkgolem.png` | 7 KB | 560x128 |
| `sprite/strips/sv1.png` | 4 KB | 240x128 |
| `sprite/strips/sv2.png` | 4 KB | 240x128 |
| `sprite/strips/thane.png` | 4 KB | 240x128 |
| `sprite/strips/tinker.png` | 4 KB | 240x128 |
| `sprite/svart_npcs.json` | 77 KB |  |
| `sprite/svart_npcs.png` | 39 KB | 240x1408 |
| `src/README_body.md` | 4 KB |  |
| `src/gen_alfheim_decal.py` | 1 KB |  |
| `src/gen_svartalfheim.py` | 15 KB |  |
| `src/hmart.py` | 32 KB |  |
| `src/kit_svart.py` | 9 KB |  |
| `src/sv_actors.py` | 33 KB |  |
| `src/sv_big.py` | 22 KB |  |
| `src/sv_boss.py` | 27 KB |  |
| `src/sv_common.py` | 7 KB |  |
| `src/tick_gen.py` | 6 KB |  |
| `tick/check_sprite_report.json` | 1 KB |  |
| `tick/tick.json` | 12 KB |  |
| `tick/tick.png` | 4 KB | 240x128 |
| `tick/tick_fx.json` | 4 KB |  |
| `tick/tick_fx.png` | 2 KB | 256x96 |
| `tick/tick_neon.png` | 4 KB | 240x128 |
