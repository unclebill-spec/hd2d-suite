"""Lady Sylvaine, the elf vampire queen of the Prism Vault (boss, 5.5x player: 128x176 frame, figure ~170 px).
Drawn natively (never upscaled), biome palette only (her neon violet lives in the gamefx: sylvaine_aura / drain_beam /
violet_moths), boss_sheet.py conventions (pivot bottom-centre, 28 columns, rows down/up/left/right).

Elegant, cozy-gloomy, never gory: long silver hair, long elf ears, a tall crystal tiara, rose eyes; NORMAL clothes with a
clear waist: a fitted deep-blue long-sleeved blouse with a white lace jabot and cuffs (top), a dark belt with a gold
clasp, a long mauve-dark bell skirt with a rose front panel and a pale hem (bottom), pale pointed slippers; a high-collared
dark-red cape with a red lining behind her.
  idle    breathing, hair / cape hem sway, tiara glints
  walk    a slow glide (hem ripples, slippers peek)
  attack  arms sweep up and out, palms open (frame 14 = drain: spawn drain_beam toward the target + sylvaine_aura pulse)
  die     a hand to her heart, she sinks to her knees, bows, then only the pooled gown, cape and tiara remain
          (spawn violet_moths on frame 26-27: she becomes moths and is gone)"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_lib"))
from hmart import ell, rect, shader  # noqa: E402

W_, H_ = 128, 176
CX = 64
HEM = 174


def thick(s, p0, p1, r, fn):
    """a round-capped thick segment; fn(t, d, x, y) -> colour (t along, d signed across in -1..1)"""
    (x0, y0), (x1, y1) = p0, p1
    L = max(0.01, math.hypot(x1 - x0, y1 - y0))
    nx, ny = -(y1 - y0) / L, (x1 - x0) / L
    for y in range(int(min(y0, y1) - r - 1), int(max(y0, y1) + r + 2)):
        for x in range(int(min(x0, x1) - r - 1), int(max(x0, x1) + r + 2)):
            t = max(0, min(1, ((x - x0) * (x1 - x0) + (y - y0) * (y1 - y0)) / (L * L)))
            px, py = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            if math.hypot(x - px, y - py) <= r:
                d = ((x - px) * nx + (y - py) * ny) / max(r, 0.01)
                s.set(x, y, fn(t, d, x, y))


def tone3(hi, mid, lo):
    return lambda u: hi if u < 0.28 else lo if u > 0.72 else mid


def cape(s, face, top, wy, sway, i):
    """the cape behind her: shoulders -> hem, folds; the lining shows at the edges"""
    for y in range(top, HEM + 1):
        t = (y - top) / (HEM - top)
        if face == "up":
            hw = 17 + 26 * t ** 0.85
            cx = CX + sway * t
        elif face == "left":
            hw = 10 + 22 * t ** 0.85
            cx = CX + 4 + 4 * t + sway * t
        else:
            hw = 17 + 27 * t ** 0.85
            cx = CX + sway * t
        rip = math.sin(y * 0.22 + i * 1.3) * 1.2 * t
        for x in range(int(cx - hw - rip), int(cx + hw + rip) + 1):
            u = (x - (cx - hw)) / (2 * hw)
            fold = math.sin((x - cx) * 0.32 + t * 1.5)
            c = "roof_lo" if fold > -0.6 else "shadow"
            if face == "up" and fold > 0.93 and t > 0.15:
                c = "roof"
            if (u < 0.035 or u > 0.965) and face != "up":
                c = "roof"
            if y >= HEM - 1:
                c = "shadow"
            s.set(x, y, c)


def skirt(s, face, wy, i, walk, spread=1.0):
    """the long bell skirt from the belt to the hem: mauve-dark folds, a rose front panel, a pale hem with gold dots"""
    n = HEM - wy
    for y in range(wy, HEM + 1):
        t = (y - wy) / max(1, n)
        rip = (math.sin(y * 0.35 + i * 1.6) * 1.0 * t) if walk else math.sin(y * 0.2 + i * 0.8) * 0.4 * t
        if face == "left":
            front, back = 10 + 24 * t ** 0.9 * spread, 11 + 24 * t ** 0.85 * spread
            cx = CX
            x0, x1 = cx - front + rip, cx + back + rip * 0.5
        else:
            hw = (11 + 26 * t ** 0.9) * spread
            cx = CX
            x0, x1 = cx - hw - rip, cx + hw + rip
        for x in range(int(x0), int(x1) + 1):
            u = (x - x0) / max(1, (x1 - x0))
            fold = math.sin((x - cx) * (0.5 - 0.25 * t) + 0.8)
            c = "stone_lo" if (u < 0.35 and fold > 0.82) else "roof_lo" if fold > 0.5 else "ink" if (u > 0.6 and fold < -0.7) else "shadow"
            if face == "down":                               # rose front panel (an inverted V opening)
                pw = 2 + 9 * t
                if abs(x - cx) < pw:
                    c = "flower_rose" if (x - cx) < pw * 0.35 else "roof_hi" if (x - cx) < pw * 0.75 else "roof"
                    if abs(abs(x - cx) - pw) < 1:
                        c = "flower_gold" if (y % 6 == 0) else "stone_hi"
            elif face == "left":
                if x - x0 < 3 + 4 * t:
                    c = "flower_rose" if (x - x0) < 1.5 + 2 * t else "roof_hi"
            if y >= HEM - 2:
                c = "stone_hi" if (x % 4) else "flower_gold"
            if y == HEM:
                c = "stone"
            s.set(x, y, c)


def slippers(s, face, i, walk):
    if face == "up":
        return
    off = [0, 1, 0, -1][i] if walk else 0
    if face == "left":
        for x in range(CX - 14 - max(0, off), CX - 8):
            s.set(x, HEM - 1, "stone_hi" if x > CX - 13 else "white")
        rect(s, CX - 15 - max(0, off), HEM, CX - 9, HEM, "stone")
        return
    for (sx, o) in ((CX - 8, off), (CX + 4, -off)):
        rect(s, sx, HEM - 2 + (1 if o > 0 else 0), sx + 4, HEM, "stone_hi")
        s.set(sx + 1, HEM - 2 + (1 if o > 0 else 0), "white"); s.set(sx + 2, HEM - 2 + (1 if o > 0 else 0), "white")
        rect(s, sx, HEM, sx + 4, HEM, "stone")


def bodice(s, face, top, wy, bob):
    """the fitted deep-blue blouse (top): shoulders -> waist, white lace jabot + gold brooch; dark belt with gold clasp"""
    for y in range(top, wy):
        t = (y - top) / max(1, wy - top)
        if face == "left":
            hw = 10 - 3 * t
            cx = CX + 1
        else:
            hw = 16 - 6 * t ** 0.8
            cx = CX
        for x in range(int(cx - hw), int(cx + hw) + 1):
            u = (x - (cx - hw)) / (2 * hw)
            c = "flower_blue" if u < 0.22 else "shadow" if u > 0.82 else "cloth"
            s.set(x, y, c)
    if face == "down":
        for y in range(top, top + 16):                       # lace jabot
            w = 3 - (y - top) // 6
            for x in range(CX - w, CX + w + 1):
                s.set(x, y, "white" if (x + y) % 3 else "plaster_hi")
        ell(s, CX, top + 2, 2.2, 1.6, "flower_gold"); s.set(CX, top + 2, "sky"); s.set(CX - 1, top + 1, "white")
    elif face == "left":
        for y in range(top, top + 12):
            s.set(int(CX - 9 + (y - top) * 0.15), y, "white" if y % 2 else "plaster_hi")
            s.set(int(CX - 8 + (y - top) * 0.15), y, "plaster_hi")
    # belt
    if face == "left":
        x0, x1 = CX - 7, CX + 9
    else:
        x0, x1 = CX - 10, CX + 10
    rect(s, x0, wy, x1, wy + 4, "timber_lo")
    rect(s, x0, wy + 4, x1, wy + 4, "ink")
    if face == "down":
        rect(s, CX - 2, wy, CX + 2, wy + 4, "flower_gold"); s.set(CX, wy + 2, "sky"); s.set(CX - 1, wy + 1, "white")
    elif face == "left":
        rect(s, CX - 7, wy, CX - 5, wy + 3, "flower_gold")


def sleeve(s, sh, hand, r=3.6, cuff=True):
    thick(s, sh, hand, r, lambda t, d, x, y: "flower_blue" if d < -0.4 else "shadow" if d > 0.5 else "cloth")
    hx, hy = hand
    if cuff:
        ell(s, hx, hy, r + 0.8, r * 0.7, "plaster_hi")
        s.set(int(hx), int(hy), "white")
    dx, dy = hx - sh[0], hy - sh[1]
    L = max(0.01, math.hypot(dx, dy))
    ux, uy = dx / L, dy / L
    ell(s, hx + ux * 3.2, hy + uy * 3.2, 2.4, 2.4, "plaster_hi", shader(hx + ux * 3.2, 2.4, "plaster_hi", "plaster_hi", "skin"))
    for k in range(3):                                       # slender fingers
        s.set(int(round(hx + ux * 5.6 + (k - 1) * uy * 1.2)), int(round(hy + uy * 5.6 - (k - 1) * ux * 1.2)), "plaster_hi")


def hair_back(s, face, hy, i, bow=0):
    """the long silver hair behind the body (drawn before the bodice and arms)"""
    hx = CX - (3 if face == "left" else 0)
    hy = hy + bow
    if face == "up":
        for y in range(hy - 12, hy + 66):
            t = (y - hy + 12) / 78
            hw = (12 + 4 * t) * (1 if t < 0.8 else max(0.15, 1 - (t - 0.8) * 4.2))
            sw = math.sin(i * 1.57 + y * 0.08) * 1.0 * t
            for x in range(int(hx - hw + sw), int(hx + hw + sw) + 1):
                u = (x - (hx - hw + sw)) / max(1, 2 * hw)
                strand = math.sin((x - hx) * 1.1 + y * 0.05)
                c = "stone_hi" if u < 0.5 else "stone" if u < 0.85 else "stone_lo"
                if strand > 0.8:
                    c = "white" if u < 0.45 else "stone_hi"
                elif strand < -0.85:
                    c = "stone" if u < 0.5 else "stone_lo"
                s.set(x, y, c)
    elif face == "left":
        for y in range(hy - 8, hy + 60):
            t = (y - hy + 8) / 68
            x0, x1 = hx + 2 + 2 * t, hx + 13 + 2 * t
            if t > 0.8:
                x0 += (t - 0.8) * 20
            sw = math.sin(i * 1.57 + y * 0.08) * 1.0 * t
            for x in range(int(x0 + sw), int(x1 + sw) + 1):
                u = (x - x0 - sw) / max(1, x1 - x0)
                strand = math.sin(x * 1.1 + y * 0.05)
                c = "stone_hi" if u < 0.45 else "stone" if u < 0.8 else "stone_lo"
                if strand > 0.85:
                    c = "white" if u < 0.5 else "stone_hi"
                s.set(x, y, c)
    else:
        for sd in (-1, 1):                                   # long locks falling behind the shoulders
            for y in range(hy - 4, hy + 58):
                t = (y - hy + 4) / 62
                xa = hx + sd * (12 + 7 * t)
                w = 3.5 * (1 if t < 0.8 else max(0.3, 1 - (t - 0.8) * 3.5))
                sw = math.sin(i * 1.57 + y * 0.09 + sd) * 1.0 * t
                for x in range(int(xa - w + sw), int(xa + w + sw) + 1):
                    u = (x - (xa - w + sw)) / max(1, 2 * w)
                    c = ("stone_hi" if u < 0.45 else "stone" if u < 0.8 else "stone_lo") if sd < 0 else ("stone" if u < 0.6 else "stone_lo")
                    if math.sin(x * 1.3 + y * 0.06) > 0.85:
                        c = "white" if sd < 0 else "stone_hi"
                    s.set(x, y, c)


def head(s, face, hy, i, glow=False, bow=0):
    """head centred at (CX, hy): long silver hair, long ears, crystal tiara, rose eyes"""
    hx = CX - (3 if face == "left" else 0)
    hy = hy + bow
    # ears (long, swept out and up)
    if face in ("down", "up"):
        for sd in (-1, 1):
            for k in range(11):
                x = hx + sd * (10 + k)
                y0 = hy + 1 - k * 0.6
                for y in range(int(y0), int(y0 + 3 - k * 0.25) + 1):
                    s.set(int(x), y, "plaster_hi" if (sd < 0 and face == "down") else "skin" if face == "down" else "skin_lo")
            s.set(int(hx + sd * 11), hy + 2, "skin_lo")
    else:
        for k in range(12):
            x = hx + 3 + k
            y0 = hy - 1 - k * 0.65
            for y in range(int(y0), int(y0 + 3 - k * 0.22) + 1):
                s.set(int(x), y, "plaster_hi" if k < 8 else "skin")
        s.set(hx + 4, hy, "skin_lo")
    # face / back of head
    if face == "up":
        ell(s, hx, hy - 1, 10.5, 12, "stone_hi", lambda x, y, c: "stone_hi" if x < hx - 3 else "stone" if x < hx + 5 else "stone_lo")
    else:
        if face == "left":
            ell(s, hx - 1, hy, 8.5, 11.5, "plaster_hi", lambda x, y, c: "plaster_hi" if x < hx + 3 else "skin")
            s.set(hx - 10, hy + 1, "plaster_hi"); s.set(hx - 10, hy + 2, "plaster_hi"); s.set(hx - 9, hy + 3, "skin")   # nose
            rect(s, hx - 9, hy + 6, hx - 8, hy + 6, "roof")                                                         # lips
            ey = hy - 1
            rect(s, hx - 8, ey - 1, hx - 5, ey - 1, "ink")
            s.set(hx - 7, ey, "white" if glow else "flower_rose"); s.set(hx - 6, ey, "white" if glow else "roof"); s.set(hx - 8, ey, "white")
            rect(s, hx - 8, ey - 3, hx - 5, ey - 3, "stone")
            ell(s, hx + 1, hy - 6, 9.5, 6.5, "stone_hi", lambda x, y, c: "white" if (x + y) % 6 == 0 else "stone_hi" if x < hx + 3 else "stone")
            for y in range(hy - 6, hy + 4):                  # hair over the temple
                s.set(hx + 5, y, "stone"); s.set(hx + 6, y, "stone_lo")
        else:
            ell(s, hx, hy, 9.5, 11.5, "plaster_hi", lambda x, y, c: "plaster_hi" if x < hx + 4 else "skin")
            ey = hy - 1
            for sd in (-1, 1):
                ex = hx + sd * 4
                rect(s, ex - 2, ey - 1, ex + 2, ey - 1, "ink")
                rect(s, ex - 1, ey, ex + 1, ey + 1, "white" if glow else "flower_rose")
                s.set(ex, ey + 1, "white" if glow else "roof"); s.set(ex - 1, ey, "white")
                s.set(ex + 2 * sd, ey, "ink")
                rect(s, ex - 2, ey - 3, ex + 2, ey - 3, "stone")
                s.set(hx + sd * 6, hy + 3, "flower_rose")                                       # soft cheeks
            s.set(hx, hy + 3, "skin")
            rect(s, hx - 1, hy + 6, hx + 1, hy + 6, "roof"); s.set(hx, hy + 7, "roof_hi")
            # hair fringe parted in the middle, over the brow
            for x in range(int(hx - 10), int(hx + 11)):
                d = abs(x - hx)
                yb = hy - 12 + int(0.06 * d * d) + 4
                for y in range(hy - 12, min(yb, hy - 3) + 1):
                    s.set(x, y, "white" if (x + y) % 7 == 0 else "stone_hi" if x < hx + 3 else "stone")
    # crystal tiara
    ty = hy - 11
    spikes = ((-8, 4), (-4, 7), (0, 11), (4, 7), (8, 4)) if face != "left" else ((-6, 4), (-2, 8), (2, 6), (6, 3))
    for (dx, hgt) in spikes:
        x = hx + dx
        for k in range(hgt):
            w = 1 if k < hgt - 2 else 0
            for xx in range(x - w, x + w + 1):
                s.set(xx, ty - k, "white" if xx < x else "sky" if xx == x else "flower_blue")
        if (i + dx) % 4 == 0:
            s.set(x, ty - hgt, "white")
    rect(s, hx - 9 + (2 if face == "left" else 0), ty, hx + 9 - (2 if face == "left" else 0), ty + 1, "flower_gold")
    if face == "down":
        s.set(hx, ty, "flower_rose"); s.set(hx, ty + 1, "roof")


def collar(s, face, top):
    """the high standing cape collar behind the head: red lining facing us, dark outer edge"""
    if face == "up":
        for y in range(top - 18, top + 2):
            t = (y - top + 18) / 20
            hw = 22 - 8 * t
            for x in range(int(CX - hw), int(CX + hw) + 1):
                s.set(x, y, "roof_lo" if abs(x - CX) < hw - 2 else "shadow")
        return
    if face == "left":
        for y in range(top - 16, top + 2):
            t = (y - top + 16) / 18
            for x in range(int(CX + 6 + 4 * (1 - t)), int(CX + 16 + 4 * (1 - t))):
                s.set(x, y, "roof" if x < CX + 13 + 4 * (1 - t) else "roof_lo")
        return
    for sd in (-1, 1):
        for y in range(top - 20, top + 3):
            t = (y - top + 20) / 23
            xa, xb = CX + sd * (10 + 6 * t), CX + sd * (22 - 4 * t + 4 * (1 - t))
            for x in range(int(min(xa, xb)), int(max(xa, xb)) + 1):
                edge = abs(x - xb) < 1.5
                s.set(x, y, "roof_lo" if edge else "roof" if (x + y) % 5 else "roof_hi")


def sylvaine(s, face, anim, i):
    walk = anim == "walk"
    bob = [0, -1, -1, 0][i] if anim == "idle" else [0, -1, 0, -1][i] if walk else 0
    sway = [0, 1, 2, 1][i] if anim == "idle" else [0, 1, 0, -1][i] if walk else 0
    sink, spread, bow = 0, 1.0, 0
    if anim == "die":
        sink, spread, bow = [(2, 1.0, 2), (26, 1.12, 4), (44, 1.2, 7), (0, 0, 0)][i]
    if anim == "die" and i == 3:                             # only the pooled gown, cape and tiara remain
        for y in range(150, HEM + 1):
            t = (y - 150) / (HEM - 150)
            hw = 18 + 26 * t ** 0.6
            for x in range(int(CX - hw), int(CX + hw) + 1):
                u = (x - CX + hw) / (2 * hw)
                fold = math.sin((x - CX) * 0.4 + y * 0.2)
                c = "roof_lo" if u < 0.2 or u > 0.8 else "shadow" if fold > -0.3 else "stone_lo"
                if abs(x - CX) < 6 * t + 2 and t > 0.3:
                    c = "flower_rose" if x < CX else "roof"
                if y >= HEM - 1:
                    c = "stone_hi" if x % 4 else "flower_gold"
                s.set(x, y, c)
        for (dx, hgt) in ((-6, 3), (-3, 5), (0, 7), (3, 5), (6, 3)):
            for k in range(hgt):
                s.set(CX + 4 + dx, 150 - k, "sky" if k else "flower_gold"); s.set(CX + 3 + dx, 150 - k, "white")
        rect(s, CX - 3, 150, CX + 11, 151, "flower_gold")
        return
    wy = 84 + bob + sink
    top = 50 + bob + sink
    hy = 30 + bob + sink
    cape(s, face, top - 2, wy, sway, i)
    if face != "up":
        collar(s, face, top)
    if face == "up":
        collar(s, face, top)
        skirt(s, face, wy, i, walk, spread)
        bodice(s, face, top, wy, bob)
        cape(s, face, top - 2, wy, sway, i)                  # the cape covers her back
        hair_back(s, face, hy, i, bow)
        head(s, face, hy, i, bow=bow)
        if anim == "attack" and i in (1, 2):
            for sd in (-1, 1):
                sleeve(s, (CX + sd * 14, top + 4), (CX + sd * (30 if i == 2 else 24), top - (14 if i == 2 else 2)))
        return
    hair_back(s, face, hy, i, bow)
    skirt(s, face, wy + 4, i, walk, spread)
    if sink == 0:
        slippers(s, face, i, walk)
    bodice(s, face, top, wy, bob)
    glow = anim == "attack" and i in (1, 2)
    # arms
    if face == "left":
        if anim == "attack":
            hand = [(CX - 10, wy - 2), (CX - 20, top - 2), (CX - 30, top - 12), (CX - 16, top + 10)][i]
        elif anim == "die":
            hand = [(CX - 4, top + 8), (CX - 6, top + 8 + sink // 4), (CX - 10, wy + 6), (0, 0)][i]
        else:
            hand = (CX - 9, wy + 2 + (sway // 2 if walk else 0))
        sleeve(s, (CX - 1, top + 5), hand, 3.4)
    else:
        for sd in (-1, 1):
            sh = (CX + sd * 13, top + 5)
            if anim == "attack":
                hand = [(CX + sd * 6, wy + 2), (CX + sd * 28, top + 2), (CX + sd * 34, top - 16), (CX + sd * 22, top + 18)][i]
            elif anim == "die":
                hand = [(CX + sd * 4, top + 10), (CX + sd * 5, top + 10), (CX + sd * 16, wy + 8), (0, 0)][i]
            else:
                hand = (CX + sd * 5, wy + 3)                 # hands folded at the waist
            sleeve(s, sh, hand)
    head(s, face, hy, i, glow, bow)
