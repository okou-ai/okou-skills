"""Offline, standard-library regressions for lightweight PDF runtime paths.

Lightweight cases block native imports and process launches; setup routing uses
inert stubs. Optional native cases use already-installed PDF/plot packages only.
No browser, network or real installer is invoked by this suite.
"""

import builtins
from contextlib import ExitStack, contextmanager, redirect_stderr, redirect_stdout
import importlib
import importlib.util
import io
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
HELPERS = ("reformat_parse", "fill_inspect", "fill_write", "merge", "render_body", "palette", "cover")
DEPENDENCIES = {"pypdf", "reportlab", "matplotlib", "PIL", "numpy", "pip"}


@contextmanager
def blocked_runtime(missing=False):
    """Fail on any dependency probe or process launch, even if installed locally."""
    attempted = []
    original_import = builtins.__import__
    original_module = importlib.import_module
    original_spec = importlib.util.find_spec

    def check(name):
        if name.split(".", 1)[0] in DEPENDENCIES:
            attempted.append(name)
            if missing:
                raise ModuleNotFoundError(f"Simulated missing dependency: {name}", name=name)
            raise AssertionError(f"Unexpected dependency access: {name}")

    def guarded_import(name, *args, **kwargs):
        check(name)
        return original_import(name, *args, **kwargs)

    def guarded_module(name, *args, **kwargs):
        check(name)
        return original_module(name, *args, **kwargs)

    def guarded_spec(name, *args, **kwargs):
        check(name)
        return original_spec(name, *args, **kwargs)

    def no_process(*args, **kwargs):
        raise AssertionError("Runtime tried to launch a subprocess/installer")

    with ExitStack() as stack:
        stack.enter_context(patch("builtins.__import__", side_effect=guarded_import))
        stack.enter_context(patch("importlib.import_module", side_effect=guarded_module))
        stack.enter_context(patch("importlib.util.find_spec", side_effect=guarded_spec))
        for name in ("Popen", "run", "call", "check_call", "check_output"):
            stack.enter_context(patch.object(subprocess, name, side_effect=no_process))
        for name in ("system", "popen", "posix_spawn", "posix_spawnp"):
            if hasattr(os, name):
                stack.enter_context(patch.object(os, name, side_effect=no_process))
        yield attempted


def cli(name, *args):
    stdout, stderr = io.StringIO(), io.StringIO()
    with patch.object(sys, "argv", [str(SCRIPTS / (name + ".py")), *map(str, args)]), \
            redirect_stdout(stdout), redirect_stderr(stderr):
        try:
            runpy.run_path(str(SCRIPTS / (name + ".py")), run_name="__main__")
            code = 0
        except SystemExit as exc:
            code = exc.code
    return code, stdout.getvalue(), stderr.getvalue()


class LazyDependencyTests(unittest.TestCase):
    def setUp(self):
        work = tempfile.TemporaryDirectory(prefix="pdf-lazy-")
        self.addCleanup(work.cleanup)
        self.work = Path(work.name)
        self.output = self.work / "output.pdf"
        self.old = b"old output must survive"
        self.output.write_bytes(self.old)
        self.source = self.work / "source.pdf"
        self.source.write_bytes(b"placeholder; dependency failure precedes PDF decoding")
        self.content = self.work / "content.json"
        self.content.write_text('[{"type":"body","text":"Actual prose"}]')
        self.tokens = self.work / "tokens.json"
        palette = importlib.import_module("palette")
        self.tokens.write_text(json.dumps(palette.build_tokens("Test", "general")))

    def test_all_helper_imports_are_dependency_and_process_free(self):
        for name in (*HELPERS, "pdf_runtime"):
            with self.subTest(name=name), blocked_runtime() as attempted:
                # Execute a fresh module, so previous imports cannot mask bootstrap.
                runpy.run_path(str(SCRIPTS / (name + ".py")), run_name="pdf_import_test")
                self.assertEqual(attempted, [])

    def test_help_needs_no_pdf_or_optional_dependencies(self):
        for name in HELPERS:
            with self.subTest(name=name), blocked_runtime() as attempted:
                code, stdout, stderr = cli(name, "--help")
                self.assertEqual(code, 0, stderr)
                self.assertIn("usage:", stdout.lower())
                self.assertEqual(attempted, [])

    def test_nonpdf_parse_library_and_cli_use_only_stdlib(self):
        parser = importlib.import_module("reformat_parse")
        cases = {
            ".md": "# Heading\n\nActual prose.",
            ".markdown": "# Heading\n\nActual prose.",
            ".txt": "Actual prose.",
            ".json": '[{"type":"body","text":"Actual prose."}]',
        }
        for suffix, text in cases.items():
            source = self.work / ("input" + suffix)
            source.write_text(text)
            with self.subTest(suffix=suffix), blocked_runtime() as attempted:
                blocks, warnings = parser.parse_file(str(source))
                self.assertTrue(blocks)
                code, stdout, stderr = cli("reformat_parse", "--input", source, "--out", self.output)
                self.assertEqual(code, 0, stderr)
                self.assertEqual(json.loads(self.output.read_text()), blocks)
                self.assertEqual(attempted, [])

    def test_invalid_inputs_precede_dependency_loading_and_preserve_output(self):
        malformed = self.work / "malformed input"
        malformed.write_text("{broken JSON")
        bad = self.work / "bad.json"
        bad.write_text("[]")
        unknown = self.work / "unknown.json"
        unknown.write_text('[{"type":"unsupported"}]')
        cases = [
            ("fill_inspect", ["--input", self.work / "absent", "--out", self.output]),
            ("fill_inspect", ["--input", self.work, "--out", self.output]),
            ("fill_write", ["--input", self.work, "--out", self.output, "--values", '{"Name":"Jane"}']),
            ("fill_write", ["--input", self.source, "--out", self.output, "--values", "[]"]),
            ("fill_write", ["--input", self.source, "--out", self.output, "--values", "broken JSON"]),
            ("fill_write", ["--input", self.source, "--out", self.output, "--data", self.work / "absent.json"]),
            ("fill_write", ["--input", self.source, "--out", self.output, "--data", self.work]),
            ("fill_write", ["--input", self.source, "--out", self.output, "--data", malformed]),
            ("merge", ["--cover", self.source, "--body", self.work / "absent", "--out", self.output]),
            ("merge", ["--cover", self.source, "--body", self.work, "--out", self.output]),
            ("reformat_parse", ["--input", self.work / "absent.pdf", "--out", self.output]),
            ("reformat_parse", ["--input", self.work, "--out", self.output]),
            ("render_body", ["--tokens", self.tokens, "--content", bad, "--out", self.output]),
            ("render_body", ["--tokens", self.tokens, "--content", unknown, "--out", self.output]),
            ("render_body", ["--tokens", self.work, "--content", self.content, "--out", self.output]),
            ("render_body", ["--tokens", self.tokens, "--content", malformed, "--out", self.output]),
            ("render_body", ["--tokens", malformed, "--content", self.content, "--out", self.output]),
        ]
        for name, args in cases:
            with self.subTest(name=name, args=args), blocked_runtime() as attempted:
                code, stdout, stderr = cli(name, *args)
                self.assertNotEqual(code, 0)
                self.assertIn("error", stderr)
                self.assertEqual(attempted, [])
                self.assertEqual(self.output.read_bytes(), self.old)

    def test_reformat_suffix_dispatch_is_unchanged(self):
        for suffix in ("", ".data"):
            source = self.work / ("unknown-format" + suffix)
            source.write_text('[{"type":"body","text":"Actual prose"}]')
            with self.subTest(suffix=suffix), blocked_runtime() as attempted:
                code, stdout, stderr = cli("reformat_parse", "--input", source, "--out", self.output)
                self.assertEqual(code, 1, stderr)
                self.assertIn("Unsupported file type", stderr)
                self.assertEqual(attempted, [])
                self.assertEqual(self.output.read_bytes(), self.old)

    def test_argument_errors_do_not_probe_dependencies(self):
        for name in HELPERS:
            with self.subTest(name=name), blocked_runtime() as attempted:
                code, stdout, stderr = cli(name, "--not-a-real-argument")
                self.assertNotEqual(code, 0)
                self.assertEqual(attempted, [])

    def test_missing_dependencies_are_actionable_nonzero_and_preserve_output(self):
        cases = [
            ("reformat_parse", ["--input", self.source, "--out", self.output], "pypdf"),
            ("fill_inspect", ["--input", self.source, "--out", self.output], "pypdf"),
            ("fill_write", ["--input", self.source, "--out", self.output, "--values", '{"Name":"Jane Doe"}'], "pypdf"),
            ("merge", ["--cover", self.source, "--body", self.source, "--out", self.output], "pypdf"),
            ("render_body", ["--tokens", self.tokens, "--content", self.content, "--out", self.output], "reportlab"),
        ]
        for name, args, dependency in cases:
            with self.subTest(name=name), blocked_runtime(missing=True) as attempted:
                code, stdout, stderr = cli(name, *args)
                self.assertEqual(code, 2, stderr)
                self.assertIn(dependency, stderr)
                self.assertIn("fix --only", stderr)
                self.assertIn("No packages were installed", stderr)
                self.assertEqual(attempted, [dependency])
                self.assertEqual(self.output.read_bytes(), self.old)
                self.assertEqual(self.source.read_bytes(), b"placeholder; dependency failure precedes PDF decoding")
        self.assertEqual(list(self.work.glob(".pdf-*.tmp")), [])

    def test_plot_features_load_matplotlib_only_on_use(self):
        renderer = importlib.import_module("render_body")
        functions = [
            (renderer._render_math_png, ("E=mc^2",)),
            (renderer._render_chart_png, ({"labels": ["a"], "datasets": [{"values": [1]}]}, "#123456")),
            (renderer._render_flowchart_png, ({"nodes": [{"id": "a", "label": "Start"}], "edges": []}, "#123456", "#123456", "#123456")),
        ]
        for function, args in functions:
            with self.subTest(feature=function.__name__), blocked_runtime(missing=True) as attempted:
                with self.assertRaisesRegex(RuntimeError, "matplotlib.*No packages were installed"):
                    function(*args)
                self.assertEqual(attempted, ["matplotlib"])

    def test_fixed_format_outputs_do_not_alias_sources(self):
        aliases = {}
        for source in (self.source, self.tokens, self.content):
            hardlink = source.with_name(source.name + ".hardlink")
            symlink = source.with_name(source.name + ".symlink")
            os.link(source, hardlink)
            symlink.symlink_to(source)
            aliases[source] = (source, hardlink, symlink)
        cases = [
            ("fill_inspect", self.source, ["--input", self.source]),
            ("fill_write", self.source, ["--input", self.source, "--values", '{"Name":"Jane"}']),
            ("merge", self.source, ["--cover", self.source, "--body", self.source]),
            ("render_body", self.tokens, ["--tokens", self.tokens, "--content", self.content]),
            ("render_body", self.content, ["--tokens", self.tokens, "--content", self.content]),
        ]
        for name, source, args in cases:
            before = source.read_bytes()
            for output in aliases[source]:
                with self.subTest(name=name, output=output), blocked_runtime() as attempted:
                    code, stdout, stderr = cli(name, *args, "--out", output)
                    self.assertEqual(code, 1, stderr)
                    self.assertIn("Output must differ", stderr)
                    self.assertEqual(attempted, [])
                    self.assertEqual(source.read_bytes(), before)


@unittest.skipUnless(
    all(importlib.util.find_spec(name) is not None for name in ("pypdf", "reportlab")),
    "Optional native PDF checks require installed pypdf and reportlab; no installation attempted",
)
class NativePdfTests(unittest.TestCase):
    """Run offline, without Chromium, only when real PDF libraries already exist."""

    def setUp(self):
        work = tempfile.TemporaryDirectory(prefix="pdf-native-")
        self.addCleanup(work.cleanup)
        self.work = Path(work.name)
        from reportlab.pdfgen import canvas
        self.source = self.work / "form.pdf"
        document = canvas.Canvas(str(self.source))
        document.acroForm.textfield(name="Name", x=30, y=700, width=180)
        document.acroForm.checkbox(name="Agree", x=30, y=660)
        document.acroForm.choice(name="Country", options=["US", "UK"], value="US", x=30, y=620)
        document.showPage()
        document.save()
        self.output = self.work / "filled.pdf"
        self.output.write_bytes(b"old output")

    def test_fill_reopens_requested_values_and_keeps_source(self):
        from pypdf import PdfReader
        filler = importlib.import_module("fill_write")
        inspector = importlib.import_module("fill_inspect")
        before = self.source.read_bytes()
        result = filler.fill(str(self.source), str(self.output), {"Name": "Jane Doe", "Agree": True, "Country": "UK"})
        self.assertEqual(result["status"], "ok", result)
        actual = PdfReader(self.output).get_fields()
        self.assertEqual(str(actual["Name"]["/V"]), "Jane Doe")
        self.assertEqual(str(actual["Country"]["/V"]), "UK")
        self.assertNotEqual(str(actual["Agree"]["/V"]), "/Off")
        self.assertEqual(inspector.inspect(str(self.output))["field_count"], 3)
        self.assertEqual(self.source.read_bytes(), before)
        self.assertEqual(list(self.work.glob(".pdf-fill-*.tmp")), [])

    def test_invalid_choices_and_unknown_fields_are_nonfatal_warnings(self):
        from pypdf import PdfReader
        filler = importlib.import_module("fill_write")
        before = self.source.read_bytes()
        cases = [
            ({"Missing": "value"}, []),
            ({"Country": "not allowed"}, []),
            ({"Name": "Jane Doe", "Country": "not allowed", "Missing": "value"}, ["Name"]),
        ]
        for values, filled in cases:
            with self.subTest(values=values):
                self.output.write_bytes(b"old output")
                result = filler.fill(str(self.source), str(self.output), values)
                self.assertEqual(result["status"], "ok", result)
                self.assertNotIn("exit_code", result)
                self.assertEqual(result["filled_fields"], filled)
                self.assertEqual(result["filled_count"], len(filled))
                if "Country" in values:
                    self.assertEqual([error["field"] for error in result["validation_errors"]], ["Country"])
                if "Missing" in values:
                    self.assertEqual(result["not_found"], ["Missing"])
                actual = PdfReader(self.output).get_fields()
                self.assertEqual(str(actual["Country"]["/V"]), "US")
                if "Name" in values:
                    self.assertEqual(str(actual["Name"]["/V"]), "Jane Doe")
                self.assertEqual(self.source.read_bytes(), before)
                self.assertEqual(list(self.work.glob(".pdf-fill-*.tmp")), [])

    def test_fill_cli_succeeds_and_reports_field_warnings(self):
        from pypdf import PdfReader
        values = {"Name": "Jane Doe", "Country": "not allowed", "Missing": "value"}
        code, stdout, stderr = cli("fill_write", "--input", self.source, "--out", self.output,
                                   "--values", json.dumps(values))
        self.assertEqual(code, 0, stderr)
        result = json.loads(stdout)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["filled_fields"], ["Name"])
        self.assertEqual(result["not_found"], ["Missing"])
        self.assertEqual(result["validation_errors"][0]["field"], "Country")
        self.assertIn("Fill complete", stderr)
        self.assertIn("Errors :", stderr)
        self.assertIn("Not found:", stderr)
        self.assertEqual(str(PdfReader(self.output).get_fields()["Name"]["/V"]), "Jane Doe")

    def test_checkbox_keeps_legacy_truthy_and_unchecked_values(self):
        from pypdf import PdfReader
        filler = importlib.import_module("fill_write")
        cases = [(True, "/Yes"), ("YES", "/Yes"), (1, "/Yes"), ("on", "/Yes"),
                 (False, "/Off"), ("false", "/Off"), (0, "/Off"), (None, "/Off"),
                 ("ambiguous", "/Off"), (" true ", "/Off")]
        for value, expected in cases:
            with self.subTest(value=value):
                result = filler.fill(str(self.source), str(self.output), {"Agree": value})
                self.assertEqual(result["status"], "ok", result)
                self.assertEqual(result["filled_fields"], ["Agree"])
                self.assertNotIn("validation_errors", result)
                self.assertEqual(str(PdfReader(self.output).get_fields()["Agree"]["/V"]), expected)

    def test_radio_keeps_legacy_value_and_widget_state_handling(self):
        from pypdf import PdfReader
        from reportlab.pdfgen import canvas
        source = self.work / "radio.pdf"
        document = canvas.Canvas(str(source))
        document.acroForm.radio(name="Choice", value="One", selected=True, x=30, y=700)
        document.acroForm.radio(name="Choice", value="Two", selected=False, x=30, y=660)
        document.showPage()
        document.save()
        before = source.read_bytes()
        original = PdfReader(source).get_fields()["Choice"]
        widget_states = [str(kid.get_object().get("/AS")) for kid in original["/Kids"]]
        filler = importlib.import_module("fill_write")
        for value in ("Two", "/Two", "not-an-option"):
            with self.subTest(value=value):
                result = filler.fill(str(source), str(self.output), {"Choice": value})
                self.assertEqual(result["status"], "ok", result)
                self.assertNotIn("validation_errors", result)
                expected = value if value.startswith("/") else "/" + value
                actual = PdfReader(self.output).trailer["/Root"]["/AcroForm"]["/Fields"][0].get_object()
                self.assertEqual(str(actual["/V"]), expected)
                self.assertEqual(str(actual["/AS"]), expected)
                self.assertEqual([str(kid.get_object().get("/AS")) for kid in actual["/Kids"]], widget_states)
                self.assertEqual(source.read_bytes(), before)

    def test_fixed_format_clis_accept_extensionless_and_renamed_valid_input(self):
        from pypdf import PdfReader, PdfWriter
        tokens_value = importlib.import_module("palette").build_tokens("Compatibility", "general")
        for suffix in ("", ".txt"):
            with self.subTest(suffix=suffix):
                source = self.work / ("form input" + suffix)
                source.write_bytes(self.source.read_bytes())
                data = self.work / ("field values" + suffix)
                data.write_text('{"Name":"Jane Doe"}')
                tokens = self.work / ("design tokens" + suffix)
                tokens.write_text(json.dumps(tokens_value))
                content = self.work / ("body content" + suffix)
                content.write_text('[{"type":"body","text":"Extensionless actual prose"}]')
                cover = self.work / ("cover input" + suffix)
                writer = PdfWriter()
                writer.add_blank_page(width=595, height=842)
                writer.write(cover)
                originals = {path: path.read_bytes() for path in (source, data, tokens, content, cover)}

                code, stdout, stderr = cli("fill_inspect", "--input", source)
                self.assertEqual(code, 0, stderr)
                self.assertEqual(json.loads(stdout)["field_count"], 3)
                code, stdout, stderr = cli("fill_write", "--input", source, "--data", data, "--out", self.output)
                self.assertEqual(code, 0, stderr)
                self.assertEqual(str(PdfReader(self.output).get_fields()["Name"]["/V"]), "Jane Doe")
                body = self.work / ("body output" + suffix)
                code, stdout, stderr = cli("render_body", "--tokens", tokens, "--content", content, "--out", body)
                self.assertEqual(code, 0, stderr)
                self.assertIn("Extensionless actual prose", PdfReader(body).pages[0].extract_text())
                parsed = importlib.import_module("reformat_parse").parse_pdf(str(body))
                self.assertTrue(any("Extensionless actual prose" in block.get("text", "") for block in parsed))
                code, stdout, stderr = cli("merge", "--cover", cover, "--body", body, "--out", self.output)
                self.assertEqual(code, 0, stderr)
                self.assertEqual(len(PdfReader(self.output).pages), 2)
                for path, before in originals.items():
                    self.assertEqual(path.read_bytes(), before)
                self.assertEqual(list(self.work.glob(".pdf-*.tmp")), [])

    def test_renamed_invalid_pdfs_still_fail_in_the_actual_parser(self):
        source = self.work / "not-a-pdf.txt"
        source.write_bytes(b"not a PDF")
        cases = [
            ("fill_inspect", ["--input", source, "--out", self.output]),
            ("fill_write", ["--input", source, "--out", self.output, "--values", '{"Name":"Jane"}']),
            ("merge", ["--cover", self.source, "--body", source, "--out", self.output]),
        ]
        for name, args in cases:
            with self.subTest(name=name):
                code, stdout, stderr = cli(name, *args)
                self.assertEqual(code, 3, (stdout, stderr))
                self.assertIn('"status": "error"', stdout + stderr)
                self.assertNotIn("Unsupported file type", stdout + stderr)
                self.assertEqual(self.output.read_bytes(), b"old output")
                self.assertEqual(source.read_bytes(), b"not a PDF")
                self.assertEqual(list(self.work.glob(".pdf-*.tmp")), [])

    def test_fill_write_or_verification_failure_preserves_existing_output(self):
        filler = importlib.import_module("fill_write")
        before = self.source.read_bytes()
        patches = [
            patch("pypdf.PdfWriter.write", side_effect=OSError("simulated write failure")),
            patch("pypdf.PdfReader.get_fields", return_value={"Name": {"/V": "wrong value"}}),
        ]
        for failure in patches:
            with self.subTest(failure=failure), failure:
                result = filler.fill(str(self.source), str(self.output), {"Name": "Jane Doe"})
                self.assertEqual(result["status"], "error", result)
                self.assertIn("Write/verification failed", result["error"])
                self.assertEqual(self.output.read_bytes(), b"old output")
                self.assertEqual(self.source.read_bytes(), before)
                self.assertEqual(list(self.work.glob(".pdf-fill-*.tmp")), [])

    @unittest.skipUnless(importlib.util.find_spec("matplotlib"), "optional matplotlib is not installed")
    def test_lazy_plot_features_render_real_output(self):
        from pypdf import PdfReader
        renderer = importlib.import_module("render_body")
        tokens = importlib.import_module("palette").build_tokens("Feature test", "general")
        body = self.work / "features.pdf"
        blocks = [
            {"type": "h1", "text": "Model outputs"},
            {"type": "math", "text": r"\bar{x}=\frac{10+12}{2}", "label": "(1)"},
            {"type": "chart", "labels": ["Q1", "Q2"],
             "datasets": [{"label": "Revenue", "values": [10, 12]}]},
            {"type": "flowchart", "nodes": [{"id": "s", "label": "Start"},
                                              {"id": "e", "label": "End"}],
             "edges": [{"from": "s", "to": "e"}]},
            {"type": "code", "text": "print(1)", "language": "python"},
            {"type": "bibliography", "items": [{"id": "1", "text": "Supplied source"}]},
        ]
        with patch.dict(os.environ, {"MPLCONFIGDIR": str(self.work / "matplotlib")}):
            renderer.build(tokens, blocks, str(body))
        reader = PdfReader(body)
        text = "\n".join(page.extract_text() for page in reader.pages)
        self.assertIn("Model outputs", text)
        self.assertIn("print(1)", text)
        self.assertIn("Supplied source", text)
        self.assertGreaterEqual(sum(len(page.images) for page in reader.pages), 3)

    def test_body_and_merge_real_output_without_browser(self):
        from pypdf import PdfReader, PdfWriter
        renderer = importlib.import_module("render_body")
        tokens = importlib.import_module("palette").build_tokens("Test", "general")
        body = self.work / "body.pdf"
        renderer.build(tokens, [{"type": "body", "text": "Actual body content"}], str(body))
        self.assertIn("Actual body content", PdfReader(body).pages[0].extract_text())
        cover = self.work / "cover.pdf"
        writer = PdfWriter()
        writer.add_blank_page(width=595, height=842)
        writer.write(cover)
        merged = importlib.import_module("merge").merge(str(cover), str(body), str(self.output))
        self.assertEqual(merged["total_pages"], 2)
        self.assertEqual(len(PdfReader(self.output).pages), 2)
        self.assertEqual(list(self.work.glob(".pdf-*.tmp")), [])


class SetupRoutingTests(unittest.TestCase):
    def setUp(self):
        work = tempfile.TemporaryDirectory(prefix="pdf-routing-")
        self.addCleanup(work.cleanup)
        self.work = Path(work.name)
        self.commands = self.work / "commands.txt"
        # Every external dependency/installer executable is inert, including the
        # fake pip branch. A real package manager or browser can never be reached.
        for name in ("python3", "node", "npm", "npx"):
            stub = self.work / name
            stub.write_text(
                '#!/bin/sh\nprintf "%s\\n" "' + name + ' $*" >> "$PDF_TEST_COMMANDS"\n'
                'if [ "$1" = "-c" ]; then\n'
                '  case " ${PDF_TEST_AVAILABLE:-} " in *" $3 "*) exit 0 ;; *) exit 1 ;; esac\n'
                'fi\nexit 0\n'
            )
            stub.chmod(0o755)
        self.env = {**os.environ, "PATH": str(self.work) + os.pathsep + os.environ.get("PATH", ""),
                    "PDF_TEST_COMMANDS": str(self.commands), "PDF_TEST_AVAILABLE": ""}

    def invoke(self, *args):
        self.commands.write_text("")
        result = subprocess.run(["/bin/bash", str(SCRIPTS / "make.sh"), *args],
                                env=self.env, capture_output=True, text=True, timeout=10)
        return result, self.commands.read_text()

    def test_fill_check_and_explicit_fix_never_touch_authoring_or_browser(self):
        for command in ("check", "fix"):
            with self.subTest(command=command):
                result, commands = self.invoke(command, "--only", "fill")
                self.assertEqual(result.returncode, 2 if command == "check" else 0, result.stderr)
                self.assertIn("pypdf", commands)
                for unrelated in ("reportlab", "matplotlib", "node ", "npm ", "npx "):
                    self.assertNotIn(unrelated, commands)
                if command == "check":
                    self.assertNotIn("pip", commands)
                else:
                    self.assertIn("-m pip install -q pypdf", commands)

    def test_minimal_body_setup_excludes_pypdf_plots_and_browser(self):
        result, commands = self.invoke("fix", "--only", "body", "--minimal")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("-m pip install -q reportlab", commands)
        for unrelated in ("pypdf", "matplotlib", "node ", "npm ", "npx "):
            self.assertNotIn(unrelated, commands)

    def test_default_check_warns_but_succeeds_without_optional_matplotlib(self):
        self.env["PDF_TEST_AVAILABLE"] = "reportlab pypdf"
        result, commands = self.invoke("check")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Cannot load matplotlib", result.stdout)
        self.assertIn("required only for math/chart/flowchart blocks", result.stdout)
        for package in ("reportlab", "pypdf", "matplotlib"):
            self.assertIn(package, commands)
        self.assertIn("node ", commands)
        for installer in ("pip", "npm ", "npx "):
            self.assertNotIn(installer, commands)

    def test_explicit_plot_scopes_remain_strict(self):
        self.env["PDF_TEST_AVAILABLE"] = "reportlab pypdf"
        for scope in ("body", "pipeline"):
            with self.subTest(scope=scope):
                result, commands = self.invoke("check", "--only", scope)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("Cannot load matplotlib", result.stdout)
                self.assertNotIn("pip", commands)

    def test_default_check_still_requires_reportlab_and_pypdf(self):
        for missing in ("reportlab", "pypdf"):
            self.env["PDF_TEST_AVAILABLE"] = "pypdf" if missing == "reportlab" else "reportlab"
            with self.subTest(missing=missing):
                result, commands = self.invoke("check")
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("Cannot load " + missing, result.stdout)
                self.assertNotIn("pip", commands)

    def test_legacy_full_fix_and_minimal_pipeline_are_distinct(self):
        result, commands = self.invoke("fix")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("pip install -q reportlab pypdf matplotlib", commands)
        result, commands = self.invoke("check", "--minimal")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertNotIn("matplotlib", commands)
        self.assertNotIn("pip", commands)
        self.assertIn("node ", commands)  # inert --check, not a browser launch

    def test_setup_help_and_bad_arguments_do_not_check_or_install(self):
        for args in (("fix", "--help"), ("check", "--help"), ("fix", "--only", "wrong"),
                     ("fix", "--only"), ("run", "--content"), ("reformat", "--input")):
            with self.subTest(args=args):
                result, commands = self.invoke(*args)
                self.assertEqual(commands, "")

    def test_run_accepts_fixed_format_content_names_before_rendering(self):
        # Stop at the first rendering-stage command; no real renderer/browser runs.
        (self.work / "python3").write_text(
            '#!/bin/sh\nprintf "%s\\n" "python3 $*" >> "$PDF_TEST_COMMANDS"\nexit 17\n'
        )
        output = self.work / "output.pdf"
        output.write_bytes(b"old output")
        for suffix in ("", ".txt"):
            content = self.work / ("body content" + suffix)
            content.write_text('[{"type":"body","text":"Actual prose"}]')
            before = content.read_bytes()
            with self.subTest(suffix=suffix):
                result, commands = self.invoke("run", "--content", str(content), "--out", str(output))
                self.assertEqual(result.returncode, 17, result.stderr)
                self.assertIn("palette.py", commands)
                self.assertNotIn("node ", commands)
                self.assertEqual(content.read_bytes(), before)
                self.assertEqual(output.read_bytes(), b"old output")

    def test_run_keeps_regular_file_and_source_alias_guards(self):
        content = self.work / "body content"
        content.write_text('[{"type":"body","text":"Actual prose"}]')
        before = content.read_bytes()
        hardlink = self.work / "hardlink"
        os.link(content, hardlink)
        symlink = self.work / "symlink"
        symlink.symlink_to(content)
        cases = [(self.work, self.work / "out.pdf")]
        cases.extend((content, output) for output in (content, hardlink, symlink))
        for source, output in cases:
            with self.subTest(source=source, output=output):
                result, commands = self.invoke("run", "--content", str(source), "--out", str(output))
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertEqual(commands, "")
                self.assertEqual(content.read_bytes(), before)

    def test_shell_fill_preserves_inline_json_as_one_argument(self):
        args_file = self.work / "args.bin"
        (self.work / "python3").write_text('#!/bin/sh\nprintf "%s\\0" "$@" > "$PDF_TEST_ARGS"\n')
        self.env["PDF_TEST_ARGS"] = str(args_file)
        values = '{"Name": "Jane Doe", "Note": "Spaces and punctuation!"}'
        result, commands = self.invoke("fill", "--input", "form.pdf", "--out", "filled.pdf", "--values", values)
        self.assertEqual(result.returncode, 0, result.stderr)
        captured = args_file.read_bytes().split(b"\0")
        self.assertEqual(captured[-3:-1], [b"--values", values.encode()])


if __name__ == "__main__":
    unittest.main()
