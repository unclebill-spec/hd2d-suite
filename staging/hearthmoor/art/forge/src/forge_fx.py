"""Forge Quarter gamefx (48 px cells, hd2d portal format). Neon only on glow pixels."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_lib"))
import hmart as H  # noqa: E402

CELL = 48


def h(*a):
    return H.rng(104, "forge", *a).random()


def forge_fire():
    """the forge mouth's fire: a low wide red-neon blaze (red lo rim, red, red hi, gold, white heart), tongues licking up"""
    out = []
    for f in range(8):
        F = H.Fx(CELL)
        for k in range(5):                                   # ~18 px wide = the 1.0 m forge mouth
            bx = 16 + k * 4
            hgt = 6 + int(6 * h("ff", k, f)) + (4 if k in (1, 2, 3) else 0)
            sway = math.sin(f * 0.8 + k) * 1.2
            for y in range(hgt):
                t = y / hgt
                hw = 2.6 * (1 - t) ** 0.7
                for x in range(int(bx - hw - 1), int(bx + hw + 2)):
                    d = abs(x - bx - sway * t) / max(0.6, hw)
                    if d > 1:
                        continue
                    c = "white" if d < 0.25 and t < 0.25 else "lamp" if d < 0.45 and t < 0.5 else "neon_red_hi" if d < 0.75 else "neon_red"
                    if t > 0.75:
                        c = "neon_red" if d < 0.6 else "neon_red_lo"
                    F.set(x, 46 - y, c)
        for k in range(4):
            sy = 26 - ((f * 3 + k * 7) % 20)
            F.set(17 + k * 5 + (f % 2), sy, "lamp" if k % 2 else "neon_red_hi")
        out.append(F)
    return out


def forge_sparks():
    """once: a hammer strike on the anvil - a fan of gold / white / red sparks with short trails"""
    out = []
    for f in range(6):
        F = H.Fx(CELL)
        for k in range(16):
            a = math.pi * (0.08 + 0.84 * h("sa", k))
            v = 10 + 12 * h("sv", k)
            t = (f + 1) / 6
            x = 24 + math.cos(a) * v * t
            y = 40 - math.sin(a) * v * t * 1.1 + 14 * t * t
            if f < 5 or k % 3 == 0:
                c = "white" if f < 2 else "lamp" if f < 4 else "neon_red_hi"
                F.set(x, y, c)
                F.set(x - math.cos(a), y + math.sin(a), "flower_gold" if f < 4 else "neon_red")
        if f < 2:
            F.star(24, 40, 2 - f, "white", "lamp", "neon_red_hi")
        out.append(F)
    return out


def quench_steam():
    """once: hot steel hits the cold-fire water - a hiss of white steam shot through with neon-blue cold sparks"""
    out = []
    for f in range(8):
        F = H.Fx(CELL)
        t = f / 7
        for k in range(26):
            x = 24 + (h("qx", k) - 0.5) * (8 + 26 * t)
            y = 44 - h("qy", k) * (10 + 26 * t)
            if h("qs", k, f) < 0.8 - t * 0.4:
                F.set(x, y, "white" if k % 4 == 0 and t < 0.5 else "plaster_hi" if k % 3 else "cold_hi")
        for k in range(6):
            if (k + f) % 2 == 0:
                F.set(24 + (h("qb", k) - 0.5) * 20, 44 - h("qc", k) * 16 * (1 + t), "neon_blue_hi" if k % 2 else "neon_blue")
        out.append(F)
    return out


def embers_drift():
    """ambient: red / gold embers rising and winking out (over the hearth, the chimney, the coal bin)"""
    out = []
    for f in range(8):
        F = H.Fx(CELL)
        for k in range(10):
            x = 10 + h("ex", k) * 28 + math.sin(f * 0.7 + k) * 2
            y = 46 - ((h("ey", k) * 46 + f * 4) % 46)
            if (f + k) % 4 != 3:
                F.set(x, y, ("neon_red_hi", "lamp", "neon_red", "flower_gold")[k % 4])
        out.append(F)
    return out


def anvil_glow():
    """the red-hot bar on the anvil, pulsing (a small billboard; swap with forge_sparks on strikes)"""
    out = []
    for f in range(4):
        F = H.Fx(CELL)
        c = ["neon_red", "neon_red_hi", "lamp", "neon_red_hi"][f]
        for x in range(18, 30):
            F.set(x, 44, c if 20 < x < 28 else "neon_red")
        F.set(24, 43, "white" if f == 2 else "lamp")
        out.append(F)
    return out


FX = {
    "forge_fire": {"fn": forge_fire, "fps": 10, "kind": "billboard", "lift": 0.27, "pivot": [24, 47],
                   "light": {"color": "neon_red_hi", "intensity": 1.4, "range": 6.0},
                   "notes": "in forge_hearth's mouth (local [0, 0.27, 0.72])"},
    "forge_fire_top": {"fn": forge_fire, "fps": 10, "kind": "billboard", "lift": 1.05, "pivot": [24, 47],
                       "notes": "on forge_hearth's top fire bed (local [0, 1.05, 0.05])"},
    "forge_sparks": {"fn": forge_sparks, "fps": 14, "kind": "billboard", "lift": 0.92, "pivot": [24, 40], "loop": False,
                     "light": {"color": "lamp", "intensity": 1.2, "range": 3.0, "curve": [1.0, 0.8, 0.5, 0.3, 0.2, 0.1]},
                     "notes": "anvil strike (on forge_anvil's face, y 0.92); fire every ~1.2 s while Hilde works"},
    "quench_steam": {"fn": quench_steam, "fps": 10, "kind": "billboard", "lift": 0.65, "pivot": [24, 47], "loop": False,
                     "light": {"color": "neon_blue_hi", "intensity": 1.0, "range": 3.5, "curve": [1.0, 0.9, 0.7, 0.5, 0.4, 0.3, 0.2, 0.1]},
                     "notes": "over quench_tank when a blade is quenched"},
    "embers_drift": {"fn": embers_drift, "fps": 6, "kind": "billboard", "lift": 1.0, "pivot": [24, 47],
                     "notes": "over the hearth / chimney top (lift 3.6) / coal bin"},
    "anvil_glow": {"fn": anvil_glow, "fps": 4, "kind": "billboard", "lift": 0.48, "pivot": [24, 47],
                   "notes": "optional: animate the hot bar (place on the anvil face)"},
    "forge_pool_red": {"fn": lambda: H.neon_pool_frames("red", 48, 6, rmax=22), "fps": 4, "kind": "decal", "lift": 0.02, "pivot": [24, 24],
                       "notes": "in front of the forge mouth (light zone r ~2.4 m)"},
    "quench_pool_blue": {"fn": lambda: H.pool_frames(("cold_hi", "cold", "cold_lo"), 48, 6, "qpool", rmax=16), "fps": 4, "kind": "decal",
                         "lift": 0.02, "pivot": [24, 24], "notes": "around the quench tank"},
}
