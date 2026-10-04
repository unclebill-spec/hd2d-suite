# Changelog

Dates are America/New_York. Newest first. Keep this current with every change you push.

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
