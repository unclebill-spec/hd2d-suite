"""Bifrost Crossing pieces for hd2d kit (original, Hearthmoor Stage 6 part 1): bifrost_plaza (the floating portal
plaza: a chamfered flagstone deck with a seven-band rainbow inlay, a kerb rim and a tapering rock root hung with
roots and cold-fire crystals), bifrost_bridge (the rainbow bridge of light out to the skiff landing), bifrost_landing
(a small floating jetty with mooring posts), skiff_keel (the cold-fire wake a rift-skiff floats on), realm_arch (a
tall gloom-stone gate with a jagged crown) + realm_glow_<hue> (its rune rim, keystone crystal, crown shards and realm
sigil in that realm's colour), guild_kiosk (the Gatekeepers' Guild post: counter, ledger, key banner, cold-fire lamp)
and rift_brazier_<cold|violet|red> (a stone bowl of jagged neon flame).
Style references (Bill's rift refs: stone arches with coloured glowing swirls, jagged neon rims) were looked at for
ideas only; nothing is traced. Imported by kit.py; biome palette + the shared mesh helpers. Off-palette colours are
only the NEON accents on glow pixels (the self-lit 'glow' material, no bloom)."""
from __future__ import annotations

import math

PI = math.pi
COLD, COLD_HI, COLD_LO = "#5ab4f0", "#d8f4ff", "#2a6cb0"         # cold fire (Sefa's / Ravenhold's blue)
NB, NB_HI, NB_LO = "#2ab4ff", "#a6ecff", "#1c62d8"               # neon blue (Niflheim)
VIOLET, VIOLET_HI, VIOLET_LO = "#a45cf0", "#d4a8ff", "#6a34b8"   # neon violet (Alfheim)
RED, RED_HI, RED_LO = "#e0302a", "#ff5a4a", "#a81c22"            # neon red (Muspelheim)


def pieces(K):
    box, cylinder, sphere, mix, Piece, W_, Mesh = K.box, K.cylinder, K.sphere, K.mix, K.Piece, K.W_, K.Mesh
    from meshlib import fix_winding as fix

    def hue3(cx, hue):
        """(lo, mid, hi) glow colours per realm: NEON for violet / blue / red, biome palette for the rest"""
        c = cx.c
        return {"gold": (c("plaster_lo"), c("flower_gold"), c("white")), "green": (c("moss"), c("grass_hi"), c("white")),
                "violet": (VIOLET_LO, VIOLET, VIOLET_HI), "ice": (c("stone_hi"), c("sky"), c("white")),
                "amber": (c("timber"), c("roof_hi"), c("lamp")), "red": (RED_LO, RED, RED_HI), "blue": (NB_LO, NB, NB_HI),
                "rose": (c("roof"), c("flower_rose"), c("white")), "rainbow": (VIOLET_LO, NB, c("white"))}[hue]

    def rainbow(cx):
        """the bridge's seven bands, red -> violet (NEON red / blue / violet + palette lamp, gold, green, blue)"""
        return [RED, cx.c("lamp"), cx.c("flower_gold"), cx.c("grass_hi"), NB, cx.c("flower_blue"), VIOLET]

    def gloom(cx, t=0.0):
        return mix(mix(W_, cx.c("stone_lo"), 0.55), cx.c("cloth"), 0.12 + t)

    def slab(pts, y0, y1, col, mat, top_mat=None, col_top=None, scale_bot=1.0):
        """a convex polygon prism (xz points, counter-clockwise or not); the bottom ring can shrink (a frustum)"""
        m = Mesh()
        n = len(pts)
        cxz = (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n)
        bot = [(cxz[0] + (x - cxz[0]) * scale_bot, cxz[1] + (z - cxz[1]) * scale_bot) for x, z in pts]
        ct = col_top or col
        for i in range(1, n - 1):
            a, b, c = pts[0], pts[i], pts[i + 1]
            m.tri((a[0], y1, a[1]), (b[0], y1, b[1]), (c[0], y1, c[1]), ct, ((a[0], a[1]), (b[0], b[1]), (c[0], c[1])), top_mat or mat)
            a, b, c = bot[0], bot[i], bot[i + 1]
            m.tri((a[0], y0, a[1]), (c[0], y0, c[1]), (b[0], y0, b[1]), col, ((a[0], a[1]), (c[0], c[1]), (b[0], b[1])), mat)
        for i in range(n):
            p, q = pts[i], pts[(i + 1) % n]
            pb, qb = bot[i], bot[(i + 1) % n]
            L = math.hypot(q[0] - p[0], q[1] - p[1])
            m.quad((pb[0], y0, pb[1]), (qb[0], y0, qb[1]), (q[0], y1, q[1]), (p[0], y1, p[1]), (col, col, ct, ct),
                   ((0, y0), (L, y0), (L, y1), (0, y1)), mat)
        return fix(m, (cxz[0], (y0 + y1) / 2, cxz[1]))

    # ------------------------------------------------------------------ the floating plaza
    PW, PD, CH = 13.5, 9.75, 3.5   # half width, half depth, front chamfer
    PLAZA = [(-PW, -PD), (PW, -PD), (PW, PD - CH), (PW - CH, PD), (-PW + CH, PD), (-PW, PD - CH)]

    def bifrost_plaza(cx):
        """27 x 19.5 m chamfered flagstone deck (top y=0, local z -9.75..9.75), the bridge gap in the front kerb at
        x -1.5..1.5; a seven-band rainbow inlay runs from the bridge gap to the stair foot (local z 2.45);
        underneath, four tapering rock bands to a point ~8 m down, roots, hanging stones and cold-fire crystals"""
        pc = Piece("bifrost_plaza"); r = K.rng(cx.seed, "bifrost_plaza"); m = Mesh()
        top = mix(W_, cx.c("stone"), 0.32)
        m.add(slab(PLAZA, -0.4, 0.0, mix(gloom(cx), cx.c("shadow"), 0.2), "stone", top_mat="cobble", col_top=top))
        # kerb rim: low blocks round the edge (under the walk step), a gap for the bridge
        for i in range(len(PLAZA)):
            p, q = PLAZA[i], PLAZA[(i + 1) % len(PLAZA)]
            L = math.hypot(q[0] - p[0], q[1] - p[1]); n = max(1, int(L / 1.5))
            ang = math.atan2(q[1] - p[1], q[0] - p[0])
            nx, nz = math.sin(ang), -math.cos(ang)   # inward normal for a clockwise-in-screen polygon
            for k in range(n):
                t = (k + 0.5) / n
                x, z = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
                if abs(z - PD) < 0.01 and abs(x) < 1.9:
                    continue
                m.add(box(L / n * 0.96, 0.12, 0.42, mix(gloom(cx), cx.c("stone_hi"), r.uniform(0.05, 0.25)), "stone", y0=0.0)
                      .xf((x - nx * 0.21, 0, z - nz * 0.21), rot=(0, -ang, 0)))
        # the rainbow inlay: seven narrow glow bands up the middle, from the bridge gap to the stair foot
        cols = rainbow(cx)
        z0, z1 = 2.45, PD
        for k, col in enumerate(cols):
            x = (k - 3) * 0.12
            m.add(box(0.1, 0.012, z1 - z0, col, "glow", y0=0.0).xf((x, 0, (z0 + z1) / 2)))
        for zz in (z0 + 0.2, z0 + 4.2, z0 + 7.2):   # stone ties across the inlay, so it reads as set in the paving
            m.add(box(1.1, 0.016, 0.16, mix(gloom(cx), cx.c("stone_hi"), 0.3), "stone", y0=0.0).xf((0, 0, zz)))
        # underneath: tapering rock bands (frustums) down to a point
        y = -0.4
        for k, (s, h) in enumerate(((0.93, 1.2), (0.78, 1.5), (0.55, 1.8), (0.3, 2.0), (0.05, 2.2))):
            s0 = 1.0 if k == 0 else (0.93, 0.78, 0.55, 0.3)[k - 1]
            pts = [(x * s0, z * s0) for x, z in PLAZA]
            col = mix(gloom(cx, 0.05 * k), cx.c("ink"), 0.12 * k)
            m.add(slab(pts, y - h, y, col, "stone", scale_bot=s / s0))
            y -= h
        for k in range(22):   # rocks jutting from the underside
            x, z = r.uniform(-PW, PW) * 0.6, r.uniform(-PD, PD) * 0.6
            m.add(sphere(r.uniform(0.5, 1.0), 6, 4, mix(gloom(cx), cx.c("ink"), 0.2), "stone", noise=0.2, rnd=r).xf((x, r.uniform(-4.5, -1.2), z)))
        for k in range(36):   # roots + hanging stones off the front and side rims
            i = r.randrange(len(PLAZA)); p, q = PLAZA[i], PLAZA[(i + 1) % len(PLAZA)]; t = r.random()
            x, z = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
            L = r.uniform(0.6, 2.6)
            m.add(box(0.07, L, 0.07, mix(cx.c("timber_lo"), cx.c("moss"), r.uniform(0, 0.5)), "paint", y0=-0.38 - L).xf((x * 0.99, 0, z * 0.99)))
            if k % 4 == 0:
                m.add(sphere(0.14, 5, 3, mix(gloom(cx), cx.c("ink"), 0.1), "stone").xf((x * 0.99, -0.4 - L, z * 0.99)))
        for k in range(10):   # cold-fire crystals growing out of the rock root
            a = r.uniform(0, 2 * PI); rr = r.uniform(0.35, 0.8); yy = -0.9 - (1 - rr) * 5.0
            x, z = math.cos(a) * PW * rr * 0.85, math.sin(a) * PD * rr * 0.85
            col = (COLD, VIOLET, COLD_HI)[k % 3]
            m.add(K.beam((x, yy, z), (x * 1.06, yy - r.uniform(0.5, 1.0), z * 1.06), 0.16, col, "glow"))
        for k in range(24):   # moss tufts on the rim
            i = r.randrange(len(PLAZA)); p, q = PLAZA[i], PLAZA[(i + 1) % len(PLAZA)]; t = r.random()
            x, z = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
            if abs(z - PD) < 0.01 and abs(x) < 2.2:
                continue
            m.add(sphere(r.uniform(0.12, 0.24), 5, 3, cx.c("moss" if k % 3 else "leaf_deep"), "paint", squash=(1, 0.5, 1)).xf((x * 0.985, 0.05, z * 0.985)))
        pc.mesh = m.ao(-10.0, 10.0, 0.3)
        pc.size = [2 * PW, 10.0, 2 * PD]
        return pc

    def bifrost_bridge(cx):
        """the rainbow bridge: 2.8 m wide, 5.6 m long (local z -2.8..2.8), deck top y=0; low gloom-stone kerbs, seven
        glowing bands of rainbow light between them, and light dripping off its underside into the void"""
        pc = Piece("bifrost_bridge"); r = K.rng(cx.seed, "bifrost_bridge"); m = Mesh()
        L = 5.6
        cols = rainbow(cx)
        bw = 2.2 / 7
        for k, col in enumerate(cols):
            x = -1.1 + bw * (k + 0.5)
            m.add(box(bw * 0.94, 0.08, L, col, "glow", y0=-0.08).xf((x, 0, 0)))
            for j in range(3):   # light dripping off the underside, longest under the middle bands
                z = r.uniform(-L / 2 + 0.3, L / 2 - 0.3)
                h = r.uniform(0.3, 1.2) * (1.3 - abs(k - 3) * 0.15)
                m.add(box(bw * 0.5, h, 0.08, col, "glow", y0=-0.08 - h).xf((x, 0, z)))
        for sx in (-1, 1):
            m.add(box(0.3, 0.16, L + 0.1, mix(gloom(cx), cx.c("stone_hi"), 0.2), "stone", y0=-0.1).xf((sx * 1.25, 0, 0)))
            m.add(box(0.26, 0.3, L, mix(gloom(cx), cx.c("ink"), 0.2), "stone", y0=-0.4).xf((sx * 1.25, 0, 0)))
            for k in range(4):   # cold-fire studs along the kerbs
                m.add(box(0.1, 0.04, 0.1, COLD_HI if k % 2 else COLD, "glow", y0=0.06).xf((sx * 1.25, 0, -L / 2 + 0.7 + k * 1.4)))
        pc.mesh = m.ao(-1.2, 1.4, 0.15)
        pc.size = [2.8, 1.5, L]
        return pc

    LAND = [(-4.0, -2.0), (4.0, -2.0), (4.0, 1.2), (3.2, 2.0), (-3.2, 2.0), (-4.0, 1.2)]

    def bifrost_landing(cx):
        """the skiff landing: an 8 x 4 m floating jetty (local z -2..2, top y=0): plank deck on a small rock root,
        mooring posts with cold-fire lamps on the east side where the skiff ties up"""
        pc = Piece("bifrost_landing"); r = K.rng(cx.seed, "bifrost_landing"); m = Mesh()
        m.add(slab(LAND, -0.3, -0.08, mix(gloom(cx), cx.c("shadow"), 0.2), "stone"))
        for i in range(19):
            x = -3.8 + 0.2 + i * 0.4
            zz = 2.0 - (max(0.0, abs(x) - 3.2))   # follow the chamfer
            m.add(box(0.37, 0.08, 1.9 + zz, mix(cx.c("timber"), cx.c("timber_hi"), r.uniform(0.0, 0.35)), "timber", y0=-0.08)
                  .xf((x, 0, (-2.0 + zz) / 2)))
        y = -0.3
        for k, (s, h) in enumerate(((0.8, 0.9), (0.5, 1.2), (0.12, 1.4))):
            s0 = (1.0, 0.8, 0.5)[k]
            m.add(slab([(x * s0, z * s0) for x, z in LAND], y - h, y, mix(gloom(cx, 0.05 * k), cx.c("ink"), 0.15 * k), "stone", scale_bot=s / s0))
            y -= h
        for z in (-1.2, 1.0):   # mooring posts with cold-fire lamps (east side)
            m.add(cylinder(0.12, 0.1, 1.2, 6, cx.c("timber_lo"), "timber", y0=-0.1, col_top=cx.c("timber")).xf((3.75, 0, z)))
            m.add(box(0.22, 0.26, 0.22, COLD, "glow", y0=1.1).xf((3.75, 0, z)))
            m.add(box(0.1, 0.14, 0.1, COLD_HI, "glow", y0=1.16).xf((3.75, 0, z)))
            m.add(box(0.3, 0.05, 0.3, cx.c("shadow"), "paint", y0=1.36).xf((3.75, 0, z)))
        m.add(K.beam((3.75, 0.7, -1.2), (3.75, 0.7, 1.0), 0.04, cx.c("plaster_lo"), "paint"))   # mooring rope
        pc.markers["lamps"] += [[3.75, 1.25, -1.2], [3.75, 1.25, 1.0]]
        pc.markers["lamp_color"] = COLD; pc.markers["lamp_fixed"] = 0.4
        pc.blockers += [[3.6, -1.35, 3.9, -1.05], [3.6, 0.85, 3.9, 1.15]]
        pc.mesh = m.ao(-3.0, 3.6, 0.2)
        pc.size = [8.0, 3.6, 4.0]
        return pc

    def skiff_keel(cx):
        """the cold-fire wake a rift-skiff floats on: an oval of glow dashes under the hull, brightest at the keel"""
        pc = Piece("skiff_keel"); r = K.rng(cx.seed, "skiff_keel"); m = Mesh()
        for k in range(26):
            a = r.uniform(0, 2 * PI); rr = r.uniform(0.2, 1.0)
            x, z = math.cos(a) * 1.3 * rr, math.sin(a) * 3.0 * rr
            col = COLD_HI if rr < 0.35 else COLD if rr < 0.75 else COLD_LO
            m.add(box(r.uniform(0.2, 0.6), 0.02, 0.08, col, "glow", y0=0.0).xf((x, 0, z)))
        for k in range(6):   # little cold-fire drips off the keel
            z = -2.0 + k * 0.8
            m.add(box(0.06, r.uniform(0.3, 0.8), 0.06, COLD, "glow", y0=-0.8).xf((r.uniform(-0.2, 0.2), 0, z)))
        pc.markers["lamps"].append([0, 0.2, 0]); pc.markers["lamp_color"] = COLD; pc.markers["lamp_fixed"] = 0.3
        pc.mesh = m
        pc.size = [2.6, 0.9, 6.0]
        return pc

    # ------------------------------------------------------------------ realm arches
    CY, R0, R1 = 2.45, 0.8, 1.42   # opening x -0.8..0.8 (the vortex / seal billboard fits it, like rift_arch)

    def realm_arch(cx):
        """a tall gloom-stone realm gate (~4.9 m): a wide two-step plinth, stepped pillars with capitals, a ring of
        voussoirs and a jagged crown of five stone spikes. The colour (rune rim, crystals, sigil) is its glow piece."""
        pc = Piece("realm_arch"); r = K.rng(cx.seed, "realm_arch"); m = Mesh()
        st = gloom(cx)
        m.add(box(3.6, 0.1, 1.5, mix(st, cx.c("stone_lo"), 0.2), "stone", y0=0))
        m.add(box(3.2, 0.08, 1.2, mix(st, cx.c("stone_hi"), 0.12), "stone", y0=0.1))
        for sx in (-1, 1):
            y = 0.18
            for i in range(4):
                h = (0.56, 0.5, 0.52, 0.48)[i]
                w = 0.7 if i % 2 == 0 else 0.62
                m.add(box(w, h - 0.02, 0.7, mix(st, cx.c("ink"), r.uniform(0.0, 0.2)), "stone", y0=y).xf((sx * 1.12, 0, 0)))
                y += h
            m.add(box(0.86, 0.14, 0.84, mix(st, cx.c("stone_hi"), 0.2), "stone", y0=y).xf((sx * 1.12, 0, 0)))   # capital
            # a thin finial post on each capital
            m.add(box(0.22, 0.5, 0.22, mix(st, cx.c("stone_lo"), 0.1), "stone", y0=y + 0.14).xf((sx * 1.62, 0, 0)))
        n = 11
        for i in range(n):
            a0, a1 = PI * i / n, PI * (i + 1) / n
            am = (a0 + a1) / 2
            ln = (R0 + R1) / 2 * (a1 - a0) * 0.94
            col = mix(st, cx.c("stone_hi" if i % 2 else "stone_lo"), 0.14)
            m.add(box(ln, R1 - R0, 0.64, col, "stone").xf((math.cos(am) * (R0 + R1) / 2, CY + math.sin(am) * (R0 + R1) / 2, 0), rot=(0, 0, am - PI / 2)))
        # the jagged crown: five stone spikes fanning out over the ring (tallest in the middle)
        for k in range(5):
            am = PI * (k + 1) / 6
            L = 0.55 + (0.5 if k == 2 else 0.25 if k in (1, 3) else 0.0)
            bx, by = math.cos(am) * (R1 - 0.05), CY + math.sin(am) * (R1 - 0.05)
            m.add(K.beam((bx, by, 0), (bx + math.cos(am) * L, by + math.sin(am) * L, 0), 0.26, mix(st, cx.c("ink"), 0.1), "stone", depth=0.4))
        pc.mesh = m.ao(0, 4.9, 0.22)
        pc.markers["rift"] = [[0, 0.2, 0.0]]
        pc.blockers += [[-1.55, -0.45, -0.77, 0.45], [0.77, -0.45, 1.55, 0.45]]
        pc.size = [3.6, 4.9, 1.5]
        return pc

    SIGILS = {   # one simple realm mark each (bars on a 5 x 5 grid: (x0, y0, x1, y1)); invented, no real runes
        "gold": [(2, 0, 2, 4), (0, 4, 4, 4), (1, 2, 3, 2)], "green": [(2, 0, 2, 4), (0, 2, 2, 4), (4, 2, 2, 4)],
        "violet": [(0, 0, 2, 4), (4, 0, 2, 4), (1, 2, 3, 2)], "ice": [(0, 0, 4, 4), (4, 0, 0, 4), (2, 0, 2, 4)],
        "amber": [(0, 1, 4, 1), (0, 3, 4, 3), (2, 1, 2, 3)], "red": [(2, 0, 0, 4), (2, 0, 4, 4), (2, 0, 2, 2)],
        "blue": [(0, 4, 2, 0), (2, 0, 4, 4), (0, 2, 4, 2)], "rose": [(0, 0, 0, 4), (4, 0, 4, 4), (0, 2, 4, 2)],
        "rainbow": [(0, 4, 2, 0), (2, 0, 4, 4), (1, 4, 3, 4)],
    }

    def realm_glow(cx, hue):
        """a realm arch's light (glow pixels only): a jagged rune rim lining the opening, a faceted keystone crystal,
        crystal tips on the crown spikes, rune ticks on the pillar fronts and the realm's sigil on the plinth"""
        pc = Piece(f"realm_glow_{hue}"); r = K.rng(cx.seed, f"realm_glow_{hue}"); m = Mesh()
        lo, mid, hi = hue3(cx, hue)
        bands = rainbow(cx) if hue == "rainbow" else None
        zf = 0.33
        # rim: the inner edge of the ring + pillar inner faces, jagged (alternating long / short teeth)
        n = 22
        for i in range(n):
            a = PI * (i + 0.5) / n
            col = bands[i * 7 // n] if bands else (hi if i % 5 == 2 else mid)
            t = 0.1 if i % 2 else 0.18
            x, y = math.cos(a) * (R0 + t / 2 - 0.02), CY + math.sin(a) * (R0 + t / 2 - 0.02)
            m.add(box(0.13, t, 0.05, col, "glow").xf((x, y, zf), rot=(0, 0, a - PI / 2)))
        for sx in (-1, 1):
            for k in range(9):
                y = 0.32 + k * 0.24
                col = bands[(k if sx < 0 else 8 - k) % 7] if bands else (mid if k % 3 else hi)
                w = 0.14 if k % 2 else 0.08
                m.add(box(w, 0.13, 0.05, col, "glow", y0=y).xf((sx * (0.8 + w / 2 - 0.02), 0, zf)))
            for k in (0, 2):   # rune ticks on the pillar fronts
                y = 0.5 + k * 0.52
                m.add(box(0.06, 0.26, 0.02, mid if not bands else bands[(k + (0 if sx < 0 else 4)) % 7], "glow", y0=y).xf((sx * 1.12, 0, 0.36)))
                m.add(box(0.22, 0.05, 0.02, lo if not bands else bands[(k + 2) % 7], "glow", y0=y + 0.16).xf((sx * 1.12, 0, 0.36)))
        # keystone crystal: a faceted diamond at the top of the ring, with a white-hot heart
        ky = CY + R1 + 0.05
        m.add(box(0.36, 0.36, 0.42, mid if not bands else bands[4], "glow").xf((0, ky, 0.08), rot=(0, 0, PI / 4)))
        m.add(box(0.16, 0.16, 0.46, hi, "glow").xf((0, ky, 0.1), rot=(0, 0, PI / 4)))
        # crystal tips on the crown spikes
        for k in range(5):
            am = PI * (k + 1) / 6
            if k == 2:
                continue   # the middle spike carries the keystone
            L = 0.55 + (0.25 if k in (1, 3) else 0.0)
            bx, by = math.cos(am) * (R1 - 0.05 + L), CY + math.sin(am) * (R1 - 0.05 + L)
            col = bands[k + 1] if bands else (mid if k % 2 else lo)
            m.add(K.beam((bx, by, 0), (bx + math.cos(am) * 0.28, by + math.sin(am) * 0.28, 0), 0.16, col, "glow"))
        # the realm's sigil on the plinth front (5 x 5 grid, 0.07 m cells)
        s = 0.07
        for x0, y0, x1, y1 in SIGILS[hue]:
            steps = max(abs(x1 - x0), abs(y1 - y0))
            for t in range(steps + 1):
                gx = x0 + (x1 - x0) * t / max(1, steps); gy = y0 + (y1 - y0) * t / max(1, steps)
                m.add(box(s, s, 0.02, mid if not bands else bands[t % 7], "glow", y0=0.02 + (4 - gy) * s * 0.5).xf(((gx - 2) * s, 0, 0.75)))
        # two glow pebbles on the plinth's top step
        for sx in (-1, 1):
            m.add(sphere(0.06, 5, 3, lo if not bands else bands[2 + sx], "glow").xf((sx * 0.5, 0.2, 0.45)))
        pc.mesh = m
        pc.size = [3.6, 4.9, 1.5]
        return pc

    # ------------------------------------------------------------------ the Gatekeepers' Guild post + braziers
    def guild_kiosk(cx):
        """the Gatekeepers' Guild post: a stone counter with an open ledger and a key rack, a tall pole with a
        guild-blue banner (a key emblem, no text) and a cold-fire lamp hung from an iron crook"""
        pc = Piece("guild_kiosk"); r = K.rng(cx.seed, "guild_kiosk"); m = Mesh()
        st = mix(gloom(cx), cx.c("stone_hi"), 0.15)
        m.add(box(2.4, 0.9, 0.8, st, "stone", y0=0))
        m.add(box(2.6, 0.1, 0.96, mix(st, cx.c("stone_hi"), 0.25), "stone", y0=0.9))
        m.add(box(2.4, 0.2, 0.04, cx.c("cloth"), "paint", y0=0.6).xf((0, 0, 0.41)))           # guild-blue front band
        for k in range(5):   # key-shaped studs on the band
            m.add(box(0.08, 0.08, 0.02, cx.c("flower_gold"), "paint", y0=0.66).xf((-0.9 + k * 0.45, 0, 0.44)))
        m.add(box(0.62, 0.05, 0.42, cx.c("plaster_hi"), "paint", y0=1.0).xf((-0.4, 0, 0.05), rot=(0, 0.2, 0)))   # open ledger
        m.add(box(0.02, 0.06, 0.42, cx.c("timber_lo"), "paint", y0=1.0).xf((-0.4, 0, 0.05), rot=(0, 0.2, 0)))
        m.add(box(0.5, 0.5, 0.06, cx.c("timber"), "timber", y0=1.0).xf((0.65, 0, -0.32)))       # key rack board
        for k in range(3):
            m.add(box(0.05, 0.18, 0.03, cx.c("flower_gold"), "paint", y0=1.12).xf((0.5 + k * 0.15, 0, -0.28)))
        # banner pole + guild banner (blue cloth, gold key emblem)
        m.add(cylinder(0.06, 0.05, 3.4, 6, cx.c("timber_lo"), "timber", y0=0).xf((-1.45, 0, -0.1)))
        m.add(box(0.06, 1.3, 0.8, cx.c("cloth"), "paint", y0=1.8).xf((-1.45, 0, 0.32)))
        m.add(box(0.07, 0.5, 0.12, cx.c("flower_gold"), "paint", y0=2.3).xf((-1.45, 0, 0.32)))
        m.add(box(0.07, 0.12, 0.3, cx.c("flower_gold"), "paint", y0=2.3).xf((-1.45, 0, 0.42)))
        m.add(box(0.07, 0.16, 0.16, cx.c("flower_gold"), "paint", y0=2.8).xf((-1.45, 0, 0.32)))
        # cold-fire lamp on an iron crook
        m.add(cylinder(0.05, 0.04, 2.2, 6, cx.c("shadow"), "paint", y0=0).xf((1.35, 0, -0.1)))
        m.add(K.beam((1.35, 2.2, -0.1), (1.35, 2.25, 0.35), 0.05, cx.c("shadow"), "paint"))
        m.add(box(0.26, 0.32, 0.26, COLD, "glow", y0=1.82).xf((1.35, 0, 0.35)))
        m.add(box(0.12, 0.18, 0.12, COLD_HI, "glow", y0=1.89).xf((1.35, 0, 0.35)))
        m.add(box(0.34, 0.06, 0.34, cx.c("shadow"), "paint", y0=2.14).xf((1.35, 0, 0.35)))
        pc.markers["lamps"].append([1.35, 1.98, 0.4]); pc.markers["lamp_color"] = COLD; pc.markers["lamp_fixed"] = 0.5
        pc.blockers.append([-1.55, -0.5, 1.45, 0.5])
        pc.mesh = m.ao(0, 3.4, 0.2)
        pc.size = [3.0, 3.4, 1.0]
        return pc

    def rift_brazier(cx, name, cols):
        """a stone bowl on a fluted pedestal holding jagged neon flame (cold-fire blue, violet or red)"""
        pc = Piece(name); r = K.rng(cx.seed, name); m = Mesh()
        st = mix(gloom(cx), cx.c("stone_hi"), 0.12)
        m.add(box(0.7, 0.12, 0.7, mix(st, cx.c("stone_lo"), 0.2), "stone", y0=0))
        m.add(cylinder(0.18, 0.15, 0.7, 6, st, "stone", y0=0.12))
        m.add(cylinder(0.24, 0.46, 0.26, 8, mix(st, cx.c("ink"), 0.15), "stone", y0=0.82))
        m.add(cylinder(0.4, 0.4, 0.03, 8, cols[2], "glow", y0=1.06))   # coals
        hi, mid, lo = cols
        for k in range(8):   # flame tongues: pointed cones leaning out, tallest in the middle, white-hot cores
            a = 2 * PI * k / 7
            rr = 0.0 if k == 0 else 0.2
            x, z = math.cos(a) * rr, math.sin(a) * rr
            h = 0.85 if k == 0 else r.uniform(0.35, 0.6)
            lean = 0.0 if k == 0 else 0.22
            m.add(cylinder(0.12 if k == 0 else 0.09, 0.0, h, 4, mid if k % 3 else lo, "glow", caps=False, y0=1.06)
                  .xf((x, 0, z), rot=(math.sin(a) * lean, r.uniform(0, PI), -math.cos(a) * lean)))
            if k == 0 or k % 2:
                m.add(cylinder(0.05, 0.0, h * 0.6, 4, hi, "glow", caps=False, y0=1.06).xf((x * 0.8, 0, z * 0.8 + 0.06), rot=(0, r.uniform(0, PI), 0)))
        pc.markers["lamps"].append([0, 1.5, 0]); pc.markers["lamp_color"] = mid; pc.markers["lamp_fixed"] = 0.55
        pc.markers["lamp_range"] = 5.0
        pc.blockers.append([-0.35, -0.35, 0.35, 0.35])
        pc.mesh = m.ao(0, 1.9, 0.2)
        pc.size = [0.9, 1.9, 0.9]
        return pc

    out = {"bifrost_plaza": bifrost_plaza, "bifrost_bridge": bifrost_bridge, "bifrost_landing": bifrost_landing,
           "skiff_keel": skiff_keel, "realm_arch": realm_arch, "guild_kiosk": guild_kiosk,
           "rift_brazier_cold": lambda cx: rift_brazier(cx, "rift_brazier_cold", (COLD_HI, COLD, COLD_LO)),
           "rift_brazier_violet": lambda cx: rift_brazier(cx, "rift_brazier_violet", (VIOLET_HI, VIOLET, VIOLET_LO)),
           "rift_brazier_red": lambda cx: rift_brazier(cx, "rift_brazier_red", (RED_HI, RED, RED_LO))}
    for h in SIGILS:
        out[f"realm_glow_{h}"] = (lambda hh: (lambda cx: realm_glow(cx, hh)))(h)
    return out
