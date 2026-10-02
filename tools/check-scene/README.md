# hd2d check-scene

Headless scene QA (Playwright Chromium + SwiftShader). Exit 0 = pass.

```
hd2d check-scene demos/hearthmoor-plaza [--out DIR] [--size 1280x720] [--no-phone]
hd2d check-scene games/hearthmoor --scene-dir areas/mossglen --params "area=mossglen&qa"   # one area of a game
```

- Shoots day / dusk / night (`?freeze&shot&hud=0`, simulation held during capture) to `<out>/{day,dusk,night}.png` plus `sprites_<time>_2x.png` crop strips.
- sprites_sharp: each actor crop must be uniform k x k blocks (>= 97%) and correlate (>= 0.85) with its source atlas frame. Verified to FAIL on a 0.8 px Gaussian blur or bilinear rescale. It is measured on a clean capture of the same frozen frame with particles and spell effects hidden, so a passing firefly can't fail an actor. The saved shot keeps everything, and the bloom/colour/grade checks use it.
- effects_sharp (scenes with spells): every effect is laid out frozen mid-animation in a grid in front of the camera, with actors hidden. Each crop must be uniform k x k blocks (>= 97%) and correlate (>= 0.85) with its spells-atlas frame, and the frame must stay under the no-bloom limits. Writes `effects.png` and `effects_2x.png`.
- camera_locked: quaternion, fov and view direction identical after arrow/WASD keys, left drag, right drag, tap and wheel; zoom stays in limits.
- no_bloom: near-white < 0.4%, clipped channel < 2%, bright area < 3%.
- height: walk heightfield range >= 1 m and world Y extent >= 4 m.
- colours: 300-12000 5-bit colours per frame; sprite crops keep <= 2x their source colours.
- grades: dusk bluer than day, night < 65% day luma with warm window/lamp pixels.
- no_errors: no JS errors. Writes `check_scene.json`.
- gamefx_sharp (scenes with `gamefx`): the same frozen-lineup test for the game effects atlas (portal vortex, portal ring, moonpetal, quest tags). Writes `gamefx.png`.
- actions (engines exposing `window.__hd2d.act`): with the simulation held, a player jump is stepped in fixed game time (`actAdvance`); the visible sprite must lift (>= 0.2 m, its screen rect rises) while the shadow caster stays at the feet, then land and end. Hero players also need >= 2 attack frames and a held defend that reaches its hold frames (2/3) and ends on release.
- phone: portrait 390x844 and landscape 844x390 at DPR 2 with `isMobile` + `hasTouch` and the Layout One pad on (`?pad=1`). Each orientation must pass every sub-check:
  - layout: HUD chips and pad controls stay inside the viewport and don't overlap each other, and enabled touch targets are at least 30 CSS px.
  - touch_tap_walk: a CDP touch tap on open ground walks the player toward it.
  - floating_stick: a touch inside the movement zone (`#stickZone`) makes the stick appear under the thumb (not in its resting corner); dragging 150 px past the 64 px radius makes the stick slide after the finger (finger-to-centre stays ~64 px) and walks the player; on release it rests again. With the left-handed flip the zone is on the right half and the stick still floats there. Writes `phone_<orientation>_floatstick.png` (mid-drag).
  - no_page_zoom: viewport meta has `user-scalable=no` + `maximum-scale=1`; html, body and the canvas have `touch-action: none` and `overscroll-behavior: none`; synthetic `gesturestart` and `dblclick` are cancelled; after a double-tap and a pull-down-from-the-top swipe the visual viewport scale is 1, the page scroll is 0 and the page didn't reload.
  - loading_gate (portrait): the page loads with every `.glb` held back; while the `#boot` overlay is up, touch taps, a stick drag and keys (E, Enter, D, F, Space, G) are all swallowed. After release: nothing queued (no walk, no drift) and the gate counted the swallowed events.
  - gamepad (portrait): a stubbed standard-mapping controller (`gamepad_stub.js` behind `navigator.getGamepads`) is plugged in; its left stick walks the player, `body.ctrl` hides the on-screen pad while it's used, and a touch brings the pad back.
  - pinch: two-finger pinch out and in changes zoom, inside the scene's limits.
  - camera_locked: the quaternion is unchanged after all of that.
  - sprites_sharp: actor crops are still uniform k x k blocks at DPR 2 (clean capture with the HUD hidden).
  - Writes `phone_portrait.png` and `phone_landscape.png` (+ the floating-stick mid-drag shots).
  - It found, and the runtime now fixes: chips under 30 px, the button column running into the pad in landscape, and touch taps dropped on slow frames.
- `--scene-dir` / `--params` check one area of a multi-area game (paths are resolved inside the scene dir; the params are added to the URL).
