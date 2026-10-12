import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image
from pypdf import PdfReader


HELPER = Path(__file__).resolve().parents[1] / "scripts" / "source-derivatives.py"


class SourceDerivativesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="presentation source ")
        self.addCleanup(self.tmp.cleanup)
        self.work = Path(self.tmp.name)
        self.pages = self.work / "source-pages"
        self.pages.mkdir()

    def capture(self, count=3, size=(1600, 900)):
        for page in range(1, count + 1):
            with Image.new("RGB", size, (page % 256, 80, 120)) as image:
                image.save(self.pages / f"page-{page:03}.png")
        self.originals = self.fingerprints()

    def fingerprints(self):
        return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in self.pages.iterdir()}

    def run_helper(self, *flags):
        result = subprocess.run(
            [sys.executable, str(HELPER), "--work-dir", str(self.work), *flags],
            capture_output=True, text=True, check=True,
        )
        self.assertEqual(self.fingerprints(), self.originals)
        return json.loads(result.stdout)

    def test_combined_outputs_preserve_originals_and_full_size_pdf_pages(self):
        self.capture()
        result = self.run_helper("--contact-sheet", "--pdf")
        self.assertEqual(result["pageCount"], 3)
        self.assertEqual(Path(result["pages"]), self.pages)
        self.assertEqual(result["previews"], [str(self.work / "previews/contact-sheet-001.png")])
        summary = json.loads(Path(result["sourceSummary"]).read_text())
        self.assertEqual([page["file"] for page in summary["pages"]], [f"page-{n:03}.png" for n in range(1, 4)])
        self.assertEqual(summary["pages"][0]["sampledColors"][0], {"hex": "#015078", "fraction": 1.0})
        self.assertEqual(Path(result["pdf"]), self.work / "upload/source.pdf")
        pdf = PdfReader(result["pdf"])
        self.assertEqual(len(pdf.pages), 3)
        for page in pdf.pages:
            self.assertEqual(float(page.mediabox.width), 1200)
            self.assertEqual(float(page.mediabox.height), 675)
        with Image.open(result["previews"][0]) as preview:
            self.assertEqual(preview.size, (1344, 212))
            self.assertEqual(preview.getpixel((10, 30)), (1, 80, 120))

    def test_preview_only_splits_large_decks_without_creating_a_pdf(self):
        self.capture(21, (160, 90))
        result = self.run_helper("--contact-sheet")
        self.assertEqual(len(result["previews"]), 2)
        self.assertIsNone(result["pdf"])
        self.assertFalse((self.work / "upload").exists())
        with Image.open(result["previews"][1]) as preview:
            self.assertEqual(preview.getpixel((10, 30)), (21, 80, 120))

    def test_pdf_only_avoids_creating_previews(self):
        self.capture(2, (160, 90))
        result = self.run_helper("--pdf")
        self.assertEqual(len(PdfReader(result["pdf"]).pages), 2)
        self.assertEqual(result["previews"], [])
        self.assertFalse((self.work / "previews").exists())

    def test_missing_source_page_stops_before_creating_outputs(self):
        self.capture()
        (self.pages / "page-002.png").unlink()
        result = subprocess.run(
            [sys.executable, str(HELPER), "--work-dir", str(self.work), "--pdf"],
            capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("consecutive original", result.stderr)
        self.assertFalse((self.work / "upload").exists())


if __name__ == "__main__":
    unittest.main()
