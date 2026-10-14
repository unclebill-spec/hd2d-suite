"""Alfheim pack generator (Hearthmoor Art seat). Run:  python3 gen_alfheim.py   (writes ../, reads the repo read-only)
Lumenvale (elf city of light magic, violet neon) + The Prism Vault (prism shards, mirror duelists, Lady Sylvaine)."""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "_lib"))
import hmart as H  # noqa: E402
import al_actors as A  # noqa: E402
import al_boss as B  # noqa: E402
import al_fx as AF  # noqa: E402
import kit_alfheim as KA  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

OUT = HERE.parent
A4 = ("idle", "walk", "attack", "die")

NPCS = {
    "elf_lampwright": {
        "spec": H.human(dict(hair="stone_hi", hairstyle="long", shirt="plaster_hi", vest="sky", belt="shadow", skirt="cloth", pants="cloth",
                             shoes="timber_lo", boots=True), A.elf_extra(lantern=True, crown=("flower_gold", "sky"))),
        "anims": ("idle", "walk"), "kind": "human", "named": True,
        "desc": "Elowen Brightwick, Lumenvale's wisp-lantern keeper: long silver hair, gold circlet with a sky gem, long pointed "
                "ears, white blouse under a sky-blue vest, dark belt, deep-blue skirt, brown boots, a brass wisp lantern on a pole",
        "light": {"color": H.ALLC["neon_blue_hi"], "intensity": 0.5, "range": 1.6, "fx": "lantern_glow"},
    },
    "elf_scholar": {
        "spec": H.human(dict(hair="plaster_hi", hairstyle="short", shirt="flower_blue", vest="cloth", belt="shadow", pants="plaster_lo",
                             shoes="shadow", boots=True, glasses=True, item="ledger"), A.elf_extra()),
        "anims": ("idle", "walk"), "kind": "human", "named": True,
        "desc": "Thalion Prismwright, prism scholar: platinum hair, long ears, round glasses, periwinkle shirt under a deep-blue "
                "vest, dark belt, pale trousers, black boots, a ledger of light-runes",
    },
    "elf_gardener": {
        "spec": H.human(dict(hair="flower_gold", hairstyle="bun", shirt="flower_rose", belt="shadow", skirt="moss", pants="moss",
                             shoes="timber", item="basket"), A.elf_extra()),
        "anims": ("idle", "walk"), "kind": "human", "named": True,
        "desc": "Faelin Dewpetal, treetop gardener: golden bun, long ears, rose blouse, dark belt, moss-green skirt, brown shoes, "
                "a basket of moonpetals",
    },
    "elf_child": {
        "spec": H.human(dict(layout="kid", hair="plaster_hi", hairstyle="cowlick", shirt="sky", belt="shadow", pants="cloth", shoes="roof"),
                        A.elf_extra()),
        "anims": ("idle", "walk"), "kind": "human", "named": True,
        "desc": "Pip Starling, elf child (wisp-catcher): white cowlick, long ears, sky-blue shirt, dark belt, deep-blue shorts, red shoes",
    },
}

ENEMIES = {
    "prismshard": {"draw": A.prismshard, "kind": "enemy", "enemy": True, "named": True, "anims": A4,
                   "desc": "Prism shard (Prism Vault common): a floating diamond crystal with slit eyes and two orbiting splinters, a "
                           "sparkle trail to the ground; attack = rears back and flings its splinters (frame 14); die = cracks, "
                           "splits and falls into a pile of glinting shards",
                   "light": {"color": H.ALLC["neon_blue_hi"], "intensity": 0.5, "range": 1.8, "pool": "pool_blue_small"},
                   "stats_hint": {"tier": "common", "hp": "low", "speed": "fast (hover)", "attack": "splinter volley (frame 14)",
                                  "fx": {"hit": "prism_shatter", "die": "prism_shatter on frame 25"}}},
    "mirrorduelist": {"draw": A.mirrorduelist, "kind": "enemy", "enemy": True, "named": True, "anims": A4,
                      "desc": "Mirror Duelist (Prism Vault elite): oval hand-mirror face under a plumed hat, deep-blue frock coat, "
                              "white cravat, dark belt with a gold buckle, pale trousers, black boots, white gloves, silver rapier; "
                              "attack = en garde, lunge, thrust (hit 14); die = mirror cracks, kneels, collapses into coat + shards",
                      "light": None,
                      "stats_hint": {"tier": "elite", "hp": "medium", "speed": "fast", "attack": "lunge thrust (frame 14) + mirror_flash",
                                     "fx": {"hit": "mirror_flash at the rapier tip", "die": "prism_shatter on frame 26"}}},
}

BOSS = {"sylvaine": {
    "draw": B.sylvaine, "frame": (B.W_, B.H_), "scale": 5.5, "anims": A4,
    "desc": "Lady Sylvaine, elf vampire queen of the Prism Vault (drains magic, neon violet): long silver hair, long elf ears, "
            "crystal tiara, rose eyes; a fitted deep-blue long-sleeved blouse with white lace jabot and cuffs, a dark belt with a "
            "gold clasp, a long mauve-dark bell skirt with a rose front panel and pale hem, pale slippers, a high-collared "
            "dark-red cape. Die: kneels, bows, and only the pooled gown, cape and tiara remain (she becomes violet moths).",
    "light": {"color": H.ALLC["neon_violet"], "intensity": 0.9, "range": 6.0, "pool": "sylvaine_aura"},
    "notes": "always spawn sylvaine_aura under her; attack frame 14 = drain (drain_stream from target to hand + drain_hit on "
             "the target); die frames 26-27 -> violet_moths x3",
    "stats_hint": {"tier": "boss", "height_x_player": 5.5, "dungeon": "The Prism Vault", "element": "energy / light"}}}

KIT_META = {
    "lumen_tree": {"fx": ["pool_violet", "light_motes", "glow_orb_violet", "glow_orb_pink"], "placement": "plaza corners, treetop walks; 4-6 m apart"},
    "lumen_tree_small": {"fx": ["pool_violet_small"], "placement": "street + garden filler"},
    "lumen_lamp": {"fx": ["pool_violet_small"], "placement": "every 5-6 m along streets and bridges"},
    "crystal_spire": {"fx": ["pool_violet", "prism_sparkle"], "placement": "plaza waymarker / Prism Vault entrance"},
    "prism_fountain": {"fx": ["pool_violet", "fountain_sparkle", "prism_sparkle"], "placement": "plaza centre"},
    "elf_archway": {"fx": ["pool_violet", "prism_sparkle"], "placement": "district gates, the Prism Vault door"},
    "wisp_lantern_post": {"fx": ["pool_blue_small", "wisp_blue"], "placement": "wisp-catching meadow edges"},
    "light_bridge": {"fx": ["glow_mist_violet"], "placement": "over glowing streams / between treetop platforms (deck ~0.6 m)"},
    "elf_rail": {"placement": "edges of terraces, bridges, treetop walks"},
    "lumen_pavilion": {"fx": ["pool_violet", "glow_orb_violet"], "placement": "gardens; the Wisp Night lantern fair"},
    "wisp_jar": {"fx": ["pool_blue_small"], "placeable": True, "placement": "shop counters, wisp-catching reward"},
    "vault_floor": {"placement": "Prism Vault floor grid (2 m)"},
    "vault_wall": {"fx": ["pool_violet_small"], "placement": "Prism Vault walls (2 m modules)"},
    "vault_pillar": {"fx": ["pool_violet_small", "prism_sparkle"], "placement": "Prism Vault halls, 4 m apart"},
    "sylvaine_throne": {"fx": ["glow_mist_violet", "pool_violet"], "placement": "Prism Vault boss room, back wall centre; boss stands at boss_stand"},
}


def decal_over(can, fr, center, org, zb, lift=0.02):
    """paste a pre-squashed decal frame centred on world `center` (ground plane y=lift), per-pixel depth tested"""
    ce, se = math.cos(H.ELEV), math.sin(H.ELEV)
    px_, py_ = H.project((center[0], lift, center[2]), org)
    src, dst = fr.load(), can.load()
    n = fr.width
    for y in range(n):
        for x in range(n):
            if src[x, y][3] == 0:
                continue
            cx_, cy_ = int(round(px_ - n / 2 + x)), int(round(py_ - n / 2 + y))
            if not (0 <= cx_ < can.width and 0 <= cy_ < can.height):
                continue
            dz = (y - n / 2) / (se * H.PX_PER_M)
            dep = (center[2] + dz) * ce + lift * se
            if 0 <= cy_ < zb.shape[0] and 0 <= cx_ < zb.shape[1] and zb[cy_, cx_] > dep + 0.08:
                continue
            dst[cx_, cy_] = src[x, y]


def main():
    rep_n = H.write_actors(OUT / "sprite", "alfheim_npcs", NPCS)
    rep_e = H.write_actors(OUT / "sprite", "prism_vault_enemies", ENEMIES)
    rep_b = H.write_boss(OUT / "sprite", "boss_sylvaine", BOSS)
    reps = {"alfheim_npcs": rep_n, "prism_vault_enemies": rep_e, "boss_sylvaine": rep_b}
    H.write_json(OUT / "check_sprite_report.json", reps)
    for k, r in reps.items():
        print(k, H.report_line(r))
    fxm = H.write_fx(OUT / "gamefx", "alfheim_fx", AF.FX, 48)
    built, km = H.build_kit(OUT / "kit", KA.pieces, KIT_META)
    rd = OUT / "renders"; rd.mkdir(exist_ok=True)
    for n, pc in built.items():
        lc = pc.markers.get("lamp_color")
        im, _ = H.render_mesh(pc.mesh, "night", lights_of(pc), pad=6)
        im.save(rd / f"{n}_night.png")
    sc = scene_city(built, fxm)
    sc.save(rd / "scene_lumenvale_night.png")
    sv = scene_vault(built, fxm)
    sv.save(rd / "scene_prism_vault_night.png")
    contact(built, fxm, sc, sv, reps)
    H.finish_pack(OUT, README)
    (OUT / "READY.txt").write_text(
        "alfheim: READY (2026-10-05, Hearthmoor Art seat)\nSee README.md + contact_sheet.png. 4 elf NPCs + 2 Prism Vault enemies "
        "(20x32) + Lady Sylvaine boss (128x176, 5.5x) all pass check-sprite; 15 kit pieces; gamefx alfheim_fx (48 px) incl. glow orbs "
        "in 5 neon colours with matching light pools.\n")


def lights_of(pc, pos=(0, 0, 0)):
    lc = pc.markers.get("lamp_color")
    return [((pos[0] + lp[0], lp[1], pos[2] + lp[2]), lc, pc.markers["lamp_range"], 1.0) for lp in pc.markers.get("lamps", [])] if lc else []


def fxf(fxm, n, i=0):
    return H.fx_frame(OUT / "gamefx/alfheim_fx.png", fxm, n, i)


ORBS_CITY = [("blue", (-4.4, 1.7, 3.4)), ("violet", (1.9, 2.1, -2.4)), ("red", (-1.0, 1.5, 3.4)), ("green", (5.4, 1.8, 1.6)),
             ("pink", (-5.8, 2.0, -1.2)), ("violet", (3.0, 1.4, 4.4)), ("blue", (-0.4, 2.4, -3.6))]


def scene_city(built, fxm):
    K = H.kit_module()
    M = K.Mesh(); lights = []
    R = H.rng(104, "lscene")
    pave = K.mix(K.mix("#f6ecd2", "#94c0dc", 0.25), "#2a2a40", 0.55)
    for i in range(30):                                     # moonstone paving as 0.5 m quads (light falls off)
        for j in range(24):
            x0, z0 = -7.5 + i * 0.5, -5.5 + j * 0.5
            c = K.mix(pave, "#000000", R.uniform(0, 0.1) + (0.06 if (i + j) % 2 else 0))
            M.quad((x0, 0, z0 + 0.5), (x0 + 0.5, 0, z0 + 0.5), (x0 + 0.5, 0, z0), (x0, 0, z0), c, mat="stone")
    def put(n, pos):
        pc = built[n]; M.add(pc.mesh.xf(pos)); lights.extend(lights_of(pc, pos))
    put("lumen_tree", (-5.4, 0, -4.0)); put("lumen_pavilion", (-1.6, 0, -4.0)); put("elf_archway", (2.9, 0, -4.8))
    put("lumen_tree_small", (5.9, 0, -3.8)); put("prism_fountain", (0.6, 0, -0.6)); put("crystal_spire", (-5.2, 0, 1.0))
    put("wisp_lantern_post", (4.6, 0, 0.2)); put("lumen_lamp", (-2.8, 0, 3.0)); put("lumen_lamp", (3.6, 0, 3.4))
    put("elf_rail", (-5.6, 0, 5.4)); put("elf_rail", (-3.6, 0, 5.4)); put("elf_rail", (4.0, 0, 5.4)); put("elf_rail", (6.0, 0, 5.4))
    put("lumen_tree_small", (6.4, 0, 3.6)); put("wisp_jar", (1.6, 0, 2.6))
    for c, p in ORBS_CITY:
        lights.append(((p[0], p[1], p[2]), H.ALLC[f"neon_{c}"], 2.6, 0.7))
    im, org, zb = H.render_mesh(M, "night", lights, pad=12, depth=True)
    can = Image.new("RGBA", im.size, (10, 10, 22, 255))
    can.alpha_composite(im)
    for (n, c, i) in (("glow_mist_violet", (-4.6, 0, 2.8), 0), ("glow_mist_violet", (5.2, 0, -1.6), 3), ("glow_mist_violet", (-0.5, 0, 4.6), 5),
                      ("pool_violet", (0.6, 0, -0.6), 0), ("pool_violet", (-5.2, 0, 1.0), 2), ("pool_violet", (-5.4, 0, -3.4), 4),
                      ("pool_violet", (-1.6, 0, -3.8), 1), ("pool_violet", (2.9, 0, -4.4), 3), ("pool_violet_small", (-2.4, 0, 3.0), 1),
                      ("pool_violet_small", (4.0, 0, 3.4), 2), ("pool_blue_small", (5.1, 0, 0.3), 1), ("pool_blue_small", (1.6, 0, 2.7), 4),
                      ("pool_violet_small", (5.9, 0, -3.6), 2), ("pool_violet_small", (6.4, 0, 3.8), 5)):
        decal_over(can, fxf(fxm, n, i), c, org, zb)
    for k, (c, p) in enumerate(ORBS_CITY):
        decal_over(can, fxf(fxm, f"glow_orb_pool_{c}", k % 6), (p[0], 0, p[2]), org, zb)
    nm = json.loads((OUT / "sprite/alfheim_npcs.json").read_text()); npng = OUT / "sprite/alfheim_npcs.png"
    hero = H.SP.frame(H.PAL, "wildcaller", "up", "idle", 0).image()
    items = [(H.frame_of(npng, nm, "elf_lampwright", "down", "idle", 0), (2.2, 0, 1.6), (10, 31)),
             (fxf(fxm, "lantern_glow", 1), (2.2 - 7 / 18, 21 / 18 / math.cos(H.ELEV), 1.6), (24, 24)),
             (H.frame_of(npng, nm, "elf_scholar", "left", "idle", 1), (-1.6, 0, 1.2), (10, 31)),
             (H.frame_of(npng, nm, "elf_gardener", "down", "walk", 1), (-3.4, 0, -1.6), (10, 31)),
             (H.frame_of(npng, nm, "elf_child", "left", "idle", 0), (3.6, 0, 1.0), (10, 31)),
             (hero, (0.8, 0, 3.8), (10, 31)),
             (fxf(fxm, "fountain_sparkle", 2), (0.6, 0.45, -0.55), (24, 47)), (fxf(fxm, "prism_sparkle", 1), (-5.2, 1.4, 1.1), (24, 40)),
             (fxf(fxm, "prism_sparkle", 5), (2.9, 3.0, -4.6), (24, 40)), (fxf(fxm, "light_motes", 3), (-5.4, 1.6, -3.4), (24, 47)),
             (fxf(fxm, "light_motes", 6), (0.2, 0.3, 2.0), (24, 47)),
             (fxf(fxm, "wisp_violet", 1), (-2.2, 1.3, -1.4), (24, 30)), (fxf(fxm, "wisp_blue", 4), (4.2, 1.1, 2.4), (24, 30)),
             (fxf(fxm, "wisp_pink", 6), (-4.0, 1.0, 4.0), (24, 30))]
    for k, (c, p) in enumerate(ORBS_CITY):
        items.append((fxf(fxm, f"glow_orb_{c}", k % 8), p, (24, 33)))
    for (fr, a, pv) in sorted(items, key=lambda r: r[1][2]):
        H.billboard_over(can, fr, a, org, zb, pv)
    return can


def scene_vault(built, fxm):
    K = H.kit_module()
    M = K.Mesh(); lights = []
    def put(n, pos):
        pc = built[n]; M.add(pc.mesh.xf(pos)); lights.extend(lights_of(pc, pos))
    for i in range(8):
        for j in range(5):
            put("vault_floor", (-7 + i * 2, 0, -3 + j * 2))
    for i in range(8):
        put("vault_wall", (-7 + i * 2, 0, -4.3))
    put("sylvaine_throne", (3.6, 0, -2.6))
    put("crystal_spire", (1.0, 0, -3.3)); put("crystal_spire", (6.4, 0, -3.3))
    for p in ((-6.0, 0, -1.6), (-6.0, 0, 3.4), (6.6, 0, 1.0), (6.6, 0, 4.4)):
        put("vault_pillar", p)
    # an unlit speck high above the back wall so the render leaves headroom for the 5.5x boss
    M.quad((-0.02, 9.5, -4.6), (0.02, 9.5, -4.6), (0.02, 9.55, -4.6), (-0.02, 9.55, -4.6), "#0a0a16", mat="glow")
    orbs = [("violet", (-4.4, 2.6, -1.8)), ("violet", (1.8, 2.4, -1.2)), ("pink", (-5.0, 1.6, 2.2)), ("blue", (3.8, 1.6, 3.6)), ("red", (5.2, 2.8, -0.8))]
    for c, p in orbs:
        lights.append((p, H.ALLC[f"neon_{c}"], 2.6, 0.7))
    boss = (-1.8, 0, 0.4)
    lights.append(((boss[0], 1.2, boss[2] + 0.6), H.ALLC["neon_violet"], 6.0, 0.9))
    im, org, zb = H.render_mesh(M, "night", lights, pad=12, depth=True)
    can = Image.new("RGBA", im.size, (10, 10, 22, 255))
    can.alpha_composite(im)
    for (n, c, i) in (("glow_mist_violet", (-3.6, 0, -1.4), 2), ("glow_mist_violet", (3.0, 0, -1.0), 6), ("glow_mist_violet", (-5.0, 0, 4.2), 4),
                      ("pool_violet", (3.6, 0, -1.0), 0), ("pool_violet", (1.0, 0, -2.6), 3), ("pool_violet", (6.4, 0, -2.6), 5)):
        decal_over(can, fxf(fxm, n, i), c, org, zb)
    for p in ((-6.0, 0, -1.6), (-6.0, 0, 3.4), (6.6, 0, 1.0), (6.6, 0, 4.4)):
        decal_over(can, fxf(fxm, "pool_violet_small", 1), (p[0], 0, p[2] + 0.4), org, zb)
    aura = fxf(fxm, "sylvaine_aura", 2)
    aura = aura.resize((aura.width * 3, aura.height * 3), Image.NEAREST)   # engine: decal scaled x3 under the boss
    decal_over(can, aura, boss, org, zb, 0.03)
    for k, (c, p) in enumerate(orbs):
        decal_over(can, fxf(fxm, f"glow_orb_pool_{c}", k), (p[0], 0, p[2]), org, zb)
    bm = json.loads((OUT / "sprite/boss_sylvaine.json").read_text())
    syl = H.frame_of(OUT / "sprite/boss_sylvaine.png", bm, "sylvaine", "down", "attack", 2)
    em = json.loads((OUT / "sprite/prism_vault_enemies.json").read_text()); epng = OUT / "sprite/prism_vault_enemies.png"
    hero_pos = (1.4, 0, 4.4)
    hero = H.SP.frame(H.PAL, "wildcaller", "up", "idle", 0).image()
    items = [(syl, boss, (64, 175)), (hero, hero_pos, (10, 31)),
             (H.frame_of(epng, em, "mirrorduelist", "left", "attack", 1), (3.4, 0, 2.6), (10, 31)),
             (H.frame_of(epng, em, "prismshard", "down", "idle", 1), (4.8, 0, 1.6), (10, 31)),
             (H.frame_of(epng, em, "prismshard", "left", "idle", 2), (5.4, 0, 3.0), (10, 31)),
             (fxf(fxm, "drain_hit", 3), hero_pos, (24, 40)), (fxf(fxm, "prism_sparkle", 3), (1.0, 1.4, -3.2), (24, 40)),
             (fxf(fxm, "prism_sparkle", 6), (6.4, 1.4, -3.2), (24, 40)), (fxf(fxm, "light_motes", 2), (-4.0, 0.2, 1.0), (24, 47))]
    for k, (c, p) in enumerate(orbs):
        items.append((fxf(fxm, f"glow_orb_{c}", k), p, (24, 33)))
    for (fr, a, pv) in sorted(items, key=lambda r: r[1][2]):
        H.billboard_over(can, fr, a, org, zb, pv)
    # the drain: tile drain_stream from the hero's chest to her raised right hand (sprite px +34, -141 from her pivot)
    bx, by = H.project(boss, org)
    hx_, hy_ = bx + 34, by - 141
    tx, ty = H.project((hero_pos[0], 0, hero_pos[2]), org)
    ty -= 18
    L = math.hypot(tx - hx_, ty - hy_); ux, uy = (tx - hx_) / L, (ty - hy_) / L
    seg = fxf(fxm, "drain_stream", 2).rotate(-math.degrees(math.atan2(uy, ux)), expand=True, resample=Image.NEAREST)
    n = max(1, int(L // 44))
    for k in range(n):
        cxp, cyp = hx_ + ux * (k + 0.5) * L / n, hy_ + uy * (k + 0.5) * L / n
        can.alpha_composite(seg, (int(cxp - seg.width / 2), int(cyp - seg.height / 2)))
    return can


def strip_of(png, meta, name, cell=48):
    e = meta["effects"][name]
    s = Image.new("RGBA", (cell * e["frames"], cell), (12, 14, 26, 255))
    for i in range(e["frames"]):
        s.alpha_composite(H.fx_frame(png, meta, name, i), (i * cell, 0))
    return s


PAL_ROWS = [("moonstone (kit)", "plaster_hi + 22% sky", "#e0e2d8"), ("vault stone (kit)", "ink + 38% cloth", None)]


def palette_card():
    """a swatch table: biome colours the pack's sprites use + the NEON glow hexes"""
    used = ["ink", "shadow", "plaster_hi", "plaster", "plaster_lo", "stone_hi", "stone", "stone_lo", "white", "sky", "flower_blue",
            "cloth", "flower_rose", "roof_hi", "roof", "roof_lo", "flower_gold", "skin", "skin_lo", "timber", "timber_lo", "moss"]
    neon = [k for k in H.NEON]
    W = 700
    rows = (len(used) + 3) // 4 + (len(neon) + 3) // 4 + 2
    im = Image.new("RGBA", (W, rows * 20 + 30), (18, 20, 34, 255))
    d = ImageDraw.Draw(im)
    y = 4
    d.text((6, y), "biome cozy-village (sprites + kit)", fill=(255, 210, 120, 255), font=H.FONT_S); y += 18
    for k, n in enumerate(used):
        x = 6 + (k % 4) * 172
        if k and k % 4 == 0:
            y += 20
        d.rectangle([x, y, x + 16, y + 14], fill=H.ALLC[n], outline=(0, 0, 0))
        d.text((x + 22, y + 1), f"{n} {H.ALLC[n]}", fill=(230, 230, 240, 255), font=H.FONT_S)
    y += 28
    d.text((6, y), "NEON glow (gamefx + kit 'glow' material only - never on the elf / enemy / boss sprites)", fill=(255, 210, 120, 255), font=H.FONT_S); y += 18
    for k, n in enumerate(neon):
        x = 6 + (k % 4) * 172
        if k and k % 4 == 0:
            y += 20
        d.rectangle([x, y, x + 16, y + 14], fill=H.ALLC[n], outline=(0, 0, 0))
        d.text((x + 22, y + 1), f"{n} {H.ALLC[n]}", fill=(230, 230, 240, 255), font=H.FONT_S)
    return im.crop((0, 0, W, y + 22))


def contact(built, fxm, sc, sv, reps):
    S = H.Sheet("Alfheim - Lumenvale (elf city of light, violet neon) + The Prism Vault (Lady Sylvaine)",
                "kit .glb at sprite density + gamefx (48 px) + 20x32 elves / enemies + 5.5x boss; glow orbs in 5 neon colours with pools")
    S.section("Lumenvale plaza at night (3x)", "prism fountain, lumen trees, pavilion, archway, crystal spire, lamps, wisp post, rails; 7 glow orbs + pools; wisps; elves + hero")
    S.cell(sc.crop(sc.getbbox()), "renders/scene_lumenvale_night.png", "", k=4 if sc.width * 4 <= 1360 else 3 if sc.width * 3 <= 1360 else 2)
    S.section("The Prism Vault throne room (2x)", "Lady Sylvaine (5.5x, attack frame 14: drain) on her aura; mirror duelist, prism shards, hero (drained) for scale")
    S.cell(sv.crop(sv.getbbox()), "renders/scene_prism_vault_night.png", "", k=3 if sv.width * 3 <= 1360 else 2)
    S.section("Palette", "sprites: biome palette only; neon only on glow pixels")
    S.cell(palette_card(), "", "", k=1)
    S.section("Elf NPCs (20x32, 4x): idle 0-3 | walk 0-3, 4 facings", "real clothes: separate top / bottom, dark belt, contrasting shoes; long pointed ears; " + H.report_line(reps["alfheim_npcs"]))
    meta = json.loads((OUT / "sprite/alfheim_npcs.json").read_text()); png = OUT / "sprite/alfheim_npcs.png"
    for role in NPCS:
        row = Image.new("RGBA", ((H.FW + 6) * 8 + 10, (H.FH + 6) * 4 + 8), (0, 0, 0, 0))
        for fi, facing in enumerate(H.FACINGS):
            for c, (an, i) in enumerate([("idle", k) for k in range(4)] + [("walk", k) for k in range(4)]):
                fr = H.frame_of(png, meta, role, facing, an, i)
                row.alpha_composite(H.lit_sprite(fr, ("neon_violet_hi", "neon_violet", "neon_violet_lo"), 11, pad=(3, 3)), (c * (H.FW + 6), fi * (H.FH + 6)))
        S.cell(row, role, NPCS[role]["desc"][:105], k=4 if row.width * 4 <= 1360 else 3)
    S.section("Prism Vault enemies (20x32, 3x): idle | walk | attack | die, 4 facings", H.report_line(reps["prism_vault_enemies"]))
    meta = json.loads((OUT / "sprite/prism_vault_enemies.json").read_text()); png = OUT / "sprite/prism_vault_enemies.png"
    for role in ENEMIES:
        seq = [(a, k) for a in A4 for k in range(4)]
        row = Image.new("RGBA", ((H.FW + 4) * 16 + 8, (H.FH + 4) * 4 + 4), (0, 0, 0, 0))
        for fi, facing in enumerate(H.FACINGS):
            for c, (an, i) in enumerate(seq):
                fr = H.frame_of(png, meta, role, facing, an, i)
                row.alpha_composite(H.lit_sprite(fr, ("neon_blue_hi", "neon_blue", "neon_blue_lo") if role == "prismshard" else None, 9, pad=(2, 2)),
                                    (c * (H.FW + 4), fi * (H.FH + 4)))
        S.cell(row, role, ENEMIES[role]["desc"][:120], k=3)
    S.section("Lady Sylvaine (boss, 128x176 = 5.5x, shown 2x): down idle | walk | attack 0-3 | die 0-3", H.report_line(reps["boss_sylvaine"]) + "; hero at the same scale on the left")
    bm = json.loads((OUT / "sprite/boss_sylvaine.json").read_text()); bpng = OUT / "sprite/boss_sylvaine.png"
    hero = H.SP.frame(H.PAL, "wildcaller", "down", "idle", 0).image()
    def brow(sel, with_hero=False):
        r = Image.new("RGBA", (len(sel) * 104 + (24 if with_hero else 0), 176), (0, 0, 0, 0))
        x = 0
        if with_hero:
            r.alpha_composite(hero, (0, 176 - 32)); x = 24
        for (fa, an, i) in sel:
            fr = H.frame_of(bpng, bm, "sylvaine", fa, an, i)
            r.alpha_composite(fr.crop((12, 0, 116, 176)), (x, 0)); x += 104
        return r
    S.cell(brow([("down", "idle", 0), ("down", "walk", 1), ("down", "attack", 1), ("down", "attack", 2), ("down", "attack", 3)], True), "", "", k=2)
    S.cell(brow([("down", "die", 0), ("down", "die", 1), ("down", "die", 2), ("down", "die", 3), ("left", "idle", 0), ("left", "attack", 2)]), "", "", k=2)
    S.cell(brow([("up", "idle", 0), ("up", "attack", 2), ("left", "walk", 1), ("left", "die", 1)]), "", "facings: down / left (right = mirrored) / up", k=2)
    S.section("Kit pieces (night, 3x)", "glow material = crystals, leaf-lights, vines, wisps, water, inlays; moonstone + vault stone")
    for n, pc in built.items():
        im, org = H.render_mesh(pc.mesh, "night", lights_of(pc), pad=8)
        S.cell(im, n, f"{pc.size[0]:.2f} x {pc.size[1]:.2f} x {pc.size[2]:.2f} m", k=3 if im.width * 3 <= 1360 else 2)
    fpng = OUT / "gamefx/alfheim_fx.png"
    S.section("Glow orbs (48 px, 2x): hovering neon orbs + their light pools", "blue cold fire, violet, red, green, pink; light colour = neon_<c>_hi, pool = glow_orb_pool_<c>")
    for c in H.NEON5:
        S.cell(strip_of(fpng, fxm, f"glow_orb_{c}").crop((0, 0, 48 * 4, 48)), f"glow_orb_{c}", "8f 6fps billboard (4 shown)", k=2)
        S.cell(strip_of(fpng, fxm, f"glow_orb_pool_{c}").crop((0, 0, 48 * 2, 48)), f"glow_orb_pool_{c}", "decal", k=2)
    S.section("Other gamefx (48 px, 2x, every frame)", "")
    for n, e in fxm["effects"].items():
        if n.startswith("glow_orb"):
            continue
        S.cell(strip_of(fpng, fxm, n), n, f"{e['kind']} {e['frames']}f {e['fps']}fps" + ("" if e["loop"] else " once"), k=2)
    S.render(OUT / "contact_sheet.png")


README = """# Alfheim pack: Lumenvale (elf city of light) + The Prism Vault (Lady Sylvaine)

Art seat staging pack for **Hearthmoor**. Generated by `src/gen_alfheim.py` (Python + Pillow + numpy, importing the
repo's tools read-only). Source docs: HEARTHMOOR_BUILDER_HANDOFF (Alfheim = light elves, wisps, prism light; Lumenvale =
glowing treetops, neon wisps, wisp catching, orb lanterns with glowing fish; The Prism Vault = energy / light, prism
shards, Mirror Duelists (elite), boss **Lady Sylvaine**, elf vampire queen, drains magic, **neon violet**) and
STORY_SEEDS / DESIGN_EXPANSION (Wisp Night, neon lantern fair). Gloom and glow: moonstone and dark vault stone lit by
violet neon crystals, leaf-lights, wisps and **floating glow orbs** in Bill's five neon colours, each over its own light pool.

![contact sheet](contact_sheet.png)

## Palette (for the Master Builder)
Sprites (elves, enemies, Sylvaine) use the **cozy-village biome palette only** (ink outline). Neon hexes appear only on
gamefx pixels and on the kit `glow` material.

| role | name | hex |
|---|---|---|
| outline | ink | #2a1e1c |
| moonstone (kit stone, city) | plaster_hi + 22% sky | ~#e0e2d8 (lit) |
| vault stone (kit, dungeon) | ink + 38% cloth | ~#323241 |
| elf hair (silver / platinum / gold) | stone_hi / plaster_hi / flower_gold | #cfc2a6 / #f6ecd2 / #f2c24a |
| elf clothes | plaster_hi, sky, cloth, flower_blue, flower_rose, moss, plaster_lo | #f6ecd2 #94c0dc #3e5a8c #6c8cd4 #e47c8c #4a7234 #c4a984 |
| belts / boots | shadow, timber_lo, timber, roof (kid shoes) | #4c3a3e #4a2e20 #7a4e2e #9a4630 |
| crystal (prism shard, tiara) | white, sky, flower_blue, cloth, plaster_hi | #fff8e6 #94c0dc #6c8cd4 #3e5a8c #f6ecd2 |
| Sylvaine gown / cape | cloth (blouse), timber_lo (belt), shadow + roof_lo (skirt), flower_rose + roof_hi (panel), roof_lo + roof (cape) | |
| **neon violet** (signature) | neon_violet / _hi / _lo | **#a45cf0 / #d4a8ff / #6a34b8** |
| neon blue (cold fire) | neon_blue / _hi / _lo | #2ab4ff / #a6ecff / #1c62d8 |
| neon pink | neon_pink / _hi / _lo | #ff4fc8 / #ffb4ea / #b82a8c |
| neon green | neon_green / _hi / _lo | #3cf08a / #b8ffd4 / #14a85a |
| neon red | neon_red / _hi / _lo | #e0302a / #ff5a4a / #a81c22 |

(neon green / pink are new staging hexes added this session for Bill's glow orbs / fireflies; red / violet / blue are the
repo's portal / bifrost hexes.)

## Neon flag (which sprites use neon)
- `sprite/alfheim_npcs`, `sprite/prism_vault_enemies`, `sprite/boss_sylvaine`: **no neon pixels** (biome palette only;
  check-sprite PASS). The lampwright's lantern glow, the prism shard's blue pool and Sylvaine's violet are separate gamefx
  (`lantern_glow`, `pool_blue_small`, `sylvaine_aura` / `drain_*` / `violet_moths`) + lights.
- Neon is used on: every `gamefx/alfheim_fx` effect, and the kit `glow` material (crystals, leaf-lights, vines, wisps,
  fountain water, inlays, lamp prisms).

## Sprites
| sheet | roles | frame | anims | notes |
|---|---|---|---|---|
| `sprite/alfheim_npcs` | elf_lampwright (Elowen Brightwick), elf_scholar (Thalion Prismwright), elf_gardener (Faelin Dewpetal), elf_child (Pip Starling) | 20x32, pivot [10,32] | idle, walk (4 facings) | long pointed ears + props via `al_actors.elf_extra` hooks (drawn before the ink outline) |
| `sprite/prism_vault_enemies` | prismshard (common), mirrorduelist (elite) | 20x32 | idle, walk, attack (hit 14), die | shard hovers with a sparkle trail to the ground row |
| `sprite/boss_sylvaine` | sylvaine | 128x176, pivot [64,176], **scale 5.5** (~170 px tall vs the 29 px hero) | idle, walk, attack, die | boss_sheet format, 28 cols; elegant normal clothes with a clear waist |

All pass the repo's check-sprite (`check_sprite_report.json`). Strips: `sprite/strips/`.

## Kit (`kit/*.glb`, `kit/kit.json`, `src/kit_alfheim.py`)
| piece | size (m) w x h x d | glow / light (lamp colour, range) | placement |
|---|---|---|---|
| `lumen_tree` | 3.2 x 5.0 x 2.4 | violet / blue / pink leaf-lights, glow vines; violet 7 m | plaza corners, treetop walks, 4-6 m apart |
| `lumen_tree_small` | 1.8 x 2.75 x 1.3 | same, smaller; violet 3.9 m | street / garden filler |
| `lumen_lamp` | 0.7 x 2.6 x 0.5 | violet prism lamp; violet 5 m | every 5-6 m along streets / bridges |
| `crystal_spire` | 1.6 x 3.2 x 1.4 | violet (+ blue, pink) crystals; violet 5.5 m | plaza waymarker, vault entrance |
| `prism_fountain` | 2.7 x 2.6 x 2.7 | glowing violet water, streams, prism; violet 6 m | plaza centre |
| `elf_archway` | 3.3 x 3.8 x 0.5 | crystal keystone, column flutes, glow vines; violet 5 m | district gates, Prism Vault door (2.5 m clear) |
| `wisp_lantern_post` | 0.8 x 2.5 x 0.4 | caged blue wisp; blue 4.5 m | wisp-catching meadow edges |
| `light_bridge` | 4.0 x 1.6 x 1.7 | violet deck inlays + post caps; violet 4 m | over glowing streams; deck ~0.6 m (marker `walk_height_center`) |
| `elf_rail` | 2.0 x 1.0 x 0.15 | glowing post caps | terraces, bridges, treetop walks |
| `lumen_pavilion` | 3.3 x 4.2 x 3.3 | crystal roof ribs, hanging orb light; violet 5.5 m | gardens, Wisp Night lantern fair |
| `wisp_jar` | 0.26 x 0.36 x 0.26 | caught blue wisp; blue 1.5 m | shop counters, wisp-catching reward (placeable) |
| `vault_floor` | 2.0 x 0.01 x 2.0 | violet inlay grid | Prism Vault floor (2 m grid) |
| `vault_wall` | 2.0 x 3.32 x 0.56 | violet crystal vein + cluster; violet 3 m | Prism Vault walls |
| `vault_pillar` | 0.8 x 3.5 x 0.8 | violet crystal capital; violet 3.5 m | Prism Vault halls, 4 m apart |
| `sylvaine_throne` | 3.4 x 4.1 x 2.4 | fan of violet crystals; violet 6.5 m | boss room back wall; `boss_stand` marker [0, 0.6, 0.6] |

`kit.json` carries per piece: lamps / lamp colour / range, blockers, size, plus `fx` (which gamefx to attach) and
`placement`. Orb lanterns with glowing fish (also listed for Lumenvale) are in the **orb_lanterns** pack: use
`orb_*_violet` / `orb_*_blue` / `orb_grand` there.

## gamefx (`gamefx/alfheim_fx.png/.json`, 48 px, hd2d portal format)
- **Glow orbs** (Bill): `glow_orb_blue / violet / red / green / pink` (billboard, 8f 6 fps, pivot [24,33], hover 1.1-2.2 m,
  light = neon_<c>_hi 0.7 / 3 m) each with its pool decal `glow_orb_pool_<c>` (the light-pool colour = the orb colour).
- Pools / fog: `pool_violet` (r ~2.4 m), `pool_violet_small`, `pool_blue_small`, `glow_mist_violet` (foggy glow areas).
- Ambient: `light_motes`, `prism_sparkle` (5-colour glints), `fountain_sparkle`.
- Wisps: `wisp_violet / blue / pink` (figure-eight drift, light 0.6 / 2 m), `wisp_catch` (once), `lantern_glow`
  (lampwright's lantern; offsets in the json notes).
- Sylvaine: `sylvaine_aura` (decal under her, scale x2-3), `drain_stream` (48 px segment, flows right -> left: tile /
  rotate from target to her hand), `drain_hit` (on the target), `violet_moths` (once, her death).
- Enemies: `prism_shatter` (once), `mirror_flash` (once).

## Placement recipe (Lumenvale plaza, see renders/scene_lumenvale_night.png)
1. Pave 14 x 11 m in moonstone (or the biome cobble tinted cool). `prism_fountain` at the centre + `pool_violet` +
   `fountain_sparkle`.
2. Back edge: `lumen_tree`, `lumen_pavilion`, `elf_archway` (gate out), `lumen_tree_small`. Each gets `pool_violet`.
3. Sides: `crystal_spire` (+ `prism_sparkle` at lift 1.4) and `wisp_lantern_post` (+ `pool_blue_small`, a `wisp_blue` nearby).
4. Front: two `lumen_lamp`s 6 m apart, `elf_rail` runs along terrace edges.
5. Float 5-7 **glow orbs** (mix all five colours) at 1.4-2.4 m with their pools directly below; 2-3 `wisp_*`; 2-3
   `glow_mist_violet` patches in corners; `light_motes` under trees.
6. Elves: Elowen by the wisp post with `lantern_glow`, Thalion near the fountain, Faelin under the trees, Pip chasing wisps.
Prism Vault (renders/scene_prism_vault_night.png): `vault_floor` grid, `vault_wall` ring, `vault_pillar`s 4 m apart,
`sylvaine_throne` at the back centre with two `crystal_spire`s, violet / pink / blue / red orbs, `glow_mist_violet`;
Sylvaine stands on `boss_stand` with `sylvaine_aura` (x2-3) under her.

## Drop-in (Master Builder)
1. Sprites: copy `sprite/*.png/.json` into the game's sprite folder; they are in the exact `hd2d sprite` /
   `hd2d boss_sheet` formats (or regenerate with the repo tools using the `src/al_actors.py` hooks and `al_boss.py` drawer).
2. Kit: copy `src/kit_alfheim.py` to `tools/kit/` + the import line from its docstring, or use the `.glb`s directly.
3. gamefx: copy `gamefx/alfheim_fx.png/.json` (+ strips) beside the other portal-format fx.
4. Lights: use each kit piece's `lamps` / `lamp_color` / `lamp_range` and each fx `light` block; no bloom, hard alpha.

## Notes
- The repo has a `realm-alfheim` branch / worktree (not touched); names here follow the docs: Lumenvale, The Prism
  Vault, Lady Sylvaine, Mirror Duelists, prism shards. Not drawn here: Lumi the wisp companion (pets/ is owned by
  another worker), hostile neon will-o-wisps (use `wisp_*` fx on a small hitbox) and crystal golems.
- Sylvaine's 5.5x scale follows the boss convention (>=5x); the docs give no exact number.
"""

if __name__ == "__main__":
    main()
