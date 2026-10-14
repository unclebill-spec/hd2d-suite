# Alfheim: Lumenvale, the Dimming and the Prism Vault

Story design doc, file 6 of 6 for Hearthmoor (staging, 2026-10-05). This is the **full Alfheim realm arc**, written so the
Master Builder can build it straight from this file. It covers the frozen gate at Bifrost, the city of **Lumenvale** (3 areas), the
befriend and conquer chains, the poisoned-springs evidence from `verdant_heart.md`, the **Prism Vault** dungeon room by
room, **Lady Sylvaine** (boss, 6×), Veyra's beats, Lumi the wisp, rewards, and every code shape.

Shapes follow the build: `QUESTS {title, giver, story?/side?/ripple?/bounty?, steps}` with **3 = done** (stages 1–2 with
flag-driven sub-steps), `TALK.id(S) → {pages, then?, choice?}`, `markerFor` (`quest_mark` / `quest_turnin`), `ITEMS`,
`ENEMIES` / `BASES` (`heroes.js`, `rares.js`), `GATES` (`bifrost.js`), `REALM` / `MERIT` (`factions.js`),
`weatherAt` / `KINDS` (`weather.js`), and the Vanaheim alliance flag `S.flags.alliance.<realm> = "befriend" | "conquer"`
(`data.js` `ally(S)`).

Lead-approved conventions carried over: bosses 5–6× (engine support coming), **conquer-path merit goes to Rift Marks**,
the trial-mode code, `ripple` / `side` / `bounty` quests skipped by `errandsDone`, and `bounty` skipping the Hearth payout
(XP half on repeats). The Mossglen golem is **Glenheart**.

**Batch 2 (2026-10-06):** the lead resolved all 17 decisions (section 14). Changes: Sylvaine is resealed, asleep, on befriend, with an
NG+ hook (9.8). **Lumi is a glowing, speaking wisp** (Bill's override; 5.5). Svartalfheim locks at the choice. Prism tier III is parked.
`prism_core` is the 5th gem (9.7). The midpoint reveal waits for the Veyra beat (6.10). Dark Lumenvale is a re-grade (9.6). The lavender
day has a fallback (2.2). Added a Rift-Breaker stub (13).

---

## 0. What's already built (hook points)

| In the build | Where | Use here |
|---|---|---|
| `GATES.alfheim`: "Veyra froze Alfheim's gate shut, and only a Guild Keybearer may cut through a frozen seal." Key `['gate', 3]` (Keybearer, 800 Rift Marks) | `bifrost.js` | *The Frozen Gate* (section 3.1) replaces "the Guild is still cutting this key: coming soon" |
| Alfheim's sealed arch: `fx: "gate_alfheim"`, hue violet, pos `[-5.0, -11.9]` | `areas/src/bifrost.json` `game.sealed` | moves into `game.portals` with rect `[-5.75, -12.3, -4.25, -11.45]`, `to: "alfheim"`, spawn `from_bifrost` (same as Vanaheim's) |
| `ally(S)` → `S.flags.alliance` (`{ vanaheim: "befriend" | "conquer" }`) | `data.js` | adds `alfheim` |
| Burrowmoss: "Someone ... burned elf-runes into the moss. Alfheim's mark, plain as day." | `data.js` `warden` | the frame-up this arc undoes |
| `S.evidence.vanaheim = "blight_spike"`, item `blight_spike` ("Alfheim-style runes, but cut cold, not lit") | `verdant_heart.md` (staging) | the key evidence (section 4) |
| `REALM`, `MERIT`, `onBoss` / `onRare` / `onRift` pay `realm()` | `factions.js` | `REALM.alfheim / lumen_court / wispwood / prismvault = "embassy"` (conquer: `gate`) |
| Rares `BASES` with `scale`, `ELEMENTS` (Gloam = violet) | `rares.js` | two new bases (section 8.3) |
| `SKY` kinds; `KINDS` particle presets | `weather.js` | a new `prism` sky: aurora and prism rain (section 2.6) |
| Hidden spring rule (`game.spring`, `secret`), Hollows brazier rule (a spell within 2.6 m), `game.bounces` | `hollows.js` | in every Alfheim area and the Vault |
| Companion flag `flags.companions.<id>` (Tobble) | `verdant_heart.md` | `flags.companions.lumi` |
| Halvard foreshadowing ("Keys go missing", "up all night with the keys") | `old_temple.md`, `rift_storms.md` | the frozen seal "knows" his key (section 5.1) |

---

## 1. Overview

**Alfheim** is the realm of the light elves. Its city, **Lumenvale**, is built in the crowns of giant **silverbark trees** over a
dark forest floor of **bioluminescent pools**. **Glowing vines** hang from every bough in neon violet and blue, **glow orbs** drift
between the terraces, **wisps** nest in the canopy, and **glowfrogs** sing in the root-pools. Alfheim's day is a long lavender
dusk. At night, aurora curtains move over the treetops. It's the most "gloom-and-glow" place in the game: dark wood, dark water,
and thousands of small neon lights.

**The trouble.** Two things are wrong, and Veyra did both.
1. **The frame.** Vanaheim blames Alfheim for poisoning Mossbrook's springs, because elf-runes were burned into the moss. The
   elves are proud, hurt and defensive. They didn't do it, and nobody believes them. Veyra **froze Alfheim's gate** at Bifrost
   so the elves couldn't answer the charge.
2. **The Dimming.** Lumenvale's wisps are going dark one by one. Deep under the city, the **Prism Vault** holds **Lady Sylvaine**,
   Alfheim's first queen, sealed there about four hundred years ago. Long ago she grew so afraid of the dark that she began to **drink light**: first wisps, then her own
   people's magic. Her people sealed her inside the Vault, where endless light, bouncing between great prisms, kept her fed
   and asleep. Veyra's frost **cracked the prisms**. The light leaks, Sylvaine is waking hungry, and she drinks the city's wisps
   from below.

**Befriend path** (`alliance.alfheim === "befriend"`):
1. ***A Name in Frost.*** Clear Alfheim's name. Show the frost-iron spike (and Mossbrook's apology, if you befriended Vanaheim) to
   Mirelle, the Prism Library's keeper. Find the second proof, **Veyra's rune stencil**, at a frost scar in the Wispwood. Alfheim
   is cleared. The evidence now points somewhere cold.
2. ***The Dimming.*** Follow the failing wisps. Find **Lumi**, an old, talking wisp gone grey, and help her
   relight the dimmed wisps in the glow-pools. Trace the drained light to the Prism Spire. Lumi joins you.
3. ***The Prism Vault.*** With Mirelle's guidance, realign the Vault's cracked prisms. Sylvaine wakes. You defeat her and
   **reseal** her, asleep, in the Heart Prism, where she sleeps in the light at last (an NG+ hook, section 9.8). Alfheim becomes your ally. Rewards: Realm Favor,
   Lumi, the **Prism light school**, later the **Prism Edge**, and the Wisp Night festival.

**Conquer path** (`alliance.alfheim === "conquer"`):
- You use the frame as your excuse: "Mossbrook's runes are your runes." Midgard demands the **Prism Heart** as reparation.
  ***The Prism Claim***: beat Captain Faelan's rangers at the Spire bridge and take the Spire key.
- ***The Prism Vault*** on hard mode: no guide, light-elf rangers alongside the crystal foes. You break the Heart Prism to take it,
  which frees Sylvaine. You kill her. **Lumenvale dims for good**: no festival, no Lumi, no school, no Prism Edge. You get gold,
  the **Prism Heart** material, the boss Legendary and a trophy crown. Alfheim becomes a permanent enemy.

**Veyra in the arc:** her frost on the gate (and Halvard's key), her stencil at the frost scar, a reflection in the Vault's Hall
of Mirrors, and the between-realms beat afterwards (approving or taunting). If the midpoint reveal has already happened
(`flags.veyra_revealed`), her lines drop the act. If Alfheim is the realm that makes the reveal due, the reveal waits until
**after** Alfheim's Veyra beat (section 6.10), so that beat always plays its "before" lines.

**Svartalfheim, the rival realm:** Alfheim and Svartalfheim are a rival pair. Picking **befriend** at Aerin's choice **locks**
Svartalfheim out of an alliance right then (lead, 2026-10-06), not at `alf_resolved`. A dwarven trader in the Wisp Market, **Brokk Emberlode**, leaves in a huff and seeds the grudge. Conquering
Alfheim pleases Anvildeep (`flags.realm_mood.svartalfheim = +1`).

---

## 2. Lumenvale: areas, layout, look

### 2.1 Area list

| Area id | Name | Kind | `REALM` | Notes |
|---|---|---|---|---|
| `alfheim` | **Lumenvale: the Glimmer Steps** | city hub | `embassy` | arrival from Bifrost, the Wisp Market, waystone, glow-pools, hidden spring |
| `lumen_court` | **The Moonlit Court** | city | `embassy` | the Empty Throne, Regent Aerin, the Prism Library, the Prism Spire door |
| `wispwood` | **The Wispwood** | wild | `embassy` | forest floor: wisp nests, glowfrog ponds, the frost scar, rifts and rares |
| `prismvault` | **The Prism Vault** | dungeon | `embassy` | 9 rooms P0–P8 (section 7), boss Lady Sylvaine |

Conquer path: `factions.realm()` returns `gate` in these four areas once `alliance.alfheim === "conquer"`, so rifts, rares and the boss
pay Rift Marks (the same lead-approved rule as Vanaheim).

`SKY`: `alfheim, lumen_court, wispwood → "prism"`. `prismvault` has no sky (fixed light, the clock pauses as in the Rotwood),
except P8, whose roof opens onto the aurora.

### 2.2 Look (for Art)

- **Palette:** deep blue-black bark and water, silver-white bark highlights, and the signature **neon violet** (`#a45cf0`, `#c890ff`).
  Cold blue (`#5ab4f0`) for water glow and wisps, rose-red (`#ff4a3a`) accents in toadstools and the red glowfrogs, and pale
  gold (`#f2c24a`) only in lanterns. Prism light shows as thin **rainbow pixel shafts** on the ground (decals plus small point
  lights, **no bloom**).
- **Silverbark trees:** trunks wide as houses, pale bark with violet sap-veins that pulse slowly. Platforms ring the trunks.
  Bridges are rope with glass planks that glow faint violet underfoot.
- **Glowing hanging vines:** curtains of vines from every bough, tipped with violet and blue buds. They sway, and brushing past
  makes them flare brighter for 1 s.
- **Glow orbs:** soap-bubble lights the size of a fist. They drift between terraces and gather around anyone standing still.
  They're the street lamps (point lights, a slow bob).
- **Bioluminescent pools:** at tree roots and on platforms in bowls of living wood. Blue water, and ripples leave cyan rings.
- **Glowfrogs:** palm-sized frogs in blue, violet and red. They sit on lily pads and glow brighter when they sing (a soft
  "prrrp" chorus at night). Walking near makes them hop and leave light ripples.
- **Wisps:** neon motes with tails. Common wisps are blue-violet. During the Dimming, some flicker grey (dimmed).
- **Red white-spotted toadstools** grow on the Wispwood floor and in planters on the Steps (Bill's signature).
- **Fish-orb lanterns:** the Wisp Market sells Midgard-style orb lanterns with glowing fish, and elf-made neon prism lanterns.
- **Day vs night:** day is a long **lavender dusk** (the light is dimmed by 40% versus Midgard's day). Night is the main show, with
  aurora curtains over the canopy and every light at full strength.
- **How to do the lavender day (lead, 2026-10-06):** the builder first checks whether the engine supports a **per-area day light level**
  (e.g. an `AREA_LIGHT.alfheim = { dayMul: 0.6, dayTint: "#b8a8e0" }` read where the sun/ambient is set). If yes, use it for all four
  Alfheim areas. **Fallback:** a full-screen **tint overlay** (multiply blend, `#b8a8e0` at ~30% alpha) that is on during day phases,
  fades out over dusk and is 0 at night, so night lights stay at full strength. Note which one shipped in the build notes.

### 2.3 `alfheim`: the Glimmer Steps (city hub)

A broad, curving platform around the largest silverbark, stepping up in three terraces. Suggested camera like Bifrost's
(`bounds [-11, -9.6, 11, 12]`).

| Spot | Pos (suggested) | What |
|---|---|---|
| **Gatelight arch** (portal back to Bifrost) | `[0, 10.6]` (south edge) | spawn `from_bifrost` `[0, 9.2, "up"]`. A silverbark arch with violet frost-scars still melting on it |
| Waystone | `[3.2, 8.4]` | adds `alfheim` to the waystone network once visited |
| **The Wisp Market** (lower terrace) | `x -9..-2, z 3..8` | stalls under vine curtains: Saelis's lantern stall, Brokk's dwarf stall, a glow-orb seller (decor) |
| Ferrin's **glow-pool** with glowfrogs | `[6.4, 4.6]` | a big root-bowl pool, 6 lily pads, glowfrogs. The festival wisp-pond on Wisp Night |
| Nim's perch | `[8.8, 1.2]` | a low branch with a wisp net hanging from it |
| Middle terrace stair | `[0, 0.4]` | up to the **Lantern Walk** |
| **Lantern Walk** (middle terrace) | `x -6..6, z -4..0` | a promenade of prism lanterns. Rainbow shafts on the floor |
| Exit north (spiral stair) | `[0, -9.0]` | → `lumen_court` (spawn `from_steps`) |
| Exit west (glass bridge) | `[-10.6, -2.0]` | → `wispwood` (spawn `from_steps`) |
| **Hidden spring** | behind a vine curtain at `[10.2, -6.4]` | `game.spring` `{ secret: "alf_spring" }`, reached by a `game.bounces` toadstool at `[8.4, -4.6]` |
| Embassy flag post (decor) | `[-3.6, 9.0]` | Alfheim's banner: a silver tree on violet |

### 2.4 `lumen_court`: the Moonlit Court

The crown of the great tree, open to the sky. Moon-white stone is grown into the wood. In the middle stands an **Empty Throne**
of violet glass with a dust sheet over it (Sylvaine's).

| Spot | Pos | What |
|---|---|---|
| Spawn `from_steps` | `[0, 9.0, "up"]` | top of the spiral stair |
| **The Empty Throne** | `[0, -6.0]` | Regent Aerin stands **beside** it, never on it |
| Regent Aerin Vael | `[1.4, -5.2]` | talkable |
| Captain Faelan Thorne + 2 rangers | `[-4.4, -2.0]` | ranger post. On the conquer path they're hostile after the choice |
| **The Prism Library** (west wing) | `x -10..-6, z -2..4` | Mirelle's desk, shelves of glass books, a lens table (the evidence scene) |
| **The Prism Spire door** (east) | `[9.4, -4.0]` | a tall glass door, sealed by Aerin's key. Exit → `prismvault` (spawn `start`) |
| Moon-pool | `[-2.0, 4.0]` | a still pool reflecting the aurora; a checkpoint brazier (E4.1) |
| Glow-orb roost | `[5.0, 3.0]` | dozens of orbs sleeping in a lantern tree. During the Dimming, half are dark |

### 2.5 `wispwood`: the Wispwood (forest floor)

Dark forest floor between silverbark roots. Glow moss, red toadstools, ponds of glowfrogs, wisp nests in hollow stumps. It's the
outdoor combat area: rifts, a roaming rare, night foes.

| Spot | Pos | What |
|---|---|---|
| Spawn `from_steps` | `[10.0, -1.8, "left"]` | the end of the glass bridge, down a root stair |
| Wisp nests (5) | `[6.0, 4.0]`, `[2.4, -5.2]`, `[-3.0, 6.4]`, `[-7.6, -2.0]`, `[-1.0, 0.8]` | hollow stumps. *The Dimming*: one dimmed wisp each (section 5.3) |
| **Glowfrog ponds** (3) | `[4.4, 7.6]`, `[-5.6, 3.6]`, `[-9.0, -6.4]` | relight points for dimmed wisps; red, blue and violet frogs |
| **The frost scar** | `[-8.4, 6.8]` | a ring of dead, frosted vines around a flat stone: Veyra's rune-cutting site. `clue_stencil` look point |
| Lumi's hollow | `[-1.0, 0.8]` (the central nest) | Lumi, grey and flickering, curled in the nest at the start of *The Dimming* |
| `RIFT_AREAS.wispwood` | spots `[[3.6, 1.6], [-4.4, -4.6], [-2.4, 7.4]]` | foes `["prismshard", "willwisp", "crystalgolem"]` |
| `RARE_AREAS.wispwood` | spots `[[5.4, -3.6], [-6.0, 0.4]]` | bases `["shardmother", "glassstalker"]` |
| Garden plot | `[8.2, 3.0]` | an Alfheim plot (`kinds: ["violet", "coldfire", "toadcap"]`), tended by Ferrin's niece (decor) |
| Hidden spring | in a hollow log at `[-10.0, 1.0]` | `{ secret: "ww_spring" }`. The vines in front only part when a light is near (your pet or Lumi). Text: `The vines part for your light.` |

`SPAWNS.wispwood` (suggested): 2 `willwisp`, 1 `crystalgolem`, 2 `prismshard` (night), 1 `willwisp` (night).

### 2.6 Weather: aurora and prism rain

`SKY.alfheim = SKY.lumen_court = SKY.wispwood = "prism"`.

```js
// weather.js
KINDS.aurora    = [{ preset: "aurora_band", rate: 1 }];     // slow curtains of violet / blue / green pixels high in the sky backdrop
KINDS.prismrain = [{ preset: "prism_rain", rate: 1.2 }];    // falling glints that split into 3 colour pixels (violet, blue, rose) on landing
// weatherAt(area, day, t), for the prism sky:
if (sky === "prism") {
  if (NIGHT(t)) return hash(day * 7 + 31) < 0.6 ? "aurora" : "clear";
  if (t >= 0.62 && t < 0.8) return hash(day * 5 + 77) < 0.3 ? "prismrain" : "clear";   // late-dusk showers, 3 days in 10
  return "clear";
}
```

| Weather | Effect (in `prism` areas) | Toast on arrival |
|---|---|---|
| **Aurora** | `spellCd +0.10` (spells come back 10% faster; this is the design's "mana regen", using the approved cooldown approach) | `The aurora is out. Your spells feel lighter.` |
| **Prism rain** | **light spells bounce once** (Prism Beam, the `light_orb` / `sparkle_burst` charms jump to 1 more foe), and **Mirror Duelists can go invisible** (they shimmer, then vanish for 3 s; you see their footprints splash) | `Prism rain. Light bends strangely, and something in the trees just vanished.` |

Wet ground from prism rain uses the build's existing glints, coloured by the 3 prism colours.

### 2.7 Wisp Night (festival)

- **When:** every 7th night in Alfheim (`S.day % 7 === 6`, at night), befriend path only, after *The Dimming* is done.
- **Look:** every glow orb in Lumenvale floats up to the canopy, and paper-and-glass **neon lanterns** are strung across the Lantern
  Walk. Ferrin's pool becomes the **wisp pond**, where elves release relit wisps. Stalls sell festival lanterns.
  Music: the Lumenvale theme on celesta and glass harmonica, with a festival drum.
- **Banner on arrival:** `WISP NIGHT` / `Lanterns up, nets out. The rare wisps are dancing tonight.`
- **The hunt:** Nim's repeatable *Wisp Night* bounty (section 3.7). Rare wisps appear in the Wispwood and on the Steps.
- **The neon lantern fair:** Saelis sells 3 festival lanterns (cosmetic house decor later): `Moon-moth lantern`, `Frog lantern`,
  `Prism lantern` (30 g each, Wisp Night only).
- Conquer path: **no festival.** Lumenvale stays dark. Banner instead, on the 7th night: `The lanterns stay down tonight. No one
  is celebrating.`

---

## 3. Quests (`QUESTS` entries)

Helpers: `A(S) = ((S.flags || {}).alliance || {}).alfheim`; `F(S) = S.flags || {}`; `found(S, ids)` counts `S.found[id]`.

### 3.1 The Frozen Gate (story, both paths)

```js
alf_gate: {
  title: "The Frozen Gate",
  giver: "Gatewright Halvard Ness",
  story: true,
  steps: {
    1: (S) => { const f = F(S);
      if (!f.ag_struck) return "Strike Alfheim's frozen seal with the Keybearer's key (E / A at the violet gate, Bifrost Crossing).";
      if (!f.ag_sentinel) return "Defeat the frost sentinel that tore free of the seal!";
      return "Tell Gatewright Halvard the seal is broken."; },
    2: "Tell Gatewright Halvard the seal is broken.",
    3: "Alfheim's gate is open. Violet light spills across the Crossing.",
  },
},
```

- **Offer:** when `G.factions.rank("gate") >= 3` (Keybearer). It's a new `gatewright` hook option, `"About the frozen gates..."`, plus `quest_mark`.
- **Stage 1:** E / A at the Alfheim arch with `thawkey` → a cut-in where the frost cracks, then the **frost sentinel** steps out of the
  ice (a fixed spawn: an `icegolem` re-skinned as `frostsentinel`, 2× scale, section 8.2). Its death sets `ag_sentinel`.
- **Stage 1 → 2** on the kill; **2 → 3** at Halvard. Then the arch moves from `sealed` to `portals`, and the gate look in
  `GATES.alfheim` stops being shown.
- **Rewards:** **+60 Rift Marks** (`MERIT.thaw = 60`, gate), 50 gold, story XP.

### 3.2 A Name in Frost (story, befriend)

```js
alf_name: {
  title: "A Name in Frost",
  giver: "Regent Aerin Vael",
  story: true,
  steps: {
    1: (S) => { const f = F(S), inv = S.inv || {};
      if (!f.an_lens) return inv.blight_spike
        ? "Show the frost-iron spike to Mirelle at the Prism Library's lens table."
        : "Ask Mirelle in the Prism Library how to prove Alfheim innocent.";
      if (!f.an_stencil) return "Search the frost scar in the Wispwood, where the vines died of cold.";
      return "Bring the rune stencil to Mirelle's lens table."; },
    2: "Tell Regent Aerin what the lens shows.",
    3: "Alfheim's name is clear. The runes were cut by frost, and the frost came from somewhere cold.",
  },
},
```

- **Stage 1 sub-steps:**
  - `an_lens`: Mirelle reads the spike at the lens table, or explains what to look for if you don't have it (the no-spike variant, section 4.3).
  - `an_stencil`: the frost scar look point gives the item `frost_stencil`.
  - Then the lens table again with the stencil → stage 2.
- **Stage 2 → 3** at Aerin. It sets `flags.alf_cleared = 1` and `S.evidence.alfheim = "frost_stencil"`.
- **Rewards:** **+60 Realm Favor** (`MERIT.alf_name`), 40 gold. +20 more if you conquered Svartalfheim (`MERIT.rivalmood = 20`,
  `realm_mood.alfheim >= 1`). If you also carry **Mossbrook's apology** (`moss_letter`), +20 more
  Realm Favor (`MERIT.apology = 20`) and Aerin's extra line.

### 3.3 The Dimming (story, befriend)

```js
alf_dim: {
  title: "The Dimming",
  giver: "Mirelle Glasswing",
  story: true,
  steps: {
    1: (S) => { const f = F(S), n = found(S, ["dw_1", "dw_2", "dw_3", "dw_4", "dw_5"]);
      if (!f.dm_lumi) return "Find the grey old wisp in the Wispwood's central nest.";
      if (n < 5) return `Carry dimmed wisps to a glowfrog pond to relight them (E / A at a nest, then a pond). ${n}/5`;
      if (!f.dm_trail) return "Follow the thread of drained light from the ponds. Lumi can see it.";
      return "Tell Mirelle where the light is going."; },
    2: "Tell Regent Aerin the light drains into the Prism Spire.",
    3: "The wisps burn again, for now. The light was draining into the Prism Vault, and Lumi is with you.",
  },
},
```

- **Offer:** from Mirelle right after *A Name in Frost* is done.
- **Relighting (`dw_1..5`):** E / A at a nest; Lumi chimes and the dimmed wisp follows you as a grey mote. E / A at any glowfrog pond
  relights it: the frogs sing, the wisp flares blue-violet and flies home, and `S.found.dw_n` is set. One at a time.
- **The trail (`dm_trail`):** after 5, Lumi (bright again) shows a thin **violet thread** on the ground (a dotted decal) from the central nest
  to the root stair, then up through the Steps to the Court's Spire door. Touching the door sets `dm_trail`.
- **Stage 1 → 2** at Mirelle. **2 → 3** at Aerin, who gives the Spire key (`spirekey`) and starts *The Prism Vault*.
- **Rewards:** **+80 Realm Favor** (`MERIT.alf_dim`), Lumi joins (`flags.companions.lumi = 1`), 60 gold.

### 3.4 The Prism Claim (story, conquer)

```js
alf_take: {
  title: "The Prism Claim",
  giver: "Regent Aerin Vael",
  story: true,
  steps: {
    1: (S) => { const f = F(S), n = found(S, ["pc_r1", "pc_r2", "pc_r3"]);
      if (n < 3) return `Break the ranger posts guarding the Spire bridge. ${n}/3`;
      if (!f.pc_faelan) return "Captain Faelan Thorne holds the Spire key. Take it from her.";
      return "Open the Prism Spire door with Faelan's key."; },
    2: "Open the Prism Spire door with Faelan's key.",
    3: "The Spire is yours. Below it lies the Prism Heart, and whatever the elves locked up with it.",
  },
},
```

- **Starts** on the conquer choice (section 5.4). The giver field credits the Regent's refusal.
- **Ranger posts** (`pc_r1..3`): three groups of 2 `lightranger` along the Court's east walk. Clearing a group sets its flag.
- **Faelan** is a 1.3× elite duel (`faelan`, section 8.2). She yields at 25% HP (no kill), drops `spirekey` and sets `pc_faelan`.
- **Stage 1 → 2** on the key; **2 → 3** at the Spire door (E / A). Starts *The Prism Vault*.
- **Rewards:** **+60 Rift Marks** (`MERIT.claim = 60`, gate), 80 gold.

### 3.5 The Prism Vault (story, both paths)

```js
prismvault: {
  title: "The Prism Vault",
  giver: "Regent Aerin Vael",
  story: true,
  steps: {
    1: (S) => { const f = F(S), n = found(S, ["pv_lens1", "pv_lens2", "pv_lens3"]);
      if (n < 3) return `Realign the Vault's three great lenses (light-beam puzzles). ${n}/3`;
      if (!f.pv_boss) return "Descend to the Heart Prism. Something is awake down there.";
      return A(S) === "conquer" ? "Take the Prism Heart and leave the Vault." : "Reseal the Heart Prism (E / A at the Heart)."; },
    2: (S) => A(S) === "conquer" ? "Leave Alfheim with the Prism Heart." : "Return to Regent Aerin in the Moonlit Court.",
    3: (S) => A(S) === "conquer"
      ? "The Prism Heart is yours. Lumenvale's lights are going out, one by one."
      : "Sylvaine is resealed, asleep in the Heart Prism, fed and at peace. Alfheim calls you friend.",
  },
},
```

- **Stage 1:** three lens rooms (P2, P4, P6), then the boss (P8). The kill sets `pv_boss`. Then E / A at the Heart sets `pv_sealed` (befriend)
  or `pv_taken` (conquer, gives `prism_heart`), and moves to stage 2.
- **Stage 2 → 3:** befriend, at Aerin (section 6.9). Conquer, on leaving the `alfheim` hub for Bifrost.
- **Rewards:** see section 9. `flags.alf_resolved = "befriend" | "conquer"`. Veyra's beat plays on the next area load.

### 3.6 The Dancing Blade (ripple, befriend)

```js
alf_edge: {
  title: "The Dancing Blade",
  giver: "Mirelle Glasswing",
  ripple: true,
  steps: {
    1: (S) => { const n = Math.min(3, (S.inv || {}).prism_glass || 0);
      return n < 3 ? `Bring Mirelle 3 prism glass from the Vault's crystal foes. ${n}/3` : "Bring the prism glass to Mirelle."; },
    2: "Stand with Mirelle at the Empty Throne at night while she wakes the blade.",
    3: "The Prism Edge dances at your side. Sylvaine's sword, freed of her hunger.",
  },
},
```

- **Offer:** befriend, `prismvault === 3` and **Realm Favor Honored** (`rank("embassy") >= 3`, 800). Mirelle: the Queen's sword,
  *the Long Light*, has hung behind the throne since the sealing.
- **Stage 1 → 2** at Mirelle with 3 `prism_glass`. **2 → 3** at night by the throne (a short scene, section 6.11).
- **Reward:** the **Prism Edge** (section 9.1). As a ripple quest it's skipped by `errandsDone`.

### 3.7 Wisp Night (bounty, repeatable, befriend)

```js
wispnight: {
  title: "Wisp Night",
  giver: "Nim",
  side: true, bounty: true,
  steps: {
    1: (S) => { const w = S.wispHunt || { n: 0, rare: 0 };
      return w.n < 5 || !w.rare ? `Catch 5 wisps tonight, at least 1 rare (E / A with the net). ${Math.min(5, w.n)}/5 · rare ${w.rare ? "✓" : "–"}`
                                : "Show Nim your catch on the Glimmer Steps."; },
    2: "Show Nim your catch on the Glimmer Steps.",
    3: "Wisp Night done. The wisps you caught are dancing on Ferrin's pond.",
  },
},
```

- **Offer:** on Wisp Night (section 2.7) if `quests.wispnight` is 0. It resets from 3 to 0 at the next Wisp Night, and `S.wispHunt` resets too.
- **Catching:** with the `wisp_net` (Nim gives it the first time), E / A within 1.2 m of a festival wisp. Common wisps drift.
  Rares blink away once before they can be caught.
- **Rewards:** **+40 Realm Favor** (`MERIT.wispnight`), 30 gold, and each rare caught for the first time goes into the **wisp
  catalog** (Prismdancer hook, section 9.4). The `bounty` tag means no Hearth payout and half XP on repeats.

### 3.8 Stage tables

| Quest | Stage | Done when | Flags |
|---|---|---|---|
| alf_gate | 1 | the seal is struck, the sentinel killed | `ag_struck`, `ag_sentinel` |
| alf_gate | 2 → 3 | talk to Halvard | sets `alf_gate_open` |
| alf_name | 1 | the lens reads the spike (or the no-spike line), the stencil is found and read | `an_lens`, `an_stencil`, item `frost_stencil` |
| alf_name | 2 → 3 | talk to Aerin | `alf_cleared`, `S.evidence.alfheim` |
| alf_dim | 1 | Lumi found, 5 wisps relit, the trail followed | `dm_lumi`, `S.found.dw_1..5`, `dm_trail` |
| alf_dim | 2 → 3 | talk to Aerin | `companions.lumi`, item `spirekey` |
| alf_take | 1 | 3 ranger posts broken, Faelan yields, the door is opened | `S.found.pc_r1..3`, `pc_faelan`, item `spirekey` |
| prismvault | 1 | 3 lenses realigned, Sylvaine defeated, the Heart sealed or taken | `S.found.pv_lens1..3`, `pv_boss`, `pv_sealed` / `pv_taken` |
| prismvault | 2 → 3 | Aerin (befriend) or leaving Alfheim (conquer) | `alf_resolved` |
| alf_edge | 1 → 2 → 3 | 3 prism glass, the night scene | item `prism_edge` (gear) |
| wispnight | 1 → 2 → 3 | 5 wisps incl. 1 rare, show Nim | `S.wispHunt`, `S.wisps` |

### 3.9 New `MERIT` keys (within the existing scale: boss 80, abyssal rift 120)

```js
thaw: 60, claim: 60,                                   // Guild (gate): the Frozen Gate; the Prism Claim (conquer pays Rift Marks)
alf_name: 60, apology: 20, rivalmood: 20, alf_dim: 80, vault: 120,    // Realm Favor (embassy), befriend
vault_c: 120,                                          // Rift Marks (gate), conquer: the Vault taken
wispnight: 40,                                         // Realm Favor, once per festival
```

The Sylvaine kill also pays `onBoss` (+80) to `realm()`: embassy (befriend) or gate (conquer).

---
## 4. The poisoned-springs evidence (Alfheim framed)

### 4.1 What the evidence proves

| Evidence | From | What the lens shows |
|---|---|---|
| **Frost-iron spike** (`blight_spike`, `S.evidence.vanaheim`) | the Blight Regent's heart (`verdant_heart.md`) | Alfheim rune-shapes, but **cut cold**: elf runes are burned with light, never carved, and elves never work iron |
| **Rune stencil** (`frost_stencil`, new) | the frost scar in the Wispwood | a thin plate of frost-iron with Alfheim runes cut out, so anyone could trace them. Rimed, never warm. The same hand as the spike |
| **Mossbrook's apology** (`moss_letter`, new, optional) | Burrowmoss, if Vanaheim is befriended | Vanaheim withdraws the charge. It's a political proof, not a physical one |

Together they prove the runes were **forged by someone who works frost-iron**. That's no elf and no dwarf (dwarves work hot iron).
The trail points **cold**, toward Niflheim. `S.evidence.alfheim = "frost_stencil"` is the second piece for the midpoint reveal.

### 4.2 Mossbrook's apology (`moss_letter`)

Burrowmoss gives it on your next talk with him once `alf_gate === 3` and `alliance.vanaheim === "befriend"`:

```js
pages: [
  "Alfheim's gate is open? Then take this. Mossbrook's apology, in my own hand. Took me four drafts.",
  "Tell the elves we were wrong. Tell them nicely. Tobble wanted to add a drawing. I let him.",
],
then: (G) => { G.give("moss_letter", 1); flags(G.S).moss_letter = 1; },
```

### 4.3 The lens table scenes (Mirelle)

**With the spike** (`an_lens`):
```js
pages: [
  "A frost-iron spike? From Vanaheim? Lay it on the lens. Gently. Iron makes the glass grumpy.",
  "(Violet light pours through the lens. The runes on the spike glow, but their edges stay dark and rimed.)",
  "See that? Our runes are burned with light. These were carved. Cold. By someone who's never lit a rune in their life.",
  "That's half a proof. Somebody made these. If they practised, they practised near here. Look for dead vines.",
],
then: (G) => { flags(G.S).an_lens = 1; },
```

**Without the spike** (Vanaheim skipped, or you no longer have it):
```js
pages: [
  "Vanaheim says our runes are on their moss. Fine. Runes can be copied. But copying takes practice.",
  "Whoever did it would need a quiet place, a cold one. Vines die near frost-iron. Look for a ring of dead vines.",
],
then: (G) => { flags(G.S).an_lens = 1; },
```

**The frost scar** (`clue_stencil` look point, `{ id: "clue", name: "The frost scar" }`):
```js
pages: [
  "A ring of dead vines, white with frost, around a flat stone. The frost hasn't melted in weeks.",
  "Under the stone: a thin frost-iron plate with Alfheim runes cut clean through it. A stencil.",
],
then: (G) => { G.give("frost_stencil", 1); flags(G.S).an_stencil = 1; G.toast("Found: a frost-iron rune stencil. Evidence.", 2.6); },
```
- Seer extra page: `"(Your runes recognise the hand. The same cold patience as the spike, the tongs, the snuffer.)"`
- Grovekeeper extra page: `"(The dead vines whisper to you: cold hands, a grey-blue cloak, a long time kneeling here.)"`

**The stencil on the lens:**
```js
pages: [
  "(The stencil and the spike lie side by side. Under the lens, the cut marks line up perfectly.)",
  "Same tool. Same cold hand. This isn't Alfheim's work. It isn't even Midgard's.",
  "Take it to the Regent. And... thank you. We've been shouting 'it wasn't us' at a frozen gate for months.",
],
then: (G) => G.setQuest("alf_name", 2),
```

### 4.4 Conquer path: the evidence used the other way

If you chose conquer, *A Name in Frost* never starts. You **can** still find the stencil (the frost scar works on both paths),
but nobody in Alfheim will look at it with you. Mirelle, if you talk to her on the conquer path while carrying the spike or
stencil, says this once: `"You carry proof we're innocent. And you came with a sword anyway."`

The evidence still counts for the midpoint reveal (`S.evidence.alfheim = "frost_stencil"` when picked up, on either path), but on
the conquer path Alfheim stays an enemy.

---

## 5. NPC roster

All characters wear normal clothes: a separate top and bottom with a visible waist. No onesies, no armour-suits.
Elves are tall and slim with long ears, pale skin with a faint violet sheen at night, and violet or silver eyes.

| Name (TALK id) | Role | Look | Where |
|---|---|---|---|
| **Regent Aerin Vael** (`regent`) | Lumenvale's regent for 300 years; Sylvaine's great-great-granddaughter. She refuses the throne | silver hair in a low braid, a slim silver circlet, a violet high-collared blouse, a charcoal wrap skirt with a silver sash at the waist, soft grey boots | `lumen_court`, beside the Empty Throne |
| **Mirelle Glasswing** (`librarian`) | keeper of the Prism Library; rune scholar and the Vault's guide | round glass spectacles, a messy bun with a stylus through it, a cream shirt with rolled sleeves, a violet vest, a brown pleated skirt, a belt of lens pouches | `lumen_court`, Prism Library |
| **Captain Faelan Thorne** (`ranger`) | captain of the light-elf rangers; suspicious of Midgard; the conquer-path duel | cropped silver hair, a dark-green leather vest over a grey linen shirt, belted trousers, knee boots, a longbow, a violet cloak clasp | `lumen_court`, ranger post |
| **Lumi** (`lumi`) | a speaking, sentient **wisp**; companion (befriend). She was the **nursery's own wisp**, the light that lit Sylvaine's nursery, and the first light Sylvaine ever drank from. She got away, and she's free now | a glowing orb about **2× the wisp kit**: a neon-blue core with a pulsing violet halo, two bright white eyes and a curling particle tail. She casts a real pool of light. Grey and flickering when dimmed | `wispwood` central nest, then with you |
| **Nim** (`wispcatcher`) | elf kid, wisp catcher; runs the Wisp Night hunt | an oversized knitted violet jumper with rolled sleeves, short brown trousers with a rope belt, muddy knees, a wisp net taller than she is | `alfheim`, Nim's perch |
| **Ferrin** (`poolkeeper`) | old pool-tender who looks after the glowfrogs | a long white ponytail, a moss-green waistcoat over a collarless shirt, wide trousers rolled at the ankle, braces, a straw hat with a lily-pad brim | `alfheim`, glow-pool |
| **Saelis** (`lanternseller`) | lantern seller (shop) | a sleeveless violet top, a wide leather belt, a long dark skirt, arms inked with glowing fish tattoos that swim slowly | `alfheim`, Wisp Market |
| **Brokk Emberlode** (`dwarftrader`) | a dwarven trader from Anvildeep; the Svartalfheim rival setup | a rust-coloured wool shirt, a leather apron belted over trousers, a soot-black beard with brass beads, half the player's height | `alfheim`, Wisp Market |
| Lumenvale folk (`elf1`–`elf3`) | ambient townsfolk (`say` lines only) | tunics and blouses, trousers and skirts, sashes; one carries a glowfrog in a jar | the Steps and the Court |
| **Lady Sylvaine** (boss) | Alfheim's first queen, the light-drinker | section 8.1 | `prismvault` P8 |

**Shop:** `SHOPS.lumen = { name: "Saelis's Lanterns", keeper: "Saelis, lantern seller", goods: ["tonic", "glowseed", "dewdrop"],
gems: ["moon_opal"], gear: { n: 3, rar: [1, 1, 2] }, sellMul: 1 }`. Festival lanterns are added on Wisp Night. Conquer path: prices ×1.5 and
the gear is Common only (`rar: [0, 0, 0]`).

### 5.1 Gatewright Halvard: the Frozen Gate (Bifrost)

New hook (Keybearer only), `"About the frozen gates..."`:
```js
pages: [
  "Keybearer. Has a ring to it. And a key, now. This one took some cutting. Longer than it should have.",
  "Alfheim's seal is frozen from the far side. Veyra's work, they say. Strike it with this and step back. Quickly.",
],
then: (G) => { G.give("thawkey", 1); G.setQuest("alf_gate", 1); },
```
- Striking the seal (E / A at the Alfheim arch, stage 1): `(The key bites into the frost. The ice groans... and something inside it stands up.)`
- Turn-in (stage 2):
```js
pages: [
  "The seal's broken? Good. Good. The ledger will say so.",
  "Odd thing. That frost took my key like it knew the shape. I'll check the stock. Keys go missing, you know.",
  "Alfheim's open. Mind the elves. They've been shouting through a frozen door for months. They'll be cross.",
],
then: (G) => { G.setQuest("alf_gate", 3); G.factions.add("gate", MERIT.thaw, "thaw"); gold(G, 50); flags(G.S).alf_gate_open = 1; },
```
- Later idle line: `"Alfheim's gate glows violet all night now. Pretty. Loud, though. Elves sing at the oddest hours."`

### 5.2 Regent Aerin Vael (`regent`)

**First audience: the alliance choice** (`!A(S)`):
```js
pages: [
  "A Midgard face. The first through our gate in months. I am Aerin Vael, Regent of Lumenvale.",
  "Mossbrook calls us poisoners. Midgard sends you. And our own wisps are going dark. It has not been a good season.",
  "So tell me plainly, hearth-walker. Are you Alfheim's friend, or one more accuser at the door?",
],
choice: { id: "alliance_alfheim", options: [
  { label: "A friend. Let me prove you innocent.", locked: (S) => (((S.flags || {}).rivals || {}).alfheim === "locked"),
    lockedLabel: "(Locked. You stand with Anvildeep.)", pick: (G) => { ally(G.S).alfheim = "befriend"; G.toast("Alfheim: befriended", 2.2);
      G.setQuest("alf_name", 1); lockRival(G.S, "svartalfheim");
      return { pages: ["Then you are welcome under our boughs. Mirelle keeps the Prism Library. If proof exists, she will see it.",
                       "(Alfheim is your friend now. Its rival, Svartalfheim, will not stand with you as well.)"] }; } },
  { label: "Alfheim will answer to Hearthmoor.", pick: (G) => { ally(G.S).alfheim = "conquer"; G.toast("Alfheim: conquered", 2.2);
      G.setQuest("alf_take", 1); moodUp(G.S, "svartalfheim");
      return { pages: ["...I see. Then you will find the Spire barred, and Captain Thorne between you and it.",
                       "(Alfheim stands against you now. The light elves will remember.)"] }; } },
  { label: "I'm only passing through.", cancel: true, pick: () => ({ pages: ["Then pass gently. Our light is thin enough already."] }) },
] },
```
- **Rival mirror (`svartalfheim.md` 1.1):** if you befriended Svartalfheim, the befriend option is greyed (`locked`), with the opener
  `"Anvildeep's friend, at my door. Bold. Say your piece."` If you conquered Svartalfheim (`realm_mood.alfheim >= 1`), the opener is
  `"You humbled Anvildeep? Then perhaps Midgard is not all cold iron. Sit."`, and Faelan's first line softens to
  `"You broke the Hushed. Hm. I still don't like Midgard. I like you slightly more."`
- Seer variant (an extra first option, befriend only): `"Your runes on Mossbrook's moss were forged. I've seen the hand."` →
  same as befriend, plus the line `"...You've seen it too? Then perhaps we are not mad after all."`
- Holding the spike: Aerin adds a page before the choice: `"You carry frost-iron. I can feel it from here. Is that Vanaheim's 'proof'?"`

**A Name in Frost, turn-in** (stage 2):
```js
pages: [
  "Carved cold. A stencil. The same hand. So we were framed, and framed by someone patient.",
  "Alfheim thanks you, and Alfheim does not say that often. Ask my advisers. They keep a list.",
  "But proof will not light our wisps. Mirelle has been watching them die. Go to her. Please.",
],
then: (G) => { G.setQuest("alf_name", 3); G.factions.add("embassy", MERIT.alf_name, "alf_name"); gold(G, 40);
               flags(G.S).alf_cleared = 1; G.S.evidence = { ...(G.S.evidence || {}), alfheim: "frost_stencil" };
               if ((G.S.inv || {}).moss_letter) G.factions.add("embassy", MERIT.apology, "apology");
               if ((G.S.flags.realm_mood || {}).alfheim >= 1) G.factions.add("embassy", MERIT.rivalmood, "rivalmood");
               G.setQuest("alf_dim", 1); },
```
- With Mossbrook's apology, an extra page after the first: `"And a letter from Mossbrook. With a drawing of a... mushroom? Tell them we accept."`

**The Dimming, turn-in** (stage 2):
```js
pages: [
  "Into the Spire. Into the Vault. Of course it is. Of course it is her.",
  "My great-great-grandmother, Sylvaine. Our first queen. She feared the dark so much she began to drink the light.",
  "We sealed her in the Vault, in endless light, so she would sleep fed. If the prisms are cracked, she is waking.",
  "Here is the Spire key. Mirelle will guide you. Put her back to sleep. Please. She was someone's grandmother once.",
],
then: (G) => { G.setQuest("alf_dim", 3); G.factions.add("embassy", MERIT.alf_dim, "alf_dim"); gold(G, 60);
               G.give("spirekey", 1); G.setQuest("prismvault", 1); },
```

**Idle lines:**

| Condition | Line |
|---|---|
| befriend, default | `"The throne stays empty. A regent is a promise to keep the chair warm, not to sit in it."` |
| befriend, night | `"The aurora's out. When I was small, I thought it was the queen dancing. Now I know better."` |
| befriend, Vault done | `"She sleeps. I went down and sat with her. I told her about the frogs. She'd have liked the frogs."` |
| befriend, Wisp Night | `"Wisp Night! Go and catch something. Regents don't get to. It's in the rules. I wrote them, sadly."` |
| conquer | `"Say what you came to say, Midgarder. Then go, and take your cold with you."` |
| conquer, Vault done | `"You took the Heart. Look at the trees. Every light you see is a light going out."` |
| neutral (passing through) | `"Still deciding what you are to us? Take your time. We are elves. We have plenty of it."` |

### 5.3 Mirelle Glasswing (`librarian`)

**First meeting:** `"Oh! Hello. Mind the shelves, the books are glass. Mirelle Glasswing, Prism Library. Do you like lenses?"`

**The Dimming, offer** (on *A Name in Frost* done):
```js
pages: [
  "Our wisps are dimming. One a night, then two. They don't die. They go grey, and they stop singing.",
  "There's an old wisp in the Wispwood. Lumi. She talks. Rudely, to regents. If anyone knows where light goes, she does.",
  "Relight the dimmed ones in the glowfrog ponds. The frogs sing light back into them. Don't ask how. They just croak.",
],
then: (G) => G.setQuest("alf_dim", 1),
```
- Reminder: `["The glowfrog ponds. Carry the grey wisps to the frogs, and the frogs will do the rest."]`
- **Turn-in** (stage 1 → 2): `["The Spire? Lumi's sure? Then it's the Vault. Then it's her. Tell the Regent. I'll pack lenses. Lots of lenses."]`
- **Prism school unlock** (befriend, Vault done, Realm Favor Friend, first talk after): see section 9.2.

**Idle lines:**

| Condition | Line |
|---|---|
| default | `"Light bends, you know. So do people. The trick is finding the right angle."` |
| prism rain | `"Prism rain! Everything's in three colours. I've been sneezing rainbows all morning."` |
| night | `"The library glows at night. I sleep under the desk. Don't tell the Regent. She knows."` |
| Vault done | `"I measured the Heart Prism this morning. It's humming. Content. I think that's her snoring."` |

### 5.4 Captain Faelan Thorne (`ranger`)

| Condition | Line |
|---|---|
| first meeting (before the choice) | `"Faelan Thorne, ranger captain. I don't like Midgard. Nothing personal. I don't like anyone."` |
| befriend, default | `"You cleared our name. I'll grudgingly admit that's useful. Don't make me say it twice."` |
| befriend, night | `"The rangers walk the canopy at night. The aurora makes good light for arrows. And for thinking."` |
| befriend, Vault done | `"You went down there and came back. I've known rangers who wouldn't. I've known rangers who didn't."` |
| conquer, on the choice | `"So that's what you are. Rangers! To the Spire bridge. Nobody passes."` |
| conquer, duel start | `"You want the key? Earn it. I'll make you sweat for every step."` |
| conquer, yields (25% HP) | `"Enough. Take it. Take the key. Whatever you find down there, you woke it, not us."` |
| conquer, afterwards | `"(Faelan turns her back on you. The rangers do the same, one after another.)"` |

### 5.5 Lumi (`lumi`, wisp companion)

**Who she is:** a **speaking, sentient wisp**, very old and very stubborn. Four hundred years ago she was the **nursery's own wisp**,
the light that hung over the cradle where the girl Sylvaine slept. When Sylvaine grew hungry, Lumi was the **first light she drank from**.
Lumi tore free half-grey and hid in a frog pond until the frogs sang her bright. She has lived wild in the Wispwood ever since,
answering to no one. She's warm, cheeky and fiercely protective of every light. She says "Ting" when she's pleased.

**Not the wisp kit (for Art and Systems):** the wisp kit pet is a **small, wordless** palm-sized orb that hums. Lumi is about **2× its size**,
**talks** (full lines with a name tag), has a **two-tone** glow (a neon-blue core with a violet halo, where the kit is one flat blue) and
a long curling particle tail. She also fights (her kit, below). Both can be out together: the kit bobs at your knee and Lumi floats higher, at
head height.

**Sprite notes (for Art):** a glow orb, with no body and no clothes.
- **Core:** a neon-blue orb (`#5ac8ff`) about 2× the wisp kit's sprite, with two bright white dot eyes that blink and squint (happy / cross / sleepy).
- **Halo:** a soft violet ring (`#a45cf0`) around the core that **pulses** (scale 1.0 → 1.15, ~1.2 s).
- **Trail:** a curling tail of blue-to-violet pixel particles, 6–8 motes that fade over 0.5 s, longer when she moves fast.
- **Light:** a real point light that throws a visible **pool of light** on the ground under her (`fx.pool`), like the pets' pools but bigger.
- **States:** idle bob, dart (a stretched orb plus a long trail), cast (the halo flares and 2 sparks split off), hurt (a white flash), dimmed
  (grey core, no halo, a stuttering light) and sleepy (eyes half-shut, a slow pulse).
- **No bloom**, in line with the build's glow rules: the light pool, halo and particles do the work.

**Finding Lumi** (stage 1, `dm_lumi`):
```js
pages: [
  "(A grey wisp, bigger than most, curls in the bottom of the nest. It flickers. Two dim eyes open.)",
  "Lumi: \"Ting. Oh. A warm one. You smell like hearth and spring water. Nice. I'm... very tired.\"",
  "Lumi: \"Something's drinking us. From under the city. I know that thirst. It drank me first, long ago.\"",
  "Lumi: \"Help the others first. Frogs can sing us bright. Then I'll show you where the light goes.\"",
],
then: (G) => { flags(G.S).dm_lumi = 1; },
```
- After 5 relit (Lumi flares neon blue, `dm_trail` shown): `"Lumi: \"Ting-ting! Bright again! See the thread? The light's going up. To the Spire.\""`
- **Joins** (at *The Dimming*'s end): `"Lumi: \"I'm coming with you. Don't argue. I'm older than your whole village. Ting.\""`

**Companion data shape** (the companion system isn't built; `flags.companions.lumi = 1` marks her as recruited). Hover and light follow
the `PETS` shape so the pet follow code can carry her:
```js
export const COMPANIONS = {
  lumi: { name: "Lumi", kind: "wisp", talks: true, role: "companion_lumi", realm: "alfheim", scale: 2.0,   // 2x the wisp kit
          hover: { lift: 1.1, bob: 0.08, hz: 0.7 },                                     // head height, above any pet
          glow: "#5ac8ff", halo: "#a45cf0",
          light: { color: "#5ac8ff", intensity: 5.5, range: 4.2, lift: 1.1, pulse: [0.85, 1.15, 0.8], r: 2.6 },   // a real light pool
          fx: { aura: "lumi_halo", pool: "lumi_pool", parts: "lumi_trail" },
          kit: {
            call:  { wisps: 2, life: 12, cd: 18, dmg: 6, reach: 3.2, ranged: true },     // Wisp Call: 2 mini-wisps orbit you and zap foes
            light: { r: 2.2 },                                                          // a light zone round you (the Lantern glow buff: +10% dmg, faster stamina)
            mark:  { crit: 0.05, every: 8 },                                            // she marks the nearest foe: +5% crit on it
          },
          about: "A talking wisp, twice a wisp kit's size. Once the light of Sylvaine's nursery. Free now, and staying with you." },
};
```

**Combat role:** support. She never melees. Every 18 s her halo flares and she **calls 2 mini-wisps** (small sparks of her own light) that
orbit you for 12 s and zap foes in reach. Her **light zone** round you counts as a light zone for the Sylvaine fight and for light-shy foes.
Every 8 s she **marks** the nearest foe (a violet ring). Suggested rule: when you faint, she dims and is back at your side at the waystone.

**Companion barks** (`{ id: "lumi", name: "Lumi" }`, shown above her like NPC barks):

| Trigger | Line |
|---|---|
| follow | `"Ting! Left, left, no, your other left."` · `"I like your boots. They're very... stompy."` |
| night | `"Night! Finally. Days are too bright. I can't see myself."` |
| aurora | `"The sky's dancing. The old queen used to dance like that, before."` |
| prism rain | `"Ooh, tickly rain. Everything's sparkling. Me most of all."` |
| near a glowfrog pond | `"Hello, frogs! (The frogs sing back. Lumi glows a little brighter.)"` |
| combat start | `"Bright and sharp! I'll light them up for you!"` |
| Wisp Call | `"Out you come, little ones! Bite!"` |
| low HP | `"You're flickering! Drink something! The red one!"` |
| a hidden spring nearby | `"Ting? Something fizzy behind those vines. I can hear it."` |
| your wisp kit pet is out | `"Hello, small one. (The wisp kit hums. It doesn't talk. Most wisps don't. I'm special.)"` |
| Bifrost | `"So many gates. Most of them are frowning. Alfheim's isn't, now. Because of you."` |
| Hearthmoor | `"Your village is so warm. Everything smells like bread. Is it always like this? Can I stay?"` |
| Vanaheim | `"Mushroom people! They used to be cross with us. Not anymore. You did that."` |
| rift storm | `"The storm's loud. I'm not scared. I'm just floating very close to you. On purpose."` |
| the Prism Vault | `"I've been here before. I hung over her cradle. She was smaller. So was I."` |

### 5.6 Nim (`wispcatcher`)

| Condition | Line |
|---|---|
| first meeting | `"Shh! There's a wisp right... it's gone. I'm Nim. I catch wisps. Well. I chase wisps. Catching's harder."` |
| Dimming active | `"My wisps went grey. All of them. I put them in a jar and sang to them. It didn't work. I'm a bad singer."` |
| befriend, default | `"There are nine rare wisps. I've seen four. I've caught none. One day."` |
| Wisp Night (offer) | `"It's Wisp Night! Here, take a net. Catch five, and at least one rare. The rare ones blink. Be quick!"` |
| Wisp Night, turn-in | `"Five! And a rare one! You're better at this than me. I'm not jealous. I'm very jealous."` |
| a new rare in the catalog | `"A ${name}! That's in my book! Can I draw it? Hold still. Not you. The wisp."` |
| all 9 rares caught | `"All nine. ALL NINE. Nobody's done that since the old stories. The Prismdancers did. You should meet one."` |
| conquer | `"(Nim hides her net behind her back and won't look at you.)"` |

### 5.7 Ferrin the pool-tender (`poolkeeper`)

| Condition | Line |
|---|---|
| first meeting | `"Mind the frogs. That's Duchess, the blue one. She bites. Affectionately. I'm Ferrin. I tend the pools."` |
| Dimming active | `"The frogs know how to sing light back. They've been singing all night. Hoarse, poor things."` |
| a wisp relit at his pool | `"Listen to them go! Every frog in the pool singing for one little wisp. That's Lumenvale for you."` |
| befriend, default | `"Bryony in Ravenhold has one of my frogs, you know. Bloop. Named him herself. Terrible name. Lovely frog."` |
| night | `"Night chorus. Best music in the Nine Realms. Don't let the bards hear me say that."` |
| conquer | `"The frogs went quiet when you came in. They know. Frogs always know."` |

### 5.8 Saelis the lantern seller (`lanternseller`)

- First: `"Lanterns! Neon ones, prism ones, and those funny Midgard fish ones. Everyone loves the fish ones."`
- Default: `"Every lantern here holds a little wisp-light. Freely given. We ask nicely. That's the elf way."`
- Wisp Night: `"Festival lanterns! Moon-moth, frog or prism. Thirty gold. Hang one up and it remembers tonight."`
- Conquer: `"Prices went up. For you. Don't look at me like that. Look at the trees."`

### 5.9 Brokk Emberlode (`dwarftrader`, the Svartalfheim setup)

| Condition | Line |
|---|---|
| first meeting | `"Brokk Emberlode, Anvildeep. Yes, a dwarf in Alfheim. The elves glare. I glare back. It's tradition."` |
| before the choice | `"The elves blame us for half their troubles. We blame them for the other half. Keeps things tidy."` |
| befriend (once, then he's gone) | `"So you've thrown in with the light-ears. Fine. Anvildeep keeps a ledger too, Midgarder. Don't forget it."` |
| conquer | `"Ha! Somebody finally put the elves in their place. Anvildeep will drink to you. Loudly."` |
| conquer, later | `"Come see us under the mountain someday. The forges are warm and the welcome's warmer. For you."` |

On befriend, Brokk's stall is empty after the next area load (`flags.brokk_left = 1`). Orri in the Forge Quarter afterwards:
`"Heard you sided with the elves. Anvildeep holds grudges the way I hold tongs. Tight, and for years."`

### 5.10 Lumenvale folk (ambient `say`)

- `"Another wisp went grey last night. Three streets over. I keep my lantern lit, just in case."` (during the Dimming)
- `"Mossbrook called us poisoners. Us! We can't even poison a slug. We apologise to the slugs."`
- `"Is that a Midgarder? They're shorter than I thought. And louder."`
- `"The aurora's coming in green tonight. Green means luck. Or rain. It's usually rain."`
- Befriend, after the Vault: `"The wisps are singing again. I'd forgotten how loud they are. I'd forgotten I liked it."`
- Conquer: `"(The elf looks away and pulls her lantern closer.)"`

---
## 6. Story scenes

### 6.1 Arrival in Lumenvale (first load of `alfheim`)

Banner: `ALFHEIM` / `Lumenvale, city of the light elves`. Then a short narration (`{ id: "narr", name: "Lumenvale" }`):
```js
pages: [
  "(Silverbark trees taller than towers. Vines of violet light. Glow orbs drifting like slow bubbles.)",
  "(Below the bridges, dark pools shine blue, and somewhere, a thousand frogs are singing.)",
  "(But here and there, a wisp hangs grey and silent in the branches, like a lamp someone forgot to light.)",
],
```
Lumenvale folk turn and stare. Their first `say` line: `"A Midgarder. Through the gate. Somebody fetch the Regent."`

### 6.2 Conquer path: the Spire bridge

Approaching the east walk after the conquer choice, Faelan's post calls out (overhead `say`): `"Rangers, hold the bridge!"`
The three posts (`pc_r1..3`) fight in turn. After the 3rd, Faelan steps out (section 5.4) for the duel. Her yield line ends it.
Opening the Spire door (stage 2 → 3): `(The glass door swings inward. Cold air rises from below, and a faint sound, like someone humming.)`

### 6.3 The Vault: Mirelle's speaking lens (befriend)

Mirelle stays in the Library and talks through a **speaking lens** you carry (`speaklens`, given with the Spire key). Her lines play
as overhead text with her portrait. Lumi, floating with you, adds hints.

| Room | Mirelle | Lumi |
|---|---|---|
| P0 | `"Can you hear me? Good. Light the stair brazier. The Vault likes visitors who bring their own light."` | `"Ting. It smells like old dust and older light. I remember it."` |
| P1 | `"Those are prism shards. Loose bits of the Vault. They fire whatever light they've swallowed. Duck."` | `"The cracks are frosty. Who freezes glass? Rude."` |
| P2 | `"The first lens! Turn the mirrors (E / A) and send the sunbeam into the lens. Think like light. Lazy and straight."` | `"Try the mirror by the pillar. No, the other pillar."` |
| P3 | `"A glowfrog grotto, down here? Oh, the frogs have been singing to her. For four hundred years. Bless them."` | `"Ting? That mirror doesn't show me. I always show up in mirrors. I'm very bright. Walk through it."` |
| P4 | `"The splitter breaks white light into three. Violet, blue and red. Match each colour to its lens."` | `"That big crystal fellow is not happy to see us."` |
| P5 | `"The murals. I've only seen sketches. Look at them for me? Slowly. I'm taking notes."` | (on the murals, section 6.4) |
| P6 | `"The Hall of Reflections. Trust the floor, not the walls. Mirrors lie. Floors are honest."` | `"That one's wearing your face. Badly. Your nose is better."` |
| P7 | `"All three lenses aligned! The bridge should hold now. Should. Walk lightly. Lighter than that."` | `"She's close. That humming. It's the song she hummed under me in the nursery."` |
| P8 | `"I'm right here. Well, I'm up here. But I'm right here. Put her back to sleep."` | (boss intro) |

### 6.4 The P5 murals (look points `mural_1..3`, `{ id: "mural", name: "A mural" }`)

| Mural | Text | Lumi (befriend) |
|---|---|---|
| 1 | `"A young queen laughing in a nursery under one bright wisp. It sits on her shoulder like a pet."` | `"...That's me. I was smaller. She was too. I thought she hung the moon."` |
| 2 | `"The queen alone in a dark room, eyes wide, holding a wisp to her lips. The wisp is going grey."` | `"That's me too. Going grey. She was so scared of the dark. She never meant to be hungry."` |
| 3 | `"Elves carry great prisms down a stair. The queen sleeps in a crystal, smiling, in a rain of light."` | `"They put her to bed with all the lights on. That's kind. I think that's kind."` |

Conquer path: the murals still show, with no Lumi lines. Seer extra on mural 3: `"(The crystal in the mural has no cracks. The cracks you passed are new, and rimed.)"`

### 6.5 Veyra's reflection (P6, Hall of Reflections)

Halfway through P6, one mirror shows a woman in grey-blue standing behind you. When you turn, she's only in the glass. Speaker:
`"Veyra"` if `met_veyra`, else `"A frost-witch in grey-blue"`.

**Before the midpoint reveal** (`!flags.veyra_revealed`):
```js
pages: [
  "The prisms are cracking all across the Nine. I can't hold them all. I'm so glad someone came.",
  "Mind the queen. Hunger never sleeps as deep as it pretends.",
  "(The mirror frosts over, white edge to white edge, and cracks. She's gone.)",
],
```
- Seer extra page: `"(Your runes flinch. The frost on this glass is the frost on the stencil. The same cold hand.)"`

**After the reveal** (`flags.veyra_revealed`):
```js
pages: [
  "I only cracked the lid. Hunger did the rest. Put her back, if you think you're clever enough.",
  "Or don't. A dark Alfheim suits me very well.",
  "(The mirror frosts over and cracks. Her laugh hangs in the cold air a moment longer.)",
],
```
Sets `flags.alf_veyra = 1`.

### 6.6 Lady Sylvaine: intro

Speaker `{ id: "sylvaine", name: "Lady Sylvaine" }`.

**Befriend:**
```js
pages: [
  "(Inside the cracked Heart Prism, a tall figure opens violet eyes. Frost-cracks race across the crystal.)",
  "Light. Warm light, walking in my house. I have been so hungry. And so very cold.",
  "Little Lumi? My nursery light? You came back to me. You were always my favourite light.",
  "Lumi: \"You drank from me first, my lady. I hid in a frog pond till the frogs sang me bright.\"",
  "Then come closer, and I'll finish. The dark is coming back. I can't be in the dark again. I can't.",
],
```

**Conquer:**
```js
pages: [
  "(You pry at the Heart Prism. It cracks wide open. A tall figure unfolds from the light, violet eyes awake.)",
  "A thief in my vault, prying at my heart. Do you know what you've let out, little warm thing?",
  "No matter. You're full of light. I'll start with you.",
],
```

### 6.7 Lady Sylvaine: outro

**Befriend** (after the kill, E / A at the Heart sets `pv_sealed`):
```js
pages: [
  "(Sylvaine sinks to her knees. Her violet light gutters like a candle in a draught.)",
  "It's so dark... Lumi? Lumi, are you there? I'm frightened.",
  "Lumi: \"I'm here, my lady. I'll glow till you sleep. Like I used to, over your cradle.\"",
  "(Lumi drifts into the Heart Prism. Gentle light fills it, endless and warm. The cracks close.)",
  "Enough light... at last. Thank you, warm thing. Tell my granddaughter the throne is hers. It always was.",
  "(Sylvaine sleeps, sealed in the Heart Prism, smiling. Lumi slips out, a little dimmer, and settles by your shoulder.)",
  "Lumi: \"She's asleep. Resealed, and fed. I left some light with her. I've got plenty. Ting.\"",
],
then: (G) => { const f = flags(G.S); f.pv_sealed = 1; f.sylvaine_sleeps = 1; G.setQuest("prismvault", 2); },   // sylvaine_sleeps: the NG+ hook (9.8)
```

**Conquer** (after the kill, E / A at the Heart sets `pv_taken`):
```js
pages: [
  "(Sylvaine falls. The Heart Prism splinters, and its core drops into your hand, still warm.)",
  "You've taken the last light in my house. So I'll take the dark with me.",
  "Every lamp in Lumenvale will remember this. Every frog. Every wisp.",
  "(Far above, through the shaft in the roof, the city's lights begin to go out, one by one.)",
],
then: (G) => { flags(G.S).pv_taken = 1; G.give("prism_heart", 1); G.setQuest("prismvault", 2); },
```

### 6.8 Conquer path: leaving Alfheim (stage 2 → 3)

On entering the Gatelight arch with `pv_taken`: `(Lumenvale is dark behind you. Only the frogs still glow, and they've stopped singing.)`
Then `G.setQuest("prismvault", 3)` and the conquer rewards (section 9). After this, the Alfheim areas load in **dark mode** (section 9.6).

### 6.9 Regent Aerin: the Vault turn-in (befriend, stage 2 → 3)

```js
pages: [
  "She's asleep? Truly? And the wisps... listen. Listen to them. They're singing again.",
  "She said the throne is mine? ...Then perhaps, one day. Not today. Today I am going to cry in a corridor.",
  "Alfheim stands with you, hearth-walker. Our gate, our light, our rangers. Even Thorne, if you ask nicely.",
  "Mirelle has something to teach you. And Nim says there will be a festival. There is always a festival.",
],
then: (G) => { G.setQuest("prismvault", 3); G.factions.add("embassy", MERIT.vault, "vault"); gold(G, 150);
               flags(G.S).alf_resolved = "befriend"; G.toast("Alfheim is your ally. Wisp Night is coming.", 3.0); },
```

### 6.10 Veyra between realms (the next area load after `alf_resolved`)

| Path | Before the reveal | After the reveal |
|---|---|---|
| befriend | `"You sang a hungry queen to sleep instead of killing her. That's rarer than you know."` · `"Alfheim's light is back. I'll... remember that."` | `"You keep mending what I break. It's becoming tiresome."` · `"Enjoy the festival. Lanterns burn out."` |
| conquer | `"A whole city of lights, and you turned it off. You're doing my work for me, you know."` · `"Keep the Heart. It'll keep you warm. No one else."` | `"Another realm in the dark. Thank you. Truly."` · `"You'd make a fine Rift-Breaker. Think on it."` |

She leaves before you can answer. Seer extra (befriend, before the reveal): `"(Your runes prickle again: the same cold as the stencil.)"`

**Midpoint reveal timing (lead, 2026-10-06):** the reveal fires **after** this beat, never in place of it. If resolving Alfheim makes the
reveal due (e.g. Alfheim is your 3rd resolved realm), this beat plays its "before" lines and then queues the reveal for the next area load:
```js
// on the area load that plays 6.10
const f = flags(G.S);
playVeyraBeat(G, "alfheim", f.veyra_revealed ? "after" : "before");
f.alf_veyra_seen = 1;
if (!f.veyra_revealed && revealDue(G.S)) f.reveal_queued = 1;      // revealDue: the existing 3-resolved-realms / evidence check
// on the NEXT area load: if (f.reveal_queued && f.alf_veyra_seen) { f.reveal_queued = 0; playMidpointReveal(G); }  // sets veyra_revealed
```

### 6.11 The Dancing Blade (stage 2 scene, at night by the Empty Throne)

```js
pages: [
  "Mirelle: \"Hold the prism glass up to the sword. Steady. She hung it here the night she was sealed.\"",
  "(The Long Light lifts off its hooks by itself. It turns once in the air, violet and bright, and settles in your hand.)",
  "Mirelle: \"It's dancing. It hasn't danced in four hundred years. Swords are terrible judges of character, but still.\"",
  "Aerin: \"Carry it well. It was hers. Now it's yours. That's how it should go.\"",
],
then: (G) => { G.setQuest("alf_edge", 3); giveGear(G, PRISM_EDGE(G.S)); G.toast("Legendary: the Prism Edge", 3.0); },
```

---

## 7. The Prism Vault, room by room

**Theme:** energy and light. A vertical dungeon down the inside of the Prism Spire's root: glass stairs, black stone, great prisms
cracked with **white frost**, and violet light leaking from every crack. It's mostly dark, lit by beams you route, prism glints
and glowfrog pools. Pools: `prismshard`, `crystalgolem`, elite `mirrorduelist`, plus `willwisp` in P1 and P3. Conquer adds 2
`lightranger` in P1 and P5 (the rangers' last guard).

Rares (2–3×): the **Shardmother** (2.4×) roams P3, and the **Glass Stalker** (2.6×) roams P7. Mini-boss: the **Lens Warden** (2.8×) in P4.
Checkpoint braziers (E4.1): P0 and P5.

| # | Room | Beat | Mechanic / puzzle | Foes | Secrets / glow |
|---|---|---|---|---|---|
| P0 | **Spire Stair** | a glass spiral down into the dark; violet light pulses up from below like a slow heartbeat | **checkpoint brazier 1** | — | befriend: Mirelle's lens crackles on |
| P1 | **Hall of Shards** | a long hall of broken prisms; loose shards hang in the air | first fight. Frost-cracked prisms leak light: standing in a leak gives **Glare** (−10% damage for 2 s) | 3 `prismshard`, 1 `willwisp` (+2 `lightranger`, conquer) | cracks rimed with white frost (look point: `"Frost on glass, deep inside the Vault. Nobody up there could have done this."`) |
| P2 | **The Mirror Gallery** (Lens 1) | the first great lens, dark, on a dais | **beam puzzle 1:** light the dark source crystal with a spell (Hollows brazier rule), then turn 3 mirrors to send the white beam into the lens. A `crystalgolem` patrols; the beam through it staggers it (teaching) | 1 `crystalgolem`, 2 `prismshard` | `pv_lens1`: the lens flares and a sealed door slides open |
| P3 | **Glowfrog Grotto** (side room) | a cave pool full of glowfrogs, who've sung to the sleeping queen for four hundred years | **illusory mirror-wall:** one mirror doesn't show your reflection. Walk through it | 2 `willwisp`; Shardmother rare spot | **hidden spring** behind the mirror (`pv_spring`, +40 Gilded Acorns, spring-fizz); frogs in blue, violet, red |
| P4 | **The Splitter Hall** (Lens 2) | a round hall; a great prism splitter in the centre | **beam puzzle 2:** the splitter breaks white into **violet, blue and red**. Turn 4 mirrors to send each colour to its matching receiver. The **Lens Warden** guards; its chest-lens shield drops only when a beam hits it | **Lens Warden** (2.8×) + 2 `prismshard` | `pv_lens2`; the three colours paint the floor |
| P5 | **Reliquary Walk** | a quiet gallery of murals: Sylvaine's story | **checkpoint brazier 2**; 3 mural look points (section 6.4) | 2 `mirrorduelist` ambush on leaving (+2 `lightranger`, conquer) | a reliquary chest: 60 gold + 1 `prism_glass` |
| P6 | **Hall of Reflections** (Lens 3) | a mirror maze; your reflections walk a beat behind you | **beam puzzle 3:** route the beam through the maze to the third lens. Two of the mirrors **turn on their own** every 6 s (time the beam). Midway, **your reflection** steps out of the glass: a `mirrorduelist` with your silhouette. Veyra's reflection beat (section 6.5) | 3 `mirrorduelist` (one is "you") | `pv_lens3`; Seer sees the beam path ghosted (a hint) |
| P7 | **The Cracked Stair** | with all 3 lenses aligned, a **bridge of light** forms down over a black chasm. Frost-cracks everywhere, and the light is pulled downward | the light bridge flickers off for 1 s every 8 s: cross in time (the flicker has a 1 s violet tell) | 2 `prismshard`, 1 `crystalgolem` (+2 `mirrorduelist`, conquer); Glass Stalker rare spot | `"(Something below is humming. The light bends toward it like grass in wind.)"` |
| P8 | **The Heart Prism** (boss) | a round chamber about 16 m across; the cracked Heart Prism in the centre with Sylvaine asleep inside. A shaft in the roof shows the aurora far above | the boss (section 8.1): 4 mirror pylons and 4 rim braziers matter | Lady Sylvaine (6×) + summoned `prismshard` | after the fight, the frogs from P3 sing up the stair (befriend) |

### 7.1 Beam puzzle spec (for Systems)

New area data `scene.game.beams`, one block per puzzle room:

```js
beams: {
  grid: 0.5,                                                  // beams travel on a 0.5 m grid, in 8 directions (0 = +x, 2 = +z, 45° steps)
  sources:   [{ id: "p2_src", pos: [-6.0, 2.0], dir: 0, col: "white", dark: true }],   // dark: light it with a spell within 2.6 m
  mirrors:   [{ id: "p2_m1", pos: [-2.0, 2.0], rot: 1 }, { id: "p2_m2", pos: [-2.0, -3.0], rot: 3, fixed: false },
              { id: "p6_m4", pos: [1.5, 0.5], rot: 0, spin: 6 }],                     // spin: turns by itself every N s
  splitters: [{ id: "p4_split", pos: [0, 0] }],               // white in -> blue straight on, violet 90° left, red 90° right
  receivers: [{ id: "pv_lens1", pos: [4.0, -3.0], col: "white", opens: "p2_door" }],
}
```

- **Mirrors** have 4 orientations (`rot` 0–3 = a line at 0°, 45°, 90° or 135°). E / A rotates one step. Reflection:
  `out = (2 * rot - dir + 8) % 8` (in 45° units).
- The beam stops at walls (nav blockers), at receivers and at the edge of the room. It is drawn as a 2 px pixel line in its colour, with
  a small point light every 2 m (no bloom).
- **Beam hits:** a `crystalgolem` is staggered for 2 s and loses its prism shield. A `mirrorduelist` is revealed when invisible. In P8,
  Sylvaine's light shield breaks. The player takes no damage from the beam (cozy), but it blocks prism shards' shots.
- **A receiver lit by the right colour** sets `S.found[id]` and fires `opens` (a door, a bridge). It stays lit forever.
- Hints: the Seer sees the solved path as a faint dotted ghost. Lumi (befriend, floating with you) gives one spoken hint per room after 60 s.
- QA: `?beams=solve` lights every receiver in the room.

---

## 8. Bosses, enemies and rares

### 8.1 Lady Sylvaine, the Light-Drinker (Prism Vault, P8)

- **Look: 6× the player's height.** An elf queen, tall and terribly elegant. Long silver-white hair floats around her as if
  under water. She wears a crown of **violet prism spikes**, a fitted violet **bodice-top** stitched with silver, and a long layered
  **dark-violet skirt** with a sash of glass beads at a clearly visible waist. A high-collared cape of glass shards glitters behind
  her. Her skin is pale and her eyes are **neon violet**, with veins of violet light running down her arms to glowing fingertips.
  Small fangs show only when she drains. **Neon violet** is her only glow, except the white frost in the cracks.
- **Arena:** round, 16 m. The **Heart Prism** stands in the centre (cracked, about 3 m tall). A **sunbeam source** falls through the roof
  shaft at the north rim. There are **4 mirror pylons** (rotatable, as in 7.1) and **4 rim braziers** (start lit, dimmed in phase 3).

| Phase | HP | Moves | Tell |
|---|---|---|---|
| 1 **The Long Light** | 100–65% | **light lances** (a fan of 3 violet beams); **drain tether** (a violet beam to you or your summon: it drains 8 HP/s and heals her, broken by a dodge roll through it or a pylon between you); a **glide** dash across the arena; summons 2 `prismshard` every 20 s | lances: her raised hand flashes 0.8 s before; tether: a violet halo opens round her palm; glide: her skirt flares and she rises 1 m |
| 2 **The Hall of Mirrors** | 65–30% | a **light shield** (absorbs 80%). She splits into **3 reflections**, and only the real one casts a **shadow** on the floor. Hitting a fake shatters it into 2 `prismshard`. **Turn the mirror pylons** to bounce the roof sunbeam into her: the shield breaks and she staggers for 4 s | the real one's shadow; Seer sees her outlined; the sunbeam path glows faintly when a pylon is close to aligned |
| 3 **Hunger** | < 30% | she **drinks the arena's light**: every 10 s one rim brazier goes dark and the room darkens. In the dark she **lunges** for heavy damage. In a light zone (a relit brazier, your pet's light, Lumi's light zone) she can't lunge and her drain is halved. **Relight braziers with spells** to fight her back | two violet eyes open in the dark 1 s before a lunge; a brazier flickers twice before she drinks it |

At 0 HP the fight ends in the outro (6.7). On the befriend path she isn't killed: she yields and is **resealed, asleep**, in the Heart Prism. The engine treats
it as a boss kill either way (`onBoss`, guaranteed Legendary).

```js
sylvaine: { name: "Lady Sylvaine, the Light-Drinker", scale: 6, hp: 1700, dmg: 24, speed: 1.4, reach: 7.0, keep: 4.5, windup: 0.8, cd: 2.0,
            aggro: 12, r: 1.4, push: 0.2, ranged: true, float: true, boss: true, minion: "prismshard", phases: [0.65, 0.3],
            drain: { dps: 8, heal: 2, range: 8 }, shield: 0.8, clones: 2, dark: { every: 10, lunge: 34 }, beamWeak: true,
            glow: "#a45cf0", legendary: true, noRespawn: true },
```

### 8.2 Mini-boss, duel and gate foes

| Foe | Scale | Look | Behaviour |
|---|---|---|---|
| **The Lens Warden** (`lenswarden`, P4) | 2.8× | a crystal golem of violet glass and black stone, a great round lens in its chest, frost-cracks across one shoulder | heavy slams; a **prism shield** soaks everything until a beam hits its chest-lens; every 3rd slam is a shockwave (`wave`) |
| **Captain Faelan** (`faelan`, conquer) | 1.3× (elite, not a boss) | as section 5 | fast bow volleys, a backstep, a 3-arrow spread; yields at 25% (no kill) |
| **Frost sentinel** (`frostsentinel`, Bifrost) | 2× | an ice golem knight-shape of Veyra's frost, blue cold-fire in its seams | the `icegolem` kit (a chill slam) with a 3-hit frost combo; it appears once |

```js
lenswarden:    { name: "The Lens Warden", scale: 2.8, hp: 520, dmg: 22, speed: 0.95, reach: 3.0, windup: 0.75, cd: 2.0, aggro: 8, r: 0.85,
                 push: 0.15, heavy: true, slam: true, boss: true, wave: { every: 3, r: 4.4, dmg: 16 }, prismShield: 0.9, beamWeak: true,
                 glow: "#a45cf0", legendary: true, noRespawn: true },
faelan:        { name: "Captain Faelan Thorne", scale: 1.3, hp: 260, dmg: 12, speed: 2.2, reach: 7.0, keep: 4.0, windup: 0.45, cd: 1.4, aggro: 10,
                 r: 0.32, push: 0.5, ranged: true, bolt: "arrow", spread: 3, elite: true, yieldAt: 0.25, noRespawn: true },
frostsentinel: { name: "Frost sentinel", scale: 2.0, hp: 300, dmg: 16, speed: 1.0, reach: 2.0, windup: 0.6, cd: 1.8, aggro: 9, r: 0.6, push: 0.2,
                 heavy: true, slam: true, chill: 20, combo: 3, glow: "#5ab4f0", noRespawn: true },
```

### 8.3 Rares (2–3× the player's height)

| Rare (`BASES` key) | Scale | Look | Behaviour | Where |
|---|---|---|---|---|
| **Shardmother** (`shardmother`) | 2.4× | a crystal queen-shape of floating shards around a violet core, a skirt of hanging glass | ranged shard volleys; a Summoner of `prismshard` | Wispwood roams; Vault P3 |
| **Glass Stalker** (`glassstalker`) | 2.6× | a tall, thin mirror-creature, a moving silhouette of reflections with violet eyes | blinks to your side (it pairs well with the **Blinking** trait); goes invisible in prism rain | Wispwood roams; Vault P7 |

```js
shardmother:  { name: "Shardmother", scale: 2.4, hp: 290, dmg: 12, speed: 1.2, reach: 6.5, keep: 3.8, windup: 0.55, cd: 2.0, aggro: 8, r: 0.66,
                push: 0.4, ranged: true, float: true, bolt: "prism_bolt", minion: "prismshard", xp: 180 },
glassstalker: { name: "Glass Stalker", scale: 2.6, hp: 300, dmg: 18, speed: 1.6, reach: 2.4, windup: 0.5, cd: 1.6, aggro: 8.5, r: 0.6, push: 0.3,
                blink: 4, invisRain: true, xp: 190 },
```
`RARE_AREAS.wispwood = { bases: ["shardmother", "glassstalker"], spots: [[5.4, -3.6], [-6.0, 0.4]] }`. In the Vault, rares spawn at fixed spots
(P3, P7) on the same daily roll (`ROAM_CHANCE`). The Gloam (violet) element suits Alfheim, so give it a higher weight here.

### 8.4 New regular enemies (`ENEMIES` suggestions)

```js
prismshard:    { name: "Prism shard", hp: 40, dmg: 9, speed: 1.4, reach: 6.0, keep: 3.4, windup: 0.6, cd: 2.4, aggro: 6.5, r: 0.24, push: 0.6,
                 ranged: true, float: true, bolt: "prism_bolt" },                     // a spinning violet crystal the size of a cat
willwisp:      { name: "Will-o'-wisp", hp: 30, dmg: 7, speed: 2.2, reach: 5.0, keep: 3.0, windup: 0.5, cd: 2.2, aggro: 7, r: 0.22, push: 0.7,
                 ranged: true, float: true, blink: 6, lure: true },                  // a hostile neon wisp; drifts away to lure you into others
crystalgolem:  { name: "Crystal golem", hp: 150, dmg: 17, speed: 0.95, reach: 1.7, windup: 0.7, cd: 2.0, aggro: 5.5, r: 0.38, push: 0.2,
                 heavy: true, slam: true, prismShield: 0.6, beamWeak: true },        // a violet glass golem; beams strip its shield
mirrorduelist: { name: "Mirror Duelist", hp: 95, dmg: 13, speed: 2.1, reach: 1.4, windup: 0.4, cd: 1.3, aggro: 7, r: 0.3, push: 0.5,
                 elite: true, mimic: true, invisRain: true },                        // an elf-shaped silhouette of mirror glass with a rapier; copies your last attack
mirroryou:     { base: "mirrorduelist", name: "Your Reflection", sprite: "hero", palette: "mirror", hp: 110 },  // P6 only: the hero sheet, palette-swapped
lightranger:   { name: "Light-elf ranger", hp: 70, dmg: 10, speed: 1.9, reach: 7.0, keep: 4.0, windup: 0.5, cd: 1.8, aggro: 8, r: 0.28, push: 0.5,
                 ranged: true, bolt: "arrow" },                                       // conquer only: leather vest, shirt, trousers, longbow
```

**P6 "your reflection" (lead-approved palette swap):** `mirroryou` draws the **current hero's own sheet** with a mirror palette (skin and
cloth mapped to silver-white `#e8ecf4` / pale violet `#c890ff` / ink-blue shadow `#2a2a4a`, eyes neon violet), at 70% opacity with a slow
vertical shimmer. It uses the Mirror Duelist kit. If the hero has no palette ramp to swap, fall back to the generic `mirrorduelist`.

XP for `progress.js XP`: `mirroryou: 72, prismshard: 32, willwisp: 26, crystalgolem: 58, mirrorduelist: 72, lightranger: 40, frostsentinel: 180,
faelan: 200, lenswarden: 320, sylvaine: 800`.

---
## 9. Rewards

### 9.0 Reward table (existing scales: errand 40, boss 80, abyssal rift 120, Embassy ranks 150 / 400 / 800)

| Source | Befriend | Conquer |
|---|---|---|
| *The Frozen Gate* (both) | **+60 Rift Marks**, 50 g | same |
| *A Name in Frost* | **+60 Realm Favor**, 40 g (+20 with Mossbrook's apology) | — |
| *The Dimming* | **+80 Realm Favor**, 60 g, **Lumi** joins | — |
| *The Prism Claim* | — | **+60 Rift Marks**, 80 g |
| Lens Warden kill (`onBoss`) | +80 Realm Favor, guaranteed Legendary | +80 Rift Marks, guaranteed Legendary |
| Sylvaine (`onBoss`) | +80 Realm Favor, guaranteed Legendary | +80 Rift Marks, guaranteed Legendary |
| *The Prism Vault* done | **+120 Realm Favor**, 150 g, Wisp Night unlocked, the **Queen's Lantern** (decor), Sylvaine resealed (NG+ hook) | **+120 Rift Marks** (`MERIT.vault_c`), 200 g, **Prism Heart**, **Sylvaine's Crown** (cosmetic trophy) |
| Prism light school | Mirelle teaches it (9.2) | — |
| *The Dancing Blade* | the **Prism Edge** (9.1) | — |
| *Wisp Night* (each festival) | +40 Realm Favor, 30 g, catalog wisps | — |
| Svartalfheim | **locked** as an ally (rival pair) | Anvildeep's mood +1 |

A full befriend run gives about **460 Realm Favor** plus rifts and rares. With Vanaheim's ~380, that's Embassy **Ambassador (800)** in reach,
which is the gate for *The Dancing Blade*.

### 9.1 The Prism Edge (legendary weapon)

*"A violet blade that dances on its own."* It's built from `makeItem` at your level, so it never goes stale, then fixed up:

```js
export function PRISM_EDGE(S) {
  const it = makeItem(Math.max(10, S.lv || 1), 4, "weapon");
  const k = RARITY[4].mul * (1 + (it.lv - 1) * 0.06);
  it.name = "Prism Edge"; it.fixed = true; it.unique = "prism_dance";
  it.mods = { meleeMul: +(0.045 * k).toFixed(3), spellMul: +(0.04 * k).toFixed(3), crit: +(0.01 * k).toFixed(3) };
  it.gems = [null, null];
  it.about = "Sylvaine's sword, the Long Light. Every 4th hit, a ghost of the blade dances out and strikes again for 50%.";
  return it;
}
```

- **Unique (`prism_dance`):** combat counts melee hits, and every 4th one spawns a violet afterimage blade that slashes the same foe for
  50% of the hit (its own little arc, `fx: "prism_dance"`). In prism rain, the ghost slashes twice.
- **Look:** a slim violet glass blade with a neon edge and a silver guard. While equipped, a tiny ghost blade orbits the hero slowly
  (a 6-frame loop, the "dances on its own" read). The Legendary aura still applies.
- It can be upgraded to +10 and rerolled like any Legendary (`forge_alchemy.md`). Rerolls never touch the unique.

### 9.2 The Prism light school (learned from Mirelle, befriend)

| Tier | Needs | Spell | Shape |
|---|---|---|---|
| I | Vault done + Embassy **Friend** | **Prism Beam** | `prism_beam: { name: "Prism Beam", cd: 2.4, dmg: 24, range: 7.0, kind: "beam", bounce: 1, school: "prism", fx: "prism_beam" }` (+1 bounce in prism rain; it also counts as a beam for crystal foes and puzzles) |
| II | Embassy **Trusted** | **Mirror Double** | `mirror_double: { name: "Mirror Double", cd: 12, kind: "decoy", life: 5, hp: 60, school: "prism" }` (foes target the double; it shatters into 3 prism shards that hurt nearby foes for 10) |
| III (**parked**) | Embassy **Honored** | **Prism wisp** (summon) | `SUMMONS.prismwisp = { name: "Prism wisp", hp: 30, dmg: 8, reach: 3.4, speed: 3.0, ranged: true, split: 1 }` (its bolt splits in two on hitting) |

Learning uses `G.learn(id)`. **Tier III is parked** (lead, 2026-10-06): it needs an "alternate summon" slot (`S.altSummon`), which isn't
built. Ship tiers I–II; the spec stays here for later.

Mirelle teaching (first talk once tier I is met):
```js
pages: [
  "You put our queen to sleep with light. Now let me teach you to throw some. Hold out your hand.",
  "(Mirelle sets a sliver of prism glass on your palm. It melts into light and runs up your arm.)",
  "Prism Beam. Point, and let it bend. Light always finds the next thing to hit. It's very rude that way.",
],
then: (G) => { G.learn("prism_beam"); G.toast("Learned: Prism Beam (Prism light school)", 2.6); },
```
Tier II: `"Mirror Double. Make a copy of yourself and let them hit that. It's how I get out of meetings."`
Tier III (parked): `"A prism wisp of your own. Be nice to it. Wisps remember everything, and they gossip."`

### 9.3 Lumi (companion, befriend)

`flags.companions.lumi = 1` at *The Dimming*'s end. She's a glowing, talking wisp about 2× the wisp kit pet, and clearly not the pet. Look,
sprite notes, `COMPANIONS.lumi`, kit and barks are in section 5.5. If you conquer Alfheim, Lumi never joins. One big grey wisp flees from you
in the Wispwood: `(A big grey wisp with two dim eyes sees you, and darts away into the dark.)`

### 9.4 The Prismdancer hook: the wisp catalog

The secret hero **Prismdancer** (light-elf blade dancer) unlocks when **all 9 rare wisps** are caught (`S.wisps`, 9 keys). Rare wisps
can be caught with Nim's `wisp_net` (E / A within 1.2 m) whenever their condition is met. They blink away once first.

| Key | Wisp | Glow | Where and when |
|---|---|---|---|
| `wisp_ember` | Ember-wisp | red | Wispwood, at night, by the red glowfrog pond |
| `wisp_frost` | Frost-wisp | cold blue | the frost scar, at night, after *A Name in Frost* |
| `wisp_gloam` | Gloam-wisp | violet | the Lantern Walk under an aurora |
| `wisp_gold` | Gold-wisp | pale gold | Ferrin's pool at dawn (`t` 0.22–0.3) |
| `wisp_moon` | Moon-wisp | white | the Court's moon-pool at night |
| `wisp_frog` | Frog-wisp | green, riding a glowfrog | any glowfrog pond in prism rain |
| `wisp_prism` | Rainbow-wisp | cycles violet, blue, rose | Wisp Night only |
| `wisp_storm` | Storm-wisp | violet-red crackle | Bifrost Crossing during a rift storm (`F.storm === "bifrost"`) |
| `wisp_hearth` | Hearth-wisp | warm amber | Bakery Lane at night outside the Kettle & Key, once Lumi is with you ("It followed us home!") |

- First catch of each: toast `Wisp catalog: ${name} (${n}/9)`, plus Nim's line on your next visit.
- All 9: `S.unlocks.prismdancer = 1`, toast `Secret hero unlocked: the Prismdancer`. On the next Wisp Night a teaser NPC appears on the
  Lantern Walk: **Vessa Dawnstep**, the last Prismdancer (look: a fitted violet dancer's top, loose silver trousers gathered at the
  ankle, a sash with two short glass blades, bare arms with prism-light tattoos):
  - `"Nine wisps in one net. Nobody's done that in five hundred years. Not even me, and I've tried. Twice."`
  - `"The old dance isn't dead, then. When you're ready to learn it, you'll find me. Or I'll find you."`

### 9.5 Svartalfheim, the rival realm

- **Befriend:** at the choice itself (section 5.2, lead-approved), `lockRival(S, "svartalfheim")` sets `S.flags.rivals = { ...rivals, svartalfheim: "locked" }`. Svartalfheim can no longer be
  befriended; neutral and conquer stay open. `GATES.svartalfheim`'s look gets one extra line while locked:
  `"A dwarven notice is nailed over the copper seal: 'No elf-friends.' Someone has underlined it twice."`
  Brokk leaves the Wisp Market, and Orri reacts (section 5.9).
- **Conquer:** also at the choice, `moodUp(S, "svartalfheim")` sets `S.flags.realm_mood = { svartalfheim: 1 }`. Svartalfheim's arc (a later doc) starts
  friendlier, e.g. its first Embassy step is skipped and Orri gives a dwarven welcome line: `"Anvildeep's heard of you. Good things. Loud things."`
- **Reverse lock** (`svartalfheim.md`): befriending Svartalfheim sets `rivals.alfheim = "locked"` (Aerin's befriend greys out);
  conquering it sets `realm_mood.alfheim = 1` (warmer opener, Faelan's line, +20 Realm Favor on *A Name in Frost*).
- The **4-ally cap** (one per rival pair, plus Vanaheim) counts `alliance` values of `"befriend"`. Alfheim fills the Alfheim/Svartalfheim slot.

### 9.6 Conquer path: dark Lumenvale (`flags.alf_dark = 1`)

After *The Prism Vault* on the conquer path, Lumenvale gets a **re-grade, not a blackout** (lead, 2026-10-06). It's gloomy, but it
glows: **cold violet, red and neon blue**. It's **never flat dark**, and the player must always read the ground.

**Art spec (the `alf_dark` grade):**
- **Ambient:** deep indigo (`#1a1430`) instead of blue-black, day and night. The lavender day becomes a cold violet dusk (day level
  ×0.45, or tint `#7a68b8` in the overlay fallback). No warm gold anywhere except Saelis's one stall lamp.
- **Cold violet:** the silverbark sap-veins and hanging vines stay lit but shift to a colder, dimmer violet (`#6a4ab8`) and pulse
  slowly, like breathing. Brushing a vine still flares it, now in cold violet.
- **Red:** about 1 vine in 6 carries a slow **red ember pulse** (`#ff4a3a`, every 4 s) up the strand. Glowfrogs all glow **red**
  (alarmed) and don't sing. The red toadstools glow a little brighter. Red is the "something's wrong" colour.
- **Neon blue:** the rangers hang **cold-fire watch-lamps** (`#5ab4f0`, small point lights) where glow orbs used to be: on bridges,
  stairs and doorways. They keep paths readable. Bioluminescent pools stay neon blue, but their ripples are slower.
- **Glow orbs:** about a third remain, dim and violet, and they drift away from you instead of gathering.
- **Aurora:** a thin, slow **red-violet** band instead of the full curtains. No prism rain (a cold drizzle instead).
- **Wisps:** none fly. Grey husks sit in the nests.
- **Readability floor:** at least one light source (watch-lamp, pool, lit vine or orb) within ~4 m of any walkable tile, and every
  door, stair, NPC and pickup keeps its own small light. Test it at night on a dim monitor.
- **Implementation:** swap each area's light colours via a per-area palette (`LIGHTS.alf_dark`) plus a light-group toggle for the orbs
  that go out, and the grade/tint above. A plain "lights off" toggle alone is not enough.

Also:
- Saelis's prices are ×1.5 and her gear is Common only. No Wisp Night. NPCs use their conquer lines.
- The Wispwood's rifts open 25% more often (`EVERY` × 0.75). The dark draws them in.
- Hidden springs and waystones still work. The game never locks you out.

### 9.8 The NG+ hook: the sleeping queen (befriend)

On the befriend path Sylvaine is **resealed, asleep** in the Heart Prism (`flags.sylvaine_sleeps = 1`), fed by Lumi's light. She is
never killed on this path, and every befriend line says so (sections 3.5, 6.7, 6.9, 6.10, 8.1). This is the **NG+ hook**:
- `sylvaine_sleeps` carries into NG+ (with the other carried flags). In NG+, the Heart Prism in P8 shows faint frost-cracks again and
  hums when you enter; look text: `"(The Heart Prism hums. Under the light, someone turns over in her sleep.)"`
- Lumi bark in NG+ P8: `"Ting... she's dreaming. Bad dreams, I think. Not yet. But someday."`
- The content itself (a "Waking Queen" NG+ quest, or a Helheim beat) is a later doc. This doc only sets the flag and the two lines.

### 9.7 Materials, cosmetics, gems

- **Prism glass** (`prism_glass`): drops from `crystalgolem` 20%, `prismshard` 8%, the Lens Warden 2, the Shardmother 1. Sells for 12 g. It's used in *The Dancing Blade*.
- **Prism Heart** (`prism_heart`, conquer): a key trophy. Sable buys it for **400 g + 40 Black Doubloons** (lead-approved).
- **Sylvaine's Crown** (conquer, cosmetic) and the **Queen's Lantern** (befriend, house decor): trophy-wall and housing items for later.
- Gem drops: `gemOdds.crystalgolem = ["moon_opal", 0.1]`, `gemOdds.prismshard = ["rift_shard", 0.06]`.
- **Prism core** (`prism_core`), the **5th socket gem** (lead-approved). It goes in `loot.js` `GEMS` after `moon_opal`, so
  `GEM_IDS` picks it up automatically:
  `prism_core: { name: 'Prism core', col: '#6af0f0', lo: '#a45cf0', mods: { spellMul: 0.04, summonMul: 0.04, crit: 0.01 }, price: 130, about: '+4% spells · +4% summons · +1% crit' }`
  - **Stats:** a spell/summon hybrid. It's weaker than a rift shard for spells alone (6%) or a moon opal for summons alone (8%), but it helps both.
  - **Sources:** the Shardmother always drops 1 (first kill), then 25%. The Lens Warden 25%. 1 in the Heart Prism chamber after Sylvaine
    (both paths). `gemOdds.prismshard` stays rift shard. Saelis sells 1 per night for 130 g (befriend, after the Vault). Nettle doesn't stock it.
  - **Icon note:** neon cyan (`col`) with a violet corner (`lo`). In a socket the inlay reads cyan with a violet pixel bottom-right, so it's
    distinct from the rift shard's lilac and the frost core's pale blue. Optional: in `gemPaint`, give `prism_core` one rose-red
    (`#ff4a3a`) facet pixel so the loose gem shows all 3 prism colours.

---

## 10. `markerFor` additions

```js
const F = S.flags || {}, A = (F.alliance || {}).alfheim, q = S.quests, inv = S.inv || {}, G_ = (id) => (S.ranks || {})[id] || 0;
// Bifrost
if (id === "gatewright" && G_("gate") >= 3 && !q.alf_gate) return "quest_mark";
if (id === "gatewright" && q.alf_gate === 1 && F.ag_sentinel) return "quest_turnin";
if (id === "gatewright" && q.alf_gate === 2) return "quest_turnin";
// Vanaheim: Mossbrook's apology
if (id === "warden" && q.alf_gate === 3 && (F.alliance || {}).vanaheim === "befriend" && !F.moss_letter) return "quest_mark";
// Lumenvale
if (id === "regent" && q.alf_gate === 3 && !A) return "quest_mark";
if (id === "regent" && (q.alf_name === 2 || q.alf_dim === 2)) return "quest_turnin";
if (id === "regent" && q.prismvault === 2 && A === "befriend") return "quest_turnin";
if (id === "librarian" && q.alf_name === 1 && !F.an_lens) return "quest_mark";
if (id === "librarian" && q.alf_name === 1 && F.an_stencil) return "quest_turnin";
if (id === "librarian" && q.alf_dim === 1 && !F.dm_lumi && !(S.met || {}).mirelle_dim) return "quest_mark";
if (id === "librarian" && q.alf_dim === 1 && F.dm_trail) return "quest_turnin";
if (id === "librarian" && A === "befriend" && q.prismvault === 3 && !q.alf_edge && G_("embassy") >= 3) return "quest_mark";
if (id === "librarian" && q.alf_edge === 1 && (inv.prism_glass || 0) >= 3) return "quest_turnin";
if (id === "lumi" && q.alf_dim === 1 && !F.dm_lumi) return "quest_mark";
if (id === "wispcatcher" && wispNight(S) && !q.wispnight) return "quest_mark";
if (id === "wispcatcher" && q.wispnight === 1 && (S.wispHunt || {}).n >= 5 && (S.wispHunt || {}).rare) return "quest_turnin";
if (id === "wispcatcher" && q.wispnight === 2) return "quest_turnin";
```

`wispNight(S) = (S.flags.alliance || {}).alfheim === "befriend" && S.quests.alf_dim === 3 && S.day % 7 === 6 && NIGHT(t)`.

TALK ids: `regent`, `librarian`, `ranger`, `lumi`, `wispcatcher`, `poolkeeper`, `lanternseller`, `dwarftrader`, `elf1..3`, `vessa`;
narration ids `narr`, `clue` (frost scar), `mural`; boss speaker `sylvaine`.

---

## 11. Items (`ITEMS` additions)

```js
thawkey:      { name: "Keybearer's key", px: "thawkey", about: "Cut by the Guild for Alfheim's frozen seal. It hums near ice." },
frost_stencil:{ name: "Rune stencil", px: "frost_stencil", about: "Frost-iron, with Alfheim runes cut clean through. Never warm. Evidence." },
moss_letter:  { name: "Mossbrook's apology", px: "moss_letter", about: "In Burrowmoss's hand, four drafts deep. Tobble drew a mushroom on it." },
spirekey:     { name: "Spire key", px: "spirekey", about: "A key of violet glass. It opens the Prism Spire, and nothing else, ever." },
speaklens:    { name: "Speaking lens", px: "speaklens", about: "Mirelle's voice comes out of it. Sometimes she forgets it's on." },
wisp_net:     { name: "Wisp net", px: "wisp_net", about: "Nim's spare net. Catch wisps with E / A. Be gentle. Let them go after." },
prism_glass:  { name: "Prism glass", px: "prism_glass", about: "A shard of living prism. It splits light into three when you breathe on it." },
prism_heart:  { name: "Prism Heart", px: "prism_heart", about: "The core of Alfheim's Heart Prism. Warm. Every lamp in Lumenvale went dark for it." },
lantern_moth: { name: "Moon-moth lantern", px: "lantern_moth", about: "A Wisp Night lantern. It remembers the night you bought it." },
lantern_frog: { name: "Frog lantern", px: "lantern_frog", about: "A Wisp Night lantern shaped like a glowfrog. It croaks once at midnight." },
lantern_prism:{ name: "Prism lantern", px: "lantern_prism", about: "A Wisp Night lantern. It throws rainbows on the ceiling." },
queen_lantern:{ name: "The Queen's Lantern", px: "queen_lantern", about: "Aerin's gift. A violet lantern from Sylvaine's nursery. Lumi used to sit in it." },
sylvaine_crown:{ name: "Sylvaine's Crown", px: "sylvaine_crown", about: "Violet prism spikes, cold to the touch. A trophy. No one in Alfheim will look at it." },
```

Gear: `PRISM_EDGE(S)` (section 9.1). Gem: `prism_core` goes in `loot.js` `GEMS` (full entry, sources and icon note in section 9.7).

---

## 12. Save shape (summary)

| Key | Meaning |
|---|---|
| `S.flags.alliance.alfheim` | `"befriend"` / `"conquer"` |
| `S.flags.ag_struck`, `ag_sentinel`, `alf_gate_open` | *The Frozen Gate* |
| `S.flags.moss_letter` | Burrowmoss gave the apology |
| `S.flags.an_lens`, `an_stencil`, `alf_cleared` | *A Name in Frost* |
| `S.flags.dm_lumi`, `dm_trail`; `S.found.dw_1..5` | *The Dimming* |
| `S.flags.pc_faelan`; `S.found.pc_r1..3` | *The Prism Claim* (conquer) |
| `S.found.pv_lens1..3`, `pv_spring`, `alf_spring`, `ww_spring`, `mural_1..3` | Vault lenses, hidden springs, murals |
| `S.flags.pv_boss`, `pv_sealed` / `pv_taken`, `alf_veyra`, `alf_resolved` | the Vault and Veyra's reflection |
| `S.flags.alf_dark` | conquer: dark Lumenvale |
| `S.flags.companions.lumi` | Lumi (the talking wisp) joined |
| `S.flags.sylvaine_sleeps` | befriend: Sylvaine resealed, asleep (the NG+ hook) |
| `S.flags.rivals.svartalfheim` / `S.flags.realm_mood.svartalfheim` | the rival lock / Anvildeep's mood |
| `S.flags.brokk_left` | Brokk has left the Wisp Market |
| `S.evidence.alfheim` | `"frost_stencil"` |
| `S.wisps` | `{ wisp_ember: 1, ... }` the rare wisp catalog (9) |
| `S.wispHunt` | `{ n, rare }` this Wisp Night's catch |
| `S.unlocks.prismdancer` | the secret hero unlocked |
| `S.altSummon` | `"prismwisp"` once learned (needs the alternate-summon system) |
| `S.quests.alf_gate / alf_name / alf_dim / alf_take / prismvault / alf_edge / wispnight` | 0–3 |
| `MERIT.thaw / claim / alf_name / apology / alf_dim / vault / vault_c / wispnight` | 60 / 60 / 60 / 20 / 80 / 120 / 120 / 40 |
| `REALM.alfheim / lumen_court / wispwood / prismvault` | `"embassy"` (conquer: `realm()` returns `"gate"`) |
| `SKY.alfheim / lumen_court / wispwood` | `"prism"` |

New helpers: `lockRival(S, realm)`, `moodUp(S, realm)`, `wispNight(S)`, `PRISM_EDGE(S)`, `giveGear(G, it)` (push to `S.bag`, or to the bank
if the bag is full, then `drawBag`), and the beam puzzle runtime (`beams.js`, suggested).

---

## 13. Later: Rift-Breaker variant (stub, low priority)

Not for this build. If the player has joined Veyra (`flags.rift_breaker`) before Alfheim, the arc flips to sabotage. Rough beats only:
- *The Frozen Gate* opens with Veyra's blessing, not Halvard's cutting: `"I'll thaw it for you. Just this once. Bring me something."`
- No befriend/conquer choice. Aerin treats you as a Midgard envoy, and you work against her from inside.
- Instead of clearing Alfheim, you **plant the frost stencil** on an Alfheim ranger (`S.evidence.alfheim = "planted"`).
- In P8 you **crack the last prism** and let Sylvaine wake, then leave her to Lumenvale. It's the conquer grade (9.6) with no Prism Heart.
  Lumi never joins. Faelan becomes a hunter who shows up later.
- Rewards would be in Veyra's currency, set by the Rift-Breaker doc. That later doc owns all the lines. Nothing here gates on it.

---

## 14. Decisions (all resolved by the lead, 2026-10-06)

1. **Sylvaine's fate (befriend): resealed, asleep.** She's never killed on befriend. All befriend lines are consistent (3.5, 6.7, 6.9, 6.10,
   8.1, 9.0). `flags.sylvaine_sleeps = 1` is the **NG+ hook** (9.8).
2. **Lumi. Overridden by Bill 2026-10-06: Lumi is a glowing wisp.** (This replaces the lead's elf wisp-caller call.) She's a speaking,
   sentient wisp about 2× the wisp kit pet, with a neon-blue core, a pulsing violet halo and a real light pool. She's the nursery's own wisp,
   the first light Sylvaine drank from, and free now. The distinction from the small, wordless wisp kit is stated in 5.5 and 9.3. Her kit
   (2 mini-wisps, light zone, mark), `COMPANIONS.lumi`, sprite notes, barks, the outro and the tables are all updated.
3. **Svartalfheim locks at the befriend/conquer choice** (`lockRival` / `moodUp` in Aerin's choice, 5.2; 9.5).
4. **Gate pacing: Keybearer (800 Rift Marks) is fine.** Storm nights and Storm Watch are the intended fast track.
5. **Faelan stays a woman.**
6. **Prism tier III is parked.** The spec is kept in 9.2. Ship tiers I–II.
7. **Prism Edge scales with player level, min 10** (as written in 9.1).
8. **Rift-Breaker variant:** a short stub was added (section 13), low priority.
9. **Two of the 9 Prismdancer wisps outside Alfheim** (a Bifrost storm, Bakery Lane): fine.
10. **The Prism Heart sale to Sable stays** (400 g + 40 Black Doubloons).
11. **`prism_core` is added as the 5th socket gem.** Stats, sources and icon note are in 9.7. There's a cross-ref in `forge_alchemy.md` section 4.
12. **The midpoint reveal fires after Alfheim's Veyra beat** (6.10 has the queue code; the overview is updated).
13. **Mirelle's speaking lens is the Vault companion** (overhead lines, no follower code, 6.3).
14. **Dark Lumenvale is a re-grade:** gloom with cold violet, red and neon-blue glows, never flat dark. There's a readability floor. The full Art
    spec is in 9.6.
15. **The lavender day:** the builder checks for per-area day dimming first, with a full-screen tint overlay as the fallback. Both are in 2.2.
16. **Palette swap approved for P6:** the `mirroryou` enemy (8.4), with the generic duelist as fallback.
17. **Wisp Night every 7th night:** fine.
