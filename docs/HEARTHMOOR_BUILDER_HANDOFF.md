# Hearthmoor: builder handoff (game design document)

**For:** Bill's Master Builder agent. **Written:** 2026-10-02 (America/New_York).
**Owner / creative director:** Bill Weathersbee (GitHub `unclebill-spec`). The storyboarding agent stays on story and management; the builder builds.
**Repo:** https://github.com/unclebill-spec/hd2d-suite (branch `main`, public, GitHub Pages serves `main` at the root).

This file is the one entry point. It merges the approved design in [`docs/story/STORY_SEEDS.md`](story/STORY_SEEDS.md), the binding [`docs/HD2D_COZY_STYLE_LOCK.md`](HD2D_COZY_STYLE_LOCK.md), [`AGENTS.md`](../AGENTS.md), [`CHANGELOG.md`](../CHANGELOG.md), the tool READMEs and the code as it actually stands. Nothing here is new design. Where drafts disagreed, the later entry won (see [Resolved contradictions](#appendix-a-resolved-contradictions)). Open questions are listed in section 11; **don't decide them yourself**, ask Bill.

**Precedence when sources disagree:** style lock (art, camera, light) > this file > `STORY_SEEDS.md` > older notes. Code facts: the code wins over any doc.

## Contents
1. [Pitch and pillars](#1-pitch-and-pillars)
2. [Style lock and art rules](#2-style-lock-and-art-rules)
3. [Platform and input requirements](#3-platform-and-input-requirements)
4. [Story](#4-story)
5. [World](#5-world)
6. [Heroes, magic, summons, pets](#6-heroes-magic-summons-pets)
7. [Enemies and bestiary](#7-enemies-and-bestiary)
8. [Dungeons and rifts](#8-dungeons-and-rifts)
9. [Progression and economy](#9-progression-and-economy)
10. [Current build status](#10-current-build-status)
11. [Open decisions for Bill](#11-open-decisions-for-bill)
12. [Suggested build order and repo rules](#12-suggested-build-order-and-repo-rules)
- [Appendix A: resolved contradictions](#appendix-a-resolved-contradictions)

---

## 1. Pitch and pillars

**Hearthmoor** is a cozy HD-2D action RPG in an original Norse Nine Realms setting. You start in the small village of Hearthmoor in Midgard, cross the **Rainbow Rift** (a Bifröst-like bridge of portals) realm by realm, and stop the frost-witch **Veyra Ashmantle** from turning the nine realms against each other, or help her do it. In every realm you choose to **conquer** or **befriend**. Those choices, plus which portals you open and close, reshape the map, your allies, your companions and the ending. Fifteen heroes (6 starters + 9 secret New Game+ heroes), elemental golems and wraiths, vampire lords and overlord demons, random rifts, factions with merit you have to earn, and real loot.

**Pillars**

| Pillar | Means |
|---|---|
| Cozy HD-2D | Super Famicom-style pixel sprites in a lit 3D miniature: locked 3/4 camera, tilt-shift, sprite shadows, warm day / blue dusk / orange-window night. The home town is kind. |
| Gloom-and-glow | Bill's absolute love: dark scenes full of glowing things (wisps, fireflies, glowing mushrooms, runes, portals, orb lanterns with glowing fish, torches casting light and shadow). Every realm gets a dark/night look with glowing points. |
| Signature glows | **Neon blue cold fire** (primary), **violet neon**, **red neon**. Emissive pixels + point lights + light pools. **Never bloom.** |
| Choices change the world | Conquer vs befriend, rival realms, Saver vs Breaker, opening/closing portals (Bill's favourite mechanic). |
| Earned progression | Five factions with merit ranks that take real activity; five-tier loot; upgrades, rerolls, sockets. |
| Phone first | Floating joystick, no page scroll/zoom, installable PWA; controller and keyboard+mouse work at the same time. |
| Original IP | Public-domain Norse myth as flavour only. All art, characters and names are original. |

---

## 2. Style lock and art rules

Binding law: [`docs/HD2D_COZY_STYLE_LOCK.md`](HD2D_COZY_STYLE_LOCK.md). Where a prompt and the style lock disagree on camera, world or lighting, the style lock wins.

- **Two pipelines in one frame.**
  - **Sprites:** native pixel art, 16-bit billboards about 16–24 px wide and 24–40 px tall (current spec 20x32, feet pivot bottom-centre), **nearest-neighbour only**, integer pixel scale, hard alpha (0/255), 1 px ink outline, big readable head, palette-locked colours (≤ 20 per role). Sprites **never** go through the world's blur pass and are never bilinear-filtered or mipmapped.
  - **World:** 3D block-out or stacked painted planes with **real height** (terraces, stairs, roofs with thickness). Painted / texel-snapped materials, not PBR chrome. A sprite is about 1.6–2.0 m (1.8 m in the kit).
- **Camera:** locked 3/4 high angle, fixed pitch, no yaw/orbit, no free cam, no first person, no side-view. Pinch/wheel zoom inside limits only. Mild tilt-shift: the focus band follows the player; foreground and far hills soft.
- **Light:** one key sun + local lamps; characters cast real shadows. Warm gold day, cool blue dusk, orange windows at night. Volume haze in valleys.
- **No bloom.** Glow = emissive palette pixels + small point lights + light pools. No full-screen bloom, no TAA smear, no "mobile bloom soup".
- **Particles:** cheap pixel points (dust motes, wisps, fireflies, embers, leaves).
- **Palette:** 16–28 colours per biome. Signature glows: blue cold fire (torches/braziers, wraiths, liches, Veyra/Niflheim), violet (Alfheim, Helheim, Lady Sylvaine), red (vampires, overlord demons, blood golems).
- **HUD:** parchment / carved wood. Never Octopath's chrome or turn-battle HUD.
- **Mood:** cozy by default. Darkness and gloom are fine in realms and dungeons (gloom-and-glow). Gross content only in the Plaguewell (section 7).
- **Octopath = craft cues only.** No Square Enix assets, characters, jobs, logos, UI, "Sacred Flame" copy or maps (no Timberain / Atlasdam / Clockbank layouts). No copied pixels from anywhere.
- **Portals:** draw them fresh in the game's palette. `/workspace/gravewake/style/rift_refs` (swirling vortexes, stone-arch gates, flame ring, wall vortex) is a **style reference only**: never trace or copy pixels, never modify Gravewake or other projects.
- **Reject:** "cozy Stardew but 3D", a flat 16×16 world, photoreal cottages with a pixel sticker, a 3D skinned player mesh, soft-filtered sprites.
- **Enforced by:** `hd2d check-sprite` (alpha, palette, outline, frames, size, feet anchor) and `hd2d check-scene` (sprite sharpness, camera lock, no bloom, height, colours, grades, effects sharpness, phone, actions). Both must pass.

---

## 3. Platform and input requirements

**Target:** web first (static three.js r160 ES modules, no build step, WebGL2), played on phones, desktop and TV. Installable PWA. **Google Play** is a later target (e.g. a TWA wrapper), not now. **Online multiplayer is optional, not required**; don't let it shape the core architecture.

| Requirement | Status |
|---|---|
| Touch: floating joystick under the thumb, tap-to-walk (A*), pinch = camera zoom, left-handed flip | Built |
| Touch action buttons (attack / guard / jump), touch targets ≥ 30 px, safe-area aware, HUD inside viewport | Targets/layout built; **action buttons not built** |
| Controller (Bluetooth/USB, Gamepad API standard mapping), hot-plug toast, pad hides while in use | Built (stub-tested only) |
| Keyboard + mouse: WASD/arrows, Shift run, click-to-walk, wheel zoom | Built |
| All three schemes work at the same time | Built |
| No page scroll or zoom (gesture, double-tap, pull-to-refresh, ctrl+wheel, long-press blocked; `touch-action: none`) | Built |
| Input blocked while loading (`#boot` gate swallows all input until first frames) | Built |
| Fullscreen button | **Not built** (manifest already uses `"display": "fullscreen"` for the installed app) |
| Display presets: **Auto, Phone landscape, 720p, 1080p TV, Retro 320x240** (+ aspect options), sprites keep integer pixel scale | **Not built** |
| "Rotate your phone" prompt | **Not built** |
| In-game **Install** button (`beforeinstallprompt`) + an **iPhone "Share → Add to Home Screen"** tip (iOS has no install prompt) | **Not built** (PWA manifest, icons and offline service worker exist) |
| Controller button remap, non-standard pads | Not built |

---

## 4. Story

### 4.1 Setting
- **Nine Realms** linked by the **Rainbow Rift**. Norse-inspired, public-domain folklore; all art and characters original.
- **Inciting threat:** a villain from one realm is trying to start a civil war among the realms. The war first erupts among mortals in Ravenhold.
- **Core mechanic (kept from the earlier "Rootfall" seed, Bill's favourite):** opening and closing portals changes how the game plays out.
- Earlier pitches (The Dimming, The Rootfall, Lantern of the Eight Winds) are superseded by this direction. Keep their **theme loves**: mushrooms, gnomes, hidden bubbly springs, night cycles, neon-pulsing wisps and fireflies, torches casting shadows, orb lanterns with glowing fish.

| Realm | Theme / unique magic | City |
|---|---|---|
| Midgard | home (hearth/earth) | Hearthmoor (village), Ravenhold (capital) |
| Asgard | light, thunder, runes | Goldspire |
| Vanaheim | nature, growth, foresight, healing | Mossbrook |
| Alfheim | light elves, wisps, prism light | Lumenvale |
| Jotunheim | frost and stone giants, strength | Stonehollow |
| Svartalfheim / Nidavellir | dwarves, forge, crafting | Anvildeep |
| Muspelheim | fire | Cinderhold |
| Niflheim | ice, mist, water | Mistmere |
| Helheim | the dead, dark magic | Gloamhaven |
| (between realms) | the Rainbow Rift | Bifrost Crossing (portal capital) |

### 4.2 Villain: Veyra Ashmantle, the Rift-Warden (Niflheim)
- Last of Niflheim's frost-witches, who guarded and stabilized the Rainbow Rift.
- **Backstory:** the Rift cracked in a fire/ice skirmish. Muspelheim blamed Niflheim, Asgard sided with fire, and Niflheim was cut off to freeze. Her sister died in the collapse (her grave is in Mistmere).
- **Goal:** prove the realms' unity is fake by making them destroy each other, then seize the Rift and remake the nine realms into one frozen, ordered kingdom.
- **Methods (= befriend quest hooks):** poisons Vanaheim's springs and plants Alfheim runes; steals a dwarven artifact and plants it on the giants; corrupts temples to frame neighbours. Her agents also work inside Bifrost Crossing.
- Each befriend quest undoes a frame-up and becomes **evidence against her**. Conquering realms advances her plan, and she taunts you.
- **Combat:** frost/mist illusion clones, freezes portals shut, turns realm guardians. Final battle on the **freezing Rainbow Rift**. Her lieutenant **Kael Frostfang** (frost vampire) is the Niflheim dungeon boss.
- Befriending Niflheim may unlock a late **redeem-vs-defeat** choice.

### 4.3 Conquer vs befriend
- **Conquer:** kill your way through. The realm becomes a permanent enemy; its companions, crafted treasures and spells are closed off.
- **Befriend:** quests that still involve fighting and problem-solving: clear an evil spirit, restore a polluted spring, return a missing egg, recover a stolen artifact, cleanse a temple.
- Companions are recruited from befriended realms.

### 4.4 Alliance map

| Rival pair (befriend one, the other turns hostile) | Ally gives |
|---|---|
| Alfheim vs Svartalfheim | light magic + wisp companion / forge, crafted treasures + dwarf smith companion |
| Muspelheim vs Niflheim | fire + salamander companion / frost-mist + frost-witch companion + Veyra redemption path |
| Asgard vs Jotunheim | thunder/runes + valkyrie-style companion / stone-frost strength + gentle giant companion |

- **Swing realm:** Vanaheim (growth/healing, gnome or moss-folk companion). An Asgard ally makes it harder (old Aesir–Vanir war); a Jotunheim ally makes it easier.
- **Neutral:** Helheim is never ally or enemy: a dangerous pass-through, dark magic at a cost. Fallen allies go there, and one can be won back.
- **Midgard** is the home hub; Hearthmoor's look changes with your alliances.
- **Cap:** **max 4 allies out of 7** (one per rival pair + Vanaheim), so **at least 3 enemies**, whom Veyra rallies for the finale.
- **Entrances:** allied realms open freely; neutral realms need a key quest; hostile realms must be fought through (a guarded gate or a cracked side portal).

### 4.5 Main branch: Saver or Breaker (Veyra recruits you mid-game)
- **Rift-Saver:** undo her frame-ups, unite the realms, defeat or redeem her on the frozen Rift. Ultimate weapon: Riftsplitter.
- **Rift-Breaker:** help her sabotage (poison, steal, frame). You gain dark/frost powers and Veyra as a companion; betrayed realms become enemies. Late choice: crown her, or betray her and take the Rift. Signature weapon: Hollow Crown Blade.
- **One late side-switch** is allowed, at the cost of allies plus permanent fury from one side.

### 4.6 Endings
Endings combine **origin + side + alliances**: **united realms**, **frozen kingdom**, **Veyra redeemed**, **you rule the Rift**. Getting an ending on both paths unlocks the secret hero Riftborn (section 6).

### 4.7 Quest types

| Type | Effect | Examples |
|---|---|---|
| Story | required; advances the war with Veyra | realm arcs, frame-up reveals, finale |
| Ripple | optional but changes the story (allies, companions, pets, endings, weakening Veyra) | expose a Veyra spy (realm friendlier); save an ambassador (opens their portal early); on Veyra's side, help a smuggler (city guard turns on you); the Gnome Council picks a side; win a nephilim ally |
| Side | rewards only, no story effect | errands, minigames, collections |

Optional quests are never required, but many change the story. Bill loves all the quest styles proposed.

---

## 5. World

**Flow:** Hearthmoor → Ravenhold → Bifrost Crossing → the realms.

### 5.1 Midgard
- **Hearthmoor:** small home village outside Ravenhold. Farms, bakery, Pudding the cat. Its look changes with your alliances. (The current prototype's Plaza, Bakery Lane and Mossglen glade live here.)
- **Ravenhold:** Midgard's great mortal capital, on terraces at the foot of the Rainbow Rift; traders from friendly realms set up stalls. Veyra's civil war first erupts here. Its portal leads to Bifrost Crossing.

| Ravenhold district | Notes |
|---|---|
| Harbor | Rift Corsairs' base (outlaw faction) |
| Market Terraces | — |
| Forge Quarter | — |
| Old Temple | — |
| Undercity | sewers and hidden springs; entrance to the Plaguewell Sewers dungeon |

### 5.2 Bifrost Crossing (portal capital, built on the Rainbow Rift)
- Nine portal gates ring a central plaza. Each realm has an **embassy quarter** whose mood follows your alliances (allied = festivals and shops; hostile = boarded up, patrols).
- Optional quest hubs: **Gatekeepers' Guild** (portal repairs unlock shortcuts), **Wayfarer's Market** (befriend merchants, rare shops), **Stray Den** (adopt and swap pets), **Tavern of Nine Tables** (realm rumours, side quests, minigames), **Veyra's agents** in the city (expose them or help them; pushes the Saver or Breaker path).

### 5.3 Realm cities (one minor city per realm)

| Realm | City | Look | Signature activities |
|---|---|---|---|
| Asgard | Goldspire | hall-city | rune-smithing trial; sky-horse to tame |
| Vanaheim | Mossbrook | mushroom village, bubbly hidden springs | gnome friends, spring buffs, moss-pup pet |
| Alfheim | Lumenvale | glowing treetops, neon wisps | wisp catching; orb lantern with glowing fish |
| Jotunheim | Stonehollow | giant-scale town | gentle-giant friendship chain; goat mount |
| Svartalfheim | Anvildeep | cavern forge city | crafted treasures; mechanical pet |
| Muspelheim | Cinderhold | lava terraces | fire-salamander pet; ember-forging contest |
| Niflheim | Mistmere | frozen lake, Veyra's home | her sister's grave; redemption path unlock |
| Helheim | Gloamhaven | lantern-lit spirit town | ghost stories; win back a fallen ally; dark magic tomes |

Every realm city gets the dark/night gloom-and-glow look. Keep every city's story as written. Every city also offers several faction activities (section 9).

### 5.4 Travel and entrances
- First entry to a realm follows the alliance rule (allied free, neutral = key quest, hostile = fight through a guarded gate or cracked side portal).
- Fast travel: rune waystones (section 9.7); Bifrost gates between realms are free for allied realms and need keys otherwise; Gatekeepers' Guild discounts.
- Area changes fade; portals are walk-in swirls (as in the prototype's moss gate).

---

## 6. Heroes, magic, summons, pets

**Rules:** everyone casts spells. Brawlers are spellcasting fighters (Thor types, paladins, dark/death knights). Summons come from each hero's background, leaning elemental and magical (mushroom folk too).

### 6.1 Six starting heroes (pick 1; each has starting magic and a realm bias)

| Class (`role` id) | Origin | Style | Magic | Summons | Realm bias | Sprite read |
|---|---|---|---|---|---|---|
| Wildcaller (`wildcaller`) | Midgard farmhand, mortal | caster | hearth/earth: seed bombs, root snares, warm healing light; a gnome mentor teaches tricks | mushroom golem, glow-beetle swarm | learns any magic faster; neutral everywhere | blond mop, rust tunic, satchel, long hoe |
| Runeguard (`runeguard`) | Shield-warden (Hearthmoor guard), mortal | paladin brawler | light runes on the shield: charge, block, slam | radiant spirit shield-maiden, rune sentinels | best fighter; Jotunheim respects you | chestnut braids, mail, round rune shield, axe |
| Seer (`seer`) | Rune-reader (village seer), mortal | caster | runic traps, teleport sigils, foresight, brief time-stop | orbiting rune-wisps, stone-rune elemental | reads Veyra's planted clues more easily | grey hood with back rune, rune staff |
| Stormborn (`stormborn`) | Child of thunder, demigod | Thor-type brawler | hammer melee, chain lightning, thunder leap, storm clouds | storm elementals, sky-ram | Asgard friendly, Jotunheim hostile | broad build, storm-blue cloak, circlet, stone hammer |
| Grovekeeper (`grovekeeper`) | Child of the Vanir, demigod | caster | growth/heal/spore: thorn walls, bloom heals, poison puffs | treant, neon wisps, mushroom folk | Vanaheim and mushroom folk friendly | moss hair, flower crown, leaf mantle |
| Cinderknight (`cinderknight`) | Ember-born, demigod | dark-knight brawler | greatsword fire and shadow: ember slash, flame aura, life-drain | fire elementals, ash-shade knights | Muspelheim friendly, Niflheim hostile; Veyra resents you | broad dark plate with ember seam, greatsword |

### 6.2 Nine secret heroes (New Game+ unlocks; 6 + 9 = **15 heroes**)

| Realm | Hero | Concept | Magic | Summons | Unlock |
|---|---|---|---|---|---|
| Asgard | Valkyr | winged spear-knight | light/thunder | spirit ravens | win Goldspire's rune trial without taking a hit |
| Vanaheim | Sporewarden | gnome-raised mushroom druid | spore | spore giants, glow-caps | find every hidden spring |
| Alfheim | Prismdancer | light-elf blade dancer | neon prism | mirror wisps | catch every rare wisp |
| Jotunheim | Frostbrute | young giant brawler | stone/frost | ice golems | finish the gentle-giant friendship chain |
| Svartalfheim | Tinkerforge | dwarf/gnome engineer | forge | clockwork constructs | build a legendary crafted treasure |
| Muspelheim | Pyreheart | fire-giant monk | fist and flame | magma elementals | win the ember-forging contest |
| Niflheim | Mistwalker | Veyra's former apprentice | frost/mist | ice spirits | finish the redemption path |
| Helheim | Gravelight | returned death knight | dark | elemental shades | win back a fallen ally |
| Bifrost | Riftborn | rare hidden hero | mixes all schools | portal beasts | get any ending on both the Saver and Breaker paths |

Secret heroes have no sprites yet.

### 6.3 Magic schools
- **Base:** elemental, light and dark, plus a unique magic per realm.
- **Learned from allied realms (mix freely):** Niflheim frost (ice golems, frost spirits); Helheim dark (elemental shades, bone-raven; at a cost, since Helheim is neutral); Alfheim light (prism wisps); Svartalfheim forge (clockwork constructs); Vanaheim growth. Asgard (thunder/runes), Jotunheim (stone/frost strength) and Muspelheim (fire) give their spells through Realm Embassies.
- **Rift-Breaker path:** adds Veyra's frost-shadow magic and darker summon variants.
- Conquered realms close off their spells.

### 6.4 Companions
From befriended realms: wisp (Alfheim), dwarf smith (Svartalfheim), salamander (Muspelheim), frost-witch (Niflheim), valkyrie-style (Asgard), gentle giant (Jotunheim), gnome or moss-folk (Vanaheim). Veyra joins on the Breaker path. A fallen ally can be won back in Helheim.

### 6.5 Gnomes
Wise trickster tinkerers hidden across the realms: riddles, trades, pranks. Kindness earns tinkered upgrades (a summon slot, spell mods, pet gadgets); cheating them brings hexes or gnome golems. The **secret Gnome Council** picks a side in the war (major ripple quest) and is also a faction (section 9).

### 6.6 Pets
One active pet; it follows you, lights areas and gives an aura buff. Swap at the Stray Den.

| Pet | Ability |
|---|---|
| Lantern moth | lights caves, reveals hidden doors |
| Wisp kit | neon pulse, slow mana regen, night light |
| Glowfish orb | water lantern with a fish; heal over time, underwater breathing |
| Ember salamander | warmth aura (frost-slow immunity), lights torches |
| Snow hare | speed aura, finds hidden snow paths |
| Moss-pup | sniffs out herbs, mushrooms, hidden springs |
| Rift fox | senses portals, opens small secret portals |
| Gloam raven | sees invisible spirits, reveals Veyra's agents |
| Mechanical pet (Anvildeep) | named in the city list; ability not designed yet |

Pets also drop rarely from rare monsters and come from the Order of the Hearth and the Glimmerdeep.

---

## 7. Enemies and bestiary

**Tone rules**
- Elemental-first. Vampire lords and **sinister overlord demons** (horns, crowns, armour); **no creepy/slimy demons**.
- Every boss and elite is gloom-and-glow: dark armour, glowing eyes and runes, nothing gross.
- **Gross content (maggots, blood, putrid grossness) appears only in the Plaguewell Sewers** (the disease dungeon). Everywhere else, flesh and blood golems are stitched hulks with glowing rune seams and pulsing crimson cores, never gross.
- Glow colour language: blue cold fire = frost, wraiths, liches; violet = Alfheim, Helheim, gloam undead; red = vampires, demons, blood golems.

### 7.1 Per realm

| Realm | Regular | Elite | Boss |
|---|---|---|---|
| Asgard (Goldspire) | light wraiths, storm sentinels, storm-centaur lancers (sky plains) | Gilded Inquisitors (fallen paladins) | **Aurelion**, light-drinking vampire lord, ex-royal guard |
| Vanaheim (Mossbrook) | rot treants, spore elementals, moss golems | Thornhexes | **The Blight Regent**, corrupted nature lord |
| Alfheim (Lumenvale) | prism shards, neon will-o-wisps, crystal golems | Mirror Duelists | **Lady Sylvaine**, elf vampire queen, drains magic, neon violet |
| Jotunheim (Stonehollow) | frost trolls, avalanche golems, stone/ice golems | Rime Berserkers | **Hrimgard the Unthawed**, ancient dead giant king |
| Svartalfheim (Anvildeep) | rogue forge constructs, soot elementals, stone golems | Shadowsmiths | **Gorrak Ironmaw**, demon forge-tyrant bound into his armour |
| Muspelheim (Cinderhold) | magma hounds, flame elementals, fire golems | Ashen Cultists | **Vharzul the Ember Throne**, horned overlord demon, crown of fire |
| Niflheim (Mistmere) | frost spirits, mist stalkers, ice golems | Veyra's Ice Wardens | **Kael Frostfang** (frost vampire lieutenant), then **Veyra** (finale on the frozen Rift) |
| Helheim (Gloamhaven) | shades, grave lanterns, bone elementals, blood golems, skeleton lines | Gloam Knights | **Mordrath, the Pale Sovereign**, soul-hunting demon king |
| Midgard / the Rift | rift-spawn, storm elementals | Rift Corsairs (pirates) | secret superboss **Nihrax the Hollow Crown**, demon overlord sealed beneath the Rift |

### 7.2 Golems and elementals (Bill loves golems of all types): one golem + matching elemental per element

| Element | Where |
|---|---|
| Stone | Jotunheim, Svartalfheim |
| Ice | Niflheim, Jotunheim |
| Fire | Muspelheim |
| Lightning | Asgard (also the Clockwork Deep, Storm Rift) |
| Blood | Helheim, vampire lairs (Bloodmoon Rift) |
| Flesh | Veyra's cult experiments (Plaguewell, Ruin Rift) |
| Moss | Vanaheim |
| Crystal | Alfheim |

Gnome golems (gnome hexes) and the Glimmerdeep's dancing golem are extra variants.

### 7.3 Skeleton lines (each tier evolves from the previous one)

| Line | T1 | T2 | T3 | T4 (elite / mini-boss) |
|---|---|---|---|---|
| Caster | Skeleton Mage | Wizard | Priest | **Lich** (phylactery / soul-jar hunt quest to kill for good) |
| Melee hybrid | Skeleton Swordsman | Warrior | Death Knight | **Death Lord** |

- Liches and Death Lords command lower tiers. Most common in Helheim and Veyra-held ruins.
- Bone + dark armour, glowing eye sockets and rune etchings; colour by realm: frost blue (Niflheim), ember (Muspelheim), gloam violet (Helheim).

### 7.4 Wraiths (a Bill favourite)
Light (Asgard), storm, frost / blue cold fire (Niflheim, Frostfire Rift), gloam (Helheim). Elder wraiths and lost wraith legions appear as rares and rift "old evils".

### 7.5 Angels, nephilim, archangels (morally grey)
- **Angels:** radiant sentinels of the old Rift order; some guard the realms, some judge every realm as unworthy. Gold-white wings, halo runes, faceless glowing masks. Fallen angels appear in the Gilded Reliquary and the Storm Rift.
- **Nephilim:** half-angel outcast giants with cracked halos and one glowing wing. Enemies, mercenaries, or a ripple-quest ally.
- **Archangels (mega bosses / optional superbosses, late game or New Game+):** **Seraphex the Final Verdict** (wants to purge all nine realms; final boss of the Celestial Citadel) and an **Azrael-style Reaper of the Rift** (working name, not final). Dark-gold armour, blazing halos, burning eyes.
- Asgard's light wraiths and Gilded Inquisitors secretly serve the archangels.

### 7.6 Vampires and demons
Vampire lords: Aurelion, Lady Sylvaine, Kael Frostfang, Bloodmoon Rift vampires. Overlord demons: Gorrak Ironmaw, Vharzul, Mordrath, Nihrax, Bloodmoon demon lords. Red neon is their glow (Sylvaine is violet, Kael frost blue).

### 7.7 Elves, nymphs, mythic creatures
- **Elves:** light-elf rangers (Alfheim), dark-elf assassins (Svartalfheim); friend or foe by alliance.
- **Nymphs/dryads:** spring nymphs at hidden springs, Vanaheim dryads; friendly when allied, **corrupted thorn-nymphs** if not.
- **Centaurs:** storm-centaur lancers on Asgard's sky plains.
- **Mythic:** frost wyrms, fire drakes, Fenrir-style dark wolves, valkyrie spirits, draugr, Midgard-serpent spawn (on the Rift), griffins.
- **Glimmerdeep lore creatures:** will-o'-wisps, kelpies, fae tricksters, mushroom folk, giant glowing snails, a riddling sphinx, gnome pranksters, a moonlit Kirin.

### 7.8 Bestiary
A monster book with a **hunt log** tracking which rares and mini-bosses you've beaten.

---

## 8. Dungeons and rifts

### 8.1 Static dungeons (hand-built, fixed bosses and set loot)

| # | Realm | Dungeon | Theme | Enemies | Boss |
|---|---|---|---|---|---|
| 1 | Asgard | The Gilded Reliquary | Heaven | fallen angels, Gilded Inquisitors | Aurelion |
| 2 | Vanaheim | The Rotwood Hollow | Decay and rot | rot treants, spore elementals | The Blight Regent |
| 3 | Alfheim | The Prism Vault | Energy / light | prism shards, Mirror Duelists | Lady Sylvaine |
| 4 | Jotunheim | The Titan's Barrow | Giant land | frost trolls, giant golems | Hrimgard the Unthawed |
| 5 | Svartalfheim | The Clockwork Deep | Techno-mage / steampunk | forge constructs, lightning golems | Gorrak Ironmaw |
| 6 | Muspelheim | The Ember Caldera | Fire | magma hounds, fire golems | Vharzul the Ember Throne |
| 7 | Niflheim | The Frozen Spire | Ice | frost wraiths, ice golems | Kael Frostfang |
| 8 | Helheim | The Ossuary of Whispers | Ghost and undead | skeleton lines, liches | Mordrath |
| 9 | Midgard | The Plaguewell Sewers (under Ravenhold's Undercity) | Disease (+ acid pools): maggots, blood, putrid grossness; **the only gross dungeon** | flesh and blood golems | the Plague Matron |

### 8.2 The two hardest dungeons

| Dungeon | Where | Themes | Enemies | Final boss |
|---|---|---|---|---|
| **The Abyssal Throne** (major underworld) | beneath the Rift | Hell + Death + Darkness | demon overlords, Death Lords | Nihrax the Hollow Crown (drops the Hollow Crown Blade) |
| **The Celestial Citadel** (major overworld) | above the Rift | Heaven + Life + Energy | angels, nephilim | archangel Seraphex the Final Verdict |

### 8.3 The Glimmerdeep (optional mythical dungeon, location TBD)
- Pitch-dark caverns lit by glowing mushrooms and cave moss: gloom-and-glow whimsy.
- Creatures: will-o'-wisps, kelpies, fae tricksters, mushroom folk, giant glowing snails, a riddling sphinx, gnome pranksters.
- **Silly:** talking mushrooms, a dancing golem, a cheese-obsessed troll, a reversed-gravity room.
- **Genuinely hard bosses:** the Mycelium Mother, the Moonlit Kirin, the Gnome King's clockwork dragon.
- Optional completion with special rewards: a unique pet, a cosmetic set, legendary gear.

### 8.4 Procedural dungeons
- Seeded room-and-corridor layouts using each realm's tile kit; random rooms, traps, secrets and hidden springs. Replayable for merit. They draw from all themes.

### 8.5 Procedural rares and under-bosses
- **Formula:** base monster + **element affix** (blue cold fire / violet / red neon) + **one trait** (e.g. Shielded, Splitting, Summoner, Blinking, Enraged).
- Spawn randomly in every realm's overworld and inside rifts (e.g. a glowing golem variant, a lone lich, an elder wraith). Some appear only at night or in certain weather.
- **Tell:** name plate + distinct neon glow + a sound cue.
- **Rewards:** merit for the faction of the realm you're in, decent gear, crafting materials, a small chance of a rare cosmetic or pet. Logged in the hunt log.

### 8.6 Random rift events
- Open randomly in every realm. Warning: a crack in the sky, a cold-fire glow, a rumble.
- Inside: a short **pocket dimension** of "old evils" aligned with no faction (ancient horrors, forgotten gods' remnants, rogue golems, lost wraith legions).
- **Reward:** merit to the faction of the realm you're in, **plus** Gatekeepers' Guild Rift Marks. This is on top of quests, bounties and other activities.
- Rifts close if ignored and are harder at night.

| Tier | Content |
|---|---|
| Minor | quick clear |
| Major | mini-boss |
| Abyssal (rare) | boss + legendary crafting-material drop |

### 8.7 The five rift types

| Rift | Enemies | Glow |
|---|---|---|
| Frostfire | blue cold-fire wraiths, ice golems, frost liches | blue |
| Gloam | shades, skeleton lines, death knights | violet |
| Bloodmoon | vampires, blood golems, red-neon demon lords | red |
| Storm | lightning golems, storm elementals, fallen angels and nephilim | blue/white |
| Ruin | ancient stone and flesh golems, forgotten-god relics, mixed old evils | mixed |

- **Rift bosses:** drawn from a shared random pool, plus a few fixed signature bosses per rift type (named in section 11).
- **Future rift theme pool (undesigned):** Acid, Plague, Heaven, Hell, Steam.
- Portal and rift art: drawn fresh from the rift_refs style.

### 8.8 Loot tables (three layers)
1. **Shared base table:** gold, materials, common gear.
2. **Semi-shared themed tables** per rift type and per realm: themed gear, element materials.
3. **Small unique drops** per fixed boss.
Drop rarity scales with rift tier, rares and bosses (section 9.4).

### 8.9 Theme coverage

| Theme | Covered by |
|---|---|
| Ice | Frozen Spire, Frostfire Rift |
| Fire | Ember Caldera |
| Darkness | Abyssal Throne |
| Death | Abyssal Throne |
| Energy / electricity | Prism Vault, Celestial Citadel, Storm Rift |
| Decay and rot | Rotwood Hollow |
| Disease | Plaguewell Sewers |
| Heaven | Gilded Reliquary, Celestial Citadel |
| Hell | Abyssal Throne |
| Techno-mage / steampunk | Clockwork Deep |
| Giant land | Titan's Barrow |
| Ghost and undead | Ossuary of Whispers, Gloam Rift |
| Acid | **partial** (acid pools in the Plaguewell only) |
| Life | **partial** (side theme of the Celestial Citadel only) |
| Nature | **missing** (no dungeon; Vanaheim's became decay) |

---

## 9. Progression and economy

### 9.1 Factions (five overall; realm cities also sell local gear when you're allied)

| Faction | Base | Currency | Earned by | Rewards |
|---|---|---|---|---|
| Gatekeepers' Guild | Bifrost Crossing | Rift Marks | closing rifts, escorts, portal repairs | portal keys, fast travel, rift-forged gear, travel discounts |
| Order of the Hearth | Midgard | Hearth Tokens | defending villages, errands | home upgrades, pets, Hearthmoor armour |
| Gnome Council (secret) | hidden | Gilded Acorns | hidden springs, gnome riddles | trickster gadgets, mushroom gear, rare charms, cheap socket clearing, safe-deposit box |
| Rift Corsairs (outlaw) | Ravenhold Harbor | Black Doubloons | smuggling, raids | pirate gear, Breaker-path tools |
| Realm Embassies (one per allied realm) | Bifrost embassy quarters | Realm Favor | each realm's quests | realm spells, companions, the realm's legendary weapon quest |

### 9.2 Merit ranks and pacing (merit must feel earned)
- **Six ranks per faction:** Stranger → Friend → Trusted → Honored → Champion → Legend. Each rank takes roughly **3–5 meaningful activities**. **Legend** unlocks the faction's legendary item/quest.
- **Activity sources (every city offers several):** faction quest chains (big merit), rotating bounty board (elite hunts), rift closures and dungeon clears, rescue and escort, gathering/crafting orders, hidden-spring and secret finds, arena or trial challenges, night-only events.
- **Extra sources:** random rifts and random rares give merit to the faction of the realm you're in.
- **Costs:** gear costs scale with rank; the best gear needs **both rank and currency**, so players mix activities instead of grinding one. Small daily/weekly bonuses, **no paywalls**.
- **Rival tension:** Corsair merit lowers Order of the Hearth standing (and similar pairs).

### 9.3 Legendary weapons (each with a quest chain)

| Source | Weapon | Description |
|---|---|---|
| Asgard | Stormcaller | neon-blue thunder hammer |
| Vanaheim | Mossheart Staff | summons a spore giant |
| Alfheim | Prism Edge | violet blade that dances on its own |
| Jotunheim | Rimebreaker | giant's frost axe |
| Svartalfheim | Anvilsoul | living forge gauntlet |
| Muspelheim | Emberfang | red-flame greatsword |
| Niflheim | Coldflame Lantern | blue cold-fire staff |
| Helheim | Gloamreaver | violet soul scythe |
| Bifrost | Riftsplitter | rainbow-light spear, ultimate Saver-path weapon |
| Nihrax drop | Hollow Crown Blade | cursed sword, Breaker path |

### 9.4 Rarity tiers (armour, weapons, trinkets)

| Tier | Colour | Extras |
|---|---|---|
| Common | white / grey | base |
| Uncommon | green | + bonus stats |
| Rare | blue | + more stats / affixes |
| Epic | purple | faint glow on the sprite |
| Legendary | orange / gold | animated neon aura + a unique effect |

Item names and loot beams match the tier colour. Rarer drops come more often from bigger rifts, rares and bosses. Glows follow the no-bloom rule.

### 9.5 Upgrades, rerolls, sockets
- **Upgrade:** +1 to +10 at forges with found or bought materials. The cap is set by rarity, so a Common can't out-scale a Legendary.
- **Reroll:** rune stones (world, rifts, faction shops) reroll **one bonus stat at a time**; lock a stat for extra cost; limited rerolls per item.
- **Sockets:** 1–3 by rarity. Gems, runes and cores give special shields (frost barrier, ember ward, light aegis), on-hit effects (chain lightning, life drain, cold-fire burn) and auras. Golem cores and rift shards are high-tier socketables. A jeweler clears sockets (cheaper through the Gnome Council).

### 9.6 Bank and merchants
- **Bank:** one shared vault across all cities, expandable tabs, gold storage, a materials bag. Gnome Council safe-deposit box for rare items.
- **Merchants:** city shops with realm stock, rotating rare traders, a sell-back / buyback tab, faction vendors, a traveling night-only merchant, and the Wayfarer's Market at Bifrost.

### 9.7 Fast travel
Rune waystones in every city and district, unlocked by visiting. Bifrost gates between realms: allied realms free, others need keys (Gatekeepers' Guild portal keys; Guild discounts). Portal repairs unlock shortcuts.

### 9.8 Mounts
Realm-themed: storm stag, moss boar, frost elk, ember lizard, griffin (late game), plus the Goldspire sky-horse (tamed) and the Stonehollow goat mount. Earned through faction ranks, rares or quests. Mounts glow at night.

### 9.9 Housing
- **Inn rooms** for rent in every realm city: rest, storage, save.
- **Homes** to buy: Hearthmoor cottage, Ravenhold townhouse, Bifrost tower suite. Upgradeable and decoratable, each with a pet corner and a trophy wall.

---

## 10. Current build status (as of commit `7b6031e`, 2026-10-02)

### 10.1 Live

| What | URL |
|---|---|
| Repo | https://github.com/unclebill-spec/hd2d-suite |
| Pages index | https://unclebill-spec.github.io/hd2d-suite/ |
| Hearthmoor | https://unclebill-spec.github.io/hd2d-suite/games/hearthmoor/ |
| Plaza demo | https://unclebill-spec.github.io/hd2d-suite/demos/hearthmoor-plaza/ |
| Bakery Lane demo | https://unclebill-spec.github.io/hd2d-suite/demos/bakery-lane/ |

Pages serves `main` at the root; pushing to `main` redeploys. Keep every game path relative (the site lives under `/hd2d-suite/`).

### 10.2 Toolset (`bin/hd2d <tool>`, Python 3.13 + Pillow + numpy; Node 20 for `trees`; Playwright + Chromium for checks)

| Command | Does |
|---|---|
| `palette` | 5 biomes × 27 colours + day/dusk/night grades |
| `sprite` | 20x32 pixel actors, 30 roles (24 villagers/animals + 6 heroes); `--roles heroes`, `--lineup`, `--anim-lineup [--anim-facing]` |
| `check-sprite` | atlas QA (alpha, palette, outline, frames, size, feet) |
| `runtime` | copies the three.js r160 diorama engine |
| `texel` | 32/64 px palette-snapped world textures |
| `kit` | town + glade .glb pieces (cottages, bakery, inn, stalls, fountain, portal arch, shrine, standing stones, mushroom ring…) |
| `trees` | layered-card trees (+ low-poly option) |
| `particles` | 16 presets (fireflies, embers, rain, snow, dust…) |
| `spells` | 9 pixel spell effects + cast sets |
| `portal` | portal vortex, portal ring, moonpetal, quest tags |
| `assemble` | scene JSON → playable static folder + zip |
| `check-scene` | headless visual/phone/action QA |
| `serve` | static server for a built folder |

The shared engine lives in `tools/runtime/web/`; change it there, then copy into `demos/*/engine` and `games/hearthmoor/engine` (`games/hearthmoor/build.py` does the game).

### 10.3 Demos
`demos/hearthmoor-plaza` (terraced square), `demos/bakery-lane` (two terraces, bakery, inn, fountain, 7 NPCs), both with zips.

### 10.4 Game (`games/hearthmoor/`, a cozy errand prototype, not yet the Nine Realms game)
- **Areas:** Hearthmoor Plaza, Bakery Lane, Mossglen (glade through a stone-arch moss portal). Specs in `areas/src/*.json`, built by `build.py`.
- **Content:** 3 errands (Warm Bread, Moonpetal Tea, Where's Pudding?), linear parchment dialogue with portraits, quest log, bag, Pudding the cat follows you, charms as rewards (F cast, Q switch).
- **Systems:** real-time day/dusk/night (12-minute day, saved), procedural WebAudio, A* tap-to-walk, PWA (manifest `display: fullscreen`, icons, offline service worker, ~12 MB precache).
- **Save:** localStorage key **`hearthmoor-slot-1-v1`** (one slot; `?reset` clears it). Other keys: `hearthmoor-mute`, `hd2d-hand`.
- **Player role in the code is `hedgewitch`** (a caster villager role with idle/walk/cast only), not a hero class and not the traveler.
- **QA URL params:** `?qa&area=plaza|lane|mossglen`, `?reset`, `?nosw`, `?day=SECONDS`, `?simscale=N`, `?pad=1`, `?hand=left`, `?t=day|dusk|night`, `?freeze`.
- Restore kit and do-not-regress list: `games/hearthmoor/RESTORE.md`. Zip: `games/hearthmoor.zip`.

### 10.5 Hero sprites (`tools/sprite/roles_heroes.py`)
- Six classes: `wildcaller`, `runeguard`, `seer`, `stormborn`, `grovekeeper`, `cinderknight`. 24-column strips, 4 facings (right = mirrored left).

| Anim | Cols | Frames |
|---|---|---|
| idle | 0–3 | |
| walk | 4–7 | |
| cast | 8–11 | gather, raise, release, recover (every class has its own glow) |
| attack | 12–15 | wind-up, swing, impact, follow-through (class weapon) |
| defend | 16–19 | raise, set, hold a, hold b (engine loops 2/3 while held) |
| jump | 20–23 | crouch, launch, airborne, land (runtime adds the 0.55 m arc; shadow stays on the ground) |

- Lineups: `docs/screenshots/hero_origins_4x.png`, `hero_anims_4x.png`, `hero_anims_side_4x.png`, `hero_anims_up_4x.png`, in-scene `hero_origins_plaza.png`. Review scene: `scenes/hero-classes-plaza.json` (player = stormborn).

### 10.6 Controls today

| Action | Keyboard / mouse | Controller (standard mapping) | Touch |
|---|---|---|---|
| Walk / run | WASD / arrows, Shift runs, click to walk | left stick (full tilt runs), d-pad | floating stick, tap to walk |
| Talk / advance | E / Space / Enter | A | tap NPC |
| Close / cancel | Esc | B | tap |
| Cast charm / next / prev | F / Q | X / Y, RB / LB | ✦ tap / hold |
| **Attack** | **R** | **RS** (right stick click) | not built |
| **Guard** | **C** (hold) | **LT** (timed 0.8 s guard) | not built |
| **Jump** | **Z** | **LS** (left stick click) | not built |
| Zoom | wheel, + / − | LT / RT | pinch |
| Quest log | J / L | Start | ☰ |
| Save | K / Ctrl+S | — | save chip |
| Pad / left hand | G / H | Select (pad) | chips |
| Other | M sound, T next time, P pause clock | | |

Runtime API: `Actors.act(a, name, {hold, dur})` / `release(a, name)` in `engine/sprites.js`; QA: `window.__hd2d.act / release / actorState / actAdvance`.

### 10.7 Checks (must pass before pushing code)
`bin/hd2d check-sprite …`, `bin/hd2d check-scene` on both demos and all 3 game areas (commands in `AGENTS.md`), and `python3 games/hearthmoor/tests/smoke.py` (46 steps, ~8 min). Last run: all PASS (2026-10-02). Headless only (Chromium + SwiftShader); run one browser job at a time.

### 10.8 Known gaps
- **No class picker**; the game player is still the hedgewitch, so the six heroes aren't playable in the game (only in the review scene).
- The game/demo atlases weren't regenerated, so in the game only **jump** (a hop on idle frames) works; R and C do nothing there.
- **No touch action buttons** (attack/guard/jump are keyboard + controller only).
- **Moves are visual only:** no hitboxes, damage, HP, enemies or AI. **No combat system chosen.**
- Controller **LT is double-mapped** (analog zoom-out and the 0.8 s guard) and guard on a pad is timed, not held.
- **Not built:** display presets, fullscreen button, rotate prompt, in-game Install button + iPhone tip, controller remap.
- **No real-device or real-GPU test** (headless + emulated phones only); controller only stub-tested; audio never listened to.
- **The player can hide behind buildings** (no see-through silhouette).
- Linear dialogue (no choices), one save slot, single-path errands, NPCs without schedules, pathfinding ignores moving NPCs.
- Plaza and Lane reuse the demo layouts; backdrop hills are simple domes; wards hidden from behind (`up` facing).
- None of sections 4–9 is implemented yet beyond the Hearthmoor village and one portal.

---

## 11. Decisions (made by the storyboarding agent at Bill's request, 2026-10-03)

These answer the former open questions. They are binding for the build unless Bill changes them.

1. **Combat style: real-time action RPG.** Attack, guard, jump, and a dodge roll, plus 4 spell slots and a summon button. On phone, holding the spell button opens a slow-time spell wheel. Fits the existing R/C/Z animations and touch/controller/keyboard support. No turn-based mode.
2. **Glimmerdeep location:** a secret entrance behind a hidden bubbly spring in **Ravenhold's Undercity**, opened by finishing the **Gnome Council** ripple chain. Available any time after you reach Ravenhold; optional completion.
3. **Nature dungeon:** add **The Verdant Heart**, a living-forest dungeon in Vanaheim (nature + life: dryads, moss golems, life elementals, healing springs). It opens after you cleanse the Rotwood Hollow. Boss: **Hjortur the Greenheart**, an elder stag-king. On the befriend path he's a guardian trial; on the conquer path he's corrupted and fought to the death. Vanaheim now has two dungeons (10 realm dungeons total).
   - **Acid:** gets its own rift type (below) and the **Caustic Mire** wing of the Plaguewell Sewers.
   - **Life:** home in the Verdant Heart and the Celestial Citadel.
4. **Rift types.** The five starters are available from the start; five more unlock after your first Abyssal Rift.

| Rift | Enemies | Glow | Signature bosses |
|---|---|---|---|
| Frostfire | cold-fire wraiths, ice golems, frost liches | blue | Ysolde of the Pale Brazier (cold-fire lich queen) |
| Gloam | shades, skeleton lines, death knights | violet | The Hollow Choir (a chorus of fused wraiths) |
| Bloodmoon | vampires, blood golems, demon lords | red | Countess Varra Crimsonveil (vampire countess); the Blood Colossus |
| Storm | lightning golems, storm elementals, fallen angels, nephilim | blue-white | Thundermaw (lightning golem titan); Azkar the Oathless (fallen nephilim) |
| Ruin | ancient stone and flesh golems, old-god relics | amber | The Forgotten Idol (god-golem) |
| Acid (later) | caustic elementals, acid golems, corroded knights | toxic green | The Corrosion Wyrm |
| Plague (later) | maggot swarms, flesh golems, plague-bearers (gross allowed, like the Plaguewell) | sickly green-red | The Rotting Bishop |
| Heaven (later) | angel sentries, light wraiths, Gilded Inquisitors | gold-white | Auriel the Unblinking (throne angel) |
| Hell (later) | demon legions, ember knights, chained hounds | red | Malgrim the Chain-Lord (overlord demon) |
| Steam (later) | clockwork constructs, steam elementals | brass and blue | The Brass Leviathan |

Rift bosses still also draw from the shared random pool.

5. **Factions: keep five overall.** Each realm city has a quartermaster who sells local gear under its Realm Embassy, so cities still feel distinct without extra factions.
6. **Smaller names and items**
   - Reaper archangel: **Morriel, the Last Toll**.
   - Legend-rank faction rewards: Gatekeepers' Guild **Keyless Rune** (open any Bifrost gate, even a hostile one, once a day); Order of the Hearth **Hearthstone Mantle** (armor set; recall home anytime, one revive per dungeon); Gnome Council **Gnome King's Pocket Engine** (summons a clockwork gnome squad and reveals secrets); Rift Corsairs **Black Sail Cutlass** plus a **Rift-skiff** mount that sails the Rift.
   - Mechanical pet (Anvildeep): **Tick, a clockwork owl.** Marks nearby hidden springs, chests and secret doors, with a loot-find aura.
   - Companions: Asgard **Sigrun Stormwing** (valkyrie); Jotunheim **Ulfar Mossback** (gentle giant); Alfheim **Lumi** (wisp spirit); Svartalfheim **Dagna Coalbeard** (dwarf smith); Muspelheim **Kindle** (ember salamander); Niflheim **Hrefna Frostveil** (frost-witch); Vanaheim **Tobble Capwhistle** (gnome); Helheim **Old Corwin** (lantern-ferryman shade, by key quest); Breaker path **Veyra**.
   - Fast travel: the agent's earlier reading is now the rule. After your first entry, gate fast travel needs a key unless the realm is allied.
7. **Ravenhold's Forge Quarter, Old Temple and Market Terraces** get detail later, during the Midgard slice storyboard.

---

## 12. Suggested build order and repo rules

### 12.1 Milestones (suggested; each ends with checks green, CHANGELOG entry and push)

| M | Goal | Key work |
|---|---|---|
| 0 | Platform polish | display presets (Auto / Phone landscape / 720p / 1080p TV / Retro 320x240, integer sprite scale), fullscreen button, rotate prompt, Install button + iPhone Add to Home Screen tip, fix the LT double-map, player see-through silhouette when occluded |
| 1 | Heroes in the game | title-screen class picker (6 starters), chosen class as player, regenerate game atlases with hero anims, touch buttons for attack/guard/jump (left-hand aware), save the class in the slot (bump the save version with migration) |
| 2 | Combat core (real-time action, see section 11) | hitboxes, HP, damage, guard, enemy AI, one golem + one wraith + one skeleton, death/respawn, per-class first spell and summon, action VFX in the spells atlas |
| 3 | Midgard slice | Hearthmoor reframed for the Nine Realms, Ravenhold (start with 1–2 of the 5 districts), dialogue choices, multiple save slots, story quest 1 |
| 4 | Bifrost Crossing + first realm | portal hub, embassy mood, alliance state (befriend/conquer, rival lockouts, max 4 allies), one realm city (e.g. Mossbrook), its static dungeon and boss |
| 5 | Loot and economy | rarity tiers, inventory, bank, merchants, factions + merit ranks, upgrades/rerolls/sockets, waystones |
| 6 | Random content | random rifts (3 tiers, 5 types), procedural rares (affix + trait), procedural dungeons, hunt log |
| 7 | Remaining realms | the other realm cities and dungeons, companions, pets, mounts, housing |
| 8 | Endgame | Saver/Breaker branch, side-switch, endings, the Abyssal Throne, the Celestial Citadel, Glimmerdeep (once placed), New Game+ secret heroes |
| 9 | Ship | real-device and real-controller tests, performance on phones, Google Play packaging later; online multiplayer only if Bill asks |

### 12.2 Repo rules (from `AGENTS.md`; binding)
1. **`git pull` first**, every time you resume.
2. Keep **`CHANGELOG.md`** (dated America/New_York, newest first) and **`AGENTS.md`** current with every push.
3. **Descriptive commits:** `area: what changed and why`.
4. **Secret scan before every push**, on the files **and** the history: rg regexes for gh/ghp_/gho_/github_pat_ tokens, AWS/Google keys, private keys, password/token assignments and `.env`/credential files, plus **gitleaks** on the tree, the staged changes and the git history. If anything real turns up, don't push; report it.
5. Run the checks and the smoke test before pushing code; they must pass.
6. Original IP only; follow the style lock; never modify Gravewake or other projects.
7. Keep game paths relative (Pages lives under `/hd2d-suite/`). Don't break the do-not-regress list in `games/hearthmoor/RESTORE.md`.
8. Story changes go into `docs/story/STORY_SEEDS.md` (via the storyboarding agent / Bill) and then this file.
9. Replies to Bill: brief.

---

## Appendix A: resolved contradictions

| Topic | Earlier draft | Resolution used here |
|---|---|---|
| Direction | Three pitches (Dimming, Rootfall, Eight Winds) | Norse Nine Realms (chosen 2026-10-01); kept the portal open/close mechanic and the theme loves |
| Farmhand magic | "Midgard farmhand: no magic, learns any magic faster" | Later "everyone casts": Wildcaller has hearth/earth magic; kept "learns any magic faster, neutral everywhere" as the bias |
| Static dungeon count | "1–2 per realm city region" | Master list: one per realm (9) + 2 hardest + Glimmerdeep |
| Flesh/blood golems | "never gross" | Never gross everywhere **except** the Plaguewell, which Bill explicitly made gross (disease theme) |
| Storm Rift | chat summary: "fallen angels" | Story file: fallen angels **and** nephilim |
| Theme coverage | Story file says all themes appear | Nature has no dungeon; acid and life are partial (flagged in section 11) |
| Niflheim boss | "bosses Kael Frostfang, then Veyra" | Kael ends the Frozen Spire; Veyra is fought in the finale on the frozen Rift |
| Nihrax | "secret superboss sealed beneath the Rift" | Same boss is the final boss of the Abyssal Throne (beneath the Rift) |
| Rift types | early list plus later theme pool | Five types stand (Frostfire, Gloam, Bloodmoon, Storm, Ruin); Acid/Plague/Heaven/Hell/Steam are an undesigned future pool |
| Allies | — | Max 4 of 7 (one per rival pair + Vanaheim); Helheim neutral; Midgard home |
| Mounts | city list (sky-horse, goat) vs mount list (stag, boar, elk, lizard, griffin) | Both kept |
| Gate access | entrances (neutral = key quest, hostile = fight) vs fast travel (non-allied = keys) | First entry follows the alliance rule; gate fast travel then needs keys unless allied |
| Game player role | `AGENTS.md`: "the player is still the traveler" | Code: `hedgewitch` in all three areas (`areas/src/*.json`); AGENTS.md corrected |
| Controller guard | docs: "LT short guard" | Code: LT also zooms out (analog); flagged as a gap |
