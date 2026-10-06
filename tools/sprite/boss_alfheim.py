"""Alfheim bosses for hd2d boss_sheet (original, Hearthmoor realm-alfheim branch). Imported by boss_sheet.py.

Style lock BOSS SCALE OVERRIDE: drawn NATIVELY at their size (never an upscaled small sprite), biome palette, hard
alpha, 1 px ink outline added by boss_sheet.frame. Their violet is their light + ground aura (game/alfheim.js).

  prismcolossus  The Prism Colossus (Lumenvale mini-boss, ~2.5x, 50x80): Mossheart's block-golem body re-cut in pale
                 crystal with rose-crystal veins, a crown of prism spires and a white-hot heart
  sylvaine       Lady Sylvaine, the elf vampire queen (Prism Vault boss, 5x, 100x160): silver hair to the knee, a
                 crown of jagged crystal, pale skin and red eyes; clothing rule: a fitted dark bodice with a high rose
                 collar (top), a broad gold waist cinch with a rose jewel (waist), a long deep-blue skirt with a pale
                 hem (bottom), a red-lined cape behind; a crystal scepter that drains magic
"""
from __future__ import annotations

import math

from roles_enemies import ell, rect

BOSS = {
    "prismcolossus": {"frame": (50, 80), "scale": 2.5, "anims": ("idle", "walk", "attack", "die"),
                      "desc": "The Prism Colossus (mini-boss, ~2.5x): pale crystal block-golem, rose-crystal veins, prism-spire crown, white-hot heart"},
    "sylvaine": {"frame": (100, 160), "scale": 5.0, "anims": ("idle", "walk", "attack", "die"),
                 "desc": "Lady Sylvaine, elf vampire queen (boss, 5x): silver hair, crystal crown, red eyes, dark bodice + rose collar, gold waist cinch, long deep-blue skirt, red-lined cape, crystal scepter"},
}

CRYSTAL = {"stone": "sky", "stone_lo": "flower_blue", "shadow": "cloth", "stone_hi": "white", "lamp": "flower_rose",
           "flower_gold": "flower_rose", "moss": "plaster_hi", "grass_hi": "white", "grass": "sky"}


class _Remap:
    def __init__(self, s, m):
        self.s, self.m, self.p, self.w, self.h = s, m, s.p, s.w, s.h

    def set(self, x, y, c):
        self.s.set(x, y, self.m.get(c, c) if c else c)


class _F:
    """float-coordinate pixel placement (rounded once), clipped to the frame"""
    def __init__(self, s):
        self.s, self.p, self.w, self.h = s, s.p, s.w, s.h

    def set(self, x, y, c):
        if c is None:
            return
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.w and 0 <= y < self.h:
            self.s.set(x, y, c)


def make_colossus(eldergolem):
    def prismcolossus(s, face, anim, i):
        eldergolem(_Remap(s, CRYSTAL), face, anim, i)
        if anim == "die" and i >= 2:
            for (x, y) in ((12, 70), (25, 66), (36, 71), (20, 74)):
                s.set(x, y, "white"); s.set(x + 1, y, "flower_rose")
            return
        b = [0, 0, 1, 1][i] if anim == "idle" else [0, 1, 0, 1][i] if anim == "walk" else [0, -2, 2, 1][i] if anim == "attack" else [1, 4, 0, 0][i]
        side = face == "left"
        F = _F(s)
        spires = ((14, 16, 9), (20, 12, 12), (27, 11, 14), (33, 13, 11), (38, 17, 8)) if not side else ((18, 13, 12), (24, 11, 14), (30, 14, 10))
        for k, (x, y, h) in enumerate(spires):   # a crown of prism spires: tapered crystals, lit left, white tips
            for d in range(h):
                w = max(0, int(2.2 * (1 - d / h)))
                for e in range(-w, w + 1):
                    F.set(x + e, y + b - d, "white" if e < 0 else "sky" if e == 0 else "flower_blue")
            F.set(x, y + b - h, "white"); F.set(x, y + b - h + 2, "flower_rose" if k % 2 else "white")
        if face == "down":   # the white-hot heart
            ell(F, 25, 40 + b, 3.2, 3.6, "flower_rose"); ell(F, 25, 40 + b, 1.8, 2.0, "white")
    return prismcolossus


def _poly(F, pts, colfn):
    """scanline fill of a polygon; colfn(x, y) -> colour"""
    ys = [p[1] for p in pts]
    for y in range(int(min(ys)), int(max(ys)) + 1):
        xs = []
        n = len(pts)
        for k in range(n):
            (x0, y0), (x1, y1) = pts[k], pts[(k + 1) % n]
            if (y0 <= y + 0.5 < y1) or (y1 <= y + 0.5 < y0):
                xs.append(x0 + (y + 0.5 - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for a, c in zip(xs[::2], xs[1::2]):
            for x in range(int(round(a)), int(round(c))):
                col = colfn(x, y)
                if col:
                    F.set(x, y, col)


def sylvaine(s, face, anim, i):
    F = _F(s)
    W, H = s.w, s.h            # 100 x 160; hem on the ground row (158 + outline 159)
    side, back = face == "left", face == "up"
    b = 0; sway = 0; arms = "rest"; flare = 0; sink = 0; glow = False
    if anim == "idle":
        b = [0, 1, 2, 1][i]; sway = [0, 1, 0, -1][i]
    elif anim == "walk":
        b = [0, 2, 0, 2][i]; sway = [2, 0, -2, 0][i]
    elif anim == "attack":
        arms = ["raise", "high", "drain", "drain"][i]; b = [0, -2, 1, 0][i]; flare = [0, 2, 4, 2][i]; glow = i in (1, 2)
    elif anim == "die":
        sink = [4, 18, 0, 0][i]; b = sink
    cx = 48 if side else 50
    wy = 92 + b
    # ------------------------------------------------ the heap (die 2-3): skirt pooled on the floor, crown and shards
    if anim == "die" and i >= 2:
        ell(F, 50, 150, 34, 8, "cloth"); ell(F, 50, 148, 26, 5, "shadow"); ell(F, 46, 146, 14, 3, "roof_lo")
        ell(F, 58, 141, 9, 6, "white"); ell(F, 58, 141, 6, 4, "stone_hi")    # silver hair spilled over the cloth
        for k, x in enumerate((30, 38, 44, 62, 70)):
            F.set(x, 152 - k % 2, "white"); F.set(x + 1, 152 - k % 2, "sky"); F.set(x, 151 - k % 2, "flower_rose")
        for k in range(5):   # the crown, toppled
            F.set(70 + k * 2, 144, "flower_gold"); F.set(70 + k * 2, 143 - (k % 2) * 2, "white" if k % 2 else "sky")
        if i == 2:
            for (x, y) in ((40, 138), (55, 134), (64, 137)):
                F.set(x, y, "flower_rose"); F.set(x, y - 1, "white")
        return
    # ------------------------------------------------ cape (behind everything; red lining shows at the sides)
    top_c = 46 + b
    hemw = 40 + flare
    _poly(F, [(cx - 22, top_c), (cx + 22, top_c), (cx + hemw, 159), (cx - hemw, 159)],
          lambda x, y: ("roof_lo" if abs(x - cx) > 18 + (y - top_c) * 0.36 else "shadow") if not back else ("shadow" if (x + y // 6) % 9 else "ink"))
    for y in range(int(top_c + 4), 159):
        t = (y - top_c) / (159 - top_c)
        for sgn in (-1, 1):
            x = cx + sgn * (22 + (hemw - 22) * t)
            F.set(x - sgn, y, "roof"); F.set(x - 2 * sgn, y, "roof_lo")
    if back:
        _poly(F, [(cx - 20, top_c + 2), (cx + 20, top_c + 2), (cx + hemw - 4, 157), (cx - hemw + 4, 157)],
              lambda x, y: "roof" if abs(x - cx) < 4 + (y - top_c) * 0.05 else "roof_lo" if (x // 5 + y // 9) % 3 == 0 else "shadow")
    # high collar wings of the cape (a vampire's standing collar), rose lining
    for sgn in ((-1, 1) if not side else (1,)):
        _poly(F, [(cx + sgn * 10, 50 + b), (cx + sgn * 26, 30 + b), (cx + sgn * 24, 52 + b)],
              lambda x, y: "flower_rose" if not back and abs(x - cx) < 20 else "roof_lo")
    # long silver locks falling behind the shoulders to the hip (drawn before the body, so it covers their inner part)
    hy = 22 + b
    hw = 12 if not side else 11
    for sgn in ((-1, 1) if not side else (1,)):
        for y in range(int(hy + 6), int(wy + 10)):
            t = (y - hy) / (wy + 10 - hy)
            x0 = cx + sgn * (hw - 3 + t * 9) + sway * t
            for e in range(7 if not side else 10):
                F.set(x0 + sgn * e, y, "white" if e < 2 else "stone_hi" if e < 5 else "stone")
        F.set(cx + sgn * (hw + 6), wy + 10, "stone_hi")
    # ------------------------------------------------ skirt (bottom): long, deep blue, pale hem trim, a dark side panel
    hem = 159   # the hem sits on the ground row (outline lands on row 159)
    skw = 26 + flare // 2
    _poly(F, [(cx - 13, wy), (cx + 13, wy), (cx + skw + sway, hem), (cx - skw + sway, hem)],
          lambda x, y: ("flower_blue" if x < cx - 10 - (y - wy) * 0.15 + sway * (y - wy) / 60 else "shadow" if x > cx + 6 + (y - wy) * 0.2 else "cloth")
          if not back else ("cloth" if (x // 4) % 3 else "shadow"))
    for x in range(int(cx - skw + sway) + 1, int(cx + skw + sway)):   # pale hem trim + a row of rose stitches
        F.set(x, hem - 1, "stone_hi"); F.set(x, hem - 2, "plaster_lo" if x % 2 else "stone_hi")
        if x % 5 == 0:
            F.set(x, hem - 4, "flower_rose")
    if not back:   # the skirt's front slit seam (silver)
        for y in range(wy + 4, hem - 3, 2):
            F.set(cx + 2 + sway * (y - wy) / 63, y, "stone")
    # ------------------------------------------------ bodice (top): fitted dark bodice, rose lacing, puffed shoulders
    sy0 = 50 + b
    bw0, bw1 = (16, 12) if not side else (11, 9)
    _poly(F, [(cx - bw0, sy0), (cx + bw0, sy0), (cx + bw1, wy - 6), (cx - bw1, wy - 6)],
          lambda x, y: "shadow" if x < cx - bw0 * 0.45 else "ink" if x > cx + bw0 * 0.5 else "cloth" if back else "shadow")
    if not back and not side:
        for y in range(sy0 + 6, wy - 7, 3):          # rose lacing down the front
            F.set(cx - 2, y, "flower_rose"); F.set(cx + 1, y, "flower_rose"); F.set(cx - 1, y + 1, "roof"); F.set(cx, y + 1, "roof")
        ell(F, cx, sy0 + 3, 6, 3, "plaster_hi")      # the pale neckline
        F.set(cx, sy0 + 6, "flower_rose"); F.set(cx, sy0 + 7, "roof_hi")   # a rose pendant
    for sgn in ((-1, 1) if not side else (-1,)):     # puffed shoulders
        ell(F, cx + sgn * (bw0 + 1), sy0 + 4, 6, 5, "shadow" if sgn < 0 else "ink")
        ell(F, cx + sgn * (bw0 + 1) - 1, sy0 + 2, 3, 2, "cloth")
    # ------------------------------------------------ the waist: a broad gold cinch with a rose jewel
    rect(F, int(cx - bw1 - 1), wy - 6, int(cx + bw1 + 1), wy - 1, "flower_gold")
    rect(F, int(cx - bw1 - 1), wy - 1, int(cx + bw1 + 1), wy, "timber_hi")
    if not back:
        ell(F, cx, wy - 3, 2.6, 2.4, "flower_rose"); F.set(cx - 1, wy - 4, "white")
    # ------------------------------------------------ arms + the crystal scepter
    def arm(x0, y0, x1, y1, w=3.2, col="shadow"):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for k in range(n):
            t = k / max(1, n - 1)
            ell(F, x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, w, w, col)
        ell(F, x1, y1 + 1, 2.4, 2.6, "plaster_hi")   # pale hand
        F.set(x1 - 1, y1 + 4, "stone"); F.set(x1 + 1, y1 + 4, "stone")   # claw tips
    def scepter(x, y, up=True, hot=False):
        L = 34
        for k in range(L):
            yy = y - k if up else y + k
            F.set(x, yy, "stone_hi" if k % 4 else "flower_gold"); F.set(x + 1, yy, "stone")
        ty = y - L if up else y + L
        for d in range(9):   # the crystal head: a long faceted diamond
            w = int(4 * (1 - abs(d - 4) / 4.5))
            for e in range(-w, w + 1):
                F.set(x + e, ty - d + 4, "white" if e < 0 else "sky" if e == 0 else "flower_blue")
        F.set(x, ty, "white" if hot else "flower_rose")
        if hot:
            for k in range(8):
                a = k / 8 * math.tau + i
                F.set(x + math.cos(a) * 7, ty + math.sin(a) * 6, "white" if k % 2 else "flower_rose")
    shL, shR = (cx - bw0 - 1, sy0 + 6), (cx + bw0 + 1, sy0 + 6)
    if side:
        if arms == "rest":
            arm(cx - 4, sy0 + 6, cx - 9, wy + 2); scepter(cx - 9, wy + 30)
        else:
            reach = {"raise": (cx - 16, sy0 - 2), "high": (cx - 14, sy0 - 14), "drain": (cx - 26, sy0 + 6)}[arms]
            arm(cx - 4, sy0 + 6, reach[0], reach[1]); scepter(reach[0], reach[1] + 2, True, glow)
    elif back:
        arm(*shL, cx - 22, wy - 2, col="ink"); arm(*shR, cx + 22, wy - 2, col="ink")
        if arms != "rest":
            scepter(cx + 24, sy0 - 4, True, glow)
    else:
        if arms == "rest":
            arm(*shL, cx - 23, wy); arm(*shR, cx + 23, wy, col="ink"); scepter(cx + 23, wy + 32)
        else:
            if arms == "raise":
                tl, tr = (cx - 26, sy0 - 4), (cx + 26, sy0 - 6)
            elif arms == "high":
                tl, tr = (cx - 22, sy0 - 18), (cx + 24, sy0 - 20)
            else:
                tl, tr = (cx - 32, sy0 + 2), (cx + 32, sy0)
            arm(*shL, *tl); arm(*shR, *tr, col="ink"); scepter(tr[0], tr[1] + 2, True, glow)
            if arms == "drain":   # stolen magic drawn into the open left hand
                for k in range(6):
                    F.set(tl[0] - 6 + k, tl[1] + 2 + (k % 2), "sky" if k % 2 else "white")
    # ------------------------------------------------ head: pale face, red eyes, silver hair, crystal crown
    hy = 22 + b
    hw = 12 if not side else 11
    ell(F, cx, hy + 13, hw, 15, "plaster_hi")
    if not back:
        for y in range(int(hy + 6), int(hy + 28)):   # a soft shade down the right of the face
            F.set(cx + hw - 2 - (1 if y > hy + 20 else 0), y, "stone_hi")
    # hair: a cap of silver over the brow, long locks falling past the waist behind the shoulders
    for y in range(int(hy - 3), int(hy + 9)):
        for x in range(int(cx - hw - 2), int(cx + hw + 3)):
            if ((x - cx) / (hw + 2)) ** 2 + ((y - hy - 8) / 12) ** 2 <= 1:
                if side and y > hy + 4 and x < cx - 1:
                    continue   # profile: the face shows, the hair sweeps back
                F.set(x, y, "white" if x < cx + 2 else "stone_hi")
    if back:
        for y in range(int(hy), int(wy + 30)):
            for x in range(int(cx - hw * 1.3), int(cx + hw * 1.3 + 1)):
                t = (y - hy) / (wy + 30 - hy)
                if abs(x - cx) <= hw * (0.9 + t * 0.35):
                    F.set(x + sway * t, y, "stone" if (x * 7 + y // 5) % 11 == 0 else "white" if x < cx - 2 else "stone_hi")
    else:
        if side:
            ex, ey = cx - hw + 4, hy + 15
            F.set(ex, ey, "roof_hi"); F.set(ex + 1, ey, "roof_hi"); F.set(ex, ey + 1, "roof")
            F.set(cx - hw - 1, hy + 18, "plaster_hi")      # nose
            F.set(cx - hw + 2, hy + 23, "roof")             # dark lips
            F.set(cx + 2, hy + 13, "plaster_hi"); F.set(cx + 4, hy + 10, "plaster_hi"); F.set(cx + 6, hy + 7, "stone_hi")   # pointed ear
        else:
            for ex in (cx - 5, cx + 4):   # red eyes, 2 px tall, a glint
                F.set(ex, hy + 15, "roof_hi"); F.set(ex + 1, hy + 15, "roof_hi"); F.set(ex, hy + 16, "roof"); F.set(ex + 1, hy + 16, "roof")
                F.set(ex, hy + 14, "ink"); F.set(ex + 1, hy + 14, "ink")
            F.set(cx, hy + 22, "roof"); F.set(cx + 1, hy + 22, "roof"); F.set(cx - 1, hy + 21, "roof_lo")   # dark lips
            F.set(cx - 7, hy + 19, "flower_rose"); F.set(cx + 7, hy + 19, "flower_rose")
            for sgn in (-1, 1):   # pointed ears out of the hair
                F.set(cx + sgn * (hw + 1), hy + 14, "plaster_hi"); F.set(cx + sgn * (hw + 3), hy + 12, "plaster_hi"); F.set(cx + sgn * (hw + 4), hy + 10, "stone_hi")
    # the crown: a gold band and jagged crystal spikes, tallest in the middle
    crown_y = hy - 1
    rect(F, int(cx - hw + 1), int(crown_y), int(cx + hw - 1), int(crown_y + 1), "flower_gold")
    n = 7 if not side else 5
    for k in range(n):
        x = cx - hw + 2 + k * (2 * hw - 4) / (n - 1)
        h = 6 + (8 if k == n // 2 else 4 if abs(k - n // 2) == 1 else 0)
        for d in range(h):
            w = 1 if d < h * 0.5 else 0
            for e in range(-w, w + 1):
                F.set(x + e, crown_y - d, "white" if e < 0 else "sky" if e == 0 else "flower_blue")
        F.set(x, crown_y - h, "white" if (k + i) % 2 else "flower_rose")
    if glow:   # the drain: rose sparks around the crown
        for k in range(6):
            a = k / 6 * math.tau + i * 0.5
            F.set(cx + math.cos(a) * 18, crown_y - 6 + math.sin(a) * 6, "flower_rose" if k % 2 else "white")


def draw_table(eldergolem):
    return {"prismcolossus": make_colossus(eldergolem), "sylvaine": sylvaine}
