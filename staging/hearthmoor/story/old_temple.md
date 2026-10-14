# The Old Temple: relighting the Rift-gate (Ravenhold, Midgard)

Story design doc, file 2 of 6 for Hearthmoor (staging, 2026-10-05). It uses the shapes in `game/data.js` (`ITEMS`,
`QUESTS`, `TALK`, `markerFor`), `factions.js` (`MERIT`, `REALM`), `bifrost.js` (`GATES`) and `ravenhold.js` (sealed
district gates). Conflicts are in the last section.

**Engine rule this doc follows:** stage **3 = done** is hard-coded in `G.setQuest` (toast, XP, `factions.onErrand`) and in
`drawLog` (the ✓). So both quests here use stages 1-2-3, and sub-progress inside a stage runs on flags with function steps,
the same way `harbor` / *The Road to the Rift* does.

---

## 1. Overview

Three nights before you reach the Temple, the **sacred cold-fire brazier** of Ravenhold's Old Temple went out. It had
burned since the Rift was young. Since then the Temple's **Rift-gate**, the stone arch in the inner court, has been dark. That
is why Bifrost's **Midgard arch** is sealed ("until the Temple is relit") and why mortals still cross by Sable's skiff.
The city watch found **dwarven forge tongs** at the altar and blamed the Forge Quarter. That was Veyra's frame-up.

Two linked story quests:

1. **The Cold Altar.** Warden Hilde sends you up with the Order of the Hearth's relief basket. Mother Ilse Brightwater asks
   you to find the truth. You and Brother Tamsin read three clues in the nave, and they prove the tools were planted.
2. **Keeper of the Gate.** A brazier lit by the Rift can only be relit with cold fire carried in a Rift-warden's
   lantern. Tamsin's ledger names a Hearthmoor warden, **Warden Aldis**, who was Grandpa Alder's grandmother. Alder gives you her
   **lantern charm**, Ida Wickmere lights it with a cold-fire wick, and you feed the seedling flame at three dark stair braziers.
   At dusk you set the charm on the altar. Blue fire pours up, the whole Temple chain-lights, and you raise the charm to the
   Rift-gate, which wakes. The Rift notices and tears open above the court (a scripted major rift). After the fight, a tired
   frost-witch in grey-blue seals the last crack with two fingers: **Veyra Ashmantle**'s first appearance (optional, see
   Decisions).

**Result:** the Temple's Rift-gate becomes a portal to Bifrost Crossing, Bifrost's Midgard arch opens back to the Temple,
and the quests pay **Hearth Tokens** (40 + 60 + 120). Gatewright Halvard adds 40 Rift Marks for a gate repaired, and he is a
little too interested in your charm.

**Look:** gloom-and-glow. The Temple starts dark grey and cold, lit only by refugee fish-orb lanterns and moonlight through
stained glass. When you relight it, **neon-blue cold fire** runs up the stair brazier by brazier, the glass throws violet and gold
pools, and the Rift-gate swirls rainbow inside a ring of blue runes. Emissive pixels, point lights and light pools, no bloom.

---

## 2. Placement

### 2.1 Ravenhold Harbor (existing area `ravenhold`)

- The Harbor's sealed **Old Temple gate** sits at `[-8.6, -11.7]` (`scene.game.sealed`, id `temple`). Once you carry the
  **Hearth writ** (*The Cold Altar* at stage ≥ 1), it stops being sealed and becomes an exit to the new area:
  `{ rect: [-9.6, -12.4, -7.6, -11.2], to: "temple", spawn: "from_harbor", label: "the Old Temple stair" }`.
- New ambient NPC at the gate: **Novice Edda** (section 3.4) at about `[-7.4, -10.4]`, facing down.
- When the gate opens, the `say` for the `temple` entry changes:
  `["The Old Temple gate stands open for Hearth folk. The stair climbs into the dark."]`, and after the relight,
  `["The Old Temple gate. Blue light spills down the stair from the top of the hill."]`.

### 2.2 New area: `temple` ("Ravenhold: the Old Temple")

A terraced hilltop at the top of Ravenhold. These are suggested coordinates in a box of about `[-11, -12, 11, 4]`. Fit them
to the kit.

| Zone | Contents | Suggested pos |
|---|---|---|
| Lower court (z 0 to 4) | arrival from the Harbor stair (`from_harbor` at `[0, 3.2, "up"]`); the refugee shelter on the west side (cots, soup pot, laundry lines, fish-orb lanterns on poles); a waystone on the east side | Ilse `[-3.6, 0.6]`, waystone `[6.0, 2.2]` |
| Stair terrace (z −1 to −4) | a wide stone stair with **3 dark braziers** (`tm_b1..3`) | `[-2.4, -2.2]`, `[2.4, -2.2]`, `[0, -4.0]` |
| Nave terrace (z −5 to −7) | the **altar with the sacred brazier**; a stained-glass back wall; **faceless angel statues** at x ±4.5; Tamsin's archive desk (east) | altar `[0, -6.0]`, Tamsin `[4.6, -5.4]` |
| Inner court (z −9 to −11) | the **Rift-gate** (a stone arch with a rune ring, dark until lit); the rift spot above it | arch `[0, -10.6]`, rift `[0, -9.4]` |

- **Clue spots** (look-at points, the same interaction as `sealed` looks): `scene.game.clues = [ {id: "clue_tongs",
  pos: [0.6, -5.2]}, {id: "clue_prints", pos: [-1.8, -6.6]}, {id: "clue_snuffer", pos: [-4.4, -6.2]} ]`. Text is in section 5.3.
- **Braziers:** use the Hollows brazier rule (a spell landing within `BRAZIER.reach` lights one). These three stay dark until
  the charm is lit (`S.flags.tm_wick`). Before that, a spell only gets the toast "The brazier won't catch. It wants a
  warden's flame."
- **Altar and gate:** E / A interact points that check flags (section 4).
- **Portal (after the relight):** `{ fx: "gate_midgard", to: "bifrost", spawn: "from_midgard",
  rect: [-0.8, -11.3, 0.8, -10.4], label: "the Rift-gate to Bifrost Crossing" }`.
- **Before / after:** before the relight, the stair, altar and gate braziers are dark (decals only), and the only lights are the
  refugee lanterns and blue moon-pools under the glass. After it, every brazier is cold-fire blue and becomes a light zone,
  and the arch has a rainbow vortex with blue rune pixels.
- `factions.js`: add `REALM.temple = "hearth"` so rifts and rares here pay Hearth Tokens.
- Music: the Ravenhold Temple arrangement (choir pads, E7.3). It is sparse while the Temple is dark and gains glass bells
  once it is lit.

### 2.3 Bifrost Crossing (existing area `bifrost`)

The Midgard arch is in `scene.game.sealed` (arch `midgard`). Once `temple_lit` is set, it moves to `scene.game.portals`
(the hook is in section 7).

---

## 3. NPCs

### 3.1 Mother Ilse Brightwater, high priestess

| Field | Value |
|---|---|
| TALK key / actor id | `priestess` |
| met flag | `S.met.ilse` |
| name plate | `Mother Ilse Brightwater, the Old Temple` |
| role | new `priestess` (fallback: recolour of the `elder` villager) |
| pos | `[-3.6, 0.6]` in the lower court (by the soup pot); after the relight she moves to `[-1.6, -5.4]` beside the altar |
| say | `["Soup's hot, flame's out. One of those is my fault. Not the flame."]` (after the relight: `["Flame's lit. Soup's on."]`) |

**Look (normal clothes):** tall, early sixties, deep brown skin, close-cropped silver hair under a soft grey headscarf. She
wears a cream wool tunic **belted at the waist** with a braided blue cord that holds a ring of temple keys and a tiny
cold-fire lamp, charcoal wide-leg trousers, and sandals over wool socks. The sprite reads as a cream top, charcoal bottom
and a blue belt line.

**Personality:** calm and warm, with dry humour and steel underneath. She mothers the refugees, won't blame anyone without
proof, and loves the flame but is honest that it's only a flame. She keeps the sacred brazier and runs the shelter.

### 3.2 Brother Tamsin, archivist

| Field | Value |
|---|---|
| TALK key / actor id | `archivist` |
| met flag | `S.met.tamsin` |
| name plate | `Brother Tamsin, archivist of the Old Temple` |
| role | new `archivist` (fallback: recolour of the `musician` villager) |
| pos | `[4.6, -5.4]` at the archive desk, facing left |
| say | `["Mind the ledgers. They don't bite. They do fall over."]` |

**Look (normal clothes):** early twenties, lanky, with an ink smudge on his nose and dark curls. He wears an oatmeal shirt
with rolled sleeves **tucked into** brown trousers, a belt with a small hanging candle-lantern, a satchel strap across his
chest, and a far-too-long blue scarf. He holds a quill.

**Personality:** eager, talks fast, loves old records and footnotes, and is a little scared of the faceless statues. He
hints at the angel storyline (*The Faceless Statues*), and he keeps the bestiary and the Rift order's ledgers.

### 3.3 Existing NPCs with new lines

| NPC (TALK key) | Role in these quests |
|---|---|
| Warden Hilde of the Hearth (`hilde`, Plaza) | gives the relief basket and the Hearth writ, which starts *The Cold Altar* |
| Gatewright Halvard Ness (`gatewright`, Bifrost) | hook option about the Midgard arch; reacts to the relight (section 8) |
| Grandpa Alder (`elder`, Plaza) | gives Warden Aldis's lantern charm |
| Ida Wickmere (`chandler`, Harbor) | lights the charm with a cold-fire wick |
| Harbormaster Brannoc (`harbormaster`), Quartermaster Sable (`quartermaster`) | one line each after the relight |

### 3.4 Novice Edda (new, small)

- TALK key `novice`, role: recolour of a villager. She is a teenager in a grey knit jumper, rust trousers, a belt with a
  little bell, and holds a lamp. Pos: Harbor `[-7.4, -10.4]`.
- Before the writ: `["Temple's shut, friend. Refugees only, and Order folk with a writ."]`
- With the writ: `["A Hearth writ! Mind the stair, it's dark since the brazier went out. Mother Ilse is in the lower court."]`
- After the relight: `["Look at the stair now! Blue all the way up. I don't even need my lamp."]`

### 3.5 Refugees (2-3 ambient, lower court)

Ambient `say` lines, one per actor, rotating:

- `"Our road is ice now. We walked out over the hill with the goats."`
- `"The soup's thin, but Mother Ilse makes it hot. Hot counts for a lot."`
- `"Is it true you've been to the Crossing? Is it as bright as they say?"`
- After the relight: `"Blue light on the stair again. My boy says it's the prettiest thing he's seen. He's seen a lot of snow."`
- After the relight: `"Two families went home through the gate today. Mother Ilse cried. She says it was the soup steam."`

### 3.6 Veyra Ashmantle (cameo, optional; see Decisions)

**Look (normal clothes, visible waist):** tall and pale, with long white-blonde hair in a loose braid and cold blue eyes. She
wears a long grey-blue wool coat worn open, **belted at the waist** with a frost-silver clasp, over a dark fitted tunic,
slate trousers and soft boots. Faint frost-flowers fade where she steps. No crown, no armour. In this scene she is gentle,
sad and convincing.

---

## 4. Quests (`QUESTS` entries)

```js
// The Cold Altar: Warden Hilde -> Mother Ilse; three clues prove the dwarven tools were planted
altar: {
  title: "The Cold Altar",
  giver: "Warden Hilde of the Hearth",
  story: true,
  steps: {
    1: "Carry the Order's relief basket to Mother Ilse at the Old Temple. Show the Hearth writ at the Temple gate in Ravenhold Harbor.",
    2: (S) => (clues(S) < 3
      ? `Find out who snuffed the sacred brazier. Look around the altar with Brother Tamsin. Clues: ${clues(S)}/3`
      : "Tell Mother Ilse what the clues say."),
    3: "The dwarven tools were planted. Someone wanted the Forge Quarter blamed and the Temple dark.",
  },
},
// Keeper of the Gate: Alder's charm -> Ida's wick -> 3 stair braziers -> the altar at dusk -> the Rift-gate -> the rift
gate: {
  title: "Keeper of the Gate",
  giver: "Mother Ilse Brightwater",
  story: true,
  steps: {
    1: (S) => { const F = S.flags || {}, inv = S.inv || {};
      if (!inv.alder_charm) return "Ask Grandpa Alder in Hearthmoor about Warden Aldis. Brother Tamsin's ledger says she was a Rift-warden.";
      if (!F.tm_wick) return "Ask Ida Wickmere, the cold-fire chandler on Ravenhold's piers, to light the lantern charm.";
      if (braziers(S) < 3) return `Feed the charm's flame at the 3 dark braziers on the Temple stair (cast a spell at each). ${braziers(S)}/3`;
      return "The charm burns bright blue. Bring it to Mother Ilse."; },
    2: (S) => { const F = S.flags || {};
      if (!F.tm_altar) return "At dusk or after dark, set the lantern charm on the cold altar (E / A).";
      if (!F.tm_gate) return "Hold the charm up to the dark Rift-gate in the inner court (E / A).";
      if (!F.tm_rift) return "Seal the rift tearing open above the Rift-gate!";
      return "Tell Mother Ilse the gate is lit."; },
    3: "The Rift-gate burns blue again. Midgard's arch at Bifrost Crossing stands open, and the skiff can rest.",
  },
},
```

Helpers: `clues(S)` counts `S.found.clue_tongs/prints/snuffer`; `braziers(S)` counts `S.found.tm_b1..3`.

### 4.1 Stage table

| Quest | Stage | Done when | Flags / found |
|---|---|---|---|
| altar | 1 | you hand the basket to Ilse | `inv.reliefbasket`, `inv.hearthwrit` |
| altar | 2 | 3 clues looked at, then you talk to Ilse | `found.clue_*` |
| altar | 3 | done; starts `gate` stage 1 | |
| gate | 1 | charm in the bag, Ida's wick, 3 braziers lit, then you talk to Ilse | `inv.alder_charm`, `flags.tm_wick`, `found.tm_b1..3` |
| gate | 2 | altar relit at dusk or night, gate lit, rift sealed, then you talk to Ilse | `flags.tm_altar`, `flags.tm_gate`, `flags.tm_rift` |
| gate | 3 | done; sets `flags.temple_lit` | |

### 4.2 Rewards

| When | Reward | Code |
|---|---|---|
| Basket delivered (altar 1 → 2) | **+40 Hearth Tokens**, the Temple waystone attunes | `G.factions.add("hearth", MERIT.refuge, "refuge")` |
| *The Cold Altar* done | **+60 Hearth Tokens**, 30 gold (plus story XP from `setQuest`) | `MERIT.altar` |
| Each stair brazier lit | a small blue sparkle; no merit (it's part of the rite) | |
| The scripted rift (tier II) | the normal major-rift reward (35 gold, 90 XP, a 60% shard chance), Rift Marks and Hearth through `onRift(1)` | |
| *Keeper of the Gate* done | **+120 Hearth Tokens**, 60 gold, 1 frost core gem, the Rift-gate portal, Bifrost's Midgard arch opens | `MERIT.relight`, `gem(G, "frost_core")` |
| First talk with Halvard after the relight | **+40 Rift Marks** (a gate repaired) | `G.factions.add("gate", MERIT.arch, "arch")` |

New `MERIT` keys (all within the existing scale, where boss = 80 and abyssal rift = 120):
`refuge: 40, altar: 60, relight: 120, arch: 40`.

Merit check: the opening already pays about 140 Hearth Tokens (3 errands × 40 + warden 20). This chain adds 220 Hearth Tokens
(about 360 total, plus anything from Temple rifts and rares). That is **Friend**, close to Trusted (400). See Decision 1 for how
the arch is keyed.

---

## 5. Dialogue

Every line fits the dialogue box (≤ 120 characters). `{cls}` variants use `S.cls`.

### 5.1 Starting it: Halvard's hook (Bifrost) and Warden Hilde (Plaza)

Add an option to `gatewright`'s `hooks` while `!flags.temple_lit`:

```js
{ label: "What about Midgard's arch?", pick: (G) => { flags(G.S).tm_hint = 1; return { pages: [
  "Midgard's arch is the far side of the Old Temple's Rift-gate. The Temple's flame went out, and the gate went dark.",
  "The Order of the Hearth tends the Temple's refugees. Ask Warden Hilde in Hearthmoor. Doors open for Hearth folk." ] }; } },
```

`hilde` (when `flags.bf_done && !quests.altar`). This branch goes before her default line:

```js
pages: [
  ...(F.tm_hint ? ["Midgard's arch, is it? Then you want the Temple anyway. Its Rift-gate is the arch's far side."] : []),
  "The Old Temple's full of folk from cut-off villages, and the Order owes them bread.",
  "Carry this basket up to Mother Ilse. The Temple gate is shut, but it opens for a Hearth writ. Here's yours.",
],
then: (G) => { G.give("reliefbasket", 1); G.give("hearthwrit", 1); G.setQuest("altar", 1); },
```

`hilde` reminders and later lines:

- altar 1: `["Up the Harbor's west stair to the Temple gate. Show Edda the writ. Mind the basket, the tea's loose."]`
- after `gate` = 3: `["Mother Ilse writes that you've a steady hand. From her, that's a medal."]`

### 5.2 Mother Ilse: first meeting (altar 1, basket in the bag)

```js
pages: [
  "Bread, blankets and Wren's tea. The Order remembered us. Bless you, and bless your aching arms.",
  "Mother Ilse Brightwater. I keep this Temple, and its flame. Kept. Three nights ago the sacred brazier went out.",
  "It has burned since the Rift was young. Cold fire doesn't go out on its own. Someone put it out.",
  "The watch found dwarven forge tongs at the altar and blamed the Forge Quarter. I'd like better proof than tongs.",
  "Brother Tamsin is up in the nave with his ledgers. Look around with him. Tell me what the Temple tells you.",
],
then: (G) => { G.take("reliefbasket", 1); G.S.met = { ...(G.S.met || {}), ilse: 1 };
               G.factions.add("hearth", MERIT.refuge, "refuge"); G.setQuest("altar", 2); },
```

Reminder (altar 2, fewer than 3 clues): `["Look at the altar with Tamsin's eyes. He sees ink. You see the rest."]`

### 5.3 Brother Tamsin and the three clues

Tamsin, first meeting:

```js
pages: [
  "Oh! A visitor who isn't a refugee or a watchman. Tamsin, archivist. Mind the ledgers. They don't bite. They fall over.",
  "Mother Ilse wants proof. I have opinions, which isn't the same. Look around the altar. I'll write down what you find.",
  "And don't mind the statues. They turn their masks toward the Rift at night. Probably the wind. Probably.",
],
then: (G) => { G.S.met = { ...(G.S.met || {}), tamsin: 1 }; },
```

Clue look texts (E / A at a clue spot, while altar = 2). The narration speaker is `{ id: "clue", name: "The nave" }`:

| Clue | Pages | Tamsin's line on your next talk |
|---|---|---|
| `clue_tongs` | `"Dwarven forge tongs. Good iron, rimed with frost. Forge tools live by the fire. These have never been warm."` | `"Frost on forge tongs. Writing it down. Underlining it."` |
| `clue_prints` | `"Frost-flowers in the shape of footprints, leading from the altar to the inner court. Not toward the forges."` | `"Footprints that freeze the floor. That's not a smith. That's not anyone I want to meet."` |
| `clue_snuffer` | `"A brazier snuffer behind a statue. Frost-iron, no maker's mark. Made so nobody could say whose it was."` | `"A snuffer with no name. Someone wanted no one blamed. Except whoever they did want blamed."` |

Seer extra page on each clue (`S.cls === "seer"`): `"(Your runes prickle. This was put here to be found. A frame, and a careful one.)"`
Runeguard extra page on `clue_prints` (`S.cls === "runeguard"`): `"(Long strides, light weight. Whoever walked here wasn't hurrying. They weren't afraid.)"`

Tamsin, idle during altar 2: `["Look by the altar's foot, behind the statues, and along the floor. Floors are honest."]`

### 5.4 Mother Ilse: *The Cold Altar* done, *Keeper of the Gate* starts (altar 2, 3 clues)

```js
pages: [
  "Cold tongs. Footprints walking the wrong way. A snuffer with no name on it.",
  "Nobody from the Forge Quarter did this. Someone wanted Ravenhold fighting itself, and the Temple dark while it did.",
  "I'll send word to the watch before anyone burns a forge. Thank you. Now for the harder thing.",
  "A brazier lit by the Rift can only be relit by cold fire carried in a warden's lantern. The wardens are long gone.",
  "Tamsin: \"But! The ledger lists a Hearthmoor warden, three lifetimes back. Warden Aldis. Ring any bells?\"",
  "Go home and ask, then. Hearthmoor folk keep everything. Especially lanterns.",
],
then: (G) => { G.setQuest("altar", 3); G.factions.add("hearth", MERIT.altar, "altar"); gold(G, 30); G.setQuest("gate", 1); },
```

Variant if the charm is already in the bag (the E1.5 opening beat, if it's built): replace the last two pages with
`"...Is that a warden's charm on your belt? Grandpa Alder's? Well. The Temple provides."` and skip Alder's step.

### 5.5 Grandpa Alder: the lantern charm (gate 1, no charm)

```js
pages: [
  "A Rift-warden? Aldis? ...Ah. Tamsin's ledger found my grandmother, did it.",
  "She walked the bridge once, when it still sang. She left me this, and a lot of stories nobody believed.",
  "It's a lantern charm. It held cold fire once. Take it. I think it's been waiting for you.",
],
then: (G) => { G.give("alder_charm", 1); G.toast("Warden Aldis's lantern charm. Cold, and waiting for a flame.", 2.6); },
```

Alder later: `["Is it lit? Show me. ...There it is. The same blue she used to talk about."]` (once `tm_wick` is set)
and after `temple_lit`: `["The Temple's lit, and by a Hearthmoor hand. Aldis would have been insufferable about it. Proudly."]`

### 5.6 Ida Wickmere: the wick (gate 1, charm, no `tm_wick`)

Add this before her shop line in `chandler`:

```js
pages: [
  "A warden's charm! I've only ever seen one in a book. Hold it still.",
  "Cold-fire wick, my very best. It'll catch, but it's a seedling flame. Feed it at the Temple's old braziers.",
],
then: (G) => { flags(G.S).tm_wick = 1; G.toast("The charm glows a small, stubborn blue.", 2.4); G.shopUI.show("harbor"); },
```

Ida later: `["How's my wick? Burning blue, I hope. Blue means it likes you."]`

### 5.7 The stair braziers (gate 1, wick lit)

- Toast per brazier: `Stair brazier lit (n/3). The charm's flame leans toward it, then grows.`
- After the first one is lit, 2 `wraith` foes slip out of the dark inner court (they hate the new light) and fight near the
  stair. This is a normal spawn and can't fail.
- Toast on the third: `Three blue braziers burn on the stair. The charm is bright enough to read by.`

### 5.8 Mother Ilse: ready for the rite (gate 1, all done)

```js
pages: [
  "That blue. Oh, that's the right blue. I'd almost forgotten it.",
  "Cold fire burns truest in the dark. Set the charm on the altar at dusk or after. I'll ring the old bell.",
],
choice: { id: "tm_rite", options: [
  ...(isDark(G) ? [{ label: "It's dark. I'm ready.", pick: (G) => { G.setQuest("gate", 2); return { pages: ["Then go. I'll be right behind you."] }; } }] : []),
  { label: "Rest on a refugee cot until dusk.", pick: (G) => { G.setQuest("gate", 2); G.restTo("dusk");
      return { pages: ["The cot is lumpy, the blanket smells of goats, and you sleep like a stone. Dusk comes blue."] }; } },
  { label: "Not yet.", cancel: true, pick: () => ({ pages: ["The altar will wait. It's had practice."] }) },
] },
```

(`isDark` = `clock.t > 0.75 || clock.t < 0.25`; `G.restTo` = the inn rest-to-time skip.)

### 5.9 The rite: altar, gate and rift (gate 2)

**The altar** (E / A at the altar while dark, `!tm_altar`). If it's still daytime:
`["The cold altar waits. Ilse said dusk or after. Cold fire burns truest in the dark."]`

```js
pages: [
  "You set the charm on the cold altar. For a breath, nothing. Then blue fire pours out of it like water running uphill.",
  "The sacred brazier roars awake. Blue light runs down the stair, brazier to brazier, and the stained glass blooms violet.",
  "Ilse: \"There. There it is. Now the gate. It's been dark so long it may not remember what it's for.\"",
],
then: (G) => { flags(G.S).tm_altar = 1; /* chain-light every temple brazier (0.25 s apart), glass light pools on, bell sfx */ },
```

**The Rift-gate** (E / A at the arch, `tm_altar && !tm_gate`):

```js
pages: [
  "You raise the charm to the dark arch. Runes wake around the stone one by one, cold blue, then every colour at once.",
  "The arch fills with a slow rainbow swirl. Far off, you hear the bells of Bifrost Crossing.",
  "Then the sky above the court cracks open. The Rift has noticed its old door.",
],
then: (G) => { flags(G.S).tm_gate = 1; G.rifts.open(1, G.ctx.scene.game.riftAt); },   // a scripted major rift (tier II)
```

The rift is tier II with its usual wave (4 foes: `wraith`, `skeleton`, `skelmage`, `wraith`) and a 50% rare chance. When it
seals, set `flags.tm_rift = 1`.
Toast: `The tear seals. A second crack is already spreading above the arch...` Then comes the Veyra cameo, or, if the cameo is
off, the crack simply fades: `...and fades. The Rift settles.`

### 5.10 Veyra's cameo (after the rift, optional)

Speaker `{ id: "veyra", name: "A frost-witch in grey-blue" }` on the first page, then `"Veyra"` once she gives her name.

```js
pages: [
  "Easy. It's only the Rift breathing out. It does that when someone lights a door it has forgotten.",
  "(She lifts two fingers. The crack above the arch stitches shut in a ribbon of frost.)",
  "Veyra Ashmantle. Once the Rift had a hundred wardens. Now it has me, and I am very tired.",
  "You relit the gate. That was kind. Kindness is rare up here.",
  "Someone is poisoning Ravenhold's water, down under the grates. If you find who, I would like to know.",
  "Keep that charm lit, hearth-walker. Cold fire remembers who carries it.",
],
then: (G) => { flags(G.S).met_veyra = 1; /* she walks into the arch's swirl and is gone; frost-flowers fade where she stood */ },
```

Seer extra page (subtle, it reveals nothing): `"(For a heartbeat your runes hear the frost on the tongs answer her, like an echo. Then it's gone.)"`
Cinderknight extra page: `"(She glances at your ember seam, and something cold passes over her face. Then the kind smile is back.)"`

### 5.11 Mother Ilse: *Keeper of the Gate* done (gate 2, `tm_rift`)

```js
pages: [
  ...(F.met_veyra ? ["The Rift-Warden. I thought the wardens were a bedtime story. She looked so tired."] : []),
  "The flame's lit, the gate's lit, and my refugees are cheering at a hole in the sky. What a week.",
  "The Rift-gate opens onto Bifrost Crossing, and Midgard's arch there opens back to us. Go where you're needed.",
  "Keep the charm. It's yours now. A warden's lantern shouldn't sit on a shelf.",
],
then: (G) => { const F = flags(G.S); F.temple_lit = 1; G.setQuest("gate", 3);
               G.factions.add("hearth", MERIT.relight, "relight"); gold(G, 60); gem(G, "frost_core");
               G.toast("The Rift-gate to Bifrost Crossing is open. Midgard's arch is lit.", 3.0); },
```

### 5.12 Later visits

**Mother Ilse** (the first matching line, top to bottom):

| Condition | Line |
|---|---|
| night | `"Listen. You can hear the brazier hum at night. It sounds pleased with itself."` |
| Vanaheim befriended | `"A gnome from Mossbrook came to pray. Or to steal candles. Either way, he left a bun."` |
| Vanaheim conquered | `"Mossbrook folk came through the gate today. They didn't look at you kindly. I gave them soup anyway."` |
| `met_veyra` (once) | `"I keep thinking of the Warden. Someone that tired shouldn't be holding the Rift alone."` |
| default | `"Flame's lit. Soup's on. Sit if you like. The Temple has room again."` |

**Brother Tamsin:**

| Condition | Line |
|---|---|
| night | `"The statues turned toward the gate again last night. I wrote it down. Twice. In capitals."` |
| `met_veyra` (once) | `"She sealed it with two fingers. Two! The ledger says the old order needed a whole choir."` |
| after the relight (once) | `"The ledger says the old order didn't build the Rift-gate. They found it. Nobody wrote down who built it."` |
| default | `"Ask me anything. Except about the statues. Actually, do ask about the statues."` |

Tamsin hub (optional, later builds): "Tell me about the Rift order." / "The statues?" (starts *The Faceless Statues* ripple) /
"The bestiary." / "Goodbye."

**Brannoc**, after the relight: `["See that blue at the top of the hill? The Temple's lit. I've watched that light forty years. I missed it."]`
**Sable**, after the relight: `["A gate that doesn't need my skiff. Bad for business, good for the city. I'll sulk quietly."]`

---

## 6. Items (`ITEMS` entries)

```js
reliefbasket: { name: "Order relief basket", px: "reliefbasket",
                about: "Hearthloaves, wool blankets and a tin of Wren's tea, packed by the Order of the Hearth for the Old Temple." },
hearthwrit:   { name: "Hearth writ", px: "hearthwrit",
                about: "A folded writ with the Order's wax seal. The Old Temple's gate opens for whoever carries it." },
alder_charm:  { name: "Warden Aldis's lantern charm", px: "alder_charm",
                about: "A thumb-sized brass lantern on a chain. Grandpa Alder's grandmother carried it on the Rift." },
```

- After `tm_wick`, the charm's bag text can read: `"A thumb-sized brass lantern. A small cold-fire flame burns inside and never gutters."`
  (Use a function `about`, or a second id `alder_charm_lit`. This is the builder's call.)
- The charm is a **key item**: it can't be sold and stays in the bag. Later uses: Gate Day bonuses, and Bill's E1.5 says it's
  "your key to Ravenhold's Rift-gate". Once the gate is lit, the gate is free to everyone.
- **Pixel art:** the basket is a woven basket with a blue cloth and a loaf poking out. The writ is cream paper with a red wax
  seal. The charm is a brass mini-lantern with a blue flame pixel (dark glass before it's lit).

---

## 7. Gate hooks (Harbor gate, Bifrost arch)

```js
// ravenhold.js: the Old Temple's district gate opens for the writ
export const templeOpen = (S) => (S.quests.altar || 0) >= 1;
// in Harbor.attach (or area load): if templeOpen(S), drop 'temple' from scene.game.sealed and add the exit (section 2.1)

// bifrost.js: Midgard's arch opens once the Temple is relit (Decision 1, option A)
export const midgardOpen = (S) => !!(S.flags || {}).temple_lit;
// GATES.midgard stays as the sealed look before then, with its text pointing at the quest:
midgard: ["Rainbow light runs round the seal. Its far side is the Old Temple's Rift-gate in Ravenhold, dark and cold. Until the Temple is relit, mortals cross by Corsair skiff.", ["hearth", 2]],
// Crossing.attach: if midgardOpen(S), move the 'midgard' arch from scene.game.sealed into scene.game.portals:
//   { fx: "gate_midgard", to: "temple", spawn: "from_bifrost", rect: [arch.pos[0]-0.75, arch.pos[1]-0.85, arch.pos[0]+0.75, arch.pos[1]], label: "Midgard's gate" }
// Crossing.pages(g): for arch 'midgard', replace the key line with the quest pointer while !temple_lit:
//   "Key: relight the Old Temple's flame (Order of the Hearth). Ask Warden Hilde in Hearthmoor."
```

- Spawns: `temple.from_bifrost = [0, -9.2, "down"]` (just in front of the Rift-gate). `bifrost.from_midgard` = in front of the
  Midgard arch, facing down.
- `ravenhold.js WAYS`: add `temple: ["the Old Temple, Ravenhold", "temple", "from_waystone"]` and a `WAY_SAY.temple` line:
  `"Cold-fire runes glow along the waystone. The Temple's old stones remember every pilgrim."`
- The skiff stays: Sable still sails both ways, which is quicker from the Harbor.
- Option B (if Bill picks it): `midgardOpen = (S) => temple_lit && G.factions.rank("hearth") >= 2`, and the sealed look says
  `"The Temple is lit. The arch wants a Trusted friend of the Hearth to walk it first."`

---

## 8. How Halvard reacts

The first talk with `gatewright` after `temple_lit` (`!S.met.arch`) goes before the hub:

```js
pages: [
  "Midgard's arch is lit! The whole ledger shook when it caught. Mother Ilse's flame, from the Temple itself?",
  "Then the city has a front door again, and Sable's skiff a quieter season. Forty marks for a gate repaired.",
  "That charm of yours. A warden's lantern, if I'm any judge. Keep it close. Keys go missing at the Crossing.",
],
then: (G) => { G.S.met = { ...(G.S.met || {}), arch: 1 }; G.factions.add("gate", MERIT.arch, "arch"); },
```

- **Later** (rotates into his first page now and then): `"Midgard's arch has the steadiest light of the nine. I check it every night. Habit."`
- **If you mention Veyra** (an optional hook when `met_veyra`, label "I met the Rift-Warden."):
  `["Veyra? Here? ...The Guild hasn't seen a warden in years. If she's holding the Rift, we should all be grateful."]`
  then `["Did she say where she was going? No? No matter. The ledger will find her, if she wants finding."]`
- **His "Which way is home?" answer** after the relight: `["Midgard's arch, now that the Temple is lit. Or Sable's skiff, if you like getting wet."]`
- **Foreshadowing intent (Act 3 betrayal):** he is too interested in the charm ("keys go missing"), checks the arch "every night",
  and asks where Veyra went. Each line reads as friendly the first time and pointed afterwards.

---

## 9. `markerFor` additions

```js
const F = S.flags || {}, inv = S.inv || {};
if (id === "hilde" && F.bf_done && !q.altar) return "quest_mark";
if (id === "priestess" && q.altar === 1 && inv.reliefbasket) return "quest_turnin";
if (id === "priestess" && q.altar === 2 && clues(S) >= 3) return "quest_turnin";
if (id === "elder" && q.gate === 1 && !inv.alder_charm) return "quest_mark";
if (id === "chandler" && q.gate === 1 && inv.alder_charm && !F.tm_wick) return "quest_turnin";
if (id === "priestess" && q.gate === 1 && F.tm_wick && braziers(S) >= 3) return "quest_turnin";
if (id === "priestess" && q.gate === 2 && F.tm_rift) return "quest_turnin";
if (id === "gatewright" && F.temple_lit && !(S.met || {}).arch) return "quest_turnin";
```

---

## 10. Save shape (summary)

| Key | Meaning |
|---|---|
| `S.quests.altar`, `S.quests.gate` | 0-3 (3 = done) |
| `S.met.ilse`, `S.met.tamsin`, `S.met.arch` | first talks (`arch` = Halvard's relight talk) |
| `S.found.clue_tongs/prints/snuffer`, `S.found.tm_b1..3` | clues looked at, stair braziers lit |
| `S.flags.tm_hint`, `tm_wick`, `tm_altar`, `tm_gate`, `tm_rift`, `temple_lit`, `met_veyra` | progress |
| `S.inv.reliefbasket`, `hearthwrit`, `alder_charm` | items |
| `MERIT.refuge / altar / relight / arch` | 40 / 60 / 120 / 40 |
| `REALM.temple` | `"hearth"` |

---

## 11. Decisions needed

1. **How the Midgard arch is keyed.** `GATES.midgard` asks for **Hearth Trusted** (400). This chain plus the opening pays about
   360. **Option A (recommended):** relighting the Temple opens the arch by itself, so the relight is the key, which matches the
   gate's own text "until the Temple is relit". **Option B:** you need the relight **and** Trusted, so most players end the
   climax about 40 tokens short (Refuge deliveries, Midgard rifts or rares make up the rest). Raising `MERIT.relight` above 120 would break
   the current scale.
2. **Story order.** The design (E2.3) put *Keeper of the Gate* at the **end of Act 1, before** Bifrost. The build already reaches
   Bifrost by skiff, so this chain becomes a post-Bifrost return to Midgard. It is still Midgard story, but the Plaguewell
   now comes after the gate. Is that OK?
3. **Veyra's first appearance.** E2.3 places it at the Cold Altar riot. This doc puts it right after the relight (section 5.10).
   She stays gentle and isn't revealed, and she hands you the Plaguewell hook. Keep it here, move it, or switch it off (the
   flow works without it)?
4. **The Cold Altar riot.** The Forge Quarter isn't built, so the riot and the Forge Quarter's vindication happen offscreen
   (Ilse "sends word to the watch"). When the Forge district is built, add a short riot beat there.
5. **The Hilde name clash.** The code has **Warden Hilde of the Hearth** (Order of the Hearth, Plaza). E6.2 has **Hilde Anvilsong**,
   the Forge Quarter smith. This doc uses the code's Warden Hilde. The smith in `forge_alchemy.md` needs a new first name
   unless Bill prefers otherwise.
6. **Alder's charm timing.** E1.5 gives the charm the morning after Lantern Eve. The build doesn't, so here Alder gives it when
   you ask. If E1.5 is built later, Ilse's variant line covers it (section 5.4).
7. **New names:** **Warden Aldis** (Alder's grandmother, the Hearthmoor Rift-warden in Tamsin's ledger) and **Novice Edda**
   (the gate novice). Both are new. OK?
8. **New area.** This needs a `temple` area (the Old Temple district) and `REALM.temple = "hearth"`. Only the Harbor is built
   in Ravenhold today.
