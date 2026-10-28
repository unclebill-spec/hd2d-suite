# Hearthmoor handoff
_

**Owner:** HD-2D Cozy Builder (single owner). Hearthmoor Art / Sound / Story and Master Builder drop work in `/workspace/hd2d-suite/staging/` (or `/workspace/hearthmoor-staging/`) and add a line under "Inbox" below instead of waking the owner.

## Goal
HD-2D cozy game (16-bit billboard actors in a lit 3D diorama). Live: unclebill-spec.github.io/hd2d-suite/games/hearthmoor/. Repo: /workspace/hd2d-suite (github unclebill-spec/hd2d-suite).

## Current state
- Last commits on main (Oct 21): Asgard music track, Asgard areas, PWA + zip builds for asgard-merge / asgard-music.
- Realm progress logs: repo root `*_PROGRESS.md` (Alfheim, Asgard, Jotunheim, Muspelheim, Svartalfheim) and `games/hearthmoor/NIFLHEIM_PROGRESS.md` (has a RESUME HERE block).
- Oct 22 cleanup: 19 realm/merge worktrees whose commits were all in origin/main were removed (branches kept). The leftover worktrees are resolved (2026-10-28, see Next action).
- Next realm and open bugs: see Next action below and the root HANDOFF.md.

## Key paths
- Game: `games/hearthmoor/` (build.py, engine/, areas/, art/, audio/, tests/, RESTORE.md)
- Story source of truth: `docs/story/STORY_SEEDS.md`, `docs/story/DESIGN_EXPA*`
- Rules: repo `AGENTS.md`, `CHANGELOG.md`

## Next action
### RESUME HERE (2026-10-28)
- Owner: HD-2D Cozy Builder.
- Current branch: `hearthmoor-stagea-1028` (from origin/main ca3ef0b; pushed, NOT live): Niflheim option B (`NIFL_MUSP_LOCK = false`, `cinderProof` in `redeemable`), The Ember Witness (`mp_witness`, `S.evidence.cinderhold = 'ember_witness'`), Lantern Eve Esc/B closes the quest log before skipping, phone Options last-row padding.
- The 3 old leftover worktrees are resolved: cold-cauldron and hearthmoor-leftovers-wip are archived as tags `archive/cold-cauldron` and `archive/hearthmoor-leftovers-wip`; the menu restyle and the Muspelheim frost-friend work are live.
- NEXT: the Vanaheim realm from `/workspace/hearthmoor-staging/story/vanaheim.md` (needs a data.js `allyCount` export, `yieldAt` and `G.startBoss` hooks like verdant_heart). Boss Mother Nettlecrown's difficulty goes to Game Director BEFORE building.
- Remaining merge queue: `ambient_barks.md`; Kindle / Hrefna optional lines.

## Inbox (non-owner bots append here: date, bot, staging path, one line)
- 2026-10-23, checks-upgrade: check-sprite now also checks holes / limbs / 1px outline / soft alpha (current art allowlisted in tools/check-sprite/art_allowlist.txt); Hearthmoor Art usage: staging/HANDOFF-art-checks.md. Pre-publish secret scan now runs tools/checks/extra_secret_patterns.sh + gitleaks (branch checks-upgrade).
- 2026-10-24 (HD-2D Cozy Builder): TOP ITEM when Hearthmoor resumes: Bill says the menus look generic and bland. Give them a full themed restyle like Gravewake's menus (framed panels, themed pixel fonts, gloom-and-glow), then screenshots and game-qa (rule 19).
