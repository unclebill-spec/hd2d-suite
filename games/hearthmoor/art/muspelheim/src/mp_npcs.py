"""Cinderhold townsfolk (story 5 roster): ember-kin (human-sized) and fire-giants (2.5-2.6x). Real tunics, belts, trousers, boots. One frame size per sheet."""
from mp_common import R, Cv
from mp_giant import giant

FRAME = (64, 100)
FRAME_FOLK = (40, 44)
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




def veins(cv, c):
    """ember-kin faint glowing veins: a few lamp-gold pixels on the neck, cheeks and forearms (palette lamp; the glow itself is a light)"""
    if c["back"]:
        for dx in (-.4, .3):
            cv.set(c["hcx"] + dx * c["hhw"], c["hcy"] + c["hh"] * .95, "lamp")
        return
    cv.set(c["hcx"] - c["hhw"] * .55, c["hcy"] + c["hh"] * .55, "lamp")
    if not c["side"]:
        cv.set(c["hcx"] + c["hhw"] * .55, c["hcy"] + c["hh"] * .6, "lamp")
    cv.set(c["hcx"] + (1 if not c["side"] else 0), c["hcy"] + c["hh"] * 1.0, "lamp")
    hx, hy = c["hand"]
    cv.set(hx, hy - 3 - c["k"], "lamp")


def scars(cv, c):
    """Grettir's burn-scarred forearms: rose-pink patches"""
    for (hx, hy) in (c["hand"], c["hand_back"]):
        for dy in (3, 4, 5):
            cv.set(hx - 1 + (dy % 2), hy - dy, "flower_rose")
    veins(cv, c) if False else None


def copper_circlet(cv, c):
    if c["back"]:
        return
    y = c["hcy"] - c["hh"] * .62
    cv.rect(c["hcx"] - c["hhw"] * .85, y, c["hcx"] + c["hhw"] * .85, y + 1, "roof")
    cv.rect(c["hcx"] - c["hhw"] * .85, y - 1, c["hcx"] + c["hhw"] * .85, y - 1, "roof_hi")
    cv.set(c["hcx"], y, "lamp"); cv.set(c["hcx"], y + 1, "flower_gold")


def hammer(cv, c):
    """forge-judge's contest hammer: timber haft, black iron head with a hot lip"""
    hx, hy = c["hand"]
    x = hx + (2 if not c["side"] else 1)
    top = hy - c["Ht"] * (.45 + c["at"] * .1)
    cv.seg(x, hy + 2, x, top, 3, 3, ("timber_hi", "timber", "timber_lo"))
    cv.rect(x - 4, top - 4, x + 4, top, "stone_lo"); cv.rect(x - 4, top - 4, x + 4, top - 4, "stone"); cv.rect(x - 4, top, x + 4, top, "lamp")


def tongs(cv, c):
    hx, hy = c["hand_back"]
    cv.seg(hx, hy, hx + 1, hy + 5, 2, 2, ("stone", "stone_lo", "shadow")); cv.set(hx + 1, hy + 6, "lamp")


def hood(cv, c):
    """ashen cultist's hood: ash-grey cloth over head and shoulders, a dark face-gap with two ember eyes"""
    hcx, hcy, hhw, hh = c["hcx"], c["hcy"], c["hhw"], c["hh"]
    cv.ell(hcx, hcy - hh * .12, hhw * 1.18, hh * 1.12, lambda u, v: "stone_hi" if (u < -.35 and v < .2) else "stone_lo" if (u > .55 or v > .8) else "stone")
    if not c["back"]:
        cv.ell(hcx - (hhw * .15 if c["side"] else 0), hcy + hh * .12, hhw * (.55 if c["side"] else .65), hh * .62, "shadow")
        for dx in ((-.3, .3) if not c["side"] else (-.45,)):
            cv.set(hcx + dx * hhw, hcy + hh * .08, "lamp")


def sash(cv, c):
    y = c["beltY"]
    cv.rect(c["CX"] - c["hw"], y - 1, c["CX"] + c["hw"], y + 2, "roof_hi")
    cv.rect(c["CX"] - c["hw"], y + 2, c["CX"] + c["hw"], y + 2, "roof_lo")
    if not c["back"]:
        cv.rect(c["CX"] + c["hw"] * .3, y + 3, c["CX"] + c["hw"] * .3 + 2, y + 7, "roof_hi")


def shield_front(cv, c):
    """Dagny's round shield on the off arm (leather + copper boss)"""
    hx, hy = c["hand_back"]
    cv.ell(hx - (0 if c["side"] else 3), hy - 3, 7 * c["k"] * .5 + 3, 7 * c["k"] * .5 + 3, lambda u, v: "lamp" if u * u + v * v < .08 else "roof_hi" if u < -.3 else "roof_lo" if u > .5 else "roof")


NPCS = {
 "envoy_mp": dict(scale=1.0, folk=True, desc="Envoy Sunndis Embervane (ember-kin, 1x): sand linen tunic, belted charcoal trousers, red sash, ember veins, blunt.",
   P=dict(skin="ember", hair="roof_lo", hairstyle="short", tunic="cream", trousers="black", belt=("roof_hi", "roof_lo"), buckle="lamp", extra=combine(veins, sash), cheeks=False)),
 "springkeeper": dict(scale=1.0, folk=True, desc="Yrsa Brightwell (ember-kin springkeeper, 1x): grey wrap tunic, belted skirt over leggings, hair in a bun.",
   P=dict(skin="ember", hair="timber", hairstyle="bun", tunic="grey", trousers="black", skirt="ashgrey", extra=veins, cheeks=False)),
 "lizardman": dict(scale=1.0, folk=True, desc="Orm Kettlebrand (lizard-keeper, 1x): quilted leather jerkin over a rust tunic, rope-belted trousers, short beard.",
   P=dict(skin="ember", hair="timber_lo", hairstyle="short", beard="short", beard_c=R["leather"], tunic="rust", jerkin="leather", trousers="black", belt=("plaster_lo", "timber"), extra=veins, cheeks=False)),
 "mp_trader": dict(scale=1.0, folk=True, desc="Svala (spice trader, 1x): layered tunics (rust under sand), a wide belt hung with pouches, topknot.",
   P=dict(skin="ember", hair="roof", hairstyle="topknot", tunic="rust", jerkin="cream", trousers="black", belt=("timber", "ink"), extra=combine(veins, pouches), width=1.1, cheeks=False)),
 "mp_guide": dict(scale=1.0, folk=True, desc="Grettir (ex-cultist guide, 1x): ash-grey tunic, belted trousers, burn-scarred arms.",
   P=dict(skin="ember", hair="stone_lo", hairstyle="short", tunic="ashgrey", trousers="black", belt=("timber_lo", "ink"), extra=combine(veins, scars), cheeks=False)),
 "warden_mp": dict(scale=2.6, desc="Ember-Warden Aska Cindervane (fire-giant, 2.6x): rust leather tunic, belted kilt-trousers, copper circlet, long grey braids.",
   P=dict(skin="ruddy", hair="grey", hairstyle="braids", tunic="rust", trousers="leather", skirt="rust", extra=combine(veins, copper_circlet), width=1.1, cheeks=False)),
 "forgejudge": dict(scale=2.5, desc="Torka Ashgrip (fire-giant forge-judge, 2.5x): leather apron over a sand tunic, belted trousers, rolled sleeves, contest hammer, tongs.",
   P=dict(skin="ruddy", hair="grey", hairstyle="topknot", beard="braids", beard_c=R["grey"], tunic="cream", trousers="black", apron="leather", sleeves="cream", extra=combine(veins, hammer, tongs), width=1.15, cheeks=False)),
 "cindercaptain": dict(scale=2.5, desc="Cinder-Captain Dagny Flameguard (fire-giant, 2.5x): leather jerkin over a belted tunic, belted trousers, round shield and short spear. No plate.",
   P=dict(skin="ruddy", hair="roof", hairstyle="braids", tunic="rust", trousers="black", jerkin="leather", extra=combine(veins, spear, shield_front), cheeks=False)),
}


def roles(folk=False):
    out = {}
    for n, r in NPCS.items():
        if bool(r.get("folk")) != folk:
            continue
        out[n] = dict(draw=giant(r["P"], Ht(r["scale"])), scale=r["scale"], desc=r["desc"], anims=A2, named=True,
                      stats_hint={"tier": "npc", "height_x_player": r["scale"]})
    return out
