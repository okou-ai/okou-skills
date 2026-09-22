"""Rendered regressions for the optional ReportLab Simplified Chinese route.

Requires reportlab, PyMuPDF, fonts-wqy-zenhei and fonts-dejavu-core as documented
in references/pdf-authoring.md. These checks supplement, not replace, page review.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    import pymupdf
    from reportlab.pdfbase.ttfonts import TTFont
except ImportError:
    pymupdf = None
    TTFont = None


SKILL_DIR = Path(__file__).resolve().parents[1]
CJK_FONT = Path("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc")
SYMBOL_FONT = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")


@unittest.skipUnless(
    pymupdf and TTFont and CJK_FONT.exists() and SYMBOL_FONT.exists(),
    "Install the optional ReportLab Chinese route dependencies to run this smoke test",
)
class ChinesePdfExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temp.name) / "chinese.pdf"
        subprocess.run(
            [sys.executable, str(SKILL_DIR / "scripts/author_pdf_cjk.py"),
             str(cls.output)],
            check=True,
        )

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_fonts_are_embedded_and_language_is_simplified_chinese(self):
        with pymupdf.open(self.output) as document:
            self.assertEqual(document.xref_get_key(document.pdf_catalog(), "Lang"),
                             ("string", "zh-CN"))
            fonts = document[0].get_fonts()
            for name in ("WenQuanYiZenHei", "DejaVuSans"):
                match = [font for font in fonts if name in font[3]]
                self.assertEqual(len(match), 1, name)
                self.assertEqual(match[0][1], "ttf")
                self.assertTrue(document.extract_font(match[0][0])[3], name)

    def test_punctuation_and_bullets_have_real_glyphs_and_visible_ink(self):
        cjk = TTFont("CoverageCjk", str(CJK_FONT), subfontIndex=0)
        symbols = TTFont("CoverageSymbols", str(SYMBOL_FONT))
        required = set("中·•，。；：“”《》（）%0123ABC")
        for character in required:
            font = symbols if character == "•" else cjk
            self.assertTrue(font.face.charToGlyph.get(ord(character)), character)

        seen = set()
        with pymupdf.open(self.output) as document:
            for page in document:
                self.assertNotIn("\ufffd", page.get_text())
                for block in page.get_text("rawdict")["blocks"]:
                    for line in block.get("lines", []):
                        for span in line["spans"]:
                            for char in span["chars"]:
                                character = char["c"]
                                if character not in required:
                                    continue
                                seen.add(character)
                                expected_font = "DejaVuSans" if character == "•" else "WenQuanYi"
                                self.assertIn(expected_font, span["font"], character)
                                pixels = page.get_pixmap(
                                    matrix=pymupdf.Matrix(4, 4),
                                    clip=pymupdf.Rect(char["bbox"]),
                                    colorspace=pymupdf.csGRAY, alpha=False,
                                )
                                self.assertGreater(
                                    sum(value < 200 for value in pixels.samples),
                                    2, f"No visible ink for {character!r}",
                                )
        self.assertEqual(seen, required)

    def test_long_chinese_paragraph_wraps_within_page_margins(self):
        with pymupdf.open(self.output) as document:
            page = document[0]
            blocks = page.get_text("dict")["blocks"]
            # A text extractor may split one authored paragraph into several
            # blocks. Its final paragraph still has distinct wrapped baselines.
            all_lines = [line for block in blocks for line in block.get("lines", [])]
            starts = [
                i for i, line in enumerate(all_lines)
                if "连续中文" in "".join(span["text"] for span in line["spans"])
            ]
            self.assertEqual(len(starts), 1)
            lines = all_lines[starts[0]:]
            self.assertGreaterEqual(len(lines), 3)
            for line in lines:
                self.assertGreaterEqual(line["bbox"][0], 54)
                self.assertLessEqual(line["bbox"][2], page.rect.width - 54)
                text = "".join(span["text"] for span in line["spans"]).strip()
                self.assertNotIn(text[0], "，。；：！？、）】》”’")


if __name__ == "__main__":
    unittest.main()
