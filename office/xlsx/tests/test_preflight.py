"""Independent formula-control tests; stdlib only, including an unskipped real-engine test.

Run deterministic fixtures alone with:
    python3 -m unittest discover -s office/xlsx/tests -p test_preflight.py -k PreflightUnitTests -v
Run the real Calc control explicitly (failure/unavailability is NOT turned into a skip):
    python3 -m unittest discover -s office/xlsx/tests -p test_preflight.py -k RealCalcPreflightTests -v
"""
import contextlib
import importlib.util
import io
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from urllib.parse import unquote, urlparse
import xml.etree.ElementTree as ET
import zipfile

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "libreoffice_recalc.py"
SPEC = importlib.util.spec_from_file_location("libreoffice_recalc_preflight_tests", SCRIPT)
recalc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(recalc)
S = recalc.S
SHEET = "xl/worksheets/sheet1.xml"


def rewrite_package(source, output, transform):
    """Change fixture OOXML in memory without external XLSX dependencies."""
    with zipfile.ZipFile(source) as package:
        parts = {name: package.read(name) for name in package.namelist()}
    transform(parts)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as package:
        for name, data in parts.items():
            package.writestr(name, data)


def change_formula_cache(parts, value="42", formula=recalc.CONTROL_FORMULA, cell_type=None):
    root = ET.fromstring(parts[SHEET])
    cell = root.find(f".//{S}c[@r='C1']")
    if cell_type is not None:
        cell.set("t", cell_type)
    f = cell.find(f"{S}f")
    if formula is None:
        cell.remove(f)
    else:
        f.text = formula
    v = cell.find(f"{S}v")
    if value is None:
        cell.remove(v)
    else:
        v.text = value
    parts[SHEET] = ET.tostring(root, encoding="utf-8", xml_declaration=True)


class PreflightUnitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="xlsx preflight tests ")
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.calls = []
        self.control_paths = []
        self.control_bytes = []

    def run_fixture(self, transform=None, *, produce_output=True, raw_output=None,
                    returncode=0, timeout=17):
        """Exercise real preflight -> recalculate, replacing only the engine call."""
        original_writer = recalc._write_preflight_workbook

        def writer(path):
            original_writer(path)
            self.control_paths.append(path)
            self.control_bytes.append(path.read_bytes())

        def engine(cmd, timeout):
            self.calls.append((cmd, timeout))
            source = Path(cmd[-1])
            outdir = Path(cmd[cmd.index("--outdir") + 1])
            self.assertNotEqual(source.parent, outdir)
            self.assertEqual(source.read_bytes(), self.control_bytes[-1])
            self.assertEqual(list(outdir.iterdir()), [])
            profile_arg = next(arg for arg in cmd if arg.startswith("-env:UserInstallation="))
            profile = Path(unquote(urlparse(profile_arg.split("=", 1)[1]).path))
            self.assertEqual(source.parent.parent, outdir.parent)
            self.assertEqual(profile.parent, outdir.parent)
            settings = (profile / "user/registrymodifications.xcu").read_text()
            self.assertIn("OOXMLRecalcMode", settings)
            self.assertIn("<value>0</value>", settings)
            if produce_output:
                output = outdir / f"{source.stem}.xlsx"
                if raw_output is not None:
                    output.write_bytes(raw_output)
                else:
                    rewrite_package(source, output, transform or change_formula_cache)
            return subprocess.CompletedProcess(cmd, returncode, b"fixture stdout", b"fixture stderr")

        with mock.patch.object(recalc, "find_soffice", return_value="/fixture/soffice"), \
                mock.patch.object(recalc, "get_libreoffice_version", return_value="fixture"), \
                mock.patch.object(recalc, "calc_component_diagnostic", return_value=""), \
                mock.patch.object(recalc, "_write_preflight_workbook", side_effect=writer), \
                mock.patch.object(recalc, "_run_soffice", side_effect=engine):
            code, message = recalc.preflight(timeout=timeout)
        # A conversion is never retried, even when exit zero, output, or verification fails.
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.calls[0][1], timeout)
        self.assertEqual(len(self.control_paths), 1)
        self.assertFalse(self.control_paths[0].parent.exists())
        source = Path(self.calls[0][0][-1])
        self.assertFalse(source.parent.parent.exists())
        return code, message

    def test_synthetic_input_is_complete_minimal_ooxml_with_empty_formula_cache(self):
        path = self.work / "control.xlsx"
        recalc._write_preflight_workbook(path)
        with zipfile.ZipFile(path) as package:
            self.assertEqual(set(package.namelist()), {
                "[Content_Types].xml", "_rels/.rels", "xl/workbook.xml",
                "xl/_rels/workbook.xml.rels", SHEET,
            })
            roots = {name: ET.fromstring(package.read(name)) for name in package.namelist()}
        self.assertEqual(roots["[Content_Types].xml"].tag,
                         "{http://schemas.openxmlformats.org/package/2006/content-types}Types")
        rel = roots["_rels/.rels"].find(f"{recalc.P}Relationship")
        self.assertEqual(rel.get("Target"), "xl/workbook.xml")
        self.assertEqual(rel.get("Type"), f"{recalc.R[1:-1]}/officeDocument")
        overrides = {item.get("PartName"): item.get("ContentType")
                     for item in roots["[Content_Types].xml"] if item.tag.endswith("}Override")}
        self.assertEqual(overrides["/xl/workbook.xml"],
                         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml")
        self.assertEqual(overrides["/xl/worksheets/sheet1.xml"],
                         "application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml")
        root = roots[SHEET]
        self.assertEqual(root.find(f".//{S}c[@r='A1']/{S}v").text, "19")
        self.assertEqual(root.find(f".//{S}c[@r='B1']/{S}v").text, "23")
        cell = root.find(f".//{S}c[@r='C1']")
        self.assertEqual(cell.find(f"{S}f").text, "SUM(A1:B1)")
        self.assertIsNone(cell.find(f"{S}v").text)
        self.assertNotEqual(recalc.CONTROL_EXPECTED, 0)

    def test_no_engine_is_exit_2_without_starting_a_control(self):
        with mock.patch.object(recalc, "find_soffice", return_value=None), \
                mock.patch.object(recalc, "recalculate") as pipeline, \
                mock.patch.object(recalc, "_write_preflight_workbook") as writer:
            code, message = recalc.preflight()
        self.assertEqual(code, 2)
        self.assertIn("not found", message)
        pipeline.assert_not_called()
        writer.assert_not_called()

    def test_exit_zero_without_new_output_fails(self):
        code, message = self.run_fixture(produce_output=False)
        self.assertEqual(code, 1, message)
        self.assertIn("exited 0 but produced no recalculated workbook", message)

    def test_copying_the_empty_input_cache_cannot_pass(self):
        code, message = self.run_fixture(transform=lambda parts: None)
        self.assertEqual(code, 1, message)
        self.assertIn("cache=''", message)

    def test_wrong_nonzero_cache_fails(self):
        code, message = self.run_fixture(transform=lambda parts: change_formula_cache(parts, "41"))
        self.assertEqual(code, 1, message)
        self.assertIn("expected cache 42", message)

    def test_empty_cache_fails(self):
        code, message = self.run_fixture(transform=lambda parts: change_formula_cache(parts, ""))
        self.assertEqual(code, 1, message)
        self.assertIn("cache=''", message)

    def test_missing_cache_fails(self):
        code, message = self.run_fixture(transform=lambda parts: change_formula_cache(parts, None))
        self.assertEqual(code, 1, message)
        self.assertIn("cache=''", message)

    def test_excel_error_cache_fails(self):
        code, message = self.run_fixture(
            transform=lambda parts: change_formula_cache(parts, "#DIV/0!", cell_type="e"))
        self.assertEqual(code, 1, message)
        self.assertIn("type='e'", message)
        self.assertIn("#DIV/0!", message)

    def test_numeric_looking_string_cache_fails(self):
        code, message = self.run_fixture(
            transform=lambda parts: change_formula_cache(parts, "42", cell_type="str"))
        self.assertEqual(code, 1, message)
        self.assertIn("type='str'", message)

    def test_nonnumeric_cache_fails(self):
        code, message = self.run_fixture(
            transform=lambda parts: change_formula_cache(parts, "not a number"))
        self.assertEqual(code, 1, message)
        self.assertIn("nonnumeric cache", message)

    def test_nonfinite_cache_fails(self):
        code, message = self.run_fixture(transform=lambda parts: change_formula_cache(parts, "NaN"))
        self.assertEqual(code, 1, message)
        self.assertIn("expected cache 42", message)

    def test_expected_cache_without_live_formula_fails(self):
        code, message = self.run_fixture(
            transform=lambda parts: change_formula_cache(parts, formula=None))
        self.assertEqual(code, 1, message)
        self.assertIn("lost the live formula", message)

    def test_replacing_the_formula_with_a_constant_formula_fails(self):
        code, message = self.run_fixture(
            transform=lambda parts: change_formula_cache(parts, formula="42"))
        self.assertEqual(code, 1, message)
        self.assertIn("lost the live formula", message)

    def test_malformed_zip_output_fails(self):
        code, message = self.run_fixture(raw_output=b"not an XLSX ZIP")
        self.assertEqual(code, 1, message)
        self.assertIn("could not be verified", message)

    def test_malformed_xml_output_fails(self):
        def corrupt(parts):
            parts[SHEET] = b"<worksheet>"
        code, message = self.run_fixture(transform=corrupt)
        self.assertEqual(code, 1, message)
        self.assertIn("could not be verified", message)

    def test_missing_output_worksheet_fails(self):
        def corrupt(parts):
            del parts[SHEET]
        code, message = self.run_fixture(transform=corrupt)
        self.assertEqual(code, 1, message)
        self.assertIn(SHEET, message)

    def test_missing_content_types_fails_even_with_the_expected_formula_and_cache(self):
        def corrupt(parts):
            change_formula_cache(parts)
            del parts["[Content_Types].xml"]
        code, message = self.run_fixture(transform=corrupt)
        self.assertEqual(code, 1, message)
        self.assertIn("[Content_Types].xml", message)

    def test_missing_workbook_relationship_fails_even_with_expected_formula_and_cache(self):
        def corrupt(parts):
            change_formula_cache(parts)
            root = ET.fromstring(parts["_rels/.rels"])
            root.remove(root[0])
            parts["_rels/.rels"] = ET.tostring(root)
        code, message = self.run_fixture(transform=corrupt)
        self.assertEqual(code, 1, message)
        self.assertIn("OOXML workbook relationship", message)

    def test_wrong_workbook_xml_root_fails(self):
        def corrupt(parts):
            parts["xl/workbook.xml"] = b"<not-a-workbook/>"
        code, message = self.run_fixture(transform=corrupt)
        self.assertEqual(code, 1, message)
        self.assertIn("OOXML workbook root", message)

    def test_lost_sheet_relationship_fails(self):
        def corrupt(parts):
            root = ET.fromstring(parts["xl/_rels/workbook.xml.rels"])
            root.remove(root[0])
            parts["xl/_rels/workbook.xml.rels"] = ET.tostring(root)
        code, message = self.run_fixture(transform=corrupt)
        self.assertEqual(code, 1, message)
        self.assertIn("worksheet relationship", message)

    def test_successful_synthetic_output_reopens_expected_formula_and_numeric_cache(self):
        code, message = self.run_fixture()
        self.assertEqual(code, 0, message)
        self.assertIn("reopened synthetic output", message)
        self.assertIn("SUM(A1:B1)", message)
        self.assertIn("cached value 42", message)
        self.assertIn("no candidate workbook was validated", message)

    def test_decimal_numeric_cache_and_absolute_worksheet_target_are_supported(self):
        def transformed(parts):
            change_formula_cache(parts, "42.0", cell_type="n")
            root = ET.fromstring(parts["xl/_rels/workbook.xml.rels"])
            root[0].set("Target", "/xl/worksheets/renamed.xml")
            parts["xl/_rels/workbook.xml.rels"] = ET.tostring(root)
            parts["xl/worksheets/renamed.xml"] = parts.pop(SHEET)
            types = ET.fromstring(parts["[Content_Types].xml"])
            for item in types:
                if item.get("PartName") == f"/{SHEET}":
                    item.set("PartName", "/xl/worksheets/renamed.xml")
            parts["[Content_Types].xml"] = ET.tostring(types)
        code, message = self.run_fixture(transform=transformed)
        self.assertEqual(code, 0, message)

    def test_nonzero_engine_exit_is_not_retried(self):
        code, message = self.run_fixture(returncode=7, produce_output=False)
        self.assertEqual(code, 1, message)
        self.assertIn("exited with code 7", message)

    def test_pipeline_success_without_a_file_still_fails_verification(self):
        with mock.patch.object(recalc, "find_soffice", return_value="/fixture/soffice"), \
                mock.patch.object(recalc, "recalculate", return_value=(True, "pretend")) as pipeline:
            code, message = recalc.preflight()
        self.assertEqual(code, 1, message)
        self.assertIn("could not be verified", message)
        pipeline.assert_called_once()

    def test_synthetic_source_is_preserved_not_just_candidate_inputs(self):
        owned = []

        def mutate_source(source, output, timeout):
            owned.append(Path(source).parent)
            shutil.copyfile(source, output)
            Path(source).write_bytes(b"modified")
            return True, "pretend"

        with mock.patch.object(recalc, "find_soffice", return_value="/fixture/soffice"), \
                mock.patch.object(recalc, "recalculate", side_effect=mutate_source) as pipeline:
            code, message = recalc.preflight()
        self.assertEqual(code, 1, message)
        self.assertIn("source workbook was modified", message)
        pipeline.assert_called_once()
        self.assertFalse(owned[0].exists())

    def test_normal_recalculate_preserves_input_and_existing_destination_on_failure(self):
        source = self.work / "input.xlsx"
        output = self.work / "existing.xlsx"
        recalc._write_preflight_workbook(source)
        before = source.read_bytes()
        output.write_bytes(b"existing destination")
        completed = subprocess.CompletedProcess([], 0, b"", b"")
        with mock.patch.object(recalc, "find_soffice", return_value="/fixture/soffice"), \
                mock.patch.object(recalc, "get_libreoffice_version", return_value="fixture"), \
                mock.patch.object(recalc, "_run_soffice", return_value=completed) as engine:
            success, message = recalc.recalculate(str(source), str(output))
        self.assertFalse(success, message)
        self.assertEqual(source.read_bytes(), before)
        self.assertEqual(output.read_bytes(), b"existing destination")
        engine.assert_called_once()

    def test_normal_recalculate_preserves_input_on_success(self):
        source = self.work / "input.xlsx"
        output = self.work / "output.xlsx"
        recalc._write_preflight_workbook(source)
        before = source.read_bytes()

        def engine(cmd, timeout):
            outdir = Path(cmd[cmd.index("--outdir") + 1])
            rewrite_package(Path(cmd[-1]), outdir / source.name, change_formula_cache)
            return subprocess.CompletedProcess(cmd, 0, b"", b"")

        with mock.patch.object(recalc, "find_soffice", return_value="/fixture/soffice"), \
                mock.patch.object(recalc, "get_libreoffice_version", return_value="fixture"), \
                mock.patch.object(recalc, "_run_soffice", side_effect=engine) as mocked:
            success, message = recalc.recalculate(str(source), str(output))
        self.assertTrue(success, message)
        self.assertEqual(source.read_bytes(), before)
        recalc._verify_preflight_output(output)
        mocked.assert_called_once()

    def test_timeout_is_not_retried_and_temp_resources_are_removed(self):
        owned = []

        def timeout(cmd, timeout):
            owned.append(Path(cmd[-1]).parent.parent)
            raise subprocess.TimeoutExpired(cmd, timeout)

        with mock.patch.object(recalc, "find_soffice", return_value="/fixture/soffice"), \
                mock.patch.object(recalc, "get_libreoffice_version", return_value="fixture"), \
                mock.patch.object(recalc, "_run_soffice", side_effect=timeout) as engine:
            code, message = recalc.preflight(timeout=3)
        self.assertEqual(code, 1, message)
        self.assertIn("timed out after 3s", message)
        engine.assert_called_once()
        self.assertFalse(owned[0].exists())

    def test_missing_calc_diagnostic_is_layout_specific_not_a_formula_test(self):
        program = self.work / "installation/program"
        registry = program.parent / "share/registry"
        program.mkdir(parents=True)
        registry.mkdir(parents=True)
        binary = program / "soffice"
        binary.touch()
        self.assertEqual(recalc.calc_component_diagnostic(str(binary)), "")
        (registry / "main.xcd").write_text("fixture")
        diagnostic = recalc.calc_component_diagnostic(str(binary))
        self.assertIn("Calc component appears missing", diagnostic)
        self.assertIn("No installation was attempted", diagnostic)
        (registry / "calc.xcd").write_text("fixture")
        self.assertEqual(recalc.calc_component_diagnostic(str(binary)), "")

    def test_check_is_availability_only_even_when_calc_is_missing(self):
        with mock.patch.object(sys, "argv", [str(SCRIPT), "--check"]), \
                mock.patch.object(recalc, "find_soffice", return_value="/fixture/soffice"), \
                mock.patch.object(recalc, "get_libreoffice_version", return_value="fixture"), \
                mock.patch.object(recalc, "calc_component_diagnostic", return_value="Calc component appears missing"), \
                mock.patch.object(recalc, "preflight") as control, \
                mock.patch.object(recalc, "recalculate") as pipeline, \
                contextlib.redirect_stdout(io.StringIO()) as output:
            with self.assertRaises(SystemExit) as ended:
                recalc.main()
        self.assertEqual(ended.exception.code, 0)
        self.assertIn("Availability-only", output.getvalue())
        self.assertIn("Calc component appears missing", output.getvalue())
        control.assert_not_called()
        pipeline.assert_not_called()

    def test_cli_preflight_uses_its_status_and_timeout_without_candidate_paths(self):
        with mock.patch.object(sys, "argv", [str(SCRIPT), "--preflight", "--timeout", "9"]), \
                mock.patch.object(recalc, "preflight", return_value=(1, "failed control")) as control, \
                contextlib.redirect_stdout(io.StringIO()) as output:
            with self.assertRaises(SystemExit) as ended:
                recalc.main()
        self.assertEqual(ended.exception.code, 1)
        control.assert_called_once_with(timeout=9)
        self.assertIn("failed control", output.getvalue())

    def test_cli_preflight_rejects_candidate_paths_without_inspecting_them(self):
        with mock.patch.object(sys, "argv", [str(SCRIPT), "candidate.xlsx", "out.xlsx", "--preflight"]), \
                mock.patch.object(recalc, "preflight") as control, \
                contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as ended:
                recalc.main()
        self.assertEqual(ended.exception.code, 1)
        control.assert_not_called()

    def test_version_probe_uses_an_isolated_temporary_profile(self):
        args = []

        def engine(cmd, timeout):
            args.append(cmd)
            self.assertEqual(timeout, 10)
            self.assertIn("--version", cmd)
            self.assertIn("--headless", cmd)
            return subprocess.CompletedProcess(cmd, 0, b"fixture version\n", b"")

        with mock.patch.object(recalc, "_run_soffice", side_effect=engine) as run:
            self.assertEqual(recalc.get_libreoffice_version("/fixture/soffice"), "fixture version")
        run.assert_called_once()
        profile_arg = next(arg for arg in args[0] if arg.startswith("-env:UserInstallation="))
        profile = Path(unquote(urlparse(profile_arg.split("=", 1)[1]).path))
        self.assertFalse(profile.parent.exists())

    def test_version_probe_failure_is_unknown_and_not_retried(self):
        with mock.patch.object(recalc, "_run_soffice", side_effect=OSError("fixture")) as engine:
            self.assertEqual(recalc.get_libreoffice_version("/fixture/soffice"), "unknown")
        engine.assert_called_once()

    @unittest.skipUnless(os.name == "posix", "POSIX process-group ownership fixture")
    def test_owned_process_group_is_scoped_and_direct_child_is_reaped_on_timeout(self):
        process = mock.Mock()
        process.pid = 123456
        process.communicate.side_effect = subprocess.TimeoutExpired(["fixture"], 1)
        with mock.patch.object(recalc.subprocess, "Popen", return_value=process) as popen, \
                mock.patch.object(recalc.os, "killpg") as killpg:
            with self.assertRaises(subprocess.TimeoutExpired):
                recalc._run_soffice(["fixture"], timeout=1)
        popen.assert_called_once_with(["fixture"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     start_new_session=True)
        killpg.assert_called_once_with(process.pid, signal.SIGKILL)
        process.wait.assert_called_once()
        process.stdout.close.assert_called_once()
        process.stderr.close.assert_called_once()
        process.kill.assert_not_called()

    @unittest.skipUnless(os.name == "posix", "POSIX process-group ownership fixture")
    def test_finished_invocation_also_cleans_only_its_owned_group(self):
        process = mock.Mock()
        process.pid = 123456
        process.returncode = 0
        process.communicate.return_value = (b"done", b"")
        with mock.patch.object(recalc.subprocess, "Popen", return_value=process), \
                mock.patch.object(recalc.os, "killpg") as killpg:
            result = recalc._run_soffice(["fixture"], timeout=2)
        self.assertEqual(result.stdout, b"done")
        self.assertEqual(result.returncode, 0)
        killpg.assert_called_once_with(process.pid, signal.SIGKILL)
        process.wait.assert_called_once()


class RealCalcPreflightTests(unittest.TestCase):
    def test_real_calc_independent_control(self):
        # Deliberately NOT skipped on missing binary/Calc: report the actual unavailable
        # environment instead of weakening the promised integration acceptance test.
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--preflight", "--timeout", "30"],
            capture_output=True, text=True, timeout=50,
        )
        self.assertEqual(
            result.returncode, 0,
            "Real Calc preflight failed or is unavailable (not a fixture pass):\n"
            + result.stdout + result.stderr,
        )
        self.assertIn("Preflight PASSED", result.stdout)
        self.assertIn("cached value 42", result.stdout)
        self.assertIn("no candidate workbook was validated", result.stdout)


if __name__ == "__main__":
    unittest.main()
