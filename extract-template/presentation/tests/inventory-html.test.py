import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HELPER = Path(__file__).resolve().parents[1] / "scripts" / "inventory-html.py"
SPEC = importlib.util.spec_from_file_location("inventory_html", HELPER)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class InventoryHTMLTest(unittest.TestCase):
    def test_preserves_editable_markup_and_reports_missing_fit(self):
        fragment = '''<section class="slide"><div class="stage" data-layout="title" data-slot="cover">
<h1 data-region="title">你好 &amp; <em>world</em></h1><svg><text x="2">Live text</text></svg>
<img src="images/one.png" alt=""><!-- keep this --></div></section>'''
        source = '<html><head><link href="styles.css" rel="stylesheet"></head><body><main class="deck">' + fragment + '</main></body></html>'
        report, fragments = MODULE.inventory(source, "source.html", base="https://example.com/deck/")
        self.assertEqual(report["pageCount"], 1)
        self.assertEqual(fragments["source/title.html"], fragment)
        self.assertEqual(report["layouts"][0]["regions"][0]["characters"], len("你好 & world"))
        self.assertEqual(report["layouts"][0]["sourceRole"], "cover")
        self.assertIn("found 0", report["layouts"][0]["issues"][0])
        self.assertEqual(report["resources"][1]["resolved"], "https://example.com/deck/images/one.png")

    def test_repeated_names_preserve_every_page_and_ignore_script_markup(self):
        slide = '<div class="slide"><div class="stage" data-layout="title"><div class="fit">Text</div></div></div>'
        source = '<main class="deck">' + slide * 3 + '</main><script>const example = \'<div class="slide">\';</script>'
        report, fragments = MODULE.inventory(source, "deck.html")
        self.assertEqual(list(fragments), ["source/title.html", "source/title-2.html", "source/title-3.html"])
        self.assertEqual([entry["sourcePages"] for entry in report["layouts"]], [[1], [2], [3]])
        self.assertTrue(all(not entry["issues"] for entry in report["layouts"]))
        self.assertEqual(len(report["scripts"]), 1)

    def test_fit_in_another_page_does_not_mask_missing_root(self):
        source = '<div class="slide"><div class="stage"><div class="fit">A</div></div></div><div class="slide"><div class="stage">B</div></div>'
        report, _ = MODULE.inventory(source, "deck.html")
        self.assertEqual(report["layouts"][0]["issues"], [])
        self.assertTrue(report["layouts"][1]["issues"])

    def test_custom_classes_and_inline_svg(self):
        source = '<section class="page"><div class="canvas"><div class="fit"><svg><path d="M0 0" /></svg></div></div></section>'
        report, _ = MODULE.inventory(source, "deck.html", "page", "canvas")
        self.assertEqual(report["pageCount"], 1)
        self.assertEqual(report["layouts"][0]["issues"], [])

    def test_html_base_changes_resource_resolution(self):
        source = '<base href="../shared/"><div class="slide"><div class="stage"><div class="fit"><img src="one.png"></div></div></div>'
        report, _ = MODULE.inventory(source, "deck.html", base="https://example.com/deck/")
        self.assertEqual(report["resources"][0]["resolved"], "https://example.com/shared/one.png")

    def test_pdf_text_lines_are_observations_without_claiming_editability(self):
        page = '<div class="pf" data-page-no="a"><div class="pc"><div class="t ff0">A <span>title</span></div><div class="t ff0" style="visibility:hidden">Hidden text</div></div></div>'
        report, fragments = MODULE.inventory(page, "source.html", "pf", "pc", text_class="t")
        self.assertEqual(fragments["source/page-001.html"], page)
        self.assertEqual(report["layouts"][0]["regions"], [{"role": "source-text", "runs": 2,
                         "characters": len("A titleHidden text"), "sample": "A titleHidden text"}])
        self.assertTrue(report["layouts"][0]["issues"])

    def test_duplicate_and_misplaced_fit_are_reported(self):
        source = '<div class="slide"><div class="stage"><div class="fit"></div><div class="fit"></div></div></div><div class="slide"><div class="stage"></div><div class="fit"></div></div>'
        report, _ = MODULE.inventory(source, "deck.html")
        self.assertIn("found 2", report["layouts"][0]["issues"][0])
        self.assertIn("found 0", report["layouts"][1]["issues"][0])

    def test_incomplete_or_dynamic_source_requests_rendered_dom(self):
        for source in ['<div id="app"></div>', '<div class="slide"><div class="stage"><p>Unclosed</div></div>',
                       '<div class="slide"><div class="slide"></div></div>']:
            with self.subTest(source=source), self.assertRaises(ValueError):
                MODULE.inventory(source, "deck.html")

    def test_cli_writes_once_without_overwriting_evidence(self):
        with tempfile.TemporaryDirectory(prefix="html inventory ") as temporary:
            root = Path(temporary)
            source, output = root / "input.html", root / "inspection"
            original = '<div class="slide"><div class="stage"><div class="fit">Title</div></div></div>'
            source.write_text(original)
            command = [sys.executable, str(HELPER), "--input", str(source), "--out", str(output)]
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            self.assertEqual(json.loads(result.stdout)["pageCount"], 1)
            self.assertEqual((output / "source/page-001.html").read_text(), original)
            self.assertEqual(source.read_text(), original)
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)


if __name__ == "__main__":
    unittest.main()
