"""Ulfar Mossback (companion), frost trolls, golems, berserkers, rares + mini-boss. All native-scale, palette only."""
from jt_common import R
from jt_giant import giant
from jt_golem import golem
from jt_npcs import combine

# --------------------------------------------------------------- props
def boulder(cv, x, y, r):
    cv.ell(x, y, r, r * .85, lambda u, v: "plaster_hi" if (v < -.6) else "stone_hi" if u < -.3 else "stone_lo" if (u > .4 or v > .6) else "stone")
    cv.set(x - r * .3, y, "stone_lo"); cv.set(x + r * .2, y + r * .3, "shadow")


def ulfar_extra(cv, c):
    """moss tufts + a patch on the knee; boulder overhead while tossing"""
    k = c["k"]
    for dx, dy in ((-.6, -.95), (.5, -1.0), (.05, -1.08)):
        cv.ell(c["hcx"] + dx * c["hhw"], c["hcy"] + dy * c["hh"], 2.5 * k * .5 + 1, 2 * k * .5 + 1, lambda u, v: "grass_hi" if u < 0 else "moss")
    if not c["back"] and not c["side"]:
        for sd in (-1, 1):                                       # knee patch + mitten-less hands
            x, y = c["CX"] + sd * c["hw"] * .52, c["G"] - c["Ht"] * .22
            cv.rect(x - 2, y, x + 1, y + 3, "plaster_lo"); cv.set(x, y + 1, "timber_lo")
    if c["at"] and c["anim"] == "attack" and c["i"] in (1, 2):
        if c["side"]:
            cv.ell(c["hcx"] - 10 * k * .3, c["hcy"] - c["hh"] - 8, 8 * k * .4 + 4, 7 * k * .4 + 3, "stone")
            boulder(cv, c["hcx"] - 4, c["hcy"] - c["hh"] - 9, 9)
        else:
            boulder(cv, c["CX"], c["hcy"] - c["hh"] - 8, 11)
    if c["anim"] == "cast" and c["ca"] > .5 and not c["side"]:   # shield hug: both arms wide, a ring of moss-light
        for sd in (-1, 1):
            cv.set(c["CX"] + sd * (c["hw"] + 12), c["sh"] + 11, "white")


def club(cv, c):
    hx, hy = c["hand"]
    k = c["k"]
    if c["at"]:
        x0, y0 = hx + (2 if not c["side"] else -2), hy
        x1, y1 = x0 + (4 if not c["side"] else -6) * 1, y0 - c["Ht"] * .55
    else:
        x0, y0 = hx + 2, hy + 2
        x1, y1 = x0 + (4 if not c["side"] else -3), y0 - c["Ht"] * .42
    cv.seg(x0, y0, x1, y1, 3, 3, ("timber_hi", "timber", "timber_lo"))
    cv.ell(x1, y1, 5 * k * .55 + 1, 5 * k * .6 + 1, lambda u, v: "white" if (u < -.3 and v < 0) else "sky" if u < .5 else "flower_blue")
    cv.set(x1 + 1, y1 - 1, "white")


def axes(big):
    def f(cv, c):
        k = c["k"]
        for h, sd in ((c["hand"], 1), (c["hand_back"], -1)):
            hx, hy = h
            if c["side"] and sd < 0:
                continue
            up = c["at"] * c["Ht"] * .28
            x0, y0 = hx + sd * 1, hy + 2
            x1, y1 = x0 + sd * 1, y0 - c["Ht"] * .42 - up * .3
            cv.seg(x0, y0, x1, y1, 2, 2, ("timber_hi", "timber", "timber_lo"))
            w = (7 if big else 5)
            cv.poly([(x1 - sd * 1, y1 - 1), (x1 + sd * w, y1 - 3 - (2 if big else 1)), (x1 + sd * w, y1 + 5 + (2 if big else 1)), (x1 - sd * 1, y1 + 3)],
                    lambda a, b: "white" if abs(a - x1) < 2 else "sky" if abs(a - x1) < w - 1 else "flower_blue")
    return f


def tusks(cv, c):
    if c["back"]:
        return
    for sd in ((-1, 1) if not c["side"] else (-1,)):
        x = c["hcx"] + sd * c["hhw"] * (.45 if not c["side"] else .85)
        y = c["hcy"] + c["hh"] * .55
        cv.rect(x, y, x, y - 3, "plaster_hi"); cv.set(x, y - 4, "white")


def ice_tufts(cv, c):
    """frost-spiked scalp: ice crystals instead of hair"""
    for dx in (-.6, -.15, .35, .75):
        x, y = c["hcx"] + dx * c["hhw"], c["hcy"] - c["hh"] * .95
        cv.poly([(x - 1, y + 2), (x + 1, y + 2), (x + (.5 if dx > 0 else -.5), y - 3 - c["k"])], lambda a, b: "white" if a <= x else "sky")


def whelp_sack(cv, c):
    """Frostmother: a swaddled whelp bundle on her back (calls troll whelps)"""
    if c["back"] or c["side"]:
        cv.ell(c["CX"] + (6 if c["side"] else 0), c["sh"] + c["Ht"] * .2, 8, 9, lambda u, v: "plaster_hi" if u < -.3 else "plaster_lo" if u > .5 else "plaster")
        cv.set(c["CX"] + (6 if c["side"] else 0), c["sh"] + c["Ht"] * .13, "sky")


TROLL = dict(skin=("sky", "flower_blue", "cloth"), hair=None, bald=True, hairstyle="none", tunic="rust", trousers="leather", trim="plaster_lo",
             boots=("timber_lo", "ink"), belt=("timber", "ink"), width=1.22, hunch=.5, head=1.1, arms_w=1.35, legs_w=1.15, raise_=1.5, brow="cloth",
             cheeks=False, hem=.07)

ULFAR = dict(skin="ruddy", hair="timber", hairstyle="short", beard="short", beard_c=R["leather"], tunic="moss", trousers="leather", mantle="moss",
             width=1.15, hunch=.25, extra=ulfar_extra, raise_=1.7)

ENEM = {
 "frost_troll": dict(scale=1.6, P={**TROLL, "extra": combine(tusks, ice_tufts, club)}, desc="Frost troll (1.6x; gate foe at 2x): ice-blue hide, ragged tunic, belted rag trousers, tusks, throws ice chunks / swings an ice club.", tier="enemy"),
 "ice_golem": dict(scale=1.5, G="ice", desc="Ice golem (1.5x): translucent ice blocks round a glowing rune heart.", tier="enemy"),
 "avalanche_golem": dict(scale=1.8, G="avalanche", desc="Avalanche golem (1.8x): a snow-capped boulder that unfolds into a golem; attack = rolls as a ball.", tier="enemy"),
 "rime_berserker": dict(scale=1.8, P=dict(skin="ruddy", hair="grey", hairstyle="long", beard="braids", beard_c=R["grey"], tunic="grey", trousers="leather", mantle="darkfur",
        width=1.1, extra=axes(False), raise_=1.4), desc="Rime Berserker (elite, 1.8x): fur over a belted tunic, belted trousers, two ice axes, wild braids.", tier="elite"),
}
ELITE = {
 "frostmother": dict(scale=2.5, P={**TROLL, "tunic": "moss", "trousers": "slate", "mantle": "snowfur", "width": 1.3, "extra": combine(tusks, ice_tufts, club, whelp_sack)},
                     desc="Frostmother (rare, 2.5x): frost troll matriarch in a belted fur tunic, an ice club, a whelp bundle on her back.", tier="rare"),
 "avalanche": dict(scale=3.0, G="avalanche", desc="Avalanche (rare, 3x): an avalanche golem the size of a house; a rolling boulder that unfolds.", tier="rare"),
 "ormgar": dict(scale=3.0, P=dict(skin="ruddy", hair="roof", hairstyle="long", beard="braids", beard_c=R["rust"], tunic="rust", trousers="leather", mantle="brownfur",
        width=1.25, extra=axes(True), raise_=1.4, belt=("timber", "ink")), desc="Rime Berserker Chief Ormgar (mini-boss, 3x): bear fur over a belted tunic, two big ice axes, frenzy at 50%.", tier="miniboss"),
}


def Ht(s):
    return round(29 * s) - 2


def make(d, anims, kind="enemy"):
    out = {}
    for n, r in d.items():
        dr = golem(r["G"], Ht(r["scale"])) if r.get("G") else giant(r["P"], Ht(r["scale"]))
        out[n] = dict(draw=dr, scale=r["scale"], desc=r["desc"], anims=anims, kind=kind, enemy=True, stats_hint={"tier": r["tier"], "height_x_player": r["scale"]})
    return out


def ulfar_roles():
    return {"ulfar": dict(draw=giant(ULFAR, Ht(3.0)), scale=3.0, combat_scale=2.4, kind="human", named=True,
            desc="Ulfar Mossback (companion; 3x in town, 2.4x in combat): gentle giant, moss-green tunic, patched belted trousers, moss on his shoulders. cast = shield hug, attack = boulder toss.",
            anims=("idle", "walk", "cast", "attack"), stats_hint={"tier": "companion"}, notes="hums when idle; faint: sits down, returns at the waystone")}
