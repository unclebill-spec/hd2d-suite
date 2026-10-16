"""Hrimgard the Unthawed (boss, 7x): ancient giant king in rune-iron plate (the ONLY plate in Jotunheim), an ice crown, cold-fire leaking
from every joint (palette sky / white here; neon-blue comes from the hrimgard fx + light). Native 144x224 frame, boss_sheet layout."""
import math
from jt_common import R, hsh
from jt_giant import giant

FRAME = (144, 224)
IR = ("stone_lo", "shadow", "ink")


def flames(cv, cx, cy, n, spread, hgt, k):
    for j in range(n):
        x = cx + (j - (n - 1) / 2) * spread
        h = hgt * (.7 + .3 * hsh("fl", j, k))
        for y in range(int(h)):
            t = y / h
            w = max(0, 2.2 * (1 - t) * (1 + .3 * math.sin(k + j)))
            for dx in range(-int(w), int(w) + 1):
                cv.set(x + dx + math.sin(y * .5 + k + j) * 1.2, cy - y, "white" if (abs(dx) < w * .4 and t < .5) else "sky" if t < .8 else "flower_blue")


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
                cv.rect(lx - lw, y, lx + lw, y, "ink")                                  # dark lame seam (a bright full-width line reads as a grid at 7x)
                cv.set(lx - lw * .55, y, "sky")                                         # a single cold-fire glint leaks from the seam
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
            cv.rect(x0 + 1, y, x1 - 1, y, "ink")                   # dark plate lip (a light full-width line reads as a white grid at 7x)
            for x in range(int(x0 + 3), int(x1 - 2), int(max(8, Ht * .10))):
                cv.set(x, y - 1, "sky")                            # leaking glow under the plate lip, sparse
        if not back and not side:
            cx_, cy_ = CX, top + (bot - top) * .38
            r = Ht * .06
            cv.poly([(cx_, cy_ - r), (cx_ + r, cy_), (cx_, cy_ + r), (cx_ - r, cy_)], lambda x, y: "white" if abs(x - cx_) + abs(y - cy_) < r * .45 else "sky")
            for sd in (-1, 1):
                for j in range(3):
                    cv.set(cx_ + sd * (hw * .6), top + 4 + j * 3, "stone")
        # fauld (skirt of lames) over the tunic hem
        for j in range(3):
            y0 = beltY + 1 + j * Ht * .045
            w_ = hw * (1.05 + j * .12)
            for y in range(int(y0), int(y0 + Ht * .05)):
                for x in range(int(CX - w_), int(CX + w_) + 1):
                    cv.set(x, y, shd((x - CX) / w_) if y > y0 else "stone_lo")
            for x in range(int(CX - w_) + 2, int(CX + w_) - 1, int(max(5, Ht * .06))):
                cv.set(x, y0 + Ht * .05, "sky")
        # pauldrons + spikes
        for sd in ((-1, 1) if not side else (0,)):
            px_ = CX + sd * (hw * 1.0)
            for j in range(3):
                cv.ell(px_, sh + 2 + j * Ht * .04, Ht * (.115 - j * .008) * (1 if not side else .8), Ht * .06, lambda u, v: "stone" if (u < -.3 and v < 0) else "stone_lo" if u < .5 else "shadow")
            sp = px_ + sd * Ht * .06 if sd else px_ - Ht * .02
            cv.poly([(sp - 3, sh - 2), (sp + 3, sh - 2), (sp + (sd or -1) * 2, sh - Ht * .12)], lambda x, y: "stone" if x < sp else "stone_lo")
            cv.set(px_ + (sd or 0), sh + 4, "sky")
        # gorget
        cv.ell(CX, sh, hw * .55, Ht * .03, lambda u, v: "stone" if v < 0 else "stone_lo")
        # gauntlets
        for hx, hy in c["hands"]:
            cv.ell(hx, hy, Ht * .08, Ht * .085, lambda u, v: "stone" if (u < -.3 and v < 0) else "stone_lo" if u < .5 else "shadow")
            cv.rect(hx - Ht * .045, hy - Ht * .055, hx + Ht * .045, hy - Ht * .05, "sky")
        # cold fire licking from the shoulder joints (phase 3: a lot more)
        if P3 and not back:
            flames(cv, CX - hw * 1.08, sh - 2, 3, 3, Ht * .10, c["i"] * 1.3)
            flames(cv, CX + hw * 1.08, sh - 2, 3, 3, Ht * .10, c["i"] * 1.3 + 2)
    return f


def crown(P3):
    def f(cv, c):
        hcx, hcy, hh, hhw, k = c["hcx"], c["hcy"], c["hh"], c["hhw"], c["k"]
        back, side = c["back"], c["side"]
        # iron band + ice crown spikes
        y = hcy - hh * .62
        cv.rect(hcx - hhw * .95, y, hcx + hhw * .95, y + Ht_(c, .02), "stone_lo")
        cv.rect(hcx - hhw * .95, y - 1, hcx + hhw * .95, y - 1, "stone_hi")
        for j, dx in enumerate((-.8, -.45, -.1, .25, .6, .92)):
            x = hcx + dx * hhw
            hgt = c["Ht"] * (.075 if j % 2 else .105)
            cv.poly([(x - 3, y), (x + 3, y), (x + .5, y - hgt)], lambda a, b, x=x: "white" if a <= x else "sky")
        if not back:
            ey = hcy + hh * .05
            exs = [hcx - hhw * .5] if side else [hcx - hhw * .42, hcx + hhw * .42]
            for ex in exs:
                cv.rect(ex - 2, ey - 1, ex + 2, ey + 1, "sky"); cv.rect(ex - 1, ey - 1, ex + 1, ey, "white")
    return f


def Ht_(c, f):
    return max(1, c["Ht"] * f)


def hrimgard(P3):
    P = dict(skin="pale", hair="grey", hairstyle="long", beard="short", beard_c=("white", "plaster_hi", "stone_hi"), tunic="slate", trousers="slate", mantle="snowfur",
             width=1.04, head=1.02, plate=plate(P3), extra=crown(P3), raise_=1.25, brow="stone_lo", belt=("stone_lo", "shadow"), buckle="sky",
             trim="sky", cheeks=False, hunch=.1, legs_w=1.15, arms_w=1.2, hem=.08)
    d = giant(P, 201)
    d.die_mode = "sink"
    return d


def roles():
    return {
        "hrimgard": dict(draw=hrimgard(False), scale=7.0, boss=True, enemy=True, kind="enemy", anims=("idle", "walk", "attack", "die"),
                         desc="Hrimgard the Unthawed (boss, 7x; the ONLY plate in Jotunheim): ancient giant king in rune-iron plate, ice crown, rimed beard, cold fire leaking from every joint. Phases 1-2.",
                         light={"color": "#3fb8ff", "intensity": 1.2, "range": 9.0}, stats_hint={"tier": "boss", "height_x_player": 7.0, "dungeon": "Titan's Barrow", "plate": True, "element": "ice"}),
        "hrimgard_p3": dict(draw=hrimgard(True), scale=7.0, boss=True, enemy=True, kind="enemy", anims=("idle", "walk", "attack", "die"),
                            desc="Hrimgard phase 3 (25%): the braziers relight, cold fire roaring off his shoulders. die = sinks to the ice, laid back to sleep.",
                            light={"color": "#6fd0ff", "intensity": 1.5, "range": 11.0}, stats_hint={"tier": "boss", "height_x_player": 7.0}),
    }
