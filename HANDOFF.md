# HANDOFF — Hearthmoor

## RESUME HERE
- 2026-11-02 20:04 ET (HD-2D Cozy Builder): branch hearthmoor-tue-1103 has the 1102 swap-list art + Vine Grasp / Moss Golem / Foresight Charm wiring and the boot-counter merge. NOT merged to main. Open: hm_fx (fx-library) and group C neon twins not wired; check_palette.patch does not apply; moss_golem_glow adds 5 palette FAILs (needs allow rows); untested in-browser.
- 2026-11-02 20:08 ET (HD-2D Cozy Builder): GD calls applied: Moss Golem = own Growth III spell (Burrowmoss, Lv10 + Embassy 2); Vine Grasp spec numbers, Burrowmoss teaches at vh_hex 3; Foresight from both Bloomtide games is TODO(vh_stars); gr_ii Moss Ward missing (TODO); palette allow rows wait on Art rebased patch; music_asgard reverted to live.
- Live: https://unclebill-spec.github.io/hd2d-suite/games/hearthmoor/ (publish ONLY via `/workspace/tools/publish-game.sh hearthmoor`, `--no-push` dry run first — rule 34)
- Live (main): 4532c6e (rollback point ca3ef0b). Pending merge: hearthmoor-harness-1030 (test/harness + Factions selected-row edge fix; pushed, NOT live). Earlier branches (menu-restyle, mp-frostfriend, stagea-1028, fun2) are merged and live.
- Open bugs (pre-existing, not menu): check-scene fails in barrow, barrow2, clockdeep, ossuary, prismvault, caldera2, jt_hall, lumen_court; ossuary2 667x375 overlap (31 px)
- Merge queue: Story's vanaheim.md (Mossbrook / Tobble / Mother Nettlecrown; game/vanaheim.js needs data.js `allyCount`, verdant_heart `yieldAt`, `G.startBoss`; open questions at doc bottom); ambient_barks.md; Kindle/Hrefna optional lines; checks-upgrade (69f898c, unmerged)
- NEXT ACTION: #2 Helheim finish, then #3 Asgard (see games/hearthmoor/HANDOFF.md RESUME HERE).

Balance numbers: games/hearthmoor/BALANCE.md. Design: docs/HEARTHMOOR_BUILDER_HANDOFF.md.
