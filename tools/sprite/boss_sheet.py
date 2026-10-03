"""hd2d boss sheets (stage 3): big foes drawn NATIVELY at their size on their own sheet (never an upscaled small sprite).

Style-lock boss-scale override: mini-bosses / rares ~2.5x the player's height, bosses 5x+. Same texel density,
hard alpha, 1 px ink outline, biome palette. A sheet uses the main atlas's column layout (idle 0-3, walk 4-7,
attack 12-15, die 24-27) with its own frame size, so the engine only swaps frame size + texture per role.

    python3 tools/sprite/boss_sheet.py --biome cozy-village --roles eldergolem --out <area>/public/art/sprite

  eldergolem  Mossheart, the elder golem (Mossglen mini-boss), 50x80 frame (~2.5x a 32 px hero)
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sprite as SP  # noqa: E402
from roles_enemies import ell, rect, shader  # noqa: E402

BOSS = {
    "eldergolem": {"frame": (50, 80), "scale": 2.5, "anims": ("idle", "walk", "attack", "die"),
                   "desc": "Mossheart the elder golem (mini-boss, ~2.5x): dark ancient stone blocks, amber crystal crown, glowing gold rune glyphs, glow-flowers in thick moss"},
}


def eldergolem(s, face, anim, i):
    W, H = s.w, s.h
    KX, KY = 2.05, 2.5                                 # golem-space (20x32) -> native 50x80 coordinates, drawn fresh at full res
    X = lambda x: 25 + (x - 9.5) * KX                  # noqa: E731
    Y = lambda y: (H - 2) - (30 - y) * KY              # noqa: E731
    def E(cx, cy, rx, ry, col, fn=None):
        ell(s, X(cx), Y(cy), rx * KX, ry * KY, col, fn)
    def R(x0, y0, x1, y1, col):
        rect(s, round(X(x0)), round(Y(y0)), round(X(x1)), round(Y(y1)), col)
    hi, mid, lo, deep = "stone", "stone_lo", "shadow", "ink"
    rune, hot = "lamp", "white"
    b = 0; lift_l = lift_r = 0; arms = "rest"; crack = 0; dust = False
    if anim == "idle":
        b = [0, 0, 0.5, 0.5][i]
    elif anim == "walk":
        b = [0, 0.5, 0, 0.5][i]; lift_l, lift_r = [(0, 0), (0.5, 0), (0, 0), (0, 0.5)][i]   # a heavy stomp: the foot barely leaves the ground
    elif anim == "attack":
        arms = ["up", "high", "slam", "mid"][i]; b = [0, -0.6, 1.0, 0.5][i]; dust = i == 2
    elif anim == "die":
        crack = i + 1; b = [0.5, 1.5, 0, 0][i]
        if crack >= 3:
            rune, hot = "flower_gold", "flower_gold"
    side = face == "left"
    if anim == "die" and i >= 2:                       # a heap of dark stone blocks, moss, the last runes cooling
        top = 21 if i == 2 else 24
        E(9.5, 28, 9.2 if i == 2 else 8.4, 30 - top - 1.2, mid, shader(X(9.5), 9 * KX, hi, mid, lo))
        for (x, y) in ((4, 26), (8, 24), (13, 25), (15.5, 28), (6, 29), (11, 28), (2.5, 29)):
            if y >= top:
                R(x, y, x + 1.6, y + 0.8, lo); R(x, y, x + 1.6, y, hi)
        for (x, y) in ((7, top + 1), (12, top + 1.5), (3, 29), (16, 28.5)):
            R(x, y, x + 1, y + 0.4, "moss"); s.set(round(X(x)), round(Y(y)) - 1, "grass_hi")
        if i == 2:
            for (x, y) in ((9, 26), (14, 27), (5, 27.5)):
                s.set(round(X(x)), round(Y(y)), "lamp"); s.set(round(X(x)) + 1, round(Y(y)), "flower_gold")
        R(1.5, 30, 17.5, 30, lo)
        return
    # legs: stacked blocks
    legs = [(5.6, lift_l), (11, lift_r)] if side else [(3.6, lift_l), (12, lift_r)]
    for lx, lift in legs:
        R(lx, 24.6 + b, lx + 4, 30 - lift, lo if lx > 9 else mid)
        R(lx, 24.6 + b, lx + 4, 24.6 + b, hi)
        R(lx, 27.4 - lift, lx + 4, 27.4 - lift, deep)            # block seam
        R(lx - 0.3, 29.4 - lift, lx + 4.3, 30 - lift, lo)        # foot slab
    # body: a huge boulder torso with block seams
    bcx, rx = (10.5, 7.8) if side else (9.5, 8.4)
    E(bcx, 18 + b, rx, 7.8, mid, shader(X(bcx), rx * KX, hi, mid, lo))
    for k, yy in enumerate((14.5, 18, 21.5)):                # horizontal seams, offset blocks (ancient masonry)
        y = round(Y(yy + b))
        for x in range(round(X(bcx - rx + 1.2)), round(X(bcx + rx - 1.2))):
            if s.p[y][x]:
                s.set(x, y, deep if (x + k) % 9 else lo)
        for x0 in range(round(X(bcx - rx)) + 5 + 4 * k, round(X(bcx + rx)) - 3, 11):
            for y2 in range(y + 1, y + 8):
                if 0 <= y2 < H and s.p[y2][x0]:
                    s.set(x0, y2, deep)
    # head
    if side:
        E(12, 11 + b, 5.8, 4.8, mid, shader(X(12), 5.8 * KX, hi, mid, lo))
        R(2.6, 8.8 + b, 9, 14 + b, mid); R(2.6, 8.8 + b, 3.6, 14 + b, hi); R(2.6, 8 + b, 9, 8.2 + b, hi)
        R(2, 10 + b, 8.4, 10.3 + b, lo); R(2.6, 13.8 + b, 8.4, 14 + b, lo)
    else:
        E(9.5, 9 + b, 4.8, 3.9, mid, shader(X(9.5), 4.8 * KX, hi, mid, lo))
        R(6, 11.4 + b, 13, 11.6 + b, lo)                     # jaw line
    # thick moss on head and shoulders, with grass blades and glow-flowers
    mossy = ((9.5, 6.6, 3.6), (4.2, 12, 2.6), (15, 12, 2.6)) if not side else ((12, 7, 4.4), (5, 8.2, 2.2))
    for (mx, my, mr) in mossy:
        E(mx, my + b, mr, 1.1, "moss")
        for k in range(int(mr * KX)):
            x = round(X(mx - mr) + k * 2); y = round(Y(my + b)) - 2 - (k % 3 == 0)
            s.set(x, y, "grass_hi" if k % 2 else "grass")
    flowers = ((6.2, 6), (12.6, 6.2), (3.4, 11.4), (16, 11.6), (10.4, 5.8)) if not side else ((11, 6.4), (14.4, 6.8), (5.4, 7.6))
    for k, (fx, fy) in enumerate(flowers):
        x, y = round(X(fx)), round(Y(fy + b))
        c = "flower_rose" if (k + i) % 2 else "flower_gold"
        s.set(x, y, c); s.set(x - 1, y, c); s.set(x + 1, y, c); s.set(x, y - 1, c); s.set(x, y, "white" if k % 2 == 0 else c)
    # crown of amber crystals (faceted shards: dark edge, gold body, white glint)
    crown = ((4.2, 7.4, 2.4), (6.4, 6.4, 3.0), (8.6, 7.2, 2.2)) if side else ((6.6, 5.6, 2.2), (8.6, 4.6, 3.0), (10.6, 4.6, 3.0), (12.6, 5.6, 2.2))
    for k, (cx, cy, hgt) in enumerate(crown):
        x0, yb = round(X(cx)), round(Y(cy + b))
        n = round(hgt * KY)
        for d in range(n):
            w = max(0, 2 - d * 3 // n)
            for x in range(x0 - w, x0 + w + 1):
                s.set(x, yb - d, "flower_gold" if x > x0 else rune)
            s.set(x0 + w, yb - d, "timber")
        s.set(x0 - 1, yb - n + 2, hot if (k + i) % 2 == 0 else rune); s.set(x0, yb - n + 1, hot)
    # eyes + rune glyphs
    if face == "down":
        for ex in (7.6, 11.4):
            x, y = round(X(ex)), round(Y(9 + b))
            rect(s, x - 1, y, x + 1, y + 1, rune if crack < 3 else lo); s.set(x, y, hot if crack < 2 else rune)
            rect(s, x - 2, y - 1, x + 2, y - 1, deep)
        s.set(round(X(9.5)), round(Y(7.6 + b)), hot); s.set(round(X(9.5)) + 1, round(Y(7.6 + b)), rune)   # third eye
        cx = round(X(9.5))
        for k, y in enumerate(range(round(Y(13.6 + b)), round(Y(24 + b)))):   # the heart seam: a zig-zag rune channel
            x = cx + (1 if (k // 3) % 2 else -1)
            s.set(x, y, hot if (k + crack + i) % 7 == 0 else rune); s.set(x + 1, y, "flower_gold")
        for (gx, gy) in ((4.6, 16), (14.4, 16.4), (5.4, 21), (13.6, 20.6)):   # four glyphs on the flanks: little runic marks
            x, y = round(X(gx)), round(Y(gy + b))
            for (dx, dy) in ((0, 0), (0, 1), (0, 2), (1, 1), (-1, 1), (1, -1)):
                s.set(x + dx, y + dy, rune)
            s.set(x, y + 1, hot)
        for lx in (5.6, 14):
            x, y = round(X(lx)), round(Y(26.4 + b))
            s.set(x, y, rune); s.set(x, y + 1, rune); s.set(x + 1, y + 1, hot)
    elif face == "up":
        for k, y in enumerate(range(round(Y(14 + b)), round(Y(22 + b)))):
            s.set(round(X(9.6)) + (k % 2), y, lo)
        for (gx, gy) in ((6.4, 13.4), (12.8, 13.4), (8, 19), (11.2, 19)):
            x, y = round(X(gx)), round(Y(gy + b))
            s.set(x, y, rune); s.set(x + 1, y, rune); s.set(x, y + 1, hot); s.set(x - 1, y + 1, rune)
    else:
        x, y = round(X(4)), round(Y(11 + b))
        rect(s, x - 1, y, x + 1, y + 1, rune if crack < 3 else lo); s.set(x - 1, y, hot)
        rect(s, x - 2, y - 1, x + 2, y - 1, deep)
        for k, yy in enumerate(range(round(Y(15.6 + b)), round(Y(24 + b)))):
            s.set(round(X(9.6)) + (k // 3) % 2, yy, hot if (k + i) % 6 == 0 else rune)
        for (gx, gy) in ((12.6, 15), (13.6, 19.4)):
            x, y = round(X(gx)), round(Y(gy + b))
            for (dx, dy) in ((0, 0), (0, 1), (0, 2), (1, 1)):
                s.set(x + dx, y + dy, rune)
    if crack:                                           # hit / death cracks spreading across the blocks
        pts = [(6, 14), (7, 15), (7.6, 16), (13, 20), (12.4, 21), (11.6, 22.4)]
        for (x, y) in pts[: 2 + crack]:
            s.set(round(X(x)), round(Y(y + b)), "white" if crack == 1 else deep)
    # arms: three-block arms ending in huge fists
    def fist(cx, cy, r=2.8):
        E(cx, cy, r, r * 0.92, mid, shader(X(cx), r * KX, hi, mid, lo))
        x, y = round(X(cx)), round(Y(cy))
        rect(s, x - 3, y, x + 2, y, deep)               # knuckle line
        s.set(x - 2, y - 2, rune if crack < 3 else lo)  # a rune on each fist
    if side:
        if arms == "rest":
            sw = 0.8 if anim == "walk" and i % 2 else 0
            R(4.6, 15 + b, 7.4, 21.6 + b + sw, mid); R(4.6, 15 + b, 5.2, 21.6 + b, hi); R(4.6, 18 + b, 7.4, 18.2 + b, deep)
            fist(6, 24.4 + b + sw, 3.0)
        elif arms in ("up", "high"):
            fist(7, 3.6 + b if arms == "high" else 6.6 + b); R(7.8, 8 + b, 9.6, 13 + b, mid)
        elif arms == "slam":
            fist(3.6, 27, 3.0); R(4.6, 20 + b, 7.4, 24 + b, mid)
        else:
            R(4.6, 15 + b, 7.4, 18 + b, mid); fist(3.6, 20 + b)
    else:
        if arms == "rest":
            sw = 0.8 if anim == "walk" and i % 2 else 0
            for (ax, s2) in ((1.6, sw), (17.4, -sw)):
                R(ax - 1.2, 13 + b, ax + 1.2, 17 + b + s2, mid if ax < 9 else lo)
                fist(ax, 19.4 + b + s2)
        elif arms in ("up", "high"):
            y = 2.8 + b if arms == "high" else 5.8 + b
            fist(4.8, y); fist(14.2, y)
            R(3.8, y + 2.4, 5.4, 12 + b, mid); R(13.6, y + 2.4, 15.2, 12 + b, lo)
        elif arms == "slam":
            fist(4.8, 27, 3.0); fist(14.2, 27, 3.0)
            R(3.8, 20 + b, 5.4, 24.6, mid); R(13.6, 20 + b, 15.2, 24.6, lo)
        else:
            fist(2.6, 15 + b); fist(16.4, 15 + b)
    if dust:
        for (x, y) in ((0, 29), (1, 27.6), (18.6, 28.4), (19, 29.4), (9, 30), (-0.2, 30), (17.6, 30)):
            s.set(round(X(x)), round(Y(y)), "plaster_lo"); s.set(round(X(x)) + 1, round(Y(y)), "plaster_hi")
        s.set(round(X(10)), round(Y(29)), "flower_gold")


DRAW = {"eldergolem": eldergolem}


def frame(pal, role, facing, anim, i):
    fw, fh = BOSS[role]["frame"]
    s = SP.HSprite(pal, fw, fh)
    DRAW[role](s, "left" if facing == "right" else facing, anim, i)
    for y in range(fh):                                 # 1 px margin so the outline always closes inside the frame
        for x in range(fw):
            if x in (0, fw - 1) or y in (0, fh - 1):
                s.p[y][x] = None
    s.outline("ink")
    return s.mirror() if facing == "right" else s


def build(biome="cozy-village", roles=("eldergolem",), out="public/art/sprite", project=None, name="boss"):
    """write <name>.png + <name>.json (same meta shape as the actor atlas) and return their paths"""
    pal = SP.Pal(SP.load_biome(biome, project))
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    fw, fh = BOSS[roles[0]]["frame"]
    assert all(BOSS[r]["frame"] == (fw, fh) for r in roles), "one frame size per boss sheet"
    cols = SP.COLS if hasattr(SP, "COLS") else 28
    cols = max(cols, max(SP.ANIMS[a]["start"] + SP.ANIMS[a]["count"] for r in roles for a in BOSS[r]["anims"]))
    from PIL import Image
    im = Image.new("RGBA", (fw * cols, fh * 4 * len(roles)), (0, 0, 0, 0))
    meta = {"tool": "hd2d boss_sheet", "biome": biome, "frame": [fw, fh], "pivot": [fw // 2, fh], "ground_row": fh - 1,
            "facings": list(SP.FACINGS), "anims": SP.ANIMS, "cols": cols, "image": f"{name}.png", "size": [im.width, im.height], "roles": {}}
    for ri, role in enumerate(roles):
        frames = []
        for fi, facing in enumerate(SP.FACINGS):
            for anim in BOSS[role]["anims"]:
                for i in range(4):
                    x, y = (SP.ANIMS[anim]["start"] + i) * fw, (ri * 4 + fi) * fh
                    im.paste(frame(pal, role, facing, anim, i).image(), (x, y))
                    frames.append({"name": f"{role}_{facing}_{anim}{i}", "facing": facing, "anim": anim, "i": i, "x": x, "y": y,
                                   "w": fw, "h": fh, "pivot": [x + fw // 2, y + fh]})
        meta["roles"][role] = {"row": ri * 4, "kind": "enemy", "enemy": True, "boss": True, "scale": BOSS[role]["scale"],
                               "desc": BOSS[role]["desc"], "anims": list(BOSS[role]["anims"]),
                               "size_bounds": [[12, fw - 2], [12, fh]], "caster": False, "frames": frames}
    assert im.height <= 4096 and im.width <= 4096, "boss sheet must fit a 4096 px texture"
    im.save(out / f"{name}.png")
    SP.write_json(out / f"{name}.json", meta)
    return {"image": str(out / f"{name}.png"), "json": str(out / f"{name}.json"), "size": [im.width, im.height]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--biome", default="cozy-village"); ap.add_argument("--roles", default="eldergolem")
    ap.add_argument("--out", default="public/art/sprite"); ap.add_argument("--project", default=None)
    ap.add_argument("--name", default="boss"); ap.add_argument("--preview", default=None, help="write a 3x nearest preview PNG here")
    a = ap.parse_args(argv)
    r = build(a.biome, tuple(a.roles.split(",")), a.out, a.project, a.name)
    if a.preview:
        from PIL import Image
        im = Image.open(r["image"]); big = im.resize((im.width * 3, im.height * 3), Image.NEAREST)
        bg = Image.new("RGBA", big.size, (236, 222, 190, 255)); bg.alpha_composite(big); bg.save(a.preview)
    print(r)


if __name__ == "__main__":
    main()
