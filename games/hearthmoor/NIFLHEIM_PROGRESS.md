# Niflheim (Mistmere, the Frozen Spire): build progress

RESUME HERE (Oct 18 2026, chunk 1 done, branch `realm-niflheim`, worktree /workspace/hd2d-niflheim, from origin/main a9802be): **ART PACK NOT READY** (`/workspace/hearthmoor-staging/art/niflheim/` does not exist; READY.txt = go). This is a DORMANT SKELETON: `NIFL_BUILT = []` in `game/niflheim.js`, so `AREAS_NIFL` is empty and the Bifrost Niflheim arch stays sealed; build.py adds the Niflheim areas only with READY.txt (or `HM_NIFL_SKELETON=1`, private builds only: never commit that output). Standalone `smoke_niflheim.py` PASS 47/47 (`/workspace/alf_qa/nifl/sm5/`), `smoke_muspelheim.py` re-run as the shared-file sanity (game.js hooks).
NEXT when READY.txt exists:
1. Read the art README; fix the GUESSED tables at the top of `tools/hearthmoor/nifl_art.py` (`TOWNS`, `FOLK`, `FOES`, `SHEETS`, `EXTRA`, `LAYOUT_AREA`, `LAMP_CAP`, `NO_TILE`, `SPEC_TERRAIN`, neon scope only if the README names it). Flip `NIFL_ROLES_READY = true` in `niflheim.js` (every foe / boss wears the stock `wraith` role until then) and re-point `smoke_niflheim.py`'s boss steps (they spawn in `plaza` with `qaBoss(..., 'wraith')`).
2. Fill `NIFL_BUILT` area by area (`niflheim`, `nf_home`, `iceglow` specs exist and assemble; `frozenspire`, `frozenspire2`, `frozen_rift` specs still to write), `/workspace/alf_qa/nifl/rebuild.sh <areas>`, then `/workspace/alf_qa/nifl/chk.sh <outdir> <area>` one area at a time (`check_scene --quick`, lowres), fix, repeat. Spot coordinates in `niflheim.js` (`HI`, `BOSS_AT`, `PORTALS`, `RARE_AREAS.iceglow`, `SPAWNS.iceglow`, `SPRINGS`, `NF_ARCH`) are PROVISIONAL.
3. Wire the Spire (10 rooms across `frozenspire` / `frozenspire2`, finale `frozen_rift`), the three runes, Brisa's trial, authored spawns, rares, glow tables.
4. Test policy (Bill, Oct 17): faster check for new realms = `smoke_niflheim` + only the groups the change touches (shared file edited -> that file's group) + `check_scene --quick` on changed areas. No full ~1.5 h sharded smoke unless engine code is edited broadly (then say so in the report).

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
