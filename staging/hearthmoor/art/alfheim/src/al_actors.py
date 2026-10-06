"""Alfheim / Lumenvale actors (Hearthmoor Art seat, 2026-10-05): elf NPC hooks (pointy ears, wisp lantern, circlet) and
the two Prism Vault enemies (prism shard, mirror duelist). 20x32 frames, biome palette only (NO neon on sprites: glow is
added by gamefx billboards / lights). Elves wear normal clothes: separate top + bottom, a dark belt, contrasting shoes."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_lib"))
from hmart import ell, rect, shader  # noqa: E402


# ------------------------------------------------------------------ elf hooks
def ears(s, L, face, bob, col="skin", tip="skin_lo"):
    """long pointy elf ears: out and up from the sides of the head (front / back), one swept-back ear in profile"""
    ht = L["head_top"] + bob
    x0 = (20 - L["head_w"]) // 2
    x1 = x0 + L["head_w"] - 1
    ey = ht + 6
    if face in ("down", "up"):
        c = col if face == "down" else tip
        for sd, xe in ((-1, x0), (1, x1)):
            s.set(xe + sd, ey, c); s.set(xe + sd, ey - 1, c)
            s.set(xe + 2 * sd, ey - 2, c)
            s.set(xe + 2 * sd, ey - 3, tip)
    else:  # left-facing profile: ear sits behind the cheek, swept back and up past the hair
        bx = x0 + 7
        s.set(bx, ey, col); s.set(bx, ey - 1, col); s.set(bx + 1, ey - 1, tip)
        s.set(bx + 1, ey - 2, col); s.set(bx + 2, ey - 3, col); s.set(bx + 3, ey - 4, tip)


def circlet(s, L, face, bob, c="flower_gold", gem="sky"):
    ht = L["head_top"] + bob
    x0 = (20 - L["head_w"]) // 2
    y = ht + 3
    if face == "down":
        for x in range(x0 + 1, x0 + L["head_w"] - 1):
            s.set(x, y, c)
        s.set(9, y, gem); s.set(10, y, gem); s.set(9, y - 1, "white")
    elif face == "left":
        for x in range(x0, x0 + 9):
            s.set(x, y, c)
        s.set(x0 + 1, y, gem)
    else:
        for x in range(x0 + 1, x0 + L["head_w"] - 1):
            s.set(x, y, c)


def wisp_lantern(s, L, face, bob, anim, i):
    """a small brass cage lantern on a short pole with a captured wisp (white / sky / flower_blue palette pixels; the
    neon glow comes from the attached gamefx `wisp_lantern_glow`)"""
    if face == "up":
        return
    top = L["torso_top"] + bob
    sw = [0, 1, 0, -1][i] if anim == "walk" else 0
    hx = 3 if face == "down" else 5
    hy = top + 6
    for y in range(hy - 6, hy + 1):                          # the pole in the hand
        s.set(hx, y, "timber")
    ly = hy - 7 + sw
    s.set(hx, ly, "flower_gold")
    lx = hx - 1 if face == "left" else hx
    rect(s, lx - 1, ly + 1, lx + 1, ly + 1, "timber_hi")
    s.set(lx - 1, ly + 2, "flower_gold"); s.set(lx, ly + 2, "white"); s.set(lx + 1, ly + 2, "flower_gold")
    s.set(lx - 1, ly + 3, "flower_gold"); s.set(lx, ly + 3, "sky" if i % 2 else "white"); s.set(lx + 1, ly + 3, "flower_gold")
    rect(s, lx - 1, ly + 4, lx + 1, ly + 4, "timber_hi")


def elf_extra(lantern=False, crown=None, sash=None):
    def hook(s, sp, L, face, bob, anim, i):
        ears(s, L, face, bob)
        if crown:
            circlet(s, L, face, bob, *crown)
        if sash and face in ("down", "left"):               # a pale shoulder sash over the top (still above the belt)
            top = L["torso_top"] + bob
            for k in range(6):
                x = (6 + k) if face == "down" else (8 + (k % 2))
                s.set(x, top + 1 + k, sash)
        if lantern:
            wisp_lantern(s, L, face, bob, anim, i)
    return hook


# ------------------------------------------------------------------ prism shard (floating crystal)
def _facet(x, y, cx, cy, side_lit):
    u = (x - cx)
    v = (y - cy)
    if u < -1.5:
        return "white" if v < 0 else "sky"
    if u < 0.5:
        return "sky" if v < 1 else "flower_blue"
    if u < 2:
        return "flower_blue" if v < 2 else "cloth"
    return "cloth"


def prismshard(s, face, anim, i):
    """prism shard (Prism Vault): a floating diamond crystal (white / sky / flower_blue / cloth facets, a rose refraction
    seam and a gold glint), two ink slit eyes with white catchlights, two orbiting splinters; a sparkle trail drops to the
    ground row so it stays anchored. attack = it rears back then flings its splinters forward (frame 14). die = cracks,
    splits, and falls into a little pile of glinting shards."""
    b = [0, -1, -1, 0][i] if anim in ("idle", "walk") else [0, -2, 0, 0][i] if anim == "attack" else 0
    side = face == "left"
    cx, cy = 9.5, 14 + b
    if anim == "die" and i >= 2:
        pile = ((6, 29, "sky"), (7, 29, "white"), (8, 30, "flower_blue"), (9, 29, "sky"), (10, 30, "cloth"), (11, 29, "white"),
                (12, 30, "flower_blue"), (13, 29, "sky"), (9, 28, "flower_rose"), (10, 28, "white"), (8, 28, "sky"), (11, 28, "flower_blue"))
        if i == 2:
            for (x, y, c) in pile[:8]:
                s.set(x, y - 2, c)
            for (dx, c) in ((-3, "sky"), (3, "flower_blue")):
                for k in range(4):
                    s.set(int(9.5 + dx + (k % 2)), 22 + k, c if k else "white")
            s.set(9, 30, "sky"); s.set(10, 30, "flower_blue")
        else:
            for (x, y, c) in pile:
                s.set(x, y, c)
            s.set(9, 27, "flower_gold")
        return
    tilt = 1 if anim == "attack" and i == 1 else -1 if anim == "attack" and i == 2 else 0
    split = 1 if anim == "die" and i == 1 else 0
    hh, hw = 8.5, 4.6
    for y in range(int(cy - hh), int(cy + hh) + 1):
        t = max(0.0, 1 - abs(y - cy) / hh)
        w = hw * t ** 0.9
        sh = tilt * (cy - y) / hh
        for x in range(int(cx - w - 1), int(cx + w + 2)):
            if abs(x - cx - sh) > w:
                continue
            xx = x + (-split if x < cx else split)
            c = _facet(x - sh, y, cx, cy, True)
            if abs(x - sh - cx - (y - cy) * 0.35) < 0.5 and abs(y - cy) < 6:
                c = "plaster_hi" if y < cy else "white"
            s.set(xx, y, c)
    if split == 0 and anim != "die":
        s.set(int(cx - 2), int(cy - 4), "white"); s.set(int(cx - 2), int(cy - 5), "flower_gold")
    if anim == "die" and i == 0:
        for k in range(6):
            s.set(int(cx - 2 + k * 0.7), int(cy - 3 + k), "white")
    if face == "down" and anim != "die":
        for ex in (7, 11):
            s.set(ex, int(cy), "ink"); s.set(ex + (1 if ex == 7 else -1), int(cy), "ink"); s.set(ex, int(cy) - 1, "white")
    elif side and anim != "die":
        s.set(6, int(cy), "ink"); s.set(7, int(cy), "ink"); s.set(6, int(cy) - 1, "white")
    # orbiting splinters
    if anim != "die":
        for k in range(2):
            a = (i / 4 + k / 2) * math.tau
            r = 7.5
            if anim == "attack" and i == 2:
                ox, oy = (cx - 9 + k, cy + 1 - k * 3) if side else (cx + (-5 if k else 5), cy + 9)
            elif anim == "attack" and i == 1:
                ox, oy = cx + (5 if not side else 6) * (1 if k else -1) * 0.6, cy - 6
            else:
                ox, oy = cx + math.cos(a) * r, cy + math.sin(a) * 2.5 + 1
                if side:
                    ox = cx + math.cos(a) * 5.5
            ox, oy = int(round(ox)), int(round(oy))
            s.set(ox, oy - 1, "white"); s.set(ox, oy, "sky"); s.set(ox, oy + 1, "flower_blue")
    # sparkle trail to the ground row (row 30)
    for y in range(int(cy + hh) + 1, 31):
        if (y + i) % 2 == 0 or y >= 29:
            s.set(9 + ((y + i) // 2) % 2, y, "sky" if y % 3 else "white")
    s.set(9, 30, "flower_blue"); s.set(10, 30, "sky")


# ------------------------------------------------------------------ mirror duelist
def mirrorduelist(s, face, anim, i):
    """mirror duelist (Prism Vault): an enchanted duellist whose face is an oval hand-mirror under a plumed hat, in
    normal clothes - a deep blue frock coat (top) over a white cravat, a dark belt with a gold buckle, pale trousers,
    black boots, white gloves and a silver rapier. attack = en garde, lunge, thrust (hit on 14), recover. die = the mirror
    cracks, it kneels and collapses into a heap of coat, hat and glinting mirror shards."""
    side = face == "left"
    up = face == "up"
    walk = anim == "walk"
    b = [0, 0, -1, 0][i] if anim == "idle" else [0, -1, 0, -1][i] if walk else 0
    lunge = (anim == "attack") and i == 2
    if anim == "die" and i == 3:
        ell(s, 10, 28.5, 6.5, 2.0, "cloth", shader(10, 6.5, "flower_blue", "cloth", "shadow"))
        rect(s, 6, 30, 14, 30, "shadow")
        for (x, y, c) in ((5, 29, "sky"), (15, 30, "white"), (13, 29, "sky"), (7, 30, "white"), (11, 30, "plaster_hi")):
            s.set(x, y, c)
        ell(s, 9, 26, 3.6, 1.2, "shadow"); rect(s, 8, 24, 10, 25, "shadow"); s.set(11, 24, "flower_rose"); s.set(12, 23, "flower_rose")
        rect(s, 3, 30, 4, 30, "stone_hi")
        return
    kneel = 3 if anim == "die" and i == 2 else 1 if anim == "die" and i == 1 else 0
    dx = (-2 if side else 0) if lunge else 0
    dy = 1 if lunge and not side else 0
    top = 15 + b + kneel + dy
    # legs + boots
    if kneel >= 3:
        rect(s, 6, 27, 13, 29, "plaster_lo"); rect(s, 5, 30, 8, 30, "shadow"); rect(s, 12, 30, 15, 30, "shadow")
    else:
        stride = [0, 2, 0, -2][i] if walk else (3 if lunge else 0)
        if side:
            for (lx, off) in ((8 + dx, -stride), (10 + dx, stride)):
                x0 = lx + off // 2
                rect(s, x0, 24 + b + dy, x0 + 1, 27, "plaster_lo")
                rect(s, x0, 28, x0 + 1, 30, "shadow"); s.set(x0 - 1, 30, "shadow")
        else:
            lift = [0, 1, 0, 0][i] if walk else 0
            rl = [0, 0, 0, 1][i] if walk else 0
            rect(s, 7, 24 + b, 8, 27 - lift, "plaster_lo"); rect(s, 7, 28 - lift, 8, 30 - lift, "shadow")
            rect(s, 11, 24 + b, 12, 27 - rl, "plaster_lo"); rect(s, 11, 28 - rl, 12, 30 - rl, "shadow")
            if lunge:
                rect(s, 6, 29, 8, 30, "shadow")
            s.set(7, 24 + b, "stone"); s.set(12, 24 + b, "stone")
    # frock coat (top) with tails, a dark belt
    cw = 4 if not side else 3
    ccx = 9.5 + dx
    for y in range(top, top + 9):
        w = cw + (1 if y > top + 6 else 0)
        for x in range(int(ccx - w), int(ccx + w) + 1):
            u = (x - (ccx - w)) / (2 * w)
            s.set(x, y, "flower_blue" if u < 0.25 else "shadow" if u > 0.8 else "cloth")
    if side:
        rect(s, int(ccx) + 2, top + 7, int(ccx) + 4, top + 10, "cloth"); s.set(int(ccx) + 4, top + 10, "shadow")
    else:
        rect(s, int(ccx - cw), top + 9, int(ccx - cw) + 1, top + 10, "cloth")
        rect(s, int(ccx + cw) - 1, top + 9, int(ccx + cw), top + 10, "shadow")
    by = top + 6
    for x in range(int(ccx - cw), int(ccx + cw) + 1):
        s.set(x, by, "ink" if (x + by) % 5 == 0 else "timber_lo")
    if not up:
        s.set(int(ccx) - (1 if side else 0), by, "flower_gold")
        if not side:                                         # white cravat + gold buttons
            rect(s, 9, top, 10, top + 2, "plaster_hi"); s.set(9, top + 3, "white")
            s.set(9, top + 4, "flower_gold")
        else:
            s.set(int(ccx) - 3, top, "plaster_hi"); s.set(int(ccx) - 3, top + 1, "plaster_hi")
    # arms: gloved hands; the rapier
    if side:
        if anim == "attack":
            reach = [0, -1, 5, 1][i]
            hx, hy = int(ccx) - 3 - reach // 2, top + 4 - (1 if i == 1 else 0)
            rect(s, hx, hy - 1, int(ccx) - 1, hy - 1, "cloth")
        else:
            hx, hy = int(ccx) - 2, top + 6 + ([0, 1, 0, -1][i] if walk else 0)
            rect(s, hx, top + 2, hx, hy - 1, "cloth")
        s.set(hx, hy, "plaster_hi")
        s.set(hx, hy - 1, "flower_gold")
        L = 8 if lunge else 6
        if anim == "attack" and i in (1, 2):
            for k in range(1, L):
                s.set(hx - k, hy - 1, "stone_hi" if k < L - 1 else "white")
        else:
            for k in range(1, 6):
                s.set(hx - k // 2, hy + k, "stone_hi" if k < 5 else "white")
    else:
        sw = [0, 1, 0, -1][i] if walk else 0
        rect(s, int(ccx - cw) - 1, top + 1, int(ccx - cw) - 1, top + 5 + sw, "cloth"); s.set(int(ccx - cw) - 1, top + 6 + sw, "plaster_hi")
        rx = int(ccx + cw) + 1
        if anim == "attack" and not up:
            ry = top + [5, 3, 7, 5][i]
            rect(s, rx, top + 1, rx, ry - 1, "shadow"); s.set(rx, ry, "plaster_hi"); s.set(rx, ry - 1, "flower_gold")
            L = [5, 4, 7, 5][i]
            for k in range(1, L):
                s.set(rx + (k + 1) // 3, ry + k, "stone_hi" if k < L - 1 else "white")
        else:
            ry = top + 6 - sw
            rect(s, rx, top + 1, rx, ry - 1, "shadow"); s.set(rx, ry, "plaster_hi")
            if not up:
                s.set(rx, ry - 1, "flower_gold")
                for k in range(1, 6):
                    s.set(rx + 1, ry + k, "stone_hi" if k < 5 else "white")
            else:
                L = [4, 3, 6, 4][i] if anim == "attack" else 4
                ry2 = ry - ([0, 1, -1, 0][i] if anim == "attack" else 0)
                for k in range(1, L + 1):
                    s.set(rx + (k // 3 if anim == "attack" and i == 2 else 0), ry2 - k - 1, "stone_hi" if k < L else "white")
    # head: an oval hand-mirror face under a plumed hat
    hy = top - 9
    hcx = 9.5 + dx - (0.5 if side else 0)
    if up:
        ell(s, hcx, hy + 4.5, 3.6, 4.2, "stone", shader(hcx, 3.6, "stone_hi", "stone", "stone_lo"))
    else:
        ell(s, hcx, hy + 4.5, 3.6, 4.2, "stone_hi")
        crack = anim == "die"
        rx_ = 2.6 if not side else 2.0
        for y in range(hy + 2, hy + 8):
            for x in range(int(hcx - 3), int(hcx + 4)):
                if ((x - hcx + (0.6 if side else 0)) / rx_) ** 2 + ((y - hy - 4.8) / 3.2) ** 2 <= 1:
                    d = (x - hcx) + (y - hy - 4.5)
                    s.set(x, y, "white" if abs(d + 1) < 0.7 else "sky" if d < 1 else "flower_blue")
        if crack:
            for k in range(4):
                s.set(int(hcx) - 1 + (k % 2), hy + 3 + k, "ink")
    # hat brim + crown + rose plume
    rect(s, int(hcx - 4), hy + 1, int(hcx + 4), hy + 1, "shadow")
    rect(s, int(hcx - 2), hy - 1, int(hcx + 2), hy, "shadow"); s.set(int(hcx - 2), hy, "timber_lo")
    rect(s, int(hcx - 2), hy, int(hcx + 2), hy, "flower_gold") if not up else None
    px_ = int(hcx + (2 if side else 3))
    s.set(px_, hy - 2, "flower_rose"); s.set(px_ + 1, hy - 3, "flower_rose"); s.set(px_ + 1, hy - 2, "roof_hi"); s.set(px_ + 2, hy - 3, "plaster_hi")
