# Helheim progress (branch realm-helheim, worktree /workspace/hd2d-hel)

## RESUME HERE
- Check the chunk table below; a step marked done is not redone. Done markers for detached jobs: /workspace/.hm-logs/hel/*.done.
- Rebuild one area (private dir): `cd games/hearthmoor && HM_BUILD_TMP=/tmp/hel_build python3 build.py --areas <a> --no-zip`, then `python3 tools/hearthmoor/hel_art.py <a>` (repo root), then `python3 -c "import build; build.write_pwa()"`.
- Specs come from `areas/src/gen/gen_helheim.py` (re-run overwrites the five specs).

## Chunks
| Chunk | State |
|---|---|
| worktree + branch off origin/main (32b2fe4) | done |
| specs (gen_helheim.py): helheim, hh_shore, hh_archive, ossuary (O1-O5), ossuary2 (O6-O9); each a 1.34 m ledge + stair | done |
| build (HM_BUILD_TMP=/tmp/hel_build) | done |
| hel_art.py installer (add / overwrite only) | done |
| game/helheim.js + game.js hooks | in progress |
| smoke_helheim.py | todo |
| quick-load every area | todo |
| smoke_helheim + touched groups after the last code commit | todo |
| check_scene --quick per area (lowres, one at a time) | todo |
| pictures in /workspace/alf_qa/hel/ | todo |
| Art follow-up (READY 03:26): violet main sheets + scoped HH_NEON_ALLOW (5 roles, #a45cf0 / #3a2458) + bone-white walls pulled via hel_art.py | done |

## Decisions (final, from Bill)
- `redeemable` really lives in `game/niflheim.js` (story 8.2, `export const redeemable`); helheim.js imports it (and `lockedBy`, which carries `NIFL_MUSP_LOCK`) from there. Not changed.
- Helheim is a stance only (`S.flags.hel` = kind / defiant), never an alliance, outside the 4-ally cap, and never marches in the finale.
- A fallen ally dragged back by force returns `pale` (`S.flags.bh_pale`): cosmetic only, no stat changes.
- Mordrath removes one finale wave (`finaleWaves(S, base)`).
- The Muspelheim lock stays behind `NIFL_MUSP_LOCK` (niflheim.js; Eira's locked branch reads `lockedBy`).

## Art notes
- The staging pack changed after READY.txt (03:19): neon sheets for gloam_knight / odric / mordrath (#a45cf0, #3a2458) plus `_safe` twins. Until READY.txt updates, hel_art.py installs the `_safe` twins (HEL_NEON_SCOPE empty).

## Status 2026-10-21 05:35 EDT
- game/helheim.js (areas, quests, stance, talk, gate) + game/helheim_boss.js (foes, Vesperin, Mordrath): split into real modules after the single-file write hit a review error. game.js [HELHEIM] hooks; smoke.py [HELHEIM] block.
- preflight PASS. smoke_helheim PASS 27/27 (alf_qa/hel/sm4). niflheim.js untouched (redeemable only imported), so smoke_niflheim not required.
- check_scene --quick: helheim FAIL (sprites_sharp / colours / phone: NPCs overlapped by fx, roofs and each other) -> NPCs moved (09d8dc0), recheck queued; hh_shore FAIL (grades night_warm_frac 0.0017 < 0.002: no warm light in the shore; effects_sharp glowplant_toadcap 0.93) - no allowed lever fixes these; hh_archive PASS; ossuary / ossuary2 pending.
- check_palette (not edited): flags hhelite odric, hhenemy gloam_knight, boss_mordrath mordrath/_p2/_p3 for #3a2458 / #a45cf0 (its sprite rows only know biome + NEON_PETS_ALLOW).
- Leftovers: audio REALM_OF untouched; Inkling flag only (not in PETS).
