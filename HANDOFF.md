# HANDOFF — Hearthmoor

## RESUME HERE
- Live: https://unclebill-spec.github.io/hd2d-suite/games/hearthmoor/ (publish ONLY via `/workspace/tools/publish-game.sh hearthmoor`, `--no-push` dry run first — rule 34)
- Pending merge: hearthmoor-menu-restyle 04adc1c (verdict: /workspace/.hm-logs/menu/rerun/VERDICT.md, no open regressions); hearthmoor-mp-frostfriend a908069 (Muspelheim 1.1 fixes; needs smoke_muspelheim + check-scene)
- Open bugs (pre-existing, not menu): check-scene fails in barrow, barrow2, clockdeep, ossuary, prismvault, caldera2, jt_hall, lumen_court; ossuary2 667x375 overlap (31 px)
- Merge queue: Story's vanaheim.md (Mossbrook / Tobble / Mother Nettlecrown; game/vanaheim.js needs data.js `allyCount`, verdant_heart `yieldAt`, `G.startBoss`; open questions at doc bottom); ambient_barks.md; Niflheim-side frost-friend lock (smoke_niflheim l.136); Kindle/Hrefna optional lines; checks-upgrade (69f898c, unmerged)
- NEXT ACTION: build the next realm, Vanaheim, from vanaheim.md.

Balance numbers: games/hearthmoor/BALANCE.md. Design: docs/HEARTHMOOR_BUILDER_HANDOFF.md.
