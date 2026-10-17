"""Bloop, Bryony Glasswort's glowing frog (The Cold Cauldron, story/forge_alchemy.md 7.6). Run: python3 bloop_gen.py
Pets atlas layout (art/pets/pets_gen.py reused unchanged): 20x32 cells, pivot [10,32], rows down/up/left/right (right = mirror of left),
idle 0-3 | walk (hop) 4-7 | follow (big hop) 8-11, one role `pet_bloop`. The frog is drawn small (about 12 x 9 px) at the bottom of the cell.
Writes ../bloop_neon.png (PRIMARY, neon-blue glow pixels), ../bloop.png (palette-safe twin, passes check-sprite), ../bloop.json,
../bloop_fx.png/json (aura, pools, vent steam), ../check_sprite_report.json, ../contact_sheet.png."""
import json, math, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
OUT = HERE.parent
sys.path.insert(0, str(HERE.parents[1] / "pets"))
import pets_gen as P  # noqa  (read-only reuse of the pets writer: Spr, Cell, build_sheet, build_fx, aura / pool helpers)
from PIL import Image, ImageDraw

P.NEON.update({"neon_blue": "#2ab4ff", "neon_blue_hi": "#a6ecff", "neon_blue_lo": "#1c62d8"})
P.ALL.update(P.NEON)
NB = ("neon_blue_hi", "neon_blue", "neon_blue_lo")
SAFE = {"e_rim": "cloth", "e_body": "flower_blue", "e_hi": "sky", "e_core": "white"}
NEONS = {"e_rim": "neon_blue_lo", "e_body": "neon_blue", "e_hi": "neon_blue_hi", "e_core": "white"}
DK, MD, LT, HI = "leaf_deep", "moss", "grass", "grass_hi"          # teal-green back: deep / mid / light / highlight
BELLY, BELLY_HI = "sky", "plaster_hi"
WARM, WARM2 = "lamp", "flower_gold"                                 # amber forge light on the upper-left rim


def back(x, y, d, u, v):
    if u < -1.4 and v < -0.6:
        return HI
    return LT if (u < 0.6 and v < 0.8) else MD if d < 0.8 else DK


def belly(x, y, d, u, v):
    return BELLY_HI if (v < 0.2 and u < 0.6) else BELLY


def draw_bloop(s, face, anim, i):
    lift, crouch, ext, infl, blink = 0, 0, 0, 0, False
    if anim == "idle":
        infl = (0, 1, 1, 0)[i]; blink = i == 3
    elif anim == "walk":
        lift, crouch, ext = ((0, 1, 0), (2, 0, 1), (3, 0, 1), (1, 1, 0))[i]
    else:
        lift, crouch, ext = ((0, 1, 0), (4, 0, 1), (5, 0, 1), (1, 1, 0))[i]
    G = 30                                   # last content row; the outline pass adds the ink ground row 31
    dy = -lift
    sh = max(2, 6 - lift) if lift else 0
    if lift:                                 # a little shadow keeps the feet row on the ground while he hops
        for x in range(10 - sh // 2, 10 + (sh + 1) // 2):
            s.set(x, G, "stone_lo")
    top = G - 9 + crouch + dy                # top of the body block
    cy = top + 4.8
    if face == "down":
        # hind legs (folded: big thighs; stretched in the air)
        for sd in (-1, 1):
            lx = 10 + sd * 3.9
            if ext:
                s.ell(lx + sd * 0.3, cy + 3.2, 1.6, 3.4, back)
                for t in (-1, 0, 1):
                    s.set(lx + sd * 0.6 + t, cy + 6.6, MD)
            else:
                s.ell(lx, G - 1.8 + dy, 2.4, 2.2, back)
                for t in (-1.5, -0.5, 0.5, 1.5):
                    s.set(lx + sd * 0.8 + t, G + dy * 0, MD if t < 0 else DK)
        # body + belly
        s.ell(10, cy + 0.8 + crouch * .3, 4.4, 3.7 - crouch * 0.3, back)
        s.ell(10, cy + 2.4, 2.9, 1.9, belly)
        # throat sac (glows when he croaks)
        if infl:
            s.ell(10, cy + 1.6, 2.4, 1.3, lambda X, Y, d, u, v: "e_hi" if d < .45 else "e_body")
            s.set(10, cy + 1.2, "e_core")
        else:
            s.set(10, cy + 1.6, "e_rim"); s.set(9, cy + 1.6, BELLY_HI); s.set(11, cy + 1.6, BELLY_HI)
        # head bulge + eyes
        s.ell(10, top + 3.6, 4.3, 2.9, back)
        for sd in (-1, 1):
            ex = 10 + sd * 3.0
            s.ell(ex, top + 1.8, 1.9, 1.8, lambda X, Y, d, u, v: HI if (u < -.3 and v < .3) else LT)
            if blink:
                s.set(ex - 1, top + 2, "ink"); s.set(ex, top + 2, "ink"); s.set(ex + 1, top + 2, "ink")
            else:
                s.set(ex, top + 2, "ink"); s.set(ex, top + 3, "ink"); s.set(ex - 0.6 * sd, top + 1.4, "white")
        # smile + warm cheeks + glowing freckles on the brow
        for x in range(8, 13):
            s.set(x, top + 5.5 - (1 if x in (8, 12) else 0), "ink" if x not in (9, 10, 11) else "roof_lo")
        s.set(7, top + 5, "flower_rose"); s.set(13, top + 5, "flower_rose")
        s.set(10, top + 2.2, "e_hi"); s.set(9, top + 3.2, "e_body"); s.set(11, top + 3.2, "e_body")
                # front paws
        for sd in (-1, 1):
            px = 10 + sd * 2.6
            for t in (-1, 0, 1):
                s.set(px + t, G + dy * (0 if ext else 0) - (2 if lift and ext else 0) + (0 if not lift else 0), MD if t else LT)
        # amber forge light on the upper-left rim
        s.set(6.0, top + 4.0, WARM); s.set(6.6, top + 3.0, WARM2)
    elif face == "up":
        for sd in (-1, 1):
            lx = 10 + sd * 3.9
            if ext:
                s.ell(lx + sd * 0.3, cy + 3.0, 1.7, 3.6, back)
                for t in (-1, 0, 1):
                    s.set(lx + sd * 0.7 + t, cy + 6.7, DK)
            else:
                s.ell(lx, G - 2.0 + dy, 2.5, 2.4, back)
                for t in (-1.5, -0.5, 0.5, 1.5):
                    s.set(lx + sd * 0.8 + t, G + dy * 0, DK)
        s.ell(10, cy + 1.2 + crouch * .3, 4.5, 3.8 - crouch * 0.3, back)
        s.ell(10, top + 2.8, 4.1, 2.5, back)
        for sd in (-1, 1):
            s.ell(10 + sd * 3.0, top + 1.5, 1.9, 1.7, lambda X, Y, d, u, v: HI if (u < -.3 and v < .3) else LT)
            s.set(10 + sd * 3.0, top + 1.9, "ink") if blink else None
        # glowing back spots (V pattern)
        for (dx, dyy, c) in ((0, 4.0, "e_hi"), (-2.2, 5.4, "e_body"), (2.2, 5.4, "e_body"), (0, 6.4, "e_body")):
            s.set(10 + dx, top + dyy, c)
        s.set(10, top + 3.4, "e_core")
        s.set(6.2, top + 5.0, WARM); s.set(6.6, top + 4.0, WARM2)
    else:   # left (right is the mirror)
        if ext:     # hind leg stretched behind him
            for k in range(5):
                s.set(12.5 + k, cy + 2.4 + k * 0.5, MD if k % 2 else LT)
            s.set(17, cy + 4.6, DK); s.set(18, cy + 4.4, DK)
            s.ell(12.3, cy + 2.2, 2.4, 2.2, back)
        else:
            s.ell(12.6, G - 2.2 + dy, 2.9, 2.6, back)
            for xx in range(9, 15):
                s.set(xx, G + dy * 0, DK if xx < 11 else MD)
        s.ell(10.6, cy + 1.2 + crouch * .3, 4.5, 3.7 - crouch * 0.3, back)
        s.ell(8.4, cy + 2.4, 2.3, 1.7, belly)
        # head
        s.ell(6.8, top + 3.6, 3.4, 2.8, back)
        s.ell(7.0, top + 1.8, 1.9, 1.8, lambda X, Y, d, u, v: HI if (u < -.3 and v < .3) else LT)
        if blink:
            s.set(6, top + 2, "ink"); s.set(7, top + 2, "ink"); s.set(8, top + 2, "ink")
        else:
            s.set(6.6, top + 2, "ink"); s.set(6.6, top + 3, "ink"); s.set(7.4, top + 1.2, "white")
        for x in range(4, 9):
            s.set(x, top + 5.8 - (1 if x == 4 else 0), "ink" if x != 6 else "roof_lo")
        s.set(8, top + 5, "flower_rose")
        if infl:
            s.ell(6.2, cy + 1.6, 1.9, 1.2, lambda X, Y, d, u, v: "e_hi" if d < .45 else "e_body")
        # glowing back spots
        for (x, yy, c) in ((10.0, top + 3.6, "e_hi"), (12.2, top + 3.3, "e_body"), (13.6, top + 4.4, "e_body"), (11.2, top + 5.4, "e_rim")):
            s.set(x, yy, c)
        s.set(10.0, top + 3.0, "e_core")
        # front leg
        for yy in range(int(cy + 3.4), G + 1):
            s.set(7.0, yy, MD)
        s.set(6, G, LT); s.set(7, G, LT); s.set(8, G, MD)
        s.set(4.8, top + 3.8, WARM); s.set(5.4, top + 2.8, WARM2)


P.PETS.clear()
P.PETS["pet_bloop"] = dict(draw=draw_bloop, name="Bloop",
    desc="Bloop, Bryony's glowing frog (The Cold Cauldron): a small teal-green frog with a pale belly, big shy eyes, a tiny smile and cold-blue glowing "
         "freckles on his brow and back; amber forge light on one side; sits by the Forge Quarter vents, hops when he follows",
    hover={"lift": 0.0, "bob": 0.0, "hz": 0.0},
    light={"color": "#7fe0e8", "intensity": 1.4, "range": 3.0, "lift": 0.3, "fadeIn": 0.4, "pulse": {"min": 0.7, "max": 1.15, "hz": 0.6, "shape": "sine"}},
    aura="pet_aura_bloop", pool="pet_pool_bloop", particles=None, speed=2.0,
    pets_js={"name": "Bloop", "role": "talk", "glow": "#7fe0e8", "hover": False, "light": 1.4, "fx": "bloop_bubble"},
    look="NEON blue glow freckles and throat in bloop_neon.png (primary); bloop.png is palette-safe (sky / flower_blue / cloth), same layout")


def bubbles(cols, seed, n=8):
    """tiny glowing bubbles rising off Bloop, a pop at the top"""
    hi, mid, lo = cols
    R = random.Random(seed); pts = [(9 + R.random() * 14, 14 + R.random() * 14, R.randrange(8)) for _ in range(6)]
    out = []
    for f in range(n):
        F = P.Cell()
        for (x, y, p) in pts:
            b = (f + p) % 8; yy = y - b * 1.5; xx = x + math.sin((b + p) * 0.9)
            if b in (1, 2, 3):
                F.set(xx, yy, mid); F.set(xx + 1, yy, hi)
            elif b in (4, 5):
                F.set(xx, yy, hi); F.set(xx, yy + 1, lo)
            elif b == 6:
                F.star(xx, yy, 1, "white", hi)
        out.append(F)
    return out


def steam(n=8):
    """Forge Quarter vent steam: soft palette puffs rising, amber underlight at the base (palette only)"""
    R = random.Random(5); out = []
    puffs = [(13 + R.random() * 6, R.random(), R.uniform(2.0, 3.4)) for _ in range(6)]
    for f in range(n):
        F = P.Cell()
        for k, (x, ph, r) in enumerate(puffs):
            t = ((f / n) + ph) % 1.0
            y = 29 - t * 24; rr = r * (0.5 + t * 0.9); xx = x + math.sin(t * 5 + k) * 2.2
            if t < 0.88:
                for yy in range(int(y - rr), int(y + rr) + 1):
                    for x0 in range(int(xx - rr), int(xx + rr) + 1):
                        d = math.hypot(x0 - xx, (yy - y) * 1.3)
                        if d <= rr and (x0 + yy + f) % 2 == (0 if t < 0.5 else 1) or (d <= rr * 0.55 and t < 0.6):
                            F.set(x0, yy, "plaster_hi" if t < 0.35 else "sky" if t < 0.65 else "flower_blue")
        for k in range(3):
            F.set(14 + k * 2 + (f % 2), 30, "lamp" if (k + f) % 2 else "flower_gold")
        out.append(F)
    return out


P.FX.clear()
P.FX["pet_aura_bloop"] = dict(fn=lambda: bubbles(NB, 81), kind="billboard", fps=8, pivot=[16, 31], lift=0.0, glow=True,
                              desc="cold-blue glowing bubbles and sparkles rising off Bloop (NEON blue)")
P.FX["pet_aura_bloop_safe"] = dict(fn=lambda: bubbles(("white", "sky", "flower_blue"), 81), kind="billboard", fps=8, pivot=[16, 31], lift=0.0, glow=True,
                                   desc="palette-safe twin of the aura")
P.FX["pet_pool_bloop"] = dict(fn=lambda: P.pet_pool(82, NB, 8.0), kind="decal", fps=6, pivot=[16, 16], lift=0.02, glow=True,
                              desc="soft cold-teal light pool under Bloop (NEON blue), small; pulses like a heartbeat")
P.FX["pet_pool_bloop_safe"] = dict(fn=lambda: P.pet_pool(82, ("sky", "flower_blue", "cloth"), 8.0), kind="decal", fps=6, pivot=[16, 16], lift=0.02, glow=True,
                                   desc="palette-safe twin of the pool")
P.FX["vent_steam"] = dict(fn=steam, kind="billboard", fps=6, pivot=[16, 31], lift=0.0, glow=False,
                          desc="Forge Quarter vent steam with an amber underglow (palette only; optional, put at Old Gurgle / the quench-tank vents)")


def main():
    safe, roles = P.build_sheet({**P.SLOTS_SAFE, **SAFE}); safe.save(OUT / "bloop.png")
    neon, _ = P.build_sheet({**P.SLOTS_NEON, **NEONS}); neon.save(OUT / "bloop_neon.png")
    for r in roles.values():
        r["size_bounds"] = [[8, 20], [7, 24]]
        r["story"] = "forge_alchemy.md 7.6: found at Tova's quench tank (flag is `cc_bloop`); talkable; sits near the Forge Quarter vents; hops when following"
        r["scale"] = 1.0
    meta = {"tool": "hearthmoor-art bloop_gen (pets_gen layout)", "biome": "cozy-village", "frame": [P.FW, P.FH], "pivot": P.PIVOT, "ground_row": P.GROUND,
            "facings": list(P.FACINGS), "anims": P.ANIMS, "cols": P.COLS, "image": "bloop_neon.png", "image_neon": "bloop_neon.png",
            "image_lock_safe": "bloop.png", "primary": "bloop_neon.png", "fallback": "bloop.png",
            "fallback_note": "primary is the neon twin; bloop.png (palette only) passes check-sprite today; the neon twin needs a scoped pet_bloop allow-list entry (neon blue #1c62d8 #2ab4ff #a6ecff, same hexes as Tick / Flurry)",
            "neon_accents": {k: P.NEON[k] for k in NB}, "size": [safe.width, safe.height], "fx": "bloop_fx.json", "roles": roles}
    (OUT / "bloop.json").write_text(json.dumps(meta, indent=1))
    fa, fm, _ = P.build_fx(); fm["image"] = "bloop_fx.png"
    fa.save(OUT / "bloop_fx.png"); (OUT / "bloop_fx.json").write_text(json.dumps(fm, indent=1))
    return safe, neon, fa, fm


def contact(safe, neon, fa, fm):
    BG = (22, 26, 40, 255)
    k = 4
    W = 20 * 12 * k + 40
    rows = []
    def sheet(im, lab):
        im2 = Image.new("RGBA", im.size, BG); im2.alpha_composite(im)
        return im2.resize((im.width * k, im.height * k), Image.NEAREST), lab
    parts = [sheet(neon, "bloop_neon.png (PRIMARY): rows down / up / left / right; cols idle 0-3 | hop 4-7 | follow-hop 8-11"), sheet(safe, "bloop.png (palette-safe twin, passes check-sprite)")]
    fx_names = list(fm["effects"])
    strips = []
    for n in fx_names:
        e = fm["effects"][n]
        st = Image.new("RGBA", (32 * e["frames"], 32), (12, 14, 26, 255))
        for i in range(e["frames"]):
            fr = fa.crop((i * 32, e["row"] * 32, i * 32 + 32, e["row"] * 32 + 32)); st.alpha_composite(fr, (i * 32, 0))
        strips.append((st.resize((st.width * 3, st.height * 3), Image.NEAREST), n))
    H = 50 + sum(p.height + 30 for p, _ in parts) + sum(s.height + 22 for s, _ in strips) + 40
    im = Image.new("RGBA", (W, H), BG); d = ImageDraw.Draw(im)
    d.text((16, 10), "Bloop, Bryony's glowing frog (The Cold Cauldron): pets layout 20x32, pivot [10,32], hop cycle; glow is NEON blue on freckles / throat only", fill=(220, 235, 255, 255))
    y = 40
    for p, lab in parts:
        d.text((16, y), lab, fill=(150, 200, 230, 255)); im.alpha_composite(p, (20, y + 18)); y += p.height + 30
    for s, n in strips:
        d.text((16, y), n, fill=(150, 200, 230, 255)); im.alpha_composite(s, (20, y + 16)); y += s.height + 22
    im.convert("RGB").save(OUT / "contact_sheet.png")


if __name__ == "__main__":
    safe, neon, fa, fm = main()
    sys.path.insert(0, "/workspace/hd2d-suite/tools/check-sprite")
    import check_sprite as CS
    rep = {"bloop (safe)": CS.check(OUT / "bloop.png", OUT / "bloop.json")}
    print("bloop safe:", rep["bloop (safe)"]["summary"])
    try:
        rep["bloop_neon (needs pet_bloop allow-list)"] = CS.check(OUT / "bloop_neon.png", OUT / "bloop.json")
        print("bloop neon:", rep["bloop_neon (needs pet_bloop allow-list)"]["summary"])
    except Exception as e:
        print("neon check error", e)
    (OUT / "check_sprite_report.json").write_text(json.dumps(rep, indent=1, default=str))
    contact(safe, neon, fa, fm)
