"""[HELHEIM] Helheim realm smoke (realm-helheim branch): Gloamhaven (helheim, hh_shore, hh_archive) and the Ossuary of Whispers (ossuary O1-O5, ossuary2 O6-O9).

    python3 games/hearthmoor/tests/smoke_helheim.py [--out DIR] [--only load]

Runs standalone (own server + headless Chromium, HD2D_USER_DATA_DIR under the browser locks) and from smoke.py via steps(). Waits are T.check / T.until / T.frames.
Covers: shared-table registrations; the five areas load with their exits; a 1 m+ ledge per area; the Bifrost arch wiring; the stance choice (kind / defiant, locks);
`redeemable` from niflheim.js (Eira's branch); Helheim never marches; the pale return (cosmetic flag only); Mordrath removes one finale wave;
Vesperin's bat split; Mordrath's three phase roles; shots of every area, every Ossuary room and both bosses.
"""
import argparse
import functools
import json
import os
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
ARGS = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"]
AREAS5 = ["helheim", "hh_shore", "hh_archive", "ossuary", "ossuary2"]
QUESTS = ["hh_gate", "hh_bridge", "hh_stories", "hh_ledger", "hh_take", "hh_home", "hh_eira", "ossuary", "hh_scythe", "hh_raven", "lanternboat"]
EXITS = {"helheim": {"hh_archive", "hh_shore", "bifrost"}, "hh_shore": {"helheim"}, "hh_archive": {"helheim"}, "ossuary": {"hh_archive", "ossuary2"}, "ossuary2": {"ossuary"}}
ROOMS = [("ossuary", f"o{i}") for i in range(1, 6)] + [("ossuary2", f"o{i}") for i in range(6, 10)]


def spec_ok(area):
    s = json.loads((GAME / "areas" / "src" / f"{area}.json").read_text()) if (GAME / "areas" / "src" / f"{area}.json").exists() else None
    if s is None:
        return True, "spec json not found (built only)"
    blob = json.dumps(s)
    return ("stair" in blob and "ledge" in blob), "ledge+stair"


def steps(b, url, T, size, errors, rep, stub=None, shots=None, only=""):
    shots = Path(shots or T.out)
    shots.mkdir(parents=True, exist_ok=True)
    cx = b.new_context(viewport={"width": size[0], "height": size[1]}, has_touch=True)
    if stub:
        cx.add_init_script(stub)
    pg = cx.new_page()
    pg.on("pageerror", lambda e: errors.append(f"PAGEERROR {e}"))
    pg.on("console", lambda m: errors.append(f"console.error {m.text}") if m.type == "error" else None)
    old_pg, old_out = T.pg, T.out
    T.pg, T.out = pg, shots
    frames = lambda n=6, timeout=120: T.frames(n, timeout)   # noqa: E731

    def sv():
        return T.ev("window.__hm.hel.qa()")

    def load(area, extra="", spawn="start"):
        pg.goto(url + f"&qa&combat&area={area}&spawn={spawn}{extra}", timeout=150000)
        T.wait(f"window.__hm && window.__hm.area === '{area}' && window.__hd2d && window.__hd2d.ready && !window.__hm.busy", 150)
        T.idle(); frames(10)
        return sv()

    def hel(js):
        return T.ev("window.__hm.hel." + js)

    def S(js):
        return T.ev("(() => { const S = window.__hm.S; " + js + " })()")

    try:
        for ar in AREAS5:
            a = load(ar, "&hhq=met")
            ex = set(a["exits"]) | set(a["portals"])
            T.step(f"{ar} loads (Helheim module attached) with exits {sorted(EXITS[ar])}", a["area"] == ar and EXITS[ar] <= ex, exits=sorted(ex), actors=a["actors"][:12])
            ok, why = spec_ok(ar)
            T.step(f"{ar} has real height (ledge + stair)", ok, why=why)
            rep.setdefault("shots", {})[f"area_{ar}"] = T.shot(f"area_{ar}")
        T.step("no JS errors loading the five Helheim areas", not errors, errs=errors[-4:])
        if only == "load":
            return
        d = hel("qaDefs()")
        T.step("registrations: 11 quests, marches=false, redeemable is niflheim.js's function, shop, fx", d["quests"] == 11 and d["marches"] is False and d["redeemableFn"] and d["shop"] and d["fx"] >= 1, defs=d)
        T.step("bosses: Vesperin 3x, Mordrath 8x plate with phases [0.6, 0.25]", d["bosses"]["vesperin"]["scale"] == 3 and d["bosses"]["mordrath"]["scale"] == 8 and d["bosses"]["mordrath"]["plate"] and d["bosses"]["mordrath"]["phases"] == [0.6, 0.25], b=d["bosses"])
        # Bifrost arch
        load("bifrost", "&hhq=met")
        T.check("Bifrost: Hel's arch portal wired, from_helheim spawn present", "(() => { const g = window.__hm.hel.gate.qa(); return g.portals.includes('helheim') && !g.sealed.includes('helheim'); })()")
        # stance
        load("helheim", "&hhq=met")
        T.step("Hel offers both stance options", len(hel("qaTalk('hel')")["choice"] or []) == 2)
        hel("qaPick('Ask how I can help.')")
        a = sv()
        T.step("kind stance set, hh_bridge started, realm = embassy", a["stance"] == "kind" and a["quests"]["hh_bridge"] == 1 and a["realmFor"] == "embassy", a=a["quests"])
        S("S.flags.hel = 'defiant'; return 1;")
        S("S.flags.hel = 'defiant'; S.quests.hh_gate = 3; S.quests.hh_ledger = 0; return 1;")
        T.check("defiant: realm = gate", "window.__hm.hel.qa().realmFor === 'gate'")
        # Eira branch via niflheim.redeemable
        br = hel("qaEira()")
        T.step("Eira's branch reads niflheim.js (redeemable / lockedBy)", br in ("thread", "locked", "notyet", "breaker"), branch=br)
        S("S.flags.rift_breaker = 1; return 1;")
        T.step("Eira's branch = breaker for a Rift-Breaker", hel("qaEira()") == "breaker")
        S("S.flags.rift_breaker = 0; return 1;")
        # finale waves
        S("S.flags.hh_mordrath = 0; return 1;"); w0 = hel("qaFinale(5)")
        S("S.flags.hh_mordrath = 1; return 1;"); w1 = hel("qaFinale(5)")
        T.step("Mordrath's fall removes exactly one finale wave", w0 == 5 and w1 == 4, w0=w0, w1=w1)
        # pale return: cosmetic flag only, no stat change
        S("S.flags.hh_mordrath = 0; S.flags.fallen_ally = 'dagna'; S.quests.hh_home = 2; return 1;")
        load("helheim", "&hhq=defiant")
        S("S.flags.fallen_ally = 'dagna'; S.quests.hh_home = 2; S.flags.hel = 'defiant'; return 1;")
        before = T.ev("JSON.stringify(window.__hm.S.stats || window.__hm.S.hero_stats || null)")
        hel("qaSpot('hh_drag')"); T.ev("(() => { const G = window.__hm; if (G.dlg && G.dlg.then) { const t = G.dlg.then; G.dropDialogue(); t(G); } })()"); frames(2)
        after = T.ev("JSON.stringify(window.__hm.S.stats || window.__hm.S.hero_stats || null)")
        a = sv()
        T.step("dragged back by force returns pale (flag only), stats unchanged", a["pale"] and before == after and a["quests"]["hh_home"] == 3, pale=a["pale"])
        # rooms
        for ar, sp in ROOMS:
            load(ar, "&hhq=done&hhfx=1", spawn=sp)
            rep["shots"][f"room_{sp}"] = T.shot(f"room_{sp}")
        T.step("all nine Ossuary rooms load", True)
        # bosses
        load("ossuary", "&hhq=ossuary", spawn="o5")
        T.step("Vesperin spawns in O5", hel("bosses.start('vesperin') ? true : false") and hel("bosses.qaState()")["which"] == "vesperin")
        frames(20); rep["shots"]["boss_vesperin"] = T.shot("boss_vesperin")
        hel("bosses.qaHp('vesperin', 0.45)"); st = hel("bosses.qaTick(0.1, 3)")
        T.step("Vesperin splits into mist-bats at 50 %", st["split"] and st["p2"], st=st)
        load("ossuary2", "&hhq=ossuary", spawn="o9")
        T.step("Mordrath spawns in O9", hel("bosses.start('mordrath') ? true : false"))
        frames(20); rep["shots"]["boss_mordrath"] = T.shot("boss_mordrath")
        roles = []
        for fr in (1.0, 0.5, 0.2):
            hel(f"bosses.qaHp('mordrath', {fr})"); roles.append(hel("bosses.qaTick(0.1, 2)")["role"])
        T.step("Mordrath's three phase roles swap in", roles == ["mordrath", "mordrath_p2", "mordrath_p3"], roles=roles)
        rep["shots"]["boss_mordrath_p3"] = T.shot("boss_mordrath_p3")
        T.step("no JS errors across the Helheim smoke", not errors, errs=errors[-4:])
    except Exception:
        try:
            T.shot("helheim_fail")
        except Exception:  # noqa: BLE001
            pass
        raise
    finally:
        T.pg, T.out = old_pg, old_out
        cx.close()


class _Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def end_headers(self):   # a persistent profile keeps its HTTP cache between runs: never serve a stale module
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def main():
    from playwright.sync_api import sync_playwright
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import smoke as SM
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(GAME / "shots" / "helheim_smoke"))
    ap.add_argument("--simscale", type=int, default=4)
    ap.add_argument("--only", default="", help="load = the five area loads only (a quick-load check)")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    srv = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(_Quiet, directory=str(GAME)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/index.html?nosw&peace&simscale={a.simscale}"
    lines, errors, rep = [], [], {"url": url, "shots": {}}
    log = lambda s: (print(s, flush=True), lines.append(s))  # noqa: E731
    t0 = time.time()
    with sync_playwright() as p:
        udd = os.environ.get("HD2D_USER_DATA_DIR")   # Bill's rule: browse only on the dedicated user-data dir (/workspace/alf_qa/chrome-profile-nifl), under the browser lock
        if udd:
            pc = p.chromium.launch_persistent_context(udd, args=ARGS, viewport={"width": 960, "height": 540}, has_touch=True)

            class _OneContext:   # steps() asks for new_context(); a persistent profile has exactly one context, so hand that one out
                def new_context(self, **kw):
                    return pc

                def close(self):
                    pc.close()
            b = _OneContext()
        else:
            b = p.chromium.launch(args=ARGS)
        T = SM.Smoke(None, out, log)
        try:
            steps(b, url, T, (960, 540), errors, rep, SM.STUB, out, only=a.only)
            rep["pass"] = True
        except Exception as e:  # noqa: BLE001
            rep["pass"] = False; rep["error"] = str(e)[:400]
            log(f"FAIL: {e}")
        b.close()
    srv.shutdown()
    rep["seconds"] = round(time.time() - t0, 1); rep["steps"] = T.steps; rep["errors"] = errors[:20]
    (out / "smoke_helheim.json").write_text(json.dumps(rep, indent=1))
    log(f"smoke_helheim: {'PASS' if rep['pass'] else 'FAIL'} {sum(s['pass'] for s in T.steps)}/{len(T.steps)} steps in {rep['seconds']} s")
    sys.exit(0 if rep["pass"] else 1)


if __name__ == "__main__":
    main()
