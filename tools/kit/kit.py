"""hd2d kit: cozy HD-2D town kit .glb generator (extends n64-suite's mesh/model code).

    hd2d kit --biome cozy-village --out PROJECT/public/art/kit [--texel PROJECT/public/art/texel]

Pieces (metres; a sprite is 1.8 m): terrace blocks, stairs, retaining walls, 4 cottage types with thick
roofs and timber framing (cottage_baker, cottage_tall, cottage_stone, cottage_shop), 3 lane buildings
(bakery with a brick bread oven, inn, flower_shop) with bracket hanging signs, market stall, barrel, crate,
sign, hanging_sign_{loaf,mug,flower,key}, flower crate, bunting, laundry line, fountain, lamp post, wall lamp,
fence, bench, hedge, well, hills.
Materials are LIT (glTF PBR metallic 0, roughness 1; the runtime converts to Lambert), textured with
texel outputs (nearest magnification, mipmapped minification), vertex colours carry tint + contact AO.
Writes <piece>.glb + kit.json (footprint, height, collision boxes, markers: lamps, chimneys, windows).
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))
from hd2d_common import Pal, ensure, load_biome, load_tool, mix, rng, write_json  # noqa: E402
from meshlib import Mesh, beam, box, cylinder, export_glb, prism_x, sphere  # noqa: E402

PI = math.pi
TEX_SIZE = {"plaster": 64, "timber": 32, "stone": 32, "roof": 64, "thatch": 64, "brick": 32, "cobble": 64,
            "grass": 64, "dirt": 64, "moss": 32, "awning": 32}
W_ = "#ffffff"


class Ctx:
    def __init__(self, pal: Pal, texel_dir: Path, seed=1):
        self.pal = pal
        self.texel = Path(texel_dir)
        self.seed = seed
        meta = load_tool("texel").METRES
        self.tile_m = dict(meta)

    def textures(self):
        return {k: str(self.texel / f"{k}_{s}.png") for k, s in TEX_SIZE.items()}

    def c(self, name):
        return self.pal[name]


class Piece:
    def __init__(self, name):
        self.name = name
        self.mesh = Mesh()
        self.markers = {"lamps": [], "chimneys": [], "windows": [], "doors": []}
        self.blockers = []  # [x0, z0, x1, z1] local
        self.kind = "prop"

    def add(self, m):
        self.mesh.add(m)
        return self


# ------------------------------------------------------------------ building parts
def window(cx: Ctx, w=0.8, h=0.95, shutter="cloth", flowers=True, seed=0):
    """Window in the local xy plane facing +z, centre at origin on the wall surface."""
    m = Mesh()
    t = 0.08
    m.add(box(w, h, 0.04, W_, "window", y0=-h / 2).xf((0, 0, -0.02)))
    tim = mix(cx.c("timber"), "#ffffff", 0.5)
    for (px, py, bw, bh) in ((0, h / 2 + t / 2, w + 2 * t, t), (0, -h / 2 - t / 2, w + 2 * t, t),
                             (-w / 2 - t / 2, 0, t, h), (w / 2 + t / 2, 0, t, h), (0, 0, 0.05, h), (0, 0.05, w, 0.05)):
        m.add(box(bw, bh, 0.1, tim, "timber", y0=-bh / 2).xf((px, py, 0.03)))
    m.add(box(w + 0.3, 0.07, 0.18, tim, "timber", y0=0).xf((0, -h / 2 - t - 0.07, 0.07)))  # sill
    if shutter:
        sc = mix(cx.c(shutter), "#ffffff", 0.35)
        for sx in (-1, 1):
            m.add(box(w / 2, h, 0.05, sc, "timber", y0=-h / 2).xf((sx * (w / 2 + t + w / 4 + 0.02), 0, 0.03)))
    if flowers:
        r = rng(cx.seed, "wflowers", seed)
        m.add(box(w + 0.2, 0.2, 0.24, mix(cx.c("timber"), "#ffffff", 0.3), "timber", y0=0).xf((0, -h / 2 - t - 0.3, 0.14)))
        cols = [cx.c("flower_rose"), cx.c("flower_gold"), cx.c("flower_blue"), cx.c("white")]
        for i in range(7):
            fx = -w / 2 + (i + 0.5) * (w / 7) + r.uniform(-0.03, 0.03)
            m.add(sphere(0.07, 5, 3, cx.c("grass")).xf((fx, -h / 2 - t - 0.08, 0.16 + r.uniform(-0.04, 0.04))))
            if r.random() < 0.75:
                m.add(sphere(0.06, 5, 3, r.choice(cols)).xf((fx + r.uniform(-0.03, 0.03), -h / 2 - t - 0.02 + r.uniform(0, 0.05), 0.2)))
    return m


def door(cx: Ctx, w=1.0, h=2.05, color="roof_lo"):
    m = Mesh()
    dc = mix(cx.c(color), "#ffffff", 0.35)
    m.add(box(w, h, 0.06, dc, "timber", y0=0).xf((0, 0, -0.02)))
    tim = cx.c("timber_lo")
    for (px, py, bw, bh) in ((0, h, w + 0.24, 0.14), (-w / 2 - 0.06, 0, 0.12, h), (w / 2 + 0.06, 0, 0.12, h)):
        m.add(box(bw, bh, 0.12, mix(tim, "#ffffff", 0.4), "timber", y0=0).xf((px, py, 0.03)))
    m.add(box(0.07, 0.07, 0.06, cx.c("flower_gold"), "paint", y0=0).xf((w / 2 - 0.16, h * 0.48, 0.03)))
    m.add(box(w + 0.4, 0.14, 0.42, W_, "stone", y0=0).xf((0, -0.14, 0.2)))  # step
    return m


def roof_gable(cx: Ctx, W, D, wall_top, pitch_deg=40, ov=0.38, T=0.28, mat="roof", trim="timber"):
    """Thick gable roof, ridge along x. Returns (mesh, ridge_y)."""
    p = math.radians(pitch_deg)
    half = D / 2 + ov
    Ls = half / math.cos(p)
    Wl = W + 2 * ov * 0.9
    m = Mesh()
    fm = [trim, trim, mat, trim, trim, trim]
    tc = mix(cx.c("timber_lo"), "#ffffff", 0.3)
    slab = box(Wl, T, Ls, W_, mat, y0=-T / 2, mats=fm, cols=[tc, tc, W_, tc, tc, tc])
    a = -p
    c, s = math.cos(a), math.sin(a)
    yr, zr = c * (T / 2) - s * (Ls / 2), s * (T / 2) + c * (Ls / 2)
    rise = (D / 2) * math.tan(p)
    ridge = wall_top + rise + T / math.cos(p) * 0.6
    back = slab.xf((0, 0, 0), rot=(a, 0, 0)).xf((0, ridge - yr, -zr))
    m.add(back)
    m.add(back.xf(rot=(0, PI, 0)))
    m.add(box(Wl + 0.06, 0.16, 0.26, mix(cx.c("roof_lo"), "#ffffff", 0.2), "timber", y0=0).xf((0, ridge - 0.02, 0)))
    return m, ridge, rise


def gable_walls(cx: Ctx, W, D, wall_top, rise, mat="plaster", frame=True, inset=0.0):
    m = Mesh()
    prof = [(-D / 2 + inset, wall_top), (D / 2 - inset, wall_top), (0, wall_top + rise)]
    tim = mix(cx.c("timber"), "#ffffff", 0.45)
    for sx in (-1, 1):
        g = prism_x(0.22, prof, W_, mat)
        m.add(g.xf((sx * (W / 2 - 0.11), 0, 0)))
        if frame:
            x = sx * (W / 2 + 0.02)
            m.add(beam((x, wall_top, -D / 2), (x, wall_top, D / 2), 0.16, tim))
            m.add(beam((x, wall_top, 0), (x, wall_top + rise * 0.82, 0), 0.15, tim))
            m.add(beam((x, wall_top + 0.05, -D / 4), (x, wall_top + rise * 0.45, 0), 0.12, tim))
            m.add(beam((x, wall_top + 0.05, D / 4), (x, wall_top + rise * 0.45, 0), 0.12, tim))
    return m


def frame_face(cx: Ctx, width, y0, y1, openings=(), braces=True, post_every=1.3):
    """Timber framing on a wall face in local xy (facing +z). openings: [(x0, x1, ytop)]."""
    m = Mesh()
    tim = mix(cx.c("timber"), "#ffffff", 0.45)
    t = 0.17
    half = width / 2
    m.add(beam((-half, y0, 0), (half, y0, 0), t, tim))  # sole plate
    m.add(beam((-half, y1, 0), (half, y1, 0), t, tim))  # top plate
    xs = [-half + t / 2, half - t / 2]
    n = max(1, int(width / post_every))
    for i in range(1, n):
        x = -half + width * i / n
        if all(not (o[0] - 0.12 < x < o[1] + 0.12) for o in openings):
            xs.append(x)
    xs = sorted(xs)
    for x in xs:
        m.add(beam((x, y0, 0), (x, y1, 0), t, tim))
    if braces:
        for a, b in zip(xs[:-1], xs[1:]):
            if any(not (o[1] < a or o[0] > b) for o in openings):
                continue
            if b - a < 0.6:
                continue
            m.add(beam((a, y0 + 0.08, 0), (b, y1 - 0.08, 0), 0.12, tim) if (int(a * 10) % 2 == 0) else
                  beam((b, y0 + 0.08, 0), (a, y1 - 0.08, 0), 0.12, tim))
    return m


def chimney(cx: Ctx, x, z, base_y, top_y, mat="brick"):
    m = Mesh()
    m.add(box(0.62, top_y - base_y, 0.62, W_, mat, y0=base_y).xf((x, 0, z)))
    m.add(box(0.78, 0.14, 0.78, W_, "stone", y0=top_y).xf((x, 0, z)))
    m.add(box(0.3, 0.16, 0.3, cx.c("shadow"), "paint", y0=top_y + 0.14).xf((x, 0, z)))
    return m, (x, top_y + 0.32, z)


def wall_lamp(cx: Ctx):
    m = Mesh()
    iron = cx.c("ink")
    m.add(beam((0, 0, 0), (0, 0, 0.32), 0.05, iron, "paint"))
    m.add(box(0.2, 0.26, 0.2, cx.c("lamp"), "lamp", y0=-0.32).xf((0, 0, 0.36)))
    m.add(box(0.26, 0.05, 0.26, iron, "paint", y0=-0.06).xf((0, 0, 0.36)))
    m.add(box(0.24, 0.04, 0.24, iron, "paint", y0=-0.36).xf((0, 0, 0.36)))
    return m, (0, -0.19, 0.36)


# ------------------------------------------------------------------ cottages
COTTAGES = {
    "cottage_baker": dict(W=5.2, D=4.2, storeys=1, wall_h=2.9, roof="gable", ridge="x", pitch=42, base="stone",
                          walls="plaster", frame=True, door=(-0.9, "roof_lo"), windows=[(1.2, 1.35)], upper=[],
                          chimney=(1.6, -0.6), shutter="moss", roofmat="roof"),
    "cottage_tall": dict(W=4.4, D=4.2, storeys=2, wall_h=2.4, roof="gable", ridge="z", pitch=44, base="stone",
                         walls="plaster", frame=True, door=(0.9, "cloth"), windows=[(-0.9, 1.3)],
                         upper=[(-1.0, 1.1), (1.0, 1.1)], chimney=(-1.2, -1.2), shutter="roof", roofmat="roof", jetty=0.3),
    "cottage_stone": dict(W=5.6, D=4.4, storeys=1, wall_h=2.6, roof="gable", ridge="x", pitch=46, base="stone",
                          walls="stone", frame=False, door=(0.0, "moss"), windows=[(-1.7, 1.3), (1.7, 1.3)], upper=[],
                          chimney=(-2.0, 0.4), shutter="flower_blue", roofmat="thatch", roof_t=0.42),
    "cottage_shop": dict(W=5.4, D=4.4, storeys=2, wall_h=2.6, roof="gable", ridge="x", pitch=40, base="stone",
                         walls="plaster", lower="brick", frame=True, door=(1.5, "flower_blue"), windows=[(-0.9, 1.25)],
                         shopfront=True, upper=[(-1.4, 1.0), (1.4, 1.0)], chimney=(1.9, -0.8), shutter="cloth",
                         roofmat="roof", dormer=True),
    # ---- Bakery Lane buildings
    "bakery": dict(W=5.6, D=4.4, storeys=1, wall_h=3.0, roof="gable", ridge="x", pitch=44, base="stone",
                   walls="plaster", frame=True, door=(-1.3, "roof_lo"), windows=[(1.2, 1.7)], upper=[],
                   chimney=(1.9, -0.7), shutter="flower_gold", roofmat="roof", oven=True, sign=("loaf", -2.35)),
    "inn": dict(W=6.6, D=4.6, storeys=2, wall_h=2.6, roof="gable", ridge="x", pitch=42, base="stone",
                walls="plaster", lower="stone", frame=True, door=(0.0, "timber"), windows=[(-2.0, 1.3), (2.0, 1.3)],
                upper=[(-2.3, 1.0), (0.0, 1.0), (2.3, 1.0)], chimney=(-2.5, -0.8), shutter="moss", roofmat="roof",
                jetty=0.35, dormer=True, sign=("mug", 1.05)),
    "flower_shop": dict(W=4.8, D=4.0, storeys=1, wall_h=2.8, roof="gable", ridge="z", pitch=46, base="stone",
                        walls="plaster", frame=True, door=(1.3, "flower_blue"), windows=[], shopfront=True, upper=[],
                        chimney=(-1.3, -1.0), shutter="flower_rose", roofmat="thatch", roof_t=0.4,
                        sign=("flower", 2.15), flowers_front=True),
}


def hanging_sign_mesh(cx: Ctx, icon="loaf"):
    """Iron bracket sticking out of a wall (+z) with a painted board facing the camera. No text."""
    m = Mesh()
    iron = cx.c("ink")
    m.add(box(0.1, 0.36, 0.06, iron, "paint", y0=-0.18))                           # wall plate
    m.add(beam((0, 0.12, 0), (0, 0.12, 0.85), 0.05, iron, "paint"))                # arm
    m.add(beam((0, -0.15, 0.02), (0, 0.1, 0.5), 0.035, iron, "paint"))             # brace
    m.add(box(0.06, 0.06, 0.06, cx.c("flower_gold"), "paint", y0=0.09).xf((0, 0, 0.86)))
    m.add(box(0.62, 0.04, 0.04, iron, "paint", y0=0.1).xf((0, 0, 0.62)))          # crossbar
    for x in (-0.26, 0.26):
        m.add(box(0.02, 0.2, 0.02, iron, "paint", y0=-0.1).xf((x, 0, 0.62)))
    b = Mesh()
    bw, bh = 0.72, 0.5
    b.add(box(bw, bh, 0.05, mix(cx.c("timber"), "#ffffff", 0.35), "timber", y0=-bh))
    b.add(box(bw - 0.1, bh - 0.1, 0.06, mix(cx.c("plaster_hi"), "#ffffff", 0.1), "paint", y0=-bh + 0.05))
    cy = -bh / 2
    if icon == "loaf":
        b.add(sphere(0.2, 7, 4, cx.c("timber_hi"), squash=(1.3, 0.6, 0.2), col_bottom=cx.c("timber")).xf((0, cy, 0.04)))
        for x in (-0.1, 0.0, 0.1):
            b.add(box(0.03, 0.1, 0.02, cx.c("flower_gold"), "paint", y0=cy - 0.02).xf((x, 0, 0.08)))
    elif icon == "mug":
        b.add(box(0.22, 0.26, 0.04, cx.c("flower_gold"), "paint", y0=cy - 0.14).xf((-0.03, 0, 0.05)))
        b.add(box(0.26, 0.07, 0.045, cx.c("white"), "paint", y0=cy + 0.1).xf((-0.03, 0, 0.055)))
        b.add(box(0.07, 0.16, 0.04, cx.c("flower_gold"), "paint", y0=cy - 0.08).xf((0.14, 0, 0.05)))
    elif icon == "flower":
        b.add(box(0.03, 0.2, 0.04, cx.c("moss"), "paint", y0=cy - 0.16).xf((0, 0, 0.05)))
        for k in range(5):
            a = k * math.tau / 5
            b.add(sphere(0.055, 5, 3, cx.c("flower_rose")).xf((math.cos(a) * 0.08, cy + 0.06 + math.sin(a) * 0.08, 0.06)))
        b.add(sphere(0.045, 5, 3, cx.c("flower_gold")).xf((0, cy + 0.06, 0.08)))
    elif icon == "key":
        b.add(box(0.26, 0.05, 0.04, cx.c("flower_gold"), "paint", y0=cy - 0.02).xf((0.04, 0, 0.05)))
        b.add(cylinder(0.08, 0.08, 0.04, 8, cx.c("flower_gold"), "paint", y0=0).xf((-0.12, cy, 0.05), rot=(PI / 2, 0, 0)))
    m.add(b.xf((0, -0.08, 0.62)))
    return m


def hanging_sign(cx: Ctx, icon) -> Piece:
    pc = Piece(f"hanging_sign_{icon}")
    m = hanging_sign_mesh(cx, icon)
    pc.mesh = m.xf((0, 2.6, 0))
    pc.size = [0.8, 2.8, 0.9]
    return pc


def bread_oven(cx: Ctx, W, D, plinth):
    """Brick bread oven built onto the +x gable: a rounded hump, a glowing mouth, its own stubby flue."""
    m = Mesh()
    ox = W / 2 + 0.75
    m.add(box(1.5, 0.5, 2.0, W_, "stone", y0=0).xf((ox, 0, 0.1)))
    m.add(box(1.4, 1.5, 1.9, W_, "brick", y0=0.5).xf((ox, 0, 0.1)))
    m.add(cylinder(0.95, 0.95, 1.9, 10, W_, "brick", caps=True, y0=-0.95).xf((ox, 2.0, 0.1), rot=(PI / 2, 0, 0), scale=(0.75, 1, 0.45)))
    mouth_z = 0.1 + 0.97
    m.add(box(0.7, 0.55, 0.06, cx.c("lamp"), "lamp", y0=0.75).xf((ox, 0, mouth_z)))
    m.add(box(0.9, 0.12, 0.14, W_, "stone", y0=1.32).xf((ox, 0, mouth_z)))
    m.add(box(0.9, 0.1, 0.18, W_, "stone", y0=0.66).xf((ox, 0, mouth_z + 0.02)))
    flue, top = chimney(cx, ox + 0.2, -0.4, 1.8, 3.25)
    m.add(flue)
    # stacked firewood by the oven
    for i in range(3):
        for j in range(3 - i):
            m.add(cylinder(0.09, 0.09, 0.7, 6, mix(cx.c("timber"), "#ffffff", 0.2 * (j % 2)), "timber", y0=-0.35)
                  .xf((ox + 0.95, 0.1 + i * 0.17, 0.55 + j * 0.2 + i * 0.1), rot=(0, 0, PI / 2)))
    return m, top, [ox, 1.0, mouth_z + 0.25]


def cottage(cx: Ctx, name, spec) -> Piece:
    pc = Piece(name)
    pc.kind = "building"
    W, D, wh, ns = spec["W"], spec["D"], spec["wall_h"], spec["storeys"]
    plinth = 0.45
    jet = spec.get("jetty", 0.0)
    m = Mesh()
    # plinth / base course
    m.add(box(W + 0.16, plinth, D + 0.16, W_, "stone", y0=0))
    wall_top = plinth + wh * ns
    # walls
    lower_mat = spec.get("lower", spec["walls"])
    if ns == 2:
        m.add(box(W, wh, D, W_, lower_mat, y0=plinth))
        m.add(box(W + 2 * jet * 0.0, wh, D + jet, W_, spec["walls"], y0=plinth + wh).xf((0, 0, jet / 2)))
        if jet:
            tim = mix(cx.c("timber"), "#ffffff", 0.4)
            for i in range(7):
                x = -W / 2 + 0.2 + i * (W - 0.4) / 6
                m.add(box(0.16, 0.16, 0.3, tim, "timber", y0=plinth + wh - 0.16).xf((x, 0, D / 2 + 0.12)))
    else:
        m.add(box(W, wh, D, W_, spec["walls"], y0=plinth))
    front_z = D / 2 + (jet if ns == 2 else 0)
    # door + ground windows
    dx, dcol = spec["door"]
    m.add(door(cx, color=dcol).xf((dx, plinth, D / 2 + 0.02)))
    pc.markers["doors"].append([dx, plinth, D / 2 + 0.3])
    openings = [(dx - 0.6, dx + 0.6, plinth + 2.1)]
    wy = plinth + 1.45
    for i, (wx, ww) in enumerate(spec["windows"]):
        m.add(window(cx, ww * 0.62, 0.95, spec["shutter"], True, seed=i).xf((wx, wy, D / 2 + 0.02)))
        openings.append((wx - ww / 2, wx + ww / 2, wy + 0.5))
        pc.markers["windows"].append([wx, wy, D / 2 + 0.1])
    if spec.get("shopfront"):
        # wide shop window with a little striped awning
        m.add(box(1.9, 1.2, 0.05, W_, "window", y0=plinth + 0.6).xf((-1.0, 0, D / 2 + 0.0)))
        tim = mix(cx.c("timber"), "#ffffff", 0.4)
        for (px, py, bw, bh) in ((-1.0, plinth + 0.55, 2.1, 0.1), (-1.0, plinth + 1.82, 2.1, 0.1),
                                 (-2.0, plinth + 0.55, 0.1, 1.35), (0.0, plinth + 0.55, 0.1, 1.35), (-1.0, plinth + 0.55, 0.06, 1.3)):
            m.add(box(bw, bh, 0.12, tim, "timber", y0=py).xf((px, 0, D / 2 + 0.04)))
        aw = box(2.5, 0.06, 0.9, W_, "awning", y0=0).xf((0, 0, 0.45), rot=(0.35, 0, 0)).xf((-1.0, plinth + 2.25, D / 2))
        m.add(aw)
        openings.append((-2.1, 0.1, plinth + 2.0))
        pc.markers["windows"].append([-1.0, plinth + 1.2, D / 2 + 0.1])
        # flower crate under the shop window
        m.add(flower_crate_mesh(cx, 1.6, 0.35, 0.35, seed=7).xf((-1.0, 0, D / 2 + 0.3)))
    if spec["frame"]:
        if ns == 2:
            if spec.get("lower", spec["walls"]) == "plaster":
                m.add(frame_face(cx, W, plinth, plinth + wh, openings).xf((0, 0, D / 2 + 0.03)))
            up_open = [(ux - uw / 2, ux + uw / 2, 0) for ux, uw in spec["upper"]]
            m.add(frame_face(cx, W, plinth + wh, wall_top, up_open).xf((0, 0, front_z + 0.03)))
            for sx in (-1, 1):
                f = frame_face(cx, D + jet, plinth + wh, wall_top, (), True).xf((0, 0, 0), rot=(0, sx * PI / 2, 0))
                m.add(f.xf((sx * (W / 2 + 0.03), 0, jet / 2)))
        else:
            m.add(frame_face(cx, W, plinth, wall_top, openings).xf((0, 0, D / 2 + 0.03)))
            for sx in (-1, 1):
                m.add(frame_face(cx, D, plinth, wall_top, (), True).xf((0, 0, 0), rot=(0, sx * PI / 2, 0)).xf((sx * (W / 2 + 0.03), 0, 0)))
    else:
        # stone cottage: quoins + lintels instead of framing
        for sx in (-1, 1):
            for k in range(int(wh / 0.45)):
                y = plinth + k * 0.45
                wq = 0.42 if k % 2 == 0 else 0.3
                m.add(box(wq, 0.4, 0.1, mix(cx.c("stone_hi"), "#ffffff", 0.2), "stone", y0=y).xf((sx * (W / 2 - wq / 2 + 0.02), 0, D / 2 + 0.03)))
        for (wx, ww) in spec["windows"]:
            m.add(box(ww * 0.62 + 0.5, 0.2, 0.12, W_, "timber", y0=wy + 0.55).xf((wx, 0, D / 2 + 0.05)))
    # upper windows
    for i, (ux, uw) in enumerate(spec["upper"]):
        m.add(window(cx, uw * 0.62, 0.85, spec["shutter"], i % 2 == 0, seed=10 + i).xf((ux, plinth + wh + 1.35, front_z + 0.02)))
        pc.markers["windows"].append([ux, plinth + wh + 1.35, front_z + 0.1])
    # roof
    rmat = spec.get("roofmat", "roof")
    T = spec.get("roof_t", 0.28)
    if spec["ridge"] == "x":
        roof, ridge, rise = roof_gable(cx, W, D + jet, wall_top, spec["pitch"], T=T, mat=rmat)
        m.add(roof.xf((0, 0, jet / 2)))
        m.add(gable_walls(cx, W, D + jet, wall_top, rise, spec["walls"] if spec["walls"] != "stone" else "stone",
                          frame=spec["frame"]).xf((0, 0, jet / 2)))
    else:
        roof, ridge, rise = roof_gable(cx, D + jet, W, wall_top, spec["pitch"], T=T, mat=rmat)
        m.add(roof.xf(rot=(0, PI / 2, 0)).xf((0, 0, jet / 2)))
        g = gable_walls(cx, D + jet, W, wall_top, rise, spec["walls"], frame=spec["frame"])
        m.add(g.xf(rot=(0, PI / 2, 0)).xf((0, 0, jet / 2)))
        # attic window in the front gable
        m.add(window(cx, 0.55, 0.65, None, False).xf((0, wall_top + rise * 0.35, front_z + 0.13)))
        pc.markers["windows"].append([0, wall_top + rise * 0.35, front_z + 0.2])
    if spec.get("dormer"):
        dw, dd = 1.5, 1.6
        dm = Mesh()
        dm.add(box(dw, 1.2, dd, W_, "plaster", y0=0))
        dm.add(window(cx, 0.6, 0.7, None, False).xf((0, 0.62, dd / 2 + 0.02)))
        r2, rr, rs = roof_gable(cx, dd, dw, 1.2, 45, ov=0.22, T=0.2)
        dm.add(r2.xf(rot=(0, PI / 2, 0)))
        dm.add(gable_walls(cx, dd, dw, 1.2, rs, "plaster", frame=False).xf(rot=(0, PI / 2, 0)))
        m.add(dm.xf((0.0, wall_top - 0.1, D / 2 - dd / 2 + 0.25)))
        pc.markers["windows"].append([0.0, wall_top + 0.52, D / 2 + 0.45])
    # chimney
    chx, chz = spec["chimney"]
    if spec["ridge"] == "z":
        ch, top = chimney(cx, chx, chz, wall_top - 0.2, ridge + 0.6)
    else:
        ch, top = chimney(cx, chx, chz, wall_top - 0.2, ridge + 0.75)
    m.add(ch)
    pc.markers["chimneys"].append(list(top))
    if spec.get("oven"):
        om, otop, omouth = bread_oven(cx, W, D, plinth)
        m.add(om)
        pc.markers.setdefault("ovens", []).append(list(otop))
        pc.markers["lamps"].append(omouth)
        pc.blockers.append([W / 2, -D / 2 + 0.6, W / 2 + 1.75, D / 2 + 0.3])
    if spec.get("sign"):
        icon, sx = spec["sign"]
        m.add(hanging_sign_mesh(cx, icon).xf((sx, plinth + 2.55, front_z + 0.02)))
    if spec.get("flowers_front"):
        r = rng(cx.seed, "fshop")
        for i, x in enumerate((-2.0, -1.45, 2.05)):
            m.add(flower_crate_mesh(cx, 0.55, 0.45, 0.4 + 0.15 * (i % 2), seed=20 + i).xf((x, 0, D / 2 + 0.75)))
        for i in range(5):
            x = -2.1 + i * 0.36
            m.add(cylinder(0.12, 0.09, 0.22, 7, cx.c("roof_hi"), "paint", y0=0).xf((x, 0, D / 2 + 1.25)))
            m.add(sphere(0.15, 6, 3, cx.c("grass"), col_bottom=cx.c("moss")).xf((x, 0.3, D / 2 + 1.25)))
            m.add(sphere(0.07, 5, 3, cx.c(r.choice(["flower_rose", "flower_gold", "flower_blue", "white"]))).xf((x + 0.03, 0.42, D / 2 + 1.3)))
        pc.blockers.append([-2.4, D / 2, -1.1, D / 2 + 1.45])
    # wall lamp beside the door
    lm, lp = wall_lamp(cx)
    lx = dx + (0.85 if dx < W / 2 - 1.2 else -0.85)
    m.add(lm.xf((lx, plinth + 2.25, D / 2 + 0.02)))
    pc.markers["lamps"].append([lx + lp[0], plinth + 2.25 + lp[1], D / 2 + 0.02 + lp[2]])
    pc.mesh = m.ao(0, 1.4, 0.3)
    pc.blockers.append([-W / 2 - 0.1, -D / 2 - 0.1, W / 2 + 0.1, D / 2 + 0.15 + (jet if ns == 2 else 0) * 0])
    pc.size = [W + 0.2, ridge + 1.0, D + 0.2]
    return pc


# ------------------------------------------------------------------ ground pieces
def terrace(cx: Ctx, w, d, h, top="cobble", wall="stone", coping=True, name=None, gaps=(), sides=True) -> Piece:
    """Raised terrace block: `top` walk surface, stone retaining faces, coping rim (with gaps for stairs)."""
    pc = Piece(name or f"terrace_{w:g}x{d:g}x{h:g}")
    pc.kind = "terrace"
    m = Mesh()
    m.add(box(w, h, d, W_, wall, y0=0, mats=[wall, wall, top, wall, wall, wall]))
    cc = mix(cx.c("stone_hi"), "#ffffff", 0.15)
    if coping:
        xs = [-w / 2 - 0.05]
        for g0, g1 in sorted(gaps):
            xs += [g0, g1]
        xs.append(w / 2 + 0.05)
        for a, b in zip(xs[0::2], xs[1::2]):
            if b - a > 0.05:
                m.add(box(b - a, 0.14, 0.36, cc, "stone", y0=h - 0.06).xf(((a + b) / 2, 0, d / 2 - 0.13)))
        if sides:
            for sx in (-1, 1):
                m.add(box(0.36, 0.14, d + 0.1, cc, "stone", y0=h - 0.06).xf((sx * (w / 2 - 0.13), 0, 0)))
    # moss + grass tufts along the wall foot
    r = rng(cx.seed, "tmoss", w, d, h)
    for i in range(int(w * 1.4)):
        x = -w / 2 + r.random() * w
        if any(g0 - 0.3 < x < g1 + 0.3 for g0, g1 in gaps):
            continue
        m.add(sphere(r.uniform(0.12, 0.22), 6, 3, cx.c("moss" if r.random() < 0.5 else "grass"), squash=(1.4, 0.6, 0.8))
              .xf((x, 0.04, d / 2 + 0.06)))
    pc.mesh = m.ao(0, max(0.8, h), 0.25)
    pc.size = [w, h, d]
    return pc


def stairs(cx: Ctx, width, rise, step=0.2, run=0.4, name=None) -> Piece:
    """Stairs climbing toward -z. Bottom step front edge at z=+L/2, top at z=-L/2."""
    n = max(2, round(rise / step))
    st = rise / n
    L = n * run
    pc = Piece(name or f"stairs_{width:g}x{rise:g}")
    pc.kind = "stairs"
    m = Mesh()
    for i in range(n):
        h = st * (i + 1)
        z1 = L / 2 - i * run
        z0 = -L / 2
        m.add(box(width, h, z1 - z0, W_, "stone", y0=0).xf((0, 0, (z0 + z1) / 2)))
        m.add(box(width, 0.05, 0.08, mix(cx.c("stone_hi"), "#ffffff", 0.3), "stone", y0=h - 0.05).xf((0, 0, z1 - 0.02)))
    cc = mix(cx.c("stone_hi"), "#ffffff", 0.15)
    for sx in (-1, 1):
        prof = [(L / 2 + 0.05, 0), (L / 2 + 0.05, 0.55), (-L / 2, rise + 0.55), (-L / 2, 0)]
        m.add(prism_x(0.32, prof, W_, "stone").xf((sx * (width / 2 + 0.16), 0, 0)))
        # coping on the cheek wall
        ln = math.hypot(L, rise)
        ang = math.atan2(rise, L)
        cop = box(0.4, 0.1, ln, cc, "stone", y0=0).xf(rot=(ang, 0, 0))
        m.add(cop.xf((sx * (width / 2 + 0.16), 0.55 + rise / 2, 0)))
        m.add(box(0.44, 0.5, 0.44, cc, "stone", y0=0).xf((sx * (width / 2 + 0.16), 0, L / 2 - 0.1)))
        m.add(sphere(0.16, 6, 4, cc).xf((sx * (width / 2 + 0.16), 0.62, L / 2 - 0.1)))
    pc.mesh = m.ao(0, rise + 0.5, 0.2)
    pc.size = [width + 0.64, rise + 0.6, L]
    pc.stairs = {"width": width, "rise": rise, "length": L, "steps": n}
    return pc


def retaining_wall(cx: Ctx, length, h, name=None) -> Piece:
    pc = Piece(name or f"wall_{length:g}x{h:g}")
    pc.kind = "wall"
    m = Mesh()
    m.add(box(length, h, 0.5, W_, "stone", y0=0))
    m.add(box(length + 0.1, 0.14, 0.62, mix(cx.c("stone_hi"), "#ffffff", 0.15), "stone", y0=h))
    pc.mesh = m.ao(0, h, 0.25)
    pc.blockers.append([-length / 2, -0.3, length / 2, 0.3])
    pc.size = [length, h + 0.14, 0.62]
    return pc


def ground_slab(cx: Ctx, w, d, mat="grass", h=0.0, name=None) -> Piece:
    pc = Piece(name or f"ground_{mat}_{w:g}x{d:g}")
    pc.kind = "ground"
    m = Mesh()
    if h > 0:
        m.add(box(w, h, d, W_, mat, y0=0, mats=["stone", "stone", mat, "stone", "stone", "stone"]))
    else:
        m.quad((-w / 2, 0, d / 2), (w / 2, 0, d / 2), (w / 2, 0, -d / 2), (-w / 2, 0, -d / 2), W_,
               ((-w / 2, d / 2), (w / 2, d / 2), (w / 2, -d / 2), (-w / 2, -d / 2)), mat)
    pc.mesh = m
    pc.size = [w, max(h, 0.01), d]
    return pc


def hills(cx: Ctx, width=90, seed=1) -> Piece:
    """Distant low-poly hills + hedgerow mounds: the far band the haze softens."""
    pc = Piece("hills")
    pc.kind = "backdrop"
    r = rng(cx.seed, "hills", seed)
    m = Mesh()
    for i in range(14):
        x = -width / 2 + i * width / 13 + r.uniform(-3, 3)
        rad = r.uniform(7, 13)
        hgt = r.uniform(3.5, 8)
        col = cx.c(r.choice(["grass", "moss", "grass_hi"]))
        # 22 x 10 segments: at 9 x 5 the big domes showed as huge flat facets on tall (portrait phone) views
        m.add(sphere(rad, 22, 10, col, squash=(1.0, hgt / rad, 0.55), noise=0.035, rnd=r, col_bottom=cx.c("moss"))
              .xf((x, -0.5, r.uniform(-6, 6))))
    for i in range(22):
        x = -width / 2 + r.random() * width
        rad = r.uniform(1.4, 2.6)
        m.add(sphere(rad, 7, 4, cx.c("leaf_deep" if r.random() < 0.5 else "moss"), squash=(1, 1.15, 1), noise=0.15, rnd=r)
              .xf((x, rad * 0.8 + r.uniform(1, 4), r.uniform(-3, 5))))
    pc.mesh = m
    pc.size = [width, 12, 20]
    return pc


# ------------------------------------------------------------------ props
def flower_crate_mesh(cx: Ctx, w=0.9, d=0.45, h=0.45, seed=0):
    m = Mesh()
    tc = mix(cx.c("timber_hi"), "#ffffff", 0.35)
    m.add(box(w, h, d, tc, "timber", y0=0))
    m.add(box(w - 0.08, 0.04, d - 0.08, cx.c("timber_lo"), "paint", y0=h - 0.02))
    r = rng(cx.seed, "fcrate", seed)
    cols = [cx.c("flower_rose"), cx.c("flower_gold"), cx.c("flower_blue"), cx.c("white"), cx.c("flower_rose")]
    nx = max(3, int(w / 0.14))
    for i in range(nx):
        for j in range(2):
            x = -w / 2 + (i + 0.5) * w / nx + r.uniform(-0.02, 0.02)
            z = -d / 4 + j * d / 2
            m.add(sphere(0.09, 5, 3, cx.c("grass" if r.random() < 0.6 else "moss")).xf((x, h + 0.06, z)))
            if r.random() < 0.8:
                m.add(sphere(0.07, 5, 3, r.choice(cols)).xf((x + r.uniform(-0.03, 0.03), h + 0.15 + r.uniform(0, 0.06), z + 0.03)))
    return m


def flower_crate(cx: Ctx) -> Piece:
    pc = Piece("flower_crate")
    pc.mesh = flower_crate_mesh(cx).ao(0, 0.5, 0.25)
    pc.blockers.append([-0.5, -0.28, 0.5, 0.28])
    pc.size = [0.9, 0.7, 0.45]
    return pc


def barrel(cx: Ctx) -> Piece:
    pc = Piece("barrel")
    m = Mesh()
    tc = mix(cx.c("timber_hi"), "#ffffff", 0.3)
    m.add(cylinder(0.31, 0.37, 0.45, 10, tc, "timber", caps=False, y0=0))
    m.add(cylinder(0.37, 0.31, 0.45, 10, tc, "timber", caps=False, y0=0.45))
    m.add(cylinder(0.3, 0.3, 0.02, 10, cx.c("timber_lo"), "paint", y0=0.9))
    iron = cx.c("shadow")
    for y in (0.12, 0.72):
        m.add(cylinder(0.36, 0.38, 0.07, 10, iron, "paint", caps=False, y0=y))
    pc.mesh = m.ao(0, 0.9, 0.25)
    pc.blockers.append([-0.38, -0.38, 0.38, 0.38])
    pc.size = [0.76, 0.92, 0.76]
    return pc


def crate(cx: Ctx) -> Piece:
    pc = Piece("crate")
    m = Mesh()
    s = 0.72
    m.add(box(s, s, s, mix(cx.c("timber_hi"), "#ffffff", 0.4), "timber", y0=0))
    ec = mix(cx.c("timber"), "#ffffff", 0.2)
    e = 0.08
    for (x, z) in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
        m.add(box(e, s + 0.01, e, ec, "timber", y0=0).xf((x * (s / 2 - e / 2 + 0.01), 0, z * (s / 2 - e / 2 + 0.01))))
    for y in (0, s - e):
        m.add(box(s + 0.02, e, e, ec, "timber", y0=y).xf((0, 0, s / 2 - e / 2 + 0.01)))
        m.add(box(e, e, s + 0.02, ec, "timber", y0=y).xf((s / 2 - e / 2 + 0.01, 0, 0)))
    m.add(beam((-s / 2, 0.05, s / 2 + 0.01), (s / 2, s - 0.05, s / 2 + 0.01), 0.07, ec))
    pc.mesh = m.ao(0, s, 0.25)
    pc.blockers.append([-0.4, -0.4, 0.4, 0.4])
    pc.size = [s, s, s]
    return pc


def sign(cx: Ctx) -> Piece:
    """Hanging bakery sign on a post: a painted loaf, no text."""
    pc = Piece("sign")
    m = Mesh()
    tc = mix(cx.c("timber"), "#ffffff", 0.3)
    m.add(box(0.14, 2.6, 0.14, tc, "timber", y0=0))
    m.add(box(0.95, 0.1, 0.1, tc, "timber", y0=2.35).xf((0.45, 0, 0)))
    m.add(beam((0.07, 2.0, 0), (0.6, 2.36, 0), 0.06, tc))
    iron = cx.c("ink")
    for x in (0.4, 0.82):
        m.add(box(0.025, 0.22, 0.025, iron, "paint", y0=2.13).xf((x, 0, 0)))
    board = Mesh()
    board.add(box(0.66, 0.46, 0.06, mix(cx.c("plaster_hi"), "#ffffff", 0.1), "timber", y0=0))
    for sz in (1, -1):
        board.add(box(0.44, 0.15, 0.02, cx.c("flower_gold"), "paint", y0=0.15).xf((0, 0, sz * 0.035)))
        board.add(box(0.36, 0.05, 0.022, cx.c("timber_hi"), "paint", y0=0.25).xf((0, 0, sz * 0.036)))
        for x in (-0.12, 0.0, 0.12):
            board.add(box(0.03, 0.08, 0.024, cx.c("timber"), "paint", y0=0.18).xf((x, 0, sz * 0.037)))
    m.add(board.xf((0.61, 1.67, 0)))
    pc.mesh = m.ao(0, 1.0, 0.2)
    pc.blockers.append([-0.12, -0.12, 0.12, 0.12])
    pc.size = [1.0, 2.7, 0.2]
    return pc


def lamp_post(cx: Ctx) -> Piece:
    pc = Piece("lamp_post")
    m = Mesh()
    iron = cx.c("ink")
    ironl = cx.c("shadow")
    m.add(box(0.4, 0.3, 0.4, W_, "stone", y0=0))
    m.add(cylinder(0.09, 0.06, 2.5, 8, ironl, "paint", y0=0.3))
    m.add(cylinder(0.12, 0.12, 0.08, 8, iron, "paint", y0=1.2))
    m.add(box(0.28, 0.06, 0.28, iron, "paint", y0=2.78))
    m.add(box(0.22, 0.38, 0.22, cx.c("lamp"), "lamp", y0=2.84))
    for (x, z) in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
        m.add(box(0.035, 0.4, 0.035, iron, "paint", y0=2.83).xf((x * 0.12, 0, z * 0.12)))
    m.add(cylinder(0.22, 0.02, 0.22, 4, iron, "paint", y0=3.22).xf(rot=(0, PI / 4, 0)))
    m.add(box(0.06, 0.12, 0.06, iron, "paint", y0=3.43))
    pc.mesh = m
    pc.markers["lamps"].append([0, 3.03, 0])
    pc.blockers.append([-0.22, -0.22, 0.22, 0.22])
    pc.size = [0.4, 3.55, 0.4]
    return pc


def fence(cx: Ctx, length=2.0) -> Piece:
    pc = Piece("fence")
    m = Mesh()
    tc = mix(cx.c("timber_hi"), "#ffffff", 0.25)
    for x in (-length / 2, length / 2):
        m.add(box(0.12, 1.0, 0.12, tc, "timber", y0=0).xf((x, 0, 0)))
        m.add(cylinder(0.08, 0.0, 0.1, 4, tc, "timber", y0=1.0).xf((x, 0, 0)))
    for y in (0.35, 0.75):
        m.add(box(length, 0.1, 0.06, tc, "timber", y0=y).xf((0, 0, 0.06)))
    pc.mesh = m.ao(0, 1, 0.2)
    pc.blockers.append([-length / 2, -0.12, length / 2, 0.12])
    pc.size = [length, 1.1, 0.12]
    return pc


def bench(cx: Ctx) -> Piece:
    pc = Piece("bench")
    m = Mesh()
    tc = mix(cx.c("timber_hi"), "#ffffff", 0.3)
    m.add(box(1.6, 0.08, 0.42, tc, "timber", y0=0.42))
    m.add(box(1.6, 0.36, 0.06, tc, "timber", y0=0.6).xf((0, 0, -0.2)))
    for x in (-0.68, 0.68):
        m.add(box(0.1, 0.42, 0.38, cx.c("shadow"), "paint", y0=0).xf((x, 0, 0)))
    pc.mesh = m.ao(0, 0.5, 0.2)
    pc.blockers.append([-0.82, -0.25, 0.82, 0.25])
    pc.size = [1.6, 0.96, 0.45]
    return pc


def market_stall(cx: Ctx) -> Piece:
    pc = Piece("market_stall")
    m = Mesh()
    W, D = 3.0, 1.6
    tc = mix(cx.c("timber"), "#ffffff", 0.35)
    for (x, z, h) in ((-W / 2, D / 2, 2.25), (W / 2, D / 2, 2.25), (-W / 2, -D / 2, 2.65), (W / 2, -D / 2, 2.65)):
        m.add(box(0.13, h, 0.13, tc, "timber", y0=0).xf((x, 0, z)))
    # counter
    m.add(box(W - 0.1, 0.85, 0.75, mix(cx.c("timber_hi"), "#ffffff", 0.35), "timber", y0=0).xf((0, 0, D / 2 - 0.4)))
    m.add(box(W + 0.1, 0.08, 0.9, mix(cx.c("timber_hi"), "#ffffff", 0.5), "timber", y0=0.85).xf((0, 0, D / 2 - 0.4)))
    # cloth skirt panel on the counter front
    m.add(box(W - 0.3, 0.55, 0.03, W_, "awning", y0=0.18).xf((0, 0, D / 2 - 0.01)))
    # awning: sloped striped slab with a scalloped valance
    ang = math.atan2(0.4, D)
    L = math.hypot(D + 0.7, 0.4)
    aw = box(W + 0.5, 0.07, L, W_, "awning", y0=0)
    m.add(aw.xf(rot=(ang, 0, 0)).xf((0, 2.42, 0.25)))
    fz = 0.25 + (L / 2) * math.cos(ang)
    fy = 2.42 - (L / 2) * math.sin(ang)
    cols = [cx.c("flower_rose"), cx.c("white")]
    nf = 10
    for i in range(nf):
        x0 = -(W + 0.5) / 2 + i * (W + 0.5) / nf
        x1 = x0 + (W + 0.5) / nf
        c = cols[i % 2]
        a, b, cc = (x0, fy, fz + 0.01), (x1, fy, fz + 0.01), ((x0 + x1) / 2, fy - 0.24, fz + 0.01)
        m.tri(a, cc, b, c, mat="paint")
        m.tri(a, b, cc, c, mat="paint")
    # goods: loaves, apples, a flower crate
    r = rng(cx.seed, "stall")
    for i in range(6):
        x = -1.2 + i * 0.32
        m.add(sphere(0.13, 6, 4, cx.c("timber_hi"), squash=(1.4, 0.7, 0.8), col_bottom=cx.c("timber")).xf((x, 0.98, D / 2 - 0.55)))
        m.add(box(0.03, 0.02, 0.1, cx.c("flower_gold"), "paint", y0=1.06).xf((x, 0, D / 2 - 0.55)))
    m.add(box(0.7, 0.18, 0.45, mix(cx.c("timber_hi"), "#ffffff", 0.3), "timber", y0=0.89).xf((0.95, 0, D / 2 - 0.45)))
    for i in range(12):
        m.add(sphere(0.07, 5, 3, cx.c("flower_rose" if i % 3 else "roof_hi")).xf((0.72 + (i % 4) * 0.15, 1.1, D / 2 - 0.6 + (i // 4) * 0.14)))
    m.add(barrel(cx).mesh.xf((W / 2 + 0.55, 0, -0.2)))
    m.add(crate(cx).mesh.xf((-W / 2 - 0.55, 0, -0.3), rot=(0, 0.3, 0)))
    m.add(crate(cx).mesh.xf((-W / 2 - 0.5, 0.72, -0.3), rot=(0, -0.2, 0), scale=0.8))
    pc.mesh = m.ao(0, 1.0, 0.25)
    pc.blockers.append([-W / 2 - 0.95, -D / 2 - 0.1, W / 2 + 0.95, D / 2 + 0.1])
    pc.size = [W + 2, 2.7, D]
    pc.markers["bunting"] = [[-W / 2, 2.3, D / 2], [W / 2, 2.3, D / 2]]
    pc.markers["vendor"] = [0.7, 0, D / 2 + 0.7]
    return pc


def bunting(cx: Ctx, p0, p1, sag=0.5, spacing=0.42, name="bunting") -> Piece:
    """String of pennants between two world points (double-sided triangles)."""
    pc = Piece(name)
    m = Mesh()
    import numpy as np
    p0, p1 = np.array(p0, float), np.array(p1, float)
    L = float(np.linalg.norm(p1 - p0))
    n = max(2, int(L / spacing))
    pts = []
    for i in range(n + 1):
        t = i / n
        p = p0 + (p1 - p0) * t
        p[1] -= sag * 4 * t * (1 - t)
        pts.append(p)
    rope = cx.c("timber_lo")
    for a, b in zip(pts[:-1], pts[1:]):
        m.add(beam(tuple(a), tuple(b), 0.025, rope, "paint"))
    cols = [cx.c("flower_rose"), cx.c("flower_gold"), cx.c("flower_blue"), cx.c("white"), cx.c("moss")]
    d = (p1 - p0) / L
    for i, (a, b) in enumerate(zip(pts[:-1], pts[1:])):
        mid = (a + b) / 2
        w = (b - a) * 0.42
        tip = mid + np.array([0, -0.32, 0])
        c = cols[i % len(cols)]
        A, B = tuple(mid - w), tuple(mid + w)
        m.tri(A, tuple(tip), B, c, mat="paint")
        m.tri(A, B, tuple(tip), c, mat="paint")
    pc.mesh = m
    pc.size = [L, sag + 0.4, 0.05]
    return pc


def laundry(cx: Ctx, p0, p1, sag=0.25, base0=0.0, base1=0.0, name="laundry", seed=0) -> Piece:
    """Washing line between two posts (world points at rope height), sheets and shirts as double-sided cards."""
    import numpy as np
    pc = Piece(name)
    m = Mesh()
    r = rng(cx.seed, "laundry", seed)
    p0, p1 = np.array(p0, float), np.array(p1, float)
    tc = mix(cx.c("timber"), "#ffffff", 0.3)
    for p, b in ((p0, base0), (p1, base1)):
        m.add(box(0.12, p[1] - b + 0.15, 0.12, tc, "timber", y0=b).xf((p[0], 0, p[2])))
        m.add(box(0.12, 0.08, 0.5, tc, "timber", y0=p[1] + 0.02).xf((p[0], 0, p[2])))
    L = float(np.linalg.norm(p1 - p0))
    n = max(2, int(L / 0.25))
    pts = []
    for i in range(n + 1):
        t = i / n
        q = p0 + (p1 - p0) * t
        q[1] -= sag * 4 * t * (1 - t)
        pts.append(q)
    for a, b in zip(pts[:-1], pts[1:]):
        m.add(beam(tuple(a), tuple(b), 0.02, cx.c("plaster_hi"), "paint"))
    d = (p1 - p0) / L
    cols = ["white", "plaster_hi", "cloth", "flower_rose", "flower_blue", "flower_gold", "white"]
    t = 0.12
    while t < L - 0.5:
        w = r.uniform(0.32, 0.62)
        h = r.uniform(0.38, 0.75) if w > 0.45 else r.uniform(0.3, 0.45)
        tt = (t + w / 2) / L
        mid = p0 + (p1 - p0) * tt
        mid[1] -= sag * 4 * tt * (1 - tt)
        c = mix(cx.c(r.choice(cols)), "#ffffff", 0.3)   # sun-bleached washing reads light at dusk too
        A, B = mid - d * w / 2, mid + d * w / 2
        C, D_ = B + np.array([0, -h, 0]), A + np.array([0, -h * r.uniform(0.92, 1.0), 0])
        # one face per cloth, wound toward +z (the camera side); 'paint' is double-sided so the back still draws
        # with a flipped normal. Two stacked faces z-fight in the shadow map and read as dark navy.
        fz = 1 if d[0] >= 0 else -1
        for (u, v, w3) in ((A, C, B), (A, D_, C)):
            m.tri(tuple(u), tuple(v if fz > 0 else w3), tuple(w3 if fz > 0 else v), c, mat="paint")
        if w < 0.45 and r.random() < 0.6:          # shirt sleeves
            for s_, base in ((-1, A), (1, B)):
                e = base + d * s_ * 0.14 + np.array([0, -0.18, 0])
                m.tri(tuple(base), tuple(base + np.array([0, -0.1, 0])), tuple(e), c, mat="paint")
        # pegs
        for q in (A, B):
            m.add(box(0.03, 0.07, 0.03, cx.c("timber_hi"), "paint", y0=q[1] - 0.04).xf((q[0], 0, q[2])))
        t += w + r.uniform(0.08, 0.2)
    pc.mesh = m
    pc.size = [L, 1.0, 0.1]
    return pc


def ring(r_in, r_out, y, seg, col, mat="stone", h=0.0):
    """Flat annulus (top face) at height y, optional outer/inner lip of height h below it."""
    m = Mesh()
    for i in range(seg):
        a0, a1 = math.tau * i / seg, math.tau * (i + 1) / seg
        i0 = (r_in * math.cos(a0), y, r_in * math.sin(a0)); i1 = (r_in * math.cos(a1), y, r_in * math.sin(a1))
        o0 = (r_out * math.cos(a0), y, r_out * math.sin(a0)); o1 = (r_out * math.cos(a1), y, r_out * math.sin(a1))
        m.quad(i0, i1, o1, o0, col, ((i0[0], i0[2]), (i1[0], i1[2]), (o1[0], o1[2]), (o0[0], o0[2])), mat)
    return m


def fountain(cx: Ctx) -> Piece:
    """Small round stone fountain: open basin with a visible water disc, rim ring, column, top bowl.
    Markers: 'spray' (jet top for the fountain_spray particles) and 'water' (basin water height)."""
    pc = Piece("fountain")
    m = Mesh()
    R, Ri, H = 1.12, 0.92, 0.5
    hi = mix(cx.c("stone_hi"), "#ffffff", 0.25)
    m.add(cylinder(R + 0.04, R, H, 16, W_, "stone", caps=False, y0=0))
    m.add(cylinder(Ri, Ri, H, 16, mix(cx.c("stone_lo"), "#ffffff", 0.15), "stone", caps=False, y0=0.02))
    m.add(ring(Ri - 0.02, R + 0.1, H + 0.08, 16, hi, "stone"))
    m.add(cylinder(R + 0.1, R + 0.1, 0.08, 16, hi, "stone", caps=False, y0=H))
    water = mix(cx.c("sky"), "#ffffff", 0.12)
    m.add(cylinder(Ri - 0.01, Ri - 0.01, 0.01, 16, water, "paint", y0=0.37))
    m.add(cylinder(0.16, 0.21, 1.0, 8, W_, "stone", y0=0.37))
    m.add(cylinder(0.46, 0.26, 0.2, 10, hi, "stone", caps=False, y0=1.3))
    m.add(ring(0.36, 0.46, 1.5, 10, hi, "stone"))
    m.add(cylinder(0.37, 0.37, 0.01, 10, water, "paint", y0=1.44))
    m.add(cylinder(0.07, 0.09, 0.2, 6, hi, "stone", y0=1.44))
    for k in range(6):
        a = k * math.tau / 6 + 0.3
        m.add(sphere(0.09, 5, 3, cx.c("moss")).xf((math.cos(a) * (R + 0.04), H + 0.12, math.sin(a) * (R + 0.04))))
    pc.mesh = m.ao(0, 0.8, 0.25)
    pc.markers["spray"] = [[0, 1.66, 0]]
    pc.markers["water"] = 0.39
    pc.blockers.append([-1.2, -1.2, 1.2, 1.2])
    pc.size = [2.4, 1.66, 2.4]
    return pc


def hedge(cx: Ctx, length=4.0, h=0.9, name=None) -> Piece:
    pc = Piece(name or f"hedge_{length:g}")
    r = rng(cx.seed, "hedge", length)
    m = Mesh()
    n = max(2, int(length / 0.55))
    for i in range(n):
        x = -length / 2 + (i + 0.5) * length / n
        rad = r.uniform(0.42, 0.58)
        m.add(sphere(rad, 7, 4, cx.c("grass" if i % 3 else "grass_hi"), squash=(1.1, h / rad * 0.62, 0.9), noise=0.14, rnd=r,
                     col_bottom=cx.c("leaf_deep")).xf((x, h * 0.5, r.uniform(-0.08, 0.08))))
        if r.random() < 0.3:
            m.add(sphere(0.07, 5, 3, cx.c(r.choice(["flower_rose", "white", "flower_gold"]))).xf((x + r.uniform(-.2, .2), h * 0.9, 0.35)))
    pc.mesh = m
    pc.blockers.append([-length / 2, -0.45, length / 2, 0.45])
    pc.size = [length, h, 0.9]
    return pc


def well(cx: Ctx) -> Piece:
    """Stone well with a little shingled roof, crank and bucket."""
    pc = Piece("well")
    m = Mesh()
    m.add(cylinder(0.8, 0.8, 0.8, 12, W_, "stone", caps=False, y0=0))
    m.add(cylinder(0.62, 0.62, 0.8, 12, mix(cx.c("stone_lo"), "#ffffff", 0.2), "stone", caps=False, y0=0.02))
    m.add(cylinder(0.9, 0.9, 0.12, 12, mix(cx.c("stone_hi"), "#ffffff", 0.2), "stone", y0=0.8))
    m.add(cylinder(0.6, 0.6, 0.02, 12, cx.c("cloth"), "paint", y0=0.4))
    tc = mix(cx.c("timber"), "#ffffff", 0.35)
    for sx in (-1, 1):
        m.add(box(0.14, 2.0, 0.14, tc, "timber", y0=0.8).xf((sx * 0.72, 0, 0)))
    m.add(cylinder(0.07, 0.07, 1.5, 6, tc, "timber", caps=True, y0=-0.75).xf((0, 2.0, 0), rot=(0, 0, PI / 2)))
    r2, ridge, rise = roof_gable(cx, 1.9, 1.2, 2.55, 38, ov=0.25, T=0.16)
    m.add(r2)
    m.add(gable_walls(cx, 1.9, 1.2, 2.55, rise, "timber", frame=False))
    m.add(cylinder(0.14, 0.17, 0.24, 7, mix(cx.c("timber_hi"), "#ffffff", 0.3), "timber", y0=1.25))
    m.add(box(0.02, 0.55, 0.02, cx.c("timber_lo"), "paint", y0=1.47))
    pc.mesh = m.ao(0, 0.9, 0.25)
    pc.blockers.append([-0.95, -0.95, 0.95, 0.95])
    pc.size = [1.9, ridge + 0.2, 1.9]
    return pc


PROPS = {"barrel": barrel, "crate": crate, "sign": sign, "flower_crate": flower_crate, "lamp_post": lamp_post,
         "fence": fence, "bench": bench, "hedge": hedge, "well": well, "market_stall": market_stall, "hills": hills,
         "fountain": fountain}
SIGN_ICONS = ("loaf", "mug", "flower", "key")
import kit_glade as _glade  # noqa: E402  (Mossglen pieces: portal_arch, shrine, standing_stone, ...)
PROPS.update(_glade.pieces(__import__('types').SimpleNamespace(**globals())))
import kit_hollows as _hollows  # noqa: E402  (Toadstool Hollows pieces: toadstools, gnome stump, spring, brazier)
PROPS.update(_hollows.pieces(__import__('types').SimpleNamespace(**globals())))
import kit_rift as _rift  # noqa: E402  (Rift Shrine + Vanaheim pieces: rift_isle, rift_arch, rift_shard, rift_dais, vine_arch)
PROPS.update(_rift.pieces(__import__('types').SimpleNamespace(**globals())))


def export_piece(cx: Ctx, pc: Piece, out: Path):
    path = out / f"{pc.name}.glb"
    export_glb(pc.mesh, path, cx.textures(), cx.tile_m, pc.name,
               emissive={"window": (0, 0, 0), "lamp": (0.2, 0.12, 0.03)}, double={"paint"})
    return {"file": path.name, "kind": pc.kind, "tris": pc.mesh.tris, "size": [round(v, 3) for v in getattr(pc, "size", [0, 0, 0])],
            "markers": pc.markers, "blockers": pc.blockers, **({"stairs": pc.stairs} if hasattr(pc, "stairs") else {})}


def build(biome="cozy-village", out="public/art/kit", texel=None, project=None, seed=1, extra=None):
    """Standard kit. `extra` = list of (kind, kwargs) for scene-specific pieces (assemble uses this)."""
    pal = Pal(load_biome(biome, project))
    out = ensure(out)
    texel = Path(texel) if texel else (Path(project) / "public/art/texel" if project else out.parent / "texel")
    if not (texel / "cobble_64.png").exists():
        load_tool("texel").build(biome, (32, 64), None, texel, project, seed)
    cx = Ctx(pal, texel, seed)
    meta = {"tool": "hd2d kit", "biome": biome, "seed": seed, "sprite_height_m": 1.8, "pieces": {}}
    pieces = [cottage(cx, n, s) for n, s in COTTAGES.items()]
    pieces += [terrace(cx, 6, 4, 1.2, name="terrace_6x4"), terrace(cx, 4, 4, 0.6, name="terrace_4x4_low"),
               stairs(cx, 2.4, 1.2, name="stairs_2.4x1.2"), retaining_wall(cx, 4, 1.0, name="retaining_wall_4")]
    pieces += [f(cx) for f in PROPS.values()]
    pieces += [hanging_sign(cx, ic) for ic in SIGN_ICONS]
    pieces.append(bunting(cx, (-3, 2.6, 0), (3, 2.6, 0), 0.5))
    for kind, kw in (extra or []):
        pieces.append({"terrace": terrace, "stairs": stairs, "ground": ground_slab, "wall": retaining_wall,
                       "bunting": bunting, "hedge": hedge, "fence": fence, "laundry": laundry}[kind](cx, **kw))
    for pc in pieces:
        meta["pieces"][pc.name] = export_piece(cx, pc, out)
    write_json(out / "kit.json", meta)
    return meta


def main(argv=None):
    ap = argparse.ArgumentParser(prog="hd2d kit", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--biome", default="cozy-village")
    ap.add_argument("--out", default="public/art/kit")
    ap.add_argument("--texel", default=None, help="texel output dir (built if missing)")
    ap.add_argument("--project", default=None)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args(argv)
    meta = build(a.biome, a.out, a.texel, a.project, a.seed)
    for k, v in meta["pieces"].items():
        print(f"  {k:18s} {v['tris']:5d} tris  size {v['size']}")
    print(f"kit: {len(meta['pieces'])} pieces -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
