# Alfheim realm (branch `realm-alfheim`)

Lumenvale Glade + the Prism Vault, wired to Alfheim's sealed arch at Bifrost Crossing. Built by the Grok Bot executor
for HD-2D Cozy Builder to merge (Cozy Builder owns main, the full build, the full test and publishing).

## What's in it
- **Areas** (`games/hearthmoor/areas/src/alfheim.json`, `prismvault.json`; built output in `areas/alfheim/`, `areas/prismvault/`)
  - *Lumenvale Glade*: the arrival arch (violet swirl, SW) back to Bifrost; Lumenvale on a 1.8 m north terrace (2 elf
    treehouses, the moon well, lumen trees, orb lanterns, banners; Warden Aelindra Starwell, Thalion Duskbough, Nyssa
    Glimmerfold, Pip); a glade of prism crystals with prism shards, neon wisps, a crystal golem, a Mirror Duelist, a
    night wisp; the Prism Vault door (E) guarded by **the Prism Colossus** (mini-boss, ~2.5x, native boss sheet 50x80).
  - *The Prism Vault*: a dark crystal hall (3.6 m walls, violet-banded pillars), shards + a wisp + two Mirror Duelists,
    **Lady Sylvaine** (boss, 5x, native boss sheet 100x160) before her crystal throne; the swirl at the south door leads out.
- **Game** (`game/alfheim.js`): enemy stats/spawns/XP, talk, story quest *The Thief of Light*, quest tags, faction realm
  (Embassy merit), glow pools; merged into the shared tables at import. Gate rule: Alfheim's arch opens when
  `factions.rank('gate') >= 3` (bifrost.js GATES), or `S.flags.alf_key`, or `S.flags.alliance.alfheim`, or `?alfheim`.
  - Sylvaine: every 3rd swing is a wave + **drain nova** (spells + charms on 4 s cooldown, she heals 2%), prism bolts at
    range, two Mirror Duelists at half HP, `S.flags.alf_sylvaine` on her fall. Mirror Duelists can blink behind you when hit.
- **Tools**: `tools/kit/kit_alfheim.py`, `tools/portal/portal_alfheim.py` (rift_vortex_violet, prism_swirl, prism_ring),
  `tools/spells/spells_alfheim.py` (prism_bolt, prism_pop, drain_nova), `tools/sprite/roles_alfheim.py` (4 elves,
  4 enemies), `tools/sprite/boss_alfheim.py` (prismcolossus, sylvaine).
- **Tests**: `tests/smoke_alfheim.py` (standalone, or called from smoke.py in its own context).

## Shared-file hooks (all marked `[ALFHEIM]`)
game.js (import, AREAS, G.alfheim, detach/attach, update, AREA_NAME), data.js (MARKER_HOOKS + 1 loop line), glow.js
(GLOW_TABLES export), build.py (AREAS), tests/smoke.py (one try-block), tools/kit/kit.py, tools/portal/portal.py,
tools/spells/spells.py, tools/sprite/sprite.py (roles + elf ears), tools/sprite/boss_sheet.py.

## Merge notes
- Run the full `build.py` after merging: the new kit pieces / effects / roles are in the shared tool tables, so every
  area's atlases change slightly, and **bifrost needs the rebuild** to get `rift_vortex_violet` on Alfheim's arch (until
  then the open arch uses the cold `rift_vortex`). `sw.js` + the zip must be regenerated (this branch only built its
  two areas, via an isolated `/tmp/alfheim_build`).
- Bifrost's `from_alfheim` spawn is patched at runtime by alfheim.js (bifrost.json is untouched).
