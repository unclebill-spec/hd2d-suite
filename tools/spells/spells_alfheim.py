"""Alfheim combat effects for hd2d spells (original pixel art, Hearthmoor realm-alfheim branch).

  prism_bolt   a prism shard / neon wisp / Lady Sylvaine bolt: a spinning violet diamond with a white heart and a
               short prism trail (projectile -> prism_pop)
  prism_pop    the bolt shattering: violet / pale-blue shards scattering (billboard)
  drain_nova   Lady Sylvaine's magic drain: a violet ring that rushes outward with rune ticks and sparks drawn back
               toward the centre (ground decal, pre-squashed)

Imported by spells.py (EFFECTS.update). 32 px cells, biome palette + the named NEON accents on glow pixels only.
"""
from __future__ import annotations

import math


def effects(Frame, DECAL_SQUASH):
    def prism_bolt(pal, seed):
        out = []
        for f in range(6):
            F = Frame(pal)
            a = f / 6 * math.tau
            for k in range(4):   # a spinning diamond: 4 tips
                b = a + k * math.tau / 4
                for t in range(6):
                    r = t * 0.8
                    w = 2 - t // 3
                    for e in range(-w, w + 1):
                        F.set(16 + math.cos(b) * r - math.sin(b) * e * 0.5, 16 + math.sin(b) * r * 0.8 + math.cos(b) * e * 0.5,
                              "neon_violet_hi" if t < 2 else "neon_violet" if t < 4 else "neon_violet_lo")
            F.set(16, 16, "white"); F.set(15, 16, "white"); F.set(16, 15, "sky")
            for k in range(3):   # prism trail motes
                F.set(16 - 5 - k * 2, 16 + (1 if (k + f) % 2 else -1), "sky" if k % 2 else "neon_violet")
            out.append(F)
        return out

    def prism_pop(pal, seed):
        out = []
        for f in range(6):
            F = Frame(pal)
            if f == 0:
                F.disk(16, 22, 3.2, ["white", "neon_violet_hi", "neon_violet"])
            for k in range(8):
                a = k * math.tau / 8 + 0.3
                r = 2 + f * 2.2
                if f > 3 and (k + f) % 2:
                    continue
                x, y = 16 + math.cos(a) * r, 22 + math.sin(a) * r * 0.8 - f * 0.5
                F.set(x, y, "white" if f < 2 else "neon_violet_hi" if k % 2 else "sky")
                if f < 4:
                    F.set(x + math.cos(a), y + math.sin(a) * 0.8, "neon_violet" if k % 2 else "flower_blue")
            out.append(F)
        return out

    def drain_nova(pal, seed):
        out = []
        sq = DECAL_SQUASH
        for f in range(8):
            F = Frame(pal)
            R = 3 + f * 1.7
            F.ring(16, 16, R, R * sq, "neon_violet" if f < 6 else "neon_violet_lo")
            if f < 6:
                F.ring(16, 16, R - 1, (R - 1) * sq, "neon_violet_hi", dots=2)
            for k in range(8):   # rune ticks riding the ring
                a = k / 8 * math.tau + f * 0.1
                F.set(16 + math.cos(a) * (R + 1), 16 + math.sin(a) * (R + 1) * sq, "white" if (k + f) % 3 == 0 else "neon_violet_hi")
            for k in range(6):   # sparks of stolen magic drawn back to the centre
                a = k / 6 * math.tau - f * 0.2
                r = max(0, 13 - f * 1.6)
                F.set(16 + math.cos(a) * r, 16 + math.sin(a) * r * sq, "sky" if k % 2 else "white")
            F.set(16, 16, "neon_violet_hi" if f % 2 else "white")
            out.append(F)
        return out

    return {
        "prism_bolt": dict(fn=prism_bolt, kind="projectile", fps=12, loop=True, pivot=[16, 16], lift=1.0, speed=5.5, travel=7.0,
                           then="prism_pop", glow=True, light={"color": "flower_blue", "intensity": 4, "range": 3.5, "curve": [1, 1, 1, 1, 1, 1]}, combat=True),
        "prism_pop": dict(fn=prism_pop, kind="billboard", fps=14, loop=False, pivot=[16, 31], lift=0.0, glow=True,
                          light={"color": "flower_blue", "intensity": 5, "range": 3.0, "curve": [1, 0.8, 0.5, 0.3, 0.1, 0]}, combat=True),
        "drain_nova": dict(fn=drain_nova, kind="decal", fps=12, loop=False, pivot=[16, 16], lift=0.03, glow=True, light=None, combat=True),
    }
