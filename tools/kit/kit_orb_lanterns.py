"""Water orb lanterns with glowing fish (original; Hearthmoor Art seat staging, 2026-10-05). Placeable in a house or garden.

Four mounts x three fish colours (blue / violet / red) = 12 pieces, named orb_<mount>_<colour>:
  orb_table_*     a 0.34 m orb on a turned wooden base (tables, shelves, windowsills)        ~0.48 m tall
  orb_hanging_*   a 0.40 m orb in an iron cage-ring on a chain from a ceiling hook at 2.6 m   (hangs, no blocker)
  orb_standing_*  a 0.46 m orb on an iron floor stand with a tripod foot (house corners)      ~1.75 m tall
  orb_garden_*    a 0.60 m orb on a mossy stone post with a copper collar (garden, paths)     ~1.65 m tall
plus orb_grand (a 1.1 m showpiece orb on a stone basin with all three fish colours, for a garden centre or plaza).
The water is self-lit 'glow' (deep, dim), the fish are bright neon glow, a white glass highlight sits on top. The
animated fish swim in the matching gamefx billboard (orb_fx_24 / orb_fx_32): the kit fish are the static fallback.

Drop-in: copy to tools/kit/ and add to kit.py like kit_harbor:
    import kit_orb_lanterns as _ol; PROPS.update(_ol.pieces(__import__('types').SimpleNamespace(**globals())))
Neon hexes only on the 'glow' material (water + fish), per Bill 2026-10-05 (glowing water / fish may be neon)."""
from __future__ import annotations

import math

PI = math.pi
FISH = {   # colour: (fish, fish_hi, fish_lo, water, water_core, light) - glowing sea water lightly tinted by its fish
    "blue": ("#2ab4ff", "#a6ecff", "#1c62d8", "#1c62d8", "#5ab4f0", "#2ab4ff"),
    "violet": ("#a45cf0", "#d4a8ff", "#6a34b8", "#4a3aa8", "#7a6ad8", "#a45cf0"),
    "red": ("#ff5a4a", "#ffb0a0", "#a81c22", "#6a2a7a", "#a04a8a", "#ff5a4a"),
}
GLASS_HI = "#e8f6ff"


def pieces(K):
    box, cylinder, sphere, beam, mix, Piece, W_, Mesh = K.box, K.cylinder, K.sphere, K.beam, K.mix, K.Piece, K.W_, K.Mesh

    def orb(m, cy, R, colour, nfish=3, r=None, extra=None):
        """the water orb: deep glowing water, a lighter inner core, fish on the camera-facing half, glass highlight, bubbles"""
        f, fhi, flo, w, whi, _ = FISH[colour]
        m.add(sphere(R, 12, 8, w, "glow", col_bottom=mix(w, "#0a0c18", 0.3)).xf((0, cy, 0)))
        m.add(sphere(R * 0.7, 8, 5, whi, "glow").xf((0, cy - R * 0.05, R * 0.25)))
        cols = extra or [colour] * nfish
        for k, c in enumerate(cols):
            ff, ffhi, fflo = FISH[c][:3]
            a = -0.9 + k * (1.8 / max(1, len(cols) - 1)) if len(cols) > 1 else 0
            fy = cy + (0.25 - 0.25 * k) * R
            fx, fz = math.sin(a) * R * 0.55, math.cos(a) * R * 0.8
            L = R * 0.36
            d = 1 if k % 2 == 0 else -1
            m.add(sphere(L * 0.5, 6, 4, ffhi, "glow", squash=(1.0, 0.55, 0.45)).xf((fx, fy, fz)))               # body
            m.add(sphere(L * 0.2, 4, 3, W_, "glow").xf((fx + d * L * 0.25, fy + L * 0.08, fz + 0.01)))            # head glint
            m.add(box(L * 0.3, L * 0.5, 0.02, ff, "glow", y0=fy - L * 0.25).xf((fx - d * L * 0.6, 0, fz)))        # tail
        m.add(sphere(R * 0.28, 6, 4, GLASS_HI, "glow", squash=(1, 0.55, 0.6)).xf((-R * 0.35, cy + R * 0.55, R * 0.55)))   # glass glint
        for k in range(3):
            m.add(sphere(R * 0.06, 4, 2, W_, "glow").xf((R * (0.3 - k * 0.12), cy + R * (-0.2 + k * 0.28), R * 0.78)))

    def lamp(pc, colour, y, rng=4.0, fixed=0.45):
        pc.markers["lamps"].append([0, y, 0.1]); pc.markers["lamp_color"] = FISH[colour][5]
        pc.markers["lamp_fixed"] = fixed; pc.markers["lamp_range"] = rng

    def table(colour):
        def fn(cx):
            pc = Piece(f"orb_table_{colour}"); m = Mesh()
            m.add(cylinder(0.16, 0.18, 0.05, 10, cx.c("timber_lo"), "timber", y0=0))
            m.add(cylinder(0.11, 0.14, 0.06, 10, cx.c("timber"), "timber", y0=0.05, col_top=cx.c("timber_hi")))
            m.add(cylinder(0.13, 0.09, 0.03, 10, cx.c("flower_gold"), "paint", y0=0.11))       # brass cup
            R = 0.17
            orb(m, 0.13 + R, R, colour, 2)
            lamp(pc, colour, 0.3, 3.0, 0.4)
            pc.mesh = m.ao(0, 0.5, 0.12)
            pc.size = [0.36, 0.48, 0.36]
            pc.blockers.append([-0.15, -0.15, 0.15, 0.15])
            return pc
        return fn

    def hanging(colour):
        def fn(cx):
            pc = Piece(f"orb_hanging_{colour}"); m = Mesh()
            R, cy = 0.2, 1.75
            iron = cx.c("shadow")
            m.add(box(0.18, 0.04, 0.18, iron, "paint", y0=2.58))                                 # ceiling plate / hook
            for k in range(8):                                                                # chain links
                y = 2.56 - k * 0.07
                m.add(box(0.03 if k % 2 else 0.05, 0.06, 0.05 if k % 2 else 0.03, iron, "paint", y0=y - 0.06))
            m.add(cylinder(0.1, 0.13, 0.05, 8, cx.c("flower_gold"), "paint", y0=cy + R - 0.02))  # brass cap
            for k in range(4):                                                                # cage ribs
                a = k * PI / 2 + PI / 4
                m.add(beam([math.cos(a) * 0.02, cy + R, math.sin(a) * 0.02], [math.cos(a) * (R + 0.02), cy, math.sin(a) * (R + 0.02)], 0.02, iron, "paint"))
                m.add(beam([math.cos(a) * (R + 0.02), cy, math.sin(a) * (R + 0.02)], [math.cos(a) * 0.05, cy - R - 0.03, math.sin(a) * 0.05], 0.02, iron, "paint"))
            m.add(cylinder(R + 0.03, R + 0.03, 0.025, 14, cx.c("flower_gold"), "paint", y0=cy - 0.012))   # equator ring
            orb(m, cy, R, colour, 3)
            m.add(sphere(0.035, 4, 3, cx.c("flower_gold")).xf((0, cy - R - 0.06, 0)))           # drip finial
            lamp(pc, colour, cy, 4.0, 0.45)
            pc.mesh = m
            pc.size = [0.48, 2.62, 0.48]
            return pc
        return fn

    def standing(colour):
        def fn(cx):
            pc = Piece(f"orb_standing_{colour}"); m = Mesh()
            iron = cx.c("shadow")
            for k in range(3):                                                                # tripod foot
                a = k * 2 * PI / 3
                m.add(beam([0, 0.2, 0], [math.cos(a) * 0.26, 0.0, math.sin(a) * 0.26], 0.04, iron, "paint"))
            m.add(cylinder(0.035, 0.03, 1.08, 6, iron, "paint", y0=0.18))
            m.add(cylinder(0.06, 0.06, 0.04, 8, cx.c("flower_gold"), "paint", y0=0.7))          # brass knop
            m.add(cylinder(0.17, 0.24, 0.08, 10, iron, "paint", y0=1.24))                       # cup
            m.add(cylinder(0.24, 0.24, 0.02, 12, cx.c("flower_gold"), "paint", y0=1.32))
            R = 0.23
            orb(m, 1.3 + R, R, colour, 3)
            m.add(box(0.1, 0.06, 0.1, iron, "paint", y0=1.3 + 2 * R - 0.02))
            lamp(pc, colour, 1.3 + R, 4.5, 0.45)
            pc.mesh = m.ao(0, 1.8, 0.12)
            pc.size = [0.6, 1.8, 0.6]
            pc.blockers.append([-0.22, -0.22, 0.22, 0.22])
            return pc
        return fn

    def garden(colour):
        def fn(cx):
            pc = Piece(f"orb_garden_{colour}"); r = K.rng(cx.seed, f"og{colour}"); m = Mesh()
            st = mix(W_, cx.c("stone"), 0.25)
            m.add(box(0.5, 0.12, 0.5, mix(st, cx.c("stone_lo"), 0.3), "stone", y0=0))
            m.add(box(0.34, 0.8, 0.34, st, "stone", y0=0.12))
            m.add(box(0.44, 0.1, 0.44, mix(st, cx.c("stone_hi"), 0.3), "stone", y0=0.92))
            m.add(sphere(0.2, 6, 3, cx.c("moss"), squash=(1.3, 0.35, 1.1)).xf((0.12, 0.95, 0.12)))
            m.add(sphere(0.22, 6, 3, cx.c("moss"), squash=(1.4, 0.3, 1.2)).xf((-0.15, 0.08, 0.2)))
            m.add(cylinder(0.2, 0.24, 0.08, 10, mix(cx.c("roof"), cx.c("leaf_deep"), 0.35), "paint", y0=1.02))   # verdigris copper collar
            R = 0.3
            orb(m, 1.04 + R, R, colour, 3)
            lamp(pc, colour, 1.04 + R, 5.0, 0.5)
            pc.mesh = m.ao(0, 1.7, 0.15)
            pc.size = [0.6, 1.65, 0.6]
            pc.blockers.append([-0.25, -0.25, 0.25, 0.25])
            return pc
        return fn

    def orb_grand(cx):
        """the showpiece: a 1.1 m orb on a round stone basin, all three fish colours swimming together"""
        pc = Piece("orb_grand"); m = Mesh()
        st = mix(W_, cx.c("stone"), 0.25)
        m.add(cylinder(0.8, 0.9, 0.2, 14, mix(st, cx.c("stone_lo"), 0.3), "stone", y0=0))
        m.add(cylinder(0.42, 0.55, 0.5, 12, st, "stone", y0=0.2))
        m.add(cylinder(0.62, 0.5, 0.14, 14, mix(st, cx.c("stone_hi"), 0.3), "stone", y0=0.7))
        m.add(cylinder(0.56, 0.56, 0.03, 14, "#2ab4ff", "glow", y0=0.8))                    # water in the basin lip
        R = 0.55
        orb(m, 0.82 + R, R, "blue", extra=["blue", "violet", "red", "violet", "blue"])
        for k in range(6):
            a = k * PI / 3
            m.add(sphere(0.12, 5, 3, cx.c("moss"), squash=(1.4, 0.4, 1)).xf((math.cos(a) * 0.82, 0.2, math.sin(a) * 0.82)))
        pc.markers["lamps"].append([0, 0.82 + R, 0.2]); pc.markers["lamp_color"] = "#7a8cff"
        pc.markers["lamp_fixed"] = 0.6; pc.markers["lamp_range"] = 7.0
        pc.mesh = m.ao(0, 2.0, 0.15)
        pc.size = [1.8, 1.95, 1.8]
        pc.blockers.append([-0.85, -0.85, 0.85, 0.85])
        return pc

    out = {}
    for c in FISH:
        out[f"orb_table_{c}"] = table(c)
        out[f"orb_hanging_{c}"] = hanging(c)
        out[f"orb_standing_{c}"] = standing(c)
        out[f"orb_garden_{c}"] = garden(c)
    out["orb_grand"] = orb_grand
    return out
