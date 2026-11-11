"""Check isolated author inputs; these tests do not measure model quality."""

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("prepare_analysis", ROOT / "prepare.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PrepareTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "Fixture")
        (self.repo / "office/references").mkdir(parents=True)
        (self.repo / "office/SKILL.md").write_text("# Frozen guidance\n")
        (self.repo / "office/references/analysis.md").write_text("Original revision\n")
        (self.repo / "reviewer.md").write_text("Withhold this answer key\n")
        (self.repo / "office/unsafe.py").write_text("raise RuntimeError('not needed')\n")
        self.git("add", ".")
        self.git("commit", "-qm", "fixture")
        self.commit = self.git("rev-parse", "HEAD").strip()

    def git(self, *args):
        return subprocess.check_output(
            ["git", *args], cwd=self.repo, text=True, stderr=subprocess.DEVNULL,
        )

    def test_freezes_requested_revision_and_exact_bytes(self):
        (self.repo / "office/references/analysis.md").write_text("Uncommitted change\n")
        output = self.root / "run"
        MODULE.prepare(self.repo, self.commit, "operating-review", output)
        self.assertEqual(
            (output / "office/references/analysis.md").read_text(), "Original revision\n",
        )
        original = ROOT / "cases/operating-review/sources/results.csv"
        self.assertEqual((output / "input/sources/results.csv").read_bytes(), original.read_bytes())
        manifest = json.loads((output / "manifest.json").read_text())
        self.assertEqual(manifest["skill_commit"], self.commit)
        actual = {
            p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in output.rglob("*") if p.is_file() and p.name != "manifest.json"
        }
        self.assertEqual(actual, manifest["sha256"])

    def test_excludes_reviewer_other_cases_and_executables(self):
        output = self.root / "run"
        MODULE.prepare(self.repo, self.commit, "narrow-edit", output)
        self.assertEqual({p.name for p in output.iterdir()}, {
            "office", "input", "request.md", "manifest.json",
        })
        self.assertFalse(list(output.rglob("reviewer.md")))
        self.assertFalse(list(output.rglob("*.py")))
        self.assertFalse(list(output.rglob("results.csv")))

    def test_preserves_an_existing_run(self):
        output = self.root / "run"
        output.mkdir()
        answer = output / "answer.md"
        answer.write_text("Existing attempt\n")
        with self.assertRaisesRegex(ValueError, "already exists"):
            MODULE.prepare(self.repo, self.commit, "narrow-edit", output)
        self.assertEqual(answer.read_text(), "Existing attempt\n")

    def test_rejects_unknown_or_escaping_case(self):
        for case in ["missing-case", "../reviewer.md"]:
            output = self.root / "run"
            with self.assertRaisesRegex(ValueError, "Unknown case"):
                MODULE.prepare(self.repo, self.commit, case, output)
            self.assertFalse(output.exists())

    def test_rejects_revision_without_office_entry(self):
        (self.repo / "office/SKILL.md").unlink()
        self.git("add", "-u")
        self.git("commit", "-qm", "remove entry")
        output = self.root / "run"
        with self.assertRaisesRegex(ValueError, "no Office entry"):
            MODULE.prepare(self.repo, "HEAD", "narrow-edit", output)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
