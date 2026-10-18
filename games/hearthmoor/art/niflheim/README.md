# Niflheim pack: Mistmere, the Quiet Shore, the Glowpool Caverns, the Frozen Spire (F1-F10), the Crown of Ice

Art seat, 2026-10-18. Story: `story/niflheim.md`. Rebuild: `cd src && python3 gen_niflheim.py` (Pillow + numpy; repo read-only; `gen_sheets.py` re-renders + checks the sheets, `NF_RESHEETS=1` forces it, otherwise the stored sheets + `check_sprite_report.json` are reused).
Library checked first (`bill-asset-library` pulled, index + CATALOG-EXISTING read): no ice-kin folk, mist or frost creatures to reuse. **Reused from Jotunheim (own copies in `src/`):** the ice kit set (snow/ice floor, wall, lake, glow pool, icicles, crystals, rune pillar, barrow door -> Spire mouth, rune bridge -> F8 Rime Bridge, ice throne -> Kael's perch, waystone, cairn, orb chain, braziers, warm lantern), the ice-golem body (Ice Golem + Glacier Colossus), and the environment fx code (pools, aurora, fireflies, vines, fog, rune pulse). Nothing added to REQUESTS.md.

![contact sheet](contact_sheet.png)  Scenes in `renders/`: `scene_niflheim_night|day`, `scene_nf_home_night|day`, `scene_iceglow_night`, `scene_spire_f1..f10_night`, `scene_frozen_rift_night`

| sheet | roles | frame / scale |
|---|---|---|
| `sprite/nf_folk` | gatewright (Halvard), frostspeaker (Gudrun Hoarwick), veyra (before the plate, **1.2x**), eira (memory; outline = fx), nf_trader (Tove), elkman (Ketil), archivist (Vigdis), brisa (captain NPC) | 40x44, idle+walk, **1x** (veyra 1.2x) |
| `sprite/nf_hrefna` | hrefna (companion): idle 0-3, walk 4-7 (= follow), cast 8-11 (ice lance / mist veil). **NO pet in this realm.** | 40x44, 1x |
| `sprite/nf_enemies` | frost_spirit 1.2x, mist_stalker 1.5x, ice_golem 1.8x, frost_wraith 1.4x, ice_warden 1x (elite, no plate) | 56x68, idle/walk/attack/die |
| `sprite/nf_elites` | brisa_mini 3x (mini-boss, conquer-only), mistalpha 2x (rare), spiritprime 3x (rare), kael_bat 2x (Kael's bat forms) | 88x100, idle/walk/attack/die |
| `sprite/boss_colossus` | colossus (P1), colossus_p2 (core exposed), colossus_p3 (runes dim), all **6x** | 144x200, idle/walk/attack/die |
| `sprite/boss_kael` | kael, kael_p3 (plate frosted white), **5.5x**, black-iron plate, red-lined cape, frost-fang helm | 144x190, idle/walk/cast/attack/die |
| `sprite/boss_veyra` | veyra_p1 Mist **5x**, veyra_p2 Freeze 5x, veyra_p3 Warden **6x** (spikes, red cracks), veyra_p4 Ask 5x (idle/walk/die only: she stops attacking, lantern low; die = she dissolves), veyra_clone (mist clone: pale, dithered, no shadow/breath) | 144x200 (28 cols x 20 rows = 4032 x 4000), rime-plate over a violet-black coat, crown of runes, frost-lantern in the left hand |
| `kit/*.glb` + `kit.json` | 39 pieces: Mistmere (arch, lantern posts, speaker hall, fish stall, elk paddock, Eira's grave, Ashmantle House, shard window, springs, rune hall, glow vines), caves + Spire (ice set, Spire gate, banners, mirror panes, glacier heart, archive tablets, crown stair, frozen portal, crown platform, Spire pillar), **frost_ledge + frost_stair (1.34 m)**. Every piece has placement / keep_clear markers | `src/kit_nif.py`, renders `renders/*_night.png` |
| `gamefx/nf_fx` | 45 effects, 48 px: pools (cold, teal, aurora, violet, warm), aurora, cold + violet flames, ice sparkles, fireflies / wisps (blue, green, violet), glow orbs (blue, green, violet), glow vines + crystals, glow fog, mist drift + violet mist, rune pulse, spring bubbles, lantern float, Eira's outline; **spells / boss**: ice_lance, frost_nova, mist_veil, mist_clone_puff, portal_freeze / thaw, coldfire_beam + beam_ring (red telegraph), grief_crack, breath_fog + veyra_shadow (her tell), lantern_change, kael_bite, bat_split, banner_burn, colossus_slam, ice_block, core_pulse, spirit_swarm | 48 px |

Big frames use the boss_sheet layout (pivot bottom centre, idle 0-3, walk 4-7, cast 8-11, attack 12-15, die 24-27). Everyone in a town / elite role wears real tops and bottoms with a visible belt and shoes (Hrefna: slate tunic, short belted skirt over grey leggings, boots, blue scarf, cold-fire lantern). No onesies, no padding, no robes-as-body. **Plate appears only on the bosses** (Kael black iron, Veyra rime-plate; the Colossus is an ice golem, not plate; Ice Wardens and Brisa wear tunics + jerkins). Veyra's four phases: mist and shadow tells are fx (`breath_fog`, `veyra_shadow`), the clone sprite has neither.

## Placement notes (also in `metadata/niflheim.json`, `metadata/niflheim_layout.json` and `kit/kit.json` markers)
- **Real height in every area and room:** 1.34 m terrace = pairs of `frost_ledge` + ONE `frost_stair` (7 steps x 0.191 m, 2 m wide) centred on the front face (stair centre z = ledge z + 2.75, climbs toward -z, rot pi for +z). Mistmere: the frost-speaker terrace; nf_home: shore terrace; iceglow: ledge beside the Spire mouth; Spire F1-F10: one ledge + stair each (F10 also has the 10-step crown stair); frozen_rift: the landing the hero arrives on.
- **Keep clear:** nothing on a stair footprint +1 m each end; props >= 1.5 m behind a ledge's front edge; 2.6 m at the Bifrost arrival [0,9.2]; speaker hall / rune hall doors 2 m, Ashmantle House door 1.8 m, Spire mouth 3 m, Eira's grave 2 m, springs 2 m. Decals and fx stay off spawns, stairs and ledge edges in all the scenes.
- **Boss stands:** Colossus F5 [0,0,4.0] off `glacier_heart`; Kael F9 [0,0,3.4] off `kael_perch`; Veyra frozen_rift [0,0.5,-3]. Tall bosses need the camera / arena padding (the scenes use `reach`).
- **Lighting:** day luma 55-70, night 20-30 with glow pools (cold blue, teal, aurora green, violet) AND a warm lantern / window pool every 6-8 m, so the grade is never all-dark-blue. Measured on my renders: niflheim_night 28.5, niflheim_day 66.2, nf_home_night 29.0, nf_home_day 65.5, iceglow_night 29.9, spire_f1_night 28.5, spire_f2_night 27.1, spire_f3_night 29.5, spire_f4_night 29.8, spire_f5_night 25.3, spire_f6_night 29.8, spire_f7_night 29.6, spire_f8_night 27.8, spire_f9_night 23.1, spire_f10_night 29.0, frozen_rift_night 22.2. The refs: cold fire #3fb8ff / core #e8f6ff, deep ice #1b2a4a, snow #c8d6ec, black water #0c1220; aurora #3fe0a0 -> #a45cf0. I can't run check-scene on a render (needs the built game); please run it once in the build.

## Check-sprite (once per sheet; sheets re-rendered after fixes were re-checked)
nf_folk PASS; nf_hrefna PASS; nf_enemies PASS; nf_elites PASS; boss_colossus PASS; boss_kael PASS; boss_veyra PASS. Details in `check_sprite_report.json`.

## Neon flag
Neon pixels: every `gamefx/nf_fx` effect and the kit `glow` material (cold fire, runes, crystals, aurora panes, violet lamps, springs, orbs). **No sprite uses neon**: Hrefna's lantern and cuffs, Veyra's lantern and crown runes, the Colossus core, Kael's eyes and the spirits are palette (sky / white / flower_blue, roof_hi red) and their glow comes from the fx + lights (`lantern_float`, `core_pulse`, `eira_outline`, ...). So **no check-sprite allow-list entries are needed** and there are no neon twins to ship. (If you want a neon-primary Hrefna like Kindle / Flurry: role `hrefna` -> `#1c62d8 #2ab4ff #a6ecff` would be the scoped entry; say so and I add the twin.)

## Left / not done
Item icons, the Hrefna companion's own spell fx beyond `ice_lance` / `mist_veil`, Ashmantle House *interior* (a scene, not kit), elk / fish props, Veyra cast frames for P4 (by design she does not attack), Ending B dissolve beyond the die frames, Mistwalker (dropped in the doc), per-room Spire layouts beyond the ledge + stair + centrepiece set.

## Questions
1. Veyra's four phases are separate roles (`veyra_p1`..`p4`) in one 5-role sheet (28 x 20 cells, 4032 x 4000 px). Should the engine instead read one role with a phase switch (smaller sheet)?
2. Brisa appears twice: `brisa` (1x captain NPC, in `nf_folk`) and `brisa_mini` (3x conquer-only mini-boss, in `nf_elites`). OK?
3. The doc's lake is at [0,-1]; I split it into two 4 x 4 m `ice_lake` pieces at z -0.6 to leave room for the speaker terrace stair. Fine?
4. Colossus width is squeezed to fit the 144 px boss-frame cap (a chunky ice golem). Want it wider on a 2-col-fewer layout (no cast/attack gap)?
