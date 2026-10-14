#!/usr/bin/env python3
"""Lumi, the Alfheim story companion: a glowing SPEAKING wisp (original pixel art, Hearthmoor cozy HD-2D style lock).

    python3 -B lumi_gen.py [--out DIR]        # writes everything next to this file by default (byte-identical reruns)

Lumi is a round NEON-BLUE cold-fire starlight wisp with a PULSING VIOLET HALO, clearly bigger and brighter than the wisp-kit pet (pet_wisp, blue cold fire):
a 14 px glowing orb with a big readable face (2x3 ink eyes with white glints, rose cheeks, a mouth that talks), a
five-tongue flame CROWN whose tips throw prism flecks (starlight aqua / gold / lilac / white, shifting frame to frame:
Alfheim's prism light), two little flame "hands" that gesture when she talks, and a curling STARRY TAIL that trails
star motes down to the ground row.

Actor sheet (lumi.png = NEON, primary; lumi_safe.png = palette-only, check-sprite PASS):
  32x40 cells, pivot [16, 40], ground row 39, rows down / up / left / right (right = mirrored left).
  Columns: idle 0-3 (3 = blink) | walk 4-7 (float drift) | follow 8-11 | talk 12-15 (mouth + glow pulse) |
           happy 16-17 | worried 18-19 | surprised 20-21.
  She is drawn standing on her tail tip; the runtime lifts the visible quad with `a.lift` (shadow + depth stay put).
Portraits (lumi_portrait.png): 33x33 bust cells, one per expression, for the 66x66 #dlgFace canvas at integer 2x.
FX (lumi_fx.png/json, tools/spells format, 32 px cells): aura, light pool, talk pulse, three emote pops.
Particles (lumi_particles.png/json, tools/particles format, 16 px cells): starlight mote, prism glint.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ------------------------------------------------------------------ palette (cozy-village biome.json) + NEON glow accents
PAL = {
    "ink": "#2a1e1c", "shadow": "#4c3a3e", "plaster_hi": "#f6ecd2", "plaster": "#e6d2ac", "plaster_lo": "#c4a984",
    "timber_hi": "#b07a44", "timber": "#7a4e2e", "timber_lo": "#4a2e20", "stone_hi": "#cfc2a6", "stone": "#9c8e7a",
    "stone_lo": "#6a5e56", "roof_hi": "#d0704a", "roof": "#9a4630", "roof_lo": "#622c24", "grass_hi": "#b2c464",
    "grass": "#72a046", "moss": "#4a7234", "leaf_deep": "#2c4c30", "flower_rose": "#e47c8c", "flower_gold": "#f2c24a",
    "flower_blue": "#6c8cd4", "skin": "#f2c4a0", "skin_lo": "#cc8c6c", "cloth": "#3e5a8c", "sky": "#94c0dc",
    "lamp": "#ffb24a", "white": "#fff8e6",
}
# NEON glow hexes (glowing pixels only). Lumi (alfheim.md 5.5 per the lead): a NEON-BLUE core in the cold-fire family
# (#5ab4f0 + a near-white-cyan highlight, brighter than pet_wisp's palette blues) and a PULSING VIOLET halo (spells.py
# neon violet); prism flecks = starlight aqua + violet hi + palette gold + white.
NEON = {"cold": "#5ab4f0", "cold_hi": "#d8f4ff", "cold_lo": "#2a6cb0",
        "neon_violet_lo": "#6a34b8",
        "neon_blue_hi": "#a6ecff", "neon_violet_hi": "#d4a8ff", "neon_violet": "#a45cf0"}
ALL = {**PAL, **NEON}
SIGNATURE = {"name": "Lumi blue core + violet halo", "hex": "#5ab4f0", "hi": "#d8f4ff", "lo": "#2a6cb0",
             "halo": {"hex": "#a45cf0", "hi": "#d4a8ff", "lo": "#6a34b8"},
             "prism_flecks": ["#a6ecff", "#f2c24a", "#d4a8ff", "#fff8e6"]}


def rgb(h):
    h = ALL.get(h, h).lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


FW, FH = 32, 40
PIVOT = [16, 40]
GROUND = 39
FACINGS = ("down", "up", "left", "right")
ANIMS = {"idle": {"start": 0, "count": 4, "fps": 3, "loop": [0, 1, 2, 1], "blink": 3},
         "walk": {"start": 4, "count": 4, "fps": 8},
         "follow": {"start": 8, "count": 4, "fps": 10},
         "talk": {"start": 12, "count": 4, "fps": 8, "loop": [0, 1, 2, 1, 0, 3, 2, 1]},
         "happy": {"start": 16, "count": 2, "fps": 4, "loop": [0, 1]},
         "worried": {"start": 18, "count": 2, "fps": 5, "loop": [0, 1]},
         "surprised": {"start": 20, "count": 2, "fps": 6, "loop": [0, 1, 1, 1], "hold": [1]}}
COLS = 22
DECAL_SQUASH = math.sin(math.radians(36))

# colour slots: NEON (primary) vs lock-safe palette-only
SLOTS_NEON = {"l_rim": "cold_lo", "l_body": "cold", "l_hi": "cold_hi", "l_core": "white",
              "l_halo": "neon_violet", "l_halo_hi": "neon_violet_hi", "l_halo_lo": "neon_violet_lo",
              "l_cheek": "flower_rose", "l_p1": "neon_blue_hi", "l_p2": "flower_gold", "l_p3": "neon_violet_hi",
              "l_tear": "neon_blue_hi"}
SLOTS_SAFE = {"l_rim": "cloth", "l_body": "flower_blue", "l_hi": "sky", "l_core": "white",
              "l_halo": "flower_rose", "l_halo_hi": "plaster_hi", "l_halo_lo": "shadow",
              "l_cheek": "flower_rose", "l_p1": "white", "l_p2": "flower_gold", "l_p3": "flower_rose",
              "l_tear": "sky"}
PRISM = ("l_p1", "l_p2", "l_p3", "l_core")


class Spr:
    def __init__(self, slots, w=FW, h=FH):
        self.w, self.h, self.slots = w, h, slots
        self.p = [[None] * w for _ in range(h)]

    def set(self, x, y, c):
        x, y = int(math.floor(x + 0.5)), int(math.floor(y + 0.5))
        if c and 0 <= x < self.w and 0 <= y < self.h:
            c = self.slots.get(c, c)
            assert c in ALL, c
            self.p[y][x] = c

    def get(self, x, y):
        return self.p[y][x] if 0 <= x < self.w and 0 <= y < self.h else None

    def ell(self, cx, cy, rx, ry, fn):
        R = int(max(rx, ry)) + 2
        for y in range(int(cy) - R, int(cy) + R + 1):
            for x in range(int(cx) - R, int(cx) + R + 1):
                u, v = x - cx, y - cy
                d = (u / rx) ** 2 + (v / ry) ** 2
                if d <= 1.0:
                    self.set(x, y, fn(x, y, d, u, v) if callable(fn) else fn)

    def stamp(self, cx, cy, rows, cmap):
        h, w = len(rows), len(rows[0])
        x0, y0 = int(math.floor(cx - w / 2 + 0.5)), int(math.floor(cy - h / 2 + 0.5))
        for j, r in enumerate(rows):
            for i, ch in enumerate(r):
                if ch != ".":
                    self.set(x0 + i, y0 + j, cmap[ch])

    def outline(self, margin=True):
        if margin:
            for y in range(self.h):
                for x in range(self.w):
                    if x in (0, self.w - 1) or y in (0, self.h - 1):
                        self.p[y][x] = None
        src = [r[:] for r in self.p]
        for y in range(self.h):
            for x in range(self.w):
                if not src[y][x] and any(0 <= y + dy < self.h and 0 <= x + dx < self.w and src[y + dy][x + dx]
                                         for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    self.p[y][x] = "ink"
        return self

    def mirror(self):
        for r in self.p:
            r.reverse()
        return self

    def image(self):
        im = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        px = im.load()
        for y in range(self.h):
            for x in range(self.w):
                if self.p[y][x]:
                    px[x, y] = rgb(self.p[y][x]) + (255,)
        return im


CMAP = {"K": "ink", "W": "l_core", "R": "l_rim", "H": "l_hi", "B": "l_body", "C": "l_cheek", "T": "l_tear"}


def star(s, x, y, size, k):
    """a prism star: white heart, arms in prism colour k (size 0 = a lone fleck)"""
    s.set(x, y, "l_core" if size else PRISM[k % 4])
    for r in range(1, size + 1):
        for dx, dy in ((r, 0), (-r, 0), (0, r), (0, -r)):
            s.set(x + dx, y + dy, PRISM[k % 3])


# ------------------------------------------------------------------ face stamps (sprite scale)
EYES = {
    "open": ["WK", "KK", "KK"],
    "blink": ["..", "..", "KK"],
    "happy": [".K.", "K.K"],
    "worried": ["KK", "KK", "KW"],
    "wide": ["WK", "KK", "KK", "KK"],
}
MOUTHS = {
    "smile": ["K..K", ".KK."],
    "talk_s": ["KKKK", ".KK."],
    "talk_w": ["KKKK", "KRRK", ".KK."],
    "grin": ["KKKKKK", ".KRRK.", "..KK.."],
    "frown": [".KK.", "K..K"],
    "o": [".KK.", "KRRK", ".KK."],
    "wee": ["KK", "KK"],
}


def halo(s, cx, cy, rx, ry, glow, fl, w=1.0):
    """pulsing violet halo ring just outside the orb: glow 0 = a dim broken lo ring, 1 = violet, 2-3 = violet with
    lilac beads + a 2nd ring hint. Drawn only on empty pixels (under hands / crown / tail)."""
    R = int(max(rx, ry)) + 4
    for y in range(int(cy) - R, int(cy) + R + 1):
        for x in range(int(cx) - R, int(cx) + R + 1):
            u, v = x - cx, y - cy
            d = math.sqrt((u / rx) ** 2 + (v / ry) ** 2)
            a = math.atan2(v, u)
            band = 1.0 + (1.25 + 0.12 * glow) * w / max(rx, ry)
            if not (1.0 < d <= band) or s.get(x, y):
                continue
            k = int((a + math.pi) / math.tau * 24 + fl * 2) % 24
            if glow == 0:
                c = "l_halo_lo" if k % 3 else None
            elif glow == 1:
                c = "l_halo" if k % 4 else "l_halo_lo"
            else:
                c = "l_halo_hi" if k % (6 if glow == 2 else 4) == 0 else "l_halo"
            s.set(x, y, c)


def pose(face, anim, i):
    """per-frame parameters"""
    P = dict(b=0, sway=0, lean=0, fl=i, glow=0, eyes="open", mouth="smile", hands=(0, 0), crown=1.0,
             sparks="idle", stretch=0.0, shake=0, brows=None, tear=False)
    if anim == "idle":
        P.update(b=[0, -1, -1, 0][i], sway=[0, 1, 0, 1][i], glow=[0, 1, 2, 0][i], eyes="blink" if i == 3 else "open")
    elif anim == "walk":
        P.update(b=[-1, -2, -1, -2][i], sway=[1, 0, -1, 0][i], lean=1, fl=i + 1, glow=1, sparks="walk", hands=(1, 1))
    elif anim == "follow":
        P.update(b=[-2, -3, -2, -3][i], sway=[1, 2, 1, 2][i], lean=2, fl=i + 2, glow=1, mouth="wee", sparks="follow",
                 hands=(1, 1), crown=1.2)
    elif anim == "talk":
        P.update(b=[0, -1, -1, -1][i], sway=[0, 1, 0, 1][i], glow=[0, 1, 3, 2][i],
                 mouth=["smile", "talk_s", "talk_w", "talk_s"][i], hands=[(0, 0), (2, 0), (2, 2), (0, 2)][i],
                 crown=[1.0, 1.1, 1.35, 1.15][i], sparks="talk")
    elif anim == "happy":
        P.update(b=[-2, 0][i], sway=[1, 0][i], glow=3, eyes="happy", mouth="grin", hands=(3, 3), crown=[1.4, 1.2][i],
                 sparks="happy", stretch=[0.5, -0.4][i])
    elif anim == "worried":
        P.update(b=[1, 1][i], shake=[0, 1][i], glow=0, eyes="worried", mouth="frown", hands=(-1, -1), crown=0.6,
                 sparks="none", brows="worried", tear=True)
    elif anim == "surprised":
        P.update(b=[-3, -2][i], glow=[3, 2][i], eyes="wide", mouth="o", hands=(3, 3), crown=[1.7, 1.45][i],
                 sparks="surprised", stretch=[1.0, 0.5][i], brows="up")
    return P


def draw_lumi(s, face, anim, i):
    P = pose(face, anim, i)
    side = face == "left"
    up = face == "up"
    lean = P["lean"]
    cx = 15.5 - (lean if side else 0) + (P["shake"] if anim == "worried" else 0)
    cy = 20.0 + P["b"]
    rx = 6.6 - 0.3 * P["stretch"] + (0.4 if (side and anim == "follow") else 0)
    ry = 6.2 + 0.4 * P["stretch"] - (0.3 if (side and anim == "follow") else 0)
    fl = P["fl"]

    # --- starry tail: tapers from the orb's base to its tip on the ground row (row 38; the ink pass closes row 39)
    top = int(cy + ry) - 2
    n = 38 - top
    tip = cx
    for k in range(n + 1):
        y = top + k
        t = k / max(1, n)
        if side:
            off = (2.0 + lean * 1.1) * math.sin(t * math.pi) * 1.8 + P["sway"] * 0.4 * t - (cx - 15.5) * t
        else:
            off = math.sin(t * 3.3 + P["sway"] * 0.9 + (0.6 if up else 0)) * (1.3 + 0.4 * abs(P["sway"])) * t * 1.7
        w = 2.7 * (1 - t) ** 0.95 + 0.25
        x0 = cx + off
        tip = x0
        for x in range(int(math.floor(x0 - w + 0.5)), int(math.floor(x0 + w + 0.5)) + 1):
            dx = abs(x - x0)
            s.set(x, y, "l_hi" if (dx < w - 1.6 and t < 0.55) else "l_body" if dx < w - 0.6 or t > 0.6 else "l_rim")
    s.set(tip, 38, "l_body")
    # stars riding the tail (prism flecks shifting frame to frame)
    for j, tt in enumerate((0.38, 0.62, 0.84)):
        y = min(top + tt * n, 35)
        t = tt
        if side:
            off = (2.0 + lean * 1.1) * math.sin(t * math.pi) * 1.8 + P["sway"] * 0.4 * t - (cx - 15.5) * t
        else:
            off = math.sin(t * 3.3 + P["sway"] * 0.9 + (0.6 if up else 0)) * (1.3 + 0.4 * abs(P["sway"])) * t * 1.7
        sideoff = (4.2 - 1.5 * tt) * (1 if (j + fl) % 2 == 0 else -1)
        if side:
            sideoff = abs(sideoff)
        star(s, cx + off + sideoff, y, 1 if (j + fl) % 3 == 0 else 0, j + fl)

    # --- flame hands (little tufts) at the orb's sides: level -1 tucked in, 0 rest, 1 trailing, 2 gesture, 3 raised
    for sgn, lv in ((-1, P["hands"][0]), (1, P["hands"][1])):
        if side and sgn == 1 and lv < 2:
            continue
        hy = cy + {-1: 3.5, 0: 2.5, 1: 2.0, 2: -0.5, 3: -3.0}[lv]
        hx = cx + sgn * (rx + (0.6 if lv >= 2 else 0.2 if lv >= 0 else -0.9))
        s.set(hx, hy, "l_body"); s.set(hx + sgn, hy, "l_body"); s.set(hx, hy + 1, "l_body")
        s.set(hx + sgn, hy - 1, "l_hi" if lv >= 2 else "l_body")
        if lv >= 2:
            s.set(hx + sgn * 2, hy - 1, "l_hi")

    # --- crown: five flame tongues rising from the orb's top (prism fleck jewels over the tips)
    base = cy - ry + 1.5
    crown = P["crown"]
    tongues = [(-4, 2), (-2, 4), (0, 6), (2, 4), (4, 2)]
    for ti, (dx, h0) in enumerate(tongues):
        wob = [0, 1, 0, -1][(fl + ti) % 4]
        hgt = max(1, int(round(h0 * crown + ((fl + ti) % 2) * 0.8)))
        if anim == "worried":
            hgt = max(1, h0 // 2)
        for k in range(0, hgt + 1):
            y = base - k
            t = k / max(1, hgt)
            if side:
                x = cx - 0.5 + dx * 0.9 + k * (0.45 + 0.35 * lean)
            else:
                x = cx + dx + (wob * 0.6 if t > 0.55 else 0) + (dx * 0.12 * k if abs(dx) == 4 else 0)
                x += 0.0 if dx > 0 else -0.5
            c = "l_core" if (k == hgt and P["glow"] >= 2) else "l_hi" if t > 0.45 else "l_body"
            if anim == "worried" and k == hgt:
                c = "l_body"
            s.set(x, y, c)
            if t <= 0.5:
                s.set(x + 1, y, "l_body" if k < 1 else "l_hi")
        if anim != "worried" and (ti + fl) % 2 == 0 and hgt >= 2:
            jx = (cx - 0.5 + dx * 0.9 + (hgt + 2) * (0.45 + 0.35 * lean)) if side else (cx + dx + (0 if dx <= 0 else 1) - 0.5)
            s.set(jx, base - hgt - 2, PRISM[(ti + fl) % 4])

    # --- the violet halo: a ring hugging the orb (under it), pulsing with the glow level
    halo(s, cx, cy, rx, ry, P["glow"], fl)
    # --- the orb: neon-blue body, near-white-cyan glowing face, rim crescent low-right, white-hot gloss up-left
    hiT = 0.42 + 0.07 * P["glow"]
    fx_ = -1.2 if side else 0.0
    fy_ = -0.8 if up else 0.4

    def orb(x, y, d, u, v):
        dd = ((u - fx_) / rx) ** 2 + ((v - fy_) / ry) ** 2
        if up:
            if d > 0.62 and v > ry * 0.15:
                return "l_rim"
            return "l_hi" if dd < hiT * 0.55 else "l_body"
        if dd < hiT:
            return "l_hi"
        if d > 0.7 and u > rx * 0.25 and (u + 0.5 * v) > rx * 0.55:
            return "l_rim"
        return "l_body"
    s.ell(cx, cy, rx, ry, orb)
    gx, gy = cx - rx * 0.55 + (0.6 if side else 0), cy - ry * 0.6
    s.set(gx, gy, "l_core"); s.set(gx + 1, gy, "l_core"); s.set(gx, gy + 1, "l_core")
    if P["glow"] >= 2:
        s.set(gx + 2, gy - 0.4, "l_core"); s.set(gx - 0.2, gy + 2, "l_hi")

    # --- face
    if not up:
        ey = cy + 0.4
        if side:
            ex = [cx - 4.0, cx - 0.2]
            mx = cx - 2.0
        else:
            ex = [cx - 2.6, cx + 2.6]
            mx = cx
        for j, x in enumerate(ex):
            rows = EYES[P["eyes"]]
            if side and j == 1 and P["eyes"] in ("open", "worried", "wide"):
                rows = [r[1:] for r in rows]       # the far eye, foreshortened to 1 px wide
            if P["eyes"] == "worried" and j == 1 and not side:
                rows = ["KK", "KK", "WK"]
            s.stamp(x, ey, rows, CMAP)
        if P["brows"] == "worried":
            if side:
                s.set(ex[0] - 0.5, ey - 3, "ink"); s.set(ex[0] + 0.5, ey - 3.6, "ink")
            else:
                s.set(ex[0] - 0.5, ey - 2.6, "ink"); s.set(ex[0] + 0.5, ey - 3.4, "ink")
                s.set(ex[1] + 0.5, ey - 2.6, "ink"); s.set(ex[1] - 0.5, ey - 3.4, "ink")
        elif P["brows"] == "up":
            for x in ex:
                s.set(x - 0.5, ey - 3.4, "ink"); s.set(x + 0.5, ey - 3.4, "ink")
        my = ey + 3.2 + (0.5 if P["mouth"] in ("talk_w", "grin", "o") else 0)
        s.stamp(mx, my, MOUTHS[P["mouth"]], CMAP)
        if P["eyes"] != "wide":
            cheeks = [cx + 1.6] if side else [cx - 4.6, cx + 4.6]
            for x in cheeks:
                s.set(x, ey + 2.0, "l_cheek")
        if P["tear"]:
            tx = cx + rx + 1.2 if not side else cx + rx * 0.4
            ty = cy - ry * 0.4
            s.set(tx, ty, "l_tear"); s.set(tx, ty + 1, "l_tear"); s.set(tx, ty - 1, "l_core")

    # --- sparkles in the air around her (they get the ink pass too)
    S = P["sparks"]
    if S == "idle":
        pts = [((3, 18), (28, 23)), ((28, 15),), ((4, 24), (27, 10)), ((28, 15),)][i]
        for k, (x, y) in enumerate(pts):
            star(s, x, y + P["b"], 1 if (k == 0 and i == 2) else 0, i + k)
    elif S == "walk":
        pts = [((27, 19),), ((3, 15), (28, 25)), ((27, 27),), ((3, 21), (28, 14))][i]
        for k, (x, y) in enumerate(pts):
            star(s, x, y, 0, i + k)
    elif S == "follow":
        trail = ([((26, 20), (29, 26)), ((27, 17), (28, 28)), ((26, 23), (29, 16)), ((27, 26), (29, 20))] if side else
                 [((3, 12), (28, 11)), ((2, 17), (29, 15)), ((4, 9), (27, 9)), ((2, 14), (29, 13))])[i]
        for k, (x, y) in enumerate(trail):
            star(s, x, y, 1 if k == 0 else 0, i + k)
    elif S == "talk":
        if i == 2:                                      # the glow pulse peak: a ring of flecks
            for (x, y) in ((3, 17), (28, 17), (5, 9), (26, 9)):
                star(s, x, y + P["b"], 0, x)
            star(s, 28, 25, 1, 1)
        elif i in (1, 3):
            star(s, 3 if i == 1 else 28, 13, 0, i)
    elif S == "happy":
        for k, (x, y) in enumerate(((3, 10), (28, 12), (4, 24), (27, 26)) if i == 0 else ((2, 14), (29, 8), (3, 27), (28, 22))):
            star(s, x, y, 1 if k < 2 else 0, k + i)
    elif S == "surprised":
        lines = [((4, 8), (5, 9)), ((27, 8), (26, 9)), ((2, 17), (3, 17)), ((29, 17), (28, 17))]
        for (a, b2) in lines[: 4 if i == 0 else 2]:
            s.set(*a, "l_core"); s.set(*b2, "l_p1")
    return tip


ROLE = {
    "name": "Lumi",
    "desc": ("Lumi, the Alfheim story companion: a speaking neon-blue cold-fire starlight wisp with a pulsing violet halo, a big readable face, a five-tongue "
             "flame crown that throws prism flecks, little flame hands that gesture when she talks and a curling starry tail. "
             "Hovers at the hero's eye level; follows like a pet but talks like a person."),
    "hover": {"lift": 0.3, "bob": 0.08, "hz": 0.7},
    "light": {"color": "#5ab4f0", "intensity": 7.0, "range": 5.0, "lift": 1.45, "fadeIn": 0.5, "r": 3.0,
              "pulse": [0.85, 1.12, 0.7],
              "talk_pulse": {"by_frame": [1.0, 1.12, 1.3, 1.15], "note": "multiply base by this per talk column 12-15"},
              "emote": {"happy": 1.25, "worried": 0.7, "surprised": 1.45},
              "halo": {"color": "#a45cf0", "hi": "#d4a8ff", "mode": "tint_pulse", "mix": [0.0, 0.35], "hz": 0.7,
                       "sync": "pulse", "note": "lerp the core light toward violet by mix[0]..mix[1] in step with the "
                                                "intensity pulse (peak = most violet); talk col 14 / happy / surprised = mix[1]",
                       "second_light": {"optional": True, "color": "#a45cf0", "intensity": 2.5, "range": 6.5, "lift": 1.45,
                                        "pulse": [0.4, 1.0, 0.7], "note": "only where the 2-3 light cap allows (cutscenes, "
                                                                          "Wisp Night): a wide faint violet halo light"}},
              "prism_shift": {"optional": True, "colors": ["#5ab4f0", "#a6ecff", "#d4a8ff", "#ffd27a"], "period_s": 6.0,
                              "mix": 0.25, "note": "Wisp Night / Prism Vault only: lerp the light colour 25% toward each in turn"}},
    "aura": "lumi_aura", "pool": "lumi_pool", "talk_fx": "lumi_talk_pulse",
    "emote_fx": {"happy": "lumi_emote_happy", "worried": "lumi_emote_worried", "surprised": "lumi_emote_surprised"},
    "particles": ["lumi_starlight", "lumi_prism_glint"], "speed": 2.6, "behavior": "follow",
}


def frame(facing, anim, i, slots):
    s = Spr(slots)
    face = "left" if facing == "right" else facing
    draw_lumi(s, face, anim, i)
    s.outline()
    return s.mirror() if facing == "right" else s


def build_sheet(slots):
    im = Image.new("RGBA", (FW * COLS, FH * 4), (0, 0, 0, 0))
    frames = []
    for fi, facing in enumerate(FACINGS):
        for anim, A in ANIMS.items():
            for i in range(A["count"]):
                col = A["start"] + i
                x, y = col * FW, fi * FH
                im.paste(frame(facing, anim, i, slots).image(), (x, y))
                frames.append({"name": f"lumi_{facing}_{anim}{i}", "facing": facing, "anim": anim, "i": i,
                               "x": x, "y": y, "w": FW, "h": FH, "pivot": [x + PIVOT[0], y + PIVOT[1]]})
    role = {"row": 0, "kind": "creature", "companion": True, "speaks": True, "name": ROLE["name"], "desc": ROLE["desc"],
            "size_bounds": [[12, 32], [24, 40]], "caster": False, "anims": list(ANIMS), "frames": frames,
            "lumifx": {k: ROLE[k] for k in ("hover", "light", "aura", "pool", "talk_fx", "emote_fx", "particles", "speed", "behavior")}}
    return im, {"lumi": role}


# ------------------------------------------------------------------ dialogue portrait: 33x33 bust cells (66x66 canvas at 2x)
PW = 33
PEYES = {
    "open": [".KK.", "KWWK", "KWKK", "KKKK", "KKKK", ".KK."],
    "blink": ["....", "....", "....", "K..K", ".KK.", "...."],
    "happy": [".KK.", "K..K", "K..K", "...."],
    "worried": [".KK.", "KKKK", "KKKK", "KKWK", "KKKK", ".KK."],
    "wide": [".KK.", "KWWK", "KWKK", "KKKK", "KKKK", "KKKK", ".KK."],
}
PMOUTHS = {
    "smile": ["K....K", ".KKKK."],
    "talk_s": ["KKKKKK", ".KRRK.", "..KK.."],
    "talk_w": ["KKKKKK", "KRRRRK", "KRRRRK", ".KKKK."],
    "grin": ["KKKKKKKK", "KRRRRRRK", ".KRRRRK.", "..KKKK.."],
    "frown": ["..KK..", ".K..K.", "K....K"],
    "o": ["..KK..", ".KRRK.", ".KRRK.", "..KK.."],
}
PORTRAITS = [("neutral", "open", "smile", 0, None), ("talk_a", "open", "talk_s", 1, None), ("talk_b", "open", "talk_w", 3, None),
             ("blink", "blink", "smile", 0, None), ("happy", "happy", "grin", 3, None),
             ("worried", "worried", "frown", 0, "worried"), ("surprised", "wide", "o", 3, "up")]


def draw_portrait(slots, eyes, mouth, glow, brows, k):
    s = Spr(slots, PW, PW)
    cx, cy, rx, ry = 16.0, 21.0, 12.4, 11.4
    crown = 1.0 + 0.12 * glow
    if brows == "worried":
        crown = 0.6
    base = cy - ry + 2
    for ti, (dx, h0) in enumerate([(-8, 3), (-4, 5), (0, 7), (4, 5), (8, 3)]):
        hgt = min(int(base - 4), max(2, int(round(h0 * crown + (ti + k) % 2))))
        for kk in range(hgt + 1):
            t = kk / hgt
            wob = [0, 1, 0, -1][(k + ti + kk // 3) % 4] if t > 0.5 else 0
            x = cx + dx + wob + (dx * 0.1 * kk if abs(dx) == 8 else 0)
            w = 2.2 * (1 - t) + 0.4
            for xx in range(int(math.floor(x - w + 0.5)), int(math.floor(x + w + 0.5)) + 1):
                c = "l_core" if (t > 0.85 and glow >= 2 and brows != "worried") else "l_hi" if t > 0.4 else "l_body"
                s.set(xx, base - kk, c)
        if brows != "worried" and (ti + k) % 2 == 0:
            star(s, cx + dx + (1 if dx > 0 else -1 if dx < 0 else 0), base - hgt - 2.5, 1 if ti == 2 else 0, ti + k)
    # hands
    for sgn in (-1, 1):
        hy = cy + (6 if brows == "worried" else 4) + (-6 if glow >= 3 else 0)
        hx = cx + sgn * (rx + (0.4 if glow >= 3 else -0.4))
        for (dx, dy, c) in ((0, 0, "l_body"), (sgn, 0, "l_body"), (0, 1, "l_body"), (sgn, -1, "l_hi"), (sgn * 2, -1, "l_hi"), (sgn, 1, "l_body")):
            s.set(hx + dx, hy + dy, c)
    hiT = 0.4 + 0.07 * glow
    halo(s, cx, cy, rx, ry, 1 if brows == "worried" else max(1, glow), k, w=1.6)

    def orb(x, y, d, u, v):
        if ((u) / rx) ** 2 + ((v - 1.0) / ry) ** 2 < hiT:
            return "l_hi"
        if d > 0.78 and (u * 0.55 + v) > ry * 0.35:
            return "l_rim"
        return "l_body"
    s.ell(cx, cy, rx, ry, orb)
    for (dx, dy) in ((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (0, 2), (-1, 1)):
        s.set(cx - 7 + dx, cy - 7 + dy, "l_core")
    if glow >= 2:
        s.set(cx - 3, cy - 8, "l_core")
    ey = cy + 0.5
    for j, x in enumerate((cx - 5, cx + 5)):
        s.stamp(x, ey, PEYES[eyes], CMAP)
    if brows == "worried":
        s.stamp(cx - 5, ey - 5, ["...K", "KKK."], CMAP)
        s.stamp(cx + 5, ey - 5, ["K...", ".KKK"], CMAP)
    elif brows == "up":
        s.stamp(cx - 5, ey - 5.5, [".KK.", "K..K"], CMAP)
        s.stamp(cx + 5, ey - 5.5, [".KK.", "K..K"], CMAP)
    if eyes != "wide":
        for x in (cx - 9, cx + 8):
            s.set(x, ey + 4, "l_cheek"); s.set(x + 1, ey + 4, "l_cheek")
    s.stamp(cx, ey + 6.5, PMOUTHS[mouth], CMAP)
    if brows == "worried":
        s.set(cx + 11, cy - 6, "l_core"); s.set(cx + 11, cy - 5, "l_tear"); s.set(cx + 11, cy - 4, "l_tear"); s.set(cx + 10, cy - 4, "l_tear")
    s.outline(margin=False)
    # the bust is cut at the bottom edge (no outline along the frame bottom, like an engine crop)
    for x in range(PW):
        if s.p[PW - 1][x] == "ink" and s.p[PW - 2][x] not in (None, "ink"):
            s.p[PW - 1][x] = s.slots.get("l_body")
    return s


def build_portraits(slots):
    im = Image.new("RGBA", (PW * len(PORTRAITS), PW), (0, 0, 0, 0))
    meta = []
    for k, (name, eyes, mouth, glow, brows) in enumerate(PORTRAITS):
        im.paste(draw_portrait(slots, eyes, mouth, glow, brows, k).image(), (k * PW, 0))
        meta.append({"name": name, "x": k * PW, "y": 0, "w": PW, "h": PW})
    return im, meta


# ------------------------------------------------------------------ 32 px effects (tools/spells format)
CELL = 32
CORE = ("l_hi", "l_body", "l_rim")


class Cell:
    def __init__(self, slots):
        self.slots = slots
        self.p = [[None] * CELL for _ in range(CELL)]

    def set(self, x, y, c):
        x, y = int(math.floor(x + 0.5)), int(math.floor(y + 0.5))
        if c and 0 <= x < CELL and 0 <= y < CELL:
            c = self.slots.get(c, c)
            assert c in ALL, c
            self.p[y][x] = c

    def star(self, x, y, size, core, arm, tip=None):
        self.set(x, y, core)
        for k in range(1, size + 1):
            c = arm if k < size or not tip else tip
            for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)):
                self.set(x + dx, y + dy, c)

    def image(self):
        im = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
        px = im.load()
        for y in range(CELL):
            for x in range(CELL):
                if self.p[y][x]:
                    px[x, y] = rgb(self.p[y][x]) + (255,)
        return im


def fx_aura(slots, seed=31, n=8):
    """prism starlight orbiting Lumi on two tilted rings (violet halo ring, prism outer flecks) + rising star motes"""
    R = random.Random(seed)
    ph = [k * math.tau / 7 + R.random() * 0.5 for k in range(7)]
    motes = [(5 + R.random() * 22, 10 + R.random() * 20, R.randrange(8), R.randrange(4)) for _ in range(10)]
    out = []
    for f in range(n):
        F = Cell(slots)
        for k, a0 in enumerate(ph):
            a = a0 + f * math.tau / n * (1 if k % 2 == 0 else -0.6)
            rx, ry = (12.5, 6.5) if k % 2 == 0 else (10.0, 4.5)
            x, y = 16 + math.cos(a) * rx, 16 + math.sin(a) * ry
            b = (f + k * 3) % 8
            col = PRISM[k % 3] if k % 2 else "l_halo_hi"
            if b in (1, 5):
                F.set(x, y, "l_halo")
            elif b == 2:
                F.star(x, y, 1, "l_core", col)
            elif b == 3:
                F.star(x, y, 2, "l_core", col, tip="l_halo_lo")
            elif b in (4, 6):
                F.set(x, y, col)
        for (x, y, p, c) in motes:
            b = (f + p) % 8
            yy = y - b * 1.1
            if b in (1, 4):
                F.set(x, yy, PRISM[c])
            elif b == 2:
                F.star(x, yy, 1, "l_core", "l_hi")
            elif b == 3:
                F.set(x, yy, "l_halo_lo")
        out.append(F)
    return out


def fx_pool(slots, seed=9, rx0=14.5, n=6):
    """her ground pool: wider + denser than pet_wisp's, a white-hot heart, a turning dotted rim with prism flecks"""
    R = random.Random(seed)
    jit = [[R.random() for _ in range(CELL)] for _ in range(CELL)]
    out = []
    for f in range(n):
        F = Cell(slots)
        rx = rx0 * [1.0, 0.96, 0.92, 0.9, 0.93, 0.97][f]
        for y in range(CELL):
            for x in range(CELL):
                d = math.hypot(x - 16, (y - 16) / DECAL_SQUASH) / rx
                if d > 1:
                    continue
                dens = 0.95 * (1 - d) ** 1.0 + 0.1
                if (x + y + f) % 2 == 0 and jit[y][x] < dens:
                    c = "l_core" if (d < 0.2 and (x + 2 * y + f) % 3 == 0) else "l_hi" if d < 0.4 else "l_body" if d < 0.66 else "l_halo"
                    F.set(x, y, c)
        for k in range(int(rx * 6)):
            if k % 4:
                continue
            a = f * 0.21 + k / (rx * 6) * math.tau
            F.set(16 + math.cos(a) * rx, 16 + math.sin(a) * rx * DECAL_SQUASH, PRISM[(k // 4 + f) % 3] if (k // 4) % 3 == 0 else "l_halo_lo")
        out.append(F)
    return out


def fx_talk(slots, n=6):
    """the talk pulse: a ring of violet halo flecks breathing out from her orb while she speaks (loops with the talk anim)"""
    out = []
    for f in range(n):
        F = Cell(slots)
        r = 7 + f * 1.4
        cnt = 12
        for k in range(cnt):
            if (k + f) % 2:
                continue
            a = k / cnt * math.tau + f * 0.12
            x, y = 16 + math.cos(a) * r, 16 + math.sin(a) * r * 0.85
            c = "l_core" if f < 2 else "l_halo_hi" if f < 4 else "l_halo" if f < 5 else "l_halo_lo"
            F.set(x, y, c)
            if f in (1, 2) and k % 4 == 0:
                F.star(x, y, 1, "l_core", PRISM[k % 3])
        out.append(F)
    return out


def fx_emote(slots, kind, n=4):
    """small pops over her crown: happy = a violet heart + flecks, worried = a starlight sweat drop + scribble,
    surprised = a white '!' with a burst"""
    out = []
    HEART = [".HH.HH.", "HBBHBBH", "HBBBBBH", ".HBBBH.", "..HBH..", "...H..."]
    DROP = ["..T..", ".TTT.", "TTTWT", "TTTTT", ".TTT."]
    BANG = ["WW", "WW", "WW", "WW", "..", "WW"]
    cm = {"H": "l_halo_hi", "B": "l_halo", "T": "l_tear", "W": "l_core", "R": "l_halo_lo"}
    for f in range(n):
        F = Cell(slots)
        rise = [0, -1, -2, -2][f]

        def stamp(cx, cy, rows):
            for j, r in enumerate(rows):
                for i, ch in enumerate(r):
                    if ch != ".":
                        F.set(cx - len(r) // 2 + i, cy - len(rows) // 2 + j, cm[ch])
        if kind == "happy":
            stamp(16, 15 + rise, HEART if f != 3 else HEART[:-1])
            for k, (x, y) in enumerate(((8, 12), (24, 10), (10, 20), (23, 19))):
                if (k + f) % 2 == 0:
                    F.star(x, y + rise, 1 if f == 1 else 0, "l_core", PRISM[k % 3])
        elif kind == "worried":
            stamp(20, 13 + [0, 1, 2, 1][f], DROP)
            for k in range(5):
                F.set(9 + k, 14 + ((k + f) % 2), "l_halo_lo")
        else:
            stamp(16, 14 + [1, 0, 0, 0][f], BANG)
            if f < 3:
                for (dx, dy) in ((-5, -4), (5, -4), (-6, 1), (6, 1), (0, -8)):
                    F.set(16 + dx * (1 + 0.2 * f), 14 + dy * (1 + 0.2 * f), "l_hi" if f else "l_core")
        out.append(F)
    return out


FX = {
    "lumi_aura": dict(fn=fx_aura, kind="billboard", fps=8, pivot=[16, 31], lift=0.0, follow_lift="hover",
                      desc="prism starlight orbiting Lumi on two tilted rings + rising star motes (NEON violet halo + blue / prism flecks)"),
    "lumi_pool": dict(fn=fx_pool, kind="decal", fps=5, pivot=[16, 16], lift=0.02,
                      desc="Lumi's ground pool: wider and denser than pet_wisp's, white-hot heart, turning rim with prism flecks"),
    "lumi_talk_pulse": dict(fn=fx_talk, kind="billboard", fps=8, pivot=[16, 16], lift=1.15, follow_lift="hover",
                            desc="talk pulse: a ring of violet halo flecks breathing out from her orb while she speaks (loop with talk)"),
    "lumi_emote_happy": dict(fn=lambda sl: fx_emote(sl, "happy"), kind="billboard", fps=6, pivot=[16, 31], lift=1.75,
                             follow_lift="hover", loop=False, desc="happy pop over her crown: a violet heart + prism flecks"),
    "lumi_emote_worried": dict(fn=lambda sl: fx_emote(sl, "worried"), kind="billboard", fps=5, pivot=[16, 31], lift=1.75,
                               follow_lift="hover", loop=False, desc="worried pop: a starlight sweat drop + a nervous scribble"),
    "lumi_emote_surprised": dict(fn=lambda sl: fx_emote(sl, "surprised"), kind="billboard", fps=8, pivot=[16, 31], lift=1.75,
                                 follow_lift="hover", loop=False, desc="surprised pop: a white '!' with a burst"),
}


def build_fx(slots, image_name):
    names = list(FX)
    atlas = Image.new("RGBA", (CELL * 8, CELL * len(names)), (0, 0, 0, 0))
    meta = {"tool": "hearthmoor-art lumi_gen (spells format)", "biome": "cozy-village", "image": image_name, "cell": CELL,
            "size": [atlas.width, atlas.height], "neon": {k: v for k, v in NEON.items() if k != "neon_blue"}, "effects": {}}
    frames_by = {}
    for row, nm in enumerate(names):
        e = FX[nm]
        frs = e["fn"](slots)
        frames_by[nm] = frs
        fl = []
        for i, F in enumerate(frs):
            atlas.paste(F.image(), (i * CELL, row * CELL))
            fl.append({"x": i * CELL, "y": row * CELL, "w": CELL, "h": CELL})
        loop = e.get("loop", True)
        meta["effects"][nm] = {"row": row, "frames": len(frs), "fps": e["fps"], "loop": loop, "loop_from": 0,
                               "loops": 1, "kind": e["kind"], "pivot": e["pivot"], "lift": e["lift"], "glow": True,
                               "light": None, "speed": None, "travel": None, "then": None, "frame_list": fl,
                               "combat": False, "duration": round(len(frs) / e["fps"], 3), "desc": e["desc"],
                               **({"follow_lift": e["follow_lift"]} if e.get("follow_lift") else {})}
    return atlas, meta, frames_by


# ------------------------------------------------------------------ 16 px particles (tools/particles format)
PCELL = 16
PROWS = ["lumi_starlight", "lumi_prism_glint"]


def build_particles(slots, image_name):
    im = Image.new("RGBA", (PCELL * 4, PCELL * len(PROWS)), (0, 0, 0, 0))
    px = im.load()

    def put(row, f, x, y, c):
        px[f * PCELL + x, row * PCELL + y] = rgb(slots.get(c, c)) + (255,)
    plus = lambda cc, arm: [(8, 8, cc), (7, 8, arm), (9, 8, arm), (8, 7, arm), (8, 9, arm)]
    shapes = {
        # a starlight mote shed by the tail: blue fleck, cyan star, white-hearted star with violet tips, fading
        "lumi_starlight": [[(8, 8, "l_body")], plus("l_core", "l_hi"),
                           plus("l_core", "l_body") + [(6, 8, "l_halo"), (10, 8, "l_halo"), (8, 6, "l_halo"), (8, 10, "l_halo")],
                           [(8, 8, "l_halo_lo")]],
        # a prism glint: shifts aqua -> gold -> lilac -> white as it twinkles
        "lumi_prism_glint": [[(8, 8, "l_p1"), (9, 8, "l_p1")], plus("l_core", "l_p2"), plus("l_core", "l_p3"), [(8, 8, "l_core")]],
    }
    for r, nm in enumerate(PROWS):
        for f, sh in enumerate(shapes[nm]):
            for (x, y, c) in sh:
                put(r, f, x, y, c)
    presets = {
        "lumi_starlight": {"row": 0, "frames": 4, "fps": 6, "mode": "life", "rate": 5.0, "life": [0.8, 1.5], "grade": None,
                           "vel": [[-0.12, 0.12], [-0.05, 0.3], [-0.12, 0.12]], "gravity": 0, "sway": 0.5, "glow": True,
                           "area": [0.3, 0.5, 0.3], "follow_companion": True, "note": "spawn along the tail (lift 0.3-1.1 m)"},
        "lumi_prism_glint": {"row": 1, "frames": 4, "fps": 5, "mode": "life", "rate": 2.5, "life": [0.6, 1.0], "grade": None,
                             "vel": [[-0.2, 0.2], [0.3, 0.6], [-0.2, 0.2]], "gravity": 0, "sway": 0.3, "glow": True,
                             "area": [0.45, 0.15, 0.35], "follow_companion": True,
                             "note": "spawn at the crown (lift ~1.9 m); double the rate while she talks"},
    }
    meta = {"tool": "hearthmoor-art lumi_gen (particles format)", "biome": "cozy-village", "image": image_name,
            "cell": PCELL, "rows": PROWS, "presets": presets}
    return im, meta


# ------------------------------------------------------------------ contact sheet
def font(sz, bold=False):
    for p in (f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf",):
        if Path(p).exists():
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def stepped_pool(d, cx, cy, rx, lc, base, steps=(0.07, 0.13, 0.2, 0.28), sq=0.34):
    for k, a in enumerate(steps):
        r = rx * (1 - k / len(steps))
        col = tuple(int(base[j] * (1 - a) + lc[j] * a) for j in range(3)) + (255,)
        d.ellipse([cx - r, cy - r * sq, cx + r, cy + r * sq], fill=col)


def night_ground(im, x0, y0, w, h, S, tint=(22, 20, 34)):
    d = ImageDraw.Draw(im)
    R = random.Random(3)
    d.rectangle([x0, y0, x0 + w - 1, y0 + h - 1], fill=tint + (255,))
    for yy in range(0, h // S, 4):
        off = 3 if (yy // 4) % 2 else 0
        for xx in range(-off, w // S, 6):
            c = R.choice([(30, 28, 46), (34, 31, 52), (27, 25, 42)])
            d.rectangle([x0 + max(0, xx) * S, y0 + yy * S, min(x0 + w - 1, x0 + (xx + 5) * S - 1),
                         min(y0 + h - 1, y0 + (yy + 3) * S - 1)], fill=c + (255,))


def contact(sheet, safe, portraits, fx_frames, p_im, hero, wisp, path):
    BG, PANEL, CELLBG = (18, 16, 28), (30, 27, 44), (24, 22, 36)
    TXT, SUB = (246, 236, 210), (172, 162, 160)
    F1, F2, F3 = font(24, True), font(14, True), font(12)
    L = ROLE["light"]
    lc = rgb(L["color"])
    S = 3
    cw, ch = FW * S, FH * S
    gap, left = 10, 84
    grid_w = left + COLS * (cw + 2) + 7 * gap
    W = grid_w + 20
    H = 92 + 470 + 60 + 4 * (FH * 3 + 2) + 40 + 16 + 290 + 16 + 30 + 100 * len(FX) + 60
    out = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(out)
    d.text((20, 14), "Lumi, Alfheim story companion: a speaking neon-blue wisp with a pulsing violet halo", fill=TXT, font=F1)
    d.text((20, 48), f"signature glow {SIGNATURE['hex']} (hi {SIGNATURE['hi']}, lo {SIGNATURE['lo']}) + violet halo {SIGNATURE['halo']['hex']} / {SIGNATURE['halo']['hi']} / {SIGNATURE['halo']['lo']} + prism flecks "
                     f"{' '.join(SIGNATURE['prism_flecks'])}   |   light {L['color']}  intensity {L['intensity']}  range {L['range']} m  "
                     f"lift {L['lift']} m  pulse x{L['pulse'][0]}-{L['pulse'][1]} @ {L['pulse'][2]} Hz   (pet_wisp: #5ab4f0, 4.0 / 3.2 m)",
           fill=SUB, font=F3)
    d.text((20, 66), "lumi.png (PRIMARY, NEON) 32x40 cells, pivot [16,40], ground row 39, nearest 3x, hard alpha, 1 px ink outline. "
                     "Rows down / up / left / right (right = mirrored left). Tinted ellipses = stepped stand-in for her point light (no bloom).",
           fill=SUB, font=F3)
    # ---- 1. night scale line-up (hero, pet_wisp, Lumi) at 4x
    y0 = 92
    sw, sh = W - 40, 430
    d.rectangle([10, y0, W - 10, y0 + sh + 40], fill=PANEL + (255,))
    d.text((20, y0 + 8), "1. Night scale line-up @4x: hero (wildcaller, 20x32), pet_wisp (20x32, hover 0.5 m), Lumi (32x40, hover 0.3 m: "
                         "her face sits at the hero's eye level). Pools sized by light range.", fill=TXT, font=F2)
    sx, sy = 20, y0 + 32
    S4 = 4
    night_ground(out, sx, sy, sw, sh, S4)
    gy = sy + sh - 50
    base = (24, 22, 38)
    # positions
    hx, wx, lx = sx + 380, sx + 640, sx + 1000
    stepped_pool(d, wx, gy, 30 * 3.2 / 3.2 * 4 * 1.0, rgb("#5ab4f0"), base, steps=(0.06, 0.12, 0.19, 0.27, 0.36))
    stepped_pool(d, lx, gy, 30 * 6.5 / 3.2 * 4, rgb("#a45cf0"), base, steps=(0.05, 0.1))
    stepped_pool(d, lx, gy, 30 * L["range"] / 3.2 * 4, lc, base, steps=(0.08, 0.14, 0.2, 0.27, 0.36, 0.46))
    shc = tuple(int(c * 0.55) for c in base) + (255,)
    for (x, r, c) in ((hx, 7, shc), (wx, 4, (34, 52, 74, 255)), (lx, 7, shc)):   # floating sprites: a faint tinted shadow
        d.ellipse([x - r * S4, gy - 1.2 * S4, x + r * S4, gy + 1.2 * S4], fill=c)
    pool = fx_frames["lumi_pool"][1].image().resize((CELL * S4, CELL * S4), Image.NEAREST)
    out.alpha_composite(pool, (lx - 16 * S4, gy - 16 * S4))
    if hero is not None:
        out.alpha_composite(hero.resize((20 * S4, 32 * S4), Image.NEAREST), (hx - 10 * S4, gy - 32 * S4))
    if wisp is not None:
        lift = int(round(0.5 * 32 / 1.8)) * S4
        out.alpha_composite(wisp.resize((20 * S4, 32 * S4), Image.NEAREST), (wx - 10 * S4, gy - 32 * S4 - lift))
    lift = int(round(ROLE["hover"]["lift"] * 32 / 1.8)) * S4
    lf = sheet.crop((0, 0, FW, FH)).resize((FW * S4, FH * S4), Image.NEAREST)
    out.alpha_composite(lf, (lx - 16 * S4, gy - 40 * S4 - lift))
    aura = fx_frames["lumi_aura"][3].image().resize((CELL * S4, CELL * S4), Image.NEAREST)
    out.alpha_composite(aura, (lx - 16 * S4, gy - 40 * S4 - lift + 2 * S4))
    # a talking Lumi turned to the hero, a second copy to the far right
    tx = sx + 1400
    stepped_pool(d, tx, gy, 30 * 6.5 / 3.2 * 4 * 0.8, rgb("#a45cf0"), base, steps=(0.06, 0.12))
    stepped_pool(d, tx, gy, 30 * L["range"] / 3.2 * 4 * 0.8, lc, base, steps=(0.06, 0.12, 0.19, 0.27, 0.36, 0.46))
    d.ellipse([tx - 7 * S4, gy - 1.2 * S4, tx + 7 * S4, gy + 1.2 * S4], fill=shc)
    out.alpha_composite(fx_frames["lumi_pool"][3].image().resize((CELL * S4, CELL * S4), Image.NEAREST), (tx - 16 * S4, gy - 16 * S4))
    if hero is not None:
        out.alpha_composite(hero.resize((20 * S4, 32 * S4), Image.NEAREST), (tx - 150 - 10 * S4, gy - 32 * S4))
    tf = sheet.crop((14 * FW, 2 * FH, 15 * FW, 3 * FH)).resize((FW * S4, FH * S4), Image.NEAREST)
    out.alpha_composite(tf, (tx - 16 * S4, gy - 40 * S4 - lift))
    out.alpha_composite(fx_frames["lumi_talk_pulse"][2].image().resize((CELL * S4, CELL * S4), Image.NEAREST),
                        (tx - 14 * S4 - 8, gy - 40 * S4 - lift + 4 * S4))
    for x, lab in ((hx, "hero 20x32"), (wx, "pet_wisp (cold fire #5ab4f0)"), (lx, "Lumi idle (#5ab4f0 + violet halo)"), (tx, "Lumi talking (talk 2, facing left)")):
        d.text((x - 60, gy + 22), lab, fill=SUB, font=F3)
    # ---- 2. full sheet grid
    y1 = y0 + sh + 60
    gh = 4 * (ch + 2) + 40
    d.rectangle([10, y1, W - 10, y1 + gh], fill=PANEL + (255,))
    d.text((20, y1 + 6), "2. Actor sheet lumi.png @3x", fill=TXT, font=F2)
    groups = [(a, A["start"], A["count"]) for a, A in ANIMS.items()]
    colx = {}
    x = left
    for gi, (a, st, cnt) in enumerate(groups):
        for i in range(cnt):
            colx[st + i] = x
            lab = f"{a} {i}" + (" blink" if (a == "idle" and i == 3) else "")
            d.text((x + 2, y1 + 24), lab, fill=SUB, font=F3)
            x += cw + 2
        x += gap
    for fi, facing in enumerate(FACINGS):
        ry = y1 + 38 + fi * (ch + 2)
        d.text((20, ry + ch // 2 - 8), facing, fill=TXT, font=F2)
        for c in range(COLS):
            xx = colx[c]
            d.rectangle([xx, ry, xx + cw - 1, ry + ch - 1], fill=CELLBG + (255,))
            stepped_pool(d, xx + cw // 2, ry + ch - 5, 42, lc, CELLBG, steps=(0.08, 0.16, 0.26))
            out.alpha_composite(sheet.crop((c * FW, fi * FH, (c + 1) * FW, (fi + 1) * FH)).resize((cw, ch), Image.NEAREST), (xx, ry))
    # ---- 3. portraits
    y2 = y1 + gh + 16
    ph = 290
    d.rectangle([10, y2, W - 10, y2 + ph], fill=PANEL + (255,))
    d.text((20, y2 + 6), "3. Dialogue portraits lumi_portrait.png (33x33 bust cells; drawn at 2x = the 66x66 #dlgFace canvas) and, right, "
                         "what the current drawPortrait() crop of the idle-down frame gives", fill=TXT, font=F2)
    for k, (nm, *_r) in enumerate(PORTRAITS):
        xx = 20 + k * 140
        d.rectangle([xx, y2 + 34, xx + 131, y2 + 34 + 131], fill=(60, 52, 70, 255), outline=(110, 96, 90, 255))
        out.alpha_composite(portraits.crop((k * PW, 0, (k + 1) * PW, PW)).resize((PW * 4, PW * 4), Image.NEAREST), (xx - 0, y2 + 34))
        d.text((xx + 4, y2 + 170), nm + " (4x)", fill=SUB, font=F3)
        d.rectangle([xx, y2 + 192, xx + 65, y2 + 257], fill=(60, 52, 70, 255))
        out.alpha_composite(portraits.crop((k * PW, 0, (k + 1) * PW, PW)).resize((PW * 2, PW * 2), Image.NEAREST), (xx, y2 + 192))
        d.text((xx + 70, y2 + 236), "66x66", fill=SUB, font=F3)
    # engine crop emulation: sh = min(fh,22), sy = fy + max(0, fh-34), s = floor(min(66/fw, 66/sh))
    ex0 = 20 + 7 * 140 + 30
    shh, syy = min(FH, 22), max(0, FH - 34)
    s_ = int(min(66 / FW, 66 / shh))
    for k, c in enumerate((0, 12, 14, 16, 18, 20)):
        xx = ex0 + k * 76
        d.rectangle([xx, y2 + 34, xx + 65, y2 + 99], fill=(60, 52, 70, 255))
        crop = sheet.crop((c * FW, syy, c * FW + FW, syy + shh)).resize((FW * s_, shh * s_), Image.NEAREST)
        out.alpha_composite(crop, (xx + (66 - FW * s_) // 2, y2 + 34 + 66 - shh * s_))
        d.text((xx, y2 + 104), ["idle", "talk0", "talk2", "happy", "worried", "surpr."][k], fill=SUB, font=F3)
    d.text((ex0, y2 + 126), f"engine crop: rows {syy}-{syy + shh - 1} of the 40 px frame at {s_}x\n(needs the sheet image, see README)",
           fill=SUB, font=F3)
    # ---- 4. fx + particles + lock-safe
    y3 = y2 + ph + 16
    d.rectangle([10, y3, W - 10, H - 40], fill=PANEL + (255,))
    d.text((20, y3 + 6), "4. lumi_fx.png (spells format, 32 px) @3x, particles @6x, lock-safe sheet", fill=TXT, font=F2)
    yy = y3 + 30
    for nm, frs in fx_frames.items():
        d.text((20, yy + 40), nm, fill=SUB, font=F3)
        for k, F in enumerate(frs):
            xx = 190 + k * 100
            d.rectangle([xx, yy, xx + 95, yy + 95], fill=(14, 13, 22, 255))
            out.alpha_composite(F.image().resize((96, 96), Image.NEAREST), (xx, yy))
        yy += 100
    px0 = 190 + 8 * 100 + 30
    d.text((px0, y3 + 30), "particles (16 px, 4f) @6x", fill=SUB, font=F3)
    for r, nm in enumerate(PROWS):
        d.text((px0, y3 + 50 + r * 70 + 20), nm, fill=SUB, font=F3)
        for f in range(4):
            c = p_im.crop((f * PCELL, r * PCELL, (f + 1) * PCELL, (r + 1) * PCELL)).crop((4, 4, 12, 12)).resize((48, 48), Image.NEAREST)
            xx = px0 + 130 + f * 54
            d.rectangle([xx, y3 + 50 + r * 70, xx + 47, y3 + 97 + r * 70], fill=(14, 13, 22, 255))
            out.alpha_composite(c, (xx, y3 + 50 + r * 70))
    d.text((px0, y3 + 200), "lumi_safe.png (palette only, check-sprite PASS) @3x", fill=SUB, font=F3)
    for k, c in enumerate((0, 12, 14, 16, 18, 20)):
        for j, fi in enumerate((0, 2)):
            xx = px0 + k * 100
            yyy = y3 + 220 + j * 124
            d.rectangle([xx, yyy, xx + cw - 1, yyy + ch - 1], fill=(14, 13, 22, 255))
            out.alpha_composite(safe.crop((c * FW, fi * FH, (c + 1) * FW, (fi + 1) * FH)).resize((cw, ch), Image.NEAREST), (xx, yyy))
    d.text((20, H - 28), "Original pixel art for Hearthmoor (no copied pixels). Glow = emissive NEON / palette pixels + one pooled point light; never bloom.",
           fill=SUB, font=F3)
    out.convert("RGB").save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent))
    ap.add_argument("--hero", default="/workspace/hd2d-suite/games/hearthmoor/areas/plaza/public/art/sprite/actors.png",
                    help="read-only area atlas: the wildcaller, for scale on the contact sheet")
    ap.add_argument("--pets", default="/workspace/hearthmoor-staging/art/pets/pets_neon.png",
                    help="read-only: pet_wisp idle-down frame for scale on the contact sheet")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    hero = wisp = None
    try:
        hj = json.loads(Path(a.hero).with_suffix(".json").read_text())
        r = hj["roles"]["wildcaller"]["row"]
        hero = Image.open(a.hero).convert("RGBA").crop((0, r * 32, 20, r * 32 + 32))
    except Exception:
        pass
    try:
        wisp = Image.open(a.pets).convert("RGBA").crop((0, 0, 20, 32))
    except Exception:
        pass

    neon, roles = build_sheet(SLOTS_NEON)
    safe, _ = build_sheet(SLOTS_SAFE)
    neon.save(out / "lumi.png")
    safe.save(out / "lumi_safe.png")
    base = {"tool": "hearthmoor-art lumi_gen", "biome": "cozy-village", "frame": [FW, FH], "pivot": PIVOT,
            "ground_row": GROUND, "facings": list(FACINGS), "anims": ANIMS, "cols": COLS,
            "size": [neon.width, neon.height], "signature": SIGNATURE, "neon_accents": {k: v for k, v in NEON.items() if k != "neon_blue"},
            "fx": "lumi_fx.json", "particles": "lumi_particles.json", "portrait": "lumi_portrait.json"}
    (out / "lumi.json").write_text(json.dumps({**base, "image": "lumi.png", "image_lock_safe": "lumi_safe.png",
                                               "primary": "lumi.png", "roles": roles}, indent=1))
    (out / "lumi_safe.json").write_text(json.dumps({**base, "image": "lumi_safe.png", "roles": roles}, indent=1))
    # stub for an area actors.json (same pattern as the pets sheet)
    (out / "actors_stub.json").write_text(json.dumps({
        "sheets": {"lumi": {"json": "lumi.json", "image": "lumi.png"}},
        "roles": {"lumi": {"sheet": "lumi", "row": 0, "kind": "creature", "companion": True, "speaks": True, "anims": list(ANIMS)}}},
        indent=1))
    pn, pmeta = build_portraits(SLOTS_NEON)
    ps, _ = build_portraits(SLOTS_SAFE)
    pn.save(out / "lumi_portrait.png")
    ps.save(out / "lumi_portrait_safe.png")
    pn.resize((pn.width * 2, pn.height * 2), Image.NEAREST).save(out / "lumi_portrait_2x.png")
    (out / "lumi_portrait.json").write_text(json.dumps({
        "tool": "hearthmoor-art lumi_gen (portrait)", "image": "lumi_portrait.png", "image_2x": "lumi_portrait_2x.png",
        "image_lock_safe": "lumi_portrait_safe.png", "cell": [PW, PW], "canvas": "#dlgFace 66x66, draw a cell at integer 2x",
        "expressions": pmeta,
        "talk_loop": {"frames": ["talk_a", "talk_b", "talk_a", "neutral"], "fps": 8},
        "blink": {"frame": "blink", "every_s": [2.5, 5.0]},
        "mood_map": {"neutral": "neutral", "happy": "happy", "worried": "worried", "surprised": "surprised"}}, indent=1))
    fx_atlas, fx_meta, fx_frames = build_fx(SLOTS_NEON, "lumi_fx.png")
    fx_atlas.save(out / "lumi_fx.png")
    (out / "lumi_fx.json").write_text(json.dumps(fx_meta, indent=1))
    p_im, p_meta = build_particles(SLOTS_NEON, "lumi_particles.png")
    p_im.save(out / "lumi_particles.png")
    (out / "lumi_particles.json").write_text(json.dumps(p_meta, indent=1))
    (out / "lumi_light.json").write_text(json.dumps({"lumi": {**ROLE["light"], "hover": ROLE["hover"]},
                                                     "compare_pet_wisp": {"color": "#5ab4f0", "intensity": 4.0, "range": 3.2, "lift": 0.75}}, indent=1))
    strips = out / "strips"
    strips.mkdir(exist_ok=True)
    for a_, A in ANIMS.items():
        neon.crop((A["start"] * FW, 0, (A["start"] + A["count"]) * FW, 4 * FH)).save(strips / f"lumi_{a_}.png")
    contact(neon, safe, pn, fx_frames, p_im, hero, wisp, out / "contact_sheet.png")
    print("lumi ->", out)


if __name__ == "__main__":
    main()
