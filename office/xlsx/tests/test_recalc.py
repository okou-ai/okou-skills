"""Check real formula caches and prevent false success from unchanged input."""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

SKILL = Path(__file__).resolve().parents[1]
S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


class RecalculationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="xlsx test ")
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        tree = self.work / "tree"
        shutil.copytree(SKILL / "templates/minimal_xlsx", tree)
        sheet = tree / "xl/worksheets/sheet1.xml"
        root = ET.parse(sheet)
        data = root.find(f"{S}sheetData")
        row = ET.SubElement(data, f"{S}row", r="1")
        cell = ET.SubElement(row, f"{S}c", r="A1")
        ET.SubElement(cell, f"{S}v").text = "20"
        cell = ET.SubElement(row, f"{S}c", r="B1")
        ET.SubElement(cell, f"{S}f").text = "A1*2"
        ET.SubElement(cell, f"{S}v").text = "999"
        root.write(sheet, encoding="utf-8", xml_declaration=True)
        self.source = self.work / "input.xlsx"
        subprocess.run([sys.executable, str(SKILL / "scripts/xlsx_pack.py"),
                        str(tree), str(self.source)], check=True, capture_output=True)
        self.before = hashlib.sha256(self.source.read_bytes()).hexdigest()

    def recalc(self, output, **kwargs):
        return subprocess.run(
            [sys.executable, str(SKILL / "scripts/libreoffice_recalc.py"),
             str(self.source), str(output)], cwd=self.work,
            capture_output=True, text=True, timeout=90, **kwargs,
        )

    def test_real_calc_updates_cached_value_and_preserves_source(self):
        output = self.work / "recalculated.xlsx"
        result = self.recalc(output)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(hashlib.sha256(self.source.read_bytes()).hexdigest(), self.before)
        with zipfile.ZipFile(output) as package:
            root = ET.fromstring(package.read("xl/worksheets/sheet1.xml"))
        cell = root.find(f".//{S}c[@r='B1']")
        self.assertEqual(float(cell.find(f"{S}v").text), 40)
        self.assertIsNotNone(cell.find(f"{S}f"))
        checked = subprocess.run([sys.executable, str(SKILL / "scripts/formula_check.py"),
                                  str(output)], capture_output=True, text=True)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)

    @unittest.skipIf(os.name == "nt", "POSIX process fixture")
    def test_exit_zero_without_new_output_does_not_copy_original(self):
        binary = self.work / "soffice"
        binary.write_text("#!/bin/sh\nexit 0\n")
        binary.chmod(0o755)
        output = self.work / "should-not-exist.xlsx"
        result = self.recalc(output, env={**os.environ, "PATH": str(self.work)})
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(output.exists())
        self.assertEqual(hashlib.sha256(self.source.read_bytes()).hexdigest(), self.before)


if __name__ == "__main__":
    unittest.main()
