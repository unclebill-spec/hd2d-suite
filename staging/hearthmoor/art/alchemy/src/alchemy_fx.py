"""Alchemy gamefx (48 px, hd2d portal format): the animated bubbling brew on the cauldron, its little fire, light pools,
a brew-success puff. Neon only on glow pixels."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_lib"))
import hmart as H  # noqa: E402

CELL = 48
BREWC = {"blue": ("white", "neon_blue_hi", "neon_blue", "neon_blue_lo"),
         "violet": ("white", "neon_violet_hi", "neon_violet", "neon_violet_lo"),
         "green": ("white", "neon_green_hi", "neon_green", "neon_green_lo")}


def h(*a):
    return H.rng(104, "alch", *a).random()


def brew(colour):
    """the brew surface seen at the locked 3/4 angle (rx 13, ry 4 px = the 0.4 m pot mouth), rolling: bubbles swell and pop
    (rings + sparkle), a swirl of light, vapour wisps and motes rising above the rim"""
    core, hi, mid, lo = BREWC[colour]

    def fn():
        out = []
        cx, cy, rx, ry = 23.5, 36.0, 13.0, 4.2
        for f in range(8):
            F = H.Fx(CELL)
            for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
                for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                    d = math.hypot((x - cx) / rx, (y - cy) / ry)
                    if d > 1:
                        continue
                    a = math.atan2((y - cy) / ry, (x - cx) / rx)
                    sw = (a / math.tau * 2 + d * 1.3 - f / 8) % 1
                    c = lo if d > 0.82 else (hi if sw < 0.14 else mid)
                    F.set(x, y, c)
            for k in range(5):                                # bubbles: swell -> pop
                ph = (f / 8 + h("bp", k)) % 1
                bx = cx + (h("bx", k) - 0.5) * rx * 1.4
                by = cy + (h("by", k) - 0.5) * ry * 1.2
                if ph < 0.6:
                    r = 0.6 + ph * 2.2
                    F.ring(bx, by - r * 0.5, r, r * 0.8, hi)
                    F.set(bx - r * 0.4, by - r, core)
                elif ph < 0.75:
                    F.star(bx, by - 1, 1, core, hi, mid)
                else:
                    F.ring(bx, by, 2.5, 1.0, mid, dots=2)
            for k in range(6):                                # vapour wisps + motes rising
                ph = (f / 8 + h("vp", k)) % 1
                vx = cx + (h("vx", k) - 0.5) * 18 + math.sin(ph * 6 + k) * 2
                vy = cy - 4 - ph * 30
                c = hi if ph < 0.3 else mid if ph < 0.65 else lo
                F.set(vx, vy, c)
                if k % 2 == 0 and ph < 0.5:
                    F.set(vx, vy - 1, c)
            out.append(F)
        return out
    return fn


def cauldron_fire():
    """the little log fire under the pot: short red / gold tongues"""
    out = []
    for f in range(6):
        F = H.Fx(CELL)
        for k in range(4):
            bx = 18 + k * 3.5
            hgt = 2 + int(3 * h("cf", k, f))
            for y in range(hgt):
                t = y / hgt
                hw = 1.8 * (1 - t)
                for x in range(int(bx - hw), int(bx + hw) + 1):
                    d = abs(x - bx) / max(0.6, hw)
                    F.set(x, 46 - y, "white" if d < 0.3 and t < 0.3 else "lamp" if d < 0.5 else "neon_red_hi" if t < 0.6 else "neon_red")
        out.append(F)
    return out


def brew_puff(colour):
    """once: a brew finishes - a round puff of coloured vapour with a burst of sparkles"""
    core, hi, mid, lo = BREWC[colour]

    def fn():
        out = []
        for f in range(7):
            F = H.Fx(CELL)
            r = 3 + f * 2.6
            for k in range(30):
                a = h("pa", k) * math.tau
                rr = r * (0.6 + 0.4 * h("pr", k))
                if h("pk", k, f) < 0.9 - f * 0.1:
                    F.set(24 + math.cos(a) * rr, 26 + math.sin(a) * rr * 0.75 - f, (hi, mid, lo)[k % 3])
            for k in range(5):
                a = k / 5 * math.tau + f * 0.4
                F.star(24 + math.cos(a) * r * 1.1, 26 + math.sin(a) * r * 0.8 - f, 1 if f < 5 else 0, core, hi, mid)
            out.append(F)
        return out
    return fn


FX = {}
for c in BREWC:
    FX[f"cauldron_brew_{c}"] = {"fn": brew(c), "fps": 8, "kind": "billboard", "lift": 0.98, "pivot": [24, 36],
                                "light": {"color": BREWC[c][2], "intensity": 0.9, "range": 4.5},
                                "notes": f"on cauldron_{c}: pivot = centre of the brew surface (local [0, 0.98, 0])"}
FX["cauldron_fire"] = {"fn": cauldron_fire, "fps": 10, "kind": "billboard", "lift": 0.04, "pivot": [24, 47],
                       "light": {"color": "neon_red_hi", "intensity": 0.5, "range": 2.0}, "notes": "under any cauldron (local [0, 0.04, 0.32]): peeks out below the belly"}
for c in BREWC:
    FX[f"cauldron_pool_{c}"] = {"fn": (lambda c=c: H.pool_frames(BREWC[c][1:], 48, 6, f"cpool{c}", rmax=19)), "fps": 4, "kind": "decal",
                                "lift": 0.02, "pivot": [24, 24], "notes": f"floor pool round cauldron_{c} (r ~2 m)"}
for c in BREWC:
    FX[f"brew_puff_{c}"] = {"fn": brew_puff(c), "fps": 12, "kind": "billboard", "lift": 1.0, "pivot": [24, 47], "loop": False,
                            "notes": "crafting success over the cauldron"}
