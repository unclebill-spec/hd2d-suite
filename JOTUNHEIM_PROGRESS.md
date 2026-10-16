# Jotunheim (Stonehollow, the Rime Caves, the Titan's Barrow): build progress

RESUME HERE (Oct 16 2026, branch `realm-jotunheim` from main 2de49ce, worktree /workspace/hd2d-jotunheim): SCAFFOLD ONLY; section 13 decisions answered below (Oct 16, 12:40 AM). Done: this file;
`tools/hearthmoor/jot_art.py` (skeleton, placeholder tables, refuses to run without READY.txt); `game/jotunheim.js` (stub, registers
`G.jot`, no areas, no quests); one-line hooks in `game/game.js` and `build.py` (tagged `[JOTUNHEIM]`); `sw.js` regenerated for the new module.
**HOLD all area builds** until `/workspace/hearthmoor-staging/art/jotunheim/READY.txt` exists (at scaffold time the folder did not exist at
all). Next, in order, once READY: (1) copy the pack to `games/hearthmoor/art/jotunheim/` and read its README, (2) fill the `jot_art.py`
tables from the real file names, (3) write `areas/src/jotunheim.json` and build ONE area at a time into a private dir
(`HM_BUILD_TMP=/tmp/jot_hmbuild python3 build.py --areas jotunheim --no-zip`), then `python3 tools/hearthmoor/jot_art.py jotunheim`, then
`HM_BUILD_TMP=/tmp/jot_hmbuild python3 -c "import build; build.write_pwa()"`, (4) move the area into `AREAS_JOT` / `AREA_NAMES_JOT` in
`game/jotunheim.js`, (5) quick-load, `check_scene --quick` under the browser lock, one area at a time. Then the quests (story 3), the
Bifrost gate (3.1), the choice (5.2), the Barrow (7), Hrimgard (8.1).
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
| `rimecaves` | The Rime Caves | 20 x 16 m | not built. Solvi's rune-hall `[-6,-4]`, Barrow mouth `[0,-7.5]` (3 rune locks), 5 glow pools, `rc_spring` behind a frozen waterfall (fire spell melts it), rares by the far pool |
| `barrow` | The Titan's Barrow, part 1 (B1-B4) | 4 rooms | not built. Door, Hall of Shields, Glow Pools, Avalanche Run. Decision 8: two areas like the Clockwork Deep |
| `barrow2` | The Titan's Barrow, part 2 (B5-B9) | 5 rooms | not built. Frozen Echo, Berserker Hall, Rune Bridge, Waystone Crypt, the Throne Barrow (Hrimgard's arena) |

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
| `hrimgard` | **Hrimgard the Unthawed** (boss, B9) | 6x (decision 4) | only plate in the arc; P1 ground slam rings + cold-fire breath cone; P2 (60%) 2 ice golems + the floor freezes (slide); P3 (25%) the snuffed braziers relight one by one, snuff them mid-fight to stop his heal. `plate: true, element: "ice"`, HP x10 base |
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
4. **Hrimgard is 6x**, to match Gorrak (`ENEMIES.hrimgard.scale = 6`; the story's 7x is superseded).
5. **Ulfar is 2.4x in combat** (3x in town). Fine.
6. **One active companion at a time**: Ulfar and Dagna don't both follow. They swap at the Bifrost Gatekeepers' Guild desk or at any inn (already built for Lumi / Dagna / Tobble in `svartalfheim_companions.js`: add `ulfar` to `COMP`).
7. **Halvard does not lose Kolbrun's horn.** Only the copper key is lost (to avoid too many lost keys). *The Barred Gate*: Halvard hands the horn over straight (no "wrong drawer" step), stage 1 keeps `jg_asked` / `jg_troll`; `jg_horn` is set when he gives it.
8. **The Barrow is two areas, `barrow` and `barrow2`**, like the Clockwork Deep (`barrow` B1-B4 with the Avalanche Run, `barrow2` B5-B9: Frozen Echo, Berserker Hall, Rune Bridge, Waystone Crypt, Throne Barrow with Hrimgard). The area list is now 5 areas.
9. **The goat mount is deferred**: it goes on the leftovers list. `jt_goat` (*The Goat Who Chose You*) can still be built as a ripple quest whose reward waits for mounts; Clatter stays a pen goat for now.

## Leftovers (deferred on purpose)
- The goat mount (`S.mounts.goat`, climbing snow slopes): mounts are not built in the engine. Decision 9.
- Everything in the RESUME HERE list that is blocked on art (READY.txt).

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
