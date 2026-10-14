"""Orb lantern gamefx: animated fish swimming inside the water orbs, light pools, and hovering glow orbs.
  orb_fx_24   24 px cells: orb_small_<blue|violet|red>  (a 13 px orb: table / hanging / standing lanterns)
  orb_fx_32   32 px cells: orb_large_<blue|violet|red>  (a 21 px orb: garden post) + orb_grand_mix (all three colours)
  orb_fx_48   48 px cells: orb_pool_<blue|violet|red> (warm-room / garden pools), glow_orb_<blue|violet|red|green|pink>,
              glow_orb_pool_<green|pink>
The orb billboards are drawn as the whole orb (water + fish + glass glint), so they can replace the kit orb's look
exactly when animated; anchor at the kit piece's lamp marker (orb centre)."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_lib"))
import hmart as H  # noqa: E402

FISHC = {   # fish: (hi, mid, lo) ; water: (deep, mid, light) - glowing sea water lightly tinted toward its fish
    "blue": (("neon_blue_hi", "neon_blue", "neon_blue_lo"), ("cloth", "neon_blue_lo", "cold")),
    "violet": (("neon_violet_hi", "neon_violet", "neon_violet_lo"), ("cloth", "neon_violet_lo", "cold_lo")),
    "red": (("neon_red_hi", "neon_red", "neon_red_lo"), ("shadow", "neon_violet_lo", "neon_red_lo")),
}


def h(*a):
    return H.rng(104, "orb", *a).random()


def fish(F, x, y, d, cols, big=False):
    """a tiny glowing fish facing d (+1 right / -1 left): body 3-4 px, head glint, forked tail"""
    hi, mid, lo = cols
    L = 4 if big else 3
    for t in range(L):
        F.set(x + d * (t - L // 2), y, hi if t < L - 1 else "white")
    F.set(x + d * (L - 1 - L // 2), y, "white")
    if big:
        F.set(x, y - 1, mid); F.set(x - d, y + 1, lo)
    F.set(x - d * (L // 2 + 1), y - 1, mid); F.set(x - d * (L // 2 + 1), y + 1, mid)


def orb_frames(cell, R, colours, frames=8):
    """the whole orb: dark-tinted water with a lit core and dithered caustics, fish circling (they pass behind = dim lo
    when on the far half), rising bubbles, a white glass glint and a thin rim"""
    out = []
    cx, cy = cell / 2 - 0.5, cell / 2 - 0.5
    base = FISHC[colours[0]][1]
    for f in range(frames):
        F = H.Fx(cell)
        for y in range(cell):
            for x in range(cell):
                d = math.hypot(x - cx, y - cy) / R
                if d > 1:
                    continue
                caust = math.sin(x * 0.9 + f * 0.8) * math.cos(y * 0.8 - f * 0.6)
                if d > 0.86:
                    c = base[0] if (x + y) % 2 else base[1]          # a darker glass rim so the orb reads round
                elif caust > 0.72 and (x + y) % 2 == 0:
                    c = base[2]                                      # sparse caustic glints
                elif d > 0.7 and (x + y + f) % 4 == 0:
                    c = base[0]
                else:
                    c = base[1]
                F.set(x, y, c)
        n = len(colours) if len(colours) > 1 else (3 if R > 8 else 2)
        for k in range(n):
            col = FISHC[colours[k % len(colours)]][0]
            ph = f / frames * math.tau * (1 if k % 2 == 0 else -1) + k * math.tau / n
            fx = cx + math.cos(ph) * R * 0.55
            fy = cy + (k - (n - 1) / 2) * (R * 0.5 / max(1, n - 1) * 1.6) + math.sin(ph * 2) * 0.8
            front = math.sin(ph) > -0.2
            d = -1 if (math.sin(ph) > 0) == (k % 2 == 0) else 1
            if front:
                fish(F, fx, fy, d, col, big=R > 8)
            else:
                fish(F, fx, fy, d, (col[1], col[2], col[2]), big=False)
        for k in range(2 + (R > 8)):
            by = cy + R * 0.7 - ((f * 2 + k * 5) % int(R * 1.5))
            F.set(cx + R * 0.3 - k * 2, by, "white" if k == 0 else FISHC[colours[0]][0][0])
        gl = max(1, int(R * 0.25))
        for t in range(gl + 1):
            F.set(cx - R * 0.45 + t, cy - R * 0.55, "white")
        F.set(cx - R * 0.55, cy - R * 0.35, "white")
        out.append(F)
    return out


FX24 = {f"orb_small_{c}": {"fn": (lambda c=c: orb_frames(24, 6.6, [c])), "fps": 6, "kind": "billboard", "lift": 0.0,
                           "pivot": [12, 12],
                           "light": {"color": FISHC[c][0][1], "intensity": 0.7, "range": 4.0},
                           "notes": "anchor (pivot = orb centre) at the kit lamp marker of orb_table / orb_hanging / orb_standing"}
        for c in FISHC}
FX32 = {f"orb_large_{c}": {"fn": (lambda c=c: orb_frames(32, 10.5, [c])), "fps": 6, "kind": "billboard", "lift": 0.0,
                           "pivot": [16, 16], "light": {"color": FISHC[c][0][1], "intensity": 0.8, "range": 5.0},
                           "notes": "orb_garden_* (orb centre = lamp marker)"}
        for c in FISHC}
FX32["orb_grand_mix"] = {"fn": lambda: orb_frames(32, 15.0, ["blue", "violet", "red", "violet", "blue"]), "fps": 6, "kind": "billboard",
                         "lift": 0.0, "pivot": [16, 16], "light": {"color": "#7a8cff", "intensity": 1.0, "range": 7.0},
                         "notes": "orb_grand (1.1 m orb = 20 px; this 30 px billboard is a touch larger: scale 0.66 or use as UI / close-up)"}
FX48 = {}
for c, (fc, _) in FISHC.items():
    FX48[f"orb_pool_{c}"] = {"fn": (lambda fc=fc, c=c: H.pool_frames(fc, 48, 6, f"orbpool_{c}", rmax=18)), "fps": 4, "kind": "decal",
                             "lift": 0.02, "pivot": [24, 24], "notes": f"light pool under any {c} orb lantern (radius ~1.9 m)"}
for c in H.NEON5:
    FX48[f"glow_orb_{c}"] = {"fn": (lambda c=c: H.glow_orb_frames(c)), "fps": 6, "kind": "billboard", "lift": 1.1, "pivot": [24, 47],
                             "light": {"color": H.NEON5[c][2], "intensity": 0.8, "range": 4.0},
                             "notes": f"hovering {c} glow orb (garden / house ambient light); pool: " + (f"orb_pool_{c}" if c in FISHC else f"glow_orb_pool_{c}")}
for c in ("green", "pink"):
    FX48[f"glow_orb_pool_{c}"] = {"fn": (lambda c=c: H.neon_pool_frames(c, 48, 6, rmax=18)), "fps": 4, "kind": "decal", "lift": 0.02,
                                  "pivot": [24, 24], "notes": f"pool under a {c} glow orb"}
