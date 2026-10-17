"""[MUSPELHEIM] Art installer for the Muspelheim areas (realm-muspelheim branch). Modeled on jot_art.py / svart_art.py / alf_art.py.

Wires the staging art in games/hearthmoor/art/muspelheim/ (copied from /workspace/hearthmoor-staging/art/muspelheim/) into the BUILT Muspelheim
areas without re-assembling:
  sprites  ember-kin / fire-giant NPC sheets, enemy sheets, the boss / mini-boss / rare sheets and Kindle become extra sheets of each area's actors.json
  kit      staging .glb files are copied in; a name clash takes the staging piece
  gamefx   staging mu_fx rows are appended under the area's gamefx atlas (48 px cells), plus the plaza's quest_mark / quest_turnin glyphs
Props: PLACE puts staging kit pieces into scene.json (objects + lamps + collision blockers). Only adds or overwrites files: it never deletes anything
(only its own earlier placements, marked "musp_art", are re-made). The area's original gamefx atlas is kept once as gamefx.base.(png|json) and every
run rebuilds from that. Idempotent.
LAMP_CAP: the warm decor lamps (lava channels, braziers, forge windows) are dimmed in reach so they do not tint the few-colour ember-kin sprites standing near
them (check_scene colours); the lights stay, only their reach shrinks. Add a piece to LAMP_CAP when check_scene's colour check names it.
NEON: scoped allow-lists only. This script NEVER edits tools/check-sprite/check_sprite.py and never widens any list. `neon_audit()` runs on every sheet before it is
installed: off-palette (neon) colours are allowed only for the roles and hexes in MUSP_NEON_SCOPE (mirrors MUSP_NEON_ALLOW in check_sprite.py; filled from the art README's
"Neon flag" + a ruling, expected: Kindle only). A role outside the scope that carries off-palette colours is NOT installed (its palette-safe `_safe` twin is installed instead
when the pack ships one; otherwise the sheet is skipped with a message).

STATUS: SKELETON. The art pack is not ready. Nothing runs until /workspace/hearthmoor-staging/art/muspelheim/READY.txt exists (--force overrides, for a dry look).
Every table below is a placeholder to be filled from the art README when the pack lands: the sheet names, the staging role names and the PLACE coordinates are guesses
from the story doc (areas / NPCs / bosses), not from real files. Missing staging files are SKIPPED with a message, never an error, so a partial pack can be wired in
stages. (Unlike jot_art.py there is no Stonefrost step: the Caldera school's spell rows arrive as their own staging fx file; add a `school()` step modelled on jot_art.stonefrost
when the README names it, and run it LAST: build.py's install_forge / install_alchemy re-crop a gamefx atlas at their own marks.)

usage: python3 tools/hearthmoor/musp_art.py [--force] [area ...]      (then: cd games/hearthmoor && python3 -c "import build; build.write_pwa()")
"""
import json, shutil, sys
from pathlib import Path
from PIL import Image

GAME = Path(__file__).resolve().parents[2] / "games" / "hearthmoor"
STAGING = Path("/workspace/hearthmoor-staging/art/muspelheim")
ST = GAME / "art" / "muspelheim"
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
FORCE = "--force" in sys.argv
PLANNED = ["muspelheim", "mp_hall", "lavafalls", "caldera", "caldera2"]   # story 2.1; the Caldera is two areas (like clockdeep / barrow), see MUSPELHEIM_PROGRESS.md
AREAS = ARGS or PLANNED

EMBERKIN = ["envoy_mp", "warden_mp", "forgejudge", "springkeeper", "lizardman", "mp_trader", "cindercaptain", "mp_guide", "mp_a", "mp_b"]   # mp_npcs.json roles (ember-kin 1x, fire-giants 2.5-2.6x)
# base-atlas stand-in role -> mp_npcs role (only roles the area has are re-pointed): the area specs use stock role names so they assemble; this repaints them.
TOWNS = {"dwarftrader": "mp_trader", "wispcatcher": "lizardman", "poolkeeper": "springkeeper", "shopkeeper": "envoy_mp", "innkeeper": "warden_mp",
         "elffolk": "mp_a", "elffolk2": "mp_b", "nightmerchant": "cindercaptain", "lanternseller": "mp_guide", "gnome": "mp_a"}
SHEETS = {  # sheet name -> (staging json, {area role: staging role})
    "mpnpc": (ST / "sprite" / "mp_npcs.json", {**TOWNS, **{r: r for r in EMBERKIN}}),
    "kindle": (ST / "sprite" / "kindle.json", {"kindle": "kindle"}),   # the companion: hound-sized salamander (neon back-spots: scoped allow-list, see NEON above)
    "kindle_safe": (ST / "sprite" / "kindle.json", {"kindle_safe": "kindle"}),   # palette-safe fallback twin (its own role, not placed) if the pack ships one
    "mpenemy": (ST / "sprite" / "mp_enemies.json", {r: r for r in ("magma_hound", "flame_elemental", "fire_golem", "ashen_cultist")}),
}
IMAGE = {"kindle": "kindle_neon.png", "kindle_safe": "kindle.png"}   # sheet -> staging png when it is not the json's own image (guess: Flurry's pattern)
EXTRA = {    # sheets only where the fight / scene is (their own frame size)
    "muspelheim": {"mpelite": (ST / "sprite" / "mp_elites.json", {"dagny": "dagny"})},   # Cinder-Captain Dagny Flameguard (conquer), 3x
    "lavafalls": {"mpelite": (ST / "sprite" / "mp_elites.json", {"ashalpha": "ashalpha", "pyreling": "pyreling"})},   # the two rares
    "caldera2": {"boss_vharzul": (ST / "sprite" / "boss_vharzul.json", {"vharzul": "vharzul", "vharzul_p3": "vharzul_p3"}),   # 8x, black-iron plate, crown of fire
                 "mpelite": (ST / "sprite" / "mp_elites.json", {"kilnmother": "kilnmother"})},
}
# Scoped neon: role -> the exact off-palette hexes it may carry. EMPTY until the README + a ruling name them (mirror MUSP_NEON_ALLOW in check_sprite.py, never wider).
MUSP_NEON_SCOPE = {}
FX_FILE = ("gamefx", "mu_fx.json")   # staging gamefx rows: ST / "gamefx" / "mu_fx.json"


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
        if got - MUSP_NEON_SCOPE.get(sr, set()): bad[sr] = got - MUSP_NEON_SCOPE.get(sr, set())
    return bad

def have(p):
    if not Path(p).exists():
        print(f"  skip (not in the pack yet): {Path(p).relative_to(GAME) if str(p).startswith(str(GAME)) else p}")
        return False
    return True


def copy_staging():
    """Copy the staging pack into art/muspelheim/ (add / overwrite only)."""
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
            print(f"  {nm}: NOT installed, off-palette colours outside MUSP_NEON_SCOPE: " + "; ".join(f"{r} {sorted(h)[:4]}" for r, h in bad.items()))
            continue
        shutil.copy2(src.parent / IMAGE.get(nm, sm["image"]), d / f"{nm}.png")
        out = {k: sm[k] for k in ("tool", "biome", "frame", "pivot", "ground_row", "facings", "anims", "cols", "size")}
        out["image"] = f"{nm}.png"; out["roles"] = {}
        for ar, sr in roles.items():
            if nm == "mpnpc" and ar in TOWNS and ar not in m["roles"]:
                continue   # re-point only roles this area actually has
            if sr not in sm["roles"]: print(f"  {nm}: no staging role {sr}"); continue
            r = sm["roles"][sr]
            out["roles"][ar] = {k: v for k, v in r.items() if k != "frames"}
            prev = m["roles"].get(ar, {})
            m["roles"][ar] = {"sheet": nm, "row": r["row"], "kind": r.get("kind", prev.get("kind", "creature")),
                              "anims": r.get("anims", ["idle", "walk"]), "desc": r.get("desc", ""),
                              **({"enemy": True} if r.get("enemy") or prev.get("enemy") else {})}
        (d / f"{nm}.json").write_text(json.dumps(out, indent=1))
        m["sheets"][nm] = {"json": f"{nm}.json", "image": f"{nm}.png"}
    mp.write_text(json.dumps(m, indent=1))


def kit(area):
    d = GAME / "areas" / area / "public" / "art" / "kit"
    for g in sorted((ST / "kit").glob("*.glb")):
        shutil.copy2(g, d / g.name)


def gamefx(area):
    if not have(ST / "gamefx" / "mu_fx.json"): return False
    d = GAME / "areas" / area / "public" / "art" / "gamefx"
    if not (d / "gamefx.json").exists() and not (d / "gamefx.base.json").exists():
        # no atlas yet (wispwood): start from an empty base so the staging rows are the whole atlas, and point the scene at it
        d.mkdir(parents=True, exist_ok=True)
        sj = json.loads((ST / "gamefx" / "mu_fx.json").read_text())
        (d / "gamefx.base.json").write_text(json.dumps({k: sj[k] for k in ("tool", "biome", "seed", "cell", "cast_sets", "cycle")} | {"image": "gamefx.png", "size": [0, 0], "effects": {}}))
        Image.new("RGBA", (sj["cell"], sj["cell"]), (0, 0, 0, 0)).save(d / "gamefx.base.png")   # one blank row
        sp = GAME / "areas" / area / "scene.json"; sc = json.loads(sp.read_text())
        sc["gamefx"] = {"image": "public/art/gamefx/gamefx.png", "json": "public/art/gamefx/gamefx.json"}
        sp.write_text(json.dumps(sc, separators=(",", ":")))
    bj, bp = d / "gamefx.base.json", d / "gamefx.base.png"
    if not bj.exists():
        shutil.copy2(d / "gamefx.json", bj); shutil.copy2(d / "gamefx.png", bp)
    base, sj = json.loads(bj.read_text()), json.loads((ST / "gamefx" / "mu_fx.json").read_text())
    assert base["cell"] == sj["cell"], "cell size mismatch"
    bi, si = Image.open(bp).convert("RGBA"), Image.open(ST / "gamefx" / sj["image"]).convert("RGBA")
    # the ! / ? quest-marker glyphs (quest_mark, quest_turnin) copied from the plaza atlas (same 48 px cell): the realm areas' atlases had none,
    # so the Muspelheim NPC markers (Aska, Torka, Svala...) spawned nothing
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
# Coordinates are the art README's Stonehollow layout (metadata/muspelheim.json), moved where the area spec's own terrain (plateau + stair come
# from the spec, so the kit's stone_ledge / stone_stair are not placed) or an actor stands. Keep-clear: nothing on the stair + 1 m, 2.5 m in
# front of longhouse doors, 1.5 m around the from_bifrost spawn.

NOBLOCK = set()   # walkable rubble: no blocker (kit.json blockers [])
WALK = {"lava_channel", "glass_bridge", "stepping_stone"}   # flat decals: walkable, no blocker (guess names: set from the README)
# props placed per area: (piece, preferred [x, z], "fixed" to hand-place). PLACEHOLDER: the kit pieces are unknown until the art README lands. Guesses from the story look
# section (2.2): basalt houses with copper roofs, lava channels (emissive tiles, a point light each), glass bridges, molten-glass orbs on chains, forge-glow doorways, the
# Warden's Flame lamps, frost-vein cracks (cold blue), the Caldera mouth (6 m basalt arch with three seal-doors), frost wedges. Pieces missing from kit.json are skipped.
PLACE = {
    "muspelheim": [("lava_channel", [0.0, 2.0], "fixed"), ("basalt_house", [-8.0, -8.0]), ("basalt_house", [8.0, -8.0]), ("glass_orb", [-3.0, 4.0]), ("glass_orb", [3.0, 4.0])],
    "mp_hall": [("shrine_lamp_violet", [-3.0, -6.4], "fixed"), ("shrine_lamp_violet", [3.0, -6.4], "fixed"), ("sigil_mould_wall", [-6.0, -3.0], "fixed")],
    "lavafalls": [("lava_fall", [-4.0, -8.0], "fixed"), ("lava_fall", [4.0, -8.0], "fixed"), ("caldera_mouth", [0.0, -7.5], "fixed")],
    "caldera": [], "caldera2": [],
}

# Cinderhold and the Lavafalls: decor lamps (lava, forge windows, braziers, glass orbs) are dimmed in reach so they do not tint the few-colour ember-kin sprites standing
# near them (check_scene colours: crop colours / source colours <= 2). The lights stay; only their reach shrinks. Piece names are guesses until the README lands.
LAMP_CAP = {"basalt_house": 3.0, "lava_channel": 3.0, "lava_fall": 3.5, "glass_orb": 3.2, "forge_brazier": 4.5, "shrine_lamp_violet": 3.0, "caldera_mouth": 4.0, "frost_wedge": 2.5}
LAMP_CAP_AREA = {a: dict(LAMP_CAP) for a in PLANNED}


def place(area):
    import base64, math
    from array import array
    sp = GAME / "areas" / area / "scene.json"; sc = json.loads(sp.read_text())
    pieces = json.loads((ST / "kit" / "kit.json").read_text())["pieces"]
    if not any(n in pieces for n, *_ in PLACE.get(area, [])): pass
    C = sc["collision"]; C.setdefault("base_data", C["data"])
    d = array("h"); d.frombytes(base64.b64decode(C["base_data"]))
    ox, oz, cl, W, H = C["origin"][0], C["origin"][1], C["cell"], C["w"], C["h"]
    sc["objects"] = [o for o in sc["objects"] if not o.get("musp_art")]
    sc["lamps"] = [l for l in sc["lamps"] if not l.get("musp_art")]
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
        o = {"glb": f"public/art/kit/{pc['file']}", "pos": [x, y, z], "rot": 0, "musp_art": True}
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
                                "color": mk.get("lamp_color", "#a45cf0"), "fixed": mk.get("lamp_fixed", 0.5), "musp_art": True})
        print(f"  {area}: {name} at ({x}, {z})")
    C["data"] = base64.b64encode(d.tobytes()).decode()
    sp.write_text(json.dumps(sc, separators=(",", ":")) if "\n" not in sp.read_text()[:200] else json.dumps(sc, indent=1))





def main():
    if not (STAGING / "READY.txt").exists() and not FORCE:
        print("musp_art: /workspace/hearthmoor-staging/art/muspelheim/READY.txt is missing: the art pack is not ready. Nothing done (use --force for a dry look).")
        return 0
    copy_staging()
    for a in AREAS:
        d = GAME / "areas" / a
        if not (d / "scene.json").exists():
            print(f"{a}: not built yet (areas/{a}/scene.json missing): skipped"); continue
        sprites(a)
        if (ST / "kit" / "kit.json").exists(): kit(a); place(a)
        fx = gamefx(a)
        print(f"{a}: sprites + kit + props{' + gamefx' if fx else ' (no gamefx atlas)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
