"""Alfheim roles for hd2d sprite (original, Hearthmoor realm-alfheim branch). Imported by sprite.py.

NPCs (named: only on sheets whose spec lists them), the light elves of Lumenvale. Clothing rule (style lock §8): a
top and a bottom in clearly different values, a darker waist band, shoes that contrast with the trousers. Elves get
small pointed ears (`elf: True`, drawn by `elf_ears` from sprite.py's draw_head).
  elfwarden   Warden Aelindra Starwell: long silver hair, sky-blue tunic to the hip with a cream collar, gold belt,
              navy trousers, tall dark boots, a staff
  elfranger   Ranger Thalion Duskbough: gold hair, moss tunic under a dark leaf vest, brown belt, timber trousers,
              boots, an elven glaive (spear)
  wispkeeper  Nyssa Glimmerfold, the wisp-catcher: auburn long hair, cream blouse, blue sash-belt, deep-blue skirt,
              a wisp lantern (cold-fire blue)
  elfchild    a Lumenvale child: white hair, sky top, dark belt, navy shorts

Enemies (20x32, anims idle / walk / attack / die, palette pixels; their violet comes from lights and pools):
  prismshard    a floating cluster of prism crystals with a white heart; fires prism bolts
  neonwisp      a neon will-o-wisp: a bright orb with a flame tail and two dot eyes, orbiting sparks
  crystalgolem  the stone golem re-cut in pale crystal, rose-crystal veins and shoulder spires
  mirrorduelist Mirror Duelist (elite): a light-elf duelist with mirror-glass skin, dark coat to the hip, gold belt,
                dark trousers, brown boots and a mirror rapier; shatters into glass when beaten
"""
from __future__ import annotations

import math

from roles_enemies import ell, rect, shader, golem, _Remap, _golem_b

E = dict(kind="enemy", enemy=True, anims=("idle", "walk", "attack", "die"))


def alfheim_roles(_r):
    return {
        "elfwarden": _r(desc="Warden Aelindra Starwell of Lumenvale: long silver hair, pointed ears, sky-blue tunic to the hip "
                             "with a cream collar, gold belt, navy trousers, tall dark boots, a staff",
                        hair="white", hairstyle="long", shirt="sky", collar="plaster_hi", tunic=1, belt="flower_gold",
                        pants="cloth", boots=True, shoes="shadow", item="staff", elf=True, named=True),
        "elfranger": _r(desc="Ranger Thalion Duskbough: gold hair, pointed ears, moss tunic under a dark leaf vest, brown belt, "
                             "timber trousers, dark boots, an elven glaive", hair="flower_gold", hairstyle="messy",
                        shirt="moss", vest="leaf_deep", belt="timber_lo", pants="timber", boots=True, shoes="shadow",
                        item="spear", elf=True, named=True),
        "wispkeeper": _r(desc="Nyssa Glimmerfold the wisp-catcher: auburn long hair, pointed ears, cream blouse, blue belt, "
                              "deep-blue skirt, dark shoes, a cold-fire wisp lantern", hair="roof_hi", hairstyle="long",
                         shirt="plaster_hi", belt="flower_blue", skirt="cloth", shoes="shadow", item="bluelantern",
                         elf=True, named=True),
        "elfchild": _r(desc="a Lumenvale child: white hair, pointed ears, sky top, dark belt, navy shorts, brown shoes",
                       layout="kid", hair="white", hairstyle="cowlick", shirt="sky", belt="shadow", pants="cloth",
                       shoes="timber", elf=True, named=True),
        "prismshard": _r(**E, draw="prismshard", named=True, desc="Alfheim prism shard: a floating cluster of prism crystals, white heart, fires prism bolts"),
        "neonwisp": _r(**E, draw="neonwisp", named=True, desc="Alfheim neon will-o-wisp: a bright orb with a flame tail, dot eyes, orbiting sparks"),
        "crystalgolem": _r(**E, draw="crystalgolem", named=True, desc="Alfheim crystal golem: the golem in pale crystal, rose-crystal veins, shoulder spires"),
        "mirrorduelist": _r(**E, draw="mirrorduelist", named=True, desc="Mirror Duelist (elite): light-elf duelist, mirror-glass skin, dark coat, gold belt, dark trousers, brown boots, mirror rapier"),
    }


# ------------------------------------------------------------------ elf ears (called from sprite.py draw_head)
def elf_ears(s, face, top, spans, skin, skin_lo):
    a, b = spans[6]
    if face in ("down", "up"):
        s.set(a - 1, top + 6, skin); s.set(a - 1, top + 5, skin); s.set(a - 2, top + 4, skin_lo)
        s.set(b + 1, top + 6, skin_lo); s.set(b + 1, top + 5, skin); s.set(b + 2, top + 4, skin_lo)
    else:   # profile: one ear, its tip sweeping up and back
        ex = a + (b - a + 1) // 2
        s.set(ex + 1, top + 5, skin); s.set(ex + 2, top + 4, skin); s.set(ex + 3, top + 3, skin_lo)


# ------------------------------------------------------------------ prism shard
def _diamond(s, cx, cy, hw, hh, cols, glint=None):
    """a vertical crystal: a diamond hw wide each side, hh tall each way; cols = (hi, mid, lo) lit from the left"""
    hi, mid, lo = cols
    for y in range(int(cy - hh), int(cy + hh) + 1):
        w = hw * (1 - abs(y - cy) / max(1, hh))
        for x in range(int(round(cx - w)), int(round(cx + w)) + 1):
            s.set(x, y, hi if x < cx - w * 0.3 else lo if x > cx + w * 0.4 else mid)
    if glint:
        s.set(int(cx - 1), int(cy - hh * 0.4), glint)


def prismshard(s, face, anim, i):
    b = [0, -1, -1, 0][i] if anim == "idle" else [0, -1, 0, 1][i] if anim == "walk" else [0, -1, -2, 0][i] if anim == "attack" else [0, 1, 3, 6][i]
    if anim == "die" and i >= 2:   # a little heap of spent crystal shards
        for (x, y, c) in ((6, 29, "sky"), (8, 28, "white"), (10, 29, "flower_blue"), (12, 28, "sky"), (13, 30, "cloth"), (9, 30, "flower_rose")):
            s.set(x, y, c); s.set(x + 1, y, "flower_blue")
        if i == 2:
            s.set(9, 27, "white"); s.set(11, 26, "sky")
        return
    spread = 1 if anim == "attack" and i in (1, 2) else 0
    cy = 16 + b
    side = face == "left"
    cols = ("white", "sky", "flower_blue")
    deep = ("sky", "flower_blue", "cloth")
    if face == "up":
        cols, deep = deep, ("flower_blue", "cloth", "shadow")
    # back shards, then the tall middle one
    _diamond(s, 5 - spread + (1 if side else 0), cy + 2, 2.2, 5, deep)
    _diamond(s, 14 + spread - (2 if side else 0), cy + 1, 2.4, 6, deep)
    _diamond(s, 9.5 - (1 if side else 0), cy - 1, 3.4, 9, cols, "white")
    # the white-hot heart (face) and rose glints
    if face != "up":
        hx = 8 if side else 9
        s.set(hx, cy - 1, "white"); s.set(hx + 1, cy - 1, "white"); s.set(hx, cy, "flower_rose")
        if not side:
            s.set(hx + 1, cy, "flower_rose")
    for k in range(3):   # orbiting prism motes
        a = k / 3 * math.tau + i * 0.9
        x, y = 9.5 + math.cos(a) * 8, cy + 4 + math.sin(a) * 3
        s.set(int(round(x)), int(round(y)), "flower_rose" if k % 2 else "white")
    for y in range(cy + 9, min(31, cy + 12)):   # a faint prism wisp under the floating cluster
        if (y + i) % 2 == 0:
            s.set(9 + (y + i) % 3 - 1, y, "flower_blue")
    if anim == "attack" and i == 2:
        cx = 16 if face != "left" else 3
        s.set(cx, cy - 2, "white"); s.set(cx - 1, cy - 2, "flower_rose"); s.set(cx + 1, cy - 2, "flower_rose"); s.set(cx, cy - 3, "sky"); s.set(cx, cy - 1, "sky")


# ------------------------------------------------------------------ neon wisp
def neonwisp(s, face, anim, i):
    b = [0, -1, -2, -1][i] if anim in ("idle", "walk") else [0, -1, -2, 0][i] if anim == "attack" else [0, 1, 3, 5][i]
    if anim == "die" and i >= 2:
        for (x, y) in ((7, 29), (10, 28), (12, 29)):
            s.set(x, y, "flower_blue" if i == 3 else "sky")
        s.set(9, 30, "cloth")
        return
    cy = 14 + b
    swell = 1 if anim == "attack" and i in (1, 2) else 0
    shrink = i if anim == "die" else 0
    r = 4.6 + swell - shrink
    # flame tail flickering down and away
    for y in range(int(cy + 2), min(30, int(cy + 11 - shrink * 2))):
        t = (y - cy - 2) / 9
        w = max(0, int(round(3 * (1 - t))))
        sway = (1 if (y + i) % 4 < 2 else -1) * int(t * 2)
        for x in range(9 - w + sway, 10 + w + sway + 1):
            s.set(x, y, "flower_blue" if abs(x - 9.5 - sway) > w * 0.5 else "sky")
    ell(s, 9.5, cy, r + 1, r + 0.6, "flower_blue")
    ell(s, 9.5, cy, r, r - 0.3, "sky")
    ell(s, 9.0, cy - 0.5, r * 0.55, r * 0.5, "white")
    if face == "down":
        s.set(8, int(cy), "cloth"); s.set(11, int(cy), "cloth")
    elif face == "left":
        s.set(7, int(cy), "cloth")
    for k in range(4):   # sparks orbiting (rose = the violet's warm edge in the palette)
        a = k / 4 * math.tau + i * 0.8
        x, y = 9.5 + math.cos(a) * (r + 3), cy + math.sin(a) * (r + 1.5)
        if 1 <= x < 19 and 1 <= y < 31:
            s.set(int(round(x)), int(round(y)), "flower_rose" if k % 2 else "white")


# ------------------------------------------------------------------ crystal golem
CRYSTAL = {"stone_hi": "white", "stone": "sky", "stone_lo": "flower_blue", "shadow": "cloth", "moss": "flower_rose",
           "grass": "plaster_hi", "grass_hi": "white", "lamp": "white", "flower_gold": "flower_rose", "plaster_lo": "plaster_hi"}


def crystalgolem(s, face, anim, i):
    golem(_Remap(s, CRYSTAL), face, anim, i)
    if anim == "die" and i >= 2:
        s.set(5, 25, "white"); s.set(14, 26, "flower_rose"); s.set(9, 27, "sky")
        return
    b = _golem_b(anim, i)
    if face == "left":
        spires = ((11, 6), (13, 5), (15, 7))
    else:
        spires = ((4, 9), (6, 7), (13, 7), (15, 9)) if face == "down" else ((5, 8), (14, 8), (9, 5), (11, 5))
    for k, (x, y) in enumerate(spires):   # rose / white crystal spires out of the shoulders
        for d in range(3):
            s.set(x, y + b - d, "white" if d == 2 else "flower_rose" if (k + d) % 2 else "sky")
    if face == "down":
        s.set(9, 6 + b, "white"); s.set(10, 5 + b, "flower_rose")


# ------------------------------------------------------------------ mirror duelist
def mirrorduelist(s, face, anim, i):
    """a light-elf duelist (elite): mirror-glass skin, silver hair, a dark coat to the hip, a gold belt, dark trousers,
    brown boots; attack = a lunge with the mirror rapier; die = the glass cracks and falls in a glittering heap"""
    skin, skin_lo, coat, coat_hi, belt, pants, boot, hair = "stone_hi", "stone", "cloth", "flower_blue", "flower_gold", "shadow", "timber_lo", "white"
    if anim == "die" and i >= 2:
        for (x, y, c) in ((5, 29, "cloth"), (7, 28, "white"), (9, 29, "sky"), (11, 28, "stone_hi"), (13, 29, "cloth"), (14, 30, "flower_gold"),
                          (8, 30, "shadow"), (10, 30, "white"), (12, 30, "timber_lo")):
            s.set(x, y, c); s.set(x + 1, y, c if i == 2 else "shadow")
        if i == 2:
            s.set(6, 27, "white"); s.set(12, 26, "sky")
        return
    b = 0; lunge = 0; lift = (0, 0); blade = "rest"; crack = 0
    if anim == "idle":
        b = [0, 0, 1, 1][i]
    elif anim == "walk":
        b = [0, -1, 0, -1][i]; lift = [(1, 0), (0, 0), (0, 1), (0, 0)][i]
    elif anim == "attack":
        lunge = [0, -1, 2, 1][i]; blade = ["guard", "draw", "thrust", "recover"][i]; b = [0, 0, 1, 0][i]
    elif anim == "die":
        crack = i + 1; b = [1, 2, 0, 0][i]
    side = face == "left"
    dx = -lunge if side else 0
    dy = lunge if face == "down" else -lunge if face == "up" else 0
    # legs + boots
    if side:
        legs = [(8 + dx, lift[0]), (10 + dx, lift[1])]
    else:
        legs = [(7, lift[0]), (11, lift[1])]
    for lx, lf in legs:
        rect(s, lx, 21 + b, lx + 1, 27 - lf, pants)
        rect(s, lx, 28 - lf, lx + 1, 29 - lf, boot)
        s.set(lx + (0 if side else 1), 21 + b, "ink")
    # coat to the hip + gold belt (the waist), lapels
    x0, x1 = (7 + dx, 12 + dx) if side else (6, 13)
    rect(s, x0, 12 + b + dy // 2, x1, 19 + b, coat)
    if not side:
        rect(s, x0 - 1, 12 + b, x1 + 1, 13 + b, coat)
    rect(s, x0, 12 + b + dy // 2, x0, 19 + b, coat_hi)
    rect(s, x0, 20 + b, x1, 20 + b, belt)
    s.set((x0 + x1) // 2, 20 + b, "white")
    if face == "down":
        s.set(9, 13 + b, "stone_hi"); s.set(10, 13 + b, "stone_hi"); s.set(9, 14 + b, coat_hi); s.set(10, 14 + b, coat_hi)
    if crack:
        for k in range(crack + 1):
            s.set(x0 + 1 + (k * 2) % 5, 14 + b + k * 2, "white")
    # head: a rounded mirror-glass face, silver hair (long, tied back), pointed ears, a pale glint
    hx0 = (6 + dx) if side else 6
    top = 3 + b + dy // 2
    spans = [(hx0 + (2 if r in (0, 8) else 1 if r in (1, 7) else 0), hx0 + 7 - (2 if r in (0, 8) else 1 if r in (1, 7) else 0)) for r in range(9)]
    for r, (a0, b0) in enumerate(spans):
        rect(s, a0, top + r, b0, top + r, skin)
        s.set(b0, top + r, skin_lo)
    if face == "up":
        for r, (a0, b0) in enumerate(spans):
            rect(s, a0, top + r, b0, top + r, hair)
        rect(s, hx0 + 3, top + 9, hx0 + 4, top + 12, hair)
        s.set(hx0 - 1, top + 5, skin); s.set(hx0 - 2, top + 4, skin_lo); s.set(hx0 + 8, top + 5, skin); s.set(hx0 + 9, top + 4, skin_lo)
    elif side:
        for r in range(4):
            rect(s, spans[r][0], top + r, spans[r][1], top + r, hair)
        for r in range(3, 9):
            rect(s, hx0 + 4, top + r, spans[r][1], top + r, hair)
        rect(s, hx0 + 6, top + 9, hx0 + 7, top + 11, hair)
        s.set(hx0 + 1, top + 5, "cloth"); s.set(hx0 - 1, top + 6, skin); s.set(hx0 + 1, top + 2, "white")
        s.set(hx0 + 4, top + 4, skin); s.set(hx0 + 5, top + 3, skin); s.set(hx0 + 6, top + 2, skin_lo)   # pointed ear
    else:
        for r in range(3):
            rect(s, spans[r][0], top + r, spans[r][1], top + r, hair)
        s.set(spans[3][0], top + 3, hair); s.set(spans[3][1], top + 3, hair); s.set(spans[4][0], top + 4, hair); s.set(spans[4][1], top + 4, hair)
        s.set(hx0 + 2, top + 5, "cloth"); s.set(hx0 + 5, top + 5, "cloth"); s.set(hx0 + 2, top + 6, "flower_blue"); s.set(hx0 + 5, top + 6, "flower_blue")
        s.set(hx0 + 2, top + 1, "white")
        s.set(hx0 - 1, top + 5, skin); s.set(hx0 - 2, top + 4, skin_lo)   # pointed ears
        s.set(hx0 + 8, top + 5, skin); s.set(hx0 + 9, top + 4, skin_lo)
    # arms + the mirror rapier
    if face == "down":
        rect(s, 4, 13 + b, 5, 18 + b, coat); s.set(4, 19 + b, skin)
        if blade in ("rest", "guard", "recover"):
            rect(s, 14, 13 + b, 15, 18 + b, coat); s.set(15, 19 + b, skin)
            for k in range(8):
                s.set(16, 19 + b + k if 19 + b + k < 31 else 30, "white" if k % 3 == 0 else "sky")
            s.set(15, 18 + b, belt); s.set(17, 18 + b, belt)
        else:
            reach = 3 if blade == "draw" else 6
            rect(s, 13, 17 + b, 14, 19 + b + min(2, reach // 2), coat)
            for k in range(reach + 4):
                y = 20 + b + k
                if y < 31:
                    s.set(13, y, "white" if k % 3 == 0 else "sky")
    elif face == "up":
        rect(s, 4, 13 + b, 5, 18 + b, coat); rect(s, 14, 13 + b, 15, 18 + b, coat)
        if blade == "thrust":
            for k in range(6):
                s.set(14, 11 + b - k, "white" if k % 2 else "sky")
        else:
            for k in range(6):
                s.set(16, 13 + b + k, "sky")
    else:
        if blade in ("draw", "thrust"):
            reach = 3 if blade == "draw" else 7
            rect(s, x0 - 2, 15 + b, x0, 16 + b, coat); s.set(x0 - 3, 16 + b, skin)
            for k in range(reach):
                s.set(x0 - 4 - k, 16 + b, "white" if k % 3 == 0 else "sky")
        else:
            rect(s, x0 + 1, 13 + b, x0 + 2, 18 + b, coat); s.set(x0 + 1, 19 + b, skin)
            for k in range(7):
                s.set(x0, 19 + b + k if 19 + b + k < 31 else 30, "white" if k % 3 == 0 else "sky")


DRAW = {"prismshard": prismshard, "neonwisp": neonwisp, "crystalgolem": crystalgolem, "mirrorduelist": mirrorduelist}
