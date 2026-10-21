"""decal_over copied from alfheim/src/gen_alfheim.py"""
import math
import hmart as H


def decal_over(can, fr, center, org, zb, lift=0.02):
    """paste a pre-squashed decal frame centred on world `center` (ground plane y=lift), per-pixel depth tested"""
    ce, se = math.cos(H.ELEV), math.sin(H.ELEV)
    px_, py_ = H.project((center[0], lift, center[2]), org)
    src, dst = fr.load(), can.load()
    n = fr.width
    for y in range(n):
        for x in range(n):
            if src[x, y][3] == 0:
                continue
            cx_, cy_ = int(round(px_ - n / 2 + x)), int(round(py_ - n / 2 + y))
            if not (0 <= cx_ < can.width and 0 <= cy_ < can.height):
                continue
            dz = (y - n / 2) / (se * H.PX_PER_M)
            dep = (center[2] + dz) * ce + lift * se
            if 0 <= cy_ < zb.shape[0] and 0 <= cx_ < zb.shape[1] and zb[cy_, cx_] > dep + 0.08:
                continue
            dst[cx_, cy_] = src[x, y]


