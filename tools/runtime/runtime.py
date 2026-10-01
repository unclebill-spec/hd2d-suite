"""hd2d runtime: copy the three.js r160 HD-2D diorama engine into a folder.

    hd2d runtime --out PROJECT            # writes PROJECT/index.html, engine/, vendor/ (three r160 + GLTFLoader)

The engine loads PROJECT/scene.json (written by `hd2d assemble`). Static ES modules + import map: no build step.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

WEB = Path(__file__).resolve().parent / "web"


def copy_to(dest) -> Path:
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    for name in ("index.html",):
        shutil.copy2(WEB / name, dest / name)
    for d in ("engine", "vendor"):
        if (dest / d).exists():
            shutil.rmtree(dest / d)
        shutil.copytree(WEB / d, dest / d)
    return dest


def main(argv=None):
    ap = argparse.ArgumentParser(prog="hd2d runtime", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    d = copy_to(a.out)
    print(f"runtime: three.js r160 engine -> {d} (needs {d}/scene.json; build one with `hd2d assemble`)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
