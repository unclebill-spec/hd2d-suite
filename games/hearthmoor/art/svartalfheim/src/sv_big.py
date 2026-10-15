"""Svartalfheim mini-boss, rares and the runaway construct, drawn natively at their game scale (boss_sheet format, palette
only; their glow comes from fx + lights):
  The Foreman        56x90  = 2.8x  (Clockwork Deep C4 mini-boss)
  Amethyst Basilisk  96x80  = 2.5x  (rare; crystal lizard)
  Soot Colossus      64x90  = 2.8x  (rare; soot elemental)
  Runaway construct  40x64  = 2.0x  (Bifrost gate foe)"""
import math

from sv_common import rect
from sv_boss import Safe, ellf, hsh, fire


def brass(u, v=0.0):
    if v < -0.8:
        return "plaster_hi"
    return "flower_gold" if u < -0.5 else "timber_hi" if u < 0.25 else "timber"


def tl(S, x0, y0, x1, y1, w, fn):
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    L = max(0.01, math.hypot(x1 - x0, y1 - y0))
    nx, ny = -(y1 - y0) / L, (x1 - x0) / L
    for j in range(n):
        t = j / max(1, n - 1)
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        r = w / 2
        for dy in range(-int(r) - 1, int(r) + 2):
            for dx in range(-int(r) - 1, int(r) + 2):
                if dx * dx + dy * dy <= r * r:
                    d = (dx * nx + dy * ny) / max(r, 1)
                    c = fn(d) if callable(fn) else fn
                    S.set(x + dx, y + dy, c)


def frost(S, cx, cy, k=0, n=7, r=4):
    """rime frost-flowers (Veyra's frost): white / sky crystals"""
    for j in range(n):
        a = j / n * math.tau + k * 0.3
        d = r * (0.4 + 0.6 * hsh("fr", j, cx))
        x, y = cx + math.cos(a) * d, cy + math.sin(a) * d * 0.7
        S.set(x, y, "white" if j % 2 else "sky")
    S.set(cx, cy, "white"); S.set(cx - 1, cy, "sky"); S.set(cx + 1, cy, "sky"); S.set(cx, cy - 1, "sky")


def grate(S, x0, y0, x1, y1, k, hot=1.0, cracked=False):
    """a furnace belly grate: dark frame, glowing bars of forge fire"""
    rect(S, x0, y0, x1, y1, "roof_lo")
    for y in range(y0 + 1, y1):
        for x in range(x0 + 1, x1):
            if (y - y0) % 2 == 1:
                S.set(x, y, fire(x, y, k, hot * 1.2))
    if cracked:
        for j in range(6):
            S.set(x0 - 1 - j // 2, y0 + 1 + j, fire(x0, y0 + j, k, 1.4))
            S.set(x1 + 1 + j // 3, y1 - j, fire(x1, y1 - j, k, 1.4))


# ============================================================== The Foreman (2.8x)
FW_, FH_ = 56, 90


def foreman(s, face, anim, i):
    """tall brass overseer construct: a whistle-chimney head with a gauge face and two lamp eyes, a riveted barrel torso, a
    furnace belly (weak point), a clipboard welded to the left arm, a clamp hand, frost on the right shoulder, piston legs"""
    S = Safe(s)
    CX, G = 28, FH_ - 2
    side, up = face == "left", face == "up"
    b = [0, 1, 1, 0][i] if anim == "idle" else [0, -1, 0, -1][i] if anim == "walk" else [0, -1, 2, 0][i] if anim == "attack" else 0
    k = i
    if anim == "die" and i >= 2:
        # collapsed: barrel on its side, the chimney fallen off, belly embers
        ellf(S, CX, G - 8, 18, 8, lambda x, y, u, v: brass(u, v))
        grate(S, CX - 4, G - 12, CX + 4, G - 6, k, 0.8 if i == 3 else 1.1)
        tl(S, CX + 10, G - 4, CX + 24, G - 10, 5, lambda d: "stone_lo" if d < 0 else "shadow")
        S.set(CX + 25, G - 11, "flower_gold"); S.set(CX + 26, G - 12, "plaster_hi")
        ellf(S, CX - 18, G - 3, 6, 3, lambda x, y, u, v: "plaster" if u < 0.3 else "plaster_lo")     # the clipboard
        for x in range(CX - 21, CX - 15, 2):
            S.set(x, G - 3, "stone_lo")
        rect(S, CX - 20, G, CX + 20, G, "shadow")
        if i == 2:
            for j in range(5):
                S.set(CX - 10 + j * 5, G - 18 - (j % 2) * 3, "plaster_hi")
        return
    if anim == "die":
        b = 3 + i * 4
    # legs (pistons)
    st = [0, 2, 0, -2][i] if anim == "walk" else 0
    for sd in (-1, 1):
        lx = CX + sd * 7 + (st * sd if not side else st * sd)
        tl(S, lx, 56 + b, lx, G - 4, 5, lambda d: "stone" if d < -0.4 else "stone_lo" if d < 0.4 else "shadow")
        tl(S, lx, 56 + b, lx, 70 + b, 7, lambda d: brass(d))
        rect(S, lx - 5, G - 3, lx + 5, G, "timber_lo"); rect(S, lx - 5, G - 3, lx + 5, G - 3, "timber")
    # torso barrel
    ty = 26 + b
    cxb = CX + (-1 if side else 0)
    ellf(S, cxb, ty + 16, 14 if not side else 12, 18, lambda x, y, u, v: brass(u, v))
    for yy in (ty + 2, ty + 30):
        for x in range(cxb - 12, cxb + 13):
            S.set(x, yy, "timber_lo")
    for x in range(cxb - 10, cxb + 11, 4):
        S.set(x, ty + 4, "plaster_hi"); S.set(x, ty + 28, "plaster_hi")
    if not up:
        gx = cxb - (3 if side else 0)
        grate(S, gx - 6, ty + 14, gx + 6, ty + 24, k, 1.0 + (0.4 if anim == "attack" else 0))
    else:
        rect(S, cxb - 3, ty + 8, cxb + 3, ty + 26, "timber_lo")
        for y in range(ty + 9, ty + 26, 3):
            S.set(cxb, y, "flower_gold")
    # frost on the right shoulder (screen left from the front)
    fsx = cxb - 12 if face == "down" else cxb + 10
    if side:
        fsx = cxb + 6
    frost(S, fsx, ty + 2, k, 9, 5)
    # arms: clipboard arm and clamp arm
    raise_ = [0, 6, -4, 0][i] if anim == "attack" else 0
    for sd in ((-1, 1) if not side else (-1,)):
        shx = cxb + sd * 14 if not side else cxb - 4
        hx, hy = shx + sd * 4 - (6 if side else 0), ty + 32 - raise_ * (1 if sd > 0 or side else 0)
        tl(S, shx, ty + 6, hx, hy, 4, lambda d: "stone_lo" if d < 0.3 else "shadow")
        ellf(S, shx, ty + 6, 4, 4, lambda x, y, u, v: brass(u, v))
        clip = (sd < 0) if face == "down" else (sd > 0) if face == "up" else False
        if clip:                                             # the clipboard welded on
            rect(S, hx - 4, hy - 2, hx + 3, hy + 8, "plaster")
            rect(S, hx - 4, hy - 2, hx + 3, hy - 2, "timber_lo"); S.set(hx, hy - 3, "stone_hi")
            for yy in range(hy, hy + 8, 2):
                for x in range(hx - 3, hx + 2):
                    if (x + yy) % 3:
                        S.set(x, yy, "stone_lo")
            S.set(hx + 2, hy + 1, "roof_hi")
        else:                                                # a clamp hand
            S.set(hx - 1, hy + 1, "stone_hi"); S.set(hx + 1, hy + 1, "stone_hi"); S.set(hx - 1, hy + 2, "stone"); S.set(hx + 1, hy + 2, "stone")
    if side:                                                 # side: clipboard held out front
        rect(S, cxb - 16, ty + 24 - raise_, cxb - 9, ty + 34 - raise_, "plaster")
        for yy in range(ty + 26 - raise_, ty + 34 - raise_, 2):
            for x in range(cxb - 15, cxb - 10):
                S.set(x, yy, "stone_lo")
    # head: whistle-chimney
    hx = cxb - (2 if side else 0)
    hy = ty - 4
    rect(S, hx - 6, hy - 14, hx + 6, hy, "timber_hi")
    for y in range(hy - 14, hy + 1):
        S.set(hx - 6, y, "flower_gold"); S.set(hx + 6, y, "timber")
    rect(S, hx - 7, hy - 15, hx + 7, hy - 14, "timber_lo")
    rect(S, hx - 2, hy - 21, hx + 2, hy - 16, "stone_lo"); S.set(hx - 2, hy - 20, "stone")        # the whistle
    rect(S, hx - 3, hy - 22, hx + 3, hy - 22, "stone")
    if not up:                                              # a gauge face with lamp eyes
        ex = (hx - 3, hx + 2) if face == "down" else (hx - 5, hx - 2)
        for x in ex:
            rect(S, x, hy - 10, x + 1, hy - 9, "lamp"); S.set(x, hy - 10, "white")
        rect(S, hx - 3, hy - 5, hx + 3, hy - 4, "shadow") if face == "down" else rect(S, hx - 6, hy - 5, hx - 1, hy - 4, "shadow")
        S.set(hx, hy - 5, "plaster_hi") if face == "down" else None
    # steam: whistles (attack), idle wisps
    if anim == "attack" and i in (1, 2):
        for j in range(10):
            a = -math.pi / 2 + (j - 4.5) * 0.18 + (-0.7 if side else 0)
            r = 4 + j * 1.6 + i * 3
            S.set(hx + math.cos(a) * r, hy - 22 + math.sin(a) * r, "white" if j % 2 else "plaster_hi")
    elif i % 2 == 0:
        S.set(hx + 1, hy - 25, "plaster_hi"); S.set(hx, hy - 27, "white")


# ============================================================== Amethyst Basilisk (2.5x)
BW_, BH_ = 96, 80


def spine(S, x, y, h, tilt, k, j, w0=3.6):
    """one faceted crystal shard: lit facet sky / flower_blue, shade facet cloth, a rose tip with a white glint
    (amethyst approximated in the cozy palette; the neon violet glow is the basilisk_glow light + crystal_sparkle fx)"""
    for t in range(int(h)):
        f = t / max(1, h)
        w = w0 * (1 - f) ** 0.8 + 0.5
        cxs = x + tilt * f * h * 0.5
        for dx in range(-int(w), int(w) + 1):
            if f > 0.82:
                c = "flower_rose"
            elif dx < 0:
                c = "sky" if dx == -int(w) and f > 0.2 else "flower_blue"
            else:
                c = "cloth" if dx > 0 else "flower_blue"
            S.set(cxs + dx, y - t, c)
    S.set(x + tilt * h * 0.5, y - h, "white" if (k + j) % 3 else "flower_rose")


def basilisk(s, face, anim, i):
    """a long crystal lizard: basalt-dark scales, a ridge of violet crystal spines glowing at the tips, crystal crusts, lamp
    eyes; gaze = eyes flare white (attack frame 14); tail sweep; die = the spines crack and it slumps"""
    S = Safe(s)
    CX, G = 48, BH_ - 2
    k = i
    b = [0, 1, 1, 0][i] if anim == "idle" else [0, -1, 0, -1][i] if anim == "walk" else 0
    dead = anim == "die"
    sl = [2, 6, 12, 14][i] if dead else 0
    gaze = anim == "attack" and i in (1, 2)
    def scales(x, y, u, v):
        c = "stone_lo" if v < -0.3 else "shadow" if v < 0.5 else "timber_lo"
        if (x * 3 + y * 5) % 11 == 0:
            c = "stone"
        return c
    if dead and i >= 2:                                      # slumped flat on its belly: body rests on the ground rows
        body_y0 = G - 12
        ellf(S, CX + (2 if face == "left" else 0), body_y0, 30 if face == "left" else 26, 10, scales)
        rect(S, CX - 26, G - 1, CX + 26, G, "timber_lo")
    if face == "left":
        body_y = 52 + b + sl // 2 if not (dead and i >= 2) else G - 14
        # legs (4) symmetric about CX
        st = [0, 3, 0, -3][i] if anim == "walk" else 0
        for j, lx in enumerate((CX - 22, CX - 10, CX + 10, CX + 22)):
            off = st if j % 2 == 0 else -st
            if dead and i >= 2:
                continue
            kx, ky = lx + off + (4 if j < 2 else -4) * 0 + 3, body_y + 12
            tl(S, lx, body_y + 4, kx, ky, 6, lambda d: "stone_lo" if d < -0.3 else "shadow")
            tl(S, kx, ky, lx + off - 3, G - 2, 5, lambda d: "shadow" if d < 0.3 else "timber_lo")
            rect(S, lx + off - 7, G - 1, lx + off + 1, G, "shadow")
            S.set(lx + off - 7, G - 1, "stone"); S.set(lx + off - 5, G - 1, "stone")
        # tail sweeping behind (right), raised so it stays off the ground rows
        sweep = [0, 4, -6, 2][i] if anim == "attack" else [0, 1, 2, 1][i]
        for j in range(30):
            t = j / 29
            x = CX + 26 + t * 18
            y = body_y - 2 - t * 10 + math.sin(t * 3 + sweep * 0.3) * 4 - sweep * t
            ellf(S, x, y, 5 * (1 - t) + 1, 4 * (1 - t) + 1, scales)
        # body
        ellf(S, CX + 2, body_y, 30, 11 - sl // 4, scales)
        for x in range(CX - 24, CX + 28):
            S.set(x, body_y + 9 - sl // 4, "timber_lo")
        # head + jaw (left)
        hx, hy = CX - 32, body_y - 4 + (2 if gaze else 0)
        ellf(S, hx, hy, 10, 7, scales)
        tl(S, hx - 9, hy + 2, hx - 18, hy + 4, 5, lambda d: "stone_lo" if d < 0 else "shadow")
        for x in range(hx - 18, hx - 4):
            S.set(x, hy + 4, "timber_lo")
        rect(S, hx - 6, hy - 3, hx - 4, hy - 1, "lamp" if not dead else "stone_lo")
        S.set(hx - 6, hy - 3, "white")
        if gaze:
            rect(S, hx - 7, hy - 4, hx - 3, hy, "white"); S.set(hx - 5, hy - 2, "lamp")
            for j in range(8):
                S.set(hx - 9 - j * 2, hy - 2 - j % 2, "flower_gold" if j % 2 else "white")
        # crystal spines along the ridge (tallest mid-back), crusts on the flank
        for j in range(11):
            t = j / 10
            x = CX - 22 + t * 48 + (hsh("bx", j) - 0.5) * 4
            h = (10 + 24 * math.sin(t * math.pi)) * (0.65 + 0.55 * hsh("bh", j)) * (1 - sl / 30)
            if dead and i == 3 and j % 2:
                h *= 0.4
            spine(S, x, body_y - 7, h, -0.5 + t + (hsh("bt", j) - 0.5) * 0.8, k, j, 2.6 + 2 * hsh("bw", j))
        for (dx, dy) in ((-10, 2), (6, 4), (18, 1)):
            S.set(CX + dx, body_y + dy, "flower_blue"); S.set(CX + dx + 1, body_y + dy, "flower_rose"); S.set(CX + dx, body_y + dy - 1, "sky")
        if dead and i == 3:
            for j in range(6):
                S.set(CX - 20 + j * 8, G - 1, "flower_rose" if j % 2 else "flower_blue")
        return
    # front / back: the lizard head-on (down) or from behind (up): a low wide body, crest fanning up
    body_y = 54 + b + sl // 2 if not (dead and i >= 2) else G - 14
    st = [0, 2, 0, -2][i] if anim == "walk" else 0
    for sd in (-1, 1):
        for lx in (CX + sd * 16, CX + sd * 26):
            off = st * sd
            if dead and i >= 2:
                continue
            tl(S, lx, body_y, lx + sd * 4, G - 2 - (2 if lx == CX + sd * 26 and off > 0 else 0), 6, lambda d: "shadow" if d < 0.3 else "timber_lo")
            rect(S, lx + sd * 4 - 4, G - 1, lx + sd * 4 + 4, G, "shadow")
    ellf(S, CX, body_y, 26, 12 - sl // 4, scales)
    for j in range(11):
        t = j / 10
        x = CX - 24 + t * 48 + (hsh("fx", j) - 0.5) * 4
        h = (10 + 24 * math.sin(t * math.pi)) * (0.65 + 0.55 * hsh("fh", j)) * (1 - sl / 30)
        spine(S, x, body_y - 7, h, (t - 0.5) * 1.8 + (hsh("ft", j) - 0.5) * 0.6, k, j, 2.6 + 2 * hsh("fw", j))
    if face == "down":
        hy = body_y + 2 + (2 if gaze else 0)
        ellf(S, CX, hy, 11, 8, scales)
        rect(S, CX - 8, hy + 5, CX + 8, hy + 5, "timber_lo")
        for ex in (CX - 6, CX + 4):
            rect(S, ex, hy - 3, ex + 2, hy - 1, "lamp" if not dead else "stone_lo"); S.set(ex, hy - 3, "white")
            if gaze:
                rect(S, ex - 1, hy - 4, ex + 3, hy, "white"); S.set(ex + 1, hy - 2, "lamp")
        if gaze:
            for j in range(6):
                S.set(CX - 8 - j, hy + 1 + j, "flower_gold"); S.set(CX + 8 + j, hy + 1 + j, "flower_gold")
    else:
        for j in range(16):                                   # tail straight back toward the camera-far side
            S.set(CX, body_y + 10 + j // 2, "shadow")
        ellf(S, CX, body_y + 14, 4, 5, scales)


# ============================================================== Soot Colossus (2.8x)
SW_, SH_ = 64, 90


def sootcolossus(s, face, anim, i):
    """a towering soot elemental: billowing smoke body, cinders, a glowing ember core in the chest, ember eyes, huge smoky
    fists; attack = both fists smother-slam (frame 14) with a soot puff; die = disperses into smoke, the core gutters out"""
    S = Safe(s)
    CX, G = 32, SH_ - 2
    k = i
    b = [0, -1, -2, -1][i] if anim in ("idle", "walk") else 0
    dead = anim == "die"
    fade = [0, 0.25, 0.55, 0.85][i] if dead else 0
    def smoke(x, y, u, v):
        n = hsh("sm", x // 2, y // 2, k)
        if fade and n < fade:
            return None
        q = u + v
        c = "stone_lo" if q < -0.7 else "shadow" if q < 0.6 else "roof_lo"
        if n > 0.96:
            c = "stone"
        return c
    up = face == "up"
    side = face == "left"
    # swirling smoke column base (wide, symmetric, touching the ground)
    for y in range(58, G + 1):
        t = (y - 58) / (G - 58)
        hw = 10 + 8 * t + math.sin(y * 0.5 + k) * 1.5
        for x in range(int(CX - hw), int(CX + hw) + 1):
            c = smoke(x, y, (x - CX) / hw, 0.3)
            if c:
                S.set(x, y, c)
    # body billows
    cy = 40 + b
    for j, (dx, dy, rx, ry) in enumerate(((0, 0, 18, 22), (-11, -11, 9, 8), (11, -11, 9, 8), (-6, -22, 9, 8), (7, 14, 11, 9), (-9, 14, 10, 9))):
        ellf(S, CX + dx, cy + dy, rx, ry, smoke)
    # head hump + ember eyes
    hx = CX - (3 if side else 0)
    ellf(S, hx, cy - 26, 11, 9, smoke)
    if not up and fade < 0.5:
        for ex in ((hx - 6, hx + 4) if not side else (hx - 8, hx - 3)):
            rect(S, ex, cy - 27, ex + 2, cy - 26, "roof_hi"); S.set(ex + 1, cy - 27, "lamp")
    # ember core
    if not up:
        r = 6 + (k % 2)
        cc = 1.0 - fade
        if cc > 0.1:
            ellf(S, CX - (2 if side else 0), cy - 2, r * cc + 1, (r + 1) * cc + 1,
                 lambda x, y, u, v: "white" if u * u + v * v < 0.2 and not dead else "flower_gold" if u * u + v * v < 0.5 else "lamp" if u * u + v * v < 0.8 else "roof_hi")
    # arms + fists of soot
    raise_ = [0, 16, -10, 0][i] if anim == "attack" else 0
    for sd in ((-1, 1) if not side else (-1,)):
        ax = CX + sd * 19 if not side else CX - 17
        fy = cy + 14 - raise_ + (6 if anim == "attack" and i == 2 else 0)
        for j in range(6):
            t = j / 5
            ellf(S, CX + sd * 12 + (ax - CX - sd * 12) * t, cy - 12 + (fy - cy + 12) * t, 6 - t, 5, smoke)
        ellf(S, ax, fy, 7, 7, smoke)
        for j in range(3):
            S.set(ax - 3 + j * 3, fy - 4, "roof" if (j + k) % 2 else "roof_hi")
    # cinders floating
    for j in range(12):
        x = CX - 26 + hsh("cx", j) * 52
        y = 8 + ((hsh("cy", j) * 60 + k * 5) % 60)
        if S.get(x, y) is None or True:
            S.set(x, y, "lamp" if j % 3 == 0 else "roof_hi" if j % 3 == 1 else "flower_gold")
    if anim == "attack" and i == 2:
        for j in range(16):
            a = math.pi * j / 15
            S.set(CX + math.cos(a) * 28, G - 6 - math.sin(a) * 8, "stone_lo" if j % 2 else "shadow")


# ============================================================== Runaway construct (2x)
RW_, RH_ = 40, 64


def runaway(s, face, anim, i):
    """a big forge construct gone wrong: cracked furnace belly leaking fire, frost flowers on its brass plates, staggering
    (idle lurch), a chain flail arm: 3-hit flail = attack frames 12-14 (wind, swing, smash), 15 recover"""
    S = Safe(s)
    CX, G = 20, RH_ - 2
    k = i
    side, up = face == "left", face == "up"
    lurch = [0, 1, 0, -1][i] if anim == "idle" else 0
    b = [0, 1, 2, 1][i] if anim == "idle" else [0, -1, 0, -1][i] if anim == "walk" else 0
    if anim == "die" and i >= 2:
        ellf(S, CX, G - 6, 15, 6, lambda x, y, u, v: brass(u, v))
        grate(S, CX - 4, G - 9, CX + 4, G - 5, k, 0.7, cracked=True)
        frost(S, CX - 9, G - 8, k, 5, 3); frost(S, CX + 10, G - 6, k + 1, 5, 3)
        for j in range(4):
            S.set(CX - 12 + j * 7, G, "timber_lo")
        rect(S, CX - 16, G, CX + 16, G, "timber_lo")
        return
    if anim == "die":
        b = 3 + 4 * i
    # legs
    st = [0, 2, 0, -2][i] if anim == "walk" else 0
    for sd in (-1, 1):
        lx = CX + sd * 6 + st * sd
        tl(S, lx, 40 + b, lx, G - 3, 5, lambda d: "stone" if d < -0.4 else "stone_lo" if d < 0.4 else "shadow")
        rect(S, lx - 4, G - 2, lx + 4, G, "timber_lo"); rect(S, lx - 4, G - 2, lx + 4, G - 2, "timber")
    # barrel body with a tilt (stagger)
    cx = CX + lurch
    ellf(S, cx, 30 + b, 13 if not side else 11, 13, lambda x, y, u, v: brass(u, v))
    for yy in (18 + b, 42 + b):
        for x in range(cx - 11, cx + 12):
            S.set(x, yy, "timber_lo")
    if not up:
        gx = cx - (2 if side else 0)
        grate(S, gx - 5, 26 + b, gx + 5, 35 + b, k, 1.2, cracked=True)
    frost(S, cx - 8, 22 + b, k, 7, 4); frost(S, cx + 7, 38 + b, k + 2, 6, 3)
    # dome head, cracked visor
    ellf(S, cx, 13 + b, 7, 6, lambda x, y, u, v: brass(u, v))
    if not up:
        rect(S, cx - 5, 13 + b, cx + 4, 14 + b, "shadow") if not side else rect(S, cx - 7, 13 + b, cx - 1, 14 + b, "shadow")
        S.set(cx - 3 if not side else cx - 5, 13 + b, "lamp"); S.set(cx + 2 if not side else cx - 3, 13 + b, "roof_hi")
        S.set(cx + 3, 11 + b, "timber_lo"); S.set(cx + 4, 10 + b, "timber_lo")       # crack in the dome
    frost(S, cx + 3, 9 + b, k, 5, 2)
    rect(S, cx - 1, 4 + b, cx + 1, 7 + b, "stone_lo")
    # arms: left clamp, right chain flail
    ph = i if anim == "attack" else -1
    for sd in ((-1, 1) if not side else (1,)):
        shx = cx + sd * 10 if not side else cx + 2
        if sd < 0:
            tl(S, shx, 22 + b, shx - 4, 36 + b, 4, lambda d: "stone_lo" if d < 0.3 else "shadow")
            S.set(shx - 5, 37 + b, "stone_hi"); S.set(shx - 3, 37 + b, "stone_hi")
            continue
        hand = (shx + 3, 36 + b)
        if ph == 0:
            hand = (shx + 4, 14 + b)
        elif ph in (1, 2):
            hand = (shx - 2 if not side else shx - 10, 30 + b)
        tl(S, shx, 22 + b, hand[0], hand[1], 4, lambda d: "stone_lo" if d < 0.3 else "shadow")
        ellf(S, shx, 22 + b, 3, 3, lambda x, y, u, v: brass(u, v))
        # chain + spiked ball
        if ph < 0:
            bx, by = hand[0] - 1, hand[1] + 12
        elif ph == 0:
            bx, by = hand[0] + 2, hand[1] - 8
        elif ph == 1:
            bx, by = (hand[0] - 14, hand[1] - 4) if not side else (hand[0] - 14, hand[1] - 2)
        elif ph == 2:
            bx, by = (hand[0] - 10, G - 12) if not side else (hand[0] - 10, G - 12)
        else:
            bx, by = hand[0], hand[1] + 10
        n = 5
        for j in range(n + 1):
            t = j / n
            S.set(hand[0] + (bx - hand[0]) * t, hand[1] + (by - hand[1]) * t, "stone" if j % 2 else "stone_lo")
        ellf(S, bx, by, 3.5, 3.5, lambda x, y, u, v: "stone_lo" if u < 0 else "shadow")
        for (dx, dy) in ((0, -4), (4, 0), (-4, 0), (0, 4)):
            S.set(bx + dx, by + dy, "stone_hi")
        if ph == 2:
            for j in range(8):
                a = math.pi * j / 7
                S.set(bx + math.cos(a) * 7, by + 3 - math.sin(a) * 4, "flower_gold" if j % 2 else "white")
