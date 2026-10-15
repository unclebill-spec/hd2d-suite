"""[ALFHEIM] Minimal, additive art build for the Alfheim areas (realm-alfheim branch).

Wires the staging art in games/hearthmoor/art/alfheim/ into the four built Alfheim areas WITHOUT re-assembling:
  sprites  lumi + alfheim_npcs + prism_vault_enemies become extra sheets of each area's actors.json
           (townsfolk roles re-pointed: lanternseller->elf_lampwright, wispcatcher->elf_child,
            poolkeeper->elf_gardener, librarian->elf_scholar; prismshard / mirrorduelist use the staging sheet)
  kit      staging .glb files are copied in; a name clash takes the staging piece (lumen_tree, light_bridge, vault_pillar ...)
  gamefx   staging alfheim_fx rows are appended under the area's gamefx atlas; a name clash takes the staging effect
Props: PLACE below puts the staging pieces into scene.json (objects + lamps + collision blockers; nav is rebuilt from\ncollision at runtime). Never deletes anything: it only writes files and rewrites actors.json / gamefx.json / gamefx.png. Idempotent: the
original gamefx atlas is kept once as gamefx.base.(png|json) and every run rebuilds from that.
usage: python3 tools/hearthmoor/alf_art.py [area ...]      (then: cd games/hearthmoor && python3 -c "import build; build.write_pwa()")
"""
import json, shutil, sys
from pathlib import Path
from PIL import Image

GAME = Path(__file__).resolve().parents[2] / "games" / "hearthmoor"
ST = GAME / "art" / "alfheim"
AREAS = sys.argv[1:] or ["alfheim", "lumen_court", "wispwood", "prismvault"]
TOWNS = {"lanternseller": "elf_lampwright", "wispcatcher": "elf_child", "poolkeeper": "elf_gardener", "librarian": "elf_scholar"}
SHEETS = {  # sheet name -> (staging json, {area role: staging role})
    "lumi": (ST / "lumi" / "lumi.json", {"lumi": "lumi"}),
    "alfnpc": (ST / "sprite" / "alfheim_npcs.json", {**TOWNS, **{v: v for v in TOWNS.values()}}),
    "alfenemy": (ST / "sprite" / "prism_vault_enemies.json", {"prismshard": "prismshard", "mirrorduelist": "mirrorduelist"}),
}


def sprites(area):
    d = GAME / "areas" / area / "public" / "art" / "sprite"
    mp = d / "actors.json"; m = json.loads(mp.read_text()); m.setdefault("sheets", {})
    for nm, (src, roles) in SHEETS.items():
        sm = json.loads(src.read_text())
        shutil.copy2(src.parent / sm["image"], d / f"{nm}.png")
        out = {k: sm[k] for k in ("tool", "biome", "frame", "pivot", "ground_row", "facings", "anims", "cols", "size")}
        out["image"] = f"{nm}.png"; out["roles"] = {}
        for ar, sr in roles.items():
            if nm == "alfnpc" and ar in TOWNS and ar not in m["roles"]:
                continue   # re-point only roles this area actually has
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
    d = GAME / "areas" / area / "public" / "art" / "gamefx"
    if not (d / "gamefx.json").exists() and not (d / "gamefx.base.json").exists():
        # no atlas yet (wispwood): start from an empty base so the staging rows are the whole atlas, and point the scene at it
        d.mkdir(parents=True, exist_ok=True)
        sj = json.loads((ST / "gamefx" / "alfheim_fx.json").read_text())
        (d / "gamefx.base.json").write_text(json.dumps({k: sj[k] for k in ("tool", "biome", "seed", "cell", "cast_sets", "cycle")} | {"image": "gamefx.png", "size": [0, 0], "effects": {}}))
        Image.new("RGBA", (sj["cell"], sj["cell"]), (0, 0, 0, 0)).save(d / "gamefx.base.png")   # one blank row
        sp = GAME / "areas" / area / "scene.json"; sc = json.loads(sp.read_text())
        sc["gamefx"] = {"image": "public/art/gamefx/gamefx.png", "json": "public/art/gamefx/gamefx.json"}
        sp.write_text(json.dumps(sc, separators=(",", ":")))
    bj, bp = d / "gamefx.base.json", d / "gamefx.base.png"
    if not bj.exists():
        shutil.copy2(d / "gamefx.json", bj); shutil.copy2(d / "gamefx.png", bp)
    base, sj = json.loads(bj.read_text()), json.loads((ST / "gamefx" / "alfheim_fx.json").read_text())
    assert base["cell"] == sj["cell"], "cell size mismatch"
    bi, si = Image.open(bp).convert("RGBA"), Image.open(ST / "gamefx" / sj["image"]).convert("RGBA")
    im = Image.new("RGBA", (max(bi.width, si.width), bi.height + si.height), (0, 0, 0, 0))
    im.paste(bi, (0, 0)); im.paste(si, (0, bi.height)); im.save(d / "gamefx.png")
    off = bi.height // base["cell"]
    for k, e in sj["effects"].items():
        e = {kk: vv for kk, vv in e.items() if kk not in ("frame_list", "strip")}
        e["row"] = e["row"] + off
        base["effects"][k] = e
    base["size"] = [im.width, im.height]
    (d / "gamefx.json").write_text(json.dumps(base, indent=1))
    return True


# props placed per area: (piece, preferred [x, z]); the spot is searched outward from there on flat, walkable,
# uncrowded ground (clear of actors, spawns, exits, portals and other objects). Placed objects / lamps carry "alf_art".
PLACE = {
    "alfheim": [("prism_fountain", [3.0, 1.0]), ("lumen_tree_small", [7.0, -4.0]),
                ("lumen_lamp", [-2.4, 6.0]), ("lumen_lamp", [2.4, 6.0]), ("wisp_lantern_post", [-4.0, 1.0]),
                ("elf_rail", [0.0, -3.0]), ("wisp_jar", [-6.5, 6.0]), ("elf_archway", [7.4, -2.0], "fixed")],
    "lumen_court": [("lumen_pavilion", [6.0, 4.5]), ("crystal_spire", [6.5, -2.0]), ("lumen_lamp", [-2.5, 2.0])],
    "wispwood": [("wisp_lantern_post", [6.0, -2.0]), ("wisp_jar", [0.0, 3.0]), ("lumen_tree_small", [-5.0, 3.0])],
    "prismvault": [("sylvaine_throne", [0.0, -52.0]), ("vault_wall", [-5.3, 31.4], "fixed"), ("crystal_spire", [5.3, 31.4], "fixed"),   # clear of the entry view (check-scene lineup)
                  
                   ("vault_floor", [0.0, 34.5])],
}
WALK = {"vault_floor"}   # flat decals: walkable, no blocker


def place(area):
    import base64, math
    from array import array
    sp = GAME / "areas" / area / "scene.json"; sc = json.loads(sp.read_text())
    pieces = json.loads((ST / "kit" / "kit.json").read_text())["pieces"]
    C = sc["collision"]; C.setdefault("base_data", C["data"])
    d = array("h"); d.frombytes(base64.b64decode(C["base_data"]))
    ox, oz, cl, W, H = C["origin"][0], C["origin"][1], C["cell"], C["w"], C["h"]
    sc["objects"] = [o for o in sc["objects"] if not o.get("alf_art")]
    sc["lamps"] = [l for l in sc["lamps"] if not l.get("alf_art")]
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
    vbox = None if area == "prismvault" or not st else (st[0] - 6.0, st[1] - 16.0, st[0] + 6.0, st[1] + 1.0)
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
        if cam and area != "prismvault" and not (cam[0] + 1 < x < cam[2] - 1 and cam[1] + 1 < z < cam[3] - 1):
            return None
        hs = []
        for i, j in cells(x, z, hw + 0.5, hd + 0.5):
            if not (0 <= i < W and 0 <= j < H) or d[j * W + i] == -32768: return None
            hs.append(d[j * W + i])
        if max(hs) - min(hs) > 6: return None
        if any(math.hypot(x - kx, z - kz) < kr + max(hw, hd) for kx, kz, kr in keep): return None
        return hs[len(hs) // 2] / 100

    for name, (px, pz), *fixed in PLACE.get(area, []):
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
        o = {"glb": f"public/art/kit/{pc['file']}", "pos": [x, y, z], "rot": 0, "alf_art": True}
        if name in WALK: o.update(walkable=True, cast=False)
        sc["objects"].append(o)
        keep.append((x, z, max(hw, hd) + 0.6))
        if name not in WALK:
            for i, j in cells(x, z, hw * 0.8, hd * 0.8): d[j * W + i] = -32768
        mk = pc["markers"]
        for lp in mk.get("lamps", []):
            sc["lamps"].append({"pos": [x + lp[0], y + lp[1], z + lp[2]], "range": mk.get("lamp_range", 5.0), "kind": name,
                                "color": mk.get("lamp_color", "#a45cf0"), "fixed": mk.get("lamp_fixed", 0.5), "alf_art": True})
        print(f"  {area}: {name} at ({x}, {z})")
    C["data"] = base64.b64encode(d.tobytes()).decode()
    sp.write_text(json.dumps(sc, separators=(",", ":")) if "\n" not in sp.read_text()[:200] else json.dumps(sc, indent=1))


def lumi_only(area):
    """non-Alfheim areas: only Lumi's own sheet (she follows you everywhere once she joins)"""
    d = GAME / "areas" / area / "public" / "art" / "sprite"
    if not (d / "actors.json").exists():
        return
    keep = dict(SHEETS); SHEETS.clear(); SHEETS["lumi"] = keep["lumi"]
    try:
        sprites(area)
    finally:
        SHEETS.clear(); SHEETS.update(keep)


if not sys.argv[1:]:
    for a in sorted(p.name for p in (GAME / "areas").iterdir() if p.is_dir() and p.name != "src" and p.name not in AREAS):
        lumi_only(a); print(f"{a}: lumi sheet")

for a in AREAS:
    sprites(a); kit(a); fx = gamefx(a); place(a)
    print(f"{a}: sprites + kit + props{' + gamefx' if fx else ' (no gamefx atlas)'}")
