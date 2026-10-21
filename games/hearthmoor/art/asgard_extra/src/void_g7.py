"""G7 Rune Bridge void look (Art seat 2026-10-20): kit pieces + fx + a scene render. Dark violet void with glow, mid-dark shadows (no near-black).
Kit: void_floor (2 m tile laid 2.4 m below the floor: deep violet with sparse glow flecks), void_rim (marble lip with a violet glow strip, edges of the drop),
void_shard (floating broken marble chunk with violet rune glow). Fx: void_motes (rising violet / pale motes), void_pool (violet glow decal), void_shade (mid-dark #4a3a66 edge shade).
Neon: only the kit 'glow' material (#a45cf0 / #d4a8ff) and fx; no sprites."""
import json, math, os, sys, random
from pathlib import Path
import as_common as C, as_fx as X, kit_as as KA, as_layouts as LY, as_scene as SC
H = C.H
OUT = Path(__file__).resolve().parent.parent
PI = math.pi
VD, VD2, VIO, VIO_HI, VRIM = "#2e2450", "#3a2e62", "#a45cf0", "#d4a8ff", "#5a4a86"


def void_pieces(K):
    box, cylinder, sphere, mix, Piece, Mesh = K.box, K.cylinder, K.sphere, K.mix, K.Piece, K.Mesh
    def lamp(pc, pos, col, rng_):
        pc.markers["lamps"].append(list(pos)); pc.markers["lamp_color"] = col; pc.markers["lamp_range"] = rng_; pc.markers["lamp_fixed"] = 0.0

    def void_floor(cx):
        r = K.rng(cx.seed, "vf"); m = Mesh(); pc = Piece("void_floor")
        m.add(box(2.0, 0.02, 2.0, VD, "paint", y0=-2.4))
        for _ in range(5):
            x, z = r.uniform(-.9, .9), r.uniform(-.9, .9)
            m.add(box(0.06, 0.01, 0.06, VIO if r.random() < .7 else VIO_HI, "glow", y0=-2.37).xf((x, 0, z)))
        for _ in range(3):
            x, z = r.uniform(-.8, .8), r.uniform(-.8, .8)
            m.add(box(0.5, 0.01, 0.3, VD2, "paint", y0=-2.38).xf((x, 0, z)))
        pc.mesh = m; pc.size = [2, 0.05, 2]
        pc.markers["note"] = "G7 void: lay where the floor is missing (2.4 m below walk level); no collision walk; fall = respawn at last lit rune"
        return pc

    def void_rim(cx):
        pc = Piece("void_rim"); m = Mesh()
        m.add(box(2.0, 2.4, 0.4, "#6e6690", "stone", y0=-2.4)); m.add(box(2.0, 0.1, 0.45, "#d8d4e6", "paint", y0=-0.1))
        m.add(box(2.0, 0.06, 0.02, VIO, "glow", y0=-0.4).xf((0, 0, 0.21)))
        pc.mesh = m.ao(-2.4, 2.6, 0.15); pc.size = [2.0, 2.5, 0.45]; lamp(pc, (0, -0.6, 0.5), VIO, 3.0)
        pc.markers["note"] = "void edge wall (face +z into the void); rot pi / +-pi/2 for the other sides; keep fx and spawns 1 m back from the lip"
        pc.markers["no_props_within_m"] = 1.0
        return pc

    def void_shard(cx):
        pc = Piece("void_shard"); m = Mesh()
        m.add(box(0.9, 0.5, 0.7, "#9a90b8", "stone", y0=0).xf((0, 0, 0), rot=(0.3, 0.5, 0.2)))
        m.add(sphere(0.12, 6, 4, VIO_HI, "glow").xf((0, 0.3, 0.3)))
        pc.mesh = m; pc.size = [1.0, 0.8, 0.8]; lamp(pc, (0, 0.3, 0.4), VIO, 2.5)
        pc.markers["note"] = "floating marble shard in the void (y -1.4 .. -0.6); decorative, no collision; >= 1.5 m from the bridge"
        return pc
    return {f.__name__: f for f in (void_floor, void_rim, void_shard)}


def all_pieces(K):
    d = KA.pieces(K); d.update(void_pieces(K)); return d


def motes():
    r = random.Random(17); ms = [(r.uniform(4, 44), r.uniform(0, 48), r.random()) for _ in range(10)]
    out = []
    for k in range(8):
        F = H.Fx(48)
        for (x, y, ph) in ms:
            yy = (y - k * 2) % 48
            F.set(x + math.sin(k * .8 + ph * 6) * 1.2, yy, "white" if ph > .8 else X.NV[0] if ph > .4 else X.NV[1])
        out.append(F)
    return out


def shade():
    F = H.Fx(48)
    for y in range(48):
        for x in range(48):
            d = math.hypot((x - 23.5) / 22, (y - 23.5) / 22)
            if d < .6:
                F.set(x, y, "ax_void")
            elif d < .9 and (x + y) % 2 == 0:
                F.set(x, y, "ax_void_hi")
    return [F] * 4


H.ALLC.update({"ax_void": "#4a3a66", "ax_void_hi": "#5e4c80"})
X.add("void_motes", motes, 6, "billboard", -1.0, [24, 47], "G7: violet + pale motes rising out of the void (place at void floor level, y -2.4 .. -1)")
X.add("void_pool", lambda: H.neon_pool_frames("violet", 48, 6, rmax=22), 4, "decal", -2.35, [24, 24], "G7: violet glow pool on the void floor (lift -2.35)")
X.add("void_shade", shade, 1, "decal", -2.36, [24, 24], "G7: MID-DARK void shade #4a3a66 / #5e4c80 (no near-black), breaks up the void floor")


def g7():
    S = LY.reliquary_g7()
    P = S["pieces"]
    P += [("void_floor", (x, 0, z)) for x in (-2.0, 0.0, 2.0) for z in (-6.0, -4.0, -2.0, 0.0, 2.0)]
    P += [("void_rim", (0 + dx, 0, 3.1), 0.0) for dx in (-2.0, 0.0, 2.0)]
    P += [("void_shard", (-1.6, -1.2, -4.6)), ("void_shard", (1.5, -0.8, -1.0)), ("void_shard", (-1.4, -1.5, 1.4))]
    S["decals"] = [d for d in S["decals"] if d[0] not in ("pool_gold",) or abs(d[1][0]) > 2.2]
    S["decals"] += [("void_pool", (x, z), (i * 2) % 6, 2, -2.35) for i, (x, z) in enumerate(((-1.0, -5.0), (1.0, -2.6), (-1.0, 0.0), (1.0, 1.8)))]
    S["decals"] += [("void_shade", (x, z), 0, 1, -2.36) for (x, z) in ((1.2, -4.0), (-1.2, -1.6), (0.8, 0.6))]
    S["bills"] += [("void_motes", (x, -2.3, z), i) for i, (x, z) in enumerate(((-1.0, -4.0), (1.0, -1.0), (0.0, 1.6)))]
    S["extra_lights"] += [((x, -1.6, z), "#a45cf0", 4.5, 0.9) for (x, z) in ((-1.0, -5.0), (1.0, -2.6), (-1.0, 0.0), (1.0, 1.8))]
    S["actors"] = [("ax_centaur", "storm_centaur", "left", "idle", 1, (4.2, 0, -2.4))] + \
                  [(a[0], a[1], a[2], a[3], a[4], a[5], "../asgard/sprite") if a[0] == "as_sigrun" else a for a in S["actors"] if a[0] != "as_enemies"]
    S["bg"] = {"night": (22, 16, 38)}; S["name"] = "reliquary_g7_void"
    return S


def main():
    import gen_asgard as GA
    fxm = H.write_fx(OUT / "gamefx", "as_fx", X.FX, 48)
    void_meta = {"void_floor": {"fx": ["void_pool", "void_shade", "void_motes"]}, "void_rim": {"fx": ["void_pool"]}, "void_shard": {"fx": ["void_motes"]}}
    H.build_kit(OUT / "kit", void_pieces, void_meta)
    built, _ = H.build_kit(Path("/tmp/ax_allkit"), all_pieces, None)
    rd = OUT / "renders"; rd.mkdir(exist_ok=True)
    for n in ("void_floor", "void_rim", "void_shard"):
        H.render_mesh(built[n].mesh, "night", SC.lights_of(built[n]), pad=6, ambient=SC.NIGHT_AMB)[0].save(rd / f"{n}_night.png")
    GA.OUT = OUT; GA.patch_frames()
    S = g7(); S["fxm"] = fxm
    im = SC.compose(built, S, "night"); im.save(rd / "scene_reliquary_g7_void_night.png")
    l = round(SC.luma(im), 1)
    (rd / "luma.json").write_text(json.dumps({"reliquary_g7_void_night": l}, indent=1))
    print("luma", l)


if __name__ == "__main__":
    main()
