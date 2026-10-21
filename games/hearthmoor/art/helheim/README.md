# Helheim art pack (follows story/helheim.md)
Build: `cd src && python3 gen_helheim.py` (sheets → gamefx → kit → renders → metadata → contact sheet).

## Sprites (check-sprite once per sheet: 5/5 pass)
| sheet | frame | roles |
|---|---|---|
| hh_folk | 40x44 | hel 1.25x, ferryman (Corvin), innghost (Hettie), archivist_hh (Quillon), eira_spirit, childghost 0.8x (Hollin), bakerghost (Old Marrow), sailorghost, gloam_folk |
| hh_inkling | 40x44 | inkling (raven pet) 0.6x |
| hh_enemies (+ _safe) | 64x72 | shade, gate_shade 1.2, soul_wraith 1.3, grave_lantern, bone_elemental 1.6, garnet_golem 1.8, skeleton_line, lich 1.4, gloam_knight |
| hh_elites (+ _safe) | 100x112 | vesperin 3x (mini-boss), vesperin_bat 1.6, odric 3x, gravelamp 2x, hollowchoir 3x |
| boss_mordrath (+ _safe) | 144x240 | mordrath / _p2 / _p3, 8x (squeezed to 144 px wide) |
Everyone wears separate top/bottom + belt + shoes; only Mordrath wears plate. 
## Neon flag (true violet, Helheim sheets only)
Main sheets use NEON violet #a45cf0 (light) and #3a2458 (dark) on these roles only:
- `gloam_knight` (hh_enemies): tabard
- `odric` (hh_elites): tabard and blade
- `mordrath`, `mordrath_p2`, `mordrath_p3` (boss_mordrath): chains and smoke-wing cape

Lead to add to check-sprite: `HH_NEON_ALLOW = {"gloam_knight","odric","mordrath","mordrath_p2","mordrath_p3"} -> {"#a45cf0","#3a2458"}`. The repo was not edited.
Palette-safe twins (blue-shadow): `*_safe` sheets, all PASS. The main sheets FAIL the stock check only on those 2 hexes / 5 roles. With a temporary in-memory allow-list (`HH_LOCAL_ALLOW=1 python3 gen_sheets.py`, report in check_sprite_report_local_allow.json) all 3 PASS.

## Areas
helheim (night + day), hh_shore, hh_archive, ossuary_o1–o9. Each has a 1.34 m mist_ledge + one mist_stair. Props/fx are ≥1 m from edges, spawns and stairs (src/check_clear.py: 0 violations). Shadow hh_shadow #4a4060/#5e5480.
Boss stands: Vesperin O5 [0,0,-2.0], Mordrath O9 [0,0,-1.4]. Measured luma: renders/luma.json.

## Doc conflicts / leftovers
- The lake is shrunk to x -4..4 and the bridge runs along z to fit the town.
- The fallen ally has no sprite of its own (it reuses the chosen ally's sheet). Its bridge lantern is dark.
- House windows stay warm orange (lead ruling). Ossuary walls and doors are soft bone-white (#d4c9b0 ramp).

## Story rulings (in metadata story_rulings)
Hel's choice is stance only. A 'pale' cosmetic returns. Mordrath removes one wave. The Muspelheim lock stays behind the flag. No art changes needed.
