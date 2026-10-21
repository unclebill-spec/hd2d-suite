"""Helheim character sheets: python3 gen_sheets.py [sheet ...] -> ../sprite + ../check_sprite_report.json. AS_STUB=1 skips check-sprite."""
import json, os
from pathlib import Path
import as_common as C, hh_roles as HR
OUT = Path(__file__).resolve().parent.parent
SHEETS = {"hh_folk": (HR.folk_roles, HR.FRAME_FOLK), "hh_inkling": (HR.pet_roles, HR.FRAME_FOLK), "hh_enemies": (HR.enemy_roles, (64, 72)),
          "hh_elites": (HR.elite_roles, (100, 112)), "boss_mordrath": (HR.boss_roles, HR.FRAME_BOSS),
          "hh_enemies_safe": (lambda: HR.enemy_roles(False), (64, 72)), "hh_elites_safe": (lambda: HR.elite_roles(False), (100, 112)),
          "boss_mordrath_safe": (lambda: HR.boss_roles(False), HR.FRAME_BOSS)}
# Proposed scoped allow-list (lead adds to hd2d-suite check-sprite; NOT edited here). Applied in-memory only when HH_LOCAL_ALLOW=1.
HH_NEON_ALLOW = {r: {HR.VIO, HR.VIO_D} for r in ("gloam_knight", "odric", "mordrath", "mordrath_p2", "mordrath_p3")}
if os.environ.get("HH_LOCAL_ALLOW"):
    _cs = C.H.load_tool("check-sprite")
    _orig = dict(_cs.NIFL_NEON_ALLOW)
    _cs.NIFL_NEON_ALLOW.update({r: set(v) for r, v in HH_NEON_ALLOW.items()})   # temporary, this process only
    C.H.load_tool = (lambda f: (lambda n: _cs if n == "check-sprite" else f(n)))(C.H.load_tool)
if os.environ.get("AS_STUB"):
    C.H.check_sprite = lambda p: {"roles": {}, "stub": True, "ok": True}
    C.H.report_line = lambda r: "stub"


def main(only=None):
    reps = {}
    for n, (fn, fr) in SHEETS.items():
        if only and n not in only:
            continue
        r = C.write_big(OUT / "sprite", n, fn(), fr); reps[n] = r
        print(n, C.H.report_line(r), flush=True)
        for role, v in r["roles"].items():
            if v.get("issues"):
                print("  ", role, v.get("colors"), v["issues"][:3])
        if not os.environ.get("AS_STUB"):
            rp = OUT / ("check_sprite_report_local_allow.json" if os.environ.get("HH_LOCAL_ALLOW") else "check_sprite_report.json")
            old = json.loads(rp.read_text()) if rp.exists() else {}
            old[n] = r; rp.write_text(json.dumps(old, indent=1, default=str))
    return reps


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)
