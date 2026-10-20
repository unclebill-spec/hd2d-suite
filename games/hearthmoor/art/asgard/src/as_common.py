"""Niflheim shared bits: palette ramps (cozy-village palette only on sprites), a native-resolution canvas with shaded
primitives, a big-frame atlas writer (boss_sheet layout, any role kind), and the rotate-to-fall helper for die frames."""
import math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_lib"))
import hmart as H  # noqa: E402
from hmart import SP  # noqa: E402
import json
from PIL import Image

# ramps (hi, mid, lo) from the cozy-village palette. Light comes from the upper left.
R = dict(
    slate=("flower_blue", "cloth", "shadow"), moss=("grass", "moss", "leaf_deep"), rust=("roof_hi", "roof", "roof_lo"),
    grey=("stone_hi", "stone", "stone_lo"), leather=("timber_hi", "timber", "timber_lo"), snowfur=("plaster_hi", "plaster", "stone_hi"),
    darkfur=("stone", "stone_lo", "shadow"), brownfur=("timber_hi", "timber", "timber_lo"), cream=("plaster_hi", "plaster", "plaster_lo"),
    coat=("cloth", "shadow", "ink"), frostwool=("plaster_hi", "sky", "stone_hi"), ice=("white", "sky", "flower_blue"), icedeep=("sky", "flower_blue", "cloth"), gold=("flower_gold", "lamp", "timber_hi"),
    skin=("skin", "skin", "skin_lo"), ruddy=("skin", "skin_lo", "roof"), pale=("plaster_hi", "plaster", "plaster_lo"),
    black=("stone_lo", "shadow", "ink"), rock=("stone", "stone_lo", "shadow"), bluerock=("sky", "stone_lo", "shadow"),
    grass=("grass_hi", "grass", "moss"), rose=("flower_rose", "roof_hi", "roof"),
    ember=("plaster_lo", "stone_hi", "stone"), ashgrey=("stone_hi", "stone", "stone_lo"), copper=("roof_hi", "roof", "roof_lo"),
    fire=("white", "flower_gold", "lamp"), lava=("flower_gold", "lamp", "roof_hi"), coal=("stone", "stone_lo", "shadow"), obsidian=("stone_lo", "shadow", "ink"),
)


class Cv:
    """clipped pixel canvas over an HSprite (hard alpha, palette names)"""
    def __init__(s, sp):
        s.s, s.w, s.h = sp, len(sp.p[0]), len(sp.p)

    def set(s, x, y, c):
        x, y = int(round(x)), int(round(y))
        if c and 1 <= x < s.w - 1 and 1 <= y < s.h - 1:
            s.s.set(x, y, c)

    def get(s, x, y):
        x, y = int(round(x)), int(round(y))
        return s.s.p[y][x] if 0 <= x < s.w and 0 <= y < s.h else None

    def rect(s, x0, y0, x1, y1, c):
        for y in range(int(round(y0)), int(round(y1)) + 1):
            for x in range(int(round(x0)), int(round(x1)) + 1):
                s.set(x, y, c)

    def ell(s, cx, cy, rx, ry, fn, ang=0.0):
        rx, ry = max(rx, .5), max(ry, .5)
        m = int(max(rx, ry)) + 2
        ca, sa = math.cos(ang), math.sin(ang)
        for y in range(int(cy) - m, int(cy) + m + 1):
            for x in range(int(cx) - m, int(cx) + m + 1):
                dx, dy = x - cx, y - cy
                u, v = (dx * ca + dy * sa) / rx, (-dx * sa + dy * ca) / ry
                if u * u + v * v <= 1.0:
                    c = fn(u, v) if callable(fn) else fn
                    if c:
                        s.set(x, y, c)

    def seg(s, x0, y0, x1, y1, w, w1, ramp):
        """thick line, width w -> w1, shaded hi (left) / lo (right)"""
        n = int(max(abs(x1 - x0), abs(y1 - y0))) * 2 + 2
        for j in range(n + 1):
            t = j / n
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            r = (w + ((w1 if w1 is not None else w) - w) * t) / 2
            ri = int(r) + 1
            for dy in range(-ri, ri + 1):
                for dx in range(-ri, ri + 1):
                    if dx * dx + dy * dy <= r * r + 0.3:
                        l = dx / max(r, 1)
                        c = ramp[0] if l < -0.45 else ramp[2] if l > 0.45 else ramp[1]
                        s.set(x + dx, y + dy, c)

    def poly(s, pts, fn):
        ys = [p[1] for p in pts]; xs = [p[0] for p in pts]
        for y in range(int(min(ys)), int(max(ys)) + 1):
            for x in range(int(min(xs)), int(max(xs)) + 1):
                ins = False
                j = len(pts) - 1
                for i in range(len(pts)):
                    xi, yi = pts[i]; xj, yj = pts[j]
                    if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi:
                        ins = not ins
                    j = i
                if ins:
                    s.set(x, y, fn(x, y) if callable(fn) else fn)


def hsh(*a):
    v = 2166136261
    for x in a:
        for ch in str(x):
            v = ((v ^ ord(ch)) * 16777619) & 0xFFFFFFFF
        v = ((v ^ 0x9E) * 16777619) & 0xFFFFFFFF
    return (v & 0xFFFF) / 65536


def shade(ramp, u, v=0.0, vlo=0.8):
    if v < -0.8:
        return ramp[0]
    return ramp[0] if u < -0.35 else ramp[2] if (u > 0.45 or v > vlo) else ramp[1]


def rotate_fall(sp, deg, shift_x=0):
    """rotate the (un-outlined) sprite grid by deg (clockwise, about the foot centre) with nearest sampling, drop to the ground row"""
    h, w = len(sp.p), len(sp.p[0])
    cx, cy = w / 2, h - 2
    a = math.radians(deg); ca, sa = math.cos(a), math.sin(a)
    out = [[None] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            dx, dy = x - cx, y - cy
            sx = cx + dx * ca + dy * sa
            sy = cy - dx * sa + dy * ca
            ix, iy = int(math.floor(sx + .5)), int(math.floor(sy + .5))
            if 0 <= ix < w and 0 <= iy < h and sp.p[iy][ix] is not None:
                out[y][x] = sp.p[iy][ix]
    # drop so the lowest opaque row is h-2
    low = max((y for y in range(h) for x in range(w) if out[y][x] is not None), default=h - 2)
    d = (h - 2) - low
    feet = [x for y in range(h) for x in range(w) if out[y][x] is not None and y >= low - 2]
    shift_x = int(round(w / 2 - (min(feet) + max(feet) + 1) / 2)) if feet else 0
    sp.p = [[None] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if out[y][x] is not None and 0 <= y + d < h:
                xx = x + shift_x
                if 0 <= xx < w:
                    sp.p[y + d][xx] = out[y][x]


def sink(sp, i, cv, cols=None):
    """boss die: the figure sinks into the ice (kneels, drops, only crown + shoulders remain) behind a rimed ice mound"""
    h, w = len(sp.p), len(sp.p[0])
    G = h - 2
    top = min((y for y in range(h) for x in range(w) if sp.p[y][x] is not None), default=0)
    Ht = G - top
    d = int(Ht * [0.0, 0.16, 0.42, 0.74][i])
    src = [r[:] for r in sp.p]
    sp.p = [[None] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if src[y][x] is not None and 0 <= y + d < h:
                sp.p[y + d][x] = src[y][x]
    if i == 0:
        return
    ry = [0, 10, 18, 26][i]
    rx = min(Ht * [0, .27, .31, .33][i], w * .44)
    c0, c1, c2, c3 = cols or ("white", "sky", "flower_blue", "cloth")
    cv.ell(w / 2, G - ry * .35, rx, ry, lambda u, v: c0 if (v < -.55 and u < .2) else c1 if (u < .35 and v < .3) else c2 if v < .75 else c3)
    for j in range(5 + i * 2):
        a = (j - (4 + i * 2) / 2) * rx * .18
        cv.rect(w / 2 + a, G - ry * .3 - 2 - (j % 3), w / 2 + a, G - ry * .3 - 1, c0)
    cv.rect(w / 2 - rx * .9, G, w / 2 + rx * .9, G, c3)


def big_frame(draw, facing, anim, i, w, h, post=None):
    """one big frame (no mirror yet): draw(cv, face, anim, i) onto an HSprite w x h, ink outline, right = mirrored left"""
    sp = SP.HSprite(H.PAL, w, h)
    face = "left" if facing == "right" else facing
    cv = Cv(sp)
    draw(cv, face, anim, i)
    if anim == "die" and getattr(draw, "die_mode", None) == "sink":
        sink(sp, i, cv, getattr(draw, 'sink_cols', None))
    elif anim == "die" and getattr(draw, "fall", True):
        ang = [0, 14, 52, 88][i]
        if ang:
            rotate_fall(sp, ang if face != "up" else -ang)
    for y in range(h):
        for x in range(w):
            if x in (0, w - 1) or y in (0, h - 1):
                sp.p[y][x] = None
    sp.outline("ink")
    if getattr(draw, "post", None):
        draw.post(sp, anim, i)
    return sp.mirror() if facing == "right" else sp


def write_big(out: Path, name, roles, frame, kind="human", pivot=None):
    """roles {id: dict(draw, scale, desc, anims, ht, [light, stats_hint, enemy, boss, named, notes])} -> png/json (boss_sheet layout:
    idle 0-3 | walk 4-7 | cast 8-11 | attack 12-15 | die 24-27; pivot = bottom centre)"""
    out.mkdir(parents=True, exist_ok=True)
    fw, fh = frame
    ANIMS = SP.ANIMS
    cols = max(SP.COLS, max(ANIMS[a]["start"] + ANIMS[a]["count"] for r in roles.values() for a in r["anims"]))
    im = Image.new("RGBA", (fw * cols, fh * 4 * len(roles)), (0, 0, 0, 0))
    meta = {"tool": "hd2d boss_sheet (niflheim big frames)", "biome": H.BIOME, "frame": [fw, fh], "pivot": [fw // 2, fh], "ground_row": fh - 1,
            "facings": list(H.FACINGS), "anims": ANIMS, "cols": cols, "image": f"{name}.png", "size": [im.width, im.height], "roles": {}}
    # ground_row fh-2: the hmart big-frame convention (row fh-1 is the cleared border) -> pivot y is fh
    for ri, (role, r) in enumerate(roles.items()):
        frames = []
        for fi, facing in enumerate(H.FACINGS):
            for anim in r["anims"]:
                for i in range(4):
                    x, y = (ANIMS[anim]["start"] + i) * fw, (ri * 4 + fi) * fh
                    im.paste(big_frame(r["draw"], facing, anim, i, fw, fh).image(), (x, y))
                    frames.append({"name": f"{role}_{facing}_{anim}{i}", "facing": facing, "anim": anim, "i": i, "x": x, "y": y, "w": fw, "h": fh,
                                   "pivot": [x + fw // 2, y + fh]})
        m = {"row": ri * 4, "kind": r.get("kind", kind), "scale": r["scale"], "desc": r["desc"], "anims": list(r["anims"]),
             "size_bounds": [[10, fw - 2], [8, fh]], "caster": False, "frames": frames}
        for k in ("enemy", "boss", "named", "light", "stats_hint", "notes", "combat_scale"):
            if r.get(k) is not None:
                m[k] = r[k]
        meta["roles"][role] = m
    assert im.width <= 4096 and im.height <= 4096, im.size
    im.save(out / f"{name}.png")
    H.write_json(out / f"{name}.json", meta)
    return H.check_sprite(out / f"{name}.png")
