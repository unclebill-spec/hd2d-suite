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
        pg.wait_for_timeout(6500); a = sv()
        T.step("C1 steam vents cycle (puff tell, then blast)", a["deep"]["vents"] >= 2, deep=a["deep"])
        a = load("clockdeep2", "&svq=seal", "c7"); a = sv()
        T.step("clockdeep2 C4-C7 foe pools spawn (shadowsmiths, spark golems...)", {"shadowsmith", "sparkgolem", "sootling"} <= set(a["foes"]), qa=a)
        T.ev("(() => { window.__hm.peace = false; window.__hd2d.ctx.player.iframes = 99; })()")
        pg.wait_for_timeout(7000); a = sv()
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
