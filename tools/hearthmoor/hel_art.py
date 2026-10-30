"""[HELHEIM] Art installer for the Helheim areas (realm-helheim branch): Gloamhaven (helheim, hh_shore, hh_archive) and the Ossuary of Whispers (ossuary O1-O5, ossuary2 O6-O9).
Copied from asg_art.py (same flow, same rules). Waits on /workspace/hearthmoor-staging/art/helheim/READY.txt (without it: prints a message and does nothing). With it, wires the
staging art in games/hearthmoor/art/helheim/ (copied from the staging pack) into the BUILT Helheim areas without re-assembling:
  sprites  hh_folk / hh_inkling / hh_enemies / hh_elites / boss_mordrath become extra sheets of each area's actors.json
  kit      staging .glb files are copied in; a name clash takes the staging piece
  gamefx   staging as_fx rows are appended under the area's gamefx atlas (48 px cells), plus the plaza's quest_mark / quest_turnin glyphs; then the SHARED rows every built
           area carries are re-applied in the documented order: jot_art Stonefrost II / III, then musp_art's Caldera school (both crop-at-mark + append, idempotent)
Props: PLACE puts staging kit pieces into scene.json (objects + lamps + collision blockers) at the pack's layout positions (metadata/helheim_layout.json; Art's check_clear.py
keeps them >= 1 m from edges, spawns and stairs, so every piece is placed "fixed"). ADD OR OVERWRITE ONLY: it never deletes a file (only its own earlier placements, marked
"hel_art", are re-made). The area's original gamefx atlas is kept once as gamefx.base.(png|json); every run rebuilds from that. Idempotent.
LAMP_CAP / NO_LIGHT / FX_SKIP are the levers for check_scene (lighting / single flat-colour fx); never loosen a check.
NEON: HEL_NEON_SCOPE lists the ONLY off-palette hexes a role may carry (README "Neon"). It starts EMPTY (the first pack has no neon on sprites). `neon_audit()` runs on every
sheet before it is installed: a role with off-palette colours outside the scope is NOT installed. This script never edits tools/check-sprite/check_sprite.py.

usage: python3 tools/hearthmoor/hel_art.py [--force] [area ...]      (then: cd games/hearthmoor && python3 -c "import build; build.write_pwa()")
"""
import json, shutil, sys
from pathlib import Path
from PIL import Image

GAME = Path(__file__).resolve().parents[2] / "games" / "hearthmoor"
STAGING = Path("/workspace/hearthmoor-staging/art/helheim")
ST = GAME / "art" / "helheim"
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
FORCE = "--force" in sys.argv
PLANNED = ["helheim", "hh_shore", "hh_archive", "ossuary", "ossuary2"]   # story 2.1; the Ossuary is two corridors (like reliquary / reliquary2), see HELHEIM_PROGRESS.md
AREAS = ARGS or PLANNED

# stock actor role (what the area spec's actors use) -> the pack's role, per area (re-pointed only if the area's actors.json has that stock role).
TOWNS = {
    "helheim": {"innkeeper": "hel", "dwarftrader": "ferryman", "poolkeeper": "innghost", "wispcatcher": "childghost", "shopkeeper": "bakerghost", "elffolk": "gloam_folk"},
    "hh_shore": {"lanternseller": "eira_spirit", "dwarftrader": "ferryman", "wispcatcher": "childghost"},
    "hh_archive": {"innkeeper": "archivist_hh", "dwarftrader": "sailorghost"},
    "ossuary": {}, "ossuary2": {},
}
# Scoped neon: EMPTY (README "Neon": no sprite uses neon). Only Art's exact scoped entries ever go here (role -> {hex}). Never wider.
_HHV = {"#a45cf0", "#3a2458"}   # Art follow-up (READY 03:26, README "Neon flag"): violet tabards + chains, these 5 roles only
HEL_NEON_SCOPE = {"gloam_knight": _HHV, "odric": _HHV, "mordrath": _HHV, "mordrath_p2": _HHV, "mordrath_p3": _HHV}
# While the scope is empty the palette-safe twins (<sheet>_safe.json, violet drawn with the blue-shadow ramp) are installed when the pack ships them;
# the neon sheets (violet tabards / chains) are used only once their exact scoped entries are in HEL_NEON_SCOPE.
def SPR(name):
    safe = ST / "sprite" / f"{name}_safe.json"
    return safe if (not HEL_NEON_SCOPE and safe.exists()) else ST / "sprite" / f"{name}.json"
FOLK = ["hel", "ferryman", "innghost", "archivist_hh", "eira_spirit", "childghost", "bakerghost", "sailorghost", "gloam_folk"]   # hh_folk.json
FOES = ["shade", "gate_shade", "soul_wraith", "grave_lantern", "bone_elemental", "garnet_golem", "skeleton_line", "lich", "gloam_knight"]
SHEETS = {  # sheet name -> (staging json, {area role: staging role}); every area gets these
    "hhfolk": (ST / "sprite" / "hh_folk.json", {r: r for r in FOLK}),
    "hhenemy": (SPR("hh_enemies"), {r: r for r in FOES}),
    "hhinkling": (ST / "sprite" / "hh_inkling.json", {"inkling": "inkling"}),   # the gloam raven (shown as a Helheim follower NPC after hh_raven)
}
IMAGE = {}   # sheet -> staging png when it is not the json's own image
ELITES = ("hhelite", (SPR("hh_elites"), {r: r for r in ("vesperin", "vesperin_bat", "odric", "gravelamp", "hollowchoir")}))
EXTRA = {    # sheets only where the fight / scene is (their own frame size)
    "helheim": {ELITES[0]: ELITES[1]},     # Ser Odric (the Pale Toll), the gravelamp rare
    "ossuary": {ELITES[0]: ELITES[1]},     # Lord Vesperin (O5, 3x) + his mist-bats
    "ossuary2": {ELITES[0]: ELITES[1], "boss_mordrath": (SPR("boss_mordrath"), {r: r for r in ("mordrath", "mordrath_p2", "mordrath_p3")})},   # the Hollow Choir (O6), Mordrath 8x (O9)
}
FX_DROP = {}   # per-area placed decals left out when check_scene no_bloom names them: {area: {(effect, x, z)}}
FX_SKIP = set()   # flat one-colour frames whose crop never matches the atlas frame (check_scene gamefx_sharp atlas_corr 0.0)
ENEMY_ROLES = set()
FXSRC = ST / "gamefx"


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
        if got - HEL_NEON_SCOPE.get(sr, set()): bad[sr] = got - HEL_NEON_SCOPE.get(sr, set())
    return bad

def have(p):
    if not Path(p).exists():
        print(f"  skip (not in the pack yet): {Path(p).relative_to(GAME) if str(p).startswith(str(GAME)) else p}")
        return False
    return True


def copy_staging():
    """Copy the staging pack into art/helheim/ (add / overwrite only; never deletes)."""
    if not STAGING.exists():
        return False
    ST.mkdir(parents=True, exist_ok=True)
    shutil.copytree(STAGING, ST, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))
    return True


def sprites(area):
    d = GAME / "areas" / area / "public" / "art" / "sprite"
    mp = d / "actors.json"; m = json.loads(mp.read_text()); m.setdefault("sheets", {})
    for nm, (src, roles) in {**SHEETS, **EXTRA.get(area, {})}.items():
        if not have(src): continue
        sm = json.loads(src.read_text())
        bad = neon_audit(src, sm, IMAGE.get(nm, sm["image"]), set(roles.values()))
        if bad:
            print(f"  {nm}: NOT installed, off-palette colours outside HEL_NEON_SCOPE: " + "; ".join(f"{r} {sorted(h)[:4]}" for r, h in bad.items()))
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
                              **({"follower": True} if nm == "hhinkling" else {})}
        (d / f"{nm}.json").write_text(json.dumps(out, indent=1))
        m["sheets"][nm] = {"json": f"{nm}.json", "image": f"{nm}.png"}
    mp.write_text(json.dumps(m, indent=1))


def kit(area):
    d = GAME / "areas" / area / "public" / "art" / "kit"
    for g in sorted((ST / "kit").glob("*.glb")):
        shutil.copy2(g, d / g.name)
    for name, pack in FOREIGN.items():
        if any(e[0] == name for e in EXTRA_PLACE.get(area, [])):
            shutil.copy2(GAME / "art" / pack / "kit" / f"{name}.glb", d / f"{name}.glb")


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


# The props come from the pack's layout (metadata/helheim_layout.json). The area spec owns the terrain (its 1.34 m ledge + stair replace the kit's mist_ledge / mist_stair),
# so those two are not placed; floor tiles are laid only on flat ground (not over a terrace or stair). WALK = flat, walkable, never casts shadows.
WALK = {"gloam_floor", "ossuary_floor", "black_lake", "pebble_shore"}
LAYOUT_AREA = {"helheim": "helheim", "hh_shore": "hh_shore", "hh_archive": "hh_archive"}
SPEC_TERRAIN = {"mist_ledge", "mist_stair"}
FLOORS = {"gloam_floor", "ossuary_floor", "pebble_shore"}
# Approved by Cozy Builder 2026-10-21 (check_scene grades night_warm_frac / ossuary colours): ONE small warm lamp per area, from existing packs,
# capped small (LAMP_CAP below) so the gloom stays dominant; placed by the clear-spot search (keeps off actors, spawns, exits, paths) - no overlaps.
# The Ossuary also gets prop variety from the Helheim kit itself (mourning_statue, lore_tablet) in O1's arrival view.
FOREIGN = {"warm_lantern": "jotunheim", "dawn_flame_brazier": "asgard"}   # piece -> pack under games/hearthmoor/art/<pack>/kit
# 2026-10-30 (Helheim finish, check_scene grades night_warm_frac 0.0015 / 0.0008 / 0.0016 < 0.002): more of the SAME two approved warm accents, 3 m cap.
# ossuary2 gets the spot the fix1028 near brazier has in ossuary (same corridor geometry). The clear-spot search cannot be used here (the floor tiles placed
# before EXTRA_PLACE fill `keep`), so the spots are "fixed", scanned clear on the collision grid (flat, unblocked 0.8 m around, >2 m actors, >2.2 m spawns,
# >3.6 m exits, >1.5 m props) and off the walking lines.
EXTRA_PLACE = {"hh_shore": [("warm_lantern", [-6.4, 7.4], "fixed"),   # spots checked clear (walkable, flat, >2 m from actors / spawns / exits / ledges / props)
                            ("dawn_flame_brazier", [6.0, 7.5], "fixed")],   # 2026-10-30: the floor corner right of the shore stair
               "hh_archive": [("dawn_flame_brazier", [-5.1, 6.0], "fixed"), ("dawn_flame_brazier", [4.9, 6.0], "fixed")],   # 2026-10-30: front corners of the reading room
               "ossuary2": [("dawn_flame_brazier", [-5.5, 3.0], "fixed"),   # approved 2026-10-21 08:18 (check_scene grades night_warm_frac), same 3 m cap
                            ("dawn_flame_brazier", [-7.5, 10.9], "fixed")],   # 2026-10-30: mirrors ossuary's fix1028 near brazier
               "ossuary": [("dawn_flame_brazier", [-6.0, 3.5], "fixed"), ("mourning_statue", [5.45, 5.85], "fixed"), ("lore_tablet", [-5.4, 0.8], "fixed")]}
PIECE_MOVE = {}    # (area, piece, x, z) -> (x, z): a prop moved off an actor / spawn / lamp (check_scene), rounded to 0.1
NOCAST = set()     # (area, piece): its shadow fell across an NPC (check_scene atlas corr)
DROP = {}          # (area, piece, x, z) left out (check_scene)

# The Ossuary: rooms O1-O5 stack north in `ossuary`, O6-O9 in `ossuary2` (14 m pitch, 8 m walk half-width); the pack's room layouts (ossuary_oN) are shifted by the room's
# z centre. Side walls / floors are regenerated for the whole corridor (the pack's per-room walls would close it); the spec owns each room's ledge + stair.
SPIRE_ROOMS = {
    "ossuary": [("ossuary_o1", 0.0), ("ossuary_o2", -14.0), ("ossuary_o3", -28.0), ("ossuary_o4", -42.0), ("ossuary_o5", -56.0)],
    "ossuary2": [("ossuary_o6", 0.0), ("ossuary_o7", -14.0), ("ossuary_o8", -28.0), ("ossuary_o9", -42.0)],
}
SPIRE_TOP = {"ossuary": -64.0, "ossuary2": -50.0}   # north end: where the corridor's back wall goes
SPIRE_X = 7.9   # side wall line (ossuary_wall pieces), the spec's own wall blocks sit at 8.2
SPOT_MOVE = {}
def _mv(area, x, z):
    return SPOT_MOVE.get(area, {}).get((round(x, 1), round(z, 1)), (x, z))
# corridor rooms: pieces that would close the corridor are left out (the O1 inner Bone Door: the Ossuary door stands in the Archive; the O6 rhythm door is a runtime spot)
def _corridor_skip(key, name, x, z):
    if name == "ossuary_door": return True
    return False


def _notile(area):
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
    lay = json.loads((ST / "metadata" / "helheim_layout.json").read_text())
    rooms = SPIRE_ROOMS[area]; nt = _notile(area)
    zs = [zc for _, zc in rooms]; z_hi, z_lo = max(zs) + 8.0, SPIRE_TOP[area]
    for key, zc in rooms:
        for p in lay[key]["pieces"]:
            name, (x, y, z) = p[0], p[1]; rot = p[2] if len(p) > 2 else 0
            if name in SPEC_TERRAIN or name in ("ossuary_wall", "ossuary_floor") or _corridor_skip(key, name, x, z): continue
            if (area, name, round(x, 1), round(z + zc, 1)) in DROP: continue
            ex = {"rot": rot} if rot else {}
            if name in ("glow_orb_chain", "floating_candles", "lantern_boat") or y: ex["y"] = y
            if (area, name, round(x, 1), round(z + zc, 1)) in PIECE_MOVE: x, z = PIECE_MOVE[(area, name, round(x, 1), round(z + zc, 1))]; z -= zc
            mx, mz = _mv(area, x, z + zc)
            out.append((name, [mx, mz], "fixed", ex))
    z = z_hi
    while z > z_lo - 0.1:   # side walls, the full length
        for sx in (-SPIRE_X, SPIRE_X):
            out.append(("ossuary_wall", [sx, z], "fixed", {"rot": 1.5707963267948966}))
        z -= 2.0
    for x in range(-8, 9, 2):   # the back wall (north end)
        out.append(("ossuary_wall", [float(x), z_lo - 0.9], "fixed", {}))
    zz = z_hi - 1.0
    while zz > z_lo + 0.4:      # floor tiles, flat ground only (off the rooms' ledges + stairs)
        for x in range(-7, 8, 2):
            if any(r[0] <= x <= r[2] and r[1] <= zz <= r[3] for r in nt): continue
            out.append(("ossuary_floor", [float(x), zz], "fixed", {}))
        zz -= 2.0
    return out


def _rooms(area):
    return SPIRE_ROOMS.get(area) or [(LAYOUT_AREA.get(area), 0.0)]


def layout_lights(area):
    lp = ST / "metadata" / "helheim_layout.json"
    if not lp.exists(): return []
    lay = json.loads(lp.read_text()); out = []
    for key, zc in _rooms(area):
        if key not in lay: continue
        for (p, col, rng, fix) in lay[key].get("extra_lights", []):
            mx, mz = _mv(area, p[0], p[2] + zc)
            out.append(((mx, p[1], mz), col, rng, fix))
    return out


FX_JS = GAME / "game" / "helheim_fx.js"


def fx_table():
    """game/helheim_fx.js: HH_FX[area] = [[effect, [x, z], dy]]: the pack's decals (pools, rings, shadows; dy 0) and billboards (flames, orbs, motes) per area,
    Ossuary rooms shifted by their z centre. Generated: do not edit (rerun hel_art.py)."""
    lp = ST / "metadata" / "helheim_layout.json"
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
        tab[area] = rows
    body = ",\n".join(f"  {a}: {json.dumps(r, separators=(',', ':'))}" for a, r in tab.items())
    FX_JS.write_text("// GENERATED by tools/hearthmoor/hel_art.py (fx_table): the pack's animated pools / flames / orbs / motes per area. Do not edit.\nexport const HH_FX = {\n" + body + ",\n};\n")


def layout_place(area):
    if area in SPIRE_ROOMS: return spire_layout(area) + EXTRA_PLACE.get(area, [])
    la = LAYOUT_AREA.get(area)
    lp = ST / "metadata" / "helheim_layout.json"
    if not la or not lp.exists(): return EXTRA_PLACE.get(area, [])
    out = []
    nt = _notile(area)
    for p in json.loads(lp.read_text())[la]["pieces"]:
        name, (x, y, z) = p[0], p[1]; rot = p[2] if len(p) > 2 else 0
        if name in SPEC_TERRAIN: continue
        if (area, name, round(x, 1), round(z, 1)) in DROP: continue
        if (area, name, round(x, 1), round(z, 1)) in PIECE_MOVE: x, z = PIECE_MOVE[(area, name, round(x, 1), round(z, 1))]
        if name in FLOORS and any(r[0] <= x <= r[2] and r[1] <= z <= r[3] for r in nt): continue
        ex = {}
        if rot: ex["rot"] = rot
        if y: ex["y"] = y   # hanging / floating pieces keep the layout height (the rest sit on the collision grid)
        out.append((name, [x, z], "fixed", ex))
    return out + EXTRA_PLACE.get(area, [])


# Lamps dimmed in reach so they do not tint the few-colour sprites standing near them (check_scene colours) or blow a surface to 255 (no_bloom). Tune from check_scene.
LAMP_CAP = {"warm_lantern": 3.0, "dawn_flame_brazier": 3.0}   # the two approved warm accents: small pools only
NO_LIGHT = set()   # (area, piece): lamps kept as glow sprites but not real point lights
EXTRA_CAP = {}     # area -> cap for the pack's extra pools (range < 9)
LAMP_CAP_AREA = {a: dict(LAMP_CAP) for a in PLANNED}
LAMP_CAP_AREA["helheim"].update(cold_fire_lamp=4.0, coldfire_brazier=4.0)   # the street lamps / braziers clipped the night frame after the NPC moves (check_scene no_bloom 0.0218 > 0.02)


# check_scene effects_sharp lever (Cozy Builder, 2026-10-21): hh_shore's lake bubbles drift over the toadcap's lineup slot, so the shore's spells
# index drops glowplant_toadcap; glowplant_violet (an existing glowplant that passes effects_sharp) stays. The shore has no garden plots (garden.js).
SPELL_SWAP = {"hh_shore": {"glowplant_toadcap": "glowplant_violet"}}


def spell_swap(area):
    sw = SPELL_SWAP.get(area)
    jp = GAME / "areas" / area / "public/art/spells/spells.json"
    if not sw or not jp.exists(): return
    j = json.loads(jp.read_text()); e = j.get("effects", j)
    for old, new in sw.items():
        if old in e and new in e: del e[old]
    raw = jp.read_text(); jp.write_text(json.dumps(j, indent=1) if "\n" in raw[:200] else json.dumps(j))


# Approved 2026-10-21 08:18 (Cozy Builder): Gloamhaven only, the #2ab4ff / #d4a8ff glow effects are thinned (checkerboard dither = half alpha in
# this pixel style; same colours, same shapes, neon still reads against the gloom) so the night frame stops clipping (check_scene no_bloom).
# Area-local atlas only; nothing skipped. The runtime has no per-effect alpha (engine/effects.js is off-limits).
GLOW_THIN = {"helheim": {"colours": [(0x2a, 0xb4, 0xff), (0xd4, 0xa8, 0xff)],
                         "effects": ["cold_flame", "pool_coldfire", "pool_window", "pool_lilac", "lake_shimmer", "soul_light", "soul_motes", "violet_motes", "glow_orb_lilac", "lantern_float"]}}


def glow_thin(area):
    g = GLOW_THIN.get(area)
    d = GAME / "areas" / area / "public/art/gamefx"
    if not g or not (d / "gamefx.json").exists(): return
    import numpy as np
    m = json.loads((d / "gamefx.json").read_text()); C = m["cell"]
    im = np.array(Image.open(d / "gamefx.png").convert("RGBA"))
    yy, xx = np.mgrid[0:im.shape[0], 0:im.shape[1]]; odd = (xx + yy) % 2 == 1
    for n in g["effects"]:
        e = m["effects"].get(n)
        if not e: continue
        r0, r1, c1 = e["row"] * C, (e["row"] + 1) * C, e["frames"] * C
        a = im[r0:r1, :c1]
        for (r, gg, b) in g["colours"]:
            hit = (a[..., 0] == r) & (a[..., 1] == gg) & (a[..., 2] == b) & (a[..., 3] > 0) & odd[r0:r1, :c1]
            a[hit, 3] = 0
    Image.fromarray(im).save(d / "gamefx.png")


def place(area):
    import base64, math
    from array import array
    sp = GAME / "areas" / area / "scene.json"; sc = json.loads(sp.read_text())
    pieces = json.loads((ST / "kit" / "kit.json").read_text())["pieces"]
    for name, pack in FOREIGN.items():
        pieces.setdefault(name, json.loads((GAME / "art" / pack / "kit" / "kit.json").read_text())["pieces"][name])
    NOBLOCK = {n for n, p in pieces.items() if not p.get("blockers")} | WALK   # kit.json blockers [] = walkable / hanging: no blocker
    C = sc["collision"]; C.setdefault("base_data", C["data"])
    d = array("h"); d.frombytes(base64.b64decode(C["base_data"]))
    ox, oz, cl, W, H = C["origin"][0], C["origin"][1], C["cell"], C["w"], C["h"]
    # objects hand-added by Art fixes-1028 carry hel_art AND fix1028: keep them (no installer regenerates them; their lamps carry no hel_art tag either)
    sc["objects"] = [o for o in sc["objects"] if not o.get("hel_art") or o.get("fix1028")]
    sc["lamps"] = [l for l in sc["lamps"] if not l.get("hel_art")]
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
        o = {"glb": f"public/art/kit/{pc['file']}", "pos": [x, y, z], "rot": rot, "hel_art": True}
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
                                "color": mk.get("lamp_color", "#3fb8ff"), "fixed": mk.get("lamp_fixed", 0.5), "hel_art": True, **({"light": False} if (area, name) in NO_LIGHT else {})})
        print(f"  {area}: {name} at ({x}, {z})")
    for (lx, ly, lz), col, rng, fix in layout_lights(area):   # the pack's extra pools of light (cold blue, teal, aurora, violet and the warm lantern / window every 6-8 m)
        if rng < 9.0: rng = min(rng, EXTRA_CAP.get(area, 99.0))
        sc["lamps"].append({"pos": [lx, ly, lz], "range": rng, "color": col, "fixed": fix, "kind": "hh_extra", "hel_art": True})
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
        print("hel_art: /workspace/hearthmoor-staging/art/helheim/READY.txt is missing: the art pack is not ready. Nothing done (use --force for a dry look).")
        return 0
    copy_staging()
    fx_table()
    for a in AREAS:
        d = GAME / "areas" / a
        if not (d / "scene.json").exists():
            print(f"{a}: not built yet (areas/{a}/scene.json missing): skipped"); continue
        sprites(a)
        if (ST / "kit" / "kit.json").exists(): kit(a); place(a)
        spell_swap(a)
        fx = gamefx(a)
        sf, cs = _shared(a) if fx else (False, False)
        if fx: glow_thin(a)
        print(f"{a}: sprites + kit + props{' + gamefx' if fx else ' (no gamefx atlas)'}{' + stonefrost' if sf else ''}{' + caldera school' if cs else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
