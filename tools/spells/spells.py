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


class Frame:
    def __init__(self, pal):
        self.pal = pal
        self.p = [[None] * CELL for _ in range(CELL)]

    def set(self, x, y, c):
        x, y = int(round(x)), int(round(y))
        if c and 0 <= x < CELL and 0 <= y < CELL:
            self.pal[c]  # raises if the colour is not in the biome
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
                    r, g, b = hex2rgb(self.pal[c])
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
}


def build(biome="cozy-village", out="public/art/spells", project=None, seed=1):
    pal = Pal(load_biome(biome, project))
    out = ensure(out)
    names = list(EFFECTS)
    atlas = Image.new("RGBA", (CELL * COLS, CELL * len(names)), (0, 0, 0, 0))
    meta = {"tool": "hd2d spells", "biome": biome, "seed": seed, "image": "spells.png", "cell": CELL,
            "size": [atlas.width, atlas.height], "effects": {}, "cast_sets": CAST_SETS, "cycle": list(CAST_SETS)}
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
