"""[ALFHEIM] Recolour the staging Lumi art: cold-fire core -> neon blue (spells.py NEON blue), halo stays neon violet.
Exact-hex swap on hard-alpha PNGs, so it is idempotent and re-runnable when the Art seat re-delivers lumi/.
usage: python3 tools/sprite/lumi_recolor.py games/hearthmoor/art/alfheim/lumi"""
import sys, pathlib
from PIL import Image
MAP = {  # core body / highlight / shade  ->  neon_blue / _hi / _lo
    (0x5a, 0xb4, 0xf0): (0x2a, 0xb4, 0xff),
    (0xd8, 0xf4, 0xff): (0xa6, 0xec, 0xff),
    (0x2a, 0x6c, 0xb0): (0x1c, 0x62, 0xd8),
    # halo: neon_violet / _hi / _lo (already; listed so a safe-palette re-delivery still lands violet)
    (0xa4, 0x5c, 0xf0): (0xa4, 0x5c, 0xf0), (0xd4, 0xa8, 0xff): (0xd4, 0xa8, 0xff), (0x6a, 0x34, 0xb8): (0x6a, 0x34, 0xb8),
}
root = pathlib.Path(sys.argv[1])
for p in sorted(root.rglob("*.png")):
    if "safe" in p.name or p.name == "contact_sheet.png":
        continue
    im = Image.open(p).convert("RGBA"); px = im.load(); n = 0
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a and (r, g, b) in MAP and MAP[(r, g, b)] != (r, g, b):
                px[x, y] = MAP[(r, g, b)] + (a,); n += 1
    if n: im.save(p); print(f"{p.relative_to(root)}: {n} px")
