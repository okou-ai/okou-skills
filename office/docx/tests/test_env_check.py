"""DOCX readiness should not require Writer unless conversion is requested."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


class EnvironmentCheckTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="docx environment ")
        self.addCleanup(self.directory.cleanup)
        self.work = Path(self.directory.name)
        self.scripts = self.work / "scripts"
        self.scripts.mkdir()
        for name in ("env_check.sh", "render_docx.py"):
            shutil.copy2(SCRIPTS / name, self.scripts / name)
        (self.scripts / "dotnet").mkdir()
        binary = self.work / "bin"
        binary.mkdir()
        # External tools: authoring is available but the installed Writer is broken.
        (binary / "dotnet").write_text(
            '#!/bin/sh\nif [ "$1" = "--version" ]; then echo 8.0.100; fi\n'
        )
        self.writer_calls = self.work / "writer-calls"
        (binary / "soffice").write_text(
            '#!/bin/sh\nprintf "%s\\n" "$*" >> "$WRITER_CALLS"\n'
            'echo "Error: source file could not be loaded" >&2\nexit 0\n'
        )
        for executable in binary.iterdir():
            executable.chmod(0o755)
        self.env = {
            **os.environ,
            "PATH": str(binary) + os.pathsep + os.environ["PATH"],
            "WRITER_CALLS": str(self.writer_calls),
        }

    def run_check(self, *args):
        return subprocess.run(
            ["bash", str(self.scripts / "env_check.sh"), *args],
            env=self.env, text=True, capture_output=True, timeout=10,
        )

    def test_default_readiness_works_without_calling_writer(self):
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Status: READY", result.stdout)
        self.assertFalse(self.writer_calls.exists())

    def test_requested_rendering_reports_failed_conversion(self):
        result = self.run_check("--with-rendering")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("--convert-to", self.writer_calls.read_text())
        self.assertIn("DOCX-to-PDF probe failed", result.stdout)
        self.assertIn("source file could not be loaded", result.stdout)


if __name__ == "__main__":
    unittest.main()
