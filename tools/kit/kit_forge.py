"""Ravenhold Forge Quarter pieces for hd2d kit (original; Hearthmoor Art seat staging, 2026-10-05). DESIGN_EXPANSION E6.2:
red forge mouths, blue cold-fire quench tanks, the master smith Hilde Anvilsong.

forge_anvil       a black-iron anvil (horn, heel, hardy hole) on an oak stump, a red-hot bar on the face (glow)
forge_hearth      a brick-and-stone forge: glowing red mouth with coals, a tapered hood and chimney (3.6 m), side bellows
quench_tank       a stone quench trough of neon-blue cold-fire water (Ravenhold's signature), iron bands
tool_rack         an oak rack with hammers, tongs and a file hanging
grindstone        a sandstone wheel on a timber frame with a foot treadle and a drip bucket
coal_bin          a timber bin of coal with a few live embers
forge_sign        the Forge Quarter hanging sign: an anvil emblem on a board, on an iron bracket post

Drop-in: copy to tools/kit/ and add to kit.py like kit_harbor:
    import kit_forge as _fg; PROPS.update(_fg.pieces(__import__('types').SimpleNamespace(**globals())))
Neon hexes only on the 'glow' material (forge fire, hot metal, embers, cold-fire water)."""
from __future__ import annotations

import math

PI = math.pi
RED, RED_HI, RED_LO, GOLD = "#e0302a", "#ff5a4a", "#a81c22", "#ffc463"
COLD, COLD_HI, COLD_LO = "#5ab4f0", "#d8f4ff", "#2a6cb0"
NB, NB_HI = "#2ab4ff", "#a6ecff"


def pieces(K):
    box, cylinder, sphere, beam, mix, Piece, W_, Mesh = K.box, K.cylinder, K.sphere, K.beam, K.mix, K.Piece, K.W_, K.Mesh

    def iron(cx, t=0.0):
        return mix(mix(cx.c("ink"), cx.c("stone_lo"), 0.45 + t), cx.c("cloth"), 0.12)

    def forge_anvil(cx):
        pc = Piece("forge_anvil"); m = Mesh()
        m.add(cylinder(0.36, 0.32, 0.5, 10, cx.c("timber"), "timber", y0=0, col_top=cx.c("timber_hi")))
        m.add(cylinder(0.3, 0.3, 0.02, 10, cx.c("plaster_lo"), "paint", y0=0.5))
        ir = iron(cx)
        m.add(box(0.42, 0.1, 0.3, ir, "paint", y0=0.52))                       # foot
        m.add(box(0.24, 0.16, 0.18, mix(ir, cx.c("ink"), 0.2), "paint", y0=0.62))   # waist
        m.add(box(0.56, 0.12, 0.24, mix(ir, cx.c("stone"), 0.15), "paint", y0=0.78))   # body / face
        m.add(box(0.54, 0.02, 0.22, mix(ir, cx.c("stone_hi"), 0.35), "paint", y0=0.9))  # polished face
        m.add(cylinder(0.11, 0.0, 0.32, 8, ir, "paint", y0=0).xf((0, 0, 0), rot=(0, 0, PI / 2)).xf((-0.28, 0.85, 0)))   # horn
        m.add(box(0.03, 0.01, 0.03, cx.c("ink"), "paint", y0=0.915).xf((0.2, 0, 0)))  # hardy hole
        m.add(box(0.3, 0.035, 0.04, RED_HI, "glow", y0=0.92).xf((0.02, 0, 0.02)))     # the red-hot bar
        m.add(box(0.1, 0.03, 0.035, GOLD, "glow", y0=0.925).xf((0.1, 0, 0.02)))
        pc.markers["lamps"].append([0, 1.0, 0.2]); pc.markers["lamp_color"] = RED_HI; pc.markers["lamp_fixed"] = 0.25; pc.markers["lamp_range"] = 2.0
        pc.mesh = m.ao(0, 1.0, 0.15)
        pc.blockers.append([-0.35, -0.3, 0.35, 0.3])
        pc.size = [0.9, 0.95, 0.75]
        return pc

    def forge_hearth(cx):
        pc = Piece("forge_hearth"); r = K.rng(cx.seed, "hearth"); m = Mesh()
        st = mix(W_, cx.c("stone_lo"), 0.25)
        brick = mix(cx.c("roof_lo"), cx.c("shadow"), 0.35)
        m.add(box(2.0, 0.95, 1.3, st, "stone", y0=0))
        for k in range(6):                                                     # stone courses
            m.add(box(2.02, 0.02, 1.32, mix(st, cx.c("ink"), 0.3), "paint", y0=0.15 + k * 0.15))
        m.add(box(1.0, 0.55, 0.04, mix(cx.c("ink"), RED_LO, 0.35), "glow", y0=0.25).xf((0, 0, 0.665)))   # mouth: a deep red-lit recess
        m.add(box(0.9, 0.22, 0.03, RED, "glow", y0=0.27).xf((0, 0, 0.685)))
        for k in range(7):                                                     # glowing coals in the mouth
            x = -0.4 + k * 0.13
            m.add(sphere(0.07, 5, 3, (RED_HI, GOLD, RED_HI, "#fff0c0", RED_HI, GOLD, RED_HI)[k], "glow", squash=(1.2, 0.7, 0.5)).xf((x, 0.32 + (k % 2) * 0.05, 0.7)))
        m.add(box(1.16, 0.1, 0.1, mix(st, cx.c("stone_hi"), 0.3), "stone", y0=0.8).xf((0, 0, 0.66)))   # lintel
        m.add(box(2.1, 0.08, 1.4, mix(st, cx.c("stone_hi"), 0.2), "stone", y0=0.95))                   # top slab
        m.add(box(0.8, 0.04, 0.6, RED, "glow", y0=1.03))                                                # fire bed on top
        for k in range(4):
            m.add(sphere(0.08, 5, 3, (RED_HI, GOLD, RED_HI, RED)[k], "glow", squash=(1.3, 0.5, 1)).xf((-0.24 + k * 0.16, 1.07, 0.05 * (k % 2))))
        # tapered brick hood + chimney
        for k, (w, d, y) in enumerate(((1.9, 1.2, 1.9), (1.4, 0.95, 2.35), (0.9, 0.7, 2.75))):
            m.add(box(w, 0.42, d, mix(brick, cx.c("ink"), 0.08 * k), "stone", y0=y).xf((0, 0, -0.1)))
        for sx in (-0.85, 0.85):
            m.add(box(0.14, 0.82, 0.14, brick, "stone", y0=1.03).xf((sx, 0, 0.45)))                      # hood posts
        m.add(box(0.6, 0.5, 0.5, brick, "stone", y0=3.15).xf((0, 0, -0.1)))
        m.add(box(0.7, 0.08, 0.6, mix(brick, cx.c("ink"), 0.3), "stone", y0=3.62).xf((0, 0, -0.1)))
        # bellows on the right side
        m.add(box(0.5, 0.12, 0.7, cx.c("timber"), "timber", y0=0.55).xf((1.3, 0, 0.1)))
        m.add(box(0.46, 0.2, 0.62, mix(cx.c("timber_lo"), cx.c("roof_lo"), 0.3), "paint", y0=0.67).xf((1.3, 0, 0.1)))
        m.add(box(0.5, 0.08, 0.7, cx.c("timber"), "timber", y0=0.87).xf((1.3, 0, 0.1)))
        m.add(beam([1.3, 0.95, 0.45], [1.3, 1.25, 0.85], 0.05, cx.c("timber_lo"), "timber"))
        m.add(beam([1.05, 0.7, -0.2], [1.0, 0.7, -0.2], 0.08, iron(cx), "paint"))
        pc.markers["lamps"].append([0, 0.55, 0.9]); pc.markers["lamp_color"] = RED_HI; pc.markers["lamp_fixed"] = 0.6; pc.markers["lamp_range"] = 6.0
        pc.mesh = m.ao(0, 3.7, 0.22)
        pc.blockers.append([-1.05, -0.7, 1.6, 0.7])
        pc.size = [3.2, 3.7, 1.4]
        return pc

    def quench_tank(cx):
        pc = Piece("quench_tank"); m = Mesh()
        st = mix(W_, cx.c("stone"), 0.3)
        m.add(box(1.4, 0.62, 0.72, st, "stone", y0=0))
        m.add(box(1.24, 0.04, 0.56, NB, "glow", y0=0.63))                       # cold-fire water, just under the rim top
        m.add(box(0.9, 0.01, 0.36, COLD, "glow", y0=0.67))
        for k in range(5):
            m.add(box(0.12, 0.01, 0.03, (NB_HI, W_, COLD_HI, NB_HI, W_)[k], "glow", y0=0.68).xf((-0.45 + k * 0.22, 0, (k % 2) * 0.12 - 0.06)))
        for x in (-0.55, 0.55):                                                # iron bands
            m.add(box(0.06, 0.64, 0.74, iron(cx), "paint", y0=0).xf((x, 0, 0)))
        rim = mix(st, cx.c("stone_hi"), 0.3)
        m.add(box(1.44, 0.07, 0.1, rim, "stone", y0=0.62).xf((0, 0, 0.33))); m.add(box(1.44, 0.07, 0.1, rim, "stone", y0=0.62).xf((0, 0, -0.33)))
        m.add(box(0.1, 0.07, 0.76, rim, "stone", y0=0.62).xf((0.67, 0, 0))); m.add(box(0.1, 0.07, 0.76, rim, "stone", y0=0.62).xf((-0.67, 0, 0)))
        m.add(beam([0.5, 0.68, -0.1], [0.85, 1.15, -0.2], 0.03, iron(cx), "paint"))     # tongs resting in it
        pc.markers["lamps"].append([0, 0.8, 0.3]); pc.markers["lamp_color"] = COLD; pc.markers["lamp_fixed"] = 0.45; pc.markers["lamp_range"] = 4.0
        pc.mesh = m.ao(0, 0.8, 0.15)
        pc.blockers.append([-0.72, -0.38, 0.72, 0.38])
        pc.size = [1.45, 0.7, 0.76]
        return pc

    def tool_rack(cx):
        pc = Piece("tool_rack"); m = Mesh()
        for x in (-0.6, 0.6):
            m.add(box(0.08, 1.7, 0.08, cx.c("timber"), "timber", y0=0).xf((x, 0, 0)))
        for y in (1.6, 0.95):
            m.add(box(1.3, 0.07, 0.08, cx.c("timber_hi"), "timber", y0=y))
        ir = iron(cx)
        for k, x in enumerate((-0.45, -0.22, 0.02, 0.25, 0.47)):
            if k % 2 == 0:                                                     # hammers
                m.add(beam([x, 1.6, 0.06], [x, 1.18, 0.06], 0.03, cx.c("timber_lo"), "timber"))
                m.add(box(0.14, 0.06, 0.06, ir, "paint", y0=1.12).xf((x, 0, 0.06)))
            else:                                                              # tongs
                m.add(beam([x - 0.02, 1.6, 0.06], [x - 0.04, 1.05, 0.06], 0.02, ir, "paint"))
                m.add(beam([x + 0.02, 1.6, 0.06], [x + 0.04, 1.05, 0.06], 0.02, ir, "paint"))
        m.add(box(0.05, 0.4, 0.02, mix(ir, cx.c("stone_hi"), 0.3), "paint", y0=0.5).xf((-0.3, 0, 0.06)))   # file
        pc.mesh = m.ao(0, 1.7, 0.12)
        pc.blockers.append([-0.65, -0.1, 0.65, 0.1])
        pc.size = [1.3, 1.7, 0.2]
        return pc

    def grindstone(cx):
        pc = Piece("grindstone"); m = Mesh()
        for x in (-0.3, 0.3):
            m.add(box(0.08, 0.75, 0.08, cx.c("timber"), "timber", y0=0).xf((x, 0, 0)))
        m.add(box(0.7, 0.07, 0.5, cx.c("timber_lo"), "timber", y0=0.1))
        m.add(cylinder(0.32, 0.32, 0.12, 14, mix(cx.c("plaster_lo"), cx.c("roof_lo"), 0.2), "stone", y0=0).xf((0, 0, 0), rot=(0, 0, PI / 2)).xf((0.06, 0.78, 0)))
        m.add(beam([-0.34, 0.78, 0], [0.34, 0.78, 0], 0.04, iron(cx), "paint"))
        m.add(beam([0.34, 0.78, 0], [0.34, 0.6, 0.12], 0.03, iron(cx), "paint"))
        m.add(cylinder(0.1, 0.08, 0.16, 8, cx.c("timber"), "timber", y0=0.17).xf((-0.15, 0, 0.18)))  # drip bucket
        pc.mesh = m.ao(0, 1.1, 0.12)
        pc.blockers.append([-0.35, -0.25, 0.35, 0.25])
        pc.size = [0.75, 1.1, 0.6]
        return pc

    def coal_bin(cx):
        pc = Piece("coal_bin"); r = K.rng(cx.seed, "coal"); m = Mesh()
        m.add(box(0.8, 0.5, 0.55, cx.c("timber"), "timber", y0=0))
        m.add(box(0.84, 0.05, 0.59, cx.c("timber_hi"), "timber", y0=0.48))
        for k in range(14):
            m.add(sphere(r.uniform(0.06, 0.1), 5, 3, mix(cx.c("ink"), cx.c("stone_lo"), r.uniform(0, 0.3)), "stone").xf((r.uniform(-0.3, 0.3), 0.5 + r.uniform(0, 0.08), r.uniform(-0.2, 0.2))))
        for k in range(3):
            m.add(sphere(0.04, 4, 2, (RED_HI, GOLD, RED)[k], "glow").xf((-0.15 + k * 0.15, 0.6, 0.05 * k)))
        pc.markers["lamps"].append([0, 0.7, 0.1]); pc.markers["lamp_color"] = RED; pc.markers["lamp_fixed"] = 0.1; pc.markers["lamp_range"] = 1.2
        pc.mesh = m.ao(0, 0.7, 0.12)
        pc.blockers.append([-0.4, -0.28, 0.4, 0.28])
        pc.size = [0.84, 0.66, 0.59]
        return pc

    def forge_sign(cx):
        pc = Piece("forge_sign"); m = Mesh()
        ir = iron(cx)
        m.add(box(0.12, 2.6, 0.12, cx.c("timber"), "timber", y0=0))
        m.add(beam([0, 2.5, 0], [0.9, 2.5, 0], 0.05, ir, "paint"))
        m.add(beam([0, 2.2, 0], [0.5, 2.5, 0], 0.03, ir, "paint"))
        for x in (0.3, 0.8):
            m.add(beam([x, 2.5, 0], [x, 2.35, 0], 0.015, ir, "paint"))
        m.add(box(0.7, 0.45, 0.05, cx.c("timber_hi"), "timber", y0=1.9).xf((0.55, 0, 0)))
        m.add(box(0.66, 0.41, 0.01, cx.c("roof_lo"), "paint", y0=1.92).xf((0.55, 0, 0.03)))
        m.add(box(0.36, 0.06, 0.01, ir, "paint", y0=2.12).xf((0.55, 0, 0.04)))     # painted anvil emblem
        m.add(box(0.12, 0.08, 0.01, ir, "paint", y0=2.04).xf((0.55, 0, 0.04)))
        m.add(box(0.22, 0.04, 0.01, ir, "paint", y0=2.0).xf((0.55, 0, 0.04)))
        m.add(box(0.1, 0.03, 0.01, RED_HI, "glow", y0=2.19).xf((0.6, 0, 0.045)))   # a glowing hot bar on the emblem
        pc.mesh = m.ao(0, 2.6, 0.1)
        pc.blockers.append([-0.1, -0.1, 0.1, 0.1])
        pc.size = [1.0, 2.6, 0.2]
        return pc

    return {"forge_anvil": forge_anvil, "forge_hearth": forge_hearth, "quench_tank": quench_tank, "tool_rack": tool_rack,
            "grindstone": grindstone, "coal_bin": coal_bin, "forge_sign": forge_sign}
