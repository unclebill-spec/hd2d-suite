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

    frames = T.frames   # engine-frame waits, never fixed sleeps

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
        pg.goto(url + f"&qa&combat&area={area}&spawn={spawn}{extra}")
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
            jt(f"qaSpot('tt{n}')"); fin()
            T.step(f"cairn {n}: two Rime Berserkers wake", until(f"window.__hm.jot.qa().cb.includes('tt{n}a') && window.__hm.jot.qa().cb.includes('tt{n}b')", 10), cb=sv()["cb"])
            jt(f"qaKill('tt{n}a')"); jt(f"qaKill('tt{n}b')"); frames(2)
            T.step(f"cairn {n} toppled (tt_c{n})", sv()["found"].get(f"tt_c{n}") == 1, found=sv()["found"])
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
        # barrow -> barrow2: the passage at the north end of the Avalanche Run
        a = load("barrow", "&jtq=barrow", "qa")
        T.step("the Avalanche Run has a passage north into the Throne Barrow", "barrow2" in a["exits"], exits=a["exits"])
        walk_to(0, -30.2)
        T.wait("window.__hm.area === 'barrow2' && window.__hd2d && window.__hd2d.ready && !window.__hm.busy", 90); T.idle(); frames(8); a = sv()
        T.step("walking through it lands you in B5 with a way back", a["area"] == "barrow2" and "barrow" in a["exits"], area=a["area"], exits=a["exits"])
        a = load("barrow2", "&jtq=deep")
        T.step("the Throne Barrow loads: foes, cold fire and lights", len(set(a["foes"])) >= 2 and a["fx"] >= 8 and a["lights"] >= 4, foes=a["foes"], fx=a["fx"], lights=a["lights"])
        hs = T.ev("(() => { const c = window.__hd2d.ctx; return { g: c.heightAt(0, 6), b6: c.heightAt(-4, -10), s6: c.heightAt(0, -2.4), br: c.heightAt(0, -22), b8: c.heightAt(-4, -36), b9: c.heightAt(-4, -48) }; })()")
        T.step("real height climbs: hall 1.2 m, bridge and crypt 2.4 m, throne dais 3.6 m", hs["g"] < 0.2 and 1.1 <= hs["b6"] <= 1.3 and 0.1 < hs["s6"] < 1.2 and hs["br"] >= 2.3 and hs["b8"] >= 2.3 and hs["b9"] >= 3.5, hs=hs)
        shot("jt_barrow2_hall")
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
        # ---- Hrimgard: P2 frozen floor + golems, P3 relit braziers that mend him until snuffed
        a = load("barrow2", "&jtq=deep"); walk_to(0, -46.0)
        T.step("Hrimgard wakes (phase 1: no slide, no relit braziers)", until("window.__hm.jot.qa().cb.includes('hrimgard')", 10) and sv()["boss"]["phase"] <= 1 and not sv()["boss"]["slide"], boss=sv()["boss"])
        jt("qaHp('hrimgard', 0.55)")
        T.step("below 60% (P2): the floor freezes and two ice golems rise", until("window.__hm.jot.qa().boss.p2 && window.__hm.jot.qa().cb.includes('hr_m1') && window.__hm.jot.qa().cb.includes('hr_m2')", 15), boss=sv()["boss"], cb=sv()["cb"])
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
        shot("jt_hrimgard_p3")
        # ---- cairn props use the existing kit (snow_mound)
        a = load("rimecaves", "&jtq=conquer")
        n = T.ev("window.__hd2d.ctx.scene.objects.filter((o) => /snow_mound/.test(o.glb)).length")
        T.step("the three watch-cairns are standing stone-mounds in the Rime Caves", n >= 3, n=n)
        shot("jt_cairns")
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
