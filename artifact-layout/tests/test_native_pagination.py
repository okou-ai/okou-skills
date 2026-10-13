"""Regressions discovered by real, multi-page report-authoring experiments."""

# ruff: noqa: E402 -- Imports follow the local script path bootstrap.

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PACKAGE / "scripts"))

from native import font_reference
from render import chart_geometry, load_asset, render_report


@unittest.skipUnless(
    all(importlib.util.find_spec(name) for name in ["docx", "typst", "PIL", "pypdf"]),
    "Native engines not installed",
)
class NativePaginationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.report = {
            "version": 1,
            "title": "Report with supplied material",
            "language": "en",
            "theme": "corporate",
            "recipe": "executive-brief",
            "sections": [{"layout": "single", "blocks": []}],
        }

    def render(self, name, formats):
        model = self.directory / f"{name}.json"
        model.write_text(json.dumps(self.report), encoding="utf-8")
        return render_report(model, self.directory / name, formats)

    def test_chart_title_unit_caption_and_source_share_one_pdf_page(self):
        from pypdf import PdfReader

        for paragraphs in [5, 8, 11, 14]:
            with self.subTest(paragraphs=paragraphs):
                self.report["sections"][0]["blocks"] = [
                    {
                        "type": "prose",
                        "paragraphs": [
                            f"FILLER_{index:02d} "
                            + "Supplied explanation stays readable and flows across pages. "
                            * 5
                            for index in range(paragraphs)
                        ],
                    },
                    {
                        "type": "bar-chart",
                        "title": "GROUP_HEAD",
                        "unit": "GROUP_UNIT",
                        "labels": ["A", "B", "C"],
                        "values": [10, 20, 30],
                        "caption": "GROUP_CAPTION",
                        "source": "GROUP_SOURCE",
                    },
                ]
                files = self.render(f"pdf{paragraphs}", ("pdf",))
                texts = [page.extract_text() for page in PdfReader(files["pdf"]).pages]
                positions = [
                    next(index for index, text in enumerate(texts) if marker in text)
                    for marker in [
                        "GROUP_HEAD",
                        "GROUP_UNIT",
                        "GROUP_CAPTION",
                        "GROUP_SOURCE",
                    ]
                ]
                self.assertEqual(len(set(positions)), 1)
                all_text = "".join(texts)
                self.assertTrue(
                    all(
                        f"FILLER_{index:02d}" in all_text for index in range(paragraphs)
                    )
                )

    def test_word_metrics_quotes_and_figures_keep_related_paragraphs(self):
        from docx import Document

        blocks = [
            {
                "type": "big-number",
                "value": "24",
                "label": "Metric label",
                "period": "2026",
                "note": "Metric context",
                "source": "Metric source",
            },
            {
                "type": "pull-quote",
                "text": "Literal quotation.",
                "attribution": "Named speaker",
                "source": "Quote source",
            },
            {
                "type": "line-chart",
                "title": "Chart heading",
                "unit": "Accounts",
                "labels": ["Apr", "Sep"],
                "values": [320, 451],
                "caption": "Chart caption",
                "source": "Chart source",
            },
        ]
        for index, block in enumerate(blocks):
            with self.subTest(component=block["type"]):
                self.report["sections"][0]["blocks"] = [block]
                word = Document(self.render(f"word{index}", ("docx",))["docx"])
                paragraphs = word.paragraphs[
                    1:
                ]  # The document title is outside the component.
                self.assertGreater(len(paragraphs), 2)
                self.assertTrue(
                    all(p.paragraph_format.keep_with_next for p in paragraphs[:-1])
                )
                self.assertFalse(paragraphs[-1].paragraph_format.keep_with_next)
                self.assertTrue(
                    all(p.paragraph_format.keep_together for p in paragraphs)
                )

    def test_unit_taller_than_a_page_flows_without_losing_content(self):
        from pypdf import PdfReader

        tokens = [f"NOTE_{index:03d}" for index in range(500)]
        self.report["sections"][0]["blocks"] = [
            {
                "type": "big-number",
                "value": "24",
                "label": "Context supplied with a metric",
                "note": " ".join(tokens),
                "source": "END_SOURCE",
            }
        ]
        pdf = PdfReader(self.render("long-context", ("pdf",))["pdf"])
        self.assertGreater(len(pdf.pages), 1)
        text = "".join("".join(page.extract_text().split()) for page in pdf.pages)
        self.assertTrue(all(token in text for token in tokens))
        self.assertIn("END_SOURCE", text)

    def test_scaled_line_axis_labels_fit_inside_the_rendered_image(self):
        from PIL import Image, ImageDraw, ImageFont

        theme = load_asset("themes.json")["corporate"]
        chart = {
            "type": "line-chart",
            "labels": ["Apr", "May", "Jun", "Jul", "Aug", "Sep"],
            "values": [320, 348, 367, 395, 423, 451],
        }
        for label_size in [30, 48]:
            with self.subTest(label_size=label_size):
                geometry = chart_geometry(chart, theme, label_size=label_size)
                file_name, face_index = font_reference(theme["body"])
                font = ImageFont.truetype(
                    file_name, round(label_size), index=face_index
                )
                draw = ImageDraw.Draw(
                    Image.new("RGB", (640, round(geometry["height"])))
                )
                for x, y, text, anchor, _, _ in geometry["texts"]:
                    bounds = draw.textbbox(
                        (x, y),
                        text,
                        font=font,
                        anchor={"start": "ls", "end": "rs", "middle": "ms"}[anchor],
                    )
                    self.assertGreaterEqual(bounds[0], 0, text)
                    self.assertGreaterEqual(bounds[1], 0, text)
                    self.assertLessEqual(bounds[2], geometry["width"], text)
                    self.assertLessEqual(bounds[3], geometry["height"], text)
