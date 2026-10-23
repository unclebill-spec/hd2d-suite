"""Extra art checks for hd2d check-sprite (added 2026-10-23, checks-upgrade).

  holes       enclosed transparent pockets inside the opaque shape (not reachable from the frame border), size >= HOLE_MIN px
  limbs       a frame's opaque area or bbox area < (1 - LIMB_DROP) x the role's median frame, or the frame splits into more
              opaque blobs (>= BLOB_MIN px, 8-connected) than the role's usual (median) count
  outline1px  every silhouette edge pixel is the ink colour (no gaps) and the pixel just inside it is not ink too (no doubled
              outline: flagged when doubled px > 15% of the edge)
  soft_alpha  alpha only 0 or 255 inside the role's frames

Known exceptions live in tools/check-sprite/art_allowlist.txt, one "atlas_relpath::role::check" per line (# comments ok).
Any issue on an allowlisted key is reported as a warning, not a failure.
"""
from __future__ import annotations

from pathlib import Path
from statistics import median

HOLE_MIN = 3
LIMB_DROP = 0.25
BLOB_MIN = 4
DOUBLED_FRAC = 0.15   # doubled-outline px must exceed this share of the edge (single dark details next to the ink are fine)
CHECKS = ("holes", "limbs", "outline1px", "soft_alpha")
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
N8 = N4 + ((1, 1), (1, -1), (-1, 1), (-1, -1))
ALLOWLIST = Path(__file__).with_name("art_allowlist.txt")
REPO = Path(__file__).resolve().parents[2]


def load_allowlist(path=ALLOWLIST):
    p = Path(path)
    if not p.exists():
        return set()
    return {l.split("#", 1)[0].strip() for l in p.read_text().splitlines() if l.split("#", 1)[0].strip()}


def atlas_key(atlas_path):
    a = Path(atlas_path).resolve()
    try:
        return str(a.relative_to(REPO))
    except ValueError:
        return a.name


def _components(cells, nbrs):
    cells, seen, out = set(cells), set(), []
    for c in cells:
        if c in seen:
            continue
        stack, comp = [c], []
        seen.add(c)
        while stack:
            x, y = stack.pop()
            comp.append((x, y))
            for dx, dy in nbrs:
                n = (x + dx, y + dy)
                if n in cells and n not in seen:
                    seen.add(n)
                    stack.append(n)
        out.append(comp)
    return out


def frame_stats(px, x0, y0, fw, fh, ink):
    """Per-frame measurements. ink is '#rrggbb'."""
    opaque, soft = set(), 0
    for y in range(fh):
        for x in range(fw):
            a = px[x0 + x, y0 + y][3]
            if a == 255:
                opaque.add((x, y))
            elif a:
                soft += 1
    st = {"soft": soft, "area": len(opaque), "bbox": 0, "blobs": 0, "holes": [], "gaps": 0, "doubled": 0, "edge": 0}
    if not opaque:
        return st
    xs = [p[0] for p in opaque]; ys = [p[1] for p in opaque]
    st["bbox"] = (max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1)
    st["blobs"] = sum(1 for c in _components(opaque, N8) if len(c) >= BLOB_MIN)
    # holes: transparent 4-components not touching the frame border
    trans = [(x, y) for y in range(fh) for x in range(fw) if (x, y) not in opaque]
    for comp in _components(trans, N4):
        if len(comp) >= HOLE_MIN and not any(x in (0, fw - 1) or y in (0, fh - 1) for x, y in comp):
            st["holes"].append(len(comp))
    hexof = lambda x, y: "#%02x%02x%02x" % px[x0 + x, y0 + y][:3]
    for (x, y) in opaque:
        outs = [(dx, dy) for dx, dy in N4 if (x + dx, y + dy) not in opaque]
        if not outs:
            continue
        st["edge"] += 1
        if hexof(x, y) != ink:
            st["gaps"] += 1
            continue
        # doubled: the pixel directly inward (away from every open side) is also an edge-free ink pixel
        for dx, dy in outs:
            ix, iy = x - dx, y - dy
            if (ix, iy) in opaque and hexof(ix, iy) == ink and all((ix + ex, iy + ey) in opaque for ex, ey in N4):
                st["doubled"] += 1
                break
    return st


def role_issues(px, frames, fw, fh, ink):
    """frames: list of dicts with x, y, name. Returns {check: [messages]}."""
    out = {c: [] for c in CHECKS}
    stats = [(fr["name"], frame_stats(px, fr["x"], fr["y"], fw, fh, ink)) for fr in frames]
    live = [s for _, s in stats if s["area"]]
    if not live:
        return out
    med_area = median(s["area"] for s in live); med_bbox = median(s["bbox"] for s in live)
    med_blobs = median(s["blobs"] for s in live)
    for name, s in stats:
        if not s["area"]:
            continue
        if s["soft"]:
            out["soft_alpha"].append(f"{name}: {s['soft']} soft-alpha px")
        if s["holes"]:
            out["holes"].append(f"{name}: {len(s['holes'])} enclosed hole(s) {sorted(s['holes'], reverse=True)[:3]} px")
        if s["area"] < (1 - LIMB_DROP) * med_area or s["bbox"] < (1 - LIMB_DROP) * med_bbox:
            out["limbs"].append(f"{name}: area {s['area']} / bbox {s['bbox']} vs role median {med_area:g} / {med_bbox:g}")
        if s["blobs"] > med_blobs:
            out["limbs"].append(f"{name}: {s['blobs']} disconnected blobs (role usual {med_blobs:g})")
        if s["gaps"] or s["doubled"] > max(2, DOUBLED_FRAC * s["edge"]):
            out["outline1px"].append(f"{name}: {s['gaps']} outline gap px, {s['doubled']} doubled-outline px")
    return out
