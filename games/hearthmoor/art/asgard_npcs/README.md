# Asgard NPCs + Thunder-Rune FX — Hearthmoor Art, 2026-10-30

**Status: GD approved 2026-10-30, final.** (v2 + violet Spirit Raven approved; final pass removed the guard back-view gold tabard sides.)

Spec sources: `hearthmoor-staging/story/asgard.md` §5 roster (envoy_as = Envoy Ingrith Goldrune, quest giver as_gate/as_take; as_guard = Goldspire guard, Thunder Toll pillar guards) and §9.2 Thunder-Rune school (Rune Spear, Sky Lance, Rune Ward, Chain Rune). Style lock: `docs/HD2D_COZY_STYLE_LOCK.md`. GD direction: dark lean, neon blue/purple, gold accents only, minimal brown/beige.

## Sprites — `sprite/an_folk.png` + `an_folk.json` (480x352)
as_folk layout: 40x44 frames, 12 cols; per role 4 facing rows (down/up/left/right), idle 0-3, walk 4-7 (32 frames per role). Scale 1x (standard NPC; neither is a boss/mini).
- `as_guard` — slate tunic, dark jerkin/trousers, **dark navy tabard with a 1px gold border** (front: sides + hem; back and side views: hem only) + sky rune, navy cap w/ gold rim, cloth bracers (no armor suit), 1px spear.
- `ingrith` — icy-blue tunic (GD-confirmed), dark trousers, **ash-silver hair/braids** (white/sky/stone_lo cool ramp, navy braid ties), gold only on the circlet + 1px cloak pin; sky belt buckle; blue cloak.
Sprites are cozy-village palette only (lock has no violet for sprites); the neon read comes from paired `rune_aura_blue` (guard) / `rune_aura_violet` (Ingrith) FX drawn under them.
Checks: `hd2d check-sprite` PASS, 0 failures (`check_sprite_report.json`).

## FX — `gamefx/thunder_rune.png` + `thunder_rune.json` (384x480, 48px cells, 10 rows; strips/ per effect)
rune_spear 6f · sky_lance_mark 8f · sky_lance_bolt 8f · rune_ward 8f · chain_rune 8f · rune_glyph_pulse 8f · rune_sparkles 8f · impact_flash 6f · rune_aura_blue 8f (loop) · rune_aura_violet 8f (loop). `cast_sets` in json chains mark→bolt→impact etc. Chain rune / sparkles / impact reuse fx-library hm sources.
Checks: palette — `tests/check_palette.py --extra` 0 failing; alpha {0,255} only; 10 colours all in NEON/gold/ink effect set (`gamefx/palette_check.json`). check-sprite (`gamefx/check_sprite.txt`) flags neon colours as off cozy-village — expected for effects, same as all fx-library packs (alpha+palette are binding for fx).
sky_lance_bolt intentionally touches the cell top (falls from sky).

## v2 pass (GD review 2026-10-30)
FX approved unchanged. Sprites: v1 kept as `sprite/an_folk_v1.png/.json`; `before_after.png` shows v1|v2 per facing. Gold px per frame now: guard 27/23/12/12 (down/up/left/right), Ingrith 10/0/8/8 (was 22+ incl. hair). check-sprite PASS (0 failures); `tests/check_palette.py --extra` 0 failing. Generator edits: `src/gen_npcs.py` (tabard, hair, buckle, braid_tie) and `src/as_giant.py` (braid tie colour is now a param); v1 copies `src/*_v1.py`.

## Final pass (GD 2026-10-30)
Guard back (up) view: gold tabard side borders removed, hem kept (same as side views). Gold px guard up 23 → 7; only guard up row changed (128 px). v2 kept as `sprite/an_folk_v2.png/.json`, `src/gen_npcs_v2.py`; `before_after.png` now shows v2 | final. check-sprite PASS (0 failures); check_palette 0 failing.

## Install notes for the lead (don't apply from here; repo untouched)
- GD 2026-10-30: **`an_folk` ingrith replaces `envoy_as` in `as_folk`** (same 40x44 as_folk layout, idle 0-3 / walk 4-7, 4 facing rows): copy ingrith rows from `sprite/an_folk.png` into the envoy_as rows and keep the envoy_as id (or remap the id to `ingrith`). `as_guard` rows install the same way.
- Pair: as_guard + `thunder_rune:rune_aura_blue`, ingrith + `rune_aura_violet`.
- Older `asgard_extra/sprite/ax_folk.*` archived to `asgard_extra/sprite/_archive/`.
- **Spirit Raven**: reuse Sigrun `raven_guard` (`art/asgard/gamefx/as_fx.json` row 34, `strips/raven_guard.png`). Its ravens were warm grey #9c8e7a (off the dark/neon lean), so a tinted copy is staged: `gamefx/spirit_raven.png/.json` (8f, 48px, loop; ravens → violet #a45cf0, blue ring kept). Palette check 0 failing, alpha {0,255}.

## Open questions
1. ~~asgard.md §5 Ingrith look~~ RESOLVED: story §5 now has icy-blue tunic + ash-silver hair (GD 2026-10-30).

Previews: `contact_sheet.png`, `preview.gif`. Generators: `src/gen_npcs.py`, `src/gen_thunder_rune.py`, `src/contact.py`. PixelLab: 0 gens.
