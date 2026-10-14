"""Svartalfheim pack shared bits: biome-tone registration (kit / fx only), the dwarf layout, a human_frame that also runs the
repo's hero action tables (so NPC-style roles such as Dagna get real attack / cast frames), and small drawing helpers."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_lib"))
import hmart as H  # noqa: E402
from hmart import ell, rect, shader  # noqa: E402,F401

SP = H.SP
import roles_heroes as RH  # noqa: E402  (repo, read-only import; already on sys.path via hmart)

# ---------------------------------------------------------------- Svartalfheim tones (story/svartalfheim.md 2.2)
# Biome tones on self-lit material / fx pixels. Never on the 20x32 or boss sprites (those stay cozy-village palette only).
SV = {
    "sv_forge": "#e0602a", "sv_forge_lo": "#c4502c", "sv_forge_hi": "#f2a63a",      # forge reds + copper (doc)
    "sv_rune": "#5ab4f0", "sv_rune_lo": "#94c0dc",                                  # cold-blue rune-light (doc; = cold fire)
    "sv_amethyst": "#7a4ab0",                                                       # violet crystal body (doc); tips = neon_violet
    "sv_water": "#3ac8b0",                                                          # blue-green cave water (doc)
    "sv_verdigris": "#5a9a7a",                                                      # copper roof edges (doc)
    # derived (staging): ramps for the doc tones
    "sv_water_hi": "#a8f4e4", "sv_water_lo": "#1c7a70",
    "sv_amethyst_lo": "#4a2a78",
    "sv_soot": "#26201e", "sv_ember": "#ffd890",
}
H.ALLC.update(SV)
# kit-only material colours (hex strings straight into the meshes)
BASALT = "#24222a"
BASALT_HI = "#3a3742"
SOOT_STONE = "#3e342e"
COPPER = "#b8643a"
COPPER_HI = "#d88a52"
BRASS = "#c09040"
BRASS_HI = "#e8c060"
IRON = "#4a4850"
IRON_HI = "#6e6c74"
WARM_WIN = "#ffb24a"

# ---------------------------------------------------------------- dwarf layout (natively short + broad; never scaled)
SP.LAYOUTS["dwarf"] = dict(head_top=12, head_w=12, head_h=10, torso_top=22, hip=26, torso_w=12, arm_len=4, leg_w=3)

# ---------------------------------------------------------------- human_frame with the hero action tables
ACT_RECOLOR = None      # set per frame: {palette name: palette name} applied to act-drawn pixels (ember hammer, blades)
_orig_tool = RH._tool


def _tool(s, kind, hx, hy, d, hook=-1):
    if kind == "shortblade" or (kind == "greatsword" and _STATE.get("blade")):
        _blade(s, hx, hy, d)
        return
    _orig_tool(s, kind, hx, hy, d, hook)


RH._tool = _tool
_STATE = {}


def _blade(s, hx, hy, d):
    """a short dark-elf blade (5 px) from the hand in direction d, a cold-blue edge glint at the tip"""
    dx, dy = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}.get(d, (0, -1))
    def put(x, y, c):
        if 0 < x < 19 and 0 < y < 31:
            s.set(x, y, c)
    put(hx + dx, hy + dy, "shadow")
    for a in range(2, 7):
        put(hx + dx * a, hy + dy * a, "stone_hi" if a < 6 else "sky")


def human_frame(spec, facing, anim, i):
    """hmart.human_frame + RH action frames for specs with hero=True (attack / cast / defend / jump)"""
    s = SP.HSprite(H.PAL)
    face = "left" if facing == "right" else facing
    L = SP.LAYOUTS[spec["layout"]]
    bob = blink = lift_l = lift_r = swing = stride = lift_b = 0
    sp = spec
    act = spec.get("hero") and anim in RH.ACTS
    _STATE["blade"] = spec.get("blades", False)
    if act:
        bob = RH.ACT_BOB[anim][i]
        sp = {**spec, "_act": (anim, i), "item": None}
    elif anim == "cast":
        bob = [0, -1, -1, 0][i]
        sp = {**spec, "_cast": i, "item": None}
    elif anim == "idle":
        bob, blink = SP.IDLE[i]
        sp = {**spec, "_idle": i}
    elif face in ("down", "up"):
        bob, lift_l, lift_r, swing = SP.WALK_FRONT[i]
    else:
        bob, stride, lift_b = SP.WALK_SIDE[i]
    if spec.get("hero") and not act and spec.get("stow"):
        sp = {**sp, "weapon": None}                 # weapon on the back (drawn by the hook) outside actions
    bob += sp["hunch"]
    if face == "up":
        lift_l, lift_r = lift_r, lift_l
        swing = -swing
    SP.draw_legs(s, sp, L, face, bob, lift_l, lift_r, stride, lift_b)
    SP.draw_body(s, sp, L, face, bob, swing, stride, anim, i)
    SP.draw_head(s, sp, L, face, bob, blink)
    before = [row[:] for row in s.p] if act and spec.get("act_recolor") else None
    SP.draw_extras(s, sp, L, face, bob, swing, stride)
    if before is not None:
        rc = {H.PAL[k] if hasattr(H.PAL, "__getitem__") else k: v for k, v in spec["act_recolor"].items()}
        for y in range(len(s.p)):
            for x in range(len(s.p[0])):
                c = s.p[y][x]
                if c is not None and c != before[y][x] and c in rc:
                    s.set(x, y, rc[c])
    if spec.get("_extra"):
        spec["_extra"](s, sp, L, face, bob, anim, i)
    s.outline("ink")
    if facing == "right":
        s.mirror()
    return s


H.human_frame = human_frame      # hmart.role_frame looks the name up at call time


# ---------------------------------------------------------------- helpers
def tline(s, x0, y0, x1, y1, w, col, hi=None, lo=None):
    """thick line: w px wide, optional light (left) / dark (right) edge colours"""
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    for k in range(n):
        t = k / max(1, n - 1)
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        r = w / 2
        for dy in range(-int(r) - 1, int(r) + 2):
            for dx in range(-int(r) - 1, int(r) + 2):
                if dx * dx + dy * dy <= r * r:
                    c = col
                    if hi and dx <= -r + 1:
                        c = hi
                    elif lo and dx >= r - 1:
                        c = lo
                    sset(s, x + dx, y + dy, c)


def sset(s, x, y, c):
    x, y = int(round(x)), int(round(y))
    if 0 <= y < len(s.p) and 0 <= x < len(s.p[0]):
        s.set(x, y, c)


def sget(s, x, y):
    x, y = int(round(x)), int(round(y))
    if 0 <= y < len(s.p) and 0 <= x < len(s.p[0]):
        return s.p[y][x]
    return None


def toad(s, x, y, w=2):
    """a tiny red toadstool cap with white spots on a cream stem"""
    for dy in range(0, w + 1):
        hw = int(round(math.sqrt(max(0, w * w - (dy * 1.6) ** 2))))
        for dx in range(-hw, hw + 1):
            sset(s, x + dx, y - dy, "roof_hi" if dx < hw else "roof")
    sset(s, x - 1, y - 1, "white"); sset(s, x + 1, y - w + 1, "white")
    sset(s, x, y + 1, "plaster_hi")


def gear(s, cx, cy, r, col, hi, lo, teeth=8, rot=0.0, hub="shadow"):
    """a small gear: ring with teeth, dark hub"""
    for y in range(int(cy - r - 2), int(cy + r + 3)):
        for x in range(int(cx - r - 2), int(cx + r + 3)):
            d = math.hypot(x - cx, y - cy)
            a = math.atan2(y - cy, x - cx) - rot
            tooth = math.cos(a * teeth) > 0.3
            if d <= r or (d <= r + 1.2 and tooth):
                u = (x - cx) / max(1, r)
                sset(s, x, y, hi if u < -0.35 else lo if u > 0.4 else col)
    if r >= 2:
        sset(s, cx, cy, hub)
