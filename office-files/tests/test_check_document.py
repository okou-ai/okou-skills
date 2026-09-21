"""Final-artifact QA tests using real synthetic PDFs, not mocked measurements."""

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

import pymupdf


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_document.py"
SPEC = importlib.util.spec_from_file_location("check_document", SCRIPT)
qa = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(qa)


class DocumentQATest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.pdf = self.root / "document.pdf"
        self.out = self.root / "qa"

    def make_pdf(self, contents=("Heading\nReadable document body.",), prepare=None):
        with pymupdf.open() as document:
            for content in contents:
                page = document.new_page(width=400, height=500)
                if content:
                    page.insert_text((45, 60), content, fontsize=12)
                if prepare:
                    prepare(page)
            document.save(self.pdf)

    def make_docx(self):
        path = self.root / "document.docx"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
            archive.writestr("word/document.xml", '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Body</w:t></w:r></w:p></w:body></w:document>')
        return path

    def make_expectations(self, data):
        path = self.root / "expectations.json"
        qa.write_json(path, data)
        return path

    def make_render_manifest(self):
        docx = self.make_docx()
        source = self.root / "source.md"
        source.write_text("# Heading\nReadable document body.\n")
        reference = self.root / "reference.docx"
        reference.write_bytes(docx.read_bytes())
        resource = self.root / "chart.svg"
        resource.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        path = self.root / "render.json"
        qa.write_json(path, {
            "status": "needs-inspection",
            "source": qa.fingerprint(source),
            "reference": qa.fingerprint(reference),
            "resources": [qa.fingerprint(resource)],
            "outputs": {"pdf": qa.fingerprint(self.pdf), "docx": qa.fingerprint(docx)},
        })
        return path

    def review(self):
        return json.loads((self.out / "review.json").read_text())

    def finish_review_fixture(self):
        """Synthetic fixture only: production callers must open each image."""
        review = self.review()
        observations = {
            "legibility_and_density": "Fixture body is readable with generous spacing.",
            "hierarchy": "Fixture heading and body have a clear reading order.",
            "composition_and_rhythm": "Fixture uses a balanced single-column composition.",
            "pagination_and_grouping": "All fixture content remains together on this page.",
            "tables_and_figures": "No tables or figures are present in this fixture.",
        }
        for page in review["pages"]:
            for criterion, result in page["criteria"].items():
                result.update(status="pass", observations=observations[criterion])
        for item in review["warning_acknowledgements"]:
            item["observations"] = "This synthetic fixture intentionally uses a short page."
        qa.write_json(self.out / "review.json", review)

    def codes(self, report, severity=None):
        return {f["code"] for f in report["findings"] if severity is None or f["severity"] == severity}

    def test_unreviewed_pages_cannot_be_accepted(self):
        self.make_pdf()
        report = qa.inspect(self.pdf, self.out)
        self.assertEqual(report["page_count"], 1)
        self.assertTrue((self.out / "page-001.png").is_file())
        with self.assertRaisesRegex(ValueError, "needs a passed review"):
            qa.accept(self.out)
        self.assertFalse((self.out / "acceptance.json").exists())

    def test_every_page_and_criterion_must_be_reviewed(self):
        self.make_pdf(("First page", "Second page"))
        qa.inspect(self.pdf, self.out)
        self.finish_review_fixture()
        full_review = self.review()
        missing_page = {**full_review, "pages": full_review["pages"][:1]}
        qa.write_json(self.out / "review.json", missing_page)
        with self.assertRaisesRegex(ValueError, "every page"):
            qa.accept(self.out)
        missing_criterion = json.loads(json.dumps(full_review))
        del missing_criterion["pages"][1]["criteria"]["hierarchy"]
        qa.write_json(self.out / "review.json", missing_criterion)
        with self.assertRaisesRegex(ValueError, "five visual criteria"):
            qa.accept(self.out)
        qa.write_json(self.out / "review.json", full_review)
        acceptance = qa.accept(self.out)
        self.assertEqual(acceptance["status"], "READY_TO_DELIVER")
        self.assertEqual(len(acceptance["page_image_sha256"]), 2)

    def test_page_edge_clipping_is_a_blocker(self):
        self.make_pdf(prepare=lambda page: page.insert_text((-8, 130), "CLIPPED content", fontsize=12))
        report = qa.inspect(self.pdf, self.out)
        self.assertIn("clipped_text", self.codes(report, "blocker"))
        self.finish_review_fixture()
        with self.assertRaisesRegex(ValueError, "machine blockers"):
            qa.accept(self.out)

    def test_superscript_and_vector_diagram_do_not_create_false_blockers(self):
        def prepare(page):
            page.insert_text((45, 160), "E = mc", fontsize=12)
            page.insert_text((84, 154), "2", fontsize=6)
            page.draw_rect((45, 220, 180, 300), color=(0, 0, 0))
            page.insert_text((60, 260), "Diagram label", fontsize=11)
            page.draw_line((180, 260), (250, 260), color=(0, 0, 0))
        self.make_pdf(prepare=prepare)
        report = qa.inspect(self.pdf, self.out)
        self.assertFalse(self.codes(report, "blocker"))
        self.assertNotIn("possible_text_overlap", self.codes(report))
        self.assertNotIn("small_text", self.codes(report))

    def test_rotation_uses_unrotated_text_coordinates(self):
        self.make_pdf(prepare=lambda page: page.set_rotation(90))
        report = qa.inspect(self.pdf, self.out)
        self.assertFalse(self.codes(report, "blocker"))
        self.assertEqual(report["pages"][0]["width_pt"], 500)

    def test_cropbox_origin_does_not_create_false_clipping(self):
        self.make_pdf(prepare=lambda page: page.set_cropbox(pymupdf.Rect(20, 20, 380, 480)))
        report = qa.inspect(self.pdf, self.out)
        self.assertFalse(self.codes(report, "blocker"))
        self.assertEqual(report["pages"][0]["width_pt"], 360)

    def test_invisible_ocr_text_is_not_treated_as_clipping(self):
        self.make_pdf(prepare=lambda page: page.insert_text((-8, 150), "Hidden OCR text", fontsize=12, render_mode=3))
        report = qa.inspect(self.pdf, self.out)
        self.assertNotIn("clipped_text", self.codes(report))

    def test_possible_overlap_is_a_warning_only(self):
        def prepare(page):
            page.insert_text((45, 150), "First overlapping line", fontsize=12)
            page.insert_text((50, 151), "Second overlapping line", fontsize=12)
        self.make_pdf(prepare=prepare)
        report = qa.inspect(self.pdf, self.out)
        self.assertIn("possible_text_overlap", self.codes(report, "warning"))
        self.assertFalse(self.codes(report, "blocker"))

    def test_warnings_require_explicit_observations(self):
        self.make_pdf()
        report = qa.inspect(self.pdf, self.out)
        self.assertIn("sparse_page", self.codes(report, "warning"))
        self.finish_review_fixture()
        review = self.review()
        review["warning_acknowledgements"][0]["observations"] = " "
        qa.write_json(self.out / "review.json", review)
        with self.assertRaisesRegex(ValueError, "Every warning"):
            qa.accept(self.out)

    def test_changed_pdf_revokes_existing_acceptance(self):
        self.make_pdf()
        qa.inspect(self.pdf, self.out)
        self.finish_review_fixture()
        qa.accept(self.out)
        self.make_pdf(("Changed content after signoff",))
        with self.assertRaisesRegex(ValueError, "pdf changed"):
            qa.accept(self.out)
        self.assertFalse((self.out / "acceptance.json").exists())

    def test_changed_docx_and_expectations_are_rejected(self):
        self.make_pdf()
        docx = self.make_docx()
        expectations = self.make_expectations({"required_text": ["Heading"]})
        qa.inspect(self.pdf, self.out, docx=docx, expectations=expectations)
        self.finish_review_fixture()
        acceptance = qa.accept(self.out)
        self.assertEqual(set(acceptance["inputs"]), {"pdf", "docx", "expectations"})
        with docx.open("ab") as stream:
            stream.write(b"changed")
        with self.assertRaisesRegex(ValueError, "docx changed"):
            qa.accept(self.out)
        self.make_docx()
        qa.inspect(self.pdf, self.out, docx=docx, expectations=expectations)
        self.finish_review_fixture()
        expectations.write_text('{"required_text": []}')
        with self.assertRaisesRegex(ValueError, "expectations changed"):
            qa.accept(self.out)

    def test_changed_image_or_inspection_is_rejected(self):
        self.make_pdf()
        qa.inspect(self.pdf, self.out)
        self.finish_review_fixture()
        with (self.out / "page-001.png").open("ab") as stream:
            stream.write(b"changed")
        with self.assertRaisesRegex(ValueError, "image changed"):
            qa.accept(self.out)
        qa.inspect(self.pdf, self.out)
        self.finish_review_fixture()
        report_path = self.out / "inspection.json"
        report = json.loads(report_path.read_text())
        report["findings"] = []
        qa.write_json(report_path, report)
        with self.assertRaisesRegex(ValueError, "inspection changed"):
            qa.accept(self.out)

    def test_render_manifest_binds_source_reference_resources_and_implicit_docx(self):
        self.make_pdf()
        manifest = self.make_render_manifest()
        report = qa.inspect(self.pdf, self.out, render=manifest)
        self.assertFalse(self.codes(report, "blocker"))
        self.assertEqual(set(report["inputs"]), {"pdf", "docx", "render_manifest", "source", "reference", "resource_001"})
        self.finish_review_fixture()
        self.assertEqual(qa.accept(self.out)["inputs"], report["inputs"])

    def test_changed_source_revokes_acceptance_and_blocks_reinspection(self):
        self.make_pdf()
        manifest = self.make_render_manifest()
        qa.inspect(self.pdf, self.out, render=manifest)
        self.finish_review_fixture()
        qa.accept(self.out)
        (self.root / "source.md").write_text("# Revised source\nThe old PDF lacks these changes.\n")
        with self.assertRaisesRegex(ValueError, "source changed"):
            qa.accept(self.out)
        self.assertFalse((self.out / "acceptance.json").exists())
        report = qa.inspect(self.pdf, self.out, render=manifest)
        self.assertIn("invalid_render_manifest", self.codes(report, "blocker"))
        self.assertEqual(report["page_count"], 1)
        self.assertTrue((self.out / "page-001.png").is_file())

    def test_failed_new_render_invalidates_old_artifacts_and_signoff(self):
        self.make_pdf()
        manifest = self.make_render_manifest()
        qa.inspect(self.pdf, self.out, render=manifest)
        self.finish_review_fixture()
        qa.accept(self.out)
        previous_pdf_hash = qa.sha256(self.pdf)
        qa.write_json(manifest, {"status": "failed", "error": "Writer unavailable"})
        self.assertEqual(qa.sha256(self.pdf), previous_pdf_hash)
        with self.assertRaisesRegex(ValueError, "render_manifest changed"):
            qa.accept(self.out)
        self.assertFalse((self.out / "acceptance.json").exists())
        report = qa.inspect(self.pdf, self.out, render=manifest)
        self.assertIn("render_not_ready", self.codes(report, "blocker"))
        self.assertEqual(report["page_count"], 1)
        self.finish_review_fixture()
        with self.assertRaisesRegex(ValueError, "machine blockers"):
            qa.accept(self.out)

    def test_in_progress_render_is_not_a_completed_snapshot(self):
        self.make_pdf()
        manifest = self.root / "render.json"
        qa.write_json(manifest, {"status": "rendering"})
        report = qa.inspect(self.pdf, self.out, render=manifest)
        self.assertIn("render_not_ready", self.codes(report, "blocker"))

    def test_reference_and_resource_changes_invalidate_manifest_inspection(self):
        self.make_pdf()
        for name, filename in (("reference", "reference.docx"), ("resource_001", "chart.svg")):
            with self.subTest(name=name):
                manifest = self.make_render_manifest()
                qa.inspect(self.pdf, self.out, render=manifest)
                self.finish_review_fixture()
                with (self.root / filename).open("ab") as stream:
                    stream.write(b"changed")
                with self.assertRaisesRegex(ValueError, f"{name} changed"):
                    qa.accept(self.out)
                report = qa.inspect(self.pdf, self.out, render=manifest)
                self.assertIn("invalid_render_manifest", self.codes(report, "blocker"))

    def test_manifest_outputs_must_match_actual_inspected_files(self):
        self.make_pdf()
        manifest = self.make_render_manifest()
        other_docx = self.root / "different.docx"
        other_docx.write_bytes((self.root / "document.docx").read_bytes())
        report = qa.inspect(self.pdf, self.out, docx=other_docx, render=manifest)
        self.assertIn("invalid_render_manifest", self.codes(report, "blocker"))
        self.make_pdf(("This PDF changed after the render snapshot.",))
        report = qa.inspect(self.pdf, self.out, render=manifest)
        self.assertIn("invalid_render_manifest", self.codes(report, "blocker"))

    def test_malformed_manifest_produces_blockers_and_page_diagnostics(self):
        self.make_pdf()
        manifest = self.make_render_manifest()
        valid = json.loads(manifest.read_text())
        invalid_values = ["{broken JSON", "[]", '{"status":"needs-inspection"}', json.dumps({**valid, "resources": {"not": "a list"}})]
        for value in invalid_values:
            with self.subTest(value=value):
                manifest.write_text(value)
                report = qa.inspect(self.pdf, self.out, render=manifest)
                self.assertIn("invalid_render_manifest", self.codes(report, "blocker"))
                self.assertEqual(report["page_count"], 1)
                self.assertTrue((self.out / "inspection.json").is_file())

    def test_same_page_relationship_is_checked_against_actual_pdf(self):
        self.make_pdf(("Section title", "Opening paragraph"))
        expectations = self.make_expectations({"same_page": [{"first": "Section title", "second": "Opening paragraph", "reason": "Keep heading with opening paragraph"}]})
        report = qa.inspect(self.pdf, self.out, expectations=expectations)
        self.assertIn("split_relationship", self.codes(report, "blocker"))
        self.make_pdf(("Section title\nOpening paragraph",))
        report = qa.inspect(self.pdf, self.out, expectations=expectations)
        self.assertFalse(self.codes(report, "blocker"))

    def test_repeated_matches_need_review_instead_of_false_pagination_failure(self):
        self.make_pdf(("Common heading\nFirst paragraph", "Common heading\nSecond paragraph"))
        expectations = self.make_expectations({"same_page": [{"first": "Common heading", "second": "Second paragraph", "reason": "Heading with its own paragraph"}]})
        report = qa.inspect(self.pdf, self.out, expectations=expectations)
        self.assertIn("ambiguous_relationship", self.codes(report, "warning"))
        self.assertNotIn("split_relationship", self.codes(report, "blocker"))
        evidence = next(f["evidence"] for f in report["findings"] if f["code"] == "ambiguous_relationship")
        self.assertEqual(evidence["first_pages"], [1, 2])

    def test_required_text_normalizes_whitespace_but_missing_text_blocks(self):
        self.make_pdf(("Required\ncontent appears",))
        expectations = self.make_expectations({"required_text": ["Required content", "Absent content"]})
        report = qa.inspect(self.pdf, self.out, expectations=expectations)
        missing = [f for f in report["findings"] if f["code"] == "required_text_missing"]
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0]["evidence"]["text"], "Absent content")

    def test_chinese_wrapping_and_cross_page_presence(self):
        first = "这是一段用于检查自动换行的中文"
        second = "文字，必须保持连续匹配。"
        self.make_pdf(("",), prepare=lambda page: page.insert_text((45, 60), first + "\n" + second, fontname="china-s", fontsize=12))
        expectations = self.make_expectations({"required_text": [first + second], "same_page": [{"first": first, "second": second, "reason": "Heading and following text"}]})
        report = qa.inspect(self.pdf, self.out, expectations=expectations)
        self.assertFalse(self.codes(report, "blocker"))
        with pymupdf.open() as document:
            for content in (first, second):
                page = document.new_page(width=400, height=500)
                page.insert_text((45, 60), content, fontname="china-s", fontsize=12)
            document.save(self.pdf)
        report = qa.inspect(self.pdf, self.out, expectations=expectations)
        self.assertNotIn("required_text_missing", self.codes(report))
        self.assertIn("split_relationship", self.codes(report, "blocker"))

    def test_ligatures_and_soft_hyphens_match_plain_source_text(self):
        def prepare(page):
            page.insert_font(fontname="fixture", fontbuffer=pymupdf.Font("cjk").buffer)
            page.insert_text((45, 120), "of\ufb01ce co\u00adoperate", fontname="fixture", fontsize=12)
        self.make_pdf(prepare=prepare)
        expectations = self.make_expectations({"required_text": ["office cooperate"]})
        report = qa.inspect(self.pdf, self.out, expectations=expectations)
        self.assertFalse(self.codes(report, "blocker"))

    @unittest.skipUnless(shutil.which("soffice"), "RTL extraction fixture needs LibreOffice Writer")
    def test_real_arabic_export_preserves_logical_words_and_detects_missing_text(self):
        fixture = Path(__file__).parent / "fixtures" / "rtl.md"
        destination = self.root / "rtl-export"
        subprocess.run([sys.executable, str(SCRIPT.with_name("render_document.py")),
                        str(fixture), "--out", str(destination)],
                       check=True, capture_output=True, text=True, timeout=180)
        report = qa.inspect(destination / "rtl.pdf", self.out,
                            expectations=destination / "expectations.json",
                            render=destination / "render.json")
        self.assertFalse(self.codes(report, "blocker"))
        self.assertNotIn("off_page_text", self.codes(report))
        expectations = self.make_expectations({
            "required_text": ["ملاحظات إضافية", "هذه وثيقة لاختبار", "كلمة غير موجودة"],
            "same_page": [{"first": "خطوات العمل", "second": "كلمة غير موجودة", "reason": "Missing Arabic content must still fail"}],
        })
        report = qa.inspect(destination / "rtl.pdf", self.out, expectations=expectations)
        missing = [finding for finding in report["findings"] if finding["code"] == "required_text_missing"]
        self.assertEqual([finding["evidence"]["text"] for finding in missing], ["كلمة غير موجودة"])
        self.assertIn("relationship_text_missing", self.codes(report, "blocker"))

    def test_off_page_text_cannot_satisfy_content_expectations(self):
        self.make_pdf(prepare=lambda page: page.insert_text((450, 200), "Entirely outside", fontsize=12))
        expectations = self.make_expectations({"required_text": ["Entirely outside"]})
        report = qa.inspect(self.pdf, self.out, expectations=expectations)
        self.assertIn("required_text_missing", self.codes(report, "blocker"))
        self.assertIn("off_page_text", self.codes(report, "warning"))

    def test_empty_or_unreadable_pdf_blocks(self):
        self.make_pdf(("",))
        report = qa.inspect(self.pdf, self.out)
        self.assertIn("empty_pdf", self.codes(report, "blocker"))
        self.pdf.write_bytes(b"not a PDF")
        report = qa.inspect(self.pdf, self.out)
        self.assertIn("unreadable_pdf", self.codes(report, "blocker"))
        self.assertEqual(report["page_count"], 0)

    def test_invalid_docx_blocks_and_reinspection_resets_review(self):
        self.make_pdf()
        qa.inspect(self.pdf, self.out)
        self.finish_review_fixture()
        qa.accept(self.out)
        docx = self.root / "invalid.docx"
        docx.write_bytes(b"invalid docx")
        report = qa.inspect(self.pdf, self.out, docx=docx)
        self.assertIn("invalid_docx", self.codes(report, "blocker"))
        self.assertFalse((self.out / "acceptance.json").exists())
        self.assertEqual(self.review()["pages"][0]["criteria"]["hierarchy"]["status"], "pending")


if __name__ == "__main__":
    unittest.main()
