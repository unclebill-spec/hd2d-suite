"""Alchemy pieces for hd2d kit (original; Hearthmoor Art seat staging, 2026-10-05): a bubbling glowing cauldron in three
brews, an alchemist's table, a potion shelf and a herb drying rack.

cauldron_blue / cauldron_violet / cauldron_green   black-iron pot (0.9 m) on three legs over a small log fire, a glowing
                     brew surface with bubbles (glow); animate with the cauldron_brew_<c> + cauldron_fire billboards
alchemy_table       oak table: glowing flasks, an alembic, a mortar and pestle, an open recipe book
potion_shelf        wall shelf with two rows of glowing bottles (red / blue / gold / violet / green)
herb_rack           a drying rack of hanging herb bundles and moonpetals

Drop-in: copy to tools/kit/ and add to kit.py like kit_harbor:
    import kit_alchemy as _al; PROPS.update(_al.pieces(__import__('types').SimpleNamespace(**globals())))
Neon hexes only on the 'glow' material (brews, potions, fire)."""
from __future__ import annotations

import math

PI = math.pi
BREW = {   # colour: (surface, hi, lo, light)
    "blue": ("#2ab4ff", "#a6ecff", "#1c62d8", "#2ab4ff"),
    "violet": ("#a45cf0", "#d4a8ff", "#6a34b8", "#a45cf0"),
    "green": ("#3cf08a", "#b8ffd4", "#14a85a", "#3cf08a"),
}
POTION = ["#ff5a4a", "#2ab4ff", "#ffc463", "#a45cf0", "#3cf08a", "#ff4fc8"]
RED, RED_HI, GOLD = "#e0302a", "#ff5a4a", "#ffc463"


def pieces(K):
    box, cylinder, sphere, beam, mix, Piece, W_, Mesh = K.box, K.cylinder, K.sphere, K.beam, K.mix, K.Piece, K.W_, K.Mesh

    def iron(cx, t=0.0):
        return mix(mix(cx.c("ink"), cx.c("stone_lo"), 0.4 + t), cx.c("cloth"), 0.12)

    def cauldron(colour):
        def fn(cx):
            pc = Piece(f"cauldron_{colour}"); r = K.rng(cx.seed, f"caul{colour}"); m = Mesh()
            s, hi, lo, lc = BREW[colour]
            for k in range(3):                                                   # legs
                a = k * 2 * PI / 3 + 0.3
                m.add(beam([math.cos(a) * 0.3, 0.42, math.sin(a) * 0.3], [math.cos(a) * 0.42, 0.0, math.sin(a) * 0.42], 0.06, iron(cx), "paint"))
            for k in range(3):                                                   # log fire under the pot
                a = k * PI / 3
                m.add(beam([math.cos(a) * -0.3, 0.06, math.sin(a) * -0.3], [math.cos(a) * 0.3, 0.06, math.sin(a) * 0.3], 0.08, cx.c("timber_lo"), "timber"))
            for k in range(5):
                m.add(sphere(0.06, 4, 3, (RED_HI, GOLD, RED, RED_HI, GOLD)[k], "glow").xf((-0.16 + k * 0.08, 0.12, 0.05 * (k % 2))))
            m.add(sphere(0.46, 12, 8, iron(cx), "paint", squash=(1, 0.8, 1), col_bottom=mix(iron(cx), cx.c("ink"), 0.4)).xf((0, 0.62, 0)))   # pot belly
            m.add(cylinder(0.4, 0.44, 0.12, 14, iron(cx, 0.1), "paint", y0=0.88))
            m.add(cylinder(0.47, 0.47, 0.05, 14, mix(iron(cx), cx.c("stone"), 0.3), "paint", y0=0.98))       # rim
            m.add(cylinder(0.4, 0.4, 0.03, 14, lo, "glow", y0=0.98))                                          # the brew
            m.add(cylinder(0.3, 0.3, 0.01, 12, s, "glow", y0=1.01))
            m.add(cylinder(0.12, 0.12, 0.01, 8, hi, "glow", y0=1.02))
            for k in range(6):
                a = k * 2 * PI / 6 + r.uniform(0, 0.5)
                rr = r.uniform(0.08, 0.32)
                m.add(sphere(r.uniform(0.03, 0.06), 5, 3, hi if k % 2 else W_, "glow").xf((math.cos(a) * rr, 1.04, math.sin(a) * rr)))
            for sx in (-1, 1):                                                   # handle lugs
                m.add(box(0.06, 0.08, 0.1, iron(cx), "paint", y0=0.9).xf((sx * 0.48, 0, 0)))
            m.add(beam([0.15, 1.0, 0.1], [0.35, 1.45, 0.25], 0.035, cx.c("timber_hi"), "timber"))            # stirring paddle
            pc.markers["lamps"].append([0, 1.25, 0.1]); pc.markers["lamp_color"] = lc; pc.markers["lamp_fixed"] = 0.55; pc.markers["lamp_range"] = 4.5
            pc.mesh = m.ao(0, 1.1, 0.15)
            pc.blockers.append([-0.48, -0.48, 0.48, 0.48])
            pc.size = [1.0, 1.1, 1.0]
            return pc
        return fn

    def bottle(m, x, y, z, col, h=0.2, r=0.06, flat=False):
        glass = mix(W_, "#9ad0e0", 0.5)
        if flat:
            m.add(box(r * 2, h * 0.7, r * 1.2, col, "glow", y0=y).xf((x, 0, z)))
        else:
            m.add(sphere(r, 6, 4, col, "glow").xf((x, y + r, z)))
        m.add(cylinder(r * 0.35, r * 0.35, h * 0.45, 6, glass, "paint", y0=y + (h * 0.7 if flat else r * 1.8)).xf((x, 0, z)))
        m.add(cylinder(r * 0.4, r * 0.4, h * 0.12, 6, "#a87850", "paint", y0=y + (h * 0.7 if flat else r * 1.8) + h * 0.42).xf((x, 0, z)))   # cork

    def alchemy_table(cx):
        pc = Piece("alchemy_table"); m = Mesh()
        m.add(box(1.5, 0.08, 0.75, cx.c("timber_hi"), "timber", y0=0.78))
        for sx in (-1, 1):
            for sz in (-1, 1):
                m.add(box(0.08, 0.78, 0.08, cx.c("timber"), "timber", y0=0).xf((sx * 0.66, 0, sz * 0.3)))
        m.add(box(1.36, 0.05, 0.6, cx.c("timber_lo"), "timber", y0=0.22))
        for k, col in enumerate(POTION[:4]):
            bottle(m, -0.6 + k * 0.14, 0.86, -0.15 + (k % 2) * 0.1, col, 0.22, 0.06 + 0.01 * (k % 2))
        # alembic: a round flask on a ring stand with a tube to a receiver
        m.add(cylinder(0.08, 0.1, 0.02, 8, iron(cx), "paint", y0=0.86).xf((0.15, 0, -0.1)))
        m.add(sphere(0.11, 8, 5, BREW["green"][0], "glow").xf((0.15, 1.0, -0.1)))
        m.add(beam([0.15, 1.1, -0.1], [0.45, 1.05, -0.1], 0.02, mix(W_, "#9ad0e0", 0.5), "paint"))
        m.add(sphere(0.07, 6, 4, BREW["green"][1], "glow").xf((0.48, 0.93, -0.1)))
        m.add(cylinder(0.05, 0.04, 0.08, 6, RED_HI, "glow", y0=0.86).xf((0.15, 0, -0.1)))       # spirit burner flame
        # mortar + pestle
        m.add(cylinder(0.08, 0.06, 0.08, 8, cx.c("stone"), "stone", y0=0.86).xf((0.45, 0, 0.18)))
        m.add(beam([0.45, 0.93, 0.18], [0.52, 1.05, 0.22], 0.025, cx.c("stone_hi"), "stone"))
        # open recipe book
        for sx in (-1, 1):
            m.add(box(0.14, 0.02, 0.2, cx.c("plaster_hi"), "paint", y0=0.86).xf((-0.12 + sx * 0.075, 0, 0.18), rot=(0, 0, sx * 0.08)))
        m.add(box(0.3, 0.015, 0.22, cx.c("roof_lo"), "paint", y0=0.855).xf((-0.12, 0, 0.18)))
        pc.markers["lamps"].append([0.1, 1.1, 0.2]); pc.markers["lamp_color"] = BREW["green"][0]; pc.markers["lamp_fixed"] = 0.3; pc.markers["lamp_range"] = 3.0
        pc.mesh = m.ao(0, 1.2, 0.12)
        pc.blockers.append([-0.75, -0.38, 0.75, 0.38])
        pc.size = [1.5, 1.15, 0.75]
        return pc

    def potion_shelf(cx):
        pc = Piece("potion_shelf"); m = Mesh()
        m.add(box(1.3, 1.5, 0.06, cx.c("timber_lo"), "timber", y0=0.4).xf((0, 0, -0.14)))
        for y in (0.45, 1.0, 1.55):
            m.add(box(1.3, 0.05, 0.3, cx.c("timber_hi"), "timber", y0=y))
        for sx in (-0.65, 0.65):
            m.add(box(0.05, 1.5, 0.3, cx.c("timber"), "timber", y0=0.4).xf((sx, 0, 0)))
        for row, y in enumerate((0.5, 1.05)):
            for k in range(6):
                col = POTION[(k + row * 3) % len(POTION)]
                bottle(m, -0.52 + k * 0.2, y, 0.02, col, 0.24 if k % 2 else 0.2, 0.065 if k % 3 else 0.05, flat=(k + row) % 3 == 0)
        m.add(box(0.36, 0.14, 0.2, cx.c("roof_lo"), "paint", y0=1.6).xf((-0.3, 0, 0)))      # books on top
        m.add(box(0.12, 0.2, 0.2, cx.c("cloth"), "paint", y0=1.6).xf((0.0, 0, 0)))
        pc.markers["lamps"].append([0, 1.0, 0.3]); pc.markers["lamp_color"] = "#a45cf0"; pc.markers["lamp_fixed"] = 0.25; pc.markers["lamp_range"] = 2.5
        pc.mesh = m.ao(0, 1.9, 0.12)
        pc.blockers.append([-0.67, -0.18, 0.67, 0.18])
        pc.size = [1.35, 1.9, 0.32]
        return pc

    def herb_rack(cx):
        pc = Piece("herb_rack"); r = K.rng(cx.seed, "herbs"); m = Mesh()
        for x in (-0.7, 0.7):
            m.add(box(0.07, 1.9, 0.07, cx.c("timber"), "timber", y0=0).xf((x, 0, 0)))
        m.add(box(1.5, 0.06, 0.06, cx.c("timber_hi"), "timber", y0=1.82))
        for k in range(7):
            x = -0.6 + k * 0.2
            m.add(beam([x, 1.82, 0], [x, 1.62, 0], 0.012, cx.c("plaster_lo"), "paint"))
            col = (cx.c("grass"), cx.c("moss"), cx.c("leaf_deep"), cx.c("grass_hi"))[k % 4]
            m.add(cylinder(0.04, 0.1, 0.32, 6, col, "paint", y0=1.3).xf((x, 0, 0)))
            if k % 3 == 1:                                                       # moonpetals in the bundle
                for j in range(3):
                    m.add(sphere(0.035, 4, 3, cx.c("flower_blue"), "paint").xf((x + (j - 1) * 0.04, 1.3, 0.05)))
            m.add(box(0.06, 0.03, 0.06, cx.c("roof"), "paint", y0=1.6).xf((x, 0, 0)))  # string tie
        pc.mesh = m.ao(0, 1.9, 0.1)
        pc.blockers.append([-0.72, -0.08, 0.72, 0.08])
        pc.size = [1.5, 1.9, 0.2]
        return pc

    out = {f"cauldron_{c}": cauldron(c) for c in BREW}
    out.update({"alchemy_table": alchemy_table, "potion_shelf": potion_shelf, "herb_rack": herb_rack})
    return out
