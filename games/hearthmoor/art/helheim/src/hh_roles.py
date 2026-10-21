"""Helheim roles per story/helheim.md (5, 7, 8, 9.5). Engine reused from the Asgard pack (as_* modules). Palette only (no violet exists in the sprite
palette: violet tabards / chains / smoke are drawn with the blue-shadow ramp flower_blue / cloth / shadow; the real violet #a45cf0 / #3a2458 glow is fx + light).
Ghosts: faded clothes, feet fading into a mist dither (colour-only). No gore, nothing wet: garnet golems are red glass, skeletons clean bone."""
import math
from as_common import R
import as_common as C
from as_giant import giant
from as_beasts import wraith, elemental, bat
from as_golem import golem
import as_npcs as N
from as_npcs import combine, cloak, mantle, lamp, gloves, sash, tabard
import as_boss as B

FRAME_FOLK = (40, 44)
A2 = ("idle", "walk")
A4 = ("idle", "walk", "attack", "die")
PALc = C.H.PAL.c


def Ht(s):
    return round(29 * s) - 2


def remap(draw, M):
    hx = {PALc[a]: PALc[b] for a, b in M.items()}
    def d(cv, face, anim, i):
        draw(cv, face, anim, i)
        for row in cv.s.p:
            for x, v in enumerate(row):
                if v is not None and v in hx:
                    row[x] = hx[v]
    for k in ("fall", "die_mode", "sink_cols"):
        if hasattr(draw, k):
            setattr(d, k, getattr(draw, k))
    return d


VIO, VIO_D = "#a45cf0", "#3a2458"


def vt(draw, violet):
    """knight tabard: palette cloth / flower_blue -> true violet on the main sheet; the _safe twin keeps blue-shadow"""
    return hexmap(draw, {PALc["cloth"]: VIO, PALc["flower_blue"]: VIO_D}) if violet else draw


def hexmap(draw, M):
    """post-draw hex swap (used for the true-violet sheets: palette names -> NEON violet)"""
    def d(cv, face, anim, i):
        draw(cv, face, anim, i)
        for row in cv.s.p:
            for x, v in enumerate(row):
                if v is not None and v in M:
                    row[x] = M[v]
    for k in ("fall", "die_mode", "sink_cols"):
        if hasattr(draw, k):
            setattr(d, k, getattr(draw, k))
    return d


def ghostly(draw, ht, faded=True):
    """faded clothes + feet fading into mist (colour dither in the bottom ~16% of the figure)"""
    FADE = {"timber": "stone", "timber_lo": "stone_lo", "timber_hi": "stone_hi", "roof": "flower_rose", "roof_lo": "roof", "skin": "plaster_hi", "skin_lo": "plaster",
            "grass": "sky", "moss": "flower_blue"} if faded else {}
    d0 = remap(draw, FADE)
    W, S = PALc["white"], PALc["sky"]
    def d(cv, face, anim, i):
        d0(cv, face, anim, i)
        G = cv.h - 2; top = G - int(ht * .16)
        for y in range(top, cv.h):
            row = cv.s.p[y]
            for x, v in enumerate(row):
                if v is not None:
                    row[x] = W if (x + y + i) % 2 == 0 else S
    for k in ("fall", "die_mode", "sink_cols"):
        if hasattr(d0, k):
            setattr(d, k, getattr(d0, k))
    return d


def half_shadow(draw, ht):
    """Hel: one half of the face lit (violet = light/fx), the other in shadow"""
    sk = {PALc["skin"]: PALc["skin_lo"], PALc["plaster_hi"]: PALc["plaster_lo"], PALc["skin_lo"]: PALc["shadow"]}
    def d(cv, face, anim, i):
        draw(cv, face, anim, i)
        if face in ("up",):
            return
        G = cv.h - 2; CX = cv.w // 2
        for y in range(G - ht, G - int(ht * .78)):
            row = cv.s.p[y]
            for x in range(CX if face != "left" else 0, cv.w):
                if row[x] in sk:
                    row[x] = sk[row[x]]
    return d


def coat(col=("shadow", "ink", "ink"), line="roof"):
    def f(cv, c):
        B.coat_tails(cv, c, col, line)
    return f


def specs(cv, c):
    if c["back"]:
        return
    y = int(c["hcy"]); cv.set(c["hcx"] - c["hhw"] * .4, y, "stone_hi"); cv.set(c["hcx"] + c["hhw"] * .4, y, "stone_hi")


def quill(cv, c):
    cv.set(c["hcx"] + c["hhw"] + 1, c["hcy"] - 2, "white"); cv.set(c["hcx"] + c["hhw"] + 1, c["hcy"] - 1, "plaster_hi"); cv.set(c["hcx"] + c["hhw"] + 2, c["hcy"] - 3, "white")


def pole_lantern(cv, c):
    hx, hy = c["hands"][-1]
    cv.rect(hx, hy - c["Ht"] * .55, hx, hy + 2, "timber")
    y = hy - c["Ht"] * .55
    cv.rect(hx - 1, y, hx + 1, y + 2, "sky"); cv.set(hx, y + 1, "white"); cv.set(hx, y - 1, "stone_lo")


def ledger(cv, c):
    hx, hy = c["hands"][0]
    cv.rect(hx - 2, hy - 3, hx + 1, hy + 1, "shadow"); cv.rect(hx - 1, hy - 2, hx, hy, "plaster_hi")


def apron(col="plaster"):
    def f(cv, c):
        if c["back"]:
            return
        CX, hw = c["CX"], c["hw"]
        cv.rect(CX - hw * .55, c["beltY"] + 1, CX + hw * .55, c["hip"] + c["Ht"] * .12, col)
    return f


NPCS = {
 "hel": dict(scale=1.25, desc="Hel (1.25x, tall): half violet-lit, half shadow; dark violet tunic, silver-belted skirt over leggings, grey mantle, carries the Ledger.",
   P=dict(skin="pale", hair="shadow", hairstyle="long", tunic="slate", skirt="slate", trousers="darkfur", belt=("stone_hi", "stone"), buckle="white",
          extra=combine(mantle(("stone_hi", "stone", "stone_lo")), ledger)), fx="half face shadow (palette); violet light = fx hel_light"),
 "ferryman": dict(scale=1.0, desc="Corvin Lanternmere (ferryman, raven-keeper): long grey coat over a tunic, rope-belted trousers, a pole-lantern.",
   P=dict(skin="skin", hair="stone", hairstyle="short", beard="short", beard_c=R["grey"], tunic="slate", trousers="grey", belt=("plaster_lo", "timber"),
          extra=combine(coat(("stone_hi", "stone", "stone_lo"), "stone_lo"), pole_lantern))),
 "innghost": dict(scale=1.0, ghost=True, desc="Hettie Tallow (ghost innkeeper): faded apron over a rose tunic, belted skirt; feet fade into mist.",
   P=dict(skin="skin", hair="stone_hi", hairstyle="bun", tunic="rust", skirt="grey", trousers="grey", belt=("timber_lo", "ink"), extra=apron(), width=1.12)),
 "archivist_hh": dict(scale=1.0, desc="Quillon Greymarch (archivist): ink-stained tunic, belted trousers, spectacles, a quill behind his ear.",
   P=dict(skin="skin", hair="timber_lo", hairstyle="short", tunic="cream", trousers="slate", belt=("timber_lo", "ink"), extra=combine(specs, quill))),
 "eira_spirit": dict(scale=1.0, ghost=True, desc="Eira Ashmantle (spirit, never fought): pale tunic, belted, cold-fire lantern; soft glowing outline = fx eira_outline.",
   P=dict(skin="skin", hair="plaster_hi", hairstyle="braids", tunic="cream", trousers="grey", skirt="pale", belt=("stone", "stone_lo"), extra=lamp)),
 "childghost": dict(scale=0.8, ghost=True, desc="Hollin (child ghost, 0.8x): oversized tunic, rope belt, bare feet fading into mist; collects buttons.",
   P=dict(skin="skin", hair="timber", hairstyle="short", tunic="slate", trousers="grey", belt=("plaster_lo", "timber"), width=1.15)),
 "bakerghost": dict(scale=1.0, ghost=True, desc="Old Marrow (baker ghost): flour-dusted tunic and apron, belted trousers.",
   P=dict(skin="skin", hair="plaster_hi", hairstyle="short", beard="short", beard_c=R["snowfur"], tunic="cream", trousers="grey", belt=("timber_lo", "ink"), extra=apron("white"), width=1.15)),
 "sailorghost": dict(scale=1.0, ghost=True, desc="the ghost sailor (story 2, gs_sailor): faded blue tunic, belted trousers, knit cap.",
   P=dict(skin="skin", hair="timber", hairstyle="short", tunic="slate", trousers="grey", belt=("timber_lo", "ink"))),
 "gloam_folk": dict(scale=1.0, ghost=True, desc="Gloamhaven folk ghost (ambient 5.9): faded tunic, belted skirt over leggings, shawl.",
   P=dict(skin="skin", hair="timber_hi", hairstyle="braids", tunic="moss", skirt="grey", trousers="grey", belt=("timber_lo", "ink"), extra=mantle(("plaster_hi", "plaster", "plaster_lo")))),
}


def folk_roles():
    out = {}
    for n, r in NPCS.items():
        h = Ht(r["scale"]); d = giant(r["P"], h)
        if r.get("ghost"):
            d = ghostly(d, h)
        if n == "hel":
            d = half_shadow(d, h)
        out[n] = dict(draw=d, scale=r["scale"], desc=r["desc"], anims=A2, named=True, stats_hint={"tier": "npc", "height_x_player": r["scale"]})
    return out


# ---------------------------------------------------------------- Inkling (pet, 9.5): small black gloam raven, violet-tipped (blue-shadow tips in palette)
def raven(ht):
    def draw(cv, face, anim, i):
        G = cv.h - 2; CX = cv.w // 2
        side, back = face == "left", face == "up"
        hop = [0, 1, 0, 0][i] if anim == "idle" else [0, 2, 3, 1][i]
        flap = (anim == "walk" and i in (1, 2))
        by = G - ht * .45 - hop
        cv.ell(CX, by, ht * (.32 if side else .26), ht * .24, lambda u, v: "shadow" if u < -.3 and v < 0 else "ink")
        hx = CX - ht * .22 if side else CX
        cv.ell(hx, by - ht * .28, ht * .15, ht * .14, lambda u, v: "shadow" if u < -.2 else "ink")
        if not back:
            if side:
                cv.poly([(hx - ht * .14, by - ht * .3), (hx - ht * .3, by - ht * .26), (hx - ht * .14, by - ht * .23)], "stone_lo")
                cv.set(hx - ht * .04, by - ht * .31, "flower_gold")
            else:
                cv.rect(hx - 1, by - ht * .25, hx, by - ht * .2, "stone_lo")
                cv.set(hx - ht * .07, by - ht * .31, "flower_gold"); cv.set(hx + ht * .07, by - ht * .31, "flower_gold")
        tx = CX + ht * .3 if side else CX
        cv.poly([(tx - 2, by + ht * .1), (tx + 2, by + ht * .1), (tx + (ht * .2 if side else 0), by + ht * .32)], lambda a, b: "ink")
        for sd in ((-1,) if side else (-1, 1)):
            wy = by - (ht * .2 if flap else 0)
            x0 = CX + sd * ht * .18
            cv.poly([(x0, wy - 2), (x0 + sd * ht * (.38 if flap else .18), wy + (-ht * .1 if flap else ht * .05)), (x0, wy + ht * .14)], lambda a, b: "ink")
            cv.set(x0 + sd * ht * (.36 if flap else .16), wy + (-ht * .1 if flap else ht * .05), "flower_blue")
            cv.set(x0 + sd * ht * (.3 if flap else .12), wy + (-ht * .06 if flap else ht * .08), "cloth")
        for lx in ((CX - 2, CX + 2) if not side else (CX,)):
            cv.rect(lx, by + ht * .22, lx, G, "stone_lo"); cv.set(lx - 1, G, "stone_lo")
    return draw


def pet_roles():
    return {"inkling": dict(draw=raven(22), scale=0.6, anims=A2, named=True, kind="pet", stats_hint={"tier": "pet", "height_x_player": 0.6},
                            desc="Inkling (pet, gloam raven, 9.5): small black raven, violet-tipped feathers (palette blue-shadow tips; violet_motes fx = PETS.inkling.fx), gold eyes.")}


# ---------------------------------------------------------------- enemies (8.4) + gate shade (8.2)
SPIRIT = {"flower_gold": "sky", "lamp": "sky", "timber_hi": "flower_blue", "plaster_lo": "flower_blue", "plaster": "sky", "plaster_hi": "white"}
SHADE = {"flower_gold": "flower_blue", "lamp": "cloth", "timber_hi": "cloth", "plaster_lo": "cloth", "plaster": "flower_blue", "plaster_hi": "sky", "white": "plaster_hi"}
BONE = {"flower_gold": "flower_blue", "lamp": "sky"}
GARNET = {"plaster_hi": "roof_hi", "stone_hi": "roof_hi", "stone": "roof", "stone_lo": "roof_lo", "sky": "flower_rose", "white": "flower_rose", "flower_blue": "roof_hi",
          "cloth": "roof_lo", "shadow": "roof_lo", "plaster": "roof", "timber_hi": "roof", "timber": "roof_lo", "timber_lo": "shadow"}


def grave_lantern(ht):
    """walking iron lantern of blue cold fire on two clean bone legs (8.3 / 8.4)"""
    def draw(cv, face, anim, i):
        G = cv.h - 2; CX = cv.w // 2
        side = face == "left"; dead = anim == "die"
        st = [1, -1, 1, -1][i] if anim == "walk" else 0
        hgt = ht * (1 if not dead else [.9, .7, .5, .35][i])
        legtop = G - hgt * .38
        for sd, ph in ((-1, st), (1, -st)):
            x = CX + sd * ht * .1
            cv.seg(x, legtop, x + ph * 2, G, 2, 2, ("plaster_hi", "plaster", "stone_hi"))
        w = ht * (.2 if side else .24); top = G - hgt
        cv.rect(CX - w, top + hgt * .1, CX + w, legtop, "stone_lo")
        cv.rect(CX - w + 2, top + hgt * .14, CX + w - 2, legtop - 2, "sky")
        cv.rect(CX - w * .4, top + hgt * .22, CX + w * .4, legtop - hgt * .1, "white" if anim != "attack" or i % 2 == 0 else "sky")
        cv.rect(CX - w - 1, top + hgt * .08, CX + w + 1, top + hgt * .12, "shadow")
        cv.poly([(CX - w * .6, top + hgt * .08), (CX + w * .6, top + hgt * .08), (CX, top)], "shadow")
        cv.rect(CX - w - 1, legtop, CX + w + 1, legtop + 1, "shadow")
    return draw


def choir(ht):
    """the Hollow Choir: three fused wraiths in a column, singing (violet = fx)"""
    parts = [(0, 1.0), (-.22, .8), (.22, .8)]
    ws = [(dx, remap(wraith(int(ht * s)), SHADE)) for dx, s in parts]
    def draw(cv, face, anim, i):
        for dx, w in ws[1:] + ws[:1]:
            tmp = C.Cv(C.SP.HSprite(C.H.PAL, cv.w, cv.h)); w(tmp, face, anim, i)
            off = int(dx * ht * .6)
            for y, row in enumerate(tmp.s.p):
                for x, v in enumerate(row):
                    if v is not None and 0 <= x + off < cv.w:
                        cv.s.p[y][x + off] = v
    return draw


KNIGHT = dict(skin="skin", hair="timber_lo", hairstyle="short", tunic="slate", jerkin="leather", trousers="grey", belt=("timber_lo", "ink"), buckle="stone_hi",
              boots=("timber", "timber_lo"), extra=combine(tabard, N.spear))
KNIGHT_MAP = {"flower_gold": "cloth", "lamp": "flower_blue", "timber_hi": "timber", "timber": "timber_lo", "timber_lo": "shadow"}
LICH = dict(skin="pale", hair=None, bald=True, hairstyle="none", tunic="slate", trousers="grey", belt=("stone_hi", "stone"), buckle="sky", cheeks=False,
            extra=combine(cloak(("shadow", "ink", "ink")), N.hood("sky"), N.mace))
SKEL = dict(skin="pale", hair=None, bald=True, hairstyle="none", tunic="cream", trousers="cream", belt=("flower_blue", "cloth"), buckle="sky", cheeks=False, eyes="cloth",
            boots=("plaster_hi", "plaster"), extra=N.spear)


def foe(dr, s, desc, tier):
    return dict(draw=dr, scale=s, desc=desc, anims=A4, kind="enemy", enemy=True, stats_hint={"tier": tier, "height_x_player": s})


def enemy_roles(violet=True):
    return {
     "shade": foe(remap(wraith(Ht(1.0), halo=False), SHADE), 1.0, "Shade (1x): drifting blue-violet shape, fades in light.", "enemy"),
     "gate_shade": foe(remap(wraith(Ht(1.2), halo=False), SHADE), 1.2, "Gate shade (1.2x, Hel's Leave): tests the living-lamp; fades in light.", "gate"),
     "soul_wraith": foe(remap(wraith(Ht(1.3)), SPIRIT), 1.3, "Soul wraith (1.3x): neon-blue drifting wraith (palette sky/white; neon glow = fx soul_glow), drifts through walls.", "enemy"),
     "grave_lantern": foe(grave_lantern(Ht(1.0)), 1.0, "Grave lantern (1x): iron lantern of blue cold fire on clean bone legs; wakes as you pass.", "enemy"),
     "bone_elemental": foe(remap(golem("rock", Ht(1.6)), {"stone_lo": "plaster", "stone": "plaster_hi", "stone_hi": "white", "timber": "plaster_lo", "timber_lo": "stone", "timber_hi": "plaster"}), 1.6,
                           "Bone elemental (1.6x): clean pale bone, rune seams (violet = fx).", "enemy"),
     "garnet_golem": foe(remap(golem("rock", Ht(1.8)), GARNET), 1.8, "Garnet golem (1.8x, the 'blood golem'): dark red glass, slow; nothing wet.", "enemy"),
     "skeleton_line": foe(remap(giant(SKEL, Ht(1.0)), {"skin": "plaster_hi", "skin_lo": "plaster", "plaster_lo": "stone_hi"}), 1.0,
                          "Skeleton line (1x): clean pale bone with blue-violet rune belt, spear; march in step.", "enemy"),
     "lich": foe(remap(giant(LICH, Ht(1.4)), {"flower_gold": "stone", "lamp": "stone_hi", "timber_hi": "stone"}), 1.4, "Lich (1.4x): dark hooded robe over a belted tunic, pale-blue eyes, staff-mace.", "enemy"),
     "gloam_knight": foe(vt(remap(giant(KNIGHT, Ht(1.0)), KNIGHT_MAP), violet), 1.0, "Gloam Knight (elite 1x): dark leather jerkin + violet (palette blue-shadow) tabard, belted, spear; NO plate.", "elite"),
    }


VESP = dict(skin="pale", hair="ink", hairstyle="long", tunic="rust", trousers="darkfur", belt=("ink", "shadow"), buckle="stone_hi", eyes="roof_hi",
            extra=combine(coat(("shadow", "ink", "ink"), "roof_hi"), B.cape(("roof_hi", "roof", "roof_lo"), ("shadow", "ink", "ink"))), width=1.05)
ODRIC = dict(KNIGHT, hair="stone", beard="short", beard_c=R["grey"], width=1.1, extra=combine(tabard, B.gold_blade))


def elite_roles(violet=True):
    return {
     "vesperin": foe(giant(VESP, Ht(3.0)), 3.0, "MINI-BOSS Lord Vesperin (3x, O5): long black coat over a wine waistcoat + belted trousers, red-lined cape, red-lit eyes; NO plate. Mist-bat split = vesperin_bat.", "miniboss"),
     "vesperin_bat": foe(remap(bat(Ht(1.6)), SHADE), 1.6, "Vesperin's mist-bat (x3 at 50%): violet mist bat (palette blue-shadow); only the real one has hh_shadow.", "miniboss_add"),
     "odric": foe(vt(remap(giant(ODRIC, Ht(3.0)), dict(KNIGHT_MAP, flower_gold="cloth")), violet), 3.0, "Ser Odric Gravemantle (defiant mini-boss 3x): Gloam Knight, dark leather jerkin + violet tabard, greatsword; NO plate; yields at 25%.", "miniboss"),
     "gravelamp": foe(grave_lantern(Ht(2.0)), 2.0, "gravelamp (rare 2x): grave lantern elder, spits cold-fire wisps.", "rare"),
     "hollowchoir": foe(choir(Ht(3.0)), 3.0, "hollowchoir (rare 3x): chorus of fused wraiths in a column (violet = fx), dirge aura.", "rare"),
    }


# ---------------------------------------------------------------- Mordrath, the Pale Sovereign (boss 8x, 3 phases)
FRAME_BOSS = (144, 240)
BONEPLATE = ("plaster_hi", "plaster", "stone_hi", "stone")


def glaive(cv, c):
    hx, hy = c["hand"]; Ht = c["Ht"]; at = c["at"]
    top = hy - Ht * (.55 + .1 * at)
    cv.rect(hx - 1, top, hx, hy + Ht * .25, "stone_hi")
    cv.poly([(hx - 1, top), (hx + Ht * .09, top + Ht * .05), (hx + 1, top - Ht * .12)], lambda a, b: "plaster_hi" if a > hx else "plaster")
    cv.rect(hx - 2, top + 2, hx + 1, top + 3, "flower_gold")


def chains(cv, c):
    for hx, hy in c["hands"]:
        for k in range(5):
            cv.set(hx - 2 + (k % 2), hy - 4 - k * 3, "stone_hi"); cv.set(hx - 1 + (k % 2), hy - 5 - k * 3, "grass_hi")


def mordrath_P(phase):
    S = dict(ramp=BONEPLATE, leak="flower_gold" if phase < 3 else "roof_hi", gem="roof_hi", coat=None)
    return dict(skin="pale", hair=("ink", "shadow", "shadow"), hairstyle="long", tunic="darkfur", trousers="darkfur", belt=("ink", "shadow"), buckle="flower_gold",
                eyes="roof_hi", width=1.06, head=1.0, plate=B.plate(S),
                extra=combine(B.cape(("grass_hi", "grass", "ink"), ("grass", "ink", "ink")), B.crown(3 if phase == 3 else 1), chains, glaive),
                raise_=1.2, brow="shadow", trim="ink", cheeks=False, hem=.08, legs_w=1.1, arms_w=1.15)


CROWN_RED = {"sky": "roof_hi", "flower_blue": "roof", "white": "flower_rose"}


def boss_roles(violet=True):
    s = 8.0; ht = Ht(s)
    hint = {"tier": "boss", "height_x_player": s, "plate": True, "element": "dark", "phases": 3}
    out = {}
    descs = {1: "P1 (100-60%): glaive sweeps (violet arc tell), name-chains (red floor line).",
             2: "P2 (60-25%): hunts (red ring + lunge), calls 2 shades + 1 soul_wraith; the dome dims.",
             3: "P3 (25-0%): pulls names to heal (violet motes), crown flares (red half-arena ring); crown taller, gold trim burns red."}
    for ph in (1, 2, 3):
        g = giant(mordrath_P(ph), ht)
        g2 = remap(g, CROWN_RED)
        g2 = hexmap(g2, {PALc["grass_hi"]: VIO, PALc["grass"]: VIO_D}) if violet else remap(g2, {"grass_hi": "cloth", "grass": "shadow"})
        d = B.squeeze(g2, .74); d.die_mode = "sink"; d.sink_cols = ("white", "plaster_hi", "plaster", "stone_hi"); d.fall = True
        out["mordrath" if ph == 1 else f"mordrath_p{ph}"] = dict(draw=d, scale=s, anims=("idle", "walk", "cast", "attack", "die"), enemy=True, kind="enemy", boss=True,
            stats_hint=hint, light={"color": "#e8321e" if ph == 3 else "#a45cf0", "intensity": 1.4, "range": 12.0},
            desc="Mordrath, the Pale Sovereign (boss 8x): bone-white plate (the only plate in the arc) with gold-black trim, crown of red cold fire, violet-smoke wings (cape; smoke = fx), chains of names on the arms, tall pale glaive. " + descs[ph])
    return out
