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

usage: python3 tools/hearthmoor/jot_art.py [--force] [area ...]      (then: cd games/hearthmoor && python3 -c "import build; build.write_pwa()")
"""
import json, shutil, sys
from pathlib import Path
from PIL import Image

GAME = Path(__file__).resolve().parents[2] / "games" / "hearthmoor"
STAGING = Path("/workspace/hearthmoor-staging/art/jotunheim")
ST = GAME / "art" / "jotunheim"
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
FORCE = "--force" in sys.argv
PLANNED = ["jotunheim", "jt_hall", "rimecaves", "barrow", "barrow2"]   # story 2.1; the Barrow is two areas (decision 8, like clockdeep / clockdeep2)
AREAS = ARGS or PLANNED

# PLACEHOLDER tables (fill from the art README). sheet name -> (staging json, {area role: staging role})
NPC_ROLES = ["envoy_jt", "jarl", "ulfar", "rimewife", "goatherd", "goatwife", "jt_trader", "rimecaptain"]   # story 5 (giants, 2x-3.2x)
SHEETS = {
    "jtnpc": (ST / "sprite" / "jt_npcs.json", {r: r for r in NPC_ROLES}),
    "jtenemy": (ST / "sprite" / "jt_enemies.json", {r: r for r in ("frost_troll", "ice_golem", "avalanche_golem", "rime_berserker")}),
    "flurry": (ST / "sprite" / "flurry.json", {"pet_flurry": "flurry"}),
}
IMAGE = {}   # sheet -> staging png when it is not the json's own image (Svartalfheim: the neon twin)
EXTRA = {    # sheets only where the fight / scene is (their own frame size)
    "barrow2": {"boss_hrimgard": (ST / "sprite" / "boss_hrimgard.json", {"hrimgard": "hrimgard"}),
               "miniboss_ormgar": (ST / "sprite" / "miniboss_ormgar.json", {"ormgar": "ormgar"})},
    "rimecaves": {"rare_frostmother": (ST / "sprite" / "rare_frostmother.json", {"frostmother": "frostmother"}),
                  "rare_avalanche": (ST / "sprite" / "rare_avalanche.json", {"avalanche": "avalanche"})},
}
# stand-ins from the base atlas, re-pointed to the realm's own NPC sheet by the spec's role names (only roles the area has)
TOWNS = {}
FX_FILE = ("gamefx", "jot_fx.json")   # staging gamefx rows: ST / "gamefx" / "jot_fx.json"


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
            if nm == "svnpc" and ar in TOWNS and ar not in m["roles"]:
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
    if not have(ST / "gamefx" / "jot_fx.json"): return False
    d = GAME / "areas" / area / "public" / "art" / "gamefx"
    if not (d / "gamefx.json").exists() and not (d / "gamefx.base.json").exists():
        # no atlas yet (wispwood): start from an empty base so the staging rows are the whole atlas, and point the scene at it
        d.mkdir(parents=True, exist_ok=True)
        sj = json.loads((ST / "gamefx" / "jot_fx.json").read_text())
        (d / "gamefx.base.json").write_text(json.dumps({k: sj[k] for k in ("tool", "biome", "seed", "cell", "cast_sets", "cycle")} | {"image": "gamefx.png", "size": [0, 0], "effects": {}}))
        Image.new("RGBA", (sj["cell"], sj["cell"]), (0, 0, 0, 0)).save(d / "gamefx.base.png")   # one blank row
        sp = GAME / "areas" / area / "scene.json"; sc = json.loads(sp.read_text())
        sc["gamefx"] = {"image": "public/art/gamefx/gamefx.png", "json": "public/art/gamefx/gamefx.json"}
        sp.write_text(json.dumps(sc, separators=(",", ":")))
    bj, bp = d / "gamefx.base.json", d / "gamefx.base.png"
    if not bj.exists():
        shutil.copy2(d / "gamefx.json", bj); shutil.copy2(d / "gamefx.png", bp)
    base, sj = json.loads(bj.read_text()), json.loads((ST / "gamefx" / "jot_fx.json").read_text())
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


# props placed per area: (piece, preferred [x, z]); the spot is searched outward from there on flat, walkable, uncrowded ground.
# PLACEHOLDER: the kit pieces are unknown until the art README lands. Guesses from the story look section (2.2): cold-fire braziers,
# frost-rune standing stones, rime-glass glow orbs, goat pens. Pieces missing from kit.json are skipped.
WALK = set()
PLACE = {
    "jotunheim": [("coldfire_brazier", [-3.0, 4.0]), ("coldfire_brazier", [3.0, 4.0]), ("rune_stone", [0.0, 8.0])],   # Welcome Ring, near the arch
    "jt_hall": [("coldfire_hearth", [0.0, -2.0], "fixed"), ("glow_orb", [-3.0, 0.0]), ("glow_orb", [3.0, 0.0])],
    "rimecaves": [("ice_pool", [4.0, 2.0]), ("rune_stone", [-6.0, -4.0])],
    "barrow": [], "barrow2": [],
}


def place(area):
    import base64, math
    from array import array
    sp = GAME / "areas" / area / "scene.json"; sc = json.loads(sp.read_text())
    pieces = json.loads((ST / "kit" / "kit.json").read_text())["pieces"]
    if not any(n in pieces for n, *_ in PLACE.get(area, [])): pass
    C = sc["collision"]; C.setdefault("base_data", C["data"])
    d = array("h"); d.frombytes(base64.b64decode(C["base_data"]))
    ox, oz, cl, W, H = C["origin"][0], C["origin"][1], C["cell"], C["w"], C["h"]
    sc["objects"] = [o for o in sc["objects"] if not o.get("jot_art")]
    sc["lamps"] = [l for l in sc["lamps"] if not l.get("jot_art")]
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
        sc["objects"].append(o)
        keep.append((x, z, max(hw, hd) + 0.6))
        if name not in WALK:
            for i, j in cells(x, z, hw * 0.8, hd * 0.8): d[j * W + i] = -32768
        mk = pc["markers"]
        for lp in mk.get("lamps", []):
            sc["lamps"].append({"pos": [x + lp[0], y + lp[1], z + lp[2]], "range": mk.get("lamp_range", 5.0), "kind": name,
                                "color": mk.get("lamp_color", "#a45cf0"), "fixed": mk.get("lamp_fixed", 0.5), "jot_art": True})
        print(f"  {area}: {name} at ({x}, {z})")
    C["data"] = base64.b64encode(d.tobytes()).decode()
    sp.write_text(json.dumps(sc, separators=(",", ":")) if "\n" not in sp.read_text()[:200] else json.dumps(sc, indent=1))




def main():
    if not (STAGING / "READY.txt").exists() and not FORCE:
        print("jot_art: /workspace/hearthmoor-staging/art/jotunheim/READY.txt is missing: the art pack is not ready. Nothing done (use --force for a dry look).")
        return 0
    copy_staging()
    for a in AREAS:
        d = GAME / "areas" / a
        if not (d / "scene.json").exists():
            print(f"{a}: not built yet (areas/{a}/scene.json missing): skipped"); continue
        if have(ST / "sprite"): sprites(a)
        if (ST / "kit" / "kit.json").exists(): kit(a); place(a)
        fx = gamefx(a)
        print(f"{a}: sprites + kit + props{' + gamefx' if fx else ' (no gamefx atlas)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
