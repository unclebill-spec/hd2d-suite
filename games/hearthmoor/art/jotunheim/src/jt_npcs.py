"""Stonehollow townsfolk (story 5 roster) at 3x etc. Frame 64x104; one frame size per sheet."""
from jt_common import R, Cv
from jt_giant import giant

FRAME = (64, 100)
A2 = ("idle", "walk")


def Ht(scale):
    return round(29 * scale) - 2


def horn(cv, c):
    """Kolbrun's horn on a strap at the hip (the kolbrun_horn item)"""
    x, y = c["CX"] + c["hw"] * .9, c["beltY"] + c["Ht"] * .09
    cv.seg(x, y - 2, x + c["Ht"] * .09, y + c["Ht"] * .06, 4 * c["k"] * .5 + 1, 6 * c["k"] * .3 + 2, ("plaster_hi", "plaster", "plaster_lo"))
    cv.rect(x - 1, y - 3, x + 1, y - 2, "flower_gold")


def circlet(cv, c):
    """rune-iron circlet (Jarl): a band across the brow with a sky rune stud"""
    if c["back"]:
        return
    y = c["hcy"] - c["hh"] * .62
    cv.rect(c["hcx"] - c["hhw"] * .85, y, c["hcx"] + c["hhw"] * .85, y + 1, "stone_lo")
    cv.rect(c["hcx"] - c["hhw"] * .85, y - 1, c["hcx"] + c["hhw"] * .85, y - 1, "stone_hi")
    cv.set(c["hcx"], y, "sky"); cv.set(c["hcx"], y + 1, "flower_blue")


def pouches(cv, c):
    for dx in (-1.0, 0.65, 0.95):
        x, y = c["CX"] + c["hw"] * dx, c["beltY"] + 2
        cv.rect(x - 2, y, x + 2, y + 5, "timber"); cv.rect(x - 2, y, x + 2, y, "timber_hi"); cv.rect(x - 2, y + 5, x + 2, y + 5, "timber_lo")
        cv.set(x, y + 1, "flower_gold")


def staff(glow):
    def f(cv, c):
        hx, hy = c["hand"]
        x = hx + (2 if not c["side"] else 1)
        top = hy - c["Ht"] * .6
        cv.seg(x, hy + 2, x, top, 3, 3, ("timber_hi", "timber", "timber_lo"))
        if glow:
            cv.ell(x, top - 2, 3, 3, lambda u, v: "white" if u * u + v * v < .3 else "sky")
            for dx, dy in ((-3, -1), (3, -1), (0, -5)):
                cv.set(x + dx, top - 2 + dy, "flower_blue")
        else:
            cv.rect(x - 2, top - 2, x + 2, top, "timber_hi")
    return f


def crook(cv, c):
    hx, hy = c["hand"]
    x = hx + 2
    top = hy - c["Ht"] * .6
    cv.seg(x, hy + 2, x, top, 2, 2, ("timber_hi", "timber", "timber_lo"))
    cv.seg(x, top, x - 4, top - 1, 2, 2, ("timber_hi", "timber", "timber_lo")); cv.set(x - 5, top + 1, "timber")


def shield_back(cv, c):
    """round shield on her back (the shield wall); only visible from behind / side"""
    if c["back"]:
        cv.ell(c["CX"], c["sh"] + c["Ht"] * .2, c["hw"] * .85, c["hw"] * .85, lambda u, v: "stone_hi" if u * u + v * v < .12 else "roof" if (u < -.3) else "roof_lo")
        cv.ell(c["CX"], c["sh"] + c["Ht"] * .2, 2, 2, "stone_hi")


def spear(cv, c):
    hx, hy = c["hand"]
    x = hx + 3
    cv.seg(x, hy + 3, x, hy - c["Ht"] * .85, 2, 2, ("timber_hi", "timber", "timber_lo"))
    cv.poly([(x - 2, hy - c["Ht"] * .85), (x + 2, hy - c["Ht"] * .85), (x, hy - c["Ht"] * .85 - 7)], lambda a, b: "stone_hi" if a < x else "stone")


def runebraids(cv, c):
    """rune-glow braid ties: sky beads down the braids (palette sky; the glow itself is fx)"""
    if c["back"] or c["side"]:
        return
    for sd in (-1, 1):
        bx = c["hcx"] + sd * (c["hhw"] + 1)
        for j in range(4, int(c["Ht"] * .30), 5):
            cv.set(bx, c["hcy"] + c["hh"] * .1 + j, "sky")


def combine(*fs):
    def f(cv, c):
        for g in fs:
            g(cv, c)
    return f


NPCS = {
 "kolbrun": dict(scale=3.0, desc="Envoy Kolbrun Hailstride (3x): slate wool tunic, belted grey trousers, white fur mantle, braided hair, Kolbrun's horn on a strap.",
   P=dict(skin="pale", hair="grey", hairstyle="braids", tunic="slate", trousers="grey", mantle="snowfur", extra=horn)),
 "jarl": dict(scale=3.2, desc="Jarl Thyra Stonebrow (3.2x): rust tunic, belted trousers, bear-fur mantle, rune-iron circlet, long grey braids.",
   P=dict(skin="skin", hair="grey", hairstyle="braids", tunic="rust", trousers="leather", mantle="brownfur", width=1.1, extra=combine(circlet, staff(False)))),
 "ulfar_town": dict(scale=3.0, desc="Ulfar Mossback in town (3x): moss-green tunic, patched belted trousers, moss on his shoulders, shy and gentle.",
   P=dict(skin="ruddy", hair="timber", hairstyle="short", beard="short", beard_c=R["leather"], tunic="moss", trousers="leather", mantle="moss", width=1.15, hunch=0.25)),
 "rimewife": dict(scale=2.8, desc="Rimewife Solvi (2.8x): blue-grey wrap tunic, belted skirt over leggings, rune-glow braids, rune staff.",
   P=dict(skin="pale", hair="grey", hairstyle="braids", tunic="slate", trousers="grey", skirt="icedeep", trim="sky", extra=combine(runebraids, staff(True)), width=.92)),
 "skuli": dict(scale=2.0, desc="Skuli (2x, a giant kid): oversized rust tunic, rope-belted trousers, a goatherd's crook.",
   P=dict(skin="skin", hair="timber_hi", hairstyle="short", tunic="rust", trousers="grey", belt=("plaster_lo", "timber"), head=1.3, width=.9, extra=crook)),
 "goatwife": dict(scale=3.0, desc="Brynja Hornwise (3x): leather apron over a tunic and belted trousers, rolled sleeves, hair in a bun.",
   P=dict(skin="ruddy", hair="roof", hairstyle="bun", tunic="cream", trousers="slate", apron="leather", sleeves="cream", width=1.05)),
 "grimsa": dict(scale=3.0, desc="Grimsa the trader (3x): layered wool tunics, a wide belt hung with pouches, a fur cap-less braid.",
   P=dict(skin="skin", hair="timber", hairstyle="topknot", tunic="moss", trousers="rust", mantle="darkfur", belt=("timber", "ink"), extra=pouches, width=1.1, jerkin="leather")),
 "rimecaptain": dict(scale=3.0, desc="Rime-Captain Hjordis Icejaw (3x): leather jerkin over a belted tunic, belted trousers, round shield on her back, spear. No plate.",
   P=dict(skin="pale", hair="timber_lo", hairstyle="braids", tunic="grey", trousers="slate", jerkin="leather", extra=combine(shield_back, spear))),
 "gi_man": dict(scale=3.0, desc="Stonehollow giant villager (3x): wool tunic, belted trousers, bushy braided beard.",
   P=dict(skin="ruddy", hair="roof", hairstyle="short", beard="braids", beard_c=R["rust"], tunic="grey", trousers="leather", width=1.1)),
 "gi_woman": dict(scale=2.9, desc="Stonehollow giant villager (2.9x): moss tunic, belted trousers, fur mantle, long hair.",
   P=dict(skin="skin", hair="flower_gold", hairstyle="long", tunic="moss", trousers="slate", mantle="darkfur", width=.95)),
}


def roles():
    out = {}
    for n, r in NPCS.items():
        out[n] = dict(draw=giant(r["P"], Ht(r["scale"])), scale=r["scale"], desc=r["desc"], anims=A2, named=n not in ("gi_man", "gi_woman"),
                      stats_hint={"tier": "npc", "height_x_player": r["scale"]})
    return out
