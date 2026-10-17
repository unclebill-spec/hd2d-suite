"""Jotunheim character sheets: python3 gen_sheets.py  (writes ../sprite/*.png/json, ../check_sprite_report.json). Pillow + numpy; repo read-only."""
import json
from pathlib import Path
import mp_common as C, mp_npcs as N, mp_foes as F, mp_boss as B
OUT = Path(__file__).resolve().parent.parent
A4 = ("idle", "walk", "attack", "die")
SHEETS = {
    "mp_folk": (lambda: N.roles(True), N.FRAME_FOLK),
    "mp_giants": (lambda: N.roles(False), N.FRAME),
    "mp_enemies": (lambda: F.make(F.ENEM, A4), (56, 68)),
    "boss_vharzul": (B.roles, B.FRAME),
    "mp_elites": (lambda: F.make(F.ELITE, A4), (88, 100)),
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
