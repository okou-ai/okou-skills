"""Execute the documented validation example, not a GUI or quality benchmark."""
from pathlib import Path
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET
from zipfile import ZipFile

from openpyxl import Workbook, load_workbook

SKILL = Path(__file__).resolve().parents[1]
GUIDE = SKILL / "references/common/data-and-inputs.md"
S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


class InputGuidanceTests(unittest.TestCase):
    def test_exact_documented_example_saves_enabled_stop_rule_without_rewriting_cells(self):
        blocks = re.findall(r"```python\n(.*?)\n```", GUIDE.read_text(), re.S)
        self.assertEqual(len(blocks), 1)
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Synthetic inputs"
        sheet["A1"] = "Existing content"
        sheet["B2"] = "001234"
        sheet["D2"] = "=SUM(J4:J6)"
        for row, value in enumerate((2, 3, 4), start=4):
            sheet.cell(row, 10, value)
        before = {cell.coordinate:cell.value for row in sheet for cell in row if cell.value is not None}
        context = dict(ws=sheet, lower_bound=2, upper_bound=4,
                       error_title="Invalid level", error_message="Choose a whole number from 2 to 4.",
                       input_range="J4:J6")
        exec(compile(blocks[0], str(GUIDE), "exec"), context)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "validation-example.xlsx"
            workbook.save(output)
            reopened = load_workbook(output, data_only=False)
            self.assertEqual(reopened.sheetnames, ["Synthetic inputs"])
            actual = reopened.active
            self.assertEqual({cell.coordinate:cell.value for row in actual for cell in row
                              if cell.value is not None}, before)
            rules = actual.data_validations.dataValidation
            self.assertEqual(len(rules), 1)
            rule = rules[0]
            self.assertEqual(str(rule.sqref), "J4:J6")
            self.assertEqual((rule.type,rule.operator,rule.formula1,rule.formula2),
                             ("whole","between","2","4"))
            self.assertTrue(rule.showErrorMessage)
            self.assertFalse(rule.allowBlank)
            self.assertEqual(rule.errorStyle,"stop")
            self.assertEqual(rule.errorTitle,context["error_title"])
            self.assertEqual(rule.error,context["error_message"])
            with ZipFile(output) as archive:
                root = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
            saved = root.find(f"{S}dataValidations/{S}dataValidation")
            self.assertEqual(saved.get("showErrorMessage"),"1")
            self.assertEqual(saved.get("errorStyle"),"stop")
            self.assertEqual(saved.get("allowBlank"),"0")

    def test_types_missing_values_narrative_and_domain_limits_are_distinct(self):
        text = " ".join(GUIDE.read_text().split())
        for requirement in ("leading zeros", "decimal fractions", "date serial",
                            "Keep missing, invalid, unavailable and zero states distinct",
                            "one identifiable source cell or named range",
                            "current scenario must follow the inputs",
                            "Do not invent business bounds", "blanket `IFERROR(...,0)`",
                            "not a GUI entry test", "Save pending edits before a different program"):
            self.assertIn(requirement,text)

    def test_guidance_does_not_imply_pivot_support_or_impose_a_batch_size(self):
        text = " ".join(GUIDE.read_text().split())
        self.assertIn("do not promise complete pivot, slicer or connection support",text)
        self.assertIn("not a fixed universal operation count",text)
        self.assertIn("Preserve existing controls during narrow edits",text)
        self.assertIn("not permission to add validation, helper sheets or formatting",text)


if __name__ == "__main__":
    unittest.main()
