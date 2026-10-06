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

    return {"lumen_tree": lumen_tree, "elf_treehouse": elf_treehouse, "orb_lantern": orb_lantern, "prism_crystal": prism_crystal,
            "prism_door": prism_door, "vault_pillar": vault_pillar, "sylvaine_throne": sylvaine_throne, "moon_well": moon_well,
            "elf_banner": elf_banner}
