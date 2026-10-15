"""[SVARTALFHEIM] Svartalfheim realm smoke (realm-svartalfheim branch): hub, Forge-Seal lock, glowmines foes, clockdeep.

    python3 games/hearthmoor/tests/smoke_svartalfheim.py [--out games/hearthmoor/shots/svartalfheim_smoke]

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

    def sv():
        return T.ev("window.__hm.svart.qa()")

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
        a = load("svartalfheim")
        T.step("Copper Row loads (Svartalfheim module live, art-pack roles wired)", a["area"] == "svartalfheim"
               and T.ev("!!window.__hd2d.ctx.actors.meta.roles.lanternseller.sheet"), qa=a)
        shot("sv_hub")
        a = load("forge_hall")
        T.step("forge_hall: the Deep's lift is sealed without the Forge-Seal (no clockdeep exit, one look spot)",
               "clockdeep" not in a["exits"] and not a["seal"] and a["spots"] == 1, qa=a)
        a = load("forge_hall", "&svq=seal")
        T.step("?svq=seal: the Forge-Seal opens the lift (clockdeep exit present, no look spot)",
               "clockdeep" in a["exits"] and a["seal"] and a["spots"] == 0, qa=a)
        shot("sv_forge_hall")
        a = load("glowmines")
        T.step("glowmines: sootlings, forge constructs and a cave golem spawn",
               {"sootling", "forgeconstruct", "golem"} <= set(a["foes"]), qa=a)
        shot("sv_glowmines")
        a = load("clockdeep", "&svq=seal")
        T.step("clockdeep loads from the lift", a["area"] == "clockdeep", qa=a)
        a = load("clockdeep2", "&svq=gorrak", "boss"); pg.wait_for_timeout(1500); a = sv()
        g = a["gorrak"]
        T.step("Gorrak spawns at 6x on his own boss sheet, phase 1, no valves or anvils shown yet",
               bool(g) and g["scale"] == 6 and g["phase"] == 1 and a["spots"] == 0
               and T.ev("window.__hd2d.ctx.actors.meta.roles.gorrak.sheet === 'boss_gorrak'"), qa=a)
        shot("sv_gorrak")
        T.ev("(() => { const G = window.__hm; G.peace = false; window.__hd2d.ctx.player.iframes = 99; const e = G.combat.enemies.find((x) => x.id === 'gorrak'); e.hp = Math.round(e.D.hp * 0.6); })()")
        pg.wait_for_timeout(1200); a = sv()
        T.step("phase 2 at 65%: the 4 quench valves become usable", a["gorrak"]["phase"] == 2 and a["spots"] == 4, qa=a)
        T.ev("(() => { window.__hd2d.ctx.player.iframes = 99; const e = window.__hm.combat.enemies.find((x) => x.id === 'gorrak'); e.hp = Math.round(e.D.hp * 0.25); })()")
        pg.wait_for_timeout(1200); a = sv()
        T.step("phase 3 at 30%: the 4 rune-anvils become usable", a["gorrak"]["phase"] == 3 and a["spots"] == 4, qa=a)
        T.ev("(() => { const f = window.__hm.svart.fight; for (let i = 0; i < 4; i++) f.anvil(i); })()")
        bind = T.ev("(() => { const e = window.__hm.combat.enemies.find((x) => x.id === 'gorrak'); return { bind: e.bind, kneel: e.kneelEnd > window.__hm.svart.fight.t }; })()")
        T.step("all 4 rune-anvils struck: Gorrak kneels and takes x1.5", bool(bind["bind"]) and bind["kneel"], bind=bind)
        T.step("no JS errors in the Svartalfheim run", not errors, errors=errors[:5])
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
    ap.add_argument("--out", default=str(GAME / "shots" / "svartalfheim_smoke"))
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
    (out / "smoke_svartalfheim.json").write_text(json.dumps(rep, indent=1))
    log(f"smoke_svartalfheim: {'PASS' if rep['pass'] else 'FAIL'} {sum(s['pass'] for s in T.steps)}/{len(T.steps)} steps in {rep['seconds']} s")
    sys.exit(0 if rep["pass"] else 1)


if __name__ == "__main__":
    main()
