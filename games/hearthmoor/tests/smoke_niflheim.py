"""[NIFLHEIM] Niflheim realm smoke (realm-niflheim branch), CHUNK 1 = skeleton: what exists before the art pack (READY.txt) and the area builds.

    python3 games/hearthmoor/tests/smoke_niflheim.py [--out games/hearthmoor/shots/niflheim_smoke]

Runs standalone (its own server + headless Chromium; HD2D_USER_DATA_DIR = Bill's dedicated profile, under the browser lock), and smoke.py calls steps() in its own browser context
after the main run, so the main run's save is untouched. Boots ?qa (fresh state, no saving) with &combat&peace. Waits are T.until / T.frames (no fixed sleeps).
Covers (runtime tables, no built Niflheim area needed): the module is live (G.nifl); the shared-table registrations (10 quests, MERIT, foes incl. the three framed bosses and Veyra's 4 phases,
rares, weather kinds, Hrefna's COMP + kit, Tove's stall, items, TALK); Bifrost's ice arch stays sealed while no area is built; the Muspelheim-lock flag (NIFL_MUSP_LOCK) and what it
switches; Gudrun's choice in every variant (free, Muspelheim friend = locked label, Muspelheim conqueror = Lanterns skipped, 4-ally cap, conquer); the Cold Mark rules; the redeemable()
test; the three bosses' phase logic through qaBoss in any area; the realm's merit routing; the weather calendar split. File-level: the three skeleton specs (real height + stair), build.py /
nifl_art.py waiting on READY.txt. When Niflheim areas are built the extra steps (area loads, gate portal, return spawn) run too.
"""
import argparse
import functools
import json
import os
import subprocess
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
READY = Path("/workspace/hearthmoor-staging/art/niflheim/READY.txt")
ARGS = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"]
QUESTS = ['nf_gate', 'nf_lanterns', 'nf_cold', 'nf_hrefna', 'nf_eira', 'nf_take', 'frozenspire', 'nf_staff', 'nf_elk', 'frostvigil']


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
    frames = lambda n=6, timeout=120: T.frames(n, timeout)   # engine-frame waits, never fixed sleeps
    until = T.until   # game-time waits (True / False, never raises)

    def sv():
        return T.ev("window.__hm.nifl.qa()")

    def load(area, extra="", spawn="start"):
        pg.goto(url + f"&qa&combat&area={area}&spawn={spawn}{extra}", timeout=150000)
        T.wait(f"window.__hm && window.__hm.area === '{area}' && window.__hd2d && window.__hd2d.ready && !window.__hm.busy", 150)
        T.idle(); frames(10)
        return sv()

    FIN = "(() => { const G = window.__hm; if (G.dlg && G.dlg.then) { const t = G.dlg.then; G.dropDialogue(); t(G); } else G.dropDialogue && G.dropDialogue(); })()"

    def fin():
        T.ev(FIN); frames(2)

    def nf(js):
        return T.ev("window.__hm.nifl." + js)

    def S(js):
        return T.ev("(() => { const S = window.__hm.S; " + js + " })()")

    def merit(k="embassy"):
        return T.ev(f"(window.__hm.factions.qa().merit.{k}) || 0")

    def reset_state():   # a clean realm state between talk scenarios (same page: no reload)
        S("S.flags = { ...(S.flags || {}), alliance: {}, rivals: {}, realm_mood: {}, veyra_revealed: 1, nf_vigil: 0, rift_breaker: 0 }; S.evidence = {}; for (const k of " + json.dumps(QUESTS) + ") S.quests[k] = 0; S.hero = 'wildcaller'; return 1;")

    try:
        # ---- file-level: the skeleton specs and the installer / build gate wait on READY.txt
        ready = READY.exists()
        spec_ok = True
        for a in ("niflheim", "nf_home", "iceglow"):
            d = json.loads((GAME / "areas" / "src" / f"{a}.json").read_text())
            hmax = max(t["h"] for t in d["terraces"] if "wall" not in t["name"])
            spec_ok &= hmax >= 1.0 and len(d.get("stairs", [])) >= 1 and d["game"]["id"] == a and len(d["grades"]) == 3
        T.step("the three skeleton specs (Mistmere, the Quiet Shore, the Glowpool Caverns) each have a 1.2 m terrace with a stair and day / dusk / night grades", spec_ok)
        r = subprocess.run([sys.executable, "-c", "import build; print(','.join(build.AREAS))"], cwd=GAME, capture_output=True, text=True, timeout=120)
        areas = r.stdout.strip().split(",") if r.returncode == 0 else []
        T.step("build.py joins the Niflheim areas only when READY.txt exists", r.returncode == 0 and (("niflheim" in areas) == ready), ready=ready, n=len(areas), err=r.stderr[-200:])
        r = subprocess.run([sys.executable, str(GAME.parents[1] / "tools" / "hearthmoor" / "nifl_art.py")], capture_output=True, text=True, timeout=300)
        T.step("nifl_art.py waits on READY.txt (does nothing without it)", r.returncode == 0 and (ready or "READY.txt is missing" in r.stdout), out=r.stdout[-200:])
        # ---- the module and its shared-table registrations
        a = load("bifrost")
        d = nf("qaDefs()")
        T.step("the Niflheim module is live (G.nifl) and plans the six areas", a["realm"] == "niflheim" and a["planned"] == ["niflheim", "nf_home", "iceglow", "frozenspire", "frozenspire2", "frozen_rift"], qa=a["planned"])
        T.step("ten quests, the merit keys (story 3.12), eight NPC talk entries, Tove's stall and eleven items are registered",
               d["quests"] == 10 and d["merit"] == {"nf_gate": 60, "rimetoll": 60, "spire_c": 120, "nf_lanterns": 40, "nf_cold": 60, "nf_rival": 20, "nf_hrefna": 80, "nf_eira": 80, "frozenspire": 120, "frostvigil": 40}
               and d["talk"] == 8 and d["shop"] and d["items"] == 11, d=d)
        B = d["bosses"]
        T.step("the Glacier Colossus is a 6x framed golem (no plate), Kael a 5.5x framed plate boss, Veyra a 5x framed plate boss with FOUR phases",
               B["colossus"]["scale"] == 6 and B["colossus"]["framed"] is True and B["colossus"]["golem"] and not B["colossus"]["plate"] and B["colossus"]["phases"] == [0.6, 0.25]
               and B["kael"]["scale"] == 5.5 and B["kael"]["framed"] is True and B["kael"]["plate"] and B["kael"]["phases"] == [0.6, 0.25]
               and B["veyra"]["scale"] == 5 and B["veyra"]["framed"] is True and B["veyra"]["plate"] and len(B["veyra"]["phases"]) == 3 and all(x["boss"] and x["element"] == "ice" for x in B.values()), b=B)
        T.step("the other six foes and both rare bases exist", len(d["foes"]) == 9 and d["bases"] == ["mistalpha", "spiritprime"], foes=d["foes"])
        T.step("Hrefna is a companion (COMP + follower kit), there is no Niflheim pet, and the two weather kinds exist",
               d["comp"] == "Hrefna Frostveil" and d["kit"] and d["wx"]["frost_mist"] and d["wx"]["still_frost"] and not T.ev("window.__hm.S.pets && !!window.__hm.S.pets.niflheim"), d=d)
        T.step("one active companion: swapping to Hrefna after Kindle / Lumi leaves exactly one active",
               T.ev("(() => { const G = window.__hm, f = (G.S.flags = G.S.flags || {}); f.companions = { lumi: 1, hrefna: 1 }; f.companion_active = 'hrefna'; return Object.keys(f.companions).length === 2 && f.companion_active === 'hrefna'; })()"))
        n = {"frost_mist": 0, "still_frost": 0, "clear": 0}; tot = 0
        for day in range(40):
            for blk in range(10):
                k = T.ev(f"window.__hm.weatherAt('niflheim', {day}, {blk / 10 + 0.05})"); n[k] = n.get(k, 0) + 1; tot += 1
        T.step("niflheim's calendar is about 40 % freezing mist, 40 % still frost, 20 % clear glow", abs(n["frost_mist"] / tot - 0.4) < 0.1 and abs(n["still_frost"] / tot - 0.4) < 0.1 and abs(n["clear"] / tot - 0.2) < 0.1, n=n)
        # ---- Bifrost's ice arch (dormant while nothing is built)
        b0 = a["gate"]
        T.step("Bifrost: the Niflheim arch is sealed, no frost spots while nothing is built", "niflheim" in b0["sealed"] and "niflheim" not in b0["portals"] and not b0["open"] and (a["spots"] == 0 or b0["live"]), gate=b0, spots=a["spots"])
        T.step("the sealed arch's look still reads the stock text before 3 realms are resolved", "frozen this gate from the inside" in T.ev("window.__hm.crossing.pages({ arch: 'niflheim', realm: 'Niflheim' }).join(' ')"))
        a1 = load("bifrost", "&nfq=open"); b1 = a1["gate"]
        if b1["live"]:
            T.step("?nfq=open: the arch moves from sealed to portals and the return spawn is added", "niflheim" not in b1["sealed"] and "niflheim" in b1["portals"] and "from_niflheim" in b1["spawns"], gate=b1)
        else:
            T.step("?nfq=open with no area built: the arch stays sealed (dormant) but the return spawn exists", "niflheim" in b1["sealed"] and "niflheim" not in b1["portals"] and "from_niflheim" in b1["spawns"] and b1["open"], gate=b1)
        # ---- the Frost Invitation's counting rules (resolvedCount) and the lock flag
        reset_state()
        S("S.flags.vh_resolved = 'x'; S.flags.alf_resolved = 'befriend'; return 1;"); r2 = sv()["resolved"]
        S("S.flags.sv_resolved = 'x'; return 1;"); r3 = sv()["resolved"]
        T.step("resolvedCount counts the realm resolved flags (2, then 3 = the invitation)", r2 == 2 and r3 == 3, r2=r2, r3=r3)
        T.step("the Muspelheim lock is ONE constant (NIFL_MUSP_LOCK, on by default)", nf("qaDefs()")["lock"] is True)
        # ---- Gudrun's choice
        reset_state()
        t = nf("qaTalk('frostspeaker')")
        T.step("Gudrun's choice for a free player: befriend / conquer, no contract, nothing locked", t["choice"] == ["Stand with Mistmere. Let me bring her home.", "Midgard's. Hand over the Spire Key."] and not t["locked"], t=t)
        nf("qaPick('Stand with Mistmere. Let me bring her home.')"); s1 = sv()
        T.step("befriend: alliance set, Muspelheim is locked as a rival, The Lanterns of Mistmere starts", s1["alliance"] == "befriend" and s1["rivals"].get("muspelheim") == "locked" and s1["quests"]["nf_lanterns"] == 1 and s1["quests"]["nf_cold"] == 0, qa=[s1["alliance"], s1["rivals"], s1["quests"]])
        reset_state(); S("S.flags.realm_mood = { niflheim: 1 }; return 1;")
        line = nf("qaLine('frostspeaker')")
        nf("qaPick('Stand with Mistmere. Let me bring her home.')"); s1 = sv()
        T.step("a Muspelheim conqueror (mood 1) skips the Lanterns (done, favor paid) and starts The Cold Mark, and Gudrun says so",
               s1["quests"]["nf_lanterns"] == 3 and s1["quests"]["nf_cold"] == 1 and s1["flags"]["trusted"] and "broke the fire-throne" in (line or ""), qa=s1["quests"], line=line)
        reset_state(); S("S.flags.rivals = { niflheim: 'locked' }; return 1;")
        t = nf("qaTalk('frostspeaker')")
        T.step("a Muspelheim friend: the befriend option is greyed with the locked label; conquer stays open; there is no contract option", t["choice"] == ["(Locked. You stand with Muspelheim.)", "Midgard's. Hand over the Spire Key."] and t["locked"] == ["(Locked. You stand with Muspelheim.)"], t=t)
        nf("qaPick('(Locked. You stand with Muspelheim.)')"); s1 = sv()
        T.step("picking the greyed option does nothing but talk", s1["alliance"] is None and s1["quests"]["nf_lanterns"] == 0 and s1["quests"]["nf_take"] == 0)
        T.step("Hrefna will not join a Muspelheim friend (her line, no quest offer)", "light yours" in (nf("qaLine('hrefna')") or "") and sv()["quests"]["nf_hrefna"] == 0)
        T.step("redeemable() is false for a Muspelheim friend even with everything else in place",
               S("S.flags.alliance = { niflheim: 'befriend' }; S.flags.nf_vigil = 3; S.evidence = { a: 1, b: 1, c: 1 }; return 1;") is not None and sv()["lockedBy"] and not sv()["redeemable"])
        S("S.flags.rivals = {}; return 1;")
        T.step("redeemable(): befriend + Eira's Lanterns done + 3 evidence + no Breaker detour = true; one missing piece = false",
               sv()["redeemable"] and not (S("S.evidence = { a: 1, b: 1 }; return 1;") is not None and sv()["redeemable"]) and not (S("S.evidence = { a: 1, b: 1, c: 1 }; S.flags.rift_breaker = 1; return 1;") is not None and sv()["redeemable"]))
        reset_state(); S("S.flags.alliance = { vanaheim: 'befriend', alfheim: 'befriend', svartalfheim: 'befriend', jotunheim: 'befriend' }; return 1;")
        t = nf("qaTalk('frostspeaker')")
        T.step("the 4-ally cap greys the befriend option with its own label", t["choice"][0] == "(Four realms already stand with you.)" and t["locked"] == ["(Four realms already stand with you.)"], t=t)
        reset_state()
        nf("qaPick(\"Midgard's. Hand over the Spire Key.\")"); s1 = sv()
        T.step("conquer: alliance conquer, Muspelheim's mood goes up, The Rime Toll starts", s1["alliance"] == "conquer" and s1["moods"].get("muspelheim") == 1 and s1["quests"]["nf_take"] == 1, qa=[s1["alliance"], s1["moods"], s1["quests"]])
        reset_state(); S("S.flags.veyra_revealed = 0; return 1;")
        T.step("before the reveal Gudrun only sends you to the Quiet Shore (no choice)", nf("qaTalk('frostspeaker')")["choice"] is None)
        # ---- the Cold Mark and the turn-ins
        reset_state(); S("S.flags.alliance = { niflheim: 'befriend' }; S.quests.nf_cold = 1; return 1;")
        c0 = nf("qaCold()"); S("S.flags.cm_table = 1; S.flags.cm_lantern = 1; S.hero = 'runeguard'; return 1;"); c1 = nf("qaCold()"); S("S.hero = 'wildcaller'; return 1;"); c2 = nf("qaCold()")
        T.step("the Cold Mark: three clues; a Rune-reader's runes read themselves (free)", c0["n"] == 0 and c1["n"] == 3 and c1["done"] and c2["n"] == 2 and not c2["done"], c0=c0, c1=c1, c2=c2)
        S("S.flags.cm_runes = 1; S.quests.nf_cold = 2; S.flags.realm_mood = { niflheim: 1 }; return 1;")
        m0 = merit(); nf("qaTalk('frostspeaker')"); s1 = sv()
        T.step("the Cold Mark turn-in: quest 3, cleared, +60 Realm Favor and +20 for a Muspelheim conqueror", s1["quests"]["nf_cold"] == 3 and s1["flags"]["cleared"] and merit() - m0 == 80, qa=[s1["quests"], merit() - m0])
        reset_state(); S("S.flags.alliance = { niflheim: 'befriend' }; S.quests.nf_lanterns = 2; return 1;")
        m0 = merit(); nf("qaTalk('frostspeaker')"); s1 = sv()
        T.step("the Lanterns turn-in: quest 3, trusted, +40 Realm Favor, The Cold Mark starts", s1["quests"]["nf_lanterns"] == 3 and s1["flags"]["trusted"] and merit() - m0 == 40 and s1["quests"]["nf_cold"] == 1, qa=[s1["quests"], merit() - m0])
        reset_state(); S("S.flags.alliance = { niflheim: 'befriend' }; S.quests.nf_cold = 3; return 1;")
        nf("qaTalk('hrefna')")
        T.step("Hrefna's Thaw is offered after The Cold Mark (befriend)", sv()["quests"]["nf_hrefna"] == 1)
        reset_state(); S("S.hero = 'cinderknight'; S.flags.alliance = { niflheim: 'befriend' }; S.quests.nf_lanterns = 1; return 1;")
        line = nf("qaLine('hrefna')"); nf("qaTalk('hrefna')")
        T.step("an Ember-born hero needs Hrefna's vouch first (she checks the ember; nl_vouch is set)", "ember-light" in (line or "") and T.ev("window.__hm.S.flags.nl_vouch === 1"), line=line)
        # ---- merit routing
        rr = T.ev("(() => { const G = window.__hm, f = G.S.flags, out = {}; const a0 = G.area; G.area = 'niflheim';"
                  " f.alliance = { niflheim: 'befriend' }; out.bef = G.factions.realm(); f.alliance = { niflheim: 'conquer' }; out.con = G.factions.realm(); G.area = 'plaza'; out.away = G.factions.realm(); G.area = a0; f.alliance = {}; return out; })()")
        T.step("merit routing: befriend pays Realm Favor, conquer pays Rift Marks (gate) inside the realm's areas only", rr == {"bef": "embassy", "con": "gate", "away": "hearth"}, rr=rr)
        # ---- the three bosses' phase logic (spawned in the Bifrost scene: any area with a combat module works; positions are provisional)
        a = load("plaza", "&nfq=revealed")   # the plaza sheet has the stock `wraith` role the QA bosses wear until their own sheets land
        T.ev("window.__hm.nifl.moveTo(0, 6)")
        for which, hp_steps in (("colossus", (0.5, 0.2)), ("kael", (0.5, 0.2))):
            ok = nf(f"qaBoss('{which}', [0, -9])"); frames(4); st = nf("qaBossState()")
            T.step(f"{which}: spawns framed at {B[which]['scale']}x in phase 1", ok and st["which"] == which and st["framed"] and st["scale"] == B[which]["scale"] and st["phase"] in (0, 1), st=st)
            nf(f"qaHp('{which}', {hp_steps[0]})"); st = nf("qaTick(0.1, 3)")
            T.step(f"{which}: phase 2 at 60 % ({'core exposed, two ice golems' if which == 'colossus' else 'three mist bats'})", st["p2"] and st["phase"] == 2 and (("co_g0" in st["ids"] and "co_g1" in st["ids"]) if which == "colossus" else st["bats"] == 3), st=st)
            nf(f"qaHp('{which}', {hp_steps[1]})"); st = nf("qaTick(0.1, 3)")
            T.step(f"{which}: phase 3 at 25 % ({'frost spirits swarm' if which == 'colossus' else 'two Ice Wardens called'})", st["p3"] and st["phase"] == 3 and (("co_s0" in st["ids"]) if which == "colossus" else ("ka_w0" in st["ids"] and "ka_w1" in st["ids"])), st=st)
            nf(f"qaKill('{which}')"); frames(2); fin()
            T.ev("(() => { const C = window.__hm.combat, c = window.__hd2d.ctx; for (const e of C.enemies) c.removeNpc(e.a); C.enemies = []; })()")
        T.step("Kael's fall sets fs_boss and moves The Frozen Spire to stage 2", T.ev("window.__hm.S.flags.fs_boss === 1") and sv()["quests"]["frozenspire"] == 2, q=sv()["quests"])
        ok = nf("qaBoss('veyra', [0, -9])"); frames(4); st = nf("qaBossState()")
        T.step("Veyra: spawns framed at 5x in phase 1 (three mist clones)", ok and st["which"] == "veyra" and st["framed"] and st["scale"] == 5 and st["clones"] == 3, st=st)
        nf("qaHp('veyra', 0.6)"); st = nf("qaTick(0.1, 3)")
        T.step("Veyra P2 (70 %): the four portals freeze", st["phase"] == 2 and st["p2"] and st["portals"] == [1, 1, 1, 1], st=st)
        st = nf("qaThaw(0)")
        T.step("a portal thaws (the thaw rune)", st["portals"] == [0, 1, 1, 1], st=st)
        nf("qaHp('veyra', 0.3)"); st = nf("qaTick(0.1, 3)")
        T.step("Veyra P3 (40 %): the Warden phase (red-ring beam telegraph, grows to 6x)", st["phase"] == 3 and st["p3"] and st["pend"] >= 1 and st["scale"] == 6, st=st)
        nf("qaHp('veyra', 0.1)"); st = nf("qaTick(0.1, 3)")
        T.step("Veyra P4 (15 %): she stops, the choice opens, and she cannot die before it", st["phase"] == 4 and st["p4"] and st["dlg"] == "veyra" and st["pend"] == 0 and st["hp"] >= 0.1 * 2800, st=st)
        choices = T.ev("window.__hm.dlg && window.__hm.dlg.choice ? window.__hm.dlg.choice.options.map((o) => o.label) : null")
        T.step("the P4 choice for a player who is NOT redeemable: only 'End it.'", choices == ["End it."], choices=choices)
        nf("qaEnding('defeated')")
        T.step("the endings set flags (veyra_defeated / veyra_redeemed)", T.ev("window.__hm.S.flags.veyra_defeated === 1"))
        T.ev("window.__hm.dropDialogue && window.__hm.dropDialogue()")
        T.step("no JS errors in the Niflheim run", not [e for e in errors if "niflheim" in e.lower() or "nifl" in e.lower()], errs=errors[-3:])
    except Exception:
        try:
            rep.setdefault("shots", {})["nf_fail"] = T.shot("nf_fail")
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
    ap.add_argument("--out", default=str(GAME / "shots" / "niflheim_smoke"))
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
            steps(b, url, T, (960, 540), errors, rep, SM.STUB, out)
            rep["pass"] = True
        except Exception as e:  # noqa: BLE001
            rep["pass"] = False; rep["error"] = str(e)[:400]
            log(f"FAIL: {e}")
        b.close()
    srv.shutdown()
    rep["seconds"] = round(time.time() - t0, 1); rep["steps"] = T.steps; rep["errors"] = errors[:20]
    (out / "smoke_niflheim.json").write_text(json.dumps(rep, indent=1))
    log(f"smoke_niflheim: {'PASS' if rep['pass'] else 'FAIL'} {sum(s['pass'] for s in T.steps)}/{len(T.steps)} steps in {rep['seconds']} s")
    sys.exit(0 if rep["pass"] else 1)


if __name__ == "__main__":
    main()
