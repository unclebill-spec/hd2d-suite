"""[SVARTALFHEIM] Minimal, additive art build for the Svartalfheim areas (realm-svartalfheim branch). Copy of alf_art.py's approach.

Wires the staging art in games/hearthmoor/art/svartalfheim/ into the built Svartalfheim areas WITHOUT re-assembling:
  sprites  svart_npcs + dagna + deep_enemies (+ Lumi's own sheet, she follows you everywhere) become extra sheets of each area's actors.json
           (the spec uses base-atlas stand-in roles: lanternseller->tinker (Tansy), wispcatcher->minerunner (Kesh),
            poolkeeper->poolkeeper_sv (Haldis), dwarftrader->dwarftrader (Brokk), elffolk->dw1, elffolk2->sv1)
  kit      staging .glb files are copied in; a name clash takes the staging piece
  gamefx   staging svart_fx rows are appended under the area's gamefx atlas (48 px cells); a name clash takes the staging effect
Props: PLACE below puts the staging pieces into scene.json (objects + lamps + collision blockers; nav is rebuilt from collision at
runtime). Only adds or overwrites files: it never deletes anything (only its own earlier placements, marked "svart_art", are re-made).
The area's original gamefx atlas is kept once as gamefx.base.(png|json) and every run rebuilds from that. Idempotent.
usage: python3 tools/hearthmoor/svart_art.py [area ...]      (then: cd games/hearthmoor && python3 -c "import build; build.write_pwa()")
"""
import json, shutil, sys
from pathlib import Path
from PIL import Image

GAME = Path(__file__).resolve().parents[2] / "games" / "hearthmoor"
ST = GAME / "art" / "svartalfheim"
ALF = GAME / "art" / "alfheim"
AREAS = sys.argv[1:] or ["svartalfheim", "forge_hall", "glowmines", "clockdeep", "clockdeep2"]
TOWNS = {"lanternseller": "tinker", "wispcatcher": "minerunner", "poolkeeper": "poolkeeper_sv", "dwarftrader": "dwarftrader",
         "elffolk": "dw1", "elffolk2": "sv1",
         "innkeeper": "thane", "shopkeeper": "runewarden", "nightmerchant": "hushed", "gnome": "dagna"}   # base-atlas stand-in role -> svart_npcs role (only roles the area has are re-pointed)
NPC = ["thane", "runewarden", "hushed", "dwarftrader", "tinker", "minerunner", "poolkeeper_sv", "dw1", "dw2", "sv1", "sv2"]
SHEETS = {  # sheet name -> (staging json, {area role: staging role})
    "lumi": (ALF / "lumi" / "lumi.json", {"lumi": "lumi"}),
    "svnpc": (ST / "sprite" / "svart_npcs.json", {**{k: v for k, v in TOWNS.items() if k != "gnome"}, **{v: v for v in NPC}}),
    "dagna": (ST / "sprite" / "dagna.json", {"gnome": "dagna", "dagna": "dagna"}),   # the neon-red twin is her main look (lead, 2026-10-15)
    "dagna_safe": (ST / "sprite" / "dagna.json", {"dagna_safe": "dagna"}),   # palette-only fallback sheet (its own role, not placed)
    "svenemy": (ST / "sprite" / "deep_enemies.json", {r: r for r in ("forgeconstruct", "sparkgolem", "sootling", "shadowsmith", "hushblade")}),
}

IMAGE = {"dagna": "dagna_neon.png", "dagna_safe": "dagna.png"}   # sheet -> staging png (default: the json's own image)
EXTRA = {"clockdeep2": {"boss_gorrak": (ST / "sprite" / "boss_gorrak.json", {"gorrak": "gorrak"}),
                          "miniboss_foreman": (ST / "sprite" / "miniboss_foreman.json", {"foreman": "foreman"})}}   # Gorrak's own 144x192 boss sheet, only where the fight is


def sprites(area):
    d = GAME / "areas" / area / "public" / "art" / "sprite"
    mp = d / "actors.json"; m = json.loads(mp.read_text()); m.setdefault("sheets", {})
    for nm, (src, roles) in {**SHEETS, **EXTRA.get(area, {})}.items():
        sm = json.loads(src.read_text())
        shutil.copy2(src.parent / IMAGE.get(nm, sm["image"]), d / f"{nm}.png")
        out = {k: sm[k] for k in ("tool", "biome", "frame", "pivot", "ground_row", "facings", "anims", "cols", "size")}
        out["image"] = f"{nm}.png"; out["roles"] = {}
        for ar, sr in roles.items():
            if nm == "svnpc" and ar in TOWNS and ar not in m["roles"]:
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
        sj = json.loads((ST / "gamefx" / "svart_fx.json").read_text())
        (d / "gamefx.base.json").write_text(json.dumps({k: sj[k] for k in ("tool", "biome", "seed", "cell", "cast_sets", "cycle")} | {"image": "gamefx.png", "size": [0, 0], "effects": {}}))
        Image.new("RGBA", (sj["cell"], sj["cell"]), (0, 0, 0, 0)).save(d / "gamefx.base.png")   # one blank row
        sp = GAME / "areas" / area / "scene.json"; sc = json.loads(sp.read_text())
        sc["gamefx"] = {"image": "public/art/gamefx/gamefx.png", "json": "public/art/gamefx/gamefx.json"}
        sp.write_text(json.dumps(sc, separators=(",", ":")))
    bj, bp = d / "gamefx.base.json", d / "gamefx.base.png"
    if not bj.exists():
        shutil.copy2(d / "gamefx.json", bj); shutil.copy2(d / "gamefx.png", bp)
    base, sj = json.loads(bj.read_text()), json.loads((ST / "gamefx" / "svart_fx.json").read_text())
    assert base["cell"] == sj["cell"], "cell size mismatch"
    bi, si = Image.open(bp).convert("RGBA"), Image.open(ST / "gamefx" / sj["image"]).convert("RGBA")
    # the ! / ? quest-marker glyphs (quest_mark, quest_turnin) copied from the plaza atlas (same 48 px cell): the realm areas' atlases had none,
    # so the Svartalfheim NPC markers (Dagna, Tansy, Bix, Halvard...) spawned nothing
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


# props placed per area: (piece, preferred [x, z]); the spot is searched outward from there on flat, walkable,
# uncrowded ground (clear of actors, spawns, exits, portals and other objects). Placed objects / lamps carry "svart_art".
PLACE = {
    # staging kit pieces (art/svartalfheim/kit/kit.json): rune-lamps = cold-blue light, braziers = forge red, cluster = violet.
    "svartalfheim": [("forge_brazier", [-1.8, 9.0]), ("forge_brazier", [1.8, 9.0]), ("rune_lamp", [-2.6, 2.0]), ("rune_lamp", [2.6, 2.0]),
                     ("forge_brazier", [-5.0, 8.4]), ("forge_brazier", [-9.8, 3.4]), ("crystal_cluster", [10.0, 5.4]),
                     ("mine_cart", [6.4, -3.6], "fixed"), ("rail_straight", [6.4, -3.0], "fixed"), ("rail_straight", [6.4, -5.0], "fixed"),
                     ("gear_wall", [-6.0, -11.0], "fixed"), ("gear_wall", [6.0, -11.0], "fixed")],
}
PLACE["forge_hall"] = [("gear_wall", [4.8, -11.0], "fixed"), ("gear_wall", [-6.8, -11.0], "fixed"), ("rune_lamp", [-2.8, 4.0]), ("rune_lamp", [2.8, 4.0]),
                       ("rune_lamp", [6.2, 1.4]), ("forge_brazier", [-7.0, 1.0]), ("forge_brazier", [5.6, 8.4]), ("crystal_cluster", [10.8, 7.0])]
PLACE["glowmines"] = [("crystal_cluster", [-9.0, -9.0], "fixed"), ("crystal_cluster", [-3.0, -9.6], "fixed"), ("crystal_cluster", [3.6, -9.4], "fixed"), ("crystal_cluster", [9.0, -9.0], "fixed"),
                      ("crystal_cluster", [-8.4, -3.0]), ("crystal_cluster", [8.0, -4.6]), ("crystal_cluster", [10.2, 3.0]),
                      ("mine_cart", [-7.6, 8.0]), ("rail_straight", [-7.6, 6.2], "fixed"), ("rail_straight", [-7.6, 8.2], "fixed"),
                      ("rune_lamp", [-3.2, 6.0]), ("rune_lamp", [4.2, 6.0]), ("gear_wall", [-9.8, 11.2], "fixed")]
PLACE["clockdeep"] = [("gear_wall", [-5.2, 41.2], "fixed"), ("gear_wall", [5.2, 41.2], "fixed"), ("gear_wall", [-5.2, 15.0], "fixed"), ("gear_wall", [5.2, 15.0], "fixed"),
                      ("gear_wall", [-5.2, -1.0], "fixed"), ("gear_wall", [5.2, -1.0], "fixed"), ("rune_lamp", [-2.8, 34.0]), ("rune_lamp", [2.8, 34.0]),
                      ("rune_lamp", [-3.0, 12.0], "fixed"), ("rune_lamp", [3.0, 12.0], "fixed"), ("crystal_cluster", [-5.6, -12.4], "fixed"), ("crystal_cluster", [5.6, -5.0], "fixed")]
PLACE["clockdeep2"] = [("gear_wall", [-5.2, 41.2], "fixed"), ("gear_wall", [5.2, 41.2], "fixed"), ("gear_wall", [-5.2, 13.0], "fixed"), ("gear_wall", [5.2, 13.0], "fixed"),
                       ("rune_lamp", [-2.8, 34.0]), ("rune_lamp", [2.8, 34.0]), ("mine_cart", [4.6, 3.0], "fixed"), ("rail_straight", [4.6, 1.2], "fixed"), ("rail_straight", [4.6, 5.0], "fixed"),
                       ("anvil_pillar", [0.0, -30.0], "fixed"), ("rune_lamp", [-3.0, -3.0], "fixed"), ("rune_lamp", [3.0, -3.0], "fixed"), ("gear_wall", [-5.2, -19.0], "fixed"), ("gear_wall", [5.2, -19.0], "fixed")]
WALK = {"rail_straight", "glow_pool", "deep_floor"}   # flat decals: walkable, no blocker


def place(area):
    import base64, math
    from array import array
    sp = GAME / "areas" / area / "scene.json"; sc = json.loads(sp.read_text())
    pieces = json.loads((ST / "kit" / "kit.json").read_text())["pieces"]
    C = sc["collision"]; C.setdefault("base_data", C["data"])
    d = array("h"); d.frombytes(base64.b64decode(C["base_data"]))
    ox, oz, cl, W, H = C["origin"][0], C["origin"][1], C["cell"], C["w"], C["h"]
    sc["objects"] = [o for o in sc["objects"] if not o.get("svart_art")]
    sc["lamps"] = [l for l in sc["lamps"] if not l.get("svart_art")]
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
        o = {"glb": f"public/art/kit/{pc['file']}", "pos": [x, y, z], "rot": 0, "svart_art": True}
        if name in WALK: o.update(walkable=True, cast=False)
        sc["objects"].append(o)
        keep.append((x, z, max(hw, hd) + 0.6))
        if name not in WALK:
            for i, j in cells(x, z, hw * 0.8, hd * 0.8): d[j * W + i] = -32768
        mk = pc["markers"]
        for lp in mk.get("lamps", []):
            sc["lamps"].append({"pos": [x + lp[0], y + lp[1], z + lp[2]], "range": mk.get("lamp_range", 5.0), "kind": name,
                                "color": mk.get("lamp_color", "#a45cf0"), "fixed": mk.get("lamp_fixed", 0.5), "svart_art": True})
        print(f"  {area}: {name} at ({x}, {z})")
    C["data"] = base64.b64encode(d.tobytes()).decode()
    sp.write_text(json.dumps(sc, separators=(",", ":")) if "\n" not in sp.read_text()[:200] else json.dumps(sc, indent=1))


for a in AREAS:
    sprites(a); kit(a); fx = gamefx(a); place(a)
    print(f"{a}: sprites + kit + props{' + gamefx' if fx else ' (no gamefx atlas)'}")
