"""Tick the clockwork owl (Svartalfheim pet) on the pets/ atlas layout (20x32, pivot [10,32], rows down/up/left/right,
idle 0-3, walk 4-7, follow 8-11). Reuses pets/pets_gen.py (Spr, build_sheet, build_fx, aura/pool helpers) unchanged.
Writes ../tick/: tick.png (lock-safe, palette only) + tick_neon.png (primary, neon-blue eyes/core) + tick.json + tick_fx."""
import json, math, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "pets"))
import pets_gen as P  # noqa

OUT = HERE.parent / "tick"
P.NEON.update({"neon_blue": "#2ab4ff", "neon_blue_hi": "#a6ecff", "neon_blue_lo": "#1c62d8"})
P.ALL.update(P.NEON)
SAFE = {"e_rim": "cloth", "e_body": "flower_blue", "e_hi": "sky", "e_core": "white"}
NEONS = {"e_rim": "neon_blue_lo", "e_body": "neon_blue", "e_hi": "neon_blue_hi", "e_core": "white"}


def draw_tick(s, face, anim, i):
    bob = [0, -1, -1, 0][i] if anim == "idle" else [0, -1, 0, 1][i] if anim == "walk" else [-1, -2, -1, 0][i]
    cx, cy = 10, 23 + bob
    flap = anim == "follow"
    # wings (brass, riveted feather plates)
    for sgn in (-1, 1):
        if face == "left" and sgn < 0:
            continue
        wx = cx + sgn * (5 if not flap else 6)
        s.ell(wx, cy + (0 if not flap else -2), 2, 4 if not flap else 3,
              lambda x, y, d, u, v: "timber" if v > 1 else "timber_hi", ang=sgn * (0.3 if not flap else 0.9))
    # body: brass egg
    s.ell(cx, cy, 5, 6, lambda x, y, d, u, v: "flower_gold" if u < -1.5 and v < 0 else "timber" if d > 0.7 and u > 1 else "timber_hi")
    # ear tufts
    for sgn in (-1, 1):
        s.set(cx + sgn * 3, cy - 6, "timber"); s.set(cx + sgn * 4, cy - 7, "timber_lo")
    if face == "up":
        P_gear(s, cx, cy + 1, 2)
    else:
        ex = [(-2, 2)] if face != "left" else [(-2,)]
        offs = (-2, 2) if face != "left" else (-3,)
        blink = anim == "idle" and i == 3
        for ox in offs:
            x, y = cx + ox, cy - 2
            s.set(x - 1, y, "stone_lo"); s.set(x + 1, y, "stone_lo"); s.set(x, y - 1, "stone_lo"); s.set(x, y + 1, "stone_lo")
            if blink:
                s.set(x, y, "e_rim")
            else:
                s.set(x, y, "e_core"); s.set(x + 1, y + 1, "e_body")
        s.set(cx + (0 if face != "left" else -4), cy, "roof_hi")         # copper beak
        P_gear(s, cx + (0 if face != "left" else -1), cy + 3, 1)       # chest gear with glowing core
    # talons / perch line
    s.set(cx - 1, 30, "stone_lo"); s.set(cx + 1, 30, "stone_lo")
    # tiny key spring on the back
    if face in ("up", "left"):
        s.set(cx + (0 if face == "up" else 5), cy - 1 + (i % 2), "stone_hi")


def P_gear(s, cx, cy, r):
    for k in range(8):
        a = k * math.pi / 4
        s.set(cx + math.cos(a) * (r + 1), cy + math.sin(a) * (r + 1), "stone_hi" if k % 2 else "stone")
    s.set(cx, cy, "e_hi"); s.set(cx + 1, cy, "e_body")


P.PETS.clear()
P.PETS["pet_tick"] = dict(draw=draw_tick, name="Tick",
    desc="Tick, the clockwork owl (Svartalfheim pet): a brass egg-bodied owl with riveted feather-plate wings, iron ear tufts, "
         "a copper beak, two round rune-lens eyes and a little chest gear with a cold-blue core; hovers at shoulder height, "
         "ticking (finds hidden gears / clockwork doors)",
    hover={"lift": 0.7, "bob": 0.05, "hz": 1.0},
    light={"color": "#2ab4ff", "intensity": 4.0, "range": 3.2, "lift": 0.9, "fadeIn": 0.4,
           "pulse": {"min": 0.8, "max": 1.1, "hz": 2.0, "shape": "tick"}},
    aura="pet_aura_tick", pool="pet_pool_tick", particles=None, speed=2.4,
    look="NEON blue eyes + chest core in tick_neon.png (primary); tick.png is palette-safe (sky / flower_blue / cloth)")
NB = ("neon_blue_hi", "neon_blue", "neon_blue_lo")
P.FX.clear()
P.FX["pet_aura_tick"] = dict(fn=lambda: P.aura_orbit(61, NB, rx=9.0, ry=5.0, cy=17, rise=0.6, extra=8), kind="billboard", fps=8,
                              pivot=[16, 31], lift=0.0, follow_lift="hover", glow=True,
                              desc="neon-blue rune sparks orbiting Tick like clock ticks (NEON blue)")
P.FX["pet_pool_tick"] = dict(fn=lambda: P.pet_pool(62, NB, 11.0), kind="decal", fps=6, pivot=[16, 16], lift=0.02, glow=True,
                              desc="cold-blue light pool under Tick (NEON blue)")
P.FX["pet_pool_tick_safe"] = dict(fn=lambda: P.pet_pool(62, P.BLUE, 11.0), kind="decal", fps=6, pivot=[16, 16], lift=0.02, glow=True,
                              desc="palette-safe twin of the pool")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    safe, roles = P.build_sheet({**P.SLOTS_SAFE, **SAFE}); safe.save(OUT / "tick.png")
    neon, _ = P.build_sheet({**P.SLOTS_NEON, **NEONS}); neon.save(OUT / "tick_neon.png")
    meta = {"tool": "hearthmoor-art tick_gen (pets_gen layout)", "biome": "cozy-village", "frame": [P.FW, P.FH], "pivot": P.PIVOT,
            "ground_row": P.GROUND, "facings": list(P.FACINGS), "anims": P.ANIMS, "cols": P.COLS, "image": "tick_neon.png",
            "image_neon": "tick_neon.png", "image_lock_safe": "tick.png", "primary": "tick_neon.png",
            "neon_accents": {k: P.NEON[k] for k in NB}, "size": [safe.width, safe.height], "fx": "tick_fx.json", "roles": roles}
    (OUT / "tick.json").write_text(json.dumps(meta, indent=1))
    fa, fm, _ = P.build_fx(); fm["image"] = "tick_fx.png"
    fa.save(OUT / "tick_fx.png"); (OUT / "tick_fx.json").write_text(json.dumps(fm, indent=1))
    return safe, neon, fa


if __name__ == "__main__":
    main()
