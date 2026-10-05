# hd2d assemble

Scene spec (JSON) -> playable static folder + zip.

```
hd2d assemble scenes/hearthmoor-plaza.json --out demos/hearthmoor-plaza [--no-zip] [--shots]
```

- Runs palette, sprite, texel, kit, trees, particles for the scene's biome + seed into `<out>/public/art/<tool>/`.
- Builds scene pieces (slabs, terraces with stair gaps, stairs, bunting, hedges), copies the runtime, resolves markers to world space, adds auto emitters (chimney wisps, leaves, lamp bugs), bakes collision (0.25 m cells).
- Writes `scene.json`, `scene.src.json`, `README.md`, and `<out>.zip`. `--shots` runs check-scene and re-zips.
- Spec format: see `scenes/hearthmoor-plaza.json` and `scenes/bakery-lane.json` (camera, ground, slabs, terraces, stairs, buildings, props, hedges, trees, bunting, laundry, emitters, actors, player, and optional spells, spell_cycle, weather, grades). JSON only (no YAML).
- Optional `decks` [{rect, h}] add walk heights with no mesh (piers whose planks are a prop) and `blocks` [[x0, z0, x1, z1]] add blocked rects (water). Piece markers `lamp_color`, `lamp_fixed` and `lamp_range` set a piece's lamps' colour, always-on level and range (Ravenhold's cold-fire lanterns). The runtime lights only the first 7 lamps (8 without spells), so list the lamps that should cast light first.
- Spells: if `"spells": true` or any actor has `"behavior": "caster"`, it runs `hd2d spells` and adds `scene.spells`.
- Markers: `ovens` adds an oven_steam emitter; fountain `spray` adds a fountain_spray emitter whose drops land on the `water` height.
- Recipe check: plaza, 3 houses, 1 stair, 1 tree, 2-4 actors, key light + 2 lamps, props.
- `hd2d serve DIR [--port 8077]` serves a built folder.
- Game effects: a `portal_arch` prop (its `portal` marker), or any `"fx"` / `"gamefx": true` in the spec, runs `hd2d portal` and adds `scene.gamefx` + `scene.fx`.
  - Each portal marker places a `portal_vortex` billboard in the arch, a `portal_ring` decal 1.25 m in front, a sky-coloured always-on lamp (`"color"`, `"fixed"`) and fireflies with `min_gate` (they show by day too).
  - `"fx": [{"id": "petal_0", "name": "moonpetal", "pos": [x, z]}]` places persistent game effects on the heightfield (pickups and so on).
- `"game": {...}` is passed through untouched to `scene.game` (exits, portals, pickups, spawns for a game shell; see `games/hearthmoor`).
