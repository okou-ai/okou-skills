"""Offline packaging/schema checks; no model calls or semantic image evaluation."""

import copy
import json
from pathlib import Path
import re
import unittest

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]


def load(relative_path):
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


class ProductPhotographyContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load("templates/brief.schema.json")
        cls.validator = Draft202012Validator(cls.schema)
        cls.concept = load("templates/concept-brief.json")
        cls.reference = load("templates/reference-brief.json")

    def assert_invalid(self, brief):
        self.assertTrue(list(self.validator.iter_errors(brief)))

    def test_schema_is_valid_and_references_only_local_definitions(self):
        Draft202012Validator.check_schema(self.schema)

        def walk(value):
            if isinstance(value, dict):
                if "$ref" in value:
                    self.assertTrue(value["$ref"].startswith("#/"))
                for child in value.values():
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)

        walk(self.schema)

    def test_both_examples_are_valid_prompt_only_plans(self):
        for example in [self.concept, self.reference]:
            with self.subTest(mode=example["product_mode"]):
                self.validator.validate(example)
                self.assertEqual(example["task"], "prompt_only")
                self.assertEqual(example["product"]["observed"], [])
                ids = [ref["id"] for ref in example["references"]]
                self.assertEqual(len(ids), len(set(ids)))

    def test_every_shot_and_look_combination_is_structurally_supported(self):
        for shot in ["studio", "lifestyle", "macro", "flat_lay", "hero"]:
            for look in ["neutral", "fresh_natural", "dark_luxury", "custom"]:
                brief = copy.deepcopy(self.concept)
                brief["shot"]["type"] = shot
                brief["look"]["preset"] = look
                with self.subTest(shot=shot, look=look):
                    self.validator.validate(brief)

    def test_reference_requires_a_product_reference(self):
        for references in [[], [{**self.reference["references"][0], "role": "style"}]]:
            brief = copy.deepcopy(self.reference)
            brief["references"] = references
            self.assert_invalid(brief)

    def test_reference_cannot_claim_concept_fidelity(self):
        brief = copy.deepcopy(self.reference)
        brief["fidelity"] = "concept"
        self.assert_invalid(brief)

    def test_concept_cannot_claim_reference_or_pixel_fidelity(self):
        for fidelity in ["reference_guided", "protected_composite"]:
            brief = copy.deepcopy(self.concept)
            brief["fidelity"] = fidelity
            self.assert_invalid(brief)

    def test_compositing_is_a_reference_plan_not_verified_execution(self):
        brief = copy.deepcopy(self.reference)
        brief["fidelity"] = "protected_composite"
        self.validator.validate(brief)
        self.assertEqual(brief["task"], "prompt_only")

    def test_reference_printing_cannot_be_replaced_with_new_label_copy(self):
        brief = copy.deepcopy(self.reference)
        brief["text"] = {"mode": "concept_label", "copy": ["NEW LABEL"]}
        self.assert_invalid(brief)
        brief["text"] = {"mode": "preserve_print", "copy": ["TRANSCRIBED LABEL"]}
        self.assert_invalid(brief)

    def test_concept_label_requires_exact_nonempty_copy(self):
        brief = copy.deepcopy(self.concept)
        brief["text"]["copy"] = []
        self.assert_invalid(brief)
        brief["text"]["copy"] = ["   "]
        self.assert_invalid(brief)
        brief["text"]["copy"] = ["雨后 Cedar 01", "柚子 Soda"]
        self.validator.validate(brief)
        self.assertEqual(brief["text"]["copy"], ["雨后 Cedar 01", "柚子 Soda"])

    def test_no_added_text_forbids_new_copy(self):
        brief = copy.deepcopy(self.concept)
        brief["text"] = {"mode": "no_added_text", "copy": ["SALE"]}
        self.assert_invalid(brief)
        brief["text"]["copy"] = []
        self.validator.validate(brief)

    def test_single_frame_only(self):
        for count in [0, 2, True, "1"]:
            brief = copy.deepcopy(self.concept)
            brief["output"]["count"] = count
            self.assert_invalid(brief)

    def test_unknown_execution_and_authorization_fields_are_rejected(self):
        for field in ["model", "provider", "auto_retry", "authorized"]:
            brief = copy.deepcopy(self.concept)
            brief[field] = True
            self.assert_invalid(brief)
        brief = copy.deepcopy(self.concept)
        brief["output"]["model"] = "not-a-model-selector"
        self.assert_invalid(brief)

    def test_fictional_reference_locator_cannot_be_submitted_as_generation(self):
        brief = copy.deepcopy(self.reference)
        brief["task"] = "generate_image"
        brief["product"]["observed"] = ["Synthetic observation fixture for schema testing, not real image evidence."]
        for source in ["example://replace-me", "EXAMPLE://replace-me", "  Example://replace-me"]:
            brief["references"][0]["source"] = source
            with self.subTest(source=source):
                self.assert_invalid(brief)

    def test_reference_generation_requires_observations_but_does_not_grant_permission(self):
        brief = copy.deepcopy(self.reference)
        brief["task"] = "generate_image"
        brief["references"][0]["source"] = "attachment://user-product-front"
        self.assert_invalid(brief)
        brief["product"]["observed"] = ["Closed bottle with one cap, front view."]
        self.validator.validate(brief)
        # This only validates planning data, not attachment accessibility or consent.
        self.assertNotIn("authorized", brief)

    def test_unsupported_modes_and_invalid_dimensions_are_rejected(self):
        for shot in ["on_model", "infographic", "batch"]:
            brief = copy.deepcopy(self.concept)
            brief["shot"]["type"] = shot
            self.assert_invalid(brief)
        for size in ["0x1536", "1024", "portrait", "1024x0"]:
            brief = copy.deepcopy(self.concept)
            brief["output"]["size"] = size
            self.assert_invalid(brief)

    def test_unprinted_macro_crop_can_exclude_source_branding(self):
        brief = copy.deepcopy(self.reference)
        brief["shot"] = {
            "type": "macro",
            "purpose": "Show an evidenced unprinted garment seam, not the whole garment.",
            "required_visible": ["The agreed seam region"],
            "required_printing": [],
        }
        brief["product"].update({
            "summary": "Illustrative garment reference with an unprinted seam and an off-frame brand mark.",
            "state": "Garment laid flat in the evidenced source view.",
            "unknown": ["This is synthetic planning data, not a real inspected source."],
            "identity_lock": ["Preserve only the evidenced visible seam and fabric characteristics in the agreed crop."],
        })
        brief["camera"]["framing"] = "Tight crop of the evidenced unprinted seam only."
        self.validator.validate(brief)
        self.assertEqual(brief["shot"]["required_printing"], [])

    def test_transparent_jpeg_is_rejected_without_promising_model_support(self):
        brief = copy.deepcopy(self.concept)
        brief["output"]["background"] = "transparent"
        brief["output"]["format"] = "jpeg"
        self.assert_invalid(brief)
        for output_format in ["png", "webp"]:
            brief["output"]["format"] = output_format
            self.validator.validate(brief)

    def test_prompt_scaffold_has_eight_ordered_slots(self):
        text = (ROOT / "templates/prompt.txt").read_text(encoding="utf-8")
        headings = re.findall(r"^\[(\d)\. .+\]$", text, re.MULTILINE)
        self.assertEqual(headings, [str(n) for n in range(1, 9)])
        slots = re.findall(r"\{\{([a-z_]+)\}\}", text)
        self.assertEqual(len(slots), 8)
        self.assertEqual(len(set(slots)), 8)

    def test_worked_prompts_are_complete_and_have_no_scaffold_variables(self):
        document = (ROOT / "references/prompt-framework.md").read_text(encoding="utf-8")
        examples = re.findall(r"```text\n(.*?)```", document, re.DOTALL)
        self.assertEqual(len(examples), 2)
        for example in examples:
            self.assertNotIn("{{", example)
            self.assertEqual(
                re.findall(r"^\[(\d)\. .+\]$", example, re.MULTILINE),
                [str(n) for n in range(1, 9)],
            )

    def test_qa_template_does_not_fabricate_observations_or_cost(self):
        report = load("templates/qa-report.json")
        self.assertEqual(report["overall"], "not_generated")
        self.assertIsNone(report["generation_id"])
        self.assertIsNone(report["billing"]["credits"])
        self.assertTrue(all(value is None for value in report["actual"].values()))
        self.assertEqual(len(report["checks"]), 8)
        for check in report["checks"].values():
            self.assertEqual(check["status"], "not_checked")
            self.assertIsNone(check["observation"])
            self.assertIsNone(check["evidence"])

    def test_all_local_markdown_links_resolve(self):
        for document in ROOT.rglob("*.md"):
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
                if "://" in target or target.startswith("#"):
                    continue
                destination = (document.parent / target.split("#", 1)[0]).resolve()
                with self.subTest(document=document.relative_to(ROOT), target=target):
                    self.assertTrue(destination.is_relative_to(ROOT))
                    self.assertTrue(destination.is_file(), str(destination))

    def test_bundled_license_and_pinned_attribution(self):
        notices = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
        self.assertIn("3bf78a423b1ba27a1f500b3b50f806b86cc5bdab", notices)
        self.assertIn("73abd50bf2b689b5a453f28ddd7b0016415deec6", notices)
        self.assertIn("Apache License", (ROOT / "LICENSE").read_text())
        self.assertIn("Copyright (c) 2026 Kshitiz Kumar", (ROOT / "licenses/SuperCMO-NOTICE.txt").read_text())
        self.assertIn("Copyright (c) 2026 Buluu@新西楼", (ROOT / "licenses/buluslan-MIT.txt").read_text())


if __name__ == "__main__":
    unittest.main()
