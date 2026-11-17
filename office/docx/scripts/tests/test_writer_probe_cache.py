"""Task-local successful Writer capability receipts; stdlib and mocks only."""
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "render_docx.py"
SPEC = importlib.util.spec_from_file_location("render_docx_cache", SCRIPT)
RENDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RENDER)


class ProbeReceiptTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="writer-session-")
        self.addCleanup(self.directory.cleanup)
        self.addCleanup(patch.stopall)
        self.root = Path(self.directory.name)
        self.path = self.root / "writer.json"
        self.cache = RENDER.WriterProbeCache(self.path, "task-A")
        self.stderr = patch.object(sys, "stderr", io.StringIO()).start()
        patch.object(sys, "stdout", io.StringIO()).start()
        self.fingerprint_patcher = patch.object(RENDER, "writer_fingerprint", return_value="environment-A")
        self.fingerprint = self.fingerprint_patcher.start()
        self.probe = patch.object(RENDER, "check_writer").start()
        self.install = patch.object(RENDER, "install_dependencies").start()

    def run_main(self, *arguments):
        with patch.object(sys, "argv", [str(SCRIPT), *map(str, arguments)]):
            RENDER.main()

    def flags(self, session="task-A"):
        return ["--probe-cache", self.path, "--probe-session", session]

    def test_prepare_and_render_share_only_successful_capability_not_document_result(self):
        source = self.root / "source.docx"
        source.touch()
        output = self.root / "out.pdf"
        self.run_main("--prepare", *self.flags())
        receipt_before = self.path.read_text()
        with patch.object(RENDER, "render") as render:
            self.run_main(source, "--out", output, "--no-install", *self.flags())
            self.run_main(source, "--out", output, "--no-install", *self.flags())
        self.probe.assert_called_once_with(60)
        self.assertEqual(render.call_count, 2, "each candidate must convert, even with a receipt")
        self.assertEqual(receipt_before, self.path.read_text())
        receipt = json.loads(receipt_before)
        self.assertEqual(set(receipt), {"version", "success", "session", "fingerprint", "created"})
        self.assertNotIn("source.docx", receipt_before)
        self.assertNotIn("out.pdf", receipt_before)
        self.assertNotIn("task-A", receipt_before)
        self.install.assert_not_called()

    def test_no_opt_in_always_runs_control_and_never_reads_environment_or_receipt(self):
        self.run_main("--prepare")
        self.run_main("--prepare")
        self.assertEqual(self.probe.call_count, 2)
        self.fingerprint.assert_not_called()
        self.assertFalse(self.path.exists())

    def test_environment_change_forces_fresh_probe(self):
        RENDER.ensure_dependencies(probe_cache=self.cache)
        self.fingerprint.return_value = "environment-B"
        RENDER.ensure_dependencies(probe_cache=self.cache)
        self.assertEqual(self.probe.call_count, 2)
        self.assertEqual(json.loads(self.path.read_text())["fingerprint"], "environment-B")

    def test_changed_session_forces_fresh_probe(self):
        self.run_main("--prepare", *self.flags())
        self.run_main("--prepare", *self.flags("task-B"))
        self.assertEqual(self.probe.call_count, 2)

    def test_expired_future_malformed_or_wrong_version_receipt_is_not_trusted(self):
        RENDER.ensure_dependencies(probe_cache=self.cache)
        baseline = json.loads(self.path.read_text())
        for bad in ({**baseline, "created": time.time() - RENDER.PROBE_MAX_AGE - 2},
                    {**baseline, "created": time.time() + 100},
                    {**baseline, "version": -1}, {**baseline, "success": False},
                    {**baseline, "created": "unknown"}, [], "broken"):
            with self.subTest(bad=bad):
                self.path.write_text(json.dumps(bad))
                self.probe.reset_mock()
                RENDER.ensure_dependencies(probe_cache=self.cache)
                self.probe.assert_called_once()
                self.assertTrue(json.loads(self.path.read_text())["success"])

    def test_uninspectable_environment_never_caches(self):
        RENDER.ensure_dependencies(probe_cache=self.cache)
        self.fingerprint.return_value = None
        RENDER.ensure_dependencies(probe_cache=self.cache)
        RENDER.ensure_dependencies(probe_cache=self.cache)
        self.assertEqual(self.probe.call_count, 3)
        self.assertFalse(self.path.exists())

    def test_environment_changing_during_control_does_not_get_receipt(self):
        self.fingerprint.side_effect = ["before", "after"]
        RENDER.ensure_dependencies(probe_cache=self.cache)
        self.probe.assert_called_once()
        self.assertFalse(self.path.exists())

    def test_unknown_probe_failure_does_not_cache_install_or_repeat(self):
        for error in (subprocess.TimeoutExpired("soffice", 60), PermissionError("denied")):
            with self.subTest(error=error):
                self.probe.reset_mock()
                self.probe.side_effect = error
                with self.assertRaises(type(error)):
                    RENDER.ensure_dependencies(probe_cache=self.cache)
                self.probe.assert_called_once()
                self.install.assert_not_called()
                self.assertFalse(self.path.exists())

    def test_failed_control_with_no_install_never_caches_or_retries(self):
        self.probe.side_effect = RENDER.WriterUnavailableError("Writer missing")
        with self.assertRaisesRegex(RuntimeError, "disabled"):
            RENDER.ensure_dependencies(probe_cache=self.cache, install=False)
        self.probe.assert_called_once()
        self.install.assert_not_called()
        self.assertFalse(self.path.exists())

    def test_install_invalidates_then_records_only_post_install_probe(self):
        self.probe.side_effect = [RENDER.WriterUnavailableError("Writer missing"), None]
        self.fingerprint.side_effect = ["old-environment", "new-environment", "new-environment"]
        RENDER.ensure_dependencies(probe_cache=self.cache)
        self.install.assert_called_once_with(writer=True, pages=False)
        self.assertEqual(self.probe.call_count, 2)
        self.assertEqual(json.loads(self.path.read_text())["fingerprint"], "new-environment")

    def test_poppler_install_does_not_relabel_old_writer_probe(self):
        with patch.object(RENDER.shutil, "which", side_effect=[None, "pdftoppm"]):
            RENDER.ensure_dependencies(pages=True, probe_cache=self.cache)
        self.assertEqual(self.probe.call_count, 2, "installation changes environment: control must be fresh")
        self.install.assert_called_once_with(writer=False, pages=True)

    def test_candidate_failure_or_timeout_invalidates_without_retry_or_install(self):
        source = self.root / "bad.docx"
        source.touch()
        output = self.root / "previous.pdf"
        output.write_bytes(b"previous")
        for error in (RuntimeError("bad candidate"), subprocess.TimeoutExpired("soffice", 60),
                      PermissionError("conversion denied")):
            with self.subTest(error=error):
                self.run_main("--prepare", *self.flags())
                self.probe.reset_mock()
                with patch.object(RENDER, "render", side_effect=error) as render:
                    with self.assertRaises(SystemExit) as result:
                        self.run_main(source, "--out", output, "--no-install", *self.flags())
                    self.assertEqual(result.exception.code, 1)
                    render.assert_called_once()
                self.probe.assert_not_called()
                self.install.assert_not_called()
                self.assertFalse(self.path.exists())
                self.assertEqual(output.read_bytes(), b"previous")

    def test_check_is_fresh_and_read_only_no_receipts(self):
        for _ in range(2):
            self.run_main("--check")
        self.assertEqual(self.probe.call_count, 2)
        self.assertFalse(self.path.exists())
        with self.assertRaises(SystemExit) as result:
            self.run_main("--check", *self.flags())
        self.assertEqual(result.exception.code, 2)
        self.assertFalse(self.path.exists())

    def test_incomplete_cache_arguments_fail_before_probe(self):
        for arguments in (("--prepare", "--probe-cache", self.path),
                          ("--prepare", "--probe-session", "task"),
                          ("--prepare", "--probe-cache", self.path, "--probe-session", "")):
            with self.subTest(arguments=arguments):
                with self.assertRaises(SystemExit) as result:
                    self.run_main(*arguments)
                self.assertEqual(result.exception.code, 2)
        self.probe.assert_not_called()
        self.install.assert_not_called()

    def test_cache_cannot_alias_document_or_output(self):
        source = self.root / "source.docx"
        source.write_bytes(b"original")
        for aliased in (source, self.root / "out.pdf"):
            with self.subTest(aliased=aliased):
                with self.assertRaises(SystemExit) as result:
                    self.run_main(source, "--out", self.root / "out.pdf", "--probe-cache", aliased,
                                  "--probe-session", "task-A")
                self.assertEqual(result.exception.code, 2)
        self.assertEqual(source.read_bytes(), b"original")
        self.probe.assert_not_called()

    def test_receipt_file_is_private(self):
        RENDER.ensure_dependencies(probe_cache=self.cache)
        if os.name != "nt":
            self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)
        self.assertFalse(list(self.root.glob(".writer-receipt-*")))

    def test_fingerprint_changes_on_converter_filter_and_environment_updates(self):
        # Run the actual passive fingerprint function against a mock installation.
        host = self.root / "installation" / "program" / "soffice"
        host.parent.mkdir(parents=True)
        host.write_text("#!/bin/sh\n")
        filters = host.parent.parent / "share" / "registry"
        filters.mkdir(parents=True)
        registry = filters / "writer.xcd"
        registry.write_text("before")
        self.fingerprint_patcher.stop()
        with patch.object(RENDER, "find_soffice", return_value=str(host)):
            before = RENDER.writer_fingerprint()
            self.assertIsNotNone(before)
            host.write_text("#!/bin/sh\n# changed converter\n")
            converter_changed = RENDER.writer_fingerprint()
            self.assertNotEqual(before, converter_changed)
            registry.write_text("changed filter")
            filter_changed = RENDER.writer_fingerprint()
            self.assertNotEqual(converter_changed, filter_changed)
            with patch.dict(os.environ, {"SAL_USE_VCLPLUGIN": "changed"}):
                self.assertNotEqual(filter_changed, RENDER.writer_fingerprint())
            with patch.dict(os.environ, {"DOCX_UNRELATED_SECRET_TOKEN": "must-not-affect-capability"}):
                self.assertEqual(filter_changed, RENDER.writer_fingerprint())

    def test_fingerprint_is_bounded_and_never_walks_trees_or_starts_processes(self):
        host = self.root / "installation" / "program" / "soffice"
        host.parent.mkdir(parents=True)
        host.write_text("converter")
        (host.parent / "soffice.bin").write_text("runtime")
        self.fingerprint_patcher.stop()
        real_stat = Path.stat
        with patch.object(RENDER, "find_soffice", return_value=str(host)), \
                patch.object(RENDER.os, "walk") as walk, \
                patch.object(RENDER.subprocess, "run") as run, \
                patch.object(Path, "stat", autospec=True, side_effect=real_stat) as stat:
            self.assertIsNotNone(RENDER.writer_fingerprint())
            self.assertLessEqual(stat.call_count, 80)
            walk.assert_not_called()
            run.assert_not_called()

    def test_unknown_installation_or_bootstrap_override_misses_safely(self):
        host = self.root / "opaque-wrapper"
        host.write_text("converter wrapper")
        self.fingerprint_patcher.stop()
        with patch.object(RENDER, "find_soffice", return_value=str(host)):
            self.assertIsNone(RENDER.writer_fingerprint())
            with patch.dict(os.environ, {"URE_BOOTSTRAP": "custom-configuration"}):
                self.assertIsNone(RENDER.writer_fingerprint())


if __name__ == "__main__":
    unittest.main()
