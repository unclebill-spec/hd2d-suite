# Hearthmoor

A first small playable cozy HD-2D game on the hd2d-suite runtime. It has three areas (Hearthmoor Plaza, Bakery Lane, and Mossglen through the moss gate) and three errands, plus a quest log, bag, dialogue, real-time day/dusk/night, charms, save/load and PWA. It plays with keyboard + mouse, touch (floating stick, tap-to-walk, pinch) and a Bluetooth/USB controller (standard mapping), all at once.

```
./startup.sh                     # serves this folder on http://0.0.0.0:8080/
python3 tests/smoke.py           # headless end-to-end playthrough
python3 build.py                 # rebuild from areas/src/*.json (needs /workspace/hd2d-suite)
```

See `RESTORE.md` for identity, controls, key files and the do-not-regress list. Zip: `../hearthmoor.zip`.
QA shots: `shots/<area>/` (check-scene: day / dusk / night, effects, gamefx, phone portrait / landscape) and `tests/shots/` (smoke playthrough).

## Known limitations

- Tested headless only (Chromium + SwiftShader, desktop and emulated phones). There has been no real GPU or real phone run, and the procedural audio has never been listened to.
- One save slot. Plaza and Lane reuse the demo layouts (they mirror each other), and Mossglen is one screen of glade.
- NPCs wander or stand; they have no daily schedules. Pudding follows in straight lines with wall sliding and hops to you if she falls far behind.
- Dialogue is linear (no choices). The errands have a single path and no fail states.
- The first visit with the service worker precaches about 12 MB for offline play.
- Distant backdrop hills are simple domes. Tall portrait views see more of them.
- The controller was tested only with a stubbed `navigator.getGamepads()` (standard mapping), not a real Bluetooth pad. Browsers only list a pad after its first button press, and some (Firefox, Safari) expose the Gamepad API only on secure origins (https or localhost), so over plain `http://<LAN-ip>:8080` a controller may not show up there.
- Non-standard controller mappings are read as if they were standard (a pad with odd button order may need remapping, which isn't offered yet).
