# Changelog

Dates are America/New_York. Newest first. Keep this current with every change you push.

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
