# hd2d palette

Biome palettes + time-of-day grades.

```
hd2d palette --biome all --out PROJECT/public/art/palette
hd2d palette --list
```

- 5 biomes: cozy-village, meadow, harbor, autumn-orchard, snow-hamlet; 27 named colours each (16-28 rule).
- Every biome has cream plaster, timber, moss and rose/gold/blue flower accents, plus ink (outline), skin, cloth, lamp.
- Outputs per biome: `biome.json` (colors, ramps light->dark, roles, `grades.day/dusk/night`, clock stops), `<biome>.gpl` (GIMP/Aseprite), `swatch.png`, `swatch_4x.png`.
- Grades drive the runtime: sun colour/intensity/azimuth/elevation, hemi fill, fog + haze, sky gradient, lamp intensity, window emissive (orange at night), sprite tint, exposure, saturation, shadow tint.
- Deterministic (no randomness).
