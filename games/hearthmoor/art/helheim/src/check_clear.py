"""clearance check: props / actors / fx >= 1 m from every ledge edge, nothing on a stair footprint + 1 m (ledge 3.1 x 2.1, stair 2.6 x 3.5)."""
import math, hh_layouts as LY
SKIP = {"mist_ledge", "mist_stair", "gloam_floor", "ossuary_floor", "pebble_shore", "black_lake", "ossuary_wall"}


def rects(S):
    L, St = [], []
    for p in S["pieces"]:
        n, (x, y, z) = p[0], p[1]
        if n == "mist_ledge":
            L.append((x - 1.55, z - 1.05, x + 1.55, z + 1.05))
        if n == "mist_stair":
            St.append((x - 1.3, z - 1.75, x + 1.3, z + 1.75))
    return L, St


def dist(r, x, z):
    dx = max(r[0] - x, 0, x - r[2]); dz = max(r[1] - z, 0, z - r[3]); return math.hypot(dx, dz)


def check(S):
    L, St = rects(S); bad = []
    items = [(p[0], p[1][0], p[1][2]) for p in S["pieces"] if p[0] not in SKIP]
    items += [(a[1], a[5][0], a[5][2]) for a in S["actors"]] + [(d[0], d[1][0], d[1][1]) for d in S["decals"]] + [(b[0], b[1][0], b[1][2]) for b in S["bills"]]
    for n, x, z in items:
        for r in L:
            if dist(r, x, z) < 1.0:
                bad.append((n, x, z, "ledge %.2f" % dist(r, x, z)))
        for r in St:
            if dist(r, x, z) < 1.0:
                bad.append((n, x, z, "stair %.2f" % dist(r, x, z)))
    return bad


if __name__ == "__main__":
    tot = 0
    for k, f, m in LY.SCENES:
        b = check(f()); tot += len(b)
        for x in b:
            print(k, x)
    print("violations", tot)
