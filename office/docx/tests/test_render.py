"""Real Writer conversion and the zero-exit/no-output failure contract."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
RENDER = SKILL / "scripts/render_docx.py"
ENV_CHECK = SKILL / "scripts/env_check.sh"


class WriterTests(unittest.TestCase):
    def test_writer_probe_converts_docx(self):
        result = subprocess.run([sys.executable, str(RENDER), "--check"],
                                capture_output=True, text=True, timeout=90)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("conversion passed", result.stdout)

    @unittest.skipIf(os.name == "nt", "POSIX process fixture")
    def test_env_check_does_not_treat_soffice_version_as_writer_support(self):
        with tempfile.TemporaryDirectory() as directory:
            fake_bin = Path(directory)
            dotnet = fake_bin / "dotnet"
            dotnet.write_text("""#!/bin/sh
if [ "$1" = "--version" ]; then echo 8.0.100; fi
exit 0
""")
            dotnet.chmod(0o755)
            soffice = fake_bin / "soffice"
            soffice.write_text("""#!/bin/sh
if [ "$1" = "--version" ]; then echo 'LibreOffice 24.2.2'; fi
exit 0
""")
            soffice.chmod(0o755)
            result = subprocess.run(
                ["bash", str(ENV_CHECK)],
                env={**os.environ, "PATH": f"{directory}{os.pathsep}{os.environ['PATH']}"},
                capture_output=True, text=True, timeout=90,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Writer", result.stdout)
            self.assertIn("DOCX-to-PDF probe failed", result.stdout)
            self.assertRegex(
                result.stdout,
                r"(sudo apt-get install libreoffice-writer|brew install --cask libreoffice)",
            )

    @unittest.skipIf(os.name == "nt", "POSIX process fixture")
    def test_soffice_exit_zero_without_output_is_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            fake = Path(directory) / "soffice"
            fake.write_text("#!/bin/sh\nexit 0\n")
            fake.chmod(0o755)
            result = subprocess.run(
                [sys.executable, str(RENDER), "--check"],
                env={**os.environ, "PATH": directory},
                capture_output=True, text=True, timeout=90,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("did not produce a PDF", result.stderr)


if __name__ == "__main__":
    unittest.main()
