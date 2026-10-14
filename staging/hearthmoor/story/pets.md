# Pets: the Stray Den at Bifrost Crossing

Story design doc, file 1 of 6 for Hearthmoor (staging, 2026-10-05). Written to lift straight into `game/data.js`
shapes (`ITEMS`, `QUESTS`, `TALK`, `markerFor`) plus one new table (`PETS`). Nothing here changes decided design;
the conflicts are listed in section 9.

---

## 1. Overview

Since the Rift cracked on Lantern Eve, small glowing creatures keep falling out of the tears. Wisps, moths and fox kits
tumble onto the bridge, lost and frightened. They all end up at the **Stray Den**, a round stone kennel-house on the
west side of the Bifrost Crossing plaza run by **Signe Larkspur**. She used to keep the Gatekeepers' Guild's message
ravens and now keeps everything else.

Your first pet comes from a short side quest, **Strays of the Rift**. You light the Den yard's cold-fire lanterns, seal a
little rift that is scaring the strays, bring a glow seed that hums like home, then sit by the hearth after dusk while
three strays creep out to meet you: a **wisp kit** (neon-blue cold fire), a **glow-moth** (violet and gold) and a
**lantern-fox** (red neon tail-lantern with a tiny light-fish inside). You pick one and name it. The other two stay
at the Den, and you can adopt them later.

Pet rules (from the handoff, section 6.6): **one active pet**. It follows you, lights the area around you, and gives a small
aura buff. You swap pets at the Stray Den. Pets never fight. They glow, notice things and carry you home when you
faint (E4.1).

Tone: cozy gloom-and-glow. The Den is a pool of blue, violet and red light in the dark, with fish-orb lanterns along the
eaves and a cold-fire hearth inside.

---

## 2. The Stray Den (place)

- **Where:** Bifrost Crossing, west side of the plaza, a short walk from Gatewright Halvard (who stands at about
  `[-4.4, -0.3]`). Suggested spot: the Den door at about **`[-8.6, 2.8]`**, Signe at **`[-7.4, 3.9]` facing down**, the yard
  between them (inside the ±11 camera bounds). These coordinates are only suggestions. Fit them to the plaza.
- **Look:** a squat round stone house with a crooked roof of patchy **rainbow-glass tiles**. **Orb lanterns with glowing
  fish** hang along the eaves. The yard has three **cold-fire lanterns on posts** (unlit until the quest), a woodpile, straw
  baskets, a scratching post and a little stone trough fed by fizzing Rift-water. A painted sign reads
  *STRAY DEN: knock, then wait, then knock softer.*
- **At night:** the strays glow through the windows, blue wisps, violet moths and red fox-tails, so the whole Den reads as a
  soft pool of three neon colours. Light pools only, no bloom.
- **Inside (if an interior is ever built):** a blue **cold-fire hearth**, perches, baskets of sleeping glows, a shelf of
  biscuit tins, and Signe's three-legged snow hare **Pockets** asleep in a hat box (a nod to the snow hare pet from Jotunheim).
- **Area data idea:** `scene.game.den = { pos: [-8.6, 2.8], lanterns: [{id: 'den_l1', pos}, {id: 'den_l2', pos},
  {id: 'den_l3', pos}], hearth: [x, z], rift: [x, z] }`. The lanterns use the Hollows brazier rule (a spell landing within
  ~2.6 m lights one; `BRAZIER` colour `#5ac8ff`). Once lit, they stay lit and act as light zones.

---

## 3. The keeper: Signe Larkspur

| Field | Value |
|---|---|
| id / TALK key | `denkeeper` |
| met flag | `S.met.signe` |
| name plate | `Signe Larkspur, keeper of the Stray Den` |
| sprite role | new role `denkeeper` (fallback: a recolour of Wren's `herbalist` villager) |
| behavior | `idle`, `talkable: true`, facing `down` |
| ambient `say` | `["Knock, then wait, then knock softer. The strays are listening."]` |

**Look (normal clothes, separate top and bottom, visible waist):** mid-fifties, short and sturdy, with freckled brown skin.
Her grey-streaked auburn hair sits in a messy bun stuck with a pencil and a raven feather, and she wears round spectacles. She
has a moss-green knit jumper with the sleeves shoved up, tucked into rust-brown corduroy trousers. A wide leather belt carries
treat pouches and a ring of tiny brass bells. Scuffed boots. A sleepy glow-moth sometimes naps on her shoulder.
Sprite read: green top, rust bottom, belt line with gold bell pixels.

**Personality:** brisk, warm and wry. She talks to animals more politely than she talks to people, and she pretends to be
grumpy but gives everything away. She is practical about danger ("it's only a little rift") and soft about strays. She
keeps her own counsel about the Crossing's politics, but she notices things, and her strays notice more.

**Backstory (lore, for the Tavern rumour mill or Brother Tamsin's archive):** she kept the Guild's message ravens
for twenty years. On Lantern Eve the ravens came home with the Rift's strays trailing behind them, and she has run the Den
ever since. The Guild gives her a roof and very little else.

---

## 4. Side quest: Strays of the Rift

**Overview:** a side quest with four objectives (a small fight, a fetch, a night beat and a choice). It teaches
pets, auras and pet light. Available once you finish *The Road to the Rift* at Bifrost (`S.flags.bf_done`).

**Engine rule:** `G.setQuest` and `drawLog` treat stage **3 as done**. So the four objectives run across stages 1-2 with
flags (the same pattern as `harbor`), and stage 3 = done.

### 4.1 `QUESTS` entry

```js
strays: {
  title: "Strays of the Rift",
  giver: "Signe Larkspur",
  side: true,        // see 9.2: errandsDone() must skip it, or it counts toward "quests n/3"
  steps: {
    1: (S) => { const F = S.flags || {};
      if (litCount(S) < 3) return `Light the 3 cold-fire lanterns in the Stray Den's yard (cast any spell at one). ${litCount(S)}/3`;
      if (!F.den_riftOpen) return "Tell Signe the lanterns are lit.";
      if (!F.den_rift) return "Seal the little rift behind the Stray Den's woodpile.";
      return "Tell Signe the rift is sealed."; },
    2: (S) => ((S.flags || {}).den_seed
      ? "Come back to the Stray Den after dusk and sit by the cold-fire hearth."
      : "Bring Signe a glow seed (Odo's Wares or Wickmere's Chandlery) or a moonpetal."),
    3: (S) => `${(S.pet && S.pet.name) || "Your pet"} has a home with you now. The other strays wait at the Den.`,
  },
},
```

### 4.2 Steps and objectives

| Objective (stage) | Objective | How it completes | Notes |
|---|---|---|---|
| A (stage 1) | Light the 3 cold-fire lanterns in the Den yard | a spell landing near each lantern (`S.found.den_l1..3`) | the Hollows brazier rule; toast on each one lit |
| B (stage 1) | Seal the little rift behind the woodpile | a scripted **minor rift** (tier I, `Rifts.open(0, den.rift)`) cleared | 3 foes: 2 `wraith` + 1 `skeleton` (the existing rift pool), no rare; pays the normal minor-rift reward + Rift Marks |
| C (stage 2) | Bring a glow seed or a moonpetal | talk to Signe with `inv.glowseed >= 1` or `inv.moonpetal >= 1`; she takes one | glow seeds cost 8 gold at Odo's or Ida's |
| D (stage 2) | Come back after dusk, sit by the hearth | talk to Signe when `clock.t > 0.75 \|\| clock.t < 0.25`, **or** pick "Can we make it dark now?" | the shutters option sets `S.flags.den_dark` so nobody has to wait |
| Done (stage 3) | Done | the pet choice + the name choice | gives the pet, the rewards and `S.pet` |

### 4.3 Rewards

| Reward | Amount | Code |
|---|---|---|
| Your first pet | wisp kit, glow-moth or lantern-fox | `S.pet = {id, name, bond: 1}`, `S.pets[id] = {name, bond: 1}` |
| Order of the Hearth merit | **+40 Hearth Tokens** | paid automatically: `G.setQuest(id, 3)` on a non-story quest already calls `factions.onErrand()` (`MERIT.errand` = 40, Hearth). Fitting, since the Hearth gives pets (handoff, section 9.1). Don't add it again. |
| Gold | 25 | `gold(G, 25)` |
| Den biscuits | 3 | `G.give('denbiscuit', 3)` |
| Unlocks | pet swapping at the Den; Signe's biscuit shop; "Adopt another stray" | `S.flags.den = 1` |

Objective B's rift also pays its usual tier-I reward (15 gold, 40 XP, Rift Marks through `onRift(0)`), so the quest has
some Guild merit in it too.

### 4.4 Quest marker (`markerFor`)

```js
if (id === "denkeeper" && (S.flags || {}).bf_done && !q.strays) return "quest_mark";
const F = S.flags || {};
if (id === "denkeeper" && q.strays === 1 && litCount(S) >= 3 && !F.den_riftOpen) return "quest_turnin";
if (id === "denkeeper" && q.strays === 1 && F.den_rift) return "quest_turnin";
if (id === "denkeeper" && q.strays === 2 && !F.den_seed && ((S.inv.glowseed || 0) + (S.inv.moonpetal || 0)) > 0) return "quest_turnin";
if (id === "denkeeper" && q.strays === 2 && F.den_seed) return "quest_turnin";
```

---

## 5. Keeper dialogue (all lines short enough for the dialogue box)

### 5.1 First meeting (quest offer, `q.strays` = 0)

```js
pages: [
  "Mind the basket! Signe Larkspur, keeper of the Stray Den. Everything in here fell out of the Rift and landed on me.",
  "Since Lantern Eve the tears keep spitting out strays. Wisps, moths, a fox kit with a lamp for a tail.",
  "Three new ones came through last night, and they're hiding under the floor. Will you help me coax them out?",
  "Strays creep toward a kind light. Light my three yard lanterns. Any spell will do.",
],
then: (G) => { G.S.met = { ...(G.S.met || {}), signe: 1 }; G.setQuest("strays", 1); },
```

If `bf_done` isn't set yet (you came by waystone before finishing the harbor quest):
`["The Den's shut to new faces till the Guild has your name. Go and see Halvard first, then come back."]`

### 5.2 Objective A: light the lanterns

- Reminder: `["Any spell will do. Cold-fire catches on anything that means well."]`
- Toast per lantern: `Den lantern lit (n/3). Something small sneezes under the floorboards.`
- Toast on the third: `Three blue lanterns burn in the Den yard. Tiny eyes shine under the floor.`
- Turn-in:

```js
pages: [
  "Look at that, three noses! ...Oh. And a tear behind the woodpile. No wonder they won't come out.",
  "It's only a little one. Seal it for me? I'll hold the biscuits.",
],
then: (G) => { flags(G.S).den_riftOpen = 1; G.rifts.open(0, G.ctx.scene.game.den.rift); G.refreshMarkers(); },
```

### 5.3 Objective B: the little rift

- Reminder: `["Behind the woodpile. Cold-fire wraiths hate a lit yard, so stay near the lanterns if it gets busy."]`
- When the rift seals, set `S.flags.den_rift = 1`, and show the toast `The little rift seals. A fox kit peeks out, then thinks better of it.`
- Turn-in:

```js
pages: [
  "Sealed! You've a steady hand. Now they need something that smells like somewhere.",
  "A glow seed hums like a garden at night. Odo and Ida Wickmere both sell them. A moonpetal works too.",
],
then: (G) => G.setQuest("strays", 2),
```

### 5.4 Objective C: something that hums like home

- Reminder (none in the bag): `["A glow seed or a moonpetal. Anything that hums. Strays trust a hum."]`
- Turn-in (takes a glow seed first, else a moonpetal):

```js
pages: [
  "That hum! Hear it? The whole floor just went quiet to listen.",
  "Now we wait for dusk. Strays are brave in the dark, same as wisps. Come back after sundown and sit by the hearth.",
],
choice: { id: "den_dark", options: [
  { label: "I'll come back after dark.", cancel: true,
    pick: (G) => { flags(G.S).den_seed = 1; return { pages: ["Rest at an inn if you like. Night comes quicker that way."] }; } },
  { label: "Can we make it dark now?",
    pick: (G) => { flags(G.S).den_seed = 1; flags(G.S).den_dark = 1;
                   return { pages: ["Ha. I'll draw the shutters. The Den's dark enough inside. Sit, sit."], then: denNight }; } },
] },
```

### 5.5 Objective D: the hearth (night or shutters drawn), then the choice

`denNight(G)` opens this scene. Narration pages use `{ id: "den", name: "The Stray Den" }`.

```js
pages: [
  "You sit by the hearth. The cold-fire burns low and blue. One by one, three small lights creep out.",
  "A wisp kit bobs up first, humming like a kettle. It bumps your knee and fizzes.",
  "A glow-moth lands on your sleeve, fanning violet eyespots. It smells of old books and summer.",
  "A fox kit pads out last. Its round tail-lantern glows red, and a tiny light-fish swims inside it.",
  "Signe: \"They've all picked you. Rude of them, really. You only get to pick one, though.\"",
],
choice: { id: "pet_pick", options: [
  { label: "The wisp kit. (A cold-fire light, quicker spells.)",   pick: (G) => pickPet(G, "wispkit") },
  { label: "The glow-moth. (Finds hidden things, better healing.)", pick: (G) => pickPet(G, "glowmoth") },
  { label: "The lantern-fox. (Senses rifts, more Rift Marks.)",     pick: (G) => pickPet(G, "lanternfox") },
  { label: "I need a minute.", cancel: true, pick: () => ({ pages: ["Take your time. They're not going anywhere. Well. They might."] }) },
] },
```

Per-pet reaction (first page of `pickPet`), then the name choice:

| Pet | Reaction line |
|---|---|
| wispkit | `"The wisp kit flares so bright the whole Den goes blue. That's a yes, if you were wondering."` |
| glowmoth | `"The glow-moth settles on your shoulder like it's always lived there. Moths don't do that for just anyone."` |
| lanternfox | `"The fox kit flops onto your boots, tail-lantern thumping. The little fish does a loop. Smitten, both of them."` |

```js
// name choice: 4 names drawn from the pet's list (seeded by the save) + keep the species name
pages: ["Now it'll need a name. Something short, so it comes when you call."],
choice: { id: "pet_name", options: [...fourNames.map((n) => ({ label: n, pick: (G) => namePet(G, n) })),
                                    { label: `Just "${PETS[id].name}".`, pick: (G) => namePet(G, PETS[id].name) }] },
```

Finish (`namePet`), with `{name}` = the chosen name:

```js
pages: [
  "There. {name} is yours, and you're {name}'s, which is the bigger job.",
  "Three Den biscuits, a little gold for the road, and a good word to the Order. They like a pet with a home.",
  "The other two can stay with me. Come back when you're ready for more company, or for a swap.",
],
then: (G) => { /* set S.pet / S.pets, give rewards (4.3), G.setQuest("strays", 3), spawn the pet actor */ },
```

Toast: `✦ {name} the {species} joined you. Aura: {aura name}. (One pet at a time. Swap at the Stray Den.)`

### 5.6 Later visits (the Den hub)

The first page rotates by state (pick the first one that matches, top to bottom), then the hub choice.

| Condition | Line |
|---|---|
| a rift storm in the Crossing (see `rift_storms.md`) | `"Storm's up. The strays are under the floor again. Bring a light if you're staying."` |
| `S.flags.fainted_recent` (fainted in the last in-game day) | `"Heard {name} hauled you home again. Biscuit for {name}. Nothing for you, you know what you did."` |
| Gate Day festival | `"Gate Day! Every stray in the Crossing turns up for the fish lanterns. Even the ones who don't eat fish."` |
| pet bond 3 | `"{name} looks at you like you hung the moon. Took me thirty years to get that look from a cat."` |
| Vanaheim befriended | `"The moss-pups heard you're a friend of Mossbrook. They've been wagging since breakfast."` |
| Vanaheim conquered | `"A stray came in from Mossbrook, singed and shaking. I don't ask whose side you're on. I just ask."` |
| night | `"Shh. The moths are reading. Well, sitting on books. Same thing."` |
| first realm resolved, and the Halvard betrayal hasn't happened yet (foreshadow, see 9.4) | `"Funny thing. Not one stray will go near the Gatewright. Animals can be wrong. Not often."` |
| default | `"Strays fed, hearth lit, roof mostly on. What can the Den do for you?"` |

```js
choice: { id: "den", options: [
  { label: "Swap my pet.",                pick: (G) => denSwap(G) },          // lists S.pets except the active one
  { label: "Buy Den biscuits (6 gold).",  pick: (G) => buyBiscuit(G) },
  { label: "Adopt another stray.",        pick: (G) => denAdopt(G) },         // see 6.4
  { label: "Tell me about pet auras.",    pick: () => ({ pages: [
      "Every pet hums a little aura. Small, but it adds up, like biscuits.",
      "Feed a biscuit once a day and the bond grows. At three hearts, the aura grows with it.",
      "At night your pet's glow is a light pool. Wraiths keep out of it, same as a lantern." ] }) },
  { label: "Just visiting.", cancel: true, pick: () => ({ pages: ["Visit any time. Knock softer on the way out."] }) },
] },
```

Short replies for the hub:

- Swap: `"Swapping? {old} gets the warm basket. {new}, up you get. No sulking, either of you."`
- Biscuit bought: `"Oat and moonpetal. Don't eat them yourself. Everyone tries it once."`
- Not enough gold: `"Six gold, love. The strays are cheap. The biscuits aren't."`
- Adopt locked: `"I don't hand out strays to just anyone. Get the Hearth to call you Friend, then we'll talk."`
- Adopt, affordable: `"A forty-gold gift to the Den, and {species} goes home with you. It's a donation, not a sale."`
- Adopt, nobody left: `"Every stray in the Den has a name now. The Rift will send more. It always does."`

---

## 6. The three starter pets

### 6.1 `PETS` table (new, `game/pets.js` or in `data.js`)

Mod keys reuse the ones in `progress.js` and `loot.js` (`spellCd`, `healMul`, `stRegen`). There are three new keys:
`secretSense` (metres), `riftWarn` (seconds) and `riftMarkMul`.

```js
export const PETS = {
  wispkit: {
    name: "Wisp kit", species: "wisp kit", role: "pet_wisp", float: 0.95, glow: "#5ac8ff",
    light: { r: 2.2, intensity: 4 },                          // light zone at night (src: 'pet')
    aura: { id: "coldfire_focus", name: "Cold-fire Focus", desc: "Spell cooldowns 6% shorter. Bond 3: 8%.",
            mods: { spellCd: 0.06 }, bond3: { spellCd: 0.08 } },
    about: "A palm-sized orb of neon-blue cold fire with two dot eyes and a flicker for a tail. Hums when happy.",
    names: ["Pip", "Wick", "Glimmer", "Bluebell", "Sputter", "Nix", "Flicker", "Mote", "Skerry", "Sapphire"],
  },
  glowmoth: {
    name: "Glow-moth", species: "glow-moth", role: "pet_moth", float: 1.1, glow: "#a45cf0",
    light: { r: 1.8, intensity: 3 },
    aura: { id: "lamplight_dust", name: "Lamplight Dust", desc: "Hidden doors, gnome doors and springs shimmer within 6 m. Healing +10%. Bond 3: 8 m, +12%.",
            mods: { secretSense: 6, healMul: 0.10 }, bond3: { secretSense: 8, healMul: 0.12 } },
    about: "A fluffy moth the size of a sparrow. Cream fur, gold antennae, violet eyespots that glow in the dark.",
    names: ["Velvet", "Plum", "Hush", "Duskwing", "Mothwick", "Lavender", "Nimbus", "Fuzz", "Sorrel-moth", "Page"],
  },
  lanternfox: {
    name: "Lantern-fox", species: "lantern-fox", role: "pet_fox", float: 0, glow: "#ff4a3a",
    light: { r: 1.6, intensity: 3 },
    aura: { id: "rift_sense", name: "Rift-sense", desc: "Rifts are sensed 10 s earlier, with a direction. +10% Rift Marks, stamina refills 8% faster. Bond 3: 15 s, +12%, 10%.",
            mods: { riftWarn: 10, riftMarkMul: 0.10, stRegen: 0.08 }, bond3: { riftWarn: 15, riftMarkMul: 0.12, stRegen: 0.10 } },
    about: "A rust-red fox kit with white socks. Its tail ends in a round glowing tuft, and a tiny light-fish swims inside.",
    names: ["Ember", "Rusk", "Tinder", "Cinnabar", "Pepper", "Saffron", "Tally", "Hob", "Marigold", "Rowan"],
  },
};
```

Names avoid clashes with existing names (no Lumi, Kindle, Biscuit, Pudding, Dusty or Sorrel). "Sorrel-moth" is a joke
on Mossglen's Sorrel, so drop it if it reads as confusing.

### 6.2 Flavour and art notes

**Wisp kit (blue, cold fire).** *"Wisps are what's left when a lantern-wish doesn't make it all the way to the Rift. This
one made it halfway and decided it liked you better."*
Sprite: about 10x10 px plus a 3-4 px flame tail, floating at shoulder height with a slow 0.9 s bob. Neon-blue core,
white-hot centre pixel, darker blue rim, two dark dot eyes. It drops `coldfire_motes` every few seconds, and the motes
reuse the harbor's effect. It is the brightest pet light, and Bill's top glow.

**Glow-moth (violet and gold).** *"Glow-moths live in the dusty corners of old temples and eat nothing but lamplight. They
can smell a door that wants to be found."*
Sprite: about 14x10 px. Cream fur body, gold antennae, violet eyespots on the wings that glow at night (emissive pixels).
It flutters in lazy figure-eights about 1.1 m up, leaves a faint `glitter` trail and lands on lamps when you stand still.

**Lantern-fox (red neon tail-lantern).** *"Rift foxes are born on the bridge. Their tails hold a single light-fish, which
swims faster when a tear is about to open. Nobody knows where the fish comes from. The foxes aren't telling."*
Sprite: about 16x12 px on the ground. Rust-red fur, white chest and socks, black ear tips. The tail tip is a round
glowing bulb (red neon rim, warm orange inside) with a 2-pixel light-fish that loops. It trots at your heel and sits when
you stop.

All three are well under half the player's height, as pets should be. None wears clothes or armour.

### 6.3 Aura balance notes

- Compare: the spring-fizz buff is +15% damage for 60 s, and the faction Friend perks are 10-25%. These auras sit at
  6-12%, always on, and small enough that no pet is the "correct" pick.
- **Wisp kit**: the handoff says "slow mana regen", but there is no mana in the code (spells run on cooldowns), so this
  uses `spellCd`. If mana arrives later, swap it for about +6% mana regen.
- **Glow-moth**: `secretSense` makes hidden doors, gnome doors and springs within range shimmer (`glitter` + a soft chime),
  and they show through walls on the minimap if there is one. The pet doesn't open anything. You still find it.
- **Lantern-fox**: `riftWarn` adds a toast with a direction arrow before the normal rift warning ("{name}'s tail flares
  red: a rift, that way."). `riftMarkMul` scales Rift Marks only, not realm merit.
- **Night light**: each pet's glow is a light zone at night (add `{src: 'pet'}` in `glow.zones()`). The radii are smaller than a
  lantern's (1.6-2.2 m), so dark-hour zones and cold-fire braziers still matter.

### 6.4 Bond, biscuits and adopting more

- **Bond: 3 hearts.** Bond 1 when you adopt. Feed a **Den biscuit** (one counts per in-game day): 3 fed days = bond 2,
  7 fed days = bond 3. Bond 3 uses the aura's `bond3` values. Bond never drops.
- **Adopting the other starters:** the two you didn't pick stay at the Den. Requirements: **Order of the Hearth Friend**
  (150 Hearth Tokens) and a **40-gold donation** each. The quest has to be finished first.
- **Later pets:** realm pets (snow hare, moss-pup, ember salamander, glowfish orb, gloam raven, Tick the clockwork owl)
  arrive at the Den through their own realm quests and are swapped here too. Each will need its own entry in `PETS`.

**Pet sources (reward table)**

| Pet | How you get it | Cost | Doc |
|---|---|---|---|
| Wisp kit / glow-moth / lantern-fox (pick one) | *Strays of the Rift* reward | free | this file, section 4 |
| The other two starters | adopt at the Den after the quest | Hearth **Friend** + 40 gold each | section 6.4 |
| **Moss-pup** | *The Rotwood Hollow* done on the **befriend** path (Vanaheim). Tobble sends it to the Den: `S.pets.mosspup = {name: "Moss-pup", bond: 1, atDen: 1}` | free, no rank needed (it's a gift) | section 6.6, `verdant_heart.md` 6.7 |
| Snow hare, ember salamander, glowfish orb, gloam raven, Tick | their realm quests (later docs) | — | — |

### 6.5 `ITEMS` entry

```js
denbiscuit: { name: "Den biscuit", px: "denbiscuit",
              about: "Signe's oat-and-moonpetal biscuit. Feed your pet once a day: bond grows, and its glow doubles for 60 s." },
```

Shop: add `den: { name: "The Stray Den", keeper: "Signe Larkspur", goods: ["denbiscuit"], sellMul: 1 }` with
`denbiscuit` priced at **6 gold** in `shop.js`'s goods table.

### 6.6 Realm pet: the Moss-pup (Vanaheim, befriend)

**Flavour:** *"Moss-pups grow in the shade of Mossbrook's giant toadstools, curled up like green buns until a gnome
whistles them awake. They can smell water through solid stone, and they never stop wagging."*

**Look:** about 14x11 px on the ground. A round puppy-shaped body of soft green moss with stubby root legs, floppy leaf ears
and a little **red white-spotted toadstool** sprouting on its head. At night its moss freckles glow **cold blue** one by one
(emissive pixels), and the toadstool cap glows faint red. It trots at your heel and sits when you stop. Well under half the
player's height.

**Aura: Forager's Nose.** Hidden springs shimmer within 5 m. A spring's spring-fizz buff lasts 15 s longer. Moonpetals, red caps and
garden harvests have a 25% chance of +1. At bond 3: 7 m, +20 s, 35%. (New mod keys: `springSense`, `springBuff` and `forage`.
`springBuff` adds seconds to `SPRING.buff` in `hollows.js`.)

`PETS` entry (in the format the build's `pets.js` now uses):

```js
mosspup: {
  name: "Moss-pup", species: "moss-pup", role: "pet_mosspup", glow: "#5ab4f0",   // cold-blue moss freckles; red cap accent #ff4a3a
  hover: { lift: 0, bob: 0, hz: 0 },
  light: { color: "#5ab4f0", intensity: 2.8, range: 2.4, lift: 0.4, pulse: [0.8, 1.05, 0.7], r: 1.5 },
  fx: { aura: "pet_aura_moss", pool: "pet_pool_moss", parts: "pet_moss_spore" },
  aura: { id: "foragers_nose", name: "Forager's Nose", desc: "Hidden springs shimmer within 5 m. Spring-fizz +15 s. Forage +1 (25%). Bond 3: 7 m, +20 s, 35%.",
          mods: { springSense: 5, springBuff: 15, forage: 0.25 }, bond3: { springSense: 7, springBuff: 20, forage: 0.35 } },
  about: "A puppy of soft green moss with root legs and a red toadstool on its head. Smells water through stone.",
  names: ["Sprout", "Clover", "Bramble", "Truffle", "Fernly", "Burdock", "Tuft", "Pebble", "Chanterelle", "Mossy"],
  gift: "vanaheim",   // not in the Den's adopt list; it arrives via S.pets.mosspup.atDen
},
```

Names avoid Pudding, Biscuit, Pip, Pipkin and Tobble.

**Signe when it arrives** (the first Den visit with `S.pets.mosspup.atDen` set, before the normal rotating line):

```js
pages: [
  "A gnome in a toadstool hat dropped this one off. Said it's from Mossbrook, with love and mud. Mostly mud.",
  "It's yours. Gifts aren't mine to keep, more's the pity. It's already dug up my carrots.",
],
then: (G) => { G.S.pets.mosspup.atDen = 0; /* offer the swap / naming: reuse denSwap + the pet_name choice */ },
```

Signe's later line (rotation, if you own the moss-pup): `"Your moss-pup found a spring under my floor. I have a pond in my kitchen now. Thank you."`
On the conquer path the moss-pup never arrives. Signe, once: `"Mossbrook's sent no pups this season. Can't think why."`

---

## 7. Pet barks

Barks are short narration lines in parentheses. Pets don't talk. Show them as a small pop text over the pet, or in the
parchment hint line, at most one every 25-40 s, and never during dialogue or combat (except the combat bark, once per fight).
`{name}` = the pet's name.

### 7.1 Wisp kit

| Trigger | Lines |
|---|---|
| follow | `(*fzzt*)` · `({name} hums a little blue tune.)` · `({name} bobs ahead, then waits for you.)` · `({name} circles your head twice, pleased.)` |
| idle (you stand still 8 s) | `({name} dozes in your hood, glowing softly.)` · `({name} chases a firefly, and loses.)` · `({name} sits on your boot like a tiny cold campfire.)` |
| night | `({name} burns brighter. The dark leans back.)` · `({name} pulses blue, slow as a heartbeat.)` |
| near an unlit brazier or lantern | `({name} tugs toward the cold brazier. Light it?)` |
| near a hidden spring | `({name} fizzes in time with the bubbles.)` |
| combat (once) | `({name} flares bright and ducks behind you, still glowing bravely.)` |
| fed a biscuit | `({name} swallows the biscuit whole and glows twice as blue.)` |
| bond up | `({name} glows the exact blue of your lantern on Lantern Eve.)` |
| faint (E4.1 carry) | `{name} glows over you until the dark turns warm, and you wake by a waystone.` |

### 7.2 Glow-moth

| Trigger | Lines |
|---|---|
| follow | `({name} flutters a lazy figure-eight.)` · `({name} lands on your shoulder, then thinks better of it.)` · `({name} drifts after a lamp, then back to you.)` |
| idle | `({name} grooms its antennae, very seriously.)` · `({name} sits on a lamp and blocks it, smugly.)` · `({name} naps on your hat. You didn't ask.)` |
| night | `({name}'s eyespots glow violet. Two more eyes in the dark, but friendly ones.)` |
| secret in range | `({name} beats its wings at a blank wall. A hidden door?)` · `({name} dusts the ground. Something fizzes below.)` · `({name} hovers at a mushroom stem. Tiny door, tiny knock?)` |
| combat (once) | `({name} spirals up out of reach, sprinkling violet sparks.)` |
| fed a biscuit | `({name} nibbles the edges first, like a proper moth.)` |
| bond up | `({name} lands on your hand and stays there.)` |
| faint (E4.1 carry) | `{name} dusts a violet path home, and you wake by a waystone.` |

### 7.3 Lantern-fox

| Trigger | Lines |
|---|---|
| follow | `({name} trots at your heel, tail-lantern swinging.)` · `({name} sniffs a puddle and sneezes.)` · `({name} races ahead, then pretends it wasn't racing.)` |
| idle | `({name} curls up with its tail-lantern for a pillow. The fish keeps swimming.)` · `({name} pounces on your shadow.)` |
| night | `({name}'s light-fish swims faster in the dark.)` · `({name} yips at the Rift's glow, then at you.)` |
| rift sensed (`riftWarn`) | `({name}'s ears go flat and its tail flares red. A rift, that way!)` · `({name} points its nose. Something's tearing open over there.)` |
| combat (once) | `({name} yips and darts between your boots.)` |
| fed a biscuit | `({name} buries half the biscuit for later. You saw where.)` |
| bond up | `({name} sleeps with its nose on your boot now.)` |
| faint (E4.1 carry) | `{name} tugs your sleeve all the way to a waystone. Fox kits are stronger than they look.` |

### 7.4 Shared barks (any pet)

- Arriving at Bifrost: `({name} perks up. It knows this bridge.)`
- Resting at an inn: `({name} claims the warm side of the pillow.)`
- Swapped in at the Den: `({name} shakes off the basket straw and falls in beside you.)`
- Near Pudding in Hearthmoor: `(Pudding and {name} regard each other. A truce is reached.)`

### 7.5 Moss-pup

| Trigger | Lines |
|---|---|
| follow | `({name} trots at your heel, wagging its whole back half.)` · `({name} sniffs a stone and sneezes a puff of spores.)` |
| idle | `({name} rolls in the moss and comes up greener.)` · `({name} curls into a green bun and snores.)` |
| night | `({name}'s moss freckles light up blue, one by one.)` |
| spring / secret in range | `({name} digs at the ground, ears up. Water down there?)` · `({name} sits and stares at a wall. It hears fizzing.)` |
| forage +1 | `({name} noses out one more. Good pup.)` |
| combat (once) | `({name} hides under your cloak, growling bravely.)` |
| fed a biscuit | `({name} chews the biscuit slowly. A tiny mushroom pops up on its head.)` |
| bond up | `({name} grows a second toadstool, just for you.)` |
| in Vanaheim | `({name} bounces in circles. Home smells!)` |
| faint (E4.1 carry) | `{name} drags you home by the sleeve, leaving a little trail of moss.` |

---

## 8. Save shape and hooks (summary for the builder)

| Key | Shape |
|---|---|
| `S.quests.strays` | 0-3 (3 = done; sub-progress in `den_riftOpen`, `den_rift`, `den_seed`) |
| `S.pet` | `{ id: "wispkit", name: "Pip", bond: 1 }` or `null` |
| `S.pets` | `{ wispkit: { name: "Pip", bond: 1, fed: 3, lastFed: <day> } }` (owned pets; `mosspup` may carry `atDen: 1` until collected) |
| `S.met.signe` | first meeting |
| `S.found.den_l1..3` | yard lanterns lit |
| `S.flags.den_rift`, `S.flags.den_dark`, `S.flags.den` | rift sealed, shutters drawn, Den unlocked |
| merit | 40 Hearth Tokens through `onErrand()` at stage 3 (no new `MERIT` key) |

The pet actor uses the cat's follow behaviour (`behavior: 'follow'`, speed ~2.4, wisp and moth float with a bob). Its aura mods
are added like gear mods while it is active. One pet at a time.

---

## 9. Conflicts and notes for the lead / Bill

1. **First pet: settled (lead, 2026-10-05).** The Stray Den adoption **is the first pet**. *Parked later option (not an open
   decision):* if the E1.2 beat 8 lantern moth from Grandpa Alder is ever built, the moth flies off toward the Rift on Lantern
   Eve and turns up at the Den as a free 4th starter ("This one asked for you by name. Well. By smell.").
2. **Stage 3 = done is hard-coded** (`G.setQuest` gives the toast, XP and `onErrand()`, and `drawLog` adds the ✓), so this quest
   uses stages 1-2 with flags and 3 = done. `errandsDone()` counts every finished non-story quest toward "quests n/3", so
   tag it `side: true` and add `&& !(QUESTS[k] && (QUESTS[k].story || QUESTS[k].side))` to the filter **(approved by the lead)**. (`onErrand` still pays
   the 40 Hearth Tokens, which is intended.) *(Revised 2026-10-05: the first draft used 5 stages.)*
3. **Names.** The Stray Den list in the story file was "rift fox, lantern moth, snow hare". This doc uses the lead's trio,
   **wisp kit / glow-moth / lantern-fox**: the glow-moth is the lantern moth and the lantern-fox is a rift-fox kit. The snow
   hare stays a Jotunheim pet (Signe's Pockets hints at it).
4. **Halvard foreshadow: keep (lead, 2026-10-05).** One Signe line hints that the strays avoid Gatewright Halvard (his Act 3
   betrayal). It only shows after your first realm is resolved, and it stays subtle.
5. **Currency naming.** "Hearth merit" in the brief = **Hearth Tokens** (faction id `hearth`) in `factions.js`.
