# hd2d texel

Chunky palette-snapped tileable world textures (32 / 64 px).

```
hd2d texel --biome cozy-village --sizes 32,64 --out PROJECT/public/art/texel
```

- Kinds: cobble, brick, timber, thatch, plaster, moss, roof (shingle), dirt (path), grass, stone, awning.
- Reuses the Gravewake pixel writer (copied into vendor/) for seeded noise; structure first, then noise.
- Every pixel is a biome colour; every texture wraps. `texel.json` records metres-per-tile for UV scale; `texel_sheet.png` preview.
- World textures can be mipmapped (sprites never are).
