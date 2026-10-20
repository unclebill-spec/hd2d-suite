# Asgard progress (branch realm-asgard)

## RESUME HERE
- WIP commit pushed (all 5 areas built + installed, asgard.js module, game.js hooks, smoke_asgard.py + smoke.py hook). Quick-load of all 5 areas: PASS, no JS errors.
- check_scene asgard: fixed so far: groom -> [9.6,-6.4], sigrun -> [-4.2,-3.2], start -> [-3.4,1.6], FX_SKIP rain + tile_flash (flat one-colour frames). Re-check of asgard in /workspace/alf_qa/asg/c_asgard.
- Next: asgard passing -> gs_hall -> gs_temple -> reliquary -> reliquary2 (chk.sh <out> <area>, one at a time; fix by moving actors / props / lamp caps), commit + push each; then the full smoke_asgard (run_load.sh <out>) after the last code commit; pictures.
- QA scripts: /workspace/alf_qa/asg/ (HM_BUILD_TMP=/workspace/alf_qa/asg/hmbuild, profile chrome-profile-nifl, lock /workspace/.hm-logs/browser-mb.lock).

## Areas
| Area | Spec | Built | check_scene | Committed |
|---|---|---|---|---|
| asgard | yes | yes | - | - |
| gs_hall | yes | yes | - | - |
| gs_temple | yes | yes | - | - |
| reliquary (G1-G5) | yes | yes | - | - |
| reliquary2 (G6-G9) | yes | yes | - | - |

## Decisions (lead 2026-10-19)
- aurelion_rest is its own role (swapped in on the befriend yield; the statue in gs_hall). Sigrun's wings are fx only. Sentinel Prime 5x, 3 phase roles, G4. Aurelion 7x, red P3, wraith copy.
- Befriend = an honourable rest. Low Vanaheim mood = soft cost: Vanaheim prices x1.2, the Elder's apology-letter offer withheld (no marker), a mead-cake / storm-charm gift restores it.
- Neon only in fx + kit glow; no neon sprites, no allow-list entries.

## Leftovers
- No guard sprite (the Inquisitor look stands in for as_guard / Fridleif).
- Ingrith at Bifrost is a look-spot (no sprite there).
- The G7 void reads as floor without tiles.
- Stormcaller's chain-lightning proc and the Thunder-Rune school need combat.js kinds (deferred, like Frostweave).
- Thunder Moot events (race / spear) are quest text only.
