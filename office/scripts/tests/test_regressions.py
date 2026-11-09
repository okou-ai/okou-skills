"""Empty-result cache and automatic external-data gate regressions."""
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
import zipfile

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import office
import lo_safety

spec = importlib.util.spec_from_file_location("regression_calc", SCRIPTS.parent / "xlsx/scripts/libreoffice_recalc.py")
calc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(calc)


class RegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "control.xlsx"
        calc._write_preflight_workbook(self.path)

    def change(self, *, formula='IF(A1=19,"",1)', kind=None, cache=True, text=None):
        with zipfile.ZipFile(self.path) as source:
            parts = {name: source.read(name) for name in source.namelist()}
        part = "xl/worksheets/sheet1.xml"
        root = ET.fromstring(parts[part])
        cell = root.find(f"{calc.S}sheetData/{calc.S}row/{calc.S}c[@r='C1']")
        cell.find(f"{calc.S}f").text = formula
        if kind is not None:
            cell.set("t", kind)
        value = cell.find(f"{calc.S}v")
        if not cache:
            cell.remove(value)
        else:
            value.text = text
        parts[part] = ET.tostring(root)
        with zipfile.ZipFile(self.path, "w") as target:
            for name, content in parts.items():
                target.writestr(name, content)

    def test_computed_empty_string_cache_is_valid(self):
        self.change(kind="str", cache=True, text=None)
        formulas, missing = office.cache_snapshot(self.path)
        self.assertEqual(len(formulas), 1)
        self.assertEqual(missing, [])

    def test_absent_string_cache_and_empty_numeric_cache_are_missing(self):
        self.change(kind="str", cache=False)
        self.assertEqual(len(office.cache_snapshot(self.path)[1]), 1)
        calc._write_preflight_workbook(self.path)
        self.change(cache=True, text=None)
        self.assertEqual(len(office.cache_snapshot(self.path)[1]), 1)

    def test_automatic_external_functions_with_prefixes_are_refused(self):
        for formula in ['IMAGE("https://example.invalid/i")',
                        '_xlfn.IMAGE("https://example.invalid/i")',
                        '_xlfn._xlws.IMAGE("https://example.invalid/i")',
                        'CUBEVALUE("conn","measure")', '_xlfn.CUBEMEMBER("conn","member")',
                        'CUBESETCOUNT(A1)', '_xlfn.STOCKHISTORY("X",1,2)']:
            with self.subTest(formula=formula):
                calc._write_preflight_workbook(self.path)
                self.change(formula=formula)
                with self.assertRaises(lo_safety.SafetyError):
                    lo_safety.validate_ooxml(self.path)

    def test_invalid_runtime_override_does_not_fall_back(self):
        with patch.dict(os.environ, {"OFFICE_SOFFICE": "/nonexistent/office-test-soffice"}):
            with self.assertRaises(lo_safety.SafetyError):
                calc.find_soffice()


if __name__ == "__main__":
    unittest.main()
