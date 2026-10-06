"""hd2d assemble: scene spec (JSON) -> playable static folder + zip.

    hd2d assemble scenes/hearthmoor-plaza.json --out demos/hearthmoor-plaza [--no-zip] [--shots]

Runs every tool for the scene's biome + seed (palette, sprite, texel, kit, trees, particles), builds the
scene-specific kit pieces (terraces with stair gaps, stairs, slabs, bunting, hedges), copies the runtime,
resolves markers (lamps, chimneys, stall vendor) to world space, bakes the collision heightfield,
writes scene.json + README.md and <out>.zip (skip with --no-zip; --shots runs check-scene and re-zips). Follows the style-lock scene recipe:
plaza, 3 houses, 1 stair, 1 tree, 2-4 actors, key light + 2 lamps, props.
"""
from __future__ import annotations

import argparse
import base64
import json
import math
import shutil
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
import numpy as np  # noqa: E402

from hd2d_common import SUITE, art_dir, ensure, load_tool, read_json, write_json  # noqa: E402


def rot_y(deg, x, z):
    a = math.radians(deg)
    # three.js rotation.y: x' = x cos + z sin, z' = -x sin + z cos
    return x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)


def to_world(local, pos, rot):
    x, z = rot_y(rot, local[0], local[2])
    return [round(pos[0] + x, 3), round(pos[1] + local[1], 3), round(pos[2] + z, 3)]


class Heights:
    """Analytic walk heights from slabs, terraces and stairs; blockers as world AABBs."""

    def __init__(self, spec):
        self.rects = []   # (x0, z0, x1, z1, h)
        self.stairs = []
        self.blocks = []  # (x0, z0, x1, z1)
        self.circles = []
        for s in spec.get("slabs", []):
            x0, z0, x1, z1 = s["rect"]
            self.rects.append((x0, z0, x1, z1, s.get("h", 0)))
        for t in spec.get("terraces", []):
            x0, z0, x1, z1 = t["rect"]
            self.rects.append((x0, z0, x1, z1, t["h"]))
        for st in spec.get("stairs", []):
            self.stairs.append(st)
        # decks: walk-height-only rects (piers whose planks are a prop, no slab mesh); blocks: unwalkable rects (water)
        for d in spec.get("decks", []):
            x0, z0, x1, z1 = d["rect"]
            self.rects.append((x0, z0, x1, z1, d.get("h", 0)))
        for b in spec.get("blocks", []):
            self.blocks.append(tuple(b["rect"] if isinstance(b, dict) else b))
        # floating islands (the Rift Shrine): walk only inside an ellipse [cx, cz, rx, rz] (blocked outside it)
        self.ellipse = spec["ground"].get("ellipse")

    def h(self, x, z):
        best = 0.0
        for x0, z0, x1, z1, h in self.rects:
            if x0 <= x < x1 and z0 <= z < z1:
                best = max(best, h)
        for st in self.stairs:
            w = st["width"] / 2
            L = st["_L"]
            zt, zb = st["z_top"], st["z_top"] + L
            if abs(x - st["x"]) < w and zt <= z < zb:
                best = max(best, st.get("base", 0) + st["rise"] * min(1, max(0, (zb - z) / L)))
        return best

    def blocked(self, x, z):
        if self.ellipse:
            ex, ez, rx, rz = self.ellipse
            if ((x - ex) / rx) ** 2 + ((z - ez) / rz) ** 2 > 1.0:
                return True
        for x0, z0, x1, z1 in self.blocks:
            if x0 <= x < x1 and z0 <= z < z1:
                return True
        for cx, cz, r in self.circles:
            if (x - cx) ** 2 + (z - cz) ** 2 < r * r:
                return True
        return False


def bake(H: Heights, walk, cell=0.25):
    x0, z0, x1, z1 = walk
    w, h = int(round((x1 - x0) / cell)), int(round((z1 - z0) / cell))
    arr = np.zeros((h, w), np.int16)
    for j in range(h):
        z = z0 + (j + 0.5) * cell
        for i in range(w):
            x = x0 + (i + 0.5) * cell
            arr[j, i] = -32768 if H.blocked(x, z) else int(round(H.h(x, z) * 100))
    return {"origin": [x0, z0], "cell": cell, "w": w, "h": h, "max_step": 0.36,
            "data": base64.b64encode(arr.astype("<i2").tobytes()).decode()}


def assemble(spec_path, out, do_zip=True):
    spec = read_json(spec_path)
    out = ensure(out)
    biome, seed = spec["biome"], spec.get("seed", 1)
    print(f"assemble: {spec['name']} ({biome}, seed {seed}) -> {out}")
    # 1-6: the tools, outputs in public/art/<tool>
    pal_dir = art_dir(out, "palette")
    load_tool("palette").build(biome, pal_dir)
    roles = sorted({a["role"] for a in spec.get("actors", [])} | {spec["player"]["role"]})
    SP = load_tool("sprite")
    all_roles = [r for r in SP.ROLES if r not in SP.EXTRA]
    if spec.get("sprite_roles"):  # e.g. ["actors", "heroes", "combat"]: keep the atlas under 4096 px tall
        pick = []
        for tok in spec["sprite_roles"]:
            pick += (roles if tok == "actors" else list(SP.RH.HERO_ORDER) if tok == "heroes"
                     else [r for r in SP.ROLES if r in SP.EXTRA and not SP.ROLES[r].get("named")] if tok == "combat" else [tok])
        all_roles = [r for r in dict.fromkeys(pick) if r in SP.ROLES]
    # boss roles (style lock: mini-bosses ~2.5x, bosses 5x+) are drawn natively on their own sheet with bigger frames;
    # the main atlas lists them as stubs `{sheet: "boss", ...}` and the engine swaps frame size + texture per role
    boss_roles = [r for r in spec.get("boss_roles", [])]
    all_roles = [r for r in all_roles if r not in boss_roles]
    sp = SP.build(biome, all_roles, art_dir(out, "sprite"), out, seed)
    if boss_roles:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "sprite"))
        import boss_sheet as BS  # noqa: E402
        # [ALFHEIM] begin: one sheet per frame size ("boss" = the first size, then "boss2", "boss3": a 6x boss + 2.8x minis share an area)
        groups = {}
        for r in boss_roles:
            groups.setdefault(tuple(BS.BOSS[r]["frame"]), []).append(r)
        mp = Path(sp["json"]); m = json.loads(mp.read_text())
        m["sheets"] = {}
        for gi, grp in enumerate(groups.values()):
            nm = "boss" if gi == 0 else f"boss{gi + 1}"
            bs = BS.build(biome, tuple(grp), art_dir(out, "sprite"), out, nm)
            bm = json.loads(Path(bs["json"]).read_text())
            m["sheets"][nm] = {"json": f"{nm}.json", "image": f"{nm}.png"}
            for r in grp:
                br = bm["roles"][r]
                m["roles"][r] = {"sheet": nm, "row": br["row"], "kind": br["kind"], "enemy": True, "boss": True,
                                 "scale": br["scale"], "frame": bm["frame"], "anims": br["anims"], "desc": br["desc"]}
        # [ALFHEIM] end
        mp.write_text(json.dumps(m, indent=1))
    load_tool("texel").build(biome, (32, 64), None, art_dir(out, "texel"), out, seed)
    # scene-specific kit pieces
    extra = []
    gw, gd = spec["ground"]["size"]
    extra.append(("ground", dict(w=gw, d=gd, mat=spec["ground"].get("mat", "grass"), h=0.0, name="scene_ground")))
    for s in spec.get("slabs", []):
        x0, z0, x1, z1 = s["rect"]
        extra.append(("ground", dict(w=x1 - x0, d=z1 - z0, mat=s["mat"], h=s.get("h", 0.1), name=f"scene_{s['name']}")))
    for t in spec.get("terraces", []):
        x0, z0, x1, z1 = t["rect"]
        cx = (x0 + x1) / 2
        gaps = [(g0 - cx, g1 - cx) for g0, g1 in t.get("gaps", [])]
        extra.append(("terrace", dict(w=x1 - x0, d=z1 - z0, h=t["h"], top=t.get("top", "cobble"), coping=t.get("coping", True),
                                      gaps=gaps, name=f"scene_{t['name']}")))
    for st in spec.get("stairs", []):
        extra.append(("stairs", dict(width=st["width"], rise=st["rise"], name=f"scene_{st['name']}")))
    for i, b in enumerate(spec.get("bunting", [])):
        extra.append(("bunting", dict(p0=tuple(b["from"]), p1=tuple(b["to"]), sag=b.get("sag", 0.4), name=f"scene_bunting_{i}")))
    for i, hd in enumerate(spec.get("hedges", [])):
        extra.append(("hedge", dict(length=hd["length"], name=f"scene_hedge_{i}")))
    for i, ln in enumerate(spec.get("laundry", [])):
        extra.append(("laundry", dict(p0=tuple(ln["from"]), p1=tuple(ln["to"]), sag=ln.get("sag", 0.25),
                                      base0=ln.get("base", [0, 0])[0], base1=ln.get("base", [0, 0])[1],
                                      name=f"scene_laundry_{i}", seed=i)))
    kit = load_tool("kit").build(biome, art_dir(out, "kit"), art_dir(out, "texel"), out, seed, extra)
    P = kit["pieces"]
    trees = load_tool("trees").build(biome, art_dir(out, "trees"), out, seed=3, count=3, texel=art_dir(out, "texel"))
    load_tool("particles").build(biome, art_dir(out, "particles"), out, seed)
    use_spells = bool(spec.get("spells")) or any(a.get("behavior") == "caster" for a in spec.get("actors", []))
    if use_spells:
        load_tool("spells").build(biome, art_dir(out, "spells"), out, seed)
    portal_pieces = {"portal_arch"}
    use_gamefx = bool(spec.get("fx")) or bool(spec.get("gamefx")) or any(p["piece"] in portal_pieces for p in spec.get("props", []))
    if use_gamefx:
        load_tool("portal").build(biome, art_dir(out, "gamefx"), out, seed)
    load_tool("runtime").copy_to(out)
    colors = __import__("hd2d_common").load_biome(biome, out)["colors"]
    fx_out = []

    # ---- resolve the scene
    for st in spec.get("stairs", []):
        st["_L"] = P[f"scene_{st['name']}"]["stairs"]["length"]
    H = Heights(spec)
    objects, lamps, chimneys, emitters = [], [], [], []
    vendor_at = {}

    def kitpath(name):
        return f"public/art/kit/{P[name]['file']}"

    objects.append({"glb": kitpath("scene_ground"), "pos": [0, 0, 0], "walkable": True, "cast": False})
    for s in spec.get("slabs", []):
        x0, z0, x1, z1 = s["rect"]
        objects.append({"glb": kitpath(f"scene_{s['name']}"), "pos": [(x0 + x1) / 2, 0, (z0 + z1) / 2], "walkable": True})
    for t in spec.get("terraces", []):
        x0, z0, x1, z1 = t["rect"]
        objects.append({"glb": kitpath(f"scene_{t['name']}"), "pos": [(x0 + x1) / 2, 0, (z0 + z1) / 2], "walkable": True, "occluder": True})
    for st in spec.get("stairs", []):
        L = st["_L"]
        objects.append({"glb": kitpath(f"scene_{st['name']}"), "pos": [st["x"], st.get("base", 0), st["z_top"] + L / 2], "walkable": True})
        w = st["width"] / 2
        for sx in (-1, 1):
            xa = st["x"] + sx * (w + 0.16)
            H.blocks.append((xa - 0.2, st["z_top"], xa + 0.2, st["z_top"] + L + 0.1))

    def place(name, pos2, rot=0, occ=False, dy=0.0, glow=None):
        info = P[name]
        y = H.h(pos2[0], pos2[1]) + dy
        pos = [pos2[0], y, pos2[1]]
        objects.append({"glb": kitpath(name), "pos": pos, "rot": rot, **({"occluder": True} if occ else {})})
        for b in info["blockers"]:
            xs, zs = [], []
            for (lx, lz) in ((b[0], b[1]), (b[2], b[1]), (b[0], b[3]), (b[2], b[3])):
                wx, wz = rot_y(rot, lx, lz)
                xs.append(pos[0] + wx); zs.append(pos[2] + wz)
            H.blocks.append((min(xs), min(zs), max(xs), max(zs)))
        mk = info["markers"]
        for L in mk.get("lamps", []):
            lamp = {"pos": to_world(L, pos, rot), "range": 7.5 if name == "lamp_post" else 5.5, "kind": name}
            if "lamp_color" in mk:   # e.g. Ravenhold's cold-fire lanterns (neon blue); 'lamp_fixed' = a steady glow level
                lamp["color"] = mk["lamp_color"]
            if "lamp_fixed" in mk:
                lamp["fixed"] = mk["lamp_fixed"]
            if "lamp_range" in mk:
                lamp["range"] = mk["lamp_range"]
            lamps.append(lamp)
        for c in mk.get("chimneys", []):
            chimneys.append(to_world(c, pos, rot))
        if "vendor" in mk:
            vendor_at[name] = to_world(mk["vendor"], pos, rot)
        for i, pm in enumerate(mk.get("portal", [])):
            w = to_world(pm, pos, rot)
            n = len([f for f in fx_out if f["name"] == "portal_vortex"])
            fx_out.append({"id": f"portal_{n}", "name": "portal_vortex", "pos": w})
            fr = to_world([pm[0], pm[1], pm[2] + 1.25], pos, rot)
            fx_out.append({"id": f"portal_{n}_ring", "name": "portal_ring", "pos": [fr[0], round(pos[1], 3), fr[2]]})
            lamps.append({"pos": [w[0], w[1] + 1.4, w[2] + 0.6], "range": 6.0, "kind": "portal", "color": colors["sky"], "glow": False, "fixed": 0.75})
            emitters.append({"preset": "fireflies", "pos": [w[0], w[1] + 1.2, w[2] + 0.8], "area": [2.2, 1.6, 1.4], "min_gate": 0.45})
        for rm in mk.get("rift", []):   # rift / vine gates: the spec's fx list places the vortex; the prop's glow lights it
            if glow:
                w = to_world(rm, pos, rot)
                lamps.append({"pos": [w[0], w[1] + 1.5, w[2] + 0.7], "range": glow.get("range", 5.0), "kind": "rift",
                              "color": glow["color"], "glow": False, "fixed": glow.get("fixed", 0.6)})
        for o in mk.get("ovens", []):
            emitters.append({"preset": "oven_steam", "pos": to_world(o, pos, rot)})
        for sp_ in mk.get("spray", []):
            w = to_world(sp_, pos, rot)
            emitters.append({"preset": "fountain_spray", "pos": w, "floor": round(pos[1] + mk.get("water", 0.4), 3)})
        return pos

    for b in spec.get("buildings", []):
        place(b["piece"], b["pos"], b.get("rot", 0), occ=True)
    for p in spec.get("props", []):
        n0 = len(objects)
        place(p["piece"], p["pos"], p.get("rot", 0), occ=p["piece"] in ("market_stall",), dy=p.get("y", 0.0), glow=p.get("glow"))
        if p.get("walkable"):   # e.g. the Rift isle's paved top: taps / clicks land on it
            objects[n0]["walkable"] = True
        if p.get("cast") is False:
            objects[n0]["cast"] = False
    for i, hd in enumerate(spec.get("hedges", [])):
        place(f"scene_hedge_{i}", hd["pos"], hd.get("rot", 0))
    for i, b in enumerate(spec.get("bunting", [])):
        objects.append({"glb": kitpath(f"scene_bunting_{i}"), "pos": [0, 0, 0], "cast": True})
    for i, ln in enumerate(spec.get("laundry", [])):
        objects.append({"glb": kitpath(f"scene_laundry_{i}"), "pos": [0, 0, 0], "cast": True})
        for end in ("from", "to"):
            px_, pz_ = ln[end][0], ln[end][2]
            H.blocks.append((px_ - 0.15, pz_ - 0.15, px_ + 0.15, pz_ + 0.15))
    if spec.get("backdrop", {}).get("hills"):
        hx, hz = spec["backdrop"]["hills"]
        objects.append({"glb": kitpath("hills"), "pos": [hx, 1.6 if hz < -11 else 0, hz], "cast": False})

    tree_out = []
    tdefs = trees["trees"]
    for t in spec.get("trees", []):
        name = next((k for k, v in tdefs.items() if v["type"] == t["type"]), next(iter(tdefs)))
        y = H.h(*t["pos"])
        tree_out.append({"tree": name, "pos": [t["pos"][0], y, t["pos"][1]], "scale": t.get("scale", 1), "lowpoly": t.get("lowpoly", False)})
        H.circles.append((t["pos"][0], t["pos"][1], tdefs[name]["blocker"]))
        emitters.append({"preset": "leaf_bits", "pos": [t["pos"][0], y + tdefs[name]["height"] * 0.6, t["pos"][1] + 0.6], "area": [3.5, 1.5, 1.6]})
    for c in chimneys:
        emitters.append({"preset": "chimney_wisp", "pos": c})
    for L in lamps:
        if L["kind"] == "lamp_post":
            emitters.append({"preset": "lamp_bugs", "pos": [L["pos"][0], 1.7 + L["pos"][1] - 3.0, L["pos"][2]], "area": [3, 1.4, 3]})
    emitters += spec.get("emitters", [])
    for f in spec.get("fx", []):
        p_ = f["pos"]
        fx_out.append({**f, "pos": [p_[0], H.h(p_[0], p_[1]), p_[1]] if len(p_) == 2 else p_})

    # blocked outside the walk rect and where the back terrace climbs into the hills
    actors = []
    for a in spec.get("actors", []):
        a = dict(a)
        if a.get("at") == "stall_vendor":
            v = vendor_at.get("market_stall")
            a["pos"] = [v[0], v[2]]
        a.pop("at", None)
        actors.append(a)
    coll = bake(H, spec["ground"]["walk"])
    scene = {
        "name": spec["name"], "about": spec.get("about", ""), "biome": biome, "seed": seed,
        "palette": f"public/art/palette/{biome}/biome.json",
        "atlas": {"image": "public/art/sprite/" + Path(sp["atlas"]).name, "json": "public/art/sprite/" + Path(sp["json"]).name},
        "particles": {"image": "public/art/particles/particles.png", "json": "public/art/particles/particles.json"},
        "trees_meta": "public/art/trees/trees.json", "trees_base": "public/art/trees/",
        "camera": spec["camera"], "time": spec.get("time", {}), "shadow_box": spec.get("shadow_box", 22),
        **({"spells": {"image": "public/art/spells/spells.png", "json": "public/art/spells/spells.json"}} if use_spells else {}),
        **({"weather": spec["weather"]} if spec.get("weather") else {}),
        **({"grades": spec["grades"]} if spec.get("grades") else {}),
        **({"spell_cycle": spec["spell_cycle"]} if spec.get("spell_cycle") else {}),
        **({"gamefx": {"image": "public/art/gamefx/gamefx.png", "json": "public/art/gamefx/gamefx.json"}, "fx": fx_out} if use_gamefx else {}),
        **({"game": spec["game"]} if spec.get("game") else {}),
        "objects": objects, "trees": tree_out, "lamps": lamps, "emitters": emitters,
        "actors": actors, "player": spec["player"], "collision": coll,
        "recipe": {"houses": len(spec.get("buildings", [])), "stairs": len(spec.get("stairs", [])), "trees": len(tree_out),
                   "actors": len(actors) + 1, "lamps": len(lamps), "props": len(spec.get("props", []))},
    }
    write_json(out / "scene.json", scene, compact=True)
    shutil.copy2(spec_path, out / "scene.src.json")
    write_readme(out, spec, scene)
    zpath = None
    if do_zip:
        zpath = make_zip(out)
    print(f"assemble: {len(objects)} objects, {len(lamps)} lamps, {len(emitters)} emitters, {len(actors) + 1} actors")
    if zpath:
        print(f"assemble: zip -> {zpath}")
    return out, zpath


def write_readme(out, spec, scene):
    r = scene["recipe"]
    spell_txt = ""
    if scene.get("spells"):
        cyc = ", ".join(scene.get("spell_cycle") or [])
        spell_txt = ("- **Spells:** F casts the current spell (then advances), Q picks the next one. The HUD chip shows it, and on the pad "
                     "tap the ✦ button to cast or hold it to pick the next spell." + (f" Cycle: {cyc}." if cyc else "") +
                     "\n- `?showcase=particles` shows every particle preset; `?weather=rain|snow` adds weather.\n")
    (out / "README.md").write_text(f"""# {spec['name']}

{spec.get('about', '')}

Built by `hd2d assemble` (hd2d-suite) from `scene.src.json`. Static three.js r160 ES modules with an import map:
no build step, no network.

## Play
```bash
hd2d serve {out}            # http://127.0.0.1:8077/
# or: cd {out.name} && python3 -m http.server 8077
```
- Desktop: WASD / arrows to walk (Shift runs), click or tap the ground to walk there, E / Space to talk,
  wheel or +/- to zoom (limited). T steps the clock (golden, dusk, night, dawn, day), P pauses it, G toggles the pad.
- Phone: tap to walk, tap a villager to talk, pinch to zoom. The **pad** button shows the Game Layout One pad
  (stick with 13 % deadzone and outer-ring run, MAIN = talk / hold 0.35 s, potion pills greyed, rail hidden when empty).
- URL options: `?t=day|golden|dusk|night|0.0-1.0`, `?freeze` (stop the clock), `?pad`, `?hud=0`, `?ss=1` (world supersample).
{spell_txt}
## Recipe (style lock section 5)
{r['houses']} houses, {r['stairs']} stair, {r['trees']} tree, {r['actors']} actors (incl. the player), {r['lamps']} lamps
(lamp posts + wall lamps{' + oven glow' if any(o.get('glb','').endswith('bakery.glb') for o in scene.get('objects', [])) else ''}) under one key sun, {r['props']} props.

## Folders
- `public/art/palette` biome palette + grades, `sprite` actor atlas, `texel` textures, `kit` .glb pieces,
  `trees` layered-card trees, `particles` sheets + presets.
- `engine/` runtime, `vendor/` three.js r160 + GLTFLoader, `shots/` QA screenshots.

Credits: canopy art from brileta-sprites (MIT, Mark Ayzenshtat). Everything else generated by hd2d-suite.
""")


def make_zip(out: Path) -> Path:
    out = Path(out)
    zpath = out.parent / f"{out.name}.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(out.rglob("*")):
            if p.is_file() and "iterations" not in p.parts:
                z.write(p, Path(out.name) / p.relative_to(out))
    return zpath


def serve_main(argv):
    ap = argparse.ArgumentParser(prog="hd2d serve")
    ap.add_argument("dir")
    ap.add_argument("--port", type=int, default=8077)
    ap.add_argument("--host", default="127.0.0.1")
    a = ap.parse_args(argv)
    import functools
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

    class H(SimpleHTTPRequestHandler):
        extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".js": "text/javascript", ".mjs": "text/javascript",
                          ".json": "application/json", ".glb": "model/gltf-binary"}
    srv = ThreadingHTTPServer((a.host, a.port), functools.partial(H, directory=a.dir))
    print(f"serving {a.dir} at http://{a.host}:{a.port}/  (Ctrl-C to stop)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="hd2d assemble", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--shots", action="store_true", help="run check-scene afterwards")
    a = ap.parse_args(argv)
    out, z = assemble(a.spec, a.out, not a.no_zip)
    if a.shots:
        rc = load_tool("check-scene").main([str(out)])
        if not a.no_zip:
            print("re-zipped with shots:", make_zip(out))
        return rc
    return 0


if __name__ == "__main__":
    sys.exit(main())
