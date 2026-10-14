"""Verdant Heart pack generator (Hearthmoor Art seat). Run:  python3 gen_verdant_heart.py
Writes ../ (the verdant_heart pack). Reads the hd2d-suite repo read-only."""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "_lib"))   # the shared lib wins; src/hmart.py is its frozen copy
import hmart as H  # noqa: E402
import kit_verdant_heart as KV  # noqa: E402
import vh_boss  # noqa: E402
import vh_bosses2 as B2  # noqa: E402
import vh_enemies as E  # noqa: E402
import vh_fx as V  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

OUT = HERE.parent
A4 = ("idle", "walk", "attack", "die")

ENEMIES = {
    "rottreant": {"draw": E.rottreant, "kind": "enemy", "enemy": True, "named": True, "anims": A4,
                  "desc": "rot treant: a squat walking tree of dark bark under a drooping moss crown with red white-spotted "
                          "toadstools, warm lamp-glow knot eyes, branch-arm slam; dies into a mossy stump",
                  "light": {"color": H.ALLC["lamp"], "intensity": 0.35, "range": 1.4, "note": "eyes; optional"},
                  "stats_hint": {"tier": "common", "hp": "high", "speed": "slow", "attack": "slam (frames 12-15, hit on 14)"}},
    "sporeelemental": {"draw": E.sporeelemental, "kind": "enemy", "enemy": True, "named": True, "anims": A4,
                       "desc": "spore elemental (dungeon tier): a puff of moss and glowing gold spores under a big red "
                               "white-spotted cap, wisp tail to the floor, lamp eyes; attack throws spore streams; dies "
                               "dropping its cap on a spore heap",
                       "light": {"color": H.ALLC["flower_gold"], "intensity": 0.5, "range": 1.8, "pool": "toadstool_glow_pool"},
                       "stats_hint": {"tier": "common", "hp": "low", "speed": "medium", "attack": "spore_burst fx on frame 14"}},
}

BOSS_SHEETS = {
    "blight_regent": {"blightregent": {
        "draw": vh_boss.blightregent, "frame": (128, 176), "scale": 5.5, "anims": A4,
        "desc": "The Blight Regent, corrupted nature lord: gnarled bark body, moss mantle with toadstools, antlers of branch "
                "hung with red white-spotted toadstools, mauve blight blossoms and gold spore-lanterns, sickly violet-rose eyes in a "
                "hollow bark mask, a dead-sapling staff, a root ribcage around a violet wound with the blue frost-iron spike "
                "and rime frost-flowers (the only blue on him). Die: kneels, the spike slides out and lies on the mossy "
                "root mound, then a fresh sapling (cleansed; V0 Sapling Door). Rotwood Hollow R7 boss.",
        "light": {"color": H.ALLC["neon_violet"], "intensity": 0.9, "range": 6.0, "pool": "blight_aura"},
        "notes": "attack frame 14 = two-arm root slam (spawn root_eruption x3-5); die frame 27 -> regent_cleansed fx",
        "stats_hint": {"tier": "boss", "height_x_player": 5.5}}},
    "hjortur": {
        "hjortur": {"draw": B2.hjortur, "frame": (144, 192), "scale": 6.0, "anims": A4,
                    "desc": "Hjortur the Greenheart, elder stag-king (guardian / befriend path): living-branch antlers in leaf "
                            "with gold spore-lanterns and moonpetals, moss mantle with fawn-spots, long white elder's beard, "
                            "a glowing leaf mark on his brow, a moonpetal garland. Die = he kneels and lies down at peace.",
                    "light": {"color": H.ALLC["neon_green"], "intensity": 0.9, "range": 7.0, "pool": "greenheart_aura"},
                    "notes": "attack = antler lowering charge + stomp (frame 14: root/leaf burst)",
                    "stats_hint": {"tier": "boss", "height_x_player": 6.0, "path": "befriend (trial)"}},
        "hjortur_corrupted": {"draw": B2.hjortur_corrupted, "frame": (144, 192), "scale": 6.0, "anims": A4,
                              "desc": "Hjortur corrupted (conquer path): dark leaves, red toadstools and mauve blight blossoms "
                                      "on the antlers, blight veins, rose eyes, a blight knot on the brow. Die = he lies down "
                                      "and the corruption lifts (leaves green again, eyes close).",
                              "light": {"color": H.ALLC["neon_violet"], "intensity": 0.9, "range": 7.0, "pool": "blight_aura"},
                              "stats_hint": {"tier": "boss", "height_x_player": 6.0, "path": "conquer"}}},
    "thornmother": {"thornmother": {
        "draw": B2.thornmother, "frame": (48, 77), "scale": 2.4, "anims": A4,
        "desc": "The Thornmother (Verdant Heart V4 rare, story/verdant_heart.md): a corrupted dryad-tree - willowy figure "
                "of bark and thorns: thorn-studded bark bodice, dark vine bound at the waist, long skirt of willow fronds, "
                "root feet, willow-frond hair, pale birch face with violet-rose eyes, a moonpetal crown gone violet, a "
                "bramble staff with a violet bud. Die: sinks into a mound that blooms with violet moonpetals.",
        "light": {"color": H.ALLC["neon_violet"], "intensity": 0.5, "range": 2.5, "pool": "pool_violet"},
        "notes": "attack frames 13-14: bramble whips from the hem (+ thorn_lash fx)",
        "stats_hint": {"tier": "rare", "height_x_player": 2.4}}},
}

KIT_META = {
    "vh_floor": {"tile_m": 4.0, "note": "grid 4 m; rotate 0/90/180/270 freely to break repeats"},
    "vh_wall": {"run_m": 4.0, "note": "back / side walls; front face +z"},
    "vh_ceiling_lip": {"note": "above walls at y 4.4; hang hanging_vines / dripcaps beneath"},
    "glowroot_arch": {"fx": ["glowroot_pool"], "note": "room doorway; walk-through"},
    "stream_straight": {"fx": ["stream_flow", "glow_mist_blue"], "flow": "+z", "tile_m": 2.0},
    "stream_bend": {"fx": ["stream_flow"], "flow": "-z in, +x out", "tile_m": 2.0},
    "glow_pool": {"fx": ["glow_mist_blue", "glowfrog_*_idle"], "note": "frogs on the lily pads / stones"},
    "waterfall": {"fx": ["waterfall_sheet", "waterfall_splash", "glow_mist_blue"], "outlet": [0, 0, 1.4], "note": "connect stream_straight at the outlet"},
    "heart_spring": {"fx": ["heart_spring_bubbles", "heart_spring_pool"]},
    "glowroot_cluster": {"fx": ["glowroot_pool"]},
    "toadstool_giant": {"fx": ["toadstool_glow_pool", "spore_motes"]},
    "toadstool_shelf": {"fx": ["toadstool_glow_pool"]},
    "neon_mushrooms_pink": {"fx": ["pool_pink"]}, "neon_mushrooms_blue": {"fx": ["glowroot_pool"]},
    "neon_mushrooms_violet": {"fx": ["pool_violet"]}, "dripcap": {"fx": ["pool_pink"]},
    "glowfern": {"fx": ["pool_violet"]}, "glowfern_blue": {"fx": ["glowroot_pool"]},
    "hanging_vines": {"fx": ["pool_green", "fireflies_green"]},
    "blight_bloom": {"fx": ["pool_violet", "glow_mist_violet"], "note": "cleansing dims it (swap lamp off)"},
    "heartseed_cradle": {"fx": ["pool_green", "glow_mist_green", "greenheart_aura"], "note": "Hjortur's arena centre"},
}


# ============================================================== scene
def placed(built, name, pos, roty=0.0):
    pc = built[name]
    m = pc.mesh.xf(pos, rot=(0, roty, 0))
    lamps = []
    lc = pc.markers.get("lamp_color")
    for lp in pc.markers.get("lamps", []):
        c, s_ = math.cos(roty), math.sin(roty)
        x, z = lp[0] * c + lp[2] * s_, -lp[0] * s_ + lp[2] * c
        lamps.append(((pos[0] + x, pos[1] + lp[1], pos[2] + z), lc, pc.markers.get("lamp_range", 4.0), 1.0))
    return m, lamps


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


def scene(built, fxm, crm, t=0):
    K = H.kit_module()
    M = K.Mesh()
    lights = []
    def put(name, pos, roty=0.0):
        m, L = placed(built, name, pos, roty)
        M.add(m); lights.extend(L)
    for x in (-6, -2, 2, 6):
        for z in (-4, 0, 4):
            put("vh_floor", (x, 0, z), (x + z) % 3 * math.pi / 2)
    put("vh_wall", (-6.2, 0, -6.4)); put("vh_wall", (2.4, 0, -6.4)); put("vh_wall", (6.4, 0, -6.4))
    put("waterfall", (-2.0, 0, -5.3))
    put("vh_ceiling_lip", (4.4, 0, -6.0)); put("hanging_vines", (4.4, 0, -5.7))
    put("stream_straight", (-2.0, 0, -3.0)); put("stream_straight", (-2.0, 0, -1.0))
    put("stream_bend", (-2.0, 0, 1.0))
    put("stream_straight", (0.0, 0, 1.0), math.pi / 2); put("stream_straight", (2.0, 0, 1.0), math.pi / 2)
    put("glow_pool", (4.9, 0, 1.2))
    put("toadstool_giant", (-6.0, 0, -2.6)); put("toadstool_shelf", (-4.6, 0, 4.0))
    put("neon_mushrooms_pink", (1.2, 0, -3.6)); put("neon_mushrooms_blue", (6.9, 0, -2.4)); put("neon_mushrooms_violet", (-6.6, 0, 3.6))
    put("dripcap", (2.9, 0, -4.6))
    put("glowfern", (-0.6, 0, 4.2)); put("glowfern_blue", (1.4, 0, 4.8)); put("glowfern", (7.0, 0, 4.4)); put("glowfern_blue", (-7.2, 0, 0.6))
    put("glowroot_cluster", (-4.4, 0, 0.4))
    im, org, zb = H.render_mesh(M, "night", lights, pad=8, depth=True)
    can = Image.new("RGBA", im.size, (10, 10, 22, 255))                 # cave darkness behind everything
    can.alpha_composite(im)
    fxpng, crpng = OUT / "gamefx/verdant_fx.png", OUT / "gamefx/verdant_critters.png"
    def fxf(name, i=None):
        e = fxm["effects"][name]
        return H.fx_frame(fxpng, fxm, name, (t if i is None else i) % e["frames"])
    for (name, c, i) in (("toadstool_glow_pool", (-6.0, 0, -2.2), 0), ("pool_pink", (1.2, 0, -3.3), 1), ("glowroot_pool", (6.9, 0, -2.1), 2),
                         ("pool_violet", (-6.6, 0, 3.9), 3), ("pool_pink", (2.9, 0, -4.2), 2), ("pool_violet", (-0.6, 0, 4.4), 1),
                         ("glowroot_pool", (-4.4, 0, 0.7), 0), ("pool_green", (4.4, 0, -4.9), 1), ("toadstool_glow_pool", (-4.6, 0, 4.4), 3),
                         ("glowroot_pool", (-3.6, 0, 2.2), 4), ("pool_violet", (6.0, 0, 3.6), 2),
                         ("stream_flow", (-2.0, 0, -3.0), 0), ("stream_flow", (-2.0, 0, -1.0), 3),
                         ("glow_mist_blue", (-1.6, 0, -2.2), 0), ("glow_mist_blue", (4.6, 0, 1.6), 3), ("glow_mist_violet", (0.6, 0, 1.4), 5),
                         ("glow_mist_green", (5.0, 0, -4.0), 2)):
        decal_over(can, fxf(name, i + t), c, org, zb, fxm["effects"][name]["lift"])
    bills = [("waterfall_sheet", (-2.0, 0.65, -4.85), 0), ("waterfall_splash", (-2.0, 0.0, -4.4), 0),
             ("glow_orb_blue", (-3.6, 1.1, 2.2), 0), ("glow_orb_violet", (6.0, 1.1, 3.6), 2), ("glow_orb_red", (-6.6, 1.1, -0.2), 4),
             ("glow_orb_green", (4.4, 1.1, -4.4), 1), ("glow_orb_pink", (0.4, 1.1, -1.8), 3),
             ("fireflies_neon", (-1.0, 0.6, -0.4), 0), ("fireflies_neon", (5.0, 0.6, 2.4), 3), ("fireflies_neon", (-5.4, 0.6, 2.0), 5),
             ("fireflies_green", (4.2, 1.6, -4.6), 2), ("fireflies_pink", (2.2, 0.8, -3.0), 1), ("spore_motes", (-6.0, 0.4, -2.2), 0),
             ("fireflies_blue", (-2.0, 1.6, -3.4), 4)]
    actors = []
    hero = H.SP.frame(H.PAL, "wildcaller", "down", "idle", 0).image()
    actors.append((hero, (0.6, 0, 3.0)))
    meta = json.loads((OUT / "sprite/verdant_actors.json").read_text())
    png = OUT / "sprite/verdant_actors.png"
    actors.append((H.frame_of(png, meta, "rottreant", "right", "walk", 1), (-2.8, 0, 3.8)))
    actors.append((H.frame_of(png, meta, "sporeelemental", "left", "idle", 1), (3.6, 0, 3.4)))
    items = [(c[2], "fx", n, c, i) for (n, c, i) in bills] + [(p[2], "act", im_, p, 0) for (im_, p) in actors]
    frogs = [("glowfrog_blue_idle", (4.0, 0.1, 0.1), 2), ("glowfrog_pink_idle", (5.9, 0.1, 0.5), 0), ("glowfrog_green_idle", (-1.0, 0.05, 2.0), 1),
             ("glowfrog_violet_idle", (-3.0, 0.05, -2.0), 3), ("glowfrog_green_hop", (3.0, 0.05, 2.5), 3)]
    items += [(c[2], "frog", n, c, i) for (n, c, i) in frogs]
    for z, kind, a, c, i in sorted(items, key=lambda r: r[0]):
        if kind == "fx":
            H.billboard_over(can, fxf(a, i + t), c, org, zb, tuple(fxm["effects"][a]["pivot"]))
        elif kind == "frog":
            H.billboard_over(can, H.fx_frame(crpng, crm, a, (i + t) % crm["effects"][a]["frames"]), c, org, zb, (12, 23))
        else:
            H.billboard_over(can, a, c, org, zb, (10, 31))
    return can


# ============================================================== contact sheet helpers
def strip_of(fxpng, fxm, name, cell, bgc=(12, 14, 26, 255)):
    e = fxm["effects"][name]
    s = Image.new("RGBA", (cell * e["frames"], cell), bgc)
    for i in range(e["frames"]):
        s.alpha_composite(H.fx_frame(fxpng, fxm, name, i), (i * cell, 0))
    return s


def boss_frame(png, meta, role, facing, anim, i):
    fw, fh = meta["frame"]
    for fr in meta["roles"][role]["frames"]:
        if fr["facing"] == facing and fr["anim"] == anim and fr["i"] == i:
            return Image.open(png).crop((fr["x"], fr["y"], fr["x"] + fw, fr["y"] + fh))


def main():
    rep = H.write_actors(OUT / "sprite", "verdant_actors", ENEMIES)
    print("actors", H.report_line(rep))
    reports = {"verdant_actors": H.report_line(rep)}
    for sheet, roles in BOSS_SHEETS.items():
        r = H.write_boss(OUT / "sprite", f"boss_{sheet}", roles)
        reports[f"boss_{sheet}"] = H.report_line(r)
        print(sheet, H.report_line(r))
    fxm = H.write_fx(OUT / "gamefx", "verdant_fx", V.FX, 48)
    crm = H.write_fx(OUT / "gamefx", "verdant_critters", V.CRITTERS, 24)
    built, km = H.build_kit(OUT / "kit", KV.pieces, KIT_META)
    print("kit", len(built), "pieces")
    rd = OUT / "renders"; rd.mkdir(exist_ok=True)
    for n, pc in built.items():
        lc = pc.markers.get("lamp_color")
        im, _ = H.render_mesh(pc.mesh, "night", [((0, 1.5, 0.6), lc, 5, 1.0)] if lc else [], pad=6)
        im.save(rd / f"{n}_night.png")
    sc = scene(built, fxm, crm, t=0)
    sc.save(rd / "scene_verdant_heart_night.png")
    contact(built, fxm, crm, sc)
    (OUT / "check_sprite_report.json").write_text(json.dumps(reports, indent=1))
    H.finish_pack(OUT, README)
    (OUT / "READY.txt").write_text(READY)


def contact(built, fxm, crm, sc):
    S = H.Sheet("The Verdant Heart (dungeon under Vanaheim) - bioluminescent cavern, enemies, Blight Regent, Hjortur, Thornmother",
                "mood: Bill's refs (neon mushrooms over black water, glow ferns, glowing stream + waterfall, hanging glow vines, fireflies, glow frogs, glow orbs)")
    fxpng, crpng = OUT / "gamefx/verdant_fx.png", OUT / "gamefx/verdant_critters.png"
    S.section("Mood scene (night, 4x)", "kit pieces + light pools + mist + stream flow + waterfall + orbs + fireflies + frogs; hero, rot treant, spore elemental for scale")
    S.cell(sc.crop(sc.getbbox()), "scene_verdant_heart_night.png (renders/)", "16 x 13 m room assembled from the kit; all glow = emissive pixels + small lights + dithered pools", k=4 if sc.width * 4 <= 1360 else 3)
    # scale lineup
    S.section("Scale lineup (2x)", "hero 29 px visible | Thornmother 2.4x | Blight Regent 5.5x | Hjortur 6x | corrupted Hjortur  (frame heights 77 / 176 / 192 = 2.4 / 5.5 / 6.0 x the 32 px hero frame)")
    hero = H.SP.frame(H.PAL, "wildcaller", "down", "idle", 0).image()
    figs = [hero]
    for sheet, role in (("thornmother", "thornmother"), ("blight_regent", "blightregent"), ("hjortur", "hjortur"), ("hjortur", "hjortur_corrupted")):
        meta = json.loads((OUT / f"sprite/boss_{sheet}.json").read_text())
        figs.append(boss_frame(OUT / f"sprite/boss_{sheet}.png", meta, role, "down", "idle", 0))
    W = sum(f.width for f in figs) + 8 * len(figs) + 20
    Hh = max(f.height for f in figs) + 12
    line = Image.new("RGBA", (W, Hh), (0, 0, 0, 0))
    ImageDraw.Draw(line).rectangle([0, Hh - 6, W, Hh - 5], fill=H.rgba("stone_lo"))   # shared ground line
    x = 10
    for f in figs:
        line.alpha_composite(f, (x, Hh - 6 - f.height))
        x += f.width + 8
    S.cell(line, "lineup", "", k=2)
    # boss detail
    for sheet, roles in BOSS_SHEETS.items():
        meta = json.loads((OUT / f"sprite/boss_{sheet}.json").read_text())
        png = OUT / f"sprite/boss_{sheet}.png"
        for role in roles:
            k = 4 if role == "thornmother" else 2
            S.section(f"{role} ({roles[role]['scale']}x, frame {roles[role]['frame'][0]}x{roles[role]['frame'][1]}, {k}x)",
                      "down idle | up idle | left walk1 | down attack 0-3 | down die 0-3")
            fs = [("down", "idle", 0), ("up", "idle", 0), ("left", "walk", 1)] + [("down", "attack", i) for i in range(4)] + [("down", "die", i) for i in range(4)]
            fw, fh = meta["frame"]
            per = max(1, int(1360 / (k * (fw + 4))))
            for s0 in range(0, len(fs), per):
                chunk = fs[s0:s0 + per]
                row = Image.new("RGBA", ((fw + 4) * len(chunk), fh), (0, 0, 0, 0))
                for j, (fc, an, i) in enumerate(chunk):
                    row.alpha_composite(boss_frame(png, meta, role, fc, an, i), (j * (fw + 4), 0))
                S.cell(row, role if s0 == 0 else "", roles[role]["desc"][:150] if s0 == 0 else "", k=k)
    S.section("Enemies (20x32, 3x): idle | walk | attack | die, 4 facings", "check-sprite PASS; biome palette only (lamp-glow eyes / gold spores)")
    meta = json.loads((OUT / "sprite/verdant_actors.json").read_text())
    png = OUT / "sprite/verdant_actors.png"
    for role in ENEMIES:
        seq = [(a, i) for a in A4 for i in range(4)]
        row = Image.new("RGBA", ((H.FW + 6) * 16 + 20, (H.FH + 6) * 4 + 12), (0, 0, 0, 0))
        for fi, facing in enumerate(H.FACINGS):
            for c, (an, i) in enumerate(seq):
                fr = H.frame_of(png, meta, role, facing, an, i)
                pool = ("flower_gold", "lamp", "timber") if role == "sporeelemental" else None
                row.alpha_composite(H.lit_sprite(fr, pool, 10, pad=(3, 3)), (c * (H.FW + 6), fi * (H.FH + 6)))
        S.cell(row, role, ENEMIES[role]["desc"][:140], k=3 if row.width * 3 <= 1360 else 2)
    S.section("Glow critters + orbs + fireflies (4x)", "glow frogs (24 px cells: idle throat pulse | hop) in blue / green / pink / violet; hovering glow orbs; neon fireflies")
    for c in ("blue", "green", "pink", "violet"):
        row = Image.new("RGBA", (24 * 12, 24), (12, 14, 26, 255))
        row.alpha_composite(strip_of(crpng, crm, f"glowfrog_{c}_idle", 24), (0, 0))
        row.alpha_composite(strip_of(crpng, crm, f"glowfrog_{c}_hop", 24), (24 * 6, 0))
        S.cell(row, f"glowfrog_{c}", "idle 6f 4fps | hop 6f 10fps", k=4)
    for c in ("blue", "violet", "red", "green", "pink"):
        S.cell(strip_of(fxpng, fxm, f"glow_orb_{c}", 48).crop((0, 0, 48 * 4, 48)), f"glow_orb_{c}", "8f 6fps (4 shown); light 4 m", k=2)
    S.cell(strip_of(fxpng, fxm, "fireflies_neon", 48).crop((0, 0, 48 * 4, 48)), "fireflies_neon", "mixed 5 neons; + single-colour rows", k=2)
    S.section("Kit pieces (night renders, 3x)", "glow material = emissive (neon hexes allowed on environment glow); structure = biome palette")
    names = list(built)
    for n in names:
        lc = built[n].markers.get("lamp_color")
        im, org = H.render_mesh(built[n].mesh, "night", [((0, 1.5, 0.6), lc, 5, 1.0)] if lc else [], pad=10)
        poolfx = (KIT_META.get(n, {}).get("fx") or [None])[0]
        can = Image.new("RGBA", im.size, (0, 0, 0, 0))
        if poolfx and poolfx.startswith(("pool_", "glowroot_pool", "toadstool_glow_pool", "heart_spring_pool")):
            col = {"pool_pink": ("neon_pink_hi", "neon_pink", "neon_pink_lo"), "pool_violet": ("neon_violet_hi", "neon_violet", "neon_violet_lo"),
                   "pool_green": ("neon_green_hi", "neon_green", "neon_green_lo"), "glowroot_pool": ("neon_blue_hi", "neon_blue", "neon_blue_lo"),
                   "toadstool_glow_pool": ("neon_red_hi", "neon_red", "neon_red_lo"), "heart_spring_pool": ("cold_hi", "cold", "cold_lo")}[poolfx]
            can.alpha_composite(H.pool_layer(can.size, H.project((0, 0, 0.3), org), min(40, im.width * 0.45), col, n))
        can.alpha_composite(im)
        S.cell(can, n, f"{built[n].size[0]:.1f} x {built[n].size[1]:.1f} x {built[n].size[2]:.1f} m", k=3 if im.width * 3 < 700 else 2)
    S.section("gamefx (48 px, 2x): every frame", "")
    for n, e in fxm["effects"].items():
        if n.startswith(("fireflies_", "glow_orb_")) and n != "fireflies_neon":
            continue
        S.cell(strip_of(fxpng, fxm, n, 48), n, f"{e['kind']} {e['frames']}f {e['fps']}fps" + ("" if e["loop"] else " once"), k=2)
    S.render(OUT / "contact_sheet.png")


READY = """verdant_heart: READY (2026-10-05, Hearthmoor Art seat)
See README.md + contact_sheet.png. Sprites pass check-sprite; kit .glb + kit.json; gamefx verdant_fx (48 px) + verdant_critters (24 px).
"""

README = """# The Verdant Heart pack (dungeon under Vanaheim): bioluminescent cavern, enemies, three big foes

Art seat staging pack for **Hearthmoor**. Generated procedurally by `src/gen_verdant_heart.py` (Python + Pillow +
numpy, importing the repo's `tools/sprite`, `tools/kit`, `tools/check-sprite` read-only). Mood pushed hard toward
Bill's reference boards (`art/_refs/bill_ref_1..6`): neon mushrooms over black water, glowing fern spirals, glowing
underground stream / pool / waterfall, hanging glow vines, glow fog, neon fireflies, glow frogs and hovering glow orbs,
plus his red white-spotted toadstools and neon-blue cold fire.

![contact sheet](contact_sheet.png)

> **Docs (confirmed by the lead 2026-10-06 + story/verdant_heart.md):** **The Rotwood Hollow** is Vanaheim's main
> dungeon (rot treants, spore elementals, boss **The Blight Regent**, R7, 5.5x). **The Verdant Heart** is the optional
> deeper dungeon (V4 rare **The Thornmother**, 2.4x; V5 boss **Hjortur the Greenheart**, 6x: guardian trial on the
> befriend path, corrupted fight on the conquer path). This pack ships the Regent too (packaged here for convenience);
> the kit works for both dungeons (use `blight_bloom` + violet mist for the Rotwood, the clean glow set +
> `heartseed_cradle` for the Heart). The Regent and Thornmother were revised on 2026-10-06 to match the doc (Regent:
> violet eyes, dead-sapling staff, root ribcage + violet wound with the blue frost-iron spike and rime; Thornmother:
> corrupted dryad-tree with a moonpetal crown gone violet). **Not drawn yet:** the doc's regular Verdant enemies
> `thornhex`, `lifewisp` and the Thornmother's summoned `thornnymph`. The game already has a Vanaheim `sporeling`;
> `sporeelemental` here is a separate dungeon-tier variant.

## Sprites (`sprite/`)
| sheet | roles | frame | scale | check-sprite |
|---|---|---|---|---|
| `verdant_actors.png/.json` | `rottreant`, `sporeelemental` | 20x32, pivot [10,32] | 1x | PASS |
| `boss_blight_regent.png/.json` | `blightregent` | 128x176, pivot [64,176] | 5.5 (figure ~171 px = 5.9x the hero's 29 px) | PASS |
| `boss_hjortur.png/.json` | `hjortur`, `hjortur_corrupted` | 144x192, pivot [72,192] | 6.0 | PASS |
| `boss_thornmother.png/.json` | `thornmother` | 48x77, pivot [24,77] | 2.4 | PASS |

All use the enemy column layout: idle 0-3 (3 fps, loop 0,1,2,1), walk 4-7 (8 fps), attack 12-15 (10 fps, loop
0,1,2,2,3; hit on frame 14), die 24-27 (6 fps, once); rows down / up / left / right (right = mirrored left). Boss sheets
are `tools/sprite/boss_sheet.py` format (`boss: true`, `scale`, size_bounds [[12, fw-2], [12, fh]]), all <= 4096 px.
Each role's JSON carries `light` (colour / intensity / range / pool fx) and `stats_hint`.

- **Rot treant**: squat walking tree, drooping moss crown with red white-spotted toadstools, lamp-glow knot eyes, branch-arm slam; dies into a mossy stump.
- **Spore elemental**: moss-and-gold-spore puff under a big red white-spotted cap, wisp tail to the floor (row 30), lamp eyes, spore-stream attack; dies dropping its cap.
- **The Blight Regent** (5.5x): gnarled bark lord in a moss mantle with toadstools, antlers hung with toadstools, mauve blight blossoms and gold spore-lanterns, sickly violet-rose eyes in a hollow bark mask, a dead-sapling staff topped with red toadstools, and a root ribcage around a violet wound with the **blue frost-iron spike** and white rime frost-flowers (the spike is the only blue on him). Attack = two-arm root slam (frame 14, spawn `root_eruption`). Die = he sinks, the spike lies on the mossy root mound, then a **fresh sapling** (cozy ending; play `regent_cleansed`). Pool: `blight_aura`.
- **Hjortur the Greenheart** (6x): elder stag-king, living-branch antlers in leaf with gold spore-lanterns and moonpetals, moss mantle with fawn-spots, long white beard, glowing leaf mark on his brow, moonpetal garland. Attack = antler-lowering charge + stomp. Die = kneels and lies down at peace (befriend: he yields). Pool: `greenheart_aura`.
- **Hjortur, corrupted** (conquer path): same rig with dark leaves, red toadstools and blight blossoms on the antlers, blight veins, rose eyes. Die = the corruption lifts (green leaves return, eyes close). Pool: `blight_aura`.
- **The Thornmother** (Verdant V4 rare, 2.4x): a corrupted dryad-tree per the doc: willowy figure of bark and thorns, thorn-studded bark bodice over a skirt of trailing willow fronds with a dark vine bound at the waist (top/bottom read kept), root feet, willow-frond hair, pale birch face with violet-rose eyes, **moonpetal crown gone violet**, bramble staff with a violet bud. Attack = bramble whips (+ `thorn_lash`; the doc's seed bombs can reuse `thorn_lash` / spore fx). Die = sinks into a mound blooming with violet moonpetals. Pool: `pool_violet`.

**Neon use (per Bill 2026-10-05): none of the sprites above use neon pixels.** They stay biome-palette only so they
pass check-sprite; their glow is lamp / gold / rose palette pixels plus the light + pool fx listed in their JSON.

## gamefx (`gamefx/`)
`verdant_fx.png/.json` (48 px cells, `hd2d portal` format) - **all neon is here, on glow pixels**:

| group | effects |
|---|---|
| water | `stream_flow` (decal, chains per 2 m tile), `waterfall_sheet` (billboard, lift 0.65), `waterfall_splash`, `heart_spring_bubbles`, `heart_spring_pool` |
| light pools (decal) | `glowroot_pool` (neon blue), `toadstool_glow_pool` (red), `pool_violet`, `pool_green`, `pool_pink` |
| glow fog (decal, lift 0.35) | `glow_mist_blue`, `glow_mist_violet`, `glow_mist_green` - sparse dither so it reads translucent; overlap 3-6 with random frame offsets |
| fireflies (billboard) | `fireflies_neon` (mixed) + `fireflies_blue/violet/red/green/pink` |
| glow orbs (billboard, lift 1.1) | `glow_orb_blue/violet/red/green/pink`: hovering orb, bob, halo sparkles; light 0.8 / 4 m in its colour; pair each with its pool (blue -> glowroot_pool, red -> toadstool_glow_pool, violet/green/pink -> pool_<c>) |
| ambient / boss | `spore_motes`, `blight_aura`, `root_eruption` (once), `spore_burst` (once), `regent_cleansed` (once, light curve), `greenheart_aura`, `thorn_lash` (once) |

`verdant_critters.png/.json` (24 px cells, pivot [12,23]): `glowfrog_<blue|green|pink|violet>_idle` (6f, 4 fps:
throat-sac pulse + blink; light 0.3 / 1.2 m) and `_hop` (6f, 10 fps: move ~0.5 m across it). Ambient critters: sit
them on pool stones, lily pads and stream banks.

Neon hexes (glow pixels only): blue `#2ab4ff/#a6ecff/#1c62d8`, violet `#a45cf0/#d4a8ff/#6a34b8`, red
`#e0302a/#ff5a4a/#a81c22`, cold fire `#5ab4f0/#d8f4ff/#2a6cb0`, **new**: green `#3cf08a/#b8ffd4/#14a85a`, pink
`#ff4fc8/#ffb4ea/#b82a8c` (added for orbs / fireflies / bioluminescence).

## Kit (`kit/*.glb`, `kit/kit.json`, `src/kit_verdant_heart.py`)
Structure: `vh_floor` (4x4 m tile with glow-moss specks), `vh_wall` (4 m, cold-fire veins), `vh_ceiling_lip` (4.4 m
overhang), `glowroot_arch` (3.4 m doorway). Water: `stream_straight` (2 m, flows +z), `stream_bend` (2x2 m, -z in / +x
out), `glow_pool` (3.8 m black-glass pond: bright shallows, dark mirror middle, glowing lily pads), `waterfall` (3.6 m
cliff + glowing fall + splash basin, outlet at +z), `heart_spring` (bubbly spring ringed by glowing roots). Flora:
`glowroot_cluster`, `toadstool_giant` (3.4 m, red #e0302a caps, white spots, warm gills), `toadstool_shelf`,
`neon_mushrooms_pink/_blue/_violet`, `dripcap` (pink cap trailing glowing tendrils), `glowfern` / `glowfern_blue`
(fiddlehead spirals), `hanging_vines` (glow-bulb curtain from 4.2 m), `blight_bloom` (violet), `heartseed_cradle`
(Hjortur's arena). Every glowing piece carries a `lamps` marker with `lamp_color` / `lamp_fixed` / `lamp_range`;
`kit.json` lists the recommended fx per piece (pools, mist, flow, frogs).

**Neon use:** only the `glow` material on mushrooms, ferns, vines, roots, water, the heartseed and bulbs; structure
(stone, bark, moss, stems) is biome palette.

## Placement recipe (the mood scene on the sheet, `renders/scene_verdant_heart_night.png`)
1. Floor tiles on a 4 m grid, back walls, `waterfall` in the back wall, `stream_straight` x2 from its outlet, a
   `stream_bend`, two rotated straights into a `glow_pool`.
2. Big red `toadstool_giant` in a corner; neon mushroom clusters, `dripcap`, ferns along the banks; `vh_ceiling_lip` +
   `hanging_vines` over the back wall.
3. Under every glowing prop drop its pool decal; 3-6 `glow_mist_*` over water; `stream_flow` per stream tile;
   `waterfall_sheet` + `waterfall_splash` on the fall.
4. Scatter 4-6 `glow_orb_*` (one per colour) at lift 1.1 with their pools, 3+ `fireflies_*`, and 3-5 glow frogs.
5. Keep ambient light low (night ambient) so the glow carries the room. No bloom: emissive pixels + small lights + pools.

## Drop-in steps (for the lead)
1. Enemies: paste `verdant_actors` rows into the Vanaheim area atlas or port the draw functions from
   `src/vh_enemies.py` into `tools/sprite/roles_enemies.py` (they use the same `ell` / `rect` / `shader` helpers).
2. Bosses: the `boss_*.png/.json` files are drop-in `boss_sheet` output (one frame size per sheet).
3. gamefx: merge `verdant_fx` / `verdant_critters` into the area's gamefx atlases (cell 48 / 24) or copy functions
   from `src/vh_fx.py` into `tools/portal/portal.py`.
4. Kit: copy `src/kit_verdant_heart.py` to `tools/kit/` and add the import line from its docstring.
5. Regenerate: `python3 src/gen_verdant_heart.py` (needs /workspace/hd2d-suite; writes only into this folder).
"""


if __name__ == "__main__":
    main()
