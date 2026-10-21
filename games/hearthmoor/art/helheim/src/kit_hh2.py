"""Helheim kit additions per story/helheim.md 2.2-2.5, 7 (Art seat 2026-10-21). Neon (#a45cf0 violet, #3fb8ff cold fire, #d6b8ff lilac orbs, realm lantern hues,
#e8321e danger red) only on the 'glow' / 'window' materials."""
import math
PI = math.pi
VIO, VIO_D, CF, CF_HI, LIL, RED = "#a45cf0", "#3a2458", "#3fb8ff", "#e8f6ff", "#d6b8ff", "#e8321e"
STONE, STONE_HI, STONE_LO = "#6e6a86", "#9894ae", "#4a4662"
BONE, BONE_SH = "#e6dfcc", "#b8ae98"
WOOD, WOOD_HI, WOOD_LO = "#4e4048", "#6e5a5e", "#3a3038"
IRON = "#3e3c50"
WATER = "#2a2446"
REALMS = [("alfheim", VIO), ("svartalfheim", "#ffb24a"), ("jotunheim", "#bfe8ff"), ("muspelheim", "#ff7a2a"), ("niflheim", CF), ("asgard", "#ffc85a"),
          ("vanaheim", "#5ee08a"), ("fallen_ally", None)]


def pieces(K):
    box, cylinder, sphere, mix, Piece, Mesh, prism_x = K.box, K.cylinder, K.sphere, K.mix, K.Piece, K.Mesh, K.prism_x

    def lamp(pc, pos, col, rng_, fixed=0.5):
        pc.markers["lamps"].append(list(pos)); pc.markers["lamp_color"] = col; pc.markers["lamp_range"] = rng_; pc.markers["lamp_fixed"] = fixed

    def keep(pc, fp, radius, note):
        pc.markers["keep_clear"] = {"footprint_m": fp, "radius_m": radius, "note": note}

    def fin(pc, m, size, block=None, ao=True):
        pc.mesh = m.ao(0, size[1] + .2, 0.15) if ao else m; pc.size = size
        if block:
            pc.blockers.append(block)
        return pc

    def black_lake(cx):
        r = K.rng(cx.seed, "bl"); m = Mesh(); pc = Piece("black_lake")
        m.add(box(2.0, 0.02, 2.0, WATER, "paint", y0=-0.12))
        for _ in range(3):
            x, z = r.uniform(-.8, .8), r.uniform(-.8, .8)
            m.add(box(r.uniform(.3, .7), 0.005, 0.04, VIO if r.random() < .6 else LIL, "glow", y0=-0.1).xf((x, 0, z)))
        pc.mesh = m; pc.size = [2, 0.02, 2]; pc.markers["water"] = True; return pc

    def pebble_shore(cx):
        r = K.rng(cx.seed, "ps"); m = Mesh(); pc = Piece("pebble_shore")
        m.add(box(2.0, 0.02, 2.0, STONE_LO, "paint", y0=0))
        for _ in range(9):
            m.add(sphere(r.uniform(.06, .12), 5, 3, mix(STONE, STONE_HI, r.random()), "stone", squash=(1, .4, 1)).xf((r.uniform(-.9, .9), 0.02, r.uniform(-.9, .9))))
        pc.mesh = m; pc.size = [2, 0.1, 2]; return pc

    def lantern_bridge(cx):
        """the Lantern Bridge: 10 m deck over the lake (runs along x), 8 lantern posts: 7 realms + the fallen ally's (dark, no name)"""
        pc = Piece("lantern_bridge"); m = Mesh()
        m.add(box(10.0, 0.25, 2.4, WOOD, "timber", y0=0.0)); m.add(box(10.0, 0.06, 2.5, WOOD_HI, "timber", y0=0.25))
        for sz in (-1.2, 1.2):
            m.add(box(10.0, 0.08, 0.08, WOOD_HI, "timber", y0=0.95).xf((0, 0, sz)))
        for k, (nm, col) in enumerate(REALMS):
            x = -4.4 + k * (8.8 / 7); z = -1.2 if k % 2 == 0 else 1.2
            m.add(cylinder(0.06, 0.06, 1.5, 6, IRON, "paint", y0=0.25).xf((x, 0, z)))
            m.add(box(0.26, 0.32, 0.26, IRON, "paint", y0=1.75).xf((x, 0, z)))
            m.add(box(0.18, 0.24, 0.27, col or "#2e2a3c", "glow" if col else "paint", y0=1.79).xf((x, 0, z)))
            if col:
                lamp(pc, (x, 1.9, z), col, 3.0)
        pc = fin(pc, m, [10.0, 2.1, 2.5], None); pc.kind = "walkable_bridge"
        pc.markers["realm_lanterns"] = [{"realm": n, "x": round(-4.4 + k * (8.8 / 7), 2), "z": -1.2 if k % 2 == 0 else 1.2, "lit_color": c} for k, (n, c) in enumerate(REALMS)]
        pc.markers["note"] = "Lantern Bridge [0,1.0] across the black lake; deck walkable at y 0.31; lanterns light per arrival rules 1.1 (dark = unlit glass); keep the deck clear"
        return pc

    def crooked_house(cx):
        pc = Piece("crooked_house"); m = Mesh()
        m.add(box(3.6, 3.2, 3.0, STONE, "stone", y0=0).xf((0, 0, 0), rot=(0, 0, 0.03)))
        m.add(prism_x(3.9, [(-1.7, 3.1), (1.7, 3.1), (0.2, 5.0)], WOOD_LO, "timber").xf((0, 0, 0), rot=(0, PI / 2, 0.05)))
        for sx in (-1, 1):
            m.add(box(0.6, 0.8, 0.05, VIO, "window", y0=1.4).xf((sx * 0.9, 0, 1.52)))
        m.add(box(0.9, 1.7, 0.05, WOOD, "timber", y0=0).xf((0, 0, 1.52)))
        pc = fin(pc, m, [3.9, 5.0, 3.1], [-1.8, -1.5, 1.8, 1.5])
        for sx in (-1, 1):
            lamp(pc, (sx * 0.9, 1.8, 1.9), VIO, 3.0, 1.0)
        pc.markers["note"] = "crooked Gloamhaven house; violet window lights (r 3 m, steady); 1.5 m clear at the door"; return pc

    def last_hearth_inn(cx):
        pc = Piece("last_hearth_inn"); m = Mesh()
        m.add(box(6.0, 3.6, 4.0, STONE, "stone", y0=0)); m.add(prism_x(6.4, [(-2.2, 3.5), (2.2, 3.5), (0, 5.6)], WOOD_LO, "timber").xf((0, 0, 0), rot=(0, PI / 2, 0)))
        for sx in (-2.0, 2.0):
            m.add(box(1.0, 1.0, 0.05, VIO, "window", y0=1.4).xf((sx, 0, 2.02)))
        m.add(box(1.2, 2.0, 0.05, WOOD, "timber", y0=0).xf((0, 0, 2.02))); m.add(box(1.4, 0.4, 0.1, WOOD_HI, "timber", y0=2.4).xf((0, 0, 2.1)))
        m.add(cylinder(0.12, 0.12, 0.3, 6, CF, "glow", y0=2.0).xf((0.9, 0, 2.2)))
        pc = fin(pc, m, [6.4, 5.6, 4.1], [-3.0, -2.0, 3.0, 2.0])
        for sx in (-2.0, 2.0):
            lamp(pc, (sx, 1.9, 2.4), VIO, 3.0, 1.0)
        lamp(pc, (0.9, 2.2, 2.5), CF, 3.5)
        keep(pc, [-1.2, 2.0, 1.2, 4.0], 2.0, "inn door"); pc.markers["note"] = "The Last Hearth Inn [-7.5,-2] (Hettie): door faces +z; the empty chair is inside (interior scene)"; return pc

    def willow_orb(cx):
        pc = Piece("willow_orb"); m = Mesh(); r = K.rng(cx.seed, "wo")
        m.add(cylinder(0.25, 0.18, 2.6, 7, WOOD_LO, "timber", y0=0))
        m.add(sphere(1.5, 8, 5, "#3e4a4e", "leaf", squash=(1, .7, 1)).xf((0, 3.0, 0)))
        for k in range(10):
            a = k * PI / 5; rr = 1.35
            y0 = r.uniform(1.4, 2.2)
            m.add(box(0.03, 3.0 - y0, 0.03, "#4e5e5a", "leaf", y0=y0).xf((math.cos(a) * rr, 0, math.sin(a) * rr)))
        for k in range(4):
            a = k * PI / 2 + .4
            m.add(sphere(0.13, 6, 4, LIL, "glow").xf((math.cos(a) * 1.2, 1.7 + (k % 2) * .3, math.sin(a) * 1.2)))
        pc = fin(pc, m, [3.0, 4.1, 3.0], [-.3, -.3, .3, .3]); lamp(pc, (0, 1.8, 0), LIL, 3.5, 0.0)
        pc.markers["note"] = "willow with lilac glow orbs (#d6b8ff); orbs bob = fx glow_orb_lilac; trunk blocks only 0.6 m"; return pc

    def jetty(cx):
        pc = Piece("jetty"); m = Mesh()
        for k in range(8):
            m.add(box(2.0, 0.08, 0.45, WOOD_HI if k % 2 else WOOD, "timber", y0=0.22).xf((0, 0, -1.75 + k * 0.5)))
        for sx in (-0.9, 0.9):
            for sz in (-1.8, 1.8):
                m.add(cylinder(0.08, 0.08, 0.5, 6, WOOD_LO, "timber", y0=-0.2).xf((sx, 0, sz)))
        m.add(cylinder(0.05, 0.05, 1.2, 6, IRON, "paint", y0=0.3).xf((0.9, 0, -1.8))); m.add(box(0.2, 0.25, 0.2, CF, "glow", y0=1.5).xf((0.9, 0, -1.8)))
        pc = fin(pc, m, [2.0, 1.8, 4.0]); lamp(pc, (0.9, 1.6, -1.8), CF, 3.5); pc.kind = "walkable"
        pc.markers["note"] = "jetty [0,-2] (hh_shore) runs along z into the lake; Lantern-Boat Night / fallen-ally scene on the end; deck clear"; return pc

    def lantern_boat(cx):
        pc = Piece("lantern_boat"); m = Mesh()
        m.add(prism_x(0.8, [(-1.1, 0.0), (1.1, 0.0), (1.4, 0.35), (-1.4, 0.35)], WOOD, "timber").xf((0, 0, 0), rot=(0, PI / 2, 0)))
        m.add(cylinder(0.03, 0.03, 0.9, 5, IRON, "paint", y0=0.3).xf((0, 0, -0.9))); m.add(sphere(0.12, 6, 4, VIO, "glow").xf((0, 1.25, -0.9)))
        pc = fin(pc, m, [0.9, 1.4, 2.8]); lamp(pc, (0, 1.25, -0.9), VIO, 2.5)
        pc.markers["note"] = "lantern-boat, floats at y -0.05 on black_lake; drifts (runtime); one carries the living-lamp in Hel's Leave"; return pc

    def name_cage(cx):
        pc = Piece("name_cage"); m = Mesh()
        m.add(cylinder(0.55, 0.55, 0.12, 10, IRON, "paint", y0=0)); m.add(cylinder(0.55, 0.0, 0.5, 10, IRON, "paint", y0=1.8))
        for k in range(10):
            a = k * PI / 5
            m.add(box(0.04, 1.7, 0.04, VIO, "glow", y0=0.1).xf((math.cos(a) * 0.52, 0, math.sin(a) * 0.52)))
        m.add(sphere(0.25, 7, 5, LIL, "glow").xf((0, 0.95, 0)))
        pc = fin(pc, m, [1.1, 2.3, 1.1], [-.55, -.55, .55, .55], ao=False); lamp(pc, (0, 1.0, 0), VIO, 4.0)
        pc.markers["note"] = "name-cage os_n1..3 / O8 fallen-ally cage: glowing violet bars of bound names; break = fx cage_break; 1.5 m clear"; return pc

    def lich_bier(cx):
        pc = Piece("lich_bier"); m = Mesh()
        m.add(box(2.4, 0.8, 1.1, BONE_SH, "stone", y0=0)); m.add(box(2.5, 0.08, 1.2, BONE, "paint", y0=0.8))
        m.add(box(0.5, 0.04, 0.02, VIO, "glow", y0=0.5).xf((0, 0, 0.56)))
        pc = fin(pc, m, [2.5, 0.9, 1.2], [-1.25, -.6, 1.25, .6]); lamp(pc, (0, 0.6, 0.8), VIO, 2.0)
        pc.markers["note"] = "O7 bier: a lich sleeps on top (sprite at y 0.88); light-meter sneak room"; return pc

    def soul_glass(cx):
        pc = Piece("soul_glass"); m = Mesh()
        m.add(cylinder(0.25, 0.3, 0.6, 8, STONE, "stone", y0=0)); m.add(sphere(0.18, 6, 5, LIL, "glow", squash=(.7, 1.3, .7)).xf((0, 0.85, 0)))
        pc = fin(pc, m, [0.6, 1.1, 0.6], ao=False); lamp(pc, (0, 0.85, 0), LIL, 2.0)
        pc.markers["note"] = "soul-glass pickup sgl_1..3 (O3, O4, O7) on a small plinth"; return pc

    def heart_slot(cx):
        pc = Piece("heart_slot"); m = Mesh()
        m.add(box(1.2, 0.3, 1.2, STONE_LO, "stone", y0=0)); m.add(cylinder(0.32, 0.32, 0.05, 10, "#5a1a2a", "paint", y0=0.3))
        m.add(sphere(0.26, 7, 5, RED, "glow").xf((0, 0.58, 0)))
        pc = fin(pc, m, [1.2, 0.9, 1.2], ao=False); lamp(pc, (0, 0.6, 0), RED, 2.0)
        pc.markers["note"] = "O4 Garnet Gallery: slot for a rolling glass heart (sphere = runtime prop; red = puzzle colour here, not danger)"; return pc

    def rhythm_door(cx):
        pc = Piece("rhythm_door"); m = Mesh()
        m.add(box(3.2, 4.2, 0.6, BONE_SH, "stone", y0=0)); m.add(box(2.0, 3.4, 0.1, IRON, "paint", y0=0).xf((0, 0, 0.32)))
        for k in range(5):
            m.add(box(0.24, 0.24, 0.02, VIO, "glow", y0=2.6).xf((-0.8 + k * 0.4, 0, 0.38)))
        pc = fin(pc, m, [3.2, 4.2, 0.6], [-1.6, -.3, 1.6, .3]); lamp(pc, (0, 2.6, 0.8), VIO, 3.5)
        keep(pc, [-1.2, .3, 1.2, 2.8], 2.5, "door"); pc.markers["note"] = "O6 Choir Loft rhythm door: 5 hum notes light in turn"; return pc

    def quillon_desk(cx):
        pc = Piece("quillon_desk"); m = Mesh()
        m.add(box(1.8, 0.1, 0.9, WOOD_HI, "timber", y0=0.8))
        for sx in (-0.8, 0.8):
            m.add(box(0.1, 0.8, 0.8, WOOD, "timber", y0=0).xf((sx, 0, 0)))
        m.add(box(0.5, 0.12, 0.35, BONE, "paint", y0=0.9).xf((-0.3, 0, 0))); m.add(cylinder(0.05, 0.05, 0.25, 6, CF, "glow", y0=0.9).xf((0.6, 0, -0.2)))
        pc = fin(pc, m, [1.8, 1.2, 0.9], [-.9, -.45, .9, .45]); lamp(pc, (0.6, 1.2, -0.2), CF, 2.5)
        pc.markers["note"] = "Quillon's desk [-5,-3] (hh_archive): books + a cold-fire candle"; return pc

    def archive_shelf(cx):
        pc = Piece("archive_shelf"); m = Mesh(); r = K.rng(cx.seed, "as")
        m.add(box(2.0, 4.0, 0.5, WOOD_LO, "timber", y0=0))
        for row in range(5):
            for k in range(7):
                m.add(box(0.2, 0.55, 0.3, mix(WOOD_HI, "#5a4a6a", r.random()), "paint", y0=0.2 + row * 0.75).xf((-0.75 + k * 0.25, 0, 0.12)))
        return fin(pc, m, [2.0, 4.0, 0.5], [-1, -.25, 1, .25])

    def floating_candles(cx):
        pc = Piece("floating_candles"); m = Mesh(); r = K.rng(cx.seed, "fc")
        for _ in range(5):
            x, y, z = r.uniform(-1, 1), r.uniform(2.4, 3.2), r.uniform(-1, 1)
            m.add(cylinder(0.04, 0.04, 0.16, 5, BONE, "paint", y0=y).xf((x, 0, z))); m.add(sphere(0.05, 5, 3, CF, "glow").xf((x, y + 0.22, z)))
        pc.mesh = m; pc.size = [2, 3.4, 2]; lamp(pc, (0, 2.8, 0), CF, 4.0)
        pc.markers["note"] = "floating cold-fire candles (hh_archive), y 2.4-3.2; flicker = fx cold_flame small"; return pc

    def chain_anchor(cx):
        pc = Piece("chain_anchor"); m = Mesh()
        m.add(box(0.6, 0.6, 0.3, BONE_SH, "stone", y0=1.6))
        for k in range(6):
            m.add(box(0.08, 0.16, 0.08, VIO, "glow", y0=1.6 - k * 0.2).xf((0, 0, 0.25 + k * 0.1)))
        pc = fin(pc, m, [0.6, 2.2, 1.0], ao=False); lamp(pc, (0, 1.2, 0.6), VIO, 2.5)
        pc.markers["note"] = "O9 wall anchor of a name-chain (P1 lash: red telegraph_line from here); breakable"; return pc

    def bone_niches(cx):
        pc = Piece("bone_niches"); m = Mesh()
        m.add(box(2.0, 3.6, 0.5, BONE_SH, "stone", y0=0))
        for row in range(3):
            for k in range(3):
                m.add(box(0.44, 0.6, 0.06, "#8a8070", "paint", y0=0.5 + row * 1.0).xf((-0.6 + k * 0.6, 0, 0.24)))
                m.add(sphere(0.12, 6, 4, BONE, "paint").xf((-0.6 + k * 0.6, 0.75 + row * 1.0, 0.26)))
        return fin(pc, m, [2.0, 3.6, 0.5], [-1, -.25, 1, .25])

    def reeds(cx):
        pc = Piece("reeds"); m = Mesh(); r = K.rng(cx.seed, "rd")
        for _ in range(12):
            x, z, h = r.uniform(-.8, .8), r.uniform(-.8, .8), r.uniform(.7, 1.3)
            m.add(box(0.03, h, 0.03, "#4e5e5a", "leaf", y0=0).xf((x, 0, z)))
        pc.mesh = m; pc.size = [1.8, 1.3, 1.8]; pc.markers["note"] = "reed bank (hh_shore): ls_spring + a Ledger page hide here"; return pc

    BW, BW_HI, BW_LO, BW_SH = "#d4c9b0", "#e2d8c2", "#b4a88e", "#958a74"   # soft warm off-white bone (not glaring)

    def ossuary_wall(cx):
        pc = Piece("ossuary_wall"); m = Mesh()
        m.add(box(2.0, 4.0, 0.5, BW_LO, "stone", y0=0)); m.add(box(2.1, 0.3, 0.6, BW_HI, "stone", y0=4.0)); m.add(box(2.1, 0.25, 0.6, BW_SH, "stone", y0=0))
        for k in range(3):
            m.add(box(0.5, 0.36, 0.06, BW, "stone", y0=1.0 + k * 0.9).xf((-0.5 + (k % 2), 0, 0.26)))
        return fin(pc, m, [2.0, 4.3, 0.6])

    def ossuary_door(cx):
        pc = Piece("ossuary_door"); m = Mesh()
        for sx in (-1, 1):
            m.add(box(0.9, 5.4, 1.0, BW_LO, "stone", y0=0).xf((sx * 2.2, 0, 0)))
        m.add(box(5.4, 0.8, 1.0, BW_HI, "stone", y0=5.2)); m.add(box(3.4, 5.2, 0.3, BW_SH, "stone", y0=0).xf((0, 0, -0.1)))
        for k in range(3):
            x = -1.1 + k * 1.1
            m.add(sphere(0.22, 7, 4, VIO, "glow", squash=(1, 1, .35)).xf((x, 2.8, 0.1))); m.add(sphere(0.1, 6, 3, LIL, "glow", squash=(1, 1, .5)).xf((x, 2.8, 0.15)))
        pc = fin(pc, m, [5.4, 6.0, 1.0]); lamp(pc, (0, 2.8, 0.9), VIO, 5.0)
        pc.markers["rune_locks"] = 3; keep(pc, [-1.7, .5, 1.7, 3.5], 3.0, "door"); return pc

    fns = [ossuary_wall, ossuary_door, reeds, black_lake, pebble_shore, lantern_bridge, crooked_house, last_hearth_inn, willow_orb, jetty, lantern_boat, name_cage, lich_bier, soul_glass, heart_slot,
           rhythm_door, quillon_desk, archive_shelf, floating_candles, chain_anchor, bone_niches]
    return {f.__name__: f for f in fns}
