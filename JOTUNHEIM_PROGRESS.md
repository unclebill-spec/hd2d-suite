# Jotunheim (Stonehollow, the Rime Caves, the Titan's Barrow): build progress

RESUME HERE (Oct 16 2026, 08:05, branch `realm-jotunheim`, worktree /workspace/hd2d-jotunheim): **Five areas are BUILT: Stonehollow (`jotunheim`), the Hall (`jt_hall`), the Rime Caves (`rimecaves`), the Barrow part 1 (`barrow`, B1-B4) and part 2 (`barrow2`, B5-B9, Hrimgard 7x). `check_scene --quick` is 11/11 on all five (barrow2 `/workspace/alf_qa/jot/chk31.log`, barrow `chk32.log`; pictures `/workspace/alf_qa/jot/check_<area>/`). `smoke_jotunheim.py` 76/76 (new steps for The Barred Gate, the Toll of Stones, Stonefrost lessons, barrow2: all `T.until` / engine-frame waits). Post-merge (main 01c86b7) full sharded smoke PASS at c68de1f: A 114, B 222 (with the Alfheim / Svartalfheim / Jotunheim realm smokes), C 29, D+G+M 39, F+H+K 39, I+J+L+E 24 (logs `/workspace/alf_qa/jot/sm2/`). Build pitfall: `build.py` rewrites `engine/main.js` from a stale copy (drops main's `pzObjs` puzzle lines); `git checkout games/hearthmoor/engine/main.js` after every build.**
Chunk 1 (done): `jot_art.py` real installer; `areas/src/jotunheim.json`; `game/jotunheim.js` (realm tables, Bifrost ice arch sealed -> portal via `?jtq=` / `jt_gate_open` / alliance, Grimsa's stall, NPC talk, *The Stone Welcome* + Welcome Ring, look-spots); scoped `pet_flurry` in `check_sprite.py`; `tests/smoke_jotunheim.py`.
Chunk 2 (done): main merged (9795278); `areas/src/jt_hall.json` (1.2 m dais + stair, cold-fire hearth pit, tables, trapdoor, and the ice cellar as the walled pocket east of the hall: one scene, the trapdoor / cellar stair move the player, spawn `cellar`); Jarl Thyra (choice, the fire, *The Hollow Heart*, contract terms), Kolbrun, Solvi, guards; clues `jh_heart` (tap the Heart), `jh_rime` (needs Solvi's rune-light: talk to her first), `jh_trail` (cellar stair); the `sv_decoy` quick route (boot mould -> done, `jt_peace`); conquer (evidence still counts, Solvi's "you know it's hollow"); contract (terms from the Jarl, Skuli guides, Rime Wages 1 -> 2). QA presets `?jtq=open|befriend|fire|heart|decoy|conquer|contract|done`. Smoke: `smoke_jotunheim.py` 31 steps.
Chunk 3 (done): `rimecaves` (spec `areas/src/rimecaves.json`: 1.2 m Barrow step with a stair at x 0, walled cave, cold braziers, five glow pools, ice-wall waterfall; `jot_art.py` PLACE list; `game/jotunheim.js`: `caves()` with the Barrow-door look-spot (3 rune locks, reads alliance / key / goat-path), the frozen waterfall -> `rc_spring` when a spell is cast within 2.6 m, Solvi + Skuli talk, the foes `frost_troll / ice_golem / avalanche_golem / rime_berserker` (ENEMIES / XP / SPAWNS.rimecaves, all north of the first view); Stonehollow gets a second exit to the caves (rect [10.8,0.6,11.9,2.6]) and `from_caves` [9.4,1.6]; the cave look-spot is hidden now). Smoke: 6 new steps.
Full sharded smoke: `--jobs 3` does NOT work in a fresh worktree (shards 2 and 3 need `tests/fixtures/smoke_cp2/3.json`, which only a serial run of A -> B -> C writes; the fixtures dir is gitignored). Correct order: `smoke.py --segments A` (cp1), then `--segments B` (cp2; B also runs the Alfheim, Svartalfheim and Jotunheim realm smokes at its end), then `--segments C` (cp3), then D F G H I J K L M / E in parallel processes under one flock. Under a box load of 14-17 segment B alone took more than 25 min. Run in `/workspace/alf_qa/jot/sm/` (`B.log`, `C.log`, `p1..p3.log`, `done` when finished); A passed (no FAIL). Lessons: Jotunheim fixes that worked: `LAMP_CAP` (dims decor lamp reach), actors must be off every brazier / ice wall column and >= 3.5 m apart from other giants (phone portrait shows the whole north strip), foes of the day set stand at x 0 or |x| >= 7 away from the HUD buttons, night-only foes may stand anywhere. **RESULT (Oct 16, 06:33): PASS.** A (first `--jobs 3` run, its shard 1: no FAIL, wrote cp1), B 183/183 (includes the Alfheim, Svartalfheim and Jotunheim 37/37 realm smokes), C (own steps pass, no FAIL; its realm-smoke tail was stopped to save time since B had run it), D+G+M 39/39, F+H+K 39/39, I+J+L+E 24/24. The last three ran through `/workspace/alf_qa/jot/sm/runseg.py`, a runner that stubs the three realm smokes out of the segment tail (they had already passed in B); logs in `/workspace/alf_qa/jot/sm/`.
**Next, in order:** (1) run the full sharded smoke once more after this chunk (runbook above; `smoke_jotunheim` is the only part that changed); (2) the rest of the story: Stonefrost tiers II / III (Stone Skin, Cold Fire, Stone Golem need new spell kinds and spell-atlas art; tier I Boulder Toss / Frost Rune are in, taught by the Hall's Solvi after `barrow` = 3), Hrimgard's P2 floor slide / P3 relit braziers and Ormgar's 50% frenzy (engine has only `wave`, `minion`, `phases` today), the Rune Bridge puzzle (no lit / unlit tile logic yet), the Waystone for `barrow2` (spec has the pos; fast-travel hookup not checked), rares via the BASES hook, the Rimebreaker, goat, weather, Ulfar companion, the Jarl's `jt_dark` consequences for conquer (Dark Stonehollow, 9.7). (3) Visual polish: cairn props for the Toll of Stones (the cairns are invisible spots in the Rime Caves, positions `CAIRNS` in `jotunheim.js`), a visible troll-through-the-arch fx. Design notes: the Barred Gate troll spawns on the Stonehollow side (Bifrost has no Jotunheim foe sheets): the horn pulls you through, `update()` spawns it (`jg_sounded`); Kolbrun's turn-in is back at Bifrost. Barrow foes: day foes at x 0 / |x| >= 7, >= 3.5 m apart, off every brazier column (see placement lessons); `barrow` and `barrow2` have no actors.
Placement lessons (check_scene): giants are 3x and the camera shows only z > about -1 from the start spawn, so an actor must be fully on screen or fully off it (a sliver fails sprites_sharp); keep props >= 1.8 m south of an actor and other giants out of their x-range (+-1.3 m).
Rules carried over from Svartalfheim: private build folder, Bill's browser lock (`/workspace/.hm-logs/browser-mb.lock`,
`HD2D_USER_DATA_DIR=/workspace/alf_qa/chrome-profile-cs`), never loosen a check, never push to main, secret-scan before every push, keep tall
props off the characters and the spawn, one build or check at a time, stop servers by port.
Pitfall (AGENTS.md): re-running only `install_pets` on plaza / lane crops their orb-lantern fx rows; rebuild those two with
`build.py --areas plaza,lane --no-zip`, then `alf_art.py` and `svart_art.py`.

Source of truth: `/workspace/hearthmoor-staging/story/jotunheim.md` (594 lines). Template: `docs/REALM_TEMPLATE.md`. Section numbers below are the story doc's.

## Areas the story calls for (section 2.1)
| id | name | size | status |
|---|---|---|---|
| `jotunheim` | Stonehollow (town hub) | 24 x 22 m | not built (holds for art). Welcome Ring `[0,4]`, ice arch to Bifrost `[0,10.6]` (spawn `from_bifrost` `[0,9.2,"up"]`), hall door `[0,-9.6]`, goat pens `[-8.5,-2]`, frozen lake `[8,-3]`, trader stall `[-6,5.5]`, cave stair `[10,-9]`, snow path `[-11,-8]`, hot spring `jt_spring` `[-10.5,-9.5]` |
| `jt_hall` | Hall of Hearthstones | 14 x 18 m | not built. High seat `[0,-6.5]`, cold-fire hearth `[0,-2]`, ice-cellar trapdoor `[5,-7]` (the false Heart; clues `jh_heart`, `jh_rime`, `jh_trail`) |
| `rimecaves` | The Rime Caves | 20 x 16 m | BUILT (chunk 3). Solvi's rune-hall `[-6,-4]`, Barrow mouth `[0,-7.5]` (3 rune locks), 5 glow pools, `rc_spring` behind a frozen waterfall (fire spell melts it), rares by the far pool |
| `barrow` | The Titan's Barrow, part 1 (B1-B4) | 4 rooms | BUILT (chunk 4). Door, Hall of Shields, Glow Pools, Avalanche Run. Decision 8: two areas like the Clockwork Deep |
| `barrow2` | The Titan's Barrow, part 2 (B5-B9) | 5 rooms | BUILT (chunk 5). Frozen Echo, Berserker Hall, Rune Bridge, Waystone Crypt, the Throne Barrow (Hrimgard's arena) |

Also needed at Bifrost (no new area): the sealed arch `fx: "gate_jotunheim"` at `[5.0,-11.9]` moves from `game.sealed` to `game.portals`
(rect `[4.25,-12.3,5.75,-11.45]`, `to: "jotunheim"`, spawn `from_bifrost`), `GATES.jotunheim` key `['embassy', 1]` (matches the story).
Weather: new `blizzard` (frost slow, -1% speed per 5 s outdoors, max -30%) and `aurora` kinds in `weather.js`; Jotunheim day 70% snow / 15% blizzard / 15% clear.
Realm tables: `REALM.jotunheim / jt_hall / rimecaves / barrow = "embassy"` (conquer, contract: `gate`), `JOTUN_AREAS` in `factions.realm()`.

## Quests (story 3; 3 = done)
| key | title | giver | kind / path | key flags |
|---|---|---|---|---|
| `jt_gate` | The Barred Gate | Envoy Kolbrun Hailstride | story, all paths. Offer: Embassy rank >= 1. Halvard's horn, a 2x frost troll comes through the arch | `jg_asked`, `jg_horn`, `jg_troll`, `jt_gate_open` |
| `jt_welcome` | The Stone Welcome | Jarl Thyra Stonebrow | story, befriend. Timing beat (hold E/A, release in the blue band), 3 lifts (2 for Runeguard); skipped if `realm_mood.jotunheim >= 1`; QA `?lift=auto` | `jw_lifts`, `jt_trusted` |
| `jt_heart` | The Hollow Heart | Jarl Thyra | story, befriend. The false-Heart frame-up (clues below) | `jh_heart`, `jh_rime`, `jh_trail`, `jt_cleared`, `jt_peace`, `S.evidence.jotunheim` |
| `jt_ulfar` | Ulfar's Walk | Ulfar Mossback | story, befriend. Goat Turnip on the lake ice, his song, the mitten (= Flurry's bed) | `S.found.uw_goat/uw_song/uw_mitten`, `companions.ulfar`, `S.pets.flurry`, `S.unlocks.frostbrute` |
| `jt_take` | The Toll of Stones | Kolbrun | story, conquer. 3 watch-cairns (2 Rime Berserkers each), Rime-Captain Hjordis Icejaw yields at 25% | `S.found.tt_c1..3`, `tt_captain`, item `barrow_key` |
| `jt_hire` | Rime Wages | Halvard | story, contract (needs `rivals.jotunheim === "locked"`). Skuli guides, no fighting | `jw_terms`, `jw_skuli`, `jt_contract` |
| `barrow` | The Titan's Barrow | Rimewife Solvi | story, all paths. 3 braziers, Hrimgard, the turn-in | `S.found.tb_b1..3`, `tb_boss`, `tb_slept` / `tb_crown`, `jt_resolved`, `jt_veyra` |
| `jt_axe` | The Rimebreaker | Solvi | ripple, befriend, after `barrow` = 3. 3 heart-ice (`hi_1..3`) | item `rimebreaker` |
| `jt_goat` | The Goat Who Chose You | Brynja Hornwise | ripple, befriend. 3 oat-cakes over 3 days, one lap; goat mount Clatter | `gt_cakes`, `gt_lastDay`, `S.mounts.goat` |
| `stonetoss` | The Stone-Toss Games | Jarl Thyra | bounty, repeatable, befriend; festival every 7th day (`S.day % 7 === 5`) on the lake: stone toss, goat race, arm-wrestle with Ulfar | `S.stonetoss {toss, race, wrestle}` |

New `MERIT` keys (3.12): `jt_gate 60, tollstones 60, jt_contract 60, barrow_c 120` (Guild gate); `jt_welcome 40, jt_heart 60, jt_rival 20, jt_ulfar 80, barrow 120, stonetoss 40` (Realm Favor). `markerFor` additions in story section 10.

### The Jarl's choice (5.2)
`TALK.jarl`: befriend (locked with `lockedLabel` if `rivals.jotunheim === "locked"`; `lockRival(S,"asgard")` + `moodUp(S,"vanaheim")`), conquer (`moodUp(S,"asgard")`), contract (shown only when locked). Stormborn pay one extra step (Ulfar vouches), Runeguard need 2 lifts.

## Shops, NPCs, items
- **Shop:** Grimsa (`jt_trader`, stall `[-6,5.5]`): fur cloak (frost resist +20%), Moonpetal tea (clears frost slow), cold-fire lamp (light radius +2). Conquer path (Dark Stonehollow, `jt_dark`): +25% prices.
- **NPCs (5):** `envoy_jt` Kolbrun (3x), `jarl` Thyra (3.2x), `ulfar` Ulfar Mossback (3x, companion 2.4x in combat), `rimewife` Solvi (2.8x, teaches Stonefrost), `goatherd` Skuli (2x), `goatwife` Brynja (3x), `jt_trader` Grimsa (3x), `rimecaptain` Hjordis Icejaw (3x, conquer). The innkeeper stays Bram.
- **Items (11):** `kolbrun_horn`, `false_heart` (look-only), `barrow_key`, `heart_ice` x3, `oat_cake`, `moonpetal_tea`, `rimebreaker` (legendary frost axe, heavy hits freeze 1.5 s, charged hit throws an ice wave), `hrimgard_crown`, cosmetics `fur_mantle` / `coldfire_lantern` / `goat_helm`.
- **School:** Stonefrost (Solvi): Boulder Toss, Frost Rune (I); Stone Skin, Cold Fire (II); Stone Golem (III).
- **Pet:** Flurry the snow hare (speed aura 1.08, frost-slow immune, reveals hidden snow paths). **Mount:** goat. **Unlock:** Frostbrute hero.
- **Companion:** Ulfar (`boulder_toss`, `shield_hug` blocks 50% for 4 s, cd 20 s; frost resist 0.5). One active companion at a time (Svartalfheim section 15 decision): extend `svartalfheim_companions.js` (`COMP`, `swap`) and `svartalfheim_follow.js` (it already follows Dagna and Tobble; Ulfar needs a 2.4x sheet).

## Bosses and rares (story 7, 8)
| id | what | scale | notes |
|---|---|---|---|
| `hrimgard` | **Hrimgard the Unthawed** (boss, B9) | 7x (decision 4, Cozy Builder's ruling) | only plate in the arc; P1 ground slam rings + cold-fire breath cone; P2 (60%) 2 ice golems + the floor freezes (slide); P3 (25%) the snuffed braziers relight one by one, snuff them mid-fight to stop his heal. `plate: true, element: "ice"`, HP x10 base |
| `ormgar` | Rime Berserker Chief Ormgar (mini-boss, B6) | 3x | two ice axes, frenzy at 50%; `hi_2` behind his seat |
| `frost_troll` (gate foe) | The Barred Gate troll | 2x | throws ice chunks |
| `rimecaptain` | Hjordis Icejaw (conquer) | 3x | shield wall, yields at 25% |
| `frostmother` (rare) | frost troll matriarch | 2.5x | belted fur tunic, ice club, calls troll whelps. Traits: frozen, thick-hide |
| `avalanche` (rare) | avalanche golem | 3x | a rolling boulder that unfolds. Traits: stone-skin, quake |
| regulars | `frost_troll` 1.6x, `ice_golem` 1.5x, `avalanche_golem` 1.8x, `rime_berserker` (elite) 1.8x | | `ENEMIES` + `XP` + `RARE_AREAS` (rimecaves, the Barrow) |
Barrow rooms B1-B9 (7): Door (2 trolls) / Hall of Shields (brazier 1) / Glow Pools (slide puzzle, `hi_1`) / Avalanche Run (rolling snowballs, brazier 2) / Frozen Echo (Veyra beat) / Berserker Hall (Ormgar) / Rune Bridge (lit runes only, brazier 3, `hi_3`) / Waystone Crypt (waystone, `tb_spring`) / Throne Barrow. Contract: Skuli skips B4. Conquer: B1 and B6 add 2 berserkers each.

## The Giant Footprints clue scenes (a Svartalfheim quest that needs this realm)
*Giant Footprints* (`sv_name`, Svartalfheim story 3.3, 4.1-4.3) is **already built and merged** (`svartalfheim_story.js`): `sn_prints` (the vault look point), `sn_lock` (Sereth's lens), `sn_mould` (the slag pits, `boot_mould`), the lens turn-in, then stage 3 sets `sv_cleared`, `sv_decoy = 1` and `S.evidence.svartalfheim = "boot_mould"`. It says the northbound trail to Stonehollow was a decoy. **Jotunheim owes the other half** (story 4):
1. **`jh_heart`** (tap the false Heart in the ice cellar `[5,-7]` in `jt_hall`): it rings hollow; the real Anvil-Heart beats like a drum.
2. **`jh_rime`** (Solvi's rune-light): the rime is blue-black like the Cold Altar tongs and the boot mould; giant frost is white.
3. **`jh_trail`** (the cellar stair): frost prints go in, none come out; someone small took off big boots.
4. **The quick route** (`flags.sv_decoy`): step 1 of *The Hollow Heart* is just "show the Jarl the boot mould" (`"The dwarves sent a friend? Then the world is not all spears."`). Sets `jt_peace = 1` (the war band turns back; Anvildeep's ambient lines change, and the Thane's "a cart of ale. Two carts." line).
5. Conquer: you ignore the clues; Solvi says `"You know it's hollow. Everyone can hear it."` Contract: Skuli mentions it, no quest; `S.evidence.jotunheim` still counts if you look.
Also from the Svartalfheim list: the **Frozen Echo** (B5, Veyra's `veyra_frost` voice, same reveal-queue timing as `alfheim.md` 6.10) and Veyra between realms (6.5, next area load after `jt_resolved`).

## Decisions on the story's section 13 open questions (Bill, Oct 16 2026: final, built in)
Same spirit as the Svartalfheim decisions: befriend vs conquer is the player's choice, rival realm locks mirror both ways, one active companion at a time.
1. **Asgard mirror: yes.** `lockRival(S,"asgard")` / `moodUp(S,"asgard")` are mirrored: Asgard's doc checks `rivals.asgard` / `realm_mood.asgard` the same way and gets the same three paths (befriend, conquer, contract for locked players).
2. **Vanaheim swing:** `moodUp(S,"vanaheim")` means **more Realm Favor and one skipped step** in Vanaheim. **No discounts.** (Exact numbers and which step get picked when Vanaheim's hooks are written; keep it to those two things.)
3. **Contract path: keep** *Rime Wages* (`jt_hire`).
4. **Hrimgard stays 7x**, as the story says (`ENEMIES.hrimgard.scale = 7`). Cozy Builder ruled this on Oct 16, overriding the earlier 6x-to-match-Gorrak call; the Big sheets list already has him at 7x.
5. **Ulfar is 2.4x in combat** (3x in town), done with the engine's `combat_scale` 2.4 on his one sheet: no second combat sheet.
6. **One active companion at a time**: Ulfar and Dagna don't both follow. They swap at the Bifrost Gatekeepers' Guild desk or at any inn (already built for Lumi / Dagna / Tobble in `svartalfheim_companions.js`: add `ulfar` to `COMP`).
7. **Halvard does not lose Kolbrun's horn.** Only the copper key is lost (to avoid too many lost keys). *The Barred Gate*: Halvard hands the horn over straight (no "wrong drawer" step), stage 1 keeps `jg_asked` / `jg_troll`; `jg_horn` is set when he gives it.
8. **The Barrow is two areas, `barrow` and `barrow2`**, like the Clockwork Deep (`barrow` B1-B4 with the Avalanche Run, `barrow2` B5-B9: Frozen Echo, Berserker Hall, Rune Bridge, Waystone Crypt, Throne Barrow with Hrimgard). The area list is now 5 areas.
9. **The goat mount is deferred**: it goes on the leftovers list. `jt_goat` (*The Goat Who Chose You*) can still be built as a ripple quest whose reward waits for mounts; Clatter stays a pen goat for now.

## Leftovers (deferred on purpose)
- The goat mount (`S.mounts.goat`, climbing snow slopes): mounts are not built in the engine. Decision 9.
- Everything in the RESUME HERE list that is blocked on art (READY.txt).
- **For Hearthmoor Art:** Stonefrost tiers II / III (Stone Skin, Cold Fire, Stone Golem). Tier I (Boulder Toss, Frost Rune) is in; II / III need new spell kinds (a buff, a ground-fire patch, a summon) plus spell-atlas art. Also nice to have: a real waystone glb for barrow2 (a `rune_standing_stone` marks it now) and cairn glbs (`snow_mound` stands in).

## Art the story needs (art pack: /workspace/hearthmoor-staging/art/jotunheim/, READY.txt = go)
At scaffold time `/workspace/hearthmoor-staging/art/jotunheim/` did not exist, so everything below is from the story (2.2, 5, 8, 9), not from a README.
- **Palette:** `pal-gloom-and-glow` blue ramp (cold fire `#3fb8ff` / core `#e8f6ff`), black stone `#1a1d26`, snow shadow `#3a4a6a`, snow lit `#c8d6ec`, aurora `#3fe0a0` -> `#a45cf0`, frost runes `#7fd4ff`, glow orbs `#9fe8ff`, ice pools `#2fd0d0`. Neon hexes only on glow pixels (check-sprite allow-list needs scoping for the realm's neon, as `SVART_NEON_ALLOW` did).
- **NPC sheets (8):** the giants above, 2x-3.2x, real tops and bottoms with a visible waist, no armour on townsfolk. **Enemy sheets:** frost troll (1.6x and the 2x gate version), ice golem, avalanche golem, rime berserker, Hjordis.
- **Big sheets (own frame sizes):** Hrimgard (7x, plate, the only plate), Ormgar (3x), rares `frostmother` (2.5x), `avalanche` (3x).
- **Companion / pet / mount:** Ulfar (2.4x combat), Flurry (hare, glowing blue ear tips), the goat (Clatter, 1.6x a horse) and goat-pen goats.
- **Kit pieces (glb):** cold-fire braziers taller than the player, frost-rune standing stones, hanging rime-glass globes, iron braziers, 3 m turf-roofed longhouse pieces and 4 m doors, goat pens, ice pools with glow tips, icicles, rune locks, the Barrow door (6 m), brazier snuffing variants, shields on walls, ice-bridge runes (lit / unlit), tomb pieces.
- **Gamefx / spells:** `jot_fx` rows (cold-fire flame strip, frost puff, snow puff, rune pulse, ice spikes, avalanche rolling snowball, boulder, frost-rune trap, cold-fire patch), Stonefrost spell icons, the aurora sky layer, blizzard snow.
- **Portraits** if the game shows them for the Jarl / Ulfar / Solvi.
- **SFX (library):** `babble` pitched down 6 semitones, `door`, `explosion`.
