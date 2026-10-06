#!/usr/bin/env python3
"""Hearthmoor palette check: every opaque pixel of the shipped atlases must be a cozy-village biome colour, or an
approved neon accent where neon is allowed.

  effects   areas/*/public/art/{spells,particles,gamefx}/*.png and the art packs' gamefx atlases (art/*/gamefx*.png,
            art/*/*_fx*.png): biome + NEON (red / violet / moss green / neon blue / cold fire) + ORB_NEON.
  orbs      orb lantern / glow-orb pieces (role or effect names starting orb_ / glow_orb): biome + NEON + ORB_NEON.
  sprites   areas/*/public/art/sprite/*.png (actors, pets, bosses): biome only, plus check_sprite's scoped
            NEON_PETS_ALLOW for the three pets. ORB_NEON is NOT allowed here.

ORB_NEON (neon green #3cf08a and pink #ff4fc8, each with its _hi / _lo shade) came with the 2026-10 art packs
(verdant_heart, orb_lanterns) for glow orbs, fireflies and bioluminescence. Bill's rule: effects and orbs only.
Usage: python3 tests/check_palette.py [--areas a,b] [--extra path.png ...]
"""
import argparse
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

from PIL import Image

GAME = Path(__file__).resolve().parents[1]
SUITE = GAME.parents[1]
_spec = importlib.util.spec_from_file_location("check_sprite", SUITE / "tools/check-sprite/check_sprite.py")
cs = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(cs)

NEON = {"#e0302a", "#a81c22", "#ff5a4a",          # red
        "#a45cf0", "#d4a8ff", "#6a34b8",          # violet
        "#5aec3c", "#c4ff8a", "#24a03a",          # moss green (moss-pup spores)
        "#2ab4ff", "#a6ecff", "#1c62d8",          # neon blue (portal / temple)
        "#5ab4f0", "#d8f4ff", "#2a6cb0"}          # cold fire (Sefa / Ravenhold: kit_harbor + kit_bifrost glow pixels)
ORB_NEON = {"#3cf08a", "#b8ffd4", "#14a85a",      # neon green mid / hi / lo
            "#ff4fc8", "#ffb4ea", "#b82a8c"}      # neon pink mid / hi / lo


def colours(path, box=None):
    im = Image.open(path).convert("RGBA")
    if box:
        im = im.crop(box)
    return Counter("#%02x%02x%02x" % p[:3] for p in (im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata()) if p[3] > 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--areas", default="")
    ap.add_argument("--extra", nargs="*", default=[], help="extra effect atlases (e.g. staged packs)")
    a = ap.parse_args()
    pal = set(cs.load_biome("cozy-village", None)["colors"].values())
    areas = [x for x in a.areas.split(",") if x] or sorted(p.parent.name for p in (GAME / "areas").glob("*/scene.json"))
    fails, n = [], 0

    def judge(path, allowed, label, what=""):
        nonlocal n
        n += 1
        off = {k: v for k, v in colours(path).items() if k not in allowed}
        if off:
            fails.append(f"{label}: {path.relative_to(GAME) if GAME in path.parents else path}{what} off-palette "
                         + ", ".join(f"{k}x{v}" for k, v in sorted(off.items(), key=lambda kv: -kv[1])[:6]))

    fx_ok = pal | NEON | ORB_NEON
    for ar in areas:
        art = GAME / "areas" / ar / "public/art"
        for k in ("spells", "particles", "gamefx"):
            for p in sorted((art / k).glob("*.png")):
                judge(p, fx_ok, "effect")
        for p in sorted((art / "sprite").glob("*.png")):
            jp = p.with_suffix(".json")
            meta = json.loads(jp.read_text()) if jp.exists() else {}
            roles = meta.get("roles", {})
            if not roles or "frame" not in meta:
                judge(p, pal, "sprite"); continue
            # per role row: pets get their scoped neon, orb roles get ORB_NEON, everything else biome only
            fw, fh = meta["frame"] if isinstance(meta["frame"], list) else (meta["frame"], meta["frame"])
            im_w = Image.open(p).size[0]
            for r, rv in roles.items():
                if "row" not in rv or rv.get("sheet"):
                    continue
                allowed = pal | set(cs.NEON_PETS_ALLOW.get(r, ()))
                if r.startswith(("orb_", "glow_orb")):
                    allowed |= NEON | ORB_NEON
                n += 1
                off = {c: v for c, v in colours(p, (0, rv["row"] * fh, im_w, (rv["row"] + 1) * fh)).items() if c not in allowed}
                if off:
                    fails.append(f"sprite: {p.relative_to(GAME)} role {r} off-palette "
                                 + ", ".join(f"{k}x{v}" for k, v in sorted(off.items(), key=lambda kv: -kv[1])[:6]))
    for p in list((GAME / "art").glob("*/*fx*.png")) + [Path(x) for x in a.extra]:
        judge(p.resolve(), fx_ok, "effect")
    print(f"palette: {n} atlases / sprite rows checked, {len(fails)} failing")
    for f in fails:
        print("  FAIL", f)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
