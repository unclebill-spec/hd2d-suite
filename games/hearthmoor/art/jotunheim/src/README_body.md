# Jotunheim pack: Stonehollow, Rime Caves, Titan's Barrow (Hrimgard the Unthawed)

Art seat, 2026-10-16. Story: `story/jotunheim.md`. Rebuild: `cd src && python3 gen_jotunheim.py` (Pillow + numpy; repo read-only; reuses `pets/pets_gen.py` for Flurry).
Library checked first (`bill-asset-library` pulled: nothing reusable for giants or hares; the glow ideas were reused from the earlier packs).

![contact sheet](contact_sheet.png)  Night scene: `renders/scene_stonehollow_night.png` (also `_day`, `scene_rimecaves_night`, `scene_titans_barrow_night`)

| sheet | roles | frame / scale |
|---|---|---|
| `sprite/jt_giants` | kolbrun, jarl, ulfar_town, rimewife (Solvi), skuli, goatwife (Brynja), grimsa, rimecaptain (Hjordis), gi_man, gi_woman | 64x100, idle+walk, **2-3.2x** (skuli 2x, rimewife 2.8x, jarl 3.2x) |
| `sprite/ulfar` | ulfar (idle, walk, cast = shield hug, attack = boulder toss) | 64x100, **3x** (2.4x in combat: meta `combat_scale`) |
| `pets/flurry*` | pet_flurry (snow hare). **Primary sheet `flurry_neon.png`** (`primary`/`image` in `flurry.json`), `flurry.png` = palette-safe fallback (`fallback`), same layout | pets layout 20x32, pivot [10,32], idle 0-3, walk 4-7, follow 8-11 |
| `sprite/jt_enemies` | frost_troll 1.6x, ice_golem 1.5x, avalanche_golem 1.8x, rime_berserker 1.8x | 56x68, idle/walk/attack/die |
| `sprite/jt_elites` | frostmother 2.5x (rare), avalanche 3x (rare), ormgar 3x (mini-boss) | 88x100, idle/walk/attack/die |
| `sprite/boss_hrimgard` | hrimgard (P1-2), hrimgard_p3 | 144x224, **7x**, the only plate |
| `kit/*.glb` + `kit.json` | 31 pieces (new: `rune_waystone`, `stone_cairn`, `watch_cairn` with horn, `cairn_toppled`; each has a `keep_clear` footprint): Stonehollow (longhouse, ledge, stair, mound, braziers, stones...), Rime Caves (ice wall/floor, pools, icicles, crystals), Barrow (door, wall, throne, bridge, brazier) | `src/kit_jotun.py`, renders `renders/*_night.png` |
| `gamefx/stonefrost_fx` | **Stonefrost II + III** (Solvi's school): per tier `cast` (hands), `bolt` (boulder rimed in ice, projectile, `then` impact), `impact`, `rune` (Frost Rune trap decal, frame 5 = armed) and `burst` (trap trigger pillar). III is larger and brighter (hexagram, extra ring, more sparkles, white-hot cores). Tier I stays the repo's `seed_bomb`/`rune_trap` | 48 px cells, hd2d portal/spells JSON (`cast_sets`, `tier_of` maps spells to ids), cold-blue + teal neon |
| `gamefx/jt_fx` | pools (cold, teal, aurora, violet), aurora_glow, cold_flame, ice_sparkles, fireflies (blue, green, violet), glow_orb x3, glow_frog, glow_vines, glow_fog, rune_pulse, snow_puff | 48 px |

Big frames use the boss_sheet layout (pivot bottom centre, idle 0-3, walk 4-7, cast 8-11, attack 12-15, die 24-27). Giants wear wool tunics, belts, belted trousers, boots and fur mantles. No onesies. Plate appears on Hrimgard only. Hrimgard's die frames sink him into an ice mound.

## Placement notes (also in `metadata/jotunheim.json` and `kit/kit.json` markers)
- **Real height:** Stonehollow has a 1.34 m plateau (two `stone_ledge`) with one `stone_stair` (6 steps, 1.2 m rise, 2 m wide), an east ledge and a 1.3 m `snow_mound`. The Rime Caves and Barrow layouts each have a ledge + stair.
- **Keep clear:** no props, fx decals or spawns on a stair footprint +1 m each end; props >= 1.5 m behind a ledge's front edge; nothing within 1.5 m of the `from_bifrost` spawn [0,9.2]; 2.5 m clear in front of longhouse doors; 3 m in front of the Barrow door; stand actors on the flat of mounds only.
- **Lighting:** day luma 55-70, night 20-30 with glow pools. Measured on my renders: {{LUMA}}. Night ambient is a lifted grey-blue and the colour comes from cold-fire, teal and aurora pools plus warm windows and `warm_lantern`s, so no grade is all dark blue. I can't run check-scene on a render (it needs the built game), so please run it once in the build.

## Check-sprite (once per sheet)
{{CHECKS}}. Details in `check_sprite_report.json`. `flurry_neon.png` (primary look) also PASSES now that the repo's check-sprite has the scoped `pet_flurry` neon-blue allow-list entry (the lead added it); `flurry.png` stays as the palette-safe fallback.

## Neon flag
Neon pixels: `pets/flurry_neon.png` (ear tips, tail puff, chest), every `gamefx/jt_fx` and `gamefx/stonefrost_fx` effect, and the kit `glow` material (cold fire, runes, crystal tips, pools, orbs). All other sprites (giants, Ulfar, trolls, golems, Hrimgard) use the palette only; their glow comes from fx and lights.

## Added 2026-10-16
Stonefrost II/III fx, real waystone + cairn kit pieces (replace the stand-ins; not yet placed in the demo scene layouts, so scene luma is unchanged), Flurry neon twin as the primary sheet. check-sprite was not re-run (no sprite sheet changed; fx and kit are not sprites).

## Left / not done
Hall of Hearthstones interior, Hjordis shield-wall pose, giant goat mount (Clatter) and Rimebreaker prop. Not in the brief's priority list.

## Questions
1. Hrimgard is 144x224 (7x). Fine, or 6x like Gorrak?
2. Ulfar is drawn at 3x with `combat_scale` 2.4 in the meta; should the engine scale the sprite down, or do you want a second 2.4x sheet?
3. (FYI, no question) the scoped `pet_flurry` allow-list entry is in the repo; `flurry_neon.png` is primary and `flurry.png` the fallback.
4. Day renders only exist for Stonehollow (caves and Barrow are interior). OK?
