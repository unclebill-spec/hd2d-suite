# Vanaheim's dungeons: the Rotwood Hollow and the Verdant Heart

Story design doc, file 3 of 6 for Hearthmoor (staging, 2026-10-05). It uses the shapes in `game/data.js` (`ITEMS`,
`QUESTS`, `TALK`, `markerFor`), `heroes.js` (`ENEMIES`, `SPAWNS`), `rares.js` (`BASES`, `RARE_AREAS`), `factions.js`
(`MERIT`, `REALM`) and `hollows.js` (bounces, gnome doors, the hidden spring, cold-fire braziers). Quests use **3 = done**,
with flag-driven sub-steps (the `harbor` pattern). Conflicts are in the last section.

---

## 0. What's already built (extend, don't duplicate)

| Already in the build | Where | How this doc uses it |
|---|---|---|
| **Mossbrook Springs** (`vanaheim`): the poisoned spring, Veyra's violet Alfheim rune burned into the glade, spore elementals, a moss golem, two braziers (`brazier_vh_w`, `brazier_vh_spring`), a gnome stump door, the vine gate (Rift Shrine / Bifrost) | `areas/src/vanaheim.json` | the realm hub. A new exit leads to the Rotwood Hollow |
| **Elder Burrowmoss** (`warden`, a gnome): the befriend / conquer choice, which sets `S.flags.alliance.vanaheim` | `data.js` `TALK.warden` | the quest giver on the befriend path. His choice branches everything here |
| **`S.flags.vanaheim_spring`**: the fx swap (`spring_poison` → `spring_clean`) and the light-pool swap (violet → cold blue). The code says "a later befriend quest sets it" | `game.js applySwaps`, `glow.js` | **The Violet Spring** (section 3.1) is that quest and sets it to `"cleansed"` |
| Enemies `sporeling` (Spore elemental) and `mossgolem` (Moss golem, a rooting slam) | `heroes.js` | reused in both dungeons |
| The rare **Sporemother** (2.2×, Summoner of sporelings) | `rares.js` | roams the Rotwood Hollow too |
| Vanaheim rifts (sporeling / mossgolem pool) | `rifts.js` | unchanged |
| `REALM.vanaheim = "embassy"`; `xpMul` +10% in Vanaheim at Embassy Friend | `factions.js` | the new areas map to `embassy` too |
| **Mossheart, the Elder Golem** (2.5×, the Mossglen mini-boss) | `heroes.js` | **not reused**. Note the name clash with the legendary *Mossheart Staff* (Decisions) |

New: two dungeon areas (`rotwood`, `verdant`), 3 regular enemies, 2 rares, 2 bosses, 3 quests, Tobble Capwhistle, and
evidence that feeds into `alfheim.md`.

---

## 1. Overview

**The frame-up:** Veyra poisoned Vanaheim's springs and burned **Alfheim runes** into the moss so Mossbrook would blame the
light elves. The poison doesn't start at the spring. It runs down from the **Rotwood Hollow**, a cave of decay under a fallen
giant tree. There, Veyra drove a **frost-iron spike** into the heart of **the Blight Regent**, once the gentle Keeper of
Fallen Leaves, who kept Vanaheim's rot-and-renewal cycle turning. The spike turned him cruel, and his rot now pumps violet
poison down the taproot into Mossbrook.

**Befriend path** (`alliance.vanaheim === "befriend"`):
1. **The Violet Spring.** Burrowmoss and his young gnome **Tobble Capwhistle** help you burn the poison out of the spring
   with cold fire and red toadstool caps. The spring clears, but a violet trickle still comes from upstream.
2. **The Rotwood Hollow.** Tobble guides you through the Hollow. You free caged gnomes, defeat the Regent and pull the
   spike. The Regent dies at peace and tells you it was "cold hands in violet". **Evidence:** the frost-iron spike, cut with
   Alfheim-style runes that were burned **cold**. Vanaheim is resolved as an ally, Tobble can join you, and a moss-pup goes
   to the Stray Den.
3. **The Verdant Heart** (optional). A living forest opens beneath the Regent's grave. **Hjortur the Greenheart**, the elder
   stag-king, tests you in a **guardian trial** and blesses you.

**Conquer path** (`alliance.vanaheim === "conquer"`):
- There is no Violet Spring. You storm the Rotwood Hollow alone to take Vanaheim's heartwood. The caged gnomes flee from
  you, and the riddle door stays shut. The Regent dies bitter and mocks you ("the cold hands will thank you"). You still take
  the spike, which is evidence, but nobody in Vanaheim will hear it from you.
- The Verdant Heart opens **corrupted**. Hjortur's antlers are choked with violet rot, and you fight him **to the death**.

**Veyra between realms:** once the Rotwood is done she appears briefly. On the befriend path she approves ("you mend what
others break"). On the conquer path she taunts you ("you're doing my work for me").

**Look:** gloom-and-glow everywhere. The Rotwood is dark mulch and grey fungus shelves, lit by **glow moss** trails, **red
white-spotted toadstools**, violet poison seams and the **cold-fire braziers** you light. Rot means leaf-litter and soft
spores. Nothing gross (the Plaguewell keeps that). The Verdant Heart is a night-time cathedral forest: moonpetals, gold
fireflies, blue cold-fire buds on new saplings, and glowing springs. Light pools, no bloom.

---

## 2. Placement

### 2.1 Mossbrook Springs (`vanaheim`): the way in

- New exit: **the root-cave under the Old Bough**, a fallen giant tree on the glade's east side, just upstream of the spring.
  Suggested spot `[8.4, -6.4]` with a rect of about `[7.6, -7.2, 9.2, -6.0]`, `to: "rotwood"`, `spawn: "from_mossbrook"`,
  label `"the root-cave under the Old Bough"`. Fit it to the area.
- Before *The Rotwood Hollow* starts, the cave is choked with thorny roots, and the look text reads:
  `["A root-cave under the fallen Old Bough. A violet trickle seeps out of it. Thorny roots bar the way."]`
- On the befriend path the roots part when Burrowmoss gives the word (rotwood stage 1). On the conquer path you burn
  through them: any spell at the roots opens the cave once the quest is active.
- The gnome stump door (`door_vh_stump`): after the cleanse its `say` becomes
  `["(The round door opens wide.) The spring's sweet again! Drink all you like. Well. Not ALL."]`. On the conquer path
  the door stays shut: `["(Through the door, someone whispers: \"Is the big one gone yet?\")"]`

### 2.2 New area: `rotwood` ("The Rotwood Hollow")

A static dungeon: a chain of root caverns running down to the Regent's Bower. `REALM.rotwood = "embassy"`. It uses its own
fixed lighting (no sky; the clock pauses per E5.1), except the Bower, whose roof is open to the night. It has one hidden spring
(`game.spring` with `secret: "rw_spring"`), braziers (`game.braziers`), bounce toadstools (`game.bounces`) and a gnome door
(`game.doors`). Room beats are in section 4.

### 2.3 New area: `verdant` ("The Verdant Heart")

It opens under the Regent's grave once *The Rotwood Hollow* is done. Enter through the new sapling that grows where he fell.
`REALM.verdant = "embassy"`. It has one hidden spring (`secret: "vh_heart_spring"`) and growth beds (section 5).

---

## 3. Quests (`QUESTS` entries)

Helpers: `A(S) = ((S.flags || {}).alliance || {}).vanaheim`; `lit(S, ids)` counts `S.found[id]`.

### 3.1 The Violet Spring (befriend only)

```js
vh_spring: {
  title: "The Violet Spring",
  giver: "Elder Burrowmoss",
  story: true,
  steps: {
    1: (S) => { const F = S.flags || {}, n = (S.inv.redcap || 0);
      if (lit(S, ["brazier_vh_w", "brazier_vh_spring"]) < 2) return `Light Mossbrook's two cold-fire braziers (cast a spell at each). ${lit(S, ["brazier_vh_w", "brazier_vh_spring"])}/2`;
      if (n < 3 && !F.vh_caps) return `Gather 3 red toadstool caps from Mossbrook's giant toadstools. ${n}/3`;
      return "Drop the red caps into the spring (E / A at the water)."; },
    2: "The spring is clearing, but a violet trickle still runs down from the Old Bough. Tell Burrowmoss.",
    3: "Mossbrook's spring runs sweet again. The poison comes from somewhere upstream.",
  },
},
```

| Stage | Done when | Sets |
|---|---|---|
| 1 | both braziers lit, 3 `redcap` picked up, then E / A at the spring (the caps are used up) | `flags.vh_caps = 1`, `flags.vanaheim_spring = "cleansed"` (the existing swap fires) |
| 2 | talk to Burrowmoss | starts `rotwood` |
| 3 | done: **+60 Realm Favor** (`MERIT.vh_spring`) | |

Red caps: three new pickups (`redcap`) under Mossbrook's giant toadstool caps. They glow red with white spots, and the cap
itself is self-lit.

### 3.2 The Rotwood Hollow (both paths)

```js
rotwood: {
  title: "The Rotwood Hollow",
  giver: "Elder Burrowmoss",          // on the conquer path the quest starts at the root-cave (section 6.6)
  story: true,
  steps: {
    1: (S) => { const F = S.flags || {};
      if (!F.rw_in) return A(S) === "conquer"
        ? "Burn through the thorny roots under the Old Bough and take the Rotwood Hollow."
        : "Follow Tobble into the root-cave under the Old Bough.";
      if (!F.rw_lock) return "Find a way through the Rotwood Hollow. The rune-sealed root door wants three cold-fire braziers lit.";
      return "Go down to the Regent's Bower, where the taproot weeps violet."; },
    2: (S) => ((S.flags || {}).rw_spike
      ? (A(S) === "conquer" ? "The Regent is dead. Take what you came for and leave Vanaheim." : "Bring the frost-iron spike to Elder Burrowmoss.")
      : "Defeat the Blight Regent."),
    3: (S) => (A(S) === "conquer"
      ? "Vanaheim bows to you, and hates you for it. The spike's cold runes are yours to keep."
      : "The Blight Regent rests. The spike's cold runes say the elves were framed."),
  },
},
```

| Stage | Done when | Sets / pays |
|---|---|---|
| 1 | reach the Bower: `rw_in` on entering, `rw_lock` when the root door opens, then the Bower arena triggers stage 2 | |
| 2 | the Regent is defeated (`rw_boss`), the spike is picked up (`rw_spike`, item `blight_spike`), then talk to Burrowmoss (befriend) or leave the area (conquer) | the boss kill pays its realm merit automatically through `onBoss` (+80, see Decision 3) |
| 3 | done | befriend: **+120 Realm Favor** (`MERIT.rotwood`), Tobble can join, a moss-pup goes to the Den, `flags.vh_resolved = "befriend"`. Conquer: 150 gold + `heartwood` material, `flags.vh_resolved = "conquer"`. Both: the Verdant Heart opens; Veyra's beat (section 6.7) plays on the next area load |

### 3.3 The Verdant Heart (optional)

```js
verdant: {
  title: "The Verdant Heart",
  giver: "Tobble Capwhistle",         // conquer: it starts when the sapling's door cracks open (section 6.6)
  ripple: true,                       // optional; errandsDone() must skip it (same filter as side: true)
  steps: {
    1: (S) => (A(S) === "conquer"
      ? "Something sick and violet stirs under the Regent's grave. Go down into the Verdant Heart."
      : "Go down through the sapling into the Verdant Heart. Hjortur the Greenheart is waiting."),
    2: (S) => (A(S) === "conquer" ? "Kill the corrupted Hjortur." : "Pass Hjortur's guardian trial: root, bloom and light."),
    3: (S) => (A(S) === "conquer"
      ? "Hjortur the Greenheart is dead. The forest is very quiet."
      : "Hjortur blessed you. The forest knows your step."),
  },
},
```

| Stage | Done when | Pays |
|---|---|---|
| 1 | reach the Heart Glade (V5) | |
| 2 | befriend: the trial ends with Hjortur yielding. Conquer: the kill | befriend: **+80 Realm Favor** (`MERIT.trial`, a trial isn't a kill, so `onBoss` doesn't fire). Conquer: `onBoss` auto merit (Decision 3) |
| 3 | talk to Tobble (befriend) or leave the glade (conquer) | befriend: **+120 Realm Favor**, *Greenheart's Blessing*, `greenheart_tine`. Conquer: *Greenheart's Crown* (cosmetic), a guaranteed Legendary drop, 200 gold |

### 3.4 New `MERIT` keys (within the existing scale: boss 80, abyssal rift 120)

`vh_spring: 60, rotwood: 120, trial: 80, verdant: 120` (all Realm Favor / `embassy`). The Gnome Council pays through the
existing hooks: each hidden spring is `onSecret()` (+40 Gilded Acorns), and the Rotwood riddle door is `onRiddle()` (+60).

**Befriend-path Realm Favor:** 60 + 80 (Regent) + 120 + 80 + 120 = **460**, plus rifts and rares. That reaches **Trusted**
(400), with Honored (800) still to earn elsewhere.

---

## 4. The Rotwood Hollow, room by room

Pools: `sporeling`, `mossgolem`, new `rottreant`, new elite `thornhex`. The Sporemother (2.2×) can roam R4. The new rare
**Rotbark Elder** (2.6×) roams R1 and R4. Two checkpoint braziers (E4.1): R0 and R6.

| # | Room | Beat | Mechanic / puzzle | Foes | Secrets / glow |
|---|---|---|---|---|---|
| R0 | **Root Gate** | a low cave under the Old Bough. Tobble lights a pocket lantern (befriend) | **checkpoint brazier 1** (light it with a spell, and it's your respawn) | — | the first red toadstools; a violet seam in the floor shows the way |
| R1 | **Leaf-Litter Hall** | a long dark hall knee-deep in fallen leaves. Spores drift | **glow-moss path:** moss patches flare blue-green when stepped on and show a safe route over the **rot-mire** (off the path you're *Mired*: stamina drains, like the moss golem's chill). Your pet light shows the next patch | 3 `sporeling`, 1 `rottreant` (asleep until you pass) | Rotbark Elder can roam here at night |
| R2 | **Toadstool Bridge** | a chasm. Giant red caps grow out of the far wall | **bounce toadstools** (the `game.bounces` from the Hollows): three hops cross; a fourth, hidden cap springs you to a ledge | 2 `sporeling` lobbing from the far side | **hidden spring** on the ledge (`rw_spring`, +40 Gilded Acorns, spring-fizz) |
| R3 | **Rune-Sealed Root Door** | a wall of roots carved with three burning violet runes | **cold-fire brazier lock:** three braziers, and each rune pulses in turn. Light the braziers **in the pulse order** (a wrong order snuffs all three). Lighting each one wakes a `rottreant`. The **Seer** sees the order written in frost (a hint toast) | 2 `rottreant`, 1 `mossgolem` | the runes burn violet but **rime with frost** when lit near (the first hint of the frame) |
| R4 | **Mire Gallery** | a wide cave of fungus shelves over black water | **light zones:** a `thornhex` throws thorn walls. Lit braziers burn the thorns away, and wraith-like rot-fog avoids the light | 1 `thornhex` (elite) + 2 `sporeling`; the rare spot (Sporemother or Rotbark Elder) | fungus shelves glow faint blue when struck |
| R5 | **Gnome Larder** (side room) | gnomes in **thorn cages**, kept for "mulch" | **befriend:** break the 3 cages with any attack; the freed gnomes open a **riddle door** (below). **Conquer:** the gnomes bolt through a burrow, and the riddle door is shut: `"(A gnome voice: \"Not for YOU.\")"` | 2 `rottreant` guards | the riddle door's chest: a moon opal + 40 gold (befriend) |
| R6 | **The Weeping Root** | the great taproot, oozing violet sap down toward Mossbrook | **checkpoint brazier 2**. Tobble's warning (section 6.4) | — | a frost-rimed rune in the root bark, and the cold seeping from below |
| R7 | **The Regent's Bower** (boss) | a round hollow under the rotting giant, its roof open to the aurora. Four dead braziers ring the arena | the boss fight (section 7.1) | the Blight Regent + summoned `sporeling` | the arena braziers matter in phase 2 |

**Riddle door (R5, befriend):** a carved gnome face asks the riddle. The answer is "a shadow", and `onRiddle()` pays +60
Gilded Acorns.

```js
pages: ["The carved gnome's eyes glow. \"I follow you all day, but run from every lamp. What am I?\""],
choice: { id: "rw_riddle", options: [
  { label: "A shadow.", pick: (G) => { flags(G.S).rw_riddle = 1; G.factions.onRiddle(); gem(G, "moon_opal"); gold(G, 40);
      return { pages: ["\"Ha! Clever big-folk.\" The door rolls aside like a sleepy snail."] }; } },
  { label: "A cat.", pick: () => ({ pages: ["\"Cats run TOWARD lamps. To sit in front of them.\" The door sulks."] }) },
  { label: "My debts.", pick: () => ({ pages: ["\"Ha! True, but no.\" The door stays shut, chuckling."] }) },
  { label: "Leave it.", cancel: true, pick: () => ({ pages: ["The carved gnome winks. It'll keep."] }) },
] },
```

---

## 5. The Verdant Heart, room by room

Nature + life. On the **befriend** path the forest is a **trial**: dryads are friendly and give hints, and life elementals
are trial spirits that "tag" you instead of hitting hard. On the **conquer** path everything is hostile: dryads become
**thorn-nymphs** and life elementals heal their kin. The pools use `mossgolem`, new `lifewisp`, `thornhex`, and corrupted
dryads (`thornnymph`, conquer only). The new rare **Thornmother** (2.4×) is a dryad-tree that Veyra's rot reached. She is in
V4 on both paths (the one corrupted thing in a healthy forest).

| # | Room | Beat | Mechanic / puzzle | Foes | Secrets / glow |
|---|---|---|---|---|---|
| V0 | **Sapling Door** | a new sapling with blue cold-fire buds, grown where the Regent fell. Its roots open a stair | **checkpoint brazier** (befriend: Tobble lights it and hums) | — | befriend: blue buds; conquer: violet-black buds |
| V1 | **Grove of Whispers** | ring-trees with faces | befriend: three **dryads** each give a line of hint for the trial. Conquer: 3 `thornnymph` attack | conquer only | gold fireflies; moonpetals (pickups) |
| V2 | **Bloom Stair** | broken root-stairs over a glowing pool | **growth puzzle:** plant a **glow seed** in a root bowl, hit it with any spell, and it blooms into a moss bridge in 3 s (Bill's glow-gardening, made instant). There are three bowls; Tobble carries 3 spare seeds on the befriend path | 2 `lifewisp` (they heal other foes; break them first) | the bridge blooms glow cold-blue, violet and red (the three garden plants) |
| V3 | **Firefly Maze** | a hedge maze in deep dark | **pet light + fireflies:** firefly swarms drift toward the correct turns, and your pet's light makes them brighter. A `mossgolem` patrols | 1–2 `mossgolem` | **hidden spring** at the maze heart (`vh_heart_spring`, +40 Gilded Acorns) |
| V4 | **Moonwell** | a still pool reflecting the aurora | a **rare fight:** the Thornmother rises from the well, and on the befriend path dryads cheer you on | Thornmother (2.4×) + 2 `lifewisp` | the moonwell heals fully once after the fight |
| V5 | **Heart Glade** (boss) | a vast tree-hollow cathedral, a ring of standing stones, four braziers | Hjortur (section 7.2) | — | befriend: braziers wait unlit for the Trial of Light |

---

## 6. Dialogue

Every line fits the dialogue box (≤ 120 characters). `{cls}` variants use `S.cls`.

### 6.1 Tobble Capwhistle (new)

| Field | Value |
|---|---|
| TALK key / actor id | `tobble` |
| met flag | `S.met.tobble` |
| name plate | `Tobble Capwhistle, gnome of Mossbrook` |
| role | `gnome` (the existing Mossbrook sprite) with a recolour |
| pos | Mossbrook `[0.6, -3.6]` beside Burrowmoss once *The Violet Spring* starts; R0 and V0 in the dungeons (befriend only) |
| say | `["*tweet* That's my whistle. It means hello. Two tweets means run."]` |

**Look (normal clothes):** a young gnome, knee-high to the hero, freckled, with a round nose. He wears a mustard knit
sweater, patched green trousers and a belt hung with tiny tools and a pocket lantern. His hat is a **red, white-spotted
toadstool cap** with a tin whistle tucked in the band.
**Personality:** cheerful, brave in short bursts, a tinkerer and riddle-lover. He calls the hero "big-folk" and whistles
when nervous. He's the Vanaheim companion (handoff, section 11) on the befriend path.

### 6.2 Elder Burrowmoss: *The Violet Spring* (befriend, right after the choice)

His current befriend reply ends with "mind those runes: they don't smell like elf-work to me." The next talk offers the quest:

```js
pages: [
  "Right. Cold fire burns poison out of water, and red toadstool caps drink up the rest. Old gnome trick.",
  "Light both braziers by the spring, then bring me three red caps. Tobble knows which ones. Tobble!",
  "Tobble: \"*tweet!* Here! Hello, big-folk! The best caps grow under the giant ones. They glow when they're ready.\"",
],
then: (G) => { G.S.met = { ...(G.S.met || {}), tobble: 1 }; G.setQuest("vh_spring", 1); },
```

- Reminder: `["Braziers first, caps second, splash third. Gnome work is all in the order."]`
- Toast when the caps hit the water: `The red caps fizz and sink. Violet swirls out of the spring like smoke... and the water runs clear.`
- Turn-in (stage 2):

```js
pages: [
  "Look at that! Clear as a gnome's conscience. Clearer, maybe.",
  "But see the trickle? Still violet, and coming down from the Old Bough. The poison's upstream, in the Rotwood.",
  "Tobble goes with you. Don't argue, Tobble. You've been whistling at that cave all week.",
],
then: (G) => { G.setQuest("vh_spring", 3); G.factions.add("embassy", MERIT.vh_spring, "vh_spring"); G.setQuest("rotwood", 1); },
```

### 6.3 Tobble in the Rotwood (befriend)

| Where | Line |
|---|---|
| R0 entering | `"It smells like old leaves and older secrets. I'll light the way. *tweet*"` |
| R0 brazier lit | `"Good! If you faint, the brazier remembers you. Braziers are nice like that."` |
| R1 rot-mire | `"Step on the glowy moss! Not the brown stuff. The brown stuff wants your boots."` |
| R2 toadstools | `"Bounce caps! Red ones bounce best. Gnome fact. I've done it a hundred times. Twice."` |
| R3 rune door | `"Those runes are violet like elf-work, but they're cold. Elf runes are warm. Weird, big-folk."` |
| R3 Seer (`seer`) | `"You can SEE the order? In frost? Can you see what I'm having for supper?"` |
| R5 cages | `"Cousins! Hold on! Big-folk, break the thorns, gently-ish!"` |
| R5 freed gnomes | `"(A freed gnome:) \"Thank you! Tell Burrowmoss we're fine. Smelly, but fine.\""` |
| R4 rare | `"That's a big one. I'll be, um, supervising. From behind this rock."` |

### 6.4 The Weeping Root (R6)

- Befriend (Tobble): `"That's him down there. The Blight Regent. He used to be the Keeper of Fallen Leaves."`
  then `"He was gentle. He'd tuck acorns into the mulch for us. Something made him cold."`
- Conquer (narration): `"Violet sap weeps from the taproot. Below, something huge breathes slow, rotten breaths."`

### 6.5 Cutscenes: the Blight Regent

**Intro (befriend):** speaker `{ id: "regent", name: "The Blight Regent" }`

```js
pages: [
  "(The rot stirs. A crown of dead antlers rises, hung with red toadstools. Violet eyes open far above you.)",
  "Little warm thing. You smell of the spring. Of moonpetal. Of hope. I will make mulch of all three.",
  "Cold... so cold in my heart. The elves did this. Their runes burn violet. I will rot their springs next.",
  "Tobble: \"Keeper, it's me, Tobble! You used to hide acorns for me!\"",
  "...I do not know that name. Everything rots, little gnome. I only hurry it along.",
],
```

**Intro (conquer):**

```js
pages: [
  "(The rot stirs. A crown of dead antlers rises, hung with red toadstools. Violet eyes open far above you.)",
  "Midgard's conqueror. Come to take Vanaheim's heart? Take mine, then. It is cold, and it is rotten.",
],
```

**Outro (befriend):** after the kill, the spike falls out of his chest (`rw_spike`). He sinks into rich soil, and a sapling
with blue buds sprouts.

```js
pages: [
  "(The Regent sinks to his knees. A frost-iron spike slides from his chest and rings on the stone.)",
  "The cold... is gone. I can hear the leaves again. They are so loud. I had forgotten.",
  "It was not the elves. It was cold hands, in the dark. They wore violet like a mask.",
  "Let me rest, warm thing. Leaves must fall so the spring can come. Tell Burrowmoss the Heart is open.",
  "Tobble: \"...*tweet*. Goodnight, Keeper.\"",
],
```

**Outro (conquer):**

```js
pages: [
  "(The Regent crashes down. A frost-iron spike juts from the rotten wood of his chest, still frosted.)",
  "So Vanaheim bows... to a fist. The cold hands will thank you for this.",
  "Rot is patient, conqueror. So is she.",
],
```

On the spike pickup, toast: `A frost-iron spike, carved with Alfheim-style runes. The runes were cut cold, not lit.`
Seer extra page (`seer`): `"(Your runes read it at once: Alfheim's shapes, but cut by frost. A forgery, and a careful one.)"`

### 6.6 Conquer path openers (no Burrowmoss)

- Root-cave look while rotwood isn't started and `alliance.vanaheim === "conquer"`:
  `["The root-cave under the Old Bough. Whatever poisons Vanaheim lives below. Whatever rules it, you'll take."]`,
  then `then: (G) => G.setQuest("rotwood", 1)`.
- Burrowmoss (conquer, any time): `["You again. Say what you came to say, Midgarder, and go."]` (the existing line)
  - After the Regent: `["The Keeper's dead, and the spring's still violet. You took his heart and left us his rot."]`
- The sapling door after a conquered Rotwood: `["The new sapling's buds are violet-black. Below it, something huge groans awake."]`,
  then `G.setQuest("verdant", 1)`.

### 6.7 Elder Burrowmoss after the Rotwood (befriend), and Veyra's beat

Burrowmoss turn-in (rotwood stage 2, spike in the bag):

```js
pages: [
  "Frost-iron! Elves don't work iron, and they never work cold. Someone wanted us at the elves' throats.",
  "Mossbrook owes Alfheim an apology. Take that spike to Lumenvale, if their gate ever thaws.",
  "And Mossbrook owes you more. Tobble's been packing his tools since you left. Take him, if you'll have him.",
  "Tobble: \"*tweet tweet!* That's two tweets. It doesn't mean run this time. It means YES.\"",
],
then: (G) => { G.setQuest("rotwood", 3); G.factions.add("embassy", MERIT.rotwood, "rotwood");
               flags(G.S).vh_resolved = "befriend"; flags(G.S).companions = { ...(flags(G.S).companions || {}), tobble: 1 };
               G.S.pets = { ...(G.S.pets || {}), mosspup: G.S.pets?.mosspup || { name: "Moss-pup", bond: 1, atDen: 1 } };
               G.toast("Tobble Capwhistle can join you. A moss-pup is waiting at the Stray Den.", 3.0); },
```

**Veyra between realms** (the next area load after `vh_resolved`). It plays where you arrive (Mossbrook or Bifrost). Speaker:
`"Veyra"` if `met_veyra`, else `"A frost-witch in grey-blue"`. She leaves before you can answer.

| Path | Pages |
|---|---|
| befriend | `"You pulled a spike from a dying god and held his hand while he went. You mend what others break."` · `"Few do. I'm glad it was you."` |
| conquer | `"Vanaheim bowed. Its springs will remember whose boot it was. You're doing my work for me, you know."` · `"Don't stop on my account."` |

Seer extra (befriend): `"(Your runes prickle at her, the way they did at the spike. You can't say why.)"`

### 6.8 Later Burrowmoss / Tobble lines (befriend)

| Who | Condition | Line |
|---|---|---|
| Burrowmoss | default | `"Spring's sweet, caps are fat, and Tobble writes home every day. Badly spelled, but every day."` |
| Burrowmoss | Verdant done | `"The Greenheart blessed you? Then the whole forest knows your boots. Wipe them anyway."` |
| Burrowmoss | night | `"The spring glows blue at night now. Cold fire's a good guest. Leaves no crumbs."` |
| Tobble (companion, idle) | Mossbrook | `"Home! Smells like mushrooms and gossip. Two of my favourite things."` |
| Tobble | Bifrost | `"So many gates! I want to take one apart. Just to look. And put it back. Mostly."` |
| Tobble | any rift | `"*tweet tweet!* That's two. That one does mean run. Or fight. Your call, big-folk."` |

---

## 7. Bosses (look, phases, tells, for Systems)

### 7.1 The Blight Regent (Rotwood Hollow, R7)

- **Look:** **5.5× the player's height.** A towering, hunched nature lord of rotting bark and moss. A crown of dead antlers
  hung with glowing **red white-spotted toadstools**, a mantle of hanging moss and fallen leaves (living growth, not a
  suit), and a ribcage of roots around a wound that glows **violet**. A **blue frost-iron spike** juts from it, and rime
  creeps out from it in frost-flowers. He has sickly violet eyes and carries a dead sapling as a staff. The spike and the frost are
  the only blue on him, so the eye goes straight to the truth.
- **Arena:** the Bower, round, about 14 m across, with an open roof (aurora) and four dead braziers on the rim.

| Phase | HP | Moves | Tell |
|---|---|---|---|
| 1 **Fall of Leaves** | 100–60% | staff sweep (a wide arc); **rot shockwave** every 3rd slam (the `wave` ring); summons 2 `sporeling` from the mulch | the staff's toadstools flare **red** 0.8 s before a sweep; a rune ring under him before the wave |
| 2 **Rot-fog** | 60–25% | the Bower fills with dark fog, and outside light zones you stack **Blight** (−stamina regen, a max of 3 stacks). **Light the 4 rim braziers** with spells to make safe pools. Violet **vine snares** root you | violet lines crawl along the floor 1 s before a snare snaps up |
| 3 **Heartwood Bare** | < 25% | his bark splits. Faster slams; **frost burst** rings out from the spike. Hitting the **spike** (a lock-on weak point) staggers him for 3 s | the spike pulses blue twice before each frost burst (a blue ring decal) |

`ENEMIES` suggestion (the numbers are for Systems to tune; compare `eldergolem`, 2.5× / 460 HP):

```js
blightregent: { name: "The Blight Regent", scale: 5.5, hp: 1400, dmg: 26, speed: 0.8, reach: 4.5, windup: 0.85, cd: 2.2, aggro: 9, r: 1.6,
                push: 0.1, heavy: true, slam: true, boss: true, wave: { every: 3, r: 6.0, dmg: 20 }, minion: "sporeling",
                phases: [0.6, 0.25], weak: "spike", glow: "#a45cf0", legendary: true, noRespawn: true },
```

### 7.2 Hjortur the Greenheart (Verdant Heart, V5)

- **Look:** **6× the player's height.** An elder stag-king with a white-and-moss coat and **antlers like a living canopy**,
  hung with glow moss, moonpetal blooms and drifting gold fireflies. His hooves are roots, and his breath mists silver. On the
  befriend path his eyes are **warm gold**. On the conquer path they are **violet**, and rot-black moss and violet poison seams
  choke his antlers. The fireflies are replaced by violet spores.

**Befriend: the guardian trial** (non-lethal; he **yields** at 0 HP: `trial: true`. No kill, no death, no loot table, only rewards)

| Trial | HP | What he tests | Tell |
|---|---|---|---|
| **Root** | 100–66% | charge lanes across the glade; root eruptions in lines | he lowers his antlers and paws the ground 1.0 s (a gold ring under his hooves) |
| **Bloom** | 66–33% | three saplings sprout. Keep his roots off them for 40 s (body-block, stun, or heal a sapling with any heal) | saplings glow gold where a root will strike next |
| **Light** | 33–0% | his antler-light dims the glade. **Light the 4 braziers** before it goes dark (60 s) while he sweeps | each antler flare = a wide sweep, 0.9 s |

**Conquer: the corrupted fight** (lethal, `boss: true`)

| Phase | HP | Moves | Tell |
|---|---|---|---|
| 1 | 100–55% | charges, antler sweeps, summons 2 `thornnymph` | lowered antlers + violet ground ring |
| 2 | 55–20% | rot roots erupt in rings; healing springs turn violet and heal **him** | springs fizz violet a beat before they heal |
| 3 | < 20% | a frenzy of double charges; he tears the glade's light out (the arena dims to point lights only) | an antler scream (an audio cue) + red-violet flare |

```js
hjortur: { name: "Hjortur the Greenheart", scale: 6, hp: 1800, dmg: 28, speed: 1.4, reach: 5.5, windup: 0.95, cd: 2.0, aggro: 10, r: 1.8,
           push: 0.1, heavy: true, charge: true, boss: true, phases: [0.66, 0.33], glow: "#f2c24a",
           trial: (S) => ((S.flags || {}).alliance || {}).vanaheim === "befriend",   // yields at 0 HP instead of dying
           corrupt: { glow: "#a45cf0", minion: "thornnymph", phases: [0.55, 0.2] }, legendary: true, noRespawn: true },
```

**Hjortur intro (befriend):**

```js
pages: [
  "(The glade breathes. Antlers like a forest canopy rise above the stones, full of fireflies.)",
  "You pulled the cold from the Keeper's heart. The forest felt it. I am Hjortur, and I am the forest's heart.",
  "A friend of Vanaheim must be tested, not trusted. Show me root, and bloom, and light.",
  "Tobble: \"*tweet* He's not going to hurt you. Much. Probably. Good luck!\"",
],
```

Grovekeeper extra page (`grovekeeper`): `"Child of the Vanir. Your mother walked these groves. Let us see if you walk them as kindly."`

**Hjortur outro (befriend, yields):**

```js
pages: [
  "(Hjortur lowers his great head until his antlers touch the moss. The fireflies settle on you like snow.)",
  "Root, bloom and light. You held all three. The forest knows your step now, and it will hold you up.",
  "Take this tine from my crown. When Vanaheim's staff is ready to be grown, it will need it.",
  "Go gently. The cold hands are not finished, and they fear warm ones.",
],
```

**Hjortur intro (conquer):**

```js
pages: [
  "(The glade groans. Antlers choked with violet rot rise above the stones. The fireflies are gone.)",
  "You killed the Keeper and left his rot in my roots. Now the cold sings in me too.",
  "Conqueror. Come and take Vanaheim's heart, then. It will cost you yours.",
],
```

**Hjortur outro (conquer):**

```js
pages: [
  "(Hjortur falls. The rot drains from his antlers, too late. His eyes clear to gold for one breath.)",
  "Ah. There it is... the forest. I had forgotten how quiet it is.",
  "(He is still. The glade goes very dark. Somewhere far off, a single firefly lights, and goes out.)",
],
```

### 7.3 Rares (2-3× the player's height)

| Rare (`BASES` key) | Scale | Look | Behaviour | Where |
|---|---|---|---|---|
| Sporemother (`sporemother`, existing) | 2.2× | (as built) | ranged, Summoner of sporelings | Rotwood R4 |
| **Rotbark Elder** (`rotbark`) | 2.6× | a hunched rot treant, bark split by violet seams, red toadstools down its back | slow grab-and-slam; uproots and lobs mulch clods | Rotwood R1 (night) and R4 |
| **Thornmother** (`thornmother`) | 2.4× | a corrupted dryad-tree: a willowy figure of bark and thorns with a moonpetal crown gone violet | thorn walls and thorn volleys; Summoner (`thornnymph`) | Verdant V4 (fixed spawn) |

```js
rotbark:     { name: "Rotbark Elder", scale: 2.6, hp: 320, dmg: 20, speed: 0.9, reach: 2.8, windup: 0.75, cd: 2.0, aggro: 7, r: 0.75, push: 0.2,
               heavy: true, slam: true, minion: "rottreant", xp: 190 },
thornmother: { name: "Thornmother", scale: 2.4, hp: 300, dmg: 14, speed: 1.1, reach: 6.5, keep: 3.8, windup: 0.6, cd: 2.0, aggro: 8, r: 0.66,
               push: 0.4, ranged: true, bolt: "seed_bomb", minion: "thornnymph", xp: 185 },
```

`RARE_AREAS.rotwood = { bases: ["sporemother", "rotbark"], spots: [...] }`. The Thornmother is a fixed V4 spawn, not a roamer.

### 7.4 New regular enemies (`ENEMIES` suggestions)

```js
rottreant:  { name: "Rot treant", hp: 110, dmg: 15, speed: 0.85, reach: 1.7, windup: 0.8, cd: 2.2, aggro: 5, r: 0.4, push: 0.25, heavy: true, sleeps: true },
thornhex:   { name: "Thornhex", hp: 90, dmg: 12, speed: 1.3, reach: 6.0, keep: 3.6, windup: 0.6, cd: 2.6, aggro: 7, r: 0.3, push: 0.5, ranged: true,
              bolt: "seed_bomb", elite: true, wall: "thorn" },   // a gaunt hag in a moss shawl, a skirt of dry leaves, a belt of bones and bells
lifewisp:   { name: "Life elemental", hp: 45, dmg: 6, speed: 1.6, reach: 5.0, keep: 3.2, windup: 0.5, cd: 2.8, aggro: 6, r: 0.26, push: 0.5, ranged: true,
              float: true, healsKin: 20 },
thornnymph: { name: "Thorn-nymph", hp: 60, dmg: 10, speed: 1.7, reach: 1.4, windup: 0.5, cd: 1.6, aggro: 6.5, r: 0.28, push: 0.6 },   // conquer only
```

XP suggestions for `progress.js XP`: `rottreant: 50, thornhex: 70, lifewisp: 32, thornnymph: 38, blightregent: 600, hjortur: 750`.

---

## 8. Items and rewards

```js
redcap:          { name: "Red toadstool cap", px: "redcap",
                   about: "A red cap with white spots, glowing softly. Gnomes swear it drinks poison right out of water." },
blight_spike:    { name: "Frost-iron spike", px: "blight_spike",
                   about: "Pulled from the Blight Regent's heart. Alfheim-style runes, but cut cold, not lit. Evidence." },
heartwood:       { name: "Regent's heartwood", px: "heartwood",
                   about: "A slab of the Blight Regent's heart, rot-black and cold. A rare forging material. Sable would pay." },
greenheart_tine: { name: "Greenheart tine", px: "greenheart_tine",
                   about: "A tine from Hjortur's crown, still budding. The Mossheart Staff will need it, one day." },
```

| Reward | Path | Effect |
|---|---|---|
| **Greenheart's Blessing** (a permanent buff) | befriend, Verdant done | +5% healing done and +1 HP/s regen out of combat **in Vanaheim areas** (`mods: { healMul: 0.05, regen: 1 }` while `REALM` is Vanaheim). A small hometown-hero perk |
| **Greenheart's Crown** (cosmetic) | conquer, Verdant done | a dark antler circlet with violet buds, purely cosmetic (a trophy-wall item later) |
| **Moss-pup** at the Stray Den | befriend, Rotwood done | the pet from the city list (Forager's Nose aura). The full `PETS` entry, barks and Signe's arrival line are in `pets.md` section 6.6 / 7.5 |
| **Tobble Capwhistle** companion | befriend, Rotwood done | sets `flags.companions.tobble` (the companion system isn't built yet) |
| **Evidence** | both | `S.evidence = { ...S.evidence, vanaheim: "blight_spike" }`. It feeds `alfheim.md` (clearing the elves) and the midpoint reveal (evidence points to Niflheim) |
| Boss loot | both | the Regent and the corrupted Hjortur drop a guaranteed Legendary (`legendary: true`). The trial Hjortur doesn't drop loot. The tine and blessing are his reward |

**Evidence hand-off to `alfheim.md`:** in Lumenvale, showing the `blight_spike` to the elves is the key beat of *the
poisoned-springs frame-up tie-in*. On the befriend path Burrowmoss's apology goes with it (a befriend chain step). On the
conquer path you have the spike but no Mossbrook apology, so it's weaker evidence (the elves ask, "Why would Vanaheim's
conqueror defend us?").

---

## 9. `markerFor` additions

```js
const F = S.flags || {}, av = (F.alliance || {}).vanaheim;
if (id === "warden" && av === "befriend" && !q.vh_spring) return "quest_mark";
if (id === "warden" && q.vh_spring === 2) return "quest_turnin";
if (id === "warden" && av === "befriend" && q.rotwood === 2 && F.rw_spike) return "quest_turnin";
if (id === "tobble" && q.rotwood === 3 && av === "befriend" && !q.verdant) return "quest_mark";
if (id === "tobble" && q.verdant === 2 && F.vd_trial) return "quest_turnin";
```

Tobble offers the Verdant Heart (befriend), after the Rotwood:
`["The Keeper's sapling opened a stair! Down there is the Verdant Heart. Hjortur lives there. THE Hjortur!"]`, then
`["He tests friends of Vanaheim. Nobody's passed in a hundred years. Nobody's tried in a hundred years. Let's go!"]`
→ `G.setQuest("verdant", 1)`.

---

## 10. Save shape (summary)

| Key | Meaning |
|---|---|
| `S.quests.vh_spring`, `rotwood`, `verdant` | 0-3 (3 = done) |
| `S.flags.vanaheim_spring` | `"cleansed"` (existing swap) |
| `S.flags.vh_caps`, `rw_in`, `rw_lock`, `rw_boss`, `rw_spike`, `rw_riddle`, `vd_trial`, `vh_resolved` | progress |
| `S.found.brazier_vh_w/_spring`, `rw_b1..3`, `rw_cp1/2`, `rw_spring`, `vh_heart_spring` | braziers, checkpoints, secrets |
| `S.flags.companions.tobble`, `S.pets.mosspup` | befriend rewards |
| `S.evidence.vanaheim` | `"blight_spike"` |
| `MERIT.vh_spring / rotwood / trial / verdant` | 60 / 120 / 80 / 120 (embassy) |
| `REALM.rotwood`, `REALM.verdant` | `"embassy"` |

---

## 11. Decisions needed

1. **Boss scale in the engine.** The style lock wants bosses at **5×+**. The biggest drawn so far is Mossheart at 2.5× on the
   boss sheet. The Regent (5.5×) and Hjortur (6×) need the boss sheet and arena cameras to handle about 160-190 px tall figures.
   Check this with Systems before the art.
2. **The "Mossheart" name clash.** The Mossglen mini-boss is "Mossheart, the Elder Golem", and Vanaheim's legendary weapon is the
   "Mossheart Staff". Rename the golem (suggestion: "Glenheart, the Elder Golem"; avoid "Mossback", which belongs to Ulfar
   Mossback), or keep both and make the staff "grown from Mossheart's core". Bill's call.
3. **Conquer-path merit.** `factions.realm()` maps Vanaheim areas to `embassy`, so a conqueror still earns **Realm Favor**
   from the Regent kill (`onBoss`), rifts and rares there. Recommended: when `alliance.vanaheim === "conquer"`, route that merit
   to `gate` (Rift Marks) instead. A cheaper option is no realm merit at all.
4. **Conquer sale to Sable (optional ripple).** Selling `heartwood` to Quartermaster Sable could pay +60 Black Doubloons
   (and cost a little Hearth standing, like `onSmuggle`). It's flavourful for the outlaw lean. Include it or skip it?
5. **The Verdant Heart's quest type.** It's optional (E2.7), so this doc tags it `ripple: true`. The `errandsDone()` filter
   should skip `ripple` as well as `story` and `side`. Alternatively tag it `story: true`, though then the log labels it "Story:".
6. **Trial mode.** Hjortur's befriend fight needs a combat flag that makes him **yield** at 0 HP (no death, no loot, no
   `onBoss`). That's new in `combat.js`. The two phase-gated objectives (saplings, braziers) are also new boss scripting.
7. **Moss-pup: done.** Added to `pets.md` (section 6.6 `PETS` entry and Signe's arrival line, 7.5 barks, the 6.4 sources table).
8. **One hidden spring per area.** `hollows.js` supports a single `game.spring`. Each dungeon here uses exactly one, so that's
   fine, but a second spring per area would need an array.
9. **Veyra on the conquer path.** Her "doing my work for me" beat plays even if the Old Temple cameo is switched off (she shows
   as an unnamed frost-witch). Is that OK, or should the first named meeting be required before any between-realm beats?
