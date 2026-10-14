"""Ravenhold Old Temple pieces for hd2d kit (original; Hearthmoor Art seat staging, 2026-10-05).

riftgate_arch            the Old Temple Rift-gate: a grand arch of white temple stone gone grey (3-step plinth, fluted
                         pillars, voussoir ring, faceless-mask keystone, orb finials). `rift` marker in the opening.
riftgate_glow_lit        its LIT state (glow pixels only, place at the same pos): neon-blue cold-fire rune rim, rune
                         ticks on the pillars, keystone crystal, plinth sigil, two cold-fire tongues at the feet.
riftgate_glow_dormant    its DORMANT state: the same rim as cooled dark stone runes with four faint cold embers.
temple_brazier_cold      the sacred cold-fire brazier (stone pedestal, bowl, tall neon-blue tongues). lamp marker.
temple_brazier_out       the same brazier gone out (ash, a last ember): The Cold Altar quest state.
faceless_statue          an angel statue of the old Rift order: folded wings, robe, a smooth faceless mask with a gold rim.
stained_window           a tall lancet window wall panel with violet / gold / blue glass (self-lit at dusk & night).
temple_column            a freestanding temple column, the top broken off, moss at the foot.

Drop-in: copy to tools/kit/ and add to kit.py like kit_harbor:
    import kit_old_temple as _ot; PROPS.update(_ot.pieces(__import__('types').SimpleNamespace(**globals())))
Biome palette + shared mesh helpers. Off-palette colours are only the NEON / cold-fire accents on the self-lit
'glow' material (style lock: glow pixels only, no bloom)."""
from __future__ import annotations

import math

PI = math.pi
COLD, COLD_HI, COLD_LO = "#5ab4f0", "#d8f4ff", "#2a6cb0"         # cold fire (kit_harbor / kit_bifrost)
NB, NB_HI, NB_LO = "#2ab4ff", "#a6ecff", "#1c62d8"               # neon blue
VIOLET, VIOLET_HI, VIOLET_LO = "#a45cf0", "#d4a8ff", "#6a34b8"   # neon violet (stained glass)

CY, R0, R1 = 2.55, 0.95, 1.62     # opening x -0.95..0.95, y 0.40..3.50: a 48 px gamefx vortex (2.67 m) fits it
PLINTH = 0.40


def pieces(K):
    box, cylinder, sphere, mix, Piece, W_, Mesh = K.box, K.cylinder, K.sphere, K.mix, K.Piece, K.W_, K.Mesh

    def tstone(cx, t=0.0):
        """white temple stone gone grey: plaster_hi pulled toward stone, a breath of cloth blue for the gloom"""
        return mix(mix(cx.c("plaster_hi"), cx.c("stone"), 0.5 + t), cx.c("cloth"), 0.14)

    # ------------------------------------------------------------------ the gate
    def riftgate_arch(cx):
        pc = Piece("riftgate_arch"); r = K.rng(cx.seed, "riftgate_arch"); m = Mesh()
        st = tstone(cx)
        # (pillars built in local space then moved: base, shaft with flutes, capital)
        m2 = Mesh()
        for sx in (-1, 1):
            px = sx * (R0 + 0.42)
            p = Mesh()
            p.add(box(0.98, 0.32, 0.98, mix(st, cx.c("stone_lo"), 0.2), "stone", y0=PLINTH))
            shaft_h = CY - PLINTH - 0.32 - 0.22
            p.add(box(0.8, shaft_h, 0.8, st, "stone", y0=PLINTH + 0.32))
            for fx in (-0.24, -0.08, 0.08, 0.24):                                      # flutes on the front and back
                for fz in (0.405, -0.405):
                    p.add(box(0.06, shaft_h - 0.2, 0.02, mix(st, cx.c("shadow"), 0.35), "paint", y0=PLINTH + 0.42).xf((fx, 0, fz)))
            p.add(box(1.02, 0.22, 1.02, mix(st, cx.c("stone_hi"), 0.25), "stone", y0=CY - 0.22))       # capital
            p.add(box(0.9, 0.06, 0.9, mix(st, cx.c("shadow"), 0.2), "stone", y0=CY - 0.28))
            m2.add(p.xf((px, 0, 0)))
        m = Mesh()
        for k, (w, d) in enumerate(((5.2, 2.4), (4.6, 2.05), (4.0, 1.7))):          # three broad steps
            m.add(box(w, 0.14, d, mix(st, cx.c("stone_lo"), 0.28 - k * 0.09), "stone", y0=k * 0.135))
        m.add(box(4.0, 0.02, 1.72, mix(st, cx.c("moss"), 0.35), "paint", y0=PLINTH - 0.01))   # worn moss seam
        m.add(m2)
        n = 13
        for i in range(n):                                                             # voussoir ring
            a0, a1 = PI * i / n, PI * (i + 1) / n
            am = (a0 + a1) / 2
            ln = (R0 + R1) / 2 * (a1 - a0) * 0.95
            col = mix(st, cx.c("stone_hi" if i % 2 else "stone_lo"), 0.18 + r.uniform(0, 0.08))
            m.add(box(ln, R1 - R0, 0.78, col, "stone").xf((math.cos(am) * (R0 + R1) / 2, CY + math.sin(am) * (R0 + R1) / 2, 0), rot=(0, 0, am - PI / 2)))
        for sx in (-1, 1):                                                             # spandrels: fill ring -> cornice
            m.add(box(0.62, R1 + 0.36, 0.7, mix(st, cx.c("stone_lo"), 0.12), "stone", y0=CY).xf((sx * (R1 + 0.1), 0, -0.02)))
            m.add(box(0.7, 0.7, 0.7, mix(st, cx.c("stone_lo"), 0.16), "stone", y0=CY + R1 * 0.62).xf((sx * R1 * 0.8, 0, -0.02)))
            m.add(box(0.9, 0.5, 0.7, mix(st, cx.c("stone_lo"), 0.1), "stone", y0=CY + R1 - 0.14).xf((sx * 0.75, 0, -0.02)))
        # keystone with a faceless mask relief (smooth oval, gold rim, no features)
        m.add(box(0.62, 0.78, 0.92, mix(st, cx.c("stone_hi"), 0.3), "stone", y0=CY + R1 - 0.42))
        m.add(sphere(0.2, 8, 5, cx.c("plaster_hi"), squash=(0.85, 1.1, 0.45)).xf((0, CY + R1 - 0.02, 0.47)))
        m.add(cylinder(0.22, 0.22, 0.03, 10, cx.c("flower_gold"), "paint", y0=0).xf((0, CY + R1 - 0.02, 0.43), rot=(PI / 2, 0, 0)))
        # cornice over the arch and orb finials on the haunches
        m.add(box(4.1, 0.16, 0.9, mix(st, cx.c("stone_hi"), 0.2), "stone", y0=CY + R1 + 0.36))
        m.add(box(3.7, 0.1, 0.8, mix(st, cx.c("shadow"), 0.25), "stone", y0=CY + R1 + 0.3))
        for sx in (-1, 1):
            m.add(cylinder(0.16, 0.2, 0.3, 8, st, "stone", y0=CY + R1 + 0.52).xf((sx * 1.7, 0, 0)))
            m.add(sphere(0.24, 8, 5, mix(st, cx.c("stone_hi"), 0.3), "stone").xf((sx * 1.7, CY + R1 + 1.0, 0)))
        # ivy / moss creeping on the left pillar and ring (age)
        for k in range(10):
            y = PLINTH + 0.4 + k * 0.28
            m.add(sphere(0.09 + 0.03 * (k % 3), 5, 3, cx.c("moss" if k % 2 else "leaf_deep"), squash=(1, 0.7, 0.5)).xf((-(R0 + 0.82), y, 0.3 - (k % 3) * 0.2)))
        for k in range(5):
            a = PI * (0.62 + k * 0.07)
            m.add(sphere(0.1, 5, 3, cx.c("moss"), squash=(1, 0.6, 0.6)).xf((math.cos(a) * (R1 + 0.03), CY + math.sin(a) * (R1 + 0.03), 0.3)))
        pc.mesh = m.ao(0, 5.0, 0.22)
        pc.markers["rift"] = [[0, PLINTH, 0.0]]
        pc.blockers += [[-(R0 + 0.92), -0.5, -(R0 - 0.0), 0.5], [R0 - 0.0, -0.5, R0 + 0.92, 0.5]]
        pc.size = [5.2, round(CY + R1 + 1.24, 2), 2.4]
        return pc

    def gate_glow(cx, name, lit):
        """the gate's state as glow pixels: lit = neon-blue cold fire, dormant = cooled stone runes + 4 faint embers"""
        pc = Piece(name); r = K.rng(cx.seed, name); m = Mesh()
        zf = 0.41
        if lit:
            lo, mid, hi, mat = NB_LO, NB, NB_HI, "glow"
        else:
            lo, mid, hi, mat = mix(cx.c("shadow"), cx.c("cloth"), 0.3), cx.c("stone_lo"), cx.c("stone_lo"), "paint"
        n = 26
        for i in range(n):                                     # jagged rim along the inner edge of the ring
            a = PI * (i + 0.5) / n
            t = 0.11 if i % 2 else 0.2
            col = (hi if i % 6 == 3 else mid) if lit else (lo if i % 2 else mid)
            x, y = math.cos(a) * (R0 + t / 2 - 0.02), CY + math.sin(a) * (R0 + t / 2 - 0.02)
            m.add(box(0.12, t, 0.05, col, mat).xf((x, y, zf), rot=(0, 0, a - PI / 2)))
        for sx in (-1, 1):                                     # pillar inner edges + rune ticks on the pillar fronts
            for k in range(10):
                y = PLINTH + 0.25 + k * 0.21
                t = 0.18 if k % 2 else 0.1
                m.add(box(t, 0.12, 0.05, mid if (k % 4) else hi, mat, y0=y).xf((sx * (R0 + t / 2 - 0.02), 0, zf)))
            px = sx * (R0 + 0.42)
            for k, (gx, gy, w, h) in enumerate(((0, 1.2, 0.06, 0.42), (-0.1, 1.42, 0.2, 0.05), (0.09, 1.12, 0.05, 0.16),
                                               (0, 1.85, 0.06, 0.3), (0.08, 1.98, 0.14, 0.05))):
                m.add(box(w, h, 0.03, hi if k == 0 and lit else mid, mat, y0=PLINTH + gy).xf((px + gx, 0, 0.415)))
        # keystone crystal under the mask, plinth sigil on the top step riser
        m.add(sphere(0.12, 6, 4, hi if lit else lo, mat, squash=(0.8, 1.3, 0.6)).xf((0, CY + R1 - 0.42, 0.48)))
        for (x0, y0, x1, y1) in ((-0.3, 0, 0, 0.22), (0.3, 0, 0, 0.22), (-0.18, 0.11, 0.18, 0.11), (0, 0.22, 0, 0.36)):
            ln = math.hypot(x1 - x0, y1 - y0); a = math.atan2(y1 - y0, x1 - x0)
            m.add(box(ln + 0.04, 0.035, 0.03, mid, mat).xf(((x0 + x1) / 2, 0.29 + (y0 + y1) / 2 * 0.5 + 0.0, 0.86), rot=(0, 0, a)))
        if lit:
            for sx in (-1, 1):                                 # two cold-fire tongues at the pillar feet
                for k, (h, rr, col) in enumerate(((0.62, 0.17, NB_LO), (0.5, 0.12, NB), (0.32, 0.06, NB_HI))):
                    m.add(cylinder(rr, 0.0, h, 6, col, "glow", caps=False, y0=PLINTH + 0.32).xf((sx * (R0 + 0.42), 0, 0.62)))
            pc.markers["lamps"] += [[0, 1.9, 0.6], [-(R0 + 0.42), 0.9, 0.7], [R0 + 0.42, 0.9, 0.7]]
            pc.markers["lamp_color"] = NB; pc.markers["lamp_fixed"] = 0.8; pc.markers["lamp_range"] = 7.0
        else:
            for (x, y) in ((-(R0 + 0.05), PLINTH + 0.9), (R0 + 0.05, PLINTH + 1.6), (math.cos(1.1) * R0, CY + math.sin(1.1) * R0), (0, CY + R1 - 0.42)):
                m.add(box(0.05, 0.05, 0.05, COLD_LO, "glow").xf((x, y, zf + 0.02)))
            pc.markers["lamps"] += [[0, 1.6, 0.6]]
            pc.markers["lamp_color"] = COLD_LO; pc.markers["lamp_fixed"] = 0.12; pc.markers["lamp_range"] = 2.5
        pc.mesh = m
        pc.size = [2 * (R0 + 0.9), CY + R1, 0.9]
        return pc

    # ------------------------------------------------------------------ braziers
    def brazier(cx, name, lit):
        pc = Piece(name); r = K.rng(cx.seed, name); m = Mesh()
        st = tstone(cx)
        m.add(box(0.7, 0.14, 0.7, mix(st, cx.c("stone_lo"), 0.3), "stone", y0=0))
        m.add(cylinder(0.2, 0.16, 0.7, 8, st, "stone", y0=0.14, col_top=mix(st, cx.c("stone_hi"), 0.2)))
        for k in range(4):                                     # four fluted ribs
            a = k * PI / 2 + PI / 4
            m.add(box(0.05, 0.62, 0.05, mix(st, cx.c("shadow"), 0.3), "paint", y0=0.18).xf((math.cos(a) * 0.19, 0, math.sin(a) * 0.19)))
        m.add(cylinder(0.24, 0.46, 0.26, 10, mix(st, cx.c("stone_hi"), 0.15), "stone", y0=0.84))    # the bowl
        m.add(cylinder(0.47, 0.47, 0.04, 10, cx.c("flower_gold"), "paint", y0=1.1))                 # a gold lip band
        if lit:
            m.add(cylinder(0.4, 0.4, 0.03, 10, NB_LO, "glow", y0=1.1))
            for k, (h, rr, col, ox, oz) in enumerate(((1.05, 0.3, COLD_LO, 0, 0), (0.85, 0.22, NB, 0.08, 0.04), (0.72, 0.16, NB, -0.12, -0.05),
                                                     (0.55, 0.11, COLD_HI, 0.0, 0.06), (0.4, 0.07, "#ffffff", 0.02, 0.1))):
                m.add(cylinder(rr, 0.0, h, 6, col, "glow", caps=False, y0=1.12).xf((ox, 0, oz)))
            pc.markers["lamps"].append([0, 1.6, 0.0]); pc.markers["lamp_color"] = NB
            pc.markers["lamp_fixed"] = 0.85; pc.markers["lamp_range"] = 5.5
        else:
            m.add(sphere(0.38, 8, 3, mix(cx.c("stone_lo"), cx.c("shadow"), 0.5), squash=(1, 0.22, 1)).xf((0, 1.1, 0)))   # cold ash
            m.add(box(0.06, 0.04, 0.06, COLD_LO, "glow", y0=1.16).xf((0.08, 0, 0.1)))                                     # one last ember
        pc.mesh = m.ao(0, 1.1, 0.18)
        pc.blockers.append([-0.3, -0.3, 0.3, 0.3])
        pc.size = [0.94, 2.2 if lit else 1.2, 0.94]
        return pc

    # ------------------------------------------------------------------ statue / window / column
    def faceless_statue(cx):
        pc = Piece("faceless_statue"); r = K.rng(cx.seed, "faceless_statue"); m = Mesh()
        st = tstone(cx, 0.05)
        m.add(box(0.9, 0.5, 0.9, mix(st, cx.c("stone_lo"), 0.3), "stone", y0=0))
        m.add(box(1.0, 0.08, 1.0, mix(st, cx.c("stone_hi"), 0.2), "stone", y0=0.5))
        m.add(cylinder(0.36, 0.26, 1.1, 9, st, "stone", y0=0.58))              # robe skirt
        m.add(cylinder(0.27, 0.24, 0.5, 9, mix(st, cx.c("stone_hi"), 0.12), "stone", y0=1.66))   # chest
        m.add(cylinder(0.25, 0.25, 0.06, 9, cx.c("flower_gold"), "paint", y0=1.62))              # a gilded girdle
        for k in range(5):                                                       # robe folds
            a = PI * 0.25 + k * PI * 0.125
            m.add(box(0.04, 1.0, 0.04, mix(st, cx.c("shadow"), 0.3), "paint", y0=0.6).xf((math.cos(a) * 0.33, 0, math.sin(a) * 0.33)))
        m.add(sphere(0.19, 8, 6, st).xf((0, 2.36, 0)))                          # head under a hood
        m.add(sphere(0.23, 8, 5, mix(st, cx.c("stone_lo"), 0.15), squash=(1, 1.05, 1)).xf((0, 2.4, -0.05)))
        m.add(sphere(0.14, 8, 5, cx.c("plaster_hi"), squash=(1, 1.25, 0.4)).xf((0, 2.34, 0.17)))   # the smooth faceless mask
        m.add(box(0.26, 0.025, 0.02, cx.c("flower_gold"), "paint", y0=2.47).xf((0, 0, 0.2)))        # gold brow rim
        for sx in (-1, 1):                                                       # folded wings behind the shoulders
            w = Mesh()
            for k in range(4):
                w.add(box(0.12, 1.25 - k * 0.22, 0.42 - k * 0.05, mix(st, cx.c("stone_hi" if k % 2 else "stone"), 0.2), "stone", y0=0.0).xf((k * 0.07, 0, 0)))
            m.add(w.xf((sx * 0.3, 1.18, -0.24), rot=(0.15, sx * 0.25, sx * -0.12)))
        m.add(box(0.34, 0.16, 0.18, mix(st, cx.c("stone_hi"), 0.1), "stone", y0=1.86).xf((0, 0, 0.24)))    # clasped hands
        pc.mesh = m.ao(0, 2.6, 0.2)
        pc.blockers.append([-0.45, -0.45, 0.45, 0.45])
        pc.size = [1.0, 2.65, 1.0]
        return pc

    def stained_window(cx):
        pc = Piece("stained_window"); r = K.rng(cx.seed, "stained_window"); m = Mesh()
        st = tstone(cx)
        m.add(box(1.8, 3.6, 0.5, mix(st, cx.c("stone_lo"), 0.2), "stone", y0=0))                # wall slab
        m.add(box(1.96, 0.16, 0.6, mix(st, cx.c("stone_hi"), 0.2), "stone", y0=3.6))
        glass = [VIOLET, cx.c("flower_gold"), NB, VIOLET_HI, cx.c("lamp"), VIOLET_LO, COLD]
        for gy in range(9):                                                                   # lancet: rect + pointed top
            for gx in range(4):
                y = 0.9 + gy * 0.22
                x = -0.39 + gx * 0.26
                top = 0.9 + 9 * 0.22
                if gy >= 7 and abs(x) > 0.32 - (gy - 7) * 0.16:
                    continue
                col = glass[(gx * 3 + gy * 2 + (gx * gy) % 3) % len(glass)]
                if gx in (1, 2) and gy in (3, 4, 5):
                    col = cx.c("flower_gold") if gy != 4 else "#ffffff"                     # a gold sun rose in the middle
                m.add(box(0.22, 0.18, 0.03, col, "glow", y0=y).xf((x, 0, 0.26)))
        m.add(box(1.0, 0.05, 0.04, cx.c("ink"), "paint", y0=0.86).xf((0, 0, 0.27)))           # leading frame
        for x in (-0.52, 0.52):
            m.add(box(0.06, 2.0, 0.06, cx.c("ink"), "paint", y0=0.86).xf((x, 0, 0.27)))
        m.add(box(1.1, 0.12, 0.2, mix(st, cx.c("stone_hi"), 0.25), "stone", y0=0.74).xf((0, 0, 0.3)))   # sill
        pc.markers["lamps"].append([0, 1.9, 0.6]); pc.markers["lamp_color"] = VIOLET
        pc.markers["lamp_fixed"] = 0.35; pc.markers["lamp_range"] = 4.0
        pc.markers["window_light"] = {"decals": ["glasslight_violet", "glasslight_gold"], "at": [0, 0, 1.8]}
        pc.mesh = m.ao(0, 3.6, 0.18)
        pc.blockers.append([-0.9, -0.25, 0.9, 0.25])
        pc.size = [1.96, 3.76, 0.6]
        return pc

    def temple_column(cx):
        pc = Piece("temple_column"); r = K.rng(cx.seed, "temple_column"); m = Mesh()
        st = tstone(cx)
        m.add(box(0.9, 0.24, 0.9, mix(st, cx.c("stone_lo"), 0.25), "stone", y0=0))
        m.add(cylinder(0.32, 0.3, 2.2, 10, st, "stone", y0=0.24))
        for k in range(10):
            a = k * PI / 5
            m.add(box(0.04, 2.0, 0.04, mix(st, cx.c("shadow"), 0.3), "paint", y0=0.3).xf((math.cos(a) * 0.31, 0, math.sin(a) * 0.31)))
        for k in range(6):                                                # the broken top: jagged chunks
            a = k * PI / 3 + 0.3
            h = 0.1 + 0.18 * ((k * 7) % 3) / 2
            m.add(box(0.22, h, 0.22, mix(st, cx.c("stone_hi"), 0.1), "stone", y0=2.44).xf((math.cos(a) * 0.17, 0, math.sin(a) * 0.17), rot=(0, a, 0)))
        m.add(sphere(0.5, 8, 3, cx.c("moss"), squash=(1, 0.22, 1)).xf((0, 0.12, 0)))
        for k in range(5):
            m.add(sphere(0.12, 5, 3, cx.c("leaf_deep" if k % 2 else "moss")).xf((0.25 * math.cos(k), 0.6 + k * 0.3, 0.25 * math.sin(k))))
        pc.mesh = m.ao(0, 2.6, 0.2)
        pc.blockers.append([-0.4, -0.4, 0.4, 0.4])
        pc.size = [0.9, 2.7, 0.9]
        return pc

    return {"riftgate_arch": riftgate_arch,
            "riftgate_glow_lit": lambda cx: gate_glow(cx, "riftgate_glow_lit", True),
            "riftgate_glow_dormant": lambda cx: gate_glow(cx, "riftgate_glow_dormant", False),
            "temple_brazier_cold": lambda cx: brazier(cx, "temple_brazier_cold", True),
            "temple_brazier_out": lambda cx: brazier(cx, "temple_brazier_out", False),
            "faceless_statue": faceless_statue, "stained_window": stained_window, "temple_column": temple_column}
