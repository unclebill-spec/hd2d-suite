# Hearthmoor design expansion (2026-10-03)

New design approved for development by Bill on 2026-10-03: the opening hour, main quest beats, leveling and skill trees, death/difficulty/New Game+, day/night and weather, Ravenhold's remaining districts, and music and sound.

- Builds on `docs/story/STORY_SEEDS.md` and `docs/HEARTHMOOR_BUILDER_HANDOFF.md` (including the section 11 decisions: real-time action combat with dodge, 4 spell slots + summon, slow-time spell wheel on phone, the Verdant Heart, 10 rift types, companion and NPC names). Where this file adds detail, it doesn't change anything already decided.
- The same seven sections are appended to `STORY_SEEDS.md`. They are **not yet merged into the builder handoff**; that happens at the end of the session.
- Section numbers use an **E** prefix (E1–E7) so they don't clash with the handoff's numbering.

## E1. Opening hour: Hearthmoor before the Rift cracks

**Goal:** about 60 minutes of cozy village life that teaches every control, then the Rift cracks on the festival night and you leave home. The current prototype's areas (Plaza, Bakery Lane, Mossglen), cast (Marla, Tib, Grandpa Alder, Wren, Bram of the Kettle & Key, Sorrel, Pudding) and its three errands become this opening.

### E1.1 Setting: Lantern Eve
- It is **Lantern Eve**, Hearthmoor's harvest festival. At dusk the whole village floats **orb lanterns with glowing fish** up toward the Rainbow Rift, which hangs over Ravenhold on the horizon like a faint aurora.
- Day 1 is warm and golden. The hour runs from morning to festival night on one compressed day (the clock is scripted here; the free cycle starts after you leave home).

### E1.2 Tutorial beats
| # | Time | Beat | Teaches |
|---|---|---|---|
| 1 | 0–5 min | Origin opening scene (E1.3) | move (floating stick / WASD / left stick), camera zoom, talk |
| 2 | 5–10 | Walk to the Plaza; Grandpa Alder asks you to help get the village ready for Lantern Eve | quest log, waystone (the Plaza's rune stone is the first waystone) |
| 3 | 10–25 | Three festival errands, any order: **Warm Bread** (Marla → Bram), **Moonpetal Tea** (Wren wants moonpetals from Mossglen), **Where's Pudding?** (Tib's cat) | errands, bag, item pickups, area exits, the Mossglen moss portal |
| 4 | 25–30 | In Mossglen, tremors knock a **moss golem** loose from the shrine steps; it's dazed, not evil. Sorrel asks you to calm it | **first fight**: attack combo, lock-on, enemy tell (the golem glows before a slam) |
| 5 | 30–35 | The golem's slam and root shockwaves | **guard** (block the slam), **dodge** (roll through the shockwave; costs stamina, i-frames), **jump** (over a root ripple and onto a mossy ledge) |
| 6 | 35–40 | Sorrel lights the shrine and wakes your magic | **first spell** in slot 1 (class starter spell); slots 2–4 shown locked; phone: hold the spell button for the **slow-time spell wheel** |
| 7 | 40–45 | A second, angrier golem; Sorrel: "call a friend" | **first summon** (class summon, tier I), summon button |
| 8 | 45–50 | Return Pudding / deliver items; Grandpa Alder gives you a **lantern moth** (first pet; lights the path, shows a hidden door to a tiny bubbly spring in Mossglen) | pets, hidden springs, healing at springs |
| 9 | 50–55 | Lantern Eve at dusk: release lanterns, music, fireflies | night look, saving at the inn (Kettle & Key room) |
| 10 | 55–60 | **The inciting event** (E1.4) | fight in the dark under pressure, using everything |

Tutorial prompts appear once, in the parchment hint line, for the input scheme you're using (touch, controller or keyboard). Every tutorial fight can be retried instantly; you can't fail the opening.

### E1.3 Origin opening scenes (one per starter, about 5 minutes, then everyone meets at the Plaza)
| Hero | Where you wake | Scene | Starter spell / summon | Foreshadowing |
|---|---|---|---|---|
| **Wildcaller** (farmhand) | the family farm at dawn | Your gnome mentor, **Fennick Burrowhat**, pops out of a turnip row and teaches you to plant a seed bomb to scare off a pack of glow-moles raiding the mushroom beds | seed bomb / mushroom golem | Fennick mutters that the gnomes have felt "a crack in the deep roots" |
| **Runeguard** (Shield-warden) | the Hearthmoor gate at the end of the night watch | Captain **Halla Greaves** drills you on shield blocks; at dawn you see blue cold fire flicker in the hills where no one should be | shield rune charge / spirit shield-maiden | a giant's boot-print near the wall; Halla says Jotunheim's giants once honored Hearthmoor's wardens |
| **Seer** (Rune-reader) | your cottage, waking from a foresight dream of the Rift freezing solid | You read the standing stones in Mossglen and find a freshly carved **Alfheim rune** that doesn't belong | runic trap / rune-wisps | first planted clue: Veyra's frame-ups; only the Seer notices it this early |
| **Stormborn** (Child of thunder) | the hilltop above the Plaza in a dawn thunderstorm | A storm-raven brings a message from your Asgard parent ("the bridge is weakening"); lightning hits your hammer and you practice thunder strikes on old stones | chain lightning / storm elemental | villagers note giants hate your kind; a Jotunheim trader glares at you later |
| **Grovekeeper** (Child of the Vanir) | the Mossglen shrine with Sorrel | A spring nymph shows you the glade's moonpetals are wilting; you bloom them back with Vanir magic | bloom heal / neon wisps | the spring water tastes faintly of frost and rot (Veyra's poison will hit Vanaheim later) |
| **Cinderknight** (Ember-born) | the smithy, ember seam glowing in your sleep | Frost flowers creep over the forge and snuff your embers; you relight it with an ember slash while the smith keeps a wary distance | ember slash / fire elemental | villagers are nervous around fire-blood; Veyra's frame-up lands on you hardest |

All six then take the same Plaza beats (E1.2 #2 onward). NPC lines shift slightly by origin (e.g. Marla gives the Cinderknight extra bread "to show you're welcome").

### E1.4 The inciting event: the Rift cracks
- At the height of Lantern Eve, a deep boom: the **Rainbow Rift splits** with a jagged seam of **blue cold fire** across the sky. The floating lanterns freeze mid-air and fall like hail.
- **Frost wraiths** and **rift-spawn** pour down the Mossglen portal and into the Plaza. You defend the village in the dark: lamps out, only cold-fire glow, your spell light and the fallen fish lanterns.
- After the fight, the villagers find a **Muspelheim ember-sigil** dropped by the attackers, so Hearthmoor blames the fire realm (the first frame-up; the Seer can read that the sigil is fake).
- For one beat, a tall silhouette with **cold blue eyes** stands in the crack above Ravenhold, then vanishes. Nobody knows who it is yet.
- Hearthmoor's own small portal (the moss gate) goes dark. The only way forward is the road to Ravenhold, where the crack is worst.

### E1.5 Leaving home
- Morning after. Grandpa Alder gives you his old **Rift-warden's lantern charm** ("my grandmother walked the bridge once"): this is your key to Ravenhold's Rift-gate later.
- Marla packs **hearthloaves** (the first healing item); Wren gives **Moonpetal tea** (cleanses frost slow); Bram gives you a pass for an inn room in Ravenhold.
- Pudding stays home with Tib (Hearthmoor always has her by the fountain, and she visits your cottage if you buy it).
- The Order of the Hearth's local warden asks you to carry word to Ravenhold: your first faction contact (rank Stranger → Friend comes quickly here).
- Walk the north road at golden hour. Title card: **HEARTHMOOR**. Act 1 begins.

---

## E2. Main quest beats

### E2.1 Act overview
| Act | Where | Length (main path) | Level band | Ends with |
|---|---|---|---|---|
| Prologue | Hearthmoor | ~1 h | 1–5 | the Rift cracks; leave home |
| Act 1 | Midgard / Ravenhold | ~5–7 h | 5–15 | the Plaguewell; the Rift-gate opens to Bifrost Crossing |
| Act 2 | Bifrost Crossing + the realms | ~20–30 h | 15–40 | Veyra's reveal and the Saver/Breaker choice (midpoint), then the alliance cap fills |
| Act 3 | everywhere: the civil war | ~8–12 h | 40–50 | the betrayal, the siege of Bifrost, the side-switch window |
| Finale | the frozen Rainbow Rift | ~1–2 h | 50 | one of four endings |
| Post-game | open | — | 50 (cap) | hardest dungeons, superbosses, New Game+ |

### E2.2 Prologue (E1)
Lantern Eve, the crack, the false ember-sigil, the blue-eyed silhouette, leaving home.

### E2.3 Act 1: Midgard and Ravenhold
1. **Arrival.** Ravenhold is in uproar: realm traders on the Market Terraces are fighting (fire vs frost stalls), the Harbor is locked down, and refugees from cut-off villages crowd the Old Temple.
2. **District beats** (see E6): help the Forge Quarter, the Old Temple and the Market Terraces; meet the Rift Corsairs at the Harbor (the first chance to lean outlaw).
3. **Frame-up #1, the Cold Altar.** The Old Temple's sacred cold-fire brazier goes out and dwarven forge tools are found at the altar; the city blames the Forge Quarter and riots start. Prove it's a setup (Seer reads it instantly; others follow clues).
4. **Veyra's first appearance.** As the riot boils over, a frost-witch in grey-blue robes calmly seals a breaking rift above the temple: **Veyra Ashmantle, the Rift-Warden**. She's gentle, sad and convincing, and says she's trying to hold the Rift together alone. She asks you to find who's poisoning Ravenhold's water. She is **not revealed as the villain yet**.
5. **The Plaguewell Sewers.** The poison leads into the Undercity and the Plaguewell: a cult lab of flesh-golem experiments. Boss: **the Plague Matron**. Her notes mention "the Warden's design", but they're half burned; it reads like the cult works against Veyra.
6. **The Rift-gate.** With Grandpa Alder's lantern charm, the Old Temple's Rift-gate opens to **Bifrost Crossing**. End of Act 1.

Optional in Act 1: the Gnome Council ripple chain (opens the **Glimmerdeep** behind a hidden spring in the Undercity), Corsair smuggling, Order of the Hearth village defence.

### E2.4 Act 2: Bifrost Crossing and the realms
- **Bifrost Crossing:** meet **Guildmaster Aud Rainholt** of the Gatekeepers' Guild and her deputy **Gatewright Halvard Ness**, who becomes your helpful contact (remember him). Embassy quarters, Stray Den, Tavern of Nine Tables, Wayfarer's Market open.
- **Realm order is free.** Each realm arc: arrive (allied/neutral/hostile entry rules) → city → frame-up or local crisis → **befriend** (quests that undo the frame-up and become evidence) **or conquer** → realm dungeon.
- **The three big frame-ups** (from the story file) are spread across realms:
  - **Poisoned springs:** Vanaheim's springs poisoned with Alfheim runes planted (Rotwood Hollow; afterwards the Verdant Heart opens).
  - **Stolen artifact:** a dwarven artifact (the **Anvil-Heart**) stolen from Anvildeep and planted in Stonehollow.
  - **Corrupted temples:** temples in Goldspire and Cinderhold corrupted to frame each other.
- **Veyra between realms:** after each realm resolves she appears briefly, approving if you befriended ("you mend what others break") and taunting if you conquered ("you're doing my work for me").
- **Midpoint reveal (after your 3rd realm is resolved):** the evidence from every undone frame-up points to Niflheim. At **Mistmere**, by her sister's grave, Veyra drops the act: she tells her backstory (the fire/ice skirmish, Asgard siding with fire, Niflheim left to freeze, her sister's death) and admits she set the realms against each other. **Kael Frostfang** stands behind her.
- **The choice (Saver or Breaker):** Veyra asks you to join her.
  - **Rift-Saver:** refuse. Kael attacks; you escape. Veyra is now openly hostile.
  - **Rift-Breaker:** accept. Veyra becomes a companion; you get her frost-shadow school; your remaining realm arcs flip to sabotage (poison, steal, frame), and betrayed realms become enemies.
- **Rest of Act 2:** finish more realms until the **4-ally cap** fills (or you've conquered/betrayed the rest). Helheim (neutral) is a pass-through at any time; Gloamhaven's key quest opens it.
- **Frozen Spire (Niflheim):** Saver: Kael defends it as Veyra's fortress. Breaker: Kael, jealous of you, challenges you to a duel there. Either way he's the boss.

### E2.5 Act 3: the civil war escalates
1. **War breaks out.** Veyra rallies the (at least 3) hostile realms. Ravenhold is besieged; Hearthmoor's look darkens (boarded windows, cold-fire watch braziers) or brightens if your allies send help.
2. **The betrayal.** **Gatewright Halvard** was Veyra's agent all along. He freezes Bifrost Crossing's gates from the inside, trapping the embassies.
   - Saver: you fight through the frozen Crossing to reopen the gates (the **Siege of Bifrost**).
   - Breaker: you are the one who hands Halvard the gate keys; the betrayal is yours, and the Crossing falls to Veyra.
3. **A fallen ally.** In the siege, your **first recruited companion falls** (if you have none, Captain Halla Greaves). They go to Helheim; winning them back at Gloamhaven is optional (and unlocks Gravelight for New Game+).
4. **The Rift splits wide.** The war tears the Rift open above and below, revealing the **Celestial Citadel** (above) and the **Abyssal Throne** (below). Both are optional and very hard (E2.7).
5. **The side-switch window: "Eve of the Frozen Rift."** One last time at Mistmere, by the grave, you can switch sides **once**:
   - Cost: you lose your newest ally realm (it won't follow a turncoat) and the side you leave keeps **permanent fury** (its hunters stalk you in every realm and some vendors close for good).
   - Saver → Breaker: Veyra takes you back, coldly; Breaker endings only.
   - Breaker → Saver: you betray Veyra early; Saver endings only, and **"Veyra redeemed" is locked** (she'll never trust you again).
6. **March to the frozen Rift.** Allies muster at Bifrost; the Rift freezes as Veyra begins remaking the realms.

### E2.6 Finale and endings
- **Saver finale:** fight up the freezing Rainbow Rift through turned realm guardians, then **Veyra**: frost/mist illusion clones, portals frozen shut mid-fight, a final phase on a bridge of ice above the void.
- **Breaker finale:** defend the frozen Rift against the realm host led by **Guildmaster Aud Rainholt** (and any realm champions you betrayed), then face Veyra at the crown of ice and make the last choice.

| Ending | Path | How you reach it |
|---|---|---|
| **United realms** | Saver | beat Veyra and choose to defeat her (or redemption conditions not met). Allied realms rebuild the Rift together |
| **Veyra redeemed** | Saver | befriended **Niflheim**, finished the **Mistmere redemption path** (her sister's grave quest), didn't switch from Breaker to Saver; beat her, then choose to spare her. She becomes the Rift's warden again, for real |
| **Frozen kingdom** | Breaker | win the defence, then **crown Veyra**. The nine realms become one frozen, ordered kingdom; you're her right hand |
| **You rule the Rift** | Breaker | win the defence, then **betray Veyra** (final duel) and take the Rift yourself |

- **Epilogue slides** change by **origin** (e.g. the Wildcaller goes home to the farm with gnome friends; the Cinderknight is welcomed back at the smithy or feared), by **alliances** (each realm city's fate), and by Hearthmoor's state.
- Riftborn unlocks after any ending on **both** paths (across playthroughs).

### E2.7 Where the big optional content fits
| Content | Opens | Recommended | Notes |
|---|---|---|---|
| **Glimmerdeep** | Act 1+, after the Gnome Council ripple chain | any time; its bosses scale to you | silly and hard; unique pet, cosmetic set, legendary gear |
| **Verdant Heart** | after cleansing the Rotwood Hollow (Vanaheim) | Act 2 | Hjortur the Greenheart: guardian trial (befriend) or corrupted fight (conquer) |
| **Abyssal Throne** (hardest, underworld) | Act 3, when the Rift splits | level 50, before or after the finale | ends with **Nihrax the Hollow Crown**; drops the Hollow Crown Blade (Breaker weapon, usable by anyone) |
| **Celestial Citadel** (hardest, overworld) | Act 3, when the Rift splits | level 50, before or after the finale | ends with **Seraphex the Final Verdict**, who judges the realms whichever side you chose |
| **Morriel, the Last Toll** (reaper archangel) | New Game+ only | NG+ | hidden bell tower atop the Celestial Citadel |
| **Riftsplitter** | Bifrost quest chain, finishes in Act 3 | Saver | the ultimate Saver weapon; best used in the finale |

The game saves after the finale and returns you to the world (post-game) so you can clear what's left.

---

## E3. Leveling and skill trees

### E3.1 Levels and XP
- **Level cap 50** on the first playthrough; **New Game+ raises it by 10 per cycle, to a maximum of 70**.
- **XP sources:** enemies (elites and rares give big bonuses), story and ripple quests (largest), side quests, faction activities, rift closures (by tier), dungeon first clears, discovering hidden springs, waystones and secrets, bestiary entries (first kill of each type), and festival events. No XP loss on death.
- **Realm scaling:** because realm order is free, Act 2 realms scale to your level within their band (15–40), so the world never feels empty or impossible.

### E3.2 Stats
| Stat | Does |
|---|---|
| **Might** | melee damage, guard break |
| **Arcana** | spell damage, mana pool |
| **Spirit** | summon power and duration, healing done |
| **Vigor** | max HP, status resistance |
| **Grit** | armour, block strength, stamina cost of guarding |
| **Swiftness** | stamina, dodge distance, attack speed, crit chance |

- **Derived:** HP, Mana, Stamina (dodge, guard, sprint), Crit, Summon Cap (one summon active; capstones add a second small one).
- Stats grow automatically by class each level, plus **2 free stat points per level** for players who want to tune. Gear, sockets and pets add the rest.

### E3.3 Skill points and trees
- **1 skill point per level** plus about 15 bonus points from trials, shrines, hidden springs (all of them) and Legend faction ranks: about 64 points by level 50.
- Each starter class has **3 branches × 8 nodes** (some multi-rank, about 40 ranks per class tree). You can max one branch and most of a second, or spread out. Capstones need 20 points in that branch.
- **Equip limit:** 4 spell slots + 1 summon. On phone, the slow-time spell wheel shows the 4 slots plus quick-swap to 4 more.

| Class | Branch | Example nodes | Capstone |
|---|---|---|---|
| **Wildcaller** | **Hearth** (healing light) | warm healing light, hearth aura (regen near you), hearthloaf heals double, ember-warm (frost resist) | **Hearth Bloom**: a warm field that heals allies and wards off frost |
| | **Root** (control) | seed bomb splits into three, root snare, bramble wall, earthquake stomp | **Old Root Wakes**: giant roots erupt and hold every enemy in an area |
| | **Gnomecraft** (summons, tricks) | mushroom golem II/III, glow-beetle swarm size, pocket gnome decoy, gnome trick (steal a buff) | **Grand Mushroom Golem**: a towering glowing golem that throws spore boulders |
| **Runeguard** | **Bulwark** (defence) | perfect-guard reflect, shield bash stun, rune aegis (party shield), guard costs less stamina | **Unbreakable Wall**: a few seconds where nothing gets through your shield |
| | **Axe of Dawn** (melee) | rune charge, cleave, light-rune slam, combo finisher burn | **Dawnbreaker**: a leaping slam that explodes into a ring of light runes |
| | **Shield-host** (summons) | shield-maiden II/III, rune sentinel turrets, sentinels taunt, shield-maiden revives you once | **Hall of Shields**: shield-maiden plus two rune sentinels at once |
| **Seer** | **Runes** (traps) | rune trap chains, frost/fire/storm rune variants, trap auto-reseed, bigger rune circles | **Runestorm**: the ground fills with rune traps that detonate in sequence |
| | **Sigil-walking** (mobility) | teleport sigil, blink-dodge (replaces the roll), sigil swap with an enemy, longer time-stop | **Still Moment**: a 3-second full time-stop |
| | **Foresight** (crits, summons) | see enemy tells early, crit after a perfect dodge, rune-wisps II/III, stone-rune elemental II/III | **Eye of Threads**: briefly see every enemy's next move; every hit crits |
| **Stormborn** | **Thunderhand** (hammer) | hammer combo + chain lightning on hit, charged swing, armour shatter, thunder throw (hammer returns) | **Skybreaker**: a huge overhead smash that calls a lightning pillar |
| | **Tempest** (storm magic) | storm cloud follows you, thunder leap, static field slow, lightning golem resist | **Eye of the Storm**: a moving storm that strikes nearby enemies for 10 s |
| | **Skyherd** (summons) | storm elemental II/III, sky-ram charge, elementals chain to each other, ram knocks back | **Thunderherd**: a stampede of sky-rams across the screen |
| **Grovekeeper** | **Bloom** (healing) | bloom heal, healing spring (place a temporary bubbly spring), cleanse, overheal shield | **Spring Eternal**: a big glowing spring that heals and revives |
| | **Thorn and Spore** (damage/control) | thorn wall, spore puff slow, spore puff poison, thorn armour | **Sporestorm**: a swirling cloud of glowing spores that blinds and weakens |
| | **Grove Kin** (summons) | treant II/III, neon wisp swarm, mushroom folk squad, summons heal you | **Elder Treant**: a huge ancient treant that roots and shields allies |
| **Cinderknight** | **Ember Blade** (greatsword) | ember slash combo, flame aura, burning ground, charged overhead | **Cinderfall**: a leaping strike that rains embers in a wide arc |
| | **Ashen Shadow** (dark, drain) | life-drain on hit, shadow step (dodge through enemies), fear pulse, drain heals more at low HP | **Ash Wraith Form**: become a shadowy ember wraith for 8 s (immune to slows, drain everything) |
| | **Ash Legion** (summons) | fire elemental II/III, ash-shade knight, shades explode in embers, legion lasts longer | **Legion of Embers**: three ash-shade knights at once |

### E3.4 School spells from allied realms
- Each realm school is a **small 6-node school tree**, unlocked through that realm's **Realm Embassy** ranks: Friend = first spell, Trusted = second spell, Honored = school summon variant, Champion = passive, Legend = school mastery (plus the legendary weapon quest).

| School | Realm | Example spells | Summon variant |
|---|---|---|---|
| Thunder runes | Asgard | rune spear, sky lance | spirit raven |
| Growth | Vanaheim | vine grasp, bloom shield | moss golem |
| Prism light | Alfheim | prism beam, mirror double | prism wisps |
| Stone strength | Jotunheim | boulder toss, stone skin | stone golem |
| Forge | Svartalfheim | rivet volley, molten armour | clockwork construct |
| Fire | Muspelheim | fire wave, magma pool | magma hound |
| Frost | Niflheim | ice lance, frost nova | ice golem, frost spirits |
| Dark (at a cost) | Helheim (Gloamhaven tomes; neutral) | soul bolt, grave grasp (costs HP to cast) | elemental shade, bone-raven |
| Frost-shadow | Veyra (Breaker only) | shadow ice clones, freezing portal | darker variants of your summons |

- School spells go into the same **4 spell slots** as class spells, so you mix freely (e.g. a Cinderknight with Niflheim frost).
- Conquered realms close their school (as the story file says). Switching sides keeps learned spells but closes further ranks in schools tied to the side you left.

### E3.5 Summon upgrades
- One summon button; you pick which summon is equipped (class summons, school variants).
- **Tiers I → II → III** through tree nodes; tier III summons get a new attack and a visible glow upgrade.
- **Golem cores and rift shards** (high-tier socketables) can also be slotted into a summon's **core socket** for an element or effect (e.g. a frost core makes the mushroom golem freeze on slam).
- Summons fade if you faint and come back at the next waystone.

### E3.6 Respec
- **Free full respec** any time before level 10, and **once per act** for free after that.
- Otherwise, **Unwinding Tea** brewed by **Wren** (Hearthmoor) or any inn: full respec of skills and free stat points, for gold that rises with level. The Gnome Council sells a cheaper single-branch version.
- Single nodes can be refunded at any **hidden spring** shrine for a small fee.

### E3.7 Secret heroes
The nine secret heroes use the same system (3 branches, 4 slots, 1 summon) and start at your NG+ carry-over level. Each has one signature branch from their concept (e.g. Valkyr: **Wings**, flight-dash and dive; Tinkerforge: **Workshop**, turrets; Riftborn: **Rift**, borrowing a node from any other class). Trees are designed when their sprites are made.

---

## E4. Death, difficulty, New Game+

### E4.1 Fainting, not dying (cozy-friendly)
- At 0 HP you **faint**, the screen dims into a warm lantern glow, and you wake at the **last waystone, inn room or hidden spring** you rested at.
- **Penalty (Adventurer and up):** you drop **10% of your carried (unbanked) gold** as a glowing **ember purse** where you fainted. Walk back and pick it up; faint again first and the old purse fades. No XP loss, no item loss, no gear damage.
- Companions faint with you and return at the waystone. Your pet carries you home in the faint animation (the lantern moth glows, the snow hare drags you, Tick chirps, etc.): a small cozy touch.
- Inside dungeons, the **last dungeon checkpoint** (a cold-fire brazier you lit) is the respawn point.

### E4.2 Difficulty modes (changeable any time, except Saga)
| Mode | For | Combat | Penalty |
|---|---|---|---|
| **Story (Cozy)** | story and exploring | enemies deal 50% damage, guard and dodge timing more generous, auto-revive once per fight | none |
| **Adventurer** (default) | most players | as designed | 10% carried gold (recoverable) |
| **Hero** | action fans | enemies +40% damage, smarter AI, elites gain a trait | 20% carried gold (recoverable) |
| **Saga** (unlocks after any ending) | veterans | Hero values + extra boss phases, rares have 2 traits | 25% carried gold; can't lower difficulty in that save |

Rewards are the same in every mode except a small loot-quality bonus on Hero and Saga, plus a Saga-only cosmetic set.

### E4.3 Boss retry
- Fainting to a boss offers **Retry** (instant, at the boss door, full HP and mana, consumables used in the fight refunded) or **Return** (to the last waystone).
- After **3 failed attempts** on Adventurer or Hero, the game offers **Hearth's Blessing** (+20% defence for that boss; optional, no penalty, can be turned off).
- Boss music skips its intro on retries.

### E4.4 New Game+
- Starts after any ending, from the title screen (**New Game+** slot).
- **Carries over:** level, stats and skill points, gear, bank, gold, materials, housing (homes and decorations), pets, mounts, bestiary and hunt log, cosmetics, learned school spells (ranks above Friend must be re-earned), legendary weapons already forged.
- **Resets:** story, alliances and rival lockouts, faction ranks (you start at **Friend** instead of Stranger in every faction you'd reached Legend in), companions (recruit again), Veyra's state.
- **Scaling:** enemies +10 levels per cycle, rares and rifts spawn more often, Abyssal Rifts are more common, new rare traits, a higher level cap (60, then 70), and **Morriel, the Last Toll** appears.
- **Choosing a hero:** pick any of the 6 starters, or any **secret hero** you've unlocked. Your old hero's gear goes into the bank.

### E4.5 How secret heroes unlock
- Each unlock condition (story file list) can be met in **any playthrough**; it's saved to your **profile**, not the save slot.
- An unlocked hero appears as a portrait in the **Hall of Heroes**, a new room in the Hearthmoor inn, with a short hint for the locked ones ("A winged knight waits for a flawless trial in Goldspire").
- Unlocked secret heroes are selectable in **New Game+ and in any new game** started after your first ending.

---

## E5. Day/night and weather

### E5.1 Cycle
- **One full day = 24 real minutes** in the full game: day 12 min, dusk 3, night 7, dawn 2. (The prototype runs a 12-minute day; switch when the Midgard slice is built.)
- The clock pauses in menus, dialogue and dungeons that have no sky (they use their own fixed lighting).
- **Rest at an inn room or home** to skip to dawn, dusk or night. Some quests need a time of day.
- Every realm has its own look per time, following the style lock grades (warm gold day, cool blue dusk, orange windows at night) plus the realm's signature glow.

### E5.2 What changes at night
| Area | At night |
|---|---|
| **Enemies** | undead (skeleton lines, wraiths, draugr), vampires and shades come out; day creatures sleep; +2 levels and more elites |
| **Rares** | night-only rares and mini-bosses (e.g. an elder wraith, a lone lich, the Moonlit Kirin's echo) |
| **Rifts** | open more often, are **harder** (+1 trait on the boss) and drop better loot |
| **Merchants** | the **traveling night merchant** appears (rotating city); most day shops close; taverns and inns stay open |
| **Glow** | fireflies, neon wisps, glowing mushrooms, orb lanterns with glowing fish, **blue cold-fire torches and braziers**, glowing runes and portals; mounts glow |
| **Events** | night-only faction events (merit), wisp catching in Lumenvale, ghost stories in Gloamhaven |
| **Secrets** | some hidden springs and doors only show at night (moonlit ripples, glowing moss trails) |
| **Stealth** | Corsair smuggling runs and some Breaker sabotage work better at night (fewer guards) |

### E5.3 Weather by realm
| Realm | Weather | Gameplay effect |
|---|---|---|
| Midgard | sun, rain, fog, rare thunderstorm | rain: fire spells −15%, lightning +15%, puddles conduct lightning; fog: shorter enemy sight (easier sneaking) |
| Asgard | clear sky, thunderstorm | thunderstorm: random lightning strikes on open ground (avoid the glowing warning circle); storm spells +20%; storm-centaurs more common |
| Vanaheim | warm rain, spore drizzle | warm rain: slow HP regen outdoors; spore drizzle: glowing spores, spore elementals spawn, mushroom harvests double |
| Alfheim | aurora, prism rain | aurora: mana regen +; prism rain: light spells bounce once, Mirror Duelists can go invisible |
| Jotunheim | snow, blizzard | blizzard: visibility down, frost slow builds outdoors (warmth aura and Moonpetal tea counter it), snow hare finds hidden paths |
| Svartalfheim | soot fall, tremors (underground) | soot fall: lamps dim, soot elementals spawn; tremors: falling rocks, new cracks reveal ore and secrets |
| Muspelheim | ash fall, ember storm | ember storm: burning ground patches, fire resistance needed; ember salamander makes you immune |
| Niflheim | freezing mist, still frost | mist: mist stalkers invisible until close, frost spells +; still frost: lakes freeze into walkable ice bridges |
| Helheim | gloam fog, soul lights | gloam fog: shades get stronger; soul lights: wandering lights that lead to secrets (the gloam raven sees them clearly) |
| Bifrost Crossing / Rift | rainbow shimmer, rift storm | rift storm: rifts open nearby, Rift Marks +25% |

- Weather uses the existing particle presets (rain, splashes, snow, embers, petals) and fog/haze in the grade. **Never bloom.**
- Weather changes about every in-game day; some quests and rares need a specific weather.

### E5.4 Festivals and events
- An **in-game week** is 7 days. Each realm holds one festival a week (one day long), shown on a calendar in the quest log. Festivals only run in realms that are **allied or neutral** to you; hostile cities are boarded up.

| Realm / city | Festival | What happens |
|---|---|---|
| Midgard / Hearthmoor | **Lantern Eve** (also the opening) | float fish-orb lanterns, bread contest, Order of the Hearth merit |
| Midgard / Ravenhold | **Harbor Lights** | boat parade, Corsair races, night market on the Terraces |
| Asgard / Goldspire | **Thunder Moot** | rune trial tournaments, sky-horse races |
| Vanaheim / Mossbrook | **Bloomtide** | mushroom harvest, spring dances with nymphs, gnome riddle contest |
| Alfheim / Lumenvale | **Wisp Night** | rare-wisp hunt, neon lantern fair |
| Jotunheim / Stonehollow | **Stone-Toss Games** | giant-scale strength contests, goat races |
| Svartalfheim / Anvildeep | **Forgefire Week** | crafting contest, discount forging |
| Muspelheim / Cinderhold | **Emberfall** | the ember-forging contest, fire dancing |
| Niflheim / Mistmere | **Frost Vigil** | quiet lights on the frozen lake for the lost (ties into Veyra's sister); redemption-path scenes |
| Helheim / Gloamhaven | **Lantern-Boat Night** | float lanterns for the dead; ghost stories; a chance to speak with fallen allies |
| Bifrost Crossing | **Gate Day** | all embassies open, rare traders, Gatekeepers' Guild bonuses |

- **World events** (not weekly): rift storms (many rifts at once in one realm), blood moon (rare night: Bloodmoon rifts and vampires everywhere, red neon sky), star-fall night (wish-stones fall; Gnome Council trades them).

---

## E6. Ravenhold districts

Ravenhold sits on terraces at the foot of the Rainbow Rift: Harbor at the bottom, Market Terraces in the middle, the Forge Quarter on the east cliff, the Old Temple at the top with the **Rift-gate**, and the Undercity beneath all of it. Waystone in every district.

### E6.1 Consistency check (existing districts)
- **Harbor:** Rift Corsairs' base (Black Doubloons; smuggling and raids; the ripple quest where helping a smuggler on Veyra's side turns the city guard against you; Legend rank gives the Rift-skiff). Consistent; no change.
- **Undercity:** sewers and hidden springs; entrance to the **Plaguewell Sewers** (with the Caustic Mire wing) and the secret **Glimmerdeep** spring (Gnome Council chain). Consistent; the Plaguewell's gross content stays below the Undercity's grates, and the Undercity itself is gloom-and-glow (glowing moss, bubbly springs, gnome hideouts).
- **New link:** the Rift-gate to Bifrost Crossing is in the **Old Temple** (opened with Grandpa Alder's lantern charm at the end of Act 1).

### E6.2 Forge Quarter
- **Look:** a cliffside of stacked stone workshops and chimneys; forge mouths glow **red** and quench tanks steam with **blue cold fire** (dwarven technique). Chains, cranes and bellows; sparks as particles; at night the whole cliff glows.
- **Key NPCs:**
  - **Hilde Anvilsong**, master smith (human): upgrades +1 to +10.
  - **Orri Flintcog**, a dwarf exile from Anvildeep: socket work and rare forge recipes (friendlier if Svartalfheim is allied).
  - **Nettle Gearwhisk**, a gnome jeweler with a stall in a chimney nook: clears sockets cheap with Gnome Council rank.
- **Shops:** forge (upgrades, repairs to the look of gear), jeweler (sockets), smelter (ore to materials), armour and weapon stalls (Midgard stock), a rune-stone seller (rerolls).
- **Quests:**
  - **The Cold Altar** (story, Act 1): the Forge Quarter is blamed for the temple frame-up; prove the dwarven tools were planted.
  - **Bellows Down** (side): a rogue forge construct is stomping through the workshops; calm it or break it.
  - **Hilde's Masterwork** (ripple): help Hilde forge a Hearthmoor guard blade; if Ravenhold falls into riots, she arms the city guard on your side in Act 3.
  - **Stolen Quench** (Breaker-path ripple): steal cold-fire quench water for Veyra; the Forge Quarter's forges go dark until Act 3.

### E6.3 Old Temple
- **Look:** an ancient temple of the old Rift order at the top of the terraces: white stone gone grey, angel statues with faceless masks, **blue cold-fire braziers**, stained glass that throws violet and gold light at dusk. The **Rift-gate** (a stone arch with a rainbow vortex) stands in the inner court.
- **Key NPCs:**
  - **Mother Ilse Brightwater**, high priestess: keeps the sacred cold-fire brazier; runs the refugee shelter.
  - **Brother Tamsin**, a young archivist: lore, the bestiary, and old records of the Rift order (hints that the angels have their own agenda).
  - **Veyra** (Act 1 first appearance, sealing a rift over the temple).
- **Shops:** a healer (potions, cleansing), a chapel shop (charms, light-rune trinkets), the archive (lore books, maps of hidden springs).
- **Quests:**
  - **The Cold Altar** (story): the sacred brazier goes out; find the real culprits (Veyra's agents).
  - **Refuge** (side/faction): bring supplies to refugees for Order of the Hearth merit.
  - **The Faceless Statues** (ripple): the statues turn their masks toward the Rift at night; leads to the angel and nephilim storyline, and an early hint of the Celestial Citadel.
  - **Keeper of the Gate** (story): open the Rift-gate to Bifrost Crossing with Grandpa Alder's lantern charm.

### E6.4 Market Terraces
- **Look:** tiered bazaar terraces with awnings, bunting and hanging signs; stalls from every friendly realm (Alfheim neon lanterns, Vanaheim mushroom baskets, Muspelheim spice braziers, Niflheim ice-fish on frost slabs); orb lanterns with glowing fish strung between stalls; a big night market. Stall mood follows your alliances (allied realm stalls are busy; hostile ones are empty or vandalized).
- **Key NPCs:**
  - **Marketwarden Ottar Vane**: keeps the peace; gives bounties (bounty board).
  - **Fen Tallowby**, a cheerful little rare-goods trader with a cart of oddities: rotating rare stock.
  - **The Nine Keys Bank**, run by gnome clerk **Bix Coppertuft**: the shared vault (tabs, gold, materials bag); hints at the Gnome Council.
  - Realm traders, one per realm, as alliances allow.
- **Shops:** general goods, the bank, a buyback stall, realm stalls (local gear when allied), a stable (first mount: the **moss boar**, once Vanaheim's stall opens, or a plain Midgard pony as a placeholder until then), a pet stall (pointer to Bifrost's Stray Den), the night merchant (some nights).
- **Quests:**
  - **Fire and Frost Stalls** (story, Act 1 arrival): stop a brawl between Muspelheim and Niflheim traders; your choices nudge their realms' opinion of you.
  - **The Counterfeit Coin** (side): fake Black Doubloons in the market; track them to the Harbor.
  - **A Stall for Every Realm** (ripple, long): bring traders back as you befriend realms; a full market gives a festival and a unique home decoration.
  - **Gnome in the Vault** (Gnome Council chain start): Bix asks you to solve a riddle lock; the chain eventually opens the Glimmerdeep.

---

## E7. Music and sound style

### E7.1 Direction
- **Cozy Nordic folk chamber music with a gloom-and-glow shimmer:** warm acoustic instruments (lyre, fiddle, hurdy-gurdy drone, frame drum, recorder, music box) plus glassy, glowing timbres (celesta, glass harmonica, soft synth pads) for magic and night.
- 16-bit spirit, modern clarity: simple memorable melodies, clear bass, no wall-of-sound. It should sit nicely on a phone speaker.
- **Originality:** all music and SFX original. **No copied melodies, chord-progression clones or sampled audio from other games** (including Octopath/Square Enix), and no recognisable folk tunes copied note for note. Norse flavour comes from instruments and modes (Dorian, Aeolian, drones), not borrowed songs.
- **Today:** the prototype uses procedural WebAudio (soft pad, music-box plucks, birds, crickets, chimes) and nobody has listened to it yet. The full game can mix procedural layers and small compressed files; keep the PWA size budget in mind.

### E7.2 Leitmotifs
| Motif | Sound | Used in |
|---|---|---|
| **Hearthmoor** (home) | a warm 6-note lyre and music-box tune | title, Hearthmoor, the Order of the Hearth, the epilogue |
| **The Rift** | a rising 9-note arpeggio on celesta and harp (one note per realm) | Bifrost Crossing, portals, the Rift-gate |
| **Veyra** | a slow falling minor line on glass harmonica and frost bells, a lone wordless voice | her scenes, Mistmere, the finale; Saver plays it sorrowful, Breaker plays it triumphant |
| **Battle** | a driving frame-drum and fiddle figure | general combat, reharmonised per realm |

### E7.3 Per-realm mood and instruments
| Realm / place | Mood | Instruments |
|---|---|---|
| Hearthmoor | warm, gentle, safe | lyre, recorder, music box, soft strings |
| Ravenhold | bustling harbour city | fiddle, accordion-like reed, hand drums, gulls and bells; each district varies the arrangement (Forge: anvils in the rhythm; Temple: choir pads; Market: lively; Undercity: sparse drips and low drones) |
| Bifrost Crossing | wondrous, shimmering | harp, celesta, glass bells; the Rift motif |
| Asgard (Goldspire) | noble, grand, a little cold | horns, choir pads, timpani thunder rolls |
| Vanaheim (Mossbrook) | playful, bubbly, green | plucked strings, marimba bubbles, woodblock, whistles (gnome mischief) |
| Alfheim (Lumenvale) | dreamy neon | glass harmonica, celesta arpeggios, soft synth pads |
| Jotunheim (Stonehollow) | vast, slow, heavy | deep drums, low strings, horn calls, wind |
| Svartalfheim (Anvildeep) | busy, mechanical | anvil percussion, ticking clocks, bellows drone, steam hiss |
| Muspelheim (Cinderhold) | fierce, driving | frame drums, hurdy-gurdy, crackling fire texture |
| Niflheim (Mistmere) | lonely, beautiful, frozen | sparse piano-like plucks, frost bells, the Veyra voice |
| Helheim (Gloamhaven) | eerie but kind | slightly detuned music box, low choir hum, lantern chimes, a slow waltz |
| Glimmerdeep | whimsical and spooky | bassoon-like reed, pizzicato, kazoo-like silliness, deep cave drones; bosses turn serious |
| Plaguewell / Plague rift | queasy, tense | low drones, wet drips, unsettling slides; still listenable, never loud gore noise |

### E7.4 Layers (one track, layers fade in and out)
| Layer | Adds |
|---|---|
| **Explore** | base realm theme |
| **Alert** | (enemy notices you) pulse and percussion fade in |
| **Combat** | full drums, bass and the battle motif in the realm's key; drops back to explore 4 s after the last enemy |
| **Elite / rare** | a short signature sting, then combat plus a lead instrument in the rare's glow colour (blue = bells, violet = glass, red = low brass) |
| **Boss** | a unique theme per boss with an intro, a loop and a final-phase variation (faster, extra layer). Vampire lords: a dark waltz; overlord demons: heavy choir and drums; archangels: huge choir pads |
| **Rift** | a detuned, slowed version of the local theme plus a reversed shimmer and a cold-fire hiss; each rift type has its own colour (Frostfire bells, Gloam choir, Bloodmoon waltz, Storm drums, Ruin stone percussion, and so on) |
| **Dungeon** | a sparser arrangement of the realm theme with more ambience; boss rooms go quiet before the boss theme |

### E7.5 Day vs night
- **Same melodies, different arrangement:** day = fuller, brighter (lyre, fiddle, birdsong); dusk = slower with a warm pad; night = sparse celesta, glass harmonica and music box, with crickets, owls and soft wisp chimes. The switch crossfades with the clock (about 20 s).
- Festival nights get special upbeat arrangements.

### E7.6 UI and ambience SFX guidelines
- **UI:** soft wooden clicks and parchment rustles (fits the HUD), music-box blips for menus, a warm chime for quest updates, a page-turn for the quest log. No harsh beeps.
- **Loot by rarity:** each tier has its own drop sound, getting richer (Common: soft tap; Uncommon: light chime; Rare: bell; Epic: glass shimmer; Legendary: a short choir swell + the Rift motif).
- **Combat:** chunky, readable hits; a distinct "perfect guard" ring and "perfect dodge" whoosh; spell sounds match their school (frost crackle, ember roar, rune hum, thunder crack).
- **Tells:** every boss and elite wind-up has an audio cue as well as the glow tell (accessibility).
- **Ambience per realm:** birds and wind (Midgard), thunder (Asgard), bubbling springs (Vanaheim), wisp chimes (Alfheim), creaking ice and wind (Jotunheim, Niflheim), forge clangs (Svartalfheim), lava bubbling (Muspelheim), whispers and lantern creaks (Helheim).
- **Mix:** separate sliders for music, SFX, ambience and voice blips; mono-safe and phone-speaker friendly; nothing piercing above the music. Respect the existing mute toggle (M, saved).
- **No voice acting:** characters use short original voice blips per personality (Hearthmoor tradition).
