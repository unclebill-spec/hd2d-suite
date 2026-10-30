"""Title attract demo check (WILL-SPEC sec 19): idle 40 s on the title -> the demo starts with real combat (enemy HP drops or a
swing / cast fired), localStorage is byte-identical before / after, a key and a click each end it within ~0.5 s, 0 JS errors.
  HM_IN_BROWSER_LOCK=1 flock /workspace/.hm-logs/browser.lock python3 tests/smoke_attract.py [--shots DIR] [--idle 40]"""
import argparse, functools, json, sys, threading, time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
GAME = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GAME / "tests"))
from smoke import ARGS, Quiet   # same chromium flags + quiet server as the main smoke

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--shots", default=""); ap.add_argument("--idle", type=float, default=40); ap.add_argument("--scenes", type=int, default=1)
    a = ap.parse_args(); shots = Path(a.shots) if a.shots else None
    if shots: shots.mkdir(parents=True, exist_ok=True)
    srv = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(GAME)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    from playwright.sync_api import sync_playwright
    fails, errs, t0 = [], [], time.time()
    def ok(name, cond, **info):
        print(("PASS " if cond else "FAIL ") + name, json.dumps(info)[:300]); (None if cond else fails.append(name))
    with sync_playwright() as p:
        b = p.chromium.launch(args=ARGS); pg = b.new_page(viewport={"width": 960, "height": 600})
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(f"http://127.0.0.1:{srv.server_address[1]}/index.html?nosw&attract")
        pg.wait_for_function("window.__hm && __hm.ready && __hm.attractDemo", timeout=180000)
        pg.evaluate("localStorage.setItem('hearthmoor-attract-probe', 'x')")   # something to compare (written before the demo)
        dump = "JSON.stringify(Object.keys(localStorage).sort().map(k => [k, localStorage.getItem(k)]))"
        before = pg.evaluate(dump)
        st = pg.evaluate("__hm.attractDemo.state()"); ok("title idle counting", not st["active"], **st)
        tw = time.time()
        pg.wait_for_function("__hm.attractDemo.state().active", timeout=int((a.idle + 30) * 1000))
        ok("demo starts after ~40 s idle", time.time() - tw >= a.idle - 3, waited=round(time.time() - tw, 1))
        for k in range(a.scenes):
            pg.wait_for_function("(() => { const s = __hm.attractDemo.state(); return s.active && !s.busy && s.t > 1; })()", timeout=90000)
            hp0 = pg.evaluate("__hm.combat.alive().reduce((c, e) => c + e.hp, 0)")
            time.sleep(9)
            st = pg.evaluate("__hm.attractDemo.state()"); hp1 = pg.evaluate("__hm.combat.alive().reduce((c, e) => c + e.hp, 0)")
            ok(f"combat in {st['scene']}", hp1 < hp0 or st["swings"] > 0 or st["casts"] > 0, hp0=hp0, hp1=hp1, **st)
            if shots: pg.screenshot(path=str(shots / f"attract_{k}_{st['scene']}.png"))
            if k < a.scenes - 1:
                pg.evaluate("__hm.attractDemo.state().scene") ; pg.wait_for_function(f"__hm.attractDemo.state().scenes > {st['scenes']}", timeout=60000)
        t = time.time(); pg.keyboard.press("x")
        pg.wait_for_function("!__hm.attractDemo.state().active && __hm.title && !document.getElementById('titlescreen').hidden", timeout=5000)
        ok("key exits to title", time.time() - t < 0.8, s=round(time.time() - t, 2))
        pg.wait_for_function("!__hm.busy", timeout=60000); time.sleep(1)
        ok("title still up after key (no game started)", pg.evaluate("__hm.title && !__hm.picking"))
        pg.evaluate("__hm.attractDemo.begin()"); pg.wait_for_function("(() => { const s = __hm.attractDemo.state(); return s.active && !s.busy; })()", timeout=60000); time.sleep(2)
        t = time.time(); pg.mouse.click(480, 300)
        pg.wait_for_function("!__hm.attractDemo.state().active && __hm.title && !document.getElementById('titlescreen').hidden", timeout=5000)
        ok("click exits to title", time.time() - t < 0.8, s=round(time.time() - t, 2))
        time.sleep(2)
        ok("title still up after click", pg.evaluate("__hm.title && !__hm.picking"))
        after = pg.evaluate(dump)
        ok("storage byte-identical", before == after, before=len(before), after=len(after))
        ok("0 JS errors", not errs, errs=errs[:3])
        b.close()
    print(f"attract smoke: {len(fails)} FAIL in {time.time() - t0:.0f} s"); return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
