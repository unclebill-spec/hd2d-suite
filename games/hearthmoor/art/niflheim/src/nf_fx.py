"""Niflheim gamefx (48 px cells, hd2d portal format via hmart.write_fx; one atlas gamefx/nf_fx.png). Neon on fx only (flagged in README).
Environment: cold / teal / aurora / violet pools, aurora, cold fire, glow orbs, fireflies + wisps, glowing icicle vines + crystals, surreal glow fog,
mist, ice sparkles, frost runes, spring bubbles, lantern float, Eira's memory outline. Spells / boss: ice lance, frost nova, mist veil, mist-clone puff,
portal freeze / thaw, cold-fire beam + red ring telegraph, Veyra grief-crack, breath fog + shadow (her tell), lantern colour change, Kael bite ring + bat split +
banner burn, Colossus slam ring / ice-block throw / core pulse / spirit swarm. The environment set builds on the Jotunheim fx code (jt_fx_base.py)."""
import math, random
import nf_common as C
import jt_fx_base as J
import mp_fx_base as M
H = C.H
CELL = 48
H.ALLC.update({"nf_mist": "#b8c8e4", "nf_mist_hi": "#e4eeff", "nf_mist_lo": "#6a7ea8", "nf_dk": "#0c1220", "nf_snow": "#c8d6ec"})
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
    """ground shadow of the real Veyra: a dithered dark ellipse (clones have none)"""
    F = H.Fx(CELL)
    for y in range(CELL):
        for x in range(CELL):
            d = math.hypot((x - 23.5) / 20, (y - 23.5) / 8)
            if d < 1 and ((x + y) % 2 == 0 or d < .55):
                F.set(x, y, "nf_dk")
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


def pools(c, seed, lo=22):
    return lambda: H.pool_frames(c, CELL, 6, seed, rmax=lo)


H.ALLC.update({"nf_tealx": "#2fd0d0"})
FX = {}


def add(name, fn, fps, kind, lift, pivot, notes, **kw):
    FX[name] = {"fn": fn, "fps": fps, "kind": kind, "lift": lift, "pivot": pivot, "notes": notes, **kw}


# --- pools and light (decals: lay them under props / at lamps; keep off spawns, stairs, ledge edges)
add("pool_cold", pools(NB, "nf_cold"), 4, "decal", 0.02, [24, 24], "cold-blue pool under lantern posts, cold braziers, rune stones (r ~ 4 m)")
add("pool_teal", pools(TE, "nf_teal"), 4, "decal", 0.03, [24, 24], "bioluminescent teal pool over glow_ice_pool / springs / frozen lake")
add("pool_aurora", pools(AG, "nf_aur"), 3, "decal", 0.02, [24, 24], "aurora-green pool on the snow (night)")
add("pool_violet", lambda: H.neon_pool_frames("violet", CELL, 6, rmax=20), 4, "decal", 0.02, [24, 24], "violet pool: Eira's lamps, violet accents, aurora spill")
add("pool_warm", lambda: H.pool_frames(("lamp", "flower_gold", "roof_hi"), CELL, 6, "nf_warm", rmax=18), 4, "decal", 0.02, [24, 24], "warm lantern / window pool (Bill: gloom AND glow, keep a warm accent every 6-8 m)")
# --- ambient
add("aurora_glow", J.aurora, 4, "billboard", 5.0, [24, 24], "green-to-violet aurora curtain, 8-frame ribbon, night sky layer (tile horizontally); Crown of Ice sky")
add("cold_flame", J.flame, 10, "billboard", 0.1, [24, 44], "cold-fire flame (no heat): lantern posts, braziers, Spire halls", light={"color": "neon_blue", "intensity": 1.0, "range": 4.0, "pool": "pool_cold"})
add("violet_flame", lambda: M.flame(NV), 10, "billboard", 0.1, [24, 44], "violet flame: Eira's lamps, Veyra's lantern (phase 1-3)", light={"color": "neon_violet", "intensity": 0.9, "range": 3.5, "pool": "pool_violet"})
add("ice_sparkles", J.sparkles, 6, "billboard", 0.8, [24, 47], "twinkling ice sparkles over snow, ice and crystals")
add("neon_fireflies_blue", J.fireflies(NB, 3), 6, "billboard", 0.8, [24, 47], "cold-blue fireflies / wisps over the shore")
add("neon_fireflies_green", J.fireflies(NG, 5), 6, "billboard", 0.8, [24, 47], "green wisps (iceglow, aurora archive)")
add("neon_fireflies_violet", J.fireflies(NV, 4), 6, "billboard", 0.8, [24, 47], "violet wisps (Eira's grave, Crown of Ice)")
add("glow_vines", J.vines, 4, "billboard", 3.0, [24, 0], "glowing icicle vines, hang from cave / hall ceilings (pivot at top)")
add("glow_crystals_blue", lambda: M.crystals(NB), 4, "billboard", 3.0, [24, 0], "hanging cold-blue glow crystals (iceglow, Spire halls)")
add("glow_crystals_violet", lambda: M.crystals(NV), 4, "billboard", 3.0, [24, 0], "hanging violet crystals (sister's glass, archive)")
add("glow_fog", J.fog, 3, "decal", 0.05, [24, 24], "surreal glowing ground fog (teal); one per 6-8 m, off stairs and spawns")
add("mist_drift", mist(MI, 41), 3, "decal", 0.05, [24, 24], "Mistmere's pale ground mist (not neon), drifting; the signature of the hub; off stairs and spawns")
add("mist_violet", mist(NV, 43, 6), 3, "decal", 0.05, [24, 24], "violet mist halo: Mist-alpha, Veyra's mist phase, Eira's memory")
add("rune_pulse", J.rune_pulse, 2, "decal", 0.03, [24, 24], "frost-rune ring pulse (every 3 s), brighter when the hero is near; floor of rune locks")
add("spring_bubbles", M.spring_bubbles, 6, "billboard", 0.0, [24, 44], "clear bubbling spring: fizz + steam over a teal pool (never murky)")
add("lantern_float", lantern_float, 6, "billboard", 1.6, [24, 22], "Frost Vigil lantern floating up: cold-fire lantern + mote trail", light={"color": "neon_blue", "intensity": 0.8, "range": 3.5, "pool": "pool_cold"})
add("eira_outline", eira_outline, 6, "billboard", 0.0, [24, 38], "Eira's memory: glowing violet outline of a 1x person; put it over the (hidden) eira sprite or alone; memories only", light={"color": "neon_violet", "intensity": 0.7, "range": 3.0, "pool": "pool_violet"})
add("snow_puff", J.snow_puff, 8, "billboard", 0.0, [24, 44], "snow puff (footfalls, falls)", loop=False)
for _c in ("blue", "green", "violet"):
    add(f"glow_orb_{_c}", (lambda c=_c: H.glow_orb_frames(c, CELL)), 6, "billboard", 1.4, [24, 33], "floating glow orb, hover 1.1-2.2 m",
        light={"color": f"neon_{_c}_hi", "intensity": 0.7, "range": 3.0, "pool": {"blue": "pool_cold", "green": "pool_aurora", "violet": "pool_violet"}[_c]})
# --- spells / boss fx
add("ice_lance", ice_lance, 12, "billboard", 0.9, [24, 24], "Hrefna's / Ice Warden's ice lance: flies right (flip for left); 6 frames, loop while flying")
add("frost_nova", ring_decal(NB, 6, 20, runes=6), 10, "decal", 0.03, [24, 24], "frost nova ring (Hrefna, Colossus golems, Veyra P2); hits at frames 4-6", loop=False)
add("mist_veil", mist_puff(MI, 6), 8, "billboard", 0.2, [24, 30], "Hrefna's mist veil: a soft mist puff around the caster (dodge)", loop=False)
add("mist_clone_puff", mist_puff(("nf_mist_hi", "nf_mist"), 6, ring=True), 8, "billboard", 0.2, [24, 30], "Veyra mist clone appears / vanishes: pale puff with a violet ring", loop=False)
add("portal_freeze", portal(False), 8, "billboard", 1.8, [24, 24], "Veyra P2: a frozen portal ice-over; scale to the portal (3 m)", loop=False)
add("portal_thaw", portal(True), 8, "billboard", 1.8, [24, 24], "a frozen portal thawing (ending / Hrefna's key); violet opens up", loop=False)
add("coldfire_beam", coldfire_beam, 12, "billboard", 1.5, [0, 24], "Veyra P3 cold-fire beam: tile right from her hand; telegraph with beam_ring first")
add("beam_ring", ring_decal(NR, 12, 4, n=6, runes=8), 8, "decal", 0.03, [24, 24], "RED ring telegraph shown 2 s before a beam / slam (the red is the danger signal)", loop=False)
add("grief_crack", grief_crack, 8, "decal", 0.03, [24, 24], "Veyra P3 grief-crack in the floor: red cracks spreading, then a damaging burst", loop=False)
add("breath_fog", breath_fog, 6, "billboard", 3.6, [24, 24], "Veyra's breath: white puffs at head height (real Veyra only; mist clones have no breath)")
add("veyra_shadow", veyra_shadow, 1, "decal", 0.02, [24, 24], "Veyra's ground shadow (real Veyra only; clones cast none): scale ~2.5x")
add("lantern_change", lantern_change, 8, "billboard", 0.5, [24, 40], "ending: Veyra's lantern turns from violet to white", loop=False)
add("kael_bite", ring_decal(NR, 4, 14, n=6, runes=2), 10, "decal", 0.03, [24, 24], "Kael's cold-bite ring (red); drains warmth", loop=False)
add("bat_split", bat_split, 10, "billboard", 0.4, [24, 28], "Kael phase 2: splits into three bat forms (and back)", loop=False)
add("banner_burn", banner_burn, 10, "billboard", 0.8, [24, 42], "Kael phase 3: the red banners burn (F2 / F9)")
add("colossus_slam", ring_decal(("white", "sky", "flower_blue") if False else NB, 4, 22, n=8, runes=8), 12, "decal", 0.03, [24, 24], "Colossus slam ring (scale 3x); hit at frames 5-7", loop=False)
add("ice_block", ice_block, 10, "billboard", 1.0, [24, 24], "thrown ice block (Colossus / ice golem), tumbling; 6 frames loop")
add("core_pulse", core_pulse, 10, "billboard", 3.2, [24, 24], "Colossus core pulse over the chest; phase 2 exposes it: pulse while vulnerable")
add("spirit_swarm", spirit_swarm, 10, "billboard", 1.0, [24, 30], "Colossus phase 3: frost spirits swirl round him (decorative; the live spirits are enemies)")
