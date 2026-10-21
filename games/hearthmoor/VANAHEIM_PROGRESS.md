# Vanaheim realm: progress audit (2026-10-21, branch realm-vanaheim off origin/main 32b2fe4)

## Already on main
- Areas: `areas/vanaheim` (Mossbrook Springs hub, src `areas/src/vanaheim.json`), `areas/rotwood` (Rotwood Hollow, 8 rooms, Blight Regent), `areas/verdant` (Verdant Heart, 6 rooms, Thornmother, Hjortur). Built in 319c38c / 0ad02da (stage 6.4).
- Logic: `game/verdant.js` + `game/data.js` (Elder Burrowmoss befriend/conquer, Violet Spring, rw_/vh_ quests, ripple follow-ups), `game/rifts.js` pools, `factions.js` (`REALM.vanaheim`, `VANAHEIM_AREAS = {vanaheim, rotwood, verdant}`).
- Asgard mood hooks: present in `game/asgard.js` (`vanaCold`, `VANA_MUL` +20 % prices in VANAHEIM_AREAS while `realm_mood.vanaheim < 0`; withheld quest = Mossbrook apology letter; gift restores mood; `moodDown(S,'vanaheim')` on Asgard befriend). Covered by tests/smoke_asgard.py.
- Smoke: covered by smoke.py step J (no smoke_vanaheim.py). Prior check_scene pass: /workspace/.hm-logs/cs_vanaheim.pass.
- Dungeon story doc: /workspace/hearthmoor-staging/story/verdant_heart.md (already implemented).

## Missing
- `game/vanaheim.js` (realm module in the asgard.js shape).
- Story doc `/workspace/hearthmoor-staging/story/vanaheim.md`; no Vanaheim doc in `docs/story/` either.
- Art pack `/workspace/hearthmoor-staging/art/vanaheim*` (hence no installer).
- `tests/smoke_vanaheim.py`.

## Status
STOPPED before step 2: story doc and art pack are missing, so no new realm content was invented.
