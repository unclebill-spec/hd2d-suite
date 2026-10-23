# hd2d check-sprite

PIL checker for sprite atlases. Exit 0 = pass, 1 = fail.

```
hd2d check-sprite PROJECT/public/art/sprite/actors.png --biome cozy-village --report report.json
```

Per role / frame it checks:
- alpha: 0 or 255 only (no semi-transparent pixels)
- palette: colours come from the biome palette; colour count per role <= --max-colors (20)
- outline: silhouette edge pixels are ink
- frames/facings: 4 facings x the frames of every anim the role lists in its JSON (idle + walk = 8; casters add cast = 12; heroes add cast, attack, defend, jump = 24), non-empty, facings differ, and in every facing each extra anim's frame 1 differs from idle
- size bounds: humans 14-24 px wide (about 16-24; profiles and kids narrower), 24-40 px tall; creatures smaller
- feet anchor: the lowest opaque row is the ground row in every frame and the feet centre is within 2 px of the pivot x

## Art checks (checks-upgrade, 2026-10-23)
Also run per role (`art_checks.py`): `holes` (enclosed transparent pockets >= 3 px), `limbs` (frame area or bbox < 75% of the role's
median frame, or more disconnected blobs than usual), `outline1px` (edge pixels must be ink: no gaps; no doubled ink outline, >15% of edge),
`soft_alpha` (alpha 0/255 only). Known exceptions: `art_allowlist.txt` (`atlas_relpath::role::check`), reported as warnings.
Tests: `python3 tools/check-sprite/test_art_checks.py`.
