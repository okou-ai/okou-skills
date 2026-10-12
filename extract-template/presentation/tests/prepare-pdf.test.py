import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


HELPER = Path(__file__).resolve().parents[1] / "scripts" / "prepare-pdf.py"
SPEC = importlib.util.spec_from_file_location("prepare_pdf", HELPER)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

HTML = '''<!DOCTYPE html><html><head><link rel="stylesheet" href="source.css"></head>
<body><div id="page-container">
<div id="pf1" class="pf w0 h0" data-page-no="1"><div class="pc pc1 w0 h0">
<img class="bi" src="bg1.png"><div class="t ff1">Cover &amp; title</div></div></div>
<div id="pf2" class="pf w0 h0" data-page-no="2"><div class="pc pc2 w0 h0">
<div class="t ff1">你好 <span>world</span></div></div></div>
</div><script src="viewer.js"></script></body></html>'''


class PreparePDFTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="pdf route ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / 'source $(literal) 名称.pdf'
        self.source.write_bytes(b"%PDF-1.4\nfixture\n%%EOF")
        self.work = self.root / "extraction work"
        self.converter = self.root / "converter with spaces"

    def converter_script(self, body):
        self.converter.write_text(f"#!{sys.executable}\nimport sys\nfrom pathlib import Path\n"
                                  "if '--version' in sys.argv:\n"
                                  " print('pdf2htmlEX test converter', file=sys.stderr)\n"
                                  " sys.exit(0)\n" + body)
        self.converter.chmod(0o755)

    def successful_converter(self, html=HTML):
        self.converter_script(
            "out = Path(sys.argv[sys.argv.index('--dest-dir') + 1])\n"
            f"(out / sys.argv[-1]).write_text({html!r})\n"
            "(out / 'source.css').write_text('.pf{width:792px;height:445.5px}')\n"
            "(out / 'bg1.png').write_bytes(b'asset')\n"
            "(out / 'viewer.js').write_text('/* viewer */')\n")

    def test_cli_hands_unchanged_pages_and_local_assets_to_html_inventory(self):
        self.successful_converter()
        original = self.source.read_bytes()
        result = subprocess.run([sys.executable, str(HELPER), "--input", str(self.source),
                                 "--work-dir", str(self.work), "--converter", str(self.converter)],
                                check=True, capture_output=True, text=True)
        receipt = json.loads(result.stdout)
        self.assertEqual(receipt["pageCount"], 2)
        self.assertEqual(receipt["sourceSha256"], hashlib.sha256(original).hexdigest())
        self.assertEqual(self.source.read_bytes(), original)
        self.assertEqual(Path(receipt["html"]).read_text(), HTML)
        inventory = json.loads(Path(receipt["inventory"]).read_text())
        self.assertEqual([entry["sourcePages"] for entry in inventory["layouts"]], [[1], [2]])
        self.assertEqual(inventory["layouts"][1]["regions"][0]["sample"], "你好 world")
        self.assertTrue(all(entry["issues"] for entry in inventory["layouts"]))
        for entry in inventory["layouts"]:
            fragment = (self.work / "html" / entry["file"]).read_text()
            self.assertIn(fragment, HTML)
        self.assertEqual((self.work / "pdf-html/bg1.png").read_bytes(), b"asset")
        self.assertEqual(inventory["resources"][1]["resolved"],
                         (self.work / "pdf-html/bg1.png").as_uri())
        self.assertFalse((self.work / "source-pages").exists())
        self.assertFalse((self.work / "upload").exists())

    def test_failure_keeps_diagnostics_without_success_receipt(self):
        self.converter_script("print('Cannot read PDF')\nsys.exit(3)\n")
        with self.assertRaises(subprocess.CalledProcessError):
            MODULE.prepare(self.source, self.work, str(self.converter))
        self.assertIn("Cannot read PDF", (self.work / "pdf-html/conversion.log").read_text())
        self.assertFalse((self.work / "pdf-html/conversion.json").exists())
        self.assertFalse((self.work / "html/inventory.json").exists())

    def test_empty_conversion_cannot_report_success(self):
        self.successful_converter("<html><body>No pages</body></html>")
        with self.assertRaises(subprocess.CalledProcessError):
            MODULE.prepare(self.source, self.work, str(self.converter))
        self.assertFalse((self.work / "pdf-html/conversion.json").exists())

    def test_existing_outputs_are_preserved_before_running_converter(self):
        for name in ("pdf-html", "html"):
            with self.subTest(name=name):
                work = self.root / name
                directory = work / name
                directory.mkdir(parents=True)
                evidence = directory / "existing.txt"
                evidence.write_text("keep")
                with self.assertRaisesRegex(ValueError, "preserving existing output"):
                    MODULE.prepare(self.source, work, "missing converter")
                self.assertEqual(evidence.read_text(), "keep")

    def test_non_pdf_input_fails_before_creating_outputs(self):
        self.source.write_text("<html>A source webpage is not the PDF input</html>")
        with self.assertRaisesRegex(ValueError, "original PDF"):
            MODULE.prepare(self.source, self.work, "missing converter")
        self.assertFalse(self.work.exists())

    def test_extracted_appimage_supplies_its_bundled_manifest_and_cmaps(self):
        executable = self.root / "app/usr/bin/pdf2htmlEX"
        executable.parent.mkdir(parents=True)
        self.converter = executable
        self.successful_converter()
        data = self.root / "app/usr/local/share/pdf2htmlEX"
        data.mkdir(parents=True)
        (data / "manifest").write_text("manifest")
        receipt = MODULE.prepare(self.source, self.work, str(executable))
        command = receipt["command"]
        self.assertEqual(command[command.index("--data-dir") + 1], str(data))
        self.assertEqual(command[command.index("--poppler-data-dir") + 1], str(data / "poppler"))

    def test_corrupted_download_is_never_executed(self):
        with patch.object(MODULE.shutil, "which", return_value=None), \
             patch.object(MODULE.platform, "system", return_value="Linux"), \
             patch.object(MODULE.platform, "machine", return_value="x86_64"), \
             patch.dict(MODULE.os.environ, {"XDG_CACHE_HOME": str(self.root / "cache")}), \
             patch.object(MODULE, "urlopen", return_value=io.BytesIO(b"corrupted archive")), \
             patch.object(MODULE.subprocess, "run") as run:
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                MODULE.converter_path()
            run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
