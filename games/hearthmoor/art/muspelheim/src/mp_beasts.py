"""Muspelheim creatures drawn natively: magma hounds (coal-black, lava seams, glowing mane for the alpha) and flame elementals
(spinning column of flame; pyreling = violet core). Palette only (lamp / flower_gold / roof_hi / white fire, stone_lo / shadow coal);
the glow is fx + light. Hounds and elementals keep their feet / base on the ground row in every frame."""
import math
from mp_common import R, hsh

COAL = ("stone_lo", "shadow", "shadow")
LAVA = ("flower_gold", "lamp", "roof_hi")


def _flame_tuft(cv, x, y, h, w, k, big=False):
    for yy in range(int(h)):
        t = yy / max(1, h)
        ww = max(0, w * (1 - t) * (1 + .25 * math.sin(k + yy * .6)))
        for dx in range(-int(ww), int(ww) + 1):
            cv.set(x + dx + math.sin(yy * .5 + k) * .8, y - yy, "white" if (abs(dx) < ww * .35 and t < .4) else "flower_gold" if t < .55 else "lamp" if t < .85 else "roof_hi")


def hound(ht, alpha=False):
    def draw(cv, face, anim, i):
        G = cv.h - 2; CX = cv.w // 2; Ht = ht; k = Ht / 29.0
        H = Ht * (.52 if not alpha else .5); L = Ht * (.78 if not alpha else .8)
        side, back = face == "left", face == "up"
        st = [1, 0, -1, 0][i] if anim == "walk" else 0
        b = [0, 1, 1, 0][i] if anim == "idle" else [0, -1, 0, -1][i] if anim == "walk" else 0
        at = [0, .5, 1, .7][i] if anim == "attack" else 0
        dead = anim == "die"
        sag = [0, .12, .3, .46][i] if dead else 0
        by = G - H * .78 + H * sag + b * .7 - (at * H * .12)       # body centre
        def leg(x, top, foot_y, sd=0, c=COAL, hi=False):
            w = max(2.5, H * .23)
            cv.seg(x, top, x + sd, foot_y - 1, w, w * .85, c)
            cv.rect(x - w * .6 + sd, foot_y - 1, x + w * .6 + sd, foot_y, "stone_lo")
        def seams(x0, x1, y0, y1, n=4):
            for j in range(n):
                t = (j + .5) / n
                x = x0 + (x1 - x0) * t; y = y0 + (y1 - y0) * ((j % 2) * .6 + .2)
                cv.set(x, y, "lamp"); cv.set(x + 1, y + 1, "roof_hi")
                if j % 2 == 0:
                    cv.set(x, y - 1, "flower_gold")
        if dead and i == 3:        # a heap of cooling coals with a few embers
            cv.ell(CX, G - H * .12, L * .45, H * .16, lambda u, v: COAL[0] if (u < -.3 and v < 0) else COAL[2] if (u > .4 or v > .5) else COAL[1])
            for j in range(5):
                cv.set(CX + (j - 2) * L * .13, G - H * .2 - (j % 2), "lamp" if j % 2 else "roof_hi")
            cv.set(CX - L * .1, G - H * .3, "flower_gold"); cv.set(CX + L * .15, G - H * .06, "white")
            return
        if side:
            bx0, bx1 = CX - L * .5, CX + L * .5
            lean = -at * L * .12
            for (xo, ph) in ((.32, 1), (-.28, -1)):
                x = CX + xo * L + st * ph * H * .25 + lean
                leg(x, by + H * .1, G - (1 if (anim == "walk" and st * ph == -1) else 0), 0)
            cv.ell(CX + lean * .5, by, L * .5, H * .3, lambda u, v: COAL[0] if (u < -.3 and v < -.2) else COAL[2] if (u > .5 or v > .55) else COAL[1])
            cv.ell(CX - L * .3 + lean, by - H * .05, L * .2, H * .3, lambda u, v: COAL[0] if (u < -.2 and v < -.1) else COAL[1])        # chest
            hx, hy = CX - L * .56 + lean * 1.6, by - H * .3 + sag * H * .5
            cv.ell(hx, hy, H * .3, H * .24, lambda u, v: COAL[0] if (u < -.3 and v < -.1) else COAL[1] if v < .5 else COAL[2])
            sx = hx - H * .34
            cv.ell(sx, hy + H * .06, H * .2, H * .12, lambda u, v: COAL[1] if v < .3 else COAL[2])             # snout
            cv.set(sx - H * .17, hy + H * .02, "ink")
            if at > .4:
                cv.rect(sx - H * .1, hy + H * .12, sx + H * .12, hy + H * .16, "lamp"); cv.set(sx - H * .05, hy + H * .12, "white")
            cv.poly([(hx - 1, hy - H * .2), (hx + 3, hy - H * .22), (hx + 1, hy - H * .5)], lambda a, b: COAL[0])        # ear
            cv.set(hx - H * .1, hy - H * .06, "lamp"); cv.set(hx - H * .1 - 1, hy - H * .06, "white")                   # eye
            tx = CX + L * .5
            for j in range(5):
                cv.seg(tx + j * 1.3, by - j * H * .12 + (1 if j > 2 else 0), tx + j * 1.3 + 1.3, by - (j + 1) * H * .12, 2.5 - j * .3, 2.2 - j * .3, COAL)
            cv.set(tx + 6, by - H * .6, "lamp"); cv.set(tx + 6, by - H * .6 - 1, "flower_gold")
            seams(bx0 + L * .3, bx1 - L * .1, by - H * .1, by + H * .18)
            if alpha:                # glowing mane of flame along the neck and back
                for j in range(4):
                    _flame_tuft(cv, hx + 3 + j * L * .1, by - H * .26 - j * .4, H * .38, 2.4, i * 1.3 + j)
            cv.ell(CX + L * .05, by + H * .22, L * .34, H * .1, lambda u, v: "stone_lo")
        else:
            wid = H * (.42 if not alpha else .46)
            for sd in (-1, 1):
                x = CX + sd * wid * .8 + st * sd * 1.5
                leg(x, by + H * .1, G - (1 if (anim == "walk" and ((i == 1 and sd < 0) or (i == 3 and sd > 0))) else 0), 0)
            cv.ell(CX, by, wid * 1.15, H * .33, lambda u, v: COAL[0] if (u < -.4 and v < -.2) else COAL[2] if (u > .5 or v > .55) else COAL[1])
            if back:
                for j in range(5):
                    cv.seg(CX + (j % 2) * 1.0, by - H * .1 - j * H * .12, CX + ((j + 1) % 2) * 1.0, by - H * .1 - (j + 1) * H * .12, 2.6 - j * .3, 2.3 - j * .3, COAL)
                cv.set(CX, by - H * .72, "lamp"); cv.set(CX, by - H * .72 - 1, "flower_gold")
                seams(CX - wid, CX + wid, by - H * .2, by + H * .15, 4)
                if alpha:
                    for j in range(4):
                        _flame_tuft(cv, CX + (j - 1.5) * 3.5, by - H * .3, H * .38, 2.2, i * 1.2 + j)
            else:
                hy = by - H * .42 + sag * H * .5
                cv.ell(CX, hy, H * .36, H * .3, lambda u, v: COAL[0] if (u < -.4 and v < -.2) else COAL[2] if (u > .5 or v > .6) else COAL[1])
                for sd in (-1, 1):
                    cv.poly([(CX + sd * H * .3 - 2, hy - H * .2), (CX + sd * H * .3 + 2, hy - H * .2), (CX + sd * H * .34, hy - H * .52)], lambda a, b: COAL[0])
                    cv.set(CX + sd * H * .15, hy - H * .02, "lamp"); cv.set(CX + sd * H * .15, hy - H * .02 - 1, "white")
                cv.ell(CX, hy + H * .14, H * .17, H * .11, lambda u, v: COAL[1] if v < .2 else COAL[2])
                cv.set(CX, hy + H * .1, "ink")
                if at > .4:
                    cv.rect(CX - H * .1, hy + H * .2, CX + H * .1, hy + H * .24, "lamp")
                seams(CX - wid, CX + wid, by - H * .05, by + H * .25, 3)
                if alpha:
                    for j in range(5):
                        _flame_tuft(cv, CX + (j - 2) * 3.2, hy - H * .24, H * .36, 2.2, i * 1.2 + j)
    draw.fall = False
    return draw


def elemental(ht, violet=False):
    def draw(cv, face, anim, i):
        G = cv.h - 2; CX = cv.w // 2; Ht = ht; k = Ht / 29.0
        side, back = face == "left", face == "up"
        dead = anim == "die"
        hgt = Ht * (1.0 if not dead else [.8, .55, .3, .12][i])
        wob = [0, 1, 0, -1][i]
        at = [0, .5, 1, .7][i] if anim == "attack" else 0
        wmax = Ht * (.26 if not side else .2) * (1 + at * .35)
        sp = i * (1.6 if anim != "idle" else .9)
        for y in range(int(hgt)):
            t = y / max(1, hgt)
            yy = G - y
            prof = (math.sin(math.pi * min(1, t * .85 + .15)) ** .7) * (1 - t * .45) * (1 + .2 * math.sin(sp + y * .35))
            w = max(.5, wmax * prof)
            sway = math.sin(y * .22 + sp) * Ht * .035 * t + wob * t * .8
            for dx in range(-int(w), int(w) + 1):
                d = abs(dx) / max(w, 1)
                c = "white" if (d < .22 and .1 < t < .55) else "flower_gold" if d < .5 and t < .75 else "lamp" if d < .8 else "roof_hi" if d < .95 else "roof"
                if t > .8 and d > .5:
                    c = "roof_hi"
                if (dx + y + i) % 7 == 0 and d > .6 and t > .3:
                    c = None
                if c:
                    cv.set(CX + dx + sway, yy, c)
        # tendrils (attack) and tip flames
        for j in range(3):
            _flame_tuft(cv, CX + (j - 1) * wmax * .6 + math.sin(sp + j) * 1.5, G - hgt * .92, Ht * .16 + at * Ht * .08, 2.4, i * 1.3 + j)
        if at > .4 and not back:
            for sd in (-1, 1):
                _flame_tuft(cv, CX + sd * (wmax + 3), G - hgt * .5, Ht * .22, 2.2, i + sd)
        # core: violet for the pyreling, white-hot otherwise
        cy = G - hgt * .42 + wob
        if violet:
            cv.ell(CX, cy, wmax * .42, wmax * .5, lambda u, v: "white" if (u * u + v * v < .12) else "flower_blue" if (u < .1 and v < .2) else "cloth")
            for a in range(4):
                cv.set(CX + math.cos(sp + a * 1.57) * wmax * .62, cy + math.sin(sp + a * 1.57) * wmax * .5, "flower_blue")
        elif not dead:
            cv.ell(CX, cy, wmax * .22, wmax * .26, "white")
        # face
        if not back and not dead:
            fy = G - hgt * .62 + wob
            for dx in ((-.28, .28) if not side else (-.3,)):
                x = CX + dx * wmax * 1.3 - (wmax * .25 if side else 0)
                cv.rect(x - 1, fy, x + 1, fy + 1, "ink")
            cv.rect(CX - wmax * .2 - (wmax * .25 if side else 0), fy + 3, CX + wmax * .2 - (wmax * .25 if side else 0), fy + 3, "roof_lo")
        elif back:
            for j in range(3):
                cv.set(CX + math.sin(sp + j) * wmax * .4, G - hgt * (.3 + .2 * j), "white")
        if dead and i == 3:
            for j in range(5):
                cv.set(CX + (j - 2) * 2, G - 1 - (j % 2), "lamp" if j % 2 else "flower_gold")
    draw.fall = False
    return draw
