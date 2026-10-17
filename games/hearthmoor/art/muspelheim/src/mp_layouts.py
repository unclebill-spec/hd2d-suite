"""Muspelheim scene / area layouts (also written to metadata/muspelheim_layout.json with the placement notes).
World metres, +z toward the camera, hero faces -z ('up'). Props / fx stay off spawns, stairs and ledge edges (see README)."""
import math
PI = math.pi
LAVA, CF, VIO, TEAL, WARM = "#ff7a1a", "#3fb8ff", "#a45cf0", "#2fd0d0", "#ffb066"


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


# ------------------------------------------------------------------------------------ Cinderhold (area `muspelheim`, 24 x 22 m hub)
def cinderhold():
    P = grid("basalt_floor", -11, 11, -9, 11)
    # the lava river across the hub at z = 3 with the Warden's Walk stepping-stones in the middle ([0, 3.0])
    P += [("lava_channel", (-8, 0, 3.0), PI / 2), ("lava_channel", (-4, 0, 3.0), PI / 2), ("warden_stones", (0, 0, 3.0)),
          ("lava_channel", (4, 0, 3.0), PI / 2), ("lava_channel", (8, 0, 3.0), PI / 2)]
    P += [("red_arch", (0, 0, 10.6)),                                                                   # Bifrost arch, arrival [0, 9.2]
          ("forge_hall", (-7.2, 0, -6.2)), ("basalt_house", (6.6, 0, -7.4)),
          # the Warden's terrace: 1.34 m (2 x 2 basalt_ledge deep), one stair centred on the front face z = -5.2
          ("basalt_ledge", (-1.55, 0, -6.2)), ("basalt_ledge", (1.55, 0, -6.2)), ("basalt_ledge", (-1.55, 0, -8.2)), ("basalt_ledge", (1.55, 0, -8.2)),
          ("basalt_stair", (0, 0, -3.7)),
          ("forge_wall", (-4.0, 1.34 * 0, -9.9)), ("forge_wall", (-2.0, 0, -9.9)), ("forge_wall", (2.0, 0, -9.9)), ("forge_wall", (4.0, 0, -9.9)),   # Sigil Forge door [0,-9.6]
          ("shrine_lamp", (-1.3, 1.34, -9.2)), ("shrine_lamp", (1.3, 1.34, -9.2)),
          ("spice_stall", (-7.0, 0, 5.6)), ("lizard_stable", (-9.0, 0, -2.4)),
          ("dance_ring", (8.0, 0, -2.0)), ("emberfall_anvil", (6.2, 0, -3.4)), ("emberfall_anvil", (9.8, 0, -3.4)), ("emberfall_anvil", (8.0, 0, 0.0)),
          ("lava_pool", (9.6, 0, 7.0)), ("glass_bridge", (10.6, 0, -9.8)),
          ("obsidian_pillar", (-10.0, 0, -7.0)), ("spring_pool", (-11.0, 0, -9.2)), ("shrine_lamp", (-9.4, 0, -9.0)),
          ("obsidian_pillar", (-5.2, 0, 0.6)), ("obsidian_pillar", (5.4, 0, 0.4)),
          ("brazier_stand", (-3.4, 0, -1.8)), ("brazier_stand", (3.4, 0, -1.8)), ("brazier_stand", (-3.6, 0, 7.0)), ("brazier_stand", (3.6, 0, 7.0)),
          ("cold_brazier", (-1.6, 0, 5.8)), ("cold_brazier", (1.6, 0, 5.8)),
          ("warm_lantern", (-4.8, 0, 8.4)), ("warm_lantern", (4.8, 0, 8.2)), ("warm_lantern", (-6.0, 0, -0.6)), ("warm_lantern", (6.6, 0, 6.0)),
          ("cinder_cairn", (10.2, 0, 0.8)),
          ("amber_orb_chain", (-5.0, 1.2, 2.0)), ("amber_orb_chain", (5.0, 1.2, 1.6)), ("amber_orb_chain", (-3.0, 1.2, -4.0)), ("amber_orb_chain", (3.4, 1.2, 8.6))]
    A = [("mp_giants", "warden_mp", "down", "idle", 0, (0.0, 1.34, -7.4)),
         ("mp_giants", "cindercaptain", "down", "idle", 1, (3.6, 0, 5.0)),
         ("mp_folk", "mp_trader", "down", "idle", 0, (-7.0, 0, 7.2)),
         ("mp_folk", "lizardman", "right", "idle", 1, (-6.8, 0, -1.6)),
         ("mp_folk", "mp_guide", "left", "walk", 1, (4.6, 0, -4.4)),
         ("mp_folk", "springkeeper", "down", "idle", 2, (-9.6, 0, -5.2)),
         ("mp_folk", "envoy_mp", "up", "idle", 0, (-1.2, 0, 8.6)),
         ("HERO", "wildcaller", "up", "idle", 0, (0.0, 0, 8.4)), ("KINDLE", "pet_kindle", "up", "idle", 0, (1.0, 0, 8.6))]
    D = [("pool_lava", (-8, 3.0), 0, 2), ("pool_lava", (-4, 3.0), 2, 2), ("pool_lava", (0, 3.0), 4, 2), ("pool_lava", (4, 3.0), 1, 2), ("pool_lava", (8, 3.0), 3, 2),
         ("pool_lava", (9.6, 7.0), 5, 2),
         ("pool_forge", (-7.2, -3.4), 0, 2), ("pool_forge", (6.6, -4.9), 1, 1), ("pool_forge", (-7.0, 7.4), 2, 1), ("pool_forge", (-9.0, -0.4), 3, 1),
         ("pool_forge", (-3.4, -1.8), 4, 1), ("pool_forge", (3.4, -1.8), 5, 1), ("pool_forge", (-3.6, 7.0), 0, 1), ("pool_forge", (3.6, 7.0), 3, 1),
         ("pool_forge", (0, -9.0), 2, 2), ("pool_forge", (8.0, -2.0), 1, 2),
         ("pool_cold", (-1.6, 5.8), 0, 1), ("pool_cold", (1.6, 5.8), 3, 1), ("pool_cold", (-5.2, 0.6), 2, 1), ("pool_cold", (5.4, 0.4), 4, 1),
         ("pool_violet", (-1.3, -9.2), 1, 1), ("pool_violet", (1.3, -9.2), 4, 1), ("pool_violet", (-9.4, -9.0), 0, 1), ("pool_teal", (-11.0, -9.2), 2, 2),
         ("frost_vein", (-5.2, 2.2), 3, 1), ("frost_vein", (5.4, 1.6), 0, 1)]
    B = [("forge_flame", (-3.4, 1.9, -1.8), 0), ("forge_flame", (3.4, 1.9, -1.8), 4), ("forge_flame", (-3.6, 1.9, 7.0), 2), ("forge_flame", (3.6, 1.9, 7.0), 6),
         ("cold_flame", (-1.6, 1.9, 5.8), 1), ("cold_flame", (1.6, 1.9, 5.8), 5),
         ("violet_flame", (-1.3, 1.34 + 2.1, -9.2), 3), ("violet_flame", (1.3, 1.34 + 2.1, -9.2), 7),
         ("heat_shimmer", (0, 1.0, 10.4), 2), ("ember_motes", (-7.2, 5.0, -6.2), 0), ("ember_motes", (-4.0, 0.2, 3.4), 3), ("ember_motes", (4.0, 0.2, 3.4), 6),
         ("neon_embers", (0, 0.4, 3.4), 2), ("neon_embers", (8.4, 0.2, 7.0), 5),
         ("glow_orb_blue", (-4.4, 2.2, 5.0), 0), ("glow_orb_violet", (-9.6, 1.9, -8.0), 3), ("glow_orb_red", (6.0, 1.9, 4.6), 5),
         ("neon_fireflies_blue", (-5.4, 0.6, 1.6), 1), ("neon_fireflies_violet", (-10.0, 0.6, -8.0), 4), ("neon_fireflies_red", (7.6, 0.6, 0.6), 6),
         ("glow_frog_blue", (-4.6, 0.0, 4.4), 3), ("glow_frog_violet", (-10.2, 0.0, -6.0), 5), ("spring_bubbles", (-11.0, 0.3, -9.2), 2),
         ("ash_fall", (-2.0, 0.0, 0.0), 1), ("ash_fall", (3.0, 0.0, 5.0), 4), ("ash_fall", (8.0, 0.0, -5.0), 6),
         ("lava_fall", (9.6, 0.0, 6.8), 0)]
    L = [((-8, 0.9, 3.0), LAVA, 7.0, 0.8), ((-4, 0.9, 3.0), LAVA, 7.0, 0.8), ((0, 0.9, 3.0), LAVA, 7.0, 0.9), ((4, 0.9, 3.0), LAVA, 7.0, 0.8), ((8, 0.9, 3.0), LAVA, 7.0, 0.8),
         ((-7.2, 2.4, -2.4), WARM, 6.0, 0.8), ((6.6, 2.0, -5.0), WARM, 5.0, 0.7), ((8, 1.5, -2), LAVA, 6.0, 0.6),
         ((-5.2, 1.6, 1.4), CF, 6.0, 0.6), ((5.4, 1.6, 1.4), CF, 6.0, 0.6), ((-10.0, 1.4, -8.0), VIO, 6.0, 0.6),
         ((0, 5.0, 6.0), "#ffd8a8", 12.0, 0.5), ((0, 4.0, -2.0), "#ffc890", 12.0, 0.45)]
    return dict(pieces=P, actors=A, decals=D, bills=B, extra_lights=L, bg={"night": (48, 42, 54), "day": (236, 204, 170)},
                amb={"night": (0.34, 0.30, 0.34), "day": (1.4, 1.3, 1.22)}, name="cinderhold")


# ------------------------------------------------------------------------------------ The Sigil Forge (area `mp_hall`, 14 x 16 m)
def sigil_forge():
    P = grid("forge_floor", -6, 6, -8, 8)
    P += [("forge_wall", (x, 0, -9.0)) for x in (-6, -4, -2, 2, 4, 6)] + [("forge_wall", (x, 0, 9.0)) for x in (-6, -4, 4, 6)]
    P += [("sigil_mould_wall", (-6.8, 0, -3.0), PI / 2)] + [("forge_wall", (-6.9, 0, z), PI / 2) for z in (1.0, 3.0, 5.0, 7.0)]
    P += [("forge_wall", (6.9, 0, z), -PI / 2) for z in (-7.0, -5.0, -3.0, -1.0, 1.0, 3.0, 5.0, 7.0)]
    P += [("wardens_seat", (0, 0, -6.4)), ("shrine_lamp", (-2.8, 0, -5.2)), ("shrine_lamp", (2.8, 0, -5.2)),
          ("seal_cast_bed", (-4.6, 0, -3.0), PI / 2), ("stamp_press", (-4.8, 0, -5.6)), ("ledger_desk", (-4.6, 0, -0.4), PI / 2),
          # real height: a 1.34 m gallery on the east side (basalt_ledge x2 + one stair on its front face)
          ("basalt_ledge", (4.6, 0, -6.2)), ("basalt_ledge", (4.6, 0, -4.2)), ("basalt_stair", (4.6, 0, -0.7), PI),
          ("cold_brazier", (4.6, 1.34, -6.6)), ("brazier_stand", (-2.6, 0, 3.4)), ("brazier_stand", (2.6, 0, 3.4)),
          ("amber_orb_chain", (-2.0, 1.2, -1.0)), ("amber_orb_chain", (2.0, 1.2, -1.0)), ("amber_orb_chain", (0, 1.2, 4.6)),
          ("warm_lantern", (-5.4, 0, 7.4)), ("warm_lantern", (5.4, 0, 7.4)), ("obsidian_pillar", (-1.6, 0, 1.6))]
    A = [("mp_giants", "warden_mp", "down", "idle", 0, (0.0, 0, -3.6)), ("mp_folk", "envoy_mp", "left", "idle", 1, (2.6, 0, 6.4)),
         ("mp_giants", "forgejudge", "right", "idle", 0, (-2.6, 0, 0.2)), ("HERO", "wildcaller", "up", "idle", 0, (0.0, 0, 6.6)), ("KINDLE", "pet_kindle", "up", "idle", 1, (-1.2, 0, 6.8))]
    D = [("pool_violet", (-2.8, -5.2), 0, 1), ("pool_violet", (2.8, -5.2), 3, 1), ("pool_forge", (-4.6, -3.0), 1, 2), ("pool_forge", (-4.8, -5.6), 4, 1), ("pool_forge", (-2.6, 3.4), 2, 1),
         ("pool_forge", (2.6, 3.4), 5, 1), ("pool_forge", (0, -6.4), 0, 2), ("pool_forge", (-4.6, -0.4), 3, 1), ("pool_cold", (4.6, -6.6), 1, 1), ("pool_forge", (0, 9.0), 4, 2),
         ("pool_forge", (-5.4, 7.4), 1, 1), ("pool_forge", (5.4, 7.4), 2, 1), ("frost_vein", (-1.6, 2.6), 0, 1)]
    B = [("violet_flame", (-2.8, 2.1, -5.2), 0), ("violet_flame", (2.8, 2.1, -5.2), 4), ("cold_flame", (4.6, 1.34 + 1.9, -6.6), 2), ("forge_flame", (-2.6, 1.9, 3.4), 5), ("forge_flame", (2.6, 1.9, 3.4), 1),
         ("ember_motes", (-4.6, 0.4, -3.0), 3), ("neon_embers", (-4.6, 0.6, -3.0), 6), ("neon_fireflies_violet", (0, 0.6, -2.0), 1), ("glow_orb_violet", (-5.6, 2.0, 2.0), 2),
         ("glow_orb_red", (5.4, 2.2, 3.6), 0), ("glow_crystals_violet", (-3.2, 3.0, -7.6), 3)]
    L = [((-2.8, 2.4, -5.2), VIO, 6.0, 0.7), ((2.8, 2.4, -5.2), VIO, 6.0, 0.7), ((-4.6, 0.8, -3.0), LAVA, 6.0, 0.8), ((0, 4.0, 0.0), "#ffd0a0", 14.0, 0.55),
         ((0, 3.0, 6.0), WARM, 10.0, 0.5), ((4.6, 1.8, -6.6), CF, 5.0, 0.5), ((-2.6, 1.6, 3.4), LAVA, 5.0, 0.5), ((2.6, 1.6, 3.4), LAVA, 5.0, 0.5)]
    return dict(pieces=P, actors=A, decals=D, bills=B, extra_lights=L, bg={"night": (40, 32, 44), "day": (150, 128, 118)}, amb={"night": (0.34, 0.30, 0.34)}, name="sigil_forge")


# ------------------------------------------------------------------------------------ The Lavafalls (area `lavafalls`, 20 x 16 m)
def lavafalls():
    P = grid("basalt_floor", -9, 9, -7, 7)
    P += [("lava_fall_cliff", (-6.4, 0, -7.6)), ("lava_fall_cliff", (6.4, 0, -7.6)), ("caldera_mouth_arch", (0, 0, -7.6))]
    P += [("lava_channel", (4, 0, 3.0), PI / 2), ("glass_bridge", (6, 0, 3.0), PI / 2), ("lava_channel", (8, 0, 3.0), PI / 2),
          ("lava_pool", (-6.4, 0, -4.4)), ("lava_pool", (6.4, 0, -4.4)),
          # real height: glass terrace 1.34 m on the west + one stair on its front face
          ("glass_terrace", (-7.4, 0, 0.2)), ("basalt_stair", (-7.4, 0, 2.7)),
          ("spring_pool", (-7.4, 0, 6.0)), ("shrine_lamp", (-5.4, 0, 6.4)), ("shrine_lamp", (-9.2, 0, 4.2)), ("obsidian_pillar", (-5.0, 0, 3.8)),
          ("emberfall_anvil", (-6.0, 0, -4.0)), ("emberfall_anvil", (-3.6, 0, -4.0)),
          ("muspel_waystone", (7.6, 0, 6.4)), ("brazier_stand", (-1.6, 0, -5.4)), ("brazier_stand", (1.6, 0, -5.4)), ("cold_brazier", (-3.6, 0, 1.0)), ("cold_brazier", (3.6, 0, 1.0)),
          ("amber_orb_chain", (0, 1.2, 2.0)), ("amber_orb_chain", (-3.0, 1.2, 4.6)), ("warm_lantern", (3.0, 0, 6.6)), ("warm_lantern", (-2.6, 0, 6.6)), ("cinder_cairn", (4.6, 0, 6.2))]
    A = [("mp_giants", "forgejudge", "right", "idle", 0, (-4.8, 0, -2.4)), ("mp_folk", "mp_guide", "down", "idle", 1, (-7.4, 1.34, -0.6)),
         ("mp_folk", "springkeeper", "down", "idle", 0, (-6.0, 0, 7.4)),
         ("mp_enemies", "magma_hound", "down", "idle", 0, (1.2, 0, -1.4)), ("mp_enemies", "magma_hound", "left", "walk", 1, (3.6, 0, -2.4)),
         ("mp_enemies", "flame_elemental", "down", "idle", 2, (-1.6, 0, -0.8)), ("mp_elites", "ashalpha", "down", "idle", 1, (6.2, 0, -2.0)),
         ("mp_elites", "pyreling", "down", "idle", 3, (-2.8, 0, -2.6)),
         ("HERO", "wildcaller", "up", "idle", 0, (0.0, 0, 5.4)), ("KINDLE", "pet_kindle", "up", "idle", 2, (1.2, 0, 5.6))]
    D = [("pool_lava", (-6.4, -4.4), 0, 3), ("pool_lava", (6.4, -4.4), 3, 3), ("pool_lava", (4, 3.0), 1, 2), ("pool_lava", (8, 3.0), 4, 2), ("pool_lava", (0, -7.0), 2, 2),
         ("pool_forge", (-1.6, -5.4), 0, 1), ("pool_forge", (1.6, -5.4), 3, 1), ("pool_cold", (-3.6, 1.0), 1, 1), ("pool_cold", (3.6, 1.0), 4, 1),
         ("pool_teal", (-7.4, 6.0), 0, 2), ("pool_violet", (-5.4, 6.4), 2, 1), ("pool_violet", (-9.2, 4.2), 5, 1), ("pool_lava", (7.6, 6.4), 3, 1), ("pool_forge", (0, -4.0), 5, 2),
         ("burn_patch", (2.6, -0.2), 2, 1), ("burn_patch", (-4.0, 0.0), 4, 1), ("pool_lava", (-6.0, -4.0), 1, 1)]
    B = [("lava_fall", (-6.4, 0.0, -6.9), 0), ("lava_fall", (-5.6, 0.0, -6.9), 4), ("lava_fall", (6.4, 0.0, -6.9), 2), ("lava_fall", (5.6, 0.0, -6.9), 6),
         ("forge_flame", (-1.6, 1.9, -5.4), 1), ("forge_flame", (1.6, 1.9, -5.4), 5), ("cold_flame", (-3.6, 1.9, 1.0), 3), ("cold_flame", (3.6, 1.9, 1.0), 7),
         ("violet_flame", (-5.4, 2.1, 6.4), 0), ("violet_flame", (-9.2, 2.1, 4.2), 4), ("spring_bubbles", (-7.4, 0.3, 6.0), 3), ("steam_puff", (-8.6, 0.2, 7.0), 2),
         ("ember_motes", (0, 0.2, -3.0), 0), ("ember_motes", (-6.4, 0.2, -4.4), 4), ("neon_embers", (6.4, 0.3, -4.4), 3), ("neon_fireflies_blue", (-3.0, 0.6, 3.0), 2),
         ("neon_fireflies_violet", (-8.0, 0.6, 5.0), 5), ("glow_orb_blue", (-1.0, 2.4, 3.0), 1), ("glow_orb_red", (4.8, 2.0, 0.0), 4), ("glow_orb_violet", (-6.4, 2.0, 2.0), 6),
         ("glow_frog_blue", (-6.0, 0.0, 7.4), 2), ("ash_fall", (1.0, 0.0, 0.0), 3), ("ash_fall", (-5.0, 0.0, -2.0), 5), ("glow_crystals_blue", (-4.4, 3.0, -5.8), 1)]
    L = [((-6.4, 0.8, -4.4), LAVA, 8.0, 0.95), ((6.4, 0.8, -4.4), LAVA, 8.0, 0.95), ((4, 0.8, 3.0), LAVA, 7.0, 0.8), ((8, 0.8, 3.0), LAVA, 7.0, 0.8), ((0, 3.2, -7.0), LAVA, 8.0, 0.8),
         ((-7.4, 1.0, 6.0), TEAL, 6.0, 0.7), ((-5.4, 2.4, 6.4), VIO, 5.0, 0.6), ((-3.6, 2.0, 1.0), CF, 5.0, 0.6), ((3.6, 2.0, 1.0), CF, 5.0, 0.6),
         ((0, 5.0, 3.0), "#ffd0a0", 14.0, 0.5), ((7.6, 3.8, 6.4), CF, 4.0, 0.5)]
    return dict(pieces=P, actors=A, decals=D, bills=B, extra_lights=L, bg={"night": (48, 40, 52), "day": (234, 200, 166)}, amb={"night": (0.34, 0.30, 0.34), "day": (1.4, 1.3, 1.22)}, name="lavafalls")


# ------------------------------------------------------------------------------------ Ember Caldera C9: the Ember Throne (Vharzul 8x)
def caldera_throne():
    P = grid("forge_floor", -8, 8, -6, 8)
    P += [("forge_wall", (x, 0, -7.2)) for x in (-8, -6, 6, 8)]
    P += [("ember_throne", (0, 0, -5.6))]
    P += [("lava_channel", (-9.4, 0, z)) for z in (-4, 0, 4)] + [("lava_channel", (9.4, 0, z)) for z in (-4, 0, 4)]                     # the arena edge lava (rises in phase 2)
    r = 5.2
    P += [("warden_lamp_stand", (r * math.cos(a), 0, r * math.sin(a) - 0.4)) for a in (PI / 2, PI / 2 + 2 * PI / 3, PI / 2 + 4 * PI / 3)]
    P += [("cold_brazier", (-5.4, 0, 6.6)), ("cold_brazier", (5.4, 0, 6.6)), ("hanging_crystals", (-6.0, 0, -2.0)), ("hanging_crystals", (6.0, 0, -2.0)), ("hanging_crystals", (0, 0, 6.0)),
          ("basalt_ledge", (-7.0, 0, 6.4)), ("basalt_stair", (-7.0, 0, 3.9), PI)]
    A = [("boss_vharzul", "vharzul", "down", "idle", 1, (0.0, 0, -1.8)), ("HERO", "wildcaller", "up", "idle", 0, (0.0, 0, 6.2)), ("KINDLE", "pet_kindle", "up", "idle", 3, (1.2, 0, 6.4)),
         ("mp_enemies", "flame_elemental", "down", "idle", 1, (-4.6, 0, 1.6)), ("mp_enemies", "flame_elemental", "down", "idle", 3, (4.6, 0, 1.6))]
    D = [("pool_lava", (-9.4, -4), 0, 2), ("pool_lava", (-9.4, 0), 3, 2), ("pool_lava", (-9.4, 4), 1, 2), ("pool_lava", (9.4, -4), 4, 2), ("pool_lava", (9.4, 0), 2, 2), ("pool_lava", (9.4, 4), 5, 2),
         ("pool_lava", (0, -4.4), 0, 3), ("magma_pool", (-3.0, 3.0), 0, 1), ("magma_pool", (3.4, 2.4), 3, 1), ("pillar_telegraph", (-1.6, 0.8), 2, 2), ("pillar_telegraph", (2.0, 2.6), 4, 2),
         ("pool_cold", (-5.4, 6.6), 1, 1), ("pool_cold", (5.4, 6.6), 3, 1)]
    for k, a in enumerate((PI / 2, PI / 2 + 2 * PI / 3, PI / 2 + 4 * PI / 3)):
        D.append(("pool_violet", (r * math.cos(a), r * math.sin(a) - 0.4), k * 2, 1))
    B = [("warden_lamp", (r * math.cos(a), 3.2, r * math.sin(a) - 0.4), 7 if k else 1) for k, a in enumerate((PI / 2, PI / 2 + 2 * PI / 3, PI / 2 + 4 * PI / 3))]
    B += [("cold_flame", (-5.4, 1.9, 6.6), 0), ("cold_flame", (5.4, 1.9, 6.6), 4), ("fire_pillar", (-1.6, 0.0, 0.8), 4), ("flame_ward", (0.0, 0.0, 6.2), 3), ("ember_swarm", (4.6, 0.0, -0.6), 5),
          ("ember_motes", (-4.0, 0.2, -3.0), 2), ("neon_embers", (4.0, 0.2, -3.0), 5), ("ash_fall", (0, 0, 0), 2), ("glow_crystals_blue", (-6.0, 3.0, -2.0), 1), ("glow_crystals_violet", (6.0, 3.0, -2.0), 4)]
    L = [((-9.4, 0.8, 0), LAVA, 9.0, 0.9), ((9.4, 0.8, 0), LAVA, 9.0, 0.9), ((0, 3.0, -5.0), LAVA, 12.0, 0.9), ((0, 6.0, 0.0), "#ffd0a0", 16.0, 0.6),
         ((-5.4, 2.0, 6.6), CF, 5.0, 0.6), ((5.4, 2.0, 6.6), CF, 5.0, 0.6)]
    return dict(pieces=P, actors=A, decals=D, bills=B, extra_lights=L, bg={"night": (46, 38, 50), "day": (140, 120, 112)}, amb={"night": (0.34, 0.30, 0.34)},
                reach=15.5, reach_z=-1.8, name="caldera_throne")
