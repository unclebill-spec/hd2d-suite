"""Forge pack generator (Hearthmoor Art seat). Run:  python3 gen_forge.py   (writes ../, reads the repo read-only)"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "_lib"))
import hmart as H  # noqa: E402
import kit_forge as KF  # noqa: E402
import forge_fx as FF  # noqa: E402
from PIL import Image  # noqa: E402

OUT = HERE.parent


def hilde_extra(s, sp, L, face, bob, anim, i):
    """Hilde: a soot smudge on the cheek and rolled-up sleeves (bare forearms in skin)"""
    ht, top = L["head_top"] + bob, L["torso_top"] + bob
    if face == "down":
        s.set(12, ht + 6, "stone_lo")
    elif face == "left":
        s.set(8, ht + 6, "stone_lo")


def orri_extra(s, sp, L, face, bob, anim, i):
    """Orri: a braided beard tip with a copper bead"""
    ht = L["head_top"] + bob
    if face == "down":
        s.set(10, ht + 11, "roof_hi"); s.set(9, ht + 11, "flower_gold")
    # his rune-chisel, held point-down (his crossed-cog tongs are the ones stolen for the temple frame-up, so not drawn)
    top = L["torso_top"] + bob
    hy = top + 1 + L["arm_len"]
    x0 = 10 - L["torso_w"] // 2
    x1 = x0 + L["torso_w"] - 1
    if face == "down":
        hx = x0 - 2
    elif face == "left":
        hx = 9 - 2 * ([1, 0, -1, 0][i] if anim == "walk" else 0)   # follows the repo's WALK_SIDE stride
    else:
        hx = x1 + 2
    s.set(hx, hy - 1, "timber_hi"); s.set(hx, hy, "timber")         # wooden grip
    s.set(hx, hy + 1, "stone_hi"); s.set(hx, hy + 2, "sky")          # steel shank with a cold-blue rune
    s.set(hx, hy + 3, "white")                                      # bright chisel edge


NPCS = {
    "smith": {
        "spec": H.human(dict(desc="", hair="roof_lo", hairstyle="bun", shirt="plaster", scarf="roof", apron="timber_lo",
                             belt="shadow", pants="stone_lo", shoes="shadow", boots=True, item="hammer"), hilde_extra),
        "anims": ("idle", "walk"), "kind": "human", "named": True,
        "desc": "Hilde Anvilsong, master smith of the Ravenhold Forge Quarter: auburn bun, red neckerchief, cream work shirt "
                "with a brown leather apron, dark belt at the waist, slate trousers, black boots, smith's hammer",
        "light": None,
    },
    "dwarfsmith": {
        "spec": H.human(dict(desc="", layout="broad", hair="roof", hairstyle="short", beard="roof", shirt="cloth", vest="timber",
                             belt="shadow", pants="timber_lo", shoes="shadow", boots=True, item=None), orri_extra),
        "anims": ("idle", "walk"), "kind": "human", "named": True,
        "desc": "Orri Flintcog, dwarf smith (bonus): ginger hair and braided beard with a copper bead, blue shirt under a brown "
                "vest, dark belt, brown trousers, black boots, a rune-chisel in his hand (steel shank, cold-blue rune, "
                "bright edge; his crossed-cog tongs are the stolen ones, so he doesn't carry them)",
    },
}

KIT_META = {
    "forge_anvil": {"fx": ["anvil_glow", "forge_sparks"], "npc": "smith stands at local [0.75, 0, 0.1] facing left"},
    "forge_hearth": {"fx": ["forge_fire", "forge_fire_top", "embers_drift", "forge_pool_red"], "mouth": [0, 0.27, 0.72], "chimney_top": [0, 3.66, -0.1]},
    "quench_tank": {"fx": ["quench_steam", "quench_pool_blue"], "note": "Ravenhold's blue cold-fire quench"},
    "coal_bin": {"fx": ["embers_drift"]},
}


def main():
    rep = H.write_actors(OUT / "sprite", "forge_actors", NPCS)
    print("actors", H.report_line(rep))
    fxm = H.write_fx(OUT / "gamefx", "forge_fx", FF.FX, 48)
    built, km = H.build_kit(OUT / "kit", KF.pieces, KIT_META)
    rd = OUT / "renders"; rd.mkdir(exist_ok=True)
    for n, pc in built.items():
        lc = pc.markers.get("lamp_color")
        im, _ = H.render_mesh(pc.mesh, "night", [((0, 1.0, 0.8), lc, 5, 1.0)] if lc else [], pad=6)
        im.save(rd / f"{n}_night.png")
    sc = scene(built, fxm)
    sc.save(rd / "scene_forge_night.png")
    contact(built, fxm, sc, H.report_line(rep))
    H.finish_pack(OUT, README)
    (OUT / "READY.txt").write_text("forge: READY (2026-10-05, Hearthmoor Art seat)\nSee README.md + contact_sheet.png. NPC atlas passes check-sprite; 7 kit pieces; gamefx forge_fx (48 px).\n")


def scene(built, fxm):
    K = H.kit_module(); cx = H.kit_ctx()
    M = K.Mesh(); lights = []
    st = K.mix(cx.c("stone_lo"), cx.c("shadow"), 0.4)
    R = H.rng(104, "fscene")
    for i in range(14):                                     # cobbled yard as small quads (light falls off)
        for j in range(10):
            x0, z0 = -3.5 + i * 0.5, -2.5 + j * 0.5
            c = K.mix(st, "#000000", R.uniform(0, 0.08))
            M.quad((x0, 0, z0 + 0.5), (x0 + 0.5, 0, z0 + 0.5), (x0 + 0.5, 0, z0), (x0, 0, z0), c, mat="stone")
    def put(n, pos):
        pc = built[n]; M.add(pc.mesh.xf(pos))
        for lp in pc.markers.get("lamps", []):
            lights.append(((pos[0] + lp[0], lp[1], pos[2] + lp[2]), pc.markers["lamp_color"], pc.markers["lamp_range"], 1.0))
    put("forge_hearth", (-1.2, 0, -1.6)); put("forge_anvil", (-0.6, 0, 0.4)); put("quench_tank", (1.8, 0, -1.0))
    put("tool_rack", (0.8, 0, -2.3)); put("coal_bin", (-3.0, 0, -0.4)); put("grindstone", (2.6, 0, 0.9)); put("forge_sign", (3.0, 0, -2.2))
    im, org, zb = H.render_mesh(M, "night", lights, pad=12, depth=True)
    can = Image.new("RGBA", im.size, (10, 10, 22, 255))
    can.alpha_composite(im)
    png = OUT / "gamefx/forge_fx.png"
    def dec(n, c, i=0):
        fr = H.fx_frame(png, fxm, n, i)
        p = H.project((c[0], 0.0, c[2]), org)
        src, dst = fr.load(), can.load()
        for y in range(48):
            for x in range(48):
                if src[x, y][3]:
                    X, Y = int(p[0] - 24 + x), int(p[1] - 24 + y)
                    if 0 <= X < can.width and 0 <= Y < can.height and zb[Y, X] < (c[2] + (y - 24) / (math.sin(H.ELEV) * 18)) * math.cos(H.ELEV) + 0.1:
                        dst[X, Y] = src[x, y]
    dec("forge_pool_red", (-1.2, 0, -0.5), 1); dec("quench_pool_blue", (1.8, 0, -0.5), 2); dec("forge_pool_red", (-0.6, 0, 0.8), 3)
    meta = json.loads((OUT / "sprite/forge_actors.json").read_text())
    smith = H.frame_of(OUT / "sprite/forge_actors.png", meta, "smith", "left", "idle", 0)
    dwarf = H.frame_of(OUT / "sprite/forge_actors.png", meta, "dwarfsmith", "down", "idle", 1)
    for (fr, a, pv) in sorted([
            (H.fx_frame(png, fxm, "forge_fire", 2), (-1.2, 0.27, -0.88), (24, 47)),
            (H.fx_frame(png, fxm, "forge_fire_top", 5), (-1.2, 1.05, -1.55), (24, 47)),
            (H.fx_frame(png, fxm, "embers_drift", 1), (-1.2, 1.4, -1.5), (24, 47)),
            (H.fx_frame(png, fxm, "forge_sparks", 2), (-0.6, 0.92, 0.42), (24, 40)),
            (H.fx_frame(png, fxm, "quench_steam", 3), (1.8, 0.65, -0.95), (24, 47)),
            (smith, (0.2, 0, 0.5), (10, 31)), (dwarf, (2.1, 0, 0.1), (10, 31))], key=lambda r: r[1][2]):
        H.billboard_over(can, fr, a, org, zb, pv)
    return can


def strip_of(png, meta, name, cell=48):
    e = meta["effects"][name]
    s = Image.new("RGBA", (cell * e["frames"], cell), (12, 14, 26, 255))
    for i in range(e["frames"]):
        s.alpha_composite(H.fx_frame(png, meta, name, i), (i * cell, 0))
    return s


def contact(built, fxm, sc, rep):
    S = H.Sheet("Ravenhold Forge Quarter - anvil, forge, cold-fire quench, Hilde Anvilsong",
                "kit .glb at sprite density + gamefx (48 px) + 20x32 NPCs; red forge fire vs blue cold-fire quench (E6.2)")
    S.section("Forge yard at night (4x)", "forge_hearth + fire fx, anvil + sparks, quench tank + steam, rack, coal bin, grindstone, sign; Hilde + Orri")
    S.cell(sc.crop(sc.getbbox()), "renders/scene_forge_night.png", "", k=4 if sc.width * 4 <= 1360 else 3)
    S.section("NPCs (20x32, 4x): idle 0-3 | walk 0-3, 4 facings", "clothing rule: separate top / bottom, dark waist band, contrasting boots; " + rep)
    meta = json.loads((OUT / "sprite/forge_actors.json").read_text())
    png = OUT / "sprite/forge_actors.png"
    for role in NPCS:
        row = Image.new("RGBA", ((H.FW + 6) * 8 + 10, (H.FH + 6) * 4 + 8), (0, 0, 0, 0))
        for fi, facing in enumerate(H.FACINGS):
            for c, (an, i) in enumerate([("idle", k) for k in range(4)] + [("walk", k) for k in range(4)]):
                fr = H.frame_of(png, meta, role, facing, an, i)
                row.alpha_composite(H.lit_sprite(fr, ("neon_red_hi", "neon_red", "neon_red_lo") if role == "smith" else None, 12, pad=(3, 3)), (c * (H.FW + 6), fi * (H.FH + 6)))
        S.cell(row, role, NPCS[role]["desc"][:110], k=4 if row.width * 4 <= 1360 else 3)
    S.section("Kit pieces (night, 3x)", "glow material = forge fire, hot metal, embers, cold-fire water")
    for n, pc in built.items():
        lc = pc.markers.get("lamp_color")
        im, org = H.render_mesh(pc.mesh, "night", [((0, 1.0, 0.8), lc, 5, 1.0)] if lc else [], pad=10)
        S.cell(im, n, f"{pc.size[0]:.2f} x {pc.size[1]:.2f} x {pc.size[2]:.2f} m", k=3)
    S.section("gamefx (48 px, 2x, every frame)", "")
    fpng = OUT / "gamefx/forge_fx.png"
    for n, e in fxm["effects"].items():
        S.cell(strip_of(fpng, fxm, n), n, f"{e['kind']} {e['frames']}f {e['fps']}fps" + ("" if e["loop"] else " once"), k=2)
    S.render(OUT / "contact_sheet.png")


README = """# Forge pack: Ravenhold Forge Quarter (anvil, forge, quench, master smith)

Art seat staging pack for **Hearthmoor**. Generated by `src/gen_forge.py` (Python + Pillow + numpy, importing the repo's
tools read-only). Follows DESIGN_EXPANSION E6.2: **red forge mouths** and **blue cold-fire quench tanks** (gloom and
glow: red neon vs neon-blue cold fire in one dark yard), master smith **Hilde Anvilsong**.

![contact sheet](contact_sheet.png)

## NPCs (`sprite/forge_actors.png/.json`, check-sprite PASS)
`hd2d sprite` atlas: 20x32, pivot [10,32], rows down / up / left / right, idle 0-3 (3 fps, loop 0,1,2,1) and walk 4-7
(8 fps), `named` roles.
- `smith`: **Hilde Anvilsong**, master smith. Auburn bun, red neckerchief, cream work shirt under a brown leather apron,
  **dark belt at the waist**, slate trousers, black boots (contrasting), smith's hammer, a soot smudge. Normal work
  clothes: separate top and bottom, visible waist.
- `dwarfsmith` (bonus): **Orri Flintcog**, dwarf smith (rune-chisel in hand, added 2026-10-06; not tongs, since his crossed-cog tongs are the stolen frame-up tongs in forge_alchemy.md 5.4): ginger hair + braided beard with a copper bead, blue shirt,
  brown vest, dark belt, brown trousers, black boots, hands free. (Uses the `broad` layout; the game has no short-adult
  layout yet.)

## Kit (`kit/*.glb`, `kit/kit.json`, `src/kit_forge.py`)
| piece | size (m) | glow / light |
|---|---|---|
| `forge_anvil` | 0.90 x 0.95 x 0.75 | red-hot bar on the face; lamp `#ff5a4a` 0.25 / 2 m |
| `forge_hearth` | 3.2 x 3.7 x 1.4 | red mouth with coals + top fire bed; lamp `#ff5a4a` fixed 0.6 / 6 m; mouth at [0, 0.27, 0.72], chimney top [0, 3.66, -0.1] |
| `quench_tank` | 1.45 x 0.70 x 0.76 | neon-blue cold-fire water; lamp `#5ab4f0` 0.45 / 4 m |
| `tool_rack` | 1.3 x 1.7 x 0.2 | - |
| `grindstone` | 0.75 x 1.1 x 0.6 | - |
| `coal_bin` | 0.84 x 0.66 x 0.59 | three live embers; lamp `#e0302a` 0.1 / 1.2 m |
| `forge_sign` | 1.0 x 2.6 x 0.2 | anvil emblem with a glowing hot bar |

## gamefx (`gamefx/forge_fx.png/.json`, 48 px)
`forge_fire` (mouth, light red 1.4 / 6 m), `forge_fire_top`, `forge_sparks` (once, anvil strike; fire every ~1.2 s while
Hilde works), `quench_steam` (once, white steam + cold-fire sparks), `embers_drift`, `anvil_glow`, `forge_pool_red` and
`quench_pool_blue` (decals). Placement per piece is in `kit.json` (`fx`, `mouth`, `chimney_top`, NPC spot).

## Neon flag
- **No neon:** the NPC sprites (biome palette only).
- **Neon:** all gamefx; kit `glow` material on the forge fire / coals, hot bar, embers, sign bar, cold-fire water.

## Drop-in steps
1. NPCs: copy the specs in `NPCS` (`src/gen_forge.py`) into `tools/sprite/roles_more.py` (existing spec keys + tiny
   `*_extra` hooks) or paste the atlas rows.
2. Kit: copy `src/kit_forge.py` to `tools/kit/` + the import line from its docstring.
3. gamefx: merge `forge_fx` into the Ravenhold gamefx atlas or copy the functions into tools/portal.
4. Regenerate: `python3 src/gen_forge.py`.
"""


if __name__ == "__main__":
    main()
