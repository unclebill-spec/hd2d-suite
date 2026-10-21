"""Helheim scene layouts per story/helheim.md 2.1-2.5 + 7. World metres, +z toward camera, hero faces -z.
Every area / Ossuary room: mist_ledge pair (3.1 x 2.1 m, top 1.34) + ONE mist_stair centred on the front face (stair centre z = ledge z + 2.75).
Clearance: props, fx and spawns >= 1 m from ledge edges (ledge braziers stand on the ground at x = cx +- 4.4); stair footprint +1 m kept clear."""
import math
PI = math.pi
CF, VIO, LIL, RED, ROSE, MOON = "#3fb8ff", "#a45cf0", "#d6b8ff", "#e8321e", "#e8a8c8", "#b8b0ff"
BG = {"night": (16, 14, 30), "day": (150, 146, 176)}
AK = {("helheim", "night"): 1.5, ("helheim", "day"): 1.2, ("hh_shore", "night"): 2.0, ("hh_archive", "night"): 1.7, ("ossuary_o4", "night"): 1.15, ("ossuary_o7", "night"): 1.1, ("ossuary_o1", "night"): 1.05}
AMB = {"night": (0.25, 0.23, 0.33), "day": (0.92, 0.90, 0.98)}


def grid(name, x0, x1, z0, z1, step=2.0, void=None):
    out = []; x = x0
    while x <= x1 + 1e-6:
        z = z0
        while z <= z1 + 1e-6:
            if not (void and void[0] <= x <= void[1] and void[2] <= z <= void[3]):
                out.append((name, (x, 0, z)))
            z += step
        x += step
    return out


def terrace(cx, zb, braz=True):
    P = [("mist_ledge", (cx - 1.55, 0, zb)), ("mist_ledge", (cx + 1.55, 0, zb)), ("mist_stair", (cx, 0, zb + 2.75))]
    D, B, L = [], [], []
    if braz:
        for sx in (-1, 1):
            P.append(("coldfire_brazier", (cx + sx * 4.4, 0, zb)))
            D.append(("pool_coldfire", (cx + sx * 4.4, zb), 1 + sx, 1)); B.append(("cold_flame", (cx + sx * 4.4, 1.3, zb), 2 + sx)); L.append(((cx + sx * 4.4, 1.6, zb), CF, 6.0, 0.8))
    return P, D, B, L


def pool(x, z, k, sc=1, n="pool_coldfire"):
    return (n, (x, z), k, sc)


def mk(name, P, A, D, B, L, modes=("night",), **kw):
    kw.setdefault("lscale", 0.7)
    P, A, D, B, L = clear_fix(P, A, D, B, L)
    return dict(pieces=P, actors=A, decals=D, bills=B, extra_lights=L, bg={m: BG[m] for m in modes}, amb={m: tuple(c * AK.get((name, m), 1.0) for c in AMB[m]) for m in modes}, name=name, **kw)


FIXED = {"mist_ledge", "mist_stair", "gloam_floor", "ossuary_floor", "pebble_shore", "black_lake", "ossuary_wall", "archive_shelf", "bone_niches"}


def _rects(P):
    L = [(p[1][0] - 1.55, p[1][2] - 1.05, p[1][0] + 1.55, p[1][2] + 1.05) for p in P if p[0] == "mist_ledge"]
    L += [(p[1][0] - 1.3, p[1][2] - 1.75, p[1][0] + 1.3, p[1][2] + 1.75) for p in P if p[0] == "mist_stair"]
    return L


def _d(r, x, z):
    return math.hypot(max(r[0] - x, 0, x - r[2]), max(r[1] - z, 0, z - r[3]))


def clear_fix(P, A, D, B, L):
    """keep props / spawns / fx >= 1.05 m from every ledge edge and stair footprint: anything too close is moved to the nearest clear spot;
    items sharing a spot (a lamp, its pool, flame and light) move together"""
    R = _rects(P); memo = {}
    fl = [p[1] for p in P if p[0] in ("gloam_floor", "ossuary_floor", "pebble_shore")]
    bx = max(abs(f[0]) for f in fl) + 0.4; bz0 = min(f[2] for f in fl) - 0.4; bz1 = max(f[2] for f in fl) + 0.4
    def mv(x, z):
        key = (round(x, 2), round(z, 2))
        if key in memo:
            return memo[key]
        if all(_d(r, x, z) >= 1.05 for r in R):
            memo[key] = (x, z); return memo[key]
        best = None
        for rad in [k * 0.25 for k in range(1, 40)]:
            for a in range(16):
                nx, nz = x + math.cos(a * PI / 8) * rad, z + math.sin(a * PI / 8) * rad
                if abs(nx) <= bx and bz0 <= nz <= bz1 and all(_d(r, nx, nz) >= 1.05 for r in R):
                    best = (round(nx, 2), round(nz, 2)); break
            if best:
                break
        memo[key] = best or (x, z); return memo[key]
    P2 = []
    for p in P:
        if p[0] in FIXED or p[0] in ("lantern_bridge", "hels_arch", "hels_hall", "last_hearth_inn", "crooked_house", "ossuary_door", "pale_throne", "jetty"):
            P2.append(p); continue
        x, y, z = p[1]; nx, nz = mv(x, z); P2.append((p[0], (nx, y, nz)) + tuple(p[2:]))
    A2 = []
    for a in A:
        x, y, z = a[5]; nx, nz = mv(x, z); A2.append(a[:5] + ((nx, y, nz),) + a[6:])
    D2 = [(d[0], mv(*d[1])) + tuple(d[2:]) for d in D]
    B2 = []
    for b in B:
        x, y, z = b[1]; nx, nz = mv(x, z); B2.append((b[0], (nx, y, nz)) + tuple(b[2:]))
    L2 = []
    for l in L:
        x, y, z = l[0]; nx, nz = mv(x, z) if (round(x, 2), round(z, 2)) in memo else (x, z); L2.append(((nx, y, nz),) + tuple(l[1:]))
    return P2, A2, D2, B2, L2


def lamps(pts):
    P = [("cold_fire_lamp", (x, 0, z)) for (x, z) in pts]
    return P, [pool(x, z, i % 6) for i, (x, z) in enumerate(pts)], [((x, 2.6, z), CF, 5.0, 0.7) for (x, z) in pts]


# ---------------------------------------------------------------- `helheim`: Gloamhaven (town), 24 x 22
def helheim():
    lake = [(x, z) for x in (-3, -1, 1, 3) for z in (-1, 1, 3)]
    P = grid("gloam_floor", -11, 11, -9, 11, void=(-4, 4, -1.5, 3.5)) + [("black_lake", (x, 0, z)) for (x, z) in lake]
    P += [("lantern_bridge", (0, 0, 1.0), PI / 2), ("hels_arch", (0, 0, 10.6)), ("hels_hall", (0, 0, -10.4)), ("last_hearth_inn", (-7.5, 0, -2.0), PI / 2),
          ("crooked_house", (8.0, 0, -7.6)), ("crooked_house", (-6.6, 0, 7.4), 0.1), ("jetty", (9.0, 0, -3.0), PI / 2), ("archive_door", (-10.0, 0, -9.0)),
          ("bubbly_spring", (-11.0, 0, 4.0), PI / 2), ("willow_orb", (-9.6, 0, 9.4)), ("willow_orb", (7.4, 0, 5.4)), ("willow_orb", (7.0, 0, -0.8))]
    tp, td, tb, tl = terrace(0, -7.0)
    lp, ld, ll = lamps([(-2.2, 6.5), (2.2, 6.5), (-4.6, 4.8), (6.0, 2.8), (4.8, -3.4), (-4.4, -3.4)])
    P += tp + lp + [("glow_orb_chain", (-5.4, 0.2, -6.8)), ("lantern_boat", (-3.6, -0.05, 2.6)), ("lantern_boat", (4.2, -0.05, -0.6), 0.6)]
    A = [("hh_folk", "ferryman", "left", "idle", 0, (8.2, 0, -1.0)), ("hh_folk", "innghost", "right", "idle", 1, (-4.6, 0, -0.6)), ("hh_folk", "childghost", "down", "idle", 2, (-8.4, 0, 5.4)),
         ("hh_folk", "gloam_folk", "right", "walk", 1, (-4.6, 0, -6.6)), ("hh_folk", "bakerghost", "down", "idle", 0, (-4.4, 0, -1.8)), ("hh_folk", "hel", "down", "idle", 0, (6.4, 0, -5.4)),
         ("hh_enemies", "shade", "down", "idle", 1, (1.8, 0, 6.5)), ("hh_inkling", "inkling", "up", "idle", 1, (1.0, 0, 8.6)), ("HERO", "wildcaller", "up", "idle", 0, (0.0, 0, 8.6))]
    D = td + ld + [("lake_shimmer", (x, z), i % 6, 1, -0.08) for i, (x, z) in enumerate(lake[::2])] + \
        [pool(-4.8, -2.0, 2, 2, "pool_window"), pool(8.0, -5.6, 1, 1, "pool_window"), pool(-6.6, 9.2, 3, 1, "pool_window"), pool(0, -8.6, 4, 2, "pool_window"),
         pool(-11.0, 4.0, 1, 2, "pool_window"), pool(-9.6, 9.4, 2, 1, "pool_lilac"), pool(7.4, 5.4, 4, 1, "pool_lilac"), pool(7.0, -0.8, 0, 1, "pool_lilac"),
         ("spirit_rose_mist", (0, 9.6), 1, 2), ("gloam_fog", (-6.0, 3.0), 0, 2), ("gloam_fog", (6.0, 7.6), 3, 2)]
    B = tb + [("glow_orb_lilac", (-9.6, 1.8, 9.4), 0), ("glow_orb_lilac", (7.4, 1.8, 5.4), 2), ("glow_orb_lilac", (7.0, 1.8, -0.8), 4), ("soul_motes", (-1.0, 0.8, -3.6), 2),
              ("soul_light", (5.0, 1.0, 7.0), 3), ("spring_fizz", (-11.0, 0.3, 4.0), 2), ("lantern_float", (-1.6, 0.0, 3.0), 1), ("violet_motes", (1.0, 0.4, 8.6), 2), ("hh_shadow", (0, 0, 0), 0)][:-1]
    L = tl + ll + [((-5.0, 1.9, -2.0), VIO, 4.0, 0.9), ((8.0, 1.9, -5.6), VIO, 3.0, 0.9), ((-6.6, 1.9, 9.2), VIO, 3.0, 0.9), ((0, 2.2, -8.6), VIO, 5.0, 0.9),
                   ((0, 2.0, 1.0), VIO, 7.0, 0.6), ((0, 2.0, 9.8), ROSE, 6.0, 0.6), ((-11.0, 0.8, 4.0), VIO, 4.0, 0.7), ((0, 6.0, 3.0), MOON, 16.0, 0.45)]
    return mk("helheim", P, A, D, B, L, ("night", "day"), lscale=0.9)


# ---------------------------------------------------------------- `hh_shore`: The Lantern Shore, 16 x 16
def hh_shore():
    lake = [(x, z) for x in (-7, -5, -3, -1, 1, 3, 5, 7) for z in (-7, -5, -3)]
    P = grid("pebble_shore", -7, 7, -1, 7) + [("black_lake", (x, 0, z)) for (x, z) in lake] + [("jetty", (0, 0, -2.0))]
    P += [("willow_orb", (-5.8, 0, 1.4)), ("willow_orb", (5.8, 0, 3.6)), ("lantern_boat", (-2.2, -0.05, -3.4), 0.3), ("lantern_boat", (2.6, -0.05, -5.0), -0.4),
          ("reeds", (-6.2, 0, -0.6)), ("bubbly_spring", (-6.0, 0, 5.4), PI / 2)]
    tp, td, tb, tl = terrace(3.4, 5.0, braz=False)
    lp, ld, ll = lamps([(-2.6, 1.4), (6.4, 0.4)])
    P += tp + lp
    A = [("hh_folk", "eira_spirit", "left", "idle", 0, (4.0, 0, -0.4)), ("hh_folk", "ferryman", "down", "idle", 1, (-1.6, 0, 0.6)), ("hh_folk", "childghost", "up", "idle", 0, (-3.2, 0, 2.6)),
         ("hh_inkling", "inkling", "up", "idle", 2, (-0.6, 0, 6.0)), ("HERO", "wildcaller", "up", "idle", 0, (0.4, 0, 6.0))]
    D = td + ld + [("lake_shimmer", (x, z), i % 6, 1, -0.08) for i, (x, z) in enumerate(lake[::2])] + \
        [pool(-5.8, 1.4, 1, 1, "pool_lilac"), pool(5.8, 3.6, 3, 1, "pool_lilac"), pool(-6.0, 5.4, 2, 2, "pool_window"), ("gloam_fog", (0, 2.0), 2, 2)]
    B = tb + [("eira_outline", (4.0, 0.0, -0.4), 2), ("glow_orb_lilac", (-5.8, 1.8, 1.4), 1), ("glow_orb_lilac", (5.8, 1.8, 3.6), 4), ("lantern_float", (-3.6, 0.0, -4.0), 2),
              ("lantern_float", (3.0, 0.0, -6.0), 5), ("soul_light", (-6.0, 0.8, -0.2), 1), ("spring_fizz", (-6.0, 0.3, 5.4), 3)]
    L = tl + ll + [((4.0, 1.2, -0.4), VIO, 4.0, 0.7), ((-5.8, 1.8, 1.4), LIL, 4.0, 0.8), ((5.8, 1.8, 3.6), LIL, 4.0, 0.8), ((0, 1.6, -3.8), CF, 4.0, 0.7),
                   ((-6.0, 0.8, 5.4), VIO, 4.0, 0.7), ((0, 6.0, 0.0), MOON, 14.0, 0.5)]
    return mk("hh_shore", P, A, D, B, L, lscale=0.95)


# ---------------------------------------------------------------- `hh_archive`: The Quiet Archive, 14 x 16
def hh_archive():
    P = grid("gloam_floor", -6, 6, -7, 7) + [("archive_shelf", (x, 0, -9.0)) for x in (-5, -3, 3, 5)] + [("archive_shelf", (-7.0, 0, z), PI / 2) for z in (-5, -1, 3)] + \
        [("archive_shelf", (7.0, 0, z), -PI / 2) for z in (-5, -1, 3)]
    P += [("ossuary_door", (0, 0, -8.0)), ("ledger_lectern", (0, 0, -4.0)), ("quillon_desk", (-5.0, 0, -3.0)),
          ("floating_candles", (-2.0, 0, 0.0)), ("floating_candles", (2.4, 0, 2.6))]
    tp, td, tb, tl = terrace(2.2, 0.2, braz=False)
    P += tp
    A = [("hh_folk", "archivist_hh", "down", "idle", 0, (-4.6, 0, -1.8)), ("hh_folk", "sailorghost", "left", "idle", 1, (-1.4, 0, 3.6)),
         ("HERO", "wildcaller", "up", "idle", 0, (0.0, 0, 6.0))]
    D = td + [pool(0, -4.0, 1, 2, "pool_window"), pool(0, -7.0, 3, 2, "pool_window"), pool(-2.0, 0.0, 2), pool(2.4, 2.6, 4), pool(-4.6, -3.0, 0), ("soul_motes", (0, -4.0), 0, 1)][:-1]
    B = tb + [("soul_motes", (0, 0.8, -4.0), 1), ("cold_flame", (-2.0, 2.6, 0.0), 0), ("cold_flame", (2.4, 2.6, 2.6), 3), ("soul_light", (5.0, 1.0, -6.0), 2)]
    L = tl + [((0, 1.6, -4.0), VIO, 5.0, 0.9), ((0, 2.6, -7.4), VIO, 5.0, 0.8), ((-2.0, 2.8, 0.0), CF, 5.0, 0.8), ((2.4, 2.8, 2.6), CF, 5.0, 0.8), ((-4.0, 1.3, -3.0), CF, 3.0, 0.7),
                   ((0, 6.0, 1.0), MOON, 12.0, 0.5)]
    return mk("hh_archive", P, A, D, B, L, lscale=0.95)


# ---------------------------------------------------------------- the Ossuary of Whispers O1..O9
def room(name, extra, A, D, B, L, lx=-4.4, lz=-3.6, size=6, void=None, wall="ossuary_wall", **kw):
    P = grid("ossuary_floor", -size, size, -size, size, void=void)
    P += [(wall, (x, 0, -size - 0.9)) for x in range(-size, size + 1, 2)] + [(wall, (-size - 0.9, 0, z), PI / 2) for z in range(-size + 2, size, 2)]
    tp, td, tb, tl = terrace(lx, lz, braz=False)
    lp, ld, ll = lamps([(4.6, 4.4), (-4.6, 4.4)])
    P += tp + lp + extra
    A = A + [("HERO", "wildcaller", "up", "idle", 0, (0.0, 0, 5.0))]
    D = D + td + ld + [("gloam_fog", (-1.0, 2.0), 3, 2)]
    B = B + tb + [("soul_motes", (-2.0, 0.8, 1.0), 4)]
    L = L + tl + ll + [((0, 5.0, 2.0), MOON, 14.0, 0.5)]
    return mk(name, P, A, D, B, L, **kw)


def ossuary_o1():   # The Bone Door
    return room("ossuary_o1", [("ossuary_door", (0, 0, -5.8))] + [("cold_fire_lamp", (x, 0, -3.4)) for x in (-2.6, 2.6)],
                [("hh_enemies", "shade", "down", "idle", 0, (-1.6, 0, 0.6)), ("hh_enemies", "shade", "left", "idle", 2, (0.8, 0, -0.6))],
                [pool(0, -5.0, 2, 2, "pool_window"), pool(-2.6, -3.4, 1), pool(2.6, -3.4, 4)], [], [((0, 2.8, -5.0), VIO, 7.0, 0.8), ((-2.6, 2.6, -3.4), CF, 5.0, 0.7), ((2.6, 2.6, -3.4), CF, 5.0, 0.7)],
                lx=4.0, lz=-1.6)


def ossuary_o2():   # The Whispering Hall
    return room("ossuary_o2", [("bone_niches", (x, 0, -6.6)) for x in (-4, -2, 0, 2, 4)] + [("bubbly_spring", (5.0, 0, -3.6), -PI / 2)],
                [("hh_enemies", "skeleton_line", "down", "walk", i, (-2.4 + i * 1.2, 0, -2.6)) for i in range(4)],
                [pool(5.0, -3.6, 1, 2, "pool_window"), ("gloam_fog", (2.0, -4.6), 1, 2)], [("spring_fizz", (5.0, 0.3, -3.6), 2), ("soul_light", (3.6, 0.8, -1.6), 1)],
                [((5.0, 0.8, -3.6), VIO, 4.0, 0.7), ((0, 2.4, -5.6), VIO, 7.0, 0.6)], lx=-3.6, lz=1.2)


def ossuary_o3():   # The Lantern Graves
    graves = [(-3.0, -4.0), (-1.0, -4.6), (1.0, -4.0), (3.0, -4.6), (-2.0, -1.6), (2.0, -1.6)]
    return room("ossuary_o3", [("grave_lantern_post", (x, 0, z)) for (x, z) in graves] + [("soul_glass", (4.4, 0, -1.0)), ("name_cage", (-4.4, 0, -1.0))],
                [("hh_enemies", "grave_lantern", "down", "walk", 1, (0.0, 0, -0.4)), ("hh_enemies", "grave_lantern", "left", "idle", 2, (2.6, 0, 1.4))],
                [pool(x, z, i) for i, (x, z) in enumerate(graves)] + [pool(4.4, -1.0, 2, 1, "pool_lilac"), pool(-4.4, -1.0, 3, 1, "pool_window")],
                [("cold_flame", (x, 1.4, z), i) for i, (x, z) in enumerate(graves[:3])], [((-4.4, 1.0, -1.0), VIO, 4.0, 0.8)], lx=3.0, lz=1.8, lscale=0.45)


def ossuary_o4():   # The Garnet Gallery
    return room("ossuary_o4", [("heart_slot", (x, 0, -4.4)) for x in (-3.0, 0.0, 3.0)] + [("soul_glass", (4.6, 0, -1.6))],
                [("hh_enemies", "garnet_golem", "down", "idle", 0, (-2.0, 0, -1.0)), ("hh_enemies", "bone_elemental", "left", "idle", 1, (2.6, 0, 0.6))],
                [pool(x, -4.4, i, 1, "pool_red") for i, x in enumerate((-3.0, 0.0, 3.0))] + [pool(4.6, -1.6, 1, 1, "pool_lilac")], [],
                [((0, 1.0, -4.4), RED, 6.0, 0.5), ((0, 2.4, -2.0), VIO, 6.0, 0.6)], lx=-3.6, lz=2.0)


def ossuary_o5():   # Vesperin's Salon
    return room("ossuary_o5", [("salon_seat", (0, 0, -5.0)), ("name_cage", (4.2, 0, -4.4))],
                [("hh_elites", "vesperin", "down", "idle", 0, (0.0, 0, -2.0))],
                [pool(0, -5.0, 1, 2, "pool_red"), pool(4.2, -4.4, 3, 1, "pool_window"), ("hunt_ring", (1.6, 0.6), 3, 2), ("hh_shadow", (0, -2.0), 0, 2)],
                [("bat_dash", (-3.6, 2.0, -1.0), 2)], [((0, 2.0, -4.4), RED, 7.0, 0.6), ((4.2, 1.0, -4.4), VIO, 4.0, 0.8)], lx=4.0, lz=1.6, reach=8.0, reach_z=-2.0)


def ossuary_o6():   # The Choir Loft
    return room("ossuary_o6", [("rhythm_door", (0, 0, -6.0))] + [("bone_niches", (x, 0, -6.6)) for x in (-4, 4)],
                [("hh_elites", "hollowchoir", "down", "idle", 1, (-1.0, 0, -2.2))],
                [pool(0, -5.4, 2, 2, "pool_window"), ("dirge_aura", (-1.0, -2.2), 1, 3)], [("soul_motes", (2.0, 1.2, -3.0), 3)], [((0, 2.6, -5.2), VIO, 7.0, 0.8)], lx=3.6, lz=1.6, reach=8.0, reach_z=-2.2)


def ossuary_o7():   # The Sleeping Liches
    return room("ossuary_o7", [("lich_bier", (-2.4, 0, -3.6)), ("lich_bier", (2.4, 0, -3.6)), ("soul_glass", (0, 0, -5.4)), ("name_cage", (4.6, 0, -0.6))],
                [("hh_enemies", "lich", "down", "idle", 0, (-2.4, 0.88, -3.6)), ("hh_enemies", "lich", "down", "idle", 2, (2.4, 0.88, -3.6))],
                [pool(-2.4, -3.6, 1, 1, "pool_window"), pool(2.4, -3.6, 3, 1, "pool_window"), pool(0, -5.4, 2, 1, "pool_lilac"), pool(4.6, -0.6, 4, 1, "pool_window")], [],
                [((0, 1.6, -4.0), VIO, 6.0, 0.6), ((4.6, 1.0, -0.6), VIO, 4.0, 0.8)], lx=-3.8, lz=1.8, lscale=0.45)


def ossuary_o8():   # Mordrath's Vault (safe)
    return room("ossuary_o8", [("hh_waystone", (3.6, 0, 0.0)), ("name_cage", (0, 0, -4.4)), ("lore_tablet", (-5.8, 0, -2.0), PI / 2), ("lore_tablet", (-5.8, 0, 0.6), PI / 2),
                               ("bubbly_spring", (4.8, 0, -4.0))],
                [], [pool(3.6, 0.0, 2, 2, "pool_window"), pool(0, -4.4, 1, 2, "pool_window"), pool(4.8, -4.0, 0, 2, "pool_window")], [("name_moths", (0, 1.4, -4.4), 2), ("spring_fizz", (4.8, 0.3, -4.0), 3)],
                [((3.6, 1.2, 0.0), VIO, 5.0, 0.7), ((0, 1.2, -4.4), VIO, 5.0, 0.9)], lx=-3.6, lz=3.2)


def ossuary_o9():   # The Pale Throne
    anchors = [("chain_anchor", (-6.6, 0, z), PI / 2) for z in (-4.0, 0.0)] + [("chain_anchor", (x, 0, -7.4)) for x in (-3.0, 3.0)]
    return room("ossuary_o9", [("pale_throne", (0, 0, -5.4))] + anchors, [("boss_mordrath", "mordrath", "down", "idle", 1, (0.0, 0, -1.4), "sprite")],
                [pool(0, -5.4, 1, 3, "pool_window"), ("glaive_arc", (0.0, -0.6), 3, 3), ("telegraph_line", (-5.6, -2.0), 1, 2), ("hh_shadow", (0, -1.4), 0, 3)],
                [("violet_smoke_wings", (0, 5.2, -1.6), 2), ("name_moths", (3.4, 1.0, 0.4), 3), ("soul_motes", (-3.0, 1.0, 0.0), 4)],
                [((0, 4.8, -6.0), VIO, 9.0, 1.0), ((0, 7.8, -1.4), RED, 7.0, 0.6)], size=7, lx=-4.4, lz=3.0, reach=18.5, reach_z=-1.4, lscale=0.6)


SCENES = [("helheim", helheim, ("night", "day")), ("hh_shore", hh_shore, ("night",)), ("hh_archive", hh_archive, ("night",))] + \
         [(f"ossuary_o{i}", globals()[f"ossuary_o{i}"], ("night",)) for i in range(1, 10)]
