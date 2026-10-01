"""hd2d check-sprite: PIL checker for hd2d sprite atlases.

    hd2d check-sprite PROJECT/public/art/sprite/actors.png [--json actors.json] [--biome cozy-village] [--report out.json]

Checks, per role and per frame:
  alpha      every pixel alpha is 0 or 255 (no semi-transparent pixels)
  palette    every opaque colour is in the biome palette; colour count per role <= --max-colors
  outline    every silhouette edge pixel (opaque next to transparent) is the outline ink colour
  frames     4 facings x (idle 4 + walk 4) present and non-empty; facings actually differ;
             magic users (caster) also need 4 cast frames per facing that differ from idle
  size       opaque bounds inside the role's size bounds (humans about 16-24 w: 14-24 allowed for profiles/kids, 24-40 h)
  feet       lowest opaque row == ground_row in every frame; feet centre within 2 px of the pivot x
Exit code 0 = pass, 1 = fail. Prints a report; --report writes JSON.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from PIL import Image  # noqa: E402

from hd2d_common import load_biome, write_json  # noqa: E402


def _hex(px):
    return "#%02x%02x%02x" % px[:3]


def check(atlas_path, json_path=None, biome=None, max_colors=20, project=None):
    atlas_path = Path(atlas_path)
    json_path = Path(json_path) if json_path else atlas_path.with_suffix(".json")
    meta = json.loads(json_path.read_text())
    biome = biome or meta.get("biome", "cozy-village")
    palette = set(load_biome(biome, project)["colors"].values())
    ink = load_biome(biome, project)["colors"]["ink"]
    im = Image.open(atlas_path).convert("RGBA")
    W, H = im.size
    px = im.load()
    fw, fh = meta["frame"]
    pivx = meta["pivot"][0]
    ground = meta.get("ground_row", fh - 1)
    failures, warnings = [], []
    report = {"atlas": str(atlas_path), "biome": biome, "roles": {}, "summary": {}}

    # global alpha check
    semi = sum(1 for y in range(H) for x in range(W) if 0 < px[x, y][3] < 255)
    if semi:
        failures.append(f"{semi} semi-transparent pixels in atlas")
    for role, info in meta["roles"].items():
        rr = {"frames": 0, "colors": 0, "issues": []}
        colors = set()
        (wmin, wmax), (hmin, hmax) = info["size_bounds"]
        facing_sigs = {}
        bad_outline = 0
        for fr in info["frames"]:
            x0, y0 = fr["x"], fr["y"]
            opaque = []
            for y in range(fh):
                for x in range(fw):
                    p = px[x0 + x, y0 + y]
                    if p[3] == 255:
                        opaque.append((x, y))
                        c = _hex(p)
                        colors.add(c)
                        if c not in palette:
                            rr["issues"].append(f"{fr['name']}: colour {c} not in {biome}")
            if not opaque:
                rr["issues"].append(f"{fr['name']}: empty frame")
                continue
            rr["frames"] += 1
            oset = set(opaque)
            xs = [p[0] for p in opaque]
            ys = [p[1] for p in opaque]
            bw, bh = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
            if not (wmin <= bw <= wmax) or not (hmin <= bh <= hmax):
                rr["issues"].append(f"{fr['name']}: bounds {bw}x{bh} outside {wmin}-{wmax} x {hmin}-{hmax}")
            # silhouette must be ink-outlined
            for (x, y) in opaque:
                edge = any((x + dx, y + dy) not in oset for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                if edge and _hex(px[x0 + x, y0 + y]) != ink:
                    bad_outline += 1
            # feet anchor
            if max(ys) != ground:
                rr["issues"].append(f"{fr['name']}: lowest opaque row {max(ys)} != ground row {ground}")
            feet = [x for (x, y) in opaque if y >= ground - 2]
            fc = (min(feet) + max(feet) + 1) / 2
            if abs(fc - pivx) > (2 if info["kind"] == "human" else 4):
                rr["issues"].append(f"{fr['name']}: feet centre {fc:.1f} vs pivot {pivx}")
            if fr["anim"] == "idle" and fr["i"] == 0:
                facing_sigs[fr["facing"]] = tuple(sorted(oset)) + tuple(px[x0 + x, y0 + y] for x, y in sorted(oset))
        if bad_outline:
            rr["issues"].append(f"{bad_outline} silhouette pixels are not the {ink} outline")
        rr["colors"] = len(colors)
        if len(colors) > max_colors:
            rr["issues"].append(f"{len(colors)} colours > {max_colors}")
        want = 48 if info.get("caster") else 32
        if rr["frames"] != want:
            rr["issues"].append(f"{rr['frames']} frames, expected {want} (4 facings x idle4+walk4"
                                + (" + cast4)" if want == 48 else ")"))
        if info.get("caster"):
            # the cast pose must actually differ from idle in every facing
            sig = {}
            for fr in info["frames"]:
                if fr["anim"] in ("idle", "cast") and fr["i"] == 1:
                    sig[(fr["facing"], fr["anim"])] = tuple(px[fr["x"] + x, fr["y"] + y] for y in range(fh) for x in range(fw))
            for f in ("down", "up", "left", "right"):
                if sig.get((f, "idle")) == sig.get((f, "cast")):
                    rr["issues"].append(f"{role} {f}: cast frame identical to idle")
        if len(set(facing_sigs.values())) < 3:
            rr["issues"].append("facings are not distinct")
        if facing_sigs.get("left") and facing_sigs.get("right") and facing_sigs["left"] == facing_sigs["right"]:
            rr["issues"].append("left == right (not mirrored)")
        report["roles"][role] = rr
        for i in rr["issues"]:
            failures.append(f"{role}: {i}")
    report["summary"] = {"roles": len(meta["roles"]), "failures": len(failures), "semi_transparent": semi,
                         "pass": not failures}
    report["failures"] = failures[:200]
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(prog="hd2d check-sprite", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("atlas")
    ap.add_argument("--json", default=None)
    ap.add_argument("--biome", default=None)
    ap.add_argument("--project", default=None)
    ap.add_argument("--max-colors", type=int, default=20)
    ap.add_argument("--report", default=None)
    a = ap.parse_args(argv)
    r = check(a.atlas, a.json, a.biome, a.max_colors, a.project)
    for role, rr in r["roles"].items():
        status = "ok  " if not rr["issues"] else "FAIL"
        print(f"  {status} {role:11s} frames={rr['frames']:2d} colours={rr['colors']:2d}" +
              ("" if not rr["issues"] else f"  ({len(rr['issues'])} issues: {rr['issues'][0]})"))
    print(f"check-sprite: {'PASS' if r['summary']['pass'] else 'FAIL'} ({r['summary']['failures']} failures, "
          f"{r['summary']['semi_transparent']} semi-transparent px)")
    if a.report:
        write_json(a.report, r)
    return 0 if r["summary"]["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
