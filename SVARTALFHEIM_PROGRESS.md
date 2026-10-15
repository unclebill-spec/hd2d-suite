# Svartalfheim (realm-svartalfheim) progress

RESUME HERE (Oct 15, 2026, chunk 1 DONE: `svartalfheim` area passes check_scene --quick, all 11 checks; result /workspace/alf_qa/sv1_b.txt; shots /workspace/alf_qa/sv/svartalfheim/): worktree /workspace/hd2d-svartalfheim, branch realm-svartalfheim from main 3b3fb0e.
Done: art pack copied to games/hearthmoor/art/svartalfheim/; check-sprite allow-list (SVART_NEON_ALLOW: pet_tick, dagna only);
tools/hearthmoor/svart_art.py (additive, idempotent, never deletes); first area `svartalfheim` (Anvildeep: Copper Row) spec at
areas/src/svartalfheim.json, built with `HM_BUILD_TMP=/tmp/sv_hmbuild python3 build.py --areas svartalfheim --no-zip`, then
`python3 tools/hearthmoor/svart_art.py`, then `cd games/hearthmoor && python3 -c "import build; build.write_pwa()"`.
Check: `HD2D_USER_DATA_DIR=/workspace/alf_qa/chrome-profile-cs flock /workspace/.hm-logs/browser-mb.lock python3 tools/check-scene/check_scene.py games/hearthmoor --scene-dir areas/svartalfheim --params "area=svartalfheim&qa" --quick --out /workspace/alf_qa/sv/svartalfheim`
Next (chunk 2): forge_hall, glowmines, clockdeep specs; game/svartalfheim.js (quests, TALK, shops, gate at Bifrost, alliance lock, Dagna, Tick,
Forgefire Week, soot/tremor weather); exits + Copper Gate portal once forge_hall / glowmines exist (the hub has no exits/portals yet: they would
point at areas that are not built); Tick needs PET_ROLES + pets.js entry (art in art/svartalfheim/tick/); big sheets (rares, foreman, Gorrak) per area.

## Areas the story calls for (section 2.1; REALM embassy; SKY deep except clockdeep = none)
| id | name | kind | status |
|---|---|---|---|
| svartalfheim | Anvildeep: Copper Row | city hub | chunk 1 (this file's area) |
| forge_hall | The Great Forge | city | todo |
| glowmines | The Amethyst Mines | wild | todo |
| clockdeep | The Clockwork Deep (9 rooms C0-C8, boss Gorrak Ironmaw) | dungeon | todo |

## Deviations from the story's suggested positions (check-scene rules, not story changes)
- Spawn `from_bifrost`/`start` is [1.6, 5.0] (story: [0, 9.2]): the Copper Gate arch at [0, 10.6] would stand in front of the player (x-ray dither
  fails sprites_sharp), and x 1.6 keeps the feet off the slab edge (Alfheim pitfall). Brokk stands in front of his stall for the same reason.
- Chasm rail row is a 1.2 m raised terrace with a 3 m stair at x 0 (height check >= 1 m); the hall stair / mine lift spots are on it, unwired.
- Stand-in base roles are re-pointed to the art pack by svart_art.py: lanternseller=Tansy (tinker), wispcatcher=Kesh (minerunner),
  poolkeeper=Haldis (poolkeeper_sv), elffolk/elffolk2 = dwarf / dark-elf folk (dw1 / sv1).

## Open questions hit (not answered here; nothing invented)
Story section 15 (open, Cozy Builder settling):
1. A mirror contract for Alfheim? (befriend Svartalfheim first locks Alfheim's befriend path; should Alfheim get a "hired" path into the Prism Vault?) Affects the alliance lock in game/svartalfheim.js, not the area builds.
2. Companions active at once (Dagna + Tobble when conquering Alfheim): is it 1 active? Affects the Dagna companion work, not the area builds.
Art README questions (art seat to Cozy Builder): (1) swap dwarf hammers for picks / tongs / chisels though they pass check-sprite; (2) Tick pulse shape "tick" vs "sine" in pets.js; (3) Dagna ships neon-red ember (dagna_neon.png) or palette only; (4) Gorrak's x3 red pool vs a dedicated gorrak_aura.
Chunk 1 uses the palette-safe sheets only (svart_npcs, dagna.png, deep_enemies): no dependence on 1-4; the allow-list entries are in for the neon twins.
