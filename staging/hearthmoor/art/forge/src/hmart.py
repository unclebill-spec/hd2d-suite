"""hmart: shared staging helpers for Hearthmoor art packs (Art seat, 2026-10-05).

Reads the hd2d-suite repo READ-ONLY (imports tools/sprite, tools/kit, tools/check-sprite, hd2d_common) and writes
everything into /workspace/hearthmoor-staging/art/<pack>/. Nothing here writes into the repo.

  - actor atlases in the exact `hd2d sprite` format (20x32 frames, feet pivot [10,32], rows down/up/left/right,
    idle 0-3 | walk 4-7 | cast 8-11 | attack 12-15 | die 24-27), checked with the repo's check-sprite
  - boss sheets in the exact `hd2d boss_sheet` format (native big frames, same column layout)
  - gamefx atlases in the exact `hd2d portal` / `hd2d spells` JSON format (cell px, rows = effects)
  - kit .glb pieces built with the repo's kit.py / meshlib (pieces(K) modules, like kit_harbor.py)
  - 16 px item icon sheets like games/hearthmoor/build.py draw_icons()
  - a tiny numpy rasteriser that previews kit pieces at sprite texel density (18 px / m, locked 3/4 camera)
  - 4x nearest contact sheets on dark panels with dithered light pools (hard alpha, no blur, no bloom)
"""
from __future__ import annotations

import json
import math
import sys
import types
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

SUITE = Path("/workspace/hd2d-suite")
sys.path.insert(0, str(SUITE))
sys.path.insert(0, str(SUITE / "tools/sprite"))
sys.path.insert(0, str(SUITE / "tools/kit"))
import sprite as SP  # noqa: E402  (repo sprite writer, read-only import)
from roles_enemies import ell, rect, shader  # noqa: E402
from hd2d_common import hex2rgb, rgb2hex, mix, rng, write_json, load_tool  # noqa: E402

BIOME = "cozy-village"
PAL = SP.Pal(SP.load_biome(BIOME))
C = dict(PAL.c)  # name -> hex
# The approved NEON glow accents (same hexes as tools/portal/portal.py + tools/kit/kit_bifrost.py). Glow pixels only.
NEON = {"neon_red": "#e0302a", "neon_red_lo": "#a81c22", "neon_red_hi": "#ff5a4a",
        "neon_violet": "#a45cf0", "neon_violet_hi": "#d4a8ff", "neon_violet_lo": "#6a34b8",
        "neon_blue": "#2ab4ff", "neon_blue_hi": "#a6ecff", "neon_blue_lo": "#1c62d8",
        # added 2026-10-05 for Bill's glow orbs / fireflies / bioluminescence (environment glow pixels only)
        "neon_green": "#3cf08a", "neon_green_hi": "#b8ffd4", "neon_green_lo": "#14a85a",
        "neon_pink": "#ff4fc8", "neon_pink_hi": "#ffb4ea", "neon_pink_lo": "#b82a8c"}
COLD = {"cold": "#5ab4f0", "cold_hi": "#d8f4ff", "cold_lo": "#2a6cb0"}   # kit cold-fire glow (kit_harbor / kit_bifrost)
ALLC = {**C, **NEON, **COLD}
FW, FH = SP.FW, SP.FH
ANIMS = SP.ANIMS
FACINGS = SP.FACINGS

try:
    FONT_B = ImageFont.truetype("DejaVuSans-Bold.ttf", 15)
    FONT = ImageFont.truetype("DejaVuSans.ttf", 12)
    FONT_S = ImageFont.truetype("DejaVuSans.ttf", 10)
    FONT_T = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
except OSError:
    FONT_B = FONT = FONT_S = FONT_T = ImageFont.load_default()


def rgba(name, a=255):
    return tuple(hex2rgb(ALLC[name] if name in ALLC else name)) + (a,)


# ============================================================== actors (20x32, repo format)
def human(spec_kw, extra=None):
    """a human role spec built with the repo's _r() defaults (sprite.py), plus an optional extra draw hook"""
    base = dict(kind="human", layout="adult", hair="timber", hairstyle="short", hat=None, hatc="plaster_hi",
                shirt="cloth", pants="timber_lo", shoes="shadow", skin="skin", apron=None, overalls=None,
                vest=None, skirt=None, cloak=None, scarf=None, satchel=None, item=None, beard=None,
                shawl=None, cane=False, hunch=0, stripes=None, boots=False, desc="",
                glasses=False, caster=False, animal=None)
    base.update(spec_kw)
    base["_extra"] = extra
    return base


def human_frame(spec, facing, anim, i):
    """sprite.py human_frame, re-run here so an extra hook (ears, glow trims, props) draws BEFORE the ink outline"""
    s = SP.HSprite(PAL)
    face = "left" if facing == "right" else facing
    L = SP.LAYOUTS[spec["layout"]]
    bob = blink = lift_l = lift_r = swing = stride = lift_b = 0
    sp = spec
    if anim == "cast":
        bob = [0, -1, -1, 0][i]
        sp = {**spec, "_cast": i, "item": None}
    elif anim == "idle":
        bob, blink = SP.IDLE[i]
        sp = {**spec, "_idle": i}
    elif face in ("down", "up"):
        bob, lift_l, lift_r, swing = SP.WALK_FRONT[i]
    else:
        bob, stride, lift_b = SP.WALK_SIDE[i]
    bob += sp["hunch"]
    if face == "up":
        lift_l, lift_r = lift_r, lift_l
        swing = -swing
    SP.draw_legs(s, sp, L, face, bob, lift_l, lift_r, stride, lift_b)
    SP.draw_body(s, sp, L, face, bob, swing, stride, anim, i)
    SP.draw_head(s, sp, L, face, bob, blink)
    SP.draw_extras(s, sp, L, face, bob, swing, stride)
    if spec.get("_extra"):
        spec["_extra"](s, sp, L, face, bob, anim, i)
    s.outline("ink")
    if facing == "right":
        s.mirror()
    return s


def drawn_frame(draw, facing, anim, i, w=FW, h=FH):
    """enemy / creature frame from a draw(s, face, anim, i) function (roles_enemies.py convention)"""
    s = SP.HSprite(PAL, w, h)
    face = "left" if facing == "right" else facing
    draw(s, face, anim, i)
    for y in range(h):
        for x in range(w):
            if x in (0, w - 1) or y in (0, h - 1):
                s.p[y][x] = None
    s.outline("ink")
    return s.mirror() if facing == "right" else s


ROLE_SIZE = {"human": [[14, 24], [24, 40]], "creature": [[10, 24], [10, 40]],
             "enemy": [[6, 20], [6, 32]], "summon": [[4, 20], [6, 32]]}


def role_frame(r, facing, anim, i):
    if r.get("draw"):
        return drawn_frame(r["draw"], facing, anim, i, *r.get("frame", (FW, FH)))
    return human_frame(r["spec"], facing, anim, i)


def write_actors(out: Path, name: str, roles: dict):
    """roles: {role: {spec | draw, kind, desc, anims, enemy?, named?}} -> <name>.png/.json (+ strips, preview)
    in the hd2d sprite atlas format, then the repo's check-sprite on it. Returns the check report."""
    out.mkdir(parents=True, exist_ok=True)
    cols = max(max(ANIMS[a]["start"] + ANIMS[a]["count"] for a in r["anims"]) for r in roles.values())
    cols = max(cols, SP.COLS)
    atlas = Image.new("RGBA", (FW * cols, FH * 4 * len(roles)), (0, 0, 0, 0))
    meta = {"tool": "hd2d sprite", "biome": BIOME, "seed": 104, "frame": [FW, FH], "pivot": [10, 32],
            "ground_row": SP.GROUND_ROW, "facings": list(FACINGS), "anims": ANIMS, "cols": cols,
            "image": f"{name}.png", "size": [atlas.width, atlas.height], "roles": {}}
    for ri, (role, r) in enumerate(roles.items()):
        frames = []
        strip = Image.new("RGBA", (FW * cols, FH * 4), (0, 0, 0, 0))
        for fi, facing in enumerate(FACINGS):
            for anim in r["anims"]:
                for i in range(4):
                    col = ANIMS[anim]["start"] + i
                    im = role_frame(r, facing, anim, i).image()
                    atlas.paste(im, (col * FW, (ri * 4 + fi) * FH))
                    strip.paste(im, (col * FW, fi * FH))
                    frames.append({"name": f"{role}_{facing}_{anim}{i}", "facing": facing, "anim": anim, "i": i,
                                   "x": col * FW, "y": (ri * 4 + fi) * FH, "w": FW, "h": FH,
                                   "pivot": [col * FW + 10, (ri * 4 + fi) * FH + 32]})
        (out / "strips").mkdir(exist_ok=True)
        strip.save(out / "strips" / f"{role}.png")
        kind = r.get("kind", "human")
        meta["roles"][role] = {"row": ri * 4, "kind": kind, "desc": r["desc"], "size_bounds": ROLE_SIZE[kind],
                               "caster": "cast" in r["anims"], "anims": list(r["anims"]), "frames": frames}
        for k in ("enemy", "named", "summon"):
            if r.get(k):
                meta["roles"][role][k] = True
        for k in ("light", "stats_hint", "notes"):
            if r.get(k):
                meta["roles"][role][k] = r[k]
    atlas.save(out / f"{name}.png")
    write_json(out / f"{name}.json", meta)
    return check_sprite(out / f"{name}.png")


def check_sprite(png: Path, max_colors=20):
    cs = load_tool("check-sprite")
    rep = cs.check(png, None, None, max_colors)
    return rep


# ============================================================== boss sheets (repo boss_sheet format)
def write_boss(out: Path, name: str, roles: dict):
    """roles: {role: {draw, frame:(w,h), scale, desc, anims}} -> <name>.png/.json like tools/sprite/boss_sheet.py"""
    out.mkdir(parents=True, exist_ok=True)
    fw, fh = next(iter(roles.values()))["frame"]
    assert all(r["frame"] == (fw, fh) for r in roles.values()), "one frame size per boss sheet"
    cols = max(SP.COLS, max(ANIMS[a]["start"] + ANIMS[a]["count"] for r in roles.values() for a in r["anims"]))
    im = Image.new("RGBA", (fw * cols, fh * 4 * len(roles)), (0, 0, 0, 0))
    meta = {"tool": "hd2d boss_sheet", "biome": BIOME, "frame": [fw, fh], "pivot": [fw // 2, fh], "ground_row": fh - 1,
            "facings": list(FACINGS), "anims": ANIMS, "cols": cols, "image": f"{name}.png", "size": [im.width, im.height],
            "roles": {}}
    for ri, (role, r) in enumerate(roles.items()):
        frames = []
        for fi, facing in enumerate(FACINGS):
            for anim in r["anims"]:
                for i in range(4):
                    x, y = (ANIMS[anim]["start"] + i) * fw, (ri * 4 + fi) * fh
                    im.paste(drawn_frame(r["draw"], facing, anim, i, fw, fh).image(), (x, y))
                    frames.append({"name": f"{role}_{facing}_{anim}{i}", "facing": facing, "anim": anim, "i": i,
                                   "x": x, "y": y, "w": fw, "h": fh, "pivot": [x + fw // 2, y + fh]})
        meta["roles"][role] = {"row": ri * 4, "kind": "enemy", "enemy": True, "boss": True, "scale": r["scale"],
                               "desc": r["desc"], "anims": list(r["anims"]), "size_bounds": [[12, fw - 2], [12, fh]],
                               "caster": False, "frames": frames}
        for k in ("light", "notes", "stats_hint"):
            if r.get(k):
                meta["roles"][role][k] = r[k]
    assert im.width <= 4096 and im.height <= 4096
    im.save(out / f"{name}.png")
    write_json(out / f"{name}.json", meta)
    return check_sprite(out / f"{name}.png")


# ============================================================== gamefx (repo portal / spells format)
class Fx:
    """an effect frame: like tools/spells Frame but any square cell size and the full NEON set (glow pixels only)"""

    def __init__(self, cell=32):
        self.n = cell
        self.p = [[None] * cell for _ in range(cell)]

    def set(self, x, y, c):
        x, y = int(round(x)), int(round(y))
        if c and 0 <= x < self.n and 0 <= y < self.n:
            if c not in ALLC:
                raise KeyError(c)
            self.p[y][x] = c

    def get(self, x, y):
        x, y = int(round(x)), int(round(y))
        return self.p[y][x] if 0 <= x < self.n and 0 <= y < self.n else None

    def star(self, x, y, size, core="white", arm="lamp", tip="flower_gold"):
        self.set(x, y, core)
        for k in range(1, size + 1):
            c = arm if k < size else tip
            for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)):
                self.set(x + dx, y + dy, c)

    def disk(self, cx, cy, r, cols, sq=1.0):
        for y in range(self.n):
            for x in range(self.n):
                d = math.hypot(x - cx, (y - cy) / sq)
                if d <= r:
                    self.set(x, y, cols[min(len(cols) - 1, int(d / max(r, 0.01) * len(cols)))])

    def ring(self, cx, cy, rx, ry, c, frac=1.0, start=0.0, dots=0):
        n = max(24, int((rx + ry) * 4))
        for i in range(int(n * frac)):
            if dots and i % dots:
                continue
            a = start + i / n * math.tau
            self.set(cx + math.cos(a) * rx, cy + math.sin(a) * ry, c)

    def line(self, x0, y0, x1, y1, c, every=1):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for i in range(n):
            if i % every == 0:
                t = i / max(1, n - 1)
                self.set(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, c)

    def image(self):
        im = Image.new("RGBA", (self.n, self.n), (0, 0, 0, 0))
        px = im.load()
        for y in range(self.n):
            for x in range(self.n):
                c = self.p[y][x]
                if c:
                    px[x, y] = rgba(c)
        return im


DECAL_SQUASH = math.sin(math.radians(36))


def pool_frames(cols, cell=32, frames=6, seed="pool", rmax=None):
    """a dithered ground light pool (pre-squashed decal) in three colours hi / mid / lo, the edge breathing"""
    out = []
    R = rng(104, seed)
    jit = [[R.random() for _ in range(cell)] for _ in range(cell)]
    c = cell / 2
    for f in range(frames):
        F = Fx(cell)
        fl = [1.0, 0.95, 0.98, 0.92, 1.0, 0.96, 0.99, 0.94][f % 8]
        rx = (rmax or (c - 1)) * fl
        for y in range(cell):
            for x in range(cell):
                d = math.hypot(x - c + 0.5, (y - c + 0.5) / DECAL_SQUASH) / rx
                if d > 1:
                    continue
                dens = (1 - d) ** 0.8 + 0.08
                if d < 0.22 or ((x + y + f) % 2 == 0 and jit[y][x] < dens):
                    F.set(x, y, cols[0] if d < 0.3 else cols[1] if d < 0.7 else cols[2])
        F.ring(c - 0.5, c - 0.5, rx, rx * DECAL_SQUASH, cols[1], 1.0, start=f * 0.19, dots=4)
        out.append(F)
    return out


def write_fx(out: Path, name: str, effects: dict, cell: int):
    """effects: {fx: {fn: () -> [Fx], fps, loop, kind, pivot, lift, glow, light, notes}} -> <name>.png/.json + strips"""
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for k, e in effects.items():
        rows.append((k, e, e["fn"]()))
    cols = max(len(fr) for _, _, fr in rows)
    atlas = Image.new("RGBA", (cell * cols, cell * len(rows)), (0, 0, 0, 0))
    meta = {"tool": "hd2d portal", "biome": BIOME, "seed": 104, "image": f"{name}.png", "cell": cell,
            "size": [atlas.width, atlas.height], "cast_sets": {}, "cycle": [], "effects": {}}
    (out / "strips").mkdir(exist_ok=True)
    for row, (k, e, frames) in enumerate(rows):
        strip = Image.new("RGBA", (cell * len(frames), cell), (0, 0, 0, 0))
        fl = []
        for i, F in enumerate(frames):
            assert F.n == cell, (k, F.n, cell)
            im = F.image()
            atlas.paste(im, (i * cell, row * cell))
            strip.paste(im, (i * cell, 0))
            fl.append({"x": i * cell, "y": row * cell, "w": cell, "h": cell})
        strip.save(out / "strips" / f"{k}.png")
        light = e.get("light")
        if light:
            light = {**light, "color": ALLC.get(light["color"], light["color"])}
        meta["effects"][k] = {"row": row, "frames": len(frames), "fps": e["fps"], "loop": e.get("loop", True),
                              "loop_from": e.get("loop_from", 0), "loops": e.get("loops", 1), "kind": e["kind"],
                              "pivot": e.get("pivot", [cell // 2, cell - 1] if e["kind"] == "billboard" else [cell // 2, cell // 2]),
                              "lift": e.get("lift", 0.0), "glow": e.get("glow", True), "light": light,
                              "speed": None, "travel": None, "then": None,
                              "duration": 9999 if e.get("loop", True) else round(len(frames) / e["fps"], 3),
                              "strip": f"strips/{k}.png", "frame_list": fl}
        if e.get("notes"):
            meta["effects"][k]["notes"] = e["notes"]
    atlas.save(out / f"{name}.png")
    write_json(out / f"{name}.json", meta)
    # hard-alpha + colour audit (biome + NEON + kit cold only)
    a = np.array(atlas)
    assert set(np.unique(a[..., 3])) <= {0, 255}
    return meta


# ============================================================== icons (16 px, like build.py draw_icons)
class Icon:
    def __init__(self, w=16):
        self.w = w
        self.p = [[None] * w for _ in range(w)]

    def set(self, x, y, c):
        x, y = int(round(x)), int(round(y))
        if c and 0 <= x < self.w and 0 <= y < self.w:
            assert c in C, c          # icons: biome palette only (HUD rule)
            self.p[y][x] = c

    def get(self, x, y):
        return self.p[y][x] if 0 <= x < self.w and 0 <= y < self.w else None

    def outline(self):
        pts = [(x, y) for y in range(self.w) for x in range(self.w) if self.p[y][x] is None and any(
            0 <= x + dx < self.w and 0 <= y + dy < self.w and self.p[y + dy][x + dx] not in (None, "ink")
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        for x, y in pts:
            self.p[y][x] = "ink"

    def image(self):
        im = Image.new("RGBA", (self.w, self.w), (0, 0, 0, 0))
        for y in range(self.w):
            for x in range(self.w):
                if self.p[y][x]:
                    im.putpixel((x, y), rgba(self.p[y][x]))
        return im


def write_icons(out: Path, name: str, icons: list):
    """icons: [(id, Icon, meta)] -> <name>.png (16 px strip) + <name>_6x.png + <name>.json"""
    w = 16
    sheet = Image.new("RGBA", (w * len(icons), w), (0, 0, 0, 0))
    meta = {"tool": "hmart icons (build.py draw_icons format)", "biome": BIOME, "cell": w, "image": f"{name}.png",
            "size": [sheet.width, w], "icons": {}}
    for i, (k, ic, m) in enumerate(icons):
        sheet.alpha_composite(ic.image(), (i * w, 0))
        meta["icons"][k] = {"index": i, "x": i * w, "y": 0, "w": w, "h": w, **m}
    sheet.save(out / f"{name}.png")
    sheet.resize((sheet.width * 6, w * 6), Image.NEAREST).save(out / f"{name}_6x.png")
    write_json(out / f"{name}.json", meta)
    return sheet


# ============================================================== kit (.glb via the repo's kit.py)
_KIT = None


def kit_module():
    global _KIT
    if _KIT is None:
        _KIT = load_tool("kit")
    return _KIT


TEXEL_CACHE = Path("/workspace/hearthmoor-staging/art/_lib/_texel")


def kit_ctx():
    K = kit_module()
    if not (TEXEL_CACHE / "cobble_64.png").exists():
        load_tool("texel").build(BIOME, (32, 64), None, TEXEL_CACHE, None, 1)
    return K.Ctx(K.Pal(K.load_biome(BIOME)), TEXEL_CACHE, 1)


def build_kit(out: Path, pieces_fn, extra_meta=None):
    """pieces_fn(K) -> {name: fn(cx) -> Piece} (the kit_*.py convention). Writes <out>/<name>.glb + kit.json.
    Returns ({name: Piece}, meta)."""
    K = kit_module()
    ns = types.SimpleNamespace(**vars(K))
    cx = kit_ctx()
    out.mkdir(parents=True, exist_ok=True)
    meta = {"tool": "hd2d kit", "biome": BIOME, "seed": 1, "sprite_height_m": 1.8, "pieces": {}}
    built = {}
    for n, f in pieces_fn(ns).items():
        pc = f(cx)
        built[n] = pc
        meta["pieces"][pc.name] = K.export_piece(cx, pc, out)
        if extra_meta and pc.name in extra_meta:
            meta["pieces"][pc.name].update(extra_meta[pc.name])
    write_json(out / "kit.json", meta)
    return built, meta


# ============================================================== preview rasteriser (kit pieces -> pixels)
PX_PER_M = 18.0          # sprite texel density: a 1.8 m sprite is 32 px
ELEV = math.radians(36)  # locked 3/4 camera (decal squash angle)
UNLIT = {"glow", "lamp", "window"}


def render_mesh(mesh, mode="night", lights=(), px_per_m=PX_PER_M, pad=4, window_lit=True, ambient=None, depth=False):
    """flat-shaded orthographic 3/4 render of a meshlib Mesh at sprite density. Returns (RGBA image, origin_px)
    where origin_px is the screen position of world (0,0,0). Hard alpha; glow / lamp materials stay unlit."""
    p, c, _ = mesh.arrays()
    P = p.reshape(-1, 3, 3)
    Ccol = c.reshape(-1, 3, 3).mean(1)
    mats = mesh.mat
    ce, se = math.cos(ELEV), math.sin(ELEV)
    sx = P[..., 0] * px_per_m
    sy = (-P[..., 1] * ce + P[..., 2] * se) * px_per_m
    dep = (P[..., 2] * ce + P[..., 1] * se)
    x0, x1 = math.floor(sx.min()) - pad, math.ceil(sx.max()) + pad
    y0, y1 = math.floor(sy.min()) - pad, math.ceil(sy.max()) + pad
    W, H = x1 - x0, y1 - y0
    img = np.zeros((H, W, 4), float)
    zb = np.full((H, W), -1e9)
    nrm = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
    ln = np.linalg.norm(nrm, axis=1, keepdims=True); ln[ln == 0] = 1
    nrm = nrm / ln
    view = np.array([0, se, ce])
    flip = (nrm @ view) < 0
    nrm[flip] *= -1
    key = np.array([-0.55, 0.75, 0.45]); key /= np.linalg.norm(key)
    cent = P.mean(1)
    if mode == "day":
        amb = np.array(ambient or (0.62, 0.6, 0.58))
        shade = amb + 0.5 * np.clip(nrm @ key, 0, 1)[:, None] * np.array([1.0, 0.92, 0.78])
    else:
        amb = np.array(ambient or (0.20, 0.23, 0.40))
        shade = amb + 0.16 * np.clip(nrm @ key, 0, 1)[:, None] * np.array([0.6, 0.7, 1.0])
    shade = np.repeat(shade[:, None, :], 1, 1)[:, 0, :] if shade.ndim == 2 else shade
    lit = np.zeros_like(Ccol)
    for (lp, lc, rng_, inten) in lights:
        lc = np.array(hex2rgb(lc)) / 255.0
        d = cent - np.array(lp)
        dist = np.linalg.norm(d, axis=1)
        fall = np.clip(1 - dist / rng_, 0, 1) ** 2 * inten
        ndl = np.clip(-(nrm * (d / np.maximum(dist[:, None], 1e-6))).sum(1), 0, 1) * 0.7 + 0.3
        lit += (fall * ndl)[:, None] * lc[None, :]
    col = Ccol * (shade + lit)
    for t in range(len(mats)):
        if mats[t] in UNLIT and (mats[t] != "window" or window_lit):
            col[t] = Ccol[t] if mats[t] != "window" else np.array(hex2rgb("#ff9a38")) / 255
    col = np.clip(col, 0, 1)
    order = np.argsort(dep.mean(1))
    for t in order:
        xs, ys, zs = sx[t] - x0, sy[t] - y0, dep[t]
        bx0, bx1 = max(0, int(math.floor(xs.min()))), min(W - 1, int(math.ceil(xs.max())))
        by0, by1 = max(0, int(math.floor(ys.min()))), min(H - 1, int(math.ceil(ys.max())))
        if bx1 < bx0 or by1 < by0:
            continue
        gx, gy = np.meshgrid(np.arange(bx0, bx1 + 1) + 0.5, np.arange(by0, by1 + 1) + 0.5)
        (ax, bx_, cx_), (ay, by_, cy_) = xs, ys
        den = (by_ - cy_) * (ax - cx_) + (cx_ - bx_) * (ay - cy_)
        if abs(den) < 1e-9:
            continue
        w0 = ((by_ - cy_) * (gx - cx_) + (cx_ - bx_) * (gy - cy_)) / den
        w1 = ((cy_ - ay) * (gx - cx_) + (ax - cx_) * (gy - cy_)) / den
        w2 = 1 - w0 - w1
        m = (w0 >= -1e-4) & (w1 >= -1e-4) & (w2 >= -1e-4)
        if not m.any():
            continue
        z = w0 * zs[0] + w1 * zs[1] + w2 * zs[2]
        sub = zb[by0:by1 + 1, bx0:bx1 + 1]
        upd = m & (z >= sub - 1e-6)
        sub[upd] = z[upd]
        tgt = img[by0:by1 + 1, bx0:bx1 + 1]
        tgt[upd, :3] = col[t]
        tgt[upd, 3] = 1.0
    out = (np.clip(img, 0, 1) * 255).round().astype(np.uint8)
    out[..., 3] = np.where(img[..., 3] > 0, 255, 0)
    if depth:
        return Image.fromarray(out, "RGBA"), (-x0, -y0), zb
    return Image.fromarray(out, "RGBA"), (-x0, -y0)


def billboard_over(can, fr, anchor, org, zb, pivot=None, offset=(0, 0)):
    """paste a gamefx billboard frame whose pivot sits at world `anchor`, hidden where the rendered mesh (zb, in the
    render's own pixel space at `offset` inside can) is nearer the camera than the billboard (engine depth test)"""
    ce, se = math.cos(ELEV), math.sin(ELEV)
    bd = anchor[2] * ce + anchor[1] * se
    px_, py_ = project(anchor, org)
    pv = pivot or (fr.width // 2, fr.height - 1)
    X0, Y0 = int(round(px_ - pv[0])) + offset[0], int(round(py_ - pv[1])) + offset[1]
    src = fr.load()
    dst = can.load()
    for y in range(fr.height):
        for x in range(fr.width):
            if src[x, y][3] == 0:
                continue
            cx_, cy_ = X0 + x, Y0 + y
            if not (0 <= cx_ < can.width and 0 <= cy_ < can.height):
                continue
            zx, zy = cx_ - offset[0], cy_ - offset[1]
            if 0 <= zy < zb.shape[0] and 0 <= zx < zb.shape[1] and zb[zy, zx] > bd + 0.02:
                continue
            dst[cx_, cy_] = src[x, y]


def project(pt, origin, px_per_m=PX_PER_M):
    ce, se = math.cos(ELEV), math.sin(ELEV)
    x, y, z = pt
    return origin[0] + x * px_per_m, origin[1] + (-y * ce + z * se) * px_per_m


def pool_layer(size, center, rx_px, cols, seed="pl"):
    """dithered ground light pool (hard alpha) drawn on its own layer, squashed for the 3/4 camera"""
    W, H = size
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = im.load()
    R = rng(104, seed)
    cx, cy = center
    for y in range(max(0, int(cy - rx_px)), min(H, int(cy + rx_px) + 1)):
        for x in range(max(0, int(cx - rx_px)), min(W, int(cx + rx_px) + 1)):
            d = math.hypot(x - cx, (y - cy) / DECAL_SQUASH) / rx_px
            if d > 1:
                continue
            dens = (1 - d) ** 1.1 * 0.9 + 0.04
            if d < 0.18 or ((x + y) % 2 == 0 and R.random() < dens) or (d < 0.45 and R.random() < dens * 0.6):
                px[x, y] = rgba(cols[0] if d < 0.28 else cols[1] if d < 0.62 else cols[2])
    return im


# ============================================================== contact sheets
BG = (18, 20, 34, 255)
BG2 = (26, 28, 46, 255)
INK_T = (246, 236, 210, 255)
SUB_T = (170, 176, 210, 255)


def scale4(im, k=4):
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


class Sheet:
    """simple flowing contact sheet: sections of labelled cells, each an image already at 4x (or scaled here)"""

    def __init__(self, title, subtitle="", width=1400):
        self.title, self.subtitle, self.W = title, subtitle, width
        self.sections = []

    def section(self, name, note=""):
        self.sections.append({"name": name, "note": note, "cells": []})

    def cell(self, im, label="", sub="", k=4, bg=None):
        big = scale4(im, k) if k != 1 else im
        self.sections[-1]["cells"].append((big, label, sub, bg))

    def render(self, path):
        pad, gap = 16, 14
        x, y = pad, 70
        placed = []
        for s in self.sections:
            y += 34
            placed.append(("hdr", s, y - 30))
            x, rowh = pad, 0
            for (im, lab, sub, bg) in s["cells"]:
                cw, ch = im.width, im.height + (34 if (lab or sub) else 6)
                if x + cw > self.W - pad and x > pad:
                    x, y = pad, y + rowh + gap
                    rowh = 0
                placed.append(("cell", (im, lab, sub, bg), (x, y)))
                x += max(cw, 60) + gap
                rowh = max(rowh, ch)
            y += rowh + gap
        H = y + 30
        out = Image.new("RGBA", (self.W, H), BG)
        d = ImageDraw.Draw(out)
        d.text((pad, 14), self.title, fill=INK_T, font=FONT_T)
        d.text((pad, 42), self.subtitle, fill=SUB_T, font=FONT)
        for kind, a, b in placed:
            if kind == "hdr":
                d.rectangle([0, b - 2, self.W, b + 24], fill=(40, 34, 56, 255))
                d.text((pad, b + 3), a["name"], fill=(255, 210, 120, 255), font=FONT_B)
                if a["note"]:
                    d.text((pad + 12 + d.textlength(a["name"], font=FONT_B), b + 6), a["note"], fill=SUB_T, font=FONT_S)
            else:
                im, lab, sub, bg = a
                xx, yy = b
                if bg:
                    d.rectangle([xx - 2, yy - 2, xx + im.width + 1, yy + im.height + 1], fill=bg)
                out.alpha_composite(im, (xx, yy))
                if lab:
                    d.text((xx, yy + im.height + 3), lab, fill=INK_T, font=FONT_S)
                if sub:
                    d.text((xx, yy + im.height + 16), sub, fill=SUB_T, font=FONT_S)
        d.text((pad, H - 22), "Hearthmoor Art seat staging pack - native pixels shown at 4x nearest, hard alpha, "
               "palette / NEON glow pixels, dithered light pools, no blur, no bloom", fill=(120, 124, 160, 255), font=FONT_S)
        out.save(path)
        return out


def lit_sprite(im, pool=None, pool_r=None, pad=(10, 6), bg=None, foot=None):
    """compose a native sprite over a dithered light pool at its feet (native px). pool = (hi, mid, lo) names"""
    px_, py_ = pad
    W, H = im.width + 2 * px_, im.height + py_ * 2
    canvas = Image.new("RGBA", (W, H), bg or (0, 0, 0, 0))
    if pool:
        r = pool_r or im.width * 0.6
        fx, fy = (foot if foot else (W / 2, py_ + im.height - 1))
        canvas.alpha_composite(pool_layer((W, H), (fx, fy), r, pool, seed=str(pool) + str(r)))
    canvas.alpha_composite(im, (px_, py_))
    return canvas


def frame_of(png: Path, meta: dict, role: str, facing: str, anim: str, i: int):
    atlas = Image.open(png).convert("RGBA")
    fw, fh = meta["frame"]
    for fr in meta["roles"][role]["frames"]:
        if fr["facing"] == facing and fr["anim"] == anim and fr["i"] == i:
            return atlas.crop((fr["x"], fr["y"], fr["x"] + fw, fr["y"] + fh))
    raise KeyError((role, facing, anim, i))


def fx_frame(png: Path, meta: dict, fx: str, i: int):
    atlas = Image.open(png).convert("RGBA")
    e = meta["effects"][fx]
    f = e["frame_list"][i]
    return atlas.crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))


def report_line(rep):
    s = rep["summary"]
    return f"check-sprite: {'PASS' if s['pass'] else 'FAIL'} ({s['failures']} failures)" + (
        "" if s["pass"] else "\n  " + "\n  ".join(rep["failures"][:12]))


def file_table(folder: Path):
    """markdown list of the pack's files (relative path, size, PNG dims)"""
    rows = ["| file | size | px |", "|---|---|---|"]
    for p in sorted(folder.rglob("*")):
        if p.is_dir() or "__pycache__" in p.parts or p.name == "README.md":
            continue
        dims = ""
        if p.suffix == ".png":
            with Image.open(p) as im:
                dims = f"{im.width}x{im.height}"
        rows.append(f"| `{p.relative_to(folder)}` | {p.stat().st_size // 1024 + 1} KB | {dims} |")
    return "\n".join(rows)


def finish_pack(folder: Path, readme_body: str):
    """copy the shared lib into src/ (pack is self-contained) and write README.md with the generated file table"""
    import shutil
    src = folder / "src"
    src.mkdir(exist_ok=True)
    shutil.copy(Path(__file__), src / "hmart.py")
    (folder / "README.md").write_text(readme_body.rstrip() + "\n\n## Files\n\n" + file_table(folder) + "\n")


# ============================================================== shared glow orbs (Bill 2026-10-05: hovering neon orbs)
NEON5 = {   # name: (core, hi, mid, lo)
    "blue": ("white", "neon_blue_hi", "neon_blue", "neon_blue_lo"),
    "violet": ("white", "neon_violet_hi", "neon_violet", "neon_violet_lo"),
    "red": ("white", "neon_red_hi", "neon_red", "neon_red_lo"),
    "green": ("white", "neon_green_hi", "neon_green", "neon_green_lo"),
    "pink": ("white", "neon_pink_hi", "neon_pink", "neon_pink_lo"),
}


def glow_orb_frames(colour, cell=48, frames=8):
    """a hovering glow orb: a 9 px glowing sphere (white core, hi, mid, lo rim), slow bob, twinkling halo sparkles and a
    faint dotted trail beneath (same art as verdant_heart's glow_orb_*)"""
    core, hi, mid, lo = NEON5[colour]
    out = []
    for f in range(frames):
        F = Fx(cell)
        bob = [0, -1, -2, -2, -1, 0, 1, 1][f % 8]
        cx, cy = cell / 2 - 0.5, cell * 22 / 48 + bob
        F.disk(cx, cy, 4.6, [core, hi, hi, mid, mid, lo])
        F.set(cx - 1.5, cy - 1.5, "white"); F.set(cx - 2, cy - 1, "white")
        F.ring(cx, cy, 7, 7, lo, dots=3, start=f * 0.25)
        for k in range(4):
            a = f / 8 * math.tau + k * math.tau / 4
            rr = 9 + (k % 2) * 2
            if (f + k) % 2 == 0:
                F.star(cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.8, 1, core, hi, mid)
            else:
                F.set(cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.8, hi)
        for t in range(4):
            if (t + f) % 2 == 0:
                F.set(cx + math.sin(f * 0.8 + t) * 1.2, cy + 7 + t * 3, lo if t > 1 else mid)
        out.append(F)
    return out


def neon_pool_frames(colour, cell=48, frames=6, rmax=None):
    c = NEON5[colour]
    return pool_frames((c[1], c[2], c[3]), cell, frames, f"pool_{colour}", rmax=rmax)
