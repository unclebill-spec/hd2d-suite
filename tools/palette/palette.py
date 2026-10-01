"""hd2d palette: cozy HD-2D biome palettes (16-28 colours) + day/dusk/night grade data.

    hd2d palette --biome cozy-village --out PROJECT/public/art/palette
    hd2d palette --biome all

Writes <out>/<biome>/biome.json, <biome>.gpl, swatch.png (and swatch_4x.png).
biome.json carries: colors (name->hex), ramps (light->dark), roles, and grades.day/dusk/night
that the runtime lerps on its clock (cycleT 0 midnight, 0.5 noon, 0.75 dusk).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from hd2d_common import ensure, hex2rgb, write_json, lum  # noqa: E402

from PIL import Image, ImageDraw  # noqa: E402

# Every biome uses the same colour NAMES so sprites, texels and kit can be re-skinned by biome.
NAMES = [
    "ink", "shadow",
    "plaster_hi", "plaster", "plaster_lo",
    "timber_hi", "timber", "timber_lo",
    "stone_hi", "stone", "stone_lo",
    "roof_hi", "roof", "roof_lo",
    "grass_hi", "grass", "moss", "leaf_deep",
    "flower_rose", "flower_gold", "flower_blue",
    "skin", "skin_lo", "cloth", "sky", "lamp", "white",
]

RAMPS = {
    "plaster": ["white", "plaster_hi", "plaster", "plaster_lo", "timber_lo", "ink"],
    "timber": ["plaster_lo", "timber_hi", "timber", "timber_lo", "ink"],
    "stone": ["plaster_hi", "stone_hi", "stone", "stone_lo", "shadow", "ink"],
    "roof": ["flower_gold", "roof_hi", "roof", "roof_lo", "ink"],
    "grass": ["flower_gold", "grass_hi", "grass", "moss", "leaf_deep", "ink"],
    "rose": ["white", "flower_rose", "roof_hi", "roof", "roof_lo", "ink"],
    "gold": ["white", "lamp", "flower_gold", "timber_hi", "timber", "timber_lo", "ink"],
    "blue": ["sky", "flower_blue", "cloth", "shadow", "ink"],
    "skin": ["plaster_hi", "skin", "skin_lo", "timber", "timber_lo", "ink"],
    "sky": ["white", "sky", "flower_blue", "cloth", "ink"],
    "dark": ["stone_lo", "shadow", "ink"],
}

BIOMES: dict[str, dict] = {
    "cozy-village": {
        "desc": "Warm market village: cream plaster, oak timber, terracotta roofs, mossy cobble, window boxes.",
        "colors": ["#2a1e1c", "#4c3a3e", "#f6ecd2", "#e6d2ac", "#c4a984", "#b07a44", "#7a4e2e", "#4a2e20",
                   "#cfc2a6", "#9c8e7a", "#6a5e56", "#d0704a", "#9a4630", "#622c24", "#b2c464", "#72a046",
                   "#4a7234", "#2c4c30", "#e47c8c", "#f2c24a", "#6c8cd4", "#f2c4a0", "#cc8c6c", "#3e5a8c",
                   "#94c0dc", "#ffb24a", "#fff8e6"],
    },
    "meadow": {
        "desc": "Open meadow hamlet: thatch roofs, pale timber, bright grass, wildflowers.",
        "colors": ["#22201a", "#3e4434", "#f8f0d8", "#e8dcb4", "#c8b48a", "#c09058", "#8a6438", "#54402a",
                   "#d6d0b4", "#a6a08a", "#6e6c5e", "#e2c06a", "#b89040", "#7a5a2a", "#c4dc6a", "#84b44c",
                   "#56883a", "#2e5a32", "#f08aa8", "#f8d850", "#8a9ce8", "#f4c8a4", "#d0906e", "#4a6aa0",
                   "#a8d4ec", "#ffbc50", "#fffcee"],
    },
    "harbor": {
        "desc": "Fishing harbour: whitewash, weathered driftwood, slate-blue roofs, rope tan, sea blue.",
        "colors": ["#1c1e26", "#384052", "#f4f2ea", "#dcd8cc", "#b4b0a4", "#a89070", "#76664e", "#4a4034",
                   "#c4c6c4", "#8e949a", "#5c626c", "#7a9ab4", "#4e6a88", "#30425a", "#a8bc72", "#6c9450",
                   "#466a40", "#284432", "#e8807c", "#f0c85a", "#4a8ac4", "#f0c6a2", "#c48a6c", "#2e4c78",
                   "#8ec4e0", "#ffb44c", "#ffffff"],
    },
    "autumn-orchard": {
        "desc": "Autumn orchard: rust leaves, warm brick, apple red, pumpkin gold, mossy stone.",
        "colors": ["#2a1a16", "#4e3434", "#f4e6cc", "#e0c8a0", "#bc9c78", "#b46e3a", "#80482a", "#4e2c1e",
                   "#c8b8a0", "#988870", "#685a50", "#c85a34", "#923a26", "#5e2420", "#d8b04c", "#a89040",
                   "#6c7034", "#3c4a2a", "#d84a3c", "#f0a830", "#7a7cc4", "#f0c09c", "#c8866a", "#4a4a7a",
                   "#a8c0d0", "#ffa83c", "#fff4e0"],
    },
    "snow-hamlet": {
        "desc": "Snow hamlet: snow-capped roofs, dark timber, ice-blue shadows, red berries, warm lamps.",
        "colors": ["#1a1a26", "#3c4258", "#f8f8fc", "#e2e6f0", "#b8c0d4", "#946a48", "#64462e", "#3a2a22",
                   "#c8ccd4", "#8e94a4", "#5c6274", "#c45a4a", "#8c3a34", "#58262a", "#a8bca0", "#6c8c72",
                   "#46644e", "#28403a", "#d4486a", "#f4c650", "#6a8cd8", "#f2c8ac", "#c88c74", "#34507e",
                   "#a4c4e4", "#ffb04a", "#ffffff"],
    },
}

# Grades: warm gold day, cool blue dusk, orange windows at night. Values the runtime uses directly.
# sun: colour, intensity, azimuth (deg, 0 = from +z/camera side, 90 = from +x), elevation (deg).
BASE_GRADES = {
    "day": {
        "sun_color": "#ffd49a", "sun_intensity": 3.1, "sun_azimuth": -40, "sun_elevation": 31,
        "hemi_sky": "#a8c4ec", "hemi_ground": "#7a6048", "hemi_intensity": 0.75,
        "fog_color": "#e8d8bc", "fog_near": 26, "fog_far": 70, "haze": 0.38, "valley_haze": 0.12,
        "sky_top": "#86b4e0", "sky_bottom": "#f4e0b8",
        "lamp_intensity": 0.0, "window_emissive": "#3a3c48", "window_intensity": 0.2,
        "sprite_tint": "#fff4e2", "exposure": 1.0, "saturation": 1.06, "shadow_tint": "#5a4a70",
        "warmth": 0.06, "bugs": 0.0, "motes": 1.0,
    },
    "dusk": {
        "sun_color": "#ff9c70", "sun_intensity": 1.05, "sun_azimuth": -70, "sun_elevation": 12,
        "hemi_sky": "#6a7ec8", "hemi_ground": "#4a3a50", "hemi_intensity": 0.95,
        "fog_color": "#7a84b8", "fog_near": 20, "fog_far": 60, "haze": 0.42, "valley_haze": 0.22,
        "sky_top": "#3a4c94", "sky_bottom": "#e89a84",
        "lamp_intensity": 1.0, "window_emissive": "#ffa040", "window_intensity": 1.4,
        "sprite_tint": "#c4ccf0", "exposure": 1.05, "saturation": 0.98, "shadow_tint": "#2a3270",
        "warmth": -0.05, "bugs": 0.6, "motes": 0.3,
    },
    "night": {
        "sun_color": "#8ea4e0", "sun_intensity": 0.36, "sun_azimuth": 30, "sun_elevation": 48,
        "hemi_sky": "#34407a", "hemi_ground": "#1c1a2a", "hemi_intensity": 0.6,
        "fog_color": "#1e2848", "fog_near": 16, "fog_far": 52, "haze": 0.42, "valley_haze": 0.26,
        "sky_top": "#0e1430", "sky_bottom": "#2c3866",
        "lamp_intensity": 1.6, "window_emissive": "#ff9a38", "window_intensity": 2.3,
        "sprite_tint": "#8a98cc", "exposure": 1.12, "saturation": 0.92, "shadow_tint": "#101838",
        "warmth": -0.08, "bugs": 1.0, "motes": 0.0,
    },
}

BIOME_GRADE_OVERRIDES = {
    "harbor": {"day": {"sun_color": "#fff0d0", "fog_color": "#d8e0e4", "sky_bottom": "#e8eef0"}},
    "autumn-orchard": {"day": {"sun_color": "#ffd090", "fog_color": "#e8c8a0", "sky_bottom": "#f4d0a0", "warmth": 0.1}},
    "snow-hamlet": {"day": {"sun_color": "#fff0dc", "sun_intensity": 2.2, "hemi_sky": "#c8d8f4", "fog_color": "#dce4f0",
                            "sky_top": "#9cc0e8", "sky_bottom": "#eef2f8", "sprite_tint": "#f4f4ff", "warmth": 0.0}},
    "meadow": {"day": {"sun_intensity": 2.8, "sky_top": "#7ab8ec"}},
}

# Clock stops on cycleT (shared with Game Layout One's day clock).
CLOCK = [
    {"t": 0.00, "grade": "night"}, {"t": 0.20, "grade": "night"}, {"t": 0.27, "grade": "dusk"},
    {"t": 0.36, "grade": "day"}, {"t": 0.66, "grade": "day"}, {"t": 0.76, "grade": "dusk"},
    {"t": 0.86, "grade": "night"}, {"t": 1.00, "grade": "night"},
]


def biome_names():
    return list(BIOMES)


def biome_data(biome: str) -> dict:
    if biome not in BIOMES:
        raise SystemExit(f"unknown biome {biome!r}; biomes: {', '.join(BIOMES)}")
    b = BIOMES[biome]
    cols = b["colors"]
    assert len(cols) == len(NAMES), (biome, len(cols))
    colors = dict(zip(NAMES, cols))
    if len(set(cols)) != len(cols):
        raise SystemExit(f"{biome}: duplicate colours")
    if not 16 <= len(cols) <= 28:
        raise SystemExit(f"{biome}: {len(cols)} colours, the law says 16-28")
    grades = {}
    for k, g in BASE_GRADES.items():
        gg = dict(g)
        gg.update(BIOME_GRADE_OVERRIDES.get(biome, {}).get(k, {}))
        gg["lamp_color"] = colors["lamp"]
        grades[k] = gg
    return {
        "biome": biome,
        "desc": b["desc"],
        "count": len(cols),
        "colors": colors,
        "order": NAMES,
        "ramps": RAMPS,
        "roles": {
            "plaster": ["plaster_hi", "plaster", "plaster_lo"], "timber": ["timber_hi", "timber", "timber_lo"],
            "moss": ["grass", "moss", "leaf_deep"], "flowers": ["flower_rose", "flower_gold", "flower_blue"],
            "outline": ["ink"], "skin": ["skin", "skin_lo"],
        },
        "grades": grades,
        "clock": CLOCK,
    }


def write_gpl(data: dict, path: Path):
    lines = ["GIMP Palette", f"Name: hd2d {data['biome']}", "Columns: 9", "#"]
    for n in data["order"]:
        r, g, b = hex2rgb(data["colors"][n])
        lines.append(f"{r:3d} {g:3d} {b:3d}\t{n}")
    path.write_text("\n".join(lines) + "\n")


def swatch(data: dict) -> Image.Image:
    """Native swatch: 9 columns of 8x8 cells, then ramps as rows, then grade strips. Hard pixels only."""
    names = data["order"]
    cols = 9
    rows = (len(names) + cols - 1) // cols
    cell = 8
    ramp_rows = len(data["ramps"])
    w = cols * cell
    h = rows * cell + 2 + ramp_rows * 4 + 2 + 3 * 4
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, n in enumerate(names):
        x, y = (i % cols) * cell, (i // cols) * cell
        d.rectangle([x, y, x + cell - 1, y + cell - 1], fill=data["colors"][n])
    y0 = rows * cell + 2
    for j, (rn, rr) in enumerate(data["ramps"].items()):
        for i, n in enumerate(rr):
            d.rectangle([i * 6, y0 + j * 4, i * 6 + 5, y0 + j * 4 + 3], fill=data["colors"][n])
    y1 = y0 + ramp_rows * 4 + 2
    for j, g in enumerate(("day", "dusk", "night")):
        gr = data["grades"][g]
        strip = [gr["sky_top"], gr["sky_bottom"], gr["sun_color"], gr["hemi_sky"], gr["fog_color"],
                 gr["window_emissive"], gr["sprite_tint"], gr["shadow_tint"], gr["lamp_color"]]
        for i, c in enumerate(strip):
            d.rectangle([i * 8, y1 + j * 4, i * 8 + 7, y1 + j * 4 + 3], fill=c)
    return im


def build(biome: str, out: Path) -> dict:
    data = biome_data(biome)
    o = ensure(out / biome)
    write_json(o / "biome.json", data)
    write_gpl(data, o / f"{biome}.gpl")
    sw = swatch(data)
    sw.save(o / "swatch.png")
    sw.resize((sw.width * 4, sw.height * 4), Image.NEAREST).save(o / "swatch_4x.png")
    return {"biome": biome, "count": data["count"], "dir": str(o)}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="hd2d palette", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--biome", default="all", help="biome name or 'all' (" + ", ".join(BIOMES) + ")")
    ap.add_argument("--out", default="public/art/palette")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args(argv)
    if a.list:
        for k, v in BIOMES.items():
            print(f"{k:16s} {len(v['colors'])} colours  {v['desc']}")
        return 0
    names = list(BIOMES) if a.biome == "all" else [a.biome]
    for n in names:
        r = build(n, Path(a.out))
        print(f"palette {r['biome']}: {r['count']} colours -> {r['dir']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
