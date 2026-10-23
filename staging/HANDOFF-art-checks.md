# Art checks before handoff (for Hearthmoor Art) - 2026-10-23

`hd2d check-sprite` now also checks every role for:
- **holes**: no enclosed transparent pockets (3 px or more) inside the opaque shape.
- **limbs**: no frame whose opaque area or bounding box is more than 25% below the role's other frames, or that splits into more separate blobs than usual.
- **outline1px**: every edge pixel is the ink outline colour (no gaps), and the outline is not doubled.
- **soft_alpha**: alpha is only 0 or 255.

Run this on every sheet you hand off (atlas PNG plus its JSON), from `/workspace/hd2d-suite`:

```
python3 bin/hd2d check-sprite <area>/public/art/sprite/<sheet>.png --json <area>/public/art/sprite/<sheet>.json --project <area>
```

Example: `python3 bin/hd2d check-sprite games/hearthmoor/areas/alfheim/public/art/sprite/pets.png --json games/hearthmoor/areas/alfheim/public/art/sprite/pets.json --project games/hearthmoor/areas/alfheim`

It must print `check-sprite: PASS` (exit code 0). Issues tagged `[holes]`, `[limbs]`, `[outline1px]` or `[soft_alpha]` come from the new checks.
Current art that already failed is listed in `tools/check-sprite/art_allowlist.txt` and only shows as a warning. Don't add new sheets
to that list. Fix the art instead, and remove a line once you've fixed that role. Branch: `checks-upgrade`.
