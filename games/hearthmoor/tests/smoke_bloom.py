"""[VANAHEIM C] Bloomtide minigames smoke (harvest + dance): own server + headless Chromium, desk 1280x720 and phone 412x915.

    HM_IN_BROWSER_LOCK=1 flock /workspace/.hm-logs/browser.lock timeout 900 python3 games/hearthmoor/tests/smoke_bloom.py [--out DIR] [--shots DIR]

Per viewport + game: Esc quit -> {won:false}, localStorage and G.S byte-unchanged, G.busy restored, overlay gone;
a stray tap (no cue near) scores nothing; a timed run (keys on schedule, plus touch taps) -> win, the only S change is
flags.vh_bloom_games[kind] = true; hit-feedback + result shots; reduced motion is picked up; also the rules unit tests
(node --test tests/test_bloom_rules.mjs) and 0 console errors. Exit 0 = pass.
"""
import argparse, functools, json, os, subprocess, sys, threading, time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
ARGS = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"]
SIZES = {"desk": (1280, 720, False), "phone": (412, 915, True)}


class _Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store"); super().end_headers()


SNAP = "JSON.stringify({ls: Object.keys(localStorage).sort().map(k => [k, localStorage.getItem(k)]), S: window.__hm.S, busy: !!window.__hm.busy})"
# schedule one keydown per cue at its exact time (+off ms) from the game's t0; returns at once
PLAY = """([off, every]) => { const st = window.__hm.bloom; const now = performance.now();
  st.times.forEach((t, i) => { if (i % every) return; setTimeout(() => dispatchEvent(new KeyboardEvent('keydown', {key: ' ', bubbles: true})), Math.max(0, st.t0 + t + off - now)); }); }"""


def run(pg, out, shots, name, kind, touch, log, checks):
    def ok(label, cond, extra=""):
        checks.append({"step": f"{name}/{kind}: {label}", "pass": bool(cond), "extra": str(extra)[:200]}); log(f"{'ok ' if cond else 'FAIL'} {name}/{kind}: {label} {extra}")
        if not cond:
            raise AssertionError(label)
    before = pg.evaluate(SNAP)
    # 1. quit -> no penalty, nothing written
    pg.evaluate(f"window.__r = null; window.__hm.startBloomGame('{kind}').then(r => window.__r = r)")
    pg.wait_for_selector("#bloomgame canvas"); ok("overlay open + busy", pg.evaluate("!!window.__hm.busy && !!window.__hm.bloom"))
    pg.wait_for_timeout(900); pg.keyboard.press("Escape"); pg.wait_for_function("window.__r !== null", timeout=10000)
    r = pg.evaluate("window.__r"); ok("quit -> won false", r["won"] is False, r)
    ok("quit: storage + state byte-unchanged", pg.evaluate(SNAP) == before)
    ok("overlay removed", pg.evaluate("!document.getElementById('bloomgame')"))
    # 2. stray tap + timed win
    pg.evaluate(f"window.__r = null; window.__hm.startBloomGame('{kind}').then(r => window.__r = r)"); pg.wait_for_selector("#bloomgame canvas")
    pg.wait_for_timeout(300)
    if touch:
        pg.tap("#bloomgame canvas")
    else:
        pg.mouse.click(640, 360)
    ok("stray tap scores nothing", pg.evaluate("window.__hm.bloom.judged.filter(Boolean).length") == 0)
    pg.evaluate(PLAY, [0, 1])
    first = pg.evaluate("window.__hm.bloom.times[0]")
    pg.wait_for_function("window.__hm.bloom && window.__hm.bloom.judged.filter(Boolean).length >= 2", timeout=30000)
    pg.wait_for_timeout(60)
    pg.screenshot(path=str(out / f"{name}-{kind}-hit.png"))
    pg.wait_for_selector("#bloomgame .bres.on", timeout=40000); pg.wait_for_timeout(500)
    pg.screenshot(path=str(out / f"{name}-{kind}-result.png"))
    res = pg.evaluate("window.__hm.bloom.result"); ok("timed run wins", res["won"], res)
    if touch:
        pg.wait_for_timeout(400); pg.tap("#bloomgame .bok")
    else:
        pg.keyboard.press("Enter")
    pg.wait_for_function("window.__r !== null", timeout=10000)
    r = pg.evaluate("window.__r"); ok("resolve {won, score}", r["won"] is True and r["score"] == res["score"], r)
    after = json.loads(pg.evaluate("JSON.stringify(window.__hm.S)")); b = json.loads(before)["S"]
    ok(f"flag vh_bloom_games.{kind} set", ((after.get("flags") or {}).get("vh_bloom_games") or {}).get(kind) is True)
    vb = (after.get("flags") or {}).pop("vh_bloom_games", None); (b.get("flags") or {}).pop("vh_bloom_games", None)
    ok("no other save change", after == b)
    ok("busy restored", pg.evaluate("!window.__hm.busy && !window.__hm.bloom"))
    # 3. a losing run (tap every 3rd cue) stays unwon and writes nothing new
    pg.evaluate(f"(() => {{ const f = window.__hm.S.flags; f.vh_bloom_games = {{}}; }})()")
    s0 = pg.evaluate(SNAP)
    pg.evaluate(f"window.__r = null; window.__hm.startBloomGame('{kind}').then(r => window.__r = r)"); pg.wait_for_selector("#bloomgame canvas")
    pg.evaluate(PLAY, [0, 3]); pg.wait_for_selector("#bloomgame .bres.on", timeout=40000)
    res = pg.evaluate("window.__hm.bloom.result"); ok("sparse run loses", not res["won"], res)
    pg.keyboard.press("Escape"); pg.wait_for_function("window.__r !== null", timeout=10000)
    ok("loss writes nothing", pg.evaluate(SNAP) == s0 and pg.evaluate("window.__r.won") is False)
    pg.evaluate(f"(() => {{ window.__hm.S.flags.vh_bloom_games = {json.dumps(vb)}; }})()")
    _ = first


def main():
    from playwright.sync_api import sync_playwright
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(GAME / "shots" / "bloom_smoke"))
    ap.add_argument("--simscale", type=int, default=4)
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    checks, errors, lines = [], [], []
    log = lambda s: (print(s, flush=True), lines.append(s))  # noqa: E731
    u = subprocess.run(["node", "--test", str(GAME / "tests" / "test_bloom_rules.mjs"), str(GAME / "tests" / "test_bloom_freeze.mjs")], capture_output=True, text=True)
    checks.append({"step": "unit: test_bloom_rules.mjs", "pass": u.returncode == 0}); log(f"unit tests: {'ok' if u.returncode == 0 else 'FAIL'}")
    srv = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(_Quiet, directory=str(GAME)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}/index.html?nosw&peace&qa&combat&simscale={a.simscale}&area=vanaheim&spawn=start"
    t0, passed = time.time(), u.returncode == 0
    with sync_playwright() as p:
        udd = os.environ.get("HD2D_USER_DATA_DIR")   # same launch as smoke_vanaheim: the dedicated warm profile under the browser lock
        pc = p.chromium.launch_persistent_context(udd, args=ARGS, viewport={"width": 1280, "height": 720}, has_touch=True) if udd else None
        b = None if udd else p.chromium.launch(args=ARGS)
        log(f"launch: {'persistent ' + udd if udd else 'fresh chromium.launch'}")
        for name, (w, h, touch) in SIZES.items():
            if pc:
                cx = pc; pg = pc.new_page(); pg.set_viewport_size({"width": w, "height": h})
            else:
                cx = b.new_context(viewport={"width": w, "height": h}, has_touch=touch, is_mobile=touch, device_scale_factor=1)
                pg = cx.new_page()
            pg.on("pageerror", lambda e: errors.append(f"PAGEERROR {e}"))
            pg.on("console", lambda m: errors.append(f"console.error {m.text}") if m.type == "error" else None)
            try:
                tl = time.time(); pg.goto(base, timeout=150000); log(f"{name}: goto ok {time.time() - tl:.0f}s")
                try:
                    pg.wait_for_function("window.__hm && window.__hm.area === 'vanaheim' && window.__hd2d && window.__hd2d.ready && !window.__hm.busy", timeout=150000)
                except Exception:
                    log(f"{name}: READY TIMEOUT dump " + json.dumps(pg.evaluate("({area: window.__hm && window.__hm.area, busy: window.__hm && window.__hm.busy, hd2dReady: !!(window.__hd2d && window.__hd2d.ready), Gready: window.__hm && window.__hm.ready, title: window.__hm && window.__hm.title})")) + " errors=" + json.dumps(errors[:10]))
                    raise
                log(f"{name}: ready {time.time() - tl:.0f}s"); pg.wait_for_timeout(1500)
                for kind in ("harvest", "dance"):
                    run(pg, out, out, name, kind, touch, log, checks)
                pg.evaluate("localStorage.setItem('hearthmoor-reduced-motion', '1')")
                pg.evaluate("window.__r = null; window.__hm.startBloomGame('harvest').then(r => window.__r = r)"); pg.wait_for_selector("#bloomgame canvas")
                rm = pg.evaluate("window.__hm.bloom.rm"); pg.keyboard.press("Escape"); pg.wait_for_function("window.__r !== null")
                pg.evaluate("localStorage.removeItem('hearthmoor-reduced-motion')")
                checks.append({"step": f"{name}: reduced motion respected", "pass": rm is True}); log(f"reduced motion: {rm}")
                passed = passed and rm is True
            except Exception as e:  # noqa: BLE001
                passed = False; log(f"FAIL {name}: {str(e)[:300]}")
            pg.close() if pc else cx.close()
        (pc or b).close()
    srv.shutdown()
    passed = passed and all(c["pass"] for c in checks) and not errors
    rep = {"pass": passed, "seconds": round(time.time() - t0, 1), "checks": checks, "errors": errors[:20]}
    (out / "smoke_bloom.json").write_text(json.dumps(rep, indent=1))
    log(f"smoke_bloom: {'PASS' if passed else 'FAIL'} {sum(c['pass'] for c in checks)}/{len(checks)} checks, {len(errors)} console errors, {rep['seconds']} s")
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
