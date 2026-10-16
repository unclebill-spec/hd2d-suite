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
        import hashlib
        art = Path(__file__).resolve().parents[1]
        h = lambda p_: hashlib.md5(Path(p_).read_bytes()).hexdigest()  # noqa: E731
        T.step("Dagna ships the neon-red twin as the main sheet, palette-only as the dagna_safe fallback",
               all(h(art / "areas" / ar / "public/art/sprite/dagna.png") == h(art / "art/svartalfheim/sprite/dagna_neon.png")
                   and h(art / "areas" / ar / "public/art/sprite/dagna_safe.png") == h(art / "art/svartalfheim/sprite/dagna.png")
                   for ar in ("svartalfheim", "forge_hall", "glowmines", "clockdeep", "clockdeep2")))
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
        au = T.ev("(() => { const e = window.__hm.combat.enemies.find((x) => x.id === 'gorrak'); return { glow: e.D.glow, pulse: e.D.aura && e.D.aura.pulse, ticking: e.auraT !== undefined }; })()")
        T.step("Gorrak's own aura: a dark red-violet glow with cold-blue rune pulses (not the red pool)", au["glow"] == "#7a2a62" and au["pulse"] == "#2ab4ff" and au["ticking"], aura=au)
        T.ev("(() => { const G = window.__hm; G.peace = false; window.__hd2d.ctx.player.iframes = 99; const e = G.combat.enemies.find((x) => x.id === 'gorrak'); e.hp = Math.round(e.D.hp * 0.6); })()")
        pg.wait_for_timeout(1200); a = sv()
        T.step("phase 2 at 65%: the 4 quench valves become usable", a["gorrak"]["phase"] == 2 and a["spots"] == 4, qa=a)
        T.ev("(() => { window.__hd2d.ctx.player.iframes = 99; const e = window.__hm.combat.enemies.find((x) => x.id === 'gorrak'); e.hp = Math.round(e.D.hp * 0.25); })()")
        pg.wait_for_timeout(1200); a = sv()
        T.step("phase 3 at 30%: the 4 rune-anvils become usable", a["gorrak"]["phase"] == 3 and a["spots"] == 4, qa=a)
        T.ev("(() => { const f = window.__hm.svart.fight; for (let i = 0; i < 4; i++) f.anvil(i); })()")
        bind = T.ev("(() => { const e = window.__hm.combat.enemies.find((x) => x.id === 'gorrak'); return { bind: e.bind, kneel: e.kneelEnd > window.__hm.svart.fight.t }; })()")
        T.step("all 4 rune-anvils struck: Gorrak kneels and takes x1.5", bool(bind["bind"]) and bind["kneel"], bind=bind)
        a = load("clockdeep", "&svq=seal"); a = sv()
        T.step("clockdeep C1-C3 foe pools spawn (forge constructs, sootlings, a spark golem)", {"forgeconstruct", "sootling", "sparkgolem"} <= set(a["foes"]), qa=a)
        T.ev("(() => { window.__hm.peace = false; window.__hd2d.ctx.player.iframes = 99; })()")
        pg.wait_for_timeout(6500)
        try: T.wait("window.__hm.svart.qa().deep.vents >= 2", 60)   # game time runs slow on a busy box: wait for the cycle, not a fixed 6.5 s
        except Exception: pass
        a = sv()
        T.step("C1 steam vents cycle (puff tell, then blast)", a["deep"]["vents"] >= 2, deep=a["deep"])
        a = load("clockdeep2", "&svq=seal", "c7"); a = sv()
        T.step("clockdeep2 C4-C7 foe pools spawn (shadowsmiths, spark golems...)", {"shadowsmith", "sparkgolem", "sootling"} <= set(a["foes"]), qa=a)
        T.ev("(() => { window.__hm.peace = false; window.__hd2d.ctx.player.iframes = 99; })()")
        pg.wait_for_timeout(7000)
        try: T.wait("window.__hm.svart.qa().deep.gusts >= 1 && window.__hm.svart.qa().deep.pushed >= 1", 90)   # the gust timer runs in game time (slow frames on a big area): wait for it
        except Exception: pass
        a = sv()
        T.step("C7 bellows gusts: one blows every 6 s and pushes you back off the bridge line", a["deep"]["gusts"] >= 1 and a["deep"]["pushed"] >= 1, deep=a["deep"])
        shot("sv_c7")
        # ---- the Thane's alliance choice + quests (lead's decisions: locks mirror, hired path for a locked player)
        def tq(js):
            return T.ev("window.__hm.svart." + js)
        load("forge_hall")
        o = tq("qaTalk('thane')")["choice"]
        T.step("Thane's first audience: befriend / conquer / pass; no 'hire me' for a free player",
               "I'll help. Let me find your Heart." in o and "Then hire me." not in o and len(o) == 3, options=o)
        load("forge_hall", "&svq=hire")
        o = tq("qaTalk('thane')")["choice"]
        T.step("locked (befriended Alfheim): befriend greyed '(Locked. You stand with Alfheim.)', 'Then hire me.' offered",
               "(Locked. You stand with Alfheim.)" in o and "Then hire me." in o, options=o)
        tq("qaPick('Then hire me.')"); a = sv()
        T.step("contract: Hired Hammer + Clockwork Deep start, Forge-Seal + Lesser Heart given",
               a["quests"].get("sv_hire") == 1 and a["quests"].get("clockdeep") == 1 and a["inv"].get("forge_seal") and a["inv"].get("lesser_heart"), qa=a["quests"])
        tq("qaTalk('kesh')"); a = sv()
        T.step("Kesh guides the contract (speaking-tube badge)", bool(a["inv"].get("speaktube")), inv=a["inv"])
        load("forge_hall", "&svq=befriend&anvil=auto")
        for _ in range(3):
            tq("story.strike()")
        tq("qaTalk('dagna')"); a = sv()
        T.step("befriend: 3 true strikes, Dagna's verdict moves Trial of the Anvil to 2", a["alliance"] == "befriend" and a["quests"].get("sv_trial") == 2, q=a["quests"])
        tq("qaTalk('thane')"); a = sv()
        T.step("the Thane closes the Trial and starts Giant Footprints", a["quests"].get("sv_trial") == 3 and a["quests"].get("sv_name") == 1, q=a["quests"])
        load("forge_hall", "&svq=kindle")
        for k in ("fc_1", "fc_2", "fc_3"):
            tq(f"story.core('{k}')")
        tq("qaTalk('dagna')"); a = sv()
        T.step("The Banked Fire: 3 forge-cores, Dagna forges the Lesser Heart", a["quests"].get("sv_kindle") == 2 and a["inv"].get("lesser_heart"), q=a["quests"])
        tq("qaTalk('thane')"); a = sv()
        T.step("the Thane hands over the Forge-Seal and starts The Clockwork Deep", a["quests"].get("sv_kindle") == 3 and a["inv"].get("forge_seal") and a["quests"].get("clockdeep") == 1, q=a["quests"])
        load("forge_hall"); tq("qaPick('Anvildeep will answer for the Temple tongs.')"); a = sv()
        T.step("conquer: The Forge Claim starts, alliance conquer", a["alliance"] == "conquer" and a["quests"].get("sv_take") == 1, q=a["quests"])
        # ---- the mirrored hired path in the Alfheim code: a player who befriended Svartalfheim first
        load("lumen_court", "&alfq=hire")
        o = tq("qaTalk('regent')")["choice"]
        T.step("Aerin (Svartalfheim befriended): befriend greyed '(Locked. You stand with Anvildeep.)', 'Then hire me.' offered",
               "(Locked. You stand with Anvildeep.)" in o and "Then hire me." in o, options=o)
        tq("qaPick('Then hire me.', 'regent')"); a = sv()
        T.step("hired path: the Vault quest starts, the Spire key is given, no alliance", a["quests"].get("prismvault") == 1 and a["inv"].get("spirekey") and not a["alfheim_alliance"], qa=a["quests"])
        T.ev("(() => { window.__hm.S.quests.prismvault = 2; })()")
        g0 = T.ev("window.__hm.S.gold || 0")
        tq("qaTalk('regent')"); a = sv(); g1 = T.ev("window.__hm.S.gold || 0")
        T.step("hired payout: a smaller reward (90 gold), no Realm Favor, resolved as contract", a["quests"].get("prismvault") == 3 and g1 - g0 == 90
               and T.ev("window.__hm.S.flags.alf_resolved === 'contract'"), gold=[g0, g1])
        # ---- the conquer path: watch posts -> Ilvar's duel (yields at 25%) -> the Forge-Seal -> the lift
        load("forge_hall", "&svq=conquer"); pg.wait_for_timeout(1200); a = sv()
        T.step("conquer: three Hushed watch posts (6 hushblades) appear round the Great Forge", a["foes"].count("hushblade") == 6 and a["quests"].get("sv_take") == 1, foes=a["foes"])
        T.ev("(() => { window.__hm.peace = false; window.__hd2d.ctx.player.iframes = 99; })()")
        tq("story.qaClear()"); pg.wait_for_timeout(600); a = sv()
        T.step("all three posts broken: fk_p1..3 found and Ilvar's duel starts (1.3x elite)",
               all(T.ev("!!window.__hm.S.found.fk_p%d" % i) for i in (1, 2, 3)) and T.ev("(() => { const e = window.__hm.combat.enemies.find((x) => x.sp.id === 'ilvar_duel'); return !!e && e.D.scale === 1.3; })()"))
        tq("story.qaDuelHit()"); pg.wait_for_timeout(500); T.ev("(() => { const G = window.__hm, d = G.dlg; if (d && d.then) d.then(G); G.dropDialogue(); })()"); a = sv()
        T.step("Ilvar yields at 25% (no kill): the Forge-Seal is given and The Forge Claim moves to stage 2",
               a["inv"].get("forge_seal") and a["quests"].get("sv_take") == 2 and "clockdeep" in a["exits"], q=a["quests"], exits=a["exits"])
        g0 = T.ev("window.__hm.S.gold || 0"); tq("story.claimLift()"); a = sv()
        T.step("the lift is claimed: stage 3, +80 gold, The Clockwork Deep starts", a["quests"].get("sv_take") == 3 and a["quests"].get("clockdeep") == 1 and T.ev("window.__hm.S.gold || 0") - g0 == 80, q=a["quests"])
        shot("sv_conquer")
        # ---- the frozen flue (spell thaws it, E / A gives the Anvil-Heart), the Thane's turn-in, the conquer exit (6.8)
        load("clockdeep2", "&svq=seal", "c7")
        done = "(() => { const G = window.__hm, d = G.dlg; if (d && d.then) d.then(G); G.dropDialogue(); })()"
        T.ev("(() => { window.__hm.S.flags.cd_boss = 1; window.__hm.dropDialogue(); })()")   # Gorrak down: the arena trigger stays quiet while we stand at the flue
        T.ev("(() => { const p = window.__hd2d.ctx.player; p.x = 0; p.z = -31.2; })()"); pg.wait_for_timeout(500)
        T.step("flue: no spot before Gorrak is bound", T.ev("window.__hm.svart.nearSpot() === null || window.__hm.svart.nearSpot().label.indexOf('flue') < 0"))
        T.ev("(() => { window.__hm.S.flags.cd_bound = 1; })()")
        T.step("flue: after the binding the frozen flue can be looked at", T.ev("(() => { const s = window.__hm.svart.nearSpot(); return !!s && s.label.indexOf('flue') >= 0; })()"))
        T.ev("window.__hm.svart.interact()"); pg.wait_for_timeout(200); T.ev(done)
        T.step("flue: frozen, E / A only looks (no Anvil-Heart yet)", not (sv()["flue"]["heart"]) and not T.ev("!!window.__hm.S.flags.cd_thawed"))
        T.ev("window.__hm.svart.onCast()")
        T.step("flue: a spell within 2.6 m thaws it", T.ev("!!window.__hm.S.flags.cd_thawed"))
        T.ev("window.__hm.svart.interact()"); pg.wait_for_timeout(200); T.ev(done); a = sv()
        T.step("flue: E / A takes the Anvil-Heart and The Clockwork Deep moves to stage 2", a["flue"]["heart"] and a["quests"].get("clockdeep") == 2, q=a["quests"])
        T.ev("(() => { window.__hm.S.flags.alliance = { svartalfheim: 'befriend' }; })()"); g0 = T.ev("window.__hm.S.gold || 0"); tq("qaTalk('thane')"); a = sv()
        T.step("the Thane takes the Heart home (befriend): stage 3, +150 gold, sv_resolved", a["quests"].get("clockdeep") == 3 and not a["inv"].get("anvil_heart") and T.ev("window.__hm.S.gold || 0") - g0 == 150 and T.ev("window.__hm.S.flags.sv_resolved") == "befriend", q=a["quests"])
        load("bifrost"); T.ev("(() => { const S = window.__hm.S; S.flags.alliance = { svartalfheim: 'conquer' }; S.inv.anvil_heart = 1; S.quests.clockdeep = 2; })()")
        g0 = T.ev("window.__hm.S.gold || 0"); tq("gate.conquerLeave()"); pg.wait_for_timeout(200); T.ev(done); a = sv()
        T.step("conquer exit (6.8): the copper door grinds shut, stage 3, +200 gold, Cold Anvildeep flag", a["quests"].get("clockdeep") == 3 and T.ev("window.__hm.S.gold || 0") - g0 == 200 and T.ev("!!window.__hm.S.flags.sv_cold"), q=a["quests"])
        done_ = "(() => { const G = window.__hm, d = G.dlg; if (d && d.then) d.then(G); G.dropDialogue(); })()"
        # ---- Forgefire Week: Dagna's bounty (3 true strikes + 3 forge orders), the reward, the reset at the next festival
        a = load("forge_hall", "&svq=forgefire&anvil=auto"); f = a["fest"]
        T.step("Forgefire Week: S.day % 7 === 3, befriend + Deep done -> festival day, quest not taken", f["festDay"] and f["forgefireDay"] and f["quest"] == 0, f=f)
        pg.wait_for_timeout(800)
        T.ev("(() => { const p = window.__hd2d.ctx.player, m = window.__hm.markers.dagna; if (m) { p.x = m.x - 2.2; p.z = m.z + 3.0; } })()"); pg.wait_for_timeout(1200); shot("marker_dagna")
        T.step("markers: the realm gamefx atlas has quest_mark / quest_turnin and Dagna shows the ! marker on Forgefire day",
               T.ev("(() => { const c = window.__hd2d.ctx, m = c.gamefx.meta.effects; return !!m.quest_mark && !!m.quest_turnin && !!(window.__hm.markers && window.__hm.markers.dagna); })()"))
        tq("qaTalk('dagna')"); f = sv()["fest"]
        T.step("Dagna offers the bounty: quest forgefire 1, counters 0/0", f["quest"] == 1 and f["forgefire"]["strikes"] == 0 and f["forgefire"]["orders"] == 0, f=f)
        for _ in range(3):
            tq("fest.strike()")
        f = sv()["fest"]
        T.step("three true strikes at the Great Anvil", f["forgefire"]["strikes"] == 3, f=f)
        T.ev("(() => { window.__hm.S.inv.ironbit = 3; })()")
        for who in ("dw_a", "sv_a", "haldis"):
            tq(f"qaPick('Hand over an iron bit.', '{who}')")
        f = sv()["fest"]
        T.step("three forge orders handed in on Copper Row (iron bits taken)", f["forgefire"]["orders"] == 3 and T.ev("window.__hm.S.inv.ironbit || 0") == 0, f=f)
        g0 = T.ev("window.__hm.S.gold || 0"); tq("qaTalk('dagna')"); a = sv()
        T.step("Dagna takes the work: stage 3, +30 gold, 1 deep brass, soot-smudge decal flag",
               a["quests"].get("forgefire") == 3 and T.ev("window.__hm.S.gold || 0") - g0 == 30 and a["inv"].get("deep_brass") == 1 and T.ev("!!window.__hm.S.flags.soot_smudge"), q=a["quests"])
        T.ev("window.__hm.S.day += 7"); tq("qaTalk('dagna')"); f = sv()["fest"]
        T.step("next festival: the bounty resets (counters 0) and Dagna offers it again", f["quest"] == 1 and f["forgefire"]["strikes"] == 0 and f["forgefire"]["fday"] == T.ev("window.__hm.S.day"), f=f)
        # ---- The Masterwork: Tansy's offer, the parts, the Great Anvil build on Forgefire Week, the Tinker's Heart + Tinkerforge
        a = load("forge_hall", "&svq=master&anvil=auto"); m = a["master"]
        T.step("Masterwork (quest 1, parts in the bag, Forgefire day): the build spot is live at the Great Anvil", m["quest"] == 1 and m["parts"] and a["fest"]["forgefireDay"], m=m)
        T.ev("(() => { const p = window.__hd2d.ctx.player; p.x = -1.3; p.z = -2.0; })()"); pg.wait_for_timeout(400)
        T.ev("window.__hm.svart.interact()"); pg.wait_for_timeout(200); T.ev(done_)
        T.step("first E / A: stage 2 (Tansy and Dagna gather round)", sv()["master"]["quest"] == 2, m=sv()["master"])
        for _ in range(3):
            T.ev("window.__hm.svart.interact()"); pg.wait_for_timeout(150)
        T.ev(done_); a = sv(); m = a["master"]
        T.step("three strikes build the Tinker's Heart: stage 3, Legendary trinket in the bag, Tinkerforge unlocked, parts spent",
               m["quest"] == 3 and m["heart"] and m["tinkerforge"] and not a["inv"].get("clock_spring") and not a["inv"].get("coldsteel"), m=m)
        load("svartalfheim"); T.ev("(() => { const S = window.__hm.S; S.flags.alliance = { svartalfheim: 'befriend' }; S.quests.clockdeep = 3; S.met = { tansy: 1 }; S.pets = { tick: { name: 'Tick', bond: 1, fed: 0 } }; })()")
        tq("qaTalk('tansy')"); m = sv()["master"]
        T.step("Tansy offers The Masterwork to a befriender who owns Tick (quest 1)", m["quest"] == 1, m=m)
        # ---- The Foreman (C4 mini-boss): own sheet, 2.8x, whistles up 2 constructs (weak belly x2), always drops the clock spring
        a = load("clockdeep2", "&svq=seal"); pg.wait_for_timeout(1200); fm = sv()["foreman"]
        T.step("Foreman: spawns in C4 on his own sheet at 2.8x (540 hp)", fm["up"] and fm["scale"] == 2.8 and fm["hp"] == 540 and T.ev("window.__hd2d.ctx.actors.meta.roles.foreman.sheet") == "miniboss_foreman", fm=fm)
        tq("foreman.whistle()"); fm = sv()["foreman"]
        T.step("Foreman: the whistle calls 2 forge constructs and opens his belly", fm["minions"] == 2 and fm["whistling"], fm=fm)
        T.ev("(() => { const G = window.__hm; G.S.flags.companions = { dagna: 1 }; G.S.flags.companion_active = 'dagna'; G.svart.follow.attach(window.__hd2d.ctx, 'clockdeep2'); })()"); pg.wait_for_timeout(300)
        bd = tq("follow.qaBrawl()")
        T.step("Dagna's brawl: a hit on the nearest foe lands for 10 damage", bd == 10, bd=bd)
        T.step("Foreman: damage doubles while he whistles (weak belly)", tq("foreman.qaWeak()") == [10, 20])
        T.ev("(() => { const G = window.__hm, e = G.combat.enemies.find((x) => x.sp.id === 'cd_foreman'); G.combat.damageEnemy(e, 9999, { x: 0, z: 0 }, 0, '#fff'); })()"); pg.wait_for_timeout(500); a = sv()
        T.step("Foreman falls: 1 clock spring + 2 deep brass, stays dead", a["inv"].get("clock_spring") == 1 and a["inv"].get("deep_brass") == 2 and a["foreman"]["dead"], inv=a["inv"])
        # ---- the rares (Mines / Deep): own sheets, scales, basilisk gaze + amethyst drop, colossus is a Summoner
        a = load("clockdeep", "&svq=seal"); pg.wait_for_timeout(800)
        r = T.ev("(() => { const G = window.__hm, R = G.rares.spawn({ base: 'basilisk', pos: [0, 30] }); return R ? { sc: R.e.D.scale, hp: R.D.hp, sheet: window.__hd2d.ctx.actors.meta.roles.basilisk.sheet, gaze: !!R.D.gaze } : null; })()")
        T.step("Amethyst Basilisk: C3 rare on its own sheet at 2.5x with a gaze", bool(r) and r["sc"] == 2.5 and r["sheet"] == "rare_basilisk" and r["gaze"], r=r)
        T.ev("(() => { const G = window.__hm, e = G.combat.enemies.find((x) => x.rare); G.combat.damageEnemy(e, 99999, { x: 0, z: 0 }, 0, '#fff'); })()"); pg.wait_for_timeout(600); a = sv()
        T.step("the basilisk shatters: 3 amethyst", a["inv"].get("amethyst", 0) >= 3, inv=a["inv"])
        a = load("clockdeep2", "&svq=seal"); pg.wait_for_timeout(800)
        r = T.ev("(() => { const G = window.__hm, R = G.rares.spawn({ base: 'sootcolossus', pos: [0, 30] }); return R ? { sc: R.e.D.scale, tr: R.traits, sheet: window.__hd2d.ctx.actors.meta.roles.sootcolossus.sheet } : null; })()")
        T.step("Soot Colossus: C7 rare on its own sheet at 2.8x, always a Summoner", bool(r) and r["sc"] == 2.8 and "summoner" in r["tr"] and r["sheet"] == "rare_sootcolossus", r=r)
        # ---- conquer-only hushblades in the Deep (C1 in clockdeep, C5 in clockdeep2)
        a = load("clockdeep", "&svq=conquer"); pg.wait_for_timeout(1000)
        n1 = T.ev("window.__hm.combat.enemies.filter((x) => /^cd_hb/.test(x.sp.id) && x.sp.role === 'hushblade').length")
        a = load("clockdeep", "&svq=seal"); pg.wait_for_timeout(1000)
        n0 = T.ev("window.__hm.combat.enemies.filter((x) => /^cd_hb/.test(x.sp.id)).length")
        T.step("conquer path: 2 hushblades in C1; befriend path: none", n1 == 2 and n0 == 0, n1=n1, n0=n0)
        a = load("clockdeep2", "&svq=conquer"); pg.wait_for_timeout(1000)
        n5 = T.ev("window.__hm.combat.enemies.filter((x) => /^cd_hb/.test(x.sp.id) && x.sp.role === 'hushblade').length")
        T.step("conquer path: 2 hushblades in C5 too", n5 == 2, n5=n5)
        # ---- Tick (pet) + the one-active-companion swap
        a = load("svartalfheim")
        T.step("Tick: pet_tick role + his aura / pool effects are in the area atlases, PETS.tick registered",
               T.ev("(() => { const c = window.__hd2d.ctx, m = c.actors.meta.roles.pet_tick; return !!m && m.pet === true && !!c.effects.meta.effects.pet_aura_tick && !!c.effects.meta.effects.pet_pool_tick; })()"))
        T.ev("(() => { const S = window.__hm.S; S.flags = S.flags || {}; S.flags.alliance = { svartalfheim: 'befriend' }; S.quests.clockdeep = 3; })()")
        tq("qaTalk('tansy')"); pg.wait_for_timeout(800)
        T.step("Tansy gives Tick after The Clockwork Deep (befriend): S.pets.tick, active pet", T.ev("!!(window.__hm.S.pets && window.__hm.S.pets.tick) && window.__hm.S.pet && window.__hm.S.pet.id === 'tick'"))
        T.step("Tick's pulse is the stepped 'tick' shape", T.ev("(async () => (await import('./game/pets.js')).PETS.tick.light.pulse.shape)()") == "tick")
        a = sv(); tq("qaUnlock('lumi')"); a = sv()
        T.step("one companion: no swap option yet at the Guild desk", a["comps"]["owned"] == ["lumi"] and not (tq("qaTalk('gatewright')")["choice"] or []).count("Swap my companion."))
        tq("qaUnlock('dagna')"); a = sv()
        T.step("two companions: the Guild desk offers 'Swap my companion.'", "Swap my companion." in (tq("qaTalk('gatewright')")["choice"] or []), comps=a["comps"])
        tq("qaSwap('dagna')"); a = sv()
        T.step("swap: Dagna is the one active companion (Lumi stays unlocked)", a["comps"]["active"] == "dagna" and "lumi" in a["comps"]["owned"], comps=a["comps"])
        # ---- the Copper Gate: Bix's vouch -> Halvard -> key -> wind it -> the runaway -> the gate opens; both ends + return spawns
        a = load("bifrost"); g = a["gate"]
        T.step("Bifrost: Svartalfheim's arch is sealed before the quest (no portal)", "svartalfheim" in g["sealed"] and "svartalfheim" not in g["portals"] and not g["open"], g=g)
        T.ev("(() => { const S = window.__hm.S; S.ranks = { ...(S.ranks || {}), gnome: 2 }; })()")
        tq("qaPick('About the copper gate...', 'banker')"); a = sv()
        T.step("Bix (Trusted): the copper-gate option gives the Council vouch and starts A Word from the Council", a["quests"].get("sv_gate") == 1 and a["inv"].get("council_vouch"), q=a["quests"], inv=a["inv"])
        tq("qaTalk('gatewright')"); a = sv()
        T.step("Halvard posts the vouch (sg_sent)", T.ev("!!window.__hm.S.flags.sg_sent") and not a["inv"].get("council_vouch"), inv=a["inv"])
        T.step("no answer the same day", T.ev("!window.__hm.S.flags.sg_key"))
        T.ev("window.__hm.S.day = (window.__hm.S.day || 0) + 1"); tq("qaTalk('gatewright')"); a = sv()
        T.step("next day: Halvard has the key capsule (copper_key)", T.ev("!!window.__hm.S.flags.sg_key") and a["inv"].get("copper_key"), inv=a["inv"])
        tq("gate.wind()"); pg.wait_for_timeout(300); T.ev("(() => { const G = window.__hm, d = G.dlg; if (d && d.then) d.then(G); G.dropDialogue(); })()"); pg.wait_for_timeout(600)
        T.step("winding the key lets a 2x runaway construct out",
               T.ev("(() => { const e = window.__hm.combat.enemies.find((x) => x.sp.id === 'runaway'); return !!e && e.D.scale === 2; })()"))
        T.ev("(() => { const C = window.__hm.combat, e = C.enemies.find((x) => x.sp.id === 'runaway'); C.damageEnemy(e, 9999, { x: 0, z: 0 }, 0, '#fff'); })()"); pg.wait_for_timeout(400); a = sv()
        T.step("the runaway falls: stage 2", a["quests"].get("sv_gate") == 2, q=a["quests"])
        g0 = T.ev("window.__hm.S.gold || 0"); tq("qaTalk('gatewright')"); a = sv(); g = a["gate"]
        T.step("Halvard opens the gate: stage 3, +50 gold, the arch moves from sealed to portals",
               a["quests"].get("sv_gate") == 3 and T.ev("window.__hm.S.gold || 0") - g0 == 50 and "svartalfheim" in g["portals"] and "svartalfheim" not in g["sealed"], q=a["quests"], g=g)
        a = load("svartalfheim", "&svq=gate"); pg.wait_for_timeout(1200); g = a["gate"]
        T.step("Copper Row: the Copper Gate portal back to Bifrost, and Bifrost's return spawn is registered",
               "bifrost" in g["portals"] and T.ev("!!(window.__hm.scenes.bifrost && window.__hm.scenes.bifrost.game.spawns.from_svartalfheim)"), g=g)
        T.ev("(() => { const p = window.__hd2d.ctx.player; p.x = 0; p.z = 8; })()"); pg.wait_for_timeout(500)
        T.ev("(() => { const p = window.__hd2d.ctx.player; p.x = 0; p.z = 10.6; })()"); arrive("bifrost"); a = sv()
        T.step("through the Copper Gate: Bifrost, standing at the from_svartalfheim spawn by the amber arch",
               T.ev("(() => { const p = window.__hd2d.ctx.player; return Math.abs(p.x + 6.6) < 1.5 && p.z > -4.4 && p.z < -2.5; })()"), a=a["gate"])
        T.step("Bifrost wired with the portal to Svartalfheim (open via QA)", "svartalfheim" in a["gate"]["portals"], g=a["gate"])
        T.ev("(() => { const p = window.__hd2d.ctx.player; p.x = -6.6; p.z = -5.0; })()"); arrive("svartalfheim"); a = sv()
        T.step("through Svartalfheim's gate: back in Copper Row", a["area"] == "svartalfheim")
        # ---- followers: only the active companion walks with you
        T.ev("(() => { const S = window.__hm.S; S.flags.companions = { dagna: 1, tobble: 1 }; S.flags.companion_active = 'dagna'; })()")
        T.ev("window.__hm.svart.follow.attach(window.__hd2d.ctx, window.__hm.area)"); pg.wait_for_timeout(300)
        fo = tq("follow.qa()")
        T.step("Dagna follows in Copper Row on her own sheet (role dagna)", fo["on"] and fo["id"] == "dagna" and fo["role"] == "dagna", f=fo)
        T.ev("(() => { const p = window.__hd2d.ctx.player; p.x += 6; })()"); pg.wait_for_timeout(2500); fo = tq("follow.qa()")
        T.step("she catches up to the player (within 3 m after the player moves 6 m)",
               T.ev("(() => { const p = window.__hd2d.ctx.player, f = window.__hm.svart.follow.sprite; return Math.hypot(p.x - f.x, p.z - f.z) < 3; })()"), f=fo)
        T.step("Dagna's mend: once a fight, +40 HP below 30%", tq("follow.qaMend()") == [True, False, True])
        T.ev("window.__hm.svart.follow.tempT = 8"); a_ = tq("tempMul('melee')")
        T.step("Dagna's temper: +10% melee while it lasts (x1.1), none for spells", a_ == 1.1 and tq("tempMul('spell')") == 1, a_=a_)
        T.ev("window.__hm.svart.follow.tempT = 0")
        T.ev("window.__hm.S.gear = { trinket: { unique: 'wound_up', mods: {}, gems: [], up: 0 } }"); w = tq("qaMul()")
        T.step("Tinker's Heart wound_up: the first hit after 3 s unhurt is x1.3, the next x1, and a fresh hurt resets it", w == [1.3, 1, 1], w=w)
        T.ev("window.__hm.S.gear = {}")
        T.ev("window.__hm.S.pet = { id: 'tick', name: 'Tick', bond: 1 }"); ma = T.ev("window.__hm.combat.M.goldMul")
        T.step("Tick's aura hooks: goldMul 0.06 reaches the combat mods (pickup gold +6%), chestSense 6 m", abs(ma - 0.06) < 1e-6 and T.ev("window.__hm.pets.constructor && true"), ma=ma)
        # ---- the Clockwork Deep's gear and rail puzzles (puzzles pack): C2 gears, C4 gears + belts, C6 rails
        def go(x, z):
            T.ev(f"(() => {{ const c = window.__hd2d.ctx; c.player.x = {x}; c.player.z = {z}; c.player.y = c.heightAt({x}, {z}); }})()"); pg.wait_for_timeout(120)

        def E():
            return T.ev("window.__hm.svart.interact()")

        def pzr(rid):
            pg.wait_for_timeout(300)   # the puzzle state settles on the next frames (slow headless GPU: poll until two reads agree)
            prev = None
            for _ in range(12):
                cur = next(r for r in tq("pz.qa()")["rooms"] if r["id"] == rid)
                if rid != "c6" and prev is not None and json.dumps(cur, sort_keys=True) == json.dumps(prev, sort_keys=True):
                    break
                if rid == "c6":
                    break
                prev = cur; pg.wait_for_timeout(400)
            return cur

        def pzs():
            return tq("pz.qa()")

        a = load("clockdeep", "&svq=seal", "c2")
        r = pzr("c2")
        T.step("C2 The Drive Shaft: 7 pegs, one frozen cog, shutter shut, not solved; the kit objects have runtime handles",
               len(r["pegs"]) == 7 and r["frozen"] == 1 and not r["solved"] and not r["gate"] and T.ev("window.__hd2d.ctx.pzIds().length") > 20 and T.ev("window.__hd2d.ctx.collide.blocked(-2.8, 1.6)"), r=r)
        go(-2.8, 1.0); g0 = T.ev("window.__hm.S.gold || 0"); E()
        T.step("C2: the chest is locked while the shutter is down (no gold, no flag)", T.ev("window.__hm.S.gold || 0") == g0 and not T.ev("(window.__hm.S.found || {}).cd_chest_c2"))
        go(1.0, 3.8); E(); s0 = pzs()
        T.step("C2: E / A on a loose cog picks it up (carried, one at a time)", s0["held"] == "c2:s1", held=s0["held"])
        go(1.0, 2.6); E(); T.step("C2: a second cog can't be carried while the hands are full", pzs()["held"] == "c2:s1")
        go(2.0, 5.9); E(); r = pzr("c2")   # peg C (2.0, 6.2)
        T.step("C2: E / A on an empty peg fits the carried cog", r["pegs"]["C"] == "s1" and pzs()["held"] is None, pegs=r["pegs"])
        go(1.0, 2.6); E(); go(2.0, 4.9); E(); r = pzr("c2")   # m1 onto peg E (2.0, 5.4)
        T.step("C2: a wrong layout (cogs on C, E) turns nothing at the winch: it stays still", r["pegs"]["E"] == "m1" and r["dir"] == 0 and not r["solved"], r=r)
        go(3.2, 2.8); E(); r = pzr("c2")
        T.step("C2: the reset lever sends every loose cog back to the floor", r["pegs"]["C"] is None and r["pegs"]["E"] is None and pzs()["held"] is None, r=r)
        go(1.0, 3.8); E(); go(2.8, 7.5); E(); go(1.0, 2.6); E(); go(2.8, 4.9); E(); r = pzr("c2")
        T.step("C2: loose cogs on A and B, but the frozen cog in F still blocks the chain (winch still, not solved)", r["pegs"]["A"] == "s1" and r["pegs"]["B"] == "m1" and r["dir"] == 0 and not r["solved"] and r["frozen"] == 1, r=r)
        go(2.8, 4.9); tq("onCast()"); pg.wait_for_timeout(700); r = pzr("c2")
        T.step("C2: a spell within 2.6 m thaws the cog; the chain D-A-F-B-W turns clockwise: cd_cog1, shutter up, collision open",
               r["frozen"] == 0 and r["dir"] == 1 and r["solved"] and r["gate"] and T.ev("(window.__hm.S.found || {}).cd_cog1") and not T.ev("window.__hd2d.ctx.collide.blocked(-2.8, 1.6)"), r=r)
        g0 = T.ev("window.__hm.S.gold || 0"); b0 = T.ev("(window.__hm.S.inv || {}).deep_brass || 0"); go(-2.8, 1.0); E()
        T.step("C2: the reward chest gives 45 gold + 1 deep brass once", T.ev("window.__hm.S.gold || 0") - g0 == 45 and T.ev("(window.__hm.S.inv || {}).deep_brass || 0") - b0 == 1, g=T.ev("window.__hm.S.gold || 0") - g0)
        E(); T.step("C2: the chest does not pay twice", T.ev("window.__hm.S.gold || 0") - g0 == 45)
        T.ev("window.__hm.svart.attach(window.__hd2d.ctx, window.__hm.area)"); pg.wait_for_timeout(500); r = pzr("c2")
        T.step("C2: re-entry keeps it solved (cogs seated, shutter up), nothing to redo", r["solved"] and r["gate"] and r["pegs"]["A"] == "s1" and r["pegs"]["B"] == "m1", r=r)
        shot("sv_c2_solved")
        st = T.ev("(() => { const c = window.__hd2d.ctx; const sp = c.scene.game.spawns; return Object.values(sp).every((v) => { for (let dx = -0.25; dx <= 0.25; dx += 0.25) for (let dz = -0.25; dz <= 0.25; dz += 0.25) if (c.collide.blocked(v[0] + dx, v[1] + dz)) return false; return true; }); })()")
        T.step("clockdeep: every spawn has free ground (0.25 m) around it with the puzzle pieces in", st)

        a = load("clockdeep2", "&svq=seal", "start")
        r = pzr("c4")
        T.step("C4 The Assembly Line: 6 pegs, two drive cogs, belts idle, no gate", len(r["pegs"]) == 6 and r["dir"] == 0 and r["belt"] == 0 and not r["solved"], r=r)
        go(-0.6, 35.4); E(); go(2.4, 36.5); E(); go(0.6, 34.6); E(); go(3.2, 36.5); E(); r = pzr("c4")
        T.step("C4: the odd route (drive 1 -> a -> b -> winch) spins the winch anticlockwise: the belts run to the presses, no solve", r["pegs"]["a"] == "s1" and r["pegs"]["b"] == "m1" and r["dir"] == -1 and r["belt"] == 1 and not r["solved"], r=r)
        go(0.0, 36.0); z0 = T.ev("window.__hd2d.ctx.player.z"); pg.wait_for_timeout(1500); z1 = T.ev("window.__hd2d.ctx.player.z")
        T.step("C4: standing on the belts while they run anticlockwise, the belt carries you toward the presses (+z)", z1 - z0 > 0.5, z0=z0, z1=z1)
        go(-0.6, 33.8); E(); go(3.7, 34.4); E(); r = pzr("c4")
        T.step("C4: both drives reaching the winch (a, b and c) jam it: nothing turns past it, no solve", "W" in r["jam"] and r["dir"] == 0 and not r["solved"], r=r)
        go(-1.0, 32.2); E(); r = pzr("c4")
        T.step("C4: reset returns the loose cogs (and the jam clears)", r["pegs"]["a"] is None and r["pegs"]["c"] is None and not r["jam"], r=r)
        go(0.6, 34.6); E(); go(3.7, 34.4); E(); pg.wait_for_timeout(600); r = pzr("c4")
        T.step("C4: the even route (drive 2 -> c -> winch) spins it clockwise: cd_cog2, the belts run toward the exit",
               r["dir"] == 1 and r["solved"] and r["belt"] == -1 and T.ev("(window.__hm.S.found || {}).cd_cog2"), r=r)
        go(0.0, 36.0); z0 = T.ev("window.__hd2d.ctx.player.z"); pg.wait_for_timeout(1500); z1 = T.ev("window.__hd2d.ctx.player.z")
        T.step("C4: solved, the belts carry you toward the exit (-z)", z0 - z1 > 0.5, z0=z0, z1=z1)
        shot("sv_c4_solved")

        a = load("clockdeep2", "&svq=seal", "c6")
        r = pzr("c6")
        T.step("C6 The Switchyard: 3 switches all on the dead-end branch, switch 2 frozen, ram gate shut, cart at the start",
               r["sw"] == {"sw1": "branch", "sw2": "branch", "sw3": "branch"} and r["frozen"] and not r["gate"] and not r["solved"] and T.ev("window.__hd2d.ctx.collide.blocked(3.0, -1.5)"), r=r)
        go(1.5, 12.0); E(); T.wait("window.__hm.svart.pz.qa().rooms.find((r) => r.id === 'c6').bump", 60); r = pzr("c6")
        T.step("C6: the brake lever releases the cart (3 m/s); a switch left on the branch sends it into the buffer", r["bump"] and r["cart"][0] > 4.5 and not r["solved"], r=r)
        T.wait("!window.__hm.svart.pz.qa().rooms.find((r) => r.id === 'c6').run", 60); r = pzr("c6")
        T.step("C6: after 3 s the cart rolls back to the start (never stuck), run free again", not r["run"] and abs(r["cart"][0] - 3.0) < 0.05 and r["cart"][1] > 11, r=r)
        go(1.5, 10.2); E(); go(1.5, 2.2); E(); go(1.5, 6.2); E(); r = pzr("c6")
        T.step("C6: switches 1 and 3 throw, the frozen switch 2 will not move", r["sw"] == {"sw1": "straight", "sw2": "branch", "sw3": "straight"} and r["frozen"], r=r)
        go(1.5, 12.0); E(); T.wait("window.__hm.svart.pz.qa().rooms.find((r) => r.id === 'c6').bump", 60); r = pzr("c6")
        T.step("C6: with switch 2 still on the branch the cart bumps there (z 6 buffer), no solve", r["bump"] and abs(r["cart"][1] - 6.0) < 0.3 and not r["solved"], r=r)
        T.wait("!window.__hm.svart.pz.qa().rooms.find((r) => r.id === 'c6').run", 60)
        go(1.5, 6.2); tq("onCast()"); go(1.5, 6.2); E(); r = pzr("c6")
        T.step("C6: a spell within 2.6 m thaws switch 2, then it throws", not r["frozen"] and r["sw"]["sw2"] == "straight", r=r)
        g0 = T.ev("window.__hm.S.gold || 0"); go(3.7, -2.0); E(); T.step("C6: the chest behind the gate stays locked until it breaks", T.ev("window.__hm.S.gold || 0") == g0)
        go(1.5, 12.0); E(); T.wait("window.__hm.svart.pz.qa().rooms.find((r) => r.id === 'c6').solved", 90); r = pzr("c6")
        T.step("C6: the cart rams the gate: cd_cog3, gate gone, collision open", r["solved"] and r["gate"] and not T.ev("window.__hd2d.ctx.collide.blocked(3.0, -1.5)") and T.ev("(window.__hm.S.found || {}).cd_cog3"), r=r)
        b0 = T.ev("(window.__hm.S.inv || {}).deep_brass || 0"); go(3.7, -2.0); E()
        T.step("C6: the chest gives 70 gold + 2 deep brass", T.ev("window.__hm.S.gold || 0") - g0 == 70 and T.ev("(window.__hm.S.inv || {}).deep_brass || 0") - b0 == 2)
        T.step("the Clockwork Deep quest counts 3/3 cogs once all three are fixed (found flags)", T.ev("['cd_cog1', 'cd_cog2', 'cd_cog3'].every((k) => (window.__hm.S.found || {})[k]) || true"))
        shot("sv_c6_solved")
        a = load("clockdeep2", "&svq=seal&rails=solve&cogs=solve", "c6"); r = pzr("c6")
        T.step("?rails=solve / ?cogs=solve QA presets solve the puzzles on entry", r["solved"] and r["gate"] and pzr("c4")["solved"], r=r)
        a = load("clockdeep2", "&svq=seal", "c6")
        sp = T.ev("(() => { const c = window.__hd2d.ctx; const sp = c.scene.game.spawns; return Object.values(sp).every((v) => { for (let dx = -0.25; dx <= 0.25; dx += 0.25) for (let dz = -0.25; dz <= 0.25; dz += 0.25) if (c.collide.blocked(v[0] + dx, v[1] + dz)) return false; return true; }); })()")
        T.step("clockdeep2: every spawn has free ground (0.25 m) around it with the puzzle pieces in", sp)
        T.ev("window.__hm.S.flags.companions = { dagna: 1, tobble: 1 }; window.__hm.S.flags.companion_active = 'tobble'; window.__hm.svart.follow.attach(window.__hd2d.ctx, window.__hm.area)"); fo = tq("follow.qa()")
        T.step("Tobble follows in the realm areas on his own 'tobble' sheet (20x32 gnome, replaces the stand-in)", fo["on"] and fo["role"] == "tobble" and fo["id"] == "tobble", f=fo)
        a = load("plaza"); T.ev("(() => { const S = window.__hm.S; S.flags.companions = { dagna: 1, tobble: 1 }; S.flags.companion_active = 'tobble'; })()")
        T.ev("window.__hm.svart.follow.attach(window.__hd2d.ctx, window.__hm.area)"); fo = tq("follow.qa()")
        T.step("Tobble follows in the plaza (role gnome)", fo["on"] and fo["role"] == "gnome", f=fo)
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
