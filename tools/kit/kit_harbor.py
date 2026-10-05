"""Ravenhold Harbor pieces for hd2d kit (original, Hearthmoor Stage 5 part 4): harbor_water (dark harbour water with
faint swell lines), pier (a plank jetty on posts, its deck at y=0), rowboat and skiff (moored boats; the skiff has a
mast, a furled sail and a cold-fire stern lamp), pier_lantern / quay_lantern (iron posts with neon-blue cold-fire
lanterns and their broken reflections on the water below), bollard, waystone (a carved standing stone with glowing
runes) and district_gate (a stone arch with barred oak doors: Ravenhold's sealed districts).
Imported by kit.py; biome palette + the shared mesh helpers. The only off-palette colours are the cold-fire glow
pixels (style lock: neon accents only for glowing effect pixels), on the self-lit 'glow' material, no bloom."""
from __future__ import annotations

import math

PI = math.pi
COLD, COLD_HI, COLD_LO = "#5ab4f0", "#d8f4ff", "#2a6cb0"   # Sefa's cold-fire blue (glow pixels only)
VIOLET, VIOLET_HI, VIOLET_LO = "#a45cf0", "#e2c4ff", "#5a2c9a"   # the Rift's violet (Embassies glow)
RED, RED_HI, RED_LO = "#e0302a", "#ffb4a0", "#8a1c1c"            # Corsair red
ORB, ORB_HI = "#2a8ca8", "#7ad8e8"                              # sea-glass orb water


def pieces(K):
    box, cylinder, sphere, mix, Piece, W_, Mesh = K.box, K.cylinder, K.sphere, K.mix, K.Piece, K.W_, K.Mesh

    def water_col(cx, t=0.0):
        """night harbour water: the biome's deep cloth blue pulled toward ink (palette mix, not a new colour)"""
        return mix(mix(cx.c("cloth"), cx.c("ink"), 0.5), cx.c("leaf_deep"), 0.18 + t)

    def harbor_water(cx):
        """a 64 x 34 m sheet of dark water, top at y=0.05, with faint lighter swell lines (stepped boxes, no shader)"""
        pc = Piece("harbor_water"); r = K.rng(cx.seed, "harbor_water"); m = Mesh()
        m.add(box(64, 0.05, 34, water_col(cx), "paint", y0=0.0))
        for k in range(70):
            x, z = r.uniform(-30, 30), r.uniform(-16, 16)
            m.add(box(r.uniform(0.6, 2.2), 0.008, 0.07, mix(water_col(cx), cx.c("sky"), r.uniform(0.12, 0.22)), "paint", y0=0.05).xf((x, 0, z)))
        pc.mesh = m
        pc.size = [64, 0.06, 34]
        return pc

    def pier(cx):
        """a plank jetty 2.4 m wide, 8 m long (local z -4..4), deck top at y=0, posts down 0.85 m into the water"""
        pc = Piece("pier"); r = K.rng(cx.seed, "pier"); m = Mesh()
        for i in range(20):
            z = -4 + 0.2 + i * 0.4
            m.add(box(2.4, 0.08, 0.36, mix(cx.c("timber"), cx.c("timber_hi"), r.uniform(0.0, 0.35)), "timber", y0=-0.08).xf((r.uniform(-0.03, 0.03), 0, z)))
        for sx in (-1, 1):
            m.add(box(0.14, 0.14, 8.0, cx.c("timber_lo"), "timber", y0=-0.22).xf((sx * 1.05, 0, 0)))
            for k in range(5):
                z = -3.8 + k * 1.9
                m.add(cylinder(0.12, 0.12, 1.05, 6, mix(cx.c("timber_lo"), cx.c("ink"), 0.25), "timber", y0=-0.9, col_top=cx.c("timber")).xf((sx * 1.12, 0, z)))
                m.add(cylinder(0.14, 0.14, 0.06, 6, mix(cx.c("moss"), cx.c("leaf_deep"), 0.4), "paint", y0=-0.72).xf((sx * 1.12, 0, z)))   # weed line
        # mooring cleats on the deck edge
        for sx, z in ((-1, -1.6), (1, 1.2), (-1, 2.8)):
            m.add(box(0.12, 0.1, 0.36, cx.c("shadow"), "paint", y0=0.0).xf((sx * 0.95, 0, z)))
        pc.mesh = m.ao(-0.9, 0.9, 0.18)
        pc.size = [2.4, 0.9, 8.0]
        return pc

    def hull(m, cx, L, W, H, col, rim):
        """a simple clinker hull: stacked tapering planks (wider at the top), bow toward -z"""
        for i, f in enumerate((0.55, 0.78, 0.92, 1.0)):
            y = 0.04 + i * H / 4
            m.add(box(W * f, H / 4 + 0.01, L * (0.7 + 0.3 * f), mix(col, cx.c("ink"), 0.25 - i * 0.06), "timber", y0=y))
        m.add(box(W + 0.06, 0.06, L, rim, "timber", y0=0.04 + H))
        m.add(box(W * 0.9, 0.04, L * 0.9, mix(cx.c("timber_lo"), cx.c("ink"), 0.3), "paint", y0=0.04 + H * 0.55))   # floor boards
        m.add(K.beam((0, 0.04 + H * 0.3, -L / 2 - 0.05), (0, 0.04 + H + 0.12, -L / 2 - 0.14), 0.1, rim, "timber"))   # stem post

    def rowboat(cx):
        pc = Piece("rowboat"); m = Mesh()
        hull(m, cx, 2.6, 1.1, 0.42, cx.c("roof_lo"), cx.c("timber_hi"))
        m.add(box(1.0, 0.06, 0.26, cx.c("timber"), "timber", y0=0.32))
        for sx in (-1, 1):
            m.add(K.beam((sx * 0.4, 0.42, 0.2), (sx * 1.15, 0.12, -0.6), 0.05, cx.c("timber_hi"), "timber"))   # shipped oars
        pc.mesh = m.ao(0, 0.6, 0.2)
        pc.size = [1.2, 0.6, 2.7]
        return pc

    def skiff(cx):
        """a harbour skiff: plaster-white hull with a red stripe, a mast with a furled sail, a cold-fire stern lamp"""
        pc = Piece("skiff"); m = Mesh()
        hull(m, cx, 5.0, 1.8, 0.62, cx.c("plaster"), cx.c("roof"))
        m.add(box(1.86, 0.08, 4.6, cx.c("roof"), "paint", y0=0.5))   # stripe
        m.add(cylinder(0.08, 0.06, 2.6, 6, cx.c("timber"), "timber", y0=0.3).xf((0, 0, -0.6)))
        m.add(K.beam((0, 1.0, -0.6), (0, 1.04, 1.5), 0.07, cx.c("timber"), "timber"))                      # boom
        m.add(cylinder(0.15, 0.15, 1.9, 6, cx.c("plaster_hi"), "paint", y0=0.0).xf((0, 1.15, 0.45), rot=(PI / 2, 0, 0)))   # furled sail
        m.add(box(0.6, 0.36, 0.8, cx.c("timber"), "timber", y0=0.62).xf((0, 0, 1.5)))                         # little cabin box
        m.add(box(0.7, 0.06, 0.9, cx.c("roof_lo"), "paint", y0=0.98).xf((0, 0, 1.5)))
        m.add(box(0.2, 0.22, 0.2, COLD, "glow", y0=1.04).xf((0, 0, 1.75)))                                    # cold-fire stern lamp
        m.add(box(0.1, 0.12, 0.1, COLD_HI, "glow", y0=1.09).xf((0, 0, 1.75)))
        pc.markers["lamps"].append([0, 1.16, 1.75])
        pc.markers["lamp_color"] = COLD
        pc.mesh = m.ao(0, 2.9, 0.2)
        pc.size = [1.9, 2.9, 5.1]
        return pc

    def lantern_head(m, cx, y):
        """an iron cage lantern with cold-fire panes (glow) and a white-hot core"""
        m.add(box(0.34, 0.06, 0.34, cx.c("shadow"), "paint", y0=y))
        m.add(box(0.26, 0.34, 0.26, COLD, "glow", y0=y + 0.06))
        m.add(box(0.12, 0.2, 0.12, COLD_HI, "glow", y0=y + 0.13))
        for sx in (-1, 1):
            for sz in (-1, 1):
                m.add(box(0.04, 0.36, 0.04, cx.c("ink"), "paint", y0=y + 0.05).xf((sx * 0.14, 0, sz * 0.14)))
        m.add(cylinder(0.2, 0.04, 0.14, 4, cx.c("shadow"), "paint", y0=y + 0.4).xf(rot=(0, PI / 4, 0)))

    def reflection(m, r, drop, z0=0.5, n=7, cols=(COLD_HI, COLD, COLD_LO)):
        """the lantern's broken reflection on the water below: short glow dashes on the surface (y = -drop + 0.06),
        narrowing and dimming away from the lamp toward the camera (+z). Static pixels; the lamp flicker sprite moves."""
        for k in range(n):
            z = z0 + k * 0.32 + r.uniform(-0.05, 0.05)
            w = max(0.1, 0.5 - k * 0.055) * r.uniform(0.8, 1.15)
            col = cols[0] if k == 0 else (cols[1] if k < n - 2 else cols[2])
            m.add(box(w, 0.006, 0.09, col, "glow", y0=-drop + 0.057).xf((r.uniform(-0.08, 0.08), 0, z)))

    def lantern_post(cx, name, drop, z_refl):
        pc = Piece(name); r = K.rng(cx.seed, name); m = Mesh()
        m.add(box(0.3, 0.12, 0.3, mix(W_, cx.c("stone_lo"), 0.3), "stone", y0=0))
        m.add(cylinder(0.06, 0.05, 1.7, 6, cx.c("shadow"), "paint", y0=0.1))
        m.add(K.beam((0, 1.72, 0), (0, 1.8, 0.22), 0.05, cx.c("shadow"), "paint"))
        lantern_head(m, cx, 1.42)
        reflection(m, r, drop, z_refl)
        pc.markers["lamps"].append([0, 1.6, 0])
        pc.markers["lamp_color"] = COLD
        pc.markers["lamp_range"] = 8.0
        pc.markers["lamp_fixed"] = 0.55   # cold-fire burns by day too (dimmer), brighter as the lamps come up
        pc.blockers.append([-0.18, -0.18, 0.18, 0.18])
        pc.mesh = m.ao(0, 2.0, 0.15)
        pc.size = [0.4, 1.9, 0.4]
        return pc

    def pier_lantern(cx):   # on a pier deck 0.75 m above the water; reflection out past the pier's tip
        return lantern_post(cx, "pier_lantern", 0.75, 0.55)

    def quay_lantern(cx):   # on the quay coping 0.8 m above the water; reflection in front of the quay wall
        return lantern_post(cx, "quay_lantern", 0.8, 0.75)

    def bollard(cx):
        pc = Piece("bollard"); m = Mesh()
        m.add(cylinder(0.16, 0.13, 0.5, 7, cx.c("shadow"), "paint", y0=0, col_top=cx.c("stone_lo")))
        m.add(cylinder(0.22, 0.22, 0.06, 7, cx.c("shadow"), "paint", y0=0.44))
        m.add(cylinder(0.17, 0.17, 0.1, 7, cx.c("timber_hi"), "paint", y0=0.18))   # a coil of rope
        pc.blockers.append([-0.2, -0.2, 0.2, 0.2])
        pc.mesh = m.ao(0, 0.5, 0.2)
        pc.size = [0.45, 0.5, 0.45]
        return pc

    def waystone(cx):
        """a waist-high plinth and a tall carved stone with a ring of glowing cold-fire runes and a pale cap crystal"""
        pc = Piece("waystone"); r = K.rng(cx.seed, "waystone"); m = Mesh()
        st = mix(W_, cx.c("stone"), 0.25)
        m.add(cylinder(0.7, 0.78, 0.2, 8, mix(st, cx.c("stone_lo"), 0.3), "stone", y0=0))
        m.add(box(0.56, 1.5, 0.44, st, "stone", y0=0.2))
        m.add(box(0.46, 0.5, 0.36, mix(st, cx.c("stone_hi"), 0.2), "stone", y0=1.7))
        m.add(box(0.3, 0.22, 0.24, mix(st, cx.c("stone_hi"), 0.35), "stone", y0=2.2))
        for k, (y, w) in enumerate(((0.55, 0.12), (0.85, 0.2), (1.15, 0.12), (1.42, 0.16), (1.9, 0.2))):
            m.add(box(w, 0.06, 0.02, COLD if k % 2 else COLD_HI, "glow", y0=y).xf((r.uniform(-0.08, 0.08), 0, 0.23)))
            m.add(box(0.04, 0.12, 0.02, COLD, "glow", y0=y - 0.04).xf((r.uniform(-0.12, 0.12), 0, 0.23)))
        m.add(sphere(0.12, 6, 4, COLD_HI, "glow").xf((0, 2.5, 0)))
        for k in range(5):
            a = r.uniform(0, 2 * PI)
            m.add(sphere(0.12, 5, 3, cx.c("moss"), "paint", squash=(1, 0.5, 1)).xf((math.cos(a) * 0.62, 0.2, math.sin(a) * 0.62)))
        pc.markers["lamps"].append([0, 1.4, 0.4])
        pc.markers["lamp_color"] = COLD
        pc.markers["lamp_fixed"] = 0.35
        pc.blockers.append([-0.6, -0.5, 0.6, 0.5])
        pc.mesh = m.ao(0, 2.6, 0.2)
        pc.size = [1.5, 2.6, 1.5]
        return pc

    def district_gate(cx):
        """one of Ravenhold's district gates, sealed: stone piers, a round arch, barred oak double doors with iron
        straps and a chain across, and a small pennant on each pier (no readable text)"""
        pc = Piece("district_gate"); r = K.rng(cx.seed, "district_gate"); m = Mesh()
        st = mix(W_, cx.c("stone"), 0.18)
        m.add(box(4.4, 0.16, 1.2, mix(st, cx.c("stone_lo"), 0.3), "stone", y0=0))
        for sx in (-1, 1):
            y = 0.16
            for i in range(6):
                h = r.uniform(0.44, 0.52)
                m.add(box(0.8, h, 1.0, mix(st, cx.c("stone_lo"), r.uniform(0, 0.25)), "stone", y0=y).xf((sx * 1.8, 0, 0)))
                y += h
            m.add(box(0.96, 0.18, 1.12, mix(st, cx.c("stone_hi"), 0.2), "stone", y0=y).xf((sx * 1.8, 0, 0)))
            m.add(cylinder(0.025, 0.025, 1.0, 4, cx.c("shadow"), "paint", y0=y + 0.18).xf((sx * 1.8, 0, 0.2)))
            m.add(box(0.03, 0.4, 0.5, cx.c("roof" if sx < 0 else "cloth"), "paint", y0=y + 0.7).xf((sx * 1.8, 0, 0.47)))
        cy, R = 2.9, 1.4
        for i in range(9):
            a0, a1 = PI * i / 9, PI * (i + 1) / 9
            m.add(K.beam((math.cos(a0) * R, cy + math.sin(a0) * R, 0), (math.cos(a1) * R, cy + math.sin(a1) * R, 0), 0.5,
                         mix(st, cx.c("stone_lo" if i % 2 else "stone_hi"), 0.2), "stone"))
        # the doors: vertical oak planks filling the opening, iron straps and a chain with a padlock
        for k in range(7):
            x = -1.2 + 0.4 * k
            top = cy + math.sqrt(max(0.0, R * R - x * x)) * 0.9
            m.add(box(0.38, top - 0.16, 0.12, mix(cx.c("timber"), cx.c("timber_lo"), r.uniform(0, 0.5)), "timber", y0=0.16).xf((x, 0, 0.05)))
        for y in (0.7, 1.8, 2.9):
            m.add(box(2.6, 0.1, 0.04, cx.c("shadow"), "paint", y0=y).xf((0, 0, 0.13)))
        for k in range(8):
            t = k / 7
            m.add(box(0.12, 0.08, 0.05, cx.c("stone_hi"), "paint", y0=1.5 - 0.35 * math.sin(PI * t)).xf((-1.1 + 2.2 * t, 0, 0.18), rot=(0, 0, 0.5 if k % 2 else -0.5)))
        m.add(box(0.2, 0.24, 0.08, mix(cx.c("flower_gold"), cx.c("timber"), 0.4), "paint", y0=1.0).xf((0, 0, 0.2)))
        pc.blockers += [[-2.25, -0.6, 2.25, 0.6]]
        pc.mesh = m.ao(0, 4.6, 0.22)
        pc.size = [4.5, 4.6, 1.2]
        return pc

    def float_lantern(cx, name, cols):
        """a mooring float on the water with a glass lantern (violet or red cold-fire) and its reflection"""
        pc = Piece(name); r = K.rng(cx.seed, name); m = Mesh()
        m.add(cylinder(0.32, 0.36, 0.16, 8, cx.c("timber"), "timber", y0=0.02, col_top=cx.c("timber_hi")))
        m.add(cylinder(0.035, 0.035, 0.7, 4, cx.c("shadow"), "paint", y0=0.18))
        m.add(box(0.26, 0.06, 0.26, cx.c("shadow"), "paint", y0=0.86))
        m.add(sphere(0.15, 7, 5, cols[1], "glow").xf((0, 0.74, 0)))
        m.add(sphere(0.07, 5, 3, cols[0], "glow").xf((0, 0.74, 0.06)))
        reflection(m, r, 0.0, 0.42, 5, cols)
        pc.markers["lamps"].append([0, 0.75, 0]); pc.markers["lamp_color"] = cols[1]; pc.markers["lamp_fixed"] = 0.5
        pc.mesh = m.ao(0, 0.9, 0.1)
        pc.size = [0.8, 0.95, 0.8]
        return pc

    def fish_orb(cx):
        """an orb lantern full of sea water on an iron stand: glowing sea-glass water with three little glowing fish"""
        pc = Piece("fish_orb"); r = K.rng(cx.seed, "fish_orb"); m = Mesh()
        m.add(box(0.36, 0.12, 0.36, mix(W_, cx.c("stone_lo"), 0.3), "stone", y0=0))
        m.add(cylinder(0.05, 0.04, 1.0, 6, cx.c("shadow"), "paint", y0=0.12))
        m.add(cylinder(0.2, 0.26, 0.08, 8, cx.c("shadow"), "paint", y0=1.06))
        R = 0.34
        m.add(sphere(R, 9, 6, ORB, "glow").xf((0, 1.14 + R, 0)))
        m.add(sphere(R * 0.45, 6, 4, ORB_HI, "glow", squash=(1, 0.6, 1)).xf((-0.08, 1.14 + R * 1.45, 0.14)))   # the glassy highlight
        for k, (col, fx, fy) in enumerate((("#f2c24a", -0.1, 0.0), ("#e47c8c", 0.12, 0.14), ("#ff9c70", 0.02, -0.14))):
            y = 1.14 + R + fy
            m.add(box(0.11, 0.06, 0.03, col, "glow", y0=y).xf((fx, 0, R - 0.03)))                       # fish body on the front of the glass
            m.add(box(0.04, 0.08, 0.03, col, "glow", y0=y - 0.01).xf((fx + (0.07 if k % 2 else -0.07), 0, R - 0.03)))   # tail
        m.add(box(0.12, 0.08, 0.12, cx.c("shadow"), "paint", y0=1.14 + 2 * R - 0.02))
        pc.markers["lamps"].append([0, 1.14 + R, 0.1]); pc.markers["lamp_color"] = ORB_HI; pc.markers["lamp_fixed"] = 0.45
        pc.markers["lamp_range"] = 5.0
        pc.blockers.append([-0.25, -0.25, 0.25, 0.25])
        pc.mesh = m.ao(0, 1.2, 0.15)
        pc.size = [0.7, 1.9, 0.7]
        return pc

    return {"float_lantern_violet": lambda cx: float_lantern(cx, "float_lantern_violet", (VIOLET_HI, VIOLET, VIOLET_LO)),
            "float_lantern_red": lambda cx: float_lantern(cx, "float_lantern_red", (RED_HI, RED, RED_LO)),
            "fish_orb": fish_orb,
            "harbor_water": harbor_water, "pier": pier, "rowboat": rowboat, "skiff": skiff, "pier_lantern": pier_lantern,
            "quay_lantern": quay_lantern, "bollard": bollard, "waystone": waystone, "district_gate": district_gate}
