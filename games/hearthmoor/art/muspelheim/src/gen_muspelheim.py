"""Muspelheim pack generator (Hearthmoor Art seat). Run: python3 gen_muspelheim.py  (writes ../, repo read-only; Pillow + numpy).
Order: character sheets (check-sprite once per sheet) -> Kindle -> gamefx -> kit .glb -> renders / scenes (+luma) -> metadata -> contact sheet -> README.
MP_SKIP_SHEETS=1 reuses the stored sheets + check_sprite_report.json (token-saver; sheets are unchanged)."""
import json, os, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mp_common as C
import gen_sheets as GS, kindle_gen as KG, mp_fx as X, kit_muspel as KJ, mp_scene as SC, mp_layouts as LY, mp_npcs as N, mp_foes as F, mp_boss as B
from PIL import Image
H = C.H
OUT = HERE.parent

KIT_META = {
 "warm_lantern": ("warm accent every 6-8 m so grades never go all red or all blue", ["pool_forge"]),
 "basalt_floor": ("2 m grid ground of Cinderhold / Lavafalls", ["ember_motes", "ash_fall"]),
 "lava_channel": ("2 x 4 m glowing channel; chain end to end (rot pi/2 to run along x); 1 m clear of spawns", ["pool_lava", "lava_crawl", "neon_embers"]),
 "lava_pool": ("round lava pool (fall-pool, hub corner); keep props 2.4 m away", ["pool_lava", "neon_embers"]),
 "basalt_ledge": ("1.34 m plateau / ledge (chain along x); props sit >= 1.5 m back from the front edge", ["pool_forge"]),
 "basalt_stair": ("one per ledge, centred, top flush with the ledge front face; climbs toward -z (rot pi to climb toward +z)", []),
 "warden_stones": ("the Warden's Walk [0,3.0]: five 0.28 m stepping-stones over lava; quest route, keep clear", ["pool_lava", "neon_embers"]),
 "basalt_house": ("ember-kin house, door faces +z, warm window pools; 1.8 m clear in front of the door", ["pool_forge", "ember_motes"]),
 "forge_hall": ("fire-giant forge, 3.2 x 4 m door; 2.5 m clear in front of it", ["pool_forge", "forge_flame", "ember_motes"]),
 "red_arch": ("Cinderhold's Red arch to Bifrost [0,10.6]; arrival [0,9.2,'up']; nothing within 2.6 m", ["heat_shimmer", "pool_lava"]),
 "spice_stall": ("Svala's spice-brazier stall [-7.0,5.0]; counter faces +z", ["pool_forge", "forge_flame"]),
 "brazier_stand": ("forge brazier; forge_flame billboard at y 1.9 m + pool_forge", ["forge_flame", "pool_forge"]),
 "cold_brazier": ("cold-fire brazier (neon blue); cold_flame billboard at y 1.9 m + pool_cold", ["cold_flame", "pool_cold"]),
 "shrine_lamp": ("violet shrine-lamp: Warden's seat (one either side) and spring grotto; violet_flame at y 2.1 m", ["violet_flame", "pool_violet"]),
 "glass_bridge": ("glass walkway 2 x 4 m; Cinderhold -> Lavafalls [10,-9]; Caldera C3 (lit panels safe)", ["pool_lava"]),
 "lizard_stable": ("Orm's lizard stables [-9,-3]; open side +z; 1.5 m clear in front", ["pool_forge"]),
 "emberfall_anvil": ("Emberfall contest anvils [8,-2] and Torka's school anvils [-6,-4]; 1.5 m clear", ["pool_forge", "neon_embers"]),
 "dance_ring": ("Emberfall fire-dance ring [8,-2], flat, festival ground", ["pool_forge"]),
 "obsidian_pillar": ("basalt pillar with frost-vein cracks; the hidden spring sits behind one [-11,-8.5]", ["pool_cold", "frost_vein"]),
 "amber_orb_chain": ("molten-glass globe on a chain over streets and halls (y 3 m); steady", ["glow_orb_amber"]),
 "spring_pool": ("hidden bubbly spring (clear teal): spring_bubbles + pool_teal + two shrine_lamps; 2 m clear", ["spring_bubbles", "pool_teal", "steam_puff"]),
 "muspel_waystone": ("Cinderhold waystone: Lavafalls arrival, Caldera C8 landing; 2.6 m clear; pool_lava r 3 m", ["pool_lava", "neon_embers"]),
 "cinder_cairn": ("trail marker on paths; 1.2 m clear", ["ember_motes"]),
 "forge_floor": ("2 m grid, Sigil Forge and the Caldera throne room (copper inlay)", []),
 "forge_wall": ("2 m wall module with a furnace window (warm pool on the floor in front)", ["pool_forge"]),
 "wardens_seat": ("the Warden's seat [0,-6.5]; a shrine_lamp 1.6 m either side", ["pool_forge"]),
 "seal_cast_bed": ("sf_cast clue point [-5.5,-3.0]", ["pool_forge", "neon_embers"]),
 "stamp_press": ("sf_mirror group, seal foundry", ["pool_forge"]),
 "ledger_desk": ("sf_ledger clue point", []),
 "sigil_mould_wall": ("sf_mirror: the sigil mould wall, west wall of mp_hall", ["pool_forge"]),
 "lava_fall_cliff": ("molten falls cliff, 4 m wide; lava_fall billboards over each ribbon; pool_lava at the foot (fall-pool)", ["lava_fall", "pool_lava", "neon_embers"]),
 "glass_terrace": ("1.34 m glass terrace (like basalt_ledge) + basalt_stair", ["pool_lava"]),
 "caldera_mouth_arch": ("Caldera mouth [0,-7.5]: 6 m arch, three seal-doors; keep 3 m clear", ["pool_lava", "pool_cold"]),
 "ember_throne": ("C9 Ember Throne, back centre; boss_stand marker z +3.6 (Vharzul 8x)", ["pool_lava", "lava_crawl"]),
 "warden_lamp_stand": ("the three Warden's lamps (Vharzul P3), 120 degrees apart on the arena ring", ["warden_lamp", "pool_violet"]),
 "furnace": ("C4 Furnace Hall furnace; 3 m clear in front of the mouth", ["heat_shimmer", "pool_lava", "forge_flame"]),
 "hanging_crystals": ("ceiling piece, hangs at y 3 m (Cold Seam, springs of glass)", ["glow_crystals_blue", "glow_crystals_violet"]),
 "cold_seam_wall": ("C5 Cold Seam frost-vein wall (Veyra's beat); pool_cold in front", ["pool_cold", "frost_vein"]),
}
KIT_META = {k: {"placement": v[0], "fx": v[1]} for k, v in KIT_META.items()}
FX_ORDER = list(X.FX)
SCENES = [("cinderhold", LY.cinderhold, ("night", "day")), ("sigil_forge", LY.sigil_forge, ("night",)), ("lavafalls", LY.lavafalls, ("night", "day")),
          ("caldera_throne", LY.caldera_throne, ("night",))]


def patch_frames():
    orig = SC.frame

    def frame2(sheet, role, facing, anim, i, folder="sprite"):
        if sheet == "HERO":
            return H.SP.frame(H.PAL, role, facing, anim, i).image(), (10, 31)
        if sheet == "KINDLE":
            m = json.loads((OUT / "pets/kindle.json").read_text())
            return H.frame_of(OUT / "pets/kindle_neon.png", m, role, facing, anim, i), (10, 31)
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
        row.alpha_composite(H.frame_of(OUT / folder / f"{sheet}.json".replace(".json", ".png"), m, role, f, a, i), (24 + c * fw, 0))
    return row


def kindle_main():
    safe, neon, fa, fm = KG.main()
    KG.contact(safe, neon, fa, fm)
    return fm


def main():
    skip = os.environ.get("MP_SKIP_SHEETS")
    if skip and (OUT / "check_sprite_report.json").exists():
        reps = json.loads((OUT / "check_sprite_report.json").read_text())
        kindle_main()
    else:
        reps = GS.main()
        kindle_main()
        sys.path.insert(0, "/workspace/hd2d-suite/tools/check-sprite")
        import check_sprite as CS
        reps["kindle (safe)"] = CS.check(OUT / "pets/kindle.png", OUT / "pets/kindle.json")
        CS.NEON_PETS_ALLOW["pet_kindle"] = {"#a81c22", "#e0302a", "#ff5a4a"}          # in-process only (repo read-only): simulates the scoped entry the lead adds
        reps["kindle_neon (needs scoped pet_kindle allow-list)"] = CS.check(OUT / "pets/kindle_neon.png", OUT / "pets/kindle.json")
        for k in ("kindle (safe)", "kindle_neon (needs scoped pet_kindle allow-list)"):
            print(k, reps[k]["summary"])
        H.write_json(OUT / "check_sprite_report.json", reps)
    fxm = H.write_fx(OUT / "gamefx", "mp_fx", X.FX, 48)
    built, _ = H.build_kit(OUT / "kit", KJ.pieces, KIT_META)
    rd = OUT / "renders"; rd.mkdir(exist_ok=True)
    for n, pc in built.items():
        H.render_mesh(pc.mesh, "night", SC.lights_of(pc), pad=6, ambient=SC.NIGHT_AMB)[0].save(rd / f"{n}_night.png")
    patch_frames()
    lumas, scenes, layouts = {}, {}, {}
    for key, fn, modes in SCENES:
        S = fn(); S["fxm"] = fxm
        for mode in modes:
            im = SC.compose(built, S, mode)
            im.save(rd / f"scene_{key}_{mode}.png")
            lumas[f"{key}_{mode}"] = round(SC.luma(im), 1)
            scenes[f"{key}_{mode}"] = im
        layouts[key] = {k: v for k, v in S.items() if k != "fxm"}
    print("luma", lumas)
    (OUT / "metadata").mkdir(exist_ok=True)
    H.write_json(OUT / "metadata/muspelheim_layout.json", layouts)
    meta = metadata(reps, lumas, built)
    contact(scenes, reps, built, fxm, lumas)
    H.write_json(OUT / "metadata/muspelheim.json", meta)
    write_readme(reps, lumas)
    return reps, lumas


def metadata(reps, lumas, built):
    sheets = {}
    for n in ("mp_folk", "mp_giants", "mp_enemies", "mp_elites", "boss_vharzul"):
        m = json.loads((OUT / "sprite" / f"{n}.json").read_text())
        sheets[n] = {"frame": m["frame"], "pivot": m["pivot"], "ground_row": m["ground_row"],
                     "roles": {r: {"scale": v["scale"], "anims": v["anims"], "tier": (v.get("stats_hint") or {}).get("tier")} for r, v in m["roles"].items()}}
    notes = {
        "height": "every area has real height: ledges / terraces >= 1.2 m and a stair (6 steps, 0.2 m rise, 0.5 m run, 2 m wide); Cinderhold Warden's terrace 1.34 m, Sigil Forge east gallery 1.34 m, Lavafalls glass terrace 1.34 m, Caldera ledge 1.34 m",
        "lighting": "day luma 55-70, night 20-30 with glow pools (lava, forge, cold fire, violet); night ambient is lifted warm grey (0.34, 0.30, 0.34) so the grade is neither all red nor all blue: forge amber + lava orange carry the warmth, cold-blue and violet are accents",
        "keep_clear": ["no props, fx decals or spawns on a stair footprint plus 1 m at each end", "ledge edges: props >= 1.5 m behind the front edge (marker ledge_edge, no_props_within_m 0.8 for fx)",
                       "Red arch arrival [0,9.2]: nothing within 2.6 m", "forge_hall door: 2.5 m clear; basalt_house door 1.8 m; Caldera mouth 3 m", "lava: nothing spawns within 1 m of a channel; warden_stones route clear",
                       "burn_patch decals only on open ground away from spawns and stairs"],
    }
    return {"pack": "muspelheim", "story": "story/muspelheim.md", "frame_convention": "boss_sheet layout (native big frames, pivot bottom centre, idle 0-3 walk 4-7 cast 8-11 attack 12-15 die 24-27)",
            "sheets": sheets, "companion": {"kindle": "pets/kindle.json (pets layout 20x32, pivot [10,32], idle 0-3 walk 4-7 follow 8-11); primary kindle_neon.png, fallback kindle.png; fx pets/kindle_fx.*"},
            "areas": {k: {"pieces": [{"piece": p[0], "pos": list(p[1]), **({"rot": p[2]} if len(p) > 2 else {})} for p in v["pieces"] if not p[0].endswith("_floor")]} for k, v in
                      {s[0]: s[1]() for s in SCENES}.items()},
            "placement_notes": notes, "luma_measured_on_renders": lumas,
            "neon": {"sprites": ["pets/kindle_neon.png (primary; needs scoped allow-list pet_kindle: #a81c22 #e0302a #ff5a4a)"], "fx": "all gamefx/mp_fx and pets/kindle_fx", "kit": "glow material"},
            "check_sprite": {k: v["summary"] for k, v in reps.items()}, "kit_pieces": len(json.loads((OUT / "kit/kit.json").read_text())["pieces"])}


def contact(scenes, reps, built, fxm, lumas):
    S = H.Sheet("Muspelheim - Cinderhold, Sigil Forge, Lavafalls, Ember Caldera (Vharzul the Ember Throne)",
                "ember-kin 1x + fire-giants 2.5x in real tunics, belts and boots; Kindle; hounds, elementals, golems; Vharzul 8x (only plate); kit with real height; neon on glow only")
    S.section("Scenes (night + day)", "luma: " + ", ".join(f"{k} {v}" for k, v in lumas.items()))
    for k in scenes:
        S.cell(scenes[k], k, "", k=1 if scenes[k].width > 700 else 2)
    S.section("Ember-kin (1x; hero for scale): down idle | down walk | left walk | up idle | right idle", H.report_line(reps["mp_folk"]))
    for role, r in N.NPCS.items():
        if r.get("folk"):
            S.cell(strip("mp_folk", role, [("down", "idle", 0), ("down", "walk", 1), ("left", "walk", 1), ("up", "idle", 0), ("right", "idle", 0)]), role, r["desc"][:92], k=3)
    S.section("Fire-giants (2.5-2.6x, tunics + belts + boots)", H.report_line(reps["mp_giants"]))
    for role, r in N.NPCS.items():
        if not r.get("folk"):
            S.cell(strip("mp_giants", role, [("down", "idle", 0), ("down", "walk", 1), ("left", "walk", 1), ("up", "idle", 0), ("right", "idle", 0)]), role, r["desc"][:92], k=2)
    S.section("Kindle the ember salamander (companion)", "kindle_neon.png primary; kindle.png palette-safe twin (passes); idle 0-3 | walk 4-7 | follow 8-11")
    for n in ("kindle_neon.png", "kindle.png"):
        S.cell(Image.open(OUT / "pets" / n), "pets/" + n, "", k=3)
    S.section("Enemies (ashen cultist 1x, magma hound 1.4x, flame elemental 1.5x, fire golem 2x)", H.report_line(reps["mp_enemies"]))
    for role in F.ENEM:
        S.cell(strip("mp_enemies", role, [("down", "idle", 0), ("down", "walk", 1), ("left", "walk", 2), ("down", "attack", 1), ("down", "attack", 2), ("left", "attack", 2), ("down", "die", 1), ("down", "die", 2), ("down", "die", 3)]), role, "", k=2)
    S.section("Gate foe, rares + mini-boss (magma hound 2x, ashalpha 2x, pyreling 3x, Kilnmother 3x)", H.report_line(reps["mp_elites"]))
    for role in F.ELITE:
        S.cell(strip("mp_elites", role, [("down", "idle", 0), ("down", "walk", 1), ("down", "attack", 1), ("down", "attack", 2), ("left", "attack", 2), ("down", "die", 1), ("down", "die", 2), ("down", "die", 3)]), role, "", k=1)
    S.section("Vharzul the Ember Throne (boss 8x; ONLY plate): phase 1-2 and phase 3 (crown flares)", H.report_line(reps["boss_vharzul"]))
    for role in ("vharzul", "vharzul_p3"):
        S.cell(strip("boss_vharzul", role, [("down", "idle", 0), ("left", "walk", 1), ("down", "attack", 2), ("up", "idle", 0), ("down", "die", 1), ("down", "die", 2), ("down", "die", 3)]), role, "", k=1)
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
