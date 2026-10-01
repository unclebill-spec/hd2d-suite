"""Mossglen glade pieces for hd2d kit (original): portal_arch, shrine, standing_stone, stone_lantern,
mushroom_ring, fern_bush. Imported by kit.py; every piece uses the biome palette and the same mesh helpers."""
from __future__ import annotations

import math

PI = math.pi


def pieces(K):
    """K = the kit module (Ctx, Piece, box, cylinder, sphere, mix, rng, W_)."""
    box, cylinder, sphere, mix, Piece, W_ = K.box, K.cylinder, K.sphere, K.mix, K.Piece, K.W_
    Mesh = K.Mesh

    def mossy_block(cx, w, h, d, y0, r, moss=True):
        m = Mesh()
        tint = mix(W_, cx.c("moss"), r.uniform(0.0, 0.18))
        m.add(box(w, h, d, tint, "stone", y0=y0))
        if moss and r.random() < 0.7:
            m.add(box(w * r.uniform(0.5, 1.02), 0.05, d * r.uniform(0.6, 1.02), cx.c("moss"), "paint", y0=y0 + h).xf(
                (r.uniform(-0.05, 0.05), 0, r.uniform(-0.05, 0.05))))
        return m

    def portal_arch(cx):
        """Stone-arch gate: two stacked mossy pillars, a ring of voussoirs with a keystone, a plinth step and two
        little lanterns. The opening (x -0.82..0.82, up to ~3.1 m) is left open for the vortex billboard."""
        pc = Piece("portal_arch")
        m = Mesh()
        r = K.rng(cx.seed, "portal_arch")
        m.add(box(3.3, 0.16, 1.3, mix(W_, cx.c("stone_lo"), 0.25), "stone", y0=0))
        m.add(box(2.0, 0.08, 1.1, cx.c("moss"), "paint", y0=0.16).xf((0, 0, 0.05)))
        for sx in (-1, 1):
            y = 0.16
            for i in range(5):
                h = r.uniform(0.38, 0.5)
                m.add(mossy_block(cx, 0.62 + r.uniform(-0.04, 0.04), h, 0.66, y, r, moss=i == 4).xf((sx * 1.12 + r.uniform(-0.02, 0.02), 0, 0)))
                y += h + 0.02
        cy, R0, R1 = 2.45, 0.82, 1.43
        n = 9
        for i in range(n):
            a0, a1 = PI * i / n, PI * (i + 1) / n
            am = (a0 + a1) / 2
            w = (R1 - R0)
            ln = (R0 + R1) / 2 * (a1 - a0) * 0.96
            bx = math.cos(am) * (R0 + R1) / 2
            by = cy + math.sin(am) * (R0 + R1) / 2
            key = i == n // 2
            col = mix(W_, cx.c("stone_hi"), 0.35) if key else mix(W_, cx.c("moss"), r.uniform(0, 0.15))
            blk = box(ln, w * (1.18 if key else 1.0), 0.6 if not key else 0.72, col, "stone")
            m.add(blk.xf((bx, by, 0), rot=(0, 0, am - PI / 2)))
        # moss drips and two lanterns
        for k in range(6):
            a = r.uniform(0.2, PI - 0.2)
            m.add(sphere(0.09, 5, 3, cx.c("moss")).xf((math.cos(a) * R1, cy + math.sin(a) * R1 + 0.02, r.uniform(-0.25, 0.25))))
        for sx in (-1, 1):
            m.add(box(0.2, 0.05, 0.2, cx.c("ink"), "paint", y0=2.4).xf((sx * 1.12, 0, 0.43)))
            m.add(box(0.16, 0.24, 0.16, cx.c("lamp"), "lamp", y0=2.45).xf((sx * 1.12, 0, 0.43)))
            m.add(box(0.2, 0.05, 0.2, cx.c("ink"), "paint", y0=2.69).xf((sx * 1.12, 0, 0.43)))
            pc.markers["lamps"].append([sx * 1.12, 2.57, 0.45])
        pc.mesh = m.ao(0, 4.0, 0.22)
        pc.markers["portal"] = [[0, 0.2, 0.0]]
        pc.blockers += [[-1.5, -0.4, -0.78, 0.4], [0.78, -0.4, 1.5, 0.4]]
        pc.size = [3.3, 4.0, 1.3]
        return pc

    def shrine(cx):
        """A small glade shrine: two stone steps, a timber hut with a thick shingle roof, an offering bowl, a
        candle lamp and moss."""
        pc = Piece("shrine")
        m = Mesh()
        m.add(box(2.6, 0.22, 2.0, mix(W_, cx.c("stone_lo"), 0.2), "stone", y0=0))
        m.add(box(2.0, 0.22, 1.5, W_, "stone", y0=0.22))
        tc = mix(cx.c("timber"), "#ffffff", 0.25)
        for sx in (-1, 1):
            for sz in (-1, 1):
                m.add(box(0.14, 1.25, 0.14, tc, "timber", y0=0.44).xf((sx * 0.62, 0, sz * 0.45)))
        m.add(box(1.38, 0.9, 0.06, mix(cx.c("plaster"), "#ffffff", 0.1), "plaster", y0=0.44).xf((0, 0, -0.45)))
        m.add(box(1.36, 0.12, 1.06, tc, "timber", y0=1.69))
        rr, ridge, rise = K.roof_gable(cx, 1.5, 1.2, 1.8, 40, ov=0.28, T=0.2)
        m.add(rr)
        m.add(K.gable_walls(cx, 1.5, 1.2, 1.8, rise, "timber", frame=False))
        m.add(cylinder(0.24, 0.16, 0.14, 10, mix(cx.c("stone_hi"), "#ffffff", 0.2), "stone", y0=0.44).xf((0, 0, 0.05)))
        m.add(sphere(0.07, 5, 3, cx.c("flower_rose")).xf((-0.06, 0.6, 0.05)))
        m.add(sphere(0.07, 5, 3, cx.c("flower_gold")).xf((0.07, 0.6, 0.02)))
        m.add(box(0.07, 0.18, 0.07, cx.c("plaster_hi"), "paint", y0=0.44).xf((0.42, 0, 0.12)))
        m.add(box(0.05, 0.06, 0.05, cx.c("lamp"), "lamp", y0=0.62).xf((0.42, 0, 0.12)))
        pc.markers["lamps"].append([0.42, 0.75, 0.2])
        for k in range(8):
            a = k * 2 * PI / 8 + 0.2
            m.add(sphere(0.12, 5, 3, cx.c("moss")).xf((math.cos(a) * 1.2, 0.22, math.sin(a) * 0.9)))
        pc.mesh = m.ao(0, 2.6, 0.25)
        pc.blockers.append([-1.3, -1.0, 1.3, 0.75])
        pc.size = [2.6, ridge + 0.3, 2.0]
        return pc

    def standing_stone(cx):
        pc = Piece("standing_stone")
        r = K.rng(cx.seed, "standing_stone")
        m = Mesh()
        m.add(box(0.7, 1.9, 0.45, mix(W_, cx.c("stone_lo"), 0.2), "stone", y0=0).xf(rot=(0.04, 0.2, 0.06)))
        m.add(box(0.5, 0.28, 0.4, mix(W_, cx.c("stone_hi"), 0.15), "stone", y0=1.86).xf(rot=(0.0, 0.2, -0.12)))
        m.add(box(0.74, 0.06, 0.5, cx.c("moss"), "paint", y0=0.0))
        for k in range(3):
            m.add(sphere(0.1, 5, 3, cx.c("moss")).xf((r.uniform(-0.3, 0.3), r.uniform(0.6, 1.9), 0.24)))
        pc.mesh = m.ao(0, 2.2, 0.25)
        pc.blockers.append([-0.4, -0.3, 0.4, 0.3])
        pc.size = [0.7, 2.2, 0.5]
        return pc

    def stone_lantern(cx):
        pc = Piece("stone_lantern")
        m = Mesh()
        st = mix(W_, cx.c("stone_hi"), 0.15)
        m.add(box(0.5, 0.18, 0.5, st, "stone", y0=0))
        m.add(cylinder(0.12, 0.12, 0.7, 6, st, "stone", y0=0.18))
        m.add(box(0.46, 0.08, 0.46, st, "stone", y0=0.88))
        m.add(box(0.3, 0.3, 0.3, cx.c("lamp"), "lamp", y0=0.96))
        for (x, z) in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
            m.add(box(0.07, 0.3, 0.07, st, "stone", y0=0.96).xf((x * 0.16, 0, z * 0.16)))
        m.add(cylinder(0.4, 0.04, 0.26, 4, st, "stone", y0=1.26).xf(rot=(0, PI / 4, 0)))
        m.add(sphere(0.07, 5, 3, cx.c("moss")).xf((0.12, 1.3, 0.1)))
        pc.mesh = m.ao(0, 1.6, 0.25)
        pc.markers["lamps"].append([0, 1.11, 0.2])
        pc.blockers.append([-0.28, -0.28, 0.28, 0.28])
        pc.size = [0.5, 1.6, 0.5]
        return pc

    def mushroom_ring(cx):
        pc = Piece("mushroom_ring")
        r = K.rng(cx.seed, "mushrooms")
        m = Mesh()
        for k in range(9):
            a = k * 2 * PI / 9 + r.uniform(-0.15, 0.15)
            R = 0.85 + r.uniform(-0.1, 0.1)
            x, z = math.cos(a) * R, math.sin(a) * R * 0.8
            h = r.uniform(0.14, 0.28)
            m.add(cylinder(0.035, 0.045, h, 5, cx.c("plaster_hi"), "paint", y0=0).xf((x, 0, z)))
            cap = cx.c("flower_rose") if k % 3 else cx.c("flower_gold")
            m.add(sphere(r.uniform(0.08, 0.12), 6, 3, cap, squash=(1, 0.55, 1)).xf((x, h, z)))
            m.add(sphere(0.02, 4, 2, cx.c("white")).xf((x + 0.03, h + 0.05, z + 0.03)))
        pc.mesh = m
        pc.size = [2.0, 0.4, 1.6]
        return pc

    def fern_bush(cx):
        pc = Piece("fern_bush")
        r = K.rng(cx.seed, "fern")
        m = Mesh()
        for k in range(6):
            a = k * 2 * PI / 6 + r.uniform(-0.3, 0.3)
            # lighter tops (grass / grass_hi) over a deep base: all leaf_deep read as a black blob in sunlight
            m.add(sphere(r.uniform(0.32, 0.46), 6, 4, cx.c("grass") if k % 2 else cx.c("moss"), squash=(1, 0.7, 1), noise=0.15, rnd=r,
                         col_bottom=cx.c("leaf_deep")).xf((math.cos(a) * 0.35, 0.3, math.sin(a) * 0.3)))
        for k in range(4):
            a = k * 2 * PI / 4 + 0.4
            m.add(sphere(0.2, 5, 3, cx.c("grass_hi"), squash=(1, 0.6, 1), noise=0.1, rnd=r).xf((math.cos(a) * 0.2, 0.55, math.sin(a) * 0.18)))
        for k in range(3):
            m.add(sphere(0.05, 4, 2, cx.c("flower_blue")).xf((r.uniform(-0.4, 0.4), 0.72, r.uniform(-0.2, 0.3))))
        pc.mesh = m.ao(0, 0.9, 0.3)
        pc.blockers.append([-0.55, -0.45, 0.55, 0.45])
        pc.size = [1.2, 0.9, 1.0]
        return pc

    return {"portal_arch": portal_arch, "shrine": shrine, "standing_stone": standing_stone, "stone_lantern": stone_lantern,
            "mushroom_ring": mushroom_ring, "fern_bush": fern_bush}
