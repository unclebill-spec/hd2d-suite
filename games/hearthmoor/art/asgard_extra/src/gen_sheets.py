"""Asgard character sheets: python3 gen_sheets.py [sheet ...]  (writes ../sprite/*.png/json, ../check_sprite_report.json). Pillow + numpy; repo read-only.
AS_STUB=1 skips check-sprite (quick previews only)."""
import json, os
from pathlib import Path
import as_common as C, as_npcs as N, as_foes as F, as_boss as B
OUT = Path(__file__).resolve().parent.parent
A4 = ("idle", "walk", "attack", "die")
SHEETS = {
    "as_folk": (N.roles, N.FRAME_FOLK),
    "as_sigrun": (N.sigrun_roles, N.FRAME_FOLK),
    "as_enemies": (lambda: F.make(F.ENEM, A4), (64, 72)),
    "as_elites": (lambda: F.make(F.ELITE, A4), (100, 112)),
    "boss_sentinel": (B.sentinel_roles, B.FRAME_SENTINEL),
    "boss_aurelion": (B.aurelion_roles, B.FRAME_AURELION),
}
if os.environ.get("AS_STUB"):
    C.H.check_sprite = lambda p: {"roles": {}, "stub": True, "ok": True}
    C.H.report_line = lambda r: "stub"


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
    if not os.environ.get("AS_STUB"):
        rp = OUT / "check_sprite_report.json"
        old = json.loads(rp.read_text()) if rp.exists() else {}
        old.update(reps)
        rp.write_text(json.dumps(old, indent=1, default=str))
    return reps


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)
