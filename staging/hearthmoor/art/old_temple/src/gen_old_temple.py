"""Old Temple pack generator (Hearthmoor Art seat). Run:  python3 gen_old_temple.py
Writes ../ (the old_temple pack). Reads the hd2d-suite repo read-only."""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "_lib"))   # the shared lib wins; src/hmart.py is its frozen copy
import hmart as H  # noqa: E402
import kit_old_temple as KO  # noqa: E402
from PIL import Image  # noqa: E402

OUT = HERE.parent
CELL = 48
RAINBOW = ("neon_red", "lamp", "flower_gold", "grass_hi", "neon_blue", "flower_blue", "neon_violet")


def h2(*a):
    return H.rng(104, *a).random()


# ============================================================== gamefx
def riftgate_vortex_lit():
    """the open Rift-gate: a two-arm cold-fire spiral (ink core, neon-blue arms with sky / white streaks), a burning
    neon-blue rim with tongues licking up and round, and the seven Rainbow-Rift glints orbiting it"""
    out = []
    cx, cy, rx, ry = 23.5, 26.0, 16.5, 21.0
    for f in range(8):
        F = H.Fx(CELL)
        ph = f / 8.0
        for y in range(CELL):
            for x in range(CELL):
                dx, dy = (x - cx) / rx, (y - cy) / ry
                d = math.hypot(dx, dy)
                if d > 1.0:
                    continue
                a = math.atan2(dy, dx)
                s_ = (a / math.tau * 2 + math.log(d + 0.08) * 1.15 - ph) % 1.0
                if d < 0.13:
                    c = "white" if (x + y + f) % 3 == 0 else "neon_blue_hi"
                elif d < 0.3:
                    c = "neon_blue" if s_ < 0.45 else "cloth"
                elif d > 0.87:
                    c = "neon_blue" if (x + y + f) % 2 == 0 or s_ < 0.5 else "neon_blue_lo"
                else:
                    c = ("white" if s_ < 0.07 else "sky" if s_ < 0.2 else "neon_blue" if s_ < 0.38
                         else "neon_blue_lo" if s_ < 0.55 else "cloth" if s_ < 0.78 else ("cloth" if (x + y) % 2 else "ink"))
                F.set(x, y, c)
        for k in range(14):                                  # cold-fire tongues off the rim
            a = k / 14 * math.tau + ph * math.tau * 0.25
            bx, by = cx + math.cos(a) * rx, cy + math.sin(a) * ry
            hgt = 2 + int(3 * h2("vt", k, f))
            for t in range(hgt):
                F.set(bx + math.cos(a) * t * 0.6, by + math.sin(a) * t * 0.6 - t * 0.7, "neon_blue_hi" if t == hgt - 1 else "neon_blue")
        for k in range(7):                                   # the Rainbow Rift's seven glints orbit the rim
            ang = -ph * math.tau + k * math.tau / 7
            gx, gy = cx + math.cos(ang) * (rx + 3.5), cy + math.sin(ang) * (ry + 2.5)
            F.set(gx, gy, RAINBOW[k]); F.set(gx + 1, gy, RAINBOW[k])
            if (k + f) % 3 == 0:
                F.set(gx, gy - 1, "white")
        out.append(F)
    return out


def riftgate_seal_dormant():
    """the gate asleep: a dark, barely-turning stone haze (ink / shadow, faint cloth streaks), a dashed cold rim and a
    small lantern-shaped lock rune (Grandpa Alder's lantern charm fits it) with a slow faint heartbeat"""
    out = []
    cx, cy, rx, ry = 23.5, 26.0, 16.5, 21.0
    for f in range(6):
        F = H.Fx(CELL)
        ph = f / 6.0 * 0.2
        beat = f in (2, 3)
        for y in range(CELL):
            for x in range(CELL):
                dx, dy = (x - cx) / rx, (y - cy) / ry
                d = math.hypot(dx, dy)
                if d > 1.0:
                    continue
                a = math.atan2(dy, dx)
                s_ = (a / math.tau * 3 + math.log(d + 0.1) * 0.7 - ph) % 1.0
                if d > 0.94:
                    c = "neon_blue_lo" if (int((a / math.tau) * 44) + f) % 4 == 0 else "cloth"
                elif s_ < 0.07 and (x + y) % 2 == 0:
                    c = "neon_blue_lo"
                elif s_ < 0.45 or d > 0.8:
                    c = "cloth"
                else:
                    c = "cloth" if (x + y) % 2 == 0 else "ink"
                F.set(x, y, c)
        lo, hi = ("neon_blue", "neon_blue_hi") if beat else ("neon_blue_lo", "neon_blue")
        for yy in range(-5, 6):                              # a lantern rune: body, cap, ring, base
            w = 3 if -3 <= yy <= 3 else 2
            F.set(cx - w, cy + yy, lo); F.set(cx + w, cy + yy, lo)
        for xx in range(-3, 4):
            F.set(cx + xx, cy - 5, lo); F.set(cx + xx, cy + 5, lo)
        F.ring(cx, cy - 8, 1.6, 1.6, lo)
        F.set(cx, cy, hi); F.set(cx, cy - 1, hi if beat else lo); F.set(cx, cy + 1, lo)
        for k in range(3):
            mx = cx + (k - 1) * 8 + (1 if (f + k) % 2 else 0)
            my = cy + 16 - ((f * 3 + k * 9) % 30)
            F.set(mx, my, "neon_blue_lo")
        out.append(F)
    return out


def riftgate_awaken():
    """one-shot: the lantern charm touches the lock, the rune flares white, rings race out, the spiral spins up"""
    out = []
    cx, cy = 23.5, 26.0
    lit = riftgate_vortex_lit()
    dark = riftgate_seal_dormant()
    for f in range(8):
        base = dark[2] if f < 3 else lit[f % 8]
        F = H.Fx(CELL)
        F.p = [row[:] for row in base.p]
        if f >= 3:                                           # the spiral grows from the core outward
            t = (f - 3) / 4
            for y in range(CELL):
                for x in range(CELL):
                    d = math.hypot((x - cx) / 16.5, (y - cy) / 21)
                    if d <= 1 and d > 0.25 + t * 0.85:
                        F.p[y][x] = dark[f % 6].p[y][x]
        r = 2 + f * 3.2
        F.ring(cx, cy, r, r * 1.25, "white" if f < 4 else "neon_blue_hi", 1.0, start=f * 0.3, dots=1 if f < 3 else 2)
        F.ring(cx, cy, r * 0.6, r * 0.75, "neon_blue_hi", 1.0, start=-f * 0.3, dots=3)
        if f < 4:
            F.star(cx, cy, 3 - (f > 1), "white", "neon_blue_hi", "neon_blue")
        for k in range(10):
            a = k / 10 * math.tau + f * 0.2
            rr = 4 + f * 2.6 + (k % 3)
            if (k + f) % 2 == 0:
                F.star(cx + math.cos(a) * rr, cy + math.sin(a) * rr * 1.2, 1 if f < 6 else 0, "white", "sky", "neon_blue")
        out.append(F)
    return out


def riftgate_ring_lit():
    """ground decal in front of the lit gate: a dithered cold-fire pool inside a stone ring of turning rune dashes"""
    out = []
    pools = H.pool_frames(("sky", "flower_blue", "cloth"), CELL, 8, "rgring", rmax=19)
    for f in range(8):
        F = pools[f]
        cx, cy, R = 23.5, 23.5, 22.5
        for i in range(150):
            a = i / 150 * math.tau
            F.set(cx + math.cos(a) * R, cy + math.sin(a) * R * H.DECAL_SQUASH, "shadow" if i % 3 else "stone_lo")
        for k in range(16):
            a = k / 16 * math.tau + f / 8 * math.tau / 8
            c = "neon_blue_hi" if (k + f) % 4 == 0 else "neon_blue"
            for t in range(3):
                aa = a + t * 0.05
                F.set(cx + math.cos(aa) * (R - 2), cy + math.sin(aa) * (R - 2) * H.DECAL_SQUASH, c)
        out.append(F)
    return out


def temple_coldfire():
    """the sacred brazier's flame: a tall neon-blue cold-fire tongue (cloth rim, flower_blue, sky heart, white core)
    with neon sparks leaving the tip"""
    out = []
    for f in range(6):
        F = H.Fx(CELL)
        sway = [0, 1, 1, 0, -1, -1][f]
        hgt = [27, 30, 28, 31, 28, 29][f]
        base = 47
        for y in range(base, base - hgt, -1):
            k = (base - y) / hgt
            hw = 8.0 * (1 - k) ** 0.8 * (1 + 0.25 * math.sin(k * 6 + f))
            cx = 23.5 + sway * k * 3
            for x in range(int(cx - hw - 1), int(cx + hw + 2)):
                d = abs(x - cx) / max(0.6, hw)
                if d > 1:
                    continue
                c = "white" if d < 0.28 and k < 0.5 else "sky" if d < 0.55 else "flower_blue" if d < 0.85 else "cloth"
                if k > 0.7 and d > 0.5:
                    c = "neon_blue"
                F.set(x, y, c)
        for k in range(4):
            sy = base - hgt - 2 - ((f + k * 2) % 6) * 2
            F.set(23.5 + sway * 3 + (k - 1.5) * 3, sy, "neon_blue_hi" if k % 2 else "white")
        out.append(F)
    return out


def coldfire_pool_wide():
    out = H.pool_frames(("sky", "flower_blue", "cloth"), CELL, 6, "cpw")
    for f, F in enumerate(out):
        for k in range(10):
            x = 8 + (k * 13 + f * 5) % 32
            y = 16 + (k * 7) % 16
            if F.get(x, y) in ("sky", "flower_blue"):
                F.set(x, y, "white")
    return out


def glasslight(cols):
    """stained-glass light thrown on the floor at dusk: a squashed lancet patch of coloured squares, shimmering"""
    def fn():
        out = []
        for f in range(4):
            F = H.Fx(CELL)
            for gy in range(7):
                for gx in range(4):
                    if gy == 0 and gx in (0, 3):
                        continue
                    x0 = 12 + gx * 6 + gy * 1.2
                    y0 = 10 + gy * 4
                    c = cols[(gx + gy * 2 + (gx * gy) % 2) % len(cols)]
                    for yy in range(3):
                        for xx in range(5):
                            if (xx + yy + f + gx) % 2 == 0 or (yy == 1 and xx == 2):
                                F.set(x0 + xx + yy * 0.4, y0 + yy, c)
            out.append(F)
        return out
    return fn


def faceless_gaze():
    """The Faceless Statues quest: at night two thin slits of cold light open on a statue's smooth mask"""
    out = []
    for f in range(4):
        F = H.Fx(CELL)
        on = [0, 1, 2, 1][f]
        for sx in (-3, 2):
            for t in range(on + 1):
                F.set(23 + sx + t, 30, "neon_blue_hi" if on == 2 else "neon_blue")
            if on == 2:
                F.set(23 + sx, 29, "neon_blue_lo")
        if on == 2:
            F.set(23.5, 26, "white")
        out.append(F)
    return out


FX = {
    "riftgate_vortex_lit": {"fn": riftgate_vortex_lit, "fps": 8, "kind": "billboard", "lift": 0.40, "pivot": [24, 47],
                            "light": {"color": "neon_blue", "intensity": 1.6, "range": 7.0},
                            "notes": "place at riftgate_arch.markers.rift (opening 1.9 x 3.1 m); with riftgate_glow_lit"},
    "riftgate_seal_dormant": {"fn": riftgate_seal_dormant, "fps": 3, "kind": "billboard", "lift": 0.40, "pivot": [24, 47],
                              "light": {"color": "neon_blue_lo", "intensity": 0.2, "range": 2.5},
                              "notes": "the gate before Keeper of the Gate; with riftgate_glow_dormant"},
    "riftgate_awaken": {"fn": riftgate_awaken, "fps": 10, "kind": "billboard", "lift": 0.40, "pivot": [24, 47], "loop": False,
                        "light": {"color": "neon_blue_hi", "intensity": 2.4, "range": 9.0, "curve": [0.2, 0.4, 1.0, 1.0, 0.9, 0.8, 0.7, 0.6]},
                        "notes": "one-shot transition dormant -> lit (Keeper of the Gate), then swap to riftgate_vortex_lit"},
    "riftgate_ring_lit": {"fn": riftgate_ring_lit, "fps": 6, "kind": "decal", "lift": 0.42, "pivot": [24, 24],
                          "notes": "ground pool + rune ring in front of the lit gate (on the plinth top, y 0.40)"},
    "temple_coldfire": {"fn": temple_coldfire, "fps": 8, "kind": "billboard", "lift": 1.10, "pivot": [24, 47],
                        "light": {"color": "sky", "intensity": 1.1, "range": 5.5},
                        "notes": "on temple_brazier_cold (bowl top y 1.10)"},
    "coldfire_pool_wide": {"fn": coldfire_pool_wide, "fps": 4, "kind": "decal", "lift": 0.02, "pivot": [24, 24],
                           "notes": "under each lit brazier / the keeper's lantern; light zone r ~2.4 m"},
    "glasslight_violet": {"fn": glasslight(("neon_violet", "neon_violet_lo", "neon_violet_hi", "flower_gold")), "fps": 2,
                          "kind": "decal", "lift": 0.02, "pivot": [24, 24], "notes": "dusk only, 1.8 m in front of stained_window"},
    "glasslight_gold": {"fn": glasslight(("flower_gold", "lamp", "white", "neon_blue")), "fps": 2, "kind": "decal",
                        "lift": 0.02, "pivot": [24, 24], "notes": "dusk only, alternate window"},
    "faceless_gaze": {"fn": faceless_gaze, "fps": 3, "kind": "billboard", "lift": 2.05, "pivot": [24, 47],
                      "notes": "The Faceless Statues (night): over faceless_statue's mask (mask centre y ~2.34)"},
}


# ============================================================== NPCs
def keeper_extra(s, sp, L, face, bob, anim, i):
    """Mother Ilse: a pale-blue stole down the front of her cream blouse and a cold-fire gem in her hair"""
    top, hip = L["torso_top"] + bob, L["hip"] + bob
    if face == "down":
        for y in range(top + 1, hip - 1):
            s.set(7, y, "flower_blue"); s.set(12, y, "flower_blue")
        s.set(7, hip - 2, "sky"); s.set(12, hip - 2, "sky")
        s.set(10, L["head_top"] + bob + 1, "sky"); s.set(9, L["head_top"] + bob + 1, "white")
    elif face == "up":
        s.hspan(top, 6, 13, "flower_blue")
        s.set(10, top + 1, "flower_blue"); s.set(9, top + 1, "flower_blue")
    else:
        for y in range(top + 1, hip - 1):
            s.set(7, y, "flower_blue")
        s.set(6, L["head_top"] + bob + 2, "sky")


def archivist_extra(s, sp, L, face, bob, anim, i):
    """Brother Tamsin: an ink-stained quill tucked behind the ear (side / front)"""
    ht = L["head_top"] + bob
    if face == "down":
        s.set(15, ht + 4, "plaster_hi"); s.set(15, ht + 3, "white")
    elif face == "left":
        s.set(12, ht + 3, "white"); s.set(13, ht + 2, "plaster_hi")


NPCS = {
    "templekeeper": {
        "spec": H.human(dict(desc="", hair="stone_hi", hairstyle="bun", shirt="plaster_hi", collar="sky", skirt="cloth",
                             belt="shadow", shoes="timber", item="bluelantern"), keeper_extra),
        "anims": ("idle", "walk"), "kind": "human", "named": True,
        "desc": "Mother Ilse Brightwater, high priestess of the Old Temple (temple keeper): silver bun with a cold-fire "
                "hair gem, cream blouse with a sky collar and a pale-blue stole, dark belt, deep-blue skirt, brown shoes, "
                "carries the sacred cold-fire lantern",
        "light": {"color": H.ALLC["neon_blue"], "intensity": 0.9, "range": 2.2, "pool": "coldfire_pool_wide",
                  "note": "her lantern: like Sefa's (Stage 3) but softer; a light zone wraiths avoid"},
    },
    "archivist": {
        "spec": H.human(dict(desc="", hair="timber", hairstyle="messy", glasses=True, shirt="plaster", vest="timber",
                             belt="shadow", pants="stone_lo", shoes="timber_lo", item="book"), archivist_extra),
        "anims": ("idle", "walk"), "kind": "human", "named": True,
        "desc": "Brother Tamsin, young archivist of the Old Temple: messy brown hair, round spectacles, quill behind the "
                "ear, cream shirt under a brown vest, dark belt, grey trousers, brown shoes, an armful of records",
    },
}


# ============================================================== build
def main():
    rep = H.write_actors(OUT / "sprite", "old_temple_actors", NPCS)
    print("actors", H.report_line(rep))
    fxm = H.write_fx(OUT / "gamefx", "old_temple_fx", FX, CELL)
    print("fx", list(fxm["effects"]))
    kit_meta = {
        "riftgate_arch": {"pair": ["riftgate_glow_dormant", "riftgate_glow_lit"], "fx": {"dormant": "riftgate_seal_dormant", "lit": "riftgate_vortex_lit", "transition": "riftgate_awaken", "ground": "riftgate_ring_lit"},
                          "opening_m": [1.9, 3.1], "rift_marker": [0, KO.PLINTH, 0]},
        "riftgate_glow_lit": {"light": {"color": KO.NB, "range": 7.0, "fixed": 0.8}, "note": "place at the arch's pos/rot"},
        "riftgate_glow_dormant": {"light": {"color": KO.COLD_LO, "range": 2.5, "fixed": 0.12}, "note": "place at the arch's pos/rot"},
        "temple_brazier_cold": {"fx": ["temple_coldfire", "coldfire_pool_wide"], "light_zone_m": 2.4},
        "temple_brazier_out": {"note": "The Cold Altar: swap for temple_brazier_cold when relit"},
        "faceless_statue": {"fx_night": "faceless_gaze", "note": "rotate toward the Rift-gate at night (The Faceless Statues)"},
        "stained_window": {"fx_dusk": ["glasslight_violet", "glasslight_gold"]},
    }
    built, km = H.build_kit(OUT / "kit", KO.pieces, kit_meta)
    print("kit", {k: v["tris"] for k, v in km["pieces"].items()})
    renders(built, fxm)
    contact(built, fxm)
    H.finish_pack(OUT, README)


def comb(*ms):
    M = H.kit_module().Mesh()
    for m in ms:
        M.add(m)
    return M


NB = KO.NB


def gate_scene(built, fxm, state, mode="night", t=0):
    arch = built["riftgate_arch"].mesh
    glow = built["riftgate_glow_lit" if state == "lit" else "riftgate_glow_dormant"].mesh
    lights = ([((0, 1.9, 0.9), NB, 7.0, 1.5), ((-1.37, 0.9, 0.9), NB, 3.0, 1.0), ((1.37, 0.9, 0.9), NB, 3.0, 1.0)]
              if state == "lit" else [((0, 1.6, 0.8), KO.COLD_LO, 2.5, 0.35)])
    im, org, zb = H.render_mesh(comb(arch, glow), mode, lights if mode == "night" else (), pad=10, depth=True)
    W, Hh = im.width, im.height + 16
    can = Image.new("RGBA", (W, Hh), (0, 0, 0, 0))
    if state == "lit" and mode == "night":
        gp = H.project((0, 0.40, 1.3), org)
        can.alpha_composite(H.pool_layer((W, Hh), gp, 46, ("sky", "flower_blue", "cloth"), "gatepool"))
    can.alpha_composite(im)
    fxname = "riftgate_vortex_lit" if state == "lit" else "riftgate_seal_dormant"
    fr = H.fx_frame(OUT / "gamefx/old_temple_fx.png", fxm, fxname, t % fxm["effects"][fxname]["frames"])
    H.billboard_over(can, fr, (0, KO.PLINTH, 0.0), org, zb, (24, 47))
    return can, org


def renders(built, fxm):
    rd = OUT / "renders"; rd.mkdir(exist_ok=True)
    for state in ("dormant", "lit"):
        for mode in ("night", "day"):
            im, _ = gate_scene(built, fxm, state, mode)
            im.save(rd / f"riftgate_{state}_{mode}.png")
    for n, pc in built.items():
        if n.startswith("riftgate"):
            continue
        lights = {"temple_brazier_cold": [((0, 1.6, 0.4), NB, 4.5, 1.2)], "stained_window": [((0, 1.9, 0.8), KO.VIOLET, 3.0, 0.9)]}.get(n, [])
        im, _ = H.render_mesh(pc.mesh, "night", lights, pad=6)
        im.save(rd / f"{n}_night.png")


def contact(built, fxm):
    S = H.Sheet("Old Temple (Ravenhold, Midgard) - Rift-gate, temple props, temple keeper",
                "kit .glb previews at sprite density (18 px/m, locked 3/4 cam) + gamefx (48 px cells) + 20x32 NPCs; 4x nearest")
    fxpng = OUT / "gamefx/old_temple_fx.png"
    hero = H.SP.frame(H.PAL, "wildcaller", "down", "idle", 0).image()
    S.section("Rift-gate: dormant vs lit", "riftgate_arch + riftgate_glow_dormant / _lit + vortex billboard; hero for scale (5.4 m gate)")
    for state, mode, lab in (("dormant", "night", "DORMANT (night)"), ("lit", "night", "LIT - neon-blue cold fire (night)"), ("lit", "day", "LIT (day)")):
        im, org = gate_scene(built, fxm, state, mode, t=2)
        hx, hy = H.project((2.3, 0.0, 1.0), org)
        can = Image.new("RGBA", (im.width + 10, im.height), (0, 0, 0, 0))
        can.alpha_composite(im)
        can.alpha_composite(hero, (int(hx - 10), int(hy - 32)))
        S.cell(can, lab, "pillars + plinth block; opening 1.9 x 3.1 m", k=3)
    S.section("Gate fx (gamefx 48 px)", "every frame")
    for fx in ("riftgate_vortex_lit", "riftgate_seal_dormant", "riftgate_awaken", "riftgate_ring_lit"):
        e = fxm["effects"][fx]
        strip = Image.new("RGBA", (CELL * e["frames"], CELL), (12, 14, 26, 255))
        for i in range(e["frames"]):
            strip.alpha_composite(H.fx_frame(fxpng, fxm, fx, i), (i * CELL, 0))
        S.cell(strip, fx, f"{e['kind']} {e['frames']}f {e['fps']}fps" + (" once" if not e["loop"] else ""), k=2)
    S.section("Temple keeper + archivist (20x32, idle 0-3 | walk 0-3, 4 facings)", "clothing rule: separate top / bottom, dark waist band, contrasting shoes")
    meta = H.json.loads((OUT / "sprite/old_temple_actors.json").read_text())
    png = OUT / "sprite/old_temple_actors.png"
    for role in NPCS:
        row = Image.new("RGBA", (H.FW * 8 + 70, H.FH * 4 + 24), (0, 0, 0, 0))
        for fi, facing in enumerate(H.FACINGS):
            for c, (anim, i) in enumerate([("idle", k) for k in range(4)] + [("walk", k) for k in range(4)]):
                fr = H.frame_of(png, meta, role, facing, anim, i)
                lit = H.lit_sprite(fr, ("sky", "flower_blue", "cloth") if role == "templekeeper" else None, 13, pad=(3, 3))
                row.alpha_composite(lit, (c * (H.FW + 8), fi * (H.FH + 6)))
        S.cell(row, role, NPCS[role]["desc"][:92], k=3)
    S.section("Temple props (night)", "sacred brazier lit / out, faceless angel statue (+ gaze fx), stained-glass window (+ floor light), broken column")
    for n in ("temple_brazier_cold", "temple_brazier_out", "faceless_statue", "stained_window", "temple_column"):
        lights = {"temple_brazier_cold": [((0, 1.6, 0.4), NB, 4.5, 1.2)], "stained_window": [((0, 1.9, 0.8), KO.VIOLET, 3.0, 0.9)]}.get(n, [])
        im, org = H.render_mesh(built[n].mesh, "night", lights, pad=14)
        can = Image.new("RGBA", (im.width + 20, im.height + 20), (0, 0, 0, 0))
        if n == "temple_brazier_cold":
            can.alpha_composite(H.pool_layer(can.size, H.project((0, 0, 0.2), org), 30, ("sky", "flower_blue", "cloth"), "bpool"))
        if n == "stained_window":
            g = H.fx_frame(fxpng, fxm, "glasslight_violet", 0)
            p = H.project((0, 0, 1.0), org)
            can.alpha_composite(g, (int(p[0] - 24), int(p[1] - 30)))
        can.alpha_composite(im)
        if n == "temple_brazier_cold":
            fl = H.fx_frame(fxpng, fxm, "temple_coldfire", 1)
            p = H.project((0, 1.1, 0), org)
            can.alpha_composite(fl, (int(p[0] - 24), int(p[1] - 47)))
        if n == "faceless_statue":
            g = H.fx_frame(fxpng, fxm, "faceless_gaze", 2)
            p = H.project((0, 2.05, 0.2), org)
            can.alpha_composite(g, (int(p[0] - 24), int(p[1] - 47)))
        S.cell(can, n, "", k=3)
    S.section("Light / floor fx", "")
    for fx in ("temple_coldfire", "coldfire_pool_wide", "glasslight_violet", "glasslight_gold", "faceless_gaze"):
        e = fxm["effects"][fx]
        strip = Image.new("RGBA", (CELL * e["frames"], CELL), (12, 14, 26, 255))
        for i in range(e["frames"]):
            strip.alpha_composite(H.fx_frame(fxpng, fxm, fx, i), (i * CELL, 0))
        S.cell(strip, fx, f"{e['kind']} {e['frames']}f {e['fps']}fps", k=2)
    S.render(OUT / "contact_sheet.png")


README = """# Old Temple pack (Ravenhold, Midgard): the Rift-gate, temple props, temple keeper

Art seat staging pack for **Hearthmoor** (Bill's HD-2D game). Generated procedurally by `src/gen_old_temple.py`
(Python + Pillow + numpy, importing the repo's own `tools/sprite`, `tools/kit`, `tools/check-sprite` read-only).
Matches DESIGN_EXPANSION E6.3: white temple stone gone grey, faceless angel statues, **blue cold-fire braziers**,
stained glass throwing violet and gold at dusk, the **Rift-gate** in the inner court (quests *The Cold Altar*,
*The Faceless Statues*, *Keeper of the Gate*).

![contact sheet](contact_sheet.png)

## What's here

| part | files | format (drop-in) |
|---|---|---|
| NPCs | `sprite/old_temple_actors.png/.json`, `sprite/strips/<role>.png` | exact `hd2d sprite` atlas: 20x32, pivot [10,32], rows down/up/left/right, idle 0-3 (3 fps, loop 0,1,2,1) / walk 4-7 (8 fps). **check-sprite: PASS** |
| gamefx | `gamefx/old_temple_fx.png/.json`, `gamefx/strips/*.png` | exact `hd2d portal` gamefx JSON (48 px cells, row per effect, fps / loop / kind / pivot / lift / glow / light) |
| kit | `kit/*.glb`, `kit/kit.json` + `src/kit_old_temple.py` | built with the repo's kit.py / meshlib (`pieces(K)` module like kit_harbor.py); markers, blockers, sizes in kit.json |
| previews | `renders/*.png` | 1x renders at sprite density (18 px/m), night + day |

### NPCs (`named` roles, so they only build when a spec names them)
- `templekeeper`: **Mother Ilse Brightwater**, high priestess / temple keeper. Silver bun with a cold-fire hair gem,
  cream blouse with a sky collar and pale-blue stole, **dark belt**, deep-blue skirt, brown shoes, carries the sacred
  cold-fire lantern (`bluelantern`). Light: neon blue `#2ab4ff`, intensity 0.9, range 2.2 m, pool `coldfire_pool_wide`
  (a light zone, like Sefa's lantern but softer).
- `archivist` (bonus): **Brother Tamsin**: messy brown hair, spectacles, quill, cream shirt + brown vest, dark belt, grey
  trousers, brown shoes, records under the arm.
- Clothing rule: separate top and bottom in different values, a 1 px darker waist band, leg split / skirt, shoes in
  their own colour. Biome palette only (cozy-village), <= 20 colours, 1 px ink outline, hard alpha.

### The Rift-gate (two states)
Place `riftgate_arch` and ONE glow piece at the same pos / rot (the realm_arch + realm_glow pattern from Bifrost):

| state | kit glow piece | billboard (at `markers.rift` = [0, 0.40, 0]) | light |
|---|---|---|---|
| dormant (Act 1 until *Keeper of the Gate*) | `riftgate_glow_dormant`: cooled stone runes, 4 faint cold embers | `riftgate_seal_dormant` (6f, 3 fps): slate-blue sleeping swirl + a lantern-shaped lock rune (Grandpa Alder's lantern charm) with a slow heartbeat | `#2a6cb0`, fixed 0.12, range 2.5 |
| transition | - | `riftgate_awaken` (8f, 10 fps, once): lock flares, rings race out, spiral spins up | `#a6ecff` flash curve, range 9 |
| lit | `riftgate_glow_lit`: neon-blue cold-fire rune rim, pillar runes, keystone crystal, plinth sigil, two cold-fire tongues | `riftgate_vortex_lit` (8f, 8 fps): neon-blue cold-fire spiral, burning rim, the 7 Rainbow-Rift glints orbiting | `#2ab4ff`, fixed 0.8, range 7 (3 lamp markers) |

Plus `riftgate_ring_lit` (decal, 8f): cold-fire pool + turning rune ring on the plinth in front of the lit gate.
Gate: 5.2 x 5.41 x 2.4 m, plinth top y 0.40, opening 1.9 x 3.1 m (a 48 px billboard = 2.67 m fits); blockers on the two
pillars only, so you walk through. Hero for scale on the sheet.

### Props (kit)
`temple_brazier_cold` (lamp `#2ab4ff`, range 5.5; add `temple_coldfire` billboard at y 1.10 + `coldfire_pool_wide`
decal; light zone ~2.4 m), `temple_brazier_out` (*The Cold Altar* state: ash + one ember), `faceless_statue` (2.65 m,
smooth faceless mask with a gold brow rim, folded wings; night fx `faceless_gaze` at lift 2.05; rotate toward the gate at
night for *The Faceless Statues*), `stained_window` (violet / gold / blue self-lit glass, violet lamp 0.35; dusk floor
decals `glasslight_violet` / `glasslight_gold` 1.8 m in front), `temple_column` (broken, mossy).

### Glow rules kept
Glow is emissive pixels + small lights + dithered pools only (no bloom). Off-palette colours appear only on glow
pixels: NEON blue `#2ab4ff/#a6ecff/#1c62d8`, cold fire `#5ab4f0/#d8f4ff/#2a6cb0`, violet `#a45cf0/#d4a8ff/#6a34b8`
(the same hexes as tools/portal + kit_bifrost). Sprites are biome-palette only.

**Neon flag (2026-10-05):** NPC sprites (`templekeeper`, `archivist`) use **no** neon pixels (biome palette, check-sprite PASS). Neon appears only in `gamefx/old_temple_fx.png` (all effects) and on the kit `glow` material of `riftgate_glow_lit`, `riftgate_glow_dormant`, `temple_brazier_cold`, `stained_window`.

## Drop-in steps (for the lead)
1. NPCs: either copy the role specs from `NPCS` in `src/gen_old_temple.py` into `tools/sprite/roles_more.py` (they use
   only existing spec keys; the stole / hair gem / quill are the small `*_extra` hooks), or paste the atlas rows.
2. gamefx: append the effect functions to `tools/portal/portal.py` (`EFFECTS` entries: same fps / kind / pivot / lift
   as `gamefx/old_temple_fx.json`), or merge rows into an area's gamefx atlas (cell 48 matches).
3. kit: copy `src/kit_old_temple.py` into `tools/kit/` and add the two-line import at the bottom of kit.py (see the
   module docstring). Area spec props: `{"piece": "riftgate_arch", ...}` + `{"piece": "riftgate_glow_lit", ...}` at
   the same pos, and a `glow` light per the table.
4. Regenerate: `python3 src/gen_old_temple.py` (needs /workspace/hd2d-suite; writes only into this folder).
"""


if __name__ == "__main__":
    main()
