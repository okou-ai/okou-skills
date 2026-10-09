import json
import re
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
EXTRACTION = REPO / "extract-template/presentation"
REFERENCES = EXTRACTION / "references"


class ExtractionWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads(
            (REFERENCES / "artifact-layout-catalog.json").read_text()
        )
        self.guide = (EXTRACTION / "SKILL.md").read_text()
        self.reuse = (REFERENCES / "layout-reuse.md").read_text()
        self.builtins = (REFERENCES / "built-in-layouts.md").read_text()

    def test_catalog_is_immutable_selection_metadata(self):
        self.assertEqual(self.catalog["repository"], "okou-ai/Template-artifact")
        self.assertRegex(self.catalog["commit"], r"^[0-9a-f]{40}$")
        self.assertTrue(self.catalog["requiresAuthenticatedAccess"])
        self.assertEqual(
            set(self.catalog),
            {"repository", "commit", "requiresAuthenticatedAccess",
             "catalogPath", "fragmentsRoot", "layoutIds"},
        )
        for key in ("catalogPath", "fragmentsRoot"):
            path = Path(self.catalog[key])
            self.assertFalse(path.is_absolute())
            self.assertNotIn("..", path.parts)
            self.assertEqual(path.parts[:2], ("Template-Presentation", "data-report"))

    def test_catalog_has_52_unique_safe_layout_ids(self):
        ids = self.catalog["layoutIds"]
        self.assertEqual(len(ids), 52)
        self.assertEqual(len(set(ids)), len(ids))
        self.assertEqual(ids, sorted(ids))
        for layout_id in ids:
            self.assertRegex(layout_id, r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
        self.assertTrue(
            {"comparison-ruled", "process-steps", "timeline", "kpi-grid",
             "table", "line-chart", "waterfall", "image-evidence"} <= set(ids)
        )

    def test_documented_selection_examples_exist_in_catalog(self):
        examples = []
        for line in self.builtins.splitlines():
            if line.startswith("| "):
                examples.extend(re.findall(r"`([^`]+)`", line))
        self.assertGreater(len(examples), 20)
        self.assertTrue(set(examples) <= set(self.catalog["layoutIds"]))

    def test_upstream_links_match_catalog_revision(self):
        links = re.findall(
            r"https://github\.com/okou-ai/Template-artifact/blob/([^/]+)/([^\s`]+)",
            self.builtins,
        )
        self.assertEqual(len(links), 2)
        for commit, path in links:
            self.assertEqual(commit, self.catalog["commit"])
        self.assertEqual(links[0][1], self.catalog["catalogPath"])
        self.assertEqual(
            links[1][1], self.catalog["fragmentsRoot"] + "/<id>.html"
        )
        self.assertIn("Template-artifact is private", self.builtins)

    def test_extraction_links_resolve_locally(self):
        documents = [EXTRACTION / "SKILL.md", *REFERENCES.glob("*.md")]
        for document in documents:
            for target in re.findall(r"\]\(([^)]+)\)", document.read_text()):
                if re.match(r"^[a-z]+://", target) or target.startswith("#"):
                    continue
                with self.subTest(document=document.name, target=target):
                    self.assertTrue(
                        (document.parent / target.split("#", 1)[0]).is_file()
                    )

    def test_extensions_are_saved_before_generation(self):
        self.assertIn("before publication", self.guide)
        self.assertIn("extended-index.json", self.guide)
        self.assertIn("extended/<name>.html", self.guide)
        self.assertIn("## Upload-time layout extension", self.reuse)
        self.assertIn("## Generation-time local reuse", self.reuse)
        self.assertIn("Admit only validated candidates", self.reuse)
        self.assertIn("copy/edit contract", self.reuse)
        combined = self.guide + self.reuse + self.builtins
        for obsolete in (
            "Generation-time built-in references",
            "Do not write the adapted layout back",
            "do not copy the catalogue or pre-adapt",
            "Put the adapted content in that generated deck, not back",
        ):
            self.assertNotIn(obsolete, combined)

    def test_fitter_and_neutral_library_follow_extraction_timing(self):
        fitter = (REFERENCES / "typography-fit.md").read_text()
        library = (REPO / "presentation-layouts/SKILL.md").read_text()
        self.assertIn("every extension adapted during extraction", fitter)
        self.assertIn("Save validated reusable extension files", fitter)
        self.assertIn("Later generation copies and edits saved layouts", library)
        self.assertNotIn("generation-time built-in adaptation", fitter)
        self.assertNotIn("does not contain copies", library)

    def test_original_source_and_format_boundaries_are_explicit(self):
        self.assertIn("restricted to original source compositions", self.reuse)
        self.assertIn("Never label an extension as an original source page", self.reuse)
        self.assertIn("Keep the reusable template and original upload unchanged", self.guide)
        self.assertIn("generation, viewing, QA, and export", self.guide)
        self.assertIn("output remains HTML", self.guide)
        self.assertIn("does not provide native PPTX in-place editing", self.guide)


if __name__ == "__main__":
    unittest.main()
