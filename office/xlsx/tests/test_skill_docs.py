"""Static documentation contracts; these do not measure LLM routing quality."""
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET


SKILL = Path(__file__).resolve().parents[1]
OFFICE = SKILL.parent
S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R = "{http://schemas.openxmlformats.org/package/2006/relationships}"


def markdown_targets(text):
    return re.findall(r"\[[^\]\n]+\]\(([^)\s]+)\)", text)


def description(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---", text, re.S)
    if not match:
        raise AssertionError(f"Missing frontmatter: {path}")
    field = re.search(r"^description: (.+)$", match[1], re.M)
    if not field:
        raise AssertionError(f"Missing one-line routing description: {path}")
    return field[1].lower()


class SkillDocumentationTests(unittest.TestCase):
    def test_excel_and_discovered_office_entry_expose_finance_tasks(self):
        for path in (OFFICE / "SKILL.md", SKILL / "SKILL.md"):
            with self.subTest(path=path):
                value = description(path)
                for trigger in ("excel", "financial model", "budget", "forecast"):
                    self.assertIn(trigger, value)
                self.assertLessEqual(len(value), 1024)
        self.assertLess(len((SKILL / "SKILL.md").read_text().splitlines()), 500)

    def test_each_reference_is_directly_discoverable_from_excel_entry(self):
        targets = set(markdown_targets((SKILL / "SKILL.md").read_text()))
        for path in (SKILL / "references").glob("*.md"):
            with self.subTest(path=path):
                self.assertIn(path.relative_to(SKILL).as_posix(), targets)
        self.assertIn("references/finance.md", targets)

    def test_package_markdown_links_resolve(self):
        paths = [OFFICE / "SKILL.md", *SKILL.rglob("*.md")]
        for path in paths:
            for target in markdown_targets(path.read_text(encoding="utf-8")):
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                with self.subTest(path=path, target=target):
                    self.assertTrue((path.parent / unquote(parsed.path)).exists())

    def test_non_financial_presentation_does_not_impose_finance_palette(self):
        common = (SKILL / "references/format.md").read_text()
        finance = (SKILL / "references/finance.md").read_text()
        for color in ("#0000FF", "#008000", "#FF0000", "#135B44", "#CFE9E0", "#E7E5E4", "#F2F2F2", "#404040"):
            self.assertNotIn(color, common)
            self.assertIn(color, finance)

    def test_finance_theme_is_fixed_and_separate_from_formula_font_roles(self):
        finance = (SKILL / "references/finance.md").read_text()
        theme = finance.split("## Apply the fixed green theme\n", 1)[1].split("\n## ", 1)[0]
        self.assertEqual(
            set(re.findall(r"#[0-9A-F]{6}\b", theme)),
            {"#135B44", "#CFE9E0", "#0B3D2C", "#E7E5E4", "#F2F2F2", "#404040", "#FFFFFF"},
        )
        roles = finance.split("## Apply financial font roles\n", 1)[1].split("\n## ", 1)[0]
        for color in ("#0000FF", "#000000", "#008000", "#FF0000"):
            self.assertIn(color, roles)
        self.assertIn("must not\noverride the font roles", theme)

    def test_table_headers_are_distinct_from_finance_section_bands(self):
        finance = (SKILL / "references/finance.md").read_text()
        theme = finance.split("## Apply the fixed green theme\n", 1)[1].split("\n## ", 1)[0]
        rows = {}
        for line in theme.splitlines():
            if line.startswith("|"):
                cells = [cell.strip() for cell in line.strip("|").split("|")]
                rows[cells[0]] = cells[1:]
        self.assertIn("#135B44", rows["Main title bands and primary chart accents"][0])
        self.assertIn("#CFE9E0", rows["Section divider bands"][0])
        self.assertEqual(
            rows["Table column-header labels"],
            ["Light gray `#F2F2F2`", "Dark gray `#404040`, bold"],
        )
        self.assertIn("keep these levels visually distinct", " ".join(theme.split()))
        self.assertIn("not editable inputs or formula outputs", " ".join(theme.split()))

    def test_new_workbook_plan_prioritizes_use_over_sheet_count(self):
        create = (SKILL / "references/create.md").read_text()
        plan = " ".join(create.split("## 1. Plan\n", 1)[1].split("\n## ", 1)[0].split())
        self.assertNotIn("smallest useful", plan)
        for requirement in (
            "reading and editing tasks",
            "Prioritize completeness and readability over reducing the sheet count",
            "give data and explanations enough space",
            "within the requested scope",
        ):
            self.assertIn(requirement, plan)
        self.assertIn(
            "initial sheet count is not a layout recommendation",
            " ".join(create.split()),
        )

    def test_finance_model_structure_has_a_default_and_bounded_exception(self):
        finance = (SKILL / "references/finance.md").read_text()
        plan = " ".join(
            finance.split("## Plan the reading and calculation paths\n", 1)[1]
            .split("\n## ", 1)[0].split()
        )
        self.assertNotIn("compact block", plan)
        for requirement in (
            "Start the reader with the answer",
            "For new budgets, forecasts or multi-scenario models, normally",
            "overview, editable assumptions and calculation schedules on distinct sheets",
            "functional example, not a required tab count",
            "single-sheet model for a straightforward task only when",
            "results, inputs, workings and explanations remain distinct and readable",
            "instead of shrinking text, crowding blocks or omitting context",
        ):
            self.assertIn(requirement, plan)
        self.assertIn(
            "Preserve supplied templates/house styles; narrow edits do not authorize redesign",
            finance,
        )

    def test_new_finance_layouts_have_bounded_blank_row_defaults(self):
        finance = (SKILL / "references/finance.md").read_text()
        spacing = " ".join(
            finance.split("## Space new report and model sheets\n", 1)[1]
            .split("\n## ", 1)[0].split()
        )
        self.assertIn("[Spacing](#space-new-report-and-model-sheets)", finance)
        for requirement in (
            "new reader-facing layouts, not raw-data-only exports",
            "two blank rows above the main title",
            "one blank row after the title band and one before the first content block",
            "keep any subtitle and unit notation together",
            "Separate completed sections or standalone tables with one blank row",
            "section band next to its table's column-header row",
            "headers next to data",
            "about 6 pt high",
            "do not stack both",
            "empty and unshaded, outside structured tables, filter ranges and raw-data blocks",
            "Plan the gaps before writing formulas and ranges",
            "Preserve existing layouts during narrow edits",
            "Inspect both the worksheet and exported pages",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, spacing)

    def test_validation_distinguishes_setup_from_ready_to_use_results(self):
        validation = " ".join((SKILL / "references/validate.md").read_text().split())
        for requirement in (
            "a Linux LibreOffice core install without Calc is not a working spreadsheet engine",
            "When dependency setup is permitted",
            "Respect explicit restrictions on installing or invoking applications",
            "For a new calculation-driven workbook intended to be ready on delivery",
            "reopen the exact final file after saving",
            "current cached results for critical cells, including ratio denominators",
            "report the delivery as incomplete, not a ready-to-use model",
            "Do not fabricate caches",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, validation)
        finance = " ".join((SKILL / "references/finance.md").read_text().split())
        self.assertIn("Operating margin is operating income divided by revenue", finance)
        self.assertIn("not the simple average of monthly percentages", finance)
        self.assertIn("Trace the effect through detail, summary and sensitivity outputs", finance)
        self.assertIn("not just the headline total", finance)

    def test_ooxml_reference_explains_relative_worksheet_element_order(self):
        reference = (SKILL / "references/ooxml-cheatsheet.md").read_text()
        order = reference.split("## Worksheet element order\n", 1)[1].split("\n## ", 1)[0]
        tokens = ("`sheetData`", "`autoFilter`", "`mergeCells`", "`dataValidations`", "`pageSetup`")
        positions = [order.index(token) for token in tokens]
        self.assertEqual(positions, sorted(positions))
        for requirement in (
            "do not append `autoFilter` after `mergeCells`",
            "not a complete schema validator",
            "repair warnings or missing worksheet content",
        ):
            self.assertIn(requirement, " ".join(order.split()))
        self.assertIn("github.com/dotnet/Open-XML-SDK/blob/", order)

    def test_new_workbook_route_prefers_objects_without_removing_raw_or_narrow_paths(self):
        create = " ".join((SKILL / "references/create.md").read_text().split())
        entry = (SKILL / "SKILL.md").read_text()
        for requirement in (
            "Prefer a maintained high-level workbook library",
            "raw OOXML path is valid when needed",
            "Do not rebuild existing files through a library that may drop features",
            "--preflight",
            "Save a first complete draft early",
            "fix clipped headings, cramped notes, split columns or chart overlaps",
            "Saving an openpyxl workbook again after Calc recalculation can clear its caches",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, create)
        self.assertIn("references/authoring.md", entry)
        self.assertTrue((SKILL / "scripts/xlsx_authoring.py").is_file())
        self.assertTrue((SKILL / "requirements-authoring.txt").is_file())
        authoring = (SKILL / "references/authoring.md").read_text()
        for operation in ("style_value", "report_band", "table_header", "report_page"):
            self.assertIn(operation, authoring)

    def test_presentation_feedback_requires_actual_page_review_and_revision(self):
        validation = " ".join((SKILL / "references/validate.md").read_text().split())
        for requirement in (
            "before substantial formula authoring",
            "A successful control does not validate a candidate",
            "inspect the rendered pages, not only extracted text",
            "Verify that the intended sheets and report areas are included",
            "regenerate and rerender affected pages",
            "success is not a financial-format certificate",
        ):
            self.assertIn(requirement, validation)

    def test_chart_guidance_is_loaded_during_planning_and_validation(self):
        entry = (SKILL / "SKILL.md").read_text()
        create = (SKILL / "references/create.md").read_text()
        validation = (SKILL / "references/validate.md").read_text()
        self.assertIn("references/charts.md", markdown_targets(entry))
        plan = create.split("## 1. Plan\n", 1)[1].split("\n## ", 1)[0]
        self.assertIn("charts.md", markdown_targets(plan))
        self.assertIn("charts.md#verify-the-saved-chart", markdown_targets(validation))
        self.assertIn("authorized chart changes", " ".join(entry.split()))

    def test_chart_guidance_is_question_led_and_scope_preserving(self):
        charts = " ".join((SKILL / "references/charts.md").read_text().split())
        for requirement in (
            "Preserve supplied templates and house styles",
            "not a chart quota",
            "Omit redundant charts when a small table is clearer",
            "Do not decorate data-only exports, expand narrow edits",
            "during read-only analysis just to satisfy this heuristic",
            "Do not add dashboard tabs solely to meet a chart count",
            "reconcile the baseline with the main model before charting it",
            "Bar/column chart",
            "Line chart",
            "Waterfall",
            "matrix/heatmap",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, charts)
        self.assertNotRegex(charts, r"#[0-9A-Fa-f]{6}\b")

    def test_chart_guidance_requires_live_sources_and_saved_plot_feedback(self):
        charts = " ".join((SKILL / "references/charts.md").read_text().split())
        for requirement in (
            "Prefer native editable charts",
            "Bind series and categories to worksheet ranges, not pasted results",
            "Review chart references after row/column insertion or range changes",
            "never invent chart data caches",
            "does not prove the chart data cache or rendered plot is current",
            "verify both dependent cells and the plotted series refresh",
            "actual previews of every relevant chart-containing sheet",
            "Revise and rerender within the same authoring attempt",
            "identify that check as unverified",
            "Deliver only the requested files",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, charts)

    def test_starter_style_roles_and_relationship_ids_remain_valid(self):
        template = SKILL / "templates/minimal_xlsx"
        styles = ET.parse(template / "xl/styles.xml").getroot()
        fonts = styles.find(f"{S}fonts")
        xfs = styles.find(f"{S}cellXfs")
        self.assertEqual(int(xfs.get("count")), len(xfs))
        for index, expected in ((1, "0000FF"), (2, "000000"), (3, "008000")):
            font = fonts[int(xfs[index].get("fontId"))]
            self.assertEqual(font.find(f"{S}color").get("rgb")[-6:], expected)
        rels = ET.parse(template / "xl/_rels/workbook.xml.rels").getroot()
        ids = [item.get("Id") for item in rels.findall(f"{R}Relationship")]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), {"rId1", "rId2", "rId3"})


if __name__ == "__main__":
    unittest.main()
