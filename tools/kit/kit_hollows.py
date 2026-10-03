"""Toadstool Hollows pieces for hd2d kit (original, Hearthmoor Part 5): big red white-spotted toadstools, toadstool
clusters, a bounce toadstool (springy low cap), gnome-door stumps, the bubbly spring basin and a cold-fire brazier.
Imported by kit.py; biome palette + the shared mesh helpers only (painted / texel look, no PBR)."""
from __future__ import annotations

import math

PI = math.pi


def pieces(K):
    box, cylinder, sphere, mix, Piece, W_, Mesh = K.box, K.cylinder, K.sphere, K.mix, K.Piece, K.W_, K.Mesh

    def cap(m, cx, r, x, y, z, R, h, spots=7, col="roof_hi"):
        """a red dome cap with a darker underside rim and white spots"""
        m.add(sphere(R, 9, 5, cx.c(col), squash=(1, h / R, 1), col_bottom=cx.c("roof")).xf((x, y, z)))
        m.add(cylinder(R * 0.92, R * 0.55, 0.06, 9, cx.c("plaster_lo"), "paint", y0=y - 0.04).xf((x, 0, z)))   # gills
        for k in range(spots):
            a = k * 2 * PI / spots + r.uniform(-0.3, 0.3)
            rr = R * r.uniform(0.3, 0.75)
            sx, sz = math.cos(a) * rr, math.sin(a) * rr
            sy = y + h * math.sqrt(max(0.0, 1 - (rr / R) ** 2)) * 0.96
            m.add(sphere(R * r.uniform(0.09, 0.15), 5, 3, cx.c("white"), squash=(1, 0.45, 1)).xf((x + sx, sy, z + sz)))
        m.add(sphere(R * 0.14, 5, 3, cx.c("white"), squash=(1, 0.5, 1)).xf((x, y + h * 0.98, z)))

    def stem(m, cx, x, z, r0, r1, h, y0=0.0):
        m.add(cylinder(r0, r1, h, 8, cx.c("plaster_hi"), "paint", y0=y0, col_top=cx.c("plaster")).xf((x, 0, z)))

    def toadstool_big(cx):
        """a tall red toadstool (~2.4 m): thick cream stem with a skirt ring, wide red cap with white spots"""
        pc = Piece("toadstool_big"); r = K.rng(cx.seed, "tbig"); m = Mesh()
        stem(m, cx, 0, 0, 0.32, 0.24, 1.9)
        m.add(cylinder(0.42, 0.3, 0.12, 8, cx.c("plaster"), "paint", y0=1.25))                   # skirt
        m.add(sphere(0.45, 7, 3, cx.c("moss"), squash=(1, 0.25, 1)).xf((0, 0.02, 0)))           # moss at the foot
        cap(m, cx, r, 0, 1.9, 0, 1.15, 0.62, spots=9)
        pc.mesh = m.ao(0, 2.6, 0.22)
        pc.blockers.append([-0.36, -0.36, 0.36, 0.36])
        pc.size = [2.3, 2.6, 2.3]
        return pc

    def toadstool_cluster(cx):
        """four smaller red toadstools of different heights growing together"""
        pc = Piece("toadstool_cluster"); r = K.rng(cx.seed, "tclus"); m = Mesh()
        for (x, z, h, R) in ((0, 0, 1.05, 0.55), (0.55, 0.25, 0.65, 0.36), (-0.5, 0.3, 0.5, 0.3), (0.2, -0.45, 0.8, 0.42)):
            stem(m, cx, x, z, R * 0.32, R * 0.24, h)
            cap(m, cx, r, x, h, z, R, R * 0.55, spots=5)
        pc.mesh = m.ao(0, 1.4, 0.22)
        pc.blockers.append([-0.3, -0.3, 0.3, 0.3])
        pc.size = [1.6, 1.4, 1.4]
        return pc

    def bounce_toadstool(cx):
        """the springy one: a short fat stem and a broad, low, extra-bright cap you can jump on"""
        pc = Piece("bounce_toadstool"); r = K.rng(cx.seed, "tbounce"); m = Mesh()
        stem(m, cx, 0, 0, 0.42, 0.36, 0.45)
        cap(m, cx, r, 0, 0.45, 0, 0.95, 0.32, spots=8, col="flower_rose")
        pc.mesh = m.ao(0, 0.9, 0.2)
        pc.size = [1.9, 0.8, 1.9]
        return pc

    def gnome_stump(cx):
        """an old stump with a little round gnome door (timber, iron studs), a tiny window and a moss roof"""
        pc = Piece("gnome_stump"); r = K.rng(cx.seed, "gstump"); m = Mesh()
        m.add(cylinder(0.75, 0.62, 1.3, 9, cx.c("timber"), "paint", y0=0, col_top=cx.c("timber_hi")))
        m.add(cylinder(0.6, 0.6, 0.04, 9, cx.c("plaster_lo"), "paint", y0=1.3))                  # cut rings
        m.add(sphere(0.7, 8, 3, cx.c("moss"), squash=(1, 0.22, 1)).xf((0, 1.32, 0)))
        for k in range(5):                                                                        # roots
            a = k * 2 * PI / 5 + 0.3
            m.add(box(0.2, 0.18, 0.5, cx.c("timber_lo"), "paint", y0=0).xf((math.cos(a) * 0.72, 0, math.sin(a) * 0.72), rot=(0, -a, 0)))
        m.add(cylinder(0.27, 0.27, 0.06, 10, cx.c("timber_lo"), "paint", y0=0).xf((0, 0.0, 0.66), rot=(PI / 2, 0, 0)))
        m.add(box(0.44, 0.56, 0.06, cx.c("roof"), "paint", y0=0.02).xf((0, 0, 0.7)))             # the door
        m.add(sphere(0.22, 8, 3, cx.c("roof"), squash=(1, 1, 0.25)).xf((0, 0.58, 0.7)))          # round top
        m.add(sphere(0.035, 4, 2, cx.c("flower_gold")).xf((0.13, 0.32, 0.74)))                  # knob
        m.add(box(0.18, 0.16, 0.04, cx.c("lamp"), "lamp", y0=0.82).xf((0.32, 0, 0.62)))         # tiny lit window
        m.add(sphere(0.08, 5, 3, cx.c("roof_hi")).xf((-0.42, 1.5, 0.3)))
        pc.mesh = m.ao(0, 1.5, 0.25)
        pc.markers["doors"].append([0, 0.3, 0.76])
        pc.blockers.append([-0.72, -0.72, 0.72, 0.72])
        pc.size = [1.6, 1.6, 1.6]
        return pc

    def spring_basin(cx):
        """the hidden spring: a ring of mossy stones round a pool of glowing blue water"""
        pc = Piece("spring_basin"); r = K.rng(cx.seed, "spring"); m = Mesh()
        m.add(cylinder(1.25, 1.25, 0.05, 14, cx.c("sky"), "lamp", y0=0.06))                     # the water (lit)
        m.add(cylinder(0.7, 0.7, 0.02, 12, cx.c("white"), "lamp", y0=0.11))
        for k in range(12):
            a = k * 2 * PI / 12 + r.uniform(-0.1, 0.1)
            m.add(box(0.42, r.uniform(0.22, 0.34), 0.34, mix(W_, cx.c("stone"), 0.2), "stone", y0=0).xf(
                (math.cos(a) * 1.42, 0, math.sin(a) * 1.42), rot=(0, -a, 0)))
            if k % 3 == 0:
                m.add(sphere(0.16, 5, 3, cx.c("moss")).xf((math.cos(a) * 1.42, 0.32, math.sin(a) * 1.42)))
        pc.mesh = m.ao(0, 0.5, 0.2)
        pc.size = [3.2, 0.4, 3.2]
        return pc

    def brazier(cx):
        """a dark-hour brazier: three stone legs, an iron bowl and (when lit) a cold-fire heart; the flame itself is a
        game effect + light, the piece carries only the glowing coals"""
        pc = Piece("brazier"); r = K.rng(cx.seed, "brazier"); m = Mesh()
        st = mix(W_, cx.c("stone_lo"), 0.2)
        for k in range(3):
            a = k * 2 * PI / 3
            m.add(box(0.1, 0.7, 0.1, st, "stone", y0=0).xf((math.cos(a) * 0.22, 0, math.sin(a) * 0.22), rot=(0, -a, 0.12)))
        m.add(cylinder(0.36, 0.22, 0.24, 8, cx.c("shadow"), "paint", y0=0.66))
        m.add(cylinder(0.3, 0.3, 0.04, 8, cx.c("flower_blue"), "lamp", y0=0.88))                # cold coals
        m.add(box(0.5, 0.06, 0.5, st, "stone", y0=0))
        pc.mesh = m.ao(0, 1.0, 0.2)
        pc.blockers.append([-0.3, -0.3, 0.3, 0.3])
        pc.size = [0.8, 1.0, 0.8]
        return pc

    return {"toadstool_big": toadstool_big, "toadstool_cluster": toadstool_cluster, "bounce_toadstool": bounce_toadstool,
            "gnome_stump": gnome_stump, "spring_basin": spring_basin, "brazier": brazier}
