"""[ALFHEIM] Alfheim realm smoke (realm-alfheim branch): Lumenvale Glade + the Prism Vault + Lady Sylvaine.

    python3 games/hearthmoor/tests/smoke_alfheim.py [--out games/hearthmoor/shots/alfheim_smoke]

Runs standalone (its own server + headless Chromium), and smoke.py calls steps() in its own browser context after the
main run, so the main run's save is untouched. Boots ?qa (fresh state, no saving) with &combat&peace: enemies move but
stay calm until a step drops G.peace for a fight.
Covers (script flow, QA presets ?alfq=): Glimmer Steps loads with the staging townsfolk sheet; befriend sets the alliance;
Wispwood's Dimming quest; Lumi follows as her own neon sheet actor; the Prism Vault's gates + staging prism-shard sheet;
?beams=solve lights P2; Lady Sylvaine spawns at 6x; no JS errors. Screenshots: steps, wispwood, lumi, vault, Sylvaine.
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

    def alf():
        return T.ev("window.__hm.alfheim.qa()")

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
        return alf()

    try:
        # script flow (alfheim.md): Glimmer Steps -> Lumen Court (alliance) -> Wispwood (Lumi's nest) -> Prism Vault -> Sylvaine
        a = load("alfheim")
        T.step("Glimmer Steps loads (Alfheim module live, staging townsfolk sheet wired)",
               a["area"] == "alfheim" and T.ev("!!window.__hd2d.ctx.actors.meta.roles.lanternseller.sheet"), qa=a)
        shot("alf_steps")
        a = load("lumen_court", "&alfq=befriend")
        T.step("befriend preset: alliance befriend, gate + naming quests done", a["alliance"] == "befriend" and a["quests"]["alf_gate"] == 3, qa=a)
        a = load("wispwood", "&alfq=dim")
        T.step("Wispwood: the Dimming quest is live", a["area"] == "wispwood" and a["quests"]["alf_dim"] == 1, qa=a)
        shot("alf_wispwood")
        a = load("lumen_court", "&alfq=lumi")
        lumi = T.ev("(() => { const l = window.__hd2d.ctx.actors.list.find((x) => x.role === 'lumi'); return l ? { sheet: l.S.name, tall: l.S.fh / 32 } : null; })()")
        T.step("Lumi joins and follows as her own neon sheet actor (not the fx wisp)",
               a["lumi"]["on"] and a["lumi"]["body"] is None and lumi and lumi["sheet"] == "lumi", qa=a["lumi"], actor=lumi)
        shot("alf_lumi")
        a = load("prismvault", "&alfq=vault")
        T.step("Prism Vault: rooms gated, Lumi along, staging prism-shard sheet", a["gates"] is not None and a["lumi"]["on"]
               and T.ev("window.__hd2d.ctx.actors.meta.roles.prismshard.sheet === 'alfenemy'"), qa={"room": a["room"], "gates": a["gates"]})
        shot("alf_vault")
        a = load("prismvault", "&alfq=vault&beams=solve", "p2"); pg.wait_for_timeout(800); a = alf()
        T.step("beams=solve lights the P2 receivers", bool(a["beams"] and a["beams"]["lit"]), beams=a["beams"])
        a = load("prismvault", "&alfq=boss", "boss"); pg.wait_for_timeout(1500); a = alf()
        sy = a["sylvaine"]
        T.step("Lady Sylvaine spawns at 6x on her own boss sheet", bool(sy) and sy["scale"] >= 5.5 and sy["phase"] == 1, sylvaine=sy)
        shot("alf_sylvaine")
        T.step("no JS errors in the Alfheim run", not errors, errors=errors[:5])
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
    ap.add_argument("--out", default=str(GAME / "shots" / "alfheim_smoke"))
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
    (out / "smoke_alfheim.json").write_text(json.dumps(rep, indent=1))
    log(f"smoke_alfheim: {'PASS' if rep['pass'] else 'FAIL'} {sum(s['pass'] for s in T.steps)}/{len(T.steps)} steps in {rep['seconds']} s")
    sys.exit(0 if rep["pass"] else 1)


if __name__ == "__main__":
    main()
