"""hd2d trees: layered-card trees for HD-2D dioramas (canopy art from brileta-sprites, MIT).

    hd2d trees --biome cozy-village --out PROJECT/public/art/trees [--count 3]

Each tree = a low-poly trunk .glb + 3 canopy cards (back / mid / front, depth-offset, tilted toward the
locked camera). Card art: brileta canopies (hard-alpha snapped, as in Gravewake's make_gravewake.mjs),
upscaled 2x nearest, re-clumped into leaf clusters lit from the upper left, snapped to the biome ramp.
Also writes <tree>_lowpoly.glb (faceted canopy option) and trees.json + trees_preview.png.
"""
from __future__ import annotations

import argparse
import base64
import json
import math
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE.parents[0] / "kit"))
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

from hd2d_common import Pal, ensure, load_biome, rng, write_json, mix, hex2rgb  # noqa: E402
from meshlib import Mesh, cylinder, beam, sphere, export_glb  # noqa: E402

NODE = "node"


def brileta(reqs):
    out = subprocess.run([NODE, str(HERE / "brileta_dump.mjs"), json.dumps(reqs)], capture_output=True, text=True, check=True)
    res = []
    for r in json.loads(out.stdout):
        a = np.frombuffer(base64.b64decode(r["data"]), np.uint8).reshape(r["h"], r["w"], 4)
        res.append(a)
    return res


def canopy_of(rgba):
    """Canopy mask + light value from a brileta tree: hard alpha (>=140), greenish pixels only."""
    a = rgba[..., 3] >= 140
    r, g, b = rgba[..., 0].astype(int), rgba[..., 1].astype(int), rgba[..., 2].astype(int)
    green = a & (g > r + 4)
    lum = (0.3 * r + 0.59 * g + 0.11 * b) / 255.0
    ys, xs = np.where(green)
    if len(xs) == 0:
        return None, None
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    return green[y0:y1, x0:x1], lum[y0:y1, x0:x1]


def value_noise(h, w, cells, r):
    gy, gx = cells, max(2, int(cells * w / h))
    g = np.array([[r.random() for _ in range(gx + 1)] for _ in range(gy + 1)])
    ys = np.linspace(0, gy, h, endpoint=False)
    xs = np.linspace(0, gx, w, endpoint=False)
    yi, xi = np.floor(ys).astype(int), np.floor(xs).astype(int)
    fy, fx = ys - yi, xs - xi
    fy, fx = fy * fy * (3 - 2 * fy), fx * fx * (3 - 2 * fx)
    a = g[np.ix_(yi, xi)] * (1 - fx) + g[np.ix_(yi, xi + 1)] * fx
    b = g[np.ix_(yi + 1, xi)] * (1 - fx) + g[np.ix_(yi + 1, xi + 1)] * fx
    return a * (1 - fy)[:, None] + b * fy[:, None]


def make_card(pal: Pal, canopies, W, H, r, tone=0, ramp=None):
    """Compose a W x H card from several brileta canopies, 2x nearest, leaf clumps, ramp snap."""
    mask = np.zeros((H, W), bool)
    light = np.zeros((H, W))
    for k, (cm, cl) in enumerate(canopies):
        m2 = np.kron(cm, np.ones((2, 2), bool))
        l2 = np.kron(cl, np.ones((2, 2)))
        h, w = m2.shape
        if h > H or w > W:
            m2, l2 = m2[:H, :W], l2[:H, :W]
            h, w = m2.shape
        ox = int((W - w) / 2 + r.uniform(-0.3, 0.3) * (W - w)) if W > w else 0
        oy = int(r.uniform(0.0, 0.6) * (H - h)) if H > h else 0
        if k == 0:
            ox, oy = (W - w) // 2, (H - h) // 3
        sub = mask[oy:oy + h, ox:ox + w]
        light[oy:oy + h, ox:ox + w] = np.where(m2 & ~sub, l2, light[oy:oy + h, ox:ox + w])
        mask[oy:oy + h, ox:ox + w] |= m2
    # round the 2x2 steps: majority filter, then bumpy leaf edge
    for _ in range(2):
        p = np.pad(mask, 1)
        n = sum(p[1 + dy:H + 1 + dy, 1 + dx:W + 1 + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1))
        mask = n >= 5
    edge = mask & ~(np.pad(mask, 1)[2:, 1:-1] & np.pad(mask, 1)[:-2, 1:-1] & np.pad(mask, 1)[1:-1, 2:] & np.pad(mask, 1)[1:-1, :-2])
    nz = value_noise(H, W, 12, r)
    mask = mask & ~(edge & (nz > 0.72))
    p = np.pad(mask, 1)
    grow = (p[:-2, 1:-1] | p[1:-1, :-2]) & ~mask & (value_noise(H, W, 14, r) > 0.62)
    mask |= grow
    # light: upper-left key + clumps (each clump bright on its upper-left, dark lower-right)
    yy, xx = np.mgrid[0:H, 0:W]
    ys, xs = np.where(mask)
    cy, cx = ys.mean(), xs.mean()
    key = 1 - ((yy - ys.min()) / max(1, ys.max() - ys.min()) * 0.7 + (xx - xs.min()) / max(1, xs.max() - xs.min()) * 0.3)
    clump = np.zeros((H, W))
    for _ in range(int(W * H / 90)):
        px_, py_ = r.uniform(0, W), r.uniform(0, H)
        rad = r.uniform(3.0, 6.5)
        d = np.sqrt((xx - px_) ** 2 + (yy - py_) ** 2) / rad
        inside = d < 1
        rim = ((xx - px_) + (yy - py_)) / rad  # negative = upper-left
        clump = np.where(inside, np.maximum(clump, (1 - d) * 0.4 - rim * 0.35 + 0.2), clump)
    v = key * 0.55 + clump * 0.6 + (light - 0.3) * 0.4 - tone * 0.12
    # self shadow at the bottom of the canopy
    bottom = (yy - ys.min()) / max(1, ys.max() - ys.min())
    v -= np.clip(bottom - 0.65, 0, 1) * 0.8
    ramp = ramp or [pal["grass_hi"], pal["grass"], pal["moss"], pal["leaf_deep"]]
    cuts = np.quantile(v[mask], [0.82, 0.5, 0.2]) if mask.any() else [0.6, 0.4, 0.2]
    idx = np.full((H, W), 3)
    idx[v >= cuts[2]] = 2
    idx[v >= cuts[1]] = 1
    idx[v >= cuts[0]] = 0
    # dark rim on the lower/right silhouette only (no black outline on world foliage)
    p = np.pad(mask, 1)
    lower_edge = mask & (~p[2:, 1:-1] | ~p[1:-1, 2:])
    idx[lower_edge] = 3
    # a few highlight flecks
    fl = (value_noise(H, W, 20, r) > 0.8) & (idx == 1) & (key > 0.5)
    idx[fl] = 0
    out = np.zeros((H, W, 4), np.uint8)
    for i, c in enumerate(ramp):
        rr, gg, bb = hex2rgb(c)
        sel = mask & (idx == i)
        out[sel] = (rr, gg, bb, 255)
    # optional blossoms / fruit dots
    return Image.fromarray(out, "RGBA")


def trunk_mesh(pal: Pal, height, r, seed):
    m = Mesh()
    bark = mix(pal["timber"], "#ffffff", 0.25)
    m.add(cylinder(0.26, 0.17, height * 0.62, 7, bark, "timber", caps=False, y0=0))
    m.add(cylinder(0.36, 0.26, 0.25, 7, bark, "timber", caps=False, y0=0))
    top = height * 0.62
    rr = rng(seed, "branches")
    for i in range(3):
        ang = i * 2.1 + rr.uniform(-0.4, 0.4)
        L = rr.uniform(0.9, 1.4)
        y0 = top * rr.uniform(0.7, 0.98)
        m.add(beam((0, y0, 0), (math.cos(ang) * L, y0 + L * 0.8, math.sin(ang) * L * 0.4 - 0.2), 0.12, bark))
    m.add(cylinder(0.17, 0.08, height * 0.25, 6, bark, "timber", caps=False, y0=top))
    return m.ao(0, 1.2, 0.3)


def lowpoly_canopy(pal: Pal, height, width, seed):
    m = Mesh()
    r = rng(seed, "lowpoly")
    cols = [pal["grass_hi"], pal["grass"], pal["moss"]]
    for i in range(6):
        rad = width * r.uniform(0.22, 0.34)
        x = r.uniform(-width * 0.28, width * 0.28)
        y = height * r.uniform(0.6, 0.85)
        z = r.uniform(-0.6, 0.6)
        m.add(sphere(rad, 7, 5, cols[i % 2], squash=(1, 0.85, 1), noise=0.18, rnd=r, col_bottom=pal["leaf_deep"]).xf((x, y, z)))
    return m


TREE_TYPES = {
    "oak": dict(arch="deciduous", h=6.0, w=5.0, cards=[(60, 54), (56, 48), (40, 34)]),
    "apple": dict(arch="deciduous", h=4.8, w=4.2, cards=[(52, 44), (48, 40), (34, 28)], fruit="flower_rose"),
    "birch": dict(arch="deciduous", h=6.4, w=3.8, cards=[(44, 56), (40, 50), (30, 34)]),
}


def build(biome="cozy-village", out="public/art/trees", project=None, seed=3, count=3, texel=None):
    pal = Pal(load_biome(biome, project))
    out = ensure(out)
    texel = Path(texel) if texel else (Path(project) / "public/art/texel" if project else out.parent / "texel")
    if not (texel / "timber_32.png").exists():
        from hd2d_common import load_tool
        load_tool("texel").build(biome, (32, 64), None, texel, project, seed)
    meta = {"tool": "hd2d trees", "biome": biome, "seed": seed, "credits": "canopy art: brileta-sprites (MIT, Mark Ayzenshtat)",
            "trees": {}}
    reqs = [{"seed": seed * 100 + i, "size": 26, "arch": "deciduous"} for i in range(count * 6)]
    cans = [c for c in (canopy_of(a) for a in brileta(reqs)) if c[0] is not None]
    previews = []
    names = list(TREE_TYPES)
    for t in range(count):
        tname = names[t % len(names)]
        tt = TREE_TYPES[tname]
        name = f"{tname}_{t + 1}"
        r = rng(seed, "tree", t)
        ppm = 12.0  # card pixels per metre (chunkier than the 17.8 px/m sprites)
        cards = []
        layers = [("back", 1, -0.55, 0.25), ("mid", 0, 0.0, 0.0), ("front", -1, 0.6, -0.35)]
        ramp_dark = [pal["grass"], pal["moss"], pal["leaf_deep"], pal["ink"]]
        for li, ((cw, ch), (lname, tone, dz, dy)) in enumerate(zip(tt["cards"], layers)):
            pick = [cans[(t * 6 + li * 2 + j) % len(cans)] for j in range(2 if li < 2 else 1)]
            ramp = ramp_dark if lname == "back" else None
            im = make_card(pal, pick, cw, ch, r, tone=tone, ramp=ramp)
            if tt.get("fruit") and lname != "back":
                a = np.array(im)
                rr2 = rng(seed, "fruit", t, li)
                ys, xs = np.where(a[..., 3] == 255)
                fr = hex2rgb(pal[tt["fruit"]])
                for _ in range(max(3, len(xs) // 120)):
                    k = rr2.randrange(len(xs))
                    y, x = ys[k], xs[k]
                    if 0 < y < a.shape[0] - 1 and 0 < x < a.shape[1] - 1 and a[y + 1, x, 3] == 255:
                        a[y, x, :3] = fr
                        a[y + 1, x, :3] = hex2rgb(pal.dk(tt["fruit"]))
                im = Image.fromarray(a, "RGBA")
            f = f"{name}_card{li}.png"
            im.save(out / f)
            w_m, h_m = cw / ppm, ch / ppm
            base_y = tt["h"] - h_m - 0.2 + dy * 2
            cards.append({"image": f, "w": round(w_m, 3), "h": round(h_m, 3),
                          "offset": [round(r.uniform(-0.3, 0.3) + (0.35 if lname == "front" else 0), 3), round(base_y, 3), dz],
                          "tilt": 16, "layer": lname})
            previews.append(im)
        tm = trunk_mesh(pal, tt["h"], r, seed * 10 + t)
        tex = {"timber": str(texel / "timber_32.png")}
        export_glb(tm, out / f"{name}_trunk.glb", tex, {"timber": 1.6}, f"{name}_trunk")
        lp = lowpoly_canopy(pal, tt["h"], tt["w"], seed * 10 + t)
        lp.add(tm)
        export_glb(lp, out / f"{name}_lowpoly.glb", tex, {"timber": 1.6}, f"{name}_lowpoly")
        meta["trees"][name] = {"type": tname, "height": tt["h"], "width": tt["w"], "trunk": f"{name}_trunk.glb",
                               "lowpoly": f"{name}_lowpoly.glb", "cards": cards, "blocker": 0.45}
    # preview: cards per tree side by side, 3x nearest on parchment
    if previews:
        Wp = sum(p.width + 4 for p in previews)
        Hp = max(p.height for p in previews)
        sheet = Image.new("RGBA", (Wp, Hp), (236, 222, 190, 255))
        x = 0
        for p in previews:
            sheet.alpha_composite(p, (x, Hp - p.height))
            x += p.width + 4
        sheet.resize((Wp * 3, Hp * 3), Image.NEAREST).save(out / "trees_preview.png")
    (out / "CREDITS.txt").write_text("Tree canopy art generated with brileta-sprites by Mark Ayzenshtat (MIT).\n"
                                     "https://github.com/mayz/brileta-sprites\nSnapped to the hd2d biome palette by tools/trees/trees.py.\n")
    write_json(out / "trees.json", meta)
    return meta


def main(argv=None):
    ap = argparse.ArgumentParser(prog="hd2d trees", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--biome", default="cozy-village")
    ap.add_argument("--out", default="public/art/trees")
    ap.add_argument("--project", default=None)
    ap.add_argument("--texel", default=None)
    ap.add_argument("--seed", type=int, default=3)
    ap.add_argument("--count", type=int, default=3)
    a = ap.parse_args(argv)
    meta = build(a.biome, a.out, a.project, a.seed, a.count, a.texel)
    for k, v in meta["trees"].items():
        print(f"  {k:10s} {len(v['cards'])} cards  h={v['height']} m")
    print(f"trees: {len(meta['trees'])} -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
