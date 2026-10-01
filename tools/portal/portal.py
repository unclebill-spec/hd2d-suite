"""hd2d portal: game effect art for cozy HD-2D games (original pixel art, biome palette only).

    hd2d portal --biome cozy-village --out PROJECT/public/art/gamefx

48x48 cells, hard alpha, nearest-neighbour, every pixel a biome colour (no glow halos, no blur):

  portal_vortex   swirling two-arm vortex for the stone-arch gate (billboard, loops)
  portal_ring     rune ring on the ground in front of the gate (ground decal, pre-squashed, loops)
  moonpetal       a glade herb with pale petals and a glint (pickup billboard, loops)
  quest_mark      a parchment "!" tag that bobs over someone who has an errand (billboard, lifted)
  quest_turnin    a gold star tag over someone waiting for your delivery (billboard, lifted)

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
            self.pal[c]
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
                    r, g, b = hex2rgb(self.pal[c])
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


EFFECTS = {
    "portal_vortex": dict(fn=vortex, fps=8, loop=True, kind="billboard", pivot=[24, 47], lift=0.18, glow=True),
    "portal_ring": dict(fn=ring, fps=6, loop=True, kind="decal", pivot=[24, 24], lift=0.02, glow=True),
    "moonpetal": dict(fn=moonpetal, fps=4, loop=True, kind="billboard", pivot=[24, 47], lift=0.0, glow=False),
    "quest_mark": dict(fn=lambda pal, seed: tag(pal, "mark"), fps=3, loop=True, kind="billboard", pivot=[24, 47], lift=2.05, glow=True),
    "quest_turnin": dict(fn=lambda pal, seed: tag(pal, "turnin"), fps=3, loop=True, kind="billboard", pivot=[24, 47], lift=2.05, glow=True),
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
