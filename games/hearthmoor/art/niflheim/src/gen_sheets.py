"""Niflheim character sheets: python3 gen_sheets.py [sheet ...]  (writes ../sprite/*.png/json, ../check_sprite_report.json). Pillow + numpy; repo read-only.
NF_STUB=1 skips check-sprite (quick previews only)."""
import json, os
from pathlib import Path
import nf_common as C, nf_npcs as N, nf_foes as F, nf_boss as B
OUT = Path(__file__).resolve().parent.parent
A4 = ("idle", "walk", "attack", "die")
SHEETS = {
    "nf_folk": (lambda: N.roles(True), N.FRAME_FOLK),
    "nf_hrefna": (N.hrefna_roles, N.FRAME_FOLK),
    "nf_enemies": (lambda: F.make(F.ENEM, A4), (56, 68)),
    "nf_elites": (lambda: F.make(F.ELITE, A4), (88, 100)),
    "boss_colossus": (B.colossus_roles, B.FRAME_COLOSSUS),
    "boss_kael": (B.kael_roles, B.FRAME_KAEL),
    "boss_veyra": (B.veyra_roles, B.FRAME_VEYRA),
}
if os.environ.get("NF_STUB"):
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
    if not os.environ.get("NF_STUB"):
        rp = OUT / "check_sprite_report.json"
        old = json.loads(rp.read_text()) if rp.exists() else {}
        old.update(reps)
        rp.write_text(json.dumps(old, indent=1, default=str))
    return reps


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)
