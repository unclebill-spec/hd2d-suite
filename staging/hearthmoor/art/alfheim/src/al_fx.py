"""Alfheim / Lumenvale + Prism Vault gamefx (48 px cells, hd2d portal format). Neon only on glow pixels.
Bill's loves: violet neon on dark, wisps, prism sparkles, radiant pools, floating glow orbs (5 colours, each with a pool)."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_lib"))
import hmart as H  # noqa: E402

CELL = 48
N5 = H.NEON5


def h(*a):
    return H.rng(104, "alfheim", *a).random()


def wisp(colour):
    """a will-o'-wisp: a teardrop flame-light (white heart, hi, mid, lo tail) drifting in a lazy figure-eight, its tail
    streaming behind it, little sparkles shed along the way"""
    core, hi, mid, lo = N5[colour]
    def fn():
        out = []
        for f in range(8):
            F = H.Fx(CELL)
            ph = f / 8 * math.tau
            cx, cy = 24 + math.sin(ph) * 6, 21 + math.sin(2 * ph) * 3
            vx, vy = math.cos(ph) * 6, math.cos(2 * ph) * 6
            L = max(0.01, math.hypot(vx, vy))
            ux, uy = -vx / L, -vy / L
            for t in range(9):                               # streaming tail
                tx, ty = cx + ux * t * 1.2 + math.sin(t * 0.9 + f) * 0.6, cy + uy * t * 1.2 + t * 0.35
                if t < 3:
                    F.set(tx, ty, mid); F.set(tx + 1, ty, lo)
                elif (t + f) % 2 == 0 or t < 5:
                    F.set(tx, ty, lo if t > 5 else mid)
            F.disk(cx, cy, 2.6, [core, core, hi, mid])
            F.set(cx - 1, cy - 1, "white")
            for k in range(3):                               # shed sparkles
                a = h("ws", k, f) * math.tau
                d = 6 + 4 * h("wd", k, f)
                if (f + k) % 3 == 0:
                    F.star(cx + math.cos(a) * d, cy + math.sin(a) * d, 1, core, hi, mid)
                else:
                    F.set(cx + math.cos(a) * d, cy + math.sin(a) * d, hi if k % 2 else lo)
            out.append(F)
        return out
    return fn


def wisp_catch():
    """once: a wisp is caught - sparkles spiral in and wink out into the jar / net with a bright pop"""
    out = []
    for f in range(8):
        F = H.Fx(CELL)
        t = f / 7
        for k in range(14):
            a = k / 14 * math.tau + t * 3.2
            r = 18 * (1 - t) + 1
            x, y = 24 + math.cos(a) * r, 26 + math.sin(a) * r * 0.75
            c = N5[("blue", "violet", "pink")[k % 3]]
            if f < 6:
                F.set(x, y, c[1] if k % 2 else c[2])
                F.set(x - math.cos(a + 1.5) * 1.5, y - math.sin(a + 1.5), c[3])
        if f >= 5:
            F.star(24, 26, 4 - (f - 5) * 1, "white", "neon_blue_hi", "neon_violet")
        out.append(F)
    return out


def prism_sparkle():
    """ambient prism glints: 4-point stars in every neon colour twinkling in turn over a crystal / fountain / arch"""
    out = []
    names = ("violet", "blue", "pink", "green", "violet", "red", "blue", "violet", "pink", "violet")
    for f in range(8):
        F = H.Fx(CELL)
        for k in range(10):
            x, y = 6 + 36 * h("px", k), 6 + 32 * h("py", k)
            c = N5[names[k]]
            st = (f + int(h("po", k) * 8)) % 8
            if st == 0:
                F.star(x, y, 2, c[0], c[1], c[2])
            elif st in (1, 7):
                F.star(x, y, 1, c[1], c[2], c[3])
            elif st == 2:
                F.set(x, y, c[2])
        out.append(F)
    return out


def light_motes():
    """slow rising light motes (violet / blue / pink / white) - Lumenvale's air at night"""
    out = []
    for f in range(8):
        F = H.Fx(CELL)
        for k in range(14):
            x = 6 + 36 * h("mx", k) + math.sin(f * 0.8 + k) * 1.2
            y = 46 - ((f * 3 + h("my", k) * 46) % 46)
            c = N5[("violet", "blue", "pink", "violet")[k % 4]]
            F.set(x, y, c[1] if y < 20 else c[2] if y < 36 else c[3])
            if k % 4 == 0 and y < 30:
                F.set(x, y - 1, "white")
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


def fountain_sparkle():
    """glowing droplets leaping from the prism fountain's upper bowl and falling into the basin (billboard)"""
    out = []
    for f in range(8):
        F = H.Fx(CELL)
        for k in range(12):
            a = k / 12 * math.tau
            t = ((f / 8) + h("ft", k)) % 1
            r = 4 + 14 * t
            x = 24 + math.cos(a) * r
            y = 14 - 10 * t + 30 * t * t + math.sin(a) * r * 0.3
            c = N5["violet" if k % 3 else "blue"]
            F.set(x, y, c[1] if t < 0.5 else c[2])
            if t < 0.3:
                F.set(x, y - 1, "white")
        F.star(24, 12, 1 + (f % 2), "white", "neon_violet_hi", "neon_violet")
        out.append(F)
    return out


def sylvaine_aura():
    """decal under Lady Sylvaine: a violet ring of drained light - two dotted rings turning opposite ways, runic glints,
    a dithered violet pool inside (her neon lives here, not on the sprite)"""
    out = []
    for f in range(8):
        F = H.Fx(CELL)
        for y in range(CELL):
            for x in range(CELL):
                d = math.hypot(x - 23.5, (y - 23.5) / H.DECAL_SQUASH) / 22
                if d > 1:
                    continue
                if (x + y) % 2 == 0 and h("sa", x, y, f // 2) < (1 - d) * 0.5:
                    F.set(x, y, "neon_violet_lo" if d > 0.45 else "neon_violet")
        F.ring(23.5, 23.5, 21, 21 * H.DECAL_SQUASH, "neon_violet", dots=28, start=f * 0.1)
        F.ring(23.5, 23.5, 15, 15 * H.DECAL_SQUASH, "neon_violet_hi", dots=18, start=-f * 0.14)
        for k in range(6):
            a = k / 6 * math.tau + f * 0.1
            F.star(23.5 + math.cos(a) * 18, 23.5 + math.sin(a) * 18 * H.DECAL_SQUASH, 1 if (k + f) % 2 else 0, "white", "neon_violet_hi", "neon_pink")
        out.append(F)
    return out


def drain_stream():
    """the drain: a 48 px horizontal stream segment of stolen light flowing RIGHT -> LEFT toward Sylvaine (rotate /
    tile along the line from target to her hand). Violet + pink + blue motes in two twisting strands."""
    out = []
    for f in range(8):
        F = H.Fx(CELL)
        for x in range(CELL):
            ph = (x + f * 6) * 0.26
            for sd, col in ((1, "violet"), (-1, "pink")):
                y = 24 + math.sin(ph) * 4 * sd
                c = N5[col]
                if (x + f * 2) % 3 != 0:
                    F.set(x, y, c[1] if math.cos(ph) * sd > 0 else c[2])
                if (x + f * 2) % 7 == 0:
                    F.set(x, y + sd, c[3])
            if (x * 3 + f * 5) % 11 == 0:
                F.set(x, 24 + math.sin(ph * 2) * 1.5, "white")
        for k in range(4):
            x = (47 - (f * 6 + k * 12) % 48)
            F.star(x, 24 + math.sin(x * 0.3) * 3, 1, "white", "neon_violet_hi", "neon_violet")
        out.append(F)
    return out


def drain_hit():
    """on the drained target: motes of their light are pulled out and up in a violet / blue spiral"""
    out = []
    for f in range(8):
        F = H.Fx(CELL)
        for k in range(12):
            t = ((f / 8) + k / 12) % 1
            a = k * 2.3 + t * 5
            r = 10 * (1 - t) + 2
            x, y = 24 + math.cos(a) * r, 36 - t * 26 + math.sin(a) * 2
            c = N5["violet" if k % 2 else "blue"]
            F.set(x, y, c[1] if t > 0.5 else c[2])
        F.ring(24, 38, 10, 4, "neon_violet", dots=10, start=f * 0.2)
        out.append(F)
    return out


def violet_moths():
    """once (Sylvaine's death, frames 26-27): her gown releases a cloud of glowing violet moths that flutter up and
    away and wink out - cozy, never gory"""
    out = []
    for f in range(10):
        F = H.Fx(CELL)
        t = f / 9
        for k in range(12):
            a = h("ma", k) * math.tau
            x = 24 + math.cos(a) * (4 + 16 * t) * (0.6 + 0.6 * h("mr", k)) + math.sin(f * 1.3 + k) * 1.5
            y = 42 - t * 38 * (0.6 + 0.5 * h("mv", k)) + math.sin(f * 2 + k) * 1
            if t > 0.8 and h("mo", k) < (t - 0.8) * 5:
                continue
            c = N5["violet" if k % 3 else "pink"]
            wing = (f + k) % 2
            F.set(x, y, "white")
            F.set(x - 1, y - wing, c[1]); F.set(x + 1, y - wing, c[1])
            F.set(x - 2, y - wing * 2 + 1, c[2]); F.set(x + 2, y - wing * 2 + 1, c[2])
            F.set(x, y + 1, c[3])
        out.append(F)
    return out


def prism_shatter():
    """once: a prism shard bursts (death / hit) - crystal splinters fly out with white glints"""
    out = []
    for f in range(7):
        F = H.Fx(CELL)
        t = (f + 1) / 7
        for k in range(14):
            a = k / 14 * math.tau + h("pa", k) * 0.4
            v = 10 + 12 * h("pv", k)
            x, y = 24 + math.cos(a) * v * t, 26 + math.sin(a) * v * t * 0.8 + 10 * t * t
            c = ("neon_blue_hi", "neon_violet_hi", "white", "neon_blue")[k % 4]
            F.set(x, y, c); F.set(x - math.cos(a), y - math.sin(a), "neon_blue_lo" if k % 2 else "neon_violet")
        if f < 3:
            F.star(24, 26, 3 - f, "white", "neon_blue_hi", "neon_violet")
        out.append(F)
    return out


def mirror_flash():
    """once: the mirror duelist's thrust - a sharp white star flash with a blue / violet glint ring"""
    out = []
    for f in range(6):
        F = H.Fx(CELL)
        sz = [2, 5, 4, 3, 2, 1][f]
        F.star(24, 24, sz, "white", "neon_blue_hi", "neon_violet_hi")
        if f >= 1:
            F.ring(24, 24, 4 + f * 3, 3 + f * 2, "neon_blue_hi" if f < 4 else "neon_violet", dots=10 + f * 2, start=f * 0.3)
        out.append(F)
    return out


def lantern_glow():
    """tiny glow for the elf lampwright's handheld wisp lantern (pin it at the lantern: see README)"""
    out = []
    for f in range(4):
        F = H.Fx(CELL)
        F.disk(24, 24, 2.2, ["white", "neon_blue_hi", "neon_blue"])
        F.ring(24, 24, 4, 3.5, "neon_blue_lo", dots=6, start=f * 0.4)
        if f % 2 == 0:
            F.star(24 + (2 if f == 0 else -3), 20, 1, "white", "neon_blue_hi", "neon_blue")
        out.append(F)
    return out


def pool(colour, rmax=22):
    return lambda: H.neon_pool_frames(colour, CELL, 6, rmax=rmax)


FX = {
    "pool_violet": {"fn": pool("violet"), "fps": 4, "kind": "decal", "lift": 0.02, "pivot": [24, 24],
                    "notes": "radiant violet light pool: under crystal_spire / lumen_tree / prism_fountain / elf_archway / vault crystals"},
    "pool_violet_small": {"fn": pool("violet", 14), "fps": 4, "kind": "decal", "lift": 0.02, "pivot": [24, 24],
                          "notes": "under lumen_lamp / elf_rail caps / vault_pillar"},
    "pool_blue_small": {"fn": pool("blue", 12), "fps": 4, "kind": "decal", "lift": 0.02, "pivot": [24, 24],
                        "notes": "under wisp_lantern_post / wisp_jar"},
    "glow_mist_violet": {"fn": glow_mist(("neon_violet_hi", "neon_violet", "neon_violet_lo")), "fps": 5, "kind": "decal", "lift": 0.05,
                         "pivot": [24, 24], "notes": "foggy glow areas: low violet fog in hollows, under bridges, around the throne"},
    "light_motes": {"fn": light_motes, "fps": 6, "kind": "billboard", "lift": 0.2, "pivot": [24, 47], "notes": "ambient air of Lumenvale"},
    "prism_sparkle": {"fn": prism_sparkle, "fps": 6, "kind": "billboard", "lift": 0.6, "pivot": [24, 40],
                      "notes": "over crystal_spire (lift 1.4), prism_fountain (lift 1.6), elf_archway keystone (lift 3.0)"},
    "fountain_sparkle": {"fn": fountain_sparkle, "fps": 8, "kind": "billboard", "lift": 0.45, "pivot": [24, 47],
                         "notes": "on prism_fountain (local [0, 0.45, 0])"},
    "wisp_violet": {"fn": wisp("violet"), "fps": 8, "kind": "billboard", "lift": 1.2, "pivot": [24, 30],
                    "light": {"color": "neon_violet_hi", "intensity": 0.6, "range": 2.0}, "notes": "wild wisp (catchable)"},
    "wisp_blue": {"fn": wisp("blue"), "fps": 8, "kind": "billboard", "lift": 1.2, "pivot": [24, 30],
                  "light": {"color": "neon_blue_hi", "intensity": 0.6, "range": 2.0}, "notes": "wild wisp (catchable)"},
    "wisp_pink": {"fn": wisp("pink"), "fps": 8, "kind": "billboard", "lift": 1.2, "pivot": [24, 30],
                  "light": {"color": "neon_pink_hi", "intensity": 0.6, "range": 2.0}, "notes": "wild wisp (rare, catchable)"},
    "wisp_catch": {"fn": wisp_catch, "fps": 12, "kind": "billboard", "lift": 1.0, "pivot": [24, 30], "loop": False,
                   "light": {"color": "neon_blue_hi", "intensity": 1.0, "range": 2.5, "curve": [0.6, 0.7, 0.8, 0.9, 1.0, 1.0, 0.6, 0.2]},
                   "notes": "on catching a wisp (at the net / jar)"},
    "lantern_glow": {"fn": lantern_glow, "fps": 4, "kind": "billboard", "lift": 0.0, "pivot": [24, 24],
                     "light": {"color": "neon_blue_hi", "intensity": 0.5, "range": 1.6},
                     "notes": "elf_lampwright's lantern: sprite px offset (-7, -21) from the feet pivot facing down, (-5, -21) left, mirrored right; hidden facing up"},
    "sylvaine_aura": {"fn": sylvaine_aura, "fps": 8, "kind": "decal", "lift": 0.03, "pivot": [24, 24],
                      "light": {"color": "neon_violet", "intensity": 0.9, "range": 6.0},
                      "notes": "under Lady Sylvaine always (scale the decal x3 for her 5.5x footprint, or tile 3x3)"},
    "drain_stream": {"fn": drain_stream, "fps": 12, "kind": "billboard", "lift": 1.2, "pivot": [0, 24],
                     "notes": "attack frame 14: stretch / tile from the target (x=47 end) to her raised hand (x=0 end)"},
    "drain_hit": {"fn": drain_hit, "fps": 10, "kind": "billboard", "lift": 0.0, "pivot": [24, 40],
                  "light": {"color": "neon_violet_hi", "intensity": 0.7, "range": 2.0}, "notes": "on the drained target"},
    "violet_moths": {"fn": violet_moths, "fps": 10, "kind": "billboard", "lift": 0.0, "pivot": [24, 47], "loop": False,
                     "light": {"color": "neon_violet_hi", "intensity": 0.8, "range": 4.0, "curve": [1, 1, 0.9, 0.8, 0.7, 0.6, 0.4, 0.3, 0.2, 0.1]},
                     "notes": "Sylvaine die frames 26-27 (spawn 3 offset copies across her gown)"},
    "prism_shatter": {"fn": prism_shatter, "fps": 14, "kind": "billboard", "lift": 0.6, "pivot": [24, 30], "loop": False,
                      "light": {"color": "neon_blue_hi", "intensity": 1.0, "range": 2.5, "curve": [1, 0.8, 0.6, 0.4, 0.3, 0.2, 0.1]},
                      "notes": "prism shard die (frame 25) and its splinter hits"},
    "mirror_flash": {"fn": mirror_flash, "fps": 14, "kind": "billboard", "lift": 1.0, "pivot": [24, 24], "loop": False,
                     "light": {"color": "white", "intensity": 1.0, "range": 2.0, "curve": [0.6, 1, 0.7, 0.4, 0.2, 0.1]},
                     "notes": "mirror duelist thrust (frame 14) at the rapier tip"},
}
ORB_POOL = {"blue": "blue", "violet": "violet", "red": "red", "green": "green", "pink": "pink"}
for c in N5:
    FX[f"glow_orb_{c}"] = {"fn": (lambda c=c: H.glow_orb_frames(c, CELL)), "fps": 6, "kind": "billboard", "lift": 1.4, "pivot": [24, 33],
                           "light": {"color": f"neon_{c}_hi", "intensity": 0.7, "range": 3.0, "pool": f"glow_orb_pool_{c}"},
                           "notes": f"floating glow orb (hover 1.1-2.2 m); light pool colour neon_{c} -> glow_orb_pool_{c} on the ground below"}
    FX[f"glow_orb_pool_{c}"] = {"fn": pool(c, 16), "fps": 4, "kind": "decal", "lift": 0.02, "pivot": [24, 24],
                                "notes": f"the ground light pool under glow_orb_{c}"}
