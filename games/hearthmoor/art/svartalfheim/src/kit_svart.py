"""Svartalfheim / Clockwork Deep pieces for hd2d kit (original; Hearthmoor Art seat staging, 2026-10-14).
  deep_floor 2x2 m basalt tile with cold-blue rune seams      deep_wall 2 m basalt wall, rune band + violet crystal vein
  rail_straight 2 m mine rail on sleepers                       mine_cart iron cart on wheels, heaped with neon-tipped violet crystal
  gear_wall 2.4 m brass gear pair on an iron frame              crystal_cluster violet crystals with neon tips (Amethyst Mines)
  rune_lamp 2.4 m iron post with a cold-blue rune flame         forge_brazier 1.1 m iron brazier, forge-fire red
  glow_pool 3x2 m glowing underground water (blue-green)        anvil_pillar Gorrak's chain anvil-pillar (boss room)
Drop-in like kit_harbor:  import kit_svart as _sv; PROPS.update(_sv.pieces(types.SimpleNamespace(**globals())))
Neon hexes only on the 'glow' material (rune seams, crystal tips, flames, water)."""
import math
PI = math.pi
NV, NV_HI, NV_LO = "#a45cf0", "#d4a8ff", "#6a34b8"
NB, NB_HI, NB_LO = "#2ab4ff", "#a6ecff", "#1c62d8"
NR, NR_HI, NR_LO = "#e0302a", "#ff5a4a", "#a81c22"
WATER, WATER_HI = "#1fb0a8", "#7af0e0"
BASALT, BASALT_HI, IRON, IRON_HI, BRASS, BRASS_HI, COPPER = "#24222a", "#3a3742", "#4a4850", "#6e6c74", "#c09040", "#e8c060", "#b8643a"


def pieces(K):
    box, cylinder, sphere, beam, mix, Piece, Mesh = K.box, K.cylinder, K.sphere, K.beam, K.mix, K.Piece, K.Mesh

    def lamp(pc, pos, col, rng_):
        pc.markers["lamps"].append(list(pos)); pc.markers["lamp_color"] = col; pc.markers["lamp_range"] = rng_; pc.markers["lamp_fixed"] = 0.5

    def crystal(m, pos, h, r, tilt=(0, 0)):
        c = Mesh()
        c.add(cylinder(r, r * 0.9, h * 0.75, 6, mix(NV_LO, "#1a1030", 0.35), "stone", y0=0))
        c.add(cylinder(r * 0.9, 0.0, h * 0.25, 6, NV_HI, "glow", y0=h * 0.75))     # neon tip
        c.add(box(r * 0.2, h * 0.6, r * 0.2, NV, "glow", y0=h * 0.1).xf((-r * 0.5, 0, r * 0.6)))
        m.add(c.xf((0, 0, 0), rot=(tilt[0], 0, tilt[1])).xf(pos))

    def gear(m, pos, R, t, teeth, col, hi):
        g = Mesh()
        g.add(cylinder(R, R, t, 16, col, "paint", y0=0))
        g.add(cylinder(R * 0.3, R * 0.3, t * 1.4, 8, IRON, "paint", y0=-t * 0.2))
        for k in range(teeth):
            a = k * 2 * PI / teeth
            g.add(box(R * 0.22, t, R * 0.22, hi, "paint", y0=0).xf((math.cos(a) * R * 1.05, 0, math.sin(a) * R * 1.05)))
        m.add(g.xf((0, 0, 0), rot=(PI / 2, 0, 0)).xf(pos))

    def deep_floor(cx):
        pc = Piece("deep_floor"); r = K.rng(cx.seed, "dfloor"); m = Mesh()
        for i in range(4):
            for j in range(4):
                x0, z0 = -1 + i * 0.5, -1 + j * 0.5
                m.quad((x0, 0, z0 + 0.5), (x0 + 0.5, 0, z0 + 0.5), (x0 + 0.5, 0, z0), (x0, 0, z0), mix(BASALT, BASALT_HI, r.uniform(0, 0.5)), mat="stone")
        m.add(box(2.0, 0.006, 0.03, NB_LO, "glow", y0=0).xf((0, 0, 0)))
        pc.mesh = m; pc.size = [2, 0.01, 2]; return pc

    def deep_wall(cx):
        pc = Piece("deep_wall"); r = K.rng(cx.seed, "dwall"); m = Mesh()
        for k in range(5):
            m.add(box(2.0, 0.64, 0.5, mix(BASALT, BASALT_HI, r.uniform(0, 0.6)), "stone", y0=k * 0.64))
        m.add(box(2.0, 0.05, 0.02, NB, "glow", y0=1.4).xf((0, 0, 0.26)))
        for k in range(6):
            m.add(box(0.06, 0.12, 0.02, NB_HI, "glow", y0=1.3).xf((-0.8 + k * 0.32, 0, 0.27)))
        crystal(m, (0.6, 0.0, 0.3), 0.7, 0.12, (0.3, 0.2)); crystal(m, (0.8, 0, 0.32), 0.45, 0.09, (0.4, -0.3))
        pc.mesh = m.ao(0, 3.2, 0.15); lamp(pc, (0, 1.4, 0.4), NB, 3.0); pc.size = [2, 3.2, 0.5]
        pc.blockers.append([-1, -0.25, 1, 0.25]); return pc

    def rail_straight(cx):
        pc = Piece("rail_straight"); m = Mesh()
        for k in range(5):
            m.add(box(0.9, 0.06, 0.14, cx.c("timber_lo"), "timber", y0=0).xf((0, 0, -0.8 + k * 0.4)))
        for x in (-0.3, 0.3):
            m.add(box(0.05, 0.07, 2.0, IRON_HI, "paint", y0=0.06).xf((x, 0, 0)))
        pc.mesh = m; pc.size = [0.9, 0.13, 2.0]; pc.markers["track_gauge"] = 0.6; return pc

    def mine_cart(cx):
        pc = Piece("mine_cart"); m = Mesh()
        m.add(box(0.8, 0.5, 1.1, IRON, "paint", y0=0.2))
        m.add(box(0.84, 0.06, 1.14, COPPER, "paint", y0=0.66))
        for x in (-0.3, 0.3):
            for z in (-0.35, 0.35):
                m.add(cylinder(0.14, 0.14, 0.06, 10, BASALT_HI, "paint", y0=0).xf((0, 0, 0), rot=(0, 0, PI / 2)).xf((x * 1.25, 0.14, z)))
        for k, (x, z, h) in enumerate(((-0.2, -0.2, 0.5), (0.15, 0.1, 0.4), (0, 0.3, 0.35), (0.2, -0.3, 0.3))):
            crystal(m, (x, 0.6, z), h, 0.09, (0.25 * (k % 2 * 2 - 1), 0.2))
        pc.mesh = m.ao(0, 1.0, 0.1); lamp(pc, (0, 0.9, 0), NV, 2.2); pc.size = [0.84, 1.1, 1.14]
        pc.blockers.append([-0.45, -0.6, 0.45, 0.6]); return pc

    def gear_wall(cx):
        pc = Piece("gear_wall"); m = Mesh()
        for x in (-1.1, 1.1):
            m.add(box(0.2, 2.4, 0.2, IRON, "paint", y0=0).xf((x, 0, 0)))
        m.add(box(2.4, 0.2, 0.2, IRON, "paint", y0=2.3))
        gear(m, (-0.35, 1.25, 0.15), 0.7, 0.1, 12, BRASS, BRASS_HI)
        gear(m, (0.65, 0.75, 0.2), 0.42, 0.1, 9, COPPER, BRASS_HI)
        m.add(sphere(0.08, 6, 4, NB_HI, "glow").xf((-0.35, 1.25, 0.28)))
        pc.mesh = m.ao(0, 2.5, 0.1); lamp(pc, (-0.35, 1.25, 0.4), NB, 2.0); pc.size = [2.4, 2.5, 0.4]
        pc.blockers.append([-1.2, -0.2, 1.2, 0.3]); return pc

    def crystal_cluster(cx):
        pc = Piece("crystal_cluster"); r = K.rng(cx.seed, "ccl"); m = Mesh()
        m.add(sphere(0.6, 7, 4, BASALT_HI, "stone", squash=(1, 0.35, 0.8)))
        for k in range(7):
            a = k * 2 * PI / 7 + r.uniform(0, 0.4)
            crystal(m, (math.cos(a) * 0.3, 0.1, math.sin(a) * 0.25), r.uniform(0.6, 1.4), r.uniform(0.09, 0.16), (math.sin(a) * 0.4, math.cos(a) * 0.4))
        crystal(m, (0, 0.1, 0), 1.7, 0.2)
        pc.mesh = m.ao(0, 1.8, 0.1); lamp(pc, (0, 1.0, 0.3), NV, 4.5); pc.size = [1.4, 1.8, 1.2]
        pc.blockers.append([-0.6, -0.5, 0.6, 0.5]); return pc

    def rune_lamp(cx):
        pc = Piece("rune_lamp"); m = Mesh()
        m.add(cylinder(0.2, 0.16, 0.2, 6, BASALT_HI, "stone", y0=0))
        m.add(cylinder(0.06, 0.06, 2.0, 6, IRON, "paint", y0=0.2))
        m.add(cylinder(0.18, 0.22, 0.12, 6, IRON_HI, "paint", y0=2.15))
        m.add(cylinder(0.1, 0.0, 0.36, 6, NB, "glow", y0=2.27)); m.add(cylinder(0.05, 0.0, 0.22, 6, NB_HI, "glow", y0=2.27))
        m.add(box(0.03, 0.4, 0.02, NB_LO, "glow", y0=0.9).xf((0, 0, 0.065)))
        pc.mesh = m.ao(0, 2.6, 0.1); lamp(pc, (0, 2.35, 0.1), NB, 5.0); pc.size = [0.44, 2.63, 0.44]; return pc

    def forge_brazier(cx):
        pc = Piece("forge_brazier"); m = Mesh()
        for k in range(3):
            a = k * 2 * PI / 3
            m.add(beam([0, 0.8, 0], [math.cos(a) * 0.35, 0, math.sin(a) * 0.35], 0.06, IRON, "paint"))
        m.add(cylinder(0.32, 0.4, 0.22, 10, IRON_HI, "paint", y0=0.78))
        m.add(sphere(0.3, 7, 4, NR, "glow", squash=(1, 0.4, 1)).xf((0, 1.0, 0)))
        m.add(cylinder(0.18, 0.0, 0.3, 6, NR_HI, "glow", y0=1.0))
        pc.mesh = m.ao(0, 1.3, 0.1); lamp(pc, (0, 1.15, 0.1), NR, 4.5); pc.size = [0.8, 1.3, 0.8]; return pc

    def glow_pool(cx):
        pc = Piece("glow_pool"); m = Mesh()
        for k in range(16):
            a0, a1 = k * 2 * PI / 16, (k + 1) * 2 * PI / 16
            m.quad((0, 0.02, 0), (math.cos(a0) * 1.5, 0.02, math.sin(a0)), (math.cos(a1) * 1.5, 0.02, math.sin(a1)), (0, 0.02, 0), WATER, mat="glow")
            m.add(box(0.35, 0.12, 0.25, BASALT_HI, "stone", y0=0).xf((math.cos(a0) * 1.6, 0, math.sin(a0) * 1.1)))
        for (x, z) in ((-0.5, 0.2), (0.4, -0.3), (0.1, 0.4)):
            m.add(box(0.12, 0.004, 0.05, WATER_HI, "glow", y0=0.025).xf((x, 0, z)))
        pc.mesh = m; lamp(pc, (0, 0.4, 0), WATER, 4.0); pc.size = [3.4, 0.12, 2.4]
        pc.blockers.append([-1.5, -1.0, 1.5, 1.0]); return pc

    def anvil_pillar(cx):
        pc = Piece("anvil_pillar"); m = Mesh()
        m.add(cylinder(1.2, 1.0, 0.4, 8, BASALT_HI, "stone", y0=0))
        m.add(cylinder(0.55, 0.55, 3.2, 8, BASALT, "stone", y0=0.4))
        m.add(box(1.6, 0.5, 0.8, IRON, "paint", y0=3.6)); m.add(box(2.2, 0.15, 0.6, IRON_HI, "paint", y0=4.1))
        for k in range(4):
            m.add(box(1.12, 0.06, 0.02, NB, "glow", y0=1.0 + k * 0.7).xf((0, 0, 0.56)))
        for x in (-0.6, 0.6):
            m.add(beam([x, 2.6, 0.5], [x * 2.4, 0.3, 1.4], 0.07, IRON_HI, "paint"))
        pc.mesh = m.ao(0, 4.3, 0.15); lamp(pc, (0, 2.0, 0.8), NB, 5.0); pc.size = [2.4, 4.25, 2.4]
        pc.markers["boss_stand"] = [0, 0, 2.2]; pc.blockers.append([-1.2, -1.2, 1.2, 1.2]); return pc

    return {f.__name__: f for f in (deep_floor, deep_wall, rail_straight, mine_cart, gear_wall, crystal_cluster, rune_lamp,
                                    forge_brazier, glow_pool, anvil_pillar)}
