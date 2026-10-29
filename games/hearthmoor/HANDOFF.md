# Hearthmoor handoff
_

**Owner:** HD-2D Cozy Builder (single owner). Hearthmoor Art / Sound / Story and Master Builder drop work in `/workspace/hd2d-suite/staging/` (or `/workspace/hearthmoor-staging/`) and add a line under "Inbox" below instead of waking the owner.

## Goal
HD-2D cozy game (16-bit billboard actors in a lit 3D diorama). Live: unclebill-spec.github.io/hd2d-suite/games/hearthmoor/. Repo: /workspace/hd2d-suite (github unclebill-spec/hd2d-suite).

## Current state
- Last commits on main (Oct 21): Asgard music track, Asgard areas, PWA + zip builds for asgard-merge / asgard-music.
- Realm progress logs: repo root `*_PROGRESS.md` (Alfheim, Asgard, Jotunheim, Muspelheim, Svartalfheim) and `games/hearthmoor/NIFLHEIM_PROGRESS.md` (has a RESUME HERE block).
- Oct 22 cleanup: 19 realm/merge worktrees whose commits were all in origin/main were removed (branches kept). Still on disk with unmerged work: `/workspace/hd2d-cauldron` (cold-cauldron, 5 uncommitted), `/workspace/hd2d-niflheim` (1 uncommitted), `/workspace/hd2d-suite-leftovers` (hearthmoor-leftovers-wip, not in main).
- Unknown: which realm is next, open bugs.

## Key paths
- Game: `games/hearthmoor/` (build.py, engine/, areas/, art/, audio/, tests/, RESTORE.md)
- Story source of truth: `docs/story/STORY_SEEDS.md`, `docs/story/DESIGN_EXPA*`
- Rules: repo `AGENTS.md`, `CHANGELOG.md`

## Next action
Unknown. Owner: fill in the next realm/task and resolve the 3 leftover worktrees above.

## Inbox (non-owner bots append here: date, bot, staging path, one line)
- 2026-10-23, checks-upgrade: check-sprite now also checks holes / limbs / 1px outline / soft alpha (current art allowlisted in tools/check-sprite/art_allowlist.txt); Hearthmoor Art usage: staging/HANDOFF-art-checks.md. Pre-publish secret scan now runs tools/checks/extra_secret_patterns.sh + gitleaks (branch checks-upgrade).
- 2026-10-24 (HD-2D Cozy Builder): TOP ITEM when Hearthmoor resumes: Bill says the menus look generic and bland. Give them a full themed restyle like Gravewake's menus (framed panels, themed pixel fonts, gloom-and-glow), then screenshots and game-qa (rule 19).
- 2026-10-29, HD-2D Cozy Builder: Fun pass (art-fix): the 8 night warm lamps (fix1028: prismvault, caldera2, barrow, barrow2, clockdeep, ossuary, jt_hall, lumen_court) now 'catch' when the hero first walks within 2.6 of one at night: a 0.9 s light swell (x1.6 fading to the unchanged steady value) + 6 existing 'embers' particles; re-arms after walking >4.5 away. Engine: engine/main.js + tools/runtime/web/engine/main.js (identical). No lamp moved (jt_hall untouched), grade/colours/numbers unchanged; sw.js cache version bumped.
