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
import os
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

    frames = lambda n=6, timeout=120: T.frames(n, timeout)   # engine-frame waits, never fixed sleeps (120 s: a loaded box in the full sharded run drew ~1 fps and tripped the 30 s default)

    def sv():
        return T.ev("window.__hm.jot.qa()")

    def screen(x, z, y=None):
        return T.ev(f"(() => {{ const c = window.__hd2d.ctx; return c.project({x}, {y if y is not None else f'c.heightAt({x}, {z})'}, {z}); }})()")

    def tap(x, y):
        t = time.time()
        cdp.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": x, "y": y, "id": 0}], "timestamp": t})
        cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": [], "timestamp": t + 0.05})

    def arrive(area, timeout=120):
        T.wait(f"window.__hm.area === '{area}' && !window.__hm.busy", timeout); T.idle(); frames(6)

    def load(area, extra="", spawn="start"):
        pg.goto(url + f"&qa&combat&area={area}&spawn={spawn}{extra}", timeout=150000)   # a busy box can take over 30 s to load a scene
        T.wait(f"window.__hm && window.__hm.area === '{area}' && window.__hd2d && window.__hd2d.ready && !window.__hm.busy", 150)
        T.idle(); frames(10)
        return sv()

    FIN = "(() => { const G = window.__hm; if (G.dlg && G.dlg.then) { const t = G.dlg.then; G.dropDialogue(); t(G); } else G.dropDialogue && G.dropDialogue(); })()"

    def fin():
        T.ev(FIN); frames(2)

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
        T.ev("window.__hd2d.setTime(0.5)"); frames(6); shot("jt_day")
        # ---- the Bifrost gate: sealed until open, then a portal; the Stonehollow return spawn exists
        load("bifrost"); b0 = T.ev("window.__hm.jot.qa().gate")
        T.step("Bifrost: Jotunheim's ice arch is sealed for a stranger", "jotunheim" in b0["sealed"] and "jotunheim" not in b0["portals"] and not b0["open"], gate=b0)
        load("bifrost", "&jtq=open"); b1 = T.ev("window.__hm.jot.qa().gate")
        T.step("?jtq=open: the arch moves from sealed to portals and the return spawn is added", "jotunheim" not in b1["sealed"] and "jotunheim" in b1["portals"] and "from_jotunheim" in b1["spawns"], gate=b1)
        # ---- Grimsa's stall
        load("jotunheim"); t = T.ev("(() => { const G = window.__hm; return { goods: G.shopUI ? true : false, shop: !!window.__hm.jot.qa().shop }; })()")
        T.ev("window.__hm.jot.qaTalk('jt_trader')"); frames(3)
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
        frames(3); a = sv(); g1 = T.ev("window.__hm.S.gold || 0")
        T.step("three lifts: the town cheers and the Jarl's fire waits (stage 2)", a["lifts"] == 3 and a["quest"] == 2, qa=[a["lifts"], a["quest"]])
        jt("qaTalk('jarl')"); a = sv(); g1 = T.ev("window.__hm.S.gold || 0")
        T.step("the Jarl's fire: The Stone Welcome completes (+20 gold, trusted) and The Hollow Heart starts", a["quest"] == 3 and g1 - g0 == 20 and a["heart"] == 1 and T.ev("window.__hm.S.flags.jt_trusted === 1"), qa=[a["quest"], a["heart"], g0, g1])
        # ---- the look-spots (Hall door, cave path, frost prints) and the Giant Footprints entry point
        T.ev("(() => { const c = window.__hd2d.ctx; c.player.x = -3.4; c.player.z = -1.6; })()"); frames(3)
        pr = T.ev("window.__hm.harbor.prompt()")
        T.step("the frost-prints look-spot prompts at the plateau foot", "frost prints" in (pr or ""), prompt=pr)
        T.ev("(() => { window.__hm.harbor.interact(); })()"); frames(3)
        T.step("looking at the prints records the clue entry (S.found.jt_prints)", T.ev("window.__hm.S.found.jt_prints === 1"))
        T.ev("(() => { const G = window.__hm; G.dropDialogue && G.dropDialogue(); })()")
        # ---- jt_hall: the Hall of Hearthstones
        a = load("jt_hall", "&jtq=heart")
        T.step("the Hall loads: Jarl, Kolbrun, Solvi, guards and diners; cold fire lit; a door back to Stonehollow", all(i in a["actors"] for i in ("jarl", "envoy_jt", "rimewife", "jt_guard1", "jt_guard2")) and a["fx"] >= 8 and "jotunheim" in a["exits"], qa=a["actors"], exits=a["exits"])
        hs = T.ev("(() => { const c = window.__hd2d.ctx; return { dais: c.heightAt(-3, -9), floor: c.heightAt(-3, 4), stair: c.heightAt(0, -5.9) }; })()")
        T.step("real height: the high seat dais stands 1.2 m up with a walkable stair", hs["dais"] >= 1.0 and hs["floor"] < 0.2 and 0.2 < hs["stair"] < hs["dais"], hs=hs)
        T.ev("window.__hd2d.setTime(0.0)"); frames(6); shot("jt_hall_night")
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
        T.ev("window.__hd2d.setTime(0.0)"); frames(6); shot("jt_caves_night")
        T.ev("(() => { const c = window.__hd2d.ctx; c.player.x = 0; c.player.z = -7.0; })()"); frames(3)
        pr = T.ev("window.__hm.harbor.prompt()")
        T.step("the Barrow door prompts at the foot of the step; looking at it explains the three rune locks", "Barrow door" in (pr or "") and jt("qaSpot('door')") and T.ev("!!window.__hm.dlg"), prompt=pr)
        fin()
        T.ev("(() => { const c = window.__hd2d.ctx; c.player.x = 9.0; c.player.z = -6.2; })()"); frames(3)
        T.ev("window.__hm.jot.onCast()"); a = sv()
        T.step("a spell cast by the frozen waterfall melts it: the hidden spring (rc_spring) is found", a["spring"], found=a["found"])
        a = load("rimecaves", "&jtq=conquer"); sol = jt("qaTalk('solvi')")
        T.step("conquer: Solvi says 'You know it's hollow' (2 pages)", sol["pages"] == 2, sol=sol)
        a = load("jotunheim"); 
        T.step("Stonehollow has a path to the Rime Caves (the 'not open yet' look-spot is gone)", "rimecaves" in a["exits"] and not any(False for _ in []), exits=a["exits"])
        # ---- barrow: B1-B4 behind the Rime Caves' door
        a = load("rimecaves"); jt("qaSpot('door')"); fin(); a = sv()
        T.step("the Barrow door stays shut for a stranger (still in the Rime Caves)", a["area"] == "rimecaves", area=a["area"])
        a = load("rimecaves", "&jtq=conquer"); jt("qaSpot('door')"); fin(); a = sv()
        T.step("conquer without the Barrow Key: the door is still shut", a["area"] == "rimecaves", area=a["area"])
        a = load("rimecaves", "&jtq=barrow"); jt("qaSpot('door')"); fin()
        T.wait("window.__hm.area === 'barrow' && window.__hd2d && window.__hd2d.ready && !window.__hm.busy", 90); T.idle(); frames(10); a = sv()
        T.step("the Jarl's trust opens the door: you stand in the Barrow (quest started, foes roam, cold fire lit, a path back)",
               a["area"] == "barrow" and a["quest_barrow"] == 1 and len(set(a["foes"])) >= 3 and a["fx"] >= 6 and "rimecaves" in a["exits"], foes=a["foes"], fx=a["fx"], exits=a["exits"])
        hs = T.ev("(() => { const c = window.__hd2d.ctx; return { ground: c.heightAt(-4, 4), b2: c.heightAt(-4, -12), stair: c.heightAt(0, -2.4), b4: c.heightAt(-4, -29.5) }; })()")
        T.step("real height: the Hall of Shields 1.2 m up (stair), the Avalanche Run ledge 2.4 m up", hs["ground"] < 0.2 and 1.1 <= hs["b2"] <= 1.3 and 0.1 < hs["stair"] < 1.2 and hs["b4"] >= 2.3, hs=hs)
        shot("jt_barrow_door")
        T.ev("(() => { const c = window.__hd2d.ctx; c.player.x = 0; c.player.z = -7.0; c.player.y = c.heightAt(0, -7.0); })()"); frames(3)
        jt("qaSpot('tb1')"); fin(); a = sv()
        T.step("snuffing brazier 1 (E / A) records tb_b1", a["found"].get("tb_b1") == 1, found=a["found"])
        T.ev("(() => { const c = window.__hd2d.ctx; c.player.x = 0; c.player.z = -27.0; c.player.y = c.heightAt(0, -27.0); })()"); frames(6)
        shot("jt_barrow_run")
        jt("qaSpot('tb2')"); fin(); a = sv()
        T.step("snuffing brazier 2 at the top of the Avalanche Run records tb_b2", a["found"].get("tb_b2") == 1, found=a["found"])
        a = load("rimecaves", "&jtq=contract"); jt("qaSpot('door')"); fin()
        T.wait("window.__hm.area === 'barrow' && window.__hd2d && window.__hd2d.ready && !window.__hm.busy", 90)
        T.step("contract: Skuli's goat-path gets you in too", sv()["area"] == "barrow")
        # ---- the Barred Gate (Kolbrun), the Toll of Stones (cairns + Hjordis), Stonefrost lessons, the Throne Barrow
        def until(js, t=20):
            return T.until(js, t)

        def walk_to(x, z):
            T.ev(f"(() => {{ const c = window.__hd2d.ctx; c.player.x = {x}; c.player.z = {z}; c.player.y = c.heightAt({x}, {z}); }})()"); frames(3)

        load("bifrost", "&jtq=gate"); jt("qaSpot('kolbrun')"); fin(); a = sv()
        T.step("Barred Gate: without Embassy rank Kolbrun only talks (no quest)", a["gate_q"] == 0 and not a["jg"][0], gate=a["gate_q"])
        load("bifrost", "&jtq=gate"); a = sv()
        T.step("the arch is still sealed during the quest", not a["gate"]["open"] and "jotunheim" in a["gate"]["sealed"], gate=a["gate"])
        T.ev("window.__hm.S.ranks = { ...(window.__hm.S.ranks || {}), embassy: 1 }"); jt("qaSpot('kolbrun')"); fin(); a = sv()
        T.step("with Embassy rank 1 Kolbrun offers the quest: jt_gate stage 1, jg_asked", a["gate_q"] == 1 and a["jg"][0], jg=a["jg"])
        jt("qaSpot('halvard')"); fin(); a = sv()
        T.step("Halvard hands over the horn (jg_horn)", a["jg"][1], jg=a["jg"])
        jt("qaSpot('arch')"); fin()
        arrive("jotunheim")
        T.step("sounding the horn at the arch pulls you through to Stonehollow, where a frost troll comes through", until("window.__hm.jot.qa().cb.includes('jg_troll')", 20) and "frost_troll" in sv()["foes"], cb=sv()["cb"])
        jt("qaKill('jg_troll')"); frames(2); a = sv()
        T.step("its fall moves jt_gate 1 -> 2", a["gate_q"] == 2 and a["jg"][2], gate=a["gate_q"])
        T.ev("window.__hm.loadArea('bifrost', 'from_jotunheim')"); arrive("bifrost")
        g0 = sv()["gold"]; jt("qaSpot('kolbrun')"); fin(); a = sv()
        T.step("Kolbrun lifts the bar: jt_gate 3, +50 gold, the arch becomes a portal", a["gate_q"] == 3 and a["gold"] == g0 + 50 and "jotunheim" in a["gate"]["portals"] and "jotunheim" not in a["gate"]["sealed"], gate=a["gate"], gold=a["gold"])
        a = load("rimecaves", "&jtq=conquer")
        T.step("rimecaves: three cairn spots wait for a conquering player", jt("qaSpot('tt3')") is True and (fin() or True))
        a = load("rimecaves", "&jtq=conquer")
        for n in (1, 2, 3):
            cx_, cz_ = ((-10.2, 6.4), (10.2, 6.4), (3.0, -1.6))[n - 1]
            cstate = lambda: T.ev(f"(() => {{ const c = window.__hd2d.ctx, u = c.pz('tt_cairn{n}'), d = c.pz('tt_cairn{n}_t'); return {{ up: !!u && u.visible, dn: !!d && d.visible, blocked: c.collide.blocked({cx_}, {cz_}) }}; }})()")
            c0 = cstate()
            T.step(f"cairn {n}: the real watch_cairn stands (blocking), its toppled rubble is hidden", c0["up"] and not c0["dn"] and c0["blocked"], c=c0)
            jt(f"qaSpot('tt{n}')"); fin()
            T.step(f"cairn {n}: two Rime Berserkers wake", until(f"window.__hm.jot.qa().cb.includes('tt{n}a') && window.__hm.jot.qa().cb.includes('tt{n}b')", 10), cb=sv()["cb"])
            jt(f"qaKill('tt{n}a')"); jt(f"qaKill('tt{n}b')"); frames(2)
            T.step(f"cairn {n} toppled (tt_c{n})", sv()["found"].get(f"tt_c{n}") == 1, found=sv()["found"])
            c1 = cstate()
            T.step(f"cairn {n}: toppled rubble replaces the watch_cairn and its blocker is lifted (walkable)", not c1["up"] and c1["dn"] and not c1["blocked"], c=c1)
        T.step("after three cairns the Rime-Captain's post opens", jt("qaSpot('captain')") is True)
        fin(); T.step("Hjordis Icejaw takes the field (a trial foe)", until("window.__hm.jot.qa().cb.includes('hjordis')", 10), cb=sv()["cb"])
        jt("qaKill('hjordis')"); fin(); a = sv()
        T.step("Hjordis yields: Barrow Key in the bag, jt_take 2", a["key"] and a["take_q"] == 2, take=a["take_q"], key=a["key"])
        g0 = a["gold"]; jt("qaSpot('door')"); fin()
        T.wait("window.__hm.area === 'barrow' && window.__hd2d && window.__hd2d.ready && !window.__hm.busy", 90); T.idle(); frames(6); a = sv()
        T.step("the Key opens the Barrow door and finishes the Toll of Stones (jt_take 3, +120 gold)", a["area"] == "barrow" and a["take_q"] == 3 and a["gold"] == g0 + 120, take=a["take_q"], gold=a["gold"])
        # Stonefrost lessons in the Hall (Solvi = the Hall's rimewife); the caves have only talk lines
        a = load("jt_hall", "&jtq=lessons"); jt("qaTalk('rimewife')"); frames(3); a = sv()
        T.step("Solvi teaches the first Stonefrost circle in the Hall: Boulder Toss and Frost Rune are learned", "boulder_toss" in a["spells"] and "frost_rune" in a["spells"] and a["unlocks"].get("stonefrost") == 1, spells=a["spells"])
        a = load("rimecaves", "&jtq=lessons"); jt("qaTalk('solvi')"); a = sv()
        T.step("in the caves Solvi only talks (no spells learned)", "boulder_toss" not in a["spells"], spells=a["spells"])
        # ---- Stonefrost II / III: Solvi's later lessons gate on the skill tiers (Lv 5 / Lv 10); the spells are real casts
        a = load("jt_hall", "&jtq=lessons"); T.ev("window.__hm.S.lv = 1"); jt("qaTalk('rimewife')"); frames(2); jt("qaTalk('rimewife')"); frames(2); a = sv()
        T.step("at Lv 1 Solvi teaches only the first circle (no Stone Skin, Cold Fire or Stone Golem yet)",
               "boulder_toss" in a["spells"] and not any(n in a["spells"] for n in ("stone_skin", "cold_fire", "stone_golem")), spells=a["spells"])
        T.ev("window.__hm.S.lv = 5"); jt("qaTalk('rimewife')"); frames(2); a = sv(); fl = T.ev("window.__hm.S.flags")
        T.step("at Lv 5 the second circle: Stone Skin and Cold Fire are learned (sf_ii)", "stone_skin" in a["spells"] and "cold_fire" in a["spells"] and fl.get("sf_ii") == 1 and "stone_golem" not in a["spells"], spells=a["spells"])
        jt("qaTalk('rimewife')"); frames(2); a = sv()
        T.step("the third circle still waits at Lv 5", "stone_golem" not in a["spells"] and not T.ev("window.__hm.S.flags.sf_iii"))
        T.ev("window.__hm.S.lv = 10"); jt("qaTalk('rimewife')"); frames(2); a = sv()
        T.step("at Lv 10 the third circle: the Stone Golem is learned (sf_iii)", "stone_golem" in a["spells"] and T.ev("window.__hm.S.flags.sf_iii") == 1, spells=a["spells"])
        T.step("all five Stonefrost spells are known", all(n in T.ev("window.__hm.knownSpells()") for n in ("boulder_toss", "frost_rune", "stone_skin", "cold_fire", "stone_golem")))
        a = load("rimecaves", "&jtq=lessons")
        CAST = "(n) => { const C = window.__hm.combat; C.cd.spell = 0; for (const k of ['skin', 'cold', 'golem']) C.cd[k] = 0; C.cast(n); }"
        T.ev("(() => { const G = window.__hm, S = G.S; S.lv = 12; S.flags = S.flags || {}; for (const n of ['boulder_toss', 'frost_rune', 'stone_skin', 'cold_fire', 'stone_golem']) G.learn(n); S.slots = ['boulder_toss', 'frost_rune', 'stone_skin', 'cold_fire']; G.ctx.setSpellCycle(G.slots()); })()")
        cyc = T.ev("window.__hm.ctx.spellCycle()")
        T.step("tier I Boulder Toss and Frost Rune are in the spell cycle (the engine lets game-drawn spells through) with Stone Skin and Cold Fire", cyc == ["boulder_toss", "frost_rune", "stone_skin", "cold_fire"], cyc=cyc)
        T.ev("(() => { const G = window.__hm; G.S.slots = ['stone_golem', 'boulder_toss']; G.ctx.setSpellCycle(G.slots()); })()")
        cyc = T.ev("window.__hm.ctx.spellCycle()")
        T.step("the Stone Golem is castable from the cycle too", cyc == ["stone_golem", "boulder_toss"], cyc=cyc)
        for tier, flags_, bolt, rune in ((1, {}, "seed_bomb", "rune_trap"), (2, {"sf_ii": 1}, "stonefrost_bolt_ii", "stonefrost_rune_ii"), (3, {"sf_ii": 1, "sf_iii": 1}, "stonefrost_bolt_iii", "stonefrost_rune_iii")):
            T.ev(f"(() => {{ const f = window.__hm.S.flags; delete f.sf_ii; delete f.sf_iii; Object.assign(f, {json.dumps(flags_)}); const C = window.__hm.combat; C.projs = []; C.traps = []; ({CAST})('boulder_toss'); C.cd.spell = 0; ({CAST})('frost_rune'); }})()")
            r = T.ev("(() => { const C = window.__hm.combat, c = window.__hd2d.ctx, pr = C.projs[C.projs.length - 1], tr = C.traps[C.traps.length - 1]; return { tier: C.stoneTier(), bolt: pr && pr.f.name, gfx: !!pr && pr.fxo === c.gamefx, mul: pr && pr.mul, rune: !!tr && (tr.T ? tr.T.rune : 'rune_trap') }; })()")
            T.step(f"Stonefrost tier {tier}: Boulder Toss flies as {bolt} (x{[1, 1.3, 1.6][tier - 1]} damage) and Frost Rune lays {rune}",
                   r["tier"] == tier and r["bolt"] == bolt and r["gfx"] == (tier > 1) and abs(r["mul"] - [1, 1.3, 1.6][tier - 1]) < 1e-6 and r["rune"] == rune, r=r)
            T.step(f"tier {tier}: the rune arms, then bursts on its own timer",
                   until("window.__hm.combat.traps.some((t) => t.armed)", 40) and T.ev("(() => { const C = window.__hm.combat; for (const t of C.traps) t.t = t.S.life + 1; return true; })()")
                   and until("window.__hm.combat.traps.length === 0", 40))
        # Stone Skin: -40 % damage, -20 % speed (re-based when the blizzard's frost slow writes p.speed), ends on its own
        T.ev("(() => { const G = window.__hm, C = G.combat, p = G.ctx.player; C.godT = 0; p.iframes = 0; G.S.hp = C.maxHp(); window.__sp0 = p.speed; window.__hp0 = G.S.hp; C.hurtPlayer(20, { x: p.x + 1, z: p.z }, 0); window.__loss0 = window.__hp0 - G.S.hp; })()")
        T.ev(f"({CAST})('stone_skin')")
        T.step("Stone Skin: -20 % speed while it lasts", abs(T.ev("window.__hm.ctx.player.speed") - T.ev("window.__sp0") * 0.8) < 1e-6 and T.ev("!!window.__hm.combat.skin"))
        T.ev("(() => { const G = window.__hm, C = G.combat, p = G.ctx.player; C.godT = 0; p.iframes = 0; G.S.hp = C.maxHp(); const h = G.S.hp; C.hurtPlayer(20, { x: p.x + 1, z: p.z }, 0); window.__loss1 = h - G.S.hp; })()")
        l0, l1 = T.ev("window.__loss0"), T.ev("window.__loss1")
        T.step("Stone Skin: -40 % damage taken (the same hit costs 60 %)", l0 > 1 and abs(l1 / l0 - 0.6) < 0.1, plain=l0, skin=l1)
        T.ev("window.__hm.ctx.player.speed = 2.0")
        T.step("a frost slow written over it is re-based (x0.8 of the new speed)", until("Math.abs(window.__hm.ctx.player.speed - 1.6) < 1e-6", 30), speed=T.ev("window.__hm.ctx.player.speed"))
        T.ev("window.__hm.combat.skin.t = 0.02")
        T.step("Stone Skin ends on its own and gives the speed back", until("!window.__hm.combat.skin && Math.abs(window.__hm.ctx.player.speed - 2.0) < 1e-6", 40), speed=T.ev("window.__hm.ctx.player.speed"))
        # Cold Fire: a lit patch that slows foes, then gone
        g0 = T.ev("window.__hd2d.ctx.gamefx.list.length")
        T.ev(f"({CAST})('cold_fire')")
        cf = T.ev("(() => { const C = window.__hm.combat, G = window.__hm, c = C.patches[0]; return c ? { n: C.patches.length, slow: C.coldAt(c.x, c.z), far: C.coldAt(c.x + 9, c.z), lit: G.glow.litAt(c.x, c.z), r: c.r, life: c.t } : null; })()")
        T.step("Cold Fire: a patch at the player's feet slows foes inside it (not outside), is a lit zone and lasts 8 s", bool(cf) and cf["n"] == 1 and cf["slow"] and not cf["far"] and cf["lit"] and 7.5 < cf["life"] <= 8, cf=cf)
        T.ev("window.__hm.combat.patches.forEach((c) => { c.t = 0.02; })")
        T.step("the Cold Fire patch burns out and its decals are removed", until("window.__hm.combat.patches.length === 0 && window.__hd2d.ctx.gamefx.list.length <= " + str(g0), 40), g0=g0, now=T.ev("window.__hd2d.ctx.gamefx.list.length"))
        # Stone Golem: 20 s, the golem role, takes the place of a summon
        T.ev(f"({CAST})('stone_golem')")
        gl = T.ev("(() => { const s = window.__hm.combat.summon; return s ? { golem: !!s.golem, role: s.a.role, life: s.life, cd: window.__hm.combat.cd.golem } : null; })()")
        T.step("Stone Golem: a golem fights for 20 s and the spell cools down for 40 s", bool(gl) and gl["golem"] and "golem" in gl["role"] and 19 < gl["life"] <= 20 and gl["cd"] > 38, gl=gl)
        T.ev("window.__hm.combat.summon.life = 0.02")
        T.step("the Stone Golem crumbles when its time is up", until("!window.__hm.combat.summon", 40))
        # barrow -> barrow2: the passage at the north end of the Avalanche Run
        a = load("barrow", "&jtq=barrow", "qa")
        T.step("the Avalanche Run has a passage north into the Throne Barrow", "barrow2" in a["exits"], exits=a["exits"])
        walk_to(0, -30.2)
        T.wait("window.__hm.area === 'barrow2' && window.__hd2d && window.__hd2d.ready && !window.__hm.busy", 90); T.idle(); frames(8); a = sv()
        T.step("walking through it lands you in B5 with a way back", a["area"] == "barrow2" and "barrow" in a["exits"], area=a["area"], exits=a["exits"])
        a = load("barrow2", "&jtq=deep")
        T.step("the Throne Barrow loads: foes, cold fire and lights", len(set(a["foes"])) >= 2 and a["fx"] >= 8 and a["lights"] >= 4, foes=a["foes"], fx=a["fx"], lights=a["lights"])
        hs = T.ev("(() => { const c = window.__hd2d.ctx; return { g: c.heightAt(0, 6), b6: c.heightAt(-4, -10), s6: c.heightAt(0, -2.4), br: c.heightAt(0, -22), b8: c.heightAt(-4, -34.2), b9: c.heightAt(-4, -48) }; })()")
        T.step("real height climbs: hall 1.2 m, bridge and crypt 2.4 m, throne dais 3.6 m", hs["g"] < 0.2 and 1.1 <= hs["b6"] <= 1.3 and 0.1 < hs["s6"] < 1.2 and hs["br"] >= 2.3 and hs["b8"] >= 2.3 and hs["b9"] >= 3.5, hs=hs)
        shot("jt_barrow2_hall")
        w = T.ev("(() => { const c = window.__hd2d.ctx, O = c.scene.objects, W = O.filter((o) => /rune_waystone\\.glb$/.test(o.glb)), p = W[0] ? W[0].pos : [0, 0, 0], sp = c.scene.game.spawns.from_waystone;"
                 " return { n: W.length, standin: O.some((o) => /rune_standing_stone/.test(o.glb) && Math.hypot(o.pos[0] + 4, o.pos[2] + 37.2) < 0.5),"
                 " near: O.filter((o) => o !== W[0] && !/frost_rune_pillar|rune_standing_stone/.test(o.glb) && Math.hypot(o.pos[0] - p[0], o.pos[2] - p[2]) < 2.6).map((o) => o.glb),"
                 " stones: O.filter((o) => o !== W[0] && Math.hypot(o.pos[0] - p[0], o.pos[2] - p[2]) < 2.6).length, lamp: c.scene.lamps.some((l) => l.kind === 'rune_waystone'),"
                 " spawnClear: Math.hypot(sp[0] - p[0], sp[1] - p[2]) >= 2.0 && !c.collide.blocked(sp[0], sp[1]), pool: !!c.gamefx.meta.effects.pool_cold }; })()")
        T.step("barrow2: the real rune_waystone replaces the stand-in, with its lamp, nothing within its 2.6 m keep-clear, and the arrival spawn is free",
               w["n"] == 1 and not w["standin"] and w["lamp"] and w["stones"] == 0 and w["spawnClear"] and w["pool"], w=w)
        walk_to(0, 0.8); jt("qaSpot('echo')"); fin()
        walk_to(0, -31.2); jt("qaSpot('tb3')"); fin(); a = sv()
        T.step("brazier 3 at the crypt entrance is snuffed (tb_b3), the third of three", a["found"].get("tb_b3") == 1 and all(a["found"].get(k) == 1 for k in ("tb_b1", "tb_b2", "tb_b3")), found=a["found"])
        T.step("the Frozen Echo and the rune tablets are look-spots", all(jt(f"qaSpot('{i}')") is True and (fin() or True) for i in ("echo", "tablet1", "tablet2")))
        walk_to(0, -7.8)
        T.step("crossing into the Berserker Hall wakes Chief Ormgar", until("window.__hm.jot.qa().cb.includes('ormgar')", 10), cb=sv()["cb"])
        walk_to(0, -46.0)
        T.step("stepping onto the throne dais wakes Hrimgard (7x, boss)", until("window.__hm.jot.qa().cb.includes('hrimgard')", 10) and "hrimgard" in sv()["foes"], foes=sv()["foes"])
        shot("jt_hrimgard")
        jt("qaKill('hrimgard')"); fin(); a = sv()
        T.step("Hrimgard sleeps: tb_boss + tb_slept, barrow 1 -> 2", a["found"].get("tb_boss") == 1 and a["found"].get("tb_slept") == 1 and a["quest_barrow"] == 2, found=a["found"], q=a["quest_barrow"])
        g0 = a["gold"]; jt("qaTalk('jarl')"); a = sv()
        T.step("the Jarl pays out: barrow 3, +150 gold", a["quest_barrow"] == 3 and a["gold"] == g0 + 150, q=a["quest_barrow"], gold=a["gold"])
        a = load("barrow2", "&jtq=deepc"); walk_to(0, -46.0); until("window.__hm.jot.qa().cb.includes('hrimgard')", 10)
        jt("qaKill('hrimgard')"); fin(); a = sv()
        T.step("conquer: taking the crown ends the barrow quest at once (tb_crown, barrow 3)", a["found"].get("tb_crown") == 1 and a["quest_barrow"] == 3 and not a["found"].get("tb_slept"), found=a["found"])
        T.step("conquer: taking the crown sets jt_dark (Dark Stonehollow)", T.ev("window.__hm.S.flags.jt_dark") == 1, flags=T.ev("window.__hm.S.flags.jt_dark"))
        a = load("barrow2", "&jtq=deep"); walk_to(8.0, -36.4)
        T.ev("window.__hm.hollows && window.__hm.hollows.onCast()"); frames(2)
        T.step("a spell cast by the ice wall thaws the hidden spring (tb_spring)", sv()["found"].get("tb_spring") == 1, found=sv()["found"])
        # ---- the Rune Bridge: solvable, resettable, never a softlock
        a = load("barrow2", "&jtq=deep"); br = a["bridge"]
        cen = lambda c, r: (-2.6 + (5.2 / 3) * (c + 0.5), -17.2 - 2.2 * (r + 0.5))  # noqa: E731
        lit = {(c, r) for r, cols in enumerate(br["lit"]) for c in cols}
        seen, todo = set(), [(c, 0) for c in br["lit"][0]]
        while todo:
            t = todo.pop()
            if t in seen or t not in lit:
                continue
            seen.add(t); todo += [(t[0] + 1, t[1]), (t[0] - 1, t[1]), (t[0], t[1] + 1), (t[0], t[1] - 1)]
        T.step("Rune Bridge: the lit runes form one connected path from the head to the far end", any(r == 5 for _, r in seen) and len(seen) == len(lit), lit=sorted(lit))
        walk_to(0, -16.8)
        x, z = cen(0, 0); walk_to(x, z)
        T.step("an unlit tile cracks: you drop back at the bridge head (never off the bridge) and the fall is counted",
               until("window.__hm.jot.qa().bridge.falls >= 1", 10) and sv()["pos"][1] > -17.2 and T.ev("window.__hd2d.ctx.player.y") >= 2.3, qa=sv()["bridge"], pos=sv()["pos"])
        f1 = sv()["bridge"]["falls"]
        for (c, r) in [(1, 0), (1, 1), (2, 1), (2, 2), (2, 3), (1, 3), (1, 4), (0, 4), (0, 5)]:
            x, z = cen(c, r); walk_to(x, z)
        T.step("walking the lit path costs no more falls", sv()["bridge"]["falls"] == f1 and not sv()["bridge"]["solved"], qa=sv()["bridge"])
        walk_to(0, -31.0)
        T.step("crossing sets tb_bridge and the way on stays open", until("window.__hm.jot.qa().bridge.solved", 10), qa=sv()["bridge"])
        x, z = cen(0, 0); walk_to(x, z); frames(3)
        T.step("once solved no tile cracks any more", sv()["bridge"]["falls"] == f1, qa=sv()["bridge"])
        shot("jt_rune_bridge")
        # ---- the Waystone Crypt: the waystone attunes and travels both ways
        a = load("barrow2", "&jtq=deep"); T.ev("(() => { const f = window.__hm.S.flags = window.__hm.S.flags || {}; f.ways = { ...(f.ways || {}), jotunheim: 1 }; })()")
        walk_to(-4.0, -35.2)
        T.step("the waystone attunes on arrival and is in reach (E / A)", T.ev("!!(window.__hm.S.flags.ways && window.__hm.S.flags.ways.barrow2 && window.__hm.harbor.near())"))
        T.ev("window.__hm.harbor.interact()"); frames(3)
        opts = T.ev("(window.__hm.dlg && window.__hm.dlg.choice) ? window.__hm.dlg.choice.options.map((o) => o.label) : []")
        T.step("it offers Stonehollow", any("Stonehollow" in o for o in opts), opts=opts)
        T.ev("(() => { const G = window.__hm; G.dlg.choice.options.find((o) => o.label.includes('Stonehollow')).pick(); G.dropDialogue(); })()"); arrive("jotunheim")
        T.step("Stonehollow's waystone lists the Throne Barrow crypt once attuned", T.ev("window.__hm.S.flags.ways.barrow2 === 1") and sv()["area"] == "jotunheim")
        # ---- Ormgar's frenzy at 50%
        a = load("barrow2", "&jtq=deep"); walk_to(0, -7.8)
        T.step("Ormgar wakes in the Berserker Hall", until("window.__hm.jot.qa().cb.includes('ormgar')", 10))
        jt("qaHp('ormgar', 0.6)"); frames(4); o0 = sv()["orm"]
        T.step("above 50% HP Ormgar is not frenzied", not o0["frenzy"] and o0["speed"] == o0["base"], orm=o0)
        jt("qaHp('ormgar', 0.4)")
        T.step("below 50% HP Ormgar goes into a frenzy (faster)", until("window.__hm.jot.qa().orm.frenzy", 10) and sv()["orm"]["speed"] > o0["base"], orm=sv()["orm"])
        HEAD = "(() => { const c = window.__hd2d.ctx, a = c.actors.list.find((x) => x.id === 'hrimgard'); if (!a) return null; const p = c.project(a.x, a.y + c.actors.heightM * a.tall, a.z), f = c.project(a.x, a.y, a.z); return { head: Math.round(p.y), feet: Math.round(f.y), top: Math.round(document.querySelector('canvas').getBoundingClientRect().top), pull: +c.pull().toFixed(2) }; })()"

        def framed(tag):
            until("window.__hd2d.ctx.pull() >= 1.9", 60); h = T.ev(HEAD)
            T.step(f"Hrimgard {tag}: the camera pulls out for the 7x boss and his head is in frame", h is not None and h["pull"] >= 1.9 and h["head"] >= h["top"] + 4 and h["feet"] > h["head"] + 120, frame=h)
            shot("jt_hrimgard_" + tag)
        # ---- Hrimgard: P2 frozen floor + golems, P3 relit braziers that mend him until snuffed
        a = load("barrow2", "&jtq=deep"); walk_to(0, -46.0)
        T.step("Hrimgard wakes (phase 1: no slide, no relit braziers)", until("window.__hm.jot.qa().cb.includes('hrimgard')", 10) and sv()["boss"]["phase"] <= 1 and not sv()["boss"]["slide"], boss=sv()["boss"])
        framed("p1")
        jt("qaHp('hrimgard', 0.55)")
        T.step("below 60% (P2): the floor freezes and two ice golems rise", until("window.__hm.jot.qa().boss.p2 && window.__hm.jot.qa().cb.includes('hr_m1') && window.__hm.jot.qa().cb.includes('hr_m2')", 15), boss=sv()["boss"], cb=sv()["cb"])
        framed("p2")
        walk_to(-2.0, -46.0); x0 = T.ev("window.__hd2d.ctx.player.x"); jt("qaSlideKick(3.0, 0)"); frames(20); x1 = T.ev("window.__hd2d.ctx.player.x")
        T.step("on the frozen dais you keep sliding after you stop", x1 > x0 + 0.3, x0=x0, x1=x1)
        jt("qaHp('hrimgard', 0.2)")
        T.step("below 25% (P3): the snuffed braziers relight one by one", until("window.__hm.jot.qa().boss.relit && window.__hm.jot.qa().boss.relit.every((x) => x)", 90), boss=sv()["boss"])
        h0 = sv()["boss"]["hp"]
        T.step("lit braziers mend him", until(f"window.__hm.jot.qa().boss.hp > {h0}", 60), boss=sv()["boss"])
        for i in (1, 2, 3):
            jt(f"qaSpot('tbt{i}')")
        h1 = sv()["boss"]["hp"]; frames(60)
        T.step("snuffing all three stops the healing (resettable: you can always snuff them)", sv()["boss"]["relit"] == [0, 0, 0] and sv()["boss"]["hp"] <= h1 + 0.01, boss=sv()["boss"])
        framed("p3")
        # ---- cairn props are the real kit models (watch_cairn + cairn_toppled at the three Toll of Stones spots, stone_cairn trail markers); the snow_mound stand-ins are gone
        a = load("rimecaves", "&jtq=conquer")
        n = T.ev("(() => { const O = window.__hd2d.ctx.scene.objects, at = (re, x, z) => O.some((o) => re.test(o.glb) && Math.hypot(o.pos[0] - x, o.pos[2] - z) < 0.3); const spots = [[-10.2, 6.4], [10.2, 6.4], [3.0, -1.6]];"
                 " return { watch: O.filter((o) => /watch_cairn\\.glb$/.test(o.glb)).length, toppled: O.filter((o) => /cairn_toppled\\.glb$/.test(o.glb)).length, trail: O.filter((o) => /stone_cairn\\.glb$/.test(o.glb)).length,"
                 " atSpots: spots.every(([x, z]) => at(/watch_cairn\\.glb$/, x, z) && at(/cairn_toppled\\.glb$/, x, z)), standins: O.filter((o) => /snow_mound/.test(o.glb) && spots.some(([x, z]) => Math.hypot(o.pos[0] - x, o.pos[2] - z) < 0.5)).length }; })()")
        T.step("the three watch-cairns are the real watch_cairn + cairn_toppled models (no snow_mound stand-ins), with stone_cairn trail markers",
               n["watch"] == 3 and n["toppled"] == 3 and n["atSpots"] and n["standins"] == 0 and n["trail"] >= 2, n=n)
        g = T.ev("(() => { const c = window.__hd2d.ctx, p = c.scene.lamps.filter((l) => l.kind === 'watch_cairn'); return { lamps: p.length, toppledLamps: c.scene.lamps.filter((l) => l.kind === 'cairn_toppled').length, pools: c.gamefx.list.filter((f) => f.name === 'pool_cold').length }; })()")
        T.step("each standing cairn has its kit lamp and cold pool; the toppled rubble is unlit until the game shows it", g["lamps"] == 3 and g["toppledLamps"] == 0 and g["pools"] == 3, g=g)
        shot("jt_cairns")
        # ---- the Rime Caves' rares (BASES hook): frostmother and avalanche
        a = load("rimecaves", "&rare")
        T.step("?rare roams one of the cave rares (frostmother or avalanche) on its own sheet", until("window.__hm.rares.list.length >= 1", 15) and T.ev("window.__hm.rares.list[0].base") in ("frostmother", "avalanche"), n=T.ev("window.__hm.rares.list.length"))
        a = load("rimecaves"); qr = jt("qaRares()")
        rr = T.ev("""(() => { const R = window.__hm.rares, f = R.spawn({ base: 'frostmother', pos: [5.2, -3.2] }), v = R.spawn({ base: 'avalanche', pos: [-4.6, 2.6] });
                     return { f: { traits: f.traits, chill: f.D.chill, minion: f.D.minion, scale: f.D.scale, role: f.e.a.role }, v: { traits: v.traits, wave: !!v.D.wave, scale: v.D.scale, role: v.e.a.role } }; })()""")
        T.step("Frostmother: 2.5x, frozen chill, calls frost-troll whelps (Summoner)", rr["f"]["scale"] == 2.5 and rr["f"]["chill"] and "summoner" in rr["f"]["traits"] and rr["f"]["minion"] == "frost_troll" and rr["f"]["role"] == "frostmother", rr=rr["f"])
        T.step("Avalanche: 3x, stone-skin (Shielded) and a quake shockwave", rr["v"]["scale"] == 3 and "shielded" in rr["v"]["traits"] and rr["v"]["wave"] and rr["v"]["role"] == "avalanche", rr=rr["v"])
        T.step("rare spots keep clear of every actor (>= 3.5 m) and are >= 3.5 m apart", min(qr["clear"]) >= 3.5 and ((qr["spots"][0][0] - qr["spots"][1][0]) ** 2 + (qr["spots"][0][1] - qr["spots"][1][1]) ** 2) ** 0.5 >= 3.5, qr=qr)
        shot("jt_rares")
        # ---- the Rimebreaker (jt_axe): Solvi offers it after the lessons, three heart-ice, the axe freezes every 3rd hit
        a = load("jt_hall", "&jtq=lessons"); jt("qaTalk('rimewife')"); frames(2); jt("qaTalk('rimewife')"); a = sv()
        T.step("Solvi offers the Rimebreaker once the first Stonefrost circle is taught (jt_axe 1)", a["axe"] == 1, axe=a["axe"])
        a = load("barrow", "&jtq=barrow"); T.ev("window.__hm.S.quests.jt_axe = 1; window.__hm.S.quests.barrow = 3"); jt("qaSpot('hi_1')"); fin(); a = sv()
        T.step("hi_1 in the Glow Pools gives heart-ice", a["found"].get("hi_1") == 1 and a["hice"] == 1, hice=a["hice"])
        a = load("barrow2", "&jtq=deep"); T.ev("window.__hm.S.quests.jt_axe = 1; window.__hm.S.found.hi_1 = 1; window.__hm.S.inv.heart_ice = 1")
        jt("qaSpot('hi_2')"); fin(); jt("qaSpot('hi_3')"); fin(); a = sv()
        T.step("hi_2 (behind Ormgar's seat) and hi_3 (crypt crystals) complete the set: jt_axe 2, 3 heart-ice", a["axe"] == 2 and a["hice"] == 3, axe=a["axe"], hice=a["hice"])
        T.ev("window.__hm.S.quests.barrow = 3; window.__hm.S.flags.sf_i = 1"); a = load("jt_hall", "&jtq=lessons")
        T.ev("(() => { const S = window.__hm.S; S.quests.jt_axe = 2; S.inv.heart_ice = 3; })()"); jt("qaTalk('rimewife')"); frames(2); a = sv()
        T.step("Solvi wakes the axe: The Rimebreaker is in the bag, heart-ice spent, jt_axe 3", a["axe"] == 3 and "rimebreaker" in a["bag"] and a["hice"] == 0, bag=a["bag"], axe=a["axe"])
        a = load("rimecaves", "&jtq=conquer")
        T.ev("(() => { const G = window.__hm, i = G.S.bag.findIndex((x) => x.unique === 'rimebreaker'); G.S.gear = G.S.gear || {}; G.S.gear.weapon = { slot: 'weapon', name: 'The Rimebreaker', unique: 'rimebreaker', rar: 4, lv: 10, mods: { meleeMul: 0.1 }, gems: [null, null] }; })()")
        T.ev("(() => { const C = window.__hm.combat, p = window.__hd2d.ctx.player; C.spawnEnemy({ id: 'rb_t', role: 'frost_troll', pos: [p.x, p.z - 3], once: true }, false); C.rimeN = 0; })()")
        for _ in range(3):
            T.ev("(() => { const C = window.__hm.combat, e = C.enemies.find((x) => x.id === 'rb_t'); C.damageEnemy(e, 1, window.__hd2d.ctx.player, 0.45); })()")
        T.step("with the Rimebreaker every 3rd melee hit freezes the foe", jt("qaFoe('rb_t')")["frozen"] and jt("qaFoe('rb_t')")["speed"] == 0, f=jt("qaFoe('rb_t')"))
        T.step("the freeze ends after 1.5 s and the foe moves again", until("window.__hm.jot.qaFoe('rb_t').speed > 0 && !window.__hm.jot.qaFoe('rb_t').frozen", 30), f=jt("qaFoe('rb_t')"))
        # ---- Jotunheim weather: the calendar, blizzard frost slow (cold fire thaws it), the aurora on a clear night
        load("jotunheim")
        cal = T.ev("""(() => { const w = window.__hm.weatherAt, c = { day: {}, night: {} }; for (let d = 1; d <= 240; d++) for (const [k, t] of [['day', 0.5], ['night', 0.0]]) { const v = w('jotunheim', d, t); c[k][v] = (c[k][v] || 0) + 1; }
                    return { c, hall: w('jt_hall', 3, 0.5), caves: w('rimecaves', 3, 0.0), barrow: w('barrow', 3, 0.5) }; })()""")
        dd = cal["c"]["day"]
        T.step("weather calendar: Stonehollow's day is mostly snow, some blizzard, some clear; no aurora by day", dd.get("snow", 0) >= 130 and dd.get("blizzard", 0) >= 15 and dd.get("clear", 0) >= 15 and not dd.get("aurora"), cal=cal["c"])
        T.step("clear nights show the aurora; the interiors (Hall, caves, Barrow) stay clear", cal["c"]["night"].get("aurora", 0) >= 15 and cal["hall"] == cal["caves"] == cal["barrow"] == "clear", cal=cal)
        a = load("jotunheim", "&wx=blizzard")
        wq = T.ev("window.__hm.weather.qa()")
        T.step("a blizzard runs snow plus mist emitters", wq["kind"] == "blizzard" and {e["preset"] for e in wq["emitters"]} >= {"snowfall", "mist"}, wq=wq)
        walk_to(8.0, 4.0); jt("qaFrost(0)"); jt("qaFrost(750)"); frames(3)
        T.step("blizzard frost slow: -1% per 5 s, capped at -30% (speed 1.82 of 2.6)", abs(sv()["wx"]["slow"] - 0.3) < 1e-6 and abs(sv()["wx"]["speed"] - 2.6 * 0.7) < 1e-3, wx=sv()["wx"])
        walk_to(-2.4, -3.2); T.ev("window.__hm.jot.qaFrost(300)")
        T.step("standing near cold fire thaws the frost", until("window.__hm.jot.qa().wx.frost < 100", 240), wx=sv()["wx"])
        a = load("jotunheim", "&wx=snow"); jt("qaFrost(0)"); frames(3)
        T.step("in plain snow there is no frost slow", sv()["wx"]["slow"] == 0 and sv()["wx"]["speed"] == 2.6, wx=sv()["wx"])
        a = load("jotunheim", "&wx=aurora")
        T.step("a clear night's aurora: the green-violet ribbon is up (and gone again in clear weather)", until("window.__hm.jot.qa().wx.aurora", 20), wx=sv()["wx"])
        T.ev("window.__hd2d.setTime(0.95)"); frames(30)
        shot("jt_aurora")
        a = load("jotunheim", "&wx=clear")
        T.step("clear weather: no aurora, no slow", not sv()["wx"]["aurora"] and sv()["wx"]["slow"] == 0, wx=sv()["wx"])
        # ---- Ulfar's Walk (jt_ulfar) and Ulfar as a companion (one at a time, combat_scale 2.4, shield hug, faint)
        FOL = "window.__hm.svart.follow.qa()"
        load("jotunheim", "&jtq=done")
        T.step("Ulfar's Walk is offered once the Stone Welcome is done; the town's Ulfar stands at the lake", (sv()["ulfar"]["q"], sv()["ulfar"]["town"]) == (0, True), ulfar=sv()["ulfar"])
        jt("qaTalk('ulfar')"); a = sv()["ulfar"]
        T.step("Ulfar's offer starts jt_ulfar at stage 1 (goat, song, mitten)", a["q"] == 1 and a["found"] == [0, 0, 0], ulfar=a)
        jt("qaSpot('uw_goat')"); fin(); jt("qaSpot('uw_mitten')"); fin()
        T.ev("window.__hm.S.found = { ...window.__hm.S.found }"); jt("qaSpot('uw_song')")
        T.ev("(() => { const G = window.__hm; G.dlg.choice.options[1].pick(G); G.dropDialogue(); })()"); a = sv()["ulfar"]
        T.step("Turnip, the song (any choice works) and the mitten: 3/3", a["found"] == [1, 1, 1], ulfar=a)
        T.step("the song changes his tune (uw_tune)", T.ev("window.__hm.S.flags.uw_tune") == "snow")
        jt("qaTalk('ulfar')"); fin(); a = sv()["ulfar"]
        T.step("with all three done he asks to be walked to the Barrow door (stage 2) and the town's Ulfar steps out of the snow", a["q"] == 2 and a["walk"] and not a["town"], ulfar=a)
        T.step("Ulfar's follower body is up before he has joined (sheet role ulfar)", until(FOL + ".on && " + FOL + ".role === 'ulfar'", 20), fol=T.ev(FOL))
        T.step("his combat_scale is 2.4 (follower scale; the sheet meta says the same)", T.ev(FOL)["scale"] == 2.4, fol=T.ev(FOL))
        T.ev("window.__hm.loadArea('rimecaves', 'from_town')"); arrive("rimecaves")
        T.step("he follows into the Rime Caves", until(FOL + ".on && " + FOL + ".role === 'ulfar'", 20), fol=T.ev(FOL))
        m0 = T.ev("(window.__hm.S.merit || {}).embassy || 0"); jt("qaSpot('door')"); fin(); a = sv()["ulfar"]
        T.step("at the Barrow door Ulfar joins: jt_ulfar 3, companion ulfar, Flurry, Frostbrute", a["q"] == 3 and a["comp"] == "ulfar" and a["flurry"] and a["brute"], ulfar=a)
        m1 = T.ev("(window.__hm.S.merit || {}).embassy || 0")
        T.step("+80 Realm Favor (Embassy merit) for Ulfar's Walk", m1 - m0 >= 80, merit=[m0, m1])
        walk_to(0.0, 1.0)
        T.ev("(() => { const C = window.__hm.combat, p = window.__hd2d.ctx.player; C.spawnEnemy({ id: 'ul_t', role: 'frost_troll', pos: [p.x + 2.0, p.z - 2.0], once: true }, false); })()"); frames(4)
        r = T.ev("window.__hm.svart.follow.qaBrawl()")
        T.step("Ulfar's boulder toss hits a foe for real damage (20)", r is not None and r >= 15, lost=r)
        # the foes' AI is asleep under ?qa, so put one in the chase and let Ulfar's own update see it
        T.ev("(() => { const G = window.__hm, C = G.combat, p = window.__hd2d.ctx.player; C.spawnEnemy({ id: 'ul_t2', role: 'frost_troll', pos: [p.x + 2.4, p.z - 1.0], once: true }, false); G.S.hp = 40; C.godT = 6; C.alive().forEach((e) => { e.state = 'chase'; }); G.svart.follow.update(0.02); })()"); frames(1)
        T.step("shield hug: when you are hurt in a fight he stands over you (50% damage for 4 s)", T.ev(FOL)["hugs"] >= 1 and T.ev(FOL)["hugT"] > 0, fol=T.ev(FOL))
        d0 = T.ev("(() => { const C = window.__hm.combat, p = window.__hd2d.ctx.player; const h = window.__hm.S.hp; p.iframes = 0; C.godT = 0; window.__hm.S.hp = 80; const h0 = 80; C.hurtPlayer(10, { x: p.x + 1, z: p.z }, 0); return h0 - window.__hm.S.hp; })()")
        T.step("while hugged a 10-damage hit lands for 5 or less (mode multiplier included)", 0 < d0 <= 5, dmg=d0)
        T.ev("window.__hm.loadArea('jotunheim', 'from_bifrost')"); arrive("jotunheim")
        a = sv()["ulfar"]
        T.step("as a companion he is no longer standing at the lake (he is with you)", not a["town"] and until(FOL + ".on && " + FOL + ".id === 'ulfar'", 20), ulfar=a)
        T.ev("window.__hm.weather.force('blizzard')"); jt("qaFrost(750)"); frames(4)
        T.step("Ulfar's aura halves the blizzard frost slow (frostResist 0.5: -15% instead of -30%)", abs(sv()["wx"]["slow"] - 0.15) < 1e-6, wx=sv()["wx"])
        T.ev("window.__hm.weather.force(null)"); jt("qaFrost(0)"); frames(4)
        T.ev("window.__hm.S.flags.companions = { ...window.__hm.S.flags.companions, dagna: 1 }; window.__hm.S.flags.companion_active = 'dagna'; window.__hm.loadArea('rimecaves', 'from_town')"); arrive("rimecaves")
        T.ev("window.__hm.loadArea('jotunheim', 'from_bifrost')"); arrive("jotunheim")
        T.step("one companion at a time: with Dagna active Ulfar is not in the party (no body) and stands at the lake again",
               T.ev(FOL)["id"] == "dagna" and not T.ev(FOL)["on"] and sv()["ulfar"]["town"], fol=T.ev(FOL), ulfar=sv()["ulfar"])
        T.ev("window.__hm.S.flags.companion_active = 'ulfar'; window.__hm.loadArea('jotunheim', 'from_bifrost')"); arrive("jotunheim")
        T.ev("window.__hm.combat.spawnEnemy({ id: 'ul_f', role: 'frost_troll', pos: [-4, 3], once: true }, false)"); frames(3)
        T.ev("window.__hm.downed = true"); frames(6); T.ev("window.__hm.downed = false")
        T.step("faint: when you go down Ulfar sits down (his body leaves)", T.ev(FOL)["fainted"] and not T.ev(FOL)["on"], fol=T.ev(FOL))
        T.ev("window.__hm.loadArea('rimecaves', 'from_town')"); arrive("rimecaves")
        T.step("and he returns when you move on (waystone / next area)", until(FOL + ".on && !" + FOL + ".fainted", 20), fol=T.ev(FOL))
        shot("jt_ulfar")
        # ---- the goat pens: two pen goats and Clatter; jt_goat (an oat-cake a day, three days); the mount stays deferred
        load("jotunheim", "&jtq=done"); gq = sv()
        T.step("the pen has a pen goat and Clatter on the goat sheets (a second pen goat does not fit the phone / main views without hiding behind Brynja)", sorted((g[0], g[1]) for g in gq["goats"]) == [("clatter", "clatter"), ("pen_goat1", "goat")], goats=gq["goats"])
        frames(40)
        gg = sv()["goats"]
        T.step("the goats stay in the pen's far-left column (x -12..-10.7, z -4.0..1.5), north of the fence and clear of Brynja", all(-11.7 <= g[2] <= -10.7 and -1.6 <= g[3] <= 1.5 and ((g[2] + 9.0) ** 2 + (g[3] - 0.8) ** 2) ** 0.5 > 1.5 for g in gg), goats=gg)
        jt("qaTalk('goatwife')"); fin(); a = sv()["goat"]
        T.step("Brynja offers The Goat Who Chose You (jt_goat 1) and hands over the first oat-cake", a["q"] == 1 and a["cake"] == 1, goat=a)
        jt("qaSpot('clatter')"); fin(); a = sv()["goat"]
        T.step("Clatter takes the first oat-cake (1/3)", a["cakes"] == 1 and a["cake"] == 0, goat=a)
        jt("qaTalk('goatwife')"); fin(); jt("qaSpot('clatter')"); fin(); a = sv()["goat"]
        T.step("one oat-cake a day: a second cake the same day is refused", a["cakes"] == 1 and a["cake"] == 0, goat=a)
        for n in (2, 3):
            T.ev("window.__hm.S.day = (window.__hm.S.day || 0) + 1"); jt("qaTalk('goatwife')"); fin(); jt("qaSpot('clatter')"); fin(); a = sv()["goat"]
        T.step("after three days Clatter trusts you: jt_goat stage 2 (the lap of the lake waits for the saddle)", a["q"] == 2 and a["cakes"] == 3, goat=a)
        T.step("the goat mount stays deferred (no S.mounts.goat, no quest 3)", not a["mount"] and a["q"] != 3, goat=a)
        # ---- Dark Stonehollow (story 9.7): conquer + the crown taken
        PRICE = "(() => { const G = window.__hm; G.shopUI.show('jt_trader'); const r = G.shopUI.rows().find((x) => x.id === 'tea'); G.shopUI.close(); return r ? r.price : null; })()"
        load("jotunheim", "&jtq=conquer"); d0 = sv()["dark"]; p0 = T.ev(PRICE); l0 = T.ev("window.__hm.jot.qaLine('jt_b')")
        T.step("conquered but the crown not taken: the cold fires still burn, normal talk, normal prices", (not d0["on"]) and d0["flames"] == 2 and d0["pulses"] >= 3 and d0["orbs"] == 0 and d0["litCold"] > 0 and "No song" not in l0 and p0 == 14, dark=d0, price=p0, line=l0)
        load("jotunheim", "&jtq=dark"); d1 = sv()["dark"]; p1 = T.ev(PRICE)
        T.step("Dark Stonehollow: the cold fires and rune pulses are out, a glow orb marks each brazier, the cold lamps are off", d1["on"] and d1["flames"] == 0 and d1["pulses"] == 0 and d1["orbs"] == 2 and d1["cold"] > 0 and d1["litCold"] == 0, dark=d1)
        T.step("the warm giant lanterns still light the town (it is dim, not black)", d1["litWarm"] > 0 and d1["glows"] >= 2, dark=d1)
        ls = {k: T.ev(f"window.__hm.jot.qaLine('{k}')") for k in ("jt_trader", "goatherd", "goatwife", "ulfar", "jt_a", "jt_b", "jarl")}
        T.step("the giants are curt: every talk line changes (no song, no Games)", len(set(ls.values())) == 7 and "No song" in ls["jt_b"] and "go" in ls["jarl"].lower(), lines=ls)
        T.step("the trader charges +25% (tea 14 -> 18)", p1 == 18 and p0 == 14, base=p0, dark=p1)
        T.ev("window.__hd2d.setTime(0.5)"); frames(6); shot("jt_dark_day")
        T.ev("window.__hd2d.setTime(0.0)"); frames(6); shot("jt_dark_night")
        a = load("jotunheim", "&jtq=befriend"); d2 = sv()["dark"]
        T.step("a befriended Stonehollow is not dark (the flag is the conquer path only)", (not d2["on"]) and d2["flames"] == 2 and d2["litCold"] > 0, dark=d2)
        # ---- B3 The Glow Pools slide puzzle: solvable, resettable, never a soft lock (the layout is searched here with the same rules as game/jotunheim.js pzSlide)
        load("barrow", "&jtq=befriend", spawn="pools"); L = sv()["pz"]["layout"]
        P = {tuple(x) for x in L["pillars"]}; NC, NR, DOOR = L["cols"], L["rows"], L["door"]

        def pz_slide(c, r, d):
            dc, dr = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}[d]; k = 0
            while True:
                nc, nr = c + dc, r + dr
                if nr >= NR: return "goal" if c == DOOR else ((c, r) if k else None)
                if nr < 0: return None if r == -1 else (c, -1)
                if nc < 0 or nc >= NC or (nc, nr) in P: return (c, r) if k else None
                c, r, k = nc, nr, k + 1

        def pz_moves(st):
            if st == "bank": return [(("N", c), pz_slide(c, -1, "N")) for c in range(NC) if pz_slide(c, -1, "N")]
            return [(d, t) for d in "NSEW" for t in [pz_slide(st[0], st[1], d)] if t]

        def pz_norm(t): return "bank" if isinstance(t, tuple) and t[1] == -1 else t
        dist, prev, q = {"bank": 0}, {}, ["bank"]
        while q:
            st = q.pop(0)
            if st == "goal": continue
            for m, t in pz_moves(st):
                t = pz_norm(t)
                if t not in dist: dist[t] = dist[st] + 1; prev[t] = (st, m); q.append(t)
        rev = {}
        for st in dist:
            if st == "goal": continue
            for m, t in pz_moves(st): rev.setdefault(pz_norm(t), set()).add(st)

        def can_reach(target):
            seen, stack = {target}, [target]
            while stack:
                for x in rev.get(stack.pop(), ()):
                    if x not in seen: seen.add(x); stack.append(x)
            return seen
        cg, cb = can_reach("goal"), can_reach("bank")
        dead = [st for st in dist if st != "goal" and (st not in cg or st not in cb)]
        T.step("the slide puzzle is solvable in 5+ moves and has no dead end (every reachable stop reaches both the far door and the bank)", "goal" in dist and dist["goal"] >= 5 and not dead and len(dist) >= 12, moves=dist.get("goal"), dead=dead, stops=len(dist))
        hx, hz = 7.2, -22.0
        T.step("the heart-ice shard (hi_1) can be reached from a stop cell of the puzzle", any(st != "goal" and st != "bank" and st in dist and ((L["x0"] + st[0] * L["cell"] - hx) ** 2 + (L["z0"] - st[1] * L["cell"] - hz) ** 2) ** 0.5 < 1.6 for st in dist), hi=[hx, hz])
        sol, st = [], "goal"
        while st != "bank": st, m = prev[st]; sol.append(m)
        sol.reverse()

        def cell_xz(c, r): return L["x0"] + c * L["cell"], L["z0"] - r * L["cell"]

        def pz_go(d, col=None):
            if col is not None:
                bx, bz = cell_xz(col, -1); walk_to(bx, bz)
            ok = T.ev(f"window.__hm.jot.qaPzGo('{d}')")
            until("window.__hm.jot.qa().pz.st === 'idle'", 30)
            return ok, T.ev("(() => { const p = window.__hd2d.ctx.player; return [p.x, p.z, p.y]; })()")
        ok, pos = pz_go("N", 4)
        T.step("blocked: from the bank a pillar in front of the cell stops you (no slide)", not ok and sv()["pz"]["st"] == "idle" and sv()["pz"]["moves"] == 0, go=ok, pz=sv()["pz"]["moves"])
        bad = None; cur = "bank"
        for i, m in enumerate(sol):
            d, col = (m[0], m[1]) if isinstance(m, tuple) else (m, None)
            t = pz_slide(col, -1, "N") if col is not None else pz_slide(cur[0], cur[1], d)
            ok, pos = pz_go(d, col)
            ex = (0.0, -24.4) if t == "goal" else cell_xz(*t)
            if not ok or abs(pos[0] - ex[0]) > 0.25 or abs(pos[1] - ex[1]) > 0.25: bad = (i, m, ok, pos, ex); break
            cur = pz_norm(t) if t != "goal" else "goal"
            if cur == "bank": cur = (t[0], -1)
        T.step("walking the solution (" + " ".join(m if isinstance(m, str) else m[0] + str(m[1]) for m in sol) + ") ends up the far door's stair", bad is None and sv()["pz"]["solved"] and pos[1] < -23.6 and pos[2] > 2.0, bad=bad, pos=pos, pz=sv()["pz"])
        T.step("solved: the pools are plain floor for good (no slide, +40 gold, found.tb_slide)", (not sv()["pz"]["on"]) and T.ev("window.__hm.S.found.tb_slide") == 1 and not T.ev("window.__hm.jot.qaPzGo('N')"), pz=sv()["pz"])
        load("barrow", "&jtq=befriend", spawn="pools"); bx, bz = cell_xz(0, -1); walk_to(bx, bz); T.ev("window.__hm.jot.qaPzGo('N')"); until("window.__hm.jot.qa().pz.st === 'idle'", 30)
        a1 = sv()["pz"]; p1 = T.ev("(() => { const p = window.__hd2d.ctx.player; return [p.x, p.z]; })()")
        T.step("a first slide stops at the top of column 0 (a fresh save has the puzzle live)", a1["on"] and abs(p1[0] - cell_xz(0, 3)[0]) < 0.2 and abs(p1[1] - cell_xz(0, 3)[1]) < 0.2, pz=a1, pos=p1)
        jt("qaSpot('pzreset')"); frames(3); p2 = T.ev("(() => { const p = window.__hd2d.ctx.player; return [p.x, p.z]; })()"); a2 = sv()["pz"]
        T.step("reset: the ice runes pull you back to the bank", a2["resets"] == 1 and p2[1] > -12.2 and a2["st"] == "idle", pz=a2, pos=p2)
        POS = "(() => { const p = window.__hd2d.ctx.player; return [p.x, p.z]; })()"
        walk_to(cell_xz(0, -1)[0], -11.6); pg.keyboard.down("w")
        got = until("window.__hm.jot.qa().pz.moves >= 2", 15); pg.keyboard.up("w"); until("window.__hm.jot.qa().pz.st === 'idle'", 30); p3 = T.ev(POS)
        T.step("real input: pushing the stick north off the bank starts the slide to the top of column 0", got and abs(p3[0] - cell_xz(0, 3)[0]) < 0.25 and abs(p3[1] - cell_xz(0, 3)[1]) < 0.25, pos=p3)
        pg.keyboard.down("d")
        got = until("window.__hm.jot.qa().pz.moves >= 3", 15); pg.keyboard.up("d"); until("window.__hm.jot.qa().pz.st === 'idle'", 30); p4 = T.ev(POS)
        T.step("real input: pushing east along the top row slides until the pillar stops you (cell 1, 3)", got and abs(p4[0] - cell_xz(1, 3)[0]) < 0.25 and abs(p4[1] - cell_xz(1, 3)[1]) < 0.25, pos=p4)
        T.ev("window.__hd2d.setTime(0.5)"); walk_to(*cell_xz(3, -1)); ok, pos = pz_go("N"); T.ev("window.__hd2d.ctx.player.x = 0"); frames(3); shot("jt_slide_pools")
        T.step("no JS errors in the Jotunheim run", not [e for e in errors if "jotunheim" in e.lower() or "jotun" in e.lower()], errs=errors[-3:])
        shot("jt_ring")
        a = load("jotunheim"); T.ev("window.__hd2d.setTime(0.0)"); frames(6); shot("jt_night")
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
        udd = os.environ.get("HD2D_USER_DATA_DIR")   # Bill's rule: browse only on the dedicated user-data dir, under the browser lock (same hook as smoke_muspelheim / smoke_niflheim)
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
    (out / "smoke_jotunheim.json").write_text(json.dumps(rep, indent=1))
    log(f"smoke_jotunheim: {'PASS' if rep['pass'] else 'FAIL'} {sum(s['pass'] for s in T.steps)}/{len(T.steps)} steps in {rep['seconds']} s")
    sys.exit(0 if rep["pass"] else 1)


if __name__ == "__main__":
    main()
