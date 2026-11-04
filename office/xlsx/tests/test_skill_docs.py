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
        for color in ("#0000FF", "#008000", "#FF0000", "#135B44", "#CFE9E0", "#E7E5E4"):
            self.assertNotIn(color, common)
            self.assertIn(color, finance)

    def test_finance_theme_is_fixed_and_separate_from_formula_font_roles(self):
        finance = (SKILL / "references/finance.md").read_text()
        theme = finance.split("## Apply the fixed green theme\n", 1)[1].split("\n## ", 1)[0]
        self.assertEqual(
            set(re.findall(r"#[0-9A-F]{6}\b", theme)),
            {"#135B44", "#CFE9E0", "#0B3D2C", "#E7E5E4", "#FFFFFF"},
        )
        roles = finance.split("## Apply financial font roles\n", 1)[1].split("\n## ", 1)[0]
        for color in ("#0000FF", "#000000", "#008000", "#FF0000"):
            self.assertIn(color, roles)
        self.assertIn("must not\noverride the font roles", theme)

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
