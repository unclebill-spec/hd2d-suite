"""Muspelheim gamefx (48 px cells, hd2d portal format via hmart.write_fx; one atlas gamefx/mp_fx.png). Neon on fx only (flagged in README).
Environment fx (lava, forge pools, embers, ash, cold fire, glow orbs, frogs, vines, crystals, springs) + boss / spell fx (Fire Wave, Magma Pool,
Ember Swarm, Flame Ward, Magma Hound summon, Vharzul's pillar telegraph, crown flare, ...)."""
import math, random
import mp_common as C
H = C.H
CELL = 48
H.ALLC.update({"mp_lava_hi": "#ffd27a", "mp_lava": "#ff7a1a", "mp_lava_lo": "#e8321e", "mp_lava_dk": "#8a1a14",
               "mp_ember": "#ffb066", "mp_ash": "#4a4650", "mp_ash_hi": "#8a8590", "mp_glass": "#ffe0a0", "mp_frost": "#3fb8ff",
               "mp_teal": "#2fd0d0", "mp_teal_hi": "#a8fff0", "mp_teal_lo": "#16807f", "mp_fizz": "#e8fff8"})
NB = ("neon_blue_hi", "neon_blue", "neon_blue_lo")
NV = ("neon_violet_hi", "neon_violet", "neon_violet_lo")
NR = ("neon_red_hi", "neon_red", "neon_red_lo")
LV = ("mp_lava_hi", "mp_lava", "mp_lava_lo")
EM = ("mp_ember", "mp_lava", "mp_lava_lo")
TE = ("mp_teal_hi", "mp_teal", "mp_teal_lo")
FL = ("white", "mp_lava_hi", "mp_lava", "mp_lava_lo")


def rise(cols, seed, n=12, spread=40, sp=1.5, tongue=True):
    """embers drifting up: round motes on a wobble, a few two-pixel tongues, a twinkle at the top"""
    def f():
        r = random.Random(seed); pts = [(r.uniform(5, 43), r.uniform(10, 46), r.randrange(8)) for _ in range(n)]
        out = []
        for k in range(8):
            F = H.Fx(CELL)
            for (x, y, p) in pts:
                b = (k + p) % 8; yy = y - b * 2.6 * sp; xx = x + math.sin((b + p) * .9) * 1.6
                if b in (1, 2):
                    F.set(xx, yy, cols[1]); F.set(xx, yy - 1, "white") if tongue else None
                elif b in (3, 4):
                    F.set(xx, yy, cols[0]); F.set(xx + 1, yy, cols[1])
                elif b == 5:
                    F.star(xx, yy, 1, "white", cols[0])
                elif b in (6, 7):
                    F.set(xx, yy, cols[2] if b == 7 else cols[1])
            out.append(F)
        return out
    return f


def fireflies(cols, seed, n=8):
    def f():
        r = random.Random(seed); pts = [(r.uniform(6, 42), r.uniform(6, 42), r.uniform(0, 6.28)) for _ in range(n)]
        out = []
        for k in range(8):
            F = H.Fx(CELL)
            for j, (x, y, ph) in enumerate(pts):
                a = k / 8 * math.tau + ph; X, Y = x + math.cos(a) * 3, y + math.sin(a * 2) * 2
                if (k + j) % 3:
                    F.set(X, Y, cols[0]); F.set(X + 1, Y, cols[1]); F.set(X, Y + 1, cols[2])
                else:
                    F.set(X, Y, cols[2])
            out.append(F)
        return out
    return f


def ash_fall():
    r = random.Random(7); pts = [(r.uniform(2, 46), r.uniform(0, 48), r.uniform(.8, 1.5), r.randrange(3)) for _ in range(26)]
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        for (x, y, sp, kind) in pts:
            yy = (y + k * 6 * sp) % 48; xx = x + math.sin(yy * .25 + x) * 2 + k * .3
            F.set(xx, yy, "mp_ash_hi" if kind == 0 else "mp_ash")
            if kind == 1:
                F.set(xx + 1, yy, "mp_ash")
            if kind == 2 and (k + int(x)) % 4 == 0:
                F.set(xx, yy, "mp_lava")                                   # a glowing flake
        out.append(F)
    return out


def ember_storm():
    r = random.Random(11); pts = [(r.uniform(0, 48), r.uniform(4, 44), r.uniform(1.0, 2.0)) for _ in range(30)]
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        for j, (x, y, sp) in enumerate(pts):
            xx = (x + k * 7 * sp) % 48; yy = y - (k * 2 * sp) % 6 + math.sin(xx * .3) * 1.5
            F.set(xx, yy, "mp_lava_hi" if j % 3 == 0 else "mp_lava"); F.set(xx - 1, yy + 1, "mp_lava_lo"); F.set(xx - 2, yy + 1, "mp_lava_lo") if j % 2 else None
            if j % 7 == 0:
                F.star(xx, yy, 1, "white", "mp_lava_hi")
        out.append(F)
    return out


def flame(cols, tall=1.0):
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        cx = 23.5
        for y in range(int(44 - 38 * tall), 44):
            t = (44 - y) / (38 * tall)
            w = max(0, 6.5 * math.sin(math.pi * min(1, t * 1.15)) ** 0.7 * (1 - t * .55)) * (1 + .12 * math.sin(k * 1.3 + y * .3))
            sway = math.sin(y * .22 + k * .9) * 2.4 * t
            for dx in range(-int(w), int(w) + 1):
                d = abs(dx) / max(w, 1)
                F.set(cx + dx + sway, y, "white" if (d < .25 and .15 < t < .6) else cols[0] if d < .5 else cols[1] if d < .8 else cols[2])
        for j in range(3):
            F.set(cx + math.sin(k + j * 2) * 8, 4 + (k * 3 + j * 7) % 16, cols[0])
        out.append(F)
    return out


def lava_crawl():
    """a 48 px emissive lava tile: dark crust cells over glowing channels, the glow crawling in 4 frames"""
    r = random.Random(3); out = []
    for k in range(4):
        F = H.Fx(CELL)
        for y in range(CELL):
            for x in range(CELL):
                v = math.sin(x * .21 + math.sin(y * .17 + k * 1.57) * 2.2) + math.sin(y * .27 - k * 1.57 * .5 + x * .09)
                if v > 1.05:
                    F.set(x, y, "mp_lava_hi" if v > 1.6 else "mp_lava")
                elif v > .55 and (x + y) % 2 == 0:
                    F.set(x, y, "mp_lava_lo")
                elif v < -1.1 and (x * 3 + y) % 5 == 0:
                    F.set(x, y, "mp_lava_dk")
        out.append(F)
    return out


def lava_fall():
    """molten fall: a 16 px wide ribbon pouring down, bright streaks running, splash foam at the foot; tile vertically"""
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        for y in range(CELL):
            for x in range(16, 32):
                u = (x - 24) / 8
                s = math.sin((y - k * 6) * .35 + u * 3) + math.sin((y * .6 + k * 9) * .21 + x)
                c = "mp_lava_hi" if s > 1.3 else "mp_lava" if s > .1 else "mp_lava_lo"
                if abs(u) > .85:
                    c = "mp_lava_lo" if (x + y) % 2 else "mp_lava_dk"
                F.set(x, y, c)
        for j in range(5):
            F.set(24 + math.sin(k + j * 2) * 12, 40 + (k * 2 + j * 3) % 8, "mp_lava_hi")                   # spray
        out.append(F)
    return out


def burn():
    r = random.Random(13); out = []
    for k in range(6):
        F = H.Fx(CELL)
        for y in range(CELL):
            for x in range(CELL):
                d = math.hypot(x - 24, (y - 24) / .62) / 19
                if d <= 1 and (x + y) % 2 == 0 and r.random() < .55:
                    F.set(x, y, "mp_lava_dk" if d > .6 else "mp_ash")
        for j in range(9):
            a = j * .7 + k * .4; rr = 4 + (j * 5 % 14)
            F.set(24 + math.cos(a) * rr, 24 + math.sin(a) * rr * .62, "mp_lava_hi" if (j + k) % 2 else "mp_lava")
            if (j + k) % 3 == 0:
                F.set(24 + math.cos(a) * rr, 24 + math.sin(a) * rr * .62 - 2, "mp_lava_lo")
        out.append(F)
    return out


def shimmer():
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        for x in range(6, 42, 3):
            for y in range(4, 46, 2):
                yy = y - k * 1.0
                if int(yy + x) % 6 == 0:
                    F.set(x + math.sin(yy * .5 + k) * 1.6, y, "mp_ember")
        out.append(F)
    return out


def frost_vein():
    """the Cold Seam: a frost-blue crack that pulses slowly (decal, over rock)"""
    out = []
    pts = [(2, 30), (10, 26), (16, 29), (22, 22), (28, 24), (34, 17), (40, 19), (46, 12)]
    for k in range(6):
        F = H.Fx(CELL)
        a = [.4, .6, .85, 1.0, .75, .5][k]
        for (p0, p1) in zip(pts[:-1], pts[1:]):
            F.line(p0[0], p0[1], p1[0], p1[1], "neon_blue" if a > .55 else "neon_blue_lo")
            if a > .7:
                F.line(p0[0], p0[1] - 1, p1[0], p1[1] - 1, "neon_blue_hi", every=2)
        for (x, y) in pts[1:-1]:
            if a > .6:
                F.star(x, y, 1, "white", "neon_blue_hi")
        for (x, y, dx, dy) in ((16, 29, 3, 6), (28, 24, -2, 6), (34, 17, 4, -5)):
            F.line(x, y, x + dx, y + dy, "neon_blue_lo")
        out.append(F)
    return out


def frog(cols):
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        hop = [0, 0, -3, -5, -4, -2, 0, 0][k]
        cx, cy = 24, 36 + hop
        F.disk(cx, cy, 5, ["mp_teal_lo", "mp_teal_lo", "mp_teal_lo"], sq=0.75)
        for dx in (-1, 0, 1):
            F.set(cx + dx * 2, cy - 2, "mp_teal")
        F.disk(cx + 4, cy - 2, 2.2, ["mp_teal", "mp_teal"], sq=1)
        for (dx, dy, c) in ((-3, 0, cols[1]), (0, 1, cols[0]), (3, -1, cols[1]), (-1, -2, cols[0]), (2, 2, cols[1]), (5, -3, "white")):
            F.set(cx + dx, cy + dy, c)
        for (lx, ly) in ((-4, 4), (4, 4)):
            F.set(cx + lx, cy + ly + (-hop // 3 if hop < -2 else 0), "mp_teal"); F.set(cx + lx + (1 if lx > 0 else -1), cy + ly + 1, "mp_teal_lo")
        if k in (2, 3, 4):
            F.set(cx + 8, cy + 3, cols[0])
        out.append(F)
    return out


def vines(cols):
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        for sx, ln, ph in ((9, 38, 0.0), (19, 30, 1.3), (29, 40, 2.1), (39, 28, 0.6)):
            for y in range(0, ln):
                x = sx + math.sin(y * .22 + k * .78 + ph) * (1 + y * .05)
                F.set(x, y, "mp_ash" if y % 3 else "mp_ash_hi")
                if y % 6 == 3:
                    F.set(x + 1, y, "mp_ash_hi"); F.set(x - 1, y + 1, "mp_ash")
                if y % 9 == 5:
                    F.set(x + 1, y + 1, cols[0]); F.set(x + 2, y + 1, cols[1])
            F.set(x, ln, cols[0]); F.set(x, ln + 1, cols[1]); F.set(x, ln + 2, "white")
        out.append(F)
    return out


def crystals(cols):
    """hanging glow-crystal cluster, pivot at the top: three points of different length, a glint walking down them"""
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        for (sx, ln, wd) in ((14, 24, 3), (24, 36, 4), (34, 20, 3)):
            for y in range(0, ln):
                w = wd * (1 - y / ln) + .4
                for dx in range(-int(w), int(w) + 1):
                    F.set(sx + dx, y, cols[0] if dx < -w * .3 else cols[2] if dx > w * .4 else cols[1])
            gy = (k * 4 + sx) % ln
            F.set(sx, gy, "white")
            F.set(sx, ln, "white") if k % 4 == 0 else None
        out.append(F)
    return out


def spring_bubbles():
    r = random.Random(17); pts = [(r.uniform(10, 38), r.uniform(26, 40), r.randrange(8)) for _ in range(9)]
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        F.disk(24, 40, 13, ["mp_teal_lo", "mp_teal_lo", "mp_teal"], sq=.35)
        for (x, y, p) in pts:
            b = (k + p) % 8; yy = y - b * 1.5; xx = x + math.sin((b + p)) * .8
            if b in (1, 2, 3):
                F.set(xx, yy, "mp_fizz")
            elif b in (4, 5):
                F.set(xx, yy, "mp_teal_hi"); F.set(xx + 1, yy, "mp_fizz")
            elif b == 6:
                F.star(xx, yy, 1, "white", "mp_teal_hi")
        for j in range(4):
            b = (k + j * 2) % 8
            F.set(20 + j * 3 + math.sin(b) * 2, 22 - b * 1.6, "mp_fizz" if b < 5 else "mp_ash_hi")             # steam
        out.append(F)
    return out


def steam():
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        for j in range(5):
            t = ((k / 8) + j * .2) % 1; rr = 2 + t * 5
            F.disk(24 + math.sin(j * 2.3 + t * 4) * 6, 44 - t * 38, rr, ["mp_ash_hi", "mp_ash"] if t < .8 else ["mp_ash"], sq=1)
        out.append(F)
    return out


def amber_orb():
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        cy = 22 + [0, 0, 1, 1, 0, 0, -1, -1][k]
        F.disk(24, cy, 5, ["mp_lava_lo", "mp_lava", "mp_ember"], sq=1)
        F.disk(24, cy - 1, 2.6, ["mp_lava_hi", "mp_glass"], sq=1)
        F.set(24, cy - 1, "white"); F.set(22, cy - 3, "white")
        for j in range(3):
            a = k / 8 * math.tau + j * 2.1
            F.set(24 + math.cos(a) * 9, cy + math.sin(a) * 6, "mp_lava_hi")
        for j in range(3):
            F.set(24 + (j - 1) * 2, cy + 8 + j * 3, "mp_lava_lo")
        for yy in range(0, cy - 5):
            F.set(24, yy, "mp_ash_hi" if yy % 2 else "mp_ash")                  # the chain it hangs on
        out.append(F)
    return out


# ------------------------------------------------------------------ spells / boss fx
def ring_pulse(cols, base, grow, n=8, dots=2, spokes=0):
    def f():
        out = []
        for k in range(n):
            F = H.Fx(CELL)
            a = base + grow * k / (n - 1)
            F.ring(23.5, 23.5, a, a * .62, cols[1], dots=dots)
            F.ring(23.5, 23.5, a * .62, a * .4, cols[0], dots=dots + 1, start=k)
            for j in range(spokes):
                ang = j * math.tau / spokes + k * .1
                F.star(23.5 + math.cos(ang) * a, 23.5 + math.sin(ang) * a * .62, 1, "white", cols[0])
            out.append(F)
        return out
    return f


def fire_wave():
    """Fire Wave: a crescent wall of flame sweeping right (flip for direction)"""
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        x0 = 6 + k * 3.2
        for y in range(8, 40):
            t = (y - 24) / 16
            bx = x0 + 12 * (1 - t * t)
            wd = 5 * (1 - abs(t) * .5) * (1 + .15 * math.sin(k + y * .5))
            for x in range(int(bx - wd), int(bx + 1)):
                d = (bx - x) / max(wd, 1)
                F.set(x, y, "white" if d < .15 else "mp_lava_hi" if d < .4 else "mp_lava" if d < .75 else "mp_lava_lo")
        for j in range(5):
            F.set(x0 + 14 + j, 10 + (j * 7 + k * 3) % 28, "mp_lava_hi")
        out.append(F)
    return out


def magma_pool():
    out = []
    r = random.Random(23)
    for k in range(6):
        F = H.Fx(CELL)
        rr = 18 + [0, 1, 0, -1, 0, 1][k]
        for y in range(CELL):
            for x in range(CELL):
                d = math.hypot(x - 24, (y - 24) / .62) / rr
                if d <= 1:
                    c = "mp_lava_hi" if d < .35 and (x + y + k) % 3 else "mp_lava" if d < .72 else "mp_lava_lo" if d < .94 else "mp_lava_dk"
                    F.set(x, y, c)
        for j in range(4):
            a = j * 1.6 + k * .5
            F.disk(24 + math.cos(a) * 8, 24 + math.sin(a) * 5, 1.6, ["mp_lava_hi", "mp_lava_hi"], sq=.7)             # bubbles
        out.append(F)
    return out


def ember_swarm():
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        for j in range(18):
            a = j * 2.4 + k * .8; rr = 5 + (j * 3) % 17
            x, y = 24 + math.cos(a) * rr, 24 + math.sin(a) * rr * .8 - (j % 4)
            F.set(x, y, "mp_lava_hi" if j % 3 == 0 else "mp_lava"); F.set(x - math.sin(a), y + math.cos(a), "mp_lava_lo")
            if j % 6 == 0:
                F.star(x, y, 1, "white", "mp_lava_hi")
        out.append(F)
    return out


def flame_ward():
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        for j in range(26):
            a = j / 26 * math.tau + k * .2
            x, y = 24 + math.cos(a) * 17, 26 + math.sin(a) * 12
            h = 3 + 2 * math.sin(j * 1.7 + k)
            for yy in range(int(h)):
                F.set(x + math.sin(yy + k + j) * .6, y - yy, "white" if yy == 0 else "mp_lava_hi" if yy < h * .5 else "mp_lava" if yy < h * .8 else "mp_lava_lo")
        out.append(F)
    return out


def fire_pillar():
    """Vharzul's fire pillar: erupts from a ground ring, a column of flame with a white core (billboard, pivot at the base)"""
    out = []
    prof = [4, 10, 18, 26, 32, 34, 30, 22]
    for k in range(8):
        F = H.Fx(CELL)
        F.ring(23.5, 42, 14, 5, "mp_lava", dots=1)
        h = prof[k]
        for y in range(int(h)):
            t = y / max(h, 1); w = 7 * (1 - t * .5) * (1 + .15 * math.sin(k + y * .6))
            for dx in range(-int(w), int(w) + 1):
                d = abs(dx) / max(w, 1)
                F.set(23.5 + dx + math.sin(y * .3 + k) * 1.5, 44 - y, "white" if d < .3 and t < .7 else "mp_lava_hi" if d < .55 else "mp_lava" if d < .85 else "mp_lava_lo")
        for j in range(4):
            F.set(23.5 + math.sin(k + j * 2) * 11, 44 - h - 2 + (j * 3 + k) % 6, "mp_lava_hi")
        out.append(F)
    return out


def crown_flare():
    out = []
    for k in range(6):
        F = H.Fx(CELL)
        a = [.4, .7, 1.0, .9, .7, .5][k]
        for j in range(9):
            x = 8 + j * 4; h = (10 + 8 * math.sin(j * 1.9 + k)) * a
            for y in range(int(h)):
                t = y / max(h, 1)
                F.set(x + math.sin(y * .5 + k + j) * 1.2, 36 - y, "white" if t < .3 else "mp_lava_hi" if t < .6 else "mp_lava" if t < .85 else "mp_lava_lo")
        for j in range(7):
            F.star(8 + (j * 6 + k * 3) % 34, 4 + (j * 5 + k * 2) % 14, 1, "white", "mp_lava_hi")
        out.append(F)
    return out


def hound_summon():
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        a = 6 + k * 1.6
        F.ring(23.5, 30, a, a * .55, "mp_lava", dots=2)
        F.ring(23.5, 30, a * .6, a * .33, "mp_lava_hi", dots=3, start=k)
        for j in range(8):
            ang = j * math.tau / 8 + k * .5
            F.set(23.5 + math.cos(ang) * a * .8, 30 + math.sin(ang) * a * .45, "mp_lava_hi")
        for y in range(int(k * 2.2)):
            for dx in (-1, 0, 1):
                F.set(23.5 + dx * 3 + math.sin(y + k) * 1.2, 30 - y, "mp_lava" if abs(dx) else "mp_lava_hi")
        out.append(F)
    return out


def molten_fist():
    out = []
    for k in range(6):
        F = H.Fx(CELL)
        rr = 18 - k * 2
        F.ring(23.5, 23.5, rr + 2, (rr + 2) * .62, "mp_lava_lo", dots=2)
        F.ring(23.5, 23.5, rr, rr * .62, "mp_lava_hi" if k % 2 else "mp_lava", dots=1)
        F.star(23.5, 23.5, 2 + k // 2, "white", "mp_lava_hi", "mp_lava")
        out.append(F)
    return out


def warden_lamp():
    """one of the three Warden's lamps (P3): a lamp-flame that relights -- violet shrine flame turning to warm gold"""
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        cols = NV if k < 3 else LV
        for y in range(14, 40):
            t = (40 - y) / 26
            w = 5 * math.sin(math.pi * min(1, t * 1.1)) ** .7 * (1 - t * .5) * (1 + .12 * math.sin(k + y * .4))
            for dx in range(-int(w), int(w) + 1):
                d = abs(dx) / max(w, 1)
                F.set(23.5 + dx + math.sin(y * .3 + k) * 1.2, y, "white" if d < .25 and t < .5 else cols[0] if d < .5 else cols[1] if d < .8 else cols[2])
        out.append(F)
    return out


FX = {
    # --- ground pools (decals)
    "pool_lava": {"fn": lambda: H.pool_frames(LV, CELL, 6, "mp_lava", rmax=22), "fps": 4, "kind": "decal", "lift": 0.02, "pivot": [24, 24], "notes": "lava glow pool (radius ~4 m) along lava channels / falls; warm flicker"},
    "pool_forge": {"fn": lambda: H.pool_frames(EM, CELL, 6, "mp_forge", rmax=18), "fps": 4, "kind": "decal", "lift": 0.02, "pivot": [24, 24], "notes": "warm orange pool under every window and doorway; off stairs and spawns"},
    "pool_cold": {"fn": lambda: H.pool_frames(NB, CELL, 6, "mp_cold", rmax=22), "fps": 4, "kind": "decal", "lift": 0.02, "pivot": [24, 24], "notes": "neon cold-fire pool (Cold Seam, cold braziers)"},
    "pool_violet": {"fn": lambda: H.neon_pool_frames("violet", CELL, 6, rmax=20), "fps": 4, "kind": "decal", "lift": 0.02, "pivot": [24, 24], "notes": "violet pool under shrine-lamps (Sigil Forge, spring grotto)"},
    "pool_teal": {"fn": lambda: H.pool_frames(TE, CELL, 6, "mp_teal", rmax=20), "fps": 4, "kind": "decal", "lift": 0.03, "pivot": [24, 24], "notes": "clear teal glow over the hidden bubbly springs"},
    "lava_crawl": {"fn": lava_crawl, "fps": 3, "kind": "decal", "lift": 0.03, "pivot": [24, 24], "notes": "48 px emissive lava tile, 4-frame slow crawl; tile over lava channels / rivers (2 m per tile)"},
    "burn_patch": {"fn": burn, "fps": 6, "kind": "decal", "lift": 0.02, "pivot": [24, 24], "notes": "ember-storm burn patch (2 dmg/s) and Kindle's ember_dash scorch; read as a hazard, keep off spawns and stairs"},
    "frost_vein": {"fn": frost_vein, "fps": 2, "kind": "decal", "lift": 0.03, "pivot": [24, 24], "notes": "Cold Seam frost-vein crack, pulses slowly (neon blue on orange rock)"},
    # --- billboards: motes, weather, flames
    "ember_motes": {"fn": rise(LV, 5), "fps": 6, "kind": "billboard", "lift": 0.4, "pivot": [24, 47], "notes": "ember motes drifting up (20 per screen), heavier in ash fall"},
    "neon_embers": {"fn": rise(NR, 9, n=10), "fps": 6, "kind": "billboard", "lift": 0.5, "pivot": [24, 47], "notes": "neon red embers rising off forges / lava falls"},
    "ash_fall": {"fn": ash_fall, "fps": 6, "kind": "billboard", "lift": 0.0, "pivot": [24, 47], "notes": "ash fall weather layer (tile / overlay), a few glowing flakes"},
    "ember_storm": {"fn": ember_storm, "fps": 8, "kind": "billboard", "lift": 0.0, "pivot": [24, 47], "notes": "ember storm weather layer: wind-driven streaks; spawn burn_patch decals under it"},
    "heat_shimmer": {"fn": shimmer, "fps": 6, "kind": "billboard", "lift": 0.0, "pivot": [24, 47], "notes": "heat shimmer over the Red arch / furnace mouths"},
    "forge_flame": {"fn": lambda: flame(FL[1:]), "fps": 10, "kind": "billboard", "lift": 0.1, "pivot": [24, 44], "light": {"color": "mp_lava", "intensity": 1.1, "range": 4.0, "pool": "pool_forge"}, "notes": "forge / brazier flame (warm), the Spice-brazier stalls and furnace hall"},
    "cold_flame": {"fn": lambda: flame(NB), "fps": 10, "kind": "billboard", "lift": 0.1, "pivot": [24, 44], "light": {"color": "neon_blue", "intensity": 1.0, "range": 4.0, "pool": "pool_cold"}, "notes": "cold-fire flame (no heat): wedges, cold braziers, the Cold Seam"},
    "violet_flame": {"fn": lambda: flame(NV), "fps": 10, "kind": "billboard", "lift": 0.1, "pivot": [24, 44], "light": {"color": "neon_violet", "intensity": 0.9, "range": 3.5, "pool": "pool_violet"}, "notes": "violet shrine-lamp flame (Warden's hall, spring grotto)"},
    "lava_fall": {"fn": lava_fall, "fps": 8, "kind": "billboard", "lift": 0.0, "pivot": [24, 47], "light": {"color": "mp_lava", "intensity": 1.2, "range": 4.0, "pool": "pool_lava"}, "notes": "molten fall ribbon (16 px wide, tile vertically down the Lavafalls cliffs), splash at the foot"},
    "steam_puff": {"fn": steam, "fps": 6, "kind": "billboard", "lift": 0.0, "pivot": [24, 47], "notes": "steam puffs: spring edges, quench tanks, vents"},
    "spring_bubbles": {"fn": spring_bubbles, "fps": 6, "kind": "billboard", "lift": 0.0, "pivot": [24, 44], "notes": "clear bubbling spring: fizz + steam over a teal pool (mp_spring / lf_spring / cd_spring; never murky)"},
    # --- neon life
    "neon_fireflies_blue": {"fn": fireflies(NB, 3), "fps": 6, "kind": "billboard", "lift": 0.8, "pivot": [24, 47], "notes": "cold-blue fireflies"},
    "neon_fireflies_violet": {"fn": fireflies(NV, 4), "fps": 6, "kind": "billboard", "lift": 0.8, "pivot": [24, 47], "notes": "violet fireflies (spring grotto, Sigil Forge)"},
    "neon_fireflies_red": {"fn": fireflies(NR, 6), "fps": 6, "kind": "billboard", "lift": 0.8, "pivot": [24, 47], "notes": "red-gold fire motes that wander (not rising)"},
    "glow_frog_blue": {"fn": lambda: frog(NB), "fps": 6, "kind": "billboard", "lift": 0.0, "pivot": [24, 44], "notes": "glowing frog, cold-fire blue spots (sits by springs and the Cold Seam; never gross)"},
    "glow_frog_violet": {"fn": lambda: frog(NV), "fps": 6, "kind": "billboard", "lift": 0.0, "pivot": [24, 44], "notes": "glowing frog, violet spots (spring grotto)"},
    "glow_vines_blue": {"fn": lambda: vines(NB), "fps": 4, "kind": "billboard", "lift": 3.0, "pivot": [24, 0], "notes": "hanging ash-vines with blue glow beads, hang from cave / arch ceilings (pivot at top)"},
    "glow_vines_violet": {"fn": lambda: vines(NV), "fps": 4, "kind": "billboard", "lift": 3.0, "pivot": [24, 0], "notes": "hanging vines with violet glow beads"},
    "glow_crystals_blue": {"fn": lambda: crystals(NB), "fps": 4, "kind": "billboard", "lift": 3.0, "pivot": [24, 0], "notes": "hanging cold-blue glow crystals (Cold Seam, Caldera ceilings)"},
    "glow_crystals_violet": {"fn": lambda: crystals(NV), "fps": 4, "kind": "billboard", "lift": 3.0, "pivot": [24, 0], "notes": "hanging violet crystals (springs of glass)"},
    "glow_orb_amber": {"fn": amber_orb, "fps": 6, "kind": "billboard", "lift": 2.6, "pivot": [24, 22], "light": {"color": "mp_ember", "intensity": 0.8, "range": 3.5, "pool": "pool_forge"}, "notes": "molten-glass globe on a chain over streets (#ffb066, steady); pivot at the globe centre"},
    # --- spells / boss
    "fire_wave": {"fn": fire_wave, "fps": 12, "kind": "billboard", "lift": 0.4, "pivot": [24, 40], "loop": False, "notes": "Fire Wave (crescent of flame, sweeps right; flip for left)"},
    "magma_pool": {"fn": magma_pool, "fps": 6, "kind": "decal", "lift": 0.03, "pivot": [24, 24], "light": {"color": "mp_lava", "intensity": 1.0, "range": 3.0}, "notes": "Magma Pool (damaging ground pool, r ~ 2-3 m; also Vharzul's rising lava edge when tiled)"},
    "ember_swarm": {"fn": ember_swarm, "fps": 12, "kind": "billboard", "lift": 0.8, "pivot": [24, 30], "notes": "Ember Swarm: a cloud of orbiting embers"},
    "flame_ward": {"fn": flame_ward, "fps": 10, "kind": "billboard", "lift": 0.0, "pivot": [24, 38], "notes": "Flame Ward: a ring of small flames around the caster (shield)"},
    "hound_summon": {"fn": hound_summon, "fps": 10, "kind": "billboard", "lift": 0.0, "pivot": [24, 30], "loop": False, "notes": "Magma Hound summon / alpha's call: a lava ring with a column rising"},
    "warm_ring_orange": {"fn": ring_pulse(LV, 6, 18, spokes=6), "fps": 8, "kind": "decal", "lift": 0.03, "pivot": [24, 24], "loop": False, "notes": "generic heat / heal ring (Kindle also has her own in pets/kindle_fx)"},
    "pillar_telegraph": {"fn": ring_pulse(NR, 14, 4, n=6, dots=1, spokes=8), "fps": 8, "kind": "decal", "lift": 0.03, "pivot": [24, 24], "notes": "Vharzul P1: the floor ring shown before a fire pillar (2 s), then fire_pillar"},
    "fire_pillar": {"fn": fire_pillar, "fps": 12, "kind": "billboard", "lift": 0.0, "pivot": [24, 44], "loop": False, "light": {"color": "mp_lava", "intensity": 1.4, "range": 4.0}, "notes": "Vharzul fire pillar erupting (damage frames 4-6)"},
    "crown_flare": {"fn": crown_flare, "fps": 10, "kind": "billboard", "lift": 0.0, "pivot": [24, 36], "loop": False, "notes": "Vharzul P3 crown flare, put over his head (scale with 8x)"},
    "molten_fist": {"fn": molten_fist, "fps": 8, "kind": "decal", "lift": 0.03, "pivot": [24, 24], "loop": False, "notes": "Kilnmother molten-fist telegraph: a shrinking ring converging on the impact point"},
    "warden_lamp": {"fn": warden_lamp, "fps": 8, "kind": "billboard", "lift": 0.0, "pivot": [24, 44], "loop": False, "light": {"color": "mp_ember", "intensity": 1.0, "range": 4.0}, "notes": "Vharzul P3: a Warden's lamp relighting (violet shrine flame turns warm gold); put over each of the three lamps"},
}
for _c in ("blue", "violet", "red"):
    FX[f"glow_orb_{_c}"] = {"fn": (lambda c=_c: H.glow_orb_frames(c, CELL)), "fps": 6, "kind": "billboard", "lift": 1.4, "pivot": [24, 33],
                            "light": {"color": f"neon_{_c}_hi", "intensity": 0.7, "range": 3.0, "pool": {"blue": "pool_cold", "violet": "pool_violet", "red": "pool_lava"}[_c]},
                            "notes": "floating glow orb, hover 1.1-2.2 m"}
