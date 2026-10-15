"""Svartalfheim actors (Hearthmoor Art seat, 2026-10-06): Anvildeep townsfolk (dwarves, dark elves, a gnome), Dagna Coalbeard
(companion), and the Clockwork Deep regulars. 20x32 frames, cozy-village palette only (no neon on sprites; glow comes from
gamefx + lights). Everyone wears real clothes: a separate top and bottom with a visible waist, contrasting shoes."""
import math

import sv_common as C
from sv_common import H, ell, rect, shader, sset, sget, tline, toad, gear

A4 = ("idle", "walk", "attack", "die")


def _head(L, bob):
    ht = L["head_top"] + bob
    x0 = (20 - L["head_w"]) // 2
    return ht, x0, x0 + L["head_w"] - 1


def _torso(L, bob):
    tw = L["torso_w"]
    x0 = 10 - tw // 2
    return L["torso_top"] + bob, x0, x0 + tw - 1, L["hip"] + bob


# ------------------------------------------------------------------ hook parts
def braids(s, L, face, bob, col, ring, n=2, length=4):
    """braided beard hanging from the chin over the top (n = 1, 2 or 3 braids), metal rings near the ends"""
    ht, x0, x1 = _head(L, bob)
    chin = ht + L["head_h"] - 1
    if face == "down":
        xs = {1: [9], 2: [7, 12], 3: [7, 10, 13]}[n]
        for bx in xs:
            for k in range(length):
                sset(s, bx, chin + k, col if k % 2 == 0 else C.SP.HSprite and col)
                sset(s, bx + (1 if k % 2 else 0), chin + k, col)
            sset(s, bx, chin + length - 2, ring)
            if n == 1:
                sset(s, bx + 1, chin + length - 2, ring)
    elif face == "left":
        bx = x0 + 2
        for k in range(length):
            sset(s, bx + (k % 2), chin + k, col)
        sset(s, bx, chin + length - 2, ring)


def ears(s, L, face, bob, col, tip):
    ht, x0, x1 = _head(L, bob)
    ey = ht + 6
    if face in ("down", "up"):
        c = col if face == "down" else tip
        for sd, xe in ((-1, x0), (1, x1)):
            sset(s, xe + sd, ey, c); sset(s, xe + sd, ey - 1, c)
            sset(s, xe + 2 * sd, ey - 2, c); sset(s, xe + 2 * sd, ey - 3, tip)
    else:
        bx = x0 + 7
        sset(s, bx, ey, col); sset(s, bx, ey - 1, col); sset(s, bx + 1, ey - 1, tip)
        sset(s, bx + 1, ey - 2, col); sset(s, bx + 2, ey - 3, col); sset(s, bx + 3, ey - 4, tip)


def rune_tattoo(s, L, face, bob, c="sky"):
    """thin cold-blue rune tattoos on the forearms (a dotted line on the skin of each arm) + one brow dot; palette sky /
    white, the night glow comes from the light, never neon"""
    T, a, b, hip = _torso(L, bob)
    for y in range(T + 1, T + 1 + L["arm_len"]):
        for x in range(1, 19):
            if (x < a or x > b) and sget(s, x, y) in (H.PAL["sky"], H.PAL["stone"]) and (y + x) % 2 == 0:
                if sget(s, x, y) != H.PAL[c]:
                    sset(s, x, y, c)
    ht, x0, x1 = _head(L, bob)
    if face == "down":
        sset(s, 9, ht + 4, c) if sget(s, 9, ht + 4) in (H.PAL["sky"], H.PAL["stone"]) else None


def sceptre(s, L, face, bob, anim, i):
    """the Thane's smith's hammer held upright as a sceptre (near hand), copper-banded head"""
    if face == "up":
        return
    T, a, b, hip = _torso(L, bob)
    hy = T + 1 + L["arm_len"]
    hx = a - 1 if face == "down" else 8
    for y in range(hy - 6, hy + 2):
        sset(s, hx, y, "timber")
    rect(s, hx - 1, hy - 9, hx + 1, hy - 7, "stone"); sset(s, hx - 1, hy - 9, "stone_hi"); sset(s, hx, hy - 8, "roof_hi")


def buckle(s, L, face, bob, c="roof_hi"):
    T, a, b, hip = _torso(L, bob)
    if face == "down":
        sset(s, 9, hip - 1, c); sset(s, 10, hip - 1, c)
    elif face == "left":
        sset(s, a + 1, hip - 1, c)


def sash_tail(s, L, face, bob, c):
    T, a, b, hip = _torso(L, bob)
    if face == "down":
        sset(s, b - 1, hip, c); sset(s, b - 1, hip + 1, c)
    elif face == "left":
        sset(s, b, hip, c); sset(s, b, hip + 1, c)
    elif face == "up":
        sset(s, a + 2, hip, c); sset(s, a + 2, hip + 1, c)


def wrap_line(s, L, face, bob, c):
    """the crossover edge of a wrap-top: a diagonal from the shoulder to the opposite hip"""
    T, a, b, hip = _torso(L, bob)
    if face == "down":
        for k in range(hip - T - 1):
            sset(s, a + 2 + k, T + 1 + k, c)


def high_collar(s, L, face, bob, c):
    T, a, b, hip = _torso(L, bob)
    ht, x0, x1 = _head(L, bob)
    if face == "down":
        for x in range(a + 2, b - 1):
            sset(s, x, T, c)
        sset(s, a + 2, T - 1, c); sset(s, b - 2, T - 1, c)
    elif face == "left":
        sset(s, a + 3, T - 1, c); sset(s, a + 4, T - 1, c); sset(s, a + 3, T, c)


def lens(s, L, face, bob):
    T, a, b, hip = _torso(L, bob)
    if face == "down":
        for k in range(3):
            sset(s, 8 + k, T + 1 + k, "flower_gold")
        sset(s, 11, T + 4, "flower_gold"); sset(s, 11, T + 5, "sky"); sset(s, 12, T + 5, "white"); sset(s, 11, T + 6, "flower_gold")
    elif face == "left":
        sset(s, a + 2, T + 3, "flower_gold"); sset(s, a + 2, T + 4, "sky"); sset(s, a + 1, T + 4, "white")


def hip_blades(s, L, face, bob):
    T, a, b, hip = _torso(L, bob)
    if face == "down":
        for sd, x in ((-1, a - 1), (1, b + 1)):
            sset(s, x, hip - 1, "shadow"); sset(s, x, hip, "stone_hi"); sset(s, x, hip + 1, "stone_hi"); sset(s, x, hip + 2, "sky")
    elif face == "up":
        for x in (a - 1, b + 1):
            sset(s, x, hip - 1, "shadow"); sset(s, x, hip, "stone_hi"); sset(s, x, hip + 1, "stone_hi")
    else:
        sset(s, b, hip - 1, "shadow"); sset(s, b + 1, hip, "stone_hi"); sset(s, b + 2, hip + 1, "stone_hi"); sset(s, b + 3, hip + 2, "sky")


def shin_wraps(s, L, face, bob, c="plaster_lo"):
    for y in (27, 29):
        for x in range(2, 18):
            v = sget(s, x, y + (0 if face == "down" else 0))
            if v in (H.PAL["stone_lo"], H.PAL["shadow"]) and y + 1 <= 30:
                if (x + y) % 2 == 0:
                    sset(s, x, y, c)


def topknot(s, L, face, bob, c, lo):
    ht, x0, x1 = _head(L, bob)
    cx = 9 if face != "left" else 10
    rect(s, cx, ht - 2, cx + 1, ht - 1, c)
    sset(s, cx, ht - 3, lo); sset(s, cx + 1, ht - 3, c)
    sset(s, cx, ht, "shadow")


def back_hammer(s, L, face, bob, anim, i, glow=True):
    """Dagna's big square hammer slung across her back: haft over the shoulder, square head above it (faint ember glow =
    lamp / flower_gold palette pixels; the real glow is the dagna_hammer_glow light)"""
    T, a, b, hip = _torso(L, bob)
    ht, x0, x1 = _head(L, bob)
    if face == "down":                   # head pokes up behind the right shoulder
        hx, hy = b + 1, T - 4
        rect(s, hx - 1, hy - 2, hx + 2, hy + 1, "stone_lo"); rect(s, hx - 1, hy - 2, hx, hy - 2, "stone")
        sset(s, hx + 1, hy - 1, "lamp" if glow else "stone"); sset(s, hx, hy, "flower_gold" if glow and i % 2 == 0 else "stone_lo")
        sset(s, a - 1, hip - 1, "timber"); sset(s, a - 1, hip, "timber")
    elif face == "up":                   # whole hammer across the back
        for k in range(9):
            sset(s, a + 1 + k, hip - 1 - k, "timber")
        hx, hy = b, T - 5
        rect(s, hx - 1, hy - 1, hx + 2, hy + 2, "stone_lo"); rect(s, hx - 1, hy - 1, hx + 2, hy - 1, "stone")
        sset(s, hx + 1, hy + 1, "lamp" if glow else "stone")
    else:
        hx, hy = b + 1, T - 3
        for k in range(8):
            sset(s, b - 3 + k // 2, hip - 1 - k, "timber")
        rect(s, hx - 1, hy - 2, hx + 2, hy + 1, "stone_lo"); rect(s, hx - 1, hy - 2, hx + 2, hy - 2, "stone")
        sset(s, hx + 1, hy - 1, "lamp" if glow else "stone"); sset(s, hx + 2, hy, "flower_gold" if glow and i % 2 == 0 else "stone_lo")


def bracers(s, L, face, bob, c="timber"):
    """leather bracers: recolour the skin of the forearm rows just above the hands"""
    T, a, b, hip = _torso(L, bob)
    hy = T + 1 + L["arm_len"]
    for y in (hy - 2, hy - 1):
        for x in range(1, 19):
            if sget(s, x, y) == H.PAL["skin"] and (x < a or x > b):
                sset(s, x, y, c)


def cheeks(s, L, face, bob):
    ht, x0, x1 = _head(L, bob)
    if face == "down":
        sset(s, x0 + 2, ht + 7, "flower_rose"); sset(s, x1 - 2, ht + 7, "flower_rose")
    elif face == "left":
        sset(s, x0 + 3, ht + 7, "flower_rose")


def toad_cap(s, L, face, bob):
    ht, x0, x1 = _head(L, bob)
    cx = 10 if face != "left" else 9
    for dy, hw in ((0, 4), (1, 3), (2, 2)):
        for dx in range(-hw, hw + 1):
            sset(s, cx + dx, ht - dy, "roof_hi" if dx < hw - 1 else "roof")
    sset(s, cx - 2, ht - 1, "white"); sset(s, cx + 1, ht - 2, "white"); sset(s, cx + 3, ht, "white")


def goggles(s, L, face, bob):
    ht, x0, x1 = _head(L, bob)
    y = ht + 2
    if face == "down":
        for x in range(x0 + 1, x1):
            sset(s, x, y, "timber_lo")
        for gx in (x0 + 3, x1 - 4):
            sset(s, gx, y, "flower_gold"); sset(s, gx + 1, y, "flower_gold"); sset(s, gx, y - 1, "sky"); sset(s, gx + 1, y - 1, "white")
    elif face == "left":
        sset(s, x0 + 1, y, "flower_gold"); sset(s, x0 + 2, y, "flower_gold"); sset(s, x0 + 1, y - 1, "white")
        for x in range(x0 + 3, x0 + 10):
            sset(s, x, y, "timber_lo")
    else:
        for x in range(x0 + 1, x1):
            sset(s, x, y, "timber_lo")


def braces(s, L, face, bob, c="timber_lo"):
    T, a, b, hip = _torso(L, bob)
    if face in ("down", "up"):
        for y in range(T, hip - 1):
            sset(s, a + 2, y, c); sset(s, b - 2, y, c)
    else:
        for y in range(T, hip - 1):
            sset(s, a + 3, y, c)


def socks(s, L, face, bob):
    for y in (27, 28):
        for x in range(1, 19):
            v = sget(s, x, y)
            if v == H.PAL["skin"]:
                sset(s, x, y, "plaster_hi" if y % 2 else "roof_hi")


def orb_jar(s, L, face, bob, i):
    if face == "up":
        return
    T, a, b, hip = _torso(L, bob)
    hy = T + 1 + L["arm_len"]
    hx = a - 2 if face == "down" else 8
    rect(s, hx - 1, hy, hx + 1, hy + 2, "stone_hi")
    sset(s, hx, hy + 1, "white" if i % 2 == 0 else "sky"); sset(s, hx - 1, hy + 1, "sky")
    sset(s, hx - 1, hy - 1, "timber"); sset(s, hx, hy - 1, "timber"); sset(s, hx + 1, hy - 1, "timber")


def sooty_knees(s, L, face, bob):
    for x in range(2, 18):
        if sget(s, x, 28) == H.PAL["skin"] and x % 2 == 0:
            sset(s, x, 28, "stone_lo")


def fishing_net(s, L, face, bob):
    if face == "up":
        return
    T, a, b, hip = _torso(L, bob)
    px = min(17, b + 1) if face == "down" else max(3, a - 1)
    top = T - 7
    for y in range(top, 31):
        sset(s, px, y, "timber")
    d = -1 if face == "down" else 1                  # the net head leans in over the head, inside the frame
    for y in range(top - 3, top + 2):
        for k in range(0, 4):
            x = px + d * k
            if (x + y) % 2 == 0 and 1 < x < 18 and k + abs(y - top + 1) <= 3:
                sset(s, x, y, "stone_hi")


def apron_tie(s, L, face, bob, c):
    T, a, b, hip = _torso(L, bob)
    if face == "up":
        sset(s, 9, hip - 1, c); sset(s, 10, hip - 1, c); sset(s, 9, hip, c); sset(s, 11, hip, c)


def hot_hammer(s, L, face, bob, anim, i):
    """the shadowsmith's glowing hammer at the hip outside actions (head lamp / flower_gold)"""
    if face == "up":
        return
    T, a, b, hip = _torso(L, bob)
    hy = T + 1 + L["arm_len"]
    hx = b + 2 if face == "down" else 9
    for y in range(hy - 2, hy + 2):
        sset(s, hx, y, "timber")
    rect(s, hx - 1, hy + 2, hx + 1, hy + 3, "roof_hi"); sset(s, hx, hy + 2, "lamp"); sset(s, hx + 1, hy + 3, "roof")


# ------------------------------------------------------------------ hooks per character
def hook(*parts):
    def fn(s, sp, L, face, bob, anim, i):
        for p in parts:
            p(s, sp, L, face, bob, anim, i)
    return fn


P = {
    "elf_sky": lambda s, sp, L, f, b, a, i: ears(s, L, f, b, "sky", "flower_blue"),
    "elf_ash": lambda s, sp, L, f, b, a, i: ears(s, L, f, b, "stone", "stone_lo"),
    "tat_white": lambda s, sp, L, f, b, a, i: rune_tattoo(s, L, f, b, "white"),
    "tat_sky": lambda s, sp, L, f, b, a, i: rune_tattoo(s, L, f, b, "sky"),
    "copper_buckle": lambda s, sp, L, f, b, a, i: buckle(s, L, f, b, "roof_hi"),
    "brass_buckle": lambda s, sp, L, f, b, a, i: buckle(s, L, f, b, "flower_gold"),
    "cheeks": lambda s, sp, L, f, b, a, i: cheeks(s, L, f, b),
}


def B(col, ring, n=2, length=4):
    return lambda s, sp, L, f, b, a, i: braids(s, L, f, b, col, ring, n, length)


def X(fn, *args):
    return lambda s, sp, L, f, b, a, i: fn(s, L, f, b, *args)


NPCS = {
    "thane": {
        "spec": H.human(dict(layout="dwarf", hair="roof_hi", hairstyle="short", beard="roof_hi", shirt="leaf_deep", belt="timber_lo",
                             pants="timber", shoes="shadow", boots=True),
                        hook(B("roof_hi", "flower_gold", 3, 4), P["copper_buckle"], P["cheeks"],
                             lambda s, sp, L, f, b, a, i: sceptre(s, L, f, b, a, i))),
        "anims": ("idle", "walk"), "kind": "human", "named": True,
        "desc": "Forge-Thane Ragna Copperbraid (dwarf smith-queen): copper-red beard in three braids with gold rings, deep-green wool "
                "tunic, wide leather belt with a copper buckle, brown trousers, heavy black boots, smith's hammer sceptre",
    },
    "runewarden": {
        "spec": H.human(dict(skin="sky", hair="white", hairstyle="short", shirt="stone_lo", belt="flower_blue", pants="shadow",
                             shoes="timber_lo"),
                        hook(P["elf_sky"], X(high_collar, "stone_lo"), X(sash_tail, "flower_blue"), X(lens), P["tat_white"])),
        "anims": ("idle", "walk"), "kind": "human", "named": True,
        "desc": "Sereth Gloamweave (dark-elf rune-warden): slate-blue skin, white jaw-length hair, long ears, high-collared charcoal "
                "blouse, cold-blue sash, slim black trousers, soft brown boots, a rune-lens on a gold chain, white rune tattoo on the cheek",
    },
    "hushed": {
        "spec": H.human(dict(skin="stone", hair="stone_hi", hairstyle="short", shirt="shadow", belt="stone", pants="stone_lo",
                             shoes="timber_lo", boots=True),
                        hook(P["elf_ash"], X(topknot, "stone_hi", "plaster_hi"), X(wrap_line, "stone_lo"), X(sash_tail, "stone"),
                             X(hip_blades), X(shin_wraps), P["tat_sky"])),
        "anims": ("idle", "walk"), "kind": "human", "named": True,
        "desc": "Captain Ilvar Hushblade (dark elf, captain of the Hushed): ash-grey skin, silver topknot, long ears, fitted black "
                "wrap-top, grey sash, dark trousers bound at the shins, two short blades at his hips, cold-blue rune tattoo",
    },
    "dwarftrader": {
        "spec": H.human(dict(layout="dwarf", hair="shadow", hairstyle="short", beard="shadow", shirt="roof", apron="timber",
                             belt="timber_lo", pants="stone_lo", shoes="timber_lo", boots=True),
                        hook(B("shadow", "flower_gold", 2, 4), X(apron_tie, "timber_lo"))),
        "anims": ("idle", "walk"), "kind": "human", "named": True,
        "desc": "Brokk Emberlode (dwarf trader): soot-black beard in two braids with brass beads, rust wool shirt, leather apron "
                "belted over slate trousers, brown boots",
    },
    "tinker": {
        "spec": H.human(dict(layout="kid", hair="timber_hi", hairstyle="short", shirt="flower_gold", belt="timber_lo", pants="timber",
                             shoes="shadow"),
                        hook(X(braces), X(socks), X(goggles), X(toad_cap))),
        "anims": ("idle", "walk"), "kind": "human", "named": True,
        "desc": "Tansy Brasswhistle (gnome tinker): tiny red white-spotted toadstool cap, brass goggles, mustard shirt, brown "
                "corduroy shorts with braces and a dark belt, striped socks, black shoes",
    },
    "minerunner": {
        "spec": H.human(dict(layout="kid", skin="sky", hair="white", hairstyle="messy", shirt="stone", belt="plaster_lo",
                             pants="timber", shoes="timber_lo"),
                        hook(P["elf_sky"], X(sooty_knees), lambda s, sp, L, f, b, a, i: orb_jar(s, L, f, b, i))),
        "anims": ("idle", "walk"), "kind": "human", "named": True,
        "desc": "Kesh (dark-elf kid, mine-runner): slate-blue skin, messy white hair, long ears, too-big grey knitted jumper, "
                "rope belt, short brown trousers, sooty knees, a cave orb in a jar",
    },
    "poolkeeper_sv": {
        "spec": H.human(dict(layout="dwarf", hair="plaster_hi", hairstyle="bun", beard="white", shirt="flower_blue", skirt="shadow",
                             pants="shadow", apron="plaster", belt="timber_lo", shoes="timber"),
                        hook(B("white", "flower_blue", 1, 5), X(fishing_net), X(apron_tie, "plaster_lo"), P["cheeks"])),
        "anims": ("idle", "walk"), "kind": "human", "named": True,
        "desc": "Old Haldis (dwarf grandmother): white bun and one long white beard braid, lavender cardigan (periwinkle palette) "
                "over a cream blouse, dark skirt with a cream apron tied at the waist, brown shoes, a fishing net",
    },
    "dw1": {
        "spec": H.human(dict(layout="dwarf", hair="timber", hairstyle="short", beard="timber_hi", shirt="cloth", apron="timber_lo",
                             belt="shadow", pants="stone", shoes="shadow", boots=True),
                        hook(B("timber_hi", "roof_hi", 2, 4))),
        "anims": ("idle", "walk"), "kind": "human",
        "desc": "Anvildeep dwarf smith (ambient): auburn beard in two braids with copper rings, blue tunic, dark leather apron, "
                "dark belt, stone trousers, black boots",
    },
    "dw2": {
        "spec": H.human(dict(layout="dwarf", hair="flower_gold", hairstyle="bun", beard="flower_gold", shirt="plaster", vest="moss",
                             belt="timber_lo", pants="timber_lo", shoes="roof_lo", boots=True),
                        hook(B("flower_gold", "roof_hi", 2, 3), P["cheeks"])),
        "anims": ("idle", "walk"), "kind": "human",
        "desc": "Anvildeep dwarf woman (ambient): golden bun and braided golden beard with copper rings, cream shirt under a moss "
                "vest, dark belt, brown trousers, red-brown boots",
    },
    "sv1": {
        "spec": H.human(dict(skin="stone", hair="white", hairstyle="long", shirt="cloth", belt="flower_blue", pants="shadow",
                             shoes="timber_lo"),
                        hook(P["elf_ash"], X(wrap_line, "flower_blue"), X(sash_tail, "flower_blue"), P["tat_sky"])),
        "anims": ("idle", "walk"), "kind": "human",
        "desc": "Svartalf rune-carver (ambient): ash-grey skin, long white hair, long ears, deep-blue wrap-top, cold-blue sash, "
                "slim dark trousers, brown soft boots, rune tattoo",
    },
    "sv2": {
        "spec": H.human(dict(skin="sky", hair="stone_hi", hairstyle="bun", shirt="roof_lo", belt="plaster_lo", pants="stone_lo",
                             shoes="shadow"),
                        hook(P["elf_sky"], X(wrap_line, "roof"), X(sash_tail, "plaster_lo"), P["tat_white"])),
        "anims": ("idle", "walk"), "kind": "human",
        "desc": "Svartalf miner (ambient): slate-blue skin, silver bun, long ears, wine-red wrap-top, pale sash, slim slate "
                "trousers, black shoes, white rune tattoo",
    },
}

# ------------------------------------------------------------------ Dagna Coalbeard (companion)
DAGNA_RECOLOR = {"sky": "lamp", "white": "flower_gold", "flower_blue": "roof_hi", "cloth": "roof"}


def dagna_hook(s, sp, L, face, bob, anim, i):
    braids(s, L, face, bob, "shadow", "roof_hi", 2, 4)
    cheeks(s, L, face, bob)
    bracers(s, L, face, bob, "timber")
    apron_tie(s, L, face, bob, "timber_lo")
    if anim in ("idle", "walk"):
        back_hammer(s, L, face, bob, anim, i)


DAGNA = {
    "dagna": {
        "spec": H.human(dict(layout="dwarf", hair="shadow", hairstyle="short", beard="shadow", shirt="roof", apron="timber",
                             belt="timber_lo", pants="stone", shoes="timber_hi", boots=True, hero=True, caster=True,
                             style="brawler", weapon="stormhammer", fx="thunder", stow=True, act_recolor=DAGNA_RECOLOR,
                             trail=("lamp", "flower_gold"), sleeves="rolled", forearm="skin"), dagna_hook),
        "anims": ("idle", "walk", "cast", "attack"), "kind": "human", "named": True,
        "desc": "Dagna Coalbeard (dwarf smith, companion): soot-black beard in two thick braids with copper rings, ruddy cheeks, "
                "red-brown work shirt with sleeves rolled to the elbow, leather bracers, leather apron tied at the waist over grey "
                "trousers, tan steel-toed boots, big square hammer on her back (head glows faint ember-orange). Attack = hammer "
                "swing (frame 14), cast = ember strike (sparks in lamp / gold)",
        "light": {"color": "#f2a63a", "intensity": 2.0, "range": 1.8, "lift": 0.6, "fx": "dagna_hammer_glow"},
    },
}

# ------------------------------------------------------------------ Clockwork Deep regulars (draw functions)


def forgeconstruct(s, face, anim, i):
    """brass construct, waist-high: a riveted barrel body with a glowing furnace belly grate, a dome head with a slit visor,
    stubby piston legs, clamp arms"""
    b = [0, 0, 1, 0][i] if anim == "idle" else [0, -1, 0, -1][i] if anim == "walk" else 0
    side = face == "left"
    if anim == "die":
        if i >= 2:
            ell(s, 10, 28, 7, 2.5, "timber", shader(10, 7, "flower_gold", "timber_hi", "timber"))
            rect(s, 6, 25, 9, 27, "timber_hi"); gear(s, 13, 26, 2, "flower_gold", "plaster_hi", "timber_hi")
            sset(s, 8, 29, "roof_hi" if i == 2 else "roof"); sset(s, 11, 28, "lamp" if i == 2 else "roof_lo")
            for x in range(4, 17):
                sset(s, x, 30, "timber_lo")
            return
        b = 2 * i
    lunge = [0, -2, 2, 0][i] if anim == "attack" else 0
    # legs
    ls = [0, 1, 0, -1][i] if anim == "walk" else 0
    for lx, off in ((7, ls), (12, -ls)):
        rect(s, lx, 24 + b // 2, lx + 1, 29, "stone_lo")
        rect(s, lx - 1, 29, lx + 2, 30, "shadow")
        sset(s, lx, 25 + b // 2, "stone")
    # body barrel
    cx = 10 + (lunge if side else 0)
    ell(s, cx, 19 + b, 6, 6, "timber_hi", shader(cx, 6, "flower_gold", "timber_hi", "timber"))
    for x in range(cx - 5, cx + 6):
        sset(s, x, 14 + b, "timber"); sset(s, x, 24 + b, "timber")
    for x in (cx - 4, cx + 4):
        sset(s, x, 15 + b, "plaster_hi")
    # furnace belly grate (weak point)
    fx = cx - 1 if side else cx
    if face != "up":
        rect(s, fx - 2, 18 + b, fx + 2, 22 + b, "roof_lo")
        for y in (19, 21):
            for x in range(fx - 2, fx + 3):
                sset(s, x, y + b, "lamp" if (x + y + i) % 3 else "flower_gold")
        sset(s, fx, 20 + b, "roof_hi")
    else:
        sset(s, cx, 16 + b, "stone_lo"); sset(s, cx, 17 + b, "plaster_lo")
        rect(s, cx - 1, 9 + b, cx + 1, 11 + b, "stone_lo")          # smokestack
    # head dome + visor
    ell(s, cx, 11 + b, 4, 3, "timber_hi", shader(cx, 4, "flower_gold", "timber_hi", "timber"))
    if face == "down":
        rect(s, cx - 2, 11 + b, cx + 2, 11 + b, "shadow"); sset(s, cx - 1, 11 + b, "lamp"); sset(s, cx + 1, 11 + b, "lamp")
    elif side:
        rect(s, cx - 4, 11 + b, cx - 1, 11 + b, "shadow"); sset(s, cx - 3, 11 + b, "lamp")
    sset(s, cx, 7 + b, "stone"); sset(s, cx, 8 + b, "stone_lo")
    # clamp arms
    raise_ = [0, 4, -2, 0][i] if anim == "attack" else 0
    if side:
        ax = cx - 6 - (2 if anim == "attack" and i == 2 else 0)
        tline(s, cx - 3, 17 + b, ax, 20 + b - raise_, 2, "stone_lo")
        sset(s, ax - 1, 20 + b - raise_, "stone_hi"); sset(s, ax - 1, 22 + b - raise_, "stone_hi"); sset(s, ax, 21 + b - raise_, "stone")
    else:
        for sd in (-1, 1):
            ax = cx + sd * 8
            tline(s, cx + sd * 5, 17 + b, ax, 21 + b - raise_, 2, "stone_lo")
            sset(s, ax, 23 + b - raise_, "stone_hi"); sset(s, ax + sd, 22 + b - raise_, "stone_hi")
    if anim == "attack" and i == 2 and face != "up":
        sset(s, fx, 20 + b, "white")


def sparkgolem(s, face, anim, i):
    """iron frame golem: a cage chest between two copper coils, blue-white arcs jumping between them (palette sky / white)"""
    b = [0, 0, 1, 0][i] if anim == "idle" else [0, -1, 0, -1][i] if anim == "walk" else 0
    side = face == "left"
    if anim == "die" and i >= 2:
        for x in range(3, 18):
            sset(s, x, 30, "stone_lo")
        rect(s, 5, 27, 9, 29, "stone_lo"); rect(s, 12, 28, 15, 29, "roof"); sset(s, 13, 28, "roof_hi")
        sset(s, 7, 26, "stone"); sset(s, 10, 29, "sky" if i == 2 else "stone")
        return
    if anim == "die":
        b = 2 * i + 1
    ls = [0, 1, 0, -1][i] if anim == "walk" else 0
    for lx, off in ((6, ls), (13, -ls)):
        tline(s, lx, 22 + b, lx + off, 29, 2, "stone_lo")
        rect(s, lx - 1 + off, 29, lx + 2 + off, 30, "shadow")
    # frame chest (open cage)
    for y in range(12 + b, 23 + b):
        sset(s, 6, y, "stone_lo"); sset(s, 14, y, "stone_lo")
    for x in range(6, 15):
        sset(s, x, 12 + b, "stone"); sset(s, x, 22 + b, "stone_lo"); sset(s, x, 17 + b, "stone_lo")
    sset(s, 7, 12 + b, "stone_hi"); sset(s, 8, 12 + b, "stone_hi")
    # copper coils on the shoulders
    for cx in ((4, 16) if not side else (5, 14)):
        for k in range(5):
            sset(s, cx, 11 + b + k, "roof_hi" if k % 2 == 0 else "roof")
            sset(s, cx + 1, 11 + b + k, "roof" if k % 2 == 0 else "roof_lo")
        sset(s, cx, 10 + b, "flower_gold")
    # head: a lamp-bulb cage
    hx = 10 if not side else 9
    ell(s, hx, 9 + b, 3, 3, "stone", shader(hx, 3, "stone_hi", "stone", "stone_lo"))
    if face != "up":
        sset(s, hx - 1, 9 + b, "white"); sset(s, hx + (1 if not side else -2), 9 + b, "sky")
    # arcs between the coils (always, brighter on attack)
    hot = anim == "attack" and i in (1, 2)
    pts = [(5, 12), (8, 10 + (i % 2) * 2), (10, 13), (12, 11), (15, 12)]
    for k in range(len(pts) - 1):
        if (k + i) % 2 == 0 or hot:
            tline(s, pts[k][0], pts[k][1] + b, pts[k + 1][0], pts[k + 1][1] + b, 1, "white" if hot and k % 2 else "sky")
    # inner core
    sset(s, 10, 19 + b, "sky"); sset(s, 10, 20 + b, "white" if i % 2 else "sky")
    if anim == "attack":
        d = -1 if side else 1
        ax = 10 + d * (6 + 2 * i)
        tline(s, 10 + d * 4, 15 + b, ax, 14 + b - (2 if i == 1 else 0), 2, "stone_lo")
        if i in (1, 2):
            for k in range(3):
                sset(s, ax + d * (1 + k), 13 + b - k % 2, "white" if k % 2 else "sky")


def sootling(s, face, anim, i):
    """a floating puff of soot with two ember eyes; a wispy smoke tail trails down to the ground row"""
    b = [0, -1, -2, -1][i] if anim in ("idle", "walk") else 0
    if anim == "die":
        for k in range(6 + i * 2):
            a = k / (6 + i * 2) * math.tau
            r = 3 + i * 2
            sset(s, 10 + math.cos(a) * r, 18 + math.sin(a) * r * 0.7, "stone_lo" if k % 2 else "shadow")
        if i < 2:
            sset(s, 8, 17, "lamp"); sset(s, 12, 17, "lamp")
        for y in range(25, 31, 2):
            sset(s, 10 + (y % 3) - 1, y, "stone_lo")
        sset(s, 10, 30, "stone_lo")
        return
    sq = [0, 1, -1, 0][i] if anim == "attack" else 0
    cy = 16 + b
    ell(s, 10, cy, 6 + sq, 5 - sq, "shadow", shader(10, 6, "stone_lo", "shadow", "shadow"))
    for (dx, dy) in ((-5, -3), (4, -4), (-2, -5), (6, 0), (-6, 1)):
        ell(s, 10 + dx, cy + dy, 2, 2, "stone_lo" if dx < 0 else "shadow")
    if face != "up":
        ex = (8, 12) if face == "down" else (6, 9)
        for x in ex:
            sset(s, x, cy, "lamp"); sset(s, x, cy - 1, "flower_gold" if anim == "attack" else "lamp")
        if anim == "attack" and i in (1, 2):
            rect(s, ex[0] + 1, cy + 2, ex[1] - 1, cy + 2, "roof_hi")
    for y in range(cy + 5, 31):                     # smoke tail to the ground row
        x = 10 + int(math.sin(y * 0.6 + i) * 1.5)
        sset(s, x, y, "stone_lo" if y % 2 else "shadow")
    sset(s, 10, 30, "stone_lo")
    for k in range(2):                              # floating embers
        sset(s, 4 + k * 11 + (i % 2), 8 + ((i + k * 2) % 4), "lamp" if k else "roof_hi")


ENEMY_SPECS = {
    "shadowsmith": {
        "spec": H.human(dict(skin="stone", hair="white", hairstyle="short", shirt="stone_lo", apron="timber", belt="timber_lo",
                             pants="shadow", shoes="timber_lo", hero=True, style="brawler", weapon="stormhammer", fx="thunder",
                             act_recolor={"sky": "lamp", "white": "flower_gold", "stone_hi": "roof_hi", "stone": "roof", "stone_lo": "roof_lo"},
                             trail=("roof_hi", "lamp")),
                        hook(P["elf_ash"], X(apron_tie, "timber_lo"), P["tat_sky"],
                             lambda s, sp, L, f, b, a, i: hot_hammer(s, L, f, b, a, i) if a in ("idle", "walk") else None)),
    },
    "hushblade": {
        "spec": H.human(dict(skin="stone", hair="stone_hi", hairstyle="short", shirt="shadow", belt="stone", pants="stone_lo",
                             shoes="shadow", hero=True, style="brawler", weapon="greatsword", fx="ember", blades=True,
                             act_recolor={"lamp": "sky", "roof_hi": "stone_hi", "flower_gold": "white"}, trail=("stone_hi", "sky")),
                        hook(P["elf_ash"], X(wrap_line, "stone_lo"), X(sash_tail, "stone"), X(shin_wraps),
                             lambda s, sp, L, f, b, a, i: hip_blades(s, L, f, b) if a in ("idle", "walk", "die") else None)),
    },
}

ENEMIES = {
    "forgeconstruct": {"draw": forgeconstruct, "kind": "enemy", "enemy": True, "named": True, "anims": A4,
                       "desc": "Forge construct: waist-high brass barrel construct, dome head with a slit visor, clamp arms, piston "
                               "legs, glowing furnace-belly grate (weak point, +50%). Attack = double clamp (frame 14, belly flares); "
                               "die = collapses into brass plates + a loose cog",
                       "light": {"color": "#f2a63a", "intensity": 0.6, "range": 1.6, "lift": 0.5},
                       "stats_hint": {"tier": "common", "weak": "belly", "fx": {"hit": "spark_burst", "die": "steam_puff"}}},
    "sparkgolem": {"draw": sparkgolem, "kind": "enemy", "enemy": True, "named": True, "anims": A4,
                   "desc": "Spark golem (lightning golem): open iron cage frame, copper coils on both shoulders, blue-white arcs "
                           "jumping between them, a lamp-bulb head. Attack = arm thrust + arc (frame 14, spawn spark_arc); die = "
                           "falls apart into iron and copper",
                   "light": {"color": "#a6ecff", "intensity": 0.7, "range": 2.0, "lift": 0.9},
                   "stats_hint": {"tier": "common", "ranged": True, "fx": {"bolt": "spark_arc", "die": "spark_burst"}}},
    "sootling": {"draw": sootling, "kind": "enemy", "enemy": True, "named": True, "anims": A4,
                 "desc": "Sootling: floating soot puff with ember eyes, a smoke tail to the ground, drifting embers. Attack = puffs "
                         "up + ember mouth (frame 14); die = pops into a smoke ring (spawn soot_pop)",
                 "light": {"color": "#e0602a", "intensity": 0.4, "range": 1.2, "lift": 0.7},
                 "stats_hint": {"tier": "common", "float": True, "fx": {"die": "soot_pop"}}},
    "shadowsmith": {**ENEMY_SPECS["shadowsmith"], "kind": "human", "enemy": True, "named": True, "anims": ("idle", "walk", "attack"),
                    "desc": "Shadowsmith (elite, dark-elf rogue smith): ash-grey skin, short white hair, long ears, grey shirt under a "
                            "leather apron tied at the waist, black trousers, a glowing hot hammer (red-hot head). Attack = hot-hammer "
                            "swing (frame 14)",
                    "light": {"color": "#e0602a", "intensity": 0.6, "range": 1.6, "lift": 0.5},
                    "stats_hint": {"tier": "elite", "fx": {"hit": "spark_burst", "shadow_step": "shadow_puff"}}},
    "hushblade": {**ENEMY_SPECS["hushblade"], "kind": "human", "enemy": True, "named": True, "anims": ("idle", "walk", "attack"),
                  "desc": "Hushed blade (conquer only, dark-elf assassin): ash-grey skin, silver hair, long ears, black wrap-top, grey "
                          "sash, slate trousers bound at the shins, black shoes, two short blades (cold-blue edge). Attack = "
                          "blade combo (frame 14); fades in / out with shadow_puff",
                  "stats_hint": {"tier": "common", "stealth": 4, "fx": {"fade": "shadow_puff"}}},
}

# Dwarves (and the small kid / gnome builds) are natively short: the repo's check-sprite size bounds for kind "human" start at
# 24 px tall, so these roles carry kind "creature" (bounds 10-40 px) plus "body" so the builder knows they are people.
for _tbl in (NPCS, DAGNA):
    for _k, _r in _tbl.items():
        _lay = _r["spec"]["layout"]
        if _lay in ("dwarf", "kid"):
            _r["kind"] = "creature"
            _r["body"] = {"dwarf": "dwarf (natively ~21 px tall, broad)", "kid": "small (kid layout)"}[_lay]
