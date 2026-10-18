# Niflheim (Mistmere, the Frozen Spire): build progress

RESUME HERE (Oct 18 2026 ~2:20 PM ET, chunk 2 WIP, branch `realm-niflheim`): ART PACK INSTALLED (`art/niflheim/`, READY.txt present), `NIFL_ROLES_READY` on, all six areas built (`niflheim nf_home iceglow frozenspire frozenspire2 frozen_rift`; Spire specs from `areas/src/gen/gen_spire.py`), Spire/Crown runtime in `game/niflheim.js` (spire1/spire2/rift/spireTick, per-phase role swap `swapRole`, Veyra clones/breath/portal fx, Hrefna calls), `smoke_niflheim.py` rewritten for real areas/roles (NOT yet re-run).
STATE of `check_scene --quick` (results under `/workspace/alf_qa/nifl/c4/`): niflheim failed only phone-landscape sprites_sharp (nf_a moved to [-1.2,3.8]); nf_home failed sprites_sharp / no_bloom (night clip 2.4 %) / colours: nf_shore moved to [-2.4,3.2], `LAMP_CAP["ice_lake"]=3.4`, `EXTRA_CAP={"nf_home":5.0}`; iceglow / frozenspire / frozenspire2 / frozen_rift: read c4 logs, fix, re-run ONE AREA AT A TIME (`/workspace/alf_qa/nifl/chk.sh <outdir> <area>`; ~5 min each). After rebuild (`rebuild.sh <areas>`) re-check niflheim and nf_home first.
NEXT: (1) finish check_scene on all six (fix by moving actors/props/lights, `LAMP_CAP`, `EXTRA_CAP`, `FX_SKIP`; never loosen). (2) screenshots of tall bosses (Colossus F5, Kael F9, Veyra Crown) and Mistmere / Spire pictures. (3) run `run_sm.sh` (smoke_niflheim) + `run_sm_m.sh` (muspelheim); fix bifrost-arch step (the arch is now live). (4) update this doc (4 README decisions below), CHANGELOG, report. Validate JS with `/workspace/alf_qa/nifl/jscheck.sh niflheim.js` (plain `node --check x.js` does NOT parse modules).
README decisions (Oct 18): (1) Veyra phases = separate roles in one sheet (`PHASE_ROLE`, game-side `swapRole`; engine `setRole` only does the main atlas, no engine edit); (2) Brisa 1x NPC and 3x mini-boss (`brisa_mini`): OK; (3) lake split into two pieces for the speaker terrace stair: OK; (4) Colossus in the 144 px frame cap: kept.
Known skips: `FX_SKIP = {veyra_shadow}` (near-black decal fails gamefx_sharp on dark floors; the tell uses breath_fog; leftover: ask art for a lighter shadow).


Helper scripts: `/workspace/alf_qa/nifl/` (`asm.sh` skeleton-assemble into the private dir only, `rebuild.sh`, `chk.sh`, `run_sm.sh`, `run_sm_m.sh`). Private build dir `/tmp/nifl_hmbuild`; browser profile `/workspace/alf_qa/chrome-profile-nifl` under `/workspace/.hm-logs/browser-mb.lock`.

Source of truth: `/workspace/hearthmoor-staging/story/niflheim.md`. Template: `docs/REALM_TEMPLATE.md`. Models: `MUSPELHEIM_PROGRESS.md`, `JOTUNHEIM_PROGRESS.md`.

## Decisions (Cozy Builder, Oct 18 2026, plus scaffolding calls)
1. **Keep the Muspelheim lock** (befriending Muspelheim makes Niflheim conquer-only; Bill has not answered). It is ONE constant: `NIFL_MUSP_LOCK` at the top of `game/niflheim.js` (`true` = locked; `false` = Hrefna's Thaw / Eira's Lanterns / Gudrun's befriend choice open regardless). `lockedBy()` is the single reader.
2. **No corrupted Cinderhold shrine**: the mirror sigil and the frost wedges are enough.
3. Weather kinds are `frost_mist` / `still_frost` (the shared kind `mist` is Mossglen's).
4. The Frozen Spire is two areas (`frozenspire`, `frozenspire2`) plus the finale `frozen_rift` (like `clockdeep` / `caldera`); there is no `nf_hall`.
5. The "Join Veyra" option in P4 / Gudrun's choice is a greyed stub (story marks it as a later arc).
6. `bifrost.js` is NOT edited: its `Crossing.pages` destructures a `['flag', ...]` key into FACTIONS and would crash, so `niflheim.js` wraps `Crossing.prototype.pages` (frost letter once live and >= 3 realms resolved) and drives the arch itself (`NfGate`).
7. Frostweave school (story 9.x) deferred: needs `combat.js` kinds (shared file, full test rules); items `colossus_core` / `kael_fang` are in as socket items only.
8. Stand-ins: until the pack lands every Niflheim foe / boss draws as the stock `wraith` role (`NIFL_ROLES_READY`).

## Areas (story 2.1)
| Area | Name | Size | State |
|---|---|---|---|
| `niflheim` | Mistmere (hub) | 24x22 | spec + generator (`areas/src/gen/gen_niflheim.py`), 1.2 m hall terrace + stair, arch at [0,10.6], exits to nf_home / iceglow; not built (skeleton) |
| `nf_home` | The Quiet Shore and Ashmantle House | 16x16 | spec, 1.2 m grave ledge + stair, Hrefna actor; not built |
| `iceglow` | Glowpool Caverns | 20x16.8 | spec, 1.2 m spire terrace + stair, spring; not built |
| `frozenspire` / `frozenspire2` | Frozen Spire (10 rooms) | | not written (art/layout owed) |
| `frozen_rift` | The Crown of Ice (finale) | 1 room | not written |

## Quests (story 3) — all 10 in `QUESTS` (`niflheim.js`)
nf_gate The Frost Invitation (story) | nf_lanterns The Lanterns of Mistmere (befriend) | nf_cold The Cold Mark (befriend) | nf_hrefna Hrefna's Thaw (befriend, companion) | nf_eira Eira's Lanterns (befriend, redemption path) | nf_take The Rime Toll (conquer) | frozenspire The Frozen Spire (all paths, stages incl. fs_boss) | nf_staff The Coldflame Lantern (ripple) | nf_elk The Elk of the Fen (ripple, mount) | frostvigil The Frost Vigil (bounty). Merit keys: nf_gate 60, rimetoll 60, spire_c 120, nf_lanterns 40, nf_cold 60, nf_rival 20, nf_hrefna 80, nf_eira 80, frozenspire 120, frostvigil 40. `?nfq=open|revealed|befriend|lanterns|cold|thaw|eira|conquer|done` QA presets.

## Content list
In code (tested, smoke 47/47): gate flow + Frost Invitation, reveal + Gudrun's choice (4-ally cap label, Muspelheim lock label, Join stub), Lanterns, Cold Mark (three clues, Rune-reader free read), Hrefna's Thaw (Ember-born vouch), Eira's Lanterns / `redeemable()`, Rime Toll, merit routing (conquer pays 'gate'), Hrefna in COMP (one active companion) + FOLLOW_KIT, bosses with `framed:true` (Colossus 6x phases .6/.25, Kael 5.5x .6/.25, Veyra 5x -> 6x, 4 phases, P2 portals + thaw runes, P3 red-ring beam telegraph, P4 choice, two endings), rares (mistalpha, spiritprime), weather, items, shop, Coldflame staff.
Owed by builds / art: area specs for the Spire, glow-pool / rune-hall props, Brisa trial arena, authored spawns / rare spots / springs, heart-ice spots, Frost Vigil festival ground, sprite sheets (frost-kin folk, foes, Hrefna, Colossus, Kael, Veyra with P3 frame), gamefx `nf_fx` rows, item icons, Frostweave school.

## Art needs (from the story doc 2.2, 7, 8, 9)
Mistmere kit (frozen lake, lantern posts, ice bridges, Bifrost frost arch, Vigil ground), Ashmantle House + Eira's grave, glowpool caverns + rune hall, Spire rooms (ice halls, three rune-locks, the Crown of Ice), frost-kin folk, mist stalker / frost spirit / ice golem / frost wraith / ice warden, Brisa 3x, Colossus 6x, Kael 5.5x, Veyra 5x with a 6x P3 frame, Hrefna companion sheet, red-ring beam + frost ring + thaw effects. Neon: none requested (`NIFL_NEON_ALLOW` is empty and scoped).

## Test plan
`smoke_niflheim.py` (T.until, no fixed sleeps; standalone via `run_sm.sh`), runs inside `smoke.py` after the Muspelheim block. `check_scene --quick` per built area, one at a time. Shared files touched (hooks only): game.js, build.py, smoke.py, check_sprite.py (empty `NIFL_NEON_ALLOW`).

## Rules carried over (never break)
Private build dir `HM_BUILD_TMP=/tmp/nifl_hmbuild` (never `/tmp/hearthmoor_build`); browser only with `/workspace/alf_qa/chrome-profile-nifl` under the browser lock; never loosen a check or allow-list; every area real height (>= 1 m + stair) and passing lighting; actors fully on or fully off screen (tall bosses: see placement lessons in MUSPELHEIM / JOTUNHEIM progress); mind the `install_pets` fx-row pitfall (AGENTS.md); engine edits only in `tools/runtime/web/engine/main.js`; `tests/check_palette.py` untouched; secret scan before every push; push only `realm-niflheim`, never main, no force; leave other worktrees, `hearthmoor-leftovers-wip` and `/workspace/hd2d-cauldron` alone; shared gamefx rows (Stonefrost II / III, then the Caldera school) are re-applied by `nifl_art.py` after its own rows.

## Leftovers
Frostweave school; Hrefna neon scope (only if the README names it); real spot coordinates; Join-Veyra arc; Muspelheim-lock decision from Bill.
