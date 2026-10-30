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
import os
import functools
import json
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
STUB = (Path(__file__).resolve().parent / "gamepad_stub.js").read_text()
def _commit():
    """the commit under test, for the smoke log header (merge checks compare it with the branch tip); '+dirty' = uncommitted game edits"""
    import subprocess
    try:
        h = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=GAME, capture_output=True, text=True).stdout.strip()
        d = subprocess.run(["git", "status", "--porcelain", "--", "."], cwd=GAME, capture_output=True, text=True).stdout.strip()
        return h + ("+dirty" if d else "")
    except Exception:  # noqa: BLE001
        return "unknown"


COMMIT = _commit()


def header(what):
    return f"# smoke header: commit {COMMIT}  {what}  started {time.strftime('%Y-%m-%d %H:%M:%S %Z')}"


def preflight(argv):
    """tests/preflight.sh first (syntax + a quick startup load); --no-preflight skips it. Exits 2 on a preflight failure."""
    import subprocess
    if "--no-preflight" in argv or os.environ.get("HM_PREFLIGHT_DONE"):
        return
    rc = subprocess.call(["bash", str(Path(__file__).resolve().parent / "preflight.sh")], env={**os.environ, "HM_IN_BROWSER_LOCK": "1"})   # smokes run under the browser lock already
    if rc:
        print(f"preflight FAILED (rc {rc}): fix it before the smoke (or --no-preflight)", flush=True); sys.exit(2)
    os.environ["HM_PREFLIGHT_DONE"] = "1"   # shard workers / child smokes skip it


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

    RETRY = True   # one immediate retry of a failing step (same check, same values); --no-retry turns it off
    retries = 0

    def _check(self, ok):
        """ok is a bool, a JS expression string (T.check) or a callable: strings / callables can be re-evaluated for the retry"""
        if callable(ok):
            return ok()
        return ok

    def step(self, name, ok, **info):
        """a failing step retries ONCE right away with the same check when the check can be re-run (a callable or T.check's JS);
        it passes only if the retry passes. A plain bool cannot be re-measured, so it is logged as [RETRY] n/a and fails as before."""
        r1 = bool(self._check(ok))
        res = r1
        if not r1 and Smoke.RETRY:
            Smoke.retries += 1
            if callable(ok):
                res = bool(self._check(ok))
                self.log(f"  [RETRY] {name}: first={r1} retry={res}")
            else:
                self.log(f"  [RETRY] {name}: first={r1} retry=n/a (value-only check, cannot re-measure)")
        self.steps.append({"step": name, "pass": res, "seg": getattr(self, "seg", ""), **({"retried": True, "first": r1} if res != r1 or (not r1 and Smoke.RETRY) else {}), **info})
        self.log(f"  [{'PASS' if res else 'FAIL'}] {name} {json.dumps(info)[:200] if info else ''}  @{time.time() - self.t0:.0f}s")
        if not res:
            raise AssertionError(name)

    def check(self, name, js, **info):
        """step on a JS boolean expression; on a fail the same expression is evaluated again once (see step)"""
        return self.step(name, lambda: self.ev(js), **info)

    def frames(self, n=6, timeout=30):
        """wait until the engine has drawn n more frames (fixed sleeps alone race slow frames on a loaded box)"""
        f0 = self.ev("window.__hd2d.frames || 0")
        self.wait(f"(window.__hd2d.frames || 0) >= {f0 + n}", timeout)

    def S(self):
        return self.ev("JSON.parse(JSON.stringify(window.__hm.S))")

    def wait(self, js, timeout=90):
        try:
            self.pg.wait_for_function(js, timeout=timeout * 1000)
        except Exception:
            self.dump_timeout(js)
            raise

    def dump_timeout(self, js):
        """on a wait timeout: log the predicate's parts, page state, recent JS errors and a screenshot (diagnosis only; the wait still fails)"""
        try:
            st = self.pg.evaluate("""() => { const G = window.__hm, H = window.__hd2d; return { href: location.href, hm: !!G, area: G && G.area, busy: G && G.busy,
              ready: G && G.ready, title: G && !!G.title, hd2d: !!H, h_ready: H && H.ready, frames: H && H.frames, gate: window.__hd2dGate && window.__hd2dGate.loading,
              errs: H && H.errors ? H.errors.slice(-5).map(String) : null, boot: (document.getElementById('boot') || {}).textContent }; }""")
        except Exception as e:  # noqa: BLE001
            st = f"state unavailable: {e}"
        self.log(f"  [TIMEOUT] waiting for {js[:160]} -> {json.dumps(st, default=str)[:900]}")
        try:
            self.shot(f"timeout_{time.strftime('%H%M%S')}")
        except Exception:  # noqa: BLE001
            pass

    def until(self, js, timeout=150):
        """wait for a condition that depends on GAME time (storm / rift / gust / vent timers, pad polls): the game clock runs slow on a
        busy box (dt is clamped per frame), so a fixed pause flakes. Returns True / False and never raises: the step that follows reports the state."""
        try:
            self.pg.wait_for_function(js, timeout=timeout * 1000)
            return True
        except Exception:
            return False

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
        for ti, off in enumerate(((0, 1.0), (1.0, 0), (-1.0, 0), (0, -1.0), (0.7, 0.7), (-0.7, 0.7), (0, 1.0), (1.0, 0), (-1.0, 0), (0, -1.0))):
            if ti == 6:   # every spot failed (a slow box, or a storm rift's foe in the way): let things settle, then try the spots once more
                self.pg.wait_for_timeout(2500); self.idle(); self.until("!window.__hm.dlg && !window.__hm.busy", 20)
                # the player can be wedged inside a collider by an earlier teleport (a storm rift seal puts you 1.4 m off the rift): stand beside the NPC
                self.ev(f"(() => {{ const c = window.__hm.ctx, a = c.npc('{npc_id}'), p = c.player; if (a) {{ p.x = a.x; p.z = a.z + 1.3; p.y = c.heightAt(p.x, p.z); c.stopWalk(); }} }})()")
            a = self.ev(f"(() => {{ const a = window.__hm.ctx.npc('{npc_id}'); return a ? [a.x, a.z] : null; }})()")
            if not a:
                raise AssertionError(f"no npc {npc_id} in {self.ev('window.__hm.area')}")
            self.walk(a[0] + off[0], a[1] + off[1])
            self.pg.keyboard.press("e")
            self.until("!!window.__hm.dlg", 2)   # was a fixed 250 ms: the E press has opened a dialogue (or 2 s: it did not, try the next spot)
            who = self.ev("window.__hm.dlg ? window.__hm.dlg.npc.id : null")
            self.tries = getattr(self, "tries", [])[-5:] + [{"who": who, "near": self.ev(f"(() => {{ const c = window.__hm.ctx, n = c.nearestNpc(), a = c.npc('{npc_id}'); return {{ n: n && n.id, vis: a && a.quad && a.quad.visible, noTalk: a && !!a.noTalk, talkable: a && !!a.talkable, say: a && !!a.say, prompt: (document.getElementById('prompt') || {{}}).textContent }}; }})()")}]
            if who == npc_id:
                break
            while self.ev("!!window.__hm.dlg"):
                self.pg.keyboard.press("Escape"); self.until("!window.__hm.dlg", 2)
        else:
            st = self.ev(f"(() => {{ const G = window.__hm, c = G.ctx, p = c.player, a = c.npc('{npc_id}'); return {{ p: [p.x, p.z, p.y].map((v) => +v.toFixed(2)), a: a && [a.x, a.z, a.y], busy: !!G.busy, walking: c.walking(), prompt: (document.getElementById('prompt') || {{}}).textContent }}; }})()")
            raise AssertionError(f"could not talk to {npc_id}: {st} tries={getattr(self, 'tries', [])}")
        pages = self.ev("window.__hm.dlg.pages.length")
        first = self.ev("window.__hm.dlg.pages[0]")
        if keep_open:
            return pages, first
        self.read_all()
        return pages, first

    def to_choice(self, n=80):
        """read a dialogue up to its choice page without ever pressing E on it (E there would pick an answer)"""
        for _ in range(n):
            st = self.ev("(() => { const d = window.__hm.dlg; return d ? [d.picking, d.full, d.i === d.pages.length - 1, d.i] : null; })()")
            if not st:
                return None
            if st[0]:
                return self.ev("window.__hm.dlgChoice()")
            if st[2]:
                self.until("!window.__hm.dlg || window.__hm.dlg.picking", 3); continue   # the last page types itself out, then the answers appear
            self.pg.keyboard.press("e"); self.until(self.DLG_MOVED % (st[3], "true" if st[1] else "false"), 3)
        return None

    # the E press was seen: the dialogue closed, turned a page, or finished typing (replaces fixed 140-250 ms pauses)
    DLG_MOVED = "(() => { const d = window.__hm.dlg; return !d || d.i !== %s || !!d.full !== %s || !!d.picking; })()"

    def read_all(self):
        n = 0
        while n < 40:
            st = self.ev("(() => { const d = window.__hm.dlg; return d ? [d.i, d.full] : null; })()")
            if not st:
                break
            self.pg.keyboard.press("e"); self.until(self.DLG_MOVED % (st[0], "true" if st[1] else "false"), 3); n += 1

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
        cx, cz = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
        p0 = self.ev("[window.__hm.ctx.player.x, window.__hm.ctx.player.z].map((v) => +v.toFixed(2))")
        ok = self.ev(f"window.__hm.ctx.walkTo({cx}, {cz})")
        try:
            self.wait(f"window.__hm.area !== '{area0}' || window.__hm.busy", timeout)
        except Exception as e:  # noqa: BLE001
            st = self.ev("(() => { const c = window.__hm.ctx, p = c.player; return { p: [p.x, p.z, p.y].map((v) => +v.toFixed(2)), walking: c.walking(), busy: !!window.__hm.busy, dlg: !!window.__hm.dlg, prompt: (document.getElementById('prompt') || {}).textContent }; })()")
            raise AssertionError(f"go_rect {kind}[{idx}] rect={r} centre=({cx:.2f},{cz:.2f}) from={p0} walkTo={ok} now={st}") from e
        self.idle(timeout)
        self.pg.wait_for_timeout(400)
        return self.ev("window.__hm.area")


# ---------------------------------------------------------------------------------------------- segments / shards
# The playthrough is cut into segments at real save points. A sharded run starts a segment from the checkpoint the
# segment before it saved (localStorage only: the same thing the serial run's reload + Continue restores from).
# Every step still runs exactly once across the shards, with the same assertions and thresholds.
FIX = Path(__file__).resolve().parent / "fixtures"
SEGS = "ABCDEFGHIJKLMNOPQRSTU"
SEG_INFO = {
    "A": "title, loading gate, Lantern Eve, errands, controller, Mossglen, leveling, combat, loot, rares + rifts, Hollows, garden (ends: K save in Mossglen -> cp1)",
    "B": "reload #1 + Continue, save slots, Pudding home, shop, bank, riddle, night merchant, factions, glow cap, weather, sockets, errand 2 (ends: K save in the Lane -> cp2)",
    "C": "reload #2, Rift Shrine + Vanaheim, Ravenhold Harbor, Bifrost Crossing (ends: -> cp3)",
    "D": "phone portrait + landscape on touch (continues the cp3 save)",
    "E": "v1 save migration",
    "F": "Stage 6+: the Stray Den + glowing pets (continues the cp3 save)",
    "G": "Stage 6.3: the Old Temple (Hilde's writ, the Harbor gate, clues, Alder's charm, Ida's wick, braziers, the rite, the rift, Veyra, Midgard's arch; continues cp3)",
    "H": "Stage 6.5: rift storms (calendar, storm rifts + Rift Marks +25%, sky cracks, Storm Watch bounty, NPC / ferry storm lines, dawn, toasts; continues cp3)",
    "J": "Stage 6.4: the Violet Spring, the Rotwood Hollow (8 rooms, root-door brazier order, the Blight Regent 5.5x: phases + frost-iron spike weak point), the Verdant Heart (6 rooms, Thornmother 2.4x, Hjortur 6x trial / corrupted) (continues cp3)",
    "K": "Stage 6.6: glow-fish orb lanterns (buy, night catch, place at home + garden, night pools + light zones, day off, take back; continues cp3)",
    "L": "Stage 6.7: the Forge Quarter (gate after the Cold Altar, red forges + blue quench glow, Tova +1..+10 temper with caps / fail heat, Orri rune rerolls; continues cp3)",
    "M": "Stage 6.8: the Glowfrog Still + Cold Cauldron (Bryony quest, vent light, recipes, fizzle hint, yields, secret broth, timed brew mods, drink from the bag, Bloop's dew, 3/day caps, spring vial, garden herbs; continues cp3)",
    "N": "Alfheim realm (tests/smoke_alfheim.py, own context)",
    "O": "Svartalfheim realm (tests/smoke_svartalfheim.py, own context)",
    "P": "Jotunheim realm (tests/smoke_jotunheim.py, own context)",
    "Q": "Muspelheim realm (tests/smoke_muspelheim.py, own context)",
    "R": "Niflheim realm (tests/smoke_niflheim.py, own context)",
    "S": "Vanaheim realm incl. Stage B (tests/smoke_vanaheim.py, own context)",
    "T": "Asgard realm (tests/smoke_asgard.py, own context)",
    "U": "Helheim realm (tests/smoke_helheim.py, own context)",
    "I": "Stage 6.4 groundwork: Glenheart rename, trial-mode yield, 5-6x boss camera pull, Vanaheim conquer merit -> Rift Marks, heartwood sale to Sable (continues cp3)",
}
# --quick <area>: the segments that cover an area / feature (a per-change check; the batch still runs everything)
QUICK = {
    "title": "A", "intro": "A", "plaza": "A", "lane": "A", "controller": "A", "mossglen": "A", "combat": "A", "loot": "A",
    "rares": "A", "rifts": "A", "hollows": "A", "garden": "A", "leveling": "A",
    "slots": "B", "shop": "B", "bank": "B", "riddle": "B", "merchant": "B", "factions": "B", "weather": "B", "glow": "B", "gear": "B",
    "rift": "C", "vanaheim": "C", "ravenhold": "C", "bifrost": "C",
    "phone": "D", "touch": "D", "audio": "D", "music": "D", "options": "D", "migration": "E", "save": "BE",
    "pet": "F", "pets": "F", "stray": "F",
    "temple": "G", "oldtemple": "G", "midgard": "G",
    "vanaheim4": "I", "verdant": "J", "rotwood": "J", "regent": "J", "hjortur": "J", "vhspring": "J", "trial": "I", "glenheart": "I", "heartwood": "I",
    "still": "M", "alchemy": "M", "brew": "M", "nettle": "M",
    "forge": "L", "temper": "L", "reroll": "L",
    "lantern": "K", "lanterns": "K", "orb": "K", "glowfish": "K",
    "alfheim": "N", "svartalfheim": "O", "jotunheim": "P", "muspelheim": "Q", "niflheim": "R", "vanaheim5": "S", "vhrealm": "S", "asgard": "T", "helheim": "U",
    "storm": "H", "storms": "H", "riftstorm": "H", "bounty": "H",
}
TIMING = FIX / "smoke_timing.json"   # seconds per segment from the last passing runs (shard balancing only)
DEFAULT_SECONDS = {"A": 560, "B": 260, "C": 230, "D": 5640, "E": 25, "F": 150, "G": 200, "H": 170, "I": 90, "J": 120, "K": 60, "L": 60, "M": 60, "N": 40, "O": 275, "P": 320, "Q": 145, "R": 330, "S": 140, "T": 175, "U": 360}   # realm segments N-U measured 2026-10-30 (NOPQ 775 s, RSTU 1001 s)


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
    rep = {"url": url, "shots": {}, "segments_run": segs, "segments": seg_rep, "commit": COMMIT}
    log(header(f"segments {segs}"))
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
                pg.keyboard.press("m"); T.until("window.__hm.picker.state().mode === 'hero'", 5)
                m1, tip = T.ev("window.__hm.picker.state().mode"), T.ev("document.getElementById('pickModeTip').textContent")
                pg.keyboard.press("m"); pg.keyboard.press("m"); T.until("window.__hm.picker.state().mode === 'adventurer'", 5)
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
                pg.click("#dlgChoices .choice[data-i='2']"); T.until("!window.__hm.dlg || !window.__hm.dlg.picking", 5)
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
                T.until("!document.getElementById('log').hidden && !document.getElementById('dlg').hidden", 5)
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
                T.ev("__padPlug(true)"); T.until("document.getElementById('toast').textContent.includes('controller connected') && !document.getElementById('toast').hidden", 10)
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
                # slow frames under load: wait (same assertion, no looser) until the engine has seen Y up and closed the wheel
                T.wait("!window.__hm.wheel.state().open", 20)
                if n_cyc >= 2: T.wait("window.__hm.ctx.spellIndex() === 1", 20)
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
                # the zoom runs on game frames (slow on a busy box): hold the stick until the distance has moved, then let go
                rs(-1); T.until(f"window.__hd2d.camState().dist < {z0 - 0.5}", 60); rs(0); pg.wait_for_timeout(200); z1 = T.ev("window.__hd2d.camState().dist")
                rs(1); T.until(f"window.__hd2d.camState().dist > {z1 + 0.5}", 60); rs(0); pg.wait_for_timeout(200); z2 = T.ev("window.__hd2d.camState().dist")
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
                T.ev("__padPlug(false)"); pg.wait_for_timeout(300)
                # the unplug is seen by the per-frame poll: under load (parallel shards) 600 ms can be too few frames
                try: T.wait("document.getElementById('toast').textContent.includes('disconnected') && !document.body.classList.contains('ctrl')", 5)
                except Exception: pass   # the step below reports what is on screen
                T.step("controller unplugged: toast, controller mode off", "disconnected" in T.ev("document.getElementById('toast').textContent")
                       and not T.ev("document.body.classList.contains('ctrl')"), toast=T.ev("document.getElementById('toast').textContent"),
                       ctrl=T.ev("document.body.classList.contains('ctrl')"), pads=T.ev("navigator.getGamepads().filter(Boolean).length"))
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
                T.ev("window.__hd2d.setTime(0.95)"); T.until("window.__hm.glow.toads.length === 6", 10)
                toads = T.ev("window.__hm.glow.toads.length")
                T.ev("(() => { const c = window.__hm.ctx, p = c.player, t = window.__hm.glow.toads[0]; p.x = t.x + 0.6; p.z = t.z + 0.3; p.y = c.heightAt(p.x, p.z); c.stopWalk(); })()")
                pg.wait_for_timeout(400)
                lit = T.ev("window.__hm.glow.lit && !document.getElementById('litTag').hidden")
                shy = T.ev("(() => { const g = window.__hm.glow, t = g.toads[0]; return g.litAt(t.x, t.z) && !g.litAt(t.x + 3, t.z + 3); })()")
                T.step("night: toadstools glow, standing by one makes you glowlit (light zones)", toads == 6 and lit and shy, toads=toads, lit=lit)
                T.ev("window.__hd2d.setTime(0.5)"); T.until("window.__hm.glow.toads.length === 0", 10)   # midday (t_keep itself may already be night)
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
                T.step("Mossglen also has a frost golem, a skeleton mage and Glenheart (mini-boss)", {"icegolem", "skelmage", "eldergolem"} <= set(roles3), roles=roles3)
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
                T.step("Glenheart (renamed from Mossheart): carries a rune light, a named boss bar shows when it fights", boss["light"] and boss["bar"] and "Glenheart" in boss["label"] and boss["w"] not in ("", "100%"), boss=boss)
                big = T.ev("(() => { const R = window.__hd2d.actorRects(), m = R.find((r) => r.id === 'mossheart'), p = R.find((r) => r.id === 'player'), C = window.__hm.combat, e = C.enemies.find((x) => x.id === 'mossheart');"
                           " return { sheet: m && m.sheet, mh: m && m.h / m.k, ph: p && p.h / p.k, r: e.a.r, scale: e.D.scale, pull: window.__hm.ctx.pull() }; })()")
                T.step("Glenheart is ~2.5x the hero, drawn natively on its own boss sheet; hitbox and camera framing scale with it",
                       big["sheet"] == "boss" and big["mh"] == 80 and big["ph"] == 32 and big["scale"] == 2.5 and big["r"] >= 0.7 and big["pull"] > 1.01, **big)
                T.ev("(() => { const C = window.__hm.combat, e = C.enemies.find((x) => x.id === 'mossheart'); window.__hm.peace = true; C.damageEnemy(e, 9999, window.__hm.ctx.player); })()")
                pg.wait_for_timeout(900)
                legs = [d for d in T.ev("window.__hm.loot.qa()") if d["rar"] == 4]
                T.step("Glenheart always drops a Legendary (and the boss bar goes away)", len(legs) >= 1 and T.ev("!document.getElementById('bossbar') || document.getElementById('bossbar').hidden"), drops=legs)
                cores = [d for d in T.ev("window.__hm.loot.qa()") if d.get("gem") == "golem_core"]
                T.step("Glenheart also drops a golem core (socket gem)", len(cores) >= 1, drops=cores)
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
                dfn = "(() => { const a = window.__hm.ctx.player.act; return !!(a && a.name === 'defend'); })()"
                pg.keyboard.down("c"); T.until(dfn)   # game-time: the guard pose starts on a game frame (slow on a busy box)
                guarded = T.ev(hurt)
                pg.keyboard.up("c"); T.until("!" + dfn)
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
                y0 = T.ev("window.__hm.ctx.player.y"); pg.keyboard.press("z"); T.until("window.__hm.ctx.player.lift > 0.8", 20)   # the spring is a game-time animation: sample it when it is in the air
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
                T.step("talking to Odo opens the shop panel (tonic, glow seed, empty orb, glow-fish, 3 pieces of gear)", T.ev("!!window.__hm.shop && !document.getElementById('shopui').hidden") and len(shop0["rows"]) == 7
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
                T.wait("!!(window.__hm.ctx.npc('nightmerchant') && window.__hm.shopUI.nm && window.__hm.shopUI.nm.light)", 15)   # she arrives on shopUI.update; slow under 2 shards, so wait for it
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
                pg.mouse.click(cv[0], cv[1]); T.until("window.__hm.ctx.walking()", 5)
                walking = T.ev("window.__hm.ctx.walking()")
                T.wait("!window.__hm.ctx.walking()", 60); p1 = T.pos()
                T.walk(7.6, 5.4); pe = T.pos(); edge = round(((pe[0]) ** 2 + (pe[1] + 1.0) ** 2) ** 0.5, 2)
                T.step("mouse: clicking the floating isle's paving walks there (the isle top is walkable); walking at the void stops at the round edge",
                       walking and abs(p1[0]) + abs(p1[1] - 3.0) > 0.8 and 6.0 < edge < 7.55, p1=p1, edge=edge)
                T.ev("(() => { const c = window.__hm.ctx, p = c.player; p.x = -3.4; p.z = -4.9; p.y = c.heightAt(-3.4, -4.9); c.stopWalk(); })()"); pg.wait_for_timeout(400)
                pr = T.ev("document.getElementById('prompt').textContent")
                T.btn(0); T.until("!!window.__hm.dlg", 5)
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
                pg.keyboard.press("1"); T.until("!window.__hm.dlg || !window.__hm.dlg.picking", 5)
                reply = T.ev("window.__hm.dlg ? window.__hm.dlg.pages[0] : ''"); T.read_all()
                T.step("the spring-warden asks what you are to Vanaheim (befriend / conquer / not now); key 1 befriends: the alliance flag is set",
                       bool(ch) and len(ch["options"]) == 3 and "friend" in ch["options"][0].lower() and "bow" in ch["options"][1].lower()
                       and T.ev("window.__hm.S.flags.alliance.vanaheim") == "befriend" and "welcome in Mossbrook" in reply, choice=ch, reply=reply[:60])
                pages, first = T.talk("warden")
                T.step("afterwards the warden greets a friend of Mossbrook (no second ask) and, since 6.4, offers The Violet Spring", "Friend of Mossbrook" in first and pages == 2
                       and T.ev("window.__hm.S.quests.vh_spring") == 1 and not T.ev("!!(window.__hm.dlg && window.__hm.dlg.choice)"), line=first[:60])
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
                pg.keyboard.press("e"); T.until("!!window.__hm.dlg", 5)
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
                pg.keyboard.press("Escape"); T.until("!window.__hm.shop", 5)
                T.step("Ida Wickmere the chandler opens Wickmere's Chandlery (tonics, glow seeds, a rift shard, harbor kit); Esc closes it", sh[0] is True and sh[1] == "harbor" and not T.ev("window.__hm.shop"), shop=sh)
                # the hidden bubbly spring in the west corner, behind the crates: heals + spring-fizz, a first find is a secret (Gnome Council merit)
                n0 = T.ev("window.__hm.S.merit.gnome")
                T.walk(-16.4, -7.4); T.until("window.__hm.hollows.buffOn() && window.__hm.S.found.rh_spring === 1", 10)
                T.step("the hidden spring behind the crates fizzes (spring-fizz buff); a first find is a secret: +40 Gnome Council merit",
                       T.ev("window.__hm.hollows.buffOn()") and T.ev("window.__hm.S.found.rh_spring") == 1 and T.ev("window.__hm.S.merit.gnome") - n0 == 40, merit=[n0, T.ev("window.__hm.S.merit.gnome")])
                # mouse: click the waystone (walks up), click again (its travel choice), key 1 travels to Bakery Lane
                T.walk(13.0, -1.6)
                def click_world(x, z):
                    s_ = T.ev(f"(() => {{ const c = window.__hd2d.ctx; return c.project({x}, c.heightAt({x}, {z}), {z}); }})()")
                    pg.mouse.click(s_["x"], s_["y"]); pg.wait_for_timeout(300)
                click_world(15.0, -3.6); T.wait("!window.__hm.ctx.walking()", 60); T.until("window.__hm.harbor.near()", 5)
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
                pg.keyboard.press("e"); T.until("!!window.__hm.dlg", 5)
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
                pg.keyboard.press("e"); T.until("!!window.__hm.dlg", 5)
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
                T.wait("window.__hm.dlgChoice && window.__hm.dlgChoice()", 90)   # (was + a fixed 300 ms: the choice is already up)
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
                pg.keyboard.press("e"); T.until("!!window.__hm.dlg", 5)
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
                    # the action starts on a game frame (slow, capped game time on a busy box): wait for it instead of sampling at a fixed 60 / 120 ms
                    T.until(f"window.__hd2d.actorState().act === '{want}'", 20)
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
                T.ev("__padPlug(true)"); T.ev("__padAxes(0, 1)"); q.wait_for_timeout(800)
                T.until("getComputedStyle(document.getElementById('pad')).display === 'none'", 30)   # the next poll hides it; slow frames on a busy box need longer than a fixed pause
                T.ev("__padAxes(0, 0)"); q.wait_for_timeout(300)
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
                tap_el("#btnOpts"); T.until("!!window.__hm.opts"); tap_el("#btnWeather"); T.until("window.__hm.weather.mode === 'off'")   # game-time: the touch lands on a game frame (slow on a busy box)
                pm.append(T.ev("[window.__hm.weather.mode, window.__hm.weather.qa().emitters.length]"))
                tap_el("#btnWeather"); T.until("window.__hm.weather.mode === 'on'"); tap_el("#btnWeather"); T.until("window.__hm.weather.mode === 'light'")
                pm.append(T.ev("window.__hm.weather.mode")); tap_el("#optsClose")
                T.step("phone: weather defaults to light; the Options button cycles light -> off -> on -> light by touch", pm == ["light", ["off", 0], "light"] and not T.ev("window.__hm.opts"), modes=pm)
                # music (2026-10-19): the Plaza plays the Midgard theme (decoded ogg, looped by buffer length), ambient ducked ~70%; music toggle + volume slider by touch, saved
                T.until("window.__hm.audio.musicState().track === 'midgard'", 60)
                m0 = T.ev("window.__hm.audio.musicState()")
                lp = T.ev("(() => { const c = window.__hm.audio.cur; return c && c.src ? [c.src.loop, c.src.loopStart, Math.abs(c.src.loopEnd - c.src.buffer.duration) < 1e-6, c.src.buffer.numberOfChannels] : null; })()")
                tap_el("#btnOpts"); T.until("!!window.__hm.opts"); tap_el("#btnMusic"); T.until("window.__hm.audio.musicMuted === true", 20)
                m1 = T.ev("[window.__hm.audio.musicState(), localStorage.getItem('hearthmoor-music-mute'), document.getElementById('btnMusic').textContent]")
                tap_el("#btnMusic"); T.until("window.__hm.audio.musicState().track === 'midgard'", 30)
                T.ev("(() => { const r = document.getElementById('musicVol'); r.value = 35; r.dispatchEvent(new Event('input', { bubbles: true })); })()")
                m2 = T.ev("[window.__hm.audio.musicVol, localStorage.getItem('hearthmoor-music-vol'), document.getElementById('musicVolN').textContent, localStorage.getItem('hearthmoor-music-mute')]")
                T.ev("(() => { const r = document.getElementById('musicVol'); r.value = 60; r.dispatchEvent(new Event('input', { bubbles: true })); })()")
                T.ev("window.__hm.audio.setBattle(true, false, 0.016)"); T.until("window.__hm.audio.musicState().track === 'battle'", 30)
                T.ev("window.__hm.audio.setBattle(true, true, 0.016)"); T.until("window.__hm.audio.musicState().track === 'boss'", 30)
                mb = T.ev("window.__hm.audio.musicState().track")
                T.ev("window.__hm.audio.setBattle(false, false, 9)"); T.until("window.__hm.audio.musicState().track === 'midgard'", 30)
                mr = T.ev("[window.__hm.audio.musicState(), window.__hm.audio.muted]"); tap_el("#optsClose")
                T.step("music: Midgard theme loops by buffer length (mono), ambient ducked not muted; music toggle + volume slider save; battle -> boss -> back to the realm theme",
                       m0["track"] == "midgard" and m0["ducked"] and not m0["failed"] and lp == [True, 0, True, 1]
                       and m1[0]["muted"] and m1[0]["track"] is None and not m1[0]["ducked"] and m1[1] == "1" and m1[2] == "music: off"
                       and m2 == [0.35, "0.35", "35%", "0"] and mb == "boss" and mr[0]["track"] == "midgard" and mr[0]["vol"] == 0.6 and mr[0]["ducked"] and not mr[1],
                       m0=m0, loop=lp, muted=m1, vol=m2, boss=mb, back=mr)
                # music, other realms (static, 2026-10-21): only the Plaza plays live above; every other realm's area -> track map in audio.js and its music_<track>.ogg are checked on disk
                import re as _re
                _aj = (Path(__file__).resolve().parent.parent / "game" / "audio.js").read_text()
                _map = {a: t for grp, t in _re.findall(r"for \(const a of \[([^\]]*)\]\) REALM_OF\[a\] = '(\w+)'", _aj) for a in _re.findall(r"'(\w+)'", grp)}
                _tr = _re.findall(r"'(\w+)'", _re.search(r"MUSIC_TRACKS = \[([^\]]*)\]", _aj).group(1))
                _md = Path(__file__).resolve().parent.parent / "audio" / "music"
                _miss = [t for t in _tr if not (_md / f"music_{t}.ogg").is_file()]
                _realms = {"alfheim", "svartalfheim", "jotunheim", "muspelheim", "niflheim", "asgard"}
                _bad = [a for a, t in _map.items() if t not in _tr]
                # the one allowed shared theme (2026-10-28): Mossbrook covers the Vanaheim, Rotwood and Verdant areas, and only those
                _shared = {"mossbrook": {"vanaheim", "vh_village", "vh_garden", "rotwood", "verdant"}}
                _shr = {t: {a for a, x in _map.items() if x == t} for t in _shared}
                _shok = all(_shr[t] == _shared[t] for t in _shared) and not (_realms & set().union(*_shared.values()))
                T.step("music (static): every non-Midgard realm hub maps to its own theme (Mossbrook shared by Vanaheim/Rotwood/Verdant only), every mapped track is in MUSIC_TRACKS, every music_<track>.ogg exists",
                       all(_map.get(r) == r for r in _realms) and _map.get("plaza") == "midgard" and set(_map.values()) | {"battle", "boss"} == set(_tr) and not _bad and not _miss and _shok,
                       areas=len(_map), tracks=_tr, missing=_miss, bad=_bad, shared={t: sorted(v) for t, v in _shr.items()})
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
        # [ALFHEIM] begin: the Alfheim realm (tests/smoke_alfheim.py) in its own context, so the main run's save is untouched
        if rep["pass"] and "N" in segs:   # segment N: realm smokes used to run in EVERY shard (shards timed out)
            seg_mark("N")
            try:
                import smoke_alfheim  # noqa: E402
                smoke_alfheim.steps(b, url, T, size, errors, rep, STUB, out)
                seg_done("N")
            except Exception as e:  # noqa: BLE001
                rep["pass"] = False
                rep["error"] = f"alfheim: {e}"[:400]
        # [ALFHEIM] end
        # [SVARTALFHEIM] begin: the Svartalfheim realm (tests/smoke_svartalfheim.py), own context again
        if rep["pass"] and "O" in segs:   # segment O: realm smokes used to run in EVERY shard (shards timed out)
            seg_mark("O")
            try:
                import smoke_svartalfheim  # noqa: E402
                smoke_svartalfheim.steps(b, url, T, size, errors, rep, STUB, out)
                seg_done("O")
            except Exception as e:  # noqa: BLE001
                rep["pass"] = False
                rep["error"] = f"svartalfheim: {e}"[:400]
        # [SVARTALFHEIM] end
        # [JOTUNHEIM] begin: the Jotunheim realm (tests/smoke_jotunheim.py), own context again
        if rep["pass"] and "P" in segs:   # segment P: realm smokes used to run in EVERY shard (shards timed out)
            seg_mark("P")
            try:
                import smoke_jotunheim  # noqa: E402
                smoke_jotunheim.steps(b, url, T, size, errors, rep, STUB, out)
                seg_done("P")
            except Exception as e:  # noqa: BLE001
                rep["pass"] = False
                rep["error"] = f"jotunheim: {e}"[:400]
        # [JOTUNHEIM] end
        # [MUSPELHEIM] begin: the Muspelheim realm (tests/smoke_muspelheim.py), own context again
        if rep["pass"] and "Q" in segs:   # segment Q: realm smokes used to run in EVERY shard (shards timed out)
            seg_mark("Q")
            try:
                import smoke_muspelheim  # noqa: E402
                smoke_muspelheim.steps(b, url, T, size, errors, rep, STUB, out)
                seg_done("Q")
            except Exception as e:  # noqa: BLE001
                rep["pass"] = False
                rep["error"] = f"muspelheim: {e}"[:400]
        # [MUSPELHEIM] end
        # [NIFLHEIM] begin: the Niflheim realm (tests/smoke_niflheim.py), own context again
        if rep["pass"] and "R" in segs:   # segment R: realm smokes used to run in EVERY shard (shards timed out)
            seg_mark("R")
            try:
                import smoke_niflheim  # noqa: E402
                smoke_niflheim.steps(b, url, T, size, errors, rep, STUB, out)
                seg_done("R")
            except Exception as e:  # noqa: BLE001
                rep["pass"] = False
                rep["error"] = f"niflheim: {e}"[:400]
        # [NIFLHEIM] end
        # [VANAHEIM] begin: the Vanaheim realm incl. Stage B (tests/smoke_vanaheim.py), own context again
        if rep["pass"] and "S" in segs:   # segment S: realm smokes used to run in EVERY shard (shards timed out)
            seg_mark("S")
            try:
                import smoke_vanaheim  # noqa: E402
                smoke_vanaheim.steps(b, url, T, size, errors, rep, STUB, out)
                seg_done("S")
            except Exception as e:  # noqa: BLE001
                rep["pass"] = False
                rep["error"] = f"vanaheim: {e}"[:400]
        # [VANAHEIM] end
        # [ASGARD] begin: the Asgard realm (tests/smoke_asgard.py), own context again
        if rep["pass"] and "T" in segs:   # segment T: realm smokes used to run in EVERY shard (shards timed out)
            seg_mark("T")
            try:
                import smoke_asgard  # noqa: E402
                smoke_asgard.steps(b, url, T, size, errors, rep, STUB, out)
                seg_done("T")
            except Exception as e:  # noqa: BLE001
                rep["pass"] = False
                rep["error"] = f"asgard: {e}"[:400]
        # [ASGARD] end
        # [HELHEIM] begin: the Helheim realm (tests/smoke_helheim.py), own context again
        if rep["pass"] and "U" in segs:   # segment U: realm smokes used to run in EVERY shard (shards timed out)
            seg_mark("U")
            try:
                import smoke_helheim  # noqa: E402
                smoke_helheim.steps(b, url, T, size, errors, rep, STUB, out)
                seg_done("U")
            except Exception as e:  # noqa: BLE001
                rep["pass"] = False
                rep["error"] = f"helheim: {e}"[:400]
        # [HELHEIM] end
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
                # drop the pet 4.5 m away on open flagstones (east of the Den yard, never inside the woodpile / house blockers)
                # the catch-up is quick (speed scales with the gap), so the game records the first follow-gait frame itself
                T.ev("(() => { const G = window.__hm, a = G.pets.a, p = G.ctx.player; G.pets.gait = null; a.x = p.x + 4.5; a.z = p.z + 0.4; a.y = G.ctx.heightAt(a.x, a.z); })()"); T.frames(2)
                try:
                    T.wait("!!window.__hm.pets.state().gait", 4)
                except Exception:  # noqa: BLE001
                    pass
                far = T.ev("window.__hm.pets.state().gait") or {}
                f.wait_for_timeout(2600); T.frames(6)
                near = T.ev("(() => { const a = window.__hm.pets.a, p = window.__hm.ctx.player; return Math.hypot(a.x - p.x, a.z - p.z); })()")
                T.step("the pet follows on its own pets sheet (role pet_fox); more than 3 m behind it switches to the follow gait, then catches up within ~2 m",
                       ps["actor"] and ps["role"] == "pet_fox" and ps["actor"]["sheet"] == "pets" and far.get("hurry") and far.get("anim") == "follow" and far.get("d", 0) > 3 and near < 2.2, actor=ps["actor"], far=far, near=round(near, 2))
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
                T.ev("window.__hm.storms.force('off'); window.__hm.peace = false; window.__hm.rifts.setTimer(10.5)")   # peace off would let the 6.5 storm calendar toast over the fox's warning: storms off for this step
                T.wait("window.__hm.rifts.warned", 30)
                wn = T.ev("({ warn: window.__hm.pets.state().warned, toast: document.getElementById('toast').innerText, next: window.__hm.rifts.nextPos, open: !!window.__hm.rifts.cur })")
                T.ev("window.__hm.rifts.setTimer(0.01)"); T.until("!!window.__hm.rifts.cur", 60)
                op = T.ev("window.__hm.rifts.state().rift")
                T.ev("window.__hm.rifts.close(false, true); window.__hm.peace = true; window.__hm.storms.force(undefined)")
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
                       bool(hub) and len(hub["options"]) == 5 and "Swap" in hub["options"][0] and "Hearth" in lock and "Friend" in lock and bool(ac) and "wisp kit" in ac["options"][0] and len(ac["options"]) == 3
                       and A["pet"]["id"] == "wispkit" and A["pets"]["wispkit"]["name"] == an["options"][1] and A["gold"] == gd1 - 40 and Mw >= 0.06
                       and bool(sw) and B["pet"]["id"] == "lanternfox" and B["pet"]["name"] == nm and T.ev("window.__hm.pets.state().role") == "pet_fox", hub=hub, adopt=ac, swap=sw)
                # save + reload: the pet comes back at your side
                T.ev("window.__hm.save(true)"); f.wait_for_timeout(300)
                f.reload(); T.wait("window.__hm && window.__hm.ready && window.__hd2d && window.__hd2d.ready && !window.__hd2dGate.loading", 120)
                f.click("#btnCont"); T.idle(); T.wait("!!window.__hm.pets.a", 60); T.frames(6)
                R = T.S(); ra = T.ev("(() => { const a = window.__hm.pets.a, p = window.__hm.ctx.player; return { d: Math.hypot(a.x - p.x, a.z - p.z), role: a.role || window.__hm.pets.state().role }; })()")
                T.step("save + reload + Continue: S.pet and S.pets round-trip (both pets, names, the fed day), and the active pet spawns beside the hero",
                       R["pet"] == B["pet"] and set(R["pets"]) == {"lanternfox", "wispkit"} and R["pets"]["lanternfox"]["fed"] == 1 and ra["d"] < 2.5, pet=R["pet"], at=ra)
                # the moss-pup (a gift from Mossbrook on the 6.4 befriend path): Signe hands it over, you name it, Forager's Nose applies
                T.ev("(() => { const S = window.__hm.S; S.pets.mosspup = { name: 'Moss-pup', bond: 1, atDen: 1 }; })()")   # QA: what 6.4's befriend ending will set
                T.ev("window.__hm.loadArea('bifrost', 'start')"); T.wait("window.__hm.area === 'bifrost' && window.__hm.pets.a", 120); T.idle(); f.wait_for_timeout(300)
                mp1, mpf = T.talk("denkeeper", keep_open=True)
                to_den(); mn = T.to_choice(); f.keyboard.press("1"); f.wait_for_timeout(300); T.read_all(); T.frames(8); f.wait_for_timeout(500)
                MP = T.S(); mst = T.ev("window.__hm.pets.state()")
                Mm = T.ev("(() => { const M = window.__hm.combat.M; return { springSense: M.springSense, springBuff: M.springBuff, forage: M.forage }; })()")
                T.step("the moss-pup gift: Signe's arrival lines, name it (4 seeded names + 'Just \"Moss-pup\"'): it is active on the pets sheet (row 12), a lime light pool, Forager's Nose mods (springs 5 m, spring-fizz +15 s, forage 25%)",
                       mp1 == 2 and "toadstool hat" in mpf and bool(mn) and len(mn["options"]) == 5 and MP["pet"]["id"] == "mosspup" and MP["pets"]["mosspup"]["atDen"] == 0
                       and MP["pet"]["name"] == mn["options"][0] and mst["role"] == "pet_mosspup" and mst["lit"] and mst["light"]["color"] == "#5aec3c"
                       and mst["fx"] == ["pet_pool_mosspup", "pet_aura_mosspup"] and Mm == {"springSense": 5, "springBuff": 15, "forage": 0.25}, pet=MP["pet"], state=mst, mods=Mm)
                rep["shots"]["stage6_pet_mosspup"] = T.shot("stage6_pet_mosspup")
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
        # ---------------------------------------------------------- G: the Old Temple (Stage 6.3, continues cp3)
        if rep["pass"] and "G" in segs:
            seg_mark("G")
            try:
                saved = cp_load(None, T, url, "cp3")["hearthmoor-slot-1-v2"]
                tc = b.new_context(viewport={"width": size[0], "height": size[1]})
                tc.add_init_script(f"if (!sessionStorage.getItem('seeded')) {{ localStorage.clear(); localStorage.setItem('hearthmoor-slot-1-v2', {json.dumps(saved)}); sessionStorage.setItem('seeded', '1'); }}")
                tc.add_init_script(STUB)
                g = tc.new_page()
                g.on("pageerror", lambda e: errors.append(f"PAGEERROR {e}"))
                g.on("console", lambda m: errors.append(f"console.error {m.text}") if m.type == "error" else None)
                T.pg = g
                g.goto(url)
                T.wait("window.__hm && window.__hm.ready && window.__hd2d && window.__hd2d.ready && !window.__hd2dGate.loading", 120)
                g.click("#btnCont"); T.idle(); g.wait_for_timeout(400)

                def area(a, spawn="start"):
                    T.ev(f"window.__hm.loadArea('{a}', '{spawn}')"); T.wait(f"window.__hm.area === '{a}' && window.__hm.ctx && !window.__hm.busy", 120); T.idle(); g.wait_for_timeout(300)

                def mark(npc):
                    return T.ev(f"window.__hm.markers['{npc}'] ? window.__hm.markers['{npc}'].name : null")

                def at(x, z):
                    T.ev(f"(() => {{ const c = window.__hm.ctx, p = c.player; p.x = {x}; p.z = {z}; p.y = c.heightAt(p.x, p.z); c.stopWalk(); }})()"); T.frames(3)

                def cast():
                    T.ev("window.__hm.combat.cd = {}"); g.keyboard.press("f"); g.wait_for_timeout(700)
                # Warden Hilde (Plaza) hands over the relief basket + the Hearth writ: 'The Cold Altar' starts
                area("plaza")
                mh = mark("hilde")
                T.talk("hilde")
                S = T.S()
                T.step("Plaza: Warden Hilde (quest tag once Bifrost is done) gives the Order's relief basket + a Hearth writ: story quest 'The Cold Altar'",
                       mh == "quest_mark" and S["quests"].get("altar") == 1 and S["inv"].get("reliefbasket") == 1 and S["inv"].get("hearthwrit") == 1
                       and "Story: The Cold Altar" in T.ev("document.getElementById('logList').innerText"), mark=mh)
                # Ravenhold: Novice Edda at the Old Temple gate; the writ turns the sealed district gate into an exit up the stair
                area("ravenhold")
                rq = T.ev("window.__hm.temple.qa()")
                pe, fe = T.talk("novice")
                ex = T.ev("window.__hm.ctx.scene.game.exits.findIndex((e) => e.to === 'temple')")
                to = T.go_rect("exits", ex) if ex >= 0 else None
                T.step("Ravenhold: Novice Edda by the Old Temple gate greets the writ; the gate is no longer sealed but an exit, and walking into it climbs to the Old Temple",
                       "temple" not in rq["sealed"] and "market" in rq["sealed"] and "temple" in rq["exits"] and "A Hearth writ" in fe and to == "temple", temple=rq, edda=fe[:60], area=to)
                tq = T.ev("""(() => { const G = window.__hm, c = G.ctx, sc = c.scene, glb = (n) => sc.objects.filter((o) => o.glb.endsWith('/' + n + '.glb')).length;
                  return { npcs: ['priestess', 'archivist', 'refugee1', 'refugee2'].map((n) => !!c.npc(n)), braz: G.hollows.braziers.filter((b) => b.temple).map((b) => b.lit),
                           arch: glb('riftgate_arch'), dormant: glb('riftgate_glow_dormant'), altar: glb('temple_brazier_out'), statues: glb('faceless_statue'), windows: glb('stained_window'),
                           columns: glb('temple_column'), way: glb('waystone'), realm: G.factions.realm(), gate: c.fx.gate_midgard ? c.fx.gate_midgard.name : null,
                           roles: ['priestess', 'archivist'].map((n) => c.npc(n) && c.npc(n).role), sheet: !!(c.actors.sheetOf && c.actors.sheetOf('templekeeper')),
                           gaze: G.temple.qa().gaze, glass: G.temple.qa().glass,
                           clues: (sc.game.clues || []).length, terrace: [c.heightAt(-2.0, -6), c.heightAt(0, -10.2)], mark: G.markers.priestess ? G.markers.priestess.name : null }; })()""")
                rep["shots"]["temple_dark"] = T.shot("temple_dark")
                T.step("the Old Temple (art/old_temple pack): Mother Ilse (templekeeper, turn-in tag), Brother Tamsin (archivist), 2 refugees; 3 dark stair braziers + the cold altar (temple_brazier_out x4) on the nave terrace (1.2 m), 4 faceless statues, 2 stained windows (dusk glass-light pools), 2 columns, the dormant Rift-gate (riftgate_arch + dormant glow, riftgate_seal_dormant) on the inner court (2 m), a waystone; Hearth realm",
                       tq["npcs"] == [True] * 4 and tq["braz"] == [False] * 3 and tq["arch"] == 1 and tq["dormant"] == 1 and tq["altar"] == 4 and tq["statues"] == 4 and tq["windows"] == 2
                       and tq["columns"] == 2 and tq["roles"] == ["templekeeper", "archivist"] and tq["sheet"] and tq["glass"] == 2
                       and tq["way"] == 1 and tq["realm"] == "hearth"
                       and tq["gate"] == "riftgate_seal_dormant" and tq["clues"] == 3 and abs(tq["terrace"][0] - 1.2) < 0.05 and abs(tq["terrace"][1] - 2.0) < 0.05 and tq["mark"] == "quest_turnin", temple=tq)
                face = T.ev("""(() => { const G = window.__hm, n = G.ctx.npc('priestess'); G.openDialogue(n, { pages: ['...'] });
                  return new Promise((res) => setTimeout(() => { const cv = document.getElementById('dlgFace'), d = cv.getContext('2d').getImageData(0, 0, cv.width, cv.height).data;
                    let k = 0; for (let i = 3; i < d.length; i += 4) if (d[i]) k++; G.dropDialogue(); res({ sheet: n.rect && n.rect.sheet, px: k }); }, 500)); })()""")
                T.step("Ilse's dialogue face is cropped from her own old_temple sheet (drawPortrait reads a role's own sheet, not column 0 of the main atlas)",
                       face["sheet"] == "old_temple" and face["px"] > 40, face=face)
                h0 = T.ev("window.__hm.S.merit.hearth || 0")
                pi, fi = T.talk("priestess")
                S = T.S()
                T.step("Mother Ilse takes the basket (5 pages): +40 Hearth Tokens (refuge), the Temple waystone attunes, 'The Cold Altar' moves on to the clues",
                       pi == 5 and S["quests"]["altar"] == 2 and not S["inv"].get("reliefbasket") and S["merit"]["hearth"] == h0 + 40 and S["flags"]["ways"].get("temple") == 1, first=fi[:60])
                T.talk("archivist")
                got = []
                for c in T.ev("window.__hm.ctx.scene.game.clues"):
                    T.walk(c["pos"][0], c["pos"][1] + 0.4)
                    if not T.ev("window.__hm.temple.near()"): at(c["pos"][0], c["pos"][1] + 0.4)   # a prop in the way: stand on the spot
                    pr = T.ev("document.getElementById('prompt').textContent")
                    g.keyboard.press("e"); g.wait_for_timeout(300)
                    who = T.ev("window.__hm.dlg ? window.__hm.dlg.npc.id : null"); T.read_all()
                    got.append([c["id"], who, "look" in pr, T.ev(f"!!window.__hm.S.found.{c['id']}")])
                tl = T.talk("archivist")[1]
                mi = mark("priestess")
                T.step("Brother Tamsin's first talk; the 3 clue spots in the nave (E: 'The nave' narration) are noted 3/3; Tamsin comments on the last one; Ilse shows a turn-in tag",
                       all(x[1] == "clue" and x[2] and x[3] for x in got) and len(got) == 3 and mi == "quest_turnin"
                       and "Tell Mother Ilse what the clues say" in T.ev("document.getElementById('logList').innerText"), clues=got, tamsin=tl[:60])
                h1 = T.ev("window.__hm.S.merit.hearth"); gd = T.ev("window.__hm.S.gold || 0")
                T.talk("priestess"); S = T.S()
                b1 = T.ev("window.__hm.hollows.braziers.find((b) => b.id === 'tm_b1').pos")
                T.walk(b1[0] + 0.6, b1[1] + 0.7); cast()
                nag = T.ev("({ lit: window.__hm.hollows.braziers.find((b) => b.id === 'tm_b1').lit, toast: document.getElementById('toast').innerText })")
                T.step("Ilse: 'The Cold Altar' done (+60 Hearth Tokens, +30 gold), 'Keeper of the Gate' starts; a spell at a stair brazier won't catch without a warden's flame",
                       S["quests"]["altar"] == 3 and S["quests"].get("gate") == 1 and S["merit"]["hearth"] >= h1 + 60 and S["gold"] >= gd + 30 and not nag["lit"] and "warden" in nag["toast"], nag=nag)
                # Grandpa Alder gives Warden Aldis's lantern charm; Ida Wickmere lights it with a cold-fire wick
                area("plaza"); me = mark("elder"); T.talk("elder")
                area("ravenhold"); mc = mark("chandler"); T.talk("chandler")
                for _ in range(4):
                    if not T.ev("!!window.__hm.shop"): break
                    g.keyboard.press("Escape"); g.wait_for_timeout(200)
                S = T.S()
                T.step("Grandpa Alder (quest tag) gives Warden Aldis's lantern charm; Ida Wickmere (turn-in tag) lights it with a cold-fire wick (then her shop opens)",
                       me == "quest_mark" and mc == "quest_turnin" and S["inv"].get("alder_charm") == 1 and S["flags"].get("tm_wick") == 1, marks=[me, mc])
                # the three stair braziers take the charm's flame; the first one stirs two wraiths out of the inner court
                area("temple", "from_waystone")
                lit = []
                for bid in ("tm_b1", "tm_b2", "tm_b3"):
                    bp = T.ev(f"window.__hm.hollows.braziers.find((b) => b.id === '{bid}').pos")
                    T.walk(bp[0] + 0.6, bp[1] + 0.7)
                    for _ in range(3):
                        cast()
                        if T.ev(f"!!window.__hm.S.found.{bid}"): break
                    lit.append(T.ev(f"!!window.__hm.S.found.{bid}"))
                wr = T.ev("window.__hm.combat.enemies.filter((e) => /^tm_wraith_/.test(e.id)).length")
                T.ev("(() => { const G = window.__hm, C = G.combat, p = G.ctx.player; for (const e of C.enemies) if (/^tm_wraith_/.test(e.id)) for (let i = 0; i < 60 && e.state !== 'dead' && e.state !== 'gone'; i++) C.damageEnemy(e, 80, p); })()")
                T.step("cast at each of the 3 stair braziers: the charm's flame lights them (toasts n/3); the first stirs 2 wraiths out of the inner court; Ilse shows a turn-in tag",
                       lit == [True] * 3 and wr == 2 and mark("priestess") == "quest_turnin" and "Bring it to Mother Ilse" in T.ev("document.getElementById('logList').innerText"), lit=lit, wraiths=wr)
                # the rite: Ilse offers a cot until dusk (it is day), then the altar, the Rift-gate, the scripted major rift
                T.ev("(() => { const G = window.__hm; G.ctx.clock.set(0.6); G.S.t = G.ctx.clock.t; })()"); T.frames(4)
                T.talk("priestess", keep_open=True); rc = T.to_choice()
                g.keyboard.press("1"); g.wait_for_timeout(300); T.read_all()
                tday = T.ev("window.__hm.ctx.clock.t")
                al = T.ev("window.__hm.ctx.scene.game.altar.use"); T.walk(al[0], al[1])
                if T.ev("(window.__hm.temple.near() || {}).kind") != "altar": at(al[0], al[1])
                g.keyboard.press("e"); g.wait_for_timeout(300); T.read_all(); T.frames(10); g.wait_for_timeout(600)
                av = T.ev("({ altar: window.__hm.S.flags.tm_altar, lit: window.__hm.temple.qa().lit, zone: window.__hm.glow.zones().some((z) => z.src === 'temple'), burning: window.__hm.hollows.braziers.filter((b) => b.temple && b.burning).length })")
                T.step("Ilse (day): 'Rest on a refugee cot until dusk' skips to dusk; E at the cold altar sets the charm: the sacred brazier roars awake (a light zone), the stair braziers burn",
                       bool(rc) and len(rc["options"]) == 2 and "cot" in rc["options"][0] and T.ev("window.__hm.S.quests.gate") == 2 and tday >= 0.74
                       and av["altar"] == 1 and av["lit"] == ["altar"] and av["zone"] and av["burning"] == 3, choice=rc, t=tday, altar=av)
                gu = T.ev("window.__hm.ctx.scene.game.riftgate.use"); T.walk(gu[0], gu[1])
                if T.ev("(window.__hm.temple.near() || {}).kind") != "gate": at(gu[0], gu[1])
                g.keyboard.press("e"); g.wait_for_timeout(300); T.read_all(); T.frames(8)
                rs = T.ev("window.__hm.rifts.state().rift"); gfx = T.ev("window.__hm.ctx.fx.gate_midgard.name")
                rep["shots"]["temple_rift"] = T.shot("temple_rift")
                T.ev("(() => { const G = window.__hm, c = G.ctx, p = c.player, R = G.rifts.cur, col = c.collide; const ok = (x, z) => !col || !col.blocked(x, z); const o = [[-1.4, 0.6], [-2.2, 0.6], [2.2, 0.6], [0, 1.6]].find(([dx, dz]) => ok(R.pos[0] + dx, R.pos[1] + dz)) || [0, 1.6]; p.x = R.pos[0] + o[0]; p.z = R.pos[1] + o[1]; p.y = c.heightAt(p.x, p.z); c.stopWalk(); })()")   # free spot beside the rift: the Temple rift sits on the court stair, and x-1.4 is the stair side wall (a blocked cell)
                T.frames(6); g.wait_for_timeout(400)
                for _ in range(3):
                    if not T.ev("window.__hm.rifts.cur"): break
                    T.ev("(() => { const G = window.__hm, C = G.combat, p = G.ctx.player; G.peace = true; for (const e of G.rifts.alive()) for (let i = 0; i < 60 && e.state !== 'dead' && e.state !== 'gone'; i++) C.damageEnemy(e, 80, p); })()")
                    T.frames(8); g.wait_for_timeout(500)
                T.step("E at the dark Rift-gate raises the charm: the gate wakes (riftgate_vortex_lit + the riftgate_ring_lit rune ring), and a scripted major rift (tier II, tagged 'temple', no rare) tears open above the court; sealing it sets tm_rift",
                       rs and rs["tag"] == "temple" and rs["id"] == "major" and gfx == "riftgate_vortex_lit" and T.ev("window.__hm.temple.qa().ring") == "riftgate_ring_lit" and not T.ev("window.__hm.rifts.cur") and T.ev("window.__hm.S.flags.tm_rift") == 1, rift=rs, gate=gfx)
                T.wait("window.__hm.dlg && window.__hm.dlg.npc.id === 'veyra'", 30)
                vn = T.ev("window.__hm.dlg.npc.name"); T.read_all(); T.frames(4)
                T.wait("!window.__hm.dlg", 30)
                T.step("Veyra's cameo (toggleable: TEMPLE.veyra / ?noveyra): a frost-witch in grey-blue seals the last crack, names herself, hands you the Plaguewell hook; met_veyra set",
                       vn == "A frost-witch in grey-blue" and T.ev("window.__hm.S.flags.met_veyra") == 1, veyra=vn)
                h2 = T.ev("window.__hm.S.merit.hearth"); gm0 = T.ev("(window.__hm.S.gems || {}).frost_core || 0")
                pi2, fi2 = T.talk("priestess"); T.frames(6); g.wait_for_timeout(400)
                S = T.S(); tq2 = T.ev("window.__hm.temple.qa()")
                rep["shots"]["temple_lit"] = T.shot("temple_lit")
                T.step("Ilse: 'Keeper of the Gate' done (+120 Hearth Tokens, +60 gold, a frost core); temple_lit: the Rift-gate is a portal to Bifrost Crossing",
                       pi2 == 4 and "Rift-Warden" in fi2 and S["quests"]["gate"] == 3 and S["flags"].get("temple_lit") == 1 and S["merit"]["hearth"] == h2 + 120
                       and S["gems"].get("frost_core", 0) == gm0 + 1 and "bifrost" in tq2["portals"], temple=tq2)
                # through the Rift-gate to the Crossing: Midgard's arch is open; Halvard pays 40 Rift Marks for a gate repaired
                pidx = T.ev("window.__hm.ctx.scene.game.portals.findIndex((p) => p.to === 'bifrost')")
                to = T.go_rect("portals", pidx)
                bq = T.ev("window.__hm.temple.qa()"); mk = mark("gatewright"); g0 = T.ev("window.__hm.S.merit.gate"); arrive = T.pos()   # where the portal set us down (before walking to Halvard)
                ph, fh = T.talk("gatewright")
                T.step("the lit Rift-gate steps out at Bifrost's Midgard arch: no longer sealed but a swirl (portal back to the Temple); Halvard (turn-in tag) pays +40 Rift Marks and eyes your charm",
                       to == "bifrost" and abs(arrive[0] - 11.0) < 1.5 and "midgard" not in bq["sealed"] and "temple" in bq["portals"] and bq["gate"] == "rift_vortex"
                       and mk == "quest_turnin" and ph == 3 and "Midgard's arch is lit" in fh and T.ev("window.__hm.S.merit.gate") == g0 + 40, why={"to": to, "pos": arrive[:2], "midSealed": "midgard" in bq["sealed"], "portals": bq["portals"], "mark": mk, "ph": ph, "fh": (fh or "")[:80], "dg": T.ev("window.__hm.S.merit.gate") - g0}, bifrost=bq)
                pidx = T.ev("window.__hm.ctx.scene.game.portals.findIndex((p) => p.to === 'temple')")
                to = T.go_rect("portals", pidx)
                T.step("Midgard's arch leads back into the Old Temple, in front of its Rift-gate", to == "temple" and T.pos()[1] < -8.5, pos=T.pos())
                T.step("no JS errors (Old Temple)", not errors and not T.ev("window.__hd2d.errors.length"), errors=errors[:5])
                tc.close()
                seg_done("G")
            except Exception as e:  # noqa: BLE001
                rep["pass"] = False
                rep["error"] = f"temple: {type(e).__name__}: {e}"[:400]
                try:
                    rep["shots"]["failure_G"] = T.shot("failure_G"); rep["state"] = T.S()
                except Exception:  # noqa: BLE001
                    pass
        # ---------------------------------------------------------- H: rift storms (Stage 6.5, continues cp3)
        if rep["pass"] and "H" in segs:
            seg_mark("H")
            try:
                saved = cp_load(None, T, url, "cp3")["hearthmoor-slot-1-v2"]
                hc = b.new_context(viewport={"width": size[0], "height": size[1]})
                hc.add_init_script(f"if (!sessionStorage.getItem('seeded')) {{ localStorage.clear(); localStorage.setItem('hearthmoor-slot-1-v2', {json.dumps(saved)}); sessionStorage.setItem('seeded', '1'); }}")
                hc.add_init_script(STUB)
                h = hc.new_page()
                h.on("pageerror", lambda e: errors.append(f"PAGEERROR {e}"))
                h.on("console", lambda m: errors.append(f"console.error {m.text}") if m.type == "error" else None)
                T.pg = h
                h.goto(url + "&rifts")   # random rifts on (this context only): the storm's own timers are under test
                T.wait("window.__hm && window.__hm.ready && window.__hd2d && window.__hd2d.ready && !window.__hd2dGate.loading", 120)
                h.click("#btnCont"); T.idle(); h.wait_for_timeout(400)

                def harea(a, spawn="start"):
                    T.ev(f"window.__hm.loadArea('{a}', '{spawn}')"); T.wait(f"window.__hm.area === '{a}' && window.__hm.ctx && !window.__hm.busy", 120); T.idle(); h.wait_for_timeout(300)
                KILL_H = ("(() => { const G = window.__hm, C = G.combat, p = G.ctx.player; G.peace = true;"
                          " for (const e of G.rifts.alive()) for (let i = 0; i < 60 && e.state !== 'dead' && e.state !== 'gone'; i++) C.damageEnemy(e, 80, p); })()")

                def seal_cur():
                    T.ev("(() => { const G = window.__hm, c = G.ctx, p = c.player, R = G.rifts.cur; p.x = R.pos[0] - 1.4; p.z = R.pos[1] + 0.6; p.y = c.heightAt(p.x, p.z); c.stopWalk(); })()")
                    T.frames(6); h.wait_for_timeout(300)
                    for _ in range(4):
                        if not T.ev("window.__hm.rifts.cur"): break
                        T.ev(KILL_H); T.frames(8); h.wait_for_timeout(400)
                    return not T.ev("window.__hm.rifts.cur")
                cal = T.ev("""(() => { const G = window.__hm; let b = 0, w = 0, two = 0, prev = null; const N = 800;
                  for (let d = 1; d <= N; d++) { const r = G.stormAt(d); if (r === 'bifrost') { b++; if (prev === 'bifrost') two++; } else if (r) w++; prev = r; }
                  return { b: b / N, w: w / N, two, d0: G.stormAt(0), same: G.stormAt(17) === G.stormAt(17) }; })()""")
                T.step("storm calendar stormAt(day) (pure, seeded by the day): Bifrost ~1 night in 4, never two nights running, never day 0; Midgard / Vanaheim world event ~1 in 10 of the rest",
                       0.2 <= cal["b"] <= 0.3 and cal["two"] == 0 and cal["d0"] is None and 0.05 <= cal["w"] <= 0.11 and cal["same"], cal=cal)
                harea("bifrost")
                T.ev("(() => { const G = window.__hm; G.peace = true; G.ctx.clock.set(0.5); G.S.t = 0.5; G.storms.force(undefined); })()"); T.frames(4)
                day_ok = T.ev("({ storm: window.__hm.storms.state().storm, wx: window.__hm.weather.kind, auto: window.__hm.rifts.canAuto() })")
                T.ev("(() => { const G = window.__hm; G.ctx.clock.set(0.86); G.S.t = 0.86; G.rifts.close(false, true); G.storms.force('bifrost'); })()"); T.frames(6)
                st = T.ev("window.__hm.storms.state()"); toastq = T.ev("document.getElementById('toast').innerText + ' | ' + window.__hm.toastQueue().join(' | ')")
                T.frames(4)
                sp = T.ev("""(() => { const G = window.__hm, sc = G.ctx.scene.game, R = G.rifts, pool = R.pool();
                  const keep = [...sc.sealed.map((g) => g.pos), ...sc.portals.map((p) => [(p.rect[0] + p.rect[2]) / 2, (p.rect[1] + p.rect[3]) / 2]), sc.ferry.pos, sc.waystone.pos,
                                ...G.hollows.braziers.filter((b) => b.den).map((b) => b.pos), [-5.6, 3.9], [G.ctx.npc('denkeeper').x, G.ctx.npc('denkeeper').z], [G.ctx.npc('gatewright').x, G.ctx.npc('gatewright').z]];
                  const md = Math.min(...pool.spots.map((s) => Math.min(...keep.map((k) => Math.hypot(s[0] - k[0], s[1] - k[1])))));
                  return { n: pool.spots.length, md: +md.toFixed(2), timer: R.state().timer, storm: R.storm(), auto: R.canAuto(), wx: G.weather.kind }; })()""")
                T.step("Bifrost by day: no storm, no rifts by themselves; at night a forced Bifrost rift storm breaks: the RIFT STORM banner, the riftstorm weather, the rift timer drops to 10-20 s",
                       day_ok["storm"] is None and not day_ok["auto"] and st["storm"] == "bifrost" and st["here"] and st["run"]["sealed"] == 0 and "RIFT STORM" in toastq
                       and sp["wx"] == "riftstorm" and sp["auto"] and sp["timer"] <= 20.5, day=day_ok, storm=st, toast=toastq[:160], spots=sp)
                T.step("storm-only rift spots at the Crossing (5) sit clear of the nine arches, the Vanaheim swirl, the Den yard, the skiff landing, the waystone and Halvard's kiosk (>= 2.5 m)",
                       sp["n"] == 5 and sp["md"] >= 2.5, spots=sp)
                T.until("!!window.__hm.rifts.cur", 150)
                rs = T.ev("window.__hm.rifts.state().rift"); ot = T.ev("document.getElementById('toast').innerText")
                g0 = T.ev("window.__hm.S.merit.gate || 0"); mul = T.ev("window.__hm.combat.M.riftMarkMul || 0")
                tier = rs["tier"]; ok1 = seal_cur()
                g1 = T.ev("window.__hm.S.merit.gate || 0"); st1 = T.ev("window.__hm.storms.state()")
                want = round([30, 60, 120][tier] * (1 + mul + 0.25))
                T.step("a storm rift opens by itself within ~20 s at a storm spot ('The storm tears a rift open nearby!' family); sealing it pays Rift Marks x1.25 (on top of the fox) and counts 1 for the storm",
                       rs and rs["inStorm"] and any(abs(rs["pos"][0] - x) < 1.5 and abs(rs["pos"][1] - z) < 1.5 for x, z in T.ev("window.__hm.rifts.pool().spots"))
                       and ok1 and g1 - g0 == want and st1["run"]["sealed"] == 1, rift=rs, toast=ot[:80], marks=[g0, g1, want], storm=st1["run"])
                T.until("window.__hm.storms.state().cracks >= 1", 150)
                ck = T.ev("window.__hm.storms.state()")
                T.step("storm sky: rift_tear_minor cracks high above, cold-fire motes and short violet / red point-light flashes every 6-10 s (no bloom, no screen flash)", ck["cracks"] >= 1, storm=ck)
                T.idle(); T.until("!window.__hm.ctx.walking() && !window.__hm.busy", 30)  # settle after storm rift seal before talking (nav flake at talk-range edge)
                pg_, fh = T.talk("gatewright", keep_open=True)
                pages_h = T.ev("window.__hm.dlg.pages.slice(0, 2)")
                ch = T.to_choice()
                labels = ch["options"] if ch else []
                k = next((i for i, l in enumerate(labels) if "storm work" in l), -1)
                if k >= 0:   # the number keys only pick answers 1-4 and this hub has more rows now: walk the highlight down with the arrow keys, then E
                    for _ in range(k): h.keyboard.press("ArrowDown"); h.wait_for_timeout(120)
                    h.keyboard.press("e"); h.wait_for_timeout(300)
                T.read_all()
                logt = T.ev("document.getElementById('logList').innerText")
                T.step("Halvard in the storm: his storm line, then the quiet keys foreshadow; 'Any storm work?' posts the Storm Watch bounty (log: 'Seal 3 rifts during the rift storm (over Bifrost Crossing). 1/3')",
                       "quarter extra" in pages_h[0] and "up all night with the keys" in pages_h[1] and k >= 0 and T.ev("window.__hm.S.quests.stormwatch") == 1
                       and "over Bifrost Crossing). 1/3" in logt, pages=pages_h, options=labels)
                for _ in range(2):
                    T.ev("window.__hm.rifts.open(0)"); T.frames(4); seal_cur()
                st3 = T.ev("window.__hm.storms.state()"); mk = T.ev("window.__hm.markers.gatewright ? window.__hm.markers.gatewright.name : null")
                T.step("two more storm rifts sealed: 3 tonight ('Three rifts sealed tonight...'), Storm Watch moves to 'Report to Gatewright Halvard', Halvard shows a turn-in tag",
                       st3["run"]["sealed"] == 3 and T.ev("window.__hm.S.quests.stormwatch") == 2 and mk == "quest_turnin", storm=st3["run"], mark=mk)
                S0 = T.S(); xp0 = T.ev("window.__hm.S.xp || 0"); lv0 = T.ev("window.__hm.S.lv || 1"); e0 = T.ev("document.getElementById('btnLog').textContent")
                T.talk("gatewright"); S1 = T.S()
                T.step("Storm Watch turn-in: +60 Rift Marks, +40 gold, a rift shard, 'Bounty done'; no Hearth Tokens, not an errand (quests n/3 unchanged), S.bountyDone.stormwatch = 1",
                       S1["quests"]["stormwatch"] == 3 and S1["merit"]["gate"] == S0["merit"]["gate"] + 60 and S1["gold"] >= S0["gold"] + 40
                       and S1["gems"].get("rift_shard", 0) == S0["gems"].get("rift_shard", 0) + 1 and S1["merit"].get("hearth", 0) == S0["merit"].get("hearth", 0)
                       and S1["bountyDone"]["stormwatch"] == 1 and T.ev("document.getElementById('btnLog').textContent") == e0, gate=[S0["merit"]["gate"], S1["merit"]["gate"]])
                fl = T.ev("(() => { const G = window.__hm; G.harbor.openFerry(); const p = G.dlg ? G.dlg.pages[0] : null; return p; })()")
                T.to_choice(); h.keyboard.press("Escape"); h.wait_for_timeout(200)
                while T.ev("!!window.__hm.dlg"): h.keyboard.press("Escape"); h.wait_for_timeout(120)
                T.step("the skiff still sails in the storm (never strands you), with the storm warning line at the landing", fl and "Storm's pushing the current" in fl, line=fl)
                harea("rift")
                ro = T.ev("({ here: window.__hm.storms.state().here, auto: window.__hm.rifts.canAuto(), n: window.__hm.rifts.pool().spots.length, wx: window.__hm.weather.kind })")
                po, fo = T.talk("riftkeeper")
                T.step("the Rift Shrine is in the Bifrost storm region too: storm-only rift spots at the dais edge, the riftstorm weather; Ondra: 'Something pulls at it from the cold side.'",
                       ro["here"] and ro["auto"] and ro["n"] == 3 and ro["wx"] == "riftstorm" and "cold side" in fo, shrine=ro, ondra=fo[:80])
                harea("ravenhold")
                rv = T.ev("({ here: window.__hm.storms.state().here, auto: window.__hm.rifts.canAuto(), wx: window.__hm.weather.kind, nell: window.__hm.ctx.npc('dockkid') && window.__hm.ctx.npc('dockkid').name })")
                pn, fn_ = T.talk("dockkid")
                T.step("Ravenhold sees the storm from afar (no rifts, normal weather); the dock kid is now Nell (display name only) and talks about the lantern-eels in the storm",
                       not rv["here"] and not rv["auto"] and rv["wx"] != "riftstorm" and rv["nell"] == "Nell" and "lantern-eels are going crazy" in fn_, harbor=rv, nell=fn_[:80])
                T.ev("(() => { const G = window.__hm; G.ctx.clock.set(0.3); G.S.t = 0.3; })()"); T.frames(6)
                dq = T.ev("window.__hm.toastQueue().join(' | ') + ' | ' + document.getElementById('toast').innerText"); sd = T.ev("window.__hm.storms.state()")
                T.step("dawn ends the storm: S.flags.storm cleared, stormAfter = today, 'Storm weathered: 3 rifts sealed...' (outside the region: 'Dawn. The Rift above Ravenhold goes quiet again.')",
                       sd["storm"] is None and sd["after"] == T.ev("window.__hm.S.day || 0") and "quiet again" in dq and "3 rifts sealed" in dq, storm=sd, toasts=dq[:200])
                c0 = T.ev("window.__hm.S.merit.corsair || 0")
                pb, fb = T.talk("harbormaster")
                pq, fq = T.talk("quartermaster"); c1 = T.ev("window.__hm.S.merit.corsair || 0")
                pb2, fb2 = T.talk("harbormaster")
                T.step("the morning after: Brannoc raises a mug (once per storm), Sable toasts too and pays +15 Black Doubloons (3+ sealed); Brannoc's next talk is his morning-after line",
                       "Raise your mugs" in fb and "Rift that didn't eat us" in fq and c1 == c0 + 15 and "All boats home" in fb2
                       and T.ev("window.__hm.S.flags.toasted.harbormaster") == T.ev("window.__hm.S.flags.stormAfter"), lines=[fb[:40], fq[:40], fb2[:40]], corsair=[c0, c1])
                harea("bifrost")
                T.ev("(() => { const G = window.__hm; G.ctx.clock.set(0.86); G.S.t = 0.86; G.rifts.close(false, true); })()"); T.frames(6)
                rp = T.ev("({ storm: window.__hm.storms.state().storm, q: window.__hm.S.quests.stormwatch, sealed: window.__hm.S.storm.sealed })")
                T.ev("(() => { const G = window.__hm; G.S.quests.stormwatch = 2; G.S.storm.sealed = 3; G.refreshMarkers && G.refreshMarkers(); })()")
                x0 = T.ev("window.__hm.S.xpTotal || 0"); T.ev("window.__hm.__xp = []; const g = window.__hm.gainXP; window.__hm.gainXP = (n, o) => { window.__hm.__xp.push(n); return g(n, o); }")
                T.talk("gatewright"); xps = T.ev("window.__hm.__xp"); full = T.ev("window.__hm.PR.XP.errand")
                T.step("the next storm night: Storm Watch is posted fresh (back to 0, the storm count reset); a repeat turn-in pays half XP (bountyDone 2)",
                       rp["storm"] == "bifrost" and rp["q"] == 0 and rp["sealed"] == 0 and full / 2 in xps and T.ev("window.__hm.S.bountyDone.stormwatch") == 2, repeat=rp, xp=xps, full=full)
                T.ev("(() => { const G = window.__hm; G.storms.force(undefined); })()")
                T.step("no JS errors (rift storms)", not errors and not T.ev("window.__hd2d.errors.length"), errors=errors[:5])
                hc.close()
                seg_done("H")
            except Exception as e:  # noqa: BLE001
                rep["pass"] = False
                rep["error"] = f"storms: {type(e).__name__}: {e}"[:400]
                try:
                    rep["shots"]["failure_H"] = T.shot("failure_H"); rep["state"] = T.S()
                except Exception:  # noqa: BLE001
                    pass
        # ---------------------------------------------------------- I: Stage 6.4 groundwork (continues cp3)
        if rep["pass"] and "I" in segs:
            seg_mark("I")
            try:
                saved = cp_load(None, T, url, "cp3")["hearthmoor-slot-1-v2"]
                ic = b.new_context(viewport={"width": size[0], "height": size[1]})
                ic.add_init_script(f"if (!sessionStorage.getItem('seeded')) {{ localStorage.clear(); localStorage.setItem('hearthmoor-slot-1-v2', {json.dumps(saved)}); sessionStorage.setItem('seeded', '1'); }}")
                ic.add_init_script(STUB)
                ip = ic.new_page()
                ip.on("pageerror", lambda e: errors.append(f"PAGEERROR {e}"))
                ip.on("console", lambda m: errors.append(f"console.error {m.text}") if m.type == "error" else None)
                T.pg = ip
                ip.goto(url)
                T.wait("window.__hm && window.__hm.ready && window.__hd2d && window.__hd2d.ready && !window.__hd2dGate.loading", 120)
                ip.click("#btnCont"); T.idle(); ip.wait_for_timeout(400)

                def iarea(a, spawn="start"):
                    T.ev(f"window.__hm.loadArea('{a}', '{spawn}')"); T.wait(f"window.__hm.area === '{a}' && window.__hm.ctx && !window.__hm.busy", 120); T.idle(); ip.wait_for_timeout(300)
                iarea("mossglen")
                T.ev("(() => { const C = window.__hm.combat; delete C.defeated['mossglen:eldergolem']; if (!C.enemies.find((e) => e.id === 'eldergolem' && e.state !== 'dead')) C.spawnEnemy({ id: 'eldergolem', role: 'eldergolem', pos: [window.__hm.ctx.player.x + 3, window.__hm.ctx.player.z] }); })()")
                T.frames(4)
                gn = T.ev("(() => { const e = window.__hm.combat.enemies.find((x) => x.id === 'eldergolem' && x.state !== 'dead'); return e ? e.D.name : null; })()")
                pulls = T.ev("[2.5, 5.5, 6].map((k) => +window.__hm.framePullFor(k).toFixed(3))")
                T.step("the Mossglen golem is now 'Glenheart, the Elder Golem' (display name only, id eldergolem); boss camera pull: 2.5x unchanged (1.18), 5.5x / 6x bosses ~1.8-1.9 (engine clamp 2.0)",
                       gn == "Glenheart, the Elder Golem" and pulls[0] == 1.18 and 1.75 <= pulls[1] <= 1.9 and 1.85 <= pulls[2] <= 2.0, golem=gn, pulls=pulls)
                S0 = T.S(); xp0 = T.ev("window.__hm.S.xp || 0"); d0 = T.ev("window.__hm.loot.drops ? window.__hm.loot.drops.length : -1")
                yv = T.ev("""(() => { const G = window.__hm, C = G.combat, e = C.enemies.find((x) => x.id === 'eldergolem' && x.state !== 'dead'); G.peace = true;
                  let fired = 0; e.sp = { ...e.sp, trial: true }; e.onYield = () => { fired++; }; C.damageEnemy(e, 99999, G.ctx.player);
                  return { yielded: !!e.yielded, state: e.state, fired, trials: (G.S.trials || {}).eldergolem || 0, def: C.defeated['mossglen:eldergolem'] || 0 }; })()""")
                T.frames(4); S1 = T.S()
                T.step("trial mode (Hjortur's guardian trial): a trial foe at 0 HP yields instead of dying: onYield fires, S.trials counts it; no XP, no Legendary / loot, no boss merit, no respawn timer",
                       yv["yielded"] and yv["fired"] == 1 and yv["trials"] == 1 and yv["def"] == 0 and T.ev("window.__hm.S.xp || 0") == xp0
                       and (S1.get("bosses") or {}).get("eldergolem", 0) == (S0.get("bosses") or {}).get("eldergolem", 0) and S1["merit"] == S0["merit"]
                       and T.ev("window.__hm.loot.drops ? window.__hm.loot.drops.length : -1") == d0, trial=yv)
                iarea("vanaheim")
                cv = T.ev("""(() => { const G = window.__hm, F = (G.S.flags = G.S.flags || {}), was = (F.alliance || {}).vanaheim;
                  F.alliance = { ...(F.alliance || {}), vanaheim: 'conquer' }; const g0 = G.S.merit.gate || 0, e0 = G.S.merit.embassy || 0, rc = G.factions.realm(); G.factions.onBoss();
                  const out = { rc, dg: (G.S.merit.gate || 0) - g0, de: (G.S.merit.embassy || 0) - e0 };
                  F.alliance.vanaheim = 'befriend'; out.rb = G.factions.realm(); F.alliance.vanaheim = was; if (was === undefined) delete F.alliance.vanaheim; return out; })()""")
                T.step("Vanaheim conqueror: realm merit there routes to Rift Marks (a boss kill pays +80 gate, 0 Realm Favor); befriended it stays Realm Favor (embassy)",
                       cv["rc"] == "gate" and cv["dg"] == 80 and cv["de"] == 0 and cv["rb"] == "embassy", conquer=cv)
                iarea("ravenhold")
                T.ev("window.__hm.give('heartwood', 1)")
                c0 = T.ev("window.__hm.S.merit.corsair || 0"); h0 = T.ev("window.__hm.S.merit.hearth || 0")
                hfloor = T.ev("window.__hm.FA.FAC_NEED[(window.__hm.S.ranks || {}).hearth || 0] || 0")   # merit never drops below the current rank's floor
                T.talk("quartermaster", keep_open=True); chq = T.to_choice()
                labs = chq["options"] if chq else []
                k = next((i for i, l in enumerate(labs) if "heartwood" in l), -1)
                if k >= 0: ip.keyboard.press(str(k + 1)); ip.wait_for_timeout(300)
                T.read_all()
                T.step("conquer sale: Sable buys the Regent's heartwood: +60 Black Doubloons, -5 Hearth standing (never below the rank floor), the slab leaves the bag",
                       k >= 0 and T.ev("window.__hm.S.merit.corsair || 0") == c0 + 60 and T.ev("window.__hm.S.merit.hearth || 0") == max(hfloor, h0 - 5) and not T.ev("window.__hm.S.inv.heartwood"), options=labs)
                T.step("no JS errors (6.4 groundwork)", not errors and not T.ev("window.__hd2d.errors.length"), errors=errors[:5])
                ic.close()
                seg_done("I")
            except Exception as e:  # noqa: BLE001
                rep["pass"] = False
                rep["error"] = f"vanaheim4: {type(e).__name__}: {e}"[:400]
                try:
                    rep["shots"]["failure_I"] = T.shot("failure_I"); rep["state"] = T.S()
                except Exception:  # noqa: BLE001
                    pass
        # ---------------------------------------------------------- J: Stage 6.4 Vanaheim's dungeons (continues cp3)
        if rep["pass"] and "J" in segs:
            seg_mark("J")
            try:
                saved = cp_load(None, T, url, "cp3")["hearthmoor-slot-1-v2"]
                jc = b.new_context(viewport={"width": size[0], "height": size[1]})
                jc.add_init_script(f"if (!sessionStorage.getItem('seeded')) {{ localStorage.clear(); localStorage.setItem('hearthmoor-slot-1-v2', {json.dumps(saved)}); sessionStorage.setItem('seeded', '1'); }}")
                jc.add_init_script(STUB)
                jp = jc.new_page()
                jp.on("pageerror", lambda e: errors.append(f"PAGEERROR {e}"))
                jp.on("console", lambda m: errors.append(f"console.error {m.text}") if m.type == "error" else None)
                T.pg = jp
                jp.goto(url)
                T.wait("window.__hm && window.__hm.ready && window.__hd2d && window.__hd2d.ready && !window.__hd2dGate.loading", 120)
                jp.click("#btnCont"); T.idle(); jp.wait_for_timeout(400)

                def jarea(a, spawn="start"):
                    T.ev(f"window.__hm.loadArea('{a}', '{spawn}')"); T.wait(f"window.__hm.area === '{a}' && window.__hm.ctx && !window.__hm.busy", 120); T.idle(); jp.wait_for_timeout(300)

                def tp(x, z):
                    T.ev(f"(() => {{ const p = window.__hm.ctx.player; p.x = {x}; p.z = {z}; }})()"); T.frames(3)
                jarea("vanaheim")
                T.ev("(() => { const G = window.__hm, F = (G.S.flags = G.S.flags || {}); G.peace = true; F.alliance = { ...(F.alliance || {}), vanaheim: 'befriend' }; })()")
                T.talk("warden"); q1 = T.ev("window.__hm.S.quests.vh_spring")
                T.ev("(() => { const S = window.__hm.S; S.found.brazier_vh_w = 1; S.found.brazier_vh_spring = 1; })()")
                for x, z in [(-5.6, -5.0), (9.6, 4.0), (-7.0, 6.0)]:
                    tp(x, z); T.ev("window.__hm.verdant.interact()")
                caps = T.ev("window.__hm.S.inv.redcap || 0")
                tp(4.6, -5.0); T.ev("window.__hm.verdant.interact()"); T.frames(2)
                sp = T.ev("({ q: window.__hm.S.quests.vh_spring, f: window.__hm.S.flags.vanaheim_spring, caps: window.__hm.S.inv.redcap || 0 })")
                e0 = T.ev("window.__hm.S.merit.embassy || 0")
                T.talk("warden")
                after = T.ev("({ q: window.__hm.S.quests.vh_spring, rw: window.__hm.S.quests.rotwood, de: (window.__hm.S.merit.embassy || 0) })")
                jarea("vanaheim")
                cave = T.ev("!!(window.__hm.ctx.scene.game.exits || []).find((e) => e.to === 'rotwood')")
                T.step("The Violet Spring (befriend): Burrowmoss starts it; 2 braziers + 3 red caps, E at the spring cleanses it (the violet->cold swap flag); his word pays +60 Realm Favor, starts The Rotwood Hollow and opens the root-cave under the Old Bough",
                       q1 == 1 and caps == 3 and sp["q"] == 2 and sp["f"] == "cleansed" and sp["caps"] == 0 and after["q"] == 3 and after["rw"] == 1 and after["de"] - e0 == 60 and cave,
                       spring=sp, after=after, caps=caps, cave=cave)
                jarea("rotwood", "from_mossbrook")
                rw = T.ev("({ rooms: window.__hm.ctx.scene.game.rooms.length, inn: window.__hm.S.flags.rw_in, enemies: window.__hm.combat.alive().length, frog: !!window.__hm.ctx.effects })")
                door = T.ev("window.__hm.ctx.scene.game.rootdoor")
                tp(door["x"] + 1.5, 2.0); held = T.ev("window.__hm.ctx.player.x") < door["x"]
                T.ev("window.__hm.S.found.rw_lock_1 = 1"); T.frames(3)
                snuffed = not T.ev("window.__hm.S.found.rw_lock_1")
                for bid in door["order"]:
                    T.ev(f"window.__hm.S.found['{bid}'] = 1"); T.frames(3)
                opened = T.ev("!!window.__hm.S.flags.rw_lock")
                T.step("the Rotwood Hollow: 8 rooms (R0-R7), rw_in on entry, foes in the halls; the rune-sealed root door holds you back, a wrong brazier order snuffs them, the pulse order opens it",
                       rw["rooms"] == 8 and rw["inn"] == 1 and rw["enemies"] >= 5 and held and snuffed and opened, rotwood=rw, held=held, snuffed=snuffed, opened=opened)
                gmr = T.ev("(() => { const g = window.__hm.ctx.scene.game; return { mire: g.mire, thorns: g.thorns, hops: window.__hm.hollows.list.length }; })()")
                T.ev("window.__hm.combat.st = 100"); off = gmr["mire"]["path"][0]
                r1 = (gmr["mire"]["rect"][0] + gmr["mire"]["rect"][2]) / 2; tp(r1 - 1.5, -1.4); T.frames(6); m1 = T.ev("({ s: window.__hm.verdant.state(), st: window.__hm.combat.st })")
                tp(off[0], off[1]); T.frames(3); m2 = T.ev("window.__hm.verdant.state()")
                tx = gmr["thorns"]["x"]; tp(tx + 0.4, 2.0); held2 = T.ev("window.__hm.ctx.player.x") < tx
                T.ev(f"window.__hm.S.found['{gmr['thorns']['brazier']}'] = 1"); tp(tx + 0.4, 2.0); passed = T.ev("window.__hm.ctx.player.x") > tx
                T.step("R1 glow-moss path: off the patches you're Mired (stamina drains), on one the moss flares; R2: 4 bounce caps (3 hops + the hidden ledge cap); R4: the thorn wall holds until the gallery brazier is lit",
                       m1["s"]["mired"] and m1["st"] < 100 and not m2["mired"] and m2["mossLit"] >= 1 and gmr["hops"] == 4 and held2 and passed,
                       mire1=m1, mire2={"mired": m2["mired"], "lit": m2["mossLit"]}, hops=gmr["hops"], thorns=[held2, passed])
                bw = T.ev("window.__hm.ctx.scene.game.bower")
                tp(bw["pos"][0] - 1.0, 2.0); T.frames(4)
                T.ev("window.__hm.peace = true")
                st1 = T.ev("window.__hm.verdant.state()")
                T.ev("(() => { const G = window.__hm, e = G.verdant.boss; G.combat.damageEnemy(e, e.D.hp * 0.45, null, 0); })()"); T.frames(3)
                st2 = T.ev("window.__hm.verdant.state()")
                T.ev("(() => { const G = window.__hm, e = G.verdant.boss; G.combat.damageEnemy(e, e.D.hp * 0.35, null, 0); })()"); T.frames(4)
                # the frost-iron spike pulses blue every 4 s (game time): strike it in the same page task that sees the window open (no forced pulse timer)
                T.until("(() => { const G = window.__hm, e = G.verdant.boss; if (!e || !e.spikeOpen) return false; const st = G.verdant.state(), h0 = e.hp; G.combat.damageEnemy(e, 10, null, 0); window.__vhHit = { st, hit: h0 - e.hp }; return true; })()", 60)
                hz = T.ev("window.__vhHit || { st: window.__hm.verdant.state(), hit: -1 }")
                st3, hit = hz["st"], hz["hit"]; st4 = T.ev("window.__hm.verdant.state()")
                rep["shots"]["regent_spike"] = T.shot("regent_spike")
                T.step("the Blight Regent (5.5x) rises in the Bower (quest stage 2): phase 2 under 60%, phase 3 under 25%; in the blue pulse window a hit strikes the frost-iron spike (double damage + stagger)",
                       st1["boss"] and st1["boss"]["scale"] == 5.5 and T.ev("window.__hm.S.quests.rotwood") == 2 and st2["boss"]["phase"] == 2 and st3["boss"]["phase"] == 3
                       and st3["boss"]["spikeOpen"] and hit == 20 and st4["boss"]["spikeHits"] == 1, s1=st1["boss"], s2=st2["boss"], s3=st3["boss"], hit=hit)
                T.ev("window.__hm.combat.damageEnemy(window.__hm.verdant.boss, 99999, null, 0)"); T.frames(4)
                dn = T.ev("({ boss: window.__hm.S.flags.rw_boss, spike: window.__hm.S.inv.blight_spike || 0, sap: !!(window.__hm.ctx.scene.game.exits || []).find((e) => e.to === 'verdant') })")
                jarea("vanaheim"); T.talk("warden")
                rs = T.ev("({ rw: window.__hm.S.quests.rotwood, vd: window.__hm.S.quests.verdant, res: window.__hm.S.flags.vh_resolved, pup: !!((window.__hm.S.pets || {}).mosspup || {}).atDen })")
                T.step("the Regent falls: the frost-iron spike, the sapling stair to the Verdant Heart; Burrowmoss reads the spike: Rotwood done (befriend), the moss-pup goes to the Den, the Verdant Heart opens",
                       dn["boss"] == 1 and dn["spike"] == 1 and dn["sap"] and rs["rw"] == 3 and rs["vd"] == 1 and rs["res"] == "befriend" and rs["pup"], down=dn, resolved=rs)
                jarea("verdant", "from_rotwood")
                vd = T.ev("window.__hm.ctx.scene.game")
                tp(vd["moonwell"]["pos"][0] - 1.0, 2.0); T.frames(4); th = T.ev("window.__hm.verdant.state().thorn")
                tp(vd["glade"]["enter_x"] + 1.0, 2.0); T.frames(4); hj = T.ev("window.__hm.verdant.state().hj")
                T.ev("(() => { const G = window.__hm, e = G.verdant.hj; G.combat.damageEnemy(e, 99999, null, 0); })()"); T.frames(3)
                vq = T.ev("({ q: window.__hm.S.quests.verdant, tine: window.__hm.S.inv.greenheart_tine || 0, tr: (window.__hm.S.trials || {}).hjortur || 0 })")
                T.step("the Verdant Heart: 6 rooms (V0-V5); the Thornmother (2.4x) rises at the Moonwell; Hjortur (6x) holds the guardian trial on the befriend path: he yields, the quest is done, a Greenheart tine",
                       len(vd["rooms"]) == 6 and th and th["scale"] == 2.4 and hj and hj["scale"] == 6 and hj["role"] == "hjortur" and hj["trial"]
                       and vq["q"] == 3 and vq["tine"] == 1 and vq["tr"] == 1, thorn=th, hj=hj, quest=vq)
                T.ev("(() => { const S = window.__hm.S; S.flags.alliance.vanaheim = 'conquer'; delete S.flags.vh_hjortur; S.quests.verdant = 1; })()")
                jarea("verdant", "from_rotwood"); tp(vd["glade"]["enter_x"] + 1.0, 2.0); T.frames(4); hc = T.ev("window.__hm.verdant.state().hj")
                T.step("conquer path: the corrupted Hjortur (6x) fights for real (no trial)", hc and hc["role"] == "hjortur_corrupted" and not hc["trial"], hj=hc)
                T.step("no JS errors (6.4 Vanaheim dungeons)", not errors and not T.ev("window.__hd2d.errors.length"), errors=errors[:5])
                jc.close()
                seg_done("J")
            except Exception as e:  # noqa: BLE001
                rep["pass"] = False
                rep["error"] = f"verdant: {type(e).__name__}: {e}"[:400]
                try:
                    rep["shots"]["failure_J"] = T.shot("failure_J"); rep["state"] = T.S()
                except Exception:  # noqa: BLE001
                    pass
        # ---------------------------------------------------------- K: Stage 6.6 glow-fish orb lanterns (continues cp3)
        if rep["pass"] and "K" in segs:
            seg_mark("K")
            try:
                saved = cp_load(None, T, url, "cp3")["hearthmoor-slot-1-v2"]
                kc = b.new_context(viewport={"width": size[0], "height": size[1]})
                kc.add_init_script(f"if (!sessionStorage.getItem('seeded')) {{ localStorage.clear(); localStorage.setItem('hearthmoor-slot-1-v2', {json.dumps(saved)}); sessionStorage.setItem('seeded', '1'); }}")
                kc.add_init_script(STUB)
                kp = kc.new_page()
                kp.on("pageerror", lambda e: errors.append(f"PAGEERROR {e}"))
                kp.on("console", lambda m: errors.append(f"console.error {m.text}") if m.type == "error" else None)
                T.pg = kp
                kp.goto(url)
                T.wait("window.__hm && window.__hm.ready && window.__hd2d && window.__hd2d.ready && !window.__hd2dGate.loading", 120)
                kp.click("#btnCont"); T.idle(); kp.wait_for_timeout(400)

                def karea(a, spawn="start"):
                    T.ev(f"window.__hm.loadArea('{a}', '{spawn}')"); T.wait(f"window.__hm.area === '{a}' && window.__hm.ctx && !window.__hm.busy", 120); T.idle(); kp.wait_for_timeout(300)

                def ktp(x, z):
                    T.ev(f"(() => {{ const p = window.__hm.ctx.player; p.x = {x}; p.z = {z}; }})()"); T.frames(3)

                def kclock(t):
                    T.ev(f"(() => {{ const G = window.__hm; G.ctx.clock.set({t}); G.S.t = G.ctx.clock.t; }})()"); T.frames(4)
                T.ev("(() => { const G = window.__hm; G.peace = true; G.S.inv.glowfish = 0; G.S.inv.orblamp = 0; G.S.orbs = {}; G.S.fishDay = {}; })()")
                gw = T.ev("(async () => { const m = await import('./game/shop.js'); return { odo: m.SHOPS.hearthmoor.goods, ida: m.SHOPS.harbor.goods, fish: m.GOODS.glowfish.price, orb: m.GOODS.orblamp.price }; })()")
                T.step("6.6 shops: Odo sells empty orbs + glow-fish, Ida sells glow-fish", "orblamp" in gw["odo"] and "glowfish" in gw["odo"] and "glowfish" in gw["ida"] and gw["fish"] > 0 and gw["orb"] > 0, shop=gw)
                karea("hollows"); kclock(0.5); ktp(10.0, -6.2); T.ev("window.__hm.lanterns.interact()")
                f_day = T.ev("window.__hm.S.inv.glowfish || 0")
                kclock(0.9); T.ev("window.__hm.lanterns.interact()"); f1 = T.ev("window.__hm.S.inv.glowfish || 0")
                T.ev("window.__hm.lanterns.interact()"); f2 = T.ev("window.__hm.S.inv.glowfish || 0")
                T.step("glow-fish: none by day, one caught at night, the spot is spent till tomorrow", f_day == 0 and f1 == 1 and f2 == 1, day=f_day, night=[f1, f2])
                T.ev("(() => { const S = window.__hm.S; S.inv.glowfish = 4; S.inv.orblamp = 4; })()")
                for a, xs in (("plaza", [(3.9, 3.5), (5.7, 3.5)]), ("lane", [(2.0, 4.7), (5.2, 5.25)])):
                    karea(a); kclock(0.5)
                    for x, z in xs:
                        ktp(x, z); T.ev("window.__hm.lanterns.interact()")
                    q = T.ev("window.__hm.lanterns.qa()")["spots"]
                    posts = T.ev("window.__hm.ctx.scene.objects.filter((o) => /orb_post/.test(o.glb || '')).length")
                    T.step(f"{a}: both orb lanterns placed on their kit stands, orbs shown, dark by day", posts == 2 and len(q) == 2 and all(s["on"] and s["orb"] and not s["lit"] for s in q), spots=q)
                inv = T.ev("({ f: window.__hm.S.inv.glowfish || 0, o: window.__hm.S.inv.orblamp || 0 })")
                T.step("placing used one orb + one glow-fish each", inv == {"f": 0, "o": 0}, inv=inv)
                kclock(0.92); T.frames(8)
                q = T.ev("window.__hm.lanterns.qa()")["spots"]; z = T.ev("window.__hm.glow.zones().filter((z) => z.src === 'orb').length")
                T.step("night: each orb lights a pool of radiance (light + light zone)", all(s["lit"] for s in q) and z == 2, spots=q, zones=z)
                ktp(3.6, 6.2); T.ev("window.__hm.qaStill = true"); kp.wait_for_timeout(900)
                rep["shots"]["stage6_lanterns"] = T.shot("stage6_lanterns"); T.ev("window.__hm.qaStill = false")
                karea("plaza"); kclock(0.92); T.frames(8)
                T.step("the home lanterns survive an area change and glow at night", all(s["on"] and s["lit"] for s in T.ev("window.__hm.lanterns.qa()")["spots"]))
                ktp(3.9, 3.5); T.ev("window.__hm.lanterns.interact()")
                tb = T.ev("({ on: window.__hm.lanterns.qa().spots[0].on, f: window.__hm.S.inv.glowfish || 0, o: window.__hm.S.inv.orblamp || 0 })")
                T.step("taking a lantern back returns the orb and the fish", not tb["on"] and tb["f"] == 1 and tb["o"] == 1, back=tb)
                T.step("no JS errors (6.6 orb lanterns)", not errors and not T.ev("window.__hd2d.errors.length"), errors=errors[:5])
                kc.close()
                seg_done("K")
            except Exception as e:  # noqa: BLE001
                rep["pass"] = False
                rep["error"] = f"lanterns: {type(e).__name__}: {e}"[:400]
                try:
                    rep["shots"]["failure_K"] = T.shot("failure_K"); rep["state"] = T.S()
                except Exception:  # noqa: BLE001
                    pass
        # ---------------------------------------------------------- L: Stage 6.7 the Forge Quarter (continues cp3)
        if rep["pass"] and "L" in segs:
            seg_mark("L")
            try:
                saved = cp_load(None, T, url, "cp3")["hearthmoor-slot-1-v2"]
                lc = b.new_context(viewport={"width": size[0], "height": size[1]})
                lc.add_init_script(f"if (!sessionStorage.getItem('seeded')) {{ localStorage.clear(); localStorage.setItem('hearthmoor-slot-1-v2', {json.dumps(saved)}); sessionStorage.setItem('seeded', '1'); }}")
                lc.add_init_script(STUB)
                lp = lc.new_page()
                lp.on("pageerror", lambda e: errors.append(f"PAGEERROR {e}"))
                lp.on("console", lambda m: errors.append(f"console.error {m.text}") if m.type == "error" else None)
                T.pg = lp
                lp.goto(url)
                T.wait("window.__hm && window.__hm.ready && window.__hd2d && window.__hd2d.ready && !window.__hd2dGate.loading", 120)
                lp.click("#btnCont"); T.idle(); lp.wait_for_timeout(400)

                def larea(a, spawn="start"):
                    T.ev(f"window.__hm.loadArea('{a}', '{spawn}')"); T.wait(f"window.__hm.area === '{a}' && window.__hm.ctx && !window.__hm.busy", 120); T.idle(); lp.wait_for_timeout(300)
                T.ev("(() => { const G = window.__hm; G.peace = true; G.S.quests.altar = 2; })()")
                larea("ravenhold"); g0 = T.ev("window.__hm.ctx.scene.game.exits.map((e) => e.to)")
                T.ev("window.__hm.S.quests.altar = 3"); larea("ravenhold"); g1 = T.ev("({ ex: window.__hm.ctx.scene.game.exits.map((e) => e.to), sealed: window.__hm.ctx.scene.game.sealed.map((g) => g.id) })")
                T.step("Forge Quarter gate: sealed until the Cold Altar is done, then an exit", "forge" not in g0 and "forge" in g1["ex"] and "forge" not in g1["sealed"], before=g0, after=g1)
                larea("forge", "from_harbor")
                fq = T.ev("(() => { const c = window.__hm.ctx; return { tova: !!c.npc('smith'), orri: !!c.npc('runesmith'), fx: window.__hm.forge.fx.length, lights: window.__hm.forge.lights.length, zones: window.__hm.glow.zones().filter((z) => z.src === 'forge').length, sheet: !!c.actors.sheetOf('smith') }; })()")
                T.step("the forge yard: Tova + Orri, forge fire / pools / embers, red + blue lights, light zones", fq["tova"] and fq["orri"] and fq["sheet"] and fq["fx"] >= 6 and fq["lights"] >= 6 and fq["zones"] >= 4, forge=fq)
                rt = T.ev("""(() => { const G = window.__hm, S = G.S, F = G.forge;
                  const npcs = ['rioter1', 'rioter2', 'rioter3'].filter((id) => G.ctx.npc(id)).length, q0 = S.quests.forge_riot, blocked = F.tova().pages[0];
                  const wrong = F.rioter('rioter1').choice.options[1].pick(G).pages[0], still = !(S.flags.rt_gunnar);
                  [0, 1, 2].forEach((k) => F.rioter('rioter' + (k + 1)).choice.options[k].pick(G));
                  const q1 = S.quests.forge_riot, o = F.orri(); o.then(G);
                  return { npcs, q0, blocked, wrong, still, q1, q2: S.quests.forge_riot, free: !!S.flags.orri_socket }; })()""")
                T.step("Sparks in the Street: 3 rioters, wrong clue reopens, right clues calm them, Orri's tongs story ends it (free socket)",
                       rt["npcs"] == 3 and rt["q0"] == 1 and "crowd" in rt["blocked"] and "change the subject" in rt["wrong"] and rt["still"] and rt["q1"] == 2 and rt["q2"] == 3 and rt["free"], riot=rt)
                ft = T.ev("""(() => { const G = window.__hm, S = G.S, F = G.forge, LO = G.LO;
                  F.tova().then(G); const q1 = S.quests.temper;
                  S.bag = S.bag || []; S.bag.unshift(LO.makeItem(1, 1, 'armor')); const i0 = S.inv.ironbit || 0;
                  const sc = F.scrapMenu().choice.options[0].pick(G).pages[0], iron = (S.inv.ironbit || 0) - i0;
                  const p = G.ctx.player; p.x = -5.6; p.z = -7.6; F.interact(); F.interact(); F.interact();
                  const w = LO.makeItem(1, 2, 'weapon'); S.gear.weapon = w; const g0 = S.gold;
                  const t = F.temperMenu().choice.options[0].pick(G).pages[0];
                  const q2 = S.quests.temper; F.orri().then(G);
                  return { q1, sc, iron, bellows: !!S.flags.tp_bellows, up: w.up, free: S.gold === g0, t, q2, q3: S.quests.temper, rs: S.inv.runestone || 0 }; })()""")
                T.step("The First Temper: offer, scrap at the forge (+2 iron), 3 bellows pumps, free +1, Orri's turn-in (rune-stone)",
                       ft["q1"] == 1 and ft["iron"] == 2 and ft["bellows"] and ft["up"] == 1 and ft["free"] and "first temper" in ft["t"] and ft["q2"] == 2 and ft["q3"] == 3 and ft["rs"] >= 1, temper=ft)
                tv = T.ev("""(async () => { const G = window.__hm, S = G.S, LO = G.LO;
                  S.gold = 5000; S.inv.ironbit = 100; S.inv.coldsteel = 30; S.gems = { ...(S.gems || {}), frost_core: 2, golem_core: 2, rift_shard: 1 };
                  const w = LO.makeItem(1, 4, 'weapon'); S.gear.weapon = w; const base = w.mods.meleeMul;
                  const lines = []; for (let i = 0; i < 10; i++) lines.push(G.forge.doTemper('weapon', () => 0).pages[0]);
                  const cap = G.forge.doTemper('weapon', () => 0).pages[0];
                  const m = LO.gearMods({ gear: { weapon: w } }, { guardMul: 1 });
                  const a = LO.makeItem(1, 2, 'armor'); a.up = 5; S.gear.armor = a; const g0 = S.gold, i0 = S.inv.ironbit;
                  const fail = G.forge.doTemper('armor', () => 0.99).pages[0];
                  return { up: w.up, last: lines[9], cap, k: m.meleeMul / base, aUp: a.up, heat: a.heat, gold: S.gold === g0, iron: i0 - S.inv.ironbit, fail, desc: LO.describe(w) }; })()""")
                T.step("Tova: +1..+10 on a Legendary (7% per +), capped at +10, a failed +6 keeps gold, eats iron, adds heat",
                       tv["up"] == 10 and abs(tv["k"] - 1.7) < 0.01 and "Hearthforged" in tv["last"] and "as far as" in tv["cap"] and tv["aUp"] == 5 and tv["heat"] == 1 and tv["gold"] and tv["iron"] == 6 and "+10 tempered" in tv["desc"], tova=tv)
                rr = T.ev("""(() => { const G = window.__hm, S = G.S; S.inv.runestone = 1; const w = S.gear.weapon, k0 = Object.keys(w.mods);
                  const e = G.forge.doReroll('weapon', null, () => 0.5); const kept = e.choice.options[0].pick(G);
                  const again = G.forge.doReroll('weapon').pages[0];
                  return { rr: w.rr, k0, k1: Object.keys(w.mods), kept: kept.pages[0], again, opts: G.forge.tova().choice.options.length }; })()""")
                T.step("Orri: a rune-stone rerolls one stat (keep new), no stone = no reroll; Tova offers 3 slots + shop + not yet",
                       rr["rr"] == 1 and len(rr["k1"]) == len(rr["k0"]) and set(rr["k1"]) != set(rr["k0"]) and "stone likes you" in rr["kept"] and "No stone" in rr["again"] and rr["opts"] == 5, orri=rr)
                sk = T.ev("""(() => { const G = window.__hm, S = G.S, F = G.forge, LO = G.LO;
                  S.flags.orri_socket = 1; const w = S.gear.weapon; w.gems = [null, null]; const n0 = w.gems.length;
                  const p1 = F.orri().choice.options[2].pick(G).choice.options[0].pick(G).pages[0], n1 = w.gems.length;
                  const cap = F.doPunch('weapon').pages[0];
                  S.gear.trinket = LO.makeItem(1, 0, 'trinket'); const com = F.doPunch('trinket').pages[0];
                  S.inv.ironbit = 4; S.gems.frost_core = 1; const st0 = S.inv.coldsteel || 0; F.tova().choice.options[1].pick(G); const st = (S.inv.coldsteel || 0) - st0;
                  S.inv.runestone = 2; const out = Object.keys(w.mods)[0], rr0 = w.rr || 0;
                  const e = F.orri().choice.options[1].pick(G).choice.options[0].pick(G).choice.options[0].pick(G); e.choice.options[0].pick(G);
                  const picked = !(out in w.mods) && (S.inv.runestone || 0) === 0 && w.rr === rr0 + 1;
                  const cv = LO.iconCanvas('weapon', 4, 1, w.gems, 10), px = cv.getContext('2d').getImageData(0, 1, 1, 1).data;
                  const s0 = F.sparks || 0; G.ctx.player.act = { name: 'attack', t: 0 }; F.update(0.016); G.ctx.player.act = null; F.update(0.016);
                  return { n0, n1, p1, cap, com, st, picked, icon: [px[0], px[1], px[2]], sparks: (F.sparks || 0) - s0 }; })()""")
                T.step("Orri sockets (free first punch to 3, cap, no Commons), smelt 4 iron + frost core -> 2 cold-steel, pick-your-stat reroll (2 stones), +10 icon mark + cold-blue swing sparks",
                       sk["n0"] == 2 and sk["n1"] == 3 and "socket" in sk["p1"] and "colander" in sk["cap"] and "Commons" in sk["com"] and sk["st"] == 2 and sk["picked"] and sk["icon"] == [42, 180, 255] and sk["sparks"] >= 5, sockets=sk)
                T.ev("(() => { const G = window.__hm, p = G.ctx.player; G.ctx.clock.set(0.95); G.S.t = G.ctx.clock.t; p.x = -2.4; p.z = -5.4; })()"); T.frames(8)
                T.ev("window.__hm.qaStill = true"); lp.wait_for_timeout(900)
                rep["shots"]["stage6_forge"] = T.shot("stage6_forge"); T.ev("window.__hm.qaStill = false")
                T.step("no JS errors (6.7 Forge Quarter)", not errors and not T.ev("window.__hd2d.errors.length"), errors=errors[:5])
                lc.close()
                seg_done("L")
            except Exception as e:  # noqa: BLE001
                rep["pass"] = False
                rep["error"] = f"forge: {type(e).__name__}: {e}"[:400]
                try:
                    rep["shots"]["failure_L"] = T.shot("failure_L"); rep["state"] = T.S()
                except Exception:  # noqa: BLE001
                    pass
        # ---------------------------------------------------------- M: Stage 6.8 the Glowfrog Still (continues cp3)
        if rep["pass"] and "M" in segs:
            seg_mark("M")
            try:
                saved = cp_load(None, T, url, "cp3")["hearthmoor-slot-1-v2"]
                mc = b.new_context(viewport={"width": size[0], "height": size[1]})
                mc.add_init_script(f"if (!sessionStorage.getItem('seeded')) {{ localStorage.clear(); localStorage.setItem('hearthmoor-slot-1-v2', {json.dumps(saved)}); sessionStorage.setItem('seeded', '1'); }}")
                mc.add_init_script(STUB)
                mp = mc.new_page()
                mp.on("pageerror", lambda e: errors.append(f"PAGEERROR {e}"))
                mp.on("console", lambda m: errors.append(f"console.error {m.text}") if m.type == "error" else None)
                T.pg = mp
                mp.goto(url)
                T.wait("window.__hm && window.__hm.ready && window.__hd2d && window.__hd2d.ready && !window.__hd2dGate.loading", 120)
                mp.click("#btnCont"); T.idle(); mp.wait_for_timeout(400)

                def marea(a, spawn="start"):
                    T.ev(f"window.__hm.loadArea('{a}', '{spawn}')"); T.wait(f"window.__hm.area === '{a}' && window.__hm.ctx && !window.__hm.busy", 120); T.idle(); mp.wait_for_timeout(300)
                T.ev("(() => { const G = window.__hm, S = G.S; G.peace = true; S.quests.altar = 3; S.quests.forge_riot = 3; delete S.quests.cauldron; S.recipes = {}; S.brew = null; delete S.dew; const F = (S.flags = S.flags || {}); delete F.cc_bloop; delete F.cc_coal; delete F.cc_vent; delete S.stillStock; })()")
                marea("forge", "from_harbor")
                cold = T.ev("(() => { const G = window.__hm, c = G.ctx; return { bryony: !!c.npc('alchemist'), fx: G.alchemy.fx.length, zone: G.glow.zones().some((z) => z.src === 'still'), lit: G.alchemy.qa().lit, cauldron: c.scene.objects.some((o) => /cauldron_blue/.test(o.glb || '')) }; })()")
                T.step("the Still starts cold after the riot (Bryony + kit cauldron, no blue fx / zone until the vent is lit)", cold["bryony"] and cold["fx"] == 0 and not cold["zone"] and not cold["lit"] and cold["cauldron"], still=cold)
                cc = T.ev("""(() => { const G = window.__hm, S = G.S, A = G.alchemy, F = (S.flags = S.flags || {}), p = G.ctx.player;
                  A.bryony().then(G); const q1 = S.quests.cauldron; const nb = G.ctx.npc('bloop'), tank = nb ? [nb.x, nb.z] : null;
                  p.x = -1.8; p.z = -8.0; A.interact(); const bloop = !!F.cc_bloop; G.dropDialogue && G.dropDialogue(); A.syncBloop(); const np = G.ctx.npc('bloop'), pad = np ? [np.x, np.z] : null;
                  p.x = -6.0; p.z = -3.4; A.interact(); const coal = !!F.cc_coal;
                  A.spellAt(-6.0, -3.4); const vent = !!F.cc_vent, fx = A.fx.length, zone = G.glow.zones().some((z) => z.src === 'still');
                  Object.assign(S.inv, { redcap: 2, moonpetal: 3 }); A.bryony().then(G);
                  const q2 = S.quests.cauldron, moon = !!S.recipes.moonmilk, dew = S.inv.dewdrop || 0, vials = S.inv.vial || 0, tea = S.inv.tea || 0;
                  return { q1, tank, pad, bloop, coal, vent, fx, zone, q2, moon, dew, vials, tea, gold: S.gold || 0 }; })()""")
                T.step("Cold Cauldron: offer → Bloop (own sprite) sits in the quench tank → find him → clear coal → cast lights vent (blue fx) → turn-in teaches Moonmilk + dew/vials/tea",
                       cc["q1"] == 1 and cc["tank"] == [-1.8, -7.3] and cc["pad"] == [-9.2, -2.4] and cc["bloop"] and cc["coal"] and cc["vent"] and cc["fx"] == 3 and cc["zone"] and cc["q2"] == 2 and cc["moon"] and cc["dew"] == 1 and cc["vials"] == 3 and cc["tea"] >= 1, cc=cc)
                br = T.ev("""(() => { const G = window.__hm, S = G.S, A = G.alchemy;
                  Object.assign(S.inv, { redcap: 3, moonpetal: 4, tea: 1, coldpetal: 1, glowbell: 1, glowcap: 1, springwater: 0, loaf: 1, dewdrop: 1 });
                  const p = G.ctx.player; p.x = -9.2; p.z = -1.4; delete S.dew; A.interact(); const dew1 = S.inv.dewdrop || 0; A.interact(); const dew2 = S.inv.dewdrop || 0;
                  A.pot.length = 0; A.pot.push('redcap', 'moonpetal'); const fz = A.stir(); const hinted = Object.keys(S.hints || {}).length, keptCap = S.inv.redcap;
                  const g0 = S.gold || 0; const g = A.stir(['redcap', 'dewdrop']).pages[0], gc = S.inv.brew_glowcap || 0, q3 = S.quests.cauldron, gold = (S.gold || 0) - g0;
                  const r0 = Object.keys(S.recipes).sort();
                  const e = A.stir(['glowcap', 'redcap']); const ec = S.inv.brew_ember || 0;
                  S.inv.dewdrop = 1; const sec0 = !!(S.found || {}).brew_breadbroth; A.stir(['loaf', 'moonpetal', 'dewdrop']);
                  const menu = A.bryony().choice.options.length;
                  // 3 redcap / day at the Still
                  const shop = G.shopUI; S.gold = (S.gold || 0) + 50; shop.show('still');
                  let bought = 0; for (let i = 0; i < 5; i++) { const rows = shop.rows(), r = rows.find((x) => x.id === 'redcap'); if (!r || r.cant) break; shop.i = rows.indexOf(r); if (shop.act()) bought++; }
                  const sold = shop.rows().find((x) => x.id === 'redcap'); shop.close();
                  return { r0, dew1, dew2, fz: fz.pages[0], hinted, keptCap, g, gc, q3, gold, ember: ec, newEmber: !!S.recipes.ember, secret: !sec0 && !!S.found.brew_breadbroth, menu, bought, soldOut: !!(sold && sold.cant) }; })()""")
                T.step("brewing: Glowcap finishes Cold Cauldron (+30g), Bloop dew 1/day, miss fizzles, Glowcap x2, Ember + bread-broth secret; Bryony sells 3 redcaps/day then sold out",
                       br["r0"] == ["glowcap", "moonmilk"] and br["q3"] == 3 and br["gold"] == 30 and br["dew1"] == 2 and br["dew2"] == 2 and "fizzles" in br["fz"] and br["hinted"] == 1 and br["gc"] == 2 and br["ember"] == 1 and br["newEmber"] and br["secret"] and br["menu"] == 4 and br["bought"] == 3 and br["soldOut"], brew=br)
                dk = T.ev("""(() => { const G = window.__hm, S = G.S, PR = G.PR;
                  const m0 = PR.mods(S).meleeMul; G.drinkBrew('ember'); const m1 = PR.mods(S).meleeMul, b1 = S.brew && S.brew.id;
                  G.alchemy.update(61); const m2 = PR.mods(S).meleeMul;
                  S.hp = 10; G.drinkBrew('glowcap'); const hp = S.hp;
                  document.querySelector('[data-item="brew_glowcap"]') && document.querySelector('[data-item="brew_glowcap"]').click(); const tap = S.inv.brew_glowcap || 0;
                  return { up: +(m1 - m0).toFixed(3), b1, off: +(m2 - m0).toFixed(3), hp, tap, brew: S.brew }; })()""")
                T.step("drinking: Ember Cap +15% melee for 60 s then off, Glowcap heals 120, tapping a potion in the bag drinks it",
                       dk["up"] == 0.15 and dk["b1"] == "ember" and dk["off"] == 0 and dk["hp"] >= 120 and dk["tap"] == 0 and dk["brew"] is None, drink=dk)
                hv = T.ev("""(async () => { const m = await import('./game/garden.js'); const s = await import('./game/shop.js');
                  return { herbs: Object.values(m.PLANTS).map((p) => p.herb), still: s.SHOPS.still.goods }; })()""")
                T.step("garden blooms give herbs (cold-fire petal, glowbell, glow-cap); Bryony sells dew, vials, red toadstools", hv["herbs"] == ["coldpetal", "glowbell", "glowcap"] and hv["still"] == ["dewdrop", "vial", "redcap"], herbs=hv)
                T.ev("(() => { const G = window.__hm, p = G.ctx.player; G.ctx.clock.set(0.95); G.S.t = G.ctx.clock.t; p.x = -5.0; p.z = -2.2; })()"); T.frames(8)
                T.ev("window.__hm.qaStill = true"); mp.wait_for_timeout(900)
                rep["shots"]["stage6_alchemy"] = T.shot("stage6_alchemy"); T.ev("window.__hm.qaStill = false")
                marea("hollows"); sw = T.ev("""(() => { const G = window.__hm, S = G.S, sp = G.ctx.scene.game.spring.pos, p = G.ctx.player; S.inv.vial = 1; delete S.inv.springwater; p.x = sp[0]; p.z = sp[1] + 1.0; G.alchemy.interact(); return { w: S.inv.springwater || 0, v: S.inv.vial || 0 }; })()""")
                T.step("a vial fills with spring water at the Hollows spring", sw == {"w": 1, "v": 0}, spring=sw)
                T.step("no JS errors (6.8 Glowfrog Still)", not errors and not T.ev("window.__hd2d.errors.length"), errors=errors[:5])
                mc.close()
                seg_done("M")
            except Exception as e:  # noqa: BLE001
                rep["pass"] = False
                rep["error"] = f"still: {type(e).__name__}: {e}"[:400]
                try:
                    rep["shots"]["failure_M"] = T.shot("failure_M"); rep["state"] = T.S()
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
    rep["retries"] = Smoke.retries; rep["commit"] = COMMIT
    log(f"smoke: {'PASS' if rep['pass'] else 'FAIL'} {sum(s['pass'] for s in T.steps)}/{len(T.steps)} steps in {rep['seconds']} s, retries {Smoke.retries} @ {COMMIT}" + (f"  ({rep.get('error')})" if not rep["pass"] else ""))
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
    print(header(f"--jobs {n} segments {segs}"), flush=True)
    print(f"smoke --jobs {n}: shards {plan} (segment seconds {seg_seconds()})", flush=True)
    procs = []
    for i, p in enumerate(plan):
        so = out / f"shard{i + 1}"
        lf = open(out / f"shard{i + 1}.log", "w")
        pr = subprocess.Popen([sys.executable, "-u", str(Path(__file__).resolve()), "--segments", p, "--out", str(so), "--simscale", str(simscale)] + ([] if Smoke.RETRY else ["--no-retry"]),
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
    merged["retries"] = sum(r.get("retries", 0) for r in reps); merged["commit"] = COMMIT; (out / "smoke.json").write_text(json.dumps(merged, indent=1))
    print(f"smoke: {'PASS' if ok else 'FAIL'} {sum(s['pass'] for s in steps)}/{len(steps)} steps in {wall} s, retries {merged['retries']} @ {COMMIT} (sharded, {len(plan)} workers, segments {''.join(sorted(segs))})", flush=True)
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
    ap.add_argument("--no-retry", action="store_true", help="a failing step fails at once (no one-shot retry)")
    ap.add_argument("--no-preflight", action="store_true", help="skip tests/preflight.sh")
    a = ap.parse_args()
    Smoke.RETRY = not a.no_retry
    if not a.list:
        preflight(sys.argv)
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
