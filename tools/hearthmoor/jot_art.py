"""[JOTUNHEIM] Skeleton art build for the Jotunheim areas (realm-jotunheim branch). Modeled on svart_art.py / alf_art.py.

Wires the staging art in games/hearthmoor/art/jotunheim/ (copied from /workspace/hearthmoor-staging/art/jotunheim/) into the BUILT Jotunheim
areas without re-assembling:
  sprites  giant NPC sheets, enemy sheets, the bosses / rares / Ulfar / Flurry become extra sheets of each area's actors.json
  kit      staging .glb files are copied in; a name clash takes the staging piece
  gamefx   staging jot_fx rows are appended under the area's gamefx atlas (48 px cells), plus the plaza's quest_mark / quest_turnin glyphs
Props: PLACE puts staging kit pieces into scene.json (objects + lamps + collision blockers). Only adds or overwrites files: it never
deletes anything (only its own earlier placements, marked "jot_art", are re-made). The area's original gamefx atlas is kept once as
gamefx.base.(png|json) and every run rebuilds from that. Idempotent.

STATUS: SKELETON. The art pack is not ready. Nothing runs until /workspace/hearthmoor-staging/art/jotunheim/READY.txt exists
(--force overrides, for a dry look). Every table below is a placeholder to be filled from the art README when the pack lands: the sheet
names, the staging role names and the PLACE coordinates are guesses from the story doc (areas / NPCs / bosses), not from real files.
Missing staging files are SKIPPED with a message, never an error, so a partial pack can be wired in stages.

Stonefrost II / III (staging gamefx/stonefrost_fx, 48 px cells, 10 effects) are appended under the gamefx atlas of EVERY built area that has one
(mark `stonefrost_from`, crop-and-append, idempotent; add / overwrite only), so the spells draw wherever the player casts. RUN THIS LAST: build.py's
install_forge / install_alchemy re-crop a gamefx atlas at their own marks and would drop the Stonefrost rows (re-run `jot_art.py --stonefrost-all` after them).
Real kit props replace the stand-ins: rune_waystone (Waystone Crypt, barrow2), watch_cairn + cairn_toppled (the Toll of Stones cairns, Rime Caves; the game
swaps them with ctx.pz) and stone_cairn trail markers.

usage: python3 tools/hearthmoor/jot_art.py [--force] [--stonefrost-all] [area ...]      (then: cd games/hearthmoor && python3 -c "import build; build.write_pwa()")
"""
import json, shutil, sys
from pathlib import Path
from PIL import Image

GAME = Path(__file__).resolve().parents[2] / "games" / "hearthmoor"
STAGING = Path("/workspace/hearthmoor-staging/art/jotunheim")
ST = GAME / "art" / "jotunheim"
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
SF_ONLY = "--stonefrost-all" in sys.argv and not ARGS   # `--stonefrost-all` alone: fx only, no sprite / kit / place work
FORCE = "--force" in sys.argv
PLANNED = ["jotunheim", "jt_hall", "rimecaves", "barrow", "barrow2"]   # story 2.1; the Barrow is two areas (decision 8, like clockdeep / clockdeep2)
AREAS = ARGS or PLANNED

GIANTS = ["kolbrun", "jarl", "ulfar_town", "rimewife", "skuli", "goatwife", "grimsa", "rimecaptain", "gi_man", "gi_woman"]   # jt_giants.json roles (2-3.2x)
# base-atlas stand-in role -> jt_giants role (only roles the area has are re-pointed): Stonehollow's actors use the stock role names so the
# area assembles; this repaints them as the giants. `gnome` = Ulfar's town look (the companion is the separate 3x / 2.4x `ulfar` sheet).
TOWNS = {"dwarftrader": "grimsa", "wispcatcher": "skuli", "poolkeeper": "goatwife", "gnome": "ulfar_town", "elffolk": "gi_man", "elffolk2": "gi_woman",
         "innkeeper": "kolbrun", "shopkeeper": "jarl", "lanternseller": "rimewife", "nightmerchant": "rimecaptain"}
SHEETS = {  # sheet name -> (staging json, {area role: staging role})
    "jtnpc": (ST / "sprite" / "jt_giants.json", {**TOWNS, **{r: r for r in GIANTS}}),
    "ulfar": (ST / "sprite" / "ulfar.json", {"ulfar": "ulfar"}),   # 3x in town, 2.4x in combat (meta combat_scale; the engine scales him, no second sheet: Cozy Builder)
    "jtenemy": (ST / "sprite" / "jt_enemies.json", {r: r for r in ("frost_troll", "ice_golem", "avalanche_golem", "rime_berserker")}),
    "flurry": (ST / "pets" / "flurry.json", {"pet_flurry": "pet_flurry"}),   # the NEON twin is the main look (Cozy Builder); scoped check-sprite allow-list entry
    "flurry_safe": (ST / "pets" / "flurry.json", {"pet_flurry_safe": "pet_flurry"}),   # palette-safe fallback (its own role, not placed)
}
IMAGE = {"flurry": "flurry_neon.png", "flurry_safe": "flurry.png"}   # sheet -> staging png when it is not the json's own image
EXTRA = {    # sheets only where the fight / scene is (their own frame size)
    "jotunheim": {"jtgoat": (ST / "sprite" / "jt_goats.json", {"goat": "goat", "clatter": "clatter"})},   # Stonehollow's pen goats + Clatter (runtime actors, goat_gen.py)
    "barrow2": {"boss_hrimgard": (ST / "sprite" / "boss_hrimgard.json", {"hrimgard": "hrimgard", "hrimgard_p3": "hrimgard_p3"}),
                "jtelite": (ST / "sprite" / "jt_elites.json", {"ormgar": "ormgar"})},
    "rimecaves": {"jtelite": (ST / "sprite" / "jt_elites.json", {"frostmother": "frostmother", "avalanche": "avalanche"})},
}
FX_FILE = ("gamefx", "jt_fx.json")   # staging gamefx rows: ST / "gamefx" / "jt_fx.json"


def have(p):
    if not Path(p).exists():
        print(f"  skip (not in the pack yet): {Path(p).relative_to(GAME) if str(p).startswith(str(GAME)) else p}")
        return False
    return True


def copy_staging():
    """Copy the staging pack into art/jotunheim/ (add / overwrite only)."""
    if not STAGING.exists():
        return False
    ST.mkdir(parents=True, exist_ok=True)
    shutil.copytree(STAGING, ST, dirs_exist_ok=True)
    return True


def sprites(area):
    d = GAME / "areas" / area / "public" / "art" / "sprite"
    mp = d / "actors.json"; m = json.loads(mp.read_text()); m.setdefault("sheets", {})
    for nm, (src, roles) in {**SHEETS, **EXTRA.get(area, {})}.items():
        if not have(src): continue
        sm = json.loads(src.read_text())
        shutil.copy2(src.parent / IMAGE.get(nm, sm["image"]), d / f"{nm}.png")
        out = {k: sm[k] for k in ("tool", "biome", "frame", "pivot", "ground_row", "facings", "anims", "cols", "size")}
        out["image"] = f"{nm}.png"; out["roles"] = {}
        for ar, sr in roles.items():
            if nm == "jtnpc" and ar in TOWNS and ar not in m["roles"]:
                continue   # re-point only roles this area actually has
            if sr not in sm["roles"]: print(f"  {nm}: no staging role {sr}"); continue
            r = sm["roles"][sr]
            out["roles"][ar] = {k: v for k, v in r.items() if k != "frames"}
            prev = m["roles"].get(ar, {})
            m["roles"][ar] = {"sheet": nm, "row": r["row"], "kind": r.get("kind", prev.get("kind", "creature")),
                              "anims": r.get("anims", ["idle", "walk"]), "desc": r.get("desc", ""),
                              **({"enemy": True} if r.get("enemy") or prev.get("enemy") else {}),
                              **({"pet": True, "follower": True} if nm == "flurry" else {})}
        (d / f"{nm}.json").write_text(json.dumps(out, indent=1))
        m["sheets"][nm] = {"json": f"{nm}.json", "image": f"{nm}.png"}
    mp.write_text(json.dumps(m, indent=1))


def kit(area):
    d = GAME / "areas" / area / "public" / "art" / "kit"
    for g in sorted((ST / "kit").glob("*.glb")):
        shutil.copy2(g, d / g.name)


def gamefx(area):
    if not have(ST / "gamefx" / "jt_fx.json"): return False
    d = GAME / "areas" / area / "public" / "art" / "gamefx"
    if not (d / "gamefx.json").exists() and not (d / "gamefx.base.json").exists():
        # no atlas yet (wispwood): start from an empty base so the staging rows are the whole atlas, and point the scene at it
        d.mkdir(parents=True, exist_ok=True)
        sj = json.loads((ST / "gamefx" / "jt_fx.json").read_text())
        (d / "gamefx.base.json").write_text(json.dumps({k: sj[k] for k in ("tool", "biome", "seed", "cell", "cast_sets", "cycle")} | {"image": "gamefx.png", "size": [0, 0], "effects": {}}))
        Image.new("RGBA", (sj["cell"], sj["cell"]), (0, 0, 0, 0)).save(d / "gamefx.base.png")   # one blank row
        sp = GAME / "areas" / area / "scene.json"; sc = json.loads(sp.read_text())
        sc["gamefx"] = {"image": "public/art/gamefx/gamefx.png", "json": "public/art/gamefx/gamefx.json"}
        sp.write_text(json.dumps(sc, separators=(",", ":")))
    bj, bp = d / "gamefx.base.json", d / "gamefx.base.png"
    if not bj.exists():
        shutil.copy2(d / "gamefx.json", bj); shutil.copy2(d / "gamefx.png", bp)
    base, sj = json.loads(bj.read_text()), json.loads((ST / "gamefx" / "jt_fx.json").read_text())
    assert base["cell"] == sj["cell"], "cell size mismatch"
    bi, si = Image.open(bp).convert("RGBA"), Image.open(ST / "gamefx" / sj["image"]).convert("RGBA")
    # the ! / ? quest-marker glyphs (quest_mark, quest_turnin) copied from the plaza atlas (same 48 px cell): the realm areas' atlases had none,
    # so the Jotunheim NPC markers (Kolbrun, Jarl Thyra, Ulfar...) spawned nothing
    pm = json.loads((GAME / "areas/plaza/public/art/gamefx/gamefx.json").read_text()); pim = Image.open(GAME / "areas/plaza/public/art/gamefx/gamefx.png").convert("RGBA")
    c = base["cell"]; assert pm["cell"] == c
    mk = [("quest_mark", pm["effects"]["quest_mark"]), ("quest_turnin", pm["effects"]["quest_turnin"])]
    strip = Image.new("RGBA", (pim.width, c * len(mk)), (0, 0, 0, 0))
    for i, (_, e) in enumerate(mk):
        strip.paste(pim.crop((0, e["row"] * c, pim.width, (e["row"] + 1) * c)), (0, i * c))
    im = Image.new("RGBA", (max(bi.width, si.width, strip.width), bi.height + si.height + strip.height), (0, 0, 0, 0))
    im.paste(bi, (0, 0)); im.paste(si, (0, bi.height)); im.paste(strip, (0, bi.height + si.height)); im.save(d / "gamefx.png")
    off = bi.height // base["cell"]
    for i, (k, e) in enumerate(mk):
        base["effects"][k] = {**{kk: vv for kk, vv in e.items() if kk != "frame_list"}, "row": off + si.height // c + i}
    for k, e in sj["effects"].items():
        e = {kk: vv for kk, vv in e.items() if kk not in ("frame_list", "strip")}
        e["row"] = e["row"] + off
        base["effects"][k] = e
    base["size"] = [im.width, im.height]
    (d / "gamefx.json").write_text(json.dumps(base, indent=1))
    return True


# props placed per area: (piece, preferred [x, z], "fixed"?); the spot is searched outward on flat, walkable, uncrowded ground unless "fixed".
# Coordinates are the art README's Stonehollow layout (metadata/jotunheim.json), moved where the area spec's own terrain (plateau + stair come
# from the spec, so the kit's stone_ledge / stone_stair are not placed) or an actor stands. Keep-clear: nothing on the stair + 1 m, 2.5 m in
# front of longhouse doors, 1.5 m around the from_bifrost spawn.
NOBLOCK = {"cairn_toppled"}   # walkable rubble: no blocker (kit.json blockers [])
WALK = {"snow_floor", "ice_floor", "ice_lake", "glow_ice_pool", "barrow_floor", "rune_bridge"}   # flat decals: walkable, no blocker
PLACE = {
    "jotunheim": [("longhouse", [-7.8, -6.0], "fixed"), ("longhouse", [7.8, -6.2], "fixed"),
                  ("cold_brazier", [-2.4, -5.0], "fixed"), ("cold_brazier", [2.4, -5.0], "fixed"), ("rune_standing_stone", [0.0, -5.4], "fixed"),
                  ("rune_standing_stone", [10.6, -1.4], "fixed"), ("snow_mound", [-10.6, 6.2], "fixed"), ("ice_lake", [8.0, -3.2], "fixed"),
                  ("lift_stone", [-1.4, 2.6], "fixed"), ("lift_stone", [0.0, 3.3], "fixed"), ("lift_stone", [1.4, 2.6], "fixed"),
                  ("cold_brazier", [-3.6, 1.6], "fixed"), ("cold_brazier", [3.6, 1.6], "fixed"), ("cold_brazier", [-3.2, 4.8], "fixed"), ("cold_brazier", [3.2, 4.8], "fixed"),
                  ("rune_standing_stone", [-5.4, 0.2], "fixed"), ("rune_standing_stone", [5.2, -0.4], "fixed"), ("warm_lantern", [-7.8, 7.4], "fixed"), ("warm_lantern", [4.8, 6.4], "fixed"),
                  ("goat_fence", [-10.6, 3.4], "fixed"), ("goat_fence", [-8.6, 3.4], "fixed"), ("goat_fence", [-7.0, 3.4], "fixed"), ("fur_stall", [-6.0, 4.8], "fixed"),
                  ("giant_stool", [-8.8, 5.2], "fixed")],
    "jt_hall": [("cold_brazier", [-1.5, -2.0], "fixed"), ("cold_brazier", [1.5, -2.0], "fixed"), ("cold_brazier", [0.0, -3.6], "fixed"), ("cold_brazier", [0.0, -0.4], "fixed"),
                ("rune_standing_stone", [-7.0, -10.4], "fixed"), ("rune_standing_stone", [7.0, -10.4], "fixed"),
                ("shield_rack", [-8.0, -11.4], "fixed"), ("shield_rack", [8.0, -11.4], "fixed"),
                ("warm_lantern", [-2.8, 9.4], "fixed"), ("warm_lantern", [2.8, 9.4], "fixed"), ("warm_lantern", [-9.0, 4.8], "fixed"), ("warm_lantern", [9.0, 4.8], "fixed"),
                ("giant_stool", [-8.0, -3.0], "fixed"), ("giant_stool", [-8.0, 0.2], "fixed"), ("giant_stool", [-8.0, 3.4], "fixed"),
                ("giant_stool", [8.0, -3.0], "fixed"), ("giant_stool", [8.0, 0.2], "fixed"), ("giant_stool", [8.0, 3.4], "fixed"),
                ("glow_ice_pool", [14.2, -5.4], "fixed"), ("ice_crystal_cluster", [12.2, -10.8], "fixed"), ("ice_crystal_cluster", [16.2, -10.8], "fixed"),
                ("frost_rune_pillar", [12.2, -7.0], "fixed"), ("frost_rune_pillar", [16.2, -7.0], "fixed"), ("cold_brazier", [12.4, -3.0], "fixed"), ("cold_brazier", [16.0, -3.0], "fixed")],
    "rimecaves": [("barrow_door", [0.0, -11.3], "fixed"), ("cold_brazier", [-3.6, -8.4], "fixed"), ("cold_brazier", [3.6, -8.4], "fixed"), ("rune_standing_stone", [-9.8, -7.0], "fixed"), ("rune_standing_stone", [-9.8, -8.8], "fixed"),
                  ("frost_rune_pillar", [-7.4, -4.6], "fixed"), ("frost_rune_pillar", [7.4, -4.6], "fixed"), ("frost_rune_pillar", [-8.0, 3.0], "fixed"), ("frost_rune_pillar", [8.0, 3.0], "fixed"),
                  ("ice_crystal_cluster", [-11.0, 10.4], "fixed"), ("ice_crystal_cluster", [11.0, 10.4], "fixed"), ("ice_crystal_cluster", [-11.0, -3.0], "fixed"), ("ice_crystal_cluster", [11.0, -3.0], "fixed"),
                  ("glow_ice_pool", [-6.0, 5.2], "fixed"), ("glow_ice_pool", [6.0, 5.2], "fixed"), ("glow_ice_pool", [-7.4, -0.4], "fixed"), ("glow_ice_pool", [7.4, -0.4], "fixed"), ("glow_ice_pool", [0.0, 0.2], "fixed"),
                  ("ice_wall", [8.0, -9.0], "fixed"), ("ice_wall", [10.0, -9.0], "fixed"), ("warm_lantern", [-2.8, 9.4], "fixed"), ("warm_lantern", [2.8, 9.4], "fixed"), ("warm_lantern", [-4.6, -3.0], "fixed"),
                  # the Toll of Stones cairns (game CAIRNS in jotunheim.js): the real watch-cairn, plus the toppled rubble that the game shows in its place
                  ("watch_cairn", [-10.2, 6.4], "fixed", {"pz": "tt_cairn1"}), ("watch_cairn", [10.2, 6.4], "fixed", {"pz": "tt_cairn2"}), ("watch_cairn", [3.0, -1.6], "fixed", {"pz": "tt_cairn3"}),
                  ("cairn_toppled", [-10.2, 6.4], "fixed", {"pz": "tt_cairn1_t", "hidden": True}), ("cairn_toppled", [10.2, 6.4], "fixed", {"pz": "tt_cairn2_t", "hidden": True}),
                  ("cairn_toppled", [3.0, -1.6], "fixed", {"pz": "tt_cairn3_t", "hidden": True}),
                  ("stone_cairn", [-5.6, 6.6], "fixed"), ("stone_cairn", [5.4, 7.2], "fixed")],   # trail markers on the snow path
    "barrow": [("cold_brazier", [-3.6, 7.0], "fixed"), ("cold_brazier", [3.6, 7.0], "fixed"), ("shield_rack", [-9.4, -6.0], "fixed"), ("shield_rack", [9.4, -6.0], "fixed"),
               ("shield_rack", [-9.4, -10.0], "fixed"), ("shield_rack", [9.4, -10.0], "fixed"), ("cold_brazier", [0.0, -8.6], "fixed"),
               ("frost_rune_pillar", [-6.4, -4.8], "fixed"), ("frost_rune_pillar", [6.4, -4.8], "fixed"),
               ("glow_ice_pool", [-5.0, -17.0], "fixed"), ("glow_ice_pool", [5.0, -17.0], "fixed"), ("glow_ice_pool", [0.0, -19.4], "fixed"), ("glow_ice_pool", [-6.4, -13.6], "fixed"), ("glow_ice_pool", [6.4, -13.6], "fixed"),
               ("ice_crystal_cluster", [-10.4, -15.0], "fixed"), ("ice_crystal_cluster", [10.4, -15.0], "fixed"), ("ice_crystal_cluster", [-10.4, -20.6], "fixed"), ("ice_crystal_cluster", [10.4, -20.6], "fixed"),
               ("cold_brazier", [0.0, -29.0], "fixed"), ("ice_wall", [-8.0, -27.0], "fixed"), ("ice_wall", [8.0, -27.0], "fixed"), ("warm_lantern", [-2.8, 9.4], "fixed"), ("warm_lantern", [2.8, 9.4], "fixed"),
               # B3 slide puzzle stoppers (game/jotunheim.js PZ.pillars: cell (c, r) -> x = -7.2 + 2.4 c, z = -13.4 - 2.4 r)
               ("frost_rune_pillar", [-4.8, -15.8], "fixed"), ("frost_rune_pillar", [-2.4, -20.6], "fixed"), ("frost_rune_pillar", [0.0, -15.8], "fixed"), ("frost_rune_pillar", [2.4, -13.4], "fixed"),
               ("frost_rune_pillar", [4.8, -13.4], "fixed"), ("frost_rune_pillar", [4.8, -20.6], "fixed"), ("frost_rune_pillar", [7.2, -13.4], "fixed")],
    "barrow2": [("ice_crystal_cluster", [-10.4, 4.0], "fixed"), ("ice_crystal_cluster", [10.4, 4.0], "fixed"), ("glow_ice_pool", [-5.6, 0.0], "fixed"), ("glow_ice_pool", [5.6, 0.0], "fixed"),
                ("ice_wall", [-7.0, -3.0], "fixed"), ("ice_wall", [7.0, -3.0], "fixed"), ("warm_lantern", [-2.8, 9.4], "fixed"), ("warm_lantern", [2.8, 9.4], "fixed"),
                ("shield_rack", [-9.4, -8.0], "fixed"), ("shield_rack", [9.4, -8.0], "fixed"), ("shield_rack", [-9.4, -13.0], "fixed"), ("shield_rack", [9.4, -13.0], "fixed"),
                ("glow_ice_pool", [-6.4, -21.0], "fixed"), ("glow_ice_pool", [6.4, -21.0], "fixed"), ("glow_ice_pool", [-6.4, -26.0], "fixed"), ("glow_ice_pool", [6.4, -26.0], "fixed"),
                ("frost_rune_pillar", [-4.4, -19.0], "fixed"), ("frost_rune_pillar", [4.4, -19.0], "fixed"), ("frost_rune_pillar", [-4.4, -24.0], "fixed"), ("frost_rune_pillar", [4.4, -24.0], "fixed"),
                ("cold_brazier", [0.0, -32.0], "fixed"), ("rune_standing_stone", [-9.0, -35.0], "fixed"), ("rune_standing_stone", [9.0, -35.0], "fixed"),
                ("rune_standing_stone", [-9.0, -39.0], "fixed"), ("rune_waystone", [-4.0, -36.4], "fixed"),   # the real waystone (was a rune_standing_stone stand-in) ("ice_wall", [8.0, -40.0], "fixed"), ("ice_crystal_cluster", [-10.4, -40.0], "fixed"),
                ("cold_brazier", [-6.0, -47.0], "fixed"), ("cold_brazier", [6.0, -47.0], "fixed"), ("frost_rune_pillar", [-9.4, -45.0], "fixed"), ("frost_rune_pillar", [9.4, -45.0], "fixed"),
                ("cold_brazier", [0.0, -52.4], "fixed")],
}


# Stonehollow and the Rime Caves: decor lamps (longhouse windows, rune stones, braziers) are dimmed in reach so they do not tint the few-colour giant sprites
# standing near them (check_scene colours: crop colours / source colours <= 2). The lights stay; only their reach shrinks.
LAMP_CAP = {"longhouse": 3.0, "rune_standing_stone": 3.2, "cold_brazier": 4.5, "warm_lantern": 4.0, "fur_stall": 3.0, "ice_lake": 3.5, "glow_ice_pool": 2.0, "frost_rune_pillar": 3.0, "ice_crystal_cluster": 3.0}

LAMP_CAP_AREA = {"jotunheim": LAMP_CAP, "rimecaves": LAMP_CAP, "barrow": LAMP_CAP, "barrow2": LAMP_CAP, "jt_hall": {**LAMP_CAP, "warm_lantern": 3.0}}   # the hall: diner2 sits 3.2 m from a lantern


def place(area):
    import base64, math
    from array import array
    sp = GAME / "areas" / area / "scene.json"; sc = json.loads(sp.read_text())
    pieces = json.loads((ST / "kit" / "kit.json").read_text())["pieces"]
    if not any(n in pieces for n, *_ in PLACE.get(area, [])): pass
    C = sc["collision"]; C.setdefault("base_data", C["data"])
    d = array("h"); d.frombytes(base64.b64decode(C["base_data"]))
    ox, oz, cl, W, H = C["origin"][0], C["origin"][1], C["cell"], C["w"], C["h"]
    sc["objects"] = [o for o in sc["objects"] if not o.get("jot_art") or o.get("fix1028")]  # keep hand-added Art fixes-1028 entries (they carry the installer tag too)
    sc["lamps"] = [l for l in sc["lamps"] if not l.get("jot_art") or l.get("fix1028")]  # keep hand-added Art fixes-1028 entries (they carry the installer tag too)
    g = sc["game"]
    keep = [(a["pos"][0], a["pos"][1], 1.6) for a in sc.get("actors", []) if "pos" in a]
    keep += [(v[0], v[1], 2.0) for v in g.get("spawns", {}).values()]
    for e in g.get("exits", []) + g.get("portals", []):
        r = e.get("rect")
        if r: keep.append(((r[0] + r[2]) / 2, (r[1] + r[3]) / 2, 2.4 + max(r[2] - r[0], r[3] - r[1]) / 2))
    keep += [(o["pos"][0], o["pos"][2], 1.4) for o in sc["objects"] if not o.get("walkable") and "scene_" not in o["glb"]]
    cam = sc["camera"].get("bounds")
    # phone-portrait view box around the start spawn (about +-6 m wide, 14 m deep at the default zoom): props go where
    # the arrival view shows them. The vault keeps its own room-by-room preferences (no box).
    st = g.get("spawns", {}).get("start")
    vbox = None if not st else (st[0] - 6.0, st[1] - 16.0, st[0] + 6.0, st[1] + 1.0)
    # never hide a character: no tall prop in a band in front of (camera side, +z) an actor or spawn
    front = [(a["pos"][0], a["pos"][1]) for a in sc.get("actors", []) if "pos" in a] + [(v[0], v[1]) for v in g.get("spawns", {}).values()]

    def cells(x, z, hw, hd):
        for j in range(int((z - hd - oz) / cl), int((z + hd - oz) / cl) + 1):
            for i in range(int((x - hw - ox) / cl), int((x + hw - ox) / cl) + 1):
                yield i, j

    nonlocal_tall = [False]

    def ok(x, z, hw, hd):
        if vbox and not (vbox[0] < x < vbox[2] and vbox[1] < z < vbox[3]):
            return None
        if nonlocal_tall[0] and any(abs(x - fx_) < hw + 0.8 and 0 < z - fz < 2.0 for fx_, fz in front):
            return None
        if cam and not (cam[0] + 1 < x < cam[2] - 1 and cam[1] + 1 < z < cam[3] - 1):
            return None
        hs = []
        for i, j in cells(x, z, hw + 0.5, hd + 0.5):
            if not (0 <= i < W and 0 <= j < H) or d[j * W + i] == -32768: return None
            hs.append(d[j * W + i])
        if max(hs) - min(hs) > 6: return None
        if any(math.hypot(x - kx, z - kz) < kr + max(hw, hd) for kx, kz, kr in keep): return None
        return hs[len(hs) // 2] / 100

    for name, (px, pz), *fixed in PLACE.get(area, []):
        extra = next((f for f in fixed if isinstance(f, dict)), {}); fixed = [f for f in fixed if not isinstance(f, dict)]
        if name not in pieces: print(f"  {area}: no kit piece {name} yet"); continue
        pc = pieces[name]; hw, hd = pc["size"][0] / 2, pc["size"][2] / 2
        if name == "elf_archway": hw *= 0.6   # a thin open arch: its posts need room, the span does not
        nonlocal_tall[0] = pc["size"][1] > 1.2
        spot = None
        if fixed:   # hand-placed against the side walls (the vault corridor is too narrow for the search)
            i_, j_ = int((px - ox) / cl), int((pz - oz) / cl)
            spot = (px, max(0, d[j_ * W + i_]) / 100, pz)
        for r in ([] if spot else [0] + [x * 0.5 for x in range(1, 30)]):
            for k in range(max(1, int(r * 8))):
                a = 2 * math.pi * k / max(1, int(r * 8)); x, z = round(px + r * math.cos(a), 2), round(pz + r * math.sin(a), 2)
                y = ok(x, z, hw, hd)
                if y is not None: spot = (x, y, z); break
            if spot: break
        if not spot: print(f"  {area}: no spot for {name}"); continue
        x, y, z = spot
        o = {"glb": f"public/art/kit/{pc['file']}", "pos": [x, y, z], "rot": 0, "jot_art": True}
        if name in WALK: o.update(walkable=True, cast=False)
        if extra.get("pz"): o["pz"] = extra["pz"]
        if extra.get("hidden"): o["hidden"] = True
        sc["objects"].append(o)
        keep.append((x, z, max(hw, hd) + 0.6))
        if name not in WALK and name not in NOBLOCK:
            for i, j in cells(x, z, hw * 0.8, hd * 0.8): d[j * W + i] = -32768
        mk = pc["markers"]
        for lp in ([] if extra.get("hidden") else mk.get("lamps", [])):   # a hidden piece (cairn_toppled) is lit at runtime when the game shows it
            sc["lamps"].append({"pos": [x + lp[0], y + lp[1], z + lp[2]], "range": min(mk.get("lamp_range", 5.0), LAMP_CAP_AREA[area].get(name, 9.0)) if area in LAMP_CAP_AREA else mk.get("lamp_range", 5.0), "kind": name,
                                "color": mk.get("lamp_color", "#a45cf0"), "fixed": mk.get("lamp_fixed", 0.5), "jot_art": True})
        print(f"  {area}: {name} at ({x}, {z})")
    C["data"] = base64.b64encode(d.tobytes()).decode()
    sp.write_text(json.dumps(sc, separators=(",", ":")) if "\n" not in sp.read_text()[:200] else json.dumps(sc, indent=1))




def stonefrost(area):
    """Stonefrost II / III fx under this area's gamefx atlas (48 px cells). Crop-at-mark + append: re-running never grows the atlas."""
    src = ST / "gamefx" / "stonefrost_fx.json"
    if not have(src): return False
    sc = json.loads((GAME / "areas" / area / "scene.json").read_text())
    if not sc.get("gamefx"): return False
    jp, ip = GAME / "areas" / area / sc["gamefx"]["json"], GAME / "areas" / area / sc["gamefx"]["image"]
    meta, sj = json.loads(jp.read_text()), json.loads(src.read_text())
    assert meta["cell"] == sj["cell"], "cell size mismatch"
    base = Image.open(ip).convert("RGBA"); h0 = meta.get("stonefrost_from", base.height)
    base = base.crop((0, 0, base.width, h0)); add = Image.open(ST / "gamefx" / sj["image"]).convert("RGBA")
    out = Image.new("RGBA", (max(base.width, add.width), h0 + add.height), (0, 0, 0, 0)); out.paste(base, (0, 0)); out.paste(add, (0, h0)); out.save(ip)
    row0 = h0 // meta["cell"]
    for k in list(meta["effects"]):   # rows appended after the mark (the Caldera school's) were cropped away: drop them, the school is re-applied below
        if meta["effects"][k]["row"] >= row0: del meta["effects"][k]
    meta.pop("caldera_from", None)
    for k, e in sj["effects"].items():
        e = {kk: vv for kk, vv in e.items() if kk not in ("frame_list", "strip")}; e["row"] += row0; meta["effects"][k] = e
    meta.setdefault("cast_sets", {}).update(sj.get("cast_sets", {}))
    meta["stonefrost_from"] = h0; meta["size"] = [out.width, out.height]
    jp.write_text(json.dumps(meta, indent=1))
    try:   # [MUSPELHEIM-2] the Caldera school rows sit after Stonefrost's: re-append them (musp_art.school, crop-at-mark, idempotent)
        sys.path.insert(0, str(Path(__file__).resolve().parent)); import musp_art; musp_art.school(area)
    except ImportError:
        pass
    return True


def main():
    if not (STAGING / "READY.txt").exists() and not FORCE:
        print("jot_art: /workspace/hearthmoor-staging/art/jotunheim/READY.txt is missing: the art pack is not ready. Nothing done (use --force for a dry look).")
        return 0
    copy_staging()
    for a in ([] if SF_ONLY else AREAS):
        d = GAME / "areas" / a
        if not (d / "scene.json").exists():
            print(f"{a}: not built yet (areas/{a}/scene.json missing): skipped"); continue
        sprites(a)
        if (ST / "kit" / "kit.json").exists(): kit(a); place(a)
        fx = gamefx(a)
        sf = stonefrost(a)
        print(f"{a}: sprites + kit + props{' + gamefx' if fx else ' (no gamefx atlas)'}{' + stonefrost' if sf else ''}")
    if "--stonefrost-all" in sys.argv:   # every other built area with a gamefx atlas (run after build.py's installers)
        done = [a.name for a in sorted((GAME / "areas").iterdir()) if (a / "scene.json").exists() and stonefrost(a.name)]
        print("stonefrost: " + ", ".join(done))
    return 0


if __name__ == "__main__":
    sys.exit(main())
