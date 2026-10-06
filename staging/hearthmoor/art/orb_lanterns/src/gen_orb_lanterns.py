"""Orb lanterns pack generator (Hearthmoor Art seat). Run:  python3 gen_orb_lanterns.py
Writes ../ (the orb_lanterns pack). Reads the hd2d-suite repo read-only."""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "_lib"))
import hmart as H  # noqa: E402
import kit_orb_lanterns as KO  # noqa: E402
import orb_fx as OF  # noqa: E402
from PIL import Image  # noqa: E402

OUT = HERE.parent
LIGHT = {c: {"color": KO.FISH[c][5], "pool_hi_mid_lo": [H.ALLC[n] for n in OF.FISHC[c][0]]} for c in KO.FISH}


# ============================================================== icons (inventory, biome palette only)
ICOL = {"blue": ("sky", "flower_blue", "cloth"), "violet": ("flower_rose", "cloth", "shadow"), "red": ("roof_hi", "roof", "roof_lo")}


def orb_icon(colour, mount):
    ic = H.Icon()
    hi, mid, lo = ICOL[colour]
    cy = 6 if mount != "table" else 7
    r = 4.6 if mount != "table" else 4.2
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - cy)
            if d <= r:
                ic.set(x, y, "cloth" if d > r - 1.2 else ("sky" if (x + y) % 3 == 0 and d < 2 else "flower_blue" if d < r - 2 else "cloth"))
    for (x, y) in ((6, cy), (7, cy), (8, cy - 1)):
        ic.set(x, y, mid)
    ic.set(9, cy, hi); ic.set(5, cy - 1, lo); ic.set(5, cy + 1, lo)
    ic.set(6, cy + 2, hi); ic.set(7, cy + 2, mid)
    ic.set(5, cy - 3, "white"); ic.set(6, cy - 3, "white")
    if mount == "table":
        for x in range(5, 11):
            ic.set(x, 12, "flower_gold"); ic.set(x, 13, "timber"); ic.set(x, 14, "timber_lo")
    elif mount == "hanging":
        for y in range(0, 2):
            ic.set(7, y, "shadow")
        ic.set(6, 1, "flower_gold"); ic.set(7, 1, "flower_gold"); ic.set(8, 1, "flower_gold")
        ic.set(7, 11, "flower_gold"); ic.set(7, 12, "flower_gold")
    elif mount == "standing":
        for y in range(11, 15):
            ic.set(7, y, "shadow"); ic.set(8, y, "stone_lo")
        for x in range(5, 11):
            ic.set(x, 11, "flower_gold")
        ic.set(5, 15, "shadow"); ic.set(10, 15, "shadow")
    else:
        for y in range(11, 15):
            for x in range(5, 11):
                ic.set(x, y, "stone" if x < 9 else "stone_lo")
        ic.set(5, 13, "moss"); ic.set(6, 14, "moss")
        for x in range(5, 11):
            ic.set(x, 11, "leaf_deep")
    ic.outline()
    return ic


def main():
    m24 = H.write_fx(OUT / "gamefx", "orb_fx_24", OF.FX24, 24)
    m32 = H.write_fx(OUT / "gamefx", "orb_fx_32", OF.FX32, 32)
    m48 = H.write_fx(OUT / "gamefx", "orb_fx_48", OF.FX48, 48)
    extra = {}
    for c in KO.FISH:
        for mt, fxn, place in (("table", f"orb_small_{c}", "house: table / shelf / sill"), ("hanging", f"orb_small_{c}", "house: ceiling beam (hook at 2.6 m)"),
                               ("standing", f"orb_small_{c}", "house corner / porch"), ("garden", f"orb_large_{c}", "garden / path / plaza")):
            extra[f"orb_{mt}_{c}"] = {"fx": fxn, "pool": f"orb_pool_{c}", "placement": place, "fish": c,
                                      "light": {"color": KO.FISH[c][5], "pool_colors": LIGHT[c]["pool_hi_mid_lo"]},
                                      "placeable": True, "item_icon": f"orb_{mt}_{c}"}
    extra["orb_grand"] = {"fx": "orb_grand_mix", "pool": ["orb_pool_blue", "orb_pool_violet", "orb_pool_red"], "placement": "garden centre / plaza showpiece",
                          "light": {"color": "#7a8cff"}, "placeable": True}
    built, km = H.build_kit(OUT / "kit", KO.pieces, extra)
    print("kit", len(built))
    icons = []
    for c in KO.FISH:
        for mt in ("table", "hanging", "standing", "garden"):
            icons.append((f"orb_{mt}_{c}", orb_icon(c, mt), {"piece": f"orb_{mt}_{c}", "name": f"{c.title()} Fish Orb ({mt})"}))
    (OUT / "icons").mkdir(exist_ok=True)
    H.write_icons(OUT / "icons", "orb_lantern_icons", icons)
    rd = OUT / "renders"; rd.mkdir(exist_ok=True)
    for n, pc in built.items():
        lc = pc.markers.get("lamp_color")
        im, _ = H.render_mesh(pc.mesh, "night", [((0, pc.markers["lamps"][0][1], 0.5), lc, 3.5, 1.0)], pad=6)
        im.save(rd / f"{n}_night.png")
    house = vignette(built, m24, m32, m48, "house")
    garden = vignette(built, m24, m32, m48, "garden")
    house.save(rd / "vignette_house_night.png"); garden.save(rd / "vignette_garden_night.png")
    contact(built, m24, m32, m48, house, garden)
    H.finish_pack(OUT, README)
    (OUT / "READY.txt").write_text("orb_lanterns: READY (2026-10-05, Hearthmoor Art seat)\nSee README.md + contact_sheet.png. 13 kit pieces, 3 gamefx atlases (24/32/48 px), 12 inventory icons.\n")


def grid(M, K, w, d, col, mat, n=0.5, y=0.0, vertical=False, z=0.0, cx=None):
    """a floor (or wall) made of small quads so lamp light falls off across it (flat shading per face)"""
    R = H.rng(104, "grid", w, d)
    nx, nz = int(w / n), int(d / n)
    for i in range(nx):
        for j in range(nz):
            c = K.mix(col, "#000000", R.uniform(0, 0.05))
            x0 = -w / 2 + i * n
            if vertical:
                y0 = j * n
                M.quad((x0, y0, z), (x0 + n, y0, z), (x0 + n, y0 + n, z), (x0, y0 + n, z), c, mat=mat)
            else:
                z0 = -d / 2 + j * n
                M.quad((x0, y, z0 + n), (x0 + n, y, z0 + n), (x0 + n, y, z0), (x0, y, z0), c, mat=mat)


def decal_over(can, fr, center, org, zb, lift=0.02):
    """paste a pre-squashed decal frame centred on world `center` (plane y=lift), per-pixel depth tested"""
    ce, se = math.cos(H.ELEV), math.sin(H.ELEV)
    px_, py_ = H.project((center[0], lift, center[2]), org)
    src, dst = fr.load(), can.load()
    n = fr.width
    for y in range(fr.height):
        for x in range(n):
            if src[x, y][3] == 0:
                continue
            cx_, cy_ = int(round(px_ - n / 2 + x)), int(round(py_ - fr.height / 2 + y))
            if not (0 <= cx_ < can.width and 0 <= cy_ < can.height):
                continue
            dep = (center[2] + (y - fr.height / 2) / (se * H.PX_PER_M)) * ce + lift * se
            if zb[cy_, cx_] > dep + 0.08:
                continue
            dst[cx_, cy_] = src[x, y]


def vignette(built, m24, m32, m48, kind):
    """a little room corner / garden patch at night with the lanterns lit, light pools and animated orb billboards"""
    K = H.kit_module()
    M = K.Mesh()
    cx = H.kit_ctx()
    lights, orbs = [], []
    def put(name, pos):
        pc = built[name]
        M.add(pc.mesh.xf(pos))
        lp = pc.markers["lamps"][0]
        p = (pos[0] + lp[0], pos[1] + lp[1], pos[2])
        lights.append((p, pc.markers["lamp_color"], pc.markers["lamp_range"], 1.0))
        orbs.append((name, p))
    if kind == "house":
        grid(M, K, 6.0, 4.0, K.mix(cx.c("timber_lo"), cx.c("timber"), 0.4), "timber")                         # floorboards
        for k in range(12):
            M.add(K.box(0.02, 0.01, 4.0, cx.c("timber_lo"), "paint", y0=0.0).xf((-3 + k * 0.5, 0, 0)))
        grid(M, K, 6.0, 2.7, K.mix(cx.c("plaster_lo"), cx.c("shadow"), 0.3), "paint", vertical=True, z=-2.0)      # back wall
        M.add(K.box(6.0, 0.25, 0.3, cx.c("timber"), "timber", y0=2.6).xf((0, 0, -0.4)))                       # ceiling beam
        M.add(K.box(1.2, 0.08, 0.7, cx.c("timber_hi"), "timber", y0=0.72).xf((-1.4, 0, -1.2)))                # table
        for sx in (-1, 1):
            for sz in (-1, 1):
                M.add(K.box(0.07, 0.72, 0.07, cx.c("timber"), "timber", y0=0).xf((-1.4 + sx * 0.5, 0, -1.2 + sz * 0.27)))
        M.add(K.box(1.0, 0.06, 0.3, cx.c("timber"), "timber", y0=1.5).xf((1.6, 0, -1.85)))                    # shelf
        put("orb_table_blue", (-1.6, 0.8, -1.2)); put("orb_table_red", (-1.1, 0.8, -1.25))
        put("orb_table_violet", (1.6, 1.56, -1.85))
        put("orb_hanging_violet", (0.2, 0, -0.4))
        put("orb_standing_blue", (2.3, 0, -0.6))
    else:
        grid(M, K, 7.0, 4.6, K.mix(cx.c("grass"), cx.c("leaf_deep"), 0.5), "grass")
        for k in range(9):                                                                                    # path stones
            M.add(K.cylinder(0.28, 0.3, 0.04, 8, cx.c("stone"), "stone", y0=0.0).xf((-3.0 + k * 0.75, 0, 0.6 + math.sin(k) * 0.3)))
        for k in range(14):                                                                                   # flowers
            M.add(K.sphere(0.12, 5, 3, cx.c(("flower_rose", "flower_gold", "flower_blue")[k % 3])).xf((-3.2 + k * 0.48, 0.15, -1.3 + (k % 3) * 0.2)))
        M.add(K.box(7.0, 1.0, 0.12, cx.c("timber"), "timber", y0=0).xf((0, 0, -2.2)))                         # fence
        put("orb_garden_blue", (-2.4, 0, -0.5)); put("orb_garden_violet", (0.0, 0, -0.9)); put("orb_garden_red", (2.4, 0, -0.5))
        put("orb_grand", (0.0, 0, 1.3))
    im, org, zb = H.render_mesh(M, "night", lights, pad=14, depth=True)
    can = Image.new("RGBA", im.size, (10, 10, 22, 255))
    can.alpha_composite(im)
    for name, p in orbs:                                   # light pools on the surface under each orb (depth-tested)
        c = "blue" if "blue" in name else "violet" if "violet" in name else "red" if "red" in name else None
        cols = OF.FISHC[c][0] if c else ("neon_violet_hi", "neon_blue", "neon_red_lo")
        surf = 0.0
        if "table" in name:
            surf = 0.8 if p[1] < 1.4 else 1.56
        r = 26 if "grand" not in name else 44
        pl = H.pool_layer((2 * r + 4, 2 * r + 4), (r + 2, r + 2), r if "table" not in name else 14, cols, name)
        decal_over(can, pl, (p[0], 0, p[2] + 0.15), org, zb, surf + 0.01)
    for name, p in orbs:
        if "grand" in name:
            fr, pv = H.fx_frame(OUT / "gamefx/orb_fx_32.png", m32, "orb_grand_mix", 2), (16, 16)
            fr = fr.resize((22, 22), Image.NEAREST) if False else fr
        elif "garden" in name:
            c = name.split("_")[-1]
            fr, pv = H.fx_frame(OUT / "gamefx/orb_fx_32.png", m32, f"orb_large_{c}", 1), (16, 16)
        else:
            c = name.split("_")[-1]
            fr, pv = H.fx_frame(OUT / "gamefx/orb_fx_24.png", m24, f"orb_small_{c}", 1), (12, 12)
        H.billboard_over(can, fr, (p[0], p[1], p[2] + 0.4), org, zb, pv)
    if kind == "garden":
        for c, p in (("green", (-3.2, 1.1, 0.8)), ("pink", (3.1, 1.1, 1.0))):
            pl = H.fx_frame(OUT / "gamefx/orb_fx_48.png", m48, f"glow_orb_pool_{c}", 0)
            pp = H.project((p[0], 0, p[2] + 0.2), org)
            can.alpha_composite(pl, (int(pp[0] - 24), int(pp[1] - 24)))
            H.billboard_over(can, H.fx_frame(OUT / "gamefx/orb_fx_48.png", m48, f"glow_orb_{c}", 2), p, org, zb, (24, 47))
    hero = H.SP.frame(H.PAL, "wildcaller", "down", "idle", 0).image()
    H.billboard_over(can, hero, (0.9 if kind == "house" else 1.4, 0, 0.9 if kind == "house" else 0.4), org, zb, (10, 31))
    return can


def strip_of(png, meta, name, cell):
    e = meta["effects"][name]
    s = Image.new("RGBA", (cell * e["frames"], cell), (12, 14, 26, 255))
    for i in range(e["frames"]):
        s.alpha_composite(H.fx_frame(png, meta, name, i), (i * cell, 0))
    return s


def contact(built, m24, m32, m48, house, garden):
    S = H.Sheet("Orb lanterns - water orbs with glowing fish (blue / violet / red), house + garden placeables",
                "kit .glb (13) + animated orb billboards (24 / 32 px) + light pools + hovering glow orbs (48 px) + inventory icons; 4x nearest unless noted")
    S.section("Night vignettes (3x)", "house corner: table x2, shelf, hanging, standing | garden: three garden posts, the grand orb, green + pink glow orbs; hero for scale")
    S.cell(house.crop(house.getbbox()), "vignette_house_night.png", "lights from each orb's lamp marker; pools = orb_pool_<colour>", k=3)
    S.cell(garden.crop(garden.getbbox()), "vignette_garden_night.png", "", k=3)
    S.section("Animated fish orbs (4x, every frame)", "fish circle the orb, dim when they pass behind; caustics shimmer; bubbles rise")
    for n in m24["effects"]:
        S.cell(strip_of(OUT / "gamefx/orb_fx_24.png", m24, n, 24), n, "24 px cell, 13 px orb, 8f 6fps", k=4)
    for n in m32["effects"]:
        S.cell(strip_of(OUT / "gamefx/orb_fx_32.png", m32, n, 32), n, "32 px cell, 8f 6fps", k=4 if n != "orb_grand_mix" else 3)
    S.section("Kit pieces (night, 4x)", "orb_<table|hanging|standing|garden>_<blue|violet|red> + orb_grand")
    for n, pc in built.items():
        lc = pc.markers.get("lamp_color")
        ly = pc.markers["lamps"][0][1]
        im, org = H.render_mesh(pc.mesh, "night", [((0, ly, 0.5), lc, 3.5, 1.0)], pad=10)
        can = Image.new("RGBA", im.size, (0, 0, 0, 0))
        c = "blue" if "blue" in n else "violet" if "violet" in n else "red" if "red" in n else None
        cols = OF.FISHC[c][0] if c else ("neon_violet_hi", "neon_blue", "neon_red_lo")
        gy = 0.0
        can.alpha_composite(H.pool_layer(can.size, H.project((0, gy, 0.15), org), min(22, im.width * 0.45), cols, n))
        can.alpha_composite(im)
        k = 4 if im.height * 4 < 260 else 3 if im.height * 3 < 300 else 2
        S.cell(can, n, f"{pc.size[1]:.2f} m tall, light {pc.markers['lamp_color']} r{pc.markers['lamp_range']}", k=k)
    S.section("Light pools + glow orbs (48 px, 2x)", "orb_pool_<c> decals; hovering glow_orb_<blue|violet|red|green|pink> (shared with verdant_heart)")
    for n in m48["effects"]:
        st = strip_of(OUT / "gamefx/orb_fx_48.png", m48, n, 48)
        S.cell(st.crop((0, 0, 48 * 4, 48)), n, f"{m48['effects'][n]['kind']} {m48['effects'][n]['frames']}f (4 shown)", k=2)
    S.section("Inventory icons (16 px, 6x)", "biome palette only (HUD rule): violet fish read as rose on slate")
    S.cell(Image.open(OUT / "icons/orb_lantern_icons.png"), "orb_lantern_icons.png", "table | hanging | standing | garden  x  blue, violet, red", k=6)
    S.render(OUT / "contact_sheet.png")


README = """# Orb lanterns pack: water orbs with glowing fish (house + garden placeables)

Art seat staging pack for **Hearthmoor**. Generated by `src/gen_orb_lanterns.py` (Python + Pillow + numpy, importing
the repo's tools read-only). Bill's ask: **orb lanterns full of water with glowing fish**, in **blue, violet and red**,
placeable in a house or garden; plus his **hovering glow orbs** (blue / violet / red / green / pink) as ambient lights.
Built on the harbor `fish_orb` idea (orb on a stand, glowing water, little fish), redrawn as a full placeable family.

![contact sheet](contact_sheet.png)

## Kit (`kit/*.glb`, `kit/kit.json`, `src/kit_orb_lanterns.py`) - 13 pieces
| mount | pieces | size | where | light (lamp marker) |
|---|---|---|---|---|
| table | `orb_table_blue/violet/red` | 0.36 x 0.48 m (0.34 m orb) | table, shelf, windowsill | fixed 0.4, range 3 m |
| hanging | `orb_hanging_*` | hook at 2.6 m, orb centre 1.75 m (0.40 m orb) | ceiling beam / porch eave; no blocker | 0.45, 4 m |
| standing | `orb_standing_*` | 1.8 m (0.46 m orb) | house corner, porch | 0.45, 4.5 m |
| garden | `orb_garden_*` | 1.65 m stone post (0.60 m orb) | garden, path, plaza | 0.5, 5 m |
| showpiece | `orb_grand` | 1.95 m, 1.1 m orb, all three fish colours | garden centre / plaza | `#7a8cff`, 0.6, 7 m |

Light / pool colours per fish colour (in `kit.json` per piece: `light.color`, `light.pool_colors`):

| colour | lamp | pool hi / mid / lo | water tint |
|---|---|---|---|
| blue | `#2ab4ff` | `#a6ecff / #2ab4ff / #1c62d8` | deep blue `#123c6c` |
| violet | `#a45cf0` | `#d4a8ff / #a45cf0 / #6a34b8` | deep indigo `#2a1e5c` |
| red | `#ff5a4a` | `#ff5a4a / #e0302a / #a81c22` | deep plum `#3a1a3a` |

Each piece's `kit.json` entry also names its animated billboard (`fx`), pool decal (`pool`), placement hint and the
inventory icon id, and is flagged `placeable: true` for the house / garden decorating system.

## gamefx (`gamefx/`)
| atlas | cell | effects |
|---|---|---|
| `orb_fx_24` | 24 | `orb_small_blue/violet/red`: a whole 13 px orb (water, caustics, 2 fish circling - dim when behind - bubbles, glass glint). 8f, 6 fps, pivot [12,12] = orb centre |
| `orb_fx_32` | 32 | `orb_large_*` (21 px orb, 3 fish) for garden posts; `orb_grand_mix` (30 px orb, 5 fish in all colours) |
| `orb_fx_48` | 48 | `orb_pool_blue/violet/red` (decals), `glow_orb_blue/violet/red/green/pink` (hovering orb billboards, lift 1.1, light 0.8 / 4 m), `glow_orb_pool_green/pink` |

Anchor an orb billboard at the piece's lamp marker (orb centre); it covers the kit orb exactly and animates the fish.
Glow orbs: float one or two per garden / room (they're the same art as verdant_heart's, from the shared lib).

## Icons (`icons/orb_lantern_icons.png/.json`, 16 px + 6x preview)
12 inventory icons (`orb_<mount>_<colour>`), biome palette only like `build.py draw_icons` (violet fish read as rose
on slate, since the HUD palette has no violet).

## Neon flag
- **Uses neon:** all gamefx (orbs, fish, pools, glow orbs) and the kit `glow` material on the water + fish.
- **No neon:** the inventory icons (biome palette), and every non-glow kit material (wood, iron, brass, stone, moss).

## Drop-in steps
1. Copy `src/kit_orb_lanterns.py` to `tools/kit/` and add the import line from its docstring; place pieces by name.
2. Merge the three gamefx atlases into the house / garden gamefx (or copy `src/orb_fx.py` functions into tools/portal).
3. Add the icons to the item sheet and map `item_icon` -> piece for the placement system.
4. Regenerate: `python3 src/gen_orb_lanterns.py`.
"""


if __name__ == "__main__":
    main()
