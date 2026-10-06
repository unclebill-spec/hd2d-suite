# Rift storm nights

Story design doc, file 4 of 6 for Hearthmoor (staging, 2026-10-05). It covers lines and one repeatable bounty for **rift
storms**, the Bifrost / Rift weather from E5.3 ("rift storm: rifts open nearby, Rift Marks +25%") and the E5.4 world
event ("many rifts at once in one realm"). It uses the shapes in `weather.js` (`weatherAt`, `KINDS`, `SKY`), `rifts.js`
(`TIERS`, `RIFT_AREAS`, `EVERY`, `open/close`), `factions.js` (`onRift`, `MERIT`) and `data.js` (`TALK`, `QUESTS` with
**3 = done**). Conflicts are in the last section.

---

## 0. What's already built (hook points)

| In the build | Where | Use |
|---|---|---|
| `weatherAt(area, day, t)`: town = clear / drizzle / rain, glen = morning mist, hollow = night glow-mist, **void (`rift`, `bifrost`) = always clear** | `weather.js` | add a `riftstorm` kind for the void sky (section 1) |
| Random rifts: one at a time, `FIRST` 45-80 s, `EVERY` 120-200 s, `LIFE` 90 s, +1 foe at night, night tier weights `[45, 38, 17]` | `rifts.js` | the storm shortens the timers |
| `RIFT_AREAS`: **mossglen, hollows, vanaheim** only (bifrost and rift have none yet) | `rifts.js` | storms need spots in `bifrost` and `rift` (section 1.3) |
| `onRift(tier)`: `MERIT.rift [30, 60, 120]` Rift Marks × `(1 + M.riftMarkMul)` (the lantern-fox), plus half to the realm faction | `factions.js` | the storm adds +0.25 to that multiplier |
| Signe's rotating line already checks **`F.storm === 'bifrost'`** | `data.js` (working tree) | this doc defines `S.flags.storm` |
| The lantern-fox's `riftWarn` / `senseRift` | `pets.js`, `rifts.js` | a storm bark on top |

---

## 1. Storm rules (for Systems)

### 1.1 When

- A storm is a **night event** (`t > 0.8 || t < 0.25`, the same window as `rifts.night()`), seeded by the day so a reload
  gives the same night.
- **Storm region** = `S.flags.storm`, one value at a time:
  - `"bifrost"` covers both void areas (`bifrost` and `rift`). Chance: **1 night in 4** once `flags.bf_seen` is set (never on
    day 0, never two nights running).
  - `"mossglen"`, `"hollows"` or `"vanaheim"`: the rarer **world event** (E5.4), **1 night in 10**, only if no Bifrost storm
    that night.
- It **starts** at dusk-into-night (t crosses 0.8) and **ends at dawn** (t crosses 0.25). It never runs during the Lantern Eve
  opening or before `flags.intro`.
- Suggested pure function next to `weatherAt`, so smoke can check the calendar:
  `stormAt(day) => "bifrost" | "mossglen" | "hollows" | "vanaheim" | null` (hash of `day`, like the town rain).

### 1.2 What it does

| Effect | Value |
|---|---|
| Rift timers in the storm region | `FIRST` → **10-20 s**, `EVERY` → **40-70 s**. Still one rift at a time |
| Tier weights in the storm (night) | `[35, 45, 20]` (more majors, a little more abyssal) |
| **Rift Marks** | **+25%**: `onRift` uses `mul = 1 + M.riftMarkMul + (storm ? 0.25 : 0)`, Rift Marks only, as with the fox |
| Rift gold | unchanged (the Guild Friend +25% still applies) |
| Weather look | `KINDS.riftstorm`: violet-red sky cracks flicker (reuse `rift_tear_minor` high in the sky as a backdrop fx every 6-10 s), cold-fire motes drifting down, a low rumble; **no bloom**, light pools only |
| Light | storm lightning = a short point-light flash in violet `#c03cc8` or red `#e0302a`, never a full-screen flash |
| Hearthmoor / Ravenhold | no rifts there (they're not storm regions), but if `F.storm === "bifrost"` the Rift above Ravenhold flickers in their sky and NPCs talk about it |

### 1.3 New rift spots

```js
RIFT_AREAS.bifrost = { foes: ["wraith", "skeleton", "skelmage", "wraith"],
                       spots: [[-8.2, 6.4], [8.4, 6.0], [0.0, 8.6], [-6.4, -4.6], [6.6, -4.4]], stormOnly: true };
RIFT_AREAS.rift    = { foes: ["wraith", "skelmage", "wraith"], spots: [/* 2-3 dais edge spots */], stormOnly: true };
```

`stormOnly`: these areas only open rifts while `F.storm === "bifrost"`. The spots are suggestions inside Bifrost's ±11 camera
bounds, away from the nine arches and the Den yard. Fit them to the plaza.

### 1.4 Save and QA

- `S.flags.storm` = region id or `null`; `S.storm = { day, sealed: 0, best: 0 }` counts rifts sealed this storm (for the bounty
  and the morning-after toasts); `S.flags.stormAfter = day` is set at dawn if `S.storm.sealed >= 1`.
- QA params (suggested): `?storm=bifrost|mossglen|hollows|vanaheim`, `?storm=off`.

---

## 2. UI text

### 2.1 Onset banner (the big title card, like the area-name banner)

| Region | Title | Subtitle |
|---|---|---|
| bifrost | `RIFT STORM` | `The bridge is cracking with light. Rifts will open tonight. Rift Marks +25%.` |
| mossglen | `RIFT STORM OVER MOSSGLEN` | `The glade's sky is splitting. Rifts will open tonight. Rift Marks +25%.` |
| hollows | `RIFT STORM IN THE HOLLOWS` | `Cold fire flickers between the toadstools. Rifts tonight. Rift Marks +25%.` |
| vanaheim | `RIFT STORM OVER MOSSBROOK` | `Violet light cracks over the springs. Rifts tonight. Rift Marks +25%.` |

When you're **outside** the region at onset, a toast instead:

| Region | Toast |
|---|---|
| bifrost | `The Rift above Ravenhold flickers violet and red. A rift storm is breaking over Bifrost Crossing.` |
| mossglen | `Cracks of cold fire over Mossglen. A rift storm is breaking in the glade.` |
| hollows | `The Hollows' glow-mist turns violet. A rift storm is breaking under the toadstools.` |
| vanaheim | `A violet glow over the vine gate. A rift storm is breaking in Vanaheim.` |

### 2.2 Storm toasts (during)

| Trigger | Toast (one at random) |
|---|---|
| a rift opens in the storm | `The storm tears a rift open nearby!` · `Another rift splits the dark!` · `The sky cracks, and something steps through.` |
| an abyssal rift in the storm | `The storm rips an abyssal rift open. The ground hums under your boots.` |
| a rift sealed in the storm | `${T.name} sealed! Storm bonus: +25% Rift Marks.` |
| 3rd rift sealed this storm | `Three rifts sealed tonight. The storm is losing its temper.` |
| 5th rift sealed this storm | `Five! The Guild will be talking about this one for weeks.` |
| midnight (t crosses 0.0) | `Midnight. The storm is at its loudest.` |
| last hour (t crosses 0.2) | `The storm's edge is fraying. Dawn's coming.` |
| entering the region mid-storm | `The air crackles. You're inside the rift storm.` |

### 2.3 Storm end (dawn)

- Banner subtitle (in region): `The rift storm blows itself out. Gold light spills over the bridge.`
  (Midgard regions: `...over the glade.` / `...under the caps.` / `...over the springs.`)
- Toast (outside the region): `Dawn. The Rift above Ravenhold goes quiet again.`
- Summary toast if you sealed any: `Storm weathered: ${n} rift${n > 1 ? "s" : ""} sealed. Folk will want to raise a cup.`
- If you sealed none: `The storm passed you by. There'll be others.`

---

## 3. NPC storm lines

**Hook:** a `STORM_SAY` table keyed by TALK id. While `F.storm` is set, the NPC's **first page** is replaced by the storm line,
**unless** they're mid-quest with you (quest pages win). `AFTER_SAY` is used the next day if `F.stormAfter === S.day - 1`
(or the same day after dawn). The storm line is chosen by whether the storm is **here** (`F.storm` covers this area) or
**afar** (seen in the sky). Ambient overhead `say` barks use the same table.

### 3.1 Hearthmoor Plaza

| NPC (id) | Storm line | Morning after |
|---|---|---|
| Marla the baker (`baker`) | `"Storm over the Rift again. I've put an extra loaf in. Storms make heroes hungry."` | `"Rift-storm rolls! Same dough, more cinnamon. I name my bakes after weather now."` |
| Tib (`kid`) | `"The sky's doing the purple crackle! Grandpa says count between flashes. I got to forty and lost track."` | `"Did you fight the storm? Did you win? Can I see your sword? Is it scorched?"` |
| Grandpa Alder (`elder`) | `"My grandmother called these bridge-storms. She said the Rift was stretching its legs. Stay warm."` | `"Quiet morning. The Rift's done stretching. Sit a while, you've earned the bench."` |
| Warden Hilde (`hilde`) | `"Rift storm. The Order's lamps stay lit till dawn, every one. If you're going out, go armed."` | `"Lamps held all night. So did you, I hear. The Order remembers that."` |
| Odo (`merchant`) | `"Storm night! Tonics are flying off the shelf. Well. Being bought. Nothing's flying. Hopefully."` | `"Bring me whatever the storm spat out. Storm-scorched finds fetch a storm-scorched price!"` |
| Bix Coppertuft (`banker`) | `"Storm insurance? No such thing. Bank your gold before you go. Fainting in a storm is expensive."` | `"Busy night for the vault. Everyone banks before a storm. Nobody banks after. Funny, that."` |
| Sefa (`nightmerchant`) | `"Storm nights are good for trade. The lantern likes the crackle. So do rift shards."` | (Sefa leaves at dawn; no morning line) |
| Pudding (`cat`) | `"Pudding is under the bread crate, glaring at the sky."` | `"Pudding emerges, dignified, as if nothing happened."` |

### 3.2 Bakery Lane

| NPC (id) | Storm line | Morning after |
|---|---|---|
| Wren the herbalist (`herbalist`) | `"Moonpetal tea calms storms. Not the sky kind. The tummy kind. Take a sip before you go."` | `"The moonpetals hummed all night. They like a storm. Strange little flowers."` |
| Bram of the Kettle & Key (`innkeeper`) | `"Storm's up! Fire's high, stew's hot, and the door stays open for anyone running from the sky."` | (Bram's toast, section 4) |
| Pip the player (`musician`) | `"I'm writing a storm song. It's about bread. Bread in a storm. It's very dramatic."` | `"Last night's song is finished. It's called 'Crust, Struck by Lightning'. It's about bread."` |
| Odile (`gardener`) | `"The geraniums don't like the crackle. Neither do I. We're staying in."` | `"Not a petal lost. The mint tried to escape in the confusion, though."` |
| Biscuit (`dog`) | `"Biscuit howls at the purple sky, then hides behind your legs."` | `"Biscuit wags at you like you personally fixed the sky."` |
| Mrs. Cluck (`chicken`) | `"Mrs. Cluck has gone indoors. Mrs. Cluck has opinions about storms."` | `"Bawk. (An egg, laid in protest, sits on the step.)"` |

### 3.3 Mossglen and the Toadstool Hollows

| NPC (id) | Storm line | Morning after |
|---|---|---|
| Sorrel (`keeper`) | here: `"The moss is shivering. Rifts are opening in the glade. Walk kindly, and walk fast."` / afar: `"The moss feels the storm from here. It hums lower. Listen."` | `"The moss is humming again. It remembers who walked through the storm for it."` |
| Hoot (`owl`) | `"(Hoot's feathers stand on end. He stares at the sky like it owes him mice.)"` | `"Hoo. (Hoot looks at you with something close to respect.)"` |
| Pipkin (`gnome`, Hollows) | here: `"Big-folk! Rifts between the caps! Light the braziers, cold fire keeps the worst off!"` / afar: `"Storm on the bridge. Down here we bolt the gnome doors and eat cake."` | `"We saved you a slice of storm cake. It's mostly crumbs. Gnomes get nervous-hungry."` |

### 3.4 The Rift Shrine and Vanaheim

| NPC (id) | Storm line | Morning after |
|---|---|---|
| Ondra, the rift-keeper (`riftkeeper`) | `"The Rift isn't angry, hearth-walker. It's straining. Something pulls at it from the cold side."` | `"It's settled. For now. Every storm leaves the bridge a little thinner. I count the cracks."` |
| Elder Burrowmoss (`warden`) | here: `"Rifts over the springs! Keep them off the water. We just got it clean."` / afar: `"Bridge-storm. The spores get twitchy. So do I."` | befriend: `"Springs held. You held. Mossbrook toasts you, and gnome toasts are loud."` · conquer: `"Storm's gone. You're still here. Pity about one of those."` |
| Tobble (`tobble`, staging) | `"*tweet tweet!* Two means run. But we're not running, are we? No. Fine. Brave tweet."` | `"I counted every rift you sealed. I ran out of fingers. I used toes. Gnome toes count double."` |

### 3.5 Ravenhold Harbor

| NPC (id) | Storm line | Morning after |
|---|---|---|
| Harbormaster Brannoc (`harbormaster`) | `"Rift storm up top. No boats under the bridge tonight, Corsair or otherwise. Not on my watch."` | `"All boats home, all ropes counted. Twice. You can see the Rift's scorch marks from the pier."` |
| Quartermaster Sable (`quartermaster`) | `"Storm nights pay double up there, if you've the nerve. The Guild pays marks. I pay in coin."` | `"Heard you were up on the bridge in that. Either brave or broke. Corsairs respect both."` |
| Ida Wickmere (`chandler`) | `"Cold-fire doesn't mind a rift storm. Buy a lantern. Or three. I'm only half joking."` | `"Sold out of wicks by midnight! Storms are good for chandlers and bad for sleep."` |
| Nell (`dockkid`, renamed from Pip) | `"The lantern-eels are going crazy! They bite more in storms. Or they're scared. Hard to tell."` | `"I caught a lantern-eel in the storm! It got away. But I caught it first. That counts."` |
| Sable's skiff (`ferry`, built in `ravenhold.js`, not `TALK`) | Ravenhold pier: `"The deckhand grins through the spray: 'Under-current's wild tonight. Hold the rail and don't look up.'"` · Bifrost landing: `"The skiff bucks on its cold-fire wake. 'Storm's pushing the current. Quick trip, rough trip. Sit low.'"` | (normal) |

**Ferry rule (lead-approved):** the skiff **still sails** during a Bifrost storm. In `openFerry()`, while `F.storm === "bifrost"`,
replace the first page with the storm line above for that side. The sail option is unchanged. After you land: toast
`A rough crossing. Your boots are wet, but you're in one piece.`

### 3.6 Bifrost Crossing

| NPC (id) | Storm line | Morning after |
|---|---|---|
| Gatewright Halvard Ness (`gatewright`) | `"Storm on the bridge. The Guild pays a quarter extra for every rift sealed tonight. The board's up."` (+ the bounty, section 5) | `"The ledger's thick this morning. Storms are bad for gates and good for Gate Runners."` |
| Halvard (second page, quiet foreshadow) | `"Storms make the gates restless. I'll be up all night with the keys. Someone has to be."` | — |
| Signe Larkspur (`denkeeper`) | `"Storm's up. The strays are under the floor again. Bring a light if you're staying."` (already in the build) | `"Every stray accounted for. Pockets slept through it, the lump. Biscuit for your pet, for bravery."` |

### 3.7 Pet storm barks

Shown once at onset and occasionally during (the same rules as other barks, `{name}` = the pet's name):

| Pet | Onset | During | Morning after |
|---|---|---|---|
| Wisp kit | `({name} flares bright blue and won't leave your shoulder.)` | `({name} hums louder with every crack, like it's arguing with the sky.)` | `({name} dozes, glowing a tired, happy blue.)` |
| Glow-moth | `({name} tucks itself into your collar.)` | `({name}'s eyespots flash violet at every crack of the sky.)` | `({name} shakes out its wings and dusts you, pleased.)` |
| Lantern-fox | `({name}'s ears flatten. The light-fish in its tail is racing.)` | `({name} points its nose. Another tear, that way!)` | `({name} sleeps with its tail over its nose. The fish sleeps too.)` |
| Moss-pup | `({name} growls at the sky, then hides behind your boot.)` | `({name} digs a little burrow and peeks out of it.)` | `({name} shakes off, spraying moss everywhere.)` |

The lantern-fox's "During" line pairs with `senseRift()`, which fires much more often in a storm.

---

## 4. Toasts the townsfolk raise (the morning after)

When `F.stormAfter` is set and you walk into these places the next day, a short **toast scene** plays once per storm. It's two
or three pages, a cozy "the whole room raises a cup" moment. If you sealed 3 or more rifts in the storm, the host adds a small gift.

| Where (trigger) | Host | Toast | Gift (3+ sealed) |
|---|---|---|---|
| Kettle & Key (talk to `innkeeper`) | Bram | `"Cups up, Lane! To the hero who walked into the storm while the rest of us hid under the stew."` · `"May the Rift stay stitched and the bread stay warm!"` | 1 Hearth tonic: `"On the house. Storms are thirsty work."` |
| Plaza (talk to `baker`) | Marla | `"To full ovens and empty skies! And to you, dear, for keeping one of them that way."` | 1 Hearthloaf (`loaf`) |
| Ravenhold Harbor (talk to `harbormaster`) | Brannoc | `"Raise your mugs, you sorry sea-dogs! To the one who sealed the sky so the boats could sleep!"` | — |
| Ravenhold Harbor (talk to `quartermaster`) | Sable | `"To the Rift that didn't eat us. And to the fool who stood in front of it. Drink up."` | +15 Black Doubloons (`MERIT.dues` scale) |
| Bifrost (talk to `gatewright`) | Halvard | `"To the ledger, and every mark in it! And to keys that stay where they're put."` | — |
| Bifrost (talk to `denkeeper`) | Signe | `"To brave pets and braver idiots. That's you. Cheers."` | 1 Den biscuit |
| Mossbrook (talk to `warden`, befriend) | Burrowmoss | `"Mushroom ale for everyone! To the big-folk who kept the rifts off our springs!"` | — |
| Hollows (talk to `gnome`) | Pipkin | `"To the storm-walker! Hip hip... (the gnomes cheer from behind every door.)"` | — |

Short UI toast after any toast scene: `Hearthmoor raised a cup to you.` / `Ravenhold raised a mug to you.` /
`The Crossing raised a glass to you.` / `Mossbrook raised a mushroom ale to you.`

---

## 5. Repeatable bounty: Storm Watch

**Overview:** the Gatekeepers' Guild posts a **Storm Watch** bounty whenever a rift storm breaks. You take it from Halvard
(or the Guild's notice board beside him), seal 3 rifts anywhere in that night's storm region, and report back. You can take it
**once per storm**. It can't fail: if dawn comes first, the rifts you sealed still count, and you report whenever you like.

### 5.1 `QUESTS` entry

```js
stormwatch: {
  title: "Storm Watch",
  giver: "Gatewright Halvard Ness",
  side: true, bounty: true,      // bounty: skips onErrand() (no Hearth Tokens) and errandsDone(); XP full once, then half
  steps: {
    1: (S) => { const n = Math.min(3, (S.storm || {}).sealed || 0);
      return n < 3 ? `Seal 3 rifts during the rift storm (${stormName(S)}). ${n}/3` : "Report to Gatewright Halvard at Bifrost Crossing."; },
    2: "Report to Gatewright Halvard at Bifrost Crossing.",
    3: "Storm Watch done. The Guild will post another when the next storm breaks.",
  },
},
```

- **`bounty` tag (lead-approved), `setQuest` change:**

```js
const B = !!QUESTS[id].bounty, kind = story ? "Story quest" : B ? "Bounty" : QUESTS[id].side ? "Side quest" : "Errand";
if (stage === 3 && was !== 3) { toast(`${kind} done: ${QUESTS[id].title}`, 2.6); G.audio.sfx("quest");
  const rep = B && (G.S.bountyDone = G.S.bountyDone || {})[id];
  G.gainXP(PR.XP.errand * (rep ? 0.5 : 1)); if (B) G.S.bountyDone[id] = (G.S.bountyDone[id] || 0) + 1;
  if (!story && !B) G.factions.onErrand(); }
// errandsDone(): also skip QUESTS[k].bounty
```

  The first Storm Watch pays the full 120 XP; every repeat pays 60. `S.bountyDone.stormwatch` counts completions.
- `stormName(S)`: `"over Bifrost Crossing"` / `"in Mossglen"` / `"in the Toadstool Hollows"` / `"in Vanaheim"`, from
  `S.storm.region`.
- Stage 1 → 2 when `S.storm.sealed >= 3` (in `rifts.close` when won, during a storm). Stage 2 → 3 at Halvard.
- **Repeat:** when a new storm starts and `quests.stormwatch === 3`, reset it to `0` so Halvard offers it again. `S.storm.sealed` resets
  at each storm's onset.

### 5.2 Halvard's lines

Offer (the storm is up and `quests.stormwatch` is 0). This is a hub option `"Any storm work?"`, plus the `quest_mark`:

```js
pages: [
  "Storm Watch, posted fresh. Seal three rifts before the storm blows out, anywhere it's raging.",
  "The Guild pays a quarter extra on every mark tonight, and a bounty on top. Go on, the keys can wait.",
],
then: (G) => { G.setQuest("stormwatch", 1); },
```

- Reminder: `["Three rifts, any tier. The board doesn't care how big, only how many. Neither do I. Much."]`
- Turn-in (stage 2):

```js
pages: [
  "Three sealed in one storm. The ledger likes you. I like the ledger. So.",
  "Bounty paid: marks, gold and a rift shard. Come back next storm. There's always a next storm.",
],
then: (G) => { G.setQuest("stormwatch", 3); G.factions.add("gate", MERIT.stormwatch, "stormwatch"); gold(G, 40); gem(G, "rift_shard");
               G.toast("+1 Rift shard (a socket gem)", 2.2); },
```

- Turn-in after 5+ sealed (an extra first page): `"Five? Six? I stopped writing and started staring. Have an extra twenty."` (+20 gold)
- No storm, `stormwatch` 0: `["No storm, no Storm Watch. Enjoy the quiet. It never lasts."]`

### 5.3 Rewards (existing scale)

| Source | Rift Marks | Other |
|---|---|---|
| Each rift sealed in a storm | `MERIT.rift[tier]` × 1.25 (× fox bonus): about **38 / 75 / 150** | the normal rift loot + half merit to the realm faction (Bifrost = Guild only) |
| **Storm Watch** bounty | **+60** (`MERIT.stormwatch = 60`) | 40 gold, 1 rift shard, (+20 gold at 5+ sealed) |
| A typical storm night (3 minor + 1 major + the bounty) | about **250** | that's most of a Guild rank at Friend → Trusted (150 → 400). Earned, but a storm night feels worth staying up for |

---

## 6. `markerFor` additions

```js
const F = S.flags || {};
if (id === "gatewright" && F.storm && !q.stormwatch) return "quest_mark";
if (id === "gatewright" && q.stormwatch === 2) return "quest_turnin";
if (id === "gatewright" && q.stormwatch === 1 && ((S.storm || {}).sealed || 0) >= 3) return "quest_turnin";
```

(Note: `F.storm` is set at Bifrost even when the storm is in a Midgard region, because the Guild posts the bounty for any storm.)

---

## 7. Save shape (summary)

| Key | Meaning |
|---|---|
| `S.flags.storm` | `"bifrost"` / `"mossglen"` / `"hollows"` / `"vanaheim"` / `null` (the build already reads `"bifrost"`) |
| `S.storm` | `{ region, day, sealed, best }`: this storm's count and your record |
| `S.flags.stormAfter` | the day a storm ended with ≥ 1 sealed (morning-after lines, toasts) |
| `S.flags.toasted` | `{ [hostId]: day }`, so each toast scene plays once per storm |
| `S.quests.stormwatch` | 0-3, reset to 0 at the next storm's onset after 3 |
| `MERIT.stormwatch` | 60 (gate) |

---

## 8. Decisions (all resolved by the lead, 2026-10-05)

1. **Storm frequency: approved.** Bifrost 1 night in 4 (after `bf_seen`), Midgard/Vanaheim world events 1 in 10.
2. **Repeat payouts: resolved.** Quests tagged `bounty: true` skip `onErrand` (no Hearth Tokens) and `errandsDone`, and the toast
   says "Bounty done". XP is full the first time and **half on repeats** (section 5.1).
3. **The skiff: resolved.** It **still sails** during storms, with a warning line on each side (section 3.5).
4. **Rift spots: the builder places them** in Bifrost and the Rift Shrine (`RIFT_AREAS`, `stormOnly`). Section 1.3 has suggestions only.
5. **The two Pips: resolved.** The Ravenhold dock kid is renamed **Nell** (`dockkid`). Pip the player keeps the name, and "Pip"
   stays a wisp-kit name.
6. **Sable's +15 Black Doubloons: kept.**
7. **Foreshadowing: both kept** (Halvard's keys, Ondra's "cold side").
8. **Storm art: as described** (the sky-crack fx reusing `rift_tear_minor`, cold-fire motes, violet/red point-light flashes, no bloom).
