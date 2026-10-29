"""[VANAHEIM] Vanaheim realm smoke (realm-vanaheim branch): Mossbrook Springs (vanaheim), the Rotwood Hollow (rotwood), the Verdant Heart (verdant).

    python3 games/hearthmoor/tests/smoke_vanaheim.py [--out games/hearthmoor/shots/vanaheim_smoke] [--only load]

Runs standalone like smoke_asgard (its own server + headless Chromium; HD2D_USER_DATA_DIR under the browser lock). Boots ?qa (fresh state) with &combat.
Tests existing behaviour only: the three areas load with their exits; nothing stuck at spawn (a short walk moves the player); no two floor props stacked
in a spec; the dungeons' 1 m+ ledge + stair; Burrowmoss's befriend / conquer choice; The Violet Spring; the Blight Regent's phases + spike;
the Thornmother; Hjortur (trial / corrupted); the Asgard-driven soft Vanaheim cost (+20 % prices, the withheld letter, the gift).
"""
import argparse
import functools
import json
import math
import os
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
ARGS = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"]
AREAS3 = ["vanaheim", "rotwood", "verdant"]
SPAWN = {"vanaheim": "start", "rotwood": "from_mossbrook", "verdant": "from_rotwood"}
EXITS = {"vanaheim": {"rift"}, "rotwood": {"vanaheim"}, "verdant": {"rotwood"}}   # fresh state: the root-cave (vanaheim -> rotwood) and the sapling stair (rotwood -> verdant) open with the quests
WALL_Z = -4.0   # props at z <= -4 hang on the back wall / ceiling lip (vines, shelves on vh_ceiling_lip): wall dressing, not floor props


def floor_overlaps(d):
    p = [x for x in d.get("props", []) if x["pos"][1] > WALL_Z]
    return [(x["piece"], y["piece"], x["pos"]) for i, x in enumerate(p) for y in p[i + 1:] if math.dist(x["pos"][:2], y["pos"][:2]) < 0.35]


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

    def load(area, spawn=None):
        pg.goto(url + f"&qa&combat&area={area}&spawn={spawn or SPAWN[area]}", timeout=150000)
        T.wait(f"window.__hm && window.__hm.area === '{area}' && window.__hd2d && window.__hd2d.ready && !window.__hm.busy", 150)
        T.idle(); frames(10)

    def jarea(a, spawn="start"):
        T.ev(f"window.__hm.loadArea('{a}', '{spawn}')"); T.wait(f"window.__hm.area === '{a}' && window.__hm.ctx && !window.__hm.busy", 120); T.idle(); frames(4)

    def tp(x, z):
        T.ev(f"(() => {{ const p = window.__hm.ctx.player; p.x = {x}; p.z = {z}; }})()"); frames(3)

    def S(js):
        return T.ev("(() => { const S = window.__hm.S; S.flags = S.flags || {}; " + js + " })()")

    try:
        # ---- the three areas load with their exits, and the player isn't stuck at spawn
        for ar in AREAS3:
            load(ar)
            ex = set(T.ev("(window.__hm.ctx.scene.game.exits || []).map((e) => e.to).concat((window.__hm.ctx.scene.game.portals || []).map((p) => p.to))"))
            p0 = T.pos()
            moved = 0.0
            for dx, dz in ((2.0, 0), (-2.0, 0), (0, 1.5), (0, -1.5)):
                T.walk(p0[0] + dx, p0[1] + dz, 20); p1 = T.pos(); moved = max(moved, math.dist(p0, p1))
                if moved > 1.0:
                    break
            T.step(f"{ar} loads with its exits {sorted(EXITS[ar])}; not stuck at spawn (walked {moved:.1f} m)", EXITS[ar] <= ex and moved > 1.0, exits=sorted(ex), moved=moved)
            rep.setdefault("shots", {})[f"area_{ar}"] = T.shot(f"area_{ar}")
        T.step("no JS errors loading the three Vanaheim areas", not errors, errs=errors[-4:])
        if only == "load":
            return
        # ---- file level: no stacked floor props; the dungeons' ledge + stair; three grades
        ov, spec, gaps = {}, True, {}
        for ar in AREAS3:
            d = json.loads((GAME / "areas" / "src" / f"{ar}.json").read_text())
            o = floor_overlaps(d)
            if o:
                ov[ar] = o
            hmax = max(t["h"] for t in d["terraces"] if "wall" not in t["name"])
            stair = len(d.get("stairs", [])) >= 1
            if not stair:
                gaps[ar] = f"terrace {hmax} m, no stair"
            spec &= hmax >= 1.0 and stair and len(d["grades"]) == 3
        rep["gaps"] = gaps
        T.step("no two floor props stacked (centres within 0.35 m) in the three specs", not ov, overlaps=ov)
        T.step("specs: every area (the Mossbrook hub included) has a 1 m+ ledge with a stair and three grades", spec, gaps=gaps)
        # ---- the Mossbrook hub stair is walkable up to the 2.4 m back terrace
        load("vanaheim")
        hs = json.loads((GAME / "areas" / "src" / "vanaheim.json").read_text())["stairs"][0]
        tp(hs["x"], hs["z_top"] + 5.6); T.walk(hs["x"], hs["z_top"] - 1.2, 30); frames(4)
        top = T.ev("(() => { const p = window.__hm.ctx.player; return { x: p.x, y: p.y, z: p.z }; })()")
        rep["shots"]["hub_stair_top"] = T.shot("hub_stair_top")
        T.step("Mossbrook: walking up the hub stair reaches the 2.4 m back terrace", top["y"] >= 2.3 and top["z"] < hs["z_top"], top=top, stair=hs)
        # ---- Burrowmoss's choice (fresh state)
        load("vanaheim")
        S("S.flags.alliance = {}; return 1;")
        T.talk("warden", keep_open=True); ch = T.to_choice()
        rep["shots"]["alliance_choice"] = T.shot("alliance_choice")
        pg.keyboard.press("1"); T.until("!window.__hm.dlg || !window.__hm.dlg.picking", 5); T.read_all()
        T.step("Burrowmoss asks befriend / conquer / not now; key 1 befriends", bool(ch) and len(ch["options"]) == 3 and T.ev("window.__hm.S.flags.alliance.vanaheim") == "befriend", choice=ch)
        load("vanaheim")
        S("S.flags.alliance = {}; return 1;")
        T.talk("warden", keep_open=True); T.to_choice()
        pg.keyboard.press("2"); T.until("!window.__hm.dlg || !window.__hm.dlg.picking", 5); T.read_all()
        T.step("key 2 conquers (alliance.vanaheim = conquer; the factions realm is 'gate' in Vanaheim)", T.ev("window.__hm.S.flags.alliance.vanaheim") == "conquer" and T.ev("window.__hm.factions.realm()") == "gate")
        # ---- The Violet Spring (befriend)
        load("vanaheim")
        S("S.flags.alliance = { vanaheim: 'befriend' }; return 1;")
        T.talk("warden"); q1 = T.ev("window.__hm.S.quests.vh_spring")
        S("S.found.brazier_vh_w = 1; S.found.brazier_vh_spring = 1; return 1;")
        for x, z in [(-5.6, -5.0), (9.6, 4.0), (-7.0, 6.0)]:
            tp(x, z); T.ev("window.__hm.verdant.interact()")
        caps = T.ev("window.__hm.S.inv.redcap || 0")
        tp(4.6, -5.0); T.ev("window.__hm.verdant.interact()"); frames(2)
        sp = T.ev("({ q: window.__hm.S.quests.vh_spring, f: window.__hm.S.flags.vanaheim_spring })")
        rep["shots"]["spring_cleansed"] = T.shot("spring_cleansed")
        T.talk("warden")
        after = T.ev("({ q: window.__hm.S.quests.vh_spring, rw: window.__hm.S.quests.rotwood })")
        jarea("vanaheim"); after["cave"] = T.ev("!!(window.__hm.ctx.scene.game.exits || []).find((e) => e.to === 'rotwood')")
        T.step("The Violet Spring: offered, 3 red caps, the spring cleansed, Burrowmoss's word completes it and starts the Rotwood Hollow and opens the root-cave",
               q1 == 1 and caps == 3 and sp["q"] == 2 and sp["f"] == "cleansed" and after["q"] == 3 and after["rw"] == 1 and after["cave"], q1=q1, caps=caps, spring=sp, after=after)
        # ---- the Blight Regent
        jarea("rotwood", "from_mossbrook")
        T.ev("window.__hm.peace = true")
        light = "(id) => { const G = window.__hm, b = G.hollows.braziers.find((q) => q.id === id); G.hollows.spellAt(b.pos[0], b.pos[1]); return !!G.S.found[id]; }"
        door = T.ev("window.__hm.ctx.scene.game.rootdoor")
        lit = []
        for bid in door["order"]:
            lit.append(T.ev(f"({light})('{bid}')")); frames(3)
        gal = T.ev(f"({light})(window.__hm.ctx.scene.game.thorns.brazier)"); frames(3)
        T.step("the root door opens from its braziers cast-lit in the pulse order (rw_lock), the gallery brazier burns the thorns", all(lit) and gal and T.ev("!!window.__hm.S.flags.rw_lock"), lit=lit, gal=gal)
        bw = T.ev("window.__hm.ctx.scene.game.bower")
        tp(bw["pos"][0] - 1.0, 2.0); frames(4)
        st1 = T.ev("window.__hm.verdant.state()")
        frames(60); rep["shots"]["boss_regent_p1"] = T.shot("boss_regent_p1")
        T.ev("(() => { const G = window.__hm, e = G.verdant.boss; G.combat.damageEnemy(e, e.D.hp * 0.45, null, 0); })()"); frames(3)
        st2 = T.ev("window.__hm.verdant.state()")
        T.ev("(() => { const G = window.__hm, e = G.verdant.boss; G.combat.damageEnemy(e, e.D.hp * 0.35, null, 0); })()"); frames(4)
        # the frost-iron spike pulses blue every 4 s (game time): strike it inside the window, in the same page task that sees it open
        # (a screenshot between "open" and the hit outlasts the 1.3 s window on a loaded box)
        T.until("(() => { const G = window.__hm, e = G.verdant.boss; if (!e || !e.spikeOpen) return false; const st = G.verdant.state(), h0 = e.hp; G.combat.damageEnemy(e, 10, null, 0); window.__vhHit = { st, hit: h0 - e.hp }; return true; })()", 60)
        hz = T.ev("window.__vhHit || { st: window.__hm.verdant.state(), hit: -1 }")
        rep["shots"]["boss_regent_p3"] = T.shot("boss_regent_p3")
        st3, hit = hz["st"], hz["hit"]
        T.step("the Blight Regent (5.5x): phase 2 < 60 %, phase 3 < 25 %, the blue pulse opens the frost-iron spike (double damage)",
               bool(st1["boss"]) and st1["boss"]["scale"] == 5.5 and st2["boss"]["phase"] == 2 and st3["boss"]["phase"] == 3 and st3["boss"]["spikeOpen"] and hit == 20,
               s1=st1["boss"], s2=st2["boss"], s3=st3["boss"], hit=hit)
        T.ev("window.__hm.combat.damageEnemy(window.__hm.verdant.boss, 99999, null, 0)"); frames(4)
        dn = T.ev("({ boss: window.__hm.S.flags.rw_boss, spike: window.__hm.S.inv.blight_spike || 0, sap: !!(window.__hm.ctx.scene.game.exits || []).find((e) => e.to === 'verdant') })")
        T.step("the Regent falls: rw_boss, the frost-iron spike, the sapling stair to the Verdant Heart", dn["boss"] == 1 and dn["spike"] == 1 and dn["sap"], down=dn)
        # ---- the Thornmother + Hjortur
        S("S.quests.verdant = 1; return 1;")
        jarea("verdant", "from_rotwood")
        vd = T.ev("window.__hm.ctx.scene.game")
        tp(vd["moonwell"]["pos"][0] - 1.0, 2.0); frames(4); th = T.ev("window.__hm.verdant.state().thorn")
        frames(60); rep["shots"]["boss_thornmother"] = T.shot("boss_thornmother")
        T.step("the Thornmother (2.4x) rises at the Moonwell", bool(th) and th["scale"] == 2.4, thorn=th)
        if th:
            T.ev("(() => { const G = window.__hm, e = G.verdant.thorn || (G.combat.enemies.find((x) => x.role === 'thornmother')); if (e) G.combat.damageEnemy(e, 99999, null, 0); })()"); frames(3)
        tp(vd["glade"]["enter_x"] + 1.0, 2.0); frames(4); hj = T.ev("window.__hm.verdant.state().hj")
        frames(60); rep["shots"]["boss_hjortur"] = T.shot("boss_hjortur")
        T.step("Hjortur (6x) holds the guardian trial on the befriend path", bool(hj) and hj["scale"] == 6 and hj["role"] == "hjortur" and hj["trial"], hj=hj)
        T.ev("(() => { const G = window.__hm, e = G.verdant.hj; G.combat.damageEnemy(e, 99999, null, 0); })()"); frames(3)
        vq = T.ev("({ q: window.__hm.S.quests.verdant, tine: window.__hm.S.inv.greenheart_tine || 0 })")
        T.step("befriend: Hjortur yields, the Verdant Heart quest is done, a Greenheart tine", vq["q"] == 3 and vq["tine"] == 1, quest=vq)
        S("S.flags.alliance.vanaheim = 'conquer'; delete S.flags.vh_hjortur; S.quests.verdant = 1; return 1;")
        jarea("verdant", "from_rotwood"); tp(vd["glade"]["enter_x"] + 1.0, 2.0); frames(4); hc = T.ev("window.__hm.verdant.state().hj")
        rep["shots"]["boss_hjortur_corrupted"] = T.shot("boss_hjortur_corrupted")
        T.step("conquer path: the corrupted Hjortur fights for real (no trial)", bool(hc) and hc["role"] == "hjortur_corrupted" and not hc["trial"], hj=hc)
        # ---- the soft Vanaheim cost (Asgard's mood hooks)
        load("vanaheim")
        S("S.flags.alliance = { vanaheim: 'befriend' }; S.flags.realm_mood = { vanaheim: -1 }; S.quests.alf_gate = 3; S.flags.moss_letter = 0; return 1;")
        mul = T.ev("window.__hm.asg.qaPrice('none')"); line = T.ev("window.__hm.asg.qaPages('warden')")
        T.ev("window.__hm.area = 'plaza'"); mul0 = T.ev("window.__hm.asg.qaPrice('none')"); T.ev("window.__hm.area = 'vanaheim'")
        T.step("low Vanaheim mood: prices x1.2 in Vanaheim (not outside), the Elder withholds the apology letter", abs(mul - 1.2) < 1e-6 and abs(mul0 - 1.0) < 1e-6 and "wait" in line, mul=mul, mul0=mul0, line=line[:80])
        S("S.inv.mead_cake = 1; return 1;"); T.ev("window.__hm.asg.qaTalk('warden')")
        T.step("a gift warms Vanaheim again (mood back to 0, prices x1.0)", T.ev("(window.__hm.S.flags.realm_mood || {}).vanaheim") == 0 and abs(T.ev("window.__hm.asg.qaPrice('none')") - 1.0) < 1e-6)
        # ---- [VANAHEIM] Stage B: Mossbrook village + the Thorngarden + Mother Nettlecrown (?vhq= presets)
        for ar, sp_ in (("vh_village", "start"), ("vh_garden", "start")):
            pg.goto(url + f"&qa&combat&vhq=village&area={ar}&spawn={sp_}", timeout=150000)
            T.wait(f"window.__hm && window.__hm.area === '{ar}' && window.__hd2d && window.__hd2d.ready && !window.__hm.busy", 150); T.idle(); frames(10)
            ex = set(T.ev("(window.__hm.ctx.scene.game.exits || []).map((e) => e.to)"))
            T.step(f"{ar} loads with its exits", ex >= ({"vanaheim", "vh_garden"} if ar == "vh_village" else {"vh_village"}), exits=sorted(ex))
            rep.setdefault("shots", {})[f"area_{ar}"] = T.shot(f"area_{ar}")
        jarea("vanaheim", "start")
        T.step("Mossbrook Springs gets the lane to the village (befriended)", "vh_village" in T.ev("(window.__hm.ctx.scene.game.exits || []).map((e) => e.to)"))
        S("S.flags.alliance = { alfheim: 'befriend', svartalfheim: 'befriend', jotunheim: 'befriend', muspelheim: 'befriend' }; return 1;")
        opts = T.ev("window.__hm.vana.qaTalk('warden').options")
        T.step("4-ally cap: the warden offers the Spring Wages contract instead of befriend", bool(opts) and "hire" in opts[0].lower() and len(opts) == 3, opts=opts)
        T.ev("(() => { const S = window.__hm.S; S.quests.vh_tobble = 0; S.flags.companions = {}; })()")
        pg.goto(url + "&qa&combat&vhq=fight&area=vh_garden&spawn=circle", timeout=150000)
        T.wait("window.__hm && window.__hm.area === 'vh_garden' && window.__hd2d && window.__hd2d.ready && !window.__hm.busy", 150); T.idle(); frames(10)
        T.wait("window.__hm.vana.boss && window.__hm.vana.boss.state !== 'dead'", 30)
        b = T.ev("(() => { const v = window.__hm.vana, e = v.boss; return { hp: e.hp, max: e.D.hp, dmg: e.D.dmg, adds: v.adds.length, xp: 0 }; })()")
        frames(20); rep.setdefault("shots", {})["nettle_fight_p1"] = T.shot("nettle_fight_p1")
        T.step("Nettlecrown spawns: 1500 HP, 22 dmg, 2 thorn-nymphs (P1)", b["max"] == 1500 and b["dmg"] == 22 and b["adds"] == 2, **b)
        ph = T.ev("(() => { const v = window.__hm.vana, e = v.boss, C = window.__hm.combat; C.damageEnemy(e, 600, null, 0); const p2 = e.phaseN; C.damageEnemy(e, 400, null, 0); return { p2, p3: e.phaseN, adds: v.adds.length, hp: e.hp }; })()")
        frames(6); rep["shots"]["nettle_fight_p3"] = T.shot("nettle_fight_p3")
        T.step("phases at 65 % and 35 %; 2 more thorn-nymphs in P3", ph["p2"] == 2 and ph["p3"] == 3 and ph["adds"] == 4, **ph)
        y = T.ev("(() => { const v = window.__hm.vana, e = v.boss, C = window.__hm.combat; C.damageEnemy(e, 360, null, 0); const grab = !!e.grabbed; C.damageEnemy(e, 9999, null, 0); return { grab, hp: e.hp, y: !!e.yieldedVh }; })()")
        T.step("heartroot grab at 10 %; she yields at 5 % (75 HP), not killed", y["grab"] and y["y"] and y["hp"] == 75, **y)
        T.wait("window.__hm.dlg && window.__hm.dlg.npc.id === 'nettlecrown'", 20)
        for _ in range(6):
            if T.ev("!!window.__hm.dlgChoice()"):
                break
            pg.keyboard.press("Enter"); frames(8)
        frames(6); rep["shots"]["nettle_spare_choice"] = T.shot("nettle_spare_choice")
        ch = T.ev("window.__hm.dlgChoice()")
        T.step("the spare choice (nettle_end) opens", bool(ch) and len(ch["options"]) == 2, ch=ch)
        r0 = T.ev("window.__hm.factions.rank('embassy')")
        T.ev("window.__hm.choicePick(0)"); frames(4)
        sp = T.ev("(() => { const S = window.__hm.S; return { nettle: S.flags.vh_nettle, circ: S.inv.nettle_circlet, bloom: S.inv.frost_bloom, bag: (S.bag || []).some((x) => x.unique === 'nettle_circlet'), rank: window.__hm.factions.rank('embassy') }; })()")
        T.step("spared: frost bloom + Nettlecrown's Bean-Circlet + Embassy rank up one", sp["nettle"] == "spared" and sp["circ"] == 1 and sp["bloom"] == 1 and sp["bag"] and sp["rank"] == r0 + 1, r0=r0, **sp)
        T.step("no JS errors in Stage B", not [e for e in errors if "PAGEERROR" in e], errs=errors[-4:])
        T.step("no JS errors in the Vanaheim run", not [e for e in errors if "PAGEERROR" in e or "vanaheim" in e.lower() or "verdant" in e.lower()], errs=errors[-4:])
    except Exception:
        try:
            rep.setdefault("shots", {})["vh_fail"] = T.shot("vh_fail")
        except Exception:
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
    ap.add_argument("--out", default=str(GAME / "shots" / "vanaheim_smoke"))
    ap.add_argument("--simscale", type=int, default=4)
    ap.add_argument("--only", default="", help="load = the three area loads only (a quick-load check)")
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
    (out / "smoke_vanaheim.json").write_text(json.dumps(rep, indent=1))
    log(f"smoke_vanaheim: {'PASS' if rep['pass'] else 'FAIL'} {sum(s['pass'] for s in T.steps)}/{len(T.steps)} steps in {rep['seconds']} s")
    sys.exit(0 if rep["pass"] else 1)


if __name__ == "__main__":
    main()
