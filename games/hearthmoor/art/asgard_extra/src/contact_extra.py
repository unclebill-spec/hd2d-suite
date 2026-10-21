"""contact sheet for asgard_extra"""
import json
from pathlib import Path
from PIL import Image
import as_common as C
H = C.H
OUT = Path(__file__).resolve().parent.parent


def strip(sheet, role, picks):
    m = json.loads((OUT / "sprite" / f"{sheet}.json").read_text()); fw, fh = m["frame"]
    row = Image.new("RGBA", (fw * len(picks), fh), (0, 0, 0, 0))
    for c, (f, a, i) in enumerate(picks):
        row.alpha_composite(H.frame_of(OUT / "sprite" / f"{sheet}.png", m, role, f, a, i), (c * fw, 0))
    return row


rep = json.loads((OUT / "check_sprite_report.json").read_text())
S = H.Sheet("Asgard extra - guard, Ingrith, red Aurelion P3, storm centaur v2, G7 void", "replacements / additions; the original asgard/ pack is untouched")
F5 = [("down", "idle", 0), ("down", "walk", 1), ("left", "walk", 1), ("up", "idle", 0), ("right", "idle", 0)]
S.section("ax_folk (40x44, 1x)", H.report_line(rep["ax_folk"]))
for r in ("as_guard", "ingrith"):
    S.cell(strip("ax_folk", r, F5), r, "", k=4)
S.section("ax_aurelion_p3 (144x224, 7x, red)", H.report_line(rep["ax_aurelion_p3"]))
S.cell(strip("ax_aurelion_p3", "aurelion_p3", [("down", "idle", 0), ("left", "walk", 1), ("up", "idle", 0), ("down", "cast", 2), ("down", "attack", 2), ("down", "die", 3)]), "aurelion_p3", "", k=1)
S.section("ax_centaur (64x72, 1.6x, bigger torso)", H.report_line(rep["ax_centaur"]))
S.cell(strip("ax_centaur", "storm_centaur", [("down", "idle", 0), ("down", "walk", 1), ("left", "walk", 2), ("down", "attack", 2), ("left", "attack", 2), ("down", "die", 3)]), "storm_centaur", "", k=2)
S.section("G7 void (night)", json.loads((OUT / "renders/luma.json").read_text()).__repr__())
S.cell(Image.open(OUT / "renders/scene_reliquary_g7_void_night.png"), "scene_reliquary_g7_void_night", "", k=2)
for n in ("void_floor", "void_rim", "void_shard"):
    S.cell(Image.open(OUT / f"renders/{n}_night.png"), n, "", k=3)
S.render(OUT / "contact_sheet.png")
