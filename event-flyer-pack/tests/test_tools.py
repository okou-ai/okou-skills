"""Local tests only: no paid image generation or network access."""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import pymupdf as fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import formats
import overlay_qr
import restore_reference

URL = "https://example.com/ai-night"


class ToolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.out = Path(cls.directory.name)
        cls.qr = cls.out / "qr.png"
        cls.svg = cls.out / "qr.svg"
        command = [sys.executable, str(ROOT / "scripts/generate_qr.py"), "--url", URL,
                   "--png", str(cls.qr), "--svg", str(cls.svg), "--error", "H",
                   "--border", "4", "--box-size", "16"]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.base = cls.out / "base.png"
        base = Image.new("RGB", formats.A6_PIXELS, "#181818")
        ImageDraw.Draw(base).rectangle((480, 1350, 759, 1629), fill="white")
        base.save(cls.base)
        cls.front = cls.out / "front.png"
        overlay_qr.composite(cls.base, cls.qr, cls.front, 480, 1350, 280, URL)

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def test_reference_restored_losslessly(self):
        target = self.out / "reference.png"
        restore_reference.restore(ROOT / "assets/style-reference.png.b64", target)
        with Image.open(target) as image:
            self.assertEqual(image.size, (896, 1200))
        self.assertEqual(target.stat().st_size, 1151312)

    def test_corrupt_reference_rejected(self):
        bad = self.out / "corrupt.b64"
        bad.write_text("YWJj")
        target = self.out / "corrupt-reference.png"
        with self.assertRaises(ValueError):
            restore_reference.restore(bad, target)
        self.assertFalse(target.exists())

    def test_qr_png_and_svg(self):
        self.assertEqual(overlay_qr.decode(formats.load(self.qr)), URL)
        self.assertIn("<svg", self.svg.read_text())

    def test_invalid_url_rejected(self):
        bad = self.out / "invalid-url.png"
        result = subprocess.run([sys.executable, str(ROOT / "scripts/generate_qr.py"),
                                 "--url", "javascript:alert(1)", "--png", str(bad)],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(bad.exists())

    def test_auto_detect_one(self):
        self.assertEqual(overlay_qr.find_white_square(self.base), (480, 1350, 280))

    def test_auto_detect_ambiguous(self):
        image = formats.load(self.base)
        ImageDraw.Draw(image).rectangle((100, 200, 379, 479), fill="white")
        path = self.out / "ambiguous.png"
        image.save(path)
        with self.assertRaises(ValueError):
            overlay_qr.find_white_square(path)

    def test_auto_detect_does_not_choose_white_canvas(self):
        path = self.out / "white.png"
        Image.new("RGB", (900, 1200), "white").save(path)
        with self.assertRaises(ValueError):
            overlay_qr.find_white_square(path)

    def test_manual_bounds_rejected(self):
        target = self.out / "off-canvas.png"
        with self.assertRaises(ValueError):
            overlay_qr.composite(self.base, self.qr, target, 1200, 1500, 280, URL)
        self.assertFalse(target.exists())

    def test_wrong_expected_url_rejected(self):
        target = self.out / "wrong-url.png"
        with self.assertRaises(ValueError):
            overlay_qr.composite(self.base, self.qr, target, 480, 1350, 280,
                                 "https://example.com/different")
        self.assertFalse(target.exists())

    def test_fake_qr_fully_cleared(self):
        path = self.out / "fake.png"
        image = formats.load(self.base)
        # Fake modules at the outer edges must disappear, not remain near the real QR.
        ImageDraw.Draw(image).rectangle((480, 1350, 759, 1629), fill="black")
        image.save(path)
        target = self.out / "cleared.png"
        result = overlay_qr.composite(path, self.qr, target, 480, 1350, 280, URL)
        exported = formats.load(target)
        self.assertEqual(exported.getpixel((480, 1350)), (255, 255, 255))
        self.assertEqual(exported.getpixel((759, 1629)), (255, 255, 255))
        self.assertTrue(result["qr_pass"])

    def test_too_few_pixels_per_module_rejected(self):
        with self.assertRaises(ValueError):
            overlay_qr.composite(self.base, self.qr, self.out / "tiny.png", 480, 1350, 80, URL)

    def test_integer_modules_and_quiet_zone(self):
        result = overlay_qr.composite(self.base, self.qr, self.out / "integer.png",
                                      480, 1350, 280, URL)
        self.assertIsInstance(result["module_pixels"], int)
        self.assertGreaterEqual(result["module_pixels"], 3)
        self.assertEqual(result["quiet_zone_modules"], 4)

    def test_dpi_metadata_preserved(self):
        source = self.out / "dpi-base.png"
        formats.load(self.base).save(source, dpi=(300, 300))
        target = self.out / "dpi-final.png"
        overlay_qr.composite(source, self.qr, target, 480, 1350, 280, URL)
        with Image.open(target) as image:
            self.assertAlmostEqual(image.info["dpi"][0], 300, places=1)

    def test_source_overwrite_rejected(self):
        with self.assertRaises(ValueError):
            overlay_qr.composite(self.base, self.qr, self.base, 480, 1350, 280, URL)

    def test_cli_requires_verify(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/overlay_qr.py"),
                                 str(self.base), str(self.qr), str(self.out / "unverified.png"),
                                 "--auto-detect"], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)

    def test_cli_auto_and_manual_conflict(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/overlay_qr.py"),
                                 str(self.base), str(self.qr), str(self.out / "conflict.png"),
                                 "--auto-detect", "--x", "480", "--y", "1350",
                                 "--size", "280", "--verify", URL], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)

    def test_normalize_preserves_aspect(self):
        source = self.out / "wide.png"
        Image.new("RGB", (200, 100), "red").save(source)
        target = self.out / "normalized.png"
        result = formats.normalize(source, target, 200, 200, "#181818")
        self.assertEqual(result["content_pixels"], [200, 100])
        self.assertEqual(formats.load(target).getpixel((0, 0)), (24, 24, 24))
        self.assertFalse(result["qr_verified"])

    def test_four_up_final_pdf_each_panel(self):
        result = formats.four_up(self.front, self.front, self.out / "four", "test-event", URL)
        self.assertEqual(result["tile_mm"], [99.75, 140.6])
        self.assertEqual(len(result["outputs"]), 2)
        for output in result["outputs"]:
            self.assertEqual(len(output["qr_checks"]), 4)
            self.assertTrue(all(check["qr_pass"] for check in output["qr_checks"]))
            with fitz.open(output["output"]) as pdf:
                self.assertEqual(len(pdf), 1)
                self.assertAlmostEqual(pdf[0].rect.width, 210 * formats.mm, places=2)
                self.assertAlmostEqual(pdf[0].rect.height, 297 * formats.mm, places=2)

    def test_four_up_invalid_slug(self):
        with self.assertRaises(ValueError):
            formats.four_up(self.front, self.front, self.out / "bad-four", "../escape", URL)

    def test_four_up_wrong_url_no_outputs(self):
        target = self.out / "wrong-four"
        with self.assertRaises(ValueError):
            formats.four_up(self.front, self.front, target, "test-event", URL + "-wrong")
        self.assertFalse(target.exists())

    def test_tent_each_half_png_and_pdf(self):
        target = self.out / "tent.png"
        result = formats.tent(self.front, self.front, target, URL)
        self.assertEqual(formats.load(target).size, (1240, 3496))
        self.assertEqual(len(result["png_qr_checks"]), 2)
        self.assertEqual(len(result["pdf_qr_checks"]), 2)
        # Exact rotation, not a horizontal mirror.
        exported = formats.load(target)
        self.assertEqual(exported.crop((0, 0, 1240, 1748)).tobytes(),
                         formats.load(self.front).transpose(Image.Transpose.ROTATE_180).tobytes())

    def test_story_lossy_export_verified(self):
        source = self.out / "story-base.png"
        Image.new("RGB", (1080, 1920), "#181818").save(source)
        composed = self.out / "story.png"
        overlay_qr.composite(source, self.qr, composed, 390, 1320, 300, URL)
        result = formats.story(composed, self.out / "story.jpg", URL)
        self.assertEqual(result["pixels"], [1080, 1920])
        self.assertTrue(result["qr_checks"][0]["qr_pass"])

    def test_story_wrong_dimensions_rejected(self):
        with self.assertRaises(ValueError):
            formats.story(self.front, self.out / "invalid-story.jpg", URL)

    def test_wrong_url_query_or_fragment_not_normalized(self):
        with self.assertRaises(ValueError):
            overlay_qr.composite(self.base, self.qr, self.out / "wrong-fragment.png",
                                 480, 1350, 280, URL + "#other")


if __name__ == "__main__":
    unittest.main()
