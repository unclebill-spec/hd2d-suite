"""Hearthmoor hero classes for hd2d sprite (Norse Nine Realms story; all original designs).

Six playable origins, same 20x32 spec as the villagers (4 facings x idle 4 + walk 4) plus a 4-frame action
pose in the cast columns (8-11). Everyone casts; the brawlers swing a weapon wreathed in their magic. The glow
is crisp emissive pixels (gloom-and-glow, no bloom). Each class has its own silhouette cue so they read apart:
  wildcaller    Midgard farmhand  mortal   blond mop, rust tunic, rolled sleeves, satchel, long hoe; hearth sparks
  runeguard     Shield-warden     mortal   chestnut braids, mail + leather, round shield with glowing light runes, axe
  seer          Rune-reader       mortal   short grey hooded robe cinched with a blue sash, brown trousers, dark boots, stitched rune, rune-stone pouch, rune staff
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
                         weapon="hoe", fx="hearth", trail=("plaster_hi", "white"),
                         desc="Wildcaller (Midgard farmhand, mortal): blond mop, rust tunic, rolled sleeves, satchel, long hoe; warm hearth sparks",
                         hair="flower_gold", hairstyle="messy", shirt="roof_hi", pants="timber", shoes="timber_lo",
                         satchel="timber_hi", sleeves="rolled", forearm="skin"),
        "runeguard": _r(**H, cls="Runeguard", origin="mortal", origin_name="Shield-warden", style="brawler",
                        weapon="axe", shield=True, fx="light", trail=("flower_gold", "white"),
                        desc="Runeguard (Shield-warden, mortal paladin brawler): chestnut braids, grey mail shirt and sleeves, tan leather tabard to the hip with a gold rune, dark belt, brown trousers, dark boots, round shield with glowing light runes, axe",
                        hair="timber_hi", hairstyle="braids", shirt="stone", tabard="timber_hi", belt="timber_lo",
                        pants="timber", boots=True, shoes="shadow", mail=True),
        "seer": _r(**H, cls="Seer", origin="mortal", origin_name="Rune-reader", style="caster",
                   weapon="runestaff", fx="rune", pouch=True,
                   desc="Seer (Rune-reader, mortal): grey hood, short pale-grey tunic-robe to mid-thigh cinched with a rune-blue sash, dark trousers, tan boots, stitched rune, rune-stone pouch, rune-carved staff; rune glow",
                   hat="hood", hatc="stone", hair="timber", shirt="stone_hi", tunic=2, sash="flower_blue",
                   pants="shadow", shoes="timber_hi", hem="flower_blue"),
        "stormborn": _r(**H, cls="Stormborn", origin="demigod", origin_name="Child of thunder", style="brawler",
                        weapon="stormhammer", fx="thunder", layout="broad", trail=("sky", "white"),
                        desc="Stormborn (Child of thunder, demigod brawler): bulky build, storm-blue cloak, silver circlet, stone war-hammer; lightning",
                        hat="circlet", hatc="stone_hi", hair="timber_lo", hairstyle="spiky", shirt="stone_hi",
                        cloak="cloth", pants="shadow", shoes="shadow", boots=True),
        "grovekeeper": _r(**H, cls="Grovekeeper", origin="demigod", origin_name="Child of the Vanir", style="caster",
                          fx="vanir", charms=True,
                          desc="Grovekeeper (Child of the Vanir, demigod): moss-green hair, flower crown, leaf-and-moss mantle over a cream blouse, dark belt, grass-green skirt, mushroom charms; neon green heal",
                          hat="crown", hair="grass_hi", hairstyle="long", shirt="plaster_hi", skirt="grass",
                          belt="timber_lo", cloak="leaf_deep", shawl="moss", shoes="timber", leaves=True),
        "cinderknight": _r(**H, cls="Cinderknight", origin="demigod", origin_name="Ember-born", style="brawler",
                           weapon="greatsword", fx="ember", ash=True, layout="broad", plate=True,
                           trail=("roof_hi", "lamp"),
                           desc="Cinderknight (Ember-born, demigod brawler): ember-red jerkin over a pale shirt collar, one small plate pauldron, bracers, dark belt with a glowing ember buckle, charcoal trousers, brown boots, ember hair, ash cheek marks, greatsword with an ember edge",
                           hair="roof_hi", hairstyle="flame", shirt="roof", collar="plaster_lo", vest=None,
                           belt="timber_lo", pants="stone_lo", shoes="timber", boots=True, sleeves="rolled",
                           forearm="stone_lo", handc="stone_hi"),
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
    elif kind == "hearthorb":                   # Wildcaller warm hearth-light orb (lamp / gold / white only)
        if k == 0:
            _fx(s, fx, fy, "lamp")
        elif k == 1:
            for (x, y) in ((0, -1), (1, 0), (0, 1), (-1, 0)):
                _fx(s, fx + x, fy + y, "lamp")
            _fx(s, fx, fy, "white")
        elif k == 2:
            for x in (-1, 0, 1):
                for y in (-1, 0, 1):
                    _fx(s, fx + x, fy + y, "lamp" if (x or y) else "white")
            for (x, y) in ((0, -3), (3, 0), (-3, 0), (2, -2), (-2, -2)):
                _fx(s, fx + x, fy + y, "flower_gold")
        else:
            _fx(s, fx, fy, "white"); _fx(s, fx - 1, fy, "lamp"); _fx(s, fx, fy + 1, "lamp")
            for (x, y, c) in ((3, 2, "flower_gold"), (5, 4, "lamp"), (2, 5, "flower_gold"), (-2, 3, "lamp")):
                _fx(s, fx + x, fy + y, c)
    elif kind == "light":                       # Runeguard light rune forming above the axe
        if k == 0:
            _fx(s, fx, fy, "white")
            return
        for (x, y) in SHIELD_RUNE:
            _fx(s, fx - 1 + x, fy - 2 + y, "white" if k >= 2 else "flower_gold")
        if k >= 2:
            for (x, y) in ((-3, -3), (3, -3), (-3, 2), (3, 2)):
                _fx(s, fx + x, fy + y, "flower_gold")
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


# ------------------------------------------------------------------ action sets
# Every hero has four action anims of 4 frames in all four facings (right = mirrored left, up = mirrored down):
#   cast    a spell with crisp glow pixels             attack  weapon melee / combo with a swoosh arc
#   defend  guard: shield up, weapon crosswise, or a small ward glyph
#   jump    crouch, launch, airborne (tucked), land. Frames stay feet-anchored; the runtime lifts the sprite
#           on a jump arc while the shadow stays on the ground.
ACTS = ("cast", "attack", "defend", "jump")
ACT_BOB = {"cast": [0, -1, -1, 0], "attack": [0, -1, 0, 1], "defend": [1, 1, 1, 1], "jump": [2, -1, 1, 3]}
MAIN_HAND = {"hoe": "L", "axe": "L", "runestaff": "R", "stormhammer": "R", "greatsword": "R"}
WARD = {"hearth": ("lamp", "flower_gold", "white"), "rune": ("sky", "flower_blue", "white"),
        "vanir": ("grass_hi", "grass", "white")}


def F(**kw):
    return kw


def _trail_any(s, trail, cols=("plaster_hi", "white")):
    if not trail:
        return
    if isinstance(trail, tuple):                    # ("dust", [(x, y), ...])
        _trail(s, trail[1], dust=True)
    else:
        _trail(s, trail, cols=cols)


def _vine(s, pts):
    """Grovekeeper vine lash: a solid moss/grass whip through the points, leaf buds along it, a bright tip."""
    path = []
    for a, b in zip(pts, pts[1:]):
        seg = _line(a[0], a[1], b[0], b[1])
        path += seg if not path else seg[1:]
    for k, (x, y) in enumerate(path[1:], 1):
        _fx(s, x, y, "grass" if k % 2 else "moss")
        if k % 3 == 0:
            _fx(s, x, y - 1, "grass_hi")
    if path:
        _fx(s, *path[-1], "grass_hi")


def _ward(s, kind, fx, fy, k):
    """A small guard glyph: core spark (k0), diamond (k1), wide diamond ring (k2), ring + corner sparks (k3)."""
    ring, alt, core = WARD[kind]
    if k >= 1:
        r = 1 if k == 1 else 2
        pts = [(0, -r), (r, 0), (0, r), (-r, 0)] + ([(1, -1), (1, 1), (-1, 1), (-1, -1)] if r == 2 else [])
        for i, (x, y) in enumerate(pts):
            _fx(s, fx + x, fy + y, ring if i < 4 else alt)
    if k == 3:
        for (x, y) in ((-3, -2), (3, -2), (-3, 2), (3, 2)):
            _fx(s, fx + x, fy + y, alt)
    _fx(s, fx, fy, core)


def _spark(s, fx, fy, k, col):
    _fx(s, fx, fy, "white")
    for (x, y) in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        _fx(s, fx + x, fy + y, col)
    if k >= 1:
        for (x, y) in ((2, -2), (-2, -2), (2, 2), (-2, 2)):
            _fx(s, fx + x, fy + y, col)


def _fx_any(s, fx, foc):
    kind, k = fx[0], fx[2]
    if kind == "spark":
        _spark(s, foc[0], foc[1], k, fx[3] if len(fx) > 3 else "flower_gold")
    elif kind == "aura":
        _effect(s, "emberaura", 0, 0, k)
    elif kind == "lightaura":
        for (x, y, c) in [(2, 17, "flower_gold"), (17, 15, "white"), (3, 10, "white"), (16, 9, "flower_gold"),
                          (1, 23, "flower_gold"), (18, 22, "white"), (9, 2, "flower_gold")][: 3 + 2 * k]:
            _fx(s, x, y, c)
    else:
        _effect(s, kind, foc[0], foc[1], k)


def _staffbar(s, hx, hy, d):
    """The Seer's staff held level: butt 4 px behind the hand, rune-stone head 7 px ahead."""
    dx = -1 if d == "left" else 1
    for a in range(-4, 7):
        _put(s, hx + dx * a, hy, "flower_blue" if a in (-3, 2) else "timber")
    _put(s, hx + dx * 7, hy, "stone_hi"); _put(s, hx + dx * 7, hy - 1, "sky"); _put(s, hx + dx * 8, hy, "stone_hi")


def _tool_any(s, spec, t, k, hx, hy, hook):
    if not t:
        return
    if t == "staff":
        _tool(s, "runestaff", hx, hy, "up")
    elif t.startswith("bar_"):
        _staffbar(s, hx, hy, t[4:])
    else:
        _tool(s, k or spec.get("weapon"), hx, hy, t, hook=hook)


# ---- down-facing frames (screen coords from the torso top T; R = screen-right hand, L = screen-left hand)
def _front_table(spec, anim, T, x0, x1):
    w, fxk = spec.get("weapon"), spec.get("fx")
    if anim == "jump":
        main = MAIN_HAND.get(w)
        tool = {"R": dict(Rt="staff" if w == "runestaff" else ("up" if w else None)), "L": dict(Lt="up"), None: {}}[main]
        sh = dict(shield=("R", 0)) if spec.get("shield") else {}
        return [F(R=(x1 + 2, T + 6), L=(x0 - 2, T + 6), **tool, **sh),
                F(R=(x1 + 1, T - 3), L=(x0 - 1, T - 3), **tool, **sh),
                F(R=(min(17, x1 + 3), T + 1), L=(max(2, x0 - 3), T + 1), **tool, **sh),
                F(R=(x1 + 2, T + 7), L=(x0 - 2, T + 7), trail=("dust", [(2, 27), (16, 27)]), **tool, **sh)]
    if w == "hoe":
        if anim == "cast":   # hoe planted, the free hand lifts a warm hearth-light orb
            return [F(R=(13, T + 4), L=(2, T + 7), Lt="up", fx=("hearthorb", (13, T + 3), 0)),
                    F(R=(16, T), L=(2, T + 7), Lt="up", fx=("hearthorb", (16, T - 2), 1)),
                    F(R=(16, T - 3), L=(2, T + 7), Lt="up", fx=("hearthorb", (16, T - 5), 2)),
                    F(R=(14, T + 3), L=(2, T + 7), Lt="up", fx=("hearthorb", (12, T + 1), 3))]
        if anim == "attack":  # raise, back over the shoulder, chop, dust + sprout
            return [F(R=(14, T + 6), L=(3, T + 1), Lt="up"),
                    F(R=(14, T + 6), L=(4, T - 2), Lt="right", trail=[(2, T + 2), (2, T - 1)]),
                    F(R=(13, T + 5), L=(12, T + 6), Lt="left", trail=[(2, T - 4), (1, T), (2, T + 4)]),
                    F(R=(13, T + 5), L=(12, T + 7), Lt="left", fx=("hearth", (3, T + 9), 3), trail=("dust", [(2, T + 10), (5, T + 9)]))]
        return [F(R=(13, T + 5), L=(2, T + 7), Lt="up", ward=("hearth", (10, T + 5), k)) if k == 0 else
                F(R=(12, T + 3), L=(2, T + 7), Lt="up", ward=("hearth", (10, T + 5), k)) for k in range(4)]
    if w == "axe":
        if anim == "cast":   # axe to the sky, a light rune blazes above it, radiance falls
            return [F(R=(14, T + 4), shield=("R", 1), L=(4, T + 3), Lt="up", fx=("light", (4, T - 6), 0)),
                    F(R=(14, T + 4), shield=("R", 1), L=(4, T - 2), Lt="up", fx=("light", (4, T - 10), 1)),
                    F(R=(14, T + 4), shield=("R", 2), L=(5, T - 4), Lt="up", fx=("light", (5, T - 11), 2)),
                    F(R=(14, T + 4), shield=("R", 2), L=(3, T + 4), Lt="down", fx=("lightaura", None, 2))]
        if anim == "attack":  # brace, axe high, chop, shield bash with the rune flaring
            return [F(R=(14, T + 4), shield=("R", 0), L=(3, T - 1), Lt="up"),
                    F(R=(14, T + 4), shield=("R", 1), L=(5, T - 4), Lt="up", trail=[(2, T + 1), (2, T - 2)]),
                    F(R=(14, T + 4), shield=("R", 1), L=(8, T + 6), Lt="down", trail=[(2, T - 3), (2, T), (3, T + 3), (5, T + 6), (6, T + 8)]),
                    F(R=(11, T + 5), shield=("R", 2), L=(3, T + 6), Lt="down")]
        return [F(R=(13, T + 4), shield=("at", (14, T + 2), 1), L=(3, T + 6), Lt="down"),
                F(R=(11, T + 3), shield=("at", (10, T + 2), 1), L=(3, T + 6), Lt="down"),
                F(R=(11, T + 3), shield=("at", (10, T + 2), 2), L=(3, T + 6), Lt="down"),
                F(R=(11, T + 3), shield=("at", (10, T + 2), 2), L=(3, T + 6), Lt="down", fx=("spark", (14, T - 2), 1))]
    if w == "runestaff":
        if anim == "cast":
            return [F(R=(13, T + 4), Rt="staff", L=(6, T + 4), fx=("rune", "staffhead", 0)),
                    F(R=(16, T), Rt="staff", L=(5, T + 5), fx=("rune", "staffhead", 1)),
                    F(R=(16, T - 3), Rt="staff", L=(3, T + 2), fx=("rune", "staffhead", 2)),
                    F(R=(14, T + 2), Rt="staff", L=(3, T + 1), fx=("rune", "staffhead", 3))]
        if anim == "attack":  # staff wind-up, level sweep, rune-tipped strike, recover
            return [F(R=(16, T + 1), Rt="staff", L=(6, T + 5)),
                    F(R=(12, T + 3), Rt="bar_left", L=(9, T + 4), trail=[(17, T - 5), (18, T - 1), (17, T + 2)]),
                    F(R=(9, T + 5), Rt="bar_left", L=(11, T + 5), trail=[(17, T - 3), (16, T + 3), (13, T + 7)], fx=("spark", (2, T + 4), 1, "sky")),
                    F(R=(14, T + 3), Rt="staff", L=(5, T + 5), fx=("spark", (14, T - 6), 0, "sky"))]
        return [F(R=(17, T + 7), Rt="staff", L=(6, T + 4), ward=("rune", (10, T + 5), k)) for k in range(4)]
    if w == "stormhammer":
        if anim == "cast":
            return [F(R=(13, T + 4), Rt="up", L=(6, T + 4), fx=("thunder", "toolhead", 0)),
                    F(R=(16, T - 1), Rt="up", L=(5, T + 5), fx=("thunder", "toolhead", 1)),
                    F(R=(16, T - 3), Rt="up", L=(3, T + 3), fx=("thunder", "toolhead", 2)),
                    F(R=(13, T + 5), Rt="down", L=(5, T + 5), fx=("thunder", "toolhead", 3))]
        if anim == "attack":  # wind-up, side swing, low follow-through with ground sparks, recover crackling
            return [F(R=(16, T + 1), Rt="up", L=(6, T + 5)),
                    F(R=(10, T + 5), Rt="left", L=(8, T + 5), trail=[(18, T - 3), (18, T + 1), (15, T + 5), (13, T + 7)]),
                    F(R=(6, T + 6), Rt="down", L=(8, T + 6), trail=[(18, T - 2), (17, T + 3), (13, T + 7), (10, T + 9)], fx=("thunder", (6, T + 8), 3)),
                    F(R=(14, T + 4), Rt="up", L=(6, T + 5), fx=("spark", (14, T - 2), 0, "sky"))]
        hy = [T + 6, T + 3, T + 3, T + 3]
        return [F(R=(12, hy[k]), Rt="right", L=(5, hy[k]), haft=True,
                  fx=(None if k < 2 else ("spark", (16, T - 1), k - 2, "sky"))) for k in range(4)]
    if w == "greatsword":
        if anim == "cast":   # blade planted, the free palm calls an ember flame, the aura rises
            return [F(L=(4, T + 5), Lt="down", R=(13, T + 4), fx=("ember", (13, T + 4), 0)),
                    F(L=(4, T + 5), Lt="down", R=(15, T + 2), fx=("ember", (15, T + 1), 1)),
                    F(L=(4, T + 5), Lt="down", R=(16, T), fx=("ember", (16, T - 1), 2), fx2=("aura", None, 1)),
                    F(L=(4, T + 5), Lt="down", R=(14, T + 3), fx=("ember", (12, T + 1), 3), fx2=("aura", None, 3))]
        if anim == "attack":
            return [F(R=(15, T + 2), Rt="up", L=(13, T + 3)),
                    F(R=(16, T - 3), Rt="up", L=(14, T - 2), trail=[(17, T + 4), (18, T + 1)]),
                    F(R=(9, T + 6), Rt="left", L=(11, T + 6), trail=[(18, T - 6), (18, T - 1), (16, T + 4), (12, T + 8), (6, T + 9)]),
                    F(R=(7, T + 7), Rt="left", L=(9, T + 7), fx=("aura", None, 3))]
        hy = [T + 5, T + 2, T + 2, T + 2]
        return [F(R=(6, hy[k]), Rt="right", L=(4, hy[k] + 1),
                  fx=(None, None, ("spark", (17, T + 1), 0, "lamp"), ("aura", None, 1))[k]) for k in range(4)]
    # Grovekeeper: open hands; the vine lash is her weapon
    if anim == "cast":
        return [F(R=(12, T + 4), L=(7, T + 4), fx=("vanir", (9, T + 4), 0)),
                F(R=(17, T + 2), L=(2, T + 2), fx=("vanir", (9, T + 3), 1)),
                F(R=(16, T - 2), L=(3, T - 2), fx=("vanir", (9, T + 5), 2)),
                F(R=(13, T + 6), L=(6, T + 6), fx=("vanir", (9, T + 9), 3))]
    if anim == "attack":
        return [F(R=(15, T + 2), L=(6, T + 5), vine=[(15, T + 2), (17, T + 1), (17, T - 1), (15, T - 1)]),
                F(R=(16, T - 2), L=(5, T + 5), vine=[(16, T - 2), (17, T - 5), (15, T - 8), (17, T - 10)]),
                F(R=(13, T + 4), L=(6, T + 5), vine=[(13, T + 4), (10, T + 6), (6, T + 5), (3, T + 6), (1, T + 4)]),
                F(R=(12, T + 5), L=(6, T + 5), vine=[(12, T + 5), (8, T + 8), (4, T + 9), (2, T + 10)], fx=("vanir", (3, T + 8), 1))]
    return [F(R=(13, T + 5), L=(6, T + 5), ward=("vanir", (10, T + 5), 0))] + \
           [F(R=(13, T + 3), L=(6, T + 3), ward=("vanir", (10, T + 5), k)) for k in (1, 2, 3)]


# ---- left-profile frames: H = the near hand; far = a tool on the far side (kind, (x, y), dir)
def _side_table(spec, anim, T):
    w = spec.get("weapon")
    if anim == "jump":
        hs = [(11, T + 5), (7, T - 3), (4, T + 1), (6, T + 7)]
        out = []
        for k, h in enumerate(hs):
            f = F(H=h, trail=("dust", [(2, 27), (14, 27)]) if k == 3 else None)
            if w == "axe":
                f.update(far=("axe", (12, T + 3 if k != 1 else T - 2), "up"), shield=(h, 5, 0))
            elif w == "runestaff":
                f.update(Ht="staff")
            elif w:
                f.update(Ht="up")
            out.append(f)
        return out
    if w == "hoe":
        if anim == "cast":
            return [F(H=(7, T + 3), far=("hoe", (4, T + 7), "up"), fx=("hearthorb", (6, T + 1), 0)),
                    F(H=(6, T), far=("hoe", (4, T + 7), "up"), fx=("hearthorb", (5, T - 2), 1)),
                    F(H=(6, T - 3), far=("hoe", (4, T + 7), "up"), fx=("hearthorb", (5, T - 5), 2)),
                    F(H=(4, T + 1), far=("hoe", (4, T + 7), "up"), fx=("hearthorb", (2, T - 1), 3))]
        if anim == "attack":
            return [F(H=(8, T - 1), Ht="up"),
                    F(H=(9, T - 2), Ht="right", trail=[(5, T - 5), (3, T - 3)]),
                    F(H=(9, T + 5), Ht="left", trail=[(14, T - 6), (9, T - 7), (4, T - 5), (2, T - 1)]),
                    F(H=(9, T + 6), Ht="left", fx=("hearth", (3, T + 9), 3), trail=("dust", [(2, T + 10), (5, T + 9)]))]
        return [F(H=(5, T + 3), far=("hoe", (12, T + 7), "up", 1), ward=("hearth", (3, T + 3), k)) for k in range(4)]
    if w == "axe":
        if anim == "cast":
            return [F(H=(6, T + 4), far=("axe", (12, T - 1), "up"), shield=((6, T + 4), 5, 1), fx=("light", (12, T - 8), 0)),
                    F(H=(6, T + 4), far=("axe", (10, T - 3), "up"), shield=((6, T + 4), 5, 1), fx=("light", (10, T - 11), 1)),
                    F(H=(6, T + 4), far=("axe", (9, T - 4), "up"), shield=((6, T + 4), 5, 2), fx=("light", (9, T - 12), 2)),
                    F(H=(6, T + 4), far=("axe", (12, T + 5), "down"), shield=((6, T + 4), 5, 2), fx=("lightaura", None, 2))]
        if anim == "attack":
            return [F(H=(6, T + 4), far=("axe", (13, T - 1), "up"), shield=((6, T + 4), 5, 0)),
                    F(H=(6, T + 4), far=("axe", (9, T - 3), "up"), shield=((6, T + 4), 5, 1)),
                    F(H=(6, T + 4), far=("axe", (4, T + 2), "left"), shield=((6, T + 4), 5, 1), trail=[(13, T - 3), (10, T - 6), (6, T - 6), (3, T - 4)]),
                    F(H=(4, T + 4), far=("axe", (12, T + 5), "down"), shield=((3, T + 4), 6, 2))]
        return [F(H=(6, T + 3), far=("axe", (12, T + 5), "down"), shield=((5, T + 2), 5, 1)),
                F(H=(5, T + 2), far=("axe", (12, T + 5), "down"), shield=((4, T + 1), 6, 1)),
                F(H=(5, T + 2), far=("axe", (12, T + 5), "down"), shield=((4, T + 1), 6, 2)),
                F(H=(5, T + 2), far=("axe", (12, T + 5), "down"), shield=((4, T + 1), 6, 2), fx=("spark", (2, T - 3), 1))]
    if w == "runestaff":
        if anim == "cast":
            return [F(H=(7, T + 4), Ht="staff", fx=("rune", "staffhead", 0)), F(H=(6, T), Ht="staff", fx=("rune", "staffhead", 1)),
                    F(H=(5, T - 3), Ht="staff", fx=("rune", "staffhead", 2)), F(H=(3, T + 2), Ht="staff", fx=("rune", "staffhead", 3))]
        if anim == "attack":   # level thrust with the rune-stone end
            return [F(H=(11, T + 3), Ht="bar_left"),
                    F(H=(8, T + 3), Ht="bar_left", trail=[(17, T + 1), (14, T + 1)]),
                    F(H=(7, T + 4), Ht="bar_left", fx=("spark", (1, T + 4), 1, "sky")),
                    F(H=(7, T + 4), Ht="staff", fx=("spark", (7, T - 6), 0, "sky"))]
        return [F(H=(5, T + 3), far=("runestaff", (12, T + 7), "up"), ward=("rune", (3, T + 3), k)) for k in range(4)]
    if w == "stormhammer":
        if anim == "cast":
            return [F(H=(8, T + 4), Ht="up", fx=("thunder", "toolhead", 0)), F(H=(8, T - 1), Ht="up", fx=("thunder", "toolhead", 1)),
                    F(H=(7, T - 3), Ht="up", fx=("thunder", "toolhead", 2)), F(H=(3, T + 3), Ht="left", fx=("thunder", "toolhead", 3))]
        if anim == "attack":
            return [F(H=(11, T + 1), Ht="up"),
                    F(H=(8, T - 2), Ht="up", trail=[(12, T + 2), (13, T - 2)]),
                    F(H=(4, T + 4), Ht="left", trail=[(13, T - 4), (9, T - 6), (4, T - 4), (2, T - 1)]),
                    F(H=(6, T + 6), Ht="down", fx=("thunder", (5, T + 8), 3))]
        return [F(H=(5, T + 5 if k == 0 else T + 4), Ht="up", fx=(None if k < 2 else ("spark", (5, T - 2), k - 2, "sky"))) for k in range(4)]
    if w == "greatsword":
        if anim == "cast":
            return [F(H=(7, T + 4), far=("greatsword", (4, T + 5), "down"), fx=("ember", (7, T + 4), 0)),
                    F(H=(6, T + 2), far=("greatsword", (4, T + 5), "down"), fx=("ember", (6, T + 1), 1)),
                    F(H=(5, T), far=("greatsword", (4, T + 5), "down"), fx=("ember", (5, T - 1), 2), fx2=("aura", None, 1)),
                    F(H=(3, T + 2), far=("greatsword", (4, T + 5), "down"), fx=("ember", (3, T + 1), 3), fx2=("aura", None, 3))]
        if anim == "attack":
            return [F(H=(8, T - 1), Ht="up"),
                    F(H=(10, T - 3), Ht="right", trail=[(6, T - 6), (3, T - 4)]),
                    F(H=(9, T + 4), Ht="left", trail=[(15, T - 7), (9, T - 8), (4, T - 6), (1, T - 2), (1, T + 2)]),
                    F(H=(9, T + 6), Ht="left", fx=("aura", None, 3))]
        return [F(H=(5, T + 5 if k == 0 else T + 3), Ht="up",
                  fx=(None, None, ("spark", (4, T - 9), 0, "lamp"), ("aura", None, 1))[k]) for k in range(4)]
    if anim == "cast":
        return [F(H=(7, T + 4), fx=("vanir", (5, T + 4), 0)), F(H=(5, T + 2), fx=("vanir", (3, T + 2), 1)),
                F(H=(5, T - 2), fx=("vanir", (4, T - 4), 2)), F(H=(3, T + 4), fx=("vanir", (3, T + 7), 3))]
    if anim == "attack":
        return [F(H=(7, T + 4), vine=[(7, T + 4), (5, T + 2), (7, T + 1), (8, T + 3)]),
                F(H=(6, T - 1), vine=[(6, T - 1), (5, T - 4), (7, T - 7), (5, T - 9)]),
                F(H=(4, T + 3), vine=[(4, T + 3), (2, T + 1), (1, T + 4), (1, T + 6)]),
                F(H=(4, T + 5), vine=[(4, T + 5), (2, T + 8), (1, T + 10)], fx=("vanir", (2, T + 8), 1))]
    return [F(H=(5, T + 3), ward=("vanir", (3, T + 3), k)) for k in range(4)]


def _focus(f, hand, d):
    if f == "staffhead":
        return (hand[0], hand[1] - 9)
    if f == "toolhead":
        dx, dy = DIRS[d]
        return (hand[0] + dx * 5, hand[1] + dy * 5)
    return f


def _hook(d, face, side):
    if d in ("left", "right"):
        return 1 if d == "left" else -1       # chop: blade under the haft; over the shoulder / crosswise: blade up
    toward_body = 1 if side == "L" else -1
    return toward_body if face == "down" else -toward_body


def _mx(p):
    return (19 - p[0], p[1]) if isinstance(p, tuple) else p


def draw_act(s, spec, L, face, top, x0, x1, anim, i):
    """Draw one action frame (after the head, so raised arms, tools and glow sit in front)."""
    T = top
    trail_cols = spec.get("trail") or ("plaster_hi", "white")
    if face in ("down", "up"):
        P = dict(_front_table(spec, anim, T, x0, x1)[i])
        up = face == "up"
        if up:                                   # seen from behind: the same pose, mirrored
            for key in ("R", "L"):
                if P.get(key):
                    P[key] = _mx(P[key])
            for key in ("Rt", "Lt"):
                if P.get(key):
                    P[key] = FLIP.get(P[key], P[key]) if not P[key].startswith("bar_") else \
                        "bar_" + FLIP[P[key][4:]]
            tr = P.get("trail")
            if tr:
                P["trail"] = ("dust", [_mx(q) for q in tr[1]]) if isinstance(tr, tuple) else [_mx(q) for q in tr]
            if P.get("vine"):
                P["vine"] = [_mx(q) for q in P["vine"]]
            for key in ("fx", "fx2"):
                if P.get(key) and isinstance(P[key][1], tuple):
                    P[key] = (P[key][0], _mx(P[key][1])) + tuple(P[key][2:])
            if P.get("shield") and P["shield"][0] == "at":
                P["shield"] = ("at", _mx(P["shield"][1]), P["shield"][2])
        shR, shL = ((x1 + 1, T + 1), (x0 - 1, T + 1)) if not up else ((x0 - 2, T + 1), (x1, T + 1))
        _trail_any(s, P.get("trail"), trail_cols)
        R, Lh = P.get("R"), P.get("L")
        if P.get("haft") and R and Lh:
            for (x, y) in _line(Lh[0], Lh[1], R[0], R[1]):
                _put(s, x, y, "timber")
        if R:
            _arm(s, spec, shR, R)
            _tool_any(s, spec, P.get("Rt"), P.get("Rk"), R[0], R[1], _hook(P.get("Rt"), face, "R") if P.get("Rt") else -1)
        if Lh:
            _arm(s, spec, shL, Lh)
            _tool_any(s, spec, P.get("Lt"), P.get("Lk"), Lh[0], Lh[1], _hook(P.get("Lt"), face, "L") if P.get("Lt") else -1)
        sh = P.get("shield")
        if sh:
            if sh[0] == "R":
                _shield(s, min(16, max(4, R[0] + (0 if up else 1))), R[1] - 1, glow=sh[1])
            else:
                _shield(s, sh[1][0], sh[1][1], glow=sh[2])
        if P.get("vine"):
            _vine(s, P["vine"])
        if P.get("ward"):
            kind, pos, k = P["ward"]
            if up:   # the glyph is in front of the body: from behind only its glow round the hands shows
                for hnd in (R, Lh):
                    if hnd:
                        _fx(s, hnd[0] + (1 if hnd[0] > 9 else -1), hnd[1] - 1, WARD[kind][0 if k else 2])
            else:
                _ward(s, kind, pos[0], pos[1], k)
        main = R if MAIN_HAND.get(spec.get("weapon"), "R") == "R" else Lh
        mdir = P.get("Rt") if main is R else P.get("Lt")
        for key in ("fx", "fx2"):
            fx = P.get(key)
            if fx and fx[0]:
                foc = _focus(fx[1], main or R, mdir) if isinstance(fx[1], str) else fx[1]
                _fx_any(s, fx, foc)
    else:
        P = _side_table(spec, anim, T)[i]
        _trail_any(s, P.get("trail"), trail_cols)
        far = P.get("far")
        if far:
            _tool(s, far[0], far[1][0], far[1][1], far[2], hook=(far[3] if len(far) > 3 else (1 if far[2] == "left" else -1)))
        H = P["H"]
        _arm(s, spec, (9, T + 1), H)
        ht = P.get("Ht")
        if ht:
            _tool_any(s, spec, ht, None, H[0], H[1], 1 if ht == "left" else -1)
        if P.get("shield"):
            pos, w, g = P["shield"]
            _shield(s, pos[0], pos[1] - 1, w=w, glow=g)
        if P.get("vine"):
            _vine(s, P["vine"])
        if P.get("ward"):
            kind, pos, k = P["ward"]
            _ward(s, kind, pos[0], pos[1], k)
        for key in ("fx", "fx2"):
            fx = P.get(key)
            if fx and fx[0]:
                foc = _focus(fx[1], H, ht) if isinstance(fx[1], str) else fx[1]
                _fx_any(s, fx, foc)


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


def draw_extras(s, spec, L, face, bob, swing, stride, act=None):
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
    if spec.get("hem") and spec.get("tunic"):
        y = L["hip"] + bob - 1 + spec["tunic"]                        # rune stitching on the tunic hem
        for x in range(1, 19, 2):
            if s.p[y][x] is not None and s.p[y][x] != s.pal["ink"]:
                s.set(x, y, spec["hem"])
    if spec.get("leaves") or (spec.get("hem") and spec.get("cloak")):
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
    if act is not None:
        draw_act(s, spec, L, face, top, x0, x1, act[0], act[1])
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
        # clothes, not armour: one small plate pauldron, ember lacing on the jerkin, a glowing ember buckle
        if face in ("down", "up"):
            a, b = (x1 - 1, x1 + 1) if face == "down" else (x0 - 1, x0 + 1)   # the character's left shoulder
            s.hspan(top, a, b, "stone"); s.hspan(top + 1, a, b, "stone_lo")
            s.set(a + 1, top, "stone_hi"); s.set(b, top + 1, "shadow")
            if face == "down":
                s.set(10, top + 3, "lamp"); s.set(10, top + 5, "lamp")          # ember lacing
                s.set(9, bottom, "lamp"); s.set(10, bottom, "lamp")              # ember buckle on the belt
        else:
            s.hspan(top, 8, 10, "stone"); s.hspan(top + 1, 8, 10, "stone_lo"); s.set(9, top, "stone_hi")
            s.set(x0, bottom, "lamp")
    if spec.get("shield") and act is None:
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
