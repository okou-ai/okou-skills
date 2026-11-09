#!/usr/bin/env python3
"""Lightweight office CLI contracts; no external engines or network required.

Run with the QA interpreter and -B, directly or via unittest discovery.
All command runners return CompletedProcess with text stdout/stderr.
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import xml.etree.ElementTree as ET
import zipfile

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1]
OFFICE = SCRIPTS.parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


office = load("office_under_test", SCRIPTS / "office.py")
control = load("office_existing_preflight", OFFICE / "xlsx/scripts/libreoffice_recalc.py")


def completed(argv, code=0, stdout="fake stdout", stderr="fake stderr"):
    return subprocess.CompletedProcess(argv, code, stdout, stderr)


def cached_copy(source, target, *, retain_formula=True):
    """Transform only the existing synthetic control, never a domain fixture."""
    with zipfile.ZipFile(source) as incoming, zipfile.ZipFile(target, "w") as outgoing:
        for name in incoming.namelist():
            content = incoming.read(name)
            if name == "xl/worksheets/sheet1.xml":
                root = ET.fromstring(content)
                cell = root.find(f"{control.S}sheetData/{control.S}row/{control.S}c[@r='C1']")
                cell.find(f"{control.S}v").text = "42"
                if not retain_formula:
                    cell.remove(cell.find(f"{control.S}f"))
                content = ET.tostring(root, encoding="utf-8")
            outgoing.writestr(name, content)


class OfficeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="office_unit_")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.source = self.directory / "source.xlsx"
        control._write_preflight_workbook(self.source)

    def invoke(self, argv, runner=None):
        stdout, stderr = io.StringIO(), io.StringIO()
        if runner is None:
            runner = mock.Mock(side_effect=AssertionError("Unexpected external command"))
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = office.main([str(arg) for arg in argv], runner=runner)
        # json.loads rejects extra receipts, prose, and other stdout pollution.
        receipt = json.loads(stdout.getvalue())
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(code, {"ok": 0, "failed": 1, "unavailable": 2}[receipt["status"]])
        self.assertEqual(receipt["schema_version"], 1)
        return code, receipt

    def recalc_args(self, out=None):
        return ["recalc", "--input", self.source, "--out", out or self.directory / "result.xlsx"]

    def style_fixture(self):
        import openpyxl
        path = self.directory / "plain.xlsx"
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet["A1"], sheet["B1"] = 0.25, "=A1*2"
        sheet["A3"], sheet["B3"] = "First", "Second"
        workbook.save(path)
        workbook.close()
        return path

    def style_args(self, source, operations, out=None):
        plan = self.directory / "plan.json"
        plan.write_text(json.dumps({"operations": operations}), encoding="utf-8")
        return ["style", "--input", source, "--out", out or self.directory / "styled.xlsx",
                "--plan", plan, "--use-finance-defaults"]

    def test_list_discovery_has_scopes_and_existing_primitives(self):
        code, receipt = self.invoke(["list"])
        self.assertEqual(code, 0)
        self.assertEqual(set(receipt["capabilities"]), set(office.TOOLS))
        self.assertEqual(receipt["style_primitives"], ["style_value", "report_band", "table_header", "report_page"])
        for name, item in receipt["capabilities"].items():
            self.assertTrue(item["scope"], name)
            self.assertTrue(item["argv"], name)
            self.assertTrue(any(str(OFFICE) in arg for arg in item["argv"]), name)
        self.assertIn("not formula evaluation", receipt["capabilities"]["xlsx-formulas"]["scope"])
        self.assertEqual(receipt["steps"], [])
        self.assertEqual(receipt["artifacts"], [])

    def test_parser_and_input_errors_are_one_json_failure(self):
        for argv in ([], ["unknown"], ["recalc"], ["preflight", "--format", "xlsx", "--timeout", "0"],
                     ["validate", "--input", self.directory / "missing.xlsx"],
                     ["preflight", "--format", "xlsx", "--rendering"]):
            with self.subTest(argv=argv):
                code, receipt = self.invoke(argv)
                self.assertEqual(code, 1)
                self.assertTrue(receipt["error"])
                self.assertEqual(receipt["artifacts"], [])

    def test_direct_cli_from_arbitrary_cwd(self):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        for arguments, expected in ((["list"], 0), (["not-a-command"], 1)):
            with self.subTest(arguments=arguments):
                result = subprocess.run([sys.executable, "-B", str(SCRIPTS / "office.py"), *arguments],
                                        cwd=self.directory, env=env, capture_output=True, text=True, timeout=15)
                self.assertEqual(result.returncode, expected)
                self.assertEqual(result.stderr, "")
                receipt = json.loads(result.stdout)
                self.assertEqual(receipt["status"], "ok" if expected == 0 else "failed")
                if expected == 0:
                    self.assertEqual(receipt["capabilities"]["xlsx-formulas"]["argv"][1],
                                     str(OFFICE / "xlsx/scripts/formula_check.py"))

    def test_unavailable_failed_and_missing_executable_never_pass(self):
        for code, expected in ((1, "failed"), (2, "unavailable")):
            with self.subTest(code=code):
                runner = mock.Mock(side_effect=lambda argv, timeout: completed(argv, code))
                actual, receipt = self.invoke(["preflight", "--format", "xlsx"], runner)
                self.assertEqual(actual, code)
                self.assertEqual(receipt["steps"][0]["status"], expected)
                self.assertEqual(receipt["steps"][0]["stdout"], "fake stdout")
                self.assertEqual(receipt["steps"][0]["stderr"], "fake stderr")
                runner.assert_called_once()
        runner = mock.Mock(side_effect=FileNotFoundError("engine absent"))
        code, receipt = self.invoke(["preflight", "--format", "xlsx"], runner)
        self.assertEqual(code, 2)
        self.assertEqual(receipt["steps"][0]["status"], "unavailable")
        self.assertEqual(receipt["artifacts"], [])

    def test_control_failure_stops_candidate_and_publication(self):
        before = self.source.read_bytes()
        for status in (1, 2):
            with self.subTest(status=status):
                runner = mock.Mock(side_effect=lambda argv, timeout: completed(argv, status))
                with mock.patch.object(office, "publish") as publication:
                    code, receipt = self.invoke(self.recalc_args(), runner)
                self.assertNotEqual(code, 0)
                runner.assert_called_once()
                self.assertIn("--preflight", runner.call_args.args[0])
                publication.assert_not_called()
                self.assertFalse((self.directory / "result.xlsx").exists())
                self.assertEqual(receipt["artifacts"], [])
        self.assertEqual(self.source.read_bytes(), before)

    def test_docx_rendering_control_is_required_after_environment(self):
        calls = []
        def runner(argv, timeout):
            calls.append(argv)
            return completed(argv, 0 if len(calls) == 1 else 1)
        code, receipt = self.invoke(["preflight", "--format", "docx", "--rendering"], runner)
        self.assertEqual(code, 1)
        self.assertEqual([step["tool"] for step in receipt["steps"]], ["docx-env", "docx-render"])
        self.assertIn("--check", calls[1])
        self.assertEqual(receipt["steps"][1]["status"], "failed")

    def test_existing_output_and_same_source_refused_before_execution(self):
        for destination in (self.source, self.directory / "existing.xlsx"):
            with self.subTest(destination=destination):
                if destination != self.source:
                    destination.write_bytes(b"existing user output")
                before = destination.read_bytes()
                runner = mock.Mock()
                code, receipt = self.invoke(self.recalc_args(destination), runner)
                self.assertEqual(code, 1)
                self.assertIn("overwrite", receipt["error"])
                runner.assert_not_called()
                self.assertEqual(destination.read_bytes(), before)

    def test_fresh_path_rejects_dangling_symlink(self):
        link = self.directory / "dangling.xlsx"
        link.symlink_to(self.directory / "absent.xlsx")
        code, receipt = self.invoke(self.recalc_args(link))
        self.assertEqual(code, 1)
        self.assertTrue(link.is_symlink())
        self.assertIn("overwrite", receipt["error"])

    def test_exclusive_publish_does_not_overwrite_racing_destination(self):
        destination = self.directory / "raced.xlsx"
        destination.write_bytes(b"winner")
        with self.assertRaises(FileExistsError):
            office.publish(self.source, destination)
        self.assertEqual(destination.read_bytes(), b"winner")

    def test_existing_preflight_fixture_has_empty_cache_and_copy_is_rejected(self):
        formulas, missing = office.cache_snapshot(self.source)
        self.assertEqual(formulas, {"xl/worksheets/sheet1.xml!C1"})
        self.assertEqual(missing, ["xl/worksheets/sheet1.xml!C1"])
        def copy_only(source, output, timeout):
            shutil.copyfile(source, output)
            return True, "fake conversion copied input"
        with mock.patch.object(control, "find_soffice", return_value="fake-engine"), \
                mock.patch.object(control, "recalculate", side_effect=copy_only):
            code, message = control.preflight()
        self.assertEqual(code, 1)
        self.assertIn("cache", message)
        self.assertIn("FAILED", message)

    def test_preflight_rejects_literal_fake_answer_without_live_formula(self):
        def literal_only(source, output, timeout):
            cached_copy(source, output, retain_formula=False)
            return True, "fake literal answer"
        with mock.patch.object(control, "find_soffice", return_value="fake-engine"), \
                mock.patch.object(control, "recalculate", side_effect=literal_only):
            code, message = control.preflight()
        self.assertEqual(code, 1)
        self.assertIn("live formula", message)

    def test_candidate_copy_or_lost_formula_cannot_publish(self):
        before = self.source.read_bytes()
        for mode in ("copy", "literal"):
            with self.subTest(mode=mode):
                calls = []
                def runner(argv, timeout):
                    calls.append(argv)
                    if "--preflight" not in argv:
                        if mode == "copy":
                            shutil.copyfile(argv[2], argv[3])
                        else:
                            cached_copy(argv[2], argv[3], retain_formula=False)
                    return completed(argv)
                with mock.patch.object(office, "publish") as publication:
                    code, receipt = self.invoke(self.recalc_args(), runner)
                self.assertEqual(code, 1)
                self.assertEqual(len(calls), 2)
                self.assertIn("formula caches empty", receipt["error"])
                publication.assert_not_called()
                self.assertEqual(receipt["artifacts"], [])
        self.assertEqual(self.source.read_bytes(), before)

    def test_recalc_cache_readback_precedes_scan_and_publishes_copy(self):
        before = self.source.read_bytes()
        calls = []
        def runner(argv, timeout):
            calls.append(argv)
            if argv[1].endswith("libreoffice_recalc.py") and "--preflight" not in argv:
                cached_copy(argv[2], argv[3])
            return completed(argv)
        code, receipt = self.invoke(self.recalc_args(), runner)
        self.assertEqual(code, 0)
        self.assertEqual([step["tool"] for step in receipt["steps"]],
                         ["xlsx-preflight", "xlsx-preflight", "formula-cache-readback", "xlsx-formulas"])
        self.assertEqual(len(calls), 3)
        self.assertEqual(office.cache_snapshot(self.directory / "result.xlsx")[1], [])
        self.assertEqual(self.source.read_bytes(), before)
        artifact = receipt["artifacts"][0]
        self.assertEqual(artifact["sha256"], hashlib.sha256((self.directory / "result.xlsx").read_bytes()).hexdigest())
        self.assertIn("expected business values remain unverified", receipt["steps"][2]["scope"])

    def test_failed_static_scan_blocks_recalc_publication(self):
        def runner(argv, timeout):
            if argv[1].endswith("formula_check.py"):
                return completed(argv, 1)
            if "--preflight" not in argv:
                cached_copy(argv[2], argv[3])
            return completed(argv)
        code, receipt = self.invoke(self.recalc_args(), runner)
        self.assertEqual(code, 1)
        self.assertEqual(receipt["steps"][-1]["status"], "failed")
        self.assertFalse((self.directory / "result.xlsx").exists())
        self.assertEqual(receipt["artifacts"], [])

    def test_style_dispatches_all_existing_primitives_and_preserves_source(self):
        import openpyxl
        source = self.style_fixture()
        before = source.read_bytes()
        operations = [
            {"op": "style_value", "sheet": "Sheet", "cell": "A1", "role": "input", "kind": "percent"},
            {"op": "table_header", "sheet": "Sheet", "range": "A3:B3"},
            {"op": "report_band", "sheet": "Sheet", "range": "A5:B5", "text": "Title", "level": "title"},
            {"op": "report_page", "sheet": "Sheet", "range": "A1:B5", "orientation": "landscape"},
        ]
        primitives = load("office_real_primitives", OFFICE / "xlsx/scripts/xlsx_authoring.py")
        with contextlib.ExitStack() as stack:
            spies = {name: stack.enter_context(mock.patch.object(primitives, name, wraps=getattr(primitives, name)))
                     for name in ("style_value", "table_header", "report_band", "report_page")}
            loader = stack.enter_context(mock.patch.object(office, "load_module", return_value=primitives))
            code, receipt = self.invoke(self.style_args(source, operations))
        self.assertEqual(code, 0)
        loader.assert_called_once_with("office_xlsx_authoring", OFFICE / "xlsx/scripts/xlsx_authoring.py")
        for spy in spies.values():
            spy.assert_called_once()
        self.assertEqual(source.read_bytes(), before)
        workbook = openpyxl.load_workbook(self.directory / "styled.xlsx")
        try:
            sheet = workbook.active
            self.assertEqual(sheet["A1"].value, 0.25)
            self.assertEqual(sheet["B1"].value, "=A1*2")
            self.assertEqual(sheet["A1"].font.color.rgb, "FF0000FF")
            self.assertEqual(sheet["A1"].number_format, "0.0%;(0.0%);0.0%")
            self.assertTrue(sheet["A3"].font.bold)
            self.assertIn("A5:B5", sheet.merged_cells)
            self.assertEqual(sheet.page_setup.orientation, "landscape")
        finally:
            workbook.close()
        self.assertEqual(receipt["steps"][0]["operations"], 4)
        self.assertIn("invalidates formula caches", " ".join(receipt["limits"]))

    def test_invalid_plan_never_publishes_even_after_valid_operation(self):
        source = self.style_fixture()
        before = source.read_bytes()
        valid = {"op": "style_value", "sheet": "Sheet", "cell": "A1", "role": "input", "kind": "percent"}
        bad_operations = [[], [{"op": "unknown", "sheet": "Sheet"}],
                          [valid, {"op": "report_page", "sheet": "Sheet", "range": "A:A"}],
                          [dict(valid, surprise=True)], [dict(valid, cell="A1:B1")],
                          [dict(valid, role="same_sheet")]]
        for operations in bad_operations:
            with self.subTest(operations=operations):
                with mock.patch.object(office, "publish") as publication:
                    code, receipt = self.invoke(self.style_args(source, operations))
                self.assertEqual(code, 1)
                publication.assert_not_called()
                self.assertEqual(receipt["artifacts"], [])
                self.assertFalse((self.directory / "styled.xlsx").exists())
                self.assertEqual(source.read_bytes(), before)

    def test_style_requires_opt_in_and_refuses_same_source(self):
        source = self.style_fixture()
        operations = [{"op": "table_header", "sheet": "Sheet", "range": "A3:B3"}]
        before = source.read_bytes()
        for argv in (self.style_args(source, operations)[:-1], self.style_args(source, operations, source)):
            with self.subTest(argv=argv):
                code, receipt = self.invoke(argv)
                self.assertEqual(code, 1)
                self.assertEqual(receipt["artifacts"], [])
                self.assertEqual(source.read_bytes(), before)

    def test_validate_claims_static_not_business_or_formula_evaluation(self):
        runner = mock.Mock(side_effect=lambda argv, timeout: completed(argv, stdout='{"errors": []}', stderr=""))
        code, receipt = self.invoke(["validate", "--input", self.source, "--styles"], runner)
        self.assertEqual(code, 0)
        self.assertEqual([step["tool"] for step in receipt["steps"]], ["xlsx-formulas", "xlsx-styles"])
        self.assertIn("not formula evaluation", receipt["steps"][0]["scope"])
        self.assertIn("not all formatting or finance accuracy", receipt["steps"][1]["scope"])
        self.assertIn("No business", " ".join(receipt["limits"]))
        self.assertEqual(receipt["artifacts"], [])
        code, _ = self.invoke(["validate", "--input", self.source, "--business"])
        self.assertEqual(code, 1)

    def test_pdf_renderer_zero_exit_without_images_is_failure(self):
        source = self.directory / "source.pdf"
        source.write_bytes(b"%PDF-1.4\n")
        runner = mock.Mock(side_effect=lambda argv, timeout: completed(argv))
        pages = self.directory / "pages"
        code, receipt = self.invoke(["render", "--input", source, "--pages", pages], runner)
        self.assertEqual(code, 1)
        self.assertIn("no page images", receipt["error"])
        self.assertEqual(receipt["artifacts"], [])
        self.assertFalse(pages.exists())
        runner.assert_called_once()

    def test_docx_renderer_zero_exit_without_pdf_does_not_publish(self):
        source = self.directory / "source.docx"
        source.write_bytes(b"fake DOCX; runner is isolated")
        destination = self.directory / "rendered.pdf"
        runner = mock.Mock(side_effect=lambda argv, timeout: completed(argv))
        code, receipt = self.invoke(["render", "--input", source, "--out", destination], runner)
        self.assertEqual(code, 1)
        self.assertEqual(receipt["artifacts"], [])
        self.assertFalse(destination.exists(), "Failed rendering must not leave a published empty PDF")

    def test_docx_renderer_empty_pdf_is_not_pass(self):
        source = self.directory / "source.docx"
        source.write_bytes(b"fake DOCX; runner is isolated")
        destination = self.directory / "rendered.pdf"
        def runner(argv, timeout):
            Path(argv[argv.index("--out") + 1]).touch()
            return completed(argv)
        code, receipt = self.invoke(["render", "--input", source, "--out", destination], runner)
        self.assertEqual(code, 1, "An empty renderer output must not be reported as success")
        self.assertEqual(receipt["artifacts"], [])
        self.assertFalse(destination.exists())

    def test_creator_zero_exit_without_output_is_failure(self):
        content = self.directory / "content.json"
        content.write_text("{}", encoding="utf-8")
        destination = self.directory / "created.docx"
        runner = mock.Mock(side_effect=lambda argv, timeout: completed(argv))
        code, receipt = self.invoke(["create", "--format", "docx", "--content", content,
                                     "--title", "Title", "--out", destination], runner)
        self.assertEqual(code, 1)
        self.assertIn("no nonempty output", receipt["error"])
        self.assertEqual(receipt["artifacts"], [])
        self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
