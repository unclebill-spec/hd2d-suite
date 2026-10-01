"""Pixel writer.

Earmarked for Gravewake and for later games.
It draws real pixels: one color per pixel, no blending, no anti-alias, no new hues
beyond the colors you pass in. A tile is 16×16 unless you ask for another size.

Use it when a zone needs ground and a downloaded sheet does not fit.
Do not scale a photo down and call it a tile. Draw the pixels.
"""

from __future__ import annotations

import random
from PIL import Image


def _rgba(hex_color: str) -> tuple[int, int, int, int]:
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


class Tile:
    """One tile. Empty pixels stay transparent."""

    def __init__(self, n: int = 16):
        self.n = n
        self.p: list[list[str | None]] = [[None] * n for _ in range(n)]

    def set(self, x: int, y: int, color: str | None) -> None:
        if color and 0 <= x < self.n and 0 <= y < self.n:
            self.p[y][x] = color

    def rect(self, x: int, y: int, w: int, h: int, color: str) -> None:
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def fill(self, color: str) -> None:
        self.rect(0, 0, self.n, self.n, color)

    def image(self) -> Image.Image:
        im = Image.new("RGBA", (self.n, self.n), (0, 0, 0, 0))
        px = im.load()
        for y in range(self.n):
            for x in range(self.n):
                c = self.p[y][x]
                if c:
                    px[x, y] = _rgba(c)
        return im


def strip(tiles: list[Tile]) -> Image.Image:
    """Lay tiles in a row. The game reads them as columns of 16."""
    n = tiles[0].n
    out = Image.new("RGBA", (n * len(tiles), n), (0, 0, 0, 0))
    for i, tile in enumerate(tiles):
        out.paste(tile.image(), (i * n, 0))
    return out


def preview(tiles: list[Tile], scale: int = 4) -> Image.Image:
    """Nearest-neighbor contact sheet, so the pixels stay countable."""
    row = strip(tiles)
    return row.resize((row.width * scale, row.height * scale), Image.NEAREST)


def _inset(tile: Tile, color: str, pad: int = 1) -> None:
    """Keep a solid border so neighboring tiles of the same ground do not seam."""
    n = tile.n
    tile.rect(0, 0, n, pad, color)
    tile.rect(0, n - pad, n, pad, color)
    tile.rect(0, 0, pad, n, color)
    tile.rect(n - pad, 0, pad, n, color)


def grass(seed: int, base: str, dark: str, tip: str, spot: str, kind: int) -> Tile:
    """Meadow tile. Blades are 1px stems in clumps. The border stays the base color."""
    t = Tile()
    t.fill(base)
    rng = random.Random(seed)
    # Two clumps, so the tile is grass and not a flat square with three dots.
    for clump in range(2):
        cx = 3 + clump * 5 + (kind % 2)
        cy = 4 + (clump * 3 + kind) % 5
        for i in range(3):
            x = cx + (i - 1)
            h = 3 + ((seed + i + clump) % 3)
            y = cy
            t.rect(x, y, 1, h, dark)
            t.set(x, y, tip)
        t.rect(cx - 1, cy + 3, 3, 1, dark)
    if kind == 2:
        t.rect(6, 8, 3, 2, spot)
        t.set(7, 7, tip)
    elif kind == 3:
        t.rect(9, 9, 2, 2, dark)
        t.set(9, 8, spot)
    elif kind == 5:
        t.rect(4, 10, 3, 2, spot)
        t.set(5, 9, tip)
    elif kind == 7:
        t.set(8, 7, spot)
        t.set(9, 7, tip)
        t.set(8, 8, dark)
    elif kind % 2 == 0:
        t.set(5, 6, tip)
        t.set(11, 9, dark)
    _inset(t, base)
    if rng.randrange(2) == 0:
        t.set(4 + (seed % 7), 5 + (kind % 6), dark)
        _inset(t, base)
    return t


def soil(seed: int, base: str, dark: str, light: str, speck: str, kind: int) -> Tile:
    """Packed earth. Clods are 2×2, not single-pixel noise."""
    t = Tile()
    t.fill(base)
    rng = random.Random(seed)
    for i in range(3):
        x = 2 + rng.randrange(10)
        y = 2 + rng.randrange(10)
        t.rect(x, y, 2, 2, dark if i % 2 == 0 else light)
    if kind % 3 == 0:
        t.rect(6, 7, 4, 1, dark)
    elif kind % 3 == 1:
        t.rect(4, 5, 2, 2, speck)
    else:
        t.set(10, 4, light)
        t.set(11, 4, speck)
        t.set(10, 5, dark)
    _inset(t, base)
    return t


def brick(seed: int, fill: str, mortar: str, hi: str, shade: str) -> Tile:
    """Two brick courses. Joints stay on the same pixels so the floor tiles."""
    t = Tile()
    t.fill(mortar)
    # Top course, joint at x = 7. Bottom course, joints at x = 3 and x = 11.
    t.rect(0, 0, 7, 7, fill)
    t.rect(8, 0, 8, 7, fill)
    t.rect(0, 8, 3, 7, fill)
    t.rect(4, 8, 7, 7, fill)
    t.rect(12, 8, 4, 7, fill)
    for x, y, w, h in ((0, 0, 7, 7), (8, 0, 8, 7), (0, 8, 3, 7), (4, 8, 7, 7), (12, 8, 4, 7)):
        t.rect(x, y, w, 1, hi)
        t.rect(x, y + h - 1, w, 1, shade)
    rng = random.Random(seed)
    for _ in range(rng.randrange(1, 3)):
        t.set(rng.randrange(1, 15), rng.randrange(1, 14), shade if rng.randrange(2) else hi)
    # Put the mortar joints back. A chip must not erase the seam.
    t.rect(7, 0, 1, 7, mortar)
    t.rect(3, 8, 1, 7, mortar)
    t.rect(11, 8, 1, 7, mortar)
    t.rect(0, 7, 16, 1, mortar)
    t.rect(0, 15, 16, 1, mortar)
    return t


def pit(floor: str, hole: str, rim: str) -> Tile:
    """A square hole. The outer pixels stay the floor color."""
    t = Tile()
    t.fill(floor)
    t.rect(3, 3, 10, 10, rim)
    t.rect(4, 4, 8, 8, hole)
    t.rect(5, 5, 4, 2, rim)
    t.set(6, 6, floor)
    return t


def water(deep: str, mid: str, light: str, frame: int) -> Tile:
    """One frame of a pond. The ripple moves. The border stays deep so it tiles."""
    t = Tile()
    t.fill(deep)
    t.rect(0, 8, 16, 8, mid)
    y = 3 + (frame % 4)
    t.rect(2, y, 6, 1, light)
    t.rect(9, (y + 5) % 12 + 2, 5, 1, light)
    _inset(t, deep)
    return t


def field(seed: int, base: str, dark: str, light: str, kind: int) -> Tile:
    """Snow, sand, ash, or swamp. Same rule: clumps, then a solid border."""
    t = Tile()
    t.fill(base)
    rng = random.Random(seed + kind * 17)
    for i in range(2 + kind % 2):
        x = 2 + rng.randrange(10)
        y = 2 + rng.randrange(10)
        t.rect(x, y, 2 + (i % 2), 1 + (kind % 2), light if i == 0 else dark)
    if kind == 1:
        t.rect(7, 8, 1, 3, dark)
        t.rect(10, 8, 1, 3, dark)
    _inset(t, base)
    return t


# ---- Dungeon secrets: cracked brick, rune doors, braziers, saints. ----
# Overlays are drawn on top of the game's own cave wall, so they carry only the marks.

GLYPHS = {
    # 4 wide, 5 tall. Read left to right on a rune door.
    "moon": (".###", "##..", "#...", "##..", ".###"),
    "eye": ("....", ".##.", "#..#", ".##.", "...."),
    "cross": (".#..", "####", ".#..", ".#..", ".#.."),
}


def glyph(tile: Tile, x: int, y: int, name: str, color: str) -> None:
    for gy, row in enumerate(GLYPHS[name]):
        for gx, c in enumerate(row):
            if c == "#":
                tile.set(x + gx, y + gy, color)


def glyph_strip(names: list[str], colors: list[str]) -> Image.Image:
    """5x5 cells: for each glyph, one cell per color. Column = glyph * len(colors) + state."""
    out = Image.new("RGBA", (5 * len(names) * len(colors), 5), (0, 0, 0, 0))
    for gi, name in enumerate(names):
        for si, color in enumerate(colors):
            t = Tile(5)
            glyph(t, 0, 0, name, color)
            out.paste(t.image(), ((gi * len(colors) + si) * 5, 0))
    return out


def crack(kind: int, line: str, chip: str) -> Tile:
    """A hairline crack over a wall. One pixel wide, a lit lip under it, a little grit at the foot."""
    t = Tile()
    paths = (
        ((9, 0), (9, 1), (8, 2), (8, 3), (7, 4), (6, 5), (6, 6), (7, 7), (7, 8), (6, 9), (5, 10), (5, 11), (6, 12), (6, 13)),
        ((5, 0), (6, 1), (6, 2), (7, 3), (8, 4), (8, 5), (9, 6), (9, 7), (8, 8), (9, 9), (10, 10), (10, 11), (9, 12), (9, 13)),
    )
    branch = (((7, 7), (8, 7), (9, 8), (10, 8)), ((9, 6), (10, 5), (11, 5), (12, 4)))
    for x, y in paths[kind % 2]:
        t.set(x, y, line)
        if (x + y) % 3 == 0:
            t.set(x + 1, y, chip)
    for x, y in branch[kind % 2]:
        t.set(x, y, line)
    # Grit that fell out of the joint.
    t.set(4 + kind * 5, 15, chip)
    t.set(6 + kind * 3, 14, line)
    t.set(10 - kind * 4, 15, line)
    return t


def rune_door(frame: str, frame_hi: str, slab: str, band: str, rivet: str, slot: str) -> Tile:
    """A sealed slab in a stone frame. Three dark slots on top take the glyphs in code."""
    t = Tile()
    t.fill(slab)
    t.rect(0, 0, 16, 2, frame)
    t.rect(0, 0, 1, 16, frame)
    t.rect(15, 0, 1, 16, frame)
    t.rect(1, 0, 14, 1, frame_hi)
    t.rect(1, 2, 14, 6, slot)
    t.rect(1, 9, 14, 1, band)
    t.rect(1, 13, 14, 1, band)
    for x in (2, 13):
        t.set(x, 9, rivet)
        t.set(x, 13, rivet)
    t.rect(7, 10, 2, 3, slot)
    t.set(7, 11, band)
    return t


def sconce(iron: str, iron_mid: str, iron_hi: str, ash: str, ember: str, plate: str) -> Tile:
    """A wall brazier: bowl, stem, and a plate that takes one glyph at (6, 10)."""
    t = Tile()
    t.rect(3, 4, 10, 1, iron_hi)
    t.rect(3, 5, 10, 2, iron_mid)
    t.rect(4, 7, 8, 1, iron)
    t.rect(4, 3, 8, 1, ash)
    t.set(6, 3, ember)
    t.set(10, 3, ember)
    t.rect(7, 8, 2, 1, iron)
    t.rect(5, 9, 6, 7, iron)
    t.rect(6, 10, 4, 5, plate)
    t.set(5, 9, iron_mid)
    t.set(10, 9, iron_mid)
    return t


def flame(frame: int, deep: str, mid: str, light: str, core: str) -> Tile:
    """Fire for a brazier bowl. The base sits on row 15; the game lifts it onto the bowl."""
    t = Tile()
    lean = (0, 1, -1)[frame % 3]
    tip = (5, 7, 4)[frame % 3]
    t.rect(4, 13, 8, 3, deep)
    t.rect(5, 10, 6, 4, mid)
    t.rect(6 + lean, tip + 2, 4, 10 - tip, mid)
    t.rect(7 + lean, tip, 2, 2, deep)
    t.rect(6, 11, 4, 4, light)
    t.rect(7 + lean, tip + 4, 2, 7 - tip, light)
    t.rect(7, 13, 2, 2, core)
    if frame % 3 == 1:
        t.set(4, 11, deep)
    if frame % 3 == 2:
        t.set(11, 10, deep)
    return t


def saint(recess: str, stone: str, shade: str, hi: str, line: str) -> Tile:
    """A hooded stone saint in an arched niche. The plinth takes one glyph at (6, 11)."""
    t = Tile()
    t.rect(4, 1, 8, 15, recess)
    t.rect(3, 3, 10, 13, recess)
    # Hood and face.
    t.rect(6, 1, 4, 4, stone)
    t.rect(7, 2, 2, 2, line)
    t.set(6, 1, hi)
    # Shoulders and robe, lit from the upper left.
    t.rect(5, 5, 6, 5, stone)
    t.rect(9, 5, 2, 5, shade)
    t.rect(5, 5, 1, 4, hi)
    t.rect(7, 6, 2, 1, hi)
    t.rect(7, 7, 1, 3, shade)
    # Plinth.
    t.rect(4, 10, 8, 6, shade)
    t.rect(4, 10, 8, 1, hi)
    t.rect(5, 11, 6, 5, stone)
    return t


# ---- Floor traps: retracting spikes and pressure plates. Overlays on the game's own floor. ----

SPIKE_HOLES = ((3, 4), (7, 4), (11, 4), (3, 10), (7, 10), (11, 10))


def spike_grate(stage: int, frame: str, hole: str, iron: str, iron_hi: str, tip: str) -> Tile:
    """Stage 0: holes only. 1: tips show (the tell). 2: spikes up (it hurts)."""
    t = Tile()
    # An iron frame so a sleeping trap still reads as a trap.
    t.rect(1, 1, 14, 1, frame)
    t.rect(1, 14, 14, 1, frame)
    t.rect(1, 1, 1, 14, frame)
    t.rect(14, 1, 1, 14, frame)
    for x, y in SPIKE_HOLES:
        t.rect(x, y, 2, 2, hole)
        if stage == 1:
            t.set(x, y, iron_hi)
            t.set(x + 1, y, iron)
        if stage == 2:
            # Spike rises north of its hole: a lit left face, a dark right face, a pale tip.
            t.rect(x, y - 3, 1, 4, iron_hi)
            t.rect(x + 1, y - 3, 1, 4, iron)
            t.set(x, y - 3, tip)
            t.set(x + 1, y - 3, tip)
            t.set(x, y + 1, hole)
            t.set(x + 1, y + 1, hole)
    return t


def pressure_plate(pressed: bool, seam: str, face: str, face_hi: str, face_lo: str, mark: str) -> Tile:
    """A square slab with a dark seam. Pressed drops one pixel and darkens."""
    t = Tile()
    t.rect(2, 2, 12, 12, seam)
    if pressed:
        t.rect(3, 4, 10, 9, face_lo)
        t.rect(3, 4, 10, 1, face)
    else:
        t.rect(3, 3, 10, 10, face)
        t.rect(3, 3, 10, 1, face_hi)
        t.rect(3, 3, 1, 10, face_hi)
        t.rect(3, 12, 10, 1, face_lo)
        t.rect(12, 3, 1, 10, face_lo)
    # A small carved cross: the warning a careful hero can read.
    oy = 1 if pressed else 0
    t.rect(7, 6 + oy, 2, 4, mark)
    t.rect(6, 7 + oy, 4, 1, mark)
    return t


# ---- Rescue: the stake a captive is chained to. An overlay on the game's own floor. ----


def shackle(broken: bool, line: str, iron: str, iron_mid: str, iron_hi: str) -> Tile:
    """An iron stake driven into the floor, a chain, and an ankle cuff.

    Bound: the chain runs taut from the ring on the stake to a closed cuff where the captive's
    feet stand (left of middle). Broken: the chain hangs off the stake in two links and the cuff
    lies open on the floor.
    """
    t = Tile()
    # Stake: a ring on top, a post with a lit left face, a dark foot driven into the floor.
    t.rect(11, 6, 4, 1, line)
    t.rect(11, 9, 4, 1, line)
    t.rect(11, 7, 1, 2, line)
    t.rect(14, 7, 1, 2, line)
    t.rect(12, 7, 2, 2, iron_hi)
    t.rect(12, 8, 2, 1, iron)
    t.rect(12, 10, 2, 4, iron_mid)
    t.rect(12, 10, 1, 4, iron_hi)
    t.rect(11, 10, 1, 4, line)
    t.rect(14, 10, 1, 4, line)
    t.rect(11, 14, 4, 1, line)
    if not broken:
        # Taut chain: alternating links stepping down-left from the ring to the cuff.
        for i, (x, y) in enumerate(((10, 9), (9, 10), (8, 10), (7, 11), (6, 12))):
            t.set(x, y, iron_hi if i % 2 == 0 else iron_mid)
            t.set(x, y + 1, line)
        # Closed cuff round the ankle.
        t.rect(2, 12, 5, 3, line)
        t.rect(3, 12, 3, 1, iron_hi)
        t.rect(3, 14, 3, 1, iron)
        t.set(2, 13, iron_mid)
        t.set(6, 13, iron_mid)
    else:
        # Two links hang straight down off the ring; the rest of the chain is gone.
        t.set(10, 9, iron_hi)
        t.set(10, 10, line)
        t.set(10, 11, iron_mid)
        t.set(10, 12, line)
        # Open cuff on the floor: a C with its mouth to the right, and one loose link.
        t.rect(2, 12, 4, 1, line)
        t.rect(2, 14, 4, 1, line)
        t.set(2, 13, line)
        t.rect(3, 13, 2, 1, iron_hi)
        t.set(5, 13, iron)
        t.set(7, 14, iron_mid)
        t.set(8, 14, line)
    return t
