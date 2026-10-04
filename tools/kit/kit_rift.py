"""Rift Shrine + Vanaheim pieces for hd2d kit (original): rift_isle (a floating stone island: paved circle on top,
a tapering rock root underneath with hanging roots), rift_arch (a gloom-stone gate, no moss, rune grooves and a
crystal keystone; the vortex / seal billboards are placed by the area's fx list), rift_shard (a small floating rock
for the void), rift_dais (the raised rune plinth in the middle of the circle) and vine_arch (Vanaheim's leafy
return gate). Imported by kit.py; biome palette only, same mesh helpers as kit_glade."""
from __future__ import annotations

import math

PI = math.pi


def pieces(K):
    box, cylinder, sphere, mix, Piece, W_ = K.box, K.cylinder, K.sphere, K.mix, K.Piece, K.W_
    Mesh = K.Mesh

    def gloom(cx, t=0.0):
        """gloom stone: the biome's low stone pulled toward shadow (the Rift's stone is older and colder)"""
        return mix(mix(W_, cx.c("stone_lo"), 0.55), cx.c("cloth"), 0.12 + t)

    def rift_isle(cx):
        """Floating island, top face at y=0 (radius 8.6 m): paved stone circle, ring kerb, moss tufts on the rim;
        underneath, five tapering rock bands down to a point ~7 m below, with roots and stones hanging off."""
        pc = Piece("rift_isle")
        m = Mesh()
        r = K.rng(cx.seed, "rift_isle")
        R = 8.6
        top = gloom(cx, -0.08)
        m.add(cylinder(R, R, 0.34, 30, mix(top, cx.c("shadow"), 0.2), "stone", y0=-0.34, cap_mat="cobble", col_top=mix(W_, cx.c("stone"), 0.3)))
        # kerb ring (low, under the walk step) and an inner paved ring of lighter slabs
        for i in range(30):
            a = 2 * PI * (i + 0.5) / 30
            m.add(box(1.72, 0.12, 0.5, mix(top, cx.c("stone_hi"), r.uniform(0.0, 0.2)), "stone", y0=0.0).xf(
                (math.cos(a) * (R - 0.3), 0, math.sin(a) * (R - 0.3)), rot=(0, -a + PI / 2, 0)))
        bands = [(R, R * 0.94, 1.0), (R * 0.94, R * 0.74, 1.3), (R * 0.74, R * 0.5, 1.5), (R * 0.5, R * 0.26, 1.7), (R * 0.26, 0.0, 1.9)]
        y = -0.34
        for k, (r0, r1, h) in enumerate(bands):
            col = mix(gloom(cx, 0.06 * k), cx.c("ink"), 0.12 * k)
            m.add(cylinder(r1, r0, h, 14 - k, col, "stone", caps=k == len(bands) - 1, y0=y - h).xf(rot=(0, 0.35 * k, 0)))
            y -= h
        # rocks jutting from the underside, roots and stones hanging off the rim
        for k in range(16):
            a = r.uniform(0, 2 * PI)
            rr = r.uniform(0.45, 0.9)
            yy = -0.6 - (1 - rr) * 6.0
            m.add(sphere(r.uniform(0.4, 0.8), 6, 4, mix(gloom(cx), cx.c("ink"), 0.2), "stone", noise=0.2, rnd=r).xf(
                (math.cos(a) * R * rr, yy, math.sin(a) * R * rr)))
        for k in range(22):
            a = 2 * PI * k / 22 + r.uniform(-0.08, 0.08)
            L = r.uniform(0.6, 2.4)
            m.add(box(0.07, L, 0.07, mix(cx.c("timber_lo"), cx.c("moss"), r.uniform(0, 0.5)), "paint", y0=-0.3 - L).xf(
                (math.cos(a) * (R - 0.1), 0, math.sin(a) * (R - 0.1))))
        for k in range(26):
            a = r.uniform(0, 2 * PI)
            m.add(sphere(r.uniform(0.12, 0.26), 5, 3, cx.c("moss" if k % 3 else "leaf_deep"), "paint", squash=(1, 0.55, 1)).xf(
                (math.cos(a) * (R - 0.15), 0.06, math.sin(a) * (R - 0.15))))
        pc.mesh = m.ao(-9.0, 9.0, 0.3)
        pc.size = [2 * R, 9.0, 2 * R]
        return pc

    def rift_arch(cx):
        """Gloom-stone gate (opening x -0.8..0.8, ~3.1 m): stacked dark pillars with carved rune grooves, a ring of
        voussoirs, a pale crystal keystone and a plinth. No lanterns: the light is the vortex / seal itself."""
        pc = Piece("rift_arch")
        m = Mesh()
        r = K.rng(cx.seed, "rift_arch")
        st = gloom(cx)
        m.add(box(3.2, 0.18, 1.3, mix(st, cx.c("stone_hi"), 0.15), "stone", y0=0))
        for sx in (-1, 1):
            y = 0.18
            for i in range(5):
                h = r.uniform(0.4, 0.5)
                m.add(box(0.6 + r.uniform(-0.04, 0.04), h, 0.64, mix(st, cx.c("ink"), r.uniform(0, 0.18)), "stone", y0=y).xf((sx * 1.1, 0, 0)))
                # rune groove on the front face (ink), every other block
                if i % 2 == 0:
                    m.add(box(0.08, h * 0.6, 0.02, cx.c("ink"), "paint", y0=y + h * 0.2).xf((sx * 1.1, 0, 0.33)))
                    m.add(box(0.26, 0.05, 0.02, cx.c("ink"), "paint", y0=y + h * 0.55).xf((sx * 1.1, 0, 0.33)))
                y += h + 0.02
        cy, R0, R1 = 2.45, 0.8, 1.4
        n = 9
        for i in range(n):
            a0, a1 = PI * i / n, PI * (i + 1) / n
            am = (a0 + a1) / 2
            ln = (R0 + R1) / 2 * (a1 - a0) * 0.95
            key = i == n // 2
            col = mix(st, cx.c("stone_hi"), 0.1) if not key else mix(W_, cx.c("sky"), 0.55)
            blk = box(ln, (R1 - R0) * (1.15 if key else 1.0), 0.72 if key else 0.6, col, "paint" if key else "stone")
            m.add(blk.xf((math.cos(am) * (R0 + R1) / 2, cy + math.sin(am) * (R0 + R1) / 2, 0), rot=(0, 0, am - PI / 2)))
        m.add(sphere(0.16, 6, 4, cx.c("white"), "paint").xf((0, cy + R1 + 0.12, 0.2)))
        pc.mesh = m.ao(0, 4.0, 0.24)
        pc.markers["rift"] = [[0, 0.2, 0.0]]
        pc.blockers += [[-1.45, -0.4, -0.78, 0.4], [0.78, -0.4, 1.45, 0.4]]
        pc.size = [3.2, 4.0, 1.3]
        return pc

    def rift_shard(cx):
        """a small floating rock (≈1.6 m): flat mossy top, pointed underside, two hanging stones"""
        pc = Piece("rift_shard")
        m = Mesh()
        r = K.rng(cx.seed, "rift_shard")
        st = gloom(cx)
        m.add(cylinder(0.8, 0.8, 0.18, 8, st, "stone", y0=-0.18, col_top=mix(W_, cx.c("moss"), 0.5)))
        m.add(cylinder(0.0, 0.8, 1.3, 7, mix(st, cx.c("ink"), 0.2), "stone", caps=False, y0=-1.48).xf(rot=(0, 0.3, 0)))
        for k in range(3):
            a = r.uniform(0, 2 * PI)
            m.add(sphere(0.12, 5, 3, cx.c("moss"), "paint", squash=(1, 0.6, 1)).xf((math.cos(a) * 0.6, 0.02, math.sin(a) * 0.6)))
        pc.mesh = m.ao(-1.5, 1.7, 0.3)
        pc.size = [1.6, 1.7, 1.6]
        return pc

    def rift_dais(cx):
        """the raised rune plinth in the circle's heart: two round steps (each under the walk step height)"""
        pc = Piece("rift_dais")
        m = Mesh()
        st = gloom(cx, -0.05)
        m.add(cylinder(2.3, 2.3, 0.14, 20, st, "stone", y0=0, cap_mat="stone", col_top=mix(W_, cx.c("stone"), 0.35)))
        m.add(cylinder(1.5, 1.5, 0.12, 16, mix(st, cx.c("stone_hi"), 0.1), "stone", y0=0.14, cap_mat="stone"))
        pc.mesh = m.ao(0, 0.3, 0.15)
        pc.size = [4.6, 0.26, 4.6]
        return pc

    def vine_arch(cx):
        """Vanaheim's way home: two living trunks bent into an arch, wrapped in leaves and gold blooms"""
        pc = Piece("vine_arch")
        m = Mesh()
        r = K.rng(cx.seed, "vine_arch")
        bark = mix(W_, cx.c("timber"), 0.4)
        m.add(box(3.2, 0.14, 1.2, mix(W_, cx.c("moss"), 0.4), "stone", y0=0))
        # trunks: stacked tapered cylinders up each side, then an arch of segments over the top
        for sx in (-1, 1):
            m.add(cylinder(0.3, 0.24, 2.3, 7, bark, "timber", y0=0.1).xf((sx * 1.2, 0, 0)))
            for k in range(3):
                m.add(cylinder(0.36, 0.3, 0.3, 7, bark, "timber", y0=0.1).xf((sx * 1.2 + sx * 0.12 * k, 0, r.uniform(-0.1, 0.1))))
        cy, R = 2.4, 1.2
        for i in range(10):
            a0, a1 = PI * i / 10, PI * (i + 1) / 10
            p0 = (math.cos(a0) * R, cy + math.sin(a0) * R, 0)
            p1 = (math.cos(a1) * R, cy + math.sin(a1) * R, 0)
            m.add(K.beam(p0, p1, 0.36, bark, "timber"))
        for k in range(26):
            a = r.uniform(0, PI)
            m.add(sphere(r.uniform(0.18, 0.32), 6, 4, cx.c("grass" if k % 3 else "leaf_deep"), "paint", noise=0.2, rnd=r).xf(
                (math.cos(a) * (R + 0.1), cy + math.sin(a) * (R + 0.1), r.uniform(-0.3, 0.3))))
        for k in range(8):
            a = r.uniform(0.1, PI - 0.1)
            m.add(sphere(0.09, 5, 3, cx.c("flower_gold" if k % 2 else "flower_rose"), "paint").xf(
                (math.cos(a) * (R + 0.3), cy + math.sin(a) * (R + 0.3), 0.3)))
        pc.mesh = m.ao(0, 4.0, 0.22)
        pc.markers["rift"] = [[0, 0.2, 0.0]]
        pc.blockers += [[-1.6, -0.4, -0.85, 0.4], [0.85, -0.4, 1.6, 0.4]]
        pc.size = [3.4, 4.0, 1.2]
        return pc

    return {"rift_isle": rift_isle, "rift_arch": rift_arch, "rift_shard": rift_shard, "rift_dais": rift_dais, "vine_arch": vine_arch}
