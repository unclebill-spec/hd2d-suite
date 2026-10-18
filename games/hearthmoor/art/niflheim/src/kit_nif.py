"""Niflheim kit pieces (original; Hearthmoor Art seat staging, 2026-10-18). Built with the repo's kit.py / meshlib like kit_jotun.py; the ice set is
reused from Jotunheim (kit_jotun_base.py: snow_floor, ice_lake, ice_floor, ice_wall, glow_ice_pool, icicle_cluster, ice_crystal_cluster, frost_rune_pillar,
barrow_door -> spire_mouth_door, rune_bridge -> rime_bridge, ice_throne -> kael_perch, rune_waystone, stone_cairn, glow_orb_chain, cold_brazier, warm_lantern)
plus new pieces:
 Mistmere : frost_ledge (1.34 m) + frost_stair (7 steps), mist_arch, lantern_post, speaker_hall, fish_stall, elk_paddock, eira_grave, ashmantle_house,
            shard_window, spring_pool, rune_hall, glow_vine
 Frozen Spire: spire_gate, banner_hall_banner, mirror_pane, glacier_heart, archive_tablets, crown_stair, frozen_portal, crown_platform, spire_pillar
Neon hexes only on the 'glow' material (cold fire, runes, crystal tips, aurora panes, violet lamps). Placement notes live in kit.json markers."""
import math
import kit_jotun_base as KB
from kit_jotun_base import (STONE, STONE_HI, STONE_LO, SNOW, SNOW_SH, SNOW_HI, TIMBER, TIMBER_HI, TIMBER_LO, IRON, IRON_HI, WARM, CF, CF_HI, CF_LO, RUNE, ORB,
                            POOL, POOL_HI, ICE, ICE_HI, ICE_DEEP, AUR_G, AUR_V)
PI = math.pi
RED, RED_HI = "#8a2a2a", "#c03a30"
VIO, VIO_HI = "#a45cf0", "#d4a8ff"
BLK = "#14182a"


def pieces(K):
    base = KB.pieces(K)
    box, cylinder, sphere, beam, mix, Piece, Mesh, prism_x = K.box, K.cylinder, K.sphere, K.beam, K.mix, K.Piece, K.Mesh, K.prism_x

    def lamp(pc, pos, col, rng_, fixed=0.5):
        pc.markers["lamps"].append(list(pos)); pc.markers["lamp_color"] = col; pc.markers["lamp_range"] = rng_; pc.markers["lamp_fixed"] = fixed

    def keep(pc, fp, radius, note):
        pc.markers["keep_clear"] = {"footprint_m": fp, "radius_m": radius, "note": note}

    def wrap(src, new, note=None):
        def f(cx):
            pc = base[src](cx)
            pc.name = new
            if note:
                pc.markers["note"] = note
            return pc
        f.__name__ = new
        return f

    def frost_ledge(cx):
        pc = base["stone_ledge"](cx); pc.name = "frost_ledge"; return pc

    def frost_stair(cx):
        """7 steps, 0.191 m rise each = 1.34 m exactly (flush with frost_ledge top)"""
        pc = Piece("frost_stair"); m = Mesh()
        n, rise, run, wd = 7, 1.34, 0.5, 2.0
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
        pc.mesh = m.ao(0, 1.9, 0.2); pc.kind = "stairs"; pc.size = [wd + 0.6, rise + 0.5, L]
        pc.stairs = {"width": wd, "rise": rise, "length": L, "steps": n}
        for sx in (-1, 1):
            lamp(pc, (sx * (wd / 2 + 0.15), 1.1, L / 2 - 0.1), CF, 3.0)
        pc.markers["no_props_within_m"] = 1.0; pc.markers["note"] = "keep props, fx and spawns off the stair footprint (+1 m each end); top flush with frost_ledge (1.34 m)"; return pc

    def mist_arch(cx):
        pc = Piece("mist_arch"); m = Mesh()
        for sx in (-1, 1):
            m.add(box(0.9, 4.6, 0.9, STONE, "stone", y0=0).xf((sx * 2.0, 0, 0)))
            m.add(box(1.0, 0.3, 1.0, STONE_HI, "stone", y0=4.6).xf((sx * 2.0, 0, 0)))
            m.add(cylinder(0.32, 0.12, 1.4, 6, ICE_HI, "paint", y0=4.9).xf((sx * 2.0, 0, 0)))
        for k in range(9):                                            # ice arch: stepped spans
            a = PI * k / 8
            m.add(sphere(0.3, 7, 4, mix(ICE, ICE_HI, k % 3 / 3), "paint", squash=(1.1, .9, 1)).xf((math.cos(a) * 2.0, 4.6 + math.sin(a) * 1.4, 0)))
        for k in range(7):
            a = PI * (k + .5) / 8
            m.add(box(0.06, 0.2, 0.02, RUNE, "glow", y0=0).xf((math.cos(a) * 2.0, 4.5 + math.sin(a) * 1.45, 0.34)))
        m.add(box(3.1, 0.05, 0.02, CF, "glow", y0=0.08).xf((0, 0, 0.46)))
        pc.mesh = m.ao(0, 6.2, 0.15); lamp(pc, (0, 3.0, 1.0), CF, 6.0); pc.size = [4.9, 6.2, 1.0]
        pc.blockers += [[-2.5, -.5, -1.5, .5], [1.5, -.5, 2.5, .5]]
        pc.markers["note"] = "Mistmere's ice arch to Bifrost [0,10.6]; arrival [0,9.2,'up']; nothing within 2.6 m"
        keep(pc, [-2.0, -1.0, 2.0, 3.0], 2.6, "arrival ring"); return pc

    def lantern_post(cx):
        pc = Piece("lantern_post"); m = Mesh()
        m.add(cylinder(0.1, 0.07, 2.8, 6, IRON, "paint", y0=0)); m.add(beam([0, 2.6, 0], [0.45, 2.7, 0], 0.045, IRON, "paint"))
        m.add(box(0.28, 0.4, 0.28, IRON, "paint", y0=2.45).xf((0.5, 0, 0))); m.add(box(0.2, 0.3, 0.2, CF, "glow", y0=2.5).xf((0.5, 0, 0)))
        m.add(sphere(0.07, 6, 3, CF_HI, "glow").xf((0.5, 2.65, 0)))
        m.add(box(0.5, 0.2, 0.5, STONE, "stone", y0=0).xf((0, 0, 0)))
        pc.mesh = m.ao(0, 3.0, 0.1); lamp(pc, (0.5, 2.55, 0), CF, 5.0); pc.size = [1.0, 3.0, 0.6]; pc.blockers.append([-.25, -.25, .25, .25])
        pc.markers["note"] = "Mistmere cold-fire lantern posts [-7,4] [0,5] [7,4]; lantern_float fx at the cage; a warm_lantern within 6 m"; return pc

    def speaker_hall(cx):
        pc = Piece("speaker_hall"); m = Mesh()
        m.add(box(5.0, 3.0, 3.4, STONE, "stone", y0=0)); m.add(box(5.4, 0.3, 3.8, STONE_HI, "stone", y0=3.0))
        m.add(prism_x(5.6, [(-1.9, 3.3), (1.9, 3.3), (0, 4.6)], SNOW, "paint").xf((0, 0, 0), rot=(0, PI / 2, 0)) if False else box(5.4, 0.9, 3.8, SNOW, "paint", y0=3.3))
        m.add(box(1.5, 2.3, 0.2, TIMBER_LO, "timber", y0=0).xf((0, 0, 1.75)))
        m.add(box(1.7, 0.2, 0.3, STONE_HI, "stone", y0=2.3).xf((0, 0, 1.78)))
        for sx in (-1, 1):
            m.add(box(0.5, 0.7, 0.05, WARM, "window", y0=1.2).xf((sx * 1.6, 0, 1.72)))
        for k in range(5):
            m.add(box(0.07, 0.3, 0.02, RUNE, "glow", y0=2.55).xf((-0.6 + k * .3, 0, 1.9)))
        pc.mesh = m.ao(0, 4.2, 0.15); lamp(pc, (0, 1.4, 2.4), WARM, 5.0); lamp(pc, (0, 2.6, 2.2), CF, 4.0); pc.size = [5.4, 4.2, 3.8]; pc.blockers.append([-2.6, -1.8, 2.6, 1.8])
        pc.markers["note"] = "frost-speaker hall [0,-9.6]: Gudrun's hall, door faces +z; 2 m clear in front"; keep(pc, [-1.5, 1.8, 1.5, 3.8], 2.0, "door"); return pc

    def fish_stall(cx):
        pc = Piece("fish_stall"); m = Mesh()
        for sx in (-1, 1):
            for sz in (-1, 1):
                m.add(cylinder(0.07, 0.07, 2.1, 6, TIMBER_HI, "timber", y0=0).xf((sx * 1.0, 0, sz * 0.6)))
        m.add(box(2.4, 0.12, 1.5, TIMBER, "timber", y0=2.1)); m.add(box(2.5, 0.2, 1.6, SNOW, "paint", y0=2.22))
        m.add(box(2.0, 0.8, 0.7, TIMBER_LO, "timber", y0=0).xf((0, 0, 0.1))); m.add(box(2.0, 0.08, 0.7, SNOW_SH, "paint", y0=0.8).xf((0, 0, 0.1)))
        for k in range(5):
            m.add(box(0.08, 0.5, 0.02, ICE_HI if k % 2 else ICE, "paint", y0=1.25).xf((-0.8 + k * .4, 0, -0.55)))
        m.add(box(0.2, 0.2, 0.2, WARM, "window", y0=1.8).xf((0.7, 0, 0.6)))
        pc.mesh = m.ao(0, 2.5, 0.15); lamp(pc, (0.7, 1.9, 0.9), WARM, 4.0); pc.size = [2.6, 2.5, 1.7]; pc.blockers.append([-1.2, -.7, 1.2, .8])
        pc.markers["note"] = "Tove's fish-stall [-8.5,-3], counter faces +z; 1.5 m clear in front"; return pc

    def elk_paddock(cx):
        pc = Piece("elk_paddock"); m = Mesh()
        for k in range(7):
            x = -1.8 + k * 0.6
            m.add(cylinder(0.06, 0.06, 1.2, 6, TIMBER_HI, "timber", y0=0).xf((x, 0, -1.4))); m.add(cylinder(0.06, 0.06, 1.2, 6, TIMBER_HI, "timber", y0=0).xf((x, 0, 1.4)))
        m.add(box(3.8, 0.08, 0.08, TIMBER, "timber", y0=0.9).xf((0, 0, -1.4))); m.add(box(3.8, 0.08, 0.08, TIMBER, "timber", y0=0.9).xf((0, 0, 1.4)))
        m.add(box(0.08, 0.08, 2.8, TIMBER, "timber", y0=0.9).xf((-1.9, 0, 0))); m.add(box(0.08, 0.08, 2.8, TIMBER, "timber", y0=0.9).xf((1.9, 0, 0)))
        m.add(box(1.0, 0.3, 0.5, TIMBER_LO, "timber", y0=0).xf((1.1, 0, 0.8))); m.add(box(0.9, 0.1, 0.4, "#c8a050", "paint", y0=0.3).xf((1.1, 0, 0.8)))
        pc.mesh = m.ao(0, 1.4, 0.1); pc.size = [4.0, 1.4, 3.0]
        for b in ([-1.9, -1.45, 1.9, -1.35], [-1.9, 1.35, 1.9, 1.45]):
            pc.blockers.append(b)
        pc.markers["note"] = "Ketil's elk paddock [9,-3]; gate gap on the -x side; the elk are runtime NPCs inside (not in this kit)"; return pc

    def eira_grave(cx):
        pc = Piece("eira_grave"); m = Mesh()
        m.add(box(1.4, 0.18, 2.2, SNOW, "paint", y0=0)); m.add(box(0.7, 1.3, 0.2, STONE_HI, "stone", y0=0.1).xf((0, 0, -0.8)))
        m.add(box(0.8, 0.12, 0.3, STONE, "stone", y0=1.4).xf((0, 0, -0.8)))
        for k in range(4):
            m.add(box(0.05, 0.2, 0.02, VIO_HI, "glow", y0=0.5 + k * .22).xf((0, 0, -0.69)))
        for sx in (-1, 1):
            m.add(cylinder(0.04, 0.04, 0.7, 6, IRON, "paint", y0=0).xf((sx * 0.8, 0, -0.3))); m.add(sphere(0.12, 7, 4, VIO, "glow").xf((sx * 0.8, 0.8, -0.3)))
            m.add(sphere(0.06, 6, 3, VIO_HI, "glow").xf((sx * 0.8, 0.82, -0.3)))
        m.add(sphere(0.18, 6, 3, SNOW_SH, "paint", squash=(1.6, .6, 1)).xf((0, 0.2, 0.3)))
        pc.mesh = m.ao(0, 1.6, 0.1); lamp(pc, (0, 0.9, 0.0), VIO, 4.5); pc.size = [1.8, 1.6, 2.4]; pc.blockers.append([-.4, -.95, .4, -.65])
        pc.markers["note"] = "Eira's grave [0,-4] (nf_home): the memory scene; two violet lamps; eira_outline fx stands at z +0.6; 2 m clear"; keep(pc, [-1.0, -1.2, 1.0, 1.4], 2.0, "memory scene"); return pc

    def ashmantle_house(cx):
        pc = Piece("ashmantle_house"); m = Mesh()
        m.add(box(4.6, 2.6, 3.6, STONE, "stone", y0=0)); m.add(box(5.0, 0.3, 4.0, STONE_HI, "stone", y0=2.6)); m.add(box(5.0, 1.0, 4.0, SNOW, "paint", y0=2.9))
        m.add(box(1.1, 2.0, 0.2, TIMBER_LO, "timber", y0=0).xf((0.6, 0, 1.8)))
        m.add(box(0.9, 0.8, 0.05, WARM, "window", y0=1.1).xf((-1.4, 0, 1.82)))
        m.add(box(0.7, 0.7, 0.05, WARM, "window", y0=1.3).xf((-0.2, 0, -1.82)))
        m.add(cylinder(0.3, 0.3, 1.4, 6, STONE_HI, "stone", y0=3.9).xf((-1.4, 0, -0.8)))
        for k in range(4):
            m.add(box(0.06, 0.22, 0.02, RUNE, "glow", y0=2.05).xf((0.15 + k * .3, 0, 1.92)))
        pc.mesh = m.ao(0, 5.4, 0.15); lamp(pc, (-1.4, 1.5, 2.4), WARM, 5.0); lamp(pc, (0.6, 1.0, 2.5), WARM, 3.0); pc.size = [5.0, 5.4, 4.0]; pc.blockers.append([-2.4, -1.8, 2.4, 1.8])
        pc.markers["note"] = "Ashmantle House [6,-3] (nf_home): hearth glow in the windows; look points eh_lantern / eh_song / eh_glass inside (interior is a scene, not kit); 1.8 m clear at the door"
        keep(pc, [-0.5, 1.8, 1.7, 3.6], 1.8, "door"); return pc

    def shard_window(cx):
        pc = Piece("shard_window"); m = Mesh()
        m.add(box(2.4, 3.0, 0.3, STONE, "stone", y0=0))
        for k, (x, w, h, col) in enumerate(((-.6, .4, 1.6, ICE), (-.1, .4, 2.2, ICE_HI), (.4, .35, 1.4, ICE), (.7, .3, 1.0, ICE_HI))):
            m.add(box(w, h, 0.06, col, "window", y0=0.5).xf((x, 0, 0.17)))
        for k in range(5):
            m.add(box(0.04, 0.3, 0.02, VIO_HI if k % 2 else CF, "glow", y0=0.4 + k * .4).xf((-0.9, 0, 0.17)))
        pc.mesh = m.ao(0, 3.2, 0.15); lamp(pc, (0, 1.6, 0.9), CF, 4.0); pc.size = [2.4, 3.0, 0.3]
        pc.markers["note"] = "Veyra's shard window (eh_glass / Spire F6 sister's glass): a pane of frozen, glowing shards"; return pc

    def spring_pool(cx):
        pc = Piece("spring_pool"); m = Mesh()
        m.add(cylinder(1.6, 1.4, 0.22, 12, STONE, "stone", y0=0)); m.add(cylinder(1.3, 1.2, 0.04, 12, POOL, "glow", y0=0.22)); m.add(cylinder(0.8, 0.7, 0.05, 12, POOL_HI, "glow", y0=0.22))
        for k in range(7):
            a = k * 2 * PI / 7
            m.add(sphere(0.24, 6, 3, mix(STONE, STONE_HI, k % 3 / 3), "stone", squash=(1.2, .7, 1)).xf((math.cos(a) * 1.5, 0.14, math.sin(a) * 1.5)))
        pc.mesh = m.ao(0, 0.5, 0.15); lamp(pc, (0, 0.6, 0), POOL, 4.5, 0.0); pc.size = [3.4, 0.4, 3.4]; pc.blockers.append([-1.4, -1.4, 1.4, 1.4])
        pc.markers["note"] = "hidden spring: bubbles + teal pool; hide behind a pillar / cairn; 2 m clear"; keep(pc, [-1.8, -1.8, 1.8, 1.8], 2.0, "spring"); return pc

    def rune_hall(cx):
        pc = Piece("rune_hall"); m = Mesh()
        m.add(box(4.6, 3.0, 3.2, STONE_LO, "stone", y0=0)); m.add(box(5.0, 0.3, 3.6, STONE_HI, "stone", y0=3.0)); m.add(box(5.0, 0.6, 3.6, SNOW, "paint", y0=3.3))
        m.add(box(2.2, 2.4, 0.3, BLK, "stone", y0=0).xf((0, 0, 1.6)))
        for k in range(9):
            m.add(box(0.07, 0.3, 0.02, RUNE, "glow", y0=1.2 + (k % 3) * .35).xf((-1.0 + k * .25, 0, 1.76)))
        m.add(box(2.0, 0.05, 0.02, CF, "glow", y0=2.55).xf((0, 0, 1.76)))
        pc.mesh = m.ao(0, 4.0, 0.15); lamp(pc, (0, 1.6, 2.4), RUNE, 5.0); pc.size = [5.0, 3.9, 3.6]; pc.blockers.append([-2.3, -1.6, 2.3, 1.6])
        pc.markers["note"] = "iceglow rune-hall [-6,-4]: the rune-reading puzzle front; door faces +z; 2 m clear"; keep(pc, [-1.5, 1.6, 1.5, 3.6], 2.0, "door"); return pc

    def glow_vine(cx):
        pc = Piece("glow_vine"); r = K.rng(cx.seed, "vine"); m = Mesh()
        m.add(box(2.0, 0.2, 0.8, STONE_LO, "stone", y0=3.1))
        for k in range(5):
            x = -0.8 + k * 0.4; ln = r.uniform(1.0, 2.2)
            m.add(beam([x, 3.1, 0.0], [x + r.uniform(-.1, .1), 3.1 - ln, 0.05], 0.035, ICE_DEEP, "paint"))
            for j in range(3):
                m.add(sphere(0.07, 6, 3, AUR_G if (k + j) % 2 else CF, "glow").xf((x + 0.05 * (j % 2), 3.1 - ln * (j + 1) / 3.2, 0.06)))
            m.add(cylinder(0.0, 0.07, 0.35, 5, CF_HI, "glow", y0=3.1 - ln - 0.3).xf((x, 0, 0.05)))
        pc.mesh = m; lamp(pc, (0, 2.2, 0.3), AUR_G, 4.5); pc.size = [2.0, 3.3, 0.9]
        pc.markers["hanging"] = "glowing icicle vines: hang at y 3.1 m from cave / hall ceilings; glow_vines fx adds the twinkle"; return pc

    # ---------------------------------------------------------------- Frozen Spire
    def spire_gate(cx):
        pc = Piece("spire_gate"); m = Mesh()
        for sx in (-1, 1):
            m.add(box(1.0, 4.6, 1.0, STONE, "stone", y0=0).xf((sx * 2.0, 0, 0))); m.add(box(1.1, 0.3, 1.1, STONE_HI, "stone", y0=4.6).xf((sx * 2.0, 0, 0)))
            m.add(cylinder(0.0, 0.3, 1.3, 6, ICE_HI, "paint", y0=4.9).xf((sx * 2.0, 0, 0)))
        m.add(box(4.0, 0.6, 1.0, STONE_HI, "stone", y0=4.2)); m.add(box(2.8, 3.8, 0.3, BLK, "stone", y0=0).xf((0, 0, -0.1)))
        for k in range(7):
            m.add(box(0.07, 0.26, 0.02, RUNE, "glow", y0=3.1).xf((-0.9 + k * .3, 0, 0.1)))
        pc.mesh = m.ao(0, 6.0, 0.15); lamp(pc, (0, 2.8, 1.0), CF, 6.0); pc.size = [5.1, 6.0, 1.1]; pc.blockers += [[-2.6, -.5, -1.4, .5], [1.4, -.5, 2.6, .5]]
        pc.markers["note"] = "F1 Spire gate (room exit / entry portal frame); 2.6 m clear"; keep(pc, [-1.4, -1.0, 1.4, 2.6], 2.6, "doorway"); return pc

    def banner_hall_banner(cx):
        pc = Piece("banner_hall_banner"); m = Mesh()
        m.add(cylinder(0.05, 0.05, 1.4, 6, IRON, "paint", y0=3.1).xf((0, 0, 0), rot=(0, 0, PI / 2)).xf((0, 0.0, 0))) if False else m.add(box(1.4, 0.07, 0.07, IRON, "paint", y0=3.4))
        m.add(box(1.1, 2.6, 0.04, RED, "paint", y0=0.8).xf((0, 0, 0.02))); m.add(box(0.9, 0.12, 0.05, RED_HI, "paint", y0=2.9).xf((0, 0, 0.03)))
        m.add(prism_x(0.04, [(-0.55, 0.8), (0.55, 0.8), (0, 0.35)], RED, "paint").xf((0, 0, 0.0), rot=(0, PI / 2, 0))) if False else m.add(box(0.5, 0.4, 0.04, RED, "paint", y0=0.45).xf((0, 0, 0.02)))
        m.add(box(0.4, 0.4, 0.03, SNOW_HI, "paint", y0=1.7).xf((0, 0, 0.06))); m.add(box(0.2, 0.2, 0.03, RED_HI, "paint", y0=1.8).xf((0, 0, 0.08)))
        pc.mesh = m.ao(0, 3.5, 0.1); pc.size = [1.4, 3.5, 0.2]
        pc.markers["hanging"] = "F2 banner hall: red banners hang from the wall at y 0.8-3.4 m, one per 2 m; Kael's house colours (they burn in his phase 3: fx)"; return pc

    def mirror_pane(cx):
        pc = Piece("mirror_pane"); m = Mesh()
        m.add(box(2.2, 3.2, 0.2, STONE_LO, "stone", y0=0)); m.add(box(1.8, 2.8, 0.06, ICE_HI, "window", y0=0.2).xf((0, 0, 0.12)))
        m.add(box(1.8, 0.05, 0.02, CF, "glow", y0=0.2).xf((0, 0, 0.16))); m.add(box(1.8, 0.05, 0.02, VIO_HI, "glow", y0=2.95).xf((0, 0, 0.16)))
        pc.mesh = m.ao(0, 3.3, 0.1); lamp(pc, (0, 1.6, 0.8), CF, 4.0); pc.size = [2.2, 3.2, 0.3]
        pc.markers["note"] = "F4 mirror stairs / F6 sister's glass: framed mirror pane, standing against the wall"; return pc

    def glacier_heart(cx):
        pc = Piece("glacier_heart"); m = Mesh()
        m.add(cylinder(2.0, 1.8, 0.4, 10, STONE_HI, "stone", y0=0))
        m.add(cylinder(1.6, 1.2, 3.6, 8, ICE_DEEP, "paint", y0=0.4)); m.add(cylinder(0.0, 1.5, 1.4, 8, ICE, "paint", y0=4.0))
        m.add(sphere(0.9, 8, 5, CF, "glow", squash=(1, 1.2, 1)).xf((0, 2.6, 0))); m.add(sphere(0.45, 7, 4, CF_HI, "glow").xf((0, 2.6, 0)))
        for k in range(6):
            a = k * PI / 3
            m.add(box(0.07, 0.4, 0.02, RUNE, "glow", y0=1.0 + (k % 2) * .8).xf((math.cos(a) * 1.55, 0, math.sin(a) * 1.55), rot=(0, -a + PI / 2, 0)))
        pc.mesh = m.ao(0, 5.6, 0.15); lamp(pc, (0, 2.6, 0), CF, 8.0); pc.size = [4.0, 5.6, 4.0]; pc.blockers.append([-1.9, -1.9, 1.9, 1.9])
        pc.markers["note"] = "F5 glacier heart (Colossus arena): centrepiece; Colossus boss_stand marker z +4.0 off it; 3 m clear ring (arena)"; pc.markers["boss_stand"] = [0, 0, 4.0]
        keep(pc, [-2.4, -2.4, 2.4, 2.4], 3.0, "arena centre"); return pc

    def archive_tablets(cx):
        pc = Piece("archive_tablets"); m = Mesh()
        for k in range(4):
            x = -1.2 + k * 0.8
            m.add(box(0.6, 1.8 + (k % 2) * .4, 0.12, STONE_HI, "stone", y0=0).xf((x, 0, 0)))
            for j in range(3):
                m.add(box(0.4, 0.04, 0.02, AUR_G if (j + k) % 2 else RUNE, "glow", y0=0.8 + j * .3).xf((x, 0, 0.07)))
        m.add(box(3.4, 0.14, 0.7, TIMBER_LO, "timber", y0=0).xf((0, 0, -0.1)))
        pc.mesh = m.ao(0, 2.4, 0.1); lamp(pc, (0, 1.2, 0.8), AUR_G, 4.5); pc.size = [3.6, 2.4, 0.9]; pc.blockers.append([-1.7, -.35, 1.7, .25])
        pc.markers["note"] = "F7 aurora archive: row of glowing record-tablets (Vigdis' archive; clue points); aurora_glow fx above"; return pc

    def crown_stair(cx):
        pc = Piece("crown_stair"); m = Mesh()
        for k in range(10):
            m.add(box(2.2, 0.15 * (k + 1), 0.45, mix(STONE, ICE_DEEP, k / 10), "stone", y0=0).xf((0, 0, -k * 0.45)))
            m.add(box(2.2, 0.03, 0.04, RUNE, "glow", y0=0.15 * (k + 1)).xf((0, 0, -k * 0.45 + 0.2)))
        for sx in (-1, 1):
            for k in range(4):
                m.add(cylinder(0.0, 0.14, 0.9 + k * .25, 5, ICE_HI, "paint", y0=0.15 * (2 * k + 1)).xf((sx * 1.3, 0, -k * 1.1)))
        pc.mesh = m.ao(0, 3.0, 0.1); lamp(pc, (0, 1.0, 0), CF, 5.0); pc.size = [3.0, 2.0, 4.5]
        pc.markers["note"] = "F10 crown stair: 10 steps up to the Crown of Ice; climbs toward -z"; pc.markers["no_props_within_m"] = 1.0; return pc

    def frozen_portal(cx):
        pc = Piece("frozen_portal"); m = Mesh()
        for k in range(14):
            a = 2 * PI * k / 14
            m.add(box(0.32, 0.5, 0.3, mix(ICE, ICE_HI, k % 3 / 3), "paint").xf((math.cos(a) * 1.5, 1.8 + math.sin(a) * 1.5, 0), rot=(0, 0, a)))
        m.add(cylinder(1.3, 1.3, 0.05, 14, CF_LO, "window", y0=0).xf((0, 1.8, 0), rot=(PI / 2, 0, 0)).xf((0, 0.0, 0.0)))
        for k in range(8):
            a = 2 * PI * k / 8
            m.add(box(0.06, 0.2, 0.02, RUNE, "glow").xf((math.cos(a) * 1.15, 1.8 + math.sin(a) * 1.15, 0.2), rot=(0, 0, a)))
        m.add(box(2.4, 0.2, 0.6, STONE_HI, "stone", y0=0))
        pc.mesh = m.ao(0, 3.6, 0.1); lamp(pc, (0, 1.8, 0.8), CF, 6.0); pc.size = [3.4, 3.6, 0.6]; pc.blockers.append([-1.2, -.3, 1.2, .3])
        pc.markers["note"] = "Crown of Ice: one of four frozen portals (N/E/S/W of the platform); portal freeze/thaw rune fx on it"; return pc

    def crown_platform(cx):
        pc = Piece("crown_platform"); m = Mesh()
        m.add(cylinder(5.0, 5.2, 0.5, 20, STONE_HI, "stone", y0=0)); m.add(cylinder(4.7, 4.7, 0.05, 20, ICE_HI, "paint", y0=0.5))
        for k in range(16):
            a = 2 * PI * k / 16
            m.add(box(0.08, 0.02, 0.5, RUNE if k % 2 else VIO_HI, "glow", y0=0.55).xf((math.cos(a) * 4.0, 0, math.sin(a) * 4.0), rot=(0, -a + PI / 2, 0)))
        m.add(cylinder(1.4, 1.4, 0.03, 16, CF_LO, "glow", y0=0.55))
        pc.mesh = m.ao(0, 0.8, 0.1); lamp(pc, (0, 0.8, 0), CF, 9.0); pc.size = [10.4, 0.55, 10.4]
        pc.markers["note"] = "frozen_rift: the Crown of Ice, round 10 m platform; Veyra boss_stand at [0,0,-3]; portals at N/E/S/W on a 6.2 m ring; aurora above"; pc.markers["boss_stand"] = [0, 0.5, -3.0]; return pc

    def spire_pillar(cx):
        pc = Piece("spire_pillar"); m = Mesh()
        m.add(cylinder(0.45, 0.4, 4.4, 8, STONE, "stone", y0=0)); m.add(cylinder(0.6, 0.5, 0.3, 8, STONE_HI, "stone", y0=0)); m.add(cylinder(0.55, 0.55, 0.25, 8, STONE_HI, "stone", y0=4.2))
        for k in range(5):
            m.add(box(0.05, 0.26, 0.02, RUNE, "glow", y0=0.6 + k * .7).xf((0, 0, 0.44)))
        m.add(cylinder(0.5, 0.0, 0.8, 7, ICE_HI, "paint", y0=0.3))
        pc.mesh = m.ao(0, 4.6, 0.1); lamp(pc, (0, 2.0, 0.7), RUNE, 3.5); pc.size = [1.2, 4.5, 1.2]; pc.blockers.append([-.5, -.5, .5, .5])
        pc.markers["note"] = "generic Spire pillar with a rune strip; rhythm along halls every 4 m"; return pc

    reuse = [("snow_floor", "snow_floor"), ("ice_lake", "ice_lake"), ("ice_floor", "ice_floor"), ("ice_wall", "ice_wall"), ("glow_ice_pool", "glow_ice_pool"),
             ("icicle_cluster", "icicle_cluster"), ("ice_crystal_cluster", "ice_crystal_cluster"), ("frost_rune_pillar", "frost_rune_pillar"),
             ("barrow_door", "spire_mouth_door"), ("rune_bridge", "rime_bridge"), ("ice_throne", "kael_perch"), ("rune_waystone", "nf_waystone"),
             ("stone_cairn", "nf_cairn"), ("glow_orb_chain", "glow_orb_chain"), ("cold_brazier", "cold_brazier"), ("warm_lantern", "warm_lantern"), ("snow_mound", "snow_mound")]
    notes = {"spire_mouth_door": "iceglow Spire mouth [0,-7.5]: 6 m ice door with three rune-locks; keep 3 m clear",
             "rime_bridge": "F8 rime bridge: step on lit runes only", "kael_perch": "F9 Kael's aerie perch (boss_stand marker); Kael 5.5x"}
    out = {}
    for s, n in reuse:
        out[n] = wrap(s, n, notes.get(n))
    for f in (frost_ledge, frost_stair, mist_arch, lantern_post, speaker_hall, fish_stall, elk_paddock, eira_grave, ashmantle_house, shard_window, spring_pool, rune_hall, glow_vine,
              spire_gate, banner_hall_banner, mirror_pane, glacier_heart, archive_tablets, crown_stair, frozen_portal, crown_platform, spire_pillar):
        out[f.__name__] = f
    return out
