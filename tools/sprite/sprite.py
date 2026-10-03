"""hd2d sprite: cozy HD-2D actor writer (extends the Gravewake sprite writer).

20x32 native frames, 4 facings (down, up, left, right) x (idle 4 + walk 4), 1px ink outline,
big readable head, hard alpha, colours only from the biome palette. All roles are original.

    hd2d sprite --biome cozy-village --roles all --out PROJECT/public/art/sprite

Writes actors.png (atlas: per role 4 rows [down, up, left, right] x 12 cols [idle0-3, walk0-3, cast0-3 (casters only)]),
actors.json (frames, pivot = feet, anims), actors_preview_4x.png (nearest), and per-role strips.
Hero classes (roles_heroes.py: wildcaller, runeguard, seer, stormborn, grovekeeper, cinderknight) add four action
anims after the cast columns: cast 8-11 (spell), attack 12-15 (weapon), defend 16-19 (guard), jump 20-23 (crouch,
launch, airborne, land). Their strips are 24 columns wide; villagers keep 12 (the atlas is as wide as its widest role).
    hd2d sprite --roles heroes ...   selects just the six heroes.
Combat roles (roles_enemies.py: golem, wraith, skeleton + six summons) are extra: never part of "all"; name them
(or --roles combat). Enemies add a die anim at cols 24-27; summons carry idle / walk / attack.
Deterministic: same biome + seed -> same bytes.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE / "vendor"))
from PIL import Image, ImageDraw  # noqa: E402

from hd2d_common import Pal, ensure, load_biome, rng, write_json  # noqa: E402
import sprite_writer as gw  # noqa: E402  (vendored Gravewake writer: Sprite grid + outline pass)
sys.path.insert(0, str(HERE))
import roles_more as RM  # noqa: E402  (second batch of roles, cast pose, animals)
import roles_heroes as RH  # noqa: E402  (six Hearthmoor hero classes: cast / attack / defend / jump sets)
import roles_enemies as RE  # noqa: E402  (Hearthmoor combat: three enemies + six tiny hero summons)

FW, FH = 20, 32
PIVOT = (10, 32)  # bottom-centre of the frame = the feet on the ground
FACINGS = ("down", "up", "left", "right")
ANIMS = {"idle": {"start": 0, "count": 4, "fps": 3, "loop": [0, 1, 2, 1], "blink": 3},
         "walk": {"start": 4, "count": 4, "fps": 8},
         "cast": {"start": 8, "count": 4, "fps": 6, "loop": [0, 1, 2, 2, 3, 3], "casters_only": True},
         # hero action sets (roles_heroes.py); villagers never fill these columns
         "attack": {"start": 12, "count": 4, "fps": 10, "loop": [0, 1, 2, 2, 3], "heroes_only": True},
         "defend": {"start": 16, "count": 4, "fps": 6, "loop": [0, 1], "hold": [2, 3], "heroes_only": True},
         "jump": {"start": 20, "count": 4, "fps": 8, "phases": ["crouch", "launch", "airborne", "land"],
                  "heroes_only": True},
         # enemies only (roles_enemies.py): a 4-frame defeat that ends in a small heap / wisp on the ground
         "die": {"start": 24, "count": 4, "fps": 6, "once": True, "enemies_only": True}}
COLS = 12  # villager strips: idle 0-3 | walk 0-3 | cast 0-3 (casters); hero strips run to col 23 (role_cols)
GROUND_ROW = 31  # lowest opaque row (the outline under the soles)


class HSprite(gw.Sprite):
    """Gravewake's Sprite grid, re-pointed at a biome palette instead of Gravewake's locked list."""

    def __init__(self, pal: Pal, w=FW, h=FH):
        super().__init__(w, h)
        self.pal = pal
        self.allowed = set(pal.hexes())

    def _c(self, color):
        c = self.pal[color] if color else None
        if c and c not in self.allowed:
            raise ValueError(f"{color} -> {c} is not in biome {self.pal.b['biome']}")
        return c

    def set(self, x, y, color):
        c = self._c(color) if color else None
        if c and 0 <= x < self.w and 0 <= y < self.h:
            self.p[y][x] = c

    def empty(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h and self.p[y][x] is None:
            self.p[y][x] = self._c(color)

    def outline(self, ink="ink"):
        src = [row[:] for row in self.p]
        ink = self._c(ink)
        for y in range(self.h):
            for x in range(self.w):
                if src[y][x]:
                    continue
                if any(0 <= y + dy < self.h and 0 <= x + dx < self.w and src[y + dy][x + dx]
                       for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    self.p[y][x] = ink

    def mirror(self):
        for row in self.p:
            row.reverse()
        return self

    def hspan(self, y, x0, x1, color):
        for x in range(x0, x1 + 1):
            self.set(x, y, color)


# ------------------------------------------------------------------ layouts
ADULT = dict(head_top=5, head_w=12, head_h=11, torso_top=16, hip=24, torso_w=10, arm_len=6, leg_w=3)
KID = dict(head_top=10, head_w=12, head_h=10, torso_top=20, hip=26, torso_w=8, arm_len=4, leg_w=3)
BROAD = dict(ADULT, torso_w=12)  # bulkier brawler build (Stormborn, Cinderknight): same head, wider chest and arms
LAYOUTS = {"adult": ADULT, "kid": KID, "broad": BROAD}


def head_spans(w, h, x0):
    """Rounded head: row -> (x_start, x_end)."""
    out = []
    for r in range(h):
        ind = 2 if r in (0, h - 1) else 1 if r in (1, h - 2) else 0
        out.append((x0 + ind, x0 + w - 1 - ind))
    return out


# ------------------------------------------------------------------ roles (all original)
def _r(**kw):
    base = dict(kind="human", layout="adult", hair="timber", hairstyle="short", hat=None, hatc="plaster_hi",
                shirt="cloth", pants="timber_lo", shoes="shadow", skin="skin", apron=None, overalls=None,
                vest=None, skirt=None, cloak=None, scarf=None, satchel=None, item=None, beard=None,
                shawl=None, cane=False, hunch=0, stripes=None, boots=False, desc="",
                glasses=False, caster=False, animal=None)
    base.update(kw)
    return base


ROLES = {
    "baker": _r(desc="plump baker, puffy cream cap, apron, warm loaf", hat="toque", hatc="white", hair="timber",
                shirt="roof", apron="plaster_hi", item="loaf", pants="timber_lo"),
    "farmer": _r(desc="straw sun hat, blue overalls, straw in mouth", hat="straw", hatc="flower_gold", hair="timber_lo",
                 shirt="plaster", overalls="cloth", shoes="timber_lo", item="straw"),
    "fisher": _r(desc="oilskin rain hat, striped jumper, grey beard, tall boots, fish basket", hat="rainhat",
                 hatc="flower_gold", hair="stone_hi", beard="stone_hi", shirt="cloth", stripes="plaster_hi",
                 pants="timber_lo", boots=True, item="fishbasket"),
    "shopkeeper": _r(desc="flat cap, green vest, moustache, ledger", hat="flatcap", hatc="timber_lo", hair="timber",
                     shirt="plaster_hi", vest="moss", beard="timber_lo", item="ledger"),
    "kid": _r(desc="small kid, cowlick, red shirt, blue shorts", layout="kid", hair="flower_gold", hairstyle="cowlick",
              shirt="roof_hi", pants="cloth", shoes="timber"),
    "elder": _r(desc="white bun, rose shawl, long blue dress, cane", hair="plaster_hi", hairstyle="bun",
                shirt="cloth", skirt="cloth", shawl="flower_rose", cane=True, hunch=1),
    "traveler": _r(desc="generic wanderer: green cloak, rose scarf, satchel (player)", hair="timber",
                   hairstyle="messy", shirt="plaster", cloak="moss", scarf="flower_rose", satchel="timber_hi",
                   pants="timber_lo", shoes="timber_lo"),
    "florist": _r(desc="flower crown, auburn hair, blue dress, cream apron, flower basket", hair="roof",
                  hairstyle="long", hat="crown", shirt="flower_blue", skirt="flower_blue", apron="plaster_hi",
                  item="basket"),
    "postie": _r(desc="letter carrier: blue cap and jacket, satchel with letter", hat="flatcap", hatc="cloth",
                 hair="timber_lo", shirt="cloth", satchel="timber_hi", item="letter", pants="timber_lo"),
    "cat": _r(kind="creature", desc="orange tabby cat with white socks", fur="timber_hi", stripe="timber",
              belly="plaster_hi"),
}
ROLES.update(RM.more_roles(_r))
ROLES.update(RH.hero_roles(_r))
ROLES.update(RE.enemy_roles(_r))  # extra: only built when a spec names them (sprite_roles), never by "all"
EXTRA = {k for k, v in ROLES.items() if v.get("enemy") or v.get("summon")}

ROLE_SIZE = {"human": ((14, 24), (24, 40)), "creature": ((10, 24), (10, 40)),
             "enemy": ((6, 20), (6, 32)), "summon": ((4, 20), (6, 32))}  # (w range, h range)


# ------------------------------------------------------------------ pose tables
# walk: (bob, lift_left, lift_right, swing). swing +1 = right arm forward. bob -1 = body up 1px.
WALK_FRONT = [(0, 2, 0, 1), (-1, 0, 0, 0), (0, 0, 2, -1), (-1, 0, 0, 0)]
# side: (bob, stride, lift_back) stride +1 near leg forward
WALK_SIDE = [(0, 1, 0), (-1, 0, 1), (0, -1, 0), (-1, 0, 1)]
IDLE = [(0, 0), (0, 0), (1, 0), (0, 1)]  # (bob, blink)


def human_frame(pal: Pal, spec: dict, facing: str, anim: str, i: int) -> HSprite:
    s = HSprite(pal)
    face = "left" if facing == "right" else facing
    L = LAYOUTS[spec["layout"]]
    bob, blink, lift_l, lift_r, swing, stride, lift_b = 0, 0, 0, 0, 0, 0, 0
    if anim in RH.ACTS and spec.get("hero"):
        bob = RH.ACT_BOB[anim][i]
        spec = {**spec, "_act": (anim, i), "item": None}
    elif anim == "cast":
        bob = [0, -1, -1, 0][i]
        spec = {**spec, "_cast": i, "item": None}
    elif anim == "idle":
        bob, blink = IDLE[i]
        spec = {**spec, "_idle": i}
    elif face in ("down", "up"):
        bob, lift_l, lift_r, swing = WALK_FRONT[i]
    else:
        bob, stride, lift_b = WALK_SIDE[i]
    bob += spec["hunch"]
    if face == "up":  # from behind, the character's left is on screen left
        lift_l, lift_r = lift_r, lift_l
        swing = -swing
    draw_legs(s, spec, L, face, bob, lift_l, lift_r, stride, lift_b)
    if spec["cloak"] and face == "up":
        pass
    draw_body(s, spec, L, face, bob, swing, stride, anim, i)
    draw_head(s, spec, L, face, bob, blink)
    draw_extras(s, spec, L, face, bob, swing, stride)
    s.outline("ink")
    if facing == "right":
        s.mirror()
    return s


def draw_legs(s, spec, L, face, bob, lift_l, lift_r, stride, lift_b):
    hip = L["hip"] + bob
    pants, shoes = spec["pants"], spec["shoes"]
    skirt = spec["skirt"]
    sole = 30
    if face in ("down", "up"):
        for x0, lift in ((6, lift_l), (11, lift_r)):
            foot = sole - lift
            for y in range(hip, foot - 1):
                if skirt and y < 29 - lift:
                    continue
                s.hspan(y, x0, x0 + 2, pants)
                s.set(x0, y, pal_dk(s, pants))
            boot_top = foot - (3 if spec["boots"] else 1)
            for y in range(boot_top, foot + 1):
                s.hspan(y, x0, x0 + 2, shoes)
            s.set(x0 + 1, boot_top, s.pal.lt(shoes))
            if face == "down":
                s.set(x0 + (2 if x0 > 9 else 0), foot, pal_dk(s, shoes))
    else:
        # profile facing left. near leg = front when stride>0.
        if stride == 0:
            legs = [(8, 0), (9, lift_b)]
        else:
            legs = [(6, 0), (11, 0)] if stride > 0 else [(11, 0), (6, 0)]
            legs = [(6, 0), (11, 0)]
        for k, (x0, lift) in enumerate(legs):
            foot = sole - lift
            col = pants if k == 0 else pal_dk(s, pants)
            for y in range(hip, foot - 1):
                if skirt and y < 29 - lift:
                    continue
                # thighs angle in toward the hip
                xs = x0
                if stride != 0 and y < hip + 2:
                    xs = x0 + (1 if x0 < 9 else -1)
                s.hspan(y, xs, xs + 2, col)
            boot_top = foot - (3 if spec["boots"] else 1)
            for y in range(boot_top, foot + 1):
                s.hspan(y, x0, x0 + 2, shoes if k == 0 else pal_dk(s, shoes))
            s.set(x0 - 1, foot, shoes if k == 0 else pal_dk(s, shoes))  # toe points left
            s.set(x0 + 1, boot_top, s.pal.lt(shoes))


def pal_dk(s, c, n=1):
    return s.pal.dk(c, n)


def shade_box(s, x0, y0, x1, y1, c, light_left=True):
    """Filled block lit from the upper left: light column left, dark column right and bottom row."""
    for y in range(y0, y1 + 1):
        s.hspan(y, x0, x1, c)
    for y in range(y0, y1 + 1):
        s.set(x1, y, s.pal.dk(c))
    s.hspan(y1, x0, x1, s.pal.dk(c))
    if light_left:
        for y in range(y0, min(y1, y0 + (y1 - y0) // 2 + 1)):
            s.set(x0 + 1, y, s.pal.lt(c))


def draw_body(s, spec, L, face, bob, swing, stride, anim, i):
    top = L["torso_top"] + bob
    hip = L["hip"] + bob
    tw = L["torso_w"]
    x0 = 10 - tw // 2
    x1 = x0 + tw - 1
    shirt = spec["shirt"]
    if face == "left":
        x0, x1 = x0 + 1, x1 - 1
    bottom = hip - 1
    shade_box(s, x0, top, x1, bottom, shirt)
    s.hspan(top, x0 + 1, x1 - 1, s.pal.lt(shirt))  # shoulder light
    if spec["stripes"] and face != "up":
        for y in range(top + 2, bottom, 2):
            s.hspan(y, x0, x1 - 1, spec["stripes"])
    elif spec["stripes"]:
        for y in range(top + 2, bottom, 2):
            s.hspan(y, x0, x1 - 1, spec["stripes"])
    if spec["skirt"]:
        sk = spec["skirt"]
        for y in range(bottom - 1, 29):
            flare = 1 if y >= bottom + 2 else 0
            s.hspan(y, x0 - flare, x1 + flare, sk)
            s.set(x1 + flare, y, s.pal.dk(sk))
            s.set(x0 - flare, y, s.pal.lt(sk) if face != "up" else sk)
        s.hspan(28, x0 - 1, x1 + 1, s.pal.dk(sk))
        if face == "left":
            s.set(x0 + 2, 26, s.pal.dk(sk))
            s.set(x0 + 2, 27, s.pal.dk(sk))
    else:
        s.hspan(bottom, x0, x1, "timber_lo")  # belt
        if face == "down":
            s.set(9, bottom, "flower_gold")
    # vest / overalls / apron
    if spec["vest"]:
        v = spec["vest"]
        if face == "down":
            for y in range(top, bottom):
                s.hspan(y, x0, x0 + 2, v)
                s.hspan(y, x1 - 2, x1, v)
            for y in range(top, bottom):
                s.set(x1, y, s.pal.dk(v))
            s.set(x0 + 2, top + 3, "flower_gold")
            s.set(x1 - 2, top + 3, "flower_gold")
        elif face == "up":
            for y in range(top, bottom):
                s.hspan(y, x0, x1, v)
                s.set(x1, y, s.pal.dk(v))
        else:
            for y in range(top, bottom):
                s.hspan(y, x0 + 2, x1, v)
                s.set(x1, y, s.pal.dk(v))
    if spec["overalls"]:
        o = spec["overalls"]
        if face == "down":
            for y in range(top + 2, bottom + 1):
                s.hspan(y, x0 + 2, x1 - 2, o)
            s.set(x0 + 2, top, o); s.set(x0 + 2, top + 1, o)
            s.set(x1 - 2, top, o); s.set(x1 - 2, top + 1, o)
            s.set(x0 + 3, top + 2, "flower_gold"); s.set(x1 - 3, top + 2, "flower_gold")
        elif face == "up":
            s.set(x0 + 2, top, o); s.set(x0 + 2, top + 1, o); s.set(x1 - 2, top, o); s.set(x1 - 2, top + 1, o)
            for y in range(top + 2, top + 4):
                s.hspan(y, x0 + 2 + (y - top - 2), x1 - 2 - (y - top - 2), o)
            s.hspan(bottom, x0, x1, o)
        else:
            for y in range(top + 2, bottom + 1):
                s.hspan(y, x0 + 1, x1 - 1, o)
            s.set(x0 + 3, top, o); s.set(x0 + 3, top + 1, o)
        # overall legs
        for y in range(hip, 28):
            for x in range(20):
                if s.p[y][x] == s.pal[spec["pants"]] or s.p[y][x] == s.pal.dk(spec["pants"]):
                    s.p[y][x] = s.pal[o] if s.p[y][x] == s.pal[spec["pants"]] else s.pal.dk(o)
    if spec["apron"] and face != "up":
        a = spec["apron"]
        ay1 = 28 if spec["skirt"] else min(hip + 2, 28)
        if face == "down":
            for y in range(top + 2, ay1 + 1):
                s.hspan(y, x0 + 1, x1 - 1, a)
                s.set(x1 - 1, y, s.pal.dk(a))
            s.hspan(top + 2, x0 + 2, x1 - 2, s.pal.lt(a))
            s.hspan(ay1, x0 + 1, x1 - 1, s.pal.dk(a))
        else:
            for y in range(top + 2, ay1 + 1):
                s.hspan(y, x0 - 1, x0 + 1, a)
                s.set(x0 + 1, y, s.pal.dk(a))
    if spec["apron"] and face == "up":
        s.hspan(bottom - 1, x0, x1, spec["apron"])  # apron strings
        s.set(9, bottom, spec["apron"]); s.set(10, bottom, spec["apron"]); s.set(10, bottom + 1, spec["apron"])
    if spec["cloak"]:
        c = spec["cloak"]
        if face == "down":
            for y in range(top, min(28, hip + 2)):
                s.hspan(y, x0 - 2, x0, c)
                s.hspan(y, x1, x1 + 2, c)
                s.set(x1 + 2, y, s.pal.dk(c))
            s.hspan(top, x0 - 1, x1 + 1, c)
        elif face == "up":
            for y in range(top, min(29, hip + 3)):
                s.hspan(y, x0 - 2, x1 + 2, c)
                s.set(x1 + 2, y, s.pal.dk(c))
                s.set(x0 - 1, y, s.pal.lt(c))
            s.hspan(min(28, hip + 2), x0 - 2, x1 + 2, s.pal.dk(c))
            for y in range(top + 3, min(28, hip + 2), 3):
                s.set(10, y, s.pal.dk(c))
        else:
            sway = 1 if stride != 0 else 0
            for y in range(top, min(29, hip + 3)):
                k = (y - top) // 4
                s.hspan(y, x1 - 1, x1 + 1 + min(k, 2) + (sway if y > top + 5 else 0), c)
            for y in range(top, min(29, hip + 3)):
                xe = x1 + 1 + min((y - top) // 4, 2) + (sway if y > top + 5 else 0)
                s.set(xe, y, s.pal.dk(c))
    if spec["shawl"]:
        sh = spec["shawl"]
        for k, y in enumerate(range(top, top + 4)):
            if face == "up":
                s.hspan(y, x0 - 1 + k, x1 + 1 - k, sh)
            elif face == "down":
                s.hspan(y, x0 - 1, x1 + 1, sh) if k < 2 else (s.hspan(y, x0, x0 + 2 - k + 1, sh), s.hspan(y, x1 - 3 + k, x1, sh))
            else:
                s.hspan(y, x0, x1 + 1 - k, sh)
        s.set(9 if face != "left" else x0 + 1, top + 1, s.pal.lt(sh))
    draw_arms(s, spec, L, face, top, swing, stride, x0, x1)


def draw_arms(s, spec, L, face, top, swing, stride, x0, x1):
    sleeve = spec["shirt"]
    if spec.get("_act") is not None:
        return  # heroes draw their action pose after the head (roles_heroes.draw_act)
    if spec.get("_cast") is not None:
        return RM.draw_cast_arms(s, spec, L, face, top, x0, x1, spec["_cast"])
    if spec["cloak"] and face == "up":
        return
    n = L["arm_len"]
    if face in ("down", "up"):
        for side, ax in ((-1, x0 - 2), (1, x1 + 1)):
            sw = swing * (1 if side > 0 else -1)  # +1 forward
            ln = n + (1 if sw > 0 else -1 if sw < 0 else 0)
            col = sleeve
            if spec["cloak"] and face == "down":
                # arms under the cloak: only hands peek out
                hy = top + n + 1 + (1 if sw > 0 else 0)
                s.set(ax + (1 if side < 0 else 0), hy, spec["skin"])
                continue
            for y in range(top + 1, top + 1 + ln):
                s.hspan(y, ax, ax + 1, col)
                s.set(ax + (0 if side < 0 else 1), y, s.pal.dk(col) if side > 0 else col)
            s.set(ax + (1 if side < 0 else 0), top + 1, s.pal.lt(col))
            hy = top + 1 + ln
            s.hspan(hy, ax, ax + 1, spec["skin"])
            s.set(ax + (1 if side > 0 else 0), hy, s.pal.dk(spec["skin"]) if side > 0 else spec["skin"])
    else:
        # near arm in profile, over the torso
        ax = 9
        dx = -2 * stride
        col = sleeve
        if spec["cloak"]:
            col = spec["cloak"]
        for k, y in enumerate(range(top + 1, top + 1 + n)):
            ox = 0 if k < 2 else (dx // 2 if k < 4 else dx)
            s.hspan(y, ax + ox, ax + ox + 1, col)
            s.set(ax + ox + 1, y, s.pal.dk(col))
        s.hspan(top + 1 + n, ax + dx, ax + dx + 1, spec["skin"])


def draw_head(s, spec, L, face, bob, blink):
    w, h = L["head_w"], L["head_h"]
    top = L["head_top"] + bob
    hx = 10 - w // 2 - (1 if face == "left" else 0)
    spans = head_spans(w, h, hx)
    skin, hair = spec["skin"], spec["hair"]
    skin_lo = s.pal.dk(skin)
    hair_dk, hair_lt = s.pal.dk(hair), s.pal.lt(hair)
    bald = False
    for r, (a, b) in enumerate(spans):
        s.hspan(top + r, a, b, skin)
    # jaw shadow
    a, b = spans[-1]
    s.hspan(top + h - 1, a, b, skin_lo)
    if face == "down":
        for r in range(0, 4):
            a, b = spans[r]
            s.hspan(top + r, a, b, hair)
        # side locks
        for r in range(4, 4 + (5 if spec["hairstyle"] in ("long",) else 3)):
            if r >= h:
                break
            a, b = spans[r]
            s.set(a, top + r, hair); s.set(b, top + r, hair_dk)
        if spec["hairstyle"] == "long":
            for r in range(4, h + 2):
                a, b = spans[min(r, h - 1)]
                s.set(a - (1 if r > 6 else 0), top + r, hair)
                s.set(b + (1 if r > 6 else 0), top + r, hair_dk)
        # fringe
        a, b = spans[4]
        fr = rng(spec.get("desc", ""), "fringe")
        for x in range(a + 1, b):
            if (x + top) % 3 == 0 or (spec["hairstyle"] == "messy" and x % 2 == 0):
                s.set(x, top + 4, hair)
        s.hspan(top + 1, a + 2, a + 4, hair_lt)
        s.set(spans[0][0] + 1, top, hair_lt)
        # ears
        a, b = spans[6]
        s.set(a, top + 6, skin_lo)
        s.set(b, top + 6, skin_lo)
        # eyes: 2 px tall, 1 wide, big readable face
        ey = top + 6
        ex0, ex1 = hx + 3, hx + w - 4
        if blink:
            s.set(ex0, ey + 1, "ink"); s.set(ex1, ey + 1, "ink")
        else:
            for ex in (ex0, ex1):
                s.set(ex, ey, "ink"); s.set(ex, ey + 1, "ink")
        s.set(ex0 - 1, ey + 2, "flower_rose"); s.set(ex1 + 1, ey + 2, "flower_rose")
        if spec["beard"]:
            bd = spec["beard"]
            if spec["hat"] == "rainhat" or spec["hairstyle"] == "short" and spec["hat"] != "flatcap":
                for r in range(h - 3, h):
                    a, b = spans[r]
                    s.hspan(top + r, a + 1, b - 1, bd)
                s.hspan(top + h - 1, spans[-1][0], spans[-1][1], s.pal.dk(bd))
                s.set(9, top + h - 3, skin_lo); s.set(10, top + h - 3, skin_lo)
            else:  # moustache
                s.hspan(top + h - 3, hx + 4, hx + w - 5, bd)
        else:
            s.set(9 + (0 if (top % 2) else 1), top + h - 2, skin_lo)  # small mouth
    elif face == "up":
        for r, (a, b) in enumerate(spans):
            if r >= h - 2 and spec["hairstyle"] not in ("long",):
                s.hspan(top + r, a + 1, b - 1, skin_lo if r == h - 1 else hair_dk)
                s.set(a, top + r, hair); s.set(b, top + r, hair_dk)
                continue
            s.hspan(top + r, a, b, hair)
            s.set(b, top + r, hair_dk)
        s.hspan(top + 1, spans[1][0] + 2, spans[1][0] + 5, hair_lt)
        s.set(spans[2][0] + 1, top + 2, hair_lt)
        for r in range(3, h - 2, 2):
            s.set(10 + (r % 3) - 1, top + r, hair_dk)
        if spec["hairstyle"] == "long":
            for r in range(h - 2, h + 3):
                a, b = spans[min(r, h - 1)]
                s.hspan(top + r, a, b, hair)
                s.set(b, top + r, hair_dk)
    else:  # left profile
        a0, b0 = spans[0]
        for r, (a, b) in enumerate(spans):
            if r < 4:
                s.hspan(top + r, a, b, hair)
            else:
                back = a + (w // 2) - (1 if r > h - 3 else 0)
                s.hspan(top + r, back, b, hair if r < h - 2 or spec["hairstyle"] == "long" else hair_dk)
                s.set(b, top + r, hair_dk)
        s.hspan(top + 1, a0 + 1, a0 + 3, hair_lt)
        # fringe tip and sideburn
        s.set(spans[4][0] + 1, top + 4, hair)
        if spec["hairstyle"] == "long":
            for r in range(h - 2, h + 3):
                bb = spans[min(r, h - 1)][1]
                s.hspan(top + r, bb - 3, bb, hair)
                s.set(bb, top + r, hair_dk)
        # ear
        ex = spans[6][0] + w // 2
        s.set(ex, top + 6, skin); s.set(ex, top + 7, skin_lo)
        # eye, nose, mouth
        eyx = spans[6][0] + 2
        if blink:
            s.set(eyx, top + 7, "ink")
        else:
            s.set(eyx, top + 6, "ink"); s.set(eyx, top + 7, "ink")
        s.set(spans[7][0] - 1, top + 7, skin)  # nose pokes out of the silhouette
        s.set(eyx + 1, top + 8, "flower_rose")
        if spec["beard"]:
            bd = spec["beard"]
            if spec["hat"] == "rainhat":
                for r in range(h - 3, h):
                    a, b = spans[r]
                    s.hspan(top + r, a, a + 5, bd)
            else:
                s.hspan(top + h - 3, spans[-3][0], spans[-3][0] + 2, bd)
    draw_hair_extra(s, spec, L, face, top, spans)
    if spec.get("glasses"):
        RM.draw_glasses(s, spec, L, face, top, hx, w)
    draw_hat(s, spec, L, face, top, spans)


def draw_hair_extra(s, spec, L, face, top, spans):
    hair = spec["hair"]
    if spec["hairstyle"] == "bun":
        cx = 9 if face != "left" else 11
        for y, (a, b) in ((top - 3, (cx - 1, cx + 2)), (top - 2, (cx - 2, cx + 3)), (top - 1, (cx - 1, cx + 2))):
            s.hspan(y, a, b, hair)
        s.set(cx, top - 3, s.pal.lt(hair))
        s.set(cx + 3 if face != "left" else cx + 3, top - 2, s.pal.dk(hair))
    elif spec["hairstyle"] == "cowlick":
        cx = 11 if face != "left" else 12
        s.set(cx, top - 1, hair); s.set(cx + 1, top - 2, hair); s.set(cx - 1, top - 1, hair)
    elif spec["hairstyle"] == "messy":
        a, b = spans[0]
        s.set(a + 1, top - 1, hair); s.set(a + 4, top - 1, hair); s.set(b - 1, top - 1, s.pal.dk(hair))
    else:
        RH.draw_hair(s, spec, L, face, top, spans)


def draw_hat(s, spec, L, face, top, spans):
    hat, c = spec["hat"], spec["hatc"]
    if not hat:
        return
    a0, b0 = spans[2]
    lt, dk = s.pal.lt(c), s.pal.dk(c)
    if hat == "toque":
        # puffy baker cap: band + mushroom puff
        s.hspan(top + 2, a0 + 1, b0 - 1, s.pal.dk(c))
        s.hspan(top + 3, a0, b0, s.pal.dk(c, 1))
        for y, ind in ((top - 3, 3), (top - 2, 1), (top - 1, 0), (top, 0), (top + 1, 0)):
            s.hspan(y, a0 + ind, b0 - ind, c)
            s.set(b0 - ind, y, s.pal.dk(c))
        s.hspan(top - 2, a0 + 2, a0 + 4, lt if lt != c else c)
        s.set(a0 + 6, top - 1, s.pal.dk(c))
    elif hat == "straw":
        for y, ind in ((top - 2, 3), (top - 1, 2), (top, 2), (top + 1, 2)):
            s.hspan(y, a0 + ind, b0 - ind, c)
            s.set(b0 - ind, y, dk)
        s.hspan(top + 1, a0 + 2, b0 - 2, "roof")  # ribbon
        m = 2 if face == "left" else 3
        s.hspan(top + 2, a0 - m + 1, b0 + 2, c)
        s.hspan(top + 3, a0 - m, b0 + 3 - (1 if face == "left" else 0), dk)
        s.hspan(top - 2, a0 + 4, a0 + 6, lt)
        if face == "left":
            s.hspan(top + 3, a0 - m, a0 + 2, c)
    elif hat == "rainhat":
        for y, ind in ((top - 1, 2), (top, 1), (top + 1, 1), (top + 2, 0)):
            s.hspan(y, a0 + ind, b0 - ind, c)
            s.set(b0 - ind, y, dk)
        s.hspan(top + 3, a0 - 1, b0 + 1, dk)
        s.hspan(top - 1, a0 + 3, a0 + 5, lt)
        if face == "left":
            for y in range(top + 3, top + 7):
                s.hspan(y, b0 - 1, b0 + 1, c)
                s.set(b0 + 1, y, dk)
        elif face == "up":
            for y in range(top + 3, top + 6):
                s.hspan(y, a0, b0, c)
                s.hspan(y, a0, a0, dk)
            s.hspan(top + 6, a0, b0, dk)
    elif hat == "flatcap":
        for y, ind in ((top - 1, 2), (top, 1), (top + 1, 0), (top + 2, 0)):
            s.hspan(y, a0 + ind, b0 - ind, c)
            s.set(b0 - ind, y, dk)
        s.hspan(top, a0 + 2, a0 + 4, lt)
        if face == "down":
            s.hspan(top + 3, a0 + 1, b0 - 1, dk)  # bill
        elif face == "left":
            s.hspan(top + 3, a0 - 2, a0 + 3, dk)
            s.hspan(top + 2, a0 - 1, a0, c)
        else:
            s.hspan(top + 3, a0 + 1, b0 - 1, c)
    elif hat == "crown":
        cols = ["flower_rose", "flower_gold", "flower_blue", "white"]
        y = top + 1
        for k, x in enumerate(range(a0, b0 + 1)):
            if face == "left" and x > b0 - 2:
                continue
            if k % 2 == 0:
                s.set(x, y, cols[(k // 2) % 3])
                s.set(x, y - 1, "leaf_deep" if k % 4 == 0 else cols[(k // 2 + 1) % 3])
            else:
                s.set(x, y, "grass")
    else:
        RM.draw_hat(s, spec, L, face, top, spans)
        RH.draw_hat(s, spec, L, face, top, spans)


def draw_extras(s, spec, L, face, bob, swing, stride):
    top = L["torso_top"] + bob
    item = spec["item"]
    tw = L["torso_w"]
    x0 = 10 - tw // 2
    x1 = x0 + tw - 1
    if spec["scarf"]:
        sc = spec["scarf"]
        if face == "down":
            s.hspan(top, x0, x1, sc); s.hspan(top + 1, x0 + 1, x1 - 1, s.pal.dk(sc))
            s.set(x1 - 2, top + 2, sc); s.set(x1 - 2, top + 3, s.pal.dk(sc))
        elif face == "up":
            s.hspan(top, x0, x1, sc)
            s.set(x0 + 2, top + 1, sc); s.set(x0 + 2, top + 2, s.pal.dk(sc))
        else:
            s.hspan(top, x0 + 1, x1, sc); s.hspan(top + 1, x0 + 2, x1 - 1, s.pal.dk(sc))
            tail = 1 if stride != 0 else 0
            s.set(x1 + 1, top + 1, sc); s.set(x1 + 2, top + 1 + tail, sc); s.set(x1 + 2, top + 2 + tail, s.pal.dk(sc))
    if spec["satchel"]:
        sa = spec["satchel"]
        if face == "down":
            for k in range(6):
                s.set(x1 - 1 - k, top + k, s.pal.dk(sa))
            s.hspan(top + 6, x0 - 1, x0 + 2, sa); s.hspan(top + 7, x0 - 1, x0 + 2, s.pal.dk(sa))
            if item == "letter":
                s.set(x0, top + 5, "white"); s.set(x0 + 1, top + 5, "white")
        elif face == "up":
            for k in range(6):
                s.set(x0 + 1 + k, top + k, s.pal.dk(sa))
            s.hspan(top + 6, x1 - 2, x1 + 1, sa); s.hspan(top + 7, x1 - 2, x1 + 1, s.pal.dk(sa))
        else:
            s.hspan(top + 6, x1 - 2, x1 + 1, sa); s.hspan(top + 7, x1 - 2, x1 + 1, s.pal.dk(sa))
            s.set(x1 - 1, top, s.pal.dk(sa))
            if item == "letter":
                s.set(x1 - 1, top + 5, "white"); s.set(x1, top + 5, "white")
    hand_y = top + 1 + L["arm_len"]
    if face == "down":
        hx = x0 - 2  # character's right hand on screen left
        if item == "loaf":
            s.hspan(hand_y - 1, hx - 1, hx + 2, "timber_hi"); s.hspan(hand_y, hx - 1, hx + 2, "timber")
            s.set(hx, hand_y - 1, "flower_gold"); s.set(hx + 2, hand_y - 1, "flower_gold")
        elif item == "basket":
            s.hspan(hand_y + 1, hx - 1, hx + 2, "timber"); s.hspan(hand_y + 2, hx - 1, hx + 2, "timber_lo")
            s.set(hx - 1, hand_y, "flower_rose"); s.set(hx, hand_y, "flower_gold"); s.set(hx + 1, hand_y, "flower_rose")
            s.set(hx + 2, hand_y, "grass")
        elif item == "fishbasket":
            s.hspan(hand_y + 1, x1, x1 + 3, "timber"); s.hspan(hand_y + 2, x1, x1 + 3, "timber_lo")
            s.set(x1 + 1, hand_y, "sky"); s.set(x1 + 2, hand_y, "stone_hi")
        elif item == "ledger":
            s.hspan(top + 3, x0 + 1, x0 + 3, "roof"); s.hspan(top + 4, x0 + 1, x0 + 3, "roof_lo")
            s.set(x0 + 3, top + 3, "plaster_hi")
        elif item == "straw":
            hy = L["head_top"] + bob + L["head_h"] - 2
            s.set(11, hy, "flower_gold"); s.set(12, hy, "flower_gold"); s.set(13, hy - 1, "flower_gold")
    elif face == "left":
        hx = 9 - 2 * stride
        if item == "loaf":
            s.hspan(hand_y, hx - 2, hx + 1, "timber_hi"); s.set(hx - 1, hand_y, "flower_gold")
        elif item == "basket":
            s.hspan(hand_y + 1, hx - 1, hx + 2, "timber"); s.set(hx, hand_y, "flower_rose"); s.set(hx + 1, hand_y, "flower_gold")
        elif item == "fishbasket":
            s.hspan(hand_y + 1, hx - 1, hx + 2, "timber"); s.set(hx, hand_y, "sky")
        elif item == "straw":
            hy = L["head_top"] + bob + L["head_h"] - 2
            s.set(3, hy, "flower_gold"); s.set(2, hy - 1, "flower_gold")
    if spec["cane"]:
        if face == "down":
            cx = x1 + 2
            for y in range(hand_y, 31):
                s.set(cx, y, "timber")
            s.set(cx - 1, hand_y, "timber_hi")
        elif face == "left":
            cx = 5
            for y in range(hand_y, 31):
                s.set(cx, y, "timber")
            s.set(cx + 1, hand_y, "timber_hi")
        elif face == "up":
            cx = x0 - 3
            for y in range(hand_y, 31):
                s.set(cx, y, "timber")
    RM.draw_items(s, spec, L, face, top, hand_y, x0, x1, stride)
    RH.draw_extras(s, spec, L, face, bob, swing, stride, spec.get("_act"))


# ------------------------------------------------------------------ cat (creature)
def cat_frame(pal: Pal, spec: dict, facing: str, anim: str, i: int) -> HSprite:
    s = HSprite(pal)
    face = "left" if facing == "right" else facing
    fur, st, belly = spec["fur"], spec["stripe"], spec["belly"]
    fdk = pal.dk(fur)
    walk = anim == "walk"
    bob = (-1 if i % 2 == 1 else 0) if walk else (1 if i == 2 else 0)
    blink = anim == "idle" and i == 3
    tail_phase = i % 4
    if face == "down":
        # body behind the head
        for y in range(24 + bob, 30):
            s.hspan(y, 6, 13, fur)
            s.set(13, y, fdk)
        # paws
        lifts = [(2, 0), (0, 0), (0, 2), (0, 0)][i] if walk else (0, 0)
        for x0, l in ((7, lifts[0]), (11, lifts[1])):
            s.hspan(30 - l, x0, x0 + 1, belly)
            s.hspan(29 - l, x0, x0 + 1, belly)
        s.hspan(27 + bob, 8, 11, belly)
        # head
        ht = 19 + bob
        for y, (a, b) in zip(range(ht, ht + 7), [(6, 13), (5, 14), (5, 14), (5, 14), (5, 14), (6, 13), (7, 12)]):
            s.hspan(y, a, b, fur)
            s.set(b, y, fdk)
        s.set(5, ht - 1, fur); s.set(6, ht - 1, fur); s.set(5, ht - 2, fur)
        s.set(14, ht - 1, fdk); s.set(13, ht - 1, fur); s.set(14, ht - 2, fdk)
        s.set(6, ht - 1, "flower_rose"); s.set(13, ht - 1, "flower_rose")
        for x in (8, 10, 11):
            s.set(x, ht, st)
        s.set(9, ht + 1, st)
        if blink:
            s.set(7, ht + 3, "ink"); s.set(8, ht + 3, "ink"); s.set(11, ht + 3, "ink"); s.set(12, ht + 3, "ink")
        else:
            s.set(7, ht + 2, "ink"); s.set(7, ht + 3, "ink"); s.set(12, ht + 2, "ink"); s.set(12, ht + 3, "ink")
            s.set(8, ht + 2, "flower_gold"); s.set(11, ht + 2, "flower_gold")
        s.hspan(ht + 4, 9, 10, "flower_rose")
        s.hspan(ht + 5, 8, 11, belly)
        s.hspan(ht + 6, 8, 11, belly)
        # tail curling round the right
        tx = 14 + (1 if tail_phase in (1, 2) else 0)
        for y in range(23 + bob, 29):
            s.set(tx, y, fur)
        s.set(tx, 22 + bob, st); s.set(tx - 1, 22 + bob - (1 if tail_phase == 2 else 0), fur)
        for y in range(25 + bob, 29, 2):
            s.set(6, y, st); s.set(12, y, st)
    elif face == "up":
        for y, (a, b) in zip(range(22 + bob, 31), [(6, 13), (5, 14), (5, 14), (5, 14), (5, 14), (5, 14), (5, 14), (6, 13), (6, 13)]):
            s.hspan(y, a, b, fur)
            s.set(b, y, fdk)
        for y in range(23 + bob, 30, 2):
            s.hspan(y, 7, 12, st)
        lifts = [(2, 0), (0, 0), (0, 2), (0, 0)][i] if walk else (0, 0)
        s.hspan(30 - lifts[0], 6, 7, fdk); s.hspan(30 - lifts[1], 12, 13, fdk)
        ht = 18 + bob
        for y, (a, b) in zip(range(ht, ht + 5), [(6, 13), (5, 14), (5, 14), (5, 14), (6, 13)]):
            s.hspan(y, a, b, fur)
            s.set(b, y, fdk)
        s.set(5, ht - 1, fur); s.set(5, ht - 2, fur); s.set(6, ht - 1, fur)
        s.set(14, ht - 1, fdk); s.set(14, ht - 2, fdk); s.set(13, ht - 1, fur)
        for x in (8, 10):
            s.set(x, ht + 1, st)
        # tail up, swishing
        tx = 10 + [0, 1, 2, 1][tail_phase]
        for y in range(14 + bob, 23 + bob):
            s.set(tx if y > 17 + bob else tx + 1, y, fur)
        s.set(tx + 1, 13 + bob, st); s.set(tx + 2, 14 + bob, fur)
    else:
        # side, facing left
        for y, (a, b) in zip(range(23 + bob, 29 + bob), [(8, 15), (7, 16), (7, 16), (7, 16), (7, 16), (8, 15)]):
            s.hspan(y, a, b, fur)
            s.set(b, y, fdk)
        for x in (10, 12, 14):
            s.set(x, 23 + bob, st); s.set(x, 24 + bob, st)
        s.hspan(28 + bob, 8, 14, belly)
        # legs
        if walk:
            pos = [[(7, 0), (10, 1), (13, 1), (15, 0)], [(8, 0), (9, 0), (13, 0), (14, 0)],
                   [(7, 1), (10, 0), (13, 0), (15, 1)], [(8, 0), (9, 0), (13, 0), (14, 0)]][i]
        else:
            pos = [(8, 0), (10, 0), (13, 0), (15, 0)]
        for k, (x, l) in enumerate(pos):
            for y in range(29 + bob, 31 - l):
                s.set(x, y, belly if y == 30 - l else (fur if k % 2 == 0 else fdk))
        # head
        ht = 19 + bob
        for y, (a, b) in zip(range(ht, ht + 6), [(3, 8), (2, 9), (2, 9), (2, 9), (3, 9), (4, 8)]):
            s.hspan(y, a, b, fur)
        s.set(9, ht + 1, fdk); s.set(9, ht + 2, fdk)
        s.set(3, ht - 1, fur); s.set(3, ht - 2, fur); s.set(4, ht - 1, fur)
        s.set(7, ht - 1, fur); s.set(7, ht - 2, fdk); s.set(8, ht - 1, fdk)
        s.set(4, ht - 1, "flower_rose")
        s.set(5, ht, st); s.set(6, ht, st)
        if blink:
            s.set(3, ht + 3, "ink"); s.set(4, ht + 3, "ink")
        else:
            s.set(4, ht + 2, "ink"); s.set(4, ht + 3, "ink"); s.set(3, ht + 2, "flower_gold")
        s.set(1, ht + 3, fur)  # muzzle
        s.set(1, ht + 4, "flower_rose")
        s.hspan(ht + 5, 3, 6, belly)
        # tail
        sw = [0, 1, 1, 0][tail_phase]
        for y in range(16 + bob, 24 + bob):
            s.set(16 + (1 if y < 20 + bob else 0) + (sw if y < 18 + bob else 0), y, fur)
        s.set(17 + sw, 15 + bob, st)
        s.set(16 + sw, 15 + bob, fur)
    s.outline("ink")
    if facing == "right":
        s.mirror()
    return s


def frame(pal, role, facing, anim, i):
    spec = ROLES[role]
    if spec.get("draw"):
        s = HSprite(pal)
        face = "left" if facing == "right" else facing
        RE.DRAW[spec["draw"]](s, face, anim, i)
        for y in range(FH):  # keep a 1 px margin so the ink outline always closes inside the frame
            for x in range(FW):
                if x in (0, FW - 1) or y in (0, FH - 1):
                    s.p[y][x] = None
        s.outline("ink")
        return s.mirror() if facing == "right" else s
    if spec["kind"] == "creature":
        if spec.get("animal"):
            s = HSprite(pal)
            face = "left" if facing == "right" else facing
            RM.ANIMAL[spec["animal"]](s, spec, face, anim == "walk", i, anim == "idle" and i == 3)
            s.outline("ink")
            return s.mirror() if facing == "right" else s
        return cat_frame(pal, spec, facing, anim, i)
    return human_frame(pal, spec, facing, anim, i)


def role_anims(role):
    if ROLES[role].get("anims"):
        return tuple(ROLES[role]["anims"])
    if ROLES[role].get("hero"):
        return ("idle", "walk") + RH.ACTS
    return ("idle", "walk", "cast") if ROLES[role].get("caster") else ("idle", "walk")


def role_cols(role):
    return max(COLS, max(ANIMS[a]["start"] + ANIMS[a]["count"] for a in role_anims(role)))


def role_sheet(pal, role) -> Image.Image:
    im = Image.new("RGBA", (FW * role_cols(role), FH * 4), (0, 0, 0, 0))
    for fi, facing in enumerate(FACINGS):
        for anim in role_anims(role):
            for i in range(4):
                col = ANIMS[anim]["start"] + i
                im.paste(frame(pal, role, facing, anim, i).image(), (col * FW, fi * FH))
    return im


def build(biome="cozy-village", roles=None, out="public/art/sprite", project=None, seed=1, name="actors"):
    pal = Pal(load_biome(biome, project))
    roles = roles or [r for r in ROLES if r not in EXTRA]
    out = ensure(out)
    cols = max(role_cols(r) for r in roles)
    atlas = Image.new("RGBA", (FW * cols, FH * 4 * len(roles)), (0, 0, 0, 0))
    meta = {"tool": "hd2d sprite", "biome": biome, "seed": seed, "frame": [FW, FH], "pivot": list(PIVOT),
            "ground_row": GROUND_ROW, "facings": list(FACINGS), "anims": ANIMS, "cols": cols,
            "image": f"{name}.png", "size": [atlas.width, atlas.height], "roles": {}}
    for ri, role in enumerate(roles):
        sheet = role_sheet(pal, role)
        atlas.paste(sheet, (0, ri * FH * 4))
        sheet.save(out / f"{role}.png")
        frames = []
        for fi, facing in enumerate(FACINGS):
            for anim in role_anims(role):
                for i in range(4):
                    col = ANIMS[anim]["start"] + i
                    frames.append({"name": f"{role}_{facing}_{anim}{i}", "facing": facing, "anim": anim, "i": i,
                                   "x": col * FW, "y": (ri * 4 + fi) * FH, "w": FW, "h": FH,
                                   "pivot": [col * FW + PIVOT[0], (ri * 4 + fi) * FH + PIVOT[1]]})
        spec = ROLES[role]
        meta["roles"][role] = {"row": ri * 4, "kind": spec["kind"], "desc": spec["desc"],
                               "size_bounds": ROLE_SIZE[spec["kind"]], "caster": bool(spec.get("caster")),
                               "anims": list(role_anims(role)), "frames": frames}
        if spec.get("hero"):
            meta["roles"][role].update(hero=True, cls=spec["cls"], origin=spec["origin"], style=spec["style"])
        if spec.get("enemy") or spec.get("summon"):
            meta["roles"][role]["enemy" if spec.get("enemy") else "summon"] = True
    atlas.save(out / f"{name}.png")
    write_json(out / f"{name}.json", meta)
    preview(atlas, roles, out / f"{name}_preview_4x.png")
    return {"atlas": str(out / f"{name}.png"), "json": str(out / f"{name}.json"),
            "preview": str(out / f"{name}_preview_4x.png"), "roles": roles}


def preview(atlas, roles, path, scale=4):
    """Nearest 4x contact sheet with a parchment backdrop and role labels."""
    big = atlas.resize((atlas.width * scale, atlas.height * scale), Image.NEAREST)
    pad = 90
    out = Image.new("RGBA", (big.width + pad, big.height), (236, 222, 190, 255))
    d = ImageDraw.Draw(out)
    for ri, role in enumerate(roles):
        y = ri * FH * 4 * scale
        if ri % 2:
            d.rectangle([0, y, out.width, y + FH * 4 * scale - 1], fill=(226, 208, 172, 255))
        d.text((6, y + 8), role, fill=(60, 40, 30, 255))
        for fi, f in enumerate(FACINGS):
            d.text((6, y + fi * FH * scale + FH * scale // 2), f, fill=(110, 80, 60, 255))
    d.text((pad + 4, 2), "idle 0-3 | walk 0-3 | cast 0-3 (magic users)", fill=(60, 40, 30, 255))
    out.alpha_composite(big, (pad, 0))
    out.save(path)


LINEUP_CELLS = [("down", "idle", 0, "idle down"), ("up", "idle", 0, "idle up"), ("left", "idle", 0, "idle left"),
                ("right", "idle", 0, "idle right"), ("left", "walk", 0, "walk"), ("down", "cast", 2, "cast")]


def lineup(pal, roles, path, scale=4):
    """Labelled nearest-neighbour lineup: one column per role, rows = idle down/up/left/right, a walk frame and
    an action frame. The action row sits on a dusk panel so the emissive glow pixels read (no bloom, no blur)."""
    from PIL import ImageFont
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 15)
        small = ImageFont.truetype("DejaVuSans.ttf", 11)
    except OSError:
        font = small = ImageFont.load_default()
    cw, ch = FW * scale, FH * scale
    gx, gy, lw, top = 44, 10, 76, 66
    W = lw + len(roles) * (cw + gx) + gx
    H = top + len(LINEUP_CELLS) * (ch + gy) + 40
    out = Image.new("RGBA", (W, H), (236, 222, 190, 255))
    d = ImageDraw.Draw(out)
    for ri, role in enumerate(roles):
        x = lw + gx + ri * (cw + gx)
        if ri % 2:
            d.rectangle([x - gx // 2, 0, x + cw + gx // 2 - 1, H], fill=(226, 208, 172, 255))
    ya = top + (len(LINEUP_CELLS) - 1) * (ch + gy)
    d.rectangle([lw + gx // 2, ya - gy // 2, W - gx // 2, ya + ch + gy // 2], fill=(44, 36, 52, 255))
    for ri, role in enumerate(roles):
        spec = ROLES[role]
        x = lw + gx + ri * (cw + gx)
        title = spec.get("cls", role)
        d.text((x + cw // 2, 8), title, fill=(60, 40, 30, 255), font=font, anchor="mt")
        if spec.get("hero"):
            d.text((x + cw // 2, 28), spec.get("origin_name", ""), fill=(110, 80, 60, 255), font=small, anchor="mt")
            d.text((x + cw // 2, 43), f"{spec['origin']} · {spec.get('style', '')}", fill=(140, 100, 70, 255), font=small, anchor="mt")
        else:
            d.text((x + cw // 2, 28), spec["kind"], fill=(110, 80, 60, 255), font=small, anchor="mt")
        for ci, (facing, anim, i, label) in enumerate(LINEUP_CELLS):
            y = top + ci * (ch + gy)
            if anim == "cast" and anim not in role_anims(role):
                continue
            im = frame(pal, role, facing, anim, i).image().resize((cw, ch), Image.NEAREST)
            out.alpha_composite(im, (x, y))
    for ci, (facing, anim, i, label) in enumerate(LINEUP_CELLS):
        y = top + ci * (ch + gy)
        lab = label.replace(" ", "\n")
        d.multiline_text((8, y + ch // 2 - 16), lab, fill=(90, 62, 44, 255), font=small, spacing=2)
    d.text((8, H - 26), "hd2d sprite: Hearthmoor hero classes, 20x32 native, shown at %dx nearest (no filtering, no bloom)" % scale,
           fill=(110, 80, 60, 255), font=small)
    out.save(path)
    return path


ANIM_ROWS = ("cast", "attack", "defend", "jump")
JUMP_LIFT = (0, 5, 9, 0)  # sheet-only preview of the runtime jump arc (native px); frames themselves stay feet-anchored


def anim_lineup(pal, roles, path, facing="down", scale=4):
    """Hero action sheet: rows = cast / attack / defend / jump, one column group per hero with all 4 frames of that
    anim in `facing`. Everything sits on a dark dusk panel so the crisp glow pixels read (no bloom, no blur)."""
    from PIL import ImageFont
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 15)
        small = ImageFont.truetype("DejaVuSans.ttf", 11)
    except OSError:
        font = small = ImageFont.load_default()
    roles = [r for r in roles if ROLES[r].get("hero")]
    cw, ch = FW * scale, FH * scale
    fg, gx, gy, lw, top = 4, 28, 14, 78, 70
    gw = 4 * cw + 3 * fg
    W = lw + len(roles) * (gw + gx) + gx
    jh = max(JUMP_LIFT) * scale  # extra headroom above the jump row for the preview arc
    rowy = [top + ai * (ch + gy + 14) + (jh if anim == "jump" else 0) for ai, anim in enumerate(ANIM_ROWS)]
    H = rowy[-1] + ch + gy + 14 + 36
    out = Image.new("RGBA", (W, H), (30, 25, 38, 255))
    d = ImageDraw.Draw(out)
    for ri, role in enumerate(roles):
        x = lw + gx + ri * (gw + gx)
        if ri % 2:
            d.rectangle([x - gx // 2, top - 8, x + gw + gx // 2 - 1, H - 30], fill=(40, 33, 50, 255))
        spec = ROLES[role]
        d.text((x + gw // 2, 10), spec.get("cls", role), fill=(246, 222, 170, 255), font=font, anchor="mt")
        d.text((x + gw // 2, 32), f"{spec.get('origin_name', '')} · {spec.get('style', '')}", fill=(200, 176, 150, 255),
               font=small, anchor="mt")
        for ai, anim in enumerate(ANIM_ROWS):
            y = rowy[ai]
            for i in range(ANIMS[anim]["count"]):
                im = frame(pal, role, facing, anim, i).image().resize((cw, ch), Image.NEAREST)
                lift = JUMP_LIFT[i] * scale if anim == "jump" else 0
                if anim == "jump":  # the shadow stays on the ground, shrinking as the hero rises
                    sx, sw = x + i * (cw + fg) + cw // 2, (7 - JUMP_LIFT[i] // 3) * scale
                    d.ellipse([sx - sw, y + ch - 2 * scale, sx + sw, y + ch + scale], fill=(18, 14, 22, 255))
                out.alpha_composite(im, (x + i * (cw + fg), y - lift))
                d.text((x + i * (cw + fg) + cw // 2, y + ch + 2), str(i), fill=(150, 130, 120, 255), font=small, anchor="mt")
    for ai, anim in enumerate(ANIM_ROWS):
        y = rowy[ai]
        sub = {"jump": "crouch\nlaunch\nair\nland", "defend": "raise\nset\nhold a\nhold b"}.get(anim, "")
        d.text((10, y + ch // 2 - 30), anim, fill=(246, 222, 170, 255), font=font)
        d.multiline_text((10, y + ch // 2 - 10), sub, fill=(170, 150, 135, 255), font=small, spacing=1)
    d.text((10, H - 24), f"hd2d sprite: hero action anims, facing {facing}, 20x32 native at {scale}x nearest "
           "(hard alpha, 1px ink outline, crisp glow pixels, no bloom)", fill=(170, 150, 135, 255), font=small)
    out.save(path)
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(prog="hd2d sprite", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--biome", default="cozy-village")
    ap.add_argument("--roles", default="all", help="comma list or 'all': " + ", ".join(ROLES))
    ap.add_argument("--out", default="public/art/sprite")
    ap.add_argument("--project", default=None, help="project root (uses its built palette if present)")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--name", default="actors")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--lineup", default=None, help="also write a labelled 4x lineup PNG of the chosen roles here")
    ap.add_argument("--anim-lineup", default=None,
                    help="also write a 4x hero action sheet (rows cast/attack/defend/jump, dark panel) here")
    ap.add_argument("--anim-facing", default="down", choices=FACINGS, help="facing for --anim-lineup (default down)")
    a = ap.parse_args(argv)
    if a.list:
        for k, v in ROLES.items():
            print(f"{k:12s} {v['kind']:8s} {v['desc']}")
        return 0
    roles = ([r for r in ROLES if r not in EXTRA] if a.roles == "all" else list(RH.HERO_ORDER) if a.roles == "heroes"
             else sorted(EXTRA, key=list(ROLES).index) if a.roles == "combat"
             else [r.strip() for r in a.roles.split(",")])
    for r in roles:
        if r not in ROLES:
            raise SystemExit(f"unknown role {r}")
    res = build(a.biome, roles, a.out, a.project, a.seed, a.name)
    print(f"sprite: {len(roles)} roles -> {res['atlas']}\n        {res['json']}\n        {res['preview']}")
    if a.lineup:
        print("        " + str(lineup(Pal(load_biome(a.biome, a.project)), roles, a.lineup)))
    if a.anim_lineup:
        print("        " + str(anim_lineup(Pal(load_biome(a.biome, a.project)), roles, a.anim_lineup, a.anim_facing)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
