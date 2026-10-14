"""Verdant Heart: Hjortur the Greenheart (boss, 6x: 144x192 frame) and the Thornmother (rare, 2.4x: 48x77 frame).
Drawn natively (never upscaled), biome palette only, boss_sheet.py conventions (pivot bottom-centre, 28 columns).

Hjortur: an elder stag-king. His antlers are living branches in leaf, hung with gold spore-lanterns and moonpetals; a
moss mantle with white fawn-spots on his back, a long white elder's beard, warm glowing eyes. Two roles share one drawer:
  hjortur            the guardian (befriend path: a trial). 'die' = he kneels and lies down at peace (yields).
  hjortur_corrupted  the conquer path: blight veins, red toadstools in place of leaves, mauve blight blossoms, rose eyes;
                     'die' = he lies down and the corruption lifts (leaves return). Cozy-gloomy, never gory.
Thornmother (story/verdant_heart.md 7.3, the V4 rare): a corrupted dryad-tree, a willowy figure of bark and thorns with a
moonpetal crown gone violet (bark bodice, dark vine at the waist, a skirt of willow fronds, root feet, a bramble staff)."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vh_boss import tline, toad, blossom, lantern  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_lib"))
from hmart import ell, rect, shader  # noqa: E402

HW, HH = 144, 192
HCX = 72


def moonpetal(s, x, y):
    for (dx, dy) in ((0, -1), (-1, 0), (1, 0), (0, 1)):
        s.set(x + dx, y + dy, "flower_blue")
    s.set(x, y, "white")


def leafclump(s, x, y, r, corrupt, i):
    if corrupt:
        ell(s, x, y, r, r * 0.7, "leaf_deep", shader(x, r, "moss", "leaf_deep", "shadow"))
    else:
        ell(s, x, y, r, r * 0.7, "grass", shader(x, r, "grass_hi", "grass", "moss"))
        s.set(int(x - r / 2), int(y - 1), "grass_hi")


def stag_antlers(s, bx, by, face, i, corrupt, lift=0, spread=1.0):
    """two great antlers of living branch: main beam + 4 tines each, leaves / lanterns / moonpetals on the tips"""
    sides = (-1, 1)
    for sd in sides:
        far = face == "left" and sd == 1
        col, hi, lo = ("timber_lo", None, "ink") if far else ("timber_hi" if not corrupt else "timber", "plaster_lo" if not corrupt else "timber_hi", "timber_lo")
        sp = spread * (0.55 if face == "left" else 1.0)
        ox = bx + sd * (6 if face != "left" else 3) + (8 if far else 0)
        pts = [(ox, by), (ox + sd * 22 * sp, by - 14 - lift), (ox + sd * 36 * sp, by - 32 - lift),
               (ox + sd * 46 * sp, by - 48 - lift), (ox + sd * 52 * sp, by - 60 - lift)]
        for k in range(4):
            tline(s, *pts[k], *pts[k + 1], 7 - k, col, hi, lo)
        tines = [(pts[1], (pts[1][0] + sd * 3 * sp, pts[1][1] - 16)),
                 (pts[2], (pts[2][0] - sd * 6 * sp, pts[2][1] - 16)),
                 (pts[2], (pts[2][0] + sd * 16 * sp, pts[2][1] - 4)),
                 (pts[3], (pts[3][0] - sd * 9 * sp, pts[3][1] - 12)),
                 (pts[3], (pts[3][0] + sd * 12 * sp, pts[3][1] - 6))]
        for k, (a, b) in enumerate(tines):
            tline(s, *a, *b, 3, col, None, lo)
            if far:
                ell(s, b[0], b[1], 3, 2, "moss" if not corrupt else "shadow")
                continue
            leafclump(s, b[0], b[1], 4 + (k % 2), corrupt, i)
            if not corrupt and k % 2 == 1:
                s.set(int(b[0]), int(b[1]) - 1, "white")               # a glint of dew-light on the leaves
            if corrupt and k % 2 == 0:
                toad(s, int(b[0]), int(b[1]) - 2, 4)
            elif corrupt:
                blossom(s, int(b[0]) + 2, int(b[1]) + 1, (i + k) % 2 == 0)
            elif k % 2 == 0:
                moonpetal(s, int(b[0]) + 2, int(b[1]) - 1)
            if k in (1, 4):
                lantern(s, int(b[0]) - sd * 2, int(b[1]) + 5, i + k)
        if not far:
            leafclump(s, pts[4][0], pts[4][1], 5, corrupt, i)
            if corrupt:
                toad(s, int(pts[4][0]), int(pts[4][1]) - 3, 5)
            else:
                moonpetal(s, int(pts[4][0]), int(pts[4][1]) - 2)


def fur(x, y, cx, rx, corrupt):
    u = (x - (cx - rx)) / max(1, 2 * rx)
    if u < 0.22:
        return "timber_hi"
    if u > 0.76:
        return "timber_lo"
    return "timber"


def body_ell(s, cx, cy, rx, ry, corrupt, belly=True):
    ell(s, cx, cy, rx, ry, "timber", lambda x, y, c: fur(x, y, cx, rx, corrupt))
    if not belly:                                                     # front / back: a pale chest patch instead
        ell(s, cx, cy - ry * 0.25, rx * 0.42, ry * 0.5, "timber_hi")
        return
    for y in range(int(cy), int(cy + ry) + 1):                       # cream belly: a soft crescent underneath
        for x in range(int(cx - rx), int(cx + rx) + 1):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 0.86 and ((x - cx) / (rx * 0.95)) ** 2 + ((y - cy + ry * 0.22) / ry) ** 2 > 1:
                s.set(x, y, "plaster" if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 0.6 else "plaster_lo")


def mantle(s, cx, cy, rx, corrupt, i):
    """moss mantle across the back with white fawn-spots and little flowers"""
    for y in range(int(cy - 8), int(cy + 4)):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            u = (x - cx) / rx
            if abs(u) <= 1 and y >= cy - 8 * math.sqrt(1 - u * u):
                s.set(x, y, ("moss" if (x + y) % 5 else "grass") if not corrupt else ("leaf_deep" if (x + y) % 4 else "shadow"))
    for k in range(int(rx / 3)):
        x = cx - rx + 3 + k * 6
        ln = 3 + (k * 5 + i) % 6
        for y in range(int(cy + 4), int(cy + 4 + ln)):
            s.set(int(x), y, "moss" if not corrupt else "leaf_deep")
    for k in range(int(rx / 6)):
        x = cx - rx + 6 + k * 12
        s.set(int(x), int(cy - 3), "plaster_hi"); s.set(int(x) + 1, int(cy - 3), "plaster_hi")
        if corrupt:
            s.set(int(x) + 3, int(cy - 5), "flower_rose")
        else:
            s.set(int(x) + 4, int(cy - 5), "flower_gold" if k % 2 else "flower_blue")


def leg(s, x0, y0, x1, y1, w, far, hoofy=None):
    col, hi, lo = ("timber_lo", None, "ink") if far else ("timber", "timber_hi", "timber_lo")
    kx, ky = (x0 + x1) / 2 + 2, (y0 + y1) / 2
    tline(s, x0, y0, kx, ky, w, col, hi, lo)
    tline(s, kx, ky, x1, y1 - 4, max(3, w - 3), col, hi, lo)
    rect(s, int(x1 - 2), int(y1 - 4), int(x1 + 2), int(y1), "shadow")
    s.set(int(x1 - 2), int(y1 - 4), "plaster_lo")


def hjortur_draw(s, face, anim, i, corrupt=False):
    side = face == "left"
    G = HH - 1                                                  # ground row
    b = 0; down = 0; lunge = 0; lift = [0, 0, 0, 0]; rest = 0; cleanse = False
    if anim == "idle":
        b = [0, 1, 1, 0][i]
    elif anim == "walk":
        lift = [(6, 0, 0, 6), (0, 0, 0, 0), (0, 6, 6, 0), (0, 0, 0, 0)][i] if face == "left" else [(6, 0, 0, 0), (0, 0, 0, 0), (0, 0, 6, 0), (0, 0, 0, 0)][i]; b = [0, -1, 0, -1][i]
    elif anim == "attack":
        down = [6, 14, 18, 8][i]; lunge = [0, 4, 10, 4][i]; b = [0, 2, 3, 1][i]
    elif anim == "die":
        rest = [6, 24, 52, 56][i]; cleanse = corrupt and i == 3; down = [4, 10, 6, 12][i]
    cr = corrupt and not cleanse
    if side:
        cx0 = 71
        cx, cy = cx0 - lunge, 124 + b + rest
        # legs (far pair first); folded when resting
        if rest < 30:
            for (lx, far, k) in ((cx0 - 30, True, 1), (cx0 + 26, True, 3), (cx0 - 24, False, 0), (cx0 + 32, False, 2)):
                fold = rest // 2
                leg(s, lx - lunge, cy + 6, lx - (3 if anim == "walk" and lift[k] else 0) - fold // 3, G - lift[k], 9 if not far else 8, far)
        else:
            for (lx, w) in ((cx - 30, 8), (cx + 22, 8)):
                tline(s, lx, G - 6, lx - 18, G - 3, w, "timber", "timber_hi", "timber_lo")
                rect(s, lx - 22, G - 4, lx - 18, G, "shadow")
        body_ell(s, cx, cy, 42, 24, cr)
        mantle(s, cx + 4, cy - 14, 34, cr, i)
        s.set(cx + 42, cy - 8, "plaster_hi"); s.set(cx + 43, cy - 9, "plaster_hi"); s.set(cx + 43, cy - 8, "white")   # tail
        # neck + head (head lowered on the attack / bow)
        hx, hy = cx - 44 - lunge // 2, cy - 44 + down
        tline(s, cx - 30, cy - 6, hx + 6, hy + 6, 18, "timber", "timber_hi", "timber_lo")
        for k in range(8):                                    # the elder's white beard down the throat
            tline(s, hx + 4 + k * 2, hy + 14 + k, hx + 2 + k * 2, hy + 26 + k * 1.5 - (k % 3), 2, "plaster_hi" if k % 2 else "white")
        stag_antlers(s, hx + 6, hy - 8, face, i, cr, lift=-down // 2, spread=1.0 if anim != "attack" else 0.8)
        ell(s, hx, hy, 12, 9, "timber", shader(hx, 12, "timber_hi", "timber", "timber_lo"))
        ell(s, hx - 13, hy + 5, 7, 5, "timber_hi", shader(hx - 13, 7, "plaster_lo", "timber_hi", "timber"))
        rect(s, hx - 20, hy + 3, hx - 18, hy + 5, "ink")
        s.set(hx - 12, hy + 10, "plaster_lo")
        tline(s, hx + 8, hy - 6, hx + 16, hy - 12, 4, "timber", None, "timber_lo"); s.set(hx + 13, hy - 9, "flower_rose")   # ear
        ec = "flower_rose" if cr else "lamp"
        if rest > 50 and i == 3:
            rect(s, hx - 5, hy - 1, hx - 1, hy - 1, "ink")        # eyes closed, at peace
        else:
            rect(s, hx - 5, hy - 2, hx - 2, hy, ec); s.set(hx - 4, hy - 2, "white")
        if cr:
            for k in range(4):
                for t in range(10):
                    s.set(cx - 30 + k * 18 + int(2 * math.sin(t + k)), cy - 4 + t * 2, "shadow")
                s.set(cx - 30 + k * 18, cy + 6, "flower_rose")
    else:
        front = face == "down"
        cx, cy = HCX, 126 + b + rest
        if rest < 30:
            for (lx, far, k) in ((cx - 20, True, 1), (cx + 20, True, 3), (cx - 13, False, 0), (cx + 13, False, 2)):
                fold = rest // 2
                leg(s, lx, cy, lx + (fold // 3) * (1 if lx > cx else -1), G - lift[k] - (1 if far else 0), 10 if not far else 8, far)
            if front:                                          # hooves of the far pair still touch ground
                pass
        else:
            for sd in (-1, 1):
                tline(s, cx + sd * 10, G - 5, cx + sd * 26, G - 3, 8, "timber", "timber_hi", "timber_lo")
                rect(s, cx + sd * 28 - 2, G - 4, cx + sd * 28 + 2, G, "shadow")
        body_ell(s, cx, cy, 30, 28, cr, False) if front else body_ell(s, cx, cy, 32, 28, cr, False)
        if front:                                              # moss over the shoulders
            for sd in (-1, 1):
                ell(s, cx + sd * 22, cy - 20, 10, 6, "moss" if not cr else "leaf_deep")
                for k in range(5):
                    for y in range(cy - 16, cy - 12 + (k * 3) % 5):
                        s.set(cx + sd * (14 + k * 4), y, "moss" if not cr else "leaf_deep")
                s.set(cx + sd * 20, cy - 23, "plaster_hi"); s.set(cx + sd * 25, cy - 21, "flower_gold" if not cr else "flower_rose")
        if not front:
            mantle(s, cx, cy - 20, 28, cr, i)
            ell(s, cx, cy + 14, 6, 5, "plaster_hi"); s.set(cx, cy + 12, "white")       # tail
        hx, hy = cx, cy - 48 + down
        if front:
            tline(s, cx, cy - 10, hx, hy + 8, 22, "timber", "timber_hi", "timber_lo")
            for k in range(11):
                tline(s, hx - 10 + k * 2, hy + 18, hx - 9 + k * 2, hy + 40 - abs(k - 5) * 2, 2, "plaster_hi" if k % 2 else "white")
        else:
            tline(s, cx, cy - 16, hx, hy + 6, 22, "timber", "timber_hi", "timber_lo")
        stag_antlers(s, hx, hy - 10, face, i, cr, lift=-down // 2, spread=1.0 if anim != "attack" else 0.86)
        for sd in (-1, 1):                                    # ears
            tline(s, hx + sd * 10, hy - 6, hx + sd * 20, hy - 9, 5, "timber", None, "timber_lo")
            s.set(hx + sd * 17, hy - 8, "flower_rose")
        ell(s, hx, hy, 12, 12, "timber", shader(hx, 12, "timber_hi", "timber", "timber_lo"))
        if front:
            ell(s, hx, hy + 11, 7, 6, "timber_hi", shader(hx, 7, "plaster_lo", "timber_hi", "timber"))
            rect(s, hx - 2, hy + 13, hx + 2, hy + 15, "ink"); s.set(hx - 1, hy + 13, "stone")
            ec = "flower_rose" if cr else "lamp"
            for sd in (-1, 1):
                if rest > 50 and i == 3:
                    rect(s, hx + sd * 6 - 2, hy, hx + sd * 6 + 1, hy, "ink")
                else:
                    rect(s, hx + sd * 6 - 2, hy - 2, hx + sd * 6 + 1, hy + 1, ec); s.set(hx + sd * 6 - 1, hy - 2, "white")
            # the Greenheart mark on his brow: a glowing leaf (or a blight knot)
            if cr:
                ell(s, hx, hy - 7, 3, 2.5, "flower_rose"); s.set(hx, hy - 7, "white")
            else:
                for (dx, dy) in ((0, -10), (-1, -9), (1, -9), (0, -9), (0, -8), (-1, -7), (1, -7), (0, -6)):
                    s.set(hx + dx, hy + dy, "grass_hi")
                s.set(hx, hy - 8, "white")
            if not cr:                                         # a garland of moonpetals across the chest
                for k in range(9):
                    a = math.pi * (0.15 + 0.7 * k / 8)
                    x, y = hx + 20 * math.cos(a), cy - 18 + 8 * math.sin(a)
                    s.set(int(x), int(y), "grass"); s.set(int(x), int(y) - 1, "moss")
                    if k % 2 == 0:
                        moonpetal(s, int(x), int(y) + 1)
            else:
                for k in range(5):
                    for t in range(12):
                        s.set(cx - 18 + k * 9 + int(2 * math.sin(t * 0.8 + k)), cy - 6 + t * 2, "shadow")
                toad(s, cx - 22, cy - 22, 4); toad(s, cx + 20, cy - 20, 3)
    if anim == "attack" and i == 2:                           # the stomp: leaves + roots burst
        for k, x in enumerate((HCX - 52, HCX - 38, HCX + 38, HCX + 52)):
            tline(s, x, G, x + (k % 2 * 2 - 1) * 3, G - 14, 3, "timber_lo", "timber", "ink")
        for (x, y) in ((HCX - 46, G - 22), (HCX + 46, G - 24), (HCX - 30, G - 10), (HCX + 30, G - 12)):
            s.set(x, y, "grass_hi"); s.set(x + 1, y, "grass")
    if anim == "die" and i >= 2:                              # flowers open around him as he rests
        for k in range(8):
            x = 18 + k * 15
            s.set(x, G - 1, "moss"); s.set(x + 1, G - 1, "grass")
            if i == 3 or k % 2 == 0:
                (moonpetal if (k % 2 or cr) is False or not corrupt else moonpetal)(s, x, G - 4)
                s.set(x, G - 2, "moss")
    # drifting motes (gold leaves / green glints)
    for k in range(10):
        a = k / 10 * math.tau + i * 0.4
        x, y = HCX + 62 * math.cos(a), 112 + 50 * math.sin(a)
        if 2 <= x < HW - 2 and 2 <= y < HH - 3 and s.p[int(y)][int(x)] is None:
            s.set(int(x), int(y), ("flower_rose" if k % 2 else "shadow") if cr else ("flower_gold" if k % 2 else "grass_hi"))


def hjortur(s, face, anim, i):
    hjortur_draw(s, face, anim, i, False)


def hjortur_corrupted(s, face, anim, i):
    hjortur_draw(s, face, anim, i, True)


# ---------------------------------------------------------------------------------------------- the Thornmother
TW, TH = 48, 77
TCX = 24


def moonpetal_violet(s, x, y, k):
    """a moonpetal gone violet: mauve / rose / blue petals round a pale heart"""
    for n, (dx, dy) in enumerate(((0, -1), (-1, 0), (1, 0), (0, 1))):
        s.set(x + dx, y + dy, ("flower_rose", "shadow", "flower_blue", "flower_rose")[(n + k) % 4])
    s.set(x, y, "plaster_hi")


def thornmother(s, face, anim, i):
    """the Thornmother (Verdant Heart V4 rare, story/verdant_heart.md 7.3): a corrupted dryad-tree, a willowy figure of
    bark and thorns: a bark bodice studded with thorns, a waist bound with a dark vine, a long skirt of trailing willow
    fronds over root feet, long willow-frond hair, a pale birch face with violet-rose eyes and a moonpetal crown gone
    violet; a bramble staff with a violet bud. Attack = bramble whips / thorn volley; die = sinks into a blooming mound."""
    side = face == "left"
    G = TH - 1
    b = 0; st = 0; sink = 0; lean = 0
    if anim == "idle":
        b = [0, 1, 1, 0][i]
    elif anim == "walk":
        b = [0, -1, 0, -1][i]
    elif anim == "attack":
        st = [1, 2, 3, 1][i]; lean = [0, -1, -2, 0][i]
    elif anim == "die":
        sink = [3, 10, 30, 40][i]
    if anim == "die" and i >= 2:                              # she sinks into a bramble mound that blooms
        top = G - (16 if i == 2 else 12)
        ell(s, TCX, G - 5, 19, G - top - 5, "leaf_deep", shader(TCX, 19, "moss", "leaf_deep", "leaf_deep"))
        for k in range(12):
            a = k / 12 * math.pi
            tline(s, TCX, G - 4, TCX + 20 * math.cos(a), G - 4 - 13 * math.sin(a), 1, "timber_lo")
        for k, (dx, dy) in enumerate(((-10, -8), (6, -12), (12, -4), (-4, -14), (-14, -2))):
            moonpetal_violet(s, TCX + dx, G + dy, k + i)
        if i == 3:
            for (dx, dy) in ((-6, -4), (2, -6), (9, -9)):
                s.set(TCX + dx, G + dy, "white"); s.set(TCX + dx + 1, G + dy, "flower_blue")
        rect(s, TCX - 16, G - 1, TCX + 16, G, "moss")
        return
    by = b + sink
    hip = 46 + by
    sw = [0, 1, 0, -1][i] if anim == "walk" else 0
    # skirt of trailing willow fronds (to the ground), root feet
    for y in range(hip, G - 1):
        t = (y - hip) / max(1, G - 1 - hip)
        hw = 6 + int(7 * t) - (2 if side else 0)
        for x in range(TCX - hw + (1 if side else 0) + int(sw * t), TCX + hw + 1 + int(sw * t)):
            u = (x - (TCX - hw)) / max(1, 2 * hw)
            frond = (x + (1 if y % 6 < 3 else 0)) % 3
            c = "grass" if u < 0.25 else "leaf_deep" if u > 0.75 else "moss"
            if frond == 0:
                c = "leaf_deep" if u > 0.3 else "moss"
            if y >= G - 3 and (x + y) % 2:
                continue                                      # ragged frond tips at the hem
            s.set(x, y, c)
    if anim != "die":
        for sd in ((-1, 1) if not side else (-1,)):
            f = [0, 2, 0, -2][i] * sd if anim == "walk" else 0
            bx = TCX + sd * 4 + f - (2 if side else 0)
            rect(s, bx - 2, G - 1, bx + 2, G, "timber_lo"); s.set(bx - 3 * (1 if sd < 0 else -1), G, "timber_lo")
    else:
        rect(s, TCX - 10, G - 1, TCX + 10, G, "leaf_deep")
    # waist: bound with a dark vine, a violet bud at the knot
    rect(s, TCX - 6 + (1 if side else 0), hip - 2, TCX + 6 - (2 if side else 0), hip, "shadow")
    if face == "down":
        s.set(TCX + 2, hip - 1, "flower_rose"); s.set(TCX + 3, hip + 1, "shadow"); s.set(TCX + 3, hip + 2, "leaf_deep")
    # bark bodice: slender, studded with thorns
    sh = 26 + by
    for y in range(sh, hip - 2):
        t = (y - sh) / max(1, hip - 2 - sh)
        hw = int(7 - 2 * t)
        for x in range(TCX - hw, TCX + hw + 1 - (2 if side else 0)):
            u = (x - (TCX - hw)) / max(1, 2 * hw)
            c = "timber_hi" if u < 0.25 else "timber_lo" if u > 0.75 else "timber"
            if (x * 3 + y) % 7 == 0:
                c = "timber_lo"
            s.set(x, y, c)
        if y % 4 == 1:                                        # thorns along the edges
            s.set(TCX - hw - 1, y, "plaster_lo")
            if not side:
                s.set(TCX + hw + 1, y, "plaster_lo")
    # arms: slender bark arms, twig fingers
    hx = TCX + (9 if not side else -11 + lean * 2)
    if face == "up":
        hx = TCX - 9
    ay = sh + 12 - st * 3
    tline(s, hx - (2 if not side else -2), sh + 2, hx, ay, 2, "timber", None, "timber_lo")
    s.set(hx - 1, ay + 1, "timber_hi"); s.set(hx + 1, ay + 1, "timber_hi"); s.set(hx, ay + 2, "timber_hi")
    if not side and face != "up":                             # the other arm hangs, thorny
        tline(s, TCX - 8, sh + 2, TCX - 10, sh + 14 + sw, 2, "timber", None, "timber_lo")
        s.set(TCX - 10, sh + 15 + sw, "timber_hi"); s.set(TCX - 11, sh + 9, "plaster_lo")
    # the bramble staff with a violet moonpetal bud
    sx = hx + (1 if not side else -1)
    stop = sh - 12 - st * 3
    for y in range(stop, G + 1):
        s.set(sx + (1 if (y // 7) % 2 and y > stop + 4 else 0), y, "timber_lo" if y % 4 else "timber")
        if y % 6 == 0 and y > stop + 4:
            s.set(sx + 2, y, "plaster_lo")
    ell(s, sx, stop - 2, 2.5, 2.5, "shadow"); moonpetal_violet(s, sx, stop - 2, i)
    if anim == "attack" and st >= 2:                          # bramble whips lash out from the hem
        d = -1 if side else 1
        for k in range(2):
            for t in range(10 + st * 3):
                x = TCX + d * (8 + t) if not side else TCX - 8 - t
                y = G - 3 - k * 6 - int(t * (0.3 + 0.2 * k))
                if 1 < x < TW - 2:
                    s.set(x, y, "leaf_deep" if t % 3 else "timber_lo")
                    if t % 4 == 2:
                        s.set(x, y - 1, "plaster_lo")
    # head: pale birch face, long willow-frond hair, violet-rose eyes, moonpetal crown gone violet
    hy = 18 + by
    hcx = TCX - (2 if side else 0)
    if face == "up":
        ell(s, hcx, hy, 6, 6.5, "moss", shader(hcx, 6, "grass", "moss", "leaf_deep"))
        for x in range(hcx - 6, hcx + 7):
            for y in range(hy + 3, hy + 26 + (x % 3) * 2):
                s.set(x, y, "moss" if (x + y // 3) % 3 else "leaf_deep")
    else:
        for x in ((hcx - 7, hcx - 6, hcx + 6, hcx + 7) if face == "down" else (hcx + 3, hcx + 4, hcx + 5, hcx + 6)):
            for y in range(hy - 4, hy + 22 + (x % 3) * 2):          # willow-frond hair falling past the shoulders
                s.set(x, y, "moss" if (x + y // 2) % 3 else "leaf_deep")
        ell(s, hcx, hy, 5, 6, "plaster", shader(hcx, 5, "plaster_hi", "plaster", "plaster_lo"))
        ell(s, hcx, hy - 5, 6.5, 3, "moss", shader(hcx, 6.5, "grass", "moss", "leaf_deep"))
        s.set(hcx - 3, hy + 3, "plaster_lo"); s.set(hcx + 3, hy + 2, "plaster_lo")       # birch marks
        if face == "down":
            for ex in (-3, 2):
                rect(s, hcx + ex, hy - 1, hcx + ex + 1, hy, "flower_rose"); s.set(hcx + ex, hy - 1, "white")
            rect(s, hcx - 1, hy + 3, hcx + 1, hy + 3, "plaster_lo")
        else:
            rect(s, hcx - 4, hy - 1, hcx - 3, hy, "flower_rose"); s.set(hcx - 4, hy - 1, "white")
            s.set(hcx - 5, hy + 1, "plaster")
    for k in range(7):                                        # moonpetal crown gone violet, on thorny twigs
        a = math.pi * (1.05 + 0.9 * k / 6)
        x, y = hcx + 7 * math.cos(a), hy - 5 + 4 * math.sin(a)
        tline(s, x, y, x + 2 * math.cos(a), y + 3 * math.sin(a) - 2, 1, "timber_lo")
        if k % 2 == 1:
            moonpetal_violet(s, int(x), int(y) - 3, k + i)
    # floating thorn-seeds / violet glints
    for k in range(5):
        a = k / 5 * math.tau + i * 0.6
        x, y = TCX + 20 * math.cos(a), 42 + by + 16 * math.sin(a)
        if 1 < x < TW - 2 and 1 < y < G - 3 and s.p[int(y)][int(x)] is None:
            s.set(int(x), int(y), "flower_rose" if k % 2 else "plaster_lo")
