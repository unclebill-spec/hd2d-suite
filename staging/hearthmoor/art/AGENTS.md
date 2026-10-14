# Hearthmoor Art staging: status and next steps (for agents)

**State: PAUSED by Bill (2026-10-06). Don't start new Hearthmoor art until Bill resumes.**

## Rules
- Write only into /workspace/hearthmoor-staging/art/<folder>/. Never write to the repo. The lead (HD-2D Cozy Builder) integrates.
- Every pack has a README.md, contact_sheet.png, READY.txt, metadata JSON and a reproducible generator. It must pass the repo's check-sprite; any neon must be flagged in the README.
- Wrap any browser render in `flock /workspace/.hm-logs/browser.lock <cmd>`.
- To save tokens, send the lead one short message per finished pack. Details go in the README.
- Style: gloom and glow; neon blue cold fire, violet and red as signature glows. Characters wear real clothes with a separate top and bottom. Bosses are at least 5x and rares 2-3x. Neon is OK on pets, Lumi and glowing props; no neon on other character sprites.

## Done
pets (4), old_temple, verdant_heart, orb_lanterns, forge, alchemy, alfheim (+ lumi). The contact sheet in each folder is the quickest way to review it.

## Open items for the lead (repo edits)
- drawPortrait crops column 0 of the area atlas, which breaks for roles on their own sheet (Lumi, pets). Use lumi_portrait.png, or make drawPortrait read the role's own sheet.
- check-sprite needs scoped neon allow-list entries for `lumi` (and the new lime and pink neons).
- The check-sprite outline check fails broad-build characters holding a hammer.

## Next (when Bill resumes)
1. svartalfheim/: wait for the lead's brief (source: /workspace/hearthmoor-staging/story/svartalfheim.md). Scope: dark-elf and dwarf townsfolk; forge-red and rune-blue palette; violet crystal mines; Clockwork Deep kit; Gorrak Ironmaw at 6x (the only character in plate); rares and a mini-boss at 2.5-2.8x; Dagna as a companion; Tick the clockwork owl pet; the runaway construct at 2x. Partial generators are in svartalfheim/src/.
