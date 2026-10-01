# hd2d trees

Layered-card trees (brileta canopy art, MIT) + low-poly canopy option.

```
hd2d trees --biome cozy-village --out PROJECT/public/art/trees --count 3
```

- Each tree: trunk .glb + 3 canopy cards (back / mid / front, depth-offset, tilted toward the camera), hard alpha, biome ramp.
- `brileta_dump.mjs` renders canopies with the vendored brileta-sprites dist (`vendor/brileta-dist`, MIT LICENSE included), then hard-edge snapping as in Gravewake's make_gravewake.mjs.
- Also `<tree>_lowpoly.glb` (faceted canopy), `trees.json`, `trees_preview.png`, `CREDITS.txt`.
- Needs Node 20+ on PATH.
