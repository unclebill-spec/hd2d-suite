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
- 1px ink outline, big readable head, hard alpha, biome palette colours only.
- 24 original roles:
  - Original set: baker, farmer, fisher, shopkeeper, kid, elder, traveler (player), florist, postie, cat.
  - New humans: blacksmith, librarian, guard, innkeeper, musician, gardener, herbalist (caster), hedgewitch (caster), fisherkid (kid layout), lamplighter.
  - New animals: dog, goat, chicken, owl.
- CAST pose (casters only, `roles_more.py: draw_cast_arms`): 4 frames (gather, raise, raised + glow, release), played as `[0,1,2,2,3,3]` at 6 fps. Roles in the JSON carry `caster` and `anims`.
- Outputs: `actors.png` + `actors.json` (frames, pivot; anims: idle 3 fps [0,1,2,1] + blink, walk 8 fps, cast 6 fps), `actors_preview_4x.png` (nearest), and per-role strips.
- New hats (helm, witch, kerchief, beret, bucket), glasses, and items (hammer, book, spear, mug, lute, watering can, sprig, staff, rod, wick) are in `roles_more.py`.
- `vendor/sprite_writer.py` + `vendor/palette_locked.py` are copies; the Gravewake originals are untouched.
- Seed deterministic. The original 10 roles' pixels are unchanged.
