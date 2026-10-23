"""Tests for art_checks.py. Run: python3 tools/check-sprite/test_art_checks.py  (or pytest)."""
import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from PIL import Image
import art_checks as ac

INK, FILL = (0x1a, 0x14, 0x18, 255), (200, 120, 80, 255)
INKHEX = "#1a1418"
FW, FH = 16, 20


def blob(im, ox, x0, y0, x1, y1, fill=FILL):
    """Ink-outlined rectangle [x0,x1]x[y0,y1] inside frame at x offset ox."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            edge = x in (x0, x1) or y in (y0, y1)
            im.putpixel((ox + x, y), INK if edge else fill)


def sheet(n):
    return Image.new("RGBA", (FW * n, FH), (0, 0, 0, 0))


def frames(n):
    return [{"x": i * FW, "y": 0, "name": f"f{i}"} for i in range(n)]


def run(im, n):
    return ac.role_issues(im.load(), frames(n), FW, FH, INKHEX)


class ArtChecks(unittest.TestCase):
    def clean(self, n=4):
        im = sheet(n)
        for i in range(n):
            blob(im, i * FW, 3, 2, 12, 19)
        return im

    def test_clean_passes(self):
        self.assertEqual({k: v for k, v in run(self.clean(), 4).items() if v}, {})

    def test_hole(self):
        im = self.clean()
        for x, y in ((6, 8), (7, 8), (6, 9), (7, 9)):
            im.putpixel((FW + x, y), (0, 0, 0, 0))
        r = run(im, 4)
        self.assertTrue(r["holes"]); self.assertIn("f1", r["holes"][0])

    def test_tiny_hole_ok(self):
        im = self.clean(); im.putpixel((FW + 6, 8), (0, 0, 0, 0))
        self.assertFalse(run(im, 4)["holes"])

    def test_missing_limb_shrink(self):
        im = self.clean()
        for y in range(FH):
            for x in range(FW):
                im.putpixel((2 * FW + x, y), (0, 0, 0, 0))
        blob(im, 2 * FW, 3, 10, 12, 19)   # half height
        self.assertTrue(any("f2" in m for m in run(im, 4)["limbs"]))

    def test_split_blobs(self):
        im = self.clean()
        for y in range(FH):
            im.putpixel((3 * FW + 7, y), (0, 0, 0, 0)); im.putpixel((3 * FW + 8, y), (0, 0, 0, 0))
        r = run(im, 4)["limbs"]
        self.assertTrue(any("f3" in m and "blobs" in m for m in r))

    def test_outline_gap(self):
        im = self.clean(); im.putpixel((5, 2), FILL)
        self.assertTrue(run(im, 4)["outline1px"])

    def test_doubled_outline(self):
        im = self.clean()
        blob(im, 0, 4, 3, 11, 18, fill=FILL)   # inner ink ring right inside the outer one
        self.assertTrue(any("doubled" in m for m in run(im, 4)["outline1px"]))

    def test_soft_alpha(self):
        im = self.clean(); im.putpixel((FW + 6, 8), (200, 120, 80, 128))
        self.assertTrue(run(im, 4)["soft_alpha"])

    def test_allowlist_parse(self):
        p = Path(__file__).with_name("_tmp_allow.txt")
        p.write_text("# c\na.png::r::holes  # why\n\n")
        try:
            self.assertEqual(ac.load_allowlist(p), {"a.png::r::holes"})
        finally:
            p.unlink()

    def test_allowlist_file_wellformed(self):
        for k in ac.load_allowlist():
            a, r, c = k.split("::")
            self.assertIn(c, ac.CHECKS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
