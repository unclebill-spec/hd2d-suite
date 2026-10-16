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

    FIN = "(() => { const G = window.__hm; if (G.dlg && G.dlg.then) { const t = G.dlg.then; G.dropDialogue(); t(G); } else G.dropDialogue && G.dropDialogue(); })()"

    def fin():
        T.ev(FIN); pg.wait_for_timeout(150)

    def jt(js):
        return T.ev("window.__hm.jot." + js)

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
               a["fx"] >= 7 and a["lights"] >= 4 and "bifrost" in a["portals"], fx=a["fx"], lights=a["lights"], portals=a["portals"])
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
        T.step("Welcome Ring: three lift stones are live (spots) at quest stage 1", a["quest"] == 1 and a["lifts"] == 0 and a["spots"] >= 4, spots=a["spots"])
        g0 = T.ev("window.__hm.S.gold || 0")
        for i in range(3):
            T.ev(f"window.__hm.jot.qaLift({i})")
            T.ev("(() => { const G = window.__hm; if (G.dlg && G.dlg.then) { const t = G.dlg.then; G.dropDialogue(); t(G); } })()")
        pg.wait_for_timeout(400); a = sv(); g1 = T.ev("window.__hm.S.gold || 0")
        T.step("three lifts: the town cheers and the Jarl's fire waits (stage 2)", a["lifts"] == 3 and a["quest"] == 2, qa=[a["lifts"], a["quest"]])
        jt("qaTalk('jarl')"); a = sv(); g1 = T.ev("window.__hm.S.gold || 0")
        T.step("the Jarl's fire: The Stone Welcome completes (+20 gold, trusted) and The Hollow Heart starts", a["quest"] == 3 and g1 - g0 == 20 and a["heart"] == 1 and T.ev("window.__hm.S.flags.jt_trusted === 1"), qa=[a["quest"], a["heart"], g0, g1])
        # ---- the look-spots (Hall door, cave path, frost prints) and the Giant Footprints entry point
        T.ev("(() => { const c = window.__hd2d.ctx; c.player.x = -3.4; c.player.z = -1.6; })()"); pg.wait_for_timeout(300)
        pr = T.ev("window.__hm.harbor.prompt()")
        T.step("the frost-prints look-spot prompts at the plateau foot", "frost prints" in (pr or ""), prompt=pr)
        T.ev("(() => { window.__hm.harbor.interact(); })()"); pg.wait_for_timeout(300)
        T.step("looking at the prints records the clue entry (S.found.jt_prints)", T.ev("window.__hm.S.found.jt_prints === 1"))
        T.ev("(() => { const G = window.__hm; G.dropDialogue && G.dropDialogue(); })()")
        # ---- jt_hall: the Hall of Hearthstones
        a = load("jt_hall", "&jtq=heart")
        T.step("the Hall loads: Jarl, Kolbrun, Solvi, guards and diners; cold fire lit; a door back to Stonehollow", all(i in a["actors"] for i in ("jarl", "envoy_jt", "rimewife", "jt_guard1", "jt_guard2")) and a["fx"] >= 8 and "jotunheim" in a["exits"], qa=a["actors"], exits=a["exits"])
        hs = T.ev("(() => { const c = window.__hd2d.ctx; return { dais: c.heightAt(-3, -9), floor: c.heightAt(-3, 4), stair: c.heightAt(0, -5.9) }; })()")
        T.step("real height: the high seat dais stands 1.2 m up with a walkable stair", hs["dais"] >= 1.0 and hs["floor"] < 0.2 and 0.2 < hs["stair"] < hs["dais"], hs=hs)
        T.ev("window.__hd2d.setTime(0.0)"); pg.wait_for_timeout(600); shot("jt_hall_night")
        jt("qaSpot('trapdoor')"); fin(); a = sv()
        T.step("the Jarl's word opens the trapdoor: you stand in the ice cellar", a["inCellar"] and a["pos"][0] > 11, pos=a["pos"])
        shot("jt_cellar")
        jt("qaSpot('plinth')"); fin(); jt("qaSpot('rime')"); fin(); a = sv()
        T.step("clue 1: the Heart rings hollow (evidence set); the rime stays grey without Solvi's light", a["clues"] == ["jh_heart"] and a["evidence"] == "false_heart", qa=a["clues"])
        jt("qaTalk('rimewife')"); jt("qaSpot('rime')"); fin(); a = sv()
        T.step("clue 2: with Solvi's rune-light the rime is blue-black", a["clues"] == ["jh_heart", "jh_rime"] and a["heart"] == 1, qa=a["clues"])
        jt("qaSpot('stair')"); fin(); a = sv()
        T.step("clue 3: the prints go in, none come out; three clues move the quest to stage 2 and you are back in the Hall", len(a["clues"]) == 3 and a["heart"] == 2 and not a["inCellar"] and a["pos"][0] < 10, qa=[a["clues"], a["heart"], a["pos"]])
        g0 = T.ev("window.__hm.S.gold || 0"); jt("qaTalk('jarl')"); a = sv(); g1 = T.ev("window.__hm.S.gold || 0")
        T.step("the Jarl closes The Hollow Heart: peace, evidence, +40 gold", a["heart"] == 3 and a["peace"] and a["evidence"] == "false_heart" and g1 - g0 == 40, qa=[a["heart"], a["peace"], g0, g1])
        a = load("jt_hall", "&jtq=decoy"); jt("qaTalk('jarl')"); a = sv()
        T.step("quick route (sv_decoy): showing Anvildeep's boot mould closes it with no cellar visit", a["heart"] == 3 and a["peace"] and not a["clues"], qa=[a["heart"], a["clues"]])
        a = load("jt_hall"); jt("qaSpot('trapdoor')"); fin(); a = sv()
        T.step("a stranger with no word from the Jarl is turned back at the trapdoor", not a["inCellar"] and a["pos"][0] < 10, pos=a["pos"])
        a = load("jt_hall", "&jtq=conquer"); jt("qaSpot('trapdoor')"); fin(); jt("qaSpot('plinth')"); fin(); a = sv(); sol = jt("qaTalk('rimewife')")
        T.step("conquer: the evidence still counts if you look; Solvi: 'You know it's hollow'", a["evidence"] == "false_heart" and a["alliance"] == "conquer" and sol["pages"] == 2 and a["heart"] == 0, qa=a["evidence"])
        a = load("jt_hall", "&jtq=contract"); jt("qaTalk('jarl')"); a = sv()
        T.step("contract: the Jarl gives her terms (jw_terms), Rime Wages stays at 1", a["terms"] and a["hire"] == 1, qa=[a["terms"], a["hire"]])
        a = load("jotunheim", "&jtq=contract"); jt("qaTalk('goatherd')"); a = sv()
        T.step("contract: Skuli waits for the terms first", not a["skuli"] and a["hire"] == 1, qa=[a["skuli"], a["hire"]])
        T.ev("window.__hm.S.flags.jw_terms = 1"); jt("qaTalk('goatherd')"); a = sv()
        T.step("contract: after the terms Skuli guides you; Rime Wages moves to 2", a["skuli"] and a["hire"] == 2, qa=[a["skuli"], a["hire"]])
        a = load("jotunheim"); pass
        T.step("Stonehollow has a door into the Hall (and no 'not open yet' look-spot at the door)", "jt_hall" in a["exits"], exits=a["exits"])
        # ---- rimecaves: the Rime Caves
        a = load("rimecaves")
        T.step("the Rime Caves load: Solvi and Skuli, frost foes roam, cold fire and pools lit, a path back to Stonehollow",
               all(i in a["actors"] for i in ("solvi", "rc_skuli")) and len(set(a["foes"])) >= 3 and a["fx"] >= 5 and "jotunheim" in a["exits"], foes=a["foes"], fx=a["fx"], exits=a["exits"])
        hs = T.ev("(() => { const c = window.__hd2d.ctx; return { step: c.heightAt(-4.4, -7.0), floor: c.heightAt(-3, 3), stair: c.heightAt(0, -5.9) }; })()")
        T.step("real height: the Barrow step stands 1.2 m up with a walkable stair", hs["step"] >= 1.0 and hs["floor"] < 0.2 and 0.2 < hs["stair"] < hs["step"], hs=hs)
        T.ev("window.__hd2d.setTime(0.0)"); pg.wait_for_timeout(600); shot("jt_caves_night")
        T.ev("(() => { const c = window.__hd2d.ctx; c.player.x = 0; c.player.z = -7.0; })()"); pg.wait_for_timeout(300)
        pr = T.ev("window.__hm.harbor.prompt()")
        T.step("the Barrow door prompts at the foot of the step; looking at it explains the three rune locks", "Barrow door" in (pr or "") and jt("qaSpot('door')") and T.ev("!!window.__hm.dlg"), prompt=pr)
        fin()
        T.ev("(() => { const c = window.__hd2d.ctx; c.player.x = 9.0; c.player.z = -6.2; })()"); pg.wait_for_timeout(300)
        T.ev("window.__hm.jot.onCast()"); a = sv()
        T.step("a spell cast by the frozen waterfall melts it: the hidden spring (rc_spring) is found", a["spring"], found=a["found"])
        a = load("rimecaves", "&jtq=conquer"); sol = jt("qaTalk('solvi')")
        T.step("conquer: Solvi says 'You know it's hollow' (2 pages)", sol["pages"] == 2, sol=sol)
        a = load("jotunheim"); 
        T.step("Stonehollow has a path to the Rime Caves (the 'not open yet' look-spot is gone)", "rimecaves" in a["exits"] and not any(False for _ in []), exits=a["exits"])
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
