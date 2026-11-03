"""Static PDF routing/content documentation contracts; no rendering or installs.

The model-case prompts below specify expected routing evidence, not executed
model runs or claims of standards-compliant PDF output.
"""
import ast
import json
from pathlib import Path
import re
import unittest

PDF = Path(__file__).resolve().parents[1]
CORE = (PDF / "SKILL.md").read_text()
DESIGN = (PDF / "design/design.md").read_text()
CONTENT = (PDF / "references/content.md").read_text()


def compact(text):
    return " ".join(text.split())


def heading_ids(text):
    return {
        re.sub(r"[^\w -]", "", heading.lower()).replace(" ", "-")
        for heading in re.findall(r"^#{1,6} (.+)$", text, re.M)
    }


class PdfSkillDocsTests(unittest.TestCase):
    def test_core_is_small_and_selects_requirement_before_operation(self):
        self.assertLess(len(CORE.splitlines()), 500)
        headings = ["## 1. Common requirements", "## 2. Named manuscript requirement or visual preset",
                    "## 3. Select the operation"]
        positions = [CORE.index(heading) for heading in headings]
        self.assertEqual(positions, sorted(positions))

    def test_direct_links_and_anchors_exist(self):
        for origin in (PDF / "SKILL.md", PDF / "design/design.md",
                       PDF / "references/content.md"):
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", origin.read_text()):
                with self.subTest(origin=origin.name, target=target):
                    filename, _, anchor = target.partition("#")
                    destination = (origin.parent / filename).resolve() if filename else origin
                    self.assertTrue(destination.is_file(), target)
                    if anchor:
                        self.assertIn(anchor, heading_ids(destination.read_text()))
        for anchor in ("block-contract", "common-blocks-and-tables", "mathematics", "charts",
                       "figures-and-captions", "bibliography", "code", "flowcharts",
                       "feature-specific-rendering-qa"):
            self.assertIn(f"references/content.md#{anchor}", CORE)
            self.assertIn(f"](#{anchor})", CONTENT)  # TOC
        self.assertIn("../references/content.md", DESIGN)

    def test_all_existing_block_types_extracted_once(self):
        expected = {"h1", "h2", "h3", "body", "bullet", "numbered", "callout", "table",
                    "image", "figure", "code", "math", "chart", "flowchart", "bibliography",
                    "divider", "caption", "pagebreak", "spacer"}
        contract = CONTENT.split("## Block contract", 1)[1].split("## Common blocks", 1)[0]
        self.assertEqual(set(re.findall(r"^\| `([^`]+)` \|", contract, re.M)), expected)
        for old_location in (CORE, DESIGN):
            self.assertNotIn("| Block |", old_location)
            self.assertNotIn("### Math formula guidance", old_location)
        self.assertIn("## Mathematics", CONTENT)
        self.assertNotIn("## Mathematics", DESIGN)

    def test_fields_defaults_numbering_and_fallbacks_preserved(self):
        text = compact(CONTENT)
        for term in ("headers", "rows", "col_widths", "path", "src", "caption", "language",
                     "label", "chart_type", "labels", "datasets", "title", "x_label", "y_label",
                     "figure", "nodes", "edges", "items", "id", "text", "pt"):
            with self.subTest(field=term):
                self.assertIn(f"`{term}`", CONTENT)
        for phrase in ("default 12pt", "defaults to `bar`", "to `true`", "`References`",
                       "summing to 1.0", "equal columns", "auto-resets", "hanging indent",
                       "share one figure counter", "still advances the shared counter",
                       "without a visible prefix", "empty title suppresses", "not a guarantee",
                       "without enclosing `$`", "`align`, `cases`, `matrix`", "multiple `math` blocks",
                       "before rendering label/caption", "code style", "[Image not found:",
                       "install-matplotlib placeholder", "no syntax highlighting", "~90 characters",
                       "3–5 words", "78%", "never up", "`oval` or `terminal`", "curved arcs"):
            with self.subTest(constraint=phrase):
                self.assertIn(phrase.lower(), text.lower())

    def test_examples_are_json_not_pseudocode(self):
        examples = re.findall(r"```json\n(.*?)\n```", CONTENT, re.S)
        self.assertEqual(len(examples), 4)
        for example in examples:
            self.assertIn("type", json.loads(example))

    def test_explicit_appearance_priority_and_honest_fonts(self):
        core, design = compact(CORE), compact(DESIGN)
        self.assertIn("typography, colors, cover/no-cover layout, spacing, and numbering", core)
        self.assertIn("supersede every visual default", design)
        self.assertIn("including \"always\", \"never\"", design)
        self.assertIn("unavailable actual fonts", design)
        self.assertIn("disclose fallbacks", design)
        self.assertIn("design inspiration, not an exact listing", design)
        self.assertIn("does not infer an industry", design)

    def test_feature_qa_requires_actual_evidence_not_renderer_promises(self):
        text = compact(CONTENT)
        for phrase in ("not existing renderer guarantees", "actual PDF page images",
                       "not an executed native rendering pass", "text extraction alone",
                       "Merge success does not prove compliance", "does **not** enforce citation style",
                       "not a promise of automatic wrapping", "no renumbering repair"):
            self.assertIn(phrase, text)
        for feature in ("Headings / lists / tables", "Math", "Charts", "Figures / captions",
                        "Bibliography", "Code", "Flowcharts"):
            self.assertIn(f"| {feature} |", CONTENT)

    def test_presets_and_color_values_not_lost(self):
        tree = ast.parse((PDF / "scripts/palette.py").read_text())
        presets = next(ast.literal_eval(node.value) for node in tree.body
                       if isinstance(node, ast.Assign)
                       and any(isinstance(name, ast.Name) and name.id == "PALETTES"
                               for name in node.targets))
        for name in presets:
            self.assertIn(f"| `{name}` |", DESIGN)
        for color in ("#1C3A5E", "#2E3440", "#3D4C5E", "#2A6B5A", "#3A7D6A", "#2D5F8A",
                      "#3D4F8A", "#2E5E3A", "#4A5E2A", "#6B2A35", "#5A2A6B", "#8A3A2A",
                      "#2A5A6B", "#2A4A6B", "#3D4A5A", "#444C56", "#1A1208", "#4A3820"):
            self.assertIn(color, DESIGN)
        for flag in ("--accent", "--cover-bg", "--abstract", "--cover-image"):
            self.assertIn(flag, DESIGN)

    def test_existing_operations_and_setup_gates_preserved(self):
        text = compact(CORE)
        self.assertIn('bash "$SKILL_DIR/scripts/make.sh" check', CORE)
        self.assertIn("once per session before this pipeline's CREATE/REFORMAT", text)
        self.assertIn("actual Chromium launch", text)
        self.assertIn("route's setup and validation instead", text)
        self.assertIn("DOCX-to-PDF does not require Chromium", text)
        self.assertIn("activated Python virtual environment", text)
        self.assertIn("not the browser pipeline", text)
        self.assertIn("do not make them install Chromium", text)
        for command in ('make.sh" run', 'make.sh" reformat', 'fill_inspect.py" --input',
                        'fill_write.py" --input'):
            self.assertIn(command, CORE)
        for field in ("`text`", "`checkbox`", "`dropdown`", "`radio`"):
            self.assertIn(field, CORE)
        self.assertIn('`"true"` or `"false"`', CORE)
        self.assertIn("`.md` `.txt` `.pdf` `.json`", CORE)
        self.assertIn("no new general READ, OCR, scans", text)
        self.assertIn("PDF-source reconstruction safeguards", text)

    def test_documented_entrypoints_and_flags_exist(self):
        # Package tests must work without Git history (archives and shallow CI).
        # Refactor-specific byte-preservation is verified separately in the audit.
        for name in ("make.sh", "palette.py", "cover.py", "render_cover.js",
                     "render_body.py", "merge.py", "fill_inspect.py", "fill_write.py",
                     "reformat_parse.py"):
            self.assertTrue((PDF / "scripts" / name).is_file(), name)
        make = (PDF / "scripts/make.sh").read_text()
        for flag in ("--title", "--type", "--content", "--out", "--accent", "--input"):
            self.assertIn(flag, make)
        docs = CORE + DESIGN + CONTENT
        for invented in ("--manuscript", "--apa", "--ieee", "--font", "--no-cover",
                         "--validate-citations", "--ocr"):
            self.assertNotIn(invented, docs)

    def test_model_case_routing_contracts(self):
        # These are modeled prompts + static assertions, NOT executed model tests.
        cases = [
            ("strict_apa_pdf", "Create a strict APA manuscript PDF, no decorative cover, requested font.",
             CORE, ["strict APA", "does **not** implement APA/IEEE", "capable authoring", "../docx/SKILL.md",
                    "Deliver only the requested format(s)", "disclose unavailable fonts"]),
            ("generic_academic_pdf", "Make a generic academic-looking PDF; no formal style standard.",
             CORE, ["generic, nonstandard academic-looking PDF", "visual preset", "CREATE"]),
            ("technical_pdf", (
                "Create a synthetic sensor-check PDF: table A=10, B=12, C=15 units; "
                "matching bar chart with units; mean equation 12.33 labeled (1); "
                "inline [1] and supplied fictional reference [1]; supplied sensor figure; "
                "Python code computing the same mean; a three-node measurement flowchart. "
                "Keep figure/chart/flowchart numbering coherent. Use white cover and #0000FF."
             ), CONTENT, ["`table`", "`chart`", "`math`", "`bibliography`", "`figure`", "`code`",
                          "`flowchart`", "shared counter", "Feature-specific rendering QA",
                          "Categories and values match table/source", "All cited IDs resolve"]),
            ("structured_markdown", "Reformat structured Markdown to PDF with tables and citations.",
             CORE, ["## Route C: REFORMAT", "--input source.md", "For structured Markdown",
                    "does not enforce the feature QA"]),
            ("fill_control", "Fill the fields in this existing PDF; preserve the layout.",
             CORE, ["## Route B: FILL", "without altering layout or design", "exact field names",
                    "not the browser pipeline"]),
            ("docx_companion", "Deliver Word and matching PDF from the same authored document.",
             CORE, ["DOCX companion control", "render the authored DOCX", "do not independently redesign"]),
        ]
        for name, prompt, document, required in cases:
            with self.subTest(case=name, prompt=prompt):
                for phrase in required:
                    self.assertIn(phrase, compact(document))


if __name__ == "__main__":
    unittest.main()
