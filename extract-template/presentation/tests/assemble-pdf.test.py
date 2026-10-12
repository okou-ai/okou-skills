import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HELPER = Path(__file__).resolve().parents[1] / "scripts/assemble-pdf.py"
SPEC = importlib.util.spec_from_file_location("assemble_pdf", HELPER)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AssemblePDFTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="pdf assembly with spaces ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.work, self.package = self.root / "work", self.root / "template"
        self.converted = self.work / "pdf-html"
        self.converted.mkdir(parents=True)
        html = '<html><head><link rel="stylesheet" href="source.css"></head><body>' + ''.join(
            f'<div class="pf w0 h0" id="pf{number}" data-page-no="{number}">'
            f'<div class="pc"><img class="bi" src="bg{number}.png">'
            '<div class="t">Original &amp; source</div><a href="https://example.com">Source link</a></div></div>'
            for number in ('1', '24')) + '</body></html>'
        (self.converted / "source.html").write_text(html)
        (self.converted / "source.css").write_text('@font-face{font-family:source;src:url("f1.woff")} .pf{width:792px;height:445.5px}')
        for name in ('bg1.png', 'bg24.png', 'f1.woff'):
            (self.converted / name).write_bytes(b'original resource')
        report, fragments = MODULE.INVENTORY.inventory(html, "source.html", "pf", "pc", text_class="t")
        for file, contents in fragments.items():
            target = self.work / "html" / file
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(contents)
        (self.work / "html/inventory.json").write_text(json.dumps(report))
        self.source_hash = hashlib.sha256(b'original PDF').hexdigest()
        (self.converted / "conversion.json").write_text(json.dumps({
            "sourceFilename": "original.pdf", "sourceSha256": self.source_hash, "pageCount": 2}))
        self.inspection = {"sourceSha256": self.source_hash, "pageCount": 2, "pages": [
            {"page": page, "sourceId": f"pf{name}", "width": 792, "height": 445.5,
             "text": {"visible": 0, "hidden": 1}, "backgrounds": [{"file": f"bg{name}.png", "loaded": True}]}
            for page, name in enumerate(('1', '24'), 1)]}
        self.write_inspection()
        (self.work / "source-pages").mkdir()
        for page in range(1, 3):
            (self.work / f"source-pages/page-{page:03}.png").write_bytes(b'original capture')
        self.notes = self.root / "notes.json"
        self.notes.write_text(json.dumps({"name": "test-pdf", "title": "PDF fixture",
            "designSystem": "# Source observations\nObserved geometry; fixture safe area.\n",
            "qaConfig": {"minFontSizePx": 11, "safeArea": {"left": 0, "right": 0, "top": 0, "bottom": 0},
                         "allowedFontFallbacks": [], "requiredChrome": []},
            "pageRoles": {"1": "cover", "2": "ending"}}))

    def write_inspection(self):
        (self.converted / "inspection.json").write_text(json.dumps(self.inspection))

    def test_complete_package_passes_existing_verifier_from_unrelated_cwd(self):
        result = subprocess.run([sys.executable, str(HELPER), "--work-dir", str(self.work),
                                 "--package", str(self.package), "--notes", str(self.notes)],
                                cwd=self.root, check=True, capture_output=True, text=True)
        receipt = json.loads(result.stdout)
        self.assertEqual(receipt["status"], "PACKAGE_VALID")
        index = json.loads((self.package / "layouts/source-index.json").read_text())
        self.assertEqual(index["sourceAspectRatio"], "16:9")
        self.assertEqual(index["sourceFilename"], "original.pdf")
        self.assertEqual(index["sourceSha256"], self.source_hash)
        self.assertEqual([entry["sourcePages"] for entry in index["layouts"]], [[1], [2]])
        self.assertEqual(index["layouts"][1]["purpose"], "ending")
        self.assertTrue(all(entry["reuse"] == "reference-only" for entry in index["layouts"]))
        fragment = (self.package / "layouts/source/page-002.html").read_text()
        self.assertIn('id="pf24"', fragment)
        self.assertIn('src="../assets/pdf-source/bg24.png"', fragment)
        self.assertIn('Original &amp; source', fragment)
        self.assertIn('href="https://example.com"', fragment)
        for source in self.converted.iterdir():
            if source.suffix in ('.png', '.woff', '.css'):
                self.assertEqual((self.package / "assets/pdf-source" / source.name).read_bytes(), source.read_bytes())
        self.assertFalse((self.package / "scripts/assemble-pdf.py").exists())
        self.assertTrue((self.package / "scripts/viewport.js").is_file())
        self.assertIn('class="pdf-chrome"', fragment)
        self.assertIn('class="fit pdf-content"></div>', fragment)

    def test_wrong_source_inspection_stops_before_packaging(self):
        self.inspection["sourceSha256"] = "another PDF"
        self.write_inspection()
        with self.assertRaisesRegex(ValueError, "this PDF"):
            MODULE.assemble(self.work, self.package, self.notes)
        self.assertFalse(self.package.exists())

    def test_incomplete_original_captures_cannot_pass(self):
        (self.work / "source-pages/page-002.png").unlink()
        with self.assertRaisesRegex(ValueError, "Original ordered page images"):
            MODULE.assemble(self.work, self.package, self.notes)
        self.assertFalse((self.work / "package-build.json").exists())

    def test_existing_package_is_preserved(self):
        self.package.mkdir()
        (self.package / "keep.txt").write_text("user work")
        with self.assertRaisesRegex(ValueError, "preserved"):
            MODULE.assemble(self.work, self.package, self.notes)
        self.assertEqual((self.package / "keep.txt").read_text(), "user work")

    def test_missing_background_is_a_hard_failure(self):
        (self.converted / "bg24.png").unlink()
        with self.assertRaisesRegex(ValueError, "Missing.*bg24.png"):
            MODULE.assemble(self.work, self.package, self.notes)

    def test_resource_escape_cannot_be_copied(self):
        (self.work / "private.png").write_bytes(b'outside converter output')
        with self.assertRaisesRegex(ValueError, "out-of-directory"):
            MODULE.adapt('<div class="pf"><div class="pc"><img src="../private.png"></div></div>',
                         "page-001", self.converted)


if __name__ == "__main__":
    unittest.main()
