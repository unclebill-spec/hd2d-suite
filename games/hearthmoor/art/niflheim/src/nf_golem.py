"""Ice / avalanche golems: stacked rock chunks with glowing rune seams (palette sky/white; the glow itself is fx + light).
Drawn natively at game scale. Die is drawn here (crumble), not by rotation."""
import math
from nf_common import R, hsh

def chunk(cv, cx, cy, rx, ry, ramp, snow=False, seed=0):
    def f(u, v):
        n = hsh("ch", int(cx), int(cy), seed, round(u * 3), round(v * 3))
        if snow and v < -.55:
            return "white" if u < .2 else "plaster_hi"
        c = ramp[0] if (u < -.4 and v < .3) else ramp[2] if (u > .5 or v > .75) else ramp[1]
        if n > .86:
            c = ramp[0] if c != ramp[0] else ramp[1]
        return c
    cv.ell(cx, cy, rx, ry, f)


def crack(cv, x0, y0, x1, y1, col="sky", glow="white"):
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    for j in range(n + 1):
        t = j / n
        x, y = x0 + (x1 - x0) * t + (1 if j % 3 == 1 else 0), y0 + (y1 - y0) * t
        cv.set(x, y, col)
    cv.set(x0, y0, glow)


def golem(kind, ht):
    colo = kind.startswith("colossus")
    ice = kind == "ice" or colo
    ph = int(kind[-1]) if kind[-1].isdigit() else 1
    body = R["ice"] if ice else R["rock"]
    deep = R["icedeep"] if ice else R["bluerock"]
    def draw(cv, face, anim, i):
        G = cv.h - 2; CX = cv.w // 2; Ht = ht; k = Ht / 29.0
        side, back = face == "left", face == "up"
        b = [0, 1, 1, 0][i] if anim == "idle" else [0, -1, 0, -1][i] if anim == "walk" else [0, -1, 2, 0][i] if anim == "attack" else 0
        st = [1, 0, -1, 0][i] if anim == "walk" else 0
        at = [0, .5, 1, .7][i] if anim == "attack" else 0
        curl = (not ice) and anim == "attack"
        # ---- die: crumble
        if anim == "die":
            n = [3, 5, 7, 8][i]
            for j in range(n + 4):
                a = j * 2.4
                rr = Ht * (.10 + .08 * hsh("d", j))
                x = CX + math.cos(a) * Ht * min(.30, 0.10 + .03 * j * (i + 1) / 4)
                y = G - rr * .6 - (abs(math.sin(a * 1.3)) * Ht * (.5 - i * .12) * (1 if j < 5 else .3))
                if i == 3:
                    y = G - rr * .6
                chunk(cv, x, y, rr, rr * .75, body if j % 3 else deep, snow=(j % 2 == 0), seed=j)
            if i < 3:
                chunk(cv, CX, G - Ht * (.42 - i * .1), Ht * .17, Ht * .15, body, seed=9)       # head sinking
                crack(cv, CX - 3, G - Ht * .55, CX + 2, G - Ht * .2)
            else:
                cv.set(CX, G - 6, "white"); cv.set(CX + 1, G - 6, "sky"); cv.set(CX - 1, G - 5, "sky")      # last rune spark
            return
        # ---- avalanche attack: a rolling boulder
        if curl:
            r = int(Ht * .36 * (1.0 if at > .4 else .8))
            cy = G - r + 1
            chunk(cv, CX, cy, r, r, body, snow=True, seed=2)
            ang = i * 1.1
            for j in range(4):
                a = ang + j * math.pi / 2
                crack(cv, CX + math.cos(a) * r * .2, cy + math.sin(a) * r * .2, CX + math.cos(a) * r * .85, cy + math.sin(a) * r * .85, "stone_lo", "stone_lo")
            for j in range(5):                           # spin streaks
                cv.rect(CX - r - 4 - j * 2, cy - r + 3 + j * 4, CX - r - 1 - j * 2, cy - r + 3 + j * 4, "stone_hi" if j % 2 else "plaster")
            cv.set(CX - r * .35, cy - r * .1, "sky"); cv.set(CX + r * .1, cy - r * .1, "sky")
            return
        hunch = 0 if ice else Ht * .08
        # legs
        for sd in (-1, 1):
            lx = CX + sd * Ht * .16 + (st * sd * 1.5 if not side else st * sd * 2)
            ly = G - Ht * .13 - (1 if (anim == "walk" and (i == 1 and sd < 0 or i == 3 and sd > 0)) else 0)
            if side:
                lx = CX + sd * 2 + st * sd * 3
            chunk(cv, lx, ly, Ht * .12, Ht * .13, deep if sd > 0 else body, seed=sd + 3)
            cv.rect(lx - Ht * .09, G - 1, lx + Ht * .09, G, deep[1])
        # torso
        ty = G - Ht * .45 + b + hunch
        chunk(cv, CX, ty, Ht * (.25 if not side else .17), Ht * .22, body, snow=not ice, seed=1)
        chunk(cv, CX, ty + Ht * .15, Ht * (.17 if not side else .12), Ht * .1, deep, seed=4)           # waist block
        if not back:
            crack(cv, CX - Ht * .08, ty - Ht * .12, CX + Ht * .04, ty + Ht * .1)
            cv.rect(CX - Ht * .12, ty + Ht * .13, CX + Ht * .12, ty + Ht * .13, "sky")
        else:
            crack(cv, CX + Ht * .05, ty - Ht * .15, CX - Ht * .04, ty + Ht * .12)
        if colo:            # hollow chest with the cold-fire core; glowing frost runes on the shoulders (dim in phase 3)
            cr, cry = Ht * (.10 if ph != 2 else .14), Ht * (.12 if ph != 2 else .17)
            if not side:
                cv.ell(CX, ty - Ht * .02, cr, cry, lambda u, v: "shadow" if v > -.2 else "ink")
                core = (cr * (.55 if ph == 1 else .8))
                if not back:
                    cv.ell(CX, ty - Ht * .02, core, core * 1.1, lambda u, v: "white" if u * u + v * v < .35 else "sky" if ph != 3 else "flower_blue")
                    for a in range(6):
                        cv.set(CX + math.cos(a * 1.05 + i * .5) * (cr + 1.5), ty - Ht * .02 + math.sin(a * 1.05 + i * .5) * (cry + 1.5), "sky" if ph != 3 else "stone_lo")
                else:
                    cv.ell(CX, ty - Ht * .02, cr * .8, cry * .8, "shadow")
                    for dy in (-.06, 0, .06):
                        cv.set(CX, ty + Ht * dy, "sky" if ph != 3 else "stone_lo")
            for sd in ((-1, 1) if not side else (-1,)):
                rx0 = CX + sd * Ht * (.26 if not side else .0)
                for j in range(4):
                    cv.set(rx0 + (j % 2) * sd, ty - Ht * .19 + j * 2, "white" if (ph != 3 and j == 0) else "sky" if ph != 3 else "stone_lo")
                cv.rect(rx0 - 2, ty - Ht * .19 + 8, rx0 + 2, ty - Ht * .19 + 8, "sky" if ph != 3 else "stone_lo")
        # arms
        for sd in (-1, 1):
            if side and sd > 0:
                continue
            ax = CX + sd * Ht * (.30 if not side else 0)
            ay = ty - Ht * .05
            hy = ay + Ht * .19 - at * Ht * .5 + (st * sd * 2)
            hx = ax + sd * Ht * .04 + (-at * Ht * .1 if side else 0)
            cv.seg(ax, ay, hx, hy, Ht * .15, Ht * .15, body if sd < 0 else deep)
            chunk(cv, hx, hy + Ht * .04, Ht * .11, Ht * .11, body, snow=False, seed=5 + sd)
        # head
        hy = ty - Ht * .28 + b
        hx = CX - (Ht * .04 if side else 0)
        chunk(cv, hx, hy, Ht * .15, Ht * .13, body, snow=not ice, seed=7)
        if not back:
            ey = hy + Ht * .02
            for sd in ((-1, 1) if not side else (-1,)):
                ex = hx + sd * Ht * .06
                cv.rect(ex - 1, ey, ex + 1, ey, "white"); cv.set(ex, ey, "sky")
        if ice:     # crystal spikes on the shoulders / crown
            for sd in (-1, 1):
                cv.poly([(CX + sd * Ht * .26 - 2, ty - Ht * .1), (CX + sd * Ht * .26 + 2, ty - Ht * .1), (CX + sd * Ht * .26 + sd, ty - Ht * .3)], lambda a, c: "white" if a < CX + sd * Ht * .26 else "sky")
            cv.poly([(hx - 2, hy - Ht * .1), (hx + 2, hy - Ht * .1), (hx, hy - Ht * .27)], "white")
    draw.fall = False
    return draw
