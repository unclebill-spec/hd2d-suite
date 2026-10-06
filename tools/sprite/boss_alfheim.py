"""Alfheim bosses for hd2d boss_sheet (original, Hearthmoor realm-alfheim branch). Imported by boss_sheet.py.

Style lock BOSS SCALE OVERRIDE: drawn NATIVELY at their size (never an upscaled small sprite), biome palette, hard
alpha, 1 px ink outline added by boss_sheet.frame. Their violet is their light + ground aura (game/alfheim.js).

  lenswarden     The Lens Warden (P4 mini-boss, 2.8x, 56x90): crystal golem of black stone + glass, a great chest-lens
  frostsentinel  Frost sentinel (Bifrost, 2x, 40x64): the same golem in ice, cold-fire seams
  shardmother    Shardmother (rare, 2.4x, 52x84 frame): floating shards round a core, a glass skirt
  glassstalker   Glass Stalker (rare, 2.6x, 52x84 frame): tall thin mirror-creature with glass blades
  sylvaine       Lady Sylvaine (boss, 6x, 128x192): the Art seat's drawing (boss_sylvaine6.py), real art
"""
from __future__ import annotations

import math

from roles_enemies import ell, rect

BOSS = {
    # script section 8.4 (alfheim.md): natively drawn at their size; one sheet per frame size (assemble [ALFHEIM] hook)
    "lenswarden": {"frame": (56, 90), "scale": 2.8, "anims": ("idle", "walk", "attack", "die"),
                   "desc": "The Lens Warden (mini-boss, 2.8x): crystal golem of violet glass and black stone, a great round chest-lens, frost-cracks across one shoulder"},
    "shardmother": {"frame": (52, 84), "scale": 2.4, "anims": ("idle", "walk", "attack", "die"),
                    "desc": "Shardmother (rare, 2.4x): a crystal queen-shape of floating shards around a glowing core, a skirt of hanging glass"},
    "glassstalker": {"frame": (52, 84), "scale": 2.6, "anims": ("idle", "walk", "attack", "die"),
                     "desc": "Glass Stalker (rare, 2.6x): a tall, thin mirror-creature, a moving silhouette of reflections with bright eyes"},
    "frostsentinel": {"frame": (40, 64), "scale": 2.0, "anims": ("idle", "walk", "attack", "die"),
                      "desc": "Frost sentinel (2x): an ice golem knight-shape of Veyra's frost, cold-fire in its seams"},
    "sylvaine": {"frame": (128, 192), "scale": 6.0, "anims": ("idle", "walk", "attack", "die"),
                 "desc": "Lady Sylvaine, elf vampire queen (boss, 6x; Art seat drawing): silver hair, crystal tiara, deep-blue blouse + lace jabot, dark belt with gold clasp, long dark bell skirt with rose panel, red-lined cape"},
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


def _golem(s, face, anim, i, pal, lens=False, frost=False):
    """a parametric crystal / ice golem drawn natively for any frame (lenswarden 56x90, frostsentinel 40x64):
    blocky stone legs + belt band (the waist), a broad glass chest, shoulder crystals, small head; attack = both fists
    up then a slam; die = it cracks and collapses into shards"""
    F = _F(s)
    W, H = s.w, s.h
    k = H / 90.0
    cx = W / 2 - (2 if face == "left" else 0)
    side, back = face == "left", face == "up"
    b = 0; lift = 0; slam = 0
    if anim == "idle":
        b = [0, 0, 1, 1][i]
    elif anim == "walk":
        b = [0, 1, 0, 1][i]
    elif anim == "attack":
        lift = [0, 1, 0, 0][i]; slam = [0, 0, 1, 0][i]; b = [0, -1, 2, 1][i]
    elif anim == "die":
        b = [1, 4, 0, 0][i]
    G = H - 2
    body, body_lo, body_hi, glass, glass_hi, glass_lo, crack = pal
    if anim == "die" and i >= 2:                      # a heap of stone blocks and glass shards
        for (dx, dy, rx, ry, c) in ((-10, -5, 9, 5, body_lo), (6, -6, 8, 6, body), (-2, -11, 7, 5, body_hi), (12, -3, 5, 3, body_lo)):
            ell(F, cx + dx * k, G + dy * k, rx * k, ry * k, c)
        for kk in range(7):
            x = cx + (kk - 3) * 6 * k; y = G - (3 + (kk * 5) % 9) * k
            for d in range(int(5 * k)):
                F.set(x + (d % 2), y - d, glass_hi if d < 2 else glass)
        if lens:
            ell(F, cx + 3 * k, G - 14 * k, 5 * k, 4 * k, glass_lo); ell(F, cx + 3 * k, G - 14 * k, 3 * k, 2.4 * k, glass_hi)
        return
    hip = G - 30 * k + b
    # legs (separate, stone blocks)
    stride = [0, 3, 0, -3][i] * k if anim == "walk" else 0
    for sd in ((-1, 1) if not side else (0,)):
        lx = cx + sd * 9 * k + (stride * sd if not side else 0)
        rect(F, int(lx - 6 * k), int(hip), int(lx + 6 * k), int(G - 4 * k), body)
        rect(F, int(lx - 6 * k), int(hip), int(lx - 4 * k), int(G - 4 * k), body_hi)
        rect(F, int(lx - 7 * k), int(G - 5 * k), int(lx + 7 * k), int(G), body_lo)   # foot block
    if side:
        rect(F, int(cx - 7 * k + stride), int(G - 5 * k), int(cx + 7 * k + stride), int(G), body_lo)
    # belt band = the waist (stone girdle with glass studs)
    rect(F, int(cx - 17 * k), int(hip - 5 * k), int(cx + 17 * k), int(hip), body_lo)
    for x in range(int(cx - 15 * k), int(cx + 16 * k), max(2, int(6 * k))):
        F.set(x, hip - 2.5 * k, glass_hi); F.set(x + 1, hip - 2.5 * k, glass)
    # chest: broad trapezoid of glass in a stone frame
    top = hip - 34 * k
    _poly(F, [(cx - 22 * k, top), (cx + 22 * k, top), (cx + 15 * k, hip - 5 * k), (cx - 15 * k, hip - 5 * k)],
          lambda x, y: body if back else (glass_lo if (x + y) % 7 == 0 else glass) if abs(x - cx) < 13 * k else body if x > cx else body_hi)
    if not back:   # facets
        for d in range(int(20 * k)):
            F.set(cx - 9 * k + d * 0.3, top + 3 * k + d, glass_hi)
    # arms: stone columns, fists raised in the attack wind-up
    for sd in ((-1, 1) if not side else (-1,)):
        ax = cx + sd * 25 * k
        if lift:
            rect(F, int(ax - 5 * k), int(top - 20 * k), int(ax + 5 * k), int(top + 4 * k), body)
            ell(F, ax, top - 22 * k, 7 * k, 6 * k, body_hi)
        else:
            y1 = hip + (8 if slam else 2) * k
            rect(F, int(ax - 5 * k), int(top + 2 * k), int(ax + 5 * k), int(y1), body)
            rect(F, int(ax - 5 * k), int(top + 2 * k), int(ax - 3 * k), int(y1), body_hi)
            ell(F, ax, y1 + 3 * k, 7 * k, 6 * k, body_hi if not slam else glass_hi)
    # shoulder crystals (frost-cracked on the right shoulder)
    for sd, h in ((-1, 14), (1, 11)):
        x0 = cx + sd * 20 * k
        for d in range(int(h * k)):
            w = max(0, int(3 * k * (1 - d / (h * k))))
            for e in range(-w, w + 1):
                F.set(x0 + e + sd * d * 0.25, top - d, glass_hi if e < 0 else glass if e == 0 else glass_lo)
    for d in range(int(12 * k)):                       # frost crack across one shoulder
        F.set(cx + 12 * k + d * 0.6, top + 1 * k + (d % 3), crack)
    # head: a small block with a crystal brow
    hy = top - 9 * k
    rect(F, int(cx - 7 * k), int(hy), int(cx + 7 * k), int(top + 1), body)
    if not back:
        eye = "white" if anim == "attack" else glass_hi
        F.set(cx - 3 * k, hy + 4 * k, eye); F.set(cx + 3 * k - (2 * k if side else 0), hy + 4 * k, eye)
        F.set(cx - 3 * k + 1, hy + 4 * k, eye); F.set(cx + 3 * k + 1 - (2 * k if side else 0), hy + 4 * k, eye)
    for d in range(int(6 * k)):
        F.set(cx - 2 * k + d * 0.7, hy - d * 0.6, glass_hi); F.set(cx + 2 * k - d * 0.2, hy - d, glass)
    if lens and not back:                              # the great chest lens
        ly = top + 15 * k
        r = 9 * k if not side else 6 * k
        ell(F, cx - (3 * k if side else 0), ly, r + 1.5 * k, r + 1.5 * k, body_lo)
        ell(F, cx - (3 * k if side else 0), ly, r, r, glass_lo)
        ell(F, cx - (3 * k if side else 0), ly, r * 0.7, r * 0.7, "white" if anim == "attack" and i == 2 else glass)
        ell(F, cx - (3 * k if side else 0) - r * 0.3, ly - r * 0.3, r * 0.28, r * 0.28, "white")
    if frost:                                          # cold-fire in the seams
        for x in range(int(cx - 14 * k), int(cx + 14 * k), 3):
            F.set(x, hip - 5 * k - 1, "white")
        for sd in (-1, 1):
            F.set(cx + sd * 9 * k, hip + 6 * k, "white"); F.set(cx + sd * 9 * k, hip + 12 * k, "sky")


LENS_PAL = ("stone_lo", "shadow", "stone", "flower_blue", "sky", "cloth", "white")      # black stone + violet-lit glass
FROST_PAL = ("sky", "flower_blue", "white", "sky", "white", "flower_blue", "cloth")     # ice


def lenswarden(s, face, anim, i):
    _golem(s, face, anim, i, LENS_PAL, lens=True)


def frostsentinel(s, face, anim, i):
    _golem(s, face, anim, i, FROST_PAL, frost=True)


def shardmother(s, face, anim, i):
    """a floating queen-shape of shards around a glowing core (~78 px of the 84 px frame), a skirt of hanging glass;
    attack = the shards flare outward (a volley); die = the shards fall and the core gutters"""
    F = _F(s)
    W, H = s.w, s.h
    cx = W / 2 - (2 if face == "left" else 0)
    bob = [0, -1, -2, -1][i] if anim in ("idle", "walk") else [0, -2, 1, 0][i] if anim == "attack" else [2, 6, 0, 0][i]
    spread = [0, 2, 5, 2][i] if anim == "attack" else 0
    G = H - 2
    if anim == "die" and i >= 2:
        for kk in range(11):
            x = cx - 20 + (kk * 37) % 41; y = G - (kk % 3)
            F.set(x, y, "white"); F.set(x + 1, y, "sky"); F.set(x, y - 1, "flower_blue")
        ell(F, cx, G - 3, 4, 2, "flower_rose" if i == 2 else "shadow")
        return
    core_y = G - 46 + bob
    # skirt of hanging glass (bottom) under a stone-dark girdle (waist)
    for kk in range(9):
        x = cx - 16 + kk * 4
        L = 20 + (kk * 7) % 9 - abs(kk - 4)
        for d in range(L):
            w = 1 if d < L * 0.6 else 0
            for e in range(-w, w + 1):
                F.set(x + e + (spread * (kk - 4) / 4 if d > 4 else 0), core_y + 12 + d, "white" if e < 0 else "sky" if e == 0 else "flower_blue")
    rect(F, int(cx - 13), int(core_y + 9), int(cx + 13), int(core_y + 12), "shadow")
    for x in range(int(cx - 11), int(cx + 12), 4):
        F.set(x, core_y + 10, "flower_rose")
    # bodice of fitted shards (top)
    _poly(F, [(cx - 11, core_y - 14), (cx + 11, core_y - 14), (cx + 9, core_y + 9), (cx - 9, core_y + 9)],
          lambda x, y: "cloth" if (x + 2 * y) % 5 else "flower_blue")
    ell(F, cx, core_y, 5.5, 6, "flower_rose"); ell(F, cx, core_y, 3, 3.4, "white")            # the core
    # head + shard crown
    hy = core_y - 22
    ell(F, cx, hy, 6, 7, "stone_hi"); ell(F, cx - 1, hy - 1, 4, 5, "white")
    if face != "up":
        F.set(cx - 2 - (2 if face == "left" else 0), hy + 1, "cloth"); F.set(cx + 2 - (2 if face == "left" else 0), hy + 1, "cloth")
    for kk, (dx, h) in enumerate(((-6, 7), (-3, 10), (0, 13), (3, 10), (6, 7))):
        for d in range(h):
            F.set(cx + dx, hy - 6 - d, "white" if d > h - 3 else "sky" if kk % 2 else "flower_blue")
    # orbiting shards (arms of the shape)
    n = 8
    for kk in range(n):
        a = kk / n * math.tau + i * 0.5
        R = 19 + spread * 2
        x, y = cx + R * math.cos(a), core_y - 4 + R * 0.55 * math.sin(a)
        for d in range(5):
            F.set(x, y - d, "white" if d < 2 else "sky"); F.set(x + 1, y - d + 1, "flower_blue")


def glassstalker(s, face, anim, i):
    """a tall, thin mirror-creature (~80 px): long jointed legs, a narrow mirror torso with a cinched girdle, long arms
    ending in glass blades, a shard head with two bright eyes; walk = a stalking lope, attack = a blade lunge"""
    F = _F(s)
    W, H = s.w, s.h
    cx = W / 2 - (2 if face == "left" else 0)
    side = face == "left"
    G = H - 2
    b = [0, 1, 0, 1][i] if anim in ("idle", "walk") else [0, 2, -1, 0][i] if anim == "attack" else [2, 10, 0, 0][i]
    if anim == "die" and i >= 2:
        for kk in range(14):
            x = cx - 22 + (kk * 29) % 45; y = G - (kk % 4)
            F.set(x, y, "white" if kk % 2 else "sky"); F.set(x + 1, y, "flower_blue")
        if i == 2:
            F.set(cx - 2, G - 6, "flower_rose"); F.set(cx + 2, G - 6, "flower_rose")
        return
    hip = G - 38 + b
    st = [0, 4, 0, -4][i] if anim == "walk" else 0
    mirror = lambda x, y: "white" if (x - y) % 9 == 0 else "sky" if (x + y) % 4 else "flower_blue"
    for sd in ((-1, 1) if not side else (-1, 1)):
        kx = cx + sd * 6 + (st * sd)
        _poly(F, [(cx + sd * 3 - 2, hip), (cx + sd * 3 + 2, hip), (kx + 2, hip + 18), (kx - 2, hip + 18)], mirror)   # thigh
        _poly(F, [(kx - 2, hip + 18), (kx + 2, hip + 18), (kx + sd * 2 + 1, G), (kx + sd * 2 - 2, G)], mirror)      # shin
        F.set(kx, hip + 18, "white")
    rect(F, int(cx - 7), int(hip - 3), int(cx + 7), int(hip), "shadow")                 # girdle (the waist)
    F.set(cx, hip - 2, "flower_rose")
    top = hip - 26
    _poly(F, [(cx - 9, top), (cx + 9, top), (cx + 6, hip - 3), (cx - 6, hip - 3)], mirror)   # narrow mirror torso (top)
    for d in range(20):
        F.set(cx - 4 + d * 0.2, top + 3 + d, "white")
    lunge = anim == "attack" and i == 2
    for sd in ((-1, 1) if not side else (-1,)):
        ex = cx + sd * (24 if lunge else 13)
        ey = top + (6 if lunge else 22)
        _poly(F, [(cx + sd * 8, top + 1), (cx + sd * 10, top + 3), (ex + 1, ey), (ex - 1, ey)], mirror)
        for d in range(12):                                                               # glass blade
            F.set(ex + sd * (d * (0.9 if lunge else 0.15)), ey + (0 if lunge else d) + (d * 0.1 if lunge else 0), "white" if d % 3 else "sky")
    hy = top - 8
    _poly(F, [(cx - 5, hy + 7), (cx + 5, hy + 7), (cx + 3, hy - 7), (cx, hy - 12), (cx - 3, hy - 7)], mirror)
    if face != "up":
        o = -2 if side else 0
        for ex in ((cx - 2 + o, cx + 2 + o) if not side else (cx - 2,)):
            F.set(ex, hy, "flower_rose"); F.set(ex, hy + 1, "white")


def draw_table(eldergolem):
    import boss_sylvaine6 as _syl   # the Art seat's real Sylvaine, at 6x
    return {"lenswarden": lenswarden, "shardmother": shardmother, "glassstalker": glassstalker,
            "frostsentinel": frostsentinel, "sylvaine": _syl.sylvaine}
