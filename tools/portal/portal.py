"""hd2d portal: game effect art for cozy HD-2D games (original pixel art, biome palette only).

    hd2d portal --biome cozy-village --out PROJECT/public/art/gamefx

48x48 cells, hard alpha, nearest-neighbour, every pixel a biome colour (no glow halos, no blur):

  portal_vortex   swirling two-arm vortex for the stone-arch gate (billboard, loops)
  portal_ring     rune ring on the ground in front of the gate (ground decal, pre-squashed, loops)
  moonpetal       a glade herb with pale petals and a glint (pickup billboard, loops)
  quest_mark      a parchment "!" tag that bobs over someone who has an errand (billboard, lifted)
  quest_turnin    a gold star tag over someone waiting for your delivery (billboard, lifted)
  rift_vortex     the open Rift gate (Vanaheim): a green-gold spiral fringed with neon-blue cold-fire tongues
  rift_seal_violet / rift_seal_blue / rift_seal_red
                  a sealed Rift gate: dark slow swirl, a thin dashed neon rim and a lock rune that pulses faintly
  rift_ring       the Rift Shrine's ground circle: dithered ellipse with blue / violet / red rune dashes (decal)
  alf_rune        a violet Alfheim rune burned into the ground (Veyra's poison mark at Vanaheim's spring; decal)
  spring_poison   the poisoned spring's water (decal over the basin): sickly violet swirl, slow dark bubbles that swell + pop
  spring_clean    the same spring cleansed (for later, behind a flag): clear blue water, pale ripples, white sparkles

Signature glows use the named NEON accents (the same approved set as hd2d spells, plus neon blue cold-fire)
for effect pixels only; scenery stays in the biome palette.

Style references (rift refs: swirling vortexes, stone-arch gates, flame rings) were looked at for ideas only;
nothing is traced or copied. Writes gamefx.png, gamefx.json (same format as hd2d spells, so the runtime's
Effects class plays it) and gamefx_contact_4x.png.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from PIL import Image, ImageDraw  # noqa: E402

from hd2d_common import Pal, ensure, hex2rgb, load_biome, write_json  # noqa: E402

CELL = 48
NEON = {"neon_red": "#e0302a", "neon_red_lo": "#a81c22", "neon_red_hi": "#ff5a4a",
        "neon_violet": "#a45cf0", "neon_violet_hi": "#d4a8ff", "neon_violet_lo": "#6a34b8",
        "neon_blue": "#2ab4ff", "neon_blue_hi": "#a6ecff", "neon_blue_lo": "#1c62d8"}
SQUASH = math.sin(math.radians(36))


def h2(x, y, s=0):
    v = math.sin(x * 12.9898 + y * 78.233 + s * 37.719) * 43758.5453
    return v - math.floor(v)


class Frame:
    def __init__(self, pal):
        self.pal = pal
        self.p = [[None] * CELL for _ in range(CELL)]

    def set(self, x, y, c):
        x, y = int(round(x)), int(round(y))
        if c and 0 <= x < CELL and 0 <= y < CELL:
            if c not in NEON:
                self.pal[c]  # raises if the colour is not in the biome (or a named neon accent)
            self.p[y][x] = c

    def get(self, x, y):
        return self.p[y][x] if 0 <= x < CELL and 0 <= y < CELL else None

    def outline(self, c="ink"):
        pts = []
        for y in range(CELL):
            for x in range(CELL):
                if self.p[y][x] is None and any(self.get(x + dx, y + dy) not in (None, c) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    pts.append((x, y))
        for x, y in pts:
            self.p[y][x] = c

    def image(self):
        im = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
        px = im.load()
        for y in range(CELL):
            for x in range(CELL):
                c = self.p[y][x]
                if c:
                    r, g, b = hex2rgb(NEON[c] if c in NEON else self.pal[c])
                    px[x, y] = (r, g, b, 255)
        return im


def vortex(pal, seed):
    """Two spiral arms wind into a deep core; the rim frays into leafy wisps that drift round; gold glints orbit."""
    out = []
    cx, cy, rx, ry = 23.5, 25.0, 12.5, 21.0
    for f in range(8):
        F = Frame(pal)
        ph = f / 8.0
        for y in range(CELL):
            for x in range(CELL):
                dx, dy = (x - cx) / rx, (y - cy) / ry
                d = math.hypot(dx, dy)
                a = math.atan2(dy, dx)
                # frayed rim: wisps leave the edge along the spin direction
                fray = 0.08 * math.sin(a * 5 + ph * math.tau) + 0.05 * (h2(int(a * 6 + f), 3, seed) - 0.5)
                if d > 1.0 + fray:
                    continue
                s = (a / math.tau * 2 + math.log(d + 0.08) * 0.9 - ph) % 1.0      # two log-spiral arms
                if d < 0.16:
                    c = "shadow"
                elif d < 0.3:
                    c = "flower_blue" if s < 0.5 else "shadow"
                elif d > 0.9:
                    c = "grass_hi" if s < 0.45 else "moss"
                else:
                    c = "white" if s < 0.12 else "sky" if s < 0.32 else "flower_blue" if s < 0.62 else "shadow"
                F.set(x, y, c)
        # orbiting glints and a few motes spun off the rim
        for k in range(5):
            ang = ph * math.tau + k * math.tau / 5
            gx, gy = cx + math.cos(ang) * (rx + 2.5), cy + math.sin(ang) * (ry + 2.0)
            F.set(gx, gy, "flower_gold"); F.set(gx + 1, gy, "lamp")
            if k % 2 == f % 2:
                F.set(gx, gy - 1, "white")
        for k in range(4):
            ang = -ph * math.tau * 1.5 + k * 1.7
            r = 1.12 + 0.12 * ((f + k) % 3)
            F.set(cx + math.cos(ang) * rx * r, cy + math.sin(ang) * ry * r, "grass_hi")
        out.append(F)
    return out


def ring(pal, seed):
    out = []
    cx, cy, R = 23.5, 24.0, 21.0
    for f in range(8):
        F = Frame(pal)
        ph = f / 8.0
        n = 120
        for i in range(n):
            a = i / n * math.tau
            for rr, c in ((R, "moss"), (R - 1, "grass_hi")):
                F.set(cx + math.cos(a) * rr, cy + math.sin(a) * rr * SQUASH, c)
        # rotating rune dashes on an inner ring
        for k in range(10):
            a = k / 10 * math.tau + ph * math.tau / 5
            for t in range(3):
                aa = a + t * 0.05
                F.set(cx + math.cos(aa) * (R - 4.5), cy + math.sin(aa) * (R - 4.5) * SQUASH, "sky" if (k + f) % 3 else "white")
        # four leaf glyphs at the quarters, pulsing gold
        for k in range(4):
            a = k / 4 * math.tau + 0.4
            gx, gy = cx + math.cos(a) * (R - 8), cy + math.sin(a) * (R - 8) * SQUASH
            c = "flower_gold" if (f // 2 + k) % 2 else "lamp"
            F.set(gx, gy, c); F.set(gx - 1, gy, c); F.set(gx + 1, gy, c); F.set(gx, gy - 1, "grass_hi")
        out.append(F)
    return out


def moonpetal(pal, seed):
    out = []
    bx, by = 24, 46
    for f in range(4):
        F = Frame(pal)
        for i in range(8):
            F.set(bx + (1 if i > 5 else 0), by - i, "moss")
        for (lx, ly) in ((-2, -3), (-3, -2), (2, -4), (3, -3)):
            F.set(bx + lx, by + ly, "grass_hi" if lx < 0 else "moss")
        # three pale petals around a gold eye
        for (px_, py_) in ((-2, -10), (2, -10), (0, -12), (-1, -9), (1, -9)):
            F.set(bx + px_, by + py_, "flower_blue")
        for (px_, py_) in ((-1, -11), (1, -11), (0, -10)):
            F.set(bx + px_, by + py_, "white")
        F.set(bx, by - 10, "flower_gold")
        F.outline("ink")
        # the glint orbits above (not outlined, a pickup tell)
        gx = [bx - 4, bx + 3, bx + 4, bx - 3][f]
        gy = [by - 15, by - 16, by - 13, by - 14][f]
        F.set(gx, gy, "white"); F.set(gx + 1, gy, "lamp"); F.set(gx - 1, gy, "lamp"); F.set(gx, gy - 1, "lamp"); F.set(gx, gy + 1, "lamp")
        out.append(F)
    return out


def tag(pal, kind):
    out = []
    for f in range(4):
        F = Frame(pal)
        bob = [0, -1, -1, 0][f]
        cx, top = 24, 30 + bob
        # little parchment tag (cozy HUD style), 9x11, with a hanging string
        for y in range(top, top + 11):
            for x in range(cx - 4, cx + 5):
                F.set(x, y, "plaster_hi" if y > top else "plaster")
        if kind == "mark":
            for y in range(top + 2, top + 7):
                F.set(cx, y, "roof_lo")
            F.set(cx, top + 8, "roof_lo")
        else:
            for (x, y) in ((0, 2), (0, 3), (-1, 4), (1, 4), (-2, 5), (2, 5), (-3, 5), (3, 5), (-1, 6), (1, 6), (-2, 7), (2, 7), (0, 5), (0, 6)):
                F.set(cx + x, top + y, "flower_gold")
            F.set(cx, top + 4, "lamp")
        F.outline("ink")
        out.append(F)
    return out


def rift_vortex(pal, seed):
    """Open Rift gate: a two-arm spiral (deep shadow core, moss / grass-gold arms, pale sky streaks) whose rim
    burns with neon-blue cold-fire tongues that lick upward and round; white pixel sparkles orbit and flicker."""
    out = []
    cx, cy, rx, ry = 23.5, 25.0, 12.5, 21.0
    for f in range(8):
        F = Frame(pal)
        ph = f / 8.0
        for y in range(CELL):
            for x in range(CELL):
                dx, dy = (x - cx) / rx, (y - cy) / ry
                d = math.hypot(dx, dy)
                a = math.atan2(dy, dx)
                if d > 1.0:
                    continue
                s_ = (a / math.tau * 2 + math.log(d + 0.08) * 1.1 - ph) % 1.0
                if d < 0.15:
                    c = "ink"
                elif d < 0.32:
                    c = "neon_blue_lo" if s_ < 0.4 else "shadow"
                elif d > 0.86:
                    # rim: cold-fire band, dithered
                    c = "neon_blue" if (x + y + f) % 2 == 0 or s_ < 0.5 else "neon_blue_lo"
                else:
                    c = ("white" if s_ < 0.08 else "grass_hi" if s_ < 0.26 else "moss" if s_ < 0.52
                         else "neon_blue_lo" if s_ < 0.62 else "leaf_deep")
                F.set(x, y, c)
        # cold-fire tongues: short flames rising off the rim, each flickering through 3 heights
        for k in range(12):
            a = k / 12 * math.tau + ph * math.tau * 0.25
            bx, by = cx + math.cos(a) * rx, cy + math.sin(a) * ry
            hgt = 2 + int(3 * h2(k, f, seed))
            for t in range(hgt):
                c = "neon_blue_hi" if t == hgt - 1 else "neon_blue"
                F.set(bx + math.cos(a) * (t * 0.6), by + math.sin(a) * (t * 0.6) - t * 0.7, c)
        for k in range(6):
            ang = -ph * math.tau + k * math.tau / 6
            gx, gy = cx + math.cos(ang) * (rx + 4), cy + math.sin(ang) * (ry + 3)
            if (k + f) % 3:
                F.set(gx, gy, "white"); F.set(gx - 1, gy, "neon_blue_hi"); F.set(gx + 1, gy, "neon_blue_hi")
                F.set(gx, gy - 1, "neon_blue_hi"); F.set(gx, gy + 1, "neon_blue_hi")
            else:
                F.set(gx, gy, "flower_gold")
        out.append(F)
    return out


def rift_seal(hue):
    """Sealed Rift gate: a dark, slow, barely-moving swirl (ink / shadow / the hue's low tone), a thin dashed rim
    in the hue and a diamond lock rune that brightens on two frames of six (a faint heartbeat)."""
    lo, mid, hi = f"neon_{hue}_lo", f"neon_{hue}", f"neon_{hue}_hi"

    def fn(pal, seed):
        out = []
        cx, cy, rx, ry = 23.5, 25.0, 12.5, 21.0
        for f in range(6):
            F = Frame(pal)
            ph = f / 6.0 * 0.25
            beat = f in (2, 3)
            for y in range(CELL):
                for x in range(CELL):
                    dx, dy = (x - cx) / rx, (y - cy) / ry
                    d = math.hypot(dx, dy)
                    if d > 1.0:
                        continue
                    a = math.atan2(dy, dx)
                    s_ = (a / math.tau * 3 + math.log(d + 0.1) * 0.7 - ph) % 1.0
                    if d > 0.93:
                        c = mid if (int((a / math.tau) * 40) + f) % 3 else lo
                    elif s_ < 0.1 and (x + y) % 2 == 0:
                        c = lo
                    elif s_ < 0.45:
                        c = "shadow"
                    else:
                        c = "ink"
                    F.set(x, y, c)
            # lock rune: a diamond with a bar, centre of the gate
            for t in range(-9, 10):
                w = round(5 * (1 - abs(t) / 9))
                for e in (-w, w):
                    F.set(cx + e, cy + t, hi if beat else mid); F.set(cx + e + (1 if e < 0 else -1), cy + t, mid if beat else lo)
            for t in range(-3, 4):
                F.set(cx + t, cy, hi if beat else mid)
            for t in range(-9, -4):
                F.set(cx, cy + t, mid)
            F.set(cx, cy, "white" if beat else mid)
            # a few faint motes drifting up the face
            for k in range(3):
                mx = cx + (k - 1) * 6 + (1 if (f + k) % 2 else 0)
                my = cy + 14 - ((f * 3 + k * 7) % 26)
                F.set(mx, my, lo)
            out.append(F)
        return out
    return fn


def rift_ring(pal, seed):
    """The shrine's ground circle (pre-squashed decal): a dithered stone-grey ellipse, an inner band of rune dashes
    cycling blue -> violet -> red as it turns, and three glyph pips at the thirds."""
    out = []
    cx, cy, R = 23.5, 24.0, 22.0
    hues = ("neon_blue", "neon_violet", "neon_red")
    for f in range(8):
        F = Frame(pal)
        ph = f / 8.0
        n = 160
        for i in range(n):
            a = i / n * math.tau
            for rr, c in ((R, "shadow"), (R - 1, "stone_lo" if i % 2 else "shadow")):
                F.set(cx + math.cos(a) * rr, cy + math.sin(a) * rr * SQUASH, c)
        for k in range(18):
            a = k / 18 * math.tau + ph * math.tau / 6
            c = hues[(k // 6 + (f // 3)) % 3] if (k + f) % 4 else hues[k % 3] + "_hi"
            for t in range(3):
                aa = a + t * 0.04
                F.set(cx + math.cos(aa) * (R - 4), cy + math.sin(aa) * (R - 4) * SQUASH, c)
        for k in range(3):
            a = k / 3 * math.tau + math.pi / 2
            gx, gy = cx + math.cos(a) * (R - 9), cy + math.sin(a) * (R - 9) * SQUASH
            c = hues[k] + ("_hi" if (f // 2 + k) % 2 else "")
            for (ox, oy) in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
                F.set(gx + ox, gy + oy, c)
        out.append(F)
    return out


def alf_rune(pal, seed):
    """Veyra's poison mark: a violet Alfheim rune (a branching stave inside a broken ring) burned into the ground,
    pre-squashed; it smoulders (dim -> bright -> dim) over six frames."""
    out = []
    cx, cy, R = 23.5, 24.0, 15.0
    for f in range(6):
        F = Frame(pal)
        hot = [0, 1, 2, 2, 1, 0][f]
        c_ring = ("neon_violet_lo", "neon_violet", "neon_violet")[hot]
        c_rune = ("neon_violet", "neon_violet_hi", "neon_violet_hi")[hot]
        for i in range(110):
            a = i / 110 * math.tau
            if int(a / math.tau * 12) % 4 == 3:
                continue
            F.set(cx + math.cos(a) * R, cy + math.sin(a) * R * SQUASH, c_ring)
        for t in range(-8, 9):
            F.set(cx, cy + t * SQUASH, c_rune)
        for (sx, sy, ex, ey) in ((0, -3, -5, -7), (0, -3, 5, -7), (0, 3, -4, 6), (0, 3, 4, 6)):
            for k in range(7):
                q = k / 6
                F.set(cx + sx + (ex - sx) * q, cy + (sy + (ey - sy) * q) * SQUASH, c_rune)
        if hot == 2:
            F.set(cx, cy, "white")
        out.append(F)
    return out


def spring_water(kind):
    """Water surface decal sized to the spring basin (r 1.25 m, pre-squashed). poison: a slow dithered swirl of
    neon-violet / shadow with ink bubbles that swell over three frames and pop into a violet ring; clean: sky and
    flower-blue ripples with white sparkles that twinkle round."""
    def fn(pal, seed):
        out = []
        cx, cy, rx = 23.5, 24.0, 23.0
        ry = rx * SQUASH
        n = 8
        for f in range(n):
            F = Frame(pal)
            ph = f / n
            for y in range(CELL):
                for x in range(CELL):
                    dx, dy = (x - cx) / rx, (y - cy) / ry
                    d = math.hypot(dx, dy)
                    if d > 1.0:
                        continue
                    a = math.atan2(dy, dx)
                    w = (a / math.tau + d * 1.6 - ph * 0.5) % 1.0
                    if kind == "poison":
                        if d > 0.9:
                            c = "shadow" if (x + y) % 2 else "neon_violet_lo"
                        elif w < 0.18:
                            c = "neon_violet" if (x + y + f) % 2 == 0 else "neon_violet_lo"
                        elif w < 0.55:
                            c = "neon_violet_lo"
                        else:
                            c = "neon_violet_lo" if (x + 2 * y) % 3 == 0 else "shadow"
                    else:
                        if d > 0.9:
                            c = "flower_blue"
                        elif w < 0.14:
                            c = "white" if (x + y) % 2 == 0 else "sky"
                        elif w < 0.6:
                            c = "sky"
                        else:
                            c = "flower_blue" if (x + y) % 2 else "sky"
                    F.set(x, y, c)
            if kind == "poison":
                # slow dark bubbles: each swells 3 frames, pops (violet ring), rests; staggered
                for k, (bx, by) in enumerate(((-9, -2), (6, -4), (-2, 4), (12, 3), (-14, 2))):
                    st = (f + k * 3) % 8
                    X, Y = cx + bx, cy + by
                    if st < 3:
                        r_ = 2 + st * 1.2
                        for t in range(22):
                            aa = t / 16 * math.tau
                            F.set(X + math.cos(aa) * r_, Y + math.sin(aa) * r_ * 0.7, "ink")
                        F.set(X - r_ * 0.4, Y - r_ * 0.4, "neon_violet_hi")
                    elif st == 3:
                        for t in range(12):
                            aa = t / 12 * math.tau
                            F.set(X + math.cos(aa) * 4, Y + math.sin(aa) * 2.6, "neon_violet")
                        F.set(X, Y, "ink")
            else:
                for k in range(6):
                    aa = ph * math.tau + k * math.tau / 6
                    X, Y = cx + math.cos(aa) * rx * 0.6, cy + math.sin(aa) * ry * 0.6
                    if (k + f) % 3 == 0:
                        F.set(X, Y, "white"); F.set(X - 1, Y, "sky"); F.set(X + 1, Y, "sky"); F.set(X, Y - 1, "white")
                    else:
                        F.set(X, Y, "white")
            out.append(F)
        return out
    return fn


EFFECTS = {
    "portal_vortex": dict(fn=vortex, fps=8, loop=True, kind="billboard", pivot=[24, 47], lift=0.18, glow=True),
    "portal_ring": dict(fn=ring, fps=6, loop=True, kind="decal", pivot=[24, 24], lift=0.02, glow=True),
    "moonpetal": dict(fn=moonpetal, fps=4, loop=True, kind="billboard", pivot=[24, 47], lift=0.0, glow=False),
    "quest_mark": dict(fn=lambda pal, seed: tag(pal, "mark"), fps=3, loop=True, kind="billboard", pivot=[24, 47], lift=2.05, glow=True),
    "quest_turnin": dict(fn=lambda pal, seed: tag(pal, "turnin"), fps=3, loop=True, kind="billboard", pivot=[24, 47], lift=2.05, glow=True),
    "rift_vortex": dict(fn=rift_vortex, fps=8, loop=True, kind="billboard", pivot=[24, 47], lift=0.18, glow=True),
    "rift_seal_violet": dict(fn=rift_seal("violet"), fps=4, loop=True, kind="billboard", pivot=[24, 47], lift=0.18, glow=True),
    "rift_seal_blue": dict(fn=rift_seal("blue"), fps=4, loop=True, kind="billboard", pivot=[24, 47], lift=0.18, glow=True),
    "rift_seal_red": dict(fn=rift_seal("red"), fps=4, loop=True, kind="billboard", pivot=[24, 47], lift=0.18, glow=True),
    "rift_ring": dict(fn=rift_ring, fps=6, loop=True, kind="decal", pivot=[24, 24], lift=0.03, glow=True),
    "alf_rune": dict(fn=alf_rune, fps=4, loop=True, kind="decal", pivot=[24, 24], lift=0.03, glow=True),
    "spring_poison": dict(fn=spring_water("poison"), fps=3, loop=True, kind="decal", pivot=[24, 24], lift=0.0, glow=True),
    "spring_clean": dict(fn=spring_water("clean"), fps=4, loop=True, kind="decal", pivot=[24, 24], lift=0.0, glow=True),
}


def build(biome="cozy-village", out="public/art/gamefx", project=None, seed=1):
    pal = Pal(load_biome(biome, project))
    out = ensure(out)
    names = list(EFFECTS)
    cols = max(len(EFFECTS[n]["fn"](pal, seed)) for n in names)
    atlas = Image.new("RGBA", (CELL * cols, CELL * len(names)), (0, 0, 0, 0))
    meta = {"tool": "hd2d portal", "biome": biome, "seed": seed, "image": "gamefx.png", "cell": CELL,
            "size": [atlas.width, atlas.height], "effects": {}, "cast_sets": {}, "cycle": []}
    for row, name in enumerate(names):
        e = EFFECTS[name]
        frames = e["fn"](pal, seed)
        for i, F in enumerate(frames):
            atlas.paste(F.image(), (i * CELL, row * CELL))
        meta["effects"][name] = {"row": row, "frames": len(frames), "fps": e["fps"], "loop": e["loop"], "loop_from": 0, "loops": 1,
                                 "kind": e["kind"], "pivot": e["pivot"], "lift": e["lift"], "glow": e["glow"], "light": None,
                                 "speed": None, "travel": None, "then": None, "duration": 9999}
    atlas.save(out / "gamefx.png")
    write_json(out / "gamefx.json", meta)
    big = atlas.resize((atlas.width * 4, atlas.height * 4), Image.NEAREST)
    sheet = Image.new("RGBA", (big.width + 140, big.height + 28), (46, 52, 84, 255))
    d = ImageDraw.Draw(sheet)
    d.text((144, 8), "hd2d portal: 48 px cells, hard alpha, biome palette, nearest 4x", fill=(246, 236, 210, 255))
    for i, n in enumerate(names):
        d.text((6, 28 + i * CELL * 4 + 80), n, fill=(246, 236, 210, 255))
    sheet.alpha_composite(big, (140, 28))
    sheet.save(out / "gamefx_contact_4x.png")
    return meta


def main(argv=None):
    ap = argparse.ArgumentParser(prog="hd2d portal", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--biome", default="cozy-village")
    ap.add_argument("--out", default="public/art/gamefx")
    ap.add_argument("--project", default=None)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args(argv)
    m = build(a.biome, a.out, a.project, a.seed)
    print(f"portal: {len(m['effects'])} effects ({', '.join(m['effects'])}) -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
