"""[NIFLHEIM] Art installer for the Niflheim areas (realm-niflheim branch). Modeled on nifl_art.py / jot_art.py / svart_art.py / alf_art.py.

Waits on /workspace/hearthmoor-staging/art/niflheim/READY.txt (without it: prints a message and does nothing). With it, wires the staging art in
games/hearthmoor/art/niflheim/ (copied from the staging pack) into the BUILT Niflheim areas without re-assembling:
  sprites  frost-kin / Ice Warden / boss / rare sheets and Hrefna become extra sheets of each area's actors.json (every sheet the pack ships in sprite/ and pets/)
  kit      staging .glb files are copied in; a name clash takes the staging piece
  gamefx   staging nf_fx rows are appended under the area's gamefx atlas (48 px cells), plus the plaza's quest_mark / quest_turnin glyphs; then the SHARED rows every built
           area carries are re-applied in the documented order: jot_art Stonefrost II / III, then musp_art's Caldera school (both crop-at-mark + append, idempotent)
Props: PLACE puts staging kit pieces into scene.json (objects + lamps + collision blockers) from the pack's layout metadata. Only adds or overwrites files: it never deletes
anything (only its own earlier placements, marked "nifl_art", are re-made). The area's original gamefx atlas is kept once as gamefx.base.(png|json); every run rebuilds from that. Idempotent.
LAMP_CAP: the neon-blue cold-fire lamps (lanterns, braziers, pools) are dimmed in reach so they do not tint the few-colour frost-kin sprites standing near them (check_scene colours);
the lights stay, only their reach shrinks. Add a piece to LAMP_CAP when check_scene's colour check names it. Lamp dimming is the lever for passing lighting; never loosen a check.
NEON: scoped allow-lists only. This script NEVER edits tools/check-sprite/check_sprite.py and never widens any list. `neon_audit()` runs on every sheet before it is installed:
off-palette (neon) colours are allowed only for the roles and hexes in NIFL_NEON_SCOPE (mirrors NIFL_NEON_ALLOW in check_sprite.py; empty until the art README's "Neon flag" + a ruling name
them; expected: Hrefna's lantern glow at most). A role outside the scope that carries off-palette colours is NOT installed (its palette-safe `_safe` twin is installed instead when
the pack ships one; otherwise the sheet is skipped with a message).

STATUS: SCAFFOLD (chunk 1, Oct 18 2026). The pack's real sheet / role / kit / layout names are not known yet: the tables below (FOLK, GIANTS, FOES, SHEETS, TOWNS, LAYOUT_AREA, FX_FILE)
are the story doc's roles with guessed file names; fix them from the art README when READY.txt lands. Missing staging files are SKIPPED with a message, never an error.

usage: python3 tools/hearthmoor/nifl_art.py [--force] [area ...]      (then: cd games/hearthmoor && python3 -c "import build; build.write_pwa()")
"""
import json, shutil, sys
from pathlib import Path
from PIL import Image

GAME = Path(__file__).resolve().parents[2] / "games" / "hearthmoor"
STAGING = Path("/workspace/hearthmoor-staging/art/niflheim")
ST = GAME / "art" / "niflheim"
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
FORCE = "--force" in sys.argv
PLANNED = ["niflheim", "nf_home", "iceglow", "frozenspire", "frozenspire2", "frozen_rift"]   # story 2.1; the Spire is two areas (like clockdeep / caldera), see NIFLHEIM_PROGRESS.md
AREAS = ARGS or PLANNED

# stock actor role (what the area spec's actors use) -> the pack's role, per area (re-pointed only if the area's actors.json has that stock role).
TOWNS = {
    "niflheim": {"innkeeper": "frostspeaker", "dwarftrader": "nf_trader", "wispcatcher": "elkman", "elffolk": "archivist", "elffolk2": "gatewright"},   # the two villagers wear Vigdis' / Halvard's looks (the pack has no generic villager)
    "nf_home": {"lanternseller": "hrefna", "elffolk": "archivist"},
    "iceglow": {"innkeeper": "frostspeaker"},
    "frozenspire": {}, "frozenspire2": {"elffolk": "archivist"}, "frozen_rift": {},
}
FOLK = ["gatewright", "frostspeaker", "veyra", "eira", "nf_trader", "elkman", "archivist", "brisa"]   # nf_folk.json: 1x (veyra 1.2x)
FOES = ["frost_spirit", "mist_stalker", "ice_golem", "frost_wraith", "ice_warden"]
SHEETS = {  # sheet name -> (staging json, {area role: staging role}); every area gets these
    "nffolk": (ST / "sprite" / "nf_folk.json", {r: r for r in FOLK}),
    "nfenemy": (ST / "sprite" / "nf_enemies.json", {r: r for r in FOES}),
    "nfhrefna": (ST / "sprite" / "nf_hrefna.json", {"hrefna": "hrefna"}),   # the companion (no pet in this realm): role `hrefna`, follows with idle / walk, casts ice_lance / mist_veil
}
IMAGE = {}   # sheet -> staging png when it is not the json's own image
ELITES = ("nfelite", (ST / "sprite" / "nf_elites.json", {"brisa_mini": "brisa_mini", "mistalpha": "mistalpha", "spiritprime": "spiritprime", "kael_bat": "kael_bat"}))
EXTRA = {    # sheets only where the fight / scene is (their own frame size)
    "niflheim": {ELITES[0]: ELITES[1]},   # Brisa's trial at the hub
    "iceglow": {ELITES[0]: ELITES[1]},    # the two rares
    "frozenspire": {ELITES[0]: ELITES[1], "boss_colossus": (ST / "sprite" / "boss_colossus.json", {"colossus": "colossus", "colossus_p2": "colossus_p2", "colossus_p3": "colossus_p3"})},   # Brisa mini at F2, the 6x ice golem at F5 (not plate)
    "frozenspire2": {ELITES[0]: ELITES[1], "boss_kael": (ST / "sprite" / "boss_kael.json", {"kael": "kael", "kael_p3": "kael_p3"}),   # 5.5x black-iron plate
                     "boss_veyra": (ST / "sprite" / "boss_veyra.json", {"veyra_clone": "veyra_clone"})},                             # F4's mist clone lives in frozenspire (below); F6's Veyra is the 1.2x folk NPC
    "frozen_rift": {ELITES[0]: ELITES[1], "boss_veyra": (ST / "sprite" / "boss_veyra.json", {r: r for r in ("veyra_p1", "veyra_p2", "veyra_p3", "veyra_p4", "veyra_clone")})},   # 5x / 5x / 6x / 5x + the clone: separate roles in ONE sheet (decision 1)
}
EXTRA["frozenspire"]["boss_veyra"] = (ST / "sprite" / "boss_veyra.json", {"veyra_clone": "veyra_clone"})   # F4: mist clones (the real door is the one with breath and shadow)
EXTRA["frozenspire2"].pop("boss_veyra")
# Scoped neon (art README "Neon flag", lead ruling): EMPTY until the README names it. Mirrors NIFL_NEON_ALLOW in check_sprite.py, never wider.
NIFL_NEON_SCOPE = {}
FX_DROP = {"nf_home": {("pool_teal", -2.0, 5.4), ("pool_teal", 2.0, 5.4)}}   # per-area placed decals left out when check_scene no_bloom names them (the Quiet Shore's two lake-edge teal pools clip the snow at 255)
FX_SKIP = set()   # (Oct 19 2026: veyra_shadow redrawn lighter, dark teal + ash grey, and back in the atlases)   # effects whose crop never matches the atlas frame (check_scene gamefx_sharp): the pack keeps them, the area atlases do not list them
FX_FILE = ("gamefx", "nf_fx.json")   # staging gamefx rows: ST / "gamefx" / "nf_fx.json"


def neon_audit(src, sm, img_name, roles):
    """off-palette colours per staging role of a sheet -> {role: set(hex)}; only roles in `roles` (staging names) are looked at"""
    sys.path.insert(0, str(GAME.parents[1]))
    from hd2d_common import load_biome  # noqa: E402
    pal = set(load_biome(sm.get("biome", "cozy-village"))["colors"].values())
    im = Image.open(src.parent / img_name).convert("RGBA"); px = im.load(); fw, fh = sm["frame"]; bad = {}
    for sr in roles:
        r = sm["roles"].get(sr)
        if not r: continue
        got = set()
        for fr in r.get("frames", []):
            for y in range(fh):
                for x in range(fw):
                    p = px[fr["x"] + x, fr["y"] + y]
                    if p[3] == 255:
                        h = "#%02x%02x%02x" % p[:3]
                        if h not in pal: got.add(h)
        if got - NIFL_NEON_SCOPE.get(sr, set()): bad[sr] = got - NIFL_NEON_SCOPE.get(sr, set())
    return bad

def have(p):
    if not Path(p).exists():
        print(f"  skip (not in the pack yet): {Path(p).relative_to(GAME) if str(p).startswith(str(GAME)) else p}")
        return False
    return True


def copy_staging():
    """Copy the staging pack into art/niflheim/ (add / overwrite only)."""
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
        bad = neon_audit(src, sm, IMAGE.get(nm, sm["image"]), set(roles.values()))
        if bad:
            print(f"  {nm}: NOT installed, off-palette colours outside NIFL_NEON_SCOPE: " + "; ".join(f"{r} {sorted(h)[:4]}" for r, h in bad.items()))
            continue
        shutil.copy2(src.parent / IMAGE.get(nm, sm["image"]), d / f"{nm}.png")
        out = {k: sm[k] for k in ("tool", "biome", "frame", "pivot", "ground_row", "facings", "anims", "cols", "size")}
        out["image"] = f"{nm}.png"; out["roles"] = {}
        # stock stand-in roles of this area point at the pack's roles (only roles the area's actors.json has)
        roles = {**roles, **{k: v for k, v in TOWNS.get(area, {}).items() if v in sm["roles"] and k in m["roles"]}}
        for ar, sr in roles.items():
            if sr not in sm["roles"]: print(f"  {nm}: no staging role {sr}"); continue
            r = sm["roles"][sr]
            out["roles"][ar] = {k: v for k, v in r.items() if k != "frames"}
            prev = m["roles"].get(ar, {})
            m["roles"][ar] = {"sheet": nm, "row": r["row"], "kind": r.get("kind", prev.get("kind", "creature")),
                              "anims": r.get("anims", ["idle", "walk"]), "desc": r.get("desc", ""),
                              **({"enemy": True} if r.get("enemy") or prev.get("enemy") else {}),
                              **({"follower": True} if nm == "nfhrefna" else {})}
        (d / f"{nm}.json").write_text(json.dumps(out, indent=1))
        m["sheets"][nm] = {"json": f"{nm}.json", "image": f"{nm}.png"}
    mp.write_text(json.dumps(m, indent=1))


def kit(area):
    d = GAME / "areas" / area / "public" / "art" / "kit"
    for g in sorted((ST / "kit").glob("*.glb")):
        shutil.copy2(g, d / g.name)


def gamefx(area):
    if not have(ST / "gamefx" / "nf_fx.json"): return False
    d = GAME / "areas" / area / "public" / "art" / "gamefx"
    if not (d / "gamefx.json").exists() and not (d / "gamefx.base.json").exists():
        # no atlas yet (wispwood): start from an empty base so the staging rows are the whole atlas, and point the scene at it
        d.mkdir(parents=True, exist_ok=True)
        sj = json.loads((ST / "gamefx" / "nf_fx.json").read_text())
        (d / "gamefx.base.json").write_text(json.dumps({k: sj[k] for k in ("tool", "biome", "seed", "cell", "cast_sets", "cycle")} | {"image": "gamefx.png", "size": [0, 0], "effects": {}}))
        Image.new("RGBA", (sj["cell"], sj["cell"]), (0, 0, 0, 0)).save(d / "gamefx.base.png")   # one blank row
        sp = GAME / "areas" / area / "scene.json"; sc = json.loads(sp.read_text())
        sc["gamefx"] = {"image": "public/art/gamefx/gamefx.png", "json": "public/art/gamefx/gamefx.json"}
        sp.write_text(json.dumps(sc, separators=(",", ":")))
    bj, bp = d / "gamefx.base.json", d / "gamefx.base.png"
    if not bj.exists():
        shutil.copy2(d / "gamefx.json", bj); shutil.copy2(d / "gamefx.png", bp)
    base, sj = json.loads(bj.read_text()), json.loads((ST / "gamefx" / "nf_fx.json").read_text())
    assert base["cell"] == sj["cell"], "cell size mismatch"
    bi, si = Image.open(bp).convert("RGBA"), Image.open(ST / "gamefx" / sj["image"]).convert("RGBA")
    # the ! / ? quest-marker glyphs (quest_mark, quest_turnin) copied from the plaza atlas (same 48 px cell): the realm areas' atlases had none,
    # so the Niflheim NPC markers (Gudrun, Hrefna, Tove...) would spawn nothing
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
        if k in FX_SKIP: continue
        e = {kk: vv for kk, vv in e.items() if kk not in ("frame_list", "strip")}
        e["row"] = e["row"] + off
        base["effects"][k] = e
    base["size"] = [im.width, im.height]
    (d / "gamefx.json").write_text(json.dumps(base, indent=1))
    return True


# props placed per area: (piece, preferred [x, z], "fixed"?); the spot is searched outward on flat, walkable, uncrowded ground unless "fixed".
# Coordinates are the art README layout (metadata/niflheim_layout.json), moved where the area spec's own terrain (plateau + stair come
# from the spec, so the kit's stone_ledge / stone_stair are not placed) or an actor stands. Keep-clear: nothing on the stair + 1 m, 2.5 m in
# front of longhouse doors, 1.5 m around the from_bifrost spawn.

# The props come from the pack's layout (metadata/niflheim_layout.json). The area spec owns the terrain (its terrace + stair replace the kit's frost_ledge / frost_stair, like
# Jotunheim's plateau), so those two are not placed; floor tiles are laid only on flat ground (not over a terrace or stair). WALK = flat, walkable, never casts shadows.
WALK = {"snow_floor", "ice_floor", "ice_lake", "rime_bridge", "crown_platform"}
LAYOUT_AREA = {"niflheim": "niflheim", "nf_home": "nf_home", "iceglow": "iceglow"}
SPEC_TERRAIN = {"frost_ledge", "frost_stair"}
NO_TILE = {"niflheim": (-4.6, -10.0, 4.6, -4.8), "nf_home": (-3.6, -8.0, 3.6, -2.2), "iceglow": (-3.6, -8.4, 3.6, -3.6)}   # terrace + stair footprints (+ a margin): no floor tiles over them
EXTRA_PLACE = {}   # area -> [(piece, [x, z], "fixed", {rot, y})] added after the layout (hand-placed extras)
PIECE_MOVE = {}    # (area, piece, x, z) -> (x, z): a prop moved off an actor / spawn / lamp (check_scene), rounded to 0.1
NOCAST = set()     # (area, piece): its shadow fell across an NPC (check_scene atlas corr)

# The Spire: rooms F1-F5 stack north in `frozenspire`, F6-F10 in `frozenspire2` (14 m pitch, 8 m walk half-width); the pack's room layouts (spire_fN) are shifted by the room's z
# centre. Side walls / floors are regenerated for the whole corridor (the pack's per-room back walls would close the corridor); the spec owns each room's ledge + stair.
SPIRE_ROOMS = {
    "frozenspire": [("spire_f1", 0.0), ("spire_f2", -14.0), ("spire_f3", -28.0), ("spire_f4", -42.0), ("spire_f5", -56.0)],
    "frozenspire2": [("spire_f6", 0.0), ("spire_f7", -14.0), ("spire_f8", -28.0), ("spire_f9", -42.0), ("spire_f10", -56.0)],
    "frozen_rift": [("frozen_rift", 0.0)],
}
SPIRE_TOP = {"frozenspire": -64.0, "frozenspire2": -64.0, "frozen_rift": -9.0}   # north end: where the corridor's back wall goes
SPIRE_NO_TILE = {   # per area: rects (x0, z0, x1, z1) of terraces + stair footprints, from the spec generator (areas/src/gen/gen_spire.py)
}
SPIRE_X = 7.9   # side wall line (ice_wall pieces), the spec's own wall blocks sit at 8.2


def _spire_notile(area):
    p = GAME / "areas" / "src" / f"{area}.json"
    if not p.exists(): return []
    sp = json.loads(p.read_text()); out = []
    for t in sp.get("terraces", []):
        if t["name"].startswith("wall"): continue
        r = t["rect"]; out.append((r[0] - 0.4, r[1] - 0.4, r[2] + 0.4, r[3] + 0.4))
    for st in sp.get("stairs", []):
        w = st["width"] / 2 + 0.4; out.append((st["x"] - w, st["z_top"] - 0.4, st["x"] + w, st["z_top"] + 4.2))
    return out


def spire_layout(area):
    out = []
    lay = json.loads((ST / "metadata" / "niflheim_layout.json").read_text())
    rooms = SPIRE_ROOMS[area]; nt = _spire_notile(area)
    zs = [zc for _, zc in rooms]; z_hi, z_lo = max(zs) + 8.0, SPIRE_TOP[area]
    if area == "frozen_rift":   # the Crown of Ice: a round platform, four portals, the landing + stair come from the spec
        PORT = [([0.0, -4.8], 0.0), ([4.8, 0.0], 1.5707963267948966), ([-4.8, 0.0], 4.71238898038469), ([-3.4, 4.8], 3.141592653589793)]   # the pack's 6.2 m ring is off the 10.4 m platform: pulled onto it (the south one beside the stair)
        for p in lay["frozen_rift"]["pieces"]:
            name, (x, y, z) = p[0], p[1]; rot = p[2] if len(p) > 2 else 0
            if name in SPEC_TERRAIN: continue
            if name == "frozen_portal": (x, z), rot = PORT.pop(0)
            ex = {**({"rot": rot} if rot else {})}
            if name == "crown_platform": ex["y"] = 1.8 - 0.55   # its top (0.55 m) meets the spec's 1.8 m crown
            out.append((name, [x, z], "fixed", ex))
        return out
    for key, zc in rooms:
        for p in lay[key]["pieces"]:
            name, (x, y, z) = p[0], p[1]; rot = p[2] if len(p) > 2 else 0
            if name in SPEC_TERRAIN or name == "ice_wall" or name in ("ice_floor", "snow_floor"): continue
            ex = {"rot": rot} if rot else {}
            if name in ("glow_orb_chain",): ex["y"] = y
            if (area, name, round(x, 1), round(z + zc, 1)) in PIECE_MOVE: x, z = PIECE_MOVE[(area, name, round(x, 1), round(z + zc, 1))]; z -= zc
            out.append((name, [x, z + zc], "fixed", ex))
    z = z_hi
    while z > z_lo - 0.1:   # side walls, the full length
        for sx, rot in ((-SPIRE_X, 1.5707963267948966), (SPIRE_X, 1.5707963267948966)):
            out.append(("ice_wall", [sx, z], "fixed", {"rot": rot}))
        z -= 2.0
    for x in range(-8, 9, 2):   # the back wall (north end)
        out.append(("ice_wall", [float(x), z_lo - 0.9], "fixed", {}))
    zz = z_hi - 1.0
    while zz > z_lo + 0.4:      # floor tiles, flat ground only (off the rooms' ledges + stairs)
        for x in range(-7, 8, 2):
            if any(r[0] <= x <= r[2] and r[1] <= zz <= r[3] for r in nt): continue
            out.append(("ice_floor", [float(x), zz], "fixed", {}))
        zz -= 2.0
    return out


def _rooms(area):
    return SPIRE_ROOMS.get(area) or [(LAYOUT_AREA.get(area), 0.0)]


def layout_lights(area):
    lp = ST / "metadata" / "niflheim_layout.json"
    if not lp.exists(): return []
    lay = json.loads(lp.read_text()); out = []
    for key, zc in _rooms(area):
        if key not in lay: continue
        for (p, col, rng, fix) in lay[key].get("extra_lights", []):
            out.append(((p[0], p[1], p[2] + zc), col, rng, fix))
    return out


FX_JS = GAME / "game" / "niflheim_fx.js"


def fx_table():
    """game/niflheim_fx.js: NF_FX[area] = [[effect, [x, z], dy]]: the pack's decals (pools, mist, fog, rune pulse; dy 0) and billboards (flames, orbs, vines, fireflies) per area,
    Spire rooms shifted by their z centre. Generated: do not edit (rerun nifl_art.py)."""
    lp = ST / "metadata" / "niflheim_layout.json"
    if not lp.exists(): return
    lay = json.loads(lp.read_text()); tab = {}
    for area in PLANNED:
        rows = []
        for key, zc in _rooms(area):
            if key not in lay: continue
            for d in lay[key].get("decals", []):
                if (d[0], round(d[1][0], 2), round(d[1][1] + zc, 2)) in FX_DROP.get(area, ()): continue
                rows.append([d[0], [round(d[1][0], 2), round(d[1][1] + zc, 2)], 0])
            for b in lay[key].get("bills", []):
                n, (x, y, z) = b[0], b[1]
                dy = 1.9 if n in ("cold_flame", "violet_flame") else y
                rows.append([n, [round(x, 2), round(z + zc, 2)], round(dy, 2)])
        tab[area] = rows
    body = ",\n".join(f"  {a}: {json.dumps(r, separators=(',', ':'))}" for a, r in tab.items())
    FX_JS.write_text("// GENERATED by tools/hearthmoor/nifl_art.py (fx_table): the pack's animated pools / flames / motes per area. Do not edit.\nexport const NF_FX = {\n" + body + ",\n};\n")


def layout_place(area):
    if area in SPIRE_ROOMS: return spire_layout(area) + EXTRA_PLACE.get(area, [])
    la = LAYOUT_AREA.get(area)
    lp = ST / "metadata" / "niflheim_layout.json"
    if not la or not lp.exists(): return EXTRA_PLACE.get(area, [])
    out = []
    nt = NO_TILE.get(area)
    for p in json.loads(lp.read_text())[la]["pieces"]:
        name, (x, y, z) = p[0], p[1]; rot = p[2] if len(p) > 2 else 0
        if name in SPEC_TERRAIN: continue
        if (area, name, round(x, 1), round(z, 1)) in PIECE_MOVE: x, z = PIECE_MOVE[(area, name, round(x, 1), round(z, 1))]
        if name in ("snow_floor", "ice_floor") and nt and nt[0] <= x <= nt[2] and nt[1] <= z <= nt[3]: continue
        ex = {}
        if rot: ex["rot"] = rot
        if name in ("glow_orb_chain",): ex["y"] = y   # hanging pieces keep the layout height
        out.append((name, [x, z], "fixed", ex))
    return out + EXTRA_PLACE.get(area, [])


# Decor lamps (lava, forge windows, braziers, glass orbs) are dimmed in reach so they do not tint the few-colour ember-kin sprites standing near them (check_scene colours:
# crop colours / source colours <= 2). The lights stay; only their reach shrinks. Tune from check_scene's colour check (add a piece when it names it).
LAMP_CAP = {"cold_lantern": 3.0, "lantern_post": 3.0, "cold_brazier": 2.8, "glow_pool": 3.0, "ice_arch": 3.2, "aurora_lamp": 3.0, "rune_gate": 2.6, "glow_orb": 2.4, "shrine_lamp": 2.6,
            "rune_pillar": 2.5, "fish_stall": 3.0, "elk_paddock": 3.0, "grave_stone": 2.6, "ashmantle_house": 3.0, "spire_door": 4.0, "freeze_core": 3.5, "frozen_portal": 4.0}   # GUESSED piece names
LAMP_CAP["ice_lake"] = 2.2   # the two lake-edge pools in the Quiet Shore blew the snow floor to 255 (check_scene no_bloom, night)
NO_LIGHT = {("nf_home", "ice_lake")}   # lamps kept as glow sprites but not real point lights (the engine gives the first 7-8 lamps real lights; the lake pair sat first and blew the snow to 255: check_scene no_bloom)
EXTRA_CAP = {"nf_home": 3.5}   # the pack's extra pools (not the ambient fill, range >= 9) capped per area when check_scene's no_bloom names one
LAMP_CAP_AREA = {a: dict(LAMP_CAP) for a in PLANNED}
# per-area tightening goes here when check_scene's colour check (crop colours / source colours <= 2) names a lamp beside a few-colour sprite.


def place(area):
    import base64, math
    from array import array
    sp = GAME / "areas" / area / "scene.json"; sc = json.loads(sp.read_text())
    pieces = json.loads((ST / "kit" / "kit.json").read_text())["pieces"]
    NOBLOCK = {n for n, p in pieces.items() if not p.get("blockers")} | WALK   # kit.json blockers [] = walkable / hanging: no blocker
    C = sc["collision"]; C.setdefault("base_data", C["data"])
    d = array("h"); d.frombytes(base64.b64decode(C["base_data"]))
    ox, oz, cl, W, H = C["origin"][0], C["origin"][1], C["cell"], C["w"], C["h"]
    sc["objects"] = [o for o in sc["objects"] if not o.get("nifl_art") or o.get("fix1028")]  # keep hand-added Art fixes-1028 entries (they carry the installer tag too)
    sc["lamps"] = [l for l in sc["lamps"] if not l.get("nifl_art") or l.get("fix1028")]  # keep hand-added Art fixes-1028 entries (they carry the installer tag too)
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

    for name, (px, pz), *fixed in layout_place(area):
        extra = next((f for f in fixed if isinstance(f, dict)), {}); fixed = [f for f in fixed if not isinstance(f, dict)]
        if name not in pieces: print(f"  {area}: no kit piece {name} yet"); continue
        pc = pieces[name]; hw, hd = pc["size"][0] / 2, pc["size"][2] / 2
        rot = extra.get("rot", 0)
        if abs(abs(rot) - math.pi / 2) < 0.1: hw, hd = hd, hw   # a quarter turn swaps the footprint
        nonlocal_tall[0] = pc["size"][1] > 1.2
        spot = None
        if fixed:   # hand-placed against the side walls (the vault corridor is too narrow for the search)
            i_, j_ = int((px - ox) / cl), int((pz - oz) / cl)
            gy = max(0, d[j_ * W + i_]) / 100 if (0 <= i_ < W and 0 <= j_ < H) else 0.0   # pieces on the wall line may sit off the collision grid
            spot = (px, extra["y"] if "y" in extra else gy, pz)
        for r in ([] if spot else [0] + [x * 0.5 for x in range(1, 30)]):
            for k in range(max(1, int(r * 8))):
                a = 2 * math.pi * k / max(1, int(r * 8)); x, z = round(px + r * math.cos(a), 2), round(pz + r * math.sin(a), 2)
                y = ok(x, z, hw, hd)
                if y is not None: spot = (x, y, z); break
            if spot: break
        if not spot: print(f"  {area}: no spot for {name}"); continue
        x, y, z = spot
        o = {"glb": f"public/art/kit/{pc['file']}", "pos": [x, y, z], "rot": rot, "nifl_art": True}
        if name in WALK: o.update(walkable=True, cast=False)
        if (area, name) in NOCAST: o["cast"] = False   # its shadow fell across the NPC in front of it (check_scene atlas corr)
        if extra.get("pz"): o["pz"] = extra["pz"]
        if extra.get("hidden"): o["hidden"] = True
        sc["objects"].append(o)
        keep.append((x, z, max(hw, hd) + 0.6))
        if name not in WALK and name not in NOBLOCK:
            for i, j in cells(x, z, hw * 0.8, hd * 0.8):
                if 0 <= i < W and 0 <= j < H: d[j * W + i] = -32768   # off-grid cells (the wall line) are already solid
        mk = pc["markers"]
        for lp in ([] if extra.get("hidden") else mk.get("lamps", [])):   # a hidden piece (cairn_toppled) is lit at runtime when the game shows it
            sc["lamps"].append({"pos": [x + lp[0], y + lp[1], z + lp[2]], "range": min(mk.get("lamp_range", 5.0), LAMP_CAP_AREA[area].get(name, 9.0)) if area in LAMP_CAP_AREA else mk.get("lamp_range", 5.0), "kind": name,
                                "color": mk.get("lamp_color", "#3fb8ff"), "fixed": mk.get("lamp_fixed", 0.5), "nifl_art": True, **({"light": False} if (area, name) in NO_LIGHT else {})})
        print(f"  {area}: {name} at ({x}, {z})")
    for (lx, ly, lz), col, rng, fix in layout_lights(area):   # the pack's extra pools of light (cold blue, teal, aurora, violet and the warm lantern / window every 6-8 m)
        if rng < 9.0: rng = min(rng, EXTRA_CAP.get(area, 99.0))
        sc["lamps"].append({"pos": [lx, ly, lz], "range": rng, "color": col, "fixed": fix, "kind": "nf_extra", "nifl_art": True})
    C["data"] = base64.b64encode(d.tobytes()).decode()
    sp.write_text(json.dumps(sc, separators=(",", ":")) if "\n" not in sp.read_text()[:200] else json.dumps(sc, indent=1))





# ---- shared rows every built area carries (documented order: this pack's nf_fx rows, then Stonefrost II / III, then the Caldera school)
def _shared(area):
    """jot_art's Stonefrost II / III, then musp_art's Caldera school, on this area's atlas (gamefx() rebuilt it from its base). Both are crop-at-mark + append: idempotent.
    The two modules read sys.argv at import, so they are imported with a neutral argv."""
    argv, sys.argv = sys.argv, [sys.argv[0]]
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import jot_art, musp_art
    finally:
        sys.argv = argv
    sf = jot_art.stonefrost(area)
    cs = musp_art.school(area)
    return sf, cs


def main():
    if not (STAGING / "READY.txt").exists() and not FORCE:
        print("nifl_art: /workspace/hearthmoor-staging/art/niflheim/READY.txt is missing: the art pack is not ready. Nothing done (use --force for a dry look).")
        return 0
    copy_staging()
    fx_table()
    for a in AREAS:
        d = GAME / "areas" / a
        if not (d / "scene.json").exists():
            print(f"{a}: not built yet (areas/{a}/scene.json missing): skipped"); continue
        sprites(a)
        if (ST / "kit" / "kit.json").exists(): kit(a); place(a)
        fx = gamefx(a)
        sf, cs = _shared(a) if fx else (False, False)
        print(f"{a}: sprites + kit + props{' + gamefx' if fx else ' (no gamefx atlas)'}{' + stonefrost' if sf else ''}{' + caldera school' if cs else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
