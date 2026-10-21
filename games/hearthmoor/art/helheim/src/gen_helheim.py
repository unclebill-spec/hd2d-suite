"""Helheim pack generator (Art seat, 2026-10-21). python3 gen_helheim.py : sheets (stored + check report reused unless HH_RESHEETS=1) -> gamefx -> kit -> renders/scenes -> metadata -> contact -> README.
Names, counts and content follow story/helheim.md."""
import json, os, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import as_common as C
import gen_sheets as GS, as_fx as X, kit_hh as KH, as_scene as SC, hh_layouts as LY, hh_roles as HR
from PIL import Image
H = C.H
OUT = HERE.parent
import kit_hh2 as K2
ALIAS = {"gloam_floor": "slate_floor", "ossuary_floor": "slate_floor", "ossuary_wall": "slate_wall", "hels_arch": "spirit_arch", "hels_hall": "hall_of_rest",
         "archive_door": "vault_door", "ossuary_door": "vault_door", "bubbly_spring": "misty_spring", "cold_fire_lamp": "spirit_lamp", "grave_lantern_post": "spirit_lamp",
         "coldfire_brazier": "spirit_brazier", "salon_seat": "warden_seat", "ledger_lectern": "memory_altar", "lore_tablet": "name_stone", "pale_throne": "warden_throne",
         "mist_ledge": "mist_ledge", "mist_stair": "mist_stair", "glow_orb_chain": "glow_orb_chain", "mourning_statue": "mourning_statue", "violet_window": "violet_window", "hh_waystone": "hh_waystone"}
KIT = {
 "gloam_floor": "2 m cobble tile, Gloamhaven streets", "ossuary_floor": "2 m Ossuary floor tile", "ossuary_wall": "2 m Ossuary wall module",
 "mist_ledge": "1.34 m ledge (pairs along x, 3.1 x 2.1 m); props / fx / spawns >= 1 m from every edge", "mist_stair": "7 x 0.191 m = 1.34 m, 2 m wide, ONE per ledge, centred on the front face; climbs -z; footprint +1 m clear",
 "hels_arch": "Hel's arch to Bifrost [0,10.6]; spawn from_bifrost [0,9.2,'up']; spirit_rose_mist; 2.6 m clear", "hels_hall": "Hel's Hall [0,-9.6] (stance choice 5.2); 2.5 m clear",
 "last_hearth_inn": "The Last Hearth Inn [-7.5,-2] (Hettie), rot pi/2 = door faces the lake; violet windows", "crooked_house": "crooked house, violet windows (r 3 m point light each)",
 "lantern_bridge": "Lantern Bridge [0,1] across the lake (rot pi/2 = runs along z); 7 realm lanterns + 1 fallen-ally lantern (dark, no name); markers realm_lanterns",
 "black_lake": "2 m black-lake tile (violet reflections = lake_shimmer)", "pebble_shore": "2 m pebble tile (hh_shore)", "jetty": "jetty / ferry steps: Corvin [9,-3] (town), [0,-2] (hh_shore)",
 "lantern_boat": "lantern-boat (drifts on the lake; Lantern-Boat Night, living-lamp)", "willow_orb": "willow hung with lilac glow orbs #d6b8ff", "reeds": "reed bank (hh_shore, ls_spring)",
 "archive_door": "archive door [-10,-9] (to hh_archive)", "ossuary_door": "Ossuary stair door [0,-8] (hh_archive) / O1 Bone Door: violet rune-locks; 3 m clear",
 "bubbly_spring": "hidden spring hh_spring [-11.5,4] / ls_spring / os_spring: warm, clear, bubbling, lit violet from below; 2 m clear", "cold_fire_lamp": "street lamp, neon-blue cold fire",
 "grave_lantern_post": "grave lantern (O3), cold fire; wakes as you pass", "coldfire_brazier": "cold-fire brazier on the ground beside ledges (x +-4.4)",
 "glow_orb_chain": "hanging glow orb (porches)", "mourning_statue": "hooded statue (somber)", "violet_window": "violet glass window wall",
 "ledger_lectern": "the Ledger of Names on a lectern [0,-4] (hh_archive), torn pages", "quillon_desk": "Quillon's desk [-5,-3]", "archive_shelf": "tall archive shelf (wall)",
 "floating_candles": "floating cold-fire candles", "name_cage": "name-cage os_n1..3 + O8 fallen-ally cage", "soul_glass": "soul-glass pickup sgl_1..3", "heart_slot": "O4 glass-heart slot",
 "rhythm_door": "O6 Choir Loft rhythm door", "lich_bier": "O7 lich bier", "bone_niches": "O2 bone-niche wall (clean)", "lore_tablet": "O8 Pale Sovereign lore",
 "hh_waystone": "O8 waystone (safe); 2.6 m clear", "salon_seat": "O5 Vesperin's seat", "chain_anchor": "O9 name-chain wall anchor (breakable)",
 "pale_throne": "O9 Pale Throne; Mordrath boss stand [0,0,-1.4]",
}


def patch_frames():
    orig = SC.frame
    def frame2(sheet, role, facing, anim, i, folder="sprite"):
        if sheet == "HERO":
            return H.SP.frame(H.PAL, role, facing, anim, i).image(), (10, 31)
        return orig(sheet, role, facing, anim, i, folder)
    SC.frame = frame2


def strip(sheet, role, picks, hero=True):
    m = json.loads((OUT / "sprite" / f"{sheet}.json").read_text()); fw, fh = m["frame"]
    h = H.SP.frame(H.PAL, "wildcaller", "down", "idle", 0).image()
    row = Image.new("RGBA", (24 + fw * len(picks), fh), (0, 0, 0, 0))
    if hero:
        row.alpha_composite(h, (0, fh - 32))
    for c, (f, a, i) in enumerate(picks):
        row.alpha_composite(H.frame_of(OUT / "sprite" / f"{sheet}.png", m, role, f, a, i), (24 + c * fw, 0))
    return row


def main():
    rp = OUT / "check_sprite_report.json"
    reps = json.loads(rp.read_text()) if rp.exists() and not os.environ.get("HH_RESHEETS") else GS.main()
    fxm = H.write_fx(OUT / "gamefx", "as_fx", X.FX, 48)
    def pieces(K):
        d = KH.pieces(K); d2 = K2.pieces(K)
        def wrap(n, f):
            def g(cx):
                pc = f(cx); pc.name = n; pc.markers["note"] = KIT.get(n, ""); return pc
            return g
        out = {}
        for n in KIT:
            src = d2.get(n) or d.get(ALIAS.get(n, n))
            out[n] = wrap(n, src)
        return out
    built, _ = H.build_kit(OUT / "kit", pieces, {k: {"placement": v} for k, v in KIT.items()})
    rd = OUT / "renders"; rd.mkdir(exist_ok=True)
    for n, pc in built.items():
        H.render_mesh(pc.mesh, "night", SC.lights_of(pc), pad=6, ambient=SC.NIGHT_AMB)[0].save(rd / f"{n}_night.png")
    patch_frames()
    lumas, scenes, layouts = {}, {}, {}
    for key, fn, modes in LY.SCENES:
        S = fn(); S["fxm"] = fxm; layouts[key] = {k: v for k, v in S.items() if k != "fxm"}
        for mode in modes:
            im = SC.compose(built, S, mode); im.save(rd / f"scene_{key}_{mode}.png")
            lumas[f"{key}_{mode}"] = round(SC.luma(im), 1); scenes[f"{key}_{mode}"] = im
    (rd / "luma.json").write_text(json.dumps(lumas, indent=1)); print("luma", lumas)
    if os.environ.get("HH_NO_CONTACT"):
        return
    (OUT / "metadata").mkdir(exist_ok=True)
    H.write_json(OUT / "metadata/helheim_layout.json", layouts)
    sheets = {}
    for n in GS.SHEETS:
        m = json.loads((OUT / "sprite" / f"{n}.json").read_text())
        sheets[n] = {"frame": m["frame"], "roles": {r: {"scale": v["scale"], "anims": v["anims"], "tier": (v.get("stats_hint") or {}).get("tier")} for r, v in m["roles"].items()}}
    H.write_json(OUT / "metadata/helheim.json", {"pack": "helheim", "story": "story/helheim.md", "sheets": sheets,
        "frame_convention": "boss_sheet layout, pivot bottom centre, idle 0-3 walk 4-7 cast 8-11 attack 12-15 die 24-27",
        "areas": {k: {"pieces": [{"piece": p[0], "pos": list(p[1])} for p in v["pieces"] if not p[0].endswith("_floor")]} for k, v in layouts.items()},
        "placement_notes": {"height": "1.34 m mist_ledge pair + ONE mist_stair in every area / room", "keep_clear": "props/fx/spawns >= 1 m from ledge edges, off stair footprint +1 m",
                            "shadow": "hh_shadow mid-dark #4a4a6a / #5e6086", "boss_stand": {"vesperin (ossuary_o5)": [0, 0, -2.0], "mordrath (ossuary_o9)": [0, 0, -1.4]}, "pet": "inkling (hh_inkling, 0.6x, follows the hero)", "fallen_ally": "no fixed sprite: uses the chosen ally's existing sheet; the dark 8th bridge lantern + O8 cage carry no name"},
        "luma_measured_on_renders": lumas,
        "neon": {"sprites": {r: ["#a45cf0", "#3a2458"] for r in ("gloam_knight", "odric", "mordrath", "mordrath_p2", "mordrath_p3")},
                 "sheets": ["hh_enemies", "hh_elites", "boss_mordrath"], "safe_twins": ["hh_enemies_safe", "hh_elites_safe", "boss_mordrath_safe"],
                 "allow_list_status": "pending: lead adds a scoped Helheim entry to hd2d-suite check-sprite (not edited by Art)"},
        "story_rulings": {"hel_choice": "stance only (no item or stat change)", "pale_cosmetic": "'pale' cosmetic return (no new art needed)",
                          "mordrath": "Mordrath removes one wave of adds", "muspelheim_lock": "stays behind the flag"}, "check_sprite": {k: v["summary"] for k, v in reps.items()}})
    S = H.Sheet("Helheim - Gloamhaven hub, Shore, Archive, The Ossuary O1-O9",
                "folk 1x in real tops/bottoms, belts, boots; spirits + wraiths; elites 2-3x; Vesperin mini-boss 3x; Mordrath 8x (3 phases); Inkling pet; 1.34 m ledge + stair everywhere")
    S.section("Scenes", "luma: " + ", ".join(f"{k} {v}" for k, v in lumas.items()))
    for k in scenes:
        S.cell(scenes[k], k, "", k=1 if scenes[k].width > 700 else 2)
    F5 = [("down", "idle", 0), ("down", "walk", 1), ("left", "walk", 1), ("up", "idle", 0), ("right", "idle", 0)]
    S.section("Folk (1x)", H.report_line(reps["hh_folk"]))
    for role, r in HR.NPCS.items():
        S.cell(strip("hh_folk", role, F5), role, r["desc"][:92], k=3)
    E8 = [("down", "idle", 0), ("down", "walk", 1), ("left", "walk", 2), ("down", "attack", 2), ("left", "attack", 2), ("down", "die", 1), ("down", "die", 3)]
    for sh, title in (("hh_enemies", "Enemies"), ("hh_elites", "Elites + mini-boss")):
        S.section(title, H.report_line(reps[sh]))
        for role in json.loads((OUT / "sprite" / f"{sh}.json").read_text())["roles"]:
            S.cell(strip(sh, role, E8), role, "", k=2 if sh == "hh_enemies" else 1)
    S.section("Inkling (pet)", H.report_line(reps["hh_inkling"]))
    S.cell(strip("hh_inkling", "inkling", F5), "inkling", "", k=4)
    S.section("Mordrath (8x boss)", H.report_line(reps["boss_mordrath"]))
    for role, v in json.loads((OUT / "sprite/boss_mordrath.json").read_text())["roles"].items():
        an = [a for a in ("cast", "attack", "die") if a in v["anims"]]
        S.cell(strip("boss_mordrath", role, [("down", "idle", 0), ("left", "walk", 1), ("up", "idle", 0)] + [("down", a, 2) for a in an], hero=False), role, "", k=1)
    S.section("Kit night renders", "")
    for n in built:
        S.cell(Image.open(rd / f"{n}_night.png"), n, "", k=3)
    S.section("gamefx (48 px)", "")
    for n in X.FX:
        e = fxm["effects"][n]; st = Image.new("RGBA", (48 * e["frames"], 48), (12, 14, 26, 255))
        for i in range(e["frames"]):
            st.alpha_composite(SC.fxf(fxm, n, i), (i * 48, 0))
        S.cell(st, n, "", k=2)
    S.render(OUT / "contact_sheet.png")


if __name__ == "__main__":
    main()
