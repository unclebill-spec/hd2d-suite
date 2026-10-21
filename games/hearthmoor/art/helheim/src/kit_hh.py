"""Helheim kit (PLACEHOLDER names; story/helheim.md missing 2026-10-21). Built from the Asgard kit code, recoloured: slate stone, silver-blue trim,
spirit-blue (#3fb8ff) and violet (#a45cf0) glow on the glow material only; a few pale-warm (#ffd8a0) lamps so the grade is never all blue."""
import math
import kit_jotun_base as KB
PI = math.pi
MAR, MAR_HI, MAR_SH, MAR_LO = "#8a90a8", "#b4bacc", "#5e6480", "#464a62"
GOLD, GOLD_HI, GOLD_LO = "#9ab0d0", "#d0e0f4", "#5a6a8a"
WARM = "#9fd8ff"
PALEWARM = "#ffd8a0"
CF, CF_HI = "#3fb8ff", "#e8f6ff"
VIO, VIO_HI = "#a45cf0", "#d4a8ff"
RED = "#e8321e"
DARKS, TIMBER, TIMBER_HI, WINE = "#3a3a56", "#5a4a44", "#7a6a60", "#3e3a5a"


def pieces(K):
    base = KB.pieces(K)
    box, cylinder, sphere, beam, mix, Piece, Mesh, prism_x = K.box, K.cylinder, K.sphere, K.beam, K.mix, K.Piece, K.Mesh, K.prism_x

    def lamp(pc, pos, col, rng_, fixed=0.5):
        pc.markers["lamps"].append(list(pos)); pc.markers["lamp_color"] = col; pc.markers["lamp_range"] = rng_; pc.markers["lamp_fixed"] = fixed

    def keep(pc, fp, radius, note):
        pc.markers["keep_clear"] = {"footprint_m": fp, "radius_m": radius, "note": note}

    def fin(pc, m, size, note=None, block=None, top=None):
        pc.mesh = m.ao(0, top or size[1] + .2, 0.15); pc.size = size
        if block:
            pc.blockers.append(block)
        if note:
            pc.markers["note"] = note
        return pc

    def slate_floor(cx):
        r = K.rng(cx.seed, "mf"); m = Mesh(); pc = Piece("slate_floor")
        for i in range(4):
            for j in range(4):
                x0, z0 = -1 + i * .5, -1 + j * .5
                m.quad((x0, 0, z0 + .5), (x0 + .5, 0, z0 + .5), (x0 + .5, 0, z0), (x0, 0, z0), mix(MAR, MAR_SH, r.uniform(0, .5) if (i + j) % 2 else r.uniform(.3, .8)), mat="paint")
        m.add(box(2.0, 0.006, 0.03, GOLD, "paint", y0=0).xf((0, 0, 1.0))); m.add(box(0.03, 0.006, 2.0, GOLD, "paint", y0=0).xf((1.0, 0, 0)))
        pc.mesh = m; pc.size = [2, 0.02, 2]; return pc

    def slate_wall(cx):
        pc = Piece("slate_wall"); m = Mesh()
        m.add(box(2.0, 4.0, 0.5, MAR_SH, "stone", y0=0)); m.add(box(2.1, 0.3, 0.6, GOLD, "paint", y0=4.0)); m.add(box(2.1, 0.25, 0.6, MAR_LO, "stone", y0=0))
        m.add(box(1.6, 0.05, 0.02, GOLD_HI, "paint", y0=3.2).xf((0, 0, 0.26)))
        return fin(pc, m, [2.0, 4.3, 0.6], "2 m wall module (halls, temple, Reliquary)", [-1, -.25, 1, .25])

    def mist_ledge(cx):
        pc = Piece("mist_ledge"); r = K.rng(cx.seed, "gl"); m = Mesh()
        for k in range(3):
            m.add(box(3.0, 0.4, 2.0, mix(MAR_SH, MAR, r.uniform(0, .6)), "stone", y0=k * 0.4))
        m.add(box(3.1, 0.14, 2.1, MAR_HI, "paint", y0=1.2)); m.add(box(3.1, 0.05, 0.04, GOLD, "paint", y0=1.29).xf((0, 0, 1.04)))
        for k in range(5):
            m.add(box(0.07, 0.16, 0.02, CF_HI if k % 2 else CF, "glow", y0=0.45).xf((-1.0 + k * .5, 0, 1.02)))
        pc = fin(pc, m, [3.1, 1.34, 2.1], None, [-1.5, -1.0, 1.5, 1.0]); lamp(pc, (0, 0.6, 1.3), CF, 3.0)
        pc.markers["height_m"] = 1.34; pc.markers["ledge_edge"] = [[-1.5, 1.0], [1.5, 1.0]]; pc.markers["no_props_within_m"] = 0.8; return pc

    def mist_stair(cx):
        pc = Piece("mist_stair"); m = Mesh()
        n, rise, run, wd = 7, 1.34, 0.5, 2.0
        st = rise / n; L = n * run
        for i in range(n):
            h = st * (i + 1); z1 = L / 2 - i * run; z0 = -L / 2
            m.add(box(wd, h, z1 - z0, mix(MAR_SH, MAR, 0.3 + 0.1 * (i % 2)), "stone", y0=0).xf((0, 0, (z0 + z1) / 2)))
            m.add(box(wd, 0.03, 0.06, GOLD, "paint", y0=h - 0.01).xf((0, 0, z1 - 0.04)))
        for sx in (-1, 1):
            prof = [(L / 2 + 0.05, 0), (L / 2 + 0.05, 0.5), (-L / 2, rise + 0.5), (-L / 2, 0)]
            m.add(prism_x(0.3, prof, MAR, "stone").xf((sx * (wd / 2 + 0.15), 0, 0)))
            m.add(sphere(0.1, 6, 4, WARM, "glow").xf((sx * (wd / 2 + 0.15), 0.62, L / 2 - 0.1)))
        pc = fin(pc, m, [wd + 0.6, rise + 0.5, L]); pc.kind = "stairs"; pc.stairs = {"width": wd, "rise": rise, "length": L, "steps": n}
        for sx in (-1, 1):
            lamp(pc, (sx * (wd / 2 + 0.15), 0.7, L / 2 - 0.1), WARM, 3.0)
        pc.markers["no_props_within_m"] = 1.0; pc.markers["note"] = "keep props, fx and spawns off the stair footprint (+1 m each end); top flush with mist_ledge (1.34 m)"; return pc

    def spirit_arch(cx):
        pc = Piece("spirit_arch"); m = Mesh()
        for sx in (-1, 1):
            m.add(box(0.9, 4.8, 0.9, MAR, "stone", y0=0).xf((sx * 2.0, 0, 0))); m.add(box(1.0, 0.3, 1.0, GOLD, "paint", y0=4.8).xf((sx * 2.0, 0, 0)))
        for k in range(9):
            a = PI * k / 8
            m.add(sphere(0.32, 7, 4, GOLD if k % 2 else GOLD_HI, "paint").xf((math.cos(a) * 2.0, 4.9 + math.sin(a) * 1.3, 0)))
        for k in range(7):
            a = PI * (k + .5) / 8
            m.add(box(0.06, 0.2, 0.02, WARM, "glow", y0=0).xf((math.cos(a) * 2.0, 4.8 + math.sin(a) * 1.35, 0.36)))
        pc = fin(pc, m, [4.9, 6.4, 1.0], "Gold arch to Bifrost [0,10.6]; arrival [0,9.2,'up']; nothing within 2.6 m"); lamp(pc, (0, 3.0, 1.0), WARM, 6.0)
        pc.blockers += [[-2.5, -.5, -1.5, .5], [1.5, -.5, 2.5, .5]]; keep(pc, [-2.0, -1.0, 2.0, 3.0], 2.6, "arrival"); return pc

    def spirit_pillar(cx):
        pc = Piece("spirit_pillar"); m = Mesh()
        m.add(cylinder(0.55, 0.5, 0.3, 8, MAR_LO, "stone", y0=0)); m.add(cylinder(0.4, 0.36, 4.0, 8, MAR, "stone", y0=0.3)); m.add(cylinder(0.55, 0.0, 0.8, 8, GOLD, "paint", y0=4.3))
        for k in range(6):
            m.add(box(0.06, 0.32, 0.02, CF, "glow", y0=0.7 + k * .6).xf((0, 0, 0.39)))
        m.add(sphere(0.18, 7, 4, CF_HI, "glow").xf((0, 5.2, 0)))
        pc = fin(pc, m, [1.1, 5.4, 1.1], "rune-pillars [-7,3] [0,4.5] [7,3]: rune lightning arcs between them every 4 s (fx rune_arc); 1.5 m clear", [-.5, -.5, .5, .5]); lamp(pc, (0, 4.8, 0), CF, 6.0); return pc

    def hall_of_rest(cx):
        pc = Piece("hall_of_rest"); m = Mesh()
        m.add(box(7.0, 4.6, 1.0, MAR_SH, "stone", y0=0)); m.add(box(7.4, 0.9, 1.2, GOLD, "paint", y0=4.6))
        m.add(box(2.4, 3.2, 0.2, TIMBER, "timber", y0=0).xf((0, 0, 0.55))); m.add(box(2.6, 0.2, 0.3, GOLD_HI, "paint", y0=3.2).xf((0, 0, 0.6)))
        for sx in (-1, 1):
            m.add(box(0.8, 1.2, 0.05, WARM, "window", y0=1.6).xf((sx * 2.4, 0, 0.52)))
        pc = fin(pc, m, [7.4, 5.5, 1.2], "Thunder Hall door [0,-9.6] (and the hall's own entrance wall); 2.5 m clear in front", [-3.5, -.5, 3.5, .5]); lamp(pc, (0, 2.0, 1.4), WARM, 6.0)
        keep(pc, [-1.4, .5, 1.4, 3.0], 2.5, "door"); return pc

    def lamp_stall(cx):
        pc = Piece("lamp_stall"); m = Mesh()
        for sx in (-1, 1):
            for sz in (-1, 1):
                m.add(cylinder(0.07, 0.07, 2.1, 6, TIMBER_HI, "timber", y0=0).xf((sx * 1.0, 0, sz * 0.6)))
        m.add(box(2.5, 0.2, 1.6, WINE, "paint", y0=2.1)); m.add(box(2.0, 0.8, 0.7, TIMBER, "timber", y0=0).xf((0, 0, 0.1)))
        for k in range(4):
            m.add(sphere(0.12, 6, 4, PALEWARM, "glow").xf((-0.7 + k * .45, 1.0, 0.1)))
        pc = fin(pc, m, [2.6, 2.4, 1.7], "Nessa's stall [-8,5.5] (storm-charms, mead-cakes, gold-glass lamps), counter faces +z; 1.5 m clear", [-1.2, -.7, 1.2, .8]); lamp(pc, (0, 1.6, 0.8), WARM, 4.0); return pc

    def river_rail(cx):
        pc = Piece("river_rail"); m = Mesh()
        for k in range(7):
            m.add(cylinder(0.07, 0.07, 1.2, 6, MAR, "stone", y0=0).xf((0, 0, -1.8 + k * .6)))
        m.add(box(0.08, 0.08, 3.8, GOLD, "paint", y0=1.0)); m.add(box(0.08, 0.08, 3.8, GOLD, "paint", y0=0.55))
        return fin(pc, m, [0.3, 1.3, 3.8], "Skyfield edge [10,-3] (Bodil, the sky-horses); run along z; the plains lie beyond", [-.1, -1.9, .1, 1.9])

    def memorial_ring(cx):
        pc = Piece("memorial_ring"); m = Mesh()
        for k in range(12):
            a = k * PI / 6
            m.add(box(0.5, 0.12, 0.3, GOLD if k % 2 else MAR_HI, "paint", y0=0).xf((math.cos(a) * 2.6, 0, math.sin(a) * 2.6), rot=(0, -a, 0)))
        m.add(cylinder(0.5, 0.5, 0.05, 10, CF, "glow", y0=0.01))
        pc = fin(pc, m, [5.6, 0.2, 5.6], "Moot ground [6,-6]: rune trial, spear toss; flat festival ring, keep clear"); lamp(pc, (0, 0.5, 0), CF, 3.0); return pc

    def misty_spring(cx):
        pc = Piece("misty_spring"); m = Mesh()
        m.add(cylinder(1.4, 1.3, 0.5, 12, MAR, "stone", y0=0)); m.add(cylinder(1.15, 1.15, 0.04, 12, WARM, "glow", y0=0.46)); m.add(cylinder(0.7, 0.7, 0.05, 12, GOLD_HI, "glow", y0=0.47))
        m.add(box(0.7, 2.2, 0.6, MAR_SH, "stone", y0=0).xf((0, 0, -1.6))); m.add(sphere(0.32, 7, 4, MAR, "stone").xf((0, 2.5, -1.6)))
        pc = fin(pc, m, [2.8, 2.9, 3.6], "hidden spring (gs_spring / dt_spring / rq_spring): a marble basin of bubbling gold-lit water behind a statue; 2 m clear", [-1.3, -1.9, 1.3, 1.3])
        lamp(pc, (0, 0.8, 0), WARM, 4.5, 0.0); keep(pc, [-1.8, -1.8, 1.8, 1.8], 2.0, "spring"); return pc

    def spirit_lamp(cx):
        pc = Piece("spirit_lamp"); m = Mesh()
        m.add(cylinder(0.09, 0.06, 2.6, 6, GOLD_LO, "paint", y0=0)); m.add(box(0.4, 0.2, 0.4, MAR_LO, "stone", y0=0))
        m.add(sphere(0.24, 8, 5, WARM, "glow").xf((0, 2.75, 0))); m.add(sphere(0.12, 6, 4, "#e8f6ff", "glow").xf((0, 2.78, 0)))
        pc = fin(pc, m, [0.6, 3.0, 0.6], "gold lamp post (point light r 4 m, steady); every 6-8 m; Aurelion drinks the four in G9 (fx light_drain)", [-.2, -.2, .2, .2]); lamp(pc, (0, 2.7, 0), WARM, 5.0); return pc

    def violet_lamp(cx):
        pc = Piece("violet_lamp"); m = Mesh()
        m.add(cylinder(0.09, 0.06, 2.6, 6, GOLD_LO, "paint", y0=0)); m.add(box(0.4, 0.2, 0.4, MAR_LO, "stone", y0=0))
        m.add(sphere(0.24, 8, 5, "#8a7a5a", "paint").xf((0, 2.75, 0))); m.add(sphere(0.26, 8, 3, CF_HI, "glow", squash=(1, .35, 1)).xf((0, 2.95, 0)))
        pc = fin(pc, m, [0.6, 3.0, 0.6], "the Dimming: a dark lamp with a cold-blue rime cap (the Cold Mark's tell); temple + Reliquary until the flame comes home", [-.2, -.2, .2, .2]); lamp(pc, (0, 2.9, 0), CF, 2.5); return pc

    def glow_orb_chain(cx):
        pc = Piece("glow_orb_chain"); m = Mesh()
        m.add(cylinder(0.015, 0.015, 1.4, 4, GOLD_LO, "paint", y0=1.6)); m.add(sphere(0.3, 8, 5, GOLD_HI, "glow").xf((0, 1.45, 0))); m.add(sphere(0.12, 6, 4, "#fff4d0", "glow").xf((0, 1.48, 0)))
        pc = fin(pc, m, [0.7, 3.0, 0.7]); lamp(pc, (0, 1.45, 0), WARM, 5.0, 0.0); pc.markers["hanging"] = "gold-glass globe on a chain, hang from beams at y 3 m; steady"; return pc

    def warden_seat(cx):
        pc = Piece("warden_seat"); m = Mesh()
        m.add(box(3.0, 0.4, 2.2, MAR, "stone", y0=0)); m.add(box(1.4, 0.6, 1.0, WINE, "paint", y0=0.4)); m.add(box(1.6, 2.6, 0.3, GOLD, "paint", y0=0.4).xf((0, 0, -0.5)))
        m.add(sphere(0.4, 8, 4, GOLD_HI, "paint", squash=(1, .4, .3)).xf((0, 3.0, -0.5)))
        pc = fin(pc, m, [3.0, 3.4, 2.2], "Lord-Warden's high seat [0,-6.5] (gs_hall); a spirit_pillar either side; 2 m clear in front", [-1.5, -1.1, 1.5, 1.1]); lamp(pc, (0, 2.0, 1.2), WARM, 5.0); return pc

    def long_table(cx):
        pc = Piece("long_table"); m = Mesh()
        m.add(box(4.0, 0.12, 1.0, TIMBER_HI, "timber", y0=0.8))
        for sx in (-1.7, 1.7):
            m.add(box(0.12, 0.8, 0.8, TIMBER, "timber", y0=0).xf((sx, 0, 0)))
        for sz in (-0.8, 0.8):
            m.add(box(3.6, 0.1, 0.35, TIMBER, "timber", y0=0.45).xf((0, 0, sz)))
        for k in range(3):
            m.add(cylinder(0.08, 0.06, 0.2, 6, GOLD, "paint", y0=0.92).xf((-1.2 + k * 1.2, 0, 0)))
        return fin(pc, m, [4.0, 1.0, 2.0], "hall long tables (run along x), benches both sides", [-2.0, -1.0, 2.0, 1.0])

    def rune_forge(cx):
        pc = Piece("rune_forge"); m = Mesh()
        m.add(box(0.3, 2.0, 0.3, TIMBER, "timber", y0=0).xf((-0.8, 0, 0))); m.add(box(0.3, 2.0, 0.3, TIMBER, "timber", y0=0).xf((0.8, 0, 0)))
        m.add(cylinder(0.85, 0.85, 0.1, 14, MAR_HI, "paint", y0=0).xf((0, 0, 0), rot=(PI / 2, 0, 0)).xf((0, 1.4, 0.1)))
        m.add(box(1.0, 0.5, 0.6, "#3a3a46", "stone", y0=0).xf((1.6, 0, 0.6))); m.add(box(0.12, 0.6, 0.12, TIMBER_HI, "timber", y0=0.5).xf((1.6, 0, 0.6))); m.add(box(0.4, 0.2, 0.2, "#5a5a68", "paint", y0=1.1).xf((1.6, 0, 0.6)))
        m.add(box(0.5, 0.05, 0.02, CF, "glow", y0=1.4).xf((0, 0, 0.17)))
        pc = fin(pc, m, [3.0, 2.3, 1.4], "the rune-forge [-5.5,-3] (gs_hall): a great blank shield on a stand + anvil and rune-hammer; Alrik works here; 1.5 m clear", [-1.0, -.3, 2.1, 1.0]); lamp(pc, (0, 1.5, 0.8), CF, 3.5); return pc

    def violet_window(cx):
        pc = Piece("violet_window"); m = Mesh()
        m.add(box(2.4, 4.4, 0.5, MAR, "stone", y0=0))
        for k, col in enumerate((VIO, GOLD_HI, VIO, GOLD_HI)):
            m.add(box(0.36, 2.2, 0.05, col, "window", y0=1.2).xf((-0.6 + k * .4, 0, 0.27)))
        m.add(sphere(0.4, 8, 3, VIO_HI, "window", squash=(1, 1, .1)).xf((0, 3.7, 0.27)))
        pc = fin(pc, m, [2.4, 4.4, 0.5], "violet + gold stained glass (temple walls; G3 violet glass)", [-1.2, -.25, 1.2, .25]); lamp(pc, (0, 2.2, 1.0), VIO, 4.5); return pc

    def mourning_statue(cx):
        pc = Piece("mourning_statue"); m = Mesh()
        m.add(box(1.0, 0.5, 1.0, MAR_LO, "stone", y0=0)); m.add(cylinder(0.32, 0.45, 1.8, 8, MAR, "stone", y0=0.5)); m.add(sphere(0.26, 8, 6, MAR_HI, "stone").xf((0, 2.55, 0)))
        for sx in (-1, 1):
            m.add(box(0.15, 1.6, 0.8, MAR_SH, "stone", y0=1.2).xf((sx * 0.45, 0, -0.35), rot=(0, 0, sx * 0.3)))
        m.add(box(0.5, 0.06, 0.3, GOLD, "paint", y0=1.5).xf((0, 0, 0.35)))
        return fin(pc, m, [1.4, 3.0, 1.3], "faceless angel statue (temple, G2); light wraiths drift out of them; sg_1 in a statue's hands", [-.5, -.5, .5, .5])

    def memory_altar(cx):
        pc = Piece("memory_altar"); m = Mesh()
        m.add(box(2.4, 1.0, 1.2, DARKS, "stone", y0=0)); m.add(box(2.6, 0.1, 1.4, GOLD_LO, "paint", y0=1.0)); m.add(box(0.7, 0.02, 0.4, "#2a2230", "paint", y0=1.1).xf((-0.5, 0, 0.2)))
        m.add(cylinder(0.14, 0.2, 0.4, 6, CF_HI, "glow", y0=1.1)); m.add(cylinder(0.0, 0.14, 0.4, 6, CF, "glow", y0=1.5))
        pc = fin(pc, m, [2.6, 2.0, 1.4], "dark altar [0,-5] (gs_temple): the rime-glass flame; clue points dt_brand (scorch on top), dt_scorch (under), dt_lamp (flame); 2 m clear", [-1.2, -.6, 1.2, .6]); lamp(pc, (0, 1.6, 0.4), CF, 4.0)
        keep(pc, [-1.6, -1.0, 1.6, 2.0], 2.0, "clue points"); return pc

    def vault_door(cx):
        pc = Piece("vault_door"); m = Mesh()
        for sx in (-1, 1):
            m.add(box(0.9, 5.4, 1.0, MAR_SH, "stone", y0=0).xf((sx * 2.2, 0, 0)))
        m.add(box(5.4, 0.8, 1.0, GOLD, "paint", y0=5.2)); m.add(box(3.4, 5.2, 0.3, GOLD_LO, "paint", y0=0).xf((0, 0, -0.1)))
        for k in range(3):
            x = -1.1 + k * 1.1
            m.add(sphere(0.22, 7, 4, CF, "glow", squash=(1, 1, .35)).xf((x, 2.8, 0.1))); m.add(sphere(0.1, 6, 3, CF_HI, "glow", squash=(1, 1, .5)).xf((x, 2.8, 0.15)))
        pc = fin(pc, m, [5.4, 6.0, 1.0], "Reliquary stair door [0,-8] behind the altar: gold door, three rune-locks; keep 3 m clear", [-2.7, -.5, 2.7, .5]); lamp(pc, (0, 2.8, 0.9), CF, 5.0)
        pc.markers["rune_locks"] = 3; keep(pc, [-1.7, .5, 1.7, 3.5], 3.0, "door"); return pc

    def wisp_pillar(cx):
        pc = Piece("wisp_pillar"); m = Mesh()
        m.add(cylinder(0.5, 0.45, 4.6, 8, MAR_SH, "stone", y0=0))
        for k in range(4):
            m.add(cylinder(0.52, 0.52, 0.12, 8, GOLD, "paint", y0=0.6 + k * 1.1))
        m.add(sphere(0.32, 8, 5, CF, "glow").xf((0, 4.9, 0))); m.add(sphere(0.16, 6, 4, CF_HI, "glow").xf((0, 4.9, 0)))
        pc = fin(pc, m, [1.1, 5.3, 1.1], "G4 storm gallery conductor pillar: chain lightning jumps between them in P2 (stand away); 2 m clear", [-.5, -.5, .5, .5]); lamp(pc, (0, 4.9, 0), CF, 6.0); return pc

    def echo_mirror(cx):
        pc = Piece("echo_mirror"); m = Mesh()
        m.add(box(2.0, 3.6, 0.25, GOLD_LO, "paint", y0=0)); m.add(box(1.6, 3.0, 0.05, "#5a5470", "window", y0=0.3).xf((0, 0, 0.14)))
        m.add(box(1.6, 0.04, 0.02, CF_HI, "glow", y0=3.25).xf((0, 0, 0.17)))
        pc = fin(pc, m, [2.0, 3.6, 0.3], "G6 Mirror of the Dawn (dark gold mirror, rime on the frame); Veyra's reflection appears behind yours"); lamp(pc, (0, 2.0, 0.8), CF, 3.5); return pc

    def urn_shelf(cx):
        pc = Piece("urn_shelf"); m = Mesh()
        m.add(box(3.0, 2.4, 0.6, MAR_SH, "stone", y0=0))
        for row in (0.3, 1.3):
            for k in range(4):
                m.add(sphere(0.2, 7, 5, GOLD if k % 2 else GOLD_HI, "paint", squash=(1, 1.3, 1)).xf((-1.1 + k * .73, row + 0.3, 0.35)))
        return fin(pc, m, [3.0, 2.4, 0.8], "G8 ossuary: sealed gold urns (no bones on show)", [-1.5, -.3, 1.5, .4])

    def name_stone(cx):
        pc = Piece("name_stone"); m = Mesh()
        m.add(box(1.0, 1.8, 0.2, MAR, "stone", y0=0))
        for j in range(4):
            m.add(box(0.6, 0.04, 0.02, GOLD_HI, "paint", y0=0.6 + j * .25).xf((0, 0, 0.11)))
        return fin(pc, m, [1.0, 1.8, 0.2], "G8 lore tablet (Aurelion's oath, the royal guard): clue / lore point", [-.5, -.1, .5, .1])

    def warden_throne(cx):
        pc = Piece("warden_throne"); m = Mesh()
        m.add(box(5.0, 0.5, 4.0, DARKS, "stone", y0=0)); m.add(box(2.0, 1.0, 1.4, GOLD_LO, "paint", y0=0.5).xf((0, 0, -1.0))); m.add(box(2.2, 4.0, 0.4, GOLD, "paint", y0=0.5).xf((0, 0, -1.7)))
        m.add(cylinder(0.25, 0.3, 0.6, 6, WARM, "glow", y0=4.5).xf((0, 0, -1.7)))
        pc = fin(pc, m, [5.0, 5.2, 4.0], "G9 Sunless Crypt throne: Aurelion boss_stand marker z +4.0; the true Dawn-Flame sits on top", [-2.5, -2.0, 2.5, 0.0]); lamp(pc, (0, 4.8, -1.4), WARM, 7.0)
        pc.markers["boss_stand"] = [0, 0, 4.0]; return pc

    def spirit_brazier(cx):
        pc = Piece("spirit_brazier"); m = Mesh()
        m.add(cylinder(0.3, 0.5, 1.0, 8, GOLD_LO, "paint", y0=0)); m.add(cylinder(0.55, 0.4, 0.3, 8, GOLD, "paint", y0=1.0))
        m.add(cylinder(0.3, 0.0, 0.9, 7, WARM, "glow", y0=1.3)); m.add(cylinder(0.14, 0.0, 0.6, 6, "#fff4d0", "glow", y0=1.3))
        pc = fin(pc, m, [1.1, 2.3, 1.1], "gold flame brazier (halls, Reliquary rest stops; relight target in G9)", [-.4, -.4, .4, .4]); lamp(pc, (0, 1.8, 0), WARM, 5.0); return pc

    def soul_bridge(cx):
        pc = base["rune_bridge"](cx); pc.name = "soul_bridge"; pc.markers["note"] = "G7 Rune Bridge: white planks over the gold-lit void; step only on lit runes (unlit drop); chain along z"; return pc

    def hh_waystone(cx):
        pc = base["rune_waystone"](cx); pc.name = "hh_waystone"; pc.markers["note"] = "waystone: G8 Waystone Ossuary safe room, hub; 2.6 m clear"; return pc

    NOTE = {}
    fns = [slate_floor, slate_wall, mist_ledge, mist_stair, spirit_arch, spirit_pillar, hall_of_rest, lamp_stall, river_rail, memorial_ring, misty_spring, spirit_lamp, violet_lamp,
           glow_orb_chain, warden_seat, violet_window, mourning_statue, memory_altar, vault_door, wisp_pillar, echo_mirror, urn_shelf, name_stone,
           warden_throne, spirit_brazier, soul_bridge, hh_waystone]
    return {f.__name__: f for f in fns}
