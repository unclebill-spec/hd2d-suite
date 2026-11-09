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
- 2026-10-30 17:10 ET, Hearthmoor Story, /workspace/hearthmoor-staging/story/: asgard.md now has section 12a, a paste-ready JS block (main game/asgard.js data half + a fun pass that wraps TALK only: Nessa/Bodil/folk quips and the secret of Alrik's crooked rune, flag as_alrik_secret). Section 5.2 choice now uses {id, options}. vanaheim.md 11 re-checked (node --check OK).
- 2026-10-28 22:00 ET, Hearthmoor Story, /workspace/hearthmoor-staging/story/: vanaheim.md has GD Q1-Q7, the boss tuning and the spare reward (nettle_circlet + embassy rank); finale.md adds the FOE_CAPTAINS Nettlecrown line; open Qs in ambient_barks.md and side_quests.md are answered; verdant_heart Decision 2 is closed.
- 2026-10-23, checks-upgrade: check-sprite now also checks holes / limbs / 1px outline / soft alpha (current art allowlisted in tools/check-sprite/art_allowlist.txt); Hearthmoor Art usage: staging/HANDOFF-art-checks.md. Pre-publish secret scan now runs tools/checks/extra_secret_patterns.sh + gitleaks (branch checks-upgrade).
- 2026-10-24 (HD-2D Cozy Builder): TOP ITEM when Hearthmoor resumes: Bill says the menus look generic and bland. Give them a full themed restyle like Gravewake's menus (framed panels, themed pixel fonts, gloom-and-glow), then screenshots and game-qa (rule 19).
- 2026-10-25 (Hearthmoor Story): /workspace/hearthmoor-staging/story/ has batch1_text.md, plus full playable scripts in side_quests.md, finale.md and rift_breaker.md (dialogue, choices, flags, bosses, epilogues, node-checked JS); helheim.md Q1-Q4 resolved and its import fixed; NIFL_MUSP_LOCK left open; forge, alchemy and glow-fish text stays on main. NIFL_MUSP_LOCK = B (Bill): on merge set NIFL_MUSP_LOCK = false and add cinderProof to redeemable (niflheim.md 8.2); new quest mp_witness / S.evidence.cinderhold (muspelheim.md 3.13).
- 2026-10-25 (Hearthmoor Story): /workspace/hearthmoor-staging/story/: Bill lifted the REVERSE lock too: befriending Niflheim no longer greys Muspelheim's befriend. On merge, in game/muspelheim.js WARDEN_OPTIONS grey only on allyCount>=4 (drop the '(Locked. You stand with Niflheim.)' branch), set mp_frostfriend + always mp_walk when lockedBy; keep lockRival calls as marks; new scene Cinder-Tea on the Doorstep (muspelheim.md 1.1 merge steps, 3.2a).
- 2026-10-26 (Hearthmoor Story): /workspace/hearthmoor-staging/story/vanaheim.md: full Vanaheim (Mossbrook) realm arc around verdant_heart.md; new game/vanaheim.js block (quests vh_hex/vh_thorn/vh_tobble/vh_tithe/vh_bloom/vh_staff, boss Mother Nettlecrown, cap check on Burrowmoss befriend); 7 open questions at the bottom.
- 2026-10-26 (Hearthmoor Story): /workspace/hearthmoor-staging/story/ambient_barks.md: 182 ambient barks (Midgard + 8 realms; any/befriended/conquered/redeemed) + 27-entry lore codex + paste-ready BARKS/CODEX JS block (node --check OK). NEW data table for the lead to wire up; open questions at the bottom.
- 2026-10-28 (Hearthmoor Sound): /workspace/hearthmoor-staging/sound/music/music_mossbrook.ogg (+ gen_mossbrook.py): Mossbrook/Vanaheim theme, 96 bpm D Dorian, 8 bars = 20.00 s, 78 KB, -15.9 LUFS / TP -2.7; for vanaheim, vh_village, vh_garden, rotwood, verdant (README row in staging music/README.md); unheard.
- 2026-10-28 (Hearthmoor Sound): /workspace/hearthmoor-staging/sound/music/music_helheim.ogg (+ gen_helheim.py): Helheim "eerie but kind" waltz, 84 bpm 3/4 G minor, 8 bars = 17.14 s, 45 KB, -16.0 LUFS / TP -4.6; for helheim, hh_shore, hh_archive, ossuary, ossuary2 (ids unverified on main). Also sfx/EVENT_MAP.md (SFX pack 1 -> sfx() call sites, gaps). Unheard.
- 2026-10-30 17:30 ET, Hearthmoor Sound, /workspace/hearthmoor-staging/sound/sfx/pack2/: SFX Pack 2 = 45 files (~550 KB) filling all 17 EVENT_MAP gaps + fun-pass juice (hit/pickup/coin/click variants, 5 stingers); call sites in pack2/README.md, EVENT_MAP.md updated, licenses in sound/LICENSES.md.
- 2026-10-30 22:53 ET, Hearthmoor Sound, /workspace/hearthmoor-staging/sound/: music/music_asgard.ogg (+gen_asgard.py, 8-bar golden/melancholy loop, 26.67 s, -16 LUFS) and music/music_attract.ogg (+gen_attract.py, 28.5 s non-looping title cue); sfx/pack3/ = thunder_rune x3, raven_caw x3, amb_asgard_loop (README has triggers); LICENSES.md now has Pack 1 rows + audit note; unheard.
- 2026-11-02 19:27 ET, Hearthmoor Story, /workspace/hearthmoor-staging/story/liss_hint_foresight.md: fix list items 2 and 8. Liss's next-Bloomtide hint (bloomHint, nightsToBloom, two nymph_vh lines) and the Foresight Charm item (name, description, giveForesight bag-item block in the Bean-Circlet shape; Cozy wires the after-dodge crit buff). node --check OK.
- 2026-10-30 22:56 ET, Hearthmoor Story, /workspace/hearthmoor-staging/story/: ingrith_repo_fixes.md (old->new art strings: Ingrith cream/gold -> icy-blue + ash-silver, gold only circlet/pin; repo untouched), vanaheim_stage_c.md (Growth school, Bloomtide, Mossheart Staff, side bits, Veyra bloom, Hushed Mossbrook; new game/vanaheim_c.js, node --check OK), demo_captions.md (DEMO_CAPTIONS for attract.js badge on hearthmoor-attract-1030).

- 2026-11-02 19:30 ET, Hearthmoor Sound, /workspace/hearthmoor-staging/sound/sfx/bloomtide/: fix-list #9. Bloomtide (bloom_fun.js) only uses procedural G.audio.sfx() plucks, and the build ships no SFX files, so Pack 2 needs a file loader + sw.js entries. 3 new SFX (bloom_perfect, bloom_miss, bloom_lose) + exact call-site wiring in README.md; hit -> pack2 harvest/pickup_juice, win -> pack2 stinger_quest_complete. Unheard.
- 2026-11-04 06:30 ET, Hearthmoor Sound, READY NOW for this push: /workspace/hearthmoor-staging/sound/ = sfx/ Pack 1 (39) + sfx/pack2/ (45) + sfx/pack3/ (7) + sfx/bloomtide/ (3, wiring in its README) + music/music_helheim.ogg + music/music_mossbrook.ogg; licenses in sound/LICENSES.md. NOT in this push: music_asgard (waits for Will's listen), music_attract (on hold). Nothing new started; sound pauses after this.
- 2026-11-02 22:24 ET, HD-2D Cozy Builder: PUBLISHED hearthmoor-tue-1103 @ 6299ce7 (live, HTTP 200, core-e409cee404; rollback tag hearthmoor-rollback-20261102-e1f601d; log /workspace/.hm-logs/tue-1103-publish/publish.log). The Nov 3 9 PM bundle now starts from 6299ce7. Not included: MB mb-smoke-stall-1102b (760ae47). Follow-ups: temple.js:62 faceless_gaze (add the row or drop the reference), 34 unwired hm_fx48 effects, MB harness PNG-size TODO (smoke checks json height, not real PNG height).
- 2026-11-09 11:45 ET, Hearthmoor Story, /workspace/hearthmoor-staging/story/intro.md: Lantern Eve intro v2 (unnamed blue-eyed Veyra silhouette cracks the Rift, bubble banter, false ember-sigil) + ! tutorial quest Lanterns Down (eve_watch); paste-ready data.js block (intro_data.js, node --check OK, test 0 fails); intro.js/setHeroUI hooks listed in section 4c for Grok Build.
## RESUME HERE: attract demo (HELD by Will via GD, 2026-10-30 11:00 PM ET)
Will: one more demo run tonight, then hold all demo work. GD decides tomorrow whether it goes to Rule 19 as is.
- Branch hearthmoor-attract-1030 @ b8bed2b (worktree /tmp/hm-attract-1030). Captions + neon blue badge are on hearthmoor-attract-cap @ 82e71bb (worktree /tmp/hm-attract-cap, one commit on b8bed2b, attract.js only). Not merged into the attract branch yet.
- Passed at b8bed2b: smoke_attract (attract4.log), check-scene 10/10 (cs_a 9/10 + prismvault retry cs_prism2 PASS), shard 3/4 355/355.
- Failed at b8bed2b on box browser/WebGL errors (not game errors): shard 1 (TargetClosed), shard 2 (WebGL preflight), shard 4 (TargetClosed). Retries CANCELLED per Will/GD; none started.
- The one last run is the 82e71bb smoke_attract (2 scenes + shots) -> /workspace/.hm-logs/attract-1030/cap/smoke_attract.out.
- Still to do when unheld: GD's Rule 19 call, fast-forward attract to 82e71bb, rule19-handoff.md, gitleaks 2bfe9ff..HEAD, EB, GD OK, publish (rollback tag at the live head). Sound's music_attract.ogg is on hold too.
- Logs: /workspace/.hm-logs/attract-1030/ (notes.md, rest.log).
