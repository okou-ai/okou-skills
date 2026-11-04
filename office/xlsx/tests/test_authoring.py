"""Behavioral tests of explicit high-level authoring primitives, not model quality."""
from pathlib import Path
from copy import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
import xml.etree.ElementTree as ET

from openpyxl import Workbook, load_workbook

SKILL = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("xlsx_authoring", SKILL / "scripts/xlsx_authoring.py")
authoring = importlib.util.module_from_spec(spec)
spec.loader.exec_module(authoring)
S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


class AuthoringTests(unittest.TestCase):
    def test_roles_and_formats_are_assigned_together_and_survive_reopen(self):
        wb = Workbook()
        ws = wb.active
        ws["A1"] = .05
        ws["A2"] = "=A1*2"
        ws["A3"] = "=Other!A1"
        authoring.style_value(ws["A1"], role="input", kind="percent")
        authoring.style_value(ws["A2"], role="same_sheet", kind="percent")
        authoring.style_value(ws["A3"], role="cross_sheet", kind="amount")
        font = copy(ws["A2"].font)
        font.bold = True
        ws["A2"].font = font
        authoring.style_value(ws["A2"], role="same_sheet", kind="percent")
        self.assertTrue(ws["A2"].font.bold)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "values.xlsx"
            wb.save(path)
            reopened = load_workbook(path, data_only=False)
            sheet = reopened.active
            self.assertEqual(sheet["A1"].font.color.rgb, "FF0000FF")
            self.assertEqual(sheet["A2"].font.color.rgb, "FF000000")
            self.assertEqual(sheet["A3"].font.color.rgb, "FF008000")
            self.assertEqual(sheet["A2"].value, "=A1*2")
            self.assertIn("%", sheet["A2"].number_format)
            self.assertNotIn("%", sheet["A3"].number_format)
            reopened.close()

    def test_library_workbook_is_actually_inspected_by_style_audit(self):
        wb = Workbook()
        ws = wb.active
        ws["A1"], ws["A2"] = .05, "=A1*2"
        authoring.style_value(ws["A1"], role="input", kind="percent")
        authoring.style_value(ws["A2"], role="same_sheet", kind="percent")
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "producer-integration.xlsx"
            for broken in (False, True):
                if broken:
                    font = copy(ws["A2"].font)
                    font.color = "FF0000FF"
                    ws["A2"].font = font
                wb.save(path)
                result = subprocess.run([sys.executable, str(SKILL / "scripts/style_audit.py"),
                                         str(path), "--json"], capture_output=True, text=True, timeout=10)
                payload = json.loads(result.stdout)
                self.assertEqual(payload["summary"]["total_cells_inspected"], 2)
                self.assertEqual(payload["summary"]["formula_cells"], 1)
                self.assertEqual(result.returncode, 1 if broken else 0, payload)
                self.assertEqual([x["type"] for x in payload["violations"]],
                                 ["formula_cell_blue_font"] if broken else [])

    def test_rejects_incorrect_roles_without_styling_the_cell(self):
        ws = Workbook().active
        ws["A1"], ws["A2"] = 5, "=1+1"
        for address, role, kind in [("A1", "cross_sheet", "amount"), ("A2", "input", "amount"),
                                    ("A1", "input", "unknown"), ("A1", "unknown", "amount")]:
            with self.subTest(address=address, role=role, kind=kind):
                before = ws[address].style_id
                with self.assertRaises(ValueError):
                    authoring.style_value(ws[address], role=role, kind=kind)
                self.assertEqual(ws[address].style_id, before)

    def test_bands_have_actual_span_height_and_do_not_destroy_existing_content(self):
        ws = Workbook().active
        authoring.report_band(ws, "B4:F4", "Quarter outlook", level="title")
        self.assertIn("B4:F4", {str(x) for x in ws.merged_cells.ranges})
        self.assertEqual(ws["B4"].value, "Quarter outlook")
        self.assertEqual(ws.row_dimensions[4].height, 26)
        self.assertEqual(ws["F4"].fill.fgColor.rgb, "FF135B44")
        ws["C7"] = "keep"
        for area in ("B7:F7", "B4:F4", "B8:F9"):
            with self.assertRaises(ValueError):
                authoring.report_band(ws, area, "Invalid")
        self.assertEqual(ws["C7"].value, "keep")

    def test_gray_label_header_is_not_applied_to_formula_outputs(self):
        ws = Workbook().active
        ws.append(["Period", "Revenue"])
        authoring.table_header(ws, "A1:B1")
        self.assertEqual(ws["B1"].fill.fgColor.rgb, "FFF2F2F2")
        self.assertEqual(ws["B1"].font.color.rgb, "FF404040")
        ws["A2"] = "=1+1"
        with self.assertRaises(ValueError):
            authoring.table_header(ws, "A2:B2")
        self.assertEqual(ws["A2"].value, "=1+1")

    def test_rejects_unbounded_reversed_or_out_of_sheet_ranges(self):
        ws = Workbook().active
        for area in ("A:C", "3:4", "D4:B4", "A0:B2", "A1:XFE2"):
            with self.subTest(area=area):
                with self.assertRaises(ValueError):
                    authoring.report_page(ws, area)
                with self.assertRaises(ValueError):
                    authoring.report_band(ws, area, "Invalid")

    def test_report_page_serializes_area_and_width_fit_without_fixed_page_count(self):
        wb = Workbook()
        ws = wb.active
        authoring.report_page(ws, "B2:J50", paper_size=ws.PAPERSIZE_A4)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "layout.xlsx"
            wb.save(path)
            with zipfile.ZipFile(path) as z:
                sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
                book = ET.fromstring(z.read("xl/workbook.xml"))
            setup = sheet.find(f"{S}pageSetup")
            self.assertEqual(setup.get("fitToWidth"), "1")
            self.assertEqual(setup.get("fitToHeight"), "0")
            self.assertEqual(sheet.find(f"{S}sheetPr/{S}pageSetUpPr").get("fitToPage"), "1")
            self.assertFalse(ws.sheet_view.showGridLines)
            area = next(x for x in book.find(f"{S}definedNames") if x.get("name") == "_xlnm.Print_Area")
            self.assertIn("$B$2:$J$50", area.text)
            children = [x.tag.rsplit("}", 1)[-1] for x in sheet]
            self.assertLess(children.index("sheetViews"), children.index("sheetData"))


if __name__ == "__main__":
    unittest.main()
