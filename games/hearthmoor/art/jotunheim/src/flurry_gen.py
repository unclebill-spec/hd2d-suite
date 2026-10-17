"""Flurry the snow hare (Jotunheim pet) on the pets/ atlas layout (20x32, pivot [10,32], rows down/up/left/right, idle 0-3, walk 4-7,
follow 8-11). Reuses pets/pets_gen.py (Spr, build_sheet, build_fx, aura / pool helpers) unchanged, like Tick.
Writes ../pets/: flurry_neon.png (primary, neon-blue glow ear tips / tail puff / chest) + flurry.png (palette-safe twin) + flurry.json + flurry_fx."""
import json, math, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "pets"))
import pets_gen as P  # noqa

OUT = HERE.parent / "pets"
P.NEON.update({"neon_blue": "#2ab4ff", "neon_blue_hi": "#a6ecff", "neon_blue_lo": "#1c62d8"})
P.ALL.update(P.NEON)
SAFE = {"e_rim": "cloth", "e_body": "flower_blue", "e_hi": "sky", "e_core": "white"}
NEONS = {"e_rim": "neon_blue_lo", "e_body": "neon_blue", "e_hi": "neon_blue_hi", "e_core": "white"}
FUR, FUR_M, FUR_D, FUR_DD = "white", "plaster_hi", "stone_hi", "sky"


def fur(x, y, d, u, v):
    return FUR if (u < -1.0 and v < 0.6) else FUR_D if (d > 0.72 or v > 1.4) else FUR_M


def draw_flurry(s, face, anim, i):
    blink = anim == "idle" and i == 3
    twitch = anim == "idle" and i == 2
    if anim == "idle":
        bob = [0, 0, 0, 0][i]; hop = [0, 0, 0, 0][i]; ear = [0, 0, 1, 0][i]; legs = (0, 0)
    elif anim == "walk":
        bob = [0, -1, -1, 0][i]; ear = [0, 0, 1, 1][i]; legs = [(0, 0), (1, 0), (1, 1), (0, 1)][i]
    else:
        bob = [-1, -2, -1, 0][i]; ear = [2, 2, 1, 1][i]; legs = [(1, 1), (1, 1), (0, 1), (0, 0)][i]
    run = anim == "follow"
    st = 1 if run else 0
    if face == "left":
        # tail puff (glowing tip) behind
        tx, ty = 16.0 + st, 24.5 + bob
        s.ell(tx, ty, 2.0, 2.0, lambda X, Y, d, u, v: FUR if u < 0 else FUR_M)
        s.set(tx + 1, ty - 1, "e_hi"); s.set(tx + 1, ty, "e_body"); s.set(tx, ty - 1, "e_core")
        # hind leg (big haunch + foot), front legs
        s.ell(12.5 + st, 25.6 + bob, 3.3, 3.0, fur)
        for yy in range(27 + bob, 31 - legs[0]):
            s.set(7.4 - st, yy, FUR_D); s.set(8.4 - st, yy, FUR_M)
        s.rect = None
        for xx in range(10 + st, 16 + st):
            s.set(xx, 30 - legs[1] * 0, FUR_D if xx < 12 + st else FUR_M)
            s.set(xx, 31 - legs[1] * 0, FUR_DD if xx < 12 + st else FUR_D)
        # body
        s.ell(10.0, 24.0 + bob, 5.2 + st * .6, 3.0, fur)
        # chest glow
        s.set(7, 24 + bob, "e_hi"); s.set(7, 25 + bob, "e_body")
        # head
        hx, hy = 6.2 - st * 1.2, 20.6 + bob + (1 if run else 0)
        s.ell(hx, hy, 2.9, 2.5, lambda X, Y, d, u, v: FUR if (u < 0.2 and v < 0.6) else FUR_M if d < .8 else FUR_D)
        s.set(hx - 3.0, hy + 0.9, "flower_rose")                      # nose
        s.set(hx - 2.0, hy + 1.9, FUR_D)
        if blink:
            s.set(hx - 1.3, hy - 0.2, "ink"); s.set(hx - 0.3, hy - 0.2, "ink")
        else:
            s.set(hx - 1.2, hy - 0.5, "ink"); s.set(hx - 1.2, hy + 0.5, "ink"); s.set(hx - 1.6, hy - 0.5, "white")
        # long ears (glowing tips), laid back when running
        if run:
            pts = [(hx + 1.6, hy - 2.4), (hx + 2.8, hy - 3.0), (hx + 4.0, hy - 3.2), (hx + 5.2, hy - 3.0), (hx + 6.2, hy - 2.6)]
        else:
            lean = 0.5 if not twitch else 1.3
            pts = [(hx + 0.8, hy - 2.4), (hx + 1.0 + lean * 0.2, hy - 4.0), (hx + 1.3 + lean * 0.5, hy - 5.6), (hx + 1.7 + lean * 0.8, hy - 7.2), (hx + 2.2 + lean, hy - 8.6)]
        for k, (x, y) in enumerate(pts):
            for dx in (0, 1):
                s.set(x + dx, y, FUR_M if dx else FUR)
            if k >= len(pts) - 2:
                s.set(x, y, "e_hi"); s.set(x + 1, y, "e_body")
        # tip sparkle
        ex, ey = pts[-1]
        s.set(ex, ey - 1, "e_core")
    else:
        back = face == "up"
        # haunches / feet
        for sd in (-1, 1):
            lf = legs[0] if sd < 0 else legs[1]
            s.ell(10 + sd * 3.2, 27.5 + bob, 2.0, 2.6, fur)
            for xx in (10 + sd * 3.2 - 1, 10 + sd * 3.2, 10 + sd * 3.2 + 1):
                s.set(xx, 31 - lf * 0 - 1, FUR_M); s.set(xx, 31, FUR_D)
        # body
        s.ell(10, 25.0 + bob, 4.4, 4.0, fur)
        if back:
            s.ell(10, 28 + bob, 2.2, 2.0, lambda X, Y, d, u, v: FUR if v < 0 else FUR_M)     # tail puff
            s.set(10, 27 + bob, "e_hi"); s.set(11, 28 + bob, "e_body"); s.set(10, 28 + bob, "e_core")
        else:
            for sd in (-1, 1):
                for yy in range(27 + bob, 30):
                    s.set(10 + sd * 1.5, yy, FUR_M)
            s.set(10, 24 + bob, "e_hi"); s.set(10, 25 + bob, "e_body"); s.set(9, 25 + bob, "e_rim"); s.set(11, 25 + bob, "e_rim")
        # head
        hx, hy = 10, 19.4 + bob
        s.ell(hx, hy, 3.6, 3.0, lambda X, Y, d, u, v: FUR if (u < -0.6 and v < 0.6) else FUR_M if d < .75 else FUR_D)
        if not back:
            for sd in (-1, 1):
                if blink:
                    s.set(hx + sd * 1.9, hy, "ink")
                else:
                    s.set(hx + sd * 1.9, hy - 0.4, "ink"); s.set(hx + sd * 1.9, hy + 0.6, "ink")
            s.set(hx - 0.0, hy + 1.6, "flower_rose"); s.set(hx + 1, hy + 1.6, "flower_rose")
        # ears
        sp = 2.0 + (1 if twitch else 0) + (1 if run else 0)
        for sd in (-1, 1):
            for k in range(8):
                x = hx + sd * (1.8 + k * 0.28 * (sp / 2.0) + (ear * 0.2 if sd > 0 else 0))
                y = hy - 2.6 - k + (0.0)
                for dx in (0, 1 if sd > 0 else -1):
                    s.set(x + dx, y, FUR_M if dx else FUR)
                if k >= 6:
                    s.set(x, y, "e_hi"); s.set(x + (1 if sd > 0 else -1), y, "e_body")
            s.set(hx + sd * (1.8 + 7 * 0.28 * (sp / 2.0)), hy - 11.6, "e_core")


P.PETS.clear()
P.PETS["pet_flurry"] = dict(draw=draw_flurry, name="Flurry",
    desc="Flurry, the snow hare (Jotunheim pet): a white hare with long ears whose tips glow cold blue, a glowing tail puff and a faint "
         "chest glint; scampers on the ground, ears flat when she bounds (speed aura, finds hidden snow paths)",
    hover={"lift": 0.0, "bob": 0.0, "hz": 0.0},
    light={"color": "#bfe8ff", "intensity": 1.2, "range": 3.0, "lift": 0.35, "fadeIn": 0.4,
           "pulse": {"min": 0.85, "max": 1.1, "hz": 0.7, "shape": "sine"}},
    aura="pet_aura_flurry", pool="pet_pool_flurry", particles=None, speed=2.6,
    pets_js={"name": "Flurry", "role": "scout", "glow": "#bfe8ff", "hover": False, "light": 1.2, "fx": "snow_puff",
             "aura": {"speedMul": 1.08, "frostSlowImmune": True, "snowPath": True}},
    look="NEON blue ear tips / tail puff / chest in flurry_neon.png (primary); flurry.png is palette-safe (sky / flower_blue / cloth)")
NB = ("neon_blue_hi", "neon_blue", "neon_blue_lo")
P.FX.clear()
P.FX["pet_aura_flurry"] = dict(fn=lambda: P.aura_orbit(71, NB, rx=8.0, ry=4.5, cy=22, rise=0.8, extra=9), kind="billboard", fps=8,
                               pivot=[16, 31], lift=0.0, glow=True, desc="neon-blue ice sparkles drifting up around Flurry's glowing ears (NEON blue)")
P.FX["pet_pool_flurry"] = dict(fn=lambda: P.pet_pool(72, NB, 9.0), kind="decal", fps=6, pivot=[16, 16], lift=0.02, glow=True,
                               desc="soft cold-blue light pool under Flurry (NEON blue)")
P.FX["pet_pool_flurry_safe"] = dict(fn=lambda: P.pet_pool(72, P.BLUE, 9.0), kind="decal", fps=6, pivot=[16, 16], lift=0.02, glow=True,
                                    desc="palette-safe twin of the pool")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    safe, roles = P.build_sheet({**P.SLOTS_SAFE, **SAFE}); safe.save(OUT / "flurry.png")
    neon, _ = P.build_sheet({**P.SLOTS_NEON, **NEONS}); neon.save(OUT / "flurry_neon.png")
    meta = {"tool": "hearthmoor-art flurry_gen (pets_gen layout)", "biome": "cozy-village", "frame": [P.FW, P.FH], "pivot": P.PIVOT,
            "ground_row": P.GROUND, "facings": list(P.FACINGS), "anims": P.ANIMS, "cols": P.COLS, "image": "flurry_neon.png",
            "image_neon": "flurry_neon.png", "image_lock_safe": "flurry.png", "primary": "flurry_neon.png", "fallback": "flurry.png",
            "fallback_note": "primary sheet is the neon twin (like pets/pets_neon.png); flurry.png is the palette-safe twin (passes check-sprite) and the fallback until the scoped pet_flurry neon allow-list entry lands (the lead is adding it)",
            "neon_accents": {k: P.NEON[k] for k in NB}, "size": [safe.width, safe.height], "fx": "flurry_fx.json", "roles": roles}
    (OUT / "flurry.json").write_text(json.dumps(meta, indent=1))
    fa, fm, _ = P.build_fx(); fm["image"] = "flurry_fx.png"
    fa.save(OUT / "flurry_fx.png"); (OUT / "flurry_fx.json").write_text(json.dumps(fm, indent=1))
    return safe, neon, fa


if __name__ == "__main__":
    main()
