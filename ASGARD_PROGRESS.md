# Asgard progress (branch realm-asgard)

## RESUME HERE
- asgard: check_scene --quick PASS (b3fc463). origin/main merged (tests/preflight.sh, tools/heavy.sh, T.check); chk.sh / run_load.sh now run preflight (HM_IN_BROWSER_LOCK=1 under browser-mb.lock) and wrap jobs in tools/heavy.sh.
- gs_hall: 1st check failed sprites_sharp (lordwarden off the top edge behind the throne; fridleif on a gold pool). Moved lordwarden -> [-2.6,-4.4], fridleif -> [4.4,1.6]; rebuilt. The re-check (/workspace/alf_qa/asg/c_hall) was queued on heavy.sh (both slots held by other bots' smokes) -- re-run: `chk.sh /workspace/alf_qa/asg/c_hall gs_hall`.
- Then gs_temple, reliquary, reliquary2 (one at a time), commit + push each; then the full smoke_asgard (`run_load.sh <out>`) after the last code commit (switch retryable steps to T.check); pictures.
- QA scripts: /workspace/alf_qa/asg/ (HM_BUILD_TMP=/workspace/alf_qa/asg/hmbuild, profile chrome-profile-nifl, lock /workspace/.hm-logs/browser-mb.lock).

## Areas
| Area | Spec | Built | check_scene | Committed |
|---|---|---|---|---|
| asgard | yes | yes | PASS | yes |
| gs_hall | yes | yes | PASS | yes |
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
