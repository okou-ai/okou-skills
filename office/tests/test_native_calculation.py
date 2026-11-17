"""Optional real Calc check; the native CI job installs the Calc component."""

import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HELPER = Path(__file__).resolve().parents[1] / "xlsx/scripts/libreoffice_recalc.py"


@unittest.skipUnless(importlib.util.find_spec("openpyxl"), "optional openpyxl is not installed")
class NativeCalculationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("native_calc_test_helper", HELPER)
        helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helper)
        converter = helper.find_soffice()
        if not converter:
            raise unittest.SkipTest("LibreOffice is not installed")
        diagnostic = helper.calc_component_diagnostic(converter)
        if diagnostic:
            # Do not replay a known unavailable Calc control on a Writer-only host.
            raise unittest.SkipTest(diagnostic)

    def test_success_receipt_reuses_control_but_not_candidate_results(self):
        from openpyxl import Workbook, load_workbook
        with tempfile.TemporaryDirectory(prefix="office-native-calc-") as directory:
            work = Path(directory)
            receipt = work / "control.json"
            common = ["--receipt", str(receipt), "--task-id", work.name, "--timeout", "45"]

            def invoke(*arguments):
                result = subprocess.run([sys.executable, str(HELPER), *arguments, *common],
                                        cwd=work, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                                        capture_output=True, text=True, timeout=90)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                return result.stdout

            self.assertIn("Preflight PASSED", invoke("--preflight"))
            self.assertTrue(receipt.is_file())
            self.assertIn("Preflight REUSED", invoke("--preflight"))
            for value in (40, 50):
                workbook = Workbook()
                sheet = workbook.active
                sheet.title = "Preflight"
                sheet["A1"], sheet["B1"], sheet["C1"] = value, 2, "=SUM(A1:B1)"
                source = work / f"source-{value}.xlsx"
                output = work / f"calculated-{value}.xlsx"
                workbook.save(source)
                before = hashlib.sha256(source.read_bytes()).hexdigest()
                invoke(str(source), str(output))
                self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), before)
                formulas = load_workbook(output, data_only=False)
                cached = load_workbook(output, data_only=True)
                try:
                    self.assertEqual(formulas["Preflight"]["C1"].value, "=SUM(A1:B1)")
                    self.assertEqual(cached["Preflight"]["C1"].value, value + 2)
                finally:
                    formulas.close()
                    cached.close()


if __name__ == "__main__":
    unittest.main()
