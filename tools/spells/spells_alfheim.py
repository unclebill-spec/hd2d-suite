"""Alfheim combat effects for hd2d spells (original pixel art, Hearthmoor realm-alfheim branch).

  prism_bolt   a prism shard / neon wisp / Lady Sylvaine bolt: a spinning violet diamond with a white heart and a
               short prism trail (projectile -> prism_pop)
  prism_pop    the bolt shattering: violet / pale-blue shards scattering (billboard)
  drain_nova   Lady Sylvaine's magic drain: a violet ring that rushes outward with rune ticks and sparks drawn back
               toward the centre (ground decal, pre-squashed)

  lumi_wisp    Lumi, the talking wisp (script 5.5): a neon-blue core (#5ac8ff) with white dot eyes, a pulsing violet halo
               (#a45cf0) and a curling trail; ~2x the wisp-kit pet (billboard, loops)
  lumi_dim     Lumi / a dimmed wisp gone grey: a stone-grey core, no halo, a stuttering flicker (billboard)
  lumi_spark   one of Lumi's Wisp Call mini-wisps: a small blue spark with a violet ring (billboard)
  lumi_zap     a mini-wisp's zap: a short blue-white bolt (projectile -> prism_pop)
  lumi_mark    Lumi's mark on a foe: a violet ring with 4 ticks turning (ground decal)
  beam_hit     a light beam landing on a receiver / foe: a white-violet starburst (billboard)

Imported by spells.py (EFFECTS.update). 32 px cells, biome palette + the named NEON accents on glow pixels only.
"""
from __future__ import annotations

import math


def effects(Frame, DECAL_SQUASH):
    # Lumi's neon blue (#5ac8ff, script 5.5) joins the named NEON glow accents from here (glow pixels only), so the shared
    # spells.py table stays untouched
    _N = Frame.__init__.__globals__.get("NEON")
    if _N is not None:
        _N.setdefault("neon_blue", "#5ac8ff"); _N.setdefault("neon_blue_hi", "#bfeaff"); _N.setdefault("neon_blue_lo", "#2a7ad0")

    def lumi_wisp(pal, seed):
        out = []
        for f in range(8):
            F = Frame(pal)
            cx, cy = 16, 15
            pulse = 1.0 + 0.15 * math.sin(f / 8 * math.tau)
            R = 8.4 * pulse
            F.ring(cx, cy, R, R, "neon_violet", dots=0)                      # the halo, pulsing 1.0 -> 1.15
            F.ring(cx, cy, R - 1, R - 1, "neon_violet_lo", dots=3)
            for k in range(7):                                             # the curling tail, blue to violet
                a = 2.2 + k * 0.32 + math.sin(f / 8 * math.tau + k) * 0.18
                r = 6 + k * 1.5
                F.set(cx + math.cos(a) * r, cy + math.sin(a) * r * 0.7 + k * 0.6, "neon_blue_hi" if k < 2 else "neon_blue" if k < 4 else "neon_violet" if k < 6 else "neon_violet_lo")
            F.disk(cx, cy, 5.2, ["neon_blue_hi", "neon_blue", "neon_blue", "neon_blue_lo"])   # the core
            F.set(cx - 2, cy - 3, "white"); F.set(cx - 1, cy - 3, "white")
            blink = f == 6
            for ex in (cx - 2, cx + 2):                                     # white dot eyes (blink once a loop)
                F.set(ex, cy, "white")
                if not blink:
                    F.set(ex, cy - 1, "white")
            out.append(F)
        return out

    def lumi_dim(pal, seed):
        out = []
        for f in range(6):
            F = Frame(pal)
            cx, cy = 16, 16
            on = f not in (2, 4)                                            # a stuttering light
            F.disk(cx, cy, 4.6, ["stone_hi", "stone", "stone", "stone_lo"] if on else ["stone", "stone_lo", "stone_lo", "shadow"])
            for ex in (cx - 2, cx + 2):
                F.set(ex, cy, "plaster" if on else "stone_hi")
            if on and f % 3 == 0:
                F.set(cx + 6, cy - 4, "stone_hi")
            out.append(F)
        return out

    def lumi_spark(pal, seed):
        out = []
        for f in range(6):
            F = Frame(pal)
            r = 3.4 + (f % 3) * 0.5
            F.ring(16, 16, r, r, "neon_violet")
            F.disk(16, 16, 2.0, ["white", "neon_blue_hi", "neon_blue"])
            a = f / 6 * math.tau
            F.set(16 + math.cos(a) * 5.5, 16 + math.sin(a) * 4, "neon_blue_hi")
            out.append(F)
        return out

    def lumi_zap(pal, seed):
        out = []
        for f in range(4):
            F = Frame(pal)
            for t in range(9):
                F.set(16 - t, 16 + ((t + f) % 3 - 1) * (1 if t > 2 else 0), "white" if t < 2 else "neon_blue_hi" if t < 5 else "neon_blue")
            F.set(16, 15, "neon_blue_hi"); F.set(16, 17, "neon_blue_hi"); F.set(17, 16, "white")
            out.append(F)
        return out

    def lumi_mark(pal, seed):
        out = []
        sq = DECAL_SQUASH
        for f in range(8):
            F = Frame(pal)
            F.ring(16, 16, 11, 11 * sq, "neon_violet", dots=0)
            for k in range(4):
                a = k / 4 * math.tau + f / 8 * math.tau / 4
                for d in (0, 1):
                    F.set(16 + math.cos(a) * (11 - d * 2), 16 + math.sin(a) * (11 - d * 2) * sq, "neon_violet_hi" if d else "white")
            out.append(F)
        return out

    def beam_hit(pal, seed):
        out = []
        for f in range(6):
            F = Frame(pal)
            n = 4 - abs(2 - f)
            F.star(16, 22, max(1, n + 2), core="white", arm="neon_violet_hi")
            for k in range(6):
                a = k / 6 * math.tau + f * 0.4
                F.set(16 + math.cos(a) * (4 + f), 22 + math.sin(a) * (3 + f * 0.6), "neon_violet" if k % 2 else "sky")
            out.append(F)
        return out

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

    lumi = {
        "lumi_wisp": dict(fn=lumi_wisp, kind="billboard", fps=8, loop=True, pivot=[16, 16], lift=0.0, glow=True, light=None, combat=True),
        "lumi_dim": dict(fn=lumi_dim, kind="billboard", fps=6, loop=True, pivot=[16, 16], lift=0.0, glow=True, light=None, combat=True),
        "lumi_spark": dict(fn=lumi_spark, kind="billboard", fps=10, loop=True, pivot=[16, 16], lift=0.0, glow=True, light=None, combat=True),
        "lumi_zap": dict(fn=lumi_zap, kind="projectile", fps=14, loop=True, pivot=[16, 16], lift=0.0, speed=9.0, travel=4.0,
                         then="prism_pop", glow=True, light=None, combat=True),
        "lumi_mark": dict(fn=lumi_mark, kind="decal", fps=8, loop=True, pivot=[16, 16], lift=0.03, glow=True, light=None, combat=True),
        "beam_hit": dict(fn=beam_hit, kind="billboard", fps=12, loop=False, pivot=[16, 31], lift=0.0, glow=True, light=None, combat=True),
    }
    return {
        **lumi,
        "prism_bolt": dict(fn=prism_bolt, kind="projectile", fps=12, loop=True, pivot=[16, 16], lift=1.0, speed=5.5, travel=7.0,
                           then="prism_pop", glow=True, light={"color": "flower_blue", "intensity": 4, "range": 3.5, "curve": [1, 1, 1, 1, 1, 1]}, combat=True),
        "prism_pop": dict(fn=prism_pop, kind="billboard", fps=14, loop=False, pivot=[16, 31], lift=0.0, glow=True,
                          light={"color": "flower_blue", "intensity": 5, "range": 3.0, "curve": [1, 0.8, 0.5, 0.3, 0.1, 0]}, combat=True),
        "drain_nova": dict(fn=drain_nova, kind="decal", fps=12, loop=False, pivot=[16, 16], lift=0.03, glow=True, light=None, combat=True),
    }
