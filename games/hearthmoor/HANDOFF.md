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
### RESUME HERE (2026-10-30)
- Owner: HD-2D Cozy Builder. Live main: 4532c6e; rollback point: ca3ef0b.
- Branch `hearthmoor-harness-1030` (from origin/main 4532c6e; pushed, NOT live): #11 harness work. Realm sub-smokes are smoke segments N-U (they used to run in every shard, so shards hit the 2400 s timeout); check-scene progress-polling ready wait + WebGL fail-fast (exit 3, check_all relaunches once) + check_all --jobs CPU cap (from harness-1028); Glenheart boss-bar check waits for the frame-driven bar redraw (BOSSBAR-TRACE log); Factions selected row keeps its faction edge (player-visible bug fix). Handoff: /workspace/.hm-logs/harness-1030/rule19-handoff.md.
- NEXT: #2 Helheim, #3 Asgard, then #7, #8, #12, #10, #9, #5, #4, #6, with #13 store last. Vanaheim #1 runs with Art/Story in parallel. No housing.
- Fun pass: n/a, test/harness only (except the player-visible bug fixes).
- **Everything left to call Hearthmoor finished** (2026-10-28, from AGENTS.md, *_PROGRESS.md, STORY_SEEDS.md, staging story/art/sound):
  1. Vanaheim realm (Stage B, first playable ~Oct 31): game/vanaheim.js from staging vanaheim.md (paste-ready), Mother Nettlecrown, smoke_vanaheim.py; reuses areas vanaheim/rotwood/verdant, verdant.js, REALM_TEMPLATE. Needs a Vanaheim art pack (none in staging). L. Lead+Art+Story. GD call (Nettlecrown difficulty, vanaheim.md Q1-Q7).
  2. Helheim finish: realm is on main (5 areas, helheim.js) but HELHEIM_PROGRESS leaves smoke/QA rows todo, helheim + hh_* fail check-scene, no REALM_OF/music track, Inkling not in PETS. M. Lead+Sound+Art.
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
- 2026-10-23, checks-upgrade: check-sprite now also checks holes / limbs / 1px outline / soft alpha (current art allowlisted in tools/check-sprite/art_allowlist.txt); Hearthmoor Art usage: staging/HANDOFF-art-checks.md. Pre-publish secret scan now runs tools/checks/extra_secret_patterns.sh + gitleaks (branch checks-upgrade).
- 2026-10-24 (HD-2D Cozy Builder): TOP ITEM when Hearthmoor resumes: Bill says the menus look generic and bland. Give them a full themed restyle like Gravewake's menus (framed panels, themed pixel fonts, gloom-and-glow), then screenshots and game-qa (rule 19).
- 2026-10-29, HD-2D Cozy Builder: Fun pass (Vanaheim Stage B): new game/vanaheim_fun.js (sfx/fx/shake helpers; CSS canvas shake OFF under the reduced-motion toggle/OS setting, boss hit-flash also skipped there). Stingers from existing audio.sfx: knot burn (spell + small shake), tithe-seal (save), frost-thorn root cut (hit + shake), fizzstone scoop (sparkle, rare 'fizzstone burps' line), Nettlecrown intro (summon + shake + flash), phase 2 (rumble + shake + flash), phase 3 (summon + shake + flash), heartroot grab (bigger shake), yield (quest stinger + sparkle); yield-to-dialogue dead time 900 -> 650 ms; rare knot line ('...and dwarf-work, honestly'). No rules, BALANCE numbers, controls, saves, palette or art changed; sw.js precache + cache version updated.
- 2026-10-29, HD-2D Cozy Builder: Fun pass (art-fix): the 8 night warm lamps (fix1028: prismvault, caldera2, barrow, barrow2, clockdeep, ossuary, jt_hall, lumen_court) now 'catch' when the hero first walks within 2.6 of one at night: a 0.9 s light swell (x1.6 fading to the unchanged steady value) + 6 existing 'embers' particles; re-arms after walking >4.5 away. Engine: engine/main.js + tools/runtime/web/engine/main.js (identical). No lamp moved (jt_hall untouched), grade/colours/numbers unchanged; sw.js cache version bumped.
- 2026-10-29, HD-2D Cozy Builder: Fun pass (GD picks, branch hearthmoor-fun2 = vanaheim-fun + artfix-fun): Settings 'shake' and 'flashes' toggles (per device; motion reduced / OS setting turns both off; all shake + hit-flash + storm lightning + lamp swell gated); Nettlecrown P3 thorn ring (visual only, THORNS_CLOSE_IN in game/vanaheim_fun.js, default OFF pending Will, QA ?thorns=1 / ?vhq=thorns); Mossbrook coin-in-the-spring + Spring-Wish Penny keepsake (?vhq=coin); bonus seed at Nettlecrown's stall, 10 %/buy, 1/day (?vhq=seed); lamp flare plays the wind-shimmer chime (engine hooks.onLampFlare/allowFlash). Numbers in BALANCE.md.
