# The Forge Quarter and the Glowfrog Still

Story design doc, file 5 of 6 for Hearthmoor (staging, 2026-10-05). It covers the Forge Quarter's smiths (upgrades +1 to
+10, rune-stone rerolls, sockets), the riot beat left over from `old_temple.md`, and an alchemist with a glowing cauldron.
All shapes follow `data.js` (`ITEMS`, `QUESTS` with **3 = done**, `TALK`, `markerFor`), `loot.js` (`RARITY`, `GEMS`,
`makeItem`, `gearMods`, `socketGem`, `scrap`), `shop.js` (`SHOPS`, `GOODS`, `drinkTonic`), `garden.js` (`PLANTS`),
`hollows.js` (`SPRING`) and `progress.js` (`mods()`). The lead's calls are in the last section (all resolved, 2026-10-06).

**Build order: batch 2.** The Forge Quarter, its smiths and the Glowfrog Still are built together, after the current four
(pets, Old Temple, Vanaheim dungeons, rift storms).

Names going forward: the Mossglen mini-boss is **Glenheart, the Elder Golem** (renamed from Mossheart, lead-approved).

---

## 0. Overview

Ravenhold's **Forge Quarter** sits on the east cliff, behind the sealed district gate already placed in `ravenhold.json`
(`id: "forge"`, pos `[11.5, -11.7]`). It's a cliffside of stone workshops and chimneys. The forge mouths glow **red**, and the
quench tanks steam with **neon-blue cold fire** (the dwarven technique). At night the whole cliff glows.

- **The gate opens** after *The Cold Altar* is done (`quests.altar === 3`). On your first visit a small **riot** is still
  simmering at the gate. You calm it with the three temple clues (*Sparks in the Street*, story).
- **Tova Anvilsong**, master smith (human), runs the forge: **upgrades +1 to +10**, capped by rarity. She replaces the
  design's "Hilde Anvilsong"; the code keeps **Warden Hilde of the Hearth**. Intro quest: *The First Temper*.
- **Orri Flintcog**, a dwarf exile from Anvildeep: **socket punching** (up to 3 by rarity) and **rune-stone rerolls**. The
  frame-up tongs were **his**, stolen the night his quench tank froze in midsummer.
- **Nettle Gearwhisk**, a gnome jeweler in a chimney nook: **clears sockets** (the gem comes back), cheaper with Gnome Council
  rank, and sells rune-stones.
- **Bryony Glasswort**, alchemist, keeps **the Glowfrog Still** on the lowest terrace, where the forges' spare heat keeps her
  cauldron, **Old Gurgle**, bubbling. Her familiar **Bloop** is a neon-blue glowing frog. She brews **potions** from moonpetals,
  red toadstools and the three garden glow-plants. Intro quest: *The Cold Cauldron*.

Looks (normal clothes, waist visible):
- **Tova:** a linen shirt with rolled sleeves, brown trousers, a leather apron belted at the waist, a hammer loop, a thick copper braid.
- **Orri:** a wool tunic and trousers, leather bracers, a short beard braided with copper cogs. About half the player's height.
- **Nettle:** a gnome in a striped waistcoat and corduroy trousers, magnifier goggles, a tiny red white-spotted toadstool cap.
- **Bryony:** a blouse with rolled sleeves, a patched green skirt, a vial belt, an apron with glow-stains in blue and violet.
- **Bloop:** a fist-sized frog, cold neon blue, with violet spots that pulse in time with the cauldron. Sits on Old Gurgle's rim.

Glow (no bloom): forge mouths are red point lights. Quench tanks and Old Gurgle are neon-blue light pools. A shelf of jarred
**glowfrogs** in blue, violet and red lights the Still at night like a row of fish-orb lanterns.

---

## 1. Materials (new `ITEMS`)

```js
// forge materials
ironbit:   { name: "Iron bits", px: "ironbit", about: "Scrap iron, sorted by size. Tova's forge eats it by the bucket." },
coldsteel: { name: "Cold-steel ingot", px: "coldsteel", about: "Iron quenched in cold fire. Blue at the edges. Needed for +4 and up." },
runestone: { name: "Rune-stone", px: "runestone", about: "A dwarven rune carved in river stone. Orri uses one to reroll a gear stat." },
// alchemy ingredients
redcap:    { name: "Red toadstool", px: "redcap", about: "A red cap with white spots. Don't eat it raw. Do brew it." },
glowcap:   { name: "Red glow-cap", px: "glowcap", about: "A garden glow toadstool, warm red. It hums when stirred." },
coldpetal: { name: "Cold-fire petal", px: "coldpetal", about: "A petal from a cold-fire bloom. Chilly. Bright. Neon blue." },
glowbell:  { name: "Violet glowbell", px: "glowbell", about: "A violet glowbell flower. It rings very quietly in the dark." },
dewdrop:   { name: "Glow-dew", px: "dewdrop", about: "Dew from Bloop's lily pad. It glows faintly blue. Bloop seems proud." },
springwater: { name: "Spring water", px: "springwater", about: "A stoppered vial of hidden-spring water. Still fizzing." },
```

### 1.1 Sources

| Material | Where from |
|---|---|
| Iron bits | **Scrap** gear at Tova's forge: Common 1, Uncommon 2, Rare 3, Epic 4, Legendary 6 (plus the usual scrap gold). Tova sells them at 6 g |
| Cold-steel | Tova **smelts** 4 iron bits + 1 frost core → 2 cold-steel (forge tab). Major rifts 30%, abyssal rifts always 2, Glenheart 2. Orri sells it at 45 g |
| Rune-stone | Nettle sells it at 40 g (Gnome Council Friend 30 g). Major rifts 25%, abyssal rifts always, rares 20%, Gnome secrets and riddles 1 |
| Red toadstool | **Regrowing patches** (`scene.game.pickups` with `regrow: 1`, `item: "redcap"`): 2 beside each garden (Bakery Lane's plot by the lamp post, the Hollows garden), plus 2 wild ones in the Hollows and 2 in Mossglen. They regrow every in-game day (section 1.2). Bryony also sells **3 a day** at 4 g |
| Moonpetal | existing Mossglen pickups (4) |
| Red glow-cap / cold-fire petal / violet glowbell | **Garden harvest**: each bloom also gives 1 of its herb, on top of today's reward (toadcap → `glowcap`, coldfire → `coldpetal`, violet → `glowbell`). The moss-pup's forage roll applies |
| Glow-dew | Bloop's lily pad gives 1 free each day (E / A at the pad). Bryony sells it at 5 g |
| Spring water | Fill a vial at any hidden spring (`game.spring`). Bryony gives 3 empty vials in the intro and sells more at 2 g (`vial`) |

`garden.js` change: `PLANTS.toadcap.herb = "glowcap"`, `coldfire.herb = "coldpetal"`, `violet.herb = "glowbell"`. In
`interact()`, after the current reward: `if (P.herb) G.give(P.herb, 1)`. Toast: `Harvested the ${P.name}: ... and 1 ${herbName}`.

### 1.2 Red toadstool regrow hook (lead-approved)

Today `pick()` in `game.js` sets `S.picked[fx] = true`, and `nearPickup` skips anything picked, so pickups never come back. A pickup
marked `regrow: 1` stores the **day** instead and comes back on the next one:

```js
// area data: scene.game.pickups
{ fx: "redcap_lane_1", item: "redcap", regrow: 1 },          // the fx is a red white-spotted toadstool sprite (glowplant-style, not glowing)
// game.js
const gone = (pk) => { const v = G.S.picked[pk.fx]; return pk.regrow ? v === (G.S.day || 0) : !!v; };
function nearPickup(ctx, d = 0.85) { for (const pk of ctx.scene.game?.pickups || []) { const f = ctx.fx[pk.fx];
  if (!f || gone(pk)) continue; if (Math.hypot(f.x - ctx.player.x, f.z - ctx.player.z) < d) return pk; } return null; }
// in pick(): G.S.picked[pk.fx] = pk.regrow ? (G.S.day || 0) : true;
// on area attach and when Garden.update() ticks S.day: re-add the fx of every regrow pickup whose picked day < S.day
```

- **Placement:** 2 patches beside the Bakery Lane garden plot (by the lamp post) and 2 beside the Hollows garden, so a garden visit
  gives seeds-to-blooms **and** fresh caps. There are also 2 wild ones in the Hollows and 2 in Mossglen.
- Toast on a regrown patch's first pick of the day: `Fresh red toadstools! They pop up again by tomorrow.`
- The moss-pup's forage roll (+1, 25% / 35%) applies to `redcap` pickups.
- Old saves: `true` values on regrow pickups count as "picked before day 0", so they regrow at once.

---

## 2. Upgrades +1 to +10 (Tova's forge)

### 2.1 Rules

- New item field `it.up` (0 by default). The **cap is set by rarity**:

| Rarity | Cap | Max multiplier on the item's own stats (7% per +) |
|---|---|---|
| Common | +2 | 1.14 × 1.0 = 1.14 (below an Uncommon's 1.4) |
| Uncommon | +4 | 1.28 × 1.4 = 1.79 (below a Rare's 1.9) |
| Rare | +6 | 1.42 × 1.9 = 2.70 (a fresh Epic is 2.6, a maxed Epic 4.06) |
| Epic | +8 | 1.56 × 2.6 = 4.06 (a fresh Legendary is 3.5, a maxed one 5.95) |
| Legendary | +10 | 1.70 × 3.5 = 5.95 |

Example: a level-1 Legendary sword (`meleeMul` 0.14) reaches 0.238 at +10 (+24% melee instead of +14%).

- Each + adds **7% to the item's own mods** (not gems). In `gearMods`: `const k = 1 + UP.per * (it.up || 0)`, and each item mod
  `v` becomes `v * k` (round `hpAdd` and `stAdd`). `it.mods` stays the base roll, so rerolls and upgrades never fight.
- Names show the level: `+3 Mossy Iron Sword`. `describe()` lists the scaled numbers. `buyPrice` × `(1 + 0.1 * up)`.
- **It never breaks and never drops a level.** +1 to +5 always succeed. From +6 up there's a chance. A failed try uses up the
  iron and cold-steel, **refunds the gold and the gem**, and adds 1 **heat** to the item (`it.heat`): +15% on the next try. It always
  succeeds at heat 3. Heat resets to 0 on a success.

### 2.2 Cost table

```js
export const UP = {
  per: 0.07, cap: [2, 4, 6, 8, 10], heatBonus: 0.15, sure: 3,
  cost: [ // index = the level you're going TO (1..10)
    null,
    { gold: 15,  iron: 2,  steel: 0, gems: [],                          chance: 1 },
    { gold: 25,  iron: 3,  steel: 0, gems: [],                          chance: 1 },
    { gold: 40,  iron: 4,  steel: 0, gems: [],                          chance: 1 },
    { gold: 60,  iron: 5,  steel: 1, gems: [],                          chance: 1 },
    { gold: 85,  iron: 6,  steel: 1, gems: [],                          chance: 1 },
    { gold: 120, iron: 6,  steel: 2, gems: [],                          chance: 0.9 },
    { gold: 160, iron: 8,  steel: 2, gems: ["frost_core"],              chance: 0.8 },   // cold-fire quench from here on
    { gold: 210, iron: 8,  steel: 3, gems: ["frost_core"],              chance: 0.7 },
    { gold: 270, iron: 10, steel: 4, gems: ["golem_core"],              chance: 0.6 },
    { gold: 350, iron: 12, steel: 5, gems: ["golem_core", "rift_shard"], chance: 0.5 },
  ],
};
```

A full Legendary +0 → +10 costs about **1,335 gold**, 64 iron bits, 18 cold-steel, 2 frost cores, 2 golem cores and 1 rift shard.
That's a late-game sink without being a wall. The first +1 in *The First Temper* is free.

### 2.3 The look

- **+1 to +6:** the item is laid on the anvil, Tova hammers 3 times, red sparks fly (pixel particles), the forge mouth flares red.
- **+7 and up: the cold-fire quench.** After the hammering, Tova plunges the piece into the quench tank. The tank flares
  **neon blue** and a column of blue steam pixels rises, with a 1 s blue point light (no bloom). On success, frost-flowers
  creep along the anvil's edge and melt.
- **Icon marks:** +7 to +9 items get a single cold-blue glint pixel on the icon's edge. **+10** gets a slow blue ember mote rising
  from the icon. A +10 weapon trails a few cold-blue sparks on its swing. The Legendary neon aura is unchanged.
- **Fail:** the tank hisses, the steam goes grey for a moment, and the piece comes out unharmed and warm.

### 2.4 Tova's lines per tier

| Going to | Success line (Tova) |
|---|---|
| +1 | `"There. Warm iron remembers being loved. It'll hold an edge for you now."` |
| +2 | `"Plus two. A good honest piece. Common steel, uncommon care."` |
| +3 | `"Plus three. Hear that ring? That's the iron saying thank you."` |
| +4 | `"Cold-steel in the fold now. Feel the weight shift? It's listening to your hand."` |
| +5 | `"Plus five. Halfway to a legend. Don't tell it. It'll get proud."` |
| +6 | `"Plus six. Steady hands, both of us. I'll have a cup of tea after that one."` |
| +7 | `"Into the quench! ...There. Cold fire took. Blue at the edges, warm at the heart."` |
| +8 | `"Plus eight. My grandmother made one plus-eight in her whole life. Now I've made two. Hm. Three."` |
| +9 | `"Plus nine. The golem core sang the whole time. I'm going to dream about that sound."` |
| +10 | `"Plus ten. Hearthforged. I'm not crying. It's the steam. Take it before I change my mind."` |

Fail lines (random): `"Hiss. The quench wasn't ready. My fault. The iron's fine, and it's warmer for trying."` ·
`"Not this time. Your gold's back in your purse. The iron and steel went into the lesson."` ·
`"Close! It wants to be better. Give it another go. It'll take next time, I promise."`

At heat 2 (the next try is certain): `"She's hot as she'll get. Next try takes, I'd stake my anvil on it."`

At cap: `"That's as far as this piece goes. A Common can't carry a Legendary's fire. Bring me something rarer."`

Can't afford: `"Short on iron. Scrap something you've outgrown, and I'll sort the bits."` ·
`"Short on gold. The forge eats coal and coal costs coin. I'll keep the fire warm for you."`

### 2.5 Forge panel (shop-style UI)

`SHOPS.forge = { name: "Anvilsong Forge", keeper: "Tova Anvilsong, master smith", goods: ["ironbit"], gear: { n: 0, rar: [] },
sellMul: 1, forge: true, tabs: ["Temper", "Smelt", "Scrap"] }`

- **Temper:** rows are your equipped gear and then your bag. Each row: `+3 Mossy Iron Sword → +4 · 60 g · 5 iron · 1 cold-steel
  · 100%`. A greyed row shows why (`at cap (Uncommon +4)` / `need 2 more iron bits`). Confirm on Enter / A:
  `Temper the Mossy Iron Sword to +4?` → `[Temper] [Not yet]`.
- **Smelt:** `4 iron bits + 1 frost core → 2 cold-steel`. Row greyed until you have them.
- **Scrap:** the same as the gear page's scrap, plus iron bits. Header: `Scrap here for gold and iron bits.`
- Panel header lines (rotating): `"The forge is hot. What are we making better today?"` · `"Bring it here. Let's see what it's made of."`

---

## 3. Rerolls (Orri's rune bench)

### 3.1 Rules

- One **rune-stone** rerolls **one** stat on a piece of gear. The new stat comes from that slot's pool (below), and its value is
  rolled from the item's own `k` (`RARITY.mul × level factor`) × 0.8 to 1.2.
- **Random** (1 rune-stone): Orri picks which stat changes. **Chosen** (2 rune-stones): you pick the stat to change and the others
  are locked.
- After the roll you see **old vs new** and choose `[Keep new]` or `[Keep old]`. The stone is used either way.
- **Rerolls per item** by rarity: Common 1, Uncommon 2, Rare 3, Epic 4, Legendary 5 (`it.rr` counts them).
- A stat already on the item can't be rolled again. Upgrades still scale the new stat.

```js
export const REROLL = {
  max: [1, 2, 3, 4, 5], cost: { random: 1, chosen: 2 },
  pool: {
    weapon:  { meleeMul: 0.04, spellMul: 0.04, summonMul: 0.05, crit: 0.01, critDmg: 0.05, drain: 0.01 },
    armor:   { hpAdd: 8, guardMul: -0.015, stAdd: 4, regen: 0.3, healMul: 0.04 },
    trinket: { crit: 0.01, stAdd: 4, summonMul: 0.05, spellCd: 0.015, stRegen: 0.04, healMul: 0.04 },
  },
};
```

`describe()` needs labels for the new keys: `critDmg` → `+N% crit damage`, `drain` → `N% life drain`, `regen` → `+N HP/s
resting`, `healMul` → `+N% healing`, `spellCd` → `-N% spell cooldown`, `stRegen` → `+N% stamina regen`. All of them are already read by
`combat.js` or `progress.js`.

### 3.2 Orri's lines

- Panel header: `"Rune bench. Pick a stat you don't love and let the stone decide. Or pay double and decide yourself."`
- Rolling: `"(Orri presses the rune-stone to the steel. It glows violet, then goes dark.)"`
- Better roll: `"Ha! The stone likes you. Don't let it go to your head. Or do. It's your head."`
- Worse roll: `"Hm. Keep the old one, I would. Stones have moods."`
- Out of rerolls: `"That piece has heard all the runes it can take. Any more and it'd start talking back."`
- No stones: `"No stone, no rune. Nettle sells them. She'll tell you she found them. She didn't."`

---

## 4. Sockets (Orri punches, Nettle clears)

### 4.1 Rules

- **Socket cap by rarity:** Common 0, Uncommon 1, Rare 2, Epic 3, Legendary 3. (Drops still roll as `rollSockets` does now:
  Rare 0 to 2, Epic 0 to 2, Legendary 2.)
- **Orri punches** a new empty socket up to the cap:

| Socket # | Cost |
|---|---|
| 1st | 50 g + 2 iron bits |
| 2nd | 120 g + 1 cold-steel |
| 3rd | 250 g + 2 cold-steel + 1 rift shard |

- Gems go in as they do now (`socketGem`, on the gear page or at Orri's bench). The existing four: golem core (+15 HP, guard -3%),
  rift shard (+6% spells, +1% crit), frost core (+12 stamina), moon opal (+8% summons).
- **5th gem:** `prism_core` (+4% spells, +4% summons, +1% crit) arrives with Alfheim. Its entry, sources and icon are in `alfheim.md` 9.7.
- **Nettle clears** a socket and the gem goes back into `S.gems`: **20 g**, Gnome Council **Friend 10 g**, **Trusted+ free**.
- **Commons never get sockets** (lead-approved): `cap[0] = 0`, and Orri's bench greys out Common rows: `Commons don't take sockets.`
- **The 3rd socket icon spot (lead-approved)**, for Epic and Legendary only. `iconCanvas` today draws sockets at `y = k ? 6 : 1`.
  Change it to a lookup by socket count, keeping the 2x2 inlays on the right edge (`x = 7`):

```js
const SOCK_Y = { 1: [1], 2: [1, 6], 3: [0, 3, 6] };          // 3 sockets: top, middle, bottom, each a 2x2 inlay
(gems || []).forEach((gm, k) => { const x = 7, y = SOCK_Y[gems.length][k]; /* the same glow ring + inlay as now */ });
```

  With 1–2 sockets the icon is unchanged. The glow-ring pixels that fall outside the 10x10 canvas are clipped.

```js
export const SOCKET = { cap: [0, 1, 2, 3, 3], punch: [
  { gold: 50, iron: 2 }, { gold: 120, steel: 1 }, { gold: 250, steel: 2, gems: ["rift_shard"] } ],
  clear: { gold: 20, friend: 10, trusted: 0 } };
export function unsocket(S, it, k) { const g = (it.gems || [])[k]; if (!g) return false;
  it.gems[k] = null; S.gems[g] = (S.gems[g] || 0) + 1; return true; }
```

### 4.2 Lines

- Orri, punching: `"(Clink. Clink. A neat round socket, rimmed with copper.) There. Room for something shiny."`
- Orri, at cap: `"Any more holes and it's a colander. Rarer steel takes more sockets. That's just the rule of iron."`
- Nettle, clearing: `"Out it pops! Not a scratch. Gnomes never scratch a gem. We scratch our heads. Different thing."`
- Nettle, gnome rank discount: `"Council friend? Half price. Council trusted? Free! I'm not soft. I'm loyal. Different thing."`
- Nettle, selling a rune-stone: `"Found it. In a river. On a shelf. In my shop. Forty gold, please."`

`SHOPS.jeweler = { name: "Gearwhisk's Nook", keeper: "Nettle Gearwhisk, gnome jeweler", goods: ["runestone"],
gems: ["frost_core", "moon_opal"], gear: { n: 0, rar: [] }, sellMul: 1, tabs: ["Buy", "Unsocket"] }` (she sells two daytime gems at
Sefa's prices).

`SHOPS.runebench = { name: "Flintcog's Rune Bench", keeper: "Orri Flintcog", goods: ["coldsteel"], gear: { n: 0, rar: [] }, sellMul: 1,
tabs: ["Sockets", "Runes"] }`

---

## 5. The riot beat: *Sparks in the Street* (story)

### 5.1 Overview

`old_temple.md` left the riot offscreen ("I'll send word to the watch before anyone burns a forge"). Word was slow. When the Forge
Quarter opens (`quests.altar === 3`), a crowd is still at its gate with torches and bad tempers. Tova stands in her forge
door with a hammer. Orri's shutters are smashed. Nettle is hiding up her chimney. You calm three loud townsfolk, each with the
clue that answers what they shout. A wrong clue just gets an eye-roll; this can't fail. Then Orri tells you whose tongs they were.

Gate `say` before `altar === 3`: `"The Forge Quarter gate. Barred. A watch notice: 'Closed. Dwarven tools found at the Temple.'"`

### 5.2 `QUESTS` entry

```js
forge_riot: {
  title: "Sparks in the Street",
  giver: "Mother Ilse Brightwater",
  story: true,
  steps: {
    1: (S) => { const n = calmed(S);
      return n < 3 ? `Calm the crowd at the Forge Quarter gate. Answer each shout with the right temple clue. ${n}/3`
                   : "Talk to Orri Flintcog, the dwarf whose shutters were smashed."; },
    2: "Talk to Orri Flintcog about the tongs.",
    3: "The crowd went home. The tongs were Orri's, stolen the night his quench froze in midsummer.",
  },
},
```

- `calmed(S)` counts `S.flags.rt_gunnar / rt_mags / rt_pell`. The quest starts on entering the Forge Quarter (no giver talk);
  the giver field credits Ilse's word to the watch.
- Stage 1 → 2 when calmed reaches 3. Stage 2 → 3 at Orri.
- Merit: **+60 Hearth Tokens** (`MERIT.riot = 60`) plus story XP.

### 5.3 Crowd lines

The three are **Gunnar Saltbeck** (fishmonger), **Old Mags** (temple candle-seller) and **Pell** (dock porter). Each TALK gives a
`choice` of the three clues; the right one sets the flag.

| Who (id) | Shout | Right clue | Calm line |
|---|---|---|---|
| Gunnar (`rioter1`) | `"Dwarf tongs at our altar! Who else in Ravenhold owns dwarf tongs? Eh?"` | tongs | `"...Frost on forge tools. Never warmed. Huh. No smith leaves cold tongs. I'm going home."` |
| Mags (`rioter2`) | `"Someone walked into my temple and straight back out to these forges!"` | prints | `"The prints walked away from the forges? Into the court? Then who was it? ...I need a candle."` |
| Pell (`rioter3`) | `"And who snuffs a holy flame? A smith, with a smith's snuffer, that's who!"` | snuffer | `"No maker's mark? Everything up here's marked. Twice. Right. Sorry, Tova. Sorry, everyone."` |

- Clue options: `"Show the frosted tongs."` · `"Describe the frost footprints."` · `"Show the snuffer with no mark."`
- Wrong clue (any): `"That's not what I asked, is it? Don't you change the subject on me."` (no penalty, the choice reopens)
- Seer extra option (on any rioter, once): `"(Read the frame aloud.)"` calms that rioter straight away:
  `"Your runes say it's a setup. You say it with a straight face. ...Fine. Fine!"`
- Cinderknight variant on Gunnar's first shout: `"And YOU. Fire-blood. Bet you know all about forges, eh?"` (same choice after)
- **Sergeant Holt** of the city watch (`sergeant`), after 3: `"About time someone used words. Clear off, all of you. Gate's open."`
- Tova, after the crowd leaves: `"I've had that hammer up so long my arm's asleep. Thank you. Go see Orri. He's taking it hard."`

### 5.4 Orri: the tongs (stage 2)

```js
pages: [
  "Those tongs had my mark on the grip. Two crossed cogs. My grandfather's mark.",
  "They went missing the night my quench tank froze solid. In midsummer. Ice an inch thick on cold fire.",
  "Cold fire doesn't freeze. I've told the watch twice. They wrote it down and looked at me funny.",
  "Someone with very cold hands wanted Ravenhold to hate dwarves. You stopped them. I owe you a socket.",
],
then: (G) => { G.setQuest("forge_riot", 3); G.factions.add("hearth", MERIT.riot, "riot"); G.S.flags.forge_open = 1;
               G.S.flags.orri_socket = 1; /* the 1st socket punch is free */ },
```

Seer extra page: `"(The frost he describes hums in your runes, the same echo you felt on the tongs.)"`

After this, the forge, rune bench, jeweler and Still open, and Tova offers *The First Temper*.

**Later hooks (not written here):** *Tova's Masterwork* (the E6.2 "Hilde's Masterwork" ripple, renamed). *Stolen Quench* (the
Breaker ripple): if you take it, the quench tanks go dark, and **+7 and above are unavailable** until Act 3.

---

## 6. Smith intro: *The First Temper* (side)

### 6.1 `QUESTS` entry

```js
temper: {
  title: "The First Temper",
  giver: "Tova Anvilsong",
  side: true,
  steps: {
    1: (S) => { const F = S.flags || {};
      if (!F.tp_scrap) return "Scrap one piece of gear at Tova's forge (Scrap tab) for iron bits.";
      if (!F.tp_bellows) return `Work the forge bellows (E / A) until the fire roars. ${F.tp_pumps || 0}/3`;
      if (!F.tp_up) return "Temper any piece of gear to +1 at the forge (Temper tab). The first one's free.";
      return "Show Orri Flintcog your tempered gear."; },
    2: "Show Orri Flintcog your tempered gear.",
    3: "Tova's forge, Orri's bench and Nettle's nook are all open to you now.",
  },
},
```

Stage 1 → 2 when `tp_up` is set (in the same `then`). Stage 2 → 3 at Orri. The completion pays the normal side-quest +40 Hearth Tokens
(`onErrand`). Reward: 6 iron bits and 1 rune-stone.

### 6.2 Lines

Tova, offer:
```js
pages: [
  "Tova Anvilsong. Six generations of us on this cliff. The Hilde in the Plaza? No relation. Thank goodness.",
  "You've got gear. Gear wants to be better. Scrap one thing you've outgrown, and we'll feed the bits to the fire.",
],
then: (G) => G.setQuest("temper", 1),
```
- Bellows look (each pump): `(Whoomph. The forge mouth flares red.)` · 3rd pump: `(The fire roars. Tova whistles, impressed.)`
- Tova after +1: `"There. Your first temper. Now go show Orri. He gets grumpy if he's not the second to know."`
- Orri, turn-in: `"Plus one. Clean work. Here's a rune-stone for luck. Every smith needs one they never use."`
- Cinderknight, first talk: `"Fire-blood? Good. The forge likes you better than it likes me. Stand back anyway."`

### 6.3 Tova's other lines

- Hub idle (rotating): `"Ravenhold's forges never go cold. Well. Once. We don't talk about Tuesday."` ·
  `"Iron's honest. People, less so. That's why I talk to iron."` · `"Bring me Legendary steel one day. I want to see +10 before I retire."`
- Night: `"The cliff glows at night. Sailors steer by us. We've never once charged them for it."`
- Rift storm (`F.storm`): `"Storm nights, the quench tanks hum. I don't temper on storm nights. Superstition. And sense."`

---

## 7. The alchemist: Bryony Glasswort and the Glowfrog Still

### 7.1 The shop

- On the lowest Forge terrace, under the chimneys. It's a round stone room with a copper cauldron (**Old Gurgle**) over a forge-heat
  vent. The brew inside glows whatever colour the last ingredient was: neon blue, violet or red. A shelf of corked jars holds
  **glowfrogs** that light up one by one at dusk. A fish-orb lantern hangs over the door.
- **Bloop** sits on the cauldron rim, pulsing violet spots. Bloop's **lily pad** (a water barrel with a pad) gives 1 glow-dew a day.
- `SHOPS.still = { name: "The Glowfrog Still", keeper: "Bryony Glasswort, alchemist", goods: ["dewdrop", "vial", "redcap"],
  stock: { redcap: 3 }, gear: { n: 0, rar: [] }, sellMul: 1, still: true, tabs: ["Brew", "Recipes", "Buy"] }`.
  `GOODS` prices: glow-dew **5 g**, vial **2 g**, red toadstool **4 g**. Red toadstools are limited to **3 per in-game day**
  (`stock`, reset when `S.day` changes; `S.stillStock = { day, redcap }`). Sold out: `"Out of caps till tomorrow. The patches by the gardens regrow overnight."`
- **The Still is built in the Forge Quarter, together with the forge** (lead-approved), in the same batch.
- New item `vial: { name: "Empty vial", px: "vial", about: "Fill it at a hidden spring." }`.

### 7.2 Potions

**Buff rules:**
- Instant heals use `C.heal(n, true)`, like `drinkTonic`.
- Timed brews set `S.brew = { id, left }` (seconds of real play, ticked in the update loop like the spring's `buffT`). They
  add their `mods` in `progress.mods()`: `return brewMods(S, petMods(S, gearMods(S, m)))`. `brewMods` clamps `guardMul` at 0.4, like `gearMods`. **One timed brew at a time**: a new one
  replaces the old (toast: `The Violet Hush fades as the Cold-fire Tonic takes hold.`).
- Brews stack with the spring-fizz (+15% damage, 60 s) and Lantern glow. The scale stays near spring-fizz's: about +15% on one
  thing, for 60 to 180 s.

```js
export const BREWS = {
  glowcap:  { name: "Glowcap Draught",   col: "#ff4a3a", heal: 120, yield: 2,
              about: "Heals 120 HP. Twice a tonic, half the taste." },
  coldfire: { name: "Cold-fire Tonic",   col: "#5ab4f0", t: 90,  mods: { spellMul: 0.15, spellCd: 0.10 },
              about: "90 s: spells +15%, spell cooldowns 10% shorter. Glows neon blue." },
  hush:     { name: "Violet Hush",       col: "#a45cf0", t: 120, mods: { guardMul: -0.10, hpAdd: 20 },
              about: "120 s: +20 HP, guarded hits do 10% less." },
  ember:    { name: "Ember Cap Brew",    col: "#e0302a", t: 60,  mods: { meleeMul: 0.15, critDmg: 0.20 },
              about: "60 s: melee +15%, crits hit 20% harder." },
  frogleap: { name: "Frogleap Fizz",     col: "#5af0c8", t: 90,  yield: 2, mods: { stAdd: 25, stRegen: 0.30, rollSpeed: 0.10 },
              about: "90 s: +25 stamina, stamina refills 30% faster, dodge 10% farther. Ribbit." },
  moonmilk: { name: "Moonmilk",          col: "#fff8e6", t: 180, heal: 30, yield: 2, mods: { regen: 2, healMul: 0.25 },
              about: "Heals 30. 180 s: 2 HP/s resting, healing +25%. Tastes like a nap." },
  wisp:     { name: "Wisplight Elixir",  col: "#7c8cff", t: 120, mods: { summonMul: 0.20, summonLife: 4 },
              about: "120 s: summons +20% and last 4 s longer. Tiny wisps orbit the bottle." },
  luckytoad:{ name: "Lucky Toad",        col: "#f2c24a", t: 120, mods: { crit: 0.06 },
              about: "120 s: +6% crit. The bottle has a frog face. It winks." },
  riftbrew: { name: "Riftbrew",          col: "#c03cc8", t: 120, mods: { spellMul: 0.20, crit: 0.03, riftMarkMul: 0.10 },
              about: "120 s: spells +20%, +3% crit, +10% Rift Marks. Fizzes violet and red." },
  breadbroth:{ name: "Warm Bread Broth", col: "#f2a63a", heal: 60, t: 60, secret: true, mods: { stRegen: 0.20 },
              about: "Heals 60. 60 s: stamina refills 20% faster. Marla would be appalled. Then ask for the recipe." },
};
```

### 7.3 Recipes

A recipe is 2 or 3 ingredients in the cauldron; the order doesn't matter. Key = sorted ids joined with `+`.
**Cheap brews make 2 potions, all others make 1** (lead-approved; `BREWS[id].yield`, default 1). Cheap means no garden herb and no gem:
everything in it is a free daily pickup, a 2–5 g shop item, or spring water.

| Brew | Ingredients | Yield | How you learn it |
|---|---|---|---|
| Glowcap Draught | red toadstool + glow-dew | **2 (cheap)** | the intro quest |
| Moonmilk | 2 moonpetal + moonpetal tea | **2 (cheap)** | the intro quest |
| Frogleap Fizz | spring water + glow-dew | **2 (cheap)** | experiment, or the hint from Bloop (after 3 brews) |
| Cold-fire Tonic | cold-fire petal + glow-dew | 1 | experiment, or the hint from Ida |
| Violet Hush | violet glowbell + moonpetal | 1 | experiment, or the hint from Wren |
| Ember Cap Brew | red glow-cap + red toadstool | 1 | experiment, or the hint from Pipkin |
| Wisplight Elixir | moonpetal + violet glowbell + cold-fire petal | 1 | experiment, or the hint from Sorrel |
| Lucky Toad | red toadstool + red glow-cap + moon opal | 1 | experiment, or the hint from Nettle |
| Riftbrew | rift shard + cold-fire petal + spring water | 1 | experiment, or the hint from Halvard (Rift Marks Friend) |
| Warm Bread Broth (secret) | Hearthloaf + moonpetal + glow-dew | 1 | experiment only. The first brew pays a Gnome Council **secret** (below) |

```js
export const RECIPES = {
  "dewdrop+redcap": "glowcap", "moonpetal+moonpetal+tea": "moonmilk", "coldpetal+dewdrop": "coldfire",
  "glowbell+moonpetal": "hush", "glowcap+redcap": "ember", "dewdrop+springwater": "frogleap",
  "coldpetal+glowbell+moonpetal": "wisp", "glowcap+moon_opal+redcap": "luckytoad",
  "coldpetal+rift_shard+springwater": "riftbrew", "dewdrop+loaf+moonpetal": "breadbroth",
};
export const recipeKey = (ids) => ids.slice().sort().join("+");
```

Gems used as ingredients come out of `S.gems`. Everything else comes out of `S.inv`.

```js
// alchemy.js: one stir
export function brew(G, ids) {
  const S = G.S, id = RECIPES[recipeKey(ids)]; if (!id) return { fizzle: true };      // nothing used; Bryony hints
  for (const x of ids) { if (GEMS[x]) S.gems[x] -= 1; else G.take(x, 1); }
  const B = BREWS[id], n = B.yield || 1, isNew = !(S.recipes = S.recipes || {})[id];
  G.give(`brew_${id}`, n); S.recipes[id] = 1;
  if (isNew && B.secret && !(S.found || {}).brew_breadbroth) {                        // Warm Bread Broth: a Gnome Council secret
    S.found = S.found || {}; S.found.brew_breadbroth = 1; G.factions.onSecret();       // +40 Gilded Acorns (MERIT.secret)
    G.toast("A secret recipe! The Gnome Council will want to hear about this one.", 2.8);
  }
  return { id, n, isNew };
}
```

Toast on a cheap brew: `${name} ×2. Old Gurgle was feeling generous.` Brewed potions are bag items `brew_<id>` (one `ITEMS` entry each,
`px: "brew_<id>"`, coloured by `BREWS[id].col`).

### 7.4 Brewing UI flow

1. Talk to Bryony → hub: `"Brew something."` / `"Buy ingredients."` / `"Chat."` (Or press E / A at Old Gurgle directly.)
2. **Brew tab:** the left list shows the ingredients you carry, with counts. The right shows the cauldron with **3 slots**.
   Enter / A / tap adds an ingredient to the next slot; X / B takes the last one out. The brew changes colour with each one.
3. **`[Stir]`** (needs 2+ slots filled): Old Gurgle bubbles for 1.5 s, glow pulses climb the room and Bloop croaks.
   - **A known or new recipe:** the ingredients are used and the potion pops out with a pixel puff in its colour. If it's new, the
     discovery banner plays (7.5).
   - **No recipe:** **nothing is used.** The brew fizzles grey and Bryony gives a hint (7.5).
4. **Recipes tab:** known recipes, each with its effect and a `[Brew again]` button that fills the slots from your bag (greyed if
   you're short). Unknown recipes show as `??? (a ${colour} brew)` once you've got a hint for them.
5. **Drinking:** potions sit in the bag beside the tonic. Tap one to drink it. The `U` / right-stick quick-drink **stays
   tonic-only** (lead-approved); potions are always drunk from the bag. Drinking shows a ring of pixels in the brew's colour around the hero and a 1 s point light. While a
   timed brew is active, a few motes in its colour drift up from the hero. The HUD shows a small brew icon with a countdown.

### 7.5 Discovery and hint lines

Discovery banner: `NEW RECIPE: ${name}`. Toast: `${name} added to your recipe book.`

| Brew | Bryony on discovery |
|---|---|
| Glowcap Draught | `"Red and dew! That's the first thing my gran taught me. Smells like a forest floor after rain."` |
| Moonmilk | `"Moonmilk. Drink it by a fire, then don't make plans. It's not a potion. It's a nap in a bottle."` |
| Cold-fire Tonic | `"Look at it glow! Cold fire in a bottle. Don't drink it too fast, your teeth will hum."` |
| Violet Hush | `"Violet Hush. Very calming. Monsters hit you and you just sort of... shrug. Gently."` |
| Ember Cap Brew | `"Two reds! That's a spicy one. Hit things with your eyebrows raised. You'll understand."` |
| Frogleap Fizz | `"Bloop! Bloop, they made your drink! (Bloop does a little hop. That's a frog's standing ovation.)"` |
| Wisplight Elixir | `"Three lights in one bottle. Your summons will feel it. They'll glow a little smug."` |
| Lucky Toad | `"A Lucky Toad! I've only seen one before, at a fair. It winked at me. I married into that family."` |
| Riftbrew | `"A rift shard in a cauldron? Bold. The Guild would approve. My eyebrows would not, but here we are."` |
| Warm Bread Broth | `"...Did you put bread in my cauldron? It worked?! Don't tell Marla. Actually do. I want her face."` |

Fizzle hints (Bryony, when nothing matches). She picks one for a recipe you haven't found and marks it as hinted:
- `"Close-ish. Old Gurgle wants something red, I think. Red and wet."` (glowcap)
- `"It's sulking. Try two reds. It loves a strong opinion."` (ember)
- `"Fizzle. Something cold, and something Bloop makes. That's all I'll say."` (coldfire)
- `"A violet bell wants a pale flower beside it. Bells get lonely."` (hush)
- `"Bubbles! Fizzy water and frog dew might be your friends. Bloop's nodding. Bloop nods at everything."` (frogleap)
- `"Three lights, I reckon. Blue, violet and pale. Like a wisp's three moods."` (wisp)
- `"Grey. Not your fault. Some brews want a gem. Opals, mostly. Toads love opals."` (luckytoad)
- If every recipe is hinted or known: `"Nothing. Old Gurgle's tired of guessing. So am I. Tea?"`

NPC hint lines (one extra page on that NPC's talk, once each, after *The Cold Cauldron* is done; sets the hint):

| NPC | Line |
|---|---|
| Ida Wickmere | `"Cold-fire petals and frog dew? Bryony tried selling me that as lamp oil. It's better as a drink."` |
| Wren | `"Glowbell and moonpetal, steeped together. My gran swore it made her unbothered. It did."` |
| Pipkin | `"Two red caps in one pot! Gnome soldiers drink it before pranks. Very brave pranks."` |
| Sorrel | `"Moonpetal, glowbell, cold-fire. The glade's three lights. Wisps gather where they grow together."` |
| Nettle | `"Toads and opals. A gnome secret. Don't tell Bryony I told you. She'll want a discount."` |
| Halvard | `"A Guild trick: shard, cold-fire, spring water. Gate Runners drink it before a long night."` |
| Bloop (after 3 brews) | `"(Bloop hops onto your spring-water vial and sits on it, very pointedly.)"` |

### 7.6 Alchemist intro: *The Cold Cauldron* (side)

**Overview:** the riot knocked a coal cart over the vent under Old Gurgle. The cauldron went cold, and Bloop fled into the Forge's quench
tank, where it's warm and blue. Bryony needs her frog, her fire and a first batch to prove the cauldron still works.

```js
cauldron: {
  title: "The Cold Cauldron",
  giver: "Bryony Glasswort",
  side: true,
  steps: {
    1: (S) => { const F = S.flags || {}, inv = S.inv || {};
      if (!F.cc_bloop) return "Find Bloop, Bryony's glowing frog. Try somewhere warm and blue in the Forge Quarter.";
      if (!F.cc_vent) return "Clear the coal from the vent under Old Gurgle (E / A), then cast a spell to light it.";
      const red = Math.min(1, inv.redcap || 0), moon = Math.min(2, inv.moonpetal || 0);
      if (red < 1 || moon < 2) return `Gather a red toadstool (Hollows) ${red}/1 and moonpetals (Mossglen) ${moon}/2.`;
      return "Bring the ingredients back to Bryony at the Glowfrog Still."; },
    2: "Brew a Glowcap Draught at Old Gurgle: red toadstool + glow-dew.",
    3: "Old Gurgle bubbles again. Bryony taught you Glowcap Draught and Moonmilk.",
  },
},
```

- Stage 1 → 2 when you talk to Bryony with everything. She gives 1 glow-dew, 3 vials and a tin of moonpetal tea, and teaches
  **Moonmilk** (`S.recipes.moonmilk = 1`).
- Stage 2 → 3 when you brew a Glowcap Draught (`S.recipes.glowcap = 1`). +40 Hearth Tokens via `onErrand`, and 30 gold.
- **Finding Bloop:** E / A at Tova's quench tank: `(A blue frog surfaces in the cold fire, blinks at you, and climbs your sleeve.)`
  Tova: `"So that's what kept humming in my tank. Take it, take it. It was judging my work."`
- **The vent** uses the Hollows brazier rule (a spell within 2.6 m lights it), with a red flare and then Old Gurgle's blue glow returning.

Bryony lines:
```js
// offer (quests.cauldron === 0, forge_open)
pages: [
  "Oh! A customer! Or a hero. Or both? I'm Bryony. This is the Glowfrog Still. It's normally much glowier.",
  "The riot tipped a coal cart over my vent. Old Gurgle's gone cold, and Bloop ran off. He hates shouting.",
  "Find my frog, light my fire, and bring me one red toadstool and two moonpetals. I'll teach you to brew. Deal?",
],
then: (G) => G.setQuest("cauldron", 1),
```
- Reminder: `["Bloop likes warm and blue. So does everyone, really. Try the forges."]`
- Stage 1 → 2: `["Bloop! And you lit the vent! And you brought... perfect. Watch. Red cap, dew, stir. Your turn."]`
- Done: `"There it is! Glowing like a lighthouse. You're a natural. Bloop agrees. Bloop is never wrong."`
- Idle (rotating): `"I keep the glowfrogs in jars because they like it. I asked. They glowed yes."` ·
  `"Everything glows if you stir it long enough. Except soup. Soup resists."` ·
  `"Don't drink two reds before bed. Learned that one the hard way."`
- Night: `"The frogs are up! Night's when the Still really shines. Literally. Mind your eyes."`
- Rift storm: `"Storm brews come out fizzier. I don't know why. I've stopped asking."`

Bloop (`frog`, talkable): `"(Bloop blinks. Bloop's spots pulse violet. Bloop says nothing, wisely.)"` · on a new recipe:
`"Rrrbit. (Bloop's whole body flashes blue. That's pride.)"`

---

## 8. `markerFor` additions

```js
const F = S.flags || {};
if (id === "rioter1" && q.forge_riot === 1 && !F.rt_gunnar) return "quest_mark";
if (id === "rioter2" && q.forge_riot === 1 && !F.rt_mags) return "quest_mark";
if (id === "rioter3" && q.forge_riot === 1 && !F.rt_pell) return "quest_mark";
if (id === "dwarfsmith" && q.forge_riot === 1 && calmed(S) >= 3) return "quest_turnin";
if (id === "dwarfsmith" && q.forge_riot === 2) return "quest_turnin";
if (id === "smith" && q.forge_riot === 3 && !q.temper) return "quest_mark";
if (id === "dwarfsmith" && q.temper === 2) return "quest_turnin";
if (id === "alchemist" && F.forge_open && !q.cauldron) return "quest_mark";
if (id === "alchemist" && q.cauldron === 1 && F.cc_bloop && F.cc_vent && (S.inv.redcap || 0) >= 1 && (S.inv.moonpetal || 0) >= 2) return "quest_turnin";
```

TALK ids: `smith` (Tova), `dwarfsmith` (Orri), `jeweler` (Nettle), `alchemist` (Bryony), `frog` (Bloop), `rioter1..3`, `sergeant` (Holt).

---

## 9. Merit, faction and save shape

- **New area** `forge` (a Ravenhold district). `REALM.forge = "hearth"` (lead-approved: Forge district rifts, rares and bosses pay
  **Hearth Tokens**; the Harbor stays `corsair`). The Still is part of the `forge` area.
- `MERIT.riot = 60` (hearth). The side quests pay the usual +40 via `onErrand`.
- Nettle's discount reads `G.factions.rank("gnome")`.

| Key | Meaning |
|---|---|
| `it.up`, `it.heat`, `it.rr` | upgrade level, failed tries since the last success, rerolls used |
| `S.flags.rt_gunnar / rt_mags / rt_pell` | rioters calmed |
| `S.flags.forge_open` | the Forge Quarter's shops are open |
| `S.flags.orri_socket` | the first socket punch is free (used up when spent) |
| `S.picked[fx]` (regrow pickups) | the in-game day it was picked (regrows when `S.day` moves on) |
| `S.stillStock` | `{ day, redcap }`: Bryony's red toadstools sold today (max 3) |
| `S.found.brew_breadbroth` | the Warm Bread Broth secret has paid out |
| `S.flags.tp_scrap / tp_pumps / tp_bellows / tp_up` | *The First Temper* progress |
| `S.flags.cc_bloop / cc_vent` | *The Cold Cauldron* progress |
| `S.recipes` | `{ glowcap: 1, moonmilk: 1, ... }` known recipes; `S.hints` `{ coldfire: 1, ... }` hinted |
| `S.brew` | `{ id, left }` the active timed brew |
| `S.dew` | the day Bloop's pad was last picked |
| `S.quests.forge_riot / temper / cauldron` | 0 to 3 |

New modules (suggested): `forge.js` (`UP`, `REROLL`, `SOCKET`, `upgrade`, `reroll`, `punch`, `unsocket`, `upScale(it)`) and
`alchemy.js` (`BREWS`, `RECIPES`, `recipeKey`, `brew(S, ids)`, `drink(G, id)`, `brewMods(S, m)`, `tick(dt)`).

---

## 10. Decisions (all resolved by the lead, 2026-10-06)

1. **The smith's name: kept.** Tova Anvilsong.
2. **Upgrade failure: kept.** +1 to +5 always succeed; +6 to +10 run from 90% down to 50%. A failure uses up the iron and cold-steel
   but refunds the gold and gems, and the 3rd failure guarantees success. Gear never breaks or drops a level.
3. **Upgrade strength: 7% per +** (section 2.1, `UP.per = 0.07`). Caps give 1.14 / 1.79 / 2.70 / 4.06 / 5.95. Note: a maxed Rare
   (2.70×) still edges a fresh Epic (2.60×) by about 4%. Staying under would need ≤ 6.1% per +. Flagged for Systems, not changed.
4. **Sockets: Commons get 0**; caps are 0 / 1 / 2 / 3 / 3. A 3rd icon spot (`SOCK_Y`) is added for Epic and Legendary (section 4.1).
5. **Batch size: cheap brews make 2** (Glowcap Draught, Moonmilk, Frogleap Fizz); all others make 1 (`yield`, section 7.3).
6. **The quick-drink key stays tonic-only.**
7. **Red toadstools regrow daily** in patches beside the gardens (plus a few wild ones), via the `regrow` pickup hook (section 1.2).
   Bryony also sells **3 a day at 4 g** (section 7.1).
8. **Bryony stays in the Forge Quarter**, built together with the Still and the forge (batch 2).
9. **Forge district merit goes to Hearth** (`REALM.forge = "hearth"`).
10. **Riftbrew stacking: kept** (up to +45% Rift Marks on a storm night with the lantern-fox).
11. **Warm Bread Broth pays a Gnome Council secret**, wired in `brew()` (`onSecret`, +40 Gilded Acorns, once, `S.found.brew_breadbroth`).
