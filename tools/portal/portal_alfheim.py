"""Alfheim game effects for hd2d portal (original pixel art, Hearthmoor realm-alfheim branch).

  rift_vortex_violet  Alfheim's open realm gate: the open-gate spiral re-lit in Alfheim's violet neon (deep core,
                      violet / white prism arms, violet cold-fire tongues off the rim, white glints orbiting)
  prism_swirl         the Prism Vault's door: a tall faceted swirl of violet and pale-blue prism light with a
                      white-hot seam that sweeps down the face (billboard, loops)
  prism_ring          a broken ring of prism dashes on the ground in front of the vault door (decal, pre-squashed)

Imported by portal.py (EFFECTS.update). Same 48 px cells, hard alpha, biome palette + the named NEON accents on glowing
pixels only. Style refs (rift refs: swirling vortexes in stone arches) were ideas only; nothing is traced or copied.
"""
from __future__ import annotations

import math


def effects(Frame, h2, SQUASH, CELL):
    def rift_vortex_violet(pal, seed):
        out = []
        cx, cy, rx, ry = 23.5, 25.0, 12.5, 21.0
        for f in range(8):
            F = Frame(pal)
            ph = f / 8.0
            for y in range(CELL):
                for x in range(CELL):
                    dx, dy = (x - cx) / rx, (y - cy) / ry
                    d = math.hypot(dx, dy)
                    if d > 1.0:
                        continue
                    a = math.atan2(dy, dx)
                    s_ = (a / math.tau * 2 + math.log(d + 0.08) * 1.1 - ph) % 1.0
                    if d < 0.15:
                        c = "ink"
                    elif d < 0.32:
                        c = "neon_violet_lo" if s_ < 0.4 else "shadow"
                    elif d > 0.86:
                        c = "neon_violet" if (x + y + f) % 2 == 0 or s_ < 0.5 else "neon_violet_lo"
                    else:
                        c = ("white" if s_ < 0.08 else "neon_violet_hi" if s_ < 0.24 else "neon_violet" if s_ < 0.42
                             else "flower_blue" if s_ < 0.55 else "neon_violet_lo" if s_ < 0.7 else "shadow")
                    F.set(x, y, c)
            for k in range(12):   # violet cold-fire tongues licking up off the rim
                a = k / 12 * math.tau + ph * math.tau * 0.25
                bx, by = cx + math.cos(a) * rx, cy + math.sin(a) * ry
                hgt = 2 + int(3 * h2(k, f, seed + 5))
                for t in range(hgt):
                    F.set(bx + math.cos(a) * (t * 0.6), by + math.sin(a) * (t * 0.6) - t * 0.7, "neon_violet_hi" if t == hgt - 1 else "neon_violet")
            for k in range(6):    # glints orbiting the gate
                ang = -ph * math.tau + k * math.tau / 6
                gx, gy = cx + math.cos(ang) * (rx + 4), cy + math.sin(ang) * (ry + 3)
                if (k + f) % 3:
                    F.set(gx, gy, "white")
                    for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        F.set(gx + ddx, gy + ddy, "neon_violet_hi")
                else:
                    F.set(gx, gy, "sky")
            out.append(F)
        return out

    def prism_swirl(pal, seed):
        out = []
        cx, cy, rx, ry = 23.5, 25.5, 11.5, 20.5
        for f in range(8):
            F = Frame(pal)
            ph = f / 8.0
            seam = int((ph * 2 % 1.0) * 2 * ry)   # the white-hot seam sweeps top -> bottom twice per loop
            for y in range(CELL):
                for x in range(CELL):
                    dx, dy = (x - cx) / rx, (y - cy) / ry
                    # a faceted (diamond-ish) outline: blend of a circle and a rhombus
                    d = 0.55 * math.hypot(dx, dy) + 0.45 * (abs(dx) + abs(dy)) * 0.82
                    if d > 1.0:
                        continue
                    a = math.atan2(dy, dx)
                    facet = (int((a / math.tau + 0.5) * 8) + int(d * 4) + f) % 4
                    if d > 0.9:
                        c = "neon_violet_hi" if (x + y + f) % 3 == 0 else "neon_violet"
                    elif abs((y - (cy - ry)) - seam) < 1 and d < 0.86:
                        c = "white"
                    elif d < 0.2:
                        c = "ink" if (x + y) % 2 else "neon_violet_lo"
                    else:
                        c = ("neon_violet_lo", "shadow", "flower_blue", "neon_violet")[facet] if d < 0.6 else ("sky", "neon_violet_lo", "neon_violet", "shadow")[facet]
                    F.set(x, y, c)
            for k in range(5):    # prism motes rising
                mx = cx + (k - 2) * 4 + (1 if (f + k) % 2 else -1)
                my = cy + 16 - ((f * 4 + k * 9) % 34)
                F.set(mx, my, "white" if k % 2 else "sky")
            out.append(F)
        return out

    def prism_ring(pal, seed):
        out = []
        cx, cy = 23.5, 23.5
        for f in range(6):
            F = Frame(pal)
            for k in range(36):
                if k % 6 in (4, 5) and (k // 6 + f) % 2:
                    continue
                a = k / 36 * math.tau + f * 0.05
                for rr in (17.0, 18.0):
                    F.set(cx + math.cos(a) * rr, cy + math.sin(a) * rr * SQUASH, "neon_violet" if (k + f) % 4 else "neon_violet_hi")
            for k in range(8):   # inner prism ticks turning the other way
                a = -k / 8 * math.tau - f * 0.12
                x0, y0 = cx + math.cos(a) * 11, cy + math.sin(a) * 11 * SQUASH
                F.set(x0, y0, "sky"); F.set(x0 + math.cos(a), y0 + math.sin(a) * SQUASH, "white" if (k + f) % 3 == 0 else "flower_blue")
            out.append(F)
        return out

    return {
        "rift_vortex_violet": dict(fn=rift_vortex_violet, fps=8, loop=True, kind="billboard", pivot=[24, 47], lift=0.18, glow=True),
        "prism_swirl": dict(fn=prism_swirl, fps=8, loop=True, kind="billboard", pivot=[24, 47], lift=0.18, glow=True),
        "prism_ring": dict(fn=prism_ring, fps=6, loop=True, kind="decal", pivot=[24, 24], lift=0.03, glow=True),
    }
