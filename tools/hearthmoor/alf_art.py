"""[ALFHEIM] Minimal, additive art build for the Alfheim areas (realm-alfheim branch).

Wires the staging art in games/hearthmoor/art/alfheim/ into the four built Alfheim areas WITHOUT re-assembling:
  sprites  lumi + alfheim_npcs + prism_vault_enemies become extra sheets of each area's actors.json
           (townsfolk roles re-pointed: lanternseller->elf_lampwright, wispcatcher->elf_child,
            poolkeeper->elf_gardener, librarian->elf_scholar; prismshard / mirrorduelist use the staging sheet)
  kit      staging .glb files are copied in; a name clash takes the staging piece (lumen_tree, light_bridge, vault_pillar ...)
  gamefx   staging alfheim_fx rows are appended under the area's gamefx atlas; a name clash takes the staging effect
Never deletes anything: it only writes files and rewrites actors.json / gamefx.json / gamefx.png. Idempotent: the
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
    if not (d / "gamefx.json").exists():
        return False
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


for a in AREAS:
    sprites(a); kit(a); fx = gamefx(a)
    print(f"{a}: sprites + kit{' + gamefx' if fx else ' (no gamefx atlas)'}")
