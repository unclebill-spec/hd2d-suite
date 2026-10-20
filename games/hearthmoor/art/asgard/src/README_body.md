# Asgard pack: Goldspire (hub, Thunder Hall, Dawn Temple) + the Gilded Reliquary (G1-G9)

Art seat, 2026-10-19. Story: `story/asgard.md`. Rebuild: `cd src && python3 gen_asgard.py` (`NF_RESHEETS=1` re-renders + re-checks the sheets). `bill-asset-library` pulled (already up to date): nothing Asgard-specific to reuse. Reused own copies of the Niflheim/Jotunheim engine, the golem body, the rune bridge + waystone and the env fx code.

![contact sheet](contact_sheet.png)  Scenes: `renders/scene_asgard_night|day`, `scene_gs_hall_night|day`, `scene_gs_temple_night`, `scene_reliquary_g1..g9_night`

| sheet | roles | frame / scale |
|---|---|---|
| `sprite/as_folk` | envoy_as, lordwarden, runemaster, priestess, fridleif, groom, as_trader, as_guide | 40x44, idle+walk, 1x |
| `sprite/as_sigrun` | sigrun (companion; wings = fx `sigrun_wings`; no pet) | 40x44, 1.1x, idle/walk/cast/attack |
| `sprite/as_enemies` | light_wraith 1.2x, storm_sentinel 1.8x, storm_centaur 1.6x, gilded_inquisitor 1x | 64x72, idle/walk/attack/die |
| `sprite/as_elites` | severin 3x, storm_sentinel_gate 2x, fridleif_boss 3x, centaurchamp 2.5x, elderwraith 3x | 100x112 |
| `sprite/boss_sentinel` | sentinelprime / sentinel_p2 (open core) / sentinel_p3 (overload), **5x** golem | 144x200 (4032x2400) |
| `sprite/boss_aurelion` | aurelion, aurelion_p3 (red), aurelion_wraith (P2 copy, no shadow), **aurelion_rest** (kneel, sword planted: befriend/outro), **7x**, gilded plate | 144x224 (4032x3584) |
| `kit/*.glb` + `kit.json` | 29 pieces incl. **gold_ledge + gold_stair (1.34 m)**, keep_clear markers | renders `renders/*_night.png` |
| `gamefx/as_fx` | 35 fx: pools (gold/cold/violet/red), lightning_arc, strike_warning + strike_bolt, chain_lightning, rune_beam + telegraph_line, beam_ring, light_drain, dawn_flame (+red), relight_burst, wraith_split, tile_flash, sigrun_wings, dive_strike, raven_guard, **as_shadow (mid-dark #5a5068/#7a7090)**, gold dust, rain, rime_tell, ... | 48 px |

Bosses are drawn wide and column-squeezed into the 144 px cap (like boss_vharzul / boss_veyra). Folk wear separate top + bottom, belt, shoes; plate only on Aurelion. Boss_sheet layout: idle 0-3, walk 4-7, cast 8-11, attack 12-15, die 24-27.

## Placement
- Every area and G-room: `gold_ledge` pair + ONE `gold_stair` (7 x 0.191 m = 1.34 m), stair centre z = ledge z + 2.75, climbs -z.
- Keep clear: stair footprint +1 m, ledge edges 1.5 m, arch arrival [0,9.2] 2.6 m, hall door 2.5 m, Reliquary door 3 m, altar/springs 2 m. Scenes keep fx/decals off spawns, stairs, ledge edges.
- Boss stands: Sentinel G4 [0,0,-0.6], Severin G5 [0,0,-2.6], Aurelion G9 [0,0,-1.4] (throne at -5.2).
- Luma measured: {{LUMA}}. Please run check-scene in the build.

## Check-sprite (once per sheet)
{{CHECKS}}.

## Neon
Neon only in gamefx and the kit `glow` material (#3fb8ff/#e8f6ff blue, #a45cf0/#d4a8ff violet). **No sprite uses neon** → no palette-safe twins and **no allow-list entries needed**.

## Left
Item icons; Sigrun wing sprite frames (fx only); centaur human torso is small; per-room puzzle logic (G5 tile pattern, G7 lit-rune order) is runtime.

## Questions
1. Aurelion's rest pose is a separate role (`aurelion_rest`, idle/walk). OK, or fold into the main role?
2. Sigrun's wings as an fx overlay rather than in-sprite: OK?
3. Storm Sentinel Prime (G4) vs the hub/gate sentinels: is G4 really the golem boss room, or should it be G9-adjacent?
