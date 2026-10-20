# Asgard progress (branch realm-asgard)

## RESUME HERE
- All 5 areas pass check_scene --quick (gs_temple: NO_LIGHT windows + per-grade window glow; reliquary: wraiths off the portrait edge).
- Next: the full smoke_asgard after the last code commit (`/workspace/alf_qa/asg/run_load.sh /workspace/alf_qa/asg/fsa`, done file fsa/done), then the pictures (smoke shots: area_*, room_g1..g9, boss_*), then the final report.
- QA scripts: /workspace/alf_qa/asg/ (HM_BUILD_TMP=/workspace/alf_qa/asg/hmbuild, profile chrome-profile-nifl, lock /workspace/.hm-logs/browser-mb.lock, jobs via tools/heavy.sh after preflight).

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
