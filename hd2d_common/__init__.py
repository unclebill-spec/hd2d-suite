"""Shared helpers for hd2d-suite: seeded RNG, colours, palette loading, PNG helpers, tool loading."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import random
from pathlib import Path

SUITE = Path(__file__).resolve().parent.parent
TOOLS = SUITE / "tools"


def rng(seed, *tags) -> random.Random:
    """Stable RNG from seed + tags (never Python's salted hash())."""
    key = "|".join([str(seed)] + [str(t) for t in tags]).encode()
    return random.Random(int.from_bytes(hashlib.sha256(key).digest()[:8], "big"))


def hex2rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rgb2hex(c) -> str:
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(v)))) for v in c[:3])


def mix(a: str, b: str, t: float) -> str:
    ca, cb = hex2rgb(a), hex2rgb(b)
    return rgb2hex([ca[i] + (cb[i] - ca[i]) * t for i in range(3)])


def lum(h: str) -> float:
    r, g, b = hex2rgb(h)
    return 0.299 * r + 0.587 * g + 0.114 * b


def ensure(p) -> Path:
    p = Path(p)
    p.mkdir(parents=True, exist_ok=True)
    return p


def write_json(path, data, compact=False):
    path = Path(path)
    ensure(path.parent)
    with open(path, "w") as f:
        if compact:
            json.dump(data, f, separators=(",", ":"))
        else:
            json.dump(data, f, indent=1)
    return path


def read_json(path):
    with open(path) as f:
        return json.load(f)


def load_tool(name: str):
    """Import tools/<name>/<name_with_underscores>.py as a module."""
    mod = name.replace("-", "_")
    path = TOOLS / name / f"{mod}.py"
    spec = importlib.util.spec_from_file_location(f"hd2d_tool_{mod}", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def art_dir(project, tool: str) -> Path:
    """Bill's convention: outputs land in <project>/public/art/<tool>."""
    return ensure(Path(project) / "public" / "art" / tool)


def load_biome(biome: str, project=None) -> dict:
    """Load a biome palette: <project>/public/art/palette/<biome>/biome.json if built, else build in memory."""
    if project:
        p = Path(project) / "public" / "art" / "palette" / biome / "biome.json"
        if p.exists():
            return read_json(p)
    return load_tool("palette").biome_data(biome)


class Pal:
    """Palette accessor with ramp-based shade steps: pal['plaster'], pal.dk('plaster'), pal.lt(..)."""

    def __init__(self, biome: dict):
        self.b = biome
        self.c = biome["colors"]  # name -> hex
        self.ramps = biome["ramps"]  # ramp name -> [names light..dark]
        self._pos = {}
        for rname, names in self.ramps.items():
            for i, n in enumerate(names):
                self._pos.setdefault(n, (rname, i))

    def __getitem__(self, name):
        if name.startswith("#"):
            return name
        return self.c[name]

    def name_of(self, hexc):
        for k, v in self.c.items():
            if v == hexc:
                return k
        return None

    def step(self, name, d):
        if name.startswith("#"):
            name = self.name_of(name) or name
        if name not in self._pos:
            return self[name]
        r, i = self._pos[name]
        ramp = self.ramps[r]
        j = max(0, min(len(ramp) - 1, i + d))
        return self.c[ramp[j]]

    def dk(self, name, n=1):
        return self.step(name, n)

    def lt(self, name, n=1):
        return self.step(name, -n)

    def hexes(self):
        return list(self.c.values())
