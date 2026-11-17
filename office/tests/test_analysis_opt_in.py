"""Optional native checks for the explicit, legacy DataFrame analysis route."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


READER = Path(__file__).resolve().parents[1] / "xlsx/scripts/xlsx_reader.py"
HAS_ANALYSIS = bool(importlib.util.find_spec("pandas") and importlib.util.find_spec("openpyxl"))


@unittest.skipUnless(HAS_ANALYSIS, "optional pandas/openpyxl are not installed")
class AnalysisOptInTests(unittest.TestCase):
    def setUp(self):
        work = tempfile.TemporaryDirectory(prefix="office-analysis-")
        self.addCleanup(work.cleanup)
        self.work = Path(work.name)

    def analyze(self, source, *options):
        before = hashlib.sha256(source.read_bytes()).hexdigest()
        result = subprocess.run([sys.executable, str(READER), str(source), *options, "--json"],
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                                cwd=self.work, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), before)
        return json.loads(result.stdout)

    def test_explicit_xlsx_analysis_and_quality_keep_the_selected_sheet(self):
        from openpyxl import Workbook
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Sales"
        sheet.append(["Item", "Amount"])
        sheet.append(["A", 10])
        sheet.append(["B", 20])
        workbook.create_sheet("Unrelated").append([999])
        source = self.work / "sales.xlsx"
        workbook.save(source)
        analysis = self.analyze(source, "--analyze", "--sheet", "Sales")
        self.assertEqual(set(analysis["structure"]), {"Sales"})
        self.assertEqual(analysis["structure"]["Sales"]["shape"]["rows"], 2)
        self.assertEqual(analysis["stats"]["Sales"]["Amount"]["mean"], 15)
        quality = self.analyze(source, "--quality", "--sheet", "Sales")
        self.assertEqual(set(quality["quality"]), {"Sales"})
        self.assertEqual(quality["stats"], {})

    def test_explicit_csv_analysis_retains_numeric_statistics(self):
        source = self.work / "records.csv"
        source.write_text("Item,Amount\nA,10\nB,20\n", encoding="utf-8")
        analysis = self.analyze(source, "--analyze")
        self.assertEqual(analysis["structure"]["records"]["shape"]["rows"], 2)
        self.assertEqual(analysis["stats"]["records"]["Amount"]["mean"], 15)


if __name__ == "__main__":
    unittest.main()
