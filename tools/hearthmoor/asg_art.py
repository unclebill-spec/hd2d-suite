"""[ASGARD] Art installer for the Asgard areas (realm-asgard branch): Goldspire (asgard, gs_hall, gs_temple) and the Gilded Reliquary (reliquary G1-G5, reliquary2 G6-G9).
Copied from nifl_art.py (same flow, same rules). Waits on /workspace/hearthmoor-staging/art/asgard/READY.txt (without it: prints a message and does nothing). With it, wires the
staging art in games/hearthmoor/art/asgard/ (copied from the staging pack) into the BUILT Asgard areas without re-assembling:
  sprites  as_folk / as_sigrun / as_enemies / as_elites / boss_sentinel / boss_aurelion become extra sheets of each area's actors.json
  kit      staging .glb files are copied in; a name clash takes the staging piece
  gamefx   staging as_fx rows are appended under the area's gamefx atlas (48 px cells), plus the plaza's quest_mark / quest_turnin glyphs; then the SHARED rows every built
           area carries are re-applied in the documented order: jot_art Stonefrost II / III, then musp_art's Caldera school (both crop-at-mark + append, idempotent)
Props: PLACE puts staging kit pieces into scene.json (objects + lamps + collision blockers) from the pack's layout metadata. Only adds or overwrites files: it never deletes
anything (only its own earlier placements, marked "asg_art", are re-made). The area's original gamefx atlas is kept once as gamefx.base.(png|json); every run rebuilds from that. Idempotent.
LAMP_CAP: lamps dimmed in reach when check_scene's colour / no_bloom checks name them; the lights stay. Lamp dimming is the lever for passing lighting; never loosen a check.
NEON: the pack puts neon only in gamefx and the kit glow material (README "Neon"): no sprite carries it, so ASG_NEON_SCOPE is EMPTY and there is no allow-list entry anywhere.
`neon_audit()` runs on every sheet before it is installed: a role with off-palette colours is NOT installed. This script never edits tools/check-sprite/check_sprite.py.

usage: python3 tools/hearthmoor/asg_art.py [--force] [area ...]      (then: cd games/hearthmoor && python3 -c "import build; build.write_pwa()")
"""
import json, shutil, sys
from pathlib import Path
from PIL import Image

GAME = Path(__file__).resolve().parents[2] / "games" / "hearthmoor"
STAGING = Path("/workspace/hearthmoor-staging/art/asgard")
ST = GAME / "art" / "asgard"
# [ASGARD EXTRA] follow-up pack (README there): as_guard + ingrith (ax_folk), red P3 (ax_aurelion_p3 replaces aurelion_p3), bigger ax_centaur (replaces storm_centaur),
# the G7 void kit (void_floor / void_rim / void_shard) and a superset as_fx atlas (+ void_motes / void_pool / void_shade). Copied to art/asgard_extra/ (add / overwrite only).
STAGING_X = Path("/workspace/hearthmoor-staging/art/asgard_extra")
STX = GAME / "art" / "asgard_extra"
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
FORCE = "--force" in sys.argv
PLANNED = ["asgard", "gs_hall", "gs_temple", "reliquary", "reliquary2"]   # story 2.1; the Reliquary is two corridors (like frozenspire / frozenspire2), see ASGARD_PROGRESS.md
AREAS = ARGS or PLANNED

# stock actor role (what the area spec's actors use) -> the pack's role, per area (re-pointed only if the area's actors.json has that stock role).
TOWNS = {
    "asgard": {"innkeeper": "ingrith", "dwarftrader": "as_trader", "wispcatcher": "groom", "lanternseller": "sigrun"},
    "gs_hall": {"innkeeper": "lordwarden", "wispcatcher": "runemaster", "elffolk": "fridleif"},
    "gs_temple": {"innkeeper": "priestess", "elffolk": "as_guide"},
    "reliquary": {}, "reliquary2": {"elffolk": "as_guide"},
}
FOLK = ["envoy_as", "lordwarden", "runemaster", "priestess", "fridleif", "groom", "as_trader", "as_guide"]   # as_folk.json: 1x
FOES = ["light_wraith", "storm_sentinel", "storm_centaur", "gilded_inquisitor"]
SHEETS = {  # sheet name -> (staging json, {area role: staging role}); every area gets these
    "asfolk": (ST / "sprite" / "as_folk.json", {r: r for r in FOLK}),
    "asenemy": (ST / "sprite" / "as_enemies.json", {r: r for r in FOES}),
    "assigrun": (ST / "sprite" / "as_sigrun.json", {"sigrun": "sigrun"}),
    "axfolk": (STX / "sprite" / "ax_folk.json", {"as_guard": "as_guard", "ingrith": "ingrith"}),   # extra: the Goldspire guards (the Thunder Toll foes) + Envoy Ingrith
    "axcent": (STX / "sprite" / "ax_centaur.json", {"storm_centaur": "storm_centaur"}),   # extra: REPLACES asenemy's storm_centaur (later sheet wins)   # the companion (no pet in this realm); wings are the fx sigrun_wings (README decision 2)
}
IMAGE = {}   # sheet -> staging png when it is not the json's own image
ELITES = ("aselite", (ST / "sprite" / "as_elites.json", {r: r for r in ("severin", "storm_sentinel_gate", "fridleif_boss", "centaurchamp", "elderwraith")}))
EXTRA = {    # sheets only where the fight / scene is (their own frame size)
    "asgard": {ELITES[0]: ELITES[1]},      # the naming's gate sentinel, Fridleif (conquer), the sky-plain rares
    "reliquary": {ELITES[0]: ELITES[1], "boss_sentinel": (ST / "sprite" / "boss_sentinel.json", {r: r for r in ("sentinelprime", "sentinel_p2", "sentinel_p3")})},   # Severin G5, the 5x golem G4
    "reliquary2": {ELITES[0]: ELITES[1], "boss_aurelion": (ST / "sprite" / "boss_aurelion.json", {r: r for r in ("aurelion", "aurelion_p3", "aurelion_wraith", "aurelion_rest")}),
                   "axp3": (STX / "sprite" / "ax_aurelion_p3.json", {"aurelion_p3": "aurelion_p3"})},   # extra: the red P3 REPLACES boss_aurelion's aurelion_p3 (no neon)   # 7x; aurelion_rest is its own role (decision 1)
    "gs_hall": {"boss_aurelion": (ST / "sprite" / "boss_aurelion.json", {"aurelion_rest": "aurelion_rest"})},   # befriend: his statue (the rest pose) in the Thunder Hall
}
# Scoped neon: EMPTY (README "Neon": no sprite uses neon). Never wider.
ASG_NEON_SCOPE = {}
FX_DROP = {"reliquary2": {("pool_gold", 0.0, -17.0)}}   # the pack drops the G7 bridge gold pool (nothing sits on the bridge over the void)   # per-area placed decals left out when check_scene no_bloom names them: {area: {(effect, x, z)}}
FX_SKIP = {"rain", "tile_flash"}   # flat one-colour frames: their crop never matches the atlas frame (check_scene gamefx_sharp atlas_corr 0.0). rain: the weather preset draws rain; tile_flash: the game uses strike_warning / rune_pulse. See ASGARD_PROGRESS.md
FX_FILE = ("gamefx", "as_fx.json")
ENEMY_ROLES = {"as_guard"}   # folk-sheet roles that only ever spawn as foes (the Thunder Toll guards)
FXSRC = STX / "gamefx"   # the extra pack's as_fx is a superset of asgard/gamefx/as_fx (all rows + the G7 void rows)


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
        if got - ASG_NEON_SCOPE.get(sr, set()): bad[sr] = got - ASG_NEON_SCOPE.get(sr, set())
    return bad

def have(p):
    if not Path(p).exists():
        print(f"  skip (not in the pack yet): {Path(p).relative_to(GAME) if str(p).startswith(str(GAME)) else p}")
        return False
    return True


def copy_staging():
    """Copy the staging pack into art/asgard/ (add / overwrite only)."""
    if not STAGING.exists():
        return False
    ST.mkdir(parents=True, exist_ok=True)
    shutil.copytree(STAGING, ST, dirs_exist_ok=True)
    if (STAGING_X / "READY.txt").exists():
        STX.mkdir(parents=True, exist_ok=True)
        shutil.copytree(STAGING_X, STX, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))
    return True


def sprites(area):
    d = GAME / "areas" / area / "public" / "art" / "sprite"
    mp = d / "actors.json"; m = json.loads(mp.read_text()); m.setdefault("sheets", {})
    for nm, (src, roles) in {**SHEETS, **EXTRA.get(area, {})}.items():
        if not have(src): continue
        sm = json.loads(src.read_text())
        bad = neon_audit(src, sm, IMAGE.get(nm, sm["image"]), set(roles.values()))
        if bad:
            print(f"  {nm}: NOT installed, off-palette colours outside ASG_NEON_SCOPE: " + "; ".join(f"{r} {sorted(h)[:4]}" for r, h in bad.items()))
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
                              **({"enemy": True} if r.get("enemy") or prev.get("enemy") or ar in ENEMY_ROLES else {}),
                              **({"follower": True} if nm == "assigrun" else {})}
        (d / f"{nm}.json").write_text(json.dumps(out, indent=1))
        m["sheets"][nm] = {"json": f"{nm}.json", "image": f"{nm}.png"}
    mp.write_text(json.dumps(m, indent=1))


def kit(area):
    d = GAME / "areas" / area / "public" / "art" / "kit"
    for g in sorted((ST / "kit").glob("*.glb")) + sorted((STX / "kit").glob("*.glb")):
        shutil.copy2(g, d / g.name)


def gamefx(area):
    if not have(FXSRC / "as_fx.json"): return False
    d = GAME / "areas" / area / "public" / "art" / "gamefx"
    if not (d / "gamefx.json").exists() and not (d / "gamefx.base.json").exists():
        # no atlas yet (wispwood): start from an empty base so the staging rows are the whole atlas, and point the scene at it
        d.mkdir(parents=True, exist_ok=True)
        sj = json.loads((FXSRC / "as_fx.json").read_text())
        (d / "gamefx.base.json").write_text(json.dumps({k: sj[k] for k in ("tool", "biome", "seed", "cell", "cast_sets", "cycle")} | {"image": "gamefx.png", "size": [0, 0], "effects": {}}))
        Image.new("RGBA", (sj["cell"], sj["cell"]), (0, 0, 0, 0)).save(d / "gamefx.base.png")   # one blank row
        sp = GAME / "areas" / area / "scene.json"; sc = json.loads(sp.read_text())
        sc["gamefx"] = {"image": "public/art/gamefx/gamefx.png", "json": "public/art/gamefx/gamefx.json"}
        sp.write_text(json.dumps(sc, separators=(",", ":")))
    bj, bp = d / "gamefx.base.json", d / "gamefx.base.png"
    if not bj.exists():
        shutil.copy2(d / "gamefx.json", bj); shutil.copy2(d / "gamefx.png", bp)
    base, sj = json.loads(bj.read_text()), json.loads((FXSRC / "as_fx.json").read_text())
    assert base["cell"] == sj["cell"], "cell size mismatch"
    bi, si = Image.open(bp).convert("RGBA"), Image.open(FXSRC / sj["image"]).convert("RGBA")
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


# The props come from the pack's layout (metadata/asgard_layout.json). The area spec owns the terrain (its 1.34 m ledge + stair replace the kit's gold_ledge / gold_stair, like
# Niflheim's frost_ledge), so those two are not placed; floor tiles are laid only on flat ground (not over a terrace, stair or the G7 void). WALK = flat, walkable, never casts shadows.
WALK = {"marble_floor", "moot_ring", "as_rune_bridge"}
LAYOUT_AREA = {"asgard": "asgard", "gs_hall": "gs_hall", "gs_temple": "gs_temple"}
SPEC_TERRAIN = {"gold_ledge", "gold_stair"}
NO_TILE = {"asgard": (-3.9, -11.2, 3.9, -2.4), "gs_hall": (-3.9, -9.2, 3.9, -2.2), "gs_temple": (-7.9, -7.3, -1.3, -1.2)}   # terrace + stair footprints (+ a margin): no floor tiles over them
EXTRA_PLACE = {"reliquary": [("marble_spring", [5.2, -27.6], "fixed", {})]}   # area -> [(piece, [x, z], "fixed", {rot, y})]: G3's hidden spring (rq_spring; the pack's G3 room has no basin)
PIECE_MOVE = {}    # (area, piece, x, z) -> (x, z): a prop moved off an actor / spawn / lamp (check_scene), rounded to 0.1
NOCAST = set()     # (area, piece): its shadow fell across an NPC (check_scene atlas corr)
DROP = {}          # (area, piece, x, z) left out (check_scene)

# The Reliquary: rooms G1-G5 stack north in `reliquary`, G6-G9 in `reliquary2` (14 m pitch, 8 m walk half-width); the pack's room layouts (reliquary_gN) are shifted by the
# room's z centre. Side walls / floors are regenerated for the whole corridor (the pack's per-room walls would close it); the spec owns each room's ledge + stair.
SPIRE_ROOMS = {
    "reliquary": [("reliquary_g1", 0.0), ("reliquary_g2", -14.0), ("reliquary_g3", -28.0), ("reliquary_g4", -42.0), ("reliquary_g5", -56.0)],
    "reliquary2": [("reliquary_g6", 0.0), ("reliquary_g7", -14.0), ("reliquary_g8", -28.0), ("reliquary_g9", -42.0)],
}
SPIRE_TOP = {"reliquary": -64.0, "reliquary2": -50.0}   # north end: where the corridor's back wall goes
SPIRE_X = 7.9   # side wall line (marble_wall pieces), the spec's own wall blocks sit at 8.2
VOID = {"reliquary2": [(-8.2, -19.0, -1.0, -12.5), (1.0, -19.0, 8.2, -12.5)]}   # G7's gold-lit void beside the Rune Bridge (the spec blocks it): no floor tiles there
# G7 void (extra pack, README "G7 void placement"): void_floor tiles (their mesh sits 2.4 m down) over the void rects, void_rim on the lips (the mesh faces +z into the
# void: rot pi on the south lip, 0 on the north lip, +-pi/2 on the bridge sides), void_shard floating >= 1.5 m from the bridge; motes / pools / shade + violet light stay in the void.
def _void_pieces(area):
    out = []
    for (x0, z0, x1, z1) in VOID.get(area, []):
        xs = [x0 + 1.0 + 2.0 * i for i in range(int((x1 - x0) / 2.0 + 0.5))]
        zs = [z1 - 1.0 - 2.0 * j for j in range(int((z1 - z0) / 2.0 + 0.5))]
        out += [("void_floor", [round(x, 2), round(z, 2)], "fixed", {}) for x in xs for z in zs]
        out += [("void_rim", [round(x, 2), z1 - 0.2], "fixed", {"rot": 3.141592653589793}) for x in xs]   # just inside the lip, the glow face toward the void
        out += [("void_rim", [round(x, 2), z0 + 0.2], "fixed", {}) for x in xs]
        bx = x1 - 0.2 if x1 < 0 else x0 + 0.2   # the bridge-side lip
        out += [("void_rim", [bx, round(z, 2)], "fixed", {"rot": (-1.5707963267948966 if x1 < 0 else 1.5707963267948966)}) for z in zs]
    return out
VOID_SHARDS = {"reliquary2": [(-4.4, -1.2, -17.2), (4.6, -0.8, -14.6), (-5.6, -1.5, -14.0), (3.4, -1.0, -17.6)]}
VOID_FX = {"reliquary2": {"decals": [("void_pool", (-4.0, -17.0)), ("void_pool", (4.0, -14.4)), ("void_pool", (-5.0, -14.2)), ("void_pool", (5.4, -17.4)),
                                     ("void_shade", (-2.6, -15.6)), ("void_shade", (2.8, -16.4)), ("void_shade", (-6.4, -16.8))],
                          "bills": [("void_motes", (-3.4, -2.3, -15.2)), ("void_motes", (3.6, -2.3, -16.0)), ("void_motes", (-6.0, -2.3, -17.6))],
                          "lights": [((-4.0, -1.6, -17.0), "#a45cf0", 4.5, 0.9), ((4.0, -1.6, -14.4), "#a45cf0", 4.5, 0.9), ((-5.0, -1.6, -14.2), "#a45cf0", 4.5, 0.9), ((5.4, -1.6, -17.4), "#a45cf0", 4.5, 0.9)]}}
# G7: the ledge brazier (and its flame, pool, light) moved back from the void lip (it was 0.9 m from the z -12.5 edge; now 1.6 m, on the ledge). Matched at 0.1 m.
SPOT_MOVE = {"reliquary2": {(-1.4, -11.6): (-2.4, -10.9)}}
def _mv(area, x, z):
    return SPOT_MOVE.get(area, {}).get((round(x, 1), round(z, 1)), (x, z))
# corridor rooms: pieces that would close the corridor are left out (the G1 inner door: the Reliquary door stands in the Dawn Temple; back-wall windows across the middle)
def _corridor_skip(key, name, x, z):
    if name == "reliquary_door": return True
    if name == "temple_window" and z < -6.0 and abs(x) < 3.0: return True
    return False


def _spire_notile(area):
    p = GAME / "areas" / "src" / f"{area}.json"
    if not p.exists(): return []
    sp = json.loads(p.read_text()); out = []
    for t in sp.get("terraces", []):
        if t["name"].startswith("wall"): continue
        r = t["rect"]; out.append((r[0] - 0.4, r[1] - 0.4, r[2] + 0.4, r[3] + 0.4))
    for st in sp.get("stairs", []):
        w = st["width"] / 2 + 0.4; out.append((st["x"] - w, st["z_top"] - 0.4, st["x"] + w, st["z_top"] + 4.2))
    return out + VOID.get(area, [])


def spire_layout(area):
    out = []
    lay = json.loads((ST / "metadata" / "asgard_layout.json").read_text())
    rooms = SPIRE_ROOMS[area]; nt = _spire_notile(area)
    zs = [zc for _, zc in rooms]; z_hi, z_lo = max(zs) + 8.0, SPIRE_TOP[area]
    for key, zc in rooms:
        for p in lay[key]["pieces"]:
            name, (x, y, z) = p[0], p[1]; rot = p[2] if len(p) > 2 else 0
            if name in SPEC_TERRAIN or name in ("marble_wall", "marble_floor") or _corridor_skip(key, name, x, z): continue
            if (area, name, round(x, 1), round(z + zc, 1)) in DROP: continue
            ex = {"rot": rot} if rot else {}
            if name in ("gold_orb_chain",): ex["y"] = y
            if (area, name, round(x, 1), round(z + zc, 1)) in PIECE_MOVE: x, z = PIECE_MOVE[(area, name, round(x, 1), round(z + zc, 1))]; z -= zc
            mx, mz = _mv(area, x, z + zc)
            out.append((name, [mx, mz], "fixed", ex))
    out += _void_pieces(area)
    out += [("void_shard", [x, z], "fixed", {"y": y}) for (x, y, z) in VOID_SHARDS.get(area, [])]
    z = z_hi
    while z > z_lo - 0.1:   # side walls, the full length
        for sx in (-SPIRE_X, SPIRE_X):
            out.append(("marble_wall", [sx, z], "fixed", {"rot": 1.5707963267948966}))
        z -= 2.0
    for x in range(-8, 9, 2):   # the back wall (north end)
        out.append(("marble_wall", [float(x), z_lo - 0.9], "fixed", {}))
    zz = z_hi - 1.0
    while zz > z_lo + 0.4:      # floor tiles, flat ground only (off the rooms' ledges + stairs and the void)
        for x in range(-7, 8, 2):
            if any(r[0] <= x <= r[2] and r[1] <= zz <= r[3] for r in nt): continue
            out.append(("marble_floor", [float(x), zz], "fixed", {}))
        zz -= 2.0
    return out


def _rooms(area):
    return SPIRE_ROOMS.get(area) or [(LAYOUT_AREA.get(area), 0.0)]


def layout_lights(area):
    lp = ST / "metadata" / "asgard_layout.json"
    if not lp.exists(): return []
    lay = json.loads(lp.read_text()); out = []
    for key, zc in _rooms(area):
        if key not in lay: continue
        for (p, col, rng, fix) in lay[key].get("extra_lights", []):
            mx, mz = _mv(area, p[0], p[2] + zc)
            out.append(((mx, p[1], mz), col, rng, fix))
    if area in VOID_FX: out += list(VOID_FX[area]["lights"])
    return out


FX_JS = GAME / "game" / "asgard_fx.js"


def fx_table():
    """game/asgard_fx.js: AS_FX[area] = [[effect, [x, z], dy]]: the pack's decals (pools, rune pulse, rime tell; dy 0) and billboards (flames, orbs, arcs, motes) per area,
    Reliquary rooms shifted by their z centre. Generated: do not edit (rerun asg_art.py)."""
    lp = ST / "metadata" / "asgard_layout.json"
    if not lp.exists(): return
    lay = json.loads(lp.read_text()); tab = {}
    for area in PLANNED:
        rows = []
        for key, zc in _rooms(area):
            if key not in lay: continue
            for d in lay[key].get("decals", []):
                if d[0] in FX_SKIP or (d[0], round(d[1][0], 2), round(d[1][1] + zc, 2)) in FX_DROP.get(area, ()): continue
                mx, mz = _mv(area, d[1][0], d[1][1] + zc)
                rows.append([d[0], [round(mx, 2), round(mz, 2)], 0])
            for b in lay[key].get("bills", []):
                n, (x, y, z) = b[0], b[1]
                if n in FX_SKIP or (n, round(x, 2), round(z + zc, 2)) in FX_DROP.get(area, ()): continue
                mx, mz = _mv(area, x, z + zc)
                rows.append([n, [round(mx, 2), round(mz, 2)], round(y, 2)])
        vf = VOID_FX.get(area, {})
        rows += [[n, [x, z], 0] for n, (x, z) in vf.get("decals", [])] + [[n, [x, z], y] for n, (x, y, z) in vf.get("bills", [])]
        tab[area] = rows
    body = ",\n".join(f"  {a}: {json.dumps(r, separators=(',', ':'))}" for a, r in tab.items())
    FX_JS.write_text("// GENERATED by tools/hearthmoor/asg_art.py (fx_table): the pack's animated pools / flames / arcs / motes per area. Do not edit.\nexport const AS_FX = {\n" + body + ",\n};\n")


def layout_place(area):
    if area in SPIRE_ROOMS: return spire_layout(area) + EXTRA_PLACE.get(area, [])
    la = LAYOUT_AREA.get(area)
    lp = ST / "metadata" / "asgard_layout.json"
    if not la or not lp.exists(): return EXTRA_PLACE.get(area, [])
    out = []
    nt = NO_TILE.get(area)
    for p in json.loads(lp.read_text())[la]["pieces"]:
        name, (x, y, z) = p[0], p[1]; rot = p[2] if len(p) > 2 else 0
        if name in SPEC_TERRAIN: continue
        if (area, name, round(x, 1), round(z, 1)) in DROP: continue
        if (area, name, round(x, 1), round(z, 1)) in PIECE_MOVE: x, z = PIECE_MOVE[(area, name, round(x, 1), round(z, 1))]
        if name == "marble_floor" and nt and nt[0] <= x <= nt[2] and nt[1] <= z <= nt[3]: continue
        ex = {}
        if rot: ex["rot"] = rot
        if name in ("gold_orb_chain",): ex["y"] = y   # hanging pieces keep the layout height (the rest sit on the collision grid: the spec ledge gives the dais pieces their 1.34 m)
        out.append((name, [x, z], "fixed", ex))
    return out + EXTRA_PLACE.get(area, [])


# Lamps dimmed in reach so they do not tint the few-colour sprites standing near them (check_scene colours) or blow the marble to 255 (no_bloom). Tune from check_scene.
LAMP_CAP = {}
NO_LIGHT = {("gs_temple", "temple_window"), ("reliquary2", "void_rim")}   # + the 22 G7 void rims: glow strip only, the void's violet comes from its own four pools of light   # (area, piece): lamps kept as glow sprites but not real point lights. The temple windows' panes clipped red at night (check_scene no_bloom)
EXTRA_CAP = {"gs_temple": 4.0}     # area -> cap for the pack's extra pools (range < 9). gs_temple: the violet window pools stacked on the window lamps (check_scene no_bloom, night)
LAMP_CAP_AREA = {a: dict(LAMP_CAP) for a in PLANNED}
LAMP_CAP_AREA["gs_temple"]["temple_window"] = 3.0   # the six violet windows clipped the night frame (check_scene no_bloom)
# per-area tightening goes here when check_scene's colour check names a lamp beside a few-colour sprite.


def place(area):
    import base64, math
    from array import array
    sp = GAME / "areas" / area / "scene.json"; sc = json.loads(sp.read_text())
    pieces = json.loads((ST / "kit" / "kit.json").read_text())["pieces"]
    if (STX / "kit" / "kit.json").exists(): pieces.update(json.loads((STX / "kit" / "kit.json").read_text())["pieces"])   # the G7 void pieces
    NOBLOCK = {n for n, p in pieces.items() if not p.get("blockers")} | WALK   # kit.json blockers [] = walkable / hanging: no blocker
    C = sc["collision"]; C.setdefault("base_data", C["data"])
    d = array("h"); d.frombytes(base64.b64decode(C["base_data"]))
    ox, oz, cl, W, H = C["origin"][0], C["origin"][1], C["cell"], C["w"], C["h"]
    sc["objects"] = [o for o in sc["objects"] if not o.get("asg_art") or o.get("fix1028")]  # keep hand-added Art fixes-1028 entries (they carry the installer tag too)
    sc["lamps"] = [l for l in sc["lamps"] if not l.get("asg_art") or l.get("fix1028")]  # keep hand-added Art fixes-1028 entries (they carry the installer tag too)
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
        o = {"glb": f"public/art/kit/{pc['file']}", "pos": [x, y, z], "rot": rot, "asg_art": True}
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
                                "color": mk.get("lamp_color", "#3fb8ff"), "fixed": mk.get("lamp_fixed", 0.5), "asg_art": True, **({"light": False} if (area, name) in NO_LIGHT else {})})
        print(f"  {area}: {name} at ({x}, {z})")
    for (lx, ly, lz), col, rng, fix in layout_lights(area):   # the pack's extra pools of light (cold blue, teal, aurora, violet and the warm lantern / window every 6-8 m)
        if rng < 9.0: rng = min(rng, EXTRA_CAP.get(area, 99.0))
        sc["lamps"].append({"pos": [lx, ly, lz], "range": rng, "color": col, "fixed": fix, "kind": "as_extra", "asg_art": True})
    C["data"] = base64.b64encode(d.tobytes()).decode()
    sp.write_text(json.dumps(sc, separators=(",", ":")) if "\n" not in sp.read_text()[:200] else json.dumps(sc, indent=1))





# ---- shared rows every built area carries (documented order: this pack's as_fx rows, then Stonefrost II / III, then the Caldera school)
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
        print("asg_art: /workspace/hearthmoor-staging/art/asgard/READY.txt is missing: the art pack is not ready. Nothing done (use --force for a dry look).")
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
