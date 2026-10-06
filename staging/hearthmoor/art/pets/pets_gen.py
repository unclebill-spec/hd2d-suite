#!/usr/bin/env python3
"""Hearthmoor pets: three glowing pet companions (original pixel art, cozy HD-2D style lock).

    python3 pets_gen.py [--out DIR]          # writes everything next to this file by default

  pet_wisp  Wisp kit      a round neon-blue cold-fire wisp with a flame crown and a curling flame tail (hovers)
  pet_moth  Glow-moth     a fuzzy lantern moth with lilac / violet glowing wings and a lit abdomen tip (hovers)
  pet_fox   Lantern-fox   a small orange fox whose bushy tail ends in a flickering red foxfire lantern (walks)

Sprite frames use the actor atlas spec exactly (tools/sprite): 20x32 cells, feet pivot [10, 32], ground row 31,
rows = facings down / up / left / right (right = mirrored left), hard alpha, 1 px ink outline, cozy-village
palette colours only. Columns: idle 0-3 (frame 3 = blink), walk 4-7, follow 8-11 (the catch-up gait).
Hovering pets are drawn standing on the ground row; the runtime lifts the visible quad with `a.lift`
(the shadow + depth stay on the ground, like the hero's jump).

Outputs: pets.png + pets.json (actor-atlas format), pets_neon.png (optional NEON glow-pixel variant),
pet_<id>.png strips, pets_fx.png + pets_fx.json (spells-format 32 px effects: aura sparkles + light pools),
pets_particles.png + pets_particles.json (particles-format 16 px rows + emitter presets), contact_sheet.png.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ------------------------------------------------------------------ palette (games/hearthmoor .../palette/cozy-village/biome.json)
PAL = {
    "ink": "#2a1e1c", "shadow": "#4c3a3e", "plaster_hi": "#f6ecd2", "plaster": "#e6d2ac", "plaster_lo": "#c4a984",
    "timber_hi": "#b07a44", "timber": "#7a4e2e", "timber_lo": "#4a2e20", "stone_hi": "#cfc2a6", "stone": "#9c8e7a",
    "stone_lo": "#6a5e56", "roof_hi": "#d0704a", "roof": "#9a4630", "roof_lo": "#622c24", "grass_hi": "#b2c464",
    "grass": "#72a046", "moss": "#4a7234", "leaf_deep": "#2c4c30", "flower_rose": "#e47c8c", "flower_gold": "#f2c24a",
    "flower_blue": "#6c8cd4", "skin": "#f2c4a0", "skin_lo": "#cc8c6c", "cloth": "#3e5a8c", "sky": "#94c0dc",
    "lamp": "#ffb24a", "white": "#fff8e6",
}
# tools/spells/spells.py NEON: the named glow accents (glowing pixels only)
NEON = {"neon_red": "#e0302a", "neon_red_lo": "#a81c22", "neon_red_hi": "#ff5a4a",
        "neon_violet": "#a45cf0", "neon_violet_hi": "#d4a8ff", "neon_violet_lo": "#6a34b8"}
# Moss-pup's spore glow (new accent for the pets, same rule: glowing pixels only): a toxic lime neon green, clearly apart
# from the palette's grass greens and from the blue / violet / red signature glows
NEON.update({"neon_green": "#5aec3c", "neon_green_hi": "#c4ff8a", "neon_green_lo": "#24a03a"})
ALL = {**PAL, **NEON}


def rgb(h):
    h = ALL.get(h, h).lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


FW, FH = 20, 32
PIVOT = [10, 32]
GROUND = 31
FACINGS = ("down", "up", "left", "right")
ANIMS = {"idle": {"start": 0, "count": 4, "fps": 3, "loop": [0, 1, 2, 1], "blink": 3},
         "walk": {"start": 4, "count": 4, "fps": 8},
         "follow": {"start": 8, "count": 4, "fps": 10, "pets_only": True}}
COLS = 12
DECAL_SQUASH = math.sin(math.radians(36))   # spells.py: ground decals pre-squashed for the 3/4 camera

# glow-colour slots: lock-safe (palette only, pets.png) vs NEON (pets_neon.png: PRIMARY, NEON glow pixels on pets approved by Bill 2026-10-05)
SLOTS_SAFE = {"m_rim": "cloth", "m_body": "flower_blue", "m_hi": "sky", "m_spot": "flower_rose", "m_core": "white",
              "f_rim": "roof", "f_body": "flower_rose", "f_hi": "flower_rose", "f_core": "white",
              "p_cap": "roof_hi", "p_cap_hi": "flower_rose", "p_cap_lo": "roof", "p_spot": "white",
              "p_glow": "grass_hi", "p_glow_hi": "white", "p_glow_lo": "grass"}
SLOTS_NEON = {"m_rim": "neon_violet_lo", "m_body": "neon_violet", "m_hi": "neon_violet_hi", "m_spot": "flower_rose", "m_core": "white",
              "f_rim": "neon_red_lo", "f_body": "neon_red", "f_hi": "neon_red_hi", "f_core": "white",
              "p_cap": "neon_red", "p_cap_hi": "neon_red_hi", "p_cap_lo": "neon_red_lo", "p_spot": "white",
              "p_glow": "neon_green", "p_glow_hi": "neon_green_hi", "p_glow_lo": "neon_green_lo"}


class Spr:
    """20x32 colour-name grid with the actor writer's outline + mirror passes."""

    def __init__(self, slots, w=FW, h=FH):
        self.w, self.h, self.slots = w, h, slots
        self.p = [[None] * w for _ in range(h)]

    def set(self, x, y, c):
        x, y = int(round(x)), int(round(y))
        if c and 0 <= x < self.w and 0 <= y < self.h:
            c = self.slots.get(c, c)
            assert c in ALL, c
            self.p[y][x] = c

    def get(self, x, y):
        return self.p[y][x] if 0 <= x < self.w and 0 <= y < self.h else None

    def ell(self, cx, cy, rx, ry, fn, ang=0.0):
        ca, sa = math.cos(ang), math.sin(ang)
        R = int(max(rx, ry)) + 2
        for y in range(int(cy) - R, int(cy) + R + 1):
            for x in range(int(cx) - R, int(cx) + R + 1):
                dx, dy = x - cx, y - cy
                u, v = dx * ca + dy * sa, -dx * sa + dy * ca
                d = (u / max(rx, .01)) ** 2 + (v / max(ry, .01)) ** 2
                if d <= 1.0:
                    c = fn(x, y, d, u, v) if callable(fn) else fn
                    self.set(x, y, c)

    def outline(self):
        for y in range(self.h):                     # 1 px margin so the outline closes inside the cell
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


def spark(s, x, y, big=False, core="white", arm="sky"):
    s.set(x, y, core)
    if big:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            s.set(x + dx, y + dy, arm)


# ------------------------------------------------------------------ wisp: neon-blue cold-fire will-o'-wisp kit
def draw_wisp(s, face, anim, i):
    blink = anim == "idle" and i == 3
    if anim == "idle":
        b = [0, -1, -1, -1][i]; sway = [0, 1, 0, 1][i]; lean = 0; fl = i
    elif anim == "walk":
        b = [-1, -2, -1, -2][i]; sway = [1, 0, -1, 0][i]; lean = 1; fl = i + 1
    else:  # follow: streams forward, flames and tail swept back, a spark trail
        b = [-2, -3, -2, -3][i]; sway = [1, 2, 1, 2][i]; lean = 2; fl = i + 2
    side = face == "left"
    cx = 9.5 - (lean if side else 0)
    cy = 22.0 + b
    rx = 4.2 + (0.4 if (side and anim == "follow") else 0)
    ry = 3.9 - (0.3 if (side and anim == "follow") else 0)

    # tail: tapers from the orb's base down to the ground row, curling away from the direction of travel
    top = int(cy + ry) - 1
    n = 30 - top
    tip_x = cx
    for k in range(n + 1):
        y = top + k
        t = k / max(1, n)
        if side:
            off = min((1.2 + lean * 0.8) * t * t * 2.6 + (sway * 0.5 * t), 12.0 - cx)   # tip stays near the pivot
        else:
            off = math.sin(t * 2.4 + sway * 0.8) * (1.0 + 0.4 * abs(sway)) * t * 1.4
        w = 2.6 * (1 - t) ** 0.9 + 0.35
        x0 = cx + off
        tip_x = x0
        for x in range(int(round(x0 - w)), int(round(x0 + w)) + 1):
            s.set(x, y, "sky" if (t < 0.5 and abs(x - x0) < w - 0.7) else "flower_blue")
    s.set(round(tip_x), 30, "flower_blue")

    # flame crown: three flickering cold-fire tongues over the orb (centre tallest, swept back when moving sideways)
    hs = [(-2, 2 + (fl % 2)), (0, 4 + (fl % 3 == 1)), (2, 2 + ((fl + 1) % 2))]
    if anim == "follow" and not side:
        hs = [(-2, 3 + (fl % 2)), (0, 6), (2, 3 + ((fl + 1) % 2))]
    base = cy - ry + 1
    for x in range(int(round(cx - 3)), int(round(cx + 3))):
        s.set(x, base, "flower_blue")
    for dx, hgt in hs:
        wob = [0, 1, 0, -1][(fl + dx) % 4]
        for k in range(1, hgt + 1):
            y = base - k
            t = k / hgt
            x = cx - 0.5 + dx + (k * (0.5 + 0.4 * lean) if side else (wob * 0.6 if t > 0.5 else 0))
            c = "white" if k == hgt else "sky"
            s.set(x, y, c)
            if t <= 0.5:
                s.set(x + 1, y, "flower_blue" if k == 1 else "sky")

    # orb: flower_blue body, sky heart, a small white highlight up-left, cloth shade low-right
    def orb(x, y, d, u, v):
        if d < 0.55 and u < 1.0 and v < 1.0:
            return "sky"
        if u + v > rx * 0.75 and d > 0.5:
            return "cloth"
        return "flower_blue"
    s.ell(cx, cy, rx, ry, orb)
    s.set(cx - 2, cy - 2, "white"); s.set(cx - 1, cy - 2, "white"); s.set(cx - 2, cy - 1, "white")

    if face in ("down", "left"):
        ex = [cx - 1.6, cx + 1.4] if face == "down" else [cx - 2.6, cx - 0.4]
        ey = cy + 0.2
        for x in ex:
            if blink:
                s.set(x, ey + 1, "ink")
            else:
                s.set(x, ey, "ink"); s.set(x, ey + 1, "ink")
        if face == "down" and anim == "follow":
            s.set(cx - 0.1, ey + 2, "cloth")          # a little open "wheee" mouth
        if face == "down":
            s.set(cx - 2.6, ey + 2, "flower_rose" if False else "sky")   # cheek glints
    else:  # up: the back of the flame, a dimmer cool crescent
        for (dx, dy) in ((-1, 2), (0, 2), (1, 2), (2, 1), (-2, 1)):
            s.set(cx + dx, cy + dy, "cloth")

    # sparkles in the air around it (outlined by the ink pass, like every glow pixel)
    if anim == "idle":
        pts = [((2, 18), (17, 21)), ((17, 17),), ((3, 22), (16, 15)), ((17, 17),)][i]
        for k, (x, y) in enumerate(pts):
            spark(s, x, y + b, big=(k == 0 and i == 2), arm="sky")
    elif anim == "walk":
        pts = [((16, 19),), ((3, 16), (17, 23)), ((16, 25),), ((3, 20), (17, 16))][i]
        for (x, y) in pts:
            spark(s, x, y, arm="sky")
    else:
        if side:
            trail = [((15, 20), (18, 24)), ((16, 18), (17, 25)), ((15, 22), (18, 18)), ((16, 24), (18, 20))][i]
        else:
            trail = [((3, 15), (16, 14)), ((2, 18), (17, 17)), ((4, 13), (15, 13)), ((2, 16), (17, 15))][i]
        for k, (x, y) in enumerate(trail):
            spark(s, x, y, big=(k == 0), arm="sky")


# ------------------------------------------------------------------ glow-moth: lantern moth with violet-glow wings
def _wing(s, cx, cy, rx, ry, ang, spot=None):
    def f(x, y, d, u, v):
        if d > 0.70:
            return "m_rim"
        if d < 0.30 and spot is None:
            return "m_hi"
        return "m_body" if v > -ry * 0.25 else "m_hi"
    s.ell(cx, cy, rx, ry, f, ang)
    if spot:
        sx, sy = spot
        s.set(sx, sy, "m_spot"); s.set(sx + 1, sy, "m_spot"); s.set(sx, sy + 1, "m_spot"); s.set(sx + 1, sy + 1, "m_spot")
        s.set(sx, sy, "m_core")


def draw_moth(s, face, anim, i):
    # flap states: up / mid / down / glide (wings swept back)
    if anim == "idle":
        st = ["mid", "up", "low", "mid"][i]
    elif anim == "walk":
        st = ["up", "mid", "down", "mid"][i]
    else:
        st = ["glide", "up", "glide", "mid"][i]
    blink = anim == "idle" and i == 3
    if face in ("down", "up"):
        cx = 9.5
        # wings first (body drawn over them)
        fw = {"up": (5.6, 2.3, 15.5, -1.15), "mid": (5.8, 2.6, 19.0, -0.45), "low": (5.6, 2.6, 20.5, -0.2),
              "down": (5.4, 2.5, 22.0, 0.25), "glide": (4.8, 2.2, 20.5, -0.85)}[st]
        rx, ry, wy, ang = fw
        for sgn in (-1, 1):
            wx = cx + sgn * (rx * math.cos(ang) * 0.82 + 0.6)
            a = ang if sgn > 0 else -ang
            a = -a if sgn > 0 else a
            spot_x = int(round(cx + sgn * (rx * 0.9) - (1 if sgn > 0 else 0)))
            spot_y = int(round(wy + (-sgn * 0) + math.sin(-abs(ang)) * rx * 0.55 * 0.9))
            _wing(s, wx, wy + math.sin(-abs(ang)) * rx * 0.6, rx, ry, a * (1 if sgn < 0 else 1) * (-1 if sgn < 0 else 1) * -1,
                  spot=(spot_x, spot_y))
            # hind wing: a smaller lobe under the fore wing
            hy = {"up": 24.5, "mid": 25.0, "low": 25.5, "down": 26.0, "glide": 24.5}[st]
            _wing(s, cx + sgn * 3.2, hy, 2.6, 2.0, sgn * 0.5)
        # body: fuzzy head, thorax, striped abdomen with a glowing lantern tip at the ground row
        s.ell(cx, 22.5, 1.9, 2.0, lambda x, y, d, u, v: "plaster_hi" if u < 0.5 else "plaster")
        for y in range(24, 31):
            w = 1.5 if y < 28 else 1.0
            for x in range(int(round(cx - w)), int(round(cx + w))):
                c = "timber_hi" if (y % 2 == 0 and y < 28) else "plaster"
                if y >= 28:
                    c = "m_core" if y == 29 else "m_hi"
                if y == 30:
                    c = "m_spot"
                s.set(x, y, c)
        if face == "up":
            s.set(9, 24, "timber"); s.set(10, 25, "timber")
        s.ell(cx, 19.8, 1.7, 1.4, lambda x, y, d, u, v: "plaster_hi" if u < 0.3 else "plaster_lo")  # head
        if face == "down" and not blink:
            s.set(8, 20, "ink"); s.set(11, 20, "ink")
        elif face == "down":
            s.set(8, 21, "timber_lo"); s.set(11, 21, "timber_lo")
        # feathery antennae with glowing tips
        tw = 1 if (anim != "idle" or i == 3) else 0
        for sgn in (-1, 1):
            bx = cx + sgn * 0.5
            for k in range(1, 4):
                s.set(bx + sgn * k, 18.5 - k + (tw if k == 3 else 0), "timber_hi")
            s.set(bx + sgn * 4, 14.5 + tw, "m_hi")
            s.set(bx + sgn * 2, 15.5, "timber_hi") if st == "glide" else None
    else:  # left: profile, head left, abdomen hanging down-back to the ground row
        # far wing peeks behind (dimmer rim colour)
        far = {"up": (11.5, 15.5, -1.05), "mid": (13.0, 19.0, -0.25), "low": (13.0, 20.5, 0.05),
               "down": (12.5, 22.5, 0.55), "glide": (13.5, 20.5, -0.35)}[st]
        s.ell(far[0] + 1, far[1] - 1, 4.4, 2.0, "m_rim", far[2])
        # abdomen: chubby, striped, hanging down-back with the lantern tip on the ground row
        def abd(x, y, d, u, v):
            if y >= 29:
                return "m_spot" if y == 30 else "m_core"
            if y == 28:
                return "m_hi"
            return "timber_hi" if (y % 2 == 0) else "plaster"
        s.ell(11.2, 26.0, 1.7, 3.6, abd, -0.35)
        s.set(12, 30, "m_spot"); s.set(12, 29, "m_core")
        # thorax + head (fuzzy)
        s.ell(8.8, 22.6, 2.4, 2.0, lambda x, y, d, u, v: "plaster_hi" if v < 0 else "plaster")
        s.ell(6.0, 21.6, 1.8, 1.7, lambda x, y, d, u, v: "plaster_hi" if u < 0.3 else "plaster_lo")
        if not blink:
            s.set(5, 21, "ink"); s.set(5, 22, "ink")
        else:
            s.set(5, 22, "ink")
        tw = 1 if (anim != "idle" or i == 3) else 0
        for (x, y) in ((5, 19), (4, 18), (3, 17)):
            s.set(x, y + (tw if y == 17 else 0), "timber_hi")
        s.set(2, 17 + tw, "m_hi"); s.set(3, 16 + tw, "timber_hi") if False else None
        s.set(6, 19, "timber_hi"); s.set(6, 18, "timber_hi"); s.set(7, 17, "m_hi")
        # near wing over the body
        near = {"up": (10.5, 15.5, -1.15, (10, 14)), "mid": (13.0, 20.0, -0.2, (13, 19)), "low": (12.5, 21.5, 0.15, (12, 21)),
                "down": (11.5, 24.0, 0.75, (11, 25)), "glide": (13.5, 21.0, -0.3, (14, 20))}[st]
        _wing(s, near[0], near[1], 4.8, 2.3, near[2], spot=near[3])
        s.ell(10.8, 26.2 if st != "down" else 27.0, 2.2, 1.6, "m_body", 0.6)     # hind wing lobe
    # violet dust in the air (glow pixels, outlined)
    pts = {"idle": [((3, 24),), ((16, 14),), ((2, 18), (17, 26)), ((16, 14),)],
           "walk": [((17, 22),), ((2, 26), (17, 16)), ((16, 25),), ((3, 14),)],
           "follow": [((16, 24), (18, 20)), ((17, 23),), ((16, 21), (18, 25)), ((18, 22),)]}[anim][i]
    for k, (x, y) in enumerate(pts):
        if face == "left" or anim != "follow" or True:
            spark(s, x, y, big=(anim == "follow" and k == 0), core="m_core", arm="m_hi")


# ------------------------------------------------------------------ lantern-fox: orange fox, red foxfire lantern tail
def flame(s, x, y, i, big=True):
    """a small foxfire flame with its base at (x, y): rim / body / white heart, the tongue flickers by frame"""
    h = [5, 6, 5, 7][i % 4]
    lean = [0, 1, 0, -1][i % 4]
    for k in range(h):
        yy = y - k
        t = k / h
        w = 1.5 if t < 0.35 else 1.0 if t < 0.7 else 0.4
        xc = x + lean * t * t * 1.6
        for xx in range(int(round(xc - w)), int(round(xc + w)) + 1):
            edge = abs(xx - xc) > w - 0.6
            if k == 0:
                c = "f_rim"
            elif t < 0.6 and not edge:
                c = "f_core"
            elif t >= 0.7:
                c = "f_hi"
            else:
                c = "f_body"
            s.set(xx, yy, c)
    if i % 2:
        s.set(x + lean * 2 + 1, y - h - 1, "f_hi")          # a spark licking off the tip


def draw_fox(s, face, anim, i):
    blink = anim == "idle" and i == 3
    run = anim == "follow"
    if anim == "idle":
        bob = [0, 0, 1, 0][i]; legs = [(0, 0, 0, 0)] * 4; tsw = [0, 1, 0, 1][i]
        legs = legs[i]
    elif anim == "walk":
        bob = [0, -1, 0, -1][i]; tsw = [0, 1, 0, -1][i]
        legs = [(1, 0, 0, 1), (0, 0, 0, 0), (0, 1, 1, 0), (0, 0, 0, 0)][i]
    else:
        bob = [0, -1, -1, 0][i]; tsw = [1, 2, 1, 0][i]
        legs = [(2, 0, 0, 2), (1, 0, 0, 1), (0, 2, 2, 0), (0, 1, 1, 0)][i]
    fur, fur_d, fur_dd, cream, sock = "roof_hi", "roof", "roof_lo", "plaster_hi", "timber_lo"
    if face == "left":
        stretch = 1 if run else 0
        # tail (behind the body): bushy, rising up and back, foxfire at the tip
        if run:
            pts = [(14.8, 23.4), (15.8, 21.9), (16.3, 20.3 - tsw * 0.3)]
            for k, (x, y) in enumerate(pts):
                s.ell(x, y + bob, 1.7 - k * 0.15, 1.5, lambda X, Y, d, u, v: fur if u < 0.4 else fur_d)
            tip = (16.4, 18.8 + bob - tsw * 0.3)
        else:
            pts = [(15.0, 24.0), (16.2, 22.0), (16.6, 19.8), (16.2 + tsw * 0.4, 17.8)]
            for k, (x, y) in enumerate(pts):
                s.ell(x, y + bob, 1.9 - k * 0.15, 1.6, lambda X, Y, d, u, v: fur if u < 0.4 else fur_d)
            tip = (16.2 + tsw * 0.4, 16.2 + bob)
        s.ell(tip[0], tip[1], 1.3, 1.1, cream)
        flame(s, round(tip[0]), round(tip[1]) - 1, i)
        # legs (far pair darker), lifts by frame
        lf, lb, rf, rb = legs
        for (x, lift, c, dx) in ((7.5 - stretch, lf, sock, -stretch), (13.0 + stretch, lb, sock, stretch),
                                 (9.0 - stretch, rf, "shadow", -stretch), (14.3 + stretch, rb, "shadow", stretch)):
            for y in range(26 + bob, 31 - lift):
                s.set(x + (dx if y > 28 - lift else 0), y, c)
        # body
        s.ell(11.0, 24.6 + bob, 4.6 + stretch, 2.4 - stretch * 0.3,
              lambda X, Y, d, u, v: fur if v < 0.2 else fur_d)
        for (x, y) in ((7, 24), (7, 25), (8, 25), (8, 26)):
            s.set(x - stretch, y + bob, cream)
        # head
        hx, hy = 5.6 - stretch, 21.2 + bob + (1 if run else 0)
        s.ell(hx, hy, 2.6, 2.2, lambda X, Y, d, u, v: fur if v < 0.6 else cream)
        for k in range(3):                                   # snout
            s.set(hx - 2.6 - k * 0.0, hy + 0.8, cream if k else cream)
        s.set(hx - 3.4, hy + 0.9, cream)
        s.set(hx - 4.1, hy + 0.9, "ink")                     # nose
        s.set(hx - 3.2, hy + 1.8, cream)
        # ears (laid back when running)
        if run:
            for (x, y, c) in ((hx + 1.5, hy - 2.2, fur), (hx + 2.5, hy - 2.6, fur_d), (hx + 3.4, hy - 2.8, fur_dd)):
                s.set(x, y, c)
        else:
            for (x, y, c) in ((hx - 0.4, hy - 2.4, fur), (hx - 0.4, hy - 3.4, fur), (hx - 0.4, hy - 4.3, fur_dd),
                              (hx + 0.6, hy - 2.4, sock), (hx + 0.6, hy - 3.4, fur_d),
                              (hx + 1.6, hy - 2.4, fur_d), (hx + 1.6, hy - 3.3, fur_dd)):
                s.set(x, y, c)
        if blink:
            s.set(hx - 1.2, hy, "timber_lo")
        else:
            s.set(hx - 1.2, hy - 0.4, "ink"); s.set(hx - 1.2, hy + 0.5, "ink")
    elif face == "down":
        # tail rising behind on the right, foxfire tip above the shoulder
        sx = [0, 1, 0, 1][i] if not run else [1, 0, 1, 0][i]
        pts = [(13.8, 26.0), (15.0, 23.8), (15.4 + sx * 0.4, 21.5), (15.0 + sx * 0.6, 19.6)] if not run else \
              [(13.6, 25.5), (15.0, 23.6), (15.8 + sx * 0.5, 21.6)]
        for k, (x, y) in enumerate(pts):
            s.ell(x, y + bob, 1.9 - k * 0.15, 1.6, lambda X, Y, d, u, v: fur if u < 0.3 else fur_d)
        tip = (pts[-1][0], pts[-1][1] - 1.6 + bob)
        s.ell(tip[0], tip[1], 1.3, 1.0, cream)
        flame(s, round(tip[0]), round(tip[1]) - 1, i)
        # legs: front pair, hind paws peeking out
        lf, lb, rf, rb = legs
        for (x, lift) in ((7.6, lf), (11.4, rf)):
            for y in range(25, 31 - lift):
                for dx in (0, 1):
                    s.set(x + dx, y, sock if y >= 28 - lift else fur_d)
        for (x, lift) in ((6.0, lb), (13.4, rb)):
            for y in range(28, 31 - lift):
                s.set(x, y, sock)
        # body + chest bib
        s.ell(9.5, 25.6 + bob, 3.8, 2.6, lambda X, Y, d, u, v: fur if u < 1.5 else fur_d)
        s.ell(9.5, 25.8 + bob, 1.6, 2.0, cream)
        # head
        hy = 20.4 + bob + (1 if run else 0)
        s.ell(9.5, hy, 3.9, 2.9, lambda X, Y, d, u, v: fur if (v < 0.6 or abs(u) > 2.2) else cream)
        for (x, y) in ((8, 22), (9, 22), (10, 22), (11, 22), (9, 23), (10, 23)):
            s.set(x, y + bob + (1 if run else 0), cream)
        s.set(9, hy + 1.4, "ink"); s.set(10, hy + 1.4, "ink")          # nose
        er = 2 if run else 0
        for sgn in (-1, 1):
            ex = 9.5 + sgn * 2.4
            s.set(ex, hy - 3 + er * 0.5, fur); s.set(ex + sgn * 0.6, hy - 3.9 + er, fur_dd if not run else fur)
            s.set(ex - sgn * 0.6, hy - 3 + er * 0.5, sock)
            if not run:
                s.set(ex + sgn * 0.3, hy - 4.8, fur_dd)
        if blink:
            s.set(7.6, hy + 0.2, "timber_lo"); s.set(11.4, hy + 0.2, "timber_lo")
        else:
            for x in (7.6, 11.4):
                s.set(x, hy - 0.4, "ink"); s.set(x, hy + 0.4, "ink")
    else:  # up: back view, tail curving up to the left with the lantern tip
        sx = [0, 1, 0, -1][i]
        lf, lb, rf, rb = legs
        for (x, lift) in ((7.4, lb), (11.6, rb)):
            for y in range(26, 31 - lift):
                for dx in (0, 1):
                    s.set(x + dx, y, sock if y >= 28 - lift else fur_d)
        s.ell(9.5, 25.2 + bob, 3.9, 2.8, lambda X, Y, d, u, v: fur if u < 1.2 else fur_d)
        for y in range(23, 27):
            s.set(9.5, y + bob, fur_d)                                    # spine shading
        hy = 20.4 + bob
        s.ell(9.5, hy, 3.6, 2.7, lambda X, Y, d, u, v: fur if u < 1.2 else fur_d)
        for sgn in (-1, 1):                                               # pointed ears, dark backs and tips
            ex = 9.5 + sgn * 2.2
            for (dx, dy, c) in ((-0.5, -2.6, fur_d), (0.5, -2.6, fur_d), (-0.5, -3.6, fur_d), (0.5, -3.6, fur_dd), (sgn * 0.5, -4.6, fur_dd)):
                s.set(ex + dx, hy + dy, c)
        s.set(7, hy + 1.6, fur_d); s.set(12, hy + 1.6, fur_d)              # cheek ruff
        # tail (in front, toward the camera) sweeping up to the left
        pts = [(10.0, 28.0), (8.0, 27.6), (6.0, 26.0), (4.8 + sx * 0.3, 23.6), (4.4 + sx * 0.5, 21.4)] if not run else \
              [(10.0, 28.0), (8.4, 28.2), (6.4, 27.2), (4.8 + sx * 0.4, 25.4)]
        for k, (x, y) in enumerate(pts):
            s.ell(x, y + (bob if k > 1 else 0), 1.7, 1.4, lambda X, Y, d, u, v: fur if u < 0.5 else fur_d)
        tip = (pts[-1][0], pts[-1][1] - 1.5 + bob)
        s.ell(tip[0], tip[1], 1.2, 1.0, cream)
        flame(s, round(tip[0]), round(tip[1]) - 1, i)
    # foxfire embers in the air (glow pixels, outlined)
    pts = {"idle": [((17, 14),), ((2, 18),), ((17, 11), (3, 22)), ((2, 18),)],
           "walk": [((18, 13),), ((2, 16),), ((17, 10),), ((3, 20),)],
           "follow": [((18, 16), (16, 12)), ((18, 11),), ((17, 14), (18, 9)), ((16, 10),)]}[anim][i]
    for k, (x, y) in enumerate(pts):
        if face == "up":
            x = 19 - x
        spark(s, x, y, big=(anim == "follow" and k == 0), core="f_core", arm="f_hi")


# ------------------------------------------------------------------ moss-pup: mossy pup with a glowing red toadstool cap
def toadcap(s, cx, cy, rx, ry, spots, stem=True):
    """a red toadstool dome (glow pixels) with crisp white spots and a pale stem under it"""
    def f(x, y, d, u, v):
        if v > ry * 0.45:
            return "p_cap_lo"
        return "p_cap_hi" if (u < -rx * 0.35 and v < 0) else "p_cap"
    s.ell(cx, cy, rx, ry, f)
    for (dx, dy) in spots:
        s.set(cx + dx, cy + dy, "p_spot")
    if stem:
        s.set(cx - 0.5, cy + ry + 0.6, "plaster_hi"); s.set(cx + 0.5, cy + ry + 0.6, "plaster")


def moss_dots(s, pts):
    for k, (x, y) in enumerate(pts):
        s.set(x, y, "p_glow_hi" if k % 3 == 0 else "p_glow")


def draw_mosspup(s, face, anim, i):
    blink = anim == "idle" and i == 3
    run = anim == "follow"
    if anim == "idle":
        bob = [0, 0, 1, 0][i]; wag = [0, 1, 0, 1][i]; legs = (0, 0, 0, 0); hop = 0
    elif anim == "walk":
        bob = [0, -1, 0, -1][i]; wag = [1, 0, 1, 0][i]
        legs = [(1, 0, 0, 1), (0, 0, 0, 0), (0, 1, 1, 0), (0, 0, 0, 0)][i]; hop = 0
    else:   # follow: a bouncy bound, ears flying, the cap bobbing a beat behind
        bob = [0, -1, -2, -1][i]; wag = [1, 2, 1, 0][i]
        legs = [(2, 0, 0, 2), (1, 0, 0, 1), (0, 2, 2, 0), (0, 1, 1, 0)][i]; hop = [0, 1, 0, -1][i]
    fur, fur_hi, fur_dk = "grass", "grass_hi", "moss"
    deep, muzzle, paw = "leaf_deep", "plaster", "timber"

    def furf(lit_left=True):
        return lambda X, Y, d, u, v: fur_hi if (u < -0.8 and v < 0) else (fur_dk if (u > 1.2 or v > 1.2) else fur)
    if face == "left":
        st = 1 if run else 0
        # stubby tail with a glowing moss tuft, wagging
        ty = 23.6 + bob - wag * 0.6
        s.set(15.4 + st, ty + 0.6, fur_dk); s.set(16.2 + st, ty, fur); s.set(16.8 + st, ty - 0.8, "p_glow")
        s.set(17.2 + st, ty - 1.6, "p_glow_hi")
        # legs: far pair darker, short and chunky with brown paws
        lf, lb, rf, rb = legs
        for (x, lift, c) in ((8.0 - st, lf, fur_dk), (13.5 + st, lb, fur_dk), (9.4 - st, rf, deep), (14.8 + st, rb, deep)):
            for y in range(27 + bob, 31 - lift):
                s.set(x, y, paw if y >= 29 - lift else c)
        # body: a round mossy loaf
        s.ell(11.4, 25.4 + bob, 4.4 + st, 2.6 - st * 0.3, furf())
        s.set(9.0, 27 + bob, fur_hi)
        moss_dots(s, [(10, 23 + bob), (12, 22.8 + bob), (14, 23.4 + bob), (11, 24 + bob), (13.4, 24.6 + bob)])
        toadcap(s, 13.0 + st, 21.2 + bob + hop * 0.3, 1.6, 1.0, [(0, -0.4)], stem=True)     # a tiny toadstool on its back
        # head: big and round, muzzle forward
        hx, hy = 6.2 - st, 21.2 + bob + (1 if run else 0)
        s.ell(hx, hy, 3.3, 2.9, furf())
        s.ell(hx - 2.4, hy + 1.2, 1.5, 1.1, muzzle)
        s.set(hx - 3.7, hy + 0.6, "ink")                       # nose
        s.set(hx - 2.0, hy + 2.2, "plaster_lo")
        # floppy leaf ear (flies back when bounding)
        if run:
            for (dx, dy) in ((1.6, -1.8), (2.6, -2.2 - hop * 0.5), (3.5, -2.0 - hop * 0.5), (2.4, -1.2)):
                s.set(hx + dx, hy + dy, deep)
        else:
            for (dx, dy) in ((1.2, -1.2), (1.8, -0.4), (1.8, 0.6), (2.2, 1.4), (1.2, 0.2)):
                s.set(hx + dx, hy + dy, deep)
        if blink:
            s.set(hx - 1.0, hy + 0.2, "ink")
        else:
            s.set(hx - 1.0, hy - 0.6, "white"); s.set(hx - 1.0, hy + 0.4, "ink"); s.set(hx - 0.1, hy + 0.4, "ink"); s.set(hx - 0.1, hy - 0.6, "ink")
        # the toadstool cap worn on its head (tilted forward), stem hidden in the moss
        toadcap(s, hx + 0.6, hy - 3.6 - (hop if run else 0) * 0.6, 3.4, 1.8, [(-1.6, -0.6), (0.8, -0.9), (2.2, 0.2), (-0.4, 0.5)], stem=False)
        moss_dots(s, [(hx + 2.2, hy - 1.6), (hx - 1.8, hy - 2.2)])
    elif face == "down":
        lf, lb, rf, rb = legs
        # tail wag peeking out behind on the right
        s.set(14.4, 25 + bob - wag, fur); s.set(15.0, 24 + bob - wag, "p_glow"); s.set(15.4, 23.2 + bob - wag, "p_glow_hi")
        for (x, lift) in ((7.0, lf), (11.0, rf)):              # front legs
            for y in range(26, 31 - lift):
                for dx in (0, 1):
                    s.set(x + dx, y, paw if y >= 29 - lift else fur_dk)
        for (x, lift) in ((5.6, lb), (13.4, rb)):              # hind paws peeking out
            for y in range(28, 31 - lift):
                s.set(x, y, paw if y >= 29 - lift else fur_dk)
        s.ell(9.5, 26.4 + bob, 3.8, 2.3, lambda X, Y, d, u, v: fur if u < -1.0 else fur_dk)   # body a shade darker than the head
        hy = 21.0 + bob + (1 if run else 0)
        s.ell(9.5, hy, 4.4, 3.0, furf())
        for x in (7, 8, 11, 12):
            s.set(x, hy + 3.0, deep)                           # chin shadow separates head and body
        for (x, y) in ((8, 1), (9, 1), (10, 1), (11, 1), (8, 2), (9, 2), (10, 2), (11, 2), (9, 3), (10, 3)):
            s.set(x, hy + y, muzzle)                           # a round cream snout under the eyes
        s.set(9, hy + 1, "ink"); s.set(10, hy + 1, "ink")       # nose
        s.set(9, hy + 2.6, "plaster_lo"); s.set(10, hy + 2.6, "plaster_lo") if False else None
        s.set(11, hy + 2, "plaster_lo")
        er = (-1 if run else 0)
        for sgn in (-1, 1):                                    # floppy leaf ears hanging either side, glowing moss tips
            ex = 9.5 + sgn * 4.4
            for dy in ((-2, -1, 0, 1, 2) if not run else (-3, -2, -1)):
                s.set(ex, hy + dy + er, deep)
                if dy > -2 or run:
                    s.set(ex + sgn, hy + dy + er + (0 if not run else -1), deep)
            s.set(ex + (sgn if not run else sgn * 2), hy + (3 if not run else -3) + er, "p_glow")
        if blink:
            for ex in (6.6, 7.4, 11.6, 12.4):
                s.set(ex, hy + 0.0, "ink")
        else:
            for ex in (6.6, 11.6):
                s.set(ex, hy - 1.0, "white"); s.set(ex + 0.9, hy - 1.0, "ink"); s.set(ex, hy, "ink"); s.set(ex + 0.9, hy, "ink")
        toadcap(s, 9.5 + 0.6, hy - 3.6 - (hop if run else 0) * 0.6, 4.1, 1.8, [(-2.4, -0.3), (-0.4, -1.0), (1.6, -0.5), (3.0, 0.4), (0.6, 0.5)], stem=False)
        moss_dots(s, [(7.0, 25.6 + bob), (12.2, 25.8 + bob), (9.5, 27.4 + bob), (11, 27 + bob)])
    else:  # up: back of the pup, cap from behind, the little back toadstool and its glowing moss trail
        lf, lb, rf, rb = legs
        for (x, lift) in ((7.0, lb), (11.0, rb)):
            for y in range(27, 31 - lift):
                for dx in (0, 1):
                    s.set(x + dx, y, paw if y >= 29 - lift else fur_dk)
        s.ell(9.5, 25.6 + bob, 4.0, 2.7, furf())
        moss_dots(s, [(8, 24 + bob), (10, 23.6 + bob), (11.6, 24.6 + bob), (9, 25.6 + bob), (7.4, 26.2 + bob)])
        hy = 20.6 + bob
        s.ell(9.5, hy, 4.0, 3.0, furf())
        er = (-1 if run else 0)
        for sgn in (-1, 1):
            ex = 9.5 + sgn * 4.2
            for dy in ((-1, 0, 1, 2) if not run else (-2, -1, 0)):
                s.set(ex, hy + dy + er, deep)
        toadcap(s, 9.5 - 0.4, hy - 3.2 - (hop if run else 0) * 0.6, 4.3, 1.9, [(-2.0, -0.6), (0.4, -1.1), (2.4, -0.2), (-0.8, 0.5)], stem=False)
        toadcap(s, 11.2, 22.6 + bob, 1.5, 1.0, [(0, -0.4)], stem=True)
        # tail toward the camera: a glowing moss tuft at the bottom centre, wagging side to side
        s.set(9.5 + wag * 0.6 - 0.3, 28.4 + bob, fur); s.set(9.5 + wag * 0.8, 29.2 + bob, "p_glow"); s.set(9.5 + wag, 29.0 + bob, "p_glow_hi")
    # floating spores (glow pixels, outlined)
    pts = {"idle": [((16, 15),), ((3, 19),), ((17, 12), (2, 23)), ((3, 19),)],
           "walk": [((17, 14),), ((2, 17),), ((17, 11),), ((3, 21),)],
           "follow": [((17, 17), (15, 12)), ((18, 13),), ((17, 15), (18, 10)), ((15, 11),)]}[anim][i]
    for k, (x, y) in enumerate(pts):
        if face == "up":
            x = 19 - x
        spark(s, x, y, big=(anim == "follow" and k == 0), core="p_glow_hi", arm="p_glow")


PETS = {
    "pet_wisp": dict(draw=draw_wisp, name="Wisp kit",
                     desc="Wisp kit: a round neon-blue cold-fire wisp with a flickering flame crown, a curling flame tail and "
                          "little cloth-blue eyes; hovers at the hero's hip (neon pulse, night light, slow mana regen)",
                     hover={"lift": 0.5, "bob": 0.06, "hz": 0.8},
                     light={"color": "#5ab4f0", "intensity": 4.0, "range": 3.2, "lift": 0.75, "fadeIn": 0.4,
                            "pulse": {"min": 0.75, "max": 1.15, "hz": 0.9, "shape": "sine"}},
                     aura="pet_aura_wisp", pool="pet_pool_wisp", particles="pet_wisp_spark", speed=2.4,
                     look="neon blue cold fire (palette sky / flower_blue / cloth / white; the cold-fire LANTERN hex for the light)"),
    "pet_moth": dict(draw=draw_moth, name="Glow-moth",
                     desc="Glow-moth (lantern moth): fuzzy cream body, feathery antennae with glowing tips, lilac-blue wings with "
                          "rose eyespots and white glints, a lit lantern tip on the abdomen; hovers at shoulder height "
                          "(lights caves, reveals hidden doors)",
                     hover={"lift": 0.75, "bob": 0.08, "hz": 0.6},
                     light={"color": "#a45cf0", "intensity": 5.0, "range": 3.8, "lift": 0.95, "fadeIn": 0.5,
                            "pulse": {"min": 0.85, "max": 1.05, "hz": 0.5, "shape": "sine"}},
                     aura="pet_aura_moth", pool="pet_pool_moth", particles="pet_moth_dust", speed=2.4,
                     look="violet neon (sprite: palette lilac-blue so check-sprite passes; NEON violet in the light, pool, aura; pets_neon.png has violet wings)"),
    "pet_fox": dict(draw=draw_fox, name="Lantern-fox",
                    desc="Lantern-fox (rift fox): a small orange fox with a cream bib and muzzle, dark socks, big ears and a bushy "
                         "tail that ends in a flickering red foxfire lantern; trots on the ground (senses portals, opens small secret portals)",
                    hover={"lift": 0.0, "bob": 0.0, "hz": 0.0},
                    light={"color": "#ff4a3a", "intensity": 3.5, "range": 2.8, "lift": 0.6, "fadeIn": 0.4,
                           "pulse": {"min": 0.85, "max": 1.1, "hz": 5.0, "shape": "flicker"}},
                    aura="pet_aura_fox", pool="pet_pool_fox", particles="pet_fox_ember", speed=2.4,
                    look="red neon foxfire (sprite: palette rose / roof / white flame; NEON red in the light, pool, aura; pets_neon.png has a neon-red flame)"),
    "pet_mosspup": dict(draw=draw_mosspup, name="Moss-pup",
                        desc="Moss-pup (Mossbrook / Stray Den): a round little pup of living moss with floppy leaf ears, a cream "
                             "muzzle, brown paws, a glowing red toadstool cap with white spots on its head, a tiny toadstool and "
                             "glowing moss dots on its back and a glowing moss-tuft tail; trots on the ground (sniffs out herbs, "
                             "mushrooms and hidden springs)",
                        hover={"lift": 0.0, "bob": 0.0, "hz": 0.0},
                        light={"color": "#5aec3c", "intensity": 3.5, "range": 3.0, "lift": 0.55, "fadeIn": 0.5,
                               "pulse": {"min": 0.8, "max": 1.1, "hz": 0.7, "shape": "sine"}},
                        aura="pet_aura_mosspup", pool="pet_pool_mosspup", particles="pet_mosspup_spore", speed=2.4,
                        look="toxic-lime neon green spores + neon-red toadstool cap with white spots (pets_neon.png); pets.png keeps them in grass / roof / white"),
}


def frame(pet, facing, anim, i, slots):
    s = Spr(slots)
    face = "left" if facing == "right" else facing
    PETS[pet]["draw"](s, face, anim, i)
    s.outline()
    return s.mirror() if facing == "right" else s


def build_sheet(slots):
    im = Image.new("RGBA", (FW * COLS, FH * 4 * len(PETS)), (0, 0, 0, 0))
    roles = {}
    for pi, pet in enumerate(PETS):
        frames = []
        for fi, facing in enumerate(FACINGS):
            for anim in ANIMS:
                for i in range(4):
                    col = ANIMS[anim]["start"] + i
                    x, y = col * FW, (pi * 4 + fi) * FH
                    im.paste(frame(pet, facing, anim, i, slots).image(), (x, y))
                    frames.append({"name": f"{pet}_{facing}_{anim}{i}", "facing": facing, "anim": anim, "i": i,
                                   "x": x, "y": y, "w": FW, "h": FH, "pivot": [x + PIVOT[0], y + PIVOT[1]]})
        P = PETS[pet]
        roles[pet] = {"row": pi * 4, "kind": "creature", "pet": True, "name": P["name"], "desc": P["desc"],
                      "size_bounds": [[8, 20], [8, 28]], "caster": False, "anims": list(ANIMS), "frames": frames,
                      "petfx": {"hover": P["hover"], "light": P["light"], "aura": P["aura"], "pool": P["pool"],
                                "particles": P["particles"], "speed": P["speed"], "look": P["look"]}}
    return im, roles


# ------------------------------------------------------------------ 32 px effects (tools/spells format): aura sparkles + pools
CELL = 32


class Cell:
    def __init__(self):
        self.p = [[None] * CELL for _ in range(CELL)]

    def set(self, x, y, c):
        x, y = int(round(x)), int(round(y))
        if c and 0 <= x < CELL and 0 <= y < CELL:
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


def aura_orbit(seed, cols, n=8, rx=10.0, ry=6.0, cy=18.0, rise=0.0, fall=0.0, extra=6):
    """sparkles orbiting the pet on a tilted ring plus free motes; twinkle cycle off / dot / star / dot"""
    R = random.Random(seed)
    hi, mid, lo = cols
    ph = [k * math.tau / 6 + R.random() * 0.6 for k in range(6)]
    motes = [(6 + R.random() * 20, 8 + R.random() * 20, R.randrange(8), R.choice([hi, mid, "white"])) for _ in range(extra)]
    out = []
    for f in range(n):
        F = Cell()
        for k, a0 in enumerate(ph):
            a = a0 + f * math.tau / n * (1 if k % 2 == 0 else -0.7)
            x, y = 16 + math.cos(a) * rx, cy + math.sin(a) * ry
            b = (f + k * 2) % 8
            if b in (1, 5):
                F.set(x, y, mid)
            elif b == 2:
                F.star(x, y, 1, "white", hi)
            elif b == 3:
                F.star(x, y, 2, "white", hi, tip=lo)
            elif b in (4, 6):
                F.set(x, y, hi)
        for (x, y, p, c) in motes:
            b = (f + p) % 8
            yy = y - b * rise + b * fall
            if b in (1, 4):
                F.set(x, yy, c)
            elif b == 2:
                F.star(x, yy, 1, "white", c if c != "white" else hi)
            elif b == 3:
                F.set(x, yy, lo)
        out.append(F)
    return out


def ember_rise(seed, cols, n=8):
    R = random.Random(seed)
    hi, mid, lo = cols
    em = [(8 + R.random() * 16, 18 + R.random() * 12, R.randrange(8), R.choice([0, 1, 1])) for _ in range(13)]
    out = []
    for f in range(n):
        F = Cell()
        for (x, y, p, kind) in em:
            b = (f + p) % 8
            yy = y - b * 1.6
            xx = x + math.sin((b + p) * 0.9) * 1.2
            if b == 0:
                continue
            if kind and b in (2, 3):                     # a two-pixel foxfire tongue: neon body, white tip
                F.set(xx, yy, mid); F.set(xx, yy - 1, "white")
            elif b in (1, 4):
                F.set(xx, yy, hi)
            elif b == 5:
                F.star(xx, yy, 1, "white", hi)
            elif b in (6, 7):
                F.set(xx, yy, lo if b == 7 else mid)
        out.append(F)
    return out


def pet_pool(seed, cols, rx0=10.5, n=6):
    """a pet's soft ground pool: a sparse dithered disc densest at the heart (pre-squashed), the edge breathing"""
    R = random.Random(seed)
    jit = [[R.random() for _ in range(CELL)] for _ in range(CELL)]
    hi, mid, lo = cols
    out = []
    for f in range(n):
        F = Cell()
        fl = [1.0, 0.95, 0.9, 0.88, 0.92, 0.97][f]
        rx = rx0 * fl
        for y in range(CELL):
            for x in range(CELL):
                d = math.hypot(x - 16, (y - 16) / DECAL_SQUASH) / rx
                if d > 1:
                    continue
                dens = 0.85 * (1 - d) ** 1.1 + 0.08
                if (x + y + f) % 2 == 0 and jit[y][x] < dens:
                    c = "white" if (d < 0.18 and (x + 2 * y + f) % 3 == 0) else hi if d < 0.4 else mid if d < 0.72 else lo
                    F.set(x, y, c)
        for k in range(int(rx * 6)):                                   # a dotted rim that turns slowly
            if k % 4:
                continue
            a = f * 0.21 + k / (rx * 6) * math.tau
            F.set(16 + math.cos(a) * rx, 16 + math.sin(a) * rx * DECAL_SQUASH, lo)
        out.append(F)
    return out


BLUE = ("sky", "flower_blue", "cloth")
VIOLET = ("neon_violet_hi", "neon_violet", "neon_violet_lo")
RED = ("neon_red_hi", "neon_red", "neon_red_lo")
GREEN = ("neon_green_hi", "neon_green", "neon_green_lo")


def spore_drift(seed, cols, n=8):
    """glowing spores puffing off the moss-pup's toadstools: round motes rising slowly on a wobble, a few 2x2 puffs,
    the odd red-cap fleck; palette / NEON pixels, no blur"""
    R = random.Random(seed)
    hi, mid, lo = cols
    sp = [(7 + R.random() * 18, 16 + R.random() * 14, R.randrange(8), R.choice([0, 0, 1, 2])) for _ in range(12)]
    out = []
    for f in range(n):
        F = Cell()
        for (x, y, p, kind) in sp:
            b = (f + p) % 8
            if b == 0:
                continue
            yy = y - b * 1.1
            xx = x + math.sin((b + p) * 0.8) * 1.4
            if kind == 1 and b in (2, 3, 4):                # a round 2x2 spore puff
                F.set(xx, yy, hi); F.set(xx + 1, yy, mid); F.set(xx, yy + 1, mid); F.set(xx + 1, yy + 1, lo)
            elif kind == 2 and b == 3:
                F.star(xx, yy, 1, "white", hi)
            elif b in (1, 2, 5):
                F.set(xx, yy, mid if b != 2 else hi)
            elif b in (6, 7):
                F.set(xx, yy, lo)
            elif b in (3, 4):
                F.set(xx, yy, hi if (p + b) % 5 else "neon_red_hi")
        out.append(F)
    return out
FX = {
    "pet_aura_wisp": dict(fn=lambda: aura_orbit(11, BLUE, rx=9.5, ry=5.5, cy=19, rise=1.0, extra=10), kind="billboard", fps=10,
                          pivot=[16, 31], lift=0.0, follow_lift="hover", glow=True,
                          desc="cold-fire sparkles orbiting the wisp + blue motes rising (palette only)"),
    "pet_aura_moth": dict(fn=lambda: aura_orbit(23, VIOLET, rx=10.5, ry=5.0, cy=17, fall=0.9, extra=12), kind="billboard", fps=8,
                          pivot=[16, 31], lift=0.0, follow_lift="hover", glow=True,
                          desc="violet neon wing-dust twinkling and drifting down around the moth (NEON violet)"),
    "pet_aura_fox": dict(fn=lambda: ember_rise(37, RED), kind="billboard", fps=10, pivot=[16, 31], lift=0.0, glow=True,
                         desc="red neon foxfire embers rising off the lantern tail (NEON red)"),
    "pet_pool_wisp": dict(fn=lambda: pet_pool(5, BLUE, 10.5), kind="decal", fps=6, pivot=[16, 16], lift=0.02, glow=True,
                          desc="soft cold-fire ground pool under the wisp (palette sky / flower_blue / cloth)"),
    "pet_pool_moth": dict(fn=lambda: pet_pool(6, VIOLET, 12.5), kind="decal", fps=5, pivot=[16, 16], lift=0.02, glow=True,
                          desc="soft violet ground pool under the moth (NEON violet), the widest (lights caves)"),
    "pet_pool_fox": dict(fn=lambda: pet_pool(7, RED, 9.0), kind="decal", fps=7, pivot=[16, 16], lift=0.02, glow=True,
                         desc="soft red foxfire ground pool under the fox's tail (NEON red)"),
    "pet_aura_mosspup": dict(fn=lambda: spore_drift(41, GREEN), kind="billboard", fps=8, pivot=[16, 31], lift=0.0, glow=True,
                             desc="neon-green glowing spores puffing up off the moss-pup's toadstools (NEON green, a red fleck now and then)"),
    "pet_pool_mosspup": dict(fn=lambda: pet_pool(8, GREEN, 10.0), kind="decal", fps=5, pivot=[16, 16], lift=0.02, glow=True,
                             desc="soft toxic-green ground pool under the moss-pup (NEON green)"),
}


def build_fx():
    names = list(FX)
    atlas = Image.new("RGBA", (CELL * 8, CELL * len(names)), (0, 0, 0, 0))
    meta = {"tool": "hearthmoor-art pets_gen (spells format)", "biome": "cozy-village", "image": "pets_fx.png", "cell": CELL,
            "size": [atlas.width, atlas.height], "neon": NEON, "effects": {}}
    frames_by = {}
    for row, n in enumerate(names):
        e = FX[n]
        frs = e["fn"]()
        frames_by[n] = frs
        fl = []
        for i, F in enumerate(frs):
            atlas.paste(F.image(), (i * CELL, row * CELL))
            fl.append({"x": i * CELL, "y": row * CELL, "w": CELL, "h": CELL})
        meta["effects"][n] = {"row": row, "frames": len(frs), "fps": e["fps"], "loop": True, "loop_from": 0, "loops": 1,
                              "kind": e["kind"], "pivot": e["pivot"], "lift": e["lift"], "glow": e["glow"], "light": None,
                              "speed": None, "travel": None, "then": None, "frame_list": fl, "combat": True,
                              "duration": round(len(frs) / e["fps"], 3), "desc": e["desc"],
                              **({"follow_lift": e["follow_lift"]} if e.get("follow_lift") else {})}
    return atlas, meta, frames_by


# ------------------------------------------------------------------ 16 px particles (tools/particles format)
PCELL = 16
PROWS = ["pet_wisp_spark", "pet_moth_dust", "pet_fox_ember", "pet_mosspup_spore"]


def build_particles():
    im = Image.new("RGBA", (PCELL * 4, PCELL * len(PROWS)), (0, 0, 0, 0))
    px = im.load()

    def put(row, f, x, y, c):
        px[f * PCELL + x, row * PCELL + y] = rgb(c) + (255,)
    shapes = {
        # cold-fire spark: dot, plus-star, white heart, fading dot
        "pet_wisp_spark": [[(8, 8, "flower_blue")],
                           [(8, 8, "white"), (7, 8, "sky"), (9, 8, "sky"), (8, 7, "sky"), (8, 9, "sky")],
                           [(8, 8, "white"), (8, 7, "sky"), (8, 9, "flower_blue")],
                           [(8, 8, "cloth")]],
        # violet wing dust: a twinkling 1-2 px scale
        "pet_moth_dust": [[(8, 8, "neon_violet_lo")],
                          [(8, 8, "neon_violet_hi"), (9, 8, "neon_violet")],
                          [(8, 8, "white"), (7, 8, "neon_violet_hi"), (9, 8, "neon_violet_hi"), (8, 7, "neon_violet_hi"), (8, 9, "neon_violet_hi")],
                          [(8, 8, "neon_violet")]],
        # foxfire ember: tongue, bright tip, cooling
        "pet_fox_ember": [[(8, 9, "neon_red"), (8, 8, "white")],
                          [(8, 9, "neon_red_hi"), (8, 8, "white"), (8, 10, "neon_red")],
                          [(8, 8, "neon_red_hi")],
                          [(8, 8, "neon_red_lo")]],
        # moss-pup spore: a fleck, a round 2x2 puff, a white-hearted twinkle, fading
        "pet_mosspup_spore": [[(8, 8, "neon_green_lo")],
                              [(8, 8, "neon_green_hi"), (9, 8, "neon_green"), (8, 9, "neon_green"), (9, 9, "neon_green_lo")],
                              [(8, 8, "white"), (7, 8, "neon_green_hi"), (9, 8, "neon_green_hi"), (8, 7, "neon_green_hi"), (8, 9, "neon_green_hi")],
                              [(8, 8, "neon_green")]],
    }
    for r, n in enumerate(PROWS):
        for f, sh in enumerate(shapes[n]):
            for (x, y, c) in sh:
                put(r, f, x, y, c)
    presets = {
        "pet_wisp_spark": {"row": 0, "frames": 4, "fps": 6, "mode": "life", "rate": 3.0, "life": [0.6, 1.2], "grade": None,
                           "vel": [[-0.15, 0.15], [0.25, 0.6], [-0.15, 0.15]], "gravity": 0, "sway": 0.4, "glow": True,
                           "area": [0.35, 0.25, 0.35], "follow_pet": True},
        "pet_moth_dust": {"row": 1, "frames": 4, "fps": 5, "mode": "life", "rate": 3.5, "life": [0.9, 1.6], "grade": None,
                          "vel": [[-0.12, 0.12], [-0.35, -0.12], [-0.12, 0.12]], "gravity": 0, "sway": 0.6, "glow": True,
                          "area": [0.45, 0.15, 0.3], "follow_pet": True},
        "pet_fox_ember": {"row": 2, "frames": 4, "fps": 5, "mode": "life", "rate": 2.5, "life": [0.6, 1.1], "grade": None,
                          "vel": [[-0.15, 0.15], [0.5, 0.9], [-0.15, 0.15]], "gravity": -0.2, "sway": 0.5, "glow": True,
                          "area": [0.15, 0.1, 0.15], "follow_pet": True},
        "pet_mosspup_spore": {"row": 3, "frames": 4, "fps": 4, "mode": "life", "rate": 2.8, "life": [1.2, 2.2], "grade": None,
                              "vel": [[-0.1, 0.1], [0.15, 0.35], [-0.1, 0.1]], "gravity": 0, "sway": 0.7, "glow": True,
                              "area": [0.35, 0.15, 0.25], "follow_pet": True},
    }
    meta = {"tool": "hearthmoor-art pets_gen (particles format)", "biome": "cozy-village", "image": "pets_particles.png",
            "cell": PCELL, "rows": PROWS, "presets": presets}
    return im, meta


# ------------------------------------------------------------------ contact sheet
def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/TTF/DejaVuSans.ttf"):
        if Path(p).exists():
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def stepped_pool(d, cx, cy, rx, lc, base, steps=(0.07, 0.13, 0.2, 0.28), sq=0.34):
    """a posterised (stepped, no blur) stand-in for the pet's point light on the ground"""
    for k, a in enumerate(steps):
        r = rx * (1 - k / len(steps))
        col = tuple(int(base[j] * (1 - a) + lc[j] * a) for j in range(3)) + (255,)
        d.ellipse([cx - r, cy - r * sq, cx + r, cy + r * sq], fill=col)


def night_ground(im, x0, y0, w, h, S):
    """dark cobbles for the preview scene (native-pixel blocks at scale S)"""
    d = ImageDraw.Draw(im)
    R = random.Random(3)
    d.rectangle([x0, y0, x0 + w - 1, y0 + h - 1], fill=(22, 24, 34, 255))
    for yy in range(0, h // S, 4):
        off = 3 if (yy // 4) % 2 else 0
        for xx in range(-off, w // S, 6):
            c = R.choice([(30, 32, 44), (34, 36, 50), (27, 29, 40)])
            d.rectangle([x0 + max(0, xx) * S, y0 + yy * S, min(x0 + w - 1, x0 + (xx + 5) * S - 1), min(y0 + h - 1, y0 + (yy + 3) * S - 1)], fill=c + (255,))


def contact(sheet, roles, fx_atlas, fx_meta, fx_frames, p_im, path, sheet_alt=None, S=4):
    """sheet = the PRIMARY sheet (pets_neon.png); sheet_alt = the lock-safe palette-only pets.png"""
    BG, PANEL, CELLBG = (20, 18, 28), (30, 28, 42), (24, 23, 34)
    TXT, SUB = (246, 236, 210), (170, 160, 150)
    F1, F2, F3 = font(22), font(13), font(11)
    cw, ch = FW * S, FH * S                  # 80 x 128 per frame
    gap, left = 8, 92
    grid_w = left + COLS * (cw + 2) + 2 * gap
    side_x = grid_w + 16
    side_w = 560
    W = side_x + side_w + 16
    pet_h = 60 + 4 * (ch + 2) + 8
    H = 78 + len(PETS) * (pet_h + 14) + 30
    out = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(out)
    d.text((20, 14), "Hearthmoor pets: wisp kit, glow-moth, lantern-fox, moss-pup", fill=TXT, font=F1)
    d.text((20, 46), "pets_neon.png (PRIMARY, NEON glow pixels approved for pets): 20x32 native cells (actor atlas spec), nearest 4x, hard alpha, 1 px ink outline. "
                     "Columns idle 0-3 (3 = blink) | walk 4-7 | follow 8-11; rows down / up / left / right (right = mirrored left).", fill=SUB, font=F3)
    d.text((20, 60), "Tinted ellipses = stepped stand-in for each pet's point light (the engine uses ctx.addGlow, never bloom). Right panel: night preview with hover lift, pool decal and aura.",
           fill=SUB, font=F3)
    for pi, pet in enumerate(PETS):
        y0 = 78 + pi * (pet_h + 14)
        d.rectangle([10, y0, W - 10, y0 + pet_h], fill=PANEL + (255,))
        P, L = PETS[pet], PETS[pet]["light"]
        lc = rgb(L["color"])
        d.rectangle([20, y0 + 10, 36, y0 + 26], fill=lc + (255,), outline=(0, 0, 0, 255))
        d.text((44, y0 + 10), f"{P['name']}  ({pet})", fill=TXT, font=F2)
        d.text((44, y0 + 30), f"light {L['color']}  intensity {L['intensity']}  range {L['range']} m  lift {L['lift']} m  "
                              f"pulse x{L['pulse']['min']}-{L['pulse']['max']} @ {L['pulse']['hz']} Hz ({L['pulse']['shape']})  |  "
                              f"hover lift {P['hover']['lift']} m, bob {P['hover']['bob']} m  |  aura {P['aura']}  pool {P['pool']}  particles {P['particles']}",
               fill=SUB, font=F3)
        gy0 = y0 + 52
        for c in range(COLS):
            an = "idle" if c < 4 else "walk" if c < 8 else "follow"
            x = left + c * (cw + 2) + (c // 4) * gap
            d.text((x + 4, gy0 - 2), f"{an} {c % 4}" + (" (blink)" if c == 3 else ""), fill=SUB, font=F3)
        for fi, facing in enumerate(FACINGS):
            ry = gy0 + 12 + fi * (ch + 2)
            d.text((20, ry + ch // 2 - 8), facing, fill=TXT, font=F2)
            for c in range(COLS):
                x = left + c * (cw + 2) + (c // 4) * gap
                d.rectangle([x, ry, x + cw - 1, ry + ch - 1], fill=CELLBG + (255,))
                stepped_pool(d, x + cw // 2, ry + ch - 6, 36, lc, CELLBG, steps=(0.08, 0.16, 0.26))
                fr = sheet.crop((c * FW, (pi * 4 + fi) * FH, (c + 1) * FW, (pi * 4 + fi + 1) * FH)).resize((cw, ch), Image.NEAREST)
                out.alpha_composite(fr, (x, ry))
        # ---- night preview scene (4x): hero for scale, the pet at its hover lift, pool decal, light, aura
        sx, sy = side_x, gy0 + 4
        sw, sh = side_w, 300
        night_ground(out, sx, sy, sw, sh, S)
        px_, py_ = sx + 330, sy + sh - 40                       # pet feet
        stepped_pool(d, px_, py_, 30 * L["range"] / 3.2 * 4, lc, (26, 28, 40), steps=(0.06, 0.12, 0.19, 0.27, 0.36))
        shc = tuple(int(c * 0.55) for c in (26, 28, 40)) + (255,)
        d.ellipse([px_ - 5 * S, py_ - 1 * S, px_ + 5 * S, py_ + 1 * S], fill=shc)   # faint sprite shadow, stays on the ground
        pool = fx_frames[P["pool"]][1].image().resize((CELL * S, CELL * S), Image.NEAREST)
        out.alpha_composite(pool, (px_ - 16 * S, py_ - 16 * S))
        if HERO:
            hx = sx + 170
            stepped_pool(d, hx, py_ - 4, 18, (0, 0, 0), (26, 28, 40), steps=(0.5,), sq=0.3)
            out.alpha_composite(HERO.resize((cw, ch), Image.NEAREST), (hx - 10 * S, py_ - 32 * S - 4))
        lift = int(round(P["hover"]["lift"] * 32 / 1.8)) * S        # metres -> native px (1.8 m = 32 px) -> 4x
        fcol = 8 if pet in ("pet_wisp", "pet_moth") else 0
        pf = sheet.crop((fcol * FW, (pi * 4 + 2) * FH, (fcol + 1) * FW, (pi * 4 + 3) * FH)).resize((cw, ch), Image.NEAREST)
        out.alpha_composite(pf, (px_ - 10 * S, py_ - 32 * S - lift))
        aura = fx_frames[P["aura"]][3].image().resize((CELL * S, CELL * S), Image.NEAREST)
        out.alpha_composite(aura, (px_ - 16 * S, py_ - 32 * S - lift + {"pet_fox": -10 * S, "pet_mosspup": -6 * S}.get(pet, 0)))
        d.text((sx + 8, sy + 6), "night preview @4x: hero for scale, pet at hover lift, pool decal + stepped light, aura", fill=SUB, font=F3)
        # ---- aura (8f) and pool (6f) strips at 2x, particle cells at 6x, NEON variant
        ay = sy + sh + 10
        d.text((sx, ay), f"{P['aura']} (billboard, 8f) @2x", fill=SUB, font=F3)
        for k in range(8):
            a2 = fx_frames[P["aura"]][k].image().resize((64, 64), Image.NEAREST)
            xx = sx + k * 68
            d.rectangle([xx, ay + 14, xx + 63, ay + 77], fill=(14, 14, 22, 255))
            out.alpha_composite(a2, (xx, ay + 14))
        py2 = ay + 84
        d.text((sx, py2), f"{P['pool']} (decal, 6f) @2x", fill=SUB, font=F3)
        for k in range(6):
            p2 = fx_frames[P["pool"]][k].image().resize((64, 64), Image.NEAREST)
            xx = sx + k * 68
            d.rectangle([xx, py2 + 14, xx + 63, py2 + 77], fill=(14, 14, 22, 255))
            out.alpha_composite(p2, (xx, py2 + 14))
        qy = py2 + 84
        d.text((sx, qy), f"particle {PROWS[pi]} (16 px, 4f) @6x", fill=SUB, font=F3)
        for f in range(4):
            cell = p_im.crop((f * PCELL, pi * PCELL, (f + 1) * PCELL, (pi + 1) * PCELL)).crop((4, 4, 12, 12)).resize((48, 48), Image.NEAREST)
            xx = sx + f * 52
            d.rectangle([xx, qy + 14, xx + 47, qy + 61], fill=(14, 14, 22, 255))
            out.alpha_composite(cell, (xx, qy + 14))
        if sheet_alt is not None:
            d.text((sx + 270, qy), "lock-safe pets.png (palette only, check-sprite PASS)", fill=SUB, font=F3)
            for k, c in enumerate((0, 4, 8)):
                for j, fi in enumerate((0, 2)):
                    nf = sheet_alt.crop((c * FW, (pi * 4 + fi) * FH + 10, (c + 1) * FW, (pi * 4 + fi + 1) * FH)).resize((FW * 2, (FH - 10) * 2), Image.NEAREST)
                    xx = sx + 270 + (k * 2 + j) * 44
                    d.rectangle([xx, qy + 14, xx + FW * 2 - 1, qy + 14 + (FH - 10) * 2 - 1], fill=(14, 14, 22, 255))
                    out.alpha_composite(nf, (xx, qy + 14))
    d.text((20, H - 22), "Original pixel art for Hearthmoor (no copied pixels). Glow = emissive palette / NEON pixels + one pooled point light per pet; never bloom.",
           fill=SUB, font=F3)
    out.convert("RGB").save(path)


HERO = None


def main():
    global HERO
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent))
    ap.add_argument("--hero", default="/workspace/hd2d-suite/games/hearthmoor/areas/plaza/public/art/sprite/actors.png",
                    help="read-only: an area atlas, used only to put the wildcaller beside the pets on the contact sheet")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    try:
        hj = json.loads(Path(a.hero).with_suffix(".json").read_text())
        r = hj["roles"]["wildcaller"]["row"]
        HERO = Image.open(a.hero).convert("RGBA").crop((0, r * 32, 20, r * 32 + 32))
    except Exception:
        HERO = None
    sheet, roles = build_sheet(SLOTS_SAFE)
    sheet.save(out / "pets.png")
    neon, _ = build_sheet(SLOTS_NEON)
    neon.save(out / "pets_neon.png")
    for pi, pet in enumerate(PETS):   # per-pet strips: <pet>.png = primary NEON, <pet>_safe.png = lock-safe palette
        neon.crop((0, pi * 4 * FH, COLS * FW, (pi + 1) * 4 * FH)).save(out / f"{pet}.png")
        sheet.crop((0, pi * 4 * FH, COLS * FW, (pi + 1) * 4 * FH)).save(out / f"{pet}_safe.png")
    meta = {"tool": "hearthmoor-art pets_gen", "biome": "cozy-village", "seed": 7, "frame": [FW, FH], "pivot": PIVOT,
            "ground_row": GROUND, "facings": list(FACINGS), "anims": ANIMS, "cols": COLS, "image": "pets_neon.png",
            "image_neon": "pets_neon.png", "image_lock_safe": "pets.png", "primary": "pets_neon.png",
            "neon_accents": NEON, "size": [sheet.width, sheet.height], "fx": "pets_fx.json",
            "particles": "pets_particles.json", "roles": roles}
    (out / "pets.json").write_text(json.dumps(meta, indent=1))
    fx_atlas, fx_meta, fx_frames = build_fx()
    fx_atlas.save(out / "pets_fx.png")
    (out / "pets_fx.json").write_text(json.dumps(fx_meta, indent=1))
    p_im, p_meta = build_particles()
    p_im.save(out / "pets_particles.png")
    (out / "pets_particles.json").write_text(json.dumps(p_meta, indent=1))
    contact(neon, roles, fx_atlas, fx_meta, fx_frames, p_im, out / "contact_sheet.png", sheet_alt=sheet)
    print("pets:", ", ".join(PETS), "->", out)


if __name__ == "__main__":
    main()
