"""Alchemy pack generator (Hearthmoor Art seat). Run:  python3 gen_alchemy.py   (writes ../, reads the repo read-only)"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "_lib"))
import hmart as H  # noqa: E402
import kit_alchemy as KA  # noqa: E402
import alchemy_fx as AF  # noqa: E402
import alchemy_icons as AI  # noqa: E402
from PIL import Image  # noqa: E402

OUT = HERE.parent
KIT_META = {f"cauldron_{c}": {"fx": [f"cauldron_brew_{c}", "cauldron_fire", f"cauldron_pool_{c}"], "brew_surface": [0, 0.98, 0],
                              "fire": [0, 0.04, 0.32], "craft_fx": f"brew_puff_{c}"} for c in KA.BREW}
KIT_META.update({"alchemy_table": {"note": "crafting station; glowing flasks + alembic"},
                 "potion_shelf": {"note": "wall prop; back against a wall"}, "herb_rack": {"note": "drying herbs; pairs with ingredient icons"}})


def main():
    fxm = H.write_fx(OUT / "gamefx", "alchemy_fx", AF.FX, 48)
    built, km = H.build_kit(OUT / "kit", KA.pieces, KIT_META)
    (OUT / "icons").mkdir(exist_ok=True)
    H.write_icons(OUT / "icons", "alchemy_icons", AI.all_icons())
    rd = OUT / "renders"; rd.mkdir(exist_ok=True)
    for n, pc in built.items():
        lc = pc.markers.get("lamp_color")
        im, _ = H.render_mesh(pc.mesh, "night", [((0, 1.2, 0.6), lc, 4, 1.0)] if lc else [], pad=6)
        im.save(rd / f"{n}_night.png")
    sc = scene(built, fxm)
    sc.save(rd / "scene_alchemy_night.png")
    contact(built, fxm, sc)
    H.finish_pack(OUT, README)
    (OUT / "READY.txt").write_text("alchemy: READY (2026-10-05, Hearthmoor Art seat)\nSee README.md + contact_sheet.png. 6 kit pieces, gamefx alchemy_fx (48 px), 12 icons (16 px).\n")


def scene(built, fxm):
    K = H.kit_module(); cx = H.kit_ctx()
    M = K.Mesh(); lights = []
    R = H.rng(104, "ascene")
    fl = K.mix(cx.c("timber_lo"), cx.c("shadow"), 0.3)
    for i in range(12):
        for j in range(8):
            x0, z0 = -3 + i * 0.5, -2 + j * 0.5
            M.quad((x0, 0, z0 + 0.5), (x0 + 0.5, 0, z0 + 0.5), (x0 + 0.5, 0, z0), (x0, 0, z0), K.mix(fl, "#000000", R.uniform(0, 0.05)), mat="timber")
    wall = K.mix(cx.c("stone_lo"), cx.c("shadow"), 0.4)
    for i in range(12):
        for j in range(6):
            x0, y0 = -3 + i * 0.5, j * 0.5
            M.quad((x0, y0, -2), (x0 + 0.5, y0, -2), (x0 + 0.5, y0 + 0.5, -2), (x0, y0 + 0.5, -2), K.mix(wall, "#000000", R.uniform(0, 0.06)), mat="stone")
    def put(n, pos):
        pc = built[n]; M.add(pc.mesh.xf(pos))
        for lp in pc.markers.get("lamps", []):
            lights.append(((pos[0] + lp[0], lp[1], pos[2] + lp[2]), pc.markers["lamp_color"], pc.markers["lamp_range"], 1.0))
    put("cauldron_green", (0.0, 0, 0.0)); put("cauldron_violet", (-2.0, 0, -0.6)); put("cauldron_blue", (2.0, 0, -0.4))
    put("alchemy_table", (-1.0, 0, -1.5)); put("potion_shelf", (1.4, 0, -1.8)); put("herb_rack", (-2.3, 0, -1.85))
    im, org, zb = H.render_mesh(M, "night", lights, pad=10, depth=True)
    can = Image.new("RGBA", im.size, (10, 10, 22, 255)); can.alpha_composite(im)
    png = OUT / "gamefx/alchemy_fx.png"
    se, ce = math.sin(H.ELEV), math.cos(H.ELEV)
    def dec(n, c, i=0):
        fr = H.fx_frame(png, fxm, n, i); p = H.project((c[0], 0, c[2]), org); src, dst = fr.load(), can.load()
        for y in range(48):
            for x in range(48):
                if src[x, y][3]:
                    X, Y = int(p[0] - 24 + x), int(p[1] - 24 + y)
                    if 0 <= X < can.width and 0 <= Y < can.height and zb[Y, X] < (c[2] + (y - 24) / (se * 18)) * ce + 0.1:
                        dst[X, Y] = src[x, y]
    for c, p in (("green", (0, 0, 0.3)), ("violet", (-2.0, 0, -0.3)), ("blue", (2.0, 0, -0.1))):
        dec(f"cauldron_pool_{c}", p, 1)
    items = []
    for c, p in (("green", (0, 0, 0)), ("violet", (-2.0, 0, -0.6)), ("blue", (2.0, 0, -0.4))):
        items.append((H.fx_frame(png, fxm, "cauldron_fire", 2), (p[0] - 0.05, 0.04, p[2] + 0.32), (24, 47)))
        items.append((H.fx_frame(png, fxm, f"cauldron_brew_{c}", 3), (p[0], 0.98, p[2] + 0.01), (24, 36)))
    hero = H.SP.frame(H.PAL, "wildcaller", "left", "idle", 0).image()
    items.append((hero, (1.0, 0, 0.9), (10, 31)))
    for fr, a, pv in sorted(items, key=lambda r: r[1][2]):
        H.billboard_over(can, fr, a, org, zb, pv)
    return can


def strip_of(png, meta, name, cell=48):
    e = meta["effects"][name]
    s = Image.new("RGBA", (cell * e["frames"], cell), (12, 14, 26, 255))
    for i in range(e["frames"]):
        s.alpha_composite(H.fx_frame(png, meta, name, i), (i * cell, 0))
    return s


def contact(built, fxm, sc):
    S = H.Sheet("Alchemy - bubbling glowing cauldrons, alchemist props, potion + ingredient icons",
                "kit .glb at sprite density + animated brew billboards (48 px) + 16 px icons (biome palette, 6x)")
    S.section("Alchemist's corner at night (4x)", "three cauldrons (green / violet / blue brews) with brew + fire billboards and pools; table, shelf, herb rack; hero for scale")
    S.cell(sc.crop(sc.getbbox()), "renders/scene_alchemy_night.png", "", k=4 if sc.width * 4 <= 1360 else 3)
    S.section("Animated brews (48 px, 3x, every frame)", "bubbles swell + pop, swirl of light, vapour + motes rising; pivot = brew surface centre")
    png = OUT / "gamefx/alchemy_fx.png"
    for c in KA.BREW:
        S.cell(strip_of(png, fxm, f"cauldron_brew_{c}").crop((0, 0, 48 * 8, 48)), f"cauldron_brew_{c}", "8f 8fps", k=3 if 48 * 8 * 3 <= 1360 else 2)
    S.section("Icons (16 px, 6x): potions | ingredients", "biome palette only like build.py draw_icons; moonpetal matches the game's item icon")
    S.cell(Image.open(OUT / "icons/alchemy_icons.png"), "alchemy_icons.png",
           "health, mana, stamina, night sight, antidote, cold-fire phial, empty | moonpetal, red toadstool, herb bundle, mint, sage", k=6)
    S.section("Kit pieces (night, 4x)", "glow material = brews, potions, burner + log fire")
    for n, pc in built.items():
        lc = pc.markers.get("lamp_color")
        im, org = H.render_mesh(pc.mesh, "night", [((0, 1.2, 0.6), lc, 4, 1.0)] if lc else [], pad=8)
        S.cell(im, n, f"{pc.size[0]:.2f} x {pc.size[1]:.2f} x {pc.size[2]:.2f} m", k=4)
    S.section("Other gamefx (48 px, 2x)", "")
    for n, e in fxm["effects"].items():
        if n.startswith("cauldron_brew_"):
            continue
        S.cell(strip_of(png, fxm, n), n, f"{e['kind']} {e['frames']}f {e['fps']}fps" + ("" if e["loop"] else " once"), k=2)
    S.render(OUT / "contact_sheet.png")


README = """# Alchemy pack: bubbling glowing cauldrons, alchemist props, potion + ingredient icons

Art seat staging pack for **Hearthmoor**. Generated by `src/gen_alchemy.py` (Python + Pillow + numpy, importing the
repo's tools read-only). Gloom and glow: dark iron pots and timber, lit only by neon brews and little fires.

![contact sheet](contact_sheet.png)

## Kit (`kit/*.glb`, `kit/kit.json`, `src/kit_alchemy.py`)
| piece | size (m) | glow / light |
|---|---|---|
| `cauldron_blue` / `cauldron_violet` / `cauldron_green` | 1.0 x 1.1 x 1.0 | brew surface (neon) + log fire; lamp in the brew colour, fixed 0.55 / 4.5 m; brew surface at [0, 0.98, 0] |
| `alchemy_table` | 1.5 x 1.15 x 0.75 | glowing flasks, green alembic, spirit-burner flame; lamp green 0.3 / 3 m |
| `potion_shelf` | 1.35 x 1.9 x 0.32 | two rows of glowing bottles (red / blue / gold / violet / green / pink); lamp violet 0.25 / 2.5 m |
| `herb_rack` | 1.5 x 1.9 x 0.2 | - (drying herb bundles + moonpetals) |

## gamefx (`gamefx/alchemy_fx.png/.json`, 48 px)
- `cauldron_brew_blue/violet/green` (8f, 8 fps, pivot [24,36] = surface centre, lift 0.98): **the animated bubbling
  brew**: swirling neon surface sized to the pot mouth at the locked camera (26 x 9 px), bubbles swelling and popping,
  vapour and motes rising. Light 0.9 / 4.5 m in the brew colour.
- `cauldron_fire` (under any pot), `cauldron_pool_<c>` (decals), `brew_puff_<c>` (once, crafting success).

## Icons (`icons/alchemy_icons.png/.json`, 16 px strip + 6x preview)
Potions: `potion_health` (Heartroot Tonic), `potion_mana` (Moonwell Draught), `potion_stamina` (Hearthfire Brew),
`potion_nightsight` (Owl-Eye Elixir), `potion_antidote` (Mossbalm), `potion_coldfire` (Cold-Fire Phial), `bottle_empty`.
Ingredients: `ing_moonpetal` (same look as the game's moonpetal item), `ing_red_toadstool` (red, white spots, warm
gills), `ing_herb_bundle`, `ing_mint`, `ing_sage` (garden herbs). Names are suggestions in the JSON.

## Neon flag
- **No neon:** the icons (biome palette only, HUD rule; the "glow" is a white glint).
- **Neon:** all gamefx; kit `glow` material on brews, bottles, burner flame, coals.

## Drop-in steps
1. Kit: copy `src/kit_alchemy.py` to `tools/kit/` + the import line from its docstring.
2. gamefx: merge `alchemy_fx` into the area atlas (cell 48) or copy `src/alchemy_fx.py` into tools/portal.
3. Icons: append to the item sheet (same 16 px cell as `art/items.png`).
4. Regenerate: `python3 src/gen_alchemy.py`.
"""


if __name__ == "__main__":
    main()
