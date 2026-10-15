"""Svartalfheim pack generator (Hearthmoor Art seat). Run: python3 gen_svartalfheim.py  (writes ../, repo read-only)."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[1] / "_lib"))
import sv_common as C  # noqa
H = C.H
import sv_actors as A, sv_big as BG, sv_boss as BS, kit_svart as KS, tick_gen as TG  # noqa
import math, random
from PIL import Image
OUT = HERE.parent
A4 = ("idle", "walk", "attack", "die")

BIGS = {
 "boss_gorrak": {"gorrak": {"draw": BS.gorrak, "frame": (BS.W, BS.HH), "scale": 6.0, "anims": A4,
    "desc": "Gorrak Ironmaw, the Bound Forge-Tyrant (boss, 6x; the ONLY plate-wearer): fire-demon bound in riveted black plate, horned maw helm, wrist chains, cold-blue rune seams, forge fire through the gaps. Phase 1 (chained).",
    "light": {"color": "#e0302a", "intensity": 1.0, "range": 7.0}, "stats_hint": {"tier": "boss", "height_x_player": 6.0, "dungeon": "Clockwork Deep"}},
   "gorrak_unbuckled": {"draw": BS.gorrak_unbuckled, "frame": (BS.W, BS.HH), "scale": 6.0, "anims": A4,
    "desc": "Gorrak Ironmaw phases 2-3: chains torn loose, plates opened, fire roaring through; die = kneels, white-hot heart-ember.",
    "light": {"color": "#ff5a4a", "intensity": 1.2, "range": 8.0}}},
 "miniboss_foreman": {"foreman": {"draw": BG.foreman, "frame": (BG.FW_, BG.FH_), "scale": 2.8, "anims": A4,
    "desc": "The Foreman (Clockwork Deep C4 mini-boss, 2.8x): brass-and-iron overseer construct with chain flail.", "stats_hint": {"tier": "miniboss"}}},
 "rare_basilisk": {"basilisk": {"draw": BG.basilisk, "frame": (BG.BW_, BG.BH_), "scale": 2.5, "anims": A4,
    "desc": "Amethyst Basilisk (rare, 2.5x): crystal-spined cave lizard of the Amethyst Mines.", "stats_hint": {"tier": "rare"}}},
 "rare_sootcolossus": {"sootcolossus": {"draw": BG.sootcolossus, "frame": (BG.SW_, BG.SH_), "scale": 2.8, "anims": A4,
    "desc": "Soot Colossus (rare, 2.8x): soot elemental over a cracked forge grate.", "stats_hint": {"tier": "rare"}}},
 "runaway_construct": {"runaway": {"draw": BG.runaway, "frame": (BG.RW_, BG.RH_), "scale": 2.0, "anims": A4,
    "desc": "Runaway construct (Bifrost gate foe, 2x): a rogue clockwork worker.", "stats_hint": {"tier": "gate"}}},
}

CELL = 48


def fireflies(cols, seed, n=7):
    def f():
        r = random.Random(seed); pts = [(r.uniform(6, 42), r.uniform(6, 42), r.uniform(0, 6.28)) for _ in range(n)]
        out = []
        for k in range(8):
            F = H.Fx(CELL)
            for j, (x, y, ph) in enumerate(pts):
                a = k / 8 * math.tau + ph
                X, Y = x + math.cos(a) * 3, y + math.sin(a * 2) * 2
                if (k + j) % 3:
                    F.set(X, Y, cols[0]); F.set(X + 1, Y, cols[1]); F.set(X, Y + 1, cols[2])
                else:
                    F.set(X, Y, cols[2])
            out.append(F)
        return out
    return f


def water_glow():
    return H.pool_frames(("sv_water_hi", "sv_water", "sv_water_lo"), CELL, 6, "svwater", rmax=22)


def embers():
    r = random.Random(9); pts = [(r.uniform(14, 34), r.uniform(0, 47)) for _ in range(8)]
    out = []
    for k in range(8):
        F = H.Fx(CELL)
        for j, (x, y0) in enumerate(pts):
            y = 46 - ((46 - y0) + k * 5) % 46
            F.set(x + math.sin(y * 0.3 + j), y, "neon_red_hi" if y > 30 else "sv_ember" if j % 2 else "neon_red")
        out.append(F)
    return out


NBL = ("neon_blue_hi", "neon_blue", "neon_blue_lo")
FX = {
    "pool_blue": {"fn": lambda: H.neon_pool_frames("blue", CELL, 6, rmax=20), "fps": 4, "kind": "decal", "lift": 0.02, "pivot": [24, 24], "notes": "under rune_lamp / deep_wall runes / anvil_pillar"},
    "pool_violet": {"fn": lambda: H.neon_pool_frames("violet", CELL, 6, rmax=22), "fps": 4, "kind": "decal", "lift": 0.02, "pivot": [24, 24], "notes": "under crystal_cluster / mine_cart"},
    "pool_red": {"fn": lambda: H.neon_pool_frames("red", CELL, 6, rmax=20), "fps": 5, "kind": "decal", "lift": 0.02, "pivot": [24, 24], "notes": "under forge_brazier; under Gorrak (x3)"},
    "water_glow": {"fn": water_glow, "fps": 4, "kind": "decal", "lift": 0.03, "pivot": [24, 24], "notes": "glowing underground water shimmer over glow_pool"},
    "neon_fireflies_blue": {"fn": fireflies(NBL, 3), "fps": 6, "kind": "billboard", "lift": 0.8, "pivot": [24, 47], "notes": "cold-blue fireflies (Bill)"},
    "neon_fireflies_violet": {"fn": fireflies(("neon_violet_hi", "neon_violet", "neon_violet_lo"), 4), "fps": 6, "kind": "billboard", "lift": 0.8, "pivot": [24, 47], "notes": "violet fireflies in the mines"},
    "forge_embers": {"fn": embers, "fps": 8, "kind": "billboard", "lift": 0.6, "pivot": [24, 47], "notes": "over forge_brazier and Gorrak's plate gaps"},
}
for _c in ("blue", "violet", "red"):
    FX[f"glow_orb_{_c}"] = {"fn": (lambda c=_c: H.glow_orb_frames(c, CELL)), "fps": 6, "kind": "billboard", "lift": 1.4, "pivot": [24, 33],
                            "light": {"color": f"neon_{_c}_hi", "intensity": 0.7, "range": 3.0, "pool": f"pool_{_c}"}, "notes": "floating glow orb, hover 1.1-2.2 m"}

KIT_META = {"deep_floor": {"placement": "2 m grid"}, "deep_wall": {"fx": ["pool_blue"], "placement": "2 m modules"},
            "rail_straight": {"placement": "chain end to end along z"}, "mine_cart": {"fx": ["pool_violet"], "placement": "on rails"},
            "gear_wall": {"fx": ["pool_blue"], "placement": "Clockwork Deep walls"}, "crystal_cluster": {"fx": ["pool_violet", "neon_fireflies_violet"], "placement": "Amethyst Mines"},
            "rune_lamp": {"fx": ["pool_blue", "neon_fireflies_blue"], "placement": "every 5-6 m"}, "forge_brazier": {"fx": ["pool_red", "forge_embers"], "placement": "forges, boss room"},
            "glow_pool": {"fx": ["water_glow"], "placement": "cave floors"}, "anvil_pillar": {"fx": ["pool_blue", "forge_embers"], "placement": "boss room centre back; boss_stand marker"}}


def lights_of(pc, pos=(0, 0, 0)):
    lc = pc.markers.get("lamp_color")
    return [((pos[0] + lp[0], lp[1], pos[2] + lp[2]), lc, pc.markers["lamp_range"], 1.0) for lp in pc.markers.get("lamps", [])] if lc else []


def fxf(fxm, n, i=0):
    return H.fx_frame(OUT / "gamefx/svart_fx.png", fxm, n, i)


def frame(sheet, role, facing, anim, i):
    m = json.loads((OUT / f"sprite/{sheet}.json").read_text())
    return H.frame_of(OUT / f"sprite/{sheet}.png", m, role, facing, anim, i)


def scene(built, fxm):
    import importlib; G = importlib.import_module("gen_alfheim_decal")
    K = H.kit_module(); M = K.Mesh(); lights = []
    def put(n, pos):
        pc = built[n]; M.add(pc.mesh.xf(pos)); lights.extend(lights_of(pc, pos))
    for i in range(9):
        for j in range(5):
            put("deep_floor", (-8 + i * 2, 0, -3 + j * 2))
    for i in range(9):
        put("gear_wall" if i in (2, 6) else "deep_wall", (-8 + i * 2, 0, -4.3))
    put("anvil_pillar", (3.0, 0, -2.8))
    for z in (-3, -1, 1, 3, 5):
        put("rail_straight", (-6.0, 0, z))
    put("mine_cart", (-6.0, 0, 1.6))
    put("crystal_cluster", (-8.0, 0, -2.4)); put("crystal_cluster", (-3.6, 0, 4.6)); put("crystal_cluster", (8.4, 0, 3.8))
    put("rune_lamp", (-1.6, 0, -2.6)); put("rune_lamp", (7.6, 0, -2.6))
    put("forge_brazier", (0.4, 0, 0.8)); put("forge_brazier", (6.0, 0, 0.8))
    put("glow_pool", (-2.4, 0, 2.6))
    M.quad((-0.02, 11.5, -4.6), (0.02, 11.5, -4.6), (0.02, 11.55, -4.6), (-0.02, 11.55, -4.6), "#0a0a16", mat="glow")
    orbs = [("blue", (-4.4, 2.4, -1.6)), ("violet", (-7.0, 1.8, 3.0)), ("red", (6.8, 2.6, -1.0)), ("blue", (1.0, 2.2, 3.6)), ("violet", (8.0, 1.6, 1.6))]
    for c, p in orbs:
        lights.append((p, H.ALLC[f"neon_{c}"], 2.6, 0.7))
    boss = (3.0, 0, -0.6)
    lights.append(((boss[0], 1.5, boss[2] + 0.8), H.ALLC["neon_red"], 6.0, 0.9))
    im, org, zb = H.render_mesh(M, "night", lights, pad=12, depth=True)
    can = Image.new("RGBA", im.size, (10, 10, 20, 255)); can.alpha_composite(im)
    dec = [("water_glow", (-2.4, 0, 2.6), 1), ("pool_violet", (-8.0, 0, -1.8), 0), ("pool_violet", (-3.6, 0, 5.0), 2), ("pool_violet", (8.4, 0, 4.2), 3),
           ("pool_violet", (-6.0, 0, 1.6), 4), ("pool_blue", (-1.6, 0, -2.2), 1), ("pool_blue", (7.6, 0, -2.2), 2), ("pool_red", (0.4, 0, 1.0), 0), ("pool_red", (6.0, 0, 1.0), 3)]
    for n, c, i in dec:
        G.decal_over(can, fxf(fxm, n, i), c, org, zb)
    aura = fxf(fxm, "pool_red", 2); aura = aura.resize((aura.width * 3, aura.height * 3), Image.NEAREST)
    G.decal_over(can, aura, boss, org, zb, 0.03)
    for k, (c, p) in enumerate(orbs):
        G.decal_over(can, fxf(fxm, f"pool_{c}", k), (p[0], 0, p[2]), org, zb)
    hero = H.SP.frame(H.PAL, "wildcaller", "up", "idle", 0).image()
    tick = Image.open(OUT / "tick/tick_neon.png").crop((0, 32, 20, 64))   # up idle0
    items = [(frame("boss_gorrak", "gorrak", "down", "attack", 1), boss, (72, 191)), (hero, (0.2, 0, 4.6), (10, 31)),
             (frame("dagna", "dagna", "up", "idle", 0), (-1.0, 0, 4.2), (10, 31)), (tick, (0.9, 0.9, 4.4), (10, 31)),
             (frame("deep_enemies", "forgeconstruct", "down", "idle", 1), (5.0, 0, 2.6), (10, 31)),
             (frame("deep_enemies", "sootling", "left", "idle", 2), (6.8, 0, 3.4), (10, 31)),
             (frame("svart_npcs", "minerunner", "right", "walk", 1), (-5.0, 0, 3.4), (10, 31)),
             (frame("svart_npcs", "runewarden", "down", "idle", 0), (-1.0, 0, -1.8), (10, 31)),
             (fxf(fxm, "forge_embers", 2), (0.4, 0.9, 0.8), (24, 47)), (fxf(fxm, "forge_embers", 5), (6.0, 0.9, 0.8), (24, 47)),
             (fxf(fxm, "neon_fireflies_blue", 1), (-2.4, 0.6, 2.4), (24, 47)), (fxf(fxm, "neon_fireflies_violet", 3), (-7.4, 0.4, -1.4), (24, 47)),
             (fxf(fxm, "neon_fireflies_violet", 6), (7.6, 0.4, 4.4), (24, 47)), (fxf(fxm, "neon_fireflies_blue", 4), (-3.8, 1.2, -1.0), (24, 47))]
    for k, (c, p) in enumerate(orbs):
        items.append((fxf(fxm, f"glow_orb_{c}", k), p, (24, 33)))
    for (fr, a, pv) in sorted(items, key=lambda r: r[1][2]):
        H.billboard_over(can, fr, a, org, zb, pv)
    return can


def dagna_neon():
    """Dagna neon twin: her ember hammer-head / cast sparks (lamp, flower_gold pixels) in neon red. Primary is dagna.png (passes)."""
    im = Image.open(OUT / "sprite/dagna.png").convert("RGBA"); px = im.load()
    rgb = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
    m = {rgb(H.ALLC["lamp"]): rgb(H.ALLC["neon_red_hi"]), rgb(H.ALLC["flower_gold"]): rgb(H.ALLC["neon_red"])}
    for y in range(im.height):
        for x in range(im.width):
            c = px[x, y]
            if c[3] and c[:3] in m:
                px[x, y] = m[c[:3]] + (255,)
    im.save(OUT / "sprite/dagna_neon.png")


def sheet_rows(sheet, roles, anims, k=3):
    meta = json.loads((OUT / f"sprite/{sheet}.json").read_text()); png = OUT / f"sprite/{sheet}.png"
    out = []
    for role in roles:
        seq = [(a, i) for a in anims if a in meta["roles"][role]["anims"] for i in range(4)]
        row = Image.new("RGBA", ((H.FW + 4) * len(seq) + 4, (H.FH + 4) * 4 + 4), (0, 0, 0, 0))
        for fi, facing in enumerate(H.FACINGS):
            for c, (an, i) in enumerate(seq):
                row.alpha_composite(H.frame_of(png, meta, role, facing, an, i), (c * (H.FW + 4) + 2, fi * (H.FH + 4) + 2))
        out.append((role, row))
    return out


def contact(sc, reps, built):
    S = H.Sheet("Svartalfheim - Anvildeep, Amethyst Mines, Clockwork Deep (Gorrak Ironmaw)",
                "20x32 townsfolk / enemies, Dagna + Tick, rares 2.5-2.8x, construct 2x, Gorrak 6x; kit + gamefx; neon only on glow")
    S.section("Clockwork Deep / Amethyst Mines at night", "Gorrak (6x) at the anvil-pillar; rails + crystal cart, gear walls, rune lamps, braziers, glowing water; orbs, fireflies; hero, Dagna, Tick")
    S.cell(sc.crop(sc.getbbox()), "renders/scene_clockwork_deep_night.png", "", k=2 if sc.width * 2 <= 1360 else 1)
    S.section("Townsfolk (20x32): idle | walk, 4 facings", "dwarves + dark elves, real clothes; " + H.report_line(reps["svart_npcs"]))
    for role, row in sheet_rows("svart_npcs", A.NPCS, ("idle", "walk")):
        S.cell(row, role, A.NPCS[role]["desc"][:100], k=2)
    S.section("Dagna (companion) + Tick (pet)", "dagna.png passes (palette); dagna_neon.png = neon-red ember twin; tick_neon.png primary, tick.png palette-safe (passes)")
    for role, row in sheet_rows("dagna", A.DAGNA, ("idle", "walk", "cast", "attack")):
        S.cell(row, role, "", k=2)
    for n in ("tick_neon.png", "tick.png"):
        S.cell(Image.open(OUT / "tick" / n), "tick/" + n, "idle 0-3 | walk 4-7 | follow 8-11", k=3)
    S.section("Clockwork Deep enemies (20x32)", H.report_line(reps["deep_enemies"]))
    for role, row in sheet_rows("deep_enemies", A.ENEMIES, A4):
        S.cell(row, role, A.ENEMIES[role]["desc"][:100], k=2)
    S.section("Big ones (down: idle0, walk1, attack1-3, die3) with hero for scale", "runaway 2x, basilisk 2.5x, foreman / colossus 2.8x, Gorrak 6x (ONLY plate)")
    hero = H.SP.frame(H.PAL, "wildcaller", "down", "idle", 0).image()
    for n, roles in BIGS.items():
        for role, r in roles.items():
            fw, fh = r["frame"]
            sel = [("idle", 0), ("walk", 1), ("attack", 1), ("attack", 2), ("attack", 3), ("die", 3)]
            row = Image.new("RGBA", (24 + fw * len(sel), fh), (0, 0, 0, 0)); row.alpha_composite(hero, (0, fh - 32))
            for c, (an, i) in enumerate(sel):
                row.alpha_composite(frame(n, role, "down", an, i), (24 + c * fw, 0))
            S.cell(row, f"{role} ({r['scale']}x)", H.report_line(reps[n]), k=1 if fw > 100 else 2)
    S.section("Kit night renders", "")
    for n, pc in built.items():
        S.cell(Image.open(OUT / f"renders/{n}_night.png"), n, "", k=3)
    S.section("gamefx (48 px)", "neon")
    fxm = json.loads((OUT / "gamefx/svart_fx.json").read_text())
    for n in FX:
        e = fxm["effects"][n]
        st = Image.new("RGBA", (CELL * e["frames"], CELL), (12, 14, 26, 255))
        for i in range(e["frames"]):
            st.alpha_composite(fxf(fxm, n, i), (i * CELL, 0))
        S.cell(st, n, "", k=2)
    S.render(OUT / "contact_sheet.png")


def main():
    reps = {}
    reps["svart_npcs"] = H.write_actors(OUT / "sprite", "svart_npcs", A.NPCS)
    reps["dagna"] = H.write_actors(OUT / "sprite", "dagna", A.DAGNA)
    reps["deep_enemies"] = H.write_actors(OUT / "sprite", "deep_enemies", A.ENEMIES)
    for n, roles in BIGS.items():
        reps[n] = H.write_boss(OUT / "sprite", n, roles)
    dagna_neon()
    TG.main()
    reps["tick (safe)"] = H.check_sprite(OUT / "tick/tick.png")
    for k, r in reps.items(): print(k, H.report_line(r))
    H.write_json(OUT / "check_sprite_report.json", reps)
    fxm = H.write_fx(OUT / "gamefx", "svart_fx", FX, CELL)
    built, _ = H.build_kit(OUT / "kit", KS.pieces, KIT_META)
    rd = OUT / "renders"; rd.mkdir(exist_ok=True)
    for n, pc in built.items():
        H.render_mesh(pc.mesh, "night", lights_of(pc), pad=6)[0].save(rd / f"{n}_night.png")
    sc = scene(built, fxm); sc.save(rd / "scene_clockwork_deep_night.png")
    contact(sc, reps, built)
    H.finish_pack(OUT, (HERE / "README_body.md").read_text())


if __name__ == "__main__":
    main()
