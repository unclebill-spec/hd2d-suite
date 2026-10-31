"""Split service-worker precache check (GD call Oct 30): fresh profile -> SW 'activated' (time recorded), boot bar seen,
offline title reload, offline before the fill (first realm plays, a lazy area gives the friendly note, no crash), saved-game
resume into a lazy area online, full background fill -> a lazy area plays offline, an old hearthmoor-v1-* cache upgrades cleanly.
--throttle KBPS: only the slow-link check (the test server caps ALL traffic, page + SW, to KBPS kB/s with 150 ms per request: DevTools
throttling does not reach service-worker fetches) -> SW activated time, first realm cached time, offline title reload.
  HM_IN_BROWSER_LOCK=1 flock /workspace/.hm-logs/browser.lock timeout 1500 python3 tests/smoke_sw.py [--shots DIR] [--skip-fill] [--throttle 200]"""
import argparse, functools, json, sys, tempfile, threading, time
from http.server import ThreadingHTTPServer
from pathlib import Path
GAME = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GAME / "tests"))
from smoke import ARGS, Quiet

class Bucket:   # one shared token bucket: the whole "link" is KBPS kB/s
    def __init__(self, kbps): self.rate = kbps * 1000; self.t = time.time(); self.lk = threading.Lock()
    def take(self, n):
        with self.lk: self.t = max(self.t, time.time()) + n / self.rate; wake = self.t
        d = wake - time.time()
        if d > 0: time.sleep(d)
def throttled(bucket):
    class T(Quiet):
        def copyfile(self, src, out):
            time.sleep(0.15)
            while (b := src.read(16384)): bucket.take(len(b)); out.write(b)
    return T

READY = "window.__hm && __hm.ready && document.getElementById('boot').classList.contains('gone')"
SAVE = {"v": 2, "cls": "wildcaller", "area": "rotwood", "pos": None, "hp": 30}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--shots", default=""); ap.add_argument("--skip-fill", action="store_true"); ap.add_argument("--throttle", type=float, default=0); a = ap.parse_args()
    shots = Path(a.shots) if a.shots else None
    if shots: shots.mkdir(parents=True, exist_ok=True)
    srv = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(throttled(Bucket(a.throttle)) if a.throttle else Quiet, directory=str(GAME)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}/"
    fails, rep = [], {}
    def ok(name, cond, **info):
        print(("PASS " if cond else "FAIL ") + name, json.dumps(info)[:400], flush=True); rep[name] = {"pass": bool(cond), **info}; (None if cond else fails.append(name))
    from playwright.sync_api import sync_playwright
    def sw_state(pg): return pg.evaluate("navigator.serviceWorker.getRegistration().then(r => r ? [r.installing && r.installing.state, r.waiting && r.waiting.state, r.active && r.active.state] : null)")
    def caches(pg): return pg.evaluate("caches.keys().then(async ks => Object.fromEntries(await Promise.all(ks.map(async k => [k, (await (await caches.open(k)).keys()).length]))))")
    def wait_active(pg, t0, tmax=600):
        while time.time() - t0 < tmax:
            st = sw_state(pg)
            if st and st[2] == 'activated' and pg.evaluate("!!navigator.serviceWorker.controller"): return time.time() - t0
            time.sleep(0.25)
        return None
    def first_ready(pg, t0, tmax):
        n = core_n()
        while time.time() - t0 < tmax:
            c = caches(pg); k = [v for kk, v in c.items() if kk.startswith("hearthmoor-core-")]
            if k and k[0] >= n: return time.time() - t0
            time.sleep(1)
        return None
    def try_area(pg, area):
        r = pg.evaluate(f"(async () => {{ try {{ const r = await __hm.loadArea('{area}', 'start'); return [String(r), __hm.area, document.getElementById('toast').textContent]; }} catch (e) {{ return ['throw', String(e)]; }} }})()")
        return r
    with sync_playwright() as p:
        for mode in (("throttled",) if a.throttle else ("upgrade", "main")):
            prof = tempfile.mkdtemp(prefix="hmsw-")
            ctx = p.chromium.launch_persistent_context(prof, args=ARGS, viewport={"width": 960, "height": 600})
            pg = ctx.pages[0] if ctx.pages else ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
            if mode == "upgrade":   # an old v1 cache + a v1-style entry, as left by the old sw.js
                pg.goto(base + "icons/icon-192.png")
                pg.evaluate(f"caches.open('hearthmoor-v1-0123456789').then(c => c.addAll(['{base}index.html', '{base}icons/icon-192.png']))")
                ok("v1 cache seeded", "hearthmoor-v1-0123456789" in caches(pg), caches=caches(pg))
            t0 = time.time(); fr = []
            pg.goto(base + ("index.html?noattract&fillgap=3000" if mode != "upgrade" else "index.html?noattract&nofill"))
            for _ in range(400):
                if pg.evaluate(READY): break
                fr.append(pg.evaluate("(() => { const $ = (i) => document.getElementById(i); return [!!($('bootart') && !$('bootart').hidden) || !!($('bootbar') && !$('bootbar').hidden), $('bootpct') && $('bootpct').textContent]; })()"))
                if shots and mode == "main" and len(fr) == 3: pg.screenshot(path=str(shots / "boot_bar.png"))
                time.sleep(0.05)
            pg.wait_for_function(READY, timeout=180000); tp = time.time() - t0
            tact = wait_active(pg, t0)
            ck = caches(pg)
            if mode == "upgrade":
                ok("v1 cache upgrades cleanly (v1 deleted, core+lazy versioned caches)", tact is not None and not any(k.startswith("hearthmoor-v1-") for k in ck) and any(k.startswith("hearthmoor-core-") for k in ck), activated_s=tact and round(tact, 2), caches=ck, errors=errs[:3])
                ctx.close(); continue
            if mode == "throttled":
                ok(f"throttled {a.throttle:g} kB/s: SW reaches activated", tact is not None, activated_s=tact and round(tact, 1), playable_s=round(tp, 1), caches=caches(pg))
                tf = first_ready(pg, t0, 1300)
                ok(f"throttled {a.throttle:g} kB/s: first realm cached", tf is not None, first_realm_s=tf and round(tf, 1), caches=caches(pg))
                ctx.set_offline(True); pg.reload()
                try: pg.wait_for_function(READY, timeout=120000); t_ok = True
                except Exception: t_ok = False
                ok(f"throttled {a.throttle:g} kB/s: offline title reload", t_ok and pg.evaluate("!document.getElementById('titlescreen').hidden"), errors=errs[:3])
                if shots: pg.screenshot(path=str(shots / "throttled_offline_title.png"))
                ok("no page errors", not errs, errors=errs[:5]); ctx.close(); continue
            widths = [w for vis, w in fr if vis]
            ok("boot bar shown while loading, progress grows", len(widths) > 1 and len(set(widths)) > 1, samples=len(fr), widths=widths[:3] + widths[-3:])
            ok("fresh profile: SW reaches activated", tact is not None, activated_s=tact and round(tact, 2), playable_s=round(tp, 2), caches=ck)
            tf = first_ready(pg, t0, 600)
            ok("first realm cached by the background fill (lazy fill still running)", tf is not None, first_realm_s=tf and round(tf, 1), caches=caches(pg))
            # offline before the fill: title reload, first realm plays, lazy area -> friendly note
            ctx.set_offline(True)
            pg.reload(); 
            try: pg.wait_for_function(READY, timeout=90000); t_ok = True
            except Exception: t_ok = False
            ok("offline reload of the title screen", t_ok and pg.evaluate("!document.getElementById('titlescreen').hidden"), errors=errs[:3])
            if shots: pg.screenshot(path=str(shots / "offline_title.png"))
            rl = [try_area(pg, x) for x in ("lane", "mossglen", "hollows")]
            ok("offline before fill: first realm areas load", all(r[1] == x for r, x in zip(rl, ("lane", "mossglen", "hollows"))), res=rl)
            r = try_area(pg, "rotwood")
            ok("offline before fill: lazy area -> friendly message, no crash", r[0] == "false" and r[1] == "hollows" and "mists" in r[2] and pg.evaluate("__hm.ready"), res=r, errors=errs[:3])
            if shots: pg.screenshot(path=str(shots / "offline_lazy_msg.png"))
            ctx.set_offline(False)
            # saved-game resume into a lazy area (online)
            pg.evaluate(f"localStorage.setItem('hearthmoor-slot-1-v2', JSON.stringify({json.dumps(SAVE)})); localStorage.setItem('hearthmoor-lastslot', '1')")
            pg.goto(base + "index.html?noattract&nofill"); pg.wait_for_function(READY, timeout=120000)
            pg.evaluate("document.getElementById('btnCont').click()")
            try: pg.wait_for_function("__hm.area === 'rotwood' && !__hm.busy && __hm.game && __hm.game.ctx", timeout=120000); rs = True
            except Exception: rs = False
            ok("saved-game resume into a lazy area (rotwood) online", rs, area=pg.evaluate("__hm.area"), errors=errs[:3])
            if not a.skip_fill:
                pg.goto(base + "index.html?noattract&fillgap=0"); pg.wait_for_function(READY, timeout=120000)
                t1 = time.time()
                done = False
                while time.time() - t1 < 900:
                    st = pg.evaluate("(async () => { const k = await caches.keys(); const l = k.find(x => x.startsWith('hearthmoor-lazy-')); return l ? (await (await caches.open(l)).keys()).length : 0; })()")
                    if st >= rep_lazy_n(): done = True; break
                    time.sleep(3)
                ok("background fill completes", done, lazy_entries=st, fill_s=round(time.time() - t1, 1))
                ctx.set_offline(True)
                pg.reload(); pg.wait_for_function(READY, timeout=90000)
                res = [try_area(pg, x) for x in ("rotwood", "vanaheim", "verdant", "vh_village")]
                ok("offline after full fill: lazy areas play", all(r[1] == x for r, x in zip(res, ("rotwood", "vanaheim", "verdant", "vh_village"))), res=res, errors=errs[:3])
                ctx.set_offline(False)
            ok("no page errors", not errs, errors=errs[:5])
            ctx.close()
    srv.shutdown()
    print(json.dumps({"fails": fails}), flush=True)
    if shots: (shots / "smoke_sw.json").write_text(json.dumps(rep, indent=1))
    sys.exit(1 if fails else 0)

def core_n():
    import re
    t = (GAME / "sw.js").read_text()
    return sum(len(json.loads(re.search(rf"const {k} = (\[.*?\]);\n", t).group(1))) for k in ("SHELL_FILES", "FIRST_FILES")) + 1

def rep_lazy_n():
    import re
    return len(json.loads(re.search(r"const LAZY_FILES = (\[.*?\]);\n", (GAME / "sw.js").read_text()).group(1))) + 1   # + the hash meta entry

if __name__ == "__main__":
    main()
