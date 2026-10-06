# Svartalfheim: Anvildeep, the Cooling and the Clockwork Deep

Story design doc, file 7 for Hearthmoor (staging, 2026-10-06). This is the **full Svartalfheim realm arc**, written so the
Master Builder can build it straight from this file, the same way as `alfheim.md`. It covers the copper gate at Bifrost, the
cavern city of **Anvildeep** (3 areas), the befriend, conquer and contract chains, the stolen **Anvil-Heart** frame-up, the
**Clockwork Deep** dungeon room by room, **Gorrak Ironmaw** (boss, 6×), Veyra's beats, Dagna the companion, Tick the owl, the
**Forge school**, rewards and every code shape.

Shapes follow the build and `alfheim.md`: `QUESTS {title, giver, story?/side?/ripple?/bounty?, steps}` with **3 = done**,
`TALK.id(S) → {pages, then?, choice?}`, `markerFor`, `ITEMS`, `ENEMIES` / `BASES`, `GATES` (`bifrost.js`), `REALM` / `MERIT`
(`factions.js`), `weatherAt` / `KINDS` (`weather.js`), the alliance flag `S.flags.alliance.<realm>` (`data.js` `ally(S)`), and the
rival helpers from `alfheim.md` (`lockRival`, `moodUp`).

Canon used (design docs, read-only): Anvildeep the cavern forge city; the **Anvil-Heart** frame-up (stolen from Anvildeep, planted
in Stonehollow; per the lead, Stonehollow is now only the decoy trail and the Heart is hidden in the Deep); the **Clockwork Deep** (forge constructs, lightning golems); boss **Gorrak Ironmaw**, a demon forge-tyrant bound
into his armour; companion **Dagna Coalbeard** (dwarf smith); mechanical pet **Tick** (clockwork owl); legendary **Anvilsoul**
(a living forge gauntlet); the **Forge school** (rivet volley, molten armour, clockwork construct); secret hero **Tinkerforge**;
hazards **soot fall** and **tremors**; the **Forgefire Week** festival; elite **Shadowsmiths**; dark-elf assassins.

**Lead calls (2026-10-06), folded in:** Hired Hammer is kept. The mine crystals have neon tips. The Anvil-Heart is found in the Deep:
it goes home on befriend and contract, and the player takes it on conquer. Gorrak's bargain is an optional ending. The 6th gem is parked.
The Forge Quarter fallbacks are dropped (batch 2 builds it first). Decisions are in section 14, and open questions in 15.

Lead-approved conventions carried over: bosses 5–6×, rares and minis 2–3×; conquer-path merit goes to Rift Marks; `ripple` /
`side` / `bounty` are skipped by `errandsDone`; `bounty` skips the Hearth payout (half XP on repeats); everyone wears real
clothes (top, bottom, visible waist); only bosses wear plate.

---

## 0. What's already built (hook points)

| In the build | Where | Use here |
|---|---|---|
| `GATES.svartalfheim`: "The dwarves forge this key under the mountain, and only for those the Gnome Council vouches for." Key `['gnome', 2]` (Gnome Council **Trusted**, "Riddle Solver", 400 Gilded Acorns) | `bifrost.js` | *A Word from the Council* (3.1) replaces "the Guild is still cutting this key: coming soon" |
| The sealed arch: `fx: "gate_svartalfheim"`, hue `amber`, pos `[-6.6, -5.0]` | `areas/src/bifrost.json` `game.sealed` | moves into `game.portals`: rect `[-7.35, -5.4, -5.85, -4.55]`, `to: "svartalfheim"`, spawn `from_bifrost` (the same offsets as Vanaheim's) |
| Bix Coppertuft, gnome clerk of the Nine Keys Bank (`banker`); the Council's riddle drawer | `data.js` | Bix writes the Council's vouch |
| Gatewright Halvard (`gatewright`) | `data.js` | receives the key capsule (another "keys go missing" beat) |
| `ally(S)` → `S.flags.alliance` | `data.js` | adds `svartalfheim` |
| `lockRival(S, realm)`, `moodUp(S, realm)`, `S.flags.rivals`, `S.flags.realm_mood` | `alfheim.md` 9.5 (staging) | the rival logic both ways (section 1.1) |
| Brokk Emberlode (`dwarftrader`), `flags.brokk_left` | `alfheim.md` 5.9 | his grudge pays off at the gate |
| Orri Flintcog, his crossed-cog tongs, the quench that froze in midsummer | `forge_alchemy.md` 5.4 | Orri's letter, and the same night the Heart was stolen (section 4) |
| The Cold Altar: frost-rimed dwarven tongs | `old_temple.md` | the first frame against dwarves; this arc closes the loop |
| `REALM`, `MERIT`, `onBoss` / `onRare` / `onRift` pay `realm()` | `factions.js` | `REALM.svartalfheim / forge_hall / glowmines / clockdeep = "embassy"` (conquer: `gate`) |
| Rares `BASES` with `scale`; `ELEMENTS` | `rares.js` | two new bases (section 8.3) |
| `SKY` kinds; `KINDS` presets (`dust_motes`, `glow_mist`) | `weather.js` | a new `deep` sky: soot fall and tremors (section 2.6) |
| Hidden spring rule, the Hollows brazier rule (a spell within 2.6 m) | `hollows.js` | thawing frozen cogs, springs in every area |
| `PETS` shape (`role`, `glow`, `hover`, `light`, `fx`, `aura`) | `pets.js` | Tick (section 9.5) |
| `COMPANIONS` shape (Lumi) | `alfheim.md` 5.5 | Dagna (section 5.4) |
| `S.evidence.vanaheim` / `.alfheim`, `flags.veyra_revealed`, the reveal queue | `verdant_heart.md`, `alfheim.md` 6.10 | `S.evidence.svartalfheim`, and the same reveal timing |

---

## 1. Overview

**Svartalfheim** is the realm under the mountain. Its city, **Anvildeep**, is carved into one enormous cavern: terraces of stone
houses with copper roofs, chimneys threaded up into the dark, chain-bridges over a glowing chasm, and at the bottom the **Great
Forge**, a furnace as big as a hill. Two peoples share it. The **dwarves** work the forges. The **svartalfar**, the dark elves,
keep the **rune-light** (cold blue binding runes) and work the **Amethyst Mines**, where violet crystal grows like frost. It's
gloom and glow: black stone, forge-fire reds and copper, cold-blue runes, violet crystal and blue-green cave pools.

**The trouble.** Two things are wrong, and Veyra did both.
1. **The frame.** On midsummer night the **Anvil-Heart** was stolen from its vault under the Great Forge. Giant-sized, frost-rimed
   footprints lead from the empty plinth to the old ice road toward Jotunheim. Anvildeep blames the frost giants of Stonehollow
   and is forging for war. The trail is a decoy: Veyra hid the Heart, frozen in rime, in the Binding Forge's flue deep below.
   The dark elves fear they're next: frost on a lock looks a lot like their cold rune-light.
2. **The Cooling.** The Anvil-Heart did two jobs. It fed the Great Forge, and its steady beat kept the binding runes hot on
   **Gorrak Ironmaw**, a fire-demon the first smiths bound into a suit of armour nine hundred years ago. Bound, his fire has
   powered the Great Forge ever since. Without the Heart the forge is cooling, the runes are going dim, the clockwork that tends
   his prison (the **Clockwork Deep**) is running wild, and Gorrak is waking.

**Befriend path** (`alliance.svartalfheim === "befriend"`):
1. ***Trial of the Anvil.*** Strike three true blows at the Great Anvil while Dagna Coalbeard judges. **Skipped** if you
   conquered Alfheim (Anvildeep already likes you, section 1.1).
2. ***Giant Footprints.*** Prove the giants were framed: a frost-iron **boot mould** in the slag pits, prints far too shallow
   for a giant, and Sereth's rune-lens showing **rime, not rune-light**. Anvildeep stands down. The evidence points cold, and
   the Heart's trail north is a decoy.
3. ***The Banked Fire.*** Gather three **forge-cores** from the mines and the Deep's edge so Dagna can forge a **Lesser Heart**,
   a stopgap to rebind Gorrak. Dagna joins you.
4. ***The Clockwork Deep.*** Restart the Deep's three drive cogs, reach the Binding Forge, beat Gorrak and **rebind** him with the
   Lesser Heart. Optionally, Dagna strikes a bargain with him (6.7). In the flue you find the **Anvil-Heart**, frozen. Thaw it and
   bring it home to the Great Forge (6.9). Rewards: Realm Favor, Dagna, Tick, the **Forge school**, later the
   **Anvilsoul**, and Forgefire Week.

**Conquer path** (`alliance.svartalfheim === "conquer"`):
- You use the Temple tongs as your excuse: "Dwarven tools snuffed our temple." Midgard demands the **Forge-Seal**, the key to the
  Deep and the right to its treasures. ***The Forge Claim***: break the Hushed's watch posts and beat Captain Ilvar Hushblade.
- ***The Clockwork Deep*** on hard mode: no Lesser Heart, Shadowsmiths and dark-elf assassins in the pools. You beat Gorrak, and his
  unbound fire gutters out. You **take the Anvil-Heart** from the flue. The Great Forge goes out for good: **Cold Anvildeep** (section 9.7). No festival, no Dagna, no school,
  no Anvilsoul. You get gold, the Anvil-Heart, the boss Legendary and a trophy horn. Svartalfheim becomes a permanent enemy.

**Contract path** (`rivals.svartalfheim === "locked"`, i.e. you befriended Alfheim, and you don't want to conquer):
- The Thane won't ally with an elf-friend, but the Deep is still waking. ***Hired Hammer***: the Guild brokers a contract. You do
  the Deep with a hired guide (Kesh, the dark-elf mine-runner), rebind Gorrak with a Lesser Heart the Thane's smiths forged
  without you, hand the Thane the Heart, and get paid in gold and Rift Marks. No alliance, no Dagna, no school. (Lead: kept.)

**Veyra in the arc:** the frost-iron boot mould, the frozen quench on midsummer night (Orri's and Anvildeep's), a **Frost Bell**
in the Deep that rings back her voice (C5), and the between-realms beat afterwards. If the midpoint reveal has already happened
(`flags.veyra_revealed`), her lines drop the act. If Svartalfheim makes the reveal due, it waits until **after** this realm's
Veyra beat (the `alfheim.md` 6.10 rule).

### 1.1 The rival logic (Alfheim ↔ Svartalfheim)

Alfheim and Svartalfheim are a rival pair. The lock fires **at the choice**, both ways (the lead's Alfheim call, mirrored).

| You already… | Effect in Svartalfheim |
|---|---|
| **befriended Alfheim** (`rivals.svartalfheim === "locked"`) | The Thane's befriend option is greyed out: `"(Locked. You stand with Alfheim.)"`. Conquer and the contract stay open. Brokk meets you at the gate with a cold line. Orri's letter can still be delivered (it's personal), but it pays no Realm Favor |
| **conquered Alfheim** (`realm_mood.svartalfheim >= 1`) | Brokk vouches for you at the gate. *Trial of the Anvil* is **skipped** (auto-done, merit paid). The Thane opens with a warm line. Orri: `"Anvildeep's heard of you. Good things. Loud things."` |
| neither | the full choice |

| You choose here… | Effect on Alfheim |
|---|---|
| **befriend** Svartalfheim | `lockRival(G.S, "alfheim")` at the choice. Aerin's befriend option greys out: `"(Locked. You stand with Anvildeep.)"`. A light-elf in the Wisp Market sniffs and leaves (mirror of Brokk) |
| **conquer** Svartalfheim | `moodUp(G.S, "alfheim")`. In Lumenvale: Aerin's warm opener, Faelan's softer first line, and +20 Realm Favor on *A Name in Frost* (applied in `alfheim.md` 3.2 / 5.2) |

The **4-ally cap** counts `alliance` values of `"befriend"`. Svartalfheim fills the Alfheim/Svartalfheim slot, so a player can
never befriend both. `alfheim.md` now mirrors this: Aerin's choice checks `rivals.alfheim === "locked"` (applied 2026-10-06).

---

## 2. Anvildeep: areas, layout, look

### 2.1 Area list

| Area id | Name | Kind | `REALM` | Notes |
|---|---|---|---|---|
| `svartalfheim` | **Anvildeep: Copper Row** | city hub | `embassy` | arrival from Bifrost, the market, the waystone, a glow-pool grotto, Brokk, the mine lift |
| `forge_hall` | **The Great Forge** | city | `embassy` | the Thane's hall, the Great Anvil, the empty Heart Vault, the rune-wardens' gallery, the Deep's lift |
| `glowmines` | **The Amethyst Mines** | wild | `embassy` | violet crystal galleries, cave pools, mine carts, the slag pits, rifts and rares |
| `clockdeep` | **The Clockwork Deep** | dungeon | `embassy` | 9 rooms C0–C8 (section 7), boss Gorrak Ironmaw |

Conquer path: `factions.realm()` returns `gate` here once `alliance.svartalfheim === "conquer"` (add `SVART_AREAS` next to
`VANAHEIM_AREAS`). The contract path also pays `gate`: you're the Guild's hire, not Anvildeep's friend.

`SKY`: `svartalfheim, forge_hall, glowmines → "deep"`. `clockdeep` has no sky (fixed light, the clock pauses, as in the Vault).

### 2.2 Look (for Art)

- **Palette:** black basalt and soot-brown stone; **forge reds and copper** (`#e0602a`, `#c4502c`, `#f2a63a`); **cold-blue rune-light**
  (`#5ab4f0`, `#94c0dc`) in thin carved lines; **violet crystal** in the mines (`#7a4ab0` body, `#a45cf0` tips); blue-green cave
  water (`#3ac8b0`). Copper roofs gone green at the edges (`#5a9a7a`).
- **Style-lock note (lead, 2026-10-06):** the style lock limits **bloom and sprite palettes**, not environment glow. So the mine crystals
  are **neon-tipped violet**: biome amethyst bodies (`#7a4ab0`) with **neon violet tips** (`#a45cf0`, a `#c890ff` highlight pixel). The
  tips are self-lit glow material, and each cluster carries a small violet point light, so the violet pools on the cave floor and
  water. Forge fire, copper and cold-blue rune-light glow freely the same way. **No bloom** anywhere, and the character and enemy
  sprites stay palette-locked.
- **The cavern:** one huge vault of stone. You never see a ceiling, only chimney smoke rising into black, with tiny lit windows
  high up. Terraces step down to the Great Forge, which glows red from below and lights everything from underneath.
- **Houses:** squat stone, round doors, copper roofs and gutters, chimneys everywhere. Window lamps are warm orange.
- **Rune-light:** the dark elves carve cold-blue runes into doorframes, bridges and lamp-posts. They glow steadily and
  **pulse in time** with the Great Forge's beat (every 2.4 s). When the forge falters, the pulse stutters. That's the Cooling, readable.
- **Glow orbs:** rune-lamps, glass globes of cold-blue light hung on chains along every street. In the mines, wild **cave orbs**
  (pale blue-green) drift slowly between the crystals and gather around anyone standing still.
- **Bioluminescent cave pools:** in the grotto and the mines. Blue-green water with glowing moss rims, **lanternfish** (small,
  orange-lit) and **cave glowfrogs** (pale blue, translucent, they glow when they sing).
- **Violet crystal:** clusters in the mines, from fist-sized to taller than a house. The tips glow; the bodies catch rune-light.
- **Mine carts and chains:** carts on rails, chain-lifts, cog-bridges. Everything ticks.
- **Red white-spotted toadstools** grow along the cave-pool rims (Bill's signature), plus a pale glowing "ember-cap" variant.
- **Shifts, not day and night:** the clock still runs. **Day shift** (t 0.25–0.8) has the forges roaring, warm light from below and
  busy streets. **Night shift** has the forges banked to an ember glow, cold-blue rune-light dominant, quieter streets and the
  cave orbs out. Night is the moodier, glowier one.
- **The Cooling (before the Deep is done):** the Great Forge glows dimmer, the rune pulse stutters, and frost flowers sit on
  some cold forge mouths. After befriend it roars. For conquer, see 9.7.

### 2.3 `svartalfheim`: Copper Row (city hub)

A long terrace street along the cavern wall, with the chasm on one side. Suggested camera like Bifrost's
(`bounds [-11, -9.6, 11, 12]`).

| Spot | Pos (suggested) | What |
|---|---|---|
| **The Copper Gate** (portal back to Bifrost) | `[0, 10.6]` (south edge) | spawn `from_bifrost` `[0, 9.2, "up"]`. A round stone door with copper gears around its rim; the gears turn when you pass |
| Waystone | `[3.2, 8.4]` | adds `svartalfheim` to the waystone network once visited |
| **Copper Row market** | `x -9..-2, z 3..8` | stalls under copper awnings: Tansy's tinker stall (shop, Tick), Brokk's stall, a lanternfish-lamp seller (decor) |
| Brokk's stall | `[-3.0, 7.2]` | Brokk Emberlode (section 5.6) |
| **The Glowpool Grotto** | `[7.0, 3.0]` | a side cave: a cave pool with lanternfish and cave glowfrogs, toadstool rims, a bench |
| Hidden spring | behind the grotto's waterfall at `[9.2, 1.8]` | `{ secret: "cr_spring" }`, +40 Gilded Acorns, spring-fizz. Text: `Behind the falling water, a pocket of warm air and a spring that fizzes.` |
| **The chasm rail** | `x -10..10, z -2` | a copper railing over the drop. The Great Forge glows far below. Look: `"Far below, the Great Forge breathes red. It's slower than it should be."` |
| Mine lift | `[-9.4, -4.4]` | a chain cage down to `glowmines` (portal) |
| Hall stair | `[0, -8.6]` | a wide stair down to `forge_hall` (portal) |
| Kesh's cart | `[5.4, -3.0]` | Kesh the mine-runner sits on an upturned cart (section 5.7) |

### 2.4 `forge_hall`: the Great Forge

The cavern floor around the Great Forge: a hall of pillars with the furnace at the north end.

| Spot | Pos (suggested) | What |
|---|---|---|
| Stair up | `[0, 10.6]` | back to Copper Row |
| **The Great Forge** | `[0, -8.0]` (north) | the furnace mouth, 8 m wide, red glow. Cooling: a dull orange with frost flowers on the rim |
| **The Great Anvil** | `[0, -4.0]` | a black anvil the size of a cart. *Trial of the Anvil* (3.2) and the Masterwork (9.6) happen here |
| **Thane's seat** | `[-6.0, -5.0]` | Forge-Thane Ragna Copperbraid, on a stone seat beside a copper war-table |
| **The Heart Vault** | `[6.4, -6.4]` | a round vault door, open. Inside: the empty plinth, frosted footprints (`clue_prints`), a rimed lock (`clue_lock`) |
| **Rune-wardens' gallery** | `[8.0, 2.0]` | a balcony of cold-blue runes. Sereth Gloamweave and her rune-lens |
| Hushed post | `[-8.6, 4.0]` | Captain Ilvar Hushblade and two of the Hushed |
| Dagna's forge | `[-3.6, 3.0]` | a side forge, half cold; Dagna Coalbeard |
| **The Deep's lift** | `[4.0, -9.6]` | a cog-cage behind the Great Forge, locked with the **Forge-Seal**: `"A lift cage. A seal of copper and rune-light holds it shut."` |
| War forges (decor) | `x -10..-6, z -2..2` | dwarves hammering spearheads. Befriend: they switch to pots and pans after *Giant Footprints* |

### 2.5 `glowmines`: the Amethyst Mines

Galleries of violet crystal around an underground lake. It's the wild area: rifts, rares, carts and pools.

| Spot | Pos (suggested) | What |
|---|---|---|
| Lift | `[-9.4, 9.0]` | back up to Copper Row |
| **Crystal galleries** | north half | tall violet clusters with **neon-tipped** points throwing violet light pools; cave orbs drift between them. Spawns: `sootling`, `forgeconstruct` (strays), `cavegolem` |
| **The underground lake** | `[2.0, 0.0]`, r 4 | blue-green, lanternfish, a stone jetty. Night shift: cave glowfrogs sing |
| **The slag pits** | `[-7.0, -5.0]` | black slag heaps with ember cracks. `clue_mould` look point (section 4.3) |
| **Forge-core seams** (3) | `[8.0, 6.4]`, `[-4.0, 4.6]`, `[6.2, -7.0]` | *The Banked Fire*: one forge-core each (section 3.4). One is guarded |
| Cart line | `x -10..10, z 8` | a ride-able cart (E / A): a short scripted ride from the lift to the lake jetty |
| Hidden spring | in a crystal hollow at `[10.0, -2.0]` | `{ secret: "gm_spring" }`. The crystals only part when a spell hits them. Text: `The crystal rings and slides aside.` |
| Rift spots | `[4.0, 7.0]`, `[-6.0, -1.0]` | `RIFT_AREAS.glowmines` (builder places them) |
| Rare spots | `[7.4, -4.0]`, `[-8.0, 2.4]` | `RARE_AREAS.glowmines` (section 8.3) |

### 2.6 Underground weather: soot fall and tremors

Add `SKY.svartalfheim = SKY.forge_hall = SKY.glowmines = "deep"` and one new kind:
```js
// weather.js
const KINDS = { ..., sootfall: [{ preset: "soot_fall", rate: 1 }, { preset: "dust_motes", rate: 0.6 }] };
// in weatherAt():
if (sky === "deep") { const r = hash(day * 4 + Math.floor(t * 4) + 4242); return r < 0.2 ? "sootfall" : "clear"; }
```
- **Soot fall** (about 1 quarter-day in 5): a new particle preset, `soot_fall`, of slow black flakes with a few orange embers. Rune-lamps
  dim by 30%. **Soot elementals spawn**: +2 `sootling` in `glowmines`. Banner: `Soot fall. The chimneys are coughing. Keep a lamp close.`
- **Tremors** are events, not a weather kind (a small `deep.js`, like the storm effects): about every 90–180 s in the `deep` areas.
  The camera shakes 0.5 s, dust falls, and pebbles drop at 3 marked spots (1 s shadow tell, 10 damage). In `glowmines`, a tremor
  can crack a marked wall and reveal an **ore vein** (+2 `deep_brass`) or a secret, once per wall (`S.found.gm_crack1..3`).
  Before the Deep is done, tremors come twice as often (Gorrak stirring). Toast: `The mountain shivers. Something below is turning over.`
- Rift storms (`rift_storms.md`) don't reach underground. Toast in the `deep` areas during a storm: `Above, a rift storm. Down here, just a hum in the pipes.`

### 2.7 Forgefire Week (festival)

- **When:** every 7th day in Anvildeep (`S.day % 7 === 3`, day shift). It's one day long. Dwarves call it a week. Befriend only,
  after *The Clockwork Deep* is done. (It never falls on Wisp Night, `S.day % 7 === 6`.)
- **Look:** every forge open and roaring, copper bunting, sparks shot up the chimneys like fireworks, and lanternfish lamps
  floated on the underground lake. Gorrak's eyes glow in the Great Forge's mouth: he's "watching" (his bargain, 6.7).
- **What's on:** *Forgefire Week* (bounty, 3.10), a crafting contest at the Great Anvil. Tova's upgrades cost 20% less in Anvildeep's
  forges that day (`forgeDiscount = 0.8`, when Tova's system exists). Dagna judges.
- **Banner:** `Forgefire Week! Every forge in Anvildeep is open. (It's a day. Don't tell the dwarves.)`
- Conquer path: **no festival.** Banner on the 7th day: `The forges stay cold. Nobody in Anvildeep is celebrating.`

---
## 3. Quests (`QUESTS` entries)

Helpers: `SV(S) = ((S.flags || {}).alliance || {}).svartalfheim`; `F(S) = S.flags || {}`; `found(S, ids)` counts `S.found[id]`;
`locked(S) = ((S.flags || {}).rivals || {}).svartalfheim === "locked"`; `mood(S) = ((S.flags || {}).realm_mood || {}).svartalfheim || 0`.

### 3.1 A Word from the Council (story, all paths)

```js
sv_gate: {
  title: "A Word from the Council",
  giver: "Bix Coppertuft",
  story: true,
  steps: {
    1: (S) => { const f = F(S);
      if (!f.sg_vouch) return "Ask Bix Coppertuft at the Nine Keys Bank for the Gnome Council's word.";
      if (!f.sg_sent) return "Take the Council's vouch to Gatewright Halvard at Bifrost Crossing.";
      if (!f.sg_key) return "Wait for the dwarves' answer. (Sleep, or seal a rift, then see Halvard.)";
      return "Wind the copper key in Svartalfheim's gate (E / A at the copper gate)."; },
    2: "Deal with whatever came out of the gate, then tell Halvard.",
    3: "Svartalfheim's gate is open. Copper light and forge-heat spill across the Crossing.",
  },
},
```

- **Offer:** when `G.factions.rank("gnome") >= 2` (Trusted). Bix gets a new option, `"About the copper gate..."`, plus `quest_mark`.
- **Stage 1:** Bix gives `council_vouch` (`sg_vouch`). Halvard posts it through the gate's message slot (`sg_sent`, and `sg_sentDay = S.day`).
  The answer comes the next day (`S.day > sg_sentDay`) or after any rift seal (the rift hook sets `sg_riftAfter = 1` while `sg_sent` and
  not `sg_key`). Then Halvard has a **key capsule** (`sg_key`, item `copper_key`).
- **Winding the key** (E / A at the arch): the gears turn, the door rolls open, and a **runaway construct** stumbles out
  (`runaway`, 2×, section 8.2), a forge construct gone wild in the Cooling. Its death moves stage 1 → 2.
- **Stage 2 → 3** at Halvard. The arch moves from `sealed` to `portals`, and `GATES.svartalfheim`'s look stops showing.
- **Rewards:** **+40 Gilded Acorns** (`MERIT.vouch = 40`, gnome) at the vouch, **+60 Rift Marks** (`MERIT.copper = 60`, gate) at the end,
  50 gold, story XP.

### 3.2 Trial of the Anvil (story, befriend)

```js
sv_trial: {
  title: "Trial of the Anvil",
  giver: "Forge-Thane Ragna Copperbraid",
  story: true,
  steps: {
    1: (S) => { const n = (S.flags || {}).st_hits || 0;
      return n < 3 ? `Strike the Great Anvil true, three times, while Dagna judges (E / A on the glow). ${n}/3`
                   : "Hear Dagna's verdict."; },
    2: "Tell the Thane what Dagna said.",
    3: "Anvildeep will hear you out. Dagna says your arm is 'not bad, for a Midgarder'.",
  },
},
```

- **Starts** on the befriend choice. **Skipped** if `mood(S) >= 1` (you conquered Alfheim): it's set straight to 3 with the merit paid,
  and the Thane says `"Brokk's told me about you. Skip the anvil. Sit. We've real trouble."`
- **The strike** (a tiny timing beat, no fail state): a glow ring shrinks on the anvil. E / A when it's smallest. A good strike sets
  `st_hits += 1` and sparks fly. A miss gets a Dagna line and the ring resets. QA: `?anvil=auto`.
- **Rewards:** **+40 Realm Favor** (`MERIT.sv_trial`), 20 gold. Sets `flags.sv_trusted = 1`.

### 3.3 Giant Footprints (story, befriend)

```js
sv_name: {
  title: "Giant Footprints",
  giver: "Forge-Thane Ragna Copperbraid",
  story: true,
  steps: {
    1: (S) => { const f = F(S);
      if (!f.sn_prints) return "Look at the giant footprints in the Heart Vault.";
      if (!f.sn_lock) return "Ask Sereth Gloamweave to read the frost on the vault lock with her rune-lens.";
      if (!f.sn_mould) return "Search the slag pits in the Amethyst Mines. Kesh says something odd turned up there.";
      return "Bring the boot mould to Sereth's rune-lens."; },
    2: "Tell the Thane what the lens shows.",
    3: "The giants never came. Someone cold wore giant boots and laid a false trail north. The Heart is still somewhere close.",
  },
},
```

- **Starts** when *Trial of the Anvil* is done (or skipped).
- **Stage 1 sub-steps:** `sn_prints` (the vault look point, section 4.3) → `sn_lock` (Sereth's lens on the lock) → `sn_mould` (the
  slag-pit look point gives `boot_mould`) → the lens again with the mould → stage 2.
- **Stage 2 → 3** at the Thane. Sets `flags.sv_cleared = 1`, `flags.sv_decoy = 1` (the trail north was false), and
  `S.evidence.svartalfheim = "boot_mould"`. The war forges switch to pots and pans.
- **Rewards:** **+60 Realm Favor** (`MERIT.sv_name`), 40 gold. With **Orri's letter** (`orri_letter`), +20 Realm Favor (`MERIT.orri = 20`)
  and the Thane's extra line.

### 3.4 The Banked Fire (story, befriend)

```js
sv_kindle: {
  title: "The Banked Fire",
  giver: "Dagna Coalbeard",
  story: true,
  steps: {
    1: (S) => { const n = found(S, ["fc_1", "fc_2", "fc_3"]);
      return n < 3 ? `Dig three forge-cores from the Amethyst Mines' ember seams. ${n}/3`
                   : "Bring the forge-cores to Dagna's side forge."; },
    2: "Watch Dagna forge the Lesser Heart, then take it to the Thane.",
    3: "The Lesser Heart beats in a copper cage. It won't last forever, but it'll hold a demon. Dagna's coming with you.",
  },
},
```

- **Offer:** from Dagna right after *Giant Footprints*.
- **Forge-cores** (`fc_1..3`): E / A at an ember seam. Seam 1 is open. Seam 2 is behind a tremor-crack (any spell cracks it early).
  Seam 3 is guarded by a `forgeconstruct` pair and a `sparkgolem`. Each gives 1 `forge_core` and sets `S.found.fc_n`.
- **Stage 1 → 2** at Dagna with 3 cores (a short forging scene, 5.4). **2 → 3** at the Thane, who gives the **Forge-Seal**
  (`forge_seal`) and starts *The Clockwork Deep*.
- **Rewards:** **+80 Realm Favor** (`MERIT.sv_kindle`), Dagna joins (`flags.companions.dagna = 1`), item `lesser_heart`, 60 gold.

### 3.5 The Forge Claim (story, conquer)

```js
sv_take: {
  title: "The Forge Claim",
  giver: "Forge-Thane Ragna Copperbraid",
  story: true,
  steps: {
    1: (S) => { const f = F(S), n = found(S, ["fk_p1", "fk_p2", "fk_p3"]);
      if (n < 3) return `Break the Hushed's watch posts around the Great Forge. ${n}/3`;
      if (!f.fk_ilvar) return "Captain Ilvar Hushblade carries the Forge-Seal. Take it from him.";
      return "Open the Deep's lift with the Forge-Seal."; },
    2: "Open the Deep's lift with the Forge-Seal.",
    3: "The lift is yours. Below it lies the Clockwork Deep, and the fire that feeds Anvildeep.",
  },
},
```

- **Starts** on the conquer choice. **Watch posts** (`fk_p1..3`): three pairs of `hushblade` around the hall. Clearing a pair sets its flag.
- **Ilvar** is a 1.3× elite duel (`ilvar`, 8.2). He yields at 25% HP (no kill), drops `forge_seal` and sets `fk_ilvar`.
- **Stage 1 → 2** on the seal; **2 → 3** at the lift (E / A). Starts *The Clockwork Deep*.
- **Rewards:** **+60 Rift Marks** (`MERIT.forgeclaim = 60`, gate), 80 gold.

### 3.6 Hired Hammer (story, contract: Svartalfheim locked)

```js
sv_hire: {
  title: "Hired Hammer",
  giver: "Gatewright Halvard Ness",
  story: true,
  steps: {
    1: (S) => { const f = F(S);
      if (!f.sh_terms) return "Hear the Thane's terms. She won't ally with an elf-friend, but she'll pay one.";
      if (!f.sh_kesh) return "Find Kesh, the mine-runner the Thane hired as your guide, on Copper Row.";
      return "Take the Forge-Seal and the Thane's Lesser Heart down the Deep's lift."; },
    2: "Collect your pay from the Thane.",
    3: "The demon's bound and you've been paid. Anvildeep owes you nothing, and says so.",
  },
},
```

- **Starts** when you pick `"Then hire me."` at the Thane's choice while `locked(S)` (5.2). The Guild brokers it (giver: Halvard).
- `sh_terms` at the Thane gives `forge_seal` and `lesser_heart`. At `sh_kesh`, Kesh gives the `speaktube` badge and becomes the guide (overhead lines only, no follower).
- *The Clockwork Deep* runs in its befriend form (the Lesser Heart rebinds Gorrak), but Dagna isn't there and the outro is the contract one (6.7).
- **Rewards:** **+60 Rift Marks** (`MERIT.contract = 60`, gate), 250 gold, and the Deep's normal loot. No Realm Favor, no school,
  no companion, no festival. `flags.sv_resolved = "contract"`.

### 3.7 The Clockwork Deep (story, all paths)

```js
clockdeep: {
  title: "The Clockwork Deep",
  giver: "Forge-Thane Ragna Copperbraid",
  story: true,
  steps: {
    1: (S) => { const f = F(S), n = found(S, ["cd_cog1", "cd_cog2", "cd_cog3"]);
      if (n < 3) return `Restart the Deep's three drive cogs (gear puzzles). ${n}/3`;
      if (!f.cd_boss) return "Descend to the Binding Forge. Something is pulling at its chains.";
      if (!f.cd_bound && !f.cd_taken) return SV(S) === "conquer" ? "Gorrak's fire is failing. Search the Binding Forge."
                                                                 : "Set the Lesser Heart in the Binding Forge (E / A).";
      return "Something glows under the rime in the flue. Thaw it (a spell) and take it."; },
    2: (S) => SV(S) === "conquer" ? "Leave Svartalfheim with the Anvil-Heart." : "Bring the Anvil-Heart home to the Thane.",
    3: (S) => SV(S) === "conquer"
      ? "The Anvil-Heart is yours. Anvildeep's forges are going cold, one by one."
      : SV(S) === "befriend"
        ? "The Heart is home, Gorrak is bound and the Great Forge roars. Anvildeep calls you friend."
        : "Gorrak is bound again. Anvildeep paid you, and showed you the door.",
  },
},
```

- **Stage 1:** three cog rooms (C2, C4, C6), then the boss (C8). The kill sets `cd_boss`. Then E / A at the Binding Forge sets
  `cd_bound` (befriend, contract: uses `lesser_heart`) or `cd_taken` (conquer: Gorrak gutters out). Then the **frozen flue** at the
  arena's north rim: any spell within 2.6 m thaws it (the Hollows brazier rule), and E / A gives `anvil_heart` (`cd_heart`) → stage 2.
- **Stage 2 → 3:** befriend and contract at the Thane (6.9); conquer on leaving the hub for Bifrost.
- **Rewards:** section 9. `flags.sv_resolved = "befriend" | "conquer" | "contract"`. Veyra's beat plays on the next area load.

### 3.8 The Living Gauntlet (ripple, befriend)

```js
sv_soul: {
  title: "The Living Gauntlet",
  giver: "Dagna Coalbeard",
  ripple: true,
  steps: {
    1: (S) => { const n = Math.min(3, (S.inv || {}).deep_brass || 0);
      return n < 3 ? `Bring Dagna 3 deep brass from the Deep's constructs. ${n}/3` : "Bring the deep brass to Dagna."; },
    2: "Stand at the Great Forge on day shift while Gorrak breathes on the gauntlet.",
    3: "The Anvilsoul flexes on your hand. A gauntlet with a forge for a heart, and a demon's breath in it.",
  },
},
```

- **Offer:** befriend, `clockdeep === 3` and **Realm Favor Honored** (`rank("embassy") >= 3`, 800).
- **Stage 1 → 2** at Dagna with 3 `deep_brass`. **2 → 3** at the Great Forge mouth on day shift (a short scene, 6.11).
- **Reward:** the **Anvilsoul** (9.1). It's a ripple quest, so `errandsDone` skips it.

### 3.9 The Masterwork (ripple, befriend: the Tinkerforge hook)

```js
sv_master: {
  title: "The Masterwork",
  giver: "Tansy Brasswhistle",
  ripple: true,
  steps: {
    1: (S) => { const i = S.inv || {}, ok = (i.clock_spring || 0) >= 1 && (i.amethyst || 0) >= 3 && (i.coldsteel || 0) >= 2;
      return ok ? "Take the parts to the Great Anvil during Forgefire Week."
                : "Gather Tansy's parts: 1 clock spring (the Foreman), 3 amethyst, 2 cold-steel."; },
    2: "Build the Tinker's Heart at the Great Anvil, with Tansy and Dagna watching.",
    3: "You built a legendary treasure with your own hands. Somewhere, a very small engineer is very proud.",
  },
},
```

- **Offer:** befriend, `clockdeep === 3`, after you've met Tansy and own Tick.
- **Stage 2** needs Forgefire Week (`S.day % 7 === 3`). A 3-strike anvil beat (as in 3.2), then the **Tinker's Heart** (9.6).
- **Reward:** the Tinker's Heart (a Legendary trinket) and `S.unlocks.tinkerforge = 1` (the secret hero).

### 3.10 Forgefire Week (bounty, repeatable, befriend)

```js
forgefire: {
  title: "Forgefire Week",
  giver: "Dagna Coalbeard",
  side: true, bounty: true,
  steps: {
    1: (S) => { const w = S.forgefire || { strikes: 0, orders: 0 };
      return w.strikes < 3 || w.orders < 3
        ? `Win the anvil contest (3 true strikes) and fill 3 forge orders on Copper Row. strikes ${Math.min(3, w.strikes)}/3 · orders ${Math.min(3, w.orders)}/3`
        : "Show Dagna your work at the Great Anvil."; },
    2: "Show Dagna your work at the Great Anvil.",
    3: "Forgefire Week done. Your name's chalked on the contest board. Spelled wrong, but chalked.",
  },
},
```

- **Offer:** during Forgefire Week if `quests.forgefire` is 0. It resets from 3 to 0 at the next festival, and so does `S.forgefire`.
- **Forge orders:** three townsfolk on Copper Row each ask for 1 common item from your bag (any `ironbit`, `amethyst` or a Common gear piece).
  Handing one over sets `orders += 1`. The strikes are the 3.2 anvil beat.
- **Rewards:** **+40 Realm Favor** (`MERIT.forgefire`), 30 gold, 1 `deep_brass`. The first time, a cosmetic **soot-smudge** face decal.

### 3.11 Stage tables

| Quest | Stage | Done when | Flags |
|---|---|---|---|
| sv_gate | 1 | vouch, sent, key back, the runaway beaten | `sg_vouch`, `sg_sent`, `sg_key`, `sg_runaway` |
| sv_gate | 2 → 3 | talk to Halvard | sets `sv_gate_open` |
| sv_trial | 1 → 2 → 3 | 3 true strikes, Dagna, the Thane (or skipped by mood) | `st_hits`, `sv_trusted` |
| sv_name | 1 | prints, lock, mould found and read | `sn_prints`, `sn_lock`, `sn_mould`, item `boot_mould` |
| sv_name | 2 → 3 | talk to the Thane | `sv_cleared`, `sv_decoy`, `S.evidence.svartalfheim` |
| sv_kindle | 1 → 2 → 3 | 3 forge-cores, Dagna forges, the Thane | `S.found.fc_1..3`, `companions.dagna`, items `lesser_heart`, `forge_seal` |
| sv_take | 1 → 2 → 3 | 3 posts, Ilvar yields, the lift opened | `S.found.fk_p1..3`, `fk_ilvar`, item `forge_seal` |
| sv_hire | 1 → 2 → 3 | terms, Kesh, the Deep, pay | `sh_terms`, `sh_kesh` |
| clockdeep | 1 | 3 cogs, Gorrak beaten, bound or guttered, the Heart thawed | `S.found.cd_cog1..3`, `cd_boss`, `cd_bound` / `cd_taken`, `gorrak_bargain`, `cd_heart` |
| clockdeep | 2 → 3 | the Thane, or leaving (conquer) | `sv_resolved` |
| sv_soul | 1 → 2 → 3 | 3 deep brass, the forge scene | item `anvilsoul` (gear) |
| sv_master | 1 → 2 → 3 | parts, built at Forgefire | `S.unlocks.tinkerforge` |
| forgefire | 1 → 2 → 3 | 3 strikes and 3 orders, Dagna | `S.forgefire` |

### 3.12 New `MERIT` keys (the existing scale: errand 40, boss 80, abyssal rift 120)

```js
vouch: 40,                                                   // Gnome Council (gnome): the Council's word
copper: 60, forgeclaim: 60, contract: 60, deep_c: 120,       // Guild (gate): the gate; conquer claim; the contract; conquer Deep
sv_trial: 40, sv_name: 60, orri: 20, sv_kindle: 80, deep: 120,   // Realm Favor (embassy), befriend
forgefire: 40,                                               // Realm Favor, once per festival
```

Gorrak's kill also pays `onBoss` (+80) to `realm()`: embassy (befriend) or gate (conquer, contract). A full befriend run is about
**420 Realm Favor** before rifts and rares, so Embassy **Honored (800)** is in reach with one other realm.

---
## 4. The stolen Anvil-Heart (Jotunheim framed)

### 4.1 What the evidence proves

| Evidence | From | What it shows |
|---|---|---|
| **The footprints** (`clue_prints`, look point) | the Heart Vault | giant-sized, frost-rimed, 2 m long, but only **an inch deep**. A frost giant weighs more than a loaded cart |
| **The rimed lock** (`clue_lock`, Sereth's lens) | the Heart Vault door | **rime, not rune-light.** Dark-elf rune-light is cold but never leaves frost. This frost grew on the metal like it does on frost-iron |
| **Boot mould** (`boot_mould`, new) | the slag pits, Amethyst Mines | a pair of huge boot soles of **frost-iron**, worn on straps over small feet. The same cold hand as the spike, the stencil and the tongs |
| **Orri's letter** (`orri_letter`, optional) | Orri Flintcog, once *Sparks in the Street* is done | his tongs went missing the night his quench froze. The Heart went missing the same midsummer night. A personal proof, not a physical one |

Together they prove someone **small, patient and cold** wore frost-iron giant boots, picked the lock with frost and carried the
Heart up the ice road. The giants are cleared, and so are the dark elves. `S.evidence.svartalfheim = "boot_mould"` counts toward
the midpoint reveal. The trail **north to Stonehollow** is a **decoy** (`flags.sv_decoy`). The Heart never left the mountain (section 4.5).

### 4.2 Orri's letter (`orri_letter`)

Orri gives it on your next talk in the Forge Quarter once `sv_gate === 3` and `forge_riot === 3`. It doesn't need an alliance.
```js
pages: [
  "Svartalfheim's open? Then take this to the Thane. Ragna knew my grandfather. She'll know the cogs on the seal.",
  "Tell her my quench froze on midsummer night. Ice on cold fire. She'll want to hear that. I think she's heard it before.",
],
then: (G) => { G.give("orri_letter", 1); flags(G.S).orri_letter = 1; },
```
It's optional.

### 4.3 The clue scenes

**The footprints** (`clue_prints`, `{ id: "clue", name: "The Heart Vault" }`):
```js
pages: [
  "An empty plinth, still warm at the centre. Giant footprints, white with frost, lead out the back tunnel.",
  "Each print is as long as you are tall. You step into one. Your boot sinks deeper than the print does.",
],
then: (G) => { flags(G.S).sn_prints = 1; },
```
- Seer extra page: `"(Your runes recognise the cold. The same patient hand as the spike, the stencil, the tongs.)"`
- Runeguard extra page: `"(You've walked a night watch in snow. Heavy feet sink. These didn't.)"`

**Sereth's lens on the lock** (`sn_lock`):
```js
pages: [
  "Hold still. The lens doesn't like being rushed. Neither do I.",
  "(Cold-blue light pours through the lens. The lock's frost sparkles white, not blue.)",
  "There. Rune-light is cold, but it's clean. It never leaves rime. This frost grew on the metal, like on frost-iron.",
  "So it wasn't us, whatever the Hushed are muttering. And it wasn't a giant. Giants don't pick locks. They remove doors.",
],
then: (G) => { flags(G.S).sn_lock = 1; },
```

**The slag pits** (`clue_mould`, `{ id: "clue", name: "The slag pits" }`):
```js
pages: [
  "Half-buried in black slag: two huge boot soles of grey iron, with leather straps meant for much smaller feet.",
  "Frost still clings to the iron. The slag around it is warm. The frost doesn't care.",
],
then: (G) => { G.give("boot_mould", 1); flags(G.S).sn_mould = 1; G.toast("Found: frost-iron giant boots. Evidence.", 2.6); },
```
- Kesh (on the way): `"Found 'em while digging for sparkly bits. Giant shoes! With little straps! Who wears giant shoes?"`

**The mould on the lens:**
```js
pages: [
  "(The mould lies under the lens. The same white rime. The same tool marks as the lock.)",
  "Same cold hand. Someone small wore giant feet and walked our Heart out the back door.",
  "The back tunnel runs to the ice road. But these prints stop at the tunnel mouth. Nobody carried a hot Heart up a frozen road.",
  "Take this to the Thane before she finishes those spears.",
],
then: (G) => G.setQuest("sv_name", 2),
```

### 4.4 Conquer and contract paths: the evidence

- **Conquer:** *Giant Footprints* never starts, but the look points and the slag pits still work. Sereth, once, if you carry the
  mould: `"You carry proof nobody here did this. And you came for our fire anyway."` The evidence counts for the reveal.
- **Contract:** Sereth reads it with you anyway, off the books: `"The Thane won't thank you. I will. Quietly."` The war forges
  stand down, but the Thane gives no merit for it.

### 4.5 Where the Heart really is (lead, 2026-10-06)

The northbound trail was a **decoy** to start a war with Jotunheim. Veyra hid the Heart where no dwarf would look: frozen in a shell of
rime inside the **Binding Forge's flue**, so the binding would starve and Gorrak would wake. It's found after the boss (3.7, 6.7).
- **Befriend and contract:** the Heart goes home to its plinth in the Great Forge (6.9).
- **Conquer:** you take it (`anvil_heart`, the realm's key trophy).
- **Jotunheim hook:** `flags.sv_decoy = 1` lets the Jotunheim doc give the giants a grievance ("Anvildeep nearly marched on us").
  Nothing here gates on it. Thane line: `"The giants nearly ate a war for this. I owe Stonehollow a cart of ale. Two carts."`

---

## 5. NPC roster

Everyone wears normal clothes: a separate top and bottom with a visible waist (belt, sash or apron tie). No onesies, no
armour-suits. Only bosses wear plate. **Dwarves** are about half the player's height, broad, with braided beards (many dwarf
women have them too). **Dark elves** (svartalfar) are tall and slim with long ears, slate-blue or ash-grey skin, white or silver
hair, and thin **cold-blue rune tattoos** that glow faintly at night.

| Name (TALK id) | Role | Look | Where |
|---|---|---|---|
| **Forge-Thane Ragna Copperbraid** (`thane`) | Anvildeep's ruler, a dwarf smith-queen; proud, blunt, grieving the Heart | a copper-red beard in three braids with gold rings, a deep-green wool tunic with rolled sleeves, a wide leather belt with a copper buckle, brown trousers, heavy boots, a smith's hammer as a sceptre | `forge_hall`, the Thane's seat |
| **Sereth Gloamweave** (`runewarden`) | dark-elf rune-warden; reads the evidence, teaches the Forge school | slate-blue skin, white hair cut to the jaw, a high-collared charcoal blouse, a cold-blue sash, slim black trousers, soft boots, a rune-lens on a chain | `forge_hall`, the gallery |
| **Dagna Coalbeard** (`dagna`) | dwarf smith; companion (befriend) | section 5.4 | `forge_hall`, her side forge, then with you |
| **Captain Ilvar Hushblade** (`hushed`) | dark-elf captain of the Hushed (the Thane's quiet guard); the conquer duel | ash-grey skin, a silver topknot, a fitted black wrap-top, a grey sash, dark trousers bound at the shins, two short blades at his hips | `forge_hall`, Hushed post |
| **Brokk Emberlode** (`dwarftrader`) | the trader from Lumenvale; the rival-grudge payoff | a rust-coloured wool shirt, a leather apron belted over trousers, a soot-black beard with brass beads | `svartalfheim`, his stall |
| **Tansy Brasswhistle** (`tinker`) | gnome tinker; shop; Tick's maker; the Masterwork | a gnome in a mustard shirt, brown corduroy shorts with braces and a belt (waist visible), striped socks, brass goggles, a tiny red white-spotted toadstool cap | `svartalfheim`, tinker stall |
| **Kesh** (`minerunner`) | dark-elf kid, mine-runner; the cart ride; the contract guide | a too-big grey knitted jumper with the sleeves rolled, a rope belt, short brown trousers, sooty knees, a cave orb in a jar | `svartalfheim`, his cart |
| **Old Haldis** (`poolkeeper_sv`) | dwarf grandmother who tends the Glowpool Grotto's lanternfish | a white beard in one long braid, a lavender knitted cardigan over a cream blouse, a dark skirt with an apron, a fishing net | `svartalfheim`, the grotto |
| Anvildeep folk (`dw1`–`dw3`, `sv1`–`sv2`) | ambient (`say` only) | dwarves in tunics, aprons and trousers; dark elves in wrap-tops, sashes and slim trousers | everywhere |
| **Gorrak Ironmaw** (boss) | the bound fire-demon of the Great Forge | section 8.1 (plate allowed) | `clockdeep` C8 |

**Shop:** `SHOPS.tinker = { name: "Brasswhistle's Tinkery", keeper: "Tansy Brasswhistle, gnome tinker", goods: ["tonic", "runestone", "ironbit"],
gems: ["golem_core"], gear: { n: 3, rar: [1, 1, 2] }, sellMul: 1 }`. Forgefire Week adds lanternfish lamps. Conquer path: prices ×1.5 and Common
gear only.

### 5.1 Bix and Halvard: the copper gate

**Bix** (`banker`), new option `"About the copper gate..."` (Gnome Council Trusted):
```js
pages: [
  "The copper gate? Ah. The dwarves only cut that key for folk the Council speaks for. And the Council... speaks for you.",
  "(Bix stamps a tiny acorn seal onto a tiny letter.) There. The Council's word. Don't fold it. Gnomes notice folds.",
],
then: (G) => { G.give("council_vouch", 1); flags(G.S).sg_vouch = 1; G.factions.add("gnome", MERIT.vouch, "vouch"); G.setQuest("sv_gate", 1); },
```

**Halvard** (`gatewright`):
- Sending (`sg_sent`): `["A Council seal? Well, well. In the slot it goes. The dwarves answer in their own time. Usually a day."]`
- The capsule (`sg_key`):
```js
pages: [
  "Your answer came. A copper capsule, with a key inside. Clockwork. Wind it in the gate.",
  "Odd thing. The capsule's seal was opened and closed again. Neatly. I'll ask the night clerk. Keys go missing, you know.",
],
then: (G) => { G.give("copper_key", 1); flags(G.S).sg_key = 1; },
```
- Turn-in (stage 2): `["Something came out of the gate? Under the mountain's in a bad way, then. Mind yourself down there."]`
- Idle, later: `"Svartalfheim's gate ticks all night now. Like a clock. Or a bomb. I'm told it's a clock."`

### 5.2 Forge-Thane Ragna Copperbraid (`thane`)

**First audience: the choice** (`!SV(S) && !F(S).sv_contract`):
```js
pages: [
  "A Midgarder in my hall. Sit, or stand. Don't touch the anvil.",
  "Our Heart is stolen. The giants walked it out of my vault on midsummer night. My forge is cooling. My city shakes.",
  "So, Midgarder. Will you help Anvildeep, or are you here to pick our bones like everyone else?",
],
choice: { id: "alliance_svartalfheim", options: [
  { label: "I'll help. Let me find your Heart.", locked: (S) => locked(S), lockedLabel: "(Locked. You stand with Alfheim.)",
    pick: (G) => { ally(G.S).svartalfheim = "befriend"; G.toast("Svartalfheim: befriended", 2.2); lockRival(G.S, "alfheim");
      if (mood(G.S) >= 1) { G.setQuest("sv_trial", 3); G.factions.add("embassy", MERIT.sv_trial, "sv_trial"); G.setQuest("sv_name", 1); }
      else G.setQuest("sv_trial", 1);
      return { pages: ["Then prove your arm first. Dagna will judge. She judges everyone. She judged me once. I lost.",
                       "(Svartalfheim is your friend now. Its rival, Alfheim, will not stand with you as well.)"] }; } },
  { label: "Anvildeep will answer for the Temple tongs.", pick: (G) => { ally(G.S).svartalfheim = "conquer"; G.toast("Svartalfheim: conquered", 2.2);
      G.setQuest("sv_take", 1); moodUp(G.S, "alfheim");
      return { pages: ["...Tongs. You come for my fire over tongs. Then you'll meet the Hushed before you meet the Deep.",
                       "(Svartalfheim stands against you now. The dwarves will remember. They write everything down.)"] }; } },
  { label: "Then hire me.", show: (S) => locked(S), pick: (G) => { flags(G.S).sv_contract = 1; G.setQuest("sv_hire", 1);
      return { pages: ["An elf-friend, for hire. Ha. Fine. Gold's gold, and my Deep is waking.",
                       "Here's the seal, and a Lesser Heart my smiths forged. Kesh will guide you. Don't come back for tea."],
               then: (G2) => { G2.give("forge_seal", 1); G2.give("lesser_heart", 1); flags(G2.S).sh_terms = 1; } }; } },
  { label: "I'm only passing through.", cancel: true, pick: () => ({ pages: ["Then pass quickly. The floor's been known to move."] }) },
] },
```
- **New choice fields:** `locked(S)` greys an option and shows `lockedLabel` (it can't be picked). `show(S)` hides an option unless true.
  Aerin's choice in `alfheim.md` needs the same `locked` field (`rivals.alfheim === "locked"`).
- **Locked opener** (befriended Alfheim), before the pages: `"Brokk tells me you're the elves' friend. Bold, coming here."`
- **Mood opener** (conquered Alfheim): `"Brokk tells me you put the light-ears in their place. Sit. Have some ale. Then we talk."`
- Seer extra option (befriend only): `"Your vault was opened by frost, not giants. I've seen the hand."` → befriend, plus
  `"...Frost? Hm. My grandmother said the old ones had a word for folk like you. 'Annoying.' Go on."`
- Cinderknight extra page: `"Ember-blood. You'll feel the Deep before you see it. So will what's down there."`

**Giant Footprints, turn-in** (stage 2):
```js
pages: [
  "Frost-iron boots. Little straps. So my vault was robbed by someone who wanted a war.",
  "And I nearly gave them one. Put down the spears, all of you! Make pans. We'll need pans for the apology feast.",
  "And if the trail north was a lie, my Heart's still under this mountain somewhere. First, the Deep. Talk to Dagna.",
],
then: (G) => { G.setQuest("sv_name", 3); G.factions.add("embassy", MERIT.sv_name, "sv_name"); gold(G, 40);
               const f = flags(G.S); f.sv_cleared = 1; f.sv_decoy = 1;
               G.S.evidence = { ...(G.S.evidence || {}), svartalfheim: "boot_mould" };
               if ((G.S.inv || {}).orri_letter) G.factions.add("embassy", MERIT.orri, "orri");
               G.setQuest("sv_kindle", 1); },
```
- With Orri's letter, an extra page: `"Flintcog's cogs. His grandfather made my first hammer. Tell Orri he can come home. If he wants."`

**The Banked Fire, turn-in** (stage 2):
```js
pages: [
  "A Lesser Heart. Dagna, you clever, stubborn thing. It'll hold him a while.",
  "Gorrak Ironmaw. Our oldest shame. A demon the first smiths bound in iron to keep our forge lit.",
  "Without the Heart the binding cools, and he wakes. Here's the Forge-Seal. Bind him again. Don't let him talk you round.",
],
then: (G) => { G.setQuest("sv_kindle", 3); G.factions.add("embassy", MERIT.sv_kindle, "sv_kindle"); gold(G, 60);
               G.give("forge_seal", 1); G.setQuest("clockdeep", 1); },
```

**Idle lines:**

| Condition | Line |
|---|---|
| befriend, default | `"The forge breathes. When it breathes, I breathe. Simple folk, dwarves."` |
| befriend, night shift | `"Night shift. The forges banked, the runes bright. My favourite hour. Don't tell the day crew."` |
| befriend, Deep done | `"He watches the festival from the forge mouth now. Gorrak. Grumbling. I find I don't mind."` |
| befriend, Forgefire Week | `"Forgefire! Go and hit something. Not me. Something metal."` |
| conquer | `"Say it and go. The forges can't hear you. They've gone quiet."` |
| conquer, Deep done | `"You took his fire. Look around. Every cold chimney is yours."` |
| contract, done | `"You've been paid. Don't take it personally. We remember who your friends are."` |
| neutral | `"Still deciding? The mountain isn't. It shakes either way."` |

### 5.3 Sereth Gloamweave (`runewarden`)

- **First meeting:** `"Rune-warden Sereth. I keep the cold lights. Mind the lens, it bites. Not literally. Mostly."`
- **Giant Footprints offer** (stage 1, before `sn_lock`): `"The Hushed say the frost on the vault is ours. It isn't. Bring me there and I'll prove it."`
- **Mould read**: section 4.3. **School teacher**: section 9.2.

| Condition | Line |
|---|---|
| default | `"Dwarves make the fire. We make the runes that hold it. Nobody writes songs about the runes."` |
| night shift | `"The runes are brightest now. Look at the bridges. Every line of blue is one of us, keeping watch."` |
| Cooling | `"The pulse is stuttering. Feel it? Like a heart missing beats. Because it is one."` |
| befriend, Deep done | `"The pulse is steady. Two point four seconds, every beat. I counted all night. Happily."` |
| conquer | `"The runes are going out. All the ones you can see. And all the ones you can't."` |

### 5.4 Dagna Coalbeard (`dagna`, companion)

**Who she is:** a dwarf smith, Anvildeep's best and rudest. She judges the Trial, forges the Lesser Heart and comes with you to
the Deep. She's blunt, warm underneath, and treats every problem like a stubborn bit of iron.

**Look and sprite notes (for Art):** about half the player's height (a normal NPC sheet at the dwarf scale; 4-direction walk, idle,
attack, cast, hurt, sit). A **soot-black beard** in two thick braids with copper rings, ruddy cheeks, a red-brown work shirt with the
sleeves rolled to the elbow, a **leather apron tied at the waist** over grey trousers, tan steel-toed boots and leather bracers.
A big square hammer on her back, its head faintly glowing ember-orange (a small point light, `#f2a63a`). No plate.

**Trial of the Anvil** (judging):
- Good strike: `"Hm. Not bad."` · `"That one sang. Do it again."`
- Miss: `"You hit it like you owe it money."` · `"Wait for the glow. The anvil talks. Listen."`
- Verdict (stage 1 → 2): `"Three true. Your arm's not bad, for a Midgarder. Tell the Thane I said so. She won't believe it."`

**The Banked Fire** (offer, after *Giant Footprints*):
```js
pages: [
  "The Heart's lost somewhere. Fine. I can't make a new one. But I can make a little one. Enough to hold him.",
  "I need forge-cores. Three. The mines have ember seams, deep down. Bring me three and I'll do the rest.",
],
then: (G) => G.setQuest("sv_kindle", 1),
```
**Forging** (stage 1 → 2): `["(Dagna hammers the three cores into one. Sparks fly up like stars. The lump begins to beat.)",
"There. A Lesser Heart. Ugly. It works. I'm coming with you. Somebody has to hold the hammer properly."]`

**Companion data shape** (the companion system isn't built; `flags.companions.dagna = 1` marks her as recruited):
```js
export const COMPANIONS = {
  // lumi: { ... },                                            // alfheim.md 5.5
  dagna: { name: "Dagna", kind: "dwarf", talks: true, role: "companion_dagna", realm: "svartalfheim", scale: 0.5,
           follow: { dist: 1.2, speed: 2.8 },
           light: { color: "#f2a63a", intensity: 2.0, range: 1.8, lift: 0.6 },              // the glowing hammer head
           kit: {
             brawl:  { dmg: 10, reach: 1.2, cd: 1.6, knock: 0.6 },                          // she melees the nearest foe
             temper: { every: 20, life: 8, mods: { meleeMul: 0.10 } },                      // she "sharpens" your weapon: +10% melee for 8 s
             mend:   { below: 0.3, heal: 40, perFight: 1 },                                 // once a fight, a quick patch-up below 30% HP
           },
           about: "A dwarf smith. Anvildeep's best and rudest. Holds the hammer properly." },
};
```
**Combat role:** a tanky brawler. She melees, tempers your weapon every 20 s (a spark burst on your blade) and patches you up once
a fight. Suggested rule: when you faint, she sits down, grumbles, and is back at the waystone.

**Barks** (`{ id: "dagna", name: "Dagna" }`):

| Trigger | Line |
|---|---|
| follow | `"Walk where I walk. The floor here bites."` · `"Your boots are Midgard-made. I can tell. They squeak."` |
| night shift | `"Banked forges. Good. Even fire needs a nap."` |
| soot fall | `"Soot fall. Breathe through your beard. Oh. You haven't got one. Shame."` |
| tremor | `"That's him. Rolling over. Hold on to something heavy. Me."` |
| combat start | `"Right. Hammer first, questions never."` |
| Temper | `"(Dagna slaps a spark onto your blade.) There. Sharper. Don't thank me, hit something."` |
| low HP | `"You're dented! Drink something! The red one!"` |
| a hidden spring nearby | `"Warm air from that wall. Springs. Gnomes'll have hidden it. They hide everything."` |
| Bifrost | `"Nine gates and a bridge of light. Showy. Ours is a door. Doors work."` |
| Hearthmoor | `"Your village smells of bread. Where's the forge? ...That's it? That's a forge? Oh, bless."` |
| Ravenhold Forge Quarter | `"Tova's work? Hm. Good quench. Don't tell her I said. Tell Orri hello."` |
| Alfheim (if conquered) | `"Elves. All that light and not one decent hammer."` |
| the Clockwork Deep | `"My great-great-grandmother built half of this. The half that works."` |

### 5.5 Captain Ilvar Hushblade (`hushed`)

| Condition | Line |
|---|---|
| first meeting | `"Ilvar. Captain of the Hushed. We guard the Thane quietly. You're very loud."` |
| Cooling, before the evidence | `"There's frost on the vault. The dwarves are looking at us. I'd rather they looked at the giants."` |
| befriend, after *Giant Footprints* | `"Rime, not rune-light. Sereth proved it. Thank you. My people sleep easier. So do I."` |
| conquer, the duel (start) | `"The Forge-Seal stays with the Hushed. Come and take it. Quietly, if you can."` |
| conquer, yields (25% HP) | `"Enough. Take it. Whatever's in the Deep, you're the one who let it out."` |
| conquer, afterwards | `"(Ilvar doesn't look at you. None of the Hushed do. You can feel them anyway.)"` |

### 5.6 Brokk Emberlode (`dwarftrader`, the rival payoff)

Brokk meets you at the Copper Gate on your first arrival, then goes back to his stall.

| Condition | Line |
|---|---|
| arrival, befriended Alfheim | `"Well. The elf-friend. I told you Anvildeep keeps a ledger. You're in it. Page one."` |
| arrival, conquered Alfheim | `"Ha! The one who humbled Lumenvale! Come in, come in. I've told everyone. Twice."` |
| arrival, neither | `"A Midgarder. Hm. Haven't picked a side yet? Down here, everyone picks a side."` |
| befriend here | `"You're one of us now. Mind, if you ever go soft on the elves, I'll know. I'll know."` |
| conquer here | `"You came for our fire. After all I said about the elves. Don't buy anything. I'm not selling."` |
| contract | `"Paid help. Elf-friend paid help. Well, gold's gold. I'll take yours too."` |
| Forgefire Week | `"Forgefire! Best day of the week. All of it. The whole week. It's a day."` |

### 5.7 Kesh (`minerunner`)

| Condition | Line |
|---|---|
| first meeting | `"I'm Kesh! I run the carts. Well, the carts run. I hang on. Want a ride? It's free. Mostly."` |
| default | `"Cave orbs follow you if you stand still. I stood still for an hour once. I had nine."` |
| the cart ride | `"Hold on! Lean left! No, other left! Wheee!"` |
| during *Giant Footprints* | `"Something weird in the slag pits. Big iron shoes. I didn't touch them. Much."` |
| contract guide (overhead, in the Deep) | `"I've never been this deep. It ticks. Everything ticks. Even my teeth."` |
| night shift | `"Glowfrogs are singing at the lake. They only sing when the forge is quiet. Like they're shy."` |
| conquer | `"The carts don't run anymore. Nothing runs. The forge went out. Did you do that?"` |

### 5.8 Tansy Brasswhistle (`tinker`)

- First: `"Tansy Brasswhistle, tinker! Mind the owl. He's not finished. Well, he's finished. He just doesn't know it."`
- Default: `"Gnomes and dwarves built half this city together. Dwarves did the heavy bits. We did the clever bits."`
- Tick (befriend, Deep done, section 9.5): `"He's done! He's yours! Tick, say hello. (Tick says 'tick'.) He's shy."`
- Masterwork offer (3.9): `"You want to build something legendary? Of course you do. Everybody does. Here's the list."`
- Conquer: `"Prices went up. The forges are cold. Cold forges, dear prices. That's economics."`

### 5.9 Old Haldis (`poolkeeper_sv`)

| Condition | Line |
|---|---|
| first | `"Mind the lanternfish. That orange one's Ember. He's ninety. He's earned the good spot."` |
| default | `"Fish glow, frogs glow, moss glows. Down here, if you don't glow, you're furniture."` |
| night shift | `"Listen. Frogs. They sing when the forge sleeps. I come down every night to hear them."` |
| Cooling | `"The water's colder. The fish are sulking. Fix the forge, dearie. For the fish."` |
| conquer | `"The fish have stopped glowing. I didn't know they could stop. Now I do."` |

### 5.10 Anvildeep folk (ambient `say`)

- `"The giants stole our Heart! ...Or so they say. My cousin says giants can't fit through the back tunnel."` (Cooling)
- `"Soot in my porridge again. Soot in everything. Soot is the dwarf seasoning."`
- `"A Midgarder! Taller than a dwarf, shorter than an elf. Just right for doorframes, really."`
- `"Is the floor shaking or is it me? ...It's the floor. It's always the floor."`
- Dark elf: `"We light the runes, they get the songs. One day someone will write a song about a rune."`
- Dark elf (befriend, after *Giant Footprints*): `"The dwarves said sorry. Out loud. In public. I'm having it carved."`

---
## 6. Story scenes

### 6.1 Arrival in Anvildeep (first load of `svartalfheim`)

```js
pages: [
  "(The copper door rolls shut behind you. Heat on your face. The smell of coal, and something like rain on hot stone.)",
  "(A street of stone houses clings to a cavern wall. Copper roofs. Chimneys climbing into the dark.)",
  "(Far below, a furnace as big as a hill glows red. Its light breathes slowly. Too slowly.)",
  "(Cold-blue runes line every doorframe, pulsing with the forge. Every few beats, the pulse stutters.)",
],
```
Then Brokk's arrival line (5.6), by path.

### 6.2 Conquer path: the Hushed posts

When `sv_take` starts, the Hushed spread out. Toast: `The Hushed have gone quiet. That's how you know they're watching.`
Folk on Copper Row switch to conquer lines. The tinker shop's prices rise.

### 6.3 The Deep: guide lines (Dagna on befriend, Kesh on contract)

Dagna walks with you (companion). On the contract path, Kesh talks through a **speaking-tube** badge (`speaktube`, overhead text, no
follower; the same pattern as Mirelle's lens). Conquer: nobody. Hint lines play once per room.

| Room | Dagna (befriend) | Kesh (contract) |
|---|---|---|
| C0 | `"The lift. Hold the rail. If it squeals, that's normal. If it stops squealing, worry."` | `"Can you hear me? I'm in the tube! It tickles!"` |
| C1 | `"Rogue constructs. They tended the binding. Now they tend nothing. Hit the furnace belly."` | `"The steam vents puff before they blow. Count to two."` |
| C2 | `"A drive cog's jammed. Find the gap, fit the cog. Big cogs turn slow, small ones fast. Think like a clock."` | `"Gears! I love gears. I don't understand them. I love them."` |
| C3 | `"A cistern. Fish down here? Ha. Life gets in everywhere. Like soot."` | `"Lanternfish! Can you catch me one? No? Fine."` |
| C4 | `"That's the Foreman. He used to keep this line running. He still thinks he does."` | `"The belts go one way. You go the other way. That's the trick, I think."` |
| C5 | (Veyra's Frost Bell, 6.5) | (same) |
| C6 | `"Rail yard. Set the switches, send the cart, ram the gate. Dwarves love a simple plan."` | `"Carts! Finally something I know! Left switch, then... no. Right. Hang on."` |
| C7 | `"Bellows. They'll blow you off the bridge if you let them. Don't let them."` | `"Hold on to the chains when it gusts. My cousin didn't. He's fine. He's just very far away now."` |
| C8 | `"He's awake. Hammer up. When the plates open, that's our moment."` | (boss intro) |

### 6.4 The C5 reliefs (look points `relief_1..3`, `{ id: "relief", name: "A carved relief" }`)

| Relief | Text | Dagna (befriend) |
|---|---|---|
| 1 | `"Dwarves and dark elves together drag a burning giant of a demon into a cave. Half of them are on fire."` | `"The first smiths. They didn't kill him. Couldn't. So they made him useful."` |
| 2 | `"The demon, bound in plates of iron and blue runes, chained to an anvil-pillar. His fire runs up into a forge."` | `"Nine hundred years he's lit our city. Nobody asked him. That's the shame of it."` |
| 3 | `"A small dwarf girl sets a glowing heart into the demon's chest-plate. He's looking down at her, not angry. Curious."` | `"The first Heart. That's the story, anyway. My gran said he liked the girl. Said she talked back."` |

Conquer: no Dagna lines. Seer extra on relief 3: `"(The heart in the carving is beating. Carvings shouldn't do that.)"`

### 6.5 Veyra's Frost Bell (C5)

In C5 hangs the Deep's great alarm bell, crusted in white frost. E / A to strike it. It rings, and **Veyra's voice** comes back out
of the ice: she froze her words into it the night she took the Heart. Frost flowers bloom on the floor while she speaks.

**Before the midpoint reveal** (`!flags.veyra_revealed`):
```js
pages: [
  "(The bell rings. The frost on it shivers, and a woman's voice comes out of the ice, soft and tired.)",
  "Veyra: \"If you're hearing this, the Deep is waking. I came to stop it. I was too late. I'm sorry.\"",
  "Veyra: \"The Heart was cracking. I took it somewhere safe to mend. Forgive the frost. It's how I hold things together.\"",
  "Veyra: \"Bind him, whoever you are. You'll do better than the dwarves. They never listen to anyone.\"",
],
then: (G) => { flags(G.S).sv_veyra = 1; },
```
- Seer extra page: `"(Your runes go cold. 'Somewhere safe.' The lie is as smooth as the frost.)"`

**After the reveal:**
```js
pages: [
  "(The bell rings. Veyra's voice comes out of the ice, and this time she doesn't sound tired at all.)",
  "Veyra: \"Still mending what I break? The dwarves stole fire and called it craft. I only took it back.\"",
  "Veyra: \"Let the demon out. Or bind him. Either way, Anvildeep learns what it's like to freeze.\"",
],
then: (G) => { flags(G.S).sv_veyra = 1; },
```
The bell's frost melts afterwards. Look: `"An old bell. Just a bell, now. Nobody's voice in it but its own."`

### 6.6 Gorrak Ironmaw: intro

**Befriend and contract:**
```js
pages: [
  "(Chains groan. A shape the size of a house heaves against the anvil-pillar. Fire leaks through the seams of its plates.)",
  "Gorrak: \"SMALL ONES. Nine hundred years I burn for your pots and spoons. Now the cold comes, and the chains go slack.\"",
  "Gorrak: \"You bring a little heart. A LITTLE heart. To hold ME. Ha! Come. Let us see if it fits.\"",
],
```
- Dagna (befriend): `"Gorrak: \"A Coalbeard. Your line always talked back.\" Dagna: \"Still do. Hold still.\""`
- Cinderknight extra page: `"Gorrak: \"Ember-blood! Kin! Why do you stand with the small ones? ...No matter. Burn bright, little cousin.\""`

**Conquer:**
```js
pages: [
  "Gorrak: \"Not a dwarf. A Midgarder. With no heart in your hands, only a sword.\"",
  "Gorrak: \"You did not come to bind me. You came for my fire. Ha! Then TAKE it. If you can.\"",
],
```

### 6.7 Gorrak Ironmaw: outro

**Befriend: rebound, with an optional bargain** (`cd_bound`):
```js
pages: [
  "(Gorrak sags against the chains. His plates hang open. The fire inside him gutters low.)",
  "Gorrak: \"Enough. Put your little heart in. I am... tired. Nine hundred years is a long shift.\"",
  "Dagna: \"Before I do. You burn for us. What would make it bearable? Say it fast, or I won't ask.\"",
  "Gorrak: \"...A Coalbeard, asking. Let me see out. Your festival. The sparks. I hear it through the stone.\"",
],
choice: { id: "gorrak_bargain", options: [
  { label: "Give him the forge mouth at Forgefire Week.", pick: (G) => { flags(G.S).gorrak_bargain = 1;
      return { pages: ["Dagna: \"Forgefire Week. Best seat in Anvildeep. Deal?\"", "Gorrak: \"Deal, small one. Deal.\"",
                       "(Dagna sets the Lesser Heart in his chest-plate. The runes flare cold blue. The Great Forge roars awake.)"] }; } },
  { label: "No deals with demons. Just bind him.", pick: () => ({ pages: ["Dagna: \"Fair. Nine hundred years of practice says you're right.\"",
      "(Dagna sets the Lesser Heart in his chest-plate. The runes flare cold blue. Gorrak glares, then sleeps.)"] }) },
] },
then: (G) => { flags(G.S).cd_bound = 1; G.take("lesser_heart", 1); },
```
- With the bargain, Gorrak's eyes watch Forgefire Week from the forge mouth. Without it, the festival runs the same with the forge
  mouth dark. Merit is the same either way.

**Contract: rebound, no bargain:**
```js
pages: [
  "(Gorrak sags against the chains. The Lesser Heart fits his chest-plate with a clank.)",
  "Gorrak: \"A hired hand. Not even a dwarf. They could not be bothered to come themselves.\"",
  "(The runes flare cold blue. Kesh whoops through the tube.)",
],
then: (G) => { flags(G.S).cd_bound = 1; G.take("lesser_heart", 1); },
```

**Conquer: Gorrak gutters out:**
```js
pages: [
  "(Gorrak falls to one knee. His plates split. The fire inside him has nothing left to hold it.)",
  "Gorrak: \"No little heart. No chains. Only a sword. ...So this is how a fire ends. Quietly.\"",
  "(The armour goes dark and cold. Above it, something glows under a shell of rime in the flue.)",
],
then: (G) => { flags(G.S).cd_taken = 1; },
```

**The frozen flue** (all paths, after the above; a spell thaws it, then E / A):
```js
pages: [
  "(The rime cracks and slides away. Inside, wrapped in frost, a heart of red-gold metal beats slowly.)",
  "(The Anvil-Heart. It never left the mountain. It was here, starving the chains it was meant to feed.)",
],
then: (G) => { flags(G.S).cd_heart = 1; G.give("anvil_heart", 1); G.setQuest("clockdeep", 2); G.toast("Found: the Anvil-Heart", 2.6); },
```
- Dagna (befriend): `"There you are. You daft lump. Let's get you home."` Kesh (contract): `"Is that it? It's warm! Can I hold it? No? Fine."`

### 6.8 Conquer path: leaving Svartalfheim (stage 2 → 3)

On leaving `svartalfheim` for Bifrost with `anvil_heart`:
```js
pages: [
  "(Behind you, the copper door grinds shut. The gears around it slow, and stop.)",
  "(Through the keyhole, the forge-glow is gone. Only cold-blue runes, and the violet glow of the mines.)",
],
then: (G) => { G.setQuest("clockdeep", 3); G.factions.add("gate", MERIT.deep_c, "deep_c"); gold(G, 200);
               const f = flags(G.S); f.sv_resolved = "conquer"; f.sv_cold = 1; },
```

### 6.9 The Thane: the Deep turn-in (befriend and contract, stage 2 → 3)

**Befriend:**
```js
pages: [
  "Our Heart. In the flue, all along. Set it down. There. On the plinth. ...Hear that? The forge, roaring like it's young.",
  "Anvildeep is your friend, Midgarder. We'll forge you anything. Within reason. Our reason. It's quite generous.",
],
then: (G) => { G.setQuest("clockdeep", 3); G.factions.add("embassy", MERIT.deep, "deep"); gold(G, 150);
               G.take("anvil_heart", 1); flags(G.S).heart_home = 1;
               flags(G.S).sv_resolved = "befriend"; G.toast("Svartalfheim is your ally. Forgefire Week is coming.", 3.0); },
```
**Contract:**
```js
pages: [
  "Bound? And you found the Heart? ...Good. Put it down. Here's your pay. Dwarves never short a debt.",
  "We're square, elf-friend. Mind the door on your way out.",
],
then: (G) => { G.take("anvil_heart", 1); flags(G.S).heart_home = 1; G.setQuest("clockdeep", 3); G.setQuest("sv_hire", 3); G.factions.add("gate", MERIT.contract, "contract"); gold(G, 250);
               flags(G.S).sv_resolved = "contract"; },
```

### 6.10 Veyra between realms (the next area load after `sv_resolved`)

| Path | Before the reveal | After the reveal |
|---|---|---|
| befriend | `"You bargained with a demon instead of killing it. Dwarves will tell that one for a thousand years."` · `"Anvildeep's fire is back. Mind it doesn't burn you."` | `"You keep mending what I break. Even the ugly things."` · `"Enjoy the festival. Fires go out."` |
| contract | `"Paid to fix someone else's mess. How Midgard of you."` · `"They didn't even say thank you, did they?"` | `"Mercenary work. I could pay better, you know."` · `"Think on it."` |
| conquer | `"You put out a fire that burned for nine hundred years. You're doing my work for me."` · `"Keep the ember warm. Nobody else will."` | `"Another realm gone cold. Thank you. Truly."` · `"You'd make a fine Rift-Breaker."` |

She leaves before you can answer. The `alfheim.md` 6.10 timing rule applies: if this realm makes the reveal due, this beat plays its
"before" lines and the reveal waits for the next area load (`f.reveal_queued`; here the "seen" flag is `sv_veyra_seen`).

### 6.11 The Living Gauntlet (stage 2 scene, day shift, at the Great Forge)

```js
pages: [
  "(Dagna holds up a gauntlet of dark brass, its knuckles fitted with tiny anvils. She lifts it to the forge mouth.)",
  "Dagna: \"Oi! Ironmaw! Breathe on this. Gently. GENTLY.\"",
  "(Two vast eyes open in the fire. A long, hot breath rolls out. The gauntlet glows red, then gold, then copper.)",
  "Gorrak: \"Hmph. A good gauntlet. For a small one. Hit something worth hitting.\"",
  "Dagna: \"That's the Anvilsoul. A forge for a heart, and a bit of him in it. Look after it. It'll look after you.\"",
],
then: (G) => { G.setQuest("sv_soul", 3); giveGear(G, ANVILSOUL(G.S)); G.toast("Legendary: the Anvilsoul", 3.0); },
```

---

## 7. The Clockwork Deep, room by room

**Theme:** clockwork and fire. A vertical dungeon below the Great Forge: brass gear-trains taller than houses, steam pipes, conveyor
belts, mine rails and chain-lifts, all built by dwarves and gnomes nine centuries ago to tend Gorrak's prison. Now the clockwork runs
wild. **Lit by** furnace bellies, ember cracks, cold-blue binding runes (stuttering) and cave-pool glow. Pools: `forgeconstruct`,
`sparkgolem` (lightning golem), `sootling`, elite `shadowsmith`. Conquer adds 2 `hushblade` in C1 and C5.

Rares (2–3×): the **Amethyst Basilisk** (2.5×) roams C3; the **Soot Colossus** (2.8×) roams C7. Mini-boss: **the Foreman** (2.8×) in C4.
Checkpoint braziers (E4.1): C0 and C5. Frozen cogs (Veyra's frost) appear in C2 and C6. **Thaw** one with any spell within 2.6 m (the
Hollows brazier rule).

| # | Room | Beat | Mechanic / puzzle | Foes | Secrets / glow |
|---|---|---|---|---|---|
| C0 | **The Lift** | a chain cage drops through rock into ticking dark; ember light pulses up from below | **checkpoint brazier 1** | — | Dagna or Kesh's first line |
| C1 | **Gearworks Hall** | a long hall of slowly turning wall-gears; steam vents in the floor | first fight. **Steam vents** puff (0.6 s white puff tell), then blow for 1.5 s (12 damage, a push) | 2 `forgeconstruct`, 2 `sootling` (+2 `hushblade`, conquer) | frost on a wall-gear (look: `"Frost on a gear, this close to the forge. Somebody very cold walked through here."`) |
| C2 | **The Drive Shaft** (Cog 1) | a great drive wheel, stopped | **gear puzzle 1:** fit 2 loose cogs onto pegs to connect the spinning drive to the winch; one fixed cog is **frozen** (thaw it first). A `forgeconstruct` patrols | 1 `forgeconstruct`, 1 `sparkgolem` | `cd_cog1`: the wheel turns and a shutter rises |
| C3 | **The Glowpool Cistern** (side room) | an old cooling cistern gone wild with life: lanternfish, cave glowfrogs, glowing moss, toadstools | a **waterwheel** turns; stop it with a spell to reach the gap behind | 2 `sootling`; Basilisk rare spot | **hidden spring** behind the wheel (`cd_spring`, +40 Gilded Acorns, spring-fizz); frogs in pale blue |
| C4 | **The Assembly Line** (Cog 2) | conveyor belts carry half-built constructs past stamping presses | **gear puzzle 2:** the cogs also set **belt direction**. Get the right spin to the winch, and the belts run toward the exit, not the presses. **The Foreman** guards | **the Foreman** (2.8×) + 2 `forgeconstruct` | `cd_cog2`; the Foreman drops `clock_spring` |
| C5 | **The Frost Bell** | a quiet hall: the alarm bell crusted in frost, 3 carved reliefs | **checkpoint brazier 2**; the bell (6.5); reliefs (6.4) | 2 `shadowsmith` ambush on leaving (+2 `hushblade`, conquer) | a dwarf chest: 60 gold + 1 `deep_brass` |
| C6 | **The Switchyard** (Cog 3) | a cavern of mine rails, switch levers and one loaded cart | **rail puzzle:** set 3 switches, then pull the brake. The cart must reach the **ram gate** and break it; that drops the last cog into place. One switch is **frozen** | 2 `sparkgolem`, 1 `forgeconstruct` | `cd_cog3`; the binding runes stop stuttering for a moment |
| C7 | **Bellows Bridge** | a chain bridge over the furnace pit; giant bellows on both sides | **gusts:** every 6 s a bellows blows across the bridge (a 1 s wheeze tell). Hold a chain post (stand by one) or be pushed back 3 m. No fall damage (cozy): you're pushed back, not off | 2 `sootling`, 1 `shadowsmith`; Soot Colossus rare spot | ember sparks float up from the pit like slow fireflies |
| C8 | **The Binding Forge** (boss) | a round chamber about 16 m across; Gorrak chained to the anvil-pillar; the Great Forge's flue climbs above him | the boss (8.1): 4 **rune-anvils** and 4 **quench valves** on the rim | Gorrak Ironmaw | the Binding Forge (E / A after the fight) |

### 7.1 Gear and rail puzzle spec (for Systems)

**Gear puzzles (C2, C4).** Each room has a small grid of **pegs** (`game.pegs: [{ id, pos, cog?: "s"|"l", fixed?, frozen? }]`).
- A **drive** cog spins on its own (clockwise). A **winch** cog is the target. Loose cogs are carried (E / A picks one up, E / A on an
  empty peg places it). One cog at a time.
- **Meshing:** two cogs mesh if their pegs are adjacent on the grid (orthogonal) and the sum of their radii fits the gap: small–small,
  small–large and large–large all fit at grid spacing 1.0 m in this build (keep it simple; size only changes speed).
- **Spin:** BFS from the drive through meshed, unfrozen cogs. Each step flips direction (`dir = -dir`). The winch turns if it's reached.
- **C4 only:** the winch must turn **clockwise** (even number of steps from the drive). Clockwise runs the belts toward the exit;
  anticlockwise runs them toward the presses (8 damage, a push). The parity is the puzzle.
- **Frozen** cogs don't turn and don't pass spin until thawed (any spell within 2.6 m). They show white rime and a blue shimmer.
- A turned winch sets `S.found[cd_cogN]` and fires `opens`. It stays solved.

**Rail puzzle (C6).** Rails form a small graph (`game.rails: { nodes, edges, switches: [{ id, at, ways: [a, b], frozen? }], start, goal }`).
- E / A at a switch lever toggles it (a clunk and a sign flip). A frozen switch must be thawed first.
- E / A at the brake sends the cart along the current path. It reaches the goal (the ram gate breaks, `cd_cog3`) or a dead end (it
  bumps a buffer and rolls back to start after 3 s). There's no fail state.
- The cart moves at 3 m/s on its own, and foes in its path take 30 damage and are knocked aside.
- Hints: Dagna or Kesh gives one line per room after 60 s. The Seer sees the solved layout as faint dotted ghosts.
- QA: `?cogs=solve` and `?rails=solve` solve the room.

---

## 8. Bosses, enemies and rares

### 8.1 Gorrak Ironmaw, the Bound Forge-Tyrant (Clockwork Deep, C8)

- **Look: 6× the player's height.** A fire-demon bound into **real plate armour** (a boss, so plate is allowed): huge blackened iron
  plates riveted over a body of living flame, a horned helm with a jaw-guard like an iron maw, and chains on his wrists to the
  anvil-pillar behind him. **Cold-blue binding runes** run along every plate seam. Fire leaks through the gaps: forge red and
  orange (biome tones, self-lit), white-hot at the core. His eyes are two coals. The armour is built in layers, so it can open.
- **Arena:** round, 16 m. The anvil-pillar stands in the centre, north of it. On the rim are **4 rune-anvils** (strike them to
  re-light the binding runes) and **4 quench valves** (cold-blue pipes: E / A opens one for 6 s, venting cold steam across a lane).

| Phase | HP | Moves | Tell |
|---|---|---|---|
| 1 **The Bound Tyrant** | 100–65% | chained, he can't leave the pillar's 6 m ring: **hammer slam** (a 3 m shockwave), **chain whip** (a long sweep along one lane), **rivet spray** (a fan of 5 hot rivets); summons 2 `forgeconstruct` every 25 s | slam: he raises both fists, a 0.8 s glow on the knuckles; whip: the chain rattles taut first; spray: his chest-plate vents steam |
| 2 **Unbuckled** | 65–30% | he tears the chains loose and walks. His plates **overheat**: every 12 s they open for 4 s, showing the fire (the **weak point**, ×2 damage). Open a **quench valve** into his path and he steps into cold steam: plates lock open for 6 s and he staggers. He drags **molten lanes** across the floor (pools that last 8 s) | plates glow from orange to white 1 s before they open; molten lane: he scrapes his hammer, sparks run ahead of it |
| 3 **Forge-Tyrant** | < 30% | he pulls on the forge flue's chains: the room heats, and every 10 s a **fire rain** falls (marked circles). Spark golems join (1 every 15 s). **Strike all 4 rune-anvils** (one melee hit or spell each, any order) to re-light the binding: he's pulled to his knees for 8 s, and his damage taken goes ×1.5 for the rest of the fight | fire rain: red circles on the floor 1 s before; an anvil glows blue when it's ready to strike |

At 0 HP the fight ends in the outro (6.7). Befriend and contract: he's **rebound**, not killed. Conquer: you take his ember. The engine
treats it as a boss kill on every path (`onBoss`, guaranteed Legendary).

```js
gorrak: { name: "Gorrak Ironmaw, the Bound Forge-Tyrant", scale: 6, hp: 1800, dmg: 26, speed: 1.1, reach: 3.2, windup: 0.85, cd: 2.1,
          aggro: 12, r: 1.5, push: 0.1, heavy: true, slam: true, boss: true, minion: "forgeconstruct", phases: [0.65, 0.3],
          chained: { r: 6 }, whip: { len: 9, dmg: 20 }, spray: { n: 5, dmg: 10 }, plates: { every: 12, open: 4, mul: 2 },
          quench: { stagger: 6 }, molten: { life: 8, dps: 10 }, rain: { every: 10, dmg: 22 }, anvils: 4, bindMul: 1.5,
          glow: "#e0602a", legendary: true, noRespawn: true },
```

### 8.2 Mini-boss, duel and gate foes

| Foe | Scale | Look | Behaviour |
|---|---|---|---|
| **The Foreman** (`foreman`, C4) | 2.8× | a tall brass overseer construct with a whistle-chimney head, a clipboard welded to one arm, a furnace belly, and frost on one shoulder | whistles up 2 `forgeconstruct` every 20 s; a **steam blast** cone; a stamping charge. Its furnace belly is the weak point while it whistles |
| **Captain Ilvar** (`ilvar`, conquer) | 1.3× (elite, not a boss) | as section 5 | fast twin-blade combos, a **shadow step** behind you (a puff of blue smoke tell), thrown knives; yields at 25% |
| **Runaway construct** (`runaway`, Bifrost) | 2× | a forge construct with a cracked furnace belly, frost flowers on its plates, staggering | the `forgeconstruct` kit with a 3-hit flail; it appears once |

```js
foreman:  { name: "The Foreman", scale: 2.8, hp: 540, dmg: 21, speed: 1.0, reach: 3.0, windup: 0.75, cd: 2.0, aggro: 8, r: 0.85, push: 0.15,
            heavy: true, boss: true, minion: "forgeconstruct", whistle: { every: 20, n: 2 }, steam: { cone: 60, len: 4, dmg: 14 },
            weakWhistle: 2, glow: "#f2a63a", legendary: true, noRespawn: true },
ilvar:    { name: "Captain Ilvar Hushblade", scale: 1.3, hp: 260, dmg: 13, speed: 2.4, reach: 1.4, windup: 0.4, cd: 1.2, aggro: 10, r: 0.32,
            push: 0.5, elite: true, shadowStep: 6, knives: 3, yieldAt: 0.25, noRespawn: true },
runaway:  { name: "Runaway construct", scale: 2.0, hp: 300, dmg: 16, speed: 1.0, reach: 2.0, windup: 0.6, cd: 1.8, aggro: 9, r: 0.6, push: 0.2,
            heavy: true, combo: 3, glow: "#f2a63a", noRespawn: true },
```

### 8.3 Rares (2–3× the player's height)

| Rare (`BASES` key) | Scale | Look | Behaviour | Where |
|---|---|---|---|---|
| **Amethyst Basilisk** (`basilisk`) | 2.5× | a long crystal lizard, violet spines glowing at the tips, eyes like lamps | its **gaze** (a cone, 1 s eye-flash tell) crystallises: −40% speed for 3 s. Tail sweep | Mines roams; Deep C3 |
| **Soot Colossus** (`sootcolossus`) | 2.8× | a towering soot elemental, smoke and cinders around an ember core | a Summoner of `sootling`; grows +10% size and damage during soot fall; a smother cloud (darkens a 3 m circle) | Mines roams; Deep C7 |

```js
basilisk:     { name: "Amethyst Basilisk", scale: 2.5, hp: 300, dmg: 15, speed: 1.4, reach: 2.6, windup: 0.6, cd: 1.8, aggro: 8, r: 0.7,
                push: 0.3, gaze: { cone: 50, len: 5, slow: 0.4, life: 3 }, xp: 185 },
sootcolossus: { name: "Soot Colossus", scale: 2.8, hp: 320, dmg: 16, speed: 1.0, reach: 2.4, windup: 0.7, cd: 2.0, aggro: 8, r: 0.8,
                push: 0.2, minion: "sootling", sootGrow: 0.1, smother: { r: 3, life: 4 }, xp: 195 },
```
`RARE_AREAS.glowmines = { bases: ["basilisk", "sootcolossus"], spots: [[7.4, -4.0], [-8.0, 2.4]] }`. In the Deep, rares spawn at fixed spots
(C3, C7) on the same daily roll (`ROAM_CHANCE`).

### 8.4 New regular enemies (`ENEMIES` suggestions)

```js
forgeconstruct: { name: "Forge construct", hp: 110, dmg: 14, speed: 1.1, reach: 1.6, windup: 0.6, cd: 1.8, aggro: 6.5, r: 0.36, push: 0.3,
                  heavy: true, weakBelly: 1.5 },                       // brass, waist-high to a dwarf's head; a glowing furnace belly (hit it for +50%)
sparkgolem:     { name: "Spark golem", hp: 130, dmg: 15, speed: 1.0, reach: 5.0, keep: 3.0, windup: 0.7, cd: 2.2, aggro: 7, r: 0.4, push: 0.3,
                  ranged: true, bolt: "spark_arc", chain: 2 },          // a lightning golem: iron frame, blue-white arcs between copper coils
sootling:       { name: "Sootling", hp: 34, dmg: 8, speed: 2.0, reach: 1.0, windup: 0.4, cd: 1.6, aggro: 6, r: 0.22, push: 0.7,
                  float: true, popSmoke: 1.5 },                         // a puff of soot with ember eyes; pops into a smoke cloud on death
shadowsmith:    { name: "Shadowsmith", hp: 100, dmg: 14, speed: 2.0, reach: 1.4, windup: 0.45, cd: 1.4, aggro: 7, r: 0.3, push: 0.5,
                  elite: true, shadowStep: 8, hotHammer: 6 },           // dark-elf rogue smith gone wild: leather apron over a shirt, trousers, a glowing hammer
hushblade:      { name: "Hushed blade", hp: 70, dmg: 11, speed: 2.2, reach: 1.3, windup: 0.4, cd: 1.4, aggro: 8, r: 0.28, push: 0.5,
                  stealth: 4 },                                         // conquer only: a dark-elf assassin; wrap-top, sash, trousers; fades in and out
cavegolem:      { base: "golem", name: "Cave golem", glow: "#7a4ab0" },  // the existing stone golem with amethyst crusts
```

XP for `progress.js XP`: `forgeconstruct: 50, sparkgolem: 60, sootling: 22, shadowsmith: 74, hushblade: 40, cavegolem: 56, runaway: 180,
ilvar: 200, foreman: 330, gorrak: 820`.

Gem drops: `gemOdds.forgeconstruct = ["golem_core", 0.08]`, `gemOdds.sparkgolem = ["rift_shard", 0.08]`, `gemOdds.cavegolem = ["golem_core", 0.12]`.

---
## 9. Rewards

### 9.0 Reward table (existing scales: errand 40, boss 80, abyssal rift 120, Embassy ranks 150 / 400 / 800)

| Source | Befriend | Contract (locked) | Conquer |
|---|---|---|---|
| *A Word from the Council* (all) | **+40 Gilded Acorns**, **+60 Rift Marks**, 50 g | same | same |
| *Trial of the Anvil* | **+40 Realm Favor**, 20 g (auto if Alfheim was conquered) | — | — |
| *Giant Footprints* | **+60 Realm Favor**, 40 g (+20 with Orri's letter) | — | — |
| *The Banked Fire* | **+80 Realm Favor**, 60 g, **Dagna** joins | — | — |
| *The Forge Claim* | — | — | **+60 Rift Marks**, 80 g |
| *Hired Hammer* + the Deep | — | **+60 Rift Marks**, 250 g | — |
| Gorrak (boss) | **+80 Realm Favor** (`onBoss`), guaranteed Legendary | **+80 Rift Marks**, Legendary | **+80 Rift Marks**, Legendary |
| *The Clockwork Deep* done | **+120 Realm Favor**, 150 g, Forgefire Week, **Tick** (from Tansy), **Coalbeard's Anvil** (decor) | — | **+120 Rift Marks**, 200 g, the **Anvil-Heart**, **Gorrak's Horn** (cosmetic trophy) |
| Forge school | tiers I–II at Embassy Friend / Trusted (9.2) | closed | closed |
| *The Living Gauntlet* | the **Anvilsoul** (Embassy Honored) | — | — |
| *The Masterwork* | the **Tinker's Heart**, Tinkerforge unlocked | — | — |
| Forgefire Week (repeat) | **+40 Realm Favor**, 30 g, 1 deep brass | — | — |
| Alfheim | **locked** as an ally (rival pair) | (already locked: you befriended Alfheim) | Lumenvale's mood +1 |

### 9.1 The Anvilsoul (legendary weapon)

*"A living forge gauntlet."* Built from `makeItem` at your level (min 10), the same rule as the Prism Edge:

```js
export function ANVILSOUL(S) {
  const it = makeItem(Math.max(10, S.lv || 1), 4, "weapon");
  const k = RARITY[4].mul * (1 + (it.lv - 1) * 0.06);
  it.name = "Anvilsoul"; it.fixed = true; it.unique = "anvil_ring";
  it.mods = { meleeMul: +(0.05 * k).toFixed(3), hpAdd: Math.round(6 * k), guardMul: -0.04 };
  it.gems = [null, null];
  it.about = "A forge gauntlet with a bit of a demon's breath in it. Every 5th hit rings out like a hammer on an anvil.";
  return it;
}
```

- **Unique (`anvil_ring`):** combat counts melee hits. Every 5th one sends a **shockwave ring** (r 2.2 m) that hits every foe in it for 60% of
  the hit and staggers small ones (`fx: "anvil_ring"`: a copper ring of sparks and a deep *clang*). During Forgefire Week, the ring is r 3.0.
- **Look:** a dark-brass gauntlet with tiny anvils on the knuckles and a warm copper glow in its palm-vents (biome tone, self-lit). While
  equipped, small sparks drift off it now and then. The Legendary aura still applies.
- It can be upgraded to +10 and rerolled like any Legendary (`forge_alchemy.md`). Rerolls never touch the unique.

### 9.2 The Forge school (learned from Sereth, befriend)

Unique to Svartalfheim: **forge-runes**, the dark elves' cold rune-light hammered into hot dwarven metal. Every spell is half fire,
half rune.

| Tier | Needs | Spell | Shape |
|---|---|---|---|
| I | Deep done + Embassy **Friend** | **Rivet Volley** | `rivet_volley: { name: "Rivet Volley", cd: 2.6, dmg: 9, n: 5, spread: 40, range: 6.0, kind: "volley", school: "forge", fx: "rivet_volley", hotGround: 2 }` (5 white-hot rivets in a fan; each leaves a hot spot for 2 s that burns foes standing in it for 4/s) |
| II | Embassy **Trusted** | **Molten Armour** | `molten_armour: { name: "Molten Armour", cd: 14, kind: "self", life: 6, school: "forge", mods: { guardMul: -0.25 }, thorns: 8 }` (your clothes glow with rune-lines for 6 s: −25% damage taken, and melee attackers take 8) |
| III (**parked**) | Embassy **Honored** | **Clockwork Construct** (summon) | `SUMMONS.clockwork = { name: "Clockwork construct", hp: 70, dmg: 10, reach: 1.4, speed: 1.6, taunt: true, life: 20 }` (a brass guard that draws aggro) |

Learning uses `G.learn(id)`. **Tier III is parked**, the same rule as the Prism school's tier III: it needs the alternate-summon slot
(`S.altSummon`). The spec stays here.

Sereth teaching (first talk once tier I is met):
```js
pages: [
  "You bound him, and you didn't gloat. Rare, in a Midgarder. Hold out your hand. Palm up.",
  "(Sereth traces a cold-blue rune on your palm. Then Dagna slaps a hot rivet into it. It doesn't burn. It hums.)",
  "Rivet Volley. Fire from the dwarves, aim from us. Throw it like you're angry at a wall.",
],
then: (G) => { G.learn("rivet_volley"); G.toast("Learned: Rivet Volley (Forge school)", 2.6); },
```
Tier II: `"Molten Armour. Wear the forge for a breath or two. Don't hug anyone."`
Tier III (parked): `"A clockwork guard of your own. Wind it daily. It sulks otherwise."`

### 9.3 Dagna (companion, befriend)

`flags.companions.dagna = 1` at *The Banked Fire*'s end. Look, sprite notes, `COMPANIONS.dagna`, kit and barks are in 5.4. Contract and
conquer: she never joins. Contract: `"Dagna: \"Elf-friend. Hm. Do your job. Don't touch my forge.\""` Conquer: her side forge stands cold
and empty.

### 9.4 The rival payoff (Alfheim)

- Befriend here: `lockRival(G.S, "alfheim")` at the Thane's choice sets `S.flags.rivals = { ...rivals, alfheim: "locked" }`. In Lumenvale,
  Aerin's befriend option greys out (`locked`), and a light-elf merchant in the Wisp Market leaves (`flags.elf_left = 1`):
  `"So you've thrown in with the coal-beards. Lumenvale keeps a ledger too. In light. It's very pretty."`
- Conquer here: `moodUp(G.S, "alfheim")` sets `S.flags.realm_mood = { ...mood, alfheim: 1 }`. In Lumenvale, Aerin opens with
  `"You humbled Anvildeep? Then perhaps Midgard is not all cold iron. Sit."`
- Brokk's lines (5.6) close the loop started in `alfheim.md` 5.9.

### 9.5 Tick, the clockwork owl (mechanical pet, befriend)

Tansy finishes Tick after *The Clockwork Deep* (befriend). He joins the Stray Den roster like any pet (`S.pets.tick`). Tansy:
`"He's done! He's yours! Tick, say hello. (Tick says 'tick'.) He's shy."`

```js
// pets.js PETS addition (neon pets rule: only the glowing eyes and the chest-gear use the neon blue ramp)
tick: {
  name: "Tick", species: "clockwork owl", role: "pet_owl", glow: "#5ab4f0",
  hover: { lift: 0.7, bob: 0.05, hz: 1.2 },                                   // a little mechanical flutter
  light: { color: "#5ab4f0", intensity: 3.0, range: 2.6, lift: 0.8, pulse: [0.9, 1.05, 1.2], r: 1.6 },
  fx: { aura: "pet_aura_owl", pool: "pet_pool_owl", parts: "pet_owl_tick" },
  aura: { id: "clockwork_eye", name: "Clockwork Eye", desc: "Hidden doors, springs and chests glint within 6 m. Gold from pickups +6%. Bond 3: 8 m, +8%.",
          mods: { secretSense: 6, chestSense: 6, goldMul: 0.06 }, bond3: { secretSense: 8, chestSense: 8, goldMul: 0.08 } },
  about: "A brass owl the size of a teacup, with cold-blue eyes and a gear that ticks in his chest. Hoots in clicks.",
  names: ["Tick", "Cogsworth", "Sprocket", "Brassy", "Whirr", "Pinion", "Tock", "Bolt"],
},
```
- **Name check:** "Tick" is the handoff's own canon name for this clockwork owl (`HEARTHMOOR_BUILDER_HANDOFF.md` §11.6, next to
  Morriel; `pets.md` lists him as a later pet). It's the same pet, so there's no second Tick and no rename.
- **Look:** a teacup-sized brass owl, riveted feathers, a little copper beak, a glass chest window with a ticking gear, and big **cold-blue**
  eyes (the glow). He flutters with a clicking sound and turns his head 180° to look at secrets.
- `chestSense` (chests glint) and `goldMul` (pickup gold) are **new aura keys**. The moss-pup added `springSense` the same way. They need
  small hooks in `pets.js` and the pickup code.
- Barks: `"(Tick clicks twice and points his whole head at the wall.)"` · `"Tick! Tick-tick!"` (a secret nearby) ·
  `"(Tick tucks his head under a brass wing. Even clockwork naps.)"` (night) · `"(Tick ticks faster. A rift storm.)"`

### 9.6 The Tinkerforge hook: the Tinker's Heart

The secret hero **Tinkerforge** (dwarf/gnome engineer, clockwork constructs) unlocks when you **build a legendary crafted treasure**
(design canon). Here that's *The Masterwork* (3.9): the **Tinker's Heart**, a Legendary trinket you build at the Great Anvil.

```js
export function TINKERS_HEART(S) {
  const it = makeItem(Math.max(10, S.lv || 1), 4, "trinket");
  const k = RARITY[4].mul * (1 + (it.lv - 1) * 0.06);
  it.name = "Tinker's Heart"; it.fixed = true; it.unique = "wound_up"; it.crafted = true;
  it.mods = { stAdd: Math.round(4 * k), summonMul: +(0.03 * k).toFixed(3), crit: +(0.008 * k).toFixed(3) };
  it.gems = [null, null];
  it.about = "A clockwork heart in a cage of amethyst. Stand still and it winds up. Your next hit lets it go.";
  return it;
}
```
- **Unique (`wound_up`):** after 3 s without taking damage, the next hit deals +30% (a tiny *ding* and a copper flash).
- On building: `S.unlocks.tinkerforge = 1` and the toast `Secret hero unlocked: Tinkerforge`. Tansy: `"You built that? With those hands? I'm going to cry into my goggles."`
- Tinkerforge's own kit (NG+ hero select) is a later doc.

### 9.7 Conquer path: Cold Anvildeep (`flags.sv_cold = 1`)

After *The Clockwork Deep* on the conquer path, Anvildeep gets a **re-grade, not a blackout** (the Dark Lumenvale rule). It's gloomy
but glowing: **cold blue, ember red and violet**. It's **never flat dark**.

**Art spec (the `sv_cold` grade):**
- **Ambient:** deep slate (`#1a1c26`) instead of warm brown-black. No warm under-light from the Great Forge: its mouth is a dull ember
  glow (`#6a2a1a`) with frost flowers round the rim.
- **Cold blue:** rune-light becomes the main light. Runes on doorframes and bridges stay lit but **stutter** (a 1-in-4 missed pulse), and the
  Hushed hang extra **rune-lamps** (`#5ab4f0`, small point lights) on bridges, stairs and doors, so paths stay readable.
- **Ember red:** chimneys show only a few dying embers (`#c4502c`, slow pulses). Window lamps go from warm orange to a dim red, and
  only 1 in 3 is lit.
- **Violet:** the mines' crystal tips stay lit, and nothing else changes there. It becomes the brightest place in the realm.
- **Cave pools:** stay blue-green, but the lanternfish dim and the frogs don't sing (chorus muted).
- **Particles:** a light, constant soot drift (`soot_fall` at rate 0.3), no sparks.
- **Readability floor:** at least one light source within ~4 m of any walkable tile. Every door, stair, NPC and pickup keeps its own small light.
- **Implementation:** a per-area light palette (`LIGHTS.sv_cold`) plus a light-group toggle for the window lamps that go out. A plain
  "lights off" toggle is not enough.

Also: Tansy's prices ×1.5 and Common gear only. No Forgefire Week. NPCs use their conquer lines. Rifts in `glowmines` open 25% more
often (`EVERY` × 0.75). Tremors stay at the doubled rate (nothing holds the mountain). Hidden springs and waystones still work.

### 9.8 Materials, cosmetics, trophies

- **Deep brass** (`deep_brass`): drops from `forgeconstruct` 20%, `sparkgolem` 10%, the Foreman 2, the C5 chest 1, tremor-cracked ore veins 2.
  Sells for 12 g. It's used in *The Living Gauntlet* and Forgefire orders.
- **Amethyst** (`amethyst`): mined from small crystal clusters in `glowmines` (E / A, 1 each, `regrow: 1`, the daily pickup hook from
  `forge_alchemy.md` 1.2), `cavegolem` 25%, the Basilisk 3. Sells for 8 g.
- **Forge-core** (`forge_core`): quest item (3.4). Extra seams don't respawn.
- **Clock spring** (`clock_spring`): the Foreman always drops 1. Used in *The Masterwork*.
- **Anvil-Heart** (`anvil_heart`): it goes home on befriend and contract. On conquer it's the key trophy: Sable buys it for
  **400 g + 40 Black Doubloons**, the same as the Prism Heart sale.
- **Gorrak's Horn** (conquer, cosmetic) and **Coalbeard's Anvil** (befriend, house decor): trophy-wall and housing items for later.
- **No new gem.** A 6th "ember core" gem is **parked** (lead, 2026-10-06). `golem_core` drops more here.

---

## 10. `markerFor` additions

```js
const F = S.flags || {}, V = (F.alliance || {}).svartalfheim, q = S.quests, inv = S.inv || {}, R_ = (id) => (S.ranks || {})[id] || 0;
const LOCK = (F.rivals || {}).svartalfheim === "locked";
// Hearthmoor / Ravenhold / Bifrost
if (id === "banker" && R_("gnome") >= 2 && !q.sv_gate) return "quest_mark";
if (id === "gatewright" && q.sv_gate === 1 && F.sg_vouch && !F.sg_sent) return "quest_turnin";
if (id === "gatewright" && q.sv_gate === 1 && F.sg_sent && !F.sg_key && keyReady(S)) return "quest_turnin";
if (id === "gatewright" && q.sv_gate === 2) return "quest_turnin";
if (id === "dwarfsmith" && q.sv_gate === 3 && q.forge_riot === 3 && !F.orri_letter) return "quest_mark";
// Anvildeep
if (id === "thane" && q.sv_gate === 3 && !V && !F.sv_contract) return "quest_mark";
if (id === "thane" && (q.sv_trial === 2 || q.sv_name === 2 || q.sv_kindle === 2)) return "quest_turnin";
if (id === "thane" && q.clockdeep === 2 && V !== "conquer") return "quest_turnin";
if (id === "dagna" && q.sv_trial === 1 && (F.st_hits || 0) >= 3) return "quest_turnin";
if (id === "dagna" && q.sv_name === 3 && !q.sv_kindle) return "quest_mark";
if (id === "dagna" && q.sv_kindle === 1 && ["fc_1", "fc_2", "fc_3"].every((k) => (S.found || {})[k])) return "quest_turnin";
if (id === "dagna" && V === "befriend" && q.clockdeep === 3 && !q.sv_soul && R_("embassy") >= 3) return "quest_mark";
if (id === "dagna" && q.sv_soul === 1 && (inv.deep_brass || 0) >= 3) return "quest_turnin";
if (id === "dagna" && forgefireDay(S) && !q.forgefire) return "quest_mark";
if (id === "dagna" && q.forgefire === 1 && (S.forgefire || {}).strikes >= 3 && (S.forgefire || {}).orders >= 3) return "quest_turnin";
if (id === "runewarden" && q.sv_name === 1 && F.sn_prints && !F.sn_lock) return "quest_mark";
if (id === "runewarden" && q.sv_name === 1 && F.sn_mould) return "quest_turnin";
if (id === "minerunner" && q.sv_hire === 1 && F.sh_terms && !F.sh_kesh) return "quest_mark";
if (id === "tinker" && V === "befriend" && q.clockdeep === 3 && !(S.pets || {}).tick) return "quest_turnin";
if (id === "tinker" && V === "befriend" && q.clockdeep === 3 && (S.pets || {}).tick && !q.sv_master) return "quest_mark";
```

`keyReady(S) = (S.day || 0) > (S.flags.sg_sentDay || 0) || (S.flags.sg_riftAfter || 0) > 0`.
`forgefireDay(S) = (S.flags.alliance || {}).svartalfheim === "befriend" && S.quests.clockdeep === 3 && S.day % 7 === 3 && !NIGHT(t)`.

TALK ids: `thane`, `runewarden`, `dagna`, `hushed`, `dwarftrader`, `tinker`, `minerunner`, `poolkeeper_sv`, `dw1..3`, `sv1..2`, `forgeorder1..3`;
narration ids `narr`, `clue` (vault, slag pits), `relief`, `bell`; boss speaker `gorrak`. New options on existing ids: `banker`, `gatewright`, `dwarfsmith` (Orri).

---

## 11. Items (`ITEMS` additions)

```js
council_vouch: { name: "Council's word", px: "council_vouch", about: "A tiny letter with a tiny acorn seal. Don't fold it. Gnomes notice folds." },
copper_key:    { name: "Copper key", px: "copper_key", about: "A clockwork key from under the mountain. Wind it in the gate. It ticks." },
orri_letter:   { name: "Orri's letter", px: "orri_letter", about: "For the Thane. Sealed with two crossed cogs. It smells of quench water." },
boot_mould:    { name: "Frost-iron giant boots", px: "boot_mould", about: "Huge iron soles with little straps. Never warm. Evidence." },
forge_core:    { name: "Forge-core", px: "forge_core", about: "A lump of ember-ore that beats faintly, like it's thinking about being a heart." },
lesser_heart:  { name: "Lesser Heart", px: "lesser_heart", about: "Dagna's stopgap heart in a copper cage. Ugly. Works." },
forge_seal:    { name: "Forge-Seal", px: "forge_seal", about: "Copper and rune-light. It opens the Deep's lift, and nothing else." },
speaktube:     { name: "Speaking-tube badge", px: "speaktube", about: "Kesh's voice comes out of it. So does a lot of humming." },
deep_brass:    { name: "Deep brass", px: "deep_brass", about: "Old dwarven brass from the Deep's clockwork. Darker than normal brass, and warmer." },
amethyst:      { name: "Amethyst", px: "amethyst", about: "Violet crystal from the mines. It catches rune-light and keeps a little." },
clock_spring:  { name: "Clock spring", px: "clock_spring", about: "The Foreman's mainspring. Still tightly wound. Mind your fingers." },
anvil_heart:   { name: "Anvil-Heart", px: "anvil_heart", about: "A heart of red-gold metal that beats slowly. Anvildeep's fire lives or dies with it." },
gorrak_horn:   { name: "Gorrak's Horn", px: "gorrak_horn", about: "A horn from an iron helm, still faintly warm. A trophy. No dwarf will look at it." },
coalbeard_anvil:{ name: "Coalbeard's Anvil", px: "coalbeard_anvil", about: "A little anvil from Dagna. 'For your mantel. Or for hitting things. Your choice.'" },
lantern_fish:  { name: "Lanternfish lamp", px: "lantern_fish", about: "A Forgefire lamp with a glowing fish painted on it. It floats, if you let it." },
```

Gear: `ANVILSOUL(S)` (9.1), `TINKERS_HEART(S)` (9.6). Pet: `PETS.tick` (9.5).

---

## 12. Save shape (summary)

| Key | Meaning |
|---|---|
| `S.flags.alliance.svartalfheim` | `"befriend"` / `"conquer"` (unset on the contract path) |
| `S.flags.sv_contract` | the contract path (Svartalfheim locked, hired instead) |
| `S.flags.sg_vouch`, `sg_sent`, `sg_sentDay`, `sg_key`, `sg_runaway`, `sv_gate_open` | *A Word from the Council* |
| `S.flags.orri_letter` | Orri gave the letter |
| `S.flags.st_hits`, `sv_trusted` | *Trial of the Anvil* |
| `S.flags.sn_prints`, `sn_lock`, `sn_mould`, `sv_cleared`, `sv_decoy` | *Giant Footprints*; the decoy trail (Jotunheim hook) |
| `S.found.fc_1..3` | *The Banked Fire* |
| `S.flags.fk_ilvar`; `S.found.fk_p1..3` | *The Forge Claim* (conquer) |
| `S.flags.sh_terms`, `sh_kesh` | *Hired Hammer* (contract) |
| `S.found.cd_cog1..3`, `cd_spring`, `cr_spring`, `gm_spring`, `relief_1..3`, `gm_crack1..3` | Deep cogs, springs, reliefs, tremor cracks |
| `S.flags.cd_boss`, `cd_bound` / `cd_taken`, `cd_heart`, `heart_home`, `gorrak_bargain` (optional), `sv_veyra`, `sv_veyra_seen`, `sv_resolved` | the Deep, the bargain, Veyra's bell |
| `S.flags.sv_cold` | conquer: Cold Anvildeep |
| `S.flags.companions.dagna` | Dagna joined |
| `S.pets.tick` | Tick, the clockwork owl |
| `S.flags.rivals.alfheim` / `S.flags.realm_mood.alfheim` | the rival lock / Lumenvale's mood (set here) |
| `S.flags.elf_left` | the light-elf merchant left the Wisp Market |
| `S.evidence.svartalfheim` | `"boot_mould"` |
| `S.forgefire` | `{ strikes, orders }` for this festival |
| `S.unlocks.tinkerforge` | the secret hero unlocked |
| `S.quests.sv_gate / sv_trial / sv_name / sv_kindle / sv_take / sv_hire / clockdeep / sv_soul / sv_master / forgefire` | 0–3 |

New helpers: `locked(S)`, `mood(S)`, `keyReady(S)`, `forgefireDay(S)`, `ANVILSOUL(S)`, `TINKERS_HEART(S)`; the choice fields `locked` /
`lockedLabel` / `show`; `factions.realm()` returns `gate` in `SVART_AREAS` when `alliance.svartalfheim === "conquer"` or `flags.sv_contract`.
Reused from `alfheim.md`: `lockRival`, `moodUp`, `giveGear`, the reveal queue.

---

## 13. Later: Rift-Breaker variant (stub, low priority)

Not for this build. If the player has joined Veyra (`flags.rift_breaker`) before Svartalfheim, the arc flips to sabotage. Rough beats:
- The copper gate opens with Veyra's help: the key capsule arrives already wound.
- No choice. The Thane takes you for a Midgard envoy.
- You **plant the boot mould** toward Stonehollow (giving the dwarves their war), carry the frozen Heart to Veyra, and in C8 you **break the Lesser Heart** so
  Gorrak walks free. It's the conquer grade (9.7) with Gorrak loose in the Deep.
- Dagna never joins, and she becomes a hunter later. The Rift-Breaker doc owns all the lines.

---
## 14. Decisions (all resolved by the lead, 2026-10-06)

1. **Hired Hammer (contract path): kept.**
2. **The Anvil-Heart is found in the Deep** (frozen in the Binding Forge's flue), and the Stonehollow trail is a decoy. It goes home on
   befriend and contract, and the player takes it on conquer (4.5, 6.7–6.9).
3. **Gorrak's bargain is an optional ending:** a choice in the befriend outro (6.7). He's bound either way.
4. **Mirror edits applied to `alfheim.md`:** Aerin's befriend option locks if Svartalfheim is befriended. Conquering Svartalfheim makes
   Lumenvale friendlier (Aerin's opener, Faelan's line, +20 Realm Favor on *A Name in Frost*).
5. **Gate pacing:** Gnome Council Trusted, as in `bifrost.js`.
6. **Crystal mines are neon-tipped violet.** The style lock limits bloom and sprite palettes, not environment glow (2.2).
7. **6th gem: parked.**
8. **Forge Quarter fallbacks: dropped.** Batch 2 builds the Forge Quarter before any post-Alfheim realm.
9. **Tick's aura keys** (`chestSense`, `goldMul`): fine. "Tick" is the canon name for this same owl, so no rename was needed (9.5).
10. **Forgefire Week** every 7th day (`% 7 === 3`), **dwarf women with beards**, **Forge tier III parked** and **Gorrak at 6×**: as written.

## 15. Open questions

1. **A mirror contract for Alfheim?** A player who befriends Svartalfheim first is locked out of Alfheim's befriend path and can only
   conquer or skip. Should Alfheim get its own "hired" path into the Prism Vault?
2. **Companions active at once.** A conquer-Alfheim player can have Dagna plus Tobble. Is it 1 active? (The system isn't built yet.)
