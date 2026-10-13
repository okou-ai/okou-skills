import hashlib
import importlib.util
from pathlib import Path
import re
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("prepare_web", Path(__file__).parents[1] / "tools/prepare-web.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class WebBundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.draft = self.root / "draft"
        self.draft.mkdir()

    def write(self, name, value):
        path = self.draft / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value)
        return path

    def build(self, name="web"):
        output = self.root / name
        receipt = module.prepare(self.draft / "index.html", output)
        for item in receipt["files"]:
            actual = hashlib.sha256((output / item["file"]).read_bytes()).hexdigest()
            self.assertEqual(actual, item["sha256"])
            if item["file"] != "index.html":
                self.assertIn(actual[:12], item["file"])
        return output, receipt

    def test_hashes_dependency_graph_and_preserves_draft(self):
        self.write("index.html", '<link href="styles/main.css" rel="stylesheet"><h1>Kept</h1>')
        self.write("styles/main.css", '@import "base.css"; .hero{background:url(../art/photo.png?v=1#crop)}')
        self.write("styles/base.css", '@font-face{src:url(../fonts/main.woff)}')
        self.write("art/photo.png", "photo")
        self.write("fonts/main.woff", "font")
        self.write("qa/report.json", "not published")
        before = {p.relative_to(self.draft): p.read_bytes() for p in self.draft.rglob("*") if p.is_file()}
        web, receipt = self.build()
        self.assertEqual(len(receipt["files"]), 5)
        self.assertFalse((web / "qa").exists())
        self.assertEqual(before, {p.relative_to(self.draft): p.read_bytes() for p in self.draft.rglob("*") if p.is_file()})
        css = next((web / "styles").glob("main-*.css")).read_text()
        self.assertRegex(css, r'base-[0-9a-f]{12}\.css')
        self.assertRegex(css, r'photo-[0-9a-f]{12}\.png\?v=1#crop')

    def test_asset_edit_changes_ancestor_hashes_and_leaves_previous_bundle(self):
        self.write("index.html", '<link href="main.css">')
        self.write("main.css", 'p{background:url(image.png)}')
        image = self.write("image.png", "first")
        one, _ = self.build("one")
        before = (one / "index.html").read_bytes()
        image.write_text("second")
        two, _ = self.build("two")
        self.assertNotEqual(before, (two / "index.html").read_bytes())
        self.assertEqual(before, (one / "index.html").read_bytes())

    def test_existing_output_and_index_are_never_removed(self):
        index = self.write("index.html", '<h1>Original</h1>')
        web, _ = self.build()
        with self.assertRaisesRegex(ValueError, "new --out"):
            module.prepare(index, web)
        self.assertEqual(index.read_bytes(), (web / "index.html").read_bytes())

    def test_missing_resource_and_cycles_fail_before_output(self):
        self.write("index.html", '<img src="missing.png">')
        with self.assertRaisesRegex(ValueError, "Missing asset"):
            self.build()
        self.assertFalse((self.root / "web").exists())
        self.write("index.html", '<link href="a.css">')
        self.write("a.css", '@import "b.css";')
        self.write("b.css", '@import "a.css";')
        with self.assertRaisesRegex(ValueError, "Cyclic"):
            self.build()
        self.assertFalse((self.root / "web").exists())

    def test_svg_case_inline_css_srcset_and_script_text_survive(self):
        self.write("a b.png", "image")
        self.write("art.svg", '<svg><defs><linearGradient id="g"></linearGradient></defs><image href="a%20b.png"/></svg>')
        script = '<script>const literal = "src=untouched.png";</script>'
        self.write("index.html", '<style>p{background:url("a%20b.png")}</style>'
                   '<img srcset="art.svg 1x, a%20b.png 2x"><svg><linearGradient id="g"></linearGradient></svg>' + script)
        web, _ = self.build()
        text = (web / "index.html").read_text()
        self.assertIn(script, text)
        self.assertIn('<linearGradient id="g"></linearGradient>', text)
        self.assertRegex(text, r'art-[0-9a-f]{12}\.svg 1x')
        self.assertIn('<linearGradient id="g"></linearGradient>', next(web.glob('art-*.svg')).read_text())

    def test_external_and_data_urls_are_untouched(self):
        raw = '<img src="data:image/png;base64,AA=="><a href="#local">Jump</a><link href="https://example.com/a.css">'
        self.write("index.html", raw)
        web, receipt = self.build()
        self.assertEqual((web / "index.html").read_text(), raw)
        self.assertEqual(len(receipt["files"]), 1)

    def test_asset_escape_via_parent_or_symlink_is_rejected(self):
        (self.root / "outside.png").write_text("outside")
        self.write("index.html", '<img src="../outside.png">')
        with self.assertRaisesRegex(ValueError, "escapes"):
            self.build()
        (self.draft / "linked.png").symlink_to(self.root / "outside.png")
        self.write("index.html", '<img src="linked.png">')
        with self.assertRaisesRegex(ValueError, "escapes"):
            self.build()


if __name__ == "__main__":
    unittest.main()
