"""Niflheim pack generator (Hearthmoor Art seat). Run: python3 gen_niflheim.py  (writes ../, repo read-only; Pillow + numpy).
Order: character sheets (check-sprite once per sheet) -> gamefx -> kit .glb -> renders / scenes (+luma) -> metadata -> contact sheet -> README.
NF_SKIP_SHEETS=1 reuses the stored sheets + check_sprite_report.json (the default when the report exists; NF_RESHEETS=1 forces a re-render).
NF_SCENES=a,b renders only those scenes (lumas merge into renders/luma.json); NF_NO_CONTACT=1 skips contact sheet + README (quick tuning loop)."""
import json, os, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import nf_common as C
import gen_sheets as GS, nf_fx as X, kit_nif as KJ, nf_scene as SC, nf_layouts as LY, nf_npcs as N, nf_foes as F, nf_boss as B
from PIL import Image
H = C.H
OUT = HERE.parent

KIT = {
 "snow_floor": ("2 m grid ground of Mistmere / nf_home (reused from Jotunheim)", ["mist_drift", "ice_sparkles"]),
 "ice_lake": ("4 x 4 m frozen lake / shore water (two side by side = Mistmere lake); glowing cracks", ["pool_teal", "ice_sparkles"]),
 "ice_floor": ("2 m grid ground of the Glowpool Caverns and the Frozen Spire rooms", ["glow_fog", "ice_sparkles"]),
 "ice_wall": ("2 m ice wall module (caves and Spire rooms)", ["pool_cold"]),
 "glow_ice_pool": ("bioluminescent pool (iceglow has five; Spire F3); never closer than 2 m to a stair", ["pool_teal", "glow_fog"]),
 "icicle_cluster": ("hanging icicles with glow tips; hang at y 3.2 m", ["glow_crystals_blue"]),
 "ice_crystal_cluster": ("standing crystal cluster; corners and Glacier Heart", ["glow_crystals_blue", "ice_sparkles"]),
 "frost_rune_pillar": ("rune pillar (every cave pillar); the hidden spring hides behind one", ["pool_cold", "rune_pulse"]),
 "spire_mouth_door": ("iceglow Spire mouth [0,-7.5]: 6 m ice door, 3 rune locks; keep 3 m clear (reused Jotunheim barrow door)", ["pool_cold", "rune_pulse"]),
 "rime_bridge": ("F8 Rime Bridge: chain along z; step only on lit runes (every second plank is lit)", ["pool_cold"]),
 "kael_perch": ("F9 Kael's aerie: boss_stand marker z +3.4 (Kael 5.5x); keep the front 4 m clear (reused Jotunheim ice throne)", ["pool_cold"]),
 "nf_waystone": ("Niflheim waystone: Quiet Shore path, Spire F7 safe room; 2.6 m clear", ["pool_cold", "rune_pulse"]),
 "nf_cairn": ("trail marker on paths; 1.2 m clear", []),
 "glow_orb_chain": ("hanging glow-orb chain (y 3 m); steady light", ["glow_orb_blue"]),
 "cold_brazier": ("cold-fire brazier; cold_flame at y 1.9 m + pool_cold", ["cold_flame", "pool_cold"]),
 "warm_lantern": ("warm accent every 6-8 m so the grade is never all blue", ["pool_warm"]),
 "snow_mound": ("1.3 m snow mound, dressing; keep off paths", []),
 "frost_ledge": ("1.34 m ledge / terrace (pairs along x, 3.1 x 2.1 m each); props >= 1.5 m behind the front edge", ["pool_cold"]),
 "frost_stair": ("7 steps x 0.191 m = 1.34 m, 2 m wide, one per ledge, centred on the front face; climbs toward -z (rot pi to climb toward +z)", []),
 "mist_arch": ("Mistmere's ice arch to Bifrost [0,10.6]; arrival [0,9.2,'up']; nothing within 2.6 m", ["pool_cold", "mist_drift"]),
 "lantern_post": ("cold-fire lantern posts [-7,4] [0,5] [7,4]; lantern_float fx at the cage + pool_cold", ["lantern_float", "pool_cold"]),
 "speaker_hall": ("frost-speaker hall [0,-9.6], door faces +z; 2 m clear in front; terrace + stair in front", ["pool_warm", "pool_cold"]),
 "fish_stall": ("Tove's fish-stall [-8.5,-3.0], counter faces +z; 1.5 m clear", ["pool_warm"]),
 "elk_paddock": ("Ketil's elk paddock [9,-3]; gate gap on the -x side; the elk are runtime NPCs", []),
 "eira_grave": ("Eira's grave [0,-4] (nf_home): runes + two violet lamps; eira_outline at z +0.6; 2 m clear", ["pool_violet", "violet_flame", "eira_outline"]),
 "ashmantle_house": ("Ashmantle House [6,-3] (nf_home): hearth glow windows; interior is a scene; 1.8 m clear at the door", ["pool_warm"]),
 "shard_window": ("eh_glass shard-window (nf_home) and F6 Sister's Glass panes; violet / blue glow", ["pool_violet", "glow_crystals_violet"]),
 "spring_pool": ("hidden bubbly spring (nf_spring / ig_spring / fs_spring): clear, warm, steaming blue-teal; 2 m clear", ["spring_bubbles", "pool_teal"]),
 "rune_hall": ("iceglow rune-hall [-6,-4] (Gudrun's school), door faces +z; 2 m clear", ["pool_cold", "rune_pulse"]),
 "glow_vine": ("glowing icicle vines hang at y 3.1 m (caves, halls); glow_vines fx adds the twinkle", ["glow_vines"]),
 "spire_gate": ("F1 Spire gate (doorway frame); 2.6 m clear", ["pool_cold"]),
 "banner_hall_banner": ("F2 / F9 red banners hang at y 0.8-3.4 m on the walls (Kael's colours; burn in his phase 3)", ["banner_burn"]),
 "mirror_pane": ("F4 mirror stairs / F6 panes; stands against a wall", ["pool_violet", "pool_cold"]),
 "glacier_heart": ("F5 glacier heart: arena centre; Colossus boss_stand marker z +4.0; 3 m clear ring", ["pool_cold", "core_pulse"]),
 "archive_tablets": ("F7 aurora archive tablet row (clue points)", ["aurora_glow", "pool_aurora"]),
 "crown_stair": ("F10 crown stair: 10 steps up to the Rift; climbs toward -z; keep clear", ["rune_pulse"]),
 "frozen_portal": ("frozen portal: F8 walls, F10 door, four at the Crown of Ice (N/E/S/W, 6.2 m ring)", ["portal_freeze", "portal_thaw"]),
 "crown_platform": ("frozen_rift Crown of Ice: round 10 m platform; Veyra boss_stand [0,0.5,-3]; aurora above", ["aurora_glow", "pool_cold", "pool_violet"]),
 "spire_pillar": ("generic Spire pillar with rune strip; rhythm every 4 m along halls", ["pool_cold"]),
}
KIT_META = {k: {"placement": v[0], "fx": v[1]} for k, v in KIT.items()}
FX_ORDER = list(X.FX)
SCENES = [("niflheim", LY.niflheim, ("night", "day")), ("nf_home", LY.nf_home, ("night", "day")), ("iceglow", LY.iceglow, ("night",))] + \
         [(f"spire_f{i}", getattr(LY, f"spire_f{i}"), ("night",)) for i in range(1, 11)] + [("frozen_rift", LY.frozen_rift, ("night",))]


def patch_frames():
    orig = SC.frame

    def frame2(sheet, role, facing, anim, i, folder="sprite"):
        if sheet == "HERO":
            return H.SP.frame(H.PAL, role, facing, anim, i).image(), (10, 31)
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
    rp = OUT / "check_sprite_report.json"
    if rp.exists() and not os.environ.get("NF_RESHEETS"):
        reps = json.loads(rp.read_text())
    else:
        reps = GS.main()
    fxm = H.write_fx(OUT / "gamefx", "nf_fx", X.FX, 48)
    built, _ = H.build_kit(OUT / "kit", KJ.pieces, KIT_META)
    rd = OUT / "renders"; rd.mkdir(exist_ok=True)
    for n, pc in built.items():
        H.render_mesh(pc.mesh, "night", SC.lights_of(pc), pad=6, ambient=SC.NIGHT_AMB)[0].save(rd / f"{n}_night.png")
    patch_frames()
    only = set(filter(None, os.environ.get("NF_SCENES", "").split(",")))
    lp = rd / "luma.json"
    lumas = json.loads(lp.read_text()) if lp.exists() else {}
    scenes, layouts = {}, {}
    for key, fn, modes in SCENES:
        S = fn(); S["fxm"] = fxm
        layouts[key] = {k: v for k, v in S.items() if k != "fxm"}
        for mode in modes:
            f = rd / f"scene_{key}_{mode}.png"
            if only and key not in only:
                if f.exists():
                    scenes[f"{key}_{mode}"] = Image.open(f)
                continue
            im = SC.compose(built, S, mode)
            im.save(f)
            lumas[f"{key}_{mode}"] = round(SC.luma(im), 1)
            scenes[f"{key}_{mode}"] = im
    lp.write_text(json.dumps(lumas, indent=1))
    print("luma", lumas)
    if os.environ.get("NF_NO_CONTACT"):
        return reps, lumas
    (OUT / "metadata").mkdir(exist_ok=True)
    H.write_json(OUT / "metadata/niflheim_layout.json", layouts)
    meta = metadata(reps, lumas, built, layouts)
    contact(scenes, reps, built, fxm, lumas)
    H.write_json(OUT / "metadata/niflheim.json", meta)
    write_readme(reps, lumas)
    return reps, lumas


def metadata(reps, lumas, built, layouts):
    sheets = {}
    for n in GS.SHEETS:
        m = json.loads((OUT / "sprite" / f"{n}.json").read_text())
        sheets[n] = {"frame": m["frame"], "pivot": m["pivot"], "ground_row": m["ground_row"],
                     "roles": {r: {"scale": v["scale"], "anims": v["anims"], "tier": (v.get("stats_hint") or {}).get("tier")} for r, v in m["roles"].items()}}
    notes = {
        "height": "every area and Spire room has a 1.34 m ledge/terrace (frost_ledge pairs) and ONE frost_stair (7 steps x 0.191 m = 1.34 m, 2 m wide) on its front face: Mistmere frost-speaker terrace, nf_home shore terrace, iceglow Spire-mouth ledge, Spire F1-F10 room ledges, the Crown of Ice landing",
        "lighting": "day luma 55-70, night 20-30 with glow pools (cold blue, teal, aurora green, violet) AND warm lantern / window pools every 6-8 m; night ambient is a lifted grey-violet (0.40, 0.38, 0.46), not the all-blue default",
        "keep_clear": ["no props, fx decals or spawns on a stair footprint plus 1 m at each end", "ledge edges: props >= 1.5 m behind the front edge (marker ledge_edge, no_props_within_m 0.8 for fx)",
                       "Bifrost arch arrival [0,9.2]: nothing within 2.6 m", "speaker hall / rune hall doors 2 m, Ashmantle House door 1.8 m, Spire mouth 3 m, Eira's grave 2 m", "springs 2 m"],
        "boss_stand": {"colossus (F5)": [0, 0, 4.0], "kael (F9)": [0, 0, 3.4], "veyra (frozen_rift)": [0, 0.5, -3.0]},
    }
    return {"pack": "niflheim", "story": "story/niflheim.md", "frame_convention": "boss_sheet layout (native big frames, pivot bottom centre, idle 0-3 walk 4-7 cast 8-11 attack 12-15 die 24-27)",
            "sheets": sheets, "companion": {"hrefna": "sprite/nf_hrefna.json role hrefna (idle 0-3, walk 4-7 = follow, cast 8-11); NO pet in this realm"},
            "areas": {k: {"pieces": [{"piece": p[0], "pos": list(p[1]), **({"rot": p[2]} if len(p) > 2 else {})} for p in v["pieces"] if not p[0].endswith("_floor")]} for k, v in layouts.items()},
            "placement_notes": notes, "luma_measured_on_renders": lumas,
            "neon": {"sprites": [], "allow_list_needed": [], "fx": "all gamefx/nf_fx", "kit": "glow material"},
            "check_sprite": {k: v["summary"] for k, v in reps.items()}, "kit_pieces": len(json.loads((OUT / "kit/kit.json").read_text())["pieces"])}


def contact(scenes, reps, built, fxm, lumas):
    S = H.Sheet("Niflheim - Mistmere, Quiet Shore, Glowpool Caverns, Frozen Spire F1-F10, Crown of Ice",
                "ice-kin 1x in real tunics, belts and boots; Hrefna (companion, no pet); stalkers, spirits, golems, wraiths, wardens; Colossus 6x, Kael 5.5x, Veyra 5-6x (4 phases); kit with a 1.34 m ledge + stair in every room; neon on glow only")
    S.section("Scenes (night + day)", "luma: " + ", ".join(f"{k} {v}" for k, v in lumas.items()))
    for k in scenes:
        S.cell(scenes[k], k, "", k=1 if scenes[k].width > 700 else 2)
    S.section("Ice-kin folk (1x; hero for scale): down idle | down walk | left walk | up idle | right idle", H.report_line(reps["nf_folk"]))
    for role, r in N.NPCS.items():
        S.cell(strip("nf_folk", role, [("down", "idle", 0), ("down", "walk", 1), ("left", "walk", 1), ("up", "idle", 0), ("right", "idle", 0)]), role, r["desc"][:92], k=3)
    S.section("Hrefna Frostveil (companion; NO pet): idle | walk (= follow) | cast", H.report_line(reps["nf_hrefna"]))
    S.cell(strip("nf_hrefna", "hrefna", [("down", "idle", 0), ("down", "walk", 1), ("left", "walk", 2), ("up", "idle", 0), ("right", "idle", 0), ("down", "cast", 1), ("down", "cast", 2), ("left", "cast", 2)]), "hrefna", "", k=3)
    S.section("Enemies (frost spirit 1.2x, mist stalker 1.5x, ice golem 1.8x, frost wraith 1.4x, ice warden 1x)", H.report_line(reps["nf_enemies"]))
    for role in F.ENEM:
        S.cell(strip("nf_enemies", role, [("down", "idle", 0), ("down", "walk", 1), ("left", "walk", 2), ("down", "attack", 1), ("down", "attack", 2), ("left", "attack", 2), ("down", "die", 1), ("down", "die", 2), ("down", "die", 3)]), role, "", k=2)
    S.section("Elites + rares (Brisa 3x mini-boss, mist-alpha 2x, spirit prime 3x, Kael bat 2x)", H.report_line(reps["nf_elites"]))
    for role in F.ELITE:
        S.cell(strip("nf_elites", role, [("down", "idle", 0), ("down", "walk", 1), ("down", "attack", 1), ("down", "attack", 2), ("left", "attack", 2), ("down", "die", 1), ("down", "die", 2), ("down", "die", 3)]), role, "", k=1)
    for sh, roles_, title in (("boss_colossus", ("colossus", "colossus_p2", "colossus_p3"), "Glacier Colossus (boss 6x): P1 core in the chest, P2 core exposed, P3 runes dim"),
                              ("boss_kael", ("kael", "kael_p3"), "Kael Frostfang (boss 5.5x; plate): black iron + red-lined cape; phase 3 frosted white"),
                              ("boss_veyra", ("veyra_p1", "veyra_p2", "veyra_p3", "veyra_p4", "veyra_clone"), "Veyra Ashmantle (boss 5x / 6x P3; plate): P1 Mist, P2 Freeze, P3 Warden (6x), P4 Ask (no attack), mist clone")):
        S.section(title, H.report_line(reps[sh]))
        for role in roles_:
            m = json.loads((OUT / "sprite" / f"{sh}.json").read_text())["roles"][role]
            an = [a for a in ("idle", "walk", "cast", "attack", "die") if a in m["anims"]]
            picks = [("down", "idle", 0), ("left", "walk", 1), ("up", "idle", 0)] + [("down", a, 2) for a in an if a in ("attack", "die", "cast")][:3]
            S.cell(strip(sh, role, picks, hero=False), role, "", k=1)
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
