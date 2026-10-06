"""The Blight Regent (Verdant Heart boss): drawn natively in a 128x176 frame (5.5 x the 32 px hero frame; the figure
stands ~162 px = 5.6 x the hero's 29 px visible height), boss_sheet.py conventions.
Cozy-gloomy, never gross: a corrupted forest lord of gnarled bark, a drooping moss mantle, antlers grown with red
white-spotted toadstools, mauve blight blossoms and gold spore-lanterns, sickly violet-rose eyes in a hollow bark mask, a
dead-sapling staff, and a root ribcage around a violet wound with the blue frost-iron spike in it (rime frost-flowers; the
only blue on him). The spike is gone from die frame 25 and lies on the mound. Die ends in a mossy root mound with a fresh green sapling (the heart cleansed)."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_lib"))
from hmart import ell, rect, shader  # noqa: E402

W, H = 128, 176
CX = 64
DY = 18          # the base drawing sits DY px lower in the taller frame; antlers grow taller to fill it


class Off:
    """draws through to the real sprite with a y offset (layout shift only, never a scale)"""
    def __init__(self, s, dy):
        self.s, self.dy = s, dy

    def set(self, x, y, c):
        self.s.set(x, y + self.dy, c)

    def get(self, x, y):
        y = int(y) + self.dy
        x = int(x)
        if 0 <= y < len(self.s.p) and 0 <= x < len(self.s.p[0]):
            return self.s.p[y][x]
        return "x"


def tline(s, x0, y0, x1, y1, w, col, hi=None, lo=None):
    """thick line: w px wide, optional light (left / top) and dark (right / bottom) edge colours"""
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    for k in range(n):
        t = k / max(1, n - 1)
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        r = w / 2
        for dy in range(-int(r) - 1, int(r) + 2):
            for dx in range(-int(r) - 1, int(r) + 2):
                if dx * dx + dy * dy <= r * r:
                    c = col
                    if hi and dx <= -r + 1:
                        c = hi
                    elif lo and dx >= r - 1:
                        c = lo
                    s.set(int(round(x + dx)), int(round(y + dy)), c)


def toad(s, x, y, w, spots=True):
    """a red toadstool cap (half-dome w px radius) with white spots and warm gills, on a cream stem"""
    for dy in range(0, w + 1):
        hw = int(round(math.sqrt(max(0, w * w - (dy * 1.6) ** 2))))
        for dx in range(-hw, hw + 1):
            c = "roof_hi" if dx < hw - 1 else "roof"
            s.set(x + dx, y - dy, c)
    for dx in range(-w, w + 1):
        s.set(x + dx, y + 1, "plaster_lo" if dx % 2 else "lamp")
    if spots:
        for (dx, dy) in ((-w // 2, -1), (w // 3, -w // 2), (0, -w // 2 - 1), (w // 2 + 1, -1)):
            s.set(x + dx, y + dy, "white")
            if w >= 4:
                s.set(x + dx + 1, y + dy, "white")
    s.set(x, y + 2, "plaster_hi"); s.set(x, y + 3, "plaster_hi")


def blossom(s, x, y, hot=False):
    """a mauve blight blossom: rose petals, a white heart (the corruption glows soft, never oozes)"""
    for (dx, dy) in ((0, -1), (-1, 0), (1, 0), (0, 1)):
        s.set(x + dx, y + dy, "flower_rose")
    s.set(x, y, "white" if hot else "plaster_hi")


def lantern(s, x, y, i):
    """a hanging gold spore-lantern pod"""
    s.set(x, y - 2, "timber_lo"); s.set(x, y - 1, "timber_lo")
    rect(s, x - 1, y, x + 1, y + 2, "flower_gold"); s.set(x, y + 1, "lamp" if i % 2 == 0 else "white")


def antlers(s, face, by, lift, i, shed=0):
    """two great branching antlers rising from the crown, toadstools and blossoms on the tines"""
    sides = (-1, 1) if face != "left" else (-1, 1)
    for sd in sides:
        far = face == "left" and sd == 1
        col, hi, lo = ("timber_lo", None, "ink") if far else ("timber", "timber_hi", "timber_lo")
        ox = CX + sd * 8 + (6 if face == "left" else 0)
        base = (ox, by)
        spread = 0.55 if face == "left" else 1.0
        p1 = (ox + sd * 16 * spread, by - 18 - lift)
        p2 = (ox + sd * 30 * spread, by - 30 - lift)
        p3 = (ox + sd * 40 * spread, by - 36 - lift)
        tline(s, *base, *p1, 6, col, hi, lo)
        tline(s, *p1, *p2, 5, col, hi, lo)
        tline(s, *p2, *p3, 4, col, hi, lo)
        tines = [(p1, (p1[0] + sd * 2 * spread, p1[1] - 13)), (p2, (p2[0] - sd * 3 * spread, p2[1] - 12)),
                 (p2, (p2[0] + sd * 10 * spread, p2[1] + 2)), (p3, (p3[0] + sd * 7 * spread, p3[1] - 6)),
                 (p3, (p3[0] - sd * 4 * spread, p3[1] - 9))]
        for k, (a, b) in enumerate(tines):
            tline(s, *a, *b, 3, col, None, lo)
            if far:
                continue
            if k == 0 and shed < 1:
                toad(s, int(b[0]), int(b[1]) + 1, 6)
            elif k == 1 and shed < 2:
                toad(s, int(b[0]), int(b[1]) + 1, 5)
            elif k == 2:
                lantern(s, int(b[0]), int(b[1]) + 3, i + k)
            elif k == 3 and shed < 1:
                blossom(s, int(b[0]), int(b[1]), (i + k) % 2 == 0)
            elif k == 4:
                blossom(s, int(b[0]), int(b[1]), (i + k) % 2 == 1)
        if not far and shed < 2:
            toad(s, int(p2[0]), int(p2[1]) - 3, 7)


def roots(s, face, b, lift_l, lift_r, spread=1.0):
    """the root-mass base: splayed root tendrils plus two thick root 'legs' that lift on a walk"""
    side = face == "left"
    for k in range(9):
        t = (k - 4) / 4
        x0 = CX + t * 18
        x1 = CX + t * 46 * spread
        y1 = 156 - abs(t) * 3
        tline(s, x0, 124 + b, (x0 + x1) / 2, 146, 4 - abs(t) * 1.5, "timber_lo", "timber", "ink")
        tline(s, (x0 + x1) / 2, 146, x1, y1, 3 - abs(t), "timber_lo", None, "ink")
    for (lx, lift) in ((CX - 16 + (4 if side else 0), lift_l), (CX + 16 - (4 if side else 0), lift_r)):
        tline(s, lx, 118 + b, lx + (-3 if lx < CX else 3), 152 - lift, 9, "timber", "timber_hi", "timber_lo")
        for d in (-6, -2, 2, 6):
            tline(s, lx + (-3 if lx < CX else 3), 152 - lift, lx + d * 1.3 + (-3 if lx < CX else 3), 157 - lift, 2, "timber_lo")
    for (x, y) in ((CX - 30, 150), (CX + 30, 150), (CX - 10, 154), (CX + 10, 154)):   # moss at the root feet
        ell(s, x, y, 4, 1.4, "moss"); s.set(x - 1, y - 1, "grass_hi")


def blightregent(s, face, anim, i):
    s = Off(s, DY)
    side = face == "left"
    b = 0; lift_l = lift_r = 0; arm = "rest"; shed = 0; sink = 0
    if anim == "idle":
        b = [0, 1, 2, 1][i]
    elif anim == "walk":
        b = [0, -1, 0, -1][i]; lift_l, lift_r = [(0, 0), (4, 0), (0, 0), (0, 4)][i]
    elif anim == "attack":
        arm = ["up", "high", "slam", "mid"][i]; b = [0, -3, 4, 1][i]
    elif anim == "die":
        shed = i + 1; sink = [4, 18, 0, 0][i]
    if anim == "die" and i >= 2:                            # the root mound: corruption gone, a sapling sprouts
        top = 112 if i == 2 else 122
        ell(s, CX, 146, 50, 157 - top - 2, "timber", shader(CX, 50, "timber_hi", "timber", "timber_lo"))
        for k in range(9):
            t = (k - 4) / 4
            tline(s, CX + t * 30, top + 14 + abs(t) * 10, CX + t * 54, 156, 3, "timber_lo", None, "ink")
        ell(s, CX - 6, top + 6, 40, 9, "leaf_deep", shader(CX, 40, "moss", "leaf_deep", "leaf_deep"))
        for k in range(12):
            x = CX - 40 + k * 7
            for y in range(top + 10, top + 16 + (k * 5) % 6):
                s.set(x, y, "moss" if y % 2 else "grass")
        # fallen antlers across the mound
        tline(s, CX - 10, top + 2, CX - 46, top - 18, 3, "timber", "timber_hi", "timber_lo")
        tline(s, CX - 30, top - 8, CX - 34, top - 22, 2, "timber", None, "timber_lo")
        tline(s, CX + 8, top + 4, CX + 44, top - 12, 3, "timber", "timber_hi", "timber_lo")
        for (x, y, w) in ((CX - 24, top + 2, 5), (CX + 30, top + 4, 4), (CX + 48, 150, 3), (CX - 46, 152, 3), (CX + 4, top - 2, 3)):
            toad(s, x, y, w)
        if i == 3:                                           # the cleansed heart: a sapling with fresh leaves
            tline(s, CX, top - 2, CX, top - 26, 2, "timber", None, "timber_lo")
            for (dx, dy) in ((-4, -22), (4, -26), (-3, -16), (3, -12), (0, -30)):
                ell(s, CX + dx, top + dy, 3, 1.6, "grass_hi", shader(CX + dx, 3, "grass_hi", "grass_hi", "grass"))
            for (x, y) in ((CX - 14, top - 30), (CX + 16, top - 20), (CX - 20, top - 10), (CX + 22, top - 36)):
                s.set(x, y, "grass_hi"); s.set(x, y - 1, "white")
        else:
            rect(s, CX - 3, top - 3, CX + 3, top + 1, "shadow"); s.set(CX, top - 1, "flower_rose")
        tline(s, CX + 20, 154, CX + 40, 150, 1, "flower_blue", "sky")          # the pulled frost-iron spike
        s.set(CX + 40, 150, "white"); s.set(CX + 23, 151, "white"); s.set(CX + 33, 149, "sky")
        return
    b += sink
    roots(s, face, b, lift_l, lift_r)
    # torso: a gnarled trunk, bark grooves, faint mauve blight veins
    tx0, tx1 = (CX - 18, CX + 22) if side else (CX - 24, CX + 24)
    top, bot = 62 + b, 126 + b
    for y in range(top, bot):
        t = (y - top) / (bot - top)
        bulge = int(3 - 8 * math.sin(t * math.pi) + 4 * t * t)       # broad shoulders, gnarled waist, root flare
        for x in range(tx0 - bulge, tx1 + bulge + 1):
            u = (x - (tx0 - bulge)) / max(1, tx1 - tx0 + 2 * bulge)
            c = "timber_hi" if u < 0.16 else "timber_lo" if u > 0.8 else "timber"
            if (x * 2 + (y // 5)) % 9 == 0 and 0.12 < u < 0.86:
                c = "timber_lo"
            if (x + y * 3) % 23 == 0 and 0.2 < u < 0.8:
                c = "shadow"
            s.set(x, y, c)
    for k in range(5):                                       # blight veins (mauve shadow lines with rose glints)
        vx = CX - 18 + k * 9 + (4 if side else 0)
        for y in range(top + 20 + k * 3, bot - 6, 2):
            x = vx + int(2 * math.sin(y * 0.2 + k))
            s.set(x, y, "shadow")
            if (y + i) % 14 == 0:
                s.set(x, y, "flower_rose")
    # the wound in the chest: a ribcage of roots around a violet-glowing hollow, the blue frost-iron spike jutting out
    if face != "up":
        kx, ky = (CX - 6 if side else CX), top + 22
        ell(s, kx, ky, 9, 8, "timber_lo")
        ell(s, kx, ky, 6.5, 5.5, "shadow")
        ell(s, kx, ky, 4.5, 3.5, "roof_lo")
        ell(s, kx, ky, 2.6, 2, "flower_rose")
        for r_ in (-6, -2, 2, 6):                              # root ribs across the wound
            tline(s, kx + r_, ky - 7, kx + r_ * 1.2, ky + 7, 1, "timber_lo")
        if not (anim == "die" and i >= 1):                   # the spike (gone once it slides out on death)
            d = -1 if side else 1
            x0, y0, x1, y1 = kx - d * 1, ky + 1, kx + d * 15, ky - 13
            tline(s, x0, y0, x1, y1, 2, "flower_blue", "sky")
            s.set(int(x1), int(y1), "white"); s.set(int(x1) - d, int(y1) + 1, "sky")
            rect(s, int(x0 + d * 2) - 1, int(y0 - 3), int(x0 + d * 2) + 1, int(y0 - 1), "sky")      # the spike's collar
            for (fx_, fy_) in ((-5, -3), (-3, 4), (4, 5), (6, -1), (-6, 2), (1, -6), (8, 3)):         # rime frost-flowers
                if (fx_ + fy_ + i) % 3:
                    s.set(kx + fx_, ky + fy_, "white" if (fx_ + i) % 2 else "sky")
    # arms (long branch arms ending in root claws)
    def arm_to(sx, sy, ex, ey, near=True):
        col, hi, lo = ("timber", "timber_hi", "timber_lo") if near else ("timber_lo", None, "ink")
        mx, my = (sx + ex) / 2 + (6 if ex > sx else -6), (sy + ey) / 2 - 4
        tline(s, sx, sy, mx, my, 11, col, hi, lo)
        tline(s, mx, my, ex, ey, 8, col, hi, lo)
        for t in (0.3, 0.7):                                  # moss tufts on the arm
            s.set(int(sx + (mx - sx) * t), int(sy + (my - sy) * t) - 4, "moss"); s.set(int(sx + (mx - sx) * t) + 1, int(sy + (my - sy) * t) - 4, "grass")
        for d in (-1, 0, 1):
            dx, dy = ex - mx, ey - my
            ln = max(1, math.hypot(dx, dy))
            ux, uy = dx / ln, dy / ln
            tline(s, ex, ey, ex + ux * 10 + uy * d * 6, ey + uy * 10 - ux * d * 6, 3, lo)
    shy = top + 10
    if side:
        tgt = {"rest": (CX - 30, 120 + b), "up": (CX - 26, 30), "high": (CX - 8, 14), "slam": (CX - 44, 148), "mid": (CX - 40, 100)}[arm]
        if anim == "walk":
            tgt = (CX - 30 + [0, 4, 0, -4][i], 120 + b)
        arm_to(CX + 14, shy, CX + 26, 116 + b, False)
        arm_to(CX - 10, shy, *tgt)
    else:
        if arm == "rest":
            sw = [0, 3, 0, -3][i] if anim == "walk" else [0, 1, 1, 0][i]
            arm_to(CX - 26, shy, CX - 46, 122 + b + sw, True)
            arm_to(CX + 26, shy, CX + 46, 122 + b - sw, face == "down")
        else:
            ty = {"up": 32, "high": 14, "slam": 146, "mid": 104}[arm]
            tx = {"up": 44, "high": 26, "slam": 46, "mid": 48}[arm]
            arm_to(CX - 26, shy, CX - tx, ty, True)
            arm_to(CX + 26, shy, CX + tx, ty, face == "down")
    # the dead-sapling staff (its red toadstools flare before a sweep)
    if side:
        hx_, hy_ = tgt
    else:
        hx_, hy_ = (CX - 46, 122 + b + (([0, 3, 0, -3][i] if anim == "walk" else [0, 1, 1, 0][i]))) if arm == "rest" else \
                   (CX - {"up": 44, "high": 26, "slam": 46, "mid": 48}[arm], {"up": 32, "high": 14, "slam": 146, "mid": 104}[arm])
    if arm in ("rest",):
        sx0, sy0, sx1, sy1 = hx_ - 2, hy_ + 30, hx_ + 4, hy_ - 72
    else:
        sx0, sy0, sx1, sy1 = hx_ + 10, hy_ + 18, hx_ - 14, hy_ - 44
        if arm == "slam":
            sx0, sy0, sx1, sy1 = hx_ + 18, hy_ - 34, hx_ - 8, hy_ - 14
    tline(s, sx0, sy0, sx1, sy1, 3, "timber_lo", "timber", "ink")
    for t in (0.55, 0.75, 0.9):                               # dead twigs + toadstools at the top
        px_, py_ = sx0 + (sx1 - sx0) * t, sy0 + (sy1 - sy0) * t
        tline(s, px_, py_, px_ - 7, py_ - 6, 1, "timber_lo")
    toad(s, int(sx1), int(sy1) - 2, 4); toad(s, int(sx1 - 7), int(sy0 + (sy1 - sy0) * 0.75) - 7, 3)
    if arm == "slam":                                         # roots burst from the ground + leaf dust
        for k, x in enumerate((CX - 50, CX - 40, CX + 40, CX + 50, CX - 6, CX + 6)):
            tline(s, x, 157, x + (k % 3 - 1) * 3, 140 - (k % 2) * 6, 3, "timber_lo", "timber", "ink")
        for (x, y) in ((CX - 50, 136), (CX + 50, 134), (CX - 20, 146), (CX + 24, 144), (CX, 138)):
            s.set(x, y, "plaster_lo"); s.set(x + 1, y + 1, "grass")
    # moss mantle draped over the shoulders: a humped collar, ragged hanging strands, toadstools sprouting on top
    my = top + 4
    mo = 4 if side else 0
    rx = 30 if side else 38
    for y in range(my - 10, my + 9):
        for x in range(CX + mo - rx - 1, CX + mo + rx + 2):
            u = (x - CX - mo) / rx
            if abs(u) > 1:
                continue
            ytop = my - 9 * math.sqrt(1 - u * u) + 4 * math.exp(-(u / 0.22) ** 2) + 2 * (abs(u) > 0.85)
            ybot = my + 6 + 2 * math.sin(x * 1.3) - 3 * (abs(u) > 0.9)
            if ytop <= y <= ybot:
                c = "grass" if y < ytop + 2 else "moss" if y < my + 2 else "leaf_deep"
                if (x * 5 + y * 3) % 11 == 0:
                    c = "grass_hi" if y < my else "moss"
                s.set(x, y, c)
    for k in range(26):
        x = CX + mo - rx + 2 + k * (2 * rx - 4) / 25
        ln = 4 + (k * 7 + i) % 11 + (10 if k % 5 == 1 else 0) - int(6 * abs(k - 12.5) / 12.5)
        for y in range(my + 6, my + 6 + ln):
            s.set(int(x), y, "moss" if (y + k) % 3 else "leaf_deep")
        s.set(int(x), my + 6 + ln, "grass")
        if k % 6 == 3:
            s.set(int(x) + 1, my + 9 + ln // 2, "timber_hi")
    for (dx, w) in ((-rx + 8, 6), (rx - 10, 5), (-rx + 18, 4)):
        if side and dx > 0:
            continue
        toad(s, CX + mo + dx, my - 9 + (2 if w < 5 else 0), w)
    for (dx, dy) in ((-14, -4), (16, -5), (-24, 2), (26, 1), (4, 4)):   # glow fungi in the moss
        s.set(CX + mo + dx, my + dy, "lamp"); s.set(CX + mo + dx + 1, my + dy, "flower_gold")
    # head: a hollow bark mask with warm eyes and a crown of bark spikes
    hx, hy = (CX - 8 if side else CX), 44 + b
    ell(s, hx + (4 if side else 0), hy, 14 if not side else 12, 17, "timber", shader(hx, 14, "timber_hi", "timber", "timber_lo"))
    if face == "down":
        ell(s, hx, hy + 3, 9, 11, "ink")
        for ex in (-5, 5):
            rect(s, hx + ex - 2, hy - 1, hx + ex + 2, hy + 2, "flower_rose")
            s.set(hx + ex - 1, hy - 1, "white"); s.set(hx + ex, hy - 1, "plaster_hi")
            rect(s, hx + ex - 2, hy + 2, hx + ex + 2, hy + 2, "shadow")
        for x in range(hx - 4, hx + 5, 2):                     # a slow soft breath of gold spores in the mouth hollow
            s.set(x, hy + 9 + (1 if abs(x - hx) < 3 else 0), "flower_gold")
        tline(s, hx - 12, hy - 14, hx + 12, hy - 14, 2, "timber_lo")
    elif side:
        ell(s, hx - 4, hy + 3, 6, 10, "ink")
        rect(s, hx - 8, hy - 1, hx - 4, hy + 2, "flower_rose"); s.set(hx - 7, hy - 1, "white"); rect(s, hx - 8, hy + 2, hx - 4, hy + 2, "shadow")
        for y in range(hy + 7, hy + 11, 2):
            s.set(hx - 6, y, "flower_gold")
    else:
        for k in range(6):
            s.set(hx - 6 + k * 2, hy - 4 + (k % 2) * 6, "timber_lo")
    for k in range(5):                                        # bark crown spikes
        x = hx - 10 + k * 5 + (3 if side else 0)
        tline(s, x, hy - 14, x + (k - 2), hy - 22 - (4 if k == 2 else 0), 2, "timber_lo", None, "ink")
    antlers(s, face, hy - 14, -sink // 2 if anim == "die" else (2 if arm in ("up", "high") else 0), i, shed)
    # drifting spores (gold / green glints), more in the attack
    n = 16 if anim == "attack" and i == 2 else 10
    for k in range(n):
        a = k / n * math.tau + i * 0.5
        x, y = CX + 52 * math.cos(a), 84 + b + 40 * math.sin(a)
        if 2 <= x < W - 2 and 2 <= y + DY < H - 3 and s.get(x, y) is None:
            s.set(int(x), int(y), "flower_gold" if k % 2 else "grass_hi")
