"""Hearthmoor smoke test: plays the whole game end to end in headless Chromium (SwiftShader WebGL2).

    python3 games/hearthmoor/tests/smoke.py [--out games/hearthmoor/tests/shots] [--simscale 4]

Real inputs where it matters: clicks on the title buttons, E presses to talk and page through dialogue, F to cast,
J for the quest log, K to save, page reload + Continue. Walking uses the game's own A* tap-to-walk (ctx.walkTo),
so exits, stairs, the moss-gate portal and pickups are reached the way a tap would reach them.
Covers: the hero picker (6 starters, keyboard + click), 3 errands (Warm Bread, Moonpetal Tea, Where's Pudding?),
both edge exits, the portal both ways, Pudding following across areas, spells learned as rewards,
combat in Mossglen (melee hits + crisp damage numbers, guard cuts damage, dodge-roll i-frames, class spell,
summon, cozy defeat + respawn), save v2 -> reload -> Continue (twice), v1 save migration, and no JS errors.
Input schemes: clicks / taps / keys while the assets load are swallowed (title not skipped, nothing queued);
a stubbed standard-mapping controller (navigator.getGamepads) hot-plugs with a toast, walks with analog speed and
the d-pad, talks with A, closes with B, attacks with X, casts with Y, switches spell with LB / RB, guards while
LT is held, summons with RT, dodges with B, zooms with the right stick, opens the log with Start, toggles the pad
with Select, hides the on-screen pad while used and Continues from the title; on a phone the floating stick lands
under the thumb, slides after the finger, mirrors with the left-handed flip, a quick tap in the stick zone and on
open ground still walks, pinch zooms, the action buttons (attack / jump / guard / roll / spell wheel / summon)
work, and the page never scrolls or zooms.
Writes screenshots + smoke.json. Exit 0 = pass.
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
STUB = (Path(__file__).resolve().parent / "gamepad_stub.js").read_text()
ARGS = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"]


# an open-ground point 1.8-3 m from the player, reachable by A*, on the bare canvas (not under the HUD or an NPC)
MOUSE_TARGET_JS = """(() => {
  const h = window.__hd2d, c = h.ctx, p = c.player;
  for (const r of [2.4, 1.8, 3.0]) for (let k = 0; k < 16; k++) {
    const a = k / 16 * Math.PI * 2, x = p.x + Math.cos(a) * r, z = p.z + Math.sin(a) * r;
    const path = h.path(x, z); if (!path || !path.length) continue;
    const e = path[path.length - 1]; if (Math.hypot(e[0] - x, e[1] - z) > 0.3) continue;
    const s = c.project(x, c.heightAt(x, z), z);
    if (s.x < 40 || s.y < 40 || s.x > innerWidth - 40 || s.y > innerHeight - 40) continue;
    const el = document.elementFromPoint(s.x, s.y); if (!el || el.tagName !== 'CANVAS') continue;
    const onActor = h.actorRects().some((q) => { if (!q.w || q.id === 'player') return false; const f = innerWidth / q.buf[0];
      return s.x > q.x * f - 14 && s.x < (q.x + q.w) * f + 14 && s.y > q.y * f - 14 && s.y < (q.y + q.h) * f + 14; });
    if (onActor) continue;
    return { x, z, sx: s.x, sy: s.y };
  }
  return null;
})()"""


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


class Smoke:
    def __init__(self, pg, out, log):
        self.pg, self.out, self.log, self.steps = pg, out, log, []

    def ev(self, js):
        return self.pg.evaluate(js)

    def step(self, name, ok, **info):
        self.steps.append({"step": name, "pass": bool(ok), **info})
        self.log(f"  [{'PASS' if ok else 'FAIL'}] {name} {json.dumps(info)[:200] if info else ''}")
        if not ok:
            raise AssertionError(name)

    def S(self):
        return self.ev("JSON.parse(JSON.stringify(window.__hm.S))")

    def wait(self, js, timeout=90):
        self.pg.wait_for_function(js, timeout=timeout * 1000)

    def idle(self, timeout=90):
        self.wait("window.__hm.ctx && !window.__hm.busy && window.__hd2d && window.__hd2d.ready", timeout)

    def shot(self, name):
        p = self.out / f"{name}.png"
        self.pg.screenshot(path=str(p), timeout=120000)
        return str(p)

    def walk(self, x, z, timeout=90):
        ok = self.ev(f"window.__hm.ctx.walkTo({x}, {z})")
        if ok is False:
            return False
        self.wait("!window.__hm.ctx || !window.__hm.ctx.walking() || window.__hm.busy", timeout)
        return True

    def pos(self):
        return self.ev("[window.__hm.ctx.player.x, window.__hm.ctx.player.z]")

    def talk(self, npc_id, keep_open=False):
        """walk up to an NPC and press E until the dialogue with that NPC has been read to the end"""
        for off in ((0, 1.0), (1.0, 0), (-1.0, 0), (0, -1.0), (0.7, 0.7), (-0.7, 0.7)):
            a = self.ev(f"(() => {{ const a = window.__hm.ctx.npc('{npc_id}'); return a ? [a.x, a.z] : null; }})()")
            if not a:
                raise AssertionError(f"no npc {npc_id} in {self.ev('window.__hm.area')}")
            self.walk(a[0] + off[0], a[1] + off[1])
            self.pg.keyboard.press("e")
            self.pg.wait_for_timeout(250)
            who = self.ev("window.__hm.dlg ? window.__hm.dlg.npc.id : null")
            if who == npc_id:
                break
            while self.ev("!!window.__hm.dlg"):
                self.pg.keyboard.press("Escape"); self.pg.wait_for_timeout(100)
        else:
            raise AssertionError(f"could not talk to {npc_id}")
        pages = self.ev("window.__hm.dlg.pages.length")
        first = self.ev("window.__hm.dlg.pages[0]")
        if keep_open:
            return pages, first
        self.read_all()
        return pages, first

    def read_all(self):
        n = 0
        while self.ev("!!window.__hm.dlg") and n < 40:
            self.pg.keyboard.press("e"); self.pg.wait_for_timeout(140); n += 1

    # ---------------------------------------------------------- controller (stubbed navigator.getGamepads)
    def btn(self, i, hold=120):
        """press and hold until the engine's next poll has seen it (slow SwiftShader frames), then release"""
        n0 = self.ev("window.__hd2d.padPresses || 0")
        self.ev(f"__padBtn({i}, 1)")
        self.pg.wait_for_timeout(hold)
        self.wait(f"(window.__hd2d.padPresses || 0) > {n0}", 20)
        p0 = self.ev("window.__hd2d.padPolls || 0")
        self.ev(f"__padBtn({i}, 0)")
        self.wait(f"(window.__hd2d.padPolls || 0) > {p0 + 1}", 20)    # the release has been polled too
        self.pg.wait_for_timeout(150)

    def talk_pad(self, npc_id):
        """walk up to an NPC and press A until the dialogue has been read to the end"""
        for off in ((0, 1.0), (1.0, 0), (-1.0, 0), (0, -1.0)):
            a = self.ev(f"(() => {{ const a = window.__hm.ctx.npc('{npc_id}'); return a ? [a.x, a.z] : null; }})()")
            self.walk(a[0] + off[0], a[1] + off[1])
            self.btn(0)
            if self.ev("window.__hm.dlg ? window.__hm.dlg.npc.id : null") == npc_id:
                break
            while self.ev("!!window.__hm.dlg"):
                self.btn(1)
        else:
            raise AssertionError(f"could not talk to {npc_id} with A")
        n = 0
        while self.ev("!!window.__hm.dlg") and n < 40:
            self.btn(0, 200); n += 1
        return n

    def go_rect(self, kind, idx=0, timeout=90):
        """walk into an exit / portal trigger and wait for the next area to finish loading"""
        area0 = self.ev("window.__hm.area")
        r = self.ev(f"window.__hm.ctx.scene.game.{kind}[{idx}].rect")
        self.ev(f"window.__hm.ctx.walkTo({(r[0] + r[2]) / 2}, {(r[1] + r[3]) / 2})")
        self.wait(f"window.__hm.area !== '{area0}' || window.__hm.busy", timeout)
        self.idle(timeout)
        self.pg.wait_for_timeout(400)
        return self.ev("window.__hm.area")


def run(out, simscale=4, size=(960, 540)):
    from playwright.sync_api import sync_playwright
    out.mkdir(parents=True, exist_ok=True)
    srv = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(GAME)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/index.html?nosw&peace&simscale={simscale}"
    lines, errors = [], []
    log = lambda s: (print(s, flush=True), lines.append(s))  # noqa: E731
    rep = {"url": url, "shots": {}}
    T_START = time.time()
    with sync_playwright() as p:
        b = p.chromium.launch(args=ARGS)
        ctx = b.new_context(viewport={"width": size[0], "height": size[1]})
        ctx.add_init_script(STUB)
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: errors.append(f"PAGEERROR {e}"))
        pg.on("console", lambda m: errors.append(f"console.error {m.text}") if m.type == "error" else None)
        T = Smoke(pg, out, log)
        try:
            # ---------------------------------------------------------- title -> new game
            # ---------------------------------------------------------- loading gate: input while assets load is ignored
            held, hold = [], [True]
            pg.route("**/*.glb", lambda route: held.append(route) if hold[0] else route.continue_())
            pg.goto(url, wait_until="commit")
            T.wait("window.__hd2dGate && document.getElementById('boot') && document.getElementById('btnNew')", 60)
            pg.wait_for_timeout(500)
            during = T.ev("[window.__hd2dGate.loading, getComputedStyle(document.getElementById('boot')).display !== 'none']")
            nb = T.ev("(() => { const r = document.getElementById('btnNew').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; })()")
            for i in range(5):
                pg.mouse.click(nb[0], nb[1]); pg.mouse.click(size[0] * (0.3 + 0.1 * i), size[1] * 0.6)
                pg.keyboard.press(["Enter", " ", "n", "e", "j"][i]); pg.wait_for_timeout(80)
            hold[0] = False
            for rt in held:
                rt.continue_()
            T.wait("window.__hm && window.__hm.ready && window.__hd2d && window.__hd2d.ready", 120)
            pg.wait_for_timeout(800)
            T.step("clicks + keys during loading are swallowed (title not skipped, nothing queued)",
                   all(during) and T.ev("window.__hm.title && !document.getElementById('titlescreen').hidden && !window.__hm.log && !window.__hd2d.walking()")
                   and T.ev("window.__hd2dGate.swallowed") > 0 and len(held) > 0,
                   held=len(held), swallowed=T.ev("window.__hd2dGate.swallowed"), during=during)
            T.step("title screen shows, no save yet", T.ev("!document.getElementById('titlescreen').hidden && document.getElementById('btnCont').hidden"))
            pg.click("#btnNew")
            T.wait("window.__hm.picking && document.querySelectorAll('#cards .card').length === 6", 30)
            pg.wait_for_timeout(700)
            cards = T.ev("[...document.querySelectorAll('#cards .card b')].map((b) => b.textContent)")
            rep["shots"]["hero_picker"] = T.shot("hero_picker")
            pg.keyboard.press("ArrowRight"); pg.keyboard.press("ArrowRight"); pg.keyboard.press("ArrowRight")   # -> Stormborn
            pg.wait_for_timeout(300)
            sel = T.ev("window.__hm.picker.state().id")
            detail = T.ev("document.getElementById('heroDetail').textContent")
            T.step("hero picker: 6 starters with origin, mortal / demigod, blurb; arrows choose", cards == ["Wildcaller", "Runeguard", "Seer", "Stormborn", "Grovekeeper", "Cinderknight"]
                   and sel == "stormborn" and "Child of thunder" in detail and "demigod" in detail and "Chain Lightning" in detail, cards=cards, sel=sel)
            pg.keyboard.press("m"); pg.wait_for_timeout(150)
            m1, tip = T.ev("window.__hm.picker.state().mode"), T.ev("document.getElementById('pickModeTip').textContent")
            pg.keyboard.press("m"); pg.keyboard.press("m"); pg.wait_for_timeout(150)
            T.step("hero picker: M cycles the mode (Story / Adventurer / Hero) with a tip", m1 == "hero" and "Hero mode" in tip
                   and T.ev("window.__hm.picker.state().mode") == "adventurer", mode=m1)
            pg.click("#btnBegin")
            T.idle()
            T.wait("window.__hm.asking && !document.getElementById('autolv').hidden", 30)
            pg.wait_for_timeout(400)
            rep["shots"]["auto_level_popup"] = T.shot("auto_level_popup")
            pg.keyboard.press("ArrowRight"); pg.wait_for_timeout(100); pg.keyboard.press("Enter"); pg.wait_for_timeout(300)
            T.step("new game asks 'Auto level? Yes / No' (No = manual)", not T.ev("window.__hm.asking") and T.ev("window.__hm.S.autoLevel") is False and T.ev("window.__hm.S.mode") == "adventurer"
                   and T.ev("window.__hm.S.lv") == 1 and T.ev("window.__hm.S.stats.might") == 7)
            S = T.S()
            T.step("new game in Hearthmoor Plaza as the chosen hero", T.ev("window.__hm.area") == "plaza" and not T.ev("window.__hm.title") and S["quests"] == {"bread": 0, "tea": 0, "cat": 0}
                   and S["cls"] == "stormborn" and T.ev("window.__hm.ctx.player.role") == "stormborn" and T.ev("window.__hm.slots()") == ["chain_lightning", "sparkle_burst"],
                   cls=S["cls"], slots=T.ev("window.__hm.slots()"))
            T.step("quest tags over Marla and Tib", T.ev("Object.keys(window.__hm.markers).sort().join()") == "baker,kid")
            rep["shots"]["plaza"] = T.shot("plaza")

            # ---------------------------------------------------------- errand 1 + 3 start in the plaza
            pages, first = T.talk("baker")
            S = T.S()
            T.step("Marla gives the warm bread errand", S["quests"]["bread"] == 1 and S["inv"].get("loaf") == 1, pages=pages, line=first[:60])
            T.talk("kid")
            T.step("Tib asks you to find Pudding", T.S()["quests"]["cat"] == 1)
            T.step("plaza has no Pudding (she is lost)", T.ev("!window.__hm.ctx.npc('cat')"))
            T.talk("elder")

            # ---------------------------------------------------------- south lane -> Bakery Lane
            area = T.go_rect("exits")
            T.step("edge exit: plaza -> Bakery Lane (fade)", area == "lane", spawn=T.pos())
            pages, first = T.talk("innkeeper")
            S = T.S()
            T.step("deliver bread to Bram: errand 1 done", S["quests"]["bread"] == 3 and not S["inv"].get("loaf") and S["inv"].get("coin") == 3
                   and "hearth_flame" in S["spells"], line=first[:60])
            # Wren: dialogue box + quest log together for the report shot
            T.talk("herbalist", keep_open=True)
            pg.wait_for_timeout(1200)
            pg.keyboard.press("j")
            pg.wait_for_timeout(500)
            T.step("quest log opens over the dialogue", T.ev("!document.getElementById('log').hidden && !document.getElementById('dlg').hidden"))
            rep["shots"]["dialogue_questlog"] = T.shot("dialogue_questlog")
            pg.keyboard.press("j")
            pg.wait_for_timeout(200)
            T.read_all()
            T.step("Wren gives the moonpetal errand", T.S()["quests"]["tea"] == 1)
            # cast: Q to the new charm, F to cast
            pg.keyboard.press("q"); pg.wait_for_timeout(200)
            near = "window.__hd2d.effects.list.filter((f) => Math.hypot(f.x - window.__hm.ctx.player.x, f.z - window.__hm.ctx.player.z) < 2.5).length"
            n0 = T.ev(near)
            cast = T.ev("window.__hd2d.spellName()")
            pg.keyboard.press("f"); pg.wait_for_timeout(150)
            casting = T.ev("window.__hm.ctx.player.castT > 0")
            pg.wait_for_timeout(500)
            T.step("spell cast key (F) still works", casting or T.ev(near) > n0, cast=cast, casting=casting)
            # ---------------------------------------------------------- Bluetooth controller (standard mapping, stubbed)
            T.ev("__padPlug(true)"); pg.wait_for_timeout(700)
            T.step("controller hot-plug: 'controller connected' toast", "controller connected" in T.ev("document.getElementById('toast').textContent")
                   and T.ev("!document.getElementById('toast').hidden"))
            pa = T.pos()
            T.ev("__padAxes(0.45, 0)"); pg.wait_for_timeout(600)
            half = T.ev("[window.__hm.ctx.player.speedScale, window.__hm.ctx.player.running]")
            T.ev("__padAxes(1, 0)"); pg.wait_for_timeout(600)
            full = T.ev("[window.__hm.ctx.player.speedScale, window.__hm.ctx.player.running]")
            T.ev("__padAxes(0, 0)"); pg.wait_for_timeout(300)
            pb = T.pos()
            ctrl = T.ev("window.__hd2d.gamepad().ctrl")
            T.step("left stick walks with analog speed (half tilt walks slower, full tilt runs)", pb[0] - pa[0] > 0.3 and half[0] < 0.8 and not half[1] and full[1] and ctrl,
                   half=half, full=full, moved=[round(pb[0] - pa[0], 2), round(pb[1] - pa[1], 2)])
            T.ev("__padBtn(13, 1)"); pg.wait_for_timeout(700); T.ev("__padBtn(13, 0)"); pg.wait_for_timeout(250)
            pc = T.pos()
            if abs(pc[1] - pb[1]) + abs(pc[0] - pb[0]) <= 0.2:   # down blocked by a fence corner on slow runs: try d-pad up
                T.ev("__padBtn(12, 1)"); pg.wait_for_timeout(700); T.ev("__padBtn(12, 0)"); pg.wait_for_timeout(250)
                pc = T.pos()
            T.step("d-pad walks", abs(pc[1] - pb[1]) + abs(pc[0] - pb[0]) > 0.2, moved=[round(pc[0] - pb[0], 2), round(pc[1] - pb[1], 2)])
            pg.wait_for_timeout(1300)   # charm cooldown from the F cast above
            n0 = T.ev(near)
            k0 = T.ev("window.__hd2d.padPresses || 0")
            T.ev("__padBtn(3, 1)"); T.wait(f"(window.__hd2d.padPresses || 0) > {k0}", 20)
            casting = T.ev("window.__hm.ctx.player.castT > 0"); pg.wait_for_timeout(150); T.ev("__padBtn(3, 0)"); pg.wait_for_timeout(300)
            T.step("Y casts", casting or T.ev(near) > n0, casting=casting)
            n_cyc = T.ev("window.__hm.ctx.spellCycle().length")
            pg.wait_for_timeout(400)   # let the engine see Y up before the next press (slow frames under load)
            k0 = T.ev("window.__hd2d.padPresses || 0")
            T.ev("__padBtn(3, 1)"); T.wait(f"(window.__hd2d.padPresses || 0) > {k0}", 20)
            T.wait("window.__hm.wheel.state().open", 10)
            w_open = T.ev("window.__hm.wheel.state().open")
            T.ev("__padAxes(1, 0)"); pg.wait_for_timeout(250)
            T.wait("window.__hm.wheel.state().sel >= 0", 10)
            w_sel = T.ev("window.__hm.wheel.state().sel")
            T.ev("__padBtn(3, 0)"); pg.wait_for_timeout(300); T.ev("__padAxes(0, 0)"); pg.wait_for_timeout(200)
            T.step("hold Y: slow-time spell wheel, stick picks, release casts", w_open and (n_cyc < 2 or (w_sel == 1 and T.ev("window.__hm.ctx.spellIndex()") == 1))
                   and not T.ev("window.__hm.wheel.state().open"), open=w_open, sel=w_sel, slots=n_cyc)
            T.ev("window.__hm.ctx.selectSpell(0)")
            k0 = T.ev("window.__hd2d.padPresses || 0")
            T.ev("__padBtn(2, 1)"); T.wait(f"(window.__hd2d.padPresses || 0) > {k0}", 20)
            swing = T.ev("window.__hd2d.actorState().act"); pg.wait_for_timeout(120); T.ev("__padBtn(2, 0)"); pg.wait_for_timeout(500)
            T.step("X attacks", swing == "attack", act=swing)
            s0 = T.ev("window.__hd2d.spellName()"); T.btn(5); s1 = T.ev("window.__hd2d.spellName()"); T.btn(4); s2 = T.ev("window.__hd2d.spellName()")
            T.btn(4); s3 = T.ev("window.__hd2d.spellName()"); T.btn(5)
            T.step("RB next spell, LB previous spell", s1 != s0 and s2 == s0 and s3 != s0, spells=[s0, s1, s2, s3])
            # LT is a real hold-to-guard now (zoom moved to the right stick: no trigger is mapped twice)
            k0 = T.ev("window.__hd2d.padPresses || 0")
            T.ev("__padBtn(6, 1)"); T.wait(f"(window.__hd2d.padPresses || 0) > {k0}", 20); pg.wait_for_timeout(700)
            g1 = T.ev("window.__hd2d.actorState().act")
            p0 = T.ev("window.__hd2d.padPolls || 0"); T.ev("__padBtn(6, 0)"); T.wait(f"(window.__hd2d.padPolls || 0) > {p0 + 1}", 20); pg.wait_for_timeout(600)
            g2 = T.ev("window.__hd2d.actorState().act")
            T.step("LT held guards, letting go drops the guard", g1 == "defend" and g2 != "defend", held=g1, after=g2)
            T.btn(7); pg.wait_for_timeout(300)
            summ = T.ev("window.__hm.combat.qa().summon")
            T.step("RT summons the hero's companion", summ and summ["role"] == "stormsprite", summon=summ)
            T.ev("window.__hm.combat.st = 100")
            T.btn(1, hold=60)
            st = T.ev("window.__hm.combat.st")
            T.step("B dodges in the field (roll costs stamina)", st < 100, stamina=st)
            T.btn(9); log_open = T.ev("window.__hm.log"); T.btn(1); log_closed = not T.ev("window.__hm.log")
            T.step("Start opens the quest log, B closes it", log_open and log_closed)
            z0 = T.ev("window.__hd2d.camState().dist")
            rs = lambda v: T.ev(f"(() => {{ window.__fakePad.axes[3] = {v}; window.__fakePad.timestamp = performance.now(); }})()")  # noqa: E731
            rs(-1); pg.wait_for_timeout(700); rs(0); pg.wait_for_timeout(200); z1 = T.ev("window.__hd2d.camState().dist")
            rs(1); pg.wait_for_timeout(1400); rs(0); pg.wait_for_timeout(200); z2 = T.ev("window.__hd2d.camState().dist")
            T.step("right stick up zooms in, down zooms out (inside the limits)", z1 < z0 - 0.3 and z2 > z1 + 0.3 and 23 - 1e-3 <= min(z1, z2) and max(z1, z2) <= 40 + 1e-3, dist=[round(z0, 2), round(z1, 2), round(z2, 2)])
            pad_hidden = T.ev("getComputedStyle(document.getElementById('pad')).display === 'none' || document.getElementById('pad').hidden")
            T.btn(8); pad_sel = T.ev("[document.body.classList.contains('padon'), getComputedStyle(document.getElementById('pad')).display !== 'none' && !document.getElementById('pad').hidden]")
            T.btn(8); pad_off = T.ev("document.body.classList.contains('padon')")
            T.step("Select toggles the on-screen pad (shown even in controller mode)", pad_hidden and pad_sel == [True, True] and not pad_off, sel=pad_sel)
            pages = T.talk_pad("musician")
            T.step("A talks to Pip and pages through to the end", T.ev("!window.__hm.dlg"), presses=pages)
            T.btn(0)
            opened = T.ev("!!window.__hm.dlg"); T.btn(1)
            T.step("B closes a dialogue", opened and T.ev("!window.__hm.dlg"))
            rep["shots"]["lane_controller"] = T.shot("lane_controller")
            # all schemes together: with the controller still connected, keys walk, a mouse click walks, the wheel zooms
            k0 = T.pos()
            pg.keyboard.down("d"); pg.wait_for_timeout(700); pg.keyboard.up("d"); pg.wait_for_timeout(200)
            k1 = T.pos()
            tgt = T.ev(MOUSE_TARGET_JS)
            clicked = False
            if tgt:
                pg.mouse.click(tgt["sx"], tgt["sy"]); pg.wait_for_timeout(300)
                clicked = T.ev("window.__hm.ctx.walking()") or ((T.pos()[0] - tgt["x"]) ** 2 + (T.pos()[1] - tgt["z"]) ** 2) ** 0.5 < 0.4
                T.wait("!window.__hm.ctx.walking()", 30)
            w0 = T.ev("window.__hd2d.camState().dist")
            pg.mouse.move(size[0] / 2, size[1] / 2); pg.mouse.wheel(0, 600); pg.wait_for_timeout(400)
            w1 = T.ev("window.__hd2d.camState().dist")
            T.step("keyboard, mouse click-to-walk and wheel zoom still work with a controller connected", abs(k1[0] - k0[0]) + abs(k1[1] - k0[1]) > 0.2 and clicked and w1 > w0 + 0.3,
                   keys_moved=[round(k1[0] - k0[0], 2), round(k1[1] - k0[1], 2)], click=tgt and [round(tgt["x"], 2), round(tgt["z"], 2)], wheel=[round(w0, 2), round(w1, 2)])
            T.ev("__padPlug(false)"); pg.wait_for_timeout(600)
            T.step("controller unplugged: toast, controller mode off", "disconnected" in T.ev("document.getElementById('toast').textContent")
                   and not T.ev("document.body.classList.contains('ctrl')"))
            rep["shots"]["lane"] = T.shot("lane")

            # ---------------------------------------------------------- back up to the plaza, through the moss gate
            area = T.go_rect("exits")
            T.step("edge exit: Bakery Lane -> plaza", area == "plaza", spawn=T.pos())
            r = T.ev("window.__hm.ctx.scene.game.portals[0].rect")
            T.walk((r[0] + r[2]) / 2, r[3] + 1.6)
            T.ev("window.__hd2d.ctx && 0")
            pg.mouse.move(size[0] / 2, size[1] / 2)
            for _ in range(6):
                pg.mouse.wheel(0, -600); pg.wait_for_timeout(120)
            pg.wait_for_timeout(600)
            rep["shots"]["portal_closeup"] = T.shot("portal_closeup")
            area = T.go_rect("portals")
            T.step("portal: plaza -> Mossglen", area == "mossglen", spawn=T.pos())

            # ---------------------------------------------------------- Mossglen: moonpetals + Pudding
            for i in range(3):
                f = T.ev(f"(() => {{ const f = window.__hm.ctx.fx['petal_{i}']; return f ? [f.x, f.z] : null; }})()")
                T.walk(f[0], f[1])
                pg.wait_for_timeout(300)
            S = T.S()
            T.step("picked 3 moonpetals (errand 2 ready)", S["inv"].get("moonpetal") == 3 and S["quests"]["tea"] == 2, picked=sorted(S["picked"]))
            T.talk("keeper")
            T.talk("cat")
            S = T.S()
            T.step("found Pudding: she follows you", S["cat"] == "follow" and S["quests"]["cat"] == 2 and T.ev("window.__hm.ctx.npc('cat').behavior") == "follow")
            rep["shots"]["mossglen"] = T.shot("mossglen")

            # ---------------------------------------------------------- leveling: the bread errand gave XP; manual spend + a skill
            S = T.S()
            lv = S["lv"]
            T.step("errands give XP: level 2+ with 2 stat points and a skill point per level", lv >= 2 and S["free"] == 2 * (lv - 1) and S["sp"] == lv - 1, lv=lv, xp=S["xp"], free=S["free"], sp=S["sp"])
            pg.keyboard.press("i"); T.wait("window.__hm.heroUI", 10); pg.wait_for_timeout(300)
            rep["shots"]["hero_stats"] = T.shot("hero_stats")
            m0 = S["stats"]["might"]
            pg.keyboard.press("Enter"); pg.wait_for_timeout(200)            # first row = Might
            pg.keyboard.press("ArrowRight"); pg.wait_for_timeout(200)       # Skills tab
            pg.keyboard.press("ArrowDown"); pg.keyboard.press("Enter"); pg.wait_for_timeout(300)   # Tempest: Forked Bolt
            rep["shots"]["hero_skills"] = T.shot("hero_skills")
            S = T.S()
            T.step("hero screen (I): spend a stat point, learn a tier-I skill (keys)", S["stats"]["might"] == m0 + 1 and S["free"] == 2 * (lv - 1) - 1
                   and S["skills"].get("sb_tempest") == 1 and S["sp"] == lv - 2, stats=S["stats"], skills=S["skills"])
            # Part 4: tiers II-III (tier II needs tier I + Lv 5; the tier-III capstone needs tier II + Lv 10 and costs 2)
            T.ev("window.__qaKeep = { lv: window.__hm.S.lv, sp: window.__hm.S.sp, xp: window.__hm.S.xp }; window.__hm.S.lv = 10; window.__hm.S.sp = 3; window.__hm.heroUI && window.__hm.drawHero && window.__hm.drawHero()")
            lk = T.ev("(() => { const P = window.__hm.PR, S = window.__hm.S, t = P.TREES[S.cls]; return [P.lockOf(S, t.find((n) => n.id === 'sb_tempest3')), t.length, t.filter((n) => n.tier === 3).length]; })()")
            for _ in range(3): pg.keyboard.press("ArrowDown")
            pg.keyboard.press("Enter"); pg.wait_for_timeout(250)
            for _ in range(3): pg.keyboard.press("ArrowDown")
            pg.keyboard.press("Enter"); pg.wait_for_timeout(300)
            rep["shots"]["hero_skill_tiers"] = T.shot("hero_skill_tiers")
            tiers = T.ev("(() => { const S = window.__hm.S, M = window.__hm.combat.M; return { t2: S.skills.sb_tempest2, t3: S.skills.sb_tempest3, sp: S.sp, jumps: M.chainJumps, spellCd: M.spellCd,"
                         " hdrs: document.querySelectorAll('#heroBody .tierhd').length }; })()")
            T.step("skill tiers II-III: 9 nodes per hero; the capstone is locked until tier II, then learned by keys (2 points) and its mods apply",
                   lk[0].startswith("needs") and lk[1] == 9 and lk[2] == 3 and tiers["t2"] == 1 and tiers["t3"] == 1 and tiers["sp"] == 0 and tiers["jumps"] == 3
                   and abs(tiers["spellCd"] - 0.15) < 1e-6 and tiers["hdrs"] == 3, lock=lk, tiers=tiers)
            T.ev("(() => { const S = window.__hm.S, k = window.__qaKeep; delete S.skills.sb_tempest2; delete S.skills.sb_tempest3; S.lv = k.lv; S.sp = k.sp; S.xp = k.xp; })()")
            pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
            pg.keyboard.press("b"); pg.wait_for_timeout(300)
            sb_open = T.ev("window.__hm.heroUI && document.querySelectorAll('#heroBody .row.sbslot').length === 4")
            before = T.ev("window.__hm.slots()")
            pg.keyboard.press("ArrowDown"); pg.keyboard.press("Enter"); pg.wait_for_timeout(300)
            after = T.ev("window.__hm.slots()"); cyc = T.ev("window.__hm.ctx.spellCycle()")
            rep["shots"]["spellbook"] = T.shot("spellbook")
            T.step("spellbook (B): 4 slots, Enter changes slot 2, the cast cycle follows", sb_open and after != before and cyc == after, before=before, after=after)
            pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
            hp_max = T.ev("window.__hm.combat.maxHp()")
            T.step("stats feed combat (chain lightning +1 leap, HP from Vigor)", T.ev("window.__hm.combat.M.chainJumps") == 1 and hp_max >= 120, hp=hp_max)

            # ---------------------------------------------------------- combat in Mossglen (enemies wake up)
            q0 = T.ev("window.__hm.combat.qa()")
            roles = sorted({e["role"] for e in q0["enemies"]})
            T.step("Mossglen has a stone golem, a cold-fire wraith and a skeleton swordsman", {"golem", "wraith", "skeleton"} <= set(roles), roles=roles)
            T.ev("window.__hm.peace = false")
            # stand left of the golem, facing it, and swing (R)
            T.ev("(() => { const c = window.__hm.ctx, p = c.player, g = c.npc('golem_0'); p.x = g.x - 1.1; p.z = g.z; p.y = c.heightAt(p.x, p.z); p.facing = 'right'; c.stopWalk(); })()")
            pg.wait_for_timeout(400)
            hp0 = T.ev("window.__hm.combat.enemies.find((e) => e.id === 'golem_0').hp")
            pg.keyboard.press("r"); pg.wait_for_timeout(450)
            nums = T.ev("document.querySelectorAll('#fxlayer .dmgnum').length")
            pg.keyboard.press("r"); pg.wait_for_timeout(450)
            hp1 = T.ev("window.__hm.combat.enemies.find((e) => e.id === 'golem_0').hp")
            T.step("R swings: the golem takes damage, a crisp pixel damage number pops", hp1 < hp0 and nums > 0, hp=[hp0, hp1], numbers=nums)
            pg.keyboard.press("1"); pg.wait_for_timeout(100); pg.keyboard.press("f"); pg.wait_for_timeout(700)
            hp2 = T.ev("window.__hm.combat.enemies.find((e) => e.id === 'golem_0').hp")
            T.step("class spell (Chain Lightning) strikes and goes on cooldown", hp2 < hp1 and T.ev("window.__hm.combat.cd.spell") > 0, hp=hp2)
            pools = T.ev("window.__hm.glow.pools.length"); glows = T.ev("window.__hm.ctx.glows.filter((g) => isFinite(g.life)).length")
            T.step("glow pass: the spell leaves a light pool (decal + glitter + point light)", pools > 0 and glows > 0, pools=pools, glows=glows)
            t_keep = T.ev("window.__hd2d.clock.t")
            T.ev("window.__hd2d.setTime(0.95)"); pg.wait_for_timeout(500)
            toads = T.ev("window.__hm.glow.toads.length")
            T.ev("(() => { const c = window.__hm.ctx, p = c.player, t = window.__hm.glow.toads[0]; p.x = t.x + 0.6; p.z = t.z + 0.3; p.y = c.heightAt(p.x, p.z); c.stopWalk(); })()")
            pg.wait_for_timeout(400)
            lit = T.ev("window.__hm.glow.lit && !document.getElementById('litTag').hidden")
            shy = T.ev("(() => { const g = window.__hm.glow, t = g.toads[0]; return g.litAt(t.x, t.z) && !g.litAt(t.x + 3, t.z + 3); })()")
            T.step("night: toadstools glow, standing by one makes you glowlit (light zones)", toads == 6 and lit and shy, toads=toads, lit=lit)
            T.ev("window.__hd2d.setTime(0.5)"); pg.wait_for_timeout(500)   # midday (t_keep itself may already be night)
            T.step("dawn: the toadstools dither away", T.ev("window.__hm.glow.toads.length") == 0)
            T.ev(f"window.__hd2d.setTime({t_keep if 0.25 < t_keep < 0.8 else 0.5})"); pg.wait_for_timeout(200)
            # ---------------------------------------------------------- loot, gear page, faint penalty, modes
            T.ev("window.__hm.peace = true")
            T.ev("(() => { const c = window.__hm.ctx, p = c.player, L = window.__hm.loot, LO = window.__hm.LO; for (let r = 0; r < 5; r++) L.drop(p.x + 1.2 + r * 0.7, p.z + 0.9, { item: LO.makeItem(3, r, LO.SLOTS[r % 3]) }); L.drop(p.x + 1.2, p.z + 1.8, { gold: 7 }); })()")
            pg.wait_for_timeout(500)
            beams, auras = T.ev("document.querySelectorAll('#fxlayer .loot .beam').length"), T.ev("document.querySelectorAll('#fxlayer .loot .aura').length")
            rep["shots"]["loot_beams"] = T.shot("loot_beams")
            T.step("loot: five rarity beams (Epic + Legendary auras) and a gold pile", beams == 5 and auras == 2, beams=beams, auras=auras)
            g0, b0 = T.ev("window.__hm.S.gold"), T.ev("window.__hm.S.bag.length")
            for d in T.ev("window.__hm.loot.qa()"):
                T.ev(f"(() => {{ const c = window.__hm.ctx, p = c.player; p.x = {d['x']}; p.z = {d['z']}; p.y = c.heightAt(p.x, p.z); c.stopWalk(); }})()"); pg.wait_for_timeout(250)
            pg.wait_for_timeout(300)
            S = T.S()
            T.step("walking over drops puts items in the bag and gold in the purse", len(S["bag"]) == b0 + 5 and S["gold"] == g0 + 7, bag=len(S["bag"]), gold=S["gold"])
            chip = T.ev("(document.querySelector('#bag .gearchip') || {}).textContent || ''")
            T.step("bag chip shows the gear count and gold", chip.strip() == f"⚔ {len(S['bag'])}" and T.ev("!!document.querySelector('#bag .goldchip')"), chip=chip)
            hp_a = T.ev("window.__hm.combat.maxHp()")
            pg.keyboard.press("g"); pg.wait_for_timeout(300)
            for _ in range(3): pg.keyboard.press("ArrowDown")
            idx = T.ev("(() => window.__hm.S.bag.findIndex((it) => it.slot === 'armor'))()")
            for _ in range(idx): pg.keyboard.press("ArrowDown")
            pg.keyboard.press("Enter"); pg.wait_for_timeout(300)
            rep["shots"]["gear_page"] = T.shot("gear_page")
            S = T.S()
            T.step("gear page (G): Enter equips armor from the bag, max HP goes up", bool(S["gear"].get("armor")) and T.ev("window.__hm.combat.maxHp()") > hp_a,
                   armor=(S["gear"].get("armor") or {}).get("name"), hp=[hp_a, T.ev("window.__hm.combat.maxHp()")])
            pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
            T.ev("window.__hm.S.gold = 50; window.__hm.S.mode = 'adventurer'; window.__hm.combat.down()"); pg.wait_for_timeout(2400)
            S = T.S(); purse = S.get("purse") or {}
            T.ev(f"(() => {{ const c = window.__hm.ctx, p = c.player; p.x = {purse.get('x', 0)}; p.z = {purse.get('z', 0)}; p.y = c.heightAt(p.x, p.z); c.stopWalk(); }})()"); pg.wait_for_timeout(600)
            T.step("faint (Adventurer): 10% of gold drops where you fell; walking back recovers it", S["gold"] == 45 and purse.get("gold") == 5 and T.S()["gold"] == 50 and not T.S().get("purse"),
                   gold=[S["gold"], T.S()["gold"]], purse=purse)
            T.ev("window.__hm.S.mode = 'story'; window.__hm.combat.down()"); pg.wait_for_timeout(2400)
            T.step("Story mode: fainting costs nothing", T.S()["gold"] == 50 and not T.S().get("purse"))
            T.ev("window.__hm.S.mode = 'adventurer'; window.__hm.combat.godT = 0")
            # pathfinding: a skeleton below the terrace wall must go round by the stairs to reach you
            T.ev("(() => { const c = window.__hm.ctx, C = window.__hm.combat, p = c.player; window.__hm.peace = false; C.godT = 0; p.iframes = 99;"
                 " p.x = 5.0; p.z = -4.0; p.y = c.heightAt(p.x, p.z); c.stopWalk(); const e = C.enemies.find((x) => x.id === 'skeleton_0');"
                 " e.a.x = 6.0; e.a.z = 0.6; e.a.y = c.heightAt(6, 0.6); e.home = [6.0, 0.6]; e.state = 'chase'; e.path = null; })()")
            pg.wait_for_timeout(3500)
            sk = T.ev("(() => { const e = window.__hm.combat.enemies.find((x) => x.id === 'skeleton_0'); return { x: e.a.x, z: e.a.z, y: e.a.y, path: !!(e.path && e.path.length), state: e.state }; })()")
            T.ev("(() => { const C = window.__hm.combat; window.__hm.peace = true; window.__hm.ctx.player.iframes = 0; const e = C.enemies.find((x) => x.id === 'skeleton_0'); e.home = [5.0, 2.6]; e.state = 'home'; })()")
            T.step("pathfinding: a foe below the terrace wall routes via the stairs", sk["y"] > 0.3 or sk["x"] < 4.0, skeleton=sk)
            # ---------------------------------------------------------- stage 3: new foes, the Mossheart mini-boss, the Legendary aura
            roles3 = sorted({e["role"] for e in T.ev("window.__hm.combat.qa()")["enemies"]})
            T.step("Mossglen also has a frost golem, a skeleton mage and Mossheart (mini-boss)", {"icegolem", "skelmage", "eldergolem"} <= set(roles3), roles=roles3)
            chill = T.ev("(() => { const c = window.__hm.ctx, C = window.__hm.combat, p = c.player, e = C.enemies.find((x) => x.id === 'icegolem_0');"
                         " p.iframes = 0; C.godT = 0; C.st = C.maxSt(); p.act = null; p.x = e.a.x + 1.0; p.z = e.a.z; p.y = c.heightAt(p.x, p.z); c.stopWalk(); e.a.facing = 'right';"
                         " const h0 = window.__hm.S.hp, s0 = C.st; C.enemyStrike(e); return [h0 - window.__hm.S.hp, Math.round(s0 - C.st)]; })()")
            T.step("frost golem slam hurts and chills (drains stamina)", chill[0] > 0 and chill[1] >= 15, hurt=chill[0], stamina_lost=chill[1])
            bolt = T.ev("(() => { const c = window.__hm.ctx, C = window.__hm.combat, p = c.player, e = C.enemies.find((x) => x.id === 'skelmage_0');"
                        " p.x = e.a.x + 4; p.z = e.a.z; p.y = c.heightAt(p.x, p.z); c.stopWalk(); C.enemyStrike(e); return c.effects.list.some((f) => f.name === 'bolt'); })()")
            T.step("skeleton mage casts an arcane bolt from range", bolt)
            T.ev("(() => { const C = window.__hm.combat, c = window.__hm.ctx, p = c.player; C.heal(999, true); p.iframes = 99; window.__hm.peace = false; C.godT = 0;"
                 " const e = C.enemies.find((x) => x.id === 'mossheart'); p.x = e.a.x - 2.2; p.z = e.a.z; p.y = c.heightAt(p.x, p.z); c.stopWalk(); C.damageEnemy(e, 40, p); })()")
            pg.wait_for_timeout(700)
            boss = T.ev("(() => { const C = window.__hm.combat, e = C.enemies.find((x) => x.id === 'mossheart'), b = document.getElementById('bossbar');"
                        " return { state: e.state, light: !!e.light, bar: !!(b && !b.hidden), name: b ? b.firstChild.textContent : '', w: b ? b.querySelector('i').style.width : '' }; })()")
            rep["shots"]["boss_fight"] = T.shot("boss_fight")
            T.step("Mossheart: carries a rune light, a named boss bar shows when it fights", boss["light"] and boss["bar"] and "Mossheart" in boss["name"] and boss["w"] not in ("", "100%"), boss=boss)
            big = T.ev("(() => { const R = window.__hd2d.actorRects(), m = R.find((r) => r.id === 'mossheart'), p = R.find((r) => r.id === 'player'), C = window.__hm.combat, e = C.enemies.find((x) => x.id === 'mossheart');"
                       " return { sheet: m && m.sheet, mh: m && m.h / m.k, ph: p && p.h / p.k, r: e.a.r, scale: e.D.scale, pull: window.__hm.ctx.pull() }; })()")
            T.step("Mossheart is ~2.5x the hero, drawn natively on its own boss sheet; hitbox and camera framing scale with it",
                   big["sheet"] == "boss" and big["mh"] == 80 and big["ph"] == 32 and big["scale"] == 2.5 and big["r"] >= 0.7 and big["pull"] > 1.01, **big)
            T.ev("(() => { const C = window.__hm.combat, e = C.enemies.find((x) => x.id === 'mossheart'); window.__hm.peace = true; C.damageEnemy(e, 9999, window.__hm.ctx.player); })()")
            pg.wait_for_timeout(900)
            legs = [d for d in T.ev("window.__hm.loot.qa()") if d["rar"] == 4]
            T.step("Mossheart always drops a Legendary (and the boss bar goes away)", len(legs) >= 1 and T.ev("!document.getElementById('bossbar') || document.getElementById('bossbar').hidden"), drops=legs)
            cores = [d for d in T.ev("window.__hm.loot.qa()") if d.get("gem") == "golem_core"]
            T.step("Mossheart also drops a golem core (socket gem)", len(cores) >= 1, drops=cores)
            for d in cores:
                T.ev(f"(() => {{ const c = window.__hm.ctx, p = c.player; p.x = {d['x']}; p.z = {d['z']}; p.y = c.heightAt(p.x, p.z); c.stopWalk(); }})()"); pg.wait_for_timeout(500)
            T.step("walking over the core puts it in the gem pouch", (T.S().get("gems") or {}).get("golem_core", 0) >= 1, gems=T.S().get("gems"))
            nb = len(T.S()["bag"])
            for d in legs:
                T.ev(f"(() => {{ const c = window.__hm.ctx, p = c.player; p.x = {d['x']}; p.z = {d['z']}; p.y = c.heightAt(p.x, p.z); c.stopWalk(); }})()"); pg.wait_for_timeout(500)
            T.ev("(() => { const S = window.__hm.S, i = S.bag.findIndex((it) => it.rar === 4); if (i >= 0) window.__hm.LO.equip(S, i); })()")
            pg.wait_for_timeout(500)
            aura = T.ev("window.__hm.loot.auraOn() && !!document.querySelector('#fxlayer .loot.paura canvas')")
            rep["shots"]["legendary_aura"] = T.shot("legendary_aura")
            T.step("a Legendary equipped: a neon aura + rune light follow the hero", len(T.S()["bag"]) >= nb and aura, aura=aura)
            T.ev("(() => { const S = window.__hm.S; for (const k of ['weapon', 'armor', 'trinket']) if (S.gear[k] && S.gear[k].rar === 4) window.__hm.LO.unequip(S, k); window.__hm.ctx.player.iframes = 0; })()")
            pg.wait_for_timeout(300)
            T.step("unequipping the Legendary drops the aura", not T.ev("window.__hm.loot.auraOn()"))
            T.ev("(() => { const c = window.__hm.ctx, p = c.player, g = c.npc('golem_0'); p.x = g.x - 1.1; p.z = g.z; p.y = c.heightAt(p.x, p.z); p.facing = 'right'; c.stopWalk(); })()")
            T.ev("window.__hm.combat.cd.summon = 0"); pg.keyboard.press("v"); pg.wait_for_timeout(500)
            T.step("V summons the storm sprite", (T.ev("window.__hm.combat.qa().summon") or {}).get("role") == "stormsprite")
            rep["shots"]["mossglen_combat"] = T.shot("mossglen_combat")
            # Part 4 summon tiers: Skyherd II + III -> tier III radiant form (own sprite, light, sparkles); + capstone -> tier IV
            tq = "(() => { const C = window.__hm.combat; C.cd.summon = 0; C.doSummon(); return { ...C.qa().summon, hp0: C.summon.D.hp }; })()"
            t1 = T.ev(tq)
            T.ev("(() => { const S = window.__hm.S; S.skills.sb_herd = 1; S.skills.sb_herd2 = 1; })()")
            t3 = T.ev(tq); pg.wait_for_timeout(600)
            rep["shots"]["summon_tier3"] = T.shot("summon_tier3")
            T.ev("window.__hm.S.skills.sb_herd3 = 1")
            t4 = T.ev(tq)
            T.step("summon tiers: base I, tier III radiant storm sprite with its own light, tier IV (capstone) stronger still",
                   t1["tier"] == 1 and t1["role"] == "stormsprite" and not t1["light"] and t3["tier"] == 3 and t3["role"] == "stormsprite_r" and t3["light"]
                   and "III" in t3["name"] and t4["tier"] == 4 and t4["hp0"] > t3["hp0"] > t1["hp0"], t1=t1, t3=t3, t4=t4)
            T.ev("(() => { const S = window.__hm.S, C = window.__hm.combat; delete S.skills.sb_herd; delete S.skills.sb_herd2; delete S.skills.sb_herd3; C.cd.summon = 0; C.doSummon(); })()")
            # guard: a hit from the front is cut to a quarter; unguarded takes it all; a roll's i-frames take nothing
            hurt = "(() => { const c = window.__hm.ctx, p = c.player, C = window.__hm.combat; p.iframes = 0; C.godT = 0; const h0 = window.__hm.S.hp; C.hurtPlayer(20, { x: p.x + 1, z: p.z }); return h0 - window.__hm.S.hp; })()"
            T.ev("(() => { const c = window.__hm.ctx; c.player.facing = 'right'; window.__hm.S.hp = 100; window.__hm.peace = true; })()")
            pg.keyboard.down("c"); pg.wait_for_timeout(500)
            guarded = T.ev(hurt)
            pg.keyboard.up("c"); pg.wait_for_timeout(500)
            open_hit = T.ev(hurt)
            T.step("guard (C) cuts a frontal hit to a quarter", guarded == 5 and open_hit == 20, guarded=guarded, unguarded=open_hit)
            T.ev("window.__hm.combat.st = 100; window.__hm.ctx.player.iframes = 0")
            rolled = T.ev("(() => { const c = window.__hm.ctx, C = window.__hm.combat; window.__hd2d.hold(true); const ok = c.dodge(1, 0); const h0 = window.__hm.S.hp; C.hurtPlayer(20, { x: c.player.x + 1, z: c.player.z }); const d = h0 - window.__hm.S.hp; window.__hd2d.hold(false); return [ok, d, C.st]; })()")
            T.step("dodge roll (X): stamina spent, i-frames ignore the hit", rolled[0] and rolled[1] == 0 and rolled[2] <= 76, roll=rolled)
            pg.wait_for_timeout(500)
            # cozy defeat: slump, fade, wake at the gate with full HP and a moment of grace; nothing lost
            inv0 = T.S()["inv"]
            T.ev("(() => { const c = window.__hm.ctx, C = window.__hm.combat; window.__hm.S.hp = 3; c.player.iframes = 0; C.godT = 0; C.hurtPlayer(20, { x: c.player.x + 1, z: c.player.z }); })()")
            downed = T.ev("window.__hm.downed")
            T.wait("!window.__hm.downed", 30)
            pg.wait_for_timeout(300)
            st = T.ev("({ hp: window.__hm.S.hp, max: window.__hm.combat.maxHp(), god: window.__hm.combat.godT, p: [window.__hm.ctx.player.x, window.__hm.ctx.player.z] })")
            sp = T.ev("window.__hm.ctx.scene.game.spawns.start")
            T.step("defeat is cozy: wake at the gate with full HP, brief grace, bag untouched", downed and st["hp"] == st["max"] and st["god"] > 0
                   and abs(st["p"][0] - sp[0]) < 0.3 and abs(st["p"][1] - sp[1]) < 0.3 and T.S()["inv"] == inv0, state=st)
            T.ev("window.__hm.peace = true")
            T.wait("!window.__hm.combat.summon || window.__hm.combat.summon.life < 20", 5)

            # ---------------------------------------------------------- Part 5: Toadstool Hollows, east past Mossheart's clearing, and back
            T.ev("(() => { const c = window.__hm.ctx, p = c.player; p.x = 12.3; p.z = -0.3; p.y = c.heightAt(p.x, p.z); c.stopWalk(); })()"); pg.wait_for_timeout(400)
            area = T.go_rect("exits")   # a short straight walk east into the gate (a summon / loot can block a diagonal one)
            hq = T.ev("(() => { const G = window.__hm, z = G.glow.zones(); return { title: G.ctx.scene.game.title, pools: z.filter((q) => q.src === 'pool').length, toads: z.filter((q) => q.src === 'toadstool').length, en: (G.combat.enemies || []).length, p: [G.ctx.player.x, G.ctx.player.z] }; })()")
            T.step("edge exit: Mossglen -> Toadstool Hollows (always-glowing toadstools + standing light pools)", area == "hollows" and hq["title"] == "Toadstool Hollows" and hq["pools"] >= 6 and hq["toads"] >= 8 and hq["en"] >= 1, hollows=hq)
            rep["shots"]["hollows"] = T.shot("hollows")
            # Part 5 step 2: bounce toadstools spring you up to the hidden ledge, and back down
            T.ev("(() => { const c = window.__hm.ctx, p = c.player; p.x = 6.2; p.z = -2.3; p.y = c.heightAt(p.x, p.z); c.stopWalk(); })()"); pg.wait_for_timeout(300)
            y0 = T.ev("window.__hm.ctx.player.y"); pg.keyboard.press("z"); pg.wait_for_timeout(250)
            mid = T.ev("(() => { const p = window.__hm.ctx.player; return [window.__hm.hollows.busy(), p.lift]; })()")
            T.wait("!window.__hm.hollows.busy()", 10); pg.wait_for_timeout(300)
            up = T.ev("(() => { const p = window.__hm.ctx.player; return [p.x, p.z, p.y]; })()")
            rep["shots"]["hollows_ledge"] = T.shot("hollows_ledge")
            T.ev("(() => { const c = window.__hm.ctx, p = c.player; p.x = 12.2; p.z = -4.4; p.y = c.heightAt(p.x, p.z); c.stopWalk(); })()"); pg.wait_for_timeout(300)
            pg.keyboard.press("z"); T.wait("!window.__hm.hollows.busy()", 10); pg.wait_for_timeout(300)
            down = T.ev("(() => { const p = window.__hm.ctx.player; return [p.x, p.z, p.y]; })()")
            T.step("bounce toadstool: Z on the cap springs you high onto the hidden ledge (y 2.6), the ledge one springs you back down",
                   mid[0] and mid[1] > 0.8 and abs(up[0] - 7.6) < 0.3 and abs(up[1] + 5.8) < 0.3 and up[2] > 2.3 and y0 < 0.3 and down[2] < 0.3 and down[1] > -2.0
                   and T.S().get("found", {}).get("ledge_up") == 1, mid=mid, up=up, down=down)
            # Part 6: the gnome, gnome doors (a little chest + a peeking gnome), the bubbly spring, a cold-fire brazier
            T.ev("(() => { const c = window.__hm.ctx, p = c.player; p.x = 1.9; p.z = -4.7; p.y = c.heightAt(p.x, p.z); p.facing = 'up'; c.stopWalk(); })()"); pg.wait_for_timeout(350)
            T.talk("gnome")
            T.step("Pipkin the gnome (Hollows-only sprite) talks", T.ev("!window.__hm.dlg") and T.ev("!!window.__hm.ctx.npc('gnome')"))
            T.ev("(() => { const c = window.__hm.ctx, p = c.player; p.x = -11.4; p.z = -6.0; p.y = c.heightAt(p.x, p.z); p.facing = 'up'; c.stopWalk(); })()"); pg.wait_for_timeout(350)
            g0 = T.S().get("gold", 0); t0 = T.S()["inv"].get("tonic", 0); pg.keyboard.press("e"); pg.wait_for_timeout(400)
            S = T.S()
            T.step("gnome door: E opens a little chest (+12 gold, a Hearth tonic), once", S["gold"] == g0 + 12 and S["inv"].get("tonic", 0) == t0 + 1 and S["found"].get("door_chest") == 1, gold=[g0, S["gold"]])
            T.ev("(() => { const c = window.__hm.ctx, p = c.player; p.x = 0.4; p.z = -6.2; p.y = c.heightAt(p.x, p.z); p.facing = 'up'; c.stopWalk(); })()"); pg.wait_for_timeout(350)
            pg.keyboard.press("e"); pg.wait_for_timeout(400)
            peek = T.ev("window.__hm.dlg ? [window.__hm.dlg.npc.role, window.__hm.dlg.npc.name] : null")
            for _ in range(12):
                if not T.ev("!!window.__hm.dlg"): break
                pg.keyboard.press("e"); pg.wait_for_timeout(250)
            T.step("gnome door: another opens on a peeking gnome (dialogue with the gnome portrait)", peek is not None and peek[0] == "gnome" and T.ev("!window.__hm.dlg"), peek=peek)
            T.ev("window.__hm.S.hp = 10"); T.ev("(() => { const c = window.__hm.ctx, p = c.player; p.x = 7.6; p.z = -5.8; p.y = c.heightAt(p.x, p.z); c.stopWalk(); })()")
            T.walk(10.0, -6.4); pg.wait_for_timeout(400)
            sp = T.ev("({ hp: window.__hm.S.hp, max: window.__hm.combat.maxHp(), buff: window.__hm.hollows.buffT, dmg: window.__hm.glow.dmgMul() })")
            rep["shots"]["hollows_spring"] = T.shot("hollows_spring")
            T.step("hidden bubbly spring on the ledge: walking in heals fully and gives spring-fizz (+15% damage, timed)", sp["hp"] == sp["max"] and sp["buff"] > 40 and sp["dmg"] >= 1.15, spring=sp)
            T.ev("(() => { const c = window.__hm.ctx, p = c.player; p.x = 9.4; p.z = -0.6; p.y = c.heightAt(p.x, p.z); p.facing = 'up'; c.stopWalk(); })()"); pg.wait_for_timeout(350)
            T.ev("window.__hm.combat.cd = {}"); pg.keyboard.press("f"); pg.wait_for_timeout(900)
            if not T.ev("window.__hm.hollows.braziers.find((b) => b.id === 'brazier_e').lit"):
                T.ev("window.__hm.combat.cd = {}"); pg.keyboard.press("f"); pg.wait_for_timeout(900)
            bz = T.ev("(() => { const H = window.__hm.hollows, b = H.braziers.find((q) => q.id === 'brazier_e'); return { lit: b.lit, burning: b.burning, light: !!b.light, zone: window.__hm.glow.zones().some((z) => z.src === 'brazier'), saved: window.__hm.S.found.brazier_e }; })()")
            rep["shots"]["hollows_brazier"] = T.shot("hollows_brazier")
            T.step("cold-fire brazier: a spell beside it lights it (flame + blue light + a light zone wraiths avoid), remembered", bz["lit"] and bz["burning"] and bz["light"] and bz["zone"] and bz["saved"] == 1, brazier=bz)
            # ---------------------------------------------------------- stage 4: glow-gardening (the Hollows plot)
            gp = T.ev("window.__hm.garden.qa()")
            T.step("Hollows glow-garden: a plot of 3 empty beds (cold-fire bloom, violet glowbell, red glow toadstool)", len(gp) == 3 and all(p["stage"] == 0 for p in gp)
                   and [p["kind"] for p in gp] == ["coldfire", "violet", "toadcap"], plots=gp)
            T.ev("window.__hm.S.inv.glowseed = 3")
            to_bed = lambda p: T.ev(f"(() => {{ const c = window.__hm.ctx, q = c.player; q.x = {p['x']}; q.z = {p['z']} + 0.6; q.y = c.heightAt(q.x, q.z); c.stopWalk(); }})()")
            T.ev("__padPlug(true)"); pg.wait_for_timeout(500)
            for k, p in enumerate(gp):
                to_bed(p); pg.wait_for_timeout(250)
                if k == 1:
                    T.btn(0)            # controller A plants (the bed counts as something near, so A does not jump)
                else:
                    pg.keyboard.press("e")
                pg.wait_for_timeout(250)
            T.ev("__padPlug(false)"); pg.wait_for_timeout(300)
            gp = T.ev("window.__hm.garden.qa()")
            T.step("E and controller A plant glow seeds (3 seeds used, 3 seed mounds)", all(p["stage"] == 1 for p in gp) and not T.ev("window.__hm.S.inv.glowseed"), plots=[p["stage"] for p in gp])
            d0 = T.ev("window.__hm.S.day || 0")
            T.ev("window.__hd2d.setTime(0.9996)"); pg.wait_for_timeout(2500)
            T.step("midnight rolls the garden's day counter", T.ev("window.__hm.S.day") == d0 + 1, day=[d0, T.ev("window.__hm.S.day")], t=T.ev("window.__hd2d.clock.t"))
            mound = all(p["stage"] == 1 for p in T.ev("window.__hm.garden.qa()"))   # midnight came less than a whole day after planting
            T.ev("window.__hm.S.day += 1"); pg.wait_for_timeout(400)
            sprout = all(p["stage"] == 2 for p in T.ev("window.__hm.garden.qa()"))
            T.ev("window.__hm.S.day += 1; window.__hd2d.setTime(0.9)"); pg.wait_for_timeout(900)
            gp = T.ev("window.__hm.garden.qa()")
            zones = T.ev("window.__hm.glow.zones().filter((z) => z.src === 'garden').length")
            T.step("a whole day after planting they sprout, after two they bloom; at night each bloom casts a light pool and is a light zone",
                   mound and sprout and all(p["stage"] == 3 and p["lit"] for p in gp) and zones == 3, mound=mound, sprout=sprout, zones=zones, plots=gp)
            T.ev(f"(() => {{ const c = window.__hm.ctx, q = c.player; q.x = {gp[1]['x']}; q.z = {gp[1]['z']} + 1.9; q.y = c.heightAt(q.x, q.z); c.stopWalk(); }})()"); pg.wait_for_timeout(900)
            rep["shots"]["garden_night"] = T.shot("garden_night")
            fc, tn = T.ev("window.__hm.S.gems.frost_core || 0"), T.ev("window.__hm.S.inv.tonic || 0")
            to_bed(gp[0]); pg.wait_for_timeout(250); pg.keyboard.press("e"); pg.wait_for_timeout(300)
            to_bed(gp[2]); pg.wait_for_timeout(250); pg.keyboard.press("e"); pg.wait_for_timeout(300)
            gp2 = T.ev("window.__hm.garden.qa()")
            T.step("harvest: the cold-fire bloom gives a frost core, the red glow toadstool 2 Hearth tonics; the beds are empty again",
                   T.ev("window.__hm.S.gems.frost_core") == fc + 1 and T.ev("window.__hm.S.inv.tonic") == tn + 2 and gp2[0]["stage"] == 0 and gp2[2]["stage"] == 0 and gp2[1]["stage"] == 3)
            T.ev("window.__hd2d.setTime(0.45)"); pg.wait_for_timeout(300)
            T.ev("(() => { const c = window.__hm.ctx, p = c.player; p.x = -11.0; p.z = 1.1; p.y = c.heightAt(p.x, p.z); c.stopWalk(); })()"); pg.wait_for_timeout(300)
            area = T.go_rect("exits")
            p = T.pos()
            T.step("edge exit: Toadstool Hollows -> Mossglen (arrive at the east edge)", area == "mossglen" and p[0] > 11, spawn=p)
            # ---------------------------------------------------------- save, reload, continue
            pg.keyboard.press("k"); pg.wait_for_timeout(300)
            saved = T.ev("JSON.parse(localStorage.getItem('hearthmoor-slot-1-v2'))")
            T.step("saved to localStorage hearthmoor-slot-1-v2 (with the hero class)", saved and saved["area"] == "mossglen" and saved["v"] == 2 and saved["cls"] == "stormborn"
                   and T.ev("localStorage.getItem('hearthmoor-slot-1-v1')") is None)
            pos_before = T.pos()
            pg.reload()
            T.wait("window.__hm && window.__hm.ready", 120)
            T.step("after reload the title offers Continue", T.ev("!document.getElementById('btnCont').hidden"), info=T.ev("document.getElementById('saveInfo').textContent"))
            # ---------------------------------------------------------- 3 save slots on the title (keys, controller, touch)
            cards = "[...document.querySelectorAll('.slotcard')].map((b) => [+b.dataset.slot, b.dataset.icon, b.classList.contains('on'), b.textContent])"
            T.wait("[...document.querySelectorAll('.slotcard')].some((b) => b.dataset.icon)", 30)
            T.wait("!window.__hd2dGate.loading && window.__hd2d && window.__hd2d.ready", 90)   # keys are swallowed until the loading gate opens
            sl = T.ev(cards)
            T.step("title: 3 save slots; slot 1 shows the pixel hero, level, area and play time, slot 2 is empty",
                   len(sl) == 3 and sl[0][1] == "stormborn" and sl[0][2] and "Lv " in sl[0][3] and "Mossglen" in sl[0][3] and "played" in sl[0][3] and "empty" in sl[1][3], slots=sl)
            pg.keyboard.press("c"); pg.wait_for_timeout(200)
            cp = T.ev("JSON.parse(localStorage.getItem('hearthmoor-slot-2-v2') || 'null')")
            T.step("keyboard: C copies slot 1 into the first empty slot (2)", cp and cp["cls"] == "stormborn" and cp["area"] == "mossglen" and cp["quests"] == saved["quests"],
                   copy=cp and [cp["cls"], cp["area"], cp["quests"]], toast=T.ev("document.getElementById('toast').textContent"), gate=T.ev("window.__hd2dGate.loading"))
            pg.keyboard.press("ArrowRight"); pg.wait_for_timeout(200)
            T.step("keyboard: right arrow picks slot 2 (the copy: Continue offered)", T.ev("window.__hm.slot") == 2 and T.ev("!document.getElementById('btnCont').hidden") and T.ev(cards)[1][1] == "stormborn")
            T.ev("__padPlug(true)"); pg.wait_for_timeout(600)
            T.btn(7)
            armed = T.ev("window.__hm.slots3.state().armed") and T.ev("!!localStorage.getItem('hearthmoor-slot-2-v2')")
            T.btn(7)
            T.step("controller: RT asks first, a second RT deletes slot 2; an empty slot hides Continue", armed and T.ev("localStorage.getItem('hearthmoor-slot-2-v2')") is None
                   and T.ev("document.getElementById('btnCont').hidden") and "empty" in T.ev(cards)[1][3])
            T.btn(14)
            T.step("controller: d-pad left goes back to slot 1", T.ev("window.__hm.slot") == 1)
            T.ev("__padPlug(false)"); pg.wait_for_timeout(300)
            pg.click(".slotcard[data-slot='3']"); pg.wait_for_timeout(200)
            on3 = T.ev("window.__hm.slot") == 3 and T.ev("document.getElementById('btnDel').disabled")
            pg.click(".slotcard[data-slot='1']"); pg.wait_for_timeout(200)
            T.step("tap: a slot card selects it (empty slot 3: Delete disabled), tapping slot 1 comes back with its save intact",
                   on3 and T.ev("window.__hm.slot") == 1 and T.ev("JSON.parse(localStorage.getItem('hearthmoor-slot-1-v2')).cls") == "stormborn" and not T.ev("document.getElementById('btnCont').hidden"))
            pg.click("#btnCont")
            T.idle()
            pg.wait_for_timeout(500)
            S = T.S()
            pos_after = T.pos()
            T.step("Continue restores area, position, hero, bag, errands, Pudding", T.ev("window.__hm.area") == "mossglen" and S["inv"].get("moonpetal") == 3
                   and S["cls"] == "stormborn" and T.ev("window.__hm.ctx.player.role") == "stormborn"
                   and S["quests"] == {"bread": 3, "tea": 2, "cat": 2} and S["cat"] == "follow" and T.ev("!!window.__hm.ctx.npc('cat')")
                   and abs(pos_after[0] - pos_before[0]) < 0.3 and abs(pos_after[1] - pos_before[1]) < 0.3
                   and T.ev("!window.__hm.ctx.fx.petal_0 && !window.__hm.ctx.fx.petal_1 && !window.__hm.ctx.fx.petal_2 && !!window.__hm.ctx.fx.petal_3"),
                   pos=[pos_before, pos_after])

            # ---------------------------------------------------------- home through the gate with Pudding
            area = T.go_rect("portals")
            T.step("portal: Mossglen -> plaza, Pudding comes too", area == "plaza" and T.ev("!!window.__hm.ctx.npc('cat')"))
            T.talk("kid")
            S = T.S()
            T.step("Pudding home with Tib: errand 3 done", S["quests"]["cat"] == 3 and S["cat"] == "home" and S["inv"].get("acorn") == 1 and "leaf_gust" in S["spells"])
            # ---------------------------------------------------------- stage 3: Odo's shop (keys, controller, touch) + tonics
            T.step("Odo the merchant keeps a stall in the plaza", T.ev("(() => { const a = window.__hm.ctx.npc('merchant'); return !!a && a.role === 'shopkeeper'; })()"))
            T.ev("__padPlug(true)"); pg.wait_for_timeout(600)   # the shop + gear steps use the controller too
            T.ev("(() => { const S = window.__hm.S, LO = window.__hm.LO; S.gold = 120; S.bag.push(LO.makeItem(2, 2, 'weapon')); })()")
            T.talk("merchant"); pg.wait_for_timeout(300)
            shop0 = T.ev("window.__hm.shopUI.qa()")
            T.step("talking to Odo opens the shop panel (tonic, glow seed, 3 pieces of gear)", T.ev("!!window.__hm.shop && !document.getElementById('shopui').hidden") and len(shop0["rows"]) == 5
                   and shop0["rows"][0]["name"] == "Hearth tonic", rows=[r["name"] for r in shop0["rows"]])
            g0, t0 = T.ev("window.__hm.S.gold"), T.ev("window.__hm.S.inv.tonic || 0")
            pg.keyboard.press("Enter"); pg.wait_for_timeout(250)
            T.step("keyboard: Enter buys a Hearth tonic (12 gold)", T.ev("window.__hm.S.gold") == g0 - 12 and T.ev("window.__hm.S.inv.tonic") == t0 + 1)
            rep["shots"]["shop_buy"] = T.shot("shop_buy")
            T.btn(5); pg.wait_for_timeout(200)
            sell = T.ev("window.__hm.shopUI.qa()")
            g1, n1 = T.ev("window.__hm.S.gold"), len(T.S()["bag"])
            T.btn(0); pg.wait_for_timeout(250)
            first = sell["rows"][0] if sell["rows"] else {}
            sold = T.ev("window.__hm.S.gold") - g1
            if not sold and first:   # an Epic / Legendary first row asks twice
                T.btn(0); pg.wait_for_timeout(250); sold = T.ev("window.__hm.S.gold") - g1
            T.step("controller: RB to the sell tab, A sells the first bag item at its rarity price", sell["tab"] == 1 and len(T.S()["bag"]) == n1 - 1 and sold == first.get("price"), first=first, sold=sold)
            T.btn(4); pg.wait_for_timeout(200)
            g2 = T.ev("window.__hm.S.gold")
            pg.click("#shopBody .row[data-k='1'] button"); pg.wait_for_timeout(250)
            T.step("touch: tapping 'buy 8g' buys a glow seed", T.ev("window.__hm.S.gold") == g2 - 8 and T.ev("window.__hm.S.inv.glowseed") >= 1)
            pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
            T.step("Esc closes the shop and the field takes input again", not T.ev("window.__hm.shop") and T.ev("document.getElementById('shopui').hidden"))
            T.ev("window.__hm.S.hp = 30"); tn = T.ev("window.__hm.S.inv.tonic")
            pg.keyboard.press("u"); pg.wait_for_timeout(300)
            T.step("U drinks a Hearth tonic: +60 HP, one fewer in the bag", T.ev("window.__hm.S.hp") >= 90 and (T.ev("window.__hm.S.inv.tonic") or 0) == tn - 1, hp=T.ev("window.__hm.S.hp"))
            # ---------------------------------------------------------- stage 4: Bix Coppertuft's Nine Keys Bank (one vault shared by all save slots)
            bx = T.ev("(() => { const a = window.__hm.ctx.npc('banker'); return a ? { role: a.role, p: [+a.x.toFixed(2), +a.z.toFixed(2)] } : null; })()")
            T.step("Bix Coppertuft the gnome clerk keeps the bank in the plaza", bx and bx["role"] == "gnome", bix=bx)
            T.ev("(() => { localStorage.removeItem('hearthmoor-bank-v1'); const S = window.__hm.S, LO = window.__hm.LO; S.gold = 100; S.bag.push(LO.makeItem(2, 1, 'armor')); })()")
            T.talk("banker"); pg.wait_for_timeout(300)
            bq = T.ev("window.__hm.shopUI.qa()")
            T.step("talking to Bix opens the bank panel (Deposit tab: gold rows, then your gear)", bq["open"] == "bank" and bq["rows"][0]["name"] == "Deposit 10 gold"
                   and T.ev("document.querySelector('#shopTabs button').textContent") == "Deposit" and T.ev("!document.getElementById('shopui').hidden"), rows=[r["name"] for r in bq["rows"]][:6])
            rep["shots"]["bank"] = T.shot("bank")
            bank = "JSON.parse(localStorage.getItem('hearthmoor-bank-v1') || 'null')"
            pg.keyboard.press("Enter"); pg.wait_for_timeout(250)
            bk = T.ev(bank)
            T.step("keyboard: Enter deposits 10 gold into the shared vault", T.ev("window.__hm.S.gold") == 90 and bk and bk["gold"] == 10, bank=bk and bk["gold"])
            nbag = len(T.S()["bag"])
            T.btn(13); T.btn(13); T.btn(0); pg.wait_for_timeout(250)   # d-pad down twice to the first bag row, A deposits it
            bk = T.ev(bank)
            T.step("controller: d-pad down + A deposits a piece of gear (it takes one of the 40 vault slots)", len(T.S()["bag"]) == nbag - 1 and len(bk["items"]) == 1, items=len(bk["items"]))
            pg.click("#shopTabs button:nth-child(2)"); pg.wait_for_timeout(250)
            pg.click("#shopBody .row[data-k='2'] button"); pg.wait_for_timeout(250)
            pg.click("#shopBody .row[data-k='0'] button"); pg.wait_for_timeout(250)
            bk = T.ev(bank)
            T.step("touch: Vault tab, 'take' brings the gear back and 'take' on the gold row withdraws 10 gold", len(T.S()["bag"]) == nbag and not bk["items"] and bk["gold"] == 0 and T.ev("window.__hm.S.gold") == 100)
            T.step("the vault lives outside the save slot (hearthmoor-bank-v1, shared by all three slots)",
                   "bank" not in json.loads(T.ev("localStorage.getItem('hearthmoor-slot-1-v2')")) and T.ev("localStorage.getItem('hearthmoor-bank-v1')") is not None)
            pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
            # ---------------------------------------------------------- stage 3: the travelling night merchant + gem sockets
            t_day = T.ev("window.__hd2d.clock.t")
            T.ev("window.__hd2d.setTime(0.9)"); pg.wait_for_timeout(700)
            nm = T.ev("(() => { const a = window.__hm.ctx.npc('nightmerchant'), s = window.__hm.shopUI; return { here: !!a, role: a && a.role, light: !!(s.nm && s.nm.light), zone: window.__hm.glow.zones().some((z) => z.src === 'lantern'),"
                 " pool: !!(s.nm && s.nm.fx.some((f) => f.name === 'coldfire_pool')), motes: s.nm ? s.nm.fx.filter((f) => f.name === 'coldfire_motes').length : 0, power: s.nm && s.nm.light ? s.nm.light.base : 0 }; })()")
            T.step("night: Sefa the night merchant sets up by the well with a neon-blue lantern (light + light zone)", nm["here"] and nm["role"] == "nightmerchant" and nm["light"] and nm["zone"], nm=nm)
            T.step("Sefa's lantern casts a bright neon-blue cold-fire pool on the cobbles (strong light + ground decal + flicker motes)", nm["pool"] and nm["motes"] == 2 and nm["power"] >= 10, nm=nm)
            T.ev("(() => { const c = window.__hm.ctx, p = c.player, a = c.npc('nightmerchant'); p.x = a.x + 0.4; p.z = a.z + 1.6; p.y = c.heightAt(p.x, p.z); c.stopWalk(); })()")
            pg.wait_for_timeout(1200)
            rep["shots"]["night_merchant"] = T.shot("night_merchant")
            T.ev("window.__hm.S.gold = 400")
            T.talk("nightmerchant"); pg.wait_for_timeout(300)
            ns = T.ev("window.__hm.shopUI.qa()")
            socks = T.ev("window.__hm.shopUI.stockOf('night').map((it) => it.gems.length)")
            T.step("Sefa's shop: socket gems (rift shard, golem core, frost core, moon opal) + socketed Rare / Epic gear", ns["open"] == "night"
                   and [r["name"] for r in ns["rows"] if r["kind"] == "gem"] == ["Rift shard", "Golem core", "Frost core", "Moon opal"] and socks and min(socks) >= 1, rows=[r["name"] for r in ns["rows"]], sockets=socks)
            T.ev("window.__hm.shopUI.i = 1; window.__hm.shopUI.draw()"); pg.keyboard.press("Enter"); pg.wait_for_timeout(250)
            T.step("buy a rift shard (120 gold) into the gem pouch", T.ev("window.__hm.S.gold") == 280 and (T.S().get("gems") or {}).get("rift_shard") == 1, gems=T.S().get("gems"))
            pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
            T.ev("window.__hd2d.setTime(0.5)"); pg.wait_for_timeout(700)
            T.step("dawn: the night merchant packs up and his lantern light goes", not T.ev("!!window.__hm.ctx.npc('nightmerchant')") and not T.ev("!!window.__hm.shopUI.nm"))
            # ---------------------------------------------------------- glow-light cap (Options): 3 on desktop, 2 on phones
            g0 = T.ev("[window.__hm.glowCap(), window.__hm.ctx.glowN]")
            T.ev("document.getElementById('btnGlow').click()")
            pg.wait_for_function("window.__hm.ctx && window.__hm.ctx.glowN === " + str(5 - g0[0]) + " && window.__hd2d.ready", timeout=120000); pg.wait_for_timeout(500)
            g1 = T.ev("[window.__hm.glowCap(), window.__hm.ctx.glowN, document.getElementById('btnGlow').textContent, window.__hm.area]")
            T.ev("document.getElementById('btnGlow').click()")
            pg.wait_for_function("window.__hm.ctx && window.__hm.ctx.glowN === " + str(g0[0]) + " && window.__hd2d.ready", timeout=120000); pg.wait_for_timeout(500)
            g2 = T.ev("[window.__hm.glowCap(), window.__hm.ctx.glowN, window.__hm.area]")
            T.step("Options: glow lights toggles 3 <-> 2 (phone) and re-opens the area in place with that many pooled lights",
                   g0 == [3, 3] and g1[:2] == [2, 2] and "2" in g1[2] and g1[3] == "plaza" and g2 == [3, 3, "plaza"], g0=g0, g1=g1, g2=g2)
            T.ev(f"window.__hd2d.setTime({t_day if 0.25 < t_day < 0.8 else 0.5})")
            T.ev("(() => { const S = window.__hm.S, LO = window.__hm.LO, it = LO.makeItem(3, 4, 'weapon'); it.name = 'Sunfire Rune Hammer'; S.bag.unshift(it); S.gems.golem_core = 1; S.gems.rift_shard = 1; })()")
            T.step("a Legendary always rolls 2 sockets; Rare+ roll 0-2", T.ev("window.__hm.S.bag[0].gems.length") == 2
                   and T.ev("(() => { const LO = window.__hm.LO; let ok = true; for (let i = 0; i < 60; i++) { const n = LO.makeItem(2, 2).gems.length; if (n > 2) ok = false; if (LO.makeItem(2, 0).gems.length) ok = false; } return ok; })()"))
            sp0 = T.ev("window.__hm.combat.M.spellMul"); hp0 = T.ev("window.__hm.combat.maxHp()")
            pg.keyboard.press("g"); pg.wait_for_timeout(300)
            pg.click("#heroBody .row[data-k='3']"); pg.wait_for_timeout(200)
            pg.keyboard.press("r"); pg.wait_for_timeout(250)
            g1 = T.ev("window.__hm.S.bag[0].gems")
            T.btn(3); pg.wait_for_timeout(250)
            g2 = T.ev("window.__hm.S.bag[0].gems")
            T.step("Gear tab: R (keys) then Y (controller) set both gems into the Legendary's sockets", g1.count(None) == 1 and None not in g2 and set(g2) == {"golem_core", "rift_shard"}, after_r=g1, after_y=g2)
            idx = T.ev("window.__hm.S.bag.findIndex((it) => it.name === 'Sunfire Rune Hammer')")
            pg.click(f"#heroBody [data-eq='{idx}']"); pg.wait_for_timeout(300)
            rep["shots"]["gear_sockets"] = T.shot("gear_sockets")
            T.step("socketed gems count once equipped (rift shard: spells, golem core: HP) and the icon shows them", T.ev("window.__hm.combat.M.spellMul") > sp0 + 0.05 and T.ev("window.__hm.combat.maxHp()") >= hp0 + 15,
                   spell=[sp0, T.ev("window.__hm.combat.M.spellMul")], hp=[hp0, T.ev("window.__hm.combat.maxHp()")])
            pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
            T.ev("(() => { const S = window.__hm.S; if (S.gear.weapon && S.gear.weapon.rar === 4) window.__hm.LO.unequip(S, 'weapon'); })()")
            T.ev("__padPlug(false)"); pg.wait_for_timeout(600)
            area = T.go_rect("exits")
            T.talk("herbalist")
            S = T.S()
            T.step("moonpetals to Wren: errand 2 done", S["quests"]["tea"] == 3 and S["inv"].get("tea") == 1 and not S["inv"].get("moonpetal") and "light_orb" in S["spells"])
            T.step("all 3 errands done, no quest tags left", all(v == 3 for v in S["quests"].values()) and T.ev("Object.keys(window.__hm.markers).length") == 0)
            pg.keyboard.press("j"); pg.wait_for_timeout(400)
            rep["shots"]["questlog_done"] = T.shot("questlog_done")
            pg.keyboard.press("j")

            # ---------------------------------------------------------- second save/reload round trip
            pg.keyboard.press("k"); pg.wait_for_timeout(300)
            pg.reload()
            T.wait("window.__hm && window.__hm.ready && window.__hd2d.ready", 120)
            pg.wait_for_timeout(400)
            T.ev("__padPlug(true)"); pg.wait_for_timeout(500)
            T.btn(0)     # A on the title = Continue
            T.idle()
            S = T.S()
            T.step("reload #2: controller A on the title Continues; finished game state restored in Bakery Lane", T.ev("window.__hm.area") == "lane" and all(v == 3 for v in S["quests"].values())
                   and set(S["spells"]) >= {"sparkle_burst", "hearth_flame", "light_orb", "leaf_gust"})
            T.step("no JS errors", not errors and not T.ev("window.__hd2d.errors.length"), errors=errors[:5])
            rep["pass"] = True
        except Exception as e:  # noqa: BLE001
            rep["pass"] = False
            rep["error"] = f"{type(e).__name__}: {e}"[:600]
            try:
                rep["shots"]["failure"] = T.shot("failure")
                rep["state"] = T.S()
            except Exception:  # noqa: BLE001
                pass
        rep["steps"] = T.steps
        rep["errors"] = errors[:20]

        # ---------------------------------------------------------- phone portrait with the pad (continue the save)
        if rep["pass"]:
            try:
                saved = pg.evaluate("localStorage.getItem('hearthmoor-slot-1-v2')")
                ctx.close()
                ph = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
                ph.add_init_script(f"if (!sessionStorage.getItem('seeded')) {{ localStorage.setItem('hearthmoor-slot-1-v2', {json.dumps(saved)}); sessionStorage.setItem('seeded', '1'); }}")
                ph.add_init_script(STUB)
                q = ph.new_page()
                q.on("pageerror", lambda e: errors.append(f"PAGEERROR {e}"))
                T.pg = q
                cdp = ph.new_cdp_session(q)
                TS = [time.time()]

                def touch(kind, pts):
                    TS[0] += 0.05   # OS-style timestamps: a slow SwiftShader frame can't stretch a tap into a hold
                    cdp.send("Input.dispatchTouchEvent", {"type": kind, "touchPoints": [{"x": x, "y": y, "id": i} for i, (x, y) in enumerate(pts)], "timestamp": TS[0]})

                def tap(x, y):
                    TS[0] = max(TS[0], time.time()); touch("touchStart", [(x, y)]); touch("touchEnd", [])

                # loading gate on the phone: taps on Continue / the world while the assets load do nothing
                held, hold = [], [True]
                q.route("**/*.glb", lambda route: held.append(route) if hold[0] else route.continue_())
                q.goto(url + "&pad=1", wait_until="commit")
                q.wait_for_function("window.__hd2dGate && document.getElementById('btnCont')", timeout=60000)
                q.wait_for_timeout(500)
                cb = T.ev("(() => { const r = document.getElementById('btnCont').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; })()")
                for i in range(5):
                    tap(cb[0] or 195, cb[1] or 420); tap(120 + 30 * i, 600); q.wait_for_timeout(90)
                hold[0] = False
                for rt in held:
                    rt.continue_()
                q.wait_for_function("window.__hm && window.__hm.ready && window.__hd2d && window.__hd2d.ready", timeout=120000)
                q.wait_for_timeout(800)
                T.step("phone: taps during loading are swallowed (still on the title)", T.ev("window.__hm.title && !document.getElementById('titlescreen').hidden")
                       and T.ev("window.__hd2dGate.swallowed") > 0, swallowed=T.ev("window.__hd2dGate.swallowed"))
                q.tap("#btnCont")
                q.wait_for_function("window.__hm.ctx && !window.__hm.busy && !window.__hm.title", timeout=120000)
                q.evaluate("window.__hm.go('plaza', 'from_lane', 'walk')")
                q.wait_for_function("window.__hm.area === 'plaza' && !window.__hm.busy && window.__hd2d.ready", timeout=120000)
                q.wait_for_timeout(800)
                padon = q.evaluate("document.body.classList.contains('padon') && !document.getElementById('pad').hidden")
                p2 = out / "phone_portrait_pad.png"
                q.screenshot(path=str(p2), timeout=120000)
                rep["shots"]["phone_portrait_pad"] = str(p2)
                T.step("phone portrait: pad on, game continues on touch", padon)
                # no page scroll / zoom
                nz = T.ev("""(() => { const m = document.querySelector('meta[name=viewport]').content; const ev = (t) => { const e = new Event(t, { bubbles: true, cancelable: true }); document.body.dispatchEvent(e); return e.defaultPrevented; };
                  return [/user-scalable=no/.test(m), getComputedStyle(document.body).touchAction, getComputedStyle(document.body).overscrollBehaviorY, ev('gesturestart'), ev('dblclick')]; })()""")
                T.ev("window.__noReload = 1")
                tap(300, 330); tap(300, 330)                                 # double-tap
                q.wait_for_timeout(300)
                TS[0] = max(TS[0], time.time()); touch("touchStart", [(240, 80)])
                for i in range(1, 9):
                    touch("touchMove", [(240, 80 + 45 * i)]); q.wait_for_timeout(20)
                touch("touchEnd", []); q.wait_for_timeout(500)
                vv = T.ev("[visualViewport.scale, scrollX, scrollY, window.__noReload === 1]")
                T.step("phone: page never scrolls or zooms (double-tap, pull-to-refresh, gesturestart, dblclick)",
                       nz == [True, "none", "none", True, True] and vv == [1, 0, 0, True], guards=nz, after=vv)
                for _ in range(3):
                    if T.ev("!!window.__hm.dlg || window.__hm.log"):
                        q.keyboard.press("Escape"); q.wait_for_timeout(150)
                T.ev("window.__hm.ctx.stopWalk()"); q.wait_for_timeout(300)
                # floating stick: lands under the thumb, slides after the finger past its radius, walks; mid-drag shot
                zone = T.ev("(() => { const a = document.getElementById('stickZone').getBoundingClientRect(); return [a.left, a.top, a.width, a.height]; })()")
                rest = T.ev("(() => { const a = document.getElementById('stick').getBoundingClientRect(); return [a.left + a.width / 2, a.top + a.height / 2]; })()")
                sx, sy = zone[0] + zone[2] * 0.5, zone[1] + zone[3] * 0.3
                pa = T.pos()
                TS[0] = max(TS[0], time.time()); touch("touchStart", [(sx, sy)]); q.wait_for_timeout(150)
                s1 = T.ev("window.__hd2d.stickState()")
                fy = sy
                for i in range(1, 11):          # north (up the plaza, open cobbles): 140 px, past the 64 px rim
                    fy = sy - 14 * i
                    touch("touchMove", [(sx + 2 * i, fy)]); q.wait_for_timeout(35)
                q.wait_for_timeout(80)
                s2 = T.ev("window.__hd2d.stickState()")
                p3 = out / "phone_portrait_floatstick.png"
                q.screenshot(path=str(p3), timeout=120000)
                rep["shots"]["phone_portrait_floatstick"] = str(p3)
                q.wait_for_timeout(600)
                touch("touchEnd", []); q.wait_for_timeout(300)
                s3 = T.ev("window.__hd2d.stickState()")
                pb = T.pos()
                b2 = s2["base"] or {"x": sx, "y": sy}
                fd = (((sx + 20) - b2["x"]) ** 2 + (fy - b2["y"]) ** 2) ** 0.5
                T.step("phone: floating stick appears under the thumb (not the fixed corner)", s1["base"] and abs(s1["base"]["x"] - sx) < 3 and abs(s1["base"]["y"] - sy) < 3
                       and ((rest[0] - sx) ** 2 + (rest[1] - sy) ** 2) ** 0.5 > 60, touch=[round(sx), round(sy)], rest=[round(v) for v in rest])
                T.step("phone: stick re-centres when dragged past its radius and walks the player", sy - b2["y"] > 50 and abs(fd - 64) < 8 and s2["run"]
                       and abs(pb[0] - pa[0]) + abs(pb[1] - pa[1]) > 0.5 and not s3["active"] and s3["rest"],
                       base=[round(b2["x"]), round(b2["y"])], finger_to_base=round(fd, 1), moved=[round(pb[0] - pa[0], 2), round(pb[1] - pa[1], 2)])
                # a quick tap in the stick zone and on open ground both still walk (no conflict with the stick)
                walked = []
                for (x, y) in ((zone[0] + zone[2] * 0.7, zone[1] + zone[3] * 0.15), (zone[0] + zone[2] * 0.4, zone[1] + zone[3] * 0.1), (300, 380), (330, 300), (260, 260)):
                    T.ev("window.__hm.ctx.stopWalk()")
                    tap(x, y); q.wait_for_timeout(250)
                    walked.append(bool(T.ev("window.__hd2d.walking()")))
                    T.ev("window.__hm.ctx.stopWalk()"); q.wait_for_timeout(100)
                    while T.ev("!!window.__hm.dlg || window.__hm.log"):
                        q.keyboard.press("Escape"); q.wait_for_timeout(150)
                T.step("phone: tap in the stick zone and tap on open ground both walk", any(walked[:2]) and any(walked[2:]), walked=walked)
                # pinch zooms the camera only
                d0 = T.ev("window.__hd2d.camState().dist")
                TS[0] = max(TS[0], time.time()); touch("touchStart", [(195 - 30, 300), (195 + 30, 300)])
                for i in range(1, 9):
                    a = 30 + 15 * i
                    touch("touchMove", [(195 - a, 300), (195 + a, 300)]); q.wait_for_timeout(25)
                touch("touchEnd", []); q.wait_for_timeout(300)
                d1 = T.ev("window.__hd2d.camState().dist")
                T.step("phone: pinch zooms the camera (page scale stays 1)", d1 < d0 - 0.5 and T.ev("visualViewport.scale") == 1, dist=[round(d0, 2), round(d1, 2)])
                # action buttons: MAIN swings when nobody is near, jump, guard (hold), roll, summon, spell tap + hold wheel
                T.ev("window.__hm.ctx.stopWalk()")
                def bc(sel):
                    return T.ev(f"(() => {{ const r = document.querySelector('{sel}').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2, r.width]; }})()")
                acts = {}
                def idle_act():
                    try:
                        T.wait("!window.__hd2d.actorState().act", 8)   # let the last action finish (slow, capped game time)
                    except Exception:  # noqa: BLE001
                        pass
                for name, sel, want in (("main", "#padMain", "attack"), ("jump", "#padJump", "jump")):
                    idle_act()
                    x, y, _w = bc(sel); q.wait_for_timeout(300)
                    TS[0] = max(TS[0], time.time()); touch("touchStart", [(x, y)]); touch("touchEnd", [])
                    q.wait_for_timeout(120 if name == "jump" else 60)
                    acts[name] = T.ev("window.__hd2d.actorState().act")
                    q.wait_for_timeout(700)
                idle_act()
                x, y, _w = bc("#padGuard"); TS[0] = max(TS[0], time.time()); touch("touchStart", [(x, y)]); q.wait_for_timeout(500)
                acts["guard"] = T.ev("window.__hd2d.actorState().act"); touch("touchEnd", []); q.wait_for_timeout(300)
                acts["guard_lit"] = T.ev("document.getElementById('padGuard').classList.contains('on')")
                try:
                    T.wait("window.__hd2d.actorState().act !== 'defend'", 8)   # the lowering frames run in (slow, capped) game time
                except Exception:  # noqa: BLE001
                    pass
                acts["guard_after"] = T.ev("window.__hd2d.actorState().act")
                idle_act(); T.ev("window.__hm.combat.st = 100")
                x, y, _w = bc("#padDodge"); TS[0] = max(TS[0], time.time()); touch("touchStart", [(x, y)]); touch("touchEnd", []); q.wait_for_timeout(40)
                acts["roll"] = T.ev("window.__hm.combat.st") < 100
                q.wait_for_timeout(600)
                T.ev("window.__hm.combat.cd.summon = 0; window.__hm.combat.cd.spell = 0; window.__hm.combat.cd.charm = 0")
                x, y, _w = bc("#padSummon"); TS[0] = max(TS[0], time.time()); touch("touchStart", [(x, y)]); touch("touchEnd", []); q.wait_for_timeout(300)
                acts["summon"] = (T.ev("window.__hm.combat.qa().summon") or {}).get("role")
                sizes = [bc(s)[2] for s in ("#padMain", "#padJump", "#padGuard", "#padDodge", "#padSpell", "#padSummon", "#pad3rd")]
                T.step("phone: action buttons work (MAIN swings, jump, hold guard, roll, summon) and are thumb-sized", acts["main"] == "attack" and acts["jump"] == "jump"
                       and acts["guard"] == "defend" and not acts["guard_lit"] and acts["guard_after"] != "defend" and acts["roll"] and acts["summon"] == "stormsprite" and min(sizes) >= 44, acts=acts, sizes=sizes)
                # spell: hold opens the slow-time wheel, slide to another slot, let go = select + cast
                T.ev("window.__hm.ctx.selectSpell(0)")
                x, y, _w = bc("#padSpell"); TS[0] = max(TS[0], time.time()); touch("touchStart", [(x, y)]); q.wait_for_timeout(700)
                wheel = T.ev("[!document.getElementById('wheel').hidden, window.__hm.ctx.timeScale()]")
                for i in range(1, 6):
                    touch("touchMove", [(x + 12 * i, y)]); q.wait_for_timeout(30)
                p5 = out / "phone_portrait_spellwheel.png"
                q.screenshot(path=str(p5), timeout=120000)
                rep["shots"]["phone_portrait_spellwheel"] = str(p5)
                touch("touchEnd", []); q.wait_for_timeout(300)
                after = T.ev("[document.getElementById('wheel').hidden, window.__hm.ctx.timeScale(), window.__hm.ctx.spellIndex()]")
                T.step("phone: holding spell opens the slow-time wheel; sliding + letting go picks and casts", wheel == [True, 0.2] and after == [True, 1, 1], wheel=wheel, after=after)
                # left-handed flip from the options card: zone and stick move to the right, still floating
                q.tap("#btnOpts"); q.wait_for_timeout(300)
                q.tap("#btnHand"); q.wait_for_timeout(200)
                q.tap("#optsClose"); q.wait_for_timeout(300)
                z2 = T.ev("(() => { const a = document.getElementById('stickZone').getBoundingClientRect(); return [a.left, a.top, a.width, a.height]; })()")
                tx, ty = z2[0] + z2[2] * 0.4, z2[1] + z2[3] * 0.35
                TS[0] = max(TS[0], time.time()); touch("touchStart", [(tx, ty)]); q.wait_for_timeout(150)
                s4 = T.ev("window.__hd2d.stickState()")
                for i in range(1, 6):
                    touch("touchMove", [(tx - 14 * i, ty)]); q.wait_for_timeout(35)
                p4 = out / "phone_portrait_floatstick_left.png"
                q.screenshot(path=str(p4), timeout=120000)
                rep["shots"]["phone_portrait_floatstick_left"] = str(p4)
                touch("touchEnd", []); q.wait_for_timeout(200)
                T.step("phone: left-handed flip mirrors the floating stick zone", T.ev("document.body.classList.contains('lefthand')") and z2[0] >= 194
                       and s4["base"] and abs(s4["base"]["x"] - tx) < 3, zone=[round(v) for v in z2])
                q.tap("#btnOpts"); q.wait_for_timeout(300); q.tap("#btnHand"); q.wait_for_timeout(200); q.tap("#optsClose"); q.wait_for_timeout(200)
                # controller on the phone: pad hides while it is used, a touch brings it back
                T.ev("__padPlug(true)"); T.ev("__padAxes(0, 1)"); q.wait_for_timeout(800); T.ev("__padAxes(0, 0)"); q.wait_for_timeout(300)
                hid = T.ev("getComputedStyle(document.getElementById('pad')).display === 'none'")
                tap(195, 150); q.wait_for_timeout(300)
                back = T.ev("!document.body.classList.contains('ctrl') && getComputedStyle(document.getElementById('pad')).display !== 'none'")
                T.step("phone: on-screen pad hides while a controller is used and comes back on touch", hid and back, hidden=hid, back=back)
                T.ev("__padPlug(false)")
                # phone landscape: the full action layout (report shot), nothing overlapping
                q.set_viewport_size({"width": 844, "height": 390}); q.wait_for_timeout(1200)
                lay = T.ev("""(() => { const els = [...document.querySelectorAll('#hud .chip, #hud button, #pad .pb, [data-hud]')].filter((e) => e.offsetParent && getComputedStyle(e).visibility !== 'hidden');
                  const R = els.map((e) => [e.id || e.className, e.getBoundingClientRect()]); const bad = [];
                  for (let i = 0; i < R.length; i++) { const a = R[i][1]; if (a.left < -1 || a.top < -1 || a.right > innerWidth + 1 || a.bottom > innerHeight + 1) bad.push(['out', R[i][0]]);
                    for (let j = i + 1; j < R.length; j++) { const b = R[j][1]; const ox = Math.min(a.right, b.right) - Math.max(a.left, b.left), oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
                      if (ox > 1 && oy > 1 && !els[i].contains(els[j]) && !els[j].contains(els[i])) bad.push([R[i][0], R[j][0]]); } } return bad; })()""")
                p6 = out / "phone_landscape_buttons.png"
                q.screenshot(path=str(p6), timeout=120000)
                rep["shots"]["phone_landscape_buttons"] = str(p6)
                T.step("phone landscape: HUD + action buttons inside the screen, nothing overlapping", not lay, overlaps=lay[:6])
            except Exception as e:  # noqa: BLE001
                rep["pass"] = False
                rep["error"] = f"phone: {e}"[:400]
        # ---------------------------------------------------------- v1 save migration (old saves still load)
        if rep["pass"]:
            try:
                v1 = {"v": 1, "area": "lane", "pos": [0.5, 2.0, "down"], "t": 0.4, "inv": {"coin": 3, "moonpetal": 2}, "quests": {"bread": 3, "tea": 1, "cat": 0},
                      "picked": {"petal_0": True, "petal_1": True}, "cat": "glade", "spells": ["sparkle_burst", "hearth_flame"], "played": 321, "savedAt": "2026-10-01T12:00:00.000Z"}
                mg = b.new_context(viewport={"width": size[0], "height": size[1]})
                mg.add_init_script(f"if (!sessionStorage.getItem('seeded')) {{ localStorage.clear(); localStorage.setItem('hearthmoor-slot-1-v1', {json.dumps(json.dumps(v1))}); sessionStorage.setItem('seeded', '1'); }}")
                m = mg.new_page()
                m.on("pageerror", lambda e: errors.append(f"PAGEERROR {e}"))
                T.pg = m
                m.goto(url)
                T.wait("window.__hm && window.__hm.ready && window.__hd2d && window.__hd2d.ready", 120)
                m.wait_for_timeout(500)
                info = T.ev("document.getElementById('saveInfo').textContent")
                T.step("v1 save: the title offers Continue", T.ev("!document.getElementById('btnCont').hidden"), info=info)
                m.click("#btnCont")
                T.wait("window.__hm.picking", 30)
                m.wait_for_timeout(300)
                m.click("#hero_grovekeeper"); m.wait_for_timeout(200); m.click("#btnBegin")
                T.idle(); m.wait_for_timeout(500)
                S = T.S()
                v2 = T.ev("JSON.parse(localStorage.getItem('hearthmoor-slot-1-v2'))")
                old = T.ev("JSON.parse(localStorage.getItem('hearthmoor-slot-1-v1'))")
                T.step("v1 save migrates: pick a hero once, area / bag / errands / charms carry over, v2 written, v1 left as it was",
                       T.ev("window.__hm.area") == "lane" and S["cls"] == "grovekeeper" and S["inv"] == v1["inv"] and S["quests"] == v1["quests"]
                       and S["spells"] == v1["spells"] and v2 and v2["v"] == 2 and v2["cls"] == "grovekeeper" and old == v1
                       and T.ev("window.__hm.ctx.player.role") == "grovekeeper", cls=S["cls"], area=T.ev("window.__hm.area"))
                T.step("no JS errors (all contexts)", not errors, errors=errors[:5])
                mg.close()
            except Exception as e:  # noqa: BLE001
                rep["pass"] = False
                rep["error"] = f"migration: {e}"[:400]
        b.close()
    srv.shutdown()
    rep["seconds"] = round(time.time() - T_START, 1)
    rep["steps"] = T.steps
    (out / "smoke.json").write_text(json.dumps(rep, indent=1))
    log(f"smoke: {'PASS' if rep['pass'] else 'FAIL'} {sum(s['pass'] for s in T.steps)}/{len(T.steps)} steps in {rep['seconds']} s" + (f"  ({rep.get('error')})" if not rep["pass"] else ""))
    return rep


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(GAME / "tests" / "shots"))
    ap.add_argument("--simscale", type=int, default=4)
    a = ap.parse_args()
    r = run(Path(a.out), a.simscale)
    sys.exit(0 if r["pass"] else 1)
