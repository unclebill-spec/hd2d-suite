# Asgard progress (branch realm-asgard)

## RESUME HERE
- DONE, ready for merge checks. All 5 areas pass check_scene --quick. Smokes at 269abd1: smoke_asgard PASS 47/47, smoke_alfheim PASS 8/8, smoke_niflheim PASS 63/63 (0 retries).
- Pictures: /workspace/alf_qa/asg/fsa/ (area_*.png, room_g1..g9.png, boss_sentinel_p1-3.png, boss_aurelion_p1-3.png, gs_hall_statue.png).
- If main moves before merge: merge origin/main, then re-run smoke_asgard (+ alfheim / niflheim).

## Areas
| Area | Spec | Built | check_scene | Committed |
|---|---|---|---|---|
| asgard | yes | yes | PASS | yes |
| gs_hall | yes | yes | PASS | yes |
| gs_temple | yes | yes | PASS | yes |
| reliquary (G1-G5) | yes | yes | PASS | yes |
| reliquary2 (G6-G9) | yes | yes | PASS | yes |

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
