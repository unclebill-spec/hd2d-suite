"""Build Hearthmoor: assemble the three area specs with the hd2d tools, copy the runtime once, prune each area to
the files its scene.json uses, draw the HUD item icons + app icons, write the service-worker file list, zip.

    python3 games/hearthmoor/build.py [--no-zip]
"""
import argparse
import hashlib
import os
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

GAME = Path(__file__).resolve().parent
SUITE = GAME.parents[1]
sys.path.insert(0, str(SUITE))
from PIL import Image  # noqa: E402

from hd2d_common import load_biome  # noqa: E402

AREAS = ["plaza", "lane", "mossglen", "hollows", "rift", "vanaheim", "ravenhold", "bifrost", "temple", "rotwood", "verdant", "forge",
         "alfheim", "lumen_court", "wispwood", "prismvault",
         "svartalfheim", "forge_hall", "glowmines", "clockdeep", "clockdeep2",
         "vh_village", "vh_garden"]   # [VANAHEIM] Stage B: Mossbrook village + the Thorngarden (vanaheim kit reuse; tools/hearthmoor/vh_art.py adds the realm sheets)   # [ALFHEIM] Lumenvale (Glimmer Steps, Lumen Court, Wispwood) + the Prism Vault
# [JOTUNHEIM] the realm's areas join the build only once their specs exist (hold until art/jotunheim/READY.txt): no spec, no change
AREAS += [a for a in ("jotunheim", "jt_hall", "rimecaves", "barrow", "barrow2") if (Path(__file__).resolve().parent / "areas" / "src" / f"{a}.json").exists()]
# [MUSPELHEIM] the realm's areas join the build only once the art pack is ready (staging art/muspelheim/READY.txt) and their specs exist: no READY.txt, no change.
# HM_MUSP_SKELETON=1 lets a QA run include the skeleton specs without the pack (private build dir only: never commit that output).
if os.environ.get("HM_MUSP_SKELETON") or Path("/workspace/hearthmoor-staging/art/muspelheim/READY.txt").exists():
    AREAS += [a for a in ("muspelheim", "mp_hall", "lavafalls", "caldera", "caldera2") if (Path(__file__).resolve().parent / "areas" / "src" / f"{a}.json").exists()]
# [NIFLHEIM] the realm's areas join the build only once the art pack is ready (staging art/niflheim/READY.txt) and their specs exist: no READY.txt, no change.
# HM_NIFL_SKELETON=1 lets a QA run include the skeleton specs without the pack (private build dir only: never commit that output).
if os.environ.get("HM_NIFL_SKELETON") or Path("/workspace/hearthmoor-staging/art/niflheim/READY.txt").exists():
    AREAS += [a for a in ("niflheim", "nf_home", "iceglow", "frozenspire", "frozenspire2", "frozen_rift") if (Path(__file__).resolve().parent / "areas" / "src" / f"{a}.json").exists()]
# [ASGARD] the realm's areas join the build only once the art pack is ready (staging art/asgard/READY.txt) and their specs exist: no READY.txt, no change.
if Path("/workspace/hearthmoor-staging/art/asgard/READY.txt").exists():
    AREAS += [a for a in ("asgard", "gs_hall", "gs_temple", "reliquary", "reliquary2") if (Path(__file__).resolve().parent / "areas" / "src" / f"{a}.json").exists()]
# [HELHEIM] the realm's areas join the build only once the art pack is ready (staging art/helheim/READY.txt) and their specs exist: no READY.txt, no change.
if Path("/workspace/hearthmoor-staging/art/helheim/READY.txt").exists():
    AREAS += [a for a in ("helheim", "hh_shore", "hh_archive", "ossuary", "ossuary2") if (Path(__file__).resolve().parent / "areas" / "src" / f"{a}.json").exists()]
TMP = Path(os.environ.get("HM_BUILD_TMP", "/tmp/hearthmoor_build"))   # [ALFHEIM] private build dir per worker


def sh(*a):
    subprocess.run([str(x) for x in a], check=True)


def assemble(areas=AREAS):
    for a in areas:
        out = TMP / a
        if out.exists():
            shutil.rmtree(out)
        sh(SUITE / "bin" / "hd2d", "assemble", GAME / "areas" / "src" / f"{a}.json", "--out", out, "--no-zip")


def used_files(scene, root):
    """every asset path the runtime will fetch for this scene"""
    keep = {"scene.json"}
    keep.add(scene["palette"])
    for k in ("atlas", "particles", "spells", "gamefx"):
        if scene.get(k):
            keep.add(scene[k]["image"]); keep.add(scene[k]["json"])
    if scene.get("atlas"):   # boss sheets next to the actor atlas (meta.sheets)
        am = json.loads((root / scene["atlas"]["json"]).read_text())
        d = scene["atlas"]["json"].rsplit("/", 1)[0] + "/"
        for sh in am.get("sheets", {}).values():
            keep.add(d + sh["image"]); keep.add(d + sh["json"])
    for o in scene["objects"]:
        keep.add(o["glb"])
    if scene.get("trees_meta"):
        keep.add(scene["trees_meta"])
        meta = json.loads((root / scene["trees_meta"]).read_text())
        names = {t["tree"] for t in scene.get("trees", [])}
        for n, t in meta["trees"].items():
            if n in names:
                for v in t.values():
                    if isinstance(v, str) and v.endswith((".glb", ".png")):
                        keep.add(scene["trees_base"] + v)
                    if isinstance(v, dict):
                        for w in v.values():
                            if isinstance(w, str) and w.endswith((".glb", ".png")):
                                keep.add(scene["trees_base"] + w)
                    if isinstance(v, list):
                        for w in v:
                            if isinstance(w, str) and w.endswith((".glb", ".png")):
                                keep.add(scene["trees_base"] + w)
    # textures referenced by the glbs live inside them; texel pngs are kept for the kit (small)
    for p in (root / "public/art/texel").rglob("*.png"):
        keep.add(str(p.relative_to(root)))
    return keep


def copy_areas(areas=AREAS):
    for d in ("engine", "vendor"):
        if (GAME / d).exists():
            shutil.rmtree(GAME / d)
        # always the suite's current runtime (not the assemble output, which is stale with --skip-assemble)
        shutil.copytree(SUITE / "tools/runtime/web" / d, GAME / d, ignore=shutil.ignore_patterns("__pycache__"))
    for a in areas:
        src, dst = TMP / a, GAME / "areas" / a
        if dst.exists():
            shutil.rmtree(dst)
        scene = json.loads((src / "scene.json").read_text())
        keep = used_files(scene, src)
        missing = []
        for rel in sorted(keep):
            s = src / rel
            if not s.exists():
                missing.append(rel); continue
            (dst / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(s, dst / rel)
        # keep the tree folder whole if the meta points at files we did not resolve
        if (src / "public/art/trees").exists():
            shutil.copytree(src / "public/art/trees", dst / "public/art/trees", dirs_exist_ok=True)
        size = sum(f.stat().st_size for f in dst.rglob("*") if f.is_file())
        print(f"area {a}: {len(keep)} files, {size / 1e6:.1f} MB" + (f", missing {missing}" if missing else ""))


# ------------------------------------------------------------------ pets (Stage 6 part 2): one shared pet sheet in every area
# The pet art (art/pets/, from the Hearthmoor Art bot; pets.png is the NEON variant Bill approved 2026-10-05) follows
# the hero everywhere, so every area gets: the pet sheet next to its actor atlas (meta.sheets.pets + stub roles, the
# boss-sheet mechanism), the pet aura / pool effects appended under its spells atlas, and the pet particles appended
# under its particles atlas. Idempotent: a re-run strips the previous pet rows first (`pets_from` remembers the cut).
PET_ROLES = ("pet_wisp", "pet_moth", "pet_fox", "pet_mosspup", "pet_tick")
TICK = GAME / "art" / "svartalfheim" / "tick"   # [SVARTALFHEIM] Tick the clockwork owl: own 240x128 sheet (NEON primary) + 3 fx rows stacked under pets_fx


def _append_atlas(img_path, meta, add_img, add_meta, key, rows_key=None, mark="pets_from"):
    base = Image.open(img_path).convert("RGBA")
    h0 = meta.get(mark, base.size[1])
    base = base.crop((0, 0, base.size[0], h0))
    add = Image.open(add_img).convert("RGBA")
    out = Image.new("RGBA", (max(base.size[0], add.size[0]), h0 + add.size[1]), (0, 0, 0, 0))
    out.paste(base, (0, 0)); out.paste(add, (0, h0))
    out.save(img_path)
    cell = meta["cell"]; row0 = h0 // cell
    items = meta[key]
    for k in list(items):
        if k in add_meta[key]:
            del items[k]
    for k, v in add_meta[key].items():
        v = json.loads(json.dumps(v)); v["row"] = v["row"] + row0
        for f in v.get("frame_list", []):
            f["y"] += h0
        items[k] = v
    if rows_key:
        meta[rows_key] = [r for r in meta[rows_key] if r not in add_meta[rows_key]][:row0] + list(add_meta[rows_key])
    meta[mark] = h0
    meta["size"] = [out.size[0], out.size[1]]
    return meta


# prismvault: pet_aura_moth's dust strip reads as sparse over the vault's dark floor (uniform 0.85 < 0.97); same call as spore_motes / faceless_gaze
PET_FX_SKIP = {"prismvault": {"pet_aura_moth"}}


def install_pets(areas=AREAS):
    P = GAME / "art" / "pets"
    pm = json.loads((P / "pets.json").read_text())
    fxm = json.loads((P / "pets_fx.json").read_text())
    ptm = json.loads((P / "pets_particles.json").read_text())
    tm = json.loads((TICK / "tick.json").read_text())
    tfx = json.loads((TICK / "tick_fx.json").read_text())
    fx_img = P / "pets_fx.png"
    if tfx:   # stack Tick's fx strip under the shared pet fx, so one appended block carries both
        base = Image.open(P / "pets_fx.png").convert("RGBA"); add = Image.open(TICK / "tick_fx.png").convert("RGBA")
        comb = Image.new("RGBA", (max(base.size[0], add.size[0]), base.size[1] + add.size[1]), (0, 0, 0, 0)); comb.paste(base, (0, 0)); comb.paste(add, (0, base.size[1]))
        TMP.mkdir(parents=True, exist_ok=True); fx_img = TMP / "pets_fx_tick.png"; comb.save(fx_img)
        row0, y0 = base.size[1] // fxm["cell"], base.size[1]
        fxm = json.loads(json.dumps(fxm))
        for k, v in tfx["effects"].items():
            v = json.loads(json.dumps(v)); v["row"] += row0
            for f in v.get("frame_list", []):
                f["y"] += y0
            fxm["effects"][k] = v
    for a in areas:
        root = GAME / "areas" / a
        scene = json.loads((root / "scene.json").read_text())
        sp = root / scene["atlas"]["json"]
        am = json.loads(sp.read_text())
        shutil.copy2(P / "pets.png", sp.parent / "pets.png")
        (sp.parent / "pets.json").write_text(json.dumps(pm, indent=1))
        am.setdefault("sheets", {})["pets"] = {"json": "pets.json", "image": "pets.png"}
        for r in PET_ROLES:
            if r == "pet_tick":   # Tick rides its own sheet (tick_neon.png is the primary look; tick.png is the palette-safe fallback)
                shutil.copy2(TICK / "tick_neon.png", sp.parent / "tick.png")
                (sp.parent / "tick.json").write_text(json.dumps(tm, indent=1))
                am["sheets"]["tick"] = {"json": "tick.json", "image": "tick.png"}
                am["roles"][r] = {"sheet": "tick", "row": tm["roles"][r]["row"], "kind": "creature", "pet": True, "anims": ["idle", "walk", "follow"]}
                continue
            am["roles"][r] = {"sheet": "pets", "row": pm["roles"][r]["row"], "kind": "creature", "pet": True, "anims": ["idle", "walk", "follow"]}
        sp.write_text(json.dumps(am, indent=1))
        for k, add_img, add_meta, key, rows in (("spells", fx_img, fxm, "effects", None),
                                                 ("particles", P / "pets_particles.png", ptm, "presets", "rows")):
            jp = root / scene[k]["json"]; ip = root / scene[k]["image"]
            if k == "spells" and a in PET_FX_SKIP:   # sparse strip stays out of this area's atlas (check-scene effects_sharp); the pet keeps its dust particles
                add_meta = {**add_meta, key: {n: v for n, v in add_meta[key].items() if n not in PET_FX_SKIP[a]}}
            m = _append_atlas(ip, json.loads(jp.read_text()), add_img, add_meta, key, rows)
            jp.write_text(json.dumps(m, indent=1))
    print(f"pets: sheet + {len(fxm['effects'])} effects + {len(ptm['presets'])} particle presets in {len(areas)} areas")


OLD_TEMPLE_AREAS = ["temple"]
OLD_TEMPLE_ROLES = ["templekeeper", "archivist"]


def install_old_temple(areas=AREAS):
    """The Old Temple art pack (art/old_temple/, Art bot 2026-10-05): Mother Ilse (templekeeper) and Brother Tamsin
    (archivist) ride in their own sheet like the pets; the riftgate / cold-fire / faceless-gaze / glasslight gamefx are
    appended to the area's gamefx atlas (48 px cells). The kit pieces build through tools/kit/kit_old_temple.py."""
    P = GAME / "art" / "old_temple"
    am_ot = json.loads((P / "sprite" / "old_temple_actors.json").read_text())
    fxm = json.loads((P / "gamefx" / "old_temple_fx.json").read_text())
    # faceless_gaze stays out for now: its eye-glint frames are under check-scene's 20 px measurable minimum (gamefx_sharp
    # counts that as unverified). It belongs to the later 'Faceless Statues' beat; the Art bot can redraw it bigger.
    skip = {"faceless_gaze"}
    fxm = {**fxm, "effects": {k: v for k, v in fxm["effects"].items() if k not in skip}}
    n = 0
    for a in areas:
        if a not in OLD_TEMPLE_AREAS:
            continue
        root = GAME / "areas" / a
        scene = json.loads((root / "scene.json").read_text())
        sp = root / scene["atlas"]["json"]
        am = json.loads(sp.read_text())
        shutil.copy2(P / "sprite" / "old_temple_actors.png", sp.parent / "old_temple.png")
        (sp.parent / "old_temple.json").write_text(json.dumps(am_ot, indent=1))
        am.setdefault("sheets", {})["old_temple"] = {"json": "old_temple.json", "image": "old_temple.png"}
        for r in OLD_TEMPLE_ROLES:
            am["roles"][r] = {"sheet": "old_temple", "row": am_ot["roles"][r]["row"], "kind": "human", "anims": ["idle", "walk"]}
        sp.write_text(json.dumps(am, indent=1))
        jp = root / scene["gamefx"]["json"]; ip = root / scene["gamefx"]["image"]
        m = _append_atlas(ip, json.loads(jp.read_text()), P / "gamefx" / "old_temple_fx.png", fxm, "effects", mark="old_temple_from")
        for v in m["effects"].values():
            v.pop("strip", None)
        jp.write_text(json.dumps(m, indent=1))
        n += 1
    print(f"old temple: sheet ({len(OLD_TEMPLE_ROLES)} roles) + {len(fxm['effects'])} gamefx in {n} areas")


# ------------------------------------------------------------------ icons (biome palette only, 16 px, hard alpha)
def draw_icons():
    C = {k: tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) + (255,) for k, v in load_biome("cozy-village")["colors"].items()}
    W = 16
    sheet = Image.new("RGBA", (W * 5, W), (0, 0, 0, 0))
    px = sheet.load()

    def put(i, x, y, c):
        if 0 <= x < W and 0 <= y < W:
            px[i * W + x, y] = C[c]

    def outline(i):
        pts = []
        for y in range(W):
            for x in range(W):
                if px[i * W + x, y][3] == 0 and any(0 <= x + dx < W and 0 <= y + dy < W and px[i * W + x + dx, y + dy][3] and px[i * W + x + dx, y + dy] != C["ink"]
                                                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    pts.append((x, y))
        for x, y in pts:
            put(i, x, y, "ink")

    # 0 loaf: a round hearthloaf with two score marks
    for y in range(4, 13):
        for x in range(2, 14):
            if ((x - 7.5) / 6.0) ** 2 + ((y - 9) / 4.6) ** 2 <= 1:
                put(0, x, y, "plaster" if y < 6 else "timber_hi" if y < 11 else "timber")
    for (x, y) in ((4, 7), (11, 7), (3, 9), (12, 9)):
        put(0, x, y, "timber")
    for (x, y) in ((5, 6), (6, 7), (9, 6), (10, 7)):
        put(0, x, y, "plaster")
    put(0, 6, 5, "plaster_hi")
    outline(0)
    # 1 moonpetal
    for y in range(8, 15):
        put(1, 8, y, "moss")
    put(1, 6, 11, "grass_hi"); put(1, 7, 12, "grass_hi"); put(1, 9, 12, "moss"); put(1, 10, 11, "moss")
    for (x, y) in ((5, 4), (6, 3), (6, 4), (10, 3), (10, 4), (11, 4), (7, 6), (9, 6), (8, 1), (8, 2), (5, 5), (11, 5)):
        put(1, x, y, "flower_blue")
    for (x, y) in ((6, 5), (10, 5), (8, 3), (7, 4), (9, 4), (7, 5), (9, 5)):
        put(1, x, y, "white")
    put(1, 8, 4, "flower_gold"); put(1, 8, 5, "flower_gold")
    outline(1)
    # 2 copper bits: one round copper with a square hole
    for y in range(W):
        for x in range(W):
            d = ((x - 7.5) ** 2 + (y - 7.5) ** 2) ** 0.5
            if d <= 6.2:
                put(2, x, y, "roof" if d > 5.0 else "roof_hi")
    for (x, y) in ((4, 5), (5, 4), (4, 6), (6, 3), (3, 7)):
        put(2, x, y, "flower_gold")
    for y in (6, 7, 8, 9):
        for x in (6, 7, 8, 9):
            put(2, x, y, "roof")
    for y in (7, 8):
        for x in (7, 8):
            px[2 * W + x, y] = (0, 0, 0, 0)
    outline(2)
    # 3 acorn
    for y in range(7, 14):
        for x in range(4, 12):
            if ((x - 7.5) / 3.6) ** 2 + ((y - 9.5) / 4.0) ** 2 <= 1:
                put(3, x, y, "timber_hi" if x < 8 else "timber")
    for x in range(3, 13):
        for y in (5, 6, 7):
            if abs(x - 7.5) <= 4.5 - (7 - y) * 0.6:
                put(3, x, y, "timber_lo" if (x + y) % 2 else "timber")
    put(3, 8, 3, "timber_lo"); put(3, 8, 4, "timber_lo"); put(3, 6, 9, "plaster")
    outline(3)
    # 4 tea tin
    for y in range(4, 14):
        for x in range(4, 12):
            put(4, x, y, "grass" if x > 5 else "grass_hi")
    for x in range(4, 12):
        put(4, x, 8, "flower_gold"); put(4, x, 9, "flower_gold"); put(4, x, 3, "stone_hi"); put(4, x, 13, "moss")
    put(4, 7, 8, "flower_blue"); put(4, 8, 8, "white"); put(4, 8, 9, "flower_blue")
    outline(4)
    (GAME / "art").mkdir(exist_ok=True)
    sheet.save(GAME / "art" / "items.png")
    sheet.resize((sheet.width * 6, sheet.height * 6), Image.NEAREST).save(GAME / "art" / "items_6x.png")

    # app icon: the moss gate (stone arch + this game's vortex frame) on a wood plate, nearest-scaled
    g = json.loads((GAME / "areas/plaza/public/art/gamefx/gamefx.json").read_text())
    atlas = Image.open(GAME / "areas/plaza/public/art/gamefx/gamefx.png").convert("RGBA")
    row = g["effects"]["portal_vortex"]["row"]
    vort = atlas.crop((0, row * 48, 48, row * 48 + 48))
    ic = Image.new("RGBA", (64, 64), C["timber"])
    ip = ic.load()
    for y in range(64):
        for x in range(64):
            if x in (0, 63) or y in (0, 63):
                ip[x, y] = C["ink"]
            elif x in (2, 61) or y in (2, 61):
                ip[x, y] = C["timber_hi"]
    # arch stones
    import math
    for y in range(64):
        for x in range(64):
            dx, dy = x - 31.5, y - 30
            r = (dx * dx + dy * dy) ** 0.5
            if (y <= 30 and 17 <= r <= 23) or (y > 30 and 17 <= abs(dx) <= 23 and y < 58):
                ip[x, y] = C["stone_hi"] if ((int(math.atan2(dy, dx) * 5) + y // 7) % 2) else C["stone"]
                if y < 26 and r > 21.5:
                    ip[x, y] = C["moss"]
    for x in range(6, 58):
        for y in (57, 58, 59):
            ip[x, y] = C["stone_lo"]
    ic.alpha_composite(vort, (8, 12))
    (GAME / "icons").mkdir(exist_ok=True)
    for s in (192, 512):
        ic.resize((s, s), Image.NEAREST).save(GAME / "icons" / f"icon-{s}.png")
    # maskable: same art with a safe margin
    m = Image.new("RGBA", (80, 80), C["timber_lo"]); m.alpha_composite(ic, (8, 8))
    m.resize((512, 512), Image.NEAREST).save(GAME / "icons" / "icon-maskable-512.png")


# ------------------------------------------------------------------ touch-button icons (16 px, palette only, ink outline)
# letters -> palette colours; '.' = clear. Drawn as ASCII so they stay easy to tweak. Outline is added after.
BTN_KEY = {"w": "white", "s": "stone_hi", "S": "stone", "k": "stone_lo", "t": "timber", "T": "timber_hi", "d": "timber_lo",
           "g": "flower_gold", "l": "lamp", "r": "flower_rose", "b": "flower_blue", "y": "sky", "G": "grass_hi", "m": "moss",
           "p": "plaster_hi", "P": "plaster", "o": "roof_hi", "R": "roof"}
BTN_ICONS = {
    "attack": [
        "............ws..", "...........wss..", "..........wss...", ".........wss....", "........wss.....", ".......wss......",
        "......wss.......", "..g..wss........", "..ggwss.........", "...ggs..........", "...tgg..........", "..tt.gg.........",
        ".tt.............", "dt..............", "d...............", "................"],
    "guard": [
        "................", "....kkkkkkkk....", "...ksssssssSk...", "..ksTTTTTTTTSk..", "..ksTTTggTTTSk..", "..ksTTgllgTTSk..",
        "..ksTTTggTTTSk..", "..ksTTTggTTTSk..", "..ksTTTggTTTSk..", "...ksTTggTTSk...", "...ksTTTTTTSk...", "....ksTTTTSk....",
        ".....ksTTSk.....", "......kSSk......", ".......kk.......", "................"],
    "jump": [
        "................", ".......pp.......", "......pppp......", ".....pppppp.....", "....pppppppp....", "...pppPppPppp...",
        "......pPPp......", "......pPPp......", "......pPPp......", "......pPPp......", "................", "....yy....yy....",
        "...y..y..y..y...", "................", "..GGGGGGGGGGGG..", "..mmmmmmmmmmmm.."],
    "dodge": [
        "................", ".....yyyyy......", "...yy.....yy....", "..y.........y...", ".y...........y..", ".y.....p.....y..",
        "y.....ppp....y..", "y....ppppp...y..", "y......p.....y..", ".y...........y..", ".y.........yyyy.", "..y.........yyy.",
        "...yy.....y.yy..", ".....yyyyy...y..", "................", "................"],
    "spell": [
        "................", ".......l........", ".......l........", "......lwl.......", "......lwl.......", ".....lwwwl...g..",
        "..llllwwwllll...", "...lwwwwwwwl....", "..llllwwwllll...", ".....lwwwl......", "......lwl.......", "..g...lwl.......",
        ".......l.....g..", ".......l........", "................", "................"],
    "summon": [
        "................", "..g.........w...", ".......GG.......", "......GmmG......", ".....GmGGmG.....", "......GmmG...g..",
        ".......GG.......", ".......mm.......", "...r...mm...r...", "..rwr..mm..rwr..", "...r..mmmm..r...", "......mddm......",
        ".....ttttttt....", ".....tTTTTTt....", "......ttttt.....", "................"],
    "log": [
        "................", "...dttttttttd...", "..dTppppppppTd..", "...dpppppppd....", "...pPPPPPPPp....", "...pppppppp.....",
        "...pPPPPPPp.....", "...pppppppp.....", "...pPPPPPp......", "...pppppppp.....", "...pPPPPPPPp....", "...pppppppp.....",
        "..dTppppppppTd..", "...dttttttttd...", "................", "................"],
    "talk": [
        "................", "................", "...pppppppppp...", "..pppppppppppp..", "..pppppppppppp..", "..ppdpppdpppdp..",
        "..pppppppppppp..", "..pppppppppppp..", "...pppppppppp...", ".....ppp........", "....pp..........", "...p............",
        "................", "................", "................", "................"],
}


def draw_button_icons():
    C = {k: tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) + (255,) for k, v in load_biome("cozy-village")["colors"].items()}
    names = list(BTN_ICONS)
    W = 16
    sheet = Image.new("RGBA", (W * len(names), W), (0, 0, 0, 0))
    px = sheet.load()
    for n, name in enumerate(names):
        rows = BTN_ICONS[name]
        assert len(rows) == 16 and all(len(r) == 16 for r in rows), name
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch != ".":
                    px[n * W + x, y] = C[BTN_KEY[ch]]
        pts = []
        for y in range(W):
            for x in range(W):
                if px[n * W + x, y][3] == 0 and any(0 <= x + dx < W and 0 <= y + dy < W and px[n * W + x + dx, y + dy][3]
                                                    and px[n * W + x + dx, y + dy] != C["ink"] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    pts.append((x, y))
        for x, y in pts:
            px[n * W + x, y] = C["ink"]
    (GAME / "art").mkdir(exist_ok=True)
    sheet.save(GAME / "art" / "buttons.png")
    sheet.resize((sheet.width * 6, sheet.height * 6), Image.NEAREST).save(GAME / "art" / "buttons_6x.png")
    return names


def write_pwa():
    man = {"name": "Hearthmoor", "short_name": "Hearthmoor", "description": "A small cozy HD-2D village errand game.",
           "start_url": "./index.html", "scope": "./", "display": "fullscreen", "orientation": "any",
           "background_color": "#1b1716", "theme_color": "#4a2e20",
           "icons": [{"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
                     {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
                     {"src": "icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}
    (GAME / "manifest.webmanifest").write_text(json.dumps(man, indent=1))
    files = sorted(str(p.relative_to(GAME)) for d in ("engine", "vendor", "areas", "game", "art", "icons", "audio") for p in (GAME / d).rglob("*")
                   if p.is_file() and "src" not in p.relative_to(GAME).parts[:2] and p.suffix != ".py")
    files = ["./", "index.html", "manifest.webmanifest"] + files
    h = hashlib.sha1()
    for f in files[1:]:
        h.update((GAME / f).read_bytes() if (GAME / f).is_file() else f.encode())
    ver = h.hexdigest()[:10]
    (GAME / "sw.js").write_text(f"""// Hearthmoor service worker: precache the whole game (offline play), cache-first, versioned.
const CACHE = 'hearthmoor-v1-{ver}';
const FILES = {json.dumps(files)};
self.addEventListener('install', (e) => {{ e.waitUntil(caches.open(CACHE).then((c) => c.addAll(FILES)).then(() => self.skipWaiting())); }});
self.addEventListener('activate', (e) => {{ e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k.startsWith('hearthmoor-') && k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim())); }});
self.addEventListener('fetch', (e) => {{
  if (e.request.method !== 'GET') return;
  e.respondWith(caches.match(e.request, {{ ignoreSearch: true }}).then((r) => r || fetch(e.request)));
}});
""")
    print(f"pwa: {len(files)} files precached, cache hearthmoor-v1-{ver}")


VERDANT_AREAS = ["rotwood", "verdant"]
VERDANT_SHEETS = {"verdant_actors": ["rottreant", "sporeelemental"], "boss_blight_regent": ["blightregent"],
                  "boss_thornmother": ["thornmother"], "boss_hjortur": ["hjortur", "hjortur_corrupted"]}


def _critters48(P, root):
    cm = json.loads((P / "gamefx" / "verdant_critters.json").read_text())
    src = Image.open(P / "gamefx" / "verdant_critters.png").convert("RGBA")
    c = cm["cell"]; nrows = len(cm["effects"]); ncol = max(v["frames"] for v in cm["effects"].values())
    out = Image.new("RGBA", (ncol * 48, nrows * 48), (0, 0, 0, 0))
    for i, (k, v) in enumerate(sorted(cm["effects"].items(), key=lambda kv: kv[1]["row"])):
        fl = []
        for j, f in enumerate(v["frame_list"]):
            out.paste(src.crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"])), (j * 48 + 24 - c // 2, i * 48 + 48 - c))
            fl.append({"x": j * 48, "y": i * 48, "w": 48, "h": 48})
        v.update(row=i, frame_list=fl, pivot=[24, 47])
    tmp = root / "_critters48.png"; out.save(tmp)
    return tmp, {**cm, "cell": 48, "size": [out.size[0], out.size[1]]}


def install_verdant_heart(areas=AREAS):
    """Stage 6.4: the Verdant Heart art pack (art/verdant_heart/, Art bot 2026-10-06) for the Rotwood Hollow and the
    Verdant Heart: rot treant / spore elemental + the three big foes (Regent 5.5x, Thornmother 2.4x, Hjortur 6x) ride
    in their own sheets (drop-in boss_sheet output); verdant_fx + the glow-frog critters join the area's gamefx atlas.
    The kit pieces build through tools/kit/kit_verdant_heart.py."""
    P = GAME / "art" / "verdant_heart"
    n = 0
    for a in areas:
        if a not in VERDANT_AREAS:
            continue
        root = GAME / "areas" / a
        scene = json.loads((root / "scene.json").read_text())
        sp = root / scene["atlas"]["json"]
        am = json.loads(sp.read_text())
        for sheet, roles in VERDANT_SHEETS.items():
            sj = json.loads((P / "sprite" / f"{sheet}.json").read_text())
            shutil.copy2(P / "sprite" / f"{sheet}.png", sp.parent / f"{sheet}.png")
            (sp.parent / f"{sheet}.json").write_text(json.dumps(sj, indent=1))
            am.setdefault("sheets", {})[sheet] = {"json": f"{sheet}.json", "image": f"{sheet}.png"}
            for r in roles:
                rd = sj["roles"][r]
                am["roles"][r] = {"sheet": sheet, "row": rd["row"], "kind": "enemy", "enemy": True, "anims": rd.get("anims", ["idle", "walk", "attack", "die"]),
                                  **({"boss": True, "scale": rd["scale"], "frame": sj["frame"]} if rd.get("boss") else {})}
        sp.write_text(json.dumps(am, indent=1))
        jp = root / scene["gamefx"]["json"]; ip = root / scene["gamefx"]["image"]
        m = json.loads(jp.read_text())
        vfx = json.loads((P / "gamefx" / "verdant_fx.json").read_text())
        # spore_motes stays out: its motes are too sparse for check-scene's gamefx_sharp to measure (unverified = fail);
        # nothing places it yet (the Regent's spore fog uses glow_mist_violet). Same call as old_temple's faceless_gaze.
        vfx = {**vfx, "effects": {k: v for k, v in vfx["effects"].items() if k != "spore_motes"}}
        m = _append_atlas(ip, m, P / "gamefx" / "verdant_fx.png", vfx, "effects", mark="verdant_fx_from")
        cp, cm = _critters48(P, root)   # the glow frogs come in 24 px cells: re-seat them in 48 px cells (same pixels, frog at the bottom centre)
        m = _append_atlas(ip, m, cp, cm, "effects", mark="verdant_critters_from")
        for v in m["effects"].values():
            v.pop("strip", None)
        jp.write_text(json.dumps(m, indent=1)); (root / "_critters48.png").unlink()
        n += 1
    print(f"verdant heart: {len(VERDANT_SHEETS)} sheets + verdant fx / critters in {n} areas")


# [VANAHEIM] Stage B: Mossbrook + the Thorngarden, Hearthmoor Art batch 2026-10-28 (staging art/vanaheim/README.md).
# sync_vanaheim_art() copies the staging pack into games/hearthmoor/art/vanaheim/ (sprite, kit, icons, gamefx; never src/), so
# a polished Nettlecrown sheet at the same path drops in by re-running the build. boss_nettlecrown_neon.png is her APPROVED, locked main look,
# boss_nettlecrown.png the fallback. Palette: vanaheim-gloom area palette (art/palette/vanaheim-gloom, check_sprite.area_palette).
VH_STAGEB_AREAS = ["vh_village", "vh_garden"]
VH_STAGEB_SHEETS = {"boss_nettlecrown": ["nettlecrown"], "thornnymph": ["thornnymph"], "thornhex": ["thornhex"], "oldmorel": ["oldmorel"]}
VH_STAGING = Path("/workspace/hearthmoor-staging/art/vanaheim")
VH_KIT = {   # static props (decor; the collision grid is unchanged)
    "vh_village": [("hex_knot", p) for p in ((-6.0, -3.0), (2.4, 2.6), (8.2, -3.6))],
    "vh_garden": [("frost_thorn_root_open", p) for p in ((-6.4, -2.6), (-1.0, 2.4), (3.0, -4.2))]
                 + [("thorn_wall_s1", (-4.0, -7.4)), ("thorn_wall_s2", (-1.6, -7.8)), ("thorn_wall_s3", (8.6, -6.8)), ("thorn_wall_s2", (10.4, -5.2))],
}


def sync_vanaheim_art():
    S, D = VH_STAGING, GAME / "art" / "vanaheim"
    if not S.exists():
        return
    for sub in ("sprite", "kit", "icons", "gamefx", "gamefx/strips"):
        if not (S / sub).exists():
            continue
        (D / sub).mkdir(parents=True, exist_ok=True)
        for f in (S / sub).iterdir():
            if f.is_file() and f.suffix in (".png", ".json", ".glb") and "contact_sheet" not in f.name and not re.search(r"_(v\d+|polish\d*|backup\w*)\.", f.name):   # skip Art's backups
                shutil.copy2(f, D / sub / f.name)
    for f in ("README.md", "READY.txt"):
        if (S / f).exists():
            shutil.copy2(S / f, D / f)


def install_vanaheim_stageb(areas=AREAS):
    sync_vanaheim_art()
    P = GAME / "art" / "vanaheim"
    if not (P / "sprite").exists():
        print("vanaheim stage B: no art pack -> placeholders (hedgewitch / sporeling)"); return
    if not (P / "READY.txt").exists():
        print("vanaheim stage B: READY.txt missing (pack still in progress)")
    n, used = 0, set()
    for a in areas:
        if a not in VH_STAGEB_AREAS:
            continue
        root = GAME / "areas" / a
        scene = json.loads((root / "scene.json").read_text())
        sp = root / scene["atlas"]["json"]
        am = json.loads(sp.read_text())
        for sheet, roles in VH_STAGEB_SHEETS.items():
            if not (P / "sprite" / f"{sheet}.json").exists():
                continue
            sj = json.loads((P / "sprite" / f"{sheet}.json").read_text())
            src = P / "sprite" / f"{sheet}_neon.png"
            if not src.exists():
                src = P / "sprite" / f"{sheet}.png"
            shutil.copy2(src, sp.parent / f"{sheet}.png")
            (sp.parent / f"{sheet}.json").write_text(json.dumps(sj, indent=1))
            am.setdefault("sheets", {})[sheet] = {"json": f"{sheet}.json", "image": f"{sheet}.png"}
            used.add(sheet)
            for r in roles:
                rd = sj["roles"][r]
                npc = r == "oldmorel"
                am["roles"][r] = {"sheet": sheet, "row": rd["row"], "kind": "human" if npc else "enemy", "enemy": not npc, "frame": sj["frame"],
                                  "anims": rd.get("anims", ["idle", "walk"] if npc else ["idle", "walk", "attack", "die"]), **({"boss": True, "scale": rd["scale"]} if rd.get("boss") else {})}
        sp.write_text(json.dumps(am, indent=1))
        # area palette file (check-sprite --project areas/<a> --biome vanaheim-gloom works too)
        pd = root / "public/art/palette/vanaheim-gloom"; pd.mkdir(parents=True, exist_ok=True)
        shutil.copy2(GAME / "art/palette/vanaheim-gloom/biome.json", pd / "biome.json")
        # kit props
        kd = root / "public/art/kit"
        objs = [o for o in scene.get("objects", []) if not o.get("vh_kit")]
        for piece, (x, z) in VH_KIT.get(a, []):
            if (P / "kit" / f"{piece}.glb").exists():
                shutil.copy2(P / "kit" / f"{piece}.glb", kd / f"{piece}.glb")
                objs.append({"glb": f"public/art/kit/{piece}.glb", "pos": [x, 0, z], "vh_kit": True})
        scene["objects"] = objs
        if "oldmorel" in am["roles"]:   # Old Morel (mushroom-folk grocer) is the cap-seller's look
            for ac in scene.get("actors", []):
                if ac.get("id") == "capseller":
                    ac["role"] = "oldmorel"
        (root / "scene.json").write_text(json.dumps(scene, indent=1))
        # game fx (frost sparkle, bud pulse, firefly drift, thorn-wall tell)
        if (P / "gamefx/vh_fx.json").exists():
            jp = root / scene["gamefx"]["json"]; ip = root / scene["gamefx"]["image"]
            m = json.loads(jp.read_text())
            m = _append_atlas(ip, m, P / "gamefx/vh_fx.png", json.loads((P / "gamefx/vh_fx.json").read_text()), "effects", mark="vh_fx_from")   # crops at the mark: re-runs replace, never stack
            for v in m["effects"].values():
                v.pop("strip", None)
            jp.write_text(json.dumps(m, indent=1))
        n += 1
    print(f"vanaheim stage B: sheets {sorted(used)}, kit + vh_fx + gloom palette in {n} areas")


ZIP_SKIP = ("areas/src", "tests/shots", "shots", "__pycache__")


def make_zip():
    z = GAME.parent / "hearthmoor.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(GAME.rglob("*")):
            rel = p.relative_to(GAME)
            if p.is_dir() or any(str(rel).startswith(s) or s in rel.parts for s in ZIP_SKIP):
                continue
            zf.write(p, Path("hearthmoor") / rel)
        for p in sorted((GAME / "areas" / "src").glob("*.json")):
            zf.write(p, Path("hearthmoor") / p.relative_to(GAME))
    print(f"zip: {z} ({z.stat().st_size / 1e6:.1f} MB)")
    return z


FORGE_AREAS = ["forge"]
FORGE_ROLES = ["smith", "dwarfsmith"]


def install_forge(areas=AREAS):
    """6.7 Forge pack (art/forge/, Art seat 2026-10-05): Tova (smith) + Orri (dwarfsmith) in their own sheet like the
    temple pair; forge_fx (fire, sparks, quench steam, embers, red / blue pools) appended to the area's gamefx atlas."""
    P = GAME / "art" / "forge"
    am_f = json.loads((P / "forge_actors.json").read_text())
    fxm = json.loads((P / "forge_fx.json").read_text())
    # quench_steam / embers_drift / anvil_glow stay out: too sparse for check-scene's gamefx_sharp (like faceless_gaze);
    # the forge uses the particle 'embers' emitter and forge_sparks instead
    skip = {"quench_steam", "embers_drift", "anvil_glow"}
    fxm = {**fxm, "effects": {k: v for k, v in fxm["effects"].items() if k not in skip}}
    for a in [x for x in areas if x in FORGE_AREAS]:
        root = GAME / "areas" / a
        scene = json.loads((root / "scene.json").read_text())
        sp = root / scene["atlas"]["json"]
        am = json.loads(sp.read_text())
        shutil.copy2(P / "forge_actors.png", sp.parent / "forge.png")
        (sp.parent / "forge.json").write_text(json.dumps(am_f, indent=1))
        am.setdefault("sheets", {})["forge"] = {"json": "forge.json", "image": "forge.png"}
        for r in FORGE_ROLES:
            am["roles"][r] = {"sheet": "forge", "row": am_f["roles"][r]["row"], "kind": "human", "anims": ["idle", "walk"]}
        sp.write_text(json.dumps(am, indent=1))
        jp = root / scene["gamefx"]["json"]; ip = root / scene["gamefx"]["image"]
        m = _append_atlas(ip, json.loads(jp.read_text()), P / "forge_fx.png", fxm, "effects", mark="forge_from")
        for v in m["effects"].values():
            v.pop("strip", None)
        jp.write_text(json.dumps(m, indent=1))
        al = GAME / "art" / "alchemy"; alm = json.loads((al / "alchemy_fx.json").read_text())
        keep = {"cauldron_brew_blue", "cauldron_fire", "cauldron_pool_blue", "brew_puff_blue"}   # 6.8 the Still: Old Gurgle's blue brew
        alm = {**alm, "effects": {k: v for k, v in alm["effects"].items() if k in keep}}
        m = _append_atlas(ip, json.loads(jp.read_text()), al / "alchemy_fx.png", alm, "effects", mark="alchemy_from")
        for v in m["effects"].values():
            v.pop("strip", None)
        jp.write_text(json.dumps(m, indent=1))
    print(f"forge: sheet ({len(FORGE_ROLES)} roles) + {len(fxm['effects'])} gamefx in {', '.join(x for x in areas if x in FORGE_AREAS)}")


CAULDRON_AREAS = ["forge"]


def install_cauldron(areas=AREAS):
    """6.8 The Cold Cauldron: Bloop, Bryony's glowing frog (art/cold_cauldron/, Art seat 2026-10-16). His own 240x128 sheet (bloop_neon.png is
    the primary look, scoped check-sprite allow-list entry for role pet_bloop; bloop.png is the palette-safe twin) added as sheet 'bloop' / role
    'pet_bloop' to the forge's actors.json. Additive and idempotent (it only adds the sheet and the role), so it also runs on a built forge
    without a rebuild: python3 -c "import build; build.install_cauldron()"."""
    P = GAME / "art" / "cold_cauldron"
    bm = json.loads((P / "bloop.json").read_text())
    for a in [x for x in areas if x in CAULDRON_AREAS]:
        root = GAME / "areas" / a
        scene = json.loads((root / "scene.json").read_text())
        sp = root / scene["atlas"]["json"]
        am = json.loads(sp.read_text())
        shutil.copy2(P / bm["primary"], sp.parent / "bloop.png")
        out = {k: bm[k] for k in ("tool", "biome", "frame", "pivot", "ground_row", "facings", "anims", "cols", "size")}
        out["image"] = "bloop.png"
        out["roles"] = {"pet_bloop": {k: v for k, v in bm["roles"]["pet_bloop"].items() if k != "frames"}}
        (sp.parent / "bloop.json").write_text(json.dumps(out, indent=1))
        am.setdefault("sheets", {})["bloop"] = {"json": "bloop.json", "image": "bloop.png"}
        r = bm["roles"]["pet_bloop"]
        am["roles"]["pet_bloop"] = {"sheet": "bloop", "row": r["row"], "kind": r.get("kind", "creature"), "anims": ["idle", "walk"], "desc": r.get("desc", "")}
        sp.write_text(json.dumps(am, indent=1))
    print(f"cauldron: Bloop sheet in {', '.join(x for x in areas if x in CAULDRON_AREAS)}")


ORB_AREAS = ["plaza", "lane"]


def install_orb_lanterns(areas=AREAS):
    """6.6 orb lanterns (art/orb_lanterns/, Art seat 2026-10-05): the 32 px orb billboards (orb_large_blue / violet / red,
    orb_grand_mix) appended under the spells atlas of the areas with lantern spots (cell 32 matches). Runs after
    install_pets (which crops at pets_from); a re-run crops at orbs_from first."""
    P = GAME / "art" / "orb_lanterns"
    fxm = json.loads((P / "orb_fx_32.json").read_text())
    for a in [x for x in areas if x in ORB_AREAS]:
        root = GAME / "areas" / a
        scene = json.loads((root / "scene.json").read_text())
        jp = root / scene["spells"]["json"]; ip = root / scene["spells"]["image"]
        m = _append_atlas(ip, json.loads(jp.read_text()), P / "orb_fx_32.png", fxm, "effects", None, mark="orbs_from")
        jp.write_text(json.dumps(m, indent=1))
    print(f"orb lanterns: {len(fxm['effects'])} orb effects in {', '.join(x for x in areas if x in ORB_AREAS)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--skip-assemble", action="store_true")
    ap.add_argument("--areas", default=None, help="comma list: rebuild only these areas (the others stay as built)")
    a = ap.parse_args()
    only = a.areas.split(",") if a.areas else AREAS
    if not a.skip_assemble:
        assemble(only)
    copy_areas(only)
    install_pets(only)
    install_old_temple(only)
    install_verdant_heart(only)
    install_vanaheim_stageb(only)
    install_orb_lanterns(only)
    install_forge(only)
    install_cauldron(only)
    draw_icons()
    draw_button_icons()
    write_pwa()
    if not a.no_zip:
        make_zip()
