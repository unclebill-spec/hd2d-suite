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
### RESUME HERE (2026-10-30, 16:00 ET)
- Owner: HD-2D Cozy Builder. Live main: 3855302 (Helheim #2 is live). Rollback point: tag `hearthmoor-rollback-20261030-60a1347` (60a1347, harness-1030, the state just before the Helheim publish).
- Rollback (no force): in a /tmp worktree off origin/main (never in /workspace/hd2d-suite, which is on checks-upgrade): `git fetch origin && git worktree add /tmp/hm-rollback origin/main && cd /tmp/hm-rollback && git revert --no-edit 60a1347..3855302 && git push origin HEAD:main` (reverts the whole range, newest first), then in /workspace/hd2d-suite `git fetch origin main:main` and `/workspace/tools/publish-game.sh hearthmoor`. Never `git revert HEAD` (that undoes only the last commit, a docs commit here). A force-push back to 60a1347 only with Will's OK. Tag a rollback point before every publish.
- Branch `hearthmoor-helheim-1030` (#2 Helheim): Rule 19 PASS, published; live at 3855302. Archive uses three small warm lanterns (GD call, BALANCE.md).
- In review: branch `hearthmoor-harness-1030b` (harness batch: self-sufficient smoke shards, measured shard timings, smokes leave the worktree clean, hero preview atlas guard, Pixel 7 hint bar wraps, ossuary2 title wraps, zip 75 -> 44.8 MB). Handoff: /workspace/.hm-logs/harness-1030b/rule19-handoff.md.
- NEXT: title attract demo (GD, Oct 30, Will's request), then #3 Asgard, then #7, #8, #12, #10, #9, #5, #4, #6, with #13 store last. Vanaheim #1 with Art/Story in parallel. No housing.
- Fun pass: done for Helheim (Inkling lines, motes).
- **Everything left to call Hearthmoor finished** (2026-10-28, from AGENTS.md, *_PROGRESS.md, STORY_SEEDS.md, staging story/art/sound):
  1. Vanaheim realm (Stage B, first playable ~Oct 31): game/vanaheim.js from staging vanaheim.md (paste-ready), Mother Nettlecrown, smoke_vanaheim.py; reuses areas vanaheim/rotwood/verdant, verdant.js, REALM_TEMPLATE. Needs a Vanaheim art pack (none in staging). L. Lead+Art+Story. GD call (Nettlecrown difficulty, vanaheim.md Q1-Q7).
  2. [RULE 19 PASS 2026-10-30 at 11b2e19, branch hearthmoor-helheim-1030; PUBLISHED: live at 3855302] music + REALM_OF + LICENSES, Inkling in PETS, fun pass, night warm accents (brazier in hh_shore and ossuary2, three small lanterns in hh_archive). smoke_helheim 29/29, check-scene all 5 areas PASS. Base was harness-1030 (60a1347).
  3. Asgard leftovers: guard sprite (as_guard/Fridleif), Ingrith sprite at Bifrost, G7 void tiles, Thunder-Rune school + Stormcaller proc (combat.js kinds, like Frostweave), Thunder Moot events beyond text. M. Lead+Art. GD call (new looks).
  4. Final Veyra arc + endings: finale.md (Frozen Rift, climbWaves, 4 endings) and rift_breaker.md (Breaker path, rb_eve switch, Veyra companion); neither is in game code yet; reuses redeemable/finaleWaves/Ember Witness. Niflheim's Join-Veyra stub hooks in here. L. Lead+Story+Art+Sound. GD call (ending, final boss).
  5. Mounts (goat from Jotunheim, lizard from Muspelheim; deferred, "needs mounts"). M. Lead+Art. GD call (new looks).
  6. NG+ secret heroes (1 per realm + Riftborn) and optional archangel superbosses (STORY_SEEDS). L. Lead+Art+Story. GD call (bosses, difficulty). Housing: not in the design docs, so not listed.
  7. Side quests (side_quests.md, sq_*) and batch1_text.md WIP sections (temple, verdant, stormwatch): not merged. M. Lead+Story.
  8. Ambient barks + codex (ambient_barks.md, 182 barks/27 entries, paste-ready; Q1-Q5 open) plus Kindle/Hrefna optional lines. S. Lead+Story.
  9. Per-realm leftovers, grouped: Svartalfheim (chestSense chests, Forgefire gating/decal, Council shortcut, forge-construct sprite, soot weather), Jotunheim (Stonehollow waystone model), Muspelheim (hound elsewhere, Emberfang ignite, Emberfall, Vharzul P3 frames, Caldera art scenes + Hall interior, cultists, Grettir skip), Niflheim (Ashmantle House interior, Hrefna fx, Spire room layouts, wall Wardens), Nettle jeweler, toadstool regrow. L. Lead+Art.
  10. Item icons (open in Muspelheim + Niflheim leftovers). M. Art.
  11. Fix standing check-scene failures: `grades` in barrow/barrow2/caldera2/clockdeep/prismvault (+effects_sharp prismvault); 37 areas time out on load in the check harness (same on main). M. Lead+Art.
  12. Audio pass: wire staging SFX pack 1 (40 files, footsteps/spells/UI) into Ambient.sfx; Helheim + Vanaheim tracks (staging has music_vanaheim.ogg); LICENSES rows. M. Sound+Lead. Needed before sale.
  13. Store/sale: no store-readiness doc exists; fuller audio (item 12) is the known blocker; menus restyle is live. Needs a GD call on platform/price, then store page + screenshots (reuse docs/screenshots). M. Lead+Art. GD call.

## Inbox (non-owner bots append here: date, bot, staging path, one line)
- 2026-10-31, Master Builder, branch mb-vanaheim-c-1030 (game/minigames/bloom*.js, art/minigames/bloomtide.json + bloomtide/bt_{caps,basket,glow_fx,sparkle_fx}.*, tests/smoke_bloom.py, tests/test_bloom_rules.mjs, tests/test_bloom_freeze.mjs): Vanaheim C Bloomtide harvest + dance timing-tap minigames, startBloomGame(G, kind) / G.bloomAction({act:'bloom_game', kind}); only write = S.flags.vh_bloom_games[kind] on win. GD calls: single tap, no spore-drizzle doubling, numbers approved; day clock + enemies frozen while open (freezeWorld: G.busy + ctx.clock.paused, restored on win/quit). Art (Hearthmoor Art, final): caps/glow/sparkle/basket + all-blue Liss (bt_liss_dance row 0 cols 4-7 while dancing, liss_vh_idle otherwise), loaded as own sheets from art/minigames/bloomtide/ (README option b); shared Seer rows and areas/* untouched; palette = cozy-village + NEON (check_palette 0 failing). check-sprite exit 1 on caps/basket/glow_fx/sparkle_fx is the character-only rules (4 facings etc.) on single-view props: GD-accepted, not fixed. FOR COZY at merge: the world NPC nymph_vh -> role liss_vh is yours, either (a) add role liss_vh as 4 rows in vanaheim/vh_village actors.png/.json (paste liss_vh_idle.png, add to sprite_roles, set "role": "liss_vh" on nymph_vh) or (b) load liss_vh_idle.png/.json as its own sheet (like hhinkling.png) and point nymph_vh at it; the files are in art/minigames/bloomtide/ and /workspace/hearthmoor-staging/art/vanaheim-bloomtide/. Gating/Liss dialogue wiring + sw.js precache of the new files are Cozy's. fun pass: done
- STOP (2026-10-31 02:31 ET, Master Builder): mb-vanaheim-c-1030, not merge-ready; browser smoke unverified, no shots. Code + art done (Liss final, palette 0 failing, 8 unit tests pass). Boot is fine: main 01fd760 and the branch both reach __hd2d.ready=true, busy=false within 9s with 0 console errors. Both smoke attempts (retry 3/3 at 1280x720 simscale 4; GD-authorised light run at 640x360 + 360x640, no simscale, no render-skip flag exists in ?qa/URL params) reach 'desk: ready 1s' then hang on the first page call (save snapshot / startBloomGame) with chrome-headless-shell gpu-proc at ~630-665% CPU (SwiftShader), killed by timeout 900 (EXIT 124). Not run: quit/save byte-unchanged, console-error check, 4 shots. ABCDES left to EB (Rule 19). Needs a real-GPU browser run of tests/smoke_bloom.py.
- EB Rule 19 @ 6bb57c5 (2026-10-31, FAIL; report /workspace/qa-reports/hearthmoor-vanaheim-c-6bb57c5-20261031.md). EB checked: diff scope (pass), unit tests 8/8, gitleaks/extra_secret_patterns clean, check_palette (177 failing on main AND branch, 0 new, 0 in minigames; my earlier '0 failing' was a narrower --areas none run), smoke_bloom no longer hangs ('; 0' fix) but 5/7 with the quit check failing, freeze (busy + clock.paused, restored), reduced motion, quit/loss localStorage byte-equal, 0 console errors. Unsure/unverified: ABCDES, in-browser timing windows + win path (SwiftShader ~16 fps), pad A, enemy position freeze. Confidence: sw.js defect high, smoke-test defect medium-high, tap-timing bias high. Fixed in one commit (MB 04:00 ET): sw.js regenerated via build.write_pwa() (16 minigame files precached, CACHE hearthmoor-v1-66ae0f6538; differs from EB's 7f440c984c because bloomtide.js changed); smoke_bloom quit/loss checks compare localStorage only, win check strips the ticking S.played/S.t (GD: playtime keeps ticking during minigames, no game change); tap() judges at st.now()-st.t0 (windows unchanged ±70/±150 ms). Awaiting EB re-run; not merged; Liss dialogue wiring is not ours.
- 2026-10-23, checks-upgrade: check-sprite now also checks holes / limbs / 1px outline / soft alpha (current art allowlisted in tools/check-sprite/art_allowlist.txt); Hearthmoor Art usage: staging/HANDOFF-art-checks.md. Pre-publish secret scan now runs tools/checks/extra_secret_patterns.sh + gitleaks (branch checks-upgrade).
- 2026-10-24 (HD-2D Cozy Builder): TOP ITEM when Hearthmoor resumes: Bill says the menus look generic and bland. Give them a full themed restyle like Gravewake's menus (framed panels, themed pixel fonts, gloom-and-glow), then screenshots and game-qa (rule 19).
- 2026-10-29, HD-2D Cozy Builder: Fun pass (Vanaheim Stage B): new game/vanaheim_fun.js (sfx/fx/shake helpers; CSS canvas shake OFF under the reduced-motion toggle/OS setting, boss hit-flash also skipped there). Stingers from existing audio.sfx: knot burn (spell + small shake), tithe-seal (save), frost-thorn root cut (hit + shake), fizzstone scoop (sparkle, rare 'fizzstone burps' line), Nettlecrown intro (summon + shake + flash), phase 2 (rumble + shake + flash), phase 3 (summon + shake + flash), heartroot grab (bigger shake), yield (quest stinger + sparkle); yield-to-dialogue dead time 900 -> 650 ms; rare knot line ('...and dwarf-work, honestly'). No rules, BALANCE numbers, controls, saves, palette or art changed; sw.js precache + cache version updated.
- 2026-10-29, HD-2D Cozy Builder: Fun pass (art-fix): the 8 night warm lamps (fix1028: prismvault, caldera2, barrow, barrow2, clockdeep, ossuary, jt_hall, lumen_court) now 'catch' when the hero first walks within 2.6 of one at night: a 0.9 s light swell (x1.6 fading to the unchanged steady value) + 6 existing 'embers' particles; re-arms after walking >4.5 away. Engine: engine/main.js + tools/runtime/web/engine/main.js (identical). No lamp moved (jt_hall untouched), grade/colours/numbers unchanged; sw.js cache version bumped.
- 2026-10-29, HD-2D Cozy Builder: Fun pass (GD picks, branch hearthmoor-fun2 = vanaheim-fun + artfix-fun): Settings 'shake' and 'flashes' toggles (per device; motion reduced / OS setting turns both off; all shake + hit-flash + storm lightning + lamp swell gated); Nettlecrown P3 thorn ring (visual only, THORNS_CLOSE_IN in game/vanaheim_fun.js, default OFF pending Will, QA ?thorns=1 / ?vhq=thorns); Mossbrook coin-in-the-spring + Spring-Wish Penny keepsake (?vhq=coin); bonus seed at Nettlecrown's stall, 10 %/buy, 1/day (?vhq=seed); lamp flare plays the wind-shimmer chime (engine hooks.onLampFlare/allowFlash). Numbers in BALANCE.md.

## RESUME HERE (2026-10-31 10:45 ET, HD-2D Cozy Builder)
- LIVE: main 6171246 (Asgard + Ingrith Rev 3 + BOSS_TRACKS gate). Rollback tag hearthmoor-rollback-20261031-01fd760; range revert 01fd760..6171246 (fixed command in /workspace/.hm-logs/asgard-1031/publish/publish.log). EB live check PASS; live SW activated at ~240 s (offline OK).
- IN PROGRESS: branch hearthmoor-vanaheim-c-merge = origin/main 6171246 + MB mb-vanaheim-c-1030 61bc1dd (merge 62dbe88), Liss/nymph_vh -> liss_vh Bloomtide options via G.bloomAction gated on vh_bloom 1 + bloom-night + befriend (58fa622), sw.js regen 6480 files, no .pyc (3d1aa1a).
- Tests @3d1aa1a: unit/check_all/check_palette ok; liss_check PASS; direct asgard load identical to 6171246 (0.8 s, 0 errors); smoke shard 3 PASS. Shards 1, 2, 4 FAIL on load waits: page ready and not busy but __hd2d.frames stops counting (render stall), in a different area each time (asgard, reliquary, vh_garden, niflheim). Merge diff doesn't touch those paths. Verdict: likely harness/SwiftShader starvation, medium confidence; needs a control run of shard 2 on 6171246. Logs and findings: /workspace/.hm-logs/vanaheim-c-1031/.
- NEXT: control shard 2 on 6171246, then EB Rule 19 on the merge SHA and GD OK. Then rebase N64's hearthmoor-sw-precache-split (81b180e). Attract demo HELD (82e71bb).

## RESUME HERE (2026-11-01 01:10 ET, HD-2D Cozy Builder): PAUSED for usage (GD, weekly 100%)
- Nothing running. Live main is still 6171246. Merge branch hearthmoor-vanaheim-c-merge is at this commit, on top of 8a9e7da.
- Shard 4 retry PASSED on the merge. Shard 3 PASS. Shards 1 and 2 still show render stalls (frames stop counting).
- The control run (shard 2 on 6171246) did NOT run: it was launched from the repo root (/tmp/hm-asg-r3/tests/smoke.py doesn't exist). On resume, run it from games/hearthmoor:
  `cd /tmp/hm-asg-r3/games/hearthmoor && HM_IN_BROWSER_LOCK=1 flock /workspace/.hm-logs/browser.lock timeout 1500 python3 tests/smoke.py --shard 2/4 > /workspace/.hm-logs/vanaheim-c-1031/control-6171246-shard2.log 2>&1`
- If the control stalls too, hand the merge SHA to EB for Rule 19. If it passes clean, debug the merge first. Wait for GD's go before resuming.

## RESUME HERE (2026-11-02 7:30 PM ET, Game Director): CHECK DAY fix list. Builders may resume.
- vhc-split fb24caa: **full Rule 19 PASS with notes; GD sign-off, CLEARED TO PUBLISH (Cozy).** Report: /workspace/qa-reports/checkday-2026-11-02.md. Run cap for Nov 2 is used (2/2).
Fix list, in priority order:
1. Cozy: before publishing, tag main `hearthmoor-rollback-20261102-6171246`; then `tools/publish-game.sh hearthmoor` (use `--no-qa` if still Nov 2 ET, since its live game-qa would hit the cap) and send GD the live SHA. GD live-checks Tue (run 1/2).
2. Cozy + Story: foresight_charm item code (ITEMS entry + effect per vanaheim_stage_c.md; Story name/desc); wire Art's staged bloom_token/foresight_charm icons (hearthmoor-staging/art/vanaheim-icons/).
3. Cozy (Systems) + Art: Vine Grasp "root" kind (snare); reuse existing root/vine FX.
4. Cozy + Art: Moss Golem summon reusing the hound minion rig/AI (copies owner stance); moss recolor of existing frames.
5. Master Builder: smoke.py render-stall hardening (fresh context per area or per N areas; on a frames stall, dump + one re-wait). Then the 6171246 control baseline in a normal test slot.
6. Nintendo 64 Style: the boot label "caching n / 110" sat at 1/110 while the bar grew, so make it count; optional "ready offline" toast after the first-realm fill (310 s at 200 kB/s). Retire hearthmoor-sw-precache-split / /tmp/hm-swsplit once live.
7. Art: add Ingrith Rev 4b to masters APPROVED.md only after Will says yes.
8. Story: Liss's befriended line should give a "next Bloomtide in N nights" hint.
9. Sound: check that Bloomtide hit/perfect/miss/win use SFX Pack 2; SFX only, music on hold.
10. Cozy, only if Will unholds it: fast-forward the attract demo (82e71bb) onto the new live head for Tue run 2.

## RESUME HERE (2026-11-02, HD-2D Cozy Builder)

Branch `hearthmoor-vhc-split` (not live; main untouched). Head: see the last commit on the branch (this HANDOFF commit sits on top of sw regen 2b17b50).
Contents, on top of hearthmoor-vanaheim-c-merge 44586bc (live main 6171246 + Bloomtide 61bc1dd + Liss wiring):
- 59baaab = cherry-pick -x of N64 04f8798 (split SW precache + loading bar via drawBootProgress). Conflicts: game.js (dropped the HELD attract-demo block, kept bootDone + startBackgroundFill; the old inline SW register is replaced by registerSW(swOn)), BALANCE.md (kept the Bloomtide art line, added only the precache GD-call line, dropped attract/palette-allowlist lines), sw.js (took N64's template, then regenerated).
- 3cddc46 = cherry-pick -x of 81b180e (smoke_sw --throttle).
- 80501ec sw regen; 99b2340 Ingrith Rev 4 (Art patch, 12 PNGs changed); 7c9283d sw regen; 873ecdd Ingrith Rev 4b (boots/belt strap #3e5a8c; as_giant.py optional boot_hi, default unchanged); 2b17b50 sw regen.
- sw.js: install shell 110 files 3.15 MB, first realm 1450 files 40.5 MB, lazy 4905 files 193.4 MB. All URLs git-tracked, no .pyc, minigames + Asgard covered.
- Art review images: /workspace/hearthmoor-staging/art/asgard-ingrith-fix/r4/before_after_r4.png and /workspace/hearthmoor-staging/art/asgard-ingrith-fix/r4b/before_after_r4b.png

GD please test (one run):
1. Full Rule 19 on this head.
2. Offline/SW install check: shell ~3.15 MB should activate fast, then the first realm fill and the throttled lazy fill (live 6171246 took ~240 s to activate). tests/smoke_sw.py --throttle is available.
3. Liss Bloomtide options (harvest + dance) in Vanaheim.
4. Render-stall question from shards 1 and 2 at 3d1aa1a (frames counter stalls with ready true / busy false): see /workspace/.hm-logs/vanaheim-c-1031/findings.md. The control run on 6171246 never completed, so there is no clean baseline yet.
Still open: Vanaheim C fixes (a) bloom_token/foresight_charm icons are staged at /workspace/hearthmoor-staging/art/vanaheim-icons/ but not wired (foresight_charm item not in code yet); (b) Vine Grasp root kind and (c) Moss Golem hound reuse: those spells aren't in game code on this branch yet (Systems).
## 2026-11-02 Master Builder: render-stall harness fix (branch mb-smoke-stall-1102b, base e1f601d = live vhc-split; was 11e2a86 on 6171246; checkday fix-list item 5)
- tests/smoke.py only (no game/engine/sw.js/build.py/areas changes; all assertions unchanged).
- `--fresh-every N` (env `HM_FRESH_EVERY`, default 1): fresh main browser context every N of segments A-C, reloaded from the run-local checkpoint just written (same path as a sharded run). D on already open their own contexts. 0 = old single context.
- Frames stall guard in `Smoke.wait` (so `frames()`, `idle()` too): on a timeout where `__hd2d.frames` did not advance, log `[STALL]` (frames, time, seg, area, /proc/loadavg, screenshot `stall_<seg>_<hhmmss>.png`) and re-wait ONCE with the same predicate/timeout. Recovered = `[STALL-WARN]` (warning, not a fail); else `[STALL-FAIL]` and the original timeout fails. Listed in smoke.json `stalls`. Off: `--no-stall-rewait` / `HM_STALL_REWAIT=0`.
- Self-test (no browser): `python3 games/hearthmoor/tests/test_stall_rewait.py`. Not run against the game (Game Director runs QA).
- Fixed smoke: `cd /workspace/hd2d-suite-smoke-stall/games/hearthmoor && python3 tests/smoke.py --jobs 4` (worktree is on mb-smoke-stall-1102b)
- One run on this branch = harness check + baseline for live e1f601d (GD, Nov 2). Old 6171246 control (optional): `git -C /workspace/hd2d-suite worktree add --detach /workspace/hm-control-6171246 6171246 && cp /workspace/hd2d-suite-smoke-stall/games/hearthmoor/tests/smoke.py /workspace/hm-control-6171246/games/hearthmoor/tests/ && cd /workspace/hm-control-6171246/games/hearthmoor && python3 tests/smoke.py --jobs 4` (or `--fresh-every 0 --no-stall-rewait` for the old harness behaviour).
