# Vanaheim / Mossbrook art — Hearthmoor Art batch (2026-10-28)

Everything procedural Python (src/), **0 PixelLab generations** (key never used). Palette = gloom-and-glow lock in `src/vh_pal.py`,
exposed as custom biome `vanaheim-gloom` (`src/project/public/art/palette/vanaheim-gloom/biome.json`).
Base: ink #0a0c1c, indigo #141a3a, slate #26305e/#3c4a86/#1c2248, moss #127a6e/#2aa894/#0c4a48, bark #1a1430 + violet rim #3a2a5e/#6a4aa8,
shawl #5a3c96, mist #8a9ad0, pale #c8d4f0, white #f0f6ff. Glow (glow pixels ONLY): cap magenta #ff3fb4 (+#ffa8de/#b02a80), spring cyan #3ff0ff (+#c0fcff),
firefly lime #b6ff4a, nymph violet #a45cf0 (+#d4a8ff), frost core #7fd8ff (+#e0f6ff). No browns, no bloom, no armour.

## sprite/ (20x32 frames, pivot [10,32], ground row 31, rows down/up/left/right, hd2d SP.ANIMS columns)
| file | role | anims (cols, fps) | notes |
|---|---|---|---|
| thornnymph.png/.json | enemy | idle 0-3 @3, walk 4-7 @8, attack 12-15 @10, die 24-27 @6 | corrupted spring nymph, thorn-wrapped; magenta buds pulse, violet hair glint; die slumps, buds fade, last frame cyan "freed" light |
| oldmorel.png/.json | npc (grocer) | idle @3, walk @8 | mushroom-folk, woven violet shawl, cyan gill twinkle, no armour |
| thornhex.png/.json | elite caster | idle @3, walk @8, cast 8-11 @6 | **palette remap of hd2d-suite plaza `hedgewitch.png`** (not redrawn); magenta hex band = glow |

check-sprite (`bin/hd2d check-sprite --biome vanaheim-gloom --project src/project`): all 3 PASS, 0 failures → `check_sprite_report.json`.

**Tobble** is reused as-is: `../svartalfheim_puzzles/tobble.png` + `.json` (not copied, not redrawn).

## kit/ (.glb + kit.json; previews renders/*_night.png) — src/kit_vh.py, src/gen_kit.py
- thorn_wall_s1 / s2 / s3: 2 m briar segment, heights 0.6 / 1.4 / 2.2 m, black-violet canes with violet-rim thorns, frost-blue glow core vein, lamp marker.
- frost_thorn_root_open / _retracted: weak-point root; open = peeled lips + lit frost core (`weak_point` marker), retracted = closed, thin frost seam.
- hex_knot: 0.3 m twisted black thorn with frost-blue bead (pickup).

## icons/ (16x16, items.png / draw_icons style) — src/gen_icons.py
vh_icons.png (96x16 strip, order below) + vh_icons.json + vh_icons_6x.png preview + single PNGs:
hexknot, fizzstone, tithe_seal, frost_bloom, mossheart_staff, **nettle_circlet** (Nettlecrown's Bean-Circlet: woven bean-vine crown, one frost-blue glowing bloom).
`nettle_circlet_safe.png` = twin with the bloom in mist/pale (no glow colours).

## gamefx/ (24 px cells, 8 frames, hard alpha) — src/gen_fx.py
vh_fx.png/.json + strips/: frost_sparkle (hex_knot / open root), bud_pulse (nymph motes), firefly_drift (ambient), thorn_wall_tell (violet decal line, 1 s before growth).

## Neon / palette flag (lead task)
Stock checks reject the whole gloom lock (not just glow): stock `hd2d check-sprite` (cozy-village) FAILS all 3 sprites, and
`games/hearthmoor/tests/check_palette.py --extra` FAILS vh_icons, vh_fx and even nettle_circlet_safe (indigo/teal base hexes aren't in cozy-village/NEON).
A "palette-safe twin" can't pass without dropping the Vanaheim look. Fix: register biome `vanaheim-gloom` (copy biome.json above) or allow-list these hexes, as with Helheim.
Our own audit: every pixel in every file is in the vanaheim-gloom lock.

## Known flaws
hexknot icon reads a bit boxy; staff icon thin; circlet bloom is only 2-3 px; thornhex keeps the hedgewitch silhouette (by design); kit renders are small at night.

## boss_nettlecrown (Mother Nettlecrown, the Thornhex) - DRAFT v3 for Game Director look sign-off
- sprite/boss_nettlecrown_neon.png/.json = PRIMARY look (lead chose neon). sprite/boss_nettlecrown.png/.json = palette-safe fallback.
- Layout = boss_veyra: 28 cols x 4 facings (down, up, left, right; right drawn, not mirrored), 160x200 frames, pivot (80,200), scale 5.5x.
- Slots: idle 0-3, walk 4-7, cast 8-11 (blossoms open), thorn-lash in attack slot 12-15, kneel/yield in die slot 24-27.
- Neon twin passes check-sprite and the palette check with VANA_NEON_ALLOW {#ff3fb4,#7fd8ff,#a45cf0,#3ff0ff,#b6ff4a} PLUS the vanaheim-gloom area palette (indigo-black gown #141a3a, teal under-robe #0c4a48/#127a6e). Allow entry alone is not enough. Local proof: python3 src/check_local.py.
- Previews: nettlecrown_contact_sheet.png, nettlecrown_preview.gif. Backups: *_v2.*, src/gen_nettlecrown_v2.py, src/.gen_v1_backup.py.
- Known flaws: flat sleeve slabs and stiff arms, thin kneel vines and whip in side views, safe twin low contrast, JSON description text not refreshed.
- 0 PixelLab gens for the whole batch.

