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
PUZ = Path("/workspace/hearthmoor-staging/art/svartalfheim_puzzles")   # [SVARTALFHEIM puzzles] peg / cog / lever / rail kit, cog_spin fx, Tobble
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
    "tobble": (PUZ / "tobble.json", {"tobble": "tobble"}),   # Tobble's own gnome-follower sheet (20x32, pets layout), replaces the stand-in in the realm areas
    "svenemy": (ST / "sprite" / "deep_enemies.json", {r: r for r in ("forgeconstruct", "sparkgolem", "sootling", "shadowsmith", "hushblade")}),
}

IMAGE = {"dagna": "dagna_neon.png", "dagna_safe": "dagna.png"}   # sheet -> staging png (default: the json's own image)
EXTRA = {"clockdeep2": {"boss_gorrak": (ST / "sprite" / "boss_gorrak.json", {"gorrak": "gorrak"}),
                          "miniboss_foreman": (ST / "sprite" / "miniboss_foreman.json", {"foreman": "foreman"}),
                          "rare_sootcolossus": (ST / "sprite" / "rare_sootcolossus.json", {"sootcolossus": "sootcolossus"})},
         "clockdeep": {"rare_basilisk": (ST / "sprite" / "rare_basilisk.json", {"basilisk": "basilisk"})},
         "glowmines": {"rare_basilisk": (ST / "sprite" / "rare_basilisk.json", {"basilisk": "basilisk"}),
                       "rare_sootcolossus": (ST / "sprite" / "rare_sootcolossus.json", {"sootcolossus": "sootcolossus"})}}   # Gorrak's own 144x192 boss sheet, only where the fight is


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
                              **({"enemy": True} if r.get("enemy") or prev.get("enemy") else {}),
                              **({"pet": True, "follower": True} if nm == "tobble" else {})}
        (d / f"{nm}.json").write_text(json.dumps(out, indent=1))
        m["sheets"][nm] = {"json": f"{nm}.json", "image": f"{nm}.png"}
    mp.write_text(json.dumps(m, indent=1))


def kit(area):
    d = GAME / "areas" / area / "public" / "art" / "kit"
    for g in sorted((ST / "kit").glob("*.glb")):
        shutil.copy2(g, d / g.name)
    if area in PZ:
        for g in sorted((PUZ / "kit").glob("*.glb")):   # the puzzle kit (a name clash, rail_straight, takes the newer piece)
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
    pz_im, pz_fx = None, {}
    if area in PZ:   # the spinning-cog decals (cog_spin_small / medium / large, 8 frames at 10 fps)
        pj = json.loads((PUZ / "gamefx" / "puzzle_fx.json").read_text()); assert pj["cell"] == c
        pz_im, pz_fx = Image.open(PUZ / "gamefx" / pj["image"]).convert("RGBA"), pj["effects"]
    ph = pz_im.height if pz_im else 0
    im = Image.new("RGBA", (max(bi.width, si.width, strip.width, pz_im.width if pz_im else 0), bi.height + si.height + strip.height + ph), (0, 0, 0, 0))
    im.paste(bi, (0, 0)); im.paste(si, (0, bi.height)); im.paste(strip, (0, bi.height + si.height))
    if pz_im: im.paste(pz_im, (0, bi.height + si.height + strip.height))
    im.save(d / "gamefx.png")
    off = bi.height // base["cell"]
    for i, (k, e) in enumerate(mk):
        base["effects"][k] = {**{kk: vv for kk, vv in e.items() if kk != "frame_list"}, "row": off + si.height // c + i}
    for k, e in sj["effects"].items():
        e = {kk: vv for kk, vv in e.items() if kk not in ("frame_list", "strip")}
        e["row"] = e["row"] + off
        base["effects"][k] = e
    for k, e in pz_fx.items():
        e = {kk: vv for kk, vv in e.items() if kk not in ("frame_list", "strip")}
        e["row"] = e["row"] + off + si.height // c + len(mk)
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
                       ("rune_lamp", [-2.8, 34.0]),   # (the east rune lamp, the decor mine cart and its 2 rails make way for the C4 / C6 puzzles)
                       ("anvil_pillar", [0.0, -30.0], "fixed"), ("rune_lamp", [-3.0, -3.0], "fixed"), ("rune_lamp", [3.0, -3.0], "fixed"), ("gear_wall", [-5.2, -19.0], "fixed"), ("gear_wall", [5.2, -19.0], "fixed")]
# ---- [SVARTALFHEIM puzzles] the C2 / C4 gear puzzles and the C6 rails (story 7.1) ---------------------------------------------------
# Pegs sit 0.8 m apart (a medium cog's diameter is 0.92 m, so teeth mesh). Positions are floor metres in the area frame.
def _pegs(*rows):
    return [{"id": r[0], "pos": [r[1], r[2]], **r[3]} for r in rows]


PZ = {
    "clockdeep": [{
        "kind": "gear", "id": "c2", "flag": "cd_cog1", "need": "cw", "title": "The Drive Shaft",
        "pegs": _pegs(("D", 2.0, 7.0, {"role": "drive", "cog": "m"}), ("A", 2.8, 7.0, {}), ("C", 2.0, 6.2, {}),
                      ("F", 2.8, 6.2, {"cog": "s", "fixed": True, "frozen": True}), ("B", 2.8, 5.4, {}), ("E", 2.0, 5.4, {}),
                      ("W", 3.6, 5.4, {"role": "winch", "cog": "m"})),
        "loose": [{"id": "s1", "size": "s", "pos": [1.0, 3.8]}, {"id": "m1", "size": "m", "pos": [1.0, 2.6]}],
        "reset": [3.2, 2.8], "gate": {"glb": "gear_wall", "pos": [-2.8, 1.6], "kind": "shutter"},
        "chest": {"pos": [-2.8, 0.5], "gold": 45, "item": "deep_brass", "n": 1, "flag": "cd_chest_c2"}}],
    "clockdeep2": [{
        "kind": "gear", "id": "c4", "flag": "cd_cog2", "need": "cw", "title": "The Assembly Line", "belts": {"x": [-1.4, 1.4], "z": [29.8, 41.0], "presses": [[-1.0, 40.4], [1.0, 40.4]]},
        "pegs": _pegs(("D1", 1.6, 36.0, {"role": "drive", "cog": "m"}), ("a", 2.4, 36.0, {}), ("b", 3.2, 36.0, {}),
                      ("W", 3.2, 35.2, {"role": "winch", "cog": "m"}), ("c", 3.2, 34.4, {}), ("D2", 3.2, 33.6, {"role": "drive", "cog": "m"})),
        "loose": [{"id": "s1", "size": "s", "pos": [-0.6, 35.4]}, {"id": "m1", "size": "m", "pos": [0.6, 34.6]}, {"id": "m2", "size": "m", "pos": [-0.6, 33.8]}],
        "reset": [-1.0, 32.2], "gate": None, "chest": None}, {
        "kind": "rails", "id": "c6", "flag": "cd_cog3", "title": "The Switchyard",
        "start": [3.0, 11.4], "x": 3.0, "branch_x": 5.0,
        "tiles": [{"z": 12.0, "t": "end", "rot": 180}, {"z": 10.0, "t": "sw", "sw": "sw1"}, {"z": 8.0, "t": "st"}, {"z": 6.0, "t": "sw", "sw": "sw2", "frozen": True},
                  {"z": 4.0, "t": "st"}, {"z": 2.0, "t": "sw", "sw": "sw3"}, {"z": 0.0, "t": "st"}],
        "levers": {"sw1": [1.5, 10.7], "sw2": [1.5, 6.7], "sw3": [1.5, 2.7], "brake": [1.5, 12.2]},
        "gate": {"glb": "gear_wall", "pos": [3.0, -1.5], "kind": "ram"},
        "chest": {"pos": [3.7, -2.3], "gold": 70, "item": "deep_brass", "n": 2, "flag": "cd_chest_c6"}}],
}
TOBBLE_AREAS = ["clockdeep", "clockdeep2", "vanaheim", "vh_village", "vh_garden", "rotwood", "verdant"]   # [VANAHEIM] Q1: he follows you home too


def pz_points(area):
    pts = []
    for r in PZ.get(area, []):
        pts += [(q["pos"][0], q["pos"][1], 0.9) for q in r.get("pegs", [])]
        pts += [(q["pos"][0], q["pos"][1], 0.7) for q in r.get("loose", [])]
        if r.get("reset"): pts.append((r["reset"][0], r["reset"][1], 0.9))
        if r.get("gate"): pts.append((r["gate"]["pos"][0], r["gate"]["pos"][1], 1.8))
        if r.get("chest"): pts.append((r["chest"]["pos"][0], r["chest"]["pos"][1], 1.0))
        if r["kind"] == "rails":
            pts += [(r["x"], t["z"], 1.5) for t in r["tiles"]] + [(r["branch_x"], t["z"], 1.5) for t in r["tiles"] if t["t"] == "sw"]
            pts += [(v[0], v[1], 0.9) for v in r["levers"].values()]
    return pts


def puzzles(area):
    """Adds the puzzle pieces to <area>/scene.json (objects `svart_pz`, collision blockers, game.pz spec). Idempotent; runs AFTER place()."""
    import base64, math
    from array import array
    if area not in PZ: return
    sp = GAME / "areas" / area / "scene.json"; sc = json.loads(sp.read_text())
    pieces = json.loads((PUZ / "kit" / "kit.json").read_text())["pieces"]; old = json.loads((ST / "kit" / "kit.json").read_text())["pieces"]
    C = sc["collision"]
    d = array("h"); d.frombytes(base64.b64decode(C["data"]))
    base = array("h"); base.frombytes(base64.b64decode(C["base_data"]))
    ox, oz, cl, W, H = C["origin"][0], C["origin"][1], C["cell"], C["w"], C["h"]
    sc["objects"] = [o for o in sc["objects"] if not o.get("svart_pz")]
    sc["lamps"] = [l for l in sc["lamps"] if not l.get("svart_pz")]
    idx = lambda x, z: int((z - oz) / cl) * W + int((x - ox) / cl)
    ground = lambda x, z: max(0, base[idx(x, z)]) / 100

    mine = set()

    def block(x0, z0, x1, z1, tag):
        n = bad = 0
        for j in range(int((z0 - oz) / cl), int((z1 - oz) / cl) + 1):
            for i in range(int((x0 - ox) / cl), int((x1 - ox) / cl) + 1):
                k = j * W + i
                if d[k] == -32768:
                    if k not in mine: bad += 1
                else: d[k] = -32768; mine.add(k); n += 1
        if bad: print(f"  WARNING {area}: {tag} overlaps {bad} already-blocked cells")
        return n

    def add(name, x, z, pzid=None, rot=0, hidden=False, blk=True, y=None, wal=False):
        pc = pieces.get(name) or old.get(name) or {"file": f"{name}.glb", "blockers": [[-0.4, -0.4, 0.4, 0.4]]}   # (crate: the base kit's, a chest stand-in)
        yy = ground(x, z) if y is None else y
        o = {"glb": f"public/art/kit/{pc['file']}", "pos": [round(x, 3), round(yy, 3), round(z, 3)], "rot": rot, "svart_pz": True}
        if pzid: o["pz"] = pzid
        if hidden: o["hidden"] = True
        if wal: o.update(walkable=True, cast=False)
        sc["objects"].append(o)
        if blk:
            for b in pc.get("blockers", []):
                c, s_ = math.cos(math.radians(rot)), math.sin(math.radians(rot))   # three.js y-rotation of local (x, z)
                pts = [(bx * c + bz * s_, -bx * s_ + bz * c) for bx in (b[0], b[2]) for bz in (b[1], b[3])]
                block(x + min(p[0] for p in pts), z + min(p[1] for p in pts), x + max(p[0] for p in pts), z + max(p[1] for p in pts), name)
        return yy

    spec = []
    for r in PZ[area]:
        R = {k: v for k, v in r.items()}
        rid = r["id"]
        if r["kind"] == "gear":
            for q in R["pegs"]:
                x, z = q["pos"]; y = add("peg_empty", x, z, f"{rid}:peg:{q['id']}"); add("peg_filled", x, z, f"{rid}:pf:{q['id']}", hidden=True, blk=False)
                q["y"] = round(y + 0.46, 3)
            for q in R["loose"]:
                q["y"] = round(ground(*q["pos"]) + 0.05, 3)
            allc = [(q["cog"], q["id"]) for q in R["pegs"] if q.get("cog")]
            for q in R["pegs"]:
                if q.get("cog"):
                    q["cogid"] = f"{rid}:{q['id']}"
            for q in R["pegs"]:
                if q.get("cog"):
                    add({"s": "cog_small", "m": "cog_medium", "l": "cog_large"}[q["cog"]], q["pos"][0], q["pos"][1], f"{rid}:cog:{q['cogid']}", blk=False, y=q["y"])
            for q in R["loose"]:
                add({"s": "cog_small", "m": "cog_medium", "l": "cog_large"}[q["size"]], q["pos"][0], q["pos"][1], f"{rid}:cog:{rid}:{q['id']}", blk=False, y=q["y"])
            x, z = R["reset"]; add("lever_up", x, z, f"{rid}:lv:up"); add("lever_down", x, z, f"{rid}:lv:dn", hidden=True, blk=False)
            R["reset_y"] = round(ground(x, z), 3)
        else:
            X, BX = R["x"], R["branch_x"]
            for t in R["tiles"]:
                z = t["z"]; t["y"] = round(ground(X, z) + 0.0, 3)
                if t["t"] == "end": add("rail_end", X, z, rot=t["rot"])
                elif t["t"] == "st": add("rail_straight", X, z, rot=0, wal=True)
                else:
                    add("rail_switch_right", X, z, f"{rid}:{t['sw']}:tile"); add("rail_end", BX, z, rot=270)   # the east branch ends in a buffer (S exit rotated to W)
            for k, (x, z) in R["levers"].items():
                add("lever_up", x, z, f"{rid}:{k}:up"); add("lever_down", x, z, f"{rid}:{k}:dn", hidden=True, blk=False)
            R["lever_y"] = round(ground(*R["levers"]["sw1"]), 3)
            cx, cz = R["start"]; add("mine_cart", cx, cz, f"{rid}:cart", blk=False, y=round(ground(cx, cz) + 0.13, 3)); R["cart_y"] = round(ground(cx, cz) + 0.13, 3)
        g = R.get("gate")
        if g:
            x, z = g["pos"]; yy = ground(x, z)
            if g["kind"] == "ram": pass
            pc = old["gear_wall"]; b = pc["blockers"][0] if pc.get("blockers") else [-1.2, -0.25, 1.2, 0.25]
            cells0 = []
            x0, z0, x1, z1 = x + b[0], z + b[1], x + b[2], z + b[3]
            for j in range(int((z0 - oz) / cl), int((z1 - oz) / cl) + 1):
                for i in range(int((x0 - ox) / cl), int((x1 - ox) / cl) + 1):
                    k = j * W + i
                    if d[k] != -32768: cells0.append([i, j, d[k]])
            add("gear_wall", x, z, f"{rid}:gate", blk=True)
            g["cells"] = cells0; g["y"] = round(yy, 3)
        ch = R.get("chest")
        if ch:
            x, z = ch["pos"]; add("crate", x, z, f"{rid}:chest"); ch["y"] = round(ground(x, z), 3)
        R["y"] = round(ground(*(R["pegs"][0]["pos"] if r["kind"] == "gear" else (R["x"], R["tiles"][0]["z"]))), 3)
        spec.append(R)
    C["data"] = base64.b64encode(d.tobytes()).decode()
    sc["game"]["pz"] = spec
    sp.write_text(json.dumps(sc, indent=1))
    print(f"  {area}: puzzles {[r['id'] for r in spec]}")


WALK = {"rail_straight", "glow_pool", "deep_floor"}   # flat decals: walkable, no blocker


def place(area):
    import base64, math
    from array import array
    sp = GAME / "areas" / area / "scene.json"; sc = json.loads(sp.read_text())
    pieces = json.loads((ST / "kit" / "kit.json").read_text())["pieces"]
    C = sc["collision"]; C.setdefault("base_data", C["data"])
    d = array("h"); d.frombytes(base64.b64decode(C["base_data"]))
    ox, oz, cl, W, H = C["origin"][0], C["origin"][1], C["cell"], C["w"], C["h"]
    sc["objects"] = [o for o in sc["objects"] if not o.get("svart_art") and not o.get("svart_pz")]
    sc["lamps"] = [l for l in sc["lamps"] if not l.get("svart_art") and not l.get("svart_pz")]
    g = sc["game"]
    keep = [(a["pos"][0], a["pos"][1], 1.6) for a in sc.get("actors", []) if "pos" in a]
    keep += [(v[0], v[1], 2.0) for v in g.get("spawns", {}).values()]
    keep += pz_points(area)   # the gear / rail puzzles keep their footprints clear of props
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
    sprites(a); kit(a); fx = gamefx(a); place(a); puzzles(a)
    print(f"{a}: sprites + kit + props{' + gamefx' if fx else ' (no gamefx atlas)'}")
