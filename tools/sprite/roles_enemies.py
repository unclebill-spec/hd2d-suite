"""Hearthmoor stage-1 combat sprites: three enemies and six tiny hero summons (original designs, cozy HD-2D lock).

Same frame spec as every hd2d actor: 20x32, feet pivot bottom-centre, hard alpha, 1 px ink outline (added by the
caller), biome palette colours only. Gloom-and-glow: emissive palette pixels (lamp / gold / sky / white), no bloom.

  enemies (anims idle, walk, attack, die)
    golem      stone golem: mossy boulder body, amber rune seam and eyes, slams with both fists
    wraith     blue cold-fire wraith: hooded spectre, cold-fire hem and tail, casts a cold-fire orb
    skeleton   skeleton swordsman: big skull under a dark rune helm, dark breastplate, notched sword
    icegolem   frost golem (stage 3): the golem drawing re-cut in pale ice + ice spikes
    skelmage   skeleton mage (stage 3): hooded robe, staff with a cold-fire orb, fires arcane bolts
    eldergolem Mossheart, the Mossglen mini-boss (stage 3): dark stone, amber crown, glowing gold runes
  summons (anims idle, walk, attack)
    mushgolem    Wildcaller: a little mushroom golem
    runesentinel Runeguard: a floating rune stone on a pillar of light
    runewisp     Seer: a blue rune-wisp with an orbiting glyph
    stormsprite  Stormborn: a storm-cloud sprite walking on lightning
    sapling      Grovekeeper: a treant sapling
    emberimp     Cinderknight: a small fire elemental

Draw functions take (s, face, anim, i) with face in down / up / left (right is mirrored by the caller).
"""
from __future__ import annotations

import math

ENEMY_ANIMS = ("idle", "walk", "attack", "die")
SUMMON_ANIMS = ("idle", "walk", "attack")


# ------------------------------------------------------------------ helpers
def ell(s, cx, cy, rx, ry, col, fn=None):
    """filled ellipse; fn(x, y, col) -> colour lets the caller shade per pixel"""
    for y in range(int(cy - ry - 1), int(cy + ry + 2)):
        for x in range(int(cx - rx - 1), int(cx + rx + 2)):
            if ((x - cx) / max(rx, .01)) ** 2 + ((y - cy) / max(ry, .01)) ** 2 <= 1.0:
                s.set(x, y, fn(x, y, col) if fn else col)


def rect(s, x0, y0, x1, y1, col):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            s.set(x, y, col)


def shader(cx, rx, hi, mid, lo, light_left=True):
    """left third light, right third dark (the key light comes from the upper left)"""
    def f(x, y, col):
        u = (x - (cx - rx)) / max(1, 2 * rx)
        if not light_left:
            u = 1 - u
        return hi if u < 0.28 else lo if u > 0.74 else mid
    return f


# ------------------------------------------------------------------ stone golem
def golem(s, face, anim, i):
    b = 0
    lift_l = lift_r = 0
    arms = "rest"
    dust = False
    crack = 0
    if anim == "idle":
        b = [0, 0, 1, 1][i]
    elif anim == "walk":
        b = [0, 1, 0, 1][i]
        lift_l, lift_r = [(0, 0), (2, 0), (0, 0), (0, 2)][i]
    elif anim == "attack":
        arms = ["up", "high", "slam", "mid"][i]
        b = [0, -1, 2, 1][i]
        dust = i == 2
    elif anim == "die":
        crack = i + 1
        b = [1, 3, 0, 0][i]
    hi, mid, lo = "stone_hi", "stone", "stone_lo"
    glow = "lamp" if crack < 2 else "flower_gold"
    if anim == "die" and i >= 2:                       # crumbled into a heap of stones, runes fading
        top = 22 if i == 2 else 25
        ell(s, 9.5, 28, 9 if i == 2 else 8, 30 - top - 1.5, mid, shader(9.5, 9, hi, mid, lo))
        for (x, y) in ((4, 26), (8, 24), (13, 25), (15, 28), (6, 29), (11, 28)):
            if y >= top:
                s.set(x, y, lo); s.set(x + 1, y, hi)
        for (x, y) in ((7, top + 1), (12, top + 2), (3, 29)):
            s.set(x, y, "moss")
        if i == 2:
            s.set(9, 26, glow); s.set(10, 26, "white"); s.set(14, 27, glow)
        else:
            s.set(10, 28, "lamp")
        rect(s, 2, 30, 17, 30, lo)
        return
    side = face == "left"
    # legs (stubby boulders)
    if side:
        legs = [(6, lift_l), (11, lift_r)]
    else:
        legs = [(4, lift_l), (12, lift_r)]
    for lx, lift in legs:
        rect(s, lx, 25 + b, lx + 3, 30 - lift, lo if lx > 9 else mid)
        s.set(lx, 25 + b, hi)
    # body
    bcx = 10.5 if side else 9.5
    rx = 7.5 if side else 8
    ell(s, bcx, 18 + b, rx, 7.5, mid, shader(bcx, rx, hi, mid, lo))
    if side:   # profile: a big shoulder hump behind a heavy, low, square head with a brow ridge
        ell(s, 12, 11 + b, 5.5, 4.5, mid, shader(12, 5.5, hi, mid, lo))
        rect(s, 3, 9 + b, 9, 14 + b, mid)
        rect(s, 3, 9 + b, 4, 14 + b, hi)
        rect(s, 3, 8 + b, 9, 8 + b, hi)
        rect(s, 2, 10 + b, 8, 10 + b, lo)          # brow ridge shadow line
        rect(s, 3, 14 + b, 8, 14 + b, lo)          # jaw
    else:
        hcx = 9.5
        ell(s, hcx, 9 + b, 4.5, 3.6, mid, shader(hcx, 4.5, hi, mid, lo))
    # moss on head and shoulders
    for x in ((10, 11, 12, 14) if side else (6, 7, 11, 12)):
        s.set(x, (7 if side else 6) + b, "moss")
    if side:
        s.set(5, 8 + b, "moss"); s.set(6, 8 + b, "grass")
    for x in ((15, 16) if side else (3, 4, 15, 16)):
        s.set(x, 12 + b, "moss" if x % 2 else "grass")
    if face == "down":
        ey = 9 + b
        for ex in (8, 11):
            s.set(ex, ey, glow if crack < 3 else lo)
            s.set(ex, ey - 1, "shadow")
        s.set(9, ey + 2, "shadow"); s.set(10, ey + 2, "shadow")
        # rune seam down the chest
        for k, y in enumerate(range(14 + b, 24 + b)):
            s.set(9 + (k // 2) % 2, y, glow if (k + crack) % 4 else "white")
        s.set(8, 17 + b, glow); s.set(11, 19 + b, glow)
    elif face == "up":
        for (x, y) in ((6, 15), (7, 16), (12, 18), (13, 17), (9, 21)):
            s.set(x, y + b, "moss")
        for k, y in enumerate(range(15 + b, 22 + b)):
            s.set(10 if k % 3 else 9, y, lo)
        s.set(10, 18 + b, glow)
    else:
        s.set(4, 11 + b, glow if crack < 3 else lo); s.set(5, 11 + b, glow if crack < 3 else lo)
        s.set(4, 12 + b, "shadow"); s.set(3, 13 + b, "shadow"); s.set(4, 13 + b, "shadow")
        for k, y in enumerate(range(16 + b, 24 + b)):
            s.set(9 + (k // 3) % 2, y, glow if (k + crack) % 4 else "white")
    if crack:                                           # hit cracks
        for (x, y) in ((6, 14), (7, 15), (13, 20), (12, 21), (11, 22)):
            s.set(x, y + b, "white" if crack == 1 else "shadow")
    # arms / fists
    def fist(cx, cy, r=2.6):
        ell(s, cx, cy, r, r, mid, shader(cx, r, hi, mid, lo))
        s.set(int(cx), int(cy), lo)
    if side:
        if arms == "rest":
            sw = 1 if anim == "walk" and i % 2 else 0
            rect(s, 5, 15 + b, 7, 21 + b + sw, mid); rect(s, 5, 15 + b, 5, 21 + b, hi)
            fist(6, 24 + b + sw, 2.8)
        elif arms in ("up", "high"):
            fist(7, 4 + b if arms == "high" else 7 + b)
            rect(s, 8, 8 + b, 9, 13 + b, mid)
        elif arms == "slam":
            fist(4, 27, 2.8)
            rect(s, 5, 20 + b, 7, 24 + b, mid)
        else:
            rect(s, 5, 15 + b, 7, 18 + b, mid)
            fist(4, 20 + b)
    else:
        if arms == "rest":
            sw = 1 if anim == "walk" and i % 2 else 0
            fist(2, 19 + b + sw); fist(17, 19 + b - sw)
        elif arms in ("up", "high"):
            y = 3 + b if arms == "high" else 6 + b
            fist(5, y); fist(14, y)
            rect(s, 4, y + 2, 5, 12 + b, mid); rect(s, 14, y + 2, 15, 12 + b, lo)
        elif arms == "slam":
            fist(5, 27, 2.8); fist(14, 27, 2.8)
            rect(s, 4, 20 + b, 5, 25, mid); rect(s, 14, 20 + b, 15, 25, lo)
        else:
            fist(3, 15 + b); fist(16, 15 + b)
    if dust:
        for (x, y) in ((0, 29), (1, 27), (18, 28), (19, 29), (9, 30)):
            s.set(x, y, "plaster_lo")
        s.set(10, 29, "flower_gold")


# ------------------------------------------------------------------ blue cold-fire wraith
def wraith(s, face, anim, i):
    b = 0
    orb = 0
    hands = "low"
    fade = 0
    flick = i
    if anim == "idle":
        b = [0, 1, 1, 0][i]
    elif anim == "walk":
        b = [0, 1, 0, -1][i]
    elif anim == "attack":
        hands = "up"; orb = [1, 2, 3, 0][i]; b = [0, -1, -1, 0][i]
    elif anim == "die":
        fade = i + 1; b = [-1, -2, -3, 0][i]
    hi, mid, lo = "flower_blue", "cloth", "shadow"
    fire = ["white", "sky", "flower_blue"]
    if anim == "die" and i == 3:                       # a last cold-fire wisp guttering on the ground
        ell(s, 9.5, 27, 2.5, 3.5, "flower_blue")
        s.set(9, 26, "sky"); s.set(10, 27, "white"); s.set(9, 24, "sky"); s.set(10, 23, "flower_blue")
        rect(s, 9, 30, 10, 30, "sky")
        s.set(6, 20, "sky"); s.set(13, 18, "flower_blue"); s.set(11, 15, "white")
        return
    side = face == "left"
    hx = 8 if side else 9.5
    # tail: tapering cold-fire down to the ground
    for y in range(23 + b, 31):
        t = (y - (23 + b)) / max(1, 30 - (23 + b))
        w = max(0, int(round(3.5 * (1 - t))))
        cx = 9.5 + (0.5 if (y + flick) % 4 < 2 else -0.5) * t
        for x in range(int(cx - w), int(cx + w) + 1):
            s.set(x, y, fire[min(2, int(t * 3 + ((x + y + flick) % 2) * 0.6))] if t > 0.15 else mid)
    s.set(9, 30, "sky"); s.set(10, 30, "sky")
    # robe
    for y in range(12 + b, 24 + b):
        t = (y - 12 - b) / 12
        half = 3.5 + t * 3.2
        for x in range(int(hx + 0.5 - half), int(hx + 0.5 + half)):
            u = (x - (hx - half)) / (2 * half)
            c = hi if u < 0.22 else lo if u > 0.72 else mid
            if (x + y) % 5 == 0 and 0.3 < u < 0.7:
                c = lo
            s.set(x, y, c)
    # cold-fire hem (flickers)
    for x in range(3, 17):
        if s.p[23 + b][x] if 0 <= 23 + b < 32 else False:
            s.set(x, 23 + b, fire[(x + flick) % 3])
            if (x + flick) % 3 == 0:
                s.set(x, 24 + b, fire[(x + flick + 1) % 3])
    # hood
    ell(s, hx, 8 + b, 5, 5.2, mid, shader(hx, 5, hi, mid, lo))
    s.set(int(hx), 2 + b, mid); s.set(int(hx) + 1, 3 + b, mid)       # pointed tip
    eyes = "white" if fade < 2 else "sky"
    if face == "down":
        ell(s, 9.5, 9 + b, 3, 2.6, "ink")
        s.set(8, 9 + b, eyes); s.set(11, 9 + b, eyes); s.set(8, 10 + b, "sky"); s.set(11, 10 + b, "sky")
    elif face == "up":
        for y in range(5 + b, 12 + b):
            s.set(10, y, lo)
        s.set(9, 6 + b, hi)
    else:
        ell(s, 6, 9 + b, 2, 2.4, "ink")
        s.set(5, 9 + b, eyes); s.set(5, 10 + b, "sky")
    # sleeves + bony hands wreathed in cold fire
    def hand(x, y):
        s.set(x, y, "stone_hi"); s.set(x + 1, y, "stone_hi"); s.set(x, y + 1, "stone")
        s.set(x, y - 1, fire[(x + flick) % 3])
    if hands == "low":
        if side:
            rect(s, 6, 14 + b, 8, 18 + b, lo); hand(5, 19 + b)
        else:
            rect(s, 3, 14 + b, 4, 19 + b, hi); rect(s, 15, 14 + b, 16, 19 + b, lo)
            hand(2, 20 + b); hand(16, 20 + b)
    else:
        if side:
            rect(s, 4, 13 + b, 7, 14 + b, lo); hand(2, 13 + b)
            ox, oy = 1, 12 + b
        else:
            rect(s, 4, 13 + b, 5, 16 + b, hi); rect(s, 14, 13 + b, 15, 16 + b, lo)
            hand(6, 16 + b); hand(12, 16 + b)
            ox, oy = 9.5, 18 + b
        if orb:
            ell(s, ox, oy, orb * 0.9 + 0.2, orb * 0.9 + 0.2, "flower_blue")
            ell(s, ox, oy, orb * 0.5, orb * 0.5, "sky")
            s.set(int(ox), int(oy), "white")
        elif anim == "attack":
            for (dx, dy) in ((-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, 2)):
                s.set(int(ox) + dx, int(oy) + dy, "sky" if dx else "white")
    if fade:                                           # dissolving: holes punched through the robe, sparks rise
        for y in range(0, 30):
            for x in range(20):
                if s.p[y][x] and ((x * 7 + y * 3 + i) % (6 - fade)) == 0 and y < 29:
                    s.p[y][x] = None
        for (x, y) in ((4, 4), (15, 6), (12, 1), (6, 0)):
            s.set(x, y + fade, "sky" if x % 2 else "white")


# ------------------------------------------------------------------ skeleton swordsman
def skeleton(s, face, anim, i, mage=False):
    b = 0
    lift_l = lift_r = 0
    sword = "rest"
    slump = 0
    if anim == "idle":
        b = [0, 0, 1, 1][i]
    elif anim == "walk":
        b = [0, 1, 0, 1][i]
        lift_l, lift_r = [(0, 0), (2, 0), (0, 0), (0, 2)][i]
    elif anim == "attack":
        sword = ["back", "over", "slash", "follow"][i]
        b = [0, -1, 1, 1][i]
    elif anim == "die":
        slump = i + 1
    bone, bone_lo, bone_hi = "stone_hi", "stone", "plaster_hi"
    iron, iron_lo = ("roof", "roof_lo") if mage else ("stone_lo", "shadow")   # mage: a deep-red hooded robe
    eye = ("lamp" if mage else "sky") if slump < 3 else "flower_blue"
    if anim == "die" and i >= 2:                       # a heap of bones with the skull on top
        ell(s, 9.5, 28.5, 7, 2.5, bone_lo)
        for (x0, y0, x1) in ((3, 28, 9), (10, 27, 16), (5, 29, 14)):
            for x in range(x0, x1 + 1):
                s.set(x, y0, bone_hi if x % 3 else bone)
        rect(s, 12, 26, 15, 27, iron); s.set(13, 26, "flower_blue")
        sy = 21 if i == 2 else 23
        ell(s, 7.5, sy + 2, 3.5, 3, bone, shader(7.5, 3.5, bone_hi, bone, bone_lo))
        s.set(6, sy + 2, "ink"); s.set(8, sy + 2, "ink")
        if i == 2:
            s.set(6, sy + 2, eye)
        rect(s, 4, 30, 15, 30, bone_lo)
        if mage:                                       # the dropped staff, its orb gone dim, and a robe rag
            rect(s, 12, 25, 18, 25, "timber"); s.set(19, 25, "sky"); rect(s, 3, 29, 7, 29, "roof_lo")
        else:
            rect(s, 15, 25, 18, 25, "stone_hi"); s.set(19, 25, "white")   # the dropped sword
        return
    side = face == "left"
    b += 1 if slump == 1 else 3 if slump == 2 else 0
    # legs (bone shins, dark boots)
    lxs = (7, 11) if side else (6, 12)
    for lx, lift in zip(lxs, (lift_l, lift_r)):
        rect(s, lx, 24 + b, lx + 1, 28 - lift, bone)
        s.set(lx, 26 + b if 26 + b <= 28 - lift else 28 - lift, bone_lo)
        rect(s, lx - (1 if side else 0), 29 - lift, lx + 1, 30 - lift, iron_lo)
    # pelvis
    rect(s, 6, 22 + b, 13, 23 + b, bone_lo)
    if mage:                                           # long robe skirt over the shins, a gold-stitched hem
        for y in range(22 + b, 29):
            w = 3 + (y - 22 - b) // 3
            for x in range(int(9.5 - w), int(9.5 + w) + 1):
                s.set(x, y, iron if x < 10 else iron_lo)
        for x in range(5, 15, 2):
            s.set(x, 28, "flower_gold")
    # torso: dark breastplate with ribs peeking out at the sides, a blue rune etched
    tx0, tx1 = (6, 13) if not side else (7, 12)
    for y in range(15 + b, 22 + b):
        for x in range(tx0, tx1 + 1):
            s.set(x, y, iron if x < (tx0 + tx1) / 2 + 1 else iron_lo)
    if not side:
        for y in range(16 + b, 22 + b, 2):
            s.set(tx0 - 1, y, bone_hi); s.set(tx1 + 1, y, bone)
    if face == "down":
        s.set(9, 17 + b, "flower_blue"); s.set(10, 18 + b, "sky"); s.set(9, 19 + b, "flower_blue")
    elif face == "up":
        for y in range(15 + b, 22 + b):
            s.set(9, y, bone_lo)                      # spine
    else:
        s.set(8, 17 + b, "flower_blue")
    # skull under a dark rune helm
    hcx = 8.5 if side else 9.5
    ell(s, hcx, 9 + b, 5.5, 5, bone, shader(hcx, 5.5, bone_hi, bone, bone_lo))
    for x in range(int(hcx - 5), int(hcx + 6)):
        for y in range(3 + b, 7 + b):
            if s.p[y][x] if 0 <= y < 32 and 0 <= x < 20 else False:
                s.set(x, y, iron if x < hcx else iron_lo)
    s.set(int(hcx), 4 + b, "flower_blue")
    if face == "down":
        for ex in (7, 11):
            rect(s, ex, 9 + b, ex + 1, 10 + b, "ink"); s.set(ex, 9 + b, eye)
        s.set(9, 11 + b, "ink"); s.set(10, 11 + b, "ink")
        for x in range(7, 13):
            s.set(x, 13 + b, "ink" if x % 2 else bone_hi)
    elif face == "up":
        s.set(9, 12 + b, bone_lo); s.set(10, 12 + b, bone_lo)
    else:
        rect(s, 5, 9 + b, 6, 10 + b, "ink"); s.set(5, 9 + b, eye)
        s.set(4, 12 + b, "ink"); s.set(5, 13 + b, bone_hi); s.set(6, 13 + b, "ink")
    # arms + notched sword (always in the near / right hand on screen)
    def blade(x0, y0, x1, y1):
        n = max(abs(x1 - x0), abs(y1 - y0))
        if mage:                                       # a crooked staff with a glowing cold-fire orb
            for k in range(n + 1):
                x = round(x0 + (x1 - x0) * k / max(1, n)); y = round(y0 + (y1 - y0) * k / max(1, n))
                s.set(x, y, "timber_hi" if k % 3 else "timber")
            ell(s, x1, y1, 1.3, 1.3, "flower_blue"); s.set(x1, y1, "white"); s.set(x1 - 1, y1 - 1, "sky")
            return
        for k in range(n + 1):
            x = round(x0 + (x1 - x0) * k / max(1, n)); y = round(y0 + (y1 - y0) * k / max(1, n))
            s.set(x, y, "white" if k == n else "stone_hi" if k % 3 else "plaster_hi")
        s.set(x0, y0, "timber")
    if side:
        if sword == "rest":
            rect(s, 8, 16 + b, 9, 20 + b, bone); blade(7, 21 + b, 2, 26 + b)
        elif sword == "back":
            rect(s, 11, 15 + b, 12, 18 + b, bone); blade(13, 16 + b, 18, 10 + b)
        elif sword == "over":
            rect(s, 8, 12 + b, 9, 15 + b, bone); blade(8, 11 + b, 8, 3 + b)
        elif sword == "slash":
            rect(s, 5, 16 + b, 7, 17 + b, bone); blade(4, 17 + b, 0, 23 + b)
            for (x, y) in ((1, 9), (0, 12), (0, 15), (2, 7)):
                s.set(x, y + b, "sky")
        else:
            rect(s, 6, 18 + b, 7, 20 + b, bone); blade(5, 21 + b, 1, 28)
    else:
        rect(s, 4, 15 + b, 5, 20 + b, bone)            # off arm
        if sword == "rest":
            rect(s, 14, 15 + b, 15, 20 + b, bone); blade(15, 21 + b, 18, 27 + b)
        elif sword == "back":
            rect(s, 14, 13 + b, 15, 16 + b, bone); blade(16, 13 + b, 19, 7 + b)
        elif sword == "over":
            rect(s, 13, 10 + b, 14, 14 + b, bone); blade(13, 9 + b, 10, 1 + b)
        elif sword == "slash":
            rect(s, 12, 18 + b, 14, 19 + b, bone); blade(11, 20 + b, 4, 27)
            for (x, y) in ((17, 6), (18, 10), (18, 14), (16, 3)):
                s.set(x, y + b, "sky")
        else:
            rect(s, 13, 19 + b, 14, 21 + b, bone); blade(12, 22 + b, 7, 28)


# ------------------------------------------------------------------ summons (tiny)
def _eyes(s, face, y, x0=8, x1=11, col="ink"):
    if face == "down":
        s.set(x0, y, col); s.set(x1, y, col)
    elif face == "left":
        s.set(x0 - 2, y, col)


def mushgolem(s, face, anim, i):
    b = [0, 1, 1, 0][i] if anim == "idle" else [0, -1, 0, -1][i] if anim == "walk" else [1, -1, 2, 0][i]
    lean = -2 if anim == "attack" and i == 2 and face == "left" else 0
    stl, str_ = (2, 0) if anim == "walk" and i == 1 else (0, 2) if anim == "walk" and i == 3 else (0, 0)
    rect(s, 7, 28, 8, 30 - stl, "timber"); rect(s, 11, 28, 12, 30 - str_, "timber_lo")
    rect(s, 6, 22 + b, 13, 28, "plaster")
    for y in range(22 + b, 29):
        s.set(6, y, "plaster_hi"); s.set(13, y, "plaster_lo")
    rect(s, 4, 24 + b, 5, 25 + b, "plaster_lo"); rect(s, 14, 24 + b, 15, 25 + b, "plaster_lo")
    ell(s, 9.5 + lean, 19 + b, 6.5, 3.8, "roof", shader(9.5, 6.5, "roof_hi", "roof", "roof_lo"))
    for (x, y) in ((6, 18), (9, 17), (12, 19), (8, 20), (11, 17)):
        s.set(x + lean, y + b, "plaster_hi" if face != "up" or x % 2 else "flower_rose")
    _eyes(s, face, 24 + b)
    if face == "down":
        s.set(9, 26 + b, "skin_lo"); s.set(10, 26 + b, "skin_lo")
    if anim == "attack" and i in (2, 3):
        for (x, y) in ((2, 20), (1, 23), (17, 21), (3, 17), (16, 18)):
            s.set(x, y + (i - 2), "grass_hi" if x % 2 else "flower_gold")


def runesentinel(s, face, anim, i):
    b = [0, -1, -1, 0][i] if anim != "walk" else [0, -1, -2, -1][i]
    for y in range(24 + b, 31):                        # pillar of light to the ground
        s.set(9, y, "flower_gold" if (y + i) % 3 else "lamp"); s.set(10, y, "lamp" if (y + i) % 3 else "white")
    for y in range(12 + b, 25 + b):                    # shield-shaped rune stone
        t = (y - 12 - b) / 12
        half = 5 if t < 0.6 else 5 - (t - 0.6) * 10
        for x in range(int(9.5 - half), int(9.5 + half) + 1):
            u = (x - (9.5 - half)) / max(1, 2 * half)
            s.set(x, y, "stone_hi" if u < 0.3 else "stone_lo" if u > 0.72 else "stone")
    flare = anim == "attack" and i in (1, 2)
    if face != "up":
        g = "white" if flare else "lamp"
        cx = 9 if face == "down" else 7
        for y in range(15 + b, 22 + b):
            s.set(cx, y, g if y % 2 else "flower_gold")
        s.set(cx - 1, 16 + b, "flower_gold"); s.set(cx + 1, 16 + b, "flower_gold")
        s.set(cx - 1, 19 + b, g); s.set(cx + 1, 19 + b, g)
    else:
        s.set(9, 17 + b, "stone_lo"); s.set(10, 19 + b, "moss")
    if flare:
        for (x, y) in ((2, 14), (17, 14), (9, 8), (3, 21), (16, 21), (10, 7)):
            s.set(x, y + b, "white" if i == 2 else "flower_gold")
    if anim == "attack" and i == 3:
        s.set(4, 11 + b, "flower_gold"); s.set(15, 11 + b, "flower_gold")


def runewisp(s, face, anim, i):
    b = [0, -1, -1, 0][i] if anim == "idle" else [0, -1, 0, 1][i] if anim == "walk" else [0, -2, -2, 0][i]
    for y in range(20 + b, 31):
        t = (y - 20 - b) / max(1, 10 - b)
        w = 2.6 * (1 - t)
        for x in range(int(9.5 - w), int(9.5 + w) + 1):
            s.set(x, y, "sky" if t < 0.5 else "flower_blue")
    s.set(9, 30, "flower_blue"); s.set(10, 30, "flower_blue")
    ell(s, 9.5, 17 + b, 4.2, 4.2, "flower_blue")
    ell(s, 9.0, 16.5 + b, 2.6, 2.6, "sky")
    s.set(8, 16 + b, "white"); s.set(9, 15 + b, "white")
    _eyes(s, face, 17 + b, 8, 11, "cloth")
    a = (i + (2 if anim == "attack" else 0)) * math.pi / 2
    r = 7 if anim != "attack" else [7, 5, 3, 8][i]
    gx, gy = 9.5 + math.cos(a) * r, 17 + b + math.sin(a) * r * 0.6
    for (dx, dy) in ((0, 0), (0, -1), (0, 1), (-1, 0)):
        s.set(int(gx) + dx, int(gy) + dy, "white" if (dx, dy) == (0, 0) else "sky")
    if anim == "attack" and i == 3:
        for (x, y) in ((2, 12), (17, 12), (1, 18), (18, 18)):
            s.set(x, y + b, "white")


def stormsprite(s, face, anim, i):
    b = [0, 0, -1, -1][i] if anim == "idle" else [0, -1, 0, -1][i] if anim == "walk" else [0, -1, -2, 0][i]
    bolt = "white" if (anim == "attack" and i == 2) else "flower_gold"
    for leg, ph in ((7, 0), (12, 1)):                  # zig-zag lightning legs
        for k, y in enumerate(range(21 + b, 31)):
            x = leg + ((k + ph + i) % 3 - 1 if anim == "walk" else (k + ph) % 2)
            s.set(x, y, bolt if k % 3 else "white")
    for (cx, cy, r) in ((6, 17, 3.6), (10, 15, 4.4), (14, 17, 3.6), (10, 19, 4.2)):
        ell(s, cx, cy + b, r, r * 0.85, "stone_hi", shader(10, 7, "plaster_hi", "stone_hi", "sky"))
    rect(s, 5, 20 + b, 15, 21 + b, "stone")
    _eyes(s, face, 17 + b, 8, 12, "cloth")
    if face == "down":
        s.set(10, 19 + b, "cloth")
    if anim == "attack":
        pts = [(), ((2, 12), (3, 10)), ((1, 10), (2, 8), (3, 6), (17, 9), (18, 7)), ((16, 11),)][i]
        for (x, y) in pts:
            s.set(x, y + b, "white" if y % 2 else "flower_gold")


def sapling(s, face, anim, i):
    b = [0, 0, 1, 1][i] if anim == "idle" else [0, -1, 0, -1][i] if anim == "walk" else [0, -1, 1, 0][i]
    stl, str_ = (2, 0) if anim == "walk" and i == 1 else (0, 2) if anim == "walk" and i == 3 else (0, 0)
    rect(s, 6, 29 - stl, 8, 30 - stl, "timber_lo"); rect(s, 11, 29 - str_, 13, 30 - str_, "timber_lo")
    rect(s, 7, 20 + b, 12, 28, "timber")
    for y in range(20 + b, 29):
        s.set(7, y, "timber_hi"); s.set(12, y, "timber_lo")
    ell(s, 9.5, 15 + b, 6.4, 5.2, "grass", shader(9.5, 6.4, "grass_hi", "grass", "moss"))
    for (x, y) in ((5, 12), (13, 13), (9, 10), (7, 17), (12, 17)):
        s.set(x, y + b, "leaf_deep")
    s.set(10, 11 + b, "flower_rose"); s.set(6, 15 + b, "flower_gold")
    if face == "down":
        s.set(8, 23 + b, "grass_hi"); s.set(11, 23 + b, "grass_hi")
    elif face == "left":
        s.set(8, 23 + b, "grass_hi")
    if anim == "attack":                               # a vine whip
        vx = [(13, 22), (15, 19), (17, 16), (16, 24)][i] if face != "left" else [(6, 22), (4, 19), (2, 16), (3, 24)][i]
        x0 = 12 if face != "left" else 7
        n = max(1, abs(vx[0] - x0))
        for k in range(n + 1):
            x = x0 + (vx[0] - x0) * k // n; y = 23 + b + (vx[1] - 23 - b) * k // n
            s.set(x, y, "moss" if k % 2 else "grass")
        s.set(vx[0], vx[1], "grass_hi")


def emberimp(s, face, anim, i):
    b = [0, -1, 0, -1][i] if anim != "attack" else [0, -1, -1, 0][i]
    stl, str_ = (2, 0) if anim == "walk" and i == 1 else (0, 2) if anim == "walk" and i == 3 else (0, 0)
    rect(s, 7, 27, 8, 30 - stl, "roof"); rect(s, 11, 27, 12, 30 - str_, "roof_lo")
    for y in range(13 + b, 28):                        # teardrop flame body
        t = (y - 13 - b) / (14 - b)
        half = 1 + 4.6 * math.sin(min(1.0, t * 1.15) * math.pi * 0.62)
        wob = ((y + i) % 4 - 1.5) * 0.25 * (1 - t)
        for x in range(int(9.5 + wob - half), int(9.5 + wob + half) + 1):
            u = abs(x - 9.5) / max(1, half)
            s.set(x, y, "white" if u < 0.22 and t > 0.45 else "flower_gold" if u < 0.45 else "lamp" if u < 0.75 else "roof_hi")
    s.set(9 + (i % 2), 12 + b, "lamp"); s.set(10, 11 + b, "roof_hi")
    _eyes(s, face, 20 + b, 8, 11, "ink")
    if anim == "attack" and i in (1, 2):
        cx = 16 if face != "left" else 3
        ell(s, cx, 18 + b, 1.6 + (i == 2), 1.6 + (i == 2), "lamp")
        s.set(cx, 18 + b, "white")


# ------------------------------------------------------------------ palette-swapped variants (stage 3)
class _Remap:
    """wraps a sprite grid and swaps colour names on the way in (same drawing, new material)"""
    def __init__(self, s, m):
        self.s, self.m = s, m

    @property
    def p(self):
        return self.s.p

    def set(self, x, y, col):
        self.s.set(x, y, self.m.get(col, col) if col else col)


def _golem_b(anim, i):
    return {"idle": [0, 0, 1, 1], "walk": [0, 1, 0, 1], "attack": [0, -1, 2, 1], "die": [1, 3, 0, 0]}.get(anim, [0, 0, 0, 0])[i]


ICE = {"stone_hi": "white", "stone": "sky", "stone_lo": "flower_blue", "moss": "white", "grass": "plaster_hi",
       "lamp": "white", "flower_gold": "sky", "plaster_lo": "plaster_hi"}


def icegolem(s, face, anim, i):
    """frost golem: the stone golem re-cut in pale ice, snow on the shoulders, ice spikes, white rune light"""
    golem(_Remap(s, ICE), face, anim, i)
    if anim == "die" and i >= 2:
        s.set(5, 25, "white"); s.set(14, 26, "white")
        return
    b = _golem_b(anim, i)
    if face == "left":
        spikes = ((11, 6), (13, 6), (15, 8))
    else:
        spikes = ((4, 10), (6, 8), (13, 8), (15, 10)) if face == "down" else ((5, 9), (14, 9), (9, 5))
    for (x, y) in spikes:                              # jagged ice crystals poking out of the shoulders
        s.set(x, y + b - 1, "white"); s.set(x, y + b - 2, "sky"); s.set(x, y + b, "flower_blue")
    if face == "down":
        s.set(9, 5 + b, "white"); s.set(10, 4 + b, "sky")


ELDER = {"stone_hi": "stone", "stone": "stone_lo", "stone_lo": "shadow", "moss": "grass_hi", "grass": "moss",
         "plaster_lo": "flower_gold"}


def eldergolem(s, face, anim, i):
    """Mossheart, the elder golem (Mossglen mini-boss): dark ancient stone, a crown of amber crystals, glowing
    gold runes across the whole body, glow-flowers in the moss (the tier-III 'glowing variant' look)"""
    golem(_Remap(s, ELDER), face, anim, i)
    if anim == "die" and i >= 2:
        s.set(5, 26, "lamp"); s.set(12, 25, "flower_gold"); s.set(15, 28, "white")
        return
    b = _golem_b(anim, i)
    lit = not (anim == "die" and i >= 1)
    rune, hot = ("lamp", "white") if lit else ("flower_gold", "flower_gold")
    side = face == "left"
    crown = ((4, 7), (6, 6), (8, 7)) if side else ((7, 5), (9, 4), (10, 4), (12, 5))
    for (x, y) in crown:                               # a crown of amber crystals
        s.set(x, y + b, rune); s.set(x, y + b - 1, "flower_gold"); s.set(x, y + b - 2, hot if (x + i) % 3 == 0 else "flower_gold")
    if face == "down":                                 # rune lines on the flanks and legs, a third eye of light
        for (x, y) in ((5, 16), (5, 18), (14, 17), (14, 19), (6, 21), (13, 21), (5, 27), (14, 27)):
            s.set(x, y + b if y < 25 else y, rune if (x + y + i) % 3 else hot)
        s.set(9, 7 + b, hot); s.set(10, 7 + b, hot)
    elif face == "up":
        for (x, y) in ((6, 13), (9, 12), (10, 12), (13, 13), (7, 19), (12, 19), (9, 22), (10, 22)):
            s.set(x, y + b, rune if (x + i) % 2 else hot)
    else:
        for (x, y) in ((12, 15), (13, 17), (12, 19), (14, 21), (8, 27), (13, 27)):
            s.set(x, y + b if y < 25 else y, rune if (x + y + i) % 3 else hot)
    for (x, y) in (((11, 7), (14, 7)) if side else ((6, 6), (12, 6), (3, 12), (16, 12))):
        s.set(x, y + b, "flower_rose" if (x + i) % 2 else "flower_gold")   # glow-flowers in the moss


def skelmage(s, face, anim, i):
    """skeleton mage (caster line T1): skull under a red hood, long robe, a crooked staff with a cold-fire orb"""
    skeleton(s, face, anim, i, mage=True)


DRAW = {"golem": golem, "icegolem": icegolem, "eldergolem": eldergolem, "skelmage": skelmage, "wraith": wraith, "skeleton": skeleton, "mushgolem": mushgolem, "runesentinel": runesentinel,
        "runewisp": runewisp, "stormsprite": stormsprite, "sapling": sapling, "emberimp": emberimp}

SUMMON_OF = {"wildcaller": "mushgolem", "runeguard": "runesentinel", "seer": "runewisp", "stormborn": "stormsprite",
             "grovekeeper": "sapling", "cinderknight": "emberimp"}


def enemy_roles(_r):
    E = dict(kind="enemy", enemy=True, anims=ENEMY_ANIMS)
    S = dict(kind="summon", summon=True, anims=SUMMON_ANIMS)
    return {
        "golem": _r(**E, draw="golem", desc="stone golem: mossy boulder body, amber rune seam and eyes, two-fist slam"),
        "wraith": _r(**E, draw="wraith", desc="blue cold-fire wraith: hooded spectre with a cold-fire hem and tail, casts a cold-fire orb"),
        "skeleton": _r(**E, draw="skeleton", desc="skeleton swordsman: big skull under a dark rune helm, dark breastplate, notched sword"),
        "icegolem": _r(**E, draw="icegolem", desc="frost golem: the stone golem in pale ice, snowy shoulders, ice spikes, white rune light"),
        "skelmage": _r(**E, draw="skelmage", desc="skeleton mage: skull under a red hood, long gold-hemmed robe, crooked staff with a cold-fire orb"),
        "eldergolem": _r(**E, draw="eldergolem", desc="Mossheart the elder golem (mini-boss): dark ancient stone, amber crystal crown, glowing gold runes, glow-flowers"),
        "mushgolem": _r(**S, draw="mushgolem", desc="summon (Wildcaller): a little mushroom golem"),
        "runesentinel": _r(**S, draw="runesentinel", desc="summon (Runeguard): a floating rune stone on a pillar of light"),
        "runewisp": _r(**S, draw="runewisp", desc="summon (Seer): a blue rune-wisp with an orbiting glyph"),
        "stormsprite": _r(**S, draw="stormsprite", desc="summon (Stormborn): a storm-cloud sprite walking on lightning"),
        "sapling": _r(**S, draw="sapling", desc="summon (Grovekeeper): a treant sapling with a vine whip"),
        "emberimp": _r(**S, draw="emberimp", desc="summon (Cinderknight): a small fire elemental"),
    }
