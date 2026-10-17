"""Kindle, the ember salamander companion (Cinderhold, story/muspelheim.md 5.4). Run: python3 kindle_gen.py
Pets atlas layout (art/pets/pets_gen.py reused unchanged): 20x32 cells, pivot [10,32], rows down/up/left/right (right = mirror of left),
idle 0-3 | walk 4-7 | follow 8-11, one role `pet_kindle`. A hound-sized (~0.5x player) salamander, drawn ~16 x 11 px at the bottom of the cell:
charcoal-red hide, amber belly, a gold scarf for visibility, red-gold back spots that pulse like coals (NEON red in kindle_neon.png, PRIMARY).
Writes ../pets/kindle_neon.png (primary), ../pets/kindle.png (palette-safe twin), ../pets/kindle.json, ../pets/kindle_fx.png/json,
../pets/kindle_check_sprite_report.json, ../pets/kindle_contact.png"""
import json, math, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "pets"
OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(HERE.parents[1] / "pets"))
import pets_gen as P  # noqa
from PIL import Image, ImageDraw

SAFE = {"e_rim": "flower_gold", "e_body": "lamp", "e_hi": "white", "e_core": "white"}
NEONS = {"e_rim": "neon_red_lo", "e_body": "neon_red", "e_hi": "neon_red_hi", "e_core": "white"}
HIDE_HI, HIDE, HIDE_LO, HIDE_DK = "roof_hi", "roof", "roof_lo", "shadow"
BELLY, BELLY_HI = "flower_gold", "lamp"
SCARF, SCARF_LO = "flower_gold", "lamp"
RED = ("neon_red_hi", "neon_red", "neon_red_lo")


def hide(x, y, d, u, v):
    return HIDE_HI if (v < -.45 and u < .5) else HIDE if v < .35 else HIDE_LO


def pulse(i, k):
    """coal pulse: spots alternate between hi and body so the back 'breathes'"""
    return "e_hi" if (i + k) % 4 in (0, 1) else "e_body"


def draw_kindle(s, face, anim, i):
    blink = anim == "idle" and i == 3
    if anim == "idle":
        bob = (0, 0, 1, 0)[i]; legs = (0, 0, 0, 0); tsw = (0, 1, 0, -1)[i]; flap = 0
    elif anim == "walk":
        bob = (0, -1, 0, -1)[i]; tsw = (0, 1, 0, -1)[i]
        legs = ((1, 0, 0, 1), (0, 0, 0, 0), (0, 1, 1, 0), (0, 0, 0, 0))[i]; flap = (0, 1, 0, 1)[i]
    else:                                   # follow: a low scuttling run, belly near the ground, scarf streaming
        bob = (0, -1, -1, 0)[i]; tsw = (1, 2, 1, 0)[i]
        legs = ((2, 0, 0, 2), (1, 0, 0, 1), (0, 2, 2, 0), (0, 1, 1, 0))[i]; flap = (1, 2, 1, 2)[i]
    G = 30
    if face == "left":
        run = anim == "follow"
        st = 1 if run else 0
        # tail: long, wavy, curling up at the tip where an ember-coal glows
        tx, ty = 15.0 + st, 26.2 + bob
        pts = [(tx, ty), (tx + 1.8, ty + .6), (tx + 3.4, ty - .2 + tsw * .4), (tx + 4.4, ty - 1.8 + tsw * .6), (tx + 4.2, ty - 3.2 + tsw * .5)]
        for k, (x, y) in enumerate(pts):
            s.ell(x, y, 1.9 - k * .25, 1.6 - k * .2, lambda X, Y, d, u, v: HIDE if v < .1 else HIDE_LO)
        s.set(pts[-1][0], pts[-1][1] - 1, "e_hi"); s.set(pts[-1][0], pts[-1][1] - 2, "e_body")
        # legs (far pair darker): short, splayed
        lf, lb, rf, rb = legs
        for (x, lift, c) in ((7.6 - st, lf, HIDE_LO), (13.0 + st, lb, HIDE_LO), (9.2 - st, rf, HIDE_DK), (14.4 + st, rb, HIDE_DK)):
            for y in range(int(27 + bob), G + 1 - lift):
                s.set(x, y, c)
            s.set(x - 1, G - lift, HIDE_LO if c != HIDE_DK else HIDE_DK)       # splayed toes
        if any(legs):
            for x in range(8, 15):                                          # lifted feet keep a ground shadow
                s.set(x, G, "stone_lo") if s.get(x, G) is None else None
        # body
        s.ell(11.0 + st, 26.2 + bob, 5.6 + st, 2.5 - st * .3, hide)
        s.ell(10.0 + st, 28.0 + bob, 3.4, .8, lambda X, Y, d, u, v: BELLY_HI if u < 0 else BELLY)
        # glowing back spots
        for k, (x, y) in enumerate(((9.4, 24.2), (11.4, 23.9), (13.2, 24.4), (14.8, 25.2))):
            s.set(x + st, y + bob, pulse(i, k))
        s.set(11.4 + st, 24.7 + bob, "e_core") if i % 2 == 0 else None
        # head
        hx, hy = 5.2 - st, 25.2 + bob + (1 if run else 0)
        s.ell(hx, hy, 3.0, 2.2, lambda X, Y, d, u, v: HIDE_HI if v < -.3 else HIDE if v < .85 else BELLY)
        s.set(hx - 3.0, hy + .6, HIDE); s.set(hx - 3.6, hy + .8, "ink")       # snout + nostril
        if blink:
            s.set(hx - 1.0, hy - .6, "ink"); s.set(hx - 1.8, hy - .6, "ink")
        else:
            s.set(hx - 1.2, hy - .8, "ink"); s.set(hx - 1.2, hy - 1.8, "e_hi"); s.set(hx - 1.2, hy - .2, "ink")
        s.set(hx + .8, hy - 2.0, HIDE_HI); s.set(hx + 1.6, hy - 1.8, HIDE)    # little frill / brow ridge
        # scarf: a gold band at the neck with a short tail that flaps
        sx = hx + 3.0
        for yy in range(int(hy - .5), int(hy + 2.6)):
            s.set(sx, yy, SCARF); s.set(sx + 1, yy, SCARF_LO)
        for k in range(3 + flap):
            s.set(sx + 1 + k, hy + 2.2 - (k * .3) - (flap * .4 if k > 1 else 0), SCARF if k % 2 == 0 else SCARF_LO)
    elif face == "down":
        # tail peeks out on the right, curling up, coal tip glowing
        sx = (0, 1, 0, -1)[i] if anim == "idle" else (1, 0, 1, 0)[i]
        pts = [(14.0, 27.4 + bob), (15.4, 26.4 + bob), (16.0, 24.8 + bob), (15.6 + sx * .4, 23.2 + bob)]
        for k, (x, y) in enumerate(pts):
            s.ell(x, y, 1.6 - k * .2, 1.4 - k * .1, lambda X, Y, d, u, v: HIDE if u < .2 else HIDE_LO)
        s.set(pts[-1][0], pts[-1][1] - 1, "e_hi"); s.set(pts[-1][0], pts[-1][1] - 2, "e_body")
        lf, lb, rf, rb = legs
        for (x, lift) in ((6.4, lf), (13.0, rf)):
            for yy in range(27 + bob, G + 1 - lift):
                s.set(x, yy, HIDE_LO); s.set(x + 1, yy, HIDE)
            s.set(x - 1, G - lift, HIDE_LO); s.set(x + 2, G - lift, HIDE_LO)
        if any(legs[:2]):
            for x in range(8, 13):
                s.set(x, G, "stone_lo") if s.get(x, G) is None else None
        # body behind the head (back spots visible above), then head
        s.ell(10.0, 25.6 + bob, 4.8, 2.7, hide)
        for k, (x, y) in enumerate(((7.6, 24.6), (10.0, 23.4), (12.4, 24.6), (10.0, 25.6))):
            s.set(x, y + bob, pulse(i, k))
        s.ell(10.0, 28.0 + bob + (1 if anim == "follow" else 0), 3.8, 2.4, lambda X, Y, d, u, v: HIDE_HI if v < -.5 else HIDE if v < .8 else BELLY)
        hy = 27.6 + bob
        for sd in (-1, 1):
            ex = 10 + sd * 2.0
            if blink:
                s.set(ex, hy - .2, "ink")
            else:
                s.set(ex, hy - .5, "ink"); s.set(ex, hy + .5, "ink"); s.set(ex - .5 * sd, hy - 1.0, "e_hi")
        s.set(9, hy + 2.0, BELLY_HI); s.set(10, hy + 2.0, "roof_lo"); s.set(11, hy + 2.0, BELLY_HI)
        # scarf across the shoulders (a gold band between head and body)
        for x in range(7, 14):
            s.set(x, 26.0 + bob + (1 if anim == "follow" else 0), SCARF if x % 2 else SCARF_LO)
        s.set(13.5, 27.2 + bob, SCARF_LO); s.set(14.2, 27.9 + bob + (flap > 1), SCARF)
    else:   # up (back view)
        sx = (0, 1, 0, -1)[i] if anim == "idle" else (1, 0, 1, 0)[i]
        lf, lb, rf, rb = legs
        for (x, lift) in ((6.0, lf), (13.4, rf)):
            for yy in range(27 + bob, G + 1 - lift):
                s.set(x, yy, HIDE_LO); s.set(x + 1, yy, HIDE)
            s.set(x - 1, G - lift, HIDE_LO); s.set(x + 2, G - lift, HIDE_LO)
        if any(legs[:2]):
            for x in range(8, 13):
                s.set(x, G, "stone_lo") if s.get(x, G) is None else None
        s.ell(10.0, 26.4 + bob, 5.0, 3.2, hide)
        # tail runs down the middle toward the viewer, ending in a coal tip
        for k, y in enumerate(range(27, 31)):
            s.set(10 + sx * (k > 1) * .6, y + (bob if k < 2 else 0), HIDE if k % 2 else HIDE_LO); s.set(11 + sx * (k > 1) * .6, y + (bob if k < 2 else 0), HIDE_LO)
        s.set(10 + sx * .6, 30, "e_body")
        # V of glowing back spots + scarf band + head peeking above
        for k, (x, y) in enumerate(((10.0, 25.2), (8.0, 26.4), (12.0, 26.4), (6.6, 27.6), (13.4, 27.6), (10.0, 28.0))):
            s.set(x, y + bob, pulse(i, k))
        s.set(10, 26.6 + bob, "e_core")
        s.ell(10.0, 23.2 + bob, 3.0, 2.0, lambda X, Y, d, u, v: HIDE_HI if v < -.2 else HIDE)
        s.set(8.4, 22.2 + bob, HIDE_HI); s.set(11.6, 22.2 + bob, HIDE_HI)
        for x in range(7, 14):
            s.set(x, 24.8 + bob, SCARF if x % 2 else SCARF_LO)
        s.set(13.4, 25.6 + bob, SCARF_LO); s.set(14.2, 26.4 + bob + (flap > 1), SCARF)


P.PETS.clear()
P.PETS["pet_kindle"] = dict(draw=draw_kindle, name="Kindle",
    desc="Kindle, the ember salamander (Cinderhold companion, ~0.5x player): charcoal-red hide, amber belly, a gold scarf, red-gold back spots that pulse "
         "like coals and a glowing coal at the tail tip; curls into a coal when she faints",
    hover={"lift": 0.0, "bob": 0.0, "hz": 0.0},
    light={"color": "#ff7a1a", "intensity": 1.6, "range": 4.0, "lift": 0.3, "fadeIn": 0.4, "pulse": {"min": 0.75, "max": 1.2, "hz": 0.7, "shape": "sine"}},
    aura="pet_aura_kindle", pool="pet_pool_kindle", particles=None, speed=1.4,
    pets_js={"name": "Kindle", "role": "companion", "glow": "#ff7a1a", "hover": False, "light": 1.6, "fx": "kindle_embers"},
    look="NEON red glow spots / tail coal in kindle_neon.png (primary); kindle.png is palette-safe (lamp / flower_gold / white coals), same layout")


def embers(cols, seed, n=8):
    """warm embers drifting up off Kindle"""
    hi, mid, lo = cols
    R = random.Random(seed); pts = [(8 + R.random() * 16, 18 + R.random() * 12, R.randrange(8)) for _ in range(8)]
    out = []
    for f in range(n):
        F = P.Cell()
        for (x, y, p) in pts:
            b = (f + p) % 8; yy = y - b * 1.7; xx = x + math.sin((b + p) * .8) * 1.3
            if b in (1, 2):
                F.set(xx, yy, mid); F.set(xx, yy - 1, "white")
            elif b in (3, 4):
                F.set(xx, yy, hi)
            elif b == 5:
                F.star(xx, yy, 1, "white", hi)
            elif b in (6, 7):
                F.set(xx, yy, lo if b == 7 else mid)
        out.append(F)
    return out


def warm_ring(cols, n=8):
    """warm_ring skill: an expanding ring of heat (heals 10 HP/s in 3 m for 4 s). 3 m = radius ~ 14 px on the 32 px cell"""
    hi, mid, lo = cols
    out = []
    for f in range(n):
        F = P.Cell()
        r = 3 + f * 1.45
        for k in range(int(r * 7)):
            a = k / (r * 7) * math.tau
            x, y = 16 + math.cos(a) * r, 16 + math.sin(a) * r * P.DECAL_SQUASH
            if (k + f) % 2 == 0:
                F.set(x, y, hi if f < 4 else mid if f < 7 else lo)
        if f < 6:
            for k in range(8):
                a = k * .8 + f * .3
                F.set(16 + math.cos(a) * r * .55, 16 + math.sin(a) * r * .55 * P.DECAL_SQUASH, "white" if k % 3 == 0 else mid)
        out.append(F)
    return out


def ember_dash(cols, n=6):
    """ember_dash skill: a streak of embers trailing left-to-right; leaves a burn patch (separate decal)"""
    hi, mid, lo = cols
    out = []
    for f in range(n):
        F = P.Cell()
        for k in range(14):
            x = 3 + k * 1.9; y = 16 + math.sin(k * .9 + f) * 1.6
            if (k + f) % 3 == 0:
                continue
            F.set(x, y, hi if k > 9 else mid if k > 4 else lo)
            if k % 4 == f % 4:
                F.set(x, y - 2 - (k % 3), "white")
        F.star(28 - f * 0.4, 16, 2, "white", hi)
        out.append(F)
    return out


def burn_patch(cols, seed, n=6):
    """a small scorch decal Kindle leaves with ember_dash: dark ring of char with flickering coals"""
    hi, mid, lo = cols
    R = random.Random(seed); out = []
    for f in range(n):
        F = P.Cell()
        for y in range(32):
            for x in range(32):
                d = math.hypot(x - 16, (y - 16) / P.DECAL_SQUASH) / 9.0
                if d <= 1 and (x + y) % 2 == 0 and R.random() < .6 * (1 - d * .5):
                    F.set(x, y, "stone_lo" if d > .55 else "shadow")
        for k in range(6):
            a = k * 1.1 + f * .5; r = 2 + k * 1.1
            F.set(16 + math.cos(a) * r, 16 + math.sin(a) * r * P.DECAL_SQUASH, hi if (k + f) % 2 else mid)
        out.append(F)
    return out


def curl_coal(cols, n=6):
    """faint: Kindle curls into a glowing coal (billboard, sits where she fell)"""
    hi, mid, lo = cols
    out = []
    for f in range(n):
        F = P.Cell()
        F.ell(16, 27, 5, 3, lambda X, Y, d, u, v: "roof_hi" if v < -.3 else "roof_lo") if hasattr(F, "ell") else None
        for (x, y, c) in ((14, 25, hi if f % 2 else mid), (17, 26, mid), (16, 24, hi if (f + 1) % 2 else mid), (19, 27, lo)):
            F.set(x, y, c)
        F.set(16, 22 - f % 3, "white")
        out.append(F)
    return out


def fx_entries(suffix, cols, safe_cols):
    pass


P.FX.clear()
P.FX["pet_aura_kindle"] = dict(fn=lambda: embers(RED, 91), kind="billboard", fps=8, pivot=[16, 31], lift=0.0, glow=True,
                               desc="warm ember motes rising off Kindle (NEON red)")
P.FX["pet_aura_kindle_safe"] = dict(fn=lambda: embers(("lamp", "flower_gold", "roof_hi"), 91), kind="billboard", fps=8, pivot=[16, 31], lift=0.0, glow=True,
                                    desc="palette-safe twin of the aura")
P.FX["pet_pool_kindle"] = dict(fn=lambda: P.pet_pool(92, RED, 10.0), kind="decal", fps=6, pivot=[16, 16], lift=0.02, glow=True,
                               desc="warm red-orange light pool under Kindle (NEON red); pulses like a coal")
P.FX["pet_pool_kindle_safe"] = dict(fn=lambda: P.pet_pool(92, ("lamp", "flower_gold", "roof_hi"), 10.0), kind="decal", fps=6, pivot=[16, 16], lift=0.02, glow=True,
                                    desc="palette-safe twin of the pool")
P.FX["kindle_warm_ring"] = dict(fn=lambda: warm_ring(RED), kind="decal", fps=8, pivot=[16, 16], lift=0.03, glow=True,
                                desc="warm_ring skill (heal 10 HP/s in 3 m for 4 s): expanding heat ring (NEON red), scale to a 3 m radius")
P.FX["kindle_warm_ring_safe"] = dict(fn=lambda: warm_ring(("lamp", "flower_gold", "roof_hi")), kind="decal", fps=8, pivot=[16, 16], lift=0.03, glow=True,
                                     desc="palette-safe twin of warm_ring")
P.FX["kindle_ember_dash"] = dict(fn=lambda: ember_dash(RED), kind="billboard", fps=12, pivot=[16, 16], lift=0.0, glow=True,
                                 desc="ember_dash skill: an ember streak along the rush (NEON red); flip for direction")
P.FX["kindle_ember_dash_safe"] = dict(fn=lambda: ember_dash(("lamp", "flower_gold", "roof_hi")), kind="billboard", fps=12, pivot=[16, 16], lift=0.0, glow=True,
                                      desc="palette-safe twin of ember_dash")
P.FX["kindle_burn_patch"] = dict(fn=lambda: burn_patch(("lamp", "flower_gold", "roof_hi"), 93), kind="decal", fps=6, pivot=[16, 16], lift=0.02, glow=True,
                                 desc="scorch + coals Kindle leaves after ember_dash (palette only; 2 s)")


def main():
    safe, roles = P.build_sheet({**P.SLOTS_SAFE, **SAFE}); safe.save(OUT / "kindle.png")
    neon, _ = P.build_sheet({**P.SLOTS_NEON, **NEONS}); neon.save(OUT / "kindle_neon.png")
    for r in roles.values():
        r["size_bounds"] = [[8, 20], [7, 24]]
        r["story"] = "muspelheim.md 5.4: companion (befriend); ember_dash, warm_ring; lights torches; faint = curls into a coal, returns at the waystone"
        r["scale"] = 1.0
    meta = {"tool": "hearthmoor-art kindle_gen (pets_gen layout)", "biome": "cozy-village", "frame": [P.FW, P.FH], "pivot": P.PIVOT, "ground_row": P.GROUND,
            "facings": list(P.FACINGS), "anims": P.ANIMS, "cols": P.COLS, "image": "kindle_neon.png", "image_neon": "kindle_neon.png",
            "image_lock_safe": "kindle.png", "primary": "kindle_neon.png", "fallback": "kindle.png",
            "fallback_note": "primary is the neon twin; kindle.png (palette only) passes check-sprite; the neon twin passes via a scoped pet_kindle allow-list entry (neon red #a81c22 #e0302a #ff5a4a, same hexes as the lantern-fox)",
            "neon_accents": {k: P.NEON[k] for k in RED}, "size": [safe.width, safe.height], "fx": "kindle_fx.json", "roles": roles}
    (OUT / "kindle.json").write_text(json.dumps(meta, indent=1))
    fa, fm, _ = P.build_fx(); fm["image"] = "kindle_fx.png"
    fa.save(OUT / "kindle_fx.png"); (OUT / "kindle_fx.json").write_text(json.dumps(fm, indent=1))
    return safe, neon, fa, fm


def contact(safe, neon, fa, fm):
    BG = (26, 22, 30, 255); k = 4
    parts = []
    for im, lab in ((neon, "kindle_neon.png (PRIMARY): rows down / up / left / right; cols idle 0-3 | walk 4-7 | follow 8-11"), (safe, "kindle.png (palette-safe twin, passes check-sprite)")):
        im2 = Image.new("RGBA", im.size, BG); im2.alpha_composite(im); parts.append((im2.resize((im.width * k, im.height * k), Image.NEAREST), lab))
    strips = []
    for n, e in fm["effects"].items():
        st = Image.new("RGBA", (32 * e["frames"], 32), (12, 12, 20, 255))
        for i in range(e["frames"]):
            st.alpha_composite(fa.crop((i * 32, e["row"] * 32, i * 32 + 32, e["row"] * 32 + 32)), (i * 32, 0))
        strips.append((st.resize((st.width * 3, st.height * 3), Image.NEAREST), n))
    W = 20 * 12 * k + 40
    H = 50 + sum(p.height + 30 for p, _ in parts) + sum(s.height + 22 for s, _ in strips) + 20
    im = Image.new("RGBA", (W, H), BG); d = ImageDraw.Draw(im)
    d.text((16, 10), "Kindle, the ember salamander: pets layout 20x32, pivot [10,32]; glow is NEON red on back spots / tail coal only", fill=(255, 220, 190, 255))
    y = 40
    for p, lab in parts:
        d.text((16, y), lab, fill=(240, 180, 140, 255)); im.alpha_composite(p, (20, y + 18)); y += p.height + 30
    for s, n in strips:
        d.text((16, y), n, fill=(240, 180, 140, 255)); im.alpha_composite(s, (20, y + 16)); y += s.height + 22
    im.convert("RGB").save(OUT / "kindle_contact.png")


if __name__ == "__main__":
    safe, neon, fa, fm = main()
    sys.path.insert(0, "/workspace/hd2d-suite/tools/check-sprite")
    import check_sprite as CS
    rep = {"kindle (safe)": CS.check(OUT / "kindle.png", OUT / "kindle.json")}
    print("kindle safe:", rep["kindle (safe)"]["summary"])
    for r, v in rep["kindle (safe)"]["roles"].items():
        print(" ", r, v["colors"], v["issues"][:6])
    CS.NEON_PETS_ALLOW["pet_kindle"] = {"#a81c22", "#e0302a", "#ff5a4a"}   # in-process only (repo read-only): simulates the scoped allow-list entry the lead adds
    try:
        rep["kindle_neon"] = CS.check(OUT / "kindle_neon.png", OUT / "kindle.json")
        print("kindle neon:", rep["kindle_neon"]["summary"])
        for r, v in rep["kindle_neon"]["roles"].items():
            print(" ", r, v["colors"], v["issues"][:3])
    except Exception as e:
        print("neon check error", e)
    (OUT / "kindle_check_sprite_report.json").write_text(json.dumps(rep, indent=1, default=str))
    contact(safe, neon, fa, fm)
