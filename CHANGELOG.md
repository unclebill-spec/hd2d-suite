# Changelog

Dates are America/New_York. Newest first. Keep this current with every change you push.

## 2026-10-21 (America/New_York): Hearthmoor Vanaheim smoke + Mossbrook terrace stair (Master Builder 8fd514c via hearthmoor-vana-merge)

- New `tests/smoke_vanaheim.py` (20/20 PASS) and a Mossbrook terrace stair (`scene_stair_terrace.glb`); the height rule is now a hard fail. Checks: preflight, smoke_vanaheim, check_all --lowres on vanaheim/rotwood/verdant PASS.

## 2026-10-21 (America/New_York): Hearthmoor Asgard extras LIVE (merge of Master Builder 99f9b16 + main 24879e7 via hearthmoor-asgx-merge)

- New sprites: as_guard + ingrith (`axfolk`), the red Aurelion phase 3 (`axp3`, 7x), a bigger 1.6x storm_centaur (`axcent`) replacing the old one; the G7 void kit. Code: `swapRole` in `game/asgard.js` re-binds the atlas across same-grid sheets.
- Merge: sw.js conflict regenerated with `build.write_pwa()`. Checks on the merged code: preflight, smoke_asgard, check_all --lowres on asgard/gs_hall/gs_temple/reliquary/reliquary2, check-sprite PASS on ax_folk/ax_centaur/ax_aurelion_p3; scale OK (Aurelion P3 200 px vs player 29 px = 6.9x; centaur 72 px = 2.5x). Screenshot `docs/screenshots/asgard_extras.png`.

## 2026-10-21 (America/New_York): Hearthmoor Asgard music track (branch `hearthmoor-asgard-music`)

- New `audio/music/music_asgard.ogg` (procedural CC0, ~80 KB mono 22.05 kHz Vorbis, 8-bar seamless loop, 29.1 s): C major golden bells, regal choir, low drone, distant soft thunder rolls. Made by `tools/hearthmoor/gen_realm_music.py` (new `asgard` entry + `thunder` voice; optional track names after out_dir regenerate only those).
- `game/audio.js`: asgard, gs_hall, gs_temple, reliquary, reliquary2 now map to `asgard` (was the Alfheim fallback); `MUSIC_TRACKS` gains `asgard`. audio/README.md, audio/LICENSES.md, RESTORE.md and sw.js precache (version bumped) updated.

## 2026-10-21 (America/New_York): Hearthmoor Asgard realm LIVE (merge of Master Builder 1e10448 + main 645be42 via hearthmoor-asgard-merge)

- Asgard: Goldspire hub, gs_hall, gs_temple, reliquary, reliquary2 merged with main (smoke_asgard, smoke_niflheim, check_all --lowres on the 5 areas, check-sprite pass on the 6 actor sheets; the gamefx atlas is not an actor sheet).
- Music: Asgard areas reuse the Alfheim track (no Asgard track yet).
- Screenshot: docs/screenshots/asgard_goldspire.png

## 2026-10-21 (America/New_York): Hearthmoor realm music LIVE (merge of `hearthmoor-music` 0a9ca64 + main aa0c99f via `hearthmoor-music-merge`)
- **Merge:** conflicts only in CHANGELOG.md (both entries kept) and `games/hearthmoor/sw.js` (regenerated with `build.write_pwa()`, precaches `audio/`). Smoke seg D default estimate raised to ~94 min (the music step visits every realm).
- **Checks on the merge:** preflight PASS, `smoke_niflheim`, music static check (37 areas all mapped in `REALM_OF`, 8 tracks `audio/music/music_<t>.ogg` present and precached). The first preflight / smoke_niflheim run (Oct 20 16:08) failed with 'Could not create a WebGL context' (SwiftShader context failure while other browser jobs were running); no code cause, rerun holding both `browser.lock` and `browser-mb.lock`. The first static check looked for `<t>.ogg` instead of `music_<t>.ogg` (check bug, not a game bug).
- **Screenshot:** `docs/screenshots/music_options.png` (Options card with the music toggle and volume slider).

## 2026-10-19 (America/New_York): Hearthmoor realm music (branch hearthmoor-music)
- `games/hearthmoor/audio/music/`: 8 procedural CC0 mono Vorbis loops (Midgard, Alfheim, Svartalfheim, Jotunheim, Muspelheim, Niflheim, battle, boss; ~525 KB) from `tools/hearthmoor/gen_realm_music.py`; ledger `audio/LICENSES.md`, area map `audio/README.md`.
- `game/audio.js`: fetch + decodeAudioData loader, music bus with 1.6 s crossfades, loop by buffer length, ambient plucks / birds / pad ducked to 30% while music plays, synth-only fallback if a file fails; battle / boss switching from `combat.enemies` (chase / attack, 4 s linger; `D.boss` and not rare = boss).
- Options card: `music: on/off` + music volume slider (saved: `hearthmoor-music-mute`, `hearthmoor-music-vol`). Smoke D step `music:`; `--quick audio|music|options` = D. sw.js precaches `audio/`.
## 2026-10-19: Niflheim-2 LIVE (merge of `realm-niflheim-2` d7cdb97 + main a70ea29 via `hearthmoor-nifl2-merge`)
- **Merge-check:** Master Builder's runs were after its last commit (6ad0f27 code, d7cdb97 docs; clean tree): `smoke_niflheim` 90/90, `smoke_muspelheim` 95/95, `smoke_jotunheim` 185/185. Its check-scenes pre-dated the commit, so they were rerun here. On the merge: preflight PASS, `smoke_niflheim` 90/90 @1d53b75 (rerun because main changed its harness), `check_all --lowres` 3/3 (frozenspire, frozenspire2, frozen_rift), `smoke.py` segment A (combat) 610/610 @7abe7a1. Segments D (phone portrait, for the new portrait `#bossbar` rule) and I (boss camera): D PASS 513/513 @7abe7a1 and I PASS 501/501 @336d5c5 (reruns holding both browser locks). No new actor sheets (only gamefx atlases and the `veyra_shadow` strip), so check-sprite had nothing to check.
- **Test infra:** the checkpoint fixtures (`tests/fixtures/smoke_cp*.json`) are gitignored, so a fresh worktree copies them from the main checkout. Segment I failed three times with 0 steps on its first Alfheim load (150 s wait timeout), at 02:22 and 13:12 ET, each time straight after a segment D run on a loaded box (the 13:12 D took 10.2 h). Segment I's Alfheim tail and standalone `smoke_alfheim` call the same `steps()`, with the same URL and ready predicate. A probe of segment I at 14:3x ET passed that load in 3 s, so no code cause was found. `Smoke.wait` now logs a `[TIMEOUT]` line on any wait timeout (the predicate, the page / game state, recent JS errors, a screenshot) and still fails the wait, so a repeat can be diagnosed.
- **Screenshot:** `docs/screenshots/niflheim_frostweave.png` (Frostweave lance and Ice Golem in the Glowpool Caverns).
- Niflheim leftovers now: Wardens that shoot from walls (optional), plus the rest of the list in AGENTS.md.

## 2026-10-19: Hearthmoor testing time-savers (branch `hearthmoor-timesavers`)
- `tests/preflight.sh` (+ `preflight_load.py`): node --check on all game / engine js (as .mjs) and one headless title load that fails on startup errors; run first by `smoke.py`, `smoke_*.py`, `check_all.py` (`--no-preflight`).
- Smoke harness: a failing re-runnable step (callable / new `T.check`) retries once immediately, `[RETRY]` logs both results, passes only if the retry passes; `retries N` in the summary; `--no-retry`. Smoke logs and json carry the commit hash (`# smoke header: commit ...`).
- Fixed waits -> `T.until(condition)` (same assertions, same values): the dialogue helpers (`talk`, `to_choice`, `read_all`), segment C, the picker / quest log / toast / glow-toad steps, Svartalfheim (Gorrak phases, vents / gusts, conquer posts) and Alfheim (beams, Sylvaine).
- `tools/heavy.sh` (2-slot nice'd heavy-job queue), `tools/secret_scan.sh`, `tools/hm_publish.sh` (detached auto-publish watcher). AGENTS.md: builder rule (smoke after the last code commit, verified by hash) and the opt-in notes.
## 2026-10-19: Niflheim-2 leftovers (branch `realm-niflheim-2` off main 581fa0f)
- F3 Glow Pool Gallery slide puzzle (`NPZ`; solving it, `fs_slide`, unseals freeze-core `fs_c1`); F8 Rime Bridge rune-step (`NBR`; crossing, `fs_bridge`, frees heart-ice `hi_3`). Game-side only, no scene rebuild.
- `veyra_shadow` redrawn lighter (dark teal / ash grey, not near-black), back in the atlases (`FX_SKIP` empty); installed on frozenspire, frozenspire2, frozen_rift.
- Veyra's HP bar: an engaged boss keeps its bar in any state; in portrait (<= 640 px) `#bossbar` sits below the HUD chips.
- The Frostweave school (Gudrun; Ice Lance, Frost Nova, Mist Veil, Frost Spirits, Ice Golem): `combat.js` kinds, tiered lessons, `?nfq=school`; draws the pack rows in Niflheim areas, stock spells elsewhere (no new atlas rows in other areas).
- `smoke_jotunheim.py` standalone main gains the same `HD2D_USER_DATA_DIR` profile hook as the other realm smokes.
- Leftover: wall-shooting Wardens (optional, not built).

## 2026-10-18: Niflheim LIVE (merge of `realm-niflheim` c7f81e7 via `hearthmoor-nifl-merge`, a fast-forward of main a9802be)
- **Merge-check:** the diff touches no engine code (no `engine/`, `combat.js`, `tools/runtime/web/engine/main.js` or other area's gamefx atlas): `game.js` (module wiring), `build.py` (the READY-gated six areas), `smoke.py` (the realm tail), `check_sprite.py` (an empty `NIFL_NEON_ALLOW`: allows nothing) and the six new areas. Master Builder's runs pre-dated the last code edit (c7f81e7: Veyra's stand, smoke waits), so they were rerun here: `smoke_niflheim` 63/63, `smoke.py` segment A 114/114, segment B (with the five realm smokes) 401/402 (the one failure is the second fix below); check-sprite PASS on nf_folk, nf_hrefna, nf_enemies, nf_elites, boss_colossus, boss_kael, boss_veyra (no neon); `check_all --lowres` 6/6 (see the fix below).
- **Fixed in the merge (iceglow, `check_all --lowres`, never loosened):** `sprites_sharp` failed (worst block 0.93 < 0.97) and `colours` too (crop / source colours 2.29): Gudrun (`frostspeaker`) stood at (1.8, -0.6) with the glow-vine bulb (3, 1) beside her staff, and at dusk / night it broke her sprite blocks; a lamp-reach cap did nothing (same 0.9278), (0.8, -1.6) put an orb-chain mesh in front of her, (1.8, -1.9) put her feet on a floor-tile seam (0.966 at night). **Gudrun now stands at (1.2, -1.0)** (spec `areas/src/iceglow.json` and the built `scene.json`): sprites_sharp 0.997, colours 1.0. `smoke_niflheim` was rerun after the move.
- **Second fix (Muspelheim smoke, found by segment B):** "rare spots are 3.5 m clear of every actor" failed once at the Lavafalls (far = 2.87 m): `lf_hound1` wanders up to 2 m off its home (8, -1.4) and drifted within 2.1 m of the rare spot (5.6, 1.6); the same live measurement had passed before only by timing luck, and it has nothing to do with Niflheim. The 3.5 m stays; the step now measures foes from their home spots (`combat.enemies[].home`) and everything else from where it stands (far = 3.84 / 3.68). Standalone `smoke_muspelheim` 95/95 after the change; segment B's other 400 steps had passed and its Niflheim tail is `smoke_niflheim` 63/63 (rerun after Gudrun's move), so B was not repeated.
- **Screenshot:** `docs/screenshots/niflheim_veyra.png` (Veyra 5x on the Crown of Ice in phase 1: three mist clones, the four portals, head and crown in frame).

## 2026-10-18: Niflheim chunk 2 (art pack installed, all six areas built; branch `realm-niflheim`)
- **Built:** Mistmere (`niflheim`, `nf_home`, `iceglow`), the Frozen Spire (`frozenspire` F1-F5, `frozenspire2` F6-F10) and the Crown of Ice (`frozen_rift`) with the Niflheim art pack (7 sheets, 39 kit pieces, 45 fx, Spire corridors from `areas/src/gen/gen_spire.py`); `tools/hearthmoor/nifl_art.py` tables fixed from the README, `NIFL_ROLES_READY` on, `NIFL_BUILT` = six areas. Runtime: Spire rooms (F1 ambush, F2 Brisa + Wardens when conquering, F3/F5/F7 freeze-cores, F4 mirror doors, F6 Sister's Glass, F7 tablets, F9 Kael once three cores are broken, F10 door to the Rift), the three bosses on their real sheets (per-phase role swap inside one sheet, no engine edit), Veyra's clones / breath / frozen portals, Hrefna's ice lance and mist veil, Hrefna joins at the Spire mouth.
- **Tests:** `check_scene --quick` PASS on all six (one at a time), `smoke_niflheim` 63/63, `smoke_muspelheim` 95/95; no engine or combat.js edit, so no full sharded smoke. Fixes were by moving actors / dimming glow (lamp caps, glow-only lake lamps, two dropped decals), never by loosening a check.
- Leftovers: see `games/hearthmoor/NIFLHEIM_PROGRESS.md`.

## 2026-10-18: Niflheim chunk 1 (scaffold only; branch `realm-niflheim`, from origin/main a9802be, art pack not ready: nothing is live)
- **Decisions (Cozy Builder):** the Muspelheim lock stays (befriending Muspelheim makes Niflheim conquer-only; Bill is being asked) behind ONE constant, `NIFL_MUSP_LOCK` in `game/niflheim.js`; no corrupted Cinderhold shrine (mirror sigil + frost wedges are enough); weather kinds `frost_mist` / `still_frost` (the shared `mist` is Mossglen's); the Spire is `frozenspire` + `frozenspire2` + `frozen_rift`; `bifrost.js` is not edited (a `Crossing.pages` wrapper in `niflheim.js` instead).
- **Added:** `NIFLHEIM_PROGRESS.md` (RESUME HERE, areas, quests, content, art needs, tests); `game/niflheim.js` (realm tables, 10 quests, NPC talk, Hrefna in COMP, three framed bosses with Veyra's 4 phases, rares, weather, gate wiring, QA presets); area specs `niflheim`, `nf_home`, `iceglow` (+ generator) that assemble in a private build; `tools/hearthmoor/nifl_art.py` (waits on READY.txt, add/overwrite only, empty neon scope, lamp dimming, re-applies Stonefrost II / III and the Caldera school); `tests/smoke_niflheim.py` (47 steps).
- **Hooks (all tagged `[NIFLHEIM]`):** game.js (import, area / name maps, `G.nifl` detach / attach / update), build.py (areas join only with READY.txt), tests/smoke.py, tools/check-sprite/check_sprite.py (empty `NIFL_NEON_ALLOW`).
- **Tests:** `smoke_niflheim.py` 47/47 standalone; `smoke_muspelheim.py` as the shared-file sanity. No engine code (main.js / combat.js) edited, so the full sharded smoke was not run.

## 2026-10-18: Muspelheim-2 LIVE: the Caldera school (Fire Wave, Magma Pool, Ember Swarm, Flame Ward, Magma Hound) (branch `hearthmoor-musp2`, from main 98d2984)
- **Spells (story 9.2; `combat.js` kinds, defs in `muspelheim.js`, game.js `EXTRA_SPELLS` so the engine's spells-atlas cycle filter lets them through):** **Fire Wave** (I, kind `firewave`): a rolling wave of fire in a 100 deg cone, 4.2 m deep, 24 damage reaching each foe as the wave rolls past it (10 m/s) plus a small burn; the art turns with your facing (`fire_wave` / `_l` / `_u` / `_d`). **Magma Pool** (I, `magma`): a 1.6 m lava patch 2 m ahead for 6 s, 5 damage every 0.5 s to foes standing in it, a lava light and a lit zone (braziers catch it), two at most. **Ember Swarm** (II, `swarm`, own 10 s cooldown): six motes circle you for 1 s, then each flies at one of the nearest six foes in 7 m (9 damage + a burn). **Flame Ward** (II, `ward`, own 16 s): 8 s ring of flames on you: -30 % fire damage taken (fire foes, fire pillars, the Warden's Walk stones; `src.fire` or the striker's `element: 'fire'`), the ember storm and Vharzul's lava edge count it as fire resist (`fireRes()`), and 10 % of every blow that lands comes back on the striker as a burn. **Magma Hound** (III, `hound`, own 40 s): the `magma_hound` role fights at your side for 20 s with a lava light and the `hound_summon` burst; it takes the place of any other summon. It answers only where the hound sheet is (the five Muspelheim areas); elsewhere it says so and costs no cooldown. Burns on foes are one shared `ignite()` pool (0.5 s ticks). The school's long cooldowns plus the shared 1 s gap follow Stonefrost's `S.own` model.
- **Torka's lessons (the Lavafalls' `forgejudge`; Decision):** the first circle (Fire Wave, Magma Pool; flag `cs_i`, `S.unlocks.caldera_school`) right after The Ember Caldera (caldera = 3, befriend), the second (Ember Swarm, Flame Ward; `cs_ii`) at Lv 5, the third (Magma Hound; `cs_iii`) at Lv 10 (`TIER` in progress.js, the same gates as Solvi's). The lessons win over the Emberfang lines as soon as the level allows; below the level he says what you are waiting for. His quest mark shows while a lesson is ready. Conquerors and contractors get no lessons. QA preset `?muq=school`.
- **Art (`musp_art.py school(area)`, `--school-all`):** appends the pack's five spell rows where an atlas does not carry them already (the Muspelheim areas have them from `mp_fx`) plus four rows derived from the pack's own pixels: `fire_wave_l` (mirrored), `fire_wave_u` / `fire_wave_d` (a quarter turn) and `ember_mote` (one small ember in the swarm's four colours), under every built area's gamefx atlas (29 areas; `hollows` / `lane` have none: Fire Wave falls back to the spells atlas' `ember_pop` there). Mark `caldera_from`, crop-and-append, idempotent. **Run it last**; `jot_art.stonefrost` now drops rows past its mark and re-applies the school itself, and a normal `musp_art.py` run re-applies Stonefrost and the school after `gamefx()`. **Fixed on the way:** the five Muspelheim areas had no Stonefrost II / III rows (the realm merged after jt4's `--stonefrost-all`), so they get them now.
- **Tests:** `smoke_muspelheim.py` 95/95 (new: atlas rows in every area, Torka's gates and lines in every variant, the cast cycle, the wave cone + facing art, pool burn + expiry, swarm orbit + six hits, ward reduction / reflect / storm resist / expiry, hound summon + replace + bite + 20 s expiry, Plaza fallbacks). Atlas sanity: 29/29 gamefx atlases (old rows byte-identical, every effect inside the image, no shared rows).
- **Merge-check (combat.js is shared engine code, so the full sharded smoke ran once):** A 114, B 458 (with the four realm smokes), C 29, FHK 39, IJLE 24 PASS (`/workspace/alf_qa/musp2/sm2/`); DGM failed once on the phone weather-cycle step (its fixed 300 ms touch waits ran 40x slow on a loaded box, 680 s for one step) and was fixed with `T.until` on the mode change, never loosened; DGM rerun alone 40/40 (`sm3/`). `check_all --lowres` 7/7 (lavafalls, muspelheim, mp_hall, caldera, caldera2, plaza, forge). No `engine/main.js` edits (the shared change is `combat.js`, which is source, not built).
- **Screenshot:** `docs/screenshots/muspelheim_caldera_spells.png` (Lavafalls: Magma Hound at your side, Flame Ward ring, Magma Pool under three hounds, Fire Wave hits).
- **Leftovers:** the Magma Hound outside Muspelheim (needs the hound sheet in other areas' actor atlases); a Flame Ward / fire-ward-charm stack rule for non-storm fire (the charm still only keeps the storm off).

## 2026-10-17: Muspelheim LIVE (merge of `realm-muspelheim` 1705bb2 via `hearthmoor-musp-merge`, a fast-forward of main 8684b7b)
- **Merge-check:** the diff touches no engine code (no `engine/`, `combat.js`, `tools/runtime/web/engine/main.js` or other area's gamefx atlas): only `game.js` (module wiring, `markLifts` for giant NPC quest tags), `svartalfheim_follow.js` (`KIT` exported), `build.py` (the READY-gated area list), `smoke.py` (the realm tail), `check_sprite.py` (`MUSP_NEON_ALLOW`, role `pet_kindle` only) and the five new areas. Master Builder's full sharded smoke (`/workspace/alf_qa/musp/sm1/`, 15:16-16:46 ET, clean tree) started after the last code commit ff5d494; the later commits are docs only, so it was accepted instead of rerunning. Rerun here: `check_all --lowres` on muspelheim, mp_hall, lavafalls, caldera, caldera2 (result below), and check-sprite PASS on mp_folk, mp_giants, mp_enemies, mp_elites, boss_vharzul, kindle (safe) and kindle_neon (with the scoped allow-list).
- **Screenshot:** `docs/screenshots/muspelheim_vharzul.png` (Vharzul 8x on the Ember Throne, the camera pulled out, head and crown in frame). `check_all --lowres` PASS 5/5 (muspelheim, mp_hall, lavafalls, caldera, caldera2).
- **Built below:**
- **Areas (five, all built, art from the Muspelheim pack via `tools/hearthmoor/musp_art.py`):** `muspelheim` (Cinderhold hub, terrace 1.2 m + stair, red arch, signed halls), `mp_hall` (the Sigil Forge / Hall of Wardens, Warden's dais), `lavafalls` (the Lavafalls, Caldera-mouth terrace, Torka's anvils, spring grotto), `caldera` (Ember Caldera C1-C4) and `caldera2` (C5-C9, the Ember Throne). `MUSP_BUILT` lists all five.
- **Runtime (`game/muspelheim.js`):** 10 quests (Armed Crossing, Cinder Walk, Mirror Sigil, A Spark for Kindle, conquer / contract paths), Kindle companion (three warmings + the Caldera-mouth ending), Warden's Walk 1.5 s cool cycle, ember-storm burn + fire resist, Orm's lizard (Smoulder), Caldera rooms (hound ambush, glass-bridge lit path, three frost wedges, heart-coals, Kilnmother), and Vharzul, an 8x framed boss in three phases (pillar telegraphs, flame elementals + lava edge, Warden's lamps that mend him until snuffed; befriend / contract binds him, conquer takes the Ember Crown).
- **Tests:** `check_scene --quick` PASS on all five areas (muspelheim c8, mp_hall c10, lavafalls c11, caldera c6, caldera2 re-run after the last muspelheim.js / game.js edits: c12). Standalone `smoke_muspelheim.py` 68/68 (sm_m15). Full sharded smoke PASS (Oct 17, `/workspace/alf_qa/musp/sm1/`): A 114/114, B 431/431 (includes the Alfheim, Svartalfheim, Jotunheim and Muspelheim realm smokes), C 29/29, DGM 40/40, FHK 39/39, IJLE 24/24.
- **Leftovers:** listed in `MUSPELHEIM_PROGRESS.md` (Caldera spell school, Emberfang ignite + prop, Emberfall, lizard mount, item icons, Vharzul cast frames, C1-C8 art scenes and the Hall interior, extra conquer cultists, contract tunnel C2-C3 skip).

## 2026-10-17: Muspelheim chunk 1 (scaffold only; branch `realm-muspelheim`, from origin/main 8684b7b, art pack not ready: nothing is live)
- **Decisions (Cozy Builder, section 13):** (1) the Niflheim lock cost of befriending Muspelheim stays as written (pending default, Bill is being asked); (2) the Ember-born skip of *The Cinder Walk* is the whole Ember-born perk (no second option); (3) Vharzul stays a boss only. Build calls: the Ember Caldera is two areas (`caldera` C1-C4, `caldera2` C5-C9), the Armed Crossing hound spawns on the Cinderhold side, Aska's greyed options are built in `TALK` (game.js has no `locked` / `lockedLabel` fields), `factions.realm()` is wrapped to pay `gate` for a conqueror / contract.
- **Added:** `MUSPELHEIM_PROGRESS.md` (RESUME HERE, areas, quests, content list, art needs, tests plan); `game/muspelheim.js` (skeleton: realm tables, red-arch wiring, 10 quests, NPC talk, Kindle in the COMP style, Vharzul 8x `framed:true`, rares, weather, items, Svala's stall, Emberfang, QA presets `?muq=`), dormant until `MUSP_BUILT` lists a built area; three area spec skeletons (`muspelheim`, `mp_hall`, `lavafalls`: 1.2 m terrace + stair, grades, stand-in kit, assemble-validated in a private dir only, no built output); `tools/hearthmoor/musp_art.py` (waits on READY.txt, add / overwrite only, scoped neon audit, LAMP_CAP); `tests/smoke_muspelheim.py`.
- **Hooks (all tagged `[MUSPELHEIM]`):** game.js (import, area / name maps, `G.musp` detach / attach / update), build.py (areas join only with READY.txt), tests/smoke.py (realm smoke in segment B), `check_sprite.py` (`MUSP_NEON_ALLOW = {}`: an empty scoped table, allows nothing), `svartalfheim_follow.js` (`KIT` exported so Kindle's kit can register).

## 2026-10-17: Jotunheim-4 LIVE: Stonefrost II / III, the real waystone and cairn models, Flurry confirmed (merge of `realm-jotunheim-4` via `hearthmoor-jt4-merge`; branch `realm-jotunheim-4`, from origin/main; `realm-jotunheim-3` stays with Cozy Builder's merge check at d4c44ec)
- **Bug fixed first:** Boulder Toss and Frost Rune (tier I) were learnable but never castable: `main.js` filters the spell cycle by the spells atlas (`cast_sets` / `effects`) and these names are in neither. `boot()` now takes `opts.extraSpells` (game.js `EXTRA_SPELLS`: boulder_toss, frost_rune, stone_skin, cold_fire, stone_golem) and lets those through, at boot and in `setSpellCycle`.
- **Stonefrost II / III art:** `jot_art.py stonefrost(area)` appends staging `gamefx/stonefrost_fx` (10 effects, 48 px cells) under every built area's gamefx atlas (24 areas; `hollows` and `lane` have no gamefx atlas, so those cast the tier I art). Mark `stonefrost_from`, crop-and-append, idempotent; `--stonefrost-all` re-applies it. **Run it last**: `build.py` `install_forge` / `install_alchemy` crop a gamefx atlas at their own marks and would drop the rows.
- **Spells (combat.js, jotunheim.js):** Boulder Toss and Frost Rune use the `_ii` / `_iii` bolt, impact, rune and burst art with x1.3 / x1.6 damage and x1.15 / x1.3 radius once Solvi has taught those circles. New kinds: `skin` (**Stone Skin**: 6 s, -40 % damage taken, -20 % speed; it re-bases `p.speed` if the blizzard's frost slow writes it meanwhile), `coldfire` (**Cold Fire**: neon-blue patch for 8 s, foes inside move at half speed, it is a glow zone so it lights dark rooms and braziers, never burns), `golem` (**Stone Golem**: 20 s, the `golem` role, replaces any other summon). They carry their own long cooldowns (`S.own`: 14 s / 12 s / 40 s) plus a shared 1 s gap, so they never lock the other spells for long.
- **Solvi's lessons (the Hall's `rimewife`; Decision):** the second circle (Stone Skin, Cold Fire; flag `sf_ii`) opens at Lv 5 and the third (Stone Golem; `sf_iii`) at Lv 10, the same gates as the skill tiers II / III (`TIER` in progress.js). They come after the first circle (`sf_i`, barrow = 3, befriend) and win over the Rimebreaker errand talk lines. Below the level she tells you what you are waiting for.
- **Real models:** `rune_waystone` replaces the rune_standing_stone stand-in in the Waystone Crypt (barrow2, at (-4, -36.4); its lamp, `pool_cold` r 3 m, `rune_pulse` and sparkles; the arrival spawn (-4, -34.2) is outside its footprint). `watch_cairn` replaces the three snow_mound stand-ins at the Toll of Stones spots in the Rime Caves, with a `cairn_toppled` twin (scene objects with `pz`, hidden): when a cairn's wardens fall the game swaps them, lifts the standing cairn's blocker (collision restored from `base_data`), drops its cold pool and lights the rubble. `stone_cairn` trail markers at (-5.6, 6.6) and (5.4, 7.2). Keep-clear footprints are kept (the berserker ambush spawns stay 1.98 m out, outside the 1.8 m radius). The `cairn_toppled` kit lamp is not in the static scene (it would glow while the cairn stands); the game adds it when the rubble shows.
- **Flurry (confirmed, no change):** all five Jotunheim areas ship `flurry.png` = `pets/flurry_neon.png` (md5 cbe0e78d, primary) and `flurry_safe.png` = `pets/flurry.png` (md5 2cbd2b74, palette-safe fallback); `check_sprite` already has the scoped `pet_flurry` allow-list; `smoke_jotunheim.py` hash-checks both.
- **Tests:** `smoke_jotunheim.py` 169/169 (new: tiered lessons and level gates, cycle, tier I / II / III bolt and rune art, Stone Skin damage / speed / re-base / end, Cold Fire slow / lit zone / expiry, Stone Golem, cairn stand / topple / walkable, waystone footprint). Two old steps follow the new models: the cairn-props step now expects `watch_cairn` + `cairn_toppled` + `stone_cairn` instead of snow_mound stand-ins, and the barrow2 crypt-height sample moved from (-4, -36), now the waystone's own footprint, to the arrival point (-4, -34.2); the threshold (>= 2.3 m) is unchanged.
- **Merge with main + full smoke:** origin/main 9b5593c (Jotunheim-3) merged in (32044fa), sw.js regenerated. Post-merge `check_scene --quick` PASS on barrow, barrow2, rimecaves, jotunheim, jt_hall. Full sharded smoke PASS (Oct 17, `/workspace/alf_qa/jot/sm6/`): A 114, B 363, C 29, DGM 39, FHK 39, IJLE 24.
- **Leftovers:** a waystone model for Stonehollow's own waystone (not asked; barrow2 only), the goat mount (needs the mounts system).
- **Merge-check (hearthmoor-jt4-merge, realm-jotunheim-4 32fa561 + main 7dc4668):** the diff touched shared engine code (`engine/main.js`, `combat.js`) and the gamefx atlas of every area, so the full sharded smoke ran once: s2 AGHIJL 477 PASS, s1 B and C PASS, then DEFKM (283/284, plus the Jotunheim tail rerun alone 185/185). `check_all --lowres` 7/7 on barrow, barrow2, rimecaves, jotunheim, jt_hall, plaza, forge; atlas sanity 50/50; `pet_flurry` neon + safe check-sprite PASS.
- **Fixed in the merge:** (1) `extraSpell` was used before its `const` in `main.js` (TDZ) and the jt4 branch had only edited the built `games/hearthmoor/engine/main.js`, which `build.py` overwrites; the fix now lives in `tools/runtime/web/engine/main.js` too. (2) Load flakes, never loosened: phone MAIN / jump buttons wait for the action with `T.until`; the realm smokes' `goto` waits up to 150 s (load average 60-90); the cold-fire thaw step waits up to 240 s of game time (frost 750 -> 117 in 60 s was progressing, just slow on a busy box).
- **Screenshot:** `docs/screenshots/jotunheim_stonefrost_iii.png` (tier III Frost Rune and Boulder Toss bursts in the Rime Caves, Stone Golem at the caster's side).

## 2026-10-17: The Cold Cauldron LIVE + Bryony's 3/day toadstools (branch `hearthmoor-cauldron-merge`, from main 9b5593c + the WIP on `hearthmoor-leftovers-wip` 8b42f34)
- **Quest** (`game/alchemy.js`, `QUESTS.cauldron`, story 7.6): after Sparks in the Street Bryony offers the intro; find Bloop in Tova's quench tank, clear the coal under Old Gurgle, cast a spell within 2.6 m to light the vent (the Still is cold, no blue glow or light zone until then), bring a red toadstool + 2 moonpetals; she teaches Moonmilk. The first Glowcap Draught finishes it (+30 gold, and the side-quest +40 Hearth Tokens through `setQuest`). Saves that already knew both recipes migrate to done.
- **Bloop:** his own 240x128 `pet_bloop` sheet (`art/cold_cauldron/`, bloop_neon.png primary, bloop.png palette-safe twin), added to the forge by `build.install_cauldron` (additive, idempotent, after `install_forge`; also runnable on a built forge without a rebuild). A runtime actor (`Alchemy.syncBloop`): in the quench tank while you look for him, on his lily pad after. `check-sprite` has a scoped `CC_NEON_ALLOW` for `pet_bloop` (#1c62d8 #2ab4ff #a6ecff); the neon twin and the safe twin both PASS.
- **Still stock:** Bryony sells 3 red toadstools per in-game day (`S.stillStock`), then "Out of caps till tomorrow."
- **Fixed in the WIP (never tested before):** `addGlow` was called with `distance:` instead of `range:` (the engine reads `range`, so Old Gurgle's and the drink glow lights fell back to defaults); smoke M's expected recipe list was read after the Ember stir (it asserts the two taught recipes, as before); Bloop had no sprite or actor at all.
- **Checks:** smoke segment M extended (offer, Bloop in the tank, find, clear coal, cast lights the vent, turn-in, brew finishes the quest, 3/day cap); full sharded smoke (BEFGJLM 391/391; ACDHIK 471/471 after the right-stick zoom step was made to wait for game frames with `T.until`); `check_all --lowres` PASS on forge and plaza.
- **Screenshot:** `docs/screenshots/cauldron_bloop_old_gurgle.png` (Old Gurgle lit blue, Bloop on his pad). Note: the staging Bloop art is the teal-green frog with blue freckles; it is not fully blue as the lead's note described.

## 2026-10-16: Jotunheim-3 LIVE: Dark Stonehollow after a conquer, the B3 Glow Pools slide puzzle (merge of `realm-jotunheim-3` via `hearthmoor-jt3-merge`)
- **Dark Stonehollow:** after a conquer (`jt_dark`) the cold fires and rune pulses go out, only the glow orbs are left, the townsfolk talk curtly and Grimsa's trader prices are +25% (`factions.js` `priceMul('jt_trader')`); `?jtq=dark` QA preset. **B3 Glow Pools slide puzzle** in `barrow` (seven frost-rune stoppers, `jot_art.py` PLACE), and the barrow golems moved to (+-2.0, -10.6) so phone portrait `sprites_sharp` passes.
- **Merge-check:** Master Builder's full sharded smoke (`/workspace/alf_qa/jot/sm5/`: A 114, B 334, C 29, DGM 39, FHK 39, IJLE 24) ran after the last commit `d4c44ec` and is accepted. Rerun here: `smoke_jotunheim.py` 156/156; `check_all --lowres` PASS on barrow and plaza, and on jotunheim after one failed try (see below).
- **jotunheim lowres note:** the first try failed `colours` (night crop of `goatwife`, crop / source colour ratio 2.53 against the 2.0 limit); an identical rerun alone passed at 1.67. The metric moves between 1.0 and 3.4 across runs of the same build (noise from lights over the crop); the limit was not changed. A second rerun hit a browser-context protocol error, a third passed.
- **Screenshot:** `docs/screenshots/jotunheim_dark_stonehollow.png`.
- **Leftovers:** Stonefrost II / III (new spell kinds + spell-atlas art), real waystone and cairn models from Hearthmoor Art, the goat mount reward (needs mounts). The Cold Cauldron quest is on `origin/hearthmoor-leftovers-wip` (8b42f34), untested.

## 2026-10-16: Jotunheim-2 LIVE: rares, Rimebreaker, weather, Ulfar companion, goats, Hrimgard framing (merge of `realm-jotunheim-2` via `hearthmoor-jt2-merge`)
- **Merge-check:** Master Builder's full sharded smoke on the branch (`/workspace/alf_qa/jot/sm4/`: A 114, B 311, C 29, DGM 39, FHK 39, IJLE 24) accepted (segment A started before the art-only Hrimgard sheet commit 67010d0, B to M ran after it; the last commit changes a test wait and docs only). Rerun here: `smoke_svartalfheim.py` 118/118, `smoke_jotunheim.py` 140/140, `check_all --lowres` PASS on jotunheim, barrow2, rimecaves, barrow, jt_hall and plaza.
- **Hrimgard:** `combat.js` honours `framed: true` (the 7x boss keeps his head in view even with AI asleep) and the sheet's white grid (seam lines, beard strands, fist rings) is fixed at the source; phase 1 / 2 / 3 shots checked: head in frame, no grid.
- **Screenshots:** `docs/screenshots/jotunheim_hrimgard_p3.png`, `docs/screenshots/jotunheim_blizzard.png`.
- **Leftovers:** Dark Stonehollow after a conquer, the B3 slide puzzle, Stonefrost II / III (spell kinds + atlas art), real waystone and cairn models from Hearthmoor Art, the goat mount reward (needs the mounts system; Clatter's `jt_goat` reward is deferred).

## 2026-10-16: Jotunheim-2: rares, the Rimebreaker, weather, Ulfar, pen goats (branch `realm-jotunheim-2`; `realm-jotunheim` is with Cozy Builder for merge checks; main still 01c86b7)
- **Rares (rimecaves):** `frostmother` (2.5x, `chill` 14, Summoner of frost-troll whelps) and `avalanche` (3x, Shielded, a quake `wave` every 4th slam) through `rares.js` `BASES` / `RARE_AREAS.rimecaves`, spots [5.2,-3.2] and [-4.6,2.6] (>= 3.5 m from every actor and each other). `?qa` suppresses rares, so `check_scene` never sees them.
- **The Rimebreaker (`jt_axe`):** Solvi offers it after the Stonefrost lesson and `barrow` 3; three heart-ice shards (`hi_1` Glow Pools, `hi_2` behind Ormgar's seat, `hi_3` crypt crystals); legendary axe (`unique: rimebreaker`); every 3rd melee hit freezes the foe for 1.5 s plus a small ice wave. Deviation: the engine has no charged attack, so the wave rides on the 3rd hit.
- **Weather:** `weather.js` exports `KINDS` and `WX_HOOK` (an area schedules its own weather). Stonehollow: 70% snow / 15% blizzard / 15% clear per 6 h block; clear nights are `aurora` (green-violet ribbon, 40 s loop). Blizzard frost slow: -1% speed per 5 s outdoors, max -30%, thawed by cold fire (Flurry / tea once they exist). Interiors stay clear.
- **Ulfar's Walk (`jt_ulfar`) and Ulfar as a companion:** Turnip on the ice, the song at the cold fire, the mitten (Flurry's bed), then the Barrow door: +80 Embassy merit, `companions.ulfar`, `S.pets.flurry`, `S.unlocks.frostbrute`. `COMP.ulfar` in `svartalfheim_companions.js`; one active companion at a time (swap at the Guild desk / inn); follower KIT in `svartalfheim_follow.js` (combat_scale 2.4, boulder-toss brawl, shield hug = -50% damage for 4 s / 20 s cooldown, aura frostResist 0.5 halves the blizzard slow, faint = sits down, back on the next area change). Deviation: the engine draws sprites at one native-pixel size, so combat_scale 2.4 shapes his reach and footprint, not the drawn size (art question 2 is still open).
- **Pen goats + Clatter:** new sheet `jt_goats` (`art/jotunheim/src/goat_gen.py`, palette-only, check-sprite PASS, installed into Stonehollow by `jot_art.py`); a pen goat and Clatter stand in the far-left column of the pen (x -11.2; a second pen goat hid behind Brynja's arm in the main or landscape-phone view, so only one fits). `jt_goat` (ripple): Brynja gives one oat-cake a day, Clatter takes three on three days, stage 2 = "ride a lap" waits for the saddle: **the goat mount stays deferred** (no `S.mounts.goat`).
- **Tests:** `smoke_jotunheim.py` 137 steps (rares, Rimebreaker, weather calendar + blizzard slow + aurora, Ulfar chain / companion / hug / faint / one-at-a-time, goats + jt_goat). `check_scene --quick` on Stonehollow 11/11 (`/workspace/alf_qa/jot/chk47.log`, pictures `/workspace/alf_qa/jot/check_jotunheim/`); no other area JSON changed since 3f3718f.
- **Leftovers:** Dark Stonehollow (`jt_dark` effects: cold fires out, curt giants, trader +25%, Berserker raid on Hearthmoor), the B3 slide puzzle, the goat mount (needs the mounts system), Stonefrost tiers II / III, Games, Veyra.

## 2026-10-16: Jotunheim part 1 LIVE: 5 new areas, 26 on main (merge of `realm-jotunheim` via `hearthmoor-jt1-merge`)
- **Realm:** Stonehollow (`jotunheim`), the Hall (`jt_hall`), the Rime Caves (`rimecaves`) and the Titan's Barrow (`barrow`, `barrow2`); Bifrost gate quest, the Jarl's choice (befriend / contract / conquer), Hrimgard (7x boss, P2 slide + ice golems, P3 relit braziers), Ormgar (3x), the Rune Bridge, the Barred Gate, the Toll of Stones, Solvi's Stonefrost I (Boulder Toss, Frost Rune), the Giant Footprints decoy (`sv_decoy`) close-out, waystone both ways.
- **Checks:** full sharded smoke (`--jobs 2`) + reruns of the two non-Jotunheim steps that flaked; `check_all --lowres` PASS on jotunheim, jt_hall, rimecaves, barrow, barrow2, ravenhold and plaza; `smoke_jotunheim.py` 94/94.
- **Flake fixes (tests only, no check loosened):** the guard (C) step in segment A waits (`T.until`) for the defend pose and its release on game frames; the Svartalfheim C4 jam / reset / even-route steps wait for the puzzle's game-frame recompute before reading `pz.qa()`. No game or puzzle code changed for these.
- **Screenshots:** `docs/screenshots/jotunheim_stonehollow.png`, `docs/screenshots/jotunheim_hrimgard_barrow.png`.
- **Leftovers:** Stonefrost II / III need new spell kinds + spell-atlas art; the real waystone and cairn models are still needed from Hearthmoor Art. Coming on `realm-jotunheim-2`: the rares (Frostmother, Avalanche), the Rimebreaker, the goat (Clatter), Jotunheim weather (blizzard / aurora) and Ulfar's companion.

## 2026-10-16: Jotunheim chunk 6: boss mechanics, Rune Bridge, waystone, cairn props (branch `realm-jotunheim`; main still 01c86b7)
- **Build fix:** `tools/runtime/web/engine/main.js` now carries main's `pzObjs` / `pz` handle lines, so `build.py` (which copies the runtime over `games/hearthmoor/engine/`) no longer drops them. No `git checkout engine/main.js` needed after a build any more.
- **Rune Bridge (B7):** 3 x 6 tiles, lit frost runes (rune_pulse fx) form one connected path; an unlit tile cracks, drops you back at the bridge head with a small hit, never off the bridge; `tb_bridge` is set on crossing and tiles stay safe after. A tablet at the bridge head hints at it. Smoke checks the path is connected by BFS.
- **Hrimgard:** P2 (< 60%): the dais freezes (you keep sliding after you stop) and two ice golems rise; P3 (< 25%): his three braziers relight one by one and each lit one mends him (+1.2% per 2 s, capped at 30%) until you snuff it (E / A spots `tbt1..3`). **Ormgar:** frenzy at 50% (x1.35 speed, x0.7 swing cooldown, +20% damage).
- **Waystone:** barrow2's waystone (B8) is attuned on arrival and travels to and from Stonehollow (`WAYS.barrow2`, spawn `from_waystone`, a rune-stone marks it); `WAY_SAY` is exported from `ravenhold.js` for the two Jotunheim waystone lines.
- **Cairns:** three `snow_mound` kit pieces at the Toll of Stones cairn spots in the Rime Caves (`CAIRNS` moved clear of the pools and pillars).
- **Tests:** `smoke_jotunheim.py` 94 steps (T.until / engine-frame waits). `check_scene --quick` 11/11 on `barrow2` and `rimecaves` (rimecaves changed too, for the cairns).
- **Leftovers for Hearthmoor Art:** Stonefrost tiers II / III (Stone Skin, Cold Fire, Stone Golem) need new spell kinds and spell-atlas art.

## 2026-10-16: Jotunheim chunk 5: the Throne Barrow (`barrow2`, B5-B9), The Barred Gate, the Toll of Stones, Stonefrost lessons (branch `realm-jotunheim`)
- **Decision:** Solvi teaches the Stonefrost school in the Hall (the Hall's `rimewife` actor, after `barrow` = 3, befriend). In the Rime Caves she only has talk lines (they point to the Hall). Tier I (Boulder Toss, Frost Rune) are real casts on existing spell kinds (projectile / trap); tiers II / III (Stone Skin, Cold Fire, Stone Golem) are recorded as a design note, not built (no matching spell kinds or spell-atlas art yet).
- **Area:** `areas/src/barrow2.json` / `areas/barrow2/`: B5 Frozen Echo (0 m), B6 Berserker Hall (1.2 m, stair), B7 Rune Bridge (2.4 m, stair), B8 Waystone Crypt (2.4 m), B9 Throne Barrow (3.6 m, stair) with Hrimgard's dais; walls 7 m, kit footprint rules kept, actors fully on or off screen. `barrow.json` gets the passage at the north end of the Avalanche Run (exit to `barrow2`, spawn `from_barrow2`); `jot_art.py` PLACE list for `barrow2` (`LAMP_CAP_AREA` entry).
- **Game (`game/jotunheim.js`):** `barrow2` wired (AREAS / names / FX / SPAWNS); `ENEMIES` + XP for `hrimgard` (7x, boss, slam + wave, ice-golem minions, phases at 60% / 25%), `ormgar` (3x) and `hjordis` (3x, trial: yields); runtime foes via `spawnEnemy` + `onKill` / `onYield`; brazier 3 (`tb_b3`), Veyra's Frozen Echo (sets `jt_veyra` when revealed), rune tablets, `tb_spring` thaw (the `onCast` thaw is now per-area); Hrimgard's death sets `tb_boss`, `tb_slept` (befriend / contract: Jarl turn-in, barrow 2 -> 3, contract also pays `jt_hire`) or `tb_crown` + `jt_dark` (conquer, barrow 3).
- **Quests:** `jt_gate` (Kolbrun at the Bifrost arch, Halvard's horn; sounding it pulls you through to Stonehollow, where a frost troll comes through (Bifrost has no Jotunheim foe sheets), +60 gate merit, 50 gold; the arch becomes a portal); `jt_take` (three watch-cairns with 2 Rime Berserkers each, Rime-Captain Hjordis, item `barrow_key`, +60 gate merit, 120 gold); `?jtq=gate|deep|deepc|lessons` QA presets.
- **Tests:** `smoke_jotunheim.py` new steps (T.until / engine-frame waits only).

## 2026-10-16: Jotunheim chunk 4: the Titan's Barrow part 1 (`barrow`, rooms B1-B4) (branch `realm-jotunheim`; main 01c86b7 merged)
- **Area:** `areas/src/barrow.json` / `areas/barrow/`: Barrow Door hall at 0 m, Hall of Shields + Glow Pools at 1.2 m (stair), the Avalanche Run ledge at 2.4 m (second stair), shield racks, glow pools, ice walls, braziers 1 and 2.
- **Game:** the Rime Caves door now opens (befriend + `jt_trusted`, contract goat-path, or `barrow_key`) and starts `barrow`; `barrowRooms()` brazier spots set `tb_b1` / `tb_b2`; frost trolls, ice golems, avalanche golems, night berserkers; `?jtq=barrow` QA preset. B5-B9 (`barrow2`), brazier 3, Ormgar and Hrimgard are not built.
- **Tests:** `smoke_jotunheim.py` 44 steps (engine-frame waits, no fixed sleeps). `check_scene --quick` 11/11 on `jotunheim`, `jt_hall`, `rimecaves` and `barrow`. Full sharded smoke passed before the main merge; rerun after it, see RESUME HERE.

## 2026-10-16: Jotunheim chunk 3: the Rime Caves (`rimecaves`) + check_scene fixes (branch `realm-jotunheim`)
- **Area:** `areas/src/rimecaves.json` / `areas/rimecaves/`: 1.2 m Barrow step with stair, cave walls, cold braziers, glow pools, the Barrow door (3 rune locks), a frozen waterfall hiding `rc_spring`; Stonehollow gets a second exit (cave path) and `from_caves`.
- **Game:** `game/jotunheim.js` `caves()`: Barrow-door and waterfall look-spots, a cast near the waterfall thaws the spring, Solvi / Skuli talk, frost foes (`frost_troll`, `ice_golem`, `avalanche_golem`, `rime_berserker`: ENEMIES / XP / SPAWNS).
- **Fixes:** Stonehollow `no_bloom` and `colours` pass (neon flame fx removed at the Welcome Ring braziers, decor lamp reach dimmed by `LAMP_CAP` in `jot_art.py`, Skuli moved to open snow); Hall guards, diners and Solvi repositioned fully on or off screen and clear of overlapping giants; Rime Caves foes placed clear of braziers / ice walls. No check or allow-list loosened.
- **Tests:** `smoke_jotunheim.py` 37 steps (6 new: caves load, height, Barrow door, spring, conquer talk, Stonehollow exit). `check_scene --quick` is 11/11 on `jotunheim`, `jt_hall` and `rimecaves`. Full sharded smoke: see RESUME HERE.

## 2026-10-16: Jotunheim chunk 2: the Hall of Hearthstones (`jt_hall`) + Hollow Heart (branch `realm-jotunheim`; main 9795278 merged)
- **Area:** `areas/src/jt_hall.json` / `areas/jt_hall/`: 1.2 m high-seat dais with a stair, cold-fire hearth pit, tables and stools, shield racks; the ice cellar is the walled pocket east of the hall (one scene; trapdoor and cellar stair move the player).
- **Game:** Jarl Thyra's choice, the fire (*The Stone Welcome* now ends at the Jarl), *The Hollow Heart* (clues `jh_heart` / `jh_rime` / `jh_trail`, Solvi's rune-light, `sv_decoy` quick route, `jt_peace`), conquer and contract variants (*Rime Wages* terms + Skuli), Kolbrun, guards. Stonehollow's Hall door is a real exit now.
- **Tests:** `smoke_jotunheim.py` 31 steps. `check_scene --quick` on both areas not yet green (see RESUME HERE). Day grade of Stonehollow darkened, pens moved south.

## 2026-10-16: Jotunheim chunk 1: Stonehollow (`jotunheim`) built (branch `realm-jotunheim`)
- **Art:** `tools/hearthmoor/jot_art.py` is the real installer (giant NPC sheet re-points the stock roles; Ulfar's own sheet; frost enemies; Flurry's neon twin as the main look with the palette-safe twin as `flurry_safe`; kit pieces; `jt_fx` gamefx rows + quest markers). The pack is copied to `games/hearthmoor/art/jotunheim/`.
- **Area:** `areas/src/jotunheim.json` / `areas/jotunheim/`: a 1.34 m Jarl plateau with a stair (spec terrace, so the collision is the proven kind), snowfield, longhouses, cold-fire braziers, rune stones, the Welcome Ring lift stones, goat pens, Grimsa's fur stall, lake decal. Deviation from the art placement: the kit `stone_ledge` / `stone_stair` are not placed (the spec stair is the real one); the south wall is 1 m so the Bifrost arch does not hide the player.
- **Game:** `game/jotunheim.js`: realm tables, the Bifrost ice arch (sealed -> portal by QA `?jtq=`, `jt_gate_open` or the alliance; Kolbrun's quest is next), Grimsa's shop, NPC talk, the Jarl's choice, *The Stone Welcome* (Welcome Ring timing beat, `?lift=auto`; +40 Realm Favor, 20 gold), Hall / cave / frost-print look-spots (the Giant Footprints entry points).
- **check-sprite:** one scoped entry, `pet_flurry` (`#1c62d8`, `#2ab4ff`, `#a6ecff`), nothing else loosened. `tests/check_palette.py` (not part of smoke) still has only the neon pets in its own list, so Flurry shows up there next to the existing Tick / Lumi lines.
- Tests: `tests/smoke_jotunheim.py` (16 steps, run from `smoke.py`).

## 2026-10-16: Jotunheim decisions (branch `realm-jotunheim`, scaffold only): the story's section 13 open questions, answered by Bill
- **1. Asgard mirror: yes.** The lock and mood calls are mirrored with the same three paths (befriend, conquer, contract for locked players).
- **2. "Vanaheim easier"** = more Realm Favor and one skipped step in Vanaheim. No discounts.
- **3. Contract path kept:** *Rime Wages* stays.
- **4. Hrimgard stays 7x**, as the story says (Cozy Builder's ruling, Oct 16; replaces the earlier 6x call).
- **5. Ulfar is 2.4x in combat** (3x in town) via the engine's `combat_scale` 2.4, with no second sheet.
- **6. One active companion at a time:** Ulfar and Dagna don't both follow; they swap at the Bifrost Gatekeepers' Guild desk or at any inn.
- **7. Halvard does not lose the horn:** only the copper key is lost, to avoid too many lost keys.
- **8. The Barrow is two areas, `barrow` and `barrow2`,** like the Clockwork Deep (area list is now 5).
- **9. The goat mount is deferred** (leftovers list); mounts are not built in the engine yet.

## 2026-10-16: Svartalfheim gear and rail puzzles (`realm-svartalfheim-3`, from main 2de49ce)
- **C2 The Drive Shaft, C4 The Assembly Line, C6 The Switchyard** are playable (`game/svartalfheim_puzzles.js`): cogs carried to pegs (meshed 0.8 m apart, drive pegs always turn, a spell thaws the frozen cog / switch within 2.6 m), C4's two drives and parity (odd route = anticlockwise = belts to the presses, even route = clockwise = belts to the exit, both = jam), C6 rails with 3 switches (switch 2 frozen) and the brake lever (3 m/s cart, 30 dmg to foes, buffer bump rolls back after 3 s). Solving sets `cd_cog1/2/3`, lifts the C2 shutter / breaks the C6 ram gate and unlocks their chests (45 g + 1 deep brass, 70 g + 2 deep brass). Reset lever per gear room; solved stays solved; QA `?cogs=solve` / `?rails=solve`.
- Art: the puzzles pack (13 kit pieces, `cog_spin_*` fx, Tobble's 20x32 sheet) installed by `svart_art.py` (add / overwrite only). Tobble's follower uses his own sheet in the realm areas. Engine: `pz` tag on scene objects + `ctx.pz(id)`.
- Moved: cd_sg2 / cd_sg6b spawns, the clockdeep2 east rune lamp and the decor cart + rails (made way for the puzzles).
- Still not built: chest objects for Tick's chestSense, Forgefire day-shift gating + soot-smudge decal, Tova's discount, a real forge-construct sprite for the Bifrost runaway, the Council rift-seal shortcut, and a full `check_all --lowres`.

## 2026-10-16: Svartalfheim part 3 LIVE: the gear and rail puzzles and Tobble's own sheet (merged Master Builder's `realm-svartalfheim-3`, dce7e3b)
- `game/svartalfheim_puzzles.js`: **C2 The Drive Shaft** (clockdeep: pegs, a frozen cog to thaw, 2 loose cogs, one chain, the shutter on the chest), **C4 The Assembly Line** (clockdeep2: two drives, the odd route runs the belts to the presses, the even route solves it, a, b and c together jam the winch) and **C6 The Switchyard** (rails, three switch levers, a brake lever and the cart). Every puzzle has a reset; solved stays solved (`S.found.cd_cogN`). New puzzle kit (13 glb), cog fx rows in the clockdeep atlases, `pz`-tagged scene objects (`engine/main.js`: `ctx.pz(id)` / `ctx.pzIds()`), and **Tobble's own sheet** in all 5 realm areas (he no longer borrows Dagna's).
- Checks: full sharded smoke (A-M) and `check_all --lowres` on the changed areas (clockdeep, clockdeep2, forge_hall, glowmines, svartalfheim) plus plaza as an engine sanity check; failing segments were rerun alone.
- Smoke fixes (waits on game-time conditions via `T.until`): the C4 belt steps, the bounce-toadstool step samples the spring while the lift is up.
- Screenshot: `docs/screenshots/svartalfheim_gear_puzzle.png` (C4 solved: the winch turns true, the belts run toward the exit).
- Still not built (Svartalfheim): chest objects for Tick's chestSense, Forgefire day-shift gating + soot-smudge decal + Tova's discount, Giant Footprints clue scenes (Jotunheim), the Council's rift-seal shortcut, a forge-construct sprite for the Bifrost runaway, the Soot Colossus's soot-fall growth / smother cloud, the Foreman's stamping charge, soot / tremor weather.

## 2026-10-16: Svartalfheim part 2 LIVE: merged Master Builder's `realm-svartalfheim-2` (12971cf, cut from main 72c930f) to main and published
- **Forgefire Week** (`svartalfheim_festival.js`: festival day, Dagna's bounty, +40 Realm Favor), **The Masterwork** (`svartalfheim_master.js`: Tansy, Tinker's Heart + `wound_up`), **The Foreman** (`svartalfheim_foreman.js`: C4 mini-boss 2.8x with his own sheet, whistle + belly, drops the clock spring so the Masterwork can be finished), **rares** (`svartalfheim_rares.js`: Amethyst Basilisk, Soot Colossus), **companion followers** (`svartalfheim_follow.js`: Dagna brawls and mends, Tobble outside the realm; Dagna's temper buff), quest-mark glyphs in the realm gamefx atlases, Tick's `goldMul` (pickup gold) and `chestSense` hooks, conquer-only hushblades.
- Checks: full sharded smoke (A-M with both realms' steps) and `check_all --lowres` on all 21 areas (21/21). Segments that stopped a shard were rerun alone (HIJ).
- Smoke: the storm rift and sky-crack waits allow 150 s (game-time timers on a busy box).
- Screenshots: `docs/screenshots/svartalfheim_foreman.png`, `svartalfheim_forgefire.png`.
- Still not built: the C2 / C4 gear puzzles and C6 rails (no peg / cog / lever / rail-switch art), chest objects for Tick's chestSense, a real Tobble sheet for the realm, Forgefire day-shift gating + soot-smudge decal + Tova's discount, Giant Footprints clue scenes (Jotunheim), the Council's rift-seal shortcut (`sg_riftAfter`), a forge-construct sprite for the Bifrost runaway, the Soot Colossus's soot-fall growth / smother cloud, the Foreman's stamping charge.

## 2026-10-15: Svartalfheim realm LIVE: merged Master Builder's `realm-svartalfheim` (08ba6bb, cut from main 3b3fb0e) to main and published
- Five new areas: Anvildeep: Copper Row (hub), the Great Forge, the Amethyst Mines, the Clockwork Deep (two areas, C0-C8, boss Gorrak Ironmaw 6x with his own aura). Gate at Bifrost: *A Word from the Council* (Bix, Council vouch, Halvard, copper key, runaway construct). The Thane's alliance choice (befriend / conquer / hire / pass) with the mirrored Alfheim lock, one active companion, Tick the clockwork owl (neon pet, stepped pulse), Dagna's recruit flag, Tansy's tinker shop, steam vents and bellows gusts in the Deep, the frozen flue and the Anvil-Heart. See `SVARTALFHEIM_PROGRESS.md`.
- Checks: full sharded smoke (A-M with the Svartalfheim and Alfheim steps) and `check_all --lowres` on all 21 areas. Segments that stopped a shard were rerun alone.
- Fixes during the merge: **plaza and lane were rebuilt** (Tick's install_pets re-run had cropped the orb-lantern fx rows from their spells atlases: duplicate rows and a truncated PNG, which crashed check-scene's effect lineup); smoke fixes: the phone pad-hide, C1 steam-vent and C7 bellows-gust steps wait for their conditions (game-time timers on slow frames), `talk()` retries every standing spot once after a settle wait.
- Not built yet (details in `SVARTALFHEIM_PROGRESS.md`): Giant Footprints clue scenes (need Jotunheim), Forgefire Week, Tansy's Masterwork quest (Tick is given after the Deep without it), the Council's rift-seal shortcut (`sg_riftAfter`), Tick's chestSense / goldMul aura hooks, in-world followers for Dagna and Tobble, soot / tremor weather, peg and cog art for the C2 / C4 / C6 puzzles (placeholders).
- Screenshots: `docs/screenshots/svartalfheim_hub.png`, `svartalfheim_forge_hall.png`, `svartalfheim_gorrak.png`.
- Next: Jotunheim and the other realms, following `docs/REALM_TEMPLATE.md`.

## 2026-10-15: Svartalfheim chunk notes (branch `realm-svartalfheim`, now merged): decisions and quests: Cozy Builder's section 15 decisions, the Thane's choice and quests
- **Decisions (final, built in):**
  1. **Mirror the rival lock.** Befriend Svartalfheim first = Alfheim is locked (Aerin's befriend option greys: "(Locked. You stand with Anvildeep.)") and she offers **"Then hire me."**: the *hired* path into the Prism Vault, hired by Sylvaine's old rivals for coin: Spire key, same vault boss, **no Realm Favor**, 90 gold instead of 150 + the Queen's Lantern + Embassy favour (`flags.alf_contract`, `alf_resolved = "contract"`). Separate small commit in `game/alfheim.js`; the other way round is the Thane's "Then hire me." (Hired Hammer).
  2. **One active companion at a time.** Recruited companions stay unlocked (`flags.companions.*`); you swap them at the Gatekeepers' Guild desk in Bifrost or at any inn. A conquer-Alfheim player may own Dagna and Tobble but brings one. (Companion system itself is still not built; Dagna's recruit flag is set at The Banked Fire.)
  3. **Art:** dwarves use picks (miners), tongs and chisels (smiths, jewelers), hammers only for the foundry crew; Tick uses the stepped `tick` pulse; Dagna ships the neon-red twin as the main look (palette-only stays as the fallback sheet); Gorrak gets his own aura (dark red-violet glow, cold-blue rune pulses) instead of the scaled red pool and the 6x boss must still pass check-scene. (Recorded; the aura and the Dagna swap are not built yet.)
  4. **Anything else in section 15:** decided in the same spirit: befriend vs conquer is the player's choice, rival realm locks mirror both ways, gloom and glow in the art. Concretely here: a locked player may still conquer; "passing through" never locks anything; the contract pays gold + Rift Marks only and never gives favour, a school, a companion or a festival.
- **Built:** the Thane's alliance choice (`game/svartalfheim_story.js`): befriend / conquer / hire (locked players only) / pass, with the story's locked and mood openers, Seer and Cinderknight extras, idle lines. Quests with the story's own text: Trial of the Anvil (a ring-pulse beat on the Great Anvil, E / A as it shrinks; `?anvil=auto`), Giant Footprints (turn-in only), The Banked Fire (3 ember seams in the mines, Dagna forges the Lesser Heart, the Thane gives the **Forge-Seal**), The Forge Claim (starts), Hired Hammer (end to end: terms give seal + heart, Kesh's badge, Gorrak rebound -> stage 2, pay 250 gold + 60 Rift Marks), The Clockwork Deep (stage 1 text). Dagna and Kesh talk by path.
- **Not built yet:** Giant Footprints' clue scenes, The Forge Claim's watch posts + Ilvar, the flue thaw / Anvil-Heart, the C2 / C4 / C6 puzzles, Bifrost's sv_gate, companions, Forgefire Week (befriend, after the Deep), Gorrak's aura, the Dagna neon twin.
- Checks: node --check, check_scene --quick on clockdeep2 (PASS), forge_hall, `tests/smoke_svartalfheim.py` (hooked into smoke.py).

## 2026-10-15: Alfheim realm LIVE: merged Master Builder's `realm-alfheim` (3f5194e, already containing batch 2) to main and published
- Four new areas: Glimmer Steps (`alfheim`), Lumen Court, Wispwood, the Prism Vault. Reached from Bifrost Crossing's Alfheim arch (the Frozen Gate quest). Quests alf_gate / alf_name / alf_dim / alf_take / prismvault, the alliance choice (Alfheim vs Svartalfheim lock), Lumi the wisp companion, the beam and mirror puzzle, five bosses ending with Lady Sylvaine (6x, three phases). See `docs/ALFHEIM.md`.
- Checks: full sharded smoke (A-M, with the Alfheim steps in seg B), `check_all --lowres` on all 16 areas.
- Fixes during the merge: smoke's Sefa step now waits for her to arrive (it flaked under two shards); the second Wispwood willwisp moved off a prism crystal that occluded its sprite crop (sprites_sharp).
- `docs/REALM_TEMPLATE.md`: the files and steps for adding the next realm, as Alfheim did it. Screenshots: `docs/screenshots/alfheim_steps.png`, `alfheim_lumi.png`, `alfheim_sylvaine.png`.
- Next: Svartalfheim (held by Bill), then Jotunheim and the other realms, each following the template.

## 2026-10-14: Batch 2 (6.6-6.8) LIVE: merged `hearthmoor-batch2-wip` to main and published
- Batch 2 = 6.6 glow-fish orb lanterns (+ kit stands), 6.7 the Forge Quarter (Tova's +1..+10 tempering, Orri's rerolls and sockets, smelt / scrap, the riot, The First Temper, cold-blue +7 / +10 sparks), 6.8 the Glowfrog Still (10 brews, potions, garden herbs, dew, spring vials). Details in the three WIP entries below.
- Checks before the merge: full sharded smoke (segments A-M, `--jobs 2`), `check_all --lowres` on all 12 areas, full-size check-scene on plaza, lane and forge.
- Smoke fix: Odo's shop now lists 7 rows (empty orb + glow-fish added).
- Still open: Nettle (jeweler / unsocket; Orri's stand-in rune-stone shop stays until then), The Cold Cauldron quest, Bloop's sprite, the 3-a-day toadstool limit and regrowing toadstool patches, the 6.4 leftovers (V3 firefly maze guidance, Tobble follower, cutscenes, Veyra's beat).

## 2026-10-14: Stage 6.8 the Glowfrog Still (batch 2 WIP, branch `hearthmoor-batch2-wip`)
- `game/alchemy.js`: Bryony Glasswort (stand-in `lamplighter` sprite; the pack has no alchemist sheet) and Old Gurgle on the forge's lower yard. All 10 brews and recipes from forge_alchemy.md 7.2-7.3 (cheap brews x2), discovery lines, fizzle = nothing used + a hint, the Warm Bread Broth Gnome secret. Brew menu = dialogue choices (add up to 3, stir, take out); recipe book re-brews known ones.
- Potions are bag items `brew_<id>`: tap to drink (U stays tonic-only). One timed brew at a time (`S.brew`), folded into `progress.mods()` by `brewMods`, motes while active. Heals use `C.heal`.
- Ingredients: garden blooms now also give a herb (cold-fire petal / violet glowbell / red glow-cap); Bloop's lily pad (barrel by the Still) 1 glow-dew a day; fill a vial at any hidden spring; `SHOPS.still` sells glow-dew 5 g, vials 2 g, red toadstools 4 g.
- Art: alchemy kit (cauldron_blue, alchemy table, potion shelf, herb rack via `tools/kit/kit_alchemy.py`) + `cauldron_brew_blue` / fire / pool / brew_puff gamefx appended to the forge atlas.
- Not built: The Cold Cauldron quest (Bryony teaches Glowcap + Moonmilk on first talk), Bloop's sprite, the 3-a-day red toadstool limit, regrowing toadstool pickups, Nettle (jeweler / unsocket). Smoke segment **M** (`--quick still`). Screenshot `stage6_alchemy.png`.

## 2026-10-14: Stage 6.7 leftovers (batch 2 WIP, branch `hearthmoor-batch2-wip`)
- **Sparks in the Street** (riot, forge_alchemy.md 5): three rioters spawn at the forge gate after the Cold Altar; answer each with the right temple clue (wrong = reopen, seer shortcut, cinderknight line); Orri's tongs story ends it (+60 Hearth, first socket free). Tova and Orri wait until it's done.
- **The First Temper** (6): Tova's offer, scrap at the forge, 3 bellows pumps by the left forge, a free +1, Orri's turn-in (6 iron bits + 1 rune-stone).
- Tova's menu: Temper / Smelt (4 iron + frost core -> 2 cold-steel) / Scrap (scrap gold + iron bits by rarity 1/2/3/4/6) / Buy (iron bits now 6 g). Orri: random reroll (1 stone), **pick-your-stat** (2 stones), **socket punching** (cap 0/1/2/3/3, costs from 4.1; Commons refused); `iconCanvas` draws 3 sockets top / middle / bottom.
- **Cold-blue sparks:** +7..+9 icons get a cold-blue glint, +10 a glint + mote; +7 weapons throw 2 cold-blue glints per swing, +10 throw 5 and shed a slow mote at rest.
- Not done: Nettle (unsocket, jeweler), the Still (6.8). Smoke segment L extended.

## 2026-10-14: Stage 6.7 the Forge Quarter + 6.6 lantern stands (batch 2 WIP, branch `hearthmoor-batch2-wip`)
- New area `forge` (Ravenhold's east district gate opens once *The Cold Altar* is done; `REALM.forge = 'hearth'`). A dark yard with two red forge mouths, three neon-blue quench tanks, embers, red / blue light pools + point lights (always glowing).
- `game/forge.js`: Tova Anvilsong tempers gear +1..+10 (forge_alchemy.md 2.1-2.4: rarity caps, cost table, +7% per + on own mods in `gearMods` / `describe`, fails from +6 keep gold + gems, eat iron / steel, add heat; sure at heat 3). Orri Flintcog rerolls one stat with a rune-stone (3.1: per-item limit, keep new / old). Shops `forge` (iron bits 4 g, cold-steel 30 g) and `runebench` (rune-stones 40 g; stand-in until Nettle). New `describe` labels (crit damage, drain, regen, healing, spell cd, stamina regen).
- Not built yet: the riot beat, *The First Temper*, sockets (Orri / Nettle), smelt / scrap-for-iron tabs, Tova's shop-style forge panel (dialogue choices for now), the Still (6.8).
- Art: forge pack (`art/forge/`: Tova = `smith`, Orri = `dwarfsmith` sheet, `forge_fx` gamefx via `build.py install_forge`, kit via `tools/kit/kit_forge.py`). Orb lantern stands: `tools/kit/kit_orb_lanterns.py` + lampless `orb_post_*` copies (the light comes only from a placed fish), placed at the 4 lantern spots.
- Smoke segment **L** (`--quick forge`); segment K checks the stands. Screenshots: `stage6_forge.png`, `stage6_lanterns.png` (refreshed).

## 2026-10-14: Stage 6.6 glow-fish orb lanterns (batch 2 WIP, branch `hearthmoor-batch2-wip`)
- `game/lanterns.js`: buy glow-fish (Odo, Ida) and empty orbs (Odo), or catch glow-fish at night (Hollows spring, Ravenhold pier ends; one per spot per day). Place orb lanterns on 2 home spots (Plaza cottage) and 2 Lane garden spots (blue / violet / red / grand mix); at night each casts a pool decal + point light + light zone. E again takes it back.
- Art: `art/orb_lanterns/orb_fx_32` (Art seat pack) appended to plaza + lane spells atlases by `build.py install_orb_lanterns`. Kit posts (glb) not placed yet: orbs hover. Smoke segment **K** (`--quick lantern`). Screenshot: `docs/screenshots/stage6_lanterns.png`.

## 2026-10-14: Batch 1 (6.2-6.5) LIVE: merged `hearthmoor-batch1-wip` to main and published
- Green before merge: check_all --lowres 11/11 areas, smoke --quick controller 114/114, smoke --quick vanaheim 29/29, smoke C 29/29 (full smoke 103/105 earlier; both fails fixed in d025afd/b42a14c).

## 2026-10-14: Stage 6.4 Vanaheim's dungeons
Story: the Story bot's `verdant_heart.md`. Art: the Art bot's Verdant Heart pack (`games/hearthmoor/art/verdant_heart/`, installed by `build.py install_verdant_heart`; kit `tools/kit/kit_verdant_heart.py`). New module `game/verdant.js`.
- **The Violet Spring** (befriend): Burrowmoss starts it; light Mossbrook's 2 braziers, pick 3 red caps under the giant toadstools, E at the spring (`vanaheim_spring = cleansed`); his word pays +60 Realm Favor, starts The Rotwood Hollow and opens the root-cave under the Old Bough (conquer: E at the roots burns through).
- **The Rotwood Hollow** (`rotwood`, R0-R7, generated by `areas/src/gen/gen_vh_dungeons.py`): glowing stream, waterfall, vines, violet fog, glow frogs, red toadstools; rot treants / spore elementals / a moss golem; the rune-sealed root door (3 braziers in pulse order, a wrong order snuffs them; a soft wall because the collision is baked), the Larder cages + the "a shadow" riddle door, the Weeping Root, and **the Blight Regent** (5.5x): phase 2 rot-fog Blight outside lit rim braziers, phase 3 the frost-iron spike pulses blue (hits in the window: x2 + 3 s stagger). His fall drops the spike and opens the sapling stair.
- **The Verdant Heart** (`verdant`, V0-V5): Bloom Stair root bowls, the Moonwell's **Thornmother** (2.4x), **Hjortur** (6x): the guardian trial on befriend (he yields: +80 +120 Realm Favor, Greenheart tine), the corrupted fight on conquer.
- Fixes: smoke F's Rift-sense step forces storms off (with peace off, the 6.5 storm toast covered the fox's warning); `rifts.setTimer` keeps a warned rift's spot when fast-forwarding. New smoke segment **J** (`--quick verdant`).
- **Correction (smoke G, Novice Edda):** the earlier "NPC beats the sealed-gate look" change did NOT fix G and is reverted. Real cause (found by logging the nearest-NPC pick per E press at (-7.6,-9.5)): the runtime's `actors.add` dropped `spec.talkable`, so an NPC added at runtime with no `say` lines (Edda) was never a talk target (`nearestNpc` -> null). Fixed in `tools/runtime/web/engine/sprites.js` (the actor keeps `talkable`).
- Check-scene fixes for `rotwood` / `verdant`: a raised root ledge (h 1.2) along the back of every cavern with a root stair per room (real height), a warmer moss-lit day grade + an explicit dusk grade (night stays gloom-and-glow), fireflies / mist / frogs moved onto the ledge and stream so they no longer blur the sprites, `spore_motes` left out of the atlas (too sparse to verify; nothing places it).
- Smoke G, past Edda (root causes logged per call: trigger rect, nav reachability, player path): Ravenhold's Old Temple stair exit's front edge was at z -10.7 but the stair foot's last walkable row is ~-10.5 (now -10.2); the cold altar at z -6.6 plus the nav radius sealed the court stair foot, so the inner court (Rift-gate, Midgard portal) was unreachable on foot (altar moved to z -5.9, use spot -4.9); the rift-fight teleport landed in the court stair's side-wall cell (now picks a free cell); the Bifrost arrival check read the position after walking to Halvard; a duplicate `name=` step kwarg.
- R1 glow-moss path over the rot-mire (off the patches you're Mired: stamina drains, no regen), R2 bounce toadstools (3 hops + a hidden cap up to the ledge spring), R4 thorn wall (a soft wall until the gallery brazier `rw_thorn` is lit).
- Not done yet: V3 firefly maze guidance, Tobble as a follower, the cutscene dialogue (6.3-6.8 of the doc), Veyra's beat. (Still open after the batch 1 release.)

## 2026-10-06: Paused by Bill (resumed 2026-10-14; batch 1 is now live, see above)
- Work on Hearthmoor is paused until Bill restarts it. The live game is still Bifrost Crossing (main 56f9b2f).
- The batch 1 work in progress (6.2 pets + Stray Den, 6.3 Old Temple, 6.4 groundwork, 6.5 rift storms, sharded tests) is on branch `hearthmoor-batch1-wip`. It is NOT green yet and NOT merged to main.
- Open test failures: smoke segment G "could not talk to novice" (Edda in Ravenhold at -7,-10.2; the fix is in this commit but not re-run) and the segment F pet-follow step (it samples the gait too late; a gaitSeen fix is in this commit but not re-run).
- Next, when resumed: re-run `smoke.py --segments FGHI --jobs 2` plus the temple check-scene, then build 6.4 Verdant Heart (story and art are in /workspace/hearthmoor-staging), then the full smoke + check_all, then merge to main and publish. After that: batch 2 (6.6 orb lanterns, 6.7 forge, 6.8 alchemy), merging Master Builder's paused `realm-alfheim` branch, then Svartalfheim (script ready).

## 2026-10-05: Hearthmoor Stage 6.2 (the Stray Den + glowing pets), 6.3 (the Old Temple), 6.4 groundwork, 6.5 (rift storms), faster tests (local; batch not pushed yet)
Story: the Hearthmoor Story bot's `pets.md`, `old_temple.md`, `verdant_heart.md` and `rift_storms.md` (staging), with Bill's decisions. Art: **the Hearthmoor Art bot** drew the pet sheets (wisp-kit, glowmoth, lantern fox and the moss-pup: `art/pets/pets.png` + `pets_fx` + `pets_particles`) and the **Old Temple pack** (`art/old_temple/`: riftgate arch + dormant glow, temple braziers, faceless statues, stained windows, broken columns, Mother Ilse `templekeeper` and Brother Tamsin `archivist`, and the riftgate / cold-fire gamefx). Screenshots: `docs/screenshots/stage6_pet_pick.png`, `stage6_pet_glow.png`, `stage6_pet_mosspup.png`.
- **The Stray Den (6.2):** a round stone house in Bifrost Crossing's west yard, with three cold-fire lantern posts, a woodpile and Signe Larkspur (new `denkeeper` sprite). The side quest **Strays of the Rift** has stages 1-2 driven by flags; 3 = done.
  - Light the 3 lanterns with any spell, seal the little scripted rift behind the woodpile (tier I, tagged `den`: no rare, never closes by itself), bring a glow seed or moonpetal, then come back after dusk and pick a pet. The 40 Hearth Tokens come from the automatic errand payout. Side quests never count toward "quests n/3", the toast says "Side quest done", and the log hides them until they start and labels them "Side:".
  - **Pets** (`game/pets.js`): the wisp-kit, the glowmoth and the lantern fox can be adopted; the **moss-pup** is a gift (`S.pets.mosspup.atDen`, from the Vanaheim befriend path). Each pet has its own sheet with a `follow` gait (it hurries when more than 3 m behind). It carries its own light, pool, aura and motes in the dark and in the Rift's gloom (and in the Old Temple until the relight); the moss-pup's light is lime `#5aec3c`.
  - Pet auras (bond 3 is stronger):
    - wisp-kit **Cold-fire Focus**: spell cooldowns 6% shorter;
    - glowmoth **Lamplight Dust**: secrets shimmer within 6 m, healing +10%;
    - lantern fox **Rift-sense**: rifts are sensed 10 s early with a direction ("{name}'s tail flares red"), +10% Rift Marks, faster stamina;
    - moss-pup **Forager's Nose**: springs shimmer within 5 m, spring-fizz +15 s, a 25% chance of +1 when foraging.
  - The Den hub lets you feed (Den biscuits, 6 gold), swap pets, adopt more (Hearth rank 1 + 40 gold) and name them. The Gear tab has a pet strip (P / LT feeds). Pets and the Den save in `S.pet` / `S.pets`.
  - **Neon exception:** Bill approved neon pets (2026-10-05). `check-sprite` has a scoped `NEON_PETS_ALLOW` for the `pet_*` roles only, and `docs/HD2D_COZY_STYLE_LOCK.md` records the override. The spells NEON palette gained lime.
- **The Old Temple (6.3):** a new `temple` area up the stair behind Ravenhold Harbor's district gate. `REALM.temple = 'hearth'`. It has a nave terrace (1.2 m) and an inner court (2 m) with the Rift-gate. **Art: the Art bot's Old Temple pack** (`art/old_temple/`). The kit builds through `tools/kit/kit_old_temple.py` (imported by kit.py). `build.py install_old_temple` adds the Ilse / Tamsin sheet (own `old_temple` sheet, like the pets) and appends 8 of its 9 gamefx to the temple's gamefx atlas.
  - The dormant Rift-gate is `riftgate_arch` + `riftgate_glow_dormant` with the `riftgate_seal_dormant` heartbeat. Raising the charm plays `riftgate_awaken`, then `riftgate_vortex_lit` plus the `riftgate_ring_lit` rune ring on the plinth.
  - The 3 stair braziers and the cold altar are `temple_brazier_out`; relit, they burn the pack's `temple_coldfire` with a `coldfire_pool_wide` pool. The stained windows throw `glasslight_violet` / `glasslight_gold` pools from dusk. The statues' `faceless_gaze` isn't installed yet: its frames are under check-scene's 20-px measurable minimum (it belongs to the later *Faceless Statues* beat; temple.js spawns it once the atlas has it).
  - Still placeholder: the lit glow mesh (`riftgate_glow_lit` would need a runtime kit swap; the lit look is the vortex, ring and light for now), Veyra's fx and Edda's role. Bifrost's Midgard arch keeps the portal kit's `rift_vortex`.
  - **The Cold Altar** (story): Warden Hilde hands over the Order's relief basket and a Hearth writ. Novice Edda lets you through the Harbor gate, which turns into an exit. Mother Ilse takes the basket (+40 Hearth, and the Temple waystone attunes). Find 3 clues with Brother Tamsin, then the clues clear the Forge Quarter (+60 Hearth, +30 gold). The Forge riot stays offscreen.
  - **Keeper of the Gate** (story): Grandpa Alder gives Warden Aldis's lantern charm and Ida Wickmere lights it. Light the 3 stair braziers, which won't catch without the charm (the first one stirs 2 wraiths). Ilse's rite has an option to sleep on a cot until dusk. Then set the charm on the cold altar and raise it at the Rift-gate, which tears open a scripted major rift.
  - Sealing that rift brings **Veyra's cameo**, which can be switched off (`TEMPLE.veyra` / `?noveyra`). Ilse then pays +120 Hearth, +60 gold and a frost core.
  - **The relight alone opens Midgard's arch** at Bifrost (option A). The lit Rift-gate is a portal to the Crossing and back, and Halvard pays +40 Rift Marks for the gate repaired.
  - Bifrost's sealed Midgard gate now points at the quest.
  - Fix: the cot-until-dusk choice used a context call that doesn't exist (`ctx.setTime`); it now sets the clock.
- **Rift storms (6.5, `game/storms.js`):** night-only storms seeded by the day (`stormAt(day)`). The Bifrost storm covers the Crossing and the Rift Shrine, about 1 night in 4 once you've seen the Crossing, never two nights running and never on day 0. Mossglen, the Hollows and Vanaheim get the rarer world event, about 1 in 10 of the remaining nights.
  - In the storm region: rifts come fast (first 10-20 s, then every 40-70 s), tiers weigh `[35, 45, 20]`, and **Rift Marks +25%**.
  - New **storm-only rift spots** at the Crossing (clear of the arches, the Den yard, the skiff, the waystone and the kiosk) and at the Shrine's dais edge.
  - The sky: `rift_tear_minor` cracks high up, cold-fire motes, glow mist and short violet / red point-light flashes, with a soft rumble. No bloom and no screen flash.
  - Storm banner and dawn toasts; NPC storm and morning-after lines (Halvard's keys and Ondra's "cold side" foreshadow lines are kept); pet barks; morning toast scenes (Sable's +15 Black Doubloons is kept).
  - **Storm Watch** is a repeatable Guild bounty with the new `bounty` tag: no Hearth payout, never an errand, full XP the first time and half on repeats.
  - **Sable's skiff keeps sailing** in a storm, with a warning line. The Ravenhold dock kid is now **Nell** (display name only; the save id `dockkid` is unchanged).
  - QA: `?storm=bifrost|mossglen|hollows|vanaheim|off`. Smoke, `?peace` and `?qa` runs have no scheduled storms.
- **6.4 groundwork (Vanaheim's dungeons are not built yet):**
  - The Mossglen mini-boss is renamed **Glenheart, the Elder Golem** (display name only; the id `eldergolem` is unchanged), because "Mossheart" is now Vanaheim's legendary staff.
  - **Trial mode** in combat: a foe with `trial` (true, or `(S) => bool`, or a spawn's `sp.trial`) **yields** at 0 HP instead of dying. There's no XP, no loot, no boss merit and no respawn timer; `S.trials[id]` counts it and `e.onYield` fires. This is for Hjortur's guardian trial.
  - **5-6x boss camera:** the engine's `framePull` clamp goes from 1.6 to 2.0, and combat pulls about 1.8-1.9 for 5.5-6x foes. 2.5x Glenheart is unchanged.
  - A **Vanaheim conqueror** earns Rift Marks instead of Realm Favor in Vanaheim areas (`factions.realm()`).
  - **Sable buys the Regent's heartwood:** +60 Black Doubloons and -5 Hearth (new item `heartwood`, palette icon).
  - New `MERIT` keys `vh_spring` / `rotwood` / `trial` / `verdant` / `heartwood`, and `REALM.rotwood` / `verdant` = `embassy`.
  - Still to build: the Rotwood Hollow and Verdant Heart areas, the Violet Spring / Rotwood / Verdant quests, Tobble, the new foes and rares, and the Blight Regent and Hjortur (boss sheets, phases, puzzles).
- **Neon green and pink for effects and orbs (2026-10-06):** the art packs add neon green `#3cf08a` and pink `#ff4fc8` (each with a _hi / _lo shade) for glow orbs, fireflies and bioluminescence. Bill allowed them **for effects and orbs only**.
  - They're in the spells / portal NEON tables (`neon_jade*`, `neon_pink*`), and check-sprite allows them on `orb_*` / `glow_orb*` roles only.
  - New `tests/check_palette.py` checks every area's spells / particles / gamefx atlases (biome + NEON + orb neon) and every sprite row (biome only, plus the scoped pet allowance). 314 atlases and rows pass.
- **Pet follow catch-up:** a follower more than 3 m behind now speeds up with the gap (1.5x at 3 m up to 2.6x), and hops to the hero's heel past 7 m or after 1.2 s stuck on a blocker. The lantern fox's hurry walk was falling short of the smoke's catch-up step under load; the test is unchanged.
- **Dialogue portraits for roles on their own sheet:** `drawPortrait` crops a role's own sheet (pets, Ilse and Tamsin, bosses) instead of column 0 of the area's main atlas, which showed the wrong face.
- **Old Temple check-scene fixes:** the two refugees moved off the market stall and out of the firefly patch (their sprites were occluded, failing sprites_sharp), and the night exposure is 1.0 (the new windows and gate lights pushed night luma just past 65% of day).
- **Faster tests (Task A):**
  - `tests/smoke.py` is cut into segments A-I at real save points (A-E the old playthrough; F pets, G Old Temple, H rift storms, I 6.4 groundwork) (checkpoints `tests/fixtures/smoke_cp{1,2,3}.json`). New flags: `--jobs N` (N parallel browser workers, longest segments first, results merged into one `smoke.json`), `--shard i/N`, `--quick <area>` (that area's segments only, for per-change checks), `--segments` and `--list`.
  - New `tests/check_all.py` runs every area's check-scene, serially or with `--jobs N`.
  - The serial default is unchanged. The same steps and thresholds run exactly once across the shards.

## 2026-10-04: Hearthmoor Stage 6, part 1: Bifrost Crossing (the portal capital)
World flow per `docs/story/STORY_SEEDS.md` and the builder handoff: Hearthmoor → Ravenhold → **Bifrost Crossing** → one city per realm. Screenshots: `docs/screenshots/stage6_bifrost_night.png` (the Crossing at night) and `docs/screenshots/stage6_bifrost_arches.png` (the realm gates).
- **New area `bifrost`:** a floating, chamfered flagstone plaza in the Rift's gloom. A seven-band rainbow inlay runs up its middle from the **rainbow bridge** (bands of glowing light with light dripping off the underside into the void) out to a small skiff landing. Underneath hang a tapering rock root, roots and cold-fire crystals. Rift shards float in the void around it.
- **Route (my pick, fits the existing map):** the Market Terraces gate **stays sealed**. Brannoc now sends you the other way, by **Sable's rift-skiff** from Ravenhold's east pier (the Corsairs sail the Rift's under-currents). E / A at the skiff, or tap / click it to walk up and again to open, gives a "Sail to Bifrost Crossing" choice. Before Brannoc's word it is "Corsair business". The skiff at Bifrost's landing sails back. Story note: in the full design the Old Temple's Rift-gate opens to Bifrost at the end of Act 1. Midgard's own gate at the Crossing is sealed and says exactly that, so the skiff is the slice's early way up.
- **Nine realm gates**, drawn fresh (style only from Bill's rift refs: stone arches with coloured glowing swirls and jagged neon rims, nothing traced). Each is a tall gloom-stone gate with stepped pillars, a voussoir ring and a jagged five-spike crown, plus a glow piece in its realm's colour: a jagged rune rim lining the opening, a faceted keystone crystal, crystal tips on the crown, pillar rune ticks and an invented realm sigil on the plinth.
  - Five gates stand on a 1.2 m gate terrace (stair in the middle): Asgard gold, Alfheim violet, **Vanaheim open**, Jotunheim ice-white, Helheim spirit-rose. Four stand on the plaza: Muspelheim red, Svartalfheim copper, Niflheim neon blue, Midgard rainbow.
  - Vanaheim's gate is the open green-gold swirl with a cold-fire rim (`rift_vortex`). It leads to Mossbrook Springs (spawn `from_bifrost`). Vanaheim's vine gate now asks "the Rift Shrine, or Bifrost Crossing?" once you have seen the Crossing.
  - The other eight have sealed swirls. New `hd2d portal` seals `rift_seal_gold / _ice / _amber / _rose / _rainbow` (biome-palette lights; Midgard's rim turns through the bridge's seven bands) join violet / blue / red.
  - Looking at a sealed gate (E / A, or tap to walk up and tap again) says why it is shut, the key it needs and where you stand ("You: Stranger, 0 Gilded Acorns"). Asgard needs the Realm Embassies at Honored (allies only), Alfheim a Guild Keybearer (frozen by Veyra), Jotunheim Embassies Friend, Helheim Embassies Trusted, Muspelheim Guild Trusted (Gate Runner), Svartalfheim Gnome Council Trusted, Midgard Hearth Trusted (the Old Temple's gate is dark). Niflheim is frozen from the inside, so no key yet. With the standing it says the key is "coming soon".
- **Gatewright Halvard Ness** (new named sprite `gatewright`, clothing rule: a sky-blue guild coat to the hip with a cream collar, a dark belt, charcoal trousers, tan boots, a rune-key staff with a cold-fire crystal) at the **Gatekeepers' Guild kiosk** (stone counter, open ledger, key rack, a guild-blue banner with a gold key, a cold-fire lamp). Meeting him pays +20 Rift Marks. His choice explains how Rift Marks are earned and why the gates are sealed, and which way is home.
- **"The Road to the Rift" now ends at the Crossing:** Brannoc (after the Market gate) pays +30 gold and +40 Corsair merit and points you to the skiff (`S.flags.rh_road`; the log shows "Take Sable's rift-skiff … report to the Gatekeepers' Guild"). Halvard (turn-in tag) finishes it: +60 Rift Marks, +50 gold, a rift shard (socket gem), story XP (`S.flags.bf_done`). Quest steps can now be functions of the save. Saves that finished the old version keep their text and can take the skiff.
- **Waystone** by the plaza (Guild stone). Bifrost is attuned on your first visit and then shows on the Lane / Ravenhold waystones.
- **Glow:** neon-blue cold-fire braziers (jagged cone flames) at the gate stair and the bridge head, a violet and a red brazier, and cold-fire / violet / red light pools (decals + motes). Each gate's light is a lamp, and the strongest near the camera get the pooled point lights, so the glow-light cap holds (3, or 2 on phones). The Crossing glows at every hour (`ALWAYS.bifrost`), with no bloom.
  - Red white-spotted toadstool clusters (two with a giant cap) sit at the plaza and terrace corners and on the landing. They glow at night (`TOADS.bifrost`).
  - Gloom grades: violet day, blue dusk, deep night.
- All inputs: keys, controller, mouse and touch for the skiff, the gates, the waystone and Halvard. `REALM.bifrost = 'gate'` (Guild merit for anything felled there).
- **Smoke:**
  - The Brannoc step now expects the skiff hand-off, not the old ending. The quest-to-Bifrost flow is new behaviour, so this is not a weakened check.
  - New steps: the skiff by keys; the Crossing's contents; Halvard by controller; a sealed gate by keys; Vanaheim's gate by mouse; the vine gate's new choice; the Crossing's waystone by controller; the Lane's waystone listing Bifrost; a sealed gate by touch on the phone.
  - The phone's Ravenhold waystone step taps the last row ("Stay here.") because Bifrost is now attuned.
- **Phone tap fix (2026-10-05):** Bifrost camera look bounds were ±4.5, so Midgard / Muspelheim at |x|≈11 stayed off-camera on a phone portrait even when you walked up to them (Ravenhold uses ±12 for the same reason). Bounds are now ±11. The smoke Midgard-tap step walks into camera range from the waystone spawn first (phone HFOV cannot see x=11 from the spawn), then taps. The area spec `areas/src/bifrost.json` now carries the same ±11 bounds, so a full `build.py` keeps them.
- **Build note:** `build.py --skip-assemble` copies areas from `/tmp/hearthmoor_build`, which a box reset wipes. For this release only `sw.js` and the zip were regenerated (`build.write_pwa()` + `build.make_zip()`), so the tested area files ship unchanged.
- **Checks:** check-scene 8/8 (plaza, lane, mossglen, hollows, rift, vanaheim, ravenhold, bifrost), each first try; smoke PASS 215/215 (1172 s), 2026-10-05.

## 2026-10-04: Hearthmoor clothing-rule pass (older cast)
Follow-up to Stage 5 part 4. The older sprites flagged against the style lock's clothing rule now wear clothes, not onesies, padded suits or armour: the top and bottom are clearly different colours / values, a darker waist band sits between them, trousers show the leg split, and the shoes contrast with the trousers. Palettes, silhouettes and glows are kept. Before/after: `docs/screenshots/clothing_pass_before_after.png`; in game: `docs/screenshots/clothing_pass_ingame.png` (Plaza by day, a staged QA line-up: extra NPCs added with `ctx.addNpc`, the player as the Seer).
- **Seer:** the long grey cloak is now a short pale-grey tunic-robe to mid-thigh (rune-stitched hem, the back rune), cinched with a rune-blue sash, over dark trousers and tan shoes. The grey hood, pouch and staff are unchanged.
- **Cinderknight:** no plate body. An ember-red jerkin over a pale shirt collar, ember lacing, one small plate pauldron (left shoulder) and the bracers, a dark belt with the glowing ember buckle, charcoal trousers, brown boots. The flame hair, ash marks and ember greatsword stay.
- **Runeguard:** a tan leather tabard that ends at the hip (gold rune on the chest), grey mail sleeves and sides showing, a dark belt, brown trousers, dark boots. The light-rune shield and axe stay.
- **Gardener:** cream shirt with moss suspender straps, a dark belt with a gold buckle, moss-green trousers, brown boots (no bib overalls).
- **Sefa (night merchant):** the open night-blue cloak frames a sky-blue tunic with a deep-blue sash; brown trousers, dark boots. Her neon-blue lantern and scarf are unchanged.
- **Hedge-witch:** a sky-blue bodice, dark belt with a gold buckle, deep-blue skirt under the night-blue cloak.
- **Grovekeeper:** a cream blouse under the moss shawl and leaf mantle, dark belt, grass-green skirt.
- **Gnome:** a broad two-row dark belt with a tall gold buckle over the blue smock, tan trousers, dark brown shoes.
- **Sable (corsair):** the sash's lower row is now darker (every sash does this), so her waist band reads.
- **Sprite tool:** `tunic` (rows of the top hanging below the waist band, with a front slit), `collar`, `suspenders`, `belt_w` (2 = broad belt), `tabard` (ends at the belt), `cloak_short`, and `belt` on skirt roles (cinches the skirt top). Sash = a light row over a darker row. Roles that don't use these render exactly as before. All seven area atlases regenerated; only the nine roles above changed.
- **Smoke fix (test only):** the controller step at Bakery Lane's waystone kept pressing A while the area was already loading; a press during the load can't be polled, so `T.btn` could time out after a successful trip to Ravenhold. The loop now stops once the travel has started (`busy`). The step's checks are unchanged.
- **Checks:** smoke PASS 207/207; check-scene PASS on all seven areas (plaza 11/11, lane 10/10, mossglen 11/11, hollows 10/10, rift 10/10, vanaheim 11/11, ravenhold 11/11). Two earlier smoke runs hit timing flakes at different steps while check-scene ran alongside (loot pick-up 4/5 at a 250 ms teleport; the bounce toadstool's 250 ms mid-flight lift sample read 0). Both steps passed unchanged in the green run; this commit changes no game code or area data.

## 2026-10-04: Hearthmoor Stage 5, part 4: Ravenhold Harbor (first playable slice)
- **New area `ravenhold`:** the Harbor district of Ravenhold, Midgard's harbor capital at the foot of the Rainbow Rift (per `docs/story/STORY_SEEDS.md` and the builder handoff). Bakery Lane has a new west road with a waystone; it leads to the harbor's east road, and back.
  - A stone quay (0.8 m) under an upper terrace (3 m) with the harbor stair.
  - Two plank piers on posts, two skiffs (furled sails, cold-fire stern lamps) and three rowboats moored on dark water with faint swell lines.
  - **Glow pass:** a row of six neon-blue cold-fire lanterns along the quay edge plus one at each pier end, each with a broken glow reflection on the water and twinkling glints on it. The first 7 lamps are real point lights (always faintly lit, brighter at night). Each lantern also stands in a cold-fire light pool (decal + motes; the 3 strongest near the camera share the pooled glow lights), so the cap holds and the quay stays dark between the pools.
  - Violet and Corsair-red accents: two violet and one red float lantern bob among the boats with their own reflections, a violet pool glows before the Market Terraces gate and a red one by Sable's barrels.
  - Three fish orbs (iron stands holding glass orbs full of glowing sea water with little gold, rose and coral fish) on the quay.
  - Neon fireflies and cold-fire wisps drift low over the water. Ravenhold glows at every hour (`ALWAYS.ravenhold`). No bloom.
  - Gloom-and-glow grades: an overcast blue day, a violet-blue dusk and a deep night with orange windows on the Rift Corsairs' counting house and the town houses on the terrace.
  - Red-white toadstools in the corners, including two clusters with a giant cap at the foot of the terrace wall in plain view (they glow at night like the other areas' toadstools), and a hidden bubbly spring behind a crate stack in the west corner. It heals and gives spring-fizz like the Hollows spring; the first find is a secret (+40 Gnome Council merit).
- **Clothing rule** (new in the style lock, Bill, 2026-10-04: separate top and bottom, a visible waist, readable shoes; no onesies or padded suits): the sprite tool takes `belt` and `sash` colours (the default brown belt is unchanged). Sable has a red waist sash, navy trousers and dark boots; Brannoc (fisher) a dark belt and yellow wellies; Ida (lamplighter) an open coat over a gold-buckled belt, grey trousers and dark shoes; Pip already passed. `docs/HD2D_COZY_STYLE_LOCK.md` gains an "Overrides from Bill" section with the boss-scale and clothing rules.
- **Fix:** Ravenhold's quest tags never appeared because the area had no game-effects sheet (`fx` was empty). The spec now sets `"gamefx": true`.
- **Sealed district gates:** the Market Terraces (top of the harbor stair), Old Temple and Forge Quarter (on the terrace) and the Undercity (at the waterline). Each is a stone arch with barred oak doors and a chain. The prompt says "sealed: coming soon"; E / A / tap shows its own text.
- **NPCs:**
  - Harbormaster Brannoc (fisher), who gives the story quest.
  - Quartermaster Sable of the Rift Corsairs (new `corsair` sprite: red kerchief, dark vest, red sash, ledger). Meeting her pays +20 Black Doubloons. Her choice explains how to earn Corsair merit and lets you pay the harbor dues once (25 gold for +15).
  - Ida Wickmere, cold-fire chandler (lamplighter), with Wickmere's Chandlery (`SHOPS.harbor`: tonics, glow seeds, a rift shard, gear).
  - Pip (fisher kid), who hints at the spring.
  - Rares and bosses in Ravenhold would count for the Corsairs (`REALM.ravenhold`).
- **Story quest "The Road to the Rift"** (`QUESTS.harbor`, `story: true`): take Brannoc's tally to Sable, climb the stair and look at the Market Terraces gate, report back. Brannoc points up through the Market Terraces to the Rainbow Rift; +40 Corsair merit, +30 gold, errand XP. Story quests show in the quest log once started ("Story: …") and never count as one of the three Lantern Eve errands (`errandsDone(S)`), so "quests n/3" and the Rift's opening are unchanged.
- **Waystones** (`game/ravenhold.js`): one by Bakery Lane's west road, one by the harbor's east road. E / A / Enter, or tap / click to walk up and tap again, opens a travel choice.
- **Tools:**
  - kit `tools/kit/kit_harbor.py`: harbor_water, pier, rowboat, skiff, pier / quay lanterns, bollard, waystone, district_gate.
  - assemble: spec `decks` (walk heights without a mesh) and `blocks` (blocked rects), piece markers `lamp_color` / `lamp_fixed` / `lamp_range`.
  - sprite: the `corsair` role.
  - The engine (runtime) is unchanged.
- **Smoke steps:**
  - lane → harbor with all the parts present;
  - the night shot;
  - E with Brannoc starts the quest (tags, log, still 3/3);
  - controller A with Sable (+20, step 2);
  - up the stair, E at the Market gate (prompt + "Coming soon", step noted);
  - Brannoc's turn-in (text, +40, +30 gold, still 3/3; quest shot);
  - the chandlery opens and closes;
  - the spring secret (+40 Gnome);
  - mouse click-click at the waystone, then key 1 travels to the lane;
  - controller A at the lane waystone travels back;
  - the east road returns to the lane;
  - phone: tap, tap the waystone, then tap "Stay here.".
- **Screenshots:** `docs/screenshots/stage5_ravenhold_harbor_night.png` (the east quay at night: the lantern row with light pools and reflections, fish orbs, toadstools, the red pool, Sable), `stage5_ravenhold_brannoc.png` (Brannoc turning in "The Road to the Rift").
- **Checks:** smoke PASS 207/207; check-scene PASS on all seven areas (plaza 11/11, lane 10/10, mossglen 11/11, hollows 10/10, rift 10/10, vanaheim 11/11, ravenhold 11/11). Lane's phone controller / tap-walk sub-checks flaked three times at load 15-19 (SwiftShader under 1 fps; the old ece94bc lane build measured no faster under the same load) and passed unchanged at lower load. No threshold was changed.

## 2026-10-04: Hearthmoor Stage 5, part 3: factions + merit
- **Five factions, six merit ranks** (`game/factions.js`, per `docs/story/STORY_SEEDS.md` and handoff §9). Ranks are Stranger → Friend → Trusted → Honored → Champion → Legend, at 0 / 150 / 400 / 800 / 1400 / 2200 merit. Each faction has its own currency name, signature glow colour, earn line, a title per rank and a Legend item (named for later).

  | Faction | Merit | Glow | Friend reward (live now) |
  |---|---|---|---|
  | Order of the Hearth | Hearth Tokens | gold `#f2c24a` | 10% off at Odo's |
  | Gatekeepers' Guild | Rift Marks | sky `#6cc8ff` | +25% gold from every rift you seal |
  | Gnome Council | Gilded Acorns | moss `#7ccf5a` | +10% gold from everything you pick up |
  | Rift Corsairs | Black Doubloons | red `#e0302a` | 15% off at Sefa's night stall |
  | Realm Embassies | Realm Favor | violet `#a45cf0` | +10% XP in Vanaheim |

- **How you earn merit** (hooked into what already exists):
  - errands: +40 Hearth;
  - sealing a rift: +30 / 60 / 120 Rift Marks by tier;
  - rares: +50 (+40 per extra trait) for the realm's faction (Midgard areas → Hearth, Vanaheim → Embassies);
  - Mossheart and other non-rare bosses: +80 for the realm's faction;
  - the drawer-nine riddle: +60 Gnome; gnome-door secrets: +40 Gnome;
  - Sefa's gems and gear: +15 Corsair, −5 Hearth (the rivalry; ranks never drop);
  - the first talk with Warden Hilde: +20 Hearth.
- **Saved per slot:** `S.merit`, `S.ranks`, `S.title`, `S.factionsV`. **Save migration:** a save from before factions is seeded once on load from its finished errands, sealed rifts, hunt log and solved riddle.
- **Factions panel:** a fifth hero-screen tab. Open it with **H**, the Factions tab button (touch / mouse), or controller Start → RB → LB / RB. Each row is edged and swatched in the faction's glow colour (hard pixel edges, no blur) and shows the rank, merit, a progress bar to the next rank, the Friend reward and how to earn. Enter / A / tap **title** wears that rank's title, shown in the hero header.
- **Rank-up:** a toast in the faction's colour ("✦ Gatekeepers' Guild: Friend! Title "Rift Warden" · unlocked: …"), a `sparkle_burst` on the hero, a 1.6 s point light in the faction colour, the quest chime, and a save. Rank-up toasts take priority: a toast that arrives while one shows (the rift's loot toast, a pickup) now waits in a short queue and shows after it, so the rank-up is never wiped out (`toast(msg, s, html, prio)`, `G.toastQueue()`).
- **Warden Hilde of the Hearth** (rune guard sprite) stands on the Plaza terrace, right of the moss gate. She takes her post once Lantern Eve is over (or skipped), so she stays out of the opening's fight by the gate. Her three pages introduce the five banners and the ranks, pay the first Hearth Tokens and open the Factions tab. Later chats are a single line and leave the tab closed, so closing her dialogue never pops a panel over the field.
- Shop rows show the faction price (`shop.js`). Rift seals and gold pickups apply the Guild and Gnome bonuses. Vanaheim XP applies the Embassy bonus.
- **Smoke steps:**
  - merit earned from play (errands, rares, riddle, secrets, Sefa);
  - +50 for a one-trait rare; +30 / 60 / 120 per rift tier;
  - the abyssal seal lifts the Guild to Friend with the toast, sparkle and light;
  - Hilde's talk (+20, the panel opens);
  - five rows in the five glow colours;
  - H, the touch tab and the controller route;
  - the Friend rewards; wearing a title;
  - the save migration (seeded once, exact values);
  - merit, ranks and the title saved in the slot;
  - a toast arriving during a rank-up waits in the queue, then shows.
  - The Odo tonic / glow-seed steps now expect the exact Hearth Friend price.
- **Screenshots:** `docs/screenshots/stage5_factions_panel.png`, `stage5_rank_up.png`.
- **Checks:** smoke 196/196. check-scene: plaza 11/11 and lane 10/10 on the final Hilde placement (16:42-16:57 ET); mossglen 11/11, hollows 10/10, rift 10/10 + height EXEMPT, vanaheim 11/11 on b779087 (15:12-15:35 ET; Hilde only stands in the plaza). Several smoke runs at load 12-19 died early on different timing-sensitive steps (first fight, controller hot-plug / hold-Y wheel, phone action buttons); none were weakened. Two real failures were fixed: Hilde overlapped the elder (plaza sprites_sharp / colours), and she stood in the opening fight and the phone's open-ground tap spots, so she moved right of the moss gate and arrives after Lantern Eve. The rank-up screenshot is a fresh capture with the toast up (the smoke-run shot caught it after it faded).

## 2026-10-04: Hearthmoor Stage 5, part 2: procedural rares + random rifts
- **Procedural rares** (`game/rares.js`): a rare is a base body + an element affix + a trait, seeded by day and area.
  - **Bodies**, drawn natively at 2-3x the hero on each wild area's boss sheet (`tools/sprite/boss_sheet.py`, 50x80 frames like Mossheart, style lock: never upscaled):
    - the **Elder Wraith** (~2.4x): a towering hooded cold-fire spectre in tattered layered robes, a crown of cold-fire tongues, skeletal hands and a cold-fire chain lantern;
    - the **Death Lord** (~2.4x, the skeleton line's T4): a skeleton knight in dark rune plate, a horned helm over a bone skull with cold-fire eyes, spiked pauldrons, a deep-red cape and a rune greatsword;
    - the **Sporemother** (~2.2x): a giant spore elemental, a floating moss mound under a wide rose toadstool cap with gold lamp eyes, root tendrils and a spore ring.
  - **Elements:** Frostfire (blue), Gloam (violet) or Bloodmoon (red). The element is the name prefix, a marching ground aura (`rare_aura_blue` / `_violet` / `_red`, new in `spells.py`) and the rare's own point light.
  - **Traits:**
    - **Shielded:** a rune ward soaks 70% of each hit until it breaks, then regrows after 8 s.
    - **Enraged:** below half health it gets faster and hits harder.
    - **Blinking:** it blinks to your side every 5-7 s.
    - **Summoner:** it calls up to two lesser kin.
  - **Name:** trait(s) + element + body, e.g. "Shielded Gloam Death Lord". The name shows in its element colour on the boss bar.
  - **Where they appear:** they roam Mossglen and the Hollows (Elder Wraith / Death Lord) and Vanaheim (Sporemother), with a 30% chance per area per day (45% at night) and one per area per day. They also come out of rifts.
  - **Rewards:** every rare always drops a Rare-or-better item (Epic+ for two-trait rares), a 50% rift shard, extra gold and big XP. Each kill goes into the **hunt log**.
- **Hunt log:** a new section in the quest log (J / Start / ☰). It lists every rare felled (an element swatch, the name, kills, the first day) and the rifts sealed per tier. Saved in the slot (`S.hunt`, `S.rifts`).
- **Random rifts** (`game/rifts.js`): small tears open now and then in Mossglen, the Hollows and Vanaheim. The first comes 45-80 s after you arrive, then one every 2-3.5 minutes; a toast warns you.
  - **Tiers:**
    - **I minor:** a small cold-fire tear (`rift_tear_minor`), 3 foes, a 15% rare.
    - **II major:** the violet-red tear, 4 foes, a 50% rare.
    - **III abyssal:** a wide crimson tear over a rune ring (`rift_tear_abyss` + `rift_ring_abyss`), two waves of 4 and always a two-trait rare.
  - **How a rift plays:** walk within about 3.4 m and it spits out its wave (one more foe at night). Clear every foe and it seals with gold, XP (40 / 90 / 200), an item of at least Uncommon / Rare / Epic, and a chance of rift shards. A rift you ignore closes by itself after 90 s. Rifts only open on their own in normal play: `?qa` / `?peace` need `&rifts`, and `?riftnow=1|2|3` opens one on arrival.
- **Combat hooks** (`combat.js`):
  - `spawnEnemy` takes a built def (`sp.D`), and `sp.once` foes don't respawn.
  - Enemies may carry `tick` (traits), `mods.hurt` (ward) and `onKill`, and `D.xp` overrides the XP table.
  - Rares get the named bar up top.
- **Loot** (`loot.js`): `onKill` honours `minRar` (always an item of at least that rarity), and the new `dropItem(x, z, lv, minRar)` serves the rift rewards.
- **Area specs:** `boss_roles` now lists mossglen eldergolem + elderwraith + deathlord, hollows elderwraith + deathlord, and vanaheim sporemother.
- **QA effects lineup, paged** (`tools/runtime/web/engine/main.js`, `effects.js`, `tools/check-scene/check_scene.py`): the six new effects take the spell atlas to 44, and one screen at 15 a row packed neighbours over the new rings (`effects_sharp` dropped to 0.91-0.94 in mossglen / hollows / vanaheim). The engine adds `effectOrder` / `effectPages(per)` and `effectLineup(frac, page, per)`; check-scene walks pages of 24 at the full 2.4 m spacing (`effects_p2.png`). Lineup effects are still never occluded by the scene but are now ordered among themselves (decals, then billboards, each far to near, by renderOrder with the depth test off; one shared depth let the first-drawn win), and effects that float 1 m or more (light orb, bolts, seed bomb) go to the back row of their page, so lane's light orb (lifted 1.5 m) no longer rises over the earth burst behind it. Rows sit 3.2 m apart, deeper when a camera squeezes that into under 1.35 cells on screen: only the rift's far camera (118 px vs 132-141 px elsewhere, so 3.52 m there), where a front-row billboard reached into the back-row red aura. The 0.97 threshold is unchanged.
- **check-scene under load:** after laying out an effects or gamefx lineup page it now waits for the engine to draw 3 more frames (up to 20 s) before reading the rects, as smoke already does. On a box at load ~20, plaza's second gamefx page drew no frame in the fixed 1 s and the rects came back unset (a KeyError, not a check failure).
- **Smoke steps:** a rare's name, aura, light and native 2-3x size; the Shielded ward and the coloured bar; the hunt entry and the Rare+ drop; Blinking, Summoner and Enraged; the hunt log via J; rift tiers I-III opening, engaging and sealing with rewards; rift rares in the hunt log; an ignored rift closing; a rift auto-opening on its timer; hunt + rifts saved.
- **Screenshots:** `docs/screenshots/stage5_rare_death_lord.png`, `stage5_rift_abyssal.png`, `stage5_hunt_log.png`.
- **Checks:** smoke 179/179 (one re-run: the terrace pathfinding step's fixed 3.5 s wait came up 0.01 m short at load ~15); check-scene plaza 11/11, lane 10/10, mossglen 11/11, hollows 10/10, rift 10/10 + height EXEMPT, vanaheim 11/11. Re-runs only for load: lane and rift phone checks once each; plaza's portrait tap-walk failed at load 17-24 with the same numbers as the live 8904caa build on the same box (2.4 -> 2.27 m), then passed at load ~10.

## 2026-10-04: Hearthmoor Stage 5, part 1 polish: paper sky lanterns and a bigger rift tear
- **Sky lanterns redrawn** (`sky_lantern` in `tools/spells/spells.py`): the rising lanterns no longer read as orange eyeballs (the old round orange disc had a dark fish in the middle). They are now paper sky lanterns, a little taller than wide with a rounded crown. The cream-gold paper glows from inside: white-hot just above the flame, cream in the body, gold at the shoulders and a warm amber rim. They have soft dithered ribs, a bamboo hoop with a bright flickering flame at the bottom opening, a warm glint on the paper and a small twinkle circling each one. There is no dark centre.
- **Rift tear enlarged** (`rift_tear`): it now fills the full 32 px cell height, zigzags harder, and has a fixed jagged lip profile and four short side cracks. The void has violet lips and a hard neon-red edge line, with red embers and sparks spitting off. Palette and NEON pixels only, no bloom.
- Screenshots `docs/screenshots/stage5_lantern_eve_lanterns.png` and `stage5_lantern_eve_rift_tear.png` were refreshed from the smoke run.
- **Checks:** smoke 166/166, Plaza check-scene 11/11. The first Plaza run measured 0 effect rects even though its shot showed the full lineup, a one-off timing flake; the re-run passed.

## 2026-10-04: Hearthmoor Stage 5, part 1: the Lantern Eve opening
- **A new game now opens on Lantern Eve** (`game/intro.js`, class `Intro`): day 0 at dusk in the Plaza. After the hero pick and the auto-level ask, seven paper sky lanterns are lit and float up over the square. Each carries a warm light pool and sparkles, and two warm point lights ride along with them. Bram (the innkeeper) steps out and speaks, then the elder, a kid and the baker, all in the usual dialogue panel.
- **The story beat:** a violet-red tear (`rift_tear`) flickers open over the moss gate and the lanterns stop in the air. A cold-fire wraith (`evewraith`: hp 30, light hits, no loot) slips out, and Bram's line starts the hero's first fight under the lanterns. When the wraith falls, the tear seals, the lanterns drift on, and the villagers send you off. The three existing errands follow as the **Lantern Eve tasks** (the quest log heading and the welcome toast say so).
- **Skip and replay:** a carved-wood **skip ▸▸** chip sits at the top centre while the opening plays. Esc, controller B or a tap on the chip skips it, and walking and fighting are blocked only during the lantern and tear beats. `S.flags.intro` records `playing`, then `done` or `skipped`, and the opening never replays on Continue (a save made mid-opening resumes as skipped). Leaving the area mid-opening ends it quietly. `?nointro` starts a new game without it.
- **New effects** (`tools/spells/spells.py`, style lock pixel billboards): `sky_lantern` (6 frames: a round paper lantern with a swimming fish, cap, flame and tassel) and `rift_tear` (8 frames: a jagged void seam with neon violet lips, red edges and sparks). All areas were rebuilt with them.
- **Plaza sheet:** `sprite_roles` adds `innkeeper` (Bram for the opening) and `wraith`. `combat.spawnEnemy` takes an optional `def` so a spawn can use an `ENEMIES` entry other than its sprite role.
- **Fix:** the skip chip sits in `#hud` (which passes clicks through), so it sets `pointer-events: auto`. A phone tap had been landing on the canvas.
- **Smoke:** new steps cover the opening (lanterns rising, the four speakers, the tear, the wraith, the fight by R, the finish and the Lantern Eve tasks), Esc skip, controller B skip, a phone tap on skip (thumb-sized chip), and Continue never replaying the opening.
- **Checks:** smoke 166/166. check-scene: plaza 11/11, lane 10/10, mossglen 11/11, hollows 10/10, rift 10/10 (height exempt), vanaheim 11/11.
- **Screenshots:** `docs/screenshots/stage5_lantern_eve_lanterns.png`, `docs/screenshots/stage5_lantern_eve_rift_tear.png`. `docs/screenshots/stage4_rift_shrine_night.png` was refreshed from the latest rift check-scene.

## 2026-10-04: Hearthmoor Stage 4, part 6: the Rift Shrine + Vanaheim
- **The Rift Shrine** (`areas/src/rift.json`, area `rift`): a small gloom-and-glow stone circle floating in the rainbow-rift void. It's a paved isle with a tapering rock root, hanging roots and moss, plus floating rock shards in the dark violet void, a rune dais and standing stones. It is reached through the Plaza's moss gate: once the three errands are done (or `S.flags.rift`, or `?rift`), stepping into the swirl opens the dialogue choice panel ("Mossglen" / "The Rift Shrine" / "Stay here"). Before that the gate still goes straight to Mossglen.
- **Realm gates:** Vanaheim's is open (a new `rift_vortex`: a green-gold spiral fringed with neon-blue cold-fire tongues). Alfheim (violet), Niflheim (blue) and Muspelheim (red) are sealed (`rift_seal_*`: a dark slow swirl, a dashed neon rim and a lock rune that pulses faintly). E / A / tap at a sealed gate says why it won't open. A mossy gate leads home to the Plaza. Bifrost Crossing's nine gates come in Stages 5-6.
- **Vanaheim, Mossbrook Springs** (`areas/src/vanaheim.json`, area `vanaheim`), the first realm (the docs leave the order free; Vanaheim is the swing realm):
  - the springs below the mushroom village, with gnome stumps, giant glowing toadstools, ferns and cold-fire braziers;
  - the poisoned spring and a glade both marked with Veyra's violet Alfheim rune (`alf_rune`);
  - a gold-green day grade and a teal and violet night;
  - a vine-arch rift gate back to the shrine.
- **Realm enemies** (style lock pixel billboards, `tools/sprite/roles_enemies.py`):
  - the **spore elemental** (`sporeling`: a floating moss puffball with a rose cap, glowing eyes and orbiting spores; ranged, it lobs spore pods);
  - the **moss golem** (`mossgolem`: a heavy slam that roots you and drains stamina).
  - Three spore elementals (one only at night) and one moss golem patrol the springs.
- **The alliance choice:** Elder Burrowmoss, spring-warden of Mossbrook (a gnome), tells you about the poisoned spring and asks what you are to Vanaheim:
  - "A friend" sets `S.flags.alliance.vanaheim = 'befriend'`;
  - "Vanaheim will bow to Hearthmoor" sets `'conquer'`;
  - "only passing through" asks again next time.
  - His later greeting depends on your answer. For now the choice only sets the flag.
- **Mossbrook art pass (lusher gloom-and-glow at night):**
  - **The poisoned spring** now reads as corrupted: a new `spring_poison` water decal over the basin (a sickly violet dithered swirl with slow dark bubbles that swell and pop into violet rings) and a violet light pool.
  - **A cleansed state for later:** `spring_clean` (clear blue water, pale ripples, twinkling white sparkles) sits behind `S.flags.vanaheim_spring === 'cleansed'`. The area's `game.swaps` entry swaps the decal on load (`applySwaps`, test hook `G.applySwaps()`), and the spring's pool turns cold blue (a glow.js `POOLS` entry can carry a flag override).
  - **Three wild glow-plant clusters** (the garden's cold-fire blooms and violet glowbells, a new glow.js pool kind `bloom`: three plants over their ground pool decal, no point light of their own) and two light pools on the path from the vine gate (cold-fire and warm gold).
  - Five more firefly / bug emitters, and a slightly brighter teal night grade.
  - Real point lights stay at the glow-light cap (3, or 2 on phones): the engine gives its fixed pool of lights to the strongest glows near the camera, and the new clusters add none.
- **Portal art** (`tools/portal/portal.py`): Bill's rift refs were used for style only and redrawn fresh in the cozy palette. New effects: `rift_vortex`, `rift_seal_violet`, `rift_seal_blue`, `rift_seal_red`, `rift_ring` (the shrine's ground circle, with blue, violet and red rune dashes) and `alf_rune`. `portal.py` gains the named `NEON` set (violet and red as in `spells.py`, plus `neon_blue*` for cold-fire), used for effect pixels only.
- **Kit:** `tools/kit/kit_rift.py` adds `rift_isle`, `rift_arch`, `rift_shard`, `rift_dais` and `vine_arch`.
- **Assemble:**
  - `ground.ellipse` gives a round walk edge.
  - Props take `walkable` (taps and clicks land on the isle), `y` (floating shards), `cast: false`, and `glow` (a coloured lamp on rift and vine gates).
- Screenshots: `docs/screenshots/stage4_rift_shrine_night.png`, `stage4_vanaheim_night.png` (retaken after the art pass), `stage4_vanaheim_alliance_choice.png`, `stage4_moss_gate_choice.png`, `stage4_vanaheim_spring_poisoned.png`, `stage4_vanaheim_spring_cleansed.png`.
- **Rift Shrine grades + dais lanterns:** the void keeps its timeless violet look but now follows the clock a little: slightly brighter violet by day, bluer at dusk, deeper at night (check-scene `grades` passes for real). Two stone lanterns flank the back of the rune dais and give a faint warm glint at night. A raised 1 m terrace dais was tried and dropped: the walk-height grid only models rect terraces + stairs, and a square block looked wrong on the round isle (and buried Ondra), so the rift's spec carries a documented `game.qa_exempt.height` (check-scene now honours `qa_exempt` for `height` / `grades` only and prints `[EXEMPT]`; sharpness, bloom and phone checks can never be exempted).
- **Controller Y tap fix:** a Y tap can only turn into a hold (the spell wheel) after 350 ms *and* 3 drawn frames, so a frame hitch on a slow phone no longer swallows a tap cast.
- **QA:** the engine's gamefx lineup is paged (one row of at most 7 effects per page, `gamefxPages()`), and check-scene walks every page (`gamefx.png`, `gamefx_2.png`): with 13 game effects the single row ran off both screen edges and 6 were skipped. Smoke: `T.frames(n)` waits for drawn frames after the analog-stick input, and the Y-cast step waits for the cast (castT / a cooldown starting / an effect) instead of one fixed 300 ms look; the cooldown from the F cast is awaited first. Assertions are unchanged.
- Checks: smoke PASS 155/155 (7 new rift / Vanaheim steps + the art-pass steps). check-scene PASS: rift 10/10 + height exempt (`game.qa_exempt`), vanaheim 11/11, plaza 11/11, mossglen 11/11.

## 2026-10-04: Hearthmoor Stage 4, part 5: dialogue choices
- **Reusable choice panel:** any dialogue entry can end in `choice: { id, options: [{ label, pick(G) -> reply entry | null, cancel? }] }`. When the last page has typed out, numbered parchment rows appear inside the wooden frame. Keys: arrows / W S and E / Enter, or 1-4. Controller: d-pad and A. Touch / mouse: tap a row (a tap elsewhere on a choice page does nothing, so nothing is picked by accident). Esc / B takes the option marked `cancel`. Answers set `S.flags` (saved with the slot) and `S.chose[id]`.
- **Bix's riddle lock** (the start of "Gnome in the Vault"): after your first visit, Bix offers drawer nine's riddle. "Footsteps" opens it (a moon opal + 25 gold, and his greeting changes for good); a wrong answer earns a hint and a retry; "not now" goes straight to the vault.
- **Bram's Lantern Eve wish:** once the bread is delivered, Bram asks who your lantern is for. Family gives 2 Hearth tonics, all of Hearthmoor 30 gold, whoever is lost 2 glow seeds, and each changes what he says afterwards. "I'll decide later" asks again next time.
- Glow seed blurbs now point to the Lane plot's new spot.
- Screenshot: `docs/screenshots/stage4_dialogue_choice_bram.png`.
- Checks: smoke PASS 145/145 (5 new choice steps: Bram by mouse click and his changed reply, Bix by keys (Esc = not now, arrow + E wrong answer), Bix by controller (d-pad + A solves it), answers surviving reload #2). check-scene PASS: plaza 11/11, lane 10/10, hollows 10/10, mossglen 11/11.

## 2026-10-04: Hearthmoor Stage 4, part 4: weather
- **Per-area weather on the day cycle** (`game/weather.js`, `weatherAt(area, day, t)`):
  - Plaza and Bakery Lane share one town sky: each 6-hour block of each day is clear, drizzle or rain (seeded by the day, so it is the same on every machine). Day 0, Lantern Eve (the opening), is always clear.
  - Mossglen: mist in the mornings (05:17-10:05).
  - Toadstool Hollows: drifting self-lit glow mist all night (19:12-06:00).
  - Snow is ready (the `snowfall` preset; `?wx=snow` or `weather.force('snow')`), but no area schedules it yet.
- **Soft pixel particles** (`tools/particles/particles.py`, rows 16-19): `mist` (a low ordered-dither puff that thickens then thins, no blur), `glow_mist` (the same in cool sky / flower-blue, self-lit), `wet_glint` and `wet_glint_cool`. Rain drops and splashes are now 45% self-lit (`glow` may be a number in `particles.js`), so they still read in the dark.
- **Wet cobbles shimmer:** rain soaks the ground over ~20 s and it dries over ~60 s. While wet, every light zone in view (lamps at night, glow and cold-fire pools, braziers, garden blooms, the night merchant's lantern, glowing toadstools) throws short 1-3 px vertical reflection glints on the ground around it. Warm lights give `lamp` / `flower_gold` glints, blue ones `sky` / `flower_blue`, and open ground gets a few sky glints. Palette pixels only, no bloom.
- **Options -> weather: on / light / off** (`#btnWeather`, mouse or touch; R or controller Y while Options is open). Light halves the rain, mist and glints, and is the default on phones (coarse pointer). Saved per device (`hearthmoor-weather`), not per save slot. Arriving in an area pre-warms its weather, so it is already falling.
- QA captures (`?qa`, check-scene) stay clear unless `?wx=<kind>` asks for weather.
- Screenshots: `docs/screenshots/stage4_weather_rain_night_plaza.png`, `stage4_weather_glowmist_hollows.png`.
- Checks: smoke PASS 140/140 (7 new weather steps: calendar, rain + splashes + glints at night, Options by mouse / R / controller Y, Hollows night glow mist, Mossglen morning mist, phone default light + touch cycle). check-scene PASS: plaza 11/11, lane 10/10, hollows 10/10, mossglen 11/11.

## 2026-10-03: Hearthmoor Stage 4, part 3: glow-gardening
- **Garden plots:** a timber-edged soil bed with three beds in Bakery Lane on the open lower street (3.6, 4.6) under the lamp post, near Odile the gardener, in full view of the camera (the first spot, 5.1, 2.2, was hidden under the flower shop's awning), and one in Toadstool Hollows (0.6, 4.8, open ground away from the braziers, pools and toadstools). Area specs: `game.gardens` (`id`, `pos`, `kinds`).
- **Grow:** E / controller A / the pad's MAIN button beside an empty bed plants one of Odo's glow seeds. It sprouts after one in-game day and blooms after two. `S.day` counts whole days as the clock passes midnight; growth is saved per bed in `S.garden`.
- **Three glow blooms** (new `spells` effects, palette + neon accent pixels, no bloom):
  - a **cold-fire bloom** (neon-blue flame flower, sparks; night pool `coldfire_pool`, blue light) -> harvest a frost core;
  - a **violet glowbell** (three neon-violet bells, white glints; night pool `violet_pool`, violet light) -> a moon opal;
  - a **red glow toadstool** (saturated red cap, crisp white spots; night pool `red_pool`, red light) -> 2 Hearth tonics.
  - At night every bloom casts its light pool (ground decal + a point light in its colour) and is a light zone (`src: 'garden'`: glowlit, wraiths keep away).
- **Neon accents:** violet and a saturated toadstool red are not in the cozy palette, so `spells.py` has a small named `NEON` set (`neon_red*`, `neon_violet*`; the red matches the Hollows kit's self-lit toadstools) for glowing effect pixels only. The world, sprites and HUD palette are unchanged.
- New effects: `garden_plot` (decal), `glowplant_seed`, `glowplant_sprout`, `glowplant_coldfire`, `glowplant_violet`, `glowplant_toadcap`, `violet_pool`, `red_pool` (36 effects).
- Odo's glow seed blurb now says where to plant it.
- **Fix: the Hollows <-> Mossglen edge exits could not always be walked into.** Both trigger rects ended 0.075 m inside the area's last walkable cell (the nav grid keeps the hero's 0.28 m radius off the map edge), and a click / tap / path walk stops within 0.12 m of its goal, so on a quiet machine the hero could stop just short of the trigger. This was a real bug (it also caught tap-to-walk players), not box load. Both rects now reach 0.35 m further in (`x <= -12.45` west in the Hollows, `x >= 12.45` east in Mossglen); the arrival spawns (-11.4 and 12.2) stay outside them. All the other exits and portals were checked: their nav goals sit 0.3 m or more inside.
- Screenshots: `docs/screenshots/stage4_garden_night_lane.png`, `stage4_garden_night_hollows.png` (all three blooms with their pools).
- Checks: smoke PASS 134/134 (6 new garden steps). check-scene PASS: lane 10/10, hollows 10/10, plaza 11/11 (36 effects in the lineup).

## 2026-10-03: Hearthmoor Stage 4, part 2: the Nine Keys Bank (Bix Coppertuft, a shared 40-slot vault)
- **Bix Coppertuft**, gnome clerk of the Nine Keys Bank, stands on open cobbles west of the plaza (-6.0, 4.4), clear of the bunting, the well, Sefa's spot and the start-to-lane path (checked against the baked collision grid). He uses the `gnome` sprite, now named on the Plaza sheet (`sprite_roles`).
- **One vault for every save slot:** `localStorage` `hearthmoor-bank-v1` (`{v, items, gems, gold}`), not part of any slot save. 40 slots: each piece of gear takes one, each gem kind stacks in one. Gold has its own rows (deposit / withdraw 10, or all). Banked gold is not carried, so a faint never drops it.
- The bank reuses the shop panel (`Shop`, `SHOPS.bank`, tabs Deposit / Vault): keys (arrows, Enter), controller (d-pad, LB / RB, A) and touch (tabs, row buttons) all work.
- Smoke: 6 new steps (Bix is there, the panel opens, keyboard gold deposit, controller gear deposit, touch take-out + gold withdraw, the vault is outside the slot save). Smoke: 129/129; check-scene plaza 11/11.
- The shop panel's footer hint now follows the panel (bank: deposit / vault).
- Screenshots: `docs/screenshots/stage4_slot_picker.png` (live build), `stage4_bix_plaza.png`, `stage4_bank_deposit.png`, `stage4_bank_vault.png`.

## 2026-10-03: Hearthmoor Stage 4, part 1: three save slots with a slot picker on the title
- **Save slots:** three slots, `hearthmoor-slot-<n>-v2`. Slot 1 keeps the old single-slot key `hearthmoor-slot-1-v2`, so an existing save simply is slot 1 (no data moves). The v1 save still migrates, into slot 1. Deleting slot 1 sets `hearthmoor-v1-migrated` so an old v1 save can't reappear. The last slot used is remembered (`hearthmoor-lastslot`); `?slot=N` picks one.
- **Slot picker on the title:** three carved-wood / parchment cards, each with the hero's own pixel sprite (idle-down frame from the Plaza atlas, integer scale, nearest-neighbour), hero, level, area and play time. Continue and New game act on the chosen slot.
  - **Copy slot** copies the chosen slot into the first empty one. **Delete** asks first ("Delete slot N? Press again", 4 s), with no browser dialog.
  - Keys: left / right (or A / D), 1-3, C copy, Delete / Backspace delete. Controller: d-pad / LB / RB pick, Y copy, RT delete, A / Start continue, X new game. Touch / mouse: tap a card to pick it, tap the picked card to continue.
- **Smoke test:** 6 new steps (the cards, keyboard copy, keyboard pick, controller delete with its confirm, d-pad back, tap pick). Smoke: 123/123; check-scene plaza 11/11. The elapsed-time printout is fixed: the start time was being overwritten by a later `t0` (tonic count), so it printed the clock time.
- Next in Stage 4: the shared bank (40 slots, gear + gems, gold deposit / withdraw), then glow-gardening.

## 2026-10-03: Hearthmoor Part 6: bright toadstools, gnome doors + Pipkin, the bubbly spring, cold-fire braziers
- **Toadstool art fix:** the giant toadstool caps (and the clusters and bounce caps) are now a clear saturated red with crisp bright-white spots and warm glowing gills underneath.
  - They use a new self-lit `glow` world material (`world.js` `litify`: an unlit `MeshBasicMaterial` that shows the baked vertex colour). So they read against the gloom at every hour with no new lights and no bloom. The dome's lower rim is a deeper red so the shape still reads.
  - Each giant toadstool also has a warm dithered `light_pool` decal underneath (a decal only, no light).
- **Gnome doors:**
  - Three `gnome_stump` homes with round doors and lit windows (`game.doors`; E / A opens one).
  - One door hides a little chest: +12 gold and a Hearth tonic, once.
  - The other two open on a peeking gnome: a dialogue with the gnome portrait ("Shoo, shoo! The mushroom loaf isn't ready yet!").
- **Pipkin, a toadstool gnome:** a new `gnome` sprite (small, tall pointy red cap with a white tassel, bushy white beard, blue smock, belt and boots). It is on the Hollows sheet only: roles marked `named` are built only when a spec names them, and the `combat` token skips them. Pipkin has three short lines pointing at the bounce cap, the spring and the braziers.
- **The hidden bubbly spring** sits on the bounce ledge (`spring_basin`, self-lit blue water).
  - It has rising, wobbling, popping glowing bubbles (new `spring_bubbles` effect), glitter and a soft sky-blue light.
  - Walking in heals you fully, refills stamina, and gives **spring-fizz** for 60 s: +15% damage and faster stamina (`Hollows.dmgMul` / `regenMul`, folded into `glow.dmgMul`). It can be used again after 8 s.
- **Dark-hour cold-fire braziers:** three stone-and-iron braziers (`game.braziers`). Cast a spell beside one, or land a spell's light pool near it, and it catches.
  - A lit brazier burns a neon-blue cold-fire tongue (new `coldfire_flame` effect), with cold-fire motes, a blue `coldfire_pool` and a blue light.
  - It burns through every dark hour (dusk to dawn) and flares for 25 s when struck by day. Lit braziers are remembered in `S.found`.
  - Burning braziers are light zones (`src: 'brazier'`, r 3.2): you're glowlit there and wraiths keep away.
  - The flame sits over a wide neon-blue `coldfire_pool` (4 decals).
  - Casting beside a brazier is detected from the spell or charm cooldown starting. Spells return `false` from `Combat.cast` so the engine skips its own effect, which hid the cast before this fix.
- **Sprite sheets:** Hollows actors 560x3456 (under 4096); spells 256x896.
- **Tests:**
  - 5 new smoke steps (gnome talk, chest door, peek door, spring heal + buff, brazier lit by a cast). Smoke: 117/117 (re-run before push).
  - check-scene: hollows 10/10, mossglen 11/11. All of Part 6 (toadstool fix, gnome doors, spring, braziers) is done and live.
  - check-scene's effect lineup (`effectLineup` in `main.js`) now alternates wide ground decals with narrow billboards. With 28 effects the row got tight and `bloom_ring` overlapped its neighbour.
  - The Hollows' front mushroom ring moved off the lineup row.
- Screenshots: `docs/screenshots/part6_hollows_night_toadstools.png`, `part6_bubbly_spring.png`, `part6_brazier_gnome.png`.

## 2026-10-03: Hearthmoor Part 5: Toadstool Hollows (area + bounce toadstools)
- **Toadstool Hollows**, a new area (`areas/src/hollows.json`): walk out of Mossglen's east edge, past Mossheart's clearing, and the west edge of the Hollows brings you back.
  - It's a dim mossy hollow with a dirt floor, a mossy bank with stairs, and a high east ledge.
  - It has giant red white-spotted toadstools (`toadstool_big`), toadstool clusters, mushroom rings, ferns and standing stones, with fireflies and motes at every hour.
  - The grades are dark: teal-grey by day, violet at dusk, deep indigo at night.
- **Always-on glow:** the Hollows' toadstool clusters glow at every hour. There are 6 standing light pools: violet and pink `light_pool` with glitter, and neon-blue `coldfire_pool` with cold-fire motes.
  - Each pool carries its own point light (`glow.js` `ALWAYS` / `POOLS`) and is a light zone (`src: 'pool'`), so you're glowlit there and wraiths keep away.
  - Violet comes only from lights and grades; the cozy-village palette is unchanged.
- **Enemies:** a cold-fire wraith, a night wraith and a skeleton (`SPAWNS.hollows`). Their sprites come from the Hollows sheet (560x3328, under 4096).
- **Bounce toadstools** (`game/hollows.js`, area `game.bounces`):
  - Press jump (Z / LS) on a low wide bounce cap and you spring along a high arc onto the hidden east ledge ("Boing! A hidden mossy ledge.", remembered in `S.found`).
  - A second cap on the ledge springs you back down.
- **New kit pieces** in `tools/kit/kit_hollows.py`: `toadstool_big`, `toadstool_cluster`, `bounce_toadstool`, `gnome_stump`, `spring_basin`, `brazier` (the last three are for the next steps).
- **Tests:** new smoke steps cover Mossglen -> Hollows -> Mossglen and the bounce up and back down. Smoke: 112/112. check-scene now runs on `areas/hollows`.
- Gnome doors, the spring and the braziers followed in Part 6 (above).
- Screenshots: `docs/screenshots/part5_hollows_night_pools.png`, `docs/screenshots/part5_bounce_toadstool.png`.

## 2026-10-03: Hearthmoor Part 4: skill tiers II-III with capstones, summon tiers; check-scene fixes
- **Skill tiers II and III:** every hero's three branches now run three tiers deep (9 nodes per hero). Tier II costs 1 point at level 5 and needs that branch's tier I; tier III is the branch **capstone**, 2 points at level 10, needing tier II. Capstones include Hearthfire Heart, Worldroot, Unbroken Wall, Sunrise Cleave, Great Sigil, Between Steps, Fate-reader, Hammer of Skies, Eye of the Storm, Evergreen, Thornheart, Sunforged and Cinder Wraithblade, plus a top summon capstone per hero (Elder Mushroom Golem, Rune Colossus, Thunderhead, Elder Treant, Ash Legion Lord). New skill effects: shorter spell cooldowns (`spellCd`), harder crits (`critDmg`), faster stamina refill (`stRegen`), quicker summons (`summonCd`).
- **Hero screen Skills tab** lists the tree by tier (tier headers, capstones edged in gold). Rows you can't learn yet are dimmed, and their button says why ("needs Gale Bolt", "Lv 10", "2 points"). The top line shows your current summon tier. Keys, controller and taps work as before, and tier-I rows keep their old positions.
- **Summon tiers:** each summon-branch skill raises your summon a tier (I to IV, shown in its name, e.g. "Storm sprite III").
  - Tier II glows: a soft light in its colour follows it, and it sheds sparkles.
  - Tier III takes a **radiant form**: a new `<summon>_r` sprite for all six summons, with brighter colours, a gold-white crown of light, a lit rim and twinkling sparkles. It arrives on a rune circle with a stronger light.
  - Tier IV (capstone) adds a sparkle burst on arrival and the widest light.
  - Stats still grow through `summonMul` / `summonLife`. All of it is palette pixels with no bloom (gloom-and-glow).
- **check-scene fixes:**
  - The QA effects lineup keeps a 26-effect row on screen (spacing `min(2.4, 19.2 / cols)` m). Before, the new cold-fire effects pushed `impact` off-screen.
  - Odo moved to [5.4, 3.4], in front of the barrels and crates, so the Plaza bunting no longer crosses his sprite (it was failing the sprite_sharp check).
- Smoke: new steps for the tiered tree (capstone locked until tier II, learned by keys, mods apply) and summon tiers I / III / IV. 109/109 pass. check-scene on the same build (5af7ea8 content): plaza 11/11, lane 10/10, mossglen 11/11 (all 26 effects on screen in the lineup).

## 2026-10-03: Hearthmoor: Mossheart at boss scale, Sefa's neon-blue lantern pool, glow-light cap option
- **Mossheart is now ~2.5x the hero** (style lock "boss scale override": mini-bosses / rares 2-3x, bosses 5x+). It is **drawn natively** on its own boss sheet at 50x80 px frames (same texel density as the 20x32 actors, never an upscale): ancient stone-block masonry, a faceted amber crystal crown, gold rune glyphs and a zig-zag heart seam, thick moss with grass blades and glow-flowers, cracks spreading as it dies, a mossy rubble heap at the end. New tool `tools/sprite/boss_sheet.py`; area specs list `boss_roles` and assemble writes `boss.png` / `boss.json` beside the actor atlas (Mossglen's actor atlas drops to 2560 px tall).
- **Engine: per-role sprite sheets / frame size.** An atlas role can say `sheet: "boss"`; the actor then uses that sheet's texture, frame size and pivot (shader quad, shadow caster plane scaled to the figure, head depth, x-ray, debug rect with `sheet` / `atlas` for check-scene). check-scene compares such actors against their own sheet.
- **Everything scales with it:** enemy `scale` field (`ENEMIES.eldergolem.scale = 2.5`), hitbox r 0.42 -> 0.8, reach 1.8 -> 3.0, shockwave ring 2.6 -> 4.2 m (now ringed by six rune circles on the wind-up), slam dust spread, its rune light (range / height / power), world-bar height, a nav grid with clearance for its hitbox (`Combat.navBig`), and the **camera breathes out** (~18%, eased) while it is engaged (`ctx.framePull`).
- **Sefa's lantern** now casts a clear, bright **neon-blue cold-fire pool** on the cobbles at night: a stronger, lower blue point light (power 5 -> 11, range 3.8 -> 4.6), a dithered blue ground decal (new `coldfire_pool` effect: sky-blue heart with white flecks, flower-blue body, flickering rim; palette pixels drawn unlit, no bloom) and rising **cold-fire flicker motes** (`coldfire_motes`). Her light zone grows to 2.2 m. All of it dithers away when she packs up at dawn.
- **Options: "glow lights: 3 / 2 (phone)"** caps the pooled glow point lights (spell pools, drops, lanterns). Default 3 on desktop, 2 on touch-first devices; saved per device (`hearthmoor-glowlights`), `?glow=2|3` overrides; changing it re-opens the area in place.
- Smoke: new steps for Mossheart's scale (own sheet, 80 vs 32 px, hitbox, camera pull), the lantern pool (decal + motes + light power) and the glow-light toggle.

## 2026-10-03: Hearthmoor Stage 3, part 3.2 + 3.3: the travelling night merchant, gem sockets
- **Sefa, the travelling night merchant** sets up by the Plaza well only in the night hours (19:12 to 06:00) and packs up at dawn (a little poof each way). Deep hood, night-blue cloak and a **neon-blue cold-fire lantern** that lights the cobbles (a pooled point light) and counts as a light zone (glowlit, wraith-proof). Her **Lantern Pack** shop (same panel and controls as Odo's) sells tonics, the four socket gems and two rarer pieces (Rare + Epic, one level up, always at least one socket), fresh each night, and buys loot back at 1.2x.
- **Gem sockets:** Rare gear rolls 0-2 sockets (mostly 0-1), Epic 0-2 (mostly 1-2), **Legendary always 2**. Gems: **Golem core** (+15 HP, guard -3% dmg), **Rift shard** (+6% spells, +1% crit), Frost core (+12 stamina), Moon opal (+8% summons). Mossheart always drops a golem core; stone golems (10%), frost golems (25% frost core), wraiths and skeleton mages (rift shards) sometimes do. Loose gems lie on the ground as faceted pixel stones and go into a gem pouch (`S.gems`).
- **Socketing in the Gear tab:** a gem line lists what you own (the chosen gem is outlined; "gem ▸", T or RT picks the next one); R (keys), Y (controller) or the row's "socket" button sets it into the chosen piece's first empty socket. Set gems glow in their colour on the item icon (a dithered ring around a 2x2 inlay with a white glint; empty sockets are dark holes) and are listed in the item text (◆ / ◇). Gear-tab icons are now drawn at 3x. Gems stay set (a jeweler to clear them comes later).
- Smoke: shop steps (keys, controller, touch, tonic), night merchant (appears with light + zone at night, gem stock, socketed gear, gone at dawn), Mossheart's golem core, socketing by R and Y, gem stats once equipped.

## 2026-10-03: Hearthmoor Stage 3, part 3.1: Odo's shop in the Plaza
- **Odo the merchant** (Plaza, by the barrels and crates east of the fountain): talk to him to open his shop, a parchment / wood panel like the hero screen. **Buy**: Hearth tonics (12 gold, heal 60 HP), glow seeds (8 gold; kept for the coming glow-gardens) and three pieces of plain gear rolled when you arrive (Common / Uncommon, priced by rarity and level). **Sell**: anything in the gear bag, priced by rarity (always more than scrapping; Epic and Legendary ask "sure?" first).
- Works on all three schemes: keys (← → tabs, ↑ ↓ choose, Enter buy / sell, Esc close), controller (LB / RB tabs, d-pad, A, B) and touch (tap a tab, a row, the buy / sell button, ✕ or outside the card). The field is input-blocked while it is open.
- **Hearth tonics** show in the bag chip with a new pixel icon; drink one with **U**, a **right-stick click**, or by tapping it in the bag.
- Plaza and Bakery Lane sprite sheets no longer carry the enemy sprites (only Mossglen has enemies): Lane 3328 → 2560 px tall, Plaza 2944 → 2432 px.
- Sprites: `nightmerchant` role added (deep hood, night-blue cloak, neon-blue lantern) for part 3.2.

## 2026-10-03: Hearthmoor Stage 3, part 2: new foes, the Mossheart mini-boss, the Legendary aura
- **Frost golem** (Mossglen, east by the hedge): the stone golem re-cut in pale ice with ice spikes and white rune light. Tougher than the stone golem; its slam also **chills** you (drains 18 stamina).
- **Skeleton mage** (Mossglen, south glade): skull under a red hood, long gold-hemmed robe, a crooked staff with a cold-fire orb. Keeps its distance and fires arcane bolts (dodge, guard, or let a summon take them). Not light-shy, unlike the wraiths.
- **Mossheart, the Elder Golem** (Mossglen mini-boss, east clearing): the glowing tier-III golem look (dark ancient stone, amber crystal crown, gold runes all over, glow-flowers in the moss) and it carries its own warm rune light. 460 HP; every third slam is a telegraphed rune shockwave all round it (rune circle on the wind-up; roll through or stay out of range). A named parchment / wood boss bar shows at the top while it fights. It **always drops a Legendary** (plus extra gold) and comes back after 10 minutes. Same sprite scale as every actor (style lock); it reads as a boss through the glow, light and bar.
- **Legendary aura on the hero:** with any Legendary equipped, the same marching neon ring as a Legendary drop circles your feet (the back arc behind your legs is left out) and a warm orange-gold rune light follows you.
- Sprites: `icegolem`, `skelmage`, `eldergolem` in `tools/sprite/roles_enemies.py` (palette-remapped golem / robed skeleton variants; atlases rebuilt). XP: frost golem 55, skeleton mage 36, Mossheart 260.
- Smoke: new steps for the three foes, the chill, the mage bolt, the boss light + bar, the guaranteed Legendary and the hero aura on / off; the part-1 pathfinding step now checks the result (the foe reached the terrace by the stairs) rather than the path length. 88/88 pass. check-scene: plaza 11/11, lane 10/10 (clean re-run), mossglen 11/11 (on 0f8fb68).

## 2026-10-03: Hearthmoor Stage 3, part 1: leftovers + enemy pathfinding
- **Brighter Epic / Legendary drops:** bigger aura (Legendary: two counter-marching rings plus four orbiting sparks; Epic: one ring plus two sparks) and each Epic / Legendary drop now lights the ground around it with a pooled point light in its colour (purple / orange-gold). Still no blur or bloom.
- **Bag chip:** shows "⚔ N" (gear pieces in the bag) and "● gold" next to the errand items, refreshed on pickup, equip, scrap and faint.
- **Mode at New Game:** the hero picker has a "mode:" button (M key, Y / X on a controller, or tap) cycling Story / Adventurer / Hero with a one-line tip; the new save starts in that mode (options can still change it).
- **Enemy pathfinding:** chasing / returning enemies follow an A* path over the area's nav grid (string-pulled, re-planned twice a second) so they walk round walls, fences, terrace edges (via the stairs) and trees instead of sliding along them. Cold-fire wraiths still refuse to path into light.
- Smoke: picker mode step, bag-chip step, a pathfinding step (a skeleton below Mossglen's terrace wall routes by the stairs).

## 2026-10-03: Hearthmoor Stage 2, loot + gear (part 3) and modes, faint penalty, 24-minute day (part 5)
- **Loot:** beaten foes drop a little gold and often an item (weapon, armor or trinket) in one of five rarities: Common (white), Uncommon (green), Rare (blue), Epic (purple), Legendary (orange-gold). Every item drop stands under a crisp pixel beam in its colour with rising motes; Epic adds a faint stepped glow ring, Legendary an animated neon aura (marching pixels cycling orange / gold / white / rose). Walk over a drop to pick it up (the toast names it in its colour; gold pops as a pixel number).
- **Gear page:** a fourth hero-screen tab, Gear (G): weapon / armor / trinket slots plus a 30-item bag. Enter / A / "equip" swaps an item in, "take off" puts it back, X / "scrap" turns it into gold. Rarity-coloured names; Epic rows glow faintly, Legendary rows have the animated neon edge. Gear adds melee / spell %, HP, guard, crit, stamina and (Epic+) summon power through the same stat system as levels. Saved as `bag`, `gear`, `gold` (old saves start empty; old coins become gold).
- **Modes:** options `mode:` Story / Adventurer / Hero (`?mode=`). Story: foes hit 40% softer, you hit 15% harder, no faint penalty. Hero: foes hit 35% harder, you hit 10% softer, better loot odds.
- **Faint penalty** (Adventurer and Hero): fainting drops 10% of carried gold as a purse where you fell. It stays there (also across area changes and saves) until you walk back over it. Story mode: nothing lost.
- **24-minute day:** a whole day / night cycle now takes 24 real minutes (was 12).
- Smoke: dawn check uses midday (the run can already be at night); new loot / gear / faint / Story steps. 78/78 pass.
- Bakery Lane: one toadstool cluster moved off a spot behind the flower shop (it showed over the roof) to the open front-left corner.

## 2026-10-03: Hearthmoor Stage 2, spellbook + controller spell wheel (part 2 of 5)
- **Spellbook:** a third "Spells" tab on the hero screen (B opens it straight away; or I / the vitals chip / Start, Y on a controller, then → / RB). Four slots; Enter / A / "change" cycles a slot through every spell you know (your class spell + each charm; slots 2-4 can be empty). The cast cycle (F, Q, 1-4, LB / RB, the wheels) follows at once; saved as `slots` in the v2 save (old saves keep the default: class spell + newest three charms). A newly learned charm fills an empty slot.
- **Controller hold-for-wheel:** tap Y casts (on release); hold Y for a third of a second opens the same slow-time spell wheel as the touch ✦ button, the left stick or d-pad picks a slot, letting go of Y casts it. The field is input-blocked while the wheel is open.
- Hint line: "B spellbook", "Y cast (hold: spell wheel)".

## 2026-10-03: Hearthmoor Stage 2, glow pass (part 4 of 5)
- **Spell light pools:** every hero spell and charm leaves a short pool of light where it lands (about 1.8 s): a dithered gold ground decal (`light_pool`), twinkling glitter motes rising out of it (`glitter`) and a real point light in the spell's own colour. No bloom: all palette pixels and point lights.
- **Glowing toadstools at night:** red-and-white toadstool clusters come out between 19:12 and 06:00 in Mossglen (6), Market Square (4) and Bakery Lane (4). Their white spots twinkle, spores drift up, and each casts a soft rose pool of light; at dawn they dither away.
- **Light is a place:** standing in a light zone (a lit lamp post, stone lantern, shrine, shop window, toadstool or spell pool) makes you **glowlit**: +10% damage and 1.5x stamina regen, shown as "✦ glowlit" and a gold rim on the vitals chip. Cold-fire wraiths will not drift into light, slip out of it if a pool blooms under them, and hold their fire while you stand lit.
- **Engine:** `ctx.addGlow(x, y, z, {color, intensity, range, life, fadeIn})` gives games a small fixed pool of point lights (3, made at boot so shaders never recompile) for the strongest glows near the camera; every glow also warms nearby sprites like a lamp. Effects take `fadeIn` (dither in). `ctx.lamps` is exposed.
- New spells-atlas effects (`tools/spells/spells.py`): `light_pool`, `glitter`, `toadstools`.

## 2026-10-03: Hearthmoor Stage 2, part 1: leveling (+ review fixes)
- **Review fixes:** the toast is a brief fade below the top HUD row (never over buttons, never takes taps); the inventory shows once (bag chip; the pad rail is empty); the see-through silhouette has a solid 1-texel ink outline around the dither; the golem's side view is a hunched stone block with a brow ridge and a long hanging arm (no more bird); check-scene's effects lineup hides quest tags, so Plaza `effects_sharp` passes.
- **Leveling (`game/progress.js`):** XP from enemies (golem 45, wraith 34, skeleton 28, +50% the first time you beat each kind) and errands (120); level cap 50; six stats (Might, Arcana, Spirit, Vigor, Grit, Swiftness) with class starting values; 2 free stat points + 1 skill point per level.
  - A new game asks **"Auto level? Yes / No"** (Yes = the class spends the points along its lean, No = spend them yourself); toggle in options (`auto level: on/off`). `?autolevel=1|0` skips the ask.
  - **Hero screen** (I, tap the vitals chip, or Y / LB / RB inside the quest log on a controller): Stats tab (+ buttons) and Skills tab with tier I of each hero's three branches (E3), e.g. Stormborn Charged Hammer / Forked Bolt / Storm Sprite II, Cinderknight Life Drain, Seer Long Step.
  - Stats feed combat: melee / spell / summon / heal multipliers, max HP (Vigor), guard strength and stamina (Grit), stamina, roll distance and crits (Swiftness). Crits pop in gold.
  - Level-up: sparkle burst, bloom ring and a light-orb pool at your feet, full heal, a toast, the vitals chip flashes. The vitals chip has a level + XP bar.
  - Saves stay `hearthmoor-slot-1-v2`; the new fields (`lv`, `xp`, `stats`, `free`, `sp`, `skills`, `autoLevel`, `bestiary`) are filled with defaults when an older v2 save loads.

## 2026-10-03: Hearthmoor Stage 1: platform polish, 6 playable heroes, real-time combat core
First build stage from the builder handoff (M0 + M1 + the start of M2). Playable on Pages.
- **Platform (M0):**
  - an options card (O / ⚙ chip, also on the title) with display presets: Auto, Phone landscape (DPR cap 1.5), 720p, 1080p TV (bigger HUD, TV-safe inset), Retro 320x240 (4:3 letterbox, chunky integer pixels). Saved as `hd2d-display`, or `?display=`;
  - fullscreen button, an in-game Install button (`beforeinstallprompt`; iPhone / iPad get an "Add to Home Screen" tip), a rotate-to-landscape banner on upright phones;
  - the LT double-map is gone: LT is a held guard, RT summons, and zoom moved to the right stick;
  - a see-through silhouette: a dithered plaster-colour ghost of the player shows through buildings and trees (second quad with an inverted depth test; no blur).
- **Heroes (M1):**
  - New game opens a hero picker with the 6 starters (name, origin, mortal / demigod, blurb, animated sprite preview from the atlas, first spell and summon). It works with keys, controller and taps. The chosen class is the player;
  - the game atlases were regenerated with the hero anims plus the new enemy and summon roles;
  - phone action buttons: MAIN (attack / talk) plus guard, jump, roll, ✦ spell (tap casts, hold opens a slow-time spell wheel), summon and log, pixel icons from `art/buttons.png`, mirrored for left hands;
  - save is now `hearthmoor-slot-1-v2` (class + HP). Old `hearthmoor-slot-1-v1` saves still load: Continue asks for a hero once, then everything carries over (the v1 key is left alone).
- **Combat core (M2 start), `game/combat.js` + `game/heroes.js`:**
  - HP and stamina (parchment vitals chip), melee hitboxes on the impact frame, crisp 3x5 pixel-font damage numbers, enemy HP bars;
  - guard cuts frontal hits to a quarter; the dodge roll is a pixel-exact tumble with 0.26 s of i-frames; defeat is cozy (wake at the area start, full HP, a moment of grace, nothing lost);
  - three gloom-and-glow enemies in Mossglen: a stone golem, a skeleton swordsman and a blue cold-fire wraith (ranged), plus a second wraith at night. They wander, aggro, telegraph, leash home and respawn;
  - each starter has a first spell (Seed Bomb, Rune Slam, Rune Trap, Chain Lightning, Bloom, Ember Slash) and a first summon (mushroom golem, rune sentinel, rune wisp, storm sprite, sapling, ember imp). The 4 spell slots are the class spell + the newest 3 charms; charms do small damage too;
  - new SFX: swing, hit, hurt, guard, dodge, spell, summon, defeat, down.
- **Tools:**
  - `hd2d sprite`: new `roles_enemies.py` (golem / wraith / skeleton with idle / walk / attack / die, and 6 summons), `--roles combat`, a `die` anim;
  - `hd2d spells`: combat effects (seed bomb, earth burst, rune slam, rune trap, glyph burst, sky strike, bloom ring, ember slash / pop, cold-fire bolt, hit spark, summon poof), glow pixels only;
  - `hd2d assemble`: a `sprite_roles` spec key;
  - engine: `dodge`, `summon`, spell-slot select, `timeScale`, hit flash and roll rotation in the sprite shader, x-ray silhouette quads, display presets, press / release for every pad button, the effects QA lineup wraps to at most 3 rows.
- Small: Marla / Bram / Wren no longer call every hero a hedgewitch; the vitals chip sits under the bag whatever its height; in QA stills (`?qa` without `&combat`) enemies hold still and the night wraith doesn't spawn, so check-scene captures stay deterministic.
- Tests: the smoke test (64 steps, PASS) now covers the hero picker, Mossglen combat (hit, guard, roll i-frames, spell, summon, defeat / respawn), the new controller map, phone action buttons and the spell wheel, and the v1 → v2 save migration. `RESTORE.md` and `AGENTS.md` (game section) are updated.

## 2026-10-03: design expansion (opening hour, main quest, skill trees, difficulty, day/night, Ravenhold, music)
- New `docs/story/DESIGN_EXPANSION_2026-10-03.md` (Bill approved), also appended to `docs/story/STORY_SEEDS.md`. Seven sections:
  - E1 opening hour: Lantern Eve in Hearthmoor, tutorial beats (move, talk, errands, first fight, guard / dodge / jump, first spell and summon), six origin openings, the Rift cracking, leaving home;
  - E2 main quest: prologue, Acts 1–3, the finale, Veyra's appearances and reveal, the Saver/Breaker choice, the betrayal (Gatewright Halvard), the one side-switch window, how each of the 4 endings is reached, where the optional dungeons and superbosses fit;
  - E3 leveling: cap 50 (+10 per NG+ cycle, max 70), six stats, 3-branch skill trees for the six starters, realm school trees, summon tiers, respec;
  - E4 fainting (recoverable 10% carried gold), Story / Adventurer / Hero / Saga modes, boss retry, New Game+ carry-over, the Hall of Heroes;
  - E5 a 24-minute day, night changes, weather per realm, weekly festivals;
  - E6 Ravenhold's Forge Quarter, Old Temple (home of the Rift-gate) and Market Terraces (NPCs, shops, quests), with a consistency check of the Harbor and Undercity;
  - E7 music and sound direction, leitmotifs, per-realm instruments, the layers, day vs night, UI / SFX rules (original only).
- Not yet merged into `docs/HEARTHMOOR_BUILDER_HANDOFF.md` (at Bill's request; that happens at the end of the session). `AGENTS.md` points to the new file.

## 2026-10-03: storyboard decisions
- docs: handoff section 11 now records the storyboard decisions (combat style, Glimmerdeep, Verdant Heart nature dungeon, 10 rift types with signature bosses, factions, names, companions, mechanical pet).

## 2026-10-02: consolidated Hearthmoor builder handoff
- New `docs/HEARTHMOOR_BUILDER_HANDOFF.md`: one game design document for the Master Builder, merged from `STORY_SEEDS.md`, `AGENTS.md`, this changelog, the style lock, the tool READMEs and the code. Sections: pitch and pillars, style lock, platform/input requirements, story, world, heroes (6 + 9 = 15), bestiary, dungeons and rifts, progression and economy, current build status, open decisions, suggested milestones and repo rules, plus an appendix of resolved contradictions (later drafts win).
- No new design. Superseded drafts resolved (e.g. one static dungeon per realm instead of 1–2, Wildcaller casts, flesh/blood golems gross only in the Plaguewell).
- `AGENTS.md` links the handoff and now says the game player is the `hedgewitch` role (the code), not the traveler.

## 2026-10-02: hero action sets (cast / attack / defend / jump) and runtime action states
- `hd2d sprite`: every hero class now has **four 4-frame action anims in all four facings** (down, up, left drawn; right is the mirrored left):
  - **cast** (cols 8–11): a spell with crisp glow pixels for every class (brawlers now cast too: Runeguard light rune, Stormborn lightning, Cinderknight ember flame; Wildcaller lifts a hearth-light orb);
  - **attack** (cols 12–15): melee with the class weapon (hoe chop, axe chop + shield bash, staff sweep / thrust, hammer swing with ground sparks, Grovekeeper vine lash, greatsword ember slash);
  - **defend** (cols 16–19): raise, set, hold a / hold b (Runeguard shield up and centred with the rune lit; Wildcaller / Seer / Grovekeeper a small ward glyph; Stormborn hammer and Cinderknight greatsword held crosswise);
  - **jump** (cols 20–23): crouch, launch, airborne, land (dust pixels on landing). Frames stay feet-anchored; the runtime adds the height.
- Hero strips are now 24 columns (480 px); villager strips stay 12 columns, and an atlas is as wide as its widest role (`meta.cols`).
- Pixel identity: the idle / walk columns of all six heroes and all 24 villager roles (per-role PNGs byte-identical) match the previous build. Palette caps hold (Wildcaller still 20 colours).
- `actors.json`: new `meta.anims` entries `attack`, `defend` (with `hold: [2, 3]`) and `jump` (with `phases`), all `heroes_only`; hero roles list `anims` = idle, walk, cast, attack, defend, jump and carry `cls` / `origin` / `style` (the old `pose` key is gone).
- New CLI: `--anim-lineup PATH [--anim-facing F]` writes a 4x action sheet (rows cast / attack / defend / jump, 4 frames per hero, dark panel; the jump row previews the arc with a ground shadow).
- Screenshots: `docs/screenshots/hero_anims_4x.png` (down), `hero_anims_side_4x.png` (left), `hero_anims_up_4x.png` (up).
- Runtime (`engine/sprites.js`, `engine/main.js`):
  - `Actors.act(a, 'attack' | 'defend' | 'jump' | 'cast', {hold, dur})` and `release()`. Jump works for every role (villagers hop on idle frames); the others need the anim.
  - The jump lifts only the visible quad (`lift = 0.55 m * sin`, crouch 0.1 s, air 0.46 s, land 0.12 s); depth and the shadow caster stay on the ground. Landing kicks footstep dust.
  - Keys: **R** attack, **C** hold to guard, **Z** jump. Controller: **RS** attack, **LS** jump, **LT** short guard. No walking during attack / guard; a jump keeps moving.
  - API: `window.__hd2d.act(name, id?, opts)`, `release(name, id?)`, `actorState(id?)`, `actAdvance(sec, id?)` (QA).
  - Copied into `demos/*/engine` and `games/hearthmoor/engine` (zips rebuilt). Their atlases were not regenerated, so the game player (traveler) only has the jump.
- check-sprite: the frame count now comes from each role's `anims`, and every extra anim must differ from idle in every facing.
- Checks: check-sprite PASS (heroes alone, all 30 roles, the review-scene atlas, both demos and all 3 game areas). check-scene PASS on the review scene (hero player: jump, attack and defend), both demos and all 3 game areas (jump on non-hero players). Smoke test PASS 46/46.
- check-scene: Playwright's default timeout now follows `--timeout` (screenshots on a loaded shared box stalled past 30 s).
- check-scene: new `actions` check: with the sim held, a jump is stepped in fixed game time; the sprite must lift (≥ 0.2 m, its screen rect rises) while the shadow caster stays at the feet, then land and end. Hero players also need ≥ 2 attack frames and a held defend reaching its hold frames, ending on release.

## 2026-10-02: hero classes (Norse Nine Realms) and story seeds
- Story: Hearthmoor is now a Norse Nine Realms story. The seeds live in `docs/story/STORY_SEEDS.md` (committed for the first time). It holds:
  - the three original pitches and the chosen direction (realms linked by the Rainbow Rift);
  - the villain Veyra Ashmantle and the realm alliance map;
  - the hero origins, plus the newer **Cities** section (the Bifrost Crossing hub and one city per realm);
  - world structure, pets, and the look-and-feel priority (gloom-and-glow, neon, still no bloom);
  - **Heroes and magic**.
- `hd2d sprite`: **6 new hero classes** (30 roles total), in the new module `tools/sprite/roles_heroes.py`:
  - **Wildcaller** (Midgard farmhand): blond, rust tunic, rolled sleeves, satchel, long hoe; hearth sparks.
  - **Runeguard** (Shield-warden, paladin brawler): chestnut braids, mail and leather, axe, a round shield whose light rune glows.
  - **Seer** (Rune-reader): grey hood with a stitched back rune, rune-stone pouch, rune staff; rune glyph glow.
  - **Stormborn** (Child of thunder, brawler): bulkier `broad` layout, storm-blue cloak, silver circlet, stone war-hammer; lightning.
  - **Grovekeeper** (Child of the Vanir): moss-green hair, flower crown, leaf mantle, mushroom charms; neon-green heal.
  - **Cinderknight** (Ember-born, dark-knight brawler): bulky dark plate with a glowing ember seam, flame-tuft hair, ash cheek marks and hands, greatsword with an ember edge.
- **Hero frames:** the same 20x32 spec (4 facings × idle 4 + walk 4, hard alpha, 1 px outline, big head), plus a 4-frame action in the cast columns:
  - casters cast;
  - brawlers swing with a solid swoosh arc (dust and sprout for the hoe, an ember flame aura for the greatsword).
  - The glow is crisp emissive pixels only.
- **Hero metadata:** heroes carry `hero`, `origin` and `pose` in `actors.json`.
- **New CLI options:**
  - `--roles heroes` builds just the six;
  - `--lineup PATH` writes a labelled 4x nearest lineup.
- The 24 existing roles are pixel-identical.
- New review scene `scenes/hero-classes-plaza.json` (all six on the plaza at golden hour, frozen clock).
- Screenshots: `docs/screenshots/hero_origins_4x.png` (lineup) and `docs/screenshots/hero_origins_plaza.png` (in-scene).
- Checks: check-sprite PASS (heroes alone and all 30 roles). check-scene PASS on the review scene (all 8 checks, including sprites_sharp on 21 actor crops and the phone check).

## 2026-10-01: docs for builder handoff
- Added `AGENTS.md` (handoff guide for Cursor and Bill's bots), this `CHANGELOG.md`, and `docs/HD2D_COZY_STYLE_LOCK.md` (Bill's style law, copied into the repo).
- `README.md` and `games/hearthmoor/RESTORE.md` link all three.

## 2026-10-01: GitHub and Pages
- Published to https://github.com/unclebill-spec/hd2d-suite (public) after a secret scan (rg regexes + gitleaks on the tree, zips and history: clean).
- GitHub Pages (main, root) with a root `index.html` linking the game and both demos. `.nojekyll` added.
- `.gitignore` keeps out the `shots/` and `iterations/` QA folders (~54 MB, regenerated by the checks) and `__pycache__`. A small curated set lives in `docs/screenshots/`.
- README opens with a play-online / run-locally quick start.

## 2026-10-01: input polish (Hearthmoor and the shared runtime)
- **Controller:** new `engine/gamepad.js` (Gamepad API, standard mapping).
  - Walking: stick and d-pad walk with analog speed.
  - Buttons: A talk, B close, X cast, Y / LB / RB charm, LT / RT zoom, Start menu or quest log, Select pad.
  - Hot-plug toast. The on-screen pad hides while a controller is used and comes back on touch.
  - Games can take buttons first with `hooks.onPad`.
- **Floating stick:** it appears under the thumb in the movement zone, follows the finger and re-centres past its rim. Analog walk, the rim runs, and a left-handed mirror is available.
  - A quick tap in the zone still walks there.
  - Pinch works even when one finger lands in the zone.
- **No page scroll or zoom:**
  - blocked: iOS gesture events, double-tap zoom, pull-to-refresh / overscroll, ctrl+wheel and long-press menus;
  - `touch-action: none` on the canvas.
- **Loading gate:** every input is swallowed until the area's first frames are drawn. The `#boot` overlay sits above the title, so early taps can't queue walks or skip the title.
- **Hearthmoor title:**
  - works with a controller;
  - "press New game twice" replaces the browser `confirm()` dialog.
- Fixes:
  - The item rail no longer overlaps the chip column on mid-height screens.
  - `build.py --skip-assemble` now copies the current runtime, not a stale one.
  - The check-scene effects lineup hides particles, so fireflies can't fail it.
- **Tests:**
  - check-scene phone check: new `floating_stick`, `no_page_zoom`, `loading_gate` and `gamepad` sub-checks.
  - Smoke test: 46 steps, including a stubbed controller (`tests/gamepad_stub.js`), the floating stick, taps during loading, and keyboard + mouse working alongside a controller.

## 2026-10-01: Hearthmoor, the first game (`games/hearthmoor/`)
- Three areas:
  - Hearthmoor Plaza and Bakery Lane, joined by edge / stair exits with a fade;
  - Mossglen, a glade reached through a stone-arch moss gate with a swirling vortex. The portal art is drawn fresh in the cozy palette; the Gravewake rift refs were a style reference only.
- Three errands (Warm Bread, Moonpetal Tea, Where's Pudding?).
- Parchment / carved-wood dialogue with portraits, a quest log, a bag, quest tags, and Pudding the cat following you between areas.
- Real-time day / dusk / night, and charms as rewards (spell keys kept).
- Procedural WebAudio ambience.
- Save / load to localStorage `hearthmoor-slot-1-v1`.
- PWA (manifest, icons, offline service worker).
- Phone play: tap, pinch, Layout One pad.
- `build.py`, playable zip `games/hearthmoor.zip`, `RESTORE.md` with a do-not-regress list, and the Playwright smoke test.
- New tool `hd2d portal`: portal vortex, rune ring, moonpetal and quest-tag effects.
- New kit glade pieces: portal arch, shrine, standing stone, stone lantern, mushroom ring, fern bush.

## 2026-10-01: fixes and phone checks
- Ground decals (rune circle, portal ring) now write per-fragment ground depth, so they sit under props and actors.
- Tap-to-walk uses A* (`engine/nav.js`) over the heightfield, terraces and stairs, going around walls and props.
- Left-handed Layout One pad: `?pad=1&hand=left`, the H key or the `hand` chip, remembered per device.
- check-scene got a `phone` check (portrait 390x844 + landscape 844x390, DPR 2, touch). It found and the runtime now fixes:
  - small chips;
  - the button column running into the pad in short landscape;
  - taps dropped on slow frames.
- Rain splashes and footstep dust are more readable, still cheap, still no bloom.
- Screenshot-review fixes: the quest log ignoring `hidden`, the hint under the dialogue, the toast over the title on phones, the coin icon, faceted hills, the black fern, and occluded spawns.
- Runtime embedding for games: `boot()` / `dispose()` and hooks; NPC `follow` behaviour; lamp `color` / `fixed`; emitter `min_gate`; `?simscale`.

## 2026-09-30 / 2026-10-01: Bakery Lane, new roles, spells, particles
- Demo **Bakery Lane at Dusk** (`demos/bakery-lane`, `scenes/bakery-lane.json`): two terrace levels and stairs, the bakery and the Kettle & Key inn, a flower shop, laundry lines, a fountain, fireflies and 7 NPCs.
- **14 new sprite roles** (24 total), including magic users with 4 cast frames per facing.
- **Spells** (`hd2d spells`): 9 pixel spell effects with frame strips, presets and cast sets. F casts, Q switches, and the pad's ✦ casts on tap and switches on hold.
- **Particles:** 16 presets (fireflies, petals, snow, rain + splashes, embers, oven steam, pollen, fountain spray, butterflies, footstep dust, …) and the `?showcase=particles` grid.

## 2026-09-30: initial toolset and the Hearthmoor Plaza demo
- `bin/hd2d` CLI with the first tools:
  - `palette`: 5 biomes × 27 colours + grades;
  - `sprite`: 20x32 actors with 4 facings, idle 4 + walk 4;
  - `check-sprite`, `runtime` (three.js r160 diorama engine), `texel`, `kit`, `trees`, `particles`, `assemble`, `check-scene`.
- Demo **Hearthmoor Plaza** (`demos/hearthmoor-plaza`, `scenes/hearthmoor-plaza.json`):
  - a terraced village square, locked 3/4 camera, tilt-shift, one sun plus flickering lamps, sprite shadows;
  - day / dusk / night;
  - Layout One pad.
