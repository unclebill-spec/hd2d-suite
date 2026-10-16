"""[JOTUNHEIM] Jotunheim realm smoke (realm-jotunheim branch): Stonehollow (art installed, Bifrost gate, Welcome Ring, Grimsa, look-spots).

    python3 games/hearthmoor/tests/smoke_jotunheim.py [--out games/hearthmoor/shots/jotunheim_smoke]

Runs standalone (its own server + headless Chromium), and smoke.py calls steps() in its own browser context after the
main run, so the main run's save is untouched. Boots ?qa (fresh state, no saving) with &combat&peace: enemies move but
stay calm until a step drops G.peace for a fight.
Covers (QA presets ?jtq=): the art pack is installed in Stonehollow (giant sheets, Flurry neon twin + safe fallback); the area loads with its
actors and no JS errors; the Bifrost ice arch is sealed until the gate opens, then a portal with a return spawn; Grimsa's shop; the Welcome Ring
(lift stones, timing beat via ?lift=auto, quest 1 -> 3, reward); the Jarl's choice; look-spots. Screenshots: Stonehollow day / night.
"""
import argparse
import functools
import json
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
ARGS = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"]


def steps(b, url, T, size, errors, rep, stub=None, shots=None):
    """b: a playwright Browser; url: .../index.html?nosw&peace&simscale=N; T: smoke.Smoke (its pg is swapped here)"""
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
    cdp = cx.new_cdp_session(pg)

    def shot(name):
        rep.setdefault("shots", {})[name] = T.shot(name)

    def sv():
        return T.ev("window.__hm.jot.qa()")

    def screen(x, z, y=None):
        return T.ev(f"(() => {{ const c = window.__hd2d.ctx; return c.project({x}, {y if y is not None else f'c.heightAt({x}, {z})'}, {z}); }})()")

    def tap(x, y):
        t = time.time()
        cdp.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": x, "y": y, "id": 0}], "timestamp": t})
        cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": [], "timestamp": t + 0.05})

    def arrive(area, timeout=120):
        T.wait(f"window.__hm.area === '{area}' && !window.__hm.busy", timeout); T.idle(); pg.wait_for_timeout(500)

    def load(area, extra="", spawn="start"):
        pg.goto(url + f"&qa&combat&area={area}&spawn={spawn}{extra}")
        T.wait(f"window.__hm && window.__hm.area === '{area}' && window.__hd2d && window.__hd2d.ready && !window.__hm.busy", 150)
        T.idle(); pg.wait_for_timeout(1500)
        return sv()

    try:
        import hashlib
        art = Path(__file__).resolve().parents[1]
        h = lambda p_: hashlib.md5(Path(p_).read_bytes()).hexdigest()  # noqa: E731
        st = art / "areas/jotunheim/public/art/sprite"
        acts = json.loads((st / "actors.json").read_text())
        T.step("Flurry ships the neon twin as the main sheet, palette-safe as the fallback",
               h(st / "flurry.png") == h(art / "art/jotunheim/pets/flurry_neon.png") and h(st / "flurry_safe.png") == h(art / "art/jotunheim/pets/flurry.png")
               and acts["roles"]["pet_flurry"]["sheet"] == "flurry" and acts["roles"]["pet_flurry"].get("pet"))
        T.step("Stonehollow's townsfolk are the giant sheets (Grimsa, Brynja, Ulfar; Ulfar's own companion sheet 3x with combat_scale 2.4)",
               all(acts["roles"][r]["sheet"] == "jtnpc" for r in ("dwarftrader", "poolkeeper", "gnome", "wispcatcher", "elffolk")) and acts["roles"]["ulfar"]["sheet"] == "ulfar"
               and json.loads((st / "ulfar.json").read_text())["roles"]["ulfar"]["combat_scale"] == 2.4)
        a = load("jotunheim")
        T.step("Stonehollow loads (Jotunheim module live)", a["area"] == "jotunheim" and a["realm"] == "jotunheim" and "jotunheim" in a["built"], qa=a)
        T.step("its six giants are there (Grimsa, Skuli, Brynja, Ulfar + two villagers)", all(i in a["actors"] for i in ("jt_trader", "goatherd", "goatwife", "ulfar", "jt_a", "jt_b")), actors=a["actors"])
        T.step("cold fire and rune glows are lit (gamefx rows + point lights), the ice arch back to Bifrost is a portal",
               a["fx"] >= 10 and a["lights"] >= 8 and "bifrost" in a["portals"], fx=a["fx"], lights=a["lights"], portals=a["portals"])
        hs = T.ev("(() => { const c = window.__hd2d.ctx; return { plateau: c.heightAt(-1.6, -8), ground: c.heightAt(0, 6), stair: c.heightAt(0, -2.4) }; })()")
        T.step("real height: the Jarl's plateau stands 1.34 m up with a walkable stair", hs["plateau"] >= 1.0 and hs["ground"] < 0.2 and 0.2 < hs["stair"] < hs["plateau"], hs=hs)
        T.ev("window.__hd2d.setTime(0.5)"); pg.wait_for_timeout(600); shot("jt_day")
        # ---- the Bifrost gate: sealed until open, then a portal; the Stonehollow return spawn exists
        load("bifrost"); b0 = T.ev("window.__hm.jot.qa().gate")
        T.step("Bifrost: Jotunheim's ice arch is sealed for a stranger", "jotunheim" in b0["sealed"] and "jotunheim" not in b0["portals"] and not b0["open"], gate=b0)
        load("bifrost", "&jtq=open"); b1 = T.ev("window.__hm.jot.qa().gate")
        T.step("?jtq=open: the arch moves from sealed to portals and the return spawn is added", "jotunheim" not in b1["sealed"] and "jotunheim" in b1["portals"] and "from_jotunheim" in b1["spawns"], gate=b1)
        # ---- Grimsa's stall
        load("jotunheim"); t = T.ev("(() => { const G = window.__hm; return { goods: G.shopUI ? true : false, shop: !!window.__hm.jot.qa().shop }; })()")
        T.ev("window.__hm.jot.qaTalk('jt_trader')"); pg.wait_for_timeout(300)
        so = T.ev("(() => { const G = window.__hm; return { open: G.shopUI.open || null }; })()")
        T.step("Grimsa opens her stall (fur cloak, tea, cold-fire lamp)", t["shop"] and so["open"] == "jt_trader", so=so)
        T.ev("(() => { const G = window.__hm; G.shopUI.close(); })()")
        # ---- the Jarl's choice (she sits in the Hall next chunk; the entry is live now)
        o = T.ev("window.__hm.jot.qaTalk('jarl')")["choice"]
        T.step("Jarl Thyra's choice: befriend / conquer; no contract for a free player", "A friend. Let me prove you innocent." in o and "Midgard's. Hand over the Barrow Key." in o and len(o) == 2, options=o)
        T.ev("window.__hm.jot.qaPick('A friend. Let me prove you innocent.')"); a = sv()
        T.step("befriend: alliance set, The Stone Welcome starts", a["alliance"] == "befriend" and a["quest"] == 1, qa=a["quest"])
        # ---- the Welcome Ring: three lifts (?lift=auto), quest 1 -> 3
        load("jotunheim", "&jtq=befriend&lift=auto"); a = sv()
        T.step("Welcome Ring: three lift stones are live (spots) at quest stage 1", a["quest"] == 1 and a["lifts"] == 0 and a["spots"] >= 6, spots=a["spots"])
        g0 = T.ev("window.__hm.S.gold || 0")
        for i in range(3):
            T.ev(f"window.__hm.jot.qaLift({i})")
            T.ev("(() => { const G = window.__hm; if (G.dlg && G.dlg.then) { const t = G.dlg.then; G.dropDialogue(); t(G); } })()")
        pg.wait_for_timeout(400); a = sv(); g1 = T.ev("window.__hm.S.gold || 0")
        T.step("three lifts: the town cheers, The Stone Welcome completes (+20 gold, trusted)", a["lifts"] == 3 and a["quest"] == 3 and g1 - g0 == 20 and T.ev("window.__hm.S.flags.jt_trusted === 1"), qa=[a["lifts"], a["quest"], g0, g1])
        # ---- the look-spots (Hall door, cave path, frost prints) and the Giant Footprints entry point
        T.ev("(() => { const c = window.__hd2d.ctx; c.player.x = -3.4; c.player.z = -1.6; })()"); pg.wait_for_timeout(300)
        pr = T.ev("window.__hm.harbor.prompt()")
        T.step("the frost-prints look-spot prompts at the plateau foot", "frost prints" in (pr or ""), prompt=pr)
        T.ev("(() => { window.__hm.harbor.interact(); })()"); pg.wait_for_timeout(300)
        T.step("looking at the prints records the clue entry (S.found.jt_prints)", T.ev("window.__hm.S.found.jt_prints === 1"))
        T.ev("(() => { const G = window.__hm; G.dropDialogue && G.dropDialogue(); })()")
        T.step("no JS errors in the Jotunheim run", not [e for e in errors if "jotunheim" in e.lower() or "jotun" in e.lower()], errs=errors[-3:])
        shot("jt_ring")
        a = load("jotunheim"); T.ev("window.__hd2d.setTime(0.0)"); pg.wait_for_timeout(800); shot("jt_night")
    except Exception:
        shot("jt_fail")
        raise
    finally:
        T.pg, T.out = old_pg, old_out
        cx.close()


class _Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def main():
    from playwright.sync_api import sync_playwright
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import smoke as SM
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(GAME / "shots" / "jotunheim_smoke"))
    ap.add_argument("--simscale", type=int, default=4)
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    srv = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(_Quiet, directory=str(GAME)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/index.html?nosw&peace&simscale={a.simscale}"
    lines, errors, rep = [], [], {"url": url, "shots": {}}
    log = lambda s: (print(s, flush=True), lines.append(s))  # noqa: E731
    t0 = time.time()
    with sync_playwright() as p:
        b = p.chromium.launch(args=ARGS)
        T = SM.Smoke(None, out, log)
        try:
            steps(b, url, T, (960, 540), errors, rep, SM.STUB, out)
            rep["pass"] = True
        except Exception as e:  # noqa: BLE001
            rep["pass"] = False; rep["error"] = str(e)[:400]
            log(f"FAIL: {e}")
        b.close()
    srv.shutdown()
    rep["seconds"] = round(time.time() - t0, 1); rep["steps"] = T.steps; rep["errors"] = errors[:20]
    (out / "smoke_jotunheim.json").write_text(json.dumps(rep, indent=1))
    log(f"smoke_jotunheim: {'PASS' if rep['pass'] else 'FAIL'} {sum(s['pass'] for s in T.steps)}/{len(T.steps)} steps in {rep['seconds']} s")
    sys.exit(0 if rep["pass"] else 1)


if __name__ == "__main__":
    main()
