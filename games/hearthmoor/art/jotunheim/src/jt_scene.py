"""Scene composer for the Jotunheim renders: kit pieces (with real height) + actors + gamefx decals/billboards -> night / day PNG."""
import json, math
from pathlib import Path
from PIL import Image
import numpy as np
import jt_common as C
import decal as D
H = C.H
OUT = Path(__file__).resolve().parent.parent
NIGHT_AMB = (0.27, 0.28, 0.33)      # not the all-blue hmart default (0.20,0.23,0.40): lifted + less saturated, pools do the colour
DAY_AMB = (0.80, 0.79, 0.79)


def lights_of(pc, pos=(0, 0, 0)):
    lc = pc.markers.get("lamp_color")
    return [((pos[0] + lp[0], pos[1] + lp[1], pos[2] + lp[2]), lc, pc.markers["lamp_range"], 1.0) for lp in pc.markers.get("lamps", [])] if lc else []


def fxf(fxm, n, i=0):
    return H.fx_frame(OUT / "gamefx/jt_fx.png", fxm, n, i)


def frame(sheet, role, facing, anim, i, folder="sprite"):
    m = json.loads((OUT / folder / f"{sheet}.json").read_text())
    im = H.frame_of(OUT / folder / f"{sheet}.png", m, role, facing, anim, i)
    fw, fh = m["frame"]
    return im, (fw // 2, fh - 1)


def billboard_tall(can, fr, anchor, org, zb, pv):
    """like hmart.billboard_over, but the depth of each billboard pixel grows with its height above the feet (a tall upright sprite is not a flat card)"""
    ce, se = math.cos(H.ELEV), math.sin(H.ELEV)
    px_, py_ = H.project(anchor, org)
    X0, Y0 = int(round(px_ - pv[0])), int(round(py_ - pv[1]))
    src, dst = fr.load(), can.load()
    for y in range(fr.height):
        h = max(0.0, (pv[1] - y) / (H.PX_PER_M * ce))
        bd = anchor[2] * ce + (anchor[1] + h) * se
        for x in range(fr.width):
            if src[x, y][3] == 0:
                continue
            cx_, cy_ = X0 + x, Y0 + y
            if 0 <= cx_ < can.width and 0 <= cy_ < can.height and not (0 <= cy_ < zb.shape[0] and 0 <= cx_ < zb.shape[1] and zb[cy_, cx_] > bd + 0.02):
                dst[cx_, cy_] = src[x, y]


def luma(im, mask_bg=None):
    a = np.asarray(im.convert("RGB"), float)
    y = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
    return float(y.mean() / 255 * 100)


def compose(built, S, mode):
    """S = dict(pieces=[(name,(x,y,z),rot?)], actors=[(sheet,role,facing,anim,i,(x,y,z))], decals=[(fx,(x,z),frame,scale)], bills=[(fx,(x,y,z),frame)],
    extra_lights=[((x,y,z),col,range,intensity)], bg=(r,g,b))"""
    K = H.kit_module(); M = K.Mesh(); lights = []
    for p in S["pieces"]:
        n, pos = p[0], p[1]
        rot = p[2] if len(p) > 2 else 0.0
        pc = built[n]
        mesh = pc.mesh.xf((0, 0, 0), rot=(0, rot, 0)).xf(pos) if rot else pc.mesh.xf(pos)
        M.add(mesh)
        if mode == "night":
            lights.extend(lights_of(pc, pos))
    if mode == "night":
        ls = S.get("lscale", 1.0)
        lights.extend([(a, b, c, d * ls) for (a, b, c, d) in S.get("extra_lights", [])])
    if S.get("reach"):
        M.quad((-0.02, S["reach"], -4.6), (0.02, S["reach"], -4.6), (0.02, S["reach"] + .05, -4.6), (-0.02, S["reach"] + .05, -4.6), "#000000", mat="glow")
    amb = S.get("amb", {}).get(mode) or (NIGHT_AMB if mode == "night" else DAY_AMB)
    im, org, zb = H.render_mesh(M, mode, lights, pad=14, depth=True, ambient=amb)
    bg = S["bg"][mode]
    can = Image.new("RGBA", im.size, bg + (255,)); can.alpha_composite(im)
    fxm = S["fxm"]
    if mode == "night":
        for (n, (x, z), i, sc, *lift) in S.get("decals", []):
            fr = fxf(fxm, n, i)
            if sc != 1:
                fr = fr.resize((fr.width * sc, fr.height * sc), Image.NEAREST)
            D.decal_over(can, fr, (x, 0, z), org, zb, (lift[0] if lift else 0.02))
    items = []
    for a in S.get("actors", []):
        sheet, role, facing, anim, i, pos = a[:6]
        folder = a[6] if len(a) > 6 else "sprite"
        fr, pv = frame(sheet, role, facing, anim, i, folder)
        items.append((fr, pos, pv))
    if mode == "night":
        for (n, pos, i) in S.get("bills", []):
            items.append((fxf(fxm, n, i), pos, tuple(fxm["effects"][n]["pivot"])))
    for (fr, a, pv) in sorted(items, key=lambda r: r[1][2]):
        (billboard_tall if fr.height > 40 else H.billboard_over)(can, fr, a, org, zb, pv)
    return can
