"""Niflheim scene / area layouts (also written to metadata/niflheim_layout.json with the placement notes).
World metres, +z toward the camera, hero faces -z ('up'). Props / fx stay off spawns, stairs and ledge edges (see README).
EVERY area / room set has a 1.34 m ledge + stair: frost_ledge (3.1 x 2.1 m, top 1.34) in pairs + one frost_stair (7 steps, 3.5 m run) centred on the front face
(stair centre z = ledge z + 1 + 1.75, climbs toward -z; rot pi to climb toward +z)."""
import math
PI = math.pi
CF, VIO, TEAL, WARM, AUR = "#3fb8ff", "#a45cf0", "#2fd0d0", "#ffc866", "#3fe0a0"
SNOWC = "#dfe9ff"


def grid(name, x0, x1, z0, z1, step=2.0):
    out = []
    x = x0
    while x <= x1 + 1e-6:
        z = z0
        while z <= z1 + 1e-6:
            out.append((name, (x, 0, z)))
            z += step
        x += step
    return out


def terrace(cx, zb, rows=1, rot=0.0):
    """1.34 m terrace: 2 ledges wide x `rows` deep, with ONE stair centred on the front (+z) face"""
    P = []
    for r in range(rows):
        P += [("frost_ledge", (cx - 1.55, 0, zb - 2 * r)), ("frost_ledge", (cx + 1.55, 0, zb - 2 * r))]
    P.append(("frost_stair", (cx, 0, zb + 1 + 1.75)))
    return P


def pool(x, z, k, sc=1, n="pool_cold"):
    return (n, (x, z), k, sc)


def mkscene(name, P, A, D, B, L, bg, amb, **kw):
    kw.setdefault("lscale", 0.7)
    return dict(pieces=P, actors=A, decals=D, bills=B, extra_lights=L, bg=bg, amb=amb, name=name, **kw)


# ---------------------------------------------------------------------------------- Mistmere (area `niflheim`, 24 x 22 m hub)
def niflheim():
    P = grid("snow_floor", -11, 11, -9, 11)
    P += [("ice_lake", (-2.0, 0, -0.6)), ("ice_lake", (2.0, 0, -0.6))]                                   # the frozen lake (centre ~[0,-1])
    P += [("mist_arch", (0, 0, 10.6)),                                                                    # Bifrost arch, arrival [0, 9.2]
          ("speaker_hall", (0, 0, -10.4))]
    P += terrace(0.0, -7.2) + [("cold_brazier", (-2.8, 1.34, -7.4)), ("cold_brazier", (2.8, 1.34, -7.4))]  # the frost-speaker's terrace + stair on the front face
    P += [("lantern_post", (-7.0, 0, 4.0)), ("lantern_post", (0.0, 0, 5.0)), ("lantern_post", (7.0, 0, 4.0)),
          ("fish_stall", (-8.5, 0, -3.0)), ("elk_paddock", (9.0, 0, -3.0)),
          ("spring_pool", (-11.0, 0, -1.0)), ("frost_rune_pillar", (-10.0, 0, -3.2)), ("ice_crystal_cluster", (-11.2, 0, -4.2)),
          ("nf_waystone", (10.0, 0, -8.6)), ("nf_cairn", (10.0, 0, -6.6)),                                  # Quiet Shore path [10,-9]
          ("frost_rune_pillar", (-10.4, 0, -8.2)), ("frost_rune_pillar", (-8.6, 0, -9.8)), ("glow_ice_pool", (-10.0, 0, -9.0)),   # cave stair [-10,-9]
          ("snow_mound", (-5.4, 0, 8.0)), ("snow_mound", (6.0, 0, -7.4)),
          ("warm_lantern", (-4.2, 0, 7.4)), ("warm_lantern", (4.2, 0, 7.6)), ("warm_lantern", (-6.0, 0, -5.0)), ("warm_lantern", (6.4, 0, 1.8)),
          ("glow_orb_chain", (-4.0, 0.2, 2.6)), ("glow_orb_chain", (4.0, 0.2, 2.8)), ("glow_orb_chain", (-3.0, 0.2, -5.0)), ("glow_orb_chain", (3.0, 0.2, -4.6))]
    A = [("nf_folk", "frostspeaker", "down", "idle", 0, (0.0, 1.34, -6.2)),
         ("nf_folk", "gatewright", "down", "idle", 1, (2.6, 0, 8.2)),
         ("nf_folk", "nf_trader", "down", "idle", 2, (-8.5, 0, -1.4)),
         ("nf_folk", "elkman", "left", "idle", 1, (7.0, 0, -2.8)),
         ("nf_folk", "brisa", "right", "walk", 1, (-4.6, 0, 1.6)),
         ("HERO", "wildcaller", "up", "idle", 0, (0.0, 0, 8.4)), ("nf_hrefna", "hrefna", "up", "idle", 1, (1.2, 0, 8.6))]
    D = [pool(-7, 4, 0), pool(0, 5, 3), pool(7, 4, 5), pool(-2.8, -7.4, 1), pool(2.8, -7.4, 4), pool(-2.0, -0.6, 2, 2, "pool_teal"), pool(2.0, -0.6, 5, 2, "pool_teal"),
         pool(-11.0, -1.0, 3, 2, "pool_teal"), pool(-10.0, -9.0, 0, 1, "pool_teal"), pool(10.0, -8.6, 2, 1), pool(-8.5, -3.0, 4, 1, "pool_warm"), pool(-4.2, 7.4, 1, 1, "pool_warm"),
         pool(4.2, 7.6, 5, 1, "pool_warm"), pool(-6.0, -5.0, 3, 1, "pool_warm"), pool(6.4, 1.8, 0, 1, "pool_warm"), pool(0, -10.0, 2, 1, "pool_warm"), pool(0, 10.0, 1, 2, "pool_cold"),
         pool(-4.0, 2.6, 2, 1, "pool_aurora"), pool(4.0, 2.8, 5, 1, "pool_aurora"), pool(-10.0, -3.2, 1, 1, "pool_violet"),
         ("mist_drift", (-6.0, 6.0), 0, 2), ("mist_drift", (5.0, -5.2), 3, 2), ("mist_drift", (-2.0, 2.4), 5, 2), ("glow_fog", (8.0, 6.0), 2, 2), ("rune_pulse", (-10.0, -3.2), 0, 1)]
    B = [("cold_flame", (-2.8, 1.34 + 1.9, -7.4), 0), ("cold_flame", (2.8, 1.34 + 1.9, -7.4), 4), ("lantern_float", (-7.0, 2.5, 4.0), 2), ("lantern_float", (7.0, 2.5, 4.0), 6),
         ("neon_fireflies_blue", (-5.0, 0.6, 1.0), 1), ("neon_fireflies_violet", (-10.0, 0.6, -3.0), 4), ("neon_fireflies_green", (5.0, 0.6, -5.0), 6),
         ("glow_orb_blue", (-3.0, 2.2, 6.0), 0), ("glow_orb_violet", (-9.0, 1.9, -5.0), 3), ("glow_orb_green", (6.0, 1.9, 6.0), 5),
         ("spring_bubbles", (-11.0, 0.3, -1.0), 2), ("ice_sparkles", (-2.0, 0.2, -0.6), 0), ("ice_sparkles", (2.0, 0.2, -0.6), 4), ("aurora_glow", (0.0, 6.0, -11.0), 2)]
    L = [((-7, 2.5, 4.0), CF, 7.0, 0.8), ((0, 2.5, 5.0), CF, 7.0, 0.8), ((7, 2.5, 4.0), CF, 7.0, 0.8), ((-2.0, 0.8, -0.6), TEAL, 7.0, 0.7), ((2.0, 0.8, -0.6), TEAL, 7.0, 0.7),
         ((-8.5, 2.0, -2.0), WARM, 6.0, 0.9), ((0, 2.4, -8.0), WARM, 7.0, 0.8), ((-11, 1.0, -1.0), TEAL, 6.0, 0.6), ((-10, 1.2, -3.2), VIO, 5.0, 0.6), ((10, 1.8, -8.0), CF, 6.0, 0.6),
         ((0, 5.0, 6.0), "#cfe0ff", 14.0, 0.55), ((0, 5.0, -3.0), "#c8d8ff", 14.0, 0.5)]
    return mkscene("niflheim", P, A, D, B, L, {"night": (15, 18, 30), "day": (150, 166, 192)}, {"night": (0.15, 0.15, 0.21), "day": (0.66, 0.65, 0.70)})


# ---------------------------------------------------------------------------------- The Quiet Shore (area `nf_home`, 16 x 16 m)
def nf_home():
    P = grid("snow_floor", -7, 7, -7, 7)
    P += [("ice_lake", (-2, 0, 5.4)), ("ice_lake", (2, 0, 5.4))]                                          # the shore water (south)
    P += [("eira_grave", (0, 0, -4.0)), ("ashmantle_house", (6.0, 0, -3.0))]
    P += terrace(-4.6, -5.2) + [("lantern_post", (-6.4, 1.34, -5.6))]                                       # 1.34 m shore terrace (stair on the front face)
    P += [("shard_window", (-7.6, 0, -0.5), PI / 2), ("lantern_post", (3.0, 0, 1.2)), ("lantern_post", (-3.0, 0, 1.4)),
          ("nf_cairn", (-5.0, 0, 3.4)), ("snow_mound", (3.4, 0, 4.4)), ("snow_mound", (-6.0, 0, 6.0)),
          ("warm_lantern", (3.2, 0, -0.2)), ("warm_lantern", (-1.6, 0, 3.0)), ("glow_orb_chain", (1.0, 0.2, -1.4)), ("glow_orb_chain", (-2.4, 0.2, -2.2))]
    A = [("nf_folk", "eira", "down", "idle", 0, (0.0, 0, -2.6)), ("nf_folk", "veyra", "right", "idle", 2, (-2.4, 0, -1.4)),
         ("HERO", "wildcaller", "up", "idle", 0, (1.0, 0, 3.8)), ("nf_hrefna", "hrefna", "up", "idle", 2, (2.2, 0, 4.0))]
    D = [pool(-1.0, -4.0, 0, 1, "pool_violet"), pool(1.0, -4.0, 3, 1, "pool_violet"), pool(6.0, -0.6, 2, 2, "pool_warm"), pool(3.2, -0.2, 4, 1, "pool_warm"), pool(3.0, 1.2, 1, 1),
         pool(-3.0, 1.4, 5, 1), pool(-2, 5.4, 0, 2, "pool_teal"), pool(2, 5.4, 3, 2, "pool_teal"), pool(-6.4, -5.6, 2, 1), pool(-7.0, -0.5, 1, 1, "pool_violet"),
         ("mist_drift", (0, 1.0), 1, 2), ("mist_violet", (0.0, -2.8), 4, 2), ("mist_drift", (-5.0, 5.0), 6, 2)]
    B = [("eira_outline", (0.0, 0.0, -2.6), 3), ("violet_flame", (-0.8, 1.2, -3.6), 1), ("violet_flame", (0.8, 1.2, -3.6), 5), ("lantern_float", (-3.0, 2.5, 1.4), 2),
         ("neon_fireflies_violet", (-1.0, 0.6, -3.0), 2), ("neon_fireflies_blue", (3.0, 0.6, 3.0), 5), ("glow_orb_violet", (-4.0, 1.9, -2.0), 0), ("glow_orb_blue", (4.0, 2.2, 4.0), 4),
         ("ice_sparkles", (0, 0.2, 5.4), 3), ("aurora_glow", (0.0, 6.0, -8.0), 6)]
    L = [((-0.8, 1.2, -3.6), VIO, 6.0, 0.8), ((0.8, 1.2, -3.6), VIO, 6.0, 0.8), ((6.0, 1.6, -0.6), WARM, 7.0, 1.0), ((3.2, 2.0, -0.2), WARM, 5.0, 0.8), ((3.0, 2.5, 1.2), CF, 6.0, 0.7),
         ((-3.0, 2.5, 1.4), CF, 6.0, 0.7), ((0, 0.8, 5.4), TEAL, 7.0, 0.7), ((0, 5.0, 2.0), "#cfe0ff", 12.0, 0.5), ((-7.0, 2.0, -0.5), VIO, 5.0, 0.6)]
    return mkscene("nf_home", P, A, D, B, L, {"night": (15, 18, 30), "day": (150, 166, 192)}, {"night": (0.15, 0.15, 0.21), "day": (0.66, 0.65, 0.70)})


# ---------------------------------------------------------------------------------- The Glowpool Caverns (area `iceglow`, 20 x 16 m)
def iceglow():
    P = grid("ice_floor", -9, 9, -7, 7)
    P += [("ice_wall", (x, 0, -7.9)) for x in (-8, -6, -4, 4, 6, 8)] + [("ice_wall", (-9.9, 0, z), PI / 2) for z in (-6, -4, -2, 0, 2, 4, 6)]
    P += [("spire_mouth_door", (0, 0, -7.5)), ("rune_hall", (-6.0, 0, -4.0))]
    P += terrace(3.6, -4.2) + [("cold_brazier", (5.6, 1.34, -4.6))]                                         # 1.34 m ledge east of the Spire mouth + stair
    pools = [(-3.0, 3.0), (3.0, 4.2), (-7.0, 3.6), (6.6, -0.6), (-1.0, -1.2)]                                # the five bioluminescent pools
    P += [("glow_ice_pool", (x, 0, z)) for (x, z) in pools]
    P += [("frost_rune_pillar", (-8.4, 0, -0.6)), ("frost_rune_pillar", (8.4, 0, 2.6)), ("frost_rune_pillar", (-3.8, 0, -3.6)), ("ice_crystal_cluster", (8.6, 0, -4.6)),
          ("spring_pool", (-8.6, 0, 6.0)), ("icicle_cluster", (-2.0, 3.2 - 3.2, -6.6)), ("glow_vine", (-4.0, 0, -2.0)), ("glow_vine", (3.0, 0, 1.0)), ("glow_vine", (-7.0, 0, 1.0)),
          ("glow_orb_chain", (-5.0, 0.2, 1.0)), ("glow_orb_chain", (0.6, 0.2, 2.0)), ("glow_orb_chain", (5.0, 0.2, 1.6)), ("warm_lantern", (-4.4, 0, 6.0)), ("warm_lantern", (4.4, 0, 6.2)),
          ("warm_lantern", (1.8, 0, -4.8)), ("nf_cairn", (7.4, 0, 6.0))]
    A = [("nf_folk", "frostspeaker", "right", "idle", 1, (-3.8, 0, -3.2)), ("nf_enemies", "mist_stalker", "left", "idle", 2, (6.8, 0, 4.2)), ("nf_enemies", "frost_spirit", "down", "idle", 0, (-1.6, 0, 3.8)),
         ("nf_elites", "mistalpha", "left", "idle", 1, (7.2, 0, 2.0)), ("HERO", "wildcaller", "up", "idle", 0, (0.0, 0, 6.0)), ("nf_hrefna", "hrefna", "up", "idle", 0, (1.2, 0, 6.2))]
    D = [pool(x, z, i, 2, "pool_teal" if i % 2 == 0 else "pool_cold") for i, (x, z) in enumerate(pools)]
    D += [pool(0, -6.2, 2, 2, "pool_cold"), pool(-6.0, -2.0, 1, 1, "pool_cold"), pool(5.6, -4.6, 4, 1), pool(-8.6, 6.0, 0, 2, "pool_teal"), pool(-4.4, 6.0, 3, 1, "pool_warm"),
          pool(4.4, 6.2, 5, 1, "pool_warm"), pool(1.8, -4.8, 2, 1, "pool_warm"), pool(-8.4, -0.6, 4, 1, "pool_violet"), pool(8.4, 2.6, 1, 1, "pool_aurora"),
          ("glow_fog", (-2.0, 1.0), 0, 2), ("glow_fog", (5.0, 2.0), 4, 2), ("rune_pulse", (0, -5.6), 1, 2), ("rune_pulse", (-3.8, -3.6), 3, 1)]
    B = [("glow_vines", (-4.0, 3.1, -2.0), 0), ("glow_vines", (3.0, 3.1, 1.0), 3), ("glow_vines", (-7.0, 3.1, 1.0), 5), ("glow_crystals_blue", (-5.0, 3.2, -6.6), 2), ("glow_crystals_violet", (5.0, 3.2, -6.6), 5),
         ("neon_fireflies_green", (-2.0, 0.6, 1.0), 1), ("neon_fireflies_blue", (4.0, 0.6, 2.0), 4), ("neon_fireflies_violet", (-8.0, 0.6, 2.0), 6),
         ("glow_orb_blue", (-1.0, 2.0, 2.0), 0), ("glow_orb_green", (2.4, 2.2, 5.0), 3), ("glow_orb_violet", (-6.6, 1.9, 4.6), 5), ("spring_bubbles", (-8.6, 0.3, 6.0), 2),
         ("cold_flame", (5.6, 1.34 + 1.9, -4.6), 3), ("ice_sparkles", (6.6, 0.2, -0.6), 5)]
    L = [(( x, 0.8, z), (TEAL if i % 2 == 0 else CF), 7.0, 0.8) for i, (x, z) in enumerate(pools)] + [((0, 3.2, -6.4), CF, 8.0, 0.8), ((-6.0, 1.6, -2.2), CF, 6.0, 0.7), ((-4.4, 2.0, 6.0), WARM, 6.0, 0.9),
         ((4.4, 2.0, 6.2), WARM, 6.0, 0.9), ((1.8, 2.0, -4.8), WARM, 5.0, 0.8), ((0, 5.0, 3.0), "#bcd2ff", 14.0, 0.5)]
    return mkscene("iceglow", P, A, D, B, L, {"night": (15, 18, 30)}, {"night": (0.15, 0.15, 0.21)}, lscale=0.5)


# ---------------------------------------------------------------------------------- The Frozen Spire (10 rooms F1..F10) + the Crown of Ice
def spire_room(name, extra_P, A, D, B, L, ledge_x=-4.4, ledge_z=-3.6, size=6, extra_light=None, bg=(15, 18, 30), void=None, **kw):
    P = [p for p in grid("ice_floor", -size, size, -size, size) if not (void and void[0] <= p[1][0] <= void[1] and void[2] <= p[1][2] <= void[3])]
    P += [("ice_wall", (x, 0, -size - 0.9)) for x in range(-size, size + 1, 2)] + [("ice_wall", (-size - 0.9, 0, z), PI / 2) for z in range(-size + 2, size, 2)]
    P += terrace(ledge_x, ledge_z) + [("spire_pillar", (ledge_x + 3.2, 1.34, ledge_z - 0.6))]
    P += [("spire_pillar", (4.4, 0, -4.6)), ("spire_pillar", (-4.4, 0, 4.4)), ("warm_lantern", (4.6, 0, 4.4)), ("warm_lantern", (-1.2, 0, 5.2)), ("cold_brazier", (5.0, 0, -1.6))]
    P += extra_P
    A = A + [("HERO", "wildcaller", "up", "idle", 0, (0.0, 0, 5.0)), ("nf_hrefna", "hrefna", "up", "idle", 3, (1.2, 0, 5.2))]
    D = D + [pool(4.6, 4.4, 1, 1, "pool_warm"), pool(-1.2, 5.2, 4, 1, "pool_warm"), pool(5.0, -1.6, 2, 1), pool(ledge_x + 3.2, ledge_z - 0.6, 0, 1, "pool_cold"), pool(4.4, -4.6, 3, 1),
             ("rune_pulse", (-4.4, 4.4), 0, 1), ("mist_drift", (-2.0, 1.0), 2, 2)]
    B = B + [("cold_flame", (5.0, 1.9, -1.6), 2), ("ice_sparkles", (0, 0.2, 0.0), 3), ("neon_fireflies_blue", (-2.0, 0.6, 1.0), 4), ("glow_orb_blue", (-3.0, 2.2, 2.0), 1)]
    L = L + [((4.6, 2.0, 4.4), WARM, 6.0, 0.9), ((-1.2, 2.0, 5.2), WARM, 5.0, 0.8), ((5.0, 2.0, -1.6), CF, 6.0, 0.7), ((0, 5.0, 2.0), "#bcd2ff", 14.0, 0.55), ((0, 3.0, -2.0), CF, 9.0, 0.6)]
    return mkscene(name, P, A, D, B, L, {"night": bg}, {"night": (0.15, 0.15, 0.21)}, **kw)


def spire_f1():
    return spire_room("spire_f1", [("spire_gate", (0, 0, -5.6)), ("cold_brazier", (-2.6, 0, -3.2)), ("cold_brazier", (2.6, 0, -3.2))],
                      [("nf_enemies", "mist_stalker", "down", "idle", 0, (-1.6, 0, 0.6)), ("nf_enemies", "mist_stalker", "left", "idle", 2, (2.2, 0, 1.4))],
                      [pool(-2.6, -3.2, 1), pool(2.6, -3.2, 4), pool(0, -5.0, 2, 2), ("mist_drift", (0, 0.5), 5, 2)], [("cold_flame", (-2.6, 1.9, -3.2), 0), ("cold_flame", (2.6, 1.9, -3.2), 4)],
                      [((0, 2.8, -4.6), CF, 7.0, 0.8)])


def spire_f2():
    ban = [("banner_hall_banner", (-5.0, 0, z), PI / 2) for z in (-4, -1, 2)] + [("banner_hall_banner", (5.5, 0, z), -PI / 2) for z in (-4, -1, 2)]
    return spire_room("spire_f2", ban + [("spire_pillar", (-2.4, 0, -2.4)), ("spire_pillar", (2.4, 0, -2.4))],
                      [("nf_enemies", "ice_warden", "down", "idle", 0, (-1.8, 0, 0.0)), ("nf_enemies", "ice_warden", "left", "walk", 1, (2.4, 0, -0.6)),
                       ("nf_elites", "brisa_mini", "down", "idle", 1, (0.0, 1.34, -4.4)), ("nf_enemies", "frost_wraith", "down", "idle", 2, (-4.2, 0, 1.6))],
                      [pool(-2.4, -2.4, 1), pool(2.4, -2.4, 4)], [("banner_burn", (-5.0, 0.0, -1.0), 2)], [((0, 2.0, -3.0), "#c03a30", 6.0, 0.5)], ledge_x=4.4, ledge_z=-4.4)


def spire_f3():
    return spire_room("spire_f3", [("glow_ice_pool", (-2.8, 0, -1.0)), ("glow_ice_pool", (2.4, 0, 1.4)), ("glow_ice_pool", (-1.2, 0, -4.4)), ("spring_pool", (4.6, 0, -4.4)), ("glow_vine", (0, 0, -2.4)), ("ice_crystal_cluster", (-5.2, 0, -1.0))],
                      [("nf_enemies", "frost_spirit", "down", "idle", 1, (-0.6, 0, 1.0))],
                      [pool(-2.8, -1.0, 0, 2, "pool_teal"), pool(2.4, 1.4, 3, 2, "pool_cold"), pool(-1.2, -4.4, 5, 2, "pool_aurora"), pool(4.6, -4.4, 2, 2, "pool_teal"), ("glow_fog", (0, -1.0), 3, 2)],
                      [("glow_vines", (0, 3.1, -2.4), 2), ("spring_bubbles", (4.6, 0.3, -4.4), 4), ("glow_orb_green", (-1.0, 2.0, 0.0), 3)],
                      [((-2.8, 0.8, -1.0), TEAL, 7.0, 0.8), ((2.4, 0.8, 1.4), CF, 7.0, 0.8), ((-1.2, 0.8, -4.4), AUR, 7.0, 0.8), ((4.6, 0.8, -4.4), TEAL, 6.0, 0.7)], lscale=0.25)


def spire_f4():
    return spire_room("spire_f4", [("mirror_pane", (x, 0, -6.6)) for x in (-4, -1.6, 1.6, 4)] + [("mirror_pane", (-6.6, 0, -1.0), PI / 2)],
                      [("boss_veyra", "veyra_clone", "down", "idle", 1, (-3.0, 0, -2.4), "sprite")],
                      [pool(-1.6, -6.0, 0, 1, "pool_violet"), pool(1.6, -6.0, 3, 1, "pool_cold"), ("mist_violet", (-3.0, -2.4), 2, 2)], [("mist_clone_puff", (-3.0, 0.0, -1.4), 2), ("glow_orb_violet", (3.0, 2.0, -2.0), 1)],
                      [((-1.6, 1.6, -5.8), VIO, 6.0, 0.7), ((1.6, 1.6, -5.8), CF, 6.0, 0.7)], reach=11.0, reach_z=-2.4, lscale=0.45)


def spire_f5():
    return spire_room("spire_f5", [("glacier_heart", (0, 0, -2.6)), ("ice_crystal_cluster", (-5.0, 0, -4.4)), ("ice_crystal_cluster", (5.2, 0, -3.4))],
                      [("boss_colossus", "colossus", "down", "idle", 1, (0.0, 0, 1.4), "sprite")],
                      [pool(0, -2.6, 1, 3, "pool_cold"), ("frost_nova", (0, 1.4), 5, 2)], [("core_pulse", (0, 3.4, 1.6), 2), ("ice_block", (-4.0, 1.4, 0.6), 1)], [((0, 2.6, -2.6), CF, 9.0, 0.9)],
                      size=7, reach=18.5, reach_z=1.4, bg=(15, 18, 30))


def spire_f6():
    return spire_room("spire_f6", [("shard_window", (x, 0, -6.6)) for x in (-4.2, 0, 4.2)] + [("mirror_pane", (-6.6, 0, -2.6), PI / 2)],
                      [("nf_folk", "veyra", "up", "idle", 1, (0.0, 0, -4.0)), ("nf_folk", "eira", "down", "idle", 2, (-2.6, 0, -2.0))],
                      [pool(0, -6.0, 0, 2, "pool_violet"), pool(-4.2, -6.0, 3, 1), pool(4.2, -6.0, 5, 1), ("mist_violet", (-2.6, -2.0), 1, 2)],
                      [("eira_outline", (-2.6, 0.0, -2.0), 4), ("glow_crystals_violet", (-4.2, 3.2, -6.0), 2), ("violet_flame", (2.6, 1.2, -4.0), 3)], [((0, 1.6, -5.8), VIO, 8.0, 0.8)])


def spire_f7():
    return spire_room("spire_f7", [("archive_tablets", (-2.6, 0, -5.0)), ("archive_tablets", (2.6, 0, -5.0)), ("nf_waystone", (4.8, 0, 0.2)), ("ice_crystal_cluster", (-5.2, 0, -1.0))],
                      [("nf_folk", "archivist", "down", "idle", 0, (-1.0, 0, -3.2))],
                      [pool(-2.6, -5.0, 1, 2, "pool_aurora"), pool(2.6, -5.0, 4, 2, "pool_aurora"), pool(4.8, 0.2, 2, 2, "pool_violet"), ("rune_pulse", (4.8, 0.2), 2, 2)],
                      [("aurora_glow", (-3.0, 6.0, -4.0), 1), ("aurora_glow", (3.0, 6.0, -4.0), 5), ("glow_crystals_blue", (0, 3.2, -3.0), 2), ("neon_fireflies_green", (0, 0.6, -2.0), 2)],
                      [((-2.6, 1.2, -4.4), AUR, 7.0, 0.8), ((2.6, 1.2, -4.4), AUR, 7.0, 0.8), ((4.8, 1.0, 0.2), VIO, 6.0, 0.7), ((0, 5.0, -3.0), "#9fe8d0", 12.0, 0.5)], ledge_x=-4.4, ledge_z=0.0, lscale=0.25)


def spire_f8():
    return spire_room("spire_f8", [("rime_bridge", (0, 0.0, z)) for z in (-4.0, -2.0, 0.0, 2.0)] + [("frozen_portal", (-6.6, 0, -2.0), PI / 2), ("frozen_portal", (6.6, 0, -2.0), -PI / 2)],
                      [], [pool(0, -3.0, 0, 2), ("portal_freeze", (-6.4, 1.8), 3, 1)] if False else [pool(0, -3.0, 0, 2), pool(-6.0, -2.0, 3, 1), pool(6.0, -2.0, 5, 1)],
                      [("portal_freeze", (-6.4, 1.8, -2.0), 4), ("portal_thaw", (6.4, 1.8, -2.0), 2), ("glow_orb_blue", (0, 1.8, -2.0), 3)], [((0, 1.0, -2.0), CF, 8.0, 0.8), ((-6.0, 1.8, -2.0), CF, 6.0, 0.7)],
                      void=(-2.0, 2.0, -6.0, 2.0), ledge_x=-4.6, ledge_z=3.0, lscale=0.6)


def spire_f9():
    return spire_room("spire_f9", [("kael_perch", (0, 0, -3.6)), ("banner_hall_banner", (-5.0, 0, -2.0), PI / 2), ("banner_hall_banner", (5.5, 0, -2.0), -PI / 2),
                                   ("banner_hall_banner", (-5.0, 0, 1.0), PI / 2), ("banner_hall_banner", (5.5, 0, 1.0), -PI / 2)],
                      [("boss_kael", "kael", "down", "idle", 1, (0.0, 0, 0.6), "sprite")],
                      [pool(0, -3.6, 1, 2, "pool_cold"), ("kael_bite", (2.4, 2.4), 3, 2)], [("banner_burn", (-5.0, 0.0, -1.0), 2), ("bat_split", (3.0, 1.0, -1.0), 3)], [((0, 3.0, -3.6), CF, 9.0, 0.8), ((0, 2.0, 0.0), "#c03a30", 7.0, 0.5)],
                      size=7, reach=16.0, reach_z=0.6)


def spire_f10():
    return spire_room("spire_f10", [("crown_stair", (0, 0, -3.2)), ("frozen_portal", (0, 0, -6.6))], [],
                      [pool(0, -3.2, 2, 2), ("rune_pulse", (0, 0.5), 1, 2)], [("aurora_glow", (0, 6.0, -5.0), 2), ("neon_fireflies_violet", (0, 0.6, -1.0), 3)], [((0, 3.0, -4.0), CF, 9.0, 0.8), ((0, 2.0, -6.0), VIO, 7.0, 0.7)],
                      ledge_x=-4.4, ledge_z=-1.0, lscale=0.3)


def frozen_rift():
    P = [("crown_platform", (0, 0, 0))]
    P += [("frozen_portal", (6.2 * math.sin(a), 0, -6.2 * math.cos(a)), a if a else 0.0) for a in (0.0, PI / 2, PI, 3 * PI / 2)]
    P += terrace(0.0, 9.0, rows=1) + [("cold_brazier", (-2.6, 1.34, 8.6)), ("cold_brazier", (2.6, 1.34, 8.6)), ("snow_floor", (0, 0, 13.0)), ("snow_floor", (2, 0, 13.0)), ("snow_floor", (-2, 0, 13.0))]
    P += [("snow_floor", (x, 0, z)) for x in (-2, 0, 2) for z in (9.0, 11.0)]
    A = [("boss_veyra", "veyra_p1", "down", "idle", 1, (0.0, 0.5, -2.4), "sprite"), ("nf_hrefna", "hrefna", "up", "idle", 1, (1.2, 1.34, 8.2)), ("HERO", "wildcaller", "up", "idle", 0, (0.0, 1.34, 8.6))]
    D = [pool(0, 0, 1, 3, "pool_cold"), pool(0, -3.0, 4, 2, "pool_violet"), ("beam_ring", (-2.4, 1.6), 3, 2), pool(-2.6, 8.6, 2, 1), pool(2.6, 8.6, 5, 1), pool(0, -6.2, 0, 2, "pool_cold"), pool(6.2, 0, 3, 2, "pool_cold"),
         pool(-6.2, 0, 1, 2, "pool_cold"), pool(0, 6.2, 5, 2, "pool_cold"), ("veyra_shadow", (0, -2.4), 0, 2), ("rune_pulse", (0, 0), 1, 3)]
    B = [("aurora_glow", (-4.0, 7.0, -7.0), 1), ("aurora_glow", (4.0, 7.0, -7.0), 5), ("portal_freeze", (0.0, 1.8, -6.2), 5), ("portal_freeze", (6.2, 1.8, 0.0), 3), ("portal_thaw", (-6.2, 1.8, 0.0), 2),
         ("breath_fog", (0.6, 3.6, -2.4), 3), ("neon_fireflies_violet", (-2.0, 0.8, -1.0), 2), ("neon_fireflies_blue", (2.0, 0.8, 2.0), 5), ("glow_orb_violet", (-4.0, 2.4, 1.0), 4), ("glow_orb_blue", (4.0, 2.4, 1.0), 1),
         ("cold_flame", (-2.6, 1.34 + 1.9, 8.6), 0), ("cold_flame", (2.6, 1.34 + 1.9, 8.6), 4), ("lantern_float", (-1.4, 2.4, 6.0), 3)]
    L = [((0, 1.0, 0), CF, 10.0, 1.0), ((0, 2.6, -3.0), VIO, 9.0, 0.9), ((0, 2.0, -6.2), CF, 7.0, 0.8), ((6.2, 2.0, 0), CF, 7.0, 0.8), ((-6.2, 2.0, 0), VIO, 7.0, 0.8), ((0, 2.0, 6.2), CF, 7.0, 0.8),
         ((-2.6, 3.0, 8.6), WARM, 6.0, 0.9), ((2.6, 3.0, 8.6), WARM, 6.0, 0.9), ((0, 6.0, 0.0), "#bcd2ff", 18.0, 0.55)]
    return mkscene("frozen_rift", P, A, D, B, L, {"night": (15, 18, 30)}, {"night": (0.15, 0.15, 0.21)}, reach=15.5, reach_z=-2.4, lscale=1.0)
