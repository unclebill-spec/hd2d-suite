"""Goldspire folk (story 5 roster, Aesir, human-sized 1x): linen / wool tunics, belted trousers or belted skirts over leggings, cloaks pinned at the
shoulder, a visible gold-buckled belt, boots. Sigrun Stormwing (companion, 1.1x) is a separate sheet. Palette only; glow = fx + light."""
import math
from as_common import R, Cv
from as_giant import giant

FRAME_FOLK = (40, 44)
A2 = ("idle", "walk")
GOLD = ("flower_gold", "lamp", "timber_hi")
WINE = ("roof_hi", "roof", "roof_lo")


def Ht(scale):
    return round(29 * scale) - 2


def combine(*fs):
    def f(cv, c):
        for g in fs:
            g(cv, c)
    return f


def cloak(col=("flower_blue", "cloth", "shadow")):
    """cloak pinned at the shoulder: back panel + flanks drawn only where empty, a gold pin on the right shoulder"""
    def f(cv, c):
        CX, sh, hw, Ht_, G = c["CX"], c["sh"], c["hw"], c["Ht"], c["G"]
        side, back = c["side"], c["back"]
        bot = c["hip"] + Ht_ * .30
        for y in range(int(sh), int(bot)):
            t = (y - sh) / max(1, bot - sh)
            w = hw * (1.08 + .3 * t)
            xa, xb = (CX - w, CX + w) if not side else (CX + 1, CX + w)
            for x in range(int(xa), int(xb) + 1):
                if back or cv.get(x, y) is None:
                    u = (x - CX) / max(1, w)
                    cv.set(x, y, col[0] if u < -.5 else col[2] if u > .5 else col[1])
        if not back:
            cv.set(CX + hw * .8 * (1 if not side else -1), sh + 1, "flower_gold"); cv.set(CX + hw * .8 * (1 if not side else -1), sh + 2, "lamp")
    return f


def mantle(col=("white", "plaster_hi", "plaster")):
    def f(cv, c):
        CX, sh, hw = c["CX"], c["sh"], c["hw"]
        cv.ell(CX, sh + 1, hw * 1.15, c["Ht"] * .09, lambda u, v: col[0] if (u < -.3 and v < 0) else col[2] if v > .3 else col[1])
    return f


def circlet(cv, c):
    if c["back"]:
        return
    y = c["hcy"] - c["hh"] * .62
    cv.rect(c["hcx"] - c["hhw"] * .85, y, c["hcx"] + c["hhw"] * .85, y, "flower_gold")
    cv.set(c["hcx"], y, "sky")


def gloves(cv, c):
    for hx, hy in c["hands"]:
        cv.rect(hx - 1, hy - 1, hx + 1, hy + 1, "timber_lo"); cv.set(hx, hy, "sky")


def sash(cv, c):
    y = c["beltY"]
    cv.rect(c["CX"] - c["hw"], y - 1, c["CX"] + c["hw"], y + 1, "flower_gold")
    if not c["back"]:
        cv.rect(c["CX"] + c["hw"] * .3, y + 2, c["CX"] + c["hw"] * .3 + 1, y + 6, "lamp")


def tabard(cv, c):
    """gilded tabard over the jerkin / tunic: a gold front panel from the shoulders to below the belt, belt stays visible over it"""
    CX, sh, hw, beltY, Ht_ = c["CX"], c["sh"], c["hw"], c["beltY"], c["Ht"]
    w = hw * (.55 if not c["side"] else .4)
    for y in range(int(sh + 1), int(beltY + Ht_ * .16)):
        if y in (int(beltY), int(beltY) + 1):
            continue
        for x in range(int(CX - w), int(CX + w) + 1):
            u = (x - CX) / max(1, w)
            cv.set(x, y, GOLD[0] if u < -.4 else GOLD[2] if u > .5 else GOLD[1])
    if not c["back"]:
        cv.rect(CX - 1, sh + Ht_ * .1, CX + 1, sh + Ht_ * .1, "white")          # sun device


def hood(eyes="roof_hi"):
    def f(cv, c):
        hcx, hcy, hhw, hh = c["hcx"], c["hcy"], c["hhw"], c["hh"]
        cv.ell(hcx, hcy - hh * .12, hhw * 1.18, hh * 1.12, lambda u, v: GOLD[0] if (u < -.35 and v < .2) else GOLD[2] if (u > .55 or v > .8) else GOLD[1])
        if not c["back"]:
            ox = -(hhw * .15 if c["side"] else 0)
            cv.ell(hcx + ox, hcy + hh * .12, hhw * (.55 if c["side"] else .65), hh * .62, lambda u, v: "plaster_hi" if v < .4 else "flower_gold")   # gold mask
            for dx in ((-.3, .3) if not c["side"] else (-.45,)):
                cv.set(hcx + dx * hhw, hcy + hh * .08, eyes); cv.set(hcx + dx * hhw + 1, hcy + hh * .08, "ink")
    return f


def lamp(cv, c):
    hx, hy = c["hand_back"] if not c["side"] else c["hand"]
    x, y = hx, hy + 3
    cv.rect(x - 2, y - 3, x + 2, y + 3, "timber_lo"); cv.rect(x - 1, y - 2, x + 1, y + 2, "lamp"); cv.set(x, y - 1, "white")


def spear(cv, c):
    hx, hy = c["hand"]
    x = hx + 3
    top = hy - c["Ht"] * .9
    cv.seg(x, hy + 3, x, top, 2, 2, ("timber_hi", "timber", "timber_lo"))
    cv.poly([(x - 2, top), (x + 2, top), (x, top - max(6, c["Ht"] * .2))], lambda a, b: "white" if a < x else "stone_hi")
    cv.set(x, top + 1, "flower_gold")


def lance(cv, c):
    hx, hy = c["hand"]
    x = hx + 3
    top = hy - c["Ht"] * .95
    cv.seg(x, hy + 3, x, top, 2, 2, GOLD)
    cv.poly([(x - 2, top), (x + 2, top), (x, top - max(6, c["Ht"] * .22))], lambda a, b: "white" if a < x else "sky")


def shield(cv, c):
    hx, hy = c["hand_back"]
    r = 2 + c["k"] * 1.6
    cv.ell(hx - (0 if c["side"] else 3), hy - 3, r, r, lambda u, v: "white" if u * u + v * v < .08 else "flower_gold" if u < -.3 else "timber_hi" if u > .5 else "lamp")


def mace(cv, c):
    hx, hy = c["hand"]
    L = c["Ht"] * .32
    cv.seg(hx + 1, hy + 2, hx + 1, hy - L, 2, 2, ("stone_hi", "stone", "stone_lo"))
    cv.ell(hx + 1, hy - L - 2, max(2, c["k"] * 1.6), max(2, c["k"] * 1.6), lambda u, v: "white" if u * u + v * v < .3 else "flower_gold")


def wings(dim=True):
    """Sigrun's light-wings in palette gold (dim): drawn behind her where nothing else is; the bright gold halo with the neon-blue edge is the fx sigrun_wings"""
    def f(cv, c):
        CX, sh, Ht_, hw, i = c["CX"], c["sh"], c["Ht"], c["hw"], c["i"]
        side = c["side"]
        for sd in ((-1, 1) if not side else (1,)):
            span = Ht_ * (.42 if not side else .3)
            for j in range(int(span)):
                t = j / span
                top = sh - Ht_ * (.18 + .1 * math.sin(t * 3.0)) + (i % 2)
                bot = sh + Ht_ * (.30 - .22 * t)
                for y in range(int(top), int(bot)):
                    x = CX + sd * (hw * .6 + j)
                    if cv.get(x, y) is None and (not dim or (j + y) % 3 != 0):
                        cv.set(x, y, "white" if t > .8 and y < top + 2 else "flower_gold" if (y - top) < (bot - top) * .45 else "plaster_hi")
                if j % 3 == 0:
                    cv.set(CX + sd * (hw * .6 + j), bot, "sky")     # feather edge glint (the neon edge itself is fx)
    return f


NPCS = {
 "envoy_as": dict(scale=1.0, desc="Envoy Ingrith Goldrune (1x): cream tunic, belted blue trousers, gold-buckled belt, a gold-pinned blue cloak.",
   P=dict(skin="skin", hair="flower_gold", hairstyle="bun", tunic="cream", trousers="slate", belt=("timber_lo", "ink"), buckle="flower_gold", extra=cloak())),
 "lordwarden": dict(scale=1.0, desc="Lord-Warden Hallgerd Sunmantle (1x): wine-red tunic, belted trousers, white fur mantle, rune circlet, short beard.",
   P=dict(skin="skin", hair="timber_hi", hairstyle="short", beard="short", beard_c=R["leather"], tunic="rust", trousers="grey", belt=("timber_lo", "ink"), buckle="flower_gold", extra=combine(mantle(), circlet))),
 "runemaster": dict(scale=1.0, desc="Rune-Master Alrik Runehammer (1x): leather apron over a grey tunic, belted trousers, rune-burned gloves, braided beard.",
   P=dict(skin="skin", hair="stone", hairstyle="short", beard="braids", beard_c=R["grey"], tunic="grey", apron="leather", trousers="slate", belt=("timber_lo", "ink"), extra=gloves)),
 "priestess": dict(scale=1.0, desc="Priestess Sunna Dawnward (1x): white wrap tunic, gold sash at the waist, belted skirt over leggings.",
   P=dict(skin="skin", hair="timber", hairstyle="braids", tunic="cream", skirt="pale", trousers="grey", belt=("flower_gold", "lamp"), extra=sash)),
 "fridleif": dict(scale=1.0, desc="Captain Fridleif Thunderhelm (1x NPC): leather jerkin under a gilded tabard, belted trousers, spear. No plate.",
   P=dict(skin="skin", hair="timber_lo", hairstyle="short", tunic="slate", jerkin="leather", trousers="grey", belt=("timber_lo", "ink"), extra=combine(tabard, spear))),
 "groom": dict(scale=1.0, desc="Bodil Windmane (sky-horse keeper, 1x): quilted jerkin over a tunic, rope-belted trousers.",
   P=dict(skin="skin", hair="flower_gold", hairstyle="braids", tunic="slate", jerkin="leather", trousers="grey", belt=("plaster_lo", "timber"))),
 "as_trader": dict(scale=1.0, desc="Nessa (stall-keeper, 1x): layered tunics (wine under cream), wide belt with pouches.",
   P=dict(skin="skin", hair="roof_lo", hairstyle="topknot", tunic="rust", jerkin="cream", trousers="grey", belt=("timber", "ink"), width=1.1)),
 "as_guide": dict(scale=1.0, desc="Orla (acolyte, contract guide, 1x): plain white tunic, belted trousers, a lamp.",
   P=dict(skin="skin", hair="timber", hairstyle="short", tunic="cream", trousers="grey", belt=("timber_lo", "ink"), extra=lamp)),
}


def roles():
    return {n: dict(draw=giant(r["P"], Ht(r["scale"])), scale=r["scale"], desc=r["desc"], anims=A2, named=True, stats_hint={"tier": "npc", "height_x_player": r["scale"]})
            for n, r in NPCS.items()}


SIGRUN = dict(skin="skin", hair="flower_gold", hairstyle="braids", tunic="slate", jerkin="leather", trousers="grey", belt=("timber_lo", "ink"), buckle="flower_gold",
              boots=("timber", "timber_lo"), extra=combine(wings(), spear))


def sigrun_roles():
    return {"sigrun": dict(draw=giant(SIGRUN, Ht(1.1)), scale=1.1, anims=("idle", "walk", "cast", "attack"), named=True, kind="companion",
                           desc="Sigrun Stormwing (companion, 1.1x): storm-blue tunic, leather jerkin, belted trousers, boots, spear, dim palette light-wings (bright wings = fx sigrun_wings). walk = follow, attack = dive_strike, cast = raven_guard. NO pet.",
                           light={"color": "#ffc85a", "intensity": 0.9, "range": 5.0}, stats_hint={"tier": "companion", "height_x_player": 1.1})}
