"""16 px item icons (build.py draw_icons style, biome palette only): potion bottles and ingredients."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_lib"))
import hmart as H  # noqa: E402

POTIONS = {   # id: (name, liquid hi, liquid mid, liquid lo, shape)
    "potion_health": ("Heartroot Tonic (health)", "flower_rose", "roof_hi", "roof_lo", "round"),
    "potion_mana": ("Moonwell Draught (mana)", "sky", "flower_blue", "cloth", "round"),
    "potion_stamina": ("Hearthfire Brew (stamina)", "lamp", "flower_gold", "timber_hi", "tall"),
    "potion_nightsight": ("Owl-Eye Elixir (night sight)", "flower_rose", "cloth", "shadow", "flask"),
    "potion_antidote": ("Mossbalm (antidote)", "grass_hi", "grass", "moss", "flask"),
    "potion_coldfire": ("Cold-Fire Phial (frost ward)", "white", "sky", "flower_blue", "tall"),
    "bottle_empty": ("Empty Bottle", None, None, None, "round"),
}


def potion(spec):
    _, hi, mid, lo, shape = spec
    ic = H.Icon()
    glass_hi, glass = "white", "plaster_hi"
    if shape == "round":
        cy, r = 10, 4.6
        for y in range(16):
            for x in range(16):
                d = math.hypot(x - 7.5, y - cy)
                if d <= r:
                    if hi and y >= cy - 1.5:
                        ic.set(x, y, hi if (x < 7 and y < cy + 1) else lo if d > r - 1.1 else mid)
                    else:
                        ic.set(x, y, glass if d > r - 1.1 else "stone_hi" if not hi else glass)
        neck = (6, 9, 3, 5)
    elif shape == "tall":
        for y in range(5, 15):
            for x in range(5, 11):
                edge = x in (5, 10) or y == 14
                if hi and y >= 7:
                    ic.set(x, y, lo if edge else (hi if x == 6 else mid))
                else:
                    ic.set(x, y, glass if edge else "stone_hi")
        neck = (6, 9, 2, 4)
    else:   # flask (conical)
        for y in range(6, 15):
            hw = 1 + (y - 6) * 0.6
            for x in range(int(7.5 - hw), int(7.5 + hw) + 1):
                edge = abs(x - 7.5) > hw - 1 or y == 14
                if hi and y >= 9:
                    ic.set(x, y, lo if edge else (hi if x < 7 else mid))
                else:
                    ic.set(x, y, glass)
        neck = (7, 8, 2, 5)
    x0, x1, y0, y1 = neck
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            ic.set(x, y, glass)
    for x in range(x0, x1 + 1):
        ic.set(x, y0 - 1, "timber_hi"); ic.set(x, y0 - 2, "timber")      # cork
    ic.set(x0, y1 + 2, glass_hi)
    if hi:
        ic.set(5 if shape != "flask" else 6, 11, "white")                # the glow glint
    ic.outline()
    return ic


def moonpetal():
    ic = H.Icon()
    for y in range(8, 15):
        ic.set(8, y, "moss")
    ic.set(6, 11, "grass_hi"); ic.set(7, 12, "grass_hi"); ic.set(9, 12, "moss"); ic.set(10, 11, "moss")
    for (x, y) in ((5, 4), (6, 3), (6, 4), (10, 3), (10, 4), (11, 4), (7, 6), (9, 6), (8, 1), (8, 2), (5, 5), (11, 5)):
        ic.set(x, y, "flower_blue")
    for (x, y) in ((6, 5), (10, 5), (8, 3), (7, 4), (9, 4), (7, 5), (9, 5)):
        ic.set(x, y, "white")
    ic.set(8, 4, "flower_gold"); ic.set(8, 5, "flower_gold")
    ic.outline()
    return ic


def red_toadstool():
    ic = H.Icon()
    for y in range(9, 15):
        for x in range(6, 10):
            ic.set(x, y, "plaster_hi" if x < 8 else "plaster")
    for x in range(5, 11):
        ic.set(x, 10, "plaster_lo")                                         # skirt ring
    for y in range(2, 9):
        for x in range(1, 15):
            if ((x - 7.5) / 6.6) ** 2 + ((y - 8.2) / 6.0) ** 2 <= 1:
                ic.set(x, y, "roof_hi" if x < 6 else "roof" if x < 12 else "roof_lo")
    for x in range(2, 14):
        ic.set(x, 8, "lamp" if x % 2 else "plaster_lo")                     # warm gills
    for (x, y) in ((4, 5), (5, 5), (8, 3), (9, 3), (11, 5), (7, 6), (12, 7), (3, 7)):
        ic.set(x, y, "white")
    ic.outline()
    return ic


def herb_bundle():
    ic = H.Icon()
    for k in range(5):
        x0 = 4 + k * 2
        for y in range(2, 11):
            ic.set(x0 + (1 if y < 5 and k % 2 else 0), y, ("grass", "moss", "grass_hi", "leaf_deep", "grass")[k])
        ic.set(x0 - 1, 3 + k % 3, "grass_hi"); ic.set(x0 + 1, 5 + k % 2, "moss")
    for x in range(5, 12):
        ic.set(x, 10, "roof"); ic.set(x, 11, "roof_lo")                    # red string tie
    for k in range(4):
        ic.set(6 + k, 12 + k % 2, "timber"); ic.set(6 + k, 13 + k % 2, "timber_lo")   # stems
    ic.set(7, 3, "flower_rose"); ic.set(10, 4, "white")
    ic.outline()
    return ic


def mint_sprig():
    ic = H.Icon()
    for y in range(4, 15):
        ic.set(8, y, "moss")
    for (cx, cy, s) in ((6, 5, -1), (10, 5, 1), (6, 9, -1), (10, 9, 1), (8, 2, 0)):
        for y in range(cy - 1, cy + 2):
            for x in range(cx - 1, cx + 2):
                if abs(x - cx) + abs(y - cy) <= 2:
                    ic.set(x, y, "grass_hi" if (x + y) % 3 == 0 else "grass")
        ic.set(cx, cy, "moss")
    ic.outline()
    return ic


def sage_leaf():
    ic = H.Icon()
    for k in range(12):
        t = k / 11
        cx, cy = 3 + t * 10, 12 - t * 9
        w = 2.6 * math.sin(t * math.pi) + 0.4
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if dx * dx + dy * dy <= w * w:
                    ic.set(cx + dx, cy + dy, "stone_hi" if dx < 0 else "grass")
    for k in range(10):
        ic.set(3 + k, 12 - k * 0.9, "moss")
    ic.set(2, 13, "timber"); ic.set(1, 14, "timber")
    ic.outline()
    return ic


def all_icons():
    out = []
    for k, spec in POTIONS.items():
        out.append((k, potion(spec), {"name": spec[0], "kind": "potion" if spec[1] else "container"}))
    out.append(("ing_moonpetal", moonpetal(), {"name": "Moonpetal", "kind": "ingredient", "note": "matches the game's moonpetal item icon"}))
    out.append(("ing_red_toadstool", red_toadstool(), {"name": "Red Toadstool", "kind": "ingredient"}))
    out.append(("ing_herb_bundle", herb_bundle(), {"name": "Garden Herb Bundle", "kind": "ingredient"}))
    out.append(("ing_mint", mint_sprig(), {"name": "Garden Mint", "kind": "ingredient"}))
    out.append(("ing_sage", sage_leaf(), {"name": "Garden Sage", "kind": "ingredient"}))
    return out
