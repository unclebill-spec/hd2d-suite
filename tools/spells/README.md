# hd2d spells

Cozy pixel spell effects: sprite strips, JSON presets, and cast sets. The effects are original. Ideas came from the Gravewake spell writer, which was read but never edited.

```
hd2d spells --biome cozy-village --out PROJECT/public/art/spells
```

- Cells are 32x32 with one row per effect and 6-8 frames each.
- Nearest-neighbour, hard alpha (0 or 255), and every pixel is a biome colour. Brightness comes from the palette's lightest steps and fades are dithers. No glow halos, no blur.

| effect | frames | kind | notes |
|---|---|---|---|
| sparkle_burst | 8 | billboard | star sparkles fly out from the hands |
| healing_petals | 8 | billboard, loops | rose petals spiral up around the target |
| hearth_flame | 8 | billboard, loops | small warm hearth flame |
| frost_puff | 8 | billboard | cold puff with ice glints that dithers away |
| leaf_gust | 8 | billboard | swirl of leaves on a wind streak |
| light_orb | 6 | billboard, loops, lifted 1.5 m | floating lantern orb with a pulse ring |
| rune_circle | 8 | ground decal, loops from frame 4 | gold rune ring, pre-squashed by sin 36° for the locked camera |
| bolt | 6 | projectile | spinning spark; flies to its target, then spawns `impact` |
| impact | 6 | billboard | star-burst hit |

- `spells.json` has:
  - `effects`: per-effect `row`, `frames`, `fps`, `loop`/`loops`/`loop_from`, `pivot`, `lift`, `glow` (ignores the time-of-day tint), `light` (`color`, `intensity`, `range`, per-frame `curve`, a small point-light flash), `duration`, and `speed`/`then` for projectiles.
  - `cast_sets`: what one cast spawns, and where (`feet`, `front` or `hands`). For example, `healing_petals` = rune_circle at the feet + healing_petals.
  - `cycle`: the order for the player's spell key.
- Outputs: `spells.png` (atlas), `<effect>.png` strips, `spells.json`, and `spells_contact_4x.png` (every effect, every frame, 4x nearest).
- Runtime (`engine/effects.js`):
  - Effects are screen-aligned quads in the SHARP pass: integer pixel scale, snapped anchor, texelFetch.
  - Billboards are depth-tested at their position. Decals are drawn under the actors with a constant depth.
  - Up to 2 pooled point lights follow the light curves. There is no bloom.
- Seed deterministic.
