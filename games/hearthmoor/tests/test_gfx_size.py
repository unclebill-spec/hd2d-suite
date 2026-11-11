#!/usr/bin/env python3
"""No-browser self-test for smoke_muspelheim.gamefx_image_problems.

  python3 games/hearthmoor/tests/test_gfx_size.py

The live repo gamefx pairs must pass. A synthetic cropped PNG (json still claims
the pre-crop size and the row that was cut off) must fail.
"""
import json
import sys
import tempfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import smoke_muspelheim as sm


def _cropped_area(areas):
    """One area whose PNG was cropped to the top row and left fully transparent."""
    area = areas / "synth"
    art = area / "public" / "art" / "gamefx"
    art.mkdir(parents=True)
    cell = 8
    full = Image.new("RGBA", (cell * 2, cell * 2), (0, 0, 0, 0))
    for y in range(cell, cell * 2):
        for x in range(cell * 2):
            full.putpixel((x, y), (220, 60, 20, 255))
    full.crop((0, 0, cell * 2, cell)).save(art / "gamefx.png")
    (art / "gamefx.json").write_text(json.dumps({
        "image": "gamefx.png",
        "cell": cell,
        "size": [cell * 2, cell * 2],
        "effects": {"kept": {"row": 0, "frames": 2}, "clipped": {"row": 1, "frames": 2}},
    }))
    (area / "scene.json").write_text(json.dumps({
        "gamefx": {"image": "public/art/gamefx/gamefx.png", "json": "public/art/gamefx/gamefx.json"},
    }))


def main():
    root = sm.GAME / "areas"
    n = sum(1 for sp in root.glob("*/scene.json") if json.loads(sp.read_text()).get("gamefx"))
    live = sm.gamefx_image_problems(root)
    if n < 1 or live:
        print(f"FAIL live gamefx pairs={n} problems={json.dumps(live)[:2000]}")
        return 1
    print(f"live gamefx: {n} pairs, problems none")
    with tempfile.TemporaryDirectory() as td:
        areas = Path(td)
        _cropped_area(areas)
        found = sm.gamefx_image_problems(areas)
        probs = found.get("synth") or []
        size_bad = any(p.startswith("size ") for p in probs)
        outside = any("outside image" in p for p in probs)
        empty = any(p.endswith(":empty") for p in probs)
        if not (size_bad and outside and empty):
            print(f"FAIL synthetic cropped png problems={probs}")
            return 1
        print(f"cropped png: rejected {probs}")
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
