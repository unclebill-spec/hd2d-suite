"""Asgard scene / area layouts (also written to metadata/asgard_layout.json). World metres, +z toward the camera, hero faces -z ('up').
Props / fx stay off spawns, stairs and ledge edges. EVERY area / Reliquary room has a 1.34 m ledge + stair: gold_ledge pairs (3.1 x 2.1 m, top 1.34)
+ one gold_stair (7 steps, 3.5 m run) centred on the front face (stair centre z = ledge z + 1 + 1.75, climbs toward -z)."""
import math
PI = math.pi
CF, VIO, WARM, RED, GOLDL = "#3fb8ff", "#a45cf0", "#ffc85a", "#e8321e", "#ffd88a"
SKY = "#d0c8ff"


def grid(name, x0, x1, z0, z1, step=2.0):
    out = []; x = x0
    while x <= x1 + 1e-6:
        z = z0
        while z <= z1 + 1e-6:
            out.append((name, (x, 0, z))); z += step
        x += step
    return out


def terrace(cx, zb):
    return [("gold_ledge", (cx - 1.55, 0, zb)), ("gold_ledge", (cx + 1.55, 0, zb)), ("gold_stair", (cx, 0, zb + 1 + 1.75))]


def pool(x, z, k, sc=1, n="pool_gold"):
    return (n, (x, z), k, sc)


def mkscene(name, P, A, D, B, L, bg, amb, **kw):
    kw.setdefault("lscale", 0.7)
    return dict(pieces=P, actors=A, decals=D, bills=B, extra_lights=L, bg=bg, amb=amb, name=name, **kw)


HERO = [("HERO", "wildcaller", "up", "idle", 0, (0.0, 0, 8.4)), ("as_sigrun", "sigrun", "up", "idle", 1, (1.2, 0, 8.6))]
BG = {"night": (16, 16, 30), "day": (172, 160, 150)}
AMB = {"night": (0.16, 0.15, 0.22), "day": (0.68, 0.64, 0.62)}


# ---------------------------------------------------------------------------------- Goldspire (area `asgard`, 24 x 22 m hub)
def asgard():
    P = grid("marble_floor", -11, 11, -9, 11)
    P += [("gold_arch", (0, 0, 10.6)), ("hall_facade", (0, 0, -10.4))]
    P += terrace(0.0, -7.2) + [("dawn_flame_brazier", (-2.8, 1.34, -7.4)), ("dawn_flame_brazier", (2.8, 1.34, -7.4))]
    P += [("rune_pillar", (-7.0, 0, 3.0)), ("rune_pillar", (0.0, 0, 4.5)), ("rune_pillar", (7.0, 0, 3.0)),
          ("market_stall", (-8.0, 0, 5.5)), ("skyfield_fence", (10.0, 0, -3.0)), ("moot_ring", (6.0, 0, -6.0)), ("marble_spring", (-11.0, 0, -2.0), PI / 2),
          ("gold_lamp", (-4.2, 0, 7.4)), ("gold_lamp", (4.2, 0, 7.6)), ("gold_lamp", (-6.0, 0, -4.6)), ("gold_lamp", (6.4, 0, 1.0)), ("gold_lamp", (-3.6, 0, 0.6)),
          ("angel_statue", (-9.6, 0, -7.6)), ("as_waystone", (9.6, 0, 7.0)),
          ("gold_orb_chain", (-3.0, 0.2, -3.4)), ("gold_orb_chain", (3.0, 0.2, -3.6))]
    A = [("as_folk", "lordwarden", "down", "idle", 0, (0.0, 1.34, -6.2)), ("as_folk", "as_guide", "down", "idle", 1, (2.6, 0, 8.2)),
         ("as_folk", "as_trader", "down", "idle", 2, (-8.0, 0, 7.0)), ("as_folk", "groom", "left", "idle", 1, (8.2, 0, -3.0)),
         ("as_folk", "runemaster", "right", "walk", 1, (-4.8, 0, 2.2)), ("as_folk", "envoy_as", "down", "idle", 0, (4.2, 0, -5.0))] + HERO
    D = [pool(-4.2, 7.4, 0), pool(4.2, 7.6, 3), pool(-6.0, -4.6, 1), pool(6.4, 1.0, 4), pool(-3.6, 0.6, 2), pool(-2.8, -7.4, 5), pool(2.8, -7.4, 1), pool(-8.0, 5.5, 3),
         pool(0, -10.0, 2, 2), pool(0, 10.0, 1, 2), pool(-3.0, -3.4, 4), pool(3.0, -3.6, 0), pool(-11.0, -2.0, 3, 2),
         pool(-7, 3, 0, 1, "pool_cold"), pool(0, 4.5, 3, 1, "pool_cold"), pool(7, 3, 5, 1, "pool_cold"), pool(6.0, -6.0, 2, 2, "pool_cold"), pool(9.6, 7.0, 1, 1, "pool_cold"),
         pool(-9.6, -7.6, 4, 1, "pool_violet"), ("rune_pulse", (6.0, -6.0), 0, 2), ("as_shadow", (0.0, -6.2), 0, 1)]
    B = [("lightning_arc", (-7.0, 4.8, 3.0), 0), ("lightning_arc", (0.0, 4.8, 4.5), 1), ("gold_flame", (-2.8, 1.34 + 1.3, -7.4), 0), ("gold_flame", (2.8, 1.34 + 1.3, -7.4), 4),
         ("gold_dust", (-2.0, 1.0, 1.0), 1), ("gold_dust", (5.0, 1.0, 5.0), 4), ("neon_fireflies_blue", (9.0, 0.6, -1.0), 2), ("neon_fireflies_violet", (-9.0, 0.6, -6.0), 5),
         ("glow_orb_blue", (-6.0, 2.2, 6.0), 0), ("glow_orb_violet", (8.0, 2.0, -7.0), 3), ("spring_bubbles", (-11.0, 0.3, -2.0), 2)]
    L = [((-7, 4.8, 3.0), CF, 8.0, 0.8), ((0, 4.8, 4.5), CF, 8.0, 0.8), ((7, 4.8, 3.0), CF, 8.0, 0.8), ((-8.0, 1.8, 6.0), WARM, 6.0, 0.9), ((0, 2.4, -8.0), WARM, 7.0, 0.9),
         ((-11, 1.0, -2.0), WARM, 6.0, 0.7), ((6.0, 0.8, -6.0), CF, 6.0, 0.6), ((-9.6, 1.6, -7.6), VIO, 5.0, 0.6), ((0, 5.0, 6.0), SKY, 14.0, 0.5), ((0, 5.0, -3.0), GOLDL, 14.0, 0.45)]
    return mkscene("asgard", P, A, D, B, L, BG, AMB)


# ---------------------------------------------------------------------------------- Thunder Hall (gs_hall, 14 x 18 m)
def gs_hall():
    P = grid("marble_floor", -6, 6, -8, 8)
    P += [("marble_wall", (x, 0, -8.9)) for x in range(-6, 7, 2)] + [("marble_wall", (-6.9, 0, z), PI / 2) for z in range(-6, 8, 2)] + [("marble_wall", (6.9, 0, z), -PI / 2) for z in range(-6, 8, 2)]
    P += terrace(0.0, -7.0)[:2] + [("gold_stair", (0.0, 0, -7.0 + 1 + 1.75)), ("high_seat", (0, 1.34, -7.4)), ("rune_pillar", (-2.8, 1.34, -7.4)), ("rune_pillar", (2.8, 1.34, -7.4))]
    P += [("long_table", (-3.4, 0, -1.0), PI / 2), ("long_table", (3.4, 0, -1.0), PI / 2), ("long_table", (-3.4, 0, 3.6), PI / 2), ("long_table", (3.4, 0, 3.6), PI / 2),
          ("rune_forge", (-5.0, 0, 6.6)), ("dawn_flame_brazier", (0, 0, 1.4)), ("gold_lamp", (-5.6, 0, -4.0)), ("gold_lamp", (5.6, 0, -4.0)), ("gold_lamp", (5.6, 0, 6.6)),
          ("gold_orb_chain", (-2.0, 0.2, 1.0)), ("gold_orb_chain", (2.0, 0.2, 1.0)), ("gold_orb_chain", (0, 0.2, -3.4))]
    A = [("as_folk", "lordwarden", "down", "idle", 0, (0.0, 1.34, -6.4)), ("as_folk", "runemaster", "down", "idle", 1, (-4.2, 0, 7.4)),
         ("as_folk", "envoy_as", "right", "idle", 1, (-1.6, 0, -2.6)), ("as_folk", "fridleif", "left", "idle", 0, (1.8, 0, -2.4)),
         ("HERO", "wildcaller", "up", "idle", 0, (0.0, 0, 6.0)), ("as_sigrun", "sigrun", "up", "idle", 1, (1.2, 0, 6.2))]
    D = [pool(0, 1.4, 1, 2), pool(-5.6, -4.0, 2), pool(5.6, -4.0, 4), pool(5.6, 6.6, 0), pool(-2.0, 1.0, 3), pool(2.0, 1.0, 5), pool(0, -3.4, 2), pool(0, -6.0, 4, 2),
         pool(-2.8, -7.4, 1, 1, "pool_cold"), pool(2.8, -7.4, 3, 1, "pool_cold"), pool(-5.0, 6.6, 0, 1, "pool_cold")]
    B = [("gold_flame", (0, 1.3, 1.4), 2), ("lightning_arc", (-2.8, 6.2, -7.4), 1), ("gold_dust", (0, 1.0, 2.0), 3), ("rain", (0, 4.0, -8.6), 2), ("glow_orb_blue", (-4.6, 2.0, 5.6), 4)]
    L = [((0, 1.8, 1.4), WARM, 7.0, 1.0), ((0, 2.4, -6.6), WARM, 7.0, 0.8), ((-2.8, 5.0, -7.4), CF, 7.0, 0.8), ((2.8, 5.0, -7.4), CF, 7.0, 0.8), ((-5.0, 1.6, 6.6), CF, 5.0, 0.7),
         ((0, 5.0, 2.0), GOLDL, 12.0, 0.45)]
    return mkscene("gs_hall", P, A, D, B, L, BG, AMB, lscale=0.55)


# ---------------------------------------------------------------------------------- Dawn Temple (gs_temple, 16 x 16 m)
def gs_temple():
    P = grid("marble_floor", -7, 7, -7, 7)
    P += [("marble_wall", (x, 0, -9.9)) for x in (-6, -4, 4, 6)] + [("temple_window", (-7.9, 0, z), PI / 2) for z in (-4, 0, 4)] + [("temple_window", (7.9, 0, z), -PI / 2) for z in (-4, 0, 4)]
    P += [("reliquary_door", (0, 0, -9.0)), ("dark_altar", (0, 0, -5.0))]
    P += terrace(-4.6, -6.0) + [("angel_statue", (-5.8, 1.34, -6.4)), ("angel_statue", (4.6, 0, -6.6)), ("angel_statue", (6.0, 0, 2.6))]
    P += [("rimed_lamp", (-3.0, 0, -1.6)), ("rimed_lamp", (3.0, 0, -1.6)), ("rimed_lamp", (3.0, 0, 3.4)), ("gold_lamp", (-3.0, 0, 3.4)), ("gold_lamp", (-1.6, 0, 6.0)), ("marble_spring", (5.6, 0, 6.0))]
    A = [("as_folk", "priestess", "down", "idle", 0, (1.8, 0, -3.4)), ("as_enemies", "light_wraith", "down", "idle", 1, (4.4, 0, -4.4)),
         ("HERO", "wildcaller", "up", "idle", 0, (0.0, 0, 5.0)), ("as_sigrun", "sigrun", "up", "idle", 1, (1.2, 0, 5.2))]
    D = [pool(0, -5.0, 1, 2, "pool_cold"), pool(-3.0, -1.6, 2, 1, "pool_cold"), pool(3.0, -1.6, 4, 1, "pool_cold"), pool(3.0, 3.4, 0, 1, "pool_cold"), pool(-3.0, 3.4, 3), pool(-1.6, 6.0, 5),
         pool(5.6, 6.0, 2, 2), pool(0, -8.2, 3, 2, "pool_cold"), pool(-7.2, -4, 1, 1, "pool_violet"), pool(-7.2, 0, 4, 1, "pool_violet"), pool(7.2, -4, 2, 1, "pool_violet"), pool(7.2, 0, 5, 1, "pool_violet"),
         pool(7.2, 4, 0, 1, "pool_violet"), ("rime_tell", (0.6, -4.6), 1, 1), ("rune_pulse", (0, -8.0), 2, 2)]
    B = [("cold_flame", (0, 1.5, -5.0), 1), ("neon_fireflies_violet", (-4.0, 0.6, 0.0), 2), ("neon_fireflies_blue", (4.0, 0.6, 1.0), 5), ("glow_orb_violet", (-2.0, 2.2, 1.0), 0), ("spring_bubbles", (5.6, 0.3, 6.0), 3)]
    L = [((0, 1.6, -5.0), CF, 7.0, 0.8), ((-7.2, 2.2, -4), VIO, 6.0, 0.8), ((-7.2, 2.2, 0), VIO, 6.0, 0.8), ((7.2, 2.2, -4), VIO, 6.0, 0.8), ((7.2, 2.2, 0), VIO, 6.0, 0.8),
         ((-3.0, 2.7, 3.4), WARM, 6.0, 0.9), ((-1.6, 2.7, 6.0), WARM, 6.0, 0.9), ((5.6, 1.0, 6.0), WARM, 6.0, 0.7), ((0, 2.8, -8.2), CF, 7.0, 0.7), ((0, 5.0, 1.0), SKY, 12.0, 0.45)]
    return mkscene("gs_temple", P, A, D, B, L, {"night": BG["night"]}, {"night": AMB["night"]}, lscale=0.5)


# ---------------------------------------------------------------------------------- The Gilded Reliquary G1..G9
def room(name, extra_P, A, D, B, L, ledge_x=-4.4, ledge_z=-3.6, size=6, void=None, rimed=True, **kw):
    P = [p for p in grid("marble_floor", -size, size, -size, size) if not (void and void[0] <= p[1][0] <= void[1] and void[2] <= p[1][2] <= void[3])]
    P += [("marble_wall", (x, 0, -size - 0.9)) for x in range(-size, size + 1, 2)] + [("marble_wall", (-size - 0.9, 0, z), PI / 2) for z in range(-size + 2, size, 2)]
    P += terrace(ledge_x, ledge_z) + [("dawn_flame_brazier", (ledge_x + 3.2, 1.34, ledge_z - 0.6))]
    lampk = "rimed_lamp" if rimed else "gold_lamp"
    P += [(lampk, (4.6, 0, -4.6)), ("gold_lamp", (4.6, 0, 4.4)), ("gold_lamp", (-1.4, 0, 5.2)), (lampk, (-4.6, 0, 4.4))] + extra_P
    A = A + [("HERO", "wildcaller", "up", "idle", 0, (0.0, 0, 5.0)), ("as_sigrun", "sigrun", "up", "idle", 3, (1.2, 0, 5.2))]
    lp = "pool_cold" if rimed else "pool_gold"
    D = D + [pool(4.6, 4.4, 1), pool(-1.4, 5.2, 4), pool(ledge_x + 3.2, ledge_z - 0.6, 0), pool(4.6, -4.6, 3, 1, lp), pool(-4.6, 4.4, 2, 1, lp)]
    B = B + [("gold_flame", (ledge_x + 3.2, 1.34 + 1.3, ledge_z - 0.6), 2), ("gold_dust", (0, 1.0, 1.0), 3), ("neon_fireflies_blue", (-2.0, 0.6, 1.0), 4)]
    L = L + [((4.6, 2.7, 4.4), WARM, 6.0, 0.9), ((-1.4, 2.7, 5.2), WARM, 5.0, 0.8), ((ledge_x + 3.2, 3.0, ledge_z - 0.6), WARM, 6.0, 0.8), ((4.6, 2.9, -4.6), CF if rimed else WARM, 5.0, 0.7),
             ((0, 5.0, 2.0), SKY, 14.0, 0.5)]
    return mkscene(name, P, A, D, B, L, {"night": BG["night"]}, {"night": AMB["night"]}, **kw)


def reliquary_g1():   # Gilded Gate
    return room("reliquary_g1", [("reliquary_door", (0, 0, -5.8)), ("angel_statue", (-2.8, 0, -4.4)), ("angel_statue", (2.8, 0, -4.4))],
                [("as_enemies", "light_wraith", "down", "idle", 0, (-1.6, 0, 0.6)), ("as_enemies", "light_wraith", "left", "idle", 2, (2.2, 0, 1.4))],
                [pool(0, -5.0, 2, 2, "pool_cold"), ("rune_pulse", (0, -4.6), 1, 2)], [], [((0, 2.8, -5.0), CF, 7.0, 0.8)])


def reliquary_g2():   # Hall of Statues
    st = [("angel_statue", (x, 0, z)) for x in (-2.4, 2.4) for z in (-4.0, -1.0, 2.0)]
    return room("reliquary_g2", st, [("as_enemies", "gilded_inquisitor", "down", "idle", 0, (0.0, 0, -2.4)), ("as_enemies", "light_wraith", "down", "idle", 1, (-4.2, 0, 1.6))],
                [pool(-2.4, -4.0, 1, 1, "pool_violet"), pool(2.4, -1.0, 4, 1, "pool_violet")], [("light_bolt", (1.6, 1.2, -1.8), 2)], [((0, 2.0, -2.0), VIO, 7.0, 0.6)], ledge_x=4.4, ledge_z=-4.4)


def reliquary_g3():   # Violet Glass
    return room("reliquary_g3", [("temple_window", (x, 0, -6.6)) for x in (-3.6, 0, 3.6)] + [("temple_window", (-6.6, 0, -1.0), PI / 2)],
                [("as_enemies", "light_wraith", "down", "idle", 2, (-0.6, 0, 1.0))],
                [pool(-3.6, -6.0, 0, 2, "pool_violet"), pool(0, -6.0, 3, 2, "pool_violet"), pool(3.6, -6.0, 5, 2, "pool_violet"), pool(-6.0, -1.0, 2, 1, "pool_violet")],
                [("neon_fireflies_violet", (0, 0.6, -2.0), 2), ("glow_orb_violet", (-1.0, 2.0, 0.0), 3)], [((-3.6, 2.0, -5.8), VIO, 7.0, 0.8), ((3.6, 2.0, -5.8), VIO, 7.0, 0.8)], lscale=0.4)


def reliquary_g4():   # Storm Gallery
    sp = [("storm_pillar", (x, 0, z)) for (x, z) in ((-2.6, -3.0), (2.6, -3.0), (-2.6, 1.0), (2.6, 1.0))]
    return room("reliquary_g4", sp, [("boss_sentinel", "sentinelprime", "down", "idle", 1, (0.0, 0, -0.6), "sprite")],
                [pool(x, z, i, 1, "pool_cold") for i, (x, z) in enumerate(((-2.6, -3.0), (2.6, -3.0), (-2.6, 1.0), (2.6, 1.0)))] + [("strike_warning", (-3.6, 3.0), 3, 2), ("as_shadow", (0, -0.6), 0, 3)],
                [("chain_lightning", (0, 4.6, -3.0), 2), ("core_pulse", (0, 4.4, -0.4), 1), ("strike_bolt", (-3.6, 0.0, 3.0), 2)], [((0, 4.8, -1.0), CF, 9.0, 0.9)],
                size=7, ledge_x=-4.6, ledge_z=-5.0, reach=16.5, reach_z=-0.6, lscale=0.55)


def reliquary_g5():   # Throne of Trials
    D = [("tile_flash", (x, z), (i * 3) % 4, 1) for i, (x, z) in enumerate(((-2, -2), (0, 0), (2, -2), (-2, 2), (2, 2)))]
    return room("reliquary_g5", [("high_seat", (0, 0, -5.0))], [("as_elites", "severin", "down", "idle", 0, (0.0, 0, -2.6))],
                D + [pool(0, -5.0, 1, 2), ("beam_ring", (0, -2.6), 3, 2), ("as_shadow", (0, -2.6), 0, 1)], [], [((0, 2.0, -4.4), WARM, 7.0, 0.8)], ledge_x=4.4, ledge_z=-4.4)


def reliquary_g6():   # Mirror of the Dawn
    return room("reliquary_g6", [("gold_mirror", (x, 0, -6.4)) for x in (-3.0, 0, 3.0)],
                [("as_folk", "priestess", "up", "idle", 1, (0.0, 0, -3.6)), ("as_enemies", "light_wraith", "down", "idle", 0, (-3.2, 0, -1.0))],
                [pool(0, -5.8, 0, 2, "pool_cold"), ("rime_tell", (0, -6.0), 2, 2)], [("glow_orb_blue", (2.6, 2.0, -2.0), 1)], [((0, 1.8, -5.6), CF, 8.0, 0.8)])


def reliquary_g7():   # Rune Bridge
    return room("reliquary_g7", [("as_rune_bridge", (0, 0.0, z)) for z in (-4.0, -2.0, 0.0, 2.0)],
                [("as_enemies", "storm_centaur", "left", "idle", 1, (4.2, 0, -2.4))], [pool(0, -3.0, 0, 2), ("rune_pulse", (0, -1.0), 1, 2), pool(0, 1.0, 3, 2, "pool_cold")],
                [("glow_orb_blue", (0, 1.8, -2.0), 3), ("gold_dust", (0, 0.4, -2.0), 5)], [((0, 1.0, -2.0), WARM, 8.0, 0.8)],
                void=(-2.0, 2.0, -6.0, 2.0), ledge_x=-4.6, ledge_z=3.0, lscale=0.6)


def reliquary_g8():   # Waystone Ossuary (safe room)
    return room("reliquary_g8", [("urn_shelf", (-3.0, 0, -6.2)), ("urn_shelf", (3.0, 0, -6.2)), ("lore_tablet", (-5.8, 0, -1.0), PI / 2), ("lore_tablet", (-5.8, 0, 1.6), PI / 2),
                                 ("as_waystone", (3.6, 0, 0.6)), ("marble_spring", (4.8, 0, -3.4))],
                [("as_folk", "as_guide", "down", "idle", 0, (-1.2, 0, -2.8))],
                [pool(3.6, 0.6, 2, 2, "pool_cold"), ("rune_pulse", (3.6, 0.6), 2, 2), pool(-3.0, -5.6, 1, 2), pool(3.0, -5.6, 4, 2), pool(4.8, -3.4, 0, 2)],
                [("spring_bubbles", (4.8, 0.3, -3.4), 2)], [((3.6, 1.2, 0.6), CF, 6.0, 0.7), ((0, 2.0, -5.4), WARM, 8.0, 0.8)], ledge_x=-4.4, ledge_z=4.2 - 8.4, rimed=False)


def reliquary_g9():   # Sunless Crypt (Aurelion)
    lamps = [("rimed_lamp", (x, 0, z)) for (x, z) in ((-5.0, -2.0), (5.0, -2.0), (-5.0, 2.4), (5.0, 2.4))]
    return room("reliquary_g9", [("crypt_throne", (0, 0, -5.2))] + lamps, [("boss_aurelion", "aurelion", "down", "idle", 1, (0.0, 0, -1.4), "sprite")],
                [pool(0, -5.2, 1, 2, "pool_red"), pool(-5.0, -2.0, 0, 1, "pool_cold"), pool(5.0, -2.0, 3, 1, "pool_cold"), ("beam_ring", (2.6, 1.6), 3, 2), ("as_shadow", (0, -1.4), 0, 3)],
                [("dawn_flame", (0, 4.5, -6.9), 2), ("light_drain", (3.0, 2.6, -1.8), 3), ("gold_dust", (-2.0, 1.2, 0.0), 4)],
                [((0, 4.8, -6.6), WARM, 9.0, 1.0), ((0, 2.0, -1.0), RED, 7.0, 0.5), ((-5, 2.9, -2), CF, 5.0, 0.6)], size=7, ledge_x=-4.6, ledge_z=-5.6, reach=18.5, reach_z=-1.4, lscale=0.55)
