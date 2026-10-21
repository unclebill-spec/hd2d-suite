"""Asgard pack generator (Hearthmoor Art seat). Run: python3 gen_asgard.py  (writes ../, repo read-only; Pillow + numpy).
Order: character sheets (check-sprite once per sheet) -> gamefx -> kit .glb -> renders / scenes (+luma) -> metadata -> contact sheet -> README.
NF_SKIP_SHEETS=1 reuses the stored sheets + check_sprite_report.json (the default when the report exists; NF_RESHEETS=1 forces a re-render).
NF_SCENES=a,b renders only those scenes (lumas merge into renders/luma.json); NF_NO_CONTACT=1 skips contact sheet + README (quick tuning loop)."""
import json, os, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import as_common as C
import gen_sheets as GS, as_fx as X, kit_as as KJ, as_scene as SC, as_layouts as LY, as_npcs as N, as_foes as F, as_boss as B
from PIL import Image
H = C.H
OUT = HERE.parent

KIT = {
 "marble_floor": ("2 m white-marble floor tile with gold seams (every Asgard area / room)", ["gold_dust"]),
 "marble_wall": ("2 m marble wall module with gold cornice (halls, temple, Reliquary)", ["pool_gold"]),
 "gold_ledge": ("1.34 m ledge / terrace (pairs along x, 3.1 x 2.1 m each); props >= 1.5 m behind the front edge", ["pool_cold"]),
 "gold_stair": ("7 steps x 0.191 m = 1.34 m, 2 m wide, one per ledge, centred on the front face; climbs toward -z", []),
 "gold_arch": ("Goldspire's gold arch to Bifrost [0,10.6]; arrival [0,9.2,'up']; nothing within 2.6 m", ["pool_gold"]),
 "rune_pillar": ("rune-pillars [-7,3] [0,4.5] [7,3] (also beside the high seat); lightning_arc between them", ["lightning_arc", "pool_cold"]),
 "hall_facade": ("Thunder Hall door [0,-10.4]; 2.5 m clear in front; terrace + stair in front", ["pool_gold"]),
 "market_stall": ("Nessa's stall [-8,5.5], counter faces +z; 1.5 m clear", ["pool_gold"]),
 "skyfield_fence": ("Skyfield edge [10,-3]; the sky-horses are runtime NPCs", ["neon_fireflies_blue"]),
 "moot_ring": ("moot ground [6,-6]: flat ring, keep clear (festival trials)", ["rune_pulse", "pool_cold"]),
 "marble_spring": ("hidden spring (gs_spring / dt_spring / rq_spring): basin + statue; 2 m clear", ["spring_bubbles", "pool_gold"]),
 "gold_lamp": ("gold lamp post, warm accent every 6-8 m; G9's four lamps get drunk (light_drain)", ["gold_flame", "pool_gold", "light_drain"]),
 "rimed_lamp": ("dark lamp with a cold-blue rime cap (the Dimming / Cold Mark)", ["rime_tell", "pool_cold", "relight_burst"]),
 "gold_orb_chain": ("hanging gold-glass globe (y 3 m); steady", ["pool_gold"]),
 "high_seat": ("Lord-Warden's high seat on the gs_hall terrace; G5 Throne of Trials", ["pool_gold"]),
 "long_table": ("hall long tables + benches", []),
 "rune_forge": ("rune-forge (gs_hall): blank shield stand + anvil; 1.5 m clear", ["pool_cold", "lightning_arc"]),
 "temple_window": ("violet + gold stained glass (temple walls, G3)", ["pool_violet"]),
 "angel_statue": ("faceless angel statue (temple, G1, G2)", ["pool_violet"]),
 "dark_altar": ("dark altar [0,-5] (gs_temple) with the rime-glass flame; clue points; 2 m clear", ["cold_flame", "pool_cold", "rime_tell"]),
 "reliquary_door": ("Reliquary door [0,-9] (gs_temple) / G1 gate: 3 rune-locks; 3 m clear", ["rune_pulse", "pool_cold"]),
 "storm_pillar": ("G4 storm gallery conductor pillar; chain lightning; 2 m clear", ["chain_lightning", "pool_cold"]),
 "gold_mirror": ("G6 Mirror of the Dawn", ["pool_cold", "rime_tell"]),
 "urn_shelf": ("G8 sealed gold urns", ["pool_gold"]),
 "lore_tablet": ("G8 lore tablets (clue points)", []),
 "crypt_throne": ("G9 Sunless Crypt throne; Aurelion boss_stand z +4.0; Dawn-Flame on top", ["dawn_flame", "dawn_flame_red", "pool_red"]),
 "dawn_flame_brazier": ("gold flame brazier (terraces, rest stops)", ["gold_flame", "pool_gold"]),
 "as_rune_bridge": ("G7 Rune Bridge: chain along z; step only on lit runes (reused Jotunheim rune bridge)", ["rune_pulse"]),
 "as_waystone": ("waystone: hub [9.6,7], G8 safe room; 2.6 m clear (reused Jotunheim waystone)", ["rune_pulse", "pool_cold"]),
}
KIT_META = {k: {"placement": v[0], "fx": v[1]} for k, v in KIT.items()}
FX_ORDER = list(X.FX)
SCENES = [("asgard", LY.asgard, ("night", "day")), ("gs_hall", LY.gs_hall, ("night", "day")), ("gs_temple", LY.gs_temple, ("night",))] + \
         [(f"reliquary_g{i}", getattr(LY, f"reliquary_g{i}"), ("night",)) for i in range(1, 10)]


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
    fxm = H.write_fx(OUT / "gamefx", "as_fx", X.FX, 48)
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
    H.write_json(OUT / "metadata/asgard_layout.json", layouts)
    meta = metadata(reps, lumas, built, layouts)
    contact(scenes, reps, built, fxm, lumas)
    H.write_json(OUT / "metadata/asgard.json", meta)
    write_readme(reps, lumas)
    return reps, lumas


def metadata(reps, lumas, built, layouts):
    sheets = {}
    for n in GS.SHEETS:
        m = json.loads((OUT / "sprite" / f"{n}.json").read_text())
        sheets[n] = {"frame": m["frame"], "pivot": m["pivot"], "ground_row": m["ground_row"],
                     "roles": {r: {"scale": v["scale"], "anims": v["anims"], "tier": (v.get("stats_hint") or {}).get("tier")} for r, v in m["roles"].items()}}
    notes = {
        "height": "every area and Reliquary room has a 1.34 m ledge (gold_ledge pairs) and ONE gold_stair (7 x 0.191 m, 2 m wide) on its front face",
        "lighting": "day luma 55-70, night 20-30: warm gold pools (#ffc85a) every 6-8 m + neon cold-blue rune / lightning pools + violet temple glass; never all-dark",
        "keep_clear": ["no props, fx or spawns on a stair footprint + 1 m each end", "ledge edges: props >= 1.5 m behind the front edge", "gold arch arrival [0,9.2]: 2.6 m",
                       "Thunder Hall door 2.5 m, Reliquary door 3 m, dark altar 2 m, springs 2 m, waystones 2.6 m"],
        "shadow": "as_shadow decal is mid-dark #5a5068 / #7a7090 (no near-black)",
        "boss_stand": {"sentinelprime (G4)": [0, 0, -0.6], "aurelion (G9)": [0, 0, -1.4], "severin (G5)": [0, 0, -2.6]},
    }
    return {"pack": "asgard", "story": "story/asgard.md", "frame_convention": "boss_sheet layout (native big frames, pivot bottom centre, idle 0-3 walk 4-7 cast 8-11 attack 12-15 die 24-27)",
            "sheets": sheets, "companion": {"sigrun": "sprite/as_sigrun.json role sigrun (idle, walk = follow, cast, attack); wings are fx sigrun_wings; NO pet in this realm"},
            "areas": {k: {"pieces": [{"piece": p[0], "pos": list(p[1]), **({"rot": p[2]} if len(p) > 2 else {})} for p in v["pieces"] if not p[0].endswith("_floor")]} for k, v in layouts.items()},
            "placement_notes": notes, "luma_measured_on_renders": lumas,
            "neon": {"sprites": [], "allow_list_needed": [], "fx": "all gamefx/as_fx", "kit": "glow material"},
            "check_sprite": {k: v["summary"] for k, v in reps.items()}, "kit_pieces": len(json.loads((OUT / "kit/kit.json").read_text())["pieces"])}


def contact(scenes, reps, built, fxm, lumas):
    S = H.Sheet("Asgard - Goldspire, Thunder Hall, Dawn Temple, Gilded Reliquary G1-G9",
                "Goldspire folk 1x in real tops/bottoms, belts, shoes; Sigrun (companion, no pet); wraiths, sentinels, centaurs, inquisitors; elites 2-3x; Storm Sentinel Prime 5x, Aurelion 7x (+ rest pose); 1.34 m ledge + stair everywhere")
    S.section("Scenes", "luma: " + ", ".join(f"{k} {v}" for k, v in lumas.items()))
    for k in scenes:
        S.cell(scenes[k], k, "", k=1 if scenes[k].width > 700 else 2)
    S.section("Goldspire folk (1x; hero for scale)", H.report_line(reps["as_folk"]))
    for role, r in N.NPCS.items():
        S.cell(strip("as_folk", role, [("down", "idle", 0), ("down", "walk", 1), ("left", "walk", 1), ("up", "idle", 0), ("right", "idle", 0)]), role, r["desc"][:92], k=3)
    S.section("Sigrun (companion 1.1x): idle | walk | cast | attack", H.report_line(reps["as_sigrun"]))
    S.cell(strip("as_sigrun", "sigrun", [("down", "idle", 0), ("down", "walk", 1), ("left", "walk", 2), ("up", "idle", 0), ("down", "cast", 1), ("down", "attack", 2), ("left", "attack", 2)]), "sigrun", "", k=3)
    S.section("Enemies (light wraith 1.2x, storm sentinel 1.8x, storm centaur 1.6x, gilded inquisitor 1x)", H.report_line(reps["as_enemies"]))
    for role in F.ENEM:
        S.cell(strip("as_enemies", role, [("down", "idle", 0), ("down", "walk", 1), ("left", "walk", 2), ("down", "attack", 1), ("down", "attack", 2), ("left", "attack", 2), ("down", "die", 1), ("down", "die", 3)]), role, "", k=2)
    S.section("Elites (2-3x)", H.report_line(reps["as_elites"]))
    for role in F.ELITE:
        S.cell(strip("as_elites", role, [("down", "idle", 0), ("down", "walk", 1), ("down", "attack", 1), ("down", "attack", 2), ("left", "attack", 2), ("down", "die", 1), ("down", "die", 3)]), role, "", k=1)
    for sh, roles_, title in (("boss_sentinel", ("sentinelprime", "sentinel_p2", "sentinel_p3"), "Storm Sentinel Prime (boss 5x golem): P1 caged core, P2 open core, P3 overload"),
                              ("boss_aurelion", ("aurelion", "aurelion_p3", "aurelion_wraith", "aurelion_rest"), "Aurelion, the Light-Drinker (boss 7x; plate): P1-2, P3 red, wraith copy, rest/befriend")):
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
