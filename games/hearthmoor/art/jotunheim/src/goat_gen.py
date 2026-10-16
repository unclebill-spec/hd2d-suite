"""Stonehollow's goats on the pets/ frame layout (20x32, pivot [10,32], rows down/up/left/right, idle 0-3, walk 4-7): 'goat' (cream / grey
pen goat) and 'clatter' (Brynja's young brown goat with a gold bell; the one who chooses you in jt_goat). Palette-only, no glow.
Uses staging pets_gen.py's Spr (grid + outline + mirror) unchanged. Writes ../sprite/jt_goats.png + jt_goats.json.
Rebuild: python3 goat_gen.py (Pillow)."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "staging" / "hearthmoor" / "art" / "pets"))
import pets_gen as P  # noqa

OUT = HERE.parent / "sprite"
ANIMS = {"idle": {"start": 0, "count": 4, "fps": 3, "loop": [0, 1, 2, 1], "blink": 3}, "walk": {"start": 4, "count": 4, "fps": 8}}
COLS = 8
LOOKS = {
    "goat": dict(hi="plaster_hi", mid="plaster", lo="stone_hi", dk="stone", horn="stone", hornhi="plaster_lo", beard="white", hoof="stone_lo", bell=None,
                 desc="a Stonehollow pen goat: cream coat, grey shading, swept-back horns, a small white beard (goat-size; the giants' goats are not tiny, but they are goats)"),
    "clatter": dict(hi="timber_hi", mid="timber", lo="timber_lo", dk="timber_lo", horn="plaster_lo", hornhi="plaster", beard="plaster_hi", hoof="ink", bell="flower_gold",
                    desc="Clatter, Brynja's young brown goat: a white blaze, short horns and a gold bell that clatters; the goat who chooses you (the mount comes later)"),
}


def draw(look):
    L = LOOKS[look]
    coat = lambda X, Y, d, u, v: L["hi"] if v < -0.4 else L["lo"] if (v > 0.55 or d > 0.8) else L["mid"]

    def goat(s, face, anim, i):
        walk = anim == "walk"
        bob = [0, -1, 0, -1][i] if walk else [0, 0, 1, 0][i]
        leg = [(0, 1), (0, 0), (1, 0), (0, 0)][i] if walk else (0, 0)
        blink = anim == "idle" and i == 3
        if face == "left":
            for k, (lx, ph) in enumerate(((7.6, leg[0]), (9.2, leg[1]), (12.4, leg[1]), (14.0, leg[0]))):      # front pair, hind pair
                far = k in (1, 2)
                for yy in range(26 + bob, 31 - (1 if ph else 0)):
                    s.set(lx + (ph and k < 2) * -0.0, yy, L["dk"] if far else L["lo"])
                s.set(lx, 30 - (1 if ph else 0), L["hoof"])
            s.ell(11.0, 23.6 + bob, 5.4, 3.1, coat)
            s.set(16, 22 + bob, L["mid"]); s.set(16, 21 + bob, L["hi"]); s.set(17, 21 + bob, L["hi"])                  # tail
            hx, hy = 5.6, 20.0 + bob + (1 if anim == "idle" and i == 2 else 0)
            s.ell(7.2, 21.6 + bob, 2.0, 2.4, coat)                                                                       # neck
            s.ell(hx, hy, 2.5, 2.2, lambda X, Y, d, u, v: L["hi"] if v < 0 else L["mid"])                                # head
            s.set(hx - 3, hy + 0.6, L["lo"]); s.set(hx - 3, hy + 1.4, L["dk"])                                           # muzzle
            if look == "clatter":
                s.set(hx - 1.6, hy - 1, "white"); s.set(hx - 2, hy, "white")                                             # blaze
            s.set(hx - 0.8, hy - 0.4, "ink" if not blink else L["lo"])
            s.set(hx + 1.6, hy - 1.2, L["mid"]); s.set(hx + 2.6, hy - 0.4, L["lo"])                                      # ear
            for k, (dx, dy) in enumerate(((1.0, -2.6), (1.6, -3.6), (2.6, -4.2), (3.6, -4.2)) if look == "goat" else ((1.0, -2.6), (1.7, -3.4))):
                s.set(hx + dx, hy + dy, L["horn"]); s.set(hx + dx + 1, hy + dy, L["hornhi"]) if k < 2 else None
            s.set(hx - 2.2, hy + 3, L["beard"]); s.set(hx - 2.2, hy + 4, L["beard"]); s.set(hx - 1.6, hy + 3.4, L["beard"])
            if L["bell"]:
                s.set(hx + 0.6, hy + 3.4, L["bell"]); s.set(hx + 0.6, hy + 4.4, L["bell"]); s.set(hx + 1.4, hy + 4.4, "flower_gold")
        else:
            back = face == "up"
            for sd in (-1, 1):
                ph = leg[0] if sd < 0 else leg[1]
                for yy in range(26 + bob, 31 - ph):
                    s.set(10 + sd * 2.4, yy, L["lo"]); s.set(10 + sd * 2.4 + 1, yy, L["dk"])
                s.set(10 + sd * 2.4, 30 - ph, L["hoof"]); s.set(10 + sd * 2.4 + 1, 30 - ph, L["hoof"])
            s.ell(10, 24 + bob, 4.0, 4.4, coat)
            if back:
                s.set(10, 20 + bob, L["hi"]); s.set(10, 21 + bob, L["mid"]); s.ell(10, 19.5 + bob, 2.6, 2.4, coat)    # rump, head over the back
                s.set(10, 27 + bob, L["hi"]); s.set(11, 27 + bob, L["mid"])                                               # tail
            else:
                hx, hy = 10, 19.4 + bob + (1 if anim == "idle" and i == 2 else 0)
                s.ell(hx, hy + 1.0, 2.4, 3.0, coat)
                s.ell(hx, hy, 2.7, 2.4, lambda X, Y, d, u, v: L["hi"] if v < 0 else L["mid"])
                for sd in (-1, 1):
                    s.set(hx + sd * 1.3, hy - 0.4, "ink" if not blink else L["lo"])
                    s.set(hx + sd * 2.9, hy - 0.6, L["mid"])                                                              # ears
                    for k in range(3 if look == "goat" else 2):
                        s.set(hx + sd * (1.5 + k * 0.9), hy - 2.6 - k * 0.9 + (0.0), L["horn"])
                        s.set(hx + sd * (1.5 + k * 0.9), hy - 1.8 - k * 0.9, L["hornhi"]) if k else None
                s.set(hx, hy + 1.6, L["lo"]); s.set(hx, hy + 2.6, L["beard"]); s.set(hx - 0.0, hy + 3.6, L["beard"])
                if look == "clatter":
                    s.set(hx, hy - 1.6, "white"); s.set(hx, hy - 0.6, "white")
                    s.set(hx, hy + 4.6, "flower_gold"); s.set(hx + 1, hy + 4.6, "flower_gold")
    return goat


def build():
    rows = list(LOOKS)
    im = P.Image.new("RGBA", (P.FW * COLS, P.FH * 4 * len(rows)), (0, 0, 0, 0))
    roles = {}
    for pi, name in enumerate(rows):
        fn = draw(name); frames = []
        for fi, facing in enumerate(P.FACINGS):
            for anim in ANIMS:
                for i in range(4):
                    s = P.Spr({}); face = "left" if facing == "right" else facing
                    fn(s, face, anim, i); s.outline()
                    if facing == "right": s.mirror()
                    col = ANIMS[anim]["start"] + i; x, y = col * P.FW, (pi * 4 + fi) * P.FH
                    im.paste(s.image(), (x, y))
                    frames.append({"name": f"{name}_{facing}_{anim}{i}", "facing": facing, "anim": anim, "i": i, "x": x, "y": y, "w": P.FW, "h": P.FH, "pivot": [x + P.PIVOT[0], y + P.PIVOT[1]]})
        roles[name] = {"row": pi * 4, "kind": "creature", "desc": LOOKS[name]["desc"], "size_bounds": [[8, 20], [8, 28]], "caster": False, "anims": list(ANIMS), "frames": frames}
    return im, roles


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    im, roles = build(); im.save(OUT / "jt_goats.png")
    meta = {"tool": "hearthmoor-art goat_gen (pets_gen layout)", "biome": "cozy-village", "frame": [P.FW, P.FH], "pivot": P.PIVOT, "ground_row": P.GROUND,
            "facings": list(P.FACINGS), "anims": ANIMS, "cols": COLS, "image": "jt_goats.png", "size": [im.width, im.height], "roles": roles}
    (OUT / "jt_goats.json").write_text(json.dumps(meta, indent=1))
    big = im.resize((im.width * 4, im.height * 4), P.Image.NEAREST); bg = P.Image.new("RGBA", big.size, (60, 80, 110, 255)); bg.alpha_composite(big); bg.save("/workspace/alf_qa/jot/goat/preview.png")


if __name__ == "__main__":
    main()
