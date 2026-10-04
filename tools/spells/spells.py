"""hd2d spells: cozy pixel spell effects (original; ideas from the Gravewake spell writer, never edited).

    hd2d spells --biome cozy-village --out PROJECT/public/art/spells

32x32 cells, one strip of 6-8 frames per effect. Nearest-neighbour, hard alpha, every pixel a biome colour,
no glow, no blur: brightness comes from the palette's lightest steps, fades are dithers.

  sparkle_burst   star sparkles fly out from the hands                (billboard)
  healing_petals  rose petals spiral up around the target             (billboard)
  hearth_flame    a small warm hearth flame (loops)                   (billboard)
  frost_puff      a cold puff with ice glints, dithers away           (billboard)
  leaf_gust       a swirl of leaves on a wind streak                  (billboard)
  light_orb       a floating lantern orb with a pulse ring (loops)    (billboard, lifted)
  rune_circle     a gold rune ring drawn on the ground, then turning   (ground decal, pre-squashed for the 3/4 camera)
  bolt            a spinning spark projectile (loops)                 (projectile -> impact)
  impact          a star-burst hit                                    (billboard)
  hero combat (Hearthmoor): seed_bomb -> earth_burst, rune_slam, rune_trap + glyph_burst, sky_strike,
  bloom_ring, ember_slash -> ember_pop; enemy coldfire_bolt -> frost_puff; hit_spark, summon_poof
  glow pass (Hearthmoor): light_pool (ground decal under spells), glitter (twinkling motes), toadstools (night glow),
  coldfire_pool + coldfire_motes (Sefa's neon-blue lantern pool at night)
  glow-gardening (Hearthmoor Stage 4): garden_plot (soil bed decal), glowplant_seed / _sprout, and the blooms
  glowplant_coldfire (neon-blue), glowplant_violet (neon violet), glowplant_toadcap (neon red, crisp white spots);
  violet_pool / red_pool (their night ground pools). Violet + saturated red use the named NEON glow accents.
  Lantern Eve (Hearthmoor Stage 5): sky_lantern (a paper sky lantern lit from inside, flame at the opening), rift_tear (Veyra's violet-red omen).
  Rares + random rifts (Stage 5 part 2): rare_aura_blue / _violet / _red (a rare's element ground aura), rift_tear_minor
  (tier I), rift_tear (tier II), rift_tear_abyss + rift_ring_abyss (tier III).

Writes spells.png (atlas, one row per effect), <effect>.png strips, spells.json (frames + effect presets the
runtime plays: kind, fps, loop, pivot, lift, point-light flash curve), spells_contact_4x.png.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from PIL import Image, ImageDraw  # noqa: E402

from hd2d_common import Pal, ensure, hex2rgb, load_biome, rng, write_json  # noqa: E402

CELL = 32
COLS = 8
# camera pitch used to pre-squash ground decals (matches the scene camera default)
DECAL_SQUASH = math.sin(math.radians(36))


# Neon glow accents (Hearthmoor glow-gardening): the story bible's signature glows are neon-blue cold fire, violet neon
# and red neon. Blue is in the cozy palette (sky / flower_blue); violet and a saturated toadstool red are not, so the
# emissive glow plants use these few named accents (same hexes as the Hollows kit's self-lit toadstools). Only for
# glowing pixels: never for world, sprites or HUD.
NEON = {"neon_red": "#e0302a", "neon_red_lo": "#a81c22", "neon_red_hi": "#ff5a4a",
        "neon_violet": "#a45cf0", "neon_violet_hi": "#d4a8ff", "neon_violet_lo": "#6a34b8"}


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

    def star(self, x, y, size, core="white", arm="lamp"):
        self.set(x, y, core)
        for k in range(1, size + 1):
            c = arm if k < size else "flower_gold"
            for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)):
                self.set(x + dx, y + dy, c)

    def disk(self, cx, cy, r, cols, sq=1.0):
        for y in range(CELL):
            for x in range(CELL):
                d = math.hypot(x - cx, (y - cy) / sq)
                if d <= r:
                    t = d / max(r, 0.01)
                    self.set(x, y, cols[min(len(cols) - 1, int(t * len(cols)))])

    def ring(self, cx, cy, rx, ry, c, frac=1.0, start=0.0, dots=0):
        n = max(24, int((rx + ry) * 4))
        for i in range(int(n * frac)):
            if dots and i % dots:
                continue
            a = start + i / n * math.tau
            self.set(cx + math.cos(a) * rx, cy + math.sin(a) * ry, c)

    def line(self, x0, y0, x1, y1, c, every=1):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for i in range(n):
            if i % every == 0:
                t = i / max(1, n - 1)
                self.set(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, c)

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


# ------------------------------------------------------------------ effects
def sparkle_burst(pal, seed):
    out = []
    R = rng(seed, "sparkle")
    angs = [R.random() * math.tau for _ in range(7)]
    cols = [("white", "lamp"), ("white", "flower_gold"), ("white", "flower_rose"), ("lamp", "flower_gold")]
    for f in range(8):
        F = Frame(pal)
        if f < 2:
            F.disk(16, 18, 2.5 + f * 1.5, ["white", "lamp", "flower_gold"])
        for k, a in enumerate(angs):
            r = 3 + f * 2.0 + (k % 3)
            x, y = 16 + math.cos(a) * r, 18 + math.sin(a) * r * 0.85 - f * 0.6
            if f >= 5 and (k + f) % 2:
                continue
            size = 2 if f < 3 else 1 if f < 6 else 0
            core, arm = cols[k % 4]
            F.star(x, y, size, core, arm)
        out.append(F)
    return out


def healing_petals(pal, seed):
    out = []
    R = rng(seed, "petals")
    ph = [(R.random() * 26, R.random() * math.tau, R.uniform(5, 10)) for _ in range(11)]
    for f in range(8):
        F = Frame(pal)
        for k in range(11):
            a = ph[k][1] + f * 0.55
            rise = (f * 2.6 + ph[k][0]) % 26
            r = ph[k][2]
            x = 16 + math.cos(a) * r
            y = 30 - rise
            front = math.sin(a) > 0
            if f >= 6 and k % 2:
                continue
            c1, c2 = ("flower_rose", "white") if front else ("roof_hi", "flower_rose")
            F.set(x, y, c1); F.set(x + 1, y, c2 if front else c1); F.set(x, y - 1, c1 if (k + f) % 2 else c2)
        # leaf bits + a healing cross that blooms at the top
        for k in range(3):
            a = k * 2.1 - f * 0.4
            F.set(16 + math.cos(a) * 4, 26 - (f * 3 + k * 5) % 20, "grass_hi")
        if 3 <= f <= 6:
            s = 1 if f in (3, 6) else 2
            F.star(16, 6, s, "white", "flower_rose")
        out.append(F)
    return out


def hearth_flame(pal, seed):
    out = []
    for f in range(8):
        F = Frame(pal)
        ph = f / 8 * math.tau
        for y in range(10, 30):
            t = (30 - y) / 20                     # 0 bottom .. 1 tip
            half = (5.2 * (1 - t) ** 0.8) + 0.6
            lean = math.sin(ph + t * 3.2) * 1.6 * t
            cx = 15.5 + lean
            for x in range(CELL):
                d = abs(x - cx)
                if d > half:
                    continue
                if t > 0.85 and (x + y + f) % 2:
                    continue                      # dithered tip
                q = d / half
                c = "white" if (q < 0.25 and t < 0.45) else "lamp" if q < 0.5 and t < 0.7 else \
                    "flower_gold" if q < 0.8 else "roof_hi"
                F.set(x, y, c)
        # logs
        for x in range(9, 23):
            F.set(x, 30, "timber_lo" if x % 5 else "timber")
            F.set(x, 29, "timber" if x not in (15, 16) else F.get(x, 29))
        # an ember rising
        ey = 9 - (f % 4) * 2
        F.set(16 + (f % 3) - 1, ey, "lamp" if f % 2 else "flower_gold")
        out.append(F)
    return out


def frost_puff(pal, seed):
    out = []
    R = rng(seed, "frost")
    lobes = [(R.uniform(-6, 6), R.uniform(-4, 3), R.uniform(3, 5)) for _ in range(5)]
    for f in range(8):
        F = Frame(pal)
        g = 0.45 + f * 0.13
        for (lx, ly, lr) in lobes:
            r = lr * g
            for y in range(CELL):
                for x in range(CELL):
                    d = math.hypot(x - (16 + lx * g), (y - (20 + ly * g - f * 0.7)) * 1.1)
                    if d > r:
                        continue
                    if f >= 4 and R.random() < 0.2 * (f - 3) * (0.5 + d / r):
                        continue                  # seeded speckle dissolve, rim first
                    lit = (x - 16) + (y - 18) < -2
                    F.set(x, y, "white" if lit or d < r * 0.4 else "sky" if d < r * 0.8 else "flower_blue")
        for k in range(5):                       # ice glints at the rim
            a = k * 1.3 + f * 0.25
            r = 4 + f * 1.4
            if (k + f) % 3 == 0 and f < 7:
                F.star(16 + math.cos(a) * r, 19 + math.sin(a) * r * 0.8, 1 if f < 5 else 0, "white", "sky")
        out.append(F)
    return out


def leaf_gust(pal, seed):
    out = []
    leaf_cols = [("grass_hi", "grass"), ("flower_gold", "timber_hi"), ("grass", "moss"), ("roof_hi", "flower_gold")]
    for f in range(8):
        F = Frame(pal)
        # wind streaks: two arcs that sweep left to right
        for s in range(2):
            a0 = -2.6 + f * 0.45 + s * 0.9
            if f < 7:
                for i in range(9):
                    a = a0 + i * 0.12
                    r = 9 - s * 3
                    if i % 3 != 2:
                        F.set(16 + math.cos(a) * r + (f - 3) * 0.8, 18 + math.sin(a) * r * 0.55, "white" if s == 0 else "plaster_hi")
        for k in range(7):
            a = k * 0.9 + f * 0.6
            r = 4 + k * 1.2
            x = 16 + math.cos(a) * r + (f - 3.5) * 1.1
            y = 20 + math.sin(a) * r * 0.5 - k * 0.8
            if f == 7 and k % 2:
                continue
            c1, c2 = leaf_cols[k % 4]
            F.set(x, y, c1); F.set(x + (1 if (k + f) % 2 else -1), y, c2); F.set(x, y + (1 if f % 2 else -1), c2)
        out.append(F)
    return out


def light_orb(pal, seed):
    out = []
    for f in range(6):
        F = Frame(pal)
        bob = [0, -1, -1, 0, 1, 1][f]
        if f in (2, 3):
            F.ring(16, 16 + bob, 7 + (f - 2) * 2, 7 + (f - 2) * 2, "flower_gold" if f == 2 else "lamp", dots=2)
        F.disk(16, 16 + bob, 4.2, ["white", "white", "lamp", "flower_gold"])
        F.set(14, 14 + bob, "white"); F.set(15, 13 + bob, "white")
        for k in range(2):
            a = f / 6 * math.tau + k * math.pi
            F.star(16 + math.cos(a) * 8, 16 + bob + math.sin(a) * 4, 1 if k == 0 else 0, "white", "flower_rose")
        out.append(F)
    return out


def rune_circle(pal, seed):
    out = []
    sq = DECAL_SQUASH
    for f in range(8):
        F = Frame(pal)
        rx, ry = 14.5, 14.5 * sq
        frac = min(1.0, (f + 1) / 4)
        F.ring(16, 16, rx, ry, "flower_gold", frac, start=-math.pi / 2)
        F.ring(16, 16, rx - 1, ry - 0.8, "lamp", frac, start=-math.pi / 2, dots=2)
        if f >= 2:
            F.ring(16, 16, rx - 4.5, ry - 4.5 * sq, "flower_rose" if f % 2 else "flower_gold", 1.0, start=f * 0.3, dots=3)
        if f >= 3:
            rot = (f - 3) * (math.tau / 24)
            for k in range(6):                       # little rune ticks between the rings
                a = rot + k * math.tau / 6
                x, y = 16 + math.cos(a) * (rx - 2.3), 16 + math.sin(a) * (ry - 1.4)
                F.set(x, y, "white"); F.set(x + 1, y, "lamp"); F.set(x, y - 1, "lamp")
            F.star(16, 16, 1 if f % 2 else 2, "white", "flower_gold")
        out.append(F)
    return out


def bolt(pal, seed):
    out = []
    for f in range(6):
        F = Frame(pal)
        a = f / 6 * math.tau
        F.disk(16, 16, 2.6, ["white", "lamp", "flower_gold"])
        for k in range(4):                          # spinning star arms
            b = a + k * math.pi / 2
            for r in range(3, 7):
                if r == 6 and k % 2:
                    continue
                F.set(16 + math.cos(b) * r, 16 + math.sin(b) * r, "lamp" if r < 5 else "flower_gold")
        for k in range(3):                          # sparkle trail all round (direction-free)
            b = -a * 1.3 + k * math.tau / 3
            F.set(16 + math.cos(b) * 9, 16 + math.sin(b) * 9, "flower_rose" if k % 2 else "white")
        out.append(F)
    return out


def impact(pal, seed):
    out = []
    for f in range(6):
        F = Frame(pal)
        if f == 0:
            F.disk(16, 18, 3, ["white", "lamp"])
        if 1 <= f <= 3:
            n = 8
            ln = [0, 9, 11, 12][f]
            st = [0, 2, 5, 8][f]
            for k in range(n):
                b = k * math.tau / n + 0.2
                for r in range(st, ln):
                    if f == 3 and r % 2:
                        continue
                    F.set(16 + math.cos(b) * r, 18 + math.sin(b) * r * 0.8, "white" if r < st + 2 else "lamp" if r < ln - 2 else "flower_gold")
        if f in (2, 3, 4):
            rr = [0, 0, 6, 9, 11][f]
            F.ring(16, 18, rr, rr * 0.8, "flower_gold" if f < 4 else "roof_hi", dots=1 if f == 2 else 2)
        if f >= 4:
            for k in range(6 if f == 4 else 3):
                b = k * 1.1 + f
                F.set(16 + math.cos(b) * (8 + f), 18 + math.sin(b) * (6 + f) - (f - 3) * 2, "flower_gold" if k % 2 else "white")
        out.append(F)
    return out


# ------------------------------------------------------------------ hero combat spells (Hearthmoor stage 1)
def seed_bomb(pal, seed):
    """Wildcaller: a spinning acorn-seed lobbed forward (projectile -> earth_burst)"""
    out = []
    for f in range(6):
        F = Frame(pal)
        F.disk(16, 16, 3.2, ["grass_hi", "grass", "moss"])
        a = f / 6 * math.tau
        F.set(16 + math.cos(a) * 2, 16 + math.sin(a) * 2, "flower_gold")
        F.set(16, 12, "timber"); F.set(17, 12, "timber_lo"); F.set(16, 11, "leaf_deep")
        for k in range(3):
            b = -a + k * math.tau / 3
            F.set(16 + math.cos(b) * 7, 16 + math.sin(b) * 7, "grass_hi" if k else "flower_gold")
        out.append(F)
    return out


def earth_burst(pal, seed):
    out = []
    R = rng(seed, "earth")
    clods = [(R.uniform(-1, 1), R.uniform(0.4, 1.0), R.choice(["timber", "timber_lo", "moss", "grass", "grass_hi"])) for _ in range(12)]
    for f in range(7):
        F = Frame(pal)
        if f < 2:
            F.disk(16, 27, 4 + f * 3, ["flower_gold", "grass_hi", "grass"], sq=0.45)
        for (vx, vy, c) in clods:
            t = f / 6
            x = 16 + vx * 13 * t
            y = 28 - vy * 22 * t + 26 * t * t
            if y < 31 and (f < 5 or (int(x) + f) % 2):
                F.set(x, y, c); F.set(x + 1, y, c)
        if 2 <= f <= 5:
            F.ring(16, 28, 4 + f * 2, (4 + f * 2) * 0.35, "grass_hi" if f < 4 else "moss", dots=2)
            F.star(16 + (f - 3) * 3, 22 - f, 1, "white", "flower_rose")
        out.append(F)
    return out


def rune_slam(pal, seed):
    """Runeguard: a gold rune shockwave rings out from the shield (ground decal)"""
    out = []
    sq = DECAL_SQUASH
    for f in range(7):
        F = Frame(pal)
        r = 3 + f * 2.1
        F.ring(16, 16, r, r * sq, "white" if f < 2 else "lamp", dots=1 if f < 4 else 2)
        if r > 4:
            F.ring(16, 16, r - 1.5, (r - 1.5) * sq, "flower_gold", dots=2 if f < 5 else 3)
        for k in range(8):
            a = k * math.tau / 8 + f * 0.1
            if f < 5:
                F.set(16 + math.cos(a) * (r + 1), 16 + math.sin(a) * (r + 1) * sq, "white" if k % 2 else "flower_gold")
        if f < 3:
            F.star(16, 16, 2 - f // 2, "white", "lamp")
        out.append(F)
    return out


def rune_trap(pal, seed):
    """Seer: a blue glyph drawn on the ground that arms and flares (ground decal)"""
    out = []
    sq = DECAL_SQUASH
    for f in range(8):
        F = Frame(pal)
        frac = min(1.0, (f + 1) / 3)
        F.ring(16, 16, 11, 11 * sq, "flower_blue", frac, start=-math.pi / 2)
        F.ring(16, 16, 10, 10 * sq - 0.6, "sky", frac, start=-math.pi / 2, dots=2)
        if f >= 2:
            for k in range(3):                       # triangle glyph
                a0 = -math.pi / 2 + k * math.tau / 3 + f * 0.05
                a1 = a0 + math.tau / 3
                F.line(16 + math.cos(a0) * 8, 16 + math.sin(a0) * 8 * sq, 16 + math.cos(a1) * 8, 16 + math.sin(a1) * 8 * sq,
                       "sky" if f % 2 else "white")
            F.set(16, 16, "white")
        if f >= 6:
            F.ring(16, 16, 13, 13 * sq, "white", dots=2)
        out.append(F)
    return out


def glyph_burst(pal, seed):
    """the Seer's trap (and the wraith's death) going off: a pillar of cold blue light"""
    out = []
    for f in range(6):
        F = Frame(pal)
        w = [2, 4, 5, 4, 2, 1][f]
        top = [20, 6, 2, 4, 10, 18][f]
        for y in range(top, 31):
            for x in range(16 - w, 16 + w + 1):
                d = abs(x - 16) / max(1, w)
                if f >= 4 and (x + y) % 2:
                    continue
                F.set(x, y, "white" if d < 0.35 else "sky" if d < 0.75 else "flower_blue")
        if 1 <= f <= 4:
            F.ring(16, 29, 6 + f * 2, (6 + f * 2) * 0.35, "sky" if f < 3 else "flower_blue", dots=2)
        out.append(F)
    return out


def sky_strike(pal, seed):
    """Stormborn chain lightning: a jagged bolt from the sky onto one target"""
    out = []
    R = rng(seed, "strike")
    path = [16]
    for _ in range(31):
        path.append(max(10, min(22, path[-1] + R.choice([-1, 0, 0, 1]))))
    for f in range(6):
        F = Frame(pal)
        if f in (0, 1, 3):
            for y in range(0 if f != 3 else 8, 31):
                x = path[y] + (1 if f == 3 and y % 6 < 3 else 0)
                F.set(x, y, "white"); F.set(x + 1, y, "flower_gold" if y % 3 else "lamp")
            for (y0, d) in ((8, -1), (15, 1), (22, -1)):
                for k in range(5):
                    F.set(path[y0] + d * (k + 1), y0 + k, "lamp" if k < 4 else "flower_gold")
        if f in (1, 2, 4):
            F.disk(16, 29, 4 + f, ["white", "flower_gold", "lamp"], sq=0.4)
        if f >= 4:
            for k in range(5):
                a = k * 1.3 + f
                F.set(16 + math.cos(a) * (7 + f), 28 - abs(math.sin(a)) * (3 + f), "flower_gold" if k % 2 else "white")
        out.append(F)
    return out


def bloom_ring(pal, seed):
    """Grovekeeper bloom: a ring of opening flowers and petals around the caster (ground decal)"""
    out = []
    sq = DECAL_SQUASH
    cols = ["flower_rose", "flower_gold", "flower_blue", "white"]
    for f in range(8):
        F = Frame(pal)
        r = min(13, 4 + f * 2)
        F.ring(16, 16, r, r * sq, "grass_hi", dots=2)
        F.ring(16, 16, r - 1, (r - 1) * sq, "grass", dots=3)
        for k in range(8):
            a = k * math.tau / 8 + f * 0.08
            x, y = 16 + math.cos(a) * r, 16 + math.sin(a) * r * sq
            c = cols[k % 4]
            if f >= 2:
                F.set(x, y, c); F.set(x - 1, y, c); F.set(x + 1, y, c); F.set(x, y - 1, c)
                F.set(x, y, "flower_gold" if c != "flower_gold" else "white")
        out.append(F)
    return out


def ember_slash(pal, seed):
    """Cinderknight: a spinning crescent of fire flung forward (projectile -> ember_pop)"""
    out = []
    for f in range(6):
        F = Frame(pal)
        a = f / 6 * math.tau
        for k in range(14):
            b = a + k * 0.19
            r = 8 - abs(k - 7) * 0.35
            for dr in (0, 1, 2):
                c = "white" if dr == 1 and 4 < k < 11 else "lamp" if dr == 1 else "flower_gold" if dr == 0 else "roof_hi"
                F.set(16 + math.cos(b) * (r - dr), 16 + math.sin(b) * (r - dr) * 0.8, c)
        F.disk(16, 16, 1.5, ["white", "lamp"])
        out.append(F)
    return out


def ember_pop(pal, seed):
    out = []
    for f in range(6):
        F = Frame(pal)
        r = [3, 5, 7, 8, 9, 9][f]
        if f < 3:
            F.disk(16, 22, r, ["white", "lamp", "flower_gold", "roof_hi"])
        for k in range(8):
            a = k * math.tau / 8 + 0.3
            rr = r + 2
            if f >= 3 and (k + f) % 2:
                continue
            F.set(16 + math.cos(a) * rr, 22 + math.sin(a) * rr * 0.8 - f, "lamp" if k % 2 else "roof_hi")
        if f >= 3:
            for k in range(3):
                F.set(13 + k * 3, 14 - f + k, "stone" if (k + f) % 2 else "stone_lo")
        out.append(F)
    return out


def coldfire_bolt(pal, seed):
    """the wraith's cold-fire orb (projectile -> frost_puff)"""
    out = []
    for f in range(6):
        F = Frame(pal)
        F.disk(16, 16, 3.6, ["white", "sky", "flower_blue"])
        a = f / 6 * math.tau
        for k in range(5):
            b = a + k * math.tau / 5
            r = 5 + (k + f) % 2
            F.set(16 + math.cos(b) * r, 16 + math.sin(b) * r, "sky" if k % 2 else "flower_blue")
            F.set(16 + math.cos(b) * (r + 2), 16 + math.sin(b) * (r + 2), "flower_blue" if (k + f) % 3 == 0 else None)
        F.set(15, 15, "white")
        out.append(F)
    return out


def hit_spark(pal, seed):
    """a weapon hit: a small crisp star that pops and scatters"""
    out = []
    for f in range(5):
        F = Frame(pal)
        if f == 0:
            F.star(16, 20, 3, "white", "white")
        elif f == 1:
            F.star(16, 20, 4, "white", "lamp")
            for k in range(4):
                a = k * math.tau / 4 + math.pi / 4
                F.set(16 + math.cos(a) * 3, 20 + math.sin(a) * 3, "lamp")
        else:
            for k in range(6):
                a = k * math.tau / 6 + f
                r = 3 + f * 2
                if (k + f) % 2 or f < 4:
                    F.set(16 + math.cos(a) * r, 20 + math.sin(a) * r * 0.8, "flower_gold" if f > 2 else "lamp")
        out.append(F)
    return out


def summon_poof(pal, seed):
    """a summon arriving or leaving: a ring of glints and a little dust"""
    out = []
    for f in range(7):
        F = Frame(pal)
        r = 3 + f * 1.8
        if f < 5:
            F.ring(16, 27, r, r * 0.4, "plaster_hi" if f < 3 else "plaster_lo", dots=2)
        for k in range(6):
            a = k * math.tau / 6 + f * 0.4
            y = 26 - f * 2.5 + math.sin(a) * 2
            if (k + f) % 2 or f < 3:
                F.star(16 + math.cos(a) * (4 + f), y, 1 if f < 4 else 0, "white", "lamp" if k % 2 else "flower_rose")
        out.append(F)
    return out


# ------------------------------------------------------------------ glow pass (Hearthmoor stage 2)
def _outline(F, ink="ink"):
    """1 px ink outline around everything drawn so far (4-neighbour)."""
    pts = [(x, y) for y in range(CELL) for x in range(CELL) if F.p[y][x] is None and any(
        F.get(x + dx, y + dy) not in (None, ink) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for x, y in pts:
        F.set(x, y, ink)


def light_pool(pal, seed):
    """A short-lived pool of light on the ground under a spell: dithered dots, densest in the middle."""
    out = []
    sq = DECAL_SQUASH
    R = rng(seed, "pool")
    jit = [[R.random() for _ in range(CELL)] for _ in range(CELL)]
    for f in range(6):
        F = Frame(pal)
        grow = min(1.0, (f + 1) / 3)
        rx = 13.5 * grow
        for y in range(CELL):
            for x in range(CELL):
                d = math.hypot(x - 16, (y - 16) / sq) / max(rx, 0.01)
                if d > 1:
                    continue
                dens = 0.95 * (1 - d) ** 0.9
                if (x + y + f) % 2 == 0 and jit[y][x] < dens:
                    F.set(x, y, "white" if d < 0.3 else "lamp" if d < 0.6 else "flower_gold")
        F.ring(16, 16, rx, rx * sq, "flower_gold", 1.0, start=f * 0.21, dots=3)
        out.append(F)
    return out


def glitter(pal, seed):
    """Sparse twinkling motes that drift up out of a light pool."""
    out = []
    R = rng(seed, "glitter")
    motes = [(5 + R.random() * 22, 10 + R.random() * 20, R.randrange(8), R.choice(["white", "lamp", "flower_rose", "sky"]))
             for _ in range(11)]
    for f in range(8):
        F = Frame(pal)
        for k, (x, y, ph, c) in enumerate(motes):
            b = (f + ph) % 8                    # 0..7 twinkle cycle: off, dot, star, dot, off ...
            yy = y - ((f + ph) % 8) * 0.75
            if b in (1, 3):
                F.set(x, yy, c)
            elif b == 2:
                F.star(x, yy, 1, "white", c if c != "white" else "lamp")
        out.append(F)
    return out


def coldfire_pool(pal, seed):
    """Sefa's lantern pool (Hearthmoor night merchant): a neon-blue cold-fire pool of light on the cobbles.
    Dithered palette pixels only (no bloom): white core, sky / flower_blue body, a flickering cloth-blue rim."""
    out = []
    sq = DECAL_SQUASH
    R = rng(seed, "coldpool")
    jit = [[R.random() for _ in range(CELL)] for _ in range(CELL)]
    for f in range(6):
        F = Frame(pal)
        fl = [1.0, 0.94, 0.98, 0.9, 1.0, 0.96][f]           # the cold flame breathes: the pool's edge flickers
        rx = 15.0 * fl
        for y in range(CELL):
            for x in range(CELL):
                d = math.hypot(x - 16, (y - 16) / sq) / rx
                if d > 1:
                    continue
                dens = 1.0 * (1 - d) ** 0.7 + 0.12
                if d < 0.3 or ((x + y + f) % 2 == 0 and jit[y][x] < dens):   # a solid sky-blue heart, white flecks dancing in it
                    core = "white" if (x + 2 * y + f) % 3 == 0 else "sky"
                    F.set(x, y, core if d < 0.3 else "sky" if d < 0.55 else "flower_blue" if d < 0.82 else "cloth")
        F.ring(16, 16, rx, rx * sq, "flower_blue", 1.0, start=f * 0.17, dots=4)
        F.ring(16, 16, rx * 0.62, rx * 0.62 * sq, "sky", 1.0, start=0.5 + f * 0.23, dots=3)
        out.append(F)
    return out


def coldfire_motes(pal, seed):
    """Cold-fire flicker motes: little blue flames / sparks drifting up out of a lantern pool."""
    out = []
    R = rng(seed, "coldmotes")
    motes = [(6 + R.random() * 20, 14 + R.random() * 16, R.randrange(8), R.choice(["sky", "flower_blue", "white", "sky"]))
             for _ in range(9)]
    for f in range(8):
        F = Frame(pal)
        for k, (x, y, ph, c) in enumerate(motes):
            b = (f + ph) % 8
            yy = y - b * 1.1
            if b in (1, 4):
                F.set(x, yy, c)
            elif b in (2, 3):                    # a two-pixel flame: blue tongue, white tip
                F.set(x, yy, c if c != "white" else "sky"); F.set(x, yy - 1, "white")
            elif b == 5:
                F.star(x, yy, 1, "white", "sky")
        out.append(F)
    return out


def spring_bubbles(pal, seed):
    """Toadstool Hollows' hidden spring: round glowing bubbles rising out of the water, wobbling, popping at the top.
    1 px ring bubbles (sky rim, white glint) and a few solid motes; palette pixels only."""
    out = []
    R = rng(seed, "bubbles")
    bub = [(5 + R.random() * 22, 26 + R.random() * 4, R.randrange(10), R.choice([1, 1, 2])) for _ in range(8)]
    for f in range(10):
        F = Frame(pal)
        for x0, y0, ph, sz in bub:
            b = (f + ph) % 10
            y = y0 - b * 2.4
            x = x0 + (1 if (b // 2) % 2 else 0)
            if b == 9:                                            # pop: four sparkle pixels
                for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    F.set(x + dx * 2, y + dy * 2, "white")
            elif sz == 1:
                F.set(x, y, "white" if b % 3 == 0 else "sky")
                F.set(x, y + 1, "flower_blue")
            else:
                F.ring(x, y, 1.6, 1.6, "sky", 1.0)
                F.set(x - 1, y - 1, "white")
        out.append(F)
    return out


def coldfire_flame(pal, seed):
    """A dark-hour brazier's neon-blue cold fire: a tall flickering tongue (cloth-blue rim, flower_blue body, sky heart,
    white core) with sparks leaving the tip; palette pixels, no bloom."""
    out = []
    R = rng(seed, "coldflame")
    for f in range(6):
        F = Frame(pal)
        sway = [0, 1, 1, 0, -1, -1][f]
        hgt = [17, 19, 18, 20, 18, 19][f]
        for y in range(31, 31 - hgt, -1):
            k = (31 - y) / hgt                                    # 0 at the coals, 1 at the tip
            hw = 5.5 * (1 - k) ** 0.8 * (1 + 0.25 * math.sin(k * 6 + f))
            cx = 16 + sway * k * 2
            for x in range(int(cx - hw - 1), int(cx + hw + 2)):
                d = abs(x - cx) / max(0.6, hw)
                if d > 1:
                    continue
                c = "white" if d < 0.3 and k < 0.55 else "sky" if d < 0.6 else "flower_blue" if d < 0.88 else "cloth"
                F.set(x, y, c)
        for k in range(3):
            sy = 31 - hgt - 2 - ((f + k * 2) % 6) * 1.5
            F.set(16 + sway * 2 + R.choice([-2, -1, 1, 2]), sy, R.choice(["sky", "white"]))
        out.append(F)
    return out


def toadstools(pal, seed):
    """Three red-and-white toadstools whose spots glow at night (looping twinkle + a drifting spore)."""
    out = []
    caps = [(14, 19, 7.0, 4.5, 30), (23.5, 24, 4.2, 2.8, 30), (6.5, 26, 3.2, 2.2, 30)]   # cx, cy, rx, ry, ground
    spots = [(10, 17), (13, 15), (17, 16), (19, 18), (12, 19), (15, 18), (22, 22), (25, 23), (6, 25), (8, 18)]
    for f in range(4):
        F = Frame(pal)
        for x in range(3, 29):                                   # grass tuft at the base
            if (x * 7) % 5 < 3:
                F.set(x, 30, "moss"); F.set(x, 29, "grass" if x % 3 else None)
        for cx, cy, rx, ry, gy in caps:
            sw = max(1, int(rx * 0.35))
            for y in range(int(cy), gy):                         # stem
                for x in range(int(cx - sw), int(cx + sw) + 1):
                    F.set(x, y, "plaster_lo" if x >= cx + sw - 0.5 else "plaster_hi" if x <= cx - sw + 0.5 else "plaster")
            for y in range(int(cy - ry), int(cy) + 1):           # dome cap
                for x in range(int(cx - rx), int(cx + rx) + 1):
                    if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                        top = (y - (cy - ry)) / max(ry, 0.01)
                        side = (x - cx) / rx
                        F.set(x, y, "roof" if y >= cy - 0.5 else "flower_rose" if top < 0.35 and -0.6 < side < 0.1 else "roof_hi")
        for k, (sx, sy) in enumerate(spots):                     # white spots (the glowing bit)
            if F.get(sx, sy) in ("roof", "roof_hi", "roof_lo", "flower_rose"):
                on = (k + f) % 4 != 0
                F.set(sx, sy, "white" if on else "plaster_hi")
                if k < 3:
                    F.set(sx + 1, sy, "white" if on else "plaster")
        _outline(F)
        # a spore drifting up (no outline: a single lit pixel like the sparkles)
        F.set(20 - f, 9 - f * 1.5, "flower_rose" if f % 2 else "white")
        F.set(9 + f * 0.5, 12 - f, "lamp" if f % 2 == 0 else None)
        out.append(F)
    return out


def garden_plot(pal, seed):
    """A small glow-garden bed (ground decal): a timber-edged rectangle of dark tilled soil with three furrows."""
    F = Frame(pal)
    sq = DECAL_SQUASH
    x0, x1 = 3, 28
    y0, y1 = int(16 - 9 * sq), int(16 + 9 * sq)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            edge = x in (x0, x1) or y in (y0, y1)
            if edge:
                F.set(x, y, "timber_hi" if y == y0 else "timber_lo" if y == y1 else "timber")
            else:
                fur = (x - x0) % 8
                F.set(x, y, "shadow" if fur in (0, 1) else "timber_lo" if (x * 3 + y) % 5 else "stone_lo")
    for x in (x0, x1):                                   # corner pegs
        F.set(x, y0 - 1, "timber_hi"); F.set(x, y1 + 1, "timber_lo")
    return [F]


def _stem(F, cx, top, leaf=True, sway=0):
    for y in range(31, top, -1):
        F.set(cx + (sway if y < top + 4 else 0), y, "moss" if y > 27 else "grass")
    if leaf:
        for dx, dy, c in ((-1, 26, "grass"), (-2, 25, "grass_hi"), (-3, 25, "grass"), (1, 23, "grass"), (2, 22, "grass_hi"), (3, 22, "grass")):
            F.set(cx + dx, dy, c)


def glowplant_seed(pal, seed):
    """A planted glow seed: a little soil mound with a faint gold hum (a pixel twinkle)."""
    out = []
    for f in range(4):
        F = Frame(pal)
        for x in range(12, 21):
            h = 2 if 14 <= x <= 18 else 1
            for y in range(31 - h, 32):
                F.set(x, y, "timber" if y < 31 else "timber_lo")
        _outline(F)
        F.set(16, 28 - (f % 2), "flower_gold" if f % 2 else "lamp")
        if f == 2:
            F.set(15, 27, "white")
        out.append(F)
    return out


def glowplant_sprout(pal, seed):
    """A glow sprout: two leaves and a curled tip whose bud glows (gold-white twinkle)."""
    out = []
    for f in range(4):
        F = Frame(pal)
        sway = [0, 0, 1, 0][f]
        _stem(F, 16, 21, leaf=True, sway=sway)
        _outline(F)
        F.set(16 + sway, 20, "lamp"); F.set(16 + sway, 19, "white" if f % 2 == 0 else "flower_gold")
        out.append(F)
    return out


def glowplant_coldfire(pal, seed):
    """A cold-fire bloom: a tall stem holding a neon-blue cold-fire flower (cloth rim, flower_blue petals, sky heart,
    white core) that flickers, with sparks drifting off it."""
    out = []
    R = rng(seed, "gp_cold")
    for f in range(6):
        F = Frame(pal)
        _stem(F, 16, 14)
        fl = [0, 1, 0, -1, 0, 1][f]
        for y in range(5, 17):
            for x in range(9, 24):
                d = math.hypot((x - 16) / 6.2, (y - 11 - fl * 0.3) / 5.2)
                if d > 1:
                    continue
                k = (y - 5) / 12
                c = "white" if d < 0.25 else "sky" if d < 0.5 else "flower_blue" if d < 0.82 else "cloth"
                if d > 0.82 and (x + y + f) % 3 == 0 and k < 0.4:
                    continue                                      # ragged flame-tongue petal tips
                F.set(x, y, c)
        _outline(F)
        for k in range(3):
            sy = 4 - ((f + k * 2) % 6) * 0.8
            F.set(16 + R.choice([-4, -2, 2, 4]), sy, R.choice(["sky", "white"]))
        out.append(F)
    return out


def glowplant_violet(pal, seed):
    """A violet glowbell: three drooping neon-violet bells (dark-violet rim, violet body, lilac highlight, white glints
    pulsing at the mouths) on arching green stalks."""
    out = []
    bells = [(11, 12), (21, 10), (16, 7)]
    for f in range(6):
        F = Frame(pal)
        _stem(F, 16, 9)
        for x in range(11, 22):                                   # arching stalks to the bells
            F.set(x, 9 + abs(x - 16) // 3, "grass")
        for bx, by in bells:
            for y in range(by, by + 6):
                w = 1 + (y - by) // 2
                for x in range(bx - w, bx + w + 1):
                    hi = x == bx - w + 1 or (x == bx and y == by)
                    F.set(x, y, "neon_violet_hi" if hi else "neon_violet_lo" if x == bx + w else "neon_violet")
            for x in range(bx - 3, bx + 4):
                F.set(x, by + 6, "neon_violet_lo")
        _outline(F)
        for k, (bx, by) in enumerate(bells):
            on = (f + k * 2) % 6 < 4
            F.set(bx, by + 6, "white" if on else "neon_violet_hi")
            if on and (f + k) % 3 == 0:
                F.set(bx, by + 8, "neon_violet_hi")
        out.append(F)
    return out


def glowplant_toadcap(pal, seed):
    """A red glow toadstool grown from a glow seed: a saturated neon-red dome (deeper red rim, a bright red sheen),
    crisp white spots that always stay white (a glint pixel twinkles beside them), a pale cream stem."""
    out = []
    spots = [(11, 14), (16, 11), (21, 14), (14, 17), (19, 17), (16, 15)]
    for f in range(4):
        F = Frame(pal)
        for y in range(19, 31):
            for x in range(14, 19):
                F.set(x, y, "plaster_lo" if x == 18 else "plaster_hi" if x == 14 else "plaster")
        for x in range(10, 23):                                   # grass at the foot
            if (x * 5) % 3:
                F.set(x, 31, "moss")
        for y in range(9, 20):
            for x in range(7, 26):
                if ((x - 16) / 9) ** 2 + ((y - 19) / 10) ** 2 <= 1.0:
                    sheen = (x - 12) ** 2 + (y - 12) ** 2 < 6
                    F.set(x, y, "neon_red_lo" if y >= 18 else "neon_red_hi" if sheen else "neon_red")
        for sx, sy in spots:                                      # crisp 2x2 white spots
            for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
                if F.get(sx + dx, sy + dy) in ("neon_red", "neon_red_hi", "neon_red_lo"):
                    F.set(sx + dx, sy + dy, "white")
        _outline(F)
        gx, gy = spots[f % len(spots)]
        F.set(gx - 1, gy - 1, "plaster_hi")                       # a twinkle beside one spot
        F.set(9 + f, 6 - f, "neon_red_hi" if f % 2 else "white")  # a drifting spore
        out.append(F)
    return out


def _bloom_pool(pal, seed, cols, tag):
    """A glow-bloom's night pool on the ground: a dithered disc in the bloom's neon, densest at the heart."""
    out = []
    sq = DECAL_SQUASH
    R = rng(seed, tag)
    jit = [[R.random() for _ in range(CELL)] for _ in range(CELL)]
    for f in range(6):
        F = Frame(pal)
        rx = 13.5 * [1.0, 0.95, 0.98, 0.92, 1.0, 0.96][f]
        for y in range(CELL):
            for x in range(CELL):
                d = math.hypot(x - 16, (y - 16) / sq) / rx
                if d > 1:
                    continue
                if d < 0.22 or ((x + y + f) % 2 == 0 and jit[y][x] < 0.95 * (1 - d) ** 0.8 + 0.08):
                    F.set(x, y, cols[0] if d < 0.22 else cols[1] if d < 0.55 else cols[2])
        F.ring(16, 16, rx, rx * sq, cols[2], 1.0, start=f * 0.19, dots=4)
        out.append(F)
    return out


def violet_pool(pal, seed):
    return _bloom_pool(pal, seed, ["neon_violet_hi", "neon_violet", "neon_violet_lo"], "vpool")


def red_pool(pal, seed):
    return _bloom_pool(pal, seed, ["neon_red_hi", "neon_red", "neon_red_lo"], "rpool")



def sky_lantern(pal, seed):
    """Lantern Eve (Hearthmoor opening): a paper sky lantern rising on its own warm air. A slightly taller rounded body
    of cream-gold paper lit from inside (white-hot near the flame, cream above, gold at the shoulders), soft paper
    ribs, a bright little flame in the bottom opening, a warm glint on the paper and a twinkle drifting round it.
    Palette pixels only, no dark centre and no bloom."""
    out = []
    R = rng(seed, "skylan")
    twinkles = [(9, 11), (23, 9), (22, 18), (10, 19), (24, 13), (8, 15)]
    for f in range(6):
        F = Frame(pal)
        bob = [0, 0, -1, -1, 0, 0][f]
        top, bot = 7 + bob, 23 + bob
        cx = 16
        flame_y = bot - 1
        h = bot - top
        for y in range(top, bot + 1):
            t = (y - top) / h
            if t < 0.3:                                    # rounded crown
                k = (0.3 - t) / 0.3
                half = 5.6 * math.sqrt(max(0.0, 1 - k * k))
            else:                                          # gentle taper to the opening
                half = 5.6 - (t - 0.3) / 0.7 * 2.1
            for x in range(cx - 7, cx + 8):
                e = abs(x - cx) / max(half, 0.5)
                if e > 1.0:
                    continue
                g = math.hypot((x - cx) / 5.6, (y - flame_y) / (h * 0.62))
                if e > 0.8 or (t < 0.3 and e > 0.62 and y == top + int(round(0.3 * h * (1 - math.sqrt(max(0.0, 1 - (e * e))))))):
                    c = "flower_gold" if g < 0.9 else "lamp"   # warm rim: gold low, deeper amber up top
                elif g < 0.22:
                    c = "white"
                elif g < 0.62:
                    c = "plaster_hi"
                elif g < 0.95:
                    c = "plaster_hi" if (x + y) % 2 else "flower_gold"
                else:
                    c = "flower_gold"
                F.set(x, y, c)
            # crown outline row
        for x in range(cx - 2, cx + 3):
            F.set(x, top - 1 if abs(x - cx) < 2 else top, "lamp")
        for rx in (cx - 3, cx + 3):                        # soft paper ribs (dithered)
            for y in range(top + 2, bot - 1):
                if (y + f) % 2 == 0 and F.get(rx, y) in ("plaster_hi", "white"):
                    F.set(rx, y, "flower_gold")
        for x in range(cx - 3, cx + 4):                    # the bottom opening: a bamboo hoop
            F.set(x, bot + 1, "timber_hi")
        F.set(cx - 4, bot, "timber_hi"); F.set(cx + 4, bot, "timber_hi")
        fl = [0, 1, 0, 2, 1, 0][f]                         # the little flame, flickering in the opening
        F.set(cx, bot, "white"); F.set(cx, bot + 1, "lamp")
        F.set(cx + (-1 if fl == 1 else 1 if fl == 2 else 0), bot - 1, "white")
        F.set(cx - 1, bot + 1, "flower_gold" if f % 2 else "lamp"); F.set(cx + 1, bot + 1, "lamp" if f % 2 else "flower_gold")
        if f % 3 != 2:
            F.set(cx, bot + 2, "lamp")
        F.set(cx - 3, top + 3, "white"); F.set(cx - 3, top + 4, "white"); F.set(cx - 2, top + 2, "white")   # warm glint
        tx, ty = twinkles[f]                               # a soft twinkle circling the lantern
        F.set(tx, ty + bob, "white"); F.set(tx + 1, ty + bob, "lamp"); F.set(tx - 1, ty + bob, "lamp")
        F.set(tx, ty + bob - 1, "flower_gold"); F.set(tx, ty + bob + 1, "flower_gold")
        out.append(F)
    return out


def rift_tear(pal, seed):
    """Lantern Eve's omen: a large jagged violet-red tear in the air over the moss gate. A black void seam that
    zigzags the full cell with side cracks, neon violet lips, a hard neon-red edge line, red embers off the edge and
    sparks spitting out; it breathes and flickers (no bloom)."""
    out = []
    R = rng(seed, "tear2")
    path = []
    x = 16.0
    for y in range(0, 32):
        if 3 < y < 29:
            x += R.choice((-2, -1, -1, 1, 1, 2)) if y % 2 == 0 else 0
        x = max(10, min(22, x))
        path.append((y, x))
    cracks = []                                            # short side cracks branching off the seam
    for i in (8, 13, 18, 23):
        side = R.choice((-1, 1))
        cracks.append((i, side, R.randrange(3, 6), R.choice((-1, 1))))
    notch = [1.0 + R.choice((-0.3, -0.15, 0.0, 0.0, 0.15, 0.35)) for _ in path]   # fixed jagged lip profile
    sparks = [(R.randrange(4, len(path) - 4), R.choice((-1, 1)), R.randrange(8)) for _ in range(10)]
    for f in range(8):
        F = Frame(pal)
        breathe = [1.0, 1.2, 0.9, 1.35, 1.1, 0.85, 1.25, 1.0][f]
        for i, (y, x) in enumerate(path):
            t = i / (len(path) - 1)
            w = max(0.0, math.sin(t * math.pi)) ** 0.6 * 4.6 * breathe * notch[i]
            for dx in range(-10, 11):
                d = abs(dx) - w
                if d <= -1.0:
                    F.set(x + dx, y, "ink" if (x + dx + 3 * y + f) % 11 else "neon_violet_lo")
                elif d <= 0.0:
                    F.set(x + dx, y, "neon_violet_hi" if (y + f) % 3 == 0 else "neon_violet")
                elif d <= 1.0:
                    F.set(x + dx, y, "neon_red_hi" if (y + f) % 3 == 0 else "neon_red")
                elif d <= 2.0 and (y + dx + f) % 2 == 0:
                    F.set(x + dx, y, "neon_red_lo")
        for (i, side, ln, slope) in cracks:                # side cracks: void line with red neon lips
            y0, x0 = path[i]
            w = max(0.0, math.sin(i / (len(path) - 1) * math.pi)) ** 0.6 * 4.6 * breathe
            for k in range(ln):
                cxk = x0 + side * (w + 1 + k)
                cyk = y0 + slope * (k // 2)
                F.set(cxk, cyk, "neon_violet" if k < ln - 1 else "neon_red_hi")
                F.set(cxk, cyk - 1, "neon_red" if (k + f) % 2 == 0 else None)
                F.set(cxk, cyk + 1, "neon_red_lo" if (k + f) % 2 else None)
        for k, (i, side, ph) in enumerate(sparks):
            b = (f + ph) % 8
            if b > 4:
                continue
            y, x = path[i]
            sx = x + side * (5 + b * 1.6)
            F.set(sx, y - b * 0.6, "neon_red_hi" if b < 2 else "neon_red")
            if b == 1:
                F.set(sx, y - 1.6, "white")
        out.append(F)
    return out


# ------------------------------------------------------------------ Stage 5 part 2: rare auras + random-rift tiers
def _rare_aura(pal, seed, cols):
    """a procedural rare's ground aura in its element colour: a marching dashed outer ring, a dithered inner ring,
    four rune ticks turning the other way and a few glints. Decal (pre-squashed), palette / NEON pixels, no bloom."""
    hi, mid, lo = cols
    out = []
    sq = DECAL_SQUASH
    for f in range(8):
        F = Frame(pal)
        rx, ry = 15.0, 15.0 * sq
        F.ring(16, 16, rx, ry, mid, 1.0, start=f * math.tau / 24, dots=2)
        F.ring(16, 16, rx - 0.8, ry - 0.6, lo, 1.0, start=f * math.tau / 24 + 0.12, dots=3)
        F.ring(16, 16, rx - 4.0, ry - 4.0 * sq, lo, 1.0, start=-f * 0.2, dots=2)
        rot = -f * math.tau / 32
        for k in range(4):
            a = rot + k * math.tau / 4
            x, y = 16 + math.cos(a) * (rx - 2.2), 16 + math.sin(a) * (ry - 1.3)
            F.set(x, y, hi); F.set(x - 1, y, mid); F.set(x + 1, y, mid)
        for k in range(3):
            a = (f * 0.7 + k * 2.1) % math.tau
            r = 6 + (f + k * 3) % 6
            F.set(16 + math.cos(a) * r, 16 + math.sin(a) * r * sq, hi if (f + k) % 2 else mid)
        out.append(F)
    return out


def rare_aura_blue(pal, seed):
    return _rare_aura(pal, seed, ("white", "sky", "flower_blue"))


def rare_aura_violet(pal, seed):
    return _rare_aura(pal, seed, ("neon_violet_hi", "neon_violet", "neon_violet_lo"))


def rare_aura_red(pal, seed):
    return _rare_aura(pal, seed, ("neon_red_hi", "neon_red", "neon_red_lo"))


def _tier_tear(pal, seed, tag, y0, y1, xlo, xhi, wmax, lips, edges, spark):
    """a random-rift tear (Stage 5 part 2) at a given size: a jagged void seam with lips and a hard neon edge line,
    a fixed jagged profile, embers off the edge and sparks; it breathes and flickers (no bloom)"""
    out = []
    R = rng(seed, tag)
    path = []
    x = 16.0
    for y in range(y0, y1 + 1):
        if y0 + 2 < y < y1 - 2 and y % 2 == 0:
            x += R.choice((-2, -1, -1, 1, 1, 2))
        x = max(xlo, min(xhi, x))
        path.append((y, x))
    notch = [1.0 + R.choice((-0.3, -0.15, 0.0, 0.0, 0.15, 0.35)) for _ in path]
    sparks = [(R.randrange(2, len(path) - 2), R.choice((-1, 1)), R.randrange(8)) for _ in range(max(4, len(path) // 3))]
    lip, lip_hi = lips
    edge, edge_hi, edge_lo = edges
    for f in range(8):
        F = Frame(pal)
        breathe = [1.0, 1.2, 0.9, 1.35, 1.1, 0.85, 1.25, 1.0][f]
        for i, (y, x) in enumerate(path):
            t = i / (len(path) - 1)
            w = max(0.0, math.sin(t * math.pi)) ** 0.6 * wmax * breathe * notch[i]
            for dx in range(-10, 11):
                d = abs(dx) - w
                if d <= -1.0:
                    F.set(x + dx, y, "ink" if (x + dx + 3 * y + f) % 11 else lip)
                elif d <= 0.0:
                    F.set(x + dx, y, lip_hi if (y + f) % 3 == 0 else lip)
                elif d <= 1.0:
                    F.set(x + dx, y, edge_hi if (y + f) % 3 == 0 else edge)
                elif d <= 2.0 and (y + dx + f) % 2 == 0:
                    F.set(x + dx, y, edge_lo)
        for (i, side, ph) in sparks:
            b = (f + ph) % 8
            if b > 4:
                continue
            y, x = path[i]
            sx = x + side * (wmax + 1 + b * 1.4)
            F.set(sx, y - b * 0.6, spark if b < 2 else edge)
            if b == 1:
                F.set(sx, y - 1.6, "white")
        out.append(F)
    return out


def rift_tear_minor(pal, seed):
    """tier I (minor) random rift: a small cold-fire tear, violet lips with a neon-blue edge"""
    return _tier_tear(pal, seed, "tearI", 14, 30, 13, 19, 2.6, ("neon_violet", "neon_violet_hi"), ("flower_blue", "sky", "cloth"), "white")


def rift_tear_abyss(pal, seed):
    """tier III (abyssal) random rift: a wide crimson tear, red lips with a violet neon edge and red embers"""
    return _tier_tear(pal, seed, "tearIII", 0, 31, 11, 21, 5.6, ("neon_red", "neon_red_hi"), ("neon_violet", "neon_violet_hi", "neon_red_lo"), "neon_red_hi")


def rift_ring_abyss(pal, seed):
    """the ground ring under an abyssal rift: a dashed crimson rune ring with violet ticks (decal)"""
    out = []
    sq = DECAL_SQUASH
    for f in range(8):
        F = Frame(pal)
        rx, ry = 14.5, 14.5 * sq
        F.ring(16, 16, rx, ry, "neon_red", 1.0, start=f * math.tau / 32, dots=2)
        F.ring(16, 16, rx - 3.5, ry - 3.5 * sq, "neon_red_lo", 1.0, start=-f * math.tau / 32, dots=3)
        for k in range(6):
            a = k * math.tau / 6 + f * 0.1
            F.set(16 + math.cos(a) * (rx - 1.8), 16 + math.sin(a) * (ry - 1.1), "neon_violet_hi" if (k + f) % 2 else "neon_violet")
        out.append(F)
    return out


EFFECTS = {
    "sparkle_burst": dict(fn=sparkle_burst, kind="billboard", fps=14, loop=False, pivot=[16, 31], lift=0.9,
                          glow=True, light={"color": "lamp", "intensity": 7, "range": 4.5, "curve": [1, 0.9, 0.7, 0.5, 0.3, 0.2, 0.1, 0]}),
    "healing_petals": dict(fn=healing_petals, kind="billboard", fps=10, loop=True, pivot=[16, 31], lift=0.0, loops=2,
                           glow=False, light={"color": "flower_rose", "intensity": 3, "range": 3.5, "curve": [0.4, 0.7, 1, 1, 1, 0.8, 0.6, 0.3]}),
    "hearth_flame": dict(fn=hearth_flame, kind="billboard", fps=10, loop=True, pivot=[16, 31], lift=0.0, loops=4,
                         glow=True, light={"color": "lamp", "intensity": 6, "range": 5, "curve": [1, 0.9, 1.05, 0.95, 1, 0.85, 1.1, 0.95]}),
    "frost_puff": dict(fn=frost_puff, kind="billboard", fps=12, loop=False, pivot=[16, 31], lift=0.2,
                       glow=False, light={"color": "sky", "intensity": 3, "range": 3.5, "curve": [1, 0.8, 0.6, 0.4, 0.3, 0.2, 0.1, 0]}),
    "leaf_gust": dict(fn=leaf_gust, kind="billboard", fps=12, loop=False, pivot=[16, 31], lift=0.1, glow=False, light=None),
    "light_orb": dict(fn=light_orb, kind="billboard", fps=8, loop=True, pivot=[16, 24], lift=1.5, loops=5,
                      glow=True, light={"color": "lamp", "intensity": 5, "range": 5, "curve": [1, 1.05, 1.1, 1.05, 1, 0.95]}),
    "rune_circle": dict(fn=rune_circle, kind="decal", fps=8, loop=True, loop_from=4, pivot=[16, 16], lift=0.02, loops=3,
                        glow=True, light={"color": "flower_gold", "intensity": 2.5, "range": 3, "curve": [0.2, 0.4, 0.7, 1, 1, 1, 1, 1]}),
    "bolt": dict(fn=bolt, kind="projectile", fps=14, loop=True, pivot=[16, 16], lift=1.1, speed=7.0, travel=4.0,
                 then="impact", glow=True, light={"color": "lamp", "intensity": 4, "range": 3.5, "curve": [1, 1, 1, 1, 1, 1]}),
    "impact": dict(fn=impact, kind="billboard", fps=14, loop=False, pivot=[16, 26], lift=0.6,
                   glow=True, light={"color": "white", "intensity": 8, "range": 4, "curve": [1, 0.8, 0.5, 0.3, 0.15, 0]}),
    # hero combat spells + enemy / hit effects (Hearthmoor); combat=True keeps them out of the default charm cycle
    "seed_bomb": dict(fn=seed_bomb, kind="projectile", fps=12, loop=True, pivot=[16, 16], lift=1.0, speed=8.0, travel=5.0,
                      then="earth_burst", glow=False, light=None, combat=True),
    "earth_burst": dict(fn=earth_burst, kind="billboard", fps=14, loop=False, pivot=[16, 31], lift=0.0, glow=False,
                        light={"color": "flower_gold", "intensity": 3, "range": 3, "curve": [1, 0.7, 0.4, 0.2, 0.1, 0, 0]}, combat=True),
    "rune_slam": dict(fn=rune_slam, kind="decal", fps=14, loop=False, pivot=[16, 16], lift=0.03, glow=True,
                      light={"color": "lamp", "intensity": 7, "range": 4.5, "curve": [1, 0.9, 0.7, 0.5, 0.3, 0.15, 0]}, combat=True),
    "rune_trap": dict(fn=rune_trap, kind="decal", fps=12, loop=False, pivot=[16, 16], lift=0.03, glow=True,
                      light={"color": "sky", "intensity": 3, "range": 3, "curve": [0.2, 0.4, 0.6, 0.8, 0.8, 0.8, 1, 1]}, combat=True),
    "glyph_burst": dict(fn=glyph_burst, kind="billboard", fps=14, loop=False, pivot=[16, 31], lift=0.0, glow=True,
                        light={"color": "sky", "intensity": 8, "range": 4.5, "curve": [0.6, 1, 1, 0.7, 0.4, 0.1]}, combat=True),
    "sky_strike": dict(fn=sky_strike, kind="billboard", fps=16, loop=False, pivot=[16, 31], lift=0.0, glow=True,
                       light={"color": "white", "intensity": 9, "range": 5, "curve": [1, 1, 0.4, 0.9, 0.3, 0]}, combat=True),
    "bloom_ring": dict(fn=bloom_ring, kind="decal", fps=12, loop=False, pivot=[16, 16], lift=0.03, glow=False,
                       light={"color": "flower_rose", "intensity": 3, "range": 3.5, "curve": [0.3, 0.6, 1, 1, 1, 0.8, 0.5, 0.2]}, combat=True),
    "ember_slash": dict(fn=ember_slash, kind="projectile", fps=16, loop=True, pivot=[16, 16], lift=0.9, speed=10.0, travel=4.5,
                        then="ember_pop", glow=True, light={"color": "lamp", "intensity": 5, "range": 3.5, "curve": [1, 1, 1, 1, 1, 1]}, combat=True),
    "ember_pop": dict(fn=ember_pop, kind="billboard", fps=14, loop=False, pivot=[16, 31], lift=0.0, glow=True,
                      light={"color": "lamp", "intensity": 6, "range": 3.5, "curve": [1, 0.8, 0.5, 0.3, 0.1, 0]}, combat=True),
    "coldfire_bolt": dict(fn=coldfire_bolt, kind="projectile", fps=12, loop=True, pivot=[16, 16], lift=1.0, speed=5.0, travel=7.0,
                          then="frost_puff", glow=True, light={"color": "sky", "intensity": 4, "range": 3.5, "curve": [1, 1, 1, 1, 1, 1]}, combat=True),
    "hit_spark": dict(fn=hit_spark, kind="billboard", fps=18, loop=False, pivot=[16, 26], lift=0.5, glow=True, light=None, combat=True),
    "summon_poof": dict(fn=summon_poof, kind="billboard", fps=12, loop=False, pivot=[16, 31], lift=0.0, glow=False,
                        light={"color": "lamp", "intensity": 3, "range": 3, "curve": [1, 0.8, 0.6, 0.4, 0.2, 0.1, 0]}, combat=True),
    "light_pool": dict(fn=light_pool, kind="decal", fps=8, loop=True, loop_from=3, pivot=[16, 16], lift=0.02, loops=2,
                       glow=True, light=None, combat=True),
    "glitter": dict(fn=glitter, kind="billboard", fps=10, loop=True, pivot=[16, 31], lift=0.0, loops=2, glow=True, light=None, combat=True),
    "coldfire_pool": dict(fn=coldfire_pool, kind="decal", fps=6, loop=True, loop_from=0, pivot=[16, 16], lift=0.02, loops=1,
                          glow=True, light=None, combat=True),
    "coldfire_motes": dict(fn=coldfire_motes, kind="billboard", fps=9, loop=True, pivot=[16, 31], lift=0.0, loops=1, glow=True, light=None, combat=True),
    "spring_bubbles": dict(fn=spring_bubbles, kind="billboard", fps=8, loop=True, pivot=[16, 31], lift=0.0, loops=1, glow=True, light=None, combat=True),
    "coldfire_flame": dict(fn=coldfire_flame, kind="billboard", fps=8, loop=True, pivot=[16, 31], lift=0.0, loops=1, glow=True, light=None, combat=True),
    "garden_plot": dict(fn=garden_plot, kind="decal", fps=1, loop=True, loop_from=0, pivot=[16, 16], lift=0.015, loops=1, glow=False, light=None, combat=True),
    "glowplant_seed": dict(fn=glowplant_seed, kind="billboard", fps=3, loop=True, pivot=[16, 31], lift=0.0, loops=1, glow=True, light=None, combat=True),
    "glowplant_sprout": dict(fn=glowplant_sprout, kind="billboard", fps=3, loop=True, pivot=[16, 31], lift=0.0, loops=1, glow=True, light=None, combat=True),
    "glowplant_coldfire": dict(fn=glowplant_coldfire, kind="billboard", fps=7, loop=True, pivot=[16, 31], lift=0.0, loops=1, glow=True, light=None, combat=True),
    "glowplant_violet": dict(fn=glowplant_violet, kind="billboard", fps=4, loop=True, pivot=[16, 31], lift=0.0, loops=1, glow=True, light=None, combat=True),
    "violet_pool": dict(fn=violet_pool, kind="decal", fps=6, loop=True, loop_from=0, pivot=[16, 16], lift=0.02, loops=1, glow=True, light=None, combat=True),
    "red_pool": dict(fn=red_pool, kind="decal", fps=6, loop=True, loop_from=0, pivot=[16, 16], lift=0.02, loops=1, glow=True, light=None, combat=True),
    "glowplant_toadcap": dict(fn=glowplant_toadcap, kind="billboard", fps=3, loop=True, pivot=[16, 31], lift=0.0, loops=1, glow=True, light=None, combat=True),
    "sky_lantern": dict(fn=sky_lantern, kind="billboard", fps=6, loop=True, pivot=[16, 31], lift=0.0, loops=1, glow=True, light=None, combat=True),
    "rift_tear": dict(fn=rift_tear, kind="billboard", fps=10, loop=True, pivot=[16, 31], lift=0.0, loops=1, glow=True, light=None, combat=True),
    "rare_aura_blue": dict(fn=rare_aura_blue, kind="decal", fps=8, loop=True, loop_from=0, pivot=[16, 16], lift=0.02, loops=1, glow=True, light=None, combat=True),
    "rare_aura_violet": dict(fn=rare_aura_violet, kind="decal", fps=8, loop=True, loop_from=0, pivot=[16, 16], lift=0.02, loops=1, glow=True, light=None, combat=True),
    "rare_aura_red": dict(fn=rare_aura_red, kind="decal", fps=8, loop=True, loop_from=0, pivot=[16, 16], lift=0.02, loops=1, glow=True, light=None, combat=True),
    "rift_tear_minor": dict(fn=rift_tear_minor, kind="billboard", fps=10, loop=True, pivot=[16, 31], lift=0.0, loops=1, glow=True, light=None, combat=True),
    "rift_tear_abyss": dict(fn=rift_tear_abyss, kind="billboard", fps=10, loop=True, pivot=[16, 31], lift=0.0, loops=1, glow=True, light=None, combat=True),
    "rift_ring_abyss": dict(fn=rift_ring_abyss, kind="decal", fps=6, loop=True, loop_from=0, pivot=[16, 16], lift=0.02, loops=1, glow=True, light=None, combat=True),
    "toadstools": dict(fn=toadstools, kind="billboard", fps=3, loop=True, pivot=[16, 31], lift=0.0, loops=1, glow=True, light=None, combat=True),
}
# what the player's spell key cycles through, and what a cast spawns (effect, where)
CAST_SETS = {
    "sparkle_burst": [["sparkle_burst", "front"]],
    "healing_petals": [["rune_circle", "feet"], ["healing_petals", "feet"]],
    "hearth_flame": [["hearth_flame", "front"]],
    "frost_puff": [["frost_puff", "front"]],
    "leaf_gust": [["leaf_gust", "front"]],
    "light_orb": [["light_orb", "front"]],
    "rune_circle": [["rune_circle", "feet"], ["sparkle_burst", "feet"]],
    "bolt": [["bolt", "hands"]],
    # hero first spells (Hearthmoor combat; the game resolves damage, these are the visuals)
    "seed_bomb": [["seed_bomb", "hands"]],
    "rune_slam": [["rune_slam", "feet"], ["impact", "feet"]],
    "rune_trap": [["rune_trap", "front"]],
    "chain_lightning": [["sky_strike", "front"]],
    "bloom": [["bloom_ring", "feet"], ["healing_petals", "feet"]],
    "ember_slash": [["ember_slash", "hands"]],
}
COMBAT_SETS = {"seed_bomb", "rune_slam", "rune_trap", "chain_lightning", "bloom", "ember_slash"}


def build(biome="cozy-village", out="public/art/spells", project=None, seed=1):
    pal = Pal(load_biome(biome, project))
    out = ensure(out)
    names = list(EFFECTS)
    atlas = Image.new("RGBA", (CELL * COLS, CELL * len(names)), (0, 0, 0, 0))
    meta = {"tool": "hd2d spells", "biome": biome, "seed": seed, "image": "spells.png", "cell": CELL,
            "size": [atlas.width, atlas.height], "effects": {}, "cast_sets": CAST_SETS,
            "cycle": [k for k in CAST_SETS if k not in COMBAT_SETS]}
    for row, name in enumerate(names):
        e = EFFECTS[name]
        frames = e["fn"](pal, seed)
        strip = Image.new("RGBA", (CELL * len(frames), CELL), (0, 0, 0, 0))
        fr = []
        for i, F in enumerate(frames):
            im = F.image()
            atlas.paste(im, (i * CELL, row * CELL))
            strip.paste(im, (i * CELL, 0))
            fr.append({"x": i * CELL, "y": row * CELL, "w": CELL, "h": CELL})
        strip.save(out / f"{name}.png")
        light = None
        if e.get("light"):
            light = {**e["light"], "color": pal[e["light"]["color"]]}
        meta["effects"][name] = {
            "row": row, "frames": len(frames), "fps": e["fps"], "loop": e["loop"], "loop_from": e.get("loop_from", 0),
            "loops": e.get("loops", 1), "kind": e["kind"], "pivot": e["pivot"], "lift": e["lift"], "glow": e["glow"],
            "light": light, "speed": e.get("speed"), "travel": e.get("travel"), "then": e.get("then"),
            "strip": f"{name}.png", "frame_list": fr,
            "duration": round(len(frames) / e["fps"] * e.get("loops", 1), 3),
        }
    atlas.save(out / "spells.png")
    write_json(out / "spells.json", meta)
    contact(atlas, names, meta, out / "spells_contact_4x.png")
    return meta


def contact(atlas, names, meta, path, scale=4):
    pad = 130
    big = atlas.resize((atlas.width * scale, atlas.height * scale), Image.NEAREST)
    out = Image.new("RGBA", (big.width + pad, big.height + 28), (46, 52, 84, 255))
    d = ImageDraw.Draw(out)
    for i, n in enumerate(names):
        y = 28 + i * CELL * scale
        if i % 2:
            d.rectangle([0, y, out.width, y + CELL * scale - 1], fill=(56, 62, 98, 255))
        e = meta["effects"][n]
        d.text((6, y + 40), n, fill=(246, 236, 210, 255))
        d.text((6, y + 56), f"{e['kind']} {e['frames']}f {e['fps']}fps", fill=(200, 190, 170, 255))
    d.text((pad + 4, 8), "hd2d spells: 32 px cells, hard alpha, biome palette, nearest 4x", fill=(246, 236, 210, 255))
    out.alpha_composite(big, (pad, 28))
    out.save(path)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="hd2d spells", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--biome", default="cozy-village")
    ap.add_argument("--out", default="public/art/spells")
    ap.add_argument("--project", default=None)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args(argv)
    m = build(a.biome, a.out, a.project, a.seed)
    print(f"spells: {len(m['effects'])} effects ({', '.join(m['effects'])}) -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
