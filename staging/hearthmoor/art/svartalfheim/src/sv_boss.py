"""Gorrak Ironmaw, the Bound Forge-Tyrant (Clockwork Deep C8 boss), drawn natively in a 144x192 frame (6 x the 32 px hero
frame; the figure stands ~180 px = 6.2 x the hero's 29 px visible height), boss_sheet.py conventions.
The ONLY plate-wearer in Hearthmoor: a fire-demon bound into real plate armour - huge blackened iron plates riveted over a body
of living flame, a horned helm with a jaw-guard like an iron maw, chains from wrist manacles to the anvil-pillar, cold-blue
binding runes along every plate seam, forge fire (palette roof / roof_hi / lamp / flower_gold, white-hot core) leaking through
every gap, two coal eyes. Two roles share the sheet: `gorrak` (phase 1, chained, plates shut) and `gorrak_unbuckled`
(phases 2-3: chains torn loose, the layered plates opened and the fire roaring through). Die = falls to one knee, the plates
split, a white-hot ember beats like a heart in the open chest. Palette only (the runes glow via gorrak_* fx + lights)."""
import math

from sv_common import H, rect

W, HH = 144, 192
CX = 72
G = 190                      # lowest opaque row (frame h - 2)


class Safe:
    def __init__(self, s):
        self.s = s
        self.w, self.h = len(s.p[0]), len(s.p)

    def set(self, x, y, c):
        x, y = int(round(x)), int(round(y))
        if 1 <= x < self.w - 1 and 1 <= y < self.h - 1:
            self.s.set(x, y, c)

    def get(self, x, y):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.s.p[y][x]
        return None


def hsh(*a):
    """fast deterministic hash -> [0, 1) (per-pixel noise; H.rng per pixel is too slow at 144x192)"""
    v = 2166136261
    for x in a:
        for ch in str(x):
            v = ((v ^ ord(ch)) * 16777619) & 0xFFFFFFFF
        v = ((v ^ 0x9E) * 16777619) & 0xFFFFFFFF
    return (v & 0xFFFF) / 65536


def ellf(S, cx, cy, rx, ry, fn):
    for y in range(int(cy - ry - 1), int(cy + ry + 2)):
        for x in range(int(cx - rx - 1), int(cx + rx + 2)):
            u, v = (x - cx) / max(rx, .01), (y - cy) / max(ry, .01)
            if u * u + v * v <= 1.0:
                c = fn(x, y, u, v)
                if c:
                    S.set(x, y, c)


def iron(u, v=0.0):
    """blackened iron shading across a plate (u -1 left .. +1 right; light from the upper left)"""
    if v < -0.85:
        return "stone_lo"
    if u < -0.55:
        return "stone_lo"
    if u < 0.15:
        return "shadow"
    return "timber_lo"


def fire(x, y, k=0, hot=1.0):
    """living flame colour for a body pixel (flickers with frame k; hot > 1 brighter)"""
    w = 0.5 + 0.35 * math.sin(x * 0.55 + y * 0.3 + k * 1.7) * math.cos(y * 0.42 - k * 0.9 + x * 0.1)
    t = (w + 0.25 * hsh("f", x // 2, y // 2, k)) * hot
    return "white" if t > 0.93 else "flower_gold" if t > 0.75 else "lamp" if t > 0.5 else "roof_hi" if t > 0.25 else "roof"


def fire_line(S, x0, y0, x1, y1, w, k, hot=1.0):
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    for j in range(n):
        t = j / max(1, n - 1)
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        r = w / 2
        for dy in range(-int(r) - 1, int(r) + 2):
            for dx in range(-int(r) - 1, int(r) + 2):
                if dx * dx + dy * dy <= r * r:
                    S.set(x + dx, y + dy, fire(int(x + dx), int(y + dy), k, hot))


def iron_line(S, x0, y0, x1, y1, w, rune=None, k=0):
    """a plate limb segment: iron with a lit top-left edge, rivets, and a rune seam along one edge"""
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
                    c = "stone_lo" if d < -0.55 else "shadow" if d < 0.2 else "timber_lo"
                    if rune and d > 0.62 and j % 2 == 0:
                        c = "white" if (j // 2 + k) % 7 == 0 else "sky"
                    S.set(x + dx, y + dy, c)
    for j in range(2, n - 1, 7):
        t = j / max(1, n - 1)
        S.set(x0 + (x1 - x0) * t - nx * (w / 2 - 1.5), y0 + (y1 - y0) * t - ny * (w / 2 - 1.5), "stone_hi")


def plate_rect(S, x0, y0, x1, y1, k, rune_bottom=True, rivets=True, curve=0.0):
    """a riveted iron plate (x0..x1, y0..y1), lit left edge, rune seam along the bottom edge"""
    w = max(1, x1 - x0)
    for y in range(int(y0), int(y1) + 1):
        for x in range(int(x0), int(x1) + 1):
            u = (x - x0) / w * 2 - 1
            yy = y + curve * (u * u)
            if yy > y1:
                continue
            c = iron(u, (y - y0) / max(1, y1 - y0) * 2 - 1)
            if y == int(y0):
                c = "stone"
            elif y == int(y0) + 1:
                c = "stone_lo"
            S.set(x, y, c)
    if rune_bottom:
        for x in range(int(x0) + 1, int(x1)):
            u = (x - x0) / w * 2 - 1
            S.set(x, y1 - int(curve * u * u) - 1, "white" if (x + k * 3) % 11 == 0 else "sky")
    if rivets:
        for x in range(int(x0) + 3, int(x1) - 1, 6):
            S.set(x, y0 + 2, "stone_hi")


def coal_eye(S, x, y, k, open_=True, hot=False):
    if not open_:
        S.set(x, y, "roof_lo"); S.set(x + 1, y, "roof_lo")
        return
    rect(S, x - 1, y - 1, x + 2, y + 1, "roof")
    S.set(x, y, "lamp"); S.set(x + 1, y, "lamp")
    S.set(x, y - 1, "roof_hi"); S.set(x + 1, y - 1, "roof_hi")
    S.set(x + (k % 2), y, "white" if hot or k % 2 == 0 else "flower_gold")


def chain(S, x0, y0, x1, y1, k=0):
    n = int(max(abs(x1 - x0), abs(y1 - y0)) / 3) + 1
    for j in range(n + 1):
        t = j / max(1, n)
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + math.sin(t * math.pi) * 3
        if j % 2 == 0:
            rect(S, int(x) - 1, int(y) - 1, int(x) + 1, int(y) + 1, "stone_lo"); S.set(x, y, "shadow"); S.set(x - 1, y - 1, "stone")
        else:
            S.set(x, y, "stone"); S.set(x, y - 1, "stone_lo"); S.set(x, y + 1, "stone_lo")


def flame_tongues(S, cx, cy, n, spread, hgt, k, hot=1.0):
    """flame licks rising from a gap (above a pauldron / the helm crest)"""
    for j in range(n):
        x = cx + (j - (n - 1) / 2) * spread
        hh = hgt * (0.5 + 0.6 * hsh("t", j, k))
        sw = math.sin(k * 1.3 + j) * 1.5
        for t in range(int(hh)):
            f = t / max(1, hh)
            w = 2.4 * (1 - f)
            for dx in range(-int(w), int(w) + 1):
                c = "flower_gold" if f < 0.3 and abs(dx) < 1 else "lamp" if f < 0.55 else "roof_hi" if f < 0.85 else "roof"
                if hot > 1.2 and f < 0.2 and dx == 0:
                    c = "white"
                S.set(x + dx + sw * f, cy - t, c)


def helm(S, face, hx, hy, k, hot=False, eyes=True):
    """horned helm with an iron-maw jaw-guard (fire glowing between its teeth)"""
    if face == "up":
        ellf(S, hx, hy, 17, 18, lambda x, y, u, v: iron(u, v))
        for x in range(hx - 15, hx + 16):
            S.set(x, hy + 4, "white" if (x + k) % 9 == 0 else "sky")
        for x in range(hx - 1, hx + 2):
            for y in range(hy - 17, hy + 14):
                S.set(x, y, "stone" if x == hx - 1 else "stone_lo")
        horns(S, face, hx, hy, k)
        return
    side = face == "left"
    if side:
        ellf(S, hx + 2, hy, 16, 18, lambda x, y, u, v: iron(u, v))
        # the maw: a jutting jaw-guard to the left
        for y in range(hy + 2, hy + 18):
            x0 = hx - 18 + (y - hy - 2) // 4
            for x in range(x0, hx + 6):
                S.set(x, y, iron(-0.2 if y < hy + 10 else 0.4))
        for j in range(5):                                  # teeth bars with fire behind
            x = hx - 14 + j * 4
            for y in range(hy + 9, hy + 15):
                S.set(x + 1, y, fire(x, y, k, 1.2))
            S.set(x, hy + 15, "stone_hi")
        rect(S, hx - 16, hy - 2, hx + 2, hy + 1, "shadow")
        if eyes:
            coal_eye(S, hx - 10, hy - 1, k, True, hot)
        for x in range(hx - 12, hx + 16):
            S.set(x, hy + 18 - max(0, (hx - x) // 6), "sky" if (x + k) % 8 else "white")
        horns(S, face, hx, hy, k)
        return
    ellf(S, hx, hy, 17, 18, lambda x, y, u, v: iron(u, v))
    rect(S, hx - 13, hy - 3, hx + 13, hy + 1, "shadow")          # eye slit band
    if eyes:
        coal_eye(S, hx - 7, hy - 1, k, True, hot)
        coal_eye(S, hx + 6, hy - 1, k, True, hot)
    # nasal ridge
    for y in range(hy - 16, hy + 4):
        S.set(hx, y, "stone" if y < hy - 3 else "stone_lo")
    # the iron maw jaw-guard: a wide jaw of riveted bars, fire between the teeth
    for y in range(hy + 4, hy + 20):
        hw = 16 - (y - hy - 4) // 3
        for x in range(hx - hw, hx + hw + 1):
            S.set(x, y, iron((x - hx) / max(1, hw)))
    for j in range(-3, 4):
        x = hx + j * 4
        for y in range(hy + 8, hy + 15):
            S.set(x, y, fire(x, y, k, 1.3 if hot else 1.0))
            S.set(x + 1, y, fire(x + 1, y, k + 1, 1.0))
        S.set(x, hy + 16, "stone_hi"); S.set(x - 1, hy + 7, "stone_hi")
    for x in range(hx - 15, hx + 16):                       # rune seam under the brow and along the jaw
        S.set(x, hy + 3, "white" if (x + k * 2) % 10 == 0 else "sky")
    for y in range(hy + 5, hy + 18):
        hw = 16 - (y - hy - 4) // 3
        S.set(hx - hw, y, "sky"); S.set(hx + hw, y, "sky")
    horns(S, face, hx, hy, k)


def horns(S, face, hx, hy, k):
    """two great curved horns (pale horn ramp) sweeping out and up from the helm"""
    sides = (-1, 1) if face != "left" else (1,)
    for sd in sides:
        bx = hx + sd * 14 if face != "left" else hx + 8
        for j in range(22):
            t = j / 21
            x = bx + sd * (math.sin(t * 1.9) * 16) + (0 if face != "left" else 6 * t)
            y = hy - 10 - t * 26 + (t * t) * 6
            w = 5.5 * (1 - t) + 1
            for dx in range(-int(w), int(w) + 1):
                c = "plaster" if dx < -w / 3 else "plaster_lo" if dx < w / 3 else "stone"
                if j % 4 == 0 and abs(dx) < w - 1:
                    c = "stone"                              # horn ridges
                S.set(x + dx, y, c)
        tip_x = bx + sd * math.sin(1.9) * 16 + (0 if face != "left" else 6)
        S.set(tip_x, hy - 36 + 6 - 1, "white")


def pose(anim, i):
    P = dict(bob=0, la=("rest", 0), ra=("rest", 0), step=0, kneel=0, split=0, core=1.0, slump=0, shock=0)
    if anim == "idle":
        P["bob"] = [0, 1, 2, 1][i]
    elif anim == "walk":
        P["bob"] = [0, 2, 0, 2][i]
        P["step"] = [-1, 0, 1, 0][i]
    elif anim == "attack":
        P["bob"] = [2, -2, 8, 3][i]
        arm = ["ready", "raise", "slam", "rest"][i]
        P["la"] = P["ra"] = (arm, 0)
        P["shock"] = 1 if i == 2 else 0
        P["core"] = [1.1, 1.3, 1.5, 1.1][i]
    elif anim == "die":
        P["bob"] = [6, 24, 30, 60][i]
        P["kneel"] = 1 if i >= 1 else 0
        P["split"] = [0, 1, 6, 10][i]
        P["la"] = P["ra"] = (["rest", "low", "low", "heap"][i], 0)
        P["core"] = [1.0, 1.2, 1.6, 1.4][i]
        P["slump"] = i
    return P


def fists(face, arm, side_sign, bob):
    """shoulder -> elbow -> fist points for one arm (front view: side_sign -1 = screen left)"""
    sx, sy = CX + side_sign * 36, 78 + bob
    if arm == "rest":
        return (sx, sy), (sx + side_sign * 10, sy + 30), (sx + side_sign * 8, sy + 56)
    if arm == "ready":
        return (sx, sy), (sx + side_sign * 14, sy + 26), (sx - side_sign * 6, sy + 30)
    if arm == "raise":
        return (sx, sy), (sx + side_sign * 14, sy - 22), (sx - side_sign * 6, sy - 46)
    if arm == "slam":
        return (sx, sy), (sx + side_sign * 8, sy + 30), (sx - side_sign * 10, G - 10 - bob + bob)
    if arm == "low":
        return (sx, sy), (sx + side_sign * 12, sy + 30), (sx + side_sign * 14, sy + 58)
    return (sx, sy), (sx + side_sign * 16, sy + 26), (sx + side_sign * 30, sy + 40)   # heap: arms flung out


def arm(S, sh, el, fi, k, hot, chained, opened, side_sign):
    fire_line(S, sh[0], sh[1], el[0], el[1], 15, k, hot)
    fire_line(S, el[0], el[1], fi[0], fi[1], 13, k + 1, hot)
    gap = 3 if opened else 1
    # plate segments, leaving fire at the elbow
    def short(a, b, f):
        return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
    p0, p1 = short(sh, el, 0.15), short(sh, el, 1 - 0.12 * gap)
    iron_line(S, p0[0], p0[1], p1[0], p1[1], 13 - gap, rune=True, k=k)
    q0, q1 = short(el, fi, 0.12 * gap), short(el, fi, 0.82)
    iron_line(S, q0[0], q0[1], q1[0], q1[1], 12 - gap, rune=True, k=k + 3)
    # elbow couter
    ellf(S, el[0], el[1], 5, 5, lambda x, y, u, v: iron(u, v))
    S.set(el[0] - 1, el[1] - 2, "stone_hi")
    # manacle at the wrist (rune band)
    wx, wy = short(el, fi, 0.84)
    ellf(S, wx, wy, 7, 4, lambda x, y, u, v: "sky" if abs(v) < 0.35 and (x + k) % 3 else iron(u, v))
    # gauntlet fist
    ellf(S, fi[0], fi[1] + 2, 7, 6.5, lambda x, y, u, v: iron(u, v))
    for j in range(-2, 3):
        S.set(fi[0] + j * 2, fi[1] - 2, "stone_hi" if j % 2 == 0 else "stone")
    if chained:
        ex = max(6, min(W - 7, fi[0] + side_sign * 14))
        ey = min(G - 16, max(wy + 20, G - 30))
        chain(S, wx, wy + 2, ex, ey, k)                           # to the anvil-pillar behind him
        chain(S, ex, ey, max(5, min(W - 6, ex + side_sign * 8)), ey - 14, k)
    elif opened:
        chain(S, wx, wy + 2, wx + side_sign * 8, wy + 16, k)     # torn chain stubs swinging


def front(S, face, anim, i, chained, opened):
    P = pose(anim, i)
    b, k = P["bob"], i + (4 if anim == "walk" else 0)
    hot = P["core"] * (1.25 if opened else 1.0)
    up = face == "up"
    if anim == "die" and i == 3:
        heap(S, face, k, chained, opened)
        return
    spl = P["split"] + (3 if opened else 0)
    # ---------------- legs (fire under greaves), or kneel
    for sd in (-1, 1):
        kneel = P["kneel"] and sd == -1
        lx = CX + sd * 18 + (P["step"] * 4 * sd if not up else -P["step"] * 4 * sd)
        lift = 2 if (P["step"] and P["step"] == sd) else 0
        if kneel:                                      # near knee on the ground
            fire_line(S, lx, 150 + b // 3, lx - 4, G - 6, 16, k, hot)
            iron_line(S, lx, 150 + b // 3, lx - 3, G - 10, 14, rune=True, k=k)
            ellf(S, lx - 2, G - 4, 10, 4, lambda x, y, u, v: iron(u, v))
            continue
        top = 146 + b // 2 if not P["kneel"] else 150 + b // 3
        fire_line(S, lx, top, lx, G - 8 - lift, 18, k, hot)
        iron_line(S, lx, top + 2, lx, 164 - lift, 16 - (2 if opened else 0), rune=True, k=k)     # cuisse
        ellf(S, lx, 168 - lift, 9, 6, lambda x, y, u, v: iron(u, v))                             # poleyn
        S.set(lx - 3, 166 - lift, "stone_hi"); S.set(lx, 165 - lift, "stone_hi")
        iron_line(S, lx, 172 - lift, lx, G - 6 - lift, 15, rune=True, k=k + 2)                    # greave
        for y in range(G - 6 - lift, G + 1 - lift):                                               # sabaton
            hw = 10 + (y - (G - 6 - lift)) // 2
            for x in range(lx - hw, lx + hw + 1):
                S.set(x, y, iron((x - lx) / hw, -1 if y == G - 6 - lift else 0.3))
        for x in range(lx - 10, lx + 11, 4):
            S.set(x, G - 4 - lift, "stone_hi")
    # ---------------- torso fire body
    ty = 64 + b
    ellf(S, CX, ty + 34, 34, 42, lambda x, y, u, v: fire(x, y, k, hot))
    # ---------------- tassets (hanging plates) with a dark war-belt
    for j, sd in enumerate((-1, 1)):
        x0 = CX + (sd * 2 if sd > 0 else -30) + sd * spl
        plate_rect(S, x0, ty + 66, x0 + 28, ty + 86, k, curve=3)
        plate_rect(S, x0 + 2 * sd + 2, ty + 80, x0 + 26 + 2 * sd, ty + 96, k + 1, curve=3)
    rect(S, CX - 30, ty + 60, CX + 30, ty + 66, "shadow")
    for x in range(CX - 30, CX + 31, 5):
        S.set(x, ty + 61, "stone_lo")
    rect(S, CX - 5, ty + 59, CX + 5, ty + 67, "stone_lo"); rect(S, CX - 3, ty + 61, CX + 3, ty + 65, "roof_lo")
    S.set(CX, ty + 63, fire(CX, ty, k, hot * 1.4))
    # ---------------- breastplate (two halves that can open) + layered abdomen lames
    if up:
        plate_rect(S, CX - 30 - spl, ty + 4, CX - 1 - spl, ty + 42, k, curve=4)
        plate_rect(S, CX + 1 + spl, ty + 4, CX + 30 + spl, ty + 42, k, curve=4)
        for j in range(3):
            plate_rect(S, CX - 26, ty + 42 + j * 6, CX + 26, ty + 48 + j * 6, k + j, curve=2, rivets=False)
        for y in range(ty + 4, ty + 60):                       # spine ridge
            S.set(CX, y, "stone_lo" if not spl else fire(CX, y, k, hot * 1.4))
    else:
        for sd in (-1, 1):
            x0 = CX - 30 - spl if sd < 0 else CX + 1 + spl
            x1 = CX - 1 - spl if sd < 0 else CX + 30 + spl
            for y in range(ty + 6, ty + 44):
                f = (y - ty - 6) / 38
                inset = int(6 * f * f)
                for x in range(x0 + (inset if sd < 0 else 0), x1 - (0 if sd < 0 else inset) + 1):
                    u = ((x - x0) / max(1, x1 - x0)) * 2 - 1
                    c = "stone_lo" if (sd < 0 and u < -0.55) else "shadow" if u < 0.35 else "timber_lo"
                    if y < ty + 8:
                        c = "stone"
                    elif y < ty + 10:
                        c = "stone_lo"
                    S.set(x, y, c)
            for (rx, ry) in ((x0 + 4, ty + 10), (x1 - 4, ty + 10), (x0 + 4, ty + 26), (x1 - 4, ty + 26)):
                S.set(rx, ry, "stone_hi")
            # rune seam along the inner edge of each half (the binding)
            ex = x1 if sd < 0 else x0
            for y in range(ty + 7, ty + 44):
                S.set(ex, y, "white" if (y + k * 2) % 9 == 0 else "sky")
        for j in range(3):                                      # abdomen lames
            plate_rect(S, CX - 25 + j, ty + 44 + j * 5, CX + 25 - j, ty + 49 + j * 5, k + j, curve=2, rivets=False)
        # the central seam: fire leaking through (wider when opened / split)
        gw = 1 + spl
        for y in range(ty + 8, ty + 60):
            for x in range(CX - gw, CX + gw + 1):
                if abs(x - CX) <= gw:
                    S.set(x, y, fire(x, y, k, hot * (1.6 if abs(x - CX) < 2 else 1.1)))
        if spl >= 4 or (anim == "die" and i >= 2):              # the white-hot ember heart, beating
            r = 5 + (i % 2) * 2
            ellf(S, CX, ty + 24, r, r + 1, lambda x, y, u, v: "white" if u * u + v * v < 0.35 else "flower_gold" if u * u + v * v < 0.7 else "lamp")
    # ---------------- arms + chains
    for sd in (-1, 1):
        a = P["la"][0] if sd < 0 else P["ra"][0]
        sh, el, fi = fists(face, a, sd, b)
        if P["kneel"] and a == "low" and sd == 1:
            fi = (fi[0] + 2, G - 20)                         # far hand braced low on the knee-line
        arm(S, sh, el, fi, k, hot, chained, opened, sd)
    # ---------------- pauldrons (layered, lift when opened)
    for sd in (-1, 1):
        px, py = CX + sd * (36 + spl), ty + 10 - (3 if opened else 0)
        for j in range(3):
            ellf(S, px + sd * j * 3, py + j * 7, 19 - j * 2, 10 - j, lambda x, y, u, v: iron(u * sd if sd < 0 else u, v))
            for x in range(px - 16 + j * 3 + sd * j * 3, px + 17 - j * 3 + sd * j * 3):
                S.set(x, py + j * 7 + 9 - j, "white" if (x + k * 3 + j) % 10 == 0 else "sky")
        for j in range(-2, 3):
            S.set(px + j * 6, py - 6, "stone_hi")
        if opened:
            flame_tongues(S, px, py - 9, 3, 6, 12, k, hot)
    # ---------------- helm
    hy = 46 + b
    if opened and not up:
        flame_tongues(S, CX, hy - 18, 3, 6, 10, k + 2, hot)
    helm(S, face, CX, hy, k, hot=opened or P["core"] > 1.2)
    # ---------------- slam shockwave sparks at the fists
    if P["shock"]:
        for j in range(14):
            a = math.pi * (j / 13)
            r = 18 + 10 * hsh("sh", j)
            for sd in (-1, 1):
                x = CX + sd * 16 + math.cos(a) * r * sd
                y = G - 6 - math.sin(a) * r * 0.5
                S.set(x, y, "flower_gold" if j % 3 else "white")


def side_view(S, anim, i, chained, opened):
    """left profile: the hulk faces left, near (left) arm in front, the far arm's chain trailing behind"""
    P = pose(anim, i)
    b, k = P["bob"], i + (4 if anim == "walk" else 0)
    hot = P["core"] * (1.25 if opened else 1.0)
    if anim == "die" and i == 3:
        heap(S, "left", k, chained, opened)
        return
    spl = P["split"] + (3 if opened else 0)
    cx = CX + 1
    ty = 64 + b
    # far arm (behind the body) + its chain to the pillar behind
    fsh, fel, ffi = (cx + 14, 80 + b), (cx + 24, 108 + b), (cx + 22, 134 + b)
    if P["la"][0] == "raise":
        fel, ffi = (cx + 10, 52 + b), (cx - 6, 30 + b)
    elif P["la"][0] == "slam":
        fel, ffi = (cx - 4, 114 + b), (cx - 22, G - 16)
    elif P["la"][0] == "ready":
        fel, ffi = (cx + 8, 104 + b), (cx - 8, 96 + b)
    arm(S, fsh, fel, ffi, k, hot * 0.8, chained, opened, 1)
    # legs: stride about cx; sabatons symmetric about each leg
    for sd in (1, -1):
        off = P["step"] * 8 * sd
        lx = cx + off + 4 * sd
        if P["kneel"] and sd == -1:                       # near knee down in front
            fire_line(S, cx - 4, 150 + b // 3, cx - 20, 170, 17, k, hot)
            iron_line(S, cx - 4, 152 + b // 3, cx - 20, 168, 15, rune=True, k=k)
            iron_line(S, cx - 20, 172, cx - 16, G - 6, 14, rune=True, k=k)
            ellf(S, cx - 18, G - 3, 11, 4, lambda x, y, u, v: iron(u, v))
            continue
        if P["kneel"] and sd == 1:                        # far knee on the ground behind
            fire_line(S, cx + 4, 150 + b // 3, cx + 20, G - 6, 17, k, hot)
            iron_line(S, cx + 4, 152 + b // 3, cx + 18, G - 10, 15, rune=True, k=k)
            ellf(S, cx + 20, G - 3, 11, 4, lambda x, y, u, v: iron(u, v))
            continue
        fire_line(S, lx, 146 + b // 2, lx, G - 8, 18, k, hot)
        iron_line(S, lx, 148 + b // 2, lx, 164, 16, rune=True, k=k)
        ellf(S, lx - 2, 168, 9, 6, lambda x, y, u, v: iron(u, v))
        S.set(lx - 6, 166, "stone_hi")
        iron_line(S, lx, 172, lx, G - 6, 15, rune=True, k=k + 2)
        for y in range(G - 6, G + 1):
            for x in range(lx - 11 - (y - G + 6) // 2, lx + 10):
                S.set(x, y, iron(-0.7 if y == G - 6 else 0.0))
        for x in range(lx - 10, lx + 9, 4):
            S.set(x, G - 4, "stone_hi")
    # fire body
    ellf(S, cx, ty + 36, 32, 44, lambda x, y, u, v: fire(x, y, k, hot))
    # tassets + war-belt
    plate_rect(S, cx - 28, ty + 66, cx + 26, ty + 86, k, curve=3)
    plate_rect(S, cx - 26, ty + 80, cx + 24, ty + 96, k + 1, curve=3)
    rect(S, cx - 30, ty + 60, cx + 28, ty + 66, "shadow")
    for x in range(cx - 30, cx + 29, 5):
        S.set(x, ty + 61, "stone_lo")
    rect(S, cx - 32, ty + 59, cx - 22, ty + 67, "stone_lo"); rect(S, cx - 30, ty + 61, cx - 24, ty + 65, "roof_lo")
    # breastplate in profile: a deep barrel chest bulging left, a back plate
    for y in range(ty + 4, ty + 60):
        f = (y - ty - 4) / 56
        x0 = cx - 30 - int(8 * math.sin(f * math.pi))
        x1 = cx + 24 - int(6 * f)
        for x in range(x0, x1 + 1):
            u = (x - x0) / max(1, x1 - x0) * 2 - 1
            c = "stone_lo" if u < -0.7 else "shadow" if u < 0.3 else "timber_lo"
            if y < ty + 7:
                c = "stone"
            S.set(x, y, c)
    for y in range(ty + 14, ty + 58, 8):                    # layered lames, rune seams, fire leaking between
        f = (y - ty - 4) / 56
        x0 = cx - 30 - int(8 * math.sin(f * math.pi))
        for x in range(x0 + 1, cx + 23):
            S.set(x, y, "white" if (x + k * 3) % 11 == 0 else "sky")
            if spl:
                S.set(x, y + 1, fire(x, y, k, hot))
    for y in range(ty + 8, ty + 58, 9):
        S.set(cx - 26, y, "stone_hi"); S.set(cx + 18, y, "stone_hi")
    if spl:                                                  # the chest plates gape at the front
        for y in range(ty + 8, ty + 56):
            f = (y - ty - 4) / 56
            x0 = cx - 30 - int(8 * math.sin(f * math.pi))
            for x in range(x0, x0 + 2 + spl // 2):
                S.set(x, y, fire(x, y, k, hot * 1.4))
    if spl >= 4:
        ellf(S, cx - 32, ty + 28, 5, 6, lambda x, y, u, v: "white" if u * u + v * v < 0.4 else "flower_gold")
    # pauldron (layered) on the near shoulder
    for j in range(3):
        oy = ty + 8 + j * 8 - (3 if opened else 0)
        ellf(S, cx - 2 - j * 2, oy, 22 - j * 2, 11 - j, lambda x, y, u, v: iron(u, v))
        for x in range(cx - 20 - j, cx + 18 - j * 3):
            S.set(x, oy + 9 - j, "white" if (x + k * 3) % 10 == 0 else "sky")
    for j in range(-2, 3):
        S.set(cx - 2 + j * 7, ty + 1 - (3 if opened else 0), "stone_hi")
    # near arm in front
    a = P["la"][0]
    sh = (cx - 6, 82 + b)
    if a == "rest":
        el, fi = (cx - 14, 110 + b), (cx - 20, 136 + b)
    elif a == "ready":
        el, fi = (cx - 22, 104 + b), (cx - 36, 94 + b)
    elif a == "raise":
        el, fi = (cx - 20, 52 + b), (cx - 34, 28 + b)
    elif a == "slam":
        el, fi = (cx - 26, 114 + b), (cx - 40, G - 14)
    else:
        el, fi = (cx - 16, 114 + b), (cx - 20, 142 + b)
    arm(S, sh, el, fi, k, hot, chained, opened, -1)
    if opened:
        flame_tongues(S, cx, ty - 6, 3, 7, 12, k, hot)
        flame_tongues(S, cx, 46 + b - 20, 2, 6, 9, k + 2, hot)
    helm(S, "left", cx - 6, 46 + b, k, hot=opened or P["core"] > 1.2)
    if P["shock"]:
        for j in range(12):
            a = math.pi * (j / 11)
            r = 16 + 10 * hsh("ss", j)
            S.set(cx - 40 + math.cos(a) * r, G - 8 - math.sin(a) * r * 0.5, "flower_gold" if j % 3 else "white")


def heap(S, face, k, chained, opened):
    """die frame 27: the plates have split and slumped into a kneeling heap; the white-hot ember heart beats in the open chest"""
    cy = G - 30
    ellf(S, CX, cy + 8, 40, 22, lambda x, y, u, v: fire(x, y, k, 0.8))
    for j, (dx, dy, w, h) in enumerate(((-40, 8, 26, 14), (14, 10, 26, 14), (-30, -14, 22, 16), (8, -12, 22, 16), (-14, 16, 28, 10))):
        plate_rect(S, CX + dx, cy + dy, CX + dx + w, cy + dy + h, k + j, curve=2)
    ellf(S, CX, cy + 2, 7, 8, lambda x, y, u, v: "white" if u * u + v * v < 0.4 else "flower_gold" if u * u + v * v < 0.75 else "lamp")
    helm(S, face if face != "up" else "up", CX - 4, cy - 26, k, hot=False, eyes=False)
    for sd in (-1, 1):                                      # gauntlets on the floor
        ellf(S, CX + sd * 46, G - 5, 8, 5, lambda x, y, u, v: iron(u, v))
    rect(S, CX - 50, G - 1, CX + 50, G, "shadow")


def gorrak(s, face, anim, i):
    S = Safe(s)
    if face == "left":
        side_view(S, anim, i, chained=True, opened=False)
    else:
        front(S, face, anim, i, chained=True, opened=False)


def gorrak_unbuckled(s, face, anim, i):
    S = Safe(s)
    if face == "left":
        side_view(S, anim, i, chained=False, opened=True)
    else:
        front(S, face, anim, i, chained=False, opened=True)
