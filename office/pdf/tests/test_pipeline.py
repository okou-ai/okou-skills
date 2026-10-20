"""Exercise browser readiness and the actual PDF generation pipeline."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from pypdf import PdfReader

SKILL = Path(__file__).resolve().parents[1]


class PdfPipelineTests(unittest.TestCase):
    def test_missing_chromium_fails_check(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                ["bash", str(SKILL / "scripts/make.sh"), "check"],
                env={**os.environ, "PLAYWRIGHT_BROWSERS_PATH": directory},
                text=True, capture_output=True, timeout=60,
            )
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertNotIn("All dependencies satisfied", result.stdout)

    def test_pipeline_writes_cover_and_body(self):
        with tempfile.TemporaryDirectory(prefix="pdf test ") as directory:
            work = Path(directory)
            content = work / "content.json"
            content.write_text(json.dumps([
                {"type": "h1", "text": "Verified content"},
                {"type": "body", "text": "Revenue increased from 20 to 40."},
            ]))
            output = work / "report.pdf"
            result = subprocess.run(
                ["bash", str(SKILL / "scripts/make.sh"), "run",
                 "--title", "Runtime verification", "--type", "minimal",
                 "--content", str(content), "--out", str(output)],
                cwd=work, text=True, capture_output=True, timeout=120,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            reader = PdfReader(output)
            self.assertGreaterEqual(len(reader.pages), 2)
            text = "\n".join(page.extract_text() for page in reader.pages)
            self.assertIn("Revenue increased from 20 to 40", text)
            self.assertIn("Runtime verification", text)


if __name__ == "__main__":
    unittest.main()
