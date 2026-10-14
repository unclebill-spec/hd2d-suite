"""The Verdant Heart (dungeon under Vanaheim) pieces for hd2d kit (original; Hearthmoor Art seat staging, 2026-10-05).
Mood: Bill's bioluminescent cave refs - a dark living-forest cavern full of glow: neon mushrooms reflected in black
water, glowing fern spirals, hanging glow vines, a glowing underground stream, pool and waterfall, red white-spotted
toadstools, glowroots in neon-blue cold fire.

Tiles / structure   vh_floor (4x4 m), vh_wall (4 m), vh_ceiling_lip (overhang for vines), glowroot_arch
Water               stream_straight (2 m), stream_bend (2x2 m, 90deg), glow_pool (3.4 m pond), waterfall (3.2 m fall
                    + splash basin), heart_spring (root-ringed bubbly spring)
Flora               glowroot_cluster, toadstool_giant, toadstool_shelf, neon_mushrooms_pink / _blue / _violet,
                    dripcap (tall cap trailing glowing tendrils), glowfern (violet), glowfern_blue, hanging_vines
                    (glow-bulb vine curtain), blight_bloom (violet corruption flower), heartseed_cradle (Hjortur's arena)

Drop-in: copy to tools/kit/ and add to kit.py like kit_harbor:
    import kit_verdant_heart as _vh; PROPS.update(_vh.pieces(__import__('types').SimpleNamespace(**globals())))
Biome palette on structure; NEON hexes appear ONLY on the self-lit 'glow' material (glowing mushrooms, vines, water,
roots, ferns, crystals) - allowed for environment glow per Bill (2026-10-05)."""
from __future__ import annotations

import math

PI = math.pi
COLD, COLD_HI, COLD_LO = "#5ab4f0", "#d8f4ff", "#2a6cb0"
NB, NB_HI, NB_LO = "#2ab4ff", "#a6ecff", "#1c62d8"
VIOLET, VIOLET_HI, VIOLET_LO = "#a45cf0", "#d4a8ff", "#6a34b8"
PINK, PINK_HI, PINK_LO = "#ff4fc8", "#ffb4ea", "#b82a8c"
GREEN, GREEN_HI, GREEN_LO = "#3cf08a", "#b8ffd4", "#14a85a"
RED, RED_LO, GILL, SPOT = "#e0302a", "#a81c22", "#ffc463", "#fff8e6"   # kit_hollows toadstool hexes
WATER, WATER_HI, WATER_DEEP = "#2ab4ff", "#a6ecff", "#1c62d8"


def pieces(K):
    box, cylinder, sphere, beam, mix, Piece, W_, Mesh = K.box, K.cylinder, K.sphere, K.beam, K.mix, K.Piece, K.W_, K.Mesh

    def rock(cx, t=0.0):
        """cavern stone: dark stone pulled toward the night-blue gloom"""
        return mix(mix(cx.c("stone_lo"), cx.c("shadow"), 0.35 + t), cx.c("cloth"), 0.18)

    def cap(m, r, x, y, z, R, h, spots=7, col=RED, lo=RED_LO, gill=GILL, spot=SPOT):
        m.add(sphere(R, 10, 6, col, "glow", squash=(1, h / R, 1), col_bottom=lo).xf((x, y, z)))
        m.add(cylinder(R * 0.93, R * 0.5, 0.07, 10, gill, "glow", y0=y - 0.06).xf((x, 0, z)))
        for k in range(spots):
            a = k * 2 * PI / spots + r.uniform(-0.3, 0.3)
            rr = R * r.uniform(0.3, 0.72)
            sy = y + h * math.sqrt(max(0.0, 1 - (rr / R) ** 2)) * 0.97
            m.add(sphere(R * r.uniform(0.11, 0.16), 6, 3, spot, "glow", squash=(1, 0.42, 1)).xf((x + math.cos(a) * rr, sy, z + math.sin(a) * rr)))

    def stem(m, cx, x, z, r0, r1, h, col=None, mat="paint", y0=0.0):
        c = col or cx.c("plaster_hi")
        m.add(cylinder(r0, r1, h, 8, c, mat, y0=y0, col_top=c if col else cx.c("plaster")).xf((x, 0, z)))

    def glowbulb(m, x, y, z, R, col, hi):
        m.add(sphere(R, 6, 4, col, "glow").xf((x, y, z)))
        m.add(sphere(R * 0.45, 5, 3, hi, "glow").xf((x - R * 0.25, y + R * 0.3, z + R * 0.4)))

    def root(m, cx, p0, p1, t, glow=None):
        m.add(beam(p0, p1, t, mix(cx.c("timber_lo"), cx.c("shadow"), 0.3), "timber"))
        if glow:                                                                 # glowing veins along the top + camera face
            a = [p0[0], p0[1] + t * 0.45, p0[2] + t * 0.3]; b = [p1[0], p1[1] + t * 0.45, p1[2] + t * 0.3]
            m.add(beam(a, b, t * 0.38, glow, "glow"))
            a = [p0[0], p0[1], p0[2] + t * 0.52]; b = [p1[0], p1[1], p1[2] + t * 0.52]
            m.add(beam(a, b, t * 0.22, glow, "glow"))

    # ------------------------------------------------------------------ tiles / structure
    def vh_floor(cx):
        """4 x 4 m cavern floor: dark loam, moss mats, pebbles, and glow-moss specks (blue / green) in the cracks"""
        pc = Piece("vh_floor"); r = K.rng(cx.seed, "vh_floor"); m = Mesh()
        base = mix(cx.c("shadow"), cx.c("leaf_deep"), 0.25)
        m.add(box(4.0, 0.1, 4.0, base, "stone", y0=-0.11))
        n = 8                                                                     # top as a 0.5 m quad grid: light pools fall off smoothly
        for i in range(n):
            for j in range(n):
                x0, z0 = -2 + i * 0.5, -2 + j * 0.5
                c = mix(base, cx.c("ink"), r.uniform(0.0, 0.18))
                m.quad((x0, 0, z0 + 0.5), (x0 + 0.5, 0, z0 + 0.5), (x0 + 0.5, 0, z0), (x0, 0, z0), c, mat="stone")
        for k in range(7):
            x, z = r.uniform(-1.6, 1.6), r.uniform(-1.6, 1.6)
            m.add(cylinder(r.uniform(0.35, 0.7), r.uniform(0.3, 0.6), 0.03, 9, mix(cx.c("moss"), cx.c("leaf_deep"), r.uniform(0.2, 0.6)), "moss", y0=0).xf((x, 0, z)))
        for k in range(10):
            x, z = r.uniform(-1.8, 1.8), r.uniform(-1.8, 1.8)
            m.add(sphere(r.uniform(0.06, 0.14), 5, 3, rock(cx, r.uniform(-0.2, 0.1)), "stone", squash=(1, 0.5, 1)).xf((x, 0.02, z)))
        for k in range(26):
            x, z = r.uniform(-1.9, 1.9), r.uniform(-1.9, 1.9)
            col = (NB_HI, GREEN, COLD, GREEN_HI)[k % 4]
            m.add(box(0.05, 0.02, 0.05, col, "glow", y0=0.0).xf((x, 0, z)))
        pc.mesh = m
        pc.size = [4.0, 0.1, 4.0]
        return pc

    def vh_wall(cx):
        """a 4 m run of cavern wall (3.6 m tall): lumpy stacked stone, moss on the ledges, cold-fire glow veins"""
        pc = Piece("vh_wall"); r = K.rng(cx.seed, "vh_wall"); m = Mesh()
        m.add(box(4.2, 3.7, 0.4, mix(rock(cx, 0.3), cx.c("ink"), 0.4), "stone", y0=0).xf((0, 0, -0.3)))   # backing slab (no gaps)
        for row in range(5):
            y = row * 0.72
            x = -2.0 + r.uniform(0, 0.3)
            while x < 2.0:
                w = r.uniform(0.6, 1.1)
                m.add(sphere(0.5, 7, 4, rock(cx, r.uniform(-0.15, 0.15)), "stone", squash=(w, 0.5, 0.55), noise=0.06, rnd=r).xf((x + w / 2, y + 0.38, r.uniform(-0.1, 0.1))))
                if r.random() < 0.4:
                    m.add(sphere(0.3, 6, 3, cx.c("moss"), "moss", squash=(w * 1.2, 0.35, 0.9)).xf((x + w / 2, y + 0.7, 0.18)))
                x += w * 0.9
        for k in range(4):                                                           # zig-zag glow veins
            x = -1.5 + k + r.uniform(-0.2, 0.2); y = 0.3
            for s in range(5):
                x2, y2 = x + r.uniform(-0.3, 0.3), y + r.uniform(0.4, 0.7)
                m.add(beam([x, y, 0.46], [x2, y2, 0.46], 0.05, (NB, COLD, GREEN, NB)[k], "glow"))
                x, y = x2, y2
        pc.mesh = m.ao(0, 3.6, 0.3)
        pc.blockers.append([-2.0, -0.5, 2.0, 0.5])
        pc.size = [4.0, 3.6, 1.1]
        return pc

    def vh_ceiling_lip(cx):
        """a rocky overhang lip at 4.2 m (hang vines / dripcaps under it; frames the top of a room)"""
        pc = Piece("vh_ceiling_lip"); r = K.rng(cx.seed, "lip"); m = Mesh()
        for k in range(6):
            x = -2.0 + k * 0.8
            m.add(sphere(0.55, 7, 4, rock(cx, r.uniform(-0.1, 0.1)), "stone", squash=(1.0, 0.55, 0.9), noise=0.06, rnd=r).xf((x, 4.4, 0)))
            m.add(cylinder(0.12, 0.0, r.uniform(0.3, 0.6), 5, rock(cx, 0.1), "stone", y0=0).xf((x + 0.3, 3.7, 0.2), rot=(PI, 0, 0)))   # stalactite
        pc.mesh = m
        pc.size = [4.6, 0.6, 1.0]
        return pc

    def glowroot_arch(cx):
        """two great roots twist up and meet overhead as a 3.4 m arch, cold-fire veins and glowing bulbs hanging"""
        pc = Piece("glowroot_arch"); r = K.rng(cx.seed, "garch"); m = Mesh()
        for sd in (-1, 1):
            pts = [(sd * 1.5, 0, 0), (sd * 1.42, 1.2, 0.1), (sd * 1.2, 2.3, -0.05), (sd * 0.7, 3.1, 0.05), (0, 3.4, 0)]
            for a, b in zip(pts, pts[1:]):
                root(m, cx, a, b, 0.42 - 0.05 * pts.index(a), NB)
            for k in range(4):                                                       # foot roots
                a = k * PI / 2 + 0.4
                root(m, cx, (sd * 1.5, 0.15, 0), (sd * 1.5 + math.cos(a) * 0.9, 0.0, math.sin(a) * 0.7), 0.16)
        for k, x in enumerate((-0.9, -0.3, 0.35, 0.95)):
            y = 3.2 - abs(x) * 0.4
            m.add(beam([x, y, 0], [x, y - 0.5 - (k % 2) * 0.3, 0], 0.03, mix(cx.c("leaf_deep"), cx.c("moss"), 0.5), "paint"))
            glowbulb(m, x, y - 0.6 - (k % 2) * 0.3, 0, 0.09, (NB, GREEN, NB, PINK)[k], NB_HI)
        pc.mesh = m.ao(0, 3.6, 0.2)
        pc.blockers += [[-1.8, -0.35, -1.2, 0.35], [1.2, -0.35, 1.8, 0.35]]
        pc.markers["lamps"].append([0, 2.6, 0.3]); pc.markers["lamp_color"] = NB; pc.markers["lamp_fixed"] = 0.5; pc.markers["lamp_range"] = 5.0
        pc.size = [3.8, 3.6, 1.2]
        return pc

    # ------------------------------------------------------------------ water
    def water_plane(m, w, d, x=0.0, z=0.0, y=0.02, streaks=True, r=None):
        m.add(box(w, 0.04, d, WATER, "glow", y0=y).xf((x, 0, z)))                 # bright shallows at the banks
        m.add(box(w * 0.62, 0.01, d, WATER_DEEP, "glow", y0=y + 0.04).xf((x, 0, z)))
        m.add(box(w * 0.26, 0.01, d, "#14204a", "glow", y0=y + 0.045).xf((x + w * 0.05, 0, z)))   # the dark mirror channel
        if streaks and r:
            for k in range(int(w * d * 3)):
                sx, sz = x + r.uniform(-w * 0.42, w * 0.42), z + r.uniform(-d * 0.45, d * 0.45)
                m.add(box(0.05, 0.01, r.uniform(0.2, 0.45), WATER_HI if k % 3 else W_, "glow", y0=y + 0.05).xf((sx, 0, sz)))

    def bank(m, cx, r, x0, z0, x1, z1, n):
        for k in range(n):
            t = k / max(1, n - 1)
            x, z = x0 + (x1 - x0) * t + r.uniform(-0.08, 0.08), z0 + (z1 - z0) * t + r.uniform(-0.08, 0.08)
            m.add(sphere(r.uniform(0.18, 0.3), 6, 4, rock(cx, r.uniform(-0.2, 0.1)), "stone", squash=(1, 0.6, 1)).xf((x, 0.05, z)))
            if k % 3 == 1:
                m.add(sphere(0.12, 5, 3, cx.c("moss"), "moss", squash=(1.3, 0.4, 1)).xf((x, 0.2, z)))
            if k % 4 == 2:
                m.add(box(0.05, 0.03, 0.05, GREEN_HI, "glow", y0=0.24).xf((x, 0, z)))

    def stream_straight(cx):
        """a 2 m run of glowing underground stream (1.4 m water between mossy stone banks), flows along z.
        Pair with the stream_flow decal for moving sparkles."""
        pc = Piece("stream_straight"); r = K.rng(cx.seed, "stream_s"); m = Mesh()
        m.add(box(2.0, 0.06, 2.0, mix(cx.c("shadow"), cx.c("ink"), 0.4), "stone", y0=-0.06))
        water_plane(m, 1.4, 2.0, r=r)
        for sd in (-1, 1):
            bank(m, cx, r, sd * 0.85, -0.95, sd * 0.85, 0.95, 6)
        pc.mesh = m
        pc.size = [2.0, 0.3, 2.0]
        pc.markers["lamps"].append([0, 0.3, 0]); pc.markers["lamp_color"] = WATER; pc.markers["lamp_fixed"] = 0.35; pc.markers["lamp_range"] = 3.5
        return pc

    def stream_bend(cx):
        """a 90deg bend (2 x 2 m): enters at -z, leaves at +x"""
        pc = Piece("stream_bend"); r = K.rng(cx.seed, "stream_b"); m = Mesh()
        m.add(box(2.0, 0.06, 2.0, mix(cx.c("shadow"), cx.c("ink"), 0.4), "stone", y0=-0.06))
        for k in range(8):                                                          # quarter ring of water strips
            a0, a1 = k / 8 * PI / 2, (k + 1) / 8 * PI / 2
            am = (a0 + a1) / 2
            px, pz = 1.0 - math.cos(am) * 1.0, -1.0 + math.sin(am) * 1.0
            m.add(box(1.4, 0.04, 0.24, WATER, "glow", y0=0.02).xf((px, 0, pz), rot=(0, am, 0)))
            m.add(box(0.85, 0.01, 0.22, WATER_DEEP, "glow", y0=0.06).xf((px, 0, pz), rot=(0, am, 0)))
            m.add(box(0.36, 0.01, 0.22, "#14204a", "glow", y0=0.065).xf((px, 0, pz), rot=(0, am, 0)))
            if k % 2 == 0:
                m.add(box(0.05, 0.01, 0.3, WATER_HI, "glow", y0=0.07).xf((px + r.uniform(-0.2, 0.2), 0, pz), rot=(0, am + PI / 2, 0)))
        bank(m, cx, r, -0.95, -0.95, -0.95, 0.95, 5); bank(m, cx, r, -0.9, 0.95, 0.95, 0.95, 5)
        bank(m, cx, r, 0.75, -0.95, 0.95, -0.75, 2)
        pc.mesh = m
        pc.size = [2.0, 0.3, 2.0]
        return pc

    def glow_pool(cx):
        """a still black-glass pond (3.4 m) that glows from below: neon-blue shallows, a dark deep middle that mirrors
        the mushrooms, glowing lily pads and a ring of mossy stones (the refs' reflecting pools)"""
        pc = Piece("glow_pool"); r = K.rng(cx.seed, "gpool"); m = Mesh()
        m.add(cylinder(1.6, 1.6, 0.04, 16, WATER, "glow", y0=0.02))
        m.add(cylinder(1.05, 1.05, 0.01, 14, WATER_DEEP, "glow", y0=0.06))
        m.add(cylinder(0.55, 0.55, 0.01, 12, mix(WATER_DEEP, "#101830", 0.5), "glow", y0=0.07))   # the dark mirror middle
        for k in range(5):
            a = k * 2 * PI / 5 + 0.3
            x, z = math.cos(a) * 1.1, math.sin(a) * 1.1
            m.add(cylinder(0.2, 0.2, 0.02, 8, GREEN_LO, "glow", y0=0.08).xf((x, 0, z)))
            m.add(sphere(0.06, 5, 3, (PINK, GREEN_HI, VIOLET_HI, PINK, NB_HI)[k], "glow").xf((x + 0.05, 0.14, z)))
        for k in range(14):
            a = k * 2 * PI / 14 + r.uniform(-0.1, 0.1)
            m.add(sphere(r.uniform(0.22, 0.34), 6, 4, rock(cx, r.uniform(-0.2, 0.1)), "stone", squash=(1.2, 0.6, 1)).xf((math.cos(a) * 1.75, 0.05, math.sin(a) * 1.75)))
            if k % 3 == 0:
                m.add(sphere(0.14, 5, 3, cx.c("moss"), "moss", squash=(1.3, 0.4, 1)).xf((math.cos(a) * 1.75, 0.25, math.sin(a) * 1.75)))
        pc.mesh = m
        pc.markers["lamps"].append([0, 0.4, 0]); pc.markers["lamp_color"] = WATER; pc.markers["lamp_fixed"] = 0.45; pc.markers["lamp_range"] = 5.0
        pc.blockers.append([-1.5, -1.5, 1.5, 1.5])
        pc.size = [3.8, 0.4, 3.8]
        return pc

    def waterfall(cx):
        """a 3.2 m glowing waterfall: a mossy cliff face, the fall as stacked glowing strips (NB / cold / white), a
        splash basin and stream mouth at +z (connects to stream_straight). Add the waterfall_sheet + waterfall_splash fx."""
        pc = Piece("waterfall"); r = K.rng(cx.seed, "wfall"); m = Mesh()
        for row in range(5):
            for k in range(5):
                x = -1.8 + k * 0.9 + r.uniform(-0.1, 0.1)
                if abs(x) < 0.8 and row < 5:
                    xo = -0.15
                else:
                    xo = 0.0
                m.add(sphere(0.55, 7, 4, rock(cx, r.uniform(-0.15, 0.15)), "stone", squash=(0.9, 0.7, 0.6), noise=0.05, rnd=r).xf((x, row * 0.7 + 0.35, -0.9 + xo)))
                if r.random() < 0.35:
                    m.add(sphere(0.25, 6, 3, cx.c("moss"), "moss", squash=(1.4, 0.35, 0.8)).xf((x, row * 0.7 + 0.72, -0.6)))
        m.add(box(1.8, 0.1, 0.5, rock(cx, -0.1), "stone", y0=3.3).xf((0, 0, -0.7)))      # the lip
        for k in range(9):                                                           # the fall
            x = -0.8 + k * 0.2
            col = (NB, COLD, WATER_HI, NB, COLD_HI, NB, COLD, WATER_HI, NB)[k]
            m.add(box(0.19, 3.3, 0.05, col, "glow", y0=0.05).xf((x, 0, -0.38 + 0.02 * (k % 2))))
        m.add(cylinder(1.3, 1.3, 0.04, 14, WATER, "glow", y0=0.02).xf((0, 0, 0.4)))
        m.add(cylinder(0.8, 0.8, 0.01, 12, WATER_HI, "glow", y0=0.06).xf((0, 0, 0.1)))
        for k in range(7):
            a = PI * (0.05 + 0.9 * k / 6)
            m.add(sphere(0.28, 6, 4, rock(cx), "stone", squash=(1.2, 0.6, 1)).xf((math.cos(a) * 1.45, 0.05, 0.4 + math.sin(a) * 0.95 * (1 if k not in (3,) else 0.0) + (1.0 if k == 3 else 0))))
        pc.mesh = m
        pc.markers["lamps"].append([0, 1.4, 0.2]); pc.markers["lamp_color"] = NB; pc.markers["lamp_fixed"] = 0.6; pc.markers["lamp_range"] = 6.5
        pc.blockers += [[-2.2, -1.4, 2.2, -0.4], [-1.3, -0.4, 1.3, 1.2]]
        pc.size = [4.4, 3.6, 2.8]
        return pc

    def heart_spring(cx):
        """the Heart Spring: a bubbly glowing spring ringed by living roots (heals on the befriend path)"""
        pc = Piece("heart_spring"); r = K.rng(cx.seed, "hspring"); m = Mesh()
        m.add(cylinder(1.25, 1.25, 0.05, 14, mix(WATER, COLD, 0.4), "glow", y0=0.06))
        m.add(cylinder(0.7, 0.7, 0.02, 12, COLD_HI, "glow", y0=0.11))
        m.add(cylinder(0.25, 0.25, 0.02, 8, W_, "glow", y0=0.13))
        for k in range(9):                                                           # bubbles
            a = k * 2 * PI / 9
            rr = r.uniform(0.2, 0.9)
            m.add(sphere(r.uniform(0.04, 0.08), 5, 3, W_, "glow").xf((math.cos(a) * rr, 0.16, math.sin(a) * rr)))
        for k in range(8):
            a = k * 2 * PI / 8
            p0 = (math.cos(a) * 1.35, 0.1, math.sin(a) * 1.35)
            p1 = (math.cos(a + 0.6) * 1.45, 0.35, math.sin(a + 0.6) * 1.45)
            root(m, cx, p0, p1, 0.24, GREEN if k % 2 else NB)
            if k % 3 == 0:
                glowbulb(m, p1[0], p1[1] + 0.15, p1[2], 0.08, GREEN, GREEN_HI)
        pc.mesh = m.ao(0, 0.5, 0.2)
        pc.markers["lamps"].append([0, 0.6, 0]); pc.markers["lamp_color"] = COLD; pc.markers["lamp_fixed"] = 0.5; pc.markers["lamp_range"] = 5.0
        pc.size = [3.2, 0.6, 3.2]
        return pc

    # ------------------------------------------------------------------ flora
    def glowroot_cluster(cx):
        """roots breaking out of the floor in a knot, cold-fire veins, three glowing bulbs"""
        pc = Piece("glowroot_cluster"); r = K.rng(cx.seed, "gclus"); m = Mesh()
        for k in range(6):
            a = k * 2 * PI / 6 + r.uniform(-0.2, 0.2)
            p0 = (math.cos(a) * 1.0, 0.0, math.sin(a) * 0.8)
            p1 = (math.cos(a) * 0.3, r.uniform(0.6, 1.1), math.sin(a) * 0.25)
            root(m, cx, p0, p1, r.uniform(0.16, 0.24), NB if k % 2 else COLD)
        for k in range(3):
            a = k * 2 * PI / 3 + 0.5
            glowbulb(m, math.cos(a) * 0.45, 0.9 + k * 0.12, math.sin(a) * 0.35, 0.12, (NB, GREEN, NB)[k], NB_HI)
        pc.mesh = m.ao(0, 1.2, 0.2)
        pc.markers["lamps"].append([0, 1.0, 0]); pc.markers["lamp_color"] = NB; pc.markers["lamp_fixed"] = 0.35; pc.markers["lamp_range"] = 3.5
        pc.blockers.append([-0.4, -0.4, 0.4, 0.4])
        pc.size = [2.0, 1.3, 1.6]
        return pc

    def toadstool_giant(cx):
        """a giant red toadstool (3.4 m): white spots, glowing warm gills, a skirt ring, glow-moss at the foot"""
        pc = Piece("toadstool_giant"); r = K.rng(cx.seed, "tgiant"); m = Mesh()
        stem(m, cx, 0, 0, 0.42, 0.3, 2.6)
        m.add(cylinder(0.55, 0.38, 0.14, 9, cx.c("plaster"), "paint", y0=1.8))
        m.add(sphere(0.6, 7, 3, cx.c("moss"), squash=(1, 0.25, 1)).xf((0, 0.02, 0)))
        for k in range(6):
            a = k * 2 * PI / 6
            m.add(box(0.05, 0.02, 0.05, GREEN_HI, "glow", y0=0.15).xf((math.cos(a) * 0.55, 0, math.sin(a) * 0.55)))
        cap(m, r, 0, 2.6, 0, 1.5, 0.8, spots=11)
        pc.mesh = m.ao(0, 3.4, 0.22)
        pc.markers["lamps"].append([0, 2.3, 0.4]); pc.markers["lamp_color"] = "#ff5a4a"; pc.markers["lamp_fixed"] = 0.4; pc.markers["lamp_range"] = 4.5
        pc.blockers.append([-0.45, -0.45, 0.45, 0.45])
        pc.size = [3.0, 3.4, 3.0]
        return pc

    def toadstool_shelf(cx):
        """an old mossy stump with red white-spotted bracket caps stepping up its side (glow material)"""
        pc = Piece("toadstool_shelf"); r = K.rng(cx.seed, "tshelf"); m = Mesh()
        m.add(cylinder(0.6, 0.5, 1.5, 9, cx.c("timber_lo"), "timber", y0=0, col_top=cx.c("timber")))
        m.add(sphere(0.55, 8, 3, cx.c("moss"), squash=(1, 0.25, 1)).xf((0, 1.5, 0)))
        for k, (y, a) in enumerate(((0.4, 0.3), (0.75, 1.2), (1.05, 0.2), (1.3, 1.6))):
            x, z = math.cos(a) * 0.55, math.sin(a) * 0.55
            m.add(sphere(0.32, 8, 4, RED, "glow", squash=(1, 0.32, 0.8), col_bottom=RED_LO).xf((x, y, z)))
            m.add(cylinder(0.28, 0.2, 0.03, 8, GILL, "glow", y0=y - 0.05).xf((x, 0, z)))
            for j in range(3):
                m.add(sphere(0.04, 4, 2, SPOT, "glow", squash=(1, 0.4, 1)).xf((x + (j - 1) * 0.1, y + 0.09, z + 0.05)))
        pc.mesh = m.ao(0, 1.6, 0.2)
        pc.blockers.append([-0.5, -0.5, 0.5, 0.5])
        pc.size = [1.4, 1.7, 1.4]
        return pc

    def neon_mushrooms(name, col, lo, hi, rim):
        def fn(cx):
            """bioluminescent mushrooms (the refs): glowing stems, neon caps with a bright rim and glowing gills"""
            pc = Piece(name); r = K.rng(cx.seed, name); m = Mesh()
            for k, (x, z, h, R) in enumerate(((0, 0, 1.6, 0.7), (0.75, 0.3, 0.9, 0.42), (-0.6, 0.35, 0.65, 0.32), (0.25, -0.5, 1.15, 0.5), (-0.3, -0.35, 0.4, 0.2))):
                m.add(cylinder(R * 0.24, R * 0.18, h, 8, rim, "glow", y0=0, col_top=hi).xf((x, 0, z)))
                m.add(sphere(R, 10, 5, col, "glow", squash=(1, 0.45, 1), col_bottom=lo).xf((x, h, z)))
                m.add(cylinder(R * 1.0, R * 0.96, 0.04, 12, hi, "glow", y0=h - 0.03).xf((x, 0, z)))       # bright rim
                m.add(cylinder(R * 0.9, R * 0.3, 0.06, 10, rim, "glow", y0=h - 0.09).xf((x, 0, z)))       # gills
                for j in range(4):
                    a = j * PI / 2 + r.uniform(0, 1)
                    m.add(sphere(R * 0.09, 4, 2, hi, "glow").xf((x + math.cos(a) * R * 0.5, h + R * 0.33, z + math.sin(a) * R * 0.5)))
            m.add(sphere(0.7, 7, 3, cx.c("moss"), squash=(1.3, 0.2, 1)).xf((0, 0.0, 0)))
            pc.mesh = m
            pc.markers["lamps"].append([0, 1.2, 0.3]); pc.markers["lamp_color"] = col; pc.markers["lamp_fixed"] = 0.45; pc.markers["lamp_range"] = 4.0
            pc.blockers.append([-0.3, -0.3, 0.3, 0.3])
            pc.size = [1.9, 1.9, 1.6]
            return pc
        return fn

    def dripcap(cx):
        """a tall pink-glow cap trailing glowing cyan tendrils like a jellyfish (ref 3)"""
        pc = Piece("dripcap"); r = K.rng(cx.seed, "dripcap"); m = Mesh()
        m.add(cylinder(0.14, 0.1, 2.6, 8, NB_HI, "glow", y0=0, col_top=PINK_HI))
        m.add(sphere(0.95, 12, 5, PINK, "glow", squash=(1, 0.38, 1), col_bottom=PINK_LO).xf((0, 2.6, 0)))
        m.add(cylinder(0.95, 0.9, 0.04, 14, PINK_HI, "glow", y0=2.57))
        for k in range(16):
            a = k * 2 * PI / 16
            x, z = math.cos(a) * 0.85, math.sin(a) * 0.85
            ln = r.uniform(0.7, 1.9)
            m.add(beam([x, 2.55, z], [x * 1.05, 2.55 - ln, z * 1.05], 0.03, (NB_HI, NB, PINK_HI, COLD_HI)[k % 4], "glow"))
            m.add(sphere(0.045, 4, 2, W_, "glow").xf((x * 1.05, 2.55 - ln, z * 1.05)))
        m.add(sphere(0.5, 7, 3, cx.c("moss"), squash=(1.2, 0.2, 1)).xf((0, 0, 0)))
        pc.mesh = m
        pc.markers["lamps"].append([0, 2.2, 0.2]); pc.markers["lamp_color"] = PINK; pc.markers["lamp_fixed"] = 0.5; pc.markers["lamp_range"] = 5.0
        pc.blockers.append([-0.2, -0.2, 0.2, 0.2])
        pc.size = [2.0, 3.0, 2.0]
        return pc

    def glowfern(name, col, hi, lo):
        def fn(cx):
            """a glowing fern: fronds arching out, each ending in a curled fiddlehead spiral (ref 5)"""
            pc = Piece(name); r = K.rng(cx.seed, name); m = Mesh()
            for k in range(7):
                a = k * 2 * PI / 7 + r.uniform(-0.2, 0.2)
                L = r.uniform(1.0, 1.4)
                p0 = (0, 0.05, 0)
                p1 = (math.cos(a) * L * 0.4, L * 0.9, math.sin(a) * L * 0.4)
                m.add(beam(p0, p1, 0.04, lo, "glow"))
                # the fiddlehead: a shrinking spiral of beads
                cxp, cyp = p1[0] + math.cos(a) * 0.12, p1[1]
                for j in range(9):
                    t = j / 8
                    rr = 0.16 * (1 - t * 0.8)
                    ang = PI * 0.5 + t * PI * 2.2
                    x = cxp + math.cos(a) * math.cos(ang) * rr
                    y = cyp + math.sin(ang) * rr
                    z = p1[2] + math.sin(a) * math.cos(ang) * rr
                    m.add(sphere(0.035 * (1 - t * 0.5), 4, 2, hi if j > 5 else col, "glow").xf((x, y, z)))
                for j in range(4):                                                   # leaflets along the frond
                    t = (j + 1) / 5
                    px, py, pz = p1[0] * t, 0.05 + (p1[1] - 0.05) * t, p1[2] * t
                    m.add(beam([px, py, pz], [px - math.sin(a) * 0.14, py + 0.05, pz + math.cos(a) * 0.14], 0.025, col, "glow"))
                    m.add(beam([px, py, pz], [px + math.sin(a) * 0.14, py + 0.05, pz - math.cos(a) * 0.14], 0.025, col, "glow"))
            m.add(sphere(0.3, 6, 3, cx.c("moss"), squash=(1.2, 0.3, 1)).xf((0, 0, 0)))
            pc.mesh = m
            pc.markers["lamps"].append([0, 0.6, 0]); pc.markers["lamp_color"] = col; pc.markers["lamp_fixed"] = 0.3; pc.markers["lamp_range"] = 2.5
            pc.size = [1.6, 1.2, 1.6]
            return pc
        return fn

    def hanging_vines(cx):
        """a curtain of glowing hanging vines (from 4.2 m) with glow bulbs in green / blue / pink, on a mossy root rail.
        Hang under vh_ceiling_lip or a glowroot_arch; does not block."""
        pc = Piece("hanging_vines"); r = K.rng(cx.seed, "vines"); m = Mesh()
        m.add(beam([-1.3, 4.2, 0], [1.3, 4.25, 0], 0.18, mix(cx.c("timber_lo"), cx.c("shadow"), 0.3), "timber"))
        m.add(beam([-1.3, 4.32, 0], [1.3, 4.37, 0], 0.12, cx.c("moss"), "moss"))
        for k in range(11):
            x = -1.2 + k * 0.24 + r.uniform(-0.05, 0.05)
            ln = r.uniform(1.4, 3.2)
            col = (GREEN, NB, GREEN, PINK, GREEN_HI, NB, GREEN, VIOLET, GREEN, NB, PINK)[k]
            m.add(beam([x, 4.15, 0], [x + r.uniform(-0.06, 0.06), 4.15 - ln, r.uniform(-0.05, 0.05)], 0.03, mix(GREEN_LO, cx.c("leaf_deep"), 0.3), "glow"))
            for j in range(int(ln / 0.45)):
                y = 4.0 - j * 0.45 - r.uniform(0, 0.1)
                m.add(sphere(0.045, 4, 2, col, "glow").xf((x, y, 0.03)))
            glowbulb(m, x, 4.15 - ln - 0.05, 0, 0.07, col, W_)
        pc.mesh = m
        pc.markers["lamps"].append([0, 2.4, 0.3]); pc.markers["lamp_color"] = GREEN; pc.markers["lamp_fixed"] = 0.35; pc.markers["lamp_range"] = 4.0
        pc.size = [2.8, 4.4, 0.4]
        return pc

    def blight_bloom(cx):
        """the corruption: a violet-glowing blight flower on a dark knot of roots (cleanse it to dim it)"""
        pc = Piece("blight_bloom"); r = K.rng(cx.seed, "bbloom"); m = Mesh()
        for k in range(5):
            a = k * 2 * PI / 5
            root(m, cx, (math.cos(a) * 0.6, 0, math.sin(a) * 0.6), (0, 0.5, 0), 0.12, VIOLET_LO)
        for k in range(6):
            a = k * 2 * PI / 6
            m.add(sphere(0.22, 6, 3, VIOLET, "glow", squash=(1, 0.35, 0.6)).xf((math.cos(a) * 0.22, 0.62, math.sin(a) * 0.22)))
        m.add(sphere(0.12, 6, 4, VIOLET_HI, "glow").xf((0, 0.68, 0)))
        m.add(sphere(0.05, 4, 2, W_, "glow").xf((0, 0.78, 0)))
        pc.mesh = m
        pc.markers["lamps"].append([0, 0.8, 0]); pc.markers["lamp_color"] = VIOLET; pc.markers["lamp_fixed"] = 0.4; pc.markers["lamp_range"] = 3.0
        pc.size = [1.3, 0.9, 1.3]
        return pc

    def heartseed_cradle(cx):
        """Hjortur's arena centrepiece: great roots cupping the Heartseed, a glowing green seed with a cold-fire halo"""
        pc = Piece("heartseed_cradle"); r = K.rng(cx.seed, "cradle"); m = Mesh()
        m.add(cylinder(1.6, 1.8, 0.3, 14, rock(cx), "stone", y0=0))
        m.add(cylinder(1.5, 1.5, 0.02, 14, mix(cx.c("moss"), cx.c("leaf_deep"), 0.4), "moss", y0=0.3))
        for k in range(5):
            a = k * 2 * PI / 5 + 0.3
            p0 = (math.cos(a) * 1.45, 0.3, math.sin(a) * 1.45)
            p1 = (math.cos(a) * 1.05, 1.3, math.sin(a) * 1.05)
            p2 = (math.cos(a + 0.5) * 0.55, 2.15, math.sin(a + 0.5) * 0.55)
            root(m, cx, p0, p1, 0.16, GREEN)
            root(m, cx, p1, p2, 0.11, GREEN)
            glowbulb(m, p2[0], p2[1] + 0.08, p2[2], 0.07, GREEN_HI, W_)
        m.add(sphere(0.42, 10, 7, GREEN, "glow", col_bottom=GREEN_LO).xf((0, 1.45, 0)))
        m.add(sphere(0.2, 6, 4, GREEN_HI, "glow").xf((-0.1, 1.58, 0.2)))
        m.add(cylinder(0.75, 0.75, 0.03, 16, NB, "glow", y0=1.45))                   # cold-fire halo ring
        pc.mesh = m.ao(0, 2.4, 0.2)
        pc.markers["lamps"].append([0, 1.5, 0]); pc.markers["lamp_color"] = GREEN; pc.markers["lamp_fixed"] = 0.7; pc.markers["lamp_range"] = 7.0
        pc.blockers.append([-1.6, -1.6, 1.6, 1.6])
        pc.size = [3.6, 2.5, 3.6]
        return pc

    return {
        "vh_floor": vh_floor, "vh_wall": vh_wall, "vh_ceiling_lip": vh_ceiling_lip, "glowroot_arch": glowroot_arch,
        "stream_straight": stream_straight, "stream_bend": stream_bend, "glow_pool": glow_pool, "waterfall": waterfall,
        "heart_spring": heart_spring, "glowroot_cluster": glowroot_cluster, "toadstool_giant": toadstool_giant,
        "toadstool_shelf": toadstool_shelf,
        "neon_mushrooms_pink": neon_mushrooms("neon_mushrooms_pink", PINK, PINK_LO, PINK_HI, NB_HI),
        "neon_mushrooms_blue": neon_mushrooms("neon_mushrooms_blue", NB, NB_LO, NB_HI, GREEN_HI),
        "neon_mushrooms_violet": neon_mushrooms("neon_mushrooms_violet", VIOLET, VIOLET_LO, VIOLET_HI, PINK_HI),
        "dripcap": dripcap,
        "glowfern": glowfern("glowfern", VIOLET, VIOLET_HI, VIOLET_LO),
        "glowfern_blue": glowfern("glowfern_blue", NB, NB_HI, NB_LO),
        "hanging_vines": hanging_vines, "blight_bloom": blight_bloom, "heartseed_cradle": heartseed_cradle,
    }
