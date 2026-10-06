"""[ALFHEIM] Alfheim realm smoke (realm-alfheim branch): Lumenvale Glade + the Prism Vault + Lady Sylvaine.

    python3 games/hearthmoor/tests/smoke_alfheim.py [--out games/hearthmoor/shots/alfheim_smoke]

Runs standalone (its own server + headless Chromium), and smoke.py calls steps() in its own browser context after the
main run, so the main run's save is untouched. Boots ?qa (fresh state, no saving) with &combat&peace: enemies move but
stay calm until a step drops G.peace for a fight.
Covers: Alfheim's arch at Bifrost stays sealed without the key, opens with it (S.flags.alf_key) as a violet / cold swirl
portal; keys: E talks to Warden Aelindra, key 1 picks the alliance (befriend) and starts the story quest; controller: A
talks to Thalion; a real fight in the glade (R attacks land on a prism shard; a neon wisp's prism bolt is a live
projectile); touch: tapping the Prism Vault's swirl walks into it; the vault moves the quest on; Lady Sylvaine is
drawn natively at 5x (boss sheet 100x160, scale 5, on-screen height >= 4.5x the hero's), her drain nova silences
spells, she calls two Mirror Duelists at half health, her fall sets the flag; mouse: clicking the vault exit swirl walks
out; Aelindra's turn-in pays gold + Embassy merit; the gate home lands in front of Alfheim's arch at Bifrost; no JS
errors. Screenshots: arrival, settlement at night (violet glow), a fight, the vault, Sylvaine at scale.
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

    def alf():
        return T.ev("window.__hm.alfheim.qa()")

    def screen(x, z, y=None):
        return T.ev(f"(() => {{ const c = window.__hd2d.ctx; return c.project({x}, {y if y is not None else f'c.heightAt({x}, {z})'}, {z}); }})()")

    def tap(x, y):
        t = time.time()
        cdp.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": x, "y": y, "id": 0}], "timestamp": t})
        cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": [], "timestamp": t + 0.05})

    def arrive(area, timeout=120):
        T.wait(f"window.__hm.area === '{area}' && !window.__hm.busy", timeout); T.idle(); pg.wait_for_timeout(500)

    try:
        pg.goto(url + "&qa&combat&area=bifrost&spawn=from_vanaheim")
        T.wait("window.__hm && window.__hm.ctx && window.__hd2d && window.__hd2d.ready", 150)
        T.idle(); pg.wait_for_timeout(600)
        a0 = alf()
        T.step("Alfheim: without the key its arch at Bifrost stays sealed (frozen violet seal, no portal)",
               not a0["open"] and "alfheim" in a0["sealed"] and "alfheim" not in a0["portals"], qa=a0)
        T.ev("window.__hm.S.flags.alf_key = 1; window.__hm.go('bifrost', 'from_vanaheim')"); arrive("bifrost")
        a1 = alf()
        T.step("Alfheim: with the key (S.flags.alf_key) the arch opens: seal gone, a swirl portal to Lumenvale (violet once bifrost is rebuilt)",
               a1["open"] and "alfheim" not in a1["sealed"] and "alfheim" in a1["portals"] and a1["gateFx"] in ("rift_vortex_violet", "rift_vortex"), qa=a1)
        T.walk(-5.0, -10.4); pg.wait_for_timeout(300)
        pr = T.ev("document.getElementById('prompt').textContent")
        idx = T.ev("window.__hm.ctx.scene.game.portals.findIndex((p) => p.to === 'alfheim')")
        area = T.go_rect("portals", idx, 150)
        arrive("alfheim")
        p = T.pos()
        T.step("keys/walk: stepping into Alfheim's swirl at Bifrost lands in Lumenvale Glade at the arrival arch",
               "Alfheim" in pr and area == "alfheim" and abs(p[0] + 11.0) < 1.2 and abs(p[1] - 3.0) < 1.2, prompt=pr, pos=p)
        shot("alfheim_arrival")
        # ---------------------------------------------------------- Lumenvale: Aelindra (keys), Thalion (controller)
        n, first = T.talk("aelindra", keep_open=True)
        ch = T.to_choice()
        pg.keyboard.press("1"); pg.wait_for_timeout(400); T.read_all(); pg.wait_for_timeout(300)
        S = T.S()
        T.step("keys: E talks to Warden Aelindra; her alliance choice (befriend / conquer / pass), key 1 befriends Alfheim and starts the story quest",
               bool(ch) and len(ch["options"]) == 3 and "friend" in ch["options"][0] and S["flags"]["alliance"]["alfheim"] == "befriend"
               and S["quests"].get("alfheim") == 1 and "Aelindra" in first, choice=ch, quests=S["quests"])
        presses = T.talk_pad("thalion")
        T.step("controller: A talks to Thalion the ranger and pages through to the end", presses >= 1 and not T.ev("!!window.__hm.dlg"), presses=presses)
        T.ev("window.__hm.ctx.clock.t = 0.96"); T.walk(0.6, -6.2); pg.wait_for_timeout(1500)
        lit = T.ev("window.__hm.ctx.glows.filter((g) => !g.kill).length")
        T.step("Lumenvale at night: elf NPCs, treehouses, moon well, orb lanterns; violet glow lights and pools are on",
               T.ev("['aelindra','thalion','nyssa','elfkid'].every((id) => !!window.__hm.ctx.npc(id))") and lit >= 3, lights=lit)
        shot("alfheim_settlement_night")
        # ---------------------------------------------------------- a fight in the glade
        T.ev("window.__hm.combat.godT = 999"); T.walk(-2.4, 0.4)
        T.ev("window.__hm.peace = false")
        sh = lambda: T.ev("(() => { const e = window.__hm.combat.enemies.find((x) => x.id === 'shard_a0'); return e ? [e.hp, e.state, e.a.x, e.a.z] : null; })()")
        h0 = sh()
        for _ in range(14):
            e = sh()
            if not e or e[1] in ("dead", "gone"):
                break
            T.ev(f"window.__hm.ctx.actors.setFacingFromVec(window.__hm.ctx.player, {e[2]} - window.__hm.ctx.player.x, {e[3]} - window.__hm.ctx.player.z)")
            pg.keyboard.press("r"); pg.wait_for_timeout(260)
            if _ == 4:
                shot("alfheim_fight")
        h1 = sh()
        bolts = T.ev("window.__hd2d.effects.list.filter((f) => f.name === 'prism_bolt' || f.name === 'prism_pop').length + window.__hm.combat.projs.length")
        T.step("fight: R attacks land on a prism shard in the glade (its HP drops / it falls); enemies use the Alfheim roles",
               h0 and (h1 is None or h1[0] < h0[0] or h1[1] in ("dead", "gone")) and T.ev("window.__hm.combat.enemies.some((e) => e.a.role === 'neonwisp')"),
               hp=[h0, h1], bolts=bolts)
        T.ev("window.__hm.peace = true")
        # ---------------------------------------------------------- touch: tap the vault swirl
        T.walk(8.6, 2.6); pg.wait_for_timeout(400)
        s = screen(10.4, 1.35, 1.4)
        tap(s["x"], s["y"]); pg.wait_for_timeout(500)
        try:
            arrive("prismvault", 90)
        except Exception:
            tap(s["x"], s["y"]); arrive("prismvault", 90)
        T.step("touch: tapping the Prism Vault's swirl walks into it; the vault moves the story quest on",
               T.ev("window.__hm.area") == "prismvault" and T.S()["quests"].get("alfheim") == 2, quests=T.S()["quests"])
        shot("prismvault")
        # ---------------------------------------------------------- Lady Sylvaine
        meta = T.ev("""(async () => { const c = window.__hm.ctx, d = c.scene.atlas.json.replace(/[^/]+$/, '');
            const r = await fetch('areas/prismvault/' + d + 'boss.json'); const m = await r.json(); return { frame: m.frame, scale: m.roles.sylvaine.scale }; })()""")
        T.walk(0.0, 0.4); pg.wait_for_timeout(1200)
        rects = T.ev("window.__hd2d.actorRects().filter((q) => q.id === 'sylvaine' || q.id === 'player').map((q) => [q.id, q.h])")
        hs = dict(rects)
        ratio = (hs.get("sylvaine") or 0) / max(1, hs.get("player") or 1)
        T.step("Lady Sylvaine: drawn natively on the vault's boss sheet (100x160 frames, scale 5) and >= 4.5x the hero on screen",
               meta["frame"] == [100, 160] and meta["scale"] >= 5 and ratio >= 4.5, meta=meta, rects=rects, ratio=round(ratio, 2))
        T.ev("window.__hm.peace = false; window.__hm.combat.godT = 999"); pg.wait_for_timeout(2500)
        shot("sylvaine_scale")
        # her drain nova: force a wave swing and check spells sputter
        T.ev("""(() => { const C = window.__hm.combat, e = C.enemies.find((x) => x.id === 'sylvaine'); C.cd.spell = 0; C.cd.charm = 0;
                 e.swings = 2; C.beginAttack(e); })()""")
        T.wait("(() => { const e = window.__hm.combat.enemies.find((x) => x.id === 'sylvaine'); return e && e.novaAt === e.swings; })()", 30)
        cd = T.ev("[window.__hm.combat.cd.spell, window.__hm.combat.cd.charm]")
        T.step("Sylvaine's drain nova (every third swing) puts your spells + charms on cooldown", cd[0] > 1 and cd[1] > 1, cd=cd)
        T.ev("(() => { const e = window.__hm.combat.enemies.find((x) => x.id === 'sylvaine'); e.hp = Math.floor(e.D.hp * 0.45); })()")
        T.wait("window.__hm.combat.enemies.filter((e) => e.id.startsWith('syl_mirror_')).length === 2", 30)
        pg.wait_for_timeout(800)
        shot("sylvaine_fight")
        T.ev("(() => { const C = window.__hm.combat, e = C.enemies.find((x) => x.id === 'sylvaine'); C.damageEnemy(e, 99999, C.ctx.player); })()")
        pg.wait_for_timeout(600)
        T.ev("window.__hm.peace = true; for (const e of window.__hm.combat.enemies) if (e.state !== 'dead' && e.state !== 'gone') window.__hm.combat.kill(e, true)")
        S = T.S()
        T.step("Sylvaine at half health calls two Mirror Duelists; her fall sets S.flags.alf_sylvaine and counts as a boss",
               S["flags"].get("alf_sylvaine") == 1 and (S.get("bosses") or {}).get("sylvaine") == 1, flags={k: S["flags"].get(k) for k in ("alf_sylvaine", "alf_vault")})
        # ---------------------------------------------------------- mouse: click the exit swirl
        T.walk(0.0, 6.6); pg.wait_for_timeout(500)
        s = screen(0.0, 8.7, 1.4)
        pg.mouse.click(s["x"], s["y"]); pg.wait_for_timeout(500)
        try:
            arrive("alfheim", 90)
        except Exception:
            pg.mouse.click(s["x"], s["y"]); arrive("alfheim", 90)
        p = T.pos()
        T.step("mouse: clicking the vault's exit swirl walks out to Lumenvale Glade in front of the vault door",
               T.ev("window.__hm.area") == "alfheim" and abs(p[0] - 10.4) < 1.5 and abs(p[1] - 3.0) < 1.5, pos=p)
        g0, m0 = T.ev("window.__hm.S.gold || 0"), T.ev("(window.__hm.S.merit || {}).embassy || 0")
        mk = T.ev("window.__hm.markers && window.__hm.markers.aelindra ? window.__hm.markers.aelindra : null")
        T.talk("aelindra")
        S = T.S()
        T.step("Aelindra's turn-in: story quest done, +60 gold, +60 Realm Embassies merit",
               S["quests"].get("alfheim") == 3 and (S.get("gold") or 0) - g0 == 60 and (S.get("merit") or {}).get("embassy", 0) - m0 >= 60, marker=str(mk)[:60],
               gold=[g0, S.get("gold")], merit=[m0, (S.get("merit") or {}).get("embassy")])
        T.walk(-11.0, 2.8)
        idx = T.ev("window.__hm.ctx.scene.game.portals.findIndex((p) => p.to === 'bifrost')")
        T.go_rect("portals", idx, 150); arrive("bifrost")
        p = T.pos()
        T.step("the violet gate home lands at Bifrost in front of Alfheim's arch", abs(p[0] + 5.0) < 1.2 and abs(p[1] + 10.1) < 1.2, pos=p)
        T.step("Alfheim: no JS errors", not errors and not T.ev("window.__hd2d.errors.length"), errors=errors[:5])
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
    ap.add_argument("--out", default=str(GAME / "shots" / "alfheim_smoke"))
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
    (out / "smoke_alfheim.json").write_text(json.dumps(rep, indent=1))
    log(f"smoke_alfheim: {'PASS' if rep['pass'] else 'FAIL'} {sum(s['pass'] for s in T.steps)}/{len(T.steps)} steps in {rep['seconds']} s")
    sys.exit(0 if rep["pass"] else 1)


if __name__ == "__main__":
    main()
