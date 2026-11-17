"""Check that the operation router and its optional references remain navigable."""

from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[2]
LINK = re.compile(r"\[[^\]\n]*\]\(<?([^\s)>]+)>?(?:\s+\"[^\"]*\")?\)")


class GuidanceLinksTests(unittest.TestCase):
    def test_office_local_reference_targets_exist(self):
        files = sorted((ROOT / "office").rglob("*.md"))
        self.assertTrue(files)
        for document in files:
            for match in LINK.finditer(document.read_text(encoding="utf-8")):
                target = urlsplit(match.group(1))
                if target.scheme or target.netloc or not target.path:
                    continue
                with self.subTest(document=str(document.relative_to(ROOT)), target=match.group(1)):
                    resolved = (document.parent / unquote(target.path)).resolve()
                    self.assertTrue(resolved.is_relative_to(ROOT), "Reference escapes the repository")
                    self.assertTrue(resolved.exists(), "Missing local reference target")

    def test_legacy_analysis_reference_points_to_the_inline_contract(self):
        # Keep the old URL usable without making it a second default loader.
        root = ROOT / "office" / "SKILL.md"
        legacy = ROOT / "office" / "references" / "analysis.md"
        for match in LINK.finditer(legacy.read_text(encoding="utf-8")):
            target = urlsplit(match.group(1))
            if (legacy.parent / target.path).resolve() != root:
                continue
            headings = re.findall(r"^#{1,6}\s+(.+)$", root.read_text(encoding="utf-8"), re.MULTILINE)
            anchors = {re.sub(r"[^\w\s-]", "", text).lower().replace(" ", "-") for text in headings}
            self.assertIn(target.fragment, anchors)
            break
        else:
            self.fail("The compatibility reference must link to the inline evidence contract")


if __name__ == "__main__":
    unittest.main()
