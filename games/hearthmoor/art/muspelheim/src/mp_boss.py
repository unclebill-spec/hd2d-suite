"""Vharzul the Ember Throne (boss, 8x): horned overlord demon in black-iron plate (the ONLY plate in Muspelheim), a crown of fire, wings of
ember-smoke, red-lit eyes, a broken-throne greatsword. Palette only (the glow is fx + light). Native 144x256 frame, boss_sheet layout."""
import math
from mp_common import R, hsh
from mp_giant import giant
from mp_npcs import combine

FRAME = (144, 256)
IR = ("stone_lo", "shadow", "ink")


def flames(cv, cx, cy, n, spread, hgt, k):
    for j in range(n):
        x = cx + (j - (n - 1) / 2) * spread
        h = hgt * (.7 + .3 * hsh("fl", j, k))
        for y in range(int(h)):
            t = y / h
            w = max(0, 2.2 * (1 - t) * (1 + .3 * math.sin(k + j)))
            for dx in range(-int(w), int(w) + 1):
                cv.set(x + dx + math.sin(y * .5 + k + j) * 1.2, cy - y, "white" if (abs(dx) < w * .4 and t < .5) else "flower_gold" if t < .6 else "lamp" if t < .85 else "roof_hi")


def plate(P3):
    def f(cv, c):
        CX, sh, hip, hw, Ht, k, face, beltY, G = c["CX"], c["sh"], c["hip"], c["hw"], c["Ht"], c["k"], c["face"], c["beltY"], c["G"]
        side, back = face == "left", face == "up"
        hl = ((P3 and 1) or 0)
        def shd(u, v=0):
            return IR[0] if u < -.55 else IR[2] if u > .55 else IR[1]
        # greaves + knee cops + sabaton cover (front/back: two legs; side: one column)
        legs = [CX] if side else [CX - hw * .52, CX + hw * .52]
        for lx in legs:
            lw = c["legw"] * (.55 if not side else .6)
            for y in range(int(hip + Ht * .12), int(G - Ht * .02)):
                for x in range(int(lx - lw), int(lx + lw) + 1):
                    u = (x - lx) / lw
                    cv.set(x, y, shd(u))
            ky = hip + Ht * .17
            cv.ell(lx, ky, lw * 1.1, Ht * .035, lambda u, v: "stone" if v < -.2 else "stone_lo")
            for y in range(int(hip + Ht * .26), int(G - Ht * .06), int(max(4, Ht * .06))):
                cv.rect(lx - lw, y, lx + lw, y, "lamp" if y % 2 == 0 else "stone")      # cold fire leaks at the lame seams
        # cuirass
        x0, x1 = CX - hw * 1.02, CX + hw * 1.02
        top, bot = sh + 2, beltY - 1
        for y in range(int(top), int(bot) + 1):
            t = (y - top) / max(1, bot - top)
            ins = (0 if t < .6 else (t - .6) * hw * .25)       # waist taper
            for x in range(int(x0 + ins), int(x1 - ins) + 1):
                u = (x - CX) / hw
                col = shd(u)
                if abs(u) < .06 and not side:
                    col = "shadow"                                 # centre seam
                cv.set(x, y, col)
        step = int(max(5, Ht * .07))
        for y in range(int(top) + step, int(bot), step):
            cv.rect(x0 + 1, y, x1 - 1, y, "stone" if y % 2 == 0 else "stone_lo")
            for x in range(int(x0 + 3), int(x1 - 2), int(max(4, Ht * .05))):
                cv.set(x, y - 1, "lamp")                            # leaking glow under each plate lip
        if not back and not side:
            cx_, cy_ = CX, top + (bot - top) * .38
            r = Ht * .06
            cv.poly([(cx_, cy_ - r), (cx_ + r, cy_), (cx_, cy_ + r), (cx_ - r, cy_)], lambda x, y: "white" if abs(x - cx_) + abs(y - cy_) < r * .45 else "flower_gold")
            for sd in (-1, 1):
                for j in range(3):
                    cv.set(cx_ + sd * (hw * .6), top + 4 + j * 3, "stone")
        # fauld (skirt of lames) over the tunic hem
        for j in range(3):
            y0 = beltY + 1 + j * Ht * .045
            w_ = hw * (1.05 + j * .12)
            for y in range(int(y0), int(y0 + Ht * .05)):
                for x in range(int(CX - w_), int(CX + w_) + 1):
                    cv.set(x, y, shd((x - CX) / w_) if y > y0 else "stone_hi")
            for x in range(int(CX - w_) + 2, int(CX + w_) - 1, int(max(5, Ht * .06))):
                cv.set(x, y0 + Ht * .05, "lamp")
        # pauldrons + spikes
        for sd in ((-1, 1) if not side else (0,)):
            px_ = CX + sd * (hw * 1.0)
            for j in range(3):
                cv.ell(px_, sh + 2 + j * Ht * .04, Ht * (.115 - j * .008) * (1 if not side else .8), Ht * .06, lambda u, v: "stone" if (u < -.3 and v < 0) else "stone_lo" if u < .5 else "shadow")
            sp = px_ + sd * Ht * .06 if sd else px_ - Ht * .02
            cv.poly([(sp - 3, sh - 2), (sp + 3, sh - 2), (sp + (sd or -1) * 2, sh - Ht * .12)], lambda x, y: "stone" if x < sp else "stone_lo")
            cv.set(px_ + (sd or 0), sh + 4, "lamp")
        # gorget
        cv.ell(CX, sh, hw * .55, Ht * .03, lambda u, v: "stone" if v < 0 else "stone_lo")
        # gauntlets
        for hx, hy in c["hands"]:
            cv.ell(hx, hy, Ht * .05, Ht * .06, lambda u, v: "stone" if (u < -.3 and v < 0) else "stone_lo" if u < .5 else "shadow")
            cv.rect(hx - Ht * .045, hy - Ht * .055, hx + Ht * .045, hy - Ht * .05, "lamp")
        # cold fire licking from the shoulder joints (phase 3: a lot more)
        if P3 and not back:
            flames(cv, CX - hw * 1.08, sh - 2, 3, 3, Ht * .10, c["i"] * 1.3)
            flames(cv, CX + hw * 1.08, sh - 2, 3, 3, Ht * .10, c["i"] * 1.3 + 2)
    return f


def wings(P3):
    """wings of ember-smoke: dithered smoke shapes behind the shoulders (only drawn where nothing else is), a few embers in them"""
    def f(cv, c):
        CX, sh, Ht, hw, face = c["CX"], c["sh"], c["Ht"], c["hw"], c["face"]
        side, back = face == "left", face == "up"
        i = c["i"]
        for sd in ((-1, 1) if not side else (1,)):
            x0 = CX + sd * hw * (1.0 if not side else .3)
            span = Ht * (.10 if not side else .08) * (1 + (.12 if P3 else 0))
            for t in range(0, 60):
                tt = t / 59
                # a swept-back wing: upper edge arcs up and out, lower edge sweeps down in feathered tongues
                ux = x0 + sd * span * tt
                uy = sh - Ht * .12 - math.sin(tt * math.pi * .7) * Ht * .27 + math.sin(i * .9 + tt * 6) * 1.5
                ly = sh + Ht * .12 + tt * Ht * .30 + math.sin(i * .9 + tt * 5) * 2
                n = int(ly - uy)
                for j in range(0, max(1, n)):
                    y = uy + j
                    q = j / max(1, n)
                    if (int(ux) + int(y) + (i if q > .5 else 0)) % 2 == 0 or q < .12:
                        if cv.get(ux, y) is None:
                            cv.set(ux, y, "stone_lo" if q < .6 else "shadow")
                if t % 7 == 3 and (t + i) % 2 == 0:
                    ey = uy + (ly - uy) * (.3 + .4 * hsh("e", t, sd))
                    if cv.get(ux, ey) is None:
                        cv.set(ux, ey, "lamp")
    return f


def sword(cv, c):
    """the broken-throne greatsword: dark iron blade with a lava-lit edge; raised on the attack"""
    hx, hy = c["hand"]
    Ht, at, side = c["Ht"], c["at"], c["side"]
    x0, y0 = hx + (3 if not side else -1), hy + 2
    ln = Ht * (.5 + .12 * at)
    x1, y1 = x0 + (Ht * .03 if not side else -Ht * .12) * at, y0 - ln
    n = int(ln)
    for j in range(n):
        t = j / n
        x = x0 + (x1 - x0) * t; y = y0 + (y1 - y0) * t
        w = Ht * .035 * (1 - .15 * t) if j > 6 else Ht * .012
        for dx in range(-int(w), int(w) + 1):
            cv.set(x + dx, y, "stone_hi" if dx < -w * .4 else "stone_lo" if dx > w * .4 else "stone")
        cv.set(x - int(w) - 1, y, "lamp" if j % 3 else "flower_gold")
    cv.rect(x0 - Ht * .05, y0 - 5, x0 + Ht * .05, y0 - 3, "shadow")                    # crossguard
    cv.poly([(x1 - 3, y1 + 3), (x1 + 3, y1 + 3), (x1 + 1, y1 - 5)], "stone")           # the broken tip


def crown(P3):
    def f(cv, c):
        hcx, hcy, hh, hhw, k = c["hcx"], c["hcy"], c["hh"], c["hhw"], c["k"]
        back, side = c["back"], c["side"]
        Ht = c["Ht"]
        # black-iron band, two great horns, and the crown of fire
        y = hcy - hh * .62
        cv.rect(hcx - hhw * .95, y, hcx + hhw * .95, y + max(1, Ht * .02), "stone_lo")
        cv.rect(hcx - hhw * .95, y - 1, hcx + hhw * .95, y - 1, "stone_hi")
        for sd in ((-1, 1) if not side else (-1,)):
            bx = hcx + sd * hhw * (.85 if not side else .2)
            pts = [(bx, y), (bx + sd * Ht * .05, y - Ht * .05), (bx + sd * Ht * .09, y - Ht * .11), (bx + sd * Ht * .08, y - Ht * .17), (bx + sd * Ht * .04, y - Ht * .21)]
            for (a, b) in zip(pts[:-1], pts[1:]):
                cv.seg(a[0], a[1], b[0], b[1], Ht * .045, Ht * .03, ("plaster_lo", "stone_hi", "stone"))
        fl = (7 if P3 else 5)
        for j in range(fl):
            x = hcx + (j - (fl - 1) / 2) * hhw * (.28 if P3 else .36)
            flames(cv, x, y, 1, 0, Ht * (.13 if j % 2 else .19) * (1.3 if P3 else 1.0), c["i"] * 1.2 + j)
        if not back:
            ey = hcy + hh * .05
            exs = [hcx - hhw * .5] if side else [hcx - hhw * .42, hcx + hhw * .42]
            for ex in exs:
                cv.rect(ex - 2, ey - 1, ex + 2, ey + 1, "roof_hi"); cv.rect(ex - 1, ey - 1, ex + 1, ey, "lamp")
    return f


def Ht_(c, f):
    return max(1, c["Ht"] * f)


def vharzul(P3):
    P = dict(skin="copper", hair=None, bald=True, hairstyle="none", tunic="obsidian", trousers="obsidian", belt=("roof_lo", "shadow"), buckle="lamp",
             width=.98, head=1.02, plate=plate(P3), extra=combine(wings(P3), sword, crown(P3)), raise_=1.25, brow="stone_lo",
             trim="roof", cheeks=False, hunch=.08, legs_w=1.15, arms_w=1.2, hem=.08)
    d = giant(P, 192)
    d.die_mode = "sink"
    d.sink_cols = ("lamp", "stone_hi", "stone_lo", "shadow")
    return d


def roles():
    return {
        "vharzul": dict(draw=vharzul(False), scale=8.0, boss=True, enemy=True, kind="enemy", anims=("idle", "walk", "attack", "die"),
                        desc="Vharzul the Ember Throne (boss, 8x; the ONLY plate in Muspelheim): horned overlord demon in black-iron plate, crown of fire, wings of ember-smoke, red-lit eyes, broken-throne greatsword. Phases 1-2. die = collapses into an ash heap with a last ember.",
                        light={"color": "#ff7a1a", "intensity": 1.3, "range": 10.0}, stats_hint={"tier": "boss", "height_x_player": 8.0, "dungeon": "The Ember Caldera", "plate": True, "element": "fire"}),
        "vharzul_p3": dict(draw=vharzul(True), scale=8.0, boss=True, enemy=True, kind="enemy", anims=("idle", "walk", "attack", "die"),
                           desc="Vharzul phase 3 (25%): the crown flares into a tall blaze, the three Warden's lamps relight, wings stream embers.",
                           light={"color": "#ffb066", "intensity": 1.7, "range": 12.0}, stats_hint={"tier": "boss", "height_x_player": 8.0}),
    }
