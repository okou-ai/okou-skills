"""Focused style diagnostics against synthetic OOXML; no external workbooks needed."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "style_audit.py"
SPEC = importlib.util.spec_from_file_location("style_audit", SCRIPT)
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)
NS = audit.NS
S = audit.NSP


def make_styles(fonts=None, xfs=None, num_fmts=None):
    """Build well-formed style parts with independently chosen workbook-local IDs."""
    fonts = ['<color rgb="FF0000FF"/>'] if fonts is None else fonts
    xfs = [(1, 0)] if xfs is None else xfs  # (numFmtId, fontId)
    num_fmts = {} if num_fmts is None else num_fmts
    root = ET.Element(f"{S}styleSheet")
    formats = ET.SubElement(root, f"{S}numFmts", count=str(len(num_fmts)))
    for fmt_id, code in num_fmts.items():
        ET.SubElement(formats, f"{S}numFmt", numFmtId=str(fmt_id), formatCode=code)
    font_list = ET.SubElement(root, f"{S}fonts", count=str(len(fonts)))
    for content in fonts:
        font_list.append(ET.fromstring(f'<font xmlns="{NS}">{content}</font>'))
    fills = ET.SubElement(root, f"{S}fills", count="2")
    for pattern in ("none", "gray125"):
        fill = ET.SubElement(fills, f"{S}fill")
        ET.SubElement(fill, f"{S}patternFill", patternType=pattern)
    borders = ET.SubElement(root, f"{S}borders", count="1")
    ET.SubElement(borders, f"{S}border")
    bases = ET.SubElement(root, f"{S}cellStyleXfs", count="1")
    ET.SubElement(bases, f"{S}xf", numFmtId="0", fontId="0", fillId="0", borderId="0")
    styles = ET.SubElement(root, f"{S}cellXfs", count=str(len(xfs)))
    for num_fmt_id, font_id in xfs:
        ET.SubElement(styles, f"{S}xf", numFmtId=str(num_fmt_id), fontId=str(font_id),
                      fillId="0", borderId="0", xfId="0")
    return ET.tostring(root, encoding="utf-8")


def make_sheet(cells='<c r="A1" s="0"><v>8</v></c>'):
    return (f'<worksheet xmlns="{NS}"><sheetData><row r="1">'
            f'{cells}</row></sheetData></worksheet>').encode()


def run_audit(styles=None, sheet=None):
    return audit._audit(make_styles() if styles is None else styles,
                        [("Synthetic", make_sheet() if sheet is None else sheet)])


def types(items):
    return [item["type"] for item in items]


class StyleDiagnosticTests(unittest.TestCase):
    def test_valid_mixed_cells_and_summary_counts(self):
        styles = make_styles(
            fonts=['<color rgb="0000FF"/>', '<color rgb="FF000000"/>',
                   '<color rgb="00008000"/>'],
            xfs=[(1, 0), (1, 1), (0, 2), (165, 0)], num_fmts={165: "0.0%"})
        sheet = make_sheet(
            '<c r="A1" s="0"><v>2024</v></c>'
            '<c r="B1" s="1"><f>A1+1</f><v>2025</v></c>'
            '<c r="C1" s="2"><f>Other!A1</f><v>8</v></c>'
            '<c r="D1" s="3"><v>0.08</v></c>'
            '<c r="E1" t="inlineStr"><is><t>Label</t></is></c>'
            '<c r="F1"><f>B1+1</f><v>2026</v></c>')
        result = run_audit(styles, sheet)
        self.assertEqual(result["violations"], [])
        self.assertEqual(result["warnings"], [])
        self.assertEqual(result["summary"], {
            "total_cells_inspected": 6, "formula_cells": 3, "input_cells": 2,
            "violations": 0, "warnings": 0})

    def test_omitted_pattern_type_is_valid_none_but_absent_pattern_fill_is_not(self):
        root = ET.fromstring(make_styles())
        fill = root.find(f"{S}fills/{S}fill")
        pattern = fill.find(f"{S}patternFill")
        pattern.attrib.pop("patternType")
        self.assertEqual(run_audit(ET.tostring(root))["violations"], [])
        fill.remove(pattern)
        self.assertIn("fills_0_corrupted", types(run_audit(ET.tostring(root))["violations"]))

    def test_blue_formula_recognizes_ff_00_and_six_digit_rgb_once(self):
        for rgb in ("FF0000FF", "000000FF", "0000FF", "ff0000fF"):
            with self.subTest(rgb=rgb):
                result = run_audit(make_styles(fonts=[f'<color rgb="{rgb}"/>']),
                                   make_sheet('<c r="A1" s="0"><f>1+1</f><v>2</v></c>'))
                self.assertEqual(types(result["violations"]), ["formula_cell_blue_font"])
                self.assertEqual(result["summary"]["formula_cells"], 1)

    def test_black_input_recognizes_ff_00_and_six_digit_rgb(self):
        for rgb in ("FF000000", "00000000", "000000"):
            with self.subTest(rgb=rgb):
                result = run_audit(make_styles(fonts=[f'<color rgb="{rgb}"/>']))
                self.assertEqual(types(result["warnings"]), ["numeric_input_may_lack_blue"])

    def test_green_rgb_comparison_normalizes_supported_forms(self):
        for rgb in ("FF008000", "00008000", "008000"):
            with self.subTest(rgb=rgb):
                font = audit._parse_styles(make_styles(fonts=[f'<color rgb="{rgb}"/>']))["fonts"][0]
                self.assertTrue(audit._is_green_font(font))
                self.assertFalse(audit._is_black_font(font))
                self.assertFalse(audit._is_blue_font(font))

    def test_theme_indexed_missing_or_malformed_rgb_is_not_guessed(self):
        contents = ['<color theme="0"/>', '<color theme="1"/>', '<color theme="7"/>',
                    '<color indexed="8"/>', '<color auto="1"/>', '',
                    '<color rgb="#000000"/>', '<color rgb="GG000000"/>',
                    '<color rgb="00000"/>', '<color rgb="FF0000000"/>']
        for content in contents:
            with self.subTest(font=content):
                result = run_audit(make_styles(fonts=[content]))
                self.assertEqual(result["warnings"], [])
                font = audit._parse_styles(make_styles(fonts=[content]))["fonts"][0]
                self.assertFalse(audit._is_black_font(font))
                self.assertFalse(audit._is_blue_font(font))
                self.assertFalse(audit._is_green_font(font))

    def test_false_bold_does_not_suppress_black_input_warning(self):
        for bold in ('<b val="0"/>', '<b val="false"/>'):
            with self.subTest(bold=bold):
                styles = make_styles(fonts=[f'<color rgb="FF000000"/>{bold}'])
                self.assertFalse(audit._parse_styles(styles)["fonts"][0]["bold"])
                self.assertEqual(types(run_audit(styles)["warnings"]),
                                 ["numeric_input_may_lack_blue"])

    def test_absent_and_true_bold_flags(self):
        for bold, expected in (('', False), ('<b/>', True),
                               ('<b val="1"/>', True), ('<b val="true"/>', True)):
            with self.subTest(bold=bold):
                styles = make_styles(fonts=[f'<color rgb="FF000000"/>{bold}'])
                self.assertEqual(audit._parse_styles(styles)["fonts"][0]["bold"], expected)
                self.assertEqual(len(run_audit(styles)["warnings"]), 0 if expected else 1)

    def test_custom_format_ids_are_local_to_each_workbook(self):
        for fmt_id in (164, 165, 167, 168, 170, 300):
            for code, percent, comma in (("0", False, False), ("0.0%", True, False),
                                          ("#,##0", False, True)):
                with self.subTest(fmt_id=fmt_id, code=code):
                    self.assertEqual(audit._fmt_is_percent(fmt_id, {fmt_id: code}), percent)
                    self.assertEqual(audit._fmt_is_comma(fmt_id, {fmt_id: code}), comma)

    def test_undefined_custom_formats_have_no_hardcoded_semantics(self):
        for fmt_id in (164, 165, 167, 168, 170, 300):
            with self.subTest(fmt_id=fmt_id):
                self.assertFalse(audit._fmt_is_percent(fmt_id, {}))
                self.assertFalse(audit._fmt_is_comma(fmt_id, {}))

    def test_builtin_percent_and_comma_formats_still_work(self):
        for fmt_id in (9, 10):
            self.assertTrue(audit._fmt_is_percent(fmt_id, {}))
        for fmt_id in (3, 4):
            self.assertTrue(audit._fmt_is_comma(fmt_id, {}))

    def test_custom_format_collisions_affect_actual_cell_diagnostics(self):
        for fmt_id, code, value, violations, warnings in (
                (165, "0", "8", [], []),
                (170, "0", "8", [], []),
                (167, "0", "2024", [], []),
                (168, "0", "2024", [], []),
                (165, "#,##0", "2024", ["year_with_comma_format"], []),
                (167, "0.0%", "8", [], ["percent_value_gt_1"])):
            with self.subTest(fmt_id=fmt_id, code=code):
                result = run_audit(make_styles(xfs=[(fmt_id, 0)], num_fmts={fmt_id: code}),
                                   make_sheet(f'<c r="A1" s="0"><v>{value}</v></c>'))
                self.assertEqual(types(result["violations"]), violations)
                self.assertEqual(types(result["warnings"]), warnings)

    def test_existing_count_and_required_fill_checks(self):
        root = ET.fromstring(make_styles())
        for name in ("fonts", "fills", "cellXfs"):
            root.find(f"{S}{name}").set("count", "99")
        fills = root.find(f"{S}fills")
        fills.remove(fills[1])
        result = run_audit(ET.tostring(root))
        self.assertEqual(types(result["violations"]).count("count_mismatch"), 3)
        self.assertIn("missing_required_fills", types(result["violations"]))

    def test_corrupted_required_fill_patterns(self):
        root = ET.fromstring(make_styles())
        for fill in root.find(f"{S}fills"):
            fill.find(f"{S}patternFill").set("patternType", "solid")
        self.assertEqual(types(run_audit(ET.tostring(root))["violations"]),
                         ["fills_0_corrupted", "fills_1_corrupted"])

    def test_out_of_range_and_negative_style_indices_are_reported(self):
        for index in ("1", "-1"):
            with self.subTest(index=index):
                result = run_audit(sheet=make_sheet(f'<c r="A1" s="{index}"><v>8</v></c>'))
                self.assertEqual(types(result["violations"]), ["style_index_out_of_range"])

    def test_malformed_style_index_is_reported_not_silently_skipped(self):
        result = run_audit(sheet=make_sheet('<c r="A1" s="oops"><v>8</v></c>'))
        self.assertEqual(types(result["violations"]), ["invalid_style_index"])

    def test_out_of_range_and_negative_font_indices_are_reported(self):
        for index in (1, -1):
            with self.subTest(index=index):
                result = run_audit(make_styles(xfs=[(1, index)]))
                self.assertEqual(types(result["violations"]), ["font_index_out_of_range"])

    def test_nonfinite_cached_values_do_not_crash_year_heuristic(self):
        for value in ("inf", "-inf", "NaN", "not-a-number"):
            with self.subTest(value=value):
                result = run_audit(sheet=make_sheet(f'<c r="A1" s="0"><v>{value}</v></c>'))
                self.assertEqual(result["violations"], [])


class StyleAuditCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="style audit test ")
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)

    def write_workbook(self, styles=None, sheet=None, packed=True,
                       relationship_target="worksheets/sheet1.xml"):
        parts = {
            "[Content_Types].xml": (
                '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                '<Default Extension="xml" ContentType="application/xml"/>'
                '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
                '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                '</Types>'),
            "_rels/.rels": (
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
                '</Relationships>'),
            "xl/styles.xml": make_styles() if styles is None else styles,
            "xl/worksheets/sheet1.xml": make_sheet() if sheet is None else sheet,
            "xl/workbook.xml": (
                f'<workbook xmlns="{NS}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                '<sheets><sheet name="Synthetic" sheetId="1" r:id="rId1"/></sheets></workbook>'),
            "xl/_rels/workbook.xml.rels": (
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                f'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="{relationship_target}"/>'
                '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
                '</Relationships>'),
        }
        if packed:
            target = self.work / "synthetic.xlsx"
            with zipfile.ZipFile(target, "w") as package:
                for name, content in parts.items():
                    package.writestr(name, content)
        else:
            target = self.work / "unpacked"
            for name, content in parts.items():
                path = target / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content.encode() if isinstance(content, str) else content)
        return target

    def cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                              capture_output=True, text=True, timeout=10)

    def test_valid_packed_and_unpacked_fixtures_with_narrow_success_message(self):
        for packed in (True, False):
            with self.subTest(packed=packed):
                result = self.cli(self.write_workbook(packed=packed))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("No violations detected by implemented style checks", result.stdout)
                self.assertNotIn("Financial formatting is compliant", result.stdout)
                self.assertIn("no business, visual, or full financial-role validation", result.stdout)
                self.assertEqual(result.stderr, "")

    def test_absolute_worksheet_targets_are_audited_in_packed_and_unpacked_files(self):
        for packed in (True, False):
            with self.subTest(packed=packed):
                target = self.write_workbook(
                    sheet=make_sheet('<c r="A1" s="0"><f>1+1</f><v>2</v></c>'),
                    packed=packed, relationship_target="/xl/worksheets/sheet1.xml")
                result = self.cli(target, "--json")
                payload = json.loads(result.stdout)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(payload["summary"]["total_cells_inspected"], 1)
                self.assertEqual(types(payload["violations"]), ["formula_cell_blue_font"])

    def test_missing_or_escaping_worksheet_parts_fail_instead_of_silent_skipping(self):
        for relationship_target in ("worksheets/missing.xml", "../../outside.xml",
                                    "https://example.invalid/sheet.xml"):
            for packed in (True, False):
                with self.subTest(target=relationship_target, packed=packed):
                    result = self.cli(self.write_workbook(packed=packed,
                                      relationship_target=relationship_target), "--json")
                    self.assertEqual(result.returncode, 1)
                    self.assertTrue(json.loads(result.stdout)["error"])
                    self.assertNotIn("PASS", result.stdout)

    def test_summary_keeps_scope_and_omits_diagnostic_details(self):
        target = self.write_workbook(sheet=make_sheet('<c r="A1" s="0"><f>1+1</f><v>2</v></c>'))
        result = self.cli(target, "--summary")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Violations : 1", result.stdout)
        self.assertIn("no business, visual, or full financial-role validation", result.stdout)
        self.assertNotIn("[FAIL]", result.stdout)

    def test_json_full_and_summary_include_scope(self):
        target = self.write_workbook(sheet=make_sheet('<c r="A1" s="0"><f>1+1</f><v>2</v></c>'))
        for flags in (("--json",), ("--json", "--summary")):
            with self.subTest(flags=flags):
                result = self.cli(target, *flags)
                self.assertEqual(result.returncode, 1)
                payload = json.loads(result.stdout)
                self.assertEqual(payload["summary"]["violations"], 1)
                self.assertIn("no business, visual, or full financial-role validation", payload["scope"])
                if "--summary" in flags:
                    self.assertNotIn("violations", payload)
                    self.assertNotIn("warnings", payload)
                else:
                    self.assertEqual(types(payload["violations"]), ["formula_cell_blue_font"])
                self.assertEqual(result.stderr, "")

    def test_warning_only_remains_exit_zero(self):
        target = self.write_workbook(styles=make_styles(xfs=[(165, 0)], num_fmts={165: "0.0%"}))
        result = self.cli(target, "--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["summary"]["violations"], 0)
        self.assertEqual(types(payload["warnings"]), ["percent_value_gt_1"])

    def test_malformed_xml_and_style_attributes_fail_cleanly(self):
        root = ET.fromstring(make_styles())
        root.find(f"{S}fonts").set("count", "not-an-integer")
        for kwargs in ({"styles": b"<broken"}, {"sheet": b"<broken"},
                       {"styles": ET.tostring(root)}):
            for flags in ((), ("--json",)):
                with self.subTest(parts=tuple(kwargs), flags=flags):
                    result = self.cli(self.write_workbook(**kwargs), *flags)
                    self.assertEqual(result.returncode, 1)
                    self.assertNotIn("Traceback", result.stderr)
                    self.assertNotIn("PASS", result.stdout)
                    if flags:
                        self.assertTrue(json.loads(result.stdout)["error"])
                    else:
                        self.assertIn("ERROR", result.stdout)

    def test_missing_and_corrupt_archives_fail_cleanly(self):
        missing = self.work / "missing.xlsx"
        corrupt = self.work / "corrupt.xlsx"
        corrupt.write_bytes(b"not a ZIP archive")
        incomplete = self.work / "incomplete.xlsx"
        with zipfile.ZipFile(incomplete, "w") as package:
            package.writestr("unrelated.xml", "<unused/>")
        for target in (missing, corrupt, incomplete):
            with self.subTest(target=target.name):
                result = self.cli(target, "--json")
                self.assertEqual(result.returncode, 1)
                self.assertTrue(json.loads(result.stdout)["error"])
                self.assertNotIn("Traceback", result.stderr)

    def test_missing_target_reports_usage_with_nonzero_exit(self):
        result = self.cli()
        self.assertEqual(result.returncode, 1)
        self.assertIn("Usage:", result.stdout)


if __name__ == "__main__":
    unittest.main()
