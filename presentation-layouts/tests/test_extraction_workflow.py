import json
import re
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
EXTRACTION = REPO / "extract-template/presentation"
REFERENCES = EXTRACTION / "references"
LIBRARY = REPO / "presentation-layouts"


class ExtractionWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads((LIBRARY / "references/catalog.json").read_text())
        self.guide = (EXTRACTION / "SKILL.md").read_text()
        self.reuse = (REFERENCES / "layout-reuse.md").read_text()
        self.builtins = (REFERENCES / "built-in-layouts.md").read_text()

    def test_public_catalog_files_resolve_locally(self):
        for layout in self.catalog["layouts"]:
            path = Path(layout["file"])
            self.assertFalse(path.is_absolute())
            resolved = (LIBRARY / "references" / path).resolve()
            self.assertTrue(resolved.is_relative_to(LIBRARY))
            self.assertTrue(resolved.is_file())
        geometry = (LIBRARY / "references" / self.catalog["geometry"]).resolve()
        self.assertTrue(geometry.is_relative_to(LIBRARY))
        self.assertTrue(geometry.is_file())

    def test_public_pilot_scope_is_accurate(self):
        ids = [layout["id"] for layout in self.catalog["layouts"]]
        self.assertEqual(len(ids), 6)
        self.assertEqual(len(set(ids)), len(ids))
        self.assertEqual(
            set(ids),
            {"kpi-grid", "table", "two-column", "comparison", "process", "image-text"},
        )
        self.assertIn("six structures", self.builtins)
        self.assertIn("not a 40+", self.builtins)

    def test_documented_selection_examples_exist_in_public_catalog(self):
        examples = []
        for line in self.builtins.splitlines():
            if line.startswith("| "):
                examples.extend(re.findall(r"`([^`]+)`", line))
        self.assertEqual(set(examples), {item["id"] for item in self.catalog["layouts"]})

    def test_extraction_dependencies_are_public_only(self):
        self.assertFalse((REFERENCES / "artifact-layout-catalog.json").exists())
        documents = [
            EXTRACTION / "SKILL.md", *REFERENCES.glob("*.md"),
            LIBRARY / "SKILL.md", *LIBRARY.glob("references/*.md"),
            *EXTRACTION.rglob("*.json"), *LIBRARY.glob("references/*.json"),
        ]
        for document in documents:
            text = document.read_text()
            for owner, repository in re.findall(
                r"https?://github\.com/([^/\s`]+)/([^/\s`]+)", text
            ):
                with self.subTest(document=document.name, repository=repository):
                    self.assertEqual((owner, repository), ("okou-ai", "okou-skills"))
            if document.suffix == ".json":
                pending = [json.loads(text)]
                while pending:
                    item = pending.pop()
                    if isinstance(item, dict):
                        if isinstance(item.get("repository"), str):
                            self.assertEqual(item["repository"], "okou-ai/okou-skills")
                        self.assertFalse(item.get("requiresAuthenticatedAccess", False))
                        pending.extend(item.values())
                    elif isinstance(item, list):
                        pending.extend(item)
        pins = re.findall(
            r"https://github\.com/okou-ai/okou-skills/blob/([0-9a-f]{40})/", self.builtins
        )
        self.assertTrue(pins)
        self.assertIn("No private repository", self.builtins)
        self.assertNotRegex(self.guide + self.reuse + self.builtins, r"52-layout|52 Data Report")

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
        combined += (LIBRARY / "references/catalog.md").read_text()
        for obsolete in (
            "Generation-time built-in references",
            "Do not write the adapted layout back",
            "do not copy the catalogue or pre-adapt",
            "Put the adapted content in that generated deck, not back",
            "**not** in the reusable template package",
        ):
            self.assertNotIn(obsolete, combined)

    def test_fitter_and_neutral_library_follow_extraction_timing(self):
        fitter = (REFERENCES / "typography-fit.md").read_text()
        library = (LIBRARY / "SKILL.md").read_text()
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
