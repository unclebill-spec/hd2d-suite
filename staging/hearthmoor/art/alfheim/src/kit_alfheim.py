"""Alfheim / Lumenvale + the Prism Vault pieces for hd2d kit (original; Hearthmoor Art seat staging, 2026-10-05).
Elf realm of light magic: moonstone-white architecture, glowing treetops, violet neon crystals, wisps.

City (Lumenvale)
  lumen_tree          a 5.4 m white-barked tree; canopy studded with glowing violet / blue / pink leaf-lights, hanging glow vines
  lumen_tree_small    a 2.8 m sapling of the same (street / garden filler)
  lumen_lamp          a 2.6 m moonstone street lamp: a violet prism lamp in a gold cage on a curled post
  crystal_spire       a 3.2 m cluster of violet neon crystals on a pale stone mound (plaza / waymarker)
  prism_fountain      a 2.6 m tiered moonstone fountain of glowing violet water crowned by a prism
  elf_archway         a 3.5 m leaf-pointed moonstone arch with a violet crystal keystone and glowing hanging vines
  wisp_lantern_post   a 2.4 m crook post hanging a gold cage with a captured blue wisp (the wisp-catching icon)
  light_bridge        a 4.0 m moonstone footbridge with violet glow inlays and glowing post caps
  elf_rail            a 2.0 m moonstone railing segment with glowing caps (bridges, treetop walks, terraces)
  lumen_pavilion      a 3.4 m open six-column pavilion with a crystal-ribbed roof and a hanging orb light
  wisp_jar            a 0.4 m glass jar with a caught wisp (wisp-catching prop / shop item)
Dungeon (The Prism Vault)
  vault_floor         a 2 x 2 m dark crystal-veined floor tile with violet inlay lines
  vault_wall          a 2.0 m wide, 3.2 m tall dark stone wall with violet crystal veins and a crystal cluster
  vault_pillar        a 3.4 m dark stone pillar with a violet crystal capital
  sylvaine_throne     Lady Sylvaine's throne: a three-step dais, a tall dark throne, a fan of violet crystals behind

Drop-in: copy to tools/kit/ and add to kit.py like kit_harbor:
    import kit_alfheim as _af; PROPS.update(_af.pieces(__import__('types').SimpleNamespace(**globals())))
Neon hexes only on the 'glow' material (crystals, leaf-lights, vines, wisps, water, inlays)."""
from __future__ import annotations

import math

PI = math.pi
NV, NV_HI, NV_LO = "#a45cf0", "#d4a8ff", "#6a34b8"
NB, NB_HI, NB_LO = "#2ab4ff", "#a6ecff", "#1c62d8"
PINK, PINK_HI = "#ff4fc8", "#ffb4ea"
GREEN = "#3cf08a"
GOLD = "#f2c24a"


def pieces(K):
    box, cylinder, sphere, beam, mix, Piece, W_, Mesh = K.box, K.cylinder, K.sphere, K.beam, K.mix, K.Piece, K.W_, K.Mesh

    def moon(cx, t=0.0):
        """moonstone: plaster_hi with a cool sky tint"""
        return mix(mix(cx.c("plaster_hi"), cx.c("sky"), 0.22), cx.c("stone_lo"), t)

    def vault(cx, t=0.0):
        return mix(mix(cx.c("ink"), cx.c("cloth"), 0.38), "#000000", t)

    def lamp(pc, pos, col, rng_, fixed=0.5):
        pc.markers["lamps"].append(list(pos)); pc.markers["lamp_color"] = col; pc.markers["lamp_range"] = rng_; pc.markers["lamp_fixed"] = fixed

    def crystal(m, pos, h, r, col, hi, tilt=(0.0, 0.0), seg=6):
        c = Mesh()
        c.add(cylinder(r, r * 0.92, h * 0.78, seg, col, "glow", y0=0))
        c.add(cylinder(r * 0.92, 0.0, h * 0.22, seg, hi, "glow", y0=h * 0.78))
        c.add(box(r * 0.25, h * 0.7, r * 0.25, hi, "glow", y0=h * 0.04).xf((-r * 0.55, 0, r * 0.6)))   # bright facet edge
        m.add(c.xf((0, 0, 0), rot=(tilt[0], 0, tilt[1])).xf(pos))

    def bulb(m, x, y, z, R, col, hi):
        m.add(sphere(R, 6, 4, col, "glow").xf((x, y, z)))
        m.add(sphere(R * 0.45, 5, 3, hi, "glow").xf((x - R * 0.25, y + R * 0.3, z + R * 0.4)))

    def vine(m, x, y, z, L, col, hi, k=0):
        m.add(beam([x, y, z], [x + 0.03, y - L, z], 0.025, NV_LO if k % 2 else mix(NV_LO, "#202040", 0.4), "glow"))
        for j in range(int(L / 0.22)):
            m.add(box(0.05, 0.05, 0.05, hi if (j + k) % 3 == 0 else col, "glow", y0=y - 0.15 - j * 0.22).xf((x + 0.01, 0, z + 0.02)))
        bulb(m, x + 0.03, y - L - 0.06, z, 0.06, col, hi)

    def bark(cx, t=0.0):
        return mix(mix(cx.c("stone_hi"), cx.c("plaster_hi"), 0.4), cx.c("stone_lo"), t)

    # ------------------------------------------------------------------ trees
    def tree(name, s, seed):
        def f(cx):
            pc = Piece(name); r = K.rng(cx.seed, seed); m = Mesh()
            pts = [(0, 0, 0), (0.08 * s, 1.0 * s, 0.02), (-0.06 * s, 2.0 * s, 0), (0.04 * s, 2.9 * s, 0)]
            for k, (a, b) in enumerate(zip(pts, pts[1:])):
                m.add(beam(list(a), list(b), (0.34 - 0.07 * k) * s, bark(cx, 0.05 * k), "timber"))
            for k in range(5):                                                       # flared roots
                a = k * 2 * PI / 5 + 0.3
                m.add(beam([0, 0.25 * s, 0], [math.cos(a) * 0.6 * s, 0.0, math.sin(a) * 0.5 * s], 0.13 * s, bark(cx, 0.15), "timber"))
            for k in range(4):                                                       # branches up into the canopy
                a = k * PI / 2 + 0.6
                m.add(beam([0, 2.4 * s, 0], [math.cos(a) * 1.0 * s, 3.3 * s, math.sin(a) * 0.7 * s], 0.11 * s, bark(cx, 0.1), "timber"))
            m.add(beam([0.05 * s, 0.8 * s, 0.17 * s], [0.03 * s, 2.2 * s, 0.14 * s], 0.035 * s, NV_HI, "glow"))  # a glowing rune-vein
            leaf = mix(mix(cx.c("leaf_deep"), cx.c("cloth"), 0.45), NV_LO, 0.3)
            blobs = [(0, 3.9, 0, 1.15), (-1.0, 3.5, 0.1, 0.85), (1.0, 3.55, -0.1, 0.9), (0.4, 4.4, -0.2, 0.8), (-0.5, 4.3, 0.2, 0.75),
                     (0.1, 3.4, 0.7, 0.8), (-0.2, 3.5, -0.7, 0.8), (1.3, 3.2, 0.5, 0.55), (-1.3, 3.15, -0.4, 0.55)]
            cols = (NV, NV_HI, NB, NV, PINK, NV_HI, NB_HI, NV)
            for (x, y, z, R) in blobs:
                m.add(sphere(R * s, 8, 5, mix(leaf, "#000000", r.uniform(0, 0.15)), "moss", squash=(1, 0.72, 1), noise=0.06, rnd=r).xf((x * s, y * s, z * s)))
                for j in range(int(20 * R)):                                          # leaf-lights on the surface
                    a, e = r.uniform(0, 2 * PI), r.uniform(-0.2, 1.1)
                    px, py, pz = math.cos(a) * math.cos(e) * R, math.sin(e) * R * 0.72, math.sin(a) * math.cos(e) * R
                    m.add(box(0.09 * s, 0.09 * s, 0.09 * s, cols[(j + int(x * 7)) % len(cols)], "glow").xf(((x + px) * s, (y + py) * s, (z + pz) * s)))
            for k, (x, z, L) in enumerate(((-1.1, 0.4, 1.0), (-0.5, 0.9, 1.4), (0.3, 0.95, 0.9), (0.9, 0.6, 1.3), (1.4, 0.2, 0.7), (-1.4, -0.2, 0.8))):
                vine(m, x * s, 3.1 * s, z * s, L * s, (NV, NB, PINK)[k % 3], (NV_HI, NB_HI, PINK_HI)[k % 3], k)
            pc.mesh = m.ao(0, 4.8 * s, 0.15)
            pc.blockers.append([-0.35 * s, -0.35 * s, 0.35 * s, 0.35 * s])
            lamp(pc, (0, 3.0 * s, 0.6 * s), NV, 7.0 * s, 0.55)
            pc.size = [3.2 * s, 5.0 * s, 2.4 * s]
            return pc
        return f

    # ------------------------------------------------------------------ street
    def lumen_lamp(cx):
        pc = Piece("lumen_lamp"); m = Mesh(); st = moon(cx)
        m.add(cylinder(0.26, 0.2, 0.18, 8, moon(cx, 0.2), "stone", y0=0))
        m.add(cylinder(0.07, 0.05, 2.0, 8, st, "stone", y0=0.18))
        for k in range(5):                                                          # the curl at the top
            a0, a1 = k / 5 * PI, (k + 1) / 5 * PI
            m.add(beam([0.22 - 0.22 * math.cos(a0), 2.15 + 0.22 * math.sin(a0), 0], [0.22 - 0.22 * math.cos(a1), 2.15 + 0.22 * math.sin(a1), 0], 0.05, st, "stone"))
        m.add(beam([0.44, 2.15, 0], [0.44, 2.05, 0], 0.02, GOLD, "paint"))
        m.add(sphere(0.16, 4, 2, NV_HI, "glow", squash=(1, 1.7, 1)).xf((0.44, 1.86, 0)))
        m.add(sphere(0.12, 4, 2, NV, "glow", squash=(1, 1.7, 1)).xf((0.5, 1.84, 0.06)))          # the prism lamp
        m.add(sphere(0.08, 4, 2, W_, "glow", squash=(1, 1.6, 1)).xf((0.42, 1.9, 0.05)))
        for k in range(4):
            a = k * PI / 2 + PI / 4
            m.add(beam([0.44 + math.cos(a) * 0.15, 2.04, math.sin(a) * 0.15], [0.44 + math.cos(a) * 0.15, 1.68, math.sin(a) * 0.15], 0.018, GOLD, "paint"))
        m.add(sphere(0.06, 4, 2, NV, "glow", squash=(1, 1.4, 1)).xf((0, 2.08, 0)))
        pc.mesh = m.ao(0, 2.5, 0.12)
        pc.blockers.append([-0.2, -0.2, 0.2, 0.2])
        lamp(pc, (0.44, 1.86, 0), NV, 5.0)
        pc.size = [0.7, 2.6, 0.5]
        return pc

    def crystal_spire(cx):
        pc = Piece("crystal_spire"); r = K.rng(cx.seed, "spire"); m = Mesh()
        for k in range(6):
            a = k * PI / 3
            m.add(sphere(r.uniform(0.35, 0.5), 6, 4, moon(cx, r.uniform(0.1, 0.35)), "stone", squash=(1, 0.55, 1)).xf((math.cos(a) * 0.45, 0.08, math.sin(a) * 0.4)))
        m.add(sphere(0.6, 7, 4, moon(cx, 0.15), "stone", squash=(1, 0.5, 1)).xf((0, 0.1, 0)))
        for (x, z, h, R, col, hi, t) in ((0, 0, 3.0, 0.24, NV, NV_HI, (0, 0.04)), (0.38, 0.1, 1.9, 0.17, NV, NV_HI, (0.1, -0.35)),
                                          (-0.4, 0.05, 1.6, 0.16, NV_LO, NV, (-0.05, 0.4)), (0.12, 0.42, 1.1, 0.13, NB, NB_HI, (0.4, -0.1)),
                                          (-0.2, -0.38, 1.3, 0.14, NV, NV_HI, (-0.35, 0.15)), (0.5, -0.3, 0.8, 0.1, PINK, PINK_HI, (-0.2, -0.5))):
            crystal(m, (x, 0.2, z), h, R, col, hi, t)
        pc.mesh = m.ao(0, 0.6, 0.2)
        pc.blockers.append([-0.7, -0.6, 0.7, 0.6])
        lamp(pc, (0, 1.6, 0.4), NV, 5.5)
        pc.size = [1.6, 3.2, 1.4]
        return pc

    def prism_fountain(cx):
        pc = Piece("prism_fountain"); m = Mesh(); st = moon(cx)
        water, deep = mix(NV, "#1a1240", 0.35), mix(NV_LO, "#100a2a", 0.4)
        m.add(cylinder(1.3, 1.25, 0.5, 14, moon(cx, 0.15), "stone", y0=0))
        m.add(K.ring(1.08, 1.34, 0.52, 14, st, "stone", h=0.04))
        m.add(cylinder(1.08, 1.08, 0.02, 14, deep, "glow", y0=0.44))
        m.add(K.ring(0.6, 1.06, 0.465, 14, water, "glow"))
        for k in range(10):
            a = k / 10 * 2 * PI
            m.add(box(0.12, 0.01, 0.05, NV_HI, "glow", y0=0.47).xf((math.cos(a) * 0.8, 0, math.sin(a) * 0.8)))
        m.add(cylinder(0.18, 0.14, 1.1, 8, st, "stone", y0=0.45))
        m.add(cylinder(0.55, 0.3, 0.22, 10, moon(cx, 0.1), "stone", y0=1.5))
        m.add(cylinder(0.5, 0.5, 0.02, 10, water, "glow", y0=1.7))
        m.add(cylinder(0.1, 0.08, 0.3, 6, st, "stone", y0=1.7))
        crystal(m, (0, 2.0, 0), 0.6, 0.14, NV, NV_HI)
        for k in range(6):                                                          # glowing streams spilling from the bowl
            a = k / 6 * 2 * PI + 0.3
            x0, z0 = math.cos(a) * 0.52, math.sin(a) * 0.52
            m.add(beam([x0, 1.7, z0], [x0 * 1.25, 1.2, z0 * 1.25], 0.035, NV_HI, "glow"))
            m.add(beam([x0 * 1.25, 1.2, z0 * 1.25], [x0 * 1.35, 0.48, z0 * 1.35], 0.03, NV if k % 2 else NB_HI, "glow"))
        pc.mesh = m.ao(0, 2.2, 0.12)
        pc.blockers.append([-1.3, -1.3, 1.3, 1.3])
        lamp(pc, (0, 1.0, 0.8), NV, 6.0)
        pc.size = [2.7, 2.6, 2.7]
        return pc

    def elf_archway(cx):
        pc = Piece("elf_archway"); m = Mesh(); st = moon(cx)
        for sd in (-1, 1):
            x = sd * 1.4
            m.add(box(0.5, 0.25, 0.5, moon(cx, 0.2), "stone", y0=0).xf((x, 0, 0)))
            m.add(cylinder(0.15, 0.13, 2.2, 8, st, "stone", y0=0.25).xf((x, 0, 0)))
            m.add(box(0.4, 0.14, 0.4, moon(cx, 0.1), "stone", y0=2.45).xf((x, 0, 0)))
            m.add(beam([x, 0.4, 0.15], [x, 2.3, 0.15], 0.03, NV_HI, "glow"))     # glowing flute on the column front
        pts = []
        for k in range(9):                                                          # a leaf-pointed arch
            t = k / 8
            x = -1.4 + 2.8 * t
            y = 2.6 + 0.95 * math.sin(t * PI) ** 0.7
            pts.append([x, y, 0])
        for a, b in zip(pts, pts[1:]):
            m.add(beam(a, b, 0.2, st, "stone"))
            m.add(beam([a[0], a[1] - 0.12, 0.12], [b[0], b[1] - 0.12, 0.12], 0.04, NV_LO, "glow"))
        crystal(m, (0, 3.35, 0.05), 0.55, 0.12, NV, NV_HI)
        m.add(sphere(0.06, 5, 3, W_, "glow").xf((0, 3.66, 0.12)))
        for k, x in enumerate((-1.0, -0.55, -0.15, 0.3, 0.7, 1.05)):
            y = 2.6 + 0.95 * math.sin((x + 1.4) / 2.8 * PI) ** 0.7 - 0.12
            vine(m, x, y, 0.05, 0.5 + (k % 3) * 0.3, (NV, NB, PINK)[k % 3], (NV_HI, NB_HI, PINK_HI)[k % 3], k)
        pc.mesh = m.ao(0, 3.6, 0.15)
        pc.blockers += [[-1.65, -0.25, -1.15, 0.25], [1.15, -0.25, 1.65, 0.25]]
        lamp(pc, (0, 3.0, 0.4), NV, 5.0)
        pc.size = [3.3, 3.8, 0.5]
        return pc

    def wisp_lantern_post(cx):
        pc = Piece("wisp_lantern_post"); m = Mesh(); st = moon(cx)
        m.add(cylinder(0.2, 0.16, 0.14, 8, moon(cx, 0.2), "stone", y0=0))
        m.add(beam([0, 0.1, 0], [0, 2.2, 0], 0.08, cx.c("timber_hi"), "timber"))
        for k in range(6):                                                          # the crook
            a0, a1 = k / 6 * PI, (k + 1) / 6 * PI
            m.add(beam([0.25 - 0.25 * math.cos(a0), 2.2 + 0.25 * math.sin(a0), 0], [0.25 - 0.25 * math.cos(a1), 2.2 + 0.25 * math.sin(a1), 0], 0.06, cx.c("timber_hi"), "timber"))
        m.add(beam([0.5, 2.2, 0], [0.5, 2.0, 0], 0.015, GOLD, "paint"))
        cy = 1.78
        for (dx, dz) in ((-0.12, -0.12), (0.12, -0.12), (-0.12, 0.12), (0.12, 0.12)):
            m.add(beam([0.5 + dx, cy - 0.2, dz], [0.5 + dx, cy + 0.2, dz], 0.014, mix(cx.c("ink"), cx.c("cloth"), 0.3), "paint"))
        iron = mix(cx.c("ink"), cx.c("cloth"), 0.3)
        m.add(box(0.3, 0.04, 0.3, iron, "paint", y0=cy + 0.2).xf((0.5, 0, 0)))
        m.add(cylinder(0.08, 0.0, 0.1, 6, iron, "paint", y0=cy + 0.24).xf((0.5, 0, 0)))
        m.add(box(0.3, 0.04, 0.3, iron, "paint", y0=cy - 0.24).xf((0.5, 0, 0)))
        bulb(m, 0.5, cy, 0.02, 0.12, NB, NB_HI)
        m.add(sphere(0.045, 4, 2, W_, "glow").xf((0.48, cy + 0.03, 0.08)))
        pc.mesh = m.ao(0, 2.4, 0.1)
        pc.blockers.append([-0.18, -0.18, 0.18, 0.18])
        lamp(pc, (0.5, cy, 0), NB, 4.5)
        pc.size = [0.8, 2.5, 0.4]
        return pc

    def rail_posts(m, cx, x0, x1, z, n, h=0.9):
        st = moon(cx)
        for k in range(n):
            x = x0 + (x1 - x0) * k / max(1, n - 1)
            m.add(box(0.12, h, 0.12, st, "stone", y0=0).xf((x, 0, z)))
            m.add(sphere(0.07, 4, 2, NV_HI, "glow", squash=(1, 1.5, 1)).xf((x, h + 0.08, z)))
        m.add(box(abs(x1 - x0) + 0.1, 0.08, 0.1, st, "stone", y0=h - 0.12).xf(((x0 + x1) / 2, 0, z)))
        m.add(box(abs(x1 - x0), 0.025, 0.04, NV, "glow", y0=h - 0.3).xf(((x0 + x1) / 2, 0, z + 0.03)))

    def light_bridge(cx):
        pc = Piece("light_bridge"); m = Mesh(); st = moon(cx)
        for k in range(8):                                                          # a gently arched deck
            x = -1.75 + k * 0.5
            y = 0.35 + 0.25 * math.sin((k + 0.5) / 8 * PI)
            m.add(box(0.52, 0.18, 1.6, st if k % 2 else moon(cx, 0.06), "stone", y0=y - 0.18).xf((x, 0, 0)))
            m.add(box(0.5, 0.012, 0.05, NV_HI, "glow", y0=y + 0.005).xf((x, 0, 0.7)))
            m.add(box(0.5, 0.012, 0.05, NV_HI, "glow", y0=y + 0.005).xf((x, 0, -0.7)))
            m.add(box(0.52, y - 0.18, 1.3, moon(cx, 0.3 if k % 2 else 0.34), "stone", y0=0).xf((x, 0, 0)))
        sub = Mesh(); rail_posts(sub, cx, -1.9, 1.9, 0, 5, 0.85); m.add(sub.xf((0, 0.55, 0.78)))
        sub = Mesh(); rail_posts(sub, cx, -1.9, 1.9, 0, 5, 0.85); m.add(sub.xf((0, 0.55, -0.78)))
        pc.mesh = m.ao(0, 1.5, 0.12)
        lamp(pc, (0, 1.3, 0.8), NV, 4.0)
        pc.size = [4.0, 1.6, 1.7]
        pc.markers["walk_height_center"] = 0.6
        return pc

    def elf_rail(cx):
        pc = Piece("elf_rail"); m = Mesh()
        rail_posts(m, cx, -0.95, 0.95, 0, 3)
        pc.mesh = m.ao(0, 1.0, 0.1)
        pc.blockers.append([-1.0, -0.08, 1.0, 0.08])
        pc.size = [2.0, 1.0, 0.15]
        return pc

    def lumen_pavilion(cx):
        pc = Piece("lumen_pavilion"); m = Mesh(); st = moon(cx)
        m.add(cylinder(1.6, 1.65, 0.22, 12, moon(cx, 0.15), "stone", y0=0))
        m.add(K.ring(1.2, 1.5, 0.225, 12, NV_LO, "glow"))
        for k in range(6):
            a = k / 6 * 2 * PI + PI / 6
            x, z = math.cos(a) * 1.35, math.sin(a) * 1.35
            m.add(cylinder(0.09, 0.08, 2.5, 8, st, "stone", y0=0.22).xf((x, 0, z)))
            m.add(box(0.22, 0.1, 0.22, moon(cx, 0.1), "stone", y0=2.7).xf((x, 0, z)))
        m.add(cylinder(1.6, 1.55, 0.14, 12, st, "stone", y0=2.8))
        m.add(cylinder(1.55, 0.15, 0.8, 12, mix(moon(cx, 0.2), cx.c("cloth"), 0.2), "paint", y0=2.94))
        for k in range(12):                                                         # crystal ribs on the roof
            a = k / 12 * 2 * PI
            m.add(beam([math.cos(a) * 1.5, 2.98, math.sin(a) * 1.5], [math.cos(a) * 0.2, 3.7, math.sin(a) * 0.2], 0.03, NV_HI if k % 2 else NV, "glow"))
        crystal(m, (0, 3.7, 0), 0.5, 0.1, NV, NV_HI)
        m.add(beam([0, 2.8, 0], [0, 2.3, 0], 0.015, GOLD, "paint"))
        bulb(m, 0, 2.18, 0, 0.14, NV, NV_HI)
        pc.mesh = m.ao(0, 3.8, 0.12)
        for k in range(6):
            a = k / 6 * 2 * PI + PI / 6
            x, z = math.cos(a) * 1.35, math.sin(a) * 1.35
            pc.blockers.append([x - 0.12, z - 0.12, x + 0.12, z + 0.12])
        lamp(pc, (0, 2.18, 0), NV, 5.5)
        pc.size = [3.3, 4.2, 3.3]
        return pc

    def wisp_jar(cx):
        pc = Piece("wisp_jar"); m = Mesh()
        glass = mix(cx.c("sky"), "#203050", 0.45)
        m.add(cylinder(0.12, 0.12, 0.26, 8, glass, "glow", y0=0))
        m.add(cylinder(0.09, 0.09, 0.05, 8, cx.c("timber"), "timber", y0=0.26))
        m.add(beam([-0.08, 0.33, 0], [0.08, 0.33, 0], 0.012, GOLD, "paint"))
        bulb(m, 0, 0.13, 0.03, 0.055, NB, NB_HI)
        pc.mesh = m.ao(0, 0.35, 0.1)
        lamp(pc, (0, 0.13, 0.1), NB, 1.5)
        pc.size = [0.26, 0.36, 0.26]
        return pc

    # ------------------------------------------------------------------ Prism Vault
    def vault_floor(cx):
        pc = Piece("vault_floor"); r = K.rng(cx.seed, "vfloor"); m = Mesh()
        for i in range(4):
            for j in range(4):
                x0, z0 = -1 + i * 0.5, -1 + j * 0.5
                c = mix(vault(cx), cx.c("stone_lo"), r.uniform(0.0, 0.12))
                m.quad((x0, 0, z0 + 0.5), (x0 + 0.5, 0, z0 + 0.5), (x0 + 0.5, 0, z0), (x0, 0, z0), c, mat="stone")
        for k in (-1.0, 0.0, 1.0):
            m.add(box(2.0, 0.006, 0.03, NV_LO, "glow", y0=0.0).xf((0, 0, k * 0.98)))
            m.add(box(0.03, 0.006, 2.0, NV_LO, "glow", y0=0.0).xf((k * 0.98, 0, 0)))
        m.add(box(0.1, 0.008, 0.1, NV_HI, "glow", y0=0.0))
        pc.mesh = m
        pc.size = [2.0, 0.01, 2.0]
        return pc

    def vault_wall(cx):
        pc = Piece("vault_wall"); r = K.rng(cx.seed, "vwall"); m = Mesh()
        for row in range(8):
            off = 0.25 if row % 2 else 0
            for k in range(5):
                x = -1 + off + k * 0.5
                if x > 1.0:
                    continue
                w = min(0.48, 1.0 - x + 0.24) if x > 0.76 else 0.48
                m.add(box(w, 0.38, 0.5, mix(vault(cx), cx.c("stone_lo"), r.uniform(0.05, 0.2)), "stone", y0=row * 0.4).xf((x, 0, 0)))
        pts = [(-0.7, 0.2), (-0.5, 0.9), (-0.65, 1.5), (-0.3, 2.2), (-0.4, 3.0)]
        for a, b in zip(pts, pts[1:]):
            m.add(beam([a[0], a[1], 0.26], [b[0], b[1], 0.26], 0.04, NV, "glow"))
        for (x, y, h, R, t) in ((0.45, 0.0, 0.9, 0.12, (0.2, 0.1)), (0.65, 0.0, 0.6, 0.09, (0.3, -0.4)), (0.25, 0.0, 0.5, 0.08, (0.4, 0.4))):
            crystal(m, (x, y, 0.3), h, R, NV, NV_HI, t)
        m.add(box(2.04, 0.12, 0.56, mix(vault(cx), cx.c("cloth"), 0.2), "stone", y0=3.2))
        pc.mesh = m.ao(0, 3.3, 0.18)
        pc.blockers.append([-1, -0.25, 1, 0.25])
        lamp(pc, (0.4, 0.6, 0.6), NV, 3.0, 0.4)
        pc.size = [2.0, 3.32, 0.56]
        return pc

    def vault_pillar(cx):
        pc = Piece("vault_pillar"); m = Mesh()
        m.add(box(0.8, 0.3, 0.8, vault(cx, 0.1), "stone", y0=0))
        m.add(cylinder(0.28, 0.26, 2.6, 8, mix(vault(cx), cx.c("stone_lo"), 0.15), "stone", y0=0.3))
        m.add(beam([0.0, 0.4, 0.27], [0.0, 2.8, 0.25], 0.03, NV_LO, "glow"))
        m.add(box(0.75, 0.2, 0.75, vault(cx, 0.05), "stone", y0=2.9))
        for k in range(5):
            a = k / 5 * 2 * PI
            crystal(m, (math.cos(a) * 0.18, 3.08, math.sin(a) * 0.18), 0.35 + (k % 2) * 0.15, 0.07, NV if k % 2 else NV_HI, W_, (math.sin(a) * 0.35, -math.cos(a) * 0.35))
        pc.mesh = m.ao(0, 3.4, 0.15)
        pc.blockers.append([-0.4, -0.4, 0.4, 0.4])
        lamp(pc, (0, 3.2, 0.3), NV, 3.5)
        pc.size = [0.8, 3.5, 0.8]
        return pc

    def sylvaine_throne(cx):
        pc = Piece("sylvaine_throne"); m = Mesh()
        for k in range(3):
            m.add(box(3.4 - k * 0.6, 0.2, 2.4 - k * 0.5, mix(vault(cx), cx.c("cloth"), 0.1 + 0.08 * k), "stone", y0=k * 0.2).xf((0, 0, -0.1 * k)))
            m.add(box(3.4 - k * 0.6, 0.012, 0.04, NV_LO if k < 2 else NV, "glow", y0=k * 0.2 + 0.2).xf((0, 0, 1.2 - 0.35 * k - 0.02)))
        y0 = 0.6
        m.add(box(1.0, 0.45, 0.8, vault(cx), "stone", y0=y0).xf((0, 0, -0.3)))
        m.add(box(0.86, 0.1, 0.66, cx.c("roof_lo"), "paint", y0=y0 + 0.45).xf((0, 0, -0.26)))   # wine-red cushion
        m.add(box(1.0, 2.2, 0.22, vault(cx, 0.05), "stone", y0=y0).xf((0, 0, -0.68)))
        m.add(box(0.7, 1.7, 0.02, cx.c("roof_lo"), "paint", y0=y0 + 0.55).xf((0, 0, -0.56)))
        for sd in (-1, 1):
            m.add(box(0.16, 0.55, 0.8, vault(cx, 0.08), "stone", y0=y0).xf((sd * 0.56, 0, -0.3)))
            m.add(sphere(0.07, 4, 2, NV_HI, "glow").xf((sd * 0.56, y0 + 0.62, 0.08)))
        m.add(cylinder(0.3, 0.0, 0.45, 4, vault(cx, 0.05), "stone", y0=y0 + 2.2).xf((0, 0, -0.68)))
        for k, (a, h) in enumerate(((-0.75, 1.6), (-0.4, 2.3), (0.0, 3.0), (0.4, 2.3), (0.75, 1.6))):   # fan of crystals
            crystal(m, (math.sin(a) * 0.9, y0 + 0.5, -0.85 - 0.1 * abs(a)), h, 0.13 + 0.02 * (k == 2), NV if k % 2 == 0 else NV_LO, NV_HI, (0, -a * 0.6))
        pc.mesh = m.ao(0, 3.2, 0.15)
        pc.blockers.append([-1.7, -1.3, 1.7, 1.1])
        lamp(pc, (0, 2.0, -0.2), NV, 6.5)
        pc.size = [3.4, 4.1, 2.4]
        pc.markers["boss_stand"] = [0, 0.6, 0.6]
        return pc

    return {"lumen_tree": tree("lumen_tree", 1.0, "ltree"), "lumen_tree_small": tree("lumen_tree_small", 0.55, "ltree_s"),
            "lumen_lamp": lumen_lamp, "crystal_spire": crystal_spire, "prism_fountain": prism_fountain, "elf_archway": elf_archway,
            "wisp_lantern_post": wisp_lantern_post, "light_bridge": light_bridge, "elf_rail": elf_rail,
            "lumen_pavilion": lumen_pavilion, "wisp_jar": wisp_jar, "vault_floor": vault_floor, "vault_wall": vault_wall,
            "vault_pillar": vault_pillar, "sylvaine_throne": sylvaine_throne}
