"""Hearthmoor hero classes for hd2d sprite (Norse Nine Realms story; all original designs).

Six playable origins, same 20x32 spec as the villagers (4 facings x idle 4 + walk 4) plus a 4-frame action
pose in the cast columns (8-11). Everyone casts; the brawlers swing a weapon wreathed in their magic. The glow
is crisp emissive pixels (gloom-and-glow, no bloom). Each class has its own silhouette cue so they read apart:
  wildcaller    Midgard farmhand  mortal   blond mop, rust tunic, rolled sleeves, satchel, long hoe; hearth sparks
  runeguard     Shield-warden     mortal   chestnut braids, mail + leather, round shield with glowing light runes, axe
  seer          Rune-reader       mortal   grey hooded cloak with a stitched rune, rune-stone pouch, rune staff
  stormborn     Child of thunder  demigod  bulky build, storm-blue cloak, silver circlet, stone war-hammer; lightning
  grovekeeper   Child of the Vanir demigod moss-green hair, flower crown, leaf mantle, mushroom charms; neon heal
  cinderknight  Ember-born        demigod  bulky dark plate, ember hair, ash cheek marks, greatsword with ember edge
Imported by sprite.py; hooks: hero_roles(), draw_hat(), draw_hair(), draw_extras().
"""

HERO_ORDER = ["wildcaller", "runeguard", "seer", "stormborn", "grovekeeper", "cinderknight"]


def hero_roles(_r):
    H = dict(hero=True, caster=True)
    return {
        "wildcaller": _r(**H, cls="Wildcaller", origin="mortal", origin_name="Midgard farmhand", style="caster",
                         pose="attack", weapon="hoe", fx="hearth", trail=("plaster_hi", "white"),
                         desc="Wildcaller (Midgard farmhand, mortal): blond mop, rust tunic, rolled sleeves, satchel, long hoe; warm hearth sparks",
                         hair="flower_gold", hairstyle="messy", shirt="roof_hi", pants="timber", shoes="timber_lo",
                         satchel="timber_hi", sleeves="rolled", forearm="skin"),
        "runeguard": _r(**H, cls="Runeguard", origin="mortal", origin_name="Shield-warden", style="brawler",
                        pose="attack", weapon="axe", shield=True, fx="light", trail=("flower_gold", "white"),
                        desc="Runeguard (Shield-warden, mortal paladin brawler): chestnut braids, mail, leather jerkin, round shield with glowing light runes, axe",
                        hair="timber_hi", hairstyle="braids", shirt="stone", vest="timber", pants="timber_lo",
                        boots=True, shoes="timber_lo", mail=True),
        "seer": _r(**H, cls="Seer", origin="mortal", origin_name="Rune-reader", style="caster",
                   pose="cast", weapon="runestaff", fx="rune", pouch=True,
                   desc="Seer (Rune-reader, mortal): grey hooded cloak with a stitched rune, rune-stone pouch, rune-carved staff; rune glow",
                   hat="hood", hatc="stone", hair="timber", shirt="plaster_lo", cloak="stone",
                   pants="timber_lo", shoes="timber_lo", hem="flower_blue"),
        "stormborn": _r(**H, cls="Stormborn", origin="demigod", origin_name="Child of thunder", style="brawler",
                        pose="attack", weapon="stormhammer", fx="thunder", layout="broad", trail=("sky", "white"),
                        desc="Stormborn (Child of thunder, demigod brawler): bulky build, storm-blue cloak, silver circlet, stone war-hammer; lightning",
                        hat="circlet", hatc="stone_hi", hair="timber_lo", hairstyle="spiky", shirt="stone_hi",
                        cloak="cloth", pants="shadow", shoes="shadow", boots=True),
        "grovekeeper": _r(**H, cls="Grovekeeper", origin="demigod", origin_name="Child of the Vanir", style="caster",
                          pose="cast", fx="vanir", charms=True,
                          desc="Grovekeeper (Child of the Vanir, demigod): moss-green hair, flower crown, leaf-and-moss mantle, mushroom charms; neon green heal",
                          hat="crown", hair="grass_hi", hairstyle="long", shirt="plaster_hi", skirt="plaster_hi",
                          cloak="leaf_deep", shawl="moss", shoes="timber", leaves=True),
        "cinderknight": _r(**H, cls="Cinderknight", origin="demigod", origin_name="Ember-born", style="brawler",
                           pose="attack", weapon="greatsword", fx="ember", ash=True, layout="broad", plate=True,
                           trail=("roof_hi", "lamp"),
                           desc="Cinderknight (Ember-born, demigod dark-knight brawler): heavy dark plate, ember hair, ash cheek marks and hands, greatsword with an ember edge",
                           hair="roof_hi", hairstyle="flame", shirt="shadow", vest=None, pants="stone_lo",
                           shoes="ink", boots=True, sleeves="rolled", forearm="stone_lo", handc="stone_hi"),
    }


# ------------------------------------------------------------------ helpers
def _fx(s, x, y, c):
    """Effect pixel: keep a 1 px ring free for the ink outline and stay above the feet rows."""
    if 1 <= x <= 18 and 1 <= y <= 27:
        s.set(x, y, c)


def _line(x0, y0, x1, y1):
    pts, dx, dy = [], abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    while True:
        pts.append((x0, y0))
        if x0 == x1 and y0 == y1:
            return pts
        e2 = 2 * err
        if e2 >= dy:
            err += dy; x0 += sx
        if e2 <= dx:
            err += dx; y0 += sy


def _sleeve(spec):
    return spec["cloak"] or spec["shirt"]


def _arm(s, spec, sh, hand, thick=2):
    """Arm from shoulder to hand, 2 px thick; rolled sleeves turn to bare forearm after 2 px."""
    sl = _sleeve(spec)
    fore = spec.get("forearm") if spec.get("sleeves") == "rolled" else None
    pts = _line(sh[0], sh[1], hand[0], hand[1])[:-1]
    for k, (x, y) in enumerate(pts):
        c = sl if (fore is None or k < 2) else fore
        if fore and k == 2:
            c = "plaster_hi" if fore == "skin" else "stone"      # the roll / a plate cuff
        s.set(x, y, c)
        if thick > 1:
            s.set(x + 1, y, s.pal.dk(c))
    hc = spec.get("handc") or spec["skin"]
    s.set(hand[0], hand[1], hc)
    if thick > 1:
        s.set(hand[0] + 1, hand[1], s.pal.dk(hc))


DIRS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}


def _put(s, x, y, c):
    """Tool / gear pixel: inside the outline ring, above the feet rows."""
    if 1 <= x <= 18 and 1 <= y <= 27:
        s.set(x, y, c)
FLIP = {"left": "right", "right": "left", "up": "up", "down": "down"}


def _tool(s, kind, hx, hy, d, hook=-1):
    """Held tool from the hand at (hx, hy) along direction d. Vertical tools put their head on the hook side
    (-1 screen-left / +1 screen-right); level tools put it on top (hook -1) or underneath (hook +1)."""
    if not kind:
        return
    if kind == "runestaff":
        for y in range(max(1, hy - 6), min(27, hy + 7) + 1):
            _put(s, hx, y, "timber")
        for y in range(hy - 4, min(27, hy + 7) + 1, 3):
            _put(s, hx, y, "flower_blue")                        # carved, inked runes
        _put(s, hx, hy - 7, "stone_hi"); _put(s, hx + 1, hy - 7, "stone"); _put(s, hx - 1, hy - 7, "stone_hi")
        _put(s, hx, hy - 8, "sky")                               # the rune-stone set in the head
        return
    dx, dy = DIRS[d]
    qx, qy = (0, hook) if dy == 0 else (hook, 0)
    P = lambda a, b: (hx + dx * a + qx * b, hy + dy * a + qy * b)
    put = lambda a, b, c: _put(s, *P(a, b), c)
    if kind == "hoe":
        for a in range(-3, 9):
            put(a, 0, "timber" if a % 4 else "timber_hi")
        put(9, 0, "timber"); put(10, 0, "timber_lo")
        put(10, 1, "stone_lo"); put(9, 1, "stone"); put(9, 2, "stone")          # a broad iron blade
        put(8, 1, "stone_hi"); put(8, 2, "stone_hi"); put(8, 3, "white")
    elif kind == "axe":
        for a in range(-1, 6):
            put(a, 0, "timber")
        put(6, 0, "timber_lo")
        for a in (3, 4, 5):
            put(a, 1, "stone")
        put(2, 2, "stone_hi"); put(3, 2, "stone_hi"); put(4, 2, "stone_hi"); put(5, 2, "white"); put(6, 2, "stone_hi")
    elif kind == "stormhammer":
        put(1, 0, "timber"); put(2, 0, "timber_lo")
        for b in (-2, -1, 0, 1, 2):
            put(3, b, "stone_hi"); put(4, b, "stone"); put(5, b, "stone_lo")
        put(4, 0, "sky"); put(4, -1, "white")                    # a lit storm rune in the face
    elif kind == "greatsword":
        put(-1, 0, "roof_hi"); put(0, 0, "timber_lo")            # ember pommel, grip
        for b in (-1, 0, 1):
            put(1, b, "stone")                                   # crossguard
        for a in range(2, 12):
            put(a, 0, "stone_lo")                                # dark blade
            put(a, hook, "lamp" if a % 3 else "roof_hi")         # glowing ember edge
        put(12, 0, "flower_gold")
    elif kind == "handhammer":
        for a in (1, 2):
            put(a, 0, "timber")
        for b in (-1, 0, 1):
            put(3, b, "stone_hi"); put(4, b, "stone")
        put(4, 0, "flower_gold")                                 # gold band round the head


SHIELD_RUNE = [(1, 0), (0, 1), (2, 1), (1, 2), (0, 3), (2, 3)]   # invented "light" rune: a lit diamond with two feet


def _shield(s, cx, cy, w=6, glow=0):
    """Round shield near (cx, cy): storm-blue face, timber rim, a light rune that glows (0 lit, 1 bright, 2 flare)."""
    rows = [(1, w - 2), (0, w - 1), (0, w - 1), (0, w - 1), (0, w - 1), (1, w - 2)]
    x0, y0 = cx - w // 2, cy - 3
    for r, (a, b) in enumerate(rows):
        for k in range(a, b + 1):
            edge = k in (a, b) or r in (0, 5)
            _put(s, x0 + k, y0 + r, "timber" if edge else "cloth")
    rx = x0 + (w - 3) // 2
    for (x, y) in SHIELD_RUNE:
        _put(s, rx + x, y0 + 1 + y, "flower_gold" if glow < 2 else "white")
    if glow:
        _put(s, rx + 1, y0 + 2, "white")                          # the rune's heart lights up
    if glow == 2:
        for (x, y) in ((-1, -1), (w, 0), (-1, 6), (w, 5), (w // 2, -2)):
            _fx(s, x0 + x, y0 + y, "flower_gold" if (x + y) % 2 else "white")


RUNE = [(0, 0), (2, 0), (1, 1), (1, 2), (0, 3), (2, 3), (1, 0)]   # an invented glyph: a forked stave


def _effect(s, kind, fx, fy, k):
    if kind == "rune":
        if k == 0:
            _fx(s, fx, fy, "sky")
            return
        ox, oy = (fx - 1, fy - 2) if k < 3 else (fx - 3, fy - 4)
        for (x, y) in RUNE:
            _fx(s, ox + x, oy + y, "white" if k == 2 else "sky")
        if k >= 2:
            _fx(s, ox - 2, oy + 4, "flower_blue"); _fx(s, ox + 4, oy - 1, "flower_blue")
        if k == 3:
            _fx(s, fx, fy, "flower_blue"); _fx(s, fx - 1, fy - 1, "sky")
    elif kind == "thunder":
        bolt = [(0, 0), (1, -1), (0, -2), (1, -3), (2, -4)]
        if k == 0:
            _fx(s, fx + 1, fy - 1, "sky"); _fx(s, fx - 1, fy, "white")
        elif k == 1:
            for (x, y) in bolt[:4]:
                _fx(s, fx + x, fy - 1 + y, "white")
            _fx(s, fx - 2, fy, "sky")
        elif k == 2:
            for (x, y) in bolt:
                _fx(s, fx + x, fy - 1 + y, "white")
                _fx(s, fx - 2 - x, fy + y, "sky")
            _fx(s, fx + 3, fy, "flower_gold"); _fx(s, fx - 3, fy - 5, "flower_gold")
        else:
            for (x, y) in bolt[:4]:
                _fx(s, fx - 2 - x, fy + 1 + y // 2, "white"); _fx(s, fx + 2 + x, fy + 1 + y // 2, "sky")
            _fx(s, fx, fy + 2, "flower_gold")
    elif kind == "vanir":
        if k == 0:
            _fx(s, fx, fy, "white"); _fx(s, fx + 1, fy, "grass_hi")
            return
        r = 1 if k == 1 else 2
        for (x, y) in ((0, -r), (r, 0), (0, r), (-r, 0)):
            _fx(s, fx + x, fy + y, "grass_hi")
        if r == 2:
            for (x, y) in ((1, -1), (1, 1), (-1, 1), (-1, -1)):
                _fx(s, fx + x, fy + y, "grass")
        _fx(s, fx, fy, "white")
        if k >= 2:
            _fx(s, fx - 3, fy - 3, "grass"); _fx(s, fx + 3, fy - 4, "grass_hi")
        if k == 3:
            _fx(s, fx + 4, fy, "flower_gold"); _fx(s, fx - 4, fy + 1, "flower_gold")
    elif kind == "ember":
        flame = {0: [(0, 0, "lamp")],
                 1: [(0, 0, "roof_hi"), (-1, 0, "roof_hi"), (1, 0, "roof_hi"), (0, -1, "lamp"), (0, -2, "flower_gold")],
                 2: [(-1, 0, "roof_hi"), (0, 0, "lamp"), (1, 0, "roof_hi"), (-1, -1, "roof_hi"), (0, -1, "white"),
                     (1, -1, "lamp"), (0, -2, "lamp"), (0, -3, "flower_gold"), (1, -4, "roof_hi")],
                 3: [(0, 0, "roof_hi"), (1, 0, "lamp"), (0, -1, "lamp"), (1, -1, "flower_gold"), (-1, -2, "roof_hi"),
                     (-2, -4, "lamp")]}[k]
        for (x, y, c) in flame:
            _fx(s, fx + x, fy - 1 + y, c)
        if k >= 2:
            _fx(s, fx + 3, fy - 3, "lamp")
    elif kind == "hearth":                      # the Wildcaller's strike wakes the soil: a sprout and warm motes
        if k >= 2:
            _fx(s, fx, fy, "grass_hi"); _fx(s, fx, fy - 1, "grass"); _fx(s, fx + 1, fy - 2, "grass_hi")
        if k == 3:
            for (x, y, c) in ((3, -4, "lamp"), (-1, -5, "flower_gold"), (5, -2, "white"), (2, -7, "flower_gold")):
                _fx(s, fx + x, fy + y, c)
    elif kind == "emberaura":                   # Cinderknight flame aura: embers rising round the body
        pts = [(2, 18, "lamp"), (17, 17, "roof_hi"), (3, 12, "flower_gold"), (16, 11, "lamp"), (1, 24, "roof_hi"),
               (18, 23, "lamp"), (9, 3, "flower_gold")]
        for (x, y, c) in pts[: 3 + 2 * k]:
            _fx(s, x, y - (k % 2), c)


def _trail(s, pts, dust=False, cols=("plaster_hi", "white")):
    """Weapon swoosh: a solid 1 px arc through the points (white head, cream tail), only on empty pixels so it
    never paints over the body. dust=True leaves a small kicked-up dust puff instead."""
    if dust:
        for (x, y) in pts:
            for (dx, dy, c) in ((0, 0, "plaster"), (1, 0, "plaster_hi"), (0, -1, "stone_hi")):
                if 1 <= x + dx <= 18 and 1 <= y + dy <= 27 and s.p[y + dy][x + dx] is None:
                    s.set(x + dx, y + dy, c)
        return
    path = []
    for a, b in zip(pts, pts[1:]):
        seg = _line(a[0], a[1], b[0], b[1])
        path += seg if not path else seg[1:]
    n = len(path)
    for k, (x, y) in enumerate(path):
        if 1 <= x <= 18 and 1 <= y <= 27 and s.p[y][x] is None:
            s.set(x, y, cols[1] if k >= n // 2 else cols[0])


# ------------------------------------------------------------------ action-pose tables
# down-facing, screen coords relative to torso top T. R = screen-right hand (character's left), L = screen-left.
# each frame: (R hand, R tool dir, L hand, L tool dir, focus, fx k, trail points)
def _trail_any(s, trail, cols=("plaster_hi", "white")):
    if isinstance(trail, tuple):                    # ("dust", [(x, y), ...])
        _trail(s, trail[1], dust=True)
    else:
        _trail(s, trail, cols=cols)


def _poses(spec, T):
    w, pose = spec.get("weapon"), spec.get("pose")
    if w == "hoe":   # R rests; the hoe swings in L: raise, back over the shoulder, chop, dust
        return [((14, T + 6), None, (3, T + 1), "up", None, 0, []),
                ((14, T + 6), None, (4, T - 2), "right", None, 0, [(2, T + 2), (2, T - 1)]),
                ((13, T + 5), None, (12, T + 6), "left", None, 0, [(2, T - 4), (1, T), (2, T + 4)]),
                ((13, T + 5), None, (12, T + 7), "left", (3, T + 9), 3, ("dust", [(2, T + 10), (5, T + 9)]))]
    if w == "axe":   # axe in L, shield carried on R
        return [((14, T + 4), None, (3, T - 1), "up", None, 0, []),
                ((14, T + 4), None, (5, T - 4), "up", None, 0, [(2, T + 1), (2, T - 2)]),
                ((14, T + 4), None, (8, T + 6), "down", None, 0, [(2, T - 3), (2, T), (3, T + 3), (5, T + 6), (6, T + 8)]),
                ((11, T + 5), None, (3, T + 6), "down", None, 0, [])]
    if w == "runestaff":
        return [((13, T + 4), "staff", (6, T + 4), None, "staffhead", 0, []),
                ((16, T), "staff", (5, T + 5), None, "staffhead", 1, []),
                ((16, T - 3), "staff", (3, T + 2), None, "staffhead", 2, []),
                ((14, T + 2), "staff", (3, T + 1), None, "staffhead", 3, [])]
    if w == "greatsword":   # two-handed: raise, overhead (ember flare), ember slash, flame aura
        return [((15, T + 2), "up", (13, T + 3), None, None, 0, []),
                ((16, T - 3), "up", (14, T - 2), None, None, 0, [(17, T + 4), (18, T + 1)]),
                ((9, T + 6), "left", (11, T + 6), None, None, 0, [(18, T - 6), (18, T - 1), (16, T + 4), (12, T + 8), (6, T + 9)]),
                ((7, T + 7), "left", (9, T + 7), None, "aura", 3, [])]
    if w in ("handhammer", "stormhammer"):
        return [((13, T + 4), "up", (6, T + 4), None, "toolhead", 0, []),
                ((16, T - 1), "up", (5, T + 5), None, "toolhead", 1, []),
                ((16, T - 3), "up", (3, T + 3), None, "toolhead", 2, []),
                ((13, T + 5), "down", (5, T + 5), None, "toolhead", 3, [])]
    if spec.get("fx") == "vanir":
        return [((12, T + 4), None, (7, T + 4), None, (9, T + 4), 0, []),
                ((17, T + 2), None, (2, T + 2), None, (9, T + 3), 1, []),
                ((16, T - 2), None, (3, T - 2), None, (9, T + 5), 2, []),
                ((13, T + 6), None, (6, T + 6), None, (9, T + 9), 3, [])]
    # ember: flame in the R palm
    return [((13, T + 4), None, (6, T + 4), None, (13, T + 4), 0, []),
            ((15, T + 2), None, (5, T + 5), None, (15, T + 1), 1, []),
            ((16, T), None, (5, T + 5), None, (16, T - 1), 2, []),
            ((14, T + 3), None, (4, T + 4), None, (12, T + 1), 3, [])]


# profile facing left: near arm only. (hand, tool dir, focus, k, trail)
def _poses_side(spec, T):
    w = spec.get("weapon")
    if w == "hoe":
        return [((8, T - 1), "up", None, 0, []),
                ((9, T - 2), "right", None, 0, [(5, T - 5), (3, T - 3)]),
                ((9, T + 5), "left", None, 0, [(14, T - 6), (9, T - 7), (4, T - 5), (2, T - 1)]),
                ((9, T + 6), "left", (3, T + 9), 3, ("dust", [(2, T + 10), (5, T + 9)]))]
    if w == "axe":   # near arm holds the shield; the axe arcs over from the far side
        return [((6, T + 4), None, None, 0, []),
                ((6, T + 4), None, None, 0, []),
                ((6, T + 4), None, None, 0, [(13, T - 3), (10, T - 6), (6, T - 6), (3, T - 4)]),
                ((4, T + 4), None, None, 0, [])]
    if w == "runestaff":
        return [((7, T + 4), "staff", "staffhead", 0, []), ((6, T), "staff", "staffhead", 1, []),
                ((5, T - 3), "staff", "staffhead", 2, []), ((3, T + 2), "staff", "staffhead", 3, [])]
    if w == "greatsword":
        return [((8, T - 1), "up", None, 0, []),
                ((10, T - 3), "right", None, 0, [(6, T - 6), (3, T - 4)]),
                ((9, T + 4), "left", None, 0, [(15, T - 7), (9, T - 8), (4, T - 6), (1, T - 2), (1, T + 2)]),
                ((9, T + 6), "left", "aura", 3, [])]
    if w in ("handhammer", "stormhammer"):
        return [((8, T + 4), "up", "toolhead", 0, []), ((8, T - 1), "up", "toolhead", 1, []),
                ((7, T - 3), "up", "toolhead", 2, []), ((3, T + 3), "left", "toolhead", 3, [])]
    if spec.get("fx") == "vanir":
        return [((7, T + 4), None, (5, T + 4), 0, []), ((5, T + 2), None, (3, T + 2), 1, []),
                ((5, T - 2), None, (4, T - 4), 2, []), ((3, T + 4), None, (3, T + 7), 3, [])]
    return [((7, T + 4), None, (7, T + 4), 0, []), ((6, T + 2), None, (6, T + 1), 1, []),
            ((5, T), None, (5, T - 1), 2, []), ((3, T + 2), None, (3, T + 1), 3, [])]


def _focus(f, hand, d):
    if f == "aura":
        return (0, 0)
    if f == "staffhead":
        return (hand[0], hand[1] - 9)
    if f == "toolhead":
        dx, dy = DIRS[d]
        return (hand[0] + dx * 5, hand[1] + dy * 5)
    return f


def _hook(d, face, side):
    if d in ("left", "right"):
        return 1 if d == "left" else -1       # chop: blade under the haft; over the shoulder: blade up
    toward_body = 1 if side == "L" else -1
    return toward_body if face == "down" else -toward_body


def _mx(p):
    return (19 - p[0], p[1]) if p else p


def draw_action(s, spec, L, face, top, x0, x1, i):
    """The hero's 4-frame action (cast or attack), drawn after the head so raised arms and tools sit in front."""
    T = top
    if face in ("down", "up"):
        R, Rd, Lh, Ld, foc, k, trail = _poses(spec, T)[i]
        if face == "up":                     # seen from behind: the same pose, mirrored
            R, Lh, foc = _mx(R), _mx(Lh), _mx(foc) if isinstance(foc, tuple) else foc
            trail = ("dust", [_mx(p) for p in trail[1]]) if isinstance(trail, tuple) else [_mx(p) for p in trail]
            Rd, Ld = (FLIP.get(Rd, Rd) if Rd else Rd), (FLIP.get(Ld, Ld) if Ld else Ld)
        shR, shL = ((x1 + 1, T + 1), (x0 - 1, T + 1)) if face == "down" else ((x0 - 2, T + 1), (x1, T + 1))
        _trail_any(s, trail, spec.get("trail") or ("plaster_hi", "white"))
        if spec.get("shield"):
            # shield arm: carried / braced / bash
            _arm(s, spec, shR, R)
            sx = R[0] + (1 if face == "down" else 0)
            _shield(s, min(16, max(4, sx)), R[1] - 1, glow=(0, 1, 1, 2)[i])
        else:
            _arm(s, spec, shR, R)
            if Rd == "staff":
                _tool(s, "runestaff", R[0], R[1], "up")
            elif Rd:
                _tool(s, spec.get("weapon"), R[0], R[1], Rd, hook=_hook(Rd, face, "R"))
        _arm(s, spec, shL, Lh)
        if Ld:
            _tool(s, spec.get("weapon"), Lh[0], Lh[1], Ld, hook=_hook(Ld, face, "L"))
        if spec.get("fx") and foc is not None:
            fp = _focus(foc, R, Rd)
            _effect(s, "emberaura" if foc == "aura" else spec["fx"], fp[0], fp[1], k)
    else:
        hand, d, foc, k, trail = _poses_side(spec, T)[i]
        _trail_any(s, trail, spec.get("trail") or ("plaster_hi", "white"))
        if spec.get("weapon") == "axe":
            # far-side axe: behind the head (wind-up), overhead, chop forward, at the hip during the bash
            ax = [((13, T - 1), "up"), ((9, T - 3), "up"), ((4, T + 2), "left"), ((12, T + 5), "down")][i]
            _tool(s, "axe", ax[0][0], ax[0][1], ax[1])
            _arm(s, spec, (9, T + 1), hand)
            _shield(s, hand[0] + (0 if i < 3 else -1), hand[1] - 1, w=5 if i < 3 else 6, glow=(0, 1, 1, 2)[i])
            return
        _arm(s, spec, (9, T + 1), hand)
        if d == "staff":
            _tool(s, "runestaff", hand[0], hand[1], "up")
        elif d:
            _tool(s, spec.get("weapon"), hand[0], hand[1], d, hook=(1 if d in ("left", "right") else -1))
        if spec.get("fx") and foc is not None:
            fp = _focus(foc, hand, d)
            _effect(s, "emberaura" if foc == "aura" else spec["fx"], fp[0], fp[1], k)


# ------------------------------------------------------------------ hats and hair
def draw_hat(s, spec, L, face, top, spans):
    hat, c = spec["hat"], spec["hatc"]
    a0, b0 = spans[2]
    lt, dk = s.pal.lt(c), s.pal.dk(c)
    h = L["head_h"]
    if hat == "hood":
        if face == "down":
            s.hspan(top - 1, a0 + 2, b0 - 2, c)
            for y in range(top, top + 4):
                s.hspan(y, a0 - 1, b0 + 1, c); s.set(b0 + 1, y, dk)
            for y in range(top + 4, top + h):
                s.hspan(y, a0 - 1, a0, c); s.hspan(y, b0, b0 + 1, c); s.set(b0 + 1, y, dk)
            s.hspan(top + 4, a0 + 1, b0 - 1, dk)                 # shadow under the brow
            s.hspan(top + h, a0, b0, c); s.hspan(top + h + 1, a0 + 1, b0 - 1, dk)   # cowl on the shoulders
            s.hspan(top, a0 + 1, a0 + 4, lt)
            s.set((a0 + b0) // 2, top + h, "flower_blue")       # rune clasp
        elif face == "up":
            s.hspan(top - 1, a0 + 2, b0 - 2, c); s.set((a0 + b0) // 2, top - 2, c)
            for y in range(top, top + h):
                s.hspan(y, a0 - 1, b0 + 1, c); s.set(b0 + 1, y, dk)
            s.hspan(top + h, a0, b0, c); s.hspan(top + h + 1, a0 + 1, b0 - 1, dk)
            for y in range(top + 2, top + h, 2):
                s.set((a0 + b0) // 2, y, dk)                     # fold down the back
            s.hspan(top, a0 + 1, a0 + 4, lt)
        else:
            s.hspan(top - 1, a0 + 1, b0 - 1, c)
            for y in range(top, top + 4):
                s.hspan(y, a0 - 1, b0 + 1, c); s.set(b0 + 1, y, dk)
            for y in range(top + 4, top + h):
                s.hspan(y, a0 + 5, b0 + 1, c); s.set(b0 + 1, y, dk)
            s.hspan(top + 4, a0, a0 + 4, dk)
            s.hspan(top + h, a0 + 3, b0 + 1, c)
            s.set(b0 + 2, top + 2, c); s.set(b0 + 2, top + 3, dk)   # hood point at the back
            s.hspan(top, a0, a0 + 3, lt)
    elif hat == "circlet":
        y = top + 3
        if face == "left":
            s.hspan(y, a0, b0 - 1, c); s.set(a0 + 1, y, "sky"); s.set(a0 + 3, y, "white")
        else:
            s.hspan(y, a0 + 1, b0 - 1, c); s.set(b0 - 1, y, s.pal.dk(c))
            if face == "down":
                s.set(9, y, "sky"); s.set(10, y, "sky"); s.set(9, y - 1, "white"); s.set(a0 + 2, y, "white")


def draw_hair(s, spec, L, face, top, spans):
    st, hair = spec["hairstyle"], spec["hair"]
    hd, hl = s.pal.dk(hair), s.pal.lt(hair)
    a0, b0 = spans[0]
    h = L["head_h"]
    if st == "braids":
        if face == "down":
            for x in (spans[5][0] - 1, spans[5][1] + 1):
                for y in range(top + 5, top + h + 3):
                    s.set(x, y, hair if (y + x) % 2 else hd)
                s.set(x, top + h + 3, "flower_gold")             # bead tie
        elif face == "up":
            for x in (7, 12):
                for y in range(top + h - 2, top + h + 4):
                    s.set(x, y, hair if y % 2 else hd)
                s.set(x, top + h + 4, "flower_gold")
        else:
            x = spans[6][1] - 1
            for y in range(top + h - 1, top + h + 4):
                s.set(x, y, hair if y % 2 else hd)
            s.set(x, top + h + 4, "flower_gold")
    elif st == "spiky":
        xs = range(a0, b0 + 1, 2)
        for k, x in enumerate(xs):
            sx = x + (1 if face == "left" and k > 1 else 0)
            s.set(sx, top - 1, hair)
            if k % 2:
                s.set(sx + (1 if face == "left" else 0), top - 2, hd)
        s.set(a0 + 1, top - 1, hl)
    elif st == "flame":
        tufts = [(a0 + 1, 1), (a0 + 3, 3), (a0 + 5, 2), (a0 + 7, 3), (b0 - 1, 1)]
        for x, n in tufts:
            for d in range(1, n + 1):
                sx = x + (d // 2 if face == "left" else 0)
                s.set(sx, top - d, "flower_gold" if d == n and n > 1 else ("lamp" if d == 2 else hair))
        s.set(a0 + 2, top, "lamp")


# ------------------------------------------------------------------ extras (idle / walk + always-on gear)
def _roll_sleeves(s, spec, L, face, top, swing, stride, x0, x1):
    fore = spec["forearm"]
    hand = spec.get("handc") or spec["skin"]
    n = L["arm_len"]
    if face in ("down", "up"):
        for side, ax in ((-1, x0 - 2), (1, x1 + 1)):
            sw = swing * (1 if side > 0 else -1)
            ln = n + (1 if sw > 0 else -1 if sw < 0 else 0)
            for y in range(top + 3, top + 1 + ln):
                s.hspan(y, ax, ax + 1, fore)
                s.set(ax + (1 if side > 0 else 0), y, s.pal.dk(fore) if side > 0 else fore)
            s.hspan(top + 2, ax, ax + 1, "plaster_hi" if fore == "skin" else "stone")
            if spec.get("handc"):
                s.hspan(top + 1 + ln, ax, ax + 1, hand)
    else:
        ax, dx = 9, -2 * stride
        for k, y in enumerate(range(top + 1, top + 1 + n)):
            ox = 0 if k < 2 else (dx // 2 if k < 4 else dx)
            if k == 1:
                s.hspan(y, ax + ox, ax + ox + 1, "plaster_hi" if fore == "skin" else "stone")
            elif k >= 2:
                s.set(ax + ox, y, fore); s.set(ax + ox + 1, y, s.pal.dk(fore))
        if spec.get("handc"):
            s.hspan(top + 1 + n, ax + dx, ax + dx + 1, hand)


def draw_extras(s, spec, L, face, bob, swing, stride, cast_i=None):
    if not spec.get("hero"):
        return
    top = L["torso_top"] + bob
    tw = L["torso_w"]
    x0 = 10 - tw // 2
    x1 = x0 + tw - 1
    bottom = L["hip"] + bob - 1
    hy = top + 1 + L["arm_len"]
    head_top = L["head_top"] + bob
    # mail rings under the jerkin
    if spec.get("mail"):
        for y in range(top + 1, bottom - 1, 2):
            for x in range(x0 + (1 if face != "left" else 2), x1, 2):
                if s.p[y][x] == s.pal[spec["shirt"]]:
                    s.set(x, y, "stone_lo")
    # leaf flecks on the Vanir mantle, rune stitching on the reader's hem
    if spec.get("leaves") or spec.get("hem"):
        cl = s.pal[spec["cloak"]]
        for y in range(top, 29):
            for x in range(20):
                if s.p[y][x] == cl:
                    if spec.get("leaves") and (x * 3 + y * 5) % 7 == 0:
                        s.set(x, y, "grass_hi" if (x + y) % 2 else "grass")
                    if spec.get("hem") and y >= min(28, L["hip"] + bob + 1) and x % 2 == 0:
                        s.set(x, y, spec["hem"])
    if spec.get("hem") and face == "up":
        for (x, y) in RUNE:
            s.set(9 + x, top + 3 + y, spec["hem"])               # a big stitched rune across the back
    # ash cheek marks
    if spec.get("ash"):
        ey = head_top + 6
        if face == "down":
            hx = 10 - L["head_w"] // 2
            for x in (hx + 2, hx + 3, hx + L["head_w"] - 4, hx + L["head_w"] - 3):
                s.set(x, ey + 2, "stone")
        elif face == "left":
            hx = 10 - L["head_w"] // 2 - 1
            s.set(hx + 3, ey + 2, "stone"); s.set(hx + 4, ey + 2, "stone")
    if cast_i is not None:
        draw_action(s, spec, L, face, top, x0, x1, cast_i)
    else:
        if spec.get("sleeves") == "rolled":
            _roll_sleeves(s, spec, L, face, top, swing, stride, x0, x1)
        w = spec.get("weapon")
        if face == "down":
            if w == "hoe":
                _tool(s, "hoe", 2, hy, "up", hook=1)
            elif w == "axe":
                _tool(s, "axe", 3, hy, "up", hook=-1)
            elif w == "runestaff":
                _tool(s, "runestaff", 17, hy, "up")
            elif w == "handhammer":
                _tool(s, "handhammer", 16, hy, "down")
            elif w == "stormhammer":
                _tool(s, "stormhammer", x1 + 2, hy - 1, "down")
            elif w == "greatsword":
                _tool(s, "greatsword", x1 + 2, hy, "up", hook=1)
        elif face == "up":
            if w == "hoe":
                _tool(s, "hoe", 17, hy, "up", hook=-1)
            elif w == "axe":
                _tool(s, "axe", 16, hy, "up", hook=1)
            elif w == "runestaff":
                _tool(s, "runestaff", 2, hy, "up")
            elif w == "handhammer":
                _tool(s, "handhammer", 3, hy, "down")
            elif w == "stormhammer":
                _tool(s, "stormhammer", x0 - 3, hy - 1, "down")
            elif w == "greatsword":
                _tool(s, "greatsword", x0 - 3, hy, "up", hook=-1)
        else:
            hx = 9 - 2 * stride
            if w == "hoe":
                _tool(s, "hoe", 5, hy, "up", hook=-1)
            elif w == "axe":
                _tool(s, "axe", 13, bottom - 2, "down", hook=1)
            elif w == "runestaff":
                _tool(s, "runestaff", 5, hy, "up")
            elif w == "handhammer":
                _tool(s, "handhammer", hx, hy, "down")
            elif w == "stormhammer":
                _tool(s, "stormhammer", hx, hy - 1, "down")
            elif w == "greatsword":
                _tool(s, "greatsword", 5, hy, "up", hook=-1)
        # idle crackle / ember mote (frame index carried in bob-free form via spec)
        k = spec.get("_idle")
        if k == 2 and spec.get("fx") == "thunder":
            hx_ = {"down": x1 + 2, "up": x0 - 3}.get(face, 9 - 2 * stride)
            _fx(s, hx_ + 2, hy + 3, "sky"); _fx(s, hx_ - 2, hy + 5, "white")
        if k == 2 and spec.get("fx") == "ember":
            hx_ = {"down": x1 + 2, "up": x0 - 3}.get(face, 5)
            _fx(s, hx_ + (1 if face == "down" else -1), hy - 13, "flower_gold")   # an ember lifting off the blade
        if k == 2 and spec.get("fx") == "rune":
            hx_ = {"down": 17, "up": 2}.get(face, 5)
            _fx(s, hx_, hy - 8, "white")
    # always-on gear
    # heavy dark plate: pauldrons and a glowing ember seam on the chest
    if spec.get("plate"):
        if face in ("down", "up"):
            for (a, b) in ((x0 - 2, x0 + 1), (x1 - 1, x1 + 2)):
                s.hspan(top, a, b, "stone_lo"); s.hspan(top + 1, a, b, "stone_lo")
                s.set(a + 1, top, "stone"); s.set(b, top + 1, "shadow")
            if face == "down":
                s.set(9, top + 3, "lamp"); s.set(10, top + 4, "roof_hi"); s.set(9, top + 5, "lamp")
                s.hspan(bottom, x0 + 1, x1 - 1, "stone_lo"); s.set(9, bottom, "lamp"); s.set(10, bottom, "lamp")
        else:
            s.hspan(top, 8, 12, "stone_lo"); s.hspan(top + 1, 8, 12, "stone_lo"); s.set(9, top, "stone")
            s.set(7, top + 4, "lamp")
    if spec.get("shield") and cast_i is None:
        if face == "down":
            _shield(s, 16, top + 5)
        elif face == "up":
            _shield(s, 10, top + 4)
        else:
            _shield(s, 7, top + 5, w=5)
    if spec.get("pouch"):
        px = {"down": x0, "up": x1 - 2, "left": x0 + 3}[face]
        s.hspan(bottom, px, px + 2, "timber_hi"); s.hspan(bottom + 1, px, px + 2, "timber")
        s.set(px + 1, bottom - 1, "timber_lo")
        if face != "up":
            s.set(px + 1, bottom, "plaster_hi"); s.set(px + 2, bottom + 1, "flower_blue")
    if spec.get("charms"):
        xs = {"down": (x0 + 1, x1 - 2), "up": (x0 + 1, x1 - 2), "left": (x0 + 3,)}[face]
        for x in xs:
            s.hspan(bottom + 1, x, x + 1, "roof_hi"); s.set(x, bottom + 1, "white")
            s.set(x + (1 if x < 10 else 0), bottom + 2, "plaster_hi")
