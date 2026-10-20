# Niflheim (Mistmere, the Frozen Spire): build progress

RESUME HERE (Oct 19 2026, branch `realm-niflheim-2` off origin/main 581fa0f, worktree `/workspace/hd2d-nifl2`, helpers `/workspace/alf_qa/nifl2/` = copies of the nifl ones pointed at this worktree, private build dir `/workspace/alf_qa/nifl2/hmbuild`, same profile `/workspace/alf_qa/chrome-profile-nifl` under `/workspace/.hm-logs/browser-mb.lock`). **Niflheim-2 leftovers pass.** Done in code: (1) F3 slide puzzle (`NPZ`, `npzSlide`, found `fs_slide` unseals freeze-core `fs_c1`); (2) F8 Rime Bridge rune-step (`NBR`, found `fs_bridge` frees heart-ice `hi_3`; F8's east Warden moved to x 6.0 off the bridge); (3) lighter `veyra_shadow` (dark teal #2c5a60 core + ash grey #5e6e74 rim + #6a7ea8 frost edge, `nf_fx.py`; row 36 of `nf_fx.png` repainted, also copied to staging), `FX_SKIP` now empty, installed with `nifl_art.py frozenspire frozenspire2 frozen_rift`; (4) Veyra's HP bar: an engaged boss (`e.engaged`, set in `bossStart`) keeps its bar in any state, and in portrait (`max-width 640px`) `#bossbar` sits at top 190px below the HUD chips (game.css); (5) the Frostweave school (combat.js kinds `lance` / `fnova` / `veil` / `spirits` / `igolem`, Gudrun's tiered lessons `fw_i` / `fw_ii` / `fw_iii`, `?nfq=school`). Status of checks / smokes and the last pushed commit: see "Niflheim-2 log" below. DONE: all five pieces, check_scene --quick PASS on frozen_rift / frozenspire / frozenspire2, WIP pushed 6ad0f27. Wardens: skipped (optional leftover). Last step: the final smokes (niflheim, muspelheim, jotunheim) on the branch head; if interrupted, rerun only those.
Remaining (optional polish, see Leftovers): the leftovers list; Bill's answer on the Muspelheim lock (`NIFL_MUSP_LOCK`); art follow-ups.
How to rebuild: `/workspace/alf_qa/nifl/rebuild.sh <areas>` (private `/tmp/nifl_hmbuild`; wait for it to finish before committing: an interrupted rebuild leaves `areas/<a>/public/art` deleted, `git ls-files -d | xargs git checkout --` restores it), check with `/workspace/alf_qa/nifl/chk.sh <outdir> <area>` (~5 min per area, one at a time under the lock), `/workspace/alf_qa/nifl/fails.py <area> <outdir>` lists failures, `/workspace/alf_qa/nifl/clip.py <area>` = a 20 s no_bloom probe. Validate JS with `/workspace/alf_qa/nifl/jscheck.sh niflheim.js` (plain `node --check x.js` does NOT parse ES modules).
README decisions (Oct 18): (1) Veyra's four phases are separate roles in ONE sheet (`PHASE_ROLE`, game-side `swapRole`; engine `setRole` only handles the main atlas, so no engine edit); (2) Brisa is both a 1x NPC and a 3x mini-boss (`brisa_mini`): OK; (3) the lake split into two pieces for the speaker-terrace stair: OK; (4) the Colossus in the 144 px frame cap: kept (reads fine, see pics).
check_scene levers used (never a loosened check): actors moved clear of occluders / fx (nf_a, nf_shore, iceglow Gudrun + stalker, F2 wraiths now wait beyond z -25, Vigdis at [4,-15.6] right of the portrait HUD), `LAMP_CAP` (ice_lake), `EXTRA_CAP` (nf_home), `NO_LIGHT` (nf_home ice_lake lamps are glow-only: the engine gives only the first 7-8 lamps real lights and the lake pair blew the snow to 255), `FX_DROP` (nf_home's two teal lake pools), `FX_SKIP = {veyra_shadow}` (near-black decal fails gamefx_sharp on dark floors; leftover: ask art for a lighter shadow).
Pictures: `/workspace/alf_qa/nifl/pics/` (Mistmere, the Spire, the three bosses P1-P3/P4).

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
| `niflheim` | Mistmere (hub) | 24x22 | built + art, 1.34 m hall terrace + stair, arch [0,10.6], check_scene PASS |
| `nf_home` | The Quiet Shore and Ashmantle House | 16x16 | spec, 1.2 m grave ledge + stair, Hrefna actor; built + art, check_scene PASS |
| `iceglow` | Glowpool Caverns | 20x16.8 | spec, 1.2 m spire terrace + stair, spring, Spire mouth; built + art, check_scene PASS |
| `frozenspire` / `frozenspire2` | Frozen Spire F1-F5 / F6-F10 | 2 long corridors (zc 0,-14,-28,-42,-56) | generated by `areas/src/gen/gen_spire.py`, built + art, check_scene PASS |
| `frozen_rift` | The Crown of Ice (finale) | 1 arena | `gen_spire.py`, built + art (platform y 1.25 + portals pulled onto it), check_scene PASS |

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
Join-Veyra arc (greyed stub); Muspelheim-lock decision from Bill (`NIFL_MUSP_LOCK`); item icons, Ashmantle House interior, extra Hrefna spell fx beyond ice_lance / mist_veil, per-room Spire layouts (generated corridors stand in); Vigdis / folk reuse stock looks; locked Wardens do not shoot from walls.

## Niflheim-2 log (Oct 19 2026)
- Frostweave decisions: the school draws the Niflheim pack's own rows (ice_lance, frost_nova, mist_veil, spirit_swarm) in the six Niflheim areas and the stock spells atlas elsewhere (coldfire_bolt, frost_puff, coldfire_motes, summon_poof), so NO new rows went into the other 31 area atlases (no repo-wide atlas rewrite, no repo-wide check_scene). Frost Spirits are two fx companions (no sprite: the summon slot holds one actor). The Ice Golem shares `doGolem` (`kind: 'igolem'`, own cooldown, the realm's `ice_golem` role first). Leftover: dedicated Frostweave gamefx rows in every area atlas (Caldera-style) if Art wants them.
- Leftovers still open: wall-shooting Wardens for `rivals.niflheim === 'locked'` (optional, not done); Join-Veyra arc; the Muspelheim-lock answer; item icons; Ashmantle House interior; extra Hrefna fx; per-room Spire layouts; folk looks; niflheim / nf_home / iceglow atlases still lack the (unused there) veyra_shadow row until their next `nifl_art.py` run.
