# HEARTHMOOR — Grok restore kit (2026-10-01, input polish: controller, floating stick, no page zoom, loading gate)

Hearthmoor, a small cozy HD-2D village errand game built on the hd2d-suite runtime. If a later Grok is asked to continue this game, **this archive is the source of truth**. Unzip it so the folder is `/workspace/hd2d-suite/games/hearthmoor/` and run `startup.sh`, which serves it on `0.0.0.0:8080`. There is no install and no build step: it is static three.js r160 ES modules with an import map. `build.py` (rebuilding the areas from `areas/src/*.json`) needs the rest of `/workspace/hd2d-suite`.

Repo handoff docs (in the suite root): [`AGENTS.md`](../../AGENTS.md), [`CHANGELOG.md`](../../CHANGELOG.md), [`docs/HD2D_COZY_STYLE_LOCK.md`](../../docs/HD2D_COZY_STYLE_LOCK.md). Play online: https://unclebill-spec.github.io/hd2d-suite/games/hearthmoor/

## Identity

- **Title:** Hearthmoor (working title)
- **Loop:** You are the new hedgewitch in town. Walk the village, talk to neighbours, run three cozy errands, learn charms as thank-yous, and save whenever you like.
- **Areas:**
  - Hearthmoor Plaza: market stall, three cottages, terrace stairs, and the moss gate at the top of the stairs.
  - Bakery Lane: bakery, the Kettle & Key inn, flower shop, fountain, laundry over the stairs.
  - Mossglen: a glade through the gate, with layered oaks and birches, a shrine up mossy steps, standing stones, stone lanterns, mushroom rings, ferns, and fireflies even by day.
- **Errands:**
  1. **Warm Bread:** Marla the baker (Plaza) gives you a hearthloaf for Bram at the Kettle & Key (Lane). Reward: copper bits and the hearth flame charm.
  2. **Moonpetal Tea:** Wren the herbalist (Lane) wants 3 moonpetals from Mossglen. Reward: a tin of moonpetal tea and the light orb charm.
  3. **Where's Pudding?:** Tib (Plaza) lost his cat. She is by the Mossglen shrine, and she follows you home through the gate. Reward: Tib's lucky acorn and the leaf gust charm.
- **Look:** pixel billboard actors (20x32, 1 px ink outline, nearest-neighbour) in a lit 3D miniature. Locked 3/4 camera with mild tilt-shift, one warm key sun plus lamps, and sprite shadows. Day is warm, dusk is blue, night has orange windows. The HUD is parchment and carved wood. No bloom and no blurred sprites.
- **Day cycle:** real-time, compressed: one whole day (day, dusk, night, dawn) takes 12 minutes. The time is saved with the game.
- **Audio:** procedural WebAudio, no files. It has a soft pad, music-box plucks, birds by day, crickets at night, a shimmer in Mossglen, and chimes for pickups, errands and the portal.

## Controls

- **Walk:** WASD / arrows (Shift runs), or tap/click the ground. Tap-to-walk is A* pathfinding, so it goes around walls and props and takes the stairs.
- **Talk:** E / Space / Enter or tap an NPC. Press E, tap the box, or tap anywhere again to finish the line or turn the page. Esc closes the dialogue.
- **Charms:** F casts, Q switches charm. On the pad, ✦ taps to cast and holds to switch.
- **Quest log:** J (or L), the `quests n/3` chip, or the pad's ☰ button.
- **Other keys:** K (or Ctrl+S) saves, M toggles sound, T jumps to the next time of day, P pauses the clock, + / - or the wheel zooms.
- **Phone:** tap to walk, pinch to zoom. The Layout One pad turns on automatically on touch screens (or with G / the `pad` chip / `?pad=1`). For a left-handed pad use H, the `hand` chip, or `?hand=left`.
  - The stick **floats**: it appears wherever your thumb lands in the movement zone (left half, lower 58 % of the screen; right half when left-handed), follows a sliding finger and re-centres if you drag past its rim. A small tilt walks slowly, the rim runs. A quick tap inside the zone still walks there; taps anywhere else walk too.
  - The page never scrolls or zooms. Pinch is the in-game camera zoom only.
- **Bluetooth / USB controller** (Gamepad API, standard mapping; press any button to wake it, a "🎮 controller connected" toast confirms):

  | Button | Does |
  |---|---|
  | Left stick | walk, analog speed (full tilt runs) |
  | D-pad | walk (full walking speed) |
  | A | talk / advance dialogue / close the log; on the title: Continue (or New game) |
  | B | close dialogue or the log, cancel a walk |
  | X | cast the charm; on the title: New game (press twice to replace a save) |
  | Y, RB | next charm |
  | LB | previous charm |
  | LT / RT | zoom out / in (analog) |
  | Start | open / close the quest log (on the title: Continue) |
  | Select | show / hide the on-screen pad |

  While the controller is in use the on-screen pad hides and the hint line shows the controller keys; touching the screen brings the pad back. Keyboard, mouse (click-to-walk, wheel zoom), touch and the controller all work at the same time.
- **Loading:** until the area's assets and first frames are ready, a loading overlay sits on top and every tap, click and key is swallowed, so nothing queues up and the title can't be skipped.
- **Gates:** walk off the south lane (Plaza → Lane) or up the north path (Lane → Plaza). Step into the swirl (Plaza ↔ Mossglen). Every area change fades.

## This snapshot

- Three areas built by `build.py` from `areas/src/{plaza,lane,mossglen}.json` with the hd2d tools. Each area folder holds only the files its `scene.json` uses.
- The moss gate (`portal_arch` kit piece plus `hd2d portal` effects) is original pixel art in the cozy palette:
  - a swirling two-arm vortex billboard in a stone arch;
  - a rotating rune ring decal under your feet;
  - a sky-blue light;
  - fireflies.
- The rift refs were used as style reference only, never copied.
- Moonpetal pickups glimmer. Quest tags ("!" and a gold star) float over whoever has an errand for you or is waiting on one.
- Dialogue is a carved-wood frame with a parchment page, a pixel portrait cropped from the NPC's own sprite, a typewriter line and a page counter.
- The parchment bag shows item icons (16 px, biome palette). On the pad, the rail shows the same items.
- Saves go to `localStorage` key **`hearthmoor-slot-1-v1`**:
  - what's saved: area, position, clock, bag, errands, pickups taken, where Pudding is, charms;
  - autosave every 20 s, on area change, on errand steps, and when the tab hides;
  - the title screen offers Continue or New game.
- PWA: `manifest.webmanifest`, icons, and a `sw.js` that precaches all files for offline play (cache-first, versioned name). `?nosw` skips registration.
- QA URL: `?qa&area=plaza|lane|mossglen` boots an area with a fresh state, no title and no saving (for check-scene). `?simscale=N` speeds the simulation up (smoke test). `?reset` clears the save. `?day=SECONDS` changes the day length.

## Key files

| Path | What |
|---|---|
| `index.html` | HUD (title chip, bag, clock, chips), dialogue box, quest log, Layout One pad, fade, title screen |
| `game/game.js` | Area manager (fresh canvas per area, fade), exits / portals / pickups, dialogue, errands, bag, quest tags, Pudding follow, save/load, title |
| `game/data.js` | Items, errands, every line of dialogue (original), quest-tag rules |
| `game/audio.js` | Procedural ambient audio + SFX, M mute |
| `game/game.css` | Parchment / carved-wood HUD, phone portrait + short-landscape layouts |
| `engine/`, `vendor/` | hd2d runtime (boot/hooks, A* nav, decal depth, pad) + three r160 |
| `areas/<id>/` | `scene.json` (+ `game` block: exits, portals, pickups, spawns) and its `public/art` |
| `areas/src/*.json` | Area specs (source of truth for rebuilding) |
| `build.py` | Assemble areas, prune, icons, manifest + sw.js, zip |
| `tests/smoke.py` | Playwright end-to-end playthrough (all 3 errands, both exits, portal both ways, save/reload x2, loading gate, stubbed controller, phone floating stick / no-zoom / left hand) |
| `tests/gamepad_stub.js` | Fake standard-mapping controller behind `navigator.getGamepads()` for the smoke test |
| `engine/gamepad.js`, `engine/pad.js` | Controller polling + hot-plug; floating-stick Layout One pad |
| `startup.sh` | Static preview server on `0.0.0.0:8080` |

## Do not regress

- Locked 3/4 camera: no yaw, no orbit, no free camera. Pinch / wheel zoom only inside the limits.
- Sprites stay sharp: integer pixel scale, nearest, 1 px outline. No bloom, no blur halos, no blurred HUD. check-scene `sprites_sharp`, `effects_sharp`, `gamefx_sharp` and `no_bloom` must pass for all 3 areas.
- Real height (terraces + stairs), one key sun plus lamps, sprite shadows, warm day / blue dusk / orange-window night.
- HUD is parchment and carved wood only. No copied UI or IP from any other game.
- Tap-to-walk uses A* (around walls and props, up the stairs). Tapping an NPC walks there and talks. Tapping a glimmer or the swirl walks onto it.
- 3 errands complete end to end. Pudding follows across areas, the gate works both ways, and both edge exits fade.
- Spell keys stay: F cast, Q switch, pad ✦ (tap cast / hold switch). Charms are rewards (start with sparkle burst).
- Save key `hearthmoor-slot-1-v1` (bump the version, don't silently change the format). Continue restores area, position, clock, bag, errands, pickups, Pudding and charms.
- Phone: tap, pinch, Layout One pad with the left-hand flip. HUD inside the viewport, no overlapping controls, touch targets ≥ 30 px (check-scene `phone`).
- Floating stick: appears under the thumb anywhere in the zone, re-centres past its radius, analog walk / rim run, mirrored by the left-hand flip; a quick tap in the zone still walks (check-scene `phone.floating_stick`, smoke).
- Controller: standard mapping as in the table above, hot-plug toast, pad hidden while used and back on touch, title usable with A / X / Start (no browser `confirm()` dialogs anywhere).
- No page scroll or zoom: viewport `user-scalable=no, maximum-scale=1`, `touch-action: none`, `overscroll-behavior: none`, `gesturestart` / `dblclick` / ctrl+wheel / long-press menu blocked (check-scene `phone.no_page_zoom`).
- Loading gate: no input reaches the game before the first frames are drawn (check-scene `phone.loading_gate`, smoke).
- Desktop: WASD / arrows, mouse click-to-walk and wheel zoom keep working alongside touch and the controller.
- The decal ring sits under props and actors.
- `tests/smoke.py` must PASS.
- Preview binds `0.0.0.0:8080` (`startup.sh`).

Player saves live in browser `localStorage`, not in this zip.

## Run

```
cd /workspace/hd2d-suite/games/hearthmoor && ./startup.sh          # http://<host>:8080/
python3 /workspace/hd2d-suite/games/hearthmoor/tests/smoke.py       # end-to-end playthrough (~5 min headless)
python3 /workspace/hd2d-suite/games/hearthmoor/build.py             # rebuild areas + zip (needs the suite)
/workspace/hd2d-suite/bin/hd2d check-scene games/hearthmoor --scene-dir areas/plaza --params "area=plaza&qa"
```
