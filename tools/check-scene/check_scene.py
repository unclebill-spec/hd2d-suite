"""check-scene: headless QA for an assembled hd2d folder.

Loads the built scene in Playwright Chromium (SwiftShader WebGL2), screenshots day / dusk / night,
then checks:
  sprites_sharp   every on-screen actor crop is made of uniform k x k blocks (nearest-neighbour,
                  never blurred) and its luminance pattern correlates with the source atlas frame
                  (measured on a clean capture of the same frozen frame with particles/effects hidden,
                  so a passing firefly can't fail an actor; the saved shot keeps everything)
  camera_locked   camera quaternion + fov + view direction unchanged after keys, drag, tap, wheel;
                  zoom stays inside the scene's limits
  no_bloom        no blown highlights (near-white fraction) and no wide glow wash
  height          real height: collision heightfield range and world Y extent
  colours         sane colour counts (not posterised, not noise); sprite crops keep a small palette
  grades          dusk is bluer than day, night darker than day with warm window/lamp pixels
  effects_sharp   (scenes with spells) every spell effect is laid out frozen mid-animation in front of the
                  camera (actors hidden); each crop must be uniform k x k blocks and correlate with its
                  spells-atlas frame, with no blown highlights around them (no bloom on effects either)
  gamefx_sharp    (scenes with game effects: portal vortex / ring, pickups, quest tags) same lineup test on the gamefx atlas
  actions         (engines with window.__hd2d.act) a triggered jump lifts the visible sprite (lift >= 0.2 m, its screen
                  rect rises) while the shadow caster stays at the feet, then lands and ends; hero players also play
                  >= 2 attack frames and a held defend reaches its hold frames (2/3) and ends on release
  phone           portrait 390x844 + landscape 844x390, DPR 2, touch (isMobile/hasTouch) with the Layout One pad on:
                  HUD + pad inside the viewport, no overlapping controls, touch targets >= 30 CSS px, a touch tap on
                  open ground walks the player, the FLOATING stick appears under the thumb, re-centres when dragged
                  past its radius and moves the player (mirrored with the left-handed flip too), a two-finger pinch
                  stays inside the zoom limits, the camera stays locked, sprites stay sharp, the page itself never
                  scrolls or zooms (viewport meta, touch-action, overscroll, gesturestart / dblclick blocked, a
                  double-tap and a pull-down leave scale 1 and scroll 0); portrait also loads with the assets held
                  back and checks that taps + keys during loading are swallowed (no queued walk), and drives a
                  stubbed standard-mapping controller (stick walks, pad hides while it is used, a touch brings the
                  pad back); saves phone_portrait.png / phone_landscape.png
  no_errors       no JS errors
Writes <out>/{day,dusk,night}.png, sprite crop strips, effects.png + effects_2x.png (if spells),
and check_scene.json. Exit 0 = pass.
"""
import argparse
import functools
import json
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import numpy as np
from PIL import Image

TIMES = ("day", "dusk", "night")


class _Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def _serve(root):
    srv = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(_Quiet, directory=str(root)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def lum(a):
    a = a[..., :3].astype(np.float32)
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


_SHEETS, _SHEET_ROOT = {}, []


def _frames(pg, n=3, timeout=20.0):
    """wait until the engine has drawn n more frames: fixed sleeps alone read rects that were never set on a loaded box
    (plaza's second gamefx page under load ~20 drew no frame in 1 s)"""
    import time
    f0 = pg.evaluate("window.__hd2d.frames || 0"); t0 = time.time()
    while pg.evaluate("window.__hd2d.frames || 0") < f0 + n and time.time() - t0 < timeout:
        pg.wait_for_timeout(100)


def sprite_check(shot, atlas, r, block_tol=6):
    """shot: HxWx3 uint8 screenshot, atlas: RGBA uint8, r: actor rect (screenshot px)."""
    if r.get("atlas") and _SHEET_ROOT:   # a boss role drawn on its own sheet (bigger native frames): compare with that sheet
        if r["atlas"] not in _SHEETS:
            _SHEETS[r["atlas"]] = np.array(Image.open(_SHEET_ROOT[0] / r["atlas"]).convert("RGBA"))
        atlas = _SHEETS[r["atlas"]]
    k = int(r["k"]); fx, fy = r["frame"]; fw, fh = r["w"] // k, r["h"] // k
    x0, y0 = int(round(r["x"])), int(round(r["y"]))
    src = atlas[fy:fy + fh, fx:fx + fw]
    H, W = shot.shape[:2]
    blocks, uniform, sv, dv = 0, 0, [], []
    for j in range(fh):
        for i in range(fw):
            if src[j, i, 3] < 128:
                continue
            ys, xs = y0 + j * k, x0 + i * k
            if ys < 0 or xs < 0 or ys + k > H or xs + k > W:
                continue
            b = shot[ys:ys + k, xs:xs + k, :3].astype(np.int16)
            blocks += 1
            if int((b.max(axis=(0, 1)) - b.min(axis=(0, 1))).max()) <= block_tol:
                uniform += 1
            sv.append(lum(src[j:j + 1, i:i + 1])[0, 0]); dv.append(lum(b).mean())
    if blocks < 20:
        if int((src[..., 3] >= 128).sum()) < 20:   # a tiny spark frame: too few pixels to measure, not missing
            return {"id": r["id"], "skipped": "sparse"}
        return {"id": r["id"], "skipped": "off-screen"}
    sv, dv = np.array(sv), np.array(dv)
    corr = float(np.corrcoef(sv, dv)[0, 1]) if sv.std() > 0 and dv.std() > 0 else 0.0
    crop = shot[max(0, y0):y0 + r["h"], max(0, x0):x0 + r["w"], :3]
    opaque = src[..., 3] >= 128
    src_cols = len({tuple(c) for c in src[opaque][:, :3]})
    # sample crop colours at block centres of opaque texels only
    cols = set()
    for j in range(fh):
        for i in range(fw):
            if opaque[j, i]:
                yy, xx = y0 + j * k + k // 2, x0 + i * k + k // 2
                if 0 <= yy < H and 0 <= xx < W:
                    cols.add(tuple(shot[yy, xx, :3]))
    return {"id": r["id"], "role": r.get("role"), "k": k, "blocks": blocks,
            "uniform_frac": round(uniform / blocks, 4), "atlas_corr": round(corr, 4),
            "src_colours": src_cols, "crop_colours": len(cols), "rect": [x0, y0, r["w"], r["h"]], "frame": [fx, fy], "facing": r.get("facing"), "_crop": crop}


PHONE_LAYOUT_JS = """() => {
  const sel = '#hud .chip, #hud .hint, #hud button, #pad .stick, #pad .pb, #pad .pill, [data-hud]';
  const vis = (el) => { if (el.closest('[hidden]')) return false; const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) return false; const r = el.getBoundingClientRect(); return r.width > 1 && r.height > 1; };
  const els = [...new Set(document.querySelectorAll(sel))].filter(vis);
  const out = els.map((el) => { const r = el.getBoundingClientRect(); return { id: el.id || el.className || el.tagName, tag: el.tagName, x: r.left, y: r.top, w: r.width, h: r.height,
    button: (el.tagName === 'BUTTON' && !el.disabled) || el.classList.contains('stick'), text: (el.textContent || '').trim().slice(0, 24) }; });
  // overlap pairs: ignore an element and its own ancestors / descendants
  const over = [];
  for (let i = 0; i < els.length; i++) for (let j = i + 1; j < els.length; j++) {
    if (els[i].contains(els[j]) || els[j].contains(els[i])) continue;
    const a = out[i], b = out[j];
    const ix = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x), iy = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
    if (ix > 1 && iy > 1) over.push([a.id, b.id, Math.round(ix), Math.round(iy)]);
  }
  return { els: out, over, W: innerWidth, H: innerHeight };
}"""

# pick a reachable ground point 1.5-3 m from the player that projects onto open canvas (not under HUD)
PHONE_TARGET_JS = """() => {
  const h = window.__hd2d, c = h.ctx, p = c.player;
  // bare canvas first; then the floating-stick zone (a quick tap there is handed on to tap-to-walk)
  for (const okEl of [(el) => el.tagName === 'CANVAS', (el) => el.id === 'stickZone'])
  for (const r of [2.4, 1.8, 3.0]) for (let k = 0; k < 16; k++) {
    const a = k / 16 * Math.PI * 2, x = p.x + Math.cos(a) * r, z = p.z + Math.sin(a) * r;
    const path = h.path(x, z); if (!path || !path.length) continue;
    const e = path[path.length - 1]; if (Math.hypot(e[0] - x, e[1] - z) > 0.3) continue;
    const s = c.project(x, c.heightAt(x, z), z);
    if (s.x < 30 || s.y < 30 || s.x > innerWidth - 30 || s.y > innerHeight - 30) continue;
    const el = document.elementFromPoint(s.x, s.y); if (!el || !okEl(el)) continue;
    // not on a sprite (a tap on an NPC talks instead of walking): rects are drawing-buffer px
    const onActor = h.actorRects().some((r) => { if (!r.w || r.id === 'player') return false; const q = innerWidth / r.buf[0];
      return s.x > r.x * q - 12 && s.x < (r.x + r.w) * q + 12 && s.y > r.y * q - 12 && s.y < (r.y + r.h) * q + 12; });
    if (onActor) continue;
    return { x, z, sx: s.x, sy: s.y, via: el.id || el.tagName };
  }
  return null;
}"""


def _touch(cdp, kind, pts, ts=None):
    ev = {"type": kind, "touchPoints": [{"x": x, "y": y, "id": i} for i, (x, y) in enumerate(pts)]}
    if ts is not None:   # OS-style input timestamps, so a slow SwiftShader frame can't stretch a tap into a hold
        ev["timestamp"] = ts
    cdp.send("Input.dispatchTouchEvent", ev)


GAMEPAD_STUB = (Path(__file__).resolve().parent / "gamepad_stub.js").read_text()
PPOS = "[window.__hd2d.ctx.player.x, window.__hd2d.ctx.player.z]"

NO_ZOOM_JS = r"""() => {
  const meta = (document.querySelector('meta[name=viewport]') || {}).content || '';
  const cs = (el) => getComputedStyle(el);
  const prevented = (type) => { const e = new Event(type, { bubbles: true, cancelable: true }); document.body.dispatchEvent(e); return e.defaultPrevented; };
  return { meta, user_scalable_no: /user-scalable\s*=\s*no/.test(meta), max_scale_1: /maximum-scale\s*=\s*1(\.0)?\b/.test(meta),
    touch_action: [cs(document.documentElement).touchAction, cs(document.body).touchAction, cs(document.getElementById('view') || document.body).touchAction],
    overscroll: [cs(document.documentElement).overscrollBehaviorY, cs(document.body).overscrollBehaviorY],
    gesturestart_blocked: prevented('gesturestart'), dblclick_blocked: prevented('dblclick'),
    scale: window.visualViewport ? visualViewport.scale : 1, scroll: [scrollX, scrollY] };
}"""


def _loading_gate(pg, cdp, url, timeout):
    """load with every .glb held back; taps, a stick drag and keys while loading must all be swallowed"""
    held, hold = [], [True]
    pg.route("**/*.glb", lambda route: held.append(route) if hold[0] else route.continue_())
    pg.goto(url, wait_until="commit")
    pg.wait_for_function("window.__hd2dGate && document.getElementById('boot')", timeout=timeout * 1000)
    pg.wait_for_timeout(400)
    vw, vh = pg.viewport_size["width"], pg.viewport_size["height"]
    boot_vis = pg.evaluate("getComputedStyle(document.getElementById('boot')).display !== 'none'")
    loading_during = pg.evaluate("window.__hd2dGate.loading === true")
    t = time.time()
    for i in range(6):
        x, y = vw * (0.3 + 0.08 * i), vh * (0.35 + 0.05 * i)
        _touch(cdp, "touchStart", [(x, y)], t + i * 0.2); _touch(cdp, "touchEnd", [], t + i * 0.2 + 0.06)
        pg.keyboard.press(["e", "Enter", "d", "f", " ", "g"][i])
        pg.wait_for_timeout(60)
    _touch(cdp, "touchStart", [(vw * 0.2, vh * 0.8)])
    for i in range(1, 6):
        _touch(cdp, "touchMove", [(vw * 0.2 + 14 * i, vh * 0.8)]); pg.wait_for_timeout(30)
    _touch(cdp, "touchEnd", [])
    hold[0] = False
    for rt in held:
        try:
            rt.continue_()
        except Exception:  # noqa: BLE001
            pass
    pg.wait_for_function("window.__hd2d && window.__hd2d.ready === true", timeout=timeout * 1000)
    p_ready = pg.evaluate(PPOS)
    pg.wait_for_timeout(1200)
    p_after = pg.evaluate(PPOS)
    walking = pg.evaluate("window.__hd2d.walking()")
    swallowed = pg.evaluate("window.__hd2dGate.swallowed")
    drift = abs(p_after[0] - p_ready[0]) + abs(p_after[1] - p_ready[1])
    ok = boot_vis and loading_during and not walking and drift < 0.05 and swallowed > 0 and pg.evaluate("!window.__hd2dGate.loading")
    return {"pass": bool(ok), "held_requests": len(held), "boot_overlay_during": boot_vis, "gate_during": loading_during,
            "swallowed": swallowed, "walking_after": walking, "drift_m": round(drift, 3)}


def _floating_stick(pg, cdp, name):
    """the stick appears under the thumb anywhere in the zone, slides after a finger dragged past its radius,
    moves the player, rests again on release; mirrored to the right side by the left-handed flip"""
    geo = pg.evaluate("""() => { const z = document.getElementById('stickZone'), s = document.getElementById('stick');
      if (!z || !s) return null; const a = z.getBoundingClientRect(), b = s.getBoundingClientRect();
      return { zone: [a.left, a.top, a.width, a.height], rest: [b.left + b.width / 2, b.top + b.height / 2], R: 64 }; }""")
    if not geo:
        return {"pass": False, "why": "no #stickZone / #stick"}
    zx, zy, zw, zh = geo["zone"]
    sx, sy = zx + zw * 0.55, zy + zh * 0.32
    out = {"zone": [round(v) for v in geo["zone"]], "rest": [round(v) for v in geo["rest"]], "touch": [round(sx), round(sy)]}
    pa = pg.evaluate(PPOS)
    _touch(cdp, "touchStart", [(sx, sy)]); pg.wait_for_timeout(150)
    s1 = pg.evaluate("window.__hd2d.stickState()")
    appear = bool(s1["base"]) and abs(s1["base"]["x"] - sx) < 3 and abs(s1["base"]["y"] - sy) < 3
    fx = sx
    for i in range(1, 11):
        fx = sx + 15 * i
        _touch(cdp, "touchMove", [(fx, sy)]); pg.wait_for_timeout(35)
    pg.wait_for_timeout(250)
    s2 = pg.evaluate("window.__hd2d.stickState()")
    shot = None
    if name:
        shot = str(name)
        pg.screenshot(path=shot)
    pg.wait_for_timeout(700)
    _touch(cdp, "touchEnd", []); pg.wait_for_timeout(250)
    s3 = pg.evaluate("window.__hd2d.stickState()")
    pb_ = pg.evaluate(PPOS)
    moved = [round(pb_[0] - pa[0], 2), round(pb_[1] - pa[1], 2)]
    b2 = s2.get("base") or {"x": sx, "y": sy}
    follow = b2["x"] - sx > 60 and abs((fx - b2["x"]) - geo["R"]) < 8
    rests = not s3["active"] and s3["rest"]
    out.update({"appears_under_thumb": appear, "base_after_drag": [round(b2["x"]), round(b2["y"])], "recentres": follow, "rests_on_release": rests,
                "moved_xz": moved, "ran_at_rim": bool(s2.get("run"))})
    # left-handed flip: the zone moves to the right half and the stick still floats
    left0 = pg.evaluate("document.body.classList.contains('lefthand')")
    pg.evaluate("window.__hd2d.setHand(true)"); pg.wait_for_timeout(150)
    z2 = pg.evaluate("(() => { const a = document.getElementById('stickZone').getBoundingClientRect(); return [a.left, a.top, a.width, a.height]; })()")
    tx, ty = z2[0] + z2[2] * 0.45, z2[1] + z2[3] * 0.4
    _touch(cdp, "touchStart", [(tx, ty)]); pg.wait_for_timeout(150)
    s4 = pg.evaluate("window.__hd2d.stickState()")
    _touch(cdp, "touchEnd", []); pg.wait_for_timeout(150)
    pg.evaluate(f"window.__hd2d.setHand({'true' if left0 else 'false'})")
    lh = z2[0] >= pg.viewport_size["width"] / 2 - 1 and bool(s4["base"]) and abs(s4["base"]["x"] - tx) < 3
    out["lefthand_zone"] = [round(v) for v in z2]
    out["lefthand_floats"] = lh
    out["pass"] = bool(appear and follow and rests and abs(moved[0]) + abs(moved[1]) > 0.5 and lh)
    if shot:
        out["shot"] = shot
    return out


def _gamepad_touch(pg, cdp):
    """stubbed standard controller: stick walks, the on-screen pad hides while it is used, a touch brings it back"""
    pa = pg.evaluate(PPOS)
    pg.evaluate("__padPlug(true)"); pg.evaluate("__padAxes(-1, 0)"); pg.wait_for_timeout(1600)
    st = pg.evaluate("window.__hd2d.gamepad()")
    pad_hidden = pg.evaluate("getComputedStyle(document.getElementById('pad')).display === 'none'")
    pg.evaluate("__padAxes(0, 0)"); pg.wait_for_timeout(300)
    pb_ = pg.evaluate(PPOS)
    vw = pg.viewport_size["width"]
    _touch(cdp, "touchStart", [(vw * 0.5, 120)]); _touch(cdp, "touchEnd", []); pg.wait_for_timeout(300)
    back = pg.evaluate("!document.body.classList.contains('ctrl') && getComputedStyle(document.getElementById('pad')).display !== 'none'")
    pg.evaluate("__padPlug(false)")
    moved = [round(pb_[0] - pa[0], 2), round(pb_[1] - pa[1], 2)]
    ok = st["ctrl"] and st["count"] >= 1 and pad_hidden and back and abs(moved[0]) + abs(moved[1]) > 0.15
    return {"pass": bool(ok), "moved_xz": moved, "ctrl_mode": st["ctrl"], "pad_hidden_while_used": pad_hidden, "pad_back_on_touch": back}


def _no_page_zoom(pg, cdp, tgt):
    a = pg.evaluate(NO_ZOOM_JS)
    if tgt:
        t = time.time()
        for k in range(2):   # double-tap
            _touch(cdp, "touchStart", [(tgt["sx"], tgt["sy"])], t + k * 0.15); _touch(cdp, "touchEnd", [], t + k * 0.15 + 0.05)
        pg.wait_for_timeout(400)
    vw = pg.viewport_size["width"]
    pg.evaluate("window.__noReload = 1")
    _touch(cdp, "touchStart", [(vw * 0.6, 70)])           # pull-to-refresh gesture from the top
    for i in range(1, 9):
        _touch(cdp, "touchMove", [(vw * 0.6, 70 + 40 * i)]); pg.wait_for_timeout(20)
    _touch(cdp, "touchEnd", []); pg.wait_for_timeout(500)
    b_ = pg.evaluate(NO_ZOOM_JS)
    same = pg.evaluate("window.__noReload === 1")
    ok = (a["user_scalable_no"] and a["max_scale_1"] and all(v == "none" for v in a["touch_action"]) and all(v == "none" for v in a["overscroll"])
          and a["gesturestart_blocked"] and a["dblclick_blocked"] and b_["scale"] == 1 and b_["scroll"] == [0, 0] and same)
    return {"pass": bool(ok), "before": a, "after_doubletap_pull": {"scale": b_["scale"], "scroll": b_["scroll"], "no_reload": same}}


def phone_check(b, url, atlas, cam_spec, out, name, vw, vh, timeout=120, extras=True):
    ctx = b.new_context(viewport={"width": vw, "height": vh}, device_scale_factor=2, is_mobile=True, has_touch=True)
    ctx.add_init_script(GAMEPAD_STUB)
    pg = ctx.new_page()
    pg.set_default_timeout(max(30, timeout) * 1000)   # a loaded shared box can stall SwiftShader screenshots past 30 s
    logs = []
    pg.on("pageerror", lambda e: logs.append(f"PAGEERROR {e}"))
    r = {"viewport": [vw, vh], "dpr": 2}
    try:
        cdp = ctx.new_cdp_session(pg)
        if extras:
            r["loading_gate"] = _loading_gate(pg, cdp, url, timeout)
        else:
            pg.goto(url)
        pg.wait_for_function("window.__hd2d && window.__hd2d.ready === true", timeout=timeout * 1000)
        pg.wait_for_timeout(800)
        lay = pg.evaluate(PHONE_LAYOUT_JS)
        outside = [e["id"] for e in lay["els"] if e["x"] < -0.5 or e["y"] < -0.5 or e["x"] + e["w"] > vw + 0.5 or e["y"] + e["h"] > vh + 0.5]
        small = [[e["id"], round(e["w"]), round(e["h"])] for e in lay["els"] if e["button"] and min(e["w"], e["h"]) < 30]
        pad_vis = any(e["id"] == "stick" for e in lay["els"])
        r["layout"] = {"elements": len(lay["els"]), "outside": outside, "overlaps": lay["over"], "small_targets": small, "pad_visible": pad_vis}
        # sharp sprites at phone DPR first (clean capture, before any input moves actors into each other), then the saved shot
        HIDE = "document.querySelectorAll('#hud,#pad,#dlg,#log,#titlescreen').forEach((e) => { e.style.visibility = '%s'; })"
        pg.evaluate("window.__hd2d.hold(true); window.__hd2d.showOverlays && window.__hd2d.showOverlays(false)")
        pg.evaluate(HIDE % "hidden")   # the clean capture is of the world only (a sprite under the stick is not blurred)
        pg.wait_for_timeout(300)
        import io
        rects = None
        for _ in range(6):
            before = pg.evaluate("window.__hd2d.actorRects()")
            clean = pg.screenshot()
            after = pg.evaluate("window.__hd2d.actorRects()")
            if json.dumps(before) == json.dumps(after):
                rects = before
                break
            pg.wait_for_timeout(120)
        rects = rects or after
        img = np.array(Image.open(io.BytesIO(clean)).convert("RGB"))
        scale = img.shape[1] / rects[0]["buf"][0] if rects else 1
        res = []
        for rr in rects:
            if abs(scale - 1) > 1e-6:
                rr = {**rr, "x": rr["x"] * scale, "y": rr["y"] * scale}
            res.append(sprite_check(img, atlas, rr))
        ok_s = [a for a in res if "uniform_frac" in a]
        wu = min((a["uniform_frac"] for a in ok_s), default=0)
        wc = min((a["atlas_corr"] for a in ok_s), default=0)
        r["sprites_sharp"] = {"pass": bool(ok_s) and wu >= 0.97 and wc >= 0.85, "checked": len(ok_s), "worst_uniform": wu, "worst_corr": wc,
                              "buffer": rects[0]["buf"] if rects else None}
        pg.evaluate("window.__hd2d.showOverlays && window.__hd2d.showOverlays(true)")
        pg.evaluate(HIDE % "")
        pg.wait_for_timeout(200)
        path = out / f"phone_{name}.png"
        pg.screenshot(path=str(path))
        pg.evaluate("window.__hd2d.hold(false)")
        r["shot"] = str(path)
        c0 = pg.evaluate("window.__hd2d.camState()")
        # touch tap on open ground
        tgt = pg.evaluate(PHONE_TARGET_JS)
        p0 = pg.evaluate("[window.__hd2d.ctx.player.x, window.__hd2d.ctx.player.z]")
        tap_ok, tap_d = False, None
        if tgt:
            t_tap = time.time()
            _touch(cdp, "touchStart", [(tgt["sx"], tgt["sy"])], t_tap); pg.wait_for_timeout(60); _touch(cdp, "touchEnd", [], t_tap + 0.08)
            pg.wait_for_timeout(250)
            started = pg.evaluate("window.__hd2d.walking()")
            pg.wait_for_timeout(1950)
            p1 = pg.evaluate("[window.__hd2d.ctx.player.x, window.__hd2d.ctx.player.z]")
            d0 = ((p0[0] - tgt["x"]) ** 2 + (p0[1] - tgt["z"]) ** 2) ** 0.5
            d1 = ((p1[0] - tgt["x"]) ** 2 + (p1[1] - tgt["z"]) ** 2) ** 0.5
            tap_d = [round(d0, 2), round(d1, 2)]
            # SwiftShader at DPR 2 runs a few fps (dt is capped), so: a path started and the player is closing in
            tap_ok = (started and d1 < d0 - 0.25) or d1 < d0 - 0.8
        r["touch_tap_walk"] = {"pass": bool(tap_ok), "target": tgt, "dist_before_after": tap_d, "path_started": bool(tgt and started)}
        # floating stick (pad): lands under the thumb, slides after the finger, walks; left-handed mirror
        r["floating_stick"] = _floating_stick(pg, cdp, out / f"phone_{name}_floatstick.png")
        if r["floating_stick"].get("shot"):
            r["floatstick_shot"] = r["floating_stick"]["shot"]
        r["no_page_zoom"] = _no_page_zoom(pg, cdp, pg.evaluate(PHONE_TARGET_JS))
        # pinch out then in
        cx, cy = vw / 2, vh * 0.45
        dists = []
        for a0, a1 in ((30, 150), (150, 20)):
            _touch(cdp, "touchStart", [(cx - a0, cy), (cx + a0, cy)])
            for i in range(1, 9):
                a = a0 + (a1 - a0) * i / 8
                _touch(cdp, "touchMove", [(cx - a, cy), (cx + a, cy)]); pg.wait_for_timeout(25)
            _touch(cdp, "touchEnd", [])
            pg.wait_for_timeout(300)
            dists.append(pg.evaluate("window.__hd2d.camState().dist"))
        zr = cam_spec.get("zoom", [c0["dist"], c0["dist"]])
        c1 = pg.evaluate("window.__hd2d.camState()")
        dq = max(abs(x - y) for x, y in zip(c0["quat"], c1["quat"]))
        pinch_ok = all(zr[0] - 1e-3 <= d <= zr[1] + 1e-3 for d in dists) and dists[0] < c0["dist"] - 0.5 and dists[1] > dists[0] + 0.5
        r["pinch"] = {"pass": pinch_ok, "dist_start_out_in": [round(c0["dist"], 2)] + [round(d, 2) for d in dists], "limits": zr}
        r["camera_locked"] = {"pass": dq < 1e-5 and c0["fov"] == c1["fov"], "quat_delta": dq}
        if extras:
            r["gamepad"] = _gamepad_touch(pg, cdp)
        errs = pg.evaluate("window.__hd2d.errors")
        r["errors"] = (errs or []) + [l for l in logs if "PAGEERROR" in l]
        L = r["layout"]
        r["layout"]["pass"] = not L["outside"] and not L["overlaps"] and not L["small_targets"] and L["pad_visible"]
        keys = ["layout", "touch_tap_walk", "floating_stick", "no_page_zoom", "pinch", "camera_locked", "sprites_sharp"] + (["loading_gate", "gamepad"] if extras else [])
        r["pass"] = all(r[k]["pass"] for k in keys) and not r["errors"]
    except Exception as e:  # noqa: BLE001
        r["pass"] = False
        r["exception"] = str(e)[:400]
    finally:
        ctx.close()
    return r


# trigger an action on the player with the simulation held, step it in fixed game time (actAdvance) and read the
# rendered state after each step, so slow software GL can't skip phases. args: name, [[advance_s, release?], ...]
ACT_SAMPLE = """async ([name, steps]) => {
  const h = window.__hd2d, raf = () => new Promise((r) => requestAnimationFrame(r));
  const settle = async () => { await raf(); await raf(); };
  h.hold(true); await settle();
  const s0 = h.actorState();
  const ok = h.act(name, null, name === 'defend' ? { hold: true } : {});
  const rows = [];
  for (const [dt, rel] of steps) {
    if (rel) h.release(name);
    h.actAdvance(dt); await settle();
    const s = h.actorState();
    rows.push({ act: s.act, anim: s.anim, frame: s.frame, lift: +s.lift.toFixed(3), gap: Math.abs(s.casterY - s.y), ry: s.rect ? s.rect.y : 0 });
  }
  h.hold(false);
  const fin = rows[rows.length - 1], frames = {};
  for (const r of rows) if (r.act) (frames[r.anim] = frames[r.anim] || []).includes(r.frame) || frames[r.anim].push(r.frame);
  return { ok, rows, frames, max_lift: Math.max(0, ...rows.map((r) => r.lift)), max_caster_gap: Math.max(0, ...rows.map((r) => r.gap)),
           rect_rise_px: (s0.rect ? s0.rect.y : 0) - Math.min(...rows.map((r) => r.ry)), ended: fin.act === null && fin.lift === 0 };
}"""
ACT_STEPS = {"jump": [[0.05, 0], [0.2, 0], [0.12, 0], [0.14, 0], [0.12, 0], [0.2, 0]],
             "attack": [[0.04, 0], [0.12, 0], [0.1, 0], [0.1, 0], [0.2, 0]],
             "defend": [[0.08, 0], [0.18, 0], [0.2, 0], [0.18, 0], [0.05, 1]]}


def run(root, out, size=(1280, 720), timeout=120, scene_dir="", params="", phone=True):
    from playwright.sync_api import sync_playwright
    root, out = Path(root).resolve(), Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    sroot = root / scene_dir if scene_dir else root
    scene = json.loads((sroot / "scene.json").read_text())
    atlas = np.array(Image.open(sroot / scene["atlas"]["image"]).convert("RGBA"))
    _SHEET_ROOT[:] = [sroot]
    pre = (params + "&") if params else ""
    cam_spec = scene.get("camera", {})
    srv = _serve(root)
    port = srv.server_address[1]
    rep = {"root": str(root), "scene_dir": scene_dir, "params": params, "size": list(size), "checks": {}, "shots": {}, "notes": []}
    logs = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
            pg = b.new_page(viewport={"width": size[0], "height": size[1]})
            pg.set_default_timeout(max(30, timeout) * 1000)
            pg.on("pageerror", lambda e: logs.append(f"PAGEERROR {e}"))
            pg.on("console", lambda m: logs.append(f"{m.type}: {m.text}") if m.type == "error" else None)
            t0 = time.time()
            pg.goto(f"http://127.0.0.1:{port}/index.html?{pre}t=day&freeze&shot&hud=0")
            pg.wait_for_function("window.__hd2d && window.__hd2d.ready === true", timeout=timeout * 1000)
            rep["load_s"] = round(time.time() - t0, 1)
            stats = pg.evaluate("window.__hd2d.stats()")
            rep["stats"] = stats

            imgs, sprites = {}, {}
            for tname in TIMES:
                pg.evaluate(f"window.__hd2d.setTime('{tname}')")
                pg.wait_for_timeout(1500)
                # frozen frame; the clean capture (spell effects + particles hidden) is what the sprite crops are
                # compared against, the full capture (everything visible) is saved and used for bloom/colour/grades
                pg.evaluate("window.__hd2d.hold(true); window.__hd2d.showOverlays && window.__hd2d.showOverlays(false)")
                pg.wait_for_timeout(300)
                shot_rects = None
                for _ in range(6):  # retry until the animation frame is stable across the capture
                    before = pg.evaluate("window.__hd2d.actorRects()")
                    clean = pg.screenshot()
                    after = pg.evaluate("window.__hd2d.actorRects()")
                    if json.dumps(before) == json.dumps(after):
                        shot_rects = before
                        break
                    pg.wait_for_timeout(120)
                pg.evaluate("window.__hd2d.showOverlays && window.__hd2d.showOverlays(true)")
                pg.wait_for_timeout(200)
                png = pg.screenshot()
                pg.evaluate("window.__hd2d.hold(false)")
                path = out / f"{tname}.png"
                path.write_bytes(png)
                rep["shots"][tname] = str(path)
                imgs[tname] = np.array(Image.open(path).convert("RGB"))
                import io
                img = np.array(Image.open(io.BytesIO(clean)).convert("RGB"))
                res = []
                rects = shot_rects or after
                scale = img.shape[1] / rects[0]["buf"][0] if rects else 1
                for r in rects:
                    if abs(scale - 1) > 1e-6:
                        rep["notes"].append("drawing buffer != screenshot size; rects scaled")
                        r = {**r, "x": r["x"] * scale, "y": r["y"] * scale}
                    res.append(sprite_check(img, atlas, r))
                sprites[tname] = {"stable": shot_rects is not None, "actors": res}
                # crop strip at 2x for human review
                crops = [c["_crop"] for c in res if "_crop" in c and c["_crop"].size]
                if crops:
                    hmax = max(c.shape[0] for c in crops)
                    strip = np.zeros((hmax, sum(c.shape[1] for c in crops) + 8 * (len(crops) - 1), 3), np.uint8) + 30
                    x = 0
                    for c in crops:
                        strip[:c.shape[0], x:x + c.shape[1]] = c; x += c.shape[1] + 8
                    Image.fromarray(strip).resize((strip.shape[1] * 2, strip.shape[0] * 2), Image.NEAREST).save(out / f"sprites_{tname}_2x.png")

            # ---- spell effects: frozen lineup, sharp-pass crops
            fx = None
            if scene.get("spells"):
                fx_atlas = np.array(Image.open(sroot / scene["spells"]["image"]).convert("RGBA"))
                pg.evaluate("window.__hd2d.setTime('dusk')")
                pg.wait_for_timeout(600)
                # particles off for the lineup: a firefly drifting over a frozen effect is not a blurred effect
                PSHOW = "(() => { const p = window.__hd2d.ctx.particles; if (p) p.points.visible = %s; })()"
                pg.evaluate(PSHOW % "false")
                # paged lineup (<= 24 per page, <= 8 a row at 2.4 m) when the runtime has effectPages; older runtimes: one page
                FPER = 24
                fpages = pg.evaluate(f"window.__hd2d.effectPages ? window.__hd2d.effectPages({FPER}) : 0")
                fres, fexp, fnw, fbf = [], 0, 0.0, 0.0
                for page in range(max(1, fpages)):
                    lineup = f"window.__hd2d.effectLineup(0.5, {page}, {FPER})" if fpages else "window.__hd2d.effectLineup(0.5)"
                    pg.evaluate(f"window.__hd2d.hideActors(true); {lineup}")
                    pg.wait_for_timeout(700); _frames(pg)
                    pg.evaluate("window.__hd2d.hold(true)")
                    pg.wait_for_timeout(300)
                    frects = pg.evaluate("window.__hd2d.effectRects()")
                    png = pg.screenshot()
                    pg.evaluate("window.__hd2d.hold(false); window.__hd2d.effects.clear(); window.__hd2d.hideActors(false)")
                    path = out / ("effects.png" if page == 0 else f"effects_p{page + 1}.png")
                    path.write_bytes(png)
                    rep["shots"]["effects" if page == 0 else f"effects_p{page + 1}"] = str(path)
                    fimg = np.array(Image.open(path).convert("RGB"))
                    scale = fimg.shape[1] / frects[0]["buf"][0] if frects else 1
                    for r in frects:
                        if abs(scale - 1) > 1e-6:
                            r = {**r, "x": r["x"] * scale, "y": r["y"] * scale}
                        fres.append({**sprite_check(fimg, fx_atlas, r), "kind": r.get("kind")})
                    im16 = fimg.astype(np.int16)
                    fexp += len(frects)
                    fnw = max(fnw, float(((im16[..., 0] > 248) & (im16[..., 1] > 248) & (im16[..., 2] > 248)).mean()))
                    fbf = max(fbf, float((lum(fimg) > 225).mean()))
                pg.evaluate(PSHOW % "true")
                fx = {"effects": fres, "expected": fexp, "near_white": fnw, "bright_frac": fbf}
                crops = [c["_crop"] for c in fres if "_crop" in c and c["_crop"].size]
                if crops:
                    hmax = max(c.shape[0] for c in crops)
                    strip = np.zeros((hmax, sum(c.shape[1] for c in crops) + 8 * (len(crops) - 1), 3), np.uint8) + 30
                    x = 0
                    for c in crops:
                        strip[:c.shape[0], x:x + c.shape[1]] = c; x += c.shape[1] + 8
                    Image.fromarray(strip).resize((strip.shape[1] * 2, strip.shape[0] * 2), Image.NEAREST).save(out / "effects_2x.png")

            # ---- game effects (portal, pickups, quest tags): same frozen lineup on the gamefx atlas
            gfx = None
            if scene.get("gamefx"):
                g_atlas = np.array(Image.open(sroot / scene["gamefx"]["image"]).convert("RGBA"))
                pg.evaluate("window.__hd2d.setTime('dusk')")
                pg.wait_for_timeout(500)
                # paged lineup (one row of <= 7 per page); older runtimes without gamefxPages have one page
                pages = pg.evaluate("window.__hd2d.gamefxPages ? window.__hd2d.gamefxPages() : 1") or 1
                gres, nw, bf = [], 0.0, 0.0
                for pi in range(pages):
                    pg.evaluate(f"window.__hd2d.hideActors(true); window.__hd2d.showOverlays && window.__hd2d.showOverlays(false); window.__hd2d.gamefxLineup(0.5, {pi})")
                    pg.wait_for_timeout(700); _frames(pg)
                    pg.evaluate("window.__hd2d.hold(true)")
                    pg.wait_for_timeout(300)
                    grects = pg.evaluate("window.__hd2d.gamefxLineupRects()")
                    png = pg.screenshot()
                    pg.evaluate("window.__hd2d.hold(false); window.__hd2d.clearGamefxLineup(); window.__hd2d.hideActors(false); window.__hd2d.showOverlays && window.__hd2d.showOverlays(true)")
                    path = out / ("gamefx.png" if pi == 0 else f"gamefx_{pi + 1}.png")
                    path.write_bytes(png)
                    rep["shots"]["gamefx" if pi == 0 else f"gamefx_{pi + 1}"] = str(path)
                    gimg = np.array(Image.open(path).convert("RGB"))
                    scale = gimg.shape[1] / grects[0]["buf"][0] if grects else 1
                    for r in grects:
                        if abs(scale - 1) > 1e-6:
                            r = {**r, "x": r["x"] * scale, "y": r["y"] * scale}
                        gres.append({**sprite_check(gimg, g_atlas, r), "kind": r.get("kind")})
                    im16 = gimg.astype(np.int16)
                    nw = max(nw, float(((im16[..., 0] > 248) & (im16[..., 1] > 248) & (im16[..., 2] > 248)).mean()))
                    bf = max(bf, float((lum(gimg) > 225).mean()))
                gfx = {"effects": gres, "expected": len(gres), "pages": pages, "near_white": nw, "bright_frac": bf}

            # ---- action states: jump arc (quad lifts, shadow caster stays on the ground); heroes also attack/defend
            acts = None
            if pg.evaluate("typeof window.__hd2d.act === 'function'"):
                pg.evaluate("window.__hd2d.setTime('day')")
                pg.wait_for_timeout(300)
                acts = {"anims": pg.evaluate("window.__hd2d.actorState().anims")}
                for nm in (("jump", "attack", "defend") if "attack" in acts["anims"] else ("jump",)):
                    acts[nm] = pg.evaluate(ACT_SAMPLE, [nm, ACT_STEPS[nm]])

            # ---- camera lock under input
            pg.evaluate("window.__hd2d.setTime('day')")
            c0 = pg.evaluate("window.__hd2d.camState()")
            W, H = size
            for key in ("ArrowUp", "d", "ArrowLeft", "s"):
                pg.keyboard.down(key); pg.wait_for_timeout(500); pg.keyboard.up(key)
            pg.mouse.move(W * 0.3, H * 0.5); pg.mouse.down(); pg.mouse.move(W * 0.7, H * 0.35, steps=12); pg.mouse.up()
            pg.mouse.move(W * 0.5, H * 0.5); pg.mouse.down(button="right"); pg.mouse.move(W * 0.2, H * 0.8, steps=8); pg.mouse.up(button="right")
            pg.mouse.click(W * 0.55, H * 0.62)
            pg.wait_for_timeout(1200)
            pg.mouse.move(W * 0.5, H * 0.5)
            pg.mouse.wheel(0, 2400); pg.wait_for_timeout(400)
            cz_out = pg.evaluate("window.__hd2d.camState()")
            pg.mouse.wheel(0, -4800); pg.wait_for_timeout(400)
            cz_in = pg.evaluate("window.__hd2d.camState()")
            c1 = pg.evaluate("window.__hd2d.camState()")
            errors = pg.evaluate("window.__hd2d.errors")
            phones = {}
            pg.close()   # one SwiftShader page at a time: a busy second page makes touch timing flaky
            if phone:
                purl = f"http://127.0.0.1:{port}/index.html?{pre}t=day&freeze&pad=1"
                for nm, (vw, vh) in (("portrait", (390, 844)), ("landscape", (844, 390))):
                    phones[nm] = phone_check(b, purl, atlas, cam_spec, out, nm, vw, vh, timeout, extras=(nm == "portrait"))
                    if phones[nm].get("shot"):
                        rep["shots"][f"phone_{nm}"] = phones[nm]["shot"]
            b.close()
    finally:
        srv.shutdown()

    C = rep["checks"]
    # sprites
    allspr = [a for t in TIMES for a in sprites[t]["actors"] if "uniform_frac" in a]
    worst_u = min((a["uniform_frac"] for a in allspr), default=0)
    worst_c = min((a["atlas_corr"] for a in allspr), default=0)
    col_ratio = max((a["crop_colours"] / max(1, a["src_colours"]) for a in allspr), default=99)
    C["sprites_sharp"] = {"pass": bool(allspr) and worst_u >= 0.97 and worst_c >= 0.85,
                          "actors_checked": len(allspr), "worst_uniform_block_frac": worst_u, "worst_atlas_corr": worst_c,
                          "stable_capture": {t: sprites[t]["stable"] for t in TIMES},
                          "per_time": {t: [{k: v for k, v in a.items() if k != "_crop"} for a in sprites[t]["actors"]] for t in TIMES}}
    # camera
    dq = max(abs(a - b) for a, b in zip(c0["quat"], c1["quat"]))
    dq_z = max(max(abs(a - b) for a, b in zip(c0["quat"], c["quat"])) for c in (cz_out, cz_in))
    doff = max(abs(a - b) for a, b in zip(c0["offset"], c1["offset"]))
    zr = cam_spec.get("zoom", [c0["dist"], c0["dist"]])
    zoom_ok = all(zr[0] - 1e-3 <= c["dist"] <= zr[1] + 1e-3 for c in (cz_out, cz_in))
    C["camera_locked"] = {"pass": dq < 1e-5 and dq_z < 1e-5 and doff < 1e-3 and c0["fov"] == c1["fov"] and zoom_ok,
                          "quat_delta": dq, "quat_delta_zoom": dq_z, "view_dir_delta": doff, "fov": [c0["fov"], c1["fov"]],
                          "zoom_dist_out_in": [cz_out["dist"], cz_in["dist"]], "zoom_limits": zr,
                          "player_moved": [round(c0["pos"][0] - c1["pos"][0], 3), round(c0["pos"][2] - c1["pos"][2], 3)]}
    # bloom / blown highlights
    bl = {}
    ok = True
    for t in TIMES:
        im = imgs[t].astype(np.int16)
        white = float(((im[..., 0] > 248) & (im[..., 1] > 248) & (im[..., 2] > 248)).mean())
        clip = float((im.max(axis=2) >= 254).mean())
        L = lum(imgs[t])
        # glow wash: big low-contrast bright area = bloom soup
        bright = float((L > 225).mean())
        bl[t] = {"near_white": round(white, 5), "clipped_channel": round(clip, 5), "bright_frac": round(bright, 5)}
        ok &= white < 0.004 and clip < 0.02 and bright < 0.03
    C["no_bloom"] = {"pass": ok, **bl}
    # height
    hr = stats.get("heightRange") or [0, 0]
    ext = stats["worldMaxY"] - max(stats["worldMinY"], -2)
    C["height"] = {"pass": (hr[1] - hr[0]) >= 1.0 and ext >= 4.0, "walk_height_range_m": hr,
                   "world_y_extent_m": round(ext, 2)}
    # colours
    cc = {}
    ok = True
    for t in TIMES:
        q = (imgs[t] >> 3).astype(np.int32)
        n = len(np.unique(q[..., 0] * 1024 + q[..., 1] * 32 + q[..., 2]))
        cc[t] = n
        ok &= 300 <= n <= 12000
    C["colours"] = {"pass": ok and col_ratio <= 2.0, "frame_colours_5bit": cc,
                    "max_sprite_crop_vs_src_colour_ratio": round(col_ratio, 2)}
    # grades
    def mean_rgb(im):
        return im.reshape(-1, 3).mean(0)
    d, k_, n_ = (mean_rgb(imgs[t].astype(np.float32)) for t in TIMES)
    blue = lambda m: m[2] / max(1, m[0])
    nim = imgs["night"].astype(np.int16)
    warm = float(((nim[..., 0] - nim[..., 2] > 60) & (lum(imgs["night"]) > 130)).mean())
    C["grades"] = {"pass": blue(k_) > blue(d) and lum(n_[None, None])[0, 0] < 0.65 * lum(d[None, None])[0, 0] and warm > 0.002,
                   "blue_ratio": {"day": round(blue(d), 3), "dusk": round(blue(k_), 3), "night": round(blue(n_), 3)},
                   "mean_luma": {t: round(float(lum(imgs[t]).mean()), 1) for t in TIMES}, "night_warm_frac": round(warm, 4)}
    if fx is not None:
        ok_fx = [a for a in fx["effects"] if "uniform_frac" in a]
        wu = min((a["uniform_frac"] for a in ok_fx), default=0)
        wc = min((a["atlas_corr"] for a in ok_fx), default=0)
        sparse = sum(1 for a in fx["effects"] if a.get("skipped") == "sparse")
        C["effects_sharp"] = {"pass": len(ok_fx) + sparse == fx["expected"] and len(ok_fx) > 0 and fx["expected"] > 0 and wu >= 0.97 and wc >= 0.85
                              and fx["near_white"] < 0.004 and fx["bright_frac"] < 0.03,
                              "effects_checked": len(ok_fx), "effects_sparse": sparse, "effects_spawned": fx["expected"],
                              "worst_uniform_block_frac": wu, "worst_atlas_corr": wc,
                              "near_white": round(fx["near_white"], 5), "bright_frac": round(fx["bright_frac"], 5),
                              "per_effect": [{k: v for k, v in a.items() if k not in ("_crop", "src_colours", "crop_colours", "facing", "role")} for a in fx["effects"]]}
    if gfx is not None:
        ok_g = [a for a in gfx["effects"] if "uniform_frac" in a]
        wu = min((a["uniform_frac"] for a in ok_g), default=0)
        wc = min((a["atlas_corr"] for a in ok_g), default=0)
        C["gamefx_sharp"] = {"pass": len(ok_g) == gfx["expected"] and gfx["expected"] > 0 and wu >= 0.97 and wc >= 0.85
                             and gfx["near_white"] < 0.004 and gfx["bright_frac"] < 0.03,
                             "effects_checked": len(ok_g), "effects_spawned": gfx["expected"], "worst_uniform_block_frac": wu,
                             "worst_atlas_corr": wc, "near_white": round(gfx["near_white"], 5), "bright_frac": round(gfx["bright_frac"], 5),
                             "per_effect": [{k: v for k, v in a.items() if k not in ("_crop", "src_colours", "crop_colours", "facing", "role")} for a in gfx["effects"]]}
    if acts is not None:
        j = acts["jump"]
        jp = (j["ok"] and j["max_lift"] >= 0.2 and j["max_caster_gap"] < 1e-6 and j["rect_rise_px"] > 0 and j["ended"]
              and (("jump" not in acts["anims"]) or len(j["frames"].get("jump", [])) >= 2))
        res = {"jump": j}
        if "attack" in acts["anims"]:
            a_, d_ = acts["attack"], acts["defend"]
            res["attack"], res["defend"] = a_, d_
            jp = jp and a_["ok"] and len(a_["frames"].get("attack", [])) >= 2 and a_["ended"]
            jp = jp and d_["ok"] and bool(set(d_["frames"].get("defend", [])) & {2, 3}) and d_["ended"]
        C["actions"] = {"pass": bool(jp), "player_anims": acts["anims"], **res}
    if phone:
        C["phone"] = {"pass": bool(phones) and all(v.get("pass") for v in phones.values()), **phones}
    C["no_errors"] = {"pass": not errors and not [l for l in logs if "PAGEERROR" in l], "errors": errors, "console": logs[:20]}
    # documented per-area exemptions (scene.json game.qa_exempt: {check: reason}); only `height` and `grades` may be
    # exempted (design rules like "real terraces" that a floating isle cannot meet); sharpness / bloom / phone never
    for name, why in ((scene.get("game") or {}).get("qa_exempt") or {}).items():
        if name in ("height", "grades") and name in C and not C[name]["pass"]:
            C[name]["pass"], C[name]["exempt"] = True, why
            rep["notes"].append(f"{name} exempt: {why}")
    rep["pass"] = all(c["pass"] for c in C.values())
    (out / "check_scene.json").write_text(json.dumps(rep, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser(prog="hd2d check-scene", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", help="assembled folder (contains index.html + scene.json)")
    ap.add_argument("--out", help="output dir (default <root>/shots)")
    ap.add_argument("--size", default="1280x720")
    ap.add_argument("--scene-dir", default="", help="sub-folder holding scene.json (games: areas/<id>); paths in it are relative to it")
    ap.add_argument("--params", default="", help="extra query string for index.html (games: area=<id>&qa)")
    ap.add_argument("--no-phone", action="store_true", help="skip the phone portrait/landscape touch check")
    a = ap.parse_args(argv)
    w, h = (int(v) for v in a.size.split("x"))
    rep = run(a.root, a.out or Path(a.root) / "shots", (w, h), scene_dir=a.scene_dir, params=a.params, phone=not a.no_phone)
    for name, c in rep["checks"].items():
        brief = {k: v for k, v in c.items() if k not in ("pass", "per_time", "console", "per_effect")}
        if name == "phone":
            brief = {o: {k: (v.get("pass") if isinstance(v, dict) else v) for k, v in c[o].items() if k not in ("shot",)} for o in c if o != "pass"}
        print(f"  [{('EXEMPT' if c.get('exempt') else 'PASS') if c['pass'] else 'FAIL'}] {name:14s} {json.dumps(brief, default=lambda o: o.item() if hasattr(o, "item") else str(o))[:300]}")
    print(f"check-scene: {'PASS' if rep['pass'] else 'FAIL'}  shots: {', '.join(rep['shots'].values())}")
    return 0 if rep["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
