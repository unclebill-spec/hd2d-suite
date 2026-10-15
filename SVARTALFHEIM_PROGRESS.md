# Svartalfheim (realm-svartalfheim) progress

RESUME HERE (Oct 15, chunk 6 DONE, partly): game/svartalfheim.js now has ENEMIES (forgeconstruct, sparkgolem, sootling, shadowsmith, hushblade, cavegolem), XP, MERIT keys, REALM, WAYS.svartalfheim, ITEMS (forge_seal etc., reused icons), SHOPS.tinker (Tansy opens it), TALK.tansy / TALK.brokk, SPAWNS.glowmines (7 strays), the Forge-Seal lock on forge_hall's lift (exit to clockdeep only while S.inv.forge_seal; look spot with the story line; QA ?svq=seal), qa(), tests/smoke_svartalfheim.py (PASS 6/6; not yet hooked into smoke.py). forge_hall check_scene --quick PASS. glowmines check FAILED only the phone sprites_sharp on gm_soot0 (behind neon_mushrooms_violet [-6.0,-8.4]); that spawn was removed and glowmines was NOT re-checked (run svx.sh glowmines glowmines first; or re-add a sootling at about [-3.4,-9.6]). Left: every quest (all hang off the Thane's alliance choice / section 15), how the Forge-Seal is earned, Brokk's own stall, glowmines rares (basilisk, sootcolossus need big sheets) and rift spots, Gorrak + boss sheets, Dagna / Tick, Bifrost gate + Copper Gate portal, alliance lock, C-room mechanics, Forgefire Week, merge main + check_all --lowres. Section 15 still open.
RESUME HERE (Oct 15, chunk 5 DONE): the Clockwork Deep is two areas, all PASS check_scene --quick: `clockdeep` (C0-C3, z 38..-20) and `clockdeep2` (C4 Assembly Line floor 0, C5 Frost Bell 1.2 via stair, C6 Switchyard 1.2, C7 Bellows Bridge 2.4 via stair, C8 Binding Forge round arena 2.4 with anvil_pillar at [0,-30], 4 rune-anvils + 4 quench tanks on the rim; NO fight, spawn 'boss' [0,-24]). Split because C0-C8 in one hall would be ~145 m (the vault is ~97 m). Links: clockdeep north exit [-1.5,-19.6,1.5,-18.4] -> clockdeep2 spawn from_c3; clockdeep2 south exit [-1.5,42.6,1.5,43.8] -> clockdeep spawn from_c4 [0,-16.4]. Forge lift -> clockdeep spawn from_forge (open for now; story gates it with the Forge-Seal). Results: /workspace/alf_qa/sv5_cd2.txt, sv5_cd.txt. Areas now built: svartalfheim, forge_hall, glowmines, clockdeep, clockdeep2 (all 4 story areas + the split). Next: the realm game module (game/svartalfheim.js: quests, TALK, shops, Forge-Seal gate, Bifrost gate + Copper Gate portal, alliance lock), Dagna / Tick, enemies + rift + rare tables, Gorrak boss + fight (big sheets: runaway, basilisk, colossus, foreman, gorrak), the C-room mechanics (gear / rail puzzles, steam vents, bellows gusts, thaw), smoke_svartalfheim.py, full check_all --lowres after merging main. Section 15 questions still open (not answered).
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
| forge_hall | The Great Forge | city | chunk 2, passes |
| glowmines | The Amethyst Mines | wild | chunk 3, passes |
| clockdeep + clockdeep2 | The Clockwork Deep (9 rooms C0-C8, boss Gorrak Ironmaw) | dungeon | C0-C3 / C4-C8 built + pass; boss fight todo |

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
