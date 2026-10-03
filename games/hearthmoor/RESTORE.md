# HEARTHMOOR — Grok restore kit (2026-10-03, Stage 1: platform polish, 6 playable heroes, real-time combat core)

Hearthmoor, a small cozy HD-2D village errand game built on the hd2d-suite runtime. If a later Grok is asked to continue this game, **this archive is the source of truth**. Unzip it so the folder is `/workspace/hd2d-suite/games/hearthmoor/` and run `startup.sh`, which serves it on `0.0.0.0:8080`. There is no install and no build step: it is static three.js r160 ES modules with an import map. `build.py` (rebuilding the areas from `areas/src/*.json`) needs the rest of `/workspace/hd2d-suite`.

Repo handoff docs (in the suite root): [`AGENTS.md`](../../AGENTS.md), [`CHANGELOG.md`](../../CHANGELOG.md), [`docs/HD2D_COZY_STYLE_LOCK.md`](../../docs/HD2D_COZY_STYLE_LOCK.md). Play online: https://unclebill-spec.github.io/hd2d-suite/games/hearthmoor/

## Identity

- **Title:** Hearthmoor (working title)
- **Loop:** Pick one of six starter heroes, arrive in the village, talk to neighbours, run three cozy errands, learn charms as thank-yous, and fight the gloom-and-glow creatures in Mossglen with real-time action combat (attack, guard, jump, dodge roll, a class spell and a summon). Save whenever you like.
- **Heroes (title → hero picker):**

  | Hero | Origin | Kind | First spell | First summon |
  |---|---|---|---|---|
  | Wildcaller | Midgard farmhand | mortal | Seed Bomb (lobbed, earth burst) | Mushroom golem |
  | Runeguard | Shield-warden | mortal | Rune Slam (nova + push) | Rune sentinel |
  | Seer | Rune-reader | mortal | Rune Trap (glyph mine) | Rune wisp |
  | Stormborn | Child of thunder | demigod | Chain Lightning (leaps to 2 more foes) | Storm sprite |
  | Grovekeeper | Child of the Vanir | demigod | Bloom (heal ring + small hit) | Sapling |
  | Cinderknight | Ember-born | demigod | Ember Slash (piercing fire wave) | Ember imp |

  Stats and blurbs live in `game/heroes.js`. The chosen class is the player sprite and is saved.
- **Enemies (Mossglen):** a stone golem (slow, heavy slam), a skeleton swordsman (quick lunge), and a blue cold-fire wraith (floats, keeps its distance, throws cold-fire bolts). A second wraith drifts in only at night. They wander near home, aggro when you come close, telegraph their attacks with a white flash, leash home past 12 m, and respawn after 60 s. Gloom-and-glow only: stone, bone and cold blue fire, nothing slimy.
- **Areas:**
  - Hearthmoor Plaza: market stall, three cottages, terrace stairs, and the moss gate at the top of the stairs.
  - Bakery Lane: bakery, the Kettle & Key inn, flower shop, fountain, laundry over the stairs.
  - Mossglen: a glade through the gate, with layered oaks and birches, a shrine up mossy steps, standing stones, stone lanterns, mushroom rings, ferns, and fireflies even by day.
- **Errands:**
  1. **Warm Bread:** Marla the baker (Plaza) gives you a hearthloaf for Bram at the Kettle & Key (Lane). Reward: copper bits and the hearth flame charm.
  2. **Moonpetal Tea:** Wren the herbalist (Lane) wants 3 moonpetals from Mossglen. Reward: a tin of moonpetal tea and the light orb charm.
  3. **Where's Pudding?:** Tib (Plaza) lost his cat. She is by the Mossglen shrine, and she follows you home through the gate. Reward: Tib's lucky acorn and the leaf gust charm.
- **Look:** pixel billboard actors (20x32, 1 px ink outline, nearest-neighbour) in a lit 3D miniature. Locked 3/4 camera with mild tilt-shift, one warm key sun plus lamps, and sprite shadows. Day is warm, dusk is blue, night has orange windows. The HUD is parchment and carved wood. No bloom and no blurred sprites.
- **Day cycle:** real-time, compressed: one whole day (day, dusk, night, dawn) takes 24 minutes (`?day=` seconds overrides). The time is saved with the game.
- **Audio:** procedural WebAudio, no files. It has a soft pad, music-box plucks, birds by day, crickets at night, a shimmer in Mossglen, and chimes for pickups, errands and the portal.

## Controls

| Action | Keyboard + mouse | Controller | Touch (pad) |
|---|---|---|---|
| Walk / run | WASD / arrows, Shift runs; click the ground | left stick (full tilt runs), d-pad | floating stick (rim runs), tap the ground |
| Talk | E / Space / Enter, click an NPC | A | MAIN button shows 💬 near someone; tap the NPC |
| Attack | R | X (or RS click) | MAIN button (⚔) when nobody is near |
| Guard (hold) | C | LT | guard button (hold) |
| Jump | Z | A when nobody is near, LS click | jump button |
| Dodge roll | X | B (when nothing to close) | roll button |
| Cast spell | F casts the current slot | Y | ✦ tap |
| Pick spell | Q next, 1-4 slot | LB / RB; hold Y: slow-time wheel, stick picks, let go casts | ✦ hold: slow-time wheel, slide, let go casts |
| Summon | V | RT | summon button |
| Quest log | J / L | Start | ☰ |
| Options | O or the ⚙ chip | | ⚙ chip |
| Hero screen (stats, skills) | I | Start, then Y / LB / RB | tap the vitals chip |
| Gear + bag (equip / scrap) | G (or I, then → to Gear) | Start, Y, then RB to Gear; A equip, X scrap | tap the vitals chip, Gear tab |
| Spellbook (assign the 4 slots) | B (or I, then → to Spells) | Start, Y, then RB to Spells | tap the vitals chip, Spells tab |
| Zoom | + / - / wheel | right stick up / down | pinch |
| Close / cancel | Esc | B | tap |

- 4 spell slots: slot 1 is the hero's class spell, slots 2-4 are the newest charms learned as errand rewards. Spells, the summon (30 s) and charms have cooldowns, shown as a dimmed sweep on the pad buttons.
- **Leveling:** XP from enemies and errands, level cap 50, six stats (Might, Arcana, Spirit, Vigor, Grit, Swiftness), 2 free stat points and 1 skill point per level. A new game asks "Auto level? Yes / No" (options: `auto level`). The hero screen spends points and learns tier I of each hero's three skill branches (`game/progress.js`).
- **Glow pass:** spells leave a short light pool (gold dithered decal + glitter + a point light in the spell's colour); red-and-white toadstools glow at night (19:12–06:00) in all three areas; light zones (lit lamps, toadstools, spell pools) make you glowlit (+10% damage, 1.5x stamina, "✦ glowlit" in the vitals chip) and wraiths stay out of light and hold fire on a lit hero (`game/glow.js`, engine `ctx.addGlow`).
- **Loot + gear:** beaten foes drop gold and (60%, 70% on Hero) an item in one of five rarities: Common white, Uncommon green, Rare blue, Epic purple, Legendary orange-gold. Each drop stands under a pixel beam in its colour; Epic has a faint stepped glow ring, Legendary an animated neon aura. Walk over a drop to take it. The hero screen's Gear tab (G) shows the weapon / armor / trinket slots and the bag (30): Enter / A equips, X scraps for gold. Gear feeds the same stat mods as levels (`game/loot.js`, saved as `bag`, `gear`, `gold`).
- **Modes + faint penalty:** chosen on the hero picker (`mode:` button, M / Y), changeable in options `mode:` Story (foes hit 40% softer, +15% damage, no faint penalty) / Adventurer (default) / Hero (foes hit 35% harder, -10% damage, better loot). Outside Story, fainting drops 10% of carried gold as a purse where you fell (saved as `purse`, survives area changes); walk back over it to get it all back. `?mode=story|adventurer|hero`.
- **Enemy pathfinding:** enemies chase and walk home along A* paths over the nav grid (`Combat.seek`), so walls, fences, terrace edges and trees are walked round, not slid along.
- **Vitals:** a parchment chip (top left, under the title) shows HP and stamina. Attacks, guarding hits and rolls cost stamina; it refills after a short pause.
- **Combat:** hits land on the attack's impact frame inside a short arc; damage numbers are a crisp 3x5 pixel font with an ink outline (red you, cream enemies, blue guarded, green heal). Guarding from the front takes a quarter of the damage (a Runeguard even less). The roll is a pixel-exact tumble with i-frames for its first 0.26 s. Being downed is cozy: you slump, the screen warms to dark, you wake at the area start with full HP, two seconds of grace and nothing lost.
- **Other keys:** K (or Ctrl+S) saves, M toggles sound, T jumps to the next time of day, P pauses the clock, G toggles the pad, H flips it for left hands.
- **Options card (O / ⚙, also on the title):** display preset, fullscreen, Install, sound, pad, hand.
  - Display presets: Auto, Phone landscape (DPR capped at 1.5), 720p, 1080p TV (bigger HUD with TV-safe inset), Retro 320x240 (4:3 letterboxed, chunky integer pixels). Stored in `localStorage` `hd2d-display`, or `?display=auto|phone|720p|1080p|retro`.
  - Install uses the browser's `beforeinstallprompt`. On iPhone / iPad (no prompt) it shows a "Share → Add to Home Screen" tip instead.
- **Rotate prompt:** on a phone held upright a small parchment banner asks you to turn it sideways (the game still works in portrait). It goes away by itself after a few seconds or when tapped.
- **See-through silhouette:** when a building or tree hides you, a dithered plaster-coloured silhouette of your hero shows through.
- **Phone:** tap to walk, pinch to zoom. The Layout One pad turns on automatically on touch screens (or with G / the `pad` chip / `?pad=1`). For a left-handed pad use H, the `hand` chip, or `?hand=left`.
  - The stick **floats**: it appears wherever your thumb lands in the movement zone (left half, lower 58 % of the screen; right half when left-handed), follows a sliding finger and re-centres if you drag past its rim. A small tilt walks slowly, the rim runs. A quick tap inside the zone still walks there; taps anywhere else walk too.
  - The page never scrolls or zooms. Pinch is the in-game camera zoom only.
- **Bluetooth / USB controller** (Gamepad API, standard mapping; press any button to wake it, a "🎮 controller connected" toast confirms):

  | Button | Does |
  |---|---|
  | Left stick | walk, analog speed (full tilt runs) |
  | D-pad | walk (full walking speed); in the hero picker: choose |
  | Right stick up / down | zoom in / out |
  | A | talk / advance dialogue / close the log; jump when nobody is near; on the title: Continue (or New game); picker: Begin |
  | B | close dialogue or the log, cancel a walk; otherwise dodge roll; picker: Back |
  | X, RS click | attack; on the title: New game (press twice to replace a save) |
  | Y | cast the current spell |
  | LB / RB | previous / next spell slot; picker: previous / next hero |
  | LT (hold) | guard (each trigger has exactly one job: the old LT zoom double-map is gone) |
  | RT | summon |
  | LS click | jump |
  | Start | open / close the quest log (on the title: Continue) |
  | Select | show / hide the on-screen pad |

  While the controller is in use the on-screen pad hides and the hint line shows the controller keys; touching the screen brings the pad back. Keyboard, mouse (click-to-walk, wheel zoom), touch and the controller all work at the same time.
- **Phone action buttons:** an arc of thumb-sized carved-wood buttons around the big MAIN button (attack / talk): guard, jump, roll, ✦ spell (with the slot name), summon and ☰ log. Pixel icons from `art/buttons.png`. The left-hand flip mirrors the whole cluster.
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
- Saves go to `localStorage` key **`hearthmoor-slot-1-v2`** (`v: 2`):
  - what's saved: hero class, HP, area, position, clock, bag, errands, pickups taken, where Pudding is, charms;
  - autosave every 20 s, on area change, on errand steps, and when the tab hides;
  - the title screen offers Continue or New game (New game opens the hero picker);
  - **migration:** an old `hearthmoor-slot-1-v1` save still loads. Continue opens the hero picker once (v1 had no class), then everything else carries over and is written to v2. The v1 key is left untouched.
- Combat lives in `game/combat.js` (enemy AI, hitboxes, damage, guard, i-frames, defeat/respawn, spells, summons, damage numbers, HP bars). Enemy and summon sprites are drawn in code by `tools/sprite/roles_enemies.py` (same 20x32 cell, ink outline, biome palette) and baked into every area atlas; spells / hit sparks are `tools/spells` effects (glow pixels only).
- PWA: `manifest.webmanifest`, icons, and a `sw.js` that precaches all files for offline play (cache-first, versioned name). `?nosw` skips registration.
- QA URL: `?qa&area=plaza|lane|mossglen` boots an area with a fresh state, no title and no saving (for check-scene); enemies stay peaceful unless `&combat`, and `&hero=<id>` picks the hero (default wildcaller). `?peace` keeps enemies calm in normal play (smoke test). `?simscale=N` speeds the simulation up (smoke test). `?reset` clears the save. `?day=SECONDS` changes the day length.

## Key files

| Path | What |
|---|---|
| `index.html` | HUD (title chip, bag, clock, chips), dialogue box, quest log, Layout One pad, fade, title screen |
| `game/game.js` | Area manager (fresh canvas per area, fade), exits / portals / pickups, dialogue, errands, bag, quest tags, Pudding follow, save/load + v1 migration, title, hero picker, options card, install, rotate prompt, touch action buttons, spell wheel, vitals |
| `game/heroes.js` | The 6 starter heroes, class spells, summons, enemy stats, Mossglen spawns, player combat constants |
| `game/combat.js` | Real-time combat: enemy AI, melee hitboxes, spells, summons, guard, i-frames, damage numbers, HP bars, cozy defeat |
| `game/data.js` | Items, errands, every line of dialogue (original), quest-tag rules |
| `game/audio.js` | Procedural ambient audio + SFX, M mute |
| `game/game.css` | Parchment / carved-wood HUD, phone portrait + short-landscape layouts |
| `engine/`, `vendor/` | hd2d runtime (boot/hooks, A* nav, decal depth, pad) + three r160 |
| `areas/<id>/` | `scene.json` (+ `game` block: exits, portals, pickups, spawns) and its `public/art` |
| `areas/src/*.json` | Area specs (source of truth for rebuilding) |
| `build.py` | Assemble areas, prune, icons, manifest + sw.js, zip |
| `tests/smoke.py` | Playwright end-to-end playthrough (hero picker, all 3 errands, both exits, portal both ways, Mossglen combat, save/reload x2, v1 migration, loading gate, stubbed controller, phone floating stick / action buttons / spell wheel / no-zoom / left hand) |
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
- Spell keys stay: F cast, Q next, 1-4 slots; pad ✦ tap casts, hold opens the slow-time wheel; controller Y tap casts (on release), hold Y opens the same wheel. Charms are rewards (start with sparkle burst); by default slot 1 is the class spell, and the spellbook (B / hero screen Spells tab, saved as `slots`) can put any known spell in any slot.
- Combat keys stay: R attack, C hold guard, Z jump, X roll, V summon (controller X / LT / A / B / RT as in the table). Enemies are gloom-and-glow (stone, bone, cold blue fire), nothing slimy. Defeat stays cozy (nothing lost).
- Save key `hearthmoor-slot-1-v2` (bump the version, don't silently change the format) and keep the v1 migration. Continue restores hero, area, position, clock, bag, errands, pickups, Pudding and charms.
- Title → hero picker for the 6 starters works with keys, controller and taps.
- New game asks "Auto level? Yes / No"; the hero screen works with keys, controller and taps; stats and tier-I skills change combat numbers; no XP loss on defeat.
- At night the toadstools glow and their pools light the ground; casting leaves a light pool + glitter; standing in light shows "✦ glowlit"; the night wraith will not enter light. No bloom anywhere.
- Loot beams show the five rarity colours with no blur; the Gear tab equips and scraps with keys, controller and taps; fainting in Story mode costs nothing, otherwise the purse can always be walked back to.
- Phone: tap, pinch, Layout One pad with the left-hand flip. HUD inside the viewport, no overlapping controls, touch targets ≥ 30 px (check-scene `phone`).
- Floating stick: appears under the thumb anywhere in the zone, re-centres past its radius, analog walk / rim run, mirrored by the left-hand flip; a quick tap in the zone still walks (check-scene `phone.floating_stick`, smoke).
- Controller: standard mapping as in the table above (no button does two jobs), hot-plug toast, pad hidden while used and back on touch, title usable with A / X / Start (no browser `confirm()` dialogs anywhere).
- Display presets keep integer sprite scale; Retro 320x240 stays letterboxed 4:3.
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
