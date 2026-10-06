# hd2d sprite

HD-2D pixel actor writer. It extends the Gravewake sprite writer; the original is copied into vendor/.

```
hd2d sprite --biome cozy-village --roles all --out PROJECT/public/art/sprite
hd2d sprite --roles herbalist,dog --name newroles --out /tmp/x
hd2d sprite --list
```

- Frames:
  - 20x32 native frames with a feet pivot at [10,32].
  - Rows are the 4 facings (down, up, left, right). Columns are idle0-3, walk0-3 and, for magic users only, cast0-3 (12 columns, 240 px wide).
  - Hero classes add attack0-3, defend0-3 and jump0-3 (24 columns, 480 px wide; see below). An atlas is as wide as its widest role.
- 1px ink outline, big readable head, hard alpha, biome palette colours only.
- 24 original roles:
  - Original set: baker, farmer, fisher, shopkeeper, kid, elder, traveler (player), florist, postie, cat.
  - New humans: blacksmith, librarian, guard, innkeeper, musician, gardener, herbalist (caster), hedgewitch (caster), fisherkid (kid layout), lamplighter.
  - Named (only when a spec lists them): gnome, corsair (Sable), gatewright (Gatewright Halvard Ness, Bifrost: sky-blue guild coat, collar, dark belt, charcoal trousers, tan boots, `keystaff` item).
  - New animals: dog, goat, chicken, owl.
- CAST pose (casters only, `roles_more.py: draw_cast_arms`): 4 frames (gather, raise, raised + glow, release), played as `[0,1,2,2,3,3]` at 6 fps. Roles in the JSON carry `caster` and `anims`.
- Outputs: `actors.png` + `actors.json` (frames, pivot; anims: idle 3 fps [0,1,2,1] + blink, walk 8 fps, cast 6 fps, hero-only attack 10 fps / defend / jump), `actors_preview_4x.png` (nearest), and per-role strips.
- New hats (helm, witch, kerchief, beret, bucket), glasses, and items (hammer, book, spear, mug, lute, watering can, sprig, staff, rod, wick) are in `roles_more.py`.
- `vendor/sprite_writer.py` + `vendor/palette_locked.py` are copies; the Gravewake originals are untouched.
- Seed deterministic. The original 10 roles' pixels are unchanged.

## Hero classes (Hearthmoor, Norse Nine Realms): `roles_heroes.py`

There are six playable classes; `--roles heroes` selects them. All are original designs. The descriptions live in `roles_heroes.py`, and the story is in `docs/story/STORY_SEEDS.md`.

| role | class (origin) | read at 1x |
|---|---|---|
| `wildcaller` | Wildcaller (Midgard farmhand, mortal) | blond mop, rust tunic, rolled sleeves, satchel, long hoe |
| `runeguard` | Runeguard (Shield-warden, mortal brawler) | chestnut braids, grey mail sleeves, tan tabard to the hip, dark belt, brown trousers, boots, round shield with a light rune, axe |
| `seer` | Seer (Rune-reader, mortal) | grey hood, short pale-grey tunic-robe with a rune-blue sash, dark trousers, tan shoes, stitched back rune, rune-stone pouch, rune staff |
| `stormborn` | Stormborn (Child of thunder, demigod brawler) | `broad` build, storm-blue cloak, silver circlet, stone war-hammer |
| `grovekeeper` | Grovekeeper (Child of the Vanir, demigod) | moss-green hair, flower crown, leaf mantle, cream blouse, dark belt, green skirt, mushroom charms |
| `cinderknight` | Cinderknight (Ember-born, demigod brawler) | `broad` ember-red jerkin over a pale collar, one small pauldron, belt with a glowing ember buckle, charcoal trousers, brown boots, flame-tuft hair, ash cheek marks and hands, greatsword with an ember edge |

Clothing rule (style lock): every human has a separate top and bottom in different values, a darker waist band, a leg split and shoes that contrast with the trousers. Spec keys: `belt` / `sash` colours (a `belt` on a `skirt` role cinches the skirt top), `belt_w` (2 = broad belt), `tunic` (rows of the top below the waist), `collar`, `suspenders`, `tabard` (a panel ending at the belt), `cloak_short` (the cloak / robe ends at the waist).

### Hero action sets (all four facings: down, up, left; right is the mirrored left)

Hero strips are 24 columns: idle 0–3, walk 4–7, then four 4-frame actions. Villager strips stay 12 columns, and the atlas is as wide as its widest role.

| anim | cols | frames | what it shows |
|---|---|---|---|
| `cast` | 8–11 | gather, raise, release, recover | a spell with crisp glow pixels (reuses each class glow) |
| `attack` | 12–15 | wind-up, swing, impact, follow-through | a melee hit with the class weapon, solid swoosh trail pixels |
| `defend` | 16–19 | raise, set, hold a, hold b | a guard pose; the engine loops 2/3 while the guard is held |
| `jump` | 20–23 | crouch, launch, airborne, land | feet stay on the frame's ground row; the runtime adds the arc height (shadow stays on the ground). Land adds two dust pixels |

| hero | cast | attack | defend |
|---|---|---|---|
| Wildcaller | hoe planted, the free hand lifts a warm hearth-light orb | hoe raise / over the shoulder / chop / dust and sprout | small hearth ward glyph in front of the hands |
| Runeguard | axe to the sky, a light rune blazes above it, radiance falls | brace / axe high / chop / shield bash with the rune flaring | shield up and centred, its rune glowing |
| Seer | staff raised, a rune glyph forms and flies off | staff wind-up / level sweep / rune-tipped thrust / recover | blue rune ward glyph |
| Stormborn | hammer up, lightning forks | wind-up / side swing / low follow-through with ground sparks / recover crackling | hammer held crosswise, sparks on the head |
| Grovekeeper | hands gather, a neon-green ring blooms | vine lash (her weapon is the vine) | green Vanir ward glyph |
| Cinderknight | blade planted, the free palm calls an ember flame, aura rises | raise / overhead / ember slash arc / flame aura | greatsword held crosswise, ember edge lit |

- From behind (`up`), wards are hidden by the body, so casters show the guard as glow at the hands only.
- The palette caps hold: Wildcaller stays at 20 colours (the hearth orb and ward reuse lamp / flower-gold / white).
- **Frames:** villager-identical frame spec (20x32, pivot bottom-centre, hard alpha, 1 px ink outline). The idle and walk columns, and all 24 villager roles, are pixel-identical to the previous build.
- **JSON:** each hero's role carries `hero: true`, `cls`, `origin` (mortal / demigod), `style` (caster / brawler) and `anims` = idle, walk, cast, attack, defend, jump. `meta.anims` gives each anim's start column, count, fps / loop, plus `defend.hold` = [2, 3] and `jump.phases`.
- **Glow:** palette pixels only, with no semi-transparency and no bloom. The ink outline wraps every spark.
- **Lineup:** `--lineup PATH` writes a labelled 4x nearest sheet. Each role is a column showing idle down / up / left / right, a walk frame and an action frame; the action row sits on a dusk panel.
  - `hd2d sprite --roles heroes --out /tmp/h --lineup docs/screenshots/hero_origins_4x.png`
- **Action sheet:** `--anim-lineup PATH [--anim-facing down|up|left|right]` writes a 4x sheet with rows cast / attack / defend / jump, all 4 frames per hero, on a dark panel. The jump row previews the runtime arc (sheet-only lift + ground shadow).
  - `hd2d sprite --roles heroes --out /tmp/h --anim-lineup docs/screenshots/hero_anims_4x.png` (also `hero_anims_side_4x.png` with `--anim-facing left` and `hero_anims_up_4x.png` with `up`)
- **Runtime:** `engine/sprites.js` `Actors.act(a, name, {hold, dur})` / `release(a, name)`; see AGENTS.md for keys and the `window.__hd2d.act` API.
