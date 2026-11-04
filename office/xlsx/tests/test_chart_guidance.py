"""Execute the documented native-chart example; not application/visual validation."""
from io import BytesIO
from pathlib import Path
import re
import unittest
from zipfile import ZipFile
import xml.etree.ElementTree as ET

from openpyxl import Workbook, load_workbook

SKILL = Path(__file__).resolve().parents[1]
C = {"c": "http://schemas.openxmlformats.org/drawingml/2006/chart"}
S = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


class ChartGuidanceExampleTests(unittest.TestCase):
    def test_exact_example_creates_range_linked_chart_without_rewriting_model(self):
        reference = (SKILL / "references/common/charts.md").read_text()
        examples = re.findall(r"```python\n(.*?)\n```", reference, re.S)
        self.assertEqual(len(examples), 1)
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Analysis"
        # Synthetic formula outputs; no claim that openpyxl calculates these.
        worksheet.append(["Month", "Revenue", "Cost"])
        worksheet.append(["Jan", "=100", "=70"])
        worksheet.append(["Feb", "=120", "=80"])
        worksheet.append(["Total", "=SUM(B2:B3)", "=SUM(C2:C3)"])
        original = {cell.coordinate: cell.value for row in worksheet for cell in row}
        scope = {
            "ws": worksheet, "question_title": "Synthetic monthly trend", "units": "CNY",
            "first_metric_col": 2, "last_metric_col": 3, "header_row": 1,
            "last_data_row": 3, "period_col": 1, "chart_width_cm": 16,
            "chart_height_cm": 9, "planned_anchor": "E2",
        }
        exec(compile(examples[0], str(SKILL / "references/common/charts.md"), "exec"), scope)
        self.assertEqual(workbook.sheetnames, ["Analysis"])
        self.assertEqual({cell.coordinate: cell.value for row in worksheet for cell in row}, original)
        output = BytesIO()
        workbook.save(output)
        with ZipFile(BytesIO(output.getvalue())) as package:
            chart_parts = [name for name in package.namelist()
                           if re.fullmatch(r"xl/charts/chart\d+\.xml", name)]
            self.assertEqual(chart_parts, ["xl/charts/chart1.xml"])
            chart = ET.fromstring(package.read(chart_parts[0]))
            self.assertIsNotNone(chart.find(".//c:lineChart", C))
            series = chart.findall(".//c:ser", C)
            self.assertEqual(len(series), 2)
            self.assertEqual([item.find("c:val/c:numRef/c:f", C).text for item in series],
                             ["'Analysis'!$B$2:$B$3", "'Analysis'!$C$2:$C$3"])
            self.assertEqual([item.find("c:cat/c:numRef/c:f", C).text for item in series],
                             ["'Analysis'!$A$2:$A$3"] * 2)
            self.assertEqual([item.find("c:tx/c:strRef/c:f", C).text for item in series],
                             ["'Analysis'!B1", "'Analysis'!C1"])
            sheet = ET.fromstring(package.read("xl/worksheets/sheet1.xml"))
            self.assertEqual(len(sheet.findall(".//m:f", S)), 6)
        reopened = load_workbook(BytesIO(output.getvalue()), data_only=False)
        self.assertEqual(reopened.active["B4"].value, "=SUM(B2:B3)")
        self.assertEqual(reopened.active["C3"].value, "=80")
        reopened.close()
        workbook.close()


if __name__ == "__main__":
    unittest.main()
