"""Jotunheim pack generator (Hearthmoor Art seat). Run: python3 gen_jotunheim.py  (writes ../, repo read-only; Pillow + numpy).
Order: character sheets (check-sprite once per sheet) -> Flurry -> gamefx -> kit .glb -> renders / scenes (+luma) -> metadata -> contact sheet -> README."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import jt_common as C
import gen_sheets as GS, flurry_gen as FG, jt_fx as X, kit_jotun as KJ, jt_scene as SC, jt_layouts as LY, jt_npcs as N
from PIL import Image
H = C.H
OUT = HERE.parent

KIT_META = {
 "snow_floor": {"placement": "2 m grid, ground of Stonehollow", "fx": ["ice_sparkles"]},
 "ice_lake": {"placement": "frozen lake [8,-3]; glow pools under the ice", "fx": ["pool_teal", "ice_sparkles"]},
 "stone_ledge": {"placement": "1.34 m plateau / ledge; chain along x. Props sit >= 1.5 m back from the front edge", "fx": ["pool_cold"], "height_m": 1.34},
 "stone_stair": {"placement": "one per ledge, centred on it; top flush with the ledge front face; stairs climb toward -z", "height_m": 1.2},
 "snow_mound": {"placement": "1.3 m mound; stand actors and props on the flat only, never on the slope", "height_m": 1.3},
 "longhouse": {"placement": "back row; door faces +z; keep 2.5 m in front of the door clear", "fx": ["pool_cold", "ice_sparkles"]},
 "rune_standing_stone": {"placement": "Welcome Ring / lake edge / plateau; rune_pulse decal under it", "fx": ["pool_cold", "rune_pulse"]},
 "lift_stone": {"placement": "the three Welcome Ring stones at [0,4]", "fx": ["rune_pulse", "pool_cold"]},
 "cold_brazier": {"placement": "Welcome Ring corners, plateau back corners; cold_flame billboard at y 2.0 m, pool_cold under it", "fx": ["cold_flame", "pool_cold"]},
 "goat_fence": {"placement": "goat pens [-8.5,-2]; chain end to end", "fx": []},
 "giant_stool": {"placement": "longhouses and the Hall; the player can climb it", "fx": []},
 "glow_orb_chain": {"placement": "hang from roof beams in jt_hall at y 3 m", "fx": ["glow_orb_blue"]},
 "fur_stall": {"placement": "Grimsa's trader stall [-6,5.5]", "fx": ["pool_cold"]},
 "warm_lantern": {"placement": "warm accent every 6-8 m so grades never go all blue", "fx": []},
 "ice_floor": {"placement": "2 m grid, Rime Caves", "fx": ["ice_sparkles"]},
 "ice_wall": {"placement": "2 m modules; icicle glow tips", "fx": ["pool_teal"]},
 "glow_ice_pool": {"placement": "5 in the Rime Caves; keep 0.5 m clear of the rim", "fx": ["pool_teal", "glow_fog", "ice_sparkles"]},
 "icicle_cluster": {"placement": "hang from the cave ceiling (y 3.2 m)", "fx": ["glow_vines"]},
 "ice_crystal_cluster": {"placement": "cave corners and pool edges", "fx": ["pool_teal", "neon_fireflies_green"]},
 "frost_rune_pillar": {"placement": "every cave pillar", "fx": ["pool_cold", "rune_pulse"]},
 "barrow_floor": {"placement": "2 m grid, Titan's Barrow", "fx": []},
 "barrow_wall": {"placement": "2 m modules", "fx": ["pool_cold"]},
 "barrow_door": {"placement": "Barrow mouth [0,-7.5] (6 m, three rune locks); keep 3 m clear", "fx": ["pool_cold"]},
 "shield_rack": {"placement": "B2 Hall of Shields, against the wall", "fx": ["pool_cold"]},
 "ice_throne": {"placement": "B9 Throne Barrow, back centre; boss_stand marker; Hrimgard stands in front (z +2.4)", "fx": ["pool_cold"]},
 "rune_bridge": {"placement": "B7 Rune Bridge: chain along z; lit planks safe, unlit crack", "fx": ["pool_cold"]},
 "rune_brazier": {"placement": "B2 / B4 / B7 braziers tb_b1..3 (snuffable)", "fx": ["cold_flame", "pool_cold"]},
}
FX_ORDER = list(X.FX)
SCENE_NAMES = {"stonehollow": "scene_stonehollow", "rimecaves": "scene_rimecaves", "barrow": "scene_titans_barrow"}


def patch_frames():
    orig = SC.frame

    def frame2(sheet, role, facing, anim, i, folder="sprite"):
        if sheet == "HERO":
            return H.SP.frame(H.PAL, role, facing, anim, i).image(), (10, 31)
        if sheet == "FLURRY":
            m = json.loads((OUT / "pets/flurry.json").read_text())
            return H.frame_of(OUT / "pets/flurry_neon.png", m, role, facing, anim, i), (10, 31)
        return orig(sheet, role, facing, anim, i, folder)
    SC.frame = frame2


def strip(sheet, role, picks, folder="sprite", hero=True):
    m = json.loads((OUT / folder / f"{sheet}.json").read_text())
    fw, fh = m["frame"]
    h = H.SP.frame(H.PAL, "wildcaller", "down", "idle", 0).image()
    row = Image.new("RGBA", (24 + fw * len(picks), fh), (0, 0, 0, 0))
    if hero:
        row.alpha_composite(h, (0, fh - 32))
    for c, (f, a, i) in enumerate(picks):
        row.alpha_composite(H.frame_of(OUT / folder / f"{sheet}.png", m, role, f, a, i), (24 + c * fw, 0))
    return row


def main():
    reps = GS.main()
    FG.main()
    reps["flurry (safe)"] = H.check_sprite(OUT / "pets/flurry.png")
    print("flurry", H.report_line(reps["flurry (safe)"]))
    H.write_json(OUT / "check_sprite_report.json", reps)
    fxm = H.write_fx(OUT / "gamefx", "jt_fx", X.FX, 48)
    built, _ = H.build_kit(OUT / "kit", KJ.pieces, KIT_META)
    rd = OUT / "renders"; rd.mkdir(exist_ok=True)
    for n, pc in built.items():
        H.render_mesh(pc.mesh, "night", SC.lights_of(pc), pad=6, ambient=SC.NIGHT_AMB)[0].save(rd / f"{n}_night.png")
    patch_frames()
    lumas, scenes = {}, {}
    for key, fn in (("stonehollow", LY.stonehollow), ("rimecaves", LY.rimecaves), ("barrow", LY.barrow)):
        S = fn(); S["fxm"] = fxm
        modes = ("night", "day") if key == "stonehollow" else ("night",)
        for mode in modes:
            im = SC.compose(built, S, mode)
            im.save(rd / f"{SCENE_NAMES[key]}_{mode}.png")
            lumas[f"{key}_{mode}"] = round(SC.luma(im), 1)
            scenes[f"{key}_{mode}"] = im
        S2 = {k: v for k, v in S.items() if k not in ("fxm",)}
        scenes[key + "_layout"] = S2
    print("luma", lumas)
    meta = metadata(reps, lumas, built)
    (OUT / "metadata").mkdir(exist_ok=True)
    contact(scenes, reps, built, fxm, lumas)
    H.write_json(OUT / "metadata/jotunheim.json", meta)
    write_readme(reps, lumas)
    return reps, lumas


def metadata(reps, lumas, built):
    sheets = {}
    for n in ("jt_giants", "ulfar", "jt_enemies", "jt_elites", "boss_hrimgard"):
        m = json.loads((OUT / "sprite" / f"{n}.json").read_text())
        sheets[n] = {"frame": m["frame"], "pivot": m["pivot"], "ground_row": m["ground_row"],
                     "roles": {r: {"scale": v["scale"], "combat_scale": v.get("combat_scale"), "anims": v["anims"], "tier": (v.get("stats_hint") or {}).get("tier")} for r, v in m["roles"].items()}}
    areas = {
        "jotunheim": {"name": "Stonehollow", "size_m": [24, 22], "real_height": "Jarl's plateau 1.34 m (2 x stone_ledge) + stone_stair 1.2 m rise / 6 steps; east ledge 1.34 m; snow_mound 1.3 m",
                      "spawns": {"from_bifrost": [0, 9.2, "up"], "clear_radius_m": 1.5},
                      "pieces": [{"piece": p[0], "pos": list(p[1])} for p in LY.stonehollow()["pieces"] if p[0] != "snow_floor"]},
        "rimecaves": {"name": "The Rime Caves", "size_m": [20, 16], "real_height": "rune-hall ledge 1.34 m + stone_stair; snow_mound 1.3 m",
                      "pieces": [{"piece": p[0], "pos": list(p[1])} for p in LY.rimecaves()["pieces"] if p[0] != "ice_floor"]},
        "barrow": {"name": "The Titan's Barrow (B9 + B2)", "real_height": "ledge 1.34 m + stone_stair; rune_bridge planks",
                   "pieces": [{"piece": p[0], "pos": list(p[1])} for p in LY.barrow()["pieces"] if p[0] != "barrow_floor"]},
    }
    notes = {
        "height": "every area has real height: ledges / mounds >= 1.2 m and a stair (6 steps, 0.2 m rise, 0.5 m run, 2 m wide)",
        "lighting": "day luma 55-70, night 20-30 with glow pools; night ambient is lifted grey-blue (0.20-0.27) so pools and warm lamps carry the colour, never an all-dark-blue grade",
        "keep_clear": ["no props, fx decals or spawns on a stair footprint plus 1 m at each end", "ledge edges: keep props >= 1.5 m behind the front edge (piece marker ledge_edge, no_props_within_m 0.8 for fx)",
                       "spawn from_bifrost [0,9.2]: nothing within 1.5 m", "longhouse doors: 2.5 m clear in front", "Barrow door: 3 m clear"],
    }
    return {"pack": "jotunheim", "story": "story/jotunheim.md", "frame_convention": "boss_sheet layout (native big frames, pivot bottom centre, idle 0-3 walk 4-7 cast 8-11 attack 12-15 die 24-27)",
            "sheets": sheets, "pet": {"flurry": "pets/flurry.json (pets layout 20x32, pivot [10,32], idle 0-3 walk 4-7 follow 8-11)"},
            "areas": areas, "placement_notes": notes, "luma_measured_on_renders": lumas,
            "neon": {"sprites": ["pets/flurry_neon.png"], "fx": "all gamefx/jt_fx", "kit": "glow material (cold fire, runes, crystal tips, pools, orbs)"},
            "check_sprite": {k: v["summary"] for k, v in reps.items()}, "kit_pieces": len(json.loads((OUT / "kit/kit.json").read_text())["pieces"])}


def contact(scenes, reps, built, fxm, lumas):
    S = H.Sheet("Jotunheim - Stonehollow, Rime Caves, Titan's Barrow (Hrimgard the Unthawed)",
                "giants 2-3.2x (real tunics, belts, boots), Ulfar, Flurry, trolls + golems, Hrimgard 7x (only plate); kit with real height; neon on glow only")
    S.section("Scenes (night + day)", "luma: " + ", ".join(f"{k} {v}" for k, v in lumas.items()))
    for k in ("stonehollow_night", "stonehollow_day", "rimecaves_night", "barrow_night"):
        S.cell(scenes[k], k, "", k=2)
    S.section("Town giants (hero for scale): down idle | down walk | left walk | up idle | right idle", H.report_line(reps["jt_giants"]))
    for role in N.NPCS:
        S.cell(strip("jt_giants", role, [("down", "idle", 0), ("down", "walk", 1), ("left", "walk", 1), ("up", "idle", 0), ("right", "idle", 0)]), role,
               N.NPCS[role]["desc"][:92], k=2)
    S.section("Ulfar Mossback (companion, 3x town / 2.4x combat): idle, walk, cast (shield hug), attack (boulder toss)", H.report_line(reps["ulfar"]))
    S.cell(strip("ulfar", "ulfar", [("down", "idle", 0), ("down", "walk", 1), ("left", "walk", 2), ("down", "cast", 2), ("down", "attack", 1), ("down", "attack", 2), ("left", "attack", 2), ("up", "idle", 0)]), "ulfar", "", k=2)
    S.section("Flurry the snow hare (pet)", "flurry_neon.png primary; flurry.png palette-safe twin (passes); idle 0-3 | walk 4-7 | follow 8-11")
    for n in ("flurry_neon.png", "flurry.png"):
        S.cell(Image.open(OUT / "pets" / n), "pets/" + n, "", k=3)
    S.section("Enemies (frost troll 1.6x, ice golem 1.5x, avalanche golem 1.8x, rime berserker 1.8x)", H.report_line(reps["jt_enemies"]))
    for role in ("frost_troll", "ice_golem", "avalanche_golem", "rime_berserker"):
        S.cell(strip("jt_enemies", role, [("down", "idle", 0), ("down", "walk", 1), ("left", "walk", 2), ("down", "attack", 1), ("down", "attack", 2), ("left", "attack", 2), ("down", "die", 1), ("down", "die", 2), ("down", "die", 3)]), role, "", k=2)
    S.section("Rares + mini-boss (frostmother 2.5x, avalanche 3x, Ormgar 3x)", H.report_line(reps["jt_elites"]))
    for role in ("frostmother", "avalanche", "ormgar"):
        S.cell(strip("jt_elites", role, [("down", "idle", 0), ("down", "walk", 1), ("down", "attack", 1), ("down", "attack", 2), ("left", "attack", 2), ("down", "die", 1), ("down", "die", 2), ("down", "die", 3)]), role, "", k=1)
    S.section("Hrimgard the Unthawed (boss 7x; ONLY plate): phase 1-2 and phase 3 (cold fire off his shoulders)", H.report_line(reps["boss_hrimgard"]))
    for role in ("hrimgard", "hrimgard_p3"):
        S.cell(strip("boss_hrimgard", role, [("down", "idle", 0), ("left", "walk", 1), ("down", "attack", 2), ("up", "idle", 0), ("down", "die", 1), ("down", "die", 2), ("down", "die", 3)]), role, "", k=1)
    S.section("Kit night renders (1 px = 1/18 m)", "")
    for n in built:
        S.cell(Image.open(OUT / f"renders/{n}_night.png"), n, "", k=2 if built[n].size[1] > 4 else 3)
    S.section("gamefx (48 px, neon)", "")
    for n in FX_ORDER:
        e = fxm["effects"][n]
        st = Image.new("RGBA", (48 * e["frames"], 48), (12, 14, 26, 255))
        for i in range(e["frames"]):
            st.alpha_composite(SC.fxf(fxm, n, i), (i * 48, 0))
        S.cell(st, n, "", k=2)
    S.render(OUT / "contact_sheet.png")


def write_readme(reps, lumas):
    body = (HERE / "README_body.md").read_text()
    body = body.replace("{{LUMA}}", ", ".join(f"{k} {v}" for k, v in lumas.items()))
    fails = {k: v["summary"]["failures"] for k, v in reps.items()}
    body = body.replace("{{CHECKS}}", "; ".join(f"{k} {'PASS' if not f else 'FAIL ' + str(f)}" for k, f in fails.items()))
    (OUT / "README.md").write_text(body)


if __name__ == "__main__":
    main()
