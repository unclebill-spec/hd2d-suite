"""Verdant Heart gamefx (hd2d portal format). Two atlases:
  verdant_fx       48 px cells: water (stream flow, waterfall sheet + splash, heart-spring bubbles), light pools in five
                   neon colours, glow mist, neon fireflies (mixed + 5 single colours), glow orbs (5 colours), spore motes,
                   boss fx (blight aura, root eruption, spore burst, Regent cleansed, Greenheart aura, thorn lash).
  verdant_critters 24 px cells: glow frogs in four neon colours (idle throat-pulse + hop).
Glow = emissive pixels + small lights + dithered pools only (no bloom). Neon hexes on glow pixels only."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_lib"))
import hmart as H  # noqa: E402

CELL = 48
NEONS = {   # name: (core, hi, mid, lo)  - the five glow colours Bill loves
    "blue": ("white", "neon_blue_hi", "neon_blue", "neon_blue_lo"),
    "violet": ("white", "neon_violet_hi", "neon_violet", "neon_violet_lo"),
    "red": ("white", "neon_red_hi", "neon_red", "neon_red_lo"),
    "green": ("white", "neon_green_hi", "neon_green", "neon_green_lo"),
    "pink": ("white", "neon_pink_hi", "neon_pink", "neon_pink_lo"),
}


def h(*a):
    return H.rng(104, "vh", *a).random()


def pool(colour, frames=6, rmax=None, seed=None):
    c = NEONS[colour]
    return lambda: H.pool_frames((c[1], c[2], c[3]), CELL, frames, seed or f"pool_{colour}", rmax=rmax)


def heart_spring_pool():
    out = H.pool_frames(("cold_hi", "cold", "cold_lo"), CELL, 6, "hsp", rmax=21)
    for f, F in enumerate(out):
        for k in range(8):
            x, y = 10 + (k * 11 + f * 3) % 28, 17 + (k * 5) % 14
            if F.get(x, y):
                F.set(x, y, "white")
    return out


def heart_spring_bubbles():
    """bubbles rising and popping off the spring (white rims, cold-fire hearts), little sparkles at the pop"""
    out = []
    for f in range(6):
        F = H.Fx(CELL)
        for k in range(9):
            x0 = 12 + h("bx", k) * 24
            ph = (f / 6 + h("bp", k)) % 1
            y = 46 - ph * 22
            r = 1 + (k % 3 == 0)
            if ph > 0.85:
                F.star(x0, y, 1, "white", "cold_hi", "cold_hi")
            else:
                F.ring(x0, y, r, r, "white" if r == 1 else "cold_hi")
                F.set(x0, y, "cold")
        out.append(F)
    return out


def stream_flow():
    """decal for stream_straight (flow toward +z = down the cell): drifting white / cold glints and neon streaks,
    repeat-safe at the top / bottom edges so tiles chain"""
    out = []
    for f in range(8):
        F = H.Fx(CELL)
        for k in range(22):
            x = 10 + h("sx", k) * 28
            y = (h("sy", k) * 48 + f * 6) % 48
            ln = 2 + int(h("sl", k) * 4)
            c = ("white", "neon_blue_hi", "cold_hi", "neon_green_hi")[k % 4]
            for t in range(ln):
                F.set(x, (y + t) % 48, c if t == ln - 1 else "neon_blue")
        out.append(F)
    return out


def waterfall_sheet():
    """the falling water's moving light (over the kit's static strips): bright streaks racing down a 1.8 m sheet,
    white foam beads; transparent between streaks"""
    out = []
    for f in range(8):
        F = H.Fx(CELL)
        for k in range(16):
            x = 11 + k * 1.7 + (k % 2)
            ph = h("wf", k)
            for j in range(3):
                y0 = (ph * 48 + f * 6 + j * 16) % 48
                ln = 4 + int(h("wl", k, j) * 5)
                for t in range(ln):
                    F.set(x, (y0 + t) % 48, "white" if t == ln - 1 else ("neon_blue_hi" if k % 3 else "cold_hi"))
        out.append(F)
    return out


def waterfall_splash():
    """spray at the foot of the fall: arcs of white / cold droplets, ripple rings, a mist puff"""
    out = []
    for f in range(6):
        F = H.Fx(CELL)
        for k in range(14):
            a = math.pi * (0.1 + 0.8 * h("sa", k))
            t = ((f / 6) + h("st", k)) % 1
            r = 4 + t * 16
            x, y = 24 + math.cos(a) * r, 44 - math.sin(a) * r * 0.9 + t * t * 14
            F.set(x, y, "white" if k % 3 == 0 else "cold_hi")
        for j in range(2):
            rr = 5 + ((f + j * 3) % 6) * 3
            F.ring(24, 44, rr, rr * H.DECAL_SQUASH, "neon_blue_hi" if j else "cold", dots=2)
        for k in range(10):
            x, y = 12 + h("mx", k) * 24, 32 + h("my", k) * 10 - f
            if (k + f) % 2:
                F.set(x, y, "cold_lo")
        out.append(F)
    return out


def glow_mist(cols):
    """low drifting glow fog (decal, sparse dither so it reads translucent): soft bands slide sideways"""
    def fn():
        out = []
        for f in range(8):
            F = H.Fx(CELL)
            for y in range(CELL):
                for x in range(CELL):
                    d = math.hypot(x - 23.5, (y - 23.5) / H.DECAL_SQUASH) / 23.5
                    if d > 1:
                        continue
                    band = 0.5 + 0.5 * math.sin((x + f * 3) * 0.18 + y * 0.35) * math.cos(y * 0.2 - f * 0.4)
                    dens = (1 - d) * 0.55 * band
                    if (x + y * 3 + f) % 4 == 0 and h("m", x, y) < dens * 1.6:
                        F.set(x, y, cols[0] if band > 0.8 and d < 0.5 else cols[1] if band > 0.5 else cols[2])
            out.append(F)
        return out
    return fn


def fireflies(cols):
    """a loose swarm of fireflies drifting in figure-eights, each blinking on and off (2-px tails when bright)"""
    def fn():
        out = []
        for f in range(8):
            F = H.Fx(CELL)
            for k in range(16):
                c = NEONS[cols[k % len(cols)]]
                ph = f / 8 * math.tau + h("fp", k) * math.tau
                x = 24 + math.sin(ph + k) * (8 + 10 * h("fr", k)) + (h("fx", k) - 0.5) * 12
                y = 22 + math.sin(2 * ph + k * 0.7) * (5 + 5 * h("fy", k)) + (h("fz", k) - 0.5) * 18
                on = (f + int(h("fo", k) * 8)) % 8
                if on == 1:
                    F.star(x, y, 1, c[0], c[1], c[1])
                elif on in (0, 2):
                    F.set(x, y, c[1]); F.set(x + 1, y, c[2])
                    F.set(x - math.cos(ph + k), y + 1, c[2])
                elif on in (3, 7):
                    F.set(x, y, c[3])
            out.append(F)
        return out
    return fn


def glow_orb(colour):
    """a hovering glow orb: a 9 px glowing sphere (white core, hi, mid, lo rim), a slow bob, a twinkling halo of
    sparkles and a faint dotted trail beneath it"""
    core, hi, mid, lo = NEONS[colour]

    def fn():
        out = []
        for f in range(8):
            F = H.Fx(CELL)
            bob = [0, -1, -2, -2, -1, 0, 1, 1][f]
            cx, cy = 23.5, 22 + bob
            F.disk(cx, cy, 4.6, [core, hi, hi, mid, mid, lo])
            F.set(cx - 1.5, cy - 1.5, "white"); F.set(cx - 2, cy - 1, "white")
            F.ring(cx, cy, 7, 7, lo, dots=3, start=f * 0.25)
            for k in range(4):
                a = f / 8 * math.tau + k * math.tau / 4
                rr = 9 + (k % 2) * 2
                if (f + k) % 2 == 0:
                    F.star(cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.8, 1, core, hi, mid)
                else:
                    F.set(cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.8, hi)
            for t in range(4):
                if (t + f) % 2 == 0:
                    F.set(cx + math.sin(f * 0.8 + t) * 1.2, cy + 7 + t * 3, lo if t > 1 else mid)
            out.append(F)
        return out
    return fn


def spore_motes():
    out = []
    for f in range(8):
        F = H.Fx(CELL)
        for k in range(14):
            x = 6 + h("smx", k) * 36 + math.sin(f / 8 * math.tau + k) * 2
            y = 44 - ((h("smy", k) * 40 + f * 2) % 40)
            c = ("flower_gold", "lamp", "neon_green_hi", "grass_hi")[k % 4]
            F.set(x, y, c)
            if k % 5 == 0 and f % 2 == 0:
                F.set(x, y - 1, "white")
        out.append(F)
    return out


def blight_aura():
    """decal under the Blight Regent: a slow violet / rose ring of corruption with dark motes (cozy-gloomy)"""
    out = H.pool_frames(("neon_violet_hi", "neon_violet", "neon_violet_lo"), CELL, 6, "blight", rmax=22)
    for f, F in enumerate(out):
        F.ring(23.5, 23.5, 22, 22 * H.DECAL_SQUASH, "flower_rose", dots=3, start=f * 0.3)
        for k in range(10):
            a = k / 10 * math.tau - f * 0.2
            F.set(23.5 + math.cos(a) * 15, 23.5 + math.sin(a) * 15 * H.DECAL_SQUASH, "neon_red" if k % 3 == 0 else "shadow")
    return out


def root_eruption():
    """once: roots burst up out of the floor (the Regent's slam), a ring of dust and leaves"""
    out = []
    for f in range(7):
        F = H.Fx(CELL)
        g = [2, 8, 16, 22, 20, 12, 4][f]
        for k in range(5):
            x = 8 + k * 8 + (k % 2) * 2
            hgt = int(g * (0.6 + 0.4 * h("re", k)))
            for t in range(hgt):
                w = 2 if t < hgt * 0.6 else 1
                for dx in range(w):
                    F.set(x + dx + (t // 6) * (1 if k % 2 else -1), 46 - t, "timber_lo" if dx == 0 else "timber")
            if hgt > 4:
                F.set(x + (hgt // 6) * (1 if k % 2 else -1), 46 - hgt, "neon_violet_hi" if k % 2 else "neon_green_hi")
        if f >= 1:
            r = 4 + f * 3
            F.ring(24, 45, r, r * H.DECAL_SQUASH, "plaster_lo", dots=2)
            for k in range(8):
                a = math.pi * (k / 7)
                F.set(24 + math.cos(a) * r * 1.1, 44 - math.sin(a) * r * 0.5, "grass" if k % 2 else "moss")
        out.append(F)
    return out


def spore_burst():
    """once: a puff of glowing spores (spore elemental attack / death)"""
    out = []
    for f in range(6):
        F = H.Fx(CELL)
        r = 3 + f * 3.4
        for k in range(22):
            a = h("sb", k) * math.tau
            rr = r * (0.5 + 0.5 * h("sr", k))
            if f < 5 or k % 2:
                F.set(24 + math.cos(a) * rr, 28 + math.sin(a) * rr * 0.8, ("flower_gold", "lamp", "neon_green_hi", "neon_green")[k % 4])
        if f < 2:
            F.disk(24, 28, 3 - f, ["white", "lamp", "flower_gold"])
        out.append(F)
    return out


def regent_cleansed():
    """once: the blight lifts - violet motes swirl up and turn green-gold, leaves sparkle, a bright cold-fire bloom"""
    out = []
    for f in range(8):
        F = H.Fx(CELL)
        t = f / 7
        for k in range(18):
            a = k / 18 * math.tau + f * 0.5
            rr = 18 * (1 - t) + 3
            y = 40 - t * 30 - (k % 4) * 2
            c = ("neon_violet", "neon_violet_hi", "flower_rose")[k % 3] if t < 0.4 else ("neon_green_hi", "lamp", "neon_green", "white")[k % 4]
            F.set(24 + math.cos(a) * rr, y + math.sin(a) * rr * 0.4, c)
        if 2 <= f <= 5:
            F.star(24, 30 - f * 2, 3 if f in (3, 4) else 2, "white", "neon_green_hi", "neon_green")
        if f >= 5:
            for k in range(6):
                F.star(10 + k * 6, 10 + (k * 7 + f) % 18, 1, "white", "neon_green_hi", "lamp")
        out.append(F)
    return out


def greenheart_aura():
    """decal under Hjortur (guardian): a ring of green leaf-light and cold-fire dashes turning slowly"""
    out = H.pool_frames(("neon_green_hi", "neon_green", "neon_green_lo"), CELL, 6, "ghaura", rmax=22)
    for f, F in enumerate(out):
        for k in range(12):
            a = k / 12 * math.tau + f * 0.18
            for s in range(3):
                F.set(23.5 + math.cos(a + s * 0.04) * 21, 23.5 + math.sin(a + s * 0.04) * 21 * H.DECAL_SQUASH, "neon_blue" if k % 2 else "neon_green_hi")
    return out


def thorn_lash():
    """the Thornmother's bramble whip: a thorny vine cracks across with rose sparks (billboard, once)"""
    out = []
    for f in range(6):
        F = H.Fx(CELL)
        reach = [10, 22, 34, 40, 36, 24][f]
        for t in range(reach):
            x = 6 + t
            y = 34 - math.sin(t / 40 * math.pi) * 14 + (math.sin(t * 0.7 + f) * 1.5 if f > 2 else 0)
            F.set(x, y, "leaf_deep" if t % 3 else "timber_lo")
            if t % 5 == 2:
                F.set(x, y - 1, "plaster_hi")
        if f >= 2:
            F.star(6 + reach, 34 - math.sin(reach / 40 * math.pi) * 14, 2 if f == 3 else 1, "white", "neon_pink_hi", "neon_pink")
        out.append(F)
    return out


FX = {
    "heart_spring_bubbles": {"fn": heart_spring_bubbles, "fps": 8, "kind": "billboard", "lift": 0.12, "pivot": [24, 47],
                             "notes": "on heart_spring (centre)"},
    "heart_spring_pool": {"fn": heart_spring_pool, "fps": 4, "kind": "decal", "lift": 0.02, "pivot": [24, 24],
                          "light": {"color": "cold", "intensity": 0.9, "range": 5.0}, "notes": "around heart_spring; heals (befriend path)"},
    "stream_flow": {"fn": stream_flow, "fps": 8, "kind": "decal", "lift": 0.08, "pivot": [24, 24],
                    "notes": "one per stream_straight tile (2 m), rotated with the tile; chains top-to-bottom"},
    "waterfall_sheet": {"fn": waterfall_sheet, "fps": 10, "kind": "billboard", "lift": 0.65, "pivot": [24, 47],
                        "light": {"color": "neon_blue", "intensity": 1.2, "range": 6.5},
                        "notes": "in front of waterfall's sheet (z -0.3); covers y 0.65-3.3 m, the splash covers the foot"},
    "waterfall_splash": {"fn": waterfall_splash, "fps": 10, "kind": "billboard", "lift": 0.0, "pivot": [24, 47],
                         "notes": "at the foot of the waterfall (z 0.0)"},
    "glowroot_pool": {"fn": pool("blue", seed="grp"), "fps": 4, "kind": "decal", "lift": 0.02, "pivot": [24, 24],
                      "notes": "neon-blue cold-fire pool under glowroot_arch / glowroot_cluster / neon_mushrooms_blue / blue orbs"},
    "toadstool_glow_pool": {"fn": pool("red", seed="tgp"), "fps": 4, "kind": "decal", "lift": 0.02, "pivot": [24, 24],
                            "notes": "red neon pool under toadstool_giant / toadstool_shelf / red orbs"},
    "pool_violet": {"fn": pool("violet"), "fps": 4, "kind": "decal", "lift": 0.02, "pivot": [24, 24],
                    "notes": "under neon_mushrooms_violet / glowfern / blight_bloom / violet orbs"},
    "pool_green": {"fn": pool("green"), "fps": 4, "kind": "decal", "lift": 0.02, "pivot": [24, 24],
                   "notes": "under hanging_vines / heartseed_cradle / green orbs"},
    "pool_pink": {"fn": pool("pink"), "fps": 4, "kind": "decal", "lift": 0.02, "pivot": [24, 24],
                  "notes": "under neon_mushrooms_pink / dripcap / pink orbs"},
    "glow_mist_blue": {"fn": glow_mist(("neon_blue_hi", "cold", "cold_lo")), "fps": 3, "kind": "decal", "lift": 0.35, "pivot": [24, 24],
                       "glow": True, "notes": "surreal glow fog: scatter 3-6 over water / low ground, overlapping, random frame offsets"},
    "glow_mist_violet": {"fn": glow_mist(("neon_violet_hi", "neon_violet", "neon_violet_lo")), "fps": 3, "kind": "decal", "lift": 0.35,
                         "pivot": [24, 24], "notes": "violet fog for blight rooms / the Regent arena"},
    "glow_mist_green": {"fn": glow_mist(("neon_green_hi", "neon_green", "neon_green_lo")), "fps": 3, "kind": "decal", "lift": 0.35,
                        "pivot": [24, 24], "notes": "green fog for the Heartseed / Hjortur arena"},
    "fireflies_neon": {"fn": fireflies(("blue", "violet", "red", "green", "pink")), "fps": 6, "kind": "billboard", "lift": 0.6,
                       "pivot": [24, 47], "light": {"color": "neon_green_hi", "intensity": 0.25, "range": 2.0},
                       "notes": "mixed neon fireflies, 12 per cell; scatter many"},
}
for c in NEONS:
    FX[f"fireflies_{c}"] = {"fn": fireflies((c,)), "fps": 6, "kind": "billboard", "lift": 0.6, "pivot": [24, 47],
                            "notes": f"{c} fireflies only"}
LIGHTC = {"blue": "neon_blue", "violet": "neon_violet", "red": "neon_red", "green": "neon_green", "pink": "neon_pink"}
POOLFOR = {"blue": "glowroot_pool", "violet": "pool_violet", "red": "toadstool_glow_pool", "green": "pool_green", "pink": "pool_pink"}
for c in NEONS:
    FX[f"glow_orb_{c}"] = {"fn": glow_orb(c), "fps": 6, "kind": "billboard", "lift": 1.1, "pivot": [24, 47],
                           "light": {"color": LIGHTC[c], "intensity": 0.8, "range": 4.0},
                           "notes": f"hovering {c} glow orb (orb centre ~2.2 m when lift 1.1); add {POOLFOR[c]} decal beneath"}
FX.update({
    "spore_motes": {"fn": spore_motes, "fps": 6, "kind": "billboard", "lift": 0.2, "pivot": [24, 47], "notes": "ambient, near toadstools"},
    "blight_aura": {"fn": blight_aura, "fps": 4, "kind": "decal", "lift": 0.03, "pivot": [24, 24],
                    "light": {"color": "neon_violet", "intensity": 0.7, "range": 5.0}, "notes": "under the Blight Regent (scale x3 to his footprint)"},
    "root_eruption": {"fn": root_eruption, "fps": 12, "kind": "billboard", "lift": 0.0, "pivot": [24, 47], "loop": False,
                      "notes": "Regent attack frame 2 (the slam): spawn 3-5 in a line toward the player"},
    "spore_burst": {"fn": spore_burst, "fps": 12, "kind": "billboard", "lift": 0.6, "pivot": [24, 47], "loop": False,
                    "notes": "spore elemental attack / death"},
    "regent_cleansed": {"fn": regent_cleansed, "fps": 8, "kind": "billboard", "lift": 0.8, "pivot": [24, 47], "loop": False,
                        "light": {"color": "neon_green_hi", "intensity": 1.6, "range": 8.0, "curve": [0.3, 0.5, 0.8, 1.0, 1.0, 0.8, 0.6, 0.4]},
                        "notes": "Regent die frame 3 (sapling): the blight lifts"},
    "greenheart_aura": {"fn": greenheart_aura, "fps": 4, "kind": "decal", "lift": 0.03, "pivot": [24, 24],
                        "light": {"color": "neon_green", "intensity": 0.8, "range": 6.0}, "notes": "under Hjortur (guardian); use blight_aura for hjortur_corrupted"},
    "thorn_lash": {"fn": thorn_lash, "fps": 12, "kind": "billboard", "lift": 0.3, "pivot": [6, 34], "loop": False,
                   "notes": "Thornmother attack (mirror for left-facing)"},
})


# ---------------------------------------------------------------------------------------------- critters (24 px)
CC = 24


FROG = [".wk...kw.",
        "mmmmmmmmm",
        "mhmmcmmhm",
        "lmlllllml",
        "lmTTTTTml",
        "l.l...l.l"]


def frog_frame(colour, squat=0, air=0, blink=False, throat=0, legs=0):
    """a little glow frog (9x6 px ~ 0.5 m, front 3/4): bulging white-and-ink eyes on top, a neon back with bright spots, a
    lo mouth line, a glowing throat sac that pulses (T), bent legs. Mirror freely."""
    core, hi, mid, lo = NEONS[colour]
    F = H.Fx(CC)
    rows = list(FROG)
    if squat:
        rows = rows[:1] + rows[2:]                         # crouch: drop a body row
    if legs:                                               # mid-hop: legs stretch down
        rows = rows[:-2] + ["lmTTTTTml", ".l.....l.", "l.......l"]
    tc = {0: hi, 1: hi, 2: core}[throat]
    cmap = {"l": lo, "m": mid, "h": hi, "c": core, "w": "white", "k": mid if blink else "ink", "T": tc}
    x0 = 8
    y0 = 23 - len(rows) + 1 - air
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch != ".":
                F.set(x0 + i, y0 + j, cmap[ch])
    if throat == 2:
        F.set(x0 + 4, y0 + len(rows) - 2, "white")
    return F


def frog_idle(colour):
    def fn():
        return [frog_frame(colour, throat=t, blink=bl) for (t, bl) in ((0, False), (1, False), (2, False), (1, False), (0, False), (0, True))]
    return fn


def frog_hop(colour):
    def fn():
        seq = [(1, 0, 0), (1, 0, 0), (0, 3, 1), (0, 6, 1), (0, 4, 1), (1, 0, 0)]
        return [frog_frame(colour, squat=sq, air=a, legs=lg) for (sq, a, lg) in seq]
    return fn


CRITTERS = {}
for c in ("blue", "green", "pink", "violet"):
    CRITTERS[f"glowfrog_{c}_idle"] = {"fn": frog_idle(c), "fps": 4, "kind": "billboard", "lift": 0.0, "pivot": [12, 23],
                                      "light": {"color": LIGHTC[c], "intensity": 0.3, "range": 1.2},
                                      "notes": f"ambient {c} glow frog: throat-sac pulse + blink; 24 px cell (frog ~9x6 px = 0.5 m wide at 18 px/m: oversized a touch so it reads)"}
    CRITTERS[f"glowfrog_{c}_hop"] = {"fn": frog_hop(c), "fps": 10, "kind": "billboard", "lift": 0.0, "pivot": [12, 23],
                                     "notes": "one hop (0.6 s): move the frog ~0.5 m across the 6 frames, then back to idle"}
