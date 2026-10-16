"""Jotunheim kit pieces (original; Hearthmoor Art seat staging, 2026-10-16). Built with the repo's kit.py / meshlib like kit_svart.py.
 Stonehollow: snow_floor, ice_lake, stone_ledge (1.2 m), stone_stair (6 steps, 1.2 m), snow_mound (1.3 m), longhouse (giant doors), rune_standing_stone,
              lift_stone, cold_brazier, goat_fence, giant_stool, glow_orb_chain, fur_stall
 Rime Caves : ice_floor, ice_wall, glow_ice_pool, icicle_cluster (hanging, glow tips), ice_crystal_cluster, frost_rune_pillar
 Warm accent: warm_lantern
 Titan's Barrow: barrow_floor, barrow_wall, barrow_door (6 m, 3 rune locks), shield_rack, ice_throne (boss_stand), rune_bridge, rune_brazier
Neon hexes only on the 'glow' material (cold fire, runes, crystal tips, water, orbs). Placement notes live in kit.json markers."""
import math
PI = math.pi
# palette (lifted for luma: black stone reads as dark blue-grey, snow keeps a blue shadow)
STONE, STONE_HI, STONE_LO = "#2c3140", "#444c60", "#1c202c"
SNOW, SNOW_SH, SNOW_HI = "#c8d6ec", "#8ea6cc", "#eef6ff"
TURF, TURF_HI = "#4a7048", "#6a9460"
TIMBER, TIMBER_HI, TIMBER_LO = "#6a4a34", "#8a6444", "#42301f"
IRON, IRON_HI = "#4a4e5c", "#7a8096"
WARM = "#ffc866"
CF, CF_HI, CF_LO = "#3fb8ff", "#e8f6ff", "#1c62d8"          # cold fire
RUNE, ORB = "#7fd4ff", "#9fe8ff"
POOL, POOL_HI, POOL_LO = "#2fd0d0", "#a8fff0", "#16807f"
ICE, ICE_HI, ICE_DEEP = "#a8d8f4", "#e4f6ff", "#5a98d0"
AUR_G, AUR_V = "#3fe0a0", "#a45cf0"
FUR = "#d8cdb8"


def pieces(K):
    box, cylinder, sphere, beam, mix, Piece, Mesh, prism_x = K.box, K.cylinder, K.sphere, K.beam, K.mix, K.Piece, K.Mesh, K.prism_x

    def lamp(pc, pos, col, rng_, fixed=0.5):
        pc.markers["lamps"].append(list(pos)); pc.markers["lamp_color"] = col; pc.markers["lamp_range"] = rng_; pc.markers["lamp_fixed"] = fixed

    def floor_tile(pc, name, seed, c0, c1, seam, flecks=None):
        r = K.rng(seed, name); m = Mesh()
        for i in range(4):
            for j in range(4):
                x0, z0 = -1 + i * 0.5, -1 + j * 0.5
                m.quad((x0, 0, z0 + 0.5), (x0 + 0.5, 0, z0 + 0.5), (x0 + 0.5, 0, z0), (x0, 0, z0), mix(c0, c1, r.uniform(0, 0.8)), mat="paint")
        if seam:
            m.add(box(2.0, 0.006, 0.03, seam, "glow", y0=0).xf((0, 0, 0.5)))
            m.add(box(0.03, 0.006, 1.0, seam, "glow", y0=0).xf((0.5, 0, -0.5)))
        for k in range(flecks or 0):
            m.add(sphere(r.uniform(0.04, 0.09), 5, 3, STONE_HI, "stone", squash=(1.3, 0.5, 1)).xf((r.uniform(-.9, .9), 0.0, r.uniform(-.9, .9))))
        pc.mesh = m; pc.size = [2, 0.02, 2]; return pc

    # ======================================================================= Stonehollow
    def snow_floor(cx):
        return floor_tile(Piece("snow_floor"), "snow_floor", cx.seed, SNOW, SNOW_SH, None, 5)

    def ice_lake(cx):
        pc = Piece("ice_lake"); r = K.rng(cx.seed, "lake"); m = Mesh()
        for i in range(8):
            for j in range(8):
                x0, z0 = -2 + i * 0.5, -2 + j * 0.5
                m.quad((x0, 0.02, z0 + 0.5), (x0 + 0.5, 0.02, z0 + 0.5), (x0 + 0.5, 0.02, z0), (x0, 0.02, z0), mix(ICE, ICE_HI, r.uniform(0, 0.7)), mat="paint")
        for (x, z, w, d) in ((-1.2, -.8, 1.6, .05), (.4, .6, .05, 1.8), (.9, -1.0, 1.2, .05), (-.4, 1.2, 1.4, .05)):
            m.add(box(w, 0.008, d, POOL, "glow", y0=0.022).xf((x, 0, z)))
        for (x, z) in ((-.8, .2), (1.1, .4), (-.2, -1.4)):
            m.add(sphere(0.35, 8, 3, POOL_HI, "glow", squash=(1.6, 0.03, 1.1)).xf((x, 0.03, z)))
        pc.mesh = m; lamp(pc, (0, 0.5, 0), POOL, 5.0); pc.size = [4, 0.04, 4]; return pc

    def stone_ledge(cx):
        pc = Piece("stone_ledge"); r = K.rng(cx.seed, "ledge"); m = Mesh()
        H = 1.2
        for k in range(3):
            m.add(box(3.0, 0.4, 2.0, mix(STONE, STONE_HI, r.uniform(0, .6)), "stone", y0=k * 0.4))
        m.add(box(3.1, 0.14, 2.1, SNOW, "paint", y0=H))
        for k in range(7):
            m.add(sphere(0.2, 6, 3, SNOW_HI, "paint", squash=(1.6, .5, 1)).xf((-1.3 + k * .43, H + .1, 1.0 + r.uniform(-.1, .05))))
        m.add(box(2.6, 0.05, 0.02, RUNE, "glow", y0=0.55).xf((0, 0, 1.01)))
        for k in range(5):
            m.add(box(0.07, 0.16, 0.02, CF_HI, "glow", y0=0.45).xf((-1.0 + k * .5, 0, 1.02)))
        pc.mesh = m.ao(0, 1.4, 0.2); lamp(pc, (0, 0.6, 1.3), RUNE, 3.0); pc.size = [3.1, 1.34, 2.1]
        pc.blockers.append([-1.5, -1.0, 1.5, 1.0])
        pc.markers["height_m"] = 1.34; pc.markers["ledge_edge"] = [[-1.5, 1.0], [1.5, 1.0]]
        pc.markers["no_props_within_m"] = 0.8; return pc

    def stone_stair(cx):
        pc = Piece("stone_stair"); m = Mesh()
        n, rise, run, wd = 6, 1.2, 0.5, 2.0
        st = rise / n; L = n * run
        for i in range(n):
            h = st * (i + 1); z1 = L / 2 - i * run; z0 = -L / 2
            m.add(box(wd, h, z1 - z0, mix(STONE, STONE_HI, 0.15 + 0.05 * (i % 2)), "stone", y0=0).xf((0, 0, (z0 + z1) / 2)))
            m.add(box(wd, 0.05, 0.1, SNOW, "paint", y0=h - 0.02).xf((0, 0, z1 - 0.06)))
            m.add(box(0.5, 0.012, 0.02, RUNE, "glow", y0=h - 0.05).xf((0, 0, z1 + 0.002)))
        for sx in (-1, 1):
            prof = [(L / 2 + 0.05, 0), (L / 2 + 0.05, 0.5), (-L / 2, rise + 0.5), (-L / 2, 0)]
            m.add(prism_x(0.3, prof, STONE_HI, "stone").xf((sx * (wd / 2 + 0.15), 0, 0)))
            m.add(box(0.36, 0.1, 0.5, SNOW, "paint", y0=0.5).xf((sx * (wd / 2 + 0.15), 0, L / 2 - 0.1)))
            m.add(cylinder(0.05, 0.05, 0.5, 6, IRON, "paint", y0=0.5).xf((sx * (wd / 2 + 0.15), 0, L / 2 - 0.1)))
            m.add(sphere(0.1, 6, 4, CF, "glow").xf((sx * (wd / 2 + 0.15), 1.05, L / 2 - 0.1)))
        pc.mesh = m.ao(0, 1.8, 0.2); pc.kind = "stairs"; pc.size = [wd + 0.6, rise + 0.5, L]
        pc.stairs = {"width": wd, "rise": rise, "length": L, "steps": n}
        for sx in (-1, 1):
            lamp(pc, (sx * (wd / 2 + 0.15), 1.1, L / 2 - 0.1), CF, 3.0)
        pc.markers["no_props_within_m"] = 1.0; pc.markers["note"] = "keep props, fx and spawns off the stair footprint (+1 m each end)"; return pc

    def snow_mound(cx):
        pc = Piece("snow_mound"); r = K.rng(cx.seed, "mound"); m = Mesh()
        m.add(sphere(1.5, 10, 6, SNOW, "paint", squash=(1.0, 0.9, 0.8), col_bottom=SNOW_SH).xf((0, -0.15, 0)))
        m.add(sphere(0.9, 8, 4, SNOW_HI, "paint", squash=(1.0, 0.5, 0.9)).xf((-0.5, 1.0, -0.1)))
        for (x, z, s) in ((1.0, 0.5, .3), (-1.1, 0.4, .25), (.3, -.9, .28)):
            m.add(sphere(s, 6, 3, STONE_HI, "stone", squash=(1.3, .7, 1)).xf((x, 0.1, z)))
        pc.mesh = m.ao(0, 1.5, 0.15); pc.size = [3.0, 1.3, 2.4]; pc.blockers.append([-1.3, -1.0, 1.3, 1.0]); pc.markers["height_m"] = 1.3; return pc

    def longhouse(cx):
        pc = Piece("longhouse"); r = K.rng(cx.seed, "lh"); m = Mesh()
        Wd, D, WH, RISE = 8.0, 5.0, 5.4, 2.6
        m.add(box(Wd + .3, 1.0, D + .3, STONE, "stone", y0=0))
        for k in range(8):
            m.add(box(1.0, 0.3, 0.1, STONE_HI, "stone", y0=0.2 + (k % 3) * .25).xf((-3.5 + k, 0, D / 2 + .16)))
        m.add(box(Wd, WH - 1.0, D, TIMBER, "timber", y0=1.0))
        for k in range(5):
            m.add(box(0.28, WH - 1.0, 0.1, TIMBER_LO, "timber", y0=1.0).xf((-3.6 + k * 1.8, 0, D / 2 + .06)))
        for y in (2.9, 4.6):
            m.add(box(Wd + .1, 0.14, 0.14, TIMBER_LO, "timber", y0=y).xf((0, 0, D / 2 + .08)))
        # giant door (3.2 x 4.0) with cold-fire rune lintel
        m.add(box(3.2, 4.0, 0.08, TIMBER_LO, "timber", y0=1.0).xf((0, 0, D / 2 + .08)))
        for sx in (-1, 1):
            m.add(box(0.2, 4.2, 0.2, TIMBER_HI, "timber", y0=1.0).xf((sx * 1.7, 0, D / 2 + .12)))
        m.add(box(3.6, 0.25, 0.22, TIMBER_HI, "timber", y0=5.0).xf((0, 0, D / 2 + .12)))
        m.add(box(3.0, 0.07, 0.03, RUNE, "glow", y0=4.75).xf((0, 0, D / 2 + .24)))
        for k in range(6):
            m.add(box(0.09, 0.2, 0.03, CF_HI, "glow", y0=4.62).xf((-1.25 + k * .5, 0, D / 2 + .25)))
        for sx in (-1, 1):
            m.add(box(0.1, 0.7, 0.03, ICE, "paint", y0=2.2).xf((sx * 0.9, 0, D / 2 + .13)))
        # warm windows up the storeys
        for y in (3.1, 4.4):
            for x in (-3.2, -2.2, 2.2, 3.2):
                m.add(box(0.7, 0.7, 0.04, WARM, "window", y0=y).xf((x, 0, D / 2 + .13)))
                m.add(box(0.8, 0.06, 0.08, TIMBER_LO, "timber", y0=y - .06).xf((x, 0, D / 2 + .12)))
        # turf roof with snow, over-hanging
        prof = [(D / 2 + .5, WH - .1), (0, WH + RISE), (-D / 2 - .5, WH - .1)]
        m.add(prism_x(Wd + .8, prof, TURF, "paint"))
        prof2 = [(D / 2 + .5, WH - .1), (D / 2 + .12, WH + .05), (0.15, WH + RISE + .1), (-.15, WH + RISE + .1), (-D / 2 - .12, WH + .05), (-D / 2 - .5, WH - .1), (0, WH + RISE - .1)]
        for k in range(10):
            m.add(sphere(r.uniform(.3, .55), 6, 3, SNOW, "paint", squash=(1.8, .4, 1)).xf((-3.6 + r.uniform(0, 7.2), WH + RISE * .55 + r.uniform(-.5, .6), r.uniform(.3, 1.9))))
        m.add(box(Wd + .8, 0.16, 0.2, SNOW_HI, "paint", y0=WH + RISE - .05))
        for sx in (-1, 1):
            m.add(beam([sx * (Wd / 2 + .4), WH + 0.0, D / 2 + .5], [sx * (Wd / 2 + .4), WH + RISE, 0], 0.18, TIMBER_HI, "timber"))
            m.add(beam([sx * (Wd / 2 + .4), WH + RISE, 0], [sx * (Wd / 2 + .4), WH + 0.0, -D / 2 - .5], 0.18, TIMBER_HI, "timber"))
        # chimney with a cold-fire glow
        m.add(box(0.9, 1.6, 0.9, STONE, "stone", y0=WH + 1.0).xf((2.6, 0, -1.2)))
        m.add(box(0.5, 0.12, 0.5, CF, "glow", y0=WH + 2.55).xf((2.6, 0, -1.2)))
        pc.mesh = m.ao(0, WH + RISE, 0.2)
        lamp(pc, (-2.4, 2.0, D / 2 + .8), CF, 5.0); lamp(pc, (2.4, 2.0, D / 2 + .8), CF, 5.0); lamp(pc, (0, 3.6, D / 2 + .6), WARM, 5.0)
        pc.size = [Wd + .8, WH + RISE, D + 1.0]; pc.blockers.append([-Wd / 2, -D / 2, Wd / 2, D / 2])
        pc.markers["doors"].append({"pos": [0, 0, D / 2 + .2], "w": 3.2, "h": 4.0}); pc.markers["spawn_clear_m"] = 2.5
        pc.markers["note"] = "keep 2.5 m in front of the door clear (spawn / door point)"; return pc

    def rune_standing_stone(cx):
        pc = Piece("rune_standing_stone"); r = K.rng(cx.seed, "rss"); m = Mesh()
        m.add(cylinder(0.9, 0.7, 0.3, 7, STONE_HI, "stone", y0=0))
        m.add(cylinder(0.55, 0.38, 4.0, 6, STONE, "stone", y0=0.3))
        m.add(cylinder(0.38, 0.0, 0.5, 6, STONE_HI, "stone", y0=4.3))
        for k in range(6):
            y = 0.9 + k * 0.5
            m.add(box(0.28, 0.05, 0.02, RUNE if k % 2 else CF_HI, "glow", y0=y).xf((0, 0, 0.5 - k * .02)))
            m.add(box(0.05, 0.22, 0.02, CF, "glow", y0=y - .1).xf((0.08 * (1 if k % 2 else -1), 0, 0.5 - k * .02)))
        m.add(sphere(.45, 7, 3, SNOW, "paint", squash=(1.1, .35, 1.0)).xf((0, 4.3, 0)))
        pc.mesh = m.ao(0, 4.6, 0.15); lamp(pc, (0, 2.4, 0.8), RUNE, 5.0); pc.size = [1.8, 4.7, 1.8]
        pc.blockers.append([-0.7, -0.7, 0.7, 0.7]); pc.markers["rune_pulse_s"] = 3.0; return pc

    def lift_stone(cx):
        pc = Piece("lift_stone"); m = Mesh()
        m.add(cylinder(0.8, 0.7, 0.18, 8, STONE_HI, "stone", y0=0))
        m.add(sphere(0.55, 7, 4, STONE, "stone", squash=(1.1, 0.8, 1.0)).xf((0, 0.5, 0)))
        for k in range(8):
            a = k * 2 * PI / 8
            m.add(box(0.1, 0.012, 0.18, RUNE, "glow", y0=0.17).xf((math.cos(a) * 0.74, 0, math.sin(a) * 0.74), rot=(0, -a + PI / 2, 0)))
        m.add(box(0.3, 0.02, 0.02, CF_HI, "glow", y0=0.9).xf((0, 0, 0.3)))
        pc.mesh = m.ao(0, 1.2, 0.15); lamp(pc, (0, 0.7, 0.5), RUNE, 3.0); pc.size = [1.6, 1.1, 1.6]
        pc.blockers.append([-.6, -.6, .6, .6]); pc.markers["interact"] = "lift (E / A on the glow): Welcome Ring"; return pc

    def cold_flame(m, y, s=1.0):
        m.add(sphere(0.32 * s, 7, 4, CF, "glow", squash=(1, 0.5, 1)).xf((0, y, 0)))
        m.add(cylinder(0.26 * s, 0.0, 0.9 * s, 7, CF, "glow", y0=y))
        m.add(cylinder(0.14 * s, 0.0, 0.6 * s, 6, CF_HI, "glow", y0=y))

    def cold_brazier(cx, name="cold_brazier", H=2.2, sc=1.0):
        pc = Piece(name); m = Mesh()
        for k in range(3):
            a = k * 2 * PI / 3 + .3
            m.add(beam([0, H * .82, 0], [math.cos(a) * .55 * sc, 0, math.sin(a) * .55 * sc], 0.1 * sc, IRON, "paint"))
        m.add(cylinder(0.5 * sc, 0.62 * sc, 0.3 * sc, 8, IRON_HI, "paint", y0=H * .8))
        m.add(cylinder(0.55 * sc, 0.5 * sc, 0.1, 8, IRON, "paint", y0=H * .8 + .3 * sc))
        cold_flame(m, H * .8 + .3 * sc, sc * 1.2)
        for sx in (-1, 1):
            m.add(box(.04, .2, .02, RUNE, "glow", y0=H * .8 + .05).xf((sx * .3 * sc, 0, .58 * sc)))
        pc.mesh = m.ao(0, H + 1.2, 0.1); lamp(pc, (0, H * .8 + .9, 0.1), CF, 6.0 * sc); pc.size = [1.3 * sc, H + 1.2, 1.3 * sc]
        pc.blockers.append([-.4 * sc, -.4 * sc, .4 * sc, .4 * sc]); return pc

    def goat_fence(cx):
        pc = Piece("goat_fence"); m = Mesh()
        for x in (-1, 0, 1):
            m.add(cylinder(0.1, 0.09, 1.2, 6, TIMBER_HI, "timber", y0=0).xf((x, 0, 0)))
            m.add(sphere(.12, 5, 3, SNOW, "paint", squash=(1, .5, 1)).xf((x, 1.2, 0)))
        for y in (0.4, 0.85):
            m.add(box(2.1, 0.12, 0.08, TIMBER, "timber", y0=y))
        pc.mesh = m; pc.size = [2.2, 1.3, 0.2]; pc.blockers.append([-1.1, -.12, 1.1, .12]); return pc

    def giant_stool(cx):
        pc = Piece("giant_stool"); m = Mesh()
        for sx in (-1, 1):
            for sz in (-1, 1):
                m.add(cylinder(0.07, 0.09, 0.8, 6, TIMBER_LO, "timber", y0=0).xf((sx * 0.35, 0, sz * 0.35)))
        m.add(cylinder(0.55, 0.55, 0.14, 8, TIMBER_HI, "timber", y0=0.8)); m.add(cylinder(0.5, 0.5, 0.03, 8, FUR, "paint", y0=0.94))
        pc.mesh = m.ao(0, 1.0, 0.15); pc.size = [1.1, 1.0, 1.1]; pc.blockers.append([-.5, -.5, .5, .5]); pc.markers["climbable"] = "the player climbs onto stools"; return pc

    def glow_orb_chain(cx):
        pc = Piece("glow_orb_chain"); m = Mesh()
        for k in range(8):
            m.add(box(0.05, 0.1, 0.02, IRON, "paint", y0=2.9 - k * 0.14 * 1.0 + 0.0))
        m.add(cylinder(0.14, 0.1, 0.1, 6, IRON_HI, "paint", y0=1.85))
        m.add(sphere(0.3, 8, 5, ORB, "glow").xf((0, 1.6, 0))); m.add(sphere(0.14, 6, 3, CF_HI, "glow").xf((0, 1.6, 0.0)))
        pc.mesh = m; lamp(pc, (0, 1.6, 0), ORB, 5.5, 0.0); pc.size = [0.7, 3.0, 0.7]
        pc.markers["hanging"] = "hang from roof beams at y = 3 m; still light (no flicker)"; return pc

    def fur_stall(cx):
        pc = Piece("fur_stall"); m = Mesh()
        for sx in (-1, 1):
            m.add(cylinder(0.1, 0.1, 2.6, 6, TIMBER_HI, "timber", y0=0).xf((sx * 1.4, 0, -.5)))
            m.add(cylinder(0.1, 0.1, 2.2, 6, TIMBER_HI, "timber", y0=0).xf((sx * 1.4, 0, .6)))
        m.add(box(3.1, 0.7, 0.8, TIMBER, "timber", y0=0.4).xf((0, 0, .6)))
        m.add(box(3.1, 0.12, 0.9, SNOW_SH, "paint", y0=1.1).xf((0, 0, .6)))
        prof = [(1.0, 2.2), (-.6, 2.7), (-1.0, 2.3)]
        m.add(prism_x(3.4, [(1.2, 2.25), (0, 2.8), (-1.2, 2.25)], FUR, "paint"))
        for k in range(5):
            m.add(sphere(.22, 5, 3, ["#a8744a", "#d8cdb8", "#7a8096"][k % 3], "paint", squash=(1, .5, 1)).xf((-1.2 + k * .6, 1.2, .5)))
        m.add(sphere(.2, 6, 4, CF, "glow").xf((1.1, 1.4, .7)))
        pc.mesh = m.ao(0, 2.8, 0.15); lamp(pc, (1.1, 1.5, .8), CF, 4.0); pc.size = [3.4, 2.8, 1.4]; pc.blockers.append([-1.5, -.2, 1.5, 1.0]); return pc

    # ======================================================================= Rime Caves
    def ice_floor(cx):
        return floor_tile(Piece("ice_floor"), "ice_floor", cx.seed, "#8ab8d8", "#b8dcf0", POOL, 3)

    def icicle(m, pos, h, r, top_down=True):
        c = Mesh()
        if top_down:
            c.add(cylinder(r, 0.0, h * .8, 5, ICE, "paint", y0=-h * .8))
            c.add(cylinder(r * 0.35, 0.0, h * .3, 5, POOL_HI, "glow", y0=-h))
        m.add(c.xf(pos))

    def ice_wall(cx):
        pc = Piece("ice_wall"); r = K.rng(cx.seed, "iw"); m = Mesh()
        for k in range(4):
            m.add(box(2.0, 0.8, 0.5, mix(ICE_DEEP, ICE, r.uniform(0, .8)), "paint", y0=k * 0.8))
        m.add(box(2.0, 0.3, 0.6, SNOW, "paint", y0=3.1))
        for k in range(6):
            icicle(m, (-0.85 + k * 0.34, 3.15, 0.3), r.uniform(.4, .9), .06)
        m.add(box(1.6, 0.05, 0.02, POOL, "glow", y0=1.6).xf((0, 0, 0.26)))
        pc.mesh = m.ao(0, 3.4, 0.15); lamp(pc, (0, 1.6, 0.6), POOL, 3.5); pc.size = [2, 3.4, 0.6]; pc.blockers.append([-1, -.3, 1, .3]); return pc

    def glow_ice_pool(cx):
        pc = Piece("glow_ice_pool"); m = Mesh()
        for k in range(16):
            a0, a1 = k * 2 * PI / 16, (k + 1) * 2 * PI / 16
            m.quad((0, 0.02, 0), (math.cos(a0) * 1.5, 0.02, math.sin(a0)), (math.cos(a1) * 1.5, 0.02, math.sin(a1)), (0, 0.02, 0), POOL, mat="glow")
            m.add(box(0.35, 0.14, 0.25, ICE, "paint", y0=0).xf((math.cos(a0) * 1.6, 0, math.sin(a0) * 1.1)))
        for (x, z) in ((-0.5, 0.2), (0.4, -0.3), (0.1, 0.4), (-0.2, -0.5)):
            m.add(box(0.14, 0.004, 0.05, POOL_HI, "glow", y0=0.025).xf((x, 0, z)))
        pc.mesh = m; lamp(pc, (0, 0.5, 0), POOL, 5.0); pc.size = [3.4, 0.14, 2.4]; pc.blockers.append([-1.5, -1.0, 1.5, 1.0])
        pc.markers["no_props_within_m"] = 0.5; return pc

    def icicle_cluster(cx):
        pc = Piece("icicle_cluster"); r = K.rng(cx.seed, "icl"); m = Mesh()
        m.add(box(1.6, 0.25, 0.9, ICE_DEEP, "paint", y0=3.2))
        for k in range(9):
            icicle(m, (r.uniform(-.7, .7), 3.25, r.uniform(-.3, .3)), r.uniform(.6, 1.7), r.uniform(.05, .11))
        pc.mesh = m; lamp(pc, (0, 2.4, 0.3), POOL_HI, 4.0); pc.size = [1.6, 3.5, 0.9]
        pc.markers["hanging"] = "mount to the cave ceiling at y = 3.2 m; glow tips"; return pc

    def ice_crystal_cluster(cx):
        pc = Piece("ice_crystal_cluster"); r = K.rng(cx.seed, "icc"); m = Mesh()
        m.add(sphere(0.6, 7, 4, STONE_HI, "stone", squash=(1, 0.35, 0.8)))
        def crys(pos, h, rr, tilt):
            c = Mesh()
            c.add(cylinder(rr, rr * .9, h * .75, 6, ICE, "paint", y0=0)); c.add(cylinder(rr * .9, 0.0, h * .25, 6, POOL_HI, "glow", y0=h * .75))
            m.add(c.xf((0, 0, 0), rot=(tilt[0], 0, tilt[1])).xf(pos))
        for k in range(7):
            a = k * 2 * PI / 7 + r.uniform(0, .4)
            crys((math.cos(a) * .3, .1, math.sin(a) * .25), r.uniform(.6, 1.4), r.uniform(.09, .15), (math.sin(a) * .4, math.cos(a) * .4))
        crys((0, .1, 0), 1.8, .2, (0, 0))
        pc.mesh = m.ao(0, 1.9, 0.1); lamp(pc, (0, 1.0, .3), POOL, 4.5); pc.size = [1.4, 1.9, 1.2]; pc.blockers.append([-.6, -.5, .6, .5]); return pc

    def frost_rune_pillar(cx):
        pc = Piece("frost_rune_pillar"); m = Mesh()
        m.add(cylinder(0.55, 0.45, 3.4, 7, ICE_DEEP, "paint", y0=0)); m.add(cylinder(0.65, 0.55, 0.25, 7, STONE_HI, "stone", y0=0))
        for k in range(5):
            m.add(box(0.2, 0.05, 0.02, RUNE, "glow", y0=0.7 + k * .55).xf((0, 0, .5 - k * .015)))
            m.add(box(0.05, 0.2, 0.02, CF_HI, "glow", y0=0.6 + k * .55).xf((0.06, 0, .5 - k * .015)))
        pc.mesh = m.ao(0, 3.5, 0.15); lamp(pc, (0, 1.8, .7), RUNE, 4.5); pc.size = [1.3, 3.4, 1.3]; pc.blockers.append([-.5, -.5, .5, .5]); return pc

    # ======================================================================= Titan's Barrow
    def barrow_floor(cx):
        return floor_tile(Piece("barrow_floor"), "barrow_floor", cx.seed, "#38404f", "#4c566a", CF_LO, 2)

    def barrow_wall(cx):
        pc = Piece("barrow_wall"); r = K.rng(cx.seed, "bw"); m = Mesh()
        for k in range(5):
            m.add(box(2.0, 0.64, 0.5, mix(STONE, STONE_HI, r.uniform(0, .7)), "stone", y0=k * 0.64))
        m.add(box(2.0, 0.05, 0.02, CF, "glow", y0=1.4).xf((0, 0, 0.26)))
        for k in range(6):
            m.add(box(0.06, 0.14, 0.02, CF_HI, "glow", y0=1.28).xf((-0.8 + k * 0.32, 0, 0.27)))
        pc.mesh = m.ao(0, 3.2, 0.15); lamp(pc, (0, 1.4, 0.5), CF, 3.2); pc.size = [2, 3.2, 0.5]; pc.blockers.append([-1, -.25, 1, .25]); return pc

    def barrow_door(cx):
        pc = Piece("barrow_door"); m = Mesh()
        for sx in (-1, 1):
            m.add(box(0.9, 6.2, 1.0, STONE, "stone", y0=0).xf((sx * 2.65, 0, 0)))
        m.add(box(6.4, 0.9, 1.0, STONE_HI, "stone", y0=6.0))
        m.add(box(3.9, 5.8, 0.4, STONE_LO, "stone", y0=0).xf((0, 0, -0.1)))
        for k in range(3):
            x = -1.2 + k * 1.2
            m.add(cylinder(0.32, 0.32, 0.06, 8, STONE_HI, "stone", y0=2.6).xf((x, 0, 0.12), rot=(PI / 2, 0, 0)).xf((0, 0.3, 0)))
            m.add(sphere(0.2, 7, 4, CF, "glow", squash=(1, 1, .35)).xf((x, 3.15, 0.2)))
            m.add(sphere(0.1, 6, 3, CF_HI, "glow", squash=(1, 1, .5)).xf((x, 3.15, 0.25)))
        for k in range(9):
            m.add(box(0.07, 0.3, 0.02, RUNE, "glow", y0=4.4).xf((-1.5 + k * .38, 0, 0.12)))
        m.add(box(3.4, 0.06, 0.02, CF, "glow", y0=4.1).xf((0, 0, 0.12)))
        pc.mesh = m.ao(0, 6.5, 0.15); lamp(pc, (0, 3.2, 0.9), CF, 6.0); pc.size = [6.4, 6.9, 1.0]
        pc.blockers.append([-3.2, -.5, 3.2, .5]); pc.markers["rune_locks"] = 3; pc.markers["note"] = "Barrow mouth: three rune locks; keep 3 m clear in front"; return pc

    def shield_rack(cx):
        pc = Piece("shield_rack"); m = Mesh()
        for sx in (-1, 1):
            m.add(cylinder(0.1, 0.1, 2.4, 6, TIMBER_HI, "timber", y0=0).xf((sx * 1.0, 0, 0)))
        m.add(box(2.3, 0.14, 0.14, TIMBER, "timber", y0=2.3))
        m.add(cylinder(0.85, 0.85, 0.1, 12, IRON, "paint", y0=0.4).xf((0, 0, 0), rot=(PI / 2, 0, 0)).xf((0, 0.9, 0.1)))
        m.add(cylinder(0.55, 0.55, 0.12, 12, "#6a3a30", "paint", y0=0).xf((0, 0, 0), rot=(PI / 2, 0, 0)).xf((0, 1.3, 0.2)))
        m.add(sphere(0.16, 6, 4, IRON_HI, "paint", squash=(1, 1, .6)).xf((0, 1.3, 0.3)))
        m.add(box(1.6, 0.04, 0.02, CF, "glow", y0=0.5).xf((0, 0, 0.2)))
        pc.mesh = m.ao(0, 2.5, 0.15); lamp(pc, (0, 1.3, 0.6), CF, 3.0); pc.size = [2.4, 2.5, 0.5]; pc.blockers.append([-1.1, -.2, 1.1, .2]); return pc

    def ice_throne(cx):
        pc = Piece("ice_throne"); m = Mesh()
        m.add(cylinder(2.4, 2.1, 0.5, 9, STONE_HI, "stone", y0=0)); m.add(cylinder(1.9, 1.6, 0.5, 9, STONE, "stone", y0=0.5))
        m.add(box(2.6, 1.0, 2.0, ICE_DEEP, "paint", y0=1.0)); m.add(box(2.6, 4.4, 0.6, ICE, "paint", y0=1.0).xf((0, 0, -0.9)))
        for sx in (-1, 1):
            m.add(box(0.5, 1.8, 2.0, ICE, "paint", y0=1.0).xf((sx * 1.55, 0, 0)))
            m.add(cylinder(0.35, 0.0, 2.2, 5, ICE_HI, "paint", y0=5.0).xf((sx * 1.0, 0, -0.9)))
        m.add(cylinder(0.5, 0.0, 2.8, 5, ICE_HI, "paint", y0=5.2).xf((0, 0, -0.9)))
        for k in range(5):
            m.add(box(0.12, 0.7, 0.03, CF, "glow", y0=2.0 + (k % 2) * .6).xf((-0.9 + k * .45, 0, -0.58)))
        m.add(box(2.4, 0.05, 0.03, RUNE, "glow", y0=0.55).xf((0, 0, 1.82)))
        pc.mesh = m.ao(0, 7.5, 0.15); lamp(pc, (0, 3.0, 0.4), CF, 7.0); pc.size = [5.0, 8.0, 5.0]
        pc.blockers.append([-2.4, -1.5, 2.4, 1.5]); pc.markers["boss_stand"] = [0, 0, 3.4]; pc.markers["note"] = "Hrimgard's throne (boss_stand marker); floor round it freezes in phase 2"; return pc

    def rune_bridge(cx):
        pc = Piece("rune_bridge"); m = Mesh()
        for k in range(4):
            lit = k % 2 == 0
            m.add(box(1.6, 0.18, 0.46, ICE if lit else "#7098b8", "paint", y0=0).xf((0, 0, -0.75 + k * 0.5)))
            if lit:
                m.add(box(0.8, 0.012, 0.14, CF_HI, "glow", y0=0.18).xf((0, 0, -0.75 + k * 0.5)))
        for sx in (-1, 1):
            m.add(box(0.1, 0.6, 2.0, IRON, "paint", y0=0.0).xf((sx * 0.85, 0, 0)))
        pc.mesh = m.ao(0, 0.8, 0.15); lamp(pc, (0, 0.5, 0), CF, 3.0); pc.size = [1.8, 0.8, 2.0]
        pc.markers["note"] = "B7: step on lit runes only; every second plank is lit in this piece"; return pc

    def rune_brazier(cx):
        pc = cold_brazier(cx, "rune_brazier", 2.6, 1.3)
        pc.markers["snuff"] = "tb_b1..3: snuff with a frost / water spell or E / A"; return pc

    def warm_lantern(cx):
        pc = Piece("warm_lantern"); m = Mesh()
        m.add(cylinder(0.2, 0.16, 0.2, 6, STONE_HI, "stone", y0=0)); m.add(cylinder(0.05, 0.05, 1.7, 6, TIMBER_HI, "timber", y0=0.2))
        m.add(beam([0, 1.85, 0], [0.35, 1.85, 0], 0.05, TIMBER_HI, "timber"))
        m.add(box(0.26, 0.34, 0.26, WARM, "glow", y0=1.45).xf((0.35, 0, 0))); m.add(box(0.34, 0.05, 0.34, IRON, "paint", y0=1.8).xf((0.35, 0, 0)))
        m.add(box(0.34, 0.05, 0.34, IRON, "paint", y0=1.4).xf((0.35, 0, 0)))
        pc.mesh = m.ao(0, 2.0, 0.1); lamp(pc, (0.35, 1.6, 0.0), WARM, 5.0); pc.size = [0.8, 2.0, 0.4]; pc.blockers.append([-.2, -.2, .2, .2])
        pc.markers["note"] = "warm accent against the cold glow (Bill: gloom and glow, not all blue)"; return pc

    fns = [warm_lantern, snow_floor, ice_lake, stone_ledge, stone_stair, snow_mound, longhouse, rune_standing_stone, lift_stone, lambda cx: cold_brazier(cx),
           goat_fence, giant_stool, glow_orb_chain, fur_stall, ice_floor, ice_wall, glow_ice_pool, icicle_cluster, ice_crystal_cluster, frost_rune_pillar,
           barrow_floor, barrow_wall, barrow_door, shield_rack, ice_throne, rune_bridge, rune_brazier]
    out = {}
    for f in fns:
        n = getattr(f, "__name__", "")
        out[n if n != "<lambda>" else "cold_brazier"] = f
    return out
