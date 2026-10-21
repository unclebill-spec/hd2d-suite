"""Asgard gamefx (Niflheim fx engine reused for mist/ring/flame helpers) (48 px cells, hd2d portal format via hmart.write_fx; one atlas gamefx/as_fx.png). Neon on fx only (flagged in README).
Environment: cold / teal / aurora / violet pools, aurora, cold fire, glow orbs, fireflies + wisps, glowing icicle vines + crystals, surreal glow fog,
mist, ice sparkles, frost runes, spring bubbles, lantern float, Eira's memory outline. Spells / boss: ice lance, frost nova, mist veil, mist-clone puff,
portal freeze / thaw, cold-fire beam + red ring telegraph, Veyra grief-crack, breath fog + shadow (her tell), lantern colour change, Kael bite ring + bat split +
banner burn, Colossus slam ring / ice-block throw / core pulse / spirit swarm. The environment set builds on the Jotunheim fx code (jt_fx_base.py)."""
import math, random
import as_common as C
import jt_fx_base as J
import mp_fx_base as M
H = C.H
CELL = 48
H.ALLC.update({"as_shade": "#5a5068", "as_shade_hi": "#7a7090", "as_gold": "#ffc85a", "as_gold_hi": "#fff0c0", "as_gold_lo": "#b07a2a", "as_rain": "#8aa0c8", "nf_mist": "#b8c8e4", "nf_mist_hi": "#e4eeff", "nf_mist_lo": "#6a7ea8", "nf_dk": "#0c1220", "nf_shade": "#2c5a60", "nf_ash": "#5e6e74", "nf_snow": "#c8d6ec"})
NB, NV, NR, NG, TE, AG = J.NB, J.NV, M.NR, J.NG, J.TE, J.AG
MI = ("nf_mist_hi", "nf_mist", "nf_mist_lo")


def mist(tint=None, seed=41, n=7):
    r = random.Random(seed)
    blobs = [(r.uniform(6, 42), r.uniform(10, 38), r.uniform(8, 15), r.uniform(0, 6.28)) for _ in range(n)]
    jit = [[r.random() for _ in range(CELL)] for _ in range(CELL)]
    cols = tint or MI
    def f():
        out = []
        for k in range(8):
            F = H.Fx(CELL)
            for y in range(CELL):
                for x in range(CELL):
                    dens = 0
                    for (bx, by, br, ph) in blobs:
                        X, Y = bx + math.cos(k / 8 * math.tau + ph) * 3, by + math.sin(k / 8 * math.tau * 2 + ph) * 1.5
                        dens += max(0, 1 - math.hypot(x - X, (y - Y) * 1.6) / br) ** 1.3
                    if dens > .12 and ((x + y + k) % 2 == 0) and jit[y][x] < dens * .9:
                        F.set(x, y, cols[0] if dens > .6 else cols[1] if dens > .3 else cols[2])
            out.append(F)
        return out
    return f


def mist_puff(cols=MI, n=6, ring=False):
    def f():
        out = []
        for k in range(n):
            F = H.Fx(CELL)
            for j in range(8):
                ang = j * math.tau / 8 + .3
                rr = 4 + k * (3.0 if ring else 2.4)
                x, y = 24 + math.cos(ang) * rr, 30 + math.sin(ang) * rr * .6 - k * .6
                if k < n - 1:
                    F.disk(x, y, 3.2 - k * .4, list(cols))
            if ring:
                F.ring(24, 30, 6 + k * 3, (6 + k * 3) * .6, NV[0], dots=2)
            out.append(F)
        return out
    return f


def lantern_float():
    """Frost Vigil lantern: a lantern floating up with a trail of cold-fire motes (pivot at the lantern)"""
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        cy = 22 + [0, 0, 1, 1, 0, 0, -1, -1][k]
        F.line(24, cy - 7, 24, cy - 11, "stone_lo")
        for y in range(cy - 6, cy + 6):
            for x in (21, 22, 23, 24, 25, 26, 27):
                F.set(x, y, "stone_lo" if x in (21, 27) or y in (cy - 6, cy + 5) else "neon_blue")
        for y in range(cy - 4, cy + 4):
            F.set(24, y, "white"); F.set(23, y, "neon_blue_hi"); F.set(25, y, "neon_blue_hi")
        for j in range(5):
            b = (k + j * 2) % 8
            F.set(24 + math.sin(b + j) * 3, cy + 8 + b * 2.3, NB[0] if b < 5 else NB[2])
        out.append(F)
    return out


def eira_outline():
    """Eira's memory glow: a 1x-person outline made of violet / white dots, shimmering (pivot at the feet; scale 1x ~ 16 x 29 px at 48 cell)"""
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        pts = [(24, 8)]
        for a in range(0, 360, 20):
            pts.append((24 + math.cos(math.radians(a)) * 4, 11 + math.sin(math.radians(a)) * 4.5))
        for y in range(15, 38):
            w = 5.5 if y < 27 else 3.6
            pts += [(24 - w, y), (24 + w, y)] if (y + k) % 2 == 0 else []
        for x in range(19, 30):
            pts.append((x, 38 if (x + k) % 2 == 0 else 37.5))
        for (x, y) in pts:
            F.set(x, y, NV[1] if (int(x) + int(y) + k) % 3 else NV[0])
        for j in range(4):
            b = (k + j * 2) % 8
            F.set(20 + j * 3, 36 - b * 3.5, "white")
        out.append(F)
    return out


def ice_lance():
    """ice lance projectile, flying right (flip for left): a long white / blue spear with a dotted trail"""
    out = []
    for k in range(6):
        F = H.Fx(CELL)
        x0 = 8 + k * 4
        for dx in range(0, 18):
            w = max(0, 2 - dx // 7)
            for dy in range(-w, w + 1):
                F.set(x0 + dx, 24 + dy, "white" if dx > 12 or dy == 0 else NB[0] if dy < 0 else NB[1])
        F.set(x0 + 18, 24, "white")
        for j in range(5):
            F.set(x0 - 2 - j * 2, 24 + (j % 2 * 2 - 1), NB[1] if j < 3 else NB[2])
        out.append(F)
    return out


def ring_decal(cols, base, grow, n=8, runes=0):
    def f():
        out = []
        for k in range(n):
            F = H.Fx(CELL)
            a = base + grow * k / (n - 1)
            F.ring(23.5, 23.5, a, a * .62, cols[1], dots=1)
            F.ring(23.5, 23.5, a * .78, a * .48, cols[0], dots=3, start=k * .3)
            for j in range(runes):
                ang = j * math.tau / runes + k * .08
                F.star(23.5 + math.cos(ang) * a, 23.5 + math.sin(ang) * a * .62, 1, "white", cols[0])
            out.append(F)
        return out
    return f


def portal(thaw):
    """a frozen portal: a ring of runes that freezes shut (white ice grows inward) or thaws (violet opens), billboard facing the camera"""
    def f():
        out = []
        for k in range(8):
            F = H.Fx(CELL)
            t = k / 7 if not thaw else 1 - k / 7
            F.ring(24, 24, 18, 18, NB[1], dots=1)
            F.ring(24, 24, 15, 15, NV[1] if thaw else NB[0], dots=2, start=k * .2)
            F.disk(24, 24, 14 * t, ["white", "nf_mist_hi", "nf_mist"]) if t > .05 else None
            for j in range(8):
                ang = j * math.tau / 8
                F.star(24 + math.cos(ang) * 18, 24 + math.sin(ang) * 18, 1, "white", NB[0])
            out.append(F)
        return out
    return f


def coldfire_beam():
    """Veyra's cold-fire beam, sweeping right (a horizontal beam with a white core, frost crackle); the red ring decal marks the target first"""
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        for x in range(0, CELL):
            wob = math.sin(x * .5 + k) * 1.2
            for dy in range(-5, 6):
                d = abs(dy - wob) / 5
                if d < .2:
                    F.set(x, 24 + dy, "white")
                elif d < .5:
                    F.set(x, 24 + dy, NB[0])
                elif d < .85 and (x + dy + k) % 2 == 0:
                    F.set(x, 24 + dy, NB[1])
        out.append(F)
    return out


def grief_crack():
    out = []
    r = random.Random(7)
    arms = []
    for j in range(7):
        a = j * math.tau / 7 + .3; pts = []
        x, y = 24, 24
        for s in range(11):
            a += r.uniform(-.35, .35); x += math.cos(a) * 2; y += math.sin(a) * 1.3; pts.append((x, y))
        arms.append(pts)
    for k in range(8):
        F = H.Fx(CELL)
        n = min(11, 2 + k * 2)
        for pts in arms:
            for (x, y) in pts[:n]:
                F.set(x, y, NR[1]); F.set(x + 1, y, NR[2])
            if pts[:n]:
                F.set(*pts[n - 1], "white" if k < 7 else NR[0])
        out.append(F)
    return out


def breath_fog():
    """Veyra's breath: a few white puffs at head height; the real Veyra has this, her mist clones do not"""
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        for j in range(3):
            t = ((k / 8) + j * .33) % 1
            F.disk(24 + t * 12, 24 - t * 6 + math.sin(j) * 2, 1.5 + t * 3, ["nf_mist_hi", "nf_mist"] if t < .7 else ["nf_mist"])
        out.append(F)
    return out


def veyra_shadow():
    """ground shadow of the real Veyra (clones have none). Oct 19 2026: redrawn lighter (was a near-black #0c1220 ellipse that vanished into the dark
    ice floors and failed check_scene gamefx_sharp): a dark-teal core with an ash-grey dithered rim and a thin frost edge, readable on dark and pale floors."""
    F = H.Fx(CELL)
    for y in range(CELL):
        for x in range(CELL):
            d = math.hypot((x - 23.5) / 20, (y - 23.5) / 8)
            if d >= 1:
                continue
            if d < .5:
                F.set(x, y, "nf_shade")                                   # solid dark-teal core
            elif d < .78:
                F.set(x, y, "nf_shade" if (x + y) % 2 == 0 else "nf_ash")  # teal / ash checker
            elif d < .92:
                if (x + y) % 2 == 0: F.set(x, y, "nf_ash")                 # ash-grey dithered rim
            elif (x * 3 + y) % 4 == 0:
                F.set(x, y, "nf_mist_lo")                                 # a sparse frost edge
    return [F] * 4


def lantern_change():
    """Veyra's lantern: violet flame turns white (ending A) - 8 frames cross-fade, pivot at the flame"""
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        t = k / 7
        cols = NV if t < .5 else NB
        for y in range(18, 40):
            w = max(0, 5 * math.sin(math.pi * (40 - y) / 24) ** .7)
            for dx in range(-int(w), int(w) + 1):
                d = abs(dx) / max(w, 1)
                F.set(24 + dx, y, "white" if d < .25 + t * .2 else cols[0] if d < .55 else cols[1])
        for j in range(4):
            F.set(24 + math.sin(k + j * 2) * 9, 8 + (k * 3 + j * 7) % 14, "white" if t > .5 else NV[0])
        out.append(F)
    return out


def bat_split():
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        t = k / 7
        for j in range(3):
            ang = j * math.tau / 3 + .5
            x, y = 24 + math.cos(ang) * 14 * t, 26 + math.sin(ang) * 9 * t - 4 * t
            F.line(x - 4, y, x - 1, y - 2, NV[1]); F.line(x + 4, y, x + 1, y - 2, NV[1]); F.set(x, y, "white"); F.set(x, y - 1, NV[0])
        F.disk(24, 28, 8 * (1 - t) + 1, [NV[0], NV[1], NV[2]]) if t < .9 else None
        out.append(F)
    return out


def banner_burn():
    out = []
    r = random.Random(5)
    for k in range(8):
        F = H.Fx(CELL)
        for x in range(14, 34):
            top = 40 - (x % 5) * 3 - k % 3 * 2 - (4 if (x + k) % 4 == 0 else 0)
            for y in range(int(top), 42):
                F.set(x, y, NR[1] if y > top + 4 else NR[0] if y > top + 1 else "white")
        for j in range(5):
            F.set(14 + r.randrange(20), 6 + (k * 4 + j * 5) % 14, NR[0])
        out.append(F)
    return out


def ice_block():
    """ice block thrown by the Colossus / ice golem: a tumbling glacier chunk (pivot centre)"""
    out = []
    for k in range(6):
        F = H.Fx(CELL)
        a = k * .5
        pts = [(math.cos(a + q * 1.57) * 9, math.sin(a + q * 1.57) * 9) for q in range(4)]
        F.disk(24, 24, 9, ["white", "sky", "flower_blue"], sq=1)
        for (px, py) in pts:
            F.line(24, 24, 24 + px * .8, 24 + py * .8, "cloth")
        F.set(21, 20, "white"); F.set(22, 20, "white")
        out.append(F)
    return out


def core_pulse():
    """Colossus core pulse (put over the chest): the white core with a ring flaring out"""
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        a = 6 + k * 1.6
        F.ring(24, 24, a, a, NB[1], dots=2)
        F.disk(24, 24, 5 + (k % 4 == 1), ["white", NB[0], NB[1]])
        for j in range(6):
            ang = j * math.tau / 6 + k * .2
            F.star(24 + math.cos(ang) * (a + 2), 24 + math.sin(ang) * (a + 2), 1, "white", NB[0])
        out.append(F)
    return out


def spirit_swarm():
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        for j in range(6):
            a = k / 8 * math.tau + j * 1.05
            x, y = 24 + math.cos(a) * (10 + j % 3 * 3), 26 + math.sin(a) * (7 + j % 2 * 3)
            for dy in range(0, 5):
                w = max(0, 2 - dy * .5)
                for dx in range(-int(w), int(w) + 1):
                    F.set(x + dx, y - dy, NB[0] if dy < 2 else NB[1])
            F.set(x, y - 1, "white")
        out.append(F)
    return out


def coloursweep():
    return None



GO = ("as_gold_hi", "as_gold", "as_gold_lo")


def bolt_path(seed, x0, y0, x1, y1, n=9, jit=3.0):
    r = random.Random(seed); pts = [(x0, y0)]
    for j in range(1, n):
        t = j / n; pts.append((x0 + (x1 - x0) * t + r.uniform(-jit, jit), y0 + (y1 - y0) * t + r.uniform(-jit * .5, jit * .5)))
    pts.append((x1, y1)); return pts


def draw_bolt(F, pts, core="white", glow=None):
    glow = glow or NB[0]
    for (a, b) in zip(pts, pts[1:]):
        F.line(a[0] + 1, a[1], b[0] + 1, b[1], glow); F.line(a[0], a[1], b[0], b[1], core)


def lightning_arc():
    """rune lightning arcing left->right between two pillars / hands (tile or scale on x); 3 flicker frames + 1 blank"""
    out = []
    for k in range(4):
        F = H.Fx(CELL)
        if k < 3:
            draw_bolt(F, bolt_path(k * 11 + 3, 0, 24, 47, 24, 10, 5)); draw_bolt(F, bolt_path(k * 7 + 50, 10, 24, 38, 18 + k * 4, 5, 3), NB[0], NV[0])
        out.append(F)
    return out


def strike_bolt():
    """a lightning strike from the sky (pivot at the ground): flash, bolt, fade; pair with strike_warning"""
    out = []
    for k in range(6):
        F = H.Fx(CELL)
        if 1 <= k <= 3:
            pts = bolt_path(k, 24, 0, 24, 46, 10, 4); draw_bolt(F, pts)
            if k == 1:
                draw_bolt(F, bolt_path(9, 24, 18, 36, 34, 4, 2), NB[0], NV[0])
            F.disk(24, 45, 5 - k, ["white", NB[0], NB[1]])
        elif k > 3:
            F.disk(24, 45, 2, [NB[1]])
        out.append(F)
    return out


def chain_lightning():
    """chain lightning hopping across three points (G4 storm pillars, Sentinel P2)"""
    pts3 = [(4, 30), (24, 14), (44, 32)]
    out = []
    for k in range(6):
        F = H.Fx(CELL)
        for j in range(min(2, k // 2 + 1)):
            a, b = pts3[j], pts3[j + 1]; draw_bolt(F, bolt_path(k * 5 + j, a[0], a[1], b[0], b[1], 7, 3))
        for (x, y) in pts3:
            F.star(x, y, 1, "white", NB[0])
        out.append(F)
    return out


def rune_beam():
    """Sentinel / rune-golem beam to the right (tile on x); telegraph with beam_ring (red) first"""
    out = []
    for k in range(6):
        F = H.Fx(CELL)
        for x in range(CELL):
            wob = math.sin(x * .6 + k * 1.3)
            for dy in range(-4, 5):
                d = abs(dy - wob) / 4
                if d < .25:
                    F.set(x, 24 + dy, "white")
                elif d < .6:
                    F.set(x, 24 + dy, NB[0])
                elif (x + dy + k) % 2 == 0:
                    F.set(x, 24 + dy, NV[0] if (x // 6 + k) % 2 else NB[1])
        out.append(F)
    return out


def telegraph_line():
    """red line telegraph along the beam path (decal, tile on x), blinks"""
    out = []
    for k in range(4):
        F = H.Fx(CELL)
        for x in range(0, CELL, 1 if k % 2 == 0 else 2):
            F.set(x, 23, NR[1]); F.set(x, 24, NR[0]); F.set(x, 25, NR[1])
        out.append(F)
    return out


def gold_dust():
    r = random.Random(77); motes = [(r.uniform(2, 46), r.uniform(4, 44), r.uniform(0, 6.28)) for _ in range(9)]
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        for (x, y, ph) in motes:
            yy = (y - k * 1.5) % 46 + 1; xx = x + math.sin(ph + k * .7) * 1.5
            F.set(xx, yy, "as_gold_hi" if (k + int(ph * 3)) % 3 == 0 else "as_gold")
        out.append(F)
    return out


def rain():
    r = random.Random(5); drops = [(r.uniform(0, 48), r.uniform(0, 48)) for _ in range(14)]
    out = []
    for k in range(6):
        F = H.Fx(CELL)
        for (x, y) in drops:
            yy = (y + k * 8) % 48
            F.line(x, yy, x - 1, yy + 4, "as_rain")
        out.append(F)
    return out


def dawn_flame(cols=GO):
    def f():
        out = []
        for k in range(8):
            F = H.Fx(CELL)
            for y in range(14, 42):
                w = max(0, 7 * math.sin(math.pi * (42 - y) / 28) ** .7 + math.sin(y * .5 + k) * .8)
                for dx in range(-int(w), int(w) + 1):
                    d = abs(dx) / max(w, 1)
                    F.set(24 + dx, y, "white" if d < .3 and y > 26 else cols[0] if d < .55 else cols[1] if d < .85 else cols[2])
            for j in range(4):
                F.set(24 + math.sin(k + j * 2) * 8, 6 + (k * 3 + j * 7) % 12, cols[0])
            out.append(F)
        return out
    return f


def light_drain():
    """Aurelion drinks a lamp: gold motes streaming from the right (lamp) into the left (him); place between them, flip as needed"""
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        for j in range(10):
            t = ((k / 8) + j / 10) % 1
            x = 44 - t * 40; y = 24 + math.sin(t * 6 + j) * 6 * (1 - t)
            F.set(x, y, "as_gold_hi" if j % 3 else "white"); F.set(x + 1, y, "as_gold")
        out.append(F)
    return out


def relight_burst():
    out = []
    for k in range(8):
        F = H.Fx(CELL); a = 3 + k * 2.6
        F.ring(24, 24, a, a, "as_gold", dots=1); F.disk(24, 24, max(0, 8 - k), ["white", "as_gold_hi", "as_gold"])
        for j in range(8):
            ang = j * math.tau / 8
            F.star(24 + math.cos(ang) * (a + 2), 24 + math.sin(ang) * (a + 2), 1, "white", "as_gold")
        out.append(F)
    return out


def as_shadow():
    """ground shadow decal (the real Aurelion / real foes; P2 wraith copies cast none). MID-DARK by rule (Oct 19 2026): #5a5068 core, #7a7090 dithered rim, no near-black."""
    F = H.Fx(CELL)
    for y in range(CELL):
        for x in range(CELL):
            d = math.hypot((x - 23.5) / 20, (y - 23.5) / 8)
            if d >= 1:
                continue
            if d < .55:
                F.set(x, y, "as_shade")
            elif d < .82:
                F.set(x, y, "as_shade" if (x + y) % 2 == 0 else "as_shade_hi")
            elif (x + y) % 2 == 0:
                F.set(x, y, "as_shade_hi")
    return [F] * 4


def wraith_split():
    out = []
    for k in range(8):
        F = H.Fx(CELL); t = k / 7
        for j in range(3):
            ang = j * math.tau / 3 - math.pi / 2
            x, y = 24 + math.cos(ang) * 16 * t, 26 + math.sin(ang) * 10 * t
            F.disk(x, y, 3, ["white", "as_gold_hi"])
        F.disk(24, 26, 9 * (1 - t) + 1, ["white", "as_gold_hi", "as_gold"]) if t < .9 else None
        out.append(F)
    return out


def tile_flash():
    """G5 Throne of Trials floor: one 48 px tile flashing gold (safe) - tint red with the beam_ring colours for unsafe; 4-frame blink"""
    out = []
    for k in range(4):
        F = H.Fx(CELL)
        c = ["as_gold_hi", "as_gold", "as_gold_lo", None][k]
        if c:
            for y in range(4, 44):
                for x in range(4, 44):
                    if x in (4, 43) or y in (4, 43) or (x + y) % 4 == 0:
                        F.set(x, y, c)
        out.append(F)
    return out


def sigrun_wings():
    """Sigrun's valkyrie wings (overlay on the sigrun sprite back; 6-frame beat). Gold feathers with a neon-blue edge (fx neon, not the sprite)."""
    out = []
    for k in range(6):
        F = H.Fx(CELL); lift = math.sin(k / 6 * math.tau) * 5
        for sx in (-1, 1):
            for j in range(6):
                x0 = 24 + sx * (3 + j * 3); y0 = 24 - lift * j / 5 - j
                F.line(x0, y0, x0, y0 + 12 - j, "as_gold" if j % 2 else "as_gold_hi")
                F.set(x0, y0 - 1, NB[0])
        out.append(F)
    return out


def dive_strike():
    """Sigrun's dive strike: gold streak downward-right ending in a spark ring"""
    out = []
    for k in range(6):
        F = H.Fx(CELL)
        e = min(5, k + 2) * 8
        F.line(6, 4, 6 + e * .8, 4 + e * .8, "as_gold"); F.line(7, 4, 7 + e * .8, 4 + e * .8, "white")
        if k >= 4:
            F.ring(42, 42, 4 + (k - 4) * 3, 2 + (k - 4) * 2, NB[0], dots=1)
        out.append(F)
    return out


def raven_guard():
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        for j in range(2):
            a = k / 8 * math.tau + j * math.pi
            x, y = 24 + math.cos(a) * 14, 24 + math.sin(a) * 6
            F.line(x - 4, y - 1, x, y + 1, "stone"); F.line(x + 4, y - 1, x, y + 1, "stone"); F.set(x, y, NB[0])
        F.ring(24, 24, 12, 12, NB[1], dots=3, start=k * .3)
        out.append(F)
    return out


def pools(c, seed, lo=22):
    return lambda: H.pool_frames(c, CELL, 6, seed, rmax=lo)


FX = {}


def add(name, fn, fps, kind, lift, pivot, notes, **kw):
    FX[name] = {"fn": fn, "fps": fps, "kind": kind, "lift": lift, "pivot": pivot, "notes": notes, **kw}


# --- pools and light (decals under lamps / props; keep off spawns, stairs, ledge edges)
add("pool_gold", lambda: H.pool_frames(GO, CELL, 6, "as_gold", rmax=20), 4, "decal", 0.02, [24, 24], "warm gold pool (#ffc85a) under gold lamps, orbs, braziers, windows")
add("pool_cold", pools(NB, "as_cold"), 4, "decal", 0.02, [24, 24], "neon cold-blue pool: rune pillars, rune locks, rimed lamps, storm pillars")
add("pool_violet", lambda: H.neon_pool_frames("violet", CELL, 6, rmax=20), 4, "decal", 0.02, [24, 24], "violet pool: temple stained glass, G3, dark orbs")
add("pool_red", pools(NR, "as_red", 16), 4, "decal", 0.02, [24, 24], "red glow (Aurelion P3 leaks, the Crypt); danger colour")
# --- ambient
add("gold_dust", gold_dust, 6, "billboard", 1.0, [24, 47], "drifting gold dust motes (Goldspire air, day + night)")
add("neon_fireflies_blue", J.fireflies(NB, 3), 6, "billboard", 0.8, [24, 47], "cold-blue sparks / wisps (skyfield, storm gallery)")
add("neon_fireflies_violet", J.fireflies(NV, 4), 6, "billboard", 0.8, [24, 47], "violet wisps (temple, G3)")
add("gold_flame", dawn_flame(GO), 10, "billboard", 0.1, [24, 44], "gold lamp / brazier flame", light={"color": "#ffc85a", "intensity": 1.0, "range": 4.0, "pool": "pool_gold"})
add("cold_flame", J.flame, 10, "billboard", 0.1, [24, 44], "rime-glass cold flame (dark altar, rimed lamps)", light={"color": "neon_blue", "intensity": 0.9, "range": 3.5, "pool": "pool_cold"})
add("rime_tell", ring_decal(("white", "nf_mist_hi"), 4, 6, n=6), 4, "decal", 0.03, [24, 24], "the Cold Mark: thin rime ring where Veyra's cold touched (lamps, clue points)")
add("rain", rain, 10, "billboard", 2.0, [24, 24], "thunderstorm rain (Goldspire night / storm): tile over the camera view")
add("spring_bubbles", M.spring_bubbles, 6, "billboard", 0.0, [24, 44], "gold-lit spring fizz over the marble_spring basin (with pool_gold)")
add("rune_pulse", J.rune_pulse, 2, "decal", 0.03, [24, 24], "rune ring pulse (rune locks, rune bridge lit tiles)")
for _c in ("blue", "violet"):
    add(f"glow_orb_{_c}", (lambda c=_c: H.glow_orb_frames(c, CELL)), 6, "billboard", 1.4, [24, 33], "floating glow orb, hover 1.1-2.2 m",
        light={"color": f"neon_{_c}_hi", "intensity": 0.7, "range": 3.0, "pool": {"blue": "pool_cold", "violet": "pool_violet"}[_c]})
# --- lightning / spells
add("lightning_arc", lightning_arc, 12, "billboard", 3.5, [0, 24], "rune lightning between pillars / hands; tile + scale on x (3 flicker frames + blank)", light={"color": "neon_blue", "intensity": 1.2, "range": 5.0, "pool": "pool_cold"})
add("strike_warning", ring_decal(NB, 6, 8, n=6, runes=6), 8, "decal", 0.03, [24, 24], "neon-blue ground ring 1.5 s before a lightning strike (dodge)", loop=False)
add("strike_bolt", strike_bolt, 14, "billboard", 0.0, [24, 47], "lightning strike from above (pivot at ground); after strike_warning", loop=False)
add("chain_lightning", chain_lightning, 12, "billboard", 2.0, [24, 24], "chain lightning hopping 3 points (G4 storm pillars, Sentinel P2); scale to the gap", loop=False)
add("rune_beam", rune_beam, 12, "billboard", 1.5, [0, 24], "rune / core beam to the right (tile on x); telegraph_line first")
add("telegraph_line", telegraph_line, 8, "decal", 0.03, [0, 24], "RED line telegraph along a beam path, 1.5 s (danger colour)")
add("beam_ring", ring_decal(NR, 12, 4, n=6, runes=8), 8, "decal", 0.03, [24, 24], "RED ring telegraph before slams / judgement (Aurelion, Severin)", loop=False)
add("core_pulse", core_pulse, 10, "billboard", 3.2, [24, 24], "Storm Sentinel core pulse over the chest (P2 open cavity = vulnerable)")
add("sentinel_slam", ring_decal(NB, 4, 22, n=8, runes=8), 12, "decal", 0.03, [24, 24], "Sentinel slam ring (scale 3x); hit frames 5-7", loop=False)
add("light_bolt", lambda: [f for f in ice_lance()], 12, "billboard", 0.9, [24, 24], "light bolt (inquisitor, light wraith): flies right")
add("tile_flash", tile_flash, 8, "decal", 0.02, [24, 24], "G5 Throne of Trials floor tile flash (pattern memory); scale to tile")
add("light_drain", light_drain, 10, "billboard", 2.4, [24, 24], "Aurelion drinks a lamp (G9 four lamps; pools shrink): gold motes stream to him; flip for direction")
add("dawn_flame", dawn_flame(GO), 10, "billboard", 0.1, [24, 44], "the true Dawn-Flame (crypt throne top; temple altar after return)", light={"color": "#ffc85a", "intensity": 1.4, "range": 7.0, "pool": "pool_gold"})
add("dawn_flame_red", dawn_flame((NR[0], NR[1], NR[2])), 10, "billboard", 0.1, [24, 44], "Aurelion P3 drinks the flame: it goes red", light={"color": "neon_red", "intensity": 1.0, "range": 5.0, "pool": "pool_red"})
add("relight_burst", relight_burst, 10, "billboard", 1.6, [24, 24], "relight a lamp / the Dawn-Flame comes home (gold burst)", loop=False)
add("wraith_split", wraith_split, 10, "billboard", 2.0, [24, 28], "Aurelion P2: splits into three light-wraith copies (only the real one keeps as_shadow)", loop=False)
add("as_shadow", as_shadow, 1, "decal", 0.02, [24, 24], "ground shadow (real Aurelion / real foes; copies cast none). MID-DARK #5a5068 / #7a7090, scale ~2.5x for bosses")
add("sigrun_wings", sigrun_wings, 10, "billboard", 1.2, [24, 24], "Sigrun's valkyrie wings: overlay behind the sprite (gold + neon-blue edge)")
add("dive_strike", dive_strike, 12, "billboard", 1.0, [24, 24], "Sigrun dive strike streak", loop=False)
add("raven_guard", raven_guard, 8, "billboard", 1.0, [24, 24], "Sigrun raven guard: two ravens circling the hero (defence buff)")


# ================= Helheim set (PLACEHOLDER-named; story/helheim.md missing) =================
for _k in ("pool_gold", "pool_red", "gold_dust", "gold_flame", "rain", "strike_warning", "strike_bolt", "chain_lightning", "rune_beam", "telegraph_line", "sentinel_slam",
           "light_bolt", "tile_flash", "light_drain", "dawn_flame", "dawn_flame_red", "relight_burst", "wraith_split", "as_shadow", "sigrun_wings", "dive_strike", "raven_guard",
           "lightning_arc", "rime_tell"):
    FX.pop(_k, None)
H.ALLC.update({"hh_shade": "#4a4a6a", "hh_shade_hi": "#5e6086", "hh_warm": "#ffd8a0", "hh_warm_lo": "#c09060"})


def hh_shadow():
    """MID-DARK ground shadow (#4a4a6a core, #5e6086 dither), no near-black"""
    F = H.Fx(CELL)
    for y in range(CELL):
        for x in range(CELL):
            d = math.hypot((x - 23.5) / 20, (y - 23.5) / 8)
            if d < .55:
                F.set(x, y, "hh_shade")
            elif d < .85 and (x + y) % 2 == 0:
                F.set(x, y, "hh_shade_hi")
    return [F] * 4


def wisps(cols):
    def f():
        r = random.Random(23); ws = [(r.uniform(8, 40), r.uniform(10, 40), r.uniform(0, 6.28)) for _ in range(4)]
        out = []
        for k in range(8):
            F = H.Fx(CELL)
            for (x, y, ph) in ws:
                a = k / 8 * math.tau + ph
                cx, cy = x + math.cos(a) * 4, y + math.sin(a * 2) * 2
                F.disk(cx, cy, 2, ["white", cols[0]])
                for j in range(1, 4):
                    F.set(cx - math.cos(a) * j * 1.5, cy - math.sin(a * 2) * j * .8, cols[min(j, 2)])
            out.append(F)
        return out
    return f


def spirit_burst():
    out = []
    for k in range(8):
        F = H.Fx(CELL); a = 3 + k * 2.6
        F.ring(24, 24, a, a, NV[0], dots=1); F.ring(24, 24, a * .7, a * .7, NB[0], dots=2, start=k * .3)
        F.disk(24, 24, max(0, 7 - k), ["white", NB[0], NV[0]])
        out.append(F)
    return out


def soul_rise():
    out = []
    for k in range(8):
        F = H.Fx(CELL); t = k / 7
        y = 40 - t * 30
        F.disk(24, y, 3 * (1 - t * .5), ["white", NB[0], NB[1]])
        for j in range(4):
            F.set(24 + math.sin(k + j) * 3, y + 4 + j * 2, NB[1] if j < 2 else NV[1])
        out.append(F)
    return out


add("pool_spirit", pools(NB, "hh_spirit"), 4, "decal", 0.02, [24, 24], "spirit-blue misty glow pool (lamps, pillars, pools)")
add("pool_warm", lambda: H.pool_frames(("hh_warm", "lamp", "hh_warm_lo"), CELL, 6, "hh_warm", rmax=16), 4, "decal", 0.02, [24, 24], "soft pale-warm pool (trader lamps, hearth windows): one per 6-8 m so the grade is never all blue")
add("mist_drift", mist(MI, 41), 3, "decal", 0.05, [24, 24], "pale ground mist (signature of the city); off stairs and spawns")
add("mist_violet", mist(NV, 43, 6), 3, "decal", 0.05, [24, 24], "violet mist halo (memorials, boss)")
add("glow_fog", J.fog, 3, "decal", 0.05, [24, 24], "glowing ground fog over the misty pools")
add("wisps_blue", wisps(NB), 8, "billboard", 1.2, [24, 24], "spirit-blue wisps circling (city air, pools)")
add("wisps_violet", wisps(NV), 8, "billboard", 1.2, [24, 24], "violet wisps (memorials, vault)")
add("spirit_flame", J.flame, 10, "billboard", 0.1, [24, 44], "spirit-blue flame (spirit_brazier, spirit_lamp)", light={"color": "neon_blue", "intensity": 1.0, "range": 4.0, "pool": "pool_spirit"})
add("violet_flame", lambda: M.flame(NV), 10, "billboard", 0.1, [24, 44], "violet flame (violet_lamp, memory_altar)", light={"color": "neon_violet", "intensity": 0.9, "range": 3.5, "pool": "pool_violet"})
add("spirit_burst", spirit_burst, 10, "billboard", 1.6, [24, 24], "spirit burst (boss cast, wraith death)", loop=False)
add("soul_rise", soul_rise, 8, "billboard", 0.3, [24, 44], "a freed soul rising (wraith die, memorial ring); gentle, not creepy", loop=False)
add("warden_slam", ring_decal(NB, 4, 22, n=8, runes=8), 12, "decal", 0.03, [24, 24], "Hel-Warden / Ferryman slam ring (scale 3x); hits frames 5-7", loop=False)
add("hh_shadow", hh_shadow, 1, "decal", 0.02, [24, 24], "ground shadow, MID-DARK #4a4a6a / #5e6086; real boss only (shade copies have none); scale 2.5x for bosses")


# ================= Helheim doc fx (story/helheim.md 2.2, 2.7, 3, 7, 8, 9) =================
for _k in ("pool_cold", "core_pulse", "rune_pulse", "memorial", "warden_slam", "hh_shadow"):
    FX.pop(_k, None)
H.ALLC.update({"hh_lilac": "#d6b8ff", "hh_vdeep": "#3a2458", "hh_vmid": "#6a3fa8", "hh_rose": "#e8a8c8", "hh_rose_lo": "#a86890"})
LILAC = ("hh_lilac", NV[0], NV[1])


def lilac_orb():
    out = []
    for k in range(6):
        F = H.Fx(CELL); y = 30 + math.sin(k / 6 * math.tau) * 2
        F.disk(24, y, 5, ["white", "hh_lilac", NV[0]]); F.ring(24, y, 7, 7, NV[1], dots=3, start=k * .3)
        out.append(F)
    return out


def name_moths():
    """freed names rising like moths (Mordrath outro, cage break): small violet/lilac moths fluttering up"""
    r = random.Random(9); ms = [(r.uniform(8, 40), r.uniform(20, 46), r.random()) for _ in range(7)]
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        for (x, y, ph) in ms:
            yy = (y - k * 3) % 46; xx = x + math.sin(k + ph * 6) * 2; up = (k + int(ph * 4)) % 2
            F.set(xx, yy, "white"); F.set(xx - 1, yy - up, "hh_lilac"); F.set(xx + 1, yy - up, "hh_lilac")
        out.append(F)
    return out


def violet_arc():
    """Mordrath P1 glaive-sweep tell: a violet arc (1 s), decal"""
    out = []
    for k in range(6):
        F = H.Fx(CELL)
        for a in range(0, 100):
            t = a / 99; ang = math.pi * (1.1 + .8 * t)
            if t <= (k + 1) / 6:
                for rr in (18, 19, 20):
                    F.set(24 + math.cos(ang) * rr, 30 + math.sin(ang) * rr * .62, NV[0] if rr == 19 else NV[1])
        out.append(F)
    return out


def half_ring(cols=None):
    """Mordrath P3 crown flare: red telegraph over HALF the arena (left half; flip for right), 2 s"""
    out = []
    for k in range(6):
        F = H.Fx(CELL)
        for y in range(4, 44):
            for x in range(2, 24):
                d = math.hypot((x - 24) / 22, (y - 24) / 20)
                if d < 1 and ((x + y + k) % 3 == 0 or d > .9 or x == 23):
                    F.set(x, y, NR[0] if d > .9 or x == 23 else NR[1])
        out.append(F)
    return out


def soul_bolt():
    out = []
    for k in range(6):
        F = H.Fx(CELL); x0 = 8 + k * 4
        F.disk(x0 + 14, 24, 3, ["white", NV[0], NV[1]])
        for j in range(6):
            F.set(x0 + 10 - j * 2, 24 + (j % 2), NV[0] if j < 3 else NV[1])
        out.append(F)
    return out


def grave_grasp():
    out = []
    for k in range(8):
        F = H.Fx(CELL); h = min(1, k / 4) * 14
        for sx in (-1, 1):
            x = 24 + sx * 7
            F.line(x, 40, x + sx * -3, 40 - h, NV[1]); F.line(x + 1, 40, x + 1 + sx * -3, 40 - h, NV[0])
            for f in range(3):
                F.set(x + sx * -3 + (f - 1) * 2, 40 - h - 2, "hh_lilac")
        F.ring(24, 40, 12, 5, NV[1], dots=2, start=k * .2)
        out.append(F)
    return out


def bat_dash():
    out = []
    for k in range(6):
        F = H.Fx(CELL); x = 6 + k * 7
        F.line(x - 5, 24, x, 21, NV[0]); F.line(x + 5, 24, x, 21, NV[0]); F.set(x, 22, "white")
        for j in range(4):
            F.set(x - 6 - j * 3, 23 + (j % 2), NV[1])
        out.append(F)
    return out


def red_mist():
    return mist((NR[1], NR[2], "hh_vdeep"), 51, 6)()


def mid_shadow(core, rim):
    def f():
        F = H.Fx(CELL)
        for y in range(CELL):
            for x in range(CELL):
                d = math.hypot((x - 23.5) / 20, (y - 23.5) / 8)
                if d < .55:
                    F.set(x, y, core)
                elif d < .85 and (x + y) % 2 == 0:
                    F.set(x, y, rim)
        return [F] * 4
    return f


H.ALLC.update({"hh_shade": "#4a4060", "hh_shade_hi": "#5e5480"})
add("pool_coldfire", pools(NB, "hh_cf"), 4, "decal", 0.02, [24, 24], "neon-blue cold-fire pool under every street lamp + grave lantern (#3fb8ff)")
add("pool_window", lambda: H.neon_pool_frames("violet", CELL, 4, rmax=12), 4, "decal", 0.02, [24, 24], "small violet window spill (r 3 m) in front of every lit window")
add("pool_lilac", pools(LILAC, "hh_lil", 16), 4, "decal", 0.02, [24, 24], "lilac pool under willow orbs / soul-glass")
add("pool_red", pools(NR, "hh_red", 16), 4, "decal", 0.02, [24, 24], "RED = danger only: Vesperin, Mordrath's crown")
add("lake_shimmer", lambda: H.neon_pool_frames("violet", CELL, 6, rmax=22), 3, "decal", -0.08, [24, 24], "violet reflections on the black lake (lift -0.08)")
add("spirit_rose_mist", mist(("hh_rose", "hh_rose_lo", "nf_mist"), 47, 6), 3, "decal", 0.05, [24, 24], "spirit-rose mist at Hel's arch (arrival)")
add("gloam_fog", mist(("nf_mist_hi", "nf_mist", "hh_vmid"), 53, 8), 3, "decal", 0.05, [24, 24], "weather gloam_fog (fog 0.7): violet-grey ground fog; off stairs + spawns")
add("soul_light", J.fireflies(NV, 1), 6, "billboard", 1.2, [24, 47], "weather soul_lights: a single wandering light that leads to a secret (3 per night)")
add("soul_motes", J.fireflies(NV, 6), 6, "billboard", 0.8, [24, 47], "violet soul motes (ambient, Ledger, P3 heal motes)")
add("violet_motes", J.fireflies(LILAC, 4), 6, "billboard", 0.4, [24, 47], "Inkling's pet fx (PETS.inkling.fx = violet_motes)")
add("glow_orb_lilac", lilac_orb, 4, "billboard", 1.8, [24, 30], "lilac willow / porch orb #d6b8ff, bobs gently", light={"color": "#d6b8ff", "intensity": 0.6, "range": 3.0, "pool": "pool_lilac"})
add("cage_break", spirit_burst, 10, "billboard", 1.0, [24, 24], "name-cage breaks (os_n1..3): violet burst, then name_moths", loop=False)
add("name_moths", name_moths, 8, "billboard", 1.2, [24, 40], "freed names rise like moths (cage break, Mordrath outro)")
add("eira_outline", eira_outline, 6, "billboard", 0.0, [24, 38], "Eira's soft glowing outline over eira_spirit", light={"color": "neon_violet", "intensity": 0.6, "range": 3.0, "pool": "pool_window"})
add("hel_light", lambda: H.neon_pool_frames("violet", CELL, 2, rmax=6), 2, "billboard", 1.9, [24, 24], "Hel's half-face violet light (small, on her lit side)")
add("lantern_float", lantern_float, 6, "billboard", 0.4, [24, 22], "Lantern-Boat Night: a lantern floated on the lake", light={"color": "neon_blue", "intensity": 0.8, "range": 3.5, "pool": "pool_coldfire"})
add("glaive_arc", violet_arc, 10, "decal", 0.03, [24, 24], "Mordrath P1 glaive sweep tell: violet arc, 1 s (scale 3x)", loop=False)
add("telegraph_line", telegraph_line, 8, "decal", 0.03, [0, 24], "RED line: name-chain lash path from a chain_anchor (1.5 s)")
add("hunt_ring", ring_decal(NR, 4, 10, n=6, runes=4), 8, "decal", 0.03, [24, 24], "Mordrath P2 hunt: red ring on the player, then a lunge; Vesperin curtain tell", loop=False)
add("crown_flare", half_ring, 6, "decal", 0.03, [24, 24], "Mordrath P3 crown flare: red over HALF the arena (scale 8x, flip for the other half), 2 s", loop=False)
add("violet_smoke_wings", mist(NV, 61, 5), 6, "billboard", 4.5, [24, 24], "Mordrath's wings of violet smoke (behind his shoulders, scale 4x)")
add("ash_light", soul_rise, 8, "billboard", 0.5, [24, 44], "Mordrath / Vesperin defeat: breaks into ash-white light (no gore)", loop=False)
add("red_mist_fade", red_mist, 8, "billboard", 1.0, [24, 30], "Vesperin yields: fades into red mist", loop=False)
add("bat_dash", bat_dash, 12, "billboard", 1.6, [0, 24], "Vesperin bat-shaped mist dash (violet), flies right")
add("soul_bolt", soul_bolt, 12, "billboard", 0.9, [24, 24], "Gloam school I: Soul Bolt (violet, pierces)")
add("grave_grasp", grave_grasp, 10, "billboard", 0.0, [24, 44], "Gloam school I: Grave Grasp (spectral hands hold 2 s)", loop=False)
add("lantern_ward", ring_decal(NB, 10, 6, n=6, runes=8), 6, "decal", 0.03, [24, 24], "Gloam school II: Lantern Ward ring (shades can't enter, 6 s)")
add("cold_wisp", J.fireflies(NB, 2), 10, "billboard", 1.0, [24, 47], "gravelamp spits cold-fire wisps")
add("dirge_aura", ring_decal(NV, 10, 8, n=6), 4, "decal", 0.03, [24, 24], "hollowchoir dirge (slow aura)")
add("soul_glow", lambda: H.neon_pool_frames("blue", CELL, 4, rmax=14), 4, "billboard", 0.6, [24, 24], "soul_wraith neon-blue glow halo (behind the palette sprite)")
add("gloamreaver_mark", ring_decal(NV, 3, 3, n=4, runes=3), 8, "decal", 0.03, [24, 24], "Gloamreaver hit mark; leaves a soul mote")
add("spring_fizz", M.spring_bubbles, 6, "billboard", 0.0, [24, 44], "hidden spring fizz (hh_spring / ls_spring / os_spring), lit violet from below (with pool_window)")
add("hh_shadow", mid_shadow("hh_shade", "hh_shade_hi"), 1, "decal", 0.02, [24, 24], "ground shadow MID-DARK #4a4060 / #5e5480 (no near-black); real Vesperin + Mordrath only; scale 2.5x")
add("slam_ring", ring_decal(NV, 4, 22, n=8, runes=8), 12, "decal", 0.03, [24, 24], "Odric / garnet golem slam ring", loop=False)
