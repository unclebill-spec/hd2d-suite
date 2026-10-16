"""Jotunheim character sheets: python3 gen_sheets.py  (writes ../sprite/*.png/json, ../check_sprite_report.json). Pillow + numpy; repo read-only."""
import json
from pathlib import Path
import jt_common as C, jt_npcs as N, jt_foes as F, jt_boss as B
OUT = Path(__file__).resolve().parent.parent
A4 = ("idle", "walk", "attack", "die")
SHEETS = {
    "jt_giants": (N.roles, N.FRAME),
    "ulfar": (F.ulfar_roles, (64, 100)),
    "jt_enemies": (lambda: F.make(F.ENEM, A4), (56, 68)),
    "boss_hrimgard": (B.roles, B.FRAME),
    "jt_elites": (lambda: F.make(F.ELITE, A4), (88, 100)),
}

def main(only=None):
    reps = {}
    for n, (fn, fr) in SHEETS.items():
        if only and n not in only:
            continue
        r = C.write_big(OUT / "sprite", n, fn(), fr)
        reps[n] = r
        print(n, C.H.report_line(r))
        for role, v in r["roles"].items():
            if v.get("issues"):
                print("  ", role, v["colors"], v["issues"][:3])
    return reps

if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)
