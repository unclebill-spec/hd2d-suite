"""Niflheim folk (story 5 roster, ice-kin, human-sized 1x): real tunics, belts, belted trousers, boots. Hrefna Frostveil (companion) is a separate sheet.
Palette only: the cold glow of lanterns / rune cuffs is fx + light, the sprite uses sky / white / flower_blue."""
from nf_common import R, Cv
from nf_giant import giant

FRAME_FOLK = (40, 44)
A2 = ("idle", "walk")


def Ht(scale):
    return round(29 * scale) - 2


def combine(*fs):
    def f(cv, c):
        for g in fs:
            g(cv, c)
    return f


def scarf(col=("sky", "flower_blue", "cloth")):
    def f(cv, c):
        sh, CX, hw, Ht_ = c["sh"], c["CX"], c["hw"], c["Ht"]
        cv.rect(CX - hw * .55, sh - 1, CX + hw * .55, sh + 1, col[1])
        cv.rect(CX - hw * .55, sh - 1, CX + hw * .55, sh - 1, col[0])
        if not c["back"]:
            x = CX + hw * (.3 if not c["side"] else -.3)
            cv.rect(x, sh + 1, x + 2, sh + Ht_ * .28, col[1]); cv.rect(x, sh + Ht_ * .28 - 1, x + 2, sh + Ht_ * .28, col[2])
    return f


def lantern(cv, c):
    """cold-fire hand lantern: iron frame, sky / white flame (glow = fx)"""
    hx, hy = c["hand_back"] if not c["side"] else c["hand"]
    x, y = hx - (1 if not c["side"] else -1), hy + 3
    cv.rect(x - 2, y - 3, x + 2, y + 3, "stone_lo")
    cv.rect(x - 1, y - 2, x + 1, y + 2, "sky"); cv.set(x, y - 1, "white"); cv.set(x, y, "white")
    cv.rect(x - 2, y - 4, x + 2, y - 4, "stone"); cv.set(x, y - 5, "stone_lo")


def belt_lantern(cv, c):
    x, y = c["CX"] - c["hw"] * (.95 if not c["back"] else -.95), c["beltY"] + 2
    cv.rect(x - 1, y, x + 1, y + 3, "stone_lo"); cv.set(x, y + 1, "white"); cv.set(x, y + 2, "sky")


def runecuffs(cv, c):
    for hx, hy in c["hands"]:
        cv.rect(hx - 1, hy - 2, hx + 1, hy - 2, "sky")
        cv.set(hx, hy - 3, "white")


def coat(cv, c):
    """long violet-black coat worn OPEN: panels either side of the hips to the knee, tunic + belt still visible in front"""
    CX, hw, beltY, hip, Ht_ = c["CX"], c["hw"], c["beltY"], c["hip"], c["Ht"]
    side, back = c["side"], c["back"]
    ylo = hip + Ht_ * .26
    for y in range(int(c["sh"] + 1), int(ylo)):
        t = max(0, (y - beltY) / max(1, ylo - beltY))
        for sd in ((-1, 1) if not side else (1,)):
            a = CX + sd * hw * (.55 if y < beltY else .5 + .55 * t)
            b = CX + sd * hw * (1.05 + .12 * t)
            if side:
                a, b = CX + 1, CX + hw * (1.0 + .2 * t)
            if back:
                a, b = CX - hw * 1.05, CX + hw * 1.05
            for x in range(int(min(a, b)), int(max(a, b)) + 1):
                if (not back) and y < beltY - 1 and abs(x - CX) < hw * .7:
                    continue
                cv.set(x, y, "shadow" if abs(x - CX) > hw * .8 else "cloth")
    for x in range(int(CX - hw * 1.05), int(CX + hw * 1.05)):
        cv.set(x, ylo, "ink") if (x // 2) % 2 == 0 else None


def mantle(cv, c):
    """ash-grey wool mantle over the shoulders"""
    CX, sh, hw = c["CX"], c["sh"], c["hw"]
    cv.ell(CX, sh + 1, hw * 1.12, c["Ht"] * .085, lambda u, v: "stone_hi" if (u < -.3 and v < 0) else "stone_lo" if v > .3 else "stone")


def inkstains(cv, c):
    for hx, hy in c["hands"]:
        cv.set(hx, hy, "cloth"); cv.set(hx, hy - 1, "shadow")
    cv.set(c["CX"] + 1, c["sh"] + 5, "cloth"); cv.set(c["CX"] - 2, c["sh"] + 8, "shadow")


def pouches(cv, c):
    for dx in (-1.0, 0.65, 0.95):
        x, y = c["CX"] + c["hw"] * dx, c["beltY"] + 2
        cv.rect(x - 2, y, x + 2, y + 5, "timber"); cv.rect(x - 2, y, x + 2, y, "timber_hi"); cv.rect(x - 2, y + 5, x + 2, y + 5, "timber_lo")
        cv.set(x, y + 1, "flower_gold")


def crook(cv, c):
    hx, hy = c["hand"]
    x = hx + 2
    top = hy - c["Ht"] * .6
    cv.seg(x, hy + 2, x, top, 2, 2, ("timber_hi", "timber", "timber_lo"))
    cv.seg(x, top, x - 4, top - 1, 2, 2, ("timber_hi", "timber", "timber_lo")); cv.set(x - 5, top + 1, "timber")


def hood(cv, c):
    """frost-warden hood: grey-blue cloth over head and shoulders, dark face-gap, two pale-blue eyes"""
    hcx, hcy, hhw, hh = c["hcx"], c["hcy"], c["hhw"], c["hh"]
    cv.ell(hcx, hcy - hh * .12, hhw * 1.18, hh * 1.12, lambda u, v: "stone_hi" if (u < -.35 and v < .2) else "flower_blue" if (u > .55 or v > .8) else "stone")
    if not c["back"]:
        cv.ell(hcx - (hhw * .15 if c["side"] else 0), hcy + hh * .12, hhw * (.55 if c["side"] else .65), hh * .62, "shadow")
        for dx in ((-.3, .3) if not c["side"] else (-.45,)):
            cv.set(hcx + dx * hhw, hcy + hh * .08, "sky")


def icelance(cv, c):
    hx, hy = c["hand"]
    x = hx + 3
    top = hy - c["Ht"] * .9
    cv.seg(x, hy + 3, x, top, 2, 2, ("timber_hi", "timber", "timber_lo"))
    cv.poly([(x - 2, top), (x + 2, top), (x, top - max(6, c["Ht"] * .22))], lambda a, b: "white" if a < x else "sky")


def frostshield(cv, c):
    hx, hy = c["hand_back"]
    r = 2 + c["k"] * 1.6
    cv.ell(hx - (0 if c["side"] else 3), hy - 3, r, r, lambda u, v: "white" if u * u + v * v < .08 else "sky" if u < -.3 else "flower_blue" if u > .5 else "plaster_hi")


def iceblades(cv, c):
    """Brisa's twin ice blades"""
    for hx, hy in c["hands"]:
        L = c["Ht"] * (.34 + .08 * c["at"])
        cv.seg(hx, hy, hx + (1 if hx > c["CX"] else -1), hy - L, 2, 1, ("white", "sky", "flower_blue"))
        cv.rect(hx - 2, hy - 1, hx + 2, hy - 1, "stone_lo")


NPCS = {
 "gatewright": dict(scale=1.0, folk=True, desc="Halvard Rimegate (gatewright, 1x): calm; slate wool tunic under a leather jerkin, belted grey trousers, short grey beard, ash mantle.",
   P=dict(skin="pale", hair="stone", hairstyle="short", beard="short", beard_c=R["grey"], tunic="slate", jerkin="leather", trousers="grey", belt=("timber_lo", "ink"), extra=mantle, cheeks=False)),
 "frostspeaker": dict(scale=1.0, folk=True, desc="Gudrun Hoarwick (frost-speaker, 1x): grey wool tunic, belted slate trousers, long pale braid to the waist, rune cuffs (blue glow = fx).",
   P=dict(skin="pale", hair="pale", hairstyle="braids", tunic="grey", trousers="slate", belt=("stone_lo", "ink"), buckle="sky", extra=combine(runecuffs, crook), cheeks=False)),
 "veyra": dict(scale=1.2, folk=True, desc="Veyra Ashmantle (the Rift-Warden before the rime-plate, 1.2x): violet-black long coat worn open over a pale tunic + belt, belted trousers, ash-grey mantle, small belt lantern. Before the rime-plate.",
   P=dict(skin="pale", hair=("stone", "stone_lo", "shadow"), hairstyle="long", tunic="cream", trousers="coat", belt=("stone_lo", "ink"), buckle="sky", extra=combine(mantle, coat, belt_lantern), cheeks=False, brow="shadow")),
 "eira": dict(scale=1.0, folk=True, desc="Eira (Veyra's sister, memory, 1x): pale belted tunic, belted trousers, hand lantern; glowing-outline = fx (eira_outline), shown only in memories.",
   P=dict(skin="pale", hair="pale", hairstyle="braids", tunic="frostwool", trousers="pale", belt=("stone_lo", "ink"), buckle="sky", extra=lantern, cheeks=False)),
 "nf_trader": dict(scale=1.0, folk=True, desc="Tove Lanternwright (trader, 1x): layered tunics (slate under sand), wide belt hung with pouches, knit cap look via short hair.",
   P=dict(skin="pale", hair="timber", hairstyle="short", tunic="slate", jerkin="cream", trousers="grey", belt=("timber", "ink"), extra=pouches, width=1.1, cheeks=False)),
 "elkman": dict(scale=1.0, folk=True, desc="Ketil Icehook (elk-keeper, 1x): quilted leather jerkin over a grey tunic, rope-belted trousers, short beard, crook.",
   P=dict(skin="pale", hair="timber_lo", hairstyle="short", beard="short", beard_c=R["leather"], tunic="grey", jerkin="leather", trousers="slate", belt=("plaster_lo", "timber"), extra=crook, cheeks=False)),
 "archivist": dict(scale=1.0, folk=True, desc="Vigdis Stillwater (archivist, 1x): ink-stained wrap tunic, belted trousers, hair in a bun.",
   P=dict(skin="pale", hair="stone", hairstyle="bun", tunic="cream", trousers="slate", belt=("timber_lo", "ink"), extra=inkstains, cheeks=False)),
 "brisa": dict(scale=1.0, folk=True, desc="Warden-Captain Brisa Rimeheart (guard captain NPC, 1x; same look as the 3x mini-boss): leather jerkin over a grey-blue belted tunic, belted trousers, small frost shield.",
   P=dict(skin="pale", hair="timber_lo", hairstyle="braids", tunic="slate", jerkin="leather", trousers="grey", belt=("timber_lo", "ink"), extra=frostshield, cheeks=False)),
}


def roles(folk=False):
    out = {}
    for n, r in NPCS.items():
        if bool(r.get("folk")) != folk:
            continue
        out[n] = dict(draw=giant(r["P"], Ht(r["scale"])), scale=r["scale"], desc=r["desc"], anims=A2, named=True,
                      stats_hint={"tier": "npc", "height_x_player": r["scale"]})
    return out


HREFNA = dict(skin="pale", hair="pale", hairstyle="braids", tunic="slate", trousers="grey", skirt="icedeep", belt=("timber_lo", "ink"), buckle="sky",
              boots=("stone_lo", "ink"), extra=combine(scarf(), lantern), cheeks=False, width=.96)


def hrefna_roles():
    return {"hrefna": dict(draw=giant(HREFNA, Ht(1.0)), scale=1.0, anims=("idle", "walk", "cast"), named=True, kind="companion",
                           desc="Hrefna Frostveil (companion, 1x): slate tunic, short belted skirt over grey leggings, boots, blue scarf, cold-fire hand lantern (glow = fx / light). follow = walk, cast = ice lance / mist veil. NO pet in this realm.",
                           light={"color": "#3fb8ff", "intensity": 1.1, "range": 6.0}, stats_hint={"tier": "companion", "height_x_player": 1.0})}
