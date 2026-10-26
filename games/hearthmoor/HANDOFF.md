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
- 2026-10-25 (Hearthmoor Story): /workspace/hearthmoor-staging/story/ has batch1_text.md, plus full playable scripts in side_quests.md, finale.md and rift_breaker.md (dialogue, choices, flags, bosses, epilogues, node-checked JS); helheim.md Q1-Q4 resolved and its import fixed; NIFL_MUSP_LOCK left open; forge, alchemy and glow-fish text stays on main. NIFL_MUSP_LOCK = B (Bill): on merge set NIFL_MUSP_LOCK = false and add cinderProof to redeemable (niflheim.md 8.2); new quest mp_witness / S.evidence.cinderhold (muspelheim.md 3.13).
- 2026-10-25 (Hearthmoor Story): /workspace/hearthmoor-staging/story/: Bill lifted the REVERSE lock too: befriending Niflheim no longer greys Muspelheim's befriend. On merge, in game/muspelheim.js WARDEN_OPTIONS grey only on allyCount>=4 (drop the '(Locked. You stand with Niflheim.)' branch), set mp_frostfriend + always mp_walk when lockedBy; keep lockRival calls as marks; new scene Cinder-Tea on the Doorstep (muspelheim.md 1.1 merge steps, 3.2a).
- 2026-10-26 (Hearthmoor Story): /workspace/hearthmoor-staging/story/vanaheim.md: full Vanaheim (Mossbrook) realm arc around verdant_heart.md; new game/vanaheim.js block (quests vh_hex/vh_thorn/vh_tobble/vh_tithe/vh_bloom/vh_staff, boss Mother Nettlecrown, cap check on Burrowmoss befriend); 7 open questions at the bottom.
- 2026-10-26 (Hearthmoor Story): /workspace/hearthmoor-staging/story/ambient_barks.md: 182 ambient barks (Midgard + 8 realms; any/befriended/conquered/redeemed) + 27-entry lore codex + paste-ready BARKS/CODEX JS block (node --check OK). NEW data table for the lead to wire up; open questions at the bottom.
