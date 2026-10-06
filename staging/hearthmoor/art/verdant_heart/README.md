# The Verdant Heart pack (dungeon under Vanaheim): bioluminescent cavern, enemies, three big foes

Art seat staging pack for **Hearthmoor**. Generated procedurally by `src/gen_verdant_heart.py` (Python + Pillow +
numpy, importing the repo's `tools/sprite`, `tools/kit`, `tools/check-sprite` read-only). Mood pushed hard toward
Bill's reference boards (`art/_refs/bill_ref_1..6`): neon mushrooms over black water, glowing fern spirals, glowing
underground stream / pool / waterfall, hanging glow vines, glow fog, neon fireflies, glow frogs and hovering glow orbs,
plus his red white-spotted toadstools and neon-blue cold fire.

![contact sheet](contact_sheet.png)

> **Docs (confirmed by the lead 2026-10-06 + story/verdant_heart.md):** **The Rotwood Hollow** is Vanaheim's main
> dungeon (rot treants, spore elementals, boss **The Blight Regent**, R7, 5.5x). **The Verdant Heart** is the optional
> deeper dungeon (V4 rare **The Thornmother**, 2.4x; V5 boss **Hjortur the Greenheart**, 6x: guardian trial on the
> befriend path, corrupted fight on the conquer path). This pack ships the Regent too (packaged here for convenience);
> the kit works for both dungeons (use `blight_bloom` + violet mist for the Rotwood, the clean glow set +
> `heartseed_cradle` for the Heart). The Regent and Thornmother were revised on 2026-10-06 to match the doc (Regent:
> violet eyes, dead-sapling staff, root ribcage + violet wound with the blue frost-iron spike and rime; Thornmother:
> corrupted dryad-tree with a moonpetal crown gone violet). **Not drawn yet:** the doc's regular Verdant enemies
> `thornhex`, `lifewisp` and the Thornmother's summoned `thornnymph`. The game already has a Vanaheim `sporeling`;
> `sporeelemental` here is a separate dungeon-tier variant.

## Sprites (`sprite/`)
| sheet | roles | frame | scale | check-sprite |
|---|---|---|---|---|
| `verdant_actors.png/.json` | `rottreant`, `sporeelemental` | 20x32, pivot [10,32] | 1x | PASS |
| `boss_blight_regent.png/.json` | `blightregent` | 128x176, pivot [64,176] | 5.5 (figure ~171 px = 5.9x the hero's 29 px) | PASS |
| `boss_hjortur.png/.json` | `hjortur`, `hjortur_corrupted` | 144x192, pivot [72,192] | 6.0 | PASS |
| `boss_thornmother.png/.json` | `thornmother` | 48x77, pivot [24,77] | 2.4 | PASS |

All use the enemy column layout: idle 0-3 (3 fps, loop 0,1,2,1), walk 4-7 (8 fps), attack 12-15 (10 fps, loop
0,1,2,2,3; hit on frame 14), die 24-27 (6 fps, once); rows down / up / left / right (right = mirrored left). Boss sheets
are `tools/sprite/boss_sheet.py` format (`boss: true`, `scale`, size_bounds [[12, fw-2], [12, fh]]), all <= 4096 px.
Each role's JSON carries `light` (colour / intensity / range / pool fx) and `stats_hint`.

- **Rot treant**: squat walking tree, drooping moss crown with red white-spotted toadstools, lamp-glow knot eyes, branch-arm slam; dies into a mossy stump.
- **Spore elemental**: moss-and-gold-spore puff under a big red white-spotted cap, wisp tail to the floor (row 30), lamp eyes, spore-stream attack; dies dropping its cap.
- **The Blight Regent** (5.5x): gnarled bark lord in a moss mantle with toadstools, antlers hung with toadstools, mauve blight blossoms and gold spore-lanterns, sickly violet-rose eyes in a hollow bark mask, a dead-sapling staff topped with red toadstools, and a root ribcage around a violet wound with the **blue frost-iron spike** and white rime frost-flowers (the spike is the only blue on him). Attack = two-arm root slam (frame 14, spawn `root_eruption`). Die = he sinks, the spike lies on the mossy root mound, then a **fresh sapling** (cozy ending; play `regent_cleansed`). Pool: `blight_aura`.
- **Hjortur the Greenheart** (6x): elder stag-king, living-branch antlers in leaf with gold spore-lanterns and moonpetals, moss mantle with fawn-spots, long white beard, glowing leaf mark on his brow, moonpetal garland. Attack = antler-lowering charge + stomp. Die = kneels and lies down at peace (befriend: he yields). Pool: `greenheart_aura`.
- **Hjortur, corrupted** (conquer path): same rig with dark leaves, red toadstools and blight blossoms on the antlers, blight veins, rose eyes. Die = the corruption lifts (green leaves return, eyes close). Pool: `blight_aura`.
- **The Thornmother** (Verdant V4 rare, 2.4x): a corrupted dryad-tree per the doc: willowy figure of bark and thorns, thorn-studded bark bodice over a skirt of trailing willow fronds with a dark vine bound at the waist (top/bottom read kept), root feet, willow-frond hair, pale birch face with violet-rose eyes, **moonpetal crown gone violet**, bramble staff with a violet bud. Attack = bramble whips (+ `thorn_lash`; the doc's seed bombs can reuse `thorn_lash` / spore fx). Die = sinks into a mound blooming with violet moonpetals. Pool: `pool_violet`.

**Neon use (per Bill 2026-10-05): none of the sprites above use neon pixels.** They stay biome-palette only so they
pass check-sprite; their glow is lamp / gold / rose palette pixels plus the light + pool fx listed in their JSON.

## gamefx (`gamefx/`)
`verdant_fx.png/.json` (48 px cells, `hd2d portal` format) - **all neon is here, on glow pixels**:

| group | effects |
|---|---|
| water | `stream_flow` (decal, chains per 2 m tile), `waterfall_sheet` (billboard, lift 0.65), `waterfall_splash`, `heart_spring_bubbles`, `heart_spring_pool` |
| light pools (decal) | `glowroot_pool` (neon blue), `toadstool_glow_pool` (red), `pool_violet`, `pool_green`, `pool_pink` |
| glow fog (decal, lift 0.35) | `glow_mist_blue`, `glow_mist_violet`, `glow_mist_green` - sparse dither so it reads translucent; overlap 3-6 with random frame offsets |
| fireflies (billboard) | `fireflies_neon` (mixed) + `fireflies_blue/violet/red/green/pink` |
| glow orbs (billboard, lift 1.1) | `glow_orb_blue/violet/red/green/pink`: hovering orb, bob, halo sparkles; light 0.8 / 4 m in its colour; pair each with its pool (blue -> glowroot_pool, red -> toadstool_glow_pool, violet/green/pink -> pool_<c>) |
| ambient / boss | `spore_motes`, `blight_aura`, `root_eruption` (once), `spore_burst` (once), `regent_cleansed` (once, light curve), `greenheart_aura`, `thorn_lash` (once) |

`verdant_critters.png/.json` (24 px cells, pivot [12,23]): `glowfrog_<blue|green|pink|violet>_idle` (6f, 4 fps:
throat-sac pulse + blink; light 0.3 / 1.2 m) and `_hop` (6f, 10 fps: move ~0.5 m across it). Ambient critters: sit
them on pool stones, lily pads and stream banks.

Neon hexes (glow pixels only): blue `#2ab4ff/#a6ecff/#1c62d8`, violet `#a45cf0/#d4a8ff/#6a34b8`, red
`#e0302a/#ff5a4a/#a81c22`, cold fire `#5ab4f0/#d8f4ff/#2a6cb0`, **new**: green `#3cf08a/#b8ffd4/#14a85a`, pink
`#ff4fc8/#ffb4ea/#b82a8c` (added for orbs / fireflies / bioluminescence).

## Kit (`kit/*.glb`, `kit/kit.json`, `src/kit_verdant_heart.py`)
Structure: `vh_floor` (4x4 m tile with glow-moss specks), `vh_wall` (4 m, cold-fire veins), `vh_ceiling_lip` (4.4 m
overhang), `glowroot_arch` (3.4 m doorway). Water: `stream_straight` (2 m, flows +z), `stream_bend` (2x2 m, -z in / +x
out), `glow_pool` (3.8 m black-glass pond: bright shallows, dark mirror middle, glowing lily pads), `waterfall` (3.6 m
cliff + glowing fall + splash basin, outlet at +z), `heart_spring` (bubbly spring ringed by glowing roots). Flora:
`glowroot_cluster`, `toadstool_giant` (3.4 m, red #e0302a caps, white spots, warm gills), `toadstool_shelf`,
`neon_mushrooms_pink/_blue/_violet`, `dripcap` (pink cap trailing glowing tendrils), `glowfern` / `glowfern_blue`
(fiddlehead spirals), `hanging_vines` (glow-bulb curtain from 4.2 m), `blight_bloom` (violet), `heartseed_cradle`
(Hjortur's arena). Every glowing piece carries a `lamps` marker with `lamp_color` / `lamp_fixed` / `lamp_range`;
`kit.json` lists the recommended fx per piece (pools, mist, flow, frogs).

**Neon use:** only the `glow` material on mushrooms, ferns, vines, roots, water, the heartseed and bulbs; structure
(stone, bark, moss, stems) is biome palette.

## Placement recipe (the mood scene on the sheet, `renders/scene_verdant_heart_night.png`)
1. Floor tiles on a 4 m grid, back walls, `waterfall` in the back wall, `stream_straight` x2 from its outlet, a
   `stream_bend`, two rotated straights into a `glow_pool`.
2. Big red `toadstool_giant` in a corner; neon mushroom clusters, `dripcap`, ferns along the banks; `vh_ceiling_lip` +
   `hanging_vines` over the back wall.
3. Under every glowing prop drop its pool decal; 3-6 `glow_mist_*` over water; `stream_flow` per stream tile;
   `waterfall_sheet` + `waterfall_splash` on the fall.
4. Scatter 4-6 `glow_orb_*` (one per colour) at lift 1.1 with their pools, 3+ `fireflies_*`, and 3-5 glow frogs.
5. Keep ambient light low (night ambient) so the glow carries the room. No bloom: emissive pixels + small lights + pools.

## Drop-in steps (for the lead)
1. Enemies: paste `verdant_actors` rows into the Vanaheim area atlas or port the draw functions from
   `src/vh_enemies.py` into `tools/sprite/roles_enemies.py` (they use the same `ell` / `rect` / `shader` helpers).
2. Bosses: the `boss_*.png/.json` files are drop-in `boss_sheet` output (one frame size per sheet).
3. gamefx: merge `verdant_fx` / `verdant_critters` into the area's gamefx atlases (cell 48 / 24) or copy functions
   from `src/vh_fx.py` into `tools/portal/portal.py`.
4. Kit: copy `src/kit_verdant_heart.py` to `tools/kit/` and add the import line from its docstring.
5. Regenerate: `python3 src/gen_verdant_heart.py` (needs /workspace/hd2d-suite; writes only into this folder).

## Files

| file | size | px |
|---|---|---|
| `READY.txt` | 1 KB |  |
| `check_sprite_report.json` | 1 KB |  |
| `contact_sheet.png` | 649 KB | 1400x11169 |
| `gamefx/strips/blight_aura.png` | 2 KB | 288x48 |
| `gamefx/strips/fireflies_blue.png` | 1 KB | 384x48 |
| `gamefx/strips/fireflies_green.png` | 1 KB | 384x48 |
| `gamefx/strips/fireflies_neon.png` | 1 KB | 384x48 |
| `gamefx/strips/fireflies_pink.png` | 1 KB | 384x48 |
| `gamefx/strips/fireflies_red.png` | 1 KB | 384x48 |
| `gamefx/strips/fireflies_violet.png` | 1 KB | 384x48 |
| `gamefx/strips/glow_mist_blue.png` | 1 KB | 384x48 |
| `gamefx/strips/glow_mist_green.png` | 1 KB | 384x48 |
| `gamefx/strips/glow_mist_violet.png` | 1 KB | 384x48 |
| `gamefx/strips/glow_orb_blue.png` | 2 KB | 384x48 |
| `gamefx/strips/glow_orb_green.png` | 2 KB | 384x48 |
| `gamefx/strips/glow_orb_pink.png` | 2 KB | 384x48 |
| `gamefx/strips/glow_orb_red.png` | 2 KB | 384x48 |
| `gamefx/strips/glow_orb_violet.png` | 2 KB | 384x48 |
| `gamefx/strips/glowfrog_blue_hop.png` | 1 KB | 144x24 |
| `gamefx/strips/glowfrog_blue_idle.png` | 1 KB | 144x24 |
| `gamefx/strips/glowfrog_green_hop.png` | 1 KB | 144x24 |
| `gamefx/strips/glowfrog_green_idle.png` | 1 KB | 144x24 |
| `gamefx/strips/glowfrog_pink_hop.png` | 1 KB | 144x24 |
| `gamefx/strips/glowfrog_pink_idle.png` | 1 KB | 144x24 |
| `gamefx/strips/glowfrog_violet_hop.png` | 1 KB | 144x24 |
| `gamefx/strips/glowfrog_violet_idle.png` | 1 KB | 144x24 |
| `gamefx/strips/glowroot_pool.png` | 2 KB | 288x48 |
| `gamefx/strips/greenheart_aura.png` | 2 KB | 288x48 |
| `gamefx/strips/heart_spring_bubbles.png` | 1 KB | 288x48 |
| `gamefx/strips/heart_spring_pool.png` | 2 KB | 288x48 |
| `gamefx/strips/pool_green.png` | 2 KB | 288x48 |
| `gamefx/strips/pool_pink.png` | 2 KB | 288x48 |
| `gamefx/strips/pool_violet.png` | 2 KB | 288x48 |
| `gamefx/strips/regent_cleansed.png` | 1 KB | 384x48 |
| `gamefx/strips/root_eruption.png` | 2 KB | 336x48 |
| `gamefx/strips/spore_burst.png` | 1 KB | 288x48 |
| `gamefx/strips/spore_motes.png` | 1 KB | 384x48 |
| `gamefx/strips/stream_flow.png` | 2 KB | 384x48 |
| `gamefx/strips/thorn_lash.png` | 1 KB | 288x48 |
| `gamefx/strips/toadstool_glow_pool.png` | 2 KB | 288x48 |
| `gamefx/strips/waterfall_sheet.png` | 2 KB | 384x48 |
| `gamefx/strips/waterfall_splash.png` | 1 KB | 288x48 |
| `gamefx/verdant_critters.json` | 8 KB |  |
| `gamefx/verdant_critters.png` | 2 KB | 144x192 |
| `gamefx/verdant_fx.json` | 30 KB |  |
| `gamefx/verdant_fx.png` | 28 KB | 384x1488 |
| `kit/blight_bloom.glb` | 57 KB |  |
| `kit/dripcap.glb` | 81 KB |  |
| `kit/glow_pool.glb` | 156 KB |  |
| `kit/glowfern.glb` | 191 KB |  |
| `kit/glowfern_blue.glb` | 191 KB |  |
| `kit/glowroot_arch.glb` | 100 KB |  |
| `kit/glowroot_cluster.glb` | 60 KB |  |
| `kit/hanging_vines.glb` | 180 KB |  |
| `kit/heart_spring.glb` | 117 KB |  |
| `kit/heartseed_cradle.glb` | 149 KB |  |
| `kit/kit.json` | 10 KB |  |
| `kit/neon_mushrooms_blue.glb` | 177 KB |  |
| `kit/neon_mushrooms_pink.glb` | 177 KB |  |
| `kit/neon_mushrooms_violet.glb` | 177 KB |  |
| `kit/stream_bend.glb` | 137 KB |  |
| `kit/stream_straight.glb` | 105 KB |  |
| `kit/toadstool_giant.glb` | 87 KB |  |
| `kit/toadstool_shelf.glb` | 75 KB |  |
| `kit/vh_ceiling_lip.glb` | 48 KB |  |
| `kit/vh_floor.glb` | 137 KB |  |
| `kit/vh_wall.glb` | 255 KB |  |
| `kit/waterfall.glb` | 267 KB |  |
| `renders/blight_bloom_night.png` | 1 KB | 34x32 |
| `renders/dripcap_night.png` | 1 KB | 48x68 |
| `renders/glow_pool_night.png` | 3 KB | 88x57 |
| `renders/glowfern_blue_night.png` | 1 KB | 39x42 |
| `renders/glowfern_night.png` | 1 KB | 36x41 |
| `renders/glowroot_arch_night.png` | 3 KB | 98x74 |
| `renders/glowroot_cluster_night.png` | 2 KB | 52x44 |
| `renders/hanging_vines_night.png` | 1 KB | 60x66 |
| `renders/heart_spring_night.png` | 2 KB | 68x51 |
| `renders/heartseed_cradle_night.png` | 3 KB | 78x69 |
| `renders/neon_mushrooms_blue_night.png` | 2 KB | 51x52 |
| `renders/neon_mushrooms_pink_night.png` | 2 KB | 51x52 |
| `renders/neon_mushrooms_violet_night.png` | 2 KB | 51x52 |
| `renders/scene_verdant_heart_night.png` | 62 KB | 330x217 |
| `renders/stream_bend_night.png` | 2 KB | 56x41 |
| `renders/stream_straight_night.png` | 2 KB | 56x39 |
| `renders/toadstool_giant_night.png` | 2 KB | 66x78 |
| `renders/toadstool_shelf_night.png` | 1 KB | 39x47 |
| `renders/vh_ceiling_lip_night.png` | 2 KB | 105x41 |
| `renders/vh_floor_night.png` | 2 KB | 87x57 |
| `renders/vh_wall_night.png` | 5 KB | 99x73 |
| `renders/waterfall_night.png` | 5 KB | 97x94 |
| `sprite/boss_blight_regent.json` | 16 KB |  |
| `sprite/boss_blight_regent.png` | 184 KB | 3584x704 |
| `sprite/boss_hjortur.json` | 30 KB |  |
| `sprite/boss_hjortur.png` | 322 KB | 4032x1536 |
| `sprite/boss_thornmother.json` | 16 KB |  |
| `sprite/boss_thornmother.png` | 33 KB | 1344x308 |
| `sprite/strips/rottreant.png` | 11 KB | 560x128 |
| `sprite/strips/sporeelemental.png` | 12 KB | 560x128 |
| `sprite/verdant_actors.json` | 29 KB |  |
| `sprite/verdant_actors.png` | 23 KB | 560x256 |
| `src/gen_verdant_heart.py` | 31 KB |  |
| `src/hmart.py` | 32 KB |  |
| `src/kit_verdant_heart.py` | 29 KB |  |
| `src/vh_boss.py` | 18 KB |  |
| `src/vh_bosses2.py` | 23 KB |  |
| `src/vh_enemies.py` | 12 KB |  |
| `src/vh_fx.py` | 20 KB |  |
