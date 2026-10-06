"""Verdant Heart enemies (20x32, roles_enemies.py conventions): rot treant + spore elemental. Biome palette only."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_lib"))
from hmart import ell, rect, shader  # noqa: E402


def toad(s, x, y, w=2, top="roof_hi"):
    """a tiny red toadstool with a white spot: cap w px each side of x at row y, stem below"""
    for dx in range(-w, w + 1):
        s.set(x + dx, y, top if abs(dx) < w else "roof")
    for dx in range(-w + 1, w):
        s.set(x + dx, y - 1, top)
    s.set(x - (1 if w > 1 else 0), y - 1, "white")
    s.set(x, y + 1, "plaster_hi")


def rottreant(s, face, anim, i):
    """rot treant: a walking old stump-tree, cozy-gloomy (dark bark, drooping moss crown, red white-spotted toadstools
    on the shoulders, warm lamp-gold knot-hole eyes, a soft glow in the hollow mouth); attack = a branch-arm slam with
    flying leaves; die = it settles into a mossy stump sprouting toadstools"""
    b = 0
    arm = "rest"
    if anim == "idle":
        b = [0, 0, 1, 0][i]
    elif anim == "walk":
        b = [0, -1, 0, -1][i]
    elif anim == "attack":
        arm = ["up", "high", "slam", "mid"][i]; b = [0, -1, 1, 0][i]
    side = face == "left"
    if anim == "die":
        if i >= 2:                                         # a mossy stump with toadstools
            top = 22 if i == 2 else 24
            rect(s, 5, top, 14, 30, "timber")
            for y in range(top, 31):
                s.set(5, y, "timber_hi"); s.set(14, y, "timber_lo")
                if y % 3 == 0:
                    s.set(9, y, "timber_lo"); s.set(11, y + 1, "timber_lo")
            ell(s, 9.5, top, 5.0, 1.4, "plaster_lo"); ell(s, 9.5, top, 3.0, 0.8, "timber_hi")   # cut rings
            ell(s, 9.5, top - 1, 5.6, 1.6, "moss") if i == 3 else None
            for (x, y) in ((4, 30), (15, 30), (3, 29), (16, 29)):
                s.set(x, y, "timber_lo")
            toad(s, 6, top - 1 - (i == 3), 1); toad(s, 13, top - 2, 2)
            if i == 3:
                toad(s, 16, 28, 1); s.set(9, top - 2, "grass_hi"); s.set(10, top - 3, "grass_hi")
            return
        b = [1, 2][i]
    lean = 1 if (anim == "die" and i == 1) else 0
    # root feet
    if side:
        for (x0, lift) in ((6, 0 if anim != "walk" else [0, 1, 0, 0][i]), (11, 0 if anim != "walk" else [0, 0, 0, 1][i])):
            rect(s, x0, 27 - lift, x0 + 3, 30 - lift, "timber_lo")
            s.set(x0 - 1, 30 - lift, "timber_lo"); s.set(x0 + 4, 30 - lift, "timber_lo"); s.set(x0, 27 - lift, "timber")
    else:
        lifts = [(0, 0), (1, 0), (0, 0), (0, 1)][i] if anim == "walk" else (0, 0)
        for (x0, lift) in ((4, lifts[0]), (12, lifts[1])):
            rect(s, x0, 27 - lift, x0 + 3, 30 - lift, "timber_lo")
            s.set(x0 - 1, 30 - lift, "timber_lo"); s.set(x0 + 4, 30 - lift, "timber"); s.set(x0 + 1, 27 - lift, "timber")
    # trunk body
    x0, x1 = (6, 14) if side else (5, 14)
    for y in range(12 + b, 28):
        for x in range(x0, x1 + 1):
            c = "timber_hi" if x == x0 + 1 else "timber_lo" if x >= x1 - 1 else "timber"
            if (x + (y // 3)) % 4 == 0 and x0 + 1 < x < x1 - 1:
                c = "timber_lo"                                # bark grooves
            s.set(x + lean, y, c)
    for (x, y) in ((7, 25), (12, 25), (6, 20)):               # moss patches on the bark
        s.set(x + lean, y + b, "moss"); s.set(x + 1 + lean, y + b, "grass")
    # face: two warm knot-hole eyes in dark sockets, a hollow mouth with a soft glow inside
    if face == "down":
        for ex in (7, 11):
            rect(s, ex - 1 + lean, 16 + b, ex + 2 + lean, 18 + b, "ink")
            s.set(ex + lean, 17 + b, "lamp"); s.set(ex + 1 + lean, 17 + b, "white"); s.set(ex + lean, 18 + b, "flower_gold"); s.set(ex + 1 + lean, 18 + b, "flower_gold")
        rect(s, 8 + lean, 21 + b, 11 + lean, 23 + b, "ink"); s.set(9 + lean, 22 + b, "flower_gold"); s.set(10 + lean, 22 + b, "lamp")
    elif side:
        rect(s, 6 + lean, 16 + b, 8 + lean, 18 + b, "ink"); s.set(6 + lean, 17 + b, "lamp"); s.set(7 + lean, 17 + b, "white"); s.set(6 + lean, 18 + b, "flower_gold")
        rect(s, 6 + lean, 21 + b, 7 + lean, 22 + b, "ink"); s.set(6 + lean, 22 + b, "flower_gold")
    else:
        s.set(9, 19 + b, "timber_lo"); s.set(10, 18 + b, "timber_lo")
    # branch arms
    def branch(ax, ay, tx, ty, near=True):
        n = max(abs(tx - ax), abs(ty - ay)) + 1
        for k in range(n):
            t = k / max(1, n - 1)
            x, y = round(ax + (tx - ax) * t), round(ay + (ty - ay) * t)
            s.set(x, y, "timber" if near else "timber_lo"); s.set(x, y + 1, "timber_lo"); s.set(x + (1 if tx > ax else -1), y, "timber_lo" if near else "ink")
        s.set(tx - 1, ty + 1, "timber_lo"); s.set(tx + 1, ty + 1, "timber_lo"); s.set(tx, ty + 2, "timber_lo")
    sh = 14 + b
    if side:
        tgt = {"rest": (4, 22), "up": (5, 10), "high": (7, 5), "slam": (2, 27), "mid": (3, 19)}[arm]
        if anim == "walk":
            tgt = (4 + [0, 1, 0, -1][i], 22)
        branch(8, sh, tgt[0], tgt[1] + (b if arm == "rest" else 0))
    else:
        if arm == "rest":
            sw = [0, 1, 0, -1][i] if anim == "walk" else 0
            branch(5, sh, 2, 22 + sw); branch(14, sh, 17, 22 - sw, face == "down")
        else:
            ty = {"up": 9, "high": 5, "slam": 27, "mid": 19}[arm]
            branch(5, sh, 3, ty); branch(14, sh, 16, ty)
        if arm == "slam":
            for (x, y) in ((1, 29), (3, 28), (16, 29), (18, 28), (9, 29)):
                s.set(x, y, "plaster_lo")
    if arm == "slam":                                        # leaves knocked loose
        for (x, y) in ((2, 24), (17, 25), (5, 26)):
            s.set(x, y, "timber_hi" if x % 2 else "grass")
    # drooping moss crown
    cy = 8 + b + (1 if lean else 0)
    ell(s, 9.5 + lean, cy, 7.4, 4.6, "leaf_deep", shader(9.5, 7.4, "moss", "leaf_deep", "leaf_deep"))
    for k in range(14):
        x = 3 + k
        y = cy - 4 + ((k * 7) % 3)
        if (k + i) % 3 == 0:
            s.set(x + lean, y, "moss")
    for k, x in enumerate((3, 5, 7, 12, 14, 16)):              # hanging moss strands
        ln = 3 + (k * 5 + i) % 3
        for y in range(cy + 3, cy + 3 + ln):
            s.set(x + lean, y, "moss" if (y + k) % 2 else "grass")
    for (x, y) in ((6, cy - 2), (13, cy - 1), (9, cy - 3)):    # a few dead leaves in the canopy
        s.set(x + lean, y, "timber_hi")
    toad(s, 4 + lean, 12 + b, 1)
    toad(s, 13 + lean, cy - 4, 2)
    if face == "up":
        toad(s, 8, 20 + b, 2)                                # a toadstool shelf on its back


def sporeelemental(s, face, anim, i):
    """spore elemental (Verdant Heart tier): a hovering swirl of moss and glowing spores wearing a big red white-spotted
    toadstool cap, warm gills and lamp eyes under the brim, spore-stream arms; attack = the body swells and a spore
    burst streams forward; die = the cap drops onto a settling heap of spores"""
    b = [0, -1, -1, 0][i] if anim == "idle" else [0, -1, 0, -1][i] if anim == "walk" else [0, -1, -2, 0][i] if anim == "attack" else [0, 1, 3, 5][i]
    side = face == "left"
    if anim == "die" and i >= 2:
        ell(s, 9.5, 29.4, 5.5, 1.6, "moss")
        for (x, y) in ((5, 29), (8, 28), (12, 29), (14, 30), (7, 30), (10, 30)):
            s.set(x, y, "grass_hi" if x % 2 else "flower_gold")
        cx = 10 if i == 2 else 11
        cyc = 26 if i == 2 else 27
        ell(s, cx, cyc, 5.4, 2.4, "roof_hi", shader(cx, 5.4, "roof_hi", "roof_hi", "roof"))
        rect(s, cx - 5, cyc + 2, cx + 5, cyc + 2, "plaster_lo")
        for (dx, dy) in ((-3, -1), (1, -2), (3, 0)):
            s.set(cx + dx, cyc + dy, "white")
        return
    swell = 1 if anim == "attack" and i in (1, 2) else 0
    shrink = 1 if anim == "die" and i == 1 else 0
    # body: a round puff of moss and glowing spores, a short wisp underneath
    bcy, brx, bry = 19 + b, 5.6 + swell - shrink, 5.4 + swell - shrink
    for y in range(int(bcy - bry), int(bcy + bry) + 1):
        for x in range(int(9.5 - brx) - 1, int(9.5 + brx) + 2):
            if ((x - 9.5) / brx) ** 2 + ((y - bcy) / bry) ** 2 > 1:
                continue
            u = (x - (9.5 - brx)) / max(1, 2 * brx)
            c = "grass_hi" if u < 0.3 else "moss" if u > 0.72 else "grass"
            if (x * 3 + y * 2 + i) % 7 == 0:
                c = "flower_gold"
            elif (x + y + i) % 6 == 0 and 0.2 < u < 0.8:
                c = "leaf_deep"
            s.set(x, y, c)
    for k in range(12):                                      # fluffy rim
        a_ = k / 12 * 6.283 + i * 0.4
        x, y = 9.5 + (brx + 0.7) * math.cos(a_), bcy + (bry + 0.7) * math.sin(a_)
        if (k + i) % 2 == 0:
            s.set(int(round(x)), int(round(y)), "grass_hi" if math.sin(a_) < 0 else "leaf_deep")
    if not side:                                             # stubby spore-puff hands
        for sd in (-1, 1):
            hx = 9.5 + sd * (brx + 1.6 + (1 if anim == "attack" and i == 2 else 0))
            hy = bcy + 1 + (-2 if anim == "attack" and i in (1, 2) else 0)
            ell(s, hx, hy, 1.4, 1.3, "grass", shader(hx, 1.4, "grass_hi", "grass", "moss"))
    else:
        hx = 9.5 - brx - 1.4 - (1.5 if anim == "attack" and i == 2 else 0)
        ell(s, hx, bcy + 1, 1.4, 1.3, "grass", shader(hx, 1.4, "grass_hi", "grass", "moss"))
    for y in range(int(bcy + bry) + 1, 31):                 # the wisp trails down to the ground (floats, still anchored)
        s.set(9 + ((y + i) % 2), y, "moss" if y % 2 else "grass")
        if y < 28:
            s.set(10 - ((y + i) % 2), y, "leaf_deep")
    # spore-stream arms
    arms = 4 if anim == "attack" and i >= 1 else 0
    for k in range(arms):
        t = k / arms
        for sd in ((-1, 1) if not side else (-1,)):
            reach = 1.0 + (0.6 if anim == "attack" and i == 2 else 0)
            if face == "up":
                reach *= 0.8
            ax = 9.5 + sd * (5 + t * 4 * reach)
            ay = 17 + b + t * 5 * (1 if anim != "attack" or i < 2 else -0.6) + (math.sin(i + k) if anim == "walk" else 0)
            s.set(int(round(ax)), int(round(ay)), "flower_gold" if (k + i) % 2 else "grass_hi")
    # the toadstool cap
    cy = 9 + b
    ell(s, 9.5, cy, 7.6 + swell * 0.5, 4.2, "roof_hi", shader(9.5, 7.6, "roof_hi", "roof_hi", "roof"))
    rect(s, 3, cy + 3, 16, cy + 3, "roof_lo")
    spots = ((5, cy - 2), (9, cy - 3), (13, cy - 1), (7, cy + 1), (15, cy + 1), (11, cy)) if face != "up" else ((6, cy - 1), (10, cy - 2), (13, cy + 1), (8, cy + 1))
    for (x, y) in spots:
        s.set(x, y, "white"); s.set(x + 1, y, "plaster_hi")
    if face != "up":                                         # warm gills under the brim + lamp eyes
        for x in range(5, 15):
            s.set(x, cy + 4, "plaster_lo" if x % 2 else "lamp")
        if face == "down":
            for ex in (7, 11):
                rect(s, ex, cy + 7, ex + 1, cy + 8, "lamp"); s.set(ex, cy + 7, "white"); s.set(ex + 1, cy + 8, "flower_gold")
        else:
            rect(s, 5, cy + 7, 6, cy + 8, "lamp"); s.set(5, cy + 7, "white")
    n, R = (12, 9.8) if anim == "attack" and i == 2 else (6, 9.0)
    for k in range(n):                                       # orbiting spores
        a = k / n * 6.283 + i * 0.7
        x, y = 9.5 + R * math.cos(a), 18 + b + R * 0.75 * math.sin(a)
        if 1 <= x < 19 and 1 <= y < 31 and s.p[int(round(y))][int(round(x))] is None:
            s.set(int(round(x)), int(round(y)), "flower_gold" if k % 2 else "grass_hi")
