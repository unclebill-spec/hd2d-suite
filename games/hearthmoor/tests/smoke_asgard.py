"""[ASGARD] Asgard realm smoke (realm-asgard branch): Goldspire (asgard, gs_hall, gs_temple) and the Gilded Reliquary (reliquary G1-G5, reliquary2 G6-G9).

    python3 games/hearthmoor/tests/smoke_asgard.py [--out games/hearthmoor/shots/asgard_smoke] [--only load]

Runs standalone (its own server + headless Chromium; HD2D_USER_DATA_DIR = Bill's dedicated profile, under the browser lock), and smoke.py calls steps() in its own browser context
after the main run. Boots ?qa (fresh state, no saving) with &combat. Waits are T.until / T.frames (no fixed sleeps).
Covers: the shared-table registrations; the five area specs (a 1 m+ ledge with a stair each); each area loads with its exits; the Named Ally at Bifrost (witnesses, the naming, the gate
sentinel, the portal); the Lord-Warden's choice (free / Jotunheim-locked + contract / 4-ally cap / conquer) and the soft Vanaheim cost (+20 % prices, the withheld letter, the gift);
the Rune Trial (?trial=auto, flawless = Valkyr); the Dimmed Dawn clues (free reads); Sigrun's Wings; the temple door modes; G5 and G7 puzzles; both bosses' phases in their rooms
(Sentinel Prime 5x, 3 roles; Aurelion 7x, red P3, wraith copies, lamp drink + relight, the befriend rest and the statue in the Thunder Hall).
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
AREAS5 = ["asgard", "gs_hall", "gs_temple", "reliquary", "reliquary2"]
QUESTS = ["as_gate", "as_trial", "as_temple", "as_sigrun", "as_take", "as_hire", "reliquary", "as_hammer", "as_horse", "thundermoot"]
EXITS = {"asgard": {"gs_hall", "gs_temple", "bifrost"}, "gs_hall": {"asgard"}, "gs_temple": {"asgard"}, "reliquary": {"gs_temple", "reliquary2"}, "reliquary2": {"reliquary"}}


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
    until = T.until

    def sv():
        return T.ev("window.__hm.asg.qa()")

    def load(area, extra="", spawn="start"):
        pg.goto(url + f"&qa&combat&area={area}&spawn={spawn}{extra}", timeout=150000)
        T.wait(f"window.__hm && window.__hm.area === '{area}' && window.__hd2d && window.__hd2d.ready && !window.__hm.busy", 150)
        T.idle(); frames(10)
        return sv()

    FIN = "(() => { const G = window.__hm; if (G.dlg && G.dlg.then) { const t = G.dlg.then; G.dropDialogue(); t(G); } else G.dropDialogue && G.dropDialogue(); })()"

    def fin():
        T.ev(FIN); frames(2)

    def asg(js):
        return T.ev("window.__hm.asg." + js)

    def S(js):
        return T.ev("(() => { const S = window.__hm.S; " + js + " })()")

    def merit(k="embassy"):
        return T.ev(f"(window.__hm.factions.qa().merit.{k}) || 0")

    def reset_state():
        S("S.flags = { ...(S.flags || {}), alliance: {}, rivals: {}, realm_mood: {}, companions: {}, as_contract: 0, sw_terms: 0, sw_orla: 0, mp_cleared: 0 }; S.evidence = {}; for (const k of " + json.dumps(QUESTS) + ") S.quests[k] = 0; S.hero = 'wildcaller'; return 1;")

    def clear_foes():
        T.ev("(() => { const C = window.__hm.combat, c = window.__hd2d.ctx; for (const e of C.enemies) { try { c.removeNpc(e.a); } catch (x) {} } C.enemies = []; })()")

    try:
        # ---- the five areas load, with their exits; no JS errors
        for ar in AREAS5:
            a = load(ar, "&asq=named")
            ex = set(a["exits"]) | set(a["portals"])
            T.step(f"{ar} loads (Asgard module attached) with its exits {sorted(EXITS[ar])}", a["area"] == ar and EXITS[ar] <= ex, exits=sorted(ex), actors=a["actors"][:12])
            rep.setdefault("shots", {})[f"area_{ar}"] = T.shot(f"area_{ar}")
        T.step("no JS errors loading the five Asgard areas", not errors, errs=errors[-4:])
        if only == "load":
            return
        # ---- pictures: the Reliquary room by room (G1-G9)
        for ar, rooms in (("reliquary", ("g1", "g2", "g3", "g4", "g5")), ("reliquary2", ("g6", "g7", "g8", "g9"))):
            for g in rooms:
                load(ar, "&asq=done&g7safe", spawn=g)
                rep["shots"][f"room_{g}"] = T.shot(f"room_{g}")
        # ---- file level: each spec has a 1 m+ ledge with a stair and three grades
        spec_ok = True
        for ar in AREAS5:
            d = json.loads((GAME / "areas" / "src" / f"{ar}.json").read_text())
            hmax = max(t["h"] for t in d["terraces"] if "wall" not in t["name"])
            spec_ok &= hmax >= 1.0 and len(d.get("stairs", [])) >= 1 and d["game"]["id"] == ar and len(d["grades"]) == 3
        T.step("the five area specs each have a 1 m+ ledge with a stair and day / dusk / night grades", spec_ok)
        # ---- the shared tables
        d = asg("qaDefs()")
        B = d["bosses"]
        T.step("registrations: 10 quests, MERIT (3.12), 11 foes, 2 rare bases, thunderstorm + the weather hook, Sigrun's COMP + kit, Nessa's stall, 12 items, 11 talks, the waystone",
               d["quests"] == 10 and d["merit"]["reliquary"] == 120 and d["merit"]["as_gate"] == 60 and len(d["foes"]) == 11 and len(d["bases"]) == 2 and d["wx"] and d["hook"] and d["comp"] == "Sigrun Stormwing" and d["kit"] and d["shop"] and d["items"] == 12 and d["talk"] == 11 and d["ways"], d=d)
        T.step("bosses: the Sentinel Prime is a 5x framed golem (lightning, 60 / 25 %); Aurelion 7x framed gilded plate (light, 60 / 25 %)",
               B["sentinelprime"]["scale"] == 5 and B["sentinelprime"]["framed"] and B["sentinelprime"]["golem"] and not B["sentinelprime"]["plate"] and B["sentinelprime"]["phases"] == [0.6, 0.25]
               and B["aurelion"]["scale"] == 7 and B["aurelion"]["framed"] and B["aurelion"]["plate"] and B["aurelion"]["phases"] == [0.6, 0.25], B=B)
        # ---- Bifrost: The Named Ally
        load("bifrost")
        reset_state(); S("S.ranks = { ...(S.ranks || {}), embassy: 3 }; S.met = { ...(S.met || {}), envoy_jt: 1, envoy_mp: 1 }; return 1;")
        frames(2)
        r = asg("qaTalk('envoy_as')")
        T.step("Bifrost: Ingrith offers The Named Ally at Embassy rank 3", sv()["quests"]["as_gate"] == 1, r=r)
        asg("qaSpot('ag_witness')"); fin(); asg("qaSpot('ag_witness')"); fin()
        T.check("two envoys witness (ag_w1, ag_w2)", "!!(window.__hm.S.flags.ag_w1 && window.__hm.S.flags.ag_w2)")
        asg("qaSpot('ag_name')"); fin()
        T.wait("window.__hm && window.__hm.area === 'asgard' && window.__hd2d.ready && !window.__hm.busy", 150); T.idle(); frames(6)
        ok = until("window.__hm.asg.cb.ag_sentinel !== undefined", 60)
        T.step("the naming cracks the arch: Goldspire loads and the storm sentinel steps out", ok and sv()["flags"]["as_crack"], f=sv()["flags"])
        asg("qaKill('ag_sentinel')"); frames(2); clear_foes()
        asg("qaTalk('envoy_as')"); frames(2)
        q = sv()["quests"]
        T.step("the sentinel down -> stage 2; Ingrith's turn-in opens the gate (as_gate 3, as_gate_open)", q["as_gate"] == 3 and sv()["flags"]["as_gate_open"], q=q)
        a = load("bifrost")
        T.step("Bifrost: the gold arch is a portal to Asgard now (sealed list without it, return spawn from_asgard)", "asgard" in a["gate"]["portals"] and "asgard" not in a["gate"]["sealed"] and "from_asgard" in a["gate"]["spawns"], g=a["gate"])
        # ---- the Lord-Warden's choice + the soft Vanaheim cost
        load("gs_hall", "&asq=named")
        reset_state(); S("S.flags.as_gate_open = 1; S.quests.as_gate = 3; return 1;")
        r = asg("qaTalk('lordwarden')")
        T.step("the Lord-Warden's choice (free): help / Midgard's, nothing locked", r["choice"] and len(r["choice"]) == 2 and not r["locked"], r=r)
        asg("qaPick('To help. Let me find out who did this.')")
        a = sv()
        T.step("befriend: alliance set, Jotunheim locked, Vanaheim's mood down, the Rune Trial opens", a["alliance"] == "befriend" and a["rivals"].get("jotunheim") == "locked" and a["moods"].get("vanaheim") == -1 and a["quests"]["as_trial"] == 1 and a["vanaCold"], a=a)
        T.ev("window.__hm.area = 'vanaheim'")
        mul = asg("qaPrice('none')")
        S("S.quests.alf_gate = 3; S.flags.alliance.vanaheim = 'befriend'; S.flags.moss_letter = 0; return 1;")
        line = asg("qaLine('warden')")
        T.ev("window.__hm.area = 'gs_hall'")
        T.step("soft cost: Vanaheim prices x1.2 and the Elder withholds the apology letter", abs(mul - 1.2) < 1e-6 and "wait" in line, mul=mul, line=line)
        S("S.inv.mead_cake = 1; return 1;")
        r = asg("qaTalk('warden')")
        T.step("a Goldspire gift warms Vanaheim again (mood back to 0)", not sv()["vanaCold"], m=sv()["moods"])
        reset_state(); S("S.flags.rivals = { asgard: 'locked' }; return 1;")
        r = asg("qaTalk('lordwarden')")
        T.step("Jotunheim's friend: the help option is greyed with the locked label and the Guild contract shows", r["locked"] == ["(Locked. You stand with Jotunheim.)"] and "(Locked path) The Guild sent me with an offer." in r["choice"], r=r)
        asg("qaPick('(Locked path) The Guild sent me with an offer.')")
        T.step("the contract: Storm Wages 1, as_contract", sv()["quests"]["as_hire"] == 1 and sv()["flags"]["as_contract"])
        reset_state(); S("S.flags.alliance = { a: 'befriend', b: 'befriend', c: 'befriend', d: 'befriend' }; return 1;")
        r = asg("qaTalk('lordwarden')")
        T.step("the 4-ally cap greys the help option", r["locked"] == ["(Four realms already stand with you.)"], r=r)
        reset_state(); asg("qaTalk('lordwarden')"); asg("qaPick(\"Midgard's. Hand over the Reliquary Key.\")")
        a = sv()
        T.step("conquer: alliance conquer, Jotunheim's mood up, the Thunder Toll opens, no Vanaheim cost", a["alliance"] == "conquer" and a["moods"].get("jotunheim") == 1 and a["quests"]["as_take"] == 1 and not a["vanaCold"], a=a)
        # ---- the Rune Trial (auto)
        a = load("gs_hall", "&asq=trial&trial=auto", spawn="forge")
        asg("qaSpot('rt_shield')"); frames(2)
        ok = until("window.__hm.asg.trial === null && (window.__hm.S.flags.rt_runes || 0) >= 5", 120)
        T.step("the Rune Trial (?trial=auto) strikes 5 runes in their windows", ok, f=T.ev("window.__hm.S.flags.rt_runes"))
        asg("qaTalk('runemaster')"); asg("qaTalk('lordwarden')")
        q = sv()["quests"]
        T.step("Alrik's verdict -> 2; the Lord-Warden -> 3 and the Dimmed Dawn opens", q["as_trial"] == 3 and q["as_temple"] == 1 and sv()["flags"]["as_trusted"], q=q)
        # ---- the Dimmed Dawn (clues)
        load("gs_temple", "&asq=temple", spawn="altar")
        S("S.flags.mp_cleared = 1; S.hero = 'runeguard'; return 1;")
        c = asg("qaClues()")
        T.step("quick route: the brand is free after the mirror sigil, the scrape free for a Rune-reader, one clue must still be read", c["n"] == 2 and not c["done"], c=c)
        asg("qaSpot('dt_lamp')"); fin()
        T.step("reading the flame completes the clues (stage 2)", sv()["quests"]["as_temple"] == 2, c=asg("qaClues()"))
        asg("qaTalk('lordwarden')")
        a = sv()
        T.step("the Lord-Warden closes the Dimmed Dawn: as_cleared, as_peace, S.evidence.asgard, the Reliquary opens", a["quests"]["as_temple"] == 3 and a["flags"]["as_cleared"] and a["flags"]["as_peace"] and T.ev("window.__hm.S.evidence.asgard") == "dimmed_dawn" and a["quests"]["reliquary"] >= 1, a=a["quests"])
        # ---- Sigrun's Wings
        load("asgard", "&asq=sigrun", spawn="pillars")
        asg("qaSpot('sw_feather')"); fin(); asg("qaSpot('sw_raven')"); fin()
        for i in range(3):
            asg(f"qaSpot('sw_pillar{i}')"); fin()
        T.step("Sigrun's Wings: the feather, the raven, the pillars -> stage 2", sv()["quests"]["as_sigrun"] == 2, q=sv()["quests"])
        load("gs_temple", "&asq=sigrun", spawn="door")
        S("S.quests.as_sigrun = 2; return 1;")
        asg("qaSpot('rq_door')"); fin()
        T.step("at the Reliquary door Sigrun joins (stage 3, companions.sigrun)", sv()["quests"]["as_sigrun"] == 3 and "sigrun" in sv()["companions"], c=sv()["companions"])
        asg("qaSpot('rq_door')"); fin()
        T.wait("window.__hm && window.__hm.area === 'reliquary' && window.__hd2d.ready && !window.__hm.busy", 150); T.idle(); frames(4)
        T.check("befriend: the Lord-Warden's word opens the door into the Reliquary", "window.__hm.area === 'reliquary'")
        # ---- the Storm Sentinel Prime (G4)
        load("reliquary", "&asq=reliquary", spawn="g4")
        frames(6); ok = asg("qaBossState()")["which"] == "sentinelprime" or asg("qaBoss('sentinelprime', null)"); frames(4)
        st = asg("qaBossState()")
        T.step("Sentinel Prime: spawns in G4, framed 5x, phase 1, its own sheet role", ok and st["which"] == "sentinelprime" and st["framed"] and st["scale"] == 5 and st["role"] == "sentinelprime", st=st)
        frames(80); T.shot("boss_sentinel_p1")
        asg("qaHp('sentinelprime', 0.5)"); st = asg("qaTick(0.1, 3)"); frames(4)
        T.step("Sentinel P2 (60 %): the core opens and two storm sentinels step out; role sentinel_p2", st["p2"] and st["phase"] == 2 and "sp_s0" in st["ids"] and st["role"] == "sentinel_p2", st=st)
        T.shot("boss_sentinel_p2")
        asg("qaHp('sentinelprime', 0.2)"); st = asg("qaTick(0.1, 30)"); frames(4)
        T.step("Sentinel P3 (25 %): overload, checker tile strikes pending; role sentinel_p3", st["p3"] and st["phase"] == 3 and st["pend"] >= 1 and st["role"] == "sentinel_p3", st=st)
        T.shot("boss_sentinel_p3")
        asg("qaKill('sentinelprime')"); frames(2); clear_foes()
        T.step("its fall: gr_sentinel, storm-glass sg_2 and a storm core", sv()["flags"]["gr_sentinel"] and T.ev("!!window.__hm.S.found.sg_2 && (window.__hm.S.inv.storm_core || 0) >= 1"))
        # ---- G5 (after Severin)
        asg("qaBoss('severin', null)"); frames(2); asg("qaKill('severin')"); frames(2); clear_foes()
        g = asg("qaG5()")
        T.step("G5: Severin's fall wakes the 4-tile chapel pattern", "order" in g and len(g["order"]) == 4, g=g)
        wrong = (set(range(9)) - {g["order"][0]}).pop()
        asg(f"qaG5Step({wrong})"); g2 = asg("qaG5()")
        for k in g["order"]:
            asg(f"qaG5Step({k})")
        T.step("G5: a wrong tile resets; the right order opens the door (gr_g5)", g2["i"] == 0 and sv()["flags"]["gr_g5"], g=asg("qaG5()"))
        # ---- G7 (the Rune Bridge) + G9 Aurelion
        load("reliquary2", "&asq=reliquary", spawn="g7")
        g = asg("qaG7()"); g1 = asg("qaG7Beat(1)")
        T.step("G7: the lit rune set alternates on the beat", "beat" in g and g1["set"] != g["set"], g=g, g1=g1)
        S("window.__hd2d.ctx.player.z = -19.6; return 1;"); asg("qaG7Beat(1)")
        T.check("G7: past the far end the bridge is done (gr_g7)", "!!window.__hm.S.flags.gr_g7")
        a = load("reliquary2", "&asq=reliquary", spawn="g9")
        frames(6); ok = asg("qaBossState()")["which"] == "aurelion" or asg("qaBoss('aurelion', null)"); frames(4)
        st = asg("qaBossState()")
        T.step("Aurelion: spawns in G9, framed 7x, gilded plate, phase 1, 4 lit lamps", ok and st["which"] == "aurelion" and st["framed"] and st["scale"] == 7 and st["role"] == "aurelion" and st["dark"] == [0, 0, 0, 0], st=st)
        frames(80); T.shot("boss_aurelion_p1")
        asg("qaHp('aurelion', 0.5)"); st = asg("qaTick(0.1, 3)"); frames(4)
        T.step("Aurelion P2 (60 %): two light-wraith copies (the real one keeps a shadow)", st["p2"] and st["phase"] == 2 and st["copies"] == 2, st=st)
        T.shot("boss_aurelion_p2")
        asg("qaHp('aurelion', 0.2)"); st = asg("qaTick(0.1, 3)"); frames(4)
        T.step("Aurelion P3 (25 %): red (aurelion_p3), drinking the Dawn-Flame", st["p3"] and st["role"] == "aurelion_p3" and st["drinking"] > 0, st=st)
        T.shot("boss_aurelion_p3")
        T.ev("window.__hm.asg.boss.dark[0] = 1"); asg("qaSpot('g9_lamp0')"); st = asg("qaBossState()")
        T.step("relighting a lamp interrupts the drink", st["drinking"] == 0 and st["dark"][0] == 0, st=st)
        T.ev("(() => { const e = window.__hm.asg.boss; window.__hm.combat.damageEnemy(e, 1e6, { x: e.a.x, z: e.a.z }, 0); })()"); frames(4)
        f = sv()["flags"]
        T.step("befriend: at 0 HP Aurelion yields into his rest (gr_boss, aurelion_rest, not slain)", f["gr_boss"] and f["aurelion_rest"] and not f["aurelion_slain"], f=f)
        fin(); clear_foes()
        asg("qaSpot('g9_flame')"); fin()
        T.step("the true Dawn-Flame is lifted (gr_flame, reliquary 2)", sv()["flags"]["gr_flame"] and sv()["quests"]["reliquary"] == 2)
        load("gs_temple", "&asq=reliquary", spawn="altar")
        S("Object.assign(S.flags, { gr_flame: 1, gr_boss: 1, aurelion_rest: 1 }); S.quests.reliquary = 2; S.inv.dawn_flame = 1; return 1;")
        asg("qaTalk('priestess')"); frames(2)
        f = sv()["flags"]
        T.check("the flame comes home (flame_home, as_resolved, reliquary 3)", "(() => { const f = window.__hm.S.flags; return !!(f.flame_home && f.as_resolved) && window.__hm.S.quests.reliquary === 3; })()", f=f)
        a = load("gs_hall", "&asq=done", spawn="seat")
        T.check("Aurelion's statue stands in the Thunder Hall (aurelion_rest role)", "!!window.__hd2d.ctx.actors.list.find((a) => a.id === 'aurelion' && a.role === 'aurelion_rest')", actors=a["actors"])
        T.shot("gs_hall_statue")
        T.step("no JS errors in the Asgard run", not [e for e in errors if "asgard" in e.lower() or "PAGEERROR" in e], errs=errors[-4:])
    except Exception:
        try:
            rep.setdefault("shots", {})["as_fail"] = T.shot("as_fail")
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
    ap.add_argument("--out", default=str(GAME / "shots" / "asgard_smoke"))
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
    (out / "smoke_asgard.json").write_text(json.dumps(rep, indent=1))
    log(f"smoke_asgard: {'PASS' if rep['pass'] else 'FAIL'} {sum(s['pass'] for s in T.steps)}/{len(T.steps)} steps in {rep['seconds']} s")
    sys.exit(0 if rep["pass"] else 1)


if __name__ == "__main__":
    main()
