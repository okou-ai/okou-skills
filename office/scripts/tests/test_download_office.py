"""Exercise main's Office-only package with real, local partial-fetch fixtures."""

import importlib.util
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "download_office.py"
SPEC = importlib.util.spec_from_file_location("download_office", SCRIPT)
downloader = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(downloader)


@unittest.skipUnless(shutil.which("git"), "Git is required")
class DownloadOfficeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = tempfile.TemporaryDirectory(prefix="office-source-")
        cls.source = Path(cls.fixture.name)
        cls.git("init", "--quiet", "--initial-branch=main")
        cls.git("config", "user.name", "Package test")
        cls.git("config", "user.email", "package-test@example.invalid")
        cls.git("config", "uploadpack.allowFilter", "true")
        (cls.source / "unrelated").mkdir()
        (cls.source / "unrelated/large.bin").write_bytes(b"not an Office dependency\0" * 50000)
        cls.git("add", ".")
        cls.commit("Unrelated files only")
        cls.no_office = cls.git("rev-parse", "HEAD")
        cls.unrelated_blob = cls.git("rev-parse", "HEAD:unrelated/large.bin")
        office = cls.source / "office"
        for directory in ("docx/scripts", "pdf", "xlsx", "references"):
            (office / directory).mkdir(parents=True)
        (office / "SKILL.md").write_text("original main\n")
        for format_name in ("docx", "pdf", "xlsx"):
            (office / format_name / "SKILL.md").write_text(f"{format_name} route\n")
            (office / format_name / "LICENSE").write_text("Test license\n")
            (office / format_name / "UPSTREAM.md").write_text("Test provenance\n")
        (office / "references/analysis.md").write_text("Shared analytical guidance\n")
        (office / "docx/scripts/docx.sh").write_text("#!/bin/sh\nexit 0\n")
        cls.git("add", ".")
        cls.git("update-index", "--chmod=+x", "office/docx/scripts/docx.sh")
        cls.commit("Office source on main")
        cls.original = cls.git("rev-parse", "HEAD")
        cls.url = cls.source.as_uri()

    @classmethod
    def tearDownClass(cls):
        cls.fixture.cleanup()

    @classmethod
    def git(cls, *args):
        return subprocess.run(["git", "-C", str(cls.source), *args], check=True,
                              text=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE).stdout.strip()

    @classmethod
    def commit(cls, message):
        cls.git("-c", "commit.gpgsign=false", "commit", "--quiet", "-m", message)

    def setUp(self):
        self.git("reset", "--hard", self.original)
        self.scratch = tempfile.TemporaryDirectory(prefix="office-output-")
        self.addCleanup(self.scratch.cleanup)
        self.output = Path(self.scratch.name) / "office.tar.gz"

    def download(self):
        return downloader.download_office(self.output, repository=self.url)

    def advance_main(self):
        (self.source / "office/SKILL.md").write_text("newer main\n")
        self.git("add", ".")
        self.commit("Office update on main")
        return self.git("rev-parse", "HEAD")

    def test_only_office_blobs_are_fetched_and_all_formats_are_packaged(self):
        original_git = downloader._git
        inspected = []

        def inspect_checkout(directory, *args):
            result = original_git(directory, *args)
            if args[0] == "archive":
                # Enumerate present objects without triggering a lazy fetch.
                objects = original_git(directory, "cat-file", "--batch-all-objects",
                                       "--batch-check=%(objectname)").splitlines()
                self.assertNotIn(self.unrelated_blob, objects)
                self.assertFalse((directory / "unrelated").exists())
                inspected.append(True)
            return result

        with patch.object(downloader, "_git", side_effect=inspect_checkout):
            result = self.download()
        self.assertTrue(inspected)
        self.assertEqual(result["revision"], self.original)
        self.assertEqual(result["root"], "office/")
        self.assertEqual(result["bytes"], self.output.stat().st_size)
        with tarfile.open(self.output, "r:gz") as archive:
            self.assertTrue(all(name == "office" or name.startswith("office/")
                                for name in archive.getnames()))
            files = {member.name for member in archive.getmembers() if member.isfile()}
            self.assertEqual(files, set(self.git("ls-files", "office").splitlines()))
            for name in files:
                self.assertEqual(archive.extractfile(name).read(), (self.source / name).read_bytes())
            self.assertEqual(archive.getmember("office/docx/scripts/docx.sh").mode & 0o111,
                             0o111)

    def test_archive_is_reproducible_and_preserves_resolved_provenance(self):
        result = self.download()
        first = self.output.read_bytes()
        self.download()
        self.assertEqual(first, self.output.read_bytes())
        with tarfile.open(self.output, "r:gz") as archive:
            self.assertEqual(archive.pax_headers["comment"], result["revision"])

    def test_current_main_is_used_after_source_changes(self):
        self.download()
        latest = self.advance_main()
        self.assertEqual(self.download()["revision"], latest)
        with tarfile.open(self.output, "r:gz") as archive:
            self.assertEqual(archive.extractfile("office/SKILL.md").read(), b"newer main\n")

    def test_main_is_resolved_once_even_if_remote_changes_during_download(self):
        original_git = downloader._git

        def move_main_after_fetch(directory, *args):
            result = original_git(directory, *args)
            if args[0] == "fetch":
                self.advance_main()
            return result

        with patch.object(downloader, "_git", side_effect=move_main_after_fetch):
            self.assertEqual(self.download()["revision"], self.original)
        with tarfile.open(self.output, "r:gz") as archive:
            self.assertEqual(archive.extractfile("office/SKILL.md").read(), b"original main\n")

    def test_failed_fetch_preserves_existing_output(self):
        self.output.write_bytes(b"existing package")
        with self.assertRaises(subprocess.CalledProcessError):
            downloader.download_office(self.output, repository=self.url + "/missing")
        self.assertEqual(self.output.read_bytes(), b"existing package")
        self.assertEqual(list(self.output.parent.iterdir()), [self.output])

    def test_main_without_office_fails_and_preserves_existing_output(self):
        self.git("reset", "--hard", self.no_office)
        self.output.write_bytes(b"existing package")
        with self.assertRaisesRegex(RuntimeError, "no office/SKILL.md"):
            self.download()
        self.assertEqual(self.output.read_bytes(), b"existing package")

    def test_archive_failure_preserves_existing_output(self):
        self.output.write_bytes(b"existing package")
        original_git = downloader._git

        def fail_archive(directory, *args):
            if args[0] == "archive":
                raise subprocess.CalledProcessError(1, ["git", *args], stderr="archive failed")
            return original_git(directory, *args)

        with patch.object(downloader, "_git", side_effect=fail_archive):
            with self.assertRaises(subprocess.CalledProcessError):
                self.download()
        self.assertEqual(self.output.read_bytes(), b"existing package")

    def test_compression_failure_cleans_up_partial_output(self):
        self.output.write_bytes(b"existing package")
        original_open = tarfile.open

        def fail_writer(*args, **kwargs):
            if kwargs.get("mode") == "w|":
                raise OSError("compression failed")
            return original_open(*args, **kwargs)

        with patch.object(downloader.tarfile, "open", side_effect=fail_writer):
            with self.assertRaisesRegex(OSError, "compression failed"):
                self.download()
        self.assertEqual(self.output.read_bytes(), b"existing package")
        self.assertEqual(list(self.output.parent.iterdir()), [self.output])

    def test_missing_git_has_an_actionable_error(self):
        with patch.object(downloader.shutil, "which", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "Git with partial-fetch"):
                self.download()


if __name__ == "__main__":
    unittest.main()
