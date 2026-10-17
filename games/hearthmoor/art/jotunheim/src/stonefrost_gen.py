"""Stonefrost tiers II and III spell fx (Jotunheim, Art seat). Run: python3 stonefrost_gen.py
Tier I (repo, read-only): Boulder Toss = projectile seed_bomb -> earth_burst; Frost Rune = decal rune_trap (+ glyph_burst on trigger), 32 px cells.
Tier II / III: same four slots (cast / bolt -> impact / rune trap / trap burst), 48 px cells (the portal fx format), larger and brighter per tier.
Colours: cold-blue + teal neon (glow pixels only) over stone and snow from the biome palette. Output: ../gamefx/stonefrost_fx.png/json (+strips)."""
import math, random, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import jt_common as C
import jt_fx  # registers jt_teal etc. into H.ALLC
H = C.H
CELL = 48
SQ = H.DECAL_SQUASH
OUT = HERE.parent / "gamefx"
NB = ("neon_blue_hi", "neon_blue", "neon_blue_lo")
TE = ("jt_teal_hi", "jt_teal", "jt_teal_lo")
STONE = ("stone_hi", "stone", "stone_lo")
# per tier: size scale, brightness (white-hot core), sparkle count, colour mix
T = {2: dict(s=1.0, spark=7, bolt_r=6, imp=17, ring=17, pillar=4, hi=1), 3: dict(s=1.45, spark=13, bolt_r=9, imp=22, ring=21, pillar=6, hi=2)}


def sparkle(F, x, y, big, tier):
    if big:
        F.star(x, y, 2 if tier == 3 else 1, "white", "neon_blue_hi", "jt_teal_hi")
    else:
        F.set(x, y, "white"); F.set(x + 1, y, "jt_teal_hi") if tier == 3 else None


def halo(F, cx, cy, r, k, cols, sq=1.0, step=3):
    for i in range(int(r * 6)):
        a = i / (r * 6) * math.tau + k * 0.4
        if i % step == 0:
            F.set(cx + math.cos(a) * r, cy + math.sin(a) * r * sq, cols[(i // step + k) % len(cols)])


def twinkles(F, rnd, n, k, tier, box, ph=None):
    x0, y0, x1, y1 = box
    for j in range(n):
        x, y, p = rnd[j]
        t = (k + p) % 6
        X, Y = x0 + (x1 - x0) * x, y0 + (y1 - y0) * y
        if t == 0:
            F.star(X, Y, 2 if tier == 3 else 1, "white", "neon_blue_hi", "jt_teal_hi")
        elif t == 1:
            F.star(X, Y, 1, "white", "jt_teal_hi", "neon_blue_hi")
        elif t in (2, 3):
            F.set(X, Y, "jt_teal_hi" if j % 2 else "neon_blue_hi")


def rnd_pts(seed, n):
    r = random.Random(seed)
    return [(r.random(), r.random(), r.randrange(6)) for _ in range(n)]


# ------------------------------------------------------------------ bolt: frost-rimed boulder (projectile)
def bolt(tier):
    P = T[tier]; R = P["bolt_r"]; pts = rnd_pts(tier * 7, P["spark"])
    out = []
    for k in range(6):
        F = H.Fx(CELL); cx, cy = 23.5, 23.5 + [0, -1, -1, 0, 1, 1][k] * (1 if tier == 2 else 1.5)
        halo(F, cx, cy, R + 4 + (k % 2), k, ("neon_blue_lo", "jt_teal_lo", "neon_blue_lo"), step=3)
        if tier == 3:
            halo(F, cx, cy, R + 7, k + 1, ("jt_teal", "neon_blue_lo"), step=5)
        for y in range(48):
            for x in range(48):
                dx, dy = x - cx, y - cy
                d = math.hypot(dx, dy)
                if d <= R:
                    lit = (-dx - dy) / (R * 1.4) + 0.12 * math.sin(x * .9 + y * .5 + k * .2)
                    rim = d > R - 1.6 and lit > 0.05
                    F.set(x, y, "stone_hi" if lit > .35 else "stone" if lit > -.25 else "stone_lo")
                    if rim:
                        F.set(x, y, "jt_snow")
        # frost crystals bursting out of the stone
        for j in range(5 + tier):
            a = j * math.tau / (5 + tier) + k * 0.12 + (0.4 if j % 2 else 0)
            ln = R * (0.55 + 0.35 * ((j * 7) % 3) / 2) * (1.0 + (tier - 2) * .4)
            x0, y0 = cx + math.cos(a) * (R - 1.5), cy + math.sin(a) * (R - 1.5)
            for s in range(int(ln)):
                f = s / max(1, ln - 1)
                F.set(x0 + math.cos(a) * s, y0 + math.sin(a) * s, "neon_blue_hi" if f < .5 else "neon_blue" if f < .85 else "white")
        # glowing rune scratch on the face + white-hot core spot
        F.set(cx - 1, cy, "neon_blue_hi"); F.set(cx, cy + 1, "neon_blue_hi"); F.set(cx + 1, cy - 1, "white" if k % 2 else "neon_blue_hi")
        if tier == 3:
            F.set(cx - 2, cy + 2, "jt_teal_hi"); F.set(cx + 2, cy + 1, "white")
        twinkles(F, pts, P["spark"], k, tier, (3, 3, 44, 44))
        out.append(F)
    return out


# ------------------------------------------------------------------ impact: frost + stone burst (billboard, feet pivot)
def impact(tier):
    P = T[tier]; RM = P["imp"]; pts = rnd_pts(tier * 11, P["spark"] + 3)
    rr = random.Random(tier)
    shards = [(j * math.tau / (9 + 3 * (tier - 2)) + rr.uniform(-.2, .2), rr.uniform(.7, 1.0)) for j in range(9 + 3 * (tier - 2))]
    chips = [(rr.uniform(-1, 1), rr.uniform(.5, 1)) for _ in range(6 + 3 * (tier - 2))]
    out = []
    for k in range(7):
        F = H.Fx(CELL); t = k / 6
        cx, cy = 23.5, 40 - 4 * tier
        if k < 3:   # flash
            r = (4 + k * 2.2) * (1 + (tier - 2) * .5)
            F.disk(cx, cy, r, ["white", "neon_blue_hi", "neon_blue"] if k < 2 else ["neon_blue_hi", "neon_blue", "neon_blue_lo"], sq=1.0)
        # expanding snow ring on the ground (squashed)
        ex = RM * (1 - (1 - t) ** 2) * 1.05
        if k >= 1:
            F.ring(cx, 41, ex, ex * SQ + 1, "neon_blue_hi" if k < 5 else "neon_blue_lo", dots=1 if k < 4 else 2)
            if k < 5:
                F.ring(cx, 41, ex * .7, ex * .7 * SQ + 1, "jt_teal_hi", dots=2, start=k)
        # ice shards
        for (a, l) in shards:
            r0 = 2 + ex * 0.45 * l
            ln = max(1, int(5 * (1 - t) * (1 + (tier - 2) * .6)) + (2 if k < 3 else 0))
            for s in range(ln):
                f = s / max(1, ln)
                x = cx + math.cos(a) * (r0 + s) ; y = cy + math.sin(a) * (r0 + s) * 0.9 + t * t * 6 * (1 if math.sin(a) > 0 else 0.5) - t * 2
                c = "white" if (s == ln - 1 and k < 5) else "neon_blue_hi" if f < .5 else "neon_blue"
                F.set(x, y, c); F.set(x + 1, y, c) if (tier == 3 or s < 2) else None; F.set(x, y + 1, "neon_blue_lo") if s < 3 else None
        # stone chips arc up and fall
        for i, (vx, vy) in enumerate(chips):
            x = cx + vx * RM * 0.9 * t; y = cy - vy * 16 * t * (1 + (tier - 2) * .3) + 28 * t * t * (0.6 + vy * .3)
            if k < 6 and y < 46:
                F.set(x, y, STONE[i % 3]); F.set(x + 1, y, STONE[(i + 1) % 3]) if tier == 3 else None
        # snow puff
        if k >= 2:
            for j in range(5):
                a = j * math.tau / 5 + .5
                F.disk(cx + math.cos(a) * ex * .55, 41 + math.sin(a) * ex * .25 - t * 4, max(0.6, 2.4 * (1 - t) * (1 + (tier - 2) * .4)), ["jt_snow", "jt_snow", "sky"])
        twinkles(F, pts, P["spark"] + 3, k, tier, (4, 4, 44, 42))
        out.append(F)
    return out


# ------------------------------------------------------------------ cast: floating rune sigil flare at the hands
def cast(tier):
    P = T[tier]; pts = rnd_pts(tier * 13, P["spark"]); out = []
    RM = 8 + 5 * (tier - 2) * 1.3
    for k in range(6):
        F = H.Fx(CELL); cx, cy = 23.5, 29
        a = [.35, .65, 1.0, .9, .65, .3][k]; r = RM * a
        F.ring(cx, cy, r, r, "jt_rune" if "jt_rune" in H.ALLC else "neon_blue_hi", dots=1)
        F.ring(cx, cy, r * .62, r * .62, "neon_blue_hi", dots=2, start=k * .5)
        F.ring(cx, cy, r + 3, r + 3, "jt_teal", dots=4, start=-k * .4)
        n = 6 if tier == 2 else 8
        for j in range(n):    # rune ticks
            ang = j * math.tau / n + k * 0.2
            F.set(cx + math.cos(ang) * r * 1.35, cy + math.sin(ang) * r * 1.35, "white" if j % 2 else "neon_blue_hi")
            F.set(cx + math.cos(ang) * r * .3, cy + math.sin(ang) * r * .3, "jt_teal_hi")
        # glyph: triangle (II) / hexagram (III) inside
        for tri in range(1 if tier == 2 else 2):
            for e in range(3):
                a0 = e * math.tau / 3 + k * .15 + tri * math.pi / 3 - math.pi / 2
                a1 = (e + 1) * math.tau / 3 + k * .15 + tri * math.pi / 3 - math.pi / 2
                F.line(cx + math.cos(a0) * r * .6, cy + math.sin(a0) * r * .6, cx + math.cos(a1) * r * .6, cy + math.sin(a1) * r * .6, "white" if k in (2, 3) else "neon_blue_hi")
        F.disk(cx, cy, 1.6 + (tier - 2) * .8, ["white", "neon_blue_hi"])
        # rising motes
        for j in range(5 + 3 * (tier - 2)):
            x = cx + math.sin(j * 2.1 + k * .6) * RM; y = cy + 8 - ((k * 3 + j * 5) % 24)
            F.set(x, y, "jt_teal_hi" if j % 2 else "neon_blue_hi")
        twinkles(F, pts, P["spark"], k, tier, (3, 3, 44, 44))
        out.append(F)
    return out


# ------------------------------------------------------------------ rune trap decal (pre-squashed), 8 frames, frame 5 = armed
def rune(tier):
    P = T[tier]; RX = P["ring"]; pts = rnd_pts(tier * 17, P["spark"]); out = []
    for k in range(8):
        F = H.Fx(CELL); cx, cy = 23.5, 23.5
        frac = [.25, .5, .8, 1, 1, 1, 1, 1][k]
        pul = [0, 0, 0, 0, 1, 1, 2, 2][k]
        def sring(rx, c, dots=1, start=0.0, fr=1.0):
            F.ring(cx, cy, rx, rx * SQ, c, frac=fr, start=start, dots=dots)
        sring(RX, "neon_blue_hi" if pul != 2 else "white", fr=frac, start=k * .3)
        sring(RX - 1, "neon_blue", fr=frac, start=k * .3)
        sring(RX + 2, "jt_teal", dots=3, start=-k * .25, fr=frac)
        if tier == 3:
            sring(RX * .66, "neon_blue_hi", dots=2, start=k * .4, fr=frac)
            sring(RX + 4, "neon_blue_lo", dots=4, start=k * .2, fr=frac)
        n = 6 if tier == 2 else 8
        if k >= 2:
            for j in range(n):
                a = j * math.tau / n + (0.0 if tier == 2 else .2)
                F.set(cx + math.cos(a) * (RX - 4), cy + math.sin(a) * (RX - 4) * SQ, "jt_teal_hi")
        # glyph
        g = RX * .62
        for tri in range(1 if tier == 2 else 2):
            for e in range(3):
                a0 = e * math.tau / 3 + tri * math.pi / 3 - math.pi / 2
                a1 = (e + 1) * math.tau / 3 + tri * math.pi / 3 - math.pi / 2
                F.line(cx + math.cos(a0) * g, cy + math.sin(a0) * g * SQ, cx + math.cos(a1) * g, cy + math.sin(a1) * g * SQ,
                       "white" if (k >= 3 and (k + e) % 3 != 0) else "neon_blue_hi") if k >= 2 else None
        if k >= 3:
            F.set(cx, cy, "white"); F.set(cx - 1, cy, "neon_blue_hi"); F.set(cx + 1, cy, "neon_blue_hi")
        # soft pool fill (dithered) inside the ring once armed
        if k >= 4:
            for y in range(48):
                for x in range(48):
                    d = math.hypot(x - cx, (y - cy) / SQ) / (RX - 1)
                    if d < 1 and (x + y + k) % 3 == 0 and d > .25 and F.get(x, y) is None and ((x * 7 + y * 13) % 5 < 2):
                        F.set(x, y, "jt_teal_lo" if d > .6 else "neon_blue_lo")
        if k >= 3:
            twinkles(F, pts, P["spark"], k, tier, (5, 12, 43, 36))
        out.append(F)
    return out


# ------------------------------------------------------------------ rune trigger: pillar of cold light (billboard, feet pivot)
def burst(tier):
    P = T[tier]; w0 = P["pillar"]; pts = rnd_pts(tier * 19, P["spark"] + 2); out = []
    for k in range(6):
        F = H.Fx(CELL); cx = 23.5; base = 43
        hgt = [14, 30, 42, 36, 24, 12][k] * (1 if tier == 2 else 1.1); hgt = min(hgt, 42)
        w = [w0 - 1, w0 + 1, w0 + 2, w0 + 1, w0 - 1, 1][k]
        if k == 4:
            pass
        for y in range(int(base - hgt), base):
            f = (base - y) / hgt
            ww = w * (1 - .25 * f) + (1 if tier == 3 and f < .1 else 0)
            for dx in range(-int(ww), int(ww) + 1):
                d = abs(dx) / max(ww, 1)
                if k >= 4 and (x_ := (dx + y + k)) % 2:
                    continue
                c = "white" if d < .3 else "neon_blue_hi" if d < .6 else "neon_blue" if d < .85 else "jt_teal"
                if f > .85:
                    c = "neon_blue_lo" if d > .4 else "jt_teal_hi"
                F.set(cx + dx, y, c)
        for j in range(2 + tier):   # base rings
            r = 5 + k * 3 + j * 3
            if r < 22:
                F.ring(cx, base - 1, r, r * SQ, "neon_blue_hi" if j == 0 else "jt_teal", dots=1 + j)
        # shards spitting out
        for j in range(8 + 4 * (tier - 2)):
            a = -math.pi * (0.1 + 0.8 * (j / (7 + 4 * (tier - 2)))); sp = 4 + k * 3.2 + (j % 3) * 2
            F.set(cx + math.cos(a) * sp * 1.3, base - 6 + math.sin(a) * sp * 1.4 + k * k * .5, "white" if j % 3 == 0 else "neon_blue_hi")
        twinkles(F, pts, P["spark"] + 2, k, tier, (3, 3, 44, 42))
        out.append(F)
    return out


FX = {}
for t, RNG, (sp, trv) in ((2, "II", (8.0, 6.0)), (3, "III", (7.5, 7.5))):
    FX[f"stonefrost_cast_{RNG.lower()}"] = {"fn": (lambda t=t: cast(t)), "fps": 12, "kind": "billboard", "pivot": [24, 30], "lift": 1.0, "loop": False,
        "light": {"color": "neon_blue_hi", "intensity": 5 + 2 * (t - 2), "range": 3.5 + t - 2, "curve": [.4, .8, 1, .9, .6, .2]},
        "notes": f"Stonefrost {RNG} cast flare at the hands: floating rune sigil ({'triangle' if t == 2 else 'hexagram'}) + rising motes + sparkles (NEON blue/teal)"}
    FX[f"stonefrost_bolt_{RNG.lower()}"] = {"fn": (lambda t=t: bolt(t)), "fps": 12, "kind": "projectile", "pivot": [24, 24], "lift": 1.0,
        "light": {"color": "neon_blue", "intensity": 4 + 2 * (t - 2), "range": 3.5 + 1.2 * (t - 2), "curve": [1, 1, 1, 1, 1, 1]}, "speed": sp, "travel": trv, "then": f"stonefrost_impact_{RNG.lower()}",
        "notes": f"Stonefrost {RNG} boulder rimed in glowing ice crystals, sparkles around it; replaces seed_bomb for tier {RNG}"}
    FX[f"stonefrost_impact_{RNG.lower()}"] = {"fn": (lambda t=t: impact(t)), "fps": 14, "kind": "billboard", "pivot": [24, 41], "lift": 0.0, "loop": False,
        "light": {"color": "neon_blue_hi", "intensity": 8 + 3 * (t - 2), "range": 4 + 1.5 * (t - 2), "curve": [1, 1, .7, .45, .25, .1, 0]},
        "notes": f"Stonefrost {RNG} impact: white-blue flash, snow ring, ice shards, stone chips, sparkles (radius ~{T[t]['imp'] * 2 / 18:.1f} m at 18 px/m x2)"}
    FX[f"stonefrost_rune_{RNG.lower()}"] = {"fn": (lambda t=t: rune(t)), "fps": 12, "kind": "decal", "pivot": [24, 24], "lift": 0.03, "loop": False,
        "light": {"color": "neon_blue", "intensity": 3 + 1.5 * (t - 2), "range": 3 + (t - 2), "curve": [.2, .4, .6, .8, .8, .8, 1, 1]},
        "notes": f"Stonefrost {RNG} Frost Rune trap decal: draws in over frames 0-3, frame 5 = armed (engine holds frame 5 like rune_trap); larger, brighter and with an outer ring per tier"}
    FX[f"stonefrost_burst_{RNG.lower()}"] = {"fn": (lambda t=t: burst(t)), "fps": 14, "kind": "billboard", "pivot": [24, 43], "lift": 0.0, "loop": False,
        "light": {"color": "neon_blue_hi", "intensity": 9 + 2 * (t - 2), "range": 4.5 + 1.5 * (t - 2), "curve": [.6, 1, 1, .7, .4, .1]},
        "notes": f"Stonefrost {RNG} trap trigger: pillar of cold light + shards (replaces glyph_burst)"}


def main():
    meta = H.write_fx(OUT, "stonefrost_fx", FX, CELL)
    p = OUT / "stonefrost_fx.json"
    m = json.loads(p.read_text())
    for k, e in FX.items():
        d = m["effects"][k]
        d["speed"] = e.get("speed"); d["travel"] = e.get("travel"); d["then"] = e.get("then")
        if e.get("light"):
            d["light"] = {**e["light"], "color": H.ALLC[e["light"]["color"]]}
        if e["kind"] == "projectile":
            d["duration"] = round(6 / e["fps"], 3)
    m["tool"] = "hd2d spells"
    m["tier_of"] = {"boulder_toss": {"I": "seed_bomb -> earth_burst (repo)", "II": ["stonefrost_cast_ii", "stonefrost_bolt_ii", "stonefrost_impact_ii"], "III": ["stonefrost_cast_iii", "stonefrost_bolt_iii", "stonefrost_impact_iii"]},
                    "frost_rune": {"I": "rune_trap + glyph_burst (repo)", "II": ["stonefrost_rune_ii", "stonefrost_burst_ii"], "III": ["stonefrost_rune_iii", "stonefrost_burst_iii"]}}
    m["cast_sets"] = {"stonefrost_ii": [["stonefrost_cast_ii", "hands"]], "stonefrost_iii": [["stonefrost_cast_iii", "hands"]]}
    m["neon"] = "all pixels use cold-blue / teal neon + biome stone and snow; tier I is palette-only, so these need the fx neon allow-list (as jt_fx)"
    p.write_text(json.dumps(m, indent=1))
    return m


if __name__ == "__main__":
    main(); print("stonefrost fx ok", list(FX))
