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
import math
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
        self.t0 = time.time()

    def ev(self, js):
        return self.pg.evaluate(js)

    def step(self, name, ok, **info):
        self.steps.append({"step": name, "pass": bool(ok), "seg": getattr(self, "seg", ""), **info})
        self.log(f"  [{'PASS' if ok else 'FAIL'}] {name} {json.dumps(info)[:200] if info else ''}  @{time.time() - self.t0:.0f}s")
        if not ok:
            raise AssertionError(name)

    def frames(self, n=6, timeout=30):
        """wait until the engine has drawn n more frames (fixed sleeps alone race slow frames on a loaded box)"""
        f0 = self.ev("window.__hd2d.frames || 0")
        self.wait(f"(window.__hd2d.frames || 0) >= {f0 + n}", timeout)

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

    def to_choice(self, n=80):
        """read a dialogue up to its choice page without ever pressing E on it (E there would pick an answer)"""
        for _ in range(n):
            st = self.ev("(() => { const d = window.__hm.dlg; return d ? [d.picking, d.full, d.i === d.pages.length - 1] : null; })()")
            if not st:
                return None
            if st[0]:
                return self.ev("window.__hm.dlgChoice()")
            if st[2]:
                self.pg.wait_for_timeout(200); continue   # the last page types itself out, then the answers appear
            self.pg.keyboard.press("e"); self.pg.wait_for_timeout(160)
        return None

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


# ---------------------------------------------------------------------------------------------- segments / shards
# The playthrough is cut into segments at real save points. A sharded run starts a segment from the checkpoint the
# segment before it saved (localStorage only: the same thing the serial run's reload + Continue restores from).
# Every step still runs exactly once across the shards, with the same assertions and thresholds.
FIX = Path(__file__).resolve().parent / "fixtures"
SEGS = "ABCDEF"
SEG_INFO = {
    "A": "title, loading gate, Lantern Eve, errands, controller, Mossglen, leveling, combat, loot, rares + rifts, Hollows, garden (ends: K save in Mossglen -> cp1)",
    "B": "reload #1 + Continue, save slots, Pudding home, shop, bank, riddle, night merchant, factions, glow cap, weather, sockets, errand 2 (ends: K save in the Lane -> cp2)",
    "C": "reload #2, Rift Shrine + Vanaheim, Ravenhold Harbor, Bifrost Crossing (ends: -> cp3)",
    "D": "phone portrait + landscape on touch (continues the cp3 save)",
    "E": "v1 save migration",
    "F": "Stage 6+: the Stray Den + glowing pets (continues the cp3 save)",
}
# --quick <area>: the segments that cover an area / feature (a per-change check; the batch still runs everything)
QUICK = {
    "title": "A", "intro": "A", "plaza": "A", "lane": "A", "controller": "A", "mossglen": "A", "combat": "A", "loot": "A",
    "rares": "A", "rifts": "A", "hollows": "A", "garden": "A", "leveling": "A",
    "slots": "B", "shop": "B", "bank": "B", "riddle": "B", "merchant": "B", "factions": "B", "weather": "B", "glow": "B", "gear": "B",
    "rift": "C", "vanaheim": "C", "ravenhold": "C", "bifrost": "C",
    "phone": "D", "touch": "D", "migration": "E", "save": "BE",
    "pet": "F", "pets": "F", "stray": "F",
}
TIMING = FIX / "smoke_timing.json"   # seconds per segment from the last passing runs (shard balancing only)
DEFAULT_SECONDS = {"A": 560, "B": 260, "C": 230, "D": 140, "E": 25, "F": 150}


def seg_seconds():
    try:
        t = json.loads(TIMING.read_text())
        return {k: float(t.get(k, DEFAULT_SECONDS[k])) for k in SEGS}
    except Exception:  # noqa: BLE001
        return dict(DEFAULT_SECONDS)


def plan_shards(n, segs=SEGS):
    """longest-first greedy split of the segments over n shards (deterministic for one timing file)"""
    w = seg_seconds()
    bins = [[0.0, []] for _ in range(n)]
    for k in sorted(segs, key=lambda k: (-w[k], k)):
        b = min(bins, key=lambda x: x[0])
        b[0] += w[k]; b[1].append(k)
    return ["".join(sorted(b[1])) for b in bins]


def run(out, simscale=4, size=(960, 540), segs=SEGS):
    from playwright.sync_api import sync_playwright
    out.mkdir(parents=True, exist_ok=True)
    segs = "".join(k for k in SEGS if k in segs)
    seg_rep = {}

    def seg_mark(k):
        seg_rep[k] = {"start": round(time.time() - T_START, 1), "steps0": len(T.steps)}; T.seg = k

    def seg_done(k):
        r = seg_rep[k]; r["end"] = round(time.time() - T_START, 1); r["seconds"] = round(r["end"] - r["start"], 1)
        r["steps"] = len(T.steps) - r.pop("steps0"); r["pass"] = True

    def cp_dump(page, name):
        """the segment passed: keep its end state (all of localStorage) as the next segment's start in a sharded run"""
        d = page.evaluate("Object.fromEntries(Object.keys(localStorage).map((k) => [k, localStorage.getItem(k)]))")
        (out / f"smoke_{name}.json").write_text(json.dumps(d, indent=1, sort_keys=True))
        FIX.mkdir(exist_ok=True)
        tmp = FIX / f".smoke_{name}.{time.time_ns()}.tmp"
        tmp.write_text(json.dumps(d, indent=1, sort_keys=True)); tmp.replace(FIX / f"smoke_{name}.json")

    def cp_load(page, T_, url_, name):
        """start a segment from a checkpoint: open the title, swap in the saved localStorage (the title never saves)"""
        d = json.loads((FIX / f"smoke_{name}.json").read_text())
        log(f"  (segment starts from checkpoint {name}: {len(d)} localStorage keys)")
        if page is None:
            return d
        page.goto(url_)
        T_.wait("window.__hm && window.__hm.ready && window.__hd2d && window.__hd2d.ready && window.__hm.title", 120)
        page.evaluate("(d) => { localStorage.clear(); for (const [k, v] of Object.entries(d)) localStorage.setItem(k, v); }", d)
        return d

    srv = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(GAME)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/index.html?nosw&peace&simscale={simscale}"
    lines, errors = [], []
    log = lambda s: (print(s, flush=True), lines.append(s))  # noqa: E731
    rep = {"url": url, "shots": {}, "segments_run": segs, "segments": seg_rep}
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
            if "A" in segs:
                seg_mark("A")
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
                # ---------------------------------------------------------- Lantern Eve opening (Stage 5): plays once on a new game
                T.wait("window.__hm.intro.active", 30)
                ist = lambda: T.ev("window.__hm.intro.state()")
                i0 = ist()
                T.step("Lantern Eve opening starts on a new game: day 0, dusk, 7 lanterns lit, skip chip up", i0["active"] and i0["lanterns"] == 7 and i0["flag"] == "playing"
                       and abs(T.ev("window.__hm.ctx.clock.t") - 0.76) < 0.03 and T.ev("!document.getElementById('introSkip').hidden") and (T.S().get("day") or 0) == 0, intro=i0)
                T.wait("window.__hm.intro.state().rising >= 5 && window.__hm.intro.state().maxUp > 0.5", 90)
                pools = T.ev("window.__hd2d.effects.list.filter((f) => f.name === 'light_pool').length")
                lan = T.ev("window.__hd2d.effects.list.filter((f) => f.name === 'sky_lantern').map((f) => +f.y.toFixed(2))")
                warm = T.ev("window.__hm.ctx.glows.filter((g) => !g.kill && g.color.r > 0.9 && g.color.b < 0.5).length")
                rep["shots"]["lantern_eve_lanterns"] = T.shot("lantern_eve_lanterns")
                T.step("lanterns float up as glowing pools of light (light pools + sparkles, warm lights riding along)", len(lan) == 7 and max(lan) > min(lan) + 0.3
                       and pools >= 5 and warm >= 2, lanterns=lan, pools=pools, warm=warm)
                T.wait("!!window.__hm.dlg", 60)
                who = []
                for _ in range(60):
                    if T.ev("window.__hm.intro.state().step") != "talk":
                        break
                    nm = T.ev("window.__hm.dlg ? document.getElementById('dlgName').textContent : ''")
                    if nm and (not who or who[-1] != nm):
                        who.append(nm)
                    pg.keyboard.press("e"); pg.wait_for_timeout(160)
                T.step("Bram and the villagers speak in the dialogue panel (Bram, Grandpa Alder, Tib, Marla)", len(who) == 4 and "Bram" in who[0] and "Alder" in who[1] and who[2] == "Tib" and "Marla" in who[3], who=who)
                T.wait("window.__hm.intro.state().tear", 30); pg.wait_for_timeout(1200)
                i1 = ist()
                tear = T.ev("window.__hd2d.effects.list.some((f) => f.name === 'rift_tear')")
                violet = T.ev("window.__hm.ctx.glows.some((g) => !g.kill && g.color.r > 0.5 && g.color.b > 0.5 && g.color.g < 0.4)")
                rep["shots"]["lantern_eve_rift_tear"] = T.shot("lantern_eve_rift_tear")
                T.step("a violet-red tear flickers open over the moss gate; the lanterns freeze in the air", i1["tear"] and i1["frozen"] and tear and violet, intro=i1)
                T.wait("window.__hm.intro.state().wraith", 30)
                ew = T.ev("(() => { const e = window.__hm.combat.enemies.find((x) => x.id === 'eve_wraith'); return e ? [e.a.role, e.D.name, e.D.shy || false] : null; })()")
                T.read_all()
                T.step("a cold-fire wraith slips out of the tear (not light-shy: it fights under the lanterns)", ew and ew[0] == "wraith" and not ew[2] and T.ev("window.__hm.intro.state().step") == "fight", wraith=ew)
                hits = 0
                for _ in range(40):
                    if not T.ev("window.__hm.intro.state().wraith"):
                        break
                    w = T.ev("(() => { const e = window.__hm.combat.enemies.find((x) => x.id === 'eve_wraith'); return e ? [e.a.x, e.a.z] : null; })()")
                    p0 = T.pos()
                    if w and math.hypot(w[0] - p0[0], w[1] - p0[1]) > 1.1:
                        T.walk(w[0], w[1] + 0.7, 30)
                        T.ev(f"window.__hm.ctx.player.facing = 'up'")
                    pg.keyboard.press("r"); pg.wait_for_timeout(450); hits += 1
                T.step("the first fight happens under the lanterns: R attacks land and the wraith falls", not T.ev("window.__hm.intro.state().wraith"), swings=hits)
                for _ in range(40):
                    if not T.ev("window.__hm.intro.active"):
                        break
                    if T.ev("!!window.__hm.dlg"):
                        pg.keyboard.press("e")
                    pg.wait_for_timeout(160)
                S = T.S()
                T.step("the tear seals and the three errands follow as the Lantern Eve tasks (flag done, skip chip gone)", not T.ev("window.__hm.intro.active") and S["flags"].get("intro") == "done"
                       and not T.ev("window.__hd2d.effects.list.some((f) => f.name === 'rift_tear' && f.t < f.dur - 0.5)") and T.ev("document.getElementById('introSkip').hidden")
                       and S["quests"] == {"bread": 0, "tea": 0, "cat": 0} and "Lantern Eve tasks" in T.ev("document.querySelector('#log .head b').textContent")
                       and not T.ev("!!window.__hm.ctx.npc('eve_bram')"))
                # skip paths (replayed for the test): Esc on the keyboard, B on the controller
                T.ev("window.__hm.intro.start(true)"); T.wait("window.__hm.intro.state().lanterns === 7", 20); pg.wait_for_timeout(300)
                pg.keyboard.press("Escape"); pg.wait_for_timeout(400)
                T.step("Esc skips the opening: lanterns, Bram and the tear cleaned up, flag 'skipped'", not T.ev("window.__hm.intro.active") and T.ev("window.__hm.S.flags.intro") == "skipped"
                       and T.ev("document.getElementById('introSkip').hidden") and not T.ev("!!window.__hm.ctx.npc('eve_bram')") and not T.ev("!!window.__hm.dlg"))
                T.ev("__padPlug(true)"); pg.wait_for_timeout(700)
                T.ev("window.__hm.intro.start(true)"); T.wait("!!window.__hm.dlg", 60); pg.wait_for_timeout(300)
                T.btn(1)
                pg.wait_for_timeout(400)
                T.step("controller B skips the opening (even mid-dialogue), nothing left behind", not T.ev("window.__hm.intro.active") and not T.ev("!!window.__hm.dlg")
                       and not T.ev("window.__hm.combat.enemies.some((e) => e.id === 'eve_wraith' && e.state !== 'dead' && e.state !== 'gone')"))
                T.ev("__padPlug(false)"); pg.wait_for_timeout(500)
                T.ev("window.__hm.S.flags.intro = 'done'; window.__hm.save()")
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
                # ---------------------------------------------------------- stage 4: dialogue choices (Bram's Lantern Eve wish, by mouse / touch)
                T.talk("innkeeper", keep_open=True); ch = T.to_choice()
                seeds0 = T.ev("window.__hm.S.inv.glowseed || 0")
                rep["shots"]["dialogue_choice"] = T.shot("dialogue_choice")
                pg.click("#dlgChoices .choice[data-i='2']"); pg.wait_for_timeout(300)
                reply = T.ev("window.__hm.dlg ? window.__hm.dlg.pages[0] : ''"); T.read_all()
                T.step("dialogue choices: Bram asks who your Lantern Eve lantern is for (4 answers); clicking one sets a flag and gives that gift",
                       bool(ch) and len(ch["options"]) == 4 and ch["ci"] == 0 and T.ev("window.__hm.S.flags.lantern") == "lost"
                       and T.ev("window.__hm.S.inv.glowseed") == seeds0 + 2 and "glow seeds" in reply, choice=ch, reply=reply[:60])
                pages, first = T.talk("innkeeper")
                T.step("the answer changes Bram's reply afterwards, and he does not ask again", "drift east" in first and pages == 2, line=first[:60])
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
                T.ev("__padAxes(0.45, 0)"); pg.wait_for_timeout(600); T.frames(8)
                half = T.ev("[window.__hm.ctx.player.speedScale, window.__hm.ctx.player.running]")
                T.ev("__padAxes(1, 0)"); pg.wait_for_timeout(600); T.frames(8)
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
                T.wait("!window.__hm.combat || ((window.__hm.combat.cd.charm || 0) <= 0 && (window.__hm.combat.cd.spell || 0) <= 0)", 20)   # game-time cooldown, slow on a loaded box
                n0 = T.ev(near)
                k0 = T.ev("window.__hd2d.padPresses || 0")
                T.ev("__padBtn(3, 1)"); T.wait(f"(window.__hd2d.padPresses || 0) > {k0}", 20)
                casting = T.ev("window.__hm.ctx.player.castT > 0"); pg.wait_for_timeout(150); T.ev("__padBtn(3, 0)")
                # Y casts on release: watch for the cast itself (castT / a cooldown starting / an effect near) instead of one
                # fixed 300 ms look, which misses it when the box only draws 1-2 frames a second
                try:
                    T.wait(f"window.__hm.ctx.player.castT > 0 || (window.__hm.combat.cd.spell || 0) > 0 || (window.__hm.combat.cd.charm || 0) > 0 || {near} > {n0}", 15)
                    casting = True
                except Exception:
                    pass
                pg.wait_for_timeout(300)
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
                            " return { state: e.state, light: !!e.light, bar: !!(b && !b.hidden), label: b ? b.firstChild.textContent : '', w: b ? b.querySelector('i').style.width : '' }; })()")
                rep["shots"]["boss_fight"] = T.shot("boss_fight")
                T.step("Mossheart: carries a rune light, a named boss bar shows when it fights", boss["light"] and boss["bar"] and "Mossheart" in boss["label"] and boss["w"] not in ("", "100%"), boss=boss)
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
                # ---------------------------------------------------------- stage 5 part 2: procedural rares + random rifts
                KILL = ("(() => { const G = window.__hm, C = G.combat, p = G.ctx.player; G.peace = true;"
                        " for (const e of %s) for (let i = 0; i < 60 && e.state !== 'dead' && e.state !== 'gone'; i++) C.damageEnemy(e, 80, p); })()")
                T.ev("(() => { const G = window.__hm, C = G.combat; G.peace = true; G.loot.clear(); C.heal(999, true); })()")
                hm0 = T.ev("window.__hm.S.merit.hearth")
                rare = T.ev("(() => { const G = window.__hm, p = G.ctx.player; const R = G.rares.spawn({ base: 'deathlord', el: 'gloam', traits: ['shielded'], pos: [p.x + 3.4, p.z - 0.3] });"
                            " return { name: R.name, id: R.e.id, light: !!R.e.light, aura: G.ctx.effects.list.some((f) => f.name === 'rare_aura_violet'), scale: R.D.scale, minRar: R.D.minRar }; })()")
                T.frames(8); pg.wait_for_timeout(500)
                big = T.ev(f"(() => {{ const R = window.__hd2d.actorRects(), m = R.find((r) => r.id === '{rare['id']}'), p = R.find((r) => r.id === 'player'); return {{ sheet: m && m.sheet, mh: m && m.h / m.k, ph: p && p.h / p.k }}; }})()")
                rep["shots"]["rare_death_lord"] = T.shot("rare_death_lord")
                T.step("a procedural rare: name prefix (trait + element + base), a coloured aura and its own light",
                       rare["name"] == "Shielded Gloam Death Lord" and rare["aura"] and rare["light"] and rare["minRar"] >= 2, rare=rare)
                T.step("the rare is drawn natively on the area's boss sheet at 2-3x the hero (80 px frame vs 32)",
                       big["sheet"] == "boss" and big["mh"] == 80 and big["ph"] == 32 and 2 <= rare["scale"] <= 3, **big)
                ward = T.ev(f"(() => {{ const G = window.__hm, C = G.combat, e = C.enemies.find((x) => x.id === '{rare['id']}'), h0 = e.hp, w0 = e.rare.ward; G.ctx.player.iframes = 99; G.peace = false; C.damageEnemy(e, 40, G.ctx.player);"
                            " const b = document.getElementById('bossbar'); return { lost: h0 - e.hp, ward: [w0, e.rare.ward], bar: !!(b && !b.hidden), label: b ? b.firstChild.textContent : '', col: b ? b.firstChild.style.color : '' }; })()")
                T.frames(3)
                # read the bar while the rare still fights (in peace it walks home and heals, which hides the bar)
                ward.update(T.ev("(() => { const b = document.getElementById('bossbar'), r = { bar: !!(b && !b.hidden), label: b ? b.firstChild.textContent : '', col: b ? b.firstChild.style.color : '' }; window.__hm.peace = true; window.__hm.ctx.player.iframes = 0; return r; })()"))
                T.step("Shielded: the rune ward soaks most of a hit; a named bar in the element colour shows the rare",
                       ward["lost"] < 40 and ward["ward"][1] < ward["ward"][0] and ward["bar"] and "Death Lord" in ward["label"] and ward["col"] != "", **ward)
                T.ev(KILL % f"window.__hm.combat.enemies.filter((x) => x.id === '{rare['id']}')")
                T.frames(6); pg.wait_for_timeout(600)
                hunt = T.S().get("hunt") or {}
                drops = T.ev("window.__hm.loot.qa()")
                T.step("felling the rare: a hunt log entry and a guaranteed Rare-or-better drop; the aura goes",
                       (hunt.get("deathlord:gloam:shielded") or {}).get("kills") == 1 and any((d["rar"] or 0) >= 2 for d in drops)
                       and not T.ev("window.__hm.ctx.effects.list.some((f) => f.name === 'rare_aura_violet' && f.t < f.dur - 0.31)"), hunt=list(hunt), drops=drops)
                T.step("merit: felling the one-trait rare earns the realm's faction 50 Hearth Tokens", T.ev("window.__hm.S.merit.hearth") == hm0 + 50, before=hm0, after=T.ev("window.__hm.S.merit.hearth"))
                traits = T.ev("(() => { const G = window.__hm, C = G.combat, p = G.ctx.player; const R = G.rares.spawn({ base: 'elderwraith', el: 'frost', traits: ['enraged', 'blinking', 'summoner'], pos: [p.x + 3.2, p.z + 0.6] });"
                              " const e = R.e; G.peace = false; e.state = 'chase'; const x0 = e.a.x, z0 = e.a.z; R.blinkT = 0; R.callT = 0; G.rares.tick(e, 0.05, false);"
                              " const moved = Math.hypot(e.a.x - x0, e.a.z - z0), sp0 = e.D.speed; C.damageEnemy(e, Math.ceil(e.hp * 0.6), p); G.rares.tick(e, 0.05, false); G.peace = true;"
                              " return { rname: R.name, blinks: R.blinks || 0, moved: +moved.toFixed(2), kin: R.minions.length, enraged: !!R.enraged, faster: e.D.speed > sp0, aura: !!R.fx }; })()")
                T.step("traits work: Blinking jumps to the hero's side, Summoner calls kin, Enraged speeds up below half health",
                       traits["blinks"] == 1 and traits["moved"] > 0.5 and traits["kin"] == 1 and traits["enraged"] and traits["faster"] and traits["rname"].endswith("Frostfire Elder Wraith"), **traits)
                T.ev(KILL % "window.__hm.combat.enemies.filter((x) => x.rare || /_kin/.test(x.id))")
                T.frames(6); pg.wait_for_timeout(600)
                pg.keyboard.press("j"); pg.wait_for_timeout(400)
                hl = T.ev("[...document.querySelectorAll('#huntList li b')].map((b) => b.textContent)")
                rep["shots"]["hunt_log"] = T.shot("hunt_log")
                pg.keyboard.press("j"); pg.wait_for_timeout(300)
                T.step("the hunt log (J / Start / ☰) lists both rares", len(hl) == 2 and "Shielded Gloam Death Lord" in hl and any("Frostfire Elder Wraith" in n for n in hl), hunt=hl)
                T.ev("window.__hm.loot.clear()")
                # random rifts: three tiers
                OPEN = "(() => { const G = window.__hm, p = G.ctx.player; const R = G.rifts.open(%d, [p.x + 4.6, p.z - 0.8]); if (%s) G.rifts.cur.forceRare = true; return G.rifts.state(); })()"   # force the tier II rare at open (setting it later races the hero's approach)
                GO = "(() => { const G = window.__hm, c = G.ctx, p = c.player, R = G.rifts.cur; p.x = R.pos[0] - 1.4; p.z = R.pos[1] + 0.6; p.y = c.heightAt(p.x, p.z); c.stopWalk(); })()"
                ALIVE = "window.__hm.rifts.alive()"
                for tier, tid, fx, shot in ((0, "minor", "rift_tear_minor", "rift_minor"), (1, "major", "rift_tear", "rift_major"), (2, "abyssal", "rift_tear_abyss", "rift_abyssal")):
                    c0 = (T.S().get("rifts") or {}).get(tid, 0); gm0 = T.ev("window.__hm.S.merit.gate"); gr0 = T.ev("window.__hm.S.ranks.gate")
                    st = T.ev(OPEN % (tier, 'true' if tier == 1 else 'false'))
                    T.frames(10); pg.wait_for_timeout(700)
                    rep["shots"][shot] = T.shot(shot)
                    ok = st["rift"] and st["rift"]["state"] == "open" and fx in st["rift"]["fx"] and (tier < 2 or "rift_ring_abyss" in st["rift"]["fx"])
                    T.ev(GO); T.frames(6); pg.wait_for_timeout(400)
                    f1 = T.ev("window.__hm.rifts.state()")["rift"]
                    waves = []
                    for w in range(3):
                        r = T.ev("window.__hm.rifts.state()")["rift"]
                        if not r: break
                        waves.append([r["wave"], r["alive"], r["rare"]])
                        T.ev(KILL % ALIVE); T.frames(8); pg.wait_for_timeout(500)
                    end = T.ev("window.__hm.rifts.state()")
                    if tier == 2:   # the Guild's rank-up toast shows (it may queue behind another rank-up, e.g. the Hearth's from the rift rare)
                        try: T.wait("(() => { const t = document.getElementById('toast'); return !t.hidden && t.innerText.includes(\"Gatekeepers' Guild: Friend\"); })()", 30)
                        except Exception: pass
                    ru = T.ev("(() => { const F = window.__hm.factions, t = document.getElementById('toast'); return { last: F.last, toast: t && !t.hidden ? t.innerText : '', merit: window.__hm.S.merit.gate, rank: window.__hm.S.ranks.gate }; })()")
                    if tier == 2: rep["shots"]["rank_up"] = T.shot("rank_up")
                    drops = T.ev("window.__hm.loot.qa()")
                    need = {0: 1, 1: 2, 2: 3}[tier]
                    T.step(f"random rift tier {tier + 1} ({tid}): opens with its tear, spits a wave when you come close, seals with a reward",
                           ok and f1 and f1["state"] == "fight" and f1["alive"] >= 3 and end["rift"] is None and end["closed"][tid] == c0 + 1
                           and any(d["gold"] for d in drops) and any((d["rar"] or 0) >= need for d in drops)
                           and (tier != 1 or (waves and waves[0][2])) and (tier != 2 or (len(waves) == 2 and waves[0][2] and waves[1][0] == 2)), waves=waves, fx=st["rift"] and st["rift"]["fx"])
                    T.step(f"merit: sealing the {tid} rift earns the Gatekeepers' Guild {(30, 60, 120)[tier]} Rift Marks", ru["merit"] == gm0 + (30, 60, 120)[tier], before=gm0, after=ru["merit"])
                    if tier == 2:
                        T.step("rank-up: the abyssal seal lifts the Guild to Friend with a toast in its glow colour + a sparkle burst and a coloured light on the hero",
                               gr0 == 0 and ru["rank"] == 1 and ru["last"] and ru["last"]["id"] == "gate" and ru["last"]["r"] == 1 and ru["last"]["spark"] and ru["last"]["glow"] and "Gatekeepers' Guild: Friend" in ru["toast"], ru=ru)
                    T.ev("window.__hm.loot.clear()")
                H = T.S().get("hunt") or {}
                T.step("rift rares go into the hunt log too (the abyssal one has two traits)", sum(h["kills"] for h in H.values()) >= 4 and any(len(h["traits"]) == 2 for h in H.values()),
                       hunt=[h["name"] for h in H.values()])
                ign = T.ev("(() => { const G = window.__hm, p = G.ctx.player; const c0 = { ...(G.S.rifts || {}) }; G.rifts.open(0, [p.x + 9, p.z]); G.rifts.cur.t = 999; G.rifts.update(0.016);"
                           " return { gone: !G.rifts.cur, same: JSON.stringify(c0) === JSON.stringify(G.S.rifts || {}) }; })()")
                T.step("an ignored rift closes by itself (no reward)", ign["gone"] and ign["same"], **ign)
                auto = T.ev("(() => { const G = window.__hm, R = G.rifts, a = R.auto; R.auto = () => true; R.timer = 0.01; R.update(0.05); const st = R.state(); R.close(false, true); R.auto = a;"
                            " return { opened: !!st.rift, tier: st.rift && st.rift.id, timer: R.timer > 30 }; })()")
                T.step("in normal play a rift tears open by itself when its timer runs out (tier picked by weight)", auto["opened"] and auto["tier"] in ("minor", "major", "abyssal"), **auto)
                T.ev("(() => { const G = window.__hm; G.peace = true; G.loot.clear(); G.combat.heal(999, true); G.ctx.player.iframes = 0; })()")
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
                pg.wait_for_timeout(1500)
                hw = T.ev("window.__hm.weather.qa()")
                T.step("Hollows at night: drifting self-lit glow mist (scheduled, not forced)", hw["kind"] == "glowmist" and not hw["forced"] and hw["parts"].get("glow_mist", 0) > 5, hw=hw)
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
                T.ev("window.__hd2d.setTime(0.3)"); pg.wait_for_timeout(2500)
                mw = T.ev("window.__hm.weather.qa()")
                T.ev("window.__hd2d.setTime(0.45)"); pg.wait_for_timeout(1200)
                mw2 = T.ev("window.__hm.weather.qa()")
                T.step("Mossglen: mist rolls in on a morning (07:12) and lifts by late morning", mw["kind"] == "mist" and mw["parts"].get("mist", 0) > 0 and mw2["kind"] == "clear" and not mw2["emitters"], morning=mw, later=mw2)
                # ---------------------------------------------------------- save, reload, continue
                pg.keyboard.press("k"); pg.wait_for_timeout(300)
                saved = T.ev("JSON.parse(localStorage.getItem('hearthmoor-slot-1-v2'))")
                T.step("saved to localStorage hearthmoor-slot-1-v2 (with the hero class)", saved and saved["area"] == "mossglen" and saved["v"] == 2 and saved["cls"] == "stormborn"
                       and T.ev("localStorage.getItem('hearthmoor-slot-1-v1')") is None)
                T.step("the hunt log and rift tally are saved with the slot", sum(h["kills"] for h in (saved.get("hunt") or {}).values()) >= 4 and (saved.get("rifts") or {}).get("abyssal", 0) >= 1,
                       hunt=len(saved.get("hunt") or {}), rifts=saved.get("rifts"))
                pos_before = T.pos()
                seg_done("A"); cp_dump(pg, "cp1")
            if "B" in segs:
                seg_mark("B")
                if "A" not in segs:   # sharded: start from segment A's checkpoint (its K save in Mossglen)
                    cp = cp_load(pg, T, url, "cp1")
                    saved = json.loads(cp["hearthmoor-slot-1-v2"]); pos_before = saved["pos"][:2]
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
                T.step("Continue never replays the Lantern Eve opening", not T.ev("window.__hm.intro.active") and S["flags"].get("intro") == "done"
                       and T.ev("document.getElementById('introSkip').hidden"))

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
                hfr = T.ev("window.__hm.S.ranks.hearth") >= 1   # Order of the Hearth Friend: 10% off at Odo's (rounded)
                tonic_p, seed_p = (11, 7) if hfr else (12, 8)
                pg.keyboard.press("Enter"); pg.wait_for_timeout(250)
                T.step(f"keyboard: Enter buys a Hearth tonic ({tonic_p} gold{', Hearth Friend 10% off' if hfr else ''})", shop0["rows"][0]["price"] == tonic_p
                       and T.ev("window.__hm.S.gold") == g0 - tonic_p and T.ev("window.__hm.S.inv.tonic") == t0 + 1, price=shop0["rows"][0]["price"], hearth=T.ev("window.__hm.S.merit.hearth"))
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
                T.step(f"touch: tapping 'buy {seed_p}g' buys a glow seed", T.ev("window.__hm.S.gold") == g2 - seed_p and T.ev("window.__hm.S.inv.glowseed") >= 1)
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
                # ---------------------------------------------------------- stage 4: dialogue choices (Bix's riddle lock, by keys + controller)
                T.talk("banker", keep_open=True); ch = T.to_choice()
                pg.keyboard.press("Escape"); pg.wait_for_timeout(250)
                c1 = [T.ev("(window.__hm.S.flags || {}).riddle || null"), T.ev("window.__hm.dlg ? window.__hm.dlg.pages[0] : ''")]
                T.read_all(); pg.keyboard.press("Escape"); pg.wait_for_timeout(250)   # his reply opens the bank: close it
                T.talk("banker", keep_open=True); T.to_choice()
                pg.keyboard.press("ArrowDown"); pg.wait_for_timeout(150); ci = T.ev("window.__hm.dlgChoice().ci")
                pg.keyboard.press("e"); pg.wait_for_timeout(300)
                c2 = [T.ev("window.__hm.S.flags.riddle"), T.ev("window.__hm.dlg ? window.__hm.dlg.pages.join(' ') : ''")]
                T.read_all(); pg.keyboard.press("Escape"); pg.wait_for_timeout(250)
                T.step("keys: Esc on a choice page takes the 'not now' answer; arrow down + E answers Bix's riddle wrong and earns a hint",
                       bool(ch) and ch["options"][0] == "Footsteps." and c1[0] is None and "lock keeps" in c1[1] and ci == 1 and c2[0] == "tried" and "hint" in c2[1], c1=c1, ci=ci, c2=c2)
                g0, op0 = T.ev("window.__hm.S.gold"), T.ev("(window.__hm.S.gems || {}).moon_opal || 0")
                T.talk("banker", keep_open=True); T.to_choice()
                T.btn(13); T.btn(12); ci2 = T.ev("window.__hm.dlgChoice().ci"); T.btn(0); pg.wait_for_timeout(300)
                c3 = T.ev("window.__hm.dlg ? window.__hm.dlg.pages.join(' ') : ''")
                T.read_all(); pg.keyboard.press("Escape"); pg.wait_for_timeout(250)
                pages, first = T.talk("banker"); pg.keyboard.press("Escape"); pg.wait_for_timeout(250)
                T.step("controller: d-pad down / up + A answers 'Footsteps': drawer nine gives a moon opal + 25 gold, and Bix's greeting changes",
                       ci2 == 0 and T.ev("window.__hm.S.flags.riddle") == "solved" and T.ev("window.__hm.S.gold") == g0 + 25
                       and T.ev("window.__hm.S.gems.moon_opal") == op0 + 1 and "drawer nine swings open" in c3.lower() and "contentedly" in first, c3=c3[:60], line=first[:60])
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
                rs0 = (T.S().get("gems") or {}).get("rift_shard", 0)   # a rare may already have dropped one (50%)
                T.ev("window.__hm.shopUI.i = 1; window.__hm.shopUI.draw()"); pg.keyboard.press("Enter"); pg.wait_for_timeout(250)
                T.step("buy a rift shard (120 gold) into the gem pouch", T.ev("window.__hm.S.gold") == 280 and (T.S().get("gems") or {}).get("rift_shard") == rs0 + 1, gems=T.S().get("gems"), before=rs0)
                pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
                T.ev("window.__hd2d.setTime(0.5)"); pg.wait_for_timeout(700)
                T.step("dawn: the night merchant packs up and his lantern light goes", not T.ev("!!window.__hm.ctx.npc('nightmerchant')") and not T.ev("!!window.__hm.shopUI.nm"))
                # ---------------------------------------------------------- stage 5 part 3: factions + merit (five factions, six ranks)
                fa0 = T.ev("window.__hm.factions.qa()")
                nerr = sum(1 for v in T.S()["quests"].values() if v == 3)
                T.step("merit so far comes from play: Hearth Tokens for errands + rares, Gilded Acorns for the riddle + secrets, Black Doubloons for Sefa's gem",
                       fa0["merit"]["hearth"] >= 40 * nerr + 180 and fa0["merit"]["gnome"] >= 60 + 40 and fa0["merit"]["corsair"] == 15 and nerr >= 2, errands=nerr, q=T.S()["quests"], gn=fa0["merit"]["gnome"], co=fa0["merit"]["corsair"], he=fa0["merit"]["hearth"])
                T.step("Warden Hilde of the Hearth stands on the plaza terrace (rune guard)", T.ev("(() => { const a = window.__hm.ctx.npc('hilde'); return !!a && a.role === 'runeguard'; })()"))
                h0 = fa0["merit"]["hearth"]
                pages, first = T.talk("hilde")
                T.wait("window.__hm.heroUI && window.__hm.hui.tab === 4", 10)
                rows = T.ev("Array.from(document.querySelectorAll('#heroBody .row.fac')).map((r) => [r.dataset.fac, getComputedStyle(r).borderLeftColor, getComputedStyle(r.querySelector('.fsw')).backgroundColor, r.querySelector('.fbar i').style.width])")
                cols = T.ev("window.__hm.FA.FAC_IDS.map((id) => window.__hm.FA.FACTIONS[id].col)")
                hexrgb = lambda h: f"rgb({int(h[1:3], 16)}, {int(h[3:5], 16)}, {int(h[5:7], 16)})"
                T.step("talking to Hilde: 3 pages on the five banners, +20 Hearth Tokens once, and the Factions tab opens", pages == 3 and "Warden Hilde" in first
                       and T.ev("window.__hm.S.merit.hearth") == h0 + 20 and T.ev("window.__hm.S.met.hilde") == 1, pages=pages, merit=T.ev("window.__hm.S.merit.hearth"))
                T.step("Factions tab: five rows, each edged + swatched in its signature glow colour, with a progress bar", [r[0] for r in rows] == ["hearth", "gate", "gnome", "corsair", "embassy"]
                       and [r[1] for r in rows] == [hexrgb(c) for c in cols] and [r[2] for r in rows] == [hexrgb(c) for c in cols] and all(r[3].endswith("%") for r in rows) and len(set(cols)) == 5, rows=rows)
                pg.keyboard.press("h"); pg.wait_for_timeout(250); shut = T.ev("!window.__hm.heroUI")
                pg.keyboard.press("h"); pg.wait_for_timeout(300)
                T.step("keyboard: H closes and opens the Factions tab", shut and T.ev("window.__hm.heroUI && window.__hm.hui.tab === 4"))
                pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
                T.ev("window.__hm.hui.tab = 0"); pg.keyboard.press("i"); pg.wait_for_timeout(250)
                pg.click("#heroTabs button:nth-child(5)"); pg.wait_for_timeout(250)
                T.step("touch: the hero screen's Factions tab button opens the panel", T.ev("window.__hm.hui.tab === 4") and T.ev("document.querySelector('#heroTabs button:nth-child(5)').classList.contains('on')"))
                T.ev("window.__hm.hui.tab = 0; window.__hm.drawHero && window.__hm.drawHero()"); pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
                T.step("the Guild reached Friend in the rift fights (abyssal seal)", T.ev("window.__hm.S.ranks.gate") >= 1 and T.ev("window.__hm.S.merit.gate") >= 210, merit=T.ev("window.__hm.S.merit.gate"))
                fa1 = T.ev("window.__hm.factions.qa()")
                T.step("Friend rewards are live: rift seals pay +25% gold; Odo's prices are 10% off at Hearth Friend",
                       T.ev("window.__hm.factions.riftGoldMul()") == 1.25 and T.ev("window.__hm.factions.priceMul('hearthmoor')") == (0.9 if T.ev("window.__hm.S.ranks.hearth") >= 1 else 1)
                       and T.ev("window.__hm.factions.priceMul('night')") == (0.85 if T.ev("window.__hm.S.ranks.corsair") >= 1 else 1), hearth=T.ev("window.__hm.S.ranks.hearth"))
                T.ev("window.__hm.loot.clear()")
                # controller: Start (log) -> RB (hero) -> LB / RB to Factions, d-pad down to the Guild, A wears its title
                T.btn(9); pg.wait_for_timeout(250); T.btn(5); pg.wait_for_timeout(250)
                for _ in range(5):
                    if T.ev("window.__hm.hui.tab") == 4: break
                    T.btn(4); pg.wait_for_timeout(200)
                T.btn(13); pg.wait_for_timeout(200); T.btn(0); pg.wait_for_timeout(300)
                head = T.ev("document.getElementById('heroHead').innerText")
                T.step("controller: Start, RB, LB to Factions, d-pad + A wears the Guild title (shown in the hero header)", T.ev("window.__hm.hui.tab") == 4 and T.ev("window.__hm.S.title") == "gate:1"
                       and T.ev("window.__hm.factions.title()") == "Rift Warden" and "Rift Warden" in head, title=T.ev("window.__hm.S.title"), head=head[:80])
                rep["shots"]["factions_panel"] = T.shot("factions_panel")
                T.btn(1); pg.wait_for_timeout(250)
                # save migration: a pre-factions save is seeded from finished errands, sealed rifts, the hunt log and the riddle; reload keeps merit
                mig = T.ev("""(() => { const o = JSON.parse(JSON.stringify(window.__hm.S)); delete o.merit; delete o.ranks; delete o.factionsV; delete o.title;
                  o.quests = { a: 3, b: 3, c: 1 }; o.rifts = { minor: 2, major: 1, abyssal: 0 }; o.hunt = { x: { base: 'deathlord', traits: ['shielded', 'swift'], kills: 1 }, y: { base: 'sporemother', traits: ['gloam'], kills: 1 } }; o.flags = { riddle: 'solved' };
                  const did = window.__hm.FA.migrate(o), again = window.__hm.FA.migrate(o); return { did, again, merit: o.merit, ranks: o.ranks, v: o.factionsV }; })()""")
                T.step("save migration: an old save gets merit seeded once (errands 80 + Death Lord 90 Hearth, rifts 120 Guild, Spore Mother 50 Embassy, riddle 60 Gnome)",
                       mig["did"] and not mig["again"] and mig["v"] == 1 and mig["merit"] == {"hearth": 170, "gate": 120, "gnome": 60, "corsair": 0, "embassy": 50} and mig["ranks"]["hearth"] == 1 and mig["ranks"]["gate"] == 0, mig=mig)
                T.ev("window.__hm.toast('✦ QA rank-up', 2.5, false, true); window.__hm.toast('QA loot toast', 1.5)")
                tq = T.ev("[document.getElementById('toast').innerText, window.__hm.toastQueue()]")
                T.wait("document.getElementById('toast').innerText === 'QA loot toast' && !document.getElementById('toast').hidden", 40)
                T.step("a rank-up toast has priority: a toast arriving while it shows waits in the queue, then shows", tq[0] == "✦ QA rank-up" and tq[1] == ["QA loot toast"], tq=tq)
                T.ev("window.__hm.save()")
                sv = T.ev("window.__hm.readSave(window.__hm.slot)")
                T.step("merit, ranks and the worn title are saved in the slot", sv and sv["merit"]["gate"] == fa1["merit"]["gate"] and sv["ranks"]["gate"] >= 1 and sv["title"] == "gate:1" and sv["factionsV"] == 1,
                       saved=sv and {"merit": sv["merit"], "title": sv.get("title")})
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
                # ---------------------------------------------------------- weather: calendar, rain + wet glints, Options toggle
                cal = T.ev("""(() => { const W = window.__hm.weatherAt, k = new Set(), same = []; for (let d = 0; d < 12; d++) for (let t = 0; t < 1; t += 0.125) { k.add(W('plaza', d, t)); same.push(W('plaza', d, t) === W('lane', d, t)); }
                  return { town: [...k].sort(), same: same.every(Boolean), glen: [W('mossglen', 3, 0.3), W('mossglen', 3, 0.6)], hollow: [W('hollows', 3, 0.9), W('hollows', 3, 0.1), W('hollows', 3, 0.5)] }; })()""")
                T.step("weather calendar: Plaza + Lane share a sky of clear / drizzle / rain blocks; Mossglen misty mornings; Hollows glow mist at night",
                       cal["town"] == ["clear", "drizzle", "rain"] and cal["same"] and cal["glen"] == ["mist", "clear"] and cal["hollow"] == ["glowmist", "glowmist", "clear"], cal=cal)
                T.ev("window.__hd2d.setTime(0.95); window.__hm.weather.force('rain')"); pg.wait_for_timeout(3500)
                wq = T.ev("window.__hm.weather.qa()")
                T.step("rain at night: drops + splashes fall, the cobbles get wet and lamps / pools throw palette glints (no bloom)",
                       wq["kind"] == "rain" and wq["mode"] == "on" and wq["parts"].get("rain", 0) > 20 and wq["parts"].get("rain_splash", 0) > 0 and wq["wet"] > 0.05
                       and wq["glints"] > 0 and wq["parts"].get("wet_glint", 0) > 0, wq=wq)
                pg.keyboard.press("o"); pg.wait_for_timeout(250)
                T.ev("document.getElementById('btnWeather').click()"); pg.wait_for_timeout(200)
                w1 = T.ev("[window.__hm.weather.mode, window.__hm.weather.qa().emitters.map((e) => e.rate), document.getElementById('btnWeather').textContent]")
                pg.keyboard.press("r"); pg.wait_for_timeout(200)
                w2 = T.ev("[window.__hm.weather.mode, window.__hm.weather.qa().emitters.length]")
                T.btn(3); pg.wait_for_timeout(250)
                w3 = T.ev("[window.__hm.weather.mode, window.__hm.weather.qa().emitters.map((e) => e.rate), window.__hm.opts]")
                pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
                T.step("Options: weather on -> light (mouse: half the rain) -> off (R: no weather) -> on (controller Y)",
                       w1[0] == "light" and w1[1] == [0.8] and "light" in w1[2] and w2 == ["off", 0] and w3[0] == "on" and w3[1] == [1.6] and w3[2], w1=w1, w2=w2, w3=w3)
                T.ev("window.__hm.weather.force(null)")
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
                seg_done("B"); cp_dump(pg, "cp2")
            if "C" in segs:
                seg_mark("C")
                if "B" not in segs:   # sharded: start from segment B's checkpoint (its K save in Bakery Lane)
                    cp_load(pg, T, url, "cp2")
                pg.reload()
                T.wait("window.__hm && window.__hm.ready && window.__hd2d.ready", 120)
                pg.wait_for_timeout(400)
                T.ev("__padPlug(true)"); pg.wait_for_timeout(500)
                T.btn(0)     # A on the title = Continue
                T.idle()
                S = T.S()
                T.step("reload #2: controller A on the title Continues; finished game state restored in Bakery Lane", T.ev("window.__hm.area") == "lane" and all(v == 3 for v in S["quests"].values())
                       and set(S["spells"]) >= {"sparkle_burst", "hearth_flame", "light_orb", "leaf_gust"})
                T.step("dialogue answers survive a reload (Bram's lantern wish, Bix's riddle)", (S.get("flags") or {}).get("lantern") == "lost" and (S.get("flags") or {}).get("riddle") == "solved", flags=S.get("flags"))
                # ---------------------------------------------------------- stage 4: the Rift Shrine + Vanaheim (errands done: the moss gate asks)
                area = T.go_rect("exits")
                T.step("lane -> plaza (to the moss gate)", area == "plaza")
                r = T.ev("window.__hm.ctx.scene.game.portals[0].rect")
                T.ev(f"window.__hm.ctx.walkTo({(r[0] + r[2]) / 2}, {(r[1] + r[3]) / 2})")
                T.wait("window.__hm.dlgChoice && window.__hm.dlgChoice()", 90)
                ch = T.ev("window.__hm.dlgChoice()")
                rep["shots"]["rift_gate_choice"] = T.shot("rift_gate_choice")
                pg.keyboard.press("ArrowDown"); pg.wait_for_timeout(150); pg.keyboard.press("e")
                T.wait("window.__hm.area === 'rift' || window.__hm.busy", 60); T.idle(); pg.wait_for_timeout(600)
                T.step("the moss gate (3 errands done) asks Mossglen or the Rift Shrine; arrow down + E steps through to the Rift Shrine",
                       bool(ch) and len(ch["options"]) == 3 and "Mossglen" in ch["options"][0] and "Rift" in ch["options"][1] and T.ev("window.__hm.area") == "rift", choice=ch)
                g = T.ev("(() => { const c = window.__hm.ctx, f = c.fx; return { open: f.gate_vanaheim && f.gate_vanaheim.name, seals: ['alfheim', 'niflheim', 'muspelheim'].map((k) => f['gate_' + k] && f['gate_' + k].name),"
                         " home: f.portal_0 && f.portal_0.name, ring: f.shrine_ring && f.shrine_ring.name, sealed: c.scene.game.sealed.length, glows: window.__hm.glow.fixed.length }; })()")
                T.step("Rift Shrine: Vanaheim's gate swirls open (cold-fire vortex), three sealed gates glow faintly (violet / blue / red), a moss gate home",
                       g["open"] == "rift_vortex" and g["seals"] == ["rift_seal_violet", "rift_seal_blue", "rift_seal_red"] and g["home"] == "portal_vortex" and g["ring"] == "rift_ring" and g["sealed"] == 3 and g["glows"] >= 4, g=g)
                p0 = T.pos()
                T.ev("(() => { const c = window.__hm.ctx, p = c.player; p.x = 0; p.z = 3.0; p.y = c.heightAt(0, 3.0); c.stopWalk(); })()"); pg.wait_for_timeout(500)
                cv = T.ev("(() => { const r = document.getElementById('view').getBoundingClientRect(); return [r.left + r.width * 0.42, r.top + r.height * 0.42]; })()")
                pg.mouse.click(cv[0], cv[1]); pg.wait_for_timeout(300)
                walking = T.ev("window.__hm.ctx.walking()")
                T.wait("!window.__hm.ctx.walking()", 60); p1 = T.pos()
                T.walk(7.6, 5.4); pe = T.pos(); edge = round(((pe[0]) ** 2 + (pe[1] + 1.0) ** 2) ** 0.5, 2)
                T.step("mouse: clicking the floating isle's paving walks there (the isle top is walkable); walking at the void stops at the round edge",
                       walking and abs(p1[0]) + abs(p1[1] - 3.0) > 0.8 and 6.0 < edge < 7.55, p1=p1, edge=edge)
                T.ev("(() => { const c = window.__hm.ctx, p = c.player; p.x = -3.4; p.z = -4.9; p.y = c.heightAt(-3.4, -4.9); c.stopWalk(); })()"); pg.wait_for_timeout(400)
                pr = T.ev("document.getElementById('prompt').textContent")
                T.btn(0); pg.wait_for_timeout(300)
                who = T.ev("window.__hm.dlg ? window.__hm.dlg.npc.id : null"); txt = T.ev("window.__hm.dlg ? window.__hm.dlg.pages[0] : ''")
                n = 0
                while T.ev("!!window.__hm.dlg") and n < 10:
                    T.btn(0, 200); n += 1
                T.step("controller: A at a sealed gate (Alfheim, violet) explains it is frozen shut; the prompt names the realm",
                       who == "sealed_alfheim" and "froze it shut" in txt and "Alfheim" in pr and n >= 1, prompt=pr, who=who)
                area = T.go_rect("portals", 1)
                en = T.ev("window.__hm.combat.enemies.map((e) => e.a.role)")
                T.step("Vanaheim's gate -> Mossbrook Springs: spore elementals + a moss golem, Veyra's violet runes, a vine gate home",
                       area == "vanaheim" and en.count("sporeling") >= 2 and "mossgolem" in en and T.ev("window.__hm.ctx.fx.rune_spring.name") == "alf_rune"
                       and T.ev("window.__hm.ctx.fx.gate_rift.name") == "rift_vortex", enemies=en)
                T.talk("warden", keep_open=True); ch = T.to_choice()
                rep["shots"]["alliance_choice"] = T.shot("alliance_choice")
                pg.keyboard.press("1"); pg.wait_for_timeout(300)
                reply = T.ev("window.__hm.dlg ? window.__hm.dlg.pages[0] : ''"); T.read_all()
                T.step("the spring-warden asks what you are to Vanaheim (befriend / conquer / not now); key 1 befriends: the alliance flag is set",
                       bool(ch) and len(ch["options"]) == 3 and "friend" in ch["options"][0].lower() and "bow" in ch["options"][1].lower()
                       and T.ev("window.__hm.S.flags.alliance.vanaheim") == "befriend" and "welcome in Mossbrook" in reply, choice=ch, reply=reply[:60])
                pages, first = T.talk("warden")
                T.step("afterwards the warden greets a friend of Mossbrook (no second ask)", "Friend of Mossbrook" in first and pages == 1, line=first[:60])
                area = T.go_rect("portals", 0)
                a2 = T.go_rect("portals", 0)
                T.step("way back: the vine gate returns to the Rift Shrine, its moss gate home to the Plaza", area == "rift" and a2 == "plaza" and T.ev("window.__hm.S.flags.alliance.vanaheim") == "befriend")
                # ---------------------------------------------------------- stage 5 part 4: Ravenhold Harbor (Bakery Lane's west road)
                area = T.go_rect("exits")   # plaza -> lane
                ln = T.ev("(() => { const g = window.__hm.ctx.scene.game; return { ex: g.exits.map((e) => e.to), way: !!g.waystone, glb: window.__hm.ctx.scene.objects.some((o) => o.glb.endsWith('/waystone.glb')) }; })()")
                a3 = T.go_rect("exits", 1)
                rh = T.ev("""(() => { const c = window.__hm.ctx, sc = c.scene, glb = (n) => sc.objects.filter((o) => o.glb.endsWith('/' + n + '.glb')).length;
                  return { water: glb('harbor_water'), piers: glb('pier'), boats: glb('skiff') + glb('rowboat'), lanterns: glb('quay_lantern') + glb('pier_lantern'),
                           cold: sc.lamps.filter((l) => l.color === '#5ab4f0').length, toads: glb('toadstool_cluster') + glb('toadstool_big'), spring: glb('spring_basin'),
                           gates: sc.game.sealed.filter((g) => g.district).map((g) => g.id), soon: sc.game.sealed.every((g) => g.say.join(' ').includes('oming soon')),
                           npcs: ['harbormaster', 'quartermaster', 'chandler', 'dockkid'].filter((i) => c.npc(i)), realm: window.__hm.factions.realm(),
                           orbs: glb('fish_orb'), floats: glb('float_lantern_violet') + glb('float_lantern_red'), pools: window.__hm.glow.fixed.map((f) => f.kind) }; })()""")
                T.step("Bakery Lane's west road (by its new waystone) -> Ravenhold Harbor: piers, boats, dark water, cold-fire lanterns + light pools, violet / red floats, fish orbs, toadstools, a spring, 4 sealed gates, 4 NPCs",
                       area == "lane" and ln["ex"] == ["plaza", "ravenhold"] and ln["way"] and ln["glb"] and a3 == "ravenhold" and rh["water"] == 1 and rh["piers"] == 2 and rh["boats"] >= 4
                       and rh["lanterns"] >= 5 and rh["cold"] >= 6 and rh["toads"] >= 4 and rh["spring"] == 1 and rh["gates"] == ["market", "temple", "forge", "undercity"] and rh["soon"]
                       and len(rh["npcs"]) == 4 and rh["realm"] == "corsair" and rh["orbs"] == 3 and rh["floats"] == 3
                       and rh["pools"].count("cold") >= 8 and "violet" in rh["pools"] and "red" in rh["pools"], lane=ln, rh=rh)
                T.ev("window.__hd2d.setTime('night')"); pg.wait_for_timeout(900)
                rep["shots"]["ravenhold_night"] = T.shot("ravenhold_night")
                # keys: E with the harbormaster (quest tag) starts the story quest; it is not one of the three errands
                mk0 = T.ev("window.__hm.markers.harbormaster ? window.__hm.markers.harbormaster.name : null")
                T.talk("harbormaster")
                S = T.S()
                T.step("keys: E with Harbormaster Brannoc (quest tag) starts the story quest 'The Road to the Rift'; the log lists it, the errand count stays 3/3",
                       mk0 == "quest_mark" and S["quests"].get("harbor") == 1 and "The Road to the Rift" in T.ev("document.getElementById('logList').innerText")
                       and T.ev("document.getElementById('btnLog').textContent") == "quests 3/3"
                       and T.ev("window.__hm.markers.quartermaster ? window.__hm.markers.quartermaster.name : null") == "quest_turnin", tag=mk0)
                # controller: A with Quartermaster Sable (Rift Corsairs): merit for meeting her, the quest moves on
                c0 = T.ev("window.__hm.S.merit.corsair")
                T.talk_pad("quartermaster")
                c1 = T.ev("window.__hm.S.merit.corsair")
                T.step("controller: A with Quartermaster Sable of the Rift Corsairs: +20 Corsair merit for meeting her; the quest moves on to the Market Terraces gate",
                       c1 - c0 == 20 and T.ev("window.__hm.S.quests.harbor") == 2, merit=[c0, c1])
                # keys: up the harbor stair; the Market Terraces gate is sealed, coming soon (E looks, the quest notes it)
                T.walk(0.5, -10.2)
                pr = T.ev("document.getElementById('prompt').textContent")
                pg.keyboard.press("e"); pg.wait_for_timeout(300)
                who = T.ev("window.__hm.dlg ? window.__hm.dlg.npc.id : null"); txt = T.ev("window.__hm.dlg ? window.__hm.dlg.pages.join(' ') : ''")
                T.read_all()
                T.step("keys: up the harbor stair onto the 3 m terrace, E at the Market Terraces gate: sealed, coming soon; the quest notes it",
                       T.ev("window.__hm.ctx.player.y") > 2.9 and "Market Terraces" in pr and "coming soon" in pr and who == "sealed_market" and "Coming soon" in txt
                       and T.ev("window.__hm.S.flags.rh_gate") == 1, prompt=pr, who=who, y=T.ev("window.__hm.ctx.player.y"))
                # back to Brannoc: the Market Terraces stay sealed, so he pays (Corsair merit + gold) and sends you the other way, by
                # Sable's rift-skiff up to Bifrost Crossing (Stage 6 part 1); the quest moves to its skiff step
                c2 = T.ev("window.__hm.S.merit.corsair"); g0 = T.ev("window.__hm.S.gold || 0")
                mk1 = T.ev("window.__hm.markers.harbormaster ? window.__hm.markers.harbormaster.name : null")
                T.talk("harbormaster", keep_open=True)
                alltxt = T.ev("window.__hm.dlg.pages.join(' ')"); pg.wait_for_timeout(1600)
                rep["shots"]["ravenhold_quest"] = T.shot("ravenhold_quest")
                T.read_all(); pg.wait_for_timeout(300)
                S = T.S()
                lg = T.ev("document.getElementById('logList').innerText")
                T.step("Brannoc (turn-in tag): the Market Terraces stay sealed, so he sends you by Sable's rift-skiff to Bifrost Crossing; +40 Corsair merit, +30 gold; the log shows the skiff step; errands stay 3/3",
                       mk1 == "quest_turnin" and S["quests"]["harbor"] == 2 and S["flags"].get("rh_road") == 1 and "Market Terraces" in alltxt and "Bifrost Crossing" in alltxt
                       and "rift-skiff" in alltxt and S["merit"]["corsair"] - c2 == 40 and (S.get("gold") or 0) - g0 == 30 and "rift-skiff" in lg and "Gatekeepers' Guild" in lg
                       and T.ev("document.getElementById('btnLog').textContent") == "quests 3/3" and not T.ev("window.__hm.markers.harbormaster"), merit=[c2, S["merit"]["corsair"]])
                # the chandler's shop (her own stock)
                T.talk("chandler")
                sh = T.ev("[window.__hm.shop, window.__hm.shopUI.open, document.getElementById('shopName') ? document.getElementById('shopName').textContent : '']")
                pg.keyboard.press("Escape"); pg.wait_for_timeout(300)
                T.step("Ida Wickmere the chandler opens Wickmere's Chandlery (tonics, glow seeds, a rift shard, harbor kit); Esc closes it", sh[0] is True and sh[1] == "harbor" and not T.ev("window.__hm.shop"), shop=sh)
                # the hidden bubbly spring in the west corner, behind the crates: heals + spring-fizz, a first find is a secret (Gnome Council merit)
                n0 = T.ev("window.__hm.S.merit.gnome")
                T.walk(-16.4, -7.4); pg.wait_for_timeout(600)
                T.step("the hidden spring behind the crates fizzes (spring-fizz buff); a first find is a secret: +40 Gnome Council merit",
                       T.ev("window.__hm.hollows.buffOn()") and T.ev("window.__hm.S.found.rh_spring") == 1 and T.ev("window.__hm.S.merit.gnome") - n0 == 40, merit=[n0, T.ev("window.__hm.S.merit.gnome")])
                # mouse: click the waystone (walks up), click again (its travel choice), key 1 travels to Bakery Lane
                T.walk(13.0, -1.6)
                def click_world(x, z):
                    s_ = T.ev(f"(() => {{ const c = window.__hd2d.ctx; return c.project({x}, c.heightAt({x}, {z}), {z}); }})()")
                    pg.mouse.click(s_["x"], s_["y"]); pg.wait_for_timeout(300)
                click_world(15.0, -3.6); T.wait("!window.__hm.ctx.walking()", 60); pg.wait_for_timeout(300)
                near = T.ev("window.__hm.harbor.near()")
                click_world(15.0, -3.6)
                wc = T.to_choice()
                pg.keyboard.press("1")
                T.wait("window.__hm.area === 'lane' && !window.__hm.busy", 90); T.idle(); pg.wait_for_timeout(400)
                T.step("mouse: clicking Ravenhold's waystone walks up to it, a second click opens its travel choice; key 1 travels to Bakery Lane's waystone",
                       near and bool(wc) and "Bakery Lane" in wc["options"][0] and T.ev("window.__hm.area") == "lane" and T.ev("window.__hm.harbor.near(3.2)"), choice=wc)
                # controller: A at Bakery Lane's waystone, A picks 'Travel to Ravenhold Harbor'
                T.walk(-13.4, 3.2)
                n = 0
                # stop pressing once the travel has started (busy): a press during the area load can't be polled
                while T.ev("window.__hm.area === 'lane' && !window.__hm.busy") and n < 10:
                    T.btn(0, 200); n += 1
                T.wait("window.__hm.area === 'ravenhold' && !window.__hm.busy", 90); T.idle(); pg.wait_for_timeout(400)
                T.step("controller: A at Bakery Lane's waystone opens it, A again travels to Ravenhold Harbor (by its waystone)",
                       T.ev("window.__hm.area") == "ravenhold" and T.ev("window.__hm.harbor.near(3.2)") and T.ev("(window.__hm.S.flags.ways || {}).lane") == 1, presses=n)
                # ---------------------------------------------------------- stage 6 part 1: Bifrost Crossing, by Sable's rift-skiff
                T.walk(6.6, 4.6)
                pr = T.ev("document.getElementById('prompt').textContent")
                pg.keyboard.press("e"); pg.wait_for_timeout(300)
                fc = T.to_choice()
                pg.keyboard.press("1")
                T.wait("window.__hm.area === 'bifrost' && !window.__hm.busy", 90); T.idle(); pg.wait_for_timeout(600)
                bf = T.ev("""(() => { const c = window.__hm.ctx, sc = c.scene, g = sc.game, glb = (n) => sc.objects.filter((o) => o.glb.endsWith('/' + n + '.glb')).length;
                  const fx = Object.values(c.fx).map((f) => f.name);
                  return { arches: glb('realm_arch'), glows: sc.objects.filter((o) => /realm_glow_/.test(o.glb)).length, seals: fx.filter((n) => n.startsWith('rift_seal_')).length,
                           vortex: c.fx.gate_vanaheim ? c.fx.gate_vanaheim.name : null, sealed: g.sealed.map((s) => s.arch), portal: g.portals.map((p) => p.to),
                           isle: [glb('bifrost_plaza'), glb('bifrost_bridge'), glb('bifrost_landing')], skiff: glb('skiff'), way: glb('waystone'), kiosk: glb('guild_kiosk'),
                           braz: ['cold', 'violet', 'red'].map((k) => glb('rift_brazier_' + k)), toads: glb('toadstool_cluster') + glb('toadstool_big'),
                           npc: !!c.npc('gatewright'), realm: window.__hm.factions.realm(), pools: window.__hm.glow.fixed.map((f) => f.kind),
                           glowN: c.glowN, cap: window.__hm.glowCap(), terrace: c.heightAt(0, -10.5), seen: window.__hm.S.flags.bf_seen,
                           pos: [c.player.x, c.player.z] }; })()""")
                T.step("keys: E at Sable's rift-skiff on Ravenhold's east pier (Brannoc's word given) opens its choice; key 1 sails to Bifrost Crossing's landing",
                       "rift-skiff" in pr and bool(fc) and "Bifrost Crossing" in fc["options"][0] and T.ev("window.__hm.area") == "bifrost" and bf["pos"][1] > 11.5, prompt=pr, choice=fc, pos=bf["pos"])
                T.step("Bifrost Crossing: a floating plaza, rainbow bridge + skiff landing, 9 realm gates (8 sealed seals + Vanaheim's open swirl) on a 1.2 m gate terrace, the Guild kiosk + gatewright, a waystone, cold-fire / violet / red braziers + pools, toadstools; pooled lights at the cap",
                       bf["arches"] == 9 and bf["glows"] == 9 and bf["seals"] == 8 and bf["vortex"] == "rift_vortex" and len(bf["sealed"]) == 8 and bf["portal"] == ["vanaheim"]
                       and bf["isle"] == [1, 1, 1] and bf["skiff"] == 1 and bf["way"] == 1 and bf["kiosk"] == 1 and bf["braz"] == [4, 1, 1] and bf["toads"] >= 6
                       and bf["npc"] and bf["realm"] == "gate" and bf["pools"].count("cold") >= 6 and "violet" in bf["pools"] and "red" in bf["pools"]
                       and bf["glowN"] == bf["cap"] == 3 and abs(bf["terrace"] - 1.2) < 0.01 and bf["seen"] == 1, bf=bf)
                T.ev("window.__hd2d.setTime('night')"); pg.wait_for_timeout(900)
                rep["shots"]["bifrost_night"] = T.shot("bifrost_night")
                # controller: A with Gatewright Halvard Ness (turn-in tag) finishes the harbor story quest at the Crossing
                g0 = T.ev("window.__hm.S.merit.gate"); gd0 = T.ev("window.__hm.S.gold || 0"); gm0 = T.ev("(window.__hm.S.gems || {}).rift_shard || 0")
                mk2 = T.ev("window.__hm.markers.gatewright ? window.__hm.markers.gatewright.name : null")
                T.talk_pad("gatewright")
                S = T.S(); lg = T.ev("document.getElementById('logList').innerText")
                T.step("controller: A with Gatewright Halvard Ness (turn-in tag) finishes 'The Road to the Rift' at the Crossing: +80 Rift Marks (meeting + quest), +50 gold, a rift shard; errands stay 3/3",
                       mk2 == "quest_turnin" and S["quests"]["harbor"] == 3 and S["flags"].get("bf_done") == 1 and S["merit"]["gate"] - g0 == 80 and (S.get("gold") or 0) - gd0 == 50
                       and (S.get("gems") or {}).get("rift_shard", 0) - gm0 == 1 and "Guild ledger" in lg and T.ev("document.getElementById('btnLog').textContent") == "quests 3/3"
                       and not T.ev("window.__hm.markers.gatewright"), merit=[g0, S["merit"]["gate"]], gold=[gd0, S.get("gold")])
                # keys: E at a sealed realm gate says why it is shut, the key it needs (a faction rank) and where you stand
                T.walk(-6.6, -3.6)
                pr = T.ev("document.getElementById('prompt').textContent")
                pg.keyboard.press("e"); pg.wait_for_timeout(300)
                who = T.ev("window.__hm.dlg ? window.__hm.dlg.npc.id : null"); txt = T.ev("window.__hm.dlg ? window.__hm.dlg.pages.join(' ') : ''")
                T.read_all()
                T.step("keys: E at Svartalfheim's sealed gate (copper light): why it is shut, its key (Gnome Council at Trusted) and your standing",
                       who == "sealed_svartalfheim" and "Svartalfheim" in pr and "Gnome Council" in txt and "Trusted" in txt and "You:" in txt and "Gilded Acorns" in txt, prompt=pr, txt=txt[:160])
                # mouse: up the gate stair, click Vanaheim's open gate: it walks in (Mossbrook Springs)
                T.walk(0.0, -9.8)
                yt = T.ev("window.__hm.ctx.player.y")
                click_world(0.0, -11.6)
                T.wait("window.__hm.area === 'vanaheim' && !window.__hm.busy", 90); T.idle(); pg.wait_for_timeout(400)
                T.step("mouse: up the gate stair onto the 1.2 m terrace, clicking Vanaheim's open gate walks into its swirl: Mossbrook Springs", yt > 1.1 and T.ev("window.__hm.area") == "vanaheim", y=yt)
                # Vanaheim's vine gate now asks where to: the Rift Shrine or Bifrost Crossing; key 2 steps out of Bifrost's open gate
                r = T.ev("window.__hm.ctx.scene.game.portals[0].rect")
                T.ev(f"window.__hm.ctx.walkTo({(r[0] + r[2]) / 2}, {(r[1] + r[3]) / 2})")
                T.wait("window.__hm.dlgChoice && window.__hm.dlgChoice()", 90); pg.wait_for_timeout(300)
                vc = T.ev("window.__hm.dlgChoice()")
                pg.keyboard.press("2")
                T.wait("window.__hm.area === 'bifrost' && !window.__hm.busy", 90); T.idle(); pg.wait_for_timeout(400)
                T.step("Vanaheim's vine gate (Bifrost seen) asks: the Rift Shrine or Bifrost Crossing; key 2 steps out of the Crossing's Vanaheim gate on the terrace",
                       bool(vc) and len(vc["options"]) == 3 and "Rift Shrine" in vc["options"][0] and "Bifrost" in vc["options"][1] and T.ev("window.__hm.area") == "bifrost"
                       and T.ev("window.__hm.ctx.player.y") > 1.1, choice=vc)
                # controller: A at the Crossing's waystone, A again takes its first row (Bakery Lane); the Lane's waystone now lists Bifrost
                T.walk(3.6, 0.0)
                n = 0
                while T.ev("window.__hm.area === 'bifrost' && !window.__hm.busy") and n < 10:
                    T.btn(0, 200); n += 1
                T.wait("window.__hm.area === 'lane' && !window.__hm.busy", 90); T.idle(); pg.wait_for_timeout(400)
                a4 = T.ev("window.__hm.area")
                T.walk(-13.4, 3.2)
                pg.keyboard.press("e"); pg.wait_for_timeout(300)
                lc = T.to_choice()
                pg.keyboard.press("1")
                T.wait("window.__hm.area === 'ravenhold' && !window.__hm.busy", 90); T.idle(); pg.wait_for_timeout(400)
                T.step("controller: A at Bifrost's waystone travels to Bakery Lane; the Lane's waystone now lists Bifrost Crossing too (attuned), key 1 goes on to Ravenhold",
                       a4 == "lane" and bool(lc) and "Ravenhold" in lc["options"][0] and "Bifrost Crossing" in lc["options"][1] and T.ev("window.__hm.area") == "ravenhold"
                       and T.ev("(window.__hm.S.flags.ways || {}).bifrost") == 1, presses=n, choice=lc)
                area = T.go_rect("exits", 0)
                T.step("the road east from the harbor leads back to Bakery Lane", area == "lane")
                T.step("no JS errors", not errors and not T.ev("window.__hd2d.errors.length"), errors=errors[:5])
                seg_done("C"); cp_dump(pg, "cp3")
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
        if rep["pass"] and "D" in segs:
            seg_mark("D")
            try:
                saved = pg.evaluate("localStorage.getItem('hearthmoor-slot-1-v2')") if "C" in segs else cp_load(None, T, url, "cp3")["hearthmoor-slot-1-v2"]
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
                q.wait_for_timeout(300)
                def tap_el(sel):   # real touch (CDP, the suite's own timestamps) on an element's centre
                    c = T.ev(f"(() => {{ const r = document.querySelector('{sel}').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }})()")
                    tap(c[0], c[1]); q.wait_for_timeout(300)
                pm = [T.ev("window.__hm.weather.mode")]
                tap_el("#btnOpts"); tap_el("#btnWeather")
                pm.append(T.ev("[window.__hm.weather.mode, window.__hm.weather.qa().emitters.length]"))
                tap_el("#btnWeather"); tap_el("#btnWeather")
                pm.append(T.ev("window.__hm.weather.mode")); tap_el("#optsClose")
                T.step("phone: weather defaults to light; the Options button cycles light -> off -> on -> light by touch", pm == ["light", ["off", 0], "light"] and not T.ev("window.__hm.opts"), modes=pm)
                # touch: the moss gate's destination choice (errands done) takes a tap on a row
                r = T.ev("window.__hm.ctx.scene.game.portals[0].rect")
                T.ev(f"window.__hm.ctx.walkTo({(r[0] + r[2]) / 2}, {(r[1] + r[3]) / 2})")
                T.wait("window.__hm.dlgChoice && window.__hm.dlgChoice()", 90); q.wait_for_timeout(300)
                gc = T.ev("window.__hm.dlgChoice()")
                tap_el('#dlgChoices .choice[data-i="2"]'); q.wait_for_timeout(300)
                T.step("touch: tapping 'Stay here.' on the moss gate's choice closes it and stays in the Plaza",
                       bool(gc) and len(gc["options"]) == 3 and not T.ev("!!window.__hm.dlg") and T.ev("window.__hm.area") == "plaza" and T.ev("window.__hm.S.chose.moss_gate") == 2, choice=gc)
                T.ev("window.__hm.intro.start(true)"); T.wait("window.__hm.intro.state().lanterns === 7", 30); q.wait_for_timeout(400)
                on = T.ev("window.__hm.intro.active && !document.getElementById('introSkip').hidden")
                sk = T.ev("(() => { const r = document.getElementById('introSkip').getBoundingClientRect(); return [r.width, r.height]; })()")
                tap_el("#introSkip")
                T.step("touch: tapping 'skip' ends the Lantern Eve opening (thumb-sized chip)", on and sk[0] >= 30 and sk[1] >= 30 and not T.ev("window.__hm.intro.active")
                       and T.ev("document.getElementById('introSkip').hidden") and T.ev("window.__hm.S.flags.intro") == "skipped", chip=sk)
                # touch: Ravenhold's waystone takes a tap to walk up and a second tap to open; tapping 'Stay here.' closes it
                T.ev("window.__hm.go('ravenhold', 'from_lane')"); T.wait("window.__hm.area === 'ravenhold' && !window.__hm.busy", 90); T.idle(); q.wait_for_timeout(600)
                def tap_world(x, z):
                    s_ = T.ev(f"(() => {{ const c = window.__hd2d.ctx; const s = c.project({x}, c.heightAt({x}, {z}), {z}); const el = document.elementFromPoint(s.x, s.y); return [s.x, s.y, el ? el.tagName : null]; }})()")
                    tap(s_[0], s_[1]); q.wait_for_timeout(300); return s_[2]
                el1 = tap_world(15.0, -3.6); T.wait("!window.__hm.ctx.walking()", 60); q.wait_for_timeout(300)
                near = T.ev("window.__hm.harbor.near()")
                tap_world(15.0, -3.6)
                T.wait("window.__hm.dlgChoice && window.__hm.dlgChoice()", 60); q.wait_for_timeout(300)
                wc = T.ev("window.__hm.dlgChoice()")
                stay = len(wc["options"]) - 1 if wc else 1   # 'Stay here.' is the last row (Bifrost Crossing is attuned by now)
                tap_el(f'#dlgChoices .choice[data-i="{stay}"]'); q.wait_for_timeout(300)
                T.step("touch: tapping Ravenhold's waystone walks up to it, a second tap opens its travel choice (Lane + Bifrost); tapping 'Stay here.' stays in the harbor",
                       el1 == "CANVAS" and near and bool(wc) and "Bakery Lane" in wc["options"][0] and "Bifrost" in wc["options"][1] and wc["options"][stay].startswith("Stay")
                       and not T.ev("!!window.__hm.dlg") and T.ev("window.__hm.area") == "ravenhold", choice=wc, el=el1)
                # touch: Bifrost Crossing's Midgard gate (rainbow seal) takes a tap to walk up and a second tap to look.
                # Phone portrait's HFOV can't see x=11 from the waystone spawn; walk into camera range first (same idea as Ravenhold spawning next to its waystone).
                T.ev("window.__hm.go('bifrost', 'from_waystone')"); T.wait("window.__hm.area === 'bifrost' && !window.__hm.busy", 90); T.idle(); q.wait_for_timeout(600)
                T.walk(8.5, -2.5); q.wait_for_timeout(300)
                el2 = tap_world(11.0, -4.2); T.wait("!window.__hm.ctx.walking()", 60); q.wait_for_timeout(300)
                pz = T.ev("[window.__hm.ctx.player.x, window.__hm.ctx.player.z]")
                tap_world(11.0, -4.2); q.wait_for_timeout(300)
                who = T.ev("window.__hm.dlg ? window.__hm.dlg.npc.id : null"); txt = T.ev("window.__hm.dlg ? window.__hm.dlg.pages.join(' ') : ''")
                T.read_all()
                T.step("touch: tapping Midgard's sealed gate at the Crossing walks up to it, a second tap looks: the Old Temple's Rift-gate is dark, its key is Hearth merit",
                       el2 == "CANVAS" and abs(pz[0] - 11.0) < 1.3 and who == "sealed_midgard" and "Old Temple" in txt and "Order of the Hearth" in txt and not T.ev("!!window.__hm.dlg"), pos=pz, who=who)
                T.ev("window.__hm.go('plaza', 'from_lane')"); T.wait("window.__hm.area === 'plaza' && !window.__hm.busy", 90); T.idle(); q.wait_for_timeout(400)
                T.walk(-1.4, -5.6)
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
                seg_done("D")
            except Exception as e:  # noqa: BLE001
                rep["pass"] = False
                rep["error"] = f"phone: {e}"[:400]
        # ---------------------------------------------------------- v1 save migration (old saves still load)
        if rep["pass"] and "E" in segs:
            seg_mark("E")
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
                seg_done("E")
            except Exception as e:  # noqa: BLE001
                rep["pass"] = False
                rep["error"] = f"migration: {e}"[:400]
        # ---------------------------------------------------------- F: the Stray Den + glowing pets (Stage 6 part 2, continues cp3)
        if rep["pass"] and "F" in segs:
            seg_mark("F")
            try:
                saved = cp_load(None, T, url, "cp3")["hearthmoor-slot-1-v2"]
                pc = b.new_context(viewport={"width": size[0], "height": size[1]})
                pc.add_init_script(f"if (!sessionStorage.getItem('seeded')) {{ localStorage.clear(); localStorage.setItem('hearthmoor-slot-1-v2', {json.dumps(saved)}); sessionStorage.setItem('seeded', '1'); }}")
                pc.add_init_script(STUB)
                f = pc.new_page()
                f.on("pageerror", lambda e: errors.append(f"PAGEERROR {e}"))
                f.on("console", lambda m: errors.append(f"console.error {m.text}") if m.type == "error" else None)
                T.pg = f
                f.goto(url)
                T.wait("window.__hm && window.__hm.ready && window.__hd2d && window.__hd2d.ready && !window.__hd2dGate.loading", 120)
                f.click("#btnCont"); T.idle(); f.wait_for_timeout(400)
                T.ev("window.__hm.loadArea('bifrost', 'start')"); T.wait("window.__hm.area === 'bifrost' && window.__hm.ctx && window.__hm.ctx.npc('denkeeper')", 120); T.idle(); f.wait_for_timeout(400)
                T.ev("(() => { const S = window.__hm.S; S.gold = Math.max(S.gold || 0, 200); })()")   # QA: enough gold for the Den's donation, whatever the fixture holds
                den = T.ev("""(() => { const G = window.__hm, c = G.ctx, sc = c.scene, glb = (n) => sc.objects.filter((o) => o.glb.endsWith('/' + n + '.glb')).length;
                  return { glb: [glb('stray_den'), glb('den_post'), glb('den_woodpile')], npc: !!c.npc('denkeeper'), name: c.npc('denkeeper').name, mark: G.markers.denkeeper ? G.markers.denkeeper.name : null,
                           lanterns: G.hollows.braziers.filter((b) => b.den).map((b) => b.lit), log: document.getElementById('logList').innerHTML.includes('Strays of the Rift'),
                           pet: G.S.pet, sheet: !!c.actors.sheetOf('pet_fox'), count: document.getElementById('btnLog').textContent }; })()""")
                T.step("the Stray Den at Bifrost: a round stone house, 3 yard lantern posts + a woodpile, Signe Larkspur with a quest tag; lanterns unlit, no pet, the side quest hidden in the log",
                       den["glb"] == [1, 3, 1] and den["npc"] and "Signe" in den["name"] and den["mark"] == "quest_mark" and den["lanterns"] == [False] * 3
                       and not den["log"] and den["pet"] is None and den["sheet"], den=den)
                # keys: E with Signe starts 'Strays of the Rift' (a side quest: 'Side:' in the log, never counted in quests n/3)
                pages, first = T.talk("denkeeper")
                S = T.S(); logh = T.ev("document.getElementById('logList').innerHTML")
                T.step("keys: E with Signe Larkspur (4 pages) starts the side quest 'Strays of the Rift': 'Side:' in the log, quests n/3 unchanged",
                       pages == 4 and "Signe Larkspur" in first and S["quests"].get("strays") == 1 and S["met"].get("signe") == 1 and "Side: Strays of the Rift" in logh
                       and "0/3" in logh and T.ev("document.getElementById('btnLog').textContent") == den["count"], first=first[:80])
                # cast beside each yard lantern: it lights (the Hollows brazier rule) and stays lit as a light zone
                lit = []
                for b_ in T.ev("window.__hm.hollows.braziers.filter((b) => b.den).map((b) => [b.id, b.pos])"):
                    T.walk(b_[1][0] + 0.6, b_[1][1] + 0.7)
                    for _ in range(3):
                        T.ev("window.__hm.combat.cd = {}"); f.keyboard.press("f"); f.wait_for_timeout(700)
                        if T.ev(f"!!window.__hm.S.found.{b_[0]}"): break
                    lit.append(T.ev(f"!!window.__hm.S.found.{b_[0]}"))
                T.frames(6)
                ln = T.ev("""(() => { const G = window.__hm; return { burning: G.hollows.braziers.filter((b) => b.den && b.burning).length, zones: G.glow.zones().filter((z) => z.src === 'brazier').length,
                  toast: document.getElementById('toast').innerText, mark: G.markers.denkeeper ? G.markers.denkeeper.name : null, step: document.getElementById('logList').innerText }; })()""")
                T.step("cast any spell beside each Den yard lantern: all 3 light and stay lit (cold-fire flames + light zones); Signe shows a turn-in tag",
                       lit == [True] * 3 and ln["burning"] == 3 and ln["zones"] >= 3 and ln["mark"] == "quest_turnin" and "Tell Signe the lanterns are lit" in ln["step"], lanterns=ln)
                # turn in: Signe opens the little rift behind the woodpile (scripted tier I: 2 wraiths + a skeleton, no rare, never closes by itself)
                g0 = T.ev("window.__hm.S.merit.gate")
                T.talk("denkeeper")
                rs = T.ev("window.__hm.rifts.state()")
                def to_den(n=30):
                    """page through Signe's lines until the Den's own scene opens (E on its choice page would pick an answer)"""
                    for _ in range(n):
                        if T.ev("!!(window.__hm.dlg && window.__hm.dlg.npc.id === 'den')"):
                            return
                        if T.ev("!!(window.__hm.dlg && window.__hm.dlg.picking)"):
                            raise AssertionError("unexpected choice before the Den scene")
                        f.keyboard.press("e"); f.wait_for_timeout(160)
                    raise AssertionError("the Den scene never opened")
                KILL_F = ("(() => { const G = window.__hm, C = G.combat, p = G.ctx.player; G.peace = true;"
                          " for (const e of G.rifts.alive()) for (let i = 0; i < 60 && e.state !== 'dead' && e.state !== 'gone'; i++) C.damageEnemy(e, 80, p); })()")
                T.ev("window.__hm.rifts.cur.t = 999; window.__hm.rifts.update(0.016)")
                still = T.ev("!!window.__hm.rifts.cur")
                T.ev("(() => { const G = window.__hm, c = G.ctx, p = c.player, R = G.rifts.cur; p.x = R.pos[0] - 1.4; p.z = R.pos[1] + 0.6; p.y = c.heightAt(p.x, p.z); c.stopWalk(); })()")
                T.frames(6); f.wait_for_timeout(400)
                w = T.ev("window.__hm.rifts.state()")["rift"]
                for _ in range(3):
                    if not T.ev("window.__hm.rifts.cur"): break
                    T.ev(KILL_F); T.frames(8); f.wait_for_timeout(500)
                F_ = T.ev("window.__hm.S.flags")
                T.step("Signe's turn-in opens the little rift behind the woodpile (tier I, tagged 'den', no rare, does not fizzle out); its wave of 2 wraiths + a skeleton sealed sets den_rift and pays Rift Marks",
                       rs["rift"] and rs["rift"]["tag"] == "den" and rs["rift"]["id"] == "minor" and abs(rs["rift"]["pos"][0] + 5.6) < 1.2 and still and w and w["wave"] == 1
                       and w["rare"] is None and not T.ev("window.__hm.rifts.cur") and F_.get("den_rift") == 1 and F_.get("den_riftOpen") == 1
                       and T.ev("window.__hm.S.merit.gate") > g0 and T.ev("window.__hm.markers.denkeeper ? window.__hm.markers.denkeeper.name : null") == "quest_turnin", rift=rs["rift"], wave=w)
                T.talk("denkeeper")
                T.ev("(() => { const S = window.__hm.S; delete S.inv.glowseed; delete S.inv.moonpetal; })()")   # QA: start stage 2 with nothing that hums
                p2, f2 = T.talk("denkeeper")
                T.ev("window.__hm.give('glowseed', 1)")
                mk = T.ev("window.__hm.markers.denkeeper ? window.__hm.markers.denkeeper.name : null")
                T.step("stage 2: without a glow seed / moonpetal Signe only reminds you; with a glow seed she shows a turn-in tag",
                       T.ev("window.__hm.S.quests.strays") == 2 and p2 == 1 and "hums" in f2 and mk == "quest_turnin", reminder=f2, mark=mk)
                # 'Can we make it dark now?' takes the seed, draws the shutters, and the hearth scene asks which stray
                T.talk("denkeeper", keep_open=True); dc = T.to_choice()
                f.keyboard.press("2"); f.wait_for_timeout(300)
                to_den()
                pc_ = T.to_choice()
                f.wait_for_timeout(300)
                shot_pick = T.shot("stage6_pet_pick")
                rep["shots"]["stage6_pet_pick"] = shot_pick
                T.step("'Can we make it dark now?' takes the glow seed, draws the shutters: the hearth scene (5 pages) ends on the pick: wisp kit / glow-moth / lantern-fox / not yet",
                       bool(dc) and "dark now" in dc["options"][1] and T.ev("window.__hm.S.flags.den_dark") == 1 and T.ev("window.__hm.S.flags.den_seed") == 1
                       and not T.ev("window.__hm.S.inv.glowseed") and bool(pc_) and len(pc_["options"]) == 4 and "wisp kit" in pc_["options"][0] and "glow-moth" in pc_["options"][1]
                       and "lantern-fox" in pc_["options"][2], dark=dc, pick=pc_)
                S0 = T.S(); h0 = S0["merit"].get("hearth", 0); gd0 = S0.get("gold", 0)
                f.keyboard.press("3"); f.wait_for_timeout(300)
                nc = T.to_choice()
                f.keyboard.press("1"); f.wait_for_timeout(300)
                T.read_all(); T.frames(8); f.wait_for_timeout(400)
                S = T.S(); nm = nc["options"][0] if nc else None
                T.step("pick the lantern-fox (key 3), name it from 4 seeded names + 'Just \"Lantern-fox\"' (key 1): S.pet / S.pets set, +25 gold, 3 Den biscuits, the Den unlocked, side quest done (+40 Hearth Tokens through the errand payout, no new merit key), quests n/3 unchanged",
                       bool(nc) and len(nc["options"]) == 5 and nc["options"][4] == 'Just "Lantern-fox".' and S["pet"] == {"id": "lanternfox", "name": nm, "bond": 1}
                       and S["pets"]["lanternfox"]["name"] == nm and S["quests"]["strays"] == 3 and S["flags"].get("den") == 1 and S["inv"].get("denbiscuit") == 3
                       and S.get("gold", 0) >= gd0 + 25 and S["merit"].get("hearth", 0) == h0 + 40 and T.ev("document.getElementById('btnLog').textContent") == den["count"]
                       and "Side: Strays of the Rift" in T.ev("document.getElementById('logList').innerText"), names=nc, pet=S["pet"], hearth=[h0, S["merit"].get("hearth")])
                # the pet follows on its own sheet; far behind it uses the follow gait
                ps = T.ev("window.__hm.pets.state()")
                p0 = T.pos(); T.walk(p0[0] + 5.5, p0[1] - 1.0, 60)
                T.ev("(() => { const G = window.__hm, a = G.pets.a, p = G.ctx.player; a.x = p.x - 5.0; a.z = p.z + 0.4; })()"); T.frames(3)
                far = T.ev("window.__hm.pets.state().actor")
                f.wait_for_timeout(2600); T.frames(6)
                near = T.ev("(() => { const a = window.__hm.pets.a, p = window.__hm.ctx.player; return Math.hypot(a.x - p.x, a.z - p.z); })()")
                T.step("the pet follows on its own pets sheet (role pet_fox); more than 3 m behind it switches to the follow gait, then catches up within ~2 m",
                       ps["actor"] and ps["role"] == "pet_fox" and ps["actor"]["sheet"] == "pets" and far["hurry"] and far["anim"] == "follow" and near < 2.2, actor=ps["actor"], far=far, near=round(near, 2))
                # glow: Bifrost is one of the Rift's dim places, so the fox's red tail-lantern is a light pool (light + pool + aura fx + embers), a light zone; aura mods apply
                T.ev("window.__hd2d.setTime('night')"); T.frames(10); f.wait_for_timeout(600)
                gl = T.ev("window.__hm.pets.state()")
                M = T.ev("(() => { const M = window.__hm.combat.M; return { riftWarn: M.riftWarn, riftMarkMul: M.riftMarkMul, stRegen: M.stRegen }; })()")
                zone = T.ev("window.__hm.glow.zones().filter((z) => z.src === 'pet').map((z) => z.r)")
                rep["shots"]["stage6_pet_glow"] = T.shot("stage6_pet_glow")
                T.step("pet glow at night / in the Rift's dim places: a red light (#ff4a3a-ish), its pool + aura effects, the ember particles, a 1.6 m light zone; Rift-sense mods in combat (riftWarn 10, +10% Rift Marks, stamina +8%)",
                       gl["lit"] and gl["light"] and gl["light"]["color"].startswith("#ff") and gl["fx"] == ["pet_pool_fox", "pet_aura_fox"] and gl["emitter"] and zone == [1.6]
                       and M["riftWarn"] == 10 and abs(M["riftMarkMul"] - 0.10) < 1e-9 and M["stRegen"] >= 0.08, glow=gl, mods=M)
                # Rift-sense: in Mossglen the fox's tail flares riftWarn seconds early, pointing where the tear will open
                T.ev("window.__hm.loadArea('mossglen', 'start')"); T.wait("window.__hm.area === 'mossglen' && window.__hm.pets.a", 120); T.idle(); f.wait_for_timeout(300)
                T.ev("window.__hm.peace = false; window.__hm.rifts.setTimer(10.5)")
                T.wait("window.__hm.rifts.warned", 30)
                wn = T.ev("({ warn: window.__hm.pets.state().warned, toast: document.getElementById('toast').innerText, next: window.__hm.rifts.nextPos, open: !!window.__hm.rifts.cur })")
                T.ev("window.__hm.rifts.setTimer(0.01)"); T.wait("!!window.__hm.rifts.cur", 30)
                op = T.ev("window.__hm.rifts.state().rift")
                T.ev("window.__hm.rifts.close(false, true); window.__hm.peace = true")
                T.step("lantern-fox Rift-sense: the tail flares red with a direction ~10 s before a random rift opens, and the rift opens where it pointed",
                       wn["warn"] and not wn["open"] and "tail flares red" in wn["toast"] and wn["warn"]["t"] <= 10.5 and op and wn["next"]
                       and math.hypot(op["pos"][0] - wn["next"][0], op["pos"][1] - wn["next"][1]) < 1.5, warn=wn, rift=op)
                # hero screen Gear tab: the pet slot; P feeds a Den biscuit (bond counts once a day, the glow doubles for 60 s)
                f.keyboard.press("i"); T.wait("window.__hm.heroUI", 20); f.wait_for_timeout(200)
                for _ in range(6):
                    if T.ev("document.querySelector('#heroTabs button.on') && document.querySelector('#heroTabs button.on').textContent.toLowerCase().includes('gear')"): break
                    f.keyboard.press("ArrowRight"); f.wait_for_timeout(150)
                slot = T.ev("(() => { const e = document.querySelector('#heroBody .pet'); return e ? e.innerText : ''; })()")
                b0 = T.ev("window.__hm.S.inv.denbiscuit || 0")
                f.keyboard.press("p"); f.wait_for_timeout(300)
                fd = T.ev("({ b: window.__hm.S.inv.denbiscuit || 0, own: window.__hm.S.pets.lanternfox, boost: window.__hm.pets.boostT, slot: document.querySelector('#heroBody .pet').innerText })")
                f.keyboard.press("Escape"); f.wait_for_timeout(200)
                T.step("hero screen Gear tab: the pet slot (name, species, aura, bond hearts, biscuits); P feeds a Den biscuit: fed day counted, glow boost for 60 s",
                       nm in slot and "lantern-fox" in slot and "Rift-sense" in slot and "♥♡♡" in slot and fd["b"] == b0 - 1 and fd["own"]["fed"] == 1
                       and fd["own"]["lastFed"] is not None and fd["boost"] > 50 and f"×{b0 - 1}" in fd["slot"], slot=slot[:160], fed=fd)
                # the Den hub: adoption needs Hearth Friend + 40 gold; swap pets
                T.ev("window.__hm.loadArea('bifrost', 'start')"); T.wait("window.__hm.area === 'bifrost' && window.__hm.pets.a", 120); T.idle(); f.wait_for_timeout(300)
                hr = T.ev("window.__hm.S.ranks.hearth || 0"); T.ev("window.__hm.S.ranks.hearth = 0")
                T.talk("denkeeper", keep_open=True); hub = T.to_choice()
                f.keyboard.press("3"); f.wait_for_timeout(300)
                lock = T.ev("window.__hm.dlg ? window.__hm.dlg.pages.join(' ') : ''"); T.read_all()
                T.ev(f"window.__hm.S.ranks.hearth = Math.max(1, {hr}); window.__hm.S.merit.hearth = Math.max(window.__hm.S.merit.hearth || 0, 150)")
                gd1 = T.ev("window.__hm.S.gold")
                T.talk("denkeeper", keep_open=True); T.to_choice(); f.keyboard.press("3"); f.wait_for_timeout(300)
                ac = T.to_choice(); f.keyboard.press("1"); f.wait_for_timeout(300)
                to_den(); an = T.to_choice(); f.keyboard.press("2"); f.wait_for_timeout(300); T.read_all(); T.frames(6)
                A = T.S(); Mw = T.ev("window.__hm.combat.M.spellCd")
                T.ev("window.__hm.pets.a && 1"); T.talk("denkeeper", keep_open=True); T.to_choice(); f.keyboard.press("1"); f.wait_for_timeout(300)
                sw = T.to_choice(); f.keyboard.press("1"); f.wait_for_timeout(300); T.read_all(); T.frames(6)
                B = T.S()
                T.step("the Den hub (swap / biscuits / adopt / auras / visiting): adopting needs Hearth Friend, then a 40-gold donation brings the wisp kit home (named, active, spellCd +0.06); 'Swap my pet' brings the fox back",
                       bool(hub) and len(hub["options"]) == 5 and "Swap" in hub["options"][0] and "Hearth" in lock and "Friend" in lock and bool(ac) and "wisp kit" in ac["options"][0]
                       and A["pet"]["id"] == "wispkit" and A["pets"]["wispkit"]["name"] == an["options"][1] and A["gold"] == gd1 - 40 and Mw >= 0.06
                       and bool(sw) and B["pet"]["id"] == "lanternfox" and B["pet"]["name"] == nm and T.ev("window.__hm.pets.state().role") == "pet_fox", hub=hub, adopt=ac, swap=sw)
                # save + reload: the pet comes back at your side
                T.ev("window.__hm.save(true)"); f.wait_for_timeout(300)
                f.reload(); T.wait("window.__hm && window.__hm.ready && window.__hd2d && window.__hd2d.ready && !window.__hd2dGate.loading", 120)
                f.click("#btnCont"); T.idle(); T.wait("!!window.__hm.pets.a", 60); T.frames(6)
                R = T.S(); ra = T.ev("(() => { const a = window.__hm.pets.a, p = window.__hm.ctx.player; return { d: Math.hypot(a.x - p.x, a.z - p.z), role: a.role || window.__hm.pets.state().role }; })()")
                T.step("save + reload + Continue: S.pet and S.pets round-trip (both pets, names, the fed day), and the active pet spawns beside the hero",
                       R["pet"] == B["pet"] and set(R["pets"]) == {"lanternfox", "wispkit"} and R["pets"]["lanternfox"]["fed"] == 1 and ra["d"] < 2.5, pet=R["pet"], at=ra)
                T.step("no JS errors (pets)", not errors and not T.ev("window.__hd2d.errors.length"), errors=errors[:5])
                pc.close()
                seg_done("F")
            except Exception as e:  # noqa: BLE001
                rep["pass"] = False
                rep["error"] = f"pets: {type(e).__name__}: {e}"[:400]
                try:
                    rep["shots"]["failure_F"] = T.shot("failure_F"); rep["state"] = T.S()
                except Exception:  # noqa: BLE001
                    pass
        # every shard checks its own pages for JS errors even when the counted 'no JS errors' steps live in another shard
        if rep["pass"] and errors:
            rep["pass"] = False; rep["error"] = f"JS errors: {errors[:3]}"
        b.close()
    srv.shutdown()
    rep["seconds"] = round(time.time() - T_START, 1)
    rep["steps"] = T.steps
    (out / "smoke.json").write_text(json.dumps(rep, indent=1))
    log(f"smoke: {'PASS' if rep['pass'] else 'FAIL'} {sum(s['pass'] for s in T.steps)}/{len(T.steps)} steps in {rep['seconds']} s" + (f"  ({rep.get('error')})" if not rep["pass"] else ""))
    return rep


def save_timing(seg_rep):
    """remember how long each passing segment took (only used to balance the shards)"""
    try:
        t = json.loads(TIMING.read_text())
    except Exception:  # noqa: BLE001
        t = {}
    for k, r in seg_rep.items():
        if r.get("pass") and r.get("seconds"):
            t[k] = r["seconds"]
    FIX.mkdir(exist_ok=True)
    tmp = FIX / f".timing.{time.time_ns()}.tmp"; tmp.write_text(json.dumps(t, indent=1, sort_keys=True)); tmp.replace(TIMING)


def run_jobs(n, out, simscale, segs=SEGS):
    """the sharded runner: n browser workers (one smoke.py process each, own server + Chromium) inside ONE job.
    Wrap the whole runner in the box's browser lock, not each worker."""
    import subprocess
    plan = [p for p in plan_shards(n, segs) if p]
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    print(f"smoke --jobs {n}: shards {plan} (segment seconds {seg_seconds()})", flush=True)
    procs = []
    for i, p in enumerate(plan):
        so = out / f"shard{i + 1}"
        lf = open(out / f"shard{i + 1}.log", "w")
        pr = subprocess.Popen([sys.executable, "-u", str(Path(__file__).resolve()), "--segments", p, "--out", str(so), "--simscale", str(simscale)],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

        def pump(pr=pr, lf=lf, tag=f"[s{i + 1}:{p}]"):
            for line in pr.stdout:
                lf.write(line); lf.flush(); print(tag, line, end="", flush=True)
        th = threading.Thread(target=pump, daemon=True); th.start()
        procs.append((p, so, pr, th, lf))
        time.sleep(4)   # stagger the Chromium launches a little
    reps = []
    for p, so, pr, th, lf in procs:
        rc = pr.wait(); th.join(); lf.close()
        try:
            r = json.loads((so / "smoke.json").read_text())
        except Exception as e:  # noqa: BLE001
            r = {"pass": False, "error": f"no smoke.json ({e})", "steps": [], "seconds": None}
        r["rc"] = rc; r["shard"] = p; reps.append(r)
    order = {k: i for i, k in enumerate(SEGS)}
    steps = sorted((s for r in reps for s in r.get("steps", [])), key=lambda s: order.get(s.get("seg", ""), 99))
    ok = all(r.get("pass") and r["rc"] == 0 for r in reps)
    segrep = {k: v for r in reps for k, v in (r.get("segments") or {}).items()}
    wall = round(time.time() - t0, 1)
    merged = {"pass": ok, "mode": f"jobs={n}", "shards": [{"segs": r["shard"], "pass": r.get("pass"), "seconds": r.get("seconds"), "steps": len(r.get("steps", [])),
              "error": r.get("error")} for r in reps], "segments": segrep, "seconds": wall, "steps": steps}
    (out / "smoke.json").write_text(json.dumps(merged, indent=1))
    for r in reps:
        print(f"  shard {r['shard']}: {'PASS' if r.get('pass') else 'FAIL'} {sum(s['pass'] for s in r.get('steps', []))}/{len(r.get('steps', []))} in {r.get('seconds')} s"
              + (f"  ({r.get('error')})" if not r.get("pass") else ""), flush=True)
    print(f"smoke: {'PASS' if ok else 'FAIL'} {sum(s['pass'] for s in steps)}/{len(steps)} steps in {wall} s (sharded, {len(plan)} workers, segments {''.join(sorted(segs))})", flush=True)
    return merged


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Hearthmoor smoke test. Serial by default (all segments, one browser).")
    ap.add_argument("--out", default=str(GAME / "tests" / "shots"))
    ap.add_argument("--simscale", type=int, default=4)
    ap.add_argument("--segments", default=SEGS, help="run only these segments (e.g. CF); later segments start from the saved checkpoints")
    ap.add_argument("--quick", default=None, help="per-change subset: the segments covering an area, e.g. --quick pet / bifrost / combat (comma list ok)")
    ap.add_argument("--shard", default=None, help="i/N: run shard i of N (same split as --jobs N)")
    ap.add_argument("--jobs", type=int, default=0, help="run all segments as N parallel browser workers in this one process")
    ap.add_argument("--list", action="store_true", help="list the segments, quick areas and the shard plan")
    a = ap.parse_args()
    segs = a.segments.upper()
    if a.quick:
        segs = "".join(sorted({c for q in a.quick.split(",") for c in QUICK[q.strip().lower()]}))
    if a.list:
        for k in SEGS:
            print(f"{k} ({seg_seconds()[k]:.0f} s): {SEG_INFO[k]}")
        print("quick:", ", ".join(f"{q}={v}" for q, v in QUICK.items()))
        for n in (2, 3, 4):
            print(f"--jobs {n}: {plan_shards(n)}")
        sys.exit(0)
    if a.jobs and a.jobs > 1:
        r = run_jobs(a.jobs, Path(a.out), a.simscale, segs)
        if r["pass"]:
            save_timing(r["segments"])
        sys.exit(0 if r["pass"] else 1)
    if a.shard:
        i, n = (int(x) for x in a.shard.split("/"))
        segs = plan_shards(n, segs)[i - 1]
    r = run(Path(a.out), a.simscale, segs=segs)
    if r["pass"] and not a.shard:
        save_timing(r["segments"])
    sys.exit(0 if r["pass"] else 1)
