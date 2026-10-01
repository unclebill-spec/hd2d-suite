"""hd2d particles: cheap pixel particle sheets + emitter presets for the runtime.

    hd2d particles --biome cozy-village --out PROJECT/public/art/particles

Sheet: 16 px cells, 4 frames per row, hard alpha, biome colours only.
  row 0 dust_motes     sunlit motes drifting over the plaza (day)
  row 1 chimney_wisp   rising smoke puffs, grow then dither away (frames follow life)
  row 2 leaf_bits      tumbling leaves under trees
  row 3 lamp_bugs      fireflies around lamps and hedges (dusk / night)
  row 4 lamp_flicker   4-frame lamp glow: 1-2 shade steps of dithered pixels, never a blur halo
  row 5 fireflies      slow blinking green-gold bugs over hedges and grass (dusk / night)
  row 6 petals         falling rose / cream petals, tumbling
  row 7 snowfall       chunky 1-3 px flakes (weather; follows the camera)
  row 8 rain           2-3 px streaks (weather; follows the camera; spawns rain_splash on the floor)
  row 9 rain_splash    4-frame ground ring splash (life)
  row 10 embers        campfire / forge sparks rising and cooling
  row 11 oven_steam    bakery steam puffs, warm cream, dissolve by dither (life)
  row 12 pollen        tiny gold specks drifting in sun (day)
  row 13 fountain_spray droplets thrown up and falling back (gravity + floor)
  row 14 butterflies   2-colour flappers on a meander (day)
  row 15 footstep_dust small dust kick under walking feet (burst by the runtime, life)
Also writes lamp_flicker.png (the native 4-frame strip), particles.json (presets), particles_preview_6x.png.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from PIL import Image, ImageDraw  # noqa: E402

from hd2d_common import Pal, ensure, hex2rgb, load_biome, rng, write_json  # noqa: E402

CELL = 16
ROWS = ["dust_motes", "chimney_wisp", "leaf_bits", "lamp_bugs", "lamp_flicker",
        "fireflies", "petals", "snowfall", "rain", "rain_splash", "embers", "oven_steam", "pollen",
        "fountain_spray", "butterflies", "footstep_dust"]
R = {n: i for i, n in enumerate(ROWS)}


class Cells:
    def __init__(self, pal):
        self.pal = pal
        self.im = Image.new("RGBA", (CELL * 4, CELL * len(ROWS)), (0, 0, 0, 0))
        self.px = self.im.load()

    def set(self, row, f, x, y, c):
        if 0 <= x < CELL and 0 <= y < CELL:
            r, g, b = hex2rgb(self.pal[c])
            self.px[f * CELL + x, row * CELL + y] = (r, g, b, 255)


def motes(C):
    for f in range(4):
        c = ["white", "lamp", "white", "plaster_hi"][f]
        C.set(0, f, 8, 8, c)
        if f in (1, 2):
            C.set(0, f, 7, 8, "flower_gold" if f == 1 else "plaster_hi")
            C.set(0, f, 8, 7, "plaster_hi")
        if f == 2:
            C.set(0, f, 9, 8, "plaster_hi"); C.set(0, f, 8, 9, "plaster_hi")


def wisp(C, seed):
    r = rng(seed, "wisp")
    for f in range(4):
        rad = [2.2, 3.4, 4.6, 5.4][f]
        keep = [1.0, 0.95, 0.7, 0.4][f]
        for y in range(CELL):
            for x in range(CELL):
                d = math.hypot(x - 7.5, (y - 8.5) * 1.1)
                if d > rad:
                    continue
                if f >= 2 and ((x + y + f) % 2 == 0) and d > rad * (0.3 if f == 3 else 0.55):
                    continue  # dithered dissolve
                if r.random() > keep and d > rad * 0.5:
                    continue
                lit = (x - 7.5) + (y - 8.5) < -rad * 0.3
                c = "white" if lit else ("plaster_hi" if d < rad * 0.7 else "stone_hi")
                C.set(1, f, x, y, c)


def leaves(C):
    shapes = [
        [(6, 7, "grass_hi"), (7, 7, "grass"), (8, 8, "grass"), (7, 8, "moss"), (9, 8, "moss")],
        [(7, 6, "grass"), (7, 7, "grass_hi"), (8, 8, "grass"), (8, 9, "moss")],
        [(6, 8, "moss"), (7, 8, "grass"), (8, 8, "grass_hi"), (9, 7, "grass")],
        [(8, 6, "moss"), (8, 7, "grass"), (7, 8, "grass_hi"), (7, 9, "grass")],
    ]
    for f, sh in enumerate(shapes):
        for x, y, c in sh:
            C.set(2, f, x, y, c)


def bugs(C):
    for f in range(4):
        C.set(3, f, 8, 8, "white" if f in (1, 2) else "lamp")
        if f in (1, 2):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                C.set(3, f, 8 + dx, 8 + dy, "lamp" if f == 1 else "flower_gold")
        if f == 2:
            for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
                C.set(3, f, 8 + dx, 8 + dy, "flower_gold")


def flicker(C):
    """Hollow dithered glow ring around the lantern (the lantern mesh shows through the middle)."""
    for f in range(4):
        r_in = [3.0, 3.2, 2.8, 3.1][f]
        r_out = [6.2, 5.6, 6.8, 5.9][f]
        for y in range(CELL):
            for x in range(CELL):
                d = math.hypot(x - 7.5, (y - 7.5) * 1.05)
                if d < r_in or d > r_out:
                    continue
                inner = d < (r_in + r_out) / 2 - 0.4
                if inner:
                    if (x + y + f) % 2 == 0:
                        C.set(4, f, x, y, "lamp")
                else:
                    if (x % 2 == 0 and y % 2 == (f % 2)):
                        C.set(4, f, x, y, "flower_gold")


def fireflies(C):
    r = R["fireflies"]
    for f in range(4):
        on = f in (1, 2)
        C.set(r, f, 8, 8, "flower_gold" if on else "grass_hi")
        if on:
            C.set(r, f, 7, 8, "grass_hi"); C.set(r, f, 9, 8, "grass_hi")
            if f == 2:
                C.set(r, f, 8, 7, "white"); C.set(r, f, 8, 9, "grass_hi")


def petals(C):
    r = R["petals"]
    shapes = [[(7, 8, "flower_rose"), (8, 8, "white"), (8, 7, "flower_rose")],
              [(7, 8, "flower_rose"), (8, 8, "flower_rose")],
              [(8, 7, "white"), (8, 8, "flower_rose"), (7, 9, "flower_rose")],
              [(8, 8, "flower_rose")]]
    for f, sh in enumerate(shapes):
        for x, y, c in sh:
            C.set(r, f, x, y, c)


def snow(C):
    r = R["snowfall"]
    for f in range(4):
        C.set(r, f, 8, 8, "white")
        if f in (1, 3):
            C.set(r, f, 7, 8, "plaster_hi"); C.set(r, f, 9, 8, "plaster_hi")
        if f == 2:
            for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                C.set(r, f, 8 + d[0], 8 + d[1], "plaster_hi")


def rain(C):
    r = R["rain"]
    for f in range(4):
        n = 3 if f % 2 == 0 else 2
        for k in range(n):
            C.set(r, f, 8 - (k + f) // 3, 6 + k + (f % 2), "sky" if k else "white")


def splash(C):
    """Rain splash: a crown that jumps up then spreads into a 2-px ring with a dark wet rim under it, so it
    reads on light cobble and on dark grass alike (still only ~6-12 opaque texels per frame: cheap)."""
    r = R["rain_splash"]
    frames = [
        # (x, y, colour) ; y grows downward, the ground line is y=10
        [(8, 10, "stone_lo"), (7, 10, "stone_lo"), (9, 10, "stone_lo"), (8, 9, "white"), (8, 8, "sky"), (7, 9, "sky"), (9, 9, "sky")],
        [(6, 10, "stone_lo"), (10, 10, "stone_lo"), (7, 10, "sky"), (9, 10, "sky"), (6, 9, "white"), (10, 9, "white"),
         (7, 8, "sky"), (9, 8, "sky"), (8, 7, "white"), (8, 6, "sky")],
        [(5, 10, "stone_lo"), (11, 10, "stone_lo"), (6, 10, "sky"), (10, 10, "sky"), (5, 9, "white"), (11, 9, "white"),
         (6, 8, "sky"), (10, 8, "sky"), (4, 8, "white"), (12, 8, "white")],
        [(4, 10, "stone_lo"), (12, 10, "stone_lo"), (5, 10, "sky"), (11, 10, "sky"), (3, 9, "sky"), (13, 9, "sky")],
    ]
    for f, pts in enumerate(frames):
        for x, y, c in pts:
            C.set(r, f, x, y, c)


def embers(C):
    r = R["embers"]
    cols = ["white", "lamp", "flower_gold", "roof_hi"]
    for f in range(4):
        C.set(r, f, 8, 8, cols[f])
        if f < 2:
            C.set(r, f, 8, 9, "roof_hi" if f else "lamp")


def steam(C, seed):
    r = R["oven_steam"]
    rr = rng(seed, "steam")
    for f in range(4):
        rad = [2.0, 3.2, 4.4, 5.2][f]
        for y in range(CELL):
            for x in range(CELL):
                d = math.hypot(x - 7.5, (y - 8.0) * 1.2)
                if d > rad:
                    continue
                if f >= 1 and (x + y + f) % 2 == 0 and d > rad * (0.75 - 0.2 * f):
                    continue
                if f == 3 and (x * 3 + y) % 4 == 0:
                    continue
                if rr.random() > 0.9 and d > rad * 0.6:
                    continue
                lit = (x - 7.5) + (y - 8.0) < 0
                C.set(r, f, x, y, "white" if lit else "plaster_hi")


def pollen(C):
    r = R["pollen"]
    for f in range(4):
        C.set(r, f, 8, 8, ["flower_gold", "lamp", "white", "flower_gold"][f])
        if f == 2:
            C.set(r, f, 9, 8, "flower_gold")


def spray(C):
    r = R["fountain_spray"]
    shapes = [[(8, 7, "white"), (8, 8, "sky"), (8, 9, "sky")], [(8, 8, "white"), (8, 9, "sky")],
              [(8, 8, "sky"), (9, 8, "white")], [(8, 8, "sky")]]
    for f, sh in enumerate(shapes):
        for x, y, c in sh:
            C.set(r, f, x, y, c)


def butterflies(C):
    r = R["butterflies"]
    wing = [("flower_blue", "sky"), ("flower_blue", "sky"), ("flower_blue", "sky"), ("flower_blue", "sky")]
    for f in range(4):
        w, hi = wing[f]
        C.set(r, f, 8, 8, "ink"); C.set(r, f, 8, 9, "ink")
        if f in (0, 2):   # open
            for x, y in ((6, 7), (7, 7), (6, 8), (7, 8), (9, 7), (10, 7), (9, 8), (10, 8), (7, 9), (9, 9)):
                C.set(r, f, x, y, w)
            C.set(r, f, 6, 7, hi); C.set(r, f, 10, 7, hi)
        elif f == 1:      # half
            for x, y in ((7, 7), (7, 8), (9, 7), (9, 8)):
                C.set(r, f, x, y, w)
        else:             # closed (edge on)
            C.set(r, f, 8, 7, w); C.set(r, f, 8, 6, hi)


def footdust(C):
    """Footstep dust: a small puff (3-5 px blobs, light top / darker bottom texel) that rises and thins out."""
    r = R["footstep_dust"]
    shapes = [
        [(7, 10, "stone_lo"), (8, 10, "plaster_lo"), (9, 10, "stone_lo"), (7, 9, "plaster"), (8, 9, "plaster_hi"), (9, 9, "plaster"), (8, 8, "plaster")],
        [(6, 10, "stone_lo"), (10, 10, "stone_lo"), (6, 9, "plaster"), (7, 9, "plaster_hi"), (9, 9, "plaster_hi"), (10, 9, "plaster"),
         (7, 8, "plaster"), (8, 8, "plaster_hi"), (9, 8, "plaster")],
        [(5, 9, "plaster_lo"), (6, 8, "plaster"), (7, 8, "plaster_hi"), (10, 8, "plaster_hi"), (11, 9, "plaster_lo"), (8, 7, "plaster"), (11, 8, "plaster")],
        [(5, 8, "plaster_lo"), (11, 8, "plaster_lo"), (7, 7, "plaster"), (10, 7, "plaster_lo")],
    ]
    for f, pts in enumerate(shapes):
        for x, y, c in pts:
            C.set(r, f, x, y, c)


PRESETS = {
    "dust_motes": {"row": 0, "frames": 4, "fps": 3, "mode": "loop", "rate": 5, "life": [4, 8], "grade": "motes",
                   "vel": [[-0.12, 0.12], [0.03, 0.14], [-0.08, 0.08]], "gravity": 0, "sway": 0.25, "glow": False,
                   "area": [8, 2.5, 6]},
    "chimney_wisp": {"row": 1, "frames": 4, "fps": 2, "mode": "life", "rate": 1.4, "life": [2.6, 3.8], "grade": None,
                     "vel": [[0.15, 0.35], [0.55, 0.9], [-0.1, 0.05]], "gravity": 0.05, "sway": 0.12, "glow": False,
                     "area": [0.25, 0.1, 0.25]},
    "leaf_bits": {"row": 2, "frames": 4, "fps": 5, "mode": "loop", "rate": 0.7, "life": [4, 6], "grade": None,
                  "vel": [[-0.2, 0.3], [-0.55, -0.3], [-0.1, 0.1]], "gravity": 0, "sway": 0.7, "glow": False,
                  "area": [3.5, 1.2, 1.5], "floor": 0.05},
    "lamp_bugs": {"row": 3, "frames": 4, "fps": 4, "mode": "loop", "rate": 2.2, "life": [3, 6], "grade": "bugs",
                  "vel": [[-0.25, 0.25], [-0.1, 0.15], [-0.25, 0.25]], "gravity": 0, "sway": 0.4, "glow": True,
                  "area": [3, 1.5, 3]},
    "lamp_flicker": {"row": 4, "frames": 4, "fps": 8, "mode": "flicker", "sequence": [0, 1, 0, 2, 1, 3, 0, 1, 2, 0, 3, 1],
                     "intensity": [1.0, 0.88, 1.1, 0.94], "glow": True},
    # ---- second batch (all cheap: one GL point each, hard alpha)
    "fireflies": {"row": 5, "frames": 4, "fps": 2.5, "mode": "loop", "rate": 1.6, "life": [4, 8], "grade": "bugs",
                  "vel": [[-0.15, 0.15], [-0.05, 0.1], [-0.15, 0.15]], "gravity": 0, "sway": 0.5, "glow": True,
                  "area": [6, 1.0, 2]},
    "petals": {"row": 6, "frames": 4, "fps": 4, "mode": "loop", "rate": 1.2, "life": [4, 7], "grade": None,
               "vel": [[0.05, 0.35], [-0.4, -0.25], [-0.1, 0.1]], "gravity": 0, "sway": 0.6, "glow": False,
               "area": [3, 1, 2], "floor": 0.04},
    "snowfall": {"row": 7, "frames": 4, "fps": 2, "mode": "loop", "rate": 40, "life": [5, 7], "grade": None,
                 "vel": [[-0.15, 0.15], [-0.9, -0.6], [-0.1, 0.1]], "gravity": 0, "sway": 0.35, "glow": False,
                 "area": [26, 1, 18], "y0": 5.5, "follow": True, "floor": 0.02, "weather": True},
    "rain": {"row": 8, "frames": 4, "fps": 10, "mode": "loop", "rate": 120, "life": [0.7, 0.9], "grade": None,
             "vel": [[-0.6, -0.4], [-9.5, -8.5], [0, 0]], "gravity": 0, "sway": 0, "glow": False,
             "area": [26, 1, 18], "y0": 7.0, "follow": True, "floor": 0.02, "on_floor": "rain_splash", "weather": True},
    "rain_splash": {"row": 9, "frames": 4, "fps": 10, "mode": "life", "rate": 0, "life": [0.38, 0.46], "grade": None,
                    "vel": [[0, 0], [0, 0], [0, 0]], "gravity": 0, "sway": 0, "glow": False, "manual": True},
    "embers": {"row": 10, "frames": 4, "fps": 3, "mode": "life", "rate": 6, "life": [1.0, 2.0], "grade": None,
               "vel": [[-0.25, 0.25], [0.7, 1.4], [-0.25, 0.25]], "gravity": -0.2, "sway": 0.5, "glow": True,
               "area": [0.5, 0.1, 0.5]},
    "oven_steam": {"row": 11, "frames": 4, "fps": 2, "mode": "life", "rate": 2.2, "life": [1.8, 2.6], "grade": None,
                   "vel": [[0.05, 0.25], [0.5, 0.8], [0.0, 0.15]], "gravity": 0.04, "sway": 0.18, "glow": False,
                   "area": [0.4, 0.1, 0.2]},
    "pollen": {"row": 12, "frames": 4, "fps": 3, "mode": "loop", "rate": 3, "life": [4, 7], "grade": "motes",
               "vel": [[-0.1, 0.1], [-0.02, 0.08], [-0.1, 0.1]], "gravity": 0, "sway": 0.2, "glow": True,
               "area": [5, 1.2, 4]},
    "fountain_spray": {"row": 13, "frames": 4, "fps": 6, "mode": "life", "rate": 14, "life": [0.7, 1.0], "grade": None,
                       "vel": [[-0.5, 0.5], [2.4, 3.0], [-0.5, 0.5]], "gravity": -6.0, "sway": 0, "glow": False,
                       "area": [0.15, 0.05, 0.15], "floor_rel": -0.05},
    "butterflies": {"row": 14, "frames": 4, "fps": 7, "mode": "loop", "rate": 0.25, "life": [10, 16], "grade": "motes",
                    "vel": [[-0.4, 0.4], [-0.05, 0.08], [-0.4, 0.4]], "gravity": 0, "sway": 0.9, "glow": False,
                    "area": [4, 0.8, 3]},
    "footstep_dust": {"row": 15, "frames": 4, "fps": 8, "mode": "life", "rate": 0, "life": [0.5, 0.65], "grade": None,
                      "vel": [[-0.35, 0.35], [0.05, 0.2], [-0.2, 0.2]], "gravity": -0.3, "sway": 0, "glow": False,
                      "manual": True, "burst": 4},
}


def build(biome="cozy-village", out="public/art/particles", project=None, seed=1):
    pal = Pal(load_biome(biome, project))
    out = ensure(out)
    C = Cells(pal)
    motes(C); wisp(C, seed); leaves(C); bugs(C); flicker(C)
    fireflies(C); petals(C); snow(C); rain(C); splash(C); embers(C); steam(C, seed); pollen(C); spray(C)
    butterflies(C); footdust(C)
    C.im.save(out / "particles.png")
    C.im.crop((0, 4 * CELL, 4 * CELL, 5 * CELL)).save(out / "lamp_flicker.png")
    meta = {"tool": "hd2d particles", "biome": biome, "seed": seed, "image": "particles.png", "cell": CELL,
            "rows": ROWS, "presets": PRESETS}
    write_json(out / "particles.json", meta)
    big = Image.new("RGBA", (C.im.width * 6 + 110, C.im.height * 6), (40, 44, 70, 255))
    big.alpha_composite(C.im.resize((C.im.width * 6, C.im.height * 6), Image.NEAREST), (110, 0))
    d = ImageDraw.Draw(big)
    for i, n in enumerate(ROWS):
        d.text((4, i * CELL * 6 + 40), n, fill=(240, 230, 200, 255))
    big.save(out / "particles_preview_6x.png")
    return meta


def main(argv=None):
    ap = argparse.ArgumentParser(prog="hd2d particles", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--biome", default="cozy-village")
    ap.add_argument("--out", default="public/art/particles")
    ap.add_argument("--project", default=None)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args(argv)
    build(a.biome, a.out, a.project, a.seed)
    print(f"particles: {len(ROWS)} rows ({', '.join(ROWS)}) -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
