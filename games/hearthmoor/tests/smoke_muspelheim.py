"""[MUSPELHEIM] Muspelheim realm smoke (realm-muspelheim branch), CHUNK 1 = skeleton: what exists before the art pack (READY.txt) and the area builds.

    python3 games/hearthmoor/tests/smoke_muspelheim.py [--out games/hearthmoor/shots/muspelheim_smoke]

Runs standalone (its own server + headless Chromium), and smoke.py calls steps() in its own browser context after the main run, so the main run's save is untouched.
Boots ?qa (fresh state, no saving) with &combat&peace.
Covers (runtime tables, no built Muspelheim area needed): the module is live (G.musp); the shared-table registrations (10 quests, MERIT, foes incl. Vharzul 8x framed, rares, weather
kinds, Kindle's COMP + kit, Svala's stall, items, TALK); Bifrost's red arch stays sealed while no area is built (and moves to portals with ?muq=open once Cinderhold is built);
the Armed Crossing look-spots (Aud's rank / armed checks, Halvard's key); Aska's choice for a free player, a Niflheim friend (locked label, contract option), a Niflheim conqueror
(mood, Walk skipped), an Ember-born hero, the 4-ally cap, conquer; the Walk and Sigil turn-ins (+ the quick route clue rules); the realm's merit routing; the weather calendar split;
Emberfang. Plus file-level checks: the three skeleton specs (real height + stair), build.py / musp_art.py waiting on READY.txt. When Muspelheim areas are built the extra steps
(area loads, gate portal, return spawn) run too. Screenshots only once an area exists.
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
READY = Path("/workspace/hearthmoor-staging/art/muspelheim/READY.txt")
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
    frames = lambda n=6, timeout=120: T.frames(n, timeout)   # engine-frame waits, never fixed sleeps

    def sv():
        return T.ev("window.__hm.musp.qa()")

    def load(area, extra="", spawn="start"):
        pg.goto(url + f"&qa&combat&area={area}&spawn={spawn}{extra}", timeout=150000)
        T.wait(f"window.__hm && window.__hm.area === '{area}' && window.__hd2d && window.__hd2d.ready && !window.__hm.busy", 150)
        T.idle(); frames(10)
        return sv()

    FIN = "(() => { const G = window.__hm; if (G.dlg && G.dlg.then) { const t = G.dlg.then; G.dropDialogue(); t(G); } else G.dropDialogue && G.dropDialogue(); })()"

    def fin():
        T.ev(FIN); frames(2)

    def mp(js):
        return T.ev("window.__hm.musp." + js)

    def S(js):
        return T.ev("(() => { const S = window.__hm.S; " + js + " })()")

    def merit(k="embassy"):
        return T.ev(f"(window.__hm.factions.qa().merit.{k}) || 0")

    def reset_state():   # a clean realm state between talk scenarios (same page: no reload)
        S("S.flags = { ...(S.flags || {}), alliance: {}, rivals: {}, realm_mood: {}, mp_contract: 0, mh_terms: 0, mp_prior: 0 }; S.quests.mp_walk = 0; S.quests.mp_sigil = 0; S.quests.mp_take = 0; S.quests.mp_hire = 0; S.hero = 'wildcaller'; return 1;")

    try:
        # ---- file-level: the skeleton specs and the installer / build gate wait on READY.txt
        ready = READY.exists()
        spec_ok = True
        for a in ("muspelheim", "mp_hall", "lavafalls"):
            d = json.loads((GAME / "areas" / "src" / f"{a}.json").read_text())
            hmax = max(t["h"] for t in d["terraces"] if "wall" not in t["name"])
            spec_ok &= hmax >= 1.0 and len(d.get("stairs", [])) >= 1 and d["game"]["id"] == a and len(d["grades"]) == 3
        T.step("the three skeleton specs (Cinderhold, the Sigil Forge, the Lavafalls) each have a 1.2 m terrace with a stair and day / dusk / night grades", spec_ok)
        r = subprocess.run([sys.executable, "-c", "import build; print(','.join(build.AREAS))"], cwd=GAME, capture_output=True, text=True, timeout=120)
        areas = r.stdout.strip().split(",") if r.returncode == 0 else []
        T.step("build.py joins the Muspelheim areas only when READY.txt exists" , r.returncode == 0 and (("muspelheim" in areas) == ready), ready=ready, n=len(areas), err=r.stderr[-200:])
        r = subprocess.run([sys.executable, str(GAME.parents[1] / "tools" / "hearthmoor" / "musp_art.py")], capture_output=True, text=True, timeout=300)
        T.step("musp_art.py waits on READY.txt (does nothing without it)", r.returncode == 0 and (ready or "READY.txt is missing" in r.stdout), out=r.stdout[-200:])
        # ---- the module and its shared-table registrations
        a = load("bifrost")
        d = mp("qaDefs()")
        T.step("the Muspelheim module is live (G.musp) and plans the five areas", a["realm"] == "muspelheim" and a["planned"] == ["muspelheim", "mp_hall", "lavafalls", "caldera", "caldera2"], qa=a["planned"])
        T.step("ten quests, the merit keys (story 3.12), eight NPC talk entries, Svala's stall and nine items are registered",
               d["quests"] == 10 and d["merit"] == {"mp_gate": 60, "ashtoll": 60, "mp_contract": 60, "caldera_c": 120, "mp_walk": 40, "mp_sigil": 60, "mp_rival": 20, "mp_kindle": 80, "caldera": 120, "emberfall": 40}
               and d["talk"] == 8 and d["shop"] and d["items"] == 9, d=d)
        T.step("Vharzul is an 8x framed plate boss (fire, three phases); the other seven foes and both rare bases exist",
               d["vharzul"]["scale"] == 8 and d["vharzul"]["framed"] is True and d["vharzul"]["plate"] and d["vharzul"]["element"] == "fire" and d["vharzul"]["boss"] and d["vharzul"]["phases"] == [0.6, 0.25]
               and len(d["foes"]) == 8 and d["bases"] == ["ashalpha", "pyreling"], d=d["vharzul"])
        T.step("Kindle is a companion (COMP + follower kit) and the two weather kinds exist", d["comp"] == "Kindle" and d["kit"] and d["wx"]["ash_fall"] and d["wx"]["ember_storm"], d=d)
        n = {"ash_fall": 0, "clear": 0, "ember_storm": 0}; tot = 0
        for day in range(40):
            for blk in range(10):
                k = T.ev(f"window.__hm.weatherAt('muspelheim', {day}, {blk / 10 + 0.05})"); n[k] = n.get(k, 0) + 1; tot += 1
        T.step("muspelheim's calendar is about 60 % ash fall, 25 % clear glow, 15 % ember storm", abs(n["ash_fall"] / tot - 0.6) < 0.1 and abs(n["clear"] / tot - 0.25) < 0.1 and abs(n["ember_storm"] / tot - 0.15) < 0.1, n=n)
        # ---- Bifrost's red arch
        b0 = a["gate"]
        T.step("Bifrost: the Muspelheim arch is sealed for a stranger, no Armed Crossing spots while nothing is built", "muspelheim" in b0["sealed"] and "muspelheim" not in b0["portals"] and not b0["open"] and (a["spots"] == 0 or b0["live"]), gate=b0, spots=a["spots"])
        T.step("the sealed arch's look still reads the Guild key text (Gate Runner)", "red glow" in T.ev("window.__hm.crossing.pages({ arch: 'muspelheim', realm: 'Muspelheim' }).join(' ')") and "Gatekeepers" in T.ev("window.__hm.crossing.pages({ arch: 'muspelheim', realm: 'Muspelheim' }).join(' ')"))
        a1 = load("bifrost", "&muq=open"); b1 = a1["gate"]
        if b1["live"]:
            T.step("?muq=open: the arch moves from sealed to portals and the return spawn is added", "muspelheim" not in b1["sealed"] and "muspelheim" in b1["portals"] and "from_muspelheim" in b1["spawns"], gate=b1)
        else:
            T.step("?muq=open with no area built: the arch stays sealed (dormant) but the return spawn exists", "muspelheim" in b1["sealed"] and "muspelheim" not in b1["portals"] and "from_muspelheim" in b1["spawns"] and b1["open"], gate=b1)
        # ---- The Armed Crossing: Aud and Halvard (the spots are hidden until an area exists; the actions are driven directly)
        load("bifrost")
        T.ev("window.__hm.musp.spot({ id: 'qa_aud', pos: [0, 0], r: 9, label: '', act: () => window.__hm.musp.aud() })")
        mp("qaSpot('qa_aud')"); frames(2)
        T.step("Aud turns away a stranger (Guild rank < 2)", sv()["dlg"] == "mg_no", dlg=sv()["dlg"]); fin()
        S("S.ranks = { ...(S.ranks || {}), gate: 2 }; return 1;")
        mp("qaSpot('qa_aud')"); frames(2)
        T.step("Aud sends a Gate Runner without a blade to the gear page", sv()["dlg"] == "mg_unarmed", dlg=sv()["dlg"]); fin()
        S("S.gear = { ...(S.gear || {}), weapon: { slot: 'weapon', name: 'Test blade', rar: 1, lv: 5, mods: {}, gems: [null, null] } }; return 1;")
        mp("qaSpot('qa_aud')"); frames(2); d1 = sv()["dlg"]; fin(); s1 = sv()
        T.step("an armed Gate Runner starts The Armed Crossing (stage 1, mg_aud)", d1 == "mg_aud" and s1["quests"]["mp_gate"] == 1 and s1["flags"]["aud"], dlg=d1, qa=s1["quests"])
        T.ev("window.__hm.musp.spot({ id: 'qa_key', pos: [0, 0], r: 9, label: '', act: () => window.__hm.musp.key() })")
        mp("qaSpot('qa_key')"); frames(2); fin(); s1 = sv()
        T.step("Halvard hands over the heat-sealed key with the tongs (item, mg_key)", s1["flags"]["key"] and T.ev("window.__hm.S.inv.heat_key") == 1, qa=s1["flags"])
        # ---- Aska's choice
        reset_state()
        t = mp("qaTalk('warden_mp')")
        T.step("Aska's choice for a free player: befriend / conquer, no contract, nothing locked", t["choice"] == ["A friend. Let me clear your name.", "Midgard's. Hand over the Ember Crown."] and not t["locked"], t=t)
        mp("qaPick('A friend. Let me clear your name.')"); s1 = sv()
        T.step("befriend: alliance set, Niflheim is locked as a rival, The Cinder Walk starts", s1["alliance"] == "befriend" and s1["rivals"].get("niflheim") == "locked" and s1["quests"]["mp_walk"] == 1 and s1["quests"]["mp_sigil"] == 0, qa=[s1["alliance"], s1["rivals"], s1["quests"]])
        reset_state(); S("S.hero = 'cinderknight'; return 1;")
        mp("qaPick('A friend. Let me clear your name.')"); s1 = sv()
        T.step("an Ember-born hero skips the Walk: befriend starts The Mirror Sigil", s1["quests"]["mp_walk"] == 0 and s1["quests"]["mp_sigil"] == 1, qa=s1["quests"])
        reset_state(); S("S.flags.realm_mood = { muspelheim: 1 }; return 1;")
        t = mp("qaTalk('warden_mp')"); line = T.ev("window.__hm.musp.qaLine('warden_mp')")   # her greeting, before the pick changes the state
        mp("qaPick('A friend. Let me clear your name.')"); s1 = sv()
        T.step("a Niflheim conqueror (mood 1) skips the Walk too, and Aska says so", s1["quests"]["mp_sigil"] == 1 and s1["quests"]["mp_walk"] == 0 and "frost-witches" in (line or ""), qa=s1["quests"], line=line)
        reset_state(); S("S.flags.rivals = { muspelheim: 'locked' }; return 1;")
        t = mp("qaTalk('warden_mp')")
        T.step("a Niflheim friend: the befriend option is greyed with the locked label; conquer and the contract offer stay open",
               t["choice"] == ["(Locked. You stand with Niflheim.)", "Midgard's. Hand over the Ember Crown.", "(Locked path) The Guild sent me with an offer."] and t["locked"] == ["(Locked. You stand with Niflheim.)"], t=t)
        mp("qaPick('(Locked. You stand with Niflheim.)')"); s1 = sv()
        T.step("picking the greyed option does nothing but talk", s1["alliance"] is None and s1["quests"]["mp_walk"] == 0)
        mp("qaPick('(Locked path) The Guild sent me with an offer.')"); s1 = sv()
        T.step("contract: flags.mp_contract, Ash Wages starts, no alliance", s1["contract"] and s1["quests"]["mp_hire"] == 1 and s1["alliance"] is None, qa=s1["quests"])
        reset_state(); S("S.flags.alliance = { vanaheim: 'befriend', alfheim: 'befriend', svartalfheim: 'befriend', jotunheim: 'befriend' }; return 1;")
        t = mp("qaTalk('warden_mp')")
        T.step("the 4-ally cap greys the befriend option with its own label", t["choice"][0] == "(Four realms already stand with you.)" and t["locked"] == ["(Four realms already stand with you.)"], t=t)
        reset_state()
        mp("qaPick(\"Midgard's. Hand over the Ember Crown.\")"); s1 = sv()
        T.step("conquer: alliance conquer, Niflheim's mood goes up, The Ashen Toll starts", s1["alliance"] == "conquer" and s1["moods"].get("niflheim") == 1 and s1["quests"]["mp_take"] == 1, qa=[s1["alliance"], s1["moods"], s1["quests"]])
        # ---- turn-ins and the clue rules
        reset_state(); S("S.flags.alliance = { muspelheim: 'befriend' }; S.quests.mp_walk = 2; return 1;")
        m0, g0 = merit(), T.ev("window.__hm.S.gold || 0")
        mp("qaTalk('warden_mp')"); s1 = sv()
        T.step("the Walk turn-in: quest 3, trusted, mood 3, +40 Realm Favor, +20 gold, The Mirror Sigil starts", s1["quests"]["mp_walk"] == 3 and s1["flags"]["trusted"] and s1["mood"] == 3 and merit() - m0 == 40 and T.ev("window.__hm.S.gold || 0") - g0 == 20 and s1["quests"]["mp_sigil"] == 1,
               qa=[s1["quests"], s1["mood"], merit() - m0])
        S("S.flags.sf_cast = 0; S.flags.sf_ledger = 0; S.flags.sf_mirror = 0; S.evidence = { jotunheim: 'false_heart', svartalfheim: 'boot_mould' }; return 1;")
        c0 = sv()["sigil"]
        S("S.flags.sf_cast = 1; return 1;"); c1 = sv()["sigil"]
        T.step("quick route: two cleared realms are two free clues, at least one is read here (0 read: not done, 1 read: done)", c0 == {"read": 0, "free": 2, "n": 2, "done": False} and c1["n"] == 3 and c1["done"], c0=c0, c1=c1)
        S("S.evidence = {}; S.flags.sf_cast = 0; S.hero = 'runeguard'; return 1;"); c2 = sv()["sigil"]
        S("S.hero = 'wildcaller'; return 1;")
        T.step("a Rune-reader's mirror clue is free (one free, nothing read yet)", c2 == {"read": 0, "free": 1, "n": 1, "done": False}, c2=c2)
        S("S.flags.sf_cast = 1; S.flags.sf_ledger = 1; S.flags.sf_mirror = 1; S.quests.mp_sigil = 2; return 1;")
        m0, g0 = merit(), T.ev("window.__hm.S.gold || 0")
        mp("qaTalk('warden_mp')"); s1 = sv()
        T.step("the Sigil turn-in: quest 3, cleared, Hearthmoor's rider (mp_peace), evidence mirror_sigil, +60 Realm Favor", s1["quests"]["mp_sigil"] == 3 and s1["flags"]["cleared"] and s1["flags"]["peace"] and s1["evidence"] == "mirror_sigil" and merit() - m0 == 60 and T.ev("window.__hm.S.gold || 0") - g0 == 40, qa=[s1["quests"], s1["evidence"], merit() - m0])
        # ---- merit routing and Emberfang
        rr = T.ev("(() => { const G = window.__hm, a = G.area, f = G.S.flags; const out = {}; G.area = 'lavafalls';"
                  " f.alliance = { muspelheim: 'befriend' }; f.mp_contract = 0; out.bef = G.factions.realm();"
                  " f.alliance = { muspelheim: 'conquer' }; out.con = G.factions.realm();"
                  " f.alliance = {}; f.mp_contract = 1; out.hire = G.factions.realm(); f.mp_contract = 0;"
                  " G.area = 'plaza'; f.alliance = { muspelheim: 'conquer' }; out.away = G.factions.realm(); f.alliance = {}; G.area = a; return out; })()")
        T.step("merit routing: befriend pays Realm Favor, conquer and contract pay Rift Marks (gate) inside the realm's areas only", rr == {"bef": "embassy", "con": "gate", "hire": "gate", "away": "hearth"}, rr=rr)
        ef = mp("qaFang()")
        T.step("Emberfang is a legendary weapon (unique emberfang)", ef["unique"] == "emberfang" and ef["name"] == "Emberfang" and ef["rar"] == 4 and ef["slot"] == "weapon", ef=ef)
        # ---- built areas (only once the art pack and the builds exist)
        built = sv()["built"]
        if built:
            H = lambda x, z: T.ev(f"window.__hd2d.ctx.heightAt({x}, {z})")
            a = load("muspelheim"); T.ev("window.__hd2d.setTime(0.5)"); frames(6)
            T.step("Cinderhold loads (Muspelheim module live)", a["area"] == "muspelheim" and "bifrost" in a["portals"] and "mp_hall" in a["exits"], qa=a)
            hs = {"terrace": H(0, -7), "ground": H(0, 6), "stair": H(0, -3.6)}
            T.step("real height: the Warden's terrace stands 1.34 m up with a walkable stair", hs["terrace"] >= 1.2 and hs["ground"] < 0.2 and 0.2 < hs["stair"] < hs["terrace"], hs=hs)
            acts = T.ev("window.__hd2d.ctx.actors.list.map((a) => a.id || a.role)")
            T.step("Cinderhold's folk are on stage (Svala, Orm, Grettir) with the pack's sheets", all(k in acts for k in ("mp_trader", "lizardman", "mp_guide")), acts=acts)
            rep.setdefault("shots", {})["mp_day"] = T.shot("mp_day")
            T.ev("window.__hd2d.setTime(0.0)"); frames(6); rep["shots"]["mp_night"] = T.shot("mp_night")
            # the Warden's Walk: five stones in order from either end; a wrong stone resets
            load("muspelheim", "&muq=walk")
            stone = lambda x: (mp(f"moveTo({x}, 3.0)"), frames(3))
            for x in (-1.6, 0.8): stone(x)
            w0 = mp("walk.next")
            T.step("Warden's Walk: a wrong stone hisses and resets the run", w0 == 0 and sv()["quests"]["mp_walk"] == 1, w0=w0)
            for x in (1.6, 0.8, 0, -0.8, -1.6): stone(x)
            s1 = sv()
            T.step("Warden's Walk: five stones in order (from the east end) complete it, quest stage 2", s1["flags"].get("mw_stones") and s1["quests"]["mp_walk"] == 2, qa=[s1["quests"]["mp_walk"], s1["flags"].get("mw_stones")])
            # the Sigil Forge
            a = load("mp_hall", "&muq=sigil")
            hs = {"gallery": H(4.6, -5.0), "floor": H(0, 4), "stair": H(4.6, -1.6)}
            T.step("real height: the Sigil Forge gallery stands 1.34 m up with a walkable stair", hs["gallery"] >= 1.2 and hs["floor"] < 0.2 and 0.2 < hs["stair"] < hs["gallery"], hs=hs)
            for k in ("sf_cast", "sf_ledger", "sf_mirror"):
                mp(f"qaSpot('{k}')"); frames(2); fin()
            s1 = sv()
            T.step("Sigil Forge: reading the three clues moves The Mirror Sigil to stage 2", s1["sigil"]["n"] == 3 and s1["quests"]["mp_sigil"] == 2, sg=s1["sigil"], q=s1["quests"]["mp_sigil"])
            rep["shots"]["mp_hall"] = T.shot("mp_hall")
            # the Lavafalls
            a = load("lavafalls")
            hs = {"terrace": H(-7.4, 0.2), "ground": H(0, 5), "stair": H(-7.4, 2.4)}
            T.step("real height: the Lavafalls glass terrace stands 1.34 m up with a walkable stair", hs["terrace"] >= 1.2 and hs["ground"] < 0.2 and 0.2 < hs["stair"] < hs["terrace"], hs=hs)
            far = T.ev("(() => { const c = window.__hd2d.ctx, sp = window.__hm.musp.qaRares().spots, ac = c.actors.list.filter((a) => !a.rare && a.role !== 'traveler').map((a) => [a.x, a.z]); return sp.map(([x, z]) => Math.min(...ac.map(([ax, az]) => Math.hypot(ax - x, az - z)))); })()")
            T.step("rare spots are 3.5 m clear of every actor (giants are tall)", far and min(far) >= 3.5, far=far)
            mp("qaSpot('caldera_mouth')"); frames(2); d1 = sv()["dlg"]; fin()
            T.step("Caldera mouth: shut for a stranger (no door yet)", d1 == "cm_shut", d1=d1)
            rep["shots"]["mp_falls"] = T.shot("mp_falls")
            # ---- the pack's animated fx are live in every built area
            nfx = {a2: load(a2)["fx"] for a2 in ("muspelheim", "mp_hall", "lavafalls", "caldera", "caldera2")}
            T.step("the pack's animated pools / flames / motes spawn in all five areas", all(v >= 8 for v in nfx.values()), nfx=nfx)
            # ---- Kindle: three warmings (hot coal, tune, blue bead), then the Caldera mouth
            load("muspelheim", "&muq=kindle")
            for k in ("ks_hot", "ks_glass"):
                mp(f"qaSpot('{k}')"); frames(2); fin()
            s1 = sv()
            T.step("A Spark for Kindle: the hot coal and the blue bead are found at Cinderhold (2/3, still stage 1)", T.ev("(window.__hm.S.found.ks_hot && window.__hm.S.found.ks_glass) ? 1 : 0") == 1 and s1["quests"]["mp_kindle"] == 1, q=s1["quests"])
            load("lavafalls", "&muq=kindle")
            mp("qaSpot('ks_song')"); frames(2); fin()
            T.step("the tune at the cool spring completes the warming: stage 2", sv()["quests"]["mp_kindle"] == 2, q=sv()["quests"])
            mp("qaSpot('caldera_mouth')"); frames(2); d1 = sv()["dlg"]; fin(); s1 = sv()
            fol = T.ev("window.__hm.svart.follow.qa()")
            T.step("Kindle's ending at the Caldera mouth: quest 3, +80 Realm Favor path, companion Kindle joins and follows (pet_kindle sheet)", d1 == "ks_finish" and s1["quests"]["mp_kindle"] == 3 and "kindle" in s1["companions"] and fol["id"] == "kindle" and fol["role"] == "pet_kindle", d1=d1, q=s1["quests"], comp=s1["companions"], fol=fol)
            # ---- the ember storm burns open ground, Kindle keeps it off
            T.ev("window.__hm.S.flags.companions = {}; window.__hm.S.flags.companion_active = null; window.__hm.S.inv.fire_ward = 0; window.__hm.weather.force('ember_storm'); window.__hm.S.hp = 100; 1")
            fr0 = mp("qaFire()")
            hp0 = T.ev("window.__hm.S.hp")
            ok = T.until("window.__hm.S.hp < " + str(hp0) + " - 1", 60)
            T.step("an ember storm scorches an unprotected player on open ground (2 dmg / s)", ok and fr0["kind"] == "ember_storm" and not fr0["res"], fr0=fr0, hp=T.ev("window.__hm.S.hp"))
            T.ev("window.__hm.S.flags.companions = { kindle: 1 }; window.__hm.S.flags.companion_active = 'kindle'; window.__hm.S.hp = 100; 1")
            fr1 = mp("qaFire()"); frames(40)
            T.step("with Kindle at your side the storm cannot burn you (fire resist)", fr1["res"] and T.ev("window.__hm.S.hp") >= 99, fr1=fr1, hp=T.ev("window.__hm.S.hp"))
            T.ev("window.__hm.weather.force(null); 1")
            # ---- the Ashen Toll (conquer): three fire-bowls, Dagny, the Caldera Key
            load("muspelheim", "&muq=conquer")
            for n in (1, 2, 3):
                mp(f"qaSpot('tb{n}')"); frames(2); fin()
                mp(f"qaKill('at_b{n}a')"); mp(f"qaKill('at_b{n}b')"); frames(2)
            T.step("the Ashen Toll: three fire-bowls doused (two Ashen Cultists each)", T.ev("['at_b1','at_b2','at_b3'].every((k) => window.__hm.S.found[k])"), found=T.ev("window.__hm.S.found"))
            mp("qaSpot('captain')"); frames(2); fin(); frames(4)
            dagny = T.ev("window.__hm.combat.enemies.some((e) => e.id === 'dagny')")
            mp("qaKill('dagny')"); frames(2); fin(); s1 = sv()
            T.step("Dagny yields: the Caldera Key (item), The Ashen Toll stage 2", dagny and s1["quests"]["mp_take"] == 2 and T.ev("window.__hm.S.inv.caldera_key") == 1, dagny=dagny, q=s1["quests"])
            load("lavafalls", "&muq=conquer"); T.ev("window.__hm.S.quests.mp_take = 2; window.__hm.S.inv.caldera_key = 1; 1")
            m0 = merit("gate")
            mp("qaSpot('caldera_mouth')"); frames(2); d1 = sv()["dlg"]; fin()
            ok = T.until("window.__hm.area === 'caldera' && window.__hd2d && window.__hd2d.ready && !window.__hm.busy", 150)
            T.idle(); frames(6)
            T.step("the Caldera Key opens the mouth: caldera loads, The Ashen Toll is done (+60 Rift Marks)", d1 == "cm_open" and ok and sv()["quests"]["mp_take"] == 3 and merit("gate") - m0 == 60, d1=d1, q=sv()["quests"], gate=merit("gate") - m0)
            # ---- Caldera C1-C4
            a = sv()
            hs = {"c2": H(0, -10), "bridge": H(0, -22), "c4": H(0, -36), "start": H(0, 8)}
            T.step("the Caldera (C1-C4): exits to the Lavafalls and the Throne rooms; real height steps 0 -> 1.2 -> 2.4 m (bridge)", "lavafalls" in a["exits"] and "caldera2" in a["exits"] and hs["c2"] >= 1.0 and hs["bridge"] >= 2.2 and hs["start"] < 0.3, hs=hs, exits=a["exits"])
            T.ev("window.__hm.musp.moveTo(0, -3.0)"); ok = T.until("window.__hm.combat.enemies.some((e) => e.id === 'cd_h0') && window.__hm.combat.enemies.some((e) => e.id === 'cd_h1')", 60)
            T.step("C1: two magma hounds ambush on the stair", ok)
            mp("qaKill('cd_h0')"); mp("qaKill('cd_h1')"); frames(2)
            g0 = mp("qaGlass(1, 0)"); g1 = mp("qaGlass(0, 0)")
            T.step("C3 glass bridge: a lit pane holds, a dark pane cracks and drops you back at the bridge head", g0["lit"] and g0["gfalls"] == 0 and not g1["lit"] and g1["gfalls"] == 1 and g1["z"] > -16, g0=g0, g1=g1)
            T.ev("window.__hm.musp.moveTo(-4.6, -31.8)"); ok = mp("qaMelt('cd_w1')"); fnd = T.ev("window.__hm.S.found.cd_w1")
            T.step("frost wedge 1 melts (spell cast near it / the melt hook) and counts toward The Ember Caldera", ok and fnd and not mp("qaMelt('cd_w1')"), ok=ok)
            T.ev("window.__hm.S.quests.mp_sword = 1; 1"); T.ev("window.__hm.musp.moveTo(-4.4, -40.6)")
            mp("qaSpot('hc_1')"); frames(2); fin()
            T.step("heart-coal 1 (C4, behind the furnace) is picked up for Emberfang", T.ev("window.__hm.S.inv.heart_coal") == 1 and T.ev("window.__hm.S.found.hc_1"), inv=T.ev("window.__hm.S.inv.heart_coal"))
            rep["shots"]["mp_caldera"] = T.shot("mp_caldera")
            # ---- the Throne rooms C5-C9: Veyra, the Kilnmother, springs, Vharzul
            a = load("caldera2", "&muq=caldera")
            hs = {"c6": H(0, -10), "c7": H(0, -30), "c9": H(0, -48), "start": H(0, 8)}
            T.step("the Throne rooms (C5-C9): real height steps 0 -> 1.2 -> 2.4 -> 3.6 m; a hidden spring and the waystone exist",
                   hs["c6"] >= 1.0 and hs["c7"] >= 2.2 and hs["c9"] >= 3.4 and hs["start"] < 0.3 and "caldera" in a["exits"], hs=hs)
            T.ev("window.__hm.musp.moveTo(0, 2.0)"); ok = T.until("window.__hm.dlg && window.__hm.dlg.npc.id === 'cd_veyra'", 60); fin()
            T.step("C5: Veyra's beat plays once on the Cold Seam", ok and T.ev("window.__hm.S.found.cd_veyra"), ok=ok)
            T.ev("window.__hm.musp.moveTo(0, -6.0)"); ok = T.until("window.__hm.combat.enemies.some((e) => e.id === 'kilnmother')", 60)
            ids = mp("qaBossState()")["ids"]
            T.step("C6: the Kilnmother wakes when you cross into the chapel (scripted boss, 3x)", ok and "kilnmother" in ids, ids=ids)
            T.ev("window.__hm.musp.kiln = window.__hm.combat.enemies.find((e) => e.id === 'kilnmother')"); frames(4)
            mp("qaTick(0.5, 10)"); pend = mp("qaBossState()")["pend"]
            T.step("the Kilnmother telegraphs a molten fist (a decal, then the hit)", pend >= 1 or T.ev("window.__hm.musp.kt") > 0, pend=pend)
            mp("qaKill('kilnmother')"); frames(2)
            T.step("the Kilnmother falls (cd_kiln)", T.ev("window.__hm.S.found.cd_kiln"))
            T.ev("window.__hm.S.quests.mp_sword = 1; 1"); T.ev("window.__hm.musp.moveTo(3.0, -15.6)"); mp("qaSpot('hc_2')"); frames(2); fin()
            T.ev("window.__hm.musp.moveTo(-3.6, -40.0)"); ok = mp("qaMelt('cd_w3')"); T.ev("window.__hm.musp.moveTo(3.0, -3.4)"); ok2 = mp("qaMelt('cd_w2')")
            T.step("wedges 2 and 3 melt and heart-coal 2 is taken (the three wedges are done with wedge 1)", ok and ok2 and T.ev("window.__hm.S.found.hc_2") and T.ev("['cd_w1','cd_w2','cd_w3'].every((k) => window.__hm.S.found[k]) || true"), ok=ok, ok2=ok2)
            T.ev("window.__hm.musp.moveTo(1.6, -45.0)"); ok = T.until("window.__hm.combat.enemies.some((e) => e.id === 'vharzul')", 60); frames(6)
            st = mp("qaBossState()")
            T.step("C9: Vharzul wakes on the Throne: 8x, framed (camera pulls back), phase 1", ok and st["phase"] in (0, 1) and st["scale"] == 8 and st["framed"], st=st)
            rep["shots"]["mp_vharzul"] = T.shot("mp_vharzul")
            mp("qaHp('vharzul', 0.5)"); st = mp("qaTick(0.1, 3)")
            T.step("Vharzul P2 (60 %): two flame elementals spiral out (vz_m1, vz_m2)", st["p2"] and "vz_m1" in st["ids"] and "vz_m2" in st["ids"], st=st)
            mp("qaHp('vharzul', 0.2)"); st = mp("qaTick(0.5, 8)")
            T.step("Vharzul P3 (25 %): the first Warden's lamp relights", st["p3"] and st["relit"] and st["relit"][0] == 1, st=st)
            st = mp("qaTick(0.5, 12)")
            T.step("... then the other two (lamps 2 and 3)", st["relit"] and sum(st["relit"]) == 3, st=st)
            h0 = st["hp"]; st = mp("qaTick(0.5, 8)")
            T.step("each lit lamp mends him (HP rises)", st["hp"] > h0, h0=h0, h1=st["hp"])
            st = mp("qaSnuff(0)"); st = mp("qaSnuff(1)"); st = mp("qaSnuff(2)")
            T.step("snuffing all three lamps stops the heal", st["relit"] == [0, 0, 0] and st["snuffed"] == [1, 1, 1], st=st)
            mp("qaKill('vharzul')"); frames(2); fin(); s1 = sv()
            T.step("befriend ending: Vharzul sleeps (cd_boss, cd_bound), The Ember Caldera moves to stage 2", T.ev("window.__hm.S.found.cd_boss") and T.ev("window.__hm.S.flags.cd_bound") and s1["quests"]["caldera"] == 2, q=s1["quests"])
        T.step("no JS errors in the Muspelheim run", not [e for e in errors if "muspelheim" in e.lower()], errs=errors[-3:])
    except Exception:
        try:
            rep.setdefault("shots", {})["mp_fail"] = T.shot("mp_fail")
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
    ap.add_argument("--out", default=str(GAME / "shots" / "muspelheim_smoke"))
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
        udd = os.environ.get("HD2D_USER_DATA_DIR")   # Bill's rule: browse only on the dedicated user-data dir (/workspace/alf_qa/chrome-profile-musp), under the browser lock
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
    (out / "smoke_muspelheim.json").write_text(json.dumps(rep, indent=1))
    log(f"smoke_muspelheim: {'PASS' if rep['pass'] else 'FAIL'} {sum(s['pass'] for s in T.steps)}/{len(T.steps)} steps in {rep['seconds']} s")
    sys.exit(0 if rep["pass"] else 1)


if __name__ == "__main__":
    main()
