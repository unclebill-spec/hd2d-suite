# hd2d portal

Game effect art (original pixel art, biome palette only, 48 px cells, hard alpha). Same JSON format as `hd2d spells`, so the runtime's Effects class plays it as `scene.gamefx`.

```
hd2d portal --biome cozy-village --out PROJECT/public/art/gamefx
```

- `portal_vortex` (billboard, 8 frames): a two-arm log spiral winding into a deep core. The rim frays into leafy wisps and gold glints orbit it. It fits inside the `portal_arch` opening.
- `portal_ring` (ground decal, 8 frames, pre-squashed): a moss-green ring with rotating sky-blue rune dashes and four pulsing gold leaf glyphs. It sits under props and actors (decal depth).
- `moonpetal` (billboard, 4 frames): a glade herb pickup with a glint that circles it.
- `quest_mark` / `quest_turnin` (billboards lifted over a head, 4-frame bob): parchment tags, "!" for an errand and a gold star for a delivery.
- `rift_vortex` / `rift_seal_<violet|blue|red>` (Rift Shrine) and, for Bifrost Crossing, `rift_seal_<gold|ice|amber|rose|rainbow>`: the same sealed swirl with a lock rune in biome-palette lights (`SEAL_HUES`); Midgard's rainbow rim turns through the seven bridge bands.
- Style references: the rift refs (swirling vortexes, stone-arch gates, a flame ring) were looked at for ideas only. Nothing was traced or copied, and the palette is this biome's cozy one.
- Writes `gamefx.png`, `gamefx.json` and `gamefx_contact_4x.png`. check-scene's `gamefx_sharp` verifies it in-engine.
