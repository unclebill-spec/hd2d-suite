"""hd2d texel: chunky palette-snapped tileable world textures (32 and 64 px).

    hd2d texel --biome cozy-village --sizes 32,64 --out PROJECT/public/art/texel

Kinds: cobble, brick, timber, thatch, plaster, moss, roof (shingle), dirt (path), grass,
stone (retaining-wall blocks), awning (stall fabric). Every pixel is one biome colour (3-5 step ramp
per kind), every texture wraps seamlessly. Structure first (cells, rows, planks), noise second,
following the Gravewake pixel writer rule: if it looks like noise, fix the shapes.
World textures may be mipmapped by the runtime; sprites never are.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE / "vendor"))
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

from hd2d_common import Pal, ensure, hex2rgb, load_biome, rng, write_json  # noqa: E402
from pixel_writer import Tile  # noqa: E402  (vendored Gravewake pixel writer grid)

KINDS = ["cobble", "brick", "timber", "thatch", "plaster", "moss", "roof", "dirt", "grass", "stone", "awning"]
# metres covered by one tile of each kind (the kit uses this for UVs)
METRES = {"cobble": 1.6, "brick": 1.6, "timber": 1.6, "thatch": 2.0, "plaster": 2.0, "moss": 2.0,
          "roof": 1.6, "dirt": 2.4, "grass": 2.4, "stone": 2.4, "awning": 1.0}


def value_noise(n, cells, seed, tag):
    """Tileable value noise in [0,1] (lattice wraps)."""
    r = rng(seed, "noise", tag, n, cells)
    g = np.array([[r.random() for _ in range(cells)] for _ in range(cells)])
    xs = np.arange(n) * cells / n
    i0 = np.floor(xs).astype(int)
    f = xs - i0
    f = f * f * (3 - 2 * f)
    i1 = (i0 + 1) % cells
    a = g[np.ix_(i0, i0)] * (1 - f)[None, :] + g[np.ix_(i0, i1)] * f[None, :]
    b = g[np.ix_(i1, i0)] * (1 - f)[None, :] + g[np.ix_(i1, i1)] * f[None, :]
    return a * (1 - f)[:, None] + b * f[:, None]


def fbm(n, seed, tag, octaves=((4, 0.6), (8, 0.3), (16, 0.1))):
    out = np.zeros((n, n))
    for c, w in octaves:
        c = min(c, n)
        out += value_noise(n, c, seed, f"{tag}{c}") * w
    return out / sum(w for _, w in octaves)


def quant(field, ramp, cuts=None):
    """Map a [0,1] field (1 = light) to ramp indices (0 = lightest)."""
    k = len(ramp)
    if cuts is None:
        cuts = [(i + 1) / k for i in range(k - 1)]
    idx = np.zeros(field.shape, int)
    for c in cuts:
        idx += (field < c).astype(int)
    # idx counts how many cuts are above -> 0 means darkest; flip so 0 = lightest
    return (k - 1) - idx


def to_tile(idx, ramp_hex) -> Tile:
    n = idx.shape[0]
    t = Tile(n)
    for y in range(n):
        for x in range(n):
            t.set(x, y, ramp_hex[int(idx[y, x])])
    return t


def voronoi(n, count, seed, tag):
    r = rng(seed, "vor", tag, n)
    pts = np.array([[r.random() * n, r.random() * n] for _ in range(count)])
    yy, xx = np.mgrid[0:n, 0:n] + 0.5
    best1 = np.full((n, n), 1e9)
    best2 = np.full((n, n), 1e9)
    owner = np.zeros((n, n), int)
    dvec = np.zeros((n, n, 2))
    for i, (px, py) in enumerate(pts):
        for ox in (-n, 0, n):
            for oy in (-n, 0, n):
                dx = xx - (px + ox)
                dy = yy - (py + oy)
                d = np.sqrt(dx * dx + dy * dy * 1.15)
                m1 = d < best1
                best2 = np.where(m1, best1, np.minimum(best2, d))
                owner = np.where(m1, i, owner)
                dvec[m1] = np.stack([dx, dy], -1)[m1]
                best1 = np.where(m1, d, best1)
    return best1, best2, owner, dvec


# ------------------------------------------------------------------ kinds
def cobble(pal, n, seed):
    ramp = [pal["stone_hi"], pal["stone"], pal["stone_lo"], pal["shadow"], pal["moss"]]
    s = n / 32
    d1, d2, own, dv = voronoi(n, int(18 * s * s), seed, "cobble")
    edge = (d2 - d1) < 1.15
    r = rng(seed, "cobtone")
    tone = np.array([r.choice([0, 0, 0, 1, 1, 1, 2]) for _ in range(own.max() + 1)])
    nz = fbm(n, seed, "cob", ((4, 0.5), (16, 0.5)))
    idx = tone[own].copy()
    # light from upper-left: pixels on the upper-left of a stone go one step lighter, lower-right darker
    lit = (dv[..., 0] + dv[..., 1]) < -1.2 * s
    shade = (dv[..., 0] + dv[..., 1]) > 1.6 * s
    idx = np.where(lit, np.maximum(idx - 1, 0), idx)
    idx = np.where(shade & (nz > 0.45), np.minimum(idx + 1, 2), idx)
    gap_moss = (value_noise(n, 4, seed, "cobmoss") > 0.7) & (value_noise(n, min(n, 16), seed, "cm2") > 0.55)
    idx = np.where(edge, np.where(gap_moss, 4, 3), idx)
    return to_tile(idx, ramp)


def brick(pal, n, seed):
    ramp = [pal["roof_hi"], pal["roof"], pal["roof_lo"], pal["plaster_lo"], pal["timber_lo"]]
    s = n // 32
    bh, bw = 4 * s, 8 * s
    idx = np.zeros((n, n), int)
    r = rng(seed, "brick")
    for row in range(n // bh):
        off = (bw // 2) * (row % 2)
        for col in range(-1, n // bw + 1):
            x0 = col * bw + off
            t = r.choice([0, 1, 1, 1, 2])
            for y in range(row * bh, row * bh + bh):
                for x in range(x0, x0 + bw):
                    xx = x % n
                    if y == row * bh + bh - 1 or x == x0:
                        idx[y, xx] = 3
                    else:
                        v = t
                        if y == row * bh and t > 0:
                            v = t - 1  # top-edge light
                        if x == x0 + bw - 1:
                            v = min(t + 1, 2)
                        idx[y, xx] = v
    sp = value_noise(n, 8, seed, "brsoot") > 0.78
    idx = np.where(sp & (idx < 3), np.minimum(idx + 1, 2), idx)
    return to_tile(idx, ramp)


def timber(pal, n, seed):
    ramp = [pal["timber_hi"], pal["timber"], pal["timber_lo"], pal["ink"]]
    s = n // 32
    pw = 8 * s
    r = rng(seed, "plank")
    grain = value_noise(n, 4, seed, "graina")[:, :1] * 0  # placeholder for shape
    idx = np.ones((n, n), int)
    g = fbm(n, seed, "grain", ((2, 0.5), (16, 0.5)))
    for p in range(n // pw):
        x0 = p * pw
        base = r.choice([0, 1, 1, 2])
        off = r.randrange(n)
        for x in range(x0, x0 + pw):
            for y in range(n):
                v = base
                gy = (y + off) % n
                stripe = math.sin((x - x0) * 1.3 + g[gy, x] * 6) > 0.75
                if stripe:
                    v = min(base + 1, 2)
                if x == x0:
                    v = 3
                elif x == x0 + 1 and base > 0:
                    v = base - 1
                idx[y, x] = v
        # plank end joint
        jy = r.randrange(n)
        idx[jy, x0:x0 + pw] = 3
        # knot
        if r.random() < 0.6:
            kx, ky = x0 + r.randrange(2, pw - 2), r.randrange(n)
            idx[ky % n, kx] = 2
            idx[(ky + 1) % n, kx] = 3
    return to_tile(idx, ramp)


def thatch(pal, n, seed):
    ramp = [pal["flower_gold"], pal["timber_hi"], pal["timber"], pal["timber_lo"]]
    s = n // 32
    idx = np.ones((n, n), int)
    r = rng(seed, "thatch")
    rowh = 6 * s
    for row in range(n // rowh):
        y0 = row * rowh
        for k in range(n * 2):
            x = r.randrange(n)
            ln = r.randrange(3, rowh + 2)
            t = r.choice([0, 0, 1, 1, 2])
            for j in range(ln):
                yy = (y0 + j) % n
                xx = (x + (j // 3)) % n
                idx[yy, xx] = t
        idx[(y0 + rowh - 1) % n, :] = np.where(np.arange(n) % 3 == 0, 3, 2)
    return to_tile(idx, ramp)


def plaster(pal, n, seed):
    ramp = [pal["plaster_hi"], pal["plaster"], pal["plaster_lo"]]
    f = fbm(n, seed, "plaster", ((2, 0.5), (4, 0.3), (32, 0.2)))
    idx = quant(f, ramp, cuts=[0.36, 0.62])
    idx = np.where(idx == 2, 1, idx)
    sp = value_noise(n, min(n, 32), seed, "plsp") > 0.9
    idx = np.where(sp, 2, idx)
    return to_tile(idx, ramp)


def moss(pal, n, seed):
    ramp = [pal["grass_hi"], pal["grass"], pal["moss"], pal["leaf_deep"]]
    f = fbm(n, seed, "moss", ((4, 0.4), (8, 0.35), (16, 0.25)))
    idx = quant(f, ramp, cuts=[0.33, 0.47, 0.62])
    return to_tile(idx, ramp)


def roof(pal, n, seed):
    ramp = [pal["roof_hi"], pal["roof"], pal["roof_lo"], pal["ink"], pal["moss"]]
    s = n // 32
    rh, tw = 5 * s if s == 1 else 4 * s, 8 * s
    rh = max(4, n // (6 if s == 1 else 12) if False else rh)
    rows = n // rh
    rh = n // rows
    idx = np.ones((n, n), int)
    r = rng(seed, "roof")
    for row in range(rows):
        y0 = row * rh
        off = (tw // 2) * (row % 2)
        for col in range(-1, n // tw + 1):
            x0 = col * tw + off
            t = r.choice([0, 1, 1, 1, 2])
            for y in range(y0, y0 + rh):
                for x in range(x0, x0 + tw):
                    xx = x % n
                    v = t
                    fy = (y - y0) / rh
                    if fy > 0.7:
                        v = min(t + 1, 2)
                    if y == y0 + rh - 1:
                        v = 3 if (x - x0) not in (0, tw - 1) else 2
                    if x == x0:
                        v = 2
                    if y == y0 and t > 0:
                        v = t - 1
                    idx[y, xx] = v
    m = value_noise(n, 4, seed, "rmoss") > 0.8
    m2 = value_noise(n, min(32, n), seed, "rmoss2") > 0.5
    idx = np.where(m & m2 & (idx < 3), 4, idx)
    return to_tile(idx, ramp)


def dirt(pal, n, seed):
    ramp = [pal["plaster_lo"], pal["timber_hi"], pal["timber"], pal["timber_lo"], pal["stone_hi"]]
    f = fbm(n, seed, "dirt", ((8, 0.5), (16, 0.3), (32, 0.2)))
    idx = quant(f, ramp[:4], cuts=[0.34, 0.5, 0.7])
    idx = np.where(idx == 3, 2, idx)
    r = rng(seed, "pebble")
    for _ in range(n // 4):
        x, y = r.randrange(n), r.randrange(n)
        idx[y, x] = 4
        idx[(y + 1) % n, x] = 3
    return to_tile(idx, ramp)


def grass(pal, n, seed):
    """Pixel-writer style: base field, 1px blades in clumps, dark under-clumps, rare flowers."""
    ramp = [pal["grass_hi"], pal["grass"], pal["moss"], pal["flower_gold"], pal["flower_rose"], pal["white"]]
    f = fbm(n, seed, "grass", ((8, 0.5), (16, 0.5)))
    idx = np.where(f > 0.6, 0, np.where(f < 0.3, 2, 1))
    idx = np.where(idx == 0, 1, idx)
    r = rng(seed, "blades")
    for _ in range(n * n // 18):
        x, y = r.randrange(n), r.randrange(n)
        idx[y % n, x] = 0
        idx[(y + 1) % n, x] = 1 if idx[(y + 1) % n, x] != 2 else 2
        idx[(y + 2) % n, x] = 2 if r.random() < 0.5 else idx[(y + 2) % n, x]
    for _ in range(max(1, n // 16)):
        x, y = r.randrange(n), r.randrange(n)
        idx[y, x] = r.choice([3, 4, 5])
    return to_tile(idx, ramp)


def stone(pal, n, seed):
    ramp = [pal["stone_hi"], pal["stone"], pal["stone_lo"], pal["shadow"], pal["moss"]]
    s = n // 32
    idx = np.ones((n, n), int)
    r = rng(seed, "stone")
    rh = 8 * s
    for row in range(n // rh):
        y0 = row * rh
        x = r.randrange(n)
        start = x
        while x < start + n:
            w = r.randrange(7 * s, 14 * s)
            t = r.choice([0, 1, 1, 2])
            for y in range(y0, y0 + rh):
                for xx in range(x, x + w):
                    xm = xx % n
                    v = t
                    if y == y0 and t > 0:
                        v = t - 1
                    if y >= y0 + rh - 2:
                        v = min(t + 1, 2)
                    if y == y0 + rh - 1 or xx == x:
                        v = 3
                    idx[y, xm] = v
            x += w
    m = value_noise(n, 4, seed, "smoss") > 0.66
    idx = np.where(m & (idx == 3), 4, idx)
    return to_tile(idx, ramp)


def awning(pal, n, seed):
    ramp = [pal["white"], pal["plaster_hi"], pal["flower_rose"], pal["roof_hi"], pal["roof"]]
    s = n // 32
    idx = np.zeros((n, n), int)
    sw = 8 * s
    for x in range(n):
        band = (x // sw) % 2
        for y in range(n):
            fold = (x % sw) in (sw - 1,)
            if band == 0:
                v = 0 if not fold else 1
            else:
                v = 2 if not fold else 3
            if y % (16 * s) >= 14 * s:
                v = 1 if band == 0 else 4
            idx[y, x] = v
    return to_tile(idx, ramp)


GEN = {"cobble": cobble, "brick": brick, "timber": timber, "thatch": thatch, "plaster": plaster, "moss": moss,
       "roof": roof, "dirt": dirt, "grass": grass, "stone": stone, "awning": awning}


def seamless_score(im: Image.Image) -> float:
    """Mean colour jump across the wrap seam vs inside (1.0 = as smooth as the interior)."""
    a = np.asarray(im.convert("RGB"), float)
    inner = np.abs(np.diff(a, axis=1)).mean() + np.abs(np.diff(a, axis=0)).mean()
    seam = np.abs(a[:, 0] - a[:, -1]).mean() + np.abs(a[0] - a[-1]).mean()
    return float(seam / max(inner, 1e-6))


def build(biome="cozy-village", sizes=(32, 64), kinds=None, out="public/art/texel", project=None, seed=1):
    pal = Pal(load_biome(biome, project))
    kinds = kinds or KINDS
    out = ensure(out)
    meta = {"tool": "hd2d texel", "biome": biome, "seed": seed, "sizes": list(sizes), "metres": METRES, "textures": {}}
    sheet_rows = []
    for size in sizes:
        row = []
        for k in kinds:
            t = GEN[k](pal, size, seed)
            im = t.image()
            path = out / f"{k}_{size}.png"
            im.save(path)
            cols = len(set(im.getdata()))
            meta["textures"][f"{k}_{size}"] = {"file": path.name, "kind": k, "size": size, "colors": cols,
                                                "metres": METRES[k], "seam": round(seamless_score(im), 2)}
            row.append(im)
        sheet_rows.append(row)
    # preview: each texture tiled 2x2 so seams show, nearest 3x
    cell = max(sizes) * 2
    sheet = Image.new("RGBA", (len(kinds) * (cell + 4), len(sizes) * (cell + 16)), (236, 222, 190, 255))
    d = ImageDraw.Draw(sheet)
    for j, row in enumerate(sheet_rows):
        for i, im in enumerate(row):
            n = im.width
            x0, y0 = i * (cell + 4), j * (cell + 16) + 12
            for ty in range(cell // n):
                for tx in range(cell // n):
                    sheet.paste(im, (x0 + tx * n, y0 + ty * n))
            d.text((x0 + 2, y0 - 11), f"{kinds[i]} {n}", fill=(60, 40, 30, 255))
    sheet = sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST)
    sheet.save(out / "texel_sheet.png")
    write_json(out / "texel.json", meta)
    return meta


def main(argv=None):
    ap = argparse.ArgumentParser(prog="hd2d texel", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--biome", default="cozy-village")
    ap.add_argument("--sizes", default="32,64")
    ap.add_argument("--kinds", default="all", help="comma list or all: " + ", ".join(KINDS))
    ap.add_argument("--out", default="public/art/texel")
    ap.add_argument("--project", default=None)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args(argv)
    kinds = KINDS if a.kinds == "all" else a.kinds.split(",")
    meta = build(a.biome, [int(x) for x in a.sizes.split(",")], kinds, a.out, a.project, a.seed)
    for k, v in meta["textures"].items():
        print(f"  {k:12s} {v['colors']} colours  seam {v['seam']}")
    print(f"texel: {len(meta['textures'])} textures -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
