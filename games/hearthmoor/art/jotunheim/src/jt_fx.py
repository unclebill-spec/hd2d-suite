"""Jotunheim gamefx (48 px cells, hd2d portal format via hmart.write_fx). Neon on fx only (flagged in README)."""
import math, random
import jt_common as C
H = C.H
CELL = 48
H.ALLC.update({"jt_teal": "#2fd0d0", "jt_teal_hi": "#a8fff0", "jt_teal_lo": "#16807f", "jt_aur_g": "#3fe0a0", "jt_aur_g_hi": "#b8ffe0", "jt_aur_g_lo": "#14a070",
               "jt_rune": "#7fd4ff", "jt_orb": "#9fe8ff", "jt_snow": "#eef6ff", "jt_fog": "#6ad8e8", "jt_fog_lo": "#2a8aa8"})
NB = ("neon_blue_hi", "neon_blue", "neon_blue_lo")
NG = ("neon_green_hi", "neon_green", "neon_green_lo")
NV = ("neon_violet_hi", "neon_violet", "neon_violet_lo")
TE = ("jt_teal_hi", "jt_teal", "jt_teal_lo")
AG = ("jt_aur_g_hi", "jt_aur_g", "jt_aur_g_lo")


def fireflies(cols, seed, n=8):
    def f():
        r = random.Random(seed); pts = [(r.uniform(6, 42), r.uniform(6, 42), r.uniform(0, 6.28)) for _ in range(n)]
        out = []
        for k in range(8):
            F = H.Fx(CELL)
            for j, (x, y, ph) in enumerate(pts):
                a = k / 8 * math.tau + ph
                X, Y = x + math.cos(a) * 3, y + math.sin(a * 2) * 2
                if (k + j) % 3:
                    F.set(X, Y, cols[0]); F.set(X + 1, Y, cols[1]); F.set(X, Y + 1, cols[2])
                else:
                    F.set(X, Y, cols[2])
            out.append(F)
        return out
    return f


def sparkles():
    r = random.Random(21); pts = [(r.uniform(5, 43), r.uniform(5, 43), r.randrange(8)) for _ in range(9)]
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        for (x, y, ph) in pts:
            t = (k + ph) % 8
            if t < 2:
                F.star(x, y, 2, "white", "neon_blue_hi", "neon_blue")
            elif t < 4:
                F.star(x, y, 1, "white", "jt_snow", "neon_blue_hi")
            elif t < 6:
                F.set(x, y, "neon_blue_hi")
        out.append(F)
    return out


def flame():
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        cx = 23.5
        for y in range(6, 44):
            t = (44 - y) / 38
            w = max(0, 6.5 * math.sin(math.pi * min(1, t * 1.15)) ** 0.7 * (1 - t * .55)) * (1 + .12 * math.sin(k * 1.3 + y * .3))
            sway = math.sin(y * .22 + k * .9) * 2.4 * t
            for dx in range(-int(w), int(w) + 1):
                d = abs(dx) / max(w, 1)
                F.set(cx + dx + sway, y, "white" if (d < .25 and .15 < t < .6) else "neon_blue_hi" if d < .5 else "neon_blue" if d < .8 else "neon_blue_lo")
        for j in range(3):
            F.set(cx + math.sin(k + j * 2) * 8, 4 + (k * 3 + j * 7) % 16, "neon_blue_hi")
        out.append(F)
    return out


def aurora():
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        for x in range(CELL):
            base = 18 + math.sin(x * .17 + k * .78) * 7
            hgt = 15 + math.sin(x * .3 - k * .5) * 4
            for y in range(int(base - hgt), int(base + 4)):
                t = (y - (base - hgt)) / (hgt + 4)
                if (x + y + k) % 2 == 0 or t > .55:
                    g = x / CELL
                    c = AG if g < .55 else NV
                    F.set(x, y, c[0] if t > .75 else c[1] if t > .35 else c[2])
        out.append(F)
    return out


def frog():
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        hop = [0, 0, -3, -5, -4, -2, 0, 0][k]
        cx, cy = 24, 36 + hop
        F.disk(cx, cy, 5, ["jt_teal_lo", "jt_teal_lo", "jt_teal_lo"], sq=0.75)           # body (dark teal)
        for dx in (-1, 0, 1):
            F.set(cx + dx * 2, cy - 2, "jt_teal")
        F.disk(cx + 4, cy - 2, 2.2, ["jt_teal", "jt_teal"], sq=1)
        for (dx, dy, c) in ((-3, 0, "neon_green"), (0, 1, "neon_green_hi"), (3, -1, "neon_green"), (-1, -2, "neon_green_hi"), (2, 2, "neon_green"), (5, -3, "white")):
            F.set(cx + dx, cy + dy, c)                                                     # glowing spots, eye
        F.set(cx + 6, cy - 3, "ink") if "ink" in H.ALLC and k % 7 == 6 else None
        for (lx, ly) in ((-4, 4), (4, 4)):
            F.set(cx + lx, cy + ly + (-hop // 3 if hop < -2 else 0), "jt_teal"); F.set(cx + lx + (1 if lx > 0 else -1), cy + ly + 1, "jt_teal_lo")
        if k in (2, 3, 4):
            F.set(cx + 8, cy + 3, "neon_green_hi")
        out.append(F)
    return out


def vines():
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        for sx, ln, ph in ((9, 38, 0.0), (19, 30, 1.3), (29, 40, 2.1), (39, 28, 0.6)):
            for y in range(0, ln):
                x = sx + math.sin(y * .22 + k * .78 + ph) * (1 + y * .05)
                F.set(x, y, "jt_teal_lo" if y % 3 else "jt_teal")
                if y % 6 == 3:
                    F.set(x + 1, y, "jt_teal"); F.set(x - 1, y + 1, "jt_teal_lo")
                if y % 9 == 5:
                    F.set(x + 1, y + 1, "neon_green_hi"); F.set(x + 2, y + 1, "neon_green")
            F.set(x, ln, "neon_green_hi"); F.set(x, ln + 1, "neon_green"); F.set(x, ln + 2, "jt_teal_hi")
        out.append(F)
    return out


def fog():
    r = random.Random(33)
    blobs = [(r.uniform(8, 40), r.uniform(10, 36), r.uniform(8, 14), r.uniform(0, 6.28)) for _ in range(6)]
    jit = [[r.random() for _ in range(CELL)] for _ in range(CELL)]
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        for y in range(CELL):
            for x in range(CELL):
                dens = 0
                for (bx, by, br, ph) in blobs:
                    X, Y = bx + math.cos(k / 8 * math.tau + ph) * 3, by + math.sin(k / 8 * math.tau * 2 + ph) * 1.5
                    d = math.hypot(x - X, (y - Y) * 1.6) / br
                    dens += max(0, 1 - d) ** 1.3
                if dens > .12 and ((x + y + k) % 2 == 0) and jit[y][x] < dens * .9:
                    F.set(x, y, "jt_fog" if dens > .6 else "jt_fog_lo" if dens > .3 else "jt_teal_lo")
        out.append(F)
    return out


def rune_pulse():
    out = []
    for k in range(6):
        F = H.Fx(CELL)
        a = [.5, .75, 1.0, .85, .65, .5][k]
        F.ring(23.5, 23.5, 16 * a + 2, 16 * a + 2, "jt_rune", dots=2)
        F.ring(23.5, 23.5, 10 * a, 10 * a, "neon_blue_hi", dots=3, start=k)
        for j in range(6):
            ang = j * math.tau / 6 + k * .1
            F.star(23.5 + math.cos(ang) * (13 * a + 3), 23.5 + math.sin(ang) * (13 * a + 3), 1, "white", "neon_blue_hi", "neon_blue")
        out.append(F)
    return out


def snow_puff():
    out = []
    for k in range(6):
        F = H.Fx(CELL)
        for j in range(7):
            ang = j * math.tau / 7 + .4
            rr = 3 + k * 2.2
            x, y = 24 + math.cos(ang) * rr, 38 + math.sin(ang) * rr * .5 - k * .8
            if k < 5:
                F.disk(x, y, 2.4 - k * .3, ["jt_snow", "jt_snow", "sky"])
        out.append(F)
    return out


FX = {
    "pool_cold": {"fn": lambda: H.pool_frames(NB, CELL, 6, "jt_cold", rmax=22), "fps": 4, "kind": "decal", "lift": 0.02, "pivot": [24, 24], "notes": "cold-blue pool under cold_brazier / rune stones / throne (x2-3 for Hrimgard)"},
    "pool_teal": {"fn": lambda: H.pool_frames(TE, CELL, 6, "jt_teal", rmax=22), "fps": 4, "kind": "decal", "lift": 0.03, "pivot": [24, 24], "notes": "bioluminescent teal pool over glow_ice_pool / ice_lake"},
    "pool_aurora": {"fn": lambda: H.pool_frames(AG, CELL, 6, "jt_aur", rmax=22), "fps": 3, "kind": "decal", "lift": 0.02, "pivot": [24, 24], "notes": "aurora-green pool on the snow (night)"},
    "pool_violet": {"fn": lambda: H.neon_pool_frames("violet", CELL, 6, rmax=20), "fps": 4, "kind": "decal", "lift": 0.02, "pivot": [24, 24], "notes": "violet pool, aurora spill"},
    "aurora_glow": {"fn": aurora, "fps": 4, "kind": "billboard", "lift": 5.0, "pivot": [24, 24], "notes": "green-to-violet aurora curtain, 8-frame ribbon, night sky layer (tile horizontally)"},
    "cold_flame": {"fn": flame, "fps": 10, "kind": "billboard", "lift": 0.1, "pivot": [24, 44], "light": {"color": "neon_blue", "intensity": 1.0, "range": 4.0, "pool": "pool_cold"}, "notes": "cold-fire flame over braziers (no heat)"},
    "ice_sparkles": {"fn": sparkles, "fps": 6, "kind": "billboard", "lift": 0.8, "pivot": [24, 47], "notes": "twinkling ice sparkles over snow, ice and crystals"},
    "neon_fireflies_blue": {"fn": fireflies(NB, 3), "fps": 6, "kind": "billboard", "lift": 0.8, "pivot": [24, 47], "notes": "cold-blue fireflies"},
    "neon_fireflies_green": {"fn": fireflies(NG, 5), "fps": 6, "kind": "billboard", "lift": 0.8, "pivot": [24, 47], "notes": "green wisps in the Rime Caves"},
    "neon_fireflies_violet": {"fn": fireflies(NV, 4), "fps": 6, "kind": "billboard", "lift": 0.8, "pivot": [24, 47], "notes": "violet wisps at the aurora"},
    "glow_frog": {"fn": frog, "fps": 6, "kind": "billboard", "lift": 0.0, "pivot": [24, 44], "notes": "glowing cave frog (hops by the pools; never gross)"},
    "glow_vines": {"fn": vines, "fps": 4, "kind": "billboard", "lift": 3.0, "pivot": [24, 0], "notes": "hanging glowing vines + icicle drip, hang from the cave ceiling (pivot at top)"},
    "glow_fog": {"fn": fog, "fps": 3, "kind": "decal", "lift": 0.05, "pivot": [24, 24], "notes": "surreal glowing ground fog (teal), drifting; one per 6-8 m, off stairs and spawns"},
    "rune_pulse": {"fn": rune_pulse, "fps": 2, "kind": "decal", "lift": 0.03, "pivot": [24, 24], "notes": "frost-rune ring pulse (every 3 s), brighter when the hero is near"},
    "snow_puff": {"fn": snow_puff, "fps": 8, "kind": "billboard", "lift": 0.0, "pivot": [24, 44], "loop": False, "notes": "Flurry's fx id snow_puff (hare hops / stops)"},
}
for _c in ("blue", "green", "violet"):
    FX[f"glow_orb_{_c}"] = {"fn": (lambda c=_c: H.glow_orb_frames(c, CELL)), "fps": 6, "kind": "billboard", "lift": 1.4, "pivot": [24, 33],
                            "light": {"color": f"neon_{_c}_hi", "intensity": 0.7, "range": 3.0, "pool": {"blue": "pool_cold", "green": "pool_aurora", "violet": "pool_violet"}[_c]},
                            "notes": "floating glow orb, hover 1.1-2.2 m"}
