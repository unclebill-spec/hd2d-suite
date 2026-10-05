"""More cozy roles for hd2d sprite (all original): new hats, held items, a 4-frame CAST pose for
magic users, and small animals (dog, goat, chicken, owl). Imported by sprite.py."""


def r(base, **kw):
    d = dict(base)
    d.update(kw)
    return d


def more_roles(_r):
    return {
        "blacksmith": _r(desc="broad smith, soot-dark leather apron, rolled sleeves, beard, hammer", hair="ink",
                         hairstyle="short", beard="timber_lo", shirt="plaster_lo", apron="timber_lo", pants="shadow",
                         boots=True, item="hammer"),
        "librarian": _r(desc="grey bun, round spectacles, long plum-brown dress, armful of books", hair="stone_hi",
                        hairstyle="bun", glasses=True, shirt="roof_lo", skirt="roof_lo", shawl="plaster_lo",
                        item="book"),
        "guard": _r(desc="friendly town watch: round iron cap, blue tabard with a gold stitch, tall spear",
                    hat="helm", hatc="stone_hi", hair="timber", shirt="stone", vest="cloth", pants="timber_lo",
                    boots=True, item="spear"),
        "innkeeper": _r(desc="jolly innkeeper, red vest, rolled sleeves, moustache, frothy mug", hair="timber_lo",
                        hairstyle="messy", beard="timber_lo", shirt="plaster_hi", vest="roof", apron="plaster",
                        item="mug"),
        "musician": _r(desc="wandering player: soft cap with a feather, gold doublet, little lute", hat="beret",
                       hatc="roof", hair="timber_hi", hairstyle="messy", shirt="flower_gold", pants="cloth",
                       scarf="flower_blue", item="lute"),
        "gardener": _r(desc="bucket hat, moss overalls, gloves, watering can", hat="bucket", hatc="grass_hi",
                       hair="timber", shirt="plaster", overalls="moss", shoes="timber_lo", item="can"),
        "herbalist": _r(desc="hedge herbalist: green kerchief, leaf shawl, satchel of sprigs; casts healing petals",
                        hat="kerchief", hatc="moss", hair="roof", hairstyle="long", shirt="plaster_hi",
                        skirt="timber", shawl="leaf_deep", satchel="timber_hi", item="sprig", caster=True),
        "hedgewitch": _r(desc="kind hedge-witch: wide pointed hat with a flower band, night-blue cloak, oak staff",
                         hat="witch", hatc="shadow", hair="plaster_hi", hairstyle="long", shirt="cloth",
                         skirt="cloth", cloak="shadow", item="staff", caster=True),
        "fisherkid": _r(desc="small fisher kid: yellow rain hat, striped top, tiny rod", layout="kid",
                        hat="rainhat", hatc="flower_gold", hair="timber", shirt="cloth", stripes="plaster_hi",
                        pants="timber_lo", boots=True, shoes="flower_gold", item="rod"),
        "lamplighter": _r(desc="lamplighter: flat cap, open long brown coat over a shirt, gold-buckled belt, grey "
                               "trousers, dark shoes, lit wick pole", hat="flatcap", hatc="shadow", hair="stone",
                          beard="stone_hi", shirt="plaster_lo", cloak="timber", belt="shadow", pants="stone_lo",
                          shoes="ink", item="wick"),
        "nightmerchant": _r(desc="travelling night merchant: deep hood, night-blue cloak, blue scarf, pack, neon-blue lantern",
                            hat="hood", hatc="shadow", hair="stone", beard="stone_hi", shirt="cloth", cloak="shadow",
                            scarf="flower_blue", satchel="timber_hi", pants="timber_lo", shoes="shadow", item="bluelantern"),
        "gnome": _r(desc="Toadstool Hollows gnome: small, tall red pointy cap with a white tassel, bushy white beard, "
                         "blue smock, brown belt and boots", layout="kid", hat="gnome", hatc="roof_hi", hair="white",
                    hairstyle="short", beard="white", shirt="cloth", pants="timber_lo", boots=True, shoes="timber_lo",
                    named=True),
        "corsair": _r(desc="Rift Corsair quartermaster (Ravenhold Harbor): red kerchief, long dark hair, cream shirt, "
                           "dark vest, red waist sash, navy trousers, tall dark boots, a tally ledger", hat="kerchief",
                      hatc="roof_hi", hair="shadow", hairstyle="long", shirt="plaster_hi", vest="shadow", sash="roof",
                      pants="cloth", boots=True, shoes="ink", item="ledger", named=True),
        "dog": _r(kind="creature", animal="dog", desc="scruffy cream terrier with floppy brown ears", fur="plaster",
                  spot="timber_hi", belly="plaster_hi"),
        "goat": _r(kind="creature", animal="goat", desc="small white goat with curled horns and a bell",
                   fur="plaster_hi", spot="stone", belly="white"),
        "chicken": _r(kind="creature", animal="chicken", desc="round speckled hen with a red comb",
                      fur="plaster_hi", spot="timber_hi", belly="white"),
        "owl": _r(kind="creature", animal="owl", desc="fluffy barn owl, heart face, hops", fur="timber_hi",
                  spot="plaster_hi", belly="plaster_hi"),
    }


# ------------------------------------------------------------------ hats
def draw_hat(s, spec, L, face, top, spans):
    hat, c = spec["hat"], spec["hatc"]
    a0, b0 = spans[2]
    lt, dk = s.pal.lt(c), s.pal.dk(c)
    if hat == "helm":
        for y, ind in ((top - 1, 2), (top, 1), (top + 1, 0), (top + 2, 0)):
            s.hspan(y, a0 + ind, b0 - ind, c)
            s.set(b0 - ind, y, dk)
        s.hspan(top + 3, a0 - 1, b0 + 1, dk)               # rim
        s.hspan(top, a0 + 2, a0 + 4, "white")                # shine
        s.set((a0 + b0) // 2, top - 2, dk)                   # little knob
    elif hat == "witch":
        band = "flower_rose"
        # wide brim
        s.hspan(top + 3, a0 - 2, b0 + 2, c)
        s.hspan(top + 4, a0 - 1, b0 + 1, s.pal.dk(c))
        # cone, tip bending back
        cx = (a0 + b0) // 2
        rows = [(top + 2, 5), (top + 1, 4), (top, 3), (top - 1, 2), (top - 2, 1)]
        for y, hw in rows:
            s.hspan(y, cx - hw, cx + hw - 1, c)
            s.set(cx + hw - 1, y, s.pal.dk(c))
        s.hspan(top + 2, cx - 5, cx + 4, band)
        s.set(cx - 2, top + 1, "flower_gold"); s.set(cx - 1, top + 2, "flower_gold"); s.set(cx + 2, top + 2, "white")
        tip = 1 if face != "left" else -1
        s.set(cx + tip, top - 3, c); s.set(cx + 2 * tip, top - 3, c); s.set(cx + 3 * tip, top - 2, s.pal.dk(c))
        s.set(cx - 1, top - 2, "stone_lo")
    elif hat == "kerchief":
        for y, ind in ((top - 1, 2), (top, 1), (top + 1, 0), (top + 2, 0)):
            s.hspan(y, a0 + ind, b0 - ind, c)
            s.set(b0 - ind, y, dk)
        s.hspan(top, a0 + 2, a0 + 5, lt)
        for x in range(a0 + 1, b0, 3):
            s.set(x, top + 1, "flower_gold")
        if face == "left":
            s.set(b0 + 1, top + 2, c); s.set(b0 + 2, top + 3, c); s.set(b0 + 1, top + 4, dk)
        elif face == "up":
            s.hspan(top + 3, a0 + 3, b0 - 3, c); s.set((a0 + b0) // 2, top + 4, dk); s.set((a0 + b0) // 2 + 1, top + 5, c)
    elif hat == "beret":
        for y, ind in ((top - 1, 1), (top, 0), (top + 1, 0)):
            s.hspan(y, a0 + ind - 1, b0 - ind + (1 if face != "left" else 0), c)
            s.set(b0 - ind + (1 if face != "left" else 0), y, dk)
        s.hspan(top + 2, a0, b0, dk)
        s.hspan(top - 1, a0 + 1, a0 + 3, lt)
        fx = b0 - 1 if face != "left" else b0
        for k in range(2):                                   # feather sweeping back
            s.set(fx + k, top - 2 - k, "white" if k < 1 else "flower_gold")
    elif hat == "gnome":
        # tall pointy red cap pulled low over the brow, tip flopping to one side, a white tassel on the tip
        cx = (a0 + b0) // 2
        s.hspan(top + 2, a0 - 1, b0 + 1, dk)                 # turned-up rim
        s.hspan(top + 1, a0 - 1, b0 + 1, c)
        rows = [(top, 6), (top - 1, 5), (top - 2, 5), (top - 3, 4), (top - 4, 3), (top - 5, 3), (top - 6, 2), (top - 7, 2)]
        for y, hw in rows:
            s.hspan(y, cx - hw, cx + hw - 1, c)
            s.set(cx + hw - 1, y, dk)
            s.set(cx - hw, y, lt)
        tip = -1 if face == "left" else 1
        s.set(cx + tip, top - 8, c); s.set(cx + 2 * tip, top - 8, dk); s.set(cx + 3 * tip, top - 7, "white")
        s.set(cx + 3 * tip, top - 6, "white"); s.set(cx + 4 * tip, top - 7, "stone_hi")
    elif hat == "bucket":
        for y, ind in ((top - 1, 2), (top, 1), (top + 1, 1)):
            s.hspan(y, a0 + ind, b0 - ind, c)
            s.set(b0 - ind, y, dk)
        s.hspan(top + 2, a0 - 1, b0 + 1, c)
        s.hspan(top + 3, a0 - 1, b0 + 1, dk)
        s.hspan(top + 1, a0 + 1, b0 - 1, "moss")             # band
        s.set(a0 + 2, top + 1, "flower_rose")


# ------------------------------------------------------------------ face extras
def draw_glasses(s, spec, L, face, top, hx, w):
    ey = top + 6
    if face == "down":
        ex0, ex1 = hx + 3, hx + w - 4
        for ex in (ex0, ex1):
            s.set(ex - 1, ey, "flower_gold"); s.set(ex + 1, ey, "flower_gold")
            s.set(ex - 1, ey + 1, "flower_gold"); s.set(ex + 1, ey + 1, "flower_gold")
        s.hspan(ey, ex0 + 1, ex1 - 1, "flower_gold")
    elif face == "left":
        x = hx + 1
        s.set(x, ey, "flower_gold"); s.set(x + 2, ey, "flower_gold"); s.set(x + 3, ey, "flower_gold")


# ------------------------------------------------------------------ held items
def draw_items(s, spec, L, face, top, hand_y, x0, x1, stride):
    item = spec["item"]
    if not item:
        return
    if item == "bluelantern":                      # night merchant: a neon-blue cold-fire lantern on a short crook
        hx = (x1 + 2) if face == "down" else (x0 - 3) if face == "up" else (4 - stride)
        for y in range(hand_y - 5, hand_y + 1):
            s.set(hx, y, "timber_lo")
        s.set(hx + (1 if face != "left" else -1), hand_y - 5, "timber_lo")
        lx = hx + (1 if face != "left" else -1)
        ly = hand_y - 3
        if face == "up":                            # carried on the far side: only the top glints past the cloak
            s.set(lx, ly, "flower_blue"); s.set(lx, ly + 1, "sky")
            return
        for dy in range(0, 4):
            s.set(lx - 1, ly + dy, "flower_blue"); s.set(lx + 1, ly + dy, "flower_blue")
        s.set(lx, ly, "flower_blue"); s.set(lx, ly + 1, "white"); s.set(lx, ly + 2, "sky"); s.set(lx, ly + 3, "flower_blue")
        return
    if face == "down":
        hl, hr = x0 - 2, x1 + 1          # screen-left / screen-right hands
        if item == "hammer":
            for y in range(hand_y - 4, hand_y + 1):
                s.set(hr + 1, y, "timber")
            s.hspan(hand_y - 5, hr - 1, hr + 3, "stone_lo"); s.hspan(hand_y - 6, hr - 1, hr + 3, "stone")
            s.set(hr - 1, hand_y - 6, "stone_hi")
        elif item == "book":
            s.hspan(top + 3, 7, 12, "roof"); s.hspan(top + 4, 7, 12, "cloth"); s.hspan(top + 5, 7, 12, "moss")
            s.set(12, top + 3, "plaster_hi"); s.set(12, top + 4, "plaster_hi"); s.set(12, top + 5, "plaster_hi")
        elif item == "spear":
            for y in range(top - 10, 29):
                s.set(hr + 1, y, "timber")
            s.set(hr + 1, top - 13, "stone_hi"); s.set(hr + 1, top - 12, "stone_hi"); s.set(hr + 1, top - 11, "stone")
            s.set(hr, top - 11, "stone"); s.set(hr + 2, top - 11, "stone_lo")
            s.set(hr + 2, top - 9, "flower_rose")        # little pennant
        elif item == "mug":
            s.hspan(hand_y - 2, hl - 1, hl + 1, "white"); s.hspan(hand_y - 1, hl - 1, hl + 1, "timber_hi")
            s.hspan(hand_y, hl - 1, hl + 1, "timber"); s.set(hl - 2, hand_y - 1, "timber")
        elif item == "lute":
            for y, (a, b) in zip(range(top + 3, top + 8), [(8, 10), (7, 11), (7, 12), (7, 12), (8, 11)]):
                s.hspan(y, a, b, "timber_hi"); s.set(b, y, "timber")
            s.set(9, top + 5, "ink")
            for k in range(4):
                s.set(12 + k, top + 2 - k, "timber_lo")
        elif item == "can":
            s.hspan(hand_y, hr - 1, hr + 2, "stone"); s.hspan(hand_y + 1, hr - 1, hr + 2, "stone_lo")
            s.set(hr + 3, hand_y - 1, "stone"); s.set(hr + 3, hand_y - 2, "stone_hi")
        elif item == "sprig":
            s.set(hl, hand_y - 1, "grass"); s.set(hl - 1, hand_y - 2, "grass_hi"); s.set(hl + 1, hand_y - 2, "flower_rose")
        elif item == "staff":
            for y in range(top - 6, 29):
                s.set(hr + 1, y, "timber")
            s.set(hr + 1, top - 8, "flower_gold"); s.set(hr, top - 7, "grass"); s.set(hr + 2, top - 7, "grass")
            s.set(hr + 1, top - 7, "lamp")
        elif item == "rod":
            tip = L["head_top"] - 3
            for y in range(tip, hand_y + 1):
                s.set(hr + 1 + (1 if y < tip + 6 else 0), y, "timber_hi" if y > tip + 3 else "timber")
            s.set(hr + 3, tip, "white"); s.set(hr + 3, tip + 1, "white")
        elif item == "wick":
            for y in range(top - 10, hand_y + 2):
                s.set(hr + 1, y, "timber_lo")
            s.set(hr + 1, top - 12, "lamp"); s.set(hr + 1, top - 11, "flower_gold"); s.set(hr + 2, top - 11, "lamp")
    elif face == "up":
        hr, hl = x1 + 1, x0 - 2
        if item in ("spear", "staff", "wick"):
            x = hl - 1
            tipc = {"spear": "stone_hi", "staff": "flower_gold", "wick": "lamp"}[item]
            lo = top - (10 if item == "spear" else 6 if item == "staff" else 10)
            for y in range(lo, 29 if item != "wick" else hand_y + 2):
                s.set(x, y, "timber" if item != "wick" else "timber_lo")
            s.set(x, lo - 1, tipc); s.set(x, lo - 2, tipc)
        elif item == "hammer":
            for y in range(hand_y - 3, hand_y + 1):
                s.set(hl - 1, y, "timber")
            s.hspan(hand_y - 4, hl - 2, hl + 1, "stone_lo")
        elif item == "rod":
            for y in range(L["head_top"] - 3, hand_y + 1):
                s.set(hl - 1, y, "timber_hi")
    else:  # left profile
        hx = 9 - 2 * stride
        if item == "hammer":
            for y in range(hand_y - 3, hand_y + 1):
                s.set(hx - 1, y, "timber")
            s.hspan(hand_y - 4, hx - 3, hx + 1, "stone_lo"); s.hspan(hand_y - 5, hx - 3, hx + 1, "stone")
        elif item == "book":
            s.hspan(top + 3, 4, 7, "roof"); s.hspan(top + 4, 4, 7, "cloth"); s.set(4, top + 3, "plaster_hi")
        elif item in ("spear", "staff", "wick"):
            x = 5
            tipc = {"spear": "stone_hi", "staff": "flower_gold", "wick": "lamp"}[item]
            lo = top - (10 if item == "spear" else 6 if item == "staff" else 10)
            for y in range(lo, 29 if item != "wick" else hand_y + 2):
                s.set(x, y, "timber" if item != "wick" else "timber_lo")
            s.set(x, lo - 1, tipc); s.set(x, lo - 2, tipc)
            if item == "staff":
                s.set(x - 1, lo, "grass")
        elif item == "mug":
            s.hspan(hand_y - 1, hx - 2, hx, "timber_hi"); s.hspan(hand_y - 2, hx - 2, hx, "white")
        elif item == "lute":
            s.hspan(top + 4, 5, 8, "timber_hi"); s.hspan(top + 5, 4, 8, "timber_hi"); s.hspan(top + 6, 5, 7, "timber")
            s.set(3, top + 3, "timber_lo"); s.set(2, top + 2, "timber_lo")
        elif item == "can":
            s.hspan(hand_y, hx - 2, hx + 1, "stone"); s.hspan(hand_y + 1, hx - 2, hx + 1, "stone_lo")
            s.set(hx - 3, hand_y - 1, "stone_hi")
        elif item == "sprig":
            s.set(hx - 1, hand_y - 1, "grass"); s.set(hx - 2, hand_y - 2, "flower_rose")
        elif item == "rod":
            tip = L["head_top"] - 3
            for y in range(tip, hand_y + 1):
                s.set(hx - 1 - (1 if y < tip + 6 else 0), y, "timber_hi")
            s.set(hx - 3, tip, "white"); s.set(hx - 3, tip + 1, "white")


# ------------------------------------------------------------------ cast pose (4 frames)
CAST_GLOW = ["flower_gold", "lamp", "white", "flower_gold"]


def draw_cast_arms(s, spec, L, face, top, x0, x1, i):
    """i 0 gather, 1 raise, 2 raised + glow, 3 release forward."""
    sl, sk = spec["shirt"] if not spec["cloak"] else spec["cloak"], spec["skin"]
    glow = CAST_GLOW[i]
    if face in ("down", "up"):
        if i == 0:
            for y in range(top + 1, top + 4):
                s.hspan(y, x0 - 1, x0, sl); s.hspan(y, x1, x1 + 1, sl)
            s.hspan(top + 4, x0, x0 + 2, sk); s.hspan(top + 4, x1 - 2, x1, sk)
            s.hspan(top + 4, x0 + 3, x1 - 3, glow)
        elif i in (1, 2):
            reach = 4 if i == 1 else 6
            for side, ax in ((-1, max(2, x0 - 2)), (1, min(16, x1 + 1))):
                for y in range(top + 2 - reach, top + 2):
                    s.hspan(y, ax, ax + 1, sl)
                s.set(ax + (1 if side > 0 else 0), top + 2 - reach, s.pal.dk(sl))
                s.hspan(top + 1 - reach, ax, ax + 1, sk)
                s.set(ax + (0 if side < 0 else 1), top - reach, glow)
                if i == 2:
                    s.set(ax + (-1 if side < 0 else 2), top - reach, glow)
                    s.set(ax + (0 if side < 0 else 1), top - reach - 1, "white")
        else:
            for side in (-1, 1):
                xs = range(x0 - 2, x0) if side < 0 else range(x1 + 1, x1 + 3)
                for x in xs:
                    s.set(x, top + 2, sl); s.set(x, top + 3, s.pal.dk(sl))
                hx = x0 - 3 if side < 0 else x1 + 3
                s.set(hx, top + 2, sk); s.set(hx, top + 3, sk)
                s.set(hx + side, top + 2, glow)
    else:  # profile, facing left
        if i == 0:
            s.hspan(top + 3, 6, 9, sl); s.set(5, top + 3, sk); s.set(4, top + 3, glow)
        elif i in (1, 2):
            pts = [(8, top + 1), (7, top), (6, top - 1), (5, top - 2)] + ([(4, top - 3)] if i == 2 else [])
            for x, y in pts:
                s.set(x, y, sl); s.set(x + 1, y, s.pal.dk(sl))
            hx, hy = pts[-1][0] - 1, pts[-1][1] - 1
            s.set(hx, hy, sk); s.set(hx - 1, hy - 1, glow)
            if i == 2:
                s.set(hx - 2, hy - 1, "white"); s.set(hx - 1, hy - 2, glow)
        else:
            s.hspan(top + 2, 3, 9, sl); s.hspan(top + 3, 4, 9, s.pal.dk(sl))
            s.set(2, top + 2, sk); s.set(1, top + 2, glow); s.set(1, top + 3, "white")


# ------------------------------------------------------------------ animals
def _lift(walk, i, which):
    if not walk:
        return 0
    return [[1, 0, 0, 0], [0, 0, 1, 0]][which][i]


def dog_frame(s, spec, face, walk, i, blink):
    fur, spot, belly = spec["fur"], spec["spot"], spec["belly"]
    fdk = s.pal.dk(fur)
    bob = (-1 if i % 2 == 1 else 0) if walk else (1 if i == 2 else 0)
    wag = [0, 1, 0, -1][i]
    if face == "down":
        for y in range(23 + bob, 30):
            s.hspan(y, 6, 13, fur); s.set(13, y, fdk)
        s.hspan(27 + bob, 8, 11, belly)
        for x0, l in ((7, _lift(walk, i, 0)), (11, _lift(walk, i, 1))):
            s.hspan(30 - l, x0, x0 + 1, belly); s.hspan(29 - l, x0, x0 + 1, fur)
        ht = 17 + bob
        for y, (a, b) in zip(range(ht, ht + 7), [(6, 13), (5, 14), (5, 14), (5, 14), (6, 13), (6, 13), (7, 12)]):
            s.hspan(y, a, b, fur); s.set(b, y, fdk)
        for y in range(ht + 1, ht + 6):                     # floppy ears
            s.set(4, y, spot); s.set(15, y, s.pal.dk(spot))
        s.set(5, ht, spot); s.set(14, ht, spot)
        s.hspan(ht, 8, 10, spot)                             # brown patch
        if blink:
            s.set(7, ht + 3, "ink"); s.set(12, ht + 3, "ink")
        else:
            s.set(7, ht + 2, "ink"); s.set(7, ht + 3, "ink"); s.set(12, ht + 2, "ink"); s.set(12, ht + 3, "ink")
        s.hspan(ht + 4, 8, 11, belly); s.hspan(ht + 5, 8, 11, belly)
        s.hspan(ht + 4, 9, 10, "ink")                        # nose
        s.set(10, ht + 6, "flower_rose")                     # tongue
        s.set(14 + (1 if wag > 0 else 0), 22 + bob, fur); s.set(14, 23 + bob, fur)
    elif face == "up":
        for y, (a, b) in zip(range(22 + bob, 31), [(6, 13), (5, 14), (5, 14), (5, 14), (5, 14), (5, 14), (6, 13), (6, 13), (6, 13)]):
            s.hspan(y, a, b, fur); s.set(b, y, fdk)
        s.hspan(25 + bob, 7, 10, spot)
        s.hspan(30 - _lift(walk, i, 0), 6, 7, fdk); s.hspan(30 - _lift(walk, i, 1), 12, 13, fdk)
        ht = 17 + bob
        for y, (a, b) in zip(range(ht, ht + 5), [(6, 13), (5, 14), (5, 14), (5, 14), (6, 13)]):
            s.hspan(y, a, b, fur); s.set(b, y, fdk)
        for y in range(ht + 1, ht + 5):
            s.set(4, y, spot); s.set(15, y, s.pal.dk(spot))
        tx = 10 + wag
        for y in range(18 + bob, 23 + bob):
            s.set(tx, y, fur)
        s.set(tx, 17 + bob, spot)
    else:
        for y, (a, b) in zip(range(22 + bob, 28 + bob), [(8, 15), (7, 16), (7, 16), (7, 16), (7, 16), (8, 15)]):
            s.hspan(y, a, b, fur); s.set(b, y, fdk)
        s.hspan(22 + bob, 11, 14, spot); s.hspan(23 + bob, 12, 14, spot)
        s.hspan(27 + bob, 8, 14, belly)
        pos = ([[(7, 0), (10, 1), (13, 1), (15, 0)], [(8, 0), (9, 0), (13, 0), (14, 0)],
                [(7, 1), (10, 0), (13, 0), (15, 1)], [(8, 0), (9, 0), (13, 0), (14, 0)]][i]
               if walk else [(8, 0), (10, 0), (13, 0), (15, 0)])
        for k, (x, l) in enumerate(pos):
            for y in range(28 + bob, 31 - l):
                s.set(x, y, belly if y == 30 - l else (fur if k % 2 == 0 else fdk))
        ht = 17 + bob
        for y, (a, b) in zip(range(ht, ht + 6), [(4, 9), (3, 9), (3, 9), (3, 9), (4, 9), (5, 8)]):
            s.hspan(y, a, b, fur)
        s.hspan(ht + 3, 1, 3, belly); s.hspan(ht + 4, 1, 3, belly); s.set(1, ht + 3, "ink")   # snout + nose
        s.set(2, ht + 5, "flower_rose")
        for y in range(ht, ht + 5):                         # ear
            s.set(8, y, spot); s.set(9, y, s.pal.dk(spot))
        s.set(5, ht + 2, "ink")
        if not blink:
            s.set(5, ht + 1, "ink")
        tw = [0, 1, 0, 1][i]
        s.set(16, 21 + bob - tw, fur); s.set(17, 20 + bob - tw, fur); s.set(17, 19 + bob - tw, spot)


def goat_frame(s, spec, face, walk, i, blink):
    fur, spot, belly = spec["fur"], spec["spot"], spec["belly"]
    fdk = s.pal.dk(fur)
    bob = (-1 if i % 2 == 1 else 0) if walk else (1 if i == 2 else 0)
    chew = i % 2
    horn = "stone"
    if face in ("down", "up"):
        for y in range(21 + bob, 28):
            s.hspan(y, 5, 14, fur); s.set(14, y, fdk)
        s.hspan(27, 5, 14, fdk)
        for x0, l in ((6, _lift(walk, i, 0)), (12, _lift(walk, i, 1))):
            for y in range(28, 31 - l):
                s.hspan(y, x0, x0 + 1, fur if y < 30 - l else "stone_lo")
        ht = 14 + bob
        for y, (a, b) in zip(range(ht, ht + 8), [(7, 12), (6, 13), (6, 13), (6, 13), (7, 12), (7, 12), (8, 11), (8, 11)]):
            s.hspan(y, a, b, fur); s.set(b, y, fdk)
        s.set(6, ht - 1, horn); s.set(5, ht - 2, horn); s.set(5, ht - 3, s.pal.dk(horn))
        s.set(13, ht - 1, horn); s.set(14, ht - 2, horn); s.set(14, ht - 3, s.pal.dk(horn))
        s.set(4, ht + 2, fur); s.set(15, ht + 2, fdk)       # sideways ears
        if face == "down":
            if blink:
                s.set(7, ht + 3, "ink"); s.set(12, ht + 3, "ink")
            else:
                s.set(7, ht + 2, "ink"); s.set(7, ht + 3, "flower_gold"); s.set(12, ht + 2, "ink"); s.set(12, ht + 3, "flower_gold")
            s.hspan(ht + 6, 9, 10, "flower_rose" if chew else "stone_hi")
            s.set(9, ht + 8, spot); s.set(10, ht + 8, spot); s.set(9, ht + 9, spot)   # beard
            s.set(9, ht + 9, "flower_gold"); s.set(10, ht + 9, "flower_gold")          # bell
        else:
            s.hspan(ht + 1, 8, 11, spot)
            s.set(10, 20 + bob, spot); s.set(10, 19 + bob, fur)   # tail tuft
    else:
        for y, (a, b) in zip(range(21 + bob, 27 + bob), [(8, 16), (7, 17), (7, 17), (7, 17), (7, 17), (8, 16)]):
            s.hspan(y, a, b, fur); s.set(b, y, fdk)
        s.hspan(26 + bob, 8, 15, belly)
        s.set(17, 20 + bob, fur); s.set(18, 19 + bob, fur)
        pos = ([[(7, 0), (10, 1), (13, 1), (16, 0)], [(8, 0), (9, 0), (14, 0), (15, 0)],
                [(7, 1), (10, 0), (13, 0), (16, 1)], [(8, 0), (9, 0), (14, 0), (15, 0)]][i]
               if walk else [(8, 0), (10, 0), (14, 0), (16, 0)])
        for k, (x, l) in enumerate(pos):
            for y in range(27 + bob, 31 - l):
                s.set(x, y, "stone_lo" if y == 30 - l else (fur if k % 2 == 0 else fdk))
        ht = 14 + bob
        for y, (a, b) in zip(range(ht, ht + 7), [(4, 8), (3, 9), (2, 9), (2, 9), (2, 8), (3, 7), (6, 9)]):
            s.hspan(y, a, b, fur)
        for y in range(ht + 2, ht + 8):
            s.set(9, y, fur); s.set(10, y, fdk)                 # neck
        s.set(6, ht - 1, horn); s.set(7, ht - 2, horn); s.set(8, ht - 2, horn); s.set(9, ht - 1, s.pal.dk(horn))
        s.set(9, ht + 1, fur); s.set(10, ht + 1, fur)          # ear
        s.set(4, ht + 2, "ink")
        if not blink:
            s.set(4, ht + 1, "flower_gold")
        s.set(2, ht + 4, "flower_rose" if chew else fdk)
        s.set(3, ht + 7, spot); s.set(3, ht + 6, spot)          # beard
        s.set(7, ht + 7, "flower_gold")                          # bell


def chicken_frame(s, spec, face, walk, i, blink):
    fur, spot, belly = spec["fur"], spec["spot"], spec["belly"]
    fdk = s.pal.dk(fur)
    bob = (-1 if i % 2 == 1 else 0) if walk else (0 if i != 2 else 1)
    peck = (not walk) and i == 2
    if face in ("down", "up"):
        for y, (a, b) in zip(range(22 + bob, 29), [(7, 12), (6, 13), (5, 14), (5, 14), (5, 14), (6, 13), (7, 12)]):
            s.hspan(y, a, b, fur); s.set(b, y, fdk)
        for y in range(24 + bob, 28, 2):
            s.set(7, y, spot); s.set(11, y, spot)
        for x, l in ((8, _lift(walk, i, 0)), (11, _lift(walk, i, 1))):
            s.set(x, 29 - l, "flower_gold"); s.set(x, 30 - l, "flower_gold"); s.set(x - 1, 30 - l, "flower_gold")
        ht = 17 + bob + (1 if peck else 0)
        for y, (a, b) in zip(range(ht, ht + 5), [(8, 11), (7, 12), (7, 12), (7, 12), (8, 11)]):
            s.hspan(y, a, b, fur); s.set(b, y, fdk)
        s.set(9, ht - 1, "roof_hi"); s.set(10, ht - 1, "roof_hi"); s.set(10, ht - 2, "roof_hi")
        if face == "down":
            s.set(9, ht + 3, "flower_gold"); s.set(10, ht + 3, "flower_gold"); s.set(9, ht + 4, "roof_hi")
            if not blink:
                s.set(8, ht + 2, "ink"); s.set(11, ht + 2, "ink")
            else:
                s.set(8, ht + 2, fdk); s.set(11, ht + 2, fdk)
        else:
            for y in range(19 + bob, 23 + bob):                # tail feathers up
                s.set(9, y, spot); s.set(10, y - 1, fdk)
    else:
        for y, (a, b) in zip(range(22 + bob, 29), [(8, 13), (7, 14), (6, 15), (6, 15), (6, 15), (7, 14), (8, 13)]):
            s.hspan(y, a, b, fur); s.set(b, y, fdk)
        s.hspan(24 + bob, 9, 13, spot); s.hspan(25 + bob, 10, 13, s.pal.dk(spot))   # wing
        s.set(15, 20 + bob, fur); s.set(16, 19 + bob, spot); s.set(16, 21 + bob, fur); s.set(15, 21 + bob, fur)
        st = [(0, 1), (1, 0), (1, 0), (0, 1)][i] if walk else (0, 0)
        for x, l in ((9, st[0]), (11, st[1])):
            s.set(x, 29 - l, "flower_gold"); s.set(x, 30 - l, "flower_gold"); s.set(x - 1, 30 - l, "flower_gold")
        ht = 17 + bob + (2 if peck else 0)
        hx = 4 if peck else 5
        for y, (a, b) in zip(range(ht, ht + 6), [(hx + 1, hx + 4), (hx, hx + 4), (hx, hx + 4), (hx, hx + 5), (hx + 1, hx + 5), (hx + 2, hx + 5)]):
            s.hspan(y, a, b, fur)
        s.set(hx + 1, ht - 1, "roof_hi"); s.set(hx + 2, ht - 1, "roof_hi"); s.set(hx + 2, ht - 2, "roof_hi")
        s.set(hx - 1, ht + 2, "flower_gold"); s.set(hx - 2, ht + 2, "flower_gold")
        s.set(hx, ht + 4, "roof_hi")
        s.set(hx + 1, ht + 1, "ink" if not blink else fdk)


def owl_frame(s, spec, face, walk, i, blink):
    fur, spot, belly = spec["fur"], spec["spot"], spec["belly"]
    fdk = s.pal.dk(fur)
    # owls hop: squash on the ground, stretch up (feet stay planted so the pivot is stable)
    sq = [0, -1, -2, -1][i] if walk else [0, 0, 1, 0][i]
    top = 15 + sq
    rows = list(range(top, 30))
    n = len(rows)
    for k, y in enumerate(rows):
        ind = 2 if k in (0, n - 1) else 1 if k in (1, n - 2) else 0
        s.hspan(y, 5 + ind, 14 - ind, fur); s.set(14 - ind, y, fdk)
    s.set(5, top - 1, fur); s.set(6, top - 2, fur)              # ear tufts
    s.set(14, top - 1, fdk); s.set(13, top - 2, fur)
    s.hspan(30, 7, 8, "flower_gold"); s.hspan(30, 11, 12, "flower_gold")
    if face == "down":
        for y in range(top + 1, top + 7):                       # heart face disc
            ind = 0 if 1 < y - top < 5 else 1
            s.hspan(y, 6 + ind, 13 - ind, belly)
        s.set(9, top + 1, fur); s.set(10, top + 1, fur)
        ey = top + 3
        if blink:
            s.hspan(ey, 7, 8, "ink"); s.hspan(ey, 11, 12, "ink")
        else:
            for ex in (7, 11):
                s.hspan(ey - 1, ex, ex + 1, "ink"); s.hspan(ey, ex, ex + 1, "ink")
                s.set(ex, ey - 1, "flower_gold")
        s.set(9, top + 5, "flower_gold"); s.set(10, top + 5, "timber_lo")
        for y in range(top + 8, 29, 2):                         # speckled chest
            s.set(8, y, spot); s.set(11, y, spot); s.set(9 + (y % 4 == 0), y + 1, spot)
        flap = walk and i in (1, 2)
        s.set(4 if not flap else 3, top + 8, fdk); s.set(15 if not flap else 16, top + 8, fdk)
        s.set(4, top + 9, fur); s.set(15, top + 9, fdk)
    elif face == "up":
        for y in range(top + 3, 29, 3):
            s.hspan(y, 7, 12, spot)
        s.hspan(28, 8, 11, fdk)
    else:
        for y in range(top + 1, top + 7):
            s.hspan(y, 5, 9, belly)
        s.set(6, top + 3, "ink")
        if not blink:
            s.set(6, top + 2, "ink"); s.set(7, top + 3, "flower_gold")
        s.set(4, top + 4, "flower_gold")
        for y in range(top + 6, 29):                            # folded wing
            s.hspan(y, 10, 13, fdk if y % 3 else spot)
        s.set(14, 27, fdk); s.set(15, 28, fdk)


ANIMAL = {"dog": dog_frame, "goat": goat_frame, "chicken": chicken_frame, "owl": owl_frame}
