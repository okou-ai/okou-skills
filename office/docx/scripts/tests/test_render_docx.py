"""Test lazy rendering setup without installing packages or using the network."""
import importlib.util
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile


SCRIPT = Path(__file__).resolve().parents[1] / "render_docx.py"
SPEC = importlib.util.spec_from_file_location("render_docx", SCRIPT)
RENDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RENDER)


class RenderingTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(patch.stopall)
        self.stderr = patch.object(sys, "stderr", io.StringIO()).start()
        patch.object(sys, "stdout", io.StringIO()).start()

    def test_pdf_only_does_not_check_or_install_poppler(self):
        with patch.object(RENDER, "check_writer") as probe, \
                patch.object(RENDER.shutil, "which") as which, \
                patch.object(RENDER, "install_dependencies") as install:
            RENDER.ensure_dependencies()
            probe.assert_called_once_with(60)
            which.assert_not_called()
            install.assert_not_called()

    def test_healthy_pages_need_no_install(self):
        with patch.object(RENDER, "check_writer") as probe, \
                patch.object(RENDER.shutil, "which", return_value="pdftoppm"), \
                patch.object(RENDER, "install_dependencies") as install:
            RENDER.ensure_dependencies(pages=True)
            probe.assert_called_once()
            install.assert_not_called()

    def test_missing_poppler_installs_only_poppler(self):
        with patch.object(RENDER, "check_writer") as probe, \
                patch.object(RENDER.shutil, "which", side_effect=[None, "pdftoppm"]), \
                patch.object(RENDER, "install_dependencies") as install:
            RENDER.ensure_dependencies(pages=True)
            install.assert_called_once_with(writer=False, pages=True)
            probe.assert_called_once()

    def test_failed_known_good_probe_installs_writer_even_if_core_exists(self):
        with patch.object(RENDER, "check_writer", side_effect=[
                RENDER.WriterUnavailableError("core alone cannot load DOCX"), None]) as probe, \
                patch.object(RENDER, "install_dependencies") as install:
            RENDER.ensure_dependencies()
            install.assert_called_once_with(writer=True, pages=False)
            self.assertEqual(probe.call_count, 2)

    def test_both_dependencies_provisioned_once(self):
        with patch.object(RENDER, "check_writer", side_effect=[
                RENDER.WriterUnavailableError("missing"), None]), \
                patch.object(RENDER.shutil, "which", side_effect=[None, "pdftoppm"]), \
                patch.object(RENDER, "install_dependencies") as install:
            RENDER.ensure_dependencies(pages=True)
            install.assert_called_once_with(writer=True, pages=True)

    def test_repair_that_does_not_fix_writer_stops(self):
        with patch.object(RENDER, "check_writer", side_effect=RENDER.WriterUnavailableError("bad")) as probe, \
                patch.object(RENDER, "install_dependencies") as install:
            with self.assertRaisesRegex(RuntimeError, "still unavailable"):
                RENDER.ensure_dependencies()
            self.assertEqual(probe.call_count, 2)
            install.assert_called_once()

    def test_repair_that_does_not_provide_poppler_stops(self):
        with patch.object(RENDER, "check_writer"), \
                patch.object(RENDER.shutil, "which", return_value=None), \
                patch.object(RENDER, "install_dependencies") as install:
            with self.assertRaisesRegex(RuntimeError, "did not provide pdftoppm"):
                RENDER.ensure_dependencies(pages=True)
            install.assert_called_once_with(writer=False, pages=True)

    def test_no_install_reports_both_missing_components(self):
        with patch.object(RENDER, "check_writer", side_effect=RENDER.WriterUnavailableError("Writer missing")), \
                patch.object(RENDER.shutil, "which", return_value=None), \
                patch.object(RENDER, "install_dependencies") as install:
            with self.assertRaisesRegex(RuntimeError, "(?s)Writer missing.*pdftoppm.*disabled"):
                RENDER.ensure_dependencies(pages=True, install=False)
            install.assert_not_called()

    def test_timeout_and_permission_errors_do_not_trigger_install(self):
        for error in (subprocess.TimeoutExpired("soffice", 60), PermissionError("profile denied")):
            with self.subTest(error=error), \
                    patch.object(RENDER, "check_writer", side_effect=error), \
                    patch.object(RENDER, "install_dependencies") as install:
                with self.assertRaises(type(error)):
                    RENDER.ensure_dependencies()
                install.assert_not_called()

    def test_probe_is_valid_docx_and_does_not_install(self):
        def fail_probe(source, destination, timeout):
            with ZipFile(source) as package:
                self.assertIn("word/document.xml", package.namelist())
                self.assertIn(b"Writer conversion check", package.read("word/document.xml"))
            raise RuntimeError("filter missing")
        with patch.object(RENDER, "render", side_effect=fail_probe), \
                patch.object(RENDER, "install_dependencies") as install:
            with self.assertRaisesRegex(RENDER.WriterUnavailableError, "filter missing"):
                RENDER.check_writer()
            install.assert_not_called()

    def test_check_mode_never_installs_and_returns_nonzero_when_unavailable(self):
        with patch.object(sys, "argv", [str(SCRIPT), "--check"]), \
                patch.object(RENDER, "check_writer", side_effect=RENDER.WriterUnavailableError("missing")), \
                patch.object(RENDER, "install_dependencies") as install:
            with self.assertRaises(SystemExit) as result:
                RENDER.main()
            self.assertEqual(result.exception.code, 1)
            install.assert_not_called()

    def test_check_pages_is_read_only_and_checks_poppler(self):
        with tempfile.TemporaryDirectory() as directory:
            pages = Path(directory) / "not created"
            with patch.object(sys, "argv", [str(SCRIPT), "--check", "--pages", str(pages)]), \
                    patch.object(RENDER, "check_writer"), \
                    patch.object(RENDER.shutil, "which", return_value=None), \
                    patch.object(RENDER, "install_dependencies") as install:
                with self.assertRaises(SystemExit) as result:
                    RENDER.main()
                self.assertEqual(result.exception.code, 1)
                self.assertFalse(pages.exists())
                install.assert_not_called()

    def test_invalid_input_does_not_provision_anything(self):
        for arguments in ([], ["--timeout", "0"], ["missing.docx", "--out", "output.pdf"]):
            with self.subTest(arguments=arguments), \
                    patch.object(sys, "argv", [str(SCRIPT), *arguments]), \
                    patch.object(RENDER, "ensure_dependencies") as ensure:
                with self.assertRaises(SystemExit) as result:
                    RENDER.main()
                self.assertEqual(result.exception.code, 2)
                ensure.assert_not_called()

    def test_same_input_and_output_does_not_provision(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.docx"
            source.touch()
            with patch.object(sys, "argv", [str(SCRIPT), str(source), "--out", str(source)]), \
                    patch.object(RENDER, "ensure_dependencies") as ensure:
                with self.assertRaises(SystemExit) as result:
                    RENDER.main()
                self.assertEqual(result.exception.code, 2)
                ensure.assert_not_called()

    def test_hardlinked_output_does_not_provision_or_overwrite_source(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.docx"
            source.write_bytes(b"original")
            output = Path(directory) / "hardlink.pdf"
            output.hardlink_to(source)
            with patch.object(sys, "argv", [str(SCRIPT), str(source), "--out", str(output)]), \
                    patch.object(RENDER, "ensure_dependencies") as ensure:
                with self.assertRaises(SystemExit) as result:
                    RENDER.main()
                self.assertEqual(result.exception.code, 2)
                ensure.assert_not_called()
                self.assertEqual(source.read_bytes(), b"original")

    def test_invalid_output_paths_do_not_provision(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.docx"
            source.touch()
            for output, pages in ((Path(directory), None), (Path(directory) / "out.pdf", source)):
                arguments = [str(SCRIPT), str(source), "--out", str(output)]
                if pages is not None:
                    arguments += ["--pages", str(pages)]
                with self.subTest(output=output), patch.object(sys, "argv", arguments), \
                        patch.object(RENDER, "ensure_dependencies") as ensure:
                    with self.assertRaises(SystemExit) as result:
                        RENDER.main()
                    self.assertEqual(result.exception.code, 2)
                    ensure.assert_not_called()

    def test_pages_failure_preserves_pdf_and_does_not_replay_conversion(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.docx"
            source.touch()
            output = Path(directory) / "out.pdf"
            pages = Path(directory) / "pages"
            arguments = [str(SCRIPT), str(source), "--out", str(output), "--pages", str(pages)]
            def write_pdf(*_args):
                output.write_bytes(b"%PDF-test")
            with patch.object(sys, "argv", arguments), \
                    patch.object(RENDER, "ensure_dependencies"), \
                    patch.object(RENDER, "render", side_effect=write_pdf) as render, \
                    patch.object(RENDER.subprocess, "run", side_effect=subprocess.TimeoutExpired("pdftoppm", 60)) as run, \
                    patch.object(RENDER, "install_dependencies") as install:
                with self.assertRaises(SystemExit) as result:
                    RENDER.main()
                self.assertEqual(result.exception.code, 1)
                self.assertIn("PDF rendered to", self.stderr.getvalue())
                self.assertIn("page rasterization failed", self.stderr.getvalue())
                self.assertEqual(output.read_bytes(), b"%PDF-test")
                render.assert_called_once()
                run.assert_called_once()
                install.assert_not_called()

    def test_actual_document_failure_is_not_retried_or_repaired(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "bad.docx"
            source.touch()
            output = Path(directory) / "keep.pdf"
            output.write_bytes(b"previous result")
            with patch.object(sys, "argv", [str(SCRIPT), str(source), "--out", str(output)]), \
                    patch.object(RENDER, "ensure_dependencies"), \
                    patch.object(RENDER, "render", side_effect=RuntimeError("bad document")) as render, \
                    patch.object(RENDER, "install_dependencies") as install:
                with self.assertRaises(SystemExit) as result:
                    RENDER.main()
                self.assertEqual(result.exception.code, 1)
                render.assert_called_once()
                install.assert_not_called()
                self.assertEqual(output.read_bytes(), b"previous result")

    def test_no_install_flag_reaches_preflight(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source with spaces.docx"
            source.touch()
            output = Path(directory) / "out.pdf"
            with patch.object(sys, "argv", [str(SCRIPT), str(source), "--out", str(output), "--no-install"]), \
                    patch.object(RENDER, "ensure_dependencies") as ensure, \
                    patch.object(RENDER, "render") as render:
                RENDER.main()
                ensure.assert_called_once_with(pages=False, install=False, timeout=60)
                render.assert_called_once_with(source, output, 60)

    def test_help_never_provisions(self):
        with patch.object(sys, "argv", [str(SCRIPT), "--help"]), \
                patch.object(RENDER, "ensure_dependencies") as ensure:
            with self.assertRaises(SystemExit) as result:
                RENDER.main()
            self.assertEqual(result.exception.code, 0)
            ensure.assert_not_called()


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(patch.stopall)
        patch.object(sys, "stderr", io.StringIO()).start()
        patch.object(RENDER.platform, "system", return_value="Linux").start()
        patch.object(RENDER.os, "geteuid", return_value=0, create=True).start()
        self.run = patch.object(RENDER.subprocess, "run").start()

    def manager(self, name, sudo=False):
        available = {name: f"/bin/{name}"}
        if sudo:
            available["sudo"] = "/bin/sudo"
        return patch.object(RENDER.shutil, "which", side_effect=available.get)

    def test_empty_install_is_a_noop(self):
        with patch.object(RENDER.shutil, "which") as which:
            RENDER.install_dependencies(writer=False, pages=False)
            which.assert_not_called()
        self.run.assert_not_called()

    def test_apt_writer_only_does_not_install_poppler_or_authoring_tools(self):
        with self.manager("apt-get"):
            RENDER.install_dependencies(writer=True, pages=False)
        self.assertEqual([entry.args[0] for entry in self.run.call_args_list], [
            ["/bin/apt-get", "update"],
            ["/bin/apt-get", "install", "-y", "--no-install-recommends", "libreoffice-writer"],
        ])
        for entry in self.run.call_args_list:
            self.assertEqual(entry.kwargs["stdin"], subprocess.DEVNULL)
            self.assertEqual(entry.kwargs["timeout"], RENDER.INSTALL_TIMEOUT)
            self.assertTrue(entry.kwargs["check"])
            self.assertTrue(entry.kwargs["start_new_session"])
            self.assertEqual(entry.kwargs["env"]["NONINTERACTIVE"], "1")
            self.assertNotIn("shell", entry.kwargs)

    def test_only_requested_poppler_package_for_each_linux_manager(self):
        expected = {"apt-get": "poppler-utils", "dnf": "poppler-utils", "pacman": "poppler",
                    "zypper": "poppler-tools", "apk": "poppler-utils"}
        for manager, package in expected.items():
            with self.subTest(manager=manager), self.manager(manager):
                self.run.reset_mock()
                RENDER.install_dependencies(writer=False, pages=True)
                command = self.run.call_args.args[0]
                self.assertEqual(command[-1], package)
                self.assertFalse(any("libreoffice" in item for item in command))

    def test_nonroot_uses_noninteractive_sudo(self):
        with self.manager("apt-get", sudo=True), patch.object(RENDER.os, "geteuid", return_value=1000):
            RENDER.install_dependencies(writer=True, pages=False)
        for entry in self.run.call_args_list:
            self.assertEqual(entry.args[0][:3], ["/bin/sudo", "-n", "--"])

    def test_no_privilege_fails_before_any_install(self):
        with self.manager("apt-get"), patch.object(RENDER.os, "geteuid", return_value=1000):
            with self.assertRaisesRegex(RuntimeError, "root or noninteractive sudo"):
                RENDER.install_dependencies(writer=True, pages=False)
            self.run.assert_not_called()

    def test_unknown_linux_manager_does_not_guess(self):
        with patch.object(RENDER.shutil, "which", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "No supported package manager"):
                RENDER.install_dependencies(writer=True, pages=False)
        self.run.assert_not_called()

    def test_brew_installs_only_requested_components(self):
        with patch.object(RENDER.platform, "system", return_value="Darwin"), self.manager("brew"):
            RENDER.install_dependencies(writer=False, pages=True)
        self.assertEqual(self.run.call_args.args[0], ["/bin/brew", "install", "poppler"])
        self.run.reset_mock()
        with patch.object(RENDER.platform, "system", return_value="Darwin"), self.manager("brew"):
            RENDER.install_dependencies(writer=True, pages=False)
        self.assertEqual(self.run.call_args.args[0], ["/bin/brew", "install", "--cask", "libreoffice"])

    def test_missing_brew_and_unsupported_os_fail_explicitly(self):
        with patch.object(RENDER.platform, "system", return_value="Darwin"), \
                patch.object(RENDER.shutil, "which", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "needs Homebrew"):
                RENDER.install_dependencies(writer=True, pages=False)
        with patch.object(RENDER.platform, "system", return_value="Windows"):
            with self.assertRaisesRegex(RuntimeError, "not supported on Windows"):
                RENDER.install_dependencies(writer=False, pages=True)
        self.run.assert_not_called()

    def test_failed_or_timed_out_install_is_not_repeated(self):
        errors = [subprocess.CalledProcessError(1, "apt-get", output="network denied"),
                  subprocess.TimeoutExpired("apt-get", RENDER.INSTALL_TIMEOUT)]
        for error in errors:
            with self.subTest(error=error), self.manager("apt-get"):
                self.run.reset_mock()
                self.run.side_effect = error
                with self.assertRaisesRegex(RuntimeError, "installation (failed|timed out)") as result:
                    RENDER.install_dependencies(writer=True, pages=True)
                if isinstance(error, subprocess.TimeoutExpired):
                    self.assertIn("children may still be running", str(result.exception))
                    self.assertIn("no rollback is implied", str(result.exception))
                self.run.assert_called_once()

    def test_find_existing_windows_install_without_path_changes(self):
        with patch.object(RENDER.platform, "system", return_value="Windows"), \
                patch.object(RENDER.shutil, "which", return_value=None), \
                patch.dict(RENDER.os.environ, {"ProgramFiles": "C:/Apps"}), \
                patch.object(Path, "is_file", autospec=True,
                             side_effect=lambda path: path.as_posix().startswith("C:/Apps/")):
            self.assertIn("LibreOffice", RENDER.find_soffice())


@unittest.skipIf(os.name == "nt" or not shutil.which("bash"), "requires a POSIX shell")
class EnvironmentCheckTests(unittest.TestCase):
    def test_writer_failure_is_required_only_when_rendering_is_requested(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            marker = work / "writer-probed"
            for name, script in {
                "dotnet": "#!/bin/sh\necho 8.0.100\n",
                "python3": '#!/bin/sh\ntouch "$WRITER_PROBE_MARKER"\necho "Writer unavailable" >&2\nexit 1\n',
            }.items():
                executable = work / name
                executable.write_text(script, encoding="utf-8")
                executable.chmod(0o755)
            env = {**os.environ, "PATH": str(work) + os.pathsep + os.environ.get("PATH", ""),
                   "WRITER_PROBE_MARKER": str(marker)}
            command = [shutil.which("bash"), str(SCRIPT.parent / "env_check.sh")]
            normal = subprocess.run(command, env=env, capture_output=True, text=True, timeout=30)
            self.assertEqual(normal.returncode, 0, normal.stdout + normal.stderr)
            self.assertFalse(marker.exists(), "DOCX-only check must not probe Writer")
            requested = subprocess.run([*command, "--with-rendering"], env=env,
                                       capture_output=True, text=True, timeout=30)
            self.assertEqual(requested.returncode, 1, requested.stdout + requested.stderr)
            self.assertTrue(marker.exists())
            self.assertIn("[FAIL]    Writer", requested.stdout)
            self.assertIn("Status: NOT READY", requested.stdout)


if __name__ == "__main__":
    unittest.main()
