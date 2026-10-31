"""Asgard extra pack (Art seat, 2026-10-20). python3 gen_extra.py [sheet ...]  -> ../sprite/*.png/json + ../check_sprite_report.json (AS_STUB=1 = no check).
ax_folk: as_guard + ingrith (40x44, as_folk layout idle+walk). ax_aurelion_p3: aurelion_p3 in a red palette (144x224, boss_aurelion grid).
ax_centaur: storm_centaur with a bigger human torso (64x72, as_enemies grid)."""
import json, os
from pathlib import Path
import as_common as C, as_npcs as N, as_boss as B, as_beasts as BE, as_foes as F
from as_common import R
from as_giant import giant
OUT = Path(__file__).resolve().parent.parent
if os.environ.get("AS_STUB"):
    C.H.check_sprite = lambda p: {"roles": {}, "stub": True, "ok": True}
    C.H.report_line = lambda r: "stub"


def cap(cv, c):
    """light leather guard cap with a gold rim (no helm plate)"""
    y0 = c["hcy"] - c["hh"] * .95; y1 = c["hcy"] - c["hh"] * .45
    for y in range(int(y0), int(y1) + 1):
        w = c["hhw"] * (0.75 + 0.3 * (y - y0) / max(1, y1 - y0))
        cv.rect(c["hcx"] - w, y, c["hcx"] + w, y, "timber" if y < y1 else "flower_gold")


def bracers(cv, c):
    for hx, hy in c["hands"]:
        cv.rect(hx - 1, hy - 3, hx + 1, hy - 2, "timber_lo")


GUARD = dict(skin="skin", hair="timber", hairstyle="short", tunic="slate", jerkin="leather", trousers="grey", belt=("timber_lo", "ink"), buckle="flower_gold",
             boots=("timber", "timber_lo"), extra=N.combine(N.tabard, cap, bracers, N.spear))
INGRITH = dict(skin="skin", hair=("white", "sky", "flower_blue"), hairstyle="bun", tunic="icedeep", trousers="slate", belt=("cloth", "ink"), buckle="stone_hi",
               boots=("timber", "timber_lo"), extra=N.combine(N.cloak(("sky", "flower_blue", "cloth")), N.circlet_band))


def folk():
    d = dict(scale=1.0, anims=N.A2, named=True, stats_hint={"tier": "npc", "height_x_player": 1.0})
    return {"as_guard": dict(draw=giant(GUARD, N.Ht(1.0)), desc="Goldspire guard (1x): storm-blue tunic, leather jerkin under a gilded tabard, belted grey trousers, boots, leather cap, bracers, spear. Light gear, no plate.", **d),
            "ingrith": dict(draw=giant(INGRITH, N.Ht(1.0)), desc="Envoy Ingrith Goldrune (1x, story 5 roster): icy-blue tunic, belted blue trousers, silver-buckled belt, boots, gold-pinned icy-blue cloak, gold circlet, ash-silver bun.", **d)}


# ---- red Aurelion P3: draw the gold figure, then remap every palette name to a red ramp (palette only -> passes check-sprite with no allow-list)
REDMAP = {"flower_gold": "roof", "lamp": "roof_hi", "timber_hi": "roof", "timber": "roof_lo", "timber_lo": "shadow",
          "plaster_hi": "roof_hi", "plaster": "roof", "plaster_lo": "roof_lo", "stone_hi": "roof", "stone": "roof_lo", "stone_lo": "shadow",
          "white": "flower_rose", "sky": "flower_rose", "flower_blue": "roof", "cloth": "roof_lo", "skin": "roof_hi", "skin_lo": "roof"}


def recolour(draw):
    hx = {C.H.PAL.c[a]: C.H.PAL.c[b] for a, b in REDMAP.items()}
    def d(cv, face, anim, i):
        draw(cv, face, anim, i)
        p = cv.s.p
        for y in range(cv.h):
            row = p[y]
            for x in range(cv.w):
                v = row[x]
                if v is not None and v in hx:
                    row[x] = hx[v]
    for k in ("fall", "die_mode", "sink_cols"):
        if hasattr(draw, k):
            setattr(d, k, getattr(draw, k))
    return d


def aurelion_red():
    r = B.aurelion_roles()["aurelion_p3"]
    dr = r["draw"]; dr.sink_cols = ("flower_rose", "roof_hi", "roof", "roof_lo")
    return {"aurelion_p3": dict(r, draw=recolour(dr), light={"color": "#e8321e", "intensity": 1.6, "range": 10.0},
            desc="Aurelion phase 3 (REPLACEMENT, red): plate, cape and blade pushed to the crimson/rust ramp (roof_lo/roof/roof_hi), rose-lit seams and eyes; pair with fx dawn_flame_red + pool_red for the red glow.")}


def centaur():
    BE.CENT_UH = 1.08
    return F.make({"storm_centaur": F.ENEM["storm_centaur"]}, ("idle", "walk", "attack", "die"))


SHEETS = {"ax_folk": (folk, N.FRAME_FOLK), "ax_aurelion_p3": (aurelion_red, B.FRAME_AURELION), "ax_centaur": (centaur, (64, 72))}


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
            rp = OUT / "check_sprite_report.json"
            old = json.loads(rp.read_text()) if rp.exists() else {}
            old[n] = r; rp.write_text(json.dumps(old, indent=1, default=str))
    return reps


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)
