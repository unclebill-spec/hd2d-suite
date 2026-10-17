"""Muspelheim kit pieces (original; Hearthmoor Art seat staging, 2026-10-17). Built with the repo's kit.py / meshlib like kit_svart.py / kit_jotun.py.
 Cinderhold (area `muspelheim`): basalt_floor, lava_channel, lava_pool, basalt_ledge (1.34 m), basalt_stair (6 steps, 1.2 m), warden_stones, basalt_house,
   forge_hall (fire-giant doors), red_arch, spice_stall, brazier_stand, cold_brazier, shrine_lamp, glass_bridge, lizard_stable, emberfall_anvil, dance_ring,
   obsidian_pillar, amber_orb_chain, spring_pool, warm_lantern, muspel_waystone, cinder_cairn
 Sigil Forge (`mp_hall`): forge_floor, forge_wall, wardens_seat, seal_cast_bed, stamp_press, ledger_desk, sigil_mould_wall
 Lavafalls (`lavafalls`): lava_fall_cliff, glass_terrace, caldera_mouth_arch (6 m, three seal doors)
 Ember Caldera: ember_throne (boss_stand), warden_lamp_stand, furnace, hanging_crystals, cold_seam_wall
Neon hexes only on the 'glow' material (lava, cold fire, violet lamps, crystals, springs, orbs). Placement notes live in kit.json markers."""
import math
PI = math.pi
# palette: black basalt LIFTED so night renders read as dark warm grey, not a pit (check-scene luma 20-30)
BAS, BAS_HI, BAS_LO = "#4c4658", "#6c6678", "#363240"
ASH, ASH_HI = "#5e5a66", "#8a8590"
RED, RED_HI, RED_LO = "#8a3026", "#b04632", "#5a1e1c"
COPPER, COPPER_HI = "#b8642e", "#e08a48"
IRON, IRON_HI = "#4a4652", "#7a7684"
LAVA, LAVA_HI, LAVA_LO = "#ff7a1a", "#ffd27a", "#e8321e"
WARM = "#ffb066"
CF, CF_HI, CF_LO = "#3fb8ff", "#d8f2ff", "#1c62d8"        # cold fire / frost vein
VIO, VIO_HI = "#a45cf0", "#d4a8ff"                          # shrine lamps
TEAL, TEAL_HI, TEAL_LO = "#2fd0d0", "#a8fff0", "#16807f"
GLASS, GLASS_HI = "#e0a050", "#ffe0a0"
TIMBER, TIMBER_HI, TIMBER_LO = "#6a4a34", "#8a6444", "#42301f"
RUST, SAND, CHAR = "#a85430", "#c8a878", "#3a3036"
HAY = "#c8a050"


def pieces(K):
    box, cylinder, sphere, beam, mix, Piece, Mesh, prism_x = K.box, K.cylinder, K.sphere, K.beam, K.mix, K.Piece, K.Mesh, K.prism_x

    def lamp(pc, pos, col, rng_, fixed=0.5):
        pc.markers["lamps"].append(list(pos)); pc.markers["lamp_color"] = col; pc.markers["lamp_range"] = rng_; pc.markers["lamp_fixed"] = fixed

    def keep(pc, fp, radius, note):
        pc.markers["keep_clear"] = {"footprint_m": fp, "radius_m": radius, "note": note}

    def floor_tile(pc, name, seed, c0, c1, seam, flecks=None, fleck_col=None):
        r = K.rng(seed, name); m = Mesh()
        for i in range(4):
            for j in range(4):
                x0, z0 = -1 + i * 0.5, -1 + j * 0.5
                m.quad((x0, 0, z0 + 0.5), (x0 + 0.5, 0, z0 + 0.5), (x0 + 0.5, 0, z0), (x0, 0, z0), mix(c0, c1, r.uniform(0, 0.8)), mat="paint")
        if seam:
            m.add(box(2.0, 0.006, 0.03, seam, "glow", y0=0).xf((0, 0, 0.5)))
            m.add(box(0.03, 0.006, 1.0, seam, "glow", y0=0).xf((0.5, 0, -0.5)))
        for k in range(flecks or 0):
            m.add(sphere(r.uniform(0.04, 0.09), 5, 3, fleck_col or BAS_HI, "stone", squash=(1.3, 0.5, 1)).xf((r.uniform(-.9, .9), 0.0, r.uniform(-.9, .9))))
        pc.mesh = m; pc.size = [2, 0.02, 2]; return pc

    def flame(m, y, s=1.0, c=LAVA, ch=LAVA_HI):
        m.add(sphere(0.32 * s, 7, 4, c, "glow", squash=(1, 0.5, 1)).xf((0, y, 0)))
        m.add(cylinder(0.26 * s, 0.0, 0.9 * s, 7, c, "glow", y0=y))
        m.add(cylinder(0.14 * s, 0.0, 0.6 * s, 6, ch, "glow", y0=y))

    def window(m, x, y, z, w=0.6, h=0.7, col=WARM):
        m.add(box(w, h, 0.04, col, "window", y0=y).xf((x, 0, z)))
        m.add(box(w + .1, 0.06, 0.08, BAS_LO, "stone", y0=y - .06).xf((x, 0, z - 0.01)))

    # ======================================================================= Cinderhold
    def basalt_floor(cx):
        return floor_tile(Piece("basalt_floor"), "basalt_floor", cx.seed, BAS, BAS_HI, None, 6, ASH)

    def lava_channel(cx):
        pc = Piece("lava_channel"); r = K.rng(cx.seed, "lavach"); m = Mesh()
        m.add(box(2.0, 0.08, 4.0, BAS_LO, "stone", y0=-0.02))
        for sx in (-1, 1):                                               # basalt banks
            m.add(box(0.4, 0.22, 4.0, mix(BAS, BAS_HI, .4), "stone", y0=0).xf((sx * 0.8, 0, 0)))
            for k in range(5):
                m.add(sphere(0.2, 6, 3, BAS_HI, "stone", squash=(1.2, .6, 1)).xf((sx * (0.62 + r.uniform(0, .05)), 0.2, -1.8 + k * .9 + r.uniform(-.1, .1))))
        m.add(box(1.2, 0.06, 4.0, LAVA_LO, "glow", y0=0.0))
        for k in range(6):
            m.add(box(r.uniform(.4, .8), 0.015, r.uniform(.5, 1.0), LAVA, "glow", y0=0.06).xf((r.uniform(-.3, .3), 0, -1.7 + k * .7)))
            m.add(box(0.18, 0.015, r.uniform(.2, .4), LAVA_HI, "glow", y0=0.075).xf((r.uniform(-.2, .2), 0, -1.7 + k * .7)))
        pc.mesh = m.ao(0, 0.5, 0.15); lamp(pc, (0, 0.5, 0), LAVA, 4.0, 0.0); pc.size = [2.0, 0.3, 4.0]
        pc.blockers.append([-0.6, -2.0, 0.6, 2.0]); pc.markers["hazard"] = "lava: damage; bridge with glass_bridge / warden_stones"
        keep(pc, [-1.0, -2.0, 1.0, 2.0], 1.0, "nothing spawns within 1 m of lava; chain end to end along z; glow pool_lava + lava_crawl decal over the channel"); return pc

    def lava_pool(cx):
        pc = Piece("lava_pool"); m = Mesh()
        m.add(cylinder(2.0, 1.8, 0.2, 12, BAS, "stone", y0=0))
        m.add(cylinder(1.6, 1.55, 0.04, 12, LAVA_LO, "glow", y0=0.2)); m.add(cylinder(1.1, 1.0, 0.05, 12, LAVA, "glow", y0=0.2))
        m.add(sphere(0.5, 8, 3, LAVA_HI, "glow", squash=(1.3, 0.12, 1.1)).xf((-0.2, 0.24, 0.1)))
        for k in range(8):
            a = k * PI / 4
            m.add(sphere(0.28, 6, 3, mix(BAS, BAS_HI, (k % 3) / 3), "stone", squash=(1.2, .7, 1)).xf((math.cos(a) * 1.85, 0.15, math.sin(a) * 1.85)))
        pc.mesh = m.ao(0, 0.5, 0.15); lamp(pc, (0, 0.6, 0), LAVA, 5.0, 0.0); pc.size = [4.0, 0.4, 4.0]; pc.blockers.append([-1.8, -1.8, 1.8, 1.8])
        keep(pc, [-2.2, -2.2, 2.2, 2.2], 2.4, "fall-pool (rares spawn here at runtime); keep props 2.4 m away"); return pc

    def basalt_ledge(cx):
        pc = Piece("basalt_ledge"); r = K.rng(cx.seed, "bledge"); m = Mesh()
        H = 1.2
        for k in range(3):
            m.add(box(3.0, 0.4, 2.0, mix(BAS, BAS_HI, r.uniform(0, .6)), "stone", y0=k * 0.4))
        m.add(box(3.1, 0.14, 2.1, BAS_HI, "stone", y0=H))
        for k in range(5):
            m.add(sphere(0.16, 6, 3, ASH, "stone", squash=(1.4, .5, 1)).xf((-1.2 + k * .6, H + .1, 1.0 + r.uniform(-.1, .05))))
        m.add(box(2.6, 0.04, 0.02, LAVA_LO, "glow", y0=0.5).xf((0, 0, 1.01)))
        for k in range(5):
            m.add(box(0.07, 0.14, 0.02, LAVA, "glow", y0=0.4).xf((-1.0 + k * .5, 0, 1.02)))
        pc.mesh = m.ao(0, 1.4, 0.2); lamp(pc, (0, 0.6, 1.3), LAVA, 3.0); pc.size = [3.1, 1.34, 2.1]
        pc.blockers.append([-1.5, -1.0, 1.5, 1.0])
        pc.markers["height_m"] = 1.34; pc.markers["ledge_edge"] = [[-1.5, 1.0], [1.5, 1.0]]; pc.markers["no_props_within_m"] = 0.8; return pc

    def basalt_stair(cx):
        pc = Piece("basalt_stair"); m = Mesh()
        n, rise, run, wd = 6, 1.2, 0.5, 2.0
        st = rise / n; L = n * run
        for i in range(n):
            h = st * (i + 1); z1 = L / 2 - i * run; z0 = -L / 2
            m.add(box(wd, h, z1 - z0, mix(BAS, BAS_HI, 0.15 + 0.05 * (i % 2)), "stone", y0=0).xf((0, 0, (z0 + z1) / 2)))
            m.add(box(0.5, 0.012, 0.02, LAVA_LO, "glow", y0=h - 0.05).xf((0, 0, z1 + 0.002)))
        for sx in (-1, 1):
            prof = [(L / 2 + 0.05, 0), (L / 2 + 0.05, 0.5), (-L / 2, rise + 0.5), (-L / 2, 0)]
            m.add(prism_x(0.3, prof, BAS_HI, "stone").xf((sx * (wd / 2 + 0.15), 0, 0)))
            m.add(cylinder(0.05, 0.05, 0.5, 6, IRON, "paint", y0=0.5).xf((sx * (wd / 2 + 0.15), 0, L / 2 - 0.1)))
            m.add(sphere(0.1, 6, 4, LAVA, "glow").xf((sx * (wd / 2 + 0.15), 1.05, L / 2 - 0.1)))
        pc.mesh = m.ao(0, 2.0, 0.15); lamp(pc, (0, 1.2, L / 2 + .1), LAVA, 3.5)
        pc.size = [wd + 0.9, rise + .1, L]; pc.markers["stairs"] = {"rise_m": rise, "steps": n, "run_m": run, "width_m": wd, "climbs_toward": "-z"}
        pc.markers["note"] = "one per ledge, centred; top flush with the ledge front face; keep 1 m clear at each end"; return pc

    def warden_stones(cx):
        pc = Piece("warden_stones"); r = K.rng(cx.seed, "wstones"); m = Mesh()
        m.add(box(4.0, 0.06, 2.0, LAVA_LO, "glow", y0=-0.02))
        for k in range(5):
            x = -1.6 + k * 0.8; z = math.sin(k * 1.7) * .35
            m.add(cylinder(0.34, 0.38, 0.28, 7, mix(BAS_HI, ASH, .3), "stone", y0=0).xf((x, 0, z)))
            m.add(cylinder(0.2, 0.2, 0.02, 7, LAVA_HI if k % 2 == 0 else COPPER_HI, "glow", y0=0.28).xf((x, 0, z)))
        for k in range(6):
            m.add(sphere(r.uniform(.15, .3), 6, 3, LAVA, "glow", squash=(1.4, .1, 1)).xf((r.uniform(-1.8, 1.8), 0.05, r.uniform(-.8, .8))))
        pc.mesh = m.ao(0, 0.4, 0.15); lamp(pc, (0, 0.5, 0), LAVA, 4.5, 0.0); pc.size = [4.0, 0.3, 2.0]
        pc.markers["note"] = "the Warden's Walk [0,3.0] (The Cinder Walk): 5 stepping-stones 0.28 m high over lava; place 2 pieces end to end"
        keep(pc, [-2.0, -1.0, 2.0, 1.0], 1.5, "quest route: no props or spawns on or within 1.5 m"); return pc

    def basalt_house(cx):
        pc = Piece("basalt_house"); r = K.rng(cx.seed, "bh"); m = Mesh()
        Wd, D, WH = 5.2, 4.2, 3.2
        m.add(box(Wd + .3, 0.5, D + .3, BAS_LO, "stone", y0=0))
        m.add(box(Wd, WH - .5, D, BAS, "stone", y0=0.5))
        for k in range(4):                                                # stacked basalt columns on the front
            for j in range(9):
                m.add(box(.5, WH - .5, .1, mix(BAS, BAS_HI, ((j + k) % 3) / 4), "stone", y0=0.5).xf((-2.3 + j * .575, 0, D / 2 + .05)))
            break
        m.add(box(1.0, 2.1, 0.08, TIMBER_LO, "timber", y0=0.5).xf((0, 0, D / 2 + .1)))
        m.add(box(1.3, 0.2, 0.2, TIMBER_HI, "timber", y0=2.6).xf((0, 0, D / 2 + .12)))
        for x in (-1.8, 1.8):
            window(m, x, 1.4, D / 2 + .13, .8, .8)
        m.add(box(Wd + .6, 0.22, D + .6, RED, "paint", y0=WH).xf((0, 0, 0)))                # low red-slate roof
        m.add(prism_x(Wd + .6, [(D / 2 + .3, WH + .2), (0, WH + 1.0), (-D / 2 - .3, WH + .2)], RED_HI, "paint"))
        m.add(box(0.7, 1.4, 0.7, BAS_HI, "stone", y0=WH + .5).xf((1.6, 0, -1.0)))
        m.add(box(0.4, 0.1, 0.4, LAVA, "glow", y0=WH + 1.85).xf((1.6, 0, -1.0)))
        for x in (-1.8, 1.8):
            m.add(box(0.8, 0.5, 0.5, SAND, "paint", y0=0.5).xf((x, 0, D / 2 + .3)))      # sill boxes
        pc.mesh = m.ao(0, WH + 1.2, 0.2); lamp(pc, (0, 1.5, D / 2 + .8), WARM, 4.5); lamp(pc, (1.6, WH + 2.0, -1.0), LAVA, 3.0)
        pc.size = [Wd + .6, WH + 2.0, D + .6]; pc.blockers.append([-Wd / 2, -D / 2, Wd / 2, D / 2])
        pc.markers["doors"].append({"pos": [0, 0, D / 2 + .2], "w": 1.0, "h": 2.1}); pc.markers["spawn_clear_m"] = 1.8
        pc.markers["note"] = "ember-kin house; every window and door gets a warm pool_forge under it; 1.8 m clear in front of the door"; return pc

    def forge_hall(cx):
        pc = Piece("forge_hall"); r = K.rng(cx.seed, "fh"); m = Mesh()
        Wd, D, WH = 8.0, 5.0, 5.4
        m.add(box(Wd + .3, 0.8, D + .3, BAS_LO, "stone", y0=0))
        m.add(box(Wd, WH - .8, D, BAS, "stone", y0=0.8))
        for k in range(8):
            m.add(box(0.4, WH - .8, 0.12, mix(BAS, BAS_HI, (k % 3) / 4), "stone", y0=0.8).xf((-3.5 + k, 0, D / 2 + .06)))
        m.add(box(3.2, 4.0, 0.1, TIMBER_LO, "timber", y0=0.8).xf((0, 0, D / 2 + .1)))                         # giant door
        m.add(box(3.4, 0.25, 0.25, COPPER, "paint", y0=4.8).xf((0, 0, D / 2 + .14)))
        m.add(box(2.4, 0.9, 0.05, LAVA, "glow", y0=1.0).xf((0, 0, D / 2 + .2)))                               # furnace-glow through the doors
        for x in (-3.0, 3.0):
            window(m, x, 2.4, D / 2 + .13, 1.0, 1.2, LAVA)
        prof = [(D / 2 + .5, WH), (0, WH + 1.5), (-D / 2 - .5, WH)]
        m.add(prism_x(Wd + .8, prof, RED, "paint"))
        for sx in (-1, 1):
            m.add(cylinder(.6, .5, 3.2, 8, BAS_HI, "stone", y0=WH).xf((sx * 2.6, 0, -1.2)))               # two big chimneys
            m.add(cylinder(.38, .38, 0.1, 8, LAVA, "glow", y0=WH + 3.2).xf((sx * 2.6, 0, -1.2)))
        pc.mesh = m.ao(0, WH + 3.5, 0.2); lamp(pc, (0, 2.2, D / 2 + .8), LAVA, 6.0); lamp(pc, (2.6, WH + 3.4, -1.2), LAVA, 4.0)
        pc.size = [Wd + .8, WH + 3.3, D + 1.0]; pc.blockers.append([-Wd / 2, -D / 2, Wd / 2, D / 2])
        pc.markers["doors"].append({"pos": [0, 0, D / 2 + .2], "w": 3.2, "h": 4.0}); pc.markers["spawn_clear_m"] = 2.5
        pc.markers["note"] = "fire-giant forge (2.5x doors); 2.5 m clear in front; ember_motes over the chimneys"; return pc

    def red_arch(cx):
        pc = Piece("red_arch"); m = Mesh()
        for sx in (-1, 1):
            m.add(box(1.0, 5.4, 1.2, RED, "stone", y0=0).xf((sx * 2.2, 0, 0)))
            m.add(box(1.2, 0.3, 1.4, RED_HI, "stone", y0=0).xf((sx * 2.2, 0, 0)))
            m.add(box(0.12, 4.4, 0.04, LAVA_LO, "glow", y0=0.5).xf((sx * 2.2, 0, 0.62)))
        m.add(box(5.6, 0.9, 1.2, RED_HI, "stone", y0=5.4)); m.add(box(4.6, 0.5, 1.0, RED, "stone", y0=6.3))
        m.add(box(3.4, 0.08, 0.04, LAVA, "glow", y0=5.35).xf((0, 0, 0.62)))
        for k in range(7):
            m.add(box(0.1, 0.35, 0.03, LAVA_HI, "glow", y0=5.55).xf((-1.5 + k * 0.5, 0, 0.62)))
        m.add(box(3.4, 5.0, 0.12, "#ffd9a0", "glow", y0=0.05).xf((0, 0, -0.1)))                        # the Bifrost shimmer behind the arch
        pc.mesh = m.ao(0, 6.8, 0.15); lamp(pc, (0, 3.0, 1.2), LAVA, 6.0); lamp(pc, (0, 2.5, -0.6), "#ffd9a0", 4.0)
        pc.size = [6.0, 6.8, 1.4]; pc.blockers.append([-2.8, -.6, -1.7, .6]); pc.blockers.append([1.7, -.6, 2.8, .6])
        pc.markers["spawn"] = {"from_bifrost": [0, 0, 0.0], "note": "Red arch [0,10.6]; arrival 1.4 m in front [0,9.2,'up']; nothing within 1.5 m"}
        keep(pc, [-2.8, -1.0, 2.8, 2.6], 2.6, "arrival point: no props, spawns or decals within 2.6 m (heat_shimmer billboard above the opening is fine)"); return pc

    def spice_stall(cx):
        pc = Piece("spice_stall"); m = Mesh()
        for sx in (-1, 1):
            m.add(cylinder(0.1, 0.1, 2.6, 6, TIMBER_HI, "timber", y0=0).xf((sx * 1.4, 0, -.5)))
            m.add(cylinder(0.1, 0.1, 2.2, 6, TIMBER_HI, "timber", y0=0).xf((sx * 1.4, 0, .6)))
        m.add(box(3.1, 0.7, 0.8, TIMBER, "timber", y0=0.4).xf((0, 0, .6)))
        m.add(box(3.1, 0.12, 0.9, RUST, "paint", y0=1.1).xf((0, 0, .6)))
        m.add(prism_x(3.4, [(1.2, 2.25), (0, 2.8), (-1.2, 2.25)], RUST, "paint"))
        for k in range(5):
            m.add(cylinder(.16, .14, .2, 6, [COPPER, SAND, RED_HI][k % 3], "paint", y0=1.22).xf((-1.2 + k * .6, 0, .5)))
        m.add(cylinder(0.3, 0.4, 0.3, 8, IRON, "paint", y0=0).xf((1.9, 0, 0.9)))                    # the spice brazier
        flame(m, .3, .7).xf((1.9, 0, 0.9)) if False else None
        m.add(sphere(.22, 6, 4, LAVA, "glow", squash=(1, .6, 1)).xf((1.9, 0.38, 0.9)))
        pc.mesh = m.ao(0, 2.8, 0.15); lamp(pc, (1.9, 0.8, .9), LAVA, 4.0); lamp(pc, (0, 1.6, .9), WARM, 3.0); pc.size = [3.8, 2.8, 1.6]; pc.blockers.append([-1.5, -.2, 1.5, 1.0])
        pc.markers["note"] = "Svala's spice-brazier stall [-7.0,5.0]; counter faces +z, 1.5 m clear in front"; return pc

    def brazier(cx, name, flame_c, flame_hi, lamp_c, H=2.0, sc=1.0):
        pc = Piece(name); m = Mesh()
        for k in range(3):
            a = k * 2 * PI / 3 + .3
            m.add(beam([0, H * .82, 0], [math.cos(a) * .55 * sc, 0, math.sin(a) * .55 * sc], 0.1 * sc, IRON, "paint"))
        m.add(cylinder(0.5 * sc, 0.62 * sc, 0.3 * sc, 8, IRON_HI, "paint", y0=H * .8))
        m.add(cylinder(0.55 * sc, 0.5 * sc, 0.1, 8, IRON, "paint", y0=H * .8 + .3 * sc))
        flame(m, H * .8 + .3 * sc, sc * 1.2, flame_c, flame_hi)
        pc.mesh = m.ao(0, H + 1.2, 0.1); lamp(pc, (0, H * .8 + .9, 0.1), lamp_c, 6.0 * sc); pc.size = [1.3 * sc, H + 1.2, 1.3 * sc]
        pc.blockers.append([-.4 * sc, -.4 * sc, .4 * sc, .4 * sc]); return pc

    def brazier_stand(cx):
        pc = brazier(cx, "brazier_stand", LAVA, LAVA_HI, LAVA)
        pc.markers["note"] = "warm forge brazier: forge_flame billboard at y 2.0 m + pool_forge; Kindle lights it"; return pc

    def cold_brazier(cx):
        pc = brazier(cx, "cold_brazier", CF, CF_HI, CF)
        pc.markers["note"] = "cold-fire brazier (neon blue): cold_flame billboard + pool_cold; wedges / Cold Seam / the quiet corners"; return pc

    def shrine_lamp(cx):
        pc = Piece("shrine_lamp"); m = Mesh()
        m.add(cylinder(0.3, 0.4, 0.3, 8, BAS_HI, "stone", y0=0)); m.add(cylinder(0.14, 0.18, 1.5, 8, BAS, "stone", y0=0.3))
        m.add(cylinder(0.34, 0.2, 0.3, 8, IRON_HI, "paint", y0=1.8))
        flame(m, 2.1, .8, VIO, VIO_HI)
        m.add(box(0.5, 0.04, 0.02, VIO, "glow", y0=0.5).xf((0, 0, 0.17)))
        pc.mesh = m.ao(0, 3.0, 0.1); lamp(pc, (0, 2.3, 0), VIO, 4.5); pc.size = [0.9, 3.0, 0.9]; pc.blockers.append([-.3, -.3, .3, .3])
        pc.markers["note"] = "violet shrine-lamp (Warden's hall: one either side of the seat; spring grotto): violet_flame billboard + pool_violet"; return pc

    def glass_bridge(cx):
        pc = Piece("glass_bridge"); r = K.rng(cx.seed, "gbridge"); m = Mesh()
        for k in range(4):
            lit = k % 2 == 0
            m.add(box(2.0, 0.14, 0.9, GLASS if lit else "#c08a48", "paint", y0=0).xf((0, 0, -1.5 + k * 1.0)))
            m.add(box(1.4, 0.012, 0.5, GLASS_HI if lit else LAVA_LO, "glow", y0=0.14).xf((0, 0, -1.5 + k * 1.0)))
        for sx in (-1, 1):
            m.add(box(0.12, 0.9, 4.0, IRON, "paint", y0=0.0).xf((sx * 1.05, 0, 0)))
            for k in range(3):
                m.add(cylinder(0.07, 0.07, 1.0, 6, IRON_HI, "paint", y0=0).xf((sx * 1.05, 0, -1.6 + k * 1.6)))
                m.add(sphere(0.1, 6, 4, LAVA, "glow").xf((sx * 1.05, 1.05, -1.6 + k * 1.6)))
        pc.mesh = m.ao(0, 1.2, 0.15); lamp(pc, (0, 0.6, 0), LAVA, 4.0); pc.size = [2.4, 1.2, 4.0]
        pc.markers["note"] = "Cinderhold -> Lavafalls bridge [10,-9]; chain along z; in the Caldera (C3) the lit panels are safe, the dark ones crack"; return pc

    def lizard_stable(cx):
        pc = Piece("lizard_stable"); r = K.rng(cx.seed, "stable"); m = Mesh()
        m.add(box(5.4, 0.2, 3.4, BAS_LO, "stone", y0=0))
        for sx in (-1, 0, 1):
            m.add(box(0.18, 1.6, 0.18, TIMBER_HI, "timber", y0=0.2).xf((sx * 1.7 - .85, 0, 1.4)))
        m.add(box(5.0, 0.12, 0.12, TIMBER, "timber", y0=1.7).xf((0, 0, 1.4)))
        m.add(box(5.0, 0.25, 3.3, BAS, "stone", y0=1.8).xf((0, 0, 0)))                                # basalt slab roof
        for z in (-1.4, -0.4):
            m.add(box(5.0, 1.5, 0.12, BAS_HI, "stone", y0=0.2).xf((0, 0, z)))
        for sx in (-1, 1):
            m.add(box(0.12, 1.5, 1.6, BAS_HI, "stone", y0=0.2).xf((sx * 2.5, 0, 0.4)))
        for k in range(4):
            m.add(sphere(.35, 6, 3, HAY, "paint", squash=(1.4, .5, 1)).xf((-1.8 + k * 1.2, 0.3, 0.2 + r.uniform(0, .4))))
        m.add(sphere(.24, 6, 4, LAVA, "glow", squash=(1, .7, 1)).xf((2.1, 0.42, 1.2)))
        pc.mesh = m.ao(0, 2.2, 0.15); lamp(pc, (2.1, 0.9, 1.2), LAVA, 3.5); lamp(pc, (0, 1.4, 1.7), WARM, 3.5); pc.size = [5.4, 2.1, 3.4]
        pc.blockers.append([-2.6, -1.6, 2.6, .0])
        pc.markers["note"] = "Orm's lizard stables [-9,-3]; open side faces +z; 1.5 m clear in front"; return pc

    def emberfall_anvil(cx):
        pc = Piece("emberfall_anvil"); m = Mesh()
        m.add(cylinder(0.55, 0.65, 0.7, 8, BAS_HI, "stone", y0=0))
        m.add(box(1.2, 0.18, 0.5, IRON_HI, "paint", y0=0.7)); m.add(box(0.6, 0.24, 0.36, IRON, "paint", y0=0.52).xf((0, 0, 0)))
        m.add(prism_x(0.4, [(0.35, 0.88), (0.0, 1.0), (-0.3, 0.88)], IRON_HI, "paint").xf((0.8, 0, 0)))
        m.add(box(0.7, 0.03, 0.3, LAVA, "glow", y0=0.88)); m.add(box(0.3, 0.03, 0.14, LAVA_HI, "glow", y0=0.9))
        pc.mesh = m.ao(0, 1.2, 0.15); lamp(pc, (0, 1.0, 0), LAVA, 3.5); pc.size = [2.0, 1.1, 1.1]; pc.blockers.append([-.6, -.4, .6, .4])
        pc.markers["note"] = "Emberfall contest anvils [8,-2] and Torka's school anvils [-6,-4] (lavafalls): 1.5 m clear around for the heat-timing beat"
        keep(pc, [-1.0, -1.0, 1.0, 1.0], 1.5, "keep the anvil circle free for the festival beat"); return pc

    def dance_ring(cx):
        pc = Piece("dance_ring"); m = Mesh()
        m.add(cylinder(3.0, 3.0, 0.06, 20, BAS_HI, "stone", y0=0)); m.add(cylinder(2.7, 2.7, 0.07, 20, BAS, "stone", y0=0))
        for k in range(16):
            a = k * PI / 8
            m.add(box(0.5, 0.012, 0.08, LAVA if k % 2 else COPPER_HI, "glow", y0=0.075).xf((math.cos(a) * 2.35, 0, math.sin(a) * 2.35), rot=(0, -a, 0)))
        m.add(cylinder(0.9, 0.9, 0.012, 14, COPPER, "paint", y0=0.075)); m.add(cylinder(0.3, 0.3, 0.014, 10, LAVA_HI, "glow", y0=0.08))
        pc.mesh = m; pc.size = [6.0, 0.08, 6.0]; lamp(pc, (0, 0.4, 0), LAVA, 4.5, 0.0)
        pc.markers["note"] = "Emberfall fire-dance ring at [8,-2]; flat, walkable; pool_forge over it on festival days"; keep(pc, [-3.0, -3.0, 3.0, 3.0], 3.0, "festival ground: no props / spawns"); return pc

    def obsidian_pillar(cx):
        pc = Piece("obsidian_pillar"); m = Mesh()
        m.add(cylinder(0.9, 0.7, 0.4, 7, BAS_HI, "stone", y0=0)); m.add(cylinder(0.65, 0.5, 3.6, 7, BAS, "stone", y0=0.4))
        m.add(cylinder(0.75, 0.9, 0.35, 7, BAS_HI, "stone", y0=4.0))
        for k, (y, h) in enumerate(((0.8, 1.0), (2.0, 1.3), (3.3, 0.5))):
            m.add(box(0.05, h, 0.03, CF, "glow", y0=y).xf((0.18 * (-1) ** k, 0, 0.62)))                # frost-vein cracks
            m.add(box(0.025, h * .6, 0.03, CF_HI, "glow", y0=y + .1).xf((0.18 * (-1) ** k, 0, 0.64)))
        pc.mesh = m.ao(0, 4.5, 0.15); lamp(pc, (0, 2.0, 0.9), CF, 3.0); pc.size = [1.8, 4.4, 1.8]; pc.blockers.append([-.7, -.7, .7, .7])
        pc.markers["note"] = "basalt pillar with frost-vein cracks; the hidden spring [-11,-8.5] sits behind one"; return pc

    def amber_orb_chain(cx):
        pc = Piece("amber_orb_chain"); m = Mesh()
        for k in range(8):
            m.add(box(0.05, 0.1, 0.02, IRON, "paint", y0=2.9 - k * 0.14))
        m.add(cylinder(0.14, 0.1, 0.1, 6, IRON_HI, "paint", y0=1.85))
        m.add(sphere(0.3, 8, 5, WARM, "glow")); m.add(sphere(0.14, 6, 3, LAVA_HI, "glow"))
        m.parts if False else None
        pc.mesh = m.xf((0, 0, 0)); lamp(pc, (0, 1.6, 0), WARM, 5.5, 0.0); pc.size = [0.7, 3.0, 0.7]
        pc.markers["hanging"] = "molten-glass globe on a chain over streets, y 3 m; steady light (no flicker)"; return pc

    def spring_pool(cx):
        pc = Piece("spring_pool"); r = K.rng(cx.seed, "spring"); m = Mesh()
        m.add(cylinder(1.6, 1.5, 0.3, 10, BAS, "stone", y0=0))
        m.add(cylinder(1.3, 1.25, 0.04, 10, TEAL_LO, "glow", y0=0.3)); m.add(cylinder(0.9, 0.85, 0.05, 10, TEAL, "glow", y0=0.3))
        m.add(sphere(0.35, 8, 3, TEAL_HI, "glow", squash=(1.3, 0.12, 1.1)).xf((0.1, 0.35, -0.1)))
        for k in range(7):
            a = k * 2 * PI / 7
            m.add(sphere(0.25, 6, 3, mix(BAS, BAS_HI, (k % 3) / 3), "stone", squash=(1.2, .7, 1)).xf((math.cos(a) * 1.5, 0.22, math.sin(a) * 1.5)))
        pc.mesh = m.ao(0, 0.6, 0.15); lamp(pc, (0, 0.8, 0), TEAL, 4.0); pc.size = [3.4, 0.5, 3.4]; pc.blockers.append([-1.5, -1.5, 1.5, 1.5])
        pc.markers["note"] = "hidden bubbly spring (mp_spring / lf_spring / cd_spring): clear teal water; spring_bubbles billboard + pool_teal + two shrine_lamps; restores HP, +2 s fire-resist per drink"
        keep(pc, [-1.8, -1.8, 1.8, 1.8], 2.0, "drink radius; nothing else within 2 m"); return pc

    def warm_lantern(cx):
        pc = Piece("warm_lantern"); m = Mesh()
        m.add(cylinder(0.2, 0.16, 0.2, 6, BAS_HI, "stone", y0=0)); m.add(cylinder(0.05, 0.05, 1.7, 6, IRON, "paint", y0=0.2))
        m.add(beam([0, 1.85, 0], [0.35, 1.85, 0], 0.05, IRON, "paint"))
        m.add(box(0.26, 0.34, 0.26, WARM, "glow", y0=1.45).xf((0.35, 0, 0))); m.add(box(0.34, 0.05, 0.34, IRON_HI, "paint", y0=1.8).xf((0.35, 0, 0)))
        m.add(box(0.34, 0.05, 0.34, IRON_HI, "paint", y0=1.4).xf((0.35, 0, 0)))
        pc.mesh = m.ao(0, 2.0, 0.1); lamp(pc, (0.35, 1.6, 0.0), WARM, 5.0); pc.size = [0.8, 2.0, 0.4]; pc.blockers.append([-.2, -.2, .2, .2])
        pc.markers["note"] = "warm street lantern every 6-8 m: the grade stays amber-warm with blue/violet accents, never all red or all blue"; return pc

    def muspel_waystone(cx):
        pc = Piece("muspel_waystone"); m = Mesh()
        m.add(cylinder(1.5, 1.7, 0.3, 8, BAS_HI, "stone", y0=0)); m.add(cylinder(1.2, 1.3, 0.25, 8, BAS, "stone", y0=0.3))
        m.add(cylinder(0.55, 0.7, 2.4, 6, BAS, "stone", y0=0.55)); m.add(cylinder(0.1, 0.55, 0.7, 6, BAS_HI, "stone", y0=2.95))
        for k, y in enumerate((0.9, 1.4, 1.9, 2.4)):
            m.add(box(0.28 - k * .03, 0.07, 0.03, LAVA if k % 2 else LAVA_HI, "glow", y0=y).xf((0, 0, 0.6 - k * .02)))
        m.add(sphere(0.22, 7, 4, CF, "glow").xf((0, 3.85, 0))); m.add(sphere(0.1, 6, 3, CF_HI, "glow").xf((0, 3.85, 0)))
        for k in range(6):
            a = k * PI / 3
            m.add(box(0.5, 0.012, 0.07, LAVA, "glow", y0=0.56).xf((math.cos(a) * 1.0, 0, math.sin(a) * 1.0), rot=(0, -a, 0)))
        pc.mesh = m.ao(0, 4.2, 0.15); lamp(pc, (0, 1.2, 0.9), LAVA, 5.0); lamp(pc, (0, 3.8, 0), CF, 4.0); pc.size = [3.4, 4.1, 3.4]
        pc.blockers.append([-1.0, -1.0, 1.0, 1.0])
        keep(pc, [-1.8, -1.8, 1.8, 1.8], 2.6, "no props, spawns or fx within 2.6 m of the plinth; arrival point 2 m in front (+z); off stairs and ledge edges (Caldera C8 landing)")
        pc.markers["note"] = "Cinderhold waystone: warm runes + a cold-fire crown; pool_lava r 3 m under it"; return pc

    def cinder_cairn(cx):
        pc = Piece("cinder_cairn"); r = K.rng(cx.seed, "ccairn"); m = Mesh()
        y = 0.0
        for k in range(6):
            rad = 0.6 - k * .07; ht = 0.26 - k * .015
            m.add(sphere(rad, 7, 3, mix(BAS_HI, ASH, (k % 3) / 3), "stone", squash=(1.2, ht / rad, 1.1)).xf((r.uniform(-.04, .04), y + ht * .5, r.uniform(-.04, .04))))
            if k == 2:
                m.add(box(0.22, 0.04, 0.03, LAVA, "glow", y0=y + ht * .6).xf((0, 0, rad * 1.0)))
            y += ht * .85
        m.add(sphere(0.085, 6, 4, LAVA_HI, "glow").xf((0.04, y + 0.12, 0)))
        pc.mesh = m.ao(0, y + 0.4, 0.15); pc.size = [1.4, y + .3, 1.4]; lamp(pc, (0.04, y + .15, 0.1), LAVA, 2.4); pc.blockers.append([-.45, -.45, .45, .45])
        keep(pc, [-0.9, -0.9, 0.9, 0.9], 1.2, "trail marker; 1.2 m clear of spawns, stairs, ledge edges"); return pc

    # ======================================================================= Sigil Forge
    def forge_floor(cx):
        return floor_tile(Piece("forge_floor"), "forge_floor", cx.seed, "#5a4a50", "#76605c", None, 3, COPPER)

    def forge_wall(cx):
        pc = Piece("forge_wall"); m = Mesh()
        m.add(box(2.0, 4.4, 0.6, BAS, "stone", y0=0)); m.add(box(2.1, 0.3, 0.7, BAS_HI, "stone", y0=4.2)); m.add(box(2.1, 0.3, 0.7, BAS_LO, "stone", y0=0))
        m.add(box(0.7, 1.3, 0.06, LAVA, "window", y0=1.4).xf((0, 0, .32)))
        m.add(box(0.8, 0.1, 0.1, COPPER, "paint", y0=2.7).xf((0, 0, .34))); m.add(box(0.8, 0.1, 0.1, COPPER, "paint", y0=1.3).xf((0, 0, .34)))
        m.add(box(0.06, 1.3, 0.1, COPPER, "paint", y0=1.4).xf((0, 0, .34)))
        pc.mesh = m.ao(0, 4.6, 0.15); lamp(pc, (0, 1.9, .9), LAVA, 3.5); pc.size = [2.0, 4.4, 0.6]; pc.blockers.append([-1.0, -.3, 1.0, .3])
        pc.markers["note"] = "2 m wall module with a furnace window (warm pool on the floor in front)"; return pc

    def wardens_seat(cx):
        pc = Piece("wardens_seat"); m = Mesh()
        m.add(cylinder(2.0, 1.8, 0.4, 9, BAS_HI, "stone", y0=0)); m.add(cylinder(1.5, 1.3, 0.3, 9, BAS, "stone", y0=0.4))
        m.add(box(1.7, 0.8, 1.3, RED, "paint", y0=0.7)); m.add(box(1.7, 2.4, 0.4, RED_HI, "paint", y0=0.7).xf((0, 0, -0.6)))
        for sx in (-1, 1):
            m.add(box(0.3, 1.3, 1.3, RED_HI, "paint", y0=0.7).xf((sx * 1.0, 0, 0)))
        m.add(box(1.2, 0.08, 0.03, LAVA, "glow", y0=2.4).xf((0, 0, -0.38)))
        m.add(cylinder(0.4, 0.4, 0.04, 8, COPPER_HI, "paint", y0=1.5).xf((0, 0, -0.38), rot=(PI / 2, 0, 0)).xf((0, 0.6, 0)))
        pc.mesh = m.ao(0, 3.4, 0.15); lamp(pc, (0, 2.0, 0.6), WARM, 5.0); pc.size = [4.0, 3.4, 4.0]; pc.blockers.append([-1.3, -1.0, 1.3, 1.0])
        pc.markers["note"] = "the Warden's seat [0,-6.5]; a shrine_lamp 1.6 m either side; Aska stands in front"; return pc

    def seal_cast_bed(cx):
        pc = Piece("seal_cast_bed"); m = Mesh()
        m.add(box(3.0, 0.5, 1.6, BAS_HI, "stone", y0=0)); m.add(box(2.6, 0.04, 1.2, BAS_LO, "stone", y0=0.5))
        for k in range(3):
            m.add(cylinder(0.36, 0.36, 0.05, 10, LAVA if k != 1 else LAVA_LO, "glow", y0=0.52).xf((-0.9 + k * .9, 0, 0)))
            m.add(cylinder(0.2, 0.2, 0.012, 8, LAVA_HI if k != 1 else COPPER, "glow", y0=0.57).xf((-0.9 + k * .9, 0, 0)))
        for sx in (-1, 1):
            m.add(cylinder(0.08, 0.08, 0.5, 6, IRON, "paint", y0=0).xf((sx * 1.6, 0, -.6)))
        pc.mesh = m.ao(0, 0.9, 0.15); lamp(pc, (0, 0.8, 0.2), LAVA, 3.5); pc.size = [3.2, 0.7, 1.8]; pc.blockers.append([-1.5, -.8, 1.5, .8])
        pc.markers["clue"] = "sf_cast: the cooling cast-bed (the fake sigil was poured here) [-5.5,-3.0]"; return pc

    def stamp_press(cx):
        pc = Piece("stamp_press"); m = Mesh()
        m.add(box(1.4, 0.7, 1.0, BAS_HI, "stone", y0=0)); m.add(box(0.28, 2.0, 0.28, IRON, "paint", y0=0.7).xf((0, 0, -.3)))
        m.add(box(0.9, 0.2, 0.9, IRON_HI, "paint", y0=2.1).xf((0, 0, -.1))); m.add(cylinder(0.06, 0.06, 0.8, 6, IRON, "paint", y0=1.3).xf((0, 0, .2)))
        m.add(cylinder(0.3, 0.3, 0.1, 8, COPPER_HI, "paint", y0=1.2).xf((0, 0, .2)))
        m.add(box(0.5, 0.04, 0.5, LAVA, "glow", y0=0.7).xf((0, 0, .2)))
        beam_ = beam([0.5, 2.2, -.1], [0.9, 1.0, .3], 0.07, TIMBER_HI, "timber"); m.add(beam_); m.add(sphere(.12, 5, 3, COPPER, "paint").xf((0.9, 0.95, 0.3)))
        pc.mesh = m.ao(0, 2.5, 0.15); lamp(pc, (0, 0.9, 0.3), LAVA, 3.0); pc.size = [1.8, 2.4, 1.2]; pc.blockers.append([-.7, -.5, .7, .5])
        pc.markers["clue"] = "sf_mirror group: the stamp-press (foundry)"; return pc

    def ledger_desk(cx):
        pc = Piece("ledger_desk"); m = Mesh()
        m.add(box(1.8, 0.1, 0.9, TIMBER_HI, "timber", y0=0.8))
        for sx in (-1, 1):
            for sz in (-1, 1):
                m.add(cylinder(0.05, 0.05, 0.8, 6, TIMBER_LO, "timber", y0=0).xf((sx * 0.8, 0, sz * 0.35)))
        m.add(box(0.6, 0.06, 0.45, SAND, "paint", y0=0.9).xf((-.2, 0, 0))); m.add(box(0.4, 0.08, 0.3, RUST, "paint", y0=0.9).xf((.5, 0, .1)))
        m.add(box(0.1, 0.2, 0.1, WARM, "glow", y0=0.9).xf((.7, 0, -.3)))
        m.add(box(1.6, .5, .1, TIMBER, "timber", y0=.3).xf((0, 0, -.38)))
        pc.mesh = m.ao(0, 1.2, 0.1); lamp(pc, (.7, 1.2, -.3), WARM, 2.5); pc.size = [1.9, 1.1, 1.0]; pc.blockers.append([-.9, -.45, .9, .45])
        pc.markers["clue"] = "sf_ledger: the ledger desk"; return pc

    def sigil_mould_wall(cx):
        pc = Piece("sigil_mould_wall"); m = Mesh()
        m.add(box(5.0, 3.6, 0.5, BAS, "stone", y0=0)); m.add(box(5.2, 0.25, 0.6, BAS_HI, "stone", y0=3.5))
        for i in range(5):
            for j in range(2):
                x = -2.0 + i * 1.0; y = 0.7 + j * 1.3
                m.add(box(0.78, 0.78, 0.06, COPPER if (i + j) % 2 else IRON_HI, "paint", y0=y).xf((x, 0, .27)))
                m.add(cylinder(0.26, 0.26, 0.04, 8, LAVA_LO if (i == 2 and j == 0) else BAS_LO, "glow" if (i == 2 and j == 0) else "stone", y0=y + .2).xf((x, 0, .31), rot=(PI / 2, 0, 0)).xf((0, 0.2, 0)))
        pc.mesh = m.ao(0, 3.8, 0.15); lamp(pc, (0, 1.8, 1.0), LAVA, 4.0); pc.size = [5.2, 3.7, 0.7]; pc.blockers.append([-2.5, -.25, 2.5, .25])
        pc.markers["clue"] = "sf_mirror: the sigil mould wall, where real sigils are cast (one mould is cold and unused)"; return pc

    # ======================================================================= Lavafalls
    def lava_fall_cliff(cx):
        pc = Piece("lava_fall_cliff"); r = K.rng(cx.seed, "falls"); m = Mesh()
        m.add(box(4.0, 5.6, 1.2, BAS, "stone", y0=0).xf((0, 0, -.2)))
        for k in range(4):
            m.add(box(4.1 - k * .15, 0.5, 1.3, mix(BAS, BAS_HI, r.uniform(.2, .7)), "stone", y0=1.2 + k * 1.3).xf((0, 0, -.15)))
        for x in (-1.0, 0.9):
            m.add(box(0.9, 5.0, 0.08, LAVA_LO, "glow", y0=0.4).xf((x, 0, .42)))
            m.add(box(0.4, 5.0, 0.04, LAVA, "glow", y0=0.4).xf((x, 0, .45)))
            for k in range(5):
                m.add(box(0.14, r.uniform(.4, .9), 0.03, LAVA_HI, "glow", y0=0.8 + k * .9).xf((x + r.uniform(-.1, .1), 0, .48)))
        m.add(box(2.6, 0.08, 1.4, LAVA, "glow", y0=0.0).xf((0, 0, 1.0)))
        pc.mesh = m.ao(0, 5.8, 0.15); lamp(pc, (0, 1.0, 1.4), LAVA, 6.0, 0.0); pc.size = [4.2, 5.7, 2.4]; pc.blockers.append([-2.0, -.8, 2.0, .4])
        pc.markers["note"] = "molten falls cliff (4 m wide): lava_fall billboard tiles over each glow ribbon; pool_lava + lava_crawl at the foot (the fall-pool)"
        keep(pc, [-2.2, -.8, 2.2, 2.0], 2.0, "fall foot: 2 m of lava, no props or spawns"); return pc

    def glass_terrace(cx):
        pc = Piece("glass_terrace"); r = K.rng(cx.seed, "gterr"); m = Mesh()
        H = 1.2
        for k in range(3):
            m.add(box(3.0, 0.4, 2.0, mix(BAS, BAS_HI, r.uniform(0, .5)), "stone", y0=k * 0.4))
        m.add(box(3.1, 0.14, 2.1, GLASS, "paint", y0=H))
        for k in range(3):
            m.add(box(0.8, 0.012, 1.6, GLASS_HI if k % 2 else LAVA_LO, "glow", y0=H + .14).xf((-1.0 + k * 1.0, 0, 0)))
        for k in range(7):
            m.add(sphere(0.12, 5, 3, GLASS_HI, "glow", squash=(1.3, .7, 1)).xf((-1.3 + k * .43, H + .16, 1.0)))
        pc.mesh = m.ao(0, 1.4, 0.2); lamp(pc, (0, 1.5, 0.6), LAVA, 3.5); pc.size = [3.1, 1.34, 2.1]; pc.blockers.append([-1.5, -1.0, 1.5, 1.0])
        pc.markers["height_m"] = 1.34; pc.markers["ledge_edge"] = [[-1.5, 1.0], [1.5, 1.0]]; pc.markers["no_props_within_m"] = 0.8
        pc.markers["note"] = "glass terrace (1.34 m, like basalt_ledge): add one basalt_stair"; return pc

    def caldera_mouth_arch(cx):
        pc = Piece("caldera_mouth_arch"); m = Mesh()
        for sx in (-1, 1):
            m.add(box(1.0, 6.2, 1.4, BAS, "stone", y0=0).xf((sx * 2.65, 0, 0))); m.add(box(1.2, 0.3, 1.6, BAS_HI, "stone", y0=0).xf((sx * 2.65, 0, 0)))
            m.add(box(0.1, 5.0, 0.04, LAVA_LO, "glow", y0=0.6).xf((sx * 2.65, 0, 0.72)))
        m.add(box(6.6, 0.9, 1.4, BAS_HI, "stone", y0=6.0)); m.add(box(5.8, 0.5, 1.2, BAS, "stone", y0=6.9))
        m.add(box(3.9, 5.8, 0.4, BAS_LO, "stone", y0=0).xf((0, 0, -0.2)))
        for k in range(3):
            x = -1.2 + k * 1.2
            m.add(cylinder(0.4, 0.4, 0.08, 10, BAS_HI, "stone", y0=2.6).xf((x, 0, 0.0), rot=(PI / 2, 0, 0)).xf((0, 0.5, 0.1)))
            m.add(sphere(0.24, 7, 4, LAVA, "glow", squash=(1, 1, .35)).xf((x, 3.1, 0.12))); m.add(sphere(0.12, 6, 3, LAVA_HI, "glow", squash=(1, 1, .5)).xf((x, 3.1, 0.17)))
        m.add(box(3.4, 0.06, 0.02, LAVA_LO, "glow", y0=4.1).xf((0, 0, 0.0)))
        for k in range(9):
            m.add(box(0.07, 0.3, 0.02, CF if k % 2 else VIO, "glow", y0=4.4).xf((-1.5 + k * .38, 0, 0.0)))
        pc.mesh = m.ao(0, 7.4, 0.15); lamp(pc, (0, 3.2, 1.0), LAVA, 6.5); lamp(pc, (0, 4.6, 0.8), CF, 4.0); pc.size = [6.8, 7.4, 1.6]
        pc.blockers.append([-3.3, -.6, 3.3, .6]); pc.markers["seal_doors"] = 3
        pc.markers["note"] = "Caldera mouth [0,-7.5]: 6 m basalt arch sealed by three seal-doors (Warden's Flame / key-fire / Grettir's tunnel); keep 3 m clear in front"
        keep(pc, [-3.4, -1.0, 3.4, 3.0], 3.0, "3 m clear in front of the seal-doors"); return pc

    # ======================================================================= Ember Caldera
    def ember_throne(cx):
        pc = Piece("ember_throne"); m = Mesh()
        m.add(cylinder(2.6, 2.3, 0.5, 9, BAS_HI, "stone", y0=0)); m.add(cylinder(2.0, 1.7, 0.5, 9, BAS, "stone", y0=0.5))
        m.add(box(2.6, 1.0, 2.0, BAS_LO, "stone", y0=1.0)); m.add(box(2.6, 4.6, 0.6, BAS, "stone", y0=1.0).xf((0, 0, -0.9)))
        for sx in (-1, 1):
            m.add(box(0.5, 1.8, 2.0, BAS_HI, "stone", y0=1.0).xf((sx * 1.55, 0, 0)))
            m.add(beam([sx * 1.0, 5.0, -0.9], [sx * 1.9, 6.8, -0.9], 0.2, BAS_HI, "stone"))                    # horned back
            m.add(sphere(0.2, 6, 4, LAVA, "glow").xf((sx * 1.9, 6.9, -0.9)))
        m.add(cylinder(0.5, 0.0, 2.4, 5, BAS_HI, "stone", y0=5.4).xf((0, 0, -0.9)))
        for k in range(5):
            m.add(box(0.12, 0.8, 0.03, LAVA, "glow", y0=1.8 + (k % 2) * .7).xf((-0.9 + k * .45, 0, -0.58)))
        m.add(box(2.4, 0.05, 0.03, LAVA_LO, "glow", y0=0.55).xf((0, 0, 1.82)))
        pc.mesh = m.ao(0, 7.8, 0.15); lamp(pc, (0, 3.0, 0.6), LAVA, 7.0); pc.size = [5.4, 8.0, 5.2]
        pc.blockers.append([-2.4, -1.5, 2.4, 1.5]); pc.markers["boss_stand"] = [0, 0, 3.6]
        pc.markers["note"] = "C9 Ember Throne, back centre; Vharzul (8x) stands in front (boss_stand z +3.6); lava_crawl ring on the arena edge rises in phase 2"; return pc

    def warden_lamp_stand(cx):
        pc = Piece("warden_lamp_stand"); m = Mesh()
        m.add(cylinder(0.5, 0.6, 0.3, 8, BAS_HI, "stone", y0=0)); m.add(cylinder(0.2, 0.26, 2.2, 8, BAS, "stone", y0=0.3))
        m.add(cylinder(0.5, 0.3, 0.3, 8, COPPER, "paint", y0=2.5)); flame(m, 2.85, 1.0, VIO, VIO_HI)
        for k in range(4):
            m.add(box(0.05, 0.3, 0.02, VIO if k % 2 else COPPER_HI, "glow", y0=0.8 + k * .4).xf((0, 0, 0.27)))
        pc.mesh = m.ao(0, 3.8, 0.1); lamp(pc, (0, 2.9, 0), VIO, 5.5); pc.size = [1.2, 3.8, 1.2]; pc.blockers.append([-.4, -.4, .4, .4])
        pc.markers["note"] = "one of the three Warden's lamps (Vharzul P3): violet until relit; warden_lamp fx over it; place on the arena ring at 120 degrees, outside the safe ring"; return pc

    def furnace(cx):
        pc = Piece("furnace"); m = Mesh()
        m.add(box(4.0, 3.0, 2.4, BAS, "stone", y0=0)); m.add(box(4.2, 0.3, 2.6, BAS_HI, "stone", y0=3.0))
        m.add(box(1.8, 1.6, 0.2, BAS_LO, "stone", y0=0.5).xf((0, 0, 1.25))); m.add(box(1.4, 1.2, 0.08, LAVA, "glow", y0=0.7).xf((0, 0, 1.32)))
        m.add(box(0.8, 0.7, 0.04, LAVA_HI, "glow", y0=0.9).xf((0, 0, 1.36)))
        m.add(cylinder(0.7, 0.55, 2.8, 8, BAS_HI, "stone", y0=3.3).xf((1.0, 0, -0.4))); m.add(box(0.7, 0.1, 0.7, LAVA, "glow", y0=6.0).xf((1.0, 0, -0.4)))
        for sx in (-1, 1):
            m.add(box(0.1, 2.4, 0.04, COPPER, "paint", y0=0.3).xf((sx * 1.8, 0, 1.22)))
        pc.mesh = m.ao(0, 6.2, 0.15); lamp(pc, (0, 1.2, 1.9), LAVA, 6.0); pc.size = [4.2, 6.2, 2.7]; pc.blockers.append([-2.0, -1.2, 2.0, 1.2])
        pc.markers["note"] = "C4 Furnace Hall: fire golems wake from the walls around it; heart-coal hc_1 sits in the mouth; heat_shimmer over the chimney"
        keep(pc, [-2.2, -1.3, 2.2, 3.2], 3.0, "3 m clear in front of the mouth"); return pc

    def hanging_crystals(cx):
        pc = Piece("hanging_crystals"); m = Mesh()
        m.add(box(2.0, 0.3, 1.0, BAS, "stone", y0=3.0))
        for (x, ln, rr, z) in ((-.6, 1.6, .22, .1), (0.1, 2.4, .3, -.1), (.7, 1.2, .18, .2), (-.1, 1.0, .14, .3)):
            m.add(cylinder(rr, 0.0, ln, 6, CF_HI if (x > 0) else CF, "glow", y0=3.0 - ln).xf((x, 0, z), rot=(PI, 0, 0)).xf((0, 2 * 3.0 - ln + 0.0, 0)) if False else cylinder(0.0, rr, ln, 6, CF if x < 0 else VIO, "glow", y0=3.0 - ln).xf((x, 0, z)))
        pc.mesh = m; lamp(pc, (0, 2.0, 0.3), CF, 5.0); pc.size = [2.0, 3.3, 1.2]
        pc.markers["hanging"] = "ceiling piece: hangs at y 3.0 m (cavern ceilings, Cold Seam, springs of glass); glow_crystals_blue/violet billboards add the twinkle"; return pc

    def cold_seam_wall(cx):
        pc = Piece("cold_seam_wall"); r = K.rng(cx.seed, "seam"); m = Mesh()
        m.add(box(2.0, 4.4, 0.6, BAS, "stone", y0=0)); m.add(box(2.1, 0.3, 0.7, BAS_HI, "stone", y0=4.2)); m.add(box(2.1, 0.3, 0.7, BAS_LO, "stone", y0=0))
        y, x = 0.3, -0.7
        for k in range(9):
            nx = x + r.uniform(0.1, 0.35) * (1 if k % 3 else -1.2); ny = y + 0.48
            m.add(beam([x, y, .32], [nx, ny, .32], 0.09, CF, "glow")); m.add(beam([x, y, .34], [nx, ny, .34], 0.035, CF_HI, "glow"))
            x, y = max(-0.9, min(0.9, nx)), ny
        pc.mesh = m.ao(0, 4.6, 0.15); lamp(pc, (0, 2.2, 0.9), CF, 5.0); pc.size = [2.0, 4.4, 0.6]; pc.blockers.append([-1.0, -.3, 1.0, .3])
        pc.markers["note"] = "C5 Cold Seam: a frost vein bright blue against orange rock (Veyra's beat); pool_cold in front, frost_vein decal on the floor, wedge 2 nearby"; return pc

    fns = [warm_lantern, basalt_floor, lava_channel, lava_pool, basalt_ledge, basalt_stair, warden_stones, basalt_house, forge_hall, red_arch, spice_stall,
           brazier_stand, cold_brazier, shrine_lamp, glass_bridge, lizard_stable, emberfall_anvil, dance_ring, obsidian_pillar, amber_orb_chain, spring_pool,
           muspel_waystone, cinder_cairn, forge_floor, forge_wall, wardens_seat, seal_cast_bed, stamp_press, ledger_desk, sigil_mould_wall,
           lava_fall_cliff, glass_terrace, caldera_mouth_arch, ember_throne, warden_lamp_stand, furnace, hanging_crystals, cold_seam_wall]
    return {f.__name__: f for f in fns}
