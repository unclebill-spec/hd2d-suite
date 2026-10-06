"""Build Hearthmoor: assemble the three area specs with the hd2d tools, copy the runtime once, prune each area to
the files its scene.json uses, draw the HUD item icons + app icons, write the service-worker file list, zip.

    python3 games/hearthmoor/build.py [--no-zip]
"""
import argparse
import hashlib
import json
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

AREAS = ["plaza", "lane", "mossglen", "hollows", "rift", "vanaheim", "ravenhold", "bifrost",
         "alfheim", "lumen_court", "wispwood", "prismvault"]   # [ALFHEIM] Lumenvale (Glimmer Steps, Lumen Court, Wispwood) + the Prism Vault
TMP = Path("/tmp/hearthmoor_build")


def sh(*a):
    subprocess.run([str(x) for x in a], check=True)


def assemble():
    for a in AREAS:
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


def copy_areas():
    for d in ("engine", "vendor"):
        if (GAME / d).exists():
            shutil.rmtree(GAME / d)
        # always the suite's current runtime (not the assemble output, which is stale with --skip-assemble)
        shutil.copytree(SUITE / "tools/runtime/web" / d, GAME / d, ignore=shutil.ignore_patterns("__pycache__"))
    for a in AREAS:
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
    files = sorted(str(p.relative_to(GAME)) for d in ("engine", "vendor", "areas", "game", "art", "icons") for p in (GAME / d).rglob("*")
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


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--skip-assemble", action="store_true")
    a = ap.parse_args()
    if not a.skip_assemble:
        assemble()
    copy_areas()
    draw_icons()
    draw_button_icons()
    write_pwa()
    if not a.no_zip:
        make_zip()
