"""hd2d boss sheets (stage 3): big foes drawn NATIVELY at their size on their own sheet (never an upscaled small sprite).

Style-lock boss-scale override: mini-bosses / rares ~2.5x the player's height, bosses 5x+. Same texel density,
hard alpha, 1 px ink outline, biome palette. A sheet uses the main atlas's column layout (idle 0-3, walk 4-7,
attack 12-15, die 24-27) with its own frame size, so the engine only swaps frame size + texture per role.

    python3 tools/sprite/boss_sheet.py --biome cozy-village --roles eldergolem --out <area>/public/art/sprite

  eldergolem  Mossheart, the elder golem (Mossglen mini-boss), 50x80 frame (~2.5x a 32 px hero)
  elderwraith / deathlord / sporemother  Stage 5 procedural rare bodies (2.2-2.4x), same 50x80 frame (game/rares.js)
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sprite as SP  # noqa: E402
from roles_enemies import ell, rect, shader  # noqa: E402

BOSS = {
    "eldergolem": {"frame": (50, 80), "scale": 2.5, "anims": ("idle", "walk", "attack", "die"),
                   "desc": "Mossheart the elder golem (mini-boss, ~2.5x): dark ancient stone blocks, amber crystal crown, glowing gold rune glyphs, glow-flowers in thick moss"},
    # Stage 5 procedural rares: base bodies drawn natively on the same 50x80 frame (2-3x the hero); the element affix is
    # their aura + light colour (game/rares.js), so one body serves every element and trait
    "elderwraith": {"frame": (50, 80), "scale": 2.4, "anims": ("idle", "walk", "attack", "die"),
                    "desc": "Elder wraith (rare, ~2.4x): towering hooded spectre, tattered layered robes, cold-fire crown, skeletal hands, a cold-fire chain lantern"},
    "deathlord": {"frame": (50, 80), "scale": 2.4, "anims": ("idle", "walk", "attack", "die"),
                  "desc": "Death Lord (rare, ~2.4x): skeleton knight in dark rune plate, horned helm over a bone skull, spiked pauldrons, deep-red cape, rune greatsword"},
    "sporemother": {"frame": (50, 80), "scale": 2.2, "anims": ("idle", "walk", "attack", "die"),
                    "desc": "Sporemother (rare, ~2.2x): giant spore elemental, floating moss mound under a wide rose toadstool cap, gold lamp eyes, root tendrils, spore ring"},
}


def eldergolem(s, face, anim, i):
    W, H = s.w, s.h
    KX, KY = 2.05, 2.5                                 # golem-space (20x32) -> native 50x80 coordinates, drawn fresh at full res
    X = lambda x: 25 + (x - 9.5) * KX                  # noqa: E731
    Y = lambda y: (H - 2) - (30 - y) * KY              # noqa: E731
    def E(cx, cy, rx, ry, col, fn=None):
        ell(s, X(cx), Y(cy), rx * KX, ry * KY, col, fn)
    def R(x0, y0, x1, y1, col):
        rect(s, round(X(x0)), round(Y(y0)), round(X(x1)), round(Y(y1)), col)
    hi, mid, lo, deep = "stone", "stone_lo", "shadow", "ink"
    rune, hot = "lamp", "white"
    b = 0; lift_l = lift_r = 0; arms = "rest"; crack = 0; dust = False
    if anim == "idle":
        b = [0, 0, 0.5, 0.5][i]
    elif anim == "walk":
        b = [0, 0.5, 0, 0.5][i]; lift_l, lift_r = [(0, 0), (0.5, 0), (0, 0), (0, 0.5)][i]   # a heavy stomp: the foot barely leaves the ground
    elif anim == "attack":
        arms = ["up", "high", "slam", "mid"][i]; b = [0, -0.6, 1.0, 0.5][i]; dust = i == 2
    elif anim == "die":
        crack = i + 1; b = [0.5, 1.5, 0, 0][i]
        if crack >= 3:
            rune, hot = "flower_gold", "flower_gold"
    side = face == "left"
    if anim == "die" and i >= 2:                       # a heap of dark stone blocks, moss, the last runes cooling
        top = 21 if i == 2 else 24
        E(9.5, 28, 9.2 if i == 2 else 8.4, 30 - top - 1.2, mid, shader(X(9.5), 9 * KX, hi, mid, lo))
        for (x, y) in ((4, 26), (8, 24), (13, 25), (15.5, 28), (6, 29), (11, 28), (2.5, 29)):
            if y >= top:
                R(x, y, x + 1.6, y + 0.8, lo); R(x, y, x + 1.6, y, hi)
        for (x, y) in ((7, top + 1), (12, top + 1.5), (3, 29), (16, 28.5)):
            R(x, y, x + 1, y + 0.4, "moss"); s.set(round(X(x)), round(Y(y)) - 1, "grass_hi")
        if i == 2:
            for (x, y) in ((9, 26), (14, 27), (5, 27.5)):
                s.set(round(X(x)), round(Y(y)), "lamp"); s.set(round(X(x)) + 1, round(Y(y)), "flower_gold")
        R(1.5, 30, 17.5, 30, lo)
        return
    # legs: stacked blocks
    legs = [(5.6, lift_l), (11, lift_r)] if side else [(3.6, lift_l), (12, lift_r)]
    for lx, lift in legs:
        R(lx, 24.6 + b, lx + 4, 30 - lift, lo if lx > 9 else mid)
        R(lx, 24.6 + b, lx + 4, 24.6 + b, hi)
        R(lx, 27.4 - lift, lx + 4, 27.4 - lift, deep)            # block seam
        R(lx - 0.3, 29.4 - lift, lx + 4.3, 30 - lift, lo)        # foot slab
    # body: a huge boulder torso with block seams
    bcx, rx = (10.5, 7.8) if side else (9.5, 8.4)
    E(bcx, 18 + b, rx, 7.8, mid, shader(X(bcx), rx * KX, hi, mid, lo))
    for k, yy in enumerate((14.5, 18, 21.5)):                # horizontal seams, offset blocks (ancient masonry)
        y = round(Y(yy + b))
        for x in range(round(X(bcx - rx + 1.2)), round(X(bcx + rx - 1.2))):
            if s.p[y][x]:
                s.set(x, y, deep if (x + k) % 9 else lo)
        for x0 in range(round(X(bcx - rx)) + 5 + 4 * k, round(X(bcx + rx)) - 3, 11):
            for y2 in range(y + 1, y + 8):
                if 0 <= y2 < H and s.p[y2][x0]:
                    s.set(x0, y2, deep)
    # head
    if side:
        E(12, 11 + b, 5.8, 4.8, mid, shader(X(12), 5.8 * KX, hi, mid, lo))
        R(2.6, 8.8 + b, 9, 14 + b, mid); R(2.6, 8.8 + b, 3.6, 14 + b, hi); R(2.6, 8 + b, 9, 8.2 + b, hi)
        R(2, 10 + b, 8.4, 10.3 + b, lo); R(2.6, 13.8 + b, 8.4, 14 + b, lo)
    else:
        E(9.5, 9 + b, 4.8, 3.9, mid, shader(X(9.5), 4.8 * KX, hi, mid, lo))
        R(6, 11.4 + b, 13, 11.6 + b, lo)                     # jaw line
    # thick moss on head and shoulders, with grass blades and glow-flowers
    mossy = ((9.5, 6.6, 3.6), (4.2, 12, 2.6), (15, 12, 2.6)) if not side else ((12, 7, 4.4), (5, 8.2, 2.2))
    for (mx, my, mr) in mossy:
        E(mx, my + b, mr, 1.1, "moss")
        for k in range(int(mr * KX)):
            x = round(X(mx - mr) + k * 2); y = round(Y(my + b)) - 2 - (k % 3 == 0)
            s.set(x, y, "grass_hi" if k % 2 else "grass")
    flowers = ((6.2, 6), (12.6, 6.2), (3.4, 11.4), (16, 11.6), (10.4, 5.8)) if not side else ((11, 6.4), (14.4, 6.8), (5.4, 7.6))
    for k, (fx, fy) in enumerate(flowers):
        x, y = round(X(fx)), round(Y(fy + b))
        c = "flower_rose" if (k + i) % 2 else "flower_gold"
        s.set(x, y, c); s.set(x - 1, y, c); s.set(x + 1, y, c); s.set(x, y - 1, c); s.set(x, y, "white" if k % 2 == 0 else c)
    # crown of amber crystals (faceted shards: dark edge, gold body, white glint)
    crown = ((4.2, 7.4, 2.4), (6.4, 6.4, 3.0), (8.6, 7.2, 2.2)) if side else ((6.6, 5.6, 2.2), (8.6, 4.6, 3.0), (10.6, 4.6, 3.0), (12.6, 5.6, 2.2))
    for k, (cx, cy, hgt) in enumerate(crown):
        x0, yb = round(X(cx)), round(Y(cy + b))
        n = round(hgt * KY)
        for d in range(n):
            w = max(0, 2 - d * 3 // n)
            for x in range(x0 - w, x0 + w + 1):
                s.set(x, yb - d, "flower_gold" if x > x0 else rune)
            s.set(x0 + w, yb - d, "timber")
        s.set(x0 - 1, yb - n + 2, hot if (k + i) % 2 == 0 else rune); s.set(x0, yb - n + 1, hot)
    # eyes + rune glyphs
    if face == "down":
        for ex in (7.6, 11.4):
            x, y = round(X(ex)), round(Y(9 + b))
            rect(s, x - 1, y, x + 1, y + 1, rune if crack < 3 else lo); s.set(x, y, hot if crack < 2 else rune)
            rect(s, x - 2, y - 1, x + 2, y - 1, deep)
        s.set(round(X(9.5)), round(Y(7.6 + b)), hot); s.set(round(X(9.5)) + 1, round(Y(7.6 + b)), rune)   # third eye
        cx = round(X(9.5))
        for k, y in enumerate(range(round(Y(13.6 + b)), round(Y(24 + b)))):   # the heart seam: a zig-zag rune channel
            x = cx + (1 if (k // 3) % 2 else -1)
            s.set(x, y, hot if (k + crack + i) % 7 == 0 else rune); s.set(x + 1, y, "flower_gold")
        for (gx, gy) in ((4.6, 16), (14.4, 16.4), (5.4, 21), (13.6, 20.6)):   # four glyphs on the flanks: little runic marks
            x, y = round(X(gx)), round(Y(gy + b))
            for (dx, dy) in ((0, 0), (0, 1), (0, 2), (1, 1), (-1, 1), (1, -1)):
                s.set(x + dx, y + dy, rune)
            s.set(x, y + 1, hot)
        for lx in (5.6, 14):
            x, y = round(X(lx)), round(Y(26.4 + b))
            s.set(x, y, rune); s.set(x, y + 1, rune); s.set(x + 1, y + 1, hot)
    elif face == "up":
        for k, y in enumerate(range(round(Y(14 + b)), round(Y(22 + b)))):
            s.set(round(X(9.6)) + (k % 2), y, lo)
        for (gx, gy) in ((6.4, 13.4), (12.8, 13.4), (8, 19), (11.2, 19)):
            x, y = round(X(gx)), round(Y(gy + b))
            s.set(x, y, rune); s.set(x + 1, y, rune); s.set(x, y + 1, hot); s.set(x - 1, y + 1, rune)
    else:
        x, y = round(X(4)), round(Y(11 + b))
        rect(s, x - 1, y, x + 1, y + 1, rune if crack < 3 else lo); s.set(x - 1, y, hot)
        rect(s, x - 2, y - 1, x + 2, y - 1, deep)
        for k, yy in enumerate(range(round(Y(15.6 + b)), round(Y(24 + b)))):
            s.set(round(X(9.6)) + (k // 3) % 2, yy, hot if (k + i) % 6 == 0 else rune)
        for (gx, gy) in ((12.6, 15), (13.6, 19.4)):
            x, y = round(X(gx)), round(Y(gy + b))
            for (dx, dy) in ((0, 0), (0, 1), (0, 2), (1, 1)):
                s.set(x + dx, y + dy, rune)
    if crack:                                           # hit / death cracks spreading across the blocks
        pts = [(6, 14), (7, 15), (7.6, 16), (13, 20), (12.4, 21), (11.6, 22.4)]
        for (x, y) in pts[: 2 + crack]:
            s.set(round(X(x)), round(Y(y + b)), "white" if crack == 1 else deep)
    # arms: three-block arms ending in huge fists
    def fist(cx, cy, r=2.8):
        E(cx, cy, r, r * 0.92, mid, shader(X(cx), r * KX, hi, mid, lo))
        x, y = round(X(cx)), round(Y(cy))
        rect(s, x - 3, y, x + 2, y, deep)               # knuckle line
        s.set(x - 2, y - 2, rune if crack < 3 else lo)  # a rune on each fist
    if side:
        if arms == "rest":
            sw = 0.8 if anim == "walk" and i % 2 else 0
            R(4.6, 15 + b, 7.4, 21.6 + b + sw, mid); R(4.6, 15 + b, 5.2, 21.6 + b, hi); R(4.6, 18 + b, 7.4, 18.2 + b, deep)
            fist(6, 24.4 + b + sw, 3.0)
        elif arms in ("up", "high"):
            fist(7, 3.6 + b if arms == "high" else 6.6 + b); R(7.8, 8 + b, 9.6, 13 + b, mid)
        elif arms == "slam":
            fist(3.6, 27, 3.0); R(4.6, 20 + b, 7.4, 24 + b, mid)
        else:
            R(4.6, 15 + b, 7.4, 18 + b, mid); fist(3.6, 20 + b)
    else:
        if arms == "rest":
            sw = 0.8 if anim == "walk" and i % 2 else 0
            for (ax, s2) in ((1.6, sw), (17.4, -sw)):
                R(ax - 1.2, 13 + b, ax + 1.2, 17 + b + s2, mid if ax < 9 else lo)
                fist(ax, 19.4 + b + s2)
        elif arms in ("up", "high"):
            y = 2.8 + b if arms == "high" else 5.8 + b
            fist(4.8, y); fist(14.2, y)
            R(3.8, y + 2.4, 5.4, 12 + b, mid); R(13.6, y + 2.4, 15.2, 12 + b, lo)
        elif arms == "slam":
            fist(4.8, 27, 3.0); fist(14.2, 27, 3.0)
            R(3.8, 20 + b, 5.4, 24.6, mid); R(13.6, 20 + b, 15.2, 24.6, lo)
        else:
            fist(2.6, 15 + b); fist(16.4, 15 + b)
    if dust:
        for (x, y) in ((0, 29), (1, 27.6), (18.6, 28.4), (19, 29.4), (9, 30), (-0.2, 30), (17.6, 30)):
            s.set(round(X(x)), round(Y(y)), "plaster_lo"); s.set(round(X(x)) + 1, round(Y(y)), "plaster_hi")
        s.set(round(X(10)), round(Y(29)), "flower_gold")


# ------------------------------------------------------------------ Stage 5 rares (2-3x the hero, drawn natively at 50x80)
class _Rnd:
    """lets the rare drawings place pixels at float coordinates (rounded once, here)"""
    def __init__(self, s):
        self.s, self.p, self.w, self.h = s, s.p, s.w, s.h

    def set(self, x, y, c):
        if c is None:
            return
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.w and 0 <= y < self.h:
            self.s.set(x, y, c)

def _tongue(s, x, y, h, flick, fire=("white", "sky", "flower_blue")):
    """a little cold-fire tongue rising from (x, y), h px tall"""
    for d in range(h):
        w = 1 if d < h * 0.55 else 0
        sway = 1 if (d + flick) % 4 == 0 and d > 1 else 0
        for dx in range(-w, w + 1):
            s.set(x + dx + sway, y - d, fire[min(2, (d * 3) // max(1, h))] if dx == 0 else fire[2])


def elderwraith(s, face, anim, i):
    """Elder wraith (rare, ~2.4x): a towering hooded spectre in layered tattered robes, a crown of cold-fire tongues on
    the hood, skeletal hands, a cold-fire lantern swinging on a chain; attack = both hands raise a cold-fire orb"""
    s = _Rnd(s)
    W, H = s.w, s.h
    b = [0, 1, 1, 0][i] if anim == "idle" else [0, 1, 0, -1][i] if anim == "walk" else [0, -1, -2, 0][i] if anim == "attack" else [-1, -2, -3, 0][i]
    hands = "up" if anim == "attack" else "low"
    orb = [2, 4, 6, 0][i] if anim == "attack" else 0
    fade = i + 1 if anim == "die" else 0
    flick = i
    hi, mid, lo = "flower_blue", "cloth", "ink"
    fire = ("white", "sky", "flower_blue")
    side = face == "left"
    if anim == "die" and i == 3:                       # a guttering cold-fire pool and the dropped lantern
        ell(s, 25, 74, 12, 3.2, "flower_blue")
        ell(s, 25, 74, 7, 1.8, "sky")
        for (x, y) in ((19, 73), (25, 72), (31, 74), (22, 75), (28, 73)):
            s.set(x, y, "white")
        for k, x in enumerate((17, 23, 29, 34)):
            _tongue(s, x, 72, 4 + (k + i) % 3, k)
        rect(s, 34, 70, 38, 75, "timber_lo"); rect(s, 35, 71, 37, 74, "flower_blue"); s.set(36, 72, "white")
        return
    cx = 23.5 if side else 25
    # tail: a cold-fire wisp tapering from under the robe to the ground (blue rim, sky body, white sparks)
    t0 = 50 + b
    for y in range(t0, 78):
        t = (y - t0) / max(1, 77 - t0)
        w = max(0, int(round(7.5 * (1 - t) ** 1.1)))
        wob = (1 if (y + flick) % 6 < 3 else -1) * t * 1.8
        for x in range(int(cx + wob - w), int(cx + wob + w) + 1):
            e = abs(x - (cx + wob)) / max(1, w)
            c = "flower_blue" if e > 0.55 else "sky"
            if e < 0.3 and (x * 3 + y + flick) % 5 == 0:
                c = "white"
            s.set(x, y, c)
    s.set(int(cx), 77, "sky")
    # layered robe: broad at the shoulders, drawn in towards the tail, ragged strips at the hem
    for y in range(30 + b, 60 + b):
        t = (y - 30 - b) / 30
        half = 12 + math.sin(min(1.0, t * 1.6) * math.pi / 2) * 3 - max(0.0, t - 0.55) * 14
        for x in range(int(cx + 0.5 - half), int(cx + 0.5 + half)):
            u = (x - (cx - half)) / (2 * half)
            if y > 48 + b and ((x * 7 + flick) % 6) < (y - 48 - b) // 2:   # rags
                continue
            c = hi if u < 0.2 else mid
            if u > 0.7:
                c = mid if (x + y) % 2 else lo
            if (x + 2 * y) % 9 == 0 and 0.3 < u < 0.66:
                c = lo
            s.set(x, y, c)
    # rune trim down the front + cold-fire at the hem tips
    if face != "up":
        tx = int(cx - 3) if side else int(cx)
        for y in range(34 + b, 54 + b, 2):
            s.set(tx, y, "sky" if (y // 2 + flick) % 3 else "white")
    for x in range(int(cx - 16), int(cx + 17)):
        for y in range(70, 30, -1):
            if 0 <= x < W and s.p[y][x] in (hi, mid, lo) and y > 50 + b:
                if (x + flick) % 3 == 0:
                    s.set(x, y + 1, fire[(x + flick) % 3])
                break
    # mantle: a heavy cowl over the shoulders
    ell(s, cx, 31 + b, 13 if not side else 11, 5.5, mid, shader(cx, 13, hi, mid, mid))
    for x in range(int(cx - 12), int(cx + 13), 3):
        s.set(x, int(36 + b), lo)
    # hood
    hx = cx - 1.5 if side else cx
    ell(s, hx, 19 + b, 8.5, 10, mid, shader(hx, 8.5, hi, mid, mid))
    for d in range(5):                                  # pointed hood tip
        s.set(int(hx) + (d // 2 if not side else d // 2 + 1), 9 + b - d, mid)
    # crown of cold-fire tongues around the hood
    for k, (dx, hgt) in enumerate(((-7, 4), (-4, 6), (0, 7), (4, 6), (7, 4)) if not side else ((-5, 5), (-1, 7), (3, 5))):
        _tongue(s, int(hx + dx), int(12 + b + abs(dx) * 0.6), hgt + (k + flick) % 2, k + flick)
    eyes = "white" if fade < 2 else "sky"
    if face == "down":
        ell(s, hx, 21 + b, 5.5, 5.5, "ink")
        for ex in (hx - 2.5, hx + 2.5):
            s.set(int(ex), int(20 + b), eyes); s.set(int(ex) + 1, int(20 + b), eyes)
            s.set(int(ex), int(21 + b), "sky"); s.set(int(ex) + 1, int(21 + b), "flower_blue")
        s.set(int(hx), int(24 + b), "flower_blue")
    elif face == "up":
        for y in range(12 + b, 27 + b):
            s.set(int(hx) + 1, y, lo)
        s.set(int(hx) - 2, 14 + b, hi)
    else:
        ell(s, hx - 4, 21 + b, 3.5, 5, "ink")
        s.set(int(hx - 6), int(20 + b), eyes); s.set(int(hx - 5), int(20 + b), eyes); s.set(int(hx - 6), int(21 + b), "sky")
    # sleeves, skeletal hands, the chain lantern
    def hand(x, y):
        rect(s, x, y, x + 2, y + 1, "stone_hi"); s.set(x, y + 2, "stone"); s.set(x + 2, y + 2, "stone")
        s.set(x + 1, y - 1, fire[(x + flick) % 3])
    def lantern(x, y):
        for d in range(5):
            s.set(x + (1 if (d + i) % 4 == 0 else 0), y + d, "stone_lo")          # chain
        y += 5
        rect(s, x - 2, y, x + 2, y, "timber_lo"); rect(s, x - 2, y + 7, x + 2, y + 7, "timber_lo")
        rect(s, x - 2, y + 1, x + 2, y + 6, "flower_blue")
        rect(s, x - 1, y + 2, x + 1, y + 5, "sky"); s.set(x, y + 3 - (i % 2), "white"); s.set(x, y + 4, "white")
        s.set(x - 2, y + 1, "timber_lo"); s.set(x + 2, y + 1, "timber_lo"); s.set(x - 2, y + 6, "timber_lo"); s.set(x + 2, y + 6, "timber_lo")
    if hands == "low":
        sw = 1 if anim == "walk" and i % 2 else 0
        if side:
            rect(s, int(cx - 5), 33 + b, int(cx - 1), 46 + b, mid); hand(int(cx - 6), 47 + b)
            lantern(int(cx - 5), 50 + b + sw)
        else:
            rect(s, int(cx - 14), 33 + b, int(cx - 10), 47 + b, hi); rect(s, int(cx + 10), 33 + b, int(cx + 14), 47 + b, mid)
            hand(int(cx - 15), 48 + b); hand(int(cx + 12), 48 + b)
            lantern(int(cx + 13), 51 + b + sw)
    else:
        if side:
            rect(s, int(cx - 10), 30 + b, int(cx - 2), 33 + b, mid); hand(int(cx - 13), 29 + b)
            ox, oy = cx - 14, 26 + b
        else:
            rect(s, int(cx - 13), 26 + b, int(cx - 9), 34 + b, hi); rect(s, int(cx + 9), 26 + b, int(cx + 13), 34 + b, mid)
            hand(int(cx - 13), 23 + b); hand(int(cx + 10), 23 + b)
            ox, oy = cx, 8 + b
        if orb:
            ell(s, ox, oy, orb * 0.9 + 0.4, orb * 0.9 + 0.4, "flower_blue")
            ell(s, ox, oy, orb * 0.55, orb * 0.55, "sky")
            s.set(int(ox), int(oy), "white"); s.set(int(ox) - 1, int(oy) - 1, "white")
        else:
            for (dx, dy) in ((-5, 0), (5, 0), (0, -5), (0, 5), (-4, -4), (4, 4), (4, -4), (-4, 4)):
                s.set(int(ox) + dx, int(oy) + dy, "sky" if dx else "white")
    if fade:                                            # dissolving: holes through the robe, sparks rising
        for y in range(0, 76):
            for x in range(W):
                if s.p[y][x] and ((x * 73 + y * 151 + i * 37) % 11) < fade * 2:
                    s.p[y][x] = None
        for (x, y) in ((10, 10), (40, 14), (32, 4), (16, 2), (44, 30), (6, 28)):
            s.set(x, y + fade * 2, "sky" if x % 2 else "white")


def deathlord(s, face, anim, i):
    """Death Lord (rare, ~2.4x; the skeleton swordsman line's T4): a huge skeleton knight in dark rune plate, a horned
    helm over a bone skull with cold-fire eyes, spiked pauldrons, a tattered deep-red cape and a rune greatsword"""
    s = _Rnd(s)
    W, H = s.w, s.h
    b = 0; lift_l = lift_r = 0; sword = "rest"; slump = 0
    if anim == "idle":
        b = [0, 0, 1, 1][i]
    elif anim == "walk":
        b = [0, 1, 0, 1][i]; lift_l, lift_r = [(0, 0), (3, 0), (0, 0), (0, 3)][i]; sword = "carry"
    elif anim == "attack":
        sword = ["back", "over", "slash", "follow"][i]; b = [0, -1, 2, 1][i]
    elif anim == "die":
        slump = i + 1
    bone, bone_lo, bone_hi = "stone_hi", "stone", "plaster_hi"
    iron_hi, iron, iron_lo = "stone", "stone_lo", "shadow"
    cape, cape_lo = "roof_lo", "ink"
    rune = "sky" if slump < 3 else "flower_blue"
    side = face == "left"
    def blade(x0, y0, x1, y1, w=2):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for k in range(n):
            t = k / max(1, n - 1)
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            for d in range(-w, w + 1):
                if abs(x1 - x0) > abs(y1 - y0):
                    s.set(x, y + d, "white" if d == -w else bone if d < w else bone_lo)
                else:
                    s.set(x + d, y, "white" if d == -w else bone if d < w else bone_lo)
            if k % 4 == 2 and 0.15 < t < 0.85:
                s.set(x, y, rune)
    def hilt(x, y, horiz=False):
        if horiz:
            rect(s, x - 1, y - 4, x + 1, y + 4, iron_lo); rect(s, x + 2, y - 1, x + 6, y + 1, "timber"); s.set(x + 7, y, rune)
        else:
            rect(s, x - 5, y - 1, x + 5, y + 1, iron_lo); s.set(x - 5, y - 1, iron_hi); s.set(x + 5, y - 1, iron_hi)
            rect(s, x - 1, y + 2, x + 1, y + 7, "timber"); s.set(x, y + 8, rune); s.set(x, y + 3, "timber_hi")
    if anim == "die" and i >= 2:                       # a heap of dark plate and bones, the skull, the greatsword
        ell(s, 25, 73, 15, 4.5, iron, shader(25, 15, iron_hi, iron, iron_lo))
        for (x0, y0, x1) in ((12, 72, 22), (26, 70, 36), (16, 75, 32)):
            for x in range(x0, x1 + 1):
                s.set(x, y0, bone_hi if x % 3 else bone)
        ell(s, 34, 69, 5, 3, iron, shader(34, 5, iron_hi, iron, iron_lo))   # a pauldron
        sy = 62 if i == 2 else 66
        ell(s, 19, sy, 5.5, 5, bone, shader(19, 5.5, bone_hi, bone, bone_lo))
        rect(s, 16, sy + 1, 17, sy + 2, "ink"); rect(s, 21, sy + 1, 22, sy + 2, "ink")
        if i == 2:
            s.set(16, sy + 1, rune); s.set(21, sy + 1, rune)
        for k in range(2):                              # helm horns lying beside the skull
            s.set(12 - k, sy - 3 - k, iron_lo); s.set(26 + k, sy - 3 - k, iron_lo)
        blade(28, 76, 47, 76, 1); rect(s, 26, 74, 27, 78, iron_lo)
        rect(s, 6, 77, 44, 77, cape)
        return
    b += 2 if slump == 1 else 6 if slump == 2 else 0
    # cape behind (wide, tattered)
    for y in range(28 + b, 72):
        t = (y - 28 - b) / 44
        half = 12 + t * 6 if face != "up" else 13 + t * 7
        for x in range(int(25 - half), int(25 + half) + 1):
            if y > 64 and ((x * 5) % 7) < (y - 64):
                continue
            s.set(x, y, cape if (x + y) % 9 else cape_lo)
    # legs: plate greaves over bone, iron sabatons
    lxs = (19, 27) if side else (16, 28)
    for lx, lift in zip(lxs, (lift_l, lift_r)):
        rect(s, lx, 54 + b, lx + 5, 74 - lift, iron)
        rect(s, lx, 54 + b, lx, 74 - lift, iron_hi); rect(s, lx + 5, 54 + b, lx + 5, 74 - lift, iron_lo)
        rect(s, lx, 63 - lift // 2, lx + 5, 64 - lift // 2, iron_lo); s.set(lx + 2, 63 - lift // 2, rune)   # knee cop
        rect(s, lx - (2 if side else 1), 75 - lift, lx + 6, 78 - lift, iron_lo); rect(s, lx - (2 if side else 1), 75 - lift, lx + 6, 75 - lift, iron)
    # faulds (skirt plates)
    for k, y in enumerate((50, 53)):
        rect(s, 14 + k, y + b, 36 - k, y + 2 + b, iron if k == 0 else iron_lo)
        rect(s, 14 + k, y + b, 36 - k, y + b, iron_hi)
    # breastplate with a cold-fire rune and visible ribs under the gorget
    bcx = 24 if side else 25
    ell(s, bcx, 40 + b, 11.5 if not side else 9.5, 11, iron, shader(bcx, 11.5, iron_hi, iron, iron_lo))
    if face == "down":
        for k, y in enumerate(range(31 + b, 37 + b, 2)):
            rect(s, 21, y, 29, y, bone if k % 2 == 0 else bone_lo)
        rect(s, 24, 30 + b, 26, 37 + b, bone_lo)
        rx0, ry0 = 25, 42 + b                           # the rune: a diamond glyph in cold fire
        for (dx, dy) in ((0, -3), (-1, -2), (1, -2), (-2, -1), (2, -1), (-2, 0), (2, 0), (-1, 1), (1, 1), (0, 2), (0, -1), (0, 0)):
            s.set(rx0 + dx, ry0 + dy, rune if (dx, dy) not in ((0, -1), (0, 0)) else "white")
    elif face == "up":
        for y in range(32 + b, 50 + b):
            s.set(25, y, iron_lo)
    else:
        rect(s, 18, 36 + b, 19, 46 + b, iron_lo); s.set(17, 41 + b, rune); s.set(17, 42 + b, rune)
    # pauldrons with spikes
    for (px, flip) in (((12, -1), (38, 1)) if not side else ((28, 1),)):
        ell(s, px, 31 + b, 6.5, 5, iron, shader(px, 6.5, iron_hi, iron, iron_lo))
        rect(s, px - 6, 34 + b, px + 6, 34 + b, iron_lo)
        for k in range(4):
            s.set(px + flip * (1 + k), 26 + b - k, iron_hi if k < 3 else bone_hi)
        s.set(px, 30 + b, rune)
    # head: bone skull under a horned helm
    hx = 22 if side else 25
    ell(s, hx, 19 + b, 6.5, 7, bone, shader(hx, 6.5, bone_hi, bone, bone_lo))
    ell(s, hx, 15 + b, 7.5, 4.5, iron, shader(hx, 7.5, iron_hi, iron, iron_lo))   # helm cap
    rect(s, hx - 7, 17 + b, hx + 7, 17 + b, iron_lo)
    for side_x, d in (((-1, 1) if not side else (1,))) and (((hx - 6, -1), (hx + 6, 1)) if not side else ((hx + 5, 1),)):
        for k in range(8):                              # horns: curving up and out
            x = side_x + d * (k // 2 + (1 if k > 4 else 0)); y = 14 + b - k
            s.set(x, y, iron_hi if k < 6 else bone_hi); s.set(x + d, y, iron_lo if k < 5 else None)
    if face == "down":
        rect(s, hx - 4, 19 + b, hx - 2, 21 + b, "ink"); rect(s, hx + 2, 19 + b, hx + 4, 21 + b, "ink")
        s.set(hx - 3, 20 + b, rune); s.set(hx + 3, 20 + b, rune); s.set(hx - 3, 19 + b, "white"); s.set(hx + 3, 19 + b, "white")
        s.set(hx, 22 + b, "ink"); rect(s, hx - 3, 25 + b, hx + 3, 25 + b, bone_lo)
        for x in range(hx - 3, hx + 4, 2):
            s.set(x, 24 + b, "ink")
    elif face == "left":
        rect(s, hx - 5, 19 + b, hx - 3, 21 + b, "ink"); s.set(hx - 4, 20 + b, rune); s.set(hx - 4, 19 + b, "white")
        rect(s, hx - 6, 24 + b, hx - 1, 24 + b, bone_lo)
    # arms + the greatsword
    def gaunt(x, y):
        rect(s, x - 2, y - 2, x + 2, y + 2, iron); s.set(x - 2, y - 2, iron_hi); rect(s, x - 2, y + 2, x + 2, y + 2, iron_lo)
    if sword == "rest":                                 # both hands on the pommel, the blade planted in front
        if face != "up":
            blade(25, 50 + b, 25, 77, 2); hilt(25, 47 + b)
        rect(s, 15, 34 + b, 18, 44 + b, iron); rect(s, 32, 34 + b, 35, 44 + b, iron_lo)
        gaunt(21, 46 + b); gaunt(29, 46 + b)
        if face == "up":
            blade(25, 46 + b, 25, 50 + b, 2)
    elif sword == "carry":
        if side:
            rect(s, 21, 36 + b, 25, 46 + b, iron_lo); gaunt(23, 48 + b)
            blade(22, 50 + b, 6, 70, 1); hilt(23, 48 + b)
        else:
            rect(s, 13, 34 + b, 16, 46 + b, iron); rect(s, 34, 34 + b, 37, 46 + b, iron_lo)
            gaunt(14, 48 + b); gaunt(36, 48 + b)
            blade(37, 52 + b, 46, 72, 1); s.set(36, 50 + b, rune)
    elif sword == "back":
        gaunt(36, 26 + b); rect(s, 33, 28 + b, 36, 36 + b, iron_lo)
        blade(38, 24 + b, 47, 4, 2); hilt(37, 27 + b)
    elif sword == "over":
        gaunt(25, 8 + b); rect(s, 22, 10 + b, 28, 14 + b, iron)
        blade(25, 6 + b, 25, 1, 2); blade(27, 6, 46, 2, 1)
    elif sword == "slash":
        gaunt(18, 46 + b); rect(s, 15, 36 + b, 19, 44 + b, iron)
        blade(16, 48 + b, 3, 76, 2); hilt(17, 47 + b)
        for (x, y) in ((8, 50), (5, 56), (3, 62), (12, 46), (6, 44)):   # the swing's cold-fire arc
            s.set(x, y, rune); s.set(x + 1, y, "white")
    else:
        gaunt(20, 50 + b); rect(s, 16, 40 + b, 20, 48 + b, iron)
        blade(18, 52 + b, 6, 74, 1)
    if slump:
        for y in range(H):
            for x in range(W):
                if s.p[y][x] and ((x * 73 + y * 151 + i * 37) % 13) < slump * 2 and y < 74:
                    s.p[y][x] = None


def sporemother(s, face, anim, i):
    """Sporemother (rare, ~2.2x; a giant spore elemental): a floating mound of living moss under a wide rose toadstool
    cap with cream spots, two smaller caps on its shoulders, big gold lamp eyes, hanging root tendrils and a ring of
    glowing spores; attack = it swells and the spores burst out; die = it thins to a heap of spent spores"""
    s = _Rnd(s)
    W, H = s.w, s.h
    b = [0, -1, -1, 0][i] if anim == "idle" else [0, -1, 0, 1][i] if anim == "walk" else [0, -2, -3, 0][i] if anim == "attack" else [0, 2, 5, 9][i]
    if anim == "die" and i == 3:
        ell(s, 25, 75, 15, 3.5, "moss", shader(25, 15, "grass", "moss", "leaf_deep"))
        ell(s, 20, 72, 8, 3, "flower_rose", shader(20, 8, "plaster_hi", "flower_rose", "roof_lo"))
        for (x, y) in ((14, 74), (22, 73), (30, 75), (36, 74), (26, 76), (18, 76), (33, 72)):
            s.set(x, y, "grass_hi" if x % 2 else "flower_gold")
        s.set(18, 71, "plaster_hi"); s.set(23, 71, "plaster_hi")
        return
    swell = 2 if anim == "attack" and i in (1, 2) else 0
    shrink = i if anim == "die" else 0
    cy, rx, ry = 45 + b, 16.5 + swell - shrink * 2.5, 14 + swell - shrink * 2
    # hanging root tendrils under the floating mound
    for k, x0 in enumerate((15, 20, 25, 30, 35)):
        y0 = int(cy + ry * 0.8)
        for d in range(0, 18 - abs(k - 2) * 3 - shrink * 4):
            x = x0 + round(math.sin((d + i * 2 + k) * 0.5) * 1.2)
            s.set(x, y0 + d, "leaf_deep" if d % 3 else "moss")
            if d % 5 == 4:
                s.set(x + 1, y0 + d, "grass_hi")
    ell(s, 25, cy, rx, ry, "grass", shader(25, rx, "grass_hi", "grass", "moss"))
    for k in range(26):                                 # fluffy dithered rim
        a = k / 26 * 6.283 + i * 0.3
        x, y = 25 + (rx + 0.8) * math.cos(a), cy + (ry + 0.8) * math.sin(a)
        if (k + i) % 2 == 0:
            s.set(int(round(x)), int(round(y)), "grass_hi" if math.sin(a) < 0 else "leaf_deep")
    for k in range(22):                                 # moss tufts on the body
        x = 25 + ((k * 37) % 29) - 14; y = cy + ((k * 13) % 21) - 10
        if ((x - 25) / max(rx, 1)) ** 2 + ((y - cy) / max(ry, 1)) ** 2 < 0.7:
            s.set(int(x), int(y), "moss" if k % 3 else "grass_hi")
    if shrink < 2:                                      # shoulder caps, then the great cap
        for (sx, sy, sr) in ((10, cy - 6, 4.5), (40, cy - 4, 3.8)):
            ell(s, sx, sy, sr, 2.2, "flower_rose", shader(sx, sr, "flower_rose", "flower_rose", "roof"))
            rect(s, int(sx) - 1, int(sy) + 2, int(sx), int(sy) + 3, "plaster_hi")
            s.set(int(sx) - 1, int(sy) - 1, "plaster_hi")
        ccy = cy - ry - 2
        ell(s, 25, ccy, 15 - shrink * 3, 6.5, "flower_rose", shader(25, 15, "flower_rose", "flower_rose", "roof"))
        for x in range(16, 23):
            s.set(x, int(ccy - 4), "plaster_hi" if x % 2 else "flower_rose")   # a soft top highlight
        rect(s, 12 + shrink * 3, int(ccy + 4), 38 - shrink * 3, int(ccy + 4), "roof_lo")    # the cap's underside
        for (dx, dy, r) in ((-8, -2, 1.6), (-2, -4, 2.0), (5, -2, 1.6), (10, 1, 1.2), (-11, 1, 1.0), (1, 1, 1.2)):   # cream spots
            ell(s, 25 + dx, ccy + dy, r, r * 0.8, "plaster_hi")
    eye = "lamp"
    if face == "down":
        for ex in (19, 31):
            ell(s, ex, cy - 2, 2.4, 2.6, eye)
            s.set(ex, int(cy - 3), "white"); s.set(ex - 1, int(cy - 3), "white")
            rect(s, ex - 2, int(cy + 1), ex + 2, int(cy + 1), "flower_gold")
        for x in range(22, 29):                          # a small soft smile of glowing spores
            if x % 2 == 0:
                s.set(x, int(cy + 5) + (1 if 23 < x < 27 else 0), "flower_gold")
    elif face == "left":
        ell(s, 13, cy - 2, 2.2, 2.6, eye); s.set(12, int(cy - 3), "white"); rect(s, 11, int(cy + 1), 15, int(cy + 1), "flower_gold")
    n, R = (16, 24.0) if anim == "attack" and i == 2 else (12, 21.0)
    for k in range(n):                                  # orbiting / bursting spores
        a = k / n * 6.283 + i * 0.6 + (0.25 if anim == "walk" else 0)
        x, y = 25 + R * math.cos(a), cy + R * 0.75 * math.sin(a)
        if 1 <= x < W - 2 and 1 <= y < H - 2:
            s.set(int(round(x)), int(round(y)), "flower_gold" if k % 2 else "grass_hi")
            if k % 3 == 0:
                s.set(int(round(x)) + 1, int(round(y)), "lamp")


DRAW = {"eldergolem": eldergolem, "elderwraith": elderwraith, "deathlord": deathlord, "sporemother": sporemother}
# [ALFHEIM] begin: Alfheim bosses (prismcolossus 50x80 ~2.5x, sylvaine 100x160 5x) live in boss_alfheim.py
import boss_alfheim as _alf  # noqa: E402
BOSS.update(_alf.BOSS); DRAW.update(_alf.draw_table(eldergolem))
# [ALFHEIM] end


def frame(pal, role, facing, anim, i):
    fw, fh = BOSS[role]["frame"]
    s = SP.HSprite(pal, fw, fh)
    DRAW[role](s, "left" if facing == "right" else facing, anim, i)
    for y in range(fh):                                 # 1 px margin so the outline always closes inside the frame
        for x in range(fw):
            if x in (0, fw - 1) or y in (0, fh - 1):
                s.p[y][x] = None
    s.outline("ink")
    return s.mirror() if facing == "right" else s


def build(biome="cozy-village", roles=("eldergolem",), out="public/art/sprite", project=None, name="boss"):
    """write <name>.png + <name>.json (same meta shape as the actor atlas) and return their paths"""
    pal = SP.Pal(SP.load_biome(biome, project))
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    fw, fh = BOSS[roles[0]]["frame"]
    assert all(BOSS[r]["frame"] == (fw, fh) for r in roles), "one frame size per boss sheet"
    cols = SP.COLS if hasattr(SP, "COLS") else 28
    cols = max(cols, max(SP.ANIMS[a]["start"] + SP.ANIMS[a]["count"] for r in roles for a in BOSS[r]["anims"]))
    from PIL import Image
    im = Image.new("RGBA", (fw * cols, fh * 4 * len(roles)), (0, 0, 0, 0))
    meta = {"tool": "hd2d boss_sheet", "biome": biome, "frame": [fw, fh], "pivot": [fw // 2, fh], "ground_row": fh - 1,
            "facings": list(SP.FACINGS), "anims": SP.ANIMS, "cols": cols, "image": f"{name}.png", "size": [im.width, im.height], "roles": {}}
    for ri, role in enumerate(roles):
        frames = []
        for fi, facing in enumerate(SP.FACINGS):
            for anim in BOSS[role]["anims"]:
                for i in range(4):
                    x, y = (SP.ANIMS[anim]["start"] + i) * fw, (ri * 4 + fi) * fh
                    im.paste(frame(pal, role, facing, anim, i).image(), (x, y))
                    frames.append({"name": f"{role}_{facing}_{anim}{i}", "facing": facing, "anim": anim, "i": i, "x": x, "y": y,
                                   "w": fw, "h": fh, "pivot": [x + fw // 2, y + fh]})
        meta["roles"][role] = {"row": ri * 4, "kind": "enemy", "enemy": True, "boss": True, "scale": BOSS[role]["scale"],
                               "desc": BOSS[role]["desc"], "anims": list(BOSS[role]["anims"]),
                               "size_bounds": [[12, fw - 2], [12, fh]], "caster": False, "frames": frames}
    assert im.height <= 4096 and im.width <= 4096, "boss sheet must fit a 4096 px texture"
    im.save(out / f"{name}.png")
    SP.write_json(out / f"{name}.json", meta)
    return {"image": str(out / f"{name}.png"), "json": str(out / f"{name}.json"), "size": [im.width, im.height]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--biome", default="cozy-village"); ap.add_argument("--roles", default="eldergolem")
    ap.add_argument("--out", default="public/art/sprite"); ap.add_argument("--project", default=None)
    ap.add_argument("--name", default="boss"); ap.add_argument("--preview", default=None, help="write a 3x nearest preview PNG here")
    a = ap.parse_args(argv)
    r = build(a.biome, tuple(a.roles.split(",")), a.out, a.project, a.name)
    if a.preview:
        from PIL import Image
        im = Image.open(r["image"]); big = im.resize((im.width * 3, im.height * 3), Image.NEAREST)
        bg = Image.new("RGBA", big.size, (236, 222, 190, 255)); bg.alpha_composite(big); bg.save(a.preview)
    print(r)


if __name__ == "__main__":
    main()
