"""Scene / area layouts (also written to metadata/jotunheim_layout.json with the placement notes)."""
AUR_G, AUR_V, CF, TEAL = "#3fe0a0", "#a45cf0", "#3fb8ff", "#2fd0d0"
HERO = ("jt_hero",)


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


# ----------------------------------------------------------------------------------------- Stonehollow (area `jotunheim`, 24 x 22 m hub)
def stonehollow():
    P = grid("snow_floor", -11, 11, -7, 7)
    P += [("longhouse", (-7.8, 0, -6.0)), ("longhouse", (7.8, 0, -6.2)),
          ("stone_ledge", (-1.55, 0, -4.2)), ("stone_ledge", (1.55, 0, -4.2)), ("stone_stair", (0, 0, -1.7)),            # the Jarl's plateau, 1.34 m, one stair
          ("cold_brazier", (-2.4, 1.34, -5.0)), ("cold_brazier", (2.4, 1.34, -5.0)), ("rune_standing_stone", (0, 1.34, -5.2)),
          ("stone_ledge", (10.0, 0, -1.0)), ("rune_standing_stone", (10.0, 1.34, -1.4)), ("snow_mound", (-10.4, 0, -1.4)),
          ("ice_lake", (6.6, 0, 3.8)),
          ("lift_stone", (-1.4, 0, 2.6)), ("lift_stone", (0, 0, 3.3)), ("lift_stone", (1.4, 0, 2.6)),                      # Welcome Ring
          ("cold_brazier", (-3.6, 0, 1.6)), ("cold_brazier", (3.6, 0, 1.6)), ("cold_brazier", (-3.2, 0, 4.8)), ("cold_brazier", (3.2, 0, 4.8)),
          ("rune_standing_stone", (-5.4, 0, 0.2)), ("rune_standing_stone", (5.2, 0, -0.4)),
          ("warm_lantern", (-7.8, 0, 6.8)), ("warm_lantern", (4.8, 0, 6.4)), ("goat_fence", (-10.6, 0, 5.6)), ("goat_fence", (-8.6, 0, 5.6)), ("goat_fence", (-6.6, 0, 6.2)), ("fur_stall", (-6.0, 0, 3.0))]
    A = [("jt_giants", "jarl", "down", "idle", 0, (-0.9, 1.34, -4.0)), ("jt_giants", "kolbrun", "down", "idle", 1, (1.8, 0, 5.0)),
         ("jt_giants", "grimsa", "down", "idle", 2, (-6.0, 0, 4.6)), ("jt_giants", "goatwife", "right", "walk", 1, (-8.8, 0, 4.4)),
         ("jt_giants", "skuli", "left", "idle", 0, (-9.6, 0, 4.2)), ("jt_giants", "rimecaptain", "down", "idle", 0, (3.8, 0, 3.4)),
         ("jt_giants", "gi_man", "left", "walk", 2, (8.8, 0, 1.2)), ("jt_giants", "gi_woman", "right", "idle", 1, (-4.0, 0, -0.6)),
         ("ulfar", "ulfar", "up", "idle", 1, (-2.2, 0, 6.2)), ("HERO", "wildcaller", "up", "idle", 0, (0.0, 0, 6.4)), ("FLURRY", "pet_flurry", "up", "idle", 0, (1.0, 0, 6.5))]
    D = [("pool_cold", (-2.4, -5.0), 0, 1), ("pool_cold", (2.4, -5.0), 1, 1), ("pool_cold", (0, -5.2), 2, 1), ("pool_cold", (-3.6, 1.6), 3, 1), ("pool_cold", (3.6, 1.6), 4, 1),
         ("pool_cold", (-3.2, 4.8), 5, 1), ("pool_cold", (3.2, 4.8), 0, 1), ("pool_cold", (-5.4, 0.2), 1, 1), ("pool_cold", (5.2, -0.4), 2, 1), ("pool_cold", (10.0, -1.4), 3, 1),
         ("pool_teal", (6.6, 3.8), 0, 2), ("pool_aurora", (-3.0, 3.8), 1, 2), ("pool_aurora", (4.5, 6.0), 2, 2), ("pool_violet", (-8.5, -2.0), 0, 2), ("pool_violet", (8.0, 1.8), 3, 1),
         ("rune_pulse", (0, 3.0), 2, 1), ("rune_pulse", (-5.4, 0.2), 3, 1), ("rune_pulse", (5.2, -0.4), 1, 1),
         ("glow_fog", (-6.0, -0.6), 2, 2), ("glow_fog", (6.2, -2.6), 5, 2), ("glow_fog", (-2.0, 7.0), 0, 2), ("glow_fog", (10.5, 5.2), 4, 2)]
    B = [("cold_flame", (-2.4, 2.0 + 1.34, -5.0), 0), ("cold_flame", (2.4, 2.0 + 1.34, -5.0), 3), ("cold_flame", (-3.6, 2.0, 1.6), 5), ("cold_flame", (3.6, 2.0, 1.6), 2),
         ("cold_flame", (-3.2, 2.0, 4.8), 6), ("cold_flame", (3.2, 2.0, 4.8), 1),
         ("ice_sparkles", (6.6, 0.4, 3.8), 2), ("ice_sparkles", (-10.4, 1.0, -1.4), 5), ("ice_sparkles", (0, 1.0, 0.4), 1), ("ice_sparkles", (10, 1.6, -1.0), 6),
         ("neon_fireflies_blue", (-5.0, 0.6, 3.0), 1), ("neon_fireflies_green", (4.6, 0.6, 5.6), 3), ("neon_fireflies_violet", (-8.4, 0.4, -1.8), 4), ("neon_fireflies_blue", (7.4, 0.6, -2.8), 6),
         ("glow_orb_blue", (-4.6, 2.2, 2.4), 0), ("glow_orb_green", (5.6, 1.9, 4.6), 2), ("glow_orb_violet", (-8.0, 1.8, 3.0), 4), ("glow_orb_blue", (2.8, 2.6, -2.2), 6)]
    L = [((0, 6.0, 2.0), AUR_G, 14.0, 0.45), ((-9, 6.0, -2), AUR_V, 12.0, 0.4), ((9, 6.0, -1), AUR_G, 12.0, 0.35), ((6.6, 0.8, 3.8), TEAL, 6.0, 0.6),
         ((0, 1.5, 6.0), "#cfe4ff", 6.0, 0.5)]
    return dict(pieces=P, actors=A, decals=D, bills=B, extra_lights=L,
                bg={"night": (40, 50, 72), "day": (150, 168, 196)}, amb={"night": (0.20, 0.21, 0.26)}, name="stonehollow")


# ----------------------------------------------------------------------------------------- Rime Caves (area `rimecaves`, 20 x 16 m)
def rimecaves():
    P = grid("ice_floor", -9, 9, -5, 5)
    P += [("ice_wall", (x, 0, -6.3)) for x in (-9, -7, -5, -3, 3, 5, 7, 9)]
    P += [("barrow_door", (0, 0, -6.7)),
          ("stone_ledge", (-7.6, 0, -1.8)), ("stone_stair", (-7.6, 0, 1.0), ), ("snow_mound", (7.8, 0, -2.6)),
          ("glow_ice_pool", (-3.0, 0, 1.8)), ("glow_ice_pool", (4.6, 0, 2.6)), ("glow_ice_pool", (0.6, 0, -3.0)),
          ("ice_crystal_cluster", (-8.6, 0, 4.6)), ("ice_crystal_cluster", (8.4, 0, 4.4)), ("ice_crystal_cluster", (6.6, 0, -4.4)),
          ("frost_rune_pillar", (-4.6, 0, -2.8)), ("frost_rune_pillar", (3.2, 0, -4.4)), ("frost_rune_pillar", (-1.4, 0, 5.2)), ("frost_rune_pillar", (8.2, 0, 0.4)),
          ("icicle_cluster", (-2.0, 0, -1.0)), ("icicle_cluster", (3.0, 0, 0.0)), ("icicle_cluster", (-6.0, 0, 3.0)), ("icicle_cluster", (6.8, 0, 1.4)),
          ("cold_brazier", (-2.2, 0, -5.0)), ("cold_brazier", (2.2, 0, -5.0)), ("warm_lantern", (-4.0, 0, -0.4)), ("warm_lantern", (6.4, 0, 3.4)), ("warm_lantern", (-0.6, 0, 6.0))]
    P = [p for p in P if not (p[0] == "stone_stair")]
    P += [("stone_stair", (-7.6, 0, 1.0))]
    A = [("jt_giants", "rimewife", "down", "idle", 0, (-5.6, 0, -2.0)), ("HERO", "wildcaller", "up", "idle", 0, (0.4, 0, 5.2)),
         ("ulfar", "ulfar", "up", "idle", 2, (-1.8, 0, 5.0)), ("FLURRY", "pet_flurry", "up", "idle", 1, (1.5, 0, 5.4)),
         ("jt_enemies", "frost_troll", "down", "idle", 1, (-0.8, 0, -0.2)), ("jt_enemies", "ice_golem", "left", "idle", 1, (5.8, 0, -1.4)),
         ("jt_elites", "frostmother", "down", "idle", 2, (7.4, 0, 2.0)), ("jt_enemies", "avalanche_golem", "down", "idle", 0, (-9.0, 0, 0.0))]
    D = [("pool_teal", (-3.0, 1.8), 0, 2), ("pool_teal", (4.6, 2.6), 2, 2), ("pool_teal", (0.6, -3.0), 4, 2), ("pool_teal", (-8.6, 4.6), 1, 1), ("pool_teal", (8.4, 4.4), 3, 1),
         ("pool_teal", (6.6, -4.4), 5, 1), ("pool_cold", (-2.2, -5.0), 0, 1), ("pool_cold", (2.2, -5.0), 3, 1), ("pool_cold", (0, -5.8), 2, 3),
         ("pool_cold", (-4.6, -2.8), 1, 1), ("pool_cold", (3.2, -4.4), 4, 1), ("pool_cold", (-1.4, 5.2), 5, 1), ("pool_cold", (8.2, 0.4), 0, 1),
         ("pool_violet", (-6.0, 3.0), 2, 1), ("pool_violet", (6.8, 1.4), 4, 1), ("glow_fog", (-4.0, 3.6), 3, 2), ("glow_fog", (3.0, -0.8), 1, 2), ("glow_fog", (8.0, 5.0), 5, 2),
         ("glow_fog", (-8.0, -3.6), 0, 2), ("rune_pulse", (0, -4.4), 1, 2)]
    B = [("cold_flame", (-2.2, 2.0, -5.0), 1), ("cold_flame", (2.2, 2.0, -5.0), 4),
         ("glow_vines", (-5.6, 3.2, 3.6), 2), ("glow_vines", (-1.0, 3.2, -1.0), 5), ("glow_vines", (5.0, 3.2, 3.8), 0), ("glow_vines", (7.4, 3.2, -1.8), 3),
         ("glow_frog", (-2.2, 0.0, 3.0), 3), ("glow_frog", (5.4, 0.0, 3.8), 5), ("glow_frog", (0.2, 0.0, -2.2), 1),
         ("ice_sparkles", (-8.6, 1.0, 4.6), 2), ("ice_sparkles", (8.4, 1.0, 4.4), 4), ("ice_sparkles", (6.6, 1.0, -4.4), 6), ("ice_sparkles", (-3, 0.6, 1.8), 1),
         ("neon_fireflies_green", (-4.0, 0.6, 1.0), 2), ("neon_fireflies_blue", (3.8, 0.6, 1.4), 5), ("neon_fireflies_violet", (-7.0, 0.6, -3.6), 0), ("neon_fireflies_green", (2.0, 0.6, 5.0), 6),
         ("glow_orb_green", (-5.2, 2.2, -0.6), 0), ("glow_orb_blue", (2.0, 2.6, 0.8), 3), ("glow_orb_violet", (7.0, 1.9, -0.2), 5)]
    L = [((-3.0, 1.2, 1.8), TEAL, 8.0, 0.7), ((4.6, 1.2, 2.6), TEAL, 8.0, 0.7), ((0.6, 1.2, -3.0), TEAL, 8.0, 0.7), ((0, 4.0, 1.0), "#bfe8ff", 14.0, 0.5),
         ((-8, 2.0, 4), AUR_V, 8.0, 0.4), ((8, 2.0, 4), AUR_V, 8.0, 0.4)]
    return dict(pieces=P, actors=A, decals=D, bills=B, extra_lights=L,
                bg={"night": (20, 28, 42), "day": (140, 164, 192)}, amb={"night": (0.08, 0.10, 0.13)}, lscale=0.62, name="rimecaves")


# ----------------------------------------------------------------------------------------- Titan's Barrow (dungeon, B9 Throne Barrow + B2 shields)
def barrow():
    P = grid("barrow_floor", -9, 9, -5, 5)
    P += [("barrow_wall", (x, 0, -6.3)) for x in (-9, -7, -5, 5, 7, 9)] + [("barrow_wall", (x, 0, -6.3)) for x in (-3, 3)]
    P += [("ice_throne", (0, 0, -3.8)), ("rune_brazier", (-5.0, 0, -3.0)), ("rune_brazier", (5.0, 0, -3.0)), ("rune_brazier", (0, 0, 4.4)),
          ("shield_rack", (-7.6, 0, -4.8)), ("shield_rack", (7.6, 0, -4.8)), ("stone_ledge", (-8.0, 0, 1.6)), ("stone_stair", (-8.0, 0, 4.4)),
          ("glow_ice_pool", (-4.4, 0, 1.2)), ("glow_ice_pool", (4.4, 0, 1.2)), ("rune_bridge", (0, 0, 1.0)), ("rune_bridge", (0, 0, 3.0)),
          ("frost_rune_pillar", (-3.2, 0, 2.6)), ("frost_rune_pillar", (3.2, 0, 2.6)), ("warm_lantern", (2.4, 0, 5.2)), ("warm_lantern", (-2.8, 0, 5.4))]
    A = [("boss_hrimgard", "hrimgard", "down", "idle", 1, (0.0, 0, -1.4)), ("HERO", "wildcaller", "up", "idle", 0, (0.2, 0, 5.6)), ("ulfar", "ulfar", "up", "idle", 3, (-1.8, 0, 5.4)),
         ("FLURRY", "pet_flurry", "up", "idle", 2, (1.4, 0, 5.8)), ("jt_elites", "ormgar", "down", "idle", 1, (-6.0, 0, 0.6)), ("jt_enemies", "rime_berserker", "down", "idle", 2, (6.4, 0, 1.0)),
         ("jt_enemies", "frost_troll", "left", "idle", 0, (-5.4, 0, 3.2))]
    D = [("pool_cold", (0, -0.2), 0, 4), ("pool_cold", (-5.0, -3.0), 1, 1), ("pool_cold", (5.0, -3.0), 2, 1), ("pool_cold", (0, 4.4), 3, 1), ("pool_cold", (0, -3.4), 4, 2),
         ("pool_teal", (-4.4, 1.2), 0, 2), ("pool_teal", (4.4, 1.2), 3, 2), ("pool_cold", (-3.2, 2.6), 5, 1), ("pool_cold", (3.2, 2.6), 1, 1), ("rune_pulse", (0, 2.0), 2, 2),
         ("glow_fog", (-6.0, 4.0), 1, 2), ("glow_fog", (6.0, -0.4), 4, 2), ("pool_violet", (7.6, -4.0), 0, 1), ("pool_violet", (-7.6, -4.0), 2, 1)]
    B = [("cold_flame", (-5.0, 2.6 * .8 + .5, -3.0), 0), ("cold_flame", (5.0, 2.6 * .8 + .5, -3.0), 4), ("cold_flame", (0, 2.6 * .8 + .5, 4.4), 2),
         ("ice_sparkles", (-4.4, 0.6, 1.2), 3), ("ice_sparkles", (4.4, 0.6, 1.2), 5), ("neon_fireflies_blue", (-2.0, 0.6, 2.0), 1), ("neon_fireflies_violet", (6.0, 0.6, 3.0), 4),
         ("glow_orb_blue", (-6.8, 2.0, 2.6), 0), ("glow_orb_blue", (6.8, 2.2, 3.2), 5)]
    L = [((0, 4.0, 0.0), CF, 14.0, 0.7), ((0, 3.0, 4.0), "#bfe8ff", 10.0, 0.5), ((-5, 1.2, 1.2), TEAL, 6.0, 0.5), ((5, 1.2, 1.2), TEAL, 6.0, 0.5),
         ((-7, 3.0, -4), AUR_V, 8.0, 0.4), ((7, 3.0, -4), AUR_V, 8.0, 0.4)]
    return dict(pieces=P, actors=A, decals=D, bills=B, extra_lights=L,
                bg={"night": (46, 58, 84), "day": (120, 138, 168)}, reach=12.8, name="barrow")
