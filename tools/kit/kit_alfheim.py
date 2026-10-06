"""Alfheim pieces for hd2d kit (original, Hearthmoor realm-alfheim branch): Lumenvale (the light elves' tree town) and
the Prism Vault. Imported by kit.py; biome palette + the shared mesh helpers. Off-palette colours are only the NEON
accents on glow pixels (the self-lit 'glow' material, no bloom): violet (Alfheim's lead glow), cold-fire blue, red.

  lumen_tree      a tall pale-barked elf tree (~6.8 m): root flare, a crooked trunk, indigo canopy lobes hung with
                  violet leaf-lights and a few cold-fire wisp-fruit
  elf_treehouse   a Lumenvale home (~8 m): a huge trunk with a stair winding round it up to a ring deck and a round pod
                  house (plaster walls, timber ribs, a tall cloth-blue roof with a violet finial), violet + warm windows
  orb_lantern     an orb lantern (~2.6 m): a silver post and crook holding a glass orb with a glowing fish inside
  prism_crystal   a cluster of prism crystals on a rock (violet / cold-fire / white glow spires, dark facets)
  prism_door      the Prism Vault's door: a gloom-rock outcrop (~6 x 4.6 m) with a pointed doorway framed by crystal
                  pillars and a violet rune rim; the swirl billboard fits the opening (markers.rift)
  vault_pillar    a tall vault pillar (~4.6 m) wrapped in crystal with violet glow bands
  sylvaine_throne Lady Sylvaine's throne: three dais steps, a tall dark backrest crowned with crystal spikes and a
                  violet / red glow seam
  moon_well       Lumenvale's moon well: a pale stone basin of self-lit violet water with a cold-fire heart
  elf_banner      a tall silver pole with a long deep-blue pennant and a violet star sigil
"""
from __future__ import annotations

import math

PI = math.pi
VIOLET, VIOLET_HI, VIOLET_LO = "#a45cf0", "#d4a8ff", "#6a34b8"   # neon violet (Alfheim)
COLD, COLD_HI, COLD_LO = "#5ab4f0", "#d8f4ff", "#2a6cb0"         # cold fire
RED, RED_HI = "#e0302a", "#ff5a4a"


def pieces(K):
    box, cylinder, sphere, mix, Piece, W_, Mesh = K.box, K.cylinder, K.sphere, K.mix, K.Piece, K.W_, K.Mesh

    def gloom(cx, t=0.0):
        return mix(mix(W_, cx.c("stone_lo"), 0.55), cx.c("cloth"), 0.16 + t)

    def bark(cx, t=0.0):
        return mix(cx.c("stone_hi"), cx.c("plaster_lo"), 0.35 + t)

    def canopy(cx):
        return mix(cx.c("cloth"), cx.c("flower_blue"), 0.3)

    def speckle(m, r, lobes, n, cols):
        """violet leaf-lights scattered over the upper half of the canopy lobes, so the crown reads at night"""
        for k in range(n):
            x, y, z, R = lobes[k % len(lobes)]
            a, el = r.uniform(0, 2 * PI), r.uniform(0.1, 1.2)
            px, py, pz = x + math.cos(a) * math.cos(el) * R * 1.0, y + math.sin(el) * R * 0.72, z + math.sin(a) * math.cos(el) * R * 1.0
            m.add(box(0.13, 0.13, 0.13, cols[k % len(cols)], "glow").xf((px, py, pz), rot=(0.4, a, 0.6)))

    def spire(m, x, z, h, r, col, lean=(0.0, 0.0), y0=0.0, mat="glow"):
        """a 4-sided crystal spire: a short prism + a pointed tip"""
        m.add(cylinder(r, r * 0.85, h * 0.7, 4, col, mat, y0=y0).xf((x, 0, z), rot=(lean[0], PI / 4, lean[1])))
        m.add(cylinder(r * 0.85, 0.0, h * 0.3, 4, col, mat, caps=False, y0=y0 + h * 0.7).xf((x, 0, z), rot=(lean[0], PI / 4, lean[1])))

    # ------------------------------------------------------------------ trees + homes
    def lumen_tree(cx):
        pc = Piece("lumen_tree"); r = K.rng(cx.seed, "lumen_tree"); m = Mesh()
        for k in range(5):   # root flare
            a = k * 2 * PI / 5 + r.uniform(-0.3, 0.3)
            m.add(K.beam((math.cos(a) * 0.15, 0.35, math.sin(a) * 0.15), (math.cos(a) * 0.9, -0.05, math.sin(a) * 0.9), 0.22, bark(cx, 0.1), "paint"))
        pts = [(0, 0), (0.12, 1.4), (-0.1, 2.8), (0.15, 4.0)]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            m.add(cylinder(0.34 - y0 * 0.05, 0.32 - y1 * 0.05, y1 - y0, 7, bark(cx), "paint", y0=y0, col_top=bark(cx, 0.08)).xf((x0, 0, 0)))
        for k in range(3):   # boughs
            a = k * 2 * PI / 3 + 0.4
            m.add(K.beam((0.1, 3.2, 0), (math.cos(a) * 1.4, 4.4, math.sin(a) * 1.1), 0.16, bark(cx, 0.05), "paint"))
        lobes = [(0, 5.2, 0, 1.9), (-1.2, 4.6, 0.3, 1.3), (1.25, 4.7, -0.2, 1.35), (0.2, 4.4, 1.0, 1.2), (-0.3, 6.0, -0.3, 1.2)]
        for x, y, z, R in lobes:
            m.add(sphere(R, 9, 6, canopy(cx), "paint", squash=(1, 0.72, 1), noise=0.12, rnd=r, col_bottom=mix(canopy(cx), cx.c("ink"), 0.35)).xf((x, y, z)))
        speckle(m, r, lobes, 34, (VIOLET, VIOLET_HI, VIOLET_LO, VIOLET))
        for k in range(26):   # violet leaf-lights hanging off the canopy rim
            x, y, z, R = lobes[k % len(lobes)]
            a = r.uniform(0, 2 * PI)
            px, pz = x + math.cos(a) * R * 0.95, z + math.sin(a) * R * 0.95
            py = y - R * 0.45 - r.uniform(0, 0.4)
            m.add(box(0.06, r.uniform(0.25, 0.6), 0.06, VIOLET_LO, "glow", y0=py - 0.3).xf((px, 0, pz)))
            m.add(box(0.12, 0.12, 0.12, VIOLET_HI if k % 3 == 0 else VIOLET, "glow", y0=py - 0.42).xf((px, 0, pz), rot=(0, a, PI / 4)))
        for k in range(5):   # cold-fire wisp-fruit
            x, y, z, R = lobes[(k * 2) % len(lobes)]
            a = r.uniform(0, 2 * PI)
            m.add(sphere(0.11, 6, 4, COLD_HI if k % 2 else COLD, "glow").xf((x + math.cos(a) * R * 0.8, y - R * 0.6, z + math.sin(a) * R * 0.8)))
        pc.blockers.append([-0.42, -0.42, 0.42, 0.42])
        pc.mesh = m.ao(0, 7.0, 0.25)
        pc.size = [4.6, 7.0, 4.2]
        return pc

    def elf_treehouse(cx):
        pc = Piece("elf_treehouse"); r = K.rng(cx.seed, "elf_treehouse"); m = Mesh()
        TR, DH = 0.95, 3.0
        for k in range(6):   # roots
            a = k * 2 * PI / 6 + 0.2
            m.add(K.beam((math.cos(a) * 0.5, 0.6, math.sin(a) * 0.5), (math.cos(a) * 1.6, -0.05, math.sin(a) * 1.6), 0.3, bark(cx, 0.12), "paint"))
        m.add(cylinder(TR * 1.1, TR, DH + 3.2, 9, bark(cx), "paint", y0=0, col_top=bark(cx, 0.1)))
        for k in range(16):   # a stair of planks winding up round the trunk
            a = -PI / 2 + k * (1.6 * PI) / 16
            y = 0.2 + k * (DH - 0.2) / 16
            m.add(box(0.7, 0.07, 0.34, mix(cx.c("timber"), cx.c("timber_hi"), r.uniform(0, 0.3)), "timber", y0=y)
                  .xf((math.cos(a) * (TR + 0.38), 0, math.sin(a) * (TR + 0.38)), rot=(0, -a, 0)))
        m.add(cylinder(2.3, 2.3, 0.16, 12, cx.c("timber_lo"), "timber", y0=DH, col_top=cx.c("timber")))   # ring deck
        for k in range(12):   # deck rail posts + violet rail lights
            a = k * 2 * PI / 12
            m.add(box(0.08, 0.6, 0.08, cx.c("timber_lo"), "timber", y0=DH + 0.16).xf((math.cos(a) * 2.2, 0, math.sin(a) * 2.2)))
            if k % 3 == 1:
                m.add(sphere(0.09, 6, 4, VIOLET_HI, "glow").xf((math.cos(a) * 2.2, DH + 0.82, math.sin(a) * 2.2)))
        # the pod house
        m.add(cylinder(1.55, 1.45, 1.9, 10, cx.c("plaster"), "plaster", y0=DH + 0.16, col_top=cx.c("plaster_hi")))
        for k in range(10):   # timber ribs
            a = k * 2 * PI / 10
            m.add(box(0.08, 1.9, 0.08, cx.c("timber"), "timber", y0=DH + 0.16).xf((math.cos(a) * 1.52, 0, math.sin(a) * 1.52)))
        for k, (a, col) in enumerate(((PI / 2, VIOLET_HI), (PI / 2 + 0.9, cx.c("lamp")), (PI / 2 - 0.9, VIOLET), (-PI / 2, cx.c("lamp")))):
            x, z = math.cos(a) * 1.53, math.sin(a) * 1.53   # round-topped windows: a glow pane + a sill
            m.add(box(0.5, 0.62, 0.05, col, "glow", y0=DH + 0.9).xf((x, 0, z), rot=(0, -a + PI / 2, 0)))
            m.add(box(0.62, 0.06, 0.12, cx.c("timber_lo"), "timber", y0=DH + 0.86).xf((x, 0, z), rot=(0, -a + PI / 2, 0)))
        m.add(box(0.7, 1.25, 0.06, cx.c("timber_lo"), "timber", y0=DH + 0.16).xf((math.cos(PI / 2 + 1.7) * 1.52, 0, math.sin(PI / 2 + 1.7) * 1.52), rot=(0, -(PI / 2 + 1.7) + PI / 2, 0)))
        roof = mix(cx.c("cloth"), cx.c("shadow"), 0.25)
        m.add(cylinder(1.95, 1.2, 0.6, 12, roof, "roof", y0=DH + 2.0, col_top=mix(roof, cx.c("flower_blue"), 0.2)))
        m.add(cylinder(1.2, 0.0, 2.0, 12, mix(roof, cx.c("flower_blue"), 0.2), "roof", caps=False, y0=DH + 2.6))
        for k in range(12):   # violet glow trim along the eave
            a = k * 2 * PI / 12 + 0.13
            m.add(box(0.3, 0.05, 0.05, VIOLET, "glow", y0=DH + 2.0).xf((math.cos(a) * 1.95, 0, math.sin(a) * 1.95), rot=(0, -a + PI / 2, 0)))
        spire(m, 0, 0, 0.8, 0.12, VIOLET_HI, y0=DH + 4.5)   # violet finial crystal
        crown = ((-1.6, DH + 4.2, -0.6, 1.3), (1.5, DH + 3.9, -0.9, 1.2))
        for x, y, z, R in crown:   # canopy lobes behind the roof
            m.add(sphere(R, 8, 5, canopy(cx), "paint", squash=(1, 0.75, 1), noise=0.12, rnd=r, col_bottom=mix(canopy(cx), cx.c("ink"), 0.3)).xf((x, y, z)))
        speckle(m, r, crown, 16, (VIOLET, VIOLET_HI, VIOLET_LO))
        m.add(box(0.05, 0.5, 0.05, cx.c("shadow"), "paint", y0=DH - 0.5).xf((1.9, 0, 1.3)))   # a hanging lantern under the deck
        m.add(box(0.24, 0.3, 0.24, VIOLET, "glow", y0=DH - 0.85).xf((1.9, 0, 1.3)))
        m.add(box(0.12, 0.16, 0.12, VIOLET_HI, "glow", y0=DH - 0.78).xf((1.9, 0, 1.3)))
        pc.markers["lamps"].append([1.9, DH - 0.7, 1.3]); pc.markers["lamp_color"] = VIOLET; pc.markers["lamp_fixed"] = 0.45
        pc.blockers.append([-1.3, -1.3, 1.3, 1.3])
        pc.mesh = m.ao(0, DH + 5.3, 0.25)
        pc.size = [4.8, DH + 5.3, 4.8]
        return pc

    def orb_lantern(cx):
        pc = Piece("orb_lantern"); m = Mesh()
        st = mix(cx.c("stone_hi"), cx.c("plaster_hi"), 0.3)
        m.add(cylinder(0.22, 0.18, 0.12, 6, gloom(cx), "stone", y0=0))
        m.add(cylinder(0.06, 0.05, 2.3, 6, st, "paint", y0=0.12))
        m.add(K.beam((0, 2.38, 0), (0.0, 2.5, 0.42), 0.05, st, "paint"))
        m.add(box(0.03, 0.18, 0.03, cx.c("shadow"), "paint", y0=2.3).xf((0, 0, 0.45)))
        m.add(sphere(0.24, 9, 6, mix(COLD_LO, VIOLET_LO, 0.5), "glow").xf((0, 2.04, 0.45)))   # the glass orb (deep, self-lit)
        m.add(sphere(0.18, 8, 5, mix(VIOLET, COLD, 0.35), "glow").xf((0, 2.04, 0.46)))
        m.add(box(0.14, 0.06, 0.04, "#ffc463", "glow").xf((0.0, 2.02, 0.66)))              # the little glowing fish
        m.add(box(0.05, 0.08, 0.04, "#ffc463", "glow").xf((0.09, 2.02, 0.66)))
        m.add(box(0.04, 0.04, 0.04, COLD_HI, "glow").xf((-0.06, 2.12, 0.67)))               # a bubble
        m.add(cylinder(0.12, 0.08, 0.06, 6, cx.c("shadow"), "paint", y0=2.26).xf((0, 0, 0.45)))
        pc.markers["lamps"].append([0, 2.04, 0.5]); pc.markers["lamp_color"] = VIOLET; pc.markers["lamp_fixed"] = 0.5
        pc.markers["lamp_range"] = 4.0
        pc.blockers.append([-0.2, -0.2, 0.2, 0.2])
        pc.mesh = m.ao(0, 2.6, 0.2)
        pc.size = [0.6, 2.6, 0.9]
        return pc

    # ------------------------------------------------------------------ crystals + the vault
    def prism_crystal(cx):
        pc = Piece("prism_crystal"); r = K.rng(cx.seed, "prism_crystal"); m = Mesh()
        m.add(sphere(0.8, 7, 4, gloom(cx), "stone", squash=(1.1, 0.45, 0.9), noise=0.2, rnd=r).xf((0, 0.1, 0)))
        cols = (VIOLET, VIOLET_HI, COLD, VIOLET_LO, COLD_HI)
        for k, (x, z, h, rr) in enumerate(((0, 0, 2.2, 0.22), (-0.45, 0.2, 1.4, 0.17), (0.5, -0.1, 1.6, 0.18), (0.15, 0.45, 1.0, 0.13), (-0.2, -0.4, 1.2, 0.15))):
            lean = (r.uniform(-0.25, 0.25), r.uniform(-0.25, 0.25))
            spire(m, x, z, h, rr, cols[k], lean, y0=0.15)
            if k < 3:   # a dark facet beside each big spire, so the cluster reads in daylight too
                spire(m, x + 0.08, z - 0.06, h * 0.75, rr * 0.7, mix(gloom(cx), VIOLET_LO, 0.35), lean, y0=0.15, mat="paint")
        pc.blockers.append([-0.7, -0.6, 0.7, 0.6])
        pc.mesh = m.ao(0, 2.4, 0.18)
        pc.size = [1.8, 2.4, 1.6]
        return pc

    def prism_door(cx):
        pc = Piece("prism_door"); r = K.rng(cx.seed, "prism_door"); m = Mesh()
        st = gloom(cx)
        for k in range(14):   # the rock outcrop: overlapping lumpy boulders round the doorway
            a = PI * k / 13
            x, y = math.cos(a) * 2.4, 0.4 + math.sin(a) * 3.0
            m.add(sphere(r.uniform(0.9, 1.3), 7, 5, mix(st, cx.c("ink"), r.uniform(0.0, 0.25)), "stone", noise=0.2, rnd=r).xf((x, y, -0.6)))
        for sx in (-1, 1):
            m.add(box(1.6, 3.2, 1.6, mix(st, cx.c("stone_lo"), 0.1), "stone", y0=0).xf((sx * 2.55, 0, -0.4)))
        m.add(box(6.6, 1.2, 1.8, mix(st, cx.c("ink"), 0.15), "stone", y0=3.6).xf((0, 0, -0.7)))
        # the doorway: two crystal-wrapped jambs and a pointed arch of rune stones
        for sx in (-1, 1):
            m.add(box(0.5, 2.6, 0.6, mix(st, cx.c("stone_hi"), 0.15), "stone", y0=0).xf((sx * 1.25, 0, 0.3)))
            spire(m, sx * 1.6, 0.6, 2.4, 0.2, VIOLET, (sx * 0.15, 0.0))
            spire(m, sx * 1.85, 0.5, 1.5, 0.15, COLD, (sx * 0.25, 0.05))
        for k in range(9):
            a = PI * (0.1 + 0.8 * k / 8)
            x, y = math.cos(a) * 1.25, 2.6 + math.sin(a) * 1.0 - (0.35 if k in (0, 8) else 0)
            m.add(box(0.5, 0.36, 0.6, mix(st, cx.c("stone_hi"), 0.1 + 0.1 * (k % 2)), "stone").xf((x, y, 0.3), rot=(0, 0, a - PI / 2)))
            m.add(box(0.1, 0.1, 0.05, VIOLET_HI if k % 2 else VIOLET, "glow").xf((math.cos(a) * 0.98, 2.6 + math.sin(a) * 0.78, 0.62)))
        for sx in (-1, 1):   # violet rune rim down the jambs
            for k in range(6):
                m.add(box(0.06 if k % 2 else 0.12, 0.18, 0.05, VIOLET if k % 2 else VIOLET_HI, "glow", y0=0.3 + k * 0.38).xf((sx * 1.0, 0, 0.62)))
        m.add(box(2.0, 0.08, 0.9, mix(st, cx.c("stone_hi"), 0.2), "stone", y0=0).xf((0, 0, 0.6)))   # threshold
        spire(m, 0, -0.1, 1.2, 0.22, VIOLET_HI, y0=4.6)   # keystone crystal on top
        pc.markers["rift"] = [[0, 0.2, 0.35]]
        pc.blockers += [[-3.4, -1.5, -0.95, 1.0], [0.95, -1.5, 3.4, 1.0], [-0.95, -1.5, 0.95, -0.3]]
        pc.mesh = m.ao(0, 5.0, 0.25)
        pc.size = [6.8, 5.0, 3.0]
        return pc

    def vault_pillar(cx):
        pc = Piece("vault_pillar"); r = K.rng(cx.seed, "vault_pillar"); m = Mesh()
        st = gloom(cx)
        m.add(box(1.1, 0.3, 1.1, mix(st, cx.c("stone_lo"), 0.2), "stone", y0=0))
        m.add(cylinder(0.38, 0.34, 4.0, 8, st, "stone", y0=0.3, col_top=mix(st, cx.c("stone_hi"), 0.15)))
        m.add(box(1.0, 0.3, 1.0, mix(st, cx.c("stone_hi"), 0.12), "stone", y0=4.3))
        for k, y in enumerate((1.0, 2.2, 3.4)):   # violet glow bands
            m.add(cylinder(0.4, 0.4, 0.07, 8, VIOLET if k % 2 else VIOLET_HI, "glow", y0=y))
        for k in range(4):   # crystals growing up the shaft
            a = k * PI / 2 + r.uniform(-0.4, 0.4)
            spire(m, math.cos(a) * 0.42, math.sin(a) * 0.42, r.uniform(0.9, 1.5), 0.12, (VIOLET, COLD, VIOLET_HI, VIOLET_LO)[k], (math.sin(a) * 0.3, -math.cos(a) * 0.3), y0=0.3)
        pc.blockers.append([-0.55, -0.55, 0.55, 0.55])
        pc.mesh = m.ao(0, 4.6, 0.2)
        pc.size = [1.1, 4.6, 1.1]
        return pc

    def sylvaine_throne(cx):
        pc = Piece("sylvaine_throne"); r = K.rng(cx.seed, "sylvaine_throne"); m = Mesh()
        st = gloom(cx, 0.05)
        for k, (w, d) in enumerate(((5.0, 2.6), (4.2, 2.0), (3.4, 1.4))):   # dais steps
            m.add(box(w, 0.18, d, mix(st, cx.c("stone_hi"), 0.08 * k), "stone", y0=k * 0.18).xf((0, 0, -0.3 - k * 0.25)))
        m.add(box(2.2, 0.6, 1.0, mix(st, cx.c("ink"), 0.1), "stone", y0=0.54).xf((0, 0, -0.9)))   # seat
        m.add(box(2.6, 4.2, 0.5, mix(st, cx.c("ink"), 0.2), "stone", y0=0.54).xf((0, 0, -1.5)))   # tall backrest
        m.add(box(2.2, 3.6, 0.06, cx.c("roof_lo"), "paint", y0=0.9).xf((0, 0, -1.22)))           # red velvet panel
        for k in range(7):   # crystal crown on the backrest
            x = -1.2 + k * 0.4
            h = 1.0 + (1.0 if k == 3 else 0.5 if k in (2, 4) else 0.0)
            spire(m, x, -1.5, h, 0.16, (VIOLET, VIOLET_HI, COLD)[k % 3], (0, (x) * 0.2), y0=4.7)
        for sx in (-1, 1):   # glow seams up the backrest edges
            m.add(box(0.06, 4.0, 0.06, VIOLET if sx < 0 else RED, "glow", y0=0.6).xf((sx * 1.28, 0, -1.22)))
            spire(m, sx * 2.2, -0.4, 1.6, 0.2, VIOLET, (0, sx * 0.25), y0=0.0)
        pc.blockers.append([-1.4, -1.9, 1.4, -0.6])
        pc.mesh = m.ao(0, 6.5, 0.25)
        pc.size = [5.0, 6.5, 2.8]
        return pc

    def moon_well(cx):
        pc = Piece("moon_well"); r = K.rng(cx.seed, "moon_well"); m = Mesh()
        st = mix(cx.c("stone_hi"), cx.c("plaster_hi"), 0.3)
        m.add(cylinder(1.45, 1.5, 0.5, 14, st, "stone", y0=0, col_top=mix(st, cx.c("white"), 0.2)))
        m.add(cylinder(1.2, 1.2, 0.02, 14, VIOLET_LO, "glow", y0=0.4))
        m.add(cylinder(0.85, 0.85, 0.02, 12, VIOLET, "glow", y0=0.41))
        m.add(cylinder(0.35, 0.35, 0.02, 10, COLD_HI, "glow", y0=0.42))
        for k in range(8):   # moonstone studs on the rim
            a = k * 2 * PI / 8
            m.add(sphere(0.07, 5, 3, VIOLET_HI if k % 2 else COLD_HI, "glow").xf((math.cos(a) * 1.35, 0.52, math.sin(a) * 1.35)))
        spire(m, 0, 0, 1.2, 0.14, VIOLET_HI, y0=0.4)
        pc.blockers.append([-1.3, -1.3, 1.3, 1.3])
        pc.mesh = m.ao(0, 1.6, 0.15)
        pc.size = [3.0, 1.6, 3.0]
        return pc

    def elf_banner(cx):
        pc = Piece("elf_banner"); m = Mesh()
        st = mix(cx.c("stone_hi"), cx.c("plaster_hi"), 0.3)
        m.add(cylinder(0.05, 0.04, 3.6, 6, st, "paint", y0=0))
        m.add(box(0.05, 2.2, 0.62, cx.c("cloth"), "paint", y0=1.2).xf((0, 0, 0.36)))
        m.add(box(0.06, 0.08, 0.62, cx.c("plaster_hi"), "paint", y0=3.3).xf((0, 0, 0.36)))
        for dy, dz in ((0, 0), (0.18, 0), (-0.18, 0), (0, 0.18), (0, -0.18)):   # a violet star sigil
            m.add(box(0.06, 0.1, 0.1, VIOLET_HI if dy == 0 and dz == 0 else VIOLET, "glow").xf((0.03, 2.6 + dy, 0.36 + dz)))
        spire(m, 0, 0, 0.4, 0.07, VIOLET_HI, y0=3.6)
        pc.blockers.append([-0.12, -0.12, 0.12, 0.12])
        pc.mesh = m.ao(0, 4.0, 0.15)
        pc.size = [0.3, 4.0, 1.0]
        return pc

    more = lumenvale_pieces(K, gloom, bark, canopy, speckle, spire)
    return {**more, "lumen_tree": lumen_tree, "elf_treehouse": elf_treehouse, "orb_lantern": orb_lantern, "prism_crystal": prism_crystal,
            "prism_door": prism_door, "vault_pillar": vault_pillar, "sylvaine_throne": sylvaine_throne, "moon_well": moon_well,
            "elf_banner": elf_banner}



# ---------------------------------------------------------------------------------------------------------------------
# Session 2 (Story bot script alfheim.md): Lumenvale's Glimmer Steps, the Moonlit Court, the Wispwood and the Prism
# Vault rooms. Silverbark giants, glowing vine curtains, root-bowl glow-pools with glowfrogs, wisp nests, the frost scar,
# Wisp Market stalls, prism lanterns, the Empty Throne, the Prism Library, the Spire door, and the Vault's beam-puzzle
# furniture (mirror stands, source crystal, lens daises, the splitter, the Heart Prism, murals, the light bridge).
ROSE = "#ff4a3a"


def lumenvale_pieces(K, gloom, bark, canopy, speckle, spire):
    box, cylinder, sphere, mix, Piece, Mesh = K.box, K.cylinder, K.sphere, K.mix, K.Piece, K.Mesh

    def silver(cx, t=0.0):
        return mix(cx.c("stone_hi"), cx.c("white"), 0.25 + t)

    def frog(m, x, y, z, col, a=0.0):
        """a palm-sized glowfrog: a self-lit body, two eye bumps"""
        m.add(box(0.16, 0.08, 0.13, col, "glow", y0=y).xf((x, 0, z), rot=(0, a, 0)))
        for sx in (-1, 1):
            m.add(box(0.04, 0.04, 0.04, "#f0f0ff", "glow", y0=y + 0.08).xf((x + math.cos(a) * 0.05 * sx, 0, z - math.sin(a) * 0.05 * sx)))

    def silverbark(cx):
        """a silverbark giant (~11 m): a house-wide pale trunk with pulsing violet sap-veins, a ring platform, boughs
        hung with violet / blue vine strands, a dark indigo crown with leaf-lights"""
        pc = Piece("silverbark"); r = K.rng(cx.seed, "silverbark"); m = Mesh()
        for k in range(7):   # buttress roots
            a = k * 2 * PI / 7 + r.uniform(-0.2, 0.2)
            m.add(K.beam((math.cos(a) * 0.9, 1.2, math.sin(a) * 0.9), (math.cos(a) * 2.3, -0.05, math.sin(a) * 2.3), 0.42, bark(cx, 0.12), "paint"))
        m.add(cylinder(1.5, 1.25, 7.0, 12, bark(cx), "paint", y0=0, col_top=bark(cx, 0.06)))
        m.add(cylinder(1.25, 0.9, 2.4, 12, bark(cx, 0.04), "paint", y0=7.0))
        for k in range(9):   # sap veins: glow strips spiralling up the bark
            a = k * 2 * PI / 9
            for j in range(7):
                y = 0.4 + j * 0.95; aa = a + j * 0.16; rr = 1.5 - y * 0.035 + 0.02
                m.add(box(0.07, 0.6, 0.05, VIOLET if (j + k) % 3 else VIOLET_HI, "glow", y0=y).xf((math.cos(aa) * rr, 0, math.sin(aa) * rr), rot=(0, -aa + PI / 2, 0.15)))
        m.add(cylinder(2.5, 2.5, 0.16, 14, cx.c("timber_lo"), "timber", y0=3.4, col_top=cx.c("timber")))   # ring platform
        for k in range(14):
            a = k * 2 * PI / 14
            m.add(box(0.07, 0.55, 0.07, silver(cx), "paint", y0=3.56).xf((math.cos(a) * 2.42, 0, math.sin(a) * 2.42)))
            if k % 2 == 0:
                m.add(box(0.1, 0.1, 0.1, VIOLET_HI if k % 4 else COLD_HI, "glow", y0=4.12).xf((math.cos(a) * 2.42, 0, math.sin(a) * 2.42)))
        tips = []
        for k in range(4):   # boughs
            a = k * PI / 2 + 0.5
            tip = (math.cos(a) * 3.4, 8.4 + r.uniform(-0.3, 0.4), math.sin(a) * 3.0)
            m.add(K.beam((math.cos(a) * 0.6, 7.6, math.sin(a) * 0.6), tip, 0.28, bark(cx, 0.06), "paint")); tips.append(tip)
        lobes = [(0, 10.2, 0, 2.8), (-2.6, 9.2, 0.4, 2.0), (2.7, 9.4, -0.3, 2.0), (0.3, 9.0, 2.2, 1.9), (-0.4, 9.2, -2.2, 1.9)]
        for x, y, z, R in lobes:
            m.add(sphere(R, 9, 6, mix(canopy(cx), cx.c("ink"), 0.2), "paint", squash=(1, 0.65, 1), noise=0.12, rnd=r, col_bottom=mix(canopy(cx), cx.c("ink"), 0.5)).xf((x, y, z)))
        speckle(m, r, lobes, 46, (VIOLET, VIOLET_HI, VIOLET_LO, COLD))
        for k in range(30):   # hanging vine strands off the crown rim, budded violet / blue
            x, y, z, R = lobes[k % len(lobes)]
            a = r.uniform(0, 2 * PI); L = r.uniform(0.8, 2.4)
            px, pz, py = x + math.cos(a) * R * 0.92, z + math.sin(a) * R * 0.92, y - R * 0.4
            m.add(box(0.05, L, 0.05, mix(cx.c("leaf_deep"), VIOLET_LO, 0.4), "glow", y0=py - L).xf((px, 0, pz)))
            m.add(box(0.11, 0.11, 0.11, (VIOLET_HI, COLD, VIOLET)[k % 3], "glow", y0=py - L - 0.1).xf((px, 0, pz), rot=(0, a, PI / 4)))
        pc.blockers.append([-1.7, -1.7, 1.7, 1.7])
        pc.markers["lamps"].append([2.42, 4.2, 0]); pc.markers["lamp_color"] = VIOLET; pc.markers["lamp_fixed"] = 0.45; pc.markers["lamp_range"] = 5.0
        pc.mesh = m.ao(0, 12.0, 0.25)
        pc.size = [8.0, 12.0, 7.0]
        return pc

    def vine_curtain(cx):
        """a curtain of glowing vines hung from a silver bough-beam on two slim posts (~3.4 m)"""
        pc = Piece("vine_curtain"); r = K.rng(cx.seed, "vine_curtain"); m = Mesh()
        for sx in (-1, 1):
            m.add(cylinder(0.07, 0.06, 3.4, 6, silver(cx), "paint", y0=0).xf((sx * 1.5, 0, 0)))
        m.add(K.beam((-1.7, 3.35, 0), (1.7, 3.45, 0), 0.1, bark(cx, 0.05), "paint"))
        for k in range(15):
            x = -1.35 + k * 2.7 / 14 + r.uniform(-0.05, 0.05); L = r.uniform(1.4, 2.7)
            m.add(box(0.045, L, 0.045, mix(cx.c("shadow"), VIOLET_LO, 0.55), "glow", y0=3.35 - L).xf((x, 0, r.uniform(-0.08, 0.08))))
            for j in range(3):
                yy = 3.35 - L * (0.3 + 0.33 * j)
                m.add(box(0.09, 0.09, 0.09, (VIOLET_HI, COLD, VIOLET, COLD_HI)[(k + j) % 4], "glow", y0=yy).xf((x, 0, 0), rot=(0, 0, PI / 4)))
        pc.blockers += [[-1.6, -0.1, -1.4, 0.1], [1.4, -0.1, 1.6, 0.1]]
        pc.mesh = m.ao(0, 3.6, 0.15)
        pc.size = [3.4, 3.6, 0.4]
        return pc

    def glow_pool(cx):
        """Ferrin's glow-pool: a bowl of living wood (r 1.7) of neon-blue water, six lily pads, glowfrogs in three colours"""
        pc = Piece("glow_pool"); r = K.rng(cx.seed, "glow_pool"); m = Mesh()
        m.add(cylinder(1.75, 1.85, 0.42, 16, bark(cx, 0.15), "paint", y0=0, col_top=bark(cx, 0.05)))
        for k in range(10):   # root ribs round the bowl
            a = k * 2 * PI / 10
            m.add(K.beam((math.cos(a) * 1.7, 0.4, math.sin(a) * 1.7), (math.cos(a) * 2.2, -0.05, math.sin(a) * 2.2), 0.13, bark(cx, 0.18), "paint"))
        m.add(cylinder(1.5, 1.5, 0.02, 16, COLD_LO, "glow", y0=0.36))
        m.add(cylinder(1.1, 1.1, 0.02, 14, COLD, "glow", y0=0.37))
        m.add(cylinder(0.45, 0.45, 0.02, 10, COLD_HI, "glow", y0=0.38))
        cols = (COLD, VIOLET, ROSE, COLD, VIOLET)
        for k in range(6):
            a = k * 2 * PI / 6 + 0.3; rr = r.uniform(0.6, 1.2)
            x, z = math.cos(a) * rr, math.sin(a) * rr
            m.add(cylinder(0.22, 0.22, 0.03, 8, mix(cx.c("grass"), cx.c("ink"), 0.2), "paint", y0=0.39).xf((x, 0, z)))
            if k < 5:
                frog(m, x, 0.42, z, cols[k], a)
        pc.blockers.append([-1.8, -1.8, 1.8, 1.8])
        pc.markers["lamps"].append([0, 0.6, 0]); pc.markers["lamp_color"] = COLD; pc.markers["lamp_fixed"] = 0.5; pc.markers["lamp_range"] = 4.2
        pc.mesh = m.ao(0, 0.6, 0.15)
        pc.size = [4.4, 0.6, 4.4]
        return pc

    def frog_pond(cx):
        """a Wispwood glowfrog pond: a rim of dark stones, neon-blue water, lily pads, three glowfrogs"""
        pc = Piece("frog_pond"); r = K.rng(cx.seed, "frog_pond"); m = Mesh()
        for k in range(14):
            a = k * 2 * PI / 14
            m.add(sphere(r.uniform(0.22, 0.34), 6, 4, mix(gloom(cx), cx.c("ink"), r.uniform(0, 0.3)), "stone", squash=(1, 0.6, 1), noise=0.2, rnd=r)
                  .xf((math.cos(a) * 1.45, 0.08, math.sin(a) * 1.2)))
        m.add(cylinder(1.35, 1.35, 0.02, 16, COLD_LO, "glow", y0=0.04).xf((0, 0, 0)))
        m.add(cylinder(0.95, 0.95, 0.02, 14, COLD, "glow", y0=0.05))
        m.add(cylinder(0.35, 0.35, 0.02, 10, COLD_HI, "glow", y0=0.06))
        for k, col in enumerate((ROSE, COLD, VIOLET)):
            a = k * 2.1 + 0.4; x, z = math.cos(a) * 0.8, math.sin(a) * 0.65
            m.add(cylinder(0.2, 0.2, 0.03, 8, mix(cx.c("grass"), cx.c("ink"), 0.25), "paint", y0=0.07).xf((x, 0, z)))
            frog(m, x, 0.1, z, col, a)
        pc.blockers.append([-1.4, -1.15, 1.4, 1.15])
        pc.markers["lamps"].append([0, 0.4, 0]); pc.markers["lamp_color"] = COLD; pc.markers["lamp_fixed"] = 0.45; pc.markers["lamp_range"] = 3.6
        pc.mesh = m.ao(0, 0.5, 0.12)
        pc.size = [3.2, 0.5, 2.8]
        return pc

    def wisp_nest(cx):
        """a hollow stump wisp nest (~1 m): a grey dimmed wisp curled inside, glow moss on the rim"""
        pc = Piece("wisp_nest"); r = K.rng(cx.seed, "wisp_nest"); m = Mesh()
        m.add(cylinder(0.55, 0.62, 0.95, 9, bark(cx, 0.2), "paint", y0=0, col_top=mix(bark(cx, 0.2), cx.c("ink"), 0.5)))
        m.add(cylinder(0.4, 0.4, 0.02, 9, cx.c("ink"), "paint", y0=0.94))
        for k in range(5):
            a = k * 2 * PI / 5 + 0.3
            m.add(K.beam((math.cos(a) * 0.45, 0.4, math.sin(a) * 0.45), (math.cos(a) * 0.95, -0.05, math.sin(a) * 0.95), 0.12, bark(cx, 0.22), "paint"))
        for k in range(8):   # glow moss tufts
            a = r.uniform(0, 2 * PI)
            m.add(box(0.12, 0.05, 0.12, (VIOLET_LO, COLD_LO)[k % 2], "glow", y0=0.95).xf((math.cos(a) * 0.5, 0, math.sin(a) * 0.5)))
        m.add(sphere(0.16, 6, 4, "#8a8aa0", "glow").xf((0.05, 1.0, 0.05)))   # the grey wisp, curled up
        pc.blockers.append([-0.55, -0.55, 0.55, 0.55])
        pc.mesh = m.ao(0, 1.2, 0.15)
        pc.size = [1.4, 1.2, 1.4]
        return pc

    def frost_scar(cx):
        """Veyra's rune-cutting site: a ring of dead white-frosted vine curls round a flat stone, rimed ground"""
        pc = Piece("frost_scar"); r = K.rng(cx.seed, "frost_scar"); m = Mesh()
        m.add(cylinder(1.5, 1.5, 0.02, 16, mix(cx.c("white"), cx.c("sky"), 0.3), "paint", y0=0.01))
        m.add(box(0.9, 0.16, 0.6, mix(gloom(cx), cx.c("stone_hi"), 0.2), "stone", y0=0).xf((0, 0, 0), rot=(0, 0.3, 0)))
        for k in range(16):   # dead vine curls, frosted white
            a = k * 2 * PI / 16 + r.uniform(-0.1, 0.1); rr = r.uniform(1.0, 1.4)
            x, z = math.cos(a) * rr, math.sin(a) * rr
            m.add(K.beam((x, 0.0, z), (x * 0.92, r.uniform(0.35, 0.7), z * 0.92), 0.04, mix(cx.c("stone_lo"), cx.c("white"), 0.65), "paint"))
            m.add(box(0.07, 0.07, 0.07, "#e8f4ff", "glow" if k % 4 == 0 else "paint", y0=r.uniform(0.3, 0.6)).xf((x * 0.93, 0, z * 0.93)))
        for k in range(5):   # ice crystals
            a = k * 1.3
            spire(m, math.cos(a) * 0.9, math.sin(a) * 0.7, 0.4, 0.06, "#cfe8ff", (0.2, 0.0), mat="paint")
        pc.blockers.append([-0.45, -0.3, 0.45, 0.3])
        pc.mesh = m.ao(0, 0.8, 0.1)
        pc.size = [3.0, 0.8, 3.0]
        return pc

    def elf_stall(cx):
        """a Wisp Market stall: a timber counter under a violet cloth roof, prism lanterns hung from the eave"""
        pc = Piece("elf_stall"); m = Mesh()
        m.add(box(2.2, 0.9, 0.8, cx.c("timber"), "timber", y0=0).xf((0, 0, 0.2)))
        m.add(box(2.3, 0.06, 0.9, cx.c("timber_hi"), "timber", y0=0.9).xf((0, 0, 0.2)))
        for sx in (-1, 1):
            m.add(box(0.08, 2.4, 0.08, silver(cx), "paint", y0=0).xf((sx * 1.1, 0, 0.6)))
            m.add(box(0.08, 2.4, 0.08, silver(cx), "paint", y0=0).xf((sx * 1.1, 0, -0.3)))
        m.add(box(2.6, 0.08, 1.3, mix(cx.c("cloth"), VIOLET_LO, 0.35), "roof", y0=2.4).xf((0, 0, 0.15), rot=(0.18, 0, 0)))
        for k in range(5):
            x = -1.0 + k * 0.5
            m.add(box(0.02, 0.3, 0.02, cx.c("shadow"), "paint", y0=2.05).xf((x, 0, 0.75)))
            m.add(box(0.14, 0.18, 0.14, (VIOLET, COLD, ROSE, VIOLET_HI, COLD_HI)[k], "glow", y0=1.88).xf((x, 0, 0.75)))
        for k in range(4):   # lanterns for sale on the counter
            m.add(box(0.16, 0.22, 0.16, (VIOLET_HI, "#ffc463", COLD, VIOLET)[k], "glow", y0=0.96).xf((-0.75 + k * 0.5, 0, 0.25)))
        pc.markers["lamps"].append([0, 1.9, 0.75]); pc.markers["lamp_color"] = VIOLET; pc.markers["lamp_fixed"] = 0.4; pc.markers["lamp_range"] = 3.6
        pc.blockers.append([-1.15, -0.35, 1.15, 0.65])
        pc.mesh = m.ao(0, 2.6, 0.15)
        pc.size = [2.6, 2.6, 1.4]
        return pc

    def dwarf_stall(cx):
        """Brokk's stall: a squat copper-banded counter, an anvil, a small ember brazier (red glow), brass goods"""
        pc = Piece("dwarf_stall"); m = Mesh()
        m.add(box(2.0, 0.8, 0.8, cx.c("timber_lo"), "timber", y0=0).xf((0, 0, 0.2)))
        for y in (0.15, 0.6):
            m.add(box(2.04, 0.06, 0.84, mix(cx.c("roof"), cx.c("flower_gold"), 0.4), "paint", y0=y).xf((0, 0, 0.2)))
        m.add(box(0.5, 0.25, 0.25, cx.c("stone_lo"), "stone", y0=0.8).xf((-0.5, 0, 0.2)))
        m.add(box(0.7, 0.08, 0.25, cx.c("stone_lo"), "stone", y0=1.05).xf((-0.5, 0, 0.2)))
        m.add(cylinder(0.2, 0.16, 0.2, 8, cx.c("shadow"), "paint", y0=0.8).xf((0.55, 0, 0.2)))
        m.add(sphere(0.14, 6, 4, ROSE, "glow").xf((0.55, 1.02, 0.2)))
        for k in range(3):
            m.add(box(0.14, 0.14, 0.14, cx.c("flower_gold"), "paint", y0=0.8).xf((0.0 + k * 0.18, 0, 0.35)))
        for sx in (-1, 1):
            m.add(box(0.1, 1.9, 0.1, cx.c("timber_lo"), "timber", y0=0).xf((sx * 1.0, 0, -0.2)))
        m.add(box(2.3, 0.1, 1.1, cx.c("roof_lo"), "roof", y0=1.9).xf((0, 0, 0.1), rot=(0.15, 0, 0)))
        pc.markers["lamps"].append([0.55, 1.1, 0.2]); pc.markers["lamp_color"] = RED; pc.markers["lamp_fixed"] = 0.35; pc.markers["lamp_range"] = 2.6
        pc.blockers.append([-1.05, -0.3, 1.05, 0.65])
        pc.mesh = m.ao(0, 2.1, 0.15)
        pc.size = [2.3, 2.1, 1.2]
        return pc

    def prism_lantern(cx):
        """a Lantern Walk prism lantern (~2.9 m): a silver post topped by a glowing three-colour prism"""
        pc = Piece("prism_lantern"); m = Mesh()
        m.add(cylinder(0.2, 0.16, 0.14, 6, gloom(cx), "stone", y0=0))
        m.add(cylinder(0.05, 0.045, 2.4, 6, silver(cx), "paint", y0=0.14))
        m.add(cylinder(0.16, 0.0, 0.16, 3, silver(cx), "paint", y0=2.5, caps=True))
        spire(m, 0, 0, 0.5, 0.16, VIOLET_HI, y0=2.45)
        spire(m, 0.08, 0.04, 0.32, 0.08, COLD, y0=2.5)
        spire(m, -0.08, 0.03, 0.3, 0.07, ROSE, y0=2.5)
        pc.markers["lamps"].append([0, 2.6, 0]); pc.markers["lamp_color"] = VIOLET; pc.markers["lamp_fixed"] = 0.5; pc.markers["lamp_range"] = 4.0
        pc.blockers.append([-0.18, -0.18, 0.18, 0.18])
        pc.mesh = m.ao(0, 3.0, 0.15)
        pc.size = [0.5, 3.0, 0.5]
        return pc

    def empty_throne(cx):
        """the Empty Throne: violet glass on a moon-white dais, a dust sheet thrown over the seat"""
        pc = Piece("empty_throne"); m = Mesh()
        st = mix(cx.c("stone_hi"), cx.c("white"), 0.3)
        for k, (w, d) in enumerate(((4.4, 2.6), (3.6, 2.0), (2.8, 1.5))):
            m.add(box(w, 0.2, d, mix(st, cx.c("stone"), 0.06 * k), "stone", y0=k * 0.2).xf((0, 0, -0.2 - k * 0.2)))
        glass = mix(VIOLET_LO, cx.c("ink"), 0.25)
        m.add(box(1.8, 0.5, 1.0, glass, "glow", y0=0.6).xf((0, 0, -0.7)))
        m.add(box(2.0, 3.4, 0.35, glass, "glow", y0=0.6).xf((0, 0, -1.25)))
        for k in range(5):
            x = -0.8 + k * 0.4
            spire(m, x, -1.25, 0.6 + (0.6 if k == 2 else 0.3 if k in (1, 3) else 0), 0.13, VIOLET if k % 2 else VIOLET_HI, y0=4.0)
        sheet = mix(cx.c("plaster_hi"), cx.c("white"), 0.3)   # the dust sheet over the seat and down the front
        m.add(box(1.95, 0.06, 1.15, sheet, "plaster", y0=1.1).xf((0, 0, -0.7)))
        m.add(box(1.95, 0.9, 0.05, sheet, "plaster", y0=0.3).xf((0, 0, -0.15), rot=(0.12, 0, 0)))
        m.add(box(2.05, 1.4, 0.05, sheet, "plaster", y0=2.6).xf((0, 0, -1.05)))
        pc.blockers.append([-1.2, -1.6, 1.2, -0.2])
        pc.markers["lamps"].append([0, 2.2, -0.9]); pc.markers["lamp_color"] = VIOLET; pc.markers["lamp_fixed"] = 0.35; pc.markers["lamp_range"] = 4.5
        pc.mesh = m.ao(0, 5.2, 0.2)
        pc.size = [4.4, 5.2, 2.6]
        return pc

    def glass_shelf(cx):
        """a Prism Library shelf (2.4 x 2.3 m): dark wood, rows of glass books glowing faintly violet / blue"""
        pc = Piece("glass_shelf"); r = K.rng(cx.seed, "glass_shelf"); m = Mesh()
        m.add(box(2.4, 2.3, 0.45, cx.c("timber_lo"), "timber", y0=0))
        for row in range(4):
            y = 0.2 + row * 0.52
            m.add(box(2.3, 0.05, 0.42, cx.c("timber"), "timber", y0=y).xf((0, 0, 0.03)))
            x = -1.05
            while x < 1.0:
                w = r.uniform(0.06, 0.12); h = r.uniform(0.3, 0.44)
                m.add(box(w, h, 0.3, (VIOLET_LO, COLD_LO, VIOLET, mix(VIOLET_LO, COLD_LO, 0.5))[r.randrange(4)], "glow", y0=y + 0.05).xf((x + w / 2, 0, 0.1)))
                x += w + 0.02
        pc.blockers.append([-1.2, -0.25, 1.2, 0.25])
        pc.mesh = m.ao(0, 2.3, 0.15)
        pc.size = [2.4, 2.3, 0.5]
        return pc

    def lens_table(cx):
        """Mirelle's lens table: a desk with a big round lens on a brass stand over a violet light, notes and lens pouches"""
        pc = Piece("lens_table"); m = Mesh()
        m.add(box(1.8, 0.08, 0.9, cx.c("timber"), "timber", y0=0.82))
        for sx in (-1, 1):
            for sz in (-1, 1):
                m.add(box(0.08, 0.82, 0.08, cx.c("timber_lo"), "timber", y0=0).xf((sx * 0.8, 0, sz * 0.38)))
        m.add(cylinder(0.05, 0.05, 0.6, 6, cx.c("flower_gold"), "paint", y0=0.9))
        m.add(cylinder(0.42, 0.42, 0.06, 16, cx.c("flower_gold"), "paint", y0=1.45).xf((0, 0, 0), rot=(PI / 2.6, 0, 0)))
        m.add(cylinder(0.36, 0.36, 0.07, 16, mix(VIOLET, COLD_HI, 0.3), "glow", y0=1.45).xf((0, 0, 0.01), rot=(PI / 2.6, 0, 0)))
        m.add(box(0.5, 0.02, 0.35, cx.c("plaster_hi"), "plaster", y0=0.9).xf((0.55, 0, 0.1), rot=(0, 0.2, 0)))
        m.add(box(0.12, 0.12, 0.12, VIOLET_HI, "glow", y0=0.9).xf((-0.6, 0, -0.2)))
        pc.markers["lamps"].append([0, 1.5, 0.1]); pc.markers["lamp_color"] = VIOLET; pc.markers["lamp_fixed"] = 0.45; pc.markers["lamp_range"] = 3.4
        pc.blockers.append([-0.9, -0.45, 0.9, 0.45])
        pc.mesh = m.ao(0, 1.9, 0.12)
        pc.size = [1.8, 1.9, 0.9]
        return pc

    def spire_door(cx):
        """the Prism Spire's door: a tall pointed glass door (violet panes) in a silver frame set in a moon-white wall"""
        pc = Piece("spire_door"); m = Mesh()
        st = mix(cx.c("stone_hi"), cx.c("white"), 0.3)
        m.add(box(4.2, 4.8, 0.8, st, "stone", y0=0).xf((0, 0, -0.5)))
        for sx in (-1, 1):
            m.add(box(0.2, 3.8, 0.2, silver(cx, 0.1), "paint", y0=0).xf((sx * 1.05, 0, 0)))
        for k in range(7):
            a = PI * (0.08 + 0.84 * k / 6)
            m.add(box(0.22, 0.22, 0.2, silver(cx, 0.1), "paint").xf((math.cos(a) * 1.05, 3.8 + math.sin(a) * 0.7, 0)))
        for j in range(4):
            for i in range(3):
                m.add(box(0.6, 0.85, 0.05, (VIOLET_LO, VIOLET, mix(VIOLET, COLD, 0.4))[(i + j) % 3], "glow", y0=0.1 + j * 0.92).xf((-0.65 + i * 0.65, 0, 0.05)))
        spire(m, 0, 0, 1.0, 0.18, VIOLET_HI, y0=4.6)
        pc.markers["rift"] = [[0, 0.2, 0.3]]
        pc.markers["lamps"].append([0, 2.2, 0.4]); pc.markers["lamp_color"] = VIOLET; pc.markers["lamp_fixed"] = 0.6; pc.markers["lamp_range"] = 5.0
        pc.blockers += [[-2.1, -0.9, -0.95, 0.1], [0.95, -0.9, 2.1, 0.1], [-0.95, -0.9, 0.95, -0.2]]
        pc.mesh = m.ao(0, 5.6, 0.2)
        pc.size = [4.2, 5.6, 1.0]
        return pc

    # ------------------------------------------------------------------ Prism Vault furniture (the beam puzzles)
    def mirror_stand(cx):
        """a beam-puzzle mirror's turning pedestal; the mirror plate itself is a gamefx billboard (turns at runtime)"""
        pc = Piece("mirror_stand"); m = Mesh()
        m.add(cylinder(0.42, 0.48, 0.3, 8, gloom(cx), "stone", y0=0, col_top=mix(gloom(cx), cx.c("stone_hi"), 0.2)))
        m.add(cylinder(0.32, 0.32, 0.04, 12, VIOLET_LO, "glow", y0=0.3))
        for k in range(4):
            a = k * PI / 2
            m.add(box(0.08, 0.05, 0.08, VIOLET_HI, "glow", y0=0.31).xf((math.cos(a) * 0.36, 0, math.sin(a) * 0.36)))
        pc.blockers.append([-0.4, -0.4, 0.4, 0.4])
        pc.mesh = m.ao(0, 0.4, 0.1)
        pc.size = [1.0, 0.4, 1.0]
        return pc

    def beam_source(cx):
        """the dark source crystal on a plinth (lit with a spell; the lit glow is a gamefx billboard)"""
        pc = Piece("beam_source"); m = Mesh()
        m.add(box(0.9, 0.6, 0.9, gloom(cx), "stone", y0=0))
        spire(m, 0, 0, 1.0, 0.24, mix(gloom(cx), VIOLET_LO, 0.45), y0=0.6, mat="paint")
        for k in range(4):
            a = k * PI / 2 + PI / 4
            m.add(box(0.06, 0.2, 0.05, VIOLET_LO, "glow", y0=0.2).xf((math.cos(a) * 0.46, 0, math.sin(a) * 0.46)))
        pc.blockers.append([-0.45, -0.45, 0.45, 0.45])
        pc.mesh = m.ao(0, 1.6, 0.12)
        pc.size = [0.9, 1.6, 0.9]
        return pc

    def lens_dais(cx):
        """one of the Vault's three great lenses: a round silver-rimmed lens upright on a dais (dark until lit)"""
        pc = Piece("lens_dais"); m = Mesh()
        st = gloom(cx, 0.04)
        m.add(cylinder(1.0, 1.1, 0.25, 12, st, "stone", y0=0, col_top=mix(st, cx.c("stone_hi"), 0.15)))
        for sx in (-1, 1):
            m.add(box(0.14, 1.6, 0.18, silver(cx), "paint", y0=0.25).xf((sx * 0.85, 0, 0)))
        m.add(cylinder(0.8, 0.8, 0.12, 18, silver(cx, 0.05), "paint", y0=1.5).xf((0, 0, 0), rot=(PI / 2, 0, 0)))
        m.add(cylinder(0.68, 0.68, 0.14, 18, mix(cx.c("ink"), VIOLET_LO, 0.35), "glow", y0=1.5).xf((0, 0, 0.0), rot=(PI / 2, 0, 0)))
        pc.blockers.append([-0.95, -0.5, 0.95, 0.5])
        pc.mesh = m.ao(0, 2.4, 0.15)
        pc.size = [2.2, 2.4, 1.2]
        return pc

    def prism_splitter(cx):
        """the Splitter Hall's great prism: a triangular glass prism on a round pedestal, three colour notches"""
        pc = Piece("prism_splitter"); m = Mesh()
        m.add(cylinder(0.9, 1.0, 0.4, 10, gloom(cx), "stone", y0=0))
        m.add(cylinder(0.75, 0.75, 1.5, 3, mix(VIOLET_LO, COLD_HI, 0.25), "glow", y0=0.4))
        for k, col in enumerate((VIOLET, COLD, ROSE)):
            a = k * 2 * PI / 3 + PI / 3
            m.add(box(0.14, 0.14, 0.14, col, "glow", y0=0.5).xf((math.cos(a) * 0.86, 0, math.sin(a) * 0.86)))
        pc.blockers.append([-0.85, -0.85, 0.85, 0.85])
        pc.mesh = m.ao(0, 1.9, 0.12)
        pc.size = [2.0, 1.9, 2.0]
        return pc

    def heart_prism(cx):
        """the Heart Prism (~3.4 m): a great violet crystal cracked with white frost, on a round dais"""
        pc = Piece("heart_prism"); r = K.rng(cx.seed, "heart_prism"); m = Mesh()
        m.add(cylinder(2.0, 2.2, 0.3, 16, gloom(cx, 0.04), "stone", y0=0))
        spire(m, 0, 0, 3.4, 0.9, mix(VIOLET, VIOLET_LO, 0.4), y0=0.3)
        spire(m, 0.7, 0.3, 1.8, 0.4, VIOLET, (0.2, 0.25), y0=0.3)
        spire(m, -0.75, 0.2, 2.0, 0.42, VIOLET_HI, (-0.2, -0.2), y0=0.3)
        spire(m, 0.1, -0.7, 1.4, 0.35, COLD, (0.1, -0.3), y0=0.3)
        for k in range(14):   # white frost cracks
            y = 0.6 + r.uniform(0, 2.4); a = r.uniform(-1.2, 1.2)
            m.add(box(0.05, r.uniform(0.2, 0.5), 0.03, "#eef6ff", "glow", y0=y).xf((math.sin(a) * 0.7, 0, 0.62 + math.cos(a) * 0.05), rot=(0, 0, r.uniform(-0.8, 0.8))))
        pc.blockers.append([-1.2, -1.2, 1.2, 1.2])
        pc.markers["lamps"].append([0, 1.8, 0.8]); pc.markers["lamp_color"] = VIOLET; pc.markers["lamp_fixed"] = 0.7; pc.markers["lamp_range"] = 7.0
        pc.mesh = m.ao(0, 4.0, 0.2)
        pc.size = [4.4, 4.0, 4.4]
        return pc

    def cracked_prism(cx):
        """a Hall of Shards prism (~2.4 m): broken, frost-rimed, leaking violet light from its cracks"""
        pc = Piece("cracked_prism"); r = K.rng(cx.seed, "cracked_prism"); m = Mesh()
        m.add(box(1.0, 0.3, 1.0, gloom(cx), "stone", y0=0))
        spire(m, 0, 0, 2.2, 0.38, mix(VIOLET_LO, cx.c("ink"), 0.3), (0.12, 0.05), y0=0.3, mat="paint")
        for k in range(6):
            m.add(box(0.05, r.uniform(0.2, 0.45), 0.04, VIOLET_HI if k % 2 else "#eef6ff", "glow", y0=0.5 + k * 0.28).xf((r.uniform(-0.15, 0.15), 0, 0.32), rot=(0, 0, r.uniform(-0.6, 0.6))))
        pc.blockers.append([-0.5, -0.5, 0.5, 0.5])
        pc.mesh = m.ao(0, 2.6, 0.12)
        pc.size = [1.0, 2.6, 1.0]
        return pc

    def mural_wall(cx):
        """a Reliquary Walk mural panel (3 x 2.6 m): a moon-white frame round a painted panel (dark, violet, silver)"""
        pc = Piece("mural_wall"); r = K.rng(cx.seed, "mural_wall"); m = Mesh()
        st = mix(cx.c("stone_hi"), cx.c("white"), 0.25)
        m.add(box(3.2, 2.8, 0.3, st, "stone", y0=0))
        m.add(box(2.8, 2.2, 0.04, mix(cx.c("ink"), VIOLET_LO, 0.2), "paint", y0=0.3).xf((0, 0, 0.16)))
        for k in range(26):   # stylised figures and wisps in paint
            x, y = r.uniform(-1.2, 1.2), r.uniform(0.45, 2.3)
            m.add(box(r.uniform(0.06, 0.2), r.uniform(0.08, 0.4), 0.03, (cx.c("plaster_hi"), VIOLET, cx.c("stone_hi"), COLD_LO)[k % 4], "paint" if k % 5 else "glow", y0=y).xf((x, 0, 0.19)))
        pc.blockers.append([-1.6, -0.2, 1.6, 0.2])
        pc.mesh = m.ao(0, 2.8, 0.12)
        pc.size = [3.2, 2.8, 0.4]
        return pc

    def tall_mirror(cx):
        """a Hall of Reflections mirror: a tall silver-framed glass panel (1.6 x 3 m) with a cold sheen"""
        pc = Piece("tall_mirror"); m = Mesh()
        m.add(box(1.7, 3.1, 0.2, silver(cx), "paint", y0=0))
        m.add(box(1.4, 2.7, 0.05, mix(cx.c("sky"), cx.c("ink"), 0.55), "glow", y0=0.2).xf((0, 0, 0.11)))
        for k in range(3):
            m.add(box(0.06, 1.6, 0.02, mix(cx.c("white"), VIOLET_HI, 0.3), "glow", y0=0.6 + k * 0.15).xf((-0.4 + k * 0.25, 0, 0.14), rot=(0, 0, 0.3)))
        pc.blockers.append([-0.85, -0.15, 0.85, 0.15])
        pc.mesh = m.ao(0, 3.1, 0.12)
        pc.size = [1.7, 3.1, 0.3]
        return pc

    def reliquary(cx):
        """a reliquary chest: moon-white stone with a violet glass lid"""
        pc = Piece("reliquary"); m = Mesh()
        m.add(box(1.0, 0.55, 0.6, mix(cx.c("stone_hi"), cx.c("white"), 0.25), "stone", y0=0))
        m.add(box(1.05, 0.12, 0.65, mix(VIOLET_LO, VIOLET, 0.4), "glow", y0=0.55))
        m.add(box(0.14, 0.14, 0.04, cx.c("flower_gold"), "paint", y0=0.35).xf((0, 0, 0.31)))
        pc.blockers.append([-0.5, -0.3, 0.5, 0.3])
        pc.mesh = m.ao(0, 0.7, 0.1)
        pc.size = [1.0, 0.7, 0.6]
        return pc

    def light_bridge(cx):
        """the Cracked Stair's bridge of light (2.2 x 8 m of glowing glass planks, walk it as a deck) over a black chasm"""
        pc = Piece("light_bridge"); m = Mesh()
        for k in range(16):
            z = -3.75 + k * 0.5
            m.add(box(2.0, 0.06, 0.42, (VIOLET, VIOLET_HI, mix(VIOLET, COLD, 0.4))[k % 3], "glow", y0=-0.06).xf((0, 0, z)))
        for sx in (-1, 1):
            m.add(box(0.06, 0.06, 8.0, COLD_HI, "glow", y0=0.5).xf((sx * 1.05, 0, 0)))
            for k in range(5):
                m.add(box(0.05, 0.5, 0.05, VIOLET_LO, "glow", y0=0.0).xf((sx * 1.05, 0, -3.6 + k * 1.8)))
        pc.mesh = m.ao(-0.1, 0.6, 0.05)
        pc.size = [2.2, 0.6, 8.0]
        return pc

    def chasm(cx):
        """a black chasm (8 x 8 m): an ink pit edged with frost-cracked stone lips and faint violet light far below"""
        pc = Piece("chasm"); r = K.rng(cx.seed, "chasm"); m = Mesh()
        m.add(box(8.0, 0.02, 8.0, cx.c("ink"), "paint", y0=0.0))
        for k in range(18):
            m.add(box(0.12, 0.02, 0.12, VIOLET_LO if k % 3 else VIOLET, "glow", y0=0.01).xf((r.uniform(-3.6, 3.6), 0, r.uniform(-3.6, 3.6))))
        pc.mesh = m.ao(0, 0.1, 0.02)
        pc.size = [8.0, 0.1, 8.0]
        return pc

    return {"silverbark": silverbark, "vine_curtain": vine_curtain, "glow_pool": glow_pool, "frog_pond": frog_pond,
            "wisp_nest": wisp_nest, "frost_scar": frost_scar, "elf_stall": elf_stall, "dwarf_stall": dwarf_stall,
            "prism_lantern": prism_lantern, "empty_throne": empty_throne, "glass_shelf": glass_shelf, "lens_table": lens_table,
            "spire_door": spire_door, "mirror_stand": mirror_stand, "beam_source": beam_source, "lens_dais": lens_dais,
            "prism_splitter": prism_splitter, "heart_prism": heart_prism, "cracked_prism": cracked_prism, "mural_wall": mural_wall,
            "tall_mirror": tall_mirror, "reliquary": reliquary, "light_bridge": light_bridge, "chasm": chasm}
