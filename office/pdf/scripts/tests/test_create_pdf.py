"""Regression checks through the standalone PDF command."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image
from pypdf import PdfReader, PdfWriter


SCRIPTS = Path(__file__).resolve().parents[1]


class CreatePdfTests(unittest.TestCase):
    def setUp(self):
        work = tempfile.TemporaryDirectory(prefix="pdf-create-")
        self.addCleanup(work.cleanup)
        self.work = Path(work.name)
        self.output = self.work / "report.pdf"
        self.old_pdf = b"existing report"
        self.output.write_bytes(self.old_pdf)

    def create(self, blocks=None, env=None, **options):
        args = ["bash", str(SCRIPTS / "make.sh"), "run", "--out", str(self.output)]
        if blocks is not None:
            content = self.work / "content.json"
            content.write_text(json.dumps(blocks, ensure_ascii=False), encoding="utf-8")
            args.extend(["--content", str(content)])
        for key, value in options.items():
            args.extend(["--" + key, value])
        return subprocess.run(args, cwd=self.work, capture_output=True, text=True, env=env, timeout=45)

    def assert_build_fails(self, result, diagnostic):
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(diagnostic, result.stderr)
        self.assertNotIn("Rendering cover", result.stdout)
        self.assertEqual(self.output.read_bytes(), self.old_pdf)

    def test_rejects_missing_content(self):
        self.assert_build_fails(self.create(), "requires --content")

    def test_rejects_empty_content(self):
        self.assert_build_fails(self.create([]), "nonempty array")

    def test_rejects_unknown_block(self):
        result = self.create([{"type": "body", "text": "Valid prose"}, {"type": "paragraph", "text": "Must survive"}])
        self.assert_build_fails(result, "Content block 2: unsupported type 'paragraph'")

    def test_rejects_missing_and_invalid_images(self):
        (self.work / "invalid.png").write_text("invalid image")
        for name, reason in (("missing.png", "Image not found"), ("invalid.png", "Cannot read image")):
            with self.subTest(name=name):
                result = self.create([{"type": "figure", "src": name, "caption": "Required figure"}])
                self.assert_build_fails(result, f"Content block 1 (figure): {reason}")

    def test_rejects_a_chart_without_data(self):
        self.assert_build_fails(self.create([{"type": "chart"}]), "chart requires labels")

    def test_reports_unavailable_cjk_font(self):
        env = {**os.environ, "PDF_CJK_FONT": str(self.work / "missing.ttf")}
        result = self.create([{"type": "body", "text": "中文正文"}], env=env)
        self.assert_build_fails(result, "PDF_CJK_FONT")

    def test_mixed_report_contains_embedded_text_and_image(self):
        Image.new("RGB", (40, 20), "red").save(self.work / "figure.png")
        result = self.create([
            {"type": "h1", "text": "中文标题"},
            {"type": "body", "text": '<font name="Helvetica">中文报告案例</font> <b>Mixed body</b>'},
            {"type": "bullet", "text": "项目清单"},
            {"type": "table", "headers": ["名称", "数量"], "rows": [["测试行", 12]]},
            {"type": "figure", "path": "figure.png", "caption": "图表说明"},
        ], title="中文报告", author="样例作者")
        self.assertEqual(result.returncode, 0, result.stderr)
        reader = PdfReader(self.output)
        self.assertEqual(len(reader.pages), 2)
        text = reader.pages[1].extract_text()
        for expected in ("中文标题", "中文报告案例", "Mixed body", "项目清单", "测试行", "图表说明", "样例作者"):
            self.assertIn(expected, text)
        self.assertEqual(len(reader.pages[1].images), 1)
        fonts = reader.pages[1]["/Resources"]["/Font"].values()
        embedded = [ref.get_object().get("/FontDescriptor") for ref in fonts]
        self.assertTrue(any(descriptor and "/FontFile2" in descriptor for descriptor in embedded))
        self.assertEqual(list(self.work.glob(".pdf-*.tmp")), [])

    def test_merge_rejects_empty_body_without_replacing_existing_file(self):
        cover = self.work / "cover.pdf"
        body = self.work / "body.pdf"
        writer = PdfWriter()
        writer.add_blank_page(width=200, height=200)
        writer.write(cover)
        PdfWriter().write(body)
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "merge.py"), "--cover", str(cover),
             "--body", str(body), "--out", str(self.output)],
            capture_output=True, text=True, timeout=10,
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("at least one body page", result.stderr)
        self.assertEqual(self.output.read_bytes(), self.old_pdf)


if __name__ == "__main__":
    unittest.main()
