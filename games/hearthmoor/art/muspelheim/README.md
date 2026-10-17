# Muspelheim pack: Cinderhold, Sigil Forge, Lavafalls, Ember Caldera (Vharzul the Ember Throne)

Art seat, 2026-10-17. Story: `story/muspelheim.md`. Rebuild: `cd src && python3 gen_muspelheim.py` (Pillow + numpy; repo read-only; reuses `pets/pets_gen.py` for Kindle; `MP_SKIP_SHEETS=1` skips the sheet re-render).
Library checked first (`bill-asset-library` pulled: nothing reusable for fire-realm folk, hounds or salamanders; only the glow-sprite ideas, already reused). Nothing added to REQUESTS.md.

![contact sheet](contact_sheet.png)  Scenes: `renders/scene_cinderhold_night.png` (+`_day`), `scene_sigil_forge_night`, `scene_lavafalls_night` (+`_day`), `scene_caldera_throne_night`

| sheet | roles | frame / scale |
|---|---|---|
| `sprite/mp_folk` | envoy_mp (Sunndis), springkeeper (Yrsa), lizardman (Orm), mp_trader (Svala), mp_guide (Grettir) | 40x44, idle+walk, **1x** ember-kin |
| `sprite/mp_giants` | warden_mp (Aska) 2.6x, forgejudge (Torka) 2.5x, cindercaptain (Dagny) 2.5x | 64x100, idle+walk |
| `pets/kindle*` | pet_kindle (ember salamander). **Primary `kindle_neon.png`** (`primary`/`image` in `kindle.json`), `kindle.png` = palette-safe fallback, same layout | pets layout 20x32, pivot [10,32], idle 0-3, walk 4-7, follow 8-11 |
| `sprite/mp_enemies` | ashen_cultist 1x, magma_hound 1.4x, flame_elemental 1.5x, fire_golem 2x | 56x68, idle/walk/attack/die |
| `sprite/mp_elites` | magma_hound_gate 2x, ashalpha 2x (rare), pyreling 3x (rare), kilnmother 3x (mini-boss) | 88x100, idle/walk/attack/die |
| `sprite/boss_vharzul` | vharzul (P1-2), vharzul_p3 (crown flares, taller blaze) | 144x256, **8x**, the only plate |
| `kit/*.glb` + `kit.json` | 38 pieces: Cinderhold (basalt floor, lava channel + pool, ledge, stair, Warden's stones, houses, forge hall, Red arch, stalls, braziers, shrine lamp, glass bridge, stable, anvil, dance ring, pillar, orb chain, spring, waystone, cairn), Sigil Forge (floor, wall, seat, cast bed, press, ledger, mould wall), Lavafalls (fall cliff, glass terrace, Caldera mouth arch with 3 seal-doors), Caldera (Ember Throne, Warden's lamps, furnace, hanging crystals, Cold Seam wall). Each has `keep_clear` / placement markers | `src/kit_muspel.py`, renders `renders/*_night.png` |
| `gamefx/mp_fx` | 43 effects, 48 px: pools (lava, forge, cold, violet, teal), lava_crawl, burn_patch, frost_vein, ember_motes, neon_embers, ash_fall, ember_storm, heat_shimmer, forge / cold / violet flames, lava_fall, steam, spring_bubbles, fireflies (blue, violet, red), glow frogs (blue, violet), glow vines + crystals (blue, violet), amber + neon glow orbs, **spells / boss**: fire_wave, magma_pool, ember_swarm, flame_ward, hound_summon, warm_ring_orange, pillar_telegraph, fire_pillar, crown_flare, molten_fist, warden_lamp | 48 px |
| `pets/kindle_fx` | aura + pool (+ safe twins), warm_ring (3 m heal), ember_dash, burn_patch | 32 px, pets format |

Big frames use the boss_sheet layout (pivot bottom centre, idle 0-3, walk 4-7, cast 8-11, attack 12-15, die 24-27). Everyone wears real tops and bottoms with a visible belt or sash and shoes (tunics, jerkins, aprons, belted trousers or kilt-trousers, boots). No onesies, no padding. Plate appears on Vharzul only (the cultists are hooded tunics with a wide sash). Vharzul's crown is palette-coloured, so the boss needs no allow-list entry; his die frames collapse into an ash heap with a last ember.

## Placement notes (also in `metadata/muspelheim.json`, `metadata/muspelheim_layout.json` and `kit/kit.json` markers)
- **Real height:** Cinderhold's Warden's terrace is 1.34 m (4 x `basalt_ledge`) with one `basalt_stair` (6 steps, 1.2 m rise, 2 m wide) on its front face; the Sigil Forge has a 1.34 m east gallery + stair, the Lavafalls a 1.34 m glass terrace + stair, the Caldera throne room a 1.34 m ledge + stair.
- **Keep clear:** nothing on a stair footprint +1 m each end; props >= 1.5 m behind a ledge's front edge; nothing within 2.6 m of the Red arch arrival [0,9.2]; 2.5 m in front of the forge-hall door, 1.8 m for house doors, 3 m at the Caldera mouth; nothing within 1 m of lava; the Warden's Walk stones stay clear; `burn_patch` only on open ground away from spawns and stairs.
- **Lighting:** day luma 55-70, night 20-30 with glow pools. Measured on my renders: cinderhold_night 24.9, cinderhold_day 60.4, sigil_forge_night 26.0, lavafalls_night 26.8, lavafalls_day 59.0, caldera_throne_night 25.1. Night ambient is a lifted warm grey; forge amber and lava orange carry the warmth, cold blue and violet are accents, so no grade is all red or all blue. I can't run check-scene on a render (it needs the built game), so please run it once in the build.
- **Lava:** `lava_channel` / pools carry a point light (radius ~4 m) plus `pool_lava` and the 4-frame `lava_crawl` decal; no bloom.

## Check-sprite (once per sheet)
mp_folk PASS; mp_giants PASS; mp_enemies PASS; boss_vharzul PASS; mp_elites PASS; kindle (safe) PASS; kindle_neon (needs scoped pet_kindle allow-list) PASS. Details in `check_sprite_report.json`. The kindle neon line is checked in-process with the entry below simulated (the repo is read-only for me); without that entry it fails only on the three neon-red hexes.

## Neon flag
Neon pixels: `pets/kindle_neon.png` (back spots, eyes glint, tail coal), every `gamefx/mp_fx` and `pets/kindle_fx` effect, and the kit `glow` material (lava, cold fire, violet lamps, crystals, springs, orbs). All other sprites (folk, giants, hounds, elementals, golems, Vharzul) use the palette only; their fire comes from palette lamp / gold / white and from fx and lights.
**Scoped allow-list entry needed in check-sprite (lead to add):** role `pet_kindle` -> `#a81c22 #e0302a #ff5a4a` (neon red lo / mid / hi, same hexes as the lantern-fox). `kindle.png` is the palette-safe fallback and passes without it.

## Left / not done
Doc section 11 item icons, the Emberfang prop, the mount lizard (Orm's "The Lizard That Chose You"), cast animations for Vharzul (layout has the slots; not drawn), a Hall of Wardens interior, Veyra's Cold Seam beat art, per-room Caldera layouts C1-C8 (the kit covers them; only the throne room C9 has a scene).

## Questions
1. Dagny is 2.5x here (roster) but the doc's section 8.2 says 3x. Which?
2. Ember-kin are drawn on a small 40x44 frame at 1x, fire-giants 2.5x on 64x100. OK, or do you want ember-kin on the 64x100 frame too?
3. Vharzul is 144x256 (8x; the 28-column boss layout caps frame width at 146 px, so his wings are folded close). Fine?
4. The Red arch carries a warm cream portal pane instead of a blue one so the hub stays warm; swap to cold blue?
